"""Keystroke timeline recorder for post-session analysis."""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Keystroke:
    char: str           # the character typed
    expected: str       # what was expected at this position
    timestamp: float    # absolute time.time()
    is_correct: bool    # did it advance the cursor?
    position: int       # cursor position at time of keypress


@dataclass
class KeystrokeTimeline:
    start_time: float = field(default_factory=time.time)
    keystrokes: list[Keystroke] = field(default_factory=list)

    # ── Rolling WPM ───────────────────────────────────────────────────────────

    def snapshot_wpm(self, window_sec: float = 5.0) -> float:
        """Rolling WPM over the last `window_sec` seconds."""
        now = time.time()
        cutoff = now - window_sec
        correct_in_window = sum(
            1 for k in self.keystrokes if k.is_correct and k.timestamp >= cutoff
        )
        elapsed = min(now - self.start_time, window_sec)
        if elapsed < 0.5:
            return 0.0
        return (correct_in_window / 5) / (elapsed / 60)

    def final_wpm(self) -> float:
        """Net WPM over the full session duration."""
        elapsed = self.elapsed_seconds()
        if elapsed < 1.0:
            return 0.0
        correct = sum(1 for k in self.keystrokes if k.is_correct)
        return (correct / 5) / (elapsed / 60)

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    # ── Accuracy ──────────────────────────────────────────────────────────────

    def accuracy(self) -> float:
        """Percentage of correct key presses (ignoring backspace)."""
        total = len(self.keystrokes)
        if total == 0:
            return 100.0
        correct = sum(1 for k in self.keystrokes if k.is_correct)
        return (correct / total) * 100

    # ── Record ────────────────────────────────────────────────────────────────

    def record(self, char: str, expected: str, position: int, is_correct: bool) -> None:
        self.keystrokes.append(
            Keystroke(
                char=char,
                expected=expected,
                timestamp=time.time(),
                is_correct=is_correct,
                position=position,
            )
        )

    # ── Per-second WPM buckets (for graph) ────────────────────────────────────

    def wpm_buckets(self, bucket_sec: float = 5.0) -> list[float]:
        """Return WPM per time bucket from start to end. Used for the graph."""
        if not self.keystrokes:
            return []

        total = self.elapsed_seconds()
        n_buckets = max(1, int(total / bucket_sec))
        result: list[float] = []

        for b in range(n_buckets):
            lo = self.start_time + b * bucket_sec
            hi = lo + bucket_sec
            chars = sum(
                1 for k in self.keystrokes
                if k.is_correct and lo <= k.timestamp < hi
            )
            wpm = (chars / 5) / (bucket_sec / 60)
            result.append(round(wpm, 1))

        return result
