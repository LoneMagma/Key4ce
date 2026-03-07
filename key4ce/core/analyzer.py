"""Post-session analysis for key4ce."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from key4ce.core.recorder import KeystrokeTimeline, Keystroke


@dataclass
class ErrorPair:
    expected: str
    got: str
    count: int


@dataclass
class SlowDigraph:
    digraph: str
    avg_ms: float
    deviation: float


@dataclass
class SessionAnalysis:
    wpm: float
    accuracy: float
    duration_sec: float
    chars_typed: int
    total_errors: int
    top_errors: list[ErrorPair]
    slow_digraphs: list[SlowDigraph]
    problem_keys: list[str]
    wpm_buckets: list[float]
    error_log: list[dict]


@dataclass
class ErrorPattern:
    expected: str
    typed: str
    count: int


@dataclass
class LegacySessionAnalysis:
    final_wpm: float
    accuracy: float
    max_combo: int
    consistency_score: float
    error_patterns: list[ErrorPattern]
    slowest_digraphs: list[SlowDigraph]
    fastest_digraphs: list[SlowDigraph]


def analyse(timeline: KeystrokeTimeline) -> SessionAnalysis:
    """Build a full SessionAnalysis from a completed KeystrokeTimeline."""
    keystrokes = timeline.keystrokes
    correct_ks = [k for k in keystrokes if k.is_correct]
    error_ks = [k for k in keystrokes if not k.is_correct]

    chars_typed = len(correct_ks)
    total_errors = len(error_ks)
    wpm = timeline.final_wpm()
    accuracy = timeline.accuracy()
    duration = timeline.elapsed_seconds()

    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    error_log: list[dict] = []
    for k in error_ks:
        pair_counts[(k.expected, k.char)] += 1
        error_log.append({"expected": k.expected, "got": k.char})

    top_errors = sorted(
        [ErrorPair(e, g, c) for (e, g), c in pair_counts.items()],
        key=lambda x: -x.count,
    )[:5]

    slow_digraphs = _compute_slow_digraphs(correct_ks)

    key_errors: dict[str, int] = defaultdict(int)
    key_total: dict[str, int] = defaultdict(int)
    for k in keystrokes:
        key_total[k.expected] += 1
        if not k.is_correct:
            key_errors[k.expected] += 1

    problem_keys = sorted(
        [ch for ch in key_errors if key_total[ch] > 0],
        key=lambda ch: -key_errors[ch] / max(key_total[ch], 1),
    )[:5]

    return SessionAnalysis(
        wpm=wpm,
        accuracy=accuracy,
        duration_sec=duration,
        chars_typed=chars_typed,
        total_errors=total_errors,
        top_errors=top_errors,
        slow_digraphs=slow_digraphs,
        problem_keys=problem_keys,
        wpm_buckets=timeline.wpm_buckets(),
        error_log=error_log,
    )


class SessionAnalyzer:
    """Compatibility analyzer for legacy tests."""

    def analyze(self, state) -> LegacySessionAnalysis:
        ks = list(getattr(state, "keystrokes", []))

        pair_counts: dict[tuple[str, str], int] = defaultdict(int)
        for k in ks:
            if not k.is_correct:
                pair_counts[(k.expected, k.char)] += 1
        patterns = [ErrorPattern(expected=e, typed=t, count=c) for (e, t), c in pair_counts.items()]

        consistency = 10.0
        if ks:
            # Simple consistency proxy from interval variance.
            intervals = [
                (ks[i].timestamp - ks[i - 1].timestamp) * 1000
                for i in range(1, len(ks))
                if ks[i].is_correct and ks[i - 1].is_correct
            ]
            if intervals:
                avg = sum(intervals) / len(intervals)
                variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
                consistency = max(0.0, min(10.0, 10.0 - (variance ** 0.5) / 20))

        slow = _compute_slow_digraphs([k for k in ks if k.is_correct])
        fast = sorted(slow, key=lambda d: d.avg_ms)[:5] if slow else []

        return LegacySessionAnalysis(
            final_wpm=float(getattr(state, "wpm", 0.0)),
            accuracy=float(getattr(state, "accuracy", 100.0)),
            max_combo=int(getattr(state, "max_combo", 0)),
            consistency_score=consistency,
            error_patterns=patterns,
            slowest_digraphs=slow,
            fastest_digraphs=fast,
        )

    def get_recommendations(self, analysis: LegacySessionAnalysis) -> list[str]:
        tips: list[str] = []
        if analysis.accuracy < 90:
            tips.append("Slow down slightly and prioritize accuracy.")
        if analysis.final_wpm < 40:
            tips.append("Practice shorter sessions daily to build rhythm.")
        if not tips:
            tips.append("Keep consistent practice to maintain progress.")
        return tips


def _compute_slow_digraphs(correct_ks: list[Keystroke]) -> list[SlowDigraph]:
    if len(correct_ks) < 2:
        return []

    intervals: dict[str, list[float]] = defaultdict(list)
    all_intervals: list[float] = []

    for i in range(1, len(correct_ks)):
        prev = correct_ks[i - 1]
        curr = correct_ks[i]
        if curr.position == prev.position + 1:
            ms = (curr.timestamp - prev.timestamp) * 1000
            if 0 < ms < 2000:
                digraph = prev.expected + curr.expected
                intervals[digraph].append(ms)
                all_intervals.append(ms)

    if not all_intervals:
        return []

    overall_avg = sum(all_intervals) / len(all_intervals)

    results: list[SlowDigraph] = []
    for digraph, times in intervals.items():
        if len(times) < 1:
            continue
        avg_ms = sum(times) / len(times)
        deviation = avg_ms - overall_avg
        results.append(SlowDigraph(digraph=digraph, avg_ms=avg_ms, deviation=deviation))

    return sorted(results, key=lambda d: -d.deviation)[:5]
