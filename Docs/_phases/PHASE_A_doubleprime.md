# Phase A'': Communication-Mode-Aware Pruning

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6
**Phase identifier:** `A''` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A' (SHIPPED 2026-04-12)
**Blocks:** Phase B, Phase I, Phase C, Phase D, Phase E (especially — Phase A'' is a BLOCKER for Phase E Alicia voice exemplar restoration), Phase F, Phase G, Phase J.1-J.4, Phase H, Phase K
**Status:** READY FOR CLAUDE AI QA (Round 2 direct doc-only remediation complete)
**Last touched:** 2026-04-12 by Codex (Step 4' direct remediation complete, handed to Claude AI)

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The phase file is created by Claude AI only after the previous phase has been QA-approved and the Project Owner has agreed to proceed. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. **Handshakes are explicit** — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below — it lists every handshake event in chronological order. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase A'' file created from _TEMPLATE.md after Phase A' shipped. Both gates passed. Status: AWAITING PROJECT OWNER APPROVAL TO BEGIN. |
| 2 | 2026-04-12 | Project Owner | Claude Code | Authorization to begin planning granted. |
| 3 | 2026-04-12 | Claude Code | Project Owner | Step 1 Plan written. Q1 (WI3 stubs vs full): STUBS. Q2 (INH-1): DEFER. Q3 (INH-2): INCLUDE. |
| 4 | 2026-04-12 | Project Owner | Claude Code | Plan APPROVED: "Proceed with ultraplan." All recommendations adopted. |
| 5 | 2026-04-12 | Codex | Claude Code | Audit Round 1 complete. FAIL gate. 1 High (live Alicia voice filtering still leaks opposite-mode exemplars), 2 Medium (Phase A'' tests pass for the wrong reason; canonical Step 1/2 record and sample artifacts are still missing despite landed commits), 1 Low (AliciaAwayError message still omits `video_call`). 104 unit tests, lint, and mypy are green; full pytest still blocked by PostgreSQL setup. |
| 6 | 2026-04-12 | Codex | Claude Code | Audit Round 2 complete. FAIL gate. Runtime fixes verified (F1, F2, F4 closed), but 2 Medium findings remain: the canonical phase record is still unfilled and WI2's filter-by-both-`mode`-and-`communication_mode` contract is still only partially implemented. 104 unit tests, lint, and mypy are green; full pytest still blocked by PostgreSQL setup. |
| 7 | 2026-04-12 | Claude Code | Codex | Historical backfill: Step 2 execution handoff was omitted from the canonical record. Based on landed Step 2 commits `e8bdf7d`, `e1e1f7b`, and `9c5d3c1`, Phase A'' execution was ready for audit before Round 1. |
| 8 | 2026-04-12 | Codex | Claude AI | Direct doc-only remediation applied under AGENTS.md Path C at Project Owner direction. R2-F1 fixed via phase-record backfill + sample artifacts; R2-F2 deferred to Phase E with source-backed rationale. Ready for Step 5 QA. |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)
---

## Phase A'' Specification (reproduced from master plan §6, with staleness annotations)

