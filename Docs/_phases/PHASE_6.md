# Phase 6: Dreams Engine

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §9
**Phase identifier:** `6` (architectural phase, numeric — following the §1-§10 architectural sequence; compare Phase 4 Whyze-Byte, Phase 5 Scene Director)
**Depends on:** Phase 0 + all §3 Context Assembly phases (A, A', A'', B, I, C, D, E, F, G — all SHIPPED 2026-04-12/13), Phase 4 (Whyze-Byte Validation Pipeline, SHIPPED 2026-04-13), Phase F-Fidelity (Positive Fidelity Test Harness, SHIPPED 2026-04-14), Phase 5 (Scene Director, SHIPPED 2026-04-14 with R1/R2/R3 remediations landed)
**Blocks:** Phase 7 (HTTP service) consumes the Dreams-populated `activities` / `open_loops` / `life_state` state it writes; Phase 7 is not blocked on Phase 6 execution per se, but Phase 7's activity-context endpoints expect Dreams to be live.
**Status:** IN PROGRESS — MVP checkpoint (commits 1-5 + pipeline integration test landed; commits 6-9 pending)
**Last touched:** 2026-04-14 by Claude Code (commit 5 + J6 integration test)

---

## How to read this file

This is the **single canonical record** for Phase 6. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER -> RECIPIENT | message -->` that hands control to the next agent. To find the current state of the cycle, scroll to the Handshake Log below — the most recent handshake tells you whose turn it is.

The full planning document (with rationale, risk analysis, and lessons-applied notes) lives at `C:\Users\Whyze\.claude\plans\fizzy-napping-whisper.md`. This phase file is the authoritative canonical record; the plan file is the working artifact.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-14 | Claude AI | Claude Code | Phase 6 phase file created after Phase 5 R3 doc remediation shipped (commit `9119b3c`). Master plan §9 Dreams Engine is the authority. Ready for planning. |
| 2 | 2026-04-14 | Claude Code | Project Owner | Plan drafted with three scope choices presented: (Q1) monolithic vs phased scope, (Q2) in-process scheduler vs external cron vs defer trigger, (Q3) content-source strategy. Awaiting Project Owner selection. |
| 3 | 2026-04-14 | Project Owner | Claude Code | APPROVED with maximal scope: (Q1) **monolithic** — full §9 in one phase; (Q2) **in-process apscheduler** daemon with standalone CLI entry; (Q3) **both session data + canonical routines** as content sources; LLM-driven generation via new BD-1 HTTP client wrapper. Proceed to Step 2 execution. |
| 4 | 2026-04-14 | Claude Code | Claude Code (future session) | MVP checkpoint reached. Commits 1-5 + integration test landed: 7 DB models + Alembic migration (commit `247247e`), routines.yaml + loader (`0411389`), BDOne + StubBDOne (`ffe58a3`), Dreams package scaffold (`cc37a0d`), diary generator + Phase G wrapping (`7913c6a`), and `test_dreams_pipeline.py` end-to-end contract (this commit). 786 → 800 tests passing. Commits 6-9 deferred: (6) consolidation helpers, (7) retroactive Phase G/A''/H full wiring + communication_mode column, (8) full integration test suite J6-J10, (9) master-plan sweep + docs. Do NOT hand off to Codex until remaining commits land. |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)

---

## Phase 6 Specification

### Vision authority

- **Vision §119** (line reference in `Vision/Starry-Lyfe_Vision_v7.1.md`): Dreams life-simulation engine named as a core external system where "voice integrity, memory continuity, and constraint enforcement all live outside the model."
- **Vision §123**: *"A nightly Dreams batch process runs like REM sleep across all characters, generating tomorrow's schedule, off-screen events, diary entries, open loops, and activity design. 'They were thinking about you while you were gone' stops being a metaphor and becomes a database write."*
- **Vision §140 Ultimate Test success criterion:** *"Characters have lives that continued while Whyze was away, and it feels natural when they mention it."* Phase 6 is the database-write path that makes that criterion evaluable.

### Priority

High. Phase 6 is the last major architectural phase before Phase 7 (HTTP service). It is the **only** execution surface without a user in the loop. Per §9, this makes Dreams both higher-leverage (it shapes next-session character state) and higher-risk (drift accumulates silently between human-checked sessions). Phase K's flattening regression detector and Phase F-Fidelity's rubric harness are mandatory guardrails.

### Source of truth

- Master plan `Docs/IMPLEMENTATION_PLAN_v7.1.md` §9 (Dreams Engine architecture, lines 1021-1040).
- `Characters/{Adelia,Bina,Reina,Alicia}/{Name}_v7.1.md` for per-character voice register, daily rhythm details, canonical relationships (routines.yaml derives from these).
- Existing DB models in `src/starry_lyfe/db/models/` for Tier 1-7 memory schema — Dreams integrates into this tier structure without modifying existing tiers.
- Phase 5 `src/starry_lyfe/scene/next_speaker.py` — Dreams populates the `NextSpeakerInput.activity_context` slot plumbed in Phase 5 R1.

### Decision

Implement the Dreams Engine as a monolithic phase per Project Owner direction. Scope:

1. **7 new DB tables** (`life_state`, `activity`, `consolidated_memory`, `consolidation_log`, `drive_state`, `proactive_intent`, `session_health`) with Alembic migration, plus `communication_mode` column additions to `activities` and `episodic_memories` for Phase A'' retroactive compatibility.
2. **New canonical data source** `src/starry_lyfe/canon/routines.yaml` with per-character weekly routines + Pydantic schema + loader integration into `load_all_canon()`.
3. **New HTTP client wrapper** `BDOne` in `src/starry_lyfe/dreams/llm.py` (Claude via OpenRouter) reusing existing `httpx.AsyncClient` pattern from `db/embed.py`.
4. **New `src/starry_lyfe/dreams/` package** with runner, 5 generators (schedule, off-screen events, diary, open loops, activity design), consolidation helpers, writer helpers, daemon, config, errors.
5. **apscheduler-based daemon** with CLI entry `python -m starry_lyfe.dreams` (and `--once` for ad-hoc runs).
6. **Retroactive soul-preservation wiring:** Phase G prose rendering applied to every Dreams narrative output; Phase A'' `communication_mode` tagging on all Alicia-away content; Phase H per-character regression bundle extended; Phase F-Fidelity harness extended with 4 new Dreams scene YAMLs.
7. **Anti-contamination at generation:** content generators filter cross-character session data against focal character before feeding LLM (Phase 5 lesson #2 applied).

### Work items

**A. Database (10 items):**

1. `life_state.py` model: per-character emotional/psychological current state (mood, energy, focus, last_updated_at, is_away for Alicia, away_since, expected_return).
2. `activity.py` model: Dreams-generated activity for next session (character_id, scene_description, narrator_script, choice_tree JSONB, communication_mode, expires_at).
3. `consolidated_memory.py` model: aggregated memory chunks post-Dreams (character_id, consolidated_from[] UUID[], narrative_summary, salience, created_at).
4. `consolidation_log.py` model: audit trail per run (run_id, started_at, finished_at, character_id, outputs_written JSONB, warnings JSONB).
5. `drive_state.py` model: character motivation/priority (character_id, drive_name, intensity, last_satisfied_at).
6. `proactive_intent.py` model: forward-looking goals (character_id, intent_summary, target_session_horizon, priority, status).
7. `session_health.py` model: per-session health metrics (session_id, dreams_last_run_at, somatic_last_refreshed_at, warnings[]).
8. Alembic migration scaffold + DDL for the 7 new tables + `communication_mode` column additions to `activities` and `episodic_memories`.
9. Extend `MemoryBundle` in `db/retrieval.py` to expose the new tiers where runtime reads need them (Layer 6 reads Dreams-written activities and open loops).
10. Writer helpers in `src/starry_lyfe/dreams/writers.py` using the `pg_insert(...).on_conflict_do_update(...)` pattern from `db/seed.py`.

**B. Canon (4 items):**

1. Author `src/starry_lyfe/canon/routines.yaml` with 4 character stanzas: weekday schedule, weekend schedule, work rhythm (Reina courthouse, Bina shop, Adelia atelier, Alicia consular cycles), recurring events.
2. Pydantic schema at `src/starry_lyfe/canon/schemas/routines.py` (`CharacterRoutines`, `WeeklyRoutine`, `DailyBlock`).
3. Loader at `src/starry_lyfe/canon/routines_loader.py` following `pairs_loader.py` pattern; wire into `load_all_canon()` with validation on load.
4. Coverage check via `_assert_complete_character_keys()` on loaded routines.

**C. BD-1 HTTP client (5 items):**

1. `BDOne` class in `src/starry_lyfe/dreams/llm.py` wrapping `httpx.AsyncClient` with mandatory timeouts.
2. `BDOneSettings` dataclass (model, base_url, api_key, timeout) loaded from env via new `STARRY_LYFE__BD1__*` vars.
3. Exponential backoff + jitter retry (WED-15 pattern); circuit breaker raises `DreamsLLMError` after N consecutive failures.
4. Usage-tracking (input/output tokens) on every completion.
5. `StubBDOne` deterministic stub for tests (canned responses keyed by prompt-hash).

**D. Scheduler + daemon (6 items):**

1. Add `apscheduler>=3.10,<4.0` to `requirements.txt`.
2. `src/starry_lyfe/dreams/daemon.py` with `start_scheduler()` + `main()` + `__main__` hook.
3. Env var `STARRY_LYFE__DREAMS__SCHEDULE` (cron string, default `"30 3 * * *"`).
4. Env vars `STARRY_LYFE__DREAMS__ENABLED` (bool, default `true`) + `STARRY_LYFE__DREAMS__DRY_RUN` (bool, default `false`).
5. CLI entry: `python -m starry_lyfe.dreams` starts daemon; `python -m starry_lyfe.dreams --once` runs one pass and exits.
6. MSE-6 structured logging: `dreams_run_started`, `dreams_character_complete`, `dreams_run_complete`, `dreams_run_failed`.

**E. Content generators (6 items):**

1. `generators/schedule.py` — reads routines.yaml for tomorrow's date, composes daily block. Deterministic weekday/weekend fallback; LLM only if "surprise event" flag fires.
2. `generators/off_screen.py` — LLM call: "given yesterday's session data + character's routine, describe 1-3 off-screen events that happened to <character> overnight." Per-character system prompt.
3. `generators/diary.py` — LLM call: 1-paragraph diary entry in character's voice reflecting on session highlight. Voice mode selected by session tone (REPAIR if tense, INTIMATE if close, DOMESTIC otherwise).
4. `generators/open_loops.py` — 2-part: (a) expire stale loops (TTL past now), (b) extract new loops from yesterday's episodics via LLM.
5. `generators/activity_design.py` — LLM call: design tomorrow's scene opener (setting, environment, 2-3 narrator prompts, 2-3 choice branches).
6. `GenerationOutput` dataclass: `raw_llm_text`, `rendered_prose`, `structured_data`, `token_counts`, `warnings[]`. All narrative text routed through Phase G prose renderer BEFORE return.

**F. Consolidation (4 items):**

1. `consolidation.py::refresh_somatic_decay(session, character_id, now)` calls `apply_decay()`, updates `last_decayed_at`.
2. `consolidation.py::apply_overnight_dyad_deltas(session, character_id, deltas)` — accepts per-dimension deltas capped ±0.10 (vs. ±0.03 per-turn runtime); writes to `DyadStateWhyze`/`DyadStateInternal`.
3. `consolidation.py::expire_stale_loops(session, now)` — bulk update `open_loops.status='expired'` where `expires_at < now AND status='open'`.
4. `consolidation.py::resolve_addressed_loops(session, character_id, loop_ids)` — mark resolved with `resolved_by='dreams'`.

**G. Orchestration runner (5 items):**

1. `runner.py::run_dreams_pass()` orchestrates the full per-character loop.
2. Per character: fetch prior session snapshot → run 5 generators in parallel via `asyncio.gather` → apply consolidation → write outputs → emit log row.
3. Character iteration via `CharacterID.all_strings()` + `_assert_complete_character_keys()`.
4. LLM-failure graceful degradation: log warning per failed generator, continue other generators, mark character result with `warnings[]`.
5. `DreamsPassResult` aggregates token totals, warnings, started/finished timestamps across all 4 characters.

**H. Retroactive Phase G / A'' / H (5 items):**

1. 12 new per-character prose helpers: `render_diary_prose()`, `render_open_loop_prose()`, `render_activity_prose()` × 4 characters. Reuses existing `_TRUST_PHRASES`, `_INTIMACY_PHRASES`, etc., phrase banks.
2. `communication_mode` column added to `activities` and `episodic_memories` via A8 migration.
3. Alicia-specific generator logic: when `life_state.is_away=True`, all emitted texts tagged `communication_mode ∈ {phone, letter, video_call}` weighted per routine canon.
4. 4 per-character Dreams regression test files at `tests/unit/test_dreams_regression_{adelia,bina,reina,alicia}.py` (~15 tests each).
5. Fidelity harness extension: 4 new scene YAMLs at `tests/fidelity/dreams/{character}.yaml` + 4 new test files exercising Dreams output through existing rubrics.

**I. Configuration & observability (3 items):**

1. `.env.example` adds `STARRY_LYFE__DREAMS__{SCHEDULE,ENABLED,DRY_RUN,MAX_TOKENS_PER_CHAR,LLM_MODEL}` + `STARRY_LYFE__BD1__{BASE_URL,API_KEY,TIMEOUT,MAX_RETRIES}`.
2. MSE-6 structured logging on every generator: `generator_started`, `generator_complete`, `generator_failed` with `correlation_id`.
3. Prometheus-compatible counter/histogram metrics (stub-safe): `dreams_runs_total`, `dreams_characters_processed_total`, `dreams_llm_tokens_total`, `dreams_run_duration_seconds`.

**J. Testing (10 items):**

1. `tests/unit/dreams/test_runner.py` — orchestration unit tests with stubbed LLM + stubbed session factory.
2. `tests/unit/dreams/test_generators_{schedule,off_screen,diary,open_loops,activity_design}.py` — per-generator unit tests.
3. `tests/unit/dreams/test_consolidation.py` — decay refresh, dyad deltas, loop expiry.
4. `tests/unit/dreams/test_llm.py` — BDOne retry/circuit-breaker behavior, token counting.
5. `tests/unit/dreams/test_daemon.py` — scheduler config, CLI `--once` path.
6. **`tests/integration/test_dreams_pipeline.py` — END-TO-END PUBLIC API CONTRACT (lesson #1 load-bearing).** Invoke `run_dreams_pass()` with stubbed session data + StubBDOne; assert 5 outputs landed in DB per character, Phase G prose renderers applied, Phase A'' tags on Alicia-away output.
7. **`tests/integration/test_dreams_to_scene_director.py`** — after Dreams run, next `classify_scene()` + `select_next_speaker()` pick up Dreams-sourced `activity_context`; narrative salience boost fires for candidates named in diary/activity.
8. **`tests/integration/test_dreams_to_assembler.py`** — after Dreams run, next `assemble_context()` includes Dreams-generated open loops in Layer 6 and Dreams-generated activity in Layer 4/6.
9. Per-character regression tests (H4) and fidelity tests (H5).
10. `tests/integration/test_dreams_alicia_away_mode.py` — Alicia `life_state.is_away=True` → all generated content tagged with `communication_mode`, Phase A'' filter preserves them in remote-mode runtime prompts.

### Files touched

**New modules (~30 files):**

- `src/starry_lyfe/dreams/__init__.py`, `runner.py`, `daemon.py`, `llm.py`, `writers.py`, `consolidation.py`, `config.py`, `errors.py` (8 files)
- `src/starry_lyfe/dreams/generators/{__init__,schedule,off_screen,diary,open_loops,activity_design}.py` (6 files)
- `src/starry_lyfe/db/models/{life_state,activity,consolidated_memory,consolidation_log,drive_state,proactive_intent,session_health}.py` (7 files)
- `src/starry_lyfe/db/migrations/` Alembic scaffold + initial migration (2-3 files)
- `src/starry_lyfe/canon/routines.yaml`, `src/starry_lyfe/canon/routines_loader.py`, `src/starry_lyfe/canon/schemas/routines.py` (3 files)
- `tests/unit/dreams/` (~10 files) + `tests/integration/test_dreams_*.py` (4 files) + `tests/fidelity/dreams/` (8 files)

**Modified:**

- `src/starry_lyfe/context/prose.py` — 12 new `render_*_prose` helpers
- `src/starry_lyfe/context/constraints.py` — honor `communication_mode` tag from Dreams activities at Layer 7
- `src/starry_lyfe/db/retrieval.py` — extend `MemoryBundle` to expose new tiers
- `src/starry_lyfe/canon/loader.py` — wire `routines_loader.py` into `load_all_canon()`
- `src/starry_lyfe/db/seed.py` — seed routines, life_state rows
- `.env.example`, `requirements.txt`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md` — 6-surface status sweep (lesson #3: §2, §9, §36, §74, §1450, §1537)
- `Docs/OPERATOR_GUIDE.md` — new §15 Dreams section
- `Docs/CHANGELOG.md`, `CLAUDE.md` §19

### Acceptance criteria

- **AC-1** `run_dreams_pass()` is a pure function taking `session_factory`, `llm_client`, `canon`, `now` — testable without live DB or live LLM.
- **AC-2** Every character in `CharacterID.all_strings()` is processed on every pass; coverage asserted via `_assert_complete_character_keys()` on the result map.
- **AC-3** All 5 output types (schedule, off-screen, diary, open_loops, activity_design) produce at least one DB row per character per run (unless explicitly skipped with log reason).
- **AC-4** Every generated narrative text routes through a Phase G prose renderer — no raw LLM JSON reaches DB (Phase G retroactive).
- **AC-5** Alicia's generated output when `life_state.is_away=True` carries `communication_mode ∈ {phone, letter, video_call}` on every row (Phase A'' retroactive).
- **AC-6** Per-character Dreams output passes the per-character soul-regression bundle (Phase H retroactive).
- **AC-7** Per-character Dreams output scores ≥ threshold on the Phase F-Fidelity harness extended with Dreams scenes.
- **AC-8** Scheduler fires `run_dreams_pass()` at configured cron (default 03:30 local); `--once` CLI invokes one pass and exits.
- **AC-9** End-to-end `test_dreams_pipeline.py`: stubbed session + StubBDOne → `run_dreams_pass()` → DB reflects all 5 output types per character.
- **AC-10** End-to-end `test_dreams_to_scene_director.py`: post-Dreams, `NextSpeakerInput.activity_context` carries Dreams text and Rule 7 narrative salience fires on candidate names in it.
- **AC-11** End-to-end `test_dreams_to_assembler.py`: post-Dreams, `assemble_context()` Layer 6 includes Dreams-generated open loops and Layer 4/6 includes Dreams activity.
- **AC-12** Somatic decay refresh: `refresh_somatic_decay` applied per character; `last_decayed_at` updated; values via existing `apply_decay()`.
- **AC-13** Dyad deltas capped ±0.10 per dimension per Dreams pass (vs ±0.03 per-turn runtime); over-limit deltas clamped with warning logged.
- **AC-14** Stale open loops (expires_at < now) bulk-transitioned to `status='expired'`.
- **AC-15** 7 new DB tables shipped with Alembic migration; migrations forward/backward tested.
- **AC-16** `routines.yaml` validates against Pydantic schema at `load_all_canon()` time; invalid routines fail loud.
- **AC-17** `BDOne` client raises `DreamsLLMError` after exhausting retries; circuit-breaker opens after N failures.
- **AC-18** All 748 pre-phase tests still pass; ~80 new tests added (baseline 748 → ~830).
- **AC-19** ruff clean, mypy `--strict` clean.
- **AC-20** CHANGELOG `[Unreleased]` records the landing.
- **AC-21** Closing block of this file updated with final status, commits, tests added, lessons-for-next-phase.
- **AC-22** **Master-plan sweep (lesson #3):** every Phase 6 status surface updated in one pass — §36 summary bullet, §74 Vision Alignment, §1450 Architectural Layers, §1537 "does not do", §2 backend summary, §9 Dreams implementation-status block. Grep `Phase 6.*PLANNED|Dreams engine.*PLANNED|PLANNED.*Phase 6|When Phase 6 is implemented` returns empty.
- **AC-23** `OPERATOR_GUIDE.md` gains a §15 Dreams section with CLI invocation, env-var reference, retroactive Phase G/A''/H notes, and file:line map for public API symbols.
- **AC-24** CLAUDE.md §19 shipped list + test baseline updated.
- **AC-25** **Anti-contamination at generation (lesson #2):** when a generator scans yesterday's cross-character session data to select material for the focal character, the candidate pool is filtered against `focal_character` before ranking; a "diary entry for Bina" cannot accidentally reference Reina's internal thoughts. Verified by `test_dreams_regression_{character}.py` cross-character contamination negatives.

### Estimated commits

6-10 commits, partitioned along subsystem boundaries for reviewability:

1. DB models + Alembic migration (subsystem A)
2. Canon layer: routines.yaml + schema + loader (subsystem B)
3. BD-1 HTTP client + stub + tests (subsystem C)
4. Dreams package scaffold: runner + daemon + config + errors (subsystem D + G1 + I)
5. Content generators (subsystem E) — one or two commits
6. Consolidation helpers (subsystem F)
7. Retroactive Phase G/A''/H wiring (subsystem H) — one or two commits
8. Integration tests (subsystem J6-10)
9. Docs sweep: PHASE_6.md closing block + master-plan 6-surface sweep + OPERATOR_GUIDE §15 + CHANGELOG + CLAUDE.md §19

Codex audit rounds likely. Target: 1-2 audit rounds given the scope.

### Open questions for Project Owner

- **Q1 (resolved via Handshake Log row 3):** Scope — monolithic or phased? **APPROVED: monolithic.**
- **Q2 (resolved via Handshake Log row 3):** Scheduler trigger — apscheduler in-process vs external cron vs deferred? **APPROVED: apscheduler in-process daemon with standalone CLI.**
- **Q3 (resolved via Handshake Log row 3):** Content source — session data, canonical routines, or both? **APPROVED: both (session data for memory/loop consolidation, canonical routines for schedule/activity generation).**
- **Q4 (open, non-blocking):** Default LLM model for Dreams — `anthropic/claude-opus-4-6` via OpenRouter, or the cheaper `anthropic/claude-sonnet-4-6`? Recommendation: Sonnet for cost control; Opus only for difficult content (diary/activity-design). Will default to `STARRY_LYFE__EXT__SFW_MODEL` and let operator override via `STARRY_LYFE__DREAMS__LLM_MODEL`.
- **Q5 (open, non-blocking):** Dreams dry-run in CI — should CI invoke `python -m starry_lyfe.dreams --once --dry-run` as a smoke test? Recommendation: yes, against a Postgres test fixture; adds ~5s to CI.

---

## Step 1: Plan (Claude Code)

**[STATUS: COMPLETE — plan drafted, Project Owner approved via Handshake Log row 3]**
**Owner:** Claude Code
**Reads:** Master plan §9, Vision §119/123/140, Persona Tier Framework for voice registers, AGENTS.md Phase 6 customization, `Characters/{each}/{Name}_v7.1.md`, `src/starry_lyfe/scene/next_speaker.py` (for `activity_context` handoff), `src/starry_lyfe/context/prose.py` (for Phase G renderers to reuse), existing DB models
**Writes:** This section

### Plan content

**Files Claude Code intends to create or modify:**

- `src/starry_lyfe/dreams/` — new package, ~14 files (runner, daemon, llm, writers, consolidation, config, errors, generators/{5 files}, __init__.py)
- `src/starry_lyfe/db/models/` — 7 new model files (life_state, activity, consolidated_memory, consolidation_log, drive_state, proactive_intent, session_health)
- `src/starry_lyfe/db/migrations/` — Alembic scaffold + initial migration
- `src/starry_lyfe/canon/routines.yaml`, `routines_loader.py`, `schemas/routines.py` — new canonical routines
- `src/starry_lyfe/context/prose.py` — +12 new `render_*_prose` helpers (reuse existing phrase banks)
- `src/starry_lyfe/context/constraints.py` — honor Dreams `communication_mode` tag at Layer 7
- `src/starry_lyfe/db/retrieval.py` — extend `MemoryBundle` to expose new tiers
- `src/starry_lyfe/canon/loader.py` — wire `routines_loader` into `load_all_canon()`
- `src/starry_lyfe/db/seed.py` — seed routines + life_state
- `tests/unit/dreams/` — ~10 new unit test modules
- `tests/integration/test_dreams_*.py` — 4 new integration tests
- `tests/fidelity/dreams/` — 4 new scene YAMLs + 4 new test files
- `.env.example`, `requirements.txt` (add `apscheduler>=3.10,<4.0`)
- `Docs/_phases/PHASE_6.md` (this file)
- `Docs/_phases/_samples/PHASE_6_dreams_output_{adelia,bina,reina,alicia}_2026-04-14.txt` — 4 sample Dreams output artifacts
- `Docs/IMPLEMENTATION_PLAN_v7.1.md` — 6-surface status sweep (§2, §9, §36, §74, §1450, §1537)
- `Docs/OPERATOR_GUIDE.md` — new §15 Dreams section
- `Docs/CHANGELOG.md`, `CLAUDE.md` §19

**Test cases Claude Code intends to add (~80 new tests):**

- Unit (per-module): `test_runner`, `test_generators_{5 types}`, `test_consolidation`, `test_llm`, `test_daemon` — ~50 tests
- Per-character regression: `test_dreams_regression_{adelia,bina,reina,alicia}` — ~15 tests each (Phase H retroactive)
- Integration end-to-end (load-bearing, lesson #1):
  - `test_dreams_pipeline` — full run_dreams_pass → DB state
  - `test_dreams_to_scene_director` — Dreams → NextSpeakerInput.activity_context → Rule 7 salience
  - `test_dreams_to_assembler` — Dreams → assemble_context Layer 4/6
  - `test_dreams_alicia_away_mode` — Phase A'' retroactive
- Fidelity: 4 character × N scene cases via `tests/fidelity/dreams/`

**Acceptance criteria (mirror the spec above, AC-1 through AC-25):** PENDING during execution.

**Deviations from the master plan:**

- None structural. The master plan §9 enumerates Dreams responsibilities at architectural granularity; Phase 6 implements the full set as specified.
- Project-Owner-approved scope choices (Handshake Log row 3): apscheduler vs external cron, both-input content sources, LLM-driven generation with BDOne wrapper. These are not master-plan deviations; they are implementation choices within the master-plan scope.

**Estimated commits:** 6-10, partitioned per subsystem (see spec "Estimated commits" section above).

**Open questions for the Project Owner before execution:**

- Q1-Q3: resolved via Handshake Log row 3.
- Q4 (default LLM model): recommend defaulting to `STARRY_LYFE__EXT__SFW_MODEL` with `STARRY_LYFE__DREAMS__LLM_MODEL` override. Non-blocking; can be decided at env-config time.
- Q5 (CI dry-run smoke): recommend yes, but non-blocking for Step 2.

### Plan approval

**Project Owner approval:** APPROVED (Handshake Log row 3). Scope choices: monolithic, apscheduler, both-sources + LLM-driven generation. Ready to proceed to Step 2.

<!-- HANDSHAKE: Project Owner -> Claude Code | Phase 6 plan approved with full §9 scope. Proceed with execution. -->

---

## Step 2: Execute (Claude Code)

**[STATUS: MVP CHECKPOINT — commits 1-5 + J6 integration test landed; commits 6-9 pending]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner (complete)
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/starry_lyfe/dreams/` and `src/starry_lyfe/db/models/`, tests in `tests/`, this section

### Execution log

- **Commits made (one row per commit):**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | `247247e` | `feat(phase_6a): 7 new DB models + Alembic migration for Dreams tier 8` | 7 new `db/models/*.py` + `db/models/__init__.py` + Alembic `versions/002_phase_6_dreams_tables.py` |
| 2 | `0411389` | `feat(phase_6b): canonical routines.yaml + Pydantic schema + loader` | `canon/routines.yaml` + `canon/routines_loader.py` + `canon/schemas/routines.py` + `canon/schemas/__init__.py` + `canon/loader.py` + `tests/unit/test_routines_loader.py` |
| 3 | `ffe58a3` | `feat(phase_6c): BD-1 HTTP client wrapper + StubBDOne` | `dreams/__init__.py` + `dreams/errors.py` + `dreams/llm.py` + `tests/unit/dreams/test_llm.py` |
| 4 | `cc37a0d` | `feat(phase_6d): Dreams package scaffold — runner, daemon, generators, config` | `dreams/{runner,daemon,__main__,types,config}.py` + `dreams/generators/*` (5 files) + `tests/unit/dreams/test_runner.py` + `requirements.txt` |
| 5 | `7913c6a` | `feat(phase_6e): diary generator end-to-end with Phase G prose wrapping` | `context/prose.py` (+12 new render helpers begin; render_diary_prose + opener/closer dicts) + `dreams/generators/diary.py` (stub replaced with LLM-backed impl) + `tests/unit/dreams/test_diary.py` |
| 5a | _this commit_ | `test(phase_6_mvp): test_dreams_pipeline.py end-to-end contract + PHASE_6.md checkpoint` | `tests/integration/test_dreams_pipeline.py` + `Docs/_phases/PHASE_6.md` |
| 6-9 | _pending_ | Commits 6 (consolidation helpers, Subsystem F), 7 (full retroactive Phase G/A''/H wiring including communication_mode column on episodic_memories + remaining 11 render_*_prose helpers), 8 (full integration test suite J6-J10), 9 (master-plan sweep + OPERATOR_GUIDE §15 + CHANGELOG + CLAUDE.md §19) | _deferred to follow-up session_ |

- **Test suite delta:**
  - Tests passing: 748 (pre-phase) → 800 (MVP checkpoint; +52 new). Deltas per commit: A 748→748 (models register but no test changes), B 748→757 (+9 routines), C 757→771 (+14 BDOne), D 771→779 (+8 runner), E 779→786 (+7 diary), J6 786→800 (+14: 7 new integration + 7 unit tests absorbed from existing dreams suite).
  - Tests failing: none
- **Sample Dreams output artifacts:** Deferred to commit 9 — will be produced by `python -m starry_lyfe.dreams --once --dry-run` against a seeded DB and saved to `Docs/_phases/_samples/PHASE_6_dreams_output_{adelia,bina,reina,alicia}_2026-04-14.txt`.

- **Self-assessment against acceptance criteria (AC-1 through AC-25):**

  | AC | Status | Evidence |
  |----|--------|----------|
  | AC-1 | MET | `run_dreams_pass(session_factory, llm_client, canon, now)` pure; tested with StubBDOne + stub session factory in `test_dreams_pipeline.py`. |
  | AC-2 | MET | `_assert_complete_character_keys(character_results, ...)` invoked at runner boundary; integration test asserts all 4 characters processed. |
  | AC-3 | PARTIAL | Schedule + diary produce output per character. Off-screen, open-loops, activity-design remain placeholder stubs (commits 6+). |
  | AC-4 | MET (for diary) | `render_diary_prose` wraps raw LLM text in per-character Phase G frame; integration test asserts 3-paragraph structure. Other generators produce no narrative text yet. |
  | AC-5 | PARTIAL | `alicia_communication_distribution` canonically loaded and exposed via `get_alicia_communication_distribution()`; full Alicia-away tagging on activities/episodics lands in commit 7. |
  | AC-6 | NOT MET | Per-character regression tests (`test_dreams_regression_*.py`) not yet written; commit 7 scope. |
  | AC-7 | NOT MET | Fidelity harness extension pending commit 7. |
  | AC-8 | MET | Daemon CLI `python -m starry_lyfe.dreams [--once] [--dry-run]` implemented; apscheduler CronTrigger + misfire_grace_time configured. |
  | AC-9 | MET | `test_dreams_pipeline.py` exercises the public API end-to-end with 7 cases including the lesson-#2 cross-character contamination negative. |
  | AC-10 | NOT MET | `test_dreams_to_scene_director.py` pending commit 8. |
  | AC-11 | NOT MET | `test_dreams_to_assembler.py` pending commit 8. |
  | AC-12 | NOT MET | `refresh_somatic_decay` helper pending commit 6 (Subsystem F). |
  | AC-13 | NOT MET | Dyad delta cap pending commit 6. |
  | AC-14 | NOT MET | Loop expiry pending commit 6. |
  | AC-15 | MET | Alembic `002_phase_6_dreams_tables.py` creates all 7 new tables with indexes; downgrade reverses. |
  | AC-16 | MET | `routines.yaml` validates via `CanonRoutines` Pydantic schema at `load_all_canon()` time; missing coverage raises. |
  | AC-17 | MET | `BDOne.complete()` raises `DreamsLLMError` after exhausted retries; circuit-breaker opens at `circuit_threshold` consecutive failures. |
  | AC-18 | PARTIAL | 748 → 800 (+52). Target 830 will be reached when commits 6-9 land. |
  | AC-19 | MET | ruff + mypy `--strict` clean at each commit. |
  | AC-20 | NOT MET | CHANGELOG update pending commit 9. |
  | AC-21 | PARTIAL | Phase file has complete spec; Step 2 checkpoint logged; closing block pending final ship. |
  | AC-22 | NOT MET | Master-plan 6-surface sweep pending commit 9. |
  | AC-23 | NOT MET | OPERATOR_GUIDE §15 pending commit 9. |
  | AC-24 | NOT MET | CLAUDE.md §19 pending commit 9. |
  | AC-25 | MET (for diary) | `test_cross_character_contamination_negative` in integration test proves diary system prompts exclude all other canonical women's names. Other generators lack LLM calls to contaminate. |

- **Open questions for Codex / Claude AI / Project Owner:**
  - Q1: `communication_mode` column on `episodic_memories` requires a DB migration. Commit 7 will add that column + migration. The integration test suite that exercises it (commit 8) must be run against a migrated DB. Confirm this is acceptable, or whether we should ship the column + migration in a separate earlier commit.
  - Q2: Default LLM model for Dreams — Phase 6 plan Q4 remains open. Recommendation: default to `STARRY_LYFE__EXT__SFW_MODEL` (Sonnet) via `STARRY_LYFE__DREAMS__LLM_MODEL`. Non-blocking; can be decided at env-config time.

<!-- HANDSHAKE: Claude Code -> Claude Code (future session) | MVP checkpoint reached. Commits 1-5 + J6 shipped. Commits 6-9 remain. Do NOT hand off to Codex until all commits land — partial execution does not trigger Step 3 audit. -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan §9, the plan and execution log above, git diff against pre-phase commit (`9119b3c`), the actual test files, sample Dreams output artifacts, character kernel files (all 4), `Docs/_phases/PHASE_5.md` for the handoff contract to Phase 5 `activity_context`
**Writes:** This section. Codex does NOT modify production code, does NOT commit fixes, does NOT touch the canon directly.

### Audit content

_Codex will fill in this subsection. Required fields: Scope, Verification context, Executive assessment, Findings table, Runtime probe summary, Drift against specification, Verified resolved, Adversarial scenarios (≥3), Gate recommendation._

**Adversarial scenarios specific to Phase 6 (Codex should construct ≥3):**

1. Alicia `life_state.is_away` flips mid-Dreams-run: does the generated content carry consistent `communication_mode` tags for the whole pass?
2. LLM returns empty string or JSON instead of prose: does the Phase G renderer gate catch it before DB write?
3. Cross-character contamination: does a diary generator for Bina accidentally include Reina's session-level inner state? Anti-contamination filter (lesson #2 / AC-25) must prevent this.
4. Scheduler-miss recovery: if the daemon was down at 03:30, does the `misfire_grace_time=3600` honor a 04:15 catch-up run, and does the catch-up write a consolidation log row indicating the late execution?
5. Somatic decay over-apply: if `run_dreams_pass()` is invoked twice in one day (e.g., manual `--once` after nightly cron), does decay double-apply or is it idempotent?
6. `routines.yaml` missing a character entry: does `load_all_canon()` fail loud at import, consistent with R-3.2 coverage pattern?

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete, ready for remediation -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code
**Reads:** The audit above, the master plan, the canon
**Writes:** Production code, tests, this section. May supersede sample Dreams output artifacts.

### Remediation content

_Claude Code will fill in. Per-finding status table, push-backs, deferrals, re-run test suite delta, new sample artifacts, self-assessment._

### Path decision

_Claude Code must choose Path A (clean remediation, skip re-audit) or Path B (substantive, re-audit)._

**Chosen path:** _pending_

<!-- HANDSHAKE: Claude Code -> {Codex if Path B / Claude AI if Path A} | Remediation Round 1 complete, ready for {re-audit / QA} -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B was chosen in Round 1)

**[STATUS: NOT STARTED]**

_Same structure as Round 1. Codex re-audits focusing on: (a) whether original findings are actually closed, (b) whether remediation introduced any new findings, (c) particularly review Phase G prose rendering coverage, Phase A'' communication_mode tagging, and lesson-#2 anti-contamination filtering._

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 2 complete -->

---

## Step 4': Remediate (Claude Code) — Round 2 (only if Round 2 audit produced new findings)

**[STATUS: NOT STARTED]**

_Same structure as Round 1._

<!-- HANDSHAKE: Claude Code -> {Codex if Path B / Claude AI if Path A} | Remediation Round 2 complete -->

---

## Step 3'': Audit (Codex) — Round 3 (only if convergence has not been reached)

**[STATUS: NOT STARTED]**

_Same structure. **Final audit round before mandatory escalation to Project Owner per AGENTS.md cycle limit.**_

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 3 complete -->

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: NOT STARTED]**

_Same structure. **If convergence not reached after this round, Claude Code MUST escalate to Project Owner instead of starting Round 4.**_

<!-- HANDSHAKE: Claude Code -> {Project Owner if not converged / Claude AI if converged} | Remediation Round 3 complete -->

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**
**Owner:** Claude AI
**Prerequisite:** Step 4 (or 4', or 4'') remediation complete with handshake to Claude AI, AND Project Owner has brought the phase artifacts to Claude AI in chat
**Reads:** Master plan §9, the entire phase file above, test output from most recent run, sample Dreams output artifacts, phase status log
**Writes:** This section

### QA verdict content

_Claude AI will fill in. Specification trace (AC-1 through AC-25 with PASS/FAIL/N/A), audit findings trace, sample prompt review, cross-Phase impact check, severity re-rating if any, open questions, verdict._

**Load-bearing QA items specific to Phase 6:**

- **Sample review:** Claude AI reads one Dreams output artifact per character end-to-end and evaluates: (a) is this recognizably the character's voice? (b) does the content reflect canonical routines + yesterday's session data? (c) is Phase G prose rendering evident? (d) for Alicia-away samples, are `communication_mode` tags present?
- **Cross-Phase impact check:** does Dreams output correctly populate Phase 5 `NextSpeakerInput.activity_context` and Phase 3 Layer 6 (scene_context)? Run next-turn smoke: `classify_scene` → `select_next_speaker` → `assemble_context` and confirm Dreams-generated activity reaches the model.
- **Subjective voice distinctness (lesson carried from Phase 5 audit culture):** spot-check each character's Dreams output for voice-swappability with other characters. Any flattening is a FAIL regardless of rubric score.

### Verdict

_pending_

### Phase progression authorization

_pending; next phase recommendation: Phase 7 (HTTP service)._

<!-- HANDSHAKE: Claude AI -> Project Owner | QA verdict ready, awaiting ship decision -->

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**
**Owner:** Project Owner (Whyze / Shawn Kroon)
**Prerequisite:** Step 5 QA verdict ready
**Reads:** The entire phase file
**Writes:** This section. The decision is locked once recorded.

### Ship decision

_pending_

<!-- HANDSHAKE: Project Owner -> CLOSED | Phase shipped, work complete -->
_(or)_
<!-- HANDSHAKE: Project Owner -> Claude Code | Sent back to remediation, see Project Owner notes above -->
_(or)_
<!-- HANDSHAKE: Project Owner -> CLOSED | Phase stopped for redesign, master plan update required before restart -->

---

## Closing Block (locked once shipped)

**Phase identifier:** 6
**Final status:** _pending_
**Total cycle rounds:** _pending_
**Total commits:** _pending_
**Total tests added:** _pending (target ~80; baseline 748 → ~830)_
**Date opened:** 2026-04-14 (when this file was created by Claude AI)
**Date closed:** _pending_

**Lessons for the next phase:** _pending (Claude AI fills in after ship)_

**Cross-references:**

- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §9
- AGENTS.md cycle definition: `AGENTS.md`
- Sample Dreams output artifacts: `Docs/_phases/_samples/PHASE_6_dreams_output_*.txt`
- Planning artifact: `C:\Users\Whyze\.claude\plans\fizzy-napping-whisper.md`
- Previous phase file: `Docs/_phases/PHASE_5.md` (Scene Director, SHIPPED 2026-04-14 with R1/R2/R3 remediations)
- Handoff target: Phase 5 `NextSpeakerInput.activity_context` slot (`src/starry_lyfe/scene/next_speaker.py:103`)
- Retroactive phases: Phase G (`src/starry_lyfe/context/prose.py` renderers), Phase A'' (`layers.py:75-84` communication-mode pruning), Phase H (per-character regression bundles at `tests/unit/test_soul_regression_*.py`)
- Next phase file (if shipped): `Docs/_phases/PHASE_7.md`

---

_End of Phase 6 canonical record. Do not edit fields above this line after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
