"""
User Profile context formatter — converts the persistent user profile into
a markdown string injected into agent prompts.
"""


def get_profile_context(profile: dict) -> str:
    income = profile.get("monthly_income", "unknown")
    lines = ["## User Profile", f"- Monthly income: {income}元"]

    spending = profile.get("spending_patterns", {})
    if spending:
        lines.append("- Monthly spending by category:")
        for cat, amt in spending.items():
            lines.append(f"  - {cat}: {amt}元")

    fixed = profile.get("fixed_expenses", {})
    if fixed:
        lines.append("- Fixed monthly expenses:")
        for cat, amt in fixed.items():
            lines.append(f"  - {cat}: {amt}元")

    total_spending = sum(spending.values()) + sum(fixed.values())
    lines.append(f"- Total monthly outflow: ~{total_spending}元")
    lines.append(f"- Estimated monthly surplus: ~{income - total_spending}元")
    lines.append(f"- Risk preference: {profile.get('risk_preference', 'moderate')}")
    return "\n".join(lines)
