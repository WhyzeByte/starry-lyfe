# Phase C: Soul Cards from Pair and Knowledge Stack

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
**Phase identifier:** `C` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A/A'/A''/B (all SHIPPED 2026-04-12)
**Blocks:** Phase D, E, F, G, H, J.1-J.4, K
**Status:** IN PROGRESS — Round 1 audit complete, awaiting remediation
**Last touched:** 2026-04-12 by Codex (Round 1 audit recorded)

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
| 4 | 2026-04-12 | Codex | Claude Code | Round 1 audit recorded from the landed Phase C code surface because Step 2 was never canonically filled. Gate recommendation: FAIL. Findings: F1 High (soul cards are still excluded from the live Layer 1 / Layer 6 assembly path), F2 Medium (Phase C tests pass for the wrong reason and the placeholder validation contract is not actually enforced), F3 Medium (the canonical Phase C record is still execution-incomplete: Step 1 remains partially templated, Step 2 is untouched, and there are no `PHASE_C_*` sample artifacts), F4 Low (the declared `scene_type` activation schema is not implemented). |

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

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan §3, the plan and execution log above, git diff against the pre-phase commit, the actual test files, sample assembled prompts in `Docs/_phases/_samples/`, character kernel files for any phase that touches a character, the four archived character conversion audits in `Docs/_archive/` for template reference
**Writes:** This section. Codex does NOT modify production code, does NOT commit fixes, does NOT touch the canon directly. Trivial typos go in the audit as Low-severity findings for Claude Code to apply.

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` Phase C and the inline Phase C specification in this file
- `Docs/_phases/PHASE_C.md` header, Handshake Log, Step 1, Step 2, and acceptance-criteria carry-forward state
- landed Phase C commit `59da789` and precondition commit `d6b20cc`
- `src/starry_lyfe/context/soul_cards.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/assembler.py`
- `src/starry_lyfe/context/types.py`
- all 15 placeholder files under `src/starry_lyfe/canon/soul_cards/`
- `tests/unit/test_soul_cards.py`
- `Docs/_phases/_samples/` for checked-in `PHASE_C_*` artifacts

Because Step 2 was never populated canonically, this audit used the landed commit surface and live runtime probes as the execution record.

#### Verification context

Independent checks run during audit:

- `.venv\Scripts\python -m pytest tests/unit/test_soul_cards.py -q` -> **PASS WITH ANOMALY** (`11 passed, 2 xpassed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS WITH ANOMALY** (`123 passed, 2 xpassed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`123 passed, 2 xpassed, 14 errors`) because PostgreSQL is unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- commit-surface diff check for claimed Layer 1 / Layer 6 integration
- live `assemble_context(...)` probe with the canonical unit-test style stub bundle patched into `retrieve_memories`
- crash-on-call probe that patched `starry_lyfe.context.soul_cards.find_activated_cards` and `load_all_soul_cards` to raise if reached from live assembly
- artifact presence check for `Docs/_phases/_samples/PHASE_C_*`

#### Executive assessment

Phase C has real scaffolding: the new soul-card loader exists, the canonical directory contains all 15 placeholder files, frontmatter parsing works, and the helper-level activation/formatting code is coherent for the currently used activation tags. Static checks are clean, and the placeholder formatter is safely inert.

The core phase objective is still unmet. The live assembly path never calls the soul-card machinery, so pair cards do not reach Layer 1 and knowledge cards do not reach Layer 6. The green test file did not catch this because it never touches `assemble_context()` and the placeholder-validation tests are vacuous enough to report `XPASS` instead of failure. The canonical phase record is also materially incomplete: Step 2 is still an untouched template and there are no Phase C sample prompt artifacts.

Gate recommendation: **FAIL**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | High | Soul cards are still excluded from the live runtime prompt path. Phase C's core Layer 1 / Layer 6 integration work item did not land. | The spec requires pair cards in Layer 1 and knowledge cards in Layer 6 at `Docs/_phases/PHASE_C.md:99-103`. But `src/starry_lyfe/context/layers.py:42-53` builds Layer 1 only from `load_kernel()`, `src/starry_lyfe/context/layers.py:210-255` builds Layer 6 only from scene state / dyads / open loops, and `src/starry_lyfe/context/assembler.py:93-116` wires only those existing formatters. The landed Phase C diff also never touched `layers.py` or `assembler.py`; `git diff --stat d6b20cc..59da789 -- ...` shows only `src/starry_lyfe/context/soul_cards.py`, the 15 card files, and `tests/unit/test_soul_cards.py`. In a live probe, `assemble_context()` still succeeded after patching `starry_lyfe.context.soul_cards.find_activated_cards` and `load_all_soul_cards` to raise on use, printing `assembled_ok`, `contains_pair_header False`, `contains_placeholder False`. | Wire pair-card activation/formatting into Layer 1 and knowledge-card activation/formatting into Layer 6 on the live `assemble_context()` path. Add end-to-end regression tests that patch in non-placeholder cards and assert their bodies appear in the correct wrapped layers. |
| F2 | Medium | The Phase C test suite passes for the wrong reason and does not enforce the placeholder-validation contract described by the spec. | `tests/unit/test_soul_cards.py:114-130` marks the content-validation tests `xfail`, but both tests skip every placeholder via `and not card.is_placeholder`, so with the current all-placeholder corpus they make no assertions and report `XPASS` instead of failing. The targeted run returned `11 passed, 2 xpassed`. The Phase C spec explicitly says placeholders should fail validation until human prose lands at `Docs/_phases/PHASE_C.md:101-103`, and the spec's named `test_knowledge_cards_within_500_token_budget` case at `Docs/_phases/PHASE_C.md:107-113` is absent entirely. The file also contains no `assemble_context()` or Layer 1 / Layer 6 integration coverage anywhere in `tests/unit/test_soul_cards.py:1-130`. | Make the placeholder-authoring state explicit and trustworthy: either use strict `xfail` or a separate failing/skip-gated validation path that actually signals "content not authored yet," add the missing knowledge-card budget test, and add live assembly-path coverage so the integration cannot be omitted while the suite stays green. |
| F3 | Medium | The canonical Phase C record is execution-incomplete. Step 1 still contains template residue, Step 2 is untouched, and there are no Phase C sample prompt artifacts. | The header claims execution began at `Docs/_phases/PHASE_C.md:7-8`, but the Handshake Log stops before any ready-for-audit handoff at `:26-30`. Step 1 still contains template residue at `:194-213`, Step 2 remains `NOT STARTED` at `:217-246`, and the sample-artifact check found no `PHASE_C_*` files under `Docs/_phases/_samples/`. That leaves AC-PRE-3 (`Step 1 and Step 2 are written during execution, not backfilled`) unproven at `Docs/_phases/PHASE_C.md:166-169`. | Fill Step 2 truthfully from the landed work, remove the leftover Step 1 template scaffolding, add the proper handshake state, and generate real `PHASE_C_assembled_*` prompt artifacts after the runtime integration actually exists. |
| F4 | Low | The declared `scene_type` activation schema is not implemented in the runtime model. | `Docs/_phases/PHASE_C.md:95` declares `scene_type: [...]` as a supported activation type, but `src/starry_lyfe/context/soul_cards.py:90-110` only handles `always`, `communication_mode`, `with_character`, and `scene_keyword`. `src/starry_lyfe/context/types.py:22-28` also has no `scene_type` field on `SceneState`, so there is no state surface that could satisfy the declared schema. | Either implement `scene_type` end to end or remove it from the canonical Phase C schema until a later phase introduces it. |

#### Runtime probe summary

- `load_all_soul_cards()` currently loads **15** cards successfully: **4 pair** and **11 knowledge**, all placeholders.
- The live-assembly crash-on-call probe showed the core integration gap directly:
  - patched `starry_lyfe.context.soul_cards.find_activated_cards` and `load_all_soul_cards` to raise if called
  - `assemble_context()` still completed successfully
  - probe output: `assembled_ok`, `contains_pair_header False`, `contains_placeholder False`
- The targeted Phase C suite is green but anomalous:
  - `tests/unit/test_soul_cards.py` -> `11 passed, 2 xpassed`
  - the two `XPASS` results are the placeholder validation tests that are supposed to represent "not authored yet"
- No `PHASE_C_*` sample prompt artifacts are present under `Docs/_phases/_samples/`

#### Drift against specification

- Work Item 2 (Layer 1 / Layer 6 runtime integration) is absent from the live code path.
- Work Item 5 is only partially implemented: the named `test_knowledge_cards_within_500_token_budget` case is missing, and there is no live assembly-path test coverage.
- The placeholder validation state does not match the stated contract that placeholders fail validation until the Project Owner authors real prose.
- The canonical Step 2 execution record and Phase C sample prompt artifacts are missing, so the phase file does not currently satisfy its own execution-record requirements.

#### Verified resolved

- `src/starry_lyfe/context/soul_cards.py` exists and correctly parses YAML frontmatter plus markdown body.
- The canonical soul-card directory exists with the expected **15** placeholder files.
- Helper-level activation works for the currently used activation types (`always`, `scene_keyword`, `communication_mode`) in `tests/unit/test_soul_cards.py`.
- Placeholder bodies are inert in `format_soul_cards()` and do not leak placeholder text into the prompt surface.

#### Adversarial scenarios constructed

1. **Crash-on-call integration probe:** patched the soul-card activation functions to raise if the live assembler touched them. `assemble_context()` still succeeded, proving the runtime path never consulted soul cards.
2. **Placeholder validation trap:** ran the dedicated Phase C suite expecting a "not authored yet" signal. Instead the validation tests came back `XPASS`, showing the suite is green for a vacuous reason.
3. **Spec-to-runtime schema mismatch check:** compared the declared activation schema against the actual runtime surface and confirmed that `scene_type` has no implementation path in either `SceneState` or `find_activated_cards()`.
4. **Artifact existence probe:** scanned `Docs/_phases/_samples/` for `PHASE_C_*` outputs and found none, despite the phase header claiming execution is underway.

#### Recommended remediation order

1. Fix F1 first. Until pair cards and knowledge cards actually reach Layers 1 and 6, Phase C has not delivered its core runtime value.
2. Fix F2 next. Tighten the tests so the missing integration and placeholder state cannot hide behind a green suite.
3. Fix F3 after the code/test corrections. The canonical phase record needs a truthful Step 2 execution log and real sample artifacts before QA can review the phase.
4. Fix or explicitly defer F4 last. It is lower-risk because no current placeholder card uses `scene_type`, but the schema should not overclaim.

#### Gate recommendation

**FAIL**

Phase C should not proceed to QA. The loader and placeholder corpus exist, but the main runtime integration work did not land, the test suite is giving a false sense of safety, and the canonical phase record is not execution-complete.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete. FAIL gate. F1 High: soul cards are still excluded from the live Layer 1 / Layer 6 assembly path. F2 Medium: Phase C tests pass for the wrong reason and the placeholder validation contract is not actually enforced. F3 Medium: the canonical Phase C record is still execution-incomplete with no Step 2 log or PHASE_C sample artifacts. F4 Low: the declared scene_type activation schema is not implemented. Ready for remediation Round 1. -->

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
