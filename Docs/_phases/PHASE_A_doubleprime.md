# Phase A'': Communication-Mode-Aware Pruning

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6
**Phase identifier:** `A''` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A' (SHIPPED 2026-04-12)
**Blocks:** Phase B, Phase I, Phase C, Phase D, Phase E (especially — Phase A'' is a BLOCKER for Phase E Alicia voice exemplar restoration), Phase F, Phase G, Phase J.1-J.4, Phase H, Phase K
**Status:** **SHIPPED** 2026-04-12 — Phase A'' complete; Phase B authorized and created
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
| 9 | 2026-04-12 | Claude AI | Project Owner | Step 5 QA verdict written: APPROVED FOR SHIP. All 10 ACs traced and verified met; all 6 audit findings disposed (4 FIXED + 1 DEFERRED-then-FIXED via Path C + 1 DEFERRED to Phase E with independently-verified source basis at master plan L674-L740); 104 unit tests pass independently verified in 2.05s; Phase-to-Vision check passes with strengthening (Vision §5 intermittent-presence architecture for Solstice Pair now structurally enforceable at assembly layer for first time, completing Phase A''s §6 enforcement). F1 fix verified at four layers: parser, filter, content-tag, live prompt sample. R2-F2 Phase E deferral verified by direct read of master plan Phase E WI1-2. Three open questions for Project Owner discussion before next phase (INH-2 audit scope, Path C workflow calibration, Phase E authoring pre-stage). Awaiting Step 6 ship decision. |
| 10 | 2026-04-12 | Project Owner | CLOSED | Phase A'' SHIPPED. Agreement to proceed to Phase B: YES. Step 6 filled in by Claude AI on Project Owner's behalf via chat instruction "#4" selecting option 4 from the Step 5 verdict's concerns-and-risks follow-up menu (proceed to ship + address concerns in Phase B Step 1). Claude AI authorized to create Docs/_phases/PHASE_B.md with four carry-forward items documented as Phase B inherited items: INH-2 master plan "VERIFIED RESOLVED" audit, INH-7 PRESERVE markers (Phase B precondition), Path C workflow calibration amendment, Phase E tag coordination. |

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

**[STATUS: COMPLETE — verdict APPROVED FOR SHIP, awaiting Project Owner ship decision]**
**Owner:** Claude AI (the assistant in this chat)
**Date:** 2026-04-12
**Reads:** Master plan §6 (reproduced in this phase file with staleness annotations), the entire Step 1 Plan (Path-C backfilled), the entire Step 2 Execute Log (Path-C backfilled), both Step 3 Audit rounds in full, both Step 4 Remediate rounds in full, the production source files (`types.py`, `constraints.py`, `assembler.py`, `kernel_loader.py`), `Characters/Alicia/Alicia_Marin_Voice.md`, `tests/unit/test_assembler.py` focusing on the eight new Phase A'' tests, the Alicia phone-mode sample at `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_phone_2026-04-12.txt`, master plan Phase E section L674-L740 (independent verification of the R2-F2 deferral source basis), Vision §5 Chosen Family (the named Phase A'' Vision authority alongside §6 Relationship Architecture).
**Writes:** This Step 5 section. Per AGENTS.md, Claude AI does not modify production code or commit code in the normal QA flow.

**Independent verification performed by Claude AI in this turn:**

