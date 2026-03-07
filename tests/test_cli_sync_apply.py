"""Tests for sync apply helper."""

import json
from pathlib import Path

from key4ce.__main__ import _apply_sync_plan


class _FakeDB:
    def __init__(self, sessions=None):
        self._sessions = sessions or []
        self.imported = []

    def connect(self):
        return None

    def close(self):
        return None

    def import_sessions(self, sessions):
        self.imported.extend(sessions)
        return len(sessions)

    def list_sessions(self):
        return self._sessions


def test_sync_apply_pulls_remote_sessions(monkeypatch, tmp_path: Path):
    remote = {
        "goals": {"daily_minutes": 15, "daily_sessions": 1},
        "profile": {"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"},
        "sessions": [{"ts": "2026-01-01T00:00:00", "source": "sentences", "wpm": 51, "accuracy": 95, "duration": 60}],
    }
    target = tmp_path / "remote.json"
    target.write_text(json.dumps(remote), encoding="utf-8")

    fake_db = _FakeDB([])
    monkeypatch.setattr("key4ce.data.db.Database", lambda: fake_db)
    monkeypatch.setattr("key4ce.__main__._build_sync_plan", lambda _: {"actions": ["pull_sessions", "merge_goals", "merge_profile"]})

    calls = {"goals": 0, "profile": 0}
    monkeypatch.setattr("key4ce.__main__._save_goals", lambda *_: calls.__setitem__("goals", calls["goals"] + 1))
    monkeypatch.setattr("key4ce.__main__._save_profile", lambda *_: calls.__setitem__("profile", calls["profile"] + 1))

    out = _apply_sync_plan(str(target), mode="safe")
    assert out["inserted_sessions"] == 1
    assert calls == {"goals": 1, "profile": 1}


def test_sync_apply_push_writes_snapshot(monkeypatch, tmp_path: Path):
    target = tmp_path / "remote.json"
    target.write_text(json.dumps({"sessions": []}), encoding="utf-8")

    fake_db = _FakeDB([{"id": 1}])
    monkeypatch.setattr("key4ce.data.db.Database", lambda: fake_db)
    monkeypatch.setattr("key4ce.__main__._build_sync_plan", lambda _: {"actions": ["push_sessions"]})
    monkeypatch.setattr("key4ce.__main__._load_goals", lambda: {"daily_minutes": 10, "daily_sessions": 1})
    monkeypatch.setattr("key4ce.__main__._load_profile", lambda: {"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"})
    monkeypatch.setattr("key4ce.__main__._sessions_to_jsonable", lambda sessions: [{"ts": "2026-01-01T00:00:00"}])

    out = _apply_sync_plan(str(target), mode="safe")
    payload = json.loads(target.read_text(encoding="utf-8"))

    assert out["wrote_snapshot"] is True
    assert payload["count"] == 1
    assert isinstance(payload["sessions"], list)
