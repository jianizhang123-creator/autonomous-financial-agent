"""
Goal Decomposition Agent — breaks a financial goal into phased sub-tasks
with weekly budget constraints and milestones.
"""

from agents.base import call_agent, load_prompt

SYSTEM_PROMPT = load_prompt("goal_decomposition")


def run(profile_context: str, goal: str, goal_type: str,
        target_amount: int, target_days: int) -> dict:
    user_prompt = (
        f"{profile_context}\n\n## Goal\n- Description: {goal}\n"
        f"- Type: {goal_type}\n- Target amount: {target_amount}元\n"
        f"- Timeframe: {target_days} days\n\n"
        f"Please decompose this goal into phased sub-tasks."
    )
    return call_agent("goal_decomposition", SYSTEM_PROMPT, user_prompt)