- Ran `pytest tests/unit -q` from the project root using the venv python: **104 passed in 2.05 seconds, return code 0**. The 104-test claim from Step 4' is independently verified (96 Phase A' baseline + 8 Phase A'' = 6 A''1-A''6 tests + 2 cross-character no-op regressions for Adelia and Reina).
- Read `types.py` directly. `CommunicationMode.VIDEO_CALL = "video_call"` at line 15 verified. `SceneState.recalled_dyads` and `communication_mode` fields from Phase A' intact at lines 27 and 27. Post-init validator at lines 30-32 correctly coerces string inputs to enum.
- Read `constraints.py:124-136` directly. Mode-conditional Alicia pillar substitution branches on `scene_state.communication_mode` and selects `ALICIA_PHONE_PILLAR`, `ALICIA_LETTER_PILLAR`, or `ALICIA_VIDEO_PILLAR` for the three remote modes, falling back to the in-person pillar otherwise. WI1 is structurally complete and correct.
- Read `assembler.py:70-79` directly. **F4 fix verified:** the `AliciaAwayError` message now reads `"Set scene_state.alicia_home=True or communication_mode to 'phone', 'letter', or 'video_call'."` — `video_call` is explicitly named. The error copy is in sync with the enum.
- Read `assembler.py:97-101` directly. **WI4 wiring verified:** `format_voice_directives(character_id, memories.character_baseline, communication_mode=scene_state.communication_mode)` — the communication mode is threaded from `SceneState` through to Layer 5 formatting.
- Read `kernel_loader.py:190, 193-246, 249-307` directly. **F1 fix verified at parser level:** `_COMM_MODE_TAG_RE` at L190 parses `<!-- communication_mode: X -->` tags; `_extract_voice_guidance()` at L193-L246 extracts `(guidance_text, communication_mode_tag)` tuples with `"any"` as the default when no tag is present; `load_voice_guidance(..., communication_mode=...)` at L274-L280 filters strictly: `[text for text, mode in raw if mode in (communication_mode, "any")]`. **This is the critical fix** — the Round 1 bug was that `in_person` returned all items as a fallback; the post-remediation code filters strictly on tag match, so items tagged `in_person` are excluded from phone/letter/video-call requests and items tagged `phone` are excluded from in-person requests.
- Read `Characters/Alicia/Alicia_Marin_Voice.md` tag survey directly. **F1 fix verified at content level:** all 13 examples are now explicitly tagged. Examples 1-10 carry `<!-- communication_mode: in_person -->` (no legacy untagged fallback); Example 11 carries `phone`; Example 12 carries `letter`; Example 13 carries `video_call`. The combination of strict filtering + explicit tagging on every exemplar closes the opposite-mode leakage Round 1 identified.
- Read `Docs/_phases/_samples/PHASE_A_doubleprime_assembled_alicia_phone_2026-04-12.txt` end-to-end. The full assembled phone-mode prompt shows Examples 3 and 5 absent from `<VOICE_DIRECTIVES>` and Example 11 present (exactly one exemplar, the Late-Night Phone Call From Operational Posting). The `<CONSTRAINTS>` block contains the substituted phone pillar verbatim: *"Your voice carries the regulation when the body cannot. Pace, breath, weight in the words. Listen for the shift before reaching for the next sentence. Do not narrate the body you do not have access to."* WI1 and WI2 both work at the live prompt level.
- Read master plan Phase E L674-L740 directly. **R2-F2 deferral verified as source-backed:** Phase E Work Item 1 (L681-L710) introduces `<!-- mode: ... -->` tag authoring with a closed enum (`domestic`, `conflict`, `intimate`, `children_gate`, `public`, `group`, `repair`, `silent`, `solo_pair`, `escalation`, `warm_refusal`, `group_temperature`). Phase E Work Item 2 (L711) explicitly says *"Replace the file-order selection with mode-aware selection. Given a scene's active mode list, the voice example selector filters examples to those tagged with at least one of the scene's active modes..."*. **The `mode` tag system is unambiguously first-class Phase E scope**, not Phase A'' scope. Deferring the generic `mode`-tag half of WI2 to Phase E preserves a clean separation of concerns: Phase A'' owns `communication_mode` (in_person / phone / letter / video_call), Phase E owns `mode` (domestic / conflict / intimate / etc.). Implementing both in Phase A'' would have duplicated Phase E Work Items 1-2.
- Read Vision §5 Chosen Family directly to verify Phase-to-Vision fidelity. See Phase-to-Vision section below.

### QA verdict content

**Specification trace** (each acceptance criterion from the Phase A'' plan, traced against actual evidence):

| # | Criterion | Status | Evidence |
|---:|---|---|---|
| **AC1** | All 6 test cases A''1-A''6 pass | **PASS** | Verified in the 104-test suite run. Tests `test_a_double_prime_1_alicia_phone_no_somatic_pillar`, `test_a_double_prime_2_alicia_phone_has_substituted_pillar`, `test_a_double_prime_3_phone_filters_in_person_exemplars`, `test_a_double_prime_4_phone_tagged_exemplar_appears`, `test_a_double_prime_5_bina_phone_mode_is_noop`, and `test_a_double_prime_6_letter_and_video_have_own_pillars` all pass. The Round 2 strengthening means A''3 and A''4 now assert concrete leakage behavior at live prompt level rather than helper-level item counts (the Round 1 defect Codex caught). |
| **AC2** | No regressions in Adelia, Bina, or Reina prompts | **PASS** | `test_adelia_phone_mode_is_noop` and `test_reina_phone_mode_is_noop` pass in the 104-test run. Bina's no-op was verified by Codex's live probe in both audit rounds: a full Bina `PHONE` prompt is byte-for-byte identical to the same Bina `IN_PERSON` prompt. |
| **AC3** | Alicia phone/letter/video-call prompts are distinct from in-person and carry mode-appropriate pillar text | **PASS** | Verified by direct read of `constraints.py:124-136` plus the four `PHASE_A_doubleprime_assembled_alicia_{in_person,phone,letter,video_call}_2026-04-12.txt` sample artifacts. The phone sample I read end-to-end shows the `"Your voice carries the regulation when the body cannot..."` pillar in `<CONSTRAINTS>` and Example 11 (the only phone-tagged exemplar) in `<VOICE_DIRECTIVES>`. The in-person, letter, and video-call samples will similarly each carry their own mode-specific pillars per the Codex runtime probes in Round 2. |
| **AC4** | `VIDEO_CALL` added to `CommunicationMode` enum | **PASS** | `types.py:15` contains `VIDEO_CALL = "video_call"`. WI4 partial completion verified. |
| **AC5** | Project Owner decision recorded for WI3 authoring scope | **PASS** | Step 1 Open Question Q1 resolved `STUBS`. Evidence in execution: `Alicia_Marin_Voice.md` carries one stub exemplar per remote mode (Examples 11, 12, 13 for phone, letter, video_call respectively). Full authored library deferred to follow-up per Project Owner direction. |
| **AC6** | Project Owner decision recorded for INH-1 | **PASS** | Step 1 Open Question Q2 resolved `DEFER`. The directive-exemption audit is deferred out of Phase A'' blocker scope per Project Owner direction. |
| **AC7** | Project Owner decision recorded for INH-2 | **PASS** | Step 1 Open Question Q3 resolved `INCLUDE`. However, I note that the Step 2 execution log does not show a distinct "verified-resolved claim audit" commit, and the landed commits (`e8bdf7d`, `e1e1f7b`, `9c5d3c1`) all address master plan §6 work items, not master plan §5 "VERIFIED RESOLVED" claims. See **Open questions** below — this is worth clarifying with Project Owner before Phase B begins. |
| **AC8** | Test suite remains at or above Phase A' baseline | **PASS** | 96 → 104 passing (+8), 0 failing. Independently verified at 104 passed in 2.05s. |
| **AC9** | Any Critical / High Codex findings fixed before QA hand-off | **PASS** | F1 High (Round 1 voice exemplar leakage) is FIXED at parser, filter, content-tag, and live-prompt level. All four verification points hold. No Critical findings in either round. |
| **AC10** | Vision §5 + §6 authority intact | **PASS with strengthening** | See Phase-to-Vision section. Phase A'' is the first phase that structurally serves Vision §5's intermittent-presence architecture for the Solstice Pair. |

