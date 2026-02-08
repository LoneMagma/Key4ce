"""Core typing engine for Key4ce.

Handles keystroke processing, timing, and real-time metrics calculation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class KeystrokeResult(Enum):
    """Result of processing a keystroke."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    BACKSPACE = "backspace"
    WORD_COMPLETE = "word_complete"
    TEXT_COMPLETE = "text_complete"


@dataclass
class Keystroke:
    """Record of a single keystroke."""
    char: str
    expected: str
    timestamp: float
    is_correct: bool
    position: int
    wpm_at_time: float = 0.0


@dataclass
class TypingState:
    """Current state of the typing session."""
    text: str
    position: int = 0
    errors: int = 0
    correct: int = 0
    start_time: float | None = None
    last_keystroke_time: float | None = None
    combo: int = 0
    max_combo: int = 0
    keystrokes: list[Keystroke] = field(default_factory=list)
    # Track which positions have errors (for highlighting)
    error_positions: set[int] = field(default_factory=set)
    
    @property
    def typed_text(self) -> str:
        """Get the text that has been typed so far."""
        return self.text[:self.position]
    
    @property
    def remaining_text(self) -> str:
        """Get the remaining text to type."""
        return self.text[self.position:]
    
    @property
    def current_char(self) -> str | None:
        """Get the current character to type."""
        if self.position < len(self.text):
            return self.text[self.position]
        return None
    
    @property
    def current_word(self) -> str:
        """Get the current word being typed."""
        # Find word boundaries
        start = self.text.rfind(" ", 0, self.position) + 1
        end = self.text.find(" ", self.position)
        if end == -1:
            end = len(self.text)
        return self.text[start:end]
    
    @property
    def progress(self) -> float:
        """Get completion progress as a percentage (0-100)."""
        if len(self.text) == 0:
            return 0.0
        return (self.position / len(self.text)) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if the text has been fully typed."""
        return self.position >= len(self.text)
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds since start."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy as a percentage."""
        total = self.correct + self.errors
        if total == 0:
            return 100.0
        return (self.correct / total) * 100
    
    @property
    def wpm(self) -> float:
        """Calculate current words per minute.
        
        Uses standard 5 characters = 1 word formula.
        """
        elapsed = self.elapsed_time
        if elapsed < 0.1:  # Avoid division by near-zero
            return 0.0
        
        # Standard: 5 characters = 1 word
        words = self.correct / 5
        minutes = elapsed / 60
        return words / minutes


