# Starry-Lyfe v7.1 Architecture

**Version:** 0.9.2
**Date:** 2026-04-15
**Status:** Concise architecture and module index. Canonical phase-completion status lives in `Docs/IMPLEMENTATION_PLAN_v7.1.md`.

## Overview

Starry-Lyfe is a character AI backend for four v7.1 persona kernels (Adelia Raye, Bina Malek, Reina Torres, Alicia Marin). Consumed exclusively by Msty AI via an OpenAI-compatible SSE streaming API on port 8001. Each character is a Msty Persona (Persona Studio, System Prompt Mode = Replace, blank system prompt in production — backend is the sole voice authority per ADR-001). Multi-character scenes use Msty Crew Mode.

**Shipped phases (as of 2026-04-15):**

- Phase 1: Canon YAML — `src/starry_lyfe/canon/`
- Phase 2: Memory Service — `src/starry_lyfe/db/`
- Phase 3: Seven-layer context assembly — `src/starry_lyfe/context/`
- Phase 4: Whyze-Byte validation — `src/starry_lyfe/validation/`
- Phase 5: Scene Director — `src/starry_lyfe/scene/`
- Phase 6: Dreams Engine (nightly batch life-simulation) — `src/starry_lyfe/dreams/`
- Phase 7: HTTP service on port 8001 — `src/starry_lyfe/api/`
- Phase 8: LLM Relationship Evaluator (Whyze-dyads) — **SEALED 2026-04-15** (Step 5 QA APPROVED FOR SHIP, 15/15 ACs PASS, all 6 Codex findings closed)
- Phase 9: LLM Relationship Evaluator (DyadStateInternal — inter-woman dyads) — **Step 3'' Audit Round 3 complete / Path C direct Codex doc-only remediation applied** (2026-04-15; all 3 Codex Round 1 findings closed: F1 speaker identity threaded into prompt + 6 regression tests, F2 Alicia-orbital remote-turn note narrowed to deferred future-phase scope per Project Owner Hybrid choice, F3 PHASE_9.md governance repair via `11a8af6`; 3 Round 3 low doc-traceability drifts closed directly by Codex under Project Owner authorization; gate PASS; ready for Step 5 QA)

**Test baseline:** 1119 passed, 0 failed (1014 unit + 60 integration + 45 fidelity). ruff clean. mypy `--strict` clean across 103 source files.

## Module Registry

### `src/starry_lyfe/canon/` -- Single Source of Truth (Phase 1)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `canon/loader.py` | Load YAML files through Pydantic schemas; `load_all_canon()` returns typed `Canon` object | GNK |
| `canon/validator.py` | Cross-file referential integrity; count assertions; CLI entry point | GNK |
| `canon/schemas/enums.py` | Shared StrEnum types for all canon models | -- |
| `canon/schemas/characters.py` | `CanonCharacters`: 4 characters + 1 operator | -- |
| `canon/schemas/pairs.py` | `CanonPairs`: 4 Whyze-to-character pairs | -- |
| `canon/schemas/dyads.py` | `CanonDyads`: 10 dyads + 7 memory tier definitions | -- |
| `canon/schemas/protocols.py` | `CanonProtocols`: 12+ protocols with Vision section 7 validation | -- |
| `canon/schemas/interlocks.py` | `CanonInterlocks`: 6 cross-partner interlocks | -- |
| `canon/schemas/voice_parameters.py` | `CanonVoiceParameters`: per-character inference parameters | -- |

### `src/starry_lyfe/db/` -- Memory Service (Phase 2)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `db/base.py` | SQLAlchemy DeclarativeBase, `starry_lyfe` schema constant | -- |
| `db/config.py` | Database and embedding settings from env vars | GNK |
| `db/engine.py` | Async engine, session factory, pgvector init, lifecycle | R5 |
| `db/models/canon_facts.py` | Tier 1: Canon Facts (immutable, seeded from YAML) | R5 |
| `db/models/character_baseline.py` | Tier 2: Character Baselines (immutable at runtime) | R5 |
| `db/models/dyad_state_whyze.py` | Tier 3: Dyad State Whyze (4 dyads, 5 dimensions) | R5 |
| `db/models/dyad_state_internal.py` | Tier 4: Dyad State Internal (6 dyads, Alicia-orbital persistence) | R5 |
| `db/models/episodic_memory.py` | Tier 5: Episodic Memories (pgvector embeddings, HNSW index) | R5 |
| `db/models/open_loop.py` | Tier 6: Open Loops (TTL, resolution, expiry) | R5 |
| `db/models/transient_somatic.py` | Tier 7: Transient Somatic State (exponential decay) | R5 |
| `db/decay.py` | Exponential decay pure function for Tier 7 | -- |
| `db/embed.py` | EmbeddingService protocol + LM Studio implementation (OpenAI-compatible `/v1/embeddings`) | BD-1 |
| `db/seed.py` | Canon YAML to DB seeding pipeline (Tiers 1-4, 7) | R5, GNK |
| `db/retrieval.py` | Per-tier retrieval API with read-time decay | R5 |

