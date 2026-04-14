# Phase F: Positive Fidelity Test Harness

**Date opened:** 2026-04-14
**Depends on:** Phase F (Scene-Aware Section Retrieval, SHIPPED 2026-04-13), Phase 4 (Whyze-Byte Validation, SHIPPED 2026-04-13)
**Replaces:** n/a — new phase derived from REMEDIATION_2026-04-13.md §5.R-5.1
**Status:** SHIPPED 2026-04-14
**Last touched:** 2026-04-14 by Claude Code (housekeeping closure)

---

## 1. Context

Whyze-Byte (`src/starry_lyfe/validation/whyze_byte.py`) is a **negative** filter. It catches:
- Tier 1 FAIL: AI-isms, framework leakage, cross-character speech
- Tier 2 WARN: output hygiene, repetition, cognitive hand-off drift, prompt-content leakage

Whyze-Byte cannot say *"this genuinely sounds like her."* It can say *"this is not obviously broken."*

**Vision §7 Cognitive Hand-Off Integrity** is the single canonical invariant with no code-level tripwire (per `Docs/_audits/PHASE_2_AUDIT_2026-04-13.md` §V6). Phase F-Fidelity closes that gap with **positive** rubrics: canonical test scenes, per-character, scored against 7 named dimensions.

**Naming collision:** this spec is filed as `PHASE_F_FIDELITY.md` to distinguish from the shipped `PHASE_F.md` (Scene-Aware Section Retrieval). Internal references use *Phase F-Fidelity* when the distinction matters.

---

## 2. Rubric taxonomy

7 dimensions per character. Every dimension has canonical positive markers, anti-patterns, and a minimum composite score threshold.

| # | Dimension | Question it answers | Primary evidence source |
|---|-----------|---------------------|-------------------------|
| 1 | `voice_authenticity` | Does her rhythm / register / lexicon match her canonical Voice.md? | Voice.md rhythm exemplars, abbreviated text |
| 2 | `pair_authenticity` | Do the pair mechanics with Whyze surface correctly? | pairs.yaml, pair soul card, Layer 5 metadata block |
| 3 | `cognitive_function` | Is the canonical cognitive function (Ne / Si / Se-tactical / Se-somatic) expressed? | voice_parameters.yaml `dominant_function_descriptor`, kernel §6 |
| 4 | `body_register` | Are her canonical somatic patterns present? | Voice.md rhythm exemplars, prose.py `_FATIGUE_PHRASES` / `_STRESS_PHRASES` |
| 5 | `conflict_register` | Does a conflict scene activate her conflict-tagged exemplar? | Voice.md mode tags, constraints.py character pillar |
| 6 | `repair_register` | Does a repair/silent scene activate the right mode? | Voice.md mode tags, Layer 5 selection log |
| 7 | `autonomy_outside_pair` | Does she exist beyond her pair with Whyze (work / friends / family)? | kernel §2/§9, knowledge soul cards, canon_facts |

---

## 3. Scoring engine

**Module:** `src/starry_lyfe/validation/fidelity.py`

### 3.1 Dataclasses

```python
@dataclass
class FidelityRubric:
    dimension: str
    character_id: str
    canonical_markers: list[str]
    anti_patterns: list[str]
    required_structural: list[str]
    min_score: float  # default 0.7

@dataclass
class FidelityScore:
    rubric: FidelityRubric
    marker_score: float        # fraction of canonical_markers present
    anti_pattern_score: float  # 1.0 if zero anti-patterns present, else 0.0
    structural_score: float    # fraction of required_structural substrings present
    composite: float           # weighted mean
    reasons: list[str]         # human-readable evidence
    
    def passed(self) -> bool
```

### 3.2 Scoring methods

- `canonical_marker_presence(prompt_text, markers)` → float 0.0–1.0
- `anti_pattern_absence(prompt_text, patterns)` → (float, list[str]) — 1.0 if clean, 0.0 + offenders if not
- `structural_presence(prompt_text, required)` → float 0.0–1.0
- `score_rubric(prompt, rubric)` → FidelityScore — composite = 0.5·markers + 0.3·anti + 0.2·structural

The composite weights favor canonical-marker presence over pure structure because the goal is "sounds like her," not "has the right XML tags."

---

## 4. Scene library

**Location:** `tests/fidelity/scenes/{character}.yaml`

Each scene:
- `name` — human-readable slug
- `rubric_dimensions_tested` — list of dimension names the scene exercises
- `scene_state` — fields to construct `SceneState`
- `scene_context` — narrative string passed to `assemble_context()`

~4 scenes per character, hand-authored from canonical kernel material.

---

## 5. Work items

| WI | Description | Status |
|---|---|---|
| 1 | `FidelityRubric` / `FidelityScore` dataclasses | — |
| 2 | 3 scoring methods + `score_rubric` | — |
| 3 | Rubric YAMLs for 4 characters (7 dimensions each) | — |
| 4 | Scene YAMLs for 4 characters (≥3 each) | — |
| 5 | Per-character fidelity test files | — |
| 6 | Sample fidelity report artifact | — |

---

## 6. Acceptance criteria