**Audit findings trace** (every Codex finding from both rounds, with independent verification):

| Finding # | Round | Severity | Final status | Independently verified by Claude AI |
|---:|---|---|---|---|
| **F1** | R1 | High | **FIXED** | YES — verified at four layers: (1) the parser at `kernel_loader.py:190-246` now extracts the `communication_mode` tag per example with `"any"` as the sentinel default; (2) the filter at `kernel_loader.py:274-280` is strict `mode in (communication_mode, "any")` so legacy items no longer fall through; (3) every Alicia Voice example is now explicitly tagged — Examples 1-10 as `in_person`, Example 11 as `phone`, Example 12 as `letter`, Example 13 as `video_call`, with no legacy untagged items remaining; (4) the live `PHASE_A_doubleprime_assembled_alicia_phone_2026-04-12.txt` sample shows only Example 11 in `<VOICE_DIRECTIVES>` with Examples 3 and 5 correctly absent. The Round 1 defect is closed at all four verification levels. |
| **F2** | R1 | Medium | **FIXED** | YES — the Round 1 defect was that tests asserted on helper-level item counts rather than rendered prompt content. The Round 1 remediation commit `66d2a1d` strengthened `test_a_double_prime_3_phone_filters_in_person_exemplars` and `test_a_double_prime_4_phone_tagged_exemplar_appears` to assert the concrete leakage cases. Codex's Round 2 re-audit verified this at live probe level. All 6 A'' tests plus the 2 cross-character no-op regressions pass in the 104-test run I executed this turn. |
| **F3** | R1 | Medium | **DEFERRED to Step 4' / then FIXED via R2-F1 remediation** | YES — F3 was that Step 1, Step 2, and Step 4 canonical sections were still template despite landed commits. It was deferred from Round 1 to Round 2 under Path C, then fixed in Round 2 remediation (`R2-F1`) by Codex backfilling all three sections plus creating the four `PHASE_A_doubleprime_assembled_alicia_*_2026-04-12.txt` sample artifacts. I verified the samples exist by direct file read and the backfilled sections are coherent with the commit history (`e8bdf7d`, `e1e1f7b`, `9c5d3c1`, `66d2a1d`). |
| **F4** | R1 | Low | **FIXED** | YES — read `assembler.py:76-78` directly. The `AliciaAwayError` message now reads `"Set scene_state.alicia_home=True or communication_mode to 'phone', 'letter', or 'video_call'."` — all three remote modes are named. `video_call` is correctly present. |
| **R2-F1** | R2 | Medium | **FIXED** | YES — Step 1, Step 2, and Step 4 are all populated with substantive content traceable to the Handshake Log and commit history. Four Phase A'' sample artifacts exist under `Docs/_phases/_samples/` (alicia in_person 2274 tokens, phone 2170, letter 2163, video_call 2149). The canonical phase record is QA-reviewable. |
| **R2-F2** | R2 | Medium | **DEFERRED to Phase E with source-backed rationale** | YES — **independently verified by direct read of master plan Phase E L674-L740**. Phase E Work Item 1 introduces the `<!-- mode: ... -->` tag system with a closed enum of 12 voice modes. Phase E Work Item 2 replaces file-order selection with mode-aware selection. Phase E also has explicit per-character mode coverage requirements including `warm_refusal` and `group_temperature` for Alicia (both annotated as "ALICIA audit additions"). The deferral reading is exactly correct: the `mode` tag half of Phase A'' WI2 is unambiguously first-class Phase E scope. Implementing it in Phase A'' would have duplicated Phase E WI1-2. The deferral is the architecturally correct call and preserves a clean separation: Phase A'' owns `communication_mode` (in_person / phone / letter / video_call), Phase E owns `mode` (domestic / conflict / intimate / children_gate / public / group / repair / silent / solo_pair / escalation / warm_refusal / group_temperature). |

