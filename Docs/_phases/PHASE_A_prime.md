# Phase A': Runtime Correctness Fixes

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §5
**Phase identifier:** `A'` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A (SHIPPED 2026-04-12)
**Blocks:** Phase A'', Phase B, Phase I, Phase C, Phase D, Phase E, Phase F, Phase G, Phase J.1-J.4, Phase H, Phase K (everything downstream)
**Status:** IN PROGRESS — Step 2 execution begun
**Last touched:** 2026-04-12 by Claude Code (Step 1 plan written + approved, Step 2 in progress)

---

## How to read this file

This is the **single canonical record** for this phase. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. The phase file is created by Claude AI only after the previous phase has been QA-approved and the Project Owner has agreed to proceed. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. **Handshakes are explicit** — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below — it lists every handshake event in chronological order. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase A' file created from _TEMPLATE.md after Phase A shipped. Both gates passed. Status: AWAITING PROJECT OWNER APPROVAL TO BEGIN. |
| 2 | 2026-04-12 | Project Owner | Claude Code | Authorization to begin planning granted via kickoff brief. |
| 3 | 2026-04-12 | Claude Code | Project Owner | Step 1 Plan written. Q1 (INH-5 Vision audit): INCLUDE. Q2 (INH-7 PRESERVE markers): DEFER to Phase B. Q3 (INH-8 AGENTS.md): INCLUDE. |
| 4 | 2026-04-12 | Project Owner | Claude Code | Plan APPROVED: "Execute on plan if it's vision aligned and produces high-quality." All recommendations adopted. |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)
---

## Phase A' Specification (reproduced from master plan §5, with staleness annotations)

This block reproduces the Phase A' specification from `Docs/IMPLEMENTATION_PLAN_v7.1.md` §5 verbatim so that Claude Code, Codex, and Claude AI all read the same specification without alt-tabbing. **Staleness annotations** below are added by Claude AI at file creation time (2026-04-12) based on Phase 0 and Phase A QA outcomes — the master plan text predates those outcomes and is partially historical.

### Priority

**Blocker (work item 3+)** / **Historical record (work items 1+2)**. Two of the original five master plan work items are now VERIFIED RESOLVED in code. One additional master plan work item (work item 3, BINA F7 Vision-vs-kernel origin drift) was resolved by the Phase 0 Vision rewrite, not by the in-place patch the master plan recommends. The remaining active master plan items (4 and 5) are smaller in scope than the master plan implies, but Phase A' inherits seven follow-up items from Phase 0 and Phase A QA deferrals that significantly expand its actual scope.

### Vision authority

Vision §6 Relationship Architecture (Rule of One, Talk-to-Each-Other Mandate), Vision §7 Behavioral Thesis.

### Source

`BINA_CONVERSION_AUDIT.md` findings 4, 5, 7; `ADELIA_CONVERSION_AUDIT.md` findings 3, 4, 8 (master plan source citations).

Plus inherited from Phase 0 closing: master plan §3 work item 3 staleness (Q9 deferral), repo-wide residue verifier automation gap (F1 deferral), broader Knowledge Stack diacritic normalization beyond kernel scope (Q8 deferral), per-character Vision directive file audit (low priority Phase 0 deferral).

Plus inherited from Phase A closing: R2-F1 AC2 list-preservation evidence gap, candidate PRESERVE marker authoring for the Adelia Marrickville paragraph and similar load-bearing prose blocks, master plan §4 AC2 wording clarification (Phase A Step 5 Open Question 3), AGENTS.md formalization of direct-Codex doc-only Round 2+ remediation (Phase A Step 5 Open Question 1).

### Master plan work items (verbatim from §5, with Claude AI staleness annotations)

**Work item 1: Fix Talk-to-Each-Other mandate trigger** (BINA F4 / ADELIA F3).

