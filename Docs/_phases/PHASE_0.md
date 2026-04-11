# Phase 0: Pre-flight Canon Verification

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
**Phase identifier:** `0`
**Depends on:** nothing (this is the entry phase)
**Blocks:** Phase A, Phase A', Phase A'', Phase B, Phase I, Phase C, Phase D, Phase E, Phase F, Phase G, Phase J.1-J.4, Phase H, Phase K (everything)
**Status:** IN PROGRESS — Step 2 execution begun
**Last touched:** 2026-04-11 by Claude Code (Step 2 execution in progress)

**Special note for Phase 0:** This is the entry phase. There is no previous phase file. Claude AI created this file as part of the workflow setup, before the cycle has actually run for any other phase. Once Phase 0 ships, all subsequent phase files will be created by Claude AI only after the previous phase has been QA-approved and Project Owner agreement to proceed has been recorded.

---

## How to read this file

This is the **single canonical record** for Phase 0. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. **Handshakes are explicit** — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below — it lists every handshake event in chronological order. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-10 | Claude AI | Project Owner | Phase 0 file created and ready for Project Owner to authorize Claude Code to begin planning |
| 2 | 2026-04-11 | Project Owner | Claude Code | Authorization to begin Step 1 planning granted via kickoff brief |
| 3 | 2026-04-11 | Claude Code | Project Owner | Step 1 Plan written; four open questions (Q1–Q4) and one deviation (D1) require Project Owner decision before Step 2 execution |
| 4 | 2026-04-11 | Project Owner | Claude Code | Plan APPROVED via "Proceed" in chat; Claude Code recommendations adopted on Q1 (fix Bina §5 in-phase), Q2/D1 (add `Aliyeh` to drift grep), Q3 (line-level evidence), Q4 (defer `_phase_status.md`); proceed to Step 2 execution |

(Append one row per handshake event. Never delete rows.)

---

## Phase 0 Specification (from master plan §3)

This block reproduces the Phase 0 work items, exit criteria, and files-touched list from `IMPLEMENTATION_PLAN_v7.1.md` §3 verbatim so that Claude Code, Codex, and Claude AI all read the same specification without needing to alt-tab to the master plan.

### Work items

1. **Run the v7.0 drift grep** from `Claude_Code_Handoff_v7.1.md` §8.1 across `src/`, `Docs/`, `Characters/`, `Vision/` (excluding `Characters/Shawn/`, per-character Vision directive files, and the Vision changelog appendix). Any match is a failure that must be resolved before proceeding.

   **Additional drift terms (added during REINA audit integration 2026-04-10):**
   - `non-resident` (when applied to Alicia)
   - `twice yearly between operations`
   - `Spanish consular officer`
   - `based in Madrid`
   - `Alicia Marín` (with the diacritic; canonical form is `Alicia Marin` unaccented)
   - `_v7.0.md` cross-references in Pair/Knowledge files (canonical form is `_v7.1.md` for all four characters; Shawn is the only legitimate `_v7.0.md` exception)

2. **Verify character kernel canonical state** for each of the four v7.1 characters:
   - Kernel mentions the correct canonical pair name (Entangled, Circuit, Kinetic, Solstice)
   - Kernel mentions no v7.0 pair names (Golden, Citadel, Synergistic, Elemental) except as deliberate historical references with rename annotations
   - Kernel surname and parents' surname match `characters.yaml`
   - Kernel §3 heading matches the canonical pair name
   - Kernel §5 behavioral tier framework references `Persona_Tier_Framework_v7.1.md` (not `_v7.md`)

3. **Verify Vision-kernel consistency** across the four characters. Specific known drift (from BINA_CONVERSION_AUDIT.md Finding 7): Vision says Bina is "Canadian-born Assyrian"; kernel says "born in Urmia, Iran, brought out by her parents in the early nineties." Resolve toward "Canadian-born Assyrian from Urmia" (both true).

4. **Verify canon YAML consistency** with character kernels. Specific fields: `surname`, `parents`, `birthplace`, `pair_name`, `pair_classification`, `pair_mechanism`, `pair_core_metaphor`.

5. **Verify Alicia residence framing** is consistent across all files. Canonical statement: Alicia is a **resident** at the property who is **frequently away on consular operations**.

### Exit criteria

