"""
Working Memory context formatter — converts session-scoped working memory
(active goal, plan, progress, recent events) into a markdown string for
agent prompts.
"""

import json


def get_plan_context(working_memory: dict) -> str:
    lines = ["## Current Plan State"]
    goal = working_memory.get("active_goal")
    if not goal:
        return "## Current Plan State\nNo active goal set."

    lines.append(f"- Active goal: {goal.get('goal', 'N/A')}")
    lines.append(f"- Type: {goal.get('goal_type', 'N/A')}")
    lines.append(f"- Target: {goal.get('target_amount', 0)}元 in {goal.get('target_days', 0)} days")

    progress = working_memory.get("goal_progress", {})
    if progress:
        lines.append(f"- Current week: {progress.get('current_week', 1)}")
        lines.append(f"- Saved so far: {progress.get('total_saved', 0)}元")
        lines.append(f"- Weekly target: {progress.get('weekly_target', 0)}元")

    plan = working_memory.get("current_plan")
    if plan and "budget_plan" in plan:
        lines.append("- Budget categories:")
        for cat in plan["budget_plan"].get("categories", []):
            lines.append(f"  - {cat['name']}: {cat.get('recommended', '?')}元/month")

    events = working_memory.get("recent_events", [])
    if events:
        lines.append(f"- Recent events ({len(events)}):")
        for ev in events[-3:]:
            desc = ev.get("event_data", {}).get(
                "description",
                json.dumps(ev.get("event_data", {}), ensure_ascii=False)[:60],
            )
            lines.append(f"  - [{ev.get('event_type')}] {desc}")

    return "\n".join(lines)
