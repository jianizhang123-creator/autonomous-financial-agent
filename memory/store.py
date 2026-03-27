"""
Persistent memory store — load / save the dual-layer memory (Working Memory +
User Profile) as a JSON file.
"""

import json

from config import MEMORY_FILE

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


def load_memory() -> dict:
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_MEMORY))


def save_memory(memory: dict) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