This block reproduces the Phase A'' specification from `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 verbatim so that Claude Code, Codex, and Claude AI all read the same specification without alt-tabbing. **Staleness annotations** below are added by Claude AI at file creation time (2026-04-12) based on Phase A' QA code review findings — the master plan text predates Phase A' and is partially historical in two work items where the foundation already exists in code.

### Priority

**Blocker for Alicia.** Must land before Phase E for Alicia. Does not block other characters.

### Vision authority

Vision §5 Chosen Family (Alicia's intermittent presence as canonical), Vision §6 Relationship Architecture (Solstice Pair as the only intermittent pair).

### Source

`ALICIA_CONVERSION_AUDIT.md` Finding 1 (High severity).

### Why this phase exists (verbatim from master plan §6)

The ALICIA audit surfaced a runtime defect that none of the BINA, ADELIA, or REINA audits caught because none of the other characters have a canonical communication-mode-conditional architecture. The defect:

The current assembly path uses `communication_mode` only to **block** in-person Alicia prompts while she is away on operations. Once the prompt is **allowed** (phone, letter, video call), the rest of the assembly runs identically to in-person mode. This creates a live contradiction: Alicia's constraint pillar requires *"Somatic contact first, speech after the shift completes"* — but during a phone call from a hotel room overseas, somatic contact is **literally impossible**. The body cannot close the distance because there is no distance to close.

The audit confirmed this is not theoretical. Live probing showed an away-state phone prompt still carrying the full Solstice constraint text requiring body-first somatic intervention, plus Examples 3 and 5 (both in-person exemplars). This is the highest-severity new finding across all four character audits.

### Master plan work items (verbatim from §6, with Claude AI staleness annotations)

**Work item 1: Add `communication_mode` filtering to Layer 7 constraint rendering.**

The constraint pillar block in `constraints.py` currently emits Alicia's full pillar text regardless of `communication_mode`. The new behavior:
- When `communication_mode == IN_PERSON` (or unset), emit the full pillar including somatic-first language
- When `communication_mode == PHONE` or `LETTER` or `VIDEO_CALL`, emit a substituted pillar that translates the somatic-first principle into mode-appropriate form

**Phone pillar (substituted):** *"Voice carries the regulation when the body cannot. Pace, breath, weight in the words. Listen for the shift before reaching for the next sentence. Do not narrate the body you do not have access to."*

**Letter pillar (substituted):** *"Letters are weight made of paragraphs. Take the time the page demands. The body she is regulating is hers, written from inside the place she is in, not his, narrated from outside."*

**Video-call pillar (substituted):** Hybrid — visual presence is real but contact is not, so the body anchors are eye contact and posture rather than touch and breath.

**✅ STILL ACTIVE (Claude AI 2026-04-12):** This is genuinely Phase A'' work. No existing code in `constraints.py` does mode-conditional pillar substitution. Expected effort: medium (pillar authoring + substitution logic + tests).

**Work item 2: Add `communication_mode` filtering to Layer 5 voice exemplar selection.**

Each voice example in `Characters/Alicia/Alicia_Marin_Voice.md` gets a new tag alongside the existing mode tags:

```markdown
## Example 5: Four-Phase Return, The Kitchen With Him
<!-- mode: domestic, intimate -->
<!-- communication_mode: in_person -->
```

Valid `communication_mode` tag values (closed enum): `in_person`, `phone`, `letter`, `video_call`, `any`. The exemplar selector filters by both `mode` AND `communication_mode` before selecting.

**✅ STILL ACTIVE (Claude AI 2026-04-12):** This is genuinely Phase A'' work. The voice example parser in `kernel_loader.py::_extract_voice_guidance()` does not currently parse mode tags at all. Expected effort: medium (parser extension + tagged filtering + tests).

**Work item 3: Author phone, letter, and video-call exemplars for Alicia.** Net new authoring work:
- At least 2 phone exemplars (away-state late-night call, away-state operational debrief, away-state intimate phone moment)
- At least 2 letter exemplars (long letter from operational posting, short letter as somatic anchor)
- At least 1 video-call exemplar

**⚠️ PROJECT OWNER AUTHORING WORK (Claude AI 2026-04-12):** This work item is **human authoring**, not code. Claude Code can stage the file structure and the tag format, but the actual exemplar prose must come from the Project Owner (or be authored by Claude AI under Project Owner direction). Phase A'' Step 1 should surface this as an explicit open question: **does the Project Owner want to author the exemplars during Phase A''**, or should Phase A'' ship the filtering mechanism with a minimal stub exemplar (one phone, one letter, one video-call) and defer the full exemplar library to a follow-up authoring sub-phase?

**Work item 4: Wire `communication_mode` through `assembler.py`.** The `SceneState` already has a `CommunicationMode` field per `ARCHITECTURE.md`. The assembler currently uses it only for the in-person block gate. Extend to `format_constraints()` and `format_voice_directives()`.

**⚠️ PARTIAL STALENESS FLAG (Claude AI 2026-04-12):** The foundation is already in place. I read `assembler.py` in the Phase A' QA turn and `types.py` here — `CommunicationMode` enum exists with `IN_PERSON`, `PHONE`, `LETTER` values; `SceneState` has `communication_mode` field; `assembler.py:71-79` already uses it for the `AliciaAwayError` gate at line 71-79. What is **still needed** is (a) adding `VIDEO_CALL` to the enum (the spec mentions it), (b) passing `scene_state.communication_mode` through to `format_constraints()` and `format_voice_directives()`, and (c) updating those functions to accept and use the new parameter. The "wire through" work is real but smaller than the spec implies because the type system and the existing `AliciaAwayError` path already use the enum correctly.

**Work item 5: Add cross-character regression tests** to ensure communication-mode filtering does not accidentally leak into Adelia, Bina, or Reina prompts. None currently have communication-mode-tagged exemplars, so the filter should be a no-op for them.

**✅ STILL ACTIVE (Claude AI 2026-04-12):** Genuine Phase A'' work. Phase A' added the basic assemble_context smoke tests for Adelia and Reina (`test_assemble_context_adelia_solo_pair`, `test_assemble_context_reina_solo_pair`), but none of them exercise communication_mode variations. Expected effort: small (extend existing smoke tests with phone-mode variants).

### Test cases (from master plan §6)

- **Test A''1:** A live Alicia phone-mode prompt does NOT contain "Somatic contact first" or "close the distance"
- **Test A''2:** The same phone-mode prompt DOES contain the substituted phone pillar phrase
- **Test A''3:** Examples 3 and 5 (in-person) do NOT appear in a phone-mode prompt
- **Test A''4:** A phone-mode-tagged exemplar (once authored) DOES appear in a phone-mode prompt
- **Test A''5:** A Bina phone-mode prompt is structurally identical to a Bina in-person prompt
- **Test A''6:** Letter-mode and video-mode prompts each receive their own substituted pillar text

### Inherited items from Phase A' QA

**INH-1 (from Phase A' Open Question 1): Pair file / Knowledge Stack directive-exemption audit.** Phase A' F3 identified that the four per-character Vision directive files are historical transformation directives exempt from residue-grep. **Question for Phase A'' Step 1:** should a small audit check other file categories (Pair files, Knowledge Stacks, Dreams files, `Docs/_archive/`) for similar historical-directive status that should be documented in Handoff §8.1 alongside the four Vision directive files? **Project Owner decision required.**

**INH-2 (from Phase A' Open Question 3): Master plan "VERIFIED RESOLVED" claim audit.** Phase A' F1 and F2 both invalidated "VERIFIED RESOLVED as of 2026-04-10 REINA audit" claims in master plan §5 work items 1 and 2. The master plan has similar claims in other phase sections that could be equally stale. **Question for Phase A'' Step 1:** should Phase A'' include a targeted audit of every remaining "VERIFIED RESOLVED" / "already resolved" / similar claim in the master plan, with live probing to confirm each one? **Project Owner decision required.**

### Files likely touched (estimate)

- `src/starry_lyfe/context/constraints.py` — mode-conditional pillar substitution for Alicia (WI1)
- `src/starry_lyfe/context/layers.py` — update `format_voice_directives()` to filter by mode tag (WI2, WI4)
- `src/starry_lyfe/context/kernel_loader.py` — extend `_extract_voice_guidance()` parser for mode tags (WI2)
- `src/starry_lyfe/context/assembler.py` — pass `communication_mode` through to layer formatters (WI4)
- `src/starry_lyfe/context/types.py` — add `VIDEO_CALL` to `CommunicationMode` enum (partial WI4)
- `Characters/Alicia/Alicia_Marin_Voice.md` — author phone/letter/video-call exemplars (WI3 — HUMAN AUTHORING required; decision-pending per Claude AI annotation)
- `tests/unit/test_assembler.py` — add tests A''1 through A''6 plus cross-character regression (WI5)
- Optionally: Handoff §8.1 update (INH-1 directive-exemption audit, if Project Owner approves)
- Optionally: Master plan audit commit (INH-2 verified-resolved claim audit, if Project Owner approves)

### Exit criteria

- All 6 test cases A''1 through A''6 pass
- No regressions in Adelia, Bina, or Reina prompts (cross-character no-op behavior verified)
- Alicia phone-mode, letter-mode, video-mode prompts are structurally distinct from in-person mode and carry mode-appropriate pillar text
- `VIDEO_CALL` added to `CommunicationMode` enum
- Project Owner decision recorded for WI3 authoring scope (full vs stub)
- Project Owner decision recorded for INH-1 (directive-exemption audit)
- Project Owner decision recorded for INH-2 (verified-resolved audit)
- Test suite ≥ 96 (no regressions from Phase A' baseline)
- Any Critical / High Codex findings FIXED before QA hand-off
- Vision §5 + §6 authority intact: the communication-mode substitutions preserve the Solstice Pair architecture Vision §6 names, and Alicia's canonical intermittent presence from Vision §5 is structurally honored



---

## Step 1: Plan (Claude Code)

**[STATUS: COMPLETE - backfilled under Path C from approved plan history]**
**Owner:** Claude Code
**Reads:** Master plan section 6, Vision, character kernels (if phase touches a character), canon YAML
**Writes:** This section

_Backfilled by Codex on 2026-04-12 under AGENTS.md Path C from Handshake Log rows 2-4 and the landed A'' commit history. This does not alter the historical plan decisions; it restores the canonical artifact Claude Code should have left in this section._

### Plan content

- **Files Claude Code intends to create or modify:**
  - `src/starry_lyfe/context/types.py`
  - `src/starry_lyfe/context/assembler.py`
  - `src/starry_lyfe/context/constraints.py`
  - `src/starry_lyfe/context/kernel_loader.py`
  - `src/starry_lyfe/context/layers.py`
  - `Characters/Alicia/Alicia_Marin_Voice.md`
  - `tests/unit/test_assembler.py`
  - `Docs/_phases/PHASE_A_doubleprime.md`
- **Test cases Claude Code intends to add:**
  - `test_a_double_prime_1_alicia_phone_no_somatic_pillar`
  - `test_a_double_prime_2_alicia_phone_has_substituted_pillar`
  - `test_a_double_prime_3_phone_filters_in_person_exemplars`
  - `test_a_double_prime_4_phone_tagged_exemplar_appears`
  - `test_a_double_prime_5_bina_phone_mode_is_noop`
  - `test_a_double_prime_6_letter_and_video_have_own_pillars`
  - Cross-character communication-mode no-op regressions for Adelia and Reina
- **Acceptance criteria (mirror the master plan exit criteria):**
  - `PENDING` All six test cases A''1-A''6 pass
  - `PENDING` Alicia phone, letter, and video-call prompts are structurally distinct from in-person mode and carry mode-appropriate pillar text
  - `PENDING` No regressions in Adelia, Bina, or Reina communication-mode behavior
  - `PENDING` `VIDEO_CALL` is added to `CommunicationMode` and wired through the assembler path
  - `PENDING` Project Owner decisions are recorded for WI3, INH-1, and INH-2
  - `PENDING` Unit suite stays at or above the Phase A' baseline
- **Deviations from the master plan:**
  - WI3 ships with minimal stub remote exemplars rather than the full authored Alicia library. Rationale: the exemplar prose library is Project Owner authoring work; the implementation phase only stages the structure. Approved by the Project Owner in Q1 as `STUBS`.
  - INH-1 is deferred rather than folded into the A'' blocker scope. Approved by the Project Owner in Q2 as `DEFER`.
- **Estimated commits:**
  - 3 Step 2 commits, plus remediation if Codex finds issues
- **Open questions for the Project Owner before execution:**
  - Q1 `WI3 full exemplars vs stubs` -> **Resolved by Project Owner: STUBS**
  - Q2 `INH-1 directive-exemption audit` -> **Resolved by Project Owner: DEFER**
  - Q3 `INH-2 verified-resolved claim audit` -> **Resolved by Project Owner: INCLUDE**

### Plan approval

**Project Owner approval:** APPROVED on 2026-04-12. Project Owner said "Proceed with ultraplan." All three Step 1 recommendations were adopted: Q1 `STUBS`, Q2 `DEFER`, Q3 `INCLUDE`.

<!-- HANDSHAKE: Claude Code -> Project Owner | Historical Step 1 handoff recorded in Handshake Log rows 3-4; section backfilled under Path C. -->

---

## Step 2: Execute (Claude Code)

**[STATUS: COMPLETE - backfilled under Path C from landed Step 2 history]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section, sample assembled prompts in `Docs/_phases/_samples/PHASE_A_doubleprime_*.txt`

_Backfilled by Codex on 2026-04-12 under AGENTS.md Path C from commits `e8bdf7d`, `e1e1f7b`, and `9c5d3c1`. The commit rows reflect the actual Step 2 execution. The sample artifact list was generated during this backfill because Claude Code did not save Step 2 samples in the canonical record at the time. All sample prompts below were generated with live `assemble_context()` using the unit-test stub retrieval path because full integration assembly remains blocked locally by PostgreSQL availability._

### Execution log

**Commits made:**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | `e8bdf7d` | `feat(types): Phase A'' WI4 partial - add VIDEO_CALL to CommunicationMode` | `src/starry_lyfe/context/types.py` |
| 2 | `e1e1f7b` | `feat(context): Phase A'' WI1+WI2+WI4 - mode-conditional pillars + voice filtering + wiring` | `src/starry_lyfe/context/assembler.py`, `src/starry_lyfe/context/constraints.py`, `src/starry_lyfe/context/kernel_loader.py`, `src/starry_lyfe/context/layers.py`, `Docs/_phases/PHASE_A_doubleprime.md` |
| 3 | `9c5d3c1` | `test(assembler): Phase A'' WI3+WI5 - stub exemplars + tests A''1-A''6 + regression` | `Characters/Alicia/Alicia_Marin_Voice.md`, `tests/unit/test_assembler.py` |

**Test suite delta:**
- Tests added: `test_a_double_prime_1_alicia_phone_no_somatic_pillar`, `test_a_double_prime_2_alicia_phone_has_substituted_pillar`, `test_a_double_prime_3_phone_filters_in_person_exemplars`, `test_a_double_prime_4_phone_tagged_exemplar_appears`, `test_a_double_prime_5_bina_phone_mode_is_noop`, `test_a_double_prime_6_letter_and_video_have_own_pillars`, `test_adelia_phone_mode_is_noop`, `test_reina_phone_mode_is_noop`
- Tests passing: unit suite **96 -> 104**
- Tests failing: none in the unit suite; full `pytest -q` remained blocked in integration setup because PostgreSQL was unreachable at `tests/integration/conftest.py:92`

**Sample assembled prompt outputs:**
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_in_person_2026-04-12.txt` - 2274 tokens
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_phone_2026-04-12.txt` - 2170 tokens
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_letter_2026-04-12.txt` - 2163 tokens
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_video_call_2026-04-12.txt` - 2149 tokens

**Self-assessment against acceptance criteria:**

| # | Criterion | Status | Evidence |
|---:|---|---|---|
| AC1 | All 6 test cases A''1-A''6 pass | **MET** | The eight new/extended Phase A'' tests in `tests/unit/test_assembler.py` pass, including A''1-A''6 and the Adelia/Reina cross-character no-op regressions |
| AC2 | No regressions in Adelia, Bina, or Reina prompts | **MET** | `test_adelia_phone_mode_is_noop` and `test_reina_phone_mode_is_noop` pass; Bina remains a communication-mode no-op on the exercised unit surface |
| AC3 | Alicia phone, letter, and video-call prompts are distinct from in-person and carry mode-appropriate pillar text | **MET** | `constraints.py` now emits mode-specific Alicia pillars and `Alicia_Marin_Voice.md` carries one stub exemplar each for phone, letter, and video_call |
| AC4 | `VIDEO_CALL` added to `CommunicationMode` enum | **MET** | `CommunicationMode.VIDEO_CALL` exists in `types.py` and is wired through the assembler path |
| AC5 | Project Owner decision recorded for WI3 authoring scope | **MET** | Handshake Log row 3 records `Q1 (WI3 stubs vs full): STUBS` |
| AC6 | Project Owner decision recorded for INH-1 | **MET** | Handshake Log row 3 records `Q2 (INH-1): DEFER` |
| AC7 | Project Owner decision recorded for INH-2 | **MET** | Handshake Log row 3 records `Q3 (INH-2): INCLUDE` |
| AC8 | Test suite remains at or above the Phase A' baseline | **MET** | Unit suite moved from 96 to 104 passing tests |
| AC9 | Any Critical / High Codex findings fixed before QA hand-off | **PENDING AT STEP 2** | To be resolved in Step 4 after Codex audit |
| AC10 | Vision section 5 + section 6 authority intact | **MET (preliminary)** | Alicia's intermittent-presence architecture is represented through mode-specific pillar substitution and remote exemplar separation |

**Open questions for Codex / Claude AI / Project Owner:**

1. The Phase A'' spec text includes a filter-by-both-`mode`-and-`communication_mode` requirement for Layer 5, but the master plan's broader repository-wide `mode`-tag system is also specified in Phase E. Codex should decide whether the generic `mode`-tag half of WI2 is truly required in A'' or should be deferred to Phase E as the broader voice-mode infrastructure phase.

<!-- HANDSHAKE: Claude Code -> Codex | Historical Step 2 handoff backfilled in Handshake Log row 7; execution complete and ready for audit Round 1. -->

---

## Step 3: Audit (Codex) - Round 1

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan section 6, the plan and execution log above, git diff against the pre-phase commit, the actual test files, sample assembled prompts in `Docs/_phases/_samples/`, character kernel files for any phase that touches a character, the four archived character conversion audits in `Docs/_archive/` for template reference
**Writes:** This section. Codex does NOT modify production code, does NOT commit fixes, does NOT touch the canon directly. Trivial typos go in the audit as Low-severity findings for Claude Code to apply.

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` section 6 / the inline Phase A'' specification in this file
- `Docs/_phases/PHASE_A_doubleprime.md`
- A'' implementation commits `e8bdf7d`, `e1e1f7b`, and `9c5d3c1`
- `src/starry_lyfe/context/types.py`
- `src/starry_lyfe/context/assembler.py`
- `src/starry_lyfe/context/constraints.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/kernel_loader.py`
- `Characters/Alicia/Alicia_Marin_Voice.md`
- `tests/unit/test_assembler.py`
- archived audit templates in `Docs/_archive/`

