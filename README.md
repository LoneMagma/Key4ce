# Key4ce

Key4ce is a terminal typing trainer focused on measurable improvement through structured practice, local-first progress tracking, and post-session feedback.

## Current Product State

Key4ce is functional and usable today as a beta terminal application.

Implemented capabilities:

- Real-time typing sessions with terminal UI flow.
- Session persistence in local SQLite storage.
- Session analytics: WPM, accuracy, errors, streak-oriented summaries.
- CLI reporting commands for weekly summaries, goals, exports/imports, brag cards, pace-drop insights, leaderboard, challenge, achievements, coaching, and profile preferences.
- Focus-oriented drill hooks powered by error and timing data.

## Universal Start Command

From a fresh clone, the simplest start command is:

```bash
python start.py
```

This launches the app through a repository-local entrypoint and avoids requiring users to remember module paths.

If dependencies are not installed yet:

```bash
pip install -e .
python start.py
```

## Installation

```bash
git clone https://github.com/LoneMagma/Key4ce.git
cd Key4ce
pip install -e .
```

Optional development dependencies:

```bash
pip install -e ".[dev]"
```

Universal one-command setup (Linux/macOS/Windows with Python 3.11+):

```bash
python install.py
```

Windows PowerShell setup (native):

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

## Usage

Primary launch methods:

```bash
python start.py
key4ce
python -m key4ce
```

Selected CLI commands:

```bash
python -m key4ce stats
python -m key4ce weekly --days 14
python -m key4ce goals --preset steady
python -m key4ce brag --days 7
python -m key4ce drops --top 5
python -m key4ce leaderboard --limit 10
python -m key4ce challenge
python -m key4ce achievements
python -m key4ce coach --days 7
python -m key4ce profile --mode sentences --words 50 --theme cyberpunk
python -m key4ce providers --days 30  # includes external availability checks
python -m key4ce report --days 7
python -m key4ce assign --days 7
python -m key4ce kpi --days 30
python -m key4ce sync-plan --target key4ce-snapshot.json
python -m key4ce sync key4ce-snapshot.json --mode safe
python -m key4ce class-report class/*.json
python -m key4ce telemetry --days 30 --out key4ce-telemetry.json
python -m key4ce export --limit 200 > sessions.json
python -m key4ce import sessions.json
python -m key4ce snapshot > key4ce-snapshot.json
python -m key4ce restore key4ce-snapshot.json
```

## Data Locations

Key4ce stores local files in:

- `~/.key4ce/sessions.db`
- `~/.key4ce/goals.json`
- `~/.key4ce/profile.json`

## Roadmap Phases

The roadmap source of truth is `PRODUCT_AUDIT.md`.

### Completed / In Progress

- Phase 0 (foundation): completed for day-to-day local usage; architecture cleanup remains as technical debt.
- Phase 1 (cohesive core loop): completed baseline (session flow, stats, persistence, import/export).
- Phase 2 (product differentiation): completed baseline with adaptive coaching command, goals/streak workflows, pace-drop insights, daily challenge, leaderboard, and achievements.

### Phase 3 Status

Phase 3 is in active baseline completion. Current delivered blocks:

1. Provider/plugin reliability snapshot (`providers`) with plugin row support from local config.
2. Cross-device sync baseline with dry-run (`sync-plan`) and apply mode (`sync --mode safe|force`) using snapshot files.
3. Team/education baseline with assignment planning (`assign`) and aggregated class snapshots (`class-report`).
4. Privacy-aware analytics baseline via KPI (`kpi`) and aggregate telemetry export (`telemetry`).

Remaining phase-3 hardening work:

- Formal plugin contracts + validation hooks.
- Optional hosted sync transport (current sync is file-based, offline-first).
- Expanded class dashboard surfaces beyond CLI reports.

## Development

Run tests:

```bash
pytest -q
```

Recommended quick checks:

```bash
python -m key4ce weekly --json
python -m key4ce goals --json
python -m key4ce drops --json
python -m key4ce coach --json
python -m key4ce achievements --json
python -m key4ce providers --json
python -m key4ce report --json
python -m key4ce assign --json
python -m key4ce kpi --json
python -m key4ce sync-plan --json
python -m key4ce telemetry --days 30
```

## Contributing

Contributions are welcome. Keep changes focused, test-backed, and documented.

## License

MIT. See `LICENSE`.
