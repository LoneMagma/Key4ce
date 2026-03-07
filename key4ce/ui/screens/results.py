"""
key4ce/ui/screens/results.py
──────────────────────────────
Post-session report — centered layout, \n filtered from all stat helpers.
"""

from __future__ import annotations

import time
from collections import Counter
from typing import Any

import readchar
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

MAX_WIDTH = 100

BUILTIN_THEMES = {
    "cyberpunk": {"primary": "cyan",    "accent": "bright_cyan",  "ok": "green", "err": "red", "dim": "dim cyan",    "border": "cyan"},
    "nord":      {"primary": "blue",    "accent": "bright_blue",  "ok": "green", "err": "red", "dim": "dim blue",    "border": "blue"},
    "dracula":   {"primary": "magenta", "accent": "bright_magenta","ok": "green", "err": "red", "dim": "dim magenta", "border": "magenta"},
    "monokai":   {"primary": "yellow",  "accent": "bright_yellow", "ok": "green", "err": "red", "dim": "dim yellow",  "border": "yellow"},
    "minimal":   {"primary": "white",   "accent": "bold white",   "ok": "white", "err": "bright_red", "dim": "dim white", "border": "white"},
}

def get_palette(theme: str) -> dict:
    return BUILTIN_THEMES.get((theme or "cyberpunk").lower(), BUILTIN_THEMES["cyberpunk"])


# ── Centered print helper ─────────────────────────────────────────

def _cp(console: Console, renderable, width: int = MAX_WIDTH) -> None:
    console.print(Align.center(renderable, width=width))


# ── Filtered stat helpers (skip \n positions) ─────────────────────

def _real_wpm(state: Any) -> float:
    secs = state.elapsed()
    if secs < 1:
        return 0.0
    printable = sum(1 for ch in state.text[:state.pos] if ch != "\n")
    return round((printable / 5.0) / (secs / 60), 1)

def _real_accuracy(state: Any) -> float:
    rel = [state.errors[i]
           for i in range(len(state.typed))
           if i < len(state.text) and state.text[i] != "\n"]
    if not rel:
        return 100.0
    return round(sum(1 for e in rel if not e) / len(rel) * 100, 1)

def _real_errors(state: Any) -> int:
    return sum(1 for i, e in enumerate(state.errors)
               if e and i < len(state.text) and state.text[i] != "\n")

def _error_pairs(state: Any) -> list[tuple[str, str, int]]:
    pairs: Counter = Counter()
    for i, is_err in enumerate(state.errors):
        if not is_err or i >= len(state.text):
            continue
        exp = state.text[i]
        act = state.typed[i]
        if exp == "\n" or not exp.isprintable():
            continue
        if not act.isprintable():
            continue
        pairs[(exp, act)] += 1
    return [(e, a, c) for (e, a), c in pairs.most_common(5)]


# ── Coaching note ─────────────────────────────────────────────────

def _coaching_note(wpm: float, acc: float, errors: int, prev_best: float) -> str:
    if acc < 93:
        return ("Accuracy dropped significantly this session. "
                "Slow down on difficult character sequences until muscle memory stabilises.")
    if acc < 96 and wpm > 60:
        return ("Speed is strong but accuracy is suffering at pace. "
                "Focus on clean keystrokes before pushing WPM further.")
    if errors == 0:
        return ("A clean run with zero errors. "
                "Accuracy is solid — now is the right moment to push for higher speed.")
    if wpm < 35:
        return ("Keep building fluency. Consistency at moderate speed compounds quickly.")
    if prev_best > 0 and wpm >= prev_best * 0.97:
        return ("Personal-best territory. Sustain this pacing pattern across longer sessions.")
    return ("Solid session. Review the key pairs that tripped you up "
            "and consider a short focus drill before your next run.")


# ── WPM sparkline ─────────────────────────────────────────────────

def _sparkline(snapshots: list[float], p: dict) -> Text:
    if not snapshots or len(snapshots) < 2:
        return Text("Insufficient data for pace graph.", style=p["dim"])
    lo, hi = min(snapshots), max(snapshots)
    span   = hi - lo or 1
    blocks = " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    t = Text()
    for val in snapshots:
        idx = int((val - lo) / span * (len(blocks) - 1))
        t.append(blocks[idx], style=p["accent"])
    t.append(f"   {lo:.0f} \u2014 {hi:.0f} WPM", style=p["dim"])
    return t


# ── Keyboard heatmap ──────────────────────────────────────────────

_KB_ROWS = [list("qwertyuiop"), list("asdfghjkl"), list("zxcvbnm")]

def _keyboard_heatmap(state: Any, p: dict) -> Text:
    err_chars: Counter = Counter()
    for i, is_err in enumerate(state.errors):
        if is_err and i < len(state.text):
            ch = state.text[i]
            if ch != "\n" and ch.isprintable():
                err_chars[ch.lower()] += 1
    t = Text()
    for row in _KB_ROWS:
        t.append("  ")
        for ch in row:
            count = err_chars.get(ch, 0)
            style = (f"bold {p['err']}" if count >= 3
                     else p["err"] if count >= 1
                     else p["dim"])
            t.append(f"{ch} ", style=style)
        t.append("\n")
    return t


# ── DB helpers ────────────────────────────────────────────────────

