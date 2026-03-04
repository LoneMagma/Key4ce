"""Tests for CLI export helpers."""

from dataclasses import dataclass

from key4ce.__main__ import _sessions_to_jsonable


@dataclass
class _Session:
    id: int
    ts: str
    source: str
    wpm: float
    accuracy: float
    duration: float
    chars_typed: int
    errors: list[dict]
    timings: list[int]


def test_sessions_to_jsonable_shape():
    records = [
        _Session(
            id=1,
            ts="2026-01-01T00:00:00",
            source="sentences",
            wpm=52.5,
            accuracy=96.0,
            duration=45.0,
            chars_typed=200,
            errors=[{"expected": "e", "got": "r"}],
            timings=[120, 110],
        )
    ]

    out = _sessions_to_jsonable(records)
    assert len(out) == 1
    assert out[0]["id"] == 1
    assert out[0]["source"] == "sentences"
    assert out[0]["chars_typed"] == 200
    assert out[0]["timings"] == [120, 110]
