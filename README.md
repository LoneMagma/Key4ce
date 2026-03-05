# Key4ce

Key4ce is a terminal typing trainer focused on measurable improvement through structured practice, local-first progress tracking, and post-session feedback.

## Current Product State

Key4ce is functional and usable today as a beta terminal application.

Implemented capabilities:

- Real-time typing sessions with terminal UI flow.
- Session persistence in local SQLite storage.
- Session analytics: WPM, accuracy, errors, streak-oriented summaries.
- CLI reporting commands for weekly summaries, goals, exports/imports, brag cards, and pace-drop insights.
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
python -m key4ce export --limit 200 > sessions.json
python -m key4ce import sessions.json
```

## Data Locations

Key4ce stores local files in:

- `~/.key4ce/sessions.db`
- `~/.key4ce/goals.json`

## Roadmap Phases

The roadmap source of truth is `PRODUCT_AUDIT.md`.

### Completed / In Progress

- Phase 0 (foundation): largely completed in practical terms for local usage (test suite passing, core CLI features available), but architecture consolidation remains open.
- Phase 1 (cohesive core loop): partially completed through improved results flow, analytics visibility, and data portability.
- Phase 2 (product differentiation): actively in progress with goals, streak summaries, social-lite brag output, and pace-drop insights.

### Upcoming Work

1. Complete architecture unification and dependency/runtime cleanup.
2. Expand adaptive coaching depth beyond current hints.
3. Add stronger personalization defaults and progression templates.
4. Move toward Phase 3 features: plugin/provider reliability, optional sync strategy, and team/education support.

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
```

## Contributing

Contributions are welcome. Keep changes focused, test-backed, and documented.

## License

MIT. See `LICENSE`.
