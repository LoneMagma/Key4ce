"""
key4ce/ui/screens/typing.py
────────────────────────────
Live typing session — centered layout, newline auto-skip.
"""

from __future__ import annotations

import textwrap
import time
from dataclasses import dataclass, field
from typing import Callable

import readchar
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

MAX_WIDTH  = 100
LINE_WIDTH = 72

BUILTIN_THEMES = {
    "cyberpunk": {"primary": "cyan",    "accent": "bright_cyan",  "ok": "green", "err": "red", "dim": "dim cyan",    "border": "cyan"},
    "nord":      {"primary": "blue",    "accent": "bright_blue",  "ok": "green", "err": "red", "dim": "dim blue",    "border": "blue"},
    "dracula":   {"primary": "magenta", "accent": "bright_magenta","ok": "green", "err": "red", "dim": "dim magenta", "border": "magenta"},
    "monokai":   {"primary": "yellow",  "accent": "bright_yellow", "ok": "green", "err": "red", "dim": "dim yellow",  "border": "yellow"},
    "minimal":   {"primary": "white",   "accent": "bold white",   "ok": "white", "err": "bright_red", "dim": "dim white", "border": "white"},
}

def get_palette(theme: str) -> dict:
    return BUILTIN_THEMES.get((theme or "cyberpunk").lower(), BUILTIN_THEMES["cyberpunk"])


# ── State ─────────────────────────────────────────────────────────

@dataclass
class TypingState:
    text:   str
    typed:  list[str]  = field(default_factory=list)
    errors: list[bool] = field(default_factory=list)
    start_time: float | None = None
    end_time:   float | None = None
    wpm_snapshots: list[float] = field(default_factory=list)

    @property
    def pos(self) -> int:
        return len(self.typed)

    @property
    def done(self) -> bool:
        return self.pos >= len(self.text)

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        return (self.end_time or time.time()) - self.start_time

    def wpm(self) -> float:
        secs = self.elapsed()
        if secs < 1:
            return 0.0
        printable = sum(1 for ch in self.text[:self.pos] if ch != "\n")
        return round((printable / 5.0) / (secs / 60), 1)

    def accuracy(self) -> float:
        rel = [self.errors[i] for i, ch in enumerate(self.text[:self.pos]) if ch != "\n"]
        if not rel:
            return 100.0
        return round(sum(1 for e in rel if not e) / len(rel) * 100, 1)

    def error_count(self) -> int:
        return sum(1 for i, e in enumerate(self.errors)
                   if e and i < len(self.text) and self.text[i] != "\n")

    def progress_pct(self) -> int:
        return int(self.pos / len(self.text) * 100) if self.text else 0


# ── Text prep ─────────────────────────────────────────────────────

def _prepare_text(raw: str, width: int = LINE_WIDTH) -> str:
    return textwrap.fill(" ".join(raw.split()), width=width)


# ── Render helpers ────────────────────────────────────────────────

def _render_text(state: TypingState, p: dict) -> Text:
    result = Text(no_wrap=False)
    for i, ch in enumerate(state.text):
        if i < state.pos:
            if ch == "\n":
                result.append("\n")
            elif state.errors[i]:
                display = state.typed[i] if state.typed[i] != " " else "_"
                result.append(display, style=f"bold {p['err']}")
            else:
                result.append(ch, style=p["ok"])
        elif i == state.pos:
            result.append("↵" if ch == "\n" else ch,
                          style=f"underline bold {p['accent']}")
        else:
            result.append("\n" if ch == "\n" else ch, style=p["dim"])
    return result


def _stats_bar(state: TypingState, p: dict) -> Text:
    e   = state.elapsed()
    bar = Text()
    bar.append("Time: ",    style=p["dim"])
    bar.append(f"{int(e//60):02d}:{int(e%60):02d}", style="white")
    bar.append("    WPM: ", style=p["dim"])
    bar.append(str(state.wpm()), style=f"bold {p['accent']}")
    bar.append("    Accuracy: ", style=p["dim"])
    bar.append(f"{state.accuracy()}%", style="white")
    bar.append("    Errors: ", style=p["dim"])
    ec = state.error_count()
    bar.append(str(ec), style=f"bold {p['err']}" if ec else "white")
    return bar