**Master plan status:** *"VERIFIED RESOLVED as of 2026-04-10 REINA audit. The REINA audit Verified Resolved section explicitly confirms: 'Solo Reina + Whyze scenes do not get the TALK-TO-EACH-OTHER mandate. The gate lives in `src/starry_lyfe/context/constraints.py:104` and the current test coverage exists in `tests/unit/test_assembler.py:229-240`.' The fix has been implemented in code."*

**⚠️ STALENESS FLAG (Claude AI 2026-04-12):** This work item is fully resolved. Phase A' Step 1 plan should record it as "no action required" rather than re-executing it. The original (pre-fix) behavior is documented in the master plan for historical reference but is no longer present in code. Claude Code should verify in Step 2 that the gate at `constraints.py:104` and the test coverage at `test_assembler.py:229-240` still exist as cited.

**Work item 2: Fix offstage dyad leakage** (BINA F5 / ADELIA F4).

**Master plan status:** *"VERIFIED RESOLVED as of 2026-04-10 REINA audit. The REINA audit confirms: 'Offstage dyads do not appear to leak into Layer 6. Internal dyads are only included when the other woman is present in `src/starry_lyfe/context/layers.py:232-240`, and live probing did not surface reina-bina in a Reina + Whyze scene.' The ALICIA audit independently confirmed: 'Offstage dyads did not leak in my live Alicia-Whyze probes.'"*

**⚠️ STALENESS FLAG (Claude AI 2026-04-12):** This work item is fully resolved. Phase A' Step 1 plan should record it as "no action required" rather than re-executing it. Claude Code should verify in Step 2 that the gate at `layers.py:232-240` still exists and that the `recalled_dyads` field on `SceneState` is still present.

**Work item 3: Resolve Vision-vs-kernel Bina origin drift** (BINA F7).

**Master plan text:** *"Status: PENDING. Vision §5 says Bina is 'Canadian-born Assyrian'. Kernel and canon YAML say 'born in Urmia, Iran, brought out by her parents in the early nineties.' Both are true — Bina was born in Urmia and her parents brought her to Canada as a toddler. The Vision summary is stale shorthand. Update Vision §5 Bina paragraph to read 'Iran-born Assyrian-Canadian, raised in Canada from the early nineties' or similar precise phrasing that matches the kernel."*

**⚠️ MAJOR STALENESS FLAG (Claude AI 2026-04-12):** This work item is **resolved by removal**, not by the in-place patch the master plan recommends. Phase 0's Vision rewrite (commit `c0edc0e`) removed the heritage line from Vision §5 Bina paragraph entirely — the new text is essence-only with biographical detail deferred to the kernel. **The master plan's recommended phrasing "Iran-born Assyrian-Canadian, raised in Canada from the early nineties" was not adopted because the Vision rewrite chose a cleaner architectural approach** (the principle: "the vision names architectural function, the kernels carry biographical detail"). This work item closure happened in Phase 0, not Phase A'. The work that Phase A' actually owes here is **updating the master plan §5 work item 3 text to reflect the Phase 0 outcome** (Q9 from Phase 0 closing). This is now a master plan documentation update task, not a Vision edit task.

**Work item 4: Verify no similar Vision-vs-kernel drifts exist** for Adelia, Reina, or Alicia.

**Master plan text:** *"Run a targeted consistency check: Vision §5 one-paragraph summary vs kernel §2 Core Identity first paragraph for each of the other three characters. Flag and resolve any drifts found."*

**✅ STILL ACTIVE (Claude AI 2026-04-12):** This is genuinely Phase A' work. The Vision essence revision in Phase 0 simplified §5 for all four characters, but a fresh Vision-vs-kernel consistency audit for Adelia, Reina, and Alicia has not been performed against the post-rewrite Vision text. Phase A' Step 1 should plan this audit and Step 2 should execute it. Expected effort: small (4 paragraph reads + 4 spot checks).

**Work item 5: Add Adelia and Reina live `assemble_context()` tests** (ADELIA F8 audit-driven addition).

