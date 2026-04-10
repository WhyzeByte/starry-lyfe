# Changelog

All notable changes to the Starry-Lyfe backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