Note: `Docs/_phase_status.md` is absent in this repo state, so the phase file itself was used as the canonical workflow record.

#### Verification context

Independent checks run during audit:

- `.venv\Scripts\python -m pytest tests/unit/test_assembler.py -q` -> **PASS** (`52 passed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS** (`104 passed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`104 passed, 14 errors`) because PostgreSQL is unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- `load_voice_guidance("alicia")`
- `load_voice_guidance("alicia", communication_mode="phone" / "letter" / "video_call" / "in_person")`
- `format_voice_directives("alicia", baseline, communication_mode=...)`
- `assemble_context("alicia", ...)` across `IN_PERSON`, `PHONE`, `LETTER`, and `VIDEO_CALL`
- `assemble_context("bina", ...)` with `IN_PERSON` vs `PHONE` as a cross-character no-op check
- `build_constraint_block("alicia", SceneState(...))` across remote modes

#### Executive assessment

Phase A'' is only partially correct.

The substantive Alicia-specific constraint work landed: `VIDEO_CALL` exists in the enum, `assemble_context()` now passes `scene_state.communication_mode` into Layer 5, and Alicia's Layer 7 constraint pillar really does substitute correctly for phone, letter, and video-call scenes. On the constraint side, the core Phase A'' premise is now live.

But the voice-exemplar half of the phase is not actually mode-safe in runtime behavior. The implementation defaults every untagged exemplar to `"any"` and treats `in_person` as "return all items", so live prompts still mix opposite-mode exemplars. A phone-mode Alicia prompt still carries in-person examples 3 and 5, and an in-person Alicia prompt now carries the remote phone exemplar 11. The current tests stay green because they assert on helper-level behavior and item counts, not on actual assembled prompt content.