**Master plan text:** *"The current Phase 3 test suite has live assemble_context() coverage for Bina and Alicia only. Adelia and Reina have NO live assemble-level tests. Add minimal smoke tests: `tests/unit/test_assembler.py::test_assemble_context_adelia_solo_pair` — assert basic assembly succeeds, terminal anchoring holds, no Msty artifacts present; `tests/unit/test_assembler.py::test_assemble_context_reina_solo_pair` — same shape for Reina. These are minimum viable smoke tests, not the per-character regression bundles from Phase H. The point is to give Phase H a working baseline to extend."*

**✅ STILL ACTIVE (Claude AI 2026-04-12):** This is genuinely Phase A' work. Phase A added 18 unit tests to `test_budgets.py` but did not extend `test_assembler.py` for Adelia or Reina. Expected effort: small (2 smoke tests, ~30 lines each).

### Inherited work items (from Phase 0 and Phase A QA deferrals)

These are not in master plan §5 but are owed to Phase A' as the natural follow-up phase. Claude Code's Step 1 plan should treat them as first-class scope items alongside the master plan items.

**INH-1: Master plan §3 work item 3 staleness update** (from Phase 0 Q9 deferral). The master plan text recommending in-place patch of Vision §5 Bina is now historical. Update master plan §3 to reflect the actual Phase 0 outcome (Vision rewrite, heritage line removed, biographical detail in kernel only). Small effort: ~2 paragraphs of master plan text.

