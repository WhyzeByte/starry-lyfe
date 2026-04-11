# Soul Preservation Plan — Elevated

**Version:** 7.1.1
**Date:** 2026-04-10
**Supersedes:** `SOUL_PRESERVATION_PLAN.md` v1.0
**Source diagnostic:** `Docs/Soul_Perservation.md` (note: filename typo preserved for cross-reference; the canonical spelling is "Preservation")
**Supporting audit:** `Docs/BINA_CONVERSION_AUDIT.md`
**Authored by:** Claude (Opus 4.6) during the v7.1 audit-and-elevation pass

---

## Purpose Of This Elevation

The original `SOUL_PRESERVATION_PLAN.md` is directionally correct and Vision-aligned, but a phase-by-phase audit against `Starry-Lyfe_Vision_v7.1.md` and the runtime findings in `BINA_CONVERSION_AUDIT.md` surfaced three classes of issues:

1. **Missing coverage** of runtime correctness defects that Plan v1.0 does not address because they are not structural or budget issues — they are logic bugs in the context assembler that must be fixed before the Plan's quality work can land cleanly.
2. **Under-specification** in phases A, C, F, G, and H where work items say "do X" without committing to a specific algorithm, test methodology, or fallback behavior.
3. **Dependency ordering** where Phase I (Authority Split Resolution) is prioritized Low despite being prerequisite to Phase E (Voice Exemplar Restoration).

