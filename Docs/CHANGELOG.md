# Changelog

All notable changes to the Starry-Lyfe backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added (Phase 3: Context Assembly — Complete)

- Seven-layer context assembler (`assembler.py`) with terminal constraint anchoring
- Per-layer formatters (`layers.py`): kernel, canon facts, memory fragments, sensory grounding, voice directives, scene blocks, constraints
- Section-aware kernel compilation (`kernel_loader.py`) with PRESERVE markers and per-section token budgets
- Soul essence (`soul_essence.py`): 45 hand-authored canonical blocks, guaranteed surcharge on kernel budget, never trimmed
- Soul cards (`soul_cards/`): 15 YAML-fronted markdown cards with Pydantic-validated activation rules (always / communication_mode / with_character / scene_keyword)
- Pair metadata runtime surface (`pairs_loader.py`) — 6 fields from pairs.yaml emitted as structured block at top of Layer 5
- VoiceMode enum (11 modes) and mode-aware exemplar selection with public-register safety
- SceneType enum (8 types) + SceneModifiers dataclass (4 cross-cutting flags) driving section promotion and Layer 7 constraint injection
- Per-character dramaturgical prose renderers (`prose.py`) for Layers 2, 4, 6
- Structured DEBUG logging in `_select_voice_exemplars()` for runtime observability
- OPERATOR_GUIDE.md — 676-line runtime pipeline walkthrough (markdown → 7-layer prompt)
- Phase E voice rhythm exemplars (all 4 characters, mode-tagged)
- Phase F scene-aware section retrieval with dormant VoiceMode closure (11/11 modes reachable)
- Phase G per-character prose rendering
- Phase H soul regression test suite (adelia/bina/reina/alicia)
- Phase K subjective success proxies
- Assembler sample artifacts at `Docs/_phases/_samples/PHASE_F_assembled_*.txt`

### Added (Phase 4: Whyze-Byte Validation Pipeline — Complete)

- `validation/whyze_byte.py` persona fidelity validator
- Whyze-Byte regression test suite

### Added (Phase 2 audit remediation — REMEDIATION_2026-04-13.md)

- `SoulEssenceNotFoundError(ValueError)` — fail-loud semantics for missing character soul essence (Vision V6-V9 defense)
- `CanonValidationError(ValueError)` with `.errors` list and `.format_errors()` helper
- `DecayConfigIncompleteError(ValueError)` + `REQUIRED_DECAY_KEYS` guard in `fetch_decayed_somatic_state`
- `SoulCardActivation` Pydantic model with `extra='forbid'` replacing untyped activation dict
- `CharacterID.all()` and `CharacterID.all_strings()` classmethods
- `_assert_complete_character_keys()` helper wired at module-load in 6 modules (budgets, kernel_loader, pairs_loader, prose, constraints, soul_essence)
- Post-assembly Layer 1 / Layer 6 budget reconciliation warnings
- Docs/_audits/PHASE_2_AUDIT_2026-04-13.md — full self-audit record
- Docs/_phases/REMEDIATION_2026-04-13.md — approved remediation spec

### Fixed (Phase 6 Round 1 remediation — closes Codex F1/F2/F3/F4/F5/F6)

