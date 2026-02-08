"""Tests for the core typing engine."""

import time
import pytest
from key4ce.core.engine import TypingEngine, TypingState, KeystrokeResult


class TestTypingState:
    """Tests for TypingState dataclass."""
    
    def test_initial_state(self):
        """Test initial state values."""
        state = TypingState(text="hello")
        
        assert state.position == 0
        assert state.errors == 0
        assert state.correct == 0
        assert state.combo == 0
        assert state.progress == 0.0
        assert not state.is_complete
    
    def test_typed_text(self):
        """Test typed_text property."""
        state = TypingState(text="hello")
        state.position = 3
        
        assert state.typed_text == "hel"
        assert state.remaining_text == "lo"
    
    def test_current_char(self):
        """Test current_char property."""
        state = TypingState(text="hello")
        
        assert state.current_char == "h"
        state.position = 2
        assert state.current_char == "l"
        state.position = 5
        assert state.current_char is None
    
    def test_progress_calculation(self):
        """Test progress percentage calculation."""
        state = TypingState(text="hello")
        
        assert state.progress == 0.0
        state.position = 2
        assert state.progress == 40.0
        state.position = 5
        assert state.progress == 100.0
    
    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        state = TypingState(text="hello")
        state.correct = 8
        state.errors = 2
        
        assert state.accuracy == 80.0
    
    def test_accuracy_empty(self):
        """Test accuracy with no keystrokes."""
        state = TypingState(text="hello")
        assert state.accuracy == 100.0


class TestTypingEngine:
    """Tests for TypingEngine."""
    
    def test_init(self):
        """Test engine initialization."""
        engine = TypingEngine("test text")
        
        assert engine.state.text == "test text"
        assert not engine.is_started
        assert not engine.is_complete
    
    def test_correct_keystroke(self):
        """Test processing correct keystrokes."""
        engine = TypingEngine("abc")
        
        result = engine.process_key("a")
        
        assert result == KeystrokeResult.CORRECT
        assert engine.state.position == 1
        assert engine.state.correct == 1
        assert engine.state.errors == 0
        assert engine.state.combo == 1
    
    def test_incorrect_keystroke(self):
        """Test processing incorrect keystrokes."""
        engine = TypingEngine("abc")
        
        result = engine.process_key("x")
        
        assert result == KeystrokeResult.INCORRECT
        assert engine.state.position == 0  # Position doesn't advance on error
        assert engine.state.errors == 1
        assert engine.state.combo == 0
    
    def test_combo_tracking(self):
        """Test combo counter."""
        engine = TypingEngine("hello")
        
        for char in "hel":
            engine.process_key(char)
        
        assert engine.state.combo == 3
        assert engine.state.max_combo == 3
        
        # Error breaks combo
        engine.process_key("x")
        assert engine.state.combo == 0
        assert engine.state.max_combo == 3
    
    def test_text_completion(self):
        """Test completing the text."""
        engine = TypingEngine("hi")
        
        engine.process_key("h")
        result = engine.process_key("i")
        
        assert result == KeystrokeResult.TEXT_COMPLETE
        assert engine.is_complete
    
    def test_backspace(self):
        """Test backspace handling."""
        engine = TypingEngine("hello")
        
        engine.process_key("h")
        engine.process_key("e")
        assert engine.state.position == 2
        
        result = engine.process_key("\b")
        assert result == KeystrokeResult.BACKSPACE
        assert engine.state.position == 1
    
    def test_word_complete(self):
        """Test word completion detection."""
        engine = TypingEngine("ab cd")
        
        engine.process_key("a")
        engine.process_key("b")
        result = engine.process_key(" ")
        
        assert result == KeystrokeResult.WORD_COMPLETE
    
    def test_timer_starts_on_first_key(self):
        """Test that timer starts on first keystroke."""
        engine = TypingEngine("test")
        
        assert engine.state.start_time is None
        engine.process_key("t")
        assert engine.state.start_time is not None
    
    def test_keystroke_callback(self):
        """Test keystroke callback is called."""
        keystrokes = []
        
        def callback(ks):
            keystrokes.append(ks)
        
        engine = TypingEngine("ab", on_keystroke=callback)
        engine.process_key("a")
        engine.process_key("x")
        
        assert len(keystrokes) == 2
        assert keystrokes[0].is_correct
        assert not keystrokes[1].is_correct
    
    def test_combo_break_callback(self):
        """Test combo break callback."""
        combo_breaks = []
        
        def callback(combo):
            combo_breaks.append(combo)
        
        engine = TypingEngine("abcd", on_combo_break=callback)
        
        for char in "abc":
            engine.process_key(char)
        
        engine.process_key("x")  # Break combo
        
        assert len(combo_breaks) == 1
        assert combo_breaks[0] == 3
    
    def test_reset(self):
        """Test engine reset."""
        engine = TypingEngine("hello")
        
        engine.process_key("h")
        engine.process_key("e")
        
        engine.reset()
        
        assert engine.state.position == 0
        assert engine.state.combo == 0
        assert engine.state.start_time is None
    
    def test_reset_with_new_text(self):
        """Test reset with new text."""
        engine = TypingEngine("hello")
        engine.process_key("h")
        
        engine.reset("world")
        
        assert engine.state.text == "world"
        assert engine.state.position == 0


class TestWPMCalculation:
    """Tests for WPM calculation."""
    
    def test_wpm_zero_time(self):
        """Test WPM with near-zero time."""
        state = TypingState(text="hello")
        state.start_time = time.time()
        
        # Should return 0, not divide by zero
        assert state.wpm == 0.0
    
    def test_wpm_calculation(self):
        """Test WPM formula (5 chars = 1 word)."""
        state = TypingState(text="hello world test")
        state.correct = 15  # 3 words (15 chars / 5)
        state.start_time = time.time() - 60  # 1 minute ago
        
        # 3 words / 1 minute = 3 WPM
        assert abs(state.wpm - 3.0) < 0.5  # Allow small timing variance