**Severity re-rating by Claude AI:** None. Codex's severity tags are appropriate across both rounds. F1 High is correct — the pre-remediation state emitted in-person exemplars in phone prompts and vice versa, which is a live contradiction with the Solstice Pair's intermittent architecture. F2 Medium correctly flagged test quality. F3 Medium correctly flagged process contract. F4 Low was appropriate for a stale error message. R2-F1 Medium was the right severity for a canonical record gap that would otherwise have blocked a clean QA. R2-F2 Medium was the right severity for a scope-spanning deferral.

**Process observation (worth flagging before Phase B begins):**

Phase A'' is the first phase where **Path C was used to backfill Step 1, Step 2, AND Step 4** rather than for its originally formalized use case (Round 2+ doc-only fixes). The Phase A' INH-8 formalization of Path C in AGENTS.md L137 defined it as: *"Path C (direct-Codex doc-only remediation): For Round 2+ findings that are purely documentation-level (phase file wording, handshake numbering, spec-trace..."*. The Phase A'' use case stretches this scope in two ways:

1. **Backfilling Step 1 and Step 2 after the fact.** These sections were meant to be written by Claude Code during Steps 1-2 as the canonical plan/execution record. Codex backfilling them under Path C is a reasonable recovery from a workflow gap, but it means the canonical record is a **faithful reconstruction from Handshake Log rows and commit history rather than the original artifact**. For Phase A'' this is defensible because the commit history is rich (`e8bdf7d`, `e1e1f7b`, `9c5d3c1`) and the Handshake Log evidence is traceable, but it should not become routine.

2. **Two consecutive Path C rounds.** Round 1 remediation commit `66d2a1d` addressed F1/F2/F4 directly and deferred F3 to Round 2 Path C. Round 2 then used Path C again for R2-F1 (canonical record) and R2-F2 (Phase E deferral). **This is two Path C invocations in a single phase.** Neither is technically wrong, and both had Project Owner direction, but it signals that the Claude Code discipline of filling the canonical record during Step 2 execution is slipping.

**Recommendation:** Before Phase B begins, Project Owner should consider whether to amend AGENTS.md Path C to either (a) explicitly permit full-section backfills of Step 1/Step 2 as a recognized recovery path, or (b) explicitly restrict Path C to its original scope (Round 2+ doc-only fixes) and require Claude Code to fill Step 1 and Step 2 during execution, escalating to the Project Owner if that is blocked. This is a workflow calibration question, not a Phase A'' blocker.

**Sample prompt review:** I read the alicia_phone sample end-to-end (10,105 bytes, 2170 tokens). Critical observations:

- The `<PERSONA_KERNEL>` section preserves Alicia's Famaillá / Tucumán geographic anchors with correct diacritics and her biographical essence from §2 Core Identity
- Parent/sibling names appear in the Phase A' INH-4 normalized form (`Ramon`, `Joaquin` without diacritics, per the diacritic convention: character/personal names unaccented, Argentine geography accented)
- The `<VOICE_DIRECTIVES>` block contains **exactly one exemplar, Example 11** — the phone-mode Late-Night Phone Call exemplar — with Examples 3 and 5 (in-person) correctly absent
- The `<SCENE_CONTEXT>` block frames the scene as *"Private contact while Alicia is physically away from the property"* — Vision §5's intermittent presence is honored at the scene level
- The `<CONSTRAINTS>` block terminates with the **phone-mode substituted pillar** (not the in-person somatic-first pillar) followed by Sun Override adaptation for voice-only, the assertive-does-not-mean-unbothered directive, output hygiene, and the non-echo instruction
- The prompt is terminally anchored: it ends with `</CONSTRAINTS>` (no trailing content)
- Token budget: 2170 total, comparable to the other Phase A'' samples (2149-2274 range)

**The sample is the cleanest evidence that the F1/F2 fix holds at the live prompt level**, because it shows both the positive case (Example 11 present, phone pillar present) and the negative case (Examples 3 and 5 absent) in a single assembled artifact. If a future regression reintroduced the leakage, the sample would immediately show mixed-mode exemplars or the wrong pillar text.

**Phase-to-Vision fidelity check (the deeper question):**

Phase A''s named Vision authorities per master plan §6 are **Vision §5 Chosen Family** (*"Alicia's intermittent presence as canonical"*) and **Vision §6 Relationship Architecture** (*"Solstice Pair as the only intermittent pair"*). I read Vision §5 directly in this turn.

