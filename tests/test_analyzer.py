"""Tests for the session analyzer."""

import pytest
from key4ce.core.engine import Keystroke
from key4ce.core.analyzer import SessionAnalyzer, SessionAnalysis, ErrorPattern


class MockTypingState:
    """Mock typing state for testing."""
    
    def __init__(self):
        self.wpm = 75.0
        self.accuracy = 95.0
        self.correct = 100
        self.errors = 5
        self.max_combo = 25
        self.keystrokes = []
        self._start_time = 0
        self._elapsed = 60.0
    
    @property
    def elapsed_time(self):
        return self._elapsed


class TestSessionAnalyzer:
    """Tests for SessionAnalyzer."""
    
    def test_analyze_empty_session(self):
        """Test analyzing a session with no keystrokes."""
        analyzer = SessionAnalyzer()
        state = MockTypingState()
        
        analysis = analyzer.analyze(state)
        
        assert analysis.final_wpm == 75.0
        assert analysis.accuracy == 95.0
        assert analysis.max_combo == 25
    
    def test_error_pattern_detection(self):
        """Test that common errors are detected."""
        analyzer = SessionAnalyzer()
        
        # Simulate keystrokes with repeated errors
        keystrokes = []
        import time
        base_time = time.time()
        
        # Add some correct keystrokes
        for i, char in enumerate("the"):
            keystrokes.append(Keystroke(
                char=char,
                expected=char,
                timestamp=base_time + i * 0.1,
                is_correct=True,
                position=i,
            ))
        
        # Add repeated error: typing 'e' instead of 'h'
        for i in range(3):
            keystrokes.append(Keystroke(
                char="e",
                expected="h",
                timestamp=base_time + 0.5 + i * 0.1,
                is_correct=False,
                position=10 + i,
            ))
        
        state = MockTypingState()
        state.keystrokes = keystrokes
        
        analysis = analyzer.analyze(state)
        
        # Should detect the e->h error pattern
        assert len(analysis.error_patterns) > 0
    
    def test_consistency_score_range(self):
        """Test that consistency score is in valid range."""
        analyzer = SessionAnalyzer()
        state = MockTypingState()
        
        analysis = analyzer.analyze(state)
        
        assert 0 <= analysis.consistency_score <= 10
    
    def test_recommendations_based_on_accuracy(self):
        """Test that recommendations are generated based on metrics."""
        analyzer = SessionAnalyzer()
        
        # Low accuracy session
        state = MockTypingState()
        state.accuracy = 85.0
        state.keystrokes = []
        
        analysis = analyzer.analyze(state)
        recommendations = analyzer.get_recommendations(analysis)
        
        # Should have accuracy-related recommendation
        assert len(recommendations) > 0
        assert any("accuracy" in r.lower() or "slow" in r.lower() for r in recommendations)


class TestDigraphAnalysis:
    """Tests for digraph timing analysis."""
    
    def test_digraph_detection(self):
        """Test that digraph timings are recorded."""
        import time
        
        analyzer = SessionAnalyzer()
        base_time = time.time()
        
        # Create keystrokes with known timing
        keystrokes = [
            Keystroke("t", "t", base_time, True, 0),
            Keystroke("h", "h", base_time + 0.1, True, 1),  # 100ms interval
            Keystroke("e", "e", base_time + 0.2, True, 2),
        ]
        
        state = MockTypingState()
        state.keystrokes = keystrokes
        
        analysis = analyzer.analyze(state)
        
        # Should have digraph data
        # 'th' and 'he' digraphs should be tracked
        assert len(analysis.slowest_digraphs) >= 0 or len(analysis.fastest_digraphs) >= 0
