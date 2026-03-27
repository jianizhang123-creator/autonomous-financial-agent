"""
/api/event — Event routing + execution monitoring + insight pipeline
(SSE stream).
"""

import json
import time
import uuid

from flask import Blueprint, Response, request

from agents import event_router, execution_monitor, insight
from events.stream import sse_event
from memory.store import load_memory, save_memory
from memory.user_profile import get_profile_context
from memory.working_memory import get_plan_context

event_bp = Blueprint("event", __name__)


@event_bp.route("/api/event", methods=["POST"])
def process_event():
    body = request.get_json(force=True)
    event_type = body.get("event_type", "unknown")
    event_data = body.get("event_data", {})

    def stream():
        memory = load_memory()
        wm = memory.setdefault("working_memory", {})
        profile = memory.get("user_profile", {})
        profile_ctx = get_profile_context(profile)
        plan_ctx = get_plan_context(wm)

        event_record = {
            "id": str(uuid.uuid4())[:8],
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        recent = wm.setdefault("recent_events", [])
        recent.append(event_record)
        wm["recent_events"] = recent[-10:]
        yield sse_event("event_received", event_record)

        ev_desc = json.dumps(event_data, ensure_ascii=False)

        # --- Event Router ---
        yield sse_event("agent_start", {"agent": "event_router"})
        routing = event_router.run(profile_ctx, plan_ctx, event_type, ev_desc)
        yield sse_event("agent_done", {"agent": "event_router", "result": routing})

        # --- Execution Monitor ---
        yield sse_event("agent_start", {"agent": "execution_monitor"})
        monitor = execution_monitor.run(
            profile_ctx, plan_ctx, event_type, ev_desc, routing,
        )
        yield sse_event("agent_done", {"agent": "execution_monitor", "result": monitor})

        # --- Insight (conditional) ---
        insight_result = None
        if monitor.get("deviation_detected") or routing.get("requires_immediate_action"):
            yield sse_event("agent_start", {"agent": "insight"})
            insight_result = insight.run(
                profile_ctx, plan_ctx, event_type, ev_desc, routing, monitor,
            )
            yield sse_event("agent_done", {"agent": "insight", "result": insight_result})

        # --- Build suggestion ---
        suggestion = {
            "id": str(uuid.uuid4())[:8],
            "event_id": event_record["id"],
            "event_type": event_type,
            "routing": routing,
            "monitor": monitor,
            "insight": insight_result,
            "created_at": event_record["timestamp"],
            "status": "pending",
        }
        wm.setdefault("pending_suggestions", []).append(suggestion)
        save_memory(memory)

        yield sse_event("event_complete", {
            "event": event_record,
            "routing": routing,
            "monitor": monitor,
            "insight": insight_result,
            "suggestion_id": suggestion["id"],
        })
        yield sse_event("memory_update", {
            "working_memory": wm,
            "user_profile": profile,
        })

    return Response(stream(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    })
