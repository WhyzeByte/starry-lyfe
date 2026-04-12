# Phase C: Soul Cards from Pair and Knowledge Stack

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
**Phase identifier:** `C` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A/A'/A''/B (all SHIPPED 2026-04-12)
**Blocks:** Phase D, E, F, G, H, J.1-J.4, K
**Status:** IN PROGRESS — Step 2 execution begun
**Last touched:** 2026-04-12 by Claude Code (Step 1 plan approved, Step 2 in progress)

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The phase file is created by Claude AI only after the previous phase has been QA-approved and the Project Owner has agreed to proceed. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. **Handshakes are explicit** — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below — it lists every handshake event in chronological order. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase C created after Phase B shipped. Two URGENT preconditions: INH-2 + INH-8. |
| 2 | 2026-04-12 | Project Owner | Claude Code | Authorization to begin. "Execute Ultraplan." All recommendations adopted. |
| 3 | 2026-04-12 | Claude Code | — | PRE-2 DONE: AGENTS.md Path C restrictive amendment committed (d6b20cc). PRE-1 DONE: INH-2 master plan audit — all VERIFIED RESOLVED claims live-probed and confirmed accurate (WI1 Gavin fix live, WI2 recalled_dyads live, WI3 Vision §5 clean, false positive in Appendix A changelog only). |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)
---

## Phase C Specification (master plan §3, with Phase B carry-forward preconditions)

### Vision authority
Vision §5 Chosen Family (non-redundancy), §6 Relationship Architecture (interlocks as first-class elements).

### Priority
High. Pair files (15-17K tokens each) and Knowledge Stacks (10-80K tokens) contain the deepest character differentiation. Currently excluded from runtime entirely.

### Source of truth
- `Characters/<n>/<n>_<Pair>_Pair.md` remains canonical authored reference (v7.1-native, verified during 2026-04-12 audit)
- `Characters/<n>/<n>_Knowledge_Stack.md` remains canonical
- **Soul cards are a NEW artifact** distilled from pair+knowledge files into compact runtime-loadable blocks
- Stored as markdown files in `src/starry_lyfe/canon/soul_cards/`
- **Human-authored**, validated by tests asserting specific canonical concepts appear

**Deliberate decision against LLM auto-distillation.** Earlier cleanup effort removed LLM-introduced drift; auto-generating soul cards would reintroduce that failure mode.

### Directory structure

```
src/starry_lyfe/canon/soul_cards/
    pair/
        adelia_entangled.md
        bina_circuit.md
        reina_kinetic.md
        alicia_solstice.md
    knowledge/
        adelia_cultural.md      (audit-driven from ADELIA F6)
        adelia_workshop.md
        adelia_pyrotechnics.md
        bina_ritual.md
        bina_grief.md
        reina_stable.md
        reina_court.md
        alicia_rioplatense.md
        alicia_famailla.md
        alicia_operational.md
        alicia_remote.md        (audit-driven from ALICIA F1 / Phase A'')
```

### Soul card schema (YAML frontmatter + markdown body)

```markdown
---
character: bina
card_type: pair
source: Characters/Bina/Bina_Malek_Circuit_Pair.md
budget_tokens: 700
activation:
  always: true
required_concepts:
  - "Circuit Pair"
  - "Orthogonal Opposition"
  - "total division of operational domains"
  - "diagnostic love"
  - "translation not mirroring"
---

# Bina + Whyze - Circuit Pair Soul Card
[500-700 tokens of hand-authored prose]
```

**Activation types:** `always: true`, `scene_type: [...]`, `scene_keyword: [...]`, `with_character: [...]`, `communication_mode: [...]` (Phase A'' integration).

### Work items

