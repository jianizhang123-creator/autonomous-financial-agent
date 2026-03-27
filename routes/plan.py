"""
/api/plan — Goal decomposition + planning pipeline (SSE stream).
"""

import time

from flask import Blueprint, Response, request

from agents import goal_decomposition, planning
from events.stream import sse_event
from memory.store import load_memory, save_memory
from memory.user_profile import get_profile_context

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/api/plan", methods=["POST"])
def create_plan():
    body = request.get_json(force=True)
    goal = body.get("goal", "")
    goal_type = body.get("goal_type", "savings")
    target_amount = body.get("target_amount", 0)
    target_days = body.get("target_days", 90)

    def stream():
        memory = load_memory()
        profile = memory.get("user_profile", {})
        profile_ctx = get_profile_context(profile)

        # --- Goal Decomposition ---
        yield sse_event("agent_start", {"agent": "goal_decomposition"})
        decomposition = goal_decomposition.run(
            profile_ctx, goal, goal_type, target_amount, target_days,
        )
        yield sse_event("agent_done", {"agent": "goal_decomposition", "result": decomposition})

        # --- Planning ---
        yield sse_event("agent_start", {"agent": "planning"})
        plan = planning.run(profile_ctx, decomposition)
        yield sse_event("agent_done", {"agent": "planning", "result": plan})

        # --- Update memory ---
        wm = memory.setdefault("working_memory", {})
        wm["active_goal"] = {
            "goal": goal,
            "goal_type": goal_type,
            "target_amount": target_amount,
            "target_days": target_days,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        wm["current_plan"] = plan
        total_weeks = decomposition.get("total_duration_weeks", target_days // 7)
        weekly_target = round(target_amount / max(total_weeks, 1), 2)
        wm["goal_progress"] = {
            "current_week": 1,
            "total_saved": 0,
            "weekly_target": weekly_target,
            "total_weeks": total_weeks,
            "decomposition": decomposition,
        }
        wm["pending_suggestions"] = []
        wm["approved_actions"] = []
        wm["recent_events"] = []
        save_memory(memory)

        yield sse_event("plan_complete", {
            "decomposition": decomposition,
            "plan": plan,
            "goal_progress": wm["goal_progress"],
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
