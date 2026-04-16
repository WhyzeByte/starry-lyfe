# Phase 10.0: Pre-flight Gap Audit + Fact/Perception Classification

**Date:** 2026-04-15
**Owner:** Claude Code (verification); Project Owner (ratification)
**Spec:** `Docs/_phases/PHASE_10.md` §Phase 10.0
**Status:** COMPLETE — awaiting Project Owner ratification of fact/perception classification

---

## 1. YAML Authoring Surface Inventory

Five rich per-character YAMLs exist (untracked in `Characters/`):

| File | Lines | Version | Top-level blocks |
|------|---:|---|---|
| `adelia_raye.yaml` | 1096 | `7.1-rich` | meta, identity, soul_substrate, work_and_world, voice, behavioral_framework, pair_architecture, intimacy_architecture, family_and_other_dyads, knowledge_stack, preserve_markers, normalization_notes |
| `bina_malek.yaml` | 1346 | `7.1-rich` | meta, identity, soul_substrate, work_and_world, voice, behavioral_framework, pair_architecture, intimacy_architecture, family_and_other_dyads, knowledge_stack, preserve_markers, normalization_notes |
| `reina_torres.yaml` | 1542 | `7.1-rich` | meta, identity, soul_substrate, work_and_world, voice, behavioral_framework, pair_architecture, intimacy_architecture, family_and_other_dyads, knowledge_stack, preserve_markers, normalization_notes |
| `alicia_marin.yaml` | 1384 | `7.1-rich` | meta, identity, soul_substrate, work_and_world, voice, behavioral_framework, pair_architecture, intimacy_architecture, family_and_other_dyads, knowledge_stack, preserve_markers, normalization_notes |
| `shawn_kroon.yaml` | 1996 | `4.2-rich` | meta, identity, soul_substrate, work_and_world, voice, behavioral_framework, pairs, family, knowledge_stack, preserve_markers, normalization_notes, continuity_layers |
| **Total** | **7364** | | |

**`shared_canon.yaml` does NOT exist yet.** Phase 10.1 must create a schema-valid skeleton. Content authoring per the fact/perception classification below.

---

## 2. v7.0 Drift Grep Results

**Scanner:** `tests/unit/test_residue_grep.py::test_v70_residue_repo_wide` with 25 extended tokens.

**Result: CLEAN** (5/5 tests pass as of commit `a407f9e`).

