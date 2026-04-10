# Starry-Lyfe v7.1 Architecture

**Version:** 0.2.0

## Overview

Starry-Lyfe is a character AI backend for four v7.1 persona kernels (Adelia Raye, Bina Malek, Reina Torres, Alicia Marin). Phase 1 (current) establishes the canon YAML single source of truth with Pydantic v2 validation and drift prevention. Planned later phases will add: memory service (Phase 2), context assembly (Phase 3), Whyze-Byte validation (Phase 4), scene director (Phase 5), Dreams engine (Phase 6), and HTTP service on port 8001 (Phase 7).

## Module Registry

### `src/starry_lyfe/canon/` -- Single Source of Truth

| Module | Purpose | Protocol Droid |
|--------|---------|---------------|
| `canon/__init__.py` | Package marker | -- |
| `canon/loader.py` | Load YAML files through Pydantic schemas; `load_all_canon()` returns typed `Canon` object | GNK (config) |
| `canon/validator.py` | Cross-file referential integrity; count assertions; CLI entry point | GNK (config) |
| `canon/schemas/__init__.py` | Re-exports root schema models | -- |
| `canon/schemas/enums.py` | Shared StrEnum types: CharacterID, PairName, MBTIType, CognitiveFunction, ThinkingEffort, DyadType, DyadSubtype, PairCadence, InterlockType, ProtocolCategory | -- |
| `canon/schemas/characters.py` | `CanonCharacters` model: 4 characters + 1 operator | -- |
| `canon/schemas/pairs.py` | `CanonPairs` model: 4 Whyze-to-character pairs | -- |
| `canon/schemas/dyads.py` | `CanonDyads` model: 10 dyads + 7 memory tier definitions | -- |
| `canon/schemas/protocols.py` | `CanonProtocols` model: 12+ named protocols with Vision section 7 validation | -- |
| `canon/schemas/interlocks.py` | `CanonInterlocks` model: 6 cross-partner interlocks | -- |
| `canon/schemas/voice_parameters.py` | `CanonVoiceParameters` model: per-character inference parameters | -- |

### Canon YAML Files

| File | Contents |
|------|----------|
| `characters.yaml` | 4 characters (Adelia, Bina, Reina, Alicia) + operator (Whyze) |
| `pairs.yaml` | 4 pairs (Entangled, Circuit, Kinetic, Solstice) from Vision section 5 |
| `dyads.yaml` | 10 dyads (6 inter-woman + 4 Whyze) + 7 memory tier definitions |
| `protocols.yaml` | 13 named protocols (12 Vision section 7 + Warlord Mode) |
| `interlocks.yaml` | 6 cross-partner interlocks from Vision section 6 |
| `voice_parameters.yaml` | Per-character temperature, thinking effort, sampling parameters |

## Data Model

Phase 1 defines canonical structured data. Database schema (Phase 2) and context assembly (Phase 3) are pending.

## Infrastructure

- Python 3.11+, Pydantic v2, PyYAML
- mypy --strict, ruff, pytest
- Port 8001 (Phase 7)
- PostgreSQL + pgvector (Phase 2)
