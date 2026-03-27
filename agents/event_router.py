"""
Event Router Agent — classifies incoming financial events by priority and
determines which downstream agent should handle them.
"""

from agents.base import call_agent, load_prompt

SYSTEM_PROMPT = load_prompt("event_router")


def run(profile_context: str, plan_context: str,
        event_type: str, event_desc: str) -> dict:
    user_prompt = (
        f"{profile_context}\n\n{plan_context}\n\n## New Event\n"
        f"- Type: {event_type}\n- Data: {event_desc}\n\n"
        f"Classify this event and determine routing."
    )
    return call_agent("event_router", SYSTEM_PROMPT, user_prompt)