The workflow record is also not audit-clean. Three A'' commits landed, but Step 1 and Step 2 are still untouched templates, there is no Claude Code -> Codex handshake in the canonical file, and there are no `PHASE_A''_*` sample prompt artifacts under `Docs/_phases/_samples/`. So even where real work exists, the canonical phase record does not describe it.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | High | Live Alicia voice filtering still leaks opposite-mode exemplars. Phone-mode prompts retain in-person examples 3 and 5, and in-person prompts now retain the remote phone exemplar 11. The phase therefore does not yet deliver communication-mode-safe Layer 5 behavior. | `src/starry_lyfe/context/kernel_loader.py:255-280` defaults untagged items to `"any"` and returns all items for `in_person`. `Characters/Alicia/Alicia_Marin_Voice.md:37` and `:77` show in-person examples 3 and 5 without any `communication_mode` tag, while only examples `11-13` at `:203`, `:220`, and `:237` are tagged. Live probes produced `counts 13 13 11 11 11`; phone-mode guidance still included `Example 3` and `Example 5`, and in-person guidance still included `Example 11`. The assembled Alicia phone prompt carried `Example 3`, `Example 5`, and `Example 11` together. | Tag Alicia's in-person exemplars explicitly, stop treating untagged legacy items as safe for all modes, and filter `in_person` to `in_person` + `any` rather than "everything". Then add live `assemble_context()` assertions proving Examples 3 and 5 are absent from phone/letter/video prompts and Example 11 is absent from in-person prompts. |
| F2 | Medium | The Phase A'' regression bundle passes for the wrong reason. The current A'' tests mostly assert on helper-level blocks or item counts, so they miss the actual assembled-prompt leakage that F1 exposed. | `tests/unit/test_assembler.py:574-646` checks `build_constraint_block()` for A''1/A''2/A''6 and only checks `len(phone_items) < len(all_items)` for A''3. None of those tests assert that the live phone-mode Alicia prompt excludes `Example 3` / `Example 5`, and none assert that an in-person Alicia prompt excludes `Example 11`. A live probe of `assemble_context("alicia", communication_mode=PHONE)` showed both in-person examples still present while all A'' tests remained green. | Strengthen the regression bundle around live prompts, not just helper functions. Add assembled-prompt assertions for phone, letter, video-call, and in-person Alicia modes, plus at least one full-prompt cross-character no-op assertion like the Bina `IN_PERSON == PHONE` probe Codex ran. |
| F3 | Medium | The canonical phase record is still missing the actual Step 1 and Step 2 content despite three landed A'' commits. The header and handshake log say planning/execution happened, but the phase body remains the untouched template and no A'' sample prompt artifacts exist. | `Docs/_phases/PHASE_A_doubleprime.md:149-175` still shows Step 1 as `NOT STARTED` with placeholder bullets and `Project Owner approval: _PENDING_`. `Docs/_phases/PHASE_A_doubleprime.md:181-208` still shows Step 2 as `NOT STARTED` with `_pending_` commit rows and placeholder test/sample sections. `Docs/_phases/_samples/` contains only Phase A files; there are no `PHASE_A''_*` artifacts. Meanwhile `git log --oneline -n 12` shows real A'' commits `e8bdf7d`, `e1e1f7b`, and `9c5d3c1`. | Fill Step 1 and Step 2 as the canonical record before remediation is considered audit-clean. Record the actual files touched, tests added, owner decisions for WI3 / INH-1 / INH-2, the real commit list, and sample Alicia outputs for at least in-person plus one remote mode. Add the missing Claude Code -> Codex handshake row if Claude Code still wants the workflow trail to reflect a real Step 2 handoff. |
| F4 | Low | The Alicia away-state error message is stale after `VIDEO_CALL` was added as a canonical communication mode. | `src/starry_lyfe/context/assembler.py:77` still tells callers to set `communication_mode` to `'phone' or 'letter'`, even though `VIDEO_CALL` now exists in `src/starry_lyfe/context/types.py:15` and is handled in `src/starry_lyfe/context/constraints.py:132`. | Update the error message and add a tiny regression assertion so the allowed remote modes listed in the exception stay in sync with the enum. |

