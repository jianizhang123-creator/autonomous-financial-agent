"""
Tests for the dual-layer memory system — load, save, and context formatters.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.store import load_memory, save_memory, DEFAULT_MEMORY
from memory.user_profile import get_profile_context
from memory.working_memory import get_plan_context


class TestMemoryStore:
    def test_load_returns_default_when_missing(self, tmp_path):
        fake_path = tmp_path / "nonexistent.json"
        with patch("memory.store.MEMORY_FILE", fake_path):
            mem = load_memory()
        assert mem["user_profile"]["monthly_income"] == 8000
        assert mem["working_memory"]["active_goal"] is None

    def test_save_and_load_round_trip(self, tmp_path):
        fake_path = tmp_path / "test_memory.json"
        with patch("memory.store.MEMORY_FILE", fake_path):
            data = {"user_profile": {"monthly_income": 9999}, "working_memory": {}}
            save_memory(data)
            loaded = load_memory()
        assert loaded["user_profile"]["monthly_income"] == 9999


class TestUserProfileContext:
    def test_basic_profile(self):
        profile = DEFAULT_MEMORY["user_profile"]
        ctx = get_profile_context(profile)
        assert "8000元" in ctx
        assert "餐饮" in ctx
        assert "Risk preference" in ctx

    def test_surplus_calculation(self):
        profile = {
            "monthly_income": 10000,
            "spending_patterns": {"食品": 2000},
            "fixed_expenses": {"房租": 3000},
            "risk_preference": "aggressive",
        }
        ctx = get_profile_context(profile)
        assert "5000元" in ctx  # surplus = 10000 - 2000 - 3000


class TestWorkingMemoryContext:
    def test_no_active_goal(self):
        wm = {"active_goal": None}
        ctx = get_plan_context(wm)
        assert "No active goal" in ctx

    def test_with_active_goal(self):
        wm = {
            "active_goal": {"goal": "Save 5000", "goal_type": "savings",
                            "target_amount": 5000, "target_days": 90},
            "goal_progress": {"current_week": 2, "total_saved": 800, "weekly_target": 420},
            "current_plan": None,
            "recent_events": [],
        }
        ctx = get_plan_context(wm)
        assert "Save 5000" in ctx
        assert "800" in ctx
