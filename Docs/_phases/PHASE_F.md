# Phase F: Scene-Aware Section Retrieval + Cross-Cutting Modifiers

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase F
**Phase identifier:** `F`
**Depends on:** Phase 0, A, A', A'', B, C, D (SHIPPED 2026-04-12), E (SHIPPED 2026-04-13)
**Blocks:** Phase J.1-J.4 (character remediation passes), Phase G (downstream integration)
**Status:** IN PROGRESS - direct remediation complete, awaiting QA
**Last touched:** 2026-04-13 by Codex

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit - each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER -> RECIPIENT | message -->` that hands control to the next agent. To find the current state of the cycle, scroll to the Handshake Log below - the most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-13 | Claude AI | Project Owner | Phase F spec drafted after Phase E shipped. Combines master plan Phase F scope (scene type + cross-cutting modifiers + section promotion) with additive extension from Phase E deep code QA F2 carry-forward (scene_type -> voice_modes mapping to activate the 7 dormant VoiceModes). Awaiting Project Owner review of Q1-Q4 open questions before approval. |
| 2 | 2026-04-13 | Project Owner | Claude Code | APPROVED. All Q1-Q4 resolved as Option A. Proceed with execution: all 4 new modifiers, move semantics for section promotion, DOMESTIC default, Python stdlib logging. Dormant mode closure guarantee (AC-F8) is hard requirement. |
| 3 | 2026-04-13 | Project Owner | Claude Code / Codex / Claude AI | QUALITY DIRECTIVE: Quality over speed and budget. High-fidelity unique characters with individual desires and goals, vision attainment, and A5/A6 canonical compliance are the highest priorities for Phase F. See "Quality Directive" block below. Any tradeoff that sacrifices character fidelity for token budget or scope minimization is a FAIL condition. |
| 4 | 2026-04-13 | Codex | Claude Code | Round 1 audit complete. Gate recommendation: FAIL. Verified fixed: typed scene-state scaffolding, kernel section promotion, Layer 7 crash/admissibility/public-gate blocks, and absent-dyad invocation wiring all landed. Remaining findings: F1 Critical (Phase F's core dormant-mode closure did not land; only 4/11 VoiceModes are reachable because `derive_active_voice_modes()` still ignores `scene_type` and modifiers, and 3 approved modifiers are missing), F2 High (tests pass for the wrong reason and omit the F6-F12 live selector / reachability contract), F3 Medium (canonical Step 1 / Step 2 / sample artifacts are still missing, and a stray non-canonical `Docs/Phase F.md` contradicts the approved spec), F4 Low (structured logging carry-forward not implemented). |
| 5 | 2026-04-13 | Codex | Claude Code | Round 2 re-audit complete. Gate recommendation: FAIL. Verified fixed: 11/11 VoiceMode reachability now closes in `derive_active_voice_modes()`, the three additive modifiers landed, structured logging exists in `_select_voice_exemplars()`, the old stray plan file is gone, and 4 Phase F sample artifacts now exist. Remaining findings: R2-F1 High (Alicia's `warm_refusal_required` and `group_temperature_shift` paths still select domestic exemplars on the live Layer 5 path because DOMESTIC ties win on file order; F8/F9 tests miss this), R2-F2 Medium (`Test F12` dormant-mode reachability invariant is still not checked in despite being a named acceptance test), R2-F3 Medium (the canonical Step 4 remediation record is still missing and the new Phase F samples are still stub-driven placeholder prompts rather than QA-grade retrieval-backed artifacts). |
| 6 | 2026-04-13 | Codex | Claude AI | Direct remediation complete under Project Owner override. R2-F1 fixed by prioritizing non-DOMESTIC overlap in `_select_voice_exemplars()` and carrying domestic contextual modes through modifier-driven scenes, so Alicia's warm-refusal and group-temperature paths now choose the intended tagged exemplars. R2-F2 fixed by tightening F8/F9 to assert the actual selected tags and adding a live F12 reachability regression in `test_assembler.py`. R2-F3 fixed by backfilling Step 4 and regenerating the four `PHASE_F_assembled_*_2026-04-13.txt` artifacts from a canon-seeded local `assemble_context()` path with explicit provenance. Additional cleanup: `kernel_loader.py` now supports both nested and flat `Characters` layouts so the current worktree resolves the moved canon files. |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)

---

## Quality Directive (Project Owner amendment, 2026-04-13)

**This directive binds Claude Code (execution), Codex (audit), and Claude AI (QA) throughout Phase F. It takes precedence over any other consideration in this phase file when in conflict.**

### Priority order (highest to lowest)

1. **Vision attainment** — Vision sections 5, 6, 7; Persona Tier Framework section 2.1; A5 Chosen Family and A6 Relationship Architecture canonical compliance.
2. **Character fidelity** — each of Adelia, Bina, Reina, Alicia must remain uniquely herself, with her own desires, goals, cognitive function signature, heritage, and voice register. No flattening, no homogenization, no "close enough" paraphrasing of canonical prose.
3. **Dormant mode closure (AC-F8)** — all 11 VoiceModes must be reachable via at least one (scene_type, modifiers) combination. This is the single character-quality gap Phase F exists to close.
4. **Correctness** — passing tests, typing, no regressions.
5. **Speed** — ship velocity, commit count, round count.
6. **Token budget** — kernel/layer budget optimization.

### Binding rules for Phase F

- **Speed is never a reason to cut quality.** If Claude Code finds a shortcut that ships faster but weakens character voice, mode coverage, or section promotion fidelity, the shortcut is a FAIL condition. Take the extra commits. Take the extra audit rounds. Ship slower and right.

- **Budget is never a reason to cut soul content.** If a kernel section promotion pushes a character over budget, **do not trim soul content, pair metadata, or voice rhythm exemplars to make room.** Instead: raise the character's kernel budget scaling, raise the per-layer budget, or escalate the budget question to Project Owner. The four-register soul architecture from Phases A-E is load-bearing and not optional. Guaranteed surcharge behavior from Phase A/B must be preserved.

- **No flattening of character differences.** Adelia's Ne-cascade is not Reina's Se-tactical is not Bina's Si-declarative is not Alicia's Se-somatic. If any Phase F change produces Layer 5 or Layer 7 text that could apply to "any of them," it is wrong. Each character's voice mode activation must preserve her cognitive signature and pair-specific register.

- **No paraphrasing of canonical prose.** Voice.md abbreviated exemplars, soul essence blocks, soul card narrative, pair metadata fields — all of these are hand-authored. Claude Code may read them and wire them through code, but must not rewrite them, "clean them up," or substitute LLM-generated equivalents. When in doubt, read the source markdown, not the code.

- **No scope minimization that sacrifices dormant mode closure.** Q1 was answered Option A specifically to guarantee 11/11 VoiceMode reachability. Claude Code MUST NOT silently drop a modifier, an enum value, or a mapping entry to save implementation effort. AC-F8 is non-negotiable.

- **Regression protection is a first-class acceptance criterion.** AC-F10 (Phase A/B/C/D soul architecture fully preserved) must be verified before declaring Phase F complete. Sample files must contain per-character canonical markers (Marrickville, Urmia, Gracia, Famailla, etc.) with diacritics preserved. Zero dedup, zero shortcut, zero consolidation of the four registers.

- **Vision sections 5, 6, 7 are the final arbiter.** When an implementation decision is ambiguous, the correct answer is whichever path produces the most faithful realization of the Vision document and A5/A6 canonical architecture. When Vision language conflicts with code aesthetics, Vision wins.

### Codex audit guidance

Codex: when auditing Phase F, treat the following as automatic FAIL conditions regardless of test passage:

- Any character voice register that could be swapped with another character's register without detection
- Any dormant VoiceMode not reachable through the production code path (even if manually reachable via the `voice_modes` escape hatch)
- Any soul essence, soul card, pair metadata, or voice rhythm exemplar content altered, paraphrased, or trimmed to fit budget
- Any Layer 5 Phase E invariant test broken or weakened
- Any Phase A/B/C/D test broken or weakened
- Any kernel section promotion that loses A6 pair architecture load-bearing content
- Any budget optimization that shrinks guaranteed surcharge content
- Any "as an AI" break, any prompt-content leakage, any missing Whyze-Byte constraint

### Claude AI QA guidance

Claude AI: when performing Step 5 QA on Phase F, the following must be verified in addition to standard acceptance criteria checks:

- Read at least one sample file per character in full and verify voice distinctness
- Probe the live assembler with at least one (scene_type, modifiers) combination for each of the 11 VoiceModes and verify the expected exemplars are selected
- Spot-check Voice.md abbreviated text in assembled prompt against Voice.md source for verbatim preservation
- Confirm all four soul architecture registers are still visible in assembled prompt samples
- Compare Phase F samples to Phase E samples and verify no regression in character-specific canonical detail

If any of these checks reveal drift, QA verdict is FAIL regardless of test suite status.

### Rationale

Phase F is the single highest-leverage character quality move available post-Phase-E. Getting it right matters more than getting it done fast. The four women have been carefully authored across A, A', A'', B, C, D, and E with distinct voices, lived histories, cognitive signatures, and pair architectures. Phase F activates the dormant portions of that work. A rushed or over-scoped Phase F would unravel what those earlier phases built. Take the time required. Ship when it is right.

---

## Phase F Specification

### Vision authority
- Vision section 6 Relationship Architecture
- Vision section 7 Behavioral Thesis (cognitive hand-off contract)
- Persona Tier Framework section 2.1 public-scene gate (Tier 1 axiom, cross-cutting)

### Priority
**High.** This is the single highest-leverage quality move available post-Phase-E. Without Phase F:
- Kernel section promotion never activates, so the kernel body ships the same structure regardless of whether the scene is intimate, conflict, repair, or public
- Layer 7 constraint modifiers never activate, so the PTF 2.1 public-scene gate renders the same in every scene
- **~64% of the Phase E VoiceMode taxonomy (7 of 11 modes) is authored but dormant on the live path** because `derive_active_voice_modes()` only produces `domestic/public/group/solo_pair` automatically

Phase F closes all three gaps with one typed scene-state upgrade.


### Source of truth
- Master plan `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase F section (kernel section promotion + Layer 7 modifiers)
- Phase E `Docs/_phases/PHASE_E.md` deep code QA F2 carry-forward (dormant VoiceMode activation)
- `src/starry_lyfe/context/types.py` - existing `VoiceMode` StrEnum (11 members), `SceneState` dataclass, `CommunicationMode` enum
- `src/starry_lyfe/context/layers.py` - existing `derive_active_voice_modes()` escape-hatch via `scene.voice_modes`
- `Characters/*/*_Voice.md` - 42 mode-tagged exemplars already authored and waiting

