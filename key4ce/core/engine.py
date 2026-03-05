"""Core typing session state machine with compatibility helpers."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

from key4ce.core.recorder import Keystroke, KeystrokeTimeline


class SessionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    COMPLETE = auto()


class KeystrokeResult(Enum):
    CORRECT = auto()
    INCORRECT = auto()
    BACKSPACE = auto()
    WORD_COMPLETE = auto()
    TEXT_COMPLETE = auto()


@dataclass
class TypingState:
    """Legacy-compatible state model used by tests and old UI code."""

    text: str
    position: int = 0
    correct: int = 0
    errors: int = 0
    combo: int = 0
    max_combo: int = 0
    start_time: float | None = None
    error_positions: set[int] = field(default_factory=set)

    @property
    def is_complete(self) -> bool:
        return self.position >= len(self.text)

    @property
    def typed_text(self) -> str:
        return self.text[: self.position]

    @property
    def remaining_text(self) -> str:
        return self.text[self.position :]

    @property
    def current_char(self) -> str | None:
        if self.position >= len(self.text):
            return None
        return self.text[self.position]

    @property
    def progress(self) -> float:
        if not self.text:
            return 100.0
        return (self.position / len(self.text)) * 100

    @property
    def accuracy(self) -> float:
        total = self.correct + self.errors
        if total == 0:
            return 100.0
        return (self.correct / total) * 100

    @property
    def wpm(self) -> float:
        if self.start_time is None:
            return 0.0
        elapsed = time.time() - self.start_time
        if elapsed < 0.5:
            return 0.0
        return (self.correct / 5) / (elapsed / 60)


@dataclass
class TypingEngine:
    """Strict-mode typing engine.

    Cursor advances only on correct keys. Supports callbacks used by the
    Textual screens and compatibility methods expected by tests.
    """

    target_text: str
    source: str = "unknown"
    on_keystroke: Callable[[Keystroke], None] | None = None
    on_combo_break: Callable[[int], None] | None = None
    on_milestone: Callable[[str, int], None] | None = None

    position: int = field(default=0, init=False)
    session_state: SessionState = field(default=SessionState.IDLE, init=False)
    has_error: bool = field(default=False, init=False)
    last_error_char: str = field(default="", init=False)

    timeline: KeystrokeTimeline = field(default_factory=KeystrokeTimeline, init=False)
    _state: TypingState = field(init=False)

    def __post_init__(self) -> None:
        self._state = TypingState(text=self.target_text)

    @property
    def state(self) -> TypingState:
        return self._state

    @property
    def is_complete(self) -> bool:
        return self.session_state == SessionState.COMPLETE

    @property
    def is_running(self) -> bool:
        return self.session_state == SessionState.RUNNING

    @property
    def is_started(self) -> bool:
        return self.session_state != SessionState.IDLE

    @property
    def progress(self) -> float:
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

    def handle_char(self, char: str) -> None:
        if self.session_state == SessionState.COMPLETE:
            return

        if self.session_state == SessionState.IDLE:
            self.session_state = SessionState.RUNNING
            self.timeline.start_time = time.time()
            self._state.start_time = self.timeline.start_time

        if self.position >= len(self.target_text):
            return

        expected = self.target_text[self.position]
        is_correct = char == expected
        self.timeline.record(char, expected, self.position, is_correct=is_correct)
        ks = self.timeline.keystrokes[-1]

        if is_correct:
            self.position += 1
            self.has_error = False
            self.last_error_char = ""

            self._state.position = self.position
            self._state.correct += 1
            self._state.combo += 1
            self._state.max_combo = max(self._state.max_combo, self._state.combo)

            if self.on_keystroke:
                self.on_keystroke(ks)
            if self._state.combo in {10, 25, 50} and self.on_milestone:
                self.on_milestone("combo", self._state.combo)

            if self.position >= len(self.target_text):
                self.session_state = SessionState.COMPLETE
            return

        self.has_error = True
        self.last_error_char = char
        self._state.errors += 1
        self._state.error_positions.add(self.position)
        prev_combo = self._state.combo
        self._state.combo = 0

        if prev_combo > 0 and self.on_combo_break:
            self.on_combo_break(prev_combo)
        if self.on_keystroke:
            self.on_keystroke(ks)

    def handle_backspace(self) -> None:
        if self.session_state == SessionState.COMPLETE:
            return
        if self.position > 0:
            self.position -= 1
            self._state.position = self.position
        self.has_error = False
        self.last_error_char = ""

    def process_key(self, key: str) -> KeystrokeResult:
        if key == "\b":
            self.handle_backspace()
            return KeystrokeResult.BACKSPACE

        before_pos = self.position
        self.handle_char(key)

        if self.is_complete:
            return KeystrokeResult.TEXT_COMPLETE
        if self.position > before_pos and key == " ":
            return KeystrokeResult.WORD_COMPLETE
        if self.position > before_pos:
            return KeystrokeResult.CORRECT
        return KeystrokeResult.INCORRECT

    def reset(self, text: str | None = None) -> None:
        if text is not None:
            self.target_text = text
        self.position = 0
        self.session_state = SessionState.IDLE
        self.has_error = False
        self.last_error_char = ""
        self.timeline = KeystrokeTimeline()
        self._state = TypingState(text=self.target_text)

    def char_state(self, index: int) -> str:
        if index < self.position:
            return "typed"
        if index == self.position:
            return "cursor_error" if self.has_error else "cursor"
        return "upcoming"
