# PHASE 10: YAML Source-of-Truth Migration

**Status:** Step 1 APPROVED 2026-04-15 (revised 2026-04-15 to per-character perspective model + shared_canon.yaml + Dreams Consistency QA). Pending Phase 9 ship before Step 2 begins (10.0 may run in parallel — verification only).
**Authority:** Project Owner directive 2026-04-15. Vision v7.1 §A principle (architecture vs life separation). Anti-regeneration directive: *"If a soul_essence.py file is causing quality issues, then we can just edit that file. Rather than changing a YAML file, then regenerating a million things."*
**Quality gate:** Project Owner directive — *"We always default to the best outcome, quality, soul, and essence of the system over time/speed/budget."* This phase takes as long as it needs. No sub-phase ships until assembled prompts are bit-for-bit equivalent in soul content to the pre-migration baseline.

**Scope:** Collapse the canonical character authoring surface from **17 files to 6**. The 5 rich character YAMLs (`adelia_raye.yaml`, `bina_malek.yaml`, `reina_torres.yaml`, `alicia_marin.yaml`, `shawn_kroon.yaml`) plus 1 cross-character anchor file (`shared_canon.yaml`) become the runtime-authoritative source. Markdown kernels, Voice files, Knowledge Stacks, Pair files, the 6 narrow canon YAMLs, `soul_essence.py`, and the 15 hand-authored soul card markdowns all retire as authoring surfaces. Runtime loaders read YAML directly. No generators. No `build/` directory. No compilation step.

**Architectural principle:** Each character's YAML carries **HER VOICE** on every relationship she is in. Two women in the same relationship hold two perspectives on it — and divergence between those perspectives is **dramaturgically required**, not a bug. Bina's read on the marriage is not Reina's read on the marriage. Authoring drift is the immersion. Factual contradiction is the bug. The two are distinguished by which YAML the content lives in: perception lives in the per-character YAML; fact lives in `shared_canon.yaml`.

---

## Step 1 — Plan

### 1.1 What "6 files" actually means

Two distinct content categories, two distinct homes:

**Per-character perspective YAMLs (5 files):** each woman's YAML carries her own POV on every shared concept she is part of. Whyze's YAML carries his POV on each pair.

| YAML | Carries (perspective blocks) |
|---|---|
| `adelia_raye.yaml` | her kernel, voice, knowledge, soul; HER POV on Entangled Pair; HER POV on adelia×bina, adelia×reina, adelia×alicia |
| `bina_malek.yaml` | her kernel, voice, knowledge, soul; HER POV on Circuit Pair; HER POV on bina×adelia, bina×reina, bina×alicia |
| `reina_torres.yaml` | her kernel, voice, knowledge, soul; HER POV on Kinetic Pair; HER POV on reina×adelia, reina×bina, reina×alicia |
| `alicia_marin.yaml` | her kernel, voice, knowledge, soul; HER POV on Solstice Pair; HER POV on alicia×adelia, alicia×bina, alicia×reina |
| `shawn_kroon.yaml` | his kernel, operator profile, factual_self/runtime continuity layers; HIS POV on Entangled, Circuit, Kinetic, Solstice |

