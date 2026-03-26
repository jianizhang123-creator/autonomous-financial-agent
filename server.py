"""
Autonomous Financial Agent Server
Flask backend with Claude API integration for a goal-driven autonomous
financial agent system with five specialized agents.
"""

import json
import re
import time
import uuid
from pathlib import Path

import anthropic
from flask import Flask, Response, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).parent
MEMORY_FILE = BASE_DIR / "memory.json"
MODEL = "claude-haiku-4-5-20251001"
app = Flask(__name__, static_folder=str(BASE_DIR))

# ---------------------------------------------------------------------------
# Preset Scenarios
# ---------------------------------------------------------------------------
PRESETS = [
    {
        "id": "save_5000",
        "name": "\u4e09\u4e2a\u6708\u6512\u0035\u0030\u0030\u0030\u5757",
        "name_en": "Save \u00a55000 in 3 Months",
        "goal": "\u6211\u60f3\u5728\u4e09\u4e2a\u6708\u5185\u6512\u4e0b\u0035\u0030\u0030\u0030\u5757\u94b1",
        "goal_type": "savings",
        "target_amount": 5000,
        "target_days": 90,
        "description": "Moderate savings goal with balanced lifestyle adjustments",
    },
    {
        "id": "pay_debt",
        "name": "\u8fd8\u6e05\u4fe1\u7528\u5361\u0038\u0030\u0030\u0030\u5143",
        "name_en": "Pay Off \u00a58000 Credit Card",
        "goal": "\u6211\u9700\u8981\u5728\u4e24\u4e2a\u6708\u5185\u8fd8\u6e05\u0038\u0030\u0030\u0030\u5143\u7684\u4fe1\u7528\u5361\u8d26\u5355",
        "goal_type": "debt_repayment",
        "target_amount": 8000,
        "target_days": 60,
        "description": "Aggressive debt repayment requiring significant spending cuts",
    },
    {
        "id": "cut_delivery",
        "name": "\u6bcf\u6708\u51cf\u5c11\u5916\u5356\u5f00\u652f\u0033\u0030\u0025",
        "name_en": "Cut Delivery Spending 30%",
        "goal": "\u6211\u60f3\u628a\u6bcf\u6708\u5916\u5356\u5f00\u652f\u4ece\u0039\u0030\u0030\u5143\u51cf\u5c11\u5230\u0036\u0033\u0030\u5143\u4ee5\u4e0b",
        "goal_type": "spending_reduction",
        "target_amount": 270,
        "target_days": 30,
        "description": "Behavioral change goal targeting a specific spending category",
    },
]

# ---------------------------------------------------------------------------
# Agent System Prompts
# ---------------------------------------------------------------------------
GOAL_DECOMPOSITION_PROMPT = """You are a financial goal decomposition specialist focused on Chinese household finance (amounts in RMB/元).

Given a user's financial goal and their profile, break it down into phased sub-tasks with weekly budget constraints.

Guidelines:
- Consider the user's income cycle (most Chinese salaries are paid monthly around the 10th-15th).
- Account for existing spending patterns and fixed expenses.
- Create realistic, achievable sub-tasks — aggressive but not punishing.
- Each phase should have a clear theme (e.g., "awareness week", "deep cut", "habit lock-in").
- Milestones should feel motivating and concrete.

You MUST respond with ONLY a JSON object in this exact schema — no extra text:
{
  "phases": [
    {
      "phase_number": 1,
      "name": "phase name",
      "duration_weeks": 2,
      "weekly_savings_target": 400,
      "weekly_budget_limit": 1200,
      "milestones": [
        {"week": 1, "description": "milestone description", "target_amount": 400}
      ]
    }
  ],
  "total_duration_weeks": 12,
  "summary": "one-paragraph summary of the plan"
}"""

