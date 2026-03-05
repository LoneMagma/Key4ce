"""Tests for leaderboard CLI helper."""

from dataclasses import dataclass

from key4ce.__main__ import _build_leaderboard


@dataclass
class _Session:
    id: int
    source: str
    wpm: float
    accuracy: float
    duration: float
    chars_typed: int


def test_build_leaderboard_sorts_descending():
    rows = _build_leaderboard(
        [
            _Session(id=1, source="sentences", wpm=50, accuracy=98, duration=60, chars_typed=250),
            _Session(id=2, source="sentences", wpm=72, accuracy=92, duration=60, chars_typed=260),
            _Session(id=3, source="words", wpm=66, accuracy=97, duration=60, chars_typed=240),
        ],
        limit=2,
    )
    assert [r["id"] for r in rows] == [2, 3]
    assert [r["rank"] for r in rows] == [1, 2]


def test_build_leaderboard_filters_source():
    rows = _build_leaderboard(
        [
            _Session(id=1, source="sentences", wpm=50, accuracy=98, duration=60, chars_typed=250),
            _Session(id=2, source="words", wpm=72, accuracy=92, duration=60, chars_typed=260),
        ],
        limit=5,
        source="sentences",
    )
    assert len(rows) == 1
    assert rows[0]["source"] == "sentences"
