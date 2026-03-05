"""Entry point for key4ce — full argparse CLI."""
from __future__ import annotations

import json
from pathlib import Path

GOALS_PATH = Path.home() / ".key4ce" / "goals.json"
DEFAULT_GOALS = {"daily_minutes": 15, "daily_sessions": 1}
GOAL_TEMPLATES = {
    "starter": {"daily_minutes": 10, "daily_sessions": 1},
    "steady": {"daily_minutes": 20, "daily_sessions": 2},
    "intense": {"daily_minutes": 35, "daily_sessions": 3},
}

PROFILE_PATH = Path.home() / ".key4ce" / "profile.json"
DEFAULT_PROFILE = {"preferred_mode": "sentences", "preferred_words": 50, "preferred_theme": "cyberpunk"}


def _load_goals(path: Path = GOALS_PATH) -> dict:
    """Load persisted goals (or defaults)."""
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "daily_minutes": int(data.get("daily_minutes", DEFAULT_GOALS["daily_minutes"])),
                "daily_sessions": int(data.get("daily_sessions", DEFAULT_GOALS["daily_sessions"])),
            }
    except Exception:
        pass
    return dict(DEFAULT_GOALS)


def _save_goals(goals: dict, path: Path = GOALS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "daily_minutes": max(1, int(goals.get("daily_minutes", DEFAULT_GOALS["daily_minutes"]))),
        "daily_sessions": max(1, int(goals.get("daily_sessions", DEFAULT_GOALS["daily_sessions"]))),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _compute_today_progress(sessions: list) -> dict:
    """Compute today's session/minute totals."""
    from datetime import datetime

    today = datetime.now().date()
    today_sessions = []
    for s in sessions:
        try:
            if datetime.fromisoformat(s.ts).date() == today:
                today_sessions.append(s)
        except Exception:
            continue

    total_sessions = len(today_sessions)
    total_minutes = round(sum(s.duration for s in today_sessions) / 60, 1)
    return {"today_sessions": total_sessions, "today_minutes": total_minutes}


def _print_goals_status(as_json: bool = False) -> None:
    """Show daily goal targets and today's progress."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    goals = _load_goals()

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    db.close()

    progress = _compute_today_progress(sessions)

    payload = {
        "goals": goals,
        "progress": progress,
        "met": {
            "daily_sessions": progress["today_sessions"] >= goals["daily_sessions"],
            "daily_minutes": progress["today_minutes"] >= goals["daily_minutes"],
        },
    }

    if as_json:
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  goals")
    c.print()
    c.print(f"  [bold]Target Sessions[/bold]  {goals['daily_sessions']}")
    c.print(f"  [bold]Target Minutes[/bold]   {goals['daily_minutes']}")
    c.print(f"  [bold]Today Sessions[/bold]   {progress['today_sessions']}")
    c.print(f"  [bold]Today Minutes[/bold]    {progress['today_minutes']:.1f}")
    c.print()


def _set_goals(daily_minutes: int | None = None, daily_sessions: int | None = None) -> dict:
    """Update persisted goals and return new goal object."""
    goals = _load_goals()
    if daily_minutes is not None:
        goals["daily_minutes"] = max(1, int(daily_minutes))
    if daily_sessions is not None:
        goals["daily_sessions"] = max(1, int(daily_sessions))
    _save_goals(goals)
    return goals


def _apply_goal_template(name: str) -> dict:
    """Apply a named goal template and return updated goals."""
    key = str(name).strip().lower()
    if key not in GOAL_TEMPLATES:
        valid = ", ".join(sorted(GOAL_TEMPLATES))
        raise ValueError(f"Unknown goals preset: {name}. Choose one of: {valid}")
    preset = GOAL_TEMPLATES[key]
    return _set_goals(preset["daily_minutes"], preset["daily_sessions"])


def _load_profile(path: Path = PROFILE_PATH) -> dict:
    """Load local user profile preferences (or defaults)."""
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "preferred_mode": str(data.get("preferred_mode", DEFAULT_PROFILE["preferred_mode"])),
                "preferred_words": max(10, int(data.get("preferred_words", DEFAULT_PROFILE["preferred_words"]))),
                "preferred_theme": str(data.get("preferred_theme", DEFAULT_PROFILE["preferred_theme"])),
            }
    except Exception:
        pass
    return dict(DEFAULT_PROFILE)


def _save_profile(profile: dict, path: Path = PROFILE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "preferred_mode": str(profile.get("preferred_mode", DEFAULT_PROFILE["preferred_mode"])),
        "preferred_words": max(10, int(profile.get("preferred_words", DEFAULT_PROFILE["preferred_words"]))),
        "preferred_theme": str(profile.get("preferred_theme", DEFAULT_PROFILE["preferred_theme"])),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _set_profile(preferred_mode: str | None = None, preferred_words: int | None = None, preferred_theme: str | None = None) -> dict:
    """Update and persist profile preferences."""
    profile = _load_profile()
    if preferred_mode is not None:
        profile["preferred_mode"] = str(preferred_mode)
    if preferred_words is not None:
        profile["preferred_words"] = max(10, int(preferred_words))
    if preferred_theme is not None:
        profile["preferred_theme"] = str(preferred_theme)
    _save_profile(profile)
    return profile


def _print_profile(as_json: bool = False) -> None:
    """Print persisted profile preferences."""
    from rich.console import Console
    from key4ce.themes.themes import DEFAULT_THEME

    profile = _load_profile()
    if as_json:
        print(json.dumps(profile, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  profile")
    c.print()
    c.print(f"  [bold]Preferred Mode[/bold]   {profile['preferred_mode']}")
    c.print(f"  [bold]Preferred Words[/bold]  {profile['preferred_words']}")
    c.print(f"  [bold]Preferred Theme[/bold]  {profile['preferred_theme']}")
    c.print()


def _build_brag_card(summary: dict) -> str:
    """Build a shareable, plain-text progress card."""
    days = summary.get("days", 7)
    sessions = summary.get("sessions", 0)
    avg_wpm = summary.get("avg_wpm", 0.0)
    avg_acc = summary.get("avg_accuracy", 0.0)
    best_wpm = summary.get("best_wpm", 0.0)
    streak = summary.get("current_streak_days", 0)

    if sessions == 0:
        return (
            f"⌨️ Key4ce {days}-day check-in\n"
            "No sessions yet this window — starting today."
        )

    return (
        f"⌨️ Key4ce {days}-day check-in\n"
        f"• Sessions: {sessions}\n"
        f"• Avg WPM: {avg_wpm:.1f}\n"
        f"• Avg Accuracy: {avg_acc:.1f}%\n"
        f"• Best WPM: {best_wpm:.1f}\n"
        f"• Current Streak: {streak} day(s)\n"
        "#Key4ce #Typing"
    )


def _print_brag(days: int = 7) -> None:
    """Print a shareable progress card."""
    from key4ce.data.db import Database

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    db.close()

    summary = _summarize_recent_sessions(sessions, days=days)
    print(_build_brag_card(summary))


def _compute_speed_drops(timings: list[int], top: int = 5) -> list[dict]:
    """Return the slowest timing spikes from a session timing series."""
    if not timings:
        return []

    drops = [
        {"position": i + 1, "ms": int(ms)}
        for i, ms in enumerate(timings)
        if isinstance(ms, (int, float))
    ]
    drops.sort(key=lambda x: x["ms"], reverse=True)
    return drops[: max(1, int(top))]


def _print_speed_drops(top: int = 5, as_json: bool = False) -> None:
    """Show where typing pace dropped most in the latest session."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    db = Database()
    db.connect()
    sessions = db.list_sessions(limit=1)
    db.close()

    if not sessions:
        payload = {"session": None, "drops": []}
        if as_json:
            print(json.dumps(payload, indent=2))
            return
        Console().print("[dim]No sessions recorded yet. Run a session first.[/dim]")
        return

    latest = sessions[0]
    drops = _compute_speed_drops(latest.timings, top=top)
    payload = {
        "session": {
            "id": latest.id,
            "ts": latest.ts,
            "source": latest.source,
            "wpm": latest.wpm,
            "accuracy": latest.accuracy,
        },
        "drops": drops,
    }

    if as_json:
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  pace drops (latest session)")
    c.print()
    c.print(f"  [bold]Source[/bold]     {latest.source}")
    c.print(f"  [bold]Result[/bold]     {latest.wpm:.1f} WPM @ {latest.accuracy:.1f}%")
    if not drops:
        c.print("  [dim]No timing data available for this session.[/dim]")
        c.print()
        return
    c.print("  [bold]Slowest positions[/bold]")
    for d in drops:
        c.print(f"    • #{d['position']}: {d['ms']} ms")
    c.print()


def _compute_streaks(sessions: list) -> tuple[int, int]:
    """Return (current_streak_days, longest_streak_days) from session timestamps."""
    from datetime import datetime, timedelta

    days = set()
    for s in sessions:
        try:
            days.add(datetime.fromisoformat(s.ts).date())
        except Exception:
            continue

    if not days:
        return 0, 0

    # longest streak across all recorded days
    sorted_days = sorted(days)
    longest = 1
    run = 1
    for i in range(1, len(sorted_days)):
        if sorted_days[i] == sorted_days[i - 1] + timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    # current streak anchored at today (or yesterday as grace)
    today = datetime.now().date()
    anchor = today if today in days else (today - timedelta(days=1) if (today - timedelta(days=1)) in days else None)
    if anchor is None:
        return 0, longest

    current = 0
    d = anchor
    while d in days:
        current += 1
        d -= timedelta(days=1)

    return current, longest



def _summarize_recent_sessions(recent_sessions: list, days: int = 7) -> dict:
    """Build a compact summary for sessions in the last `days` days."""
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=days)
    in_window = []
    for s in recent_sessions:
        try:
            ts = datetime.fromisoformat(s.ts)
        except Exception:
            continue
        if ts >= cutoff:
            in_window.append(s)

    if not in_window:
        return {
            "days": days,
            "sessions": 0,
            "avg_wpm": 0.0,
            "avg_accuracy": 0.0,
            "best_wpm": 0.0,
            "total_minutes": 0.0,
            "current_streak_days": 0,
            "longest_streak_days": 0,
        }

    sessions = len(in_window)
    avg_wpm = sum(s.wpm for s in in_window) / sessions
    avg_accuracy = sum(s.accuracy for s in in_window) / sessions
    best_wpm = max(s.wpm for s in in_window)
    total_minutes = sum(s.duration for s in in_window) / 60
    current_streak, longest_streak = _compute_streaks(recent_sessions)

    return {
        "days": days,
        "sessions": sessions,
        "avg_wpm": round(avg_wpm, 1),
        "avg_accuracy": round(avg_accuracy, 1),
        "best_wpm": round(best_wpm, 1),
        "total_minutes": round(total_minutes, 1),
        "current_streak_days": current_streak,
        "longest_streak_days": longest_streak,
    }