### `src/starry_lyfe/context/` -- Context Assembly (Phase 3)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `context/assembler.py` | Seven-layer prompt assembly with terminal constraint anchoring | -- |
| `context/budgets.py` | Per-layer budgets, kernel scaling, scene profiles, token estimation | -- |
| `context/constraints.py` | Layer 7 character pillars and scene-gated constraint blocks | -- |
| `context/kernel_loader.py` | Kernel/voice loading, section-aware compilation, cache | GNK |
| `context/layers.py` | Layer formatters, VoiceMode selection, and scene block formatting | -- |
| `context/prose.py` | Dramaturgical prose renderers for canon, dyads, protocols, and somatic state | -- |
| `context/soul_cards.py` | Soul-card activation and formatting | -- |
| `context/types.py` | Shared dataclasses and enums for assembly, scenes, and voice modes | -- |

### `src/starry_lyfe/validation/` -- Whyze-Byte (Phase 4)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `validation/whyze_byte.py` | Two-tier response validator with AI-ism, framework-leak, repetition, and hand-off checks | -- |
| `validation/fidelity.py` | Positive fidelity rubrics (Phase F-Fidelity); 7 dimensions × 4 characters = 28 rubrics | -- |

### `src/starry_lyfe/scene/` -- Scene Director (Phase 5)

| Module | Purpose |
|--------|---------|
| `scene/classifier.py` | `classify_scene()` — rule-based `SceneState` builder from caller inputs; auto-appends Whyze, normalizes `recalled_dyads` |
| `scene/next_speaker.py` | `select_next_speaker()` — Talk-to-Each-Other Mandate scoring; `DyadStateProvider` Protocol; `build_dyad_state_provider()` |
| `scene/errors.py` | `AliciaAwayContradictionError` |

### `src/starry_lyfe/dreams/` -- Dreams Engine (Phase 6)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `dreams/runner.py` | `run_dreams_pass()` — iterates all 4 characters, runs 5 generators, aggregates | BD-1 |
| `dreams/daemon.py` | apscheduler daemon; `python -m starry_lyfe.dreams` entry point | -- |
| `dreams/config.py` | `DreamsSettings` / `.from_env()` | GNK |
| `dreams/llm.py` | `BDOne` (OpenRouter/Anthropic HTTP client) + `StubBDOne` (test double) | BD-1 |
| `dreams/consolidation.py` | Somatic decay, overnight dyad delta cap (±0.10), loop expiry/resolution | R5 |
| `dreams/alicia_mode.py` | `pick_alicia_communication_mode()` — samples phone/letter/video per canonical distribution | -- |
| `dreams/generators/diary.py` | LLM-backed per-character diary entry generator | BD-1 |
| `dreams/generators/schedule.py` | Deterministic daily schedule from `routines.yaml` | -- |
| `dreams/generators/off_screen.py` | LLM-backed off-screen event generator | BD-1 |
| `dreams/generators/open_loops.py` | LLM-backed open loop generator | BD-1 |
| `dreams/generators/activity_design.py` | LLM-backed activity design generator | BD-1 |

