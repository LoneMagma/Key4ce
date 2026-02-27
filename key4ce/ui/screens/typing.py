"""Typing screen — Phase 2 (zen mode, ghost racer, live heatmap toggle)."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Optional

import readchar
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from key4ce.core.engine import TypingEngine, SessionState
from key4ce.themes.themes import Theme
from key4ce.ui.components.progress import render_stats_bar
from key4ce.ui.components.heatmap import render_heatmap, counts_from_timeline

if TYPE_CHECKING:
    from key4ce.ui.app import ScreenAction

_LINE_WIDTH = 65
_VISIBLE_LINES = 3


class TypingScreen:
    """Displays target text and handles keystroke input.

    Phase 2 additions:
    - zen_mode: hides stats bar; stats shown only at end
    - ghost_timings: cumulative ms list from best previous session
    - 'h' key toggles live keyboard heatmap
    """

    def __init__(
        self,
        text: str,
        source: str,
        theme: Theme,
        zen_mode: bool = False,
        ghost_timings: list[int] | None = None,
    ) -> None:
        self.theme = theme
        self.engine = TypingEngine(target_text=text, source=source)
        self._source = source
        self._zen = zen_mode
        self._show_heatmap = False

        # Ghost racer: cumulative ms offsets per correct char
        self._ghost: list[int] = []
        if ghost_timings:
            cumulative = 0
            for ms in ghost_timings:
                cumulative += ms
                self._ghost.append(cumulative)

        # Pre-wrap text
        self._lines = _wrap_text(text, _LINE_WIDTH)
        self._char_to_line: dict[int, int] = {}
        pos = 0
        for li, line in enumerate(self._lines):
            for _ in line:
                self._char_to_line[pos] = li
                pos += 1
            if li < len(self._lines) - 1:
                pos += 1

    # ── Ghost helper ──────────────────────────────────────────────────────────

    def _ghost_position(self) -> int:
        """Return how many chars the ghost has typed at current elapsed time."""
        if not self._ghost:
            return -1
        if self.engine.state == SessionState.IDLE:
            return 0
        elapsed_ms = self.engine.elapsed * 1000
        pos = 0
        for i, t in enumerate(self._ghost):
            if t <= elapsed_ms:
                pos = i + 1
            else:
                break
        return min(pos, len(self._ghost))

    def _ghost_delta(self) -> str:
        gpos = self._ghost_position()
        if gpos < 0:
            return ""
        my_pos = self.engine.position
        diff = gpos - my_pos
        if diff > 0:
            return f"ghost ahead by {diff}"
        if diff < 0:
            return f"you ahead by {abs(diff)}"
        return "tied with ghost"

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> object:
        t = self.theme
        eng = self.engine
        parts = []

        # Header
        header = Text()
        header.append("  key4ce", style=f"bold {t.primary}")
        header.append(f"  ·  {self._source}", style=t.text_muted)
        if self._zen:
            header.append("  ·  zen", style=t.secondary)
        if self._ghost:
            delta = self._ghost_delta()
            header.append(f"  ·  {delta}", style=t.secondary)
        parts.append(header)
        parts.append(Text(""))

        # Typing text
        parts.append(self._render_text_block())
        parts.append(Text(""))

        # Stats bar (hidden in zen mode while typing)
        if not self._zen or eng.is_complete:
            parts.append(
                render_stats_bar(
                    eng.wpm, eng.accuracy, eng.elapsed, eng.progress,
                    t.primary, t.secondary, t.text_muted,
                )
            )
        else:
            parts.append(Text("  — zen mode —", style=t.text_muted))

        # Live heatmap (toggleable with 'h')
        if self._show_heatmap:
            parts.append(Text(""))
            key_counts = counts_from_timeline(eng.timeline.keystrokes)
            for line in render_heatmap(key_counts, t, show_keys=True):
                parts.append(line)

        # Footer
        parts.append(Text(""))
        hint = Text()
        hint.append("  Esc ", style=t.primary)
        hint.append("abandon   ", style=t.text_muted)
        hint.append("h ", style=t.primary)
        hint.append("heatmap", style=t.text_muted)
        if eng.has_error:
            hint.append("   ✗ wrong key", style=f"bold {t.error}")
        parts.append(hint)

        border = t.error if eng.has_error else (t.secondary if self._zen else t.dim)
        return Panel(Group(*parts), border_style=border, padding=(1, 2))

    def _render_text_block(self) -> Text:
        eng = self.engine
        pos = eng.position

        current_line_idx = self._char_to_line.get(pos, 0)
        start_line = max(0, current_line_idx - 1)
        end_line = min(len(self._lines), start_line + _VISIBLE_LINES)
        if end_line - start_line < _VISIBLE_LINES:
            start_line = max(0, end_line - _VISIBLE_LINES)

        text = Text(overflow="fold")
        text.append("  ", style="")

        global_pos = _line_start_pos(self._lines, start_line)
        for li in range(start_line, end_line):
            for ch in self._lines[li]:
                state = eng.char_state(global_pos)
                _append_char(text, ch, state, self.theme)
                global_pos += 1
            if li < len(self._lines) - 1:
                space_state = eng.char_state(global_pos)
                _append_char(text, " ", space_state, self.theme)
                global_pos += 1
            text.append("\n  ", style="")
        return text

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: str) -> Optional["ScreenAction"]:
        from key4ce.ui.app import ScreenAction

        if key == readchar.key.ESC:
            return ScreenAction.pop()

        if key in ("h", "H"):
            self._show_heatmap = not self._show_heatmap
            return None

        if key in (readchar.key.BACKSPACE, "\x08"):
            self.engine.handle_backspace()
            return None

        if len(key) == 1 and key.isprintable():
            self.engine.handle_char(key)
            if self.engine.is_complete:
                return ScreenAction.session_complete(self.engine, self._source)

        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        wl = len(word)
        if current and current_len + 1 + wl > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = wl
        else:
            current.append(word)
            current_len += (1 if current_len else 0) + wl
    if current:
        lines.append(" ".join(current))
    return lines


def _line_start_pos(lines: list[str], line_idx: int) -> int:
    pos = 0
    for i in range(line_idx):
        pos += len(lines[i]) + 1
    return pos


def _append_char(text: Text, ch: str, state: str, theme: Theme) -> None:
    t = theme
    if state == "typed":
        text.append(ch, style=t.dim)
    elif state == "cursor":
        display = "█" if ch == " " else ch
        text.append(display, style=f"bold black on {t.primary}")
    elif state == "cursor_error":
        text.append("█", style=f"bold black on {t.error}")
    else:
        text.append(ch, style=t.text_muted)
