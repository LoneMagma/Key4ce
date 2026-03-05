"""Tests for pace-drop CLI helpers."""

from key4ce.__main__ import _compute_speed_drops


def test_compute_speed_drops_returns_descending_top_n():
    drops = _compute_speed_drops([110, 300, 220, 150], top=2)
    assert drops == [
        {"position": 2, "ms": 300},
        {"position": 3, "ms": 220},
    ]


def test_compute_speed_drops_empty_input():
    assert _compute_speed_drops([], top=3) == []