def _build_coach_plan(recent_sessions: list, focus_data: object, days: int = 7) -> dict:
    """Build a minimal adaptive coaching plan from recent history."""
    summary = _summarize_recent_sessions(recent_sessions, days=days)

    weak_digraphs = list(getattr(focus_data, "weak_digraphs", []) or [])
    problem_chars = list(getattr(focus_data, "problem_chars", []) or [])

    drills: list[dict] = []
    if weak_digraphs:
        drills.append({"type": "digraph", "targets": weak_digraphs[:3], "words": 25})
    if problem_chars:
        drills.append({"type": "keys", "targets": problem_chars[:5], "words": 25})

    if summary["sessions"] == 0:
        next_step = "Start with one 25-word run, then execute focus mode once."
    elif summary["avg_accuracy"] < 93:
        next_step = "Prioritize accuracy: run focus mode and keep pace relaxed."
    elif summary["avg_wpm"] < 45:
        next_step = "Run two short sessions (25 words) to build rhythm, then one challenge."
    else:
        next_step = "Attempt today's challenge and then compare in leaderboard."

    return {
        "window_days": days,
        "summary": summary,
        "drills": drills,
        "next_step": next_step,
    }


def _print_coach(days: int = 7, as_json: bool = False) -> None:
    """Print adaptive coaching plan from recent local data."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    focus_data = db.get_focus_data()
    db.close()

    plan = _build_coach_plan(sessions, focus_data, days=days)

    if as_json:
        print(json.dumps(plan, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  coach ({days}-day)")
    c.print()
    c.print(f"  [bold]Sessions[/bold]    {plan['summary']['sessions']}")
    c.print(f"  [bold]Avg WPM[/bold]     {plan['summary']['avg_wpm']:.1f}")
    c.print(f"  [bold]Avg Accuracy[/bold] {plan['summary']['avg_accuracy']:.1f}%")
    c.print()
    if plan["drills"]:
        c.print("  [bold]Suggested Drills[/bold]")
        for drill in plan["drills"]:
            targets = ", ".join(drill["targets"])
            c.print(f"  • {drill['type']} targets: {targets} ({drill['words']} words)")
        c.print()
    c.print(f"  [bold]Next Step[/bold]  {plan['next_step']}")
    c.print()




def _compute_provider_health(records: list, days: int = 30) -> list[dict]:
    """Estimate provider reliability from recent usage and outcomes."""
    from datetime import datetime, timedelta

    from key4ce.content.base import ProviderRegistry
    from key4ce.content.builtin import BuiltinContent, CATEGORIES
    from key4ce.content.loader import EXTERNAL_CATEGORIES

    registry = ProviderRegistry()
    registry.register(BuiltinContent())

    provider_map: dict[str, str] = {k: "builtin" for k in CATEGORIES.keys()}
    provider_map.update({k: "external" for k in EXTERNAL_CATEGORIES.keys()})
    provider_map["focus"] = "builtin"

    cutoff = datetime.now() - timedelta(days=max(1, int(days)))

    stats: dict[str, dict[str, float]] = {
        "builtin": {"sessions": 0.0, "avg_acc_sum": 0.0, "avg_wpm_sum": 0.0},
        "external": {"sessions": 0.0, "avg_acc_sum": 0.0, "avg_wpm_sum": 0.0},
    }

    for r in records:
        try:
            ts = datetime.fromisoformat(r.ts)
        except Exception:
            continue
        if ts < cutoff:
            continue

        provider = provider_map.get(str(r.source), "builtin")
        row = stats.setdefault(provider, {"sessions": 0.0, "avg_acc_sum": 0.0, "avg_wpm_sum": 0.0})
        row["sessions"] += 1
        row["avg_acc_sum"] += float(r.accuracy)
        row["avg_wpm_sum"] += float(r.wpm)

    out: list[dict] = []

    availability = {row["source_type"]: bool(row["available"]) for row in registry.availability_snapshot()}
    availability.setdefault("external", True)

    for source_type in ["builtin", "external"]:
        row = stats.get(source_type, {"sessions": 0.0, "avg_acc_sum": 0.0, "avg_wpm_sum": 0.0})
        sessions = int(row["sessions"])
        if sessions > 0:
            avg_acc = row["avg_acc_sum"] / sessions
            avg_wpm = row["avg_wpm_sum"] / sessions
        else:
            avg_acc = 0.0
            avg_wpm = 0.0

        score = 50.0
        if sessions > 0:
            score = min(100.0, max(0.0, 30.0 + (avg_acc * 0.4) + min(avg_wpm, 100.0) * 0.3))
        if not availability.get(source_type, False):
            score = max(0.0, score - 40.0)

        out.append(
            {
                "provider": source_type,
                "available": availability.get(source_type, False),
                "sessions": sessions,
                "avg_accuracy": round(avg_acc, 1),
                "avg_wpm": round(avg_wpm, 1),
                "reliability": round(score, 1),
            }
        )

    out.sort(key=lambda x: x["reliability"], reverse=True)
    return out


def _print_provider_health(days: int = 30, as_json: bool = False) -> None:
    """Print provider reliability snapshot (phase 3 readiness)."""
    from rich.console import Console
    from rich.table import Table
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    db.close()

    rows = _compute_provider_health(sessions, days=days)
    payload = {"window_days": days, "providers": rows}

    if as_json:
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  provider health ({days}-day)")
    c.print()
    table = Table("Provider", "Available", "Sessions", "Avg Acc", "Avg WPM", "Reliability", border_style=t.dim, header_style=f"bold {t.secondary}")
    for row in rows:
        table.add_row(
            row["provider"],
            "yes" if row["available"] else "no",
            str(row["sessions"]),
            f"{row['avg_accuracy']:.1f}%",
            f"{row['avg_wpm']:.1f}",
            f"{row['reliability']:.1f}",
        )
    c.print(table)
    c.print()

def _compute_achievements(records: list) -> list[dict]:
    """Compute simple milestone achievements from local sessions."""
    total_sessions = len(records)
    if total_sessions == 0:
        return []

    best_wpm = max(float(r.wpm) for r in records)
    best_acc = max(float(r.accuracy) for r in records)
    total_minutes = sum(float(r.duration) for r in records) / 60.0

    unlocked: list[dict] = []

    if total_sessions >= 1:
        unlocked.append({"id": "first_run", "title": "First Run", "detail": "Complete your first session."})
    if total_sessions >= 10:
        unlocked.append({"id": "ten_sessions", "title": "Consistency I", "detail": "Complete 10 sessions."})
    if total_sessions >= 50:
        unlocked.append({"id": "fifty_sessions", "title": "Consistency II", "detail": "Complete 50 sessions."})

    if best_wpm >= 40:
        unlocked.append({"id": "speed_40", "title": "Speed Tier 1", "detail": "Reach 40 WPM."})
    if best_wpm >= 60:
        unlocked.append({"id": "speed_60", "title": "Speed Tier 2", "detail": "Reach 60 WPM."})
    if best_wpm >= 80:
        unlocked.append({"id": "speed_80", "title": "Speed Tier 3", "detail": "Reach 80 WPM."})

    if best_acc >= 95:
        unlocked.append({"id": "accuracy_95", "title": "Precision", "detail": "Reach 95% accuracy."})
    if total_minutes >= 60:
        unlocked.append({"id": "one_hour", "title": "One Hour Club", "detail": "Accumulate 60+ minutes."})

    return unlocked


def _print_achievements(as_json: bool = False) -> None:
    """Print unlocked achievements for game-like progression."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    db.close()

    unlocked = _compute_achievements(sessions)
    payload = {
        "total_sessions": len(sessions),
        "unlocked": unlocked,
    }

    if as_json:
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  achievements")
    c.print()

    if not unlocked:
        c.print("  [dim]No achievements yet. Complete your first run to unlock one.[/dim]")
        c.print()
        return

    c.print(f"  [bold]Unlocked[/bold]   {len(unlocked)}")
    c.print(f"  [bold]Sessions[/bold]   {len(sessions)}")
    c.print()
    for item in unlocked:
        c.print(f"  • [bold]{item['title']}[/bold] — {item['detail']}")
    c.print()