- Zero drift grep hits across the extended token list
- Zero Vision-vs-kernel drifts (or all drifts explicitly resolved with written decision)
- Zero canon YAML vs kernel mismatches
- Zero stale Alicia framing

### Files touched

No code changes. Output is a verification report, optionally committed to `Docs/Phase_0_Verification_Report_{date}.md`.

---

## Step 1: Plan (Claude Code)

**[STATUS: APPROVED by Project Owner on 2026-04-11; Claude Code proceeding to Step 2]**
**Owner:** Claude Code
**Reads:** Master plan §3 (reproduced above), `Claude_Code_Handoff_v7.1.md` §8.1 for the v7.0 drift token list, character kernels in `Characters/`, canon YAML in `src/starry_lyfe/canon/`
**Writes:** This section

### Plan content

**Files Claude Code intends to create or modify:**

1. `Docs/Phase_0_Verification_Report_2026-04-11.md` — **new file, the verification output.** Sections: (a) drift grep results with line-level evidence per token, (b) Vision-vs-kernel comparison results per character, (c) canon YAML vs kernel mismatch results per field per character, (d) Alicia residence framing check results, (e) overall verdict (CLEAN or DRIFT FOUND with itemized list).
2. `Docs/_phases/PHASE_0.md` — Claude Code updates the Step 2 execution log subsection with commit hashes, result tables, and self-assessment. Updates the `Status` field in the header. Appends rows to the Handshake Log for the Claude Code → Codex handoff at the end of Step 2.
3. **Conditional, pending Project Owner approval of Q1 below:** `Vision/Starry-Lyfe_Vision_v7.1.md` §5 Bina paragraph — resolve the BINA F7 origin drift toward `Canadian-born Assyrian from Urmia` per master plan §3 work item 3. Claude Code will draft the single-sentence replacement in Step 2 and surface it for Project Owner review before committing.
4. **Conditional, pending Project Owner approval of D1/Q2 below AND Step 2 verification:** any files containing residual `Aliyeh` occurrences — rename `Aliyeh` → `Bina` per the v7.0-to-v7.1 character rename. Prior-conversation memory indicates 46 occurrences live in Alicia's files; to be verified in Step 2 before any edits, and deferred entirely if verification shows the memory is stale.
5. **Explicitly NOT creating:** `Docs/_phase_status.md`. See Q4 below.

**Test cases Claude Code intends to add:**

None. Phase 0 is verification only — no production code changes, no new assertions. The existing test suite must still pass; Claude Code will run `make check` at the end of Step 2 as a sanity check.

**Acceptance criteria (mirror master plan §3 exit criteria):**

| # | Criterion | Status after planning |
|---:|---|---|
| AC1 | Zero drift grep hits across the extended token list | PENDING |
| AC2 | Zero Vision-vs-kernel drifts (or all drifts explicitly resolved with written decision) | PENDING |
| AC3 | Zero canon YAML vs kernel mismatches | PENDING |
| AC4 | Zero stale Alicia framing | PENDING |

**Deviations from master plan:**

**D1 (requires Project Owner approval).** Add `Aliyeh` to the drift grep token list. Master plan §3 work item 1 specifies the token list from `Claude_Code_Handoff_v7.1.md` §8.1 plus six Reina-audit additions; `Aliyeh` appears in neither. Rationale for proposing the addition: prior-conversation memory records 46 occurrences of `Aliyeh` (legacy v7.0 name for Bina) in Alicia's files. If true, these are clear v7.0 residue that AC1 ("zero drift grep hits") should catch. Adding a token to a specification-controlled grep list without written approval would itself be drift, so Claude Code is flagging this as a plan-time deviation rather than a silent execution-time choice. No other deviations proposed.

**Estimated commits:**

- **Lower bound: 1 commit.** Verification report + PHASE_0.md Step 2 execution log, committed together with message `Phase 0: pre-flight canon verification, drift grep {result}`.
- **Upper bound: 3 commits.** +1 commit if Q1 resolves to "fix in Phase 0" (Bina Vision §5 single-sentence rewrite). +1 commit if D1/Q2 resolves to "add Aliyeh to grep" AND Step 2 verification finds residual occurrences needing rename.
- Each additional commit would reference the specific work item or finding it resolves.

**Open questions for the Project Owner before execution:**

**Q1 (seeded in template).** Should the Bina Vision §5 origin drift (BINA F7) be fixed in Phase 0, or deferred to Phase A' work item 3?

