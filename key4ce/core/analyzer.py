"""Session analyzer for Key4ce.

Provides detailed analysis of typing sessions including error patterns,
digraph speeds, and performance insights.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from key4ce.core.engine import TypingState, Keystroke


@dataclass
class ErrorPattern:
    """Pattern of a common typing error."""
    typed: str
    expected: str
    count: int
    positions: list[int] = field(default_factory=list)


@dataclass
class DigraphStats:
    """Statistics for a character pair (digraph)."""
    chars: str
    avg_time_ms: float
    count: int
    times: list[float] = field(default_factory=list)


@dataclass
class SessionAnalysis:
    """Complete analysis of a typing session."""
    # Basic metrics
    final_wpm: float
    accuracy: float
    total_chars: int
    total_errors: int
    total_time_seconds: float
    
    # Consistency
    consistency_score: float  # 0-10 scale
    wpm_variance: float
    
    # Error analysis
    error_patterns: list[ErrorPattern]
    
    # Digraph analysis
    slowest_digraphs: list[DigraphStats]
    fastest_digraphs: list[DigraphStats]
    
    # Keystroke timing
    avg_interval_ms: float
    interval_std_ms: float
    
    # Combo stats
    max_combo: int
    avg_combo: float
    
    # Performance over time
    wpm_timeline: list[tuple[float, float]]  # (time_seconds, wpm)


class SessionAnalyzer:
    """Analyzes typing sessions for insights and recommendations."""
    
    def __init__(self) -> None:
        self._digraph_times: dict[str, list[float]] = defaultdict(list)
        self._error_counts: dict[str, int] = defaultdict(int)
        self._error_positions: dict[str, list[int]] = defaultdict(list)
        self._wpm_samples: list[tuple[float, float]] = []
        self._combo_lengths: list[int] = []
    
    def analyze(self, state: TypingState) -> SessionAnalysis:
        """Perform full analysis of a typing session.
        
        Args:
            state: The final typing state to analyze
            
        Returns:
            Complete session analysis
        """
        self._process_keystrokes(state.keystrokes)
        
        # Calculate consistency (lower variance = more consistent)
        consistency = self._calculate_consistency()
        
        # Get error patterns
        error_patterns = self._get_error_patterns()
        
        # Get digraph stats
        slowest = self._get_slowest_digraphs(5)
        fastest = self._get_fastest_digraphs(5)
        
        # Calculate WPM timeline samples
        wpm_timeline = self._get_wpm_timeline(state.keystrokes)
        
        # Calculate interval stats
        intervals = self._calculate_intervals(state.keystrokes)
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        interval_std = self._std_dev(intervals) if intervals else 0
        
        # Combo analysis
        avg_combo = sum(self._combo_lengths) / len(self._combo_lengths) if self._combo_lengths else 0
        
        return SessionAnalysis(
            final_wpm=state.wpm,
            accuracy=state.accuracy,
            total_chars=state.correct + state.errors,
            total_errors=state.errors,
            total_time_seconds=state.elapsed_time,
            consistency_score=consistency,
            wpm_variance=self._calculate_wpm_variance(),
            error_patterns=error_patterns,
            slowest_digraphs=slowest,
            fastest_digraphs=fastest,
            avg_interval_ms=avg_interval,
            interval_std_ms=interval_std,
            max_combo=state.max_combo,
            avg_combo=avg_combo,
            wpm_timeline=wpm_timeline,
        )
    
    def _process_keystrokes(self, keystrokes: list[Keystroke]) -> None:
        """Process keystrokes to extract patterns and timing data."""
        current_combo = 0
        
        for i, ks in enumerate(keystrokes):
            # Track errors
            if not ks.is_correct:
                key = f"{ks.char}->{ks.expected}"
                self._error_counts[key] += 1
                self._error_positions[key].append(ks.position)
                
                # Record combo length
                if current_combo > 0:
                    self._combo_lengths.append(current_combo)
                current_combo = 0
            else:
                current_combo += 1
            
            # Track digraph timing
            if i > 0:
                prev = keystrokes[i - 1]
                if prev.is_correct and ks.is_correct:
                    digraph = prev.expected + ks.expected
                    interval = (ks.timestamp - prev.timestamp) * 1000  # ms
                    self._digraph_times[digraph].append(interval)
            
            # Sample WPM periodically
            if i % 10 == 0:
                elapsed = ks.timestamp - keystrokes[0].timestamp if keystrokes else 0
                self._wpm_samples.append((elapsed, ks.wpm_at_time))
        
        # Don't forget the last combo
        if current_combo > 0:
            self._combo_lengths.append(current_combo)
    
    def _get_error_patterns(self, limit: int = 10) -> list[ErrorPattern]:
        """Get the most common error patterns."""
        patterns = []
        
        for key, count in sorted(
            self._error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]:
            typed, expected = key.split("->")
            patterns.append(ErrorPattern(
                typed=typed,
                expected=expected,
                count=count,
                positions=self._error_positions[key],
            ))
        
        return patterns
    
    def _get_slowest_digraphs(self, limit: int = 5) -> list[DigraphStats]:
        """Get the slowest character pairs."""
        digraphs = []
        
        for chars, times in self._digraph_times.items():
            if len(times) >= 2:  # Need at least 2 samples
                avg = sum(times) / len(times)
                digraphs.append(DigraphStats(
                    chars=chars,
                    avg_time_ms=avg,
                    count=len(times),
                    times=times,
                ))
        
        return sorted(digraphs, key=lambda x: x.avg_time_ms, reverse=True)[:limit]
    
    def _get_fastest_digraphs(self, limit: int = 5) -> list[DigraphStats]:
        """Get the fastest character pairs."""
        digraphs = []
        
        for chars, times in self._digraph_times.items():
            if len(times) >= 2:
                avg = sum(times) / len(times)
                digraphs.append(DigraphStats(
                    chars=chars,
                    avg_time_ms=avg,
                    count=len(times),
                    times=times,
                ))
        
        return sorted(digraphs, key=lambda x: x.avg_time_ms)[:limit]
    
    def _get_wpm_timeline(
        self, 
        keystrokes: list[Keystroke],
        interval: float = 5.0
    ) -> list[tuple[float, float]]:
        """Get WPM samples at regular intervals.
        
        Args:
            keystrokes: List of keystrokes
            interval: Sampling interval in seconds
            
        Returns:
            List of (time, wpm) tuples
        """
        if not keystrokes:
            return []
        
        timeline = []
        start_time = keystrokes[0].timestamp
        
        last_sample_time = 0.0
        for ks in keystrokes:
            elapsed = ks.timestamp - start_time
            if elapsed - last_sample_time >= interval:
                timeline.append((elapsed, ks.wpm_at_time))
                last_sample_time = elapsed
        
        # Always include final WPM
        if keystrokes:
            final_elapsed = keystrokes[-1].timestamp - start_time
            timeline.append((final_elapsed, keystrokes[-1].wpm_at_time))
        
        return timeline
    
    def _calculate_intervals(self, keystrokes: list[Keystroke]) -> list[float]:
        """Calculate all keystroke intervals in ms."""
        intervals = []
        for i in range(1, len(keystrokes)):
            interval = (keystrokes[i].timestamp - keystrokes[i-1].timestamp) * 1000
            intervals.append(interval)
        return intervals
    
    def _calculate_consistency(self) -> float:
        """Calculate a 0-10 consistency score based on WPM variance.
        
        Lower variance = higher consistency score.
        """
        if len(self._wpm_samples) < 3:
            return 5.0  # Default middle score
        
        wpm_values = [wpm for _, wpm in self._wpm_samples if wpm > 0]
        if not wpm_values:
            return 5.0
        
        variance = self._calculate_wpm_variance()
        
        # Convert variance to a 0-10 score
        # Low variance (< 50) = high score, high variance (> 400) = low score
        if variance < 25:
            return 10.0
        elif variance > 500:
            return 1.0
        else:
            # Linear interpolation between 1 and 10
            score = 10 - ((variance - 25) / 475) * 9
            return max(1.0, min(10.0, score))
    
    def _calculate_wpm_variance(self) -> float:
        """Calculate variance in WPM over the session."""
        wpm_values = [wpm for _, wpm in self._wpm_samples if wpm > 0]
        if len(wpm_values) < 2:
            return 0.0
        
        mean = sum(wpm_values) / len(wpm_values)
        variance = sum((x - mean) ** 2 for x in wpm_values) / len(wpm_values)
        return variance
    
    def _std_dev(self, values: list[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_recommendations(self, analysis: SessionAnalysis) -> list[str]:
        """Generate recommendations based on analysis.
        
        Args:
            analysis: Session analysis to base recommendations on
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Accuracy recommendations
        if analysis.accuracy < 90:
            recommendations.append(
                "Focus on accuracy over speed. Try slowing down by 10-15 WPM."
            )
        elif analysis.accuracy < 95:
            recommendations.append(
                "Good accuracy! A slight slowdown could push you above 95%."
            )
        
        # Consistency recommendations
        if analysis.consistency_score < 5:
            recommendations.append(
                "Your typing rhythm varies significantly. Try maintaining a steady pace."
            )
        elif analysis.consistency_score > 8:
            recommendations.append(
                "Excellent consistency! Your rhythm is in the top tier."
            )
        
        # Error pattern recommendations
        if analysis.error_patterns:
            top_error = analysis.error_patterns[0]
            if top_error.count >= 3:
                recommendations.append(
                    f"Practice the '{top_error.expected}' key - "
                    f"you typed '{top_error.typed}' instead {top_error.count} times."
                )
        
        # Digraph recommendations
        if analysis.slowest_digraphs:
            slowest = analysis.slowest_digraphs[0]
            recommendations.append(
                f"The '{slowest.chars}' combination is slowing you down. "
                "Consider focused practice."
            )
        
        return recommendations
