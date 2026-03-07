"""
key4ce/ui/screens/menu.py
─────────────────────────
Main menu — fully centered layout.

Layout decisions:
  - All content lives inside a MAX_WIDTH=100 column, centered in the terminal.
  - Intro animation: line-reveal → colour pulse → tagline → "Press any key"
    All rendered with console.clear() + direct print, no Live (avoids double-flash).
  - Panels: fixed width, printed with Align.center().
  - Two-column status panels: built as a single fixed-width Table, centered.
  - Pickers and settings: also centered at MAX_WIDTH.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import readchar
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# ── DB ────────────────────────────────────────────────────────────
try:
    from key4ce.data.db import Database
    _DB_AVAILABLE = True
except ImportError:
    _DB_AVAILABLE = False

DATA_DIR  = Path.home() / ".key4ce"
PROFILE_F = DATA_DIR / "profile.json"
GOALS_F   = DATA_DIR / "goals.json"

CONTENT_MODES = ["words", "sentences", "quotes", "code", "numbers", "wikipedia", "focus"]
LENGTHS       = [25, 50, 75, 100, 150]

_intro_shown = False   # fire animation once per process

# ── Layout constant ───────────────────────────────────────────────
MAX_WIDTH = 100        # content column width; panels are this wide


# ── JSON helpers ──────────────────────────────────────────────────

def _load(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text()) if path.exists() else default
    except Exception:
        return default

def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# ── Palette ───────────────────────────────────────────────────────

BUILTIN_THEMES = {
    "cyberpunk": {"primary": "cyan",        "accent": "bright_cyan",
                  "ok": "green",            "err": "red",
                  "dim": "dim cyan",        "border": "cyan"},
    "nord":      {"primary": "blue",        "accent": "bright_blue",
                  "ok": "green",            "err": "red",
                  "dim": "dim blue",        "border": "blue"},
    "dracula":   {"primary": "magenta",     "accent": "bright_magenta",
                  "ok": "green",            "err": "red",
                  "dim": "dim magenta",     "border": "magenta"},
    "monokai":   {"primary": "yellow",      "accent": "bright_yellow",
                  "ok": "green",            "err": "red",
                  "dim": "dim yellow",      "border": "yellow"},
    "minimal":   {"primary": "white",       "accent": "bold white",
                  "ok": "white",            "err": "bright_red",
                  "dim": "dim white",       "border": "white"},
}

def get_palette(theme_name: str) -> dict:
    return BUILTIN_THEMES.get((theme_name or "cyberpunk").lower(),
                              BUILTIN_THEMES["cyberpunk"])


# ── DB stats ──────────────────────────────────────────────────────

def _get_profile_stats() -> dict:
    if not _DB_AVAILABLE:
        return {}
    try:
        db   = Database()
        rows = db.get_sessions(limit=9999)
        if not rows:
            return {}
        wpms = [r["wpm"]      for r in rows if r.get("wpm")]
        accs = [r["accuracy"] for r in rows if r.get("accuracy")]
        return {
            "sessions": len(rows),
            "best_wpm": max(wpms) if wpms else 0,
            "peak_acc": max(accs) if accs else 0,
        }
    except Exception:
        return {}

def _level(best_wpm: int) -> str:
    if best_wpm == 0:  return "Beginner"
    if best_wpm < 40:  return "Novice"
    if best_wpm < 60:  return "Intermediate"
    if best_wpm < 80:  return "Advanced"
    if best_wpm < 100: return "Expert"
    return "Elite"


# ═════════════════════════════════════════════════════════════════
#  Intro animation
# ═════════════════════════════════════════════════════════════════

_ASCII_LINES = [
    " ██╗  ██╗███████╗██╗   ██╗██╗  ██╗ ██████╗███████╗",
    " ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║  ██║██╔════╝██╔════╝",
    " █████╔╝ █████╗   ╚████╔╝ ███████║██║     █████╗  ",
    " ██╔═██╗ ██╔══╝    ╚██╔╝  ╚════██║██║     ██╔══╝  ",
    " ██║  ██╗███████╗   ██║        ██║╚██████╗███████╗ ",
    " ╚═╝  ╚═╝╚══════╝   ╚═╝        ╚═╝ ╚═════╝╚══════╝",
]

# colour pulse sequence: each entry is (style, sleep_seconds)
_PULSE = [
    ("dim cyan",        0.06),
    ("cyan",            0.06),
    ("bright_cyan",     0.07),
    ("bold bright_cyan",0.08),
    ("bold cyan",       0.07),
    ("cyan",            0.06),
]

def _print_banner(console: Console, style: str) -> None:
    """Print the full ASCII banner centered in the given style."""
    for line in _ASCII_LINES:
        console.print(Align.center(Text(line, style=style)))


def _intro_animation(console: Console, p: dict) -> None:
    """
    1. Reveal ASCII lines one-by-one (35 ms gap) — dim colour
    2. Colour pulse (no Live, just clear+redraw each frame)
    3. Tagline
    4. "Press any key to start" — blocks until keypress
    """
    # Step 1 — line reveal
    for i in range(len(_ASCII_LINES)):
        console.clear()
        for line in _ASCII_LINES[:i + 1]:
            console.print(Align.center(Text(line, style=p["dim"])))
        time.sleep(0.04)

    # Step 2 — colour pulse (clear+redraw, no Live)
    for style, delay in _PULSE:
        console.clear()
        _print_banner(console, style)
        time.sleep(delay)

    # Step 3 — tagline
    console.print()
    console.print(Align.center(
        Text("Precision typing for terminal operators",
             style=f"bold {p['accent']}")))
    console.print(Align.center(
        Text("Train speed, control, and consistency in a focused environment.",
             style=p["dim"])))
    console.print()

    # Step 4 — gate
    console.print(Align.center(
        Text("Press any key to start", style=p["dim"])))
    readchar.readkey()


# ═════════════════════════════════════════════════════════════════
#  Centered print helper
# ═════════════════════════════════════════════════════════════════

def _cprint(console: Console, renderable, width: int = MAX_WIDTH) -> None:
    """Print any Rich renderable centered, constrained to `width`."""
    console.print(Align.center(renderable, width=width))


# ═════════════════════════════════════════════════════════════════
#  Menu render
# ═════════════════════════════════════════════════════════════════

def _render_menu(console: Console, p: dict, theme: str,
                 profile: dict, stats: dict, status_msg: str) -> None:
    console.clear()

    # ── Top bar ───────────────────────────────────────────────────
    right = f"THEME: {theme.upper()}"
    bar_w = MAX_WIDTH
    gap   = max(2, bar_w - len("KEY4CE") - len(right))
    top   = Text()
    top.append("KEY4CE", style=f"bold {p['primary']}")
    top.append(" " * gap)
    top.append(right, style=p["dim"])
    _cprint(console, top)
    _cprint(console, Rule(style=p["border"]))
    console.print()

    # ── Tagline ───────────────────────────────────────────────────
    _cprint(console, Text("Precision typing for terminal operators",
                          style=f"bold {p['accent']}"))
    _cprint(console, Text("Train speed, control, and consistency in a focused environment.",
                          style=p["dim"]))
    console.print()

    # ── Two-column status panels ──────────────────────────────────
    # Build as a single fixed-width table so both halves stay equal
    W, V = p["dim"], "white"
    HALF = (MAX_WIDTH - 3) // 2   # -3 for the inner gap/border

    # left content
    lt = Table(box=None, show_header=False, pad_edge=False, padding=(0, 1))
    lt.add_column("k", style=W,  width=14, no_wrap=True)
    lt.add_column("v", style=V,  no_wrap=True)
    lt.add_row("Mode",         profile.get("mode", "words").title())
    lt.add_row("Length",       f"{profile.get('words', 50)} words")
    lt.add_row("Theme",        profile.get("theme", "cyberpunk").title())
    lt.add_row("Content Pack", "Standard")

    # right content
    rt = Table(box=None, show_header=False, pad_edge=False, padding=(0, 1))
    rt.add_column("k", style=W, width=14, no_wrap=True)
    rt.add_column("v", style=V, no_wrap=True)
    best_wpm = stats.get("best_wpm", 0)
    peak_acc = stats.get("peak_acc", 0.0)
    rt.add_row("Level",         _level(best_wpm))
    rt.add_row("Best WPM",      str(best_wpm) if best_wpm else "--")
    rt.add_row("Peak Accuracy", f"{peak_acc:.1f}%" if peak_acc else "--")
    rt.add_row("Sessions",      str(stats.get("sessions", 0)))

    left_panel  = Panel(lt, title="SESSION STATUS",   title_align="left",
                        border_style=p["border"], box=box.ROUNDED,
                        width=HALF, padding=(0, 1))
    right_panel = Panel(rt, title="PROFILE SNAPSHOT", title_align="left",
                        border_style=p["border"], box=box.ROUNDED,
                        width=HALF, padding=(0, 1))

    pair = Table.grid(padding=(0, 1))
    pair.add_column(width=HALF)
    pair.add_column(width=HALF)
    pair.add_row(left_panel, right_panel)
    _cprint(console, pair)
    console.print()

    # ── Ready panel ───────────────────────────────────────────────
    body = Text()
    body.append("Start a focused typing session using curated content.\n", style="white")
    body.append("Review performance trends, identify weak zones, and build consistency over time.",
                style=p["dim"])
    _cprint(console, Panel(body, title="READY", title_align="left",
                           border_style=p["border"], box=box.ROUNDED,
                           width=MAX_WIDTH, padding=(0, 1)))
    console.print()

    # ── Commands panel ────────────────────────────────────────────
    A = f"bold {p['accent']}"
    row1 = Text()
    for k, label in [("S","Start"),("T","Themes"),("C","Content"),
                      ("A","Analytics"),("X","Settings")]:
        row1.append(f"[{k}]", style=A)
        row1.append(f" {label}   ", style="white")
    row2 = Text()
    for k, label in [("H","Help"),("Q","Quit")]:
        row2.append(f"[{k}]", style=A)
        row2.append(f" {label}   ", style="white")
    cmd_body = Text()
    cmd_body.append_text(row1)
    cmd_body.append("\n")
    cmd_body.append_text(row2)
    _cprint(console, Panel(cmd_body, title="COMMANDS", title_align="left",
                           border_style=p["border"], box=box.ROUNDED,
                           width=MAX_WIDTH, padding=(0, 1)))

    # ── Status bar ────────────────────────────────────────────────
    console.print()
    _cprint(console, Text(f"Status: {status_msg}", style=p["dim"]))


# ═════════════════════════════════════════════════════════════════
#  Centered pickers
# ═════════════════════════════════════════════════════════════════

def _cycle_pick(console: Console, p: dict, title: str,
                options: list, current) -> object:
    idx = options.index(current) if current in options else 0
    while True:
        console.clear()
        _cprint(console, Rule(f" {title} ", style=p["border"]), MAX_WIDTH)
        console.print()

        for i, opt in enumerate(options):
            if i == idx:
                line = Text(f"  >  {opt}", style=f"bold {p['accent']}")
            else:
                line = Text(f"     {opt}", style=p["dim"])
            _cprint(console, line, MAX_WIDTH)

        console.print()
        _cprint(console,
                Text("  Up / Down   Enter to confirm   Esc to cancel", style=p["dim"]),
                MAX_WIDTH)

        ch = readchar.readkey()
        if   ch in (readchar.key.UP,   "k"): idx = (idx - 1) % len(options)
        elif ch in (readchar.key.DOWN, "j"): idx = (idx + 1) % len(options)
        elif ch in ("\r", "\n"):             return options[idx]
        elif ch in (readchar.key.ESC,  "q"): return current


def _themes_menu(console: Console, profile: dict, p: dict) -> None:
    chosen = _cycle_pick(console, p, "SELECT THEME",
                         list(BUILTIN_THEMES.keys()),
                         profile.get("theme", "cyberpunk"))
    profile["theme"] = chosen
    _save(PROFILE_F, profile)


def _content_menu(console: Console, profile: dict, p: dict) -> None:
    chosen_mode = _cycle_pick(console, p, "SELECT CONTENT MODE",
                              CONTENT_MODES, profile.get("mode", "words"))
    profile["mode"] = chosen_mode
    chosen_len = _cycle_pick(console, p, "SELECT LENGTH (words)",
                             [str(l) for l in LENGTHS],
                             str(profile.get("words", 50)))
    profile["words"] = int(chosen_len)
    _save(PROFILE_F, profile)


# ═════════════════════════════════════════════════════════════════
#  Settings — centered, inline (no external import)
# ═════════════════════════════════════════════════════════════════

def _settings_screen(console: Console, profile: dict, p: dict) -> None:
    SECTIONS = [
        ("Goals",     _settings_goals),
        ("Profile",   _settings_profile),
        ("< Back",    None),
    ]
    cursor = 0
    while True:
        console.clear()
        _cprint(console, Rule(" SETTINGS ", style=p["border"]), MAX_WIDTH)
        console.print()
        for i, (label, _) in enumerate(SECTIONS):
            style = f"bold {p['accent']}" if i == cursor else p["dim"]
            pre   = ">" if i == cursor else " "
            _cprint(console, Text(f"  {pre}  {label}", style=style), MAX_WIDTH)
        console.print()
        _cprint(console,
                Text("  Up / Down   Enter to open   Esc to return", style=p["dim"]),
                MAX_WIDTH)

        ch = readchar.readkey()
        if   ch in (readchar.key.UP,   "k"): cursor = (cursor - 1) % len(SECTIONS)
        elif ch in (readchar.key.DOWN, "j"): cursor = (cursor + 1) % len(SECTIONS)
        elif ch in ("\r", "\n"):
            label, fn = SECTIONS[cursor]
            if fn is None:
                return
            goals = _load(GOALS_F, {"daily_minutes": 15, "daily_sessions": 2})
            fn(console, profile, goals, p)
        elif ch in (readchar.key.ESC, "q"):
            return


def _settings_goals(console: Console, profile: dict, goals: dict, p: dict) -> None:
    PRESETS = {
        "Starter  (10 min / 1 session)":  {"daily_minutes": 10, "daily_sessions": 1},
        "Steady   (20 min / 2 sessions)": {"daily_minutes": 20, "daily_sessions": 2},
        "Intense  (40 min / 4 sessions)": {"daily_minutes": 40, "daily_sessions": 4},
    }
    MIN_OPT = ["5","10","15","20","30","40","60"]
    SES_OPT = ["1","2","3","4","5"]
    ITEMS = [
        ("Daily minutes",  "daily_minutes", MIN_OPT),
        ("Daily sessions", "daily_sessions",SES_OPT),
    ] + [(k, None, None) for k in PRESETS] + [("Save & return", None, None)]

    cursor = 0
    while True:
        console.clear()
        _cprint(console, Rule(" GOALS ", style=p["border"]), MAX_WIDTH)
        console.print()
        for i, (label, key, opts) in enumerate(ITEMS):
            hi  = f"bold {p['accent']}" if i == cursor else p["dim"]
            pre = ">" if i == cursor else " "
            val = f"  [ {goals.get(key, '')} ]" if key else ""
            _cprint(console, Text(f"  {pre}  {label}{val}", style=hi), MAX_WIDTH)
        console.print()
        _cprint(console,
                Text("  Up/Down   Left/Right to change   Enter to apply   Esc back",
                     style=p["dim"]), MAX_WIDTH)

        ch = readchar.readkey()
        if   ch in (readchar.key.UP,   "k"): cursor = (cursor - 1) % len(ITEMS)
        elif ch in (readchar.key.DOWN, "j"): cursor = (cursor + 1) % len(ITEMS)
        elif ch in (readchar.key.LEFT, readchar.key.RIGHT):
            label, key, opts = ITEMS[cursor]
            if key and opts:
                cur = str(goals.get(key, opts[0]))
                idx = opts.index(cur) if cur in opts else 0
                d   = -1 if ch == readchar.key.LEFT else 1
                goals[key] = int(opts[(idx + d) % len(opts)])
        elif ch in ("\r", "\n"):
            label, key, opts = ITEMS[cursor]
            if label == "Save & return":
                _save(GOALS_F, goals)
                return
            if label in PRESETS:
                goals.update(PRESETS[label])
        elif ch in (readchar.key.ESC, "q"):
            return


def _settings_profile(console: Console, profile: dict, goals: dict, p: dict) -> None:
    ITEMS = [
        ("Mode",          "mode",  CONTENT_MODES),
        ("Length",        "words", [str(l) for l in LENGTHS]),
        ("Theme",         "theme", list(BUILTIN_THEMES.keys())),
        ("Zen mode",      "zen",   ["off", "on"]),
        ("Save & return", None,    None),
    ]
    cursor = 0
    while True:
        console.clear()
        _cprint(console, Rule(" PROFILE ", style=p["border"]), MAX_WIDTH)
        console.print()
        for i, (label, key, opts) in enumerate(ITEMS):
            hi  = f"bold {p['accent']}" if i == cursor else p["dim"]
            pre = ">" if i == cursor else " "
            val = ""
            if key and opts:
                raw = profile.get(key, opts[0])
                if key == "zen":
                    raw = "on" if raw else "off"
                s   = str(raw)
                idx = opts.index(s) if s in opts else 0
                prv = opts[(idx - 1) % len(opts)]
                nxt = opts[(idx + 1) % len(opts)]
                val = f"   {prv}  [ {s} ]  {nxt}"
            _cprint(console, Text(f"  {pre}  {label}{val}", style=hi), MAX_WIDTH)
        console.print()
        _cprint(console,
                Text("  Up/Down   Left/Right to change   Enter to save   Esc back",
                     style=p["dim"]), MAX_WIDTH)

        ch = readchar.readkey()
        if   ch in (readchar.key.UP,   "k"): cursor = (cursor - 1) % len(ITEMS)
        elif ch in (readchar.key.DOWN, "j"): cursor = (cursor + 1) % len(ITEMS)
        elif ch in (readchar.key.LEFT, readchar.key.RIGHT):
            label, key, opts = ITEMS[cursor]
            if not key or not opts:
                continue
            raw = profile.get(key, opts[0])
            if key == "zen":
                raw = "on" if raw else "off"
            s   = str(raw)
            idx = opts.index(s) if s in opts else 0
            d   = -1 if ch == readchar.key.LEFT else 1
            nv  = opts[(idx + d) % len(opts)]
            if key == "zen":
                profile[key] = (nv == "on")
            elif key == "words":
                profile[key] = int(nv)
            else:
                profile[key] = nv
        elif ch in ("\r", "\n"):
            label, key, opts = ITEMS[cursor]
            if label == "Save & return":
                _save(PROFILE_F, profile)
                return
        elif ch in (readchar.key.ESC, "q"):
            return


def _help_screen(console: Console, p: dict) -> None:
    console.clear()
    _cprint(console, Rule(" HELP ", style=p["border"]), MAX_WIDTH)
    console.print()
    rows = [
        ("During a session", ""),
        ("  Backspace",  "Delete the last character"),
        ("  Tab",        "Restart the current session"),
        ("  Esc",        "Exit to main menu"),
        ("", ""),
        ("After a session", ""),
        ("  R",  "Retry"),
        ("  F",  "Focus drill on weakest keys"),
        ("  M",  "Main menu"),
        ("  Q",  "Quit"),
        ("", ""),
        ("Main menu", ""),
        ("  S",  "Start session"),
        ("  T",  "Select theme"),
        ("  C",  "Select content mode and length"),
        ("  A",  "Analytics dashboard"),
        ("  X",  "Settings"),
        ("  H",  "This screen"),
        ("  Q",  "Quit"),
    ]
    t = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2),
              width=MAX_WIDTH - 4)
    t.add_column("key",  style=f"bold {p['accent']}", min_width=20)
    t.add_column("desc", style="white")
    for k, v in rows:
        if v == "":
            t.add_row(Text(k, style=f"bold {p['primary']}"), "")
        else:
            t.add_row(k, v)
    _cprint(console, t, MAX_WIDTH)
    console.print()
    _cprint(console, Text("Press any key to return.", style=p["dim"]), MAX_WIDTH)
    readchar.readkey()


# ═════════════════════════════════════════════════════════════════
#  Entry point
# ═════════════════════════════════════════════════════════════════

def run_menu(console: Console | None = None) -> dict | None:
    global _intro_shown

    if console is None:
        console = Console()

    profile = _load(PROFILE_F, {"mode": "words", "words": 50,
                                "theme": "cyberpunk", "zen": False})
    theme   = profile.get("theme", "cyberpunk")
    p       = get_palette(theme)

    if not _intro_shown:
        _intro_shown = True
        try:
            _intro_animation(console, p)
        except Exception:
            pass

    status_msg = "Waiting for input"

    while True:
        profile = _load(PROFILE_F, {"mode": "words", "words": 50,
                                    "theme": "cyberpunk", "zen": False})
        theme   = profile.get("theme", "cyberpunk")
        p       = get_palette(theme)
        stats   = _get_profile_stats()

        _render_menu(console, p, theme, profile, stats, status_msg)

        ch = readchar.readkey()

        if   ch in ("s", "S", "\r", "\n"):
            return profile
        elif ch in ("t", "T"):
            _themes_menu(console, profile, p)
            profile = _load(PROFILE_F, {"mode": "words", "words": 50,
                                        "theme": "cyberpunk", "zen": False})
            status_msg = f"Theme set to {profile.get('theme', 'cyberpunk').title()}"
        elif ch in ("c", "C", "p", "P"):
            _content_menu(console, profile, p)
            profile = _load(PROFILE_F, {"mode": "words", "words": 50,
                                        "theme": "cyberpunk", "zen": False})
            status_msg = f"Mode: {profile.get('mode')}  |  Length: {profile.get('words')} words"
        elif ch in ("a", "A"):
            return {"_action": "analytics", **profile}
        elif ch in ("x", "X"):
            _settings_screen(console, profile, p)
            profile = _load(PROFILE_F, {"mode": "words", "words": 50,
                                        "theme": "cyberpunk", "zen": False})
            status_msg = "Settings saved"
        elif ch in ("h", "H", "?"):
            _help_screen(console, p)
            status_msg = "Waiting for input"
        elif ch in ("q", "Q", readchar.key.ESC):
            return None
        else:
            status_msg = "Unknown command. Press [H] for help."