1. **Soul card loader** `src/starry_lyfe/context/soul_cards.py`: `load_soul_card()`, `find_activated_cards()`, `format_soul_cards()`.
2. **Layer 1/6 integration.** Pair cards load into Layer 1 (always, 700 tok). Knowledge cards load into Layer 6 (scene-conditional, 300-500 tok each).
3. **Author 4 pair soul cards.** HUMAN AUTHORING (Project Owner or knowledgeable reviewer). Placeholders fail validation until real content lands.
4. **Author 11 knowledge soul cards** in Phase J priority order.
5. **Validation tests.** Token budget, required concepts, activation logic.

### Test cases (spec + INH-7 extension)

- `test_soul_card_loader_parses_frontmatter`
- `test_pair_cards_within_700_token_budget`
- `test_knowledge_cards_within_500_token_budget`
- `test_required_concepts_present_in_each_card`
- `test_pair_card_always_activated_for_focal_character`
- `test_knowledge_card_scene_activation`
- `test_alicia_remote_card_activates_on_communication_mode_phone` (Phase A'' integration)

### Files likely touched
- `src/starry_lyfe/canon/soul_cards/` (new, 15 card files)
- `src/starry_lyfe/context/soul_cards.py` (new)
- `src/starry_lyfe/context/layers.py` (L1 + L6 integration)
- `src/starry_lyfe/context/assembler.py` (scene_state passthrough)
- `tests/unit/test_soul_cards.py` (new)

---

## URGENT PRECONDITIONS from Phase B carry-forward

**These MUST resolve before any Phase C Step 2 code work.**

### INH-2: Master plan "VERIFIED RESOLVED" claim audit

**Status:** CRITICAL — SILENTLY DROPPED IN PHASE B

**Why this matters:** Phase A' F1 and F2 both invalidated "VERIFIED RESOLVED as of 2026-04-10 REINA audit" claims in master plan §5. The Talk-to-Each-Other gate was live-broken (Gavin case). The `recalled_dyads` field was entirely absent from `SceneState`. Both claimed resolved, both false. Codex caught via live probes.

**What Phase B was supposed to do:** Project Owner approved `INCLUDE` in Phase B Step 1 Q3. Phase B Step 2 never executed the audit. No finding logged. No deferral rationale. Silently dropped.

**What Phase C Step 1 MUST do:**
1. Grep master plan for "VERIFIED RESOLVED", "already resolved", "historically resolved", "resolved in" patterns
2. For each hit, run a live Python probe that would falsify the claim if wrong
3. Log all results in Step 2 as first work item BEFORE any soul card code
4. Either confirm all claims OR file findings for each stale claim

**Estimated effort:** 1-2 hours. Pays for itself the first time it prevents a Round 1 failure.

### INH-8: AGENTS.md Path C amendment

**Status:** CRITICAL — WORKFLOW DRIFT AT 1-1-2-3 ACROSS 4 PHASES

**The trajectory:**
- Phase A: 1 Path C use
- Phase A': 1 Path C use + INH-8 formalization
- Phase A'': 2 Path C uses
- Phase B: **3 Path C uses** (Step 1, Step 2, Step 4 all backfilled)

**Why this matters:** Path C was formalized for "Round 2+ doc-only fixes." Full-section backfills stretch the scope. The cycle's audit value comes from original authoring (in-flight uncertainty, open questions considered, pre-commit rationale). Reconstruction from commit history is lossy.

**What Phase C Step 1 MUST do:**
1. Draft AGENTS.md Path C amendment text (Restrictive recommended: Path C = Round 2+ doc-only cleanup only, max 1 use per phase, Codex hard-refusal on template Step 1/2/4 R1)
2. Project Owner approves wording
3. Amendment lands as first Phase C Step 2 commit
4. Claude Code fills Step 1 and Step 2 during execution (not backfilled)

**Escalation behavior required:** If Claude Code is blocked from filling Step 1 or Step 2, escalate to Project Owner in chat and pause the cycle. Do NOT proceed to later steps and reconstruct earlier ones.

### Acceptance criteria additions (on top of master plan)