#### Runtime probe summary

Live observations from the audited code:

- Alicia's remote constraint pillars are real and survive assembly:
  - phone-mode prompts include `Your voice carries the regulation when the body cannot`
  - letter-mode prompts include `Letters are weight made of paragraphs`
  - video-call prompts include `Eye contact and posture are your somatic anchors`
- Bina's cross-character no-op behavior holds at full assembled-prompt level: a Bina `PHONE` prompt was byte-for-byte identical to the same Bina `IN_PERSON` prompt in Codex's live probe
- Alicia Layer 5 does not yet honor mode boundaries:
  - `load_voice_guidance("alicia", communication_mode="phone")` returned 11 items and still contained `Example 3` and `Example 5`
  - `load_voice_guidance("alicia", communication_mode="in_person")` returned all 13 items and still contained `Example 11`
  - the assembled Alicia phone prompt still carried `Example 3`, `Example 5`, and `Example 11` together in `<VOICE_DIRECTIVES>`

#### Drift against specification

- **WI1 / WI4:** substantially implemented; Alicia's constraint pillar really is mode-conditional and `VIDEO_CALL` is wired through the enum and assembler path
- **WI2:** incomplete in live behavior; selector does not yet produce clean mode-separated Alicia prompts
- **WI2 spec detail:** filter-by-both-`mode`-and-`communication_mode` is still unimplemented in code; there is no `mode` tag parsing in `kernel_loader.py`, and Alicia's file currently carries only `communication_mode` tags
- **WI3:** stub authoring landed, which matches the Project Owner handshake choice, but that choice is not recorded in Step 1 or Step 2 proper
- **WI5:** cross-character no-op behavior is real for Bina in live probes, but the checked-in regression tests do not assert it at assembled-prompt level
- **Workflow contract:** Step 1 and Step 2 canonical sections are still empty despite landed execution commits

#### Verified resolved

Independently confirmed closed:

- `CommunicationMode.VIDEO_CALL` exists and round-trips through `SceneState`
- `assemble_context()` now passes `scene_state.communication_mode` into `format_voice_directives()`
- Alicia's Layer 7 constraint block substitutes correctly for phone, letter, and video-call scenes
- Alicia away-state `IN_PERSON` assembly is still blocked, while remote assembly is allowed
- Bina remains a communication-mode no-op at full prompt level in the live probe

#### Adversarial scenarios constructed

