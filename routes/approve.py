"""
Miscellaneous API routes: suggestion approval, status, and presets.
"""

import time

from flask import Blueprint, jsonify, request

from memory.store import load_memory, save_memory
from presets import PRESETS

approve_bp = Blueprint("approve", __name__)


@approve_bp.route("/api/presets")
def get_presets():
    return jsonify(PRESETS)


@approve_bp.route("/api/status")
def get_status():
    mem = load_memory()
    return jsonify({
        "working_memory": mem.get("working_memory", {}),
        "user_profile": mem.get("user_profile", {}),
    })


@approve_bp.route("/api/approve", methods=["POST"])
def approve_suggestion():
    body = request.get_json(force=True)
    suggestion_id = body.get("suggestion_id", "")
    approved = body.get("approved", False)
    user_note = body.get("user_note", "")

    memory = load_memory()
    wm = memory.setdefault("working_memory", {})
    pending = wm.get("pending_suggestions", [])

    target, remaining = None, []
    for s in pending:
        if s.get("id") == suggestion_id:
            target = s
        else:
            remaining.append(s)

    if target is None:
        return jsonify({"error": f"Suggestion {suggestion_id} not found"}), 404

    if approved:
        target["status"] = "approved"
        target["user_note"] = user_note
        target["approved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        wm.setdefault("approved_actions", []).append(target)
        # Update goal progress if monitor suggested an adjusted weekly target
        suggestion_detail = target.get("monitor", {}).get("suggestion", {})
        adjusted = suggestion_detail.get("adjusted_weekly_target")
        if adjusted is not None:
            progress = wm.get("goal_progress")
            if progress:
                progress["weekly_target"] = adjusted
        # Record intervention pattern in user profile
        profile = memory.get("user_profile", {})
        profile.setdefault("intervention_history", []).append({
            "event_type": target.get("event_type"),
            "action": suggestion_detail.get("action", "unknown"),
            "outcome": "approved",
            "timestamp": target["approved_at"],
        })
    else:
        target["status"] = "rejected"
        target["user_note"] = user_note

    wm["pending_suggestions"] = remaining
    save_memory(memory)
    return jsonify({
        "success": True,
        "suggestion_id": suggestion_id,
        "approved": approved,
        "working_memory": wm,
        "user_profile": memory.get("user_profile", {}),
    })