def _progress_bar(pct: int, p: dict, width: int = 58) -> Text:
    filled = int(width * pct / 100)
    t = Text()
    t.append("Progress: [",              style=p["dim"])
    t.append("\u2588" * filled,          style=p["accent"])
    t.append("\u2591" * (width - filled), style=p["dim"])
    t.append(f"]  {pct}%",              style=p["dim"])
    return t


def _build_frame(state: TypingState, p: dict, theme: str,
                 zen: bool, console_width: int) -> Table:
    root = Table.grid(expand=True)
    root.add_column()

    # Header
    right = f"THEME: {theme.upper()}"
    title = "KEY4CE :: ACTIVE SESSION"
    gap   = max(2, MAX_WIDTH - len(title) - len(right))
    hdr   = Text()
    hdr.append(title, style=f"bold {p['primary']}")
    hdr.append(" " * gap)
    hdr.append(right, style=p["dim"])
    root.add_row(Align.center(hdr, width=MAX_WIDTH))
    root.add_row(Align.center(Rule(style=p["border"]), width=MAX_WIDTH))
    root.add_row(Text(""))

    if not zen:
        root.add_row(Align.center(_stats_bar(state, p), width=MAX_WIDTH))
        root.add_row(Text(""))

    root.add_row(Align.center(
        Panel(_render_text(state, p),
              title="TEXT SAMPLE", title_align="left",
              border_style=p["border"], box=box.ROUNDED,
              width=MAX_WIDTH, padding=(1, 2)),
        width=MAX_WIDTH,
    ))
    root.add_row(Text(""))
    root.add_row(Align.center(_progress_bar(state.progress_pct(), p), width=MAX_WIDTH))
    root.add_row(Text(""))

    footer = Text()
    footer.append("[Tab]", style=f"bold {p['accent']}")
    footer.append(" Restart    ", style=p["dim"])
    footer.append("[Esc]", style=f"bold {p['accent']}")
    footer.append(" Exit Session", style=p["dim"])
    root.add_row(Align.center(footer, width=MAX_WIDTH))

    return root


# ═════════════════════════════════════════════════════════════════
#  Runner
# ═════════════════════════════════════════════════════════════════

def run_typing_session(
    text: str,
    profile: dict,
    console: Console | None = None,
    on_complete: Callable | None = None,
) -> "TypingState | None":
    if console is None:
        console = Console()

    theme    = profile.get("theme", "cyberpunk")
    zen      = profile.get("zen", False)
    p        = get_palette(theme)
    prepared = _prepare_text(text, width=LINE_WIDTH)
    state    = TypingState(text=prepared)
    action   = None

    def _auto_skip() -> None:
        """Silently consume any \n chars so user never types Enter."""
        while state.pos < len(state.text) and state.text[state.pos] == "\n":
            state.typed.append("\n")
            state.errors.append(False)

    _auto_skip()  # skip any leading newlines

    with Live(
        _build_frame(state, p, theme, zen, console.width),
        console=console,
        refresh_per_second=20,
        screen=True,
    ) as live:

        def _refresh() -> None:
            live.update(_build_frame(state, p, theme, zen, console.width))

        while not state.done:
            ch = readchar.readkey()

            if ch == readchar.key.TAB:
                action = "restart"; break
            elif ch == readchar.key.ESC:
                action = "quit"; break
            elif ch == readchar.key.BACKSPACE:
                if state.typed:
                    state.typed.pop()
                    state.errors.pop()
                # un-skip trailing auto-consumed newlines
                while state.typed and state.text[len(state.typed) - 1] == "\n":
                    state.typed.pop()
                    state.errors.pop()
            elif len(ch) == 1 and ch.isprintable():
                if state.start_time is None:
                    state.start_time = time.time()
                # IMPORTANT: read target BEFORE appending so index is correct
                target = state.text[state.pos]
                state.typed.append(ch)
                state.errors.append(ch != target)
                _auto_skip()
                if state.pos % 25 == 0 and state.pos > 0:
                    state.wpm_snapshots.append(state.wpm())

            _refresh()

    if state.done:
        state.end_time = time.time()

    if action == "restart":
        return run_typing_session(text, profile, console, on_complete)
    if action == "quit":
        return None
    if on_complete:
        on_complete(state)
    return state