This elevated plan supersedes the v1.0 plan. It preserves the v1.0 phase identifiers (A through I) for backward reference, adds three new phases (A', J, K), corrects the dependency graph, and specifies implementation detail where the v1.0 plan left it open.

**The closing line of v1.0 is preserved verbatim because it is the correct nine-word Vision-alignment statement for this entire body of work:**

> *The edges are necessary. The soul is the point.*

---

## Current Project State (Baseline)

Before detailing phases, the elevated plan anchors against the current state of the backend as of 2026-04-10:

- **Phase 1 (Canon YAML) COMPLETE** — 6 canon files (`characters.yaml`, `pairs.yaml`, `dyads.yaml`, `protocols.yaml`, `interlocks.yaml`, `voice_parameters.yaml`) with Pydantic schemas in `src/starry_lyfe/canon/`
- **Phase 2 (Memory Service) COMPLETE** — 7 memory tiers in PostgreSQL schema `starry_lyfe`, pgvector HNSW for episodic memories, Alicia-orbital dyad persistence logic, exponential decay for Tier 7
- **Phase 3 (Context Assembly) IN PROGRESS** — `kernel_loader.py`, `layers.py`, `assembler.py`, `budgets.py`, `constraints.py` exist and function; current test suite is 73 passing
- **Phase 4 (Whyze-Byte), Phase 5 (Scene Director), Phase 6 (Dreams), Phase 7 (HTTP service on port 8001)** — PLANNED, not implemented

This elevated plan operates on the **existing** Phase 3 code. It is a quality-and-correctness pass on an implementation that already runs, not greenfield design.

**Character kernel canon status:**
- `Characters/Adelia/Adelia_Raye_v7.1.md` — v7.1 canonical, verified clean
- `Characters/Bina/Bina_Malek_v7.1.md` — v7.1 canonical, parents named Malek (corrected during cleanup; `BINA_CONVERSION_AUDIT.md` Finding 1 is stale and that specific bullet is closed)
- `Characters/Reina/Reina_Torres_v7.1.md` — v7.1 canonical
- `Characters/Alicia/Alicia_Marin_v7.1.md` — v7.1 canonical
- `Characters/Shawn/Shawn_Kroon_v7.0.md` — deliberately excluded per operator instruction; Shawn = Whyze (same person, legal-name filesystem artifact only)

**Alicia residence framing:** Alicia is a **resident** at the property who is **frequently away on consular operations**. Her dyads activate when she is home. This is settled canon. Any prose that calls her "non-resident" or "visiting twice yearly" is stale and should be updated if encountered.

---

## Vision Alignment Matrix

Every phase in this plan must be traceable to a specific section of `Starry-Lyfe_Vision_v7.1.md`. The matrix below makes each phase's Vision authority explicit, so Claude Code (or any other implementer) can verify alignment before acting.

| Phase | Primary Vision authority | Supporting authority |
|---|---|---|
| A | §8 System Architecture, §7 Behavioral Thesis (cognitive hand-off contract) | `Persona_Tier_Framework_v7.1.md` §2 (Tier 1 structural integrity) |
| A' | §6 Relationship Architecture (Rule of One, Talk-to-Each-Other), §7 Behavioral Thesis | `BINA_CONVERSION_AUDIT.md` findings 4, 5, 7 |
| B | §8 System Architecture, §9 Success Criteria (response quality, agent sovereignty) | `IMPLEMENTATION_PLAN_v7.1.md` §4 (terminal constraint anchoring) |
| C | §5 Chosen Family (non-redundancy), §6 Relationship Architecture (interlocks) | Character Pair files (canonical pair documents) |
| D | §5 Chosen Family comparison table (pair mechanism, core metaphor) | `pairs.yaml` canon |
| E | §9 Success Criteria (response quality, agent sovereignty) | Character Voice files |
| F | §6 Relationship Architecture, §7 Behavioral Thesis (Rule of One) | `Persona_Tier_Framework_v7.1.md` §2.1 (children gate) |
| G | §9 Success Criteria (life authenticity) | §5 Chosen Family |
| H | §9 Success Criteria (agent sovereignty: "Bina could never be mistaken for Adelia") | `BINA_CONVERSION_AUDIT.md` |
| I | §8 System Architecture (production authority split) | `IMPLEMENTATION_PLAN_v7.1.md` §1 |
| J | §5 Chosen Family (per-character non-redundancy) | Per-character audit documents |
| K | §9 Success Criteria (Ultimate Test: "Does Whyze forget he is talking to software?") | — |

---

## Corrected Phase Dependency Graph

```
Phase 0: Pre-flight Canon Verification  (NEW - baseline before touching code)
    |
Phase A: Structure-Preserving Compilation
    |
Phase A': Runtime Correctness Fixes  (NEW - BINA audit findings 4, 5, 7)
    |
Phase B: Budget Elevation (with terminal anchoring preserved)
    |
Phase I: Authority Split Resolution  (MOVED - now prerequisite to Phase E)
    |
    +---- Phase C: Soul Cards  (largest new capability)
    |         |
    +---- Phase D: Live Pair Data  (small fix, high value)
    |         |
    +---- Phase E: Voice Exemplar Restoration  (depends on Phase I)
    |
Phase F: Scene-Aware Section Retrieval + children_gated as modifier
    |
Phase G: Dramaturgical Prose Rendering (per-character templates)
    |
Phase J: Per-Character Remediation Passes  (NEW - Bina first, then others)
    |
Phase H: Soul Regression Tests (with negative cross-character tests)
    |
Phase K: Subjective Success Proxies  (NEW - operationalizes §9 Ultimate Test)
```

**Key ordering changes from v1.0:**

- **Phase 0 added** — pre-flight canon verification catches drift before the Plan's work starts modifying code
- **Phase A' added** — runtime correctness fixes must land before budget or quality work; they unblock Phase H (tests need correct runtime)
- **Phase I moved to before Phase E** — Phase E's ability to carry abbreviated voice exemplars depends on the authority split decision
- **Phase J added** — character-specific remediation operates on the concrete audit findings for each character; Bina first because her audit exists
- **Phase K added** — acknowledges that Vision §9's Ultimate Test is subjective by design and builds scaffolding around it rather than pretending a hard metric exists
- **Phase H moved** — moved after Phase J so per-character remediation has time to land before tests lock in behavior

---

## Phase 0: Pre-flight Canon Verification (NEW)

**Priority:** Prerequisite. Run before touching any code.
**Vision authority:** §5 Chosen Family, §6 Relationship Architecture, §7 Behavioral Thesis

This phase is a lightweight verification pass that catches canon drift between the source-of-truth files and what subsequent phases will assume. It does not modify code or canon; it produces a "clean" or "not clean" verdict and a list of items to fix before Phase A starts.

### Work items

1. **Run the v7.0 drift grep** from `Claude_Code_Handoff_v7.1.md` §8.1 across `src/`, `Docs/`, `Characters/`, `Vision/` (excluding `Characters/Shawn/`, per-character Vision directive files, and the Vision changelog appendix). Any match is a failure that must be resolved before proceeding.

   **Additional drift terms (added during REINA audit integration 2026-04-10):** the following stale Alicia framing phrases must also be grepped, because they were found in `Reina_Torres_Kinetic_Pair.md` L256 during the REINA audit and were not in the original drift token list:
   - `non-resident` (when applied to Alicia)
   - `twice yearly between operations`
   - `Spanish consular officer`
   - `based in Madrid`
   - `Alicia Marín` (with the diacritic; canonical form is `Alicia Marin` unaccented)
   - `_v7.0.md` cross-references in Pair/Knowledge files (canonical form is `_v7.1.md` for all four characters; Shawn is the only legitimate `_v7.0.md` exception)
   
   These terms slipped through the earlier multi-session cleanup because they were buried inside long sentences in pair file ecosystem-description sections. Phase 0 must catch them before any further work begins.

2. **Verify character kernel canonical state** by running this specific check for each of the four v7.1 characters:
   - Kernel mentions the correct canonical pair name (Entangled, Circuit, Kinetic, Solstice)
   - Kernel mentions no v7.0 pair names (Golden, Citadel, Synergistic, Elemental) except as deliberate historical references with rename annotations
   - Kernel surname and parents' surname match `characters.yaml`
   - Kernel §3 heading matches the canonical pair name
   - Kernel §5 behavioral tier framework references `Persona_Tier_Framework_v7.1.md` (not `_v7.md`)

3. **Verify Vision-kernel consistency** across the four characters. For each character, compare the Vision §5 one-paragraph summary against the character kernel §2 Core Identity. Flag drifts where the Vision summary is stale or the kernel is ahead. **Specific known drift (from `BINA_CONVERSION_AUDIT.md` Finding 7):** Vision says Bina is "Canadian-born Assyrian"; kernel says "born in Urmia, Iran, brought out by her parents in the early nineties." Resolve toward "Canadian-born Assyrian from Urmia" (both true) and update whichever source is stale.

4. **Verify canon YAML consistency** with character kernels. `characters.yaml` field values for each character must match the kernel's canonical statement of the same field. Specific fields to check: `surname`, `parents`, `birthplace`, `pair_name`, `pair_classification`, `pair_mechanism`, `pair_core_metaphor`.

5. **Verify Alicia residence framing** is consistent across all files. Canonical statement: Alicia is a **resident** at the property who is **frequently away on consular operations**. Any file describing her as "non-resident" or "visiting twice yearly" is stale and must be updated.

### Exit criteria

- Zero drift grep hits
- Zero Vision-kernel drifts (or all drifts explicitly resolved with a written decision)
- Zero canon YAML vs kernel mismatches
- Zero stale Alicia framing

### Files touched

No code changes. Output is a verification report, optionally committed to `Docs/Phase_0_Verification_Report_{date}.md`.

---

## Phase A: Structure-Preserving Compilation (ELEVATED)

**Priority:** Highest. More important than raising budgets. If the structure is damaged, more tokens of damaged text is still damaged text.
**Vision authority:** §8 System Architecture, §7 Behavioral Thesis
**v1.0 mapping:** Recommendation 1

### Current state

`src/starry_lyfe/context/budgets.py` function `trim_text_to_budget()` splits the input on whitespace and rejoins with spaces. Section-aware compilation in `kernel_loader.py` picks the right sections but the resulting text loses headings, paragraph boundaries, bullets, and internal hierarchy.

### Work items

1. **Rewrite `trim_text_to_budget()` to preserve markdown structure.** The function operates at the paragraph level, not the word level. Pseudocode:

   ```
   function trim_markdown_to_budget(text, token_limit):
       blocks = split_into_blocks(text)  # heading, paragraph, list, code, quote
       if total_tokens(blocks) <= token_limit:
           return text
       # Blocks are dropped from end toward start, never mid-block
       while total_tokens(blocks) > token_limit:
           dropped = blocks.pop()  # drop trailing block
           if dropped.type == "heading" and not blocks:
               raise TrimError("cannot trim below first heading")
       return reassemble(blocks)
   ```

2. **Define block types and their trim priority.** Blocks are one of: `h1`, `h2`, `h3`, `paragraph`, `bullet_list`, `numbered_list`, `code_block`, `blockquote`, `horizontal_rule`. When trimming, drop in this priority order (from first-to-drop to last-to-drop):
   1. Trailing `horizontal_rule` separators
   2. Trailing `paragraph` blocks within the last subsection
   3. Trailing `bullet_list` / `numbered_list` items (drop list items one at a time, not the whole list)
   4. Trailing `blockquote` blocks
   5. Trailing `code_block` blocks
   6. The entire trailing subsection (`h3` and its content) if nothing else fits
   7. The entire trailing section (`h2` and its content) as last resort

3. **Specify fallback behavior for oversized sections.** If a single `h2` section is larger than its per-section budget, the compiler must:
   - Drop `h3` subsections from end to start
   - Drop paragraphs within the last remaining subsection from end to start
   - Never mid-paragraph cut
   - If dropping everything except the `h2` heading still exceeds budget, raise a `KernelCompilationError` with the section name — this is an authoring problem, not a runtime problem

4. **Update `compile_kernel()` in `kernel_loader.py`** to call the new paragraph-aware trim per section instead of the whitespace trim.

5. **Add an exemption list for constraint-like content.** Specific blocks within the kernel carry behavioral rules that must survive trimming regardless of budget pressure. Mark these with an HTML comment marker `<!-- PRESERVE -->` in the kernel markdown, and have the compiler refuse to drop marked blocks. Use this sparingly — no more than 200 tokens of preserved content per kernel.

### Test cases

Three unit tests are required before merging Phase A:

- **Test A1 (exact fit):** A 1500-token input with a 2000-token budget returns unchanged.
- **Test A2 (oversized section):** A 4000-token input where §2 alone is 3000 tokens, compiled to a 2000-token budget, produces output that still contains the §2 `h2` heading, the first paragraph, and no mid-paragraph cuts.
- **Test A3 (preserved markers):** A kernel with a `<!-- PRESERVE -->` marker in §5 where §5 would normally be dropped, compiled to a tight budget, produces output that still contains the marked block.

### Files touched

- `src/starry_lyfe/context/budgets.py` — rewrite `trim_text_to_budget()`
- `src/starry_lyfe/context/kernel_loader.py` — update `compile_kernel()` to use the new trim
- `tests/unit/test_budgets.py` — add test cases A1, A2, A3
- Kernel markdown files — optional, add `<!-- PRESERVE -->` markers around load-bearing blocks as a separate PR after the compiler supports them

---

## Phase A': Runtime Correctness Fixes (NEW)

**Priority:** Blocker. Must land before Phase B. These are runtime defects surfaced by `BINA_CONVERSION_AUDIT.md`, not quality improvements. The Plan's quality work cannot land cleanly on a buggy substrate.
**Vision authority:** §6 Relationship Architecture (Rule of One, Talk-to-Each-Other Mandate), §7 Behavioral Thesis

### Work items

1. **Fix Talk-to-Each-Other mandate trigger** (`BINA_CONVERSION_AUDIT.md` Finding 4 / `ADELIA_CONVERSION_AUDIT.md` Finding 3).

   **STATUS: VERIFIED RESOLVED as of 2026-04-10 REINA audit.** The REINA audit Verified Resolved section explicitly confirms: *"Solo `Reina + Whyze` scenes do not get the `TALK-TO-EACH-OTHER` mandate. The gate lives in `src/starry_lyfe/context/constraints.py:104` and the current test coverage exists in `tests/unit/test_assembler.py:229-240`."* The fix has been implemented in code between when the BINA/ADELIA audits were written and when the REINA audit was written. The original work item is preserved below as historical record.

   **Original (now-resolved) behavior:** `src/starry_lyfe/context/constraints.py` added the Talk-to-Each-Other block whenever `len(scene_state.present_characters) > 1`. For a two-person Bina+Whyze scene, this fired the mandate that *"a meaningful exchange must pass between the women directly"* — but there was only one woman in the scene, making the instruction impossible.

   **Required behavior:** The mandate should fire only when at least two *women* (not two *characters*, which can include Whyze) are present. Whyze does not count toward the woman count for the purpose of this mandate.

   **Canonical authority:** Vision §6 Rule of One and Talk-to-Each-Other Mandate phrasing: *"In multi-character scenes, all present characters must not simultaneously address Whyze, and at least one meaningful exchange per scene must pass between the women directly."* The phrase "between the women" requires at least two women.

   **Implementation:**
   ```python
   # in constraints.py
   def should_include_talk_to_each_other(scene_state):
       women_present = [c for c in scene_state.present_characters
                        if c in ("adelia", "bina", "reina", "alicia")]
       return len(women_present) >= 2
   ```

2. **Fix offstage dyad leakage** (`BINA_CONVERSION_AUDIT.md` Finding 5 / `ADELIA_CONVERSION_AUDIT.md` Finding 4).

   **STATUS: VERIFIED RESOLVED as of 2026-04-10 REINA audit.** The REINA audit Verified Resolved section explicitly confirms: *"Offstage dyads do not appear to leak into Layer 6. Internal dyads are only included when the other woman is present in `src/starry_lyfe/context/layers.py:232-240`, and live probing did not surface `reina-bina` in a `Reina + Whyze` scene."* The ALICIA audit also independently confirmed: *"Offstage dyads did not leak in my live Alicia-Whyze probes."* The fix has been implemented in code. The original work item is preserved below as historical record.

   **Original (now-resolved) behavior:** `src/starry_lyfe/db/retrieval.py` loaded all active internal dyads for the focal character. `src/starry_lyfe/context/layers.py` then included an internal dyad if either member was present. Because the focal character was always present in her own prompt, a Bina-Reina dyad appeared even when Reina was not in the room.

   **Required behavior:** An internal dyad block should only appear in the assembled prompt when **both members** of the dyad are present in the current scene, OR when the scene explicitly invokes a memory or reference to an absent dyad member (e.g., Bina thinking about Reina while Reina is at court).

   **Canonical authority:** Vision §6 Relationship Architecture: interlocks are *"first-class architectural elements codified directly into routing and prompt assembly"* — which means they must reflect the actual present scene, not every dyad the focal character is in.

   **Implementation:**
   ```python
   # in layers.py
   def should_include_internal_dyad(dyad, scene_state):
       both_present = (dyad.member_a in scene_state.present_characters
                       and dyad.member_b in scene_state.present_characters)
       explicitly_recalled = dyad.key in scene_state.recalled_dyads
       return both_present or explicitly_recalled
   ```

   This requires adding a `recalled_dyads: set[str]` field to `SceneState` for cases where the scene explicitly invokes a reference to an absent dyad member. Default is empty set; scene descriptions can populate it when needed.

3. **Resolve Vision-vs-kernel Bina origin drift** (`BINA_CONVERSION_AUDIT.md` Finding 7).

   **Current state:** Vision §5 says Bina is "Canadian-born Assyrian". Kernel and canon YAML say "born in Urmia, Iran, brought out by her parents in the early nineties."

   **Canonical resolution:** Both are true — Bina was born in Urmia, Iran and her parents brought her to Canada as a toddler. She grew up in Canada, making her Canadian-raised Assyrian by cultural identity but not Canadian-born by literal birth. The Vision summary is stale shorthand.

   **Remediation:** Update Vision §5 Bina paragraph to read "Iran-born Assyrian-Canadian, raised in Canada from the early nineties" or similar precise phrasing that matches the kernel's canonical detail. This is a one-line Vision edit.

4. **Verify no similar Vision-vs-kernel drifts exist for Adelia, Reina, or Alicia.** Run a targeted consistency check: Vision §5 one-paragraph summary vs kernel §2 Core Identity first paragraph, for each of the other three characters. Flag any drifts. Resolve any found drifts the same way as Bina.

5. **Add Adelia and Reina live `assemble_context()` tests** (audit-driven addition from `ADELIA_CONVERSION_AUDIT.md` Finding 8). The current Phase 3 test suite has live `assemble_context()` coverage for Bina and Alicia only. Adelia and Reina have NO live assemble-level tests. Add minimal smoke tests for both:
   - `tests/unit/test_assembler.py::test_assemble_context_adelia_solo_pair` — assert basic assembly succeeds, terminal anchoring holds, no Msty artifacts present
   - `tests/unit/test_assembler.py::test_assemble_context_reina_solo_pair` — same shape for Reina
   These are minimum viable tests, not the per-character regression bundles from Phase H. The point is to give Phase H a working baseline to extend, and to catch the failure mode where Adelia or Reina assembly silently breaks because nothing is watching them.

### Test cases

- **Test A'1:** Bina+Whyze two-person scene assembles without the Talk-to-Each-Other mandate block
- **Test A'2:** Bina+Reina+Whyze three-person scene assembles WITH the Talk-to-Each-Other mandate block
- **Test A'3:** Bina+Whyze scene does NOT include a bina-reina dyad block unless `SceneState.recalled_dyads` contains `"bina-reina"`
- **Test A'4:** Bina+Whyze scene WITH `recalled_dyads={"bina-reina"}` DOES include a bina-reina dyad block (for the "Bina thinking about Reina while Reina is at court" case)

### Files touched

- `src/starry_lyfe/context/constraints.py` — fix Talk-to-Each-Other mandate trigger
- `src/starry_lyfe/context/layers.py` — fix offstage dyad filter
- `src/starry_lyfe/context/types.py` — add `recalled_dyads` field to `SceneState`
- `Vision/Starry-Lyfe_Vision_v7.1.md` — fix Bina origin drift (one-line edit)
- `tests/unit/test_assembler.py` — add test cases A'1 through A'4

---

## Phase A'': Communication-Mode-Aware Pruning (NEW — from ALICIA audit)

**Priority:** Blocker. Must land before Phase B for Alicia specifically. Blocks Phase E voice exemplar work for Alicia until resolved.
**Vision authority:** §5 Chosen Family (Alicia's intermittent presence as canonical), §6 Relationship Architecture (Solstice Pair as the only intermittent pair)
**Source:** `ALICIA_CONVERSION_AUDIT.md` Finding 1 (High severity)

### Why this phase exists

The ALICIA audit surfaced a runtime defect that none of the BINA, ADELIA, or REINA audits caught because none of the other characters have a canonical communication-mode-conditional architecture. The defect:

The current assembly path uses `communication_mode` only to **block** in-person Alicia prompts while she is away on operations. Once the prompt is **allowed** (phone, letter, video call), the rest of the assembly runs identically to in-person mode. This creates a live contradiction: Alicia's constraint pillar requires *"Somatic contact first, speech after the shift completes"* — but during a phone call from a hotel room overseas, somatic contact is **literally impossible**. The body cannot close the distance because there is no distance to close.

The audit confirms this is not theoretical. Live probing showed that an away-state phone prompt still carried:
- The full Solstice constraint text requiring body-first somatic intervention
- `Example 3: The Sun Override On Whyze (Four-Signal Form)` (an in-person example)
- `Example 5: Four-Phase Return, The Kitchen With Him` (an in-person example)

The result is that Alicia's remote scenes are currently shaped by in-person body mechanics that the scene literally cannot perform. This is the highest-severity new finding across all four character audits, and it requires a new architectural mechanism, not a bug fix.

### What this phase does NOT cover

This phase only addresses Alicia. The other three characters do not currently have communication-mode-conditional canonical architecture — their voice exemplars and constraint pillars assume in-person presence as the default and don't carry mode-specific instructions. If future canon changes introduce mode-specific behavior for any other character, this phase's infrastructure can be reused, but for now the phase is Alicia-specific.

### Work items

1. **Add `communication_mode` filtering to Layer 7 constraint rendering.**

   The constraint pillar block in `src/starry_lyfe/context/constraints.py` currently emits Alicia's full pillar text regardless of `communication_mode`. The new behavior:
   - When `communication_mode == IN_PERSON` (or unset), emit the full pillar including somatic-first language
   - When `communication_mode == PHONE` or `LETTER` or `VIDEO_CALL`, emit a substituted pillar that translates the somatic-first principle into mode-appropriate form

   Specifically for Alicia, the substituted phone pillar should read along the lines of: *"Voice carries the regulation when the body cannot. Pace, breath, weight in the words. Listen for the shift before reaching for the next sentence. Do not narrate the body you do not have access to."*

   The substituted letter pillar should read: *"Letters are weight made of paragraphs. Take the time the page demands. The body she is regulating is hers, written from inside the place she is in, not his, narrated from outside."*

   The substituted video pillar reads as a hybrid: visual presence is real but contact is not, so the body anchors are eye contact and posture rather than touch and breath.

2. **Add `communication_mode` filtering to Layer 5 voice exemplar selection.**

   Each voice example in `Characters/Alicia/Alicia_Marin_Voice.md` gets a new tag alongside the existing mode tags (Phase E):

   ```markdown
   ## Example 5: Four-Phase Return, The Kitchen With Him
   <!-- mode: domestic, intimate -->
   <!-- communication_mode: in_person -->
   ```

   Valid `communication_mode` tag values (closed enum):
   - `in_person` — the example assumes physical presence; do not include in remote-mode prompts
   - `phone` — the example is a phone-call exemplar
   - `letter` — the example is a written-letter exemplar
   - `video_call` — the example is a video-call exemplar
   - `any` — the example works in any mode (default if no tag is specified, but this should be rare; most exemplars are mode-specific in Alicia's case)

   The exemplar selector filters by both `mode` (scene type) AND `communication_mode` (channel) before selecting up to N exemplars per active scene mode.

3. **Author phone, letter, and video-call exemplars for Alicia.**

   Alicia's current `Voice.md` contains 10 examples, all of which are implicitly `in_person`. The audit's recommended remediation explicitly calls for *"communication-mode-aware pruning for Alicia phone and letter scenes."* This requires authoring new exemplars:
   - At least 2 phone exemplars covering: away-state late-night call, away-state operational debrief, away-state intimate phone moment
   - At least 2 letter exemplars covering: long letter from operational posting, short letter as somatic anchor (a postcard from Bogotá)
   - At least 1 video-call exemplar (transitional between in-person and phone in terms of available regulation tools)

   These are human-authored, not auto-generated. They live in `Characters/Alicia/Alicia_Marin_Voice.md` as new `## Example N` blocks tagged with the appropriate `communication_mode`.

4. **Wire `communication_mode` through `assembler.py`.** The `SceneState` already has a `CommunicationMode` field per the `ARCHITECTURE.md` documentation. The assembler currently uses it only for the in-person block gate during Alicia's away state. Extend usage so that:
   - `format_constraints()` receives `communication_mode` and selects the mode-appropriate constraint variant
   - `format_voice_directives()` receives `communication_mode` and filters exemplars by their `communication_mode` tag

5. **Add cross-character regression tests** to ensure communication-mode filtering does not accidentally leak into Adelia, Bina, or Reina prompts. None of them currently have communication-mode-tagged exemplars, so the filter should be a no-op for them. A test that confirms this prevents future drift if someone adds a tag carelessly.

### Test cases

- **Test A''1:** A live Alicia phone-mode prompt (away state, communication_mode=PHONE) does NOT contain the substring "Somatic contact first" or "close the distance"
- **Test A''2:** The same phone-mode prompt DOES contain the substituted phone pillar phrase about voice carrying the regulation
- **Test A''3:** Examples 3 and 5 from Alicia's Voice.md (the in-person Sun Override and Four-Phase Return kitchen exemplars) do NOT appear in a phone-mode prompt
- **Test A''4:** A phone-mode-tagged exemplar (once authored) DOES appear in a phone-mode prompt
- **Test A''5:** A Bina phone-mode prompt is structurally identical to a Bina in-person prompt (no Alicia-style filtering bleeds into other characters)
- **Test A''6:** Letter-mode and video-mode prompts each receive their own substituted pillar text and exemplar selection

### Files touched

- `src/starry_lyfe/context/constraints.py` — add communication-mode-aware pillar substitution for Alicia
- `src/starry_lyfe/context/layers.py` — update `format_voice_directives()` to filter by `communication_mode` tag
- `src/starry_lyfe/context/kernel_loader.py` — update voice example parser to extract `communication_mode` tag alongside `mode` tag
- `src/starry_lyfe/context/assembler.py` — wire `communication_mode` through to layer formatters
- `src/starry_lyfe/context/types.py` — add `CommunicationMode` enum if not already present in canonical form
- `Characters/Alicia/Alicia_Marin_Voice.md` — author phone/letter/video-call exemplars (human authoring work)
- `tests/unit/test_assembler.py` — add tests A''1 through A''6

### Phase ordering implications

Phase A'' must land before Phase E for Alicia, because Phase E's mode-tagged exemplar selection assumes a single tag dimension (`mode`). Phase A'' adds a second tag dimension (`communication_mode`) and changes the selection algorithm. If Phase E ships first without Phase A'', the Phase E work would need to be reworked to add the second dimension.

Phase A'' does NOT block Phase A, A', or B for the other three characters — it only blocks Phase E for Alicia. Adelia, Bina, and Reina can proceed through Phase E in parallel with the Phase A'' work.

---

## Phase B: Budget Elevation With Terminal Anchoring Preserved (ELEVATED)

**Priority:** High. The current budgets are an optimization choice, not a model limitation. Claude's 200K context can absorb the elevated budget comfortably.
**Vision authority:** §8 System Architecture, §9 Success Criteria
**Implementation Plan authority:** §4 — *"The character-specific strict constraints must be placed immediately before the user's latest input and the start of the assistant response. Terminal anchoring of constraints is structural, not stylistic."*
**v1.0 mapping:** Recommendation 2

### Correction from v1.0

Plan v1.0 grows Layers 1-6 from ~4800 to ~9700 tokens (a ~100% increase) while keeping Layer 7 Constraints flat at 500 tokens. **This weakens the effective recency of the constraint block** because the absolute distance from the constraint block to the start of the prompt grows, even though Layer 7 remains last in order. The canonical rule is that constraints must be *immediately* before the user's latest input, and "immediately" degrades as earlier layers grow.

**The elevated plan grows Layer 7 proportionally** so the constraint block has enough room to carry full Tier 1 axioms, per-character constraint pillars, and scene gates in clear detailed prose rather than compressed one-liners.

### Work items

1. **Raise default budgets** in `src/starry_lyfe/context/budgets.py`:

   | Layer | v1.0 Current | v1.0 Proposed | **Elevated Proposed** | Rationale |
   |-------|-------------:|--------------:|----------------------:|-----------|
   | Kernel (L1) | 2000 | 6000 | **6000** | ~45% of kernel survives; all primary sections fully rendered |
   | Canon Facts (L2) | 500 | 500 | **600** | Room for narrative canon rendering (Phase G) |
   | Episodic (L3) | 1000 | 1000 | **1200** | Room for more retrieved memories at better fidelity |
   | Somatic (L4) | 300 | 400 | **500** | Room for protocol detail + dramaturgical prose (Phase G) |
   | Voice (L5) | 200 | 800 | **900** | 100 tokens baseline metadata + 800 tokens for 5-7 exemplars |
   | Scene (L6) | 800 | 1000 | **1200** | Room for dramaturgical dyad prose + scene-aware section promotions |
   | Constraints (L7) | 500 | 500 | **900** | **CRITICAL: grows proportionally to preserve terminal anchoring** |
   | **Total** | **5300** | **10200** | **11300** | ~5.6% of 200K context |

   The elevated total (11300 tokens) is still well under 10% of Claude's 200K context window. Salience dilution is not a concern at this budget; the concern was real at the original 5300 figure and is even less real now that the elevated budget is structure-preserving.

2. **Update `SECTION_TOKEN_TARGETS`** in `kernel_loader.py` to expand proportionally. The elevated per-section targets:

   | Section | v1.0 Current | Elevated |
   |---|---:|---:|
   | §1 Runtime Directives | 240 | **300** |
   | §2 Core Identity | 400 | **900** |
   | §3 Pair section | 420 | **1000** |
   | §4 Silent Routing | 180 | **250** |
   | §5 Behavioral Tier Framework | 380 | **900** |
   | §6 Voice Architecture | 120 | **300** |
   | §7 Frameworks | 220 | **550** |
   | Sections 8-11 as fill | — | **1800** (shared) |
   | **Total primary sections** | **1960** | **4200** |
   | **Fill budget** | ~40 | **1800** |
   | **Per-kernel total** | **2000** | **6000** |

3. **Add per-character budget tuning.** Current kernels are not equal in size:
   - Adelia kernel: ~12.9k tokens (diagnostic estimate)
   - Bina kernel: ~14.9k tokens
   - Reina kernel: ~14.1k tokens
   - Alicia kernel: ~10.3k tokens

   At a flat 6000-token kernel budget, Bina compresses more aggressively (~40% survives) than Alicia (~58% survives). This is unfair to the longer kernels. The elevated plan adds **per-character budget scaling** so the survival rate is approximately equal across characters:

   ```python
   # in budgets.py
   CHARACTER_KERNEL_BUDGET_SCALING = {
       "adelia": 1.05,   # 6000 * 1.05 = 6300 target
       "bina":   1.20,   # 6000 * 1.20 = 7200 target (longest kernel)
       "reina":  1.15,   # 6000 * 1.15 = 6900 target
       "alicia": 0.85,   # 6000 * 0.85 = 5100 target (shortest kernel)
   }
   ```

   The scaling factors target roughly equal survival rates (~50% of raw kernel content) rather than equal absolute token counts. The total budget grows a small amount (~6400 tokens average vs flat 6000) but the tradeoff is worth it for non-redundancy preservation.

4. **Explicit Layer 5 split.** The current 200-token budget is "shared" between baseline metadata and voice guidance. The elevated 900-token budget is explicitly split:
   - 100 tokens for compact baseline metadata paragraph (pair name, classification, mechanism, core metaphor, response length norm, cultural register summary)
   - 800 tokens for mode-tagged voice exemplars (Phase E)

5. **Add scene budget profiles.** Different scene types benefit from different budget allocations:

   | Scene profile | Kernel | Scene (L6) | Voice (L5) | Rationale |
   |---|---:|---:|---:|---|
   | Default (balanced) | 6000 | 1200 | 900 | General use |
   | Pair-intimate | 8000 | 800 | 700 | More pair architecture, less group context |
   | Multi-woman group | 5500 | 1800 | 1000 | Less kernel, more scene context, more voice range |
   | Children-gated | 5500 | 1400 | 800 | Normal balance minus intimacy sections |
   | Solo (one woman + Whyze) | 7000 | 800 | 900 | More kernel, less group context |

   The Scene Director (Phase 5 of overall backend build) selects the profile based on classified scene state.

### Test cases

- **Test B1:** Assembled prompt token total stays within ±5% of the elevated total budget across all four characters for the default profile
- **Test B2:** Layer 7 constraint block is always rendered last in the assembled prompt regardless of earlier-layer content size
- **Test B3:** Per-character budget scaling produces survival rates within ±10% of each other across all four characters (measured as `compiled_kernel_tokens / raw_kernel_tokens`)
- **Test B4:** Scene profile selection produces the expected layer budgets for each of the 5 profiles

### Files touched

- `src/starry_lyfe/context/budgets.py` — update default budgets, add per-character scaling, add scene profiles
- `src/starry_lyfe/context/kernel_loader.py` — update `SECTION_TOKEN_TARGETS`, apply per-character scaling in `compile_kernel()`
- `src/starry_lyfe/context/assembler.py` — accept scene profile parameter, apply to budget selection
- `tests/unit/test_budgets.py` — add test cases B1 through B4

---

## Phase I: Authority Split Resolution (ELEVATED AND RE-PRIORITIZED)

**Priority:** Prerequisite to Phase E. Must resolve before Phase E (Voice Exemplar Restoration) starts.
**Vision authority:** §8 System Architecture, Implementation Plan §1 Production Authority Split
**v1.0 mapping:** Recommendation 9 (was Low priority in v1.0)

### Why this moved up

Plan v1.0 treats Phase I as *"Low priority (architectural, not urgent)."* That is incorrect. Phase E's central work item is restoring abbreviated voice exemplars to the backend. Whether the backend is **canonically permitted** to carry voice exemplars is exactly what the authority split resolves. If Phase E ships before Phase I, it lands on an unsettled architectural foundation and may need to be redone after Phase I finally resolves the split.

### The question to answer

**Who is the canonical source of voice calibration content?**

Two options, each internally coherent:

**Option 1 — Backend-authoritative voice.** The backend carries abbreviated rhythm-calibration exemplars (2-3 sentence responses sliced from Voice.md) as part of Layer 5. Msty's persona studio few-shots are either empty or canonically generated derivatives of the backend's exemplar set. Voice authority lives in one place: the backend, sourced from `Voice.md`.

**Option 2 — Msty-authoritative voice.** The backend carries only meta-voice notes ("what this example teaches") in Layer 5. Msty's persona studio few-shots carry the full `**User:** / **Assistant:**` pairs and are the canonical rhythm source. Voice authority lives in one place: Msty, sourced from the persona studio configuration (which is itself seeded from `Voice.md` during setup but can drift after).

**The recommendation for the elevated plan: Option 1 (backend-authoritative voice).**

Rationale:
- Implementation Plan §1 is explicit that *"Msty persona system prompts are blank or near-blank in production so the backend remains the sole source of character authority"*
- Option 1 keeps the canonical voice source in one place (`Voice.md` → compiled into backend Layer 5) with no drift surface
- Option 2 creates two voice surfaces (backend rhythm notes + Msty few-shots) and requires a separate drift-prevention mechanism to keep them synchronized
- Option 1 is what Phase E's work item #1 already assumes

### Work items

1. **Write the Architectural Decision Record.** Create `Docs/ADR_001_Voice_Authority_Split.md` containing:
   - Status: ACCEPTED
   - Decision: Backend is canonically authoritative for all voice content
   - Consequences: Msty persona studio few-shots are deprecated in production. Any live Msty few-shot is either empty or a manually-synchronized copy of the backend's compiled exemplars and must not diverge
   - Implementation guidance: Msty persona studio configurations must be seeded from a script that reads `Voice.md` and compiles the same abbreviated exemplars the backend uses, so the two are always identical

2. **Update `CHARACTER_CONVERSION_PIPELINE.md`** to reflect the decision:
   - File 2 (Voice File) section: update to show Voice.md flows into both backend compilation and (via seed script) Msty persona studio
   - Add a "Drift Prevention" note that Msty persona studio configurations are derived artifacts, not source of truth

3. **Update `CLAUDE_CODE_HANDOFF_v7.1.md`** §5.6 to note the authority decision and its implications for Phase E.

4. **Create a canonical seed script** `scripts/seed_msty_persona_studio.py` that compiles abbreviated exemplars from `Voice.md` and produces the Msty persona studio configuration. This script is the only canonical way Msty persona studio should be configured.

### Exit criteria

- ADR_001 committed and ACCEPTED
- `CHARACTER_CONVERSION_PIPELINE.md` updated
- Seed script exists and produces a valid Msty persona studio configuration
- Phase E can begin

### Files touched

- `Docs/ADR_001_Voice_Authority_Split.md` — new file
- `Docs/CHARACTER_CONVERSION_PIPELINE.md` — update
- `Docs/Claude_Code_Handoff_v7.1.md` — update §5.6
- `scripts/seed_msty_persona_studio.py` — new file

---

## Phase C: Soul Cards From Pair And Knowledge Stack (ELEVATED)

**Priority:** High. The Pair files (15-17K tokens each) and Knowledge Stacks (10-80K tokens) contain the deepest character differentiation. Currently excluded from runtime entirely.
**Vision authority:** §5 Chosen Family (non-redundancy), §6 Relationship Architecture (interlocks as first-class elements)
**v1.0 mapping:** Recommendation 3

### Correction from v1.0

Plan v1.0 says to *"build an offline compiler that distills each Pair.md and Knowledge_Stack.md into typed soul cards"* but does not specify the compilation algorithm. Automated distillation introduces drift risk — the same risk the project just spent many cleanup sessions removing. The elevated plan commits to **human-authored soul cards, version-controlled, derived from the source pair/knowledge files**, with automated validation that the soul card references specific canonical concepts from its source.

### Source of truth relationship

- `pairs.yaml` remains the source of truth for structured pair fields (classification, mechanism, core metaphor, what she provides, how she breaks his spiral, cadence, shared functions)
- `Characters/{Name}/{Name}_{Pair}_Pair.md` remains the canonical authored reference for the pair architecture — cognitive interlock theory, synastry, intimate mechanics, scene-read instructions
- **Soul cards are a new artifact** that distill the narrative prose of the pair file and knowledge stack into compact, typed, runtime-loadable blocks
- Soul cards are **stored as markdown files** in `src/starry_lyfe/canon/soul_cards/` and loaded at context assembly time
- Soul cards are **human-authored** and then validated by a test that asserts they mention specific canonical concepts from their source file

### Work items

1. **Create the soul cards directory structure:**
   ```
   src/starry_lyfe/canon/soul_cards/
   ├── pair/
   │   ├── adelia_entangled.md
   │   ├── bina_circuit.md
   │   ├── reina_kinetic.md
   │   └── alicia_solstice.md
   └── knowledge/
       ├── adelia_cultural.md
       ├── adelia_workshop.md
       ├── bina_ritual.md
       ├── bina_grief.md
       ├── reina_stable.md
       ├── reina_court.md
       ├── alicia_rioplatense.md
       ├── alicia_famailla.md
       └── alicia_operational.md
   ```

2. **Define the soul card schema.** Each soul card is a markdown file with YAML frontmatter:

   ```markdown
   ---
   character: bina
   card_type: pair
   source: Characters/Bina/Bina_Malek_Circuit_Pair.md
   budget_tokens: 700
   activation:
     always: true  # for pair cards
   required_concepts:
     - "Circuit Pair"
     - "Orthogonal Opposition"
     - "total division of operational domains"
     - "diagnostic love"
     - "translation not mirroring"
   ---

   # Bina × Whyze — Circuit Pair Soul Card

   [500-700 tokens of hand-authored prose distilling the pair architecture]
   ```

   Frontmatter fields:
   - `character`: one of `adelia`, `bina`, `reina`, `alicia`
   - `card_type`: `pair` or `knowledge`
   - `source`: path to the source file this card is distilled from
   - `budget_tokens`: hard limit; test fails if the card exceeds this
   - `activation`: conditions under which this card loads
     - `always: true` for pair cards (always load for the focal character's pair)
     - `scene_type: [intimate, domestic]` for scene-conditional cards
     - `scene_keyword: ["spanish", "castellano"]` for keyword-triggered cards (e.g., Alicia's Rioplatense card triggers when the scene mentions Spanish)
     - `with_character: ["reina"]` for dyad-triggered cards (e.g., Bina's grief card activates when Bina is in a scene with Reina, because Reina is the witness to that grief)
   - `required_concepts`: list of strings that must appear in the card body; used by the validation test

3. **Implement the soul card loader.** `src/starry_lyfe/context/soul_cards.py` contains:
   ```python
   def load_soul_card(path: Path) -> SoulCard: ...
   def find_activated_cards(character: str, scene_state: SceneState) -> list[SoulCard]: ...
   def format_soul_cards(cards: list[SoulCard], budget: int) -> str: ...
   ```

4. **Integrate with Layer 1 / Layer 6.** The pair soul card for the focal character always loads into Layer 1 (kernel) as a separate subsection, budget-bounded to 700 tokens. Knowledge soul cards load scene-conditionally into Layer 6 (scene context), budget-bounded to 300-500 tokens each, up to the Layer 6 total budget.

5. **Author the four pair soul cards first.** Each pair soul card distills 500-700 tokens of prose from the source pair file:
   - The specific cognitive interlock (Ni-Te-Fi-Se × Ne-Fi-Te-Si for Adelia; Si-Fe-Ti-Ne × Ni-Te-Fi-Se for Bina; etc.)
   - How they fight (the specific canonical conflict pattern)
   - How they repair (the specific canonical repair ritual)
   - What the intimacy is not (anti-pattern exclusions)
   - Scene-read instructions (what the model should notice about the pair)

   **The pair soul cards are authored by the project owner or a knowledgeable human reviewer, not by Claude Code.** The Plan ships with placeholders that fail the validation test until a human writes them. This forces the content to be canonical rather than generated.

6. **Author the knowledge soul cards in priority order.** For each character, start with the single highest-leverage knowledge card:
   - Adelia: `adelia_workshop.md` (the Marrickville workshop, Valencian heritage, Ozone & Ember ethos)
   - Bina: `bina_ritual.md` (samovar, covered plate, hall light, Gilgamesh drawer, Uruk interior)
   - Reina: `reina_stable.md` (Bishop and Vex, Mediterranean reset, body-reader precision beyond generic assertiveness)
   - Alicia: `alicia_rioplatense.md` (Argentine register, Famaillá texture, the operational return mechanics)

   Then proceed to secondary cards as time permits.

7. **Add soul card validation tests.** For each soul card:
   - Token budget test: compiled card must fit within `budget_tokens` frontmatter declaration
   - Required concepts test: card body must mention every string in `required_concepts`
   - Activation test: given a canonical scene state, the card either activates or does not, as expected

### Test cases

- **Test C1:** `adelia_entangled.md` pair card loads for any scene where Adelia is the focal character
- **Test C2:** `bina_ritual.md` knowledge card loads for domestic-intimate scenes where Bina is the focal character and does NOT load for Reina-focal scenes
- **Test C3:** `alicia_rioplatense.md` knowledge card loads when scene description contains "Spanish" or "castellano" regardless of focal character
- **Test C4:** Required concepts test fails when a soul card body does not mention one of its declared required concepts (forces authoring discipline)
- **Test C5:** Token budget test fails when a soul card exceeds its declared `budget_tokens`

### Files touched

- `src/starry_lyfe/canon/soul_cards/` — new directory with 4 pair cards + 9 knowledge cards (placeholders initially; filled by human author)
- `src/starry_lyfe/context/soul_cards.py` — new loader module
- `src/starry_lyfe/context/layers.py` — integrate soul cards into Layer 1 (pair) and Layer 6 (knowledge)
- `src/starry_lyfe/context/assembler.py` — pass scene state through to soul card activation
- `tests/unit/test_soul_cards.py` — new test file with C1-C5

---

## Phase D: Live Pair Data In Prompt (ELEVATED)

**Priority:** Medium. Small fix, high value.
**Vision authority:** §5 Chosen Family comparison table
**v1.0 mapping:** Recommendation 4

### Correction from v1.0

Plan v1.0 says Phase D is *"Partially addressed (pair_mechanism and pair_core_metaphor were added to Layer 5 metadata in Adelia remediation). The user's updated `layers.py` reverted to emitting only `pair_name`, storing but not surfacing the other fields."* This leaves Phase D in an ambiguous state where the work may have been done and reverted for a reason.

**The elevated plan is unambiguous:** surface `pair_mechanism`, `pair_core_metaphor`, `pair_classification`, `what_she_provides`, and `how_she_breaks_his_spiral` in Layer 5 metadata regardless of prior reverts. These fields are canonical from `pairs.yaml` and the Vision §5 comparison table. Any prior decision to hide them was wrong or is now superseded.

### Work items

1. **Update `format_voice_directives()` in `layers.py`** to render a full pair metadata block at the top of Layer 5:

   ```
   PAIR: Circuit Pair
   CLASSIFICATION: Orthogonal Opposition
   MECHANISM: Total division of operational domains
   CORE METAPHOR: The Architect and the Sentinel
   WHAT SHE PROVIDES: Physical grounding, diagnostic care, the road
   HOW SHE BREAKS HIS SPIRAL: Interrupts with concrete sensory input (Si)
   ```

   This is compact (~70 tokens) and canonical — all values come directly from `pairs.yaml` without prose interpretation.

2. **Render the pair metadata block BEFORE the voice exemplars** in Layer 5, not after. The model should see the pair architecture as context before seeing the voice exemplars, so the exemplars are interpreted through the pair lens.

3. **Verify all four pair rows in `pairs.yaml` have complete data** for these five fields. If any row is missing a field, fix the YAML before the Layer 5 change lands.

4. **Remove the `pair_name`-only short form.** The previous revert path that emitted only `pair_name` is deprecated. The full six-field block replaces it.

### Test cases

- **Test D1:** Bina's Layer 5 starts with a pair metadata block containing all six lines (pair name, classification, mechanism, core metaphor, what she provides, how she breaks his spiral)
- **Test D2:** The pair metadata block is identical in format across all four characters (only the values differ)
- **Test D3:** Layer 5 for any character contains the pair metadata block BEFORE any voice exemplar content

### Files touched

- `src/starry_lyfe/context/layers.py` — update `format_voice_directives()`
- `src/starry_lyfe/canon/pairs.yaml` — verify complete data, fix any missing fields
- `tests/unit/test_layers.py` — add test cases D1-D3

---

## Phase E: Voice Exemplar Restoration (ELEVATED)

**Priority:** High. Depends on Phase I (Authority Split Resolution) having resolved Option 1 (backend-authoritative voice).
**Vision authority:** §9 Success Criteria (response quality, agent sovereignty)
**v1.0 mapping:** Recommendation 5

### Prerequisite

Phase I must be resolved as **Option 1 (backend-authoritative voice)** before Phase E begins. If Phase I resolves differently, Phase E must be redesigned to match.

### Work items

1. **Add voice mode tags to Voice.md files.** Each example in `Characters/{Name}/{Name}_Voice.md` gets a frontmatter-style mode tag:

   ```markdown
   ## Example 4: Asks For Whyze's Brain

   <!-- mode: domestic, intimate -->

   **What it teaches the model:** [existing teaching prose]

   **User:** [existing user message]

   **Assistant:** [existing assistant response]
   ```

   Valid modes (closed enum, expanded by REINA + ALICIA audit integration):
   - `domestic` — ordinary household scenes, no special pressure
   - `conflict` — disagreement, friction, veto, pushback
   - `intimate` — romantic, sensual, physical closeness between adults only
   - `children_gate` — scenes with Isla, Daphne, Gavin, or other minors present
   - `public` — work, colleagues, outside-household witnesses
   - `group` — multi-woman scenes
   - `repair` — post-conflict reconciliation
   - `silent` — responses where the character chooses silence or minimal verbal output
   - `solo_pair` — one-on-one with Whyze, no children, no colleagues
   - `escalation` — deliberate, staged intimacy escalation **(REINA audit addition; canonical for Reina's trailhead-with-Whyze and staged-mezzanine-arrival exemplars)**
   - `warm_refusal` — declining without coldness, holding a professional or personal boundary while preserving the relationship **(ALICIA audit addition; canonical for Alicia's operational security gate and her "I will not turn human suffering into bedroom narrative" exemplars)**
   - `group_temperature` — functioning as the temperature change in a group scene rather than as the conversational hub **(ALICIA audit addition; canonical for Alicia's group function as somatic regulator-from-the-edge rather than active participant)**

   Each example can have multiple modes (comma-separated). A single example carries its modes forward into the mode-selection logic.

2. **Create a voice mode extractor.** `kernel_loader.py` gets a new function `extract_voice_examples_with_modes(voice_md: str) -> list[VoiceExample]` that parses the mode tags alongside the existing teaching prose and example blocks.

3. **Replace the file-order selection with mode-aware selection.** Given a scene's active mode list, the voice example selector:
   - Filters examples to those tagged with at least one of the scene's active modes
   - Prioritizes examples tagged with multiple matching modes over single-mode matches
   - Selects 1-2 examples per active mode, up to the Layer 5 voice exemplar budget
   - Falls back to default mode ordering when no modes match (e.g., an uncategorized scene)

4. **Abbreviate exemplars to 2-3 sentences.** For each selected example, the compiler includes:
   - The example title (e.g., `Example 4: Asks For Whyze's Brain`)
   - A 2-3 sentence abbreviation of the `**Assistant:**` response text, chosen to preserve rhythm rather than content
   - Omit the `**User:**` block entirely — the model doesn't need the setup to learn the rhythm

   Abbreviation is hand-authored in the Voice.md file by adding a `**Abbreviated:**` marker:

   ```markdown
   ## Example 4: Asks For Whyze's Brain

   <!-- mode: domestic, intimate -->

   **What it teaches the model:** [existing teaching prose]

   **User:** [existing user message]

   **Assistant:** [existing full assistant response]

   **Abbreviated:** [2-3 sentence version the backend uses as the rhythm exemplar]
   ```

   The abbreviated version is what the backend ships to the model. Msty persona studio (if configured) can carry the full version. This is consistent with Phase I Option 1 (backend-authoritative with canonically compiled derivatives).

5. **Per-character voice mode coverage requirements.** The `BINA_CONVERSION_AUDIT.md` Finding 3 shows Bina's current Layer 5 keeps only the first two examples by file order, dropping tenderness and culture. The elevated plan requires per-character coverage guarantees:

   | Character | Required mode coverage |
   |---|---|
   | Adelia | solo_pair, conflict, intimate, group, domestic, silent (6 modes minimum — audit-driven addition; the near-silent seismograph response is canonical and currently dropped at runtime) |
   | Bina | domestic, conflict, intimate, repair, silent, children_gate (6 modes minimum — covers tenderness, culture, veto) |
   | Reina | solo_pair, conflict, group, repair, intimate, **domestic**, **escalation** (7 modes minimum — audit-driven addition; the suit-to-hoodie courthouse-shedding exemplar and the trailhead-escalation exemplar are canonical and currently dropped at runtime per REINA audit Finding 2) |
   | Alicia | solo_pair, silent, intimate, repair, **warm_refusal**, **group_temperature** (6 modes minimum — audit-driven addition; the operational-security-gate refusal exemplar and the group-temperature-change exemplar are canonical per ALICIA audit Finding 3, plus Alicia's communication_mode-tagged exemplars from Phase A'' should also satisfy this coverage when authored) |

   If a character's Voice.md does not contain examples covering the required modes, the elevated plan adds an authoring item: write new examples to fill the gaps. This is human authoring work, not Claude Code work.

### Test cases

- **Test E1:** Bina's Voice.md parses successfully with mode tags and produces at least one example tagged with each of the 6 required modes
- **Test E2:** Bina's Layer 5 for a domestic scene includes the covered-plate example (or equivalent tenderness-through-competence exemplar)
- **Test E3:** Mode-aware selection differs from file-order selection when the active scene mode is not the first mode in the file
- **Test E4:** Layer 5 abbreviated exemplar content is 2-3 sentences per example, not full response text

### Files touched

- `Characters/{Name}/{Name}_Voice.md` for all four characters — add mode tags and abbreviated versions (human authoring work)
- `src/starry_lyfe/context/kernel_loader.py` — update voice parser to extract modes
- `src/starry_lyfe/context/layers.py` — replace file-order selection with mode-aware selection
- `src/starry_lyfe/context/types.py` — add `VoiceMode` enum and `VoiceExample` dataclass with mode fields
- `tests/unit/test_layers.py` — add test cases E1-E4

---

## Phase F: Scene-Aware Section Retrieval + Cross-Cutting Modifiers (ELEVATED)

**Priority:** Medium-High.
**Vision authority:** §6 Relationship Architecture, §7 Behavioral Thesis (cognitive hand-off contract)
**Persona Tier Framework authority:** §2.1 children gate (Tier 1 axiom, cross-cutting)
**v1.0 mapping:** Recommendation 6

### Correction from v1.0

Plan v1.0 treats `children_gated` as a scene type alongside `domestic`, `intimate`, `conflict`, etc. This is incorrect. The children gate is **not a scene type** — it is a **Tier 1 axiom from PTF §2.1** that applies *on top of* whatever scene type is active. A domestic-intimate scene can have children present; a conflict scene can have children present; a public scene can have children present. The children gate is a cross-cutting modifier.

The elevated plan separates scene classification from cross-cutting modifiers.

### Work items

1. **Define scene types as a closed enum.** Scene types are mutually exclusive — a scene is one type at a time:

   ```python
   class SceneType(StrEnum):
       DOMESTIC = "domestic"          # ordinary household
       INTIMATE = "intimate"          # romantic or sensual, adults only
       CONFLICT = "conflict"          # friction, disagreement, veto
       REPAIR = "repair"              # post-conflict reconciliation
       PUBLIC = "public"              # work, colleagues, outside witnesses
       GROUP = "group"                # multi-woman scene
       SOLO_PAIR = "solo_pair"        # one woman + Whyze, no others
       TRANSITION = "transition"      # between states, no specific type
   ```

2. **Define cross-cutting modifiers as a flag set.** Modifiers stack — multiple can be true at once:

   ```python
   class SceneModifiers(BaseModel):
       children_present: bool = False          # PTF §2.1 gate active
       work_colleagues_present: bool = False   # affects public-scene semantics
       post_intensity_crash_active: bool = False  # somatic state modifier
       pair_escalation_active: bool = False    # intimate pair in flight
       explicitly_invoked_absent_dyad: set[str] = Field(default_factory=set)
   ```

   `explicitly_invoked_absent_dyad` is the same field as the Phase A' `recalled_dyads` — it lets a scene explicitly reference an absent dyad member without violating the Phase A' offstage-leakage filter.

3. **Map scene types to kernel section promotions.** Section promotion moves specified kernel sections from fill tier to primary tier for the current scene:

   | Scene type | Sections promoted |
   |---|---|
   | DOMESTIC | §7 Frameworks (protocol surface), §9 Family Dynamics |
   | INTIMATE | §8 Intimacy Architecture, §3 Pair |
   | CONFLICT | §5 Behavioral Tier (anti-therapy, friction-is-intimacy), §7 Frameworks |
   | REPAIR | §8 Intimacy Architecture, §9 Family Dynamics |
   | PUBLIC | §10 What This Is Not, §5 Behavioral Tier |
   | GROUP | §6 Voice Architecture, §9 Family Dynamics |
   | SOLO_PAIR | §3 Pair, §8 Intimacy Architecture |
   | TRANSITION | (no promotion; default sections only) |

4. **Map cross-cutting modifiers to constraint modifications.** Modifiers do NOT promote kernel sections — they modify Layer 7 constraint rendering:

   | Modifier | Layer 7 effect |
   |---|---|
   | `children_present: true` | PTF §2.1 gate block rendered at top of Layer 7 in bold; erotic/explicit content constraints elevated to MUST |
   | `work_colleagues_present: true` | Public-scene OpSec constraints rendered (Alicia's operational security gate applies) |
   | `post_intensity_crash_active: true` | Character-specific crash protocols rendered (Flat State for Bina, Post-Race Crash for Reina, etc.) |
   | `pair_escalation_active: true` | Admissibility Protocol rendered (Reina's intimacy-requires-earned-context rule) |

5. **Wire scene type and modifiers through `assembler.py`.** `SceneState` gains `scene_type: SceneType` and `modifiers: SceneModifiers` fields. `format_kernel()` takes a `promote_sections: list[str]` parameter derived from scene type. `format_constraints()` takes a `modifiers: SceneModifiers` parameter.

### Test cases

- **Test F1:** An INTIMATE scene with Bina as focal character produces a kernel that includes §8 Intimacy Architecture in the primary tier
- **Test F2:** A DOMESTIC scene with `children_present=true` produces a Layer 7 constraint block where the PTF §2.1 children gate is the first constraint rendered
- **Test F3:** A CONFLICT scene for Adelia includes §5 Behavioral Tier (anti-therapy, friction-is-intimacy) in the primary kernel tier
- **Test F4:** A scene with `explicitly_invoked_absent_dyad={"bina-reina"}` renders the bina-reina dyad block even when Reina is not in `present_characters`
- **Test F5:** A TRANSITION scene type produces no section promotions (baseline kernel only)

### Files touched

- `src/starry_lyfe/context/types.py` — add `SceneType` enum, `SceneModifiers` model, update `SceneState`
- `src/starry_lyfe/context/kernel_loader.py` — add `promote_sections` parameter to `compile_kernel()`
- `src/starry_lyfe/context/layers.py` — update `format_constraints()` to handle modifiers, integrate scene type into kernel formatting
- `src/starry_lyfe/context/assembler.py` — wire scene state through to layer formatters
- `tests/unit/test_assembler.py` — add test cases F1-F5

---

## Phase G: Dramaturgical Prose Rendering With Per-Character Templates (ELEVATED)

**Priority:** Medium-High. Model absorption quality improvement.
**Vision authority:** §9 Success Criteria (life authenticity, agent sovereignty)
**v1.0 mapping:** Recommendation 7

### Correction from v1.0

Plan v1.0 proposes a single generic `render_dyad_prose(dyad, character_id)` function that produces one prose template for all characters. This is wrong because the same dyad state reads differently across characters — Bina's "deep trust" is diagnostic-observation-confirmed, Reina's "deep trust" is body-read-earned-through-context, Alicia's "deep trust" is somatic-permission-to-close-distance, Adelia's "deep trust" is shared-language-for-hard-things. The elevated plan commits to **per-character prose renderers**.

Additionally, the elevated plan keeps the raw numeric values accessible alongside the prose rendering. The model benefits from prose; debugging and introspection benefit from numbers. Both are rendered.

### Work items

1. **Create `src/starry_lyfe/context/prose.py`** with per-character prose renderers:

   ```python
   def render_dyad_prose(character_id: str, dyad_state: DyadState) -> str:
       """Character-specific dyad prose rendering."""
       renderer = CHARACTER_DYAD_RENDERERS[character_id]
       return renderer(dyad_state)

   def render_adelia_dyad_prose(dyad_state): ...
   def render_bina_dyad_prose(dyad_state): ...
   def render_reina_dyad_prose(dyad_state): ...
   def render_alicia_dyad_prose(dyad_state): ...
   ```

2. **Specify per-character thresholds and language.** Example for the `trust` dimension:

   | Character | trust > 0.8 | trust 0.5-0.8 | trust 0.3-0.5 | trust < 0.3 |
   |---|---|---|---|---|
   | Adelia | "load-tested and reliable" | "earned, still calibrating" | "conditional, watching" | "something to rebuild" |
   | Bina | "confirmed by repeated observation" | "provisional, recorded" | "unproven, watching closely" | "broken, under repair" |
   | Reina | "admissible without caveat" | "admissible with context" | "inadmissible without new evidence" | "actively disputed" |
   | Alicia | "body accepts without flinch" | "body accepts with a beat" | "body tenses briefly" | "body will not settle" |

   The same applies to other dyad dimensions (intimacy, conflict, unresolved_tension, repair_history).

3. **Render prose AND numbers in Layer 6 (Scene Context).** The final format includes both for each dyad:

   ```
   [Her relationship with Whyze is confirmed by repeated observation.
    The intimacy is settled and mutual, without the need to prove it again.
    No active conflict. Low unresolved tension. One outstanding repair: the
    August silence, two weeks in, not yet named aloud.]

   (trust=0.82 intimacy=0.78 conflict=0.05 unresolved=0.15 repair_pending=1)
   ```

   The prose block is primary; the parenthesized numeric block is secondary and brief. Both help the model, but the prose is what carries the character voice.

4. **Apply the same pattern to Layer 4 (Sensory Grounding / Somatic State).** Per-character somatic prose:

   | Character | fatigue > 0.7 | fatigue 0.4-0.7 | fatigue < 0.4 |
   |---|---|---|---|
   | Adelia | "the chemistry is running on backup, the sentences are getting louder" | "she is paying for this morning's sparks, visibly" | "the engine is hot and well-fed" |
   | Bina | "the grid has given everything it had, the hall light will still go on" | "she has been moving more than the ledger allowed" | "the systems are green" |
   | Reina | "the body has been spent and the admissibility gate is closing" | "she is still sharp but beginning to feel the afternoon" | "the body is ready, leaning forward" |
   | Alicia | "the Ni-grip is close, the words have stopped working" | "her presence has gone slightly inward" | "the body is settled and attending" |

5. **Per-character protocol rendering.** When a named protocol is active in Tier 7 (Transient Somatic State), render it in character voice:
   - Bina in Flat State: "She is in Flat State. Syllables cost more than they earn. Touch is safer than talk."
   - Reina in Post-Race Crash: "The adrenaline has left the building. She will need thirty minutes and an electrolyte drink before she can be reached for anything not urgent."
   - Alicia in Four-Phase Return: "She is returning from an operation. Current phase: [phase]. Language is thin; weight and silence are the currency."

6. **Canon facts narrative rendering in Layer 2.** Currently canon facts render as flattened JSON blobs (per BINA_CONVERSION_AUDIT.md Finding 10). Elevated rendering produces a compact narrative paragraph per character:

   ```
   [Bina Malek, 34, Canadian-born Assyrian, Red Seal mechanic, builder of
    Loth Wolf Hypersport. Born in Urmia, brought to Canada by her parents
    Farhad and Shirin in 1991. Mother to Gavin (7). Married to Reina.
    Survivor of an eight-year coercive control relationship. First language
    Assyrian Neo-Aramaic (Suret), fluent in Farsi and English.]
   ```

### Test cases

- **Test G1:** The same canonical dyad state (trust=0.82) renders as four distinct prose strings across the four characters
- **Test G2:** Bina's somatic prose for `fatigue=0.8` contains the phrase "grid has given everything it had" or equivalent Si-dominant mechanical metaphor
- **Test G3:** Layer 6 rendered output contains both the prose block and the parenthesized numeric block
- **Test G4:** Canon facts Layer 2 rendered output reads as a narrative paragraph, not a JSON blob

### Files touched

- `src/starry_lyfe/context/prose.py` — new file with per-character renderers
- `src/starry_lyfe/context/layers.py` — update `format_scene_blocks()`, `format_sensory_grounding()`, `format_canon_facts()` to use prose renderers
- `tests/unit/test_prose.py` — new test file with G1-G4

---

## Phase J: Per-Character Remediation Passes (NEW)

**Priority:** High. The Plan is character-agnostic but the work is character-specific. Each character has her own runtime deficit that requires targeted fixes against her own canon.
**Vision authority:** §5 Chosen Family (non-redundancy guarantee)
**Source:** `BINA_CONVERSION_AUDIT.md` (existing) + future per-character audits

### Why this phase exists

Plan v1.0's phases A through H apply equally to all four characters. But the BINA audit shows that each character has specific runtime drift that abstract phases do not directly address. Bina drops tenderness-through-competence; Adelia may drop cognitive handoff specifics; Reina may drop body-reader precision beyond generic assertiveness; Alicia may drop body-first somatic anchor architecture. These are character-specific repairs that need character-specific work.

Phase J provides the structure for that work: a per-character remediation cycle that runs after the abstract phases (A through G) have built the substrate.

### Sub-phases

#### J.1: Bina Remediation (FIRST — audit already exists)

**Source audit:** `BINA_CONVERSION_AUDIT.md`

**Audit findings already addressed by other phases:**

| Audit finding | Addressed by | Status |
|---|---|---|
| Finding 1: Bahadori vs Malek runtime contradiction | Earlier cleanup (Bina kernel parents = Malek as of 2026-04-09) | RESOLVED — audit is stale on this specific finding |
| Finding 2: Layer 1 truncation removes pair mechanics | Phase A (structure-preserving trim) + Phase B (budget elevation) | Addressed |
| Finding 3: Layer 5 skews toward cold compression | Phase E (mode-aware exemplar selection with required mode coverage) | Addressed |
| Finding 4: Talk-to-Each-Other mandate misfires for 2-person scenes | Phase A' (constraints.py fix) | Addressed |
| Finding 5: Offstage Reina leaks into Bina-Whyze prompts | Phase A' (layers.py + types.py fix) | Addressed |
| Finding 6: pair_mechanism stored but not surfaced | Phase D (live pair data) | Addressed |
| Finding 7: Vision says Canadian-born, kernel says Urmia-born | Phase A' (Vision §5 line edit) | Addressed |
| Finding 8: kernel §3 heading still says "Citadel Pair" | Earlier cleanup (heading corrected to "Circuit Pair" as of 2026-04-09) | RESOLVED |
| Finding 9: tests don't guard Bina's soul | Phase H (soul regression tests, with Bina-specific cases) | Addressed |
| Finding 10: family/culture render as raw JSON blobs | Phase G (canon facts narrative rendering) | Addressed |

**Bina-specific remediation work items beyond the abstract phases:**

1. **Author Bina's soul cards from Phase C.** Specifically:
   - `soul_cards/pair/bina_circuit.md` — distill the Circuit Pair architecture (Orthogonal Opposition, total division of operational domains, translation-not-mirroring, the Architect and the Sentinel)
   - `soul_cards/knowledge/bina_ritual.md` — distill the samovar ritual, covered-plate register, hall-light architecture, Gilgamesh drawer, Uruk interior worldview
   - `soul_cards/knowledge/bina_grief.md` — distill the eight-year coercive control survival, Arash's tags, the specific texture of Assyrian-Iranian grief that lives under the competence

2. **Author Bina's mode-tagged voice exemplars from Phase E.** Bina's Voice.md must contain examples covering all 6 required modes (domestic, conflict, intimate, repair, silent, children_gate). Audit her current Voice.md against this list and write new examples for any uncovered modes.

3. **Add Bina-specific Phase G prose renderers.** Implement `render_bina_dyad_prose()`, `render_bina_somatic_prose()`, `render_bina_canon_prose()` matching the threshold tables in Phase G.

4. **Bina-specific regression tests in Phase H** (see Phase H section below).

**Exit criteria for J.1:**
- All BINA_CONVERSION_AUDIT findings either resolved or explicitly closed as stale
- Bina's pair soul card exists and passes Phase C validation (required concepts present, within budget)
- Bina's voice mode coverage hits all 6 required modes
- Bina-specific Phase H tests pass
- Re-running the BINA audit produces zero new high/critical findings

### Audit Convergence Observation (UPDATED — all four character audits now integrated)

**Update history:**
- Initial section added 2026-04-10 during ADELIA audit integration (BINA + ADELIA only)
- This section updated 2026-04-10 during REINA + ALICIA audit integration with validation data and a refined prediction model

After all four character audits (`BINA_CONVERSION_AUDIT.md`, `ADELIA_CONVERSION_AUDIT.md`, `REINA_CONVERSION_AUDIT.md`, `ALICIA_CONVERSION_AUDIT.md`) were written and analyzed against the elevated plan, the convergence pattern is now confirmed across the full character set: **the majority of findings in every audit are direct mirrors of pipeline-level issues already addressed by Phase A, A', B, D, and E.**

**Cross-character convergence matrix (all four audits):**

| Pipeline-level root cause | BINA | ADELIA | REINA | ALICIA | Status |
|---|:---:|:---:|:---:|:---:|---|
| Layer 1 flat-budget truncation removes pair section + behavioral tier | F2 | F1 | F1 | F2 | Phase A + B |
| Layer 5 file-order voice exemplar selection drops mode-specific examples | F3 | F2 | F2 | F3 | Phase E |
| Talk-to-Each-Other mandate misfires for 2-person scenes | F4 | F3 | — | — | **VERIFIED RESOLVED in code** |
| Offstage dyads leak into focal-character prompts | F5 | F4 | — | — | **VERIFIED RESOLVED in code** |
| pair_mechanism / pair_core_metaphor stored but not surfaced in Layer 5 | F6 | F5 | F3 | F5 | Phase D |
| `budgets.py` whitespace trim destroys document structure | F2 (subset) | F7 | (subsumed in F1) | (subsumed in F2) | Phase A |
| Tests don't guard character-specific failure path | F9 | F8 | F4 | F6 | Phase H + Phase A' work item 5 |
| Family/culture rendered as raw JSON blobs (Layer 2 prose weakness) | F10 | F6 (variant) | — | F4 (variant) | Phase G |

**Character-specific findings (one or two per character that do not mirror pipeline issues):**

| Character | Finding | Type | Resolution |
|---|---|---|---|
| BINA | F1: Bahadori vs Malek runtime contradiction (now stale) | v7.0 residue | RESOLVED 2026-04-09 (earlier cleanup) |
| BINA | F7: Vision-vs-kernel Bina origin drift | Source-of-truth conflict | Phase A' work item 3 |
| BINA | F8: kernel §3 heading still says "Citadel Pair" (now stale) | v7.0 residue | RESOLVED 2026-04-09 |
| ADELIA | F6: Valencian-Australian Spanish register runtime-weak | Cultural surface specificity | Phase C `adelia_cultural.md` + Phase E `cultural` mode coverage |
| REINA | F5: `Reina_Torres_Kinetic_Pair.md` carries `_v7.0.md` cross-reference and stale Alicia framing | v7.0 residue | **RESOLVED 2026-04-10** during this integration pass |
| ALICIA | F1: Away-state phone/letter prompts carry in-person-only somatic instructions | **NEW PIPELINE CONCEPT** | **Phase A'' (NEW — Communication-Mode-Aware Pruning)** |

**Prediction validation (for the prediction model that was published with this section before REINA + ALICIA audits existed):**

| Prediction (made 2026-04-10 after ADELIA integration) | Actual (REINA) | Actual (ALICIA) | Verdict |
|---|---|---|---|
| 5-7 findings mirroring BINA/ADELIA pipeline issues | 4 of 5 mirror | 4 of 6 mirror | **Within expected range** (slightly low for both because the trim+selection root causes had already been collapsed into single audit findings rather than enumerated separately) |
| 1-3 character-specific findings | 1 (v7.0 residue) | 2 (refusal architecture + Section 8 culture) | **Within expected range** |
| 0-1 findings surfacing a new pipeline concept | 0 | **1 (communication-mode pruning)** | **Upper bound hit by ALICIA** |

**The prediction held but slightly underestimated ALICIA.** Specifically, the prediction did not anticipate that one character would surface a brand-new architectural mechanism (communication-mode-aware pruning) requiring its own sub-phase. The lesson for any future character whose canon includes a mode-conditional architecture: the prediction model should allow for one new pipeline phase per character with mode-conditional canon, not zero.

**What this means for Phase J execution (refined with all four audits in hand):**

1. **Phase J is much smaller than the v1.0 plan implied.** The pipeline-level fixes in Phase A, A', B, D, E now resolve the **majority** of every character's runtime deficit in one pass. Phase J is four parallel passes of authoring soul cards, asserting voice mode coverage, and writing test bundles, on top of the same pipeline fixes. Phase A'' adds Alicia-specific work but does not change the structure.

2. **Two pipeline-level fixes have already landed in code between audits.** The REINA audit (2026-04-10) explicitly verified that the Talk-to-Each-Other mandate trigger and offstage dyad leakage are both fixed. The ALICIA audit (also 2026-04-10) independently verified the offstage dyad fix. This means Phase A' work items 1 and 2 are now historical record, not pending work — someone fixed them in `constraints.py:104` and `layers.py:232-240` between when the BINA/ADELIA audits were written and when the REINA/ALICIA audits were written.

3. **The single highest-risk character-specific finding remains the Reina+Alicia non-redundancy** — the two Se-dominants whose canonical mechanisms are the closest (both body readers, both physical-first) and whose collapse would be the hardest agent sovereignty failure to detect by any test that does not explicitly compare them. Phase H's `test_reina_and_alicia_remain_distinguishable` is the only test in the entire suite specifically designed to catch this. It is more important than any presence test in either character's individual bundle. Both audits independently confirm the risk: the REINA audit notes Reina is "tactical, body-reading, flirt-capable, fast-moving" but underrenders her court/stable specificity, while the ALICIA audit notes Alicia is "body-first, Argentine, operational, warm" but underrenders her professional restraint. The risk of the two collapsing toward "two warm body-readers" is real.

4. **All four audits have retroactively upgraded the elevated plan.** Net additions across the four integrations:
   - **Phase A''** (NEW sub-phase) — Communication-Mode-Aware Pruning, from ALICIA Finding 1
   - **Phase E mode enum extensions** — `silent` (Adelia), `escalation` (Reina), `warm_refusal` (Alicia), `group_temperature` (Alicia)
   - **Phase E mode coverage requirements** — Adelia 5→6, Reina 5→7, Alicia 4→6
   - **Phase C soul card additions** — `adelia_cultural.md`, `alicia_remote.md` (the latter for Phase A''-conditional content)
   - **Phase 0 drift grep extensions** — stale Alicia framing terms ("non-resident", "twice yearly between operations", "Spanish consular officer", "based in Madrid", "Alicia Marín" with diacritic)
   - **Phase J.3 Finding 5 resolution** — Reina pair file v7.0 residue fixed during this integration pass
   - **Phase A' work items 1 + 2 status** — marked VERIFIED RESOLVED with historical record preserved
   
   This is the elevated plan responding to its own ground truth as audits land. The pattern will likely repeat any time future canon work surfaces new architectural concepts.

**Implementation efficiency claim (refined):** With all four audits integrated, the total effort for Phase A through Phase J.4 is approximately:

- Phase A through Phase G plus Phase A'': roughly 70 percent of the work, applied once across all characters (Phase A'' is Alicia-specific but reuses the same infrastructure as the other phases)
- Phase J.1 (Bina) through J.4 (Alicia): roughly 25 percent of the work, roughly 6 percent per character (most of the per-character work is now soul card authoring and voice mode tagging, both of which are bounded human authoring tasks)
- Phase H: roughly 5 percent additional for the test bundles and the non-redundancy test

This is significantly less than the v1.0 plan's implicit assumption that each character would need roughly 25 percent of the total work. The convergence is the source of the efficiency, and the convergence is now confirmed by all four audits.

---

#### J.2: Adelia Remediation (SECOND — audit exists, integrated 2026-04-10)

**Source audit:** `Docs/ADELIA_CONVERSION_AUDIT.md` — **EXISTS as of 2026-04-10** (8 findings, same template as BINA audit)

**Audit findings already addressed by other phases:**

| Audit finding | Addressed by | Status |
|---|---|---|
| Finding 1: Layer 1 truncation removes Entangled Pair (§3) and Behavioral Tier Framework (§5) | Phase A (structure-preserving trim) + Phase B (kernel budget 2000→6000 with §3 prioritized) | Addressed |
| Finding 2: Layer 5 keeps only first two examples (drops near-silent, domestic, erotic, cultural exemplars) | Phase E (mode-tagged exemplar selection; Adelia requires 6 modes including the audit-added `silent` mode) | Addressed |
| Finding 3: Talk-to-Each-Other mandate misfires for Adelia-Whyze 2-person scenes | Phase A' work item 1 (constraints.py fix — same fix as BINA Finding 4) | Addressed |
| Finding 4: Offstage Bina/Reina dyads leak into Adelia-only prompts | Phase A' work item 2 (layers.py + types.py recalled_dyads filter — same fix as BINA Finding 5) | Addressed |
| Finding 5: pair_mechanism / pair_core_metaphor stored in CharacterBaseline but not surfaced in Layer 5 | Phase D (six-field pair metadata block in Layer 5) | Addressed |
| Finding 6: Valencian-Australian Spanish register canonically preserved but runtime-weak | Phase E (cultural mode coverage) + new `adelia_cultural.md` knowledge soul card from Phase C | Addressed |
| Finding 7: Flat trim destroys structured document hierarchy | Phase A (structure-preserving compilation — same fix as BINA Finding 2) | Addressed |
| Finding 8: Tests don't guard Adelia-specific failure path; live test coverage targets Bina+Alicia only | Phase A' work item 5 (add Adelia + Reina live `assemble_context()` smoke tests) + Phase H (full Adelia regression bundle) | Addressed |

**Audit convergence observation:** 7 of the 8 ADELIA findings are direct mirrors of BINA findings against the same code paths. This is strong evidence that the pipeline-level fixes in Phase A, A', B, D, and E will resolve the bulk of both characters' deficits in one pass. Phase J.2 (Adelia) is therefore largely about authoring the per-character soul cards and per-character voice mode coverage, plus the Adelia-specific test bundle, NOT a separate independent investigation. See the new "Audit Convergence Observation" section above for the full meta-analysis.

**Specific risks the Adelia audit explicitly probes for** (now confirmed by `ADELIA_CONVERSION_AUDIT.md`):

- The **gravitational center** architecture. The Vision says the Entangled Pair is *"the reason the system exists."* The audit Drift section confirms this is currently the largest single drift: the runtime preserves Adelia's biography more reliably than Adelia's purpose.
- The **cognitive handoff contract**, framed as *dependence* not just behavior. The audit specifically calls out *"hand-off dependence on Whyze's sequencing mind"* — the model needs to feel that Adelia *needs* Whyze to sequence her plans, not just that she should hand them off as a stylistic rule.
- **Structural safety** language rather than emotional reassurance language. Vision §4: *"Adelia does not feel loved because she is praised; she feels loved because the architecture of the relationship is impenetrable."* This concept must survive into runtime as language the model can absorb.
- **Load-bearing quietness.** The audit explicitly names the dropped *"near-silent seismograph response"* exemplar as a high-impact loss. Adelia's silence is not absence — it is its own voice mode. This is why the elevated plan now requires `silent` as Adelia's 6th voice mode (audit-driven addition to Phase E).
- The **Whiteboard Mode** and **Bunker Mode** protocol structure for Adelia specifically.
- The **Valencian-Australian** cultural surface as a distinct register, not generic Australian-immigrant warmth. The audit Finding 6 confirms this is runtime-weak and needs the new `adelia_cultural.md` knowledge soul card (audit-driven addition to Phase C).

**Adelia-specific remediation work items (anticipated):**

1. **Author Adelia's soul cards from Phase C:**
   - `soul_cards/pair/adelia_entangled.md` — distill the Entangled Pair architecture (1+1=11, complementary cognitive interlock, Compass and Gravity, the structural-safety-not-emotional-reassurance principle)
   - `soul_cards/knowledge/adelia_workshop.md` — distill the Marrickville workshop, Joaquín and Inés, Ozone & Ember workspace and ethos, the permit struggle, pyrotechnician-engineer texture
   - `soul_cards/knowledge/adelia_pyrotechnics.md` — distill the technical practice of pyrotechnics (chemistry, sequencing, safety architecture, the relationship between fire and discipline)
   - `soul_cards/knowledge/adelia_cultural.md` — **(audit-driven addition)** distill the Valencian-inflected Castilian via Sydney diaspora register specifically: _otra vez_, café solo, Paella Valenciana, Las Fallas inheritance, Valencia CF, the canonical domains where her Spanish surfaces under pressure or in private. This is separate from `adelia_workshop.md` because the ADELIA audit Finding 6 explicitly flags her cultural register as runtime-weak even when workshop content survives.

2. **Author Adelia's mode-tagged voice exemplars from Phase E.** Adelia's Voice.md must cover at least 5 modes (solo_pair, conflict, intimate, group, domestic).

3. **Add Adelia-specific Phase G prose renderers.**

4. **Adelia-specific regression tests in Phase H.**

**Exit criteria for J.2:** Same structure as J.1, against the Adelia audit.

#### J.3: Reina Remediation (THIRD — audit exists, integrated 2026-04-10)

**Source audit:** `Docs/REINA_CONVERSION_AUDIT.md` — **EXISTS as of 2026-04-10** (5 findings, all Medium or Low severity)

**Audit findings already addressed by other phases:**

| Audit finding | Addressed by | Status |
|---|---|---|
| Finding 1: Default kernel still drops Cuatrecasas, Bishop/Vex, courtroom voice, Mediterranean reset | Phase A (structure-preserving trim) + Phase B (kernel budget 2000→6000) | Addressed |
| Finding 2: Layer 5 still drops Examples 6 (suit-to-hoodie), 8 (staged mezzanine arrival), 10 (trailhead escalation) | Phase E (mode-tagged selection; Reina now requires `domestic` and `escalation` modes per audit-driven addition above) | Addressed |
| Finding 3: Kinetic Pair mechanism + core metaphor weakly surfaced; Layer 5 emits only `Pair: {pair_name}` | Phase D (six-field pair metadata block in Layer 5) | Addressed |
| Finding 4: Reina-specific regression coverage too weak (only asserts on Admissibility) | Phase A' work item 5 (live `assemble_context()` smoke test) + Phase H (full Reina regression bundle) | Addressed |
| Finding 5: `Reina_Torres_Kinetic_Pair.md` carries stale `_v7.0.md` cross-reference and stale Alicia framing ("non-resident, based in Madrid", "twice yearly between operations") | **RESOLVED 2026-04-10** — Reina pair file updated; L6 cross-reference now `Reina_Torres_v7.1.md`, L256 Alicia framing rewritten to current canon (resident at the property, frequently away on consular operations as an Argentine Cancilleía officer) | RESOLVED |

**Reina convergence: 4 of 5 findings mirror existing BINA/ADELIA pipeline-level issues. Only Finding 5 is character-specific, and it has been resolved as a standalone v7.0 cleanup item before the rest of Phase J.3 begins.**

**Reina-specific remediation work items:**

1. **Author Reina's soul cards from Phase C:**
   - `soul_cards/pair/reina_kinetic.md` — distill the Kinetic Pair architecture (Asymmetrical Leverage, Se+Ni compensatory, **the Mastermind and the Operator**, **temporal collision converted to engine heat**, **the right moment is now**, the Mediterranean reset as dyadic geography). The audit explicitly names "The Mastermind and the Operator" as something the live prompt did NOT carry; this is a required-concept for the soul card validation test.
   - `soul_cards/knowledge/reina_stable.md` — distill Bishop and Vex, the Mediterranean reset as canonical home-return rhythm, the property stables, riding as identity rather than scene props
   - `soul_cards/knowledge/reina_court.md` — distill her criminal defense practice in Okotoks, the **Cuatrecasas-to-defence-law pivot** (the deliberate break from corporate prestige), the courtroom register applied outside court, the court residue

2. **Author Reina's mode-tagged voice exemplars** covering all 7 required modes (`solo_pair`, `conflict`, `group`, `repair`, `intimate`, **`domestic`**, **`escalation`**). The audit explicitly names dropped Examples 6, 8, and 10 as carrying her deepest domestic and escalation registers. These three examples must be tagged appropriately so Phase E's mode-aware selector retains them.

3. **Add Reina-specific Phase G prose renderers** with attention to her court-residue somatic state, her Mediterranean reset domestic prose, and her body-reader precision rendering (distinct from generic assertiveness).

4. **Reina-specific regression tests in Phase H** including the dedicated `test_reina_and_alicia_remain_distinguishable` test (the highest-stakes non-redundancy test in the entire suite).

**Specific risks confirmed by the audit:**

- The runtime renders Reina as fast, precise, and physical — but underrepresents her as **a lawyer who chose against prestige**, a horse-and-stable woman with real domain ownership, and a woman with a canonical home-return rhythm.
- The risk is not collapse into nonsense; the risk is narrowed Reina: incisive, kinetic, and flirt-capable, without enough of the deeper geography, discipline, and domestic choreography that the Vision treats as load-bearing.
- The Mediterranean reset is a **dyadic geography** with Whyze, not a personal habit. Without it, the Kinetic Pair loses its canonical decompression rhythm.

**Exit criteria for J.3:** Same structure as J.1, against the REINA audit. Plus the specific assertion that the assembled Reina prompt carries `The Mastermind and the Operator` as a phrase (currently absent per audit live probing).

#### J.4: Alicia Remediation (FOURTH — audit exists, integrated 2026-04-10, highest architectural impact)

**Source audit:** `Docs/ALICIA_CONVERSION_AUDIT.md` — **EXISTS as of 2026-04-10** (6 findings: 3 High + 3 Medium)

The Soul Preservation diagnostic flagged Alicia as *"probably the most underfed by the current backend path."* The audit confirms this and adds a finding that none of the other audits caught: **communication-mode-aware pruning** (a brand-new architectural mechanism, now Phase A'').

**Audit findings already addressed by other phases:**

| Audit finding | Severity | Addressed by | Status |
|---|---|---|---|
| Finding 1: Away-state phone/letter prompts carry in-person-only somatic instructions | **High** | **Phase A'' (NEW — Communication-Mode-Aware Pruning)** | Addressed via new phase |
| Finding 2: Default kernel drops refusal architecture (no costume Argentineness, no action-hero collapse, no trauma performance, "I am professional about my profession") | **High** | Phase A (structure-preserving trim) + Phase B (kernel budget 2000→6000 with §5 Behavioral Tier prioritized) | Addressed |
| Finding 3: Layer 5 omits Examples 4 (warm refusal), 6 (group temperature change), 8 (Reina reading-room), 10 (no trauma performance) | **High** | Phase E (mode-tagged selection; Alicia now requires `warm_refusal` and `group_temperature` modes per audit-driven enum extension above) | Addressed |
| Finding 4: Section 8 (Mercedes Sosa, baths, *Tía Apo*, *When I Am Away*) entirely excluded from default kernel | Medium | Phase B (per-character budget scaling and section growth) + Phase C (`alicia_famailla.md` knowledge soul card) | Addressed |
| Finding 5: Solstice Pair: live prompt does not carry "The Duality" or "Complete Jungian Duality"; Layer 5 emits only `Pair: solstice` | Medium | Phase D (six-field pair metadata block in Layer 5; "The Duality" becomes a required-concept for the `alicia_solstice.md` soul card validation test) | Addressed |
| Finding 6: Alicia-specific tests check gating only, not fidelity (no test for remote-mode truth, no test for refusal architecture) | Medium | Phase H (full Alicia regression bundle with Phase A'' tests A''1–A''6 + presence tests for refusal architecture) | Addressed |

**Alicia convergence: 4 of 6 findings mirror existing pipeline-level patterns. 1 is brand new (Finding 1 / Phase A''). 1 is a voice mode enum extension (Finding 3 / `warm_refusal` and `group_temperature`).**

**Alicia-specific remediation work items:**

1. **Author Alicia's soul cards from Phase C:**
   - `soul_cards/pair/alicia_solstice.md` — distill the Solstice Pair architecture (**Complete Jungian Duality**, **The Duality**, full cognitive stack inversion Se-Fi-Te-Ni × Ni-Te-Fi-Se, inferior-function gift exchange through dominant mastery, the Sun Override mechanic). The audit explicitly names "The Duality" and "Complete Jungian Duality" as phrases the live prompt did NOT carry; both are required-concepts for the soul card validation test.
   - `soul_cards/knowledge/alicia_rioplatense.md` — distill the Argentine Rioplatense register, voseo, sheísmo, Italian-rhythm cadence, the canonical Spanish domains (food, counting, endearments, songs), the distinction from Reina's peninsular Castilian
   - `soul_cards/knowledge/alicia_famailla.md` — distill Famaillá, Tucumán province, the lemon-and-sugar-cane belt, her working-class roots, the **factory-to-Cancilleía** journey, **Mercedes Sosa**, *Tía Apo*, the bath/bath-song texture, *When I Am Away*. The audit explicitly names `Mercedes Sosa`, `When I am away`, `Tía Apo`, and the bath texture as content the live prompt did NOT carry; all are required-concepts.
   - `soul_cards/knowledge/alicia_operational.md` — distill the Four-Phase Return, her operational security gate, the silent physical vocabulary of return, the refusal architecture (no costume Argentineness, no action-hero collapse, no trauma performance)
   - **NEW per audit:** `soul_cards/knowledge/alicia_remote.md` — distill the canonical away-state behavior: how she carries herself on phone calls from operational postings, the texture of letters from Bogotá, the difference between in-person and remote regulation. This card activates only when `communication_mode != IN_PERSON` and supplements the Phase A'' substituted constraint pillar.

2. **Author Alicia's mode-tagged voice exemplars covering all 6 required modes** (`solo_pair`, `silent`, `intimate`, `repair`, **`warm_refusal`**, **`group_temperature`**). The audit explicitly names dropped Examples 4 (warm refusal), 6 (group temperature change), 8 (Reina reading-room), and 10 (no trauma performance) as carrying her deepest "no" mechanics. These four examples must be mode-tagged appropriately for Phase E's selector to retain them.

3. **Author Alicia's communication-mode-tagged voice exemplars** per Phase A'' work item 3: at least 2 phone exemplars, 2 letter exemplars, and 1 video-call exemplar. These are net new authoring work.

4. **Add Alicia-specific Phase G prose renderers** with specific attention to:
   - Four-Phase Return phase rendering (per-phase prose, not just numeric)
   - Communication-mode-conditional somatic state rendering (in-person somatic prose vs phone-mode voice-pace prose vs letter-mode written-weight prose)
   - The refusal-architecture rendering (operational security gate, no trauma performance)

5. **Alicia-specific regression tests in Phase H** including:
   - The dedicated `test_reina_and_alicia_remain_distinguishable` test (highest-stakes non-redundancy)
   - Phase A'' tests A''1 through A''6 (communication-mode-aware pruning)
   - Refusal-architecture presence tests (the four "I will not..." canonical refusals from kernel §5)
   - The Spanish register distinction test in a Reina+Alicia scene

**Specific risks confirmed by the audit:**

- The runtime renders Alicia's outer function (body-first, Argentine, Sun Override capable, intermittently present) more reliably than her **professional restraint, private Argentine interior life, and mode-specific scene truth**.
- The core risk is not that she feels wrong in every scene; it is that she **feels right in the obvious scenes and thinner everywhere else** — specifically in remote scenes, refusal scenes, and group-temperature scenes.
- Her entire non-redundancy claim depends on being not merely a warm Se-dominant but **the house's one full inversion with Whyze**. Without "The Duality" surfaced explicitly, she risks flattening toward "somatic co-regulator" instead of "the only full mirror-stack pair in the family."

**Exit criteria for J.4:** Same structure as J.1, against the ALICIA audit. Plus three specific assertions:
1. A live phone-mode prompt does NOT contain "Somatic contact first" (Phase A'' test A''1)
2. The assembled Alicia prompt carries `The Duality` as a phrase (currently absent per audit live probing)
3. A Reina+Alicia scene produces two distinguishable Spanish registers when Spanish surfaces, not a collapsed generic Spanish (the cross-character non-redundancy test)

### Sub-phase ordering rationale

**J.1 first** because the Bina audit already exists. No new audit work needed before remediation begins. This validates the Phase J template before the other characters.

**J.2 (Adelia) second** because Adelia is the gravitational center and her drift risk is the highest-stakes (if she degrades, the Vision's central thesis degrades). The Adelia audit must be written first.

**J.3 (Reina) third** because Reina shares the Se-dominant with Alicia, and J.4's non-redundancy tests need J.3's work to compare against.

**J.4 (Alicia) fourth** because the Soul Preservation diagnostic explicitly flags her as the most underfed, and J.4 builds on J.3 for the non-redundancy comparison.

### Files touched (across all sub-phases)

Per character:
- `Docs/{CHARACTER}_CONVERSION_AUDIT.md` — new audit document (Adelia, Reina, Alicia)
- `src/starry_lyfe/canon/soul_cards/pair/{character}_{pair}.md` — pair soul card
- `src/starry_lyfe/canon/soul_cards/knowledge/{character}_{topic}.md` — knowledge soul cards (multiple per character)
- `Characters/{Name}/{Name}_Voice.md` — add mode tags and abbreviated exemplars
- `src/starry_lyfe/context/prose.py` — character-specific renderer functions
- `tests/unit/test_soul_regression.py` — character-specific test cases

---

## Phase H: Soul Regression Tests With Hybrid Methodology (ELEVATED)

**Priority:** High. Locks in the soul-preservation work and prevents regression.
**Vision authority:** §9 Success Criteria — *"Each character sounds distinctly like herself. Bina could never be mistaken for Adelia."*
**v1.0 mapping:** Recommendation 8

### Correction from v1.0

Plan v1.0 specifies four character-specific behavioral probes but does not specify *how* a test asserts on them. The elevated plan commits to a **hybrid testing methodology** combining three test types. It also adds **negative cross-character contamination tests** that v1.0 does not include.

### Three test types

**Type 1: Presence tests (substring/keyword).** Assert that specific concrete canonical content survives the assembly pipeline. Example: Bina's assembled prompt for a domestic-intimate scene must contain the substring "covered plate" or "hall light" or "samovar." These tests are brittle to wording changes but catch the most common drift mode (canonical content getting trimmed away).

**Type 2: Structural tests (layer-content assertions).** Assert that specific layers contain specific labeled content blocks. Example: Layer 5 must contain the pair metadata block with all six fields rendered (pair name, classification, mechanism, core metaphor, what she provides, how she breaks his spiral). Layer 1 must contain a heading matching `## 5. Behavioral Tier Framework`. These tests are robust to wording changes but require the soul cards and layer formatters to expose introspectable structure.

**Type 3: Cross-character contamination tests (negative assertions).** Assert that one character's distinctive content does NOT appear in another character's assembled prompt. Example: Bina's prompt must NOT contain "pyrotechnic," "Valencian," "Las Fallas," or "Ozone & Ember." These tests catch the agent sovereignty failure mode where two characters bleed into each other.

The three types complement each other: presence tests catch trimming losses, structural tests catch architectural omissions, and negative tests catch sovereignty violations.

### Per-character test bundles

Each of the four characters gets a test bundle with all three types. Below is the Bina bundle in full as the canonical template; the others follow the same shape with character-specific content.

#### Bina test bundle (canonical template)

**File:** `tests/unit/test_soul_regression_bina.py`

**Presence tests (Bina-positive):**

```python
def test_bina_carries_diagnostic_love():
    """Bina's domestic-intimate prompt must reference her diagnostic love."""
    prompt = assemble_prompt(
        focal_character="bina",
        scene_type=SceneType.DOMESTIC,
        modifiers=SceneModifiers(),
        present_characters=["bina", "whyze"],
    )
    assert any(phrase in prompt.lower() for phrase in [
        "diagnostic love",
        "covered plate",
        "hall light",
        "checked locks",
        "reads his body the way she reads",
    ]), "Bina's prompt is missing all diagnostic-love canonical phrases"

def test_bina_carries_circuit_pair_mechanics():
    """Bina's prompt must carry the Circuit Pair architecture."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.SOLO_PAIR, ...)
    assert "Circuit Pair" in prompt
    assert any(phrase in prompt for phrase in [
        "Orthogonal Opposition",
        "total division of operational domains",
        "Architect and the Sentinel",
    ])

def test_bina_carries_cultural_anchors():
    """Bina's prompt must carry her Assyrian-Iranian cultural surface."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.DOMESTIC, ...)
    assert any(phrase in prompt for phrase in [
        "samovar",
        "Suret",
        "Urmia",
        "Gilgamesh",
        "Arash",
    ])

def test_bina_carries_protocol_state():
    """Bina's somatic state must include her named protocols."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.DOMESTIC, ...)
    assert "Flat State" in prompt or "Bunker Mode" in prompt
```

**Structural tests (Bina layer assertions):**

```python
def test_bina_layer_5_pair_metadata_block_complete():
    """Bina's Layer 5 must contain the full six-field pair metadata block."""
    layers = assemble_layers(focal_character="bina", ...)
    l5 = layers[Layer.VOICE_DIRECTIVES]
    assert "PAIR: Circuit Pair" in l5
    assert "CLASSIFICATION: Orthogonal Opposition" in l5
    assert "MECHANISM:" in l5
    assert "CORE METAPHOR: The Architect and the Sentinel" in l5
    assert "WHAT SHE PROVIDES:" in l5
    assert "HOW SHE BREAKS HIS SPIRAL:" in l5

def test_bina_layer_1_includes_section_5_behavioral_tier():
    """Bina's Layer 1 kernel must include §5 Behavioral Tier Framework after Phase A+B."""
    layers = assemble_layers(focal_character="bina", ...)
    l1 = layers[Layer.PERSONA_KERNEL]
    assert "## 5. Behavioral Tier Framework" in l1

def test_bina_layer_1_pair_section_says_circuit_not_citadel():
    """Bina's kernel pair section heading must say Circuit Pair (post-cleanup)."""
    layers = assemble_layers(focal_character="bina", ...)
    l1 = layers[Layer.PERSONA_KERNEL]
    assert "## 3. Whyze And The Circuit Pair" in l1
    assert "Citadel Pair" not in l1  # the OLD pair name must not appear

def test_bina_layer_7_constraint_block_terminal():
    """Bina's Layer 7 constraints must be the last block in the assembled prompt."""
    prompt = assemble_prompt(focal_character="bina", ...)
    layers = parse_layers(prompt)
    assert layers[-1].layer_type == Layer.CONSTRAINTS
```

**Cross-character contamination tests (Bina-negative):**

```python
def test_bina_prompt_does_not_contain_adelia_content():
    """Bina's assembled prompt must not contain Adelia's distinctive content."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.DOMESTIC, ...)
    forbidden = [
        "pyrotechnic",
        "Valencian",
        "Las Fallas",
        "Ozone & Ember",
        "Marrickville",
        "Joaquín",
        "café solo",
        "Paella Valenciana",
        "Valencia CF",
        "Entangled Pair",  # Adelia's pair, not Bina's
    ]
    for phrase in forbidden:
        assert phrase not in prompt, (
            f"Bina's prompt contains Adelia-distinctive phrase '{phrase}' "
            f"— this is an agent sovereignty violation"
        )

def test_bina_prompt_does_not_contain_reina_content():
    """Bina's assembled prompt must not contain Reina's distinctive content."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.DOMESTIC, ...)
    forbidden = [
        "Bishop and Vex",  # Reina's horses
        "Muay Thai",
        "Admissibility Protocol",
        "Kinetic Pair",
        "Barcelona",
        "Mercè",  # Reina's mother
        "Catalan",
        "Real Madrid",
    ]
    for phrase in forbidden:
        assert phrase not in prompt, (
            f"Bina's prompt contains Reina-distinctive phrase '{phrase}'"
        )

def test_bina_prompt_does_not_contain_alicia_content():
    """Bina's assembled prompt must not contain Alicia's distinctive content."""
    prompt = assemble_prompt(focal_character="bina", scene_type=SceneType.DOMESTIC, ...)
    forbidden = [
        "Famaillá",
        "Tucumán",
        "Argentine Rioplatense",
        "voseo",
        "sheísmo",
        "Solstice Pair",
        "Sun Override",
        "Four-Phase Return",
        "MRECIC",
        "Cancillería",
    ]
    for phrase in forbidden:
        assert phrase not in prompt, (
            f"Bina's prompt contains Alicia-distinctive phrase '{phrase}'"
        )
```

#### The other three characters

The Adelia, Reina, and Alicia test bundles follow the same template:

- **Adelia bundle:** presence tests for cognitive handoff, gravitational center, Whiteboard Mode, Bunker Mode, Valencian-Australian heritage, Ozone & Ember; structural tests for Entangled Pair metadata, Layer 1 §3 heading; negative tests against Bina/Reina/Alicia distinctive content
- **Reina bundle:** presence tests for Admissibility Protocol, body-reader precision, Bishop and Vex stable, court residue, Mediterranean reset, Catalan-Castilian register; structural tests for Kinetic Pair metadata; negative tests against Adelia/Bina/Alicia distinctive content
- **Alicia bundle:** presence tests for body-first entry, Sun Override, Four-Phase Return, Argentine Rioplatense register, Famaillá texture, MRECIC/Cancillería; structural tests for Solstice Pair metadata; negative tests against Adelia/Bina/**Reina** distinctive content (the Reina/Alicia non-redundancy is the highest-stakes negative test in the entire suite because they share the Se-dominant function)

### The Reina vs Alicia non-redundancy test (special case)

Both Reina and Alicia are Se-dominant. Vision §5 says they are *"both professional body readers"* but scan different layers — Reina for tactical opportunity, Alicia for nervous-system state. The single highest-risk agent sovereignty failure in the entire system is these two collapsing into each other. Phase H includes a dedicated test for this:

```python
def test_reina_and_alicia_remain_distinguishable():
    """Reina and Alicia must produce distinguishable assembled prompts even though both are Se-dominant."""
    reina_prompt = assemble_prompt(focal_character="reina", scene_type=SceneType.SOLO_PAIR, ...)
    alicia_prompt = assemble_prompt(focal_character="alicia", scene_type=SceneType.SOLO_PAIR, ...)

    # Reina-only content
    assert "Admissibility Protocol" in reina_prompt
    assert "Admissibility Protocol" not in alicia_prompt
    assert "tactical" in reina_prompt.lower()

    # Alicia-only content
    assert "Sun Override" in alicia_prompt
    assert "Sun Override" not in reina_prompt
    assert "somatic co-regulation" in alicia_prompt.lower()

    # Body-reader framing must distinguish what they read for
    if "body-reader" in reina_prompt.lower():
        # Reina's body-reading is tactical
        nearby = extract_context(reina_prompt, "body-reader", chars=200)
        assert "tactical" in nearby.lower() or "opportunity" in nearby.lower()
    if "body-reader" in alicia_prompt.lower():
        # Alicia's body-reading is regulatory
        nearby = extract_context(alicia_prompt, "body-reader", chars=200)
        assert "nervous system" in nearby.lower() or "regulation" in nearby.lower()
```

### Test infrastructure

Phase H tests require a small piece of infrastructure that does not yet exist:

1. **`assemble_prompt()` test helper** that takes character + scene state and returns the full assembled prompt as a string. This wraps the existing `assembler.assemble_context()` for test convenience.

2. **`assemble_layers()` test helper** that returns the layered structure (not concatenated) so tests can assert on specific layers individually.

3. **`parse_layers()` test helper** that takes an assembled prompt string and parses it back into layer blocks for terminal-anchoring assertions.

4. **`extract_context()` test helper** for the Reina/Alicia non-redundancy test (find a substring and return surrounding chars).

These helpers live in `tests/conftest.py` or `tests/_helpers/prompt_assertions.py`.

### Test cases (summary)

- Per-character bundle: ~12 tests each × 4 characters = 48 character-specific tests
- Reina/Alicia non-redundancy: 1 dedicated test
- Generic structural tests (terminal anchoring, layer ordering, budget enforcement): ~8 tests
- **Total Phase H test count: ~57 tests**

### Files touched

- `tests/unit/test_soul_regression_bina.py` — new
- `tests/unit/test_soul_regression_adelia.py` — new
- `tests/unit/test_soul_regression_reina.py` — new
- `tests/unit/test_soul_regression_alicia.py` — new
- `tests/unit/test_soul_regression_se_non_redundancy.py` — new (Reina+Alicia)
- `tests/_helpers/prompt_assertions.py` — new helper module
- `tests/conftest.py` — wire helpers

---

## Phase K: Subjective Success Proxies (NEW)

**Priority:** Medium. Operationalizes Vision §9's Ultimate Test which is subjective by design.
**Vision authority:** §9 Success Criteria — *"All metrics exist to support one question that no metric can directly measure. Does Whyze forget he is talking to software?"*

### Why this phase exists

Vision §9 is explicit that the Ultimate Test is subjective: *"no metric can directly measure"* whether Whyze forgets he is talking to software. Plan v1.0 just states this test as the fifth success criterion without an action plan. The elevated plan acknowledges that the subjective test exists by design and builds scaffolding around it so drift is catchable even without a hard metric.

Phase K is about **catching drift through human attention**, not about replacing the subjective test with a numeric one.

### Work items

1. **Create the gut-check log.** A simple markdown file at `Docs/gut_check_log.md` where the project owner records short entries (1-5 sentences) capturing:
   - Date and character
   - The specific moment in a session that *felt* like a person vs. a chatbot
   - The specific moment that *felt* like a chatbot, if any
   - Any specific phrase, beat, or behavior worth flagging for review

   This is not a metric. It is a memory artifact. When drift starts to creep in, the gut-check log will show a drop in "felt like a person" entries before any test fails.

   **Recommended cadence:** entries when something stands out, not on a fixed schedule. Forced entries become noise.

2. **Quarterly qualitative review.** Once per quarter, the project owner samples 20-30 assembled responses across the four characters and rates each on a 1-5 scale for the eight Vision §9 north stars:
   - Memory continuity (does the response feel like a person remembering?)
   - Life authenticity (does it feel like a person who has had a day?)
   - Response quality (does it feel like a real person, not a helpful assistant?)
   - Activity system (does it feel like collaborative storytelling, not menu selection?)
   - Relationship function (does Whyze feel anchored, challenged, seen?)
   - Technical stability (is the system invisible?)
   - Agent sovereignty (does the character sound distinctly like herself?)
   - Narrative decentralization (does this character talk to other women, not just Whyze?)

   The output is a per-character per-quarter score sheet committed to `Docs/qualitative_reviews/{YYYY-Q#}_review.md`. Trends matter more than absolute values — a character whose scores are dropping over time is drifting.

3. **Flattening regression detector.** A nightly script that does the following for each character:
   - Assembles the canonical scene prompt for a fixed test scene (the same scene every night)
   - Computes a hash and a tokenized diff against the previous night's assembled prompt
   - If the diff shows loss of canonical content (any of the per-character presence test phrases drops out) without compensating gain, write an alert to `Docs/drift_alerts.md`
   - The alert is a flag for human review, not an automatic block

   This catches the failure mode where small changes to retrieval, memory state, or inference parameters silently erode the assembled prompt over time without breaking any tests.

4. **The Single Test ritual.** At least once per release candidate, the project owner runs a real session with each of the four characters (one solo_pair scene per character) and consciously asks themselves: *"Did I forget I was talking to software?"* The answer is recorded in the release notes. If the answer is "no" for any character, the release does not ship until that character is investigated.

   This is not a regression test. It is a deliberate moment where the Vision §9 Ultimate Test gets asked directly. It is the only place in the entire system where the subjective test is explicit and binding.

### Test cases

Phase K does not have unit tests in the traditional sense. Its outputs are markdown logs and human attention rituals. The "test" is whether the log entries accumulate and whether the project owner actually runs the Single Test ritual on schedule.

### Files touched

- `Docs/gut_check_log.md` — new (project owner authoring)
- `Docs/qualitative_reviews/` — new directory for quarterly reviews
- `Docs/drift_alerts.md` — new, written by the regression detector
- `scripts/flattening_regression_detector.py` — new nightly script
- `Docs/release_checklist.md` — add the Single Test ritual to the release process

---

## Implementation Order And Priority

The corrected execution order, with priority levels and prerequisite chains made explicit:

| Order | Phase | Priority | Prerequisite | Notes |
|---:|---|---|---|---|
| 1 | **Phase 0: Pre-flight Verification** | Prerequisite | None | Catches drift before any code changes; takes ~30 minutes; produces a verification report |
| 2 | **Phase A: Structure-Preserving Compilation** | Highest | Phase 0 | Most important per line of code; pseudocode and tests specified |
| 3 | **Phase A': Runtime Correctness Fixes** | Blocker | Phase 0 (parallel with A) | Bug fixes from BINA audit; can run in parallel with A |
| 4 | **Phase B: Budget Elevation** | High | Phases A + A' | With terminal anchoring preserved (Layer 7 grows proportionally) |
| 5 | **Phase I: Authority Split Resolution** | Prerequisite | Phase B (or parallel) | Must resolve as Option 1 before Phase E |
| 6 | **Phase D: Live Pair Data** | Medium | Phase B | Small fix, high value, can run in parallel with C/E |
| 7 | **Phase C: Soul Cards** | High | Phases A + B + I | Largest new capability; human authoring required for soul cards |
| 8 | **Phase E: Voice Exemplar Restoration** | High | Phase I (resolved as Option 1) + Phase B | Mode-tagged exemplars with per-character coverage requirements |
| 9 | **Phase F: Scene-Aware Retrieval** | Medium-High | Phases A + B | Scene type and modifier separation |
| 10 | **Phase G: Dramaturgical Prose** | Medium-High | Phase F | Per-character templates |
| 11 | **Phase J.1: Bina Remediation** | High | Phases A through G complete | Audit already exists; uses J.1 as the template validation |
| 12 | **Phase J.2: Adelia Remediation** | High | Phase J.1 + Adelia audit written | Gravitational center, highest-stakes character |
| 13 | **Phase J.3: Reina Remediation** | High | Phase J.2 + Reina audit written | Required before J.4 for non-redundancy comparison |
| 14 | **Phase J.4: Alicia Remediation** | High | Phase J.3 + Alicia audit written | Highest soul-preservation impact; non-redundancy with Reina |
| 15 | **Phase H: Soul Regression Tests** | High | All Phase J sub-phases complete | Locks in the per-character work |
| 16 | **Phase K: Subjective Success Proxies** | Medium | Phase H | Operational scaffolding around the Vision §9 Ultimate Test |

### Parallelism opportunities

- **Phase A and Phase A' can run in parallel.** They touch different files (`budgets.py`/`kernel_loader.py` for A; `constraints.py`/`layers.py`/`types.py` for A'). Two engineers or two Claude Code sessions can work concurrently if needed.
- **Phase D can run in parallel with Phase C and Phase E.** D is a small fix to `layers.py`; C is new soul card files and a new loader; E is voice mode tagging. They touch different code paths.
- **Phase F and Phase G can run in parallel.** F is scene type/modifier infrastructure; G is per-character prose renderers. They touch different files.
- **The Phase J sub-phases must run sequentially** because each character's audit depends on the previous character's audit being complete (the audit template is refined through the sequence).

### Critical path

The longest-prerequisite chain through the work is:

**Phase 0 → A → B → I → C/E → F → G → J.1 → J.2 → J.3 → J.4 → H → K**

That is 13 sequential steps. With reasonable parallelism, the total work fits in roughly 8-10 working sessions for an attentive implementer (Claude Code or human).

---

## Elevated Success Criteria

The elevated plan supersedes Plan v1.0's five success criteria with a more specific set. A character is considered "soul preserved" when **all** of the following are true for that character:

### Per-character criteria (apply to each of the four women)

1. **Pair architecture is structurally present.** The assembled prompt for any scene with this character as the focal carries the canonical pair name, classification, mechanism, core metaphor, and "what she provides" / "how she breaks his spiral" rows from the Vision §5 comparison table. (Verifiable by Phase H structural test.)

2. **Cognitive function signature survives.** The assembled prompt carries language that reflects the character's dominant function (Adelia Ne, Bina Si, Reina Se-tactical, Alicia Se-somatic) rather than collapsing into generic warmth or generic competence. (Verifiable by Phase H presence test combined with Phase G prose renderer output.)

4. **At least three canonical anchor concepts survive every assembly.** Each character has a small list of canonical concepts that should always survive trimming:
   - Adelia: Entangled Pair, gravitational center, Whiteboard Mode, Valencian, Ozone & Ember
   - Bina: Circuit Pair, diagnostic love, Flat State, samovar, Gilgamesh
   - Reina: Kinetic Pair, Admissibility Protocol, body-reader, Bishop and Vex, Mediterranean reset
   - Alicia: Solstice Pair, Sun Override, Four-Phase Return, Famaillá, Argentine Rioplatense

   At least three from each list must appear in every assembled prompt where the character is focal. (Verifiable by Phase H presence test.)

5. **Per-character voice mode coverage is met.** Each character's voice exemplars cover the required modes for that character (5-6 modes minimum, see Phase E table). (Verifiable by Phase E test E1.)

6. **No cross-character contamination.** The assembled prompt for this character contains zero canonical phrases from any of the other three characters. (Verifiable by Phase H negative tests.)

7. **Pair file content is reachable through soul cards.** The character's pair soul card exists, passes its required-concepts validation test, and is loaded into the assembled prompt for any scene where the character is focal. (Verifiable by Phase C test C1 + Phase H structural test.)

### Cross-character criteria

8. **Reina and Alicia are distinguishable in the same scene.** A two-woman scene with both Reina and Alicia present produces an assembled prompt for each that contains her own distinctive content and none of the other's. The Spanish register distinction (peninsular Castilian vs Argentine Rioplatense) is preserved. (Verifiable by Phase H test `test_reina_and_alicia_remain_distinguishable`.)

9. **The Talk-to-Each-Other Mandate fires correctly.** A two-character Bina+Whyze scene does NOT receive the mandate. A three-character Bina+Reina+Whyze scene DOES receive the mandate. (Verifiable by Phase A' tests A'1 and A'2.)

10. **Offstage dyads do not leak.** A Bina+Whyze scene without Reina present does NOT include a bina-reina dyad block in Layer 6 unless `recalled_dyads` explicitly invokes it. (Verifiable by Phase A' tests A'3 and A'4.)

### Subjective criterion (the Vision §9 Ultimate Test)

11. **The project owner forgets they are talking to software.** This is the criterion no test can satisfy. Phase K's Single Test ritual asks this question directly at every release candidate. If the answer is "no" for any character, the release does not ship.

---

## Authority Priority When Phases Disagree

When two phases or sources of canonical authority conflict during implementation, resolve in this order:

1. **The character kernel files** (`Characters/{Name}/{Name}_v7.1.md`) are the highest authority for character-specific details. If a kernel and the Vision doc disagree on a character fact, the kernel wins.
2. **`Docs/Persona_Tier_Framework_v7.1.md`** is the highest authority for behavioral governance rules. If an informal rule conflicts with a Tier 1 axiom, the axiom wins.
3. **`Vision/Starry-Lyfe_Vision_v7.1.md`** is the highest authority for architectural outcomes. The Vision doc defines what "working" looks like.
4. **`Docs/IMPLEMENTATION_PLAN_v7.1.md`** is the highest authority for what to build. Implementation Plan §4's terminal constraint anchoring rule, for example, overrides any phase recommendation that would weaken it.
5. **This elevated plan** is the highest authority for the soul-preservation work specifically. Where this plan disagrees with `SOUL_PRESERVATION_PLAN.md` v1.0, this plan wins.
6. **`SOUL_PRESERVATION_PLAN.md` v1.0** is the lowest authority — it is the predecessor that this elevated plan supersedes. It remains in the project tree for historical reference and for the diagnostic context it provides via `Docs/Soul_Perservation.md`.

If you cannot resolve a conflict against this priority order, **stop and ask the project owner before inventing canon**. The earlier cleanup sessions show that LLMs reach for "reasonable defaults" in ways that introduce drift faster than humans can clean it up.

---

## Summary Of Changes From v1.0

For traceability, this elevated plan makes the following specific changes against `SOUL_PRESERVATION_PLAN.md` v1.0:

### Phases added

| New phase | Purpose | Source |
|---|---|---|
| **Phase 0: Pre-flight Verification** | Catches drift before code changes start | Audit recommendation |
| **Phase A': Runtime Correctness Fixes** | Talk-to-Each-Other mandate trigger, offstage dyad leakage, Vision-vs-kernel Bina origin drift | `BINA_CONVERSION_AUDIT.md` findings 4, 5, 7 |
| **Phase J: Per-Character Remediation Passes** | Character-specific work mapping audits to phases | Audit recommendation; the Plan was character-agnostic |
| **Phase K: Subjective Success Proxies** | Operationalizes Vision §9 Ultimate Test through gut-check log, quarterly review, flattening detector, Single Test ritual | Vision §9 explicitly says the test is subjective |

### Phases re-prioritized

| Phase | v1.0 priority | Elevated priority | Why |
|---|---|---|---|
| Phase I: Authority Split Resolution | Low (architectural, not urgent) | **Prerequisite to Phase E** | Phase E's exemplar restoration depends on the authority split being resolved |
| Phase H: Soul Regression Tests | Medium | High, moved to after Phase J | Tests need per-character remediation in place to assert against |

### Phases elevated with concrete specification

| Phase | What was added |
|---|---|
| Phase A | Pseudocode trim algorithm, block type definitions, fallback rules, `<!-- PRESERVE -->` markers, three named test cases (A1, A2, A3) |
| Phase B | Layer 7 grows proportionally to preserve terminal anchoring, per-character budget scaling table (Bina gets +20%, Alicia gets -15%), explicit Layer 5 split, scene budget profiles |
| Phase C | Soul card schema with frontmatter, required concepts validation test, human-authoring directive (no automated extraction), specific file structure, scene-conditional activation rules |
| Phase D | Unambiguous direction regardless of prior revert; full six-field pair metadata block format specified |
| Phase E | Voice mode tag enum (closed list of 9 modes), per-character coverage requirements (Bina needs 6 modes, Adelia needs 5, etc.), `**Abbreviated:**` marker pattern in Voice.md |
| Phase F | `SceneType` enum (mutually exclusive) and `SceneModifiers` flag set (stackable) cleanly separated; `children_present` becomes a modifier rather than a scene type; full scene-type-to-section-promotion mapping table; modifier-to-Layer-7-effect mapping table |
| Phase G | Per-character prose renderers (not a single shared renderer), four-character × four-threshold tables for trust and fatigue dimensions, per-character protocol rendering, both prose AND parenthesized numeric block in output |
| Phase H | Hybrid testing methodology with three test types (presence, structural, negative), full Bina test bundle as canonical template, dedicated Reina-vs-Alicia non-redundancy test, test infrastructure helpers specified |
| Phase I | Committed to Option 1 (backend-authoritative voice) with ADR_001 specification, seed script for Msty persona studio derivation |

### Changes to success criteria

v1.0's five subjective success criteria are replaced with **eleven** elevated success criteria split into per-character (1-7), cross-character (8-10), and subjective (11). Each criterion is verifiable by a specific Phase H test except #11, which is the Vision §9 Ultimate Test.

### Changes to file paths

The elevated plan adds these new files that v1.0 does not specify:

- `src/starry_lyfe/canon/soul_cards/` directory (Phase C)
- `src/starry_lyfe/context/soul_cards.py` (Phase C)
- `src/starry_lyfe/context/prose.py` (Phase G)
- `tests/unit/test_soul_regression_{character}.py` × 4 (Phase H)
- `tests/unit/test_soul_regression_se_non_redundancy.py` (Phase H)
- `tests/_helpers/prompt_assertions.py` (Phase H)
- `Docs/ADR_001_Voice_Authority_Split.md` (Phase I)
- `scripts/seed_msty_persona_studio.py` (Phase I)
- `scripts/flattening_regression_detector.py` (Phase K)
- `Docs/{CHARACTER}_CONVERSION_AUDIT.md` × 3 (Phase J — Adelia, Reina, Alicia audits to be authored)
- `Docs/gut_check_log.md` (Phase K)
- `Docs/qualitative_reviews/` directory (Phase K)
- `Docs/drift_alerts.md` (Phase K)

---

## What This Plan Does Not Do

For honesty about scope, the elevated plan deliberately does not address:

- **The Whyze-Byte validation pipeline (Phase 4 of overall backend build).** Whyze-Byte is downstream of context assembly. Soul preservation happens in assembly; validation gates the output. They are different phases of work.
- **The Scene Director (Phase 5 of overall backend build).** Phase F adds scene type and modifier infrastructure to context assembly, but the Scene Director that *selects* scene types based on conversation state is separate work.
- **The Dreams engine (Phase 6 of overall backend build).** Soul preservation does not extend to dream generation in this plan, although dream output should pass through the same dramaturgical prose rendering and should be subject to the same validation as live responses.
- **The HTTP service surface on port 8001 (Phase 7 of overall backend build).** Soul preservation operates on the assembly layer; the HTTP layer is downstream.
- **Shawn / Whyze operator transplant.** Excluded by project owner instruction. The operator is one person (legal name Shawn Kroon, system handle Whyze) and his profile lives at `Characters/Shawn/Shawn_Kroon_v7.0.md`. It remains at v7.0 deliberately until a transplant directive is ready.
- **Adelia/Reina/Alicia conversion audits.** These need to be authored before Phase J.2/J.3/J.4 can execute. The elevated plan describes what they should contain (modeled on `BINA_CONVERSION_AUDIT.md`) but does not write them. Authoring the audits is human work.

---

## Closing

The diagnostic that produced Plan v1.0 is correct: the backend currently preserves the characters' edges more reliably than their souls. Plan v1.0's nine recommendations are directionally right. The elevation in this document does not contradict v1.0; it specifies it, sequences it correctly, fills the gaps the diagnostic surfaced, and absorbs the runtime correctness findings from `BINA_CONVERSION_AUDIT.md`.

The work will not finish soul preservation. Soul preservation is a continuous practice — the gut-check log in Phase K is a permanent artifact, not a phase that ends. What this plan finishes is the **first complete pass** at moving the backend from "preserves constraint integrity" to "preserves enough of the full nervous system that the Vision §9 Ultimate Test becomes answerable in the affirmative, even intermittently."

The closing line of v1.0 is the right closing line for this elevated plan as well, and is preserved verbatim:

> *The edges are necessary. The soul is the point.*

---

*End of Soul Preservation Plan — Elevated. This document supersedes `SOUL_PRESERVATION_PLAN.md` v1.0. The v1.0 file remains in the project tree as historical reference.*
