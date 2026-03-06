"""Tests for sync-plan helper."""

import json
from pathlib import Path

from key4ce.__main__ import _build_sync_plan


class _FakeDB:
    def __init__(self, n):
        self._n = n

    def connect(self):
        return None

    def close(self):
        return None

    def list_sessions(self):
        return [object() for _ in range(self._n)]


def test_sync_plan_push_when_local_has_more(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("key4ce.data.db.Database", lambda: _FakeDB(5))
    monkeypatch.setattr("key4ce.__main__._load_goals", lambda: {"daily_minutes": 10, "daily_sessions": 1})
    monkeypatch.setattr("key4ce.__main__._load_profile", lambda: {"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"})

    target = tmp_path / "remote.json"
    target.write_text(json.dumps({"sessions": [{}]}), encoding="utf-8")

    plan = _build_sync_plan(str(target))
    assert "push_sessions" in plan["actions"]