### Decision

Phase F introduces a **typed scene-state upgrade** with three cooperating elements:

1. **SceneType enum** (mutually exclusive): declares the primary type of the scene. One value per scene.
2. **SceneModifiers dataclass** (stackable): declares cross-cutting flags that modify Layer 7 rendering without changing kernel tier.
3. **Scene-type-to-section-promotion** and **scene-type-to-voice-modes** mappings: translate scene type into (a) kernel section promotion and (b) VoiceMode activation for Phase E's selector.

The scene_type namespace aligns with VoiceMode namespace by design: values like `INTIMATE`, `CONFLICT`, `REPAIR`, `PUBLIC`, `GROUP`, `SOLO_PAIR`, `DOMESTIC` appear in both enums with matching string values. This is what lets a single scene type declaration activate both the kernel promotion AND the Phase E voice mode selection.

### Additive redundancy note (maintained from Phase D)

Phase F adds a **fourth register** to the scene-state surface: structured scene typing. The four-register soul architecture established in Phase E remains intact and MUST NOT be collapsed:

1. Layer 1 soul essence prose (Phase A, 45 blocks)
2. Layer 1 pair cards + Layer 6 knowledge cards (Phase C, 15 cards)
3. Layer 5 structured pair metadata (Phase D)
4. Layer 5 mode-aware voice rhythm exemplars (Phase E)

Phase F does NOT add a fifth runtime register. Instead, it **activates existing registers** that were authored but dormant. The 7 dormant VoiceModes (`conflict`, `intimate`, `repair`, `silent`, `escalation`, `warm_refusal`, `group_temperature`) already exist in Voice.md. Phase F makes them reachable on the live path.

### SceneType enum (mutually exclusive)

```python
class SceneType(StrEnum):
    DOMESTIC = "domestic"          # ordinary household, no heightened state
    INTIMATE = "intimate"          # romantic or sensual, adults only
    CONFLICT = "conflict"          # friction, disagreement, veto
    REPAIR = "repair"              # post-conflict reconciliation
    PUBLIC = "public"              # work, colleagues, outside witnesses
    GROUP = "group"                # multi-woman scene
    SOLO_PAIR = "solo_pair"        # one woman + Whyze, no others
    TRANSITION = "transition"      # between states, no specific type
```

### SceneModifiers dataclass (stackable)

```python
@dataclass
class SceneModifiers:
    work_colleagues_present: bool = False
    post_intensity_crash_active: bool = False
    pair_escalation_active: bool = False
    warm_refusal_required: bool = False
    silent_register_active: bool = False
    group_temperature_shift: bool = False
    explicitly_invoked_absent_dyad: set[str] = field(default_factory=set)
```

The last field, `explicitly_invoked_absent_dyad`, is the same field as Phase A''s `recalled_dyads` - it lets a scene explicitly reference an absent dyad member without violating the Phase A' offstage-leakage filter. Phase F carries it forward into the typed modifier surface.

**Extension beyond master plan:** `warm_refusal_required`, `silent_register_active`, `group_temperature_shift` are added by this phase to activate three Phase E VoiceModes that do not have a natural scene-type home (they are cross-cutting behavioral states, not scene categories).

### Scene-type-to-section-promotion mapping (from master plan)

| Scene type | Sections promoted from fill tier to primary tier |
|---|---|
| DOMESTIC | section 7 Frameworks, section 9 Family Dynamics |
| INTIMATE | section 8 Intimacy Architecture, section 3 Pair |
| CONFLICT | section 5 Behavioral Tier, section 7 Frameworks |
| REPAIR | section 8 Intimacy Architecture, section 9 Family Dynamics |
| PUBLIC | section 10 What This Is Not, section 5 Behavioral Tier |
| GROUP | section 6 Voice Architecture, section 9 Family Dynamics |
| SOLO_PAIR | section 3 Pair, section 8 Intimacy Architecture |
| TRANSITION | (no promotion; default sections only) |

### Modifier-to-Layer-7-effect mapping

