"""
Integration tests for the Flask API routes.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestPresetsRoute:
    def test_returns_presets(self, client):
        res = client.get("/api/presets")
        data = res.get_json()
        assert res.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["id"] == "save_5000"


class TestStatusRoute:
    def test_returns_status(self, client, tmp_path):
        fake_path = tmp_path / "mem.json"
        with patch("memory.store.MEMORY_FILE", fake_path):
            res = client.get("/api/status")
        data = res.get_json()
        assert "working_memory" in data
        assert "user_profile" in data


class TestApproveRoute:
    def test_not_found(self, client, tmp_path):
        fake_path = tmp_path / "mem.json"
        with patch("memory.store.MEMORY_FILE", fake_path):
            res = client.post("/api/approve",
                              data=json.dumps({"suggestion_id": "nope", "approved": True}),
                              content_type="application/json")
        assert res.status_code == 404