> **Claude Code recommendation: fix in Phase 0.**
> Rationale: (a) master plan §3 work item 3 reads `Resolve toward "Canadian-born Assyrian from Urmia" (both true)` — imperative language, not a deferral notice. (b) AC2 is more cleanly met by fixing than by deferring with a written-decision carve-out. (c) The fix is a single sentence in `Vision/Starry-Lyfe_Vision_v7.1.md` §5 — minutes of work, not scope creep into Phase A'. (d) The AGENTS.md worked example shows a "PARTIAL, deferred" outcome, but the worked example is an illustration of cycle mechanics, not a directive overriding the master plan's imperative wording. Per the source-of-truth hierarchy, the master plan wins.
> **REQUIRES PROJECT OWNER APPROVAL.** If "fix in Phase 0", Claude Code will draft the §5 Bina paragraph replacement in Step 2 and surface it for Project Owner review before committing. If "defer to Phase A'", Claude Code will record AC2 as PARTIAL in the verification report with the written deferral decision attached.

**Q2 (seeded in template).** Are there any new drift terms the Project Owner has noticed since the integration that should be added to the grep before Phase 0 runs?

> **Claude Code recommendation:** Add `Aliyeh` (see D1 above). Beyond that, this is a question only the Project Owner can answer — it depends on what the Project Owner has noticed in recent conversations or in files Claude Code has not yet read.
> **REQUIRES PROJECT OWNER INPUT.** Any additional tokens named at approval time will be folded into the Step 2 grep in a single pass.

**Q3 (surfaced during planning).** What level of evidence detail should the verification report capture?

> **Claude Code recommendation:** line-level evidence (`file:line:quoted-context`) for every grep hit, plus `PASS` + per-token hit count for clean tokens. Vision-vs-kernel comparisons should quote both the Vision §5 paragraph and the kernel §2 first paragraph side by side. Canon YAML mismatches should quote both sides. This matches the archived REINA/ADELIA/BINA/ALICIA audit evidence style and gives Codex concrete material to verify in Step 3 without re-running the full grep.
> **REQUIRES CONFIRMATION.** Happy to lower the detail level if the Project Owner prefers a lighter-weight report.

**Q4 (surfaced during planning).** Should the optional cross-phase status index `Docs/_phase_status.md` be created in Phase 0?

> **Claude Code recommendation: no, defer.** The phase file itself is the canonical record, and there is only one phase file right now — a cross-phase index has nothing to index. Revisit after Phase A ships when the index starts earning its keep. AGENTS.md describes `_phase_status.md` as "optional; phase files are the source of truth," so skipping it is consistent with the workflow spec.
> **REQUIRES CONFIRMATION** (or Project Owner may direct otherwise).

### Plan approval

**Project Owner approval:** APPROVED on 2026-04-11 — Project Owner said "Proceed" in chat after reading the Step 1 summary. Claude Code interprets this as blanket approval of the Plan and adoption of Claude Code recommendations on all five flagged items:

