# Changelog

All notable changes to the Starry-Lyfe backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Project skeleton: `pyproject.toml`, `Makefile`, requirements, `.env.example`, `.gitignore`
- Canon YAML single source of truth: `characters.yaml`, `pairs.yaml`, `dyads.yaml`, `protocols.yaml`, `interlocks.yaml`, `voice_parameters.yaml`
- Pydantic v2 schema models for all 6 YAML files with strict validation
- Canon loader (`loader.py`) with typed `Canon` dataclass
- Cross-file referential integrity validator (`validator.py`) with 11 check categories
- GitHub Actions Phase 1 gate workflow: `.github/workflows/phase1-gate.yml`
- v7.0 residue drift detection test (22 tokens from Handoff section 8.1)
- Em-dash/en-dash ban test for canon YAML
- Gate 1 verification test suite (23 tests)

### Fixed
- Aliyeh legacy name replaced with Bina across Alicia character files
- Alicia residence model aligned to resident-with-operational-travel across canon, tests, and handoff
- Claude Code handoff aligned to presence-conditional Alicia-orbital behavior
- Argentine geography diacritics: `Famaillá`, `Tucumán`
- Spanish institutional name diacritics: `Cancillería`, `Dirección`, `Ferretería`
- Reina's mother diacritics: `Mercè Benítez`
- Duplicate-member validation added to Dyad and Interlock schemas
- Cross-file validator extended: dyad-interlock refs, whyze-pair refs, recovery-architecture character refs
- Protocol inventory now enforces the Vision section 7 set plus explicitly source-tagged extensions only
