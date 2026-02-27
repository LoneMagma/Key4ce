"""Core typing session state machine."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from key4ce.core.recorder import KeystrokeTimeline


class SessionState(Enum):
    IDLE = auto()       # not started yet (waiting for first keypress)
    RUNNING = auto()    # actively typing
    COMPLETE = auto()   # finished all characters


@dataclass
class TypingEngine:
    """Strict-mode typing engine.

    The cursor only advances when the correct character is typed.
    Backspace moves the cursor back one position.
    An error flag is set when a wrong key is pressed — it clears on correct input.
    """

    target_text: str
    source: str = "unknown"

    # ── State ──────────────────────────────────────────────────────────────────
    position: int = field(default=0, init=False)
    state: SessionState = field(default=SessionState.IDLE, init=False)
    has_error: bool = field(default=False, init=False)  # red cursor indicator
    last_error_char: str = field(default="", init=False)

    timeline: KeystrokeTimeline = field(default_factory=KeystrokeTimeline, init=False)

    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def is_complete(self) -> bool:
        return self.state == SessionState.COMPLETE

    @property
    def is_running(self) -> bool:
        return self.state == SessionState.RUNNING

    @property
    def progress(self) -> float:
        """0.0 – 1.0"""
        return self.position / max(len(self.target_text), 1)

    @property
    def wpm(self) -> float:
        return self.timeline.snapshot_wpm()

    @property
    def accuracy(self) -> float:
        return self.timeline.accuracy()

    @property
    def elapsed(self) -> float:
        return self.timeline.elapsed_seconds()

    # ── Input handling ─────────────────────────────────────────────────────────

    def handle_char(self, char: str) -> None:
        """Process one typed character. Ignores input when complete."""
        if self.state == SessionState.COMPLETE:
            return

        # First keypress starts the clock
        if self.state == SessionState.IDLE:
            self.state = SessionState.RUNNING
            self.timeline.start_time = time.time()

        if self.position >= len(self.target_text):
            return

        expected = self.target_text[self.position]

        if char == expected:
            self.timeline.record(char, expected, self.position, is_correct=True)
            self.position += 1
            self.has_error = False
            self.last_error_char = ""

            if self.position >= len(self.target_text):
                self.state = SessionState.COMPLETE
        else:
            self.timeline.record(char, expected, self.position, is_correct=False)
            self.has_error = True
            self.last_error_char = char

    def handle_backspace(self) -> None:
        """Move cursor back one position (if not at start)."""
        if self.state == SessionState.COMPLETE:
            return
        if self.position > 0:
            self.position -= 1
        self.has_error = False
        self.last_error_char = ""

    # ── Display helpers ────────────────────────────────────────────────────────

    def char_state(self, index: int) -> str:
        """Return display state for a character at a given index.

        Returns one of: 'typed', 'cursor', 'cursor_error', 'upcoming'
        """
        if index < self.position:
            return "typed"
        if index == self.position:
            return "cursor_error" if self.has_error else "cursor"
        return "upcoming"