- **Q1:** Fix Bina Vision §5 origin drift in Phase 0 (toward "Canadian-born Assyrian from Urmia"). Draft surfaced for review before committing the Vision file edit.
- **Q2 / D1:** Add `Aliyeh` to the drift grep token list. Step 2 verification will confirm whether the prior-conversation memory (46 occurrences in Alicia's files) is still accurate before any rename edits are made.
- **Q3:** Line-level evidence (`file:line:quoted-context`) for grep hits; side-by-side quoted text for Vision-vs-kernel and canon-vs-kernel comparisons.
- **Q4:** Do not create `Docs/_phase_status.md` in Phase 0; revisit after Phase A ships.

If the Project Owner intended any narrower scope, this is the field to record a correction in before Claude Code commits any Vision or Aliyeh edits.

<!-- HANDSHAKE: Claude Code → Project Owner | Step 1 Plan written; Q1–Q4 and D1 require Project Owner decision before Step 2 execution -->

---

## Step 2: Execute (Claude Code)

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan §3, `Claude_Code_Handoff_v7.1.md` §8.1, the canon, the character kernels
**Writes:** `Docs/Phase_0_Verification_Report_{date}.md`, this section, sample evidence files in `Docs/_phases/_samples/`

### Execution log

_Claude Code fills in during and after execution. For Phase 0 specifically:_

- **Verification report path:** `Docs/Phase_0_Verification_Report_{date}.md`
- **Drift grep results:** _per token, per file, with line numbers if found, or CLEAN_

| Token | Files searched | Hits | Status |
|---|---|---:|---|
| `Aliyeh` | src/, Docs/, Characters/, Vision/ (excluded paths per spec) | 0 | CLEAN |
| ... (one row per token) | | | |

- **Vision-vs-kernel comparison results:**

| Character | Vision §5 paragraph | Kernel §2 first paragraph | Status |
|---|---|---|---|
| Adelia | _quote_ | _quote_ | PASS / DRIFT |
| Bina | _quote_ | _quote_ | PASS / DRIFT (expected: BINA F7 known drift) |
| Reina | _quote_ | _quote_ | PASS / DRIFT |
| Alicia | _quote_ | _quote_ | PASS / DRIFT |

- **Canon YAML vs kernel mismatch results:**

| Field | Expected (kernel) | Actual (YAML) | Status |
|---|---|---|---|
| _per character per field_ | | | |

- **Alicia residence framing check results:**
  - _list of files searched, hits found (should be zero after the master integration archive pass)_

- **Commits made:**

| # | Hash | Message |
|---:|---|---|
| 1 | _pending_ | _Phase 0: pre-flight canon verification, drift grep clean_ |

- **Self-assessment against acceptance criteria:**
  - Zero drift grep hits — _MET / NOT MET / PARTIAL_
  - Zero Vision-vs-kernel drifts (or all resolved) — _MET / NOT MET / PARTIAL_
  - Zero canon YAML vs kernel mismatches — _MET / NOT MET / PARTIAL_
  - Zero stale Alicia framing — _MET / NOT MET / PARTIAL_
- **Open questions for Codex:**
  - _list, or "none"_

<!-- HANDSHAKE: Claude Code → Codex | Phase 0 execution complete, ready for audit Round 1 -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan §3, the plan and execution log above, the verification report Claude Code produced, the four archived character conversion audits in `Docs/_archive/` for template reference

### Audit content

_Codex fills in. For Phase 0 specifically, the audit focuses on:_

- **Independent re-run of the drift grep:** Did Claude Code grep all the right paths? Did Claude Code use the canonical token list including the Reina audit additions? Does Codex's grep produce the same results?
- **Vision-vs-kernel comparison spot-check:** Pick at least one character and verify Claude Code's comparison was accurate.
- **Canon YAML cross-check:** Independently load `characters.yaml` and verify field values match the kernels.
- **Adversarial scenarios constructed for Phase 0:**
  1. Insert a synthetic v7.0 token in a test file outside the excluded paths and re-run the grep to confirm it would be caught
  2. Create a synthetic Vision-vs-kernel mismatch in a temporary branch and confirm the comparison detects it
  3. Create a synthetic canon YAML field mismatch and confirm the canon check catches it
- **Findings:**

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| _per finding_ | | | | |

- **Gate recommendation:** PASS / PASS WITH MINOR FIXES / FAIL

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete, ready for remediation -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code

### Remediation content

_Claude Code fills in. For Phase 0 specifically:_

- **Per-finding status table** (one row per audit finding):

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| _per finding_ | | FIXED / PUSH_BACK / DEFERRED | | |

- **Push-backs:** _list with citations_
- **Deferrals:** _list with target follow-up phase_
- **Re-run drift grep delta:** _hits before remediation → hits after_
- **Self-assessment:** _are all Critical and High findings now closed?_

### Path decision

**Chosen path:** _A (clean) or B (substantive)_ — Phase 0 is unlikely to need Path B since it has no production code changes; remediation is typically just fixing drift in canon files

<!-- HANDSHAKE: Claude Code → Claude AI | Remediation Round 1 complete, ready for QA (Path A expected for Phase 0) -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B was chosen, or if Round 1 audit produced findings that need re-verification)

**[STATUS: NOT INVOKED]**

_Reserved. Codex re-audits only if Claude Code chose Path B in Round 1, or if the Round 1 remediation introduced new architectural surface._

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 2 complete (if invoked) -->

---

## Step 4': Remediate (Claude Code) — Round 2

**[STATUS: NOT INVOKED]**

_Reserved._

<!-- HANDSHAKE: Claude Code → Claude AI | Remediation Round 2 complete (if invoked) -->

