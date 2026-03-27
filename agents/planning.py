"""
Planning Agent — generates a concrete execution plan with category-level
budget adjustments and a savings schedule.
"""

import json

from agents.base import call_agent, load_prompt

SYSTEM_PROMPT = load_prompt("planning")


def run(profile_context: str, decomposition: dict) -> dict:
    user_prompt = (
        f"{profile_context}\n\n## Decomposed Goal\n"
        f"```json\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Generate a concrete execution plan with category-level budget adjustments."
    )
    return call_agent("planning", SYSTEM_PROMPT, user_prompt)