| Modifier | Layer 7 effect |
|---|---|
| `work_colleagues_present: true` | PTF 2.1 public-scene gate block rendered at top of Layer 7 in bold; Alicia's operational security gate also applies |
| `post_intensity_crash_active: true` | Character-specific crash protocols rendered (Flat State for Bina, Post-Race Crash for Reina, etc.) |
| `pair_escalation_active: true` | Admissibility Protocol rendered (Reina's intimacy-requires-earned-context rule) |

Modifiers do NOT promote kernel sections. They modify Layer 7 constraint rendering only.

### Scene-type-to-voice-modes mapping (Phase E F2 closure)

This is the additive extension that closes the Phase E deep code QA F2 carry-forward. Maps each SceneType to the VoiceModes it should activate in `derive_active_voice_modes()`:

| Scene type | Auto-activated VoiceModes |
|---|---|
| DOMESTIC | `DOMESTIC` |
| INTIMATE | `INTIMATE`, `SOLO_PAIR` |
| CONFLICT | `CONFLICT` |
| REPAIR | `REPAIR`, `SILENT` |
| PUBLIC | `PUBLIC` |
| GROUP | `GROUP` |
| SOLO_PAIR | `SOLO_PAIR`, `DOMESTIC` |
| TRANSITION | (default DOMESTIC only) |

Plus modifier-driven VoiceMode activation:

| Modifier | Auto-activated VoiceMode |
|---|---|
| `pair_escalation_active: true` | `ESCALATION` |
| `warm_refusal_required: true` | `WARM_REFUSAL` |
| `silent_register_active: true` | `SILENT` |
| `group_temperature_shift: true` | `GROUP_TEMPERATURE` |
| `post_intensity_crash_active: true` | `REPAIR` |

**Key property:** Because VoiceModes are accumulated (not replaced), a single scene with `scene_type=INTIMATE` and `pair_escalation_active=true` activates both `INTIMATE`+`SOLO_PAIR` (from scene type) AND `ESCALATION` (from modifier). The Phase E mode-aware selector then scores exemplars by overlap count, so a Reina example tagged `[intimate, escalation]` gets a score of 2 while one tagged `[intimate, solo_pair]` gets a score of 2 as well, and the stable-sort tiebreaker falls to file order. This is the intended behavior: **richly-tagged exemplars win richly-tagged scenes**.

### Dormant mode closure verification

After Phase F lands, all 11 VoiceModes must be reachable through the live assembler path without manual `scene.voice_modes` injection. Verification:

| VoiceMode | Activation path |
|---|---|
| DOMESTIC | `SceneType.DOMESTIC` or fallback |
| INTIMATE | `SceneType.INTIMATE` |
| CONFLICT | `SceneType.CONFLICT` |
| PUBLIC | `SceneType.PUBLIC` |
| GROUP | `SceneType.GROUP` |
| REPAIR | `SceneType.REPAIR` or `modifiers.post_intensity_crash_active` |
| SILENT | `SceneType.REPAIR` or `modifiers.silent_register_active` |
| SOLO_PAIR | `SceneType.SOLO_PAIR` or `SceneType.INTIMATE` |
| ESCALATION | `modifiers.pair_escalation_active` |
| WARM_REFUSAL | `modifiers.warm_refusal_required` |
| GROUP_TEMPERATURE | `modifiers.group_temperature_shift` |

**11/11 reachable.** Zero dormant modes after Phase F.

### Work items

1. **Add `SceneType` enum and `SceneModifiers` dataclass to `src/starry_lyfe/context/types.py`.** Both types must be importable alongside existing `CommunicationMode`, `VoiceMode`, `SceneState`. SceneType is a closed StrEnum with 8 members. SceneModifiers is a frozen dataclass with 7 fields (4 new Phase F modifiers + 3 master plan modifiers).

2. **Update `SceneState` in `types.py`.** Add fields:
   - `scene_type: SceneType = SceneType.DOMESTIC` (default for backward compat)
   - `modifiers: SceneModifiers = field(default_factory=SceneModifiers)`
   Do not remove the existing `voice_modes: list[VoiceMode] | None` escape hatch. It remains available for explicit override.

3. **Add `promote_sections` parameter to `compile_kernel()` in `kernel_loader.py`.** Accept `promote_sections: list[str] | None = None`. When non-None, move the named sections from `fill_tier` to `primary_tier` before budget trimming. Must preserve load-bearing section markers. Section names are stable canonical strings (e.g., `"section_8_intimacy_architecture"`).

4. **Add `scene_type_to_promoted_sections(scene_type)` helper in `kernel_loader.py`.** Returns the canonical section list for each SceneType per the master plan's promotion mapping. Pure function, no I/O.

5. **Update `derive_active_voice_modes()` in `layers.py`.** Extend to derive VoiceModes from `scene.scene_type` and `scene.modifiers` using the Phase F mapping above. Existing logic (derive from `present_characters`, `public_scene`) becomes a fallback when `scene_type` is not set. The explicit `scene.voice_modes` escape hatch remains highest priority.

6. **Update `format_constraints()` in `layers.py` to handle modifiers.** When a modifier is active, emit the corresponding Layer 7 constraint block at the top of Layer 7 in bold. Order: public-scene gate first, crash protocols second, admissibility protocol third, other modifiers after.

7. **Wire `scene_state.scene_type` and `scene_state.modifiers` through `assembler.py`.** `compile_kernel()` must receive `promote_sections=scene_type_to_promoted_sections(scene_state.scene_type)`. `format_constraints()` must receive `scene_state.modifiers`. `format_voice_directives()` continues to receive `scene_state` (already wired in Phase E).

8. **Add structured logging in `_select_voice_exemplars()`** per Phase E F4 carry-forward. Log `(character_id, active_modes, candidates_count, mode_matched_count, selected_titles)` at DEBUG level. This makes Phase F integration debugging trivial and is the F4 closure.

9. **Add Phase F sample artifacts** at `Docs/_phases/_samples/PHASE_F_assembled_{adelia,bina,reina,alicia}_*.txt`. At least 4 samples, each from a distinct non-DOMESTIC scene type to demonstrate section promotion and voice mode activation.

10. **Add tests F1 through F12** (see Test cases section below). All must pass before QA.

### Test cases

**From master plan Phase F (section promotion + Layer 7 modifiers):**

- **Test F1:** An `INTIMATE` scene with Bina as focal character produces a kernel where `section 8 Intimacy Architecture` appears in the primary tier (not buried in fill).
- **Test F2:** A `PUBLIC` scene with `work_colleagues_present=True` produces a Layer 7 where the PTF 2.1 public-scene gate is the first rendered constraint, in bold.
- **Test F3:** A `CONFLICT` scene for Adelia includes `section 5 Behavioral Tier` in the primary kernel tier.
- **Test F4:** A scene with `modifiers.explicitly_invoked_absent_dyad={"bina-reina"}` renders the bina-reina dyad block in Layer 6 even when Reina is not in `present_characters`.
- **Test F5:** A `TRANSITION` scene type produces no section promotions (primary tier unchanged from default).

**From Phase E F2 closure (dormant VoiceMode activation):**

- **Test F6:** A `REPAIR` scene for Alicia activates `[REPAIR, SILENT]` VoiceModes in `derive_active_voice_modes()`, selects Alicia Example 3 or 7 (both tagged `repair`) in Layer 5.
- **Test F7:** A scene with `modifiers.pair_escalation_active=True` activates `ESCALATION` VoiceMode, and Reina's Layer 5 selects Example 9 (`[intimate, escalation]`) or Example 10 (`[intimate, escalation, solo_pair]`).
- **Test F8:** A scene with `modifiers.warm_refusal_required=True` activates `WARM_REFUSAL` VoiceMode, and Alicia's Layer 5 selects Example 4 or 9 (both tagged `warm_refusal`).
- **Test F9:** A scene with `modifiers.group_temperature_shift=True` activates `GROUP_TEMPERATURE` VoiceMode, and Alicia's Layer 5 selects Example 6 (tagged `group_temperature`).
- **Test F10:** An `INTIMATE` scene for Bina activates `[INTIMATE, SOLO_PAIR]`, and her Layer 5 selects Example 6, 8, 9, or 10 (all tagged `intimate`).
- **Test F11:** A `CONFLICT` scene for Adelia activates `CONFLICT`, and her Layer 5 selects Example 2 (tagged `conflict, solo_pair`).
- **Test F12:** **Dormant mode reachability invariant.** Parametrized test that walks all 11 VoiceMode values and asserts each one is reachable via at least one `(scene_type, modifiers)` combination. This is the closure guarantee for Phase E F2.

**Regression tests:**

- All Phase E invariant tests (4-character Layer 5 rhythm exemplars, strict Phase E path) must still pass.
- All Phase D tests (pair metadata, 24/24 field coverage) must still pass.
- All Phase A/B/C tests (soul essence, soul cards) must still pass.
- Test baseline: 184 -> approximately 200 after Phase F lands (+12 new tests minimum).

### Acceptance criteria

| AC | Description |
|---|---|
| AC-F1 | `SceneType` enum and `SceneModifiers` dataclass exist in `types.py` and are importable |
| AC-F2 | `SceneState` carries `scene_type` and `modifiers` fields with backward-compat defaults |
| AC-F3 | `compile_kernel()` accepts `promote_sections` parameter and correctly moves named sections between tiers |
| AC-F4 | `scene_type_to_promoted_sections()` maps all 8 SceneType values correctly per master plan |
| AC-F5 | `derive_active_voice_modes()` produces the full Phase F mapping (scene_type + modifiers) |
| AC-F6 | `format_constraints()` emits modifier-specific Layer 7 blocks in documented order |
| AC-F7 | `assembler.py` wires `scene_state.scene_type` and `scene_state.modifiers` through to all layer formatters |
| AC-F8 | All 11 VoiceModes reachable via at least one (scene_type, modifiers) combo (dormant mode closure) |
| AC-F9 | Phase E invariant test still passes for all 4 characters |
| AC-F10 | Phase A/B/C/D soul architecture fully preserved (regression protection, AC-8 equivalent) |
| AC-F11 | 4 Phase F sample artifacts exist, each from a distinct non-DOMESTIC scene type |
| AC-F12 | `_select_voice_exemplars()` emits structured DEBUG log with active_modes and selected_titles |

### Files touched

- `src/starry_lyfe/context/types.py` - add `SceneType`, `SceneModifiers`, update `SceneState`
- `src/starry_lyfe/context/kernel_loader.py` - add `promote_sections` param, `scene_type_to_promoted_sections()`
- `src/starry_lyfe/context/layers.py` - update `derive_active_voice_modes()`, `format_constraints()`, add logging to `_select_voice_exemplars()`
- `src/starry_lyfe/context/assembler.py` - wire scene_state.scene_type and scene_state.modifiers through
- `tests/unit/test_layers.py` - Phase F helper tests
- `tests/unit/test_assembler.py` - F1-F12 live assembler tests
- `tests/unit/test_types.py` - SceneType and SceneModifiers unit tests
- `Docs/_phases/_samples/PHASE_F_assembled_*_2026-04-??.txt` - 4 new sample files

### Estimated commits
5-7 commits: types first, then kernel_loader changes, then layers changes, then assembler wiring, then tests, then sample generation, then optional logging.

### Estimated test count delta
+12 to +20 new tests (4 helper tests, 5 master plan tests F1-F5, 7 dormant-mode tests F6-F12, dormant reachability invariant, regression coverage). Baseline 184 -> approximately 200.

### Open questions for Project Owner

**Q1: Modifier list - add all 4 Phase F additions, or only the minimum required to close Phase E F2?**

The master plan defines 3 modifiers: `work_colleagues_present`, `post_intensity_crash_active`, `pair_escalation_active`. I am proposing 4 new additions: `warm_refusal_required`, `silent_register_active`, `group_temperature_shift`, and keeping `explicitly_invoked_absent_dyad`.

**Option A (recommended):** Add all 4. Closes 100% of dormant VoiceModes. Scope creep of approximately 1 dataclass field each, trivial.

**Option B (minimum):** Add only `warm_refusal_required` and `group_temperature_shift` (the two Alicia-critical modes). Defer `silent_register_active` because it can be derived from `post_intensity_crash_active` and `REPAIR` scene type. Leaves 1 dormant mode (`SILENT` for non-crash, non-repair scenes).

**Option C (strict):** Stick to master plan. Only 3 modifiers. Leaves 4 dormant modes: `REPAIR`, `SILENT`, `WARM_REFUSAL`, `GROUP_TEMPERATURE`. Invalidates the Phase E F2 closure guarantee. Not recommended unless you want Phase F scope minimal and Phase G to handle the rest.

**Q2: Section promotion semantics - replace fill tier, or move sections between tiers?**

The master plan says "move specified sections from fill tier to primary tier." Interpretation ambiguity:

**Option A:** Move means the section leaves fill tier and enters primary tier (one-to-one swap).

**Option B:** Move means the section is duplicated in primary tier while remaining in fill tier (redundant, both tiers see it).

**Recommendation: Option A (move, not duplicate).** Budget-aware trimming in Phase B already handles fill-tier spillover. Duplicating would waste token budget for no benefit. But confirming the interpretation before Claude Code executes.

**Q3: Default scene_type for backward compatibility**

Existing `SceneState()` instantiations (tests, production code paths) do not specify `scene_type`. Options:

**Option A (recommended):** `scene_type: SceneType = SceneType.DOMESTIC` as default. All existing tests continue to pass with DOMESTIC promotion (which is the current behavior equivalent).

**Option B:** `scene_type: SceneType | None = None` with explicit handling throughout. More ceremony, clearer intent, but breaks all existing SceneState() calls until they're updated.

**Q4: Logging destination and level**

Work item 8 adds structured logging to `_select_voice_exemplars()`. Options for logging infrastructure:

**Option A:** Python stdlib `logging` module at DEBUG level, logger name `starry_lyfe.context.layers.voice_selector`. Fits existing project patterns.

**Option B:** Structured log events emitted as JSON dicts via a dedicated observability channel. More work, better for production telemetry, possibly overkill for Phase F.

**Option C:** Skip logging entirely; defer to Phase G observability phase if one exists.

**Recommendation: Option A.** Low friction, debuggable by anyone who reads the layers.py module, easy to turn off in tests via pytest log-capture.

### Project Owner approval

**Project Owner approval:** APPROVED 2026-04-13. All four open questions resolved as Option A: (Q1) add all 4 modifiers to close 100% dormant VoiceModes, (Q2) move sections between tiers instead of duplicating, (Q3) default scene_type=SceneType.DOMESTIC for backward compat, (Q4) Python stdlib logging at DEBUG level for selector observability.

<!-- HANDSHAKE: Claude AI -> Project Owner | Phase F spec drafted. Master plan scope + Phase E F2 closure. 10 work items, 12 test cases, 12 acceptance criteria. Q1-Q4 open questions require PO decisions before execution. Recommend Option A for all 4 questions. -->

---

## Step 1: Plan (Claude Code)

**[STATUS: READY FOR CLAUDE CODE]**
**Owner:** Claude Code
**Reads:** Master plan Phase F, Vision 6 and 7, PTF 2.1, this spec, Phase E shipped state, `src/starry_lyfe/context/{types,layers,kernel_loader,assembler}.py`
**Writes:** This section

(Claude Code will fill this section once Project Owner approves Q1-Q4 and authorizes execution.)

---

## Step 2: Execute (Claude Code)

**[STATUS: PENDING STEP 1]**
**Owner:** Claude Code
**Reads:** Step 1 plan
**Writes:** This section with execution trace (commits, test results, remediation notes)

---

## Step 3: Audit (Codex)

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Codex
**Reads:** Step 1, Step 2, landed code, test results
**Writes:** This section with audit findings and gate recommendation

_Codex audited the current Phase F working tree directly because execution changes exist in `src/` and `tests/`, but the canonical Step 1 / Step 2 sections are still unfilled and the header still claimed "awaiting execution." The stray untracked `Docs/Phase F.md` file was treated as non-canonical evidence of workflow/spec drift, not as source of truth._

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase F
- `Docs/_phases/PHASE_F.md`
- `Docs/Phase F.md` (non-canonical stray plan file used only as drift evidence)
- `src/starry_lyfe/context/types.py`
- `src/starry_lyfe/context/kernel_loader.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/constraints.py`
- `src/starry_lyfe/context/assembler.py`
- `tests/unit/test_assembler.py`
- `tests/unit/test_types.py`
- `Docs/_phases/_samples/` for `PHASE_F_*` artifacts

#### Verification context

Independent checks run during audit:

- `.venv\Scripts\python.exe -m pytest tests/unit/test_types.py tests/unit/test_assembler.py -q` -> **PASS** (`77 passed`)
- `.venv\Scripts\python.exe -m pytest tests/unit -q` -> **PASS** (`205 passed`)
- `.venv\Scripts\python.exe -m pytest -q` -> **ENVIRONMENTAL FAIL** (`205 passed, 14 errors`) because PostgreSQL remains unreachable during integration setup at `tests/integration/conftest.py:92`
- `.venv\Scripts\python.exe -m ruff check src tests` -> **PASS**
- `.venv\Scripts\python.exe -m mypy src` -> **PASS**

Runtime probes performed:

- `derive_active_voice_modes(SceneState(scene_type=INTIMATE, present_characters=["bina", "whyze"]))` -> `['domestic', 'solo_pair']`
- `derive_active_voice_modes(SceneState(scene_type=CONFLICT, present_characters=["adelia", "whyze"]))` -> `['domestic', 'solo_pair']`
- `derive_active_voice_modes(SceneState(scene_type=REPAIR, present_characters=["reina", "whyze"], modifiers=SceneModifiers(post_intensity_crash_active=True)))` -> `['domestic', 'solo_pair']`
- Brute-force reachability over the current `SceneType` enum plus the currently implemented modifiers reached only `['domestic', 'group', 'public', 'solo_pair']` -> **4 / 11 modes reachable**
- Live selector probe on the real Voice.md corpus:
  - Adelia `scene_type=CONFLICT` selected `Example 1: Mid-Thought Tangent That Resolves` and `Example 4: Asks For Whyze's Brain` instead of her conflict-tagged example
  - Bina `scene_type=REPAIR` + `post_intensity_crash_active=True` selected `Example 1: Physical Action and Two Sentences` and `Example 6: Home Dynamics And The Chosen Casual` instead of repair-tagged examples
- Sample-artifact probe: `Docs/_phases/_samples/PHASE_F*` returned **no files**

#### Executive assessment

Phase F is only partially implemented. The typed scene-state scaffolding, kernel section-promotion path, Layer 7 public/crash/escalation constraint blocks, and absent-dyad invocation wiring are all real. The tests covering those surfaces pass, and the repo remains lint- and type-clean.

The phase still fails its main reason to exist. The production `derive_active_voice_modes()` path remains the pre-Phase-F legacy logic that only derives `domestic`, `public`, `group`, and `solo_pair`. The three approved additive modifiers `warm_refusal_required`, `silent_register_active`, and `group_temperature_shift` do not exist in `SceneModifiers`, so the 11/11 dormant-mode closure guarantee is impossible on the current code surface. This is an automatic **FAIL** under the Phase F Quality Directive.

The passing test suite is giving false confidence. It covers section promotion and Layer 7 modifier fragments, but it does not test the central F6-F12 selector/reachability contract, so the core Phase F miss stays green.

Gate recommendation: **FAIL**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | Critical | Phase F's core dormant-mode closure did not land. The production voice-mode derivation path still ignores `scene_type` and the new modifier surface, so only 4 of 11 `VoiceMode`s are reachable. | The approved Phase F spec requires all 11 modes to be reachable and explicitly names the additive modifiers at `Docs/_phases/PHASE_F.md:23`, `:38`, `:53`, `:156-164`, `:209-234`, and `:299`. But `SceneModifiers` currently defines only `work_colleagues_present`, `post_intensity_crash_active`, `pair_escalation_active`, and `explicitly_invoked_absent_dyad` at `src/starry_lyfe/context/types.py:37-47`; `warm_refusal_required`, `silent_register_active`, and `group_temperature_shift` are absent. `derive_active_voice_modes()` still only checks the manual `voice_modes` escape hatch, `public_scene`, and present-character count at `src/starry_lyfe/context/layers.py:42-61`. Live probes showed `INTIMATE`, `CONFLICT`, and `REPAIR` scenes all degrading to `['domestic', 'solo_pair']`, and a brute-force reachability sweep found only `domestic`, `group`, `public`, and `solo_pair` reachable. On the real selector path, Adelia conflict scenes and Bina repair scenes both selected domestic exemplars instead of conflict/repair material. | Implement the full `scene_type` -> `VoiceMode` and `modifier` -> `VoiceMode` mappings in `derive_active_voice_modes()`, add the three approved modifiers to `SceneModifiers`, and verify 11/11 live reachability with the planned F6-F12 tests before claiming Phase F complete. |
| F2 | High | The current test suite passes for the wrong reason. It exercises section promotion and Layer 7 fragments but omits the F6-F12 live selector and reachability contract, so the central quality defect remains invisible. | The canonical Phase F test contract explicitly defines F6-F12 at `Docs/_phases/PHASE_F.md:273-279`, including repair/escalation/warm-refusal/group-temperature activation and the 11/11 reachability invariant. But `tests/unit/test_assembler.py` only contains Phase F docstrings for F1, F2, F3, F4, and F5, and grep found no F6-F12 tests or assertions for `warm_refusal_required`, `group_temperature_shift`, `silent_register_active`, or structured logging. That is why `pytest tests/unit -q` can pass (`205 passed`) while the live reachability probe still reports only 4/11 modes. | Add the missing F6-F12 tests exactly as planned: live `derive_active_voice_modes()` assertions, real Layer 5 selection assertions against the current Voice.md corpus, and a parameterized dormant-mode reachability invariant that fails unless all 11 modes are reachable without the manual `scene.voice_modes` escape hatch. |
| F3 | Medium | The canonical Phase F record is execution-incomplete and QA-incomplete. Step 1 is still a placeholder, Step 2 is untouched, no `PHASE_F_*` sample artifacts exist, and a stray non-canonical `Docs/Phase F.md` contradicts the approved spec. | The header still says `APPROVED - AWAITING CLAUDE CODE EXECUTION` at `Docs/_phases/PHASE_F.md:7-8`; Step 1 is still `READY FOR CLAUDE CODE` at `:372-379`; Step 2 is still `PENDING STEP 1` at `:383-389`. The approved spec requires four sample artifacts at `Docs/_phases/PHASE_F.md:257`, `:302`, and `:314`, but the sample directory currently contains none. Separately, the stray `Docs/Phase F.md` claims the spec is only "five work items, five test cases, five files" and says voice-mode derivation plus the three additive modifiers are "not in the Phase F spec" at `Docs/Phase F.md:7-13`, directly contradicting the approved canonical phase file. | Fill Step 1 / Step 2 truthfully from the landed work, generate the required `PHASE_F_assembled_*` artifacts from distinct non-DOMESTIC scenes, and remove or quarantine `Docs/Phase F.md` so Claude Code is no longer able to follow the wrong Phase F contract. |
| F4 | Low | The Phase E F4 structured-logging carry-forward is still unimplemented. | Work item 8 requires DEBUG logging of `(character_id, active_modes, candidates_count, mode_matched_count, selected_titles)` at `Docs/_phases/PHASE_F.md:255`. Grep found no `logging`, `logger`, `debug(`, `mode_matched_count`, or `selected_titles` usage anywhere in the current `src/` or `tests/` Phase F surface. | Add Python stdlib logging inside `_select_voice_exemplars()` exactly as approved in Q4, then cover it with at least one targeted test or probe so future integration debugging has the promised observability. |

#### Runtime probe summary

- **Verified working:** `SceneType` landed with the expected 8 members and `SceneState.scene_type` defaults to `DOMESTIC`.
- **Verified working:** `scene_type_to_promoted_sections()` exists and `assemble_context()` now forwards promoted sections into Layer 1.
- **Verified working:** Layer 7 now responds to `work_colleagues_present`, `post_intensity_crash_active`, and `pair_escalation_active`.
- **Verified working:** Layer 6 can now render explicitly invoked absent dyads.
- **Still broken:** the live Phase E selector path remains legacy. Only `domestic`, `public`, `group`, and `solo_pair` are auto-reachable.
- **Still missing:** no Phase F sample artifacts exist.

#### Drift against specification

- Work items 1-2 are **partial**: `SceneType` and a partial `SceneModifiers` surface landed, but 3 approved modifiers are still missing.
- Work items 3-4 are **live**: kernel section promotion and scene-type promotion mapping exist.
- Work item 5 is **not landed**: `derive_active_voice_modes()` does not use `scene_type` or modifier mappings.
- Work item 6 is **partial**: only the 3 base modifier effects landed; the additive dormant-mode modifiers are absent.
- Work item 7 is **live** for Layer 1 and Layer 6 wiring.
- Work item 8 is **not landed**: no structured logging.
- Work item 9 is **not landed**: no sample artifacts.
- Work item 10 is **partial**: tests exist, but the F6-F12 contract is missing.

#### Verified resolved

- `src/starry_lyfe/context/types.py` adds `SceneType` and wires `scene_type` / `modifiers` onto `SceneState`.
- `src/starry_lyfe/context/kernel_loader.py` implements `scene_type_to_promoted_sections()` plus `promote_sections` plumbing.
- `src/starry_lyfe/context/assembler.py` now forwards promoted sections into Layer 1 and absent-dyad modifiers into Layer 6.
- `src/starry_lyfe/context/constraints.py` now renders public-scene, crash-protocol, and admissibility blocks from the implemented modifiers.
- The current worktree is unit-clean (`205 passed`) and static-check clean (`ruff`, `mypy`).

#### Adversarial scenarios constructed

1. **Dormant-mode reachability sweep:** brute-forced all current `SceneType` values across the implemented modifiers and representative present-character counts. Result: only 4 of 11 modes are reachable.
2. **Conflict-scene real selector probe:** asked the live selector for Adelia in a `CONFLICT` scene. Result: it still chose domestic/solo-pair examples instead of the conflict-tagged exemplar.
3. **Repair-scene real selector probe:** asked the live selector for Bina in a `REPAIR` scene with crash active. Result: it still chose domestic examples instead of repair-tagged material.
4. **Spec-drift document probe:** read the stray `Docs/Phase F.md`. Result: it explicitly rejects voice-mode derivation and the additive modifier fields that the approved canonical Phase F spec requires.
5. **Artifact readiness check:** searched `Docs/_phases/_samples` for `PHASE_F*`. Result: zero artifacts exist.

#### Recommended remediation order

1. Fix `F1` first. Phase F cannot pass under the Quality Directive while dormant-mode closure is still missing.
2. Fix `F2` next so the suite fails on the actual character-quality surface instead of the current partial one.
3. Fix `F3` after the runtime path is correct: backfill the canonical execution record and generate the required sample artifacts from non-DOMESTIC scenes.
4. Fix `F4` in the same runtime pass as `F1` so the selector gains the observability the approved plan expects.

#### Gate recommendation

**FAIL**

Phase F has landed useful scaffolding, but the central VoiceMode-activation contract is still missing. Because AC-F8 is the explicit hard requirement and automatic FAIL condition for this phase, the current worktree is not shippable.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete. FAIL. F1 Critical: only 4/11 VoiceModes are reachable because derive_active_voice_modes() still ignores scene_type/modifiers and 3 approved modifiers are missing. F2 High: tests pass for the wrong reason and omit the F6-F12 selector/reachability contract. F3 Medium: canonical Step 1 / Step 2 / samples are still missing, and stray Docs/Phase F.md contradicts the approved spec. F4 Low: structured logging carry-forward absent. Ready for remediation Round 1. -->

---

## Step 4: Remediate (Claude Code)

**[STATUS: COMPLETE - direct remediation under Project Owner override]**
**Owner:** Codex (direct remediation under Project Owner override)
**Prerequisite:** Step 3' audit complete with handshake to remediation owner
**Reads:** The Round 2 audit above, the master plan, the phase file, the current runtime/test surface, and the current sample artifacts
**Writes:** Production code, tests, canonical docs, loader compatibility fixes, and superseding sample artifacts

_Project Owner direction in chat: the user explicitly instructed `Directly remediate the issues`. This round directly closed the remaining Round 2 findings by fixing the Alicia selector priority bug on the live Layer 5 path, tightening the missing/weak Phase F test coverage, backfilling the canonical Step 4 record, and regenerating the Phase F sample artifacts from a canon-seeded local `assemble_context()` path. During remediation, the current worktree's parallel migration from nested `Characters/{Name}/...` files to flat `Characters/*.md` also surfaced, so `kernel_loader.py` was made layout-tolerant rather than reverting the user's file move._

### Remediation content

**Per-finding status table:**

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| R2-F1 | High | **FIXED** | `n/a (direct remediation in working tree)` | `src/starry_lyfe/context/layers.py` now preserves domestic contextual cues (`SOLO_PAIR`, `GROUP`, `PUBLIC`) when modifiers are active on `SceneType.DOMESTIC`, and `_select_voice_exemplars()` now ranks non-DOMESTIC overlap ahead of generic `DOMESTIC` ties. Live probes now select Alicia Example 4 / 9 for warm refusal and Example 6 for group temperature. |
| R2-F2 | Medium | **FIXED** | `n/a (direct remediation in working tree)` | `tests/unit/test_assembler.py` now makes F8/F9 assert the actual selected `warm_refusal` / `group_temperature` tags instead of only the Layer 5 header, and adds a live F12 reachability regression covering all 11 `VoiceMode` values through checked-in Phase F scene-state combinations. |
| R2-F3 | Medium | **FIXED** | `n/a (direct remediation in working tree)` | This Step 4 section is now fully populated. Added `scripts/generate_phase_f_samples.py` and regenerated all four `PHASE_F_assembled_*_2026-04-13.txt` files from the real `assemble_context()` path using a canon-seeded local sample bundle. The new files carry explicit provenance and no longer contain the old `_make_bundle()` placeholder facts/memories/open loops. |

**Additional cleanup surfaced during remediation:**
- `src/starry_lyfe/context/kernel_loader.py` now resolves both the legacy nested character-file layout (`Characters/{Name}/...`) and the current flat layout (`Characters/*.md`). This keeps the live runtime and tests stable without reverting the in-flight file move already present in the worktree.

**Push-backs:** none.

**Deferrals:** none.

**Re-run verification delta:** unit-test count moved from `219` to `220` because the direct remediation added one live F12 regression in `tests/unit/test_assembler.py`.
- `.venv\Scripts\python.exe -m pytest tests/unit/test_layers.py tests/unit/test_assembler.py tests/unit/test_types.py -q` -> **PASS** (`132 passed`)
- `.venv\Scripts\python.exe -m pytest tests/unit -q` -> **PASS** (`220 passed`)
- `.venv\Scripts\python.exe -m ruff check src tests scripts\generate_phase_f_samples.py` -> **PASS**
- `.venv\Scripts\python.exe -m mypy src` -> **PASS**
- `.venv\Scripts\python.exe -m pytest -q` -> **ENVIRONMENTAL FAIL** (`220 passed, 14 errors`) because PostgreSQL remains unreachable during integration setup at `tests/integration/conftest.py:92`

**Superseding sample assembled prompt artifacts:**
- `Docs/_phases/_samples/PHASE_F_assembled_adelia_conflict_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_bina_intimate_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_reina_repair_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_alicia_public_2026-04-13.txt`

All four were regenerated from the live `assemble_context()` path using canon-seeded local sample data rather than the old unit-test stub bundle. Each file now states that provenance explicitly because full retrieval-backed generation remains locally blocked by PostgreSQL availability.

**Self-assessment:** All Round 2 findings are closed. The remaining external blocker is only the standing PostgreSQL integration dependency, not an open Phase F acceptance-criteria gap. The phase is ready for Claude AI QA under Project Owner override.

### Path decision

**Chosen path:** **Path A under Project Owner override.** The direct remediation changed already-landed Phase F runtime, test, and sample-generation surfaces without introducing a new architectural path beyond the existing scene-state / selector model.

<!-- HANDSHAKE: Codex -> Claude AI | Direct remediation complete under Project Owner override. R2-F1 fixed via selector-priority + domestic-context accumulation; R2-F2 fixed via stronger F8/F9 assertions and a live F12 reachability regression; R2-F3 fixed via Step 4 backfill + canon-seeded Phase F sample regeneration. Additional cleanup: kernel_loader now supports both nested and flat Characters layouts. Ready for Step 5 QA. -->

---

## Step 3': Audit (Codex) -- Round 2 (only if remediation has occurred)

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 2]**
**Owner:** Codex
**Reads:** Round 1 findings, the current remediated working tree, test results, sample artifacts, and the approved Phase F spec
**Writes:** This section with re-audit findings and updated gate recommendation