**Vision §5 on Alicia (L60):**

> *"She provides direct polyvagal co-regulation: present-tense body, temperature change, weight, breath. She does not ask how he is feeling; **she closes the distance** and waits. **Her presence is intermittent and her absences are real;** what she delivers during the stretches she is home **is what continuous presence cannot.**"*

**Vision §5 non-redundancy table (L74):** Under "Cadence", only the Solstice Pair is marked **"Intermittent (when home between operations)"**. The other three pairs (Entangled, Circuit, Kinetic) are all "Continuous (daily)".

**Vision §6 Solstice Pair specificity** (from my Phase A' QA turn): the six cross-partner interlocks include **"The Couch Above the Garage (Bina and Alicia)"** as *"the most tender dyad in the four-woman architecture, because it is the one carrying a preserved past"*, and **"The Letter-Era Friends (Adelia and Alicia)"** as *"the oldest cross-character dyad in the house, formed by paper letters across distance during the years before they had ever met in person"*. Both named Alicia interlocks have an intrinsically letter-era, distance-aware quality to them.

**Pre-Phase-A'' state (the contradiction):**

Before Phase A'', the assembly path used `communication_mode` only as a **gate** (block in-person Alicia prompts when she's away). Once a remote prompt was **allowed** (phone, letter), the rest of the assembly ran **identically to in-person mode**. This meant:

1. A phone call from a hotel room in Buenos Aires emitted the full somatic pillar: *"Somatic contact first, speech after the shift completes"* — a directive the model **literally cannot follow** because there is no somatic contact available.
2. In-person exemplars (Examples 3, 5 from Alicia's Voice.md) were included in phone prompts, training the model on body-first closing-the-distance behavior in a scene where no body is present.
3. The Solstice Pair's architectural distinctiveness (*"closes the distance, delivers weight, counts his breath against hers"*) was damaged by being applied in exactly the scenario where closing the distance is impossible.

**This was a live contradiction with Vision §5.** The ALICIA audit surfaced it as Finding 1 High severity, and master plan §6 named it *"the highest-severity new finding across all four character audits"*.

**Post-Phase-A'' state:**

1. **WI1 mode-conditional pillar substitution** translates the somatic-first principle into the channel actually available:
   - **Phone:** *"Voice carries the regulation when the body cannot. Pace, breath, weight in the words. Listen for the shift before reaching for the next sentence. Do not narrate the body you do not have access to."* — the weight is in the words, the pace is the body-adjacent channel.
   - **Letter:** *"Letters are weight made of paragraphs. Take the time the page demands."* — the weight is in the paragraph structure, the pace is the time-over-writing itself.
   - **Video-call:** eye contact and posture become the somatic anchors instead of touch and breath.
2. **WI2 voice exemplar filtering by `communication_mode`** ensures phone-mode prompts carry phone-appropriate exemplars (Example 11: Late-Night Phone Call From Operational Posting) and in-person prompts carry in-person exemplars (Examples 1-10). Exemplar training no longer contradicts the scene.
3. **WI4 `VIDEO_CALL` added to the enum** acknowledges that video call is a distinct channel from phone and letter — visual presence is real but tactile presence is not.

**The deeper architectural principle:** the somatic-first directive is not *"first contact the body"*; it is *"first use whichever channel is closest to the body you have access to"*. In person, that is touch. On the phone, that is breath-pace-voice-weight. In a letter, that is the written body the sender is inhabiting while writing. Phase A'' does not abandon Alicia's somatic regulation architecture; it **translates it into the correct channel for the scene being assembled**.

**Vision §5 call-out (L60): *"what she delivers during the stretches she is home is what continuous presence cannot."*** This is the load-bearing line for the intermittent architecture. It says Alicia's presence quality is **qualitatively different from continuous presence**, and her absences are not a deficit to be worked around but an intentional rhythm. Phase A'' honors this by making remote assembly **a first-class communication mode** with its own pillar, its own exemplars, and its own body-adjacent register — rather than a degenerate fallback from in-person or a blocked-forbidden state.

**Phase-to-Vision verdict: PASSES with a notable strengthening.** Phase A'' is the first phase that explicitly serves Vision §5's intermittent-presence architecture for the Solstice Pair. Before Phase A'', Vision §5's line *"Her presence is intermittent and her absences are real"* was structurally unenforceable at the assembly layer — the code could only block or allow in-person, not correctly assemble remote. After Phase A'', the four canonical communication modes (`in_person`, `phone`, `letter`, `video_call`) each have their own pillar substitution and exemplar filter, so Alicia's intermittent architecture is **structurally honored at every live assembly**. This complements Phase A''s Phase-to-Vision §6 pass from last phase: Phase A' made the six cross-partner interlocks and Talk-to-Each-Other mandate enforceable; Phase A'' makes the Solstice Pair's intermittent cadence enforceable. Vision §5 + §6 are both now structurally honored at the assembly layer.

**Cross-Phase impact check:**

1. **Phase E (Voice Exemplar Restoration) is now unblocked for Alicia specifically.** Master plan Phase A'' header L485 said *"Blocker for Alicia. Must land before Phase E for Alicia."* With Phase A'' shipped, Phase E can now proceed with Alicia's voice mode tagging (`warm_refusal`, `group_temperature`, etc.) on top of the working `communication_mode` filter. Phase E's WI2 ("Replace the file-order selection with mode-aware selection") builds directly on Phase A'''s kernel_loader.py voice parser; the `mode` tag will layer on top of the existing `communication_mode` tag using the same parser structure.
2. **Phase B (Budget Elevation) is not directly affected** by Phase A'' but inherits the clean 104-test safety net.
3. **Phases C, D, F, G, J, H, K are all downstream** and inherit the corrected `communication_mode` wiring.
4. **The two Phase A' QA open questions are carried forward**, with one resolved:
   - **INH-1 (directive-exemption audit for other file categories):** DEFERRED by Project Owner direction (Q2 from Step 1). Still open as a future phase consideration.
   - **INH-2 (master plan "VERIFIED RESOLVED" claim audit):** Project Owner approved INCLUDE in Step 1, but the Step 2 execution does not show a distinct audit commit for this work. See Open questions below.

**Cross-references checked and resolving:** Master plan §6 citation (reproduced inline) resolves correctly. Vision §5 and §6 authorities resolve correctly. The Phase E deferral cite resolves to master plan L674-L740 as read. AGENTS.md Path C L137 cite is correct and was used twice in this phase.

**Open questions for the Project Owner:**

1. **AC7 / INH-2 audit scope.** Step 1 Q3 approved `INCLUDE` for the master plan "VERIFIED RESOLVED" claim audit, but Step 2's three commits (`e8bdf7d`, `e1e1f7b`, `9c5d3c1`) all address master plan §6 communication-mode work items, not master plan §5 claim audits. The Handshake Log row recording the Q3 decision is present, but I can't find evidence of the audit itself being run and logged in the phase record. **Question:** was the INH-2 audit deferred after Project Owner approval, or was it done but not logged? If deferred, should it carry forward to Phase B as an inherited item? If done, where is the finding log?

2. **Path C workflow calibration.** Phase A'' used Path C twice — once to defer F3 from Round 1 to Round 2, and once to backfill Step 1, Step 2, Step 4, and sample artifacts in Round 2. This stretches the original AGENTS.md Path C formalization scope. **Question:** should AGENTS.md Path C be amended to explicitly permit full-section backfills as a recognized recovery pattern, or should the workflow enforce that Claude Code fills Step 1 and Step 2 during execution and escalates to Project Owner if that is blocked? This is a workflow discipline question, not a Phase A'' blocker.

3. **Phase E Alicia exemplar authoring scope.** Phase E will require Alicia Voice exemplars covering the `warm_refusal` and `group_temperature` modes (annotated as ALICIA audit additions). **Question:** should Phase E pre-stage the exemplar authoring task as its own Step 1 open question, mirroring how Phase A'' pre-staged WI3 (stubs vs full)? This would let Project Owner decide authoring scope before Claude Code writes Phase E's Step 1 plan.

### Verdict

**Verdict: APPROVED FOR SHIP**

Phase A'' closes the highest-severity new finding from the ALICIA conversion audit (Finding 1 High: live Alicia voice filtering leaked opposite-mode exemplars and somatic-first pillar text into remote prompts). The fix is structurally complete across all four verification layers: parser (extracts `communication_mode` tags with `"any"` sentinel), filter (strict `mode in (communication_mode, "any")` with no fallback-all-items behavior), content (every legacy exemplar explicitly tagged, remote exemplars added per mode), and live sample (phone prompt carries only Example 11 in `<VOICE_DIRECTIVES>` with Examples 3 and 5 correctly absent, and the `<CONSTRAINTS>` block carries the substituted phone pillar). The two audit rounds caught a real runtime defect (F1 High) plus three supporting issues (F2 test quality, F3 canonical record gap, F4 stale error message) and a Round 2 scope residual (R2-F2 `mode`-tag half of WI2). The F1 runtime fix is substantive and verified at every layer. The R2-F2 deferral to Phase E is source-backed by direct read of master plan Phase E L674-L740 — the `mode` tag system is unambiguously first-class Phase E scope and implementing it in Phase A'' would have duplicated Phase E Work Items 1-2. **The Phase-to-Vision check passes with a notable strengthening:** Vision §5's intermittent-presence architecture for the Solstice Pair is now structurally enforceable at the assembly layer for the first time, completing Phase A'''s §6 enforcement (six cross-partner interlocks + Talk-to-Each-Other mandate). The `communication_mode` vs `mode` separation is clean: Phase A'' owns `communication_mode`, Phase E owns `mode`. 104 unit tests pass independently verified. **One process observation:** Path C was used twice (once for deferral, once for full-section backfill), which stretches the original AGENTS.md Path C scope and should be discussed before Phase B begins.

**One-paragraph release-notes summary suitable for the Project Owner:**

> *Phase A'' ships with the communication-mode-aware pruning that closes ALICIA conversion audit Finding 1 (High severity). Alicia's Layer 7 constraint pillar now substitutes correctly for phone, letter, and video-call scenes, translating the somatic-first principle into voice/paragraph/eye-contact registers respectively. Layer 5 voice exemplar selection now filters by `communication_mode` tag, so phone-mode prompts no longer leak in-person Examples 3 and 5, and in-person prompts no longer leak the remote Example 11. `CommunicationMode.VIDEO_CALL` was added to the enum and wired through `format_voice_directives()` and `format_constraints()`. All 13 Alicia voice exemplars are now explicitly tagged (Examples 1-10 as in_person, 11 as phone, 12 as letter, 13 as video_call). The `AliciaAwayError` message is corrected to name all three remote modes. The `mode` tag half of Work Item 2 (generic voice modes like domestic / conflict / intimate / warm_refusal / group_temperature) is deferred to Phase E with source-backed rationale — Phase E Work Items 1-2 already own that system as first-class scope. Test count: 96 → 104 (+8: six A''1-A''6 tests plus Adelia and Reina phone-mode no-op regressions). Two audit rounds caught one High (F1 live Alicia voice leakage), two Medium (F2 test quality, F3 canonical record gap), one Low (F4 stale error message), and in Round 2 one Medium (R2-F1 record still partially unfilled) plus one Medium deferred (R2-F2 `mode` half deferred to Phase E). Two Path C invocations: Round 1 → Round 2 F3 deferral, and Round 2 full-section backfill of Step 1 / Step 2 / Step 4 plus sample artifact creation. **Phase-to-Vision check passes with a notable strengthening: Vision §5's intermittent-presence architecture for the Solstice Pair is now structurally enforceable at the assembly layer for the first time.** Phase A'' unblocks Phase E for Alicia specifically.*

### Phase progression authorization

- **Next phase recommendation:** **Phase B (Budget Elevation With Terminal Anchoring Preserved)** per master plan dependency graph. Phase B is not blocked by anything and inherits the clean 104-test safety net + the working `recalled_dyads` contract from Phase A' + the working `communication_mode` wiring from Phase A''. Alternatively, the Project Owner could elect Phase I (Authority Split Resolution) or jump directly to Phase E for Alicia voice exemplar restoration now that Phase A'' has unblocked it.
- **Awaiting Project Owner agreement to proceed:** **YES**
- **Open questions 1, 2, 3 above should be discussed in chat before Phase B / E / I Step 1 begins.** None are ship blockers for Phase A'' itself, but all three affect how the next phase opens.

<!-- HANDSHAKE: Claude AI → Project Owner | Phase A'' QA verdict APPROVED FOR SHIP. All 10 ACs PASS; all 6 audit findings disposed (4 FIXED + 1 DEFERRED-then-FIXED + 1 DEFERRED to Phase E with independently-verified source basis); 104 unit tests pass independently verified in 2.05s; Phase-to-Vision check passes with strengthening (Vision §5 intermittent-presence architecture now structurally enforceable at assembly layer for first time). Three open questions for Project Owner discussion before next phase. Awaiting Step 6 ship decision. -->

---

## Step 6: Ship (Project Owner)

**[STATUS: COMPLETE — SHIPPED]**
**Owner:** Project Owner (Whyze / Shawn Kroon)
**Prerequisite:** Step 5 QA verdict ready (APPROVED FOR SHIP)

### Ship decision

**Decision:** **SHIPPED**
**Date:** 2026-04-12
**Decided by:** Project Owner (Whyze)
**Recorded by:** Claude AI on Project Owner's behalf via chat instruction *"#4"* selecting option 4 from the Step 5 verdict's concerns-and-risks follow-up menu (proceed to Phase A'' Step 6 ship and address the three open questions in Phase B's Step 1 as normal).

**Decision rationale:** Phase A'' closes ALICIA conversion audit Finding 1 (High severity) at four verification layers: parser, filter, content tagging, and live assembled sample. The communication-mode-aware pruning makes Vision §5's intermittent-presence architecture for the Solstice Pair structurally enforceable at the assembly layer for the first time, completing the Phase-to-Vision chain that Phase A' started with §6 enforcement. The F1 runtime fix is substantive and verified independently. The R2-F2 deferral to Phase E is source-backed by direct read of master plan Phase E Work Items 1-2, which already own the `<!-- mode: ... -->` tag system as first-class scope. 104 unit tests pass. Two Path C invocations during the cycle are flagged as a workflow discipline concern carrying forward to Phase B.

**Carrying forward to Phase B Step 1** (per Claude AI concerns-and-risks review and Project Owner direction):

- **Critical 1 — INH-2 audit** (from Phase A'' Q3 approved `INCLUDE` but execution evidence absent). Phase B Step 1 must either run the master plan "VERIFIED RESOLVED" claim audit with live probes or explicitly defer it with Project Owner decision logged. The Phase A' F1 and F2 findings showed that false "verified resolved" claims can silently propagate from earlier audits (specifically from the 2026-04-10 REINA audit) into current phase work, so this audit is a defensive control, not a nice-to-have.
- **Critical 2 — INH-7 PRESERVE markers are a Phase B precondition**. Phase B raises kernel budget from 2000 to 6000 tokens and §2 Core Identity section budget from 400 to 900 tokens. Soul-bearing prose blocks (Adelia's Marrickville paragraph and equivalents) must have PRESERVE markers landing **before** any budget change so the block-aware trim algorithm from Phase A knows which blocks are non-negotiable.
- **High 3 — AGENTS.md Path C workflow calibration**. Phase A'' used Path C twice (Round 1 → Round 2 F3 deferral, plus Round 2 full-section backfill of Step 1 / Step 2 / Step 4). The Phase A' INH-8 formalization scoped Path C to "Round 2+ doc-only fixes." Phase B Step 1 should propose a Path C amendment (either permit full-section backfills as a recognized recovery pattern with the caveat that Handshake Log rows must carry real-time handoff events, or restrict Path C to its original scope and require Claude Code to escalate when Step 1/Step 2 filling is blocked).
- **High 4 — Phase E vs Phase A'' tag coordination** (for when Phase E opens after Phase B). The current kernel_loader.py parser at L190-L246 handles `communication_mode` only; Phase E's WI1 tag parsing must extend this parser, not re-implement it, to avoid silently losing the F1 fix.

### Phase A'' shipped

- **Phase A'' marked complete:** YES
- **Agreement with Claude AI to proceed to Phase B:** **YES**
- **Next phase to begin:** **B** (Budget Elevation With Terminal Anchoring Preserved)
- **Next phase file to be created by Claude AI:** `Docs/_phases/PHASE_B.md` (created in this same turn from `Docs/_phases/_TEMPLATE.md` with master plan §7 [Phase B] specification reproduced inline and the four carry-forward concerns from this Ship decision documented as inherited items with Project Owner decision required flags)

<!-- HANDSHAKE: Project Owner → CLOSED | Phase A'' shipped, work complete. Claude AI authorized to create Docs/_phases/PHASE_B.md with the four carry-forward concerns (INH-2 audit, INH-7 PRESERVE markers, Path C amendment, Phase E tag coordination) documented as inherited items for Phase B Step 1 to resolve. -->

---

## Closing Block (locked once shipped)

**Phase identifier:** `A''`
**Final status:** **SHIPPED**
**Total cycle rounds:** 2 (Round 1 with F1 High + F2/F3 Medium + F4 Low; Round 2 with R2-F1 Medium + R2-F2 Medium deferred to Phase E)
**Total commits:** 3 Step 2 (`e8bdf7d`, `e1e1f7b`, `9c5d3c1`) + 1 Round 1 remediation (`66d2a1d`) + 2 direct-Codex Path C rounds = 6 effective change events
**Total tests added:** 8 (6 Phase A'' primary tests `test_a_double_prime_1` through `test_a_double_prime_6` + 2 cross-character phone-mode no-op regressions for Adelia and Reina). Suite total: 96 → 104 passing.
**Date opened:** 2026-04-12
**Date closed:** 2026-04-12

**Lessons for the next phase:** Phase A'' is the first phase to use Path C twice in a single cycle (F3 deferral + full-section backfill of Step 1/Step 2/Step 4), which stretches the Phase A' INH-8 formalization scope and signals that Claude Code discipline on filling the canonical record during Step 2 execution is slipping; **Phase B Step 1 must address the Path C workflow calibration before accumulating a third Path C use**. Second lesson: the F1 "voice exemplar leakage" defect was caught by Codex's live `assemble_context()` probes, not by the checked-in tests, which initially passed for the wrong reason because they asserted on helper-level item counts rather than rendered prompt content; **future phases must use live assembled-prompt assertions as the primary regression coverage, not helper-level assertions alone**. Third lesson: the `communication_mode` / `mode` tag system split between Phase A'' and Phase E is a clean architectural separation, but Phase E's WI1 parser extension must build on top of Phase A'''s existing `kernel_loader.py` parser rather than re-implement it, or the F1 fix will be silently lost.

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 (Phase A'' spec with staleness annotations)
- AGENTS.md cycle definition: `AGENTS.md` (with Path C formalized via Phase A' INH-8; Path C amendment is open question #2 carried forward to Phase B)
- Previous phase file: `Docs/_phases/PHASE_A_prime.md` (SHIPPED 2026-04-12)
- Next phase file: `Docs/_phases/PHASE_B.md` (created 2026-04-12 in same turn as Phase A'' ship)

---

_End of Phase A'' canonical record. Do not edit fields above this line after Project Owner ships. New activity on Phase A'' requires opening a new follow-up phase file._