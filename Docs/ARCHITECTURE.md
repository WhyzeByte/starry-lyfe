# Starry-Lyfe v7.1 Architecture

**Version:** 0.4.0
**Date:** 2026-04-13
**Status:** Concise architecture and module index. Canonical phase-completion status lives in `Docs/IMPLEMENTATION_PLAN_v7.1.md`.

## Overview

Starry-Lyfe is a character AI backend for four v7.1 persona kernels (Adelia Raye, Bina Malek, Reina Torres, Alicia Marin).

Current implementation covers:

- Phase 1: canon YAML
- Phase 2: memory service
- Phase 3: seven-layer context assembly
- Phase 4: Whyze-Byte validation

Planned later phases remain:

- Phase 5: Scene Director
- Phase 6: Dreams engine
- Phase 7: HTTP service on port 8001

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
| `db/embed.py` | EmbeddingService protocol + Ollama implementation | BD-1 |
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
- Embedding via Ollama API (nomic-embed-text, 768 dimensions)
