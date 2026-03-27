"""
Execution Monitor Agent — detects plan deviations and generates concrete
adjustment suggestions with expected impact analysis.
"""

from agents.base import call_agent, load_prompt

SYSTEM_PROMPT = load_prompt("execution_monitor")


def run(profile_context: str, plan_context: str,
        event_type: str, event_desc: str, routing: dict) -> dict:
    user_prompt = (
        f"{profile_context}\n\n{plan_context}\n\n## Triggering Event\n"
        f"- Type: {event_type}\n- Data: {event_desc}\n\n## Routing Info\n"
        f"- Priority: {routing.get('priority', 'medium')}\n"
        f"- Category: {routing.get('event_category', 'unknown')}\n\n"
        f"Analyze deviation and suggest adjustments."
    )
    return call_agent("execution_monitor", SYSTEM_PROMPT, user_prompt)
