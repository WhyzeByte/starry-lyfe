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
- Docs/REMEDIATION_2026-04-13.md — approved remediation spec

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