class TypingEngine:
    """Core engine for processing typing input and tracking metrics.
    
    This engine allows fluid typing - errors don't block progress.
    Users can continue typing even after making mistakes, or use
    backspace to correct them.
    """
    
    def __init__(
        self,
        text: str,
        on_keystroke: Callable[[Keystroke], None] | None = None,
        on_combo_break: Callable[[int], None] | None = None,
        on_milestone: Callable[[str, int], None] | None = None,
    ) -> None:
        """Initialize the typing engine.
        
        Args:
            text: The text to type
            on_keystroke: Callback for each keystroke
            on_combo_break: Callback when combo breaks (receives combo count)
            on_milestone: Callback for milestones (type, value)
        """
        self._state = TypingState(text=text)
        self._on_keystroke = on_keystroke
        self._on_combo_break = on_combo_break
        self._on_milestone = on_milestone
        
        # Milestone tracking
        self._combo_milestones = {10, 25, 50, 100, 200}
        self._achieved_combo_milestones: set[int] = set()
    
    @property
    def state(self) -> TypingState:
        """Get the current typing state."""
        return self._state
    
    @property
    def is_started(self) -> bool:
        """Check if the session has started."""
        return self._state.start_time is not None
    
    @property
    def is_complete(self) -> bool:
        """Check if the text is complete."""
        return self._state.is_complete
    
    def process_key(self, char: str) -> KeystrokeResult:
        """Process a keystroke.
        
        Args:
            char: The character that was typed
            
        Returns:
            Result of the keystroke processing
        """
        now = time.time()
        
        # Start timer on first keystroke
        if self._state.start_time is None:
            self._state.start_time = now
        
        # Handle backspace
        if char == "\b" or char == "backspace":
            return self._handle_backspace(now)
        
        # Check if text is already complete
        if self._state.is_complete:
            return KeystrokeResult.TEXT_COMPLETE
        
        expected = self._state.current_char
        is_correct = char == expected
        
        # Record keystroke
        keystroke = Keystroke(
            char=char,
            expected=expected or "",
            timestamp=now,
            is_correct=is_correct,
            position=self._state.position,
            wpm_at_time=self._state.wpm,
        )
        self._state.keystrokes.append(keystroke)
        
        if is_correct:
            result = self._handle_correct(keystroke)
        else:
            result = self._handle_incorrect(keystroke)
        
        self._state.last_keystroke_time = now
        
        # Call keystroke callback
        if self._on_keystroke:
            self._on_keystroke(keystroke)
        
        return result
    
    def _handle_correct(self, keystroke: Keystroke) -> KeystrokeResult:
        """Handle a correct keystroke."""
        self._state.position += 1
        self._state.correct += 1
        self._state.combo += 1
        
        # Track max combo
        if self._state.combo > self._state.max_combo:
            self._state.max_combo = self._state.combo
        
        # Check for combo milestones
        self._check_combo_milestone()
        
        # Check if text is complete
        if self._state.is_complete:
            return KeystrokeResult.TEXT_COMPLETE
        
        # Check if word is complete
        if keystroke.char == " ":
            return KeystrokeResult.WORD_COMPLETE
        
        return KeystrokeResult.CORRECT
    
    def _handle_incorrect(self, keystroke: Keystroke) -> KeystrokeResult:
        """Handle an incorrect keystroke.
        
        IMPORTANT: The position ADVANCES even on errors - this creates a fluid
        typing experience. The incorrect position is tracked for display.
        """
        # Record error position for highlighting
        self._state.error_positions.add(self._state.position)
        
        # Advance position - don't block on errors!
        self._state.position += 1
        self._state.errors += 1
        
        # Break combo
        if self._state.combo > 0:
            if self._on_combo_break:
                self._on_combo_break(self._state.combo)
            self._state.combo = 0
            self._achieved_combo_milestones.clear()
        
        # Check if text is complete (even with errors)
        if self._state.is_complete:
            return KeystrokeResult.TEXT_COMPLETE
        
        return KeystrokeResult.INCORRECT
    
    def _handle_backspace(self, timestamp: float) -> KeystrokeResult:
        """Handle backspace key.
        
        Allows correcting errors by going back and retyping.
        """
        if self._state.position > 0:
            self._state.position -= 1
            
            # If we're going back to an error position, clear it
            # so the user can retype correctly
            if self._state.position in self._state.error_positions:
                self._state.error_positions.discard(self._state.position)
                # Don't adjust error count - we still made the error
        
        return KeystrokeResult.BACKSPACE
    
    def _check_combo_milestone(self) -> None:
        """Check and trigger combo milestones."""
        combo = self._state.combo
        
        for milestone in self._combo_milestones:
            if combo >= milestone and milestone not in self._achieved_combo_milestones:
                self._achieved_combo_milestones.add(milestone)
                if self._on_milestone:
                    self._on_milestone("combo", milestone)
    
    def get_interval_stats(self) -> dict[str, float]:
        """Calculate keystroke interval statistics.
        
        Returns:
            Dictionary with avg, min, max, and std deviation of intervals
        """
        if len(self._state.keystrokes) < 2:
            return {"avg": 0, "min": 0, "max": 0, "std": 0}
        
        intervals = []
        for i in range(1, len(self._state.keystrokes)):
            interval = (
                self._state.keystrokes[i].timestamp 
                - self._state.keystrokes[i-1].timestamp
            )
            intervals.append(interval * 1000)  # Convert to ms
        
        avg = sum(intervals) / len(intervals)
        min_val = min(intervals)
        max_val = max(intervals)
        
        # Standard deviation
        variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
        std = variance ** 0.5
        
        return {
            "avg": avg,
            "min": min_val,
            "max": max_val,
            "std": std,
        }
    
    def reset(self, new_text: str | None = None) -> None:
        """Reset the engine for a new session.
        
        Args:
            new_text: Optional new text to type (keeps current if None)
        """
        text = new_text if new_text is not None else self._state.text
        self._state = TypingState(text=text)
        self._achieved_combo_milestones.clear()
