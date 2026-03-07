"""Tests for snapshot/restore helpers."""

import json
from dataclasses import dataclass
from pathlib import Path

from key4ce.__main__ import _restore_snapshot_from_file


class _FakeDB:
    def connect(self):
        return None

    def close(self):
        return None

    def import_sessions(self, sessions):
        return len(sessions)


def test_restore_snapshot_restores_flags_and_counts(tmp_path: Path, monkeypatch):
    snapshot = {
        "goals": {"daily_minutes": 20, "daily_sessions": 2},
        "profile": {"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"},
        "sessions": [{"ts": "2026-01-01T00:00:00", "source": "sentences", "wpm": 50, "accuracy": 95, "duration": 60}],
    }
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    calls = {"goals": 0, "profile": 0}

    monkeypatch.setattr("key4ce.__main__._save_goals", lambda goals: calls.__setitem__("goals", calls["goals"] + 1))
    monkeypatch.setattr("key4ce.__main__._save_profile", lambda profile: calls.__setitem__("profile", calls["profile"] + 1))
    monkeypatch.setattr("key4ce.data.db.Database", _FakeDB)

    out = _restore_snapshot_from_file(str(path))
    assert out["inserted_sessions"] == 1
    assert out["restored_goals"] is True
    assert out["restored_profile"] is True
    assert calls == {"goals": 1, "profile": 1}
