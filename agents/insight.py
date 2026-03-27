"""
Insight Agent — generates concise, empathetic explanations of why a
particular financial action is recommended.
"""

import json

from agents.base import call_agent, load_prompt

SYSTEM_PROMPT = load_prompt("insight")


def run(profile_context: str, plan_context: str,
        event_type: str, event_desc: str,
        routing: dict, monitor: dict) -> dict:
    user_prompt = (
        f"{profile_context}\n\n{plan_context}\n\n"
        f"## Event\n- Type: {event_type}\n- Data: {event_desc}\n\n"
        f"## Routing\n```json\n{json.dumps(routing, ensure_ascii=False)}\n```\n\n"
        f"## Monitor Analysis\n```json\n{json.dumps(monitor, ensure_ascii=False)}\n```\n\n"
        f"Generate a concise, empathetic insight for the user."
    )
    return call_agent("insight", SYSTEM_PROMPT, user_prompt)
