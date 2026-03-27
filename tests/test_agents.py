"""
Tests for agent utilities — JSON parsing and prompt loading.
"""

import json
import sys
from pathlib import Path

import pytest

# Ensure project root is on the import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.base import parse_json_response, load_prompt


class TestParseJsonResponse:
    def test_direct_json(self):
        raw = json.dumps({"key": "value"})
        assert parse_json_response(raw) == {"key": "value"}

    def test_markdown_fence(self):
        raw = "Some text\n```json\n{\"a\": 1}\n```\nmore text"
        assert parse_json_response(raw) == {"a": 1}

    def test_outermost_braces(self):
        raw = 'Here is the result: {"b": 2} — done.'
        assert parse_json_response(raw) == {"b": 2}

    def test_fallback_raw_text(self):
        raw = "not json at all"
        result = parse_json_response(raw)
        assert result == {"raw_text": "not json at all"}


class TestLoadPrompt:
    def test_loads_existing_prompt(self):
        prompt = load_prompt("goal_decomposition")
        assert "financial goal decomposition" in prompt.lower()

    def test_missing_prompt_raises(self):
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_agent")
