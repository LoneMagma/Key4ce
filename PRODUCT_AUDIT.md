# Key4ce Product Audit & Full-Product Roadmap

## 1) What the current project is about

Key4ce is a terminal-first typing trainer/game that aims to blend clean UX, performance analytics, and configurable content sources.

At a high level, the repository currently contains **two parallel app implementations**:

- A **newer Rich/readchar stack** launched from the CLI (`key4ce.ui.app.App`).
- A **Textual screen-based stack** (`key4ce.app.Key4ceApp` and `key4ce.ui.screens.*_screen`) that appears partially integrated and partially stale.

This split strongly suggests an active transition in architecture, not a single stable product surface.

## 2) What it already does well

- Clear product intent and positioning in README (typing trainer with analytics and configurable content).
- Solid core domain concepts exist:
  - typing engine
  - keystroke timeline recording
  - post-session analysis
  - local SQLite persistence
  - builtin + external content fetching with cache/fallback
- CLI surface already supports practical modes (`stats`, `--mode`, `--focus`, `--zen`).

## 3) What it currently lacks (product gaps)

### A. Single coherent architecture and public API

The codebase has mismatches between modules/tests/UI layers:

- Tests expect objects that are not present in current engine/content modules.
- UI code references APIs that differ across implementations.
- Two app shells coexist, which increases maintenance cost and user confusion.

**Impact:** slows development, breaks confidence, and makes releases risky.

### B. Reliability baseline (tests are not passing)

Current test collection fails due to import/API drift.

**Impact:** shipping regressions are likely; contributors cannot trust CI.

### C. Packaging/dependency consistency

The project imports Textual in parts of the codebase, but runtime dependencies list only `rich` and `readchar`.

**Impact:** installation/runtime behavior depends on which path users execute; this is fragile.

### D. Product completeness for end users

Key user-facing capabilities are partial/uneven:

- Stats/analysis views differ between implementations.
- Many “full product” elements are still conceptual (roadmap/design doc vs robust shipped behavior).
- No explicit onboarding funnel, habit loop, or progression economy at product level.

### E. Delivery & operational maturity

Missing or unclear for production-readiness:

- No explicit release train with quality gates tied to passing tests.
- No clear telemetry/usage instrumentation strategy.
- No explicit support/documentation lifecycle for external providers and failure modes.

## 4) How to become a full-fledged product (practical roadmap)

## Phase 0 (1–2 weeks): Stabilize foundation

1. **Pick one UI architecture** as canonical (Rich/readchar _or_ Textual).
2. **Deprecate/remove the other path** or isolate behind feature flags with clear status.
3. **Reconcile API contracts** across engine, analyzer, content providers, and tests.
4. **Make test suite green** and enforce in CI.
5. **Align `pyproject.toml` dependencies** with actual runtime imports.

**Exit criteria:** `pip install -e .` + `pytest` works cleanly for fresh clones.

## Phase 1 (2–4 weeks): Ship cohesive core experience

1. **Session loop polish:** start → type → results → retry/menu flow consistency.
2. **Unified stats model:** one canonical metrics schema (WPM, accuracy, consistency, errors, combos).
3. **Progressive onboarding:** first-run tutorial + initial baseline test.
4. **Content UX:** transparent source selection, difficulty scaling, and offline fallback messaging.
5. **Data durability:** migration-safe DB schema versioning and import/export of user profile.

**Exit criteria:** one polished “daily use” loop with predictable behavior.

## Phase 2 (4–8 weeks): Product differentiation

1. **Adaptive coaching:** use error pairs/digraph speed data to auto-generate targeted drills.
2. **Goals & streak system:** daily target, streak calendar, weekly summary.
3. **Replay/insights:** session timeline replay + pinpoint “where speed drops.”
4. **Personalization:** per-user themes/modes and goal templates.
5. **Social-lite features:** shareable result card and optional leaderboard challenge mode.

**Exit criteria:** meaningful retention hooks beyond one-off typing tests.

## Phase 3 (ongoing): Scale and monetizable readiness

1. **Plugin/provider framework** for text sources with reliability scoring.
2. **Cross-device profile sync** (optional account) while preserving offline-first mode.
3. **Team/education mode:** assignments, class dashboards, progress reports.
4. **Product analytics pipeline** (privacy-aware) for activation/retention optimization.
5. **Pricing packaging (if desired):** free core + premium insights/challenges/themes.

## 5) Priority matrix (Do Now / Next / Later)

### Do now
- Resolve architecture split and API drift.
- Restore tests and CI as non-negotiable gate.
- Fix packaging dependencies.

### Next
- Cohesive onboarding + consistent stats/results loop.
- Better content source UX and reliability communication.

### Later
- Adaptive coaching depth, social features, sync/team tooling.

## 6) Suggested product KPIs

- **Activation:** % users completing first full session.
- **Retention:** D1, D7, D30 returning typists.
- **Habit health:** sessions/user/week, median session length.
- **Skill outcome:** median WPM and accuracy improvements over 4 weeks.
- **Reliability:** crash-free sessions %, external source success rate.

## 7) Bottom line

Key4ce already has the ingredients of a strong typing product, but it is currently in a **transition state**. To become full-fledged, it must first become **internally coherent and reliable** (single architecture, passing tests, aligned dependencies), then layer product-grade retention and coaching features on top.