def _daily_challenge_spec(day: object | None = None) -> dict:
    """Return a deterministic daily challenge configuration."""
    from datetime import date

    today = day if day is not None else date.today()
    if not hasattr(today, "toordinal"):
        today = date.today()

    categories = ["words", "sentences", "quotes", "code", "numbers"]
    lengths = [25, 50, 100]

    ordv = today.toordinal()
    category = categories[ordv % len(categories)]
    words = lengths[ordv % len(lengths)]
    challenge_id = f"{today.isoformat()}:{category}:{words}"

    return {
        "date": today.isoformat(),
        "challenge_id": challenge_id,
        "category": category,
        "words": words,
    }


def _print_daily_challenge(as_json: bool = False) -> None:
    """Print today's challenge card and launch command."""
    from rich.console import Console
    from key4ce.themes.themes import DEFAULT_THEME

    spec = _daily_challenge_spec()
    command = f"python -m key4ce --mode {spec['category']} --words {spec['words']}"

    if as_json:
        payload = dict(spec)
        payload["command"] = command
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  daily challenge")
    c.print()
    c.print(f"  [bold]Date[/bold]        {spec['date']}")
    c.print(f"  [bold]Challenge ID[/bold] {spec['challenge_id']}")
    c.print(f"  [bold]Mode[/bold]        {spec['category']}")
    c.print(f"  [bold]Target[/bold]      {spec['words']} words")
    c.print()
    c.print("  [bold]Play now[/bold]")
    c.print(f"  {command}")
    c.print()

