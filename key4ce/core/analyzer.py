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
    digraph: str       # two-character pair e.g. "th"
    avg_ms: float      # average inter-key time in ms
    deviation: float   # how much slower than overall average (positive = slower)


@dataclass
class SessionAnalysis:
    # Summary
    wpm: float
    accuracy: float
    duration_sec: float
    chars_typed: int
    total_errors: int

    # Detail
    top_errors: list[ErrorPair]      # most common mistake pairs, top 5
    slow_digraphs: list[SlowDigraph] # slowest two-char transitions, top 5
    problem_keys: list[str]          # single keys with highest error rate
    wpm_buckets: list[float]         # for graph

    # Serialisable error log (for DB)
    error_log: list[dict]


def analyse(timeline: KeystrokeTimeline) -> SessionAnalysis:
    """Build a full SessionAnalysis from a completed KeystrokeTimeline."""
    keystrokes = timeline.keystrokes

    # ── Basic stats ───────────────────────────────────────────────────────────
    correct_ks = [k for k in keystrokes if k.is_correct]
    error_ks = [k for k in keystrokes if not k.is_correct]

    chars_typed = len(correct_ks)
    total_errors = len(error_ks)
    wpm = timeline.final_wpm()
    accuracy = timeline.accuracy()
    duration = timeline.elapsed_seconds()

    # ── Error pairs ───────────────────────────────────────────────────────────
    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    error_log: list[dict] = []

    for k in error_ks:
        pair_counts[(k.expected, k.char)] += 1
        error_log.append({"expected": k.expected, "got": k.char})

    top_errors = sorted(
        [ErrorPair(e, g, c) for (e, g), c in pair_counts.items()],
        key=lambda x: -x.count,
    )[:5]

    # ── Slow digraphs ─────────────────────────────────────────────────────────
    # Only analyse correct keystrokes — we want real rhythm data
    slow_digraphs = _compute_slow_digraphs(correct_ks)

    # ── Problem keys ──────────────────────────────────────────────────────────
    key_errors: dict[str, int] = defaultdict(int)
    key_total: dict[str, int] = defaultdict(int)

    for k in keystrokes:
        key_total[k.expected] += 1
        if not k.is_correct:
            key_errors[k.expected] += 1

    # Sort by error rate, take top keys that had at least one error
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


def _compute_slow_digraphs(correct_ks: list[Keystroke]) -> list[SlowDigraph]:
    """Find which two-character transitions are slowest."""
    if len(correct_ks) < 2:
        return []

    intervals: dict[str, list[float]] = defaultdict(list)
    all_intervals: list[float] = []

    for i in range(1, len(correct_ks)):
        prev = correct_ks[i - 1]
        curr = correct_ks[i]
        # Only measure if consecutive positions (skip backtrack)
        if curr.position == prev.position + 1:
            ms = (curr.timestamp - prev.timestamp) * 1000
            if 0 < ms < 2000:  # sanity cap at 2s
                digraph = prev.expected + curr.expected
                intervals[digraph].append(ms)
                all_intervals.append(ms)

    if not all_intervals:
        return []

    overall_avg = sum(all_intervals) / len(all_intervals)

    results: list[SlowDigraph] = []
    for digraph, times in intervals.items():
        if len(times) < 2:  # not enough samples
            continue
        avg_ms = sum(times) / len(times)
        deviation = avg_ms - overall_avg
        results.append(SlowDigraph(digraph=digraph, avg_ms=avg_ms, deviation=deviation))

    return sorted(results, key=lambda d: -d.deviation)[:5]