- **AC-PRE-1:** INH-2 audit executed with log in Step 2 first work item position
- **AC-PRE-2:** AGENTS.md Path C amendment landed and approved before first soul card code commit
- **AC-PRE-3:** Claude Code Step 1 and Step 2 are written during execution, not backfilled
- **AC-PRE-4:** Zero Path C uses in Phase C cycle (target: reset the discipline)



---

## Step 1: Plan (Claude Code)

**[STATUS: APPROVED by Project Owner on 2026-04-12]**
**Owner:** Claude Code
**Reads:** Master plan §3, Phase C spec above, AGENTS.md Phase C customization
**Writes:** This section

### Plan content

**Scope:** Infrastructure + placeholders. Per AGENTS.md Phase C customization, Claude Code builds the soul card loader, schema, directory structure, and placeholder files. Validation tests for content will fail until PO authors real card prose. Soul card authoring is NOT part of the four-agent cycle.

**Files:** `src/starry_lyfe/context/soul_cards.py` (new), `src/starry_lyfe/canon/soul_cards/{pair,knowledge}/` (15 placeholder files), `src/starry_lyfe/context/layers.py` + `assembler.py` (Layer 1/6 integration), `tests/unit/test_soul_cards.py` (new).

**Commits:** ~4 (loader+schema, placeholders, integration, tests+docs).

### Plan approval

**Project Owner approval:** APPROVED on 2026-04-12 — "Execute Ultraplan."

_Claude Code fills in this subsection. Required fields:_

- **Files Claude Code intends to create or modify:**
  - _list with full paths_
- **Test cases Claude Code intends to add:**
  - _list with test names matching the master plan_
- **Acceptance criteria (mirror the master plan exit criteria):**
  - _list, marked as PENDING during planning_
- **Deviations from the master plan:**
  - _list with rationale; deviations require Project Owner approval before execution_
- **Estimated commits:**
  - _number_
- **Open questions for the Project Owner before execution:**
  - _list, or "none"_

### Plan approval

**Project Owner approval:** _PENDING_ (must be APPROVED before Claude Code proceeds to Step 2)

<!-- HANDSHAKE: Claude Code → Project Owner | Plan ready for review and approval -->

---

## Step 2: Execute (Claude Code)

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section, sample assembled prompts in `Docs/_phases/_samples/PHASE_C_*.txt`

### Execution log

_Claude Code fills in this subsection during and after execution. Required fields:_

- **Commits made (one row per commit):**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | _pending_ | _pending_ | _pending_ |

- **Test suite delta:**
  - Tests added: _list with names_
  - Tests passing: _count before → count after_
  - Tests failing: _list with names + reason, or "none"_
- **Sample assembled prompt outputs:** (saved to `Docs/_phases/_samples/PHASE_C_assembled_character_name_2026-04-12.txt`)
  - _list of file paths_
- **Self-assessment against acceptance criteria:**
  - _per criterion: MET / NOT MET / PARTIAL with one-sentence evidence_
- **Open questions for Codex / Claude AI / Project Owner:**
  - _list, or "none"_

<!-- HANDSHAKE: Claude Code → Codex | Execution complete, ready for audit (Round 1) -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan §3, the plan and execution log above, git diff against the pre-phase commit, the actual test files, sample assembled prompts in `Docs/_phases/_samples/`, character kernel files for any phase that touches a character, the four archived character conversion audits in `Docs/_archive/` for template reference
**Writes:** This section. Codex does NOT modify production code, does NOT commit fixes, does NOT touch the canon directly. Trivial typos go in the audit as Low-severity findings for Claude Code to apply.

### Audit content

_Codex fills in this subsection. Follows the template of the four archived character conversion audits. Required fields:_

