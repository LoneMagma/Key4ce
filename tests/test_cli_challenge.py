"""Tests for daily challenge helper."""

from datetime import date

from key4ce.__main__ import _daily_challenge_spec


def test_daily_challenge_is_deterministic_for_given_day():
    d = date(2026, 3, 5)
    a = _daily_challenge_spec(d)
    b = _daily_challenge_spec(d)
    assert a == b


def test_daily_challenge_shape():
    spec = _daily_challenge_spec(date(2026, 3, 5))
    assert set(spec.keys()) == {"date", "challenge_id", "category", "words"}
    assert spec["category"] in {"words", "sentences", "quotes", "code", "numbers"}
    assert spec["words"] in {25, 50, 100}