def _build_leaderboard(records: list, limit: int = 10, source: str | None = None) -> list[dict]:
    """Build a compact leaderboard from session records."""
    rows = records
    if source:
        wanted = str(source).strip().lower()
        rows = [r for r in rows if str(r.source).lower() == wanted]

    ranked = sorted(rows, key=lambda r: (float(r.wpm), float(r.accuracy), float(r.chars_typed)), reverse=True)
    out = []
    for i, r in enumerate(ranked[: max(1, int(limit))], start=1):
        out.append(
            {
                "rank": i,
                "id": r.id,
                "source": r.source,
                "wpm": round(float(r.wpm), 1),
                "accuracy": round(float(r.accuracy), 1),
                "duration": round(float(r.duration), 1),
            }
        )
    return out


def _print_leaderboard(limit: int = 10, source: str | None = None, as_json: bool = False) -> None:
    """Print a terminal leaderboard for local score-chasing."""
    from rich.console import Console
    from rich.table import Table
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    db = Database()
    db.connect()
    sessions = db.list_sessions()
    db.close()

    rows = _build_leaderboard(sessions, limit=limit, source=source)

    payload = {"limit": max(1, int(limit)), "source": source, "rows": rows}
    if as_json:
        print(json.dumps(payload, indent=2))
        return

    t = DEFAULT_THEME
    c = Console()
    c.print()
    title = "leaderboard" if not source else f"leaderboard ({source})"
    c.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  {title}")
    c.print()

    if not rows:
        c.print("  [dim]No matching sessions yet. Run a session to post a score.[/dim]")
        c.print()
        return

    table = Table("Rank", "Source", "WPM", "Accuracy", "Duration", border_style=t.dim, header_style=f"bold {t.secondary}")
    for row in rows:
        mins, secs = divmod(int(row["duration"]), 60)
        table.add_row(
            f"#{row['rank']}",
            row["source"],
            f"{row['wpm']:.1f}",
            f"{row['accuracy']:.1f}%",
            f"{mins}:{secs:02d}",
        )
    c.print(table)
    c.print()

