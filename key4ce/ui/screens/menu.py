"""Main menu and mode/content selection screens — Phase 2."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import readchar
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from key4ce.content.builtin import CATEGORIES
from key4ce.content.loader import EXTERNAL_CATEGORIES
from key4ce.themes.themes import Theme, ALL_THEMES

if TYPE_CHECKING:
    from key4ce.ui.app import ScreenAction


LOGO = """\
 ██╗  ██╗███████╗██╗   ██╗██╗  ██╗ ██████╗███████╗
 ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║  ██║██╔════╝██╔════╝
 █████╔╝ █████╗   ╚████╔╝ ███████║██║     █████╗  
 ██╔═██╗ ██╔══╝    ╚██╔╝  ╚════██║██║     ██╔══╝  
 ██║  ██╗███████╗   ██║        ██║╚██████╗███████╗
 ╚═╝  ╚═╝╚══════╝   ╚═╝        ╚═╝ ╚═════╝╚══════╝"""

BUILTIN_KEYS = list(CATEGORIES.keys())
EXTERNAL_KEYS = list(EXTERNAL_CATEGORIES.keys())
ALL_CONTENT_KEYS = BUILTIN_KEYS + EXTERNAL_KEYS + ["focus"]
WORD_TARGETS = [25, 50, 100]
THEME_NAMES = list(ALL_THEMES.keys())


class MenuScreen:
    """Main menu: category → length select → launch."""

    def __init__(self, theme: Theme, stats_line: str = "", focus_hint: str = "") -> None:
        self.theme = theme
        self.stats_line = stats_line
        self.focus_hint = focus_hint  # e.g. "weak: 'th', 'ng'" from DB analysis
        self._cat_index = 0
        self._len_index = 1   # default 50 words
        self._stage = 0       # 0=category, 1=length, 2=theme-picker

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> object:
        t = self.theme
        parts = []

        # Logo
        parts.append(Align.center(Text(LOGO, style=f"bold {t.primary}")))
        parts.append(Text(""))
        parts.append(Align.center(Text("type better. every session.", style=t.text_muted)))
        parts.append(Text(""))

        if self.stats_line:
            parts.append(Align.center(Text(self.stats_line, style=t.secondary)))
            parts.append(Text(""))

        if self._stage == 0:
            parts.append(self._render_categories())
        elif self._stage == 1:
            parts.append(self._render_length())
        elif self._stage == 2:
            parts.append(self._render_themes())

        parts.append(Text(""))
        parts.append(self._render_footer())

        return Panel(Group(*parts), border_style=t.dim, padding=(1, 4))

    def _render_categories(self) -> object:
        t = self.theme
        lines: list[Text] = []

        lines.append(Text("  Builtin\n", style=t.secondary))
        for i, key in enumerate(BUILTIN_KEYS):
            cat = CATEGORIES[key]
            lines.append(self._cat_line(i, cat["emoji"], cat["label"], cat["description"]))

        lines.append(Text(""))
        lines.append(Text("  Live\n", style=t.secondary))

        for i, key in enumerate(EXTERNAL_KEYS):
            cat = EXTERNAL_CATEGORIES[key]
            real_i = len(BUILTIN_KEYS) + i
            lines.append(self._cat_line(real_i, cat["emoji"], cat["label"], cat["description"]))

        # Focus mode entry
        lines.append(Text(""))
        focus_i = len(BUILTIN_KEYS) + len(EXTERNAL_KEYS)
        desc = self.focus_hint if self.focus_hint else "targets your weak spots from recent sessions"
        lines.append(self._cat_line(focus_i, "🎯", "Focus Practice", desc))

        lines.append(Text(""))
        theme_hint = Text()
        theme_hint.append("  t ", style=f"bold {t.primary}")
        theme_hint.append(f"change theme  (current: {t.name})", style=t.text_muted)
        lines.append(theme_hint)

        return Align.center(Group(*lines))

    def _cat_line(self, idx: int, emoji: str, label: str, desc: str) -> Text:
        t = self.theme
        selected = idx == self._cat_index
        line = Text()
        if selected:
            line.append(f"  ❯ {emoji}  ", style=f"bold {t.primary}")
            line.append(label, style=f"bold {t.primary}")
            line.append(f"  — {desc}", style=t.secondary)
        else:
            line.append(f"    {emoji}  ", style=t.dim)
            line.append(label, style=t.text_muted)
        return line

    def _render_length(self) -> object:
        t = self.theme
        key = ALL_CONTENT_KEYS[self._cat_index]
        if key in CATEGORIES:
            cat_name = CATEGORIES[key]["label"]
            cat_emoji = CATEGORIES[key]["emoji"]
        elif key in EXTERNAL_CATEGORIES:
            cat_name = EXTERNAL_CATEGORIES[key]["label"]
            cat_emoji = EXTERNAL_CATEGORIES[key]["emoji"]
        else:
            cat_name = "Focus Practice"
            cat_emoji = "🎯"

        lines: list[Text] = []
        header = Text(f"  {cat_emoji}  {cat_name}  —  session length:\n", style=t.primary)
        lines.append(header)

        for i, n in enumerate(WORD_TARGETS):
            selected = i == self._len_index
            label = f"≈ {n} words"
            line = Text()
            if selected:
                line.append(f"  ❯  {label:>10}", style=f"bold {t.primary}")
            else:
                line.append(f"     {label:>10}", style=t.text_muted)
            lines.append(line)

        lines.append(Text(""))
        lines.append(Text("  ← Backspace to go back", style=t.dim))
        return Align.center(Group(*lines))

    def _render_themes(self) -> object:
        t = self.theme
        lines: list[Text] = []
        lines.append(Text("  Select theme:\n", style=t.secondary))
        for i, name in enumerate(THEME_NAMES):
            selected = name == t.name
            cursor = i == self._cat_index
            line = Text()
            if cursor:
                line.append(f"  ❯  {name}", style=f"bold {t.primary}")
                if selected:
                    line.append("  ✓ active", style=t.secondary)
            else:
                line.append(f"     {name}", style=t.text_muted)
            lines.append(line)
        lines.append(Text(""))
        lines.append(Text("  ← Backspace to go back", style=t.dim))
        return Align.center(Group(*lines))

    def _render_footer(self) -> object:
        t = self.theme
        hint = Text()
        hint.append("  ↑↓ ", style=t.primary)
        hint.append("navigate  ", style=t.text_muted)
        hint.append("Enter ", style=t.primary)
        hint.append("select  ", style=t.text_muted)
        hint.append("q ", style=t.primary)
        hint.append("quit", style=t.text_muted)
        return Align.center(hint)

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: str) -> Optional["ScreenAction"]:
        from key4ce.ui.app import ScreenAction

        if self._stage == 2:
            return self._handle_theme_key(key)

        n_cats = len(ALL_CONTENT_KEYS) if self._stage == 0 else len(WORD_TARGETS)

        if key in (readchar.key.UP, "k"):
            if self._stage == 0:
                self._cat_index = (self._cat_index - 1) % len(ALL_CONTENT_KEYS)
            else:
                self._len_index = (self._len_index - 1) % len(WORD_TARGETS)

        elif key in (readchar.key.DOWN, "j"):
            if self._stage == 0:
                self._cat_index = (self._cat_index + 1) % len(ALL_CONTENT_KEYS)
            else:
                self._len_index = (self._len_index + 1) % len(WORD_TARGETS)

        elif key in (readchar.key.ENTER, "\r", "\n"):
            if self._stage == 0:
                self._stage = 1
            else:
                return self._launch()

        elif key in (readchar.key.BACKSPACE, "\x08"):
            if self._stage == 1:
                self._stage = 0

        elif key in ("t", "T") and self._stage == 0:
            self._current_theme_cursor = THEME_NAMES.index(self.theme.name)
            self._cat_index = self._current_theme_cursor
            self._stage = 2

        elif key in ("q", "Q"):
            return ScreenAction.quit()

        return None

    def _handle_theme_key(self, key: str) -> Optional["ScreenAction"]:
        from key4ce.ui.app import ScreenAction

        if key in (readchar.key.UP, "k"):
            self._cat_index = (self._cat_index - 1) % len(THEME_NAMES)
        elif key in (readchar.key.DOWN, "j"):
            self._cat_index = (self._cat_index + 1) % len(THEME_NAMES)
        elif key in (readchar.key.ENTER, "\r", "\n"):
            chosen = THEME_NAMES[self._cat_index]
            self._stage = 0
            self._cat_index = 0
            return ScreenAction.change_theme(chosen)
        elif key in (readchar.key.BACKSPACE, "\x08", readchar.key.ESC):
            self._stage = 0
            self._cat_index = 0
        elif key in ("q", "Q"):
            return ScreenAction.quit()
        return None

    def _launch(self) -> "ScreenAction":
        from key4ce.ui.app import ScreenAction
        category = ALL_CONTENT_KEYS[self._cat_index]
        word_target = WORD_TARGETS[self._len_index]
        return ScreenAction.start_session(category, word_target)