PLANNING_PROMPT = """You are a financial planning specialist focused on Chinese consumer spending patterns.

Given decomposed goals and user spending patterns, generate a concrete execution plan with category-level budget adjustments.

Guidelines:
- Analyze each spending category for reduction potential.
- Prioritize cuts in discretionary categories (外卖/delivery, 娱乐/entertainment, 购物/shopping) before essentials.
- Generate actionable, specific tips — not generic advice.
- Consider Chinese lifestyle context (e.g., group meal culture, 双十一 sales temptation, WeChat Pay convenience).

You MUST respond with ONLY a JSON object in this exact schema — no extra text:
{
  "budget_plan": {
    "categories": [
      {
        "name": "category name",
        "current_avg": 900,
        "recommended": 630,
        "reduction_pct": 30,
        "strategy": "specific strategy for this category"
      }
    ]
  },
  "savings_schedule": [
    {"week": 1, "expected_savings": 400, "cumulative": 400}
  ],
  "risk_assessment": "brief risk assessment paragraph",
  "tips": ["specific actionable tip 1", "tip 2"]
}"""

EVENT_ROUTER_PROMPT = """You are a financial event classification and routing system.

Given an event, determine its priority, impact on active goals, and which agent should handle it.

Priority levels:
- critical: spending exceeds 80% of category budget, or a single expense > 50% of weekly budget
- high: large unexpected expense, bill due within 3 days, significant deviation
- medium: spending anomaly, pattern change, approaching threshold
- low: regular income, milestone reached, positive progress

Route mapping:
- execution_monitor: overspending, budget breaches, deviations
- insight: milestones, income events, pattern recognition
- planning: major life changes, new recurring expenses

You MUST respond with ONLY a JSON object in this exact schema — no extra text:
{
  "priority": "critical|high|medium|low",
  "event_category": "category string",
  "impact_on_goal": "description of impact",
  "route_to": "execution_monitor|insight|planning",
  "routing_rationale": "why this routing",
  "requires_immediate_action": true
}"""

EXECUTION_MONITOR_PROMPT = """You are a financial execution monitor.

Given the current plan, actual spending, and a triggering event, detect any deviation from the plan and generate an adjustment suggestion.

Deviation types:
- overspend: actual spending exceeds planned budget for a category or week
- underspend: spending significantly below plan (opportunity to accelerate savings)
- off_schedule: savings progress not tracking with the weekly schedule
- category_breach: a single category blew past its limit

Guidelines:
- Generate specific, actionable adjustment suggestions (not vague advice).
- Include concrete numbers — how much to cut, from which category, for how long.
- Consider whether the deviation is recoverable within the current phase.
- Be pragmatic: a small one-time overspend is different from a pattern.

You MUST respond with ONLY a JSON object in this exact schema — no extra text:
{
  "deviation_detected": true,
  "deviation_type": "overspend|underspend|off_schedule|category_breach",
  "deviation_amount": 500,
  "severity": "critical|high|medium|low",
  "suggestion": {
    "action": "reduce_category|reallocate|extend_timeline|accelerate",
    "description": "specific description of what to do",
    "expected_impact": "what this achieves",
    "adjusted_weekly_target": 450
  },
  "rationale": "explanation"
}"""

INSIGHT_PROMPT = """You are a financial insight generator for Chinese consumers.

Generate a brief, human-friendly explanation of why a certain action is recommended, considering the user's profile, goals, and current situation.

Guidelines:
- Be concise: 2-3 sentences maximum for the explanation.
- Be empathetic, not judgmental — no shaming about spending habits.
- Reference specific numbers from the plan (amounts in 元).
- Frame adjustments as smart moves, not failures.
- Use a warm, encouraging tone.

You MUST respond with ONLY a JSON object in this exact schema — no extra text:
{
  "headline": "short attention-grabbing headline",
  "explanation": "2-3 sentence explanation",
  "confidence": "high|medium|low",
  "supporting_factors": ["factor 1", "factor 2"],
  "risk_note": "brief risk note or empty string"
}"""

