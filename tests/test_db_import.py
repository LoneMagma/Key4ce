"""Tests for database import path."""

from pathlib import Path

from key4ce.data.db import Database


def test_import_sessions_inserts_and_skips_duplicates(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    db = Database(path=db_path)
    db.connect()

    payload = [
        {
            "ts": "2026-01-01T10:00:00",
            "source": "sentences",
            "wpm": 50.0,
            "accuracy": 95.0,
            "duration": 60.0,
            "chars_typed": 200,
            "errors": [],
            "timings": [100, 120],
        },
        {
            "ts": "2026-01-02T10:00:00",
            "source": "code",
            "wpm": 40.0,
            "accuracy": 90.0,
            "duration": 70.0,
            "chars_typed": 180,
            "errors": [{"expected": "e", "got": "r"}],
            "timings": [130],
        },
    ]

    assert db.import_sessions(payload) == 2
    # second import should skip exact duplicates
    assert db.import_sessions(payload) == 0

    sessions = db.list_sessions()
    assert len(sessions) == 2
    assert sessions[0].source in {"sentences", "code"}

    db.close()
