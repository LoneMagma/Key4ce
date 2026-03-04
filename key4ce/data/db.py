"""SQLite persistence layer for key4ce sessions."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DB_PATH = Path.home() / ".key4ce" / "sessions.db"

_CREATE_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT    NOT NULL,
    source      TEXT    NOT NULL,
    wpm         REAL    NOT NULL,
    accuracy    REAL    NOT NULL,
    duration    REAL    NOT NULL,
    chars_typed INTEGER NOT NULL,
    errors      TEXT    NOT NULL DEFAULT '[]',
    timings     TEXT    NOT NULL DEFAULT '[]'
);
"""


@dataclass
class SessionRecord:
    id: int
    ts: str
    source: str
    wpm: float
    accuracy: float
    duration: float
    chars_typed: int
    errors: list[dict]
    timings: list[int]   # ms between correct keystrokes


@dataclass
class StatsSnapshot:
    total_sessions: int
    best_wpm: float
    avg_wpm: float
    avg_accuracy: float
    recent_sessions: list[SessionRecord]


@dataclass
class FocusData:
    """Aggregated weak spots from recent sessions."""

    weak_digraphs: list[str]   # ordered worst→best
    problem_chars: list[str]


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(str(self._path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_CREATE_SQL)
        self._conn.commit()
        self._maybe_migrate()

    def _maybe_migrate(self) -> None:
        cols = {row[1] for row in self._conn.execute("PRAGMA table_info(sessions)")}
        if "timings" not in cols:
            try:
                self._conn.execute("ALTER TABLE sessions ADD COLUMN timings TEXT NOT NULL DEFAULT '[]'")
                self._conn.commit()
            except Exception:
                pass

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ── Write ──────────────────────────────────────────────────────────────────

    def save_session(
        self,
        source: str,
        wpm: float,
        accuracy: float,
        duration: float,
        chars_typed: int,
        errors: list[dict],
        timings: list[int] | None = None,
    ) -> int:
        return self._insert_session(
            ts=datetime.now().isoformat(),
            source=source,
            wpm=wpm,
            accuracy=accuracy,
            duration=duration,
            chars_typed=chars_typed,
            errors=errors,
            timings=timings,
        )

    def import_sessions(self, sessions: list[dict]) -> int:
        """Import sessions from exported JSON format, skipping exact duplicates."""
        assert self._conn, "Not connected"
        inserted = 0

        existing = {
            (r["ts"], r["source"], float(r["wpm"]), float(r["accuracy"]), float(r["duration"]))
            for r in self._conn.execute("SELECT ts, source, wpm, accuracy, duration FROM sessions").fetchall()
        }

        for s in sessions:
            key = (
                str(s.get("ts", "")),
                str(s.get("source", "")),
                float(s.get("wpm", 0.0)),
                float(s.get("accuracy", 0.0)),
                float(s.get("duration", 0.0)),
            )
            if not key[0] or not key[1] or key in existing:
                continue

            self._insert_session(
                ts=key[0],
                source=key[1],
                wpm=key[2],
                accuracy=key[3],
                duration=key[4],
                chars_typed=int(s.get("chars_typed", 0)),
                errors=list(s.get("errors", [])),
                timings=list(s.get("timings", [])),
            )
            existing.add(key)
            inserted += 1

        return inserted

    def _insert_session(
        self,
        ts: str,
        source: str,
        wpm: float,
        accuracy: float,
        duration: float,
        chars_typed: int,
        errors: list[dict],
        timings: list[int] | None = None,
    ) -> int:
        assert self._conn, "Not connected"
        cur = self._conn.execute(
            """INSERT INTO sessions
               (ts, source, wpm, accuracy, duration, chars_typed, errors, timings)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                source,
                round(wpm, 2),
                round(accuracy, 2),
                round(duration, 2),
                chars_typed,
                json.dumps(errors),
                json.dumps(timings or []),
            ),
        )
        self._conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_stats(self) -> StatsSnapshot:
        assert self._conn, "Not connected"
        row = self._conn.execute("SELECT COUNT(*), MAX(wpm), AVG(wpm), AVG(accuracy) FROM sessions").fetchone()
        total, best, avg_wpm, avg_acc = row
        recent_rows = self._conn.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 10").fetchall()
        return StatsSnapshot(
            total_sessions=total or 0,
            best_wpm=round(best or 0.0, 2),
            avg_wpm=round(avg_wpm or 0.0, 2),
            avg_accuracy=round(avg_acc or 0.0, 2),
            recent_sessions=[self._row_to_record(r) for r in recent_rows],
        )

    def list_sessions(self, limit: int | None = None) -> list[SessionRecord]:
        assert self._conn, "Not connected"
        if limit is None:
            rows = self._conn.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (max(1, int(limit)),)).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_best_wpm_for_source(self, source: str) -> float:
        assert self._conn, "Not connected"
        row = self._conn.execute("SELECT MAX(wpm) FROM sessions WHERE source = ?", (source,)).fetchone()
        return row[0] or 0.0

    def get_ghost_timings(self, source: str) -> list[int]:
        assert self._conn, "Not connected"
        row = self._conn.execute(
            "SELECT timings FROM sessions WHERE source = ? ORDER BY wpm DESC LIMIT 1",
            (source,),
        ).fetchone()
        if row and row["timings"]:
            data = json.loads(row["timings"])
            return data if isinstance(data, list) else []
        return []

    def get_focus_data(self, n_sessions: int = 10) -> FocusData:
        assert self._conn, "Not connected"
        rows = self._conn.execute("SELECT errors FROM sessions ORDER BY id DESC LIMIT ?", (n_sessions,)).fetchall()

        from collections import Counter

        digraph_errors: Counter[str] = Counter()
        char_errors: Counter[str] = Counter()

        for row in rows:
            errors = json.loads(row["errors"])
            for e in errors:
                expected = e.get("expected", "")
                if expected and len(expected) == 1:
                    char_errors[expected] += 1

        for row in rows:
            errors = json.loads(row["errors"])
            chars = [e.get("expected", "") for e in errors if e.get("expected")]
            for i in range(len(chars) - 1):
                if chars[i] and chars[i + 1]:
                    digraph_errors[chars[i] + chars[i + 1]] += 1

        weak_digraphs = [dg for dg, _ in digraph_errors.most_common(5)]
        problem_chars = [ch for ch, _ in char_errors.most_common(5)]
        return FocusData(weak_digraphs=weak_digraphs, problem_chars=problem_chars)

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> SessionRecord:
        timings_raw = row["timings"] if "timings" in row.keys() else "[]"
        return SessionRecord(
            id=row["id"],
            ts=row["ts"],
            source=row["source"],
            wpm=row["wpm"],
            accuracy=row["accuracy"],
            duration=row["duration"],
            chars_typed=row["chars_typed"],
            errors=json.loads(row["errors"]),
            timings=json.loads(timings_raw) if timings_raw else [],
        )