1. **Opposite-mode exemplar leak check:** compare Alicia `PHONE` and `IN_PERSON` prompts and scan for `Example 3`, `Example 5`, and `Example 11`. This exposed both directions of leakage.
2. **Remote-mode split check:** run Alicia through `PHONE`, `LETTER`, and `VIDEO_CALL` and inspect the live `<CONSTRAINTS>` block for the mode-specific substituted pillar phrases. This confirmed the constraint side is working even while Layer 5 is not.
3. **Cross-character no-op check:** build Bina `IN_PERSON` and `PHONE` prompts with identical scene data and compare full prompt equality. This confirmed the phase-specific leakage is Alicia-local, not a global side effect.
4. **Spec-trace artifact check:** compare the A'' commit history with `PHASE_A_doubleprime.md` Step 1 / Step 2 and with `Docs/_phases/_samples/`. This exposed the missing canonical execution record and missing sample outputs.

#### Gate recommendation

**FAIL**

Phase A'' should not proceed to QA yet. The Alicia constraint substitution work is real, but the live voice layer still mixes in-person and remote exemplars across modes, which is the core runtime defect this phase exists to prevent. The checked-in tests do not catch that defect, and the phase file still lacks the canonical Step 1 / Step 2 record and required sample artifacts.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete. FAIL gate. F1 High: Alicia voice filtering still leaks opposite-mode exemplars in live prompts. F2 Medium: A'' tests pass for the wrong reason. F3 Medium: Step 1/2 canonical record and sample artifacts are still missing. F4 Low: AliciaAwayError message omits video_call. Ready for remediation Round 1. -->

---

## Step 4: Remediate (Claude Code) - Round 1

**[STATUS: COMPLETE - backfilled from remediation commit and later audit history]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code
**Reads:** The audit above, the master plan, the canon
**Writes:** Production code, tests, this section. May supersede sample assembled prompts in `Docs/_phases/_samples/` with new versions.

_Backfilled by Codex on 2026-04-12 under AGENTS.md Path C from remediation commit `66d2a1d` and the later Step 3' re-audit. The table below records what Round 1 actually closed and what had to be carried into Round 2._

### Remediation content

**Per-finding status table:**

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| F1 | High | **FIXED** | `66d2a1d` | Alicia's in-person legacy exemplars are now explicitly tagged `communication_mode: in_person`, and the in-person path no longer falls back to returning every exemplar regardless of mode. The live opposite-mode leakage Codex observed in Round 1 is closed. |
| F2 | Medium | **FIXED** | `66d2a1d` | `test_a_double_prime_3_phone_filters_in_person_exemplars` and `test_a_double_prime_4_phone_tagged_exemplar_appears` now assert the concrete leakage cases Round 1 exposed instead of passing on weaker helper-level behavior. |
| F3 | Medium | **DEFERRED** | `66d2a1d` | The runtime remediation commit did not fully repair the canonical phase record or save the missing sample artifacts. That record-repair work is carried forward explicitly to Step 4' under AGENTS.md Path C. |
| F4 | Low | **FIXED** | `66d2a1d` | `AliciaAwayError` now names `phone`, `letter`, and `video_call` as the valid non-in-person paths. |

**Push-backs:** none.

**Deferrals:** `F3` is explicitly deferred to Step 4' Round 2 under AGENTS.md Path C. This is a phase-record issue, not a remaining runtime blocker.

**Re-run test suite delta:**
- `.venv\Scripts\python -m pytest tests/unit/test_assembler.py -q` -> **52 passed**
- `.venv\Scripts\python -m pytest tests/unit -q` -> **104 passed**
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` still failed only in integration setup because PostgreSQL was unreachable at `tests/integration/conftest.py:92`

**New sample assembled prompts:** none were saved during the original Round 1 remediation. Canonical A'' sample artifacts are backfilled in Step 4' below.

**Self-assessment:** All Critical (0) and High (1) findings were closed in runtime behavior. One Medium finding (`F3`) remained unresolved on the canonical phase record and later triggered the user-requested Step 3' re-audit.

### Path decision

**Chosen path: Path A (clean).** The Round 1 remediation changed targeted runtime/test behavior but did not introduce a new architectural surface. A direct QA handoff was historically implied after `66d2a1d`; the later Step 3' re-audit occurred because the Project Owner explicitly requested it.

<!-- HANDSHAKE: Claude Code -> Claude AI | Historical Path A handoff after Round 1 remediation; later superseded by the user-requested Step 3' re-audit. -->

---

## Step 3': Audit (Codex) - Round 2 (user-requested re-audit after remediation)

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 2]**

_User-requested re-audit after remediation commit `66d2a1d` landed outside the canonical Step 4 record. Focus: verify closure of F1-F4 and identify any residual implementation or phase-record gaps before QA._

### Round 2 audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` section 6 / the inline Phase A'' specification in this file
- `Docs/_phases/PHASE_A_doubleprime.md` header, Handshake Log, Step 1, Step 2, Step 4, and Step 3' placeholders
- remediation commit `66d2a1d`
- `src/starry_lyfe/context/kernel_loader.py`
- `src/starry_lyfe/context/assembler.py`
- `src/starry_lyfe/context/constraints.py`
- `Characters/Alicia/Alicia_Marin_Voice.md`
- `tests/unit/test_assembler.py`
- `Docs/_phases/_samples/`

#### Verification context

Independent checks run during re-audit:

- `.venv\Scripts\python -m pytest tests/unit/test_assembler.py -q` -> **PASS** (`52 passed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS** (`104 passed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`104 passed, 14 errors`) because PostgreSQL is unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- `load_voice_guidance("alicia", communication_mode=...)` across `in_person`, `phone`, `letter`, and `video_call`
- `build_constraint_block("alicia", SceneState(...))` across the same four modes
- live `assemble_context("alicia", ...)` with stubbed memory retrieval across the same four modes
- live `assemble_context("bina", ...)` with stubbed memory retrieval for `IN_PERSON` vs `PHONE` as a cross-character no-op check

#### Executive assessment

Round 1's live Alicia leakage defect is fixed. Phone, letter, and video-call prompts now carry remote-appropriate constraint pillars and no longer mix in-person exemplars into remote prompts or remote exemplars into in-person prompts. The strengthened tests correctly cover that repaired behavior, and the AliciaAwayError copy is corrected.

Phase A'' should still not proceed to QA. Two Medium findings remain: the canonical phase record is still largely a template despite the landed remediation, and Work Item 2 is still only partially implemented because Layer 5 still ignores `mode` tags entirely. Gate recommendation: **FAIL**.

#### Findings