v7.0 tokens in Character YAMLs appear **exclusively inside `normalization_notes:` blocks** (audit trail of resolved legacy drift). The residue scanner's `_get_normalization_notes_lines()` function correctly excludes these blocks. Additional allowances:
- `sheismo` with Rioplatense/voseo context (Alicia's canon — real phonological feature)
- `Characters/shawn_kroon.yaml` in `EXCLUDED_PATHS` (deliberately v7.0 per Handoff §3)

**No residue scrub needed.** The v7.0 tokens are properly quarantined in audit-trail blocks.

---

## 3. Preserve Marker Verification

**Total markers across 5 YAMLs: 62**

| File | Markers | Exact pass | Prefix pass | FAIL |
|------|---:|---:|---:|---:|
| `adelia_raye.yaml` | 6 | 5 | 1 | 0 |
| `bina_malek.yaml` | 13 | 12 | 0 | **1** |
| `reina_torres.yaml` | 13 | 8 | 1 | **4** |
| `alicia_marin.yaml` | 12 | 9 | 1 | **2** |
| `shawn_kroon.yaml` | 18 | 16 | 0 | **2** |
| **Total** | **62** | **50** | **3** | **9** |

**53/62 pass (86%). 9 fail (14%).**

### 3.1 Failure Detail

#### bina_malek.yaml (1 failure)

| Marker ID | Anchor | Body | Root cause |
|---|---|---|---|
| `kernel_core_identity_paragraph` | "I am Bina Malek. Forty. First-generation Assyrian-Iranian Canadian..." | "I am Bina Malek. Forty. Red Seal mechanic..." | Opening rewritten to lead with profession. Heritage phrase moved to `heritage_reference` metadata field. |

#### reina_torres.yaml (4 failures — worst file)

| Marker ID | Anchor | Body | Root cause |
|---|---|---|---|
| `kernel_opening_declaration` | "I am Reina Torres. Thirty-six. Criminal defence lawyer, solo practice in Okotoks." | "I am Reina Torres. Barcelona born. Gracia raised." | Completely different opening structure. |
| `rafa_otra_vez` | "Every cortado was the same temperature..." | "Every cortado the same temperature..." | Multiple micro-drifts: `was` dropped, `When` → `If`, quotes removed around `otra vez`. |
| `complete_life_pre_whyze` | "I have a docket, a stable, a wife, a fight gym, and a city..." | "I have a docket. I have a stable. I have a wife..." | Comma-list restructured to anaphoric "I have" repetitions. |
| `the_knowing_changed_the_temperature` | "...The knowing has not made me a better lawyer in any technical sense. The knowing has made me sharper." | Same start but with extra sentence inserted and qualifier appended. | Prose expansion beyond marker anchor. |

#### alicia_marin.yaml (2 failures)

| Marker ID | Anchor | Body | Root cause |
|---|---|---|---|
| `kernel_lucia_vega_paragraph` | "...a young woman from a town an hour north of Famailla named Lucia Vega..." | "...was Lucia Vega, a young woman from a town an hour north of Famailla." | Name position shifted (fronted vs trailing). |
| `warmth_as_discipline` | "I am the sun in this household because I chose to be..." | "I am the sun in this household because I choose to be..." | Single-letter tense drift: `chose` (past) → `choose` (present). |

#### shawn_kroon.yaml (2 failures)

| Marker ID | Anchor | Body | Root cause |
|---|---|---|---|
| `challenger_dialogue_age_seven` | Uses single quotes, no periods: `'Yes'`, `'Most likely'` | Uses double quotes with periods: `"Yes."`, `"Most likely."` | Quote style + punctuation drift. |
| `i_stay_until_orbit` | `"I stay until orbit."` (lowercase) | `"I Stay Until Orbit."` (title case) | Casing mismatch. |

### 3.2 Recommended Resolution

Per CLAUDE.md §19 quality directive (canonical correctness > ship velocity), **the body text should be corrected to match the preserve_marker anchors** in all 9 cases. The anchors are the canonical source (hand-authored against source kernels); the body text is the drift. Two approaches:

- **5 prose rewrites** (Reina 4, Bina 1): the body text was intentionally rephrased during YAML authoring. Decision: either (a) restore the anchor wording in the body, or (b) update the anchor to match the new body wording if the body version is deemed superior. **Requires Project Owner / Claude AI judgment on which version to keep.**
- **4 micro-drifts** (Alicia 2, Shawn 2): mechanical errors (tense, casing, punctuation). Decision: fix the body to match the anchor. No judgment call needed.

**Authoring action items for Phase 10.1 gate:**

| # | File | Marker ID | Action | Owner |
|---|---|---|---|---|
| 1 | bina_malek.yaml | `kernel_core_identity_paragraph` | Restore "First-generation Assyrian-Iranian Canadian" in opening OR update anchor | Claude AI / PO |
| 2 | reina_torres.yaml | `kernel_opening_declaration` | Restore "Thirty-six. Criminal defence lawyer" opening OR update anchor | Claude AI / PO |
| 3 | reina_torres.yaml | `rafa_otra_vez` | Restore `was`, `When`, quoted `otra vez` OR update anchor to match body's tighter prose | Claude AI / PO |
| 4 | reina_torres.yaml | `complete_life_pre_whyze` | Restore comma-list form OR update anchor to match anaphoric form | Claude AI / PO |
| 5 | reina_torres.yaml | `the_knowing_changed_the_temperature` | Trim expansion to match anchor OR update anchor | Claude AI / PO |
| 6 | alicia_marin.yaml | `kernel_lucia_vega_paragraph` | Fix name position to match anchor (mechanical) | Claude Code |
| 7 | alicia_marin.yaml | `warmth_as_discipline` | Fix `choose` → `chose` (mechanical tense fix) | Claude Code |
| 8 | shawn_kroon.yaml | `challenger_dialogue_age_seven` | Fix quotes + periods to match anchor (mechanical) | Claude Code |
| 9 | shawn_kroon.yaml | `i_stay_until_orbit` | Fix title case → lowercase to match anchor (mechanical) | Claude Code |

---

## 4. Fact vs Perception Classification

Per `PHASE_10.md` §1.4 rules. This table classifies the relationship-bearing canonical content that must be routed to either `shared_canon.yaml` (objective fact) or per-character POV blocks (subjective perception).

### 4.1 FACT — lives in `shared_canon.yaml`

| Fact | Source | shared_canon field |
|------|--------|-------------------|
| Bina × Reina marriage date | `dyads.yaml` | `marriage.date` |
| Bay-door scene (Adelia walked Reina through) — objective event | Pair files + kernels | `signature_scenes[].id: bay_door_2024` |
| Samovar chai moment — objective event | Bina's kernel | `signature_scenes[].id: samovar_chai` |
| Alicia's arrival into the family — objective event | Alicia's kernel | `signature_scenes[].id: alicia_arrival` |
| Gavin's biological parents (Bina + donor) | `characters.yaml` | `genealogy.gavin.biological_parents` |
| Gavin's legal parents (Bina + Reina) | `characters.yaml` | `genealogy.gavin.legal_parents` |
| Property location: Foothills County near Priddis, Alberta | CLAUDE.md §18 | `property.location` |
| Property layout (main house, mezzanine, bay, garage apartment) | Kernels | `property.layout` |
| Adelia introduced Bina and Reina (2021) | CLAUDE.md §16 | `timeline.adelia_introduced_bina_reina` |
| 4 canonical pair names: Entangled, Completed Circuit, Kinetic, Solstice | `pairs.yaml` | `pairs[].canonical_name` |
| 6 canonical dyad keys + subtypes | `dyads.yaml` | (derived from per-character POV blocks) |
| Gavin's age: 7 | CLAUDE.md §18 | `genealogy.gavin.age` |

### 4.2 PERCEPTION — lives in per-character YAML

| Content type | Where it lives | Notes |
|---|---|---|
| Each woman's read on her trust/intimacy/conflict/repair with another woman | `{her}.yaml → relationships.{other}` | Two POVs per dyad; divergence is canonical |
| Lived mechanics from her POV ("how I fight with her") | `{her}.yaml → relationships.{other}.lived_mechanics` | Voice-specific |
| Signature scenes IN HER VOICE | `{her}.yaml → relationships.{other}.signature_scenes[]` | Same event, different emotional read |
| Cognitive interlock FROM HER ANGLE | `{her}.yaml → pair_architecture.her_pov.cognitive_interlock` | Same mechanism, different framing |
| Repair memory coloring | `{her}.yaml → relationships.{other}.repair_register` | Bina remembers sharper than Reina |
| Her soul essence blocks | `{her}.yaml → soul_substrate` | Non-transferable |
| Her voice exemplars | `{her}.yaml → voice.few_shots.examples[]` | Non-transferable |
| Her kernel body prose | `{her}.yaml → kernel_sections` (future 10.2) | Non-transferable |
| Her knowledge cards | `{her}.yaml → knowledge_stack.cards[]` | Non-transferable |
| Evaluator register notes (Phase 8 Whyze-dyad) | `{her}.yaml → evaluator_register.whyze_dyad` | Her voice on her relationship with Whyze |
| Evaluator register notes (Phase 9 inter-woman) | `{her}.yaml → evaluator_register.internal_dyads[]` | Her voice on each of her 3 inter-woman dyads |

### 4.3 BOTH (shared anchor + per-character POV)

| Content | shared_canon | per-character |
|---|---|---|
| Bay-door scene | Objective anchor: "Reina walked through the bay door, August 2024, Adelia present" | Bina's POV: her read of the moment. Reina's POV: her body-read of the same moment. |
| Marriage | Objective anchor: date, legal status | Bina's POV: load-bearing. Reina's POV: founding act. |
| Samovar chai | Objective anchor: the event itself | Bina's POV: "Shirin's way." |

---

## 5. Per-Character POV Authoring Inventory

### 5.1 Inter-woman perspective blocks (12 total)

Each woman carries 3 inter-woman POV blocks (one for each of her inter-woman dyads):

| Character | relationships.{X} blocks needed |
|---|---|
| Adelia | `relationships.bina`, `relationships.reina`, `relationships.alicia` |
| Bina | `relationships.adelia`, `relationships.reina`, `relationships.alicia` |
| Reina | `relationships.adelia`, `relationships.bina`, `relationships.alicia` |
| Alicia | `relationships.adelia`, `relationships.bina`, `relationships.reina` |

**Current YAML state:** All 4 women's YAMLs carry `family_and_other_dyads` or `intimacy_architecture` blocks with inter-woman relationship content. The exact field names may not yet match the Phase 10.1 schema (`relationships.{X}` key format). Schema mapping is a Phase 10.1 deliverable.

### 5.2 Pair perspective blocks (8 total)

| Character | Pair POV block |
|---|---|
| Adelia | `pair_architecture.her_pov` (Entangled Pair) |
| Bina | `pair_architecture.her_pov` (Completed Circuit Pair) |
| Reina | `pair_architecture.her_pov` (Kinetic Pair) |
| Alicia | `pair_architecture.her_pov` (Solstice Pair) |
| Shawn | `pairs.entangled.his_pov`, `pairs.circuit.his_pov`, `pairs.kinetic.his_pov`, `pairs.solstice.his_pov` |

**Current YAML state:** All 4 women carry `pair_architecture` blocks. Shawn carries `pairs` with per-pair entries. Schema mapping is a Phase 10.1 deliverable.

### 5.3 Schema blocks not yet present in YAMLs (gaps for 10.1 schema)

| Block | Present? | Notes |
|---|---|---|
| `relationships.{X}` (explicit key per other character) | Partial — content exists under `intimacy_architecture` / `family_and_other_dyads` but not keyed by character ID | Schema 10.1 must define the mapping |
| `evaluator_register.whyze_dyad` | Not present in any YAML | Phase 10.4 will populate from `relationship_prompts.py::RELATIONSHIP_EVAL_SYSTEM` |
| `evaluator_register.internal_dyads[]` | Not present in any YAML | Phase 10.4 will populate from `internal_relationship_prompts.py::INTERNAL_RELATIONSHIP_EVAL_SYSTEM` |
| `runtime.kernel_budget_scaling` | Not present | Phase 10.2 will populate from `budgets.py` |
| `runtime.scene_profiles` | Not present | Phase 10.2 will populate from scene-type infrastructure |
| `shared_canon.yaml` | File does not exist | Phase 10.1 creates skeleton; content authoring per §4 classification above |

---

## 6. Summary + Gate Decision

### Completeness

- **62 preserve_markers** catalogued; **53 pass** (86%); **9 require remediation** (4 mechanical fixes by Claude Code, 5 voice-judgment calls by Claude AI / Project Owner)
- **v7.0 drift:** CLEAN (normalization_notes exclusion pattern verified)
- **Fact/perception classification:** Drafted above — **awaiting Project Owner ratification**
- **POV inventory:** 12 inter-woman + 8 pair = 20 perspective blocks identified; content exists in YAMLs under variant key names; schema mapping is Phase 10.1 scope
- **Schema gaps:** 6 blocks not yet present in YAMLs (evaluator_register, runtime, shared_canon) — all are Phase 10.1+ scope, content derived from existing source code

### Gate Recommendation

Phase 10.0 exit criteria per `PHASE_10.md §Phase 10.0`:

| Criterion | Status |
|---|---|
| Zero gaps unaccounted for | **MET** — all 6 gap blocks identified with source derivation path |
| Zero drift | **MET** — residue scanner clean |
| Every preserve marker anchor verbatim-present | **NOT MET** — 9/62 fail; 4 mechanical (Claude Code fixable), 5 voice-judgment (Claude AI/PO) |
| Project Owner ratifies fact/perception table | **PENDING** — table drafted, awaiting ratification |

**Recommendation:** Proceed with Phase 10.1 schema + loader infrastructure work in parallel with the 9 preserve_marker remediation items. The 4 mechanical fixes can be committed before 10.1 ships. The 5 voice-judgment items need Claude AI / Project Owner input and can be resolved before the 10.2 kernel cutover (which is when preserve_markers become load-bearing at runtime).