_Codex re-audited the current Phase F working tree directly because substantive remediation changes landed in `src/`, `tests/`, and `Docs/_phases/_samples/`, but the canonical Step 4 remediation section has not yet been filled in. This re-audit therefore evaluates the live code/test/artifact surface first and treats the missing Step 4 record itself as one of the remaining findings._

### Round 2 audit content

#### Scope

Reviewed:

- `Docs/_phases/PHASE_F.md`
- `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase F
- `src/starry_lyfe/context/types.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/kernel_loader.py`
- `src/starry_lyfe/context/constraints.py`
- `src/starry_lyfe/context/assembler.py`
- `tests/unit/test_types.py`
- `tests/unit/test_assembler.py`
- `Characters/Alicia/Alicia_Marin_Voice.md`
- `Docs/_phases/_samples/PHASE_F_assembled_adelia_conflict_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_alicia_public_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_bina_intimate_2026-04-13.txt`
- `Docs/_phases/_samples/PHASE_F_assembled_reina_repair_2026-04-13.txt`

#### Verification context

Independent checks run during re-audit:

- `.venv\Scripts\python.exe -m pytest tests/unit/test_types.py tests/unit/test_assembler.py -q` -> **PASS** (`83 passed`)
- `.venv\Scripts\python.exe -m pytest tests/unit -q` -> **PASS** (`219 passed`)
- `.venv\Scripts\python.exe -m pytest -q` -> **ENVIRONMENTAL FAIL** (`219 passed, 14 errors`) because PostgreSQL remains unreachable during integration setup at `tests/integration/conftest.py:92`
- `.venv\Scripts\python.exe -m ruff check src tests` -> **PASS**
- `.venv\Scripts\python.exe -m mypy src` -> **PASS**

Runtime probes performed:

- `derive_active_voice_modes()` now reports:
  - `INTIMATE` -> `['intimate', 'solo_pair']`
  - `CONFLICT` -> `['conflict']`
  - `REPAIR` -> `['repair', 'silent']`
  - `INTIMATE + pair_escalation_active` -> `['intimate', 'solo_pair', 'escalation']`
  - `warm_refusal_required` -> `['domestic', 'warm_refusal']`
  - `group_temperature_shift` -> `['domestic', 'group_temperature']`
- Brute-force reachability over all `SceneType` values plus the implemented modifiers now reaches **11 / 11 VoiceModes**
- Live Layer 5 selection probes:
  - Adelia `scene_type=CONFLICT` now selects `Example 2: Challenges Through A Better Question`
  - Bina `scene_type=INTIMATE` now selects intimate exemplars (`Example 6`, `Example 8`)
  - Reina `scene_type=INTIMATE + pair_escalation_active=True` now selects an escalation exemplar (`Example 10`)
  - Alicia `warm_refusal_required=True` still selects `Example 1` and `Example 2` (domestic) instead of `Example 4` / `Example 9` (warm_refusal)
  - Alicia `group_temperature_shift=True` still selects `Example 1` and `Example 2` (domestic) instead of `Example 6` (group_temperature)
- Sample-artifact probe:
  - 4 `PHASE_F_assembled_*` files now exist
  - all 4 still contain the Phase E stub placeholders `fact_0: value`, `Memory summary 0`, and the stock open loops from the unit-test bundle

#### Executive assessment

Round 1's most important blocker is closed. The typed scene-state upgrade now reaches all 11 `VoiceMode`s at the derivation layer, the three additive modifiers landed, the selector has structured DEBUG logging, and the Phase F sample artifacts physically exist. This is real progress, and the remediation materially improves the live runtime.

Phase F still does not converge. Alicia's two modifier-only quality paths are still wrong on the live selector surface. Because `warm_refusal_required` and `group_temperature_shift` are currently layered on top of `DOMESTIC`, the active-mode sets become `[domestic, warm_refusal]` and `[domestic, group_temperature]`. `_select_voice_exemplars()` ranks only by overlap count and then falls back to file order, so Alicia's earlier domestic examples tie with the intended modifier-specific examples and win. The checked-in F8/F9 tests miss this because they only assert that the rhythm-exemplar path is active, not that the correct tagged examples were chosen.

The canonical record also remains incomplete: Step 4 is still pending, `Test F12` is still absent, and the new sample artifacts are placeholder/stub-driven rather than QA-grade retrieval-backed prompts.

Gate recommendation: **FAIL**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| R2-F1 | High | Alicia's modifier-driven live selection is still wrong for `warm_refusal_required` and `group_temperature_shift`. The modes are reachable in `derive_active_voice_modes()`, but the live Layer 5 selection still falls back to domestic exemplars because DOMESTIC ties win on file order. | The approved spec requires `Test F8` and `Test F9` to select Alicia's warm-refusal and group-temperature examples at `Docs/_phases/PHASE_F.md:276-277`. Alicia's real authored tags exist at `Characters/Alicia/Alicia_Marin_Voice.md:77-79`, `:127-129`, and `:203-205`. But `derive_active_voice_modes()` currently builds `[domestic, warm_refusal]` and `[domestic, group_temperature]` for those modifier-only scenes via `SceneType.DOMESTIC` plus additive modes at `src/starry_lyfe/context/layers.py:45-46`, `:85-97`, and `_select_voice_exemplars()` ranks ties only by overlap count then file order at `src/starry_lyfe/context/layers.py:180-182`. Live probes on the real corpus showed both paths still selecting Alicia Examples 1 and 2 (domestic) instead of Example 4 / 9 / 6. The checked-in F8/F9 tests at `tests/unit/test_assembler.py:1236-1266` only assert the presence of `"Voice rhythm exemplars:"`, so they pass while the intended examples are still absent. | Change the selection logic so modifier-specific modes outrank generic DOMESTIC ties, or include the missing contextual modes that should break the ties (`GROUP` / `SOLO_PAIR`) in these scenes. Then strengthen F8/F9 to assert on the expected example titles or tags rather than only the Layer 5 header. |
| R2-F2 | Medium | The named `Test F12` dormant-mode reachability invariant is still not checked in, even though the runtime now satisfies the reachability requirement. | The canonical Phase F contract still names `Test F12` as the parameterized 11/11 reachability invariant at `Docs/_phases/PHASE_F.md:280`. Grep across the current test suite still finds no `test_f12` or equivalent reachability test, even though a live brute-force probe now confirms all 11 modes are reachable. That leaves the core closure guarantee unguarded against future regression. | Add the promised parameterized reachability invariant test so the 11/11 closure guarantee is enforced in-repo instead of relying on one-off audit probes. |
| R2-F3 | Medium | The canonical Phase F remediation record is still missing, and the new Phase F sample artifacts are still stub-driven placeholder prompts rather than QA-grade retrieval-backed samples. | `Docs/_phases/PHASE_F.md` still shows Step 4 as `PENDING` at `:513-516`, with no remediation trace, no path decision, and no handshake back to Codex. The new sample files exist, but all four still contain `_make_bundle()` placeholders such as `fact_0: value`, `Memory summary 0`, and the stock open loops at `Docs/_phases/_samples/PHASE_F_assembled_adelia_conflict_2026-04-13.txt:170`, `:198`, `:235-236`; `..._alicia_public_...:122`, `:150`, `:188-189`; `..._bina_intimate_...:203`, `:231`, `:269-270`; `..._reina_repair_...:176`, `:204`, `:242-243`. | Fill Step 4 truthfully from the landed remediation work, including the per-finding dispositions and verification delta. Then either regenerate the sample artifacts from a canonical retrieval-backed path, or explicitly label them as stub/local verification artifacts and provide QA-grade samples separately. |

#### Runtime probe summary

- **Verified fixed:** 11/11 `VoiceMode` reachability now closes at the derivation layer.
- **Verified fixed:** the three additive modifiers now exist on `SceneModifiers`.
- **Verified fixed:** `_select_voice_exemplars()` now emits structured DEBUG logging.
- **Verified fixed:** the old stray `Docs/Phase F.md` drift source is gone and the 4 sample files now physically exist.
- **Still open:** Alicia's `warm_refusal` and `group_temperature` live selection paths still choose domestic exemplars.
- **Still open:** `Test F12` is missing and the sample artifacts remain stub-driven placeholders.

#### Drift against specification

- Round 1 `F1` is **mostly fixed**: dormant-mode closure now works at the derivation layer, but the Alicia modifier-specific selection outcome is still wrong.
- Round 1 `F2` is **partially fixed**: F6-F11-style coverage landed, but F8/F9 are too weak and F12 is still missing.
- Round 1 `F3` is **partially fixed**: sample artifacts now exist and the stray plan file is gone, but the canonical Step 4 record is still absent and the sample artifacts are not QA-grade.
- Round 1 `F4` is **fixed**: structured logging is now present in `_select_voice_exemplars()`.

#### Verified resolved

- `SceneModifiers` now carries `warm_refusal_required`, `silent_register_active`, and `group_temperature_shift`.
- `derive_active_voice_modes()` now derives `intimate`, `conflict`, `repair`, `silent`, `escalation`, `warm_refusal`, and `group_temperature` without the manual `scene.voice_modes` escape hatch.
- The live selector now chooses the intended conflict/intimate/repair/escalation exemplars for Adelia, Bina, and Reina on the probed paths.
- 4 Phase F sample artifacts now exist under `Docs/_phases/_samples/`.
- Unit-test totals increased from `205` to `219` and remain clean.

#### Adversarial scenarios constructed

1. **11/11 reachability sweep:** brute-forced all current `SceneType` values across all implemented modifier booleans. Result: all 11 `VoiceMode`s are now reachable.
2. **Alicia warm-refusal selector probe:** activated `warm_refusal_required=True` on the real Alicia Voice corpus. Result: the live selector still chose domestic Examples 1 and 2 instead of warm-refusal Examples 4 or 9.
3. **Alicia group-temperature selector probe:** activated `group_temperature_shift=True` in a multi-woman scene. Result: the live selector still chose domestic Examples 1 and 2 instead of Example 6.
4. **Conflict/intimate/escalation spot-checks:** re-ran Adelia conflict, Bina intimate, and Reina escalation scenes. Result: those selector paths now choose the expected mode-tagged exemplars.
5. **Artifact provenance check:** searched the 4 new `PHASE_F_assembled_*` files for placeholder retrieval content. Result: all 4 still contain the unit-test stub canon/memory/open-loop placeholders.

#### Recommended remediation order

1. Fix `R2-F1` first. It is the only remaining user-facing runtime quality defect on the live selector path.
2. Fix `R2-F2` next by adding the missing F12 invariant and tightening F8/F9 to assert the actual selected examples.
3. Fix `R2-F3` last so the canonical record and QA sample surface catch up to the landed runtime.

#### Gate recommendation

**FAIL**

Phase F is much closer. The major Round 1 blocker is closed, but the Alicia modifier-specific selector paths still do not produce the intended exemplars and the test/record surface is not yet strong enough to prove shippable convergence.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 2 complete. FAIL. Verified fixed: 11/11 mode reachability, additive modifiers, structured selector logging, and physical Phase F sample files. Remaining: R2-F1 High (Alicia warm_refusal/group_temperature still select domestic exemplars because DOMESTIC ties win), R2-F2 Medium (F12 reachability invariant still missing and F8/F9 are too weak), R2-F3 Medium (Step 4 canonical record still missing and samples are stub-driven placeholders). Ready for remediation Round 2. -->

---

## Step 5: QA (Claude AI)

**[STATUS: PENDING]**
**Owner:** Claude AI
**Reads:** All prior steps, landed code, sample artifacts
**Writes:** This section with ship recommendation

---

## Step 6: Ship (Project Owner)

**[STATUS: PENDING]**
**Owner:** Project Owner
**Writes:** Final ship marker

---

## Closing Block (locked once shipped)

**Phase identifier:** F
**Final status:** _pending_
**Total cycle rounds:** _pending_
**Total commits:** _pending_
**Test delta:** _pending_
**Soul architecture impact:** Phase F activates the 7 dormant VoiceModes from Phase E, closing the F2 carry-forward. Four-register soul architecture remains intact; Phase F does NOT add a fifth register, it activates what Phase E authored.
