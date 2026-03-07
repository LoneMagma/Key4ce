"""
key4ce/ui/screens/analytics.py
────────────────────────────────
Performance Analytics dashboard.

Layout:

  KEY4CE :: PERFORMANCE ANALYTICS                        THEME: CYBERPUNK
  ────────────────────────────────────────────────────────────────────────

  Overview
  [ Avg WPM       ] [ Avg Accuracy   ] [ Total Sessions ]

  Highlights
  [ Best WPM      ] [ Best Accuracy  ] [ Lowest Error Run ]

  Trend Summary
  [ Narrative from recent sessions                                        ]

  AI Recommendation
  [ 1-2 lines from Groq or deterministic fallback                        ]

  Session Breakdown
  [ Last 5 runs — WPM / Accuracy / Errors                                ]

  [R] Refresh   [B] Back
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

import readchar
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# ── Palette ───────────────────────────────────────────────────────
BUILTIN_THEMES = {
    "cyberpunk": {"primary": "cyan",    "accent": "bright_cyan",
                  "ok": "green",        "err": "red",
                  "dim": "dim cyan",    "border": "cyan"},
    "nord":      {"primary": "blue",    "accent": "bright_blue",
                  "ok": "green",        "err": "red",
                  "dim": "dim blue",    "border": "blue"},
    "dracula":   {"primary": "magenta", "accent": "bright_magenta",
                  "ok": "green",        "err": "red",
                  "dim": "dim magenta", "border": "magenta"},
    "monokai":   {"primary": "yellow",  "accent": "bright_yellow",
                  "ok": "green",        "err": "red",
                  "dim": "dim yellow",  "border": "yellow"},
    "minimal":   {"primary": "white",   "accent": "bold white",
                  "ok": "white",        "err": "bright_red",
                  "dim": "dim white",   "border": "white"},
}

def get_palette(theme: str) -> dict:
    return BUILTIN_THEMES.get((theme or "cyberpunk").lower(),
                              BUILTIN_THEMES["cyberpunk"])


# ── DB helpers ────────────────────────────────────────────────────

def _fetch_sessions(limit: int = 9999) -> list[dict]:
    try:
        from key4ce.data.db import Database
        return Database().get_sessions(limit=limit) or []
    except Exception:
        return []


def _compute_stats(rows: list[dict]) -> dict:
    if not rows:
        return {}

    wpms  = [r["wpm"]      for r in rows if r.get("wpm")]
    accs  = [r["accuracy"] for r in rows if r.get("accuracy")]
    errs  = [r.get("errors", 0) for r in rows]

    recent = rows[:10]
    recent_wpms = [r["wpm"] for r in recent if r.get("wpm")]
    older_wpms  = [r["wpm"] for r in rows[10:20] if r.get("wpm")]

    speed_trend = "stable"
    if recent_wpms and older_wpms:
        if sum(recent_wpms) / len(recent_wpms) > sum(older_wpms) / len(older_wpms) * 1.05:
            speed_trend = "improving"
        elif sum(recent_wpms) / len(recent_wpms) < sum(older_wpms) / len(older_wpms) * 0.95:
            speed_trend = "declining"

    recent_accs  = [r["accuracy"] for r in recent if r.get("accuracy")]
    older_accs   = [r["accuracy"] for r in rows[10:20] if r.get("accuracy")]
    acc_trend = "stable"
    if recent_accs and older_accs:
        if sum(recent_accs) / len(recent_accs) > sum(older_accs) / len(older_accs) + 0.5:
            acc_trend = "improving"
        elif sum(recent_accs) / len(recent_accs) < sum(older_accs) / len(older_accs) - 0.5:
            acc_trend = "declining"

    return {
        "count":        len(rows),
        "avg_wpm":      round(sum(wpms) / len(wpms), 1) if wpms else 0,
        "avg_acc":      round(sum(accs) / len(accs), 1) if accs else 0,
        "best_wpm":     round(max(wpms), 1) if wpms else 0,
        "best_acc":     round(max(accs), 1) if accs else 0,
        "min_errors":   min(errs) if errs else 0,
        "speed_trend":  speed_trend,
        "acc_trend":    acc_trend,
        "recent_5":     rows[:5],
    }


# ── Trend narrative ───────────────────────────────────────────────

def _trend_narrative(stats: dict) -> str:
    if not stats:
        return "No session data recorded yet. Complete a session to begin tracking progress."

    speed = stats["speed_trend"]
    acc   = stats["acc_trend"]

    if speed == "improving" and acc == "improving":
        return (
            "Both speed and accuracy are trending upward across recent sessions. "
            "Current trajectory is strong — maintain consistent daily practice to lock in the gains."
        )
    if speed == "improving" and acc == "declining":
        return (
            "Speed has increased over recent sessions, but accuracy is slipping slightly. "
            "This is a common trade-off — consider slowing down by 5–10 WPM to stabilise error rate."
        )
    if speed == "declining" and acc == "improving":
        return (
            "Accuracy is improving as speed has dropped slightly. "
            "This is a healthy correction phase — rebuild speed gradually once accuracy feels natural."
        )
    if speed == "stable" and acc == "stable":
        return (
            "Performance has been consistent recently. "
            "To push through a plateau, try longer sessions or switch to a more challenging content mode."
        )
    if speed == "declining" and acc == "declining":
        return (
            "Both metrics have dipped in recent sessions. "
            "A short break or a switch to shorter, low-pressure runs can help reset consistency."
        )
    return (
        "Recent sessions show mixed signals. "
        "Focus on one metric at a time — pick either speed or accuracy as the priority for your next block."
    )


# ── AI recommendation (Groq + local fallback) ─────────────────────

def _local_recommendation(stats: dict) -> str:
    if not stats:
        return "Complete at least one session to receive a personalised recommendation."

    avg_wpm = stats.get("avg_wpm", 0)
    avg_acc = stats.get("avg_acc", 0)
    best    = stats.get("best_wpm", 0)

    if avg_acc < 93:
        return (
            "Accuracy is the limiting factor right now. "
            "Drop speed by 10 WPM and focus on eliminating errors before increasing pace."
        )
    if avg_acc < 96 and avg_wpm > 60:
        return (
            f"At {avg_wpm} WPM your accuracy sits at {avg_acc}% — "
            "try 60-second focused runs at a controlled pace to bring accuracy above 97% consistently."
        )
    if avg_wpm < 40:
        return (
            "Build baseline fluency first. Short daily sessions of 25 words with no time pressure "
            "will compound into real gains within two weeks."
        )
    if best > 0 and avg_wpm > best * 0.90:
        return (
            f"You are consistently close to your personal best of {best} WPM. "
            "Push for longer clean sessions to convert that peak into a reliable average."
        )
    if avg_acc >= 98 and avg_wpm < 70:
        return (
            "Accuracy is excellent. You have room to safely increase pace — "
            "push WPM targets up by 5 each session until accuracy begins to drop."
        )
    return (
        f"Solid baseline at {avg_wpm} WPM / {avg_acc}% accuracy. "
        "Vary content modes to expose new character patterns and prevent plateau."
    )


def _groq_recommendation(stats: dict) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

    prompt = (
        f"You are a typing coach. Give a single actionable recommendation "
        f"of 1-2 sentences based on these stats:\n"
        f"Average WPM: {stats.get('avg_wpm')}, "
        f"Average Accuracy: {stats.get('avg_acc')}%, "
        f"Best WPM: {stats.get('best_wpm')}, "
        f"Sessions: {stats.get('count')}, "
        f"Speed trend: {stats.get('speed_trend')}, "
        f"Accuracy trend: {stats.get('acc_trend')}.\n"
        f"Be direct, specific, and keep it under 40 words."
    )

    payload = json.dumps({
        "model": model,
        "max_tokens": 80,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()
            # Clamp to 2 sentences max
            sentences = text.split(". ")
            return ". ".join(sentences[:2]).strip() + ("." if not text.endswith(".") else "")
    except Exception:
        return None


def get_recommendation(stats: dict) -> tuple[str, str]:
    """Returns (recommendation_text, source) where source is 'AI' or 'Local'."""
    if not stats:
        return _local_recommendation(stats), "Local"

    ai = _groq_recommendation(stats)
    if ai:
        return ai, "AI"
    return _local_recommendation(stats), "Local"


# ═════════════════════════════════════════════════════════════════
#  Renderer
# ═════════════════════════════════════════════════════════════════

def _metric_card(label: str, value: str, p: dict) -> Panel:
    body = Text()
    body.append(value, style=f"bold {p['accent']}")
    return Panel(
        body,
        title=label,
        title_align="left",
        border_style=p["border"],
        box=box.SIMPLE_HEAD,
        padding=(0, 2),
    )


def _render_analytics(console: Console, p: dict, theme: str,
                       stats: dict, rec: str, rec_source: str) -> None:
    console.clear()

    # ── Header ────────────────────────────────────────────────────
    title = "KEY4CE :: PERFORMANCE ANALYTICS"
    right = f"THEME: {theme.upper()}"
    gap   = max(2, console.width - len(title) - len(right) - 4)
    hdr   = Text()
    hdr.append(title, style=f"bold {p['primary']}")
    hdr.append(" " * gap)
    hdr.append(right, style=p["dim"])
    console.print(hdr)
    console.print(Rule(style=p["border"]))
    console.print()

    if not stats:
        console.print(Text(
            "  No session data found. Complete a typing session to begin.",
            style=p["dim"],
        ))
        console.print()
    else:
        # ── Overview row ──────────────────────────────────────────
        console.print(Text("  Overview", style=f"bold {p['primary']}"))
        console.print(Columns([
            _metric_card("Average WPM",      str(stats["avg_wpm"]),    p),
            _metric_card("Average Accuracy", f"{stats['avg_acc']}%",  p),
            _metric_card("Total Sessions",   str(stats["count"]),      p),
        ], equal=True, expand=True))
        console.print()

        # ── Highlights row ────────────────────────────────────────
        console.print(Text("  Highlights", style=f"bold {p['primary']}"))
        console.print(Columns([
            _metric_card("Best WPM",         str(stats["best_wpm"]),   p),
            _metric_card("Best Accuracy",    f"{stats['best_acc']}%", p),
            _metric_card("Lowest Error Run", str(stats["min_errors"]), p),
        ], equal=True, expand=True))
        console.print()

        # ── Trend summary ─────────────────────────────────────────
        console.print(Text("  Trend Summary", style=f"bold {p['primary']}"))
        console.print(Panel(
            Text(_trend_narrative(stats), style="white"),
            title_align="left",
            border_style=p["border"],
            box=box.SIMPLE_HEAD,
            padding=(0, 2),
        ))
        console.print()

    # ── AI Recommendation ─────────────────────────────────────────
    panel_title = f"AI Recommendation" if rec_source == "AI" else "Recommendation"
    source_note = Text()
    source_note.append(rec, style="white")
    if rec_source == "AI":
        source_note.append("\n")
        source_note.append("  Powered by Groq", style=p["dim"])

    console.print(Text(f"  {panel_title}", style=f"bold {p['primary']}"))
    console.print(Panel(
        source_note,
        title_align="left",
        border_style=p["border"],
        box=box.SIMPLE_HEAD,
        padding=(0, 2),
    ))
    console.print()

    # ── Session Breakdown ─────────────────────────────────────────
    if stats and stats.get("recent_5"):
        console.print(Text("  Session Breakdown", style=f"bold {p['primary']}"))

        t = Table(box=box.SIMPLE_HEAD, show_header=True,
                  header_style=f"bold {p['dim']}", pad_edge=False,
                  border_style=p["border"])
        t.add_column("#",         style=p["dim"],  width=4)
        t.add_column("WPM",       style=f"bold {p['accent']}", min_width=8)
        t.add_column("Accuracy",  style="white",   min_width=12)
        t.add_column("Errors",    style="white",   min_width=8)
        t.add_column("Mode",      style=p["dim"],  min_width=10)

        for i, row in enumerate(stats["recent_5"], 1):
            err_style = f"bold {p['err']}" if row.get("errors", 0) > 5 else "white"
            t.add_row(
                str(i),
                str(row.get("wpm", "--")),
                f"{row.get('accuracy', '--')}%",
                Text(str(row.get("errors", "--")), style=err_style),
                row.get("mode", "--"),
            )

        console.print(t)
        console.print()

    # ── Commands ──────────────────────────────────────────────────
    cmd = Text()
    for key, label in [("R", "Refresh"), ("B", "Back")]:
        cmd.append(f"[{key}]", style=f"bold {p['accent']}")
        cmd.append(f" {label}   ", style="white")
    console.print(cmd)
    console.print()


# ═════════════════════════════════════════════════════════════════
#  Entry point
# ═════════════════════════════════════════════════════════════════

def run_analytics(
    profile: dict,
    console: Console | None = None,
) -> None:
    """Display the analytics dashboard. Returns when user presses B."""
    if console is None:
        console = Console()

    theme = profile.get("theme", "cyberpunk")
    p     = get_palette(theme)

    def _load():
        rows  = _fetch_sessions()
        stats = _compute_stats(rows)
        rec, src = get_recommendation(stats)
        return stats, rec, src

    # Show loading state while fetching / calling API
    console.clear()
    hdr = Text()
    hdr.append("KEY4CE :: PERFORMANCE ANALYTICS", style=f"bold {p['primary']}")
    console.print(hdr)
    console.print(Rule(style=p["border"]))
    console.print()
    console.print(Text("  Loading...", style=p["dim"]))

    stats, rec, src = _load()

    while True:
        _render_analytics(console, p, theme, stats, rec, src)

        ch = readchar.readkey()
        if ch in ("r", "R"):
            # Refresh — reload data + re-query AI
            console.clear()
            console.print(Text("  Refreshing...", style=p["dim"]))
            stats, rec, src = _load()
        elif ch in ("b", "B", readchar.key.ESC, readchar.key.BACKSPACE, "q", "Q"):
            return