---

## Step 3'': Audit (Codex) — Round 3 (final round before mandatory escalation)

**[STATUS: NOT INVOKED]**

_Reserved. **If this round produces unconverged findings, Claude Code MUST escalate to the Project Owner instead of starting Round 4 — see AGENTS.md cycle limit.**_

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: NOT INVOKED]**

_Reserved._

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**
**Owner:** Claude AI (the assistant in this chat)
**Prerequisite:** Step 4 (or 4', or 4'') remediation complete with handshake to Claude AI, AND Project Owner has brought the phase artifacts to Claude AI in chat

### QA verdict content

_Claude AI fills in. For Phase 0 specifically:_

- **Specification trace** (each acceptance criterion from the master plan):

| Criterion | Status | Evidence |
|---|---|---|
| Zero drift grep hits across the extended token list | _PASS / FAIL / PARTIAL_ | _evidence from execution log §2_ |
| Zero Vision-vs-kernel drifts (or all resolved) | _PASS / FAIL / PARTIAL_ | _evidence; Bina origin drift may remain as deferred to Phase A'_ |
| Zero canon YAML vs kernel mismatches | _PASS / FAIL / PARTIAL_ | _evidence_ |
| Zero stale Alicia framing | _PASS / FAIL / PARTIAL_ | _evidence_ |

- **Audit findings trace:**

| Finding # | Original severity | Final status | Evidence |
|---:|---|---|---|

- **Sample prompt review:** N/A — Phase 0 produces no assembled prompts
- **Cross-Phase impact check:** _does this Phase's verification result affect any other Phase's plan? Specifically, does the deferred Bina Vision §5 fix correctly thread into Phase A' work item 3?_
- **Open questions for the Project Owner:** _list, or "none"_

### Verdict

**Verdict:** _APPROVED FOR SHIP / APPROVED WITH MINOR FIXES / RETURN FOR REMEDIATION_

### Phase progression authorization

_Filled in only if verdict is APPROVED:_

- **Next phase recommendation:** Phase A (Structure-Preserving Compilation) per master plan dependency graph
- **Awaiting Project Owner agreement to proceed:** YES
- **Once Project Owner agrees, Claude AI will create:** `Docs/_phases/PHASE_A.md`

<!-- HANDSHAKE: Claude AI → Project Owner | QA verdict ready, awaiting ship decision -->

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**
**Owner:** Project Owner (Whyze / Shawn Kroon)
**Prerequisite:** Step 5 QA verdict ready

### Ship decision

**Decision:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Date:** _YYYY-MM-DD_
**Decided by:** Project Owner
**Decision rationale:** _one or two sentences_

### If SHIPPED

- **Phase 0 marked complete:** YES
- **Agreement with Claude AI to proceed to Phase A:** YES / NO
- **Next phase to begin:** A
- **Next phase file to be created by Claude AI:** `Docs/_phases/PHASE_A.md`

### If SENT BACK

- **Specific issues identified by Project Owner:** _list_
- **Returns to Step:** _4 (remediation) or 1 (replan)_

### If STOPPED FOR REDESIGN

- **Architectural issue surfaced:** _description_
- **Master plan update required:** _what section needs to change_

<!-- HANDSHAKE: Project Owner → CLOSED | Phase 0 shipped, work complete -->
_(or)_
<!-- HANDSHAKE: Project Owner → Claude Code | Sent back to remediation -->
_(or)_
<!-- HANDSHAKE: Project Owner → CLOSED | Phase 0 stopped for redesign -->

---

## Closing Block (locked once shipped)

**Phase identifier:** 0
**Final status:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _audit-remediate rounds completed_
**Total commits:** _count_
**Total tests added:** 0 (Phase 0 is verification only)
**Date opened:** 2026-04-10
**Date closed:** _YYYY-MM-DD_

**Lessons for the next phase:** _2-3 sentences from Claude AI_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
- AGENTS.md cycle definition: `AGENTS.md`
- Verification report: `Docs/Phase_0_Verification_Report_{date}.md`
- Previous phase file: none (Phase 0 is the entry phase)
- Next phase file (if shipped and Project Owner agrees): `Docs/_phases/PHASE_A.md`

---

_End of Phase 0 canonical record. Do not edit fields above this line after Project Owner ships. New activity on Phase 0 requires opening a new follow-up phase file._
