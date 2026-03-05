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

Windows one-command setup:

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
python -m key4ce providers --days 30
python -m key4ce export --limit 200 > sessions.json
python -m key4ce import sessions.json
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

### Upcoming Work (Phase 3 focus)

1. Complete architecture unification and dependency/runtime cleanup.
2. Expand provider reliability from baseline scoring to full plugin/provider contracts.
3. Add optional profile sync strategy while preserving offline-first operation.
4. Add team/education reporting surfaces.

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
```

## Contributing

Contributions are welcome. Keep changes focused, test-backed, and documented.

## License

MIT. See `LICENSE`.
