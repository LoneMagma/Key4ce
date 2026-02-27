"""Post-session results screen — Phase 2 (heatmap, focus suggestion, 'f' key)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import readchar
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from key4ce.core.analyzer import SessionAnalysis
from key4ce.themes.themes import Theme
from key4ce.ui.components.graph import render_wpm_graph
from key4ce.ui.components.progress import render_progress_bar
from key4ce.ui.components.heatmap import render_heatmap, counts_from_timeline

if TYPE_CHECKING:
    from key4ce.ui.app import ScreenAction


class ResultsScreen:
    """Comprehensive post-session report with heatmap and focus suggestion."""

    def __init__(
        self,
        analysis: SessionAnalysis,
        source: str,
        pb_wpm: float,
        theme: Theme,
        keystrokes: list | None = None,
    ) -> None:
        self.analysis = analysis
        self.source = source
        self.pb_wpm = pb_wpm
        self.theme = theme
        self._keystrokes = keystrokes or []

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> object:
        t = self.theme
        a = self.analysis
        parts = []

        # Header
        parts.append(Align.center(Text("  SESSION COMPLETE", style=f"bold {t.primary}")))
        parts.append(Text(""))

        # Performance
        parts.append(self._section("PERFORMANCE", t))
        pb_delta = a.wpm - self.pb_wpm
        pb_str = f"  +{pb_delta:.1f} new PB! 🎉" if pb_delta > 0 else f"  (PB: {self.pb_wpm:.1f})"

        wpm_line = Text()
        wpm_line.append(f"  WPM    {a.wpm:6.1f}  ", style=f"bold {t.primary}")
        wpm_line.append(render_progress_bar(min(a.wpm / 150, 1.0), 20, t.primary, t.dim))
        wpm_line.append(pb_str, style=t.secondary if pb_delta > 0 else t.text_muted)
        parts.append(wpm_line)

        acc_col = t.primary if a.accuracy >= 95 else (t.secondary if a.accuracy >= 85 else t.error)
        acc_line = Text()
        acc_line.append(f"  Accuracy  {a.accuracy:5.1f}%  ", style=f"bold {acc_col}")
        acc_line.append(render_progress_bar(a.accuracy / 100, 20, acc_col, t.dim))
        parts.append(acc_line)

        mins, secs = divmod(int(a.duration_sec), 60)
        meta = Text()
        meta.append(f"  {mins}:{secs:02d}   ·   {a.chars_typed} chars   ·   {a.total_errors} errors", style=t.text_muted)
        parts.append(meta)
        parts.append(Text(""))

        # WPM graph
        if a.wpm_buckets:
            parts.append(self._section("WPM OVER TIME", t))
            for line in render_wpm_graph(a.wpm_buckets, 40, 5, t.graph_line, t.dim):
                parts.append(Text("  ") + line)
            parts.append(Text(""))

        # Keyboard heatmap
        if self._keystrokes:
            parts.append(self._section("KEYBOARD HEATMAP", t))
            key_counts = counts_from_timeline(self._keystrokes)
            for line in render_heatmap(key_counts, t, show_keys=True):
                parts.append(line)
            parts.append(Text(""))

        # Top errors
        if a.top_errors:
            parts.append(self._section("TOP MISTAKES", t))
            for ep in a.top_errors:
                line = Text()
                line.append(f"  '{ep.expected}'", style=f"bold {t.error}")
                line.append(" ← typed ", style=t.text_muted)
                line.append(f"'{ep.got}'", style=t.secondary)
                line.append(f"  ×{ep.count}", style=t.text_muted)
                parts.append(line)
            parts.append(Text(""))

        # Slow digraphs
        if a.slow_digraphs:
            parts.append(self._section("SLOW TRANSITIONS", t))
            for dg in a.slow_digraphs:
                line = Text()
                line.append(f"  '{dg.digraph}'", style=f"bold {t.secondary}")
                line.append(f"  {dg.avg_ms:5.0f}ms avg  ", style=t.text_muted)
                sign = "+" if dg.deviation >= 0 else ""
                line.append(f"  {sign}{dg.deviation:.0f}ms vs avg", style=t.error if dg.deviation > 0 else t.primary)
                parts.append(line)
            parts.append(Text(""))

        # Problem keys
        if a.problem_keys:
            parts.append(self._section("PROBLEM KEYS", t))
            line = Text("  ")
            for k in a.problem_keys:
                line.append(f" {k} ", style=f"bold black on {t.error}")
                line.append(" ", style="")
            parts.append(line)
            parts.append(Text(""))

        # Focus mode suggestion
        if a.slow_digraphs or a.problem_keys:
            suggestion = Text()
            dgs = [d.digraph for d in a.slow_digraphs[:2]]
            keys = a.problem_keys[:3]
            suggestion.append("  🎯 Focus suggestion: ", style=f"bold {t.primary}")
            if dgs:
                suggestion.append(f"digraphs {', '.join(repr(d) for d in dgs)}", style=t.secondary)
            if keys:
                if dgs:
                    suggestion.append("  ·  ", style=t.text_muted)
                suggestion.append(f"keys {', '.join(repr(k) for k in keys)}", style=t.secondary)
            parts.append(suggestion)
            parts.append(Text("  Press f to launch focus practice now", style=t.text_muted))
            parts.append(Text(""))

        # Action bar
        parts.append(Rule(style=t.dim))
        actions = Text()
        actions.append("  r ", style=f"bold {t.primary}")
        actions.append("retry    ", style=t.text_muted)
        actions.append("f ", style=f"bold {t.primary}")
        actions.append("focus    ", style=t.text_muted)
        actions.append("m ", style=f"bold {t.primary}")
        actions.append("menu    ", style=t.text_muted)
        actions.append("q ", style=f"bold {t.primary}")
        actions.append("quit", style=t.text_muted)
        parts.append(Align.center(actions))

        return Panel(Group(*parts), border_style=t.primary, padding=(1, 2))

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: str) -> Optional["ScreenAction"]:
        from key4ce.ui.app import ScreenAction

        if key in ("r", "R"):
            return ScreenAction.retry()
        if key in ("f", "F"):
            return ScreenAction.focus_from_results(self.analysis)
        if key in ("m", "M", readchar.key.ESC):
            return ScreenAction.go_menu()
        if key in ("q", "Q"):
            return ScreenAction.quit()
        return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _section(label: str, t: Theme) -> Text:
        line = Text()
        line.append(f"  ▸ {label}", style=f"bold {t.secondary}")
        return line