- **F1 Critical** (`726e550`): writers.py with 5 writer functions (diary/activity/new_open_loops/off_screen_events/consolidation_log); default_snapshot_loader reads 24h of real session data replacing the empty stub; runner.py `_process_character` invokes writers + consolidation inside a per-character `session.begin()` transaction; `DreamsCharacterResult` fields populated from real DB outcomes (diary_entry_id, activities_designed, somatic_refreshed, etc. — no hardcoded None/0/False).
- **F2 High** (`5172bb7` + `dc42add`): off_screen / open_loops / activity_design generators now LLM-backed end-to-end with per-character voice-register system prompts, anti-contamination user prompts (lesson #2), Phase G `render_*_prose` wrapping, and Alicia-away `communication_mode` sampling. All 5 Dreams generators are now real. `activities_designed` false-positive bug from Codex adversarial scenario #2 closed.
- **F3 High** (`5e7f788`): `MemoryBundle` extended with `activities` + `life_state` Tier-8 fields; `_retrieve_activities` + `_retrieve_life_state` added. `tests/integration/test_dreams_db_round_trip.py` (4 cases) proves end-to-end DB-backed contract: `run_dreams_pass → rows → retrieve_memories → assembler` with live Postgres. Writer embedding column fix (`"[0.0,...]"` → `[0.0] * 768`) landed same commit.
- **F4 Medium** (`1c69629`): `tests/unit/dreams/test_daemon.py` (11 cases — CLI parser, scheduler config, invalid cron, env overrides). `tests/fidelity/dreams/test_dreams_voice_fidelity.py` (8 parametrized — per-character opener presence + cross-character contamination negative). Per-generator unit tests for off_screen/open_loops/activity_design from R3/R4/R5.
- **F5 Medium** (`aebb30e` + this commit): header reopened to IN PROGRESS → corrected back to SHIPPED after full remediation landed; handshake log row 5 annotated as original overclaim; Step 4 per-finding status table updated with real commit hashes and FIXED statuses; closing block corrected to 897 actual tests (was overclaimed 843); sample Dreams output artifacts at `Docs/_phases/_samples/PHASE_6_dreams_output_*.txt` generated via `--once --dry-run`.
- **F6 Low** (`726e550`): runner `_process_character` uses `asyncio.gather(*..., return_exceptions=True)` with per-generator graceful failure. `test_generators_run_in_parallel` + `test_one_generator_failure_does_not_kill_others` prove parallelism + failure isolation.

Test baseline 748 → 897 (+149 total Phase 6 contribution). ruff + mypy `--strict` clean.

### Added (Phase 6: Dreams Engine)

- `src/starry_lyfe/dreams/` package — nightly batch life-simulation engine per `Docs/IMPLEMENTATION_PLAN_v7.1.md` §9
- `run_dreams_pass(session_factory, llm_client, canon, now)` — public API that iterates all 4 canonical characters, runs the 5 content generators per character, aggregates token totals and warnings; `_assert_complete_character_keys` coverage invariant on the result map
- apscheduler-based daemon + CLI entry `python -m starry_lyfe.dreams [--once] [--dry-run]`
- `DreamsSettings` / `BDOneSettings` GNK-pattern config loaded from new `STARRY_LYFE__DREAMS__*` / `STARRY_LYFE__BD1__*` env vars
- Protocol Droid BD-1: `BDOne` HTTP client wrapping `httpx.AsyncClient` with exponential backoff + circuit breaker + token tracking; `StubBDOne` deterministic test stub keyed by prompt hash
- 5 content generators: `schedule` (deterministic from `routines.yaml`), `diary` (LLM-backed, end-to-end with Phase G prose wrapping), `off_screen` / `open_loops` / `activity_design` (placeholder stubs with TODO markers for follow-up)
- `src/starry_lyfe/dreams/consolidation.py` — `refresh_somatic_decay` (tier-7 exponential decay), `apply_overnight_dyad_deltas` (per-dimension ±0.10 cap with audit bookkeeping), `expire_stale_loops` (TTL transition), `resolve_addressed_loops` (Dreams-resolution)
- `src/starry_lyfe/canon/routines.yaml` + Pydantic schema + loader — canonical per-character weekday/weekend routines plus Alicia's away-mode communication_mode distribution (0.45 phone / 0.20 letter / 0.35 video_call)
- 7 new DB models + Alembic migration 002: `LifeState`, `Activity`, `ConsolidatedMemory`, `ConsolidationLog`, `DriveState`, `ProactiveIntent`, `SessionHealth`
- Alembic migration 003 adds `communication_mode` column to `episodic_memories` (Phase A'' retroactive)
- `src/starry_lyfe/dreams/alicia_mode.py` — deterministic weighted sampling of `communication_mode` for Alicia-away artifacts; `should_tag_alicia_away()` narrow gate
- `src/starry_lyfe/context/prose.py` — `render_diary_prose()` per-character helpers with `_DIARY_OPENERS` / `_DIARY_CLOSERS` phrase banks (Phase G retroactive)
- 4 new integration test files: `test_dreams_pipeline` (end-to-end runner + anti-contamination negative), `test_dreams_to_scene_director` (Dreams `activity_context` → Rule 7 salience boost), `test_dreams_to_assembler` (Dreams `scene_description` → Layer 4/6), `test_dreams_alicia_away_mode` (full-pass tagging distribution)
- Per-character regression bundle `test_dreams_regression_per_character.py` — 16 parametrized cases covering opener presence, cross-character contamination negatives, 3-paragraph Phase G structure, and Alicia-away communication_mode invariants
- ~95 new tests added in original ship; Round 1 remediation added +54 more (baseline 748 → 897 post-remediation)
- `Docs/_phases/PHASE_6.md` — full phase spec + closing block
- `apscheduler>=3.10,<4.0` added to `requirements.txt`

### Fixed (Phase 5 Round 3 direct doc remediation — closes Codex R3-F1/R3-F2)

- **R3-F1** (MEDIUM): completed the remaining Phase 5 master-plan sync inside the live prose surfaces that Round 2 missed. `Docs/IMPLEMENTATION_PLAN_v7.1.md` now marks Scene Director complete in the §2 backend summary and the §8 Scene Director implementation-status block, and rewrites the stale pre-implementation classifier notes to match the shipped `src/starry_lyfe/scene/` surface.
- **R3-F2** (LOW): corrected the Phase 5 remediation record so it no longer overclaims that Round 2 removed every remaining `Phase 5 planned` / `PLANNED` line. `Docs/_phases/PHASE_5.md` now records the Round 3 direct doc remediation explicitly, and the Round 2 narrative is narrowed to the four named status-surface updates it actually made.

### Fixed (Phase 5 Round 2 remediation — closes Codex R2-F2 and partially closes R2-F1)

- **R2-F1** (MEDIUM): master-plan status drift reduced. `Docs/IMPLEMENTATION_PLAN_v7.1.md` was updated in four canonical status surfaces (status summary bullet :36, Vision Alignment matrix :74, Architectural Layers table :1450, "What This Plan Does Not Do" :1537) to reflect Phase 5 shipped state. The remaining §2 / §8 prose drift was closed in Round 3.
- **R2-F2** (LOW): `_detect_absent_dyads()` at `src/starry_lyfe/scene/classifier.py` now skips women whose names appear in `present_characters`. Phrases like `"thinking about adelia"` while Adelia is in the room are narrative color, not absent-dyad triggers. `_classify_modifiers()` + `classify_scene()` updated to thread `present_characters` through.
- 2 new regression tests (Codex's exact live probe + mixed present/absent scene). Test baseline 746 → 748.

### Fixed (Phase 5 Round 1 remediation — closes Codex F1/F2/F3)

- **F1** (HIGH): classifier-inferred absent dyads now normalize to `"<W>-<N>"` dyad-key shape (via `_to_dyad_keys()` in `classifier.py`) so `layers.format_scene_blocks()` actually renders the internal-dyad prose in Layer 6. Pre-remediation: classifier emitted bare names that Layer 6's string-equality check could not match.
- **F2** (MEDIUM): `classify_scene()` auto-appends `"whyze"` to `present_characters` when caller omits. Matches the runtime-canonical convention used by every pre-Phase-5 `assemble_context` test and prevents Layer 5 mode-derivation mis-routing (`solo_pair` vs `group`) for two-woman domestic scenes.
- **F3** (LOW): `NextSpeakerInput` gains `activity_context: str | None = None` field; `select_next_speaker()` adds Rule (7) narrative-salience (+0.05) when candidate is named in `scene_state.scene_description` or `activity_context`. Closes the `IMPLEMENTATION_PLAN_v7.1.md` §8 "current activity context" scoring-input gap.
- 9 new regression tests (3 classifier shape, 2 integration F1/F2, 4 Rule 7 salience). Test baseline 737 → 746.

### Added (Phase 5: Scene Director)

- `src/starry_lyfe/scene/` package — pre-assembly Scene Director implementing `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8
- `classify_scene(director_input)` — rule-based classifier produces `SceneState` from user message, present characters, residence flag, optional hints; `hints.*` always override inference
- `select_next_speaker(speaker_input)` — Talk-to-Each-Other Mandate scoring function with 6 rules: residence zero-out, Rule of One, 2-turn Whyze-chain penalty/reward, w2w continuation reward, dyad-state fitness (injected `DyadStateProvider`), recency suppression
- `AliciaAwayContradictionError` front-door gate (complements assembler's defense-in-depth `AliciaAwayError`)
- `NoValidSpeakerError` raised when every candidate is zeroed out by hard gates
- `DyadStateProvider` Protocol + `DictDyadStateProvider` dict-backed impl + `build_dyad_state_provider(rows)` adapter for `db/retrieval.py` output
- 86 new tests (64 unit in `tests/unit/scene/`, 6 integration, plus absorbed coverage improvements); test baseline 651 → 737
- `Docs/_phases/PHASE_5.md` — full phase spec, ACs, closing block

### Added (Phase F-Fidelity: Positive Fidelity Test Harness)

- `src/starry_lyfe/validation/fidelity.py` — `FidelityRubric`, `FidelityScore`, scoring methods (`canonical_marker_presence`, `anti_pattern_absence`, `structural_presence`, `score_rubric`)
- 7 rubric dimensions: voice_authenticity, pair_authenticity, cognitive_function, body_register, conflict_register, repair_register, autonomy_outside_pair (`RUBRIC_DIMENSIONS` constant)
- Per-character rubric YAMLs (4 files, 28 rubrics) at `tests/fidelity/rubrics/`
- Per-character scene YAMLs (4 files, 12 scenes) at `tests/fidelity/scenes/`
- Per-character fidelity tests at `tests/fidelity/test_{adelia,bina,reina,alicia}_fidelity.py` (37 parametrized cases)
- `Docs/_phases/PHASE_F_FIDELITY.md` — full spec including Vision V6 (Cognitive Hand-Off Integrity) → rubric mapping
- Whyze-Byte (negative filter) now complemented by positive rubric scoring; closes the gap identified in the Phase 2 audit (V6 had no code-level tripwire)

### Added (Phase 2 audit polish — Tier 4)

- `CharacterNotFoundError(ValueError)` unifies character-lookup failures in `kernel_loader._load_raw_kernel` and `pairs_loader.get_pair_metadata`
- `logger.warning` on missing Voice.md file or unregistered character path (M3)
- One-time `logger.warning` when a character's Voice.md has zero mode-tagged examples, signaling Layer 5 fallback to legacy calibration guidance (M4)
- Defense-in-depth documentation on the `_select_voice_exemplars` communication-mode empty-candidate branch (L1)

### Changed (Phase 2 audit polish — Tier 4)

- `budgets.py` LayerBudgets.scene comment replaced with dated Phase C pointer (M1)
- `budgets.py` heading regex now uses walrus operator; removed `# type: ignore[union-attr]` (M2)

### Changed (Phase 2 audit remediation)

- `load_all_canon()` now validates cross-file referential integrity by default (`validate_on_load=True`)
- `load_kernel()` cache key includes `profile_name` — prevents silent profile-collision caching
- `format_soul_essence()` raises `SoulEssenceNotFoundError` instead of silently returning empty string
- Pair loader `_ensure_loaded()` collects all missing entries and raises a single comprehensive error (was silent skip)
- `fetch_decayed_somatic_state` requires complete decay_config; removed `.get(key, default)` fallbacks
- `seed.main()` prints full traceback before exit-nonzero on failure

### Added (Phase 2: Memory Service)
- PostgreSQL + pgvector seven-tier memory substrate
- SQLAlchemy 2.0+ async ORM models for all 7 memory tiers
- Docker Compose for pgvector/pgvector:pg16
- Alembic async migration framework with initial migration
- Exponential decay logic for Transient Somatic State (configurable per-field half-lives)
- EmbeddingService protocol with Ollama implementation for pgvector episodic memory
- Canon-to-DB seed pipeline (Tiers 1-4 and 7 from Phase 1 YAML)
- Per-tier retrieval API with read-time decay and pgvector cosine similarity search
- Integration test suite for Gate 2 verification (seed counts, Alicia-orbital persistence, decay)
- Decay logic unit tests

### Added (Phase 1: Canon YAML Scaffolding)
- Project skeleton: `pyproject.toml`, `Makefile`, requirements, `.env.example`, `.gitignore`
- Canon YAML single source of truth: `characters.yaml`, `pairs.yaml`, `dyads.yaml`, `protocols.yaml`, `interlocks.yaml`, `voice_parameters.yaml`
- Pydantic v2 schema models for all 6 YAML files with strict validation
- Canon loader (`loader.py`) with typed `Canon` dataclass
- Cross-file referential integrity validator (`validator.py`) with 11 check categories
- GitHub Actions Phase 1 gate workflow
- v7.0 residue drift detection test (22 tokens from Handoff section 8.1)
- Em-dash/en-dash ban test for canon YAML
- Gate 1 verification test suite

### Fixed
- Aliyeh legacy name replaced with Bina across Alicia character files
- Alicia residence model aligned to resident-with-operational-travel
- Argentine geography diacritics: Famaillá, Tucumán
- Spanish institutional name diacritics: Cancillería, Dirección, Ferretería
- Reina's mother diacritics: Mercè Benítez
- Duplicate-member validation added to Dyad and Interlock schemas