That gives 12 inter-woman perspective blocks across 4 YAMLs covering 6 actual relationships, and 8 pair perspective blocks (4 women × her pair + 4 of Whyze's POVs) covering 4 actual pairs. Two perspectives per relationship, by design.

**Shared canon YAML (6th file):** the small set of objective facts that are not anyone's perspective — they are what happened.

| YAML | Carries |
|---|---|
| `shared_canon.yaml` | Marriage anchors (Bina×Reina date + canonical scene); chosen-family origin events (the bay-door scene where Adelia walked Reina through; samovar chai moment; Alicia's arrival into the family); Gavin's biological/legal parents; joint property facts; canonical timeline anchors that must not drift |

`shared_canon.yaml` is intentionally small. If a piece of content can be written in either woman's voice with subjective coloring, it does NOT belong in `shared_canon` — it belongs in each per-character YAML. `shared_canon` is reserved for content where divergence would be a continuity bug.

### 1.2 What retires and where it goes

| Current artifact | Retires to | Notes |
|---|---|---|
| `Characters/{Name}/{Name}_v7.1.md` (4 files) | per-character YAML `kernel_sections` | focal character |
| `Characters/{Name}/{Name}_Voice.md` (4 files) | per-character YAML `voice.few_shots.examples` | focal character |
| `Characters/{Name}/{Name}_Knowledge_Stack.md` (4 files) | per-character YAML `knowledge_stack` | focal character |
| `Characters/{Name}/{Name}_<Pair>_Pair.md` (4 files) | focal woman's `pair_architecture.her_pov` + Shawn's `pairs[<pair_name>].his_pov` + objective scene anchors to `shared_canon.yaml` | split per §1.1 |
| `Characters/Shawn/*.md` | `shawn_kroon.yaml` | Shawn |
| `src/starry_lyfe/canon/characters.yaml` | per-character YAML `identity` blocks | focal character |
| `src/starry_lyfe/canon/pairs.yaml` | each woman's `pair_architecture.her_pov` + Shawn's `pairs[*].his_pov` + objective pair-classification anchors to `shared_canon.yaml` | split |
| `src/starry_lyfe/canon/dyads.yaml` | each woman's `relationships.{other_id}` (per-POV) + objective dyad anchors to `shared_canon.yaml` | split |
| `src/starry_lyfe/canon/protocols.yaml` | per-character YAML `behavioral_framework.state_protocols` | character whose protocol it is |
| `src/starry_lyfe/canon/interlocks.yaml` | each woman's `pair_architecture.her_pov.cognitive_interlock` + Shawn's `pairs[*].his_pov.cognitive_interlock` | split |
| `src/starry_lyfe/canon/voice_parameters.yaml` | per-character YAML `voice.inference_parameters` | focal character |
| `src/starry_lyfe/canon/soul_essence.py` (45 blocks) | per-character YAML `soul_substrate` + `intimacy_blocks` | focal character |
| `src/starry_lyfe/canon/soul_cards/*.md` (15 cards) | per-character YAML `pair_architecture.her_pov.soul_card` (4 pair) + `knowledge_stack.cards` (11 knowledge) | focal character |

Total artifacts retired: **17 character files + 6 narrow canon YAMLs + 1 Python module + 15 soul card markdowns = 39**. Net source-file count after migration: **6**.

### 1.3 Schema additions (gaps from current rich YAMLs)

| Block | Source phase | Owner YAMLs |
|---|---|---|
| `relationships.{other_character_id}` (per-POV trust/intimacy/conflict/repair register, lived mechanics, signature scenes from her POV) | Phase 10 + Phase 9 | each per-character YAML, 3 blocks each |
| `pair_architecture.her_pov` (women) / `pairs[<pair_name>].his_pov` (Shawn) | Phase 10 | each woman + Shawn |
| `voice.few_shots.examples[].mode` (closed enum) | Phase E | all 4 women |
| `voice.few_shots.examples[].communication_mode` | Phase A'' | Alicia primary; others tagged `in_person` default |
| `behavioral_framework.constraint_pillars[mode]` (4-variant for Alicia) | Phase A'' | Alicia |
| `runtime.kernel_budget_scaling` (1.05/1.20/1.15/0.85) | Phase B | per character |
| `runtime.scene_profiles` | Phase F | per character; defaults inherited from system |
| `runtime.scene_type_section_promotions` | Phase F | per character |
| `pair_architecture.her_pov.dramaturgical_prose_templates` | Phase G | each woman |
| `behavioral_framework.somatic_prose_templates` | Phase G | per character |
| `evaluator_register.whyze_dyad` | Phase 8 | per character |
| `evaluator_register.internal_dyads[]` | Phase 9 | each woman, her POV on each of her 3 internal dyads |
| `preserve_markers[].content_anchor` enforcement metadata | Phase 10.6 | all 6 |
| `shared_canon.yaml` schema (anchors, scenes, timelines, gavin_parents, marriage_record) | Phase 10 | new file |

### 1.4 Fact vs perception classification rules

Phase 10.0 audits existing canonical content and routes each item by these rules:

**FACT (lives in `shared_canon.yaml`)** — content where divergence between two YAMLs would create a continuity contradiction:
- Dates of canonical events (Bina×Reina marriage date)
- Identity of canonical scenes (the bay-door scene is the bay-door scene; both women refer to it)
- Genealogy and legal facts (Gavin's biological/legal parents)
- Shared property facts (who lives at the property, address, layout)
- Timeline anchors (Adelia arrived in Canada in [year]; Reina was called to the bar in [year])

**PERCEPTION (lives in per-character YAML)** — content where two women holding different views is the immersion:
- Subjective read on the relationship state (trust level, intimacy temperature, current conflict)
- Lived mechanics from her POV ("how I fight with her", "what she gives me that no one else does")
- Signature scenes IN HER VOICE (the bay-door scene from Bina's POV vs Reina's POV)
- Cognitive interlock theory FROM HER ANGLE (Adelia describes the Entangled Pair like a generator describing its governor; Whyze describes it like an architect describing his expansion engine)
- Repair memory ("the August silence, two weeks in" — Bina remembers it sharper than Reina does)

**The same scene can have THREE entries:** (1) the objective anchor in `shared_canon.yaml` ("Reina walked through the bay door, August 2024, Adelia present"); (2) Bina's POV in `bina_malek.yaml.relationships.reina.signature_scenes` ("She gave me my life back, in a different shape than the one I was using before"); (3) Reina's POV in `reina_torres.yaml.relationships.bina.signature_scenes` (her body-read of the same moment). All three are canon. The first is what happened. The other two are what it means to each woman.

### 1.5 Sub-phase sequencing

| Sub-phase | Title | Type | Tests must remain | Risk |
|---|---|---|---:|---|
| 10.0 | Pre-flight gap audit + fact/perception classification | Verification only | 1113+ | Low |
| 10.1 | Schema + loader infrastructure (alongside existing) | Additive | 1113+ | Low |
| 10.2 | Loader cutover — kernel body + voice exemplars | Replacement | 1113+ | High |
| 10.3 | Loader cutover — soul essence + soul cards | Replacement | 1113+ | High |
| 10.4 | Loader cutover — narrow canon + constraints + evaluator prompts + shared_canon | Replacement | 1113+ | High |
| 10.5 | Archive retired sources + governance update | Cleanup | 1113+ | Low |
| 10.6 | Schema enforcement + regression re-baseline | Hardening | 1113+ | Medium |
| 10.7 | Dreams Consistency QA Pass | Additive (new Dreams generator) | 1113+ | Medium |

**Sequencing relative to Phase 9:** 10.0 may run in parallel with the Phase 9 audit cycle (no code changes). 10.1+ blocks on Phase 9 ship. Any Phase 9 remediation that touches `relationship_prompts.py` or `internal_relationship_prompts.py` updates the corresponding YAML `evaluator_register` block as part of the same fix from this point forward.

---

### Phase 10.0 — Pre-flight Gap Audit + Fact/Perception Classification

**Deliverable:** `Docs/_phases/PHASE_10_GAP_AUDIT.md` containing:
1. **Fidelity matrix** — every canonical phrase / preserve marker / voice example / knowledge node / behavioral axiom currently in the 17 markdown files + 6 narrow canon YAMLs + soul_essence.py + 15 soul cards, mapped to its target location in the 6 YAMLs. Missing items get an authoring item with target sub-phase.
2. **Fact/perception classification** per §1.4 rules. Every relationship-bearing item from the 4 Pair markdown files + dyads.yaml + interlocks.yaml + each character's relationship-mentioning kernel paragraphs gets routed to: (a) `shared_canon.yaml`, (b) per-character POV block, or (c) both (with the per-character POV being a re-voicing of the shared anchor).
3. **Per-character POV authoring inventory.** For each of the 12 inter-woman perspective blocks + 8 pair perspective blocks: list the canonical phrases, lived mechanics, and signature scenes that must appear in that POV from the existing source files.
4. v7.0 drift grep run against the 6 YAMLs (per Phase 0 spec, including REINA-audit-added drift terms).
5. preserve_marker `content_anchor` verbatim presence test against `soul_substrate` and section bodies.
6. List of all new schema blocks per §1.3 with concrete authoring items.

**Exit criteria:** Zero gaps unaccounted for. Zero drift. Every preserve marker anchor verbatim-present. Project Owner ratifies the fact/perception classification table.

**Files touched:** `Docs/_phases/PHASE_10_GAP_AUDIT.md` only. No code, no YAML edits.

---

### Phase 10.1 — Schema + Loader Infrastructure

**Deliverable:** Pydantic models + `load_rich_character()` + `load_shared_canon()` running alongside the existing loaders. Zero runtime integration.

**Work items:**
1. `src/starry_lyfe/canon/rich_schema.py` — Pydantic v2 models: `RichCharacter`, `Identity`, `SoulSubstrate`, `WorkAndWorld`, `KnowledgeStack`, `KnowledgeCard`, `BehavioralFramework`, `StateProtocol`, `ConstraintPillars`, `PairArchitectureHerPov` (women) / `PairArchitectureHisPov` (Shawn), `CognitiveInterlockPerspective`, `IntimacyArchitecture`, `RelationshipPerspective` (the per-character POV on a single inter-woman dyad), `Voice`, `FewShot`, `InferenceParameters`, `PreserveMarker`, `NormalizationNote`, `CanonFact`, `WhyzePartnerProfile`, `EvaluatorRegister`, `RuntimeConfig`, `ContinuityLayers` (Shawn-only).
2. `src/starry_lyfe/canon/shared_schema.py` — Pydantic v2 models for `SharedCanon`: `MarriageRecord`, `SignatureSceneAnchor`, `GenealogyFact`, `PropertyFact`, `TimelineAnchor`. Each scene anchor carries an `id` (e.g., `bay_door_2024`) referenced by per-character POV blocks.
3. `src/starry_lyfe/canon/rich_loader.py` — `load_rich_character(id) -> RichCharacter`, `load_all_rich_characters() -> dict[str, RichCharacter]`, `load_shared_canon() -> SharedCanon`. Pydantic validation on load. preserve_marker enforcement (`content_anchor` must appear verbatim in indicated body block).
4. **Cross-reference validator (NEW SHAPE)** — extended for the per-POV model:
   - Every `relationships.{X}` block in character A's YAML must have a matching `relationships.{A}` block in character X's YAML (perspective symmetry, NOT content symmetry — divergence is allowed and expected).
   - Every `signature_scenes[].anchor_id` referenced by a per-character POV block must resolve to an entry in `shared_canon.yaml`.
   - Every pair POV (`her_pov` in women, `his_pov` in Shawn) must resolve to a matching pair in `shared_canon.yaml.pairs`.
5. `tests/unit/test_rich_loader.py` — load all 6, schema-validate, exercise preserve_marker enforcement against synthetic violation, cross-reference validator passes on perspective symmetry, **assert at least one per-character POV pair is content-divergent (e.g., trust score differs by ≥0.05) to verify divergence-is-required is working**.

**Exit criteria:** All 6 YAMLs load and validate. preserve_marker enforcement passes. Cross-reference validator green on perspective symmetry. Divergence-required test passes. Existing 1113 tests remain green. Codex Round 1 audit pass.

**Files touched:**
- `src/starry_lyfe/canon/rich_schema.py` — new
- `src/starry_lyfe/canon/shared_schema.py` — new
- `src/starry_lyfe/canon/rich_loader.py` — new
- `tests/unit/test_rich_loader.py` — new

---

### Phase 10.2 — Loader Cutover: Kernel Body + Voice Exemplars

**Deliverable:** `kernel_loader.compile_kernel()` and `format_voice_directives()` read from rich YAML. Markdown kernel + Voice files no longer consulted at runtime.

**Work items:**
1. Replace `kernel_loader.compile_kernel(character_id, ...)` markdown read with `RichCharacter.compile_kernel_body(budget, scene_profile, promote_sections)`. Phase A structure-preserving algorithm operates on YAML `kernel_sections` block scalars. `<!-- PRESERVE -->` markers map to `preserve_markers` array.
2. Replace `format_voice_directives()` voice exemplar source with `RichCharacter.voice.few_shots.examples`. Mode-aware selection (Phase E) and communication-mode filtering (Phase A'') drive directly off YAML tags. `voice.inference_parameters` replaces `voice_parameters.yaml` lookup.
3. Cache key in `kernel_loader.py` keyed on rich YAML mtime.
4. Pair metadata block in Layer 5 (Phase D) sources from focal woman's `pair_architecture.her_pov` (or for Whyze-perspective scenes, from `shawn_kroon.yaml.pairs[<pair>].his_pov`). Objective pair classification anchors source from `shared_canon.yaml.pairs`.
5. Update fixtures in `test_kernel_loader.py`, `test_layers.py`, `test_assembler.py`.
6. Regenerate 4 sample assembled prompts at `Docs/_phases/_samples/PHASE_10_2_assembled_*_<date>.txt`.

**Exit criteria:** All 4 character samples assemble cleanly, terminal-anchored at `</WHYZE_BYTE_CONSTRAINTS>`. A5 pre-Whyze autonomy substrate present in all 4 outputs. A6 pair names present in soul essence AND pair soul card outputs (rendered from same YAML field — see §1.6). No PRESERVE marker leak. Load-bearing canonical phrases verbatim present. 1113+ tests green. Codex audit pass.

**Files touched:**
- `src/starry_lyfe/context/kernel_loader.py` — replace markdown read path
- `src/starry_lyfe/context/layers.py` — `format_voice_directives()`, pair metadata block source
- `tests/unit/test_kernel_loader.py`, `test_layers.py`, `test_assembler.py` — fixture updates
- `Docs/_phases/_samples/` — regenerated samples

---

### Phase 10.3 — Loader Cutover: Soul Essence + Soul Cards

**Deliverable:** Soul essence and soul card consumers read from rich YAML. `src/starry_lyfe/canon/soul_essence.py` and `src/starry_lyfe/canon/soul_cards/*.md` no longer consulted at runtime.

**Work items:**
1. Replace every `from starry_lyfe.canon.soul_essence import <BLOCK>` import with a call to `RichCharacter.soul_essence_text(block_id)` or equivalent accessor on the loaded model. The 45 blocks become methods/properties on `RichCharacter` returning the block scalar text from `soul_substrate` / `intimacy_blocks`.
2. `soul_essence_token_estimate(character)` reads YAML-sourced essence text rather than the Python module.
3. `find_activated_cards(character, scene_state)` iterates `RichCharacter.pair_architecture.her_pov.soul_card` (single pair card) + `RichCharacter.knowledge_stack.cards[]` (knowledge cards) using YAML `activation` blocks. Card `required_concepts` validation continues, sourced from YAML.
4. `format_soul_cards()` formatting unchanged; only the source iterator changes.
5. Effective Layer 1 ceiling formula `resolve_kernel_budget(character) + soul_essence_token_estimate(character)` continues to hold; both inputs now derive from rich YAML.
6. Regenerate 4 samples at `Docs/_phases/_samples/PHASE_10_3_assembled_*_<date>.txt`.

**Exit criteria:** Sample prompts identical (modulo whitespace) to Phase 10.2 samples. Per-character essence token counts within ±1% of pre-migration baselines. AC6 (revised per §1.6) holds. 1113+ tests green. Codex audit pass.

**Files touched:**
- `src/starry_lyfe/context/soul_cards.py` — source iterator
- All call sites of `soul_essence` imports (ripgrep-enumerate; estimated 8-15 sites)
- `src/starry_lyfe/context/budgets.py` — `soul_essence_token_estimate()`
- `tests/unit/test_soul_cards.py` — fixture updates
- `Docs/_phases/_samples/` — regenerated samples

---

### Phase 10.4 — Loader Cutover: Narrow Canon + Constraints + Evaluator Prompts + shared_canon

**Deliverable:** Remaining runtime consumers read from rich YAMLs + `shared_canon.yaml`. The 6 narrow canon YAMLs no longer consulted at runtime.

**Work items:**
1. `load_all_canon()` reads from rich YAMLs + `shared_canon.yaml` and constructs the 6 narrow canon Pydantic objects in memory. Existing narrow Pydantic schemas retain their validation surface; they get hydrated from a different source. Cross-reference validator (Phase 2 C3 remediation) re-runs against rich-YAML-hydrated objects.
2. `constraints.py` per-character Tier 1 axioms + constraint pillars source from `RichCharacter.behavioral_framework.tier_1_axioms` and `constraint_pillars[mode]`. Phase A'' Alicia 4-variant pillars driven directly from YAML.
3. Per-character state protocol triggers (Bina Flat State, Reina Post-Race Crash, Alicia Four-Phase Return + Sun Override, Adelia Whiteboard/Bunker/Warlord) source from `RichCharacter.behavioral_framework.state_protocols`.
4. Phase 8 `RELATIONSHIP_EVAL_SYSTEM` per-character register sections source from `RichCharacter.evaluator_register.whyze_dyad`.
5. Phase 9 `INTERNAL_RELATIONSHIP_EVAL_SYSTEM` 6 per-pair register sections source from each woman's `evaluator_register.internal_dyads[]`. Because each woman now carries her POV on each of her 3 internal dyads, the Phase 9 evaluator gets two register sections per dyad (one per POV) instead of a single shared one. **The evaluator becomes per-perspective:** it scores trust/intimacy/conflict/repair from the speaking woman's POV, not as a neutral observer.
6. Cognitive interlock theory (current `interlocks.yaml`) sources from each woman's `pair_architecture.her_pov.cognitive_interlock` + Shawn's `pairs[*].his_pov.cognitive_interlock`.
7. Layer 6 dyad rendering (Phase G) sources from the focal character's POV. When Bina is focal in a Bina+Reina scene, the rendered dyad block is BINA'S read of bina×reina, not a neutral merge. Reina's POV is loaded into the assembler context but rendered only if Reina becomes focal in a later turn.

**Exit criteria:** All 1113+ tests green. 4 samples for each focal character render that character's POV on present dyads (NOT the other character's). Whyze-Byte validator still enforces all 4 constraint pillar variants. Phase 8/9 LLM evaluator outputs structurally identical (with per-POV register sections). Codex audit pass.

**Files touched:**
- `src/starry_lyfe/canon/__init__.py` — `load_all_canon()` rewires; new `load_shared_canon()` integrated
- `src/starry_lyfe/context/constraints.py` — per-character source rewires
- `src/starry_lyfe/context/layers.py` — dyad rendering uses focal-character POV
- `src/starry_lyfe/api/orchestration/relationship_prompts.py` — register sections per-POV
- `src/starry_lyfe/api/orchestration/internal_relationship_prompts.py` — register sections per-POV (12 sections instead of 6)

---

### Phase 10.5 — Archive Retired Sources + Governance Update

**Deliverable:** Retired sources moved to `Archive/v7.1_pre_yaml/` with manifest. All governance docs updated.

**Work items:**
1. Move to `Archive/v7.1_pre_yaml/Characters/{Name}/`: all 16 character markdown files + Shawn's markdown sources.
2. Move to `Archive/v7.1_pre_yaml/canon/`: the 6 narrow canon YAMLs, `soul_essence.py`, `soul_cards/` directory.
3. `Archive/v7.1_pre_yaml/MANIFEST.md` — SHA256 of every archived file + the rich YAML field path (or `shared_canon.yaml` field path) that supersedes it.
4. `CLAUDE.md` Sacred Texts section: replace "Canonical character data" block with the 6 YAML files as authoritative; soul_essence.py / soul_cards / narrow canon YAML lines removed; add note that Vision Appendix B Document Map is updated.
5. `AGENTS.md` cycle rules updated for YAML-only authoring; per-character POV authoring is the new norm; explicit rule that divergence between two POVs on the same relationship is canonical, not a bug to fix.
6. `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3 Canon section: rich YAML + shared_canon declared as canonical source; Phase 10 record added to phase ledger.
7. `Docs/CHARACTER_CONVERSION_PIPELINE.md` retired or rewritten — under YAML-direct, there is no conversion pipeline; YAML *is* the canon.
8. `Vision/Starry-Lyfe_Vision_v7.1.md` Appendix B Document Map: per-character 4-file lines collapse to single YAML line per character + shared_canon line. v7.1 essence-vs-life principle preserved verbatim.
9. Step 5 QA checklist updated: AC6 per §1.6; new AC for divergence-is-canon; new AC for fact-lives-in-shared-canon-only.
10. `journal.txt` entry recording the migration.

**Exit criteria:** `grep -rn "_v7.1.md\|_Voice.md\|_Knowledge_Stack.md\|_Pair.md\|soul_essence\|soul_cards" src/ tests/` returns only Archive/MANIFEST references and historical Phase docs. Governance docs reflect YAML authority. Archive manifest committed and SHA256-verified. 1113+ tests green. Project Owner ratifies governance changes.

**Files touched:**
- `Archive/v7.1_pre_yaml/` — new tree (mass move)
- `CLAUDE.md`, `AGENTS.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, `Docs/CHARACTER_CONVERSION_PIPELINE.md`, `Vision/Starry-Lyfe_Vision_v7.1.md` Appendix B — governance updates
- `journal.txt` — entry

---

### Phase 10.6 — Schema Enforcement + Regression Re-baseline

**Deliverable:** Hardened invariants. Phase H regression bundle re-baselined against YAML-sourced output.

**Work items:**
1. **preserve_marker enforcement test** (`tests/unit/test_preserve_markers.py`): for each of 5 character YAMLs + shared_canon, every `content_anchor` in `preserve_markers` must appear verbatim in the assembled Layer 1 output for at least one realistic scene profile (or in the shared_canon-rendered Layer 2 for shared anchors). Test fails by named marker if a regression drops a load-bearing phrase.
2. **Voice mode coverage test** (`tests/unit/test_voice_mode_coverage.py`): assert per-character required mode coverage from Phase E (Adelia 6 incl. silent; Bina 5; Reina 7 incl. escalation; Alicia 6 incl. warm_refusal + group_temperature).
3. **Constraint pillar shape test** (`tests/unit/test_constraint_pillar_shape.py`): assert Alicia has all 4 communication-mode pillar variants; assert Adelia / Bina / Reina have at minimum the in_person variant.
4. **Cross-reference enforcement** (`tests/unit/test_cross_references.py`): every `relationships.{X}` in A's YAML matches a `relationships.{A}` in X's YAML (perspective symmetry); every `signature_scenes[].anchor_id` resolves in `shared_canon.yaml`; every pair POV resolves to a `shared_canon.yaml.pairs` entry.
5. **Divergence-required test** (`tests/unit/test_perspective_divergence.py`): for each of 6 inter-woman dyads, assert that the two POVs are content-divergent — at minimum, at least one of trust/intimacy/conflict/repair_history scores differs by ≥0.05 between POVs, AND at least one of the lived-mechanic prose blocks is non-identical. Identical POVs fail the test (drift in the wrong direction — toward agreeable mush).
6. **Fact-not-perception test** (`tests/unit/test_shared_canon_purity.py`): for each entry in `shared_canon.yaml`, assert no per-character YAML carries a contradicting value for the same field. Marriage date in `shared_canon` cannot be contradicted by a date in any character's YAML.
7. **Phase H regression bundle re-baselined** with YAML-sourced prompts. Hybrid methodology (deterministic anti-pattern grep + soul-fidelity assertion) re-verified.
8. **Phase 0 verification rewritten** to consume `normalization_notes` blocks directly from YAML and verify against rich YAML content. Markdown drift grep retired in favor of YAML drift grep.
9. `normalization_notes` ledger promoted to canonical drift record across all 6 YAMLs.

**Exit criteria:** All new tests pass for all 6 YAMLs. Phase H regression bundle baseline updated and green. Test count grows by ≥15 (was ≥10; per-perspective + shared_canon adds more). Step 5 QA full pass.

**Files touched:**
- `tests/unit/test_preserve_markers.py` — new
- `tests/unit/test_voice_mode_coverage.py` — new
- `tests/unit/test_constraint_pillar_shape.py` — new
- `tests/unit/test_cross_references.py` — new
- `tests/unit/test_perspective_divergence.py` — new
- `tests/unit/test_shared_canon_purity.py` — new
- `tests/regression/` — re-baselined Phase H bundle
- `scripts/phase_0_verification.py` — rewritten

---

### Phase 10.7 — Dreams Consistency QA Pass

**Deliverable:** Sixth Dreams content generator that runs nightly to detect drift between perspectives. Distinguishes healthy divergence (canonical, surfaced as scene fodder) from factual contradiction (operator-flagged for review).

**Architectural rationale:** Per-character POV authoring is the dramaturgically correct model, but it creates a new failure mode — over time, runtime updates via Phase 9 evaluator can drift each woman's perception state toward incoherence. Dreams already runs nightly for schedule, diary, off-screen, open loops, and activity design generation; adding a Consistency QA pass slots into the same REM cycle. This is the verification layer that makes per-character authoring safe long-term.

**Work items:**
1. **New Dreams generator** at `src/starry_lyfe/dreams/generators/consistency_qa.py`. Runs after the other 5 generators in the nightly pass. Reads from both static YAML POVs AND runtime `DyadStateInternal` rows for each character.
2. **Per-relationship coherence check** for each of:
   - 6 inter-woman dyads (adelia×bina, adelia×reina, adelia×alicia, bina×reina, bina×alicia, reina×alicia)
   - 4 woman-Whyze pairs (Entangled, Circuit, Kinetic, Solstice)
3. **Per-check LLM call** (BDOne-backed, same client pattern as Phase 8/9 evaluators):
   - Inputs: both POVs (static YAML perspective blocks + runtime DyadStateInternal numeric state + last 7 days of episodic memories that mention both parties)
   - Output schema (Pydantic-validated): `{verdict: "healthy_divergence" | "factual_contradiction" | "concerning_drift", divergence_summary: str, contradictions: list[Contradiction], scene_fodder: list[str]}`
   - `Contradiction` shape: `{field: str, pov_a_value: str, pov_b_value: str, severity: "low"|"medium"|"high", suggested_resolution: str}`
4. **Output routing:**
   - `healthy_divergence` → logged to `Docs/_dreams_qa/YYYY-MM-DD_consistency.md` under "Healthy divergence (the gap IS the story)" section. `scene_fodder` strings get written into shared open loops as potential scene seeds for the next time both women are present.
   - `concerning_drift` → logged under "Drift watch" section. No automatic action; surfaces in next Dreams pass for re-evaluation. If 3 consecutive nights flag the same drift, auto-promote to `factual_contradiction`.
   - `factual_contradiction` → logged under "Operator review required" section. Sends a notification (per existing Dreams notification path). Drift is BLOCKED from compounding by pinning each contradicting field at its last-coherent value until operator resolves.
5. **Anti-contamination** (per Phase 6 pattern): per-character system prompts when reading each POV. The QA judge LLM does NOT speak in any character's voice; it operates as a neutral observer.
6. **Dreams scheduler entry**: register in `src/starry_lyfe/dreams/__main__.py` apscheduler config; runs after content generators complete (typical: 03:30 local time).
7. **Operator-facing summary digest**: weekly rollup at `Docs/_dreams_qa/_weekly/YYYY-WW.md` consolidating each relationship's divergence trajectory (improving / stable / drifting).
8. **Test bundle** at `tests/unit/test_dreams_consistency_qa.py`: synthetic divergent POV fixtures must classify correctly as healthy; synthetic contradicting POV fixtures must classify correctly as factual_contradiction; LLM client mocked.
9. **Integration test** at `tests/integration/test_dreams_consistency_glue.py`: run nightly Dreams pass against fixture data, assert consistency QA output written, assert healthy-divergence scene fodder lands in open loops.

**Exit criteria:**
- Consistency QA generator implemented and registered in Dreams scheduler
- All 10 relationships (6 inter-woman + 4 pair) checked per nightly run
- Three verdicts (healthy_divergence / concerning_drift / factual_contradiction) all reachable in tests
- Anti-contamination per-character system prompts in place
- Weekly digest generated
- 1113+ tests green; ≥10 new tests added for consistency QA path
- Step 5 QA full pass on Phase 10 as a whole
- Project Owner ships Phase 10

**Files touched:**
- `src/starry_lyfe/dreams/generators/consistency_qa.py` — new
- `src/starry_lyfe/dreams/__main__.py` — register new generator
- `src/starry_lyfe/dreams/notifications.py` — extend for QA notifications
- `Docs/_dreams_qa/` — new output directory (git-ignored runtime data, structure committed)
- `Docs/_dreams_qa/_weekly/` — new
- `tests/unit/test_dreams_consistency_qa.py` — new
- `tests/integration/test_dreams_consistency_glue.py` — new

---

### 1.6 Updated invariant: AC6 (the only QA semantic change)

The Step 5 QA checklist item 6 originally read: *"A6 pair names present in BOTH soul essence AND soul cards (redundancy required)."* That rule was a defense against drift between two source files. Under YAML-direct, drift between source files for objective pair names is structurally impossible — both render from `shared_canon.yaml.pairs[<pair>].canonical_name`. The rule **evolves**:

> **AC6 (revised):** A6 pair names present in BOTH the soul essence Layer 1 output AND the pair soul card Layer 1 output of the assembled prompt, both rendered from the same `shared_canon.yaml.pairs[<pair>].canonical_name` field.

Same external invariant. Different source-layer enforcement.

### 1.7 Acceptance criteria (phase-level)

| AC | Description |
|---|---|
| AC-10.1 | All 5 rich character YAMLs + `shared_canon.yaml` load and Pydantic-validate |
| AC-10.2 | Cross-reference validator passes: perspective symmetry between every pair of women's `relationships.{X}` blocks; every `signature_scenes[].anchor_id` resolves in shared_canon; every pair POV resolves to shared_canon pair entry |
| AC-10.3 | preserve_marker enforcement test passes for all 6 YAMLs across scene profiles |
| AC-10.4 | All 6 narrow canon YAML files removed from runtime path; `load_all_canon()` reads from rich YAMLs + shared_canon |
| AC-10.5 | `soul_essence.py` removed from runtime path; soul essence text accessed via `RichCharacter` accessors |
| AC-10.6 | 15 soul card markdown files removed from runtime path; cards iterated from YAML blocks |
| AC-10.7 | All 17 character markdown files archived under `Archive/v7.1_pre_yaml/` with SHA256 manifest |
| AC-10.8 | Sample assembled prompts for all 4 women terminal-anchor at `</WHYZE_BYTE_CONSTRAINTS>` |
| AC-10.9 | A5 pre-Whyze autonomy substrate present in all 4 character runtime outputs |
| AC-10.10 | A6 pair names present in BOTH soul essence AND pair soul card outputs of assembled prompts (revised per §1.6, both rendered from `shared_canon.yaml.pairs[<pair>].canonical_name`) |
| AC-10.11 | No PRESERVE marker leak in any output |
| AC-10.12 | Load-bearing canonical phrases verbatim present (sourced from YAML `preserve_markers`) |
| AC-10.13 | Phase H regression bundle re-baselined and green against YAML-sourced output |
| AC-10.14 | Test baseline ≥1138 (1113 baseline + ≥15 new YAML-specific tests + ≥10 new Dreams Consistency QA tests) |
| AC-10.15 | Per-character soul essence token counts within ±1% of pre-migration values |
| AC-10.16 | Whyze-Byte validator enforces all 4 constraint pillar variants from YAML-sourced text |
| AC-10.17 | Phase 8 + Phase 9 LLM evaluator register sections rendered from per-character POV YAML; outputs structurally identical to pre-migration shape (with per-POV register sections — 12 internal dyad sections instead of 6) |
| AC-10.18 | Vision Appendix B Document Map updated; v7.1 essence-vs-life principle preserved verbatim |
| AC-10.19 | Zero `_v7.1.md` / `_Voice.md` / `_Knowledge_Stack.md` / `_Pair.md` / `soul_essence` / `soul_cards` references in `src/` or `tests/` (Archive references excepted) |
| AC-10.20 | `journal.txt` entry recorded |
| AC-10.21 | **Per-perspective divergence test passes** — each of 6 inter-woman dyads has at least one numeric score differing by ≥0.05 between POVs AND at least one non-identical lived-mechanic prose block. Identical POVs FAIL the test (drift toward agreeable mush is the regression). |
| AC-10.22 | **Fact-not-perception purity test passes** — no per-character YAML carries a value that contradicts a `shared_canon.yaml` field |
| AC-10.23 | **Layer 6 dyad rendering uses focal-character POV** — when Bina is focal, the rendered bina×reina block is BINA's read, not a neutral merge or Reina's read |
| AC-10.24 | **Dreams Consistency QA generator registered and running** in nightly Dreams pass; all 10 relationships (6 inter-woman + 4 pair) checked per night |
| AC-10.25 | **Three Dreams QA verdicts reachable in tests** — healthy_divergence, concerning_drift, factual_contradiction |
| AC-10.26 | **Healthy divergence outputs route to scene fodder** — fodder strings land in open loops as scene seeds for next time both women are present |
| AC-10.27 | **Factual contradiction blocks drift compounding** — contradicting fields pinned at last-coherent value until operator review; notification fires |
| AC-10.28 | **Weekly QA digest generated** at `Docs/_dreams_qa/_weekly/YYYY-WW.md` |

### 1.8 Risks and mitigations

| Risk | Mitigation |
|---|---|
| Rich YAMLs incomplete vs current canonical content | Phase 10.0 gap audit is the gate; nothing else moves until gaps closed and authored back into YAML |
| Fact/perception classification disputed | Phase 10.0 produces explicit table; Project Owner ratifies before Phase 10.1 begins |
| Per-character POVs accidentally written identical (drift toward agreeable mush) | AC-10.21 divergence-required test FAILS the build if POVs are identical — explicitly inverts the usual drift-detection direction |
| Per-character POVs drift into factual contradiction over time via runtime updates | Phase 10.7 Dreams Consistency QA pass detects nightly; pinning prevents compounding |
| Bina YAML at 1347 lines will grow further with new schema additions | Acceptable — large file is easier to maintain than 4 small files because cross-block cognitive distance disappears; YAML structural folding handles scrolling |
| Phase 9 in-flight | 10.0 runs in parallel; 10.1+ blocks on 9 ship; any Phase 9 remediation that touches evaluator prompts dual-updates YAML from this point forward |
| `soul_essence.py` Python imports scattered across codebase | Ripgrep-enumerate in Phase 10.3; convert each import site one at a time; tests catch regressions |
| Loss of file-level git blame on retired content | Archive preserves full history; git follows moves through `--follow` |
| Operator quality-edits a YAML field and discovers downstream code expected a specific shape | Pydantic validation catches schema drift; preserve_marker enforcement catches phrase drift |
| Phase 9 evaluator becomes per-POV (12 register sections instead of 6) — token budget impact | Each register section is shorter (single POV not dual); net token impact is neutral or slightly positive (per-POV register can be more focused) |
| Dreams Consistency QA LLM cost (10 checks per night per character) | Acceptable — runs during off-hours nightly cycle; no impact on request-time latency |
| Dreams QA flags a healthy divergence as factual contradiction (false positive) | Operator-review step is the final arbiter; pinning is reversible; no data is destroyed |

### 1.9 Out of scope (explicit)

- No changes to Vision §1-§7 (architecture content). Only Appendix B Document Map updates.
- No changes to `IMPLEMENTATION_PLAN_v7.1.md` §1-§9 (architectural sections). Only §3 Canon authority statement + Phase 10 ledger entry.
- No changes to PTF, behavioral axioms, or constraint pillar *content* (only their source location).
- No new character authoring work. Phase 10 is migration, not extension. (New characters or new exemplars handled in subsequent phases against the new YAML surface.)
- No retiring of `soul_essence.py` *concept* — soul essence remains a guaranteed-surcharge Layer 1 component per the §16 budget semantics. Only the *file* retires; the runtime function is preserved.
- No automated reconciliation of factual contradictions detected by Dreams Consistency QA. Operator review is the ONLY path to resolving a factual contradiction. Drift is pinned; nothing is silently rewritten.

### 1.10 Direct remediation reservation

Per CLAUDE.md direct remediation authority: any soul-bearing prose drift that surfaces during Phase 10.2 / 10.3 / 10.4 sample regeneration is handled by Claude AI direct edit to the appropriate YAML, not by cycle handoff. The YAML is now the canonical home for that prose; edits there are the cleanest possible remediation path. Note: per-character POV edits MUST stay within that character's YAML; if a remediation surfaces a contradicting fact, it is escalated to `shared_canon.yaml` and both POVs may need to be re-aligned around the new shared anchor.

---

## Step 2 — Execute

*Pending Phase 9 ship + Step 1 sign-off complete. 10.0 may begin in parallel with Phase 9 audit cycle.*

## Step 3 — Codex Audit (Round 1)

*Pending Step 2.*

## Step 4 — Remediation

*Pending Step 3.*

## Step 5 — Claude AI QA

*Pending Step 4.*

## Step 6 — Project Owner Ship

*Pending Step 5.*