# ---------------------------------------------------------------------------
# Memory Helpers
# ---------------------------------------------------------------------------
DEFAULT_MEMORY = {
    "user_profile": {
        "monthly_income": 8000,
        "spending_patterns": {
            "餐饮": 1500,
            "外卖": 900,
            "交通": 400,
            "购物": 800,
            "娱乐": 600,
            "日用": 300,
            "通讯": 100,
        },
        "fixed_expenses": {"房租": 2000, "水电": 200},
        "risk_preference": "moderate",
        "intervention_history": [],
    },
    "working_memory": {
        "active_goal": None,
        "current_plan": None,
        "goal_progress": None,
        "recent_events": [],
        "pending_suggestions": [],
        "approved_actions": [],
    },
}


def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_MEMORY))


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def get_profile_context(profile):
    """Format user profile as markdown for prompt injection."""
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


def get_plan_context(working_memory):
    """Format current plan and progress as markdown for prompt injection."""
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
            desc = ev.get("event_data", {}).get("description",
                   json.dumps(ev.get("event_data", {}), ensure_ascii=False)[:60])
            lines.append(f"  - [{ev.get('event_type')}] {desc}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Claude API & SSE Helpers
# ---------------------------------------------------------------------------
def parse_json_response(text):
    """Multi-strategy JSON extraction from Claude's response text."""
    text = text.strip()
    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strategy 2: markdown code fences
    fence = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Strategy 3: outermost braces
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        try:
            return json.loads(text[i : j + 1])
        except json.JSONDecodeError:
            pass
    return {"raw_text": text}


def call_agent(agent_name, system_prompt, user_prompt, max_retries=3):
    """Call Claude API with retry + exponential backoff + JSON extraction."""
    last_error = None
    for attempt in range(max_retries):
        try:
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model=MODEL, max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return parse_json_response(resp.content[0].text)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
    return {"error": f"Agent {agent_name} failed after {max_retries} retries: {last_error}"}


def sse_event(event_type, data):
    """Format a single Server-Sent Event frame."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "index.html")

@app.route("/api/presets")
def get_presets():
    return jsonify(PRESETS)

@app.route("/api/status")
def get_status():
    mem = load_memory()
    return jsonify({"working_memory": mem.get("working_memory", {}),
                     "user_profile": mem.get("user_profile", {})})

@app.route("/api/plan", methods=["POST"])
def create_plan():
    """Decompose a financial goal and build an execution plan (SSE stream)."""
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
        decompose_prompt = (
            f"{profile_ctx}\n\n## Goal\n- Description: {goal}\n"
            f"- Type: {goal_type}\n- Target amount: {target_amount}元\n"
            f"- Timeframe: {target_days} days\n\n"
            f"Please decompose this goal into phased sub-tasks."
        )
        decomposition = call_agent(
            "goal_decomposition", GOAL_DECOMPOSITION_PROMPT, decompose_prompt)
        yield sse_event("agent_done", {"agent": "goal_decomposition", "result": decomposition})

        # --- Planning ---
        yield sse_event("agent_start", {"agent": "planning"})
        plan_prompt = (
            f"{profile_ctx}\n\n## Decomposed Goal\n"
            f"```json\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}\n```\n\n"
            f"Generate a concrete execution plan with category-level budget adjustments."
        )
        plan = call_agent("planning", PLANNING_PROMPT, plan_prompt)
        yield sse_event("agent_done", {"agent": "planning", "result": plan})

        # --- Update memory ---
        wm = memory.setdefault("working_memory", {})
        wm["active_goal"] = {
            "goal": goal, "goal_type": goal_type,
            "target_amount": target_amount, "target_days": target_days,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        wm["current_plan"] = plan
        total_weeks = decomposition.get("total_duration_weeks", target_days // 7)
        weekly_target = round(target_amount / max(total_weeks, 1), 2)
        wm["goal_progress"] = {
            "current_week": 1, "total_saved": 0,
            "weekly_target": weekly_target, "total_weeks": total_weeks,
            "decomposition": decomposition,
        }
        wm["pending_suggestions"] = []
        wm["approved_actions"] = []
        wm["recent_events"] = []
        save_memory(memory)

        yield sse_event("plan_complete", {
            "decomposition": decomposition, "plan": plan,
            "goal_progress": wm["goal_progress"],
        })
        yield sse_event("memory_update", {
            "working_memory": wm, "user_profile": profile,
        })

    return Response(stream(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    })


@app.route("/api/event", methods=["POST"])
def process_event():
    """Route and analyse a financial event (SSE stream)."""
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
            "id": str(uuid.uuid4())[:8], "event_type": event_type,
            "event_data": event_data, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        recent = wm.setdefault("recent_events", [])
        recent.append(event_record)
        wm["recent_events"] = recent[-10:]
        yield sse_event("event_received", event_record)

        ev_desc = json.dumps(event_data, ensure_ascii=False)

        # --- Event Router ---
        yield sse_event("agent_start", {"agent": "event_router"})
        router_prompt = (
            f"{profile_ctx}\n\n{plan_ctx}\n\n## New Event\n"
            f"- Type: {event_type}\n- Data: {ev_desc}\n\n"
            f"Classify this event and determine routing."
        )
        routing = call_agent("event_router", EVENT_ROUTER_PROMPT, router_prompt)
        yield sse_event("agent_done", {"agent": "event_router", "result": routing})

        # --- Execution Monitor ---
        yield sse_event("agent_start", {"agent": "execution_monitor"})
        monitor_prompt = (
            f"{profile_ctx}\n\n{plan_ctx}\n\n## Triggering Event\n"
            f"- Type: {event_type}\n- Data: {ev_desc}\n\n## Routing Info\n"
            f"- Priority: {routing.get('priority', 'medium')}\n"
            f"- Category: {routing.get('event_category', 'unknown')}\n\n"
            f"Analyze deviation and suggest adjustments."
        )
        monitor = call_agent("execution_monitor", EXECUTION_MONITOR_PROMPT, monitor_prompt)
        yield sse_event("agent_done", {"agent": "execution_monitor", "result": monitor})

        # --- Insight (conditional) ---
        insight = None
        if monitor.get("deviation_detected") or routing.get("requires_immediate_action"):
            yield sse_event("agent_start", {"agent": "insight"})
            insight_prompt = (
                f"{profile_ctx}\n\n{plan_ctx}\n\n"
                f"## Event\n- Type: {event_type}\n- Data: {ev_desc}\n\n"
                f"## Routing\n```json\n{json.dumps(routing, ensure_ascii=False)}\n```\n\n"
                f"## Monitor Analysis\n```json\n{json.dumps(monitor, ensure_ascii=False)}\n```\n\n"
                f"Generate a concise, empathetic insight for the user."
            )
            insight = call_agent("insight", INSIGHT_PROMPT, insight_prompt)
            yield sse_event("agent_done", {"agent": "insight", "result": insight})

        # --- Build suggestion ---
        suggestion = {
            "id": str(uuid.uuid4())[:8], "event_id": event_record["id"],
            "event_type": event_type, "routing": routing,
            "monitor": monitor, "insight": insight,
            "created_at": event_record["timestamp"], "status": "pending",
        }
        wm.setdefault("pending_suggestions", []).append(suggestion)
        save_memory(memory)

        yield sse_event("event_complete", {
            "event": event_record, "routing": routing, "monitor": monitor,
            "insight": insight, "suggestion_id": suggestion["id"],
        })
        yield sse_event("memory_update", {"working_memory": wm, "user_profile": profile})

    return Response(stream(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    })


@app.route("/api/approve", methods=["POST"])
def approve_suggestion():
    """Approve or reject a pending suggestion."""
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
        # Record successful intervention pattern in user profile
        profile = memory.get("user_profile", {})
        profile.setdefault("intervention_history", []).append({
            "event_type": target.get("event_type"),
            "action": suggestion_detail.get("action", "unknown"),
            "outcome": "approved", "timestamp": target["approved_at"],
        })
    else:
        target["status"] = "rejected"
        target["user_note"] = user_note

    wm["pending_suggestions"] = remaining
    save_memory(memory)
    return jsonify({
        "success": True, "suggestion_id": suggestion_id, "approved": approved,
        "working_memory": wm, "user_profile": memory.get("user_profile", {}),
    })


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
