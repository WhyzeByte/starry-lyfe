# Phase G: Dramaturgical Prose Rendering With Per-Character Templates

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase G
**Phase identifier:** `G`
**Depends on:** Phase 0, A, A', A'', B, C, D (SHIPPED), E (SHIPPED), F (SHIPPED 2026-04-13)
**Blocks:** Phase J.1-J.4 (per-character remediation), Phase H (regression tests)
**Status:** SHIPPED 2026-04-13
**Last touched:** 2026-04-13 by Claude AI (direct execution under Project Owner authorization)

---

## How to read this file

Single canonical record for Phase G. All four agents read and append. Scroll to the Handshake Log for current state.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-13 | Claude AI | Project Owner | Phase G executed and shipped under Project Owner "Continue" authorization following Phase F QA. 237 tests pass. ruff and mypy clean. Samples regenerated. |

---

## Phase G Specification

### Vision authority
- Vision §9 Success Criteria — "Response quality: responses feel like a real person, not a helpful assistant with a persona layer"
- Vision §7 Behavioral Thesis — "Biological limits" and per-character protocol states
- Implementation Plan §4 Phase G

### Problem statement

After Phase F, Layers 2, 4, and 6 still render structured data as flat output:

- **Layer 2** — `- full_name: Adelia Raye` (key-value list)
- **Layer 4** — `Fatigue: 0.38 / Stress residue: 0.22` (raw numeric)
- **Layer 6** — `Relationship with Whyze (entangled): trust=0.92, intimacy=0.90` (raw numeric)

The model receives correct data but in a format that the model must interpret before acting. Per-character voiced prose delivers the same information in a register the model can inhabit immediately.

### Decision

Per-character prose renderers, one register per character, for three dimensions:

1. **Dyad prose** (Whyze-dyad + internal-dyad) — trust, intimacy, conflict, tension rendered in character voice
2. **Somatic prose** — fatigue, stress residue rendered in character voice; active protocols voiced
3. **Canon facts** — flat list converted to compact narrative paragraph

Both prose AND parenthesized numeric block in all Layer 4 and Layer 6 output. Layer 2 becomes narrative-only (no numeric block needed for identity facts).

### Per-character registers

| Register | Adelia | Bina | Reina | Alicia |
|---|---|---|---|---|
| Trust (high) | "Load-tested and reliable" | "Confirmed by repeated observation" | "Admissible without caveat" | "Body accepts without flinch" |
| Fatigue (high) | "Chemistry running on backup" | "Grid has given everything it had" | "Body has been spent, admissibility gate closing" | "Ni-grip is close, words have stopped working" |
| Conflict (low) | "Low friction in the system" | "Low conflict reading on the diagnostic" | "Minimal contested ground" | "Small tension in the air" |

### Files touched

- `src/starry_lyfe/context/prose.py` — new module (432 lines)
- `src/starry_lyfe/context/layers.py` — `format_canon_facts()`, `format_sensory_grounding()`, `format_scene_blocks()` updated to use prose renderers
- `src/starry_lyfe/context/assembler.py` — `format_canon_facts()` call updated with `character_id=character_id`
- `tests/unit/test_prose.py` — new test file (17 tests)
- `tests/unit/test_assembler.py` — 1 stale assertion updated (`"Relationship bina-reina"` → `"bina-reina"`)

---

## Step 1 + 2: Plan + Execute (Claude AI, direct authorization)

**Owner:** Claude AI under Project Owner "Continue" authorization
**Execution date:** 2026-04-13

### Work items completed