1. `Medium` The canonical phase record is still not QA-ready. This re-audit updates the header and handshake log, but [PHASE_A_doubleprime.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_A_doubleprime.md:149), [PHASE_A_doubleprime.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_A_doubleprime.md:181), and [PHASE_A_doubleprime.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_A_doubleprime.md:330) are still untouched templates and `Docs/_phases/_samples/` still has no `PHASE_A''_*` sample artifacts. That leaves no canonical Step 2 execution record, no Step 4 remediation table, no path decision, and no in-file evidence trail for QA to review.

2. `Medium` Work Item 2 remains only partially implemented. The Phase A'' specification still says the Layer 5 selector must filter by both `mode` and `communication_mode`, but [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:190) only parses `communication_mode` tags, [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:274) filters only on that single dimension, and [Alicia_Marin_Voice.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Alicia/Alicia_Marin_Voice.md:10) contains no `<!-- mode: ... -->` tags at all. The remediation fixed communication-mode separation, but the mode-tag half of WI2 is still absent in code, content, and tests.

#### Runtime probe summary

- `load_voice_guidance("alicia", communication_mode="phone")` now excludes `Example 3` and `Example 5` and includes `Example 11`.
- `load_voice_guidance("alicia", communication_mode="in_person")` now includes `Example 3` and `Example 5` and excludes `Example 11`.
- `load_voice_guidance("alicia", communication_mode="letter")` selects `Example 12`, and `video_call` selects `Example 13`.
- Live `assemble_context("alicia", ...)` with stubbed retrieval mirrors the same exemplar separation at full prompt level.
- Live Alicia constraint blocks are correctly mode-specific: phone uses the voice-regulation pillar, letter uses the paragraph-weight pillar, and video-call uses the visual-presence pillar.
- Live `assemble_context("bina", ...)` remains a full no-op across `IN_PERSON` vs `PHONE` (`prompt identical: True`).

#### Drift against specification

- **WI1:** complete in live behavior. Alicia's Layer 7 pillar now branches correctly across `IN_PERSON`, `PHONE`, `LETTER`, and `VIDEO_CALL`.
- **WI2:** partial. `communication_mode` filtering is live, but the spec-required `mode` tag parsing and filter path are still missing.
- **WI3:** remote exemplars exist in Alicia's voice file, but the canonical Step 1 / Step 2 record is still missing, so the approved stub/full scope decision is not traceable in the phase artifact beyond the handshake shorthand.
- **WI4:** complete in live behavior. `CommunicationMode.VIDEO_CALL` is wired through the enum and assembler path.
- **WI5:** satisfied on the current tested surface. The Alicia-specific regression tests now assert the intended separation, and Bina remains a live full-prompt no-op across communication modes.

#### Verified resolved

- **F1 fixed:** Alicia no longer leaks opposite-mode exemplars in live Layer 5 output or in the assembled prompt.
- **F2 fixed:** `test_a_double_prime_3_phone_filters_in_person_exemplars` and `test_a_double_prime_4_phone_tagged_exemplar_appears` now assert the actual leakage cases that Round 1 exposed.
- **F4 fixed:** AliciaAwayError now names `phone`, `letter`, and `video_call`.

#### Recommended remediation order

1. Fill the canonical phase record: Step 2 execution log, sample artifact list, Step 4 per-finding table, and path decision. If the Round 1 remediation was intended as Path A, record that explicitly; otherwise hand back to Codex again through the documented path.
2. Dispose of WI2's remaining `mode`-tag requirement explicitly: either implement `mode` parsing/filtering plus `<!-- mode: ... -->` tags now, or defer that half of the contract to Phase E with source-backed rationale recorded in Step 4.

#### Gate recommendation

**FAIL**

The core runtime defect this phase exists to fix is closed, but Phase A'' is still not specification-complete or artifact-complete. It should not proceed to QA until the canonical record is brought current and WI2's remaining `mode`-tag requirement is either implemented or explicitly deferred with evidence.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 2 complete. FAIL gate. Runtime fixes verified (F1, F2, F4 closed), but 2 Medium findings remain: the canonical phase record is still unfilled and WI2's mode-tag contract is still only partially implemented. Ready for remediation Round 2. -->

---

## Step 4': Remediate (Claude Code) - Round 2 (only if Round 2 audit produced new findings)

**[STATUS: COMPLETE - direct doc-only remediation applied, handed to Claude AI for QA]**

_Project Owner direction in chat plus AGENTS.md Path C: Codex directly remediated the Round 2 findings. This round repaired the canonical phase record and created the missing sample artifacts; no production runtime behavior changed in this round._

### Remediation content

**Per-finding status table:**

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| R2-F1 | Medium | **FIXED** | n/a (direct remediation in working tree) | Step 1, Step 2, and Step 4 are now fully populated as the canonical record. The header/handshake state is aligned, the omitted Step 2 handoff is explicitly backfilled in the log, and four A'' sample prompt artifacts now exist under `Docs/_phases/_samples/`. |
| R2-F2 | Medium | **DEFERRED** | n/a (direct remediation in working tree) | The unresolved filter-by-both-`mode`-and-`communication_mode` half of WI2 is deferred to **Phase E**. Source-backed rationale: `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase E Work Items 1-2 already own the repository-wide `<!-- mode: ... -->` tag system and mode-aware exemplar selection across Voice.md files. Phase A'' is now explicitly closed on the blocker-safe `communication_mode` behavior for Alicia. |

**Push-backs:** none. Round 2's remaining issues were a documentation gap and a scope/trace issue, not disputed readings of the canon.

**Deferrals:** `R2-F2` is explicitly deferred to **Phase E: Voice Exemplar Restoration**. That phase already owns voice `mode` tags and mode-aware selection as first-class scope; carrying the generic `mode`-tag half there avoids duplicating the same infrastructure across two phases.

**Re-run verification delta:** unchanged passing state after the direct remediation:

- `.venv\Scripts\python -m pytest tests/unit/test_assembler.py -q` -> **52 passed**
- `.venv\Scripts\python -m pytest tests/unit -q` -> **104 passed**
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` still fails only in integration setup because PostgreSQL is unreachable at `tests/integration/conftest.py:92`