def _sessions_to_jsonable(records: list) -> list[dict]:
    """Convert session records to serialisable dicts."""
    return [
        {
            "id": s.id,
            "ts": s.ts,
            "source": s.source,
            "wpm": s.wpm,
            "accuracy": s.accuracy,
            "duration": s.duration,
            "chars_typed": s.chars_typed,
            "errors": s.errors,
            "timings": s.timings,
        }
        for s in records
    ]


def _print_export_json(limit: int | None = None) -> None:
    """Export session history as JSON for backup/portability."""
    from key4ce.data.db import Database

    db = Database()
    db.connect()
    sessions = db.list_sessions(limit=limit)
    db.close()

    output = {
        "exported_at": __import__("datetime").datetime.now().isoformat(),
        "count": len(sessions),
        "sessions": _sessions_to_jsonable(sessions),
    }
    print(json.dumps(output, indent=2))



def _import_sessions_from_file(path: str) -> int:
    """Import sessions from an export JSON file and return inserted count."""
    from key4ce.data.db import Database

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sessions = data.get("sessions", []) if isinstance(data, dict) else []
    if not isinstance(sessions, list):
        sessions = []

    db = Database()
    db.connect()
    inserted = db.import_sessions(sessions)
    db.close()
    return inserted


def _print_stats() -> None:
    """Print a stats summary table directly to stdout (no TUI)."""
    from rich.console import Console
    from rich.table import Table
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    t = DEFAULT_THEME
    db = Database()
    db.connect()
    stats = db.get_stats()
    db.close()

    console = Console()

    if stats.total_sessions == 0:
        console.print("[dim]No sessions recorded yet. Run key4ce and start typing![/dim]")
        return

    console.print()
    console.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  stats", style="")
    console.print()
    console.print(f"  [bold]Best WPM[/bold]       {stats.best_wpm:.1f}")
    console.print(f"  [bold]Average WPM[/bold]    {stats.avg_wpm:.1f}")
    console.print(f"  [bold]Avg Accuracy[/bold]   {stats.avg_accuracy:.1f}%")
    console.print(f"  [bold]Sessions[/bold]       {stats.total_sessions}")
    console.print()

    if not stats.recent_sessions:
        return

    table = Table(
        "Date", "Source", "WPM", "Accuracy", "Duration",
        border_style=t.dim,
        header_style=f"bold {t.secondary}",
        show_edge=True,
    )

    for s in stats.recent_sessions:
        date_str = s.ts[:10]
        mins, secs = divmod(int(s.duration), 60)
        table.add_row(
            date_str,
            s.source,
            f"{s.wpm:.1f}",
            f"{s.accuracy:.1f}%",
            f"{mins}:{secs:02d}",
        )

    console.print(table)
    console.print()