1. **Created `src/starry_lyfe/context/prose.py`** with:
   - `_trust_phrase()`, `_intimacy_phrase()`, `_conflict_phrase()`, `_tension_phrase()` — per-character threshold helpers
   - `render_dyad_whyze_prose()` — Whyze-dyad state as bracketed prose + `(trust= intimacy= conflict= tension=)` numeric block
   - `render_dyad_internal_prose()` — internal dyad state in focal character's voice register
   - `_fatigue_phrase()`, `_stress_phrase()` — per-character somatic helpers
   - `render_somatic_prose()` — fatigue/stress/injury as bracketed prose + `(fatigue= stress= injury=)` numeric block
   - `render_protocol_prose()` — named protocol (flat_state, post_race_crash, four_phase_return, whiteboard_mode, warlord_mode, bunker_mode) in character-voiced text
   - `render_canon_prose()` — canon fact list as narrative paragraph (e.g. "Bina Malek (The Sentinel). ISFJ-A, Si-dominant. Assyrian-Iranian Canadian, born Urmia, Iran. Red Seal mechanic. The Circuit Pair.")

2. **Updated `format_canon_facts()`** — added `character_id` parameter; when set, calls `render_canon_prose()` instead of flat list rendering. Fallback to flat list when `character_id` is absent (backward compat).

3. **Updated `format_sensory_grounding()`** — calls `render_somatic_prose()` for voiced prose + numeric block; calls `render_protocol_prose()` for named protocols with canonical fallback to protocol name.

4. **Updated `format_scene_blocks()`** — calls `render_dyad_whyze_prose()` for Whyze dyad; calls `render_dyad_internal_prose()` for internal dyads. Open loops unchanged.

5. **Updated `assembler.py`** — passes `character_id=character_id` to `format_canon_facts()`.

6. **Updated stale test** — `test_recalled_dyad_included_when_other_absent` updated: `"Relationship bina-reina"` → `"bina-reina"` to match new prose block format (`[bina-reina — Shield Wall. ...]`).

7. **Written `tests/unit/test_prose.py`** — 17 tests covering:
   - G1: four-character dyad prose distinctness + numeric block presence
   - G2: per-character somatic canonical phrases (grid/chemistry/admissibility/Ni-grip)
   - G3: bracketed prose + numeric block in Layer 6 outputs
   - G4: canon facts as narrative paragraph, not JSON blob
   - Protocol prose: flat_state (Bina), post_race_crash (Reina), four_phase_return (Alicia), whiteboard_mode (Adelia)
   - Reina+Alicia non-redundancy at prose level (admissibility vs body registers)

### Verification

- `pytest tests/unit -q` → **237 passed, 0 failed** (+17 Phase G tests)
- `ruff check src tests` → **All checks passed**
- `mypy src` → **Success: no issues found in 40 source files**

---

## Acceptance criteria

| AC | Description | Status |
|---:|---|---|
| AC-G1 | `prose.py` exists with all four public render functions | ✅ PASS |
| AC-G2 | Same canonical dyad state renders as four distinct prose strings | ✅ PASS (test_g1) |
| AC-G3 | Bina's somatic prose for fatigue>0.7 contains "grid" canonical phrase | ✅ PASS (test_g2) |
| AC-G4 | Layer 6 rendered output contains both bracketed prose and numeric block | ✅ PASS (test_g3) |
| AC-G5 | Canon facts Layer 2 renders as narrative paragraph, not key-value list | ✅ PASS (test_g4) |
| AC-G6 | Reina and Alicia dyad prose registers remain distinct (admissibility vs body) | ✅ PASS (non-redundancy test) |
| AC-G7 | Protocol prose renders voiced text for all six canonical protocols | ✅ PASS |
| AC-G8 | Phase F invariant tests still pass (no regressions) | ✅ PASS (237 total) |

---

## Closing Block

**Phase identifier:** G
**Final status:** SHIPPED 2026-04-13
**Total cycle rounds:** 1 (direct execution)
**Test delta:** +17 tests (220 → 237)
**Soul architecture impact:** Phase G activates the character-voiced prose layer for Layers 2, 4, and 6. The data retrieved from memory was always correct; Phase G ensures it reaches the model in a form the model can inhabit rather than interpret.