- **Scope:** _which files reviewed, which Phase specification consulted_
- **Verification context:** _test suite state, lint state, type-check state_
- **Executive assessment:** _2-3 paragraph plain-language verdict_
- **Findings (numbered, severity-tagged):**

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| 1 | _Critical/High/Medium/Low_ | _description_ | _file:line or test name_ | _what should change_ |

- **Runtime probe summary:** _live observations from running the code_
- **Drift against specification:** _places where the implementation diverged from the master plan_
- **Verified resolved:** _items from the execution log that Codex independently confirmed_
- **Adversarial scenarios constructed:** _at least 3 red-team scenarios specific to this Phase_
- **Gate recommendation:** PASS / PASS WITH MINOR FIXES / FAIL

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete, ready for remediation -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code
**Reads:** The audit above, the master plan, the canon
**Writes:** Production code, tests, this section. May supersede sample assembled prompts in `Docs/_phases/_samples/` with new versions.

### Remediation content

_Claude Code fills in this subsection. Required fields:_

- **Per-finding status table** (one row per finding from the audit):

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| 1 | _from audit_ | FIXED / PUSH_BACK / DEFERRED | _pending_ | _push-back rationale or deferral target phase_ |

- **Push-backs:** Each push-back must cite specific evidence from the master plan, character kernel files, or canon YAML showing that Codex misread the specification. Push-backs are recorded but do not unilaterally close findings — Codex may re-file in a re-audit round with stronger evidence.
- **Deferrals:** Each deferral must specify the target phase or follow-up work item and be tracked in the master plan.
- **Re-run test suite delta:** _tests passing before remediation → tests passing after_
- **New sample assembled prompts:** _list of paths that supersede the originals_
- **Self-assessment:** _are all Critical and High findings now closed?_

### Path decision

_Claude Code must choose one of the two paths from AGENTS.md:_

- **Path A (clean remediation):** No new architectural surface introduced. Skip re-audit, hand directly to Claude AI QA.
- **Path B (substantive remediation):** Nontrivial design changes. Codex re-audits before Claude AI QA.

**Chosen path:** _A or B_

<!-- HANDSHAKE: Claude Code → {Codex if Path B / Claude AI if Path A} | Remediation Round 1 complete, ready for {re-audit / QA} -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B was chosen in Round 1)

**[STATUS: NOT STARTED]**

_Same structure as Round 1. Codex re-audits the remediation, focusing on (a) whether the original findings are now actually closed and (b) whether the remediation introduced any new findings._

### Round 2 audit content

_Codex fills in if invoked. Same fields as Round 1._

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 2 complete, ready for remediation Round 2 -->

---

## Step 4': Remediate (Claude Code) — Round 2 (only if Round 2 audit produced new findings)

**[STATUS: NOT STARTED]**

_Same structure as Round 1. Same path decision rule._

<!-- HANDSHAKE: Claude Code → {Codex if Path B / Claude AI if Path A} | Remediation Round 2 complete -->

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
**Reads:** Master plan §3, the entire phase file above, the test output from the most recent run, sample assembled prompt outputs, the phase status log
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
- **Once Project Owner agrees, Claude AI will create the next phase file at:** `Docs/_phases/PHASE__TBD.md`

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

**Phase identifier:** _C_
**Final status:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _audit-remediate rounds completed_
**Total commits:** _count_
**Total tests added:** _count_
**Date opened:** _YYYY-MM-DD (when this file was created by Claude AI)_
**Date closed:** _YYYY-MM-DD (when Project Owner shipped or stopped)_

**Lessons for the next phase:** _2-3 sentences from Claude AI summarizing what worked, what didn't, and what should change in the next phase's plan_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
- AGENTS.md cycle definition: `AGENTS.md`
- Sample assembled prompts: `Docs/_phases/_samples/PHASE_C_*.txt`
- Previous phase file (if any): `Docs/_phases/PHASE_B.md`
- Next phase file (if shipped): `Docs/_phases/PHASE__TBD.md`

---

_End of Phase C canonical record. Do not edit fields above this line after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