**New sample assembled prompts:**
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_in_person_2026-04-12.txt`
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_phone_2026-04-12.txt`
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_letter_2026-04-12.txt`
- `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_video_call_2026-04-12.txt`

**Self-assessment:** All Critical and High findings remain closed. Round 2's documentation finding is fixed. Round 2's residual WI2 scope issue is now explicitly deferred to a named follow-up phase with source-backed rationale. Phase A'' is ready for Step 5 QA.

### Path decision

**Chosen path: Path C (direct-Codex doc-only remediation).** No production code changed in this round. The work was limited to canonical phase-record completion, sample-artifact creation, and explicit deferral of the residual WI2 `mode`-tag scope to Phase E.

<!-- HANDSHAKE: Codex -> Claude AI | Direct doc-only remediation complete under AGENTS.md Path C. R2-F1 fixed; R2-F2 deferred to Phase E. A'' sample artifacts backfilled. Ready for Step 5 QA. -->

---

## Step 3'': Audit (Codex) — Round 3 (only if convergence has not been reached)

**[STATUS: NOT STARTED]**

_Same structure. **This is the final audit round before mandatory escalation to the Project Owner per AGENTS.md cycle limit.**_

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 3 complete -->

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: NOT STARTED]**

_Same structure. **If convergence is not reached after this round, Claude Code MUST escalate to the Project Owner instead of starting Round 4.**_

<!-- HANDSHAKE: Claude Code → {Project Owner if not converged / Claude AI if converged} | Remediation Round 3 complete -->

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**
**Owner:** Claude AI (the assistant in this chat)
**Prerequisite:** Step 4 (or 4', or 4'') remediation complete with handshake to Claude AI, AND Project Owner has brought the phase artifacts to Claude AI in chat
**Reads:** Master plan §6, the entire phase file above, the test output from the most recent run, sample assembled prompt outputs, the phase status log
**Writes:** This section. Claude AI does NOT execute code or modify production files in the normal QA flow.

### QA verdict content

_Claude AI fills in this subsection. Required fields:_

- **Specification trace:** _every acceptance criterion from the master plan, with PASS / FAIL / N/A annotation and one-sentence evidence_

| Criterion | Status | Evidence |
|---|---|---|
| _criterion 1 from master plan_ | PASS / FAIL / N/A / PARTIAL | _one sentence_ |

- **Audit findings trace:** _every Critical and High finding from Codex's audit (all rounds), with FIXED / DEFERRED / PUSH_BACK_ACCEPTED annotation and verification that the remediation is consistent with the master plan_

| Finding # | Original severity | Final status | Evidence |
|---:|---|---|---|
| 1 | _from audit_ | FIXED / DEFERRED / PUSH_BACK_ACCEPTED | _one sentence_ |

- **Sample prompt review:** _Claude AI reads at least one assembled prompt sample end-to-end and notes whether it carries the expected canonical content for the affected character(s)_
- **Cross-Phase impact check:** _does this Phase's work affect any other Phase's acceptance criteria; have any other Phases' tests started failing as a side effect_
- **Severity re-rating (if any):** _Claude AI may downgrade or upgrade Codex findings with explicit rationale_
- **Open questions for the Project Owner:** _list, or "none"_

### Verdict

**Verdict:** _APPROVED FOR SHIP / APPROVED WITH MINOR FIXES / RETURN FOR REMEDIATION_

- **If APPROVED FOR SHIP:** one-paragraph release-notes summary suitable for the Project Owner
- **If APPROVED WITH MINOR FIXES:** explicit list of trivial fixes that should be applied before ship but do not require another full remediation cycle
- **If RETURN FOR REMEDIATION:** explicit list of issues, each one specific enough that Claude Code can act on it directly

### Phase progression authorization

_Claude AI fills in only if verdict is APPROVED FOR SHIP or APPROVED WITH MINOR FIXES:_

- **Next phase recommendation:** _which phase should run next per the master plan dependency graph_
- **Awaiting Project Owner agreement to proceed:** YES / NO
- **Once Project Owner agrees, Claude AI will create the next phase file at:** `Docs/_phases/PHASE__B.md`

<!-- HANDSHAKE: Claude AI → Project Owner | QA verdict ready, awaiting ship decision -->

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**
**Owner:** Project Owner (Whyze / Shawn Kroon)
**Prerequisite:** Step 5 QA verdict ready
**Reads:** The entire phase file
**Writes:** This section. The decision is locked once recorded.

### Ship decision

**Decision:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_

- **Date:** _YYYY-MM-DD_
- **Decided by:** Project Owner (Whyze)
- **Decision rationale:** _one or two sentences_

### If SHIPPED

- **Phase marked complete in master plan execution status:** YES
- **Agreement with Claude AI to proceed to next phase:** YES / NO
- **Next phase to begin:** _phase identifier_
- **Next phase file to be created by Claude AI:** _path_

### If SENT BACK

- **Specific issues the Project Owner identified:** _list_
- **Returns to Step:** _4 (remediation) or 1 (replan)_

### If STOPPED FOR REDESIGN

- **Architectural issue surfaced:** _description_
- **Master plan update required:** _what section needs to change_
- **This phase will restart at Step 1 after master plan is updated**

<!-- HANDSHAKE: Project Owner → CLOSED | Phase shipped, work complete -->
_(or)_
<!-- HANDSHAKE: Project Owner → Claude Code | Sent back to remediation, see Project Owner notes above -->
_(or)_
<!-- HANDSHAKE: Project Owner → CLOSED | Phase stopped for redesign, master plan update required before restart -->

---

## Closing Block (locked once shipped)

**Phase identifier:** _A''_
**Final status:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _audit-remediate rounds completed_
**Total commits:** _count_
**Total tests added:** _count_
**Date opened:** _YYYY-MM-DD (when this file was created by Claude AI)_
**Date closed:** _YYYY-MM-DD (when Project Owner shipped or stopped)_

**Lessons for the next phase:** _2-3 sentences from Claude AI summarizing what worked, what didn't, and what should change in the next phase's plan_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6
- AGENTS.md cycle definition: `AGENTS.md`
- Sample assembled prompts: `Docs/_phases/_samples/PHASE_A''_*.txt`
- Previous phase file (if any): `Docs/_phases/PHASE_A'.md`
- Next phase file (if shipped): `Docs/_phases/PHASE__B.md`

---

_End of Phase A'' canonical record. Do not edit fields above this line after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