def _get_prev_best() -> float:
    try:
        from key4ce.data.db import Database
        rows = Database().get_sessions(limit=9999)
        wpms = [r["wpm"] for r in rows if r.get("wpm")]
        return max(wpms) if wpms else 0.0
    except Exception:
        return 0.0

def _save_session(state: Any, profile: dict,
                  wpm: float, acc: float, errors: int) -> None:
    try:
        from key4ce.data.db import Database
        Database().save_session({
            "wpm":       wpm,
            "accuracy":  acc,
            "errors":    errors,
            "duration":  state.elapsed(),
            "mode":      profile.get("mode", "words"),
            "wpm_curve": state.wpm_snapshots,
        })
    except Exception:
        pass


# ═════════════════════════════════════════════════════════════════
#  Main renderer
# ═════════════════════════════════════════════════════════════════

def run_results(state: Any, profile: dict,
                console: Console | None = None) -> str:
    """Returns: 'retry' | 'focus' | 'menu' | 'quit'"""
    if console is None:
        console = Console()

    theme     = profile.get("theme", "cyberpunk")
    p         = get_palette(theme)
    prev_best = _get_prev_best()

    wpm    = _real_wpm(state)
    acc    = _real_accuracy(state)
    errors = _real_errors(state)
    dur_s  = f"{int(state.elapsed()//60):02d}:{int(state.elapsed()%60):02d}"
    is_pb  = prev_best > 0 and wpm >= prev_best

    _save_session(state, profile, wpm, acc, errors)
    console.clear()

    # ── Header ────────────────────────────────────────────────────
    title = "KEY4CE :: SESSION RESULTS"
    right = f"THEME: {theme.upper()}"
    gap   = max(2, MAX_WIDTH - len(title) - len(right))
    hdr   = Text()
    hdr.append(title, style=f"bold {p['primary']}")
    hdr.append(" " * gap)
    hdr.append(right, style=p["dim"])
    _cp(console, hdr)
    _cp(console, Rule(style=p["border"]))
    console.print()

    # ── PB badge ─────────────────────────────────────────────────
    if is_pb:
        _cp(console, Text(f"NEW PERSONAL BEST  —  {wpm} WPM",
                          style=f"bold {p['accent']}"))
        console.print()

    # ── Performance summary ───────────────────────────────────────
    st = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2))
    st.add_column("k", style=p["dim"], min_width=12)
    st.add_column("v", style=f"bold {p['accent']}")
    st.add_row("WPM",      str(wpm))
    st.add_row("Accuracy", f"{acc}%")
    st.add_row("Errors",   str(errors))
    st.add_row("Duration", dur_s)
    if prev_best > 0:
        delta = wpm - prev_best
        st.add_row("vs Best", f"{'+'if delta>=0 else ''}{delta:.1f} WPM")
    _cp(console, Panel(st, title="PERFORMANCE SUMMARY", title_align="left",
                       border_style=p["border"], box=box.ROUNDED,
                       width=MAX_WIDTH, padding=(0, 1)))
    console.print()

    # ── Pace graph ────────────────────────────────────────────────
    if state.wpm_snapshots:
        _cp(console, Panel(_sparkline(state.wpm_snapshots, p),
                           title="PACE GRAPH", title_align="left",
                           border_style=p["border"], box=box.ROUNDED,
                           width=MAX_WIDTH, padding=(0, 1)))
        console.print()

    # ── Error breakdown ───────────────────────────────────────────
    pairs = _error_pairs(state)
    if pairs:
        et = Table(box=box.SIMPLE_HEAD, show_header=True,
                   header_style=f"bold {p['dim']}", pad_edge=False)
        et.add_column("Expected", style=p["dim"],            min_width=12)
        et.add_column("Typed",    style=f"bold {p['err']}",  min_width=12)
        et.add_column("Count",    style="white", justify="right", min_width=6)
        for exp, act, cnt in pairs:
            et.add_row(repr(exp).strip("'"), repr(act).strip("'"), str(cnt))
        _cp(console, Panel(et, title="ERROR BREAKDOWN", title_align="left",
                           border_style=p["border"], box=box.ROUNDED,
                           width=MAX_WIDTH, padding=(0, 1)))
        console.print()

    # ── Keyboard heatmap ──────────────────────────────────────────
    _cp(console, Panel(_keyboard_heatmap(state, p),
                       title="KEYBOARD HEATMAP", title_align="left",
                       border_style=p["border"], box=box.ROUNDED,
                       width=MAX_WIDTH, padding=(0, 1)))
    console.print()

    # ── Coaching note ─────────────────────────────────────────────
    note = _coaching_note(wpm, acc, errors, prev_best)
    _cp(console, Panel(Text(note, style="white"),
                       title="COACHING NOTE", title_align="left",
                       border_style=p["border"], box=box.ROUNDED,
                       width=MAX_WIDTH, padding=(0, 1)))
    console.print()

    # ── Commands ──────────────────────────────────────────────────
    cmd = Text()
    for k, label in [("R","Retry"),("F","Focus Drill"),("M","Menu"),("Q","Quit")]:
        cmd.append(f"[{k}]", style=f"bold {p['accent']}")
        cmd.append(f" {label}   ", style="white")
    _cp(console, cmd)
    console.print()

    while True:
        ch = readchar.readkey()
        if   ch in ("r", "R"): return "retry"
        elif ch in ("f", "F"): return "focus"
        elif ch in ("m", "M", readchar.key.ESC): return "menu"
        elif ch in ("q", "Q"): return "quit"