**INH-2: Master plan §5 work item 3 staleness update** (from this file's staleness flag above). Same task, different section: update master plan §5 work item 3 to acknowledge it was resolved in Phase 0, not deferred. Small effort: ~1 paragraph.

**INH-3: Repo-wide residue verifier automation** (from Phase 0 F1 deferral). Add a checked-in repo-wide residue verifier covering `src/ + Characters/ + Vision/` with the same exclusion list Phase 0's manual `rg` pass used. This closes the AC1 automation gap that Phase 0 F1 surfaced. Medium effort: ~80-120 lines of test infrastructure.

**INH-4: Broader Knowledge Stack diacritic normalization** (from Phase 0 Q8 deferral). The narrow reading of "kernels" in Phase 0 Q8 was scoped to `<Name>_v7.1.md` files only; ~20 additional parent-name diacritic line-hits remain across `Adelia_Raye_Knowledge_Stack.md` (~13), `Alicia_Marin_Knowledge_Stack.md` (~4), `Reina_Torres_Knowledge_Stack.md` (~2), and `Adelia_Raye_Entangled_Pair.md` (~1). Small effort: ~20 line-edits across 4 files.

**INH-5: Per-character Vision directive file audit** (from Phase 0 low-priority deferral, optional). The four files `Vision/Adelia Raye.md`, `Vision/Alicia Marin.md`, `Vision/Bina Malek.md`, `Vision/Reina Torres.md` contain v7.0 transplant narratives technically excluded from Phase 0 grep but may drift over time. Small effort if simple audit only; larger if rewrites required. Phase A' Step 1 should decide whether to include this or defer further.

**INH-6: R2-F1 AC2 list-preservation evidence gap** (from Phase A R2-F1 deferral). Two named remediation paths from Phase A Step 4': **(a)** rebalance section budgets so a real list block survives under realistic pressure, OR **(b)** add a master-plan clarification narrowing the AC2 sample-evidence requirement to structures present in the retained runtime slice. Path (b) is the cheaper option and aligns with the reality that the kernels are prose-only. Phase A' Step 1 should pick one path explicitly.

**INH-7: Candidate PRESERVE marker authoring** (from Phase A QA Step 5 Open Question 2). Phase A defers production marker authoring to a separate PR per master plan §4 Q5. The Adelia Marrickville paragraph is a legitimate candidate based on Phase A QA's sample review (~226 tokens of soul-bearing Inner West origin content currently dropped at the 2000-token budget). **Project Owner decision required:** should Phase A' include marker authoring as a work item, or wait for Phase B to raise default budgets?

**INH-8: AGENTS.md formalization of direct-Codex doc-only Round 2+ remediation** (from Phase A QA Step 5 Open Question 1). The Phase A Round 2 remediation was applied directly by Codex under Project Owner override. Defensible optimization for trivial doc fixes but worth recording in AGENTS.md. **Project Owner decision required:** should AGENTS.md be updated to formally permit "direct-Codex remediation for doc-only Round 2+ findings when explicitly authorized by the Project Owner"?

### Test cases (from master plan §5 + inherited)

- **Test A'1:** Bina+Whyze two-person scene assembles without the Talk-to-Each-Other mandate block ✅ ALREADY PASSING in code (from work item 1 historical resolution)
- **Test A'2:** Bina+Reina+Whyze three-person scene assembles WITH the Talk-to-Each-Other mandate block ✅ ALREADY PASSING in code (from work item 1 historical resolution)
- **Test A'3:** Bina+Whyze scene does NOT include a bina-reina dyad block unless `recalled_dyads={"bina-reina"}` ✅ ALREADY PASSING in code (from work item 2 historical resolution)
- **Test A'4:** Vision-vs-kernel consistency check passes for all four characters against post-rewrite Vision §5 (from work item 4, PENDING)
- **Test A'5:** `test_assemble_context_adelia_solo_pair` and `test_assemble_context_reina_solo_pair` exist and pass (from work item 5, PENDING)
- **Test A'6:** Repo-wide residue verifier (INH-3) passes against the canonical exclusion list (PENDING)
- **Test A'7:** PRESERVE marker authoring (INH-7) verified by sample re-generation showing the previously-dropped content is now retained (PENDING, only if Project Owner approves INH-7)

### Files likely touched (estimate)

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` (master plan staleness updates from INH-1 and INH-2)
- `Vision/Starry-Lyfe_Vision_v7.1.md` (consistency check from work item 4 — likely no edits needed since Phase 0 already normalized it; this is a verification task)
- `tests/unit/test_assembler.py` (work item 5 smoke tests for Adelia and Reina)
- `tests/unit/test_residue_grep.py` or new `tests/integration/test_residue_repo_wide.py` (INH-3 automation)
- `Characters/{Adelia,Alicia,Reina}/*_Knowledge_Stack.md` and `Adelia_Raye_Entangled_Pair.md` (INH-4 diacritic normalization)
- Optionally: `Vision/{Adelia Raye,Alicia Marin,Bina Malek,Reina Torres}.md` (INH-5 audit)
- Optionally: `Characters/Adelia/Adelia_Raye_v7.1.md` and other kernels (INH-7 PRESERVE marker authoring, contingent on Project Owner approval)
- Optionally: `AGENTS.md` (INH-8 workflow formalization, contingent on Project Owner approval)
- This phase file (Steps 1 through 6 fill-in across the cycle)

### Exit criteria (acceptance criteria for Phase A' complete)

- Master plan §3 and §5 staleness updates committed (INH-1, INH-2)
- Vision-vs-kernel consistency check verified for all four characters with no remaining drifts (work item 4)
- Adelia and Reina smoke `assemble_context()` tests added and passing (work item 5)
- Decision recorded for INH-3 (automation), INH-4 (diacritics), INH-5 (Vision directive audit), INH-6 (R2-F1 path), INH-7 (PRESERVE markers), INH-8 (AGENTS.md formalization)
- For each INH-* item that the Project Owner approves into scope: corresponding code/doc edits committed and any tests passing
- Test suite total ≥ 91 (no regressions from Phase A baseline)
- All Critical and High Codex audit findings (if any) FIXED before QA hand-off
- Vision authority intact: any changes to Vision §6 or §7 (the named Phase A' Vision authorities) are explicitly traced through Plan + QA



---

## Step 1: Plan (Claude Code)

**[STATUS: APPROVED by Project Owner on 2026-04-12; Claude Code proceeding to Step 2]**
**Owner:** Claude Code
**Reads:** Master plan §5 (reproduced above with staleness flags), Phase A closing lessons, `src/starry_lyfe/context/` current code state, character kernels, Vision
**Writes:** This section

### Plan content

**Scope:** Phase A' is a correctness and hygiene phase. No new production runtime code. Work is: verification (WI1/2/4), documentation (INH-1/2/6), new tests (WI5, INH-3), canon cleanup (INH-4), workflow formalization (INH-8), and a light Vision directive audit (INH-5). INH-7 (PRESERVE markers) deferred to Phase B.

**Files to modify:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` (INH-1/2/6), `tests/unit/test_assembler.py` (WI5), `tests/unit/test_residue_grep.py` (INH-3), `Characters/{Adelia,Alicia,Reina}/*_Knowledge_Stack.md` + `Adelia_Raye_Entangled_Pair.md` (INH-4), `AGENTS.md` (INH-8), `Vision/{Name}.md` files (INH-5 audit), `Docs/_phases/PHASE_A_prime.md`.

**Test cases:** `test_assemble_context_adelia_solo_pair` (WI5), `test_assemble_context_reina_solo_pair` (WI5), `test_v70_residue_repo_wide` (INH-3 extending existing test_residue_grep.py).

**Acceptance criteria:** AC1 master plan staleness committed, AC2 Vision-vs-kernel 4-character consistency, AC3 Adelia+Reina smoke tests, AC4 all INH decisions recorded + approved items done, AC5 test suite ≥91, AC6 repo-wide verifier passing, AC7 diacritic normalization complete.

**Deviations:** none. INH-7 (PRESERVE markers) explicitly deferred to Phase B per Project Owner approval.

**Estimated commits:** 5-6.

**Open questions:** Q1 INH-5 INCLUDE (approved), Q2 INH-7 DEFER (approved), Q3 INH-8 INCLUDE (approved).

### Plan approval

**Project Owner approval:** APPROVED on 2026-04-12 — "Execute on plan if it's vision aligned and produces high-quality." All recommendations adopted.

<!-- HANDSHAKE: Claude Code → Project Owner | Step 1 Plan written and approved; proceeding to Step 2 -->

---

## Step 2: Execute (Claude Code)

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section, sample assembled prompts in `Docs/_phases/_samples/PHASE_A'_*.txt`

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
- **Sample assembled prompt outputs:** (saved to `Docs/_phases/_samples/PHASE_A'_assembled_character_name_2026-04-12.txt`)
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
**Reads:** Master plan §5, the plan and execution log above, git diff against the pre-phase commit, the actual test files, sample assembled prompts in `Docs/_phases/_samples/`, character kernel files for any phase that touches a character, the four archived character conversion audits in `Docs/_archive/` for template reference
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
**Reads:** Master plan §5, the entire phase file above, the test output from the most recent run, sample assembled prompt outputs, the phase status log
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
- **Once Project Owner agrees, Claude AI will create the next phase file at:** `Docs/_phases/PHASE__doubleprime.md`

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

**Phase identifier:** _A'_
**Final status:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _audit-remediate rounds completed_
**Total commits:** _count_
**Total tests added:** _count_
**Date opened:** _YYYY-MM-DD (when this file was created by Claude AI)_
**Date closed:** _YYYY-MM-DD (when Project Owner shipped or stopped)_

**Lessons for the next phase:** _2-3 sentences from Claude AI summarizing what worked, what didn't, and what should change in the next phase's plan_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §5
- AGENTS.md cycle definition: `AGENTS.md`
- Sample assembled prompts: `Docs/_phases/_samples/PHASE_A'_*.txt`
- Previous phase file (if any): `Docs/_phases/PHASE_A.md`
- Next phase file (if shipped): `Docs/_phases/PHASE__doubleprime.md`

---

_End of Phase A' canonical record. Do not edit fields above this line after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