def _print_stats_json() -> None:
    from key4ce.data.db import Database

    db = Database()
    db.connect()
    stats = db.get_stats()
    db.close()
    output = {
        "total_sessions": stats.total_sessions,
        "best_wpm": stats.best_wpm,
        "avg_wpm": stats.avg_wpm,
        "avg_accuracy": stats.avg_accuracy,
        "recent": _sessions_to_jsonable(stats.recent_sessions),
    }
    print(json.dumps(output, indent=2))


def _print_weekly_summary(days: int = 7, as_json: bool = False) -> None:
    """Print progress summary over the recent window."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    t = DEFAULT_THEME
    db = Database()
    db.connect()
    all_sessions = db.list_sessions()
    db.close()

    summary = _summarize_recent_sessions(all_sessions, days=days)

    if as_json:
        print(json.dumps(summary, indent=2))
        return

    console = Console()
    console.print()
    console.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  {days}-day summary")
    console.print()
    if summary["sessions"] == 0:
        console.print("  [dim]No sessions in this period yet.[/dim]")
        console.print()
        return

    console.print(f"  [bold]Sessions[/bold]       {summary['sessions']}")
    console.print(f"  [bold]Average WPM[/bold]    {summary['avg_wpm']:.1f}")
    console.print(f"  [bold]Avg Accuracy[/bold]   {summary['avg_accuracy']:.1f}%")
    console.print(f"  [bold]Best WPM[/bold]       {summary['best_wpm']:.1f}")
    console.print(f"  [bold]Practice Time[/bold]  {summary['total_minutes']:.1f} min")
    console.print(f"  [bold]Current Streak[/bold] {summary['current_streak_days']} day(s)")
    console.print(f"  [bold]Longest Streak[/bold] {summary['longest_streak_days']} day(s)")
    console.print()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="key4ce",
        description="A terminal typing trainer that actually makes you better.",
    )

    sub = parser.add_subparsers(dest="command")

    stats_cmd = sub.add_parser("stats", help="Print session stats and exit (no TUI)")
    stats_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    weekly_cmd = sub.add_parser("weekly", help="Print recent progress summary and exit")
    weekly_cmd.add_argument("--days", type=int, default=7, metavar="N", help="Window size in days (default: 7)")
    weekly_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    export_cmd = sub.add_parser("export", help="Export session history as JSON")
    export_cmd.add_argument("--limit", type=int, default=None, metavar="N", help="Optional max number of sessions to export")

    import_cmd = sub.add_parser("import", help="Import session history from exported JSON")
    import_cmd.add_argument("path", help="Path to exported JSON file")

    goals_cmd = sub.add_parser("goals", help="Show or set daily practice goals")
    goals_cmd.add_argument("--set-minutes", type=int, default=None, metavar="N", help="Set daily minutes goal")
    goals_cmd.add_argument("--set-sessions", type=int, default=None, metavar="N", help="Set daily sessions goal")
    goals_cmd.add_argument("--json", action="store_true", help="Output as JSON")
    goals_cmd.add_argument("--preset", choices=sorted(GOAL_TEMPLATES.keys()), default=None, help="Apply a built-in goals preset")

    brag_cmd = sub.add_parser("brag", help="Print a shareable progress card")
    brag_cmd.add_argument("--days", type=int, default=7, metavar="N", help="Window size in days (default: 7)")

    drops_cmd = sub.add_parser("drops", help="Show biggest pace drops in latest session")
    drops_cmd.add_argument("--top", type=int, default=5, metavar="N", help="How many slow positions to show")
    drops_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    leaderboard_cmd = sub.add_parser("leaderboard", help="Show local top runs")
    leaderboard_cmd.add_argument("--limit", type=int, default=10, metavar="N", help="Number of top runs to show")
    leaderboard_cmd.add_argument("--source", default=None, help="Optional source filter (e.g. sentences)")
    leaderboard_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    challenge_cmd = sub.add_parser("challenge", help="Show today's daily challenge")
    challenge_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    achievements_cmd = sub.add_parser("achievements", help="Show unlocked milestone badges")
    achievements_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    coach_cmd = sub.add_parser("coach", help="Show adaptive coaching plan")
    coach_cmd.add_argument("--days", type=int, default=7, metavar="N", help="Window size in days")
    coach_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    profile_cmd = sub.add_parser("profile", help="Show or set local profile preferences")
    profile_cmd.add_argument("--mode", default=None, help="Preferred mode (sentences, words, code, etc.)")
    profile_cmd.add_argument("--words", type=int, default=None, metavar="N", help="Preferred word target")
    profile_cmd.add_argument("--theme", default=None, help="Preferred theme name")
    profile_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    providers_cmd = sub.add_parser("providers", help="Show content provider reliability snapshot")
    providers_cmd.add_argument("--days", type=int, default=30, metavar="N", help="Window size in days")
    providers_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    parser.add_argument(
        "--theme",
        metavar="NAME",
        default=None,
        help="Colour theme: cyberpunk (default), nord, dracula, monokai, minimal",
    )
    parser.add_argument(
        "--zen",
        action="store_true",
        help="Zen mode — no stats during typing, stats shown only at end",
    )
    parser.add_argument(
        "--focus",
        action="store_true",
        help="Focus mode — generates text targeting your weak spots from recent sessions",
    )
    parser.add_argument(
        "--mode",
        metavar="CATEGORY",
        default=None,
        help="Skip menu and go straight to a session: words, sentences, quotes, code, numbers, wikipedia, quote",
    )
    parser.add_argument(
        "--words",
        type=int,
        default=50,
        metavar="N",
        help="Approximate word count for --mode / --focus sessions (default: 50)",
    )

    args = parser.parse_args()

    if args.command == "stats":
        if args.json:
            _print_stats_json()
        else:
            _print_stats()
        return

    if args.command == "weekly":
        days = max(1, int(args.days))
        _print_weekly_summary(days=days, as_json=args.json)
        return

    if args.command == "export":
        limit = None if args.limit is None else max(1, int(args.limit))
        _print_export_json(limit=limit)
        return

    if args.command == "import":
        inserted = _import_sessions_from_file(args.path)
        print(f"Imported {inserted} session(s).")
        return

    if args.command == "goals":
        if args.preset is not None:
            _apply_goal_template(args.preset)
        if args.set_minutes is not None or args.set_sessions is not None:
            _set_goals(args.set_minutes, args.set_sessions)
        _print_goals_status(as_json=args.json)
        return

    if args.command == "brag":
        _print_brag(days=max(1, int(args.days)))
        return

    if args.command == "drops":
        _print_speed_drops(top=max(1, int(args.top)), as_json=args.json)
        return

    if args.command == "leaderboard":
        _print_leaderboard(limit=max(1, int(args.limit)), source=args.source, as_json=args.json)
        return

    if args.command == "challenge":
        _print_daily_challenge(as_json=args.json)
        return

    if args.command == "achievements":
        _print_achievements(as_json=args.json)
        return

    if args.command == "coach":
        _print_coach(days=max(1, int(args.days)), as_json=args.json)
        return

    if args.command == "profile":
        if args.mode is not None or args.words is not None or args.theme is not None:
            _set_profile(args.mode, args.words, args.theme)
        _print_profile(as_json=args.json)
        return

    if args.command == "providers":
        _print_provider_health(days=max(1, int(args.days)), as_json=args.json)
        return

    from key4ce.themes.themes import get_theme, DEFAULT_THEME
    from key4ce.ui.app import App

    theme = get_theme(args.theme) if args.theme else DEFAULT_THEME

    skip_to: str | None = None
    if args.focus:
        skip_to = "focus"
    elif args.mode:
        skip_to = args.mode

    app = App(
        theme=theme,
        zen_mode=args.zen,
        skip_to_category=skip_to,
        word_target=args.words,
    )
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
