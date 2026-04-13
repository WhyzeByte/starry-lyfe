# ADR-001: Voice Authority Split

**Status:** ACCEPTED
**Date:** 2026-04-13
**Context:** Phase I (Authority Split Resolution) of `IMPLEMENTATION_PLAN_v7.1.md`
**Decision makers:** Project Owner (Whyze), Claude AI, Claude Code

---

## Context

The Starry-Lyfe backend assembles a seven-layer prompt for each character. Layer 5 (Voice Directives) carries voice calibration data. The `Characters/{Name}/{Name}_Voice.md` files contain full User/Assistant exemplar pairs plus teaching prose for each character.

Two competing models were considered for where voice exemplar authority lives:

- **Option 1 (Backend-authoritative voice):** The backend carries abbreviated rhythm-calibration exemplars (1-2 sentence responses from Voice.md) as part of Layer 5. Msty's persona studio few-shots are either empty or canonically generated derivatives of the backend's exemplar set via a seed script.

- **Option 2 (Msty-authoritative voice):** The backend carries only meta-voice notes ("what this example teaches") in Layer 5. Msty's persona studio few-shots carry the full User/Assistant pairs and are the canonical rhythm source.

## Decision

**Option 1: Backend-authoritative voice.**

## Rationale

1. The Operating Model (IMPLEMENTATION_PLAN_v7.1.md section 1) is explicit: "Msty persona system prompts are blank or near-blank in production so the backend remains the sole source of character authority."
2. Option 1 keeps the canonical voice source in one place (`Voice.md` compiled into backend Layer 5) with no drift surface.
3. Option 2 creates two voice surfaces (backend meta-notes and Msty few-shots) and requires a separate drift-prevention mechanism to keep them synchronized.
4. The seed script (`scripts/seed_msty_persona_studio.py`) provides a canonical, reproducible path from Voice.md to Msty persona studio configuration, eliminating manual copy-paste drift.

## Consequences

- Phase E (Voice Exemplar Restoration) is authorized to add abbreviated exemplars to Layer 5.
- Voice.md files gain `<!-- mode: X, Y -->` tags and `**Abbreviated:**` sections as the single source of truth.
- `scripts/seed_msty_persona_studio.py` is the only canonical way to configure Msty persona studio few-shots.
- Any future Msty persona studio configuration must be derived from Voice.md via the seed script, not authored independently.

## Inapplicable work items

- **WI2 (Update `Docs/CHARACTER_CONVERSION_PIPELINE.md`):** N/A. File deleted 2026-04-12 by Project Owner directive as part of pre-v7 documentation cleanup.
- **WI3 (Update `Docs/Claude_Code_Handoff_v7.1.md` section 5.6):** N/A. File deleted 2026-04-12 by Project Owner directive. Section 5.6 was "Architecture hard rules" with no voice-specific subsection to update.