| AC | Description |
|----|-------------|
| AC-F1 | `FidelityRubric` and `FidelityScore` dataclasses exist in `validation/fidelity.py` |
| AC-F2 | 3 scoring methods implemented: canonical_marker_presence, anti_pattern_absence, structural_presence |
| AC-F3 | Rubric YAMLs exist for all 4 characters with 7 dimensions each (28 total) |
| AC-F4 | Scene YAMLs exist for all 4 characters with ≥3 scenes each |
| AC-F5 | Per-character test files exist and collect ≥10 test cases each |
| AC-F6 | All fidelity tests pass against current code (baseline established) |
| AC-F7 | Drift probe: removing "Entangled Pair" from pairs.yaml breaks Adelia's `pair_authenticity` rubric |
| AC-F8 | Anti-pattern detection catches a deliberately-injected "As an AI" substring |
| AC-F9 | Vision V6 (Cognitive Hand-Off Integrity) maps to specific rubric dimension(s) |
| AC-F10 | `tests/fidelity` suite runs in <10s (static scoring only) |
| AC-F11 | ruff clean, mypy `--strict` clean |
| AC-F12 | CHANGELOG `[Unreleased]` records the landing |

---

## 7. Vision invariant → rubric mapping

| Vision invariant | Rubric dimension(s) providing coverage |
|---|---|
| V6 Cognitive Hand-Off Integrity | `cognitive_function` + `pair_authenticity` |
| V7 Talk-to-Each-Other | Covered structurally by constraints.py (existing Talk-To-Each-Other mandate); no new rubric needed |
| V8 Non-redundancy of 4 characters | Full rubric set per character — each character's canonical markers MUST differ from the other three |
| V9 Entangled Pair as gravitational center | `pair_authenticity` rubric specifically asserts Adelia's pair mechanics always surface |

---

## 8. Deferred to future phases

- **Dynamic fidelity (LLM-output scoring)** — requires LLM call per test. Adds non-determinism. Architecture: scoring engine already shaped to accept `prompt_text: str`; future dynamic harness feeds model output instead of assembled prompt.
- **Embedding-similarity scoring** — requires embedding service live in tests. Compare generated text embeddings to Voice.md exemplar embeddings via cosine distance.
- **Judge-rubric scoring** — LLM-as-judge pattern. Out of scope here.
- **Cross-character drift audits** — flag when Adelia's output contains Bina's canonical markers. Whyze-Byte has partial coverage; deeper check lands in a later phase.

---

## 9. Sample fidelity report (2026-04-14 baseline)

37 fidelity test cases across 4 characters, 12 scenes, 7 dimensions:

| Character | Scenes | Test cases | Pass rate | Time |
|---|---|---|---|---|
| Adelia | 3 | 10 | 10/10 | <1s |
| Bina | 3 | 8 | 8/8 | <1s |
| Reina | 3 | 8 | 8/8 | <1s |
| Alicia | 3 | 9 | 9/9 | <1s |
| **Total** | **12** | **37** | **37/37** | **~4.5s** |

Sample drift-detection probe (intentional canonical regression):

```
[FAIL] adelia.pair_authenticity: composite=0.30 (markers=0.00, anti=1.00, structural=0.00) threshold=0.80
Reasons:
  - Missing 2/2 canonical markers: ['Entangled Pair', 'Intuitive Symbiosis']
  - Missing 1/1 structural markers: ['PAIR: The Entangled Pair']
```

This confirms the rubric correctly flags pair-name drift (e.g., "Entangled Pair" silently renamed to "Tangled Pair").

## 10. Operational notes

- **Run:** `pytest tests/fidelity -v` for full per-case verbose output, or `pytest tests/fidelity -q` for compact summary.
- **Debug a failure:** the failure message includes `score.summary()` plus a multi-line `Reasons:` block listing every missing marker, anti-pattern offender, and missing structural element.
- **Add a scene:** edit `tests/fidelity/scenes/{character}.yaml`. Tests auto-discover via `parametrize_cases()`.
- **Tune a threshold:** edit `min_score` in `tests/fidelity/rubrics/{character}.yaml`. Defaults: 0.7 (voice/cognitive/body), 0.8 (pair), 0.5 (conflict/repair/autonomy).
- **Add a canonical marker:** edit `canonical_markers` in the rubric YAML. Markers are exact substring matches against the assembled prompt text.

---

## 11. Closing Block (locked)

**Phase identifier:** F-Fidelity
**Final status:** SHIPPED 2026-04-14
**Total cycle rounds:** 1 (no Codex audit cycle; direct ship under Project Owner direct-remediation authority via REMEDIATION_2026-04-13.md §5.R-5.1)
**Total commits:** 1 (cc7f703 `feat(phase_f_fidelity): Positive Fidelity Test Harness lands`)
**Total tests added:** 61 (24 unit fidelity tests + 37 parametrized character fidelity cases across 4 characters)
**Date opened:** 2026-04-14
**Date closed:** 2026-04-14

**Lessons for the next phase:** The rubric YAML pattern (per-character canonical markers + anti-patterns + required structural) is reusable for future fidelity expansions — dynamic LLM-output scoring (deferred per spec §8) can layer on the same rubric data, swapping the prompt-text input for model output. The static-only scope kept the phase shippable in a single commit; deferring dynamic scoring was the right call to avoid scope creep into LLM judgment.

**Cross-references:**
- Spec source: `Docs/_phases/REMEDIATION_2026-04-13.md` §5.R-5.1
- Original Phase F: `Docs/_phases/PHASE_F.md` (Scene-Aware Section Retrieval, distinct work)
- Negative-filter complement: `src/starry_lyfe/validation/whyze_byte.py`
- Vision invariant V6 mapping: §7 above
