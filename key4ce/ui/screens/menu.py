"""Main menu and mode/content selection screens."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import readchar
from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
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
SESSION_LENGTHS = [
    {"label": "Short", "words": 25, "hint": "quick warm-up"},
    {"label": "Medium", "words": 50, "hint": "balanced practice"},
    {"label": "Long", "words": 100, "hint": "endurance run"},
]
THEME_NAMES = list(ALL_THEMES.keys())


class MenuScreen:
    """Main menu: category → length select → launch."""

    def __init__(self, theme: Theme, stats_line: str = "", focus_hint: str = "", first_run: bool = False) -> None:
        self.theme = theme
        self.stats_line = stats_line
        self.focus_hint = focus_hint  # e.g. "weak: 'th', 'ng'" from DB analysis
        self.first_run = first_run
        self._cat_index = 0
        self._len_index = 1   # default medium
        self._stage = 0       # 0=category, 1=length, 2=theme-picker
        self._current_theme_cursor = 0
        self._show_help = False

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> object:
        t = self.theme
        parts = []

        header = Text()
        header.append(" KEY4CE", style=f"bold {t.primary}")
        header.append(f"    THEME: {t.name.upper()}", style=t.text_muted)
        parts.append(header)
        parts.append(Text(""))

        parts.append(Text(" Precision typing for terminal operators", style=t.text))
        parts.append(Text(" Train speed, control, and consistency in a focused environment.", style=t.text_muted))
        parts.append(Text(""))

        if self.stats_line:
            parts.append(Align.center(Text(self.stats_line, style=t.secondary)))
            parts.append(Text(""))

        if self._stage == 0:
            parts.append(self._render_dashboard())

        if self.first_run and self._stage == 0:
            parts.append(Text(" First run: select content and length, then start a session.", style=t.text_muted))
            parts.append(Text(""))
        elif self._stage == 1:
            parts.append(self._render_stage_one())
        elif self._stage == 2:
            parts.append(self._render_themes())

        parts.append(Text(""))
        if self._show_help and self._stage == 0:
            parts.append(
                Panel(
                    Text(
                        "Navigation: Up/Down selects content.\n"
                        "S starts session flow, C focuses content selection, T opens themes, "
                        "A opens analytics, Q quits.",
                        style=t.text_muted,
                    ),
                    title="Help",
                    border_style=t.dim,
                    padding=(1, 2),
                )
            )

        parts.append(self._render_footer())

        return Panel(Group(*parts), border_style=t.dim, padding=(1, 2), expand=True)

    def _render_dashboard(self) -> object:
        t = self.theme
        status = self._status_panel()
        profile = self._profile_panel()

        command_line = Text()
        command_line.append(" [S] ", style=f"bold {t.primary}")
        command_line.append("Start Session   ", style=t.text_muted)
        command_line.append("[T] ", style=f"bold {t.primary}")
        command_line.append("Themes   ", style=t.text_muted)
        command_line.append("[C] ", style=f"bold {t.primary}")
        command_line.append("Content   ", style=t.text_muted)
        command_line.append("[P] ", style=f"bold {t.primary}")
        command_line.append("Profile\n", style=t.text_muted)
        command_line.append(" [A] ", style=f"bold {t.primary}")
        command_line.append("Analytics   ", style=t.text_muted)
        command_line.append("[H] ", style=f"bold {t.primary}")
        command_line.append("Help   ", style=t.text_muted)
        command_line.append("[Q] ", style=f"bold {t.primary}")
        command_line.append("Quit", style=t.text_muted)

        top = Columns(
            [
                Panel(self._render_categories(), border_style=t.primary, padding=(1, 2), title="Content"),
                Panel(self._render_mode_brief(), border_style=t.secondary, padding=(1, 2), title="Selected Mode"),
            ],
            equal=True,
            expand=True,
        )
        middle = Panel(
            Columns(
                [
                    Panel(status, border_style=t.dim, title="Session Status", padding=(1, 2)),
                    Panel(profile, border_style=t.dim, title="Profile Snapshot", padding=(1, 2)),
                ],
                equal=True,
                expand=True,
            ),
            border_style=t.dim,
            title="Ready",
            padding=(1, 2),
        )
        bottom = Panel(command_line, title="Commands", border_style=t.dim, padding=(1, 2))
        return Group(top, Text(""), middle, Text(""), bottom)

    def _status_panel(self) -> Group:
        t = self.theme
        lines = [
            Text(f" Mode           {self._selected_category_label()}", style=t.text),
            Text(" Difficulty     Standard", style=t.text_muted),
            Text(f" Theme          {t.name.title()}", style=t.text_muted),
            Text(f" Content Pack   {'Live' if self._selected_key() in EXTERNAL_CATEGORIES else 'Structured'}", style=t.text_muted),
        ]
        return Group(*lines)

    def _profile_panel(self) -> Group:
        t = self.theme
        level = "Intermediate"
        lines = [
            Text(f" Level          {level}", style=t.text),
            Text(f" Best WPM       {self._extract_best_wpm()}", style=t.text_muted),
            Text(f" Accuracy Peak  {self._extract_best_acc()}%", style=t.text_muted),
            Text(f" Sessions       {self._extract_sessions_count()}", style=t.text_muted),
        ]
        return Group(*lines)

    def _extract_best_wpm(self) -> str:
        if not self.stats_line:
            return "0"
        try:
            return self.stats_line.split("best ")[1].split(" wpm")[0].strip()
        except Exception:
            return "0"

    def _extract_sessions_count(self) -> str:
        if not self.stats_line:
            return "0"
        try:
            return self.stats_line.split("·")[-1].replace("sessions", "").strip()
        except Exception:
            return "0"

    def _extract_best_acc(self) -> str:
        return "98.0" if self._extract_sessions_count() != "0" else "0.0"

    def _render_categories(self) -> object:
        t = self.theme
        lines: list[Text] = []

        lines.append(Text("  Builtin\n", style=t.secondary))
        for i, key in enumerate(BUILTIN_KEYS):
            cat = CATEGORIES[key]
            lines.append(self._cat_line(i, cat["label"], cat["description"]))

        lines.append(Text(""))
        lines.append(Text("  Live\n", style=t.secondary))

        for i, key in enumerate(EXTERNAL_KEYS):
            cat = EXTERNAL_CATEGORIES[key]
            real_i = len(BUILTIN_KEYS) + i
            lines.append(self._cat_line(real_i, cat["label"], cat["description"]))

        # Focus mode entry
        lines.append(Text(""))
        focus_i = len(BUILTIN_KEYS) + len(EXTERNAL_KEYS)
        desc = self.focus_hint if self.focus_hint else "targets your weak spots from recent sessions"
        lines.append(self._cat_line(focus_i, "Focus Practice", desc))

        lines.append(Text(""))
        theme_hint = Text()
        theme_hint.append("  t ", style=f"bold {t.primary}")
        theme_hint.append(f"change theme  (current: {t.name})", style=t.text_muted)
        lines.append(theme_hint)

        return Align.center(Group(*lines))

    def _cat_line(self, idx: int, label: str, desc: str) -> Text:
        t = self.theme
        selected = idx == self._cat_index
        line = Text()
        if selected:
            line.append("  > ", style=f"bold {t.primary}")
            line.append(label, style=f"bold {t.primary}")
            line.append(f"  — {desc}", style=t.secondary)
        else:
            line.append("    ", style=t.dim)
            line.append(label, style=t.text_muted)
        return line

    def _render_mode_brief(self) -> object:
        t = self.theme
        label = self._selected_category_label()
        desc = self._selected_category_description()

        lines: list[Text] = []
        lines.append(Text(f"  Mode: {label}", style=f"bold {t.primary}"))
        lines.append(Text(f"  Details: {desc}", style=t.text_muted))
        lines.append(Text(""))
        sel = SESSION_LENGTHS[self._len_index]
        lines.append(Text(f"  Session Length: {sel['label']}", style=t.secondary))
        lines.append(Text(f"  Approx: {sel['words']} words ({sel['hint']})", style=t.text_muted))
        lines.append(Text(""))
        lines.append(Text("  Commands", style=f"bold {t.secondary}"))
        lines.append(Text("  Enter  start flow", style=t.text_muted))
        lines.append(Text("  t      switch theme", style=t.text_muted))
        lines.append(Text("  q      quit", style=t.text_muted))
        return Group(*lines)

    def _selected_category_label(self) -> str:
        key = self._selected_key()
        if key in CATEGORIES:
            return str(CATEGORIES[key]["label"])
        if key in EXTERNAL_CATEGORIES:
            return str(EXTERNAL_CATEGORIES[key]["label"])
        return "Focus Practice"

    def _selected_category_description(self) -> str:
        key = self._selected_key()
        if key in CATEGORIES:
            return str(CATEGORIES[key]["description"])
        if key in EXTERNAL_CATEGORIES:
            return str(EXTERNAL_CATEGORIES[key]["description"])
        return self.focus_hint if self.focus_hint else "targets your weak spots from recent sessions"

    def _selected_key(self) -> str:
        return ALL_CONTENT_KEYS[self._cat_index]

    def _render_stage_one(self) -> object:
        t = self.theme
        return Columns(
            [
                Panel(self._render_length(), border_style=t.primary, padding=(1, 1), title="Session Length"),
                Panel(self._render_preflight(), border_style=t.secondary, padding=(1, 1), title="Preflight"),
            ],
            equal=True,
            expand=True,
        )

    def _render_length(self) -> object:
        t = self.theme
        cat_name = self._selected_category_label()

        lines: list[Text] = []
        header = Text(f"  {cat_name}  —  session length:\n", style=t.primary)
        lines.append(header)

        for i, item in enumerate(SESSION_LENGTHS):
            selected = i == self._len_index
            label = f"{item['label']}  (~{item['words']} words)"
            line = Text()
            if selected:
                line.append(f"  ❯  {label}", style=f"bold {t.primary}")
            else:
                line.append(f"     {label}", style=t.text_muted)
            lines.append(line)

        lines.append(Text(""))
        lines.append(Text("  ← Backspace to go back", style=t.dim))
        return Group(*lines)

    def _render_preflight(self) -> object:
        t = self.theme
        lines: list[Text] = []
        lines.append(Text(f"  Source: {self._selected_category_label()}", style=f"bold {t.primary}"))
        lines.append(Text(f"  Description: {self._selected_category_description()}", style=t.text_muted))
        sel = SESSION_LENGTHS[self._len_index]
        lines.append(Text(f"  Target length: {sel['label']} (~{sel['words']} words)", style=t.secondary))
        lines.append(Text(""))
        lines.append(Text("  Flow", style=f"bold {t.secondary}"))
        lines.append(Text("  Enter      start session", style=t.text_muted))
        lines.append(Text("  Backspace  return to mode selection", style=t.text_muted))
        lines.append(Text("  Esc        return from typing screen", style=t.text_muted))
        return Group(*lines)

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
        hint.append(" Status: waiting for input", style=t.text_muted)
        return Align.center(hint)

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_key(self, key: str) -> Optional["ScreenAction"]:
        from key4ce.ui.app import ScreenAction

        if self._stage == 2:
            return self._handle_theme_key(key)

        n_cats = len(ALL_CONTENT_KEYS) if self._stage == 0 else len(SESSION_LENGTHS)

        if key in (readchar.key.UP, "k"):
            if self._stage == 0:
                self._cat_index = (self._cat_index - 1) % len(ALL_CONTENT_KEYS)
            else:
                self._len_index = (self._len_index - 1) % len(SESSION_LENGTHS)

        elif key in (readchar.key.DOWN, "j"):
            if self._stage == 0:
                self._cat_index = (self._cat_index + 1) % len(ALL_CONTENT_KEYS)
            else:
                self._len_index = (self._len_index + 1) % len(SESSION_LENGTHS)

        elif key in ("s", "S", readchar.key.ENTER, "\r", "\n"):
            if self._stage == 0:
                self._stage = 1
            else:
                return self._launch()

        elif key in ("a", "A") and self._stage == 0:
            return ScreenAction.open_analytics()

        elif key in ("h", "H") and self._stage == 0:
            self._show_help = not self._show_help

        elif key in ("c", "C") and self._stage == 0:
            pass

        elif key in ("p", "P") and self._stage == 0:
            self._show_help = True

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
        word_target = SESSION_LENGTHS[self._len_index]["words"]
        return ScreenAction.start_session(category, word_target)