### `src/starry_lyfe/api/` -- HTTP Service (Phase 7)

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `api/app.py` | `create_app()` FastAPI factory + lifespan | -- |
| `api/main.py` | `main()` uvicorn entry point | -- |
| `api/config.py` | `ApiSettings` — host, port, API key, crew max, BD-1 probe toggle | GNK |
| `api/endpoints/chat.py` | `chat_completions()` — POST `/v1/chat/completions` SSE | -- |
| `api/endpoints/metrics.py` | `MetricsMiddleware` + GET `/metrics` Prometheus | MSE-6 |
| `api/routing/character.py` | `resolve_character_id()` — model field → inline override → header → default | -- |
| `api/routing/msty.py` | `preprocess_msty_request()` — Crew roster + prior response extraction; `MstyPreprocessed` | -- |
| `api/orchestration/pipeline.py` | `run_chat_pipeline()` — 12-step flow; `_run_crew_turn()` — multi-speaker SSE loop | -- |
| `api/orchestration/post_turn.py` | `schedule_post_turn_tasks()` — fire-and-forget memory extraction + relationship update | -- |
| `api/orchestration/relationship.py` | `evaluate_and_update()` — per-turn Whyze-dyad delta (±0.03 cap); LLM-primary with heuristic `_propose_deltas()` fallback; `_clamp_delta` + `_bound01` shared with Phase 9 | -- |
| `api/orchestration/relationship_prompts.py` | `RELATIONSHIP_EVAL_SYSTEM` (hand-authored, per-character register notes); `build_eval_prompt()`; `parse_eval_response()`; `RelationshipEvalResponse`; `_NumericValue` + `_reject_bool` Pydantic primitives shared with Phase 9 — Phase 8 authored by Claude AI 2026-04-15 | -- |
| `api/orchestration/internal_relationship.py` | `evaluate_and_update_internal()` — per-turn inter-woman dyad delta (Phase 9, ±0.03 cap, 5 dimensions); LLM-primary with heuristic `_propose_internal_deltas()` fallback; Alicia-orbital active-gate at SQL boundary | -- |
| `api/orchestration/internal_relationship_prompts.py` | `INTERNAL_RELATIONSHIP_EVAL_SYSTEM` (hand-authored, 6 per-pair register notes); `build_internal_eval_prompt()` with `html.escape` injection defense; `parse_internal_eval_response()` with `isinstance(raw, dict)` fail-closed guard; `InternalRelationshipEvalResponse` 5-field Pydantic schema; `CANONICAL_DYAD_KEYS` + `ALICIA_ORBITAL_DYAD_KEYS` frozensets — Phase 9 authored by Claude AI 2026-04-15 | -- |
| `api/orchestration/memory_extraction.py` | `extract_episodic()` — post-turn episodic memory extraction | BD-1 |
| `api/orchestration/session.py` | `upsert_session()` — `chat_sessions` table management | R5 |
| `api/schemas/chat.py` | OpenAI-compatible request/response schemas | -- |

### Canon YAML Files

| File | Contents |
|------|----------|
| `characters.yaml` | 4 characters (Adelia, Bina, Reina, Alicia) + operator (Whyze) |
| `pairs.yaml` | 4 pairs (Entangled, Circuit, Kinetic, Solstice) |
| `dyads.yaml` | 10 dyads (6 inter-woman + 4 Whyze) + 7 memory tier definitions |
| `protocols.yaml` | 13 named protocols (12 Vision section 7 + Warlord Mode) |
| `interlocks.yaml` | 6 cross-partner interlocks |
| `voice_parameters.yaml` | Per-character temperature, thinking effort, sampling |

## Data Model

Seven memory tiers in PostgreSQL schema `starry_lyfe`:

| Tier | Table | Mutability | Row Count |
|------|-------|-----------|-----------|
| 1 | `canon_facts` | Immutable | N (flattened canon) |
| 2 | `character_baselines` | Immutable at runtime | 4 |
| 3 | `dyad_state_whyze` | Mutable (episodic extraction) | 4 |
| 4 | `dyad_state_internal` | Mutable (episodic extraction) | 6 |
| 5 | `episodic_memories` | Mutable (grows, decays) | Variable |
| 6 | `open_loops` | Mutable (TTL expiry) | Variable |
| 7 | `transient_somatic_states` | Mutable (exponential decay) | 4 |

## Infrastructure

- Python 3.11+, Pydantic v2, SQLAlchemy 2.0+ async, asyncpg, pgvector
- PostgreSQL 16 via Docker (pgvector/pgvector:pg16)
- Alembic for migrations
- mypy --strict, ruff, pytest, pytest-asyncio
- Embedding via LM Studio OpenAI-compatible `/v1/embeddings` endpoint (`text-embedding-nomic-embed-text-v1.5`, 768 dimensions)
