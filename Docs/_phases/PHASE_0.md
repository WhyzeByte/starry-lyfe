# Phase 0: Pre-flight Canon Verification

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3
**Phase identifier:** `0`
**Depends on:** nothing (this is the entry phase)
**Blocks:** Phase A, Phase A', Phase A'', Phase B, Phase I, Phase C, Phase D, Phase E, Phase F, Phase G, Phase J.1-J.4, Phase H, Phase K (everything)
**Status:** READY FOR CLAUDE AI QA (Round 1 remediation complete, Path A)
**Last touched:** 2026-04-11 by Claude Code (Step 4 Round 1 remediation complete, handed to Claude AI for QA)

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
| 5 | 2026-04-11 | Project Owner | Claude Code | Vision rewrite delivered mid-Step-2; Claude Code re-verified and replanned. Plan re-approved with decisions on Q6 (all edits in Phase 0), Q7 (fix Reina directive file), Q8 (normalize kernel diacritics), Q9 (defer master plan update to Phase A'). Project Owner directive: Alicia lives with chosen family, no resident/non-resident framing anywhere, pair names must match pair file markdown filenames. |
| 6 | 2026-04-11 | Claude Code | Codex | Phase 0 execution complete across 10 commits (dc085d5 → final). AC1-AC4 all MET. Residue-grep automated test passes. Ready for audit Round 1. |
| 7 | 2026-04-11 | Codex | Claude Code | Audit Round 1 complete. 0 Critical, 0 High, 1 Medium, 1 Low. Live files satisfy AC1-AC4, but the Phase 0 artifact trail overstates automation coverage and still carries stale pre-remediation report state. Ready for minor remediation. |
| 8 | 2026-04-11 | Claude Code | Claude AI | Remediation Round 1 complete (Path A, clean). F1 FIXED via PHASE_0.md:181 language softening (authoritative-signal claim replaced with src/-only scope note + Phase A' automation gap item). F2 FIXED via verification report header + §1 SUPERSEDED marker (historical sections preserved; §11 declared authoritative). No new architectural surface; skipping re-audit, handing directly to Claude AI QA. |

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

**[STATUS: COMPLETE — handed to Codex for Step 3 audit]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan §3, `Claude_Code_Handoff_v7.1.md` §8.1, the canon, the character kernels
**Writes:** `Docs/Phase_0_Verification_Report_2026-04-11.md`, this section

### Execution log

**Verification report path:** `Docs/Phase_0_Verification_Report_2026-04-11.md` — original verification body plus §11 "Post-Vision-Rewrite Re-Verification" addendum.

**Mid-execution event:** after Step 2 read-only verification but before any remediation edits, the Project Owner delivered a substantial Vision rewrite (`Vision/Starry-Lyfe_Vision_v7.1.md` + `Characters/Alicia/Alicia_Marin_v7.1.md` §2 new paragraph) plus additional pre-session canonical normalization work across Bina/Reina/Alicia kernels and support files. Claude Code re-verified, re-planned (plan file at `C:\Users\Whyze\.claude\plans\wiggly-kindling-floyd.md`), re-approved with Project Owner (Q6-Q9), and executed the adjusted remediation plan across 10 commits.

**Drift grep results (post-remediation):**

| Scope | Total hits | Exempt (documented exclusions) | Real drift |
|---|---:|---:|---:|
| `src/` | 2 | 2 (Mercè Benítez canonical exception + Shawn `_v7.0.md` profile_file exception) | **0** |
| `Characters/` | 5 | 5 (4 in `Characters/Shawn/` excluded, 1 in `Reina_Torres_Knowledge_Stack.md:332` Mercè household) | **0** |
| `Vision/` | 11 | 11 (8 in per-character directive files, 3 in Appendix A version history lines 179/181/185) | **0** |
| `Docs/` | all exempt | all exempt (meta references in master plan spec, changelog entries, this phase file, workflow handoff doc, archive) | **0** |

The automated residue-grep test `tests/unit/test_residue_grep.py::test_v70_residue_grep_returns_zero_matches` was run via `.venv/Scripts/python -m pytest` and **PASSED**. This test provides regression coverage for `src/` only (`_scan_src_for_residue(src_dir)` traverses `src_dir` exclusively), which is narrower than the full Phase 0 AC1 scope of `src/ + Characters/ + Vision/ + Docs/`. The authoritative evidence for AC1 across the broader scope is the four-row drift grep results table above, populated by manual `rg` passes with the documented exclusions. Closing the automation gap — adding a checked-in repo-wide residue verifier that covers `src/ + Characters/ + Vision/` with the same exclusion list used by the Phase 0 manual pass — is tracked as a Phase A' follow-up work item.

**Vision-vs-kernel comparison results:**

| Character | Status | Evidence |
|---|---|---|
| Adelia | PASS | Vision §5 (line 54) compresses kernel §2 (line 18) "born in Valencia... emigrated to Sydney 1993" to "Valencian-Australian"; consistent with canon YAML |
| Bina | PASS | **BINA F7 resolved by Vision rewrite (commit c0edc0e).** New Vision §5 (line 56) removes the heritage line entirely; kernel §2 line 18 carries canonical "First-generation Assyrian-Iranian Canadian... carried out of Urmia... Raised in Edmonton" |
| Reina | PASS | Vision §5 (line 58) and kernel §2 (line 18) agree on Barcelona-born criminal defence lawyer |
| Alicia | PASS | Vision §5 (line 60) and kernel §2 (line 18) agree on Famaillá-born; kernel §2 line 36 now canonicalizes "I am a resident, not a visitor. My absences are real absences, not visits to somewhere else." per Project Owner rewrite |

**Canon YAML vs kernel mismatch results:**

All specified fields (`surname`, `parents`, `birthplace`, `pair_name`) match for all four characters in `src/starry_lyfe/canon/characters.yaml`. `pair_classification`, `pair_mechanism`, `pair_core_metaphor` live in `src/starry_lyfe/canon/pairs.yaml` (not `characters.yaml`) and all four pair entries are canonical (Entangled / Circuit / Kinetic / Solstice with correct classifications, mechanisms, metaphors, cadences).

Parent-name diacritic inconsistency (Adelia kernel `Joaquín`/`Inés`; Alicia kernel `Ramón`; Reina kernel references to same) was normalized in commit 1 (R15-R17) per Project Owner Q8 decision. Kernel `{Name}_v7.1.md` files are now strict-compliant with the AGENTS.md "character names are unaccented" convention. Broader normalization across Knowledge Stack / Pair / Voice files deferred to Phase A' per the narrow reading of "kernels" in the Q8 question framing.

**Alicia residence framing check results:**

All stale framings (`non-resident`, `twice yearly`, `based in Buenos Aires`, `based in Madrid`, `Spanish consular officer`, `Marín` accent) removed from all non-excluded paths. Canonical phrasing now present in three locations:

1. **Alicia kernel §2 line 36** (added by Project Owner Vision rewrite, committed as c0edc0e): "My home is the Foothills County property where Whyze and the chosen family live. My work takes me away frequently and unpredictably, sometimes for weeks at a time, sometimes longer. The household is what I return to. The operations are what I do between returns. **I am a resident, not a visitor. My absences are real absences, not visits to somewhere else.**"
2. **Bina_Malek_Knowledge_Stack.md** (commit 8, b6ed33f): both the pit wall paragraph (line 137) and the context block (line 414) rewritten to "resident at the property but frequently away on consular operations."
3. **Reina_Torres_Knowledge_Stack.md** (commit 9, 3bd8597): five edits across lines 308, 310, 405, 407, 425 rewriting every Alicia-framing hit to the canonical phrasing. Commit 9 also corrected a factual error (`Racing Club Madrid` → `Racing Club de Avellaneda`, the actual Argentine club).

**Commits made (10 total):**

| # | Hash | Message | Attribution |
|---:|---|---|---|
| 1 | `dc085d5` | `chore(kernels): v7.1 canonical normalization across all four kernels` | Project Owner pre-session (Bahadori→Malek, Citadel→Circuit, Alicia §2 paragraph) + Claude Code R2-R5 (PTF refs) + R15-R17 (parent diacritics) |
| 2 | `0713331` | `chore(canon): v7.1 canonical normalization across character support files` | Project Owner pre-session (pair-name fixes in Alicia Knowledge Stack + Alicia Solstice Pair + Reina Kinetic Pair; Bina Knowledge Stack surname + pair-name fixes; Reina Kinetic Pair Alicia residence framing) |
| 3 | `c0edc0e` | `docs(vision): rewrite Vision §5 + §6 to move biographical lock-ins into kernels` | Project Owner rewrite (resolves BINA F7) |
| 4 | `9f09a5a` | `chore(workflow): establish Phase 0 four-agent workflow infrastructure` | Claude Code (AGENTS.md + `Docs/_phases/_TEMPLATE.md` + this PHASE_0.md + `Docs/_archive/` historical reference files) |
| 5 | `9cce59f` | `fix(vision): Phase 0 Q7 — Reina directive file Synergistic -> Kinetic` | Claude Code R18 |
| 6 | `35ce037` | `fix(canon): Phase 0 AC1 R6 — Adelia Entangled Pair file Elemental -> Solstice` | Claude Code R6 |
| 7 | `9a6d4f9` | `fix(canon): Phase 0 AC1 R7 — Reina kernel Alicia consular framing Spanish -> Argentine` | Claude Code R7 |
| 8 | `b6ed33f` | `fix(canon): Phase 0 AC1+AC4 R8+R9 — Bina Knowledge Stack Alicia residence framing` | Claude Code R8+R9 |
| 9 | `3bd8597` | `fix(canon): Phase 0 AC1+AC4 R10-R14 — Reina Knowledge Stack Alicia framing + Racing Club correction` | Claude Code R10-R14 |
| 10 | _(this commit)_ | `docs(phase_0): Phase 0 verification report finalized and Step 2 execution log` | Claude Code Phase 0 closure |

R1 from the original plan (in-place Bina Vision §5 patch) was **dropped** because commit 3 (Vision rewrite) resolved BINA F7 before any patch was needed.

**Self-assessment against acceptance criteria:**

- **AC1** Zero drift grep hits across the extended token list — **MET.** Production grep across `src/`, `Characters/`, `Vision/` returns zero real drift hits. All remaining hits are in documented exempt paths (Shawn/, per-character Vision directive files, Vision Appendix A, Mercè Benítez canonical exception, Shawn profile_file exception). The automated `test_v70_residue_grep_returns_zero_matches` test PASSES.
- **AC2** Zero Vision-vs-kernel drifts (or all drifts explicitly resolved with written decision) — **MET.** BINA F7 resolved by Vision rewrite (commit `c0edc0e`), not by in-place patch. All four characters pass Vision-vs-kernel consistency check.
- **AC3** Zero canon YAML vs kernel mismatches — **MET.** All specified fields match for all four characters. Parent-name diacritic normalization (commit `dc085d5`) brought the kernels into strict AGENTS.md compliance.
- **AC4** Zero stale Alicia residence framing — **MET.** All stale framings removed from non-excluded paths. Canonical "I am a resident, not a visitor" statement now present in Alicia kernel §2 line 36 and consistently applied in Bina_Malek_Knowledge_Stack.md and Reina_Torres_Knowledge_Stack.md.

**Open questions for Codex:**

- **Commit history attribution.** Phase 0 delivered 10 commits, several of which bundle Project Owner's pre-session v7.1 integration cleanup with Claude Code's Phase 0 remediation. Codex should spot-check that commit-message attribution ("Project Owner pre-session" vs "Claude Code Phase 0 remediation") matches the actual hunks in each commit. Specific commits to audit: `dc085d5` (kernel canonical normalization, mixed) and `0713331` (character support files, all Project Owner pre-session).
- **Scope expansions approved by Project Owner.** Project Owner Q7 (fix `Vision/Reina Torres.md:43` in Phase 0) and Q8 (normalize kernel parent-name diacritics in Phase 0) are scope widenings beyond the master plan's documented Phase 0 work items. Codex should confirm these are appropriately bounded (Q7 = 1 line, Q8 = kernels only, not Knowledge Stack / Pair / Voice).
- **Deferred items for Phase A'.** Three items are explicitly deferred: (1) master plan `IMPLEMENTATION_PLAN_v7.1.md` §3 work item 3 text is now stale since BINA F7 was resolved by rewrite not patch (Q9 deferral); (2) broader diacritic normalization across `Adelia_Raye_Knowledge_Stack.md` (13 line-hits) + `Alicia_Marin_Knowledge_Stack.md` (4 line-hits) + `Reina_Torres_Knowledge_Stack.md` (2 line-hits) + `Adelia_Raye_Entangled_Pair.md` (1 line-hit) — total ~20 additional parent-name diacritic line-hits; (3) Vision per-character directive file audit beyond the single-line Q7 fix (Vision/Adelia Raye.md, Vision/Alicia Marin.md, Vision/Bina Malek.md contain v7.0 transplant narratives which are technically excluded but may drift over time).
- **`make check` status.** Full `make check` was NOT run because the working tree contains substantial pre-session in-progress work in `src/starry_lyfe/context/*.py` (assembler, constraints, kernel_loader, layers), `tests/unit/test_assembler.py`, `Docs/IMPLEMENTATION_PLAN_v7.1.md` (~1485 lines), and two pending `Docs/PHASE_3_*.md` deletions — none of which are Phase 0 scope and all of which are deliberately left uncommitted for Project Owner review. The `test_v70_residue_grep_returns_zero_matches` test was run in isolation via `.venv/Scripts/python -m pytest tests/unit/test_residue_grep.py -v` and passes. Phase 0 deliverables are markdown-only and do not require lint / type-check / full test pass. If Codex wants to run `make check` against a clean state, it will need to stash the pre-session working-tree changes first.

**Files left uncommitted (deliberately, for Project Owner review):**

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` (~1485 line pre-session update)
- `src/starry_lyfe/context/{assembler,constraints,kernel_loader,layers}.py`
- `tests/unit/test_assembler.py`
- `Docs/PHASE_3_AUDIT_REMEDIATION.md` (pre-session deletion)
- `Docs/PHASE_3_REMEDIATION_AUDIT.md` (pre-session deletion)
- `Docs/CHARACTER_CONVERSION_PIPELINE.md` (pre-session untracked, not reviewed)

These are Project Owner's in-progress work that predates this session and falls outside Phase 0's canon-verification scope. Phase 0 remediation is complete without them.

<!-- HANDSHAKE: Claude Code → Codex | Phase 0 execution complete across 10 commits, AC1-AC4 all MET, residue-grep test passes, ready for audit Round 1 -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: COMPLETE — handed to Claude Code for remediation Round 1]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex
**Reads:** Master plan §3, the plan and execution log above, the verification report Claude Code produced, the four archived character conversion audits in `Docs/_archive/` for template reference

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` §3 (Phase 0 specification)
- `Docs/_phases/PHASE_0.md` Step 1 and Step 2
- `Docs/Phase_0_Verification_Report_2026-04-11.md` including §11 addendum
- `Docs/Claude_Code_Handoff_v7.1.md` §8.1 token list
- `tests/unit/test_residue_grep.py`
- Live canon files touched by the remediation:
  - `Vision/Starry-Lyfe_Vision_v7.1.md`
  - `Characters/{Adelia,Bina,Reina,Alicia}/*_v7.1.md`
  - `Characters/Bina/Bina_Malek_Knowledge_Stack.md`
  - `Characters/Reina/Reina_Torres_Knowledge_Stack.md`
  - `src/starry_lyfe/canon/characters.yaml`

#### Verification context

Independent checks run during audit:

- `python -m pytest tests/unit/test_residue_grep.py -q` → **PASS**
- Targeted `rg` over `src/`, `Characters/`, and `Vision/` for the Phase 0 residue tokens, with the same exclusions Claude Code documented, returned only the expected Appendix A references in `Vision/Starry-Lyfe_Vision_v7.1.md`
- Direct spot-checks confirm all four kernels now point to `Persona_Tier_Framework_v7.1.md`
- Direct spot-checks confirm:
  - Alicia's kernel now carries the canonical resident framing (`Characters/Alicia/Alicia_Marin_v7.1.md:36`)
  - Reina's kernel now says `Argentine consular rooms` (`Characters/Reina/Reina_Torres_v7.1.md:228`)
  - Bina and Reina knowledge-stack files now use `resident at the property but frequently away on consular operations` (`Characters/Bina/Bina_Malek_Knowledge_Stack.md:414`, `Characters/Reina/Reina_Torres_Knowledge_Stack.md:407`, `:425`)
- Direct Bina spot-check confirms the live canon stack is aligned on birthplace:
  - Vision no longer contains the stale `Canadian-born Assyrian` phrasing
  - kernel still says Urmia / Edmonton
  - `src/starry_lyfe/canon/characters.yaml` still says `birthplace: "Urmia, Iran"`

Full `pytest -q` is not a Phase 0 quality signal in this environment. The integration suite still requires a reachable PostgreSQL instance and errors during setup in `tests/integration/conftest.py:92`, which is orthogonal to this markdown/canon verification phase.

#### Executive assessment

Phase 0 is substantively in good shape.

I independently verified the remediated live files against the Phase 0 work items and did not find remaining production drift within the declared Phase 0 scope. AC1 through AC4 appear met in the repo state currently under audit.

The remaining defects are in the verification trail, not in the canon files themselves:

- the only automated regression Claude Code cites as "authoritative" does not cover the full AC1 surface
- the verification report still presents a stale pre-remediation verdict at the top, even though the addendum and the phase file state the opposite

No Critical or High findings.

#### Adversarial scenarios constructed

1. **Synthetic residue reintroduction in a non-exempt path.** If a token such as `Citadel Pair` or `Spanish consular` reappears in a live `Characters/` or non-Appendix `Vision/Starry-Lyfe_Vision_v7.1.md` line, the current path-aware grep pattern will surface it. I verified the negative case on the live tree: after exclusions, zero real hits remain.
2. **Kernel reference regression.** If any kernel regresses from `Persona_Tier_Framework_v7.1.md` back to `_v7.md`, the current residue test will not catch it because `_v7.md` is not in the drift token list. This adversarial scenario is live-proof that Work Item 2 still depends on manual or dedicated automated verification.
3. **False-negative phase reading from stale report state.** If a later reviewer reads only the top of `Docs/Phase_0_Verification_Report_2026-04-11.md`, they will conclude `NOT CLEAN` / `remediation pending` even though the phase file and §11 addendum say AC1-AC4 are met. This is a process-level adversarial scenario: the artifact can mislead a correct reviewer.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | Medium | The residue-grep test is not authoritative for AC1 because it only scans `src/`, not the full Phase 0 scope. | `tests/unit/test_residue_grep.py` explicitly says "Scans all files under src/" and `_scan_src_for_residue(src_dir)` only traverses `src_dir`, while Phase 0 AC1 covers `src/`, `Characters/`, `Vision/`, and `Docs/`. Step 2 and the verification report currently describe this test as the "authoritative signal" that AC1 is met. | Reword the Step 2 / verification-report claim to make the test a supporting `src/` regression only, or add a checked-in repo-wide verifier that covers the actual Phase 0 scope. |
| F2 | Low | The verification report still carries stale pre-remediation state at the top, which conflicts with the live audit-ready state recorded later in the same document. | `Docs/Phase_0_Verification_Report_2026-04-11.md` header still says `State: Verification complete, remediation pending...` and §1 still says `AC status: NOT CLEAN`, while §11 and Step 2 of this phase file state AC1-AC4 are met and the phase is ready for audit. | Collapse §11 into a final top-level verdict or revise the report header / §1 so the document reads as a final post-remediation artifact instead of a pre-remediation report with a corrective addendum appended later. |

#### Runtime probe summary

Phase 0 is a verification phase, so the live probes were canon checks rather than executable runtime probes:

- `tests/unit/test_residue_grep.py` passes for `src/`
- independent path-aware grep across `src/`, `Characters/`, and `Vision/` returns zero real hits after applying the approved exclusions
- all four kernels now reference `Persona_Tier_Framework_v7.1.md`
- Bina's Vision/kernel/YAML origin drift is resolved in the live files
- Alicia's resident-but-frequently-away framing is now present in the kernel and in the remediated Bina/Reina support files

#### Drift against specification

Against the master plan's actual Phase 0 work items, the live repository now satisfies the substantive canon-verification requirements:

- **Work Item 1:** zero real drift hits in production paths after exclusions
- **Work Item 2:** kernel pair names, surnames, §3 headings, and PTF references are aligned
- **Work Item 3:** Bina Vision/kernel drift no longer exists in the live files
- **Work Item 4:** YAML and kernels still align on the specified fields
- **Work Item 5:** stale Alicia residence framing is removed from the live production files Claude Code identified

The remaining drift is in the documentation of the verification process itself, not in the canon state the phase was supposed to clean.

#### Verified resolved

Confirmed working in the live repo state:

- zero real residue-token hits remain across `src/`, `Characters/`, and `Vision/` after applying the documented exclusions
- all four kernels reference `Persona_Tier_Framework_v7.1.md`
- the stale `Canadian-born Assyrian` Bina Vision phrasing is gone
- Alicia's resident framing is present in her kernel and consistently reflected in the remediated Bina/Reina support files
- the `Spanish consular` → `Argentine consular` correction is present in Reina's kernel

#### Recommended remediation order

1. **F1 first.** Tighten the claim around AC1 proof so the artifact does not overstate what the automated test actually covers.
2. **F2 second.** Rewrite the verification report into a single post-remediation state so future QA does not have to reconcile contradictory sections.

#### Gate recommendation

**PASS WITH MINOR FIXES**

Phase 0's canon-verification objective appears achieved in the live files under audit. Claude Code should remediate the two artifact-level findings above, then proceed to QA.

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete. 0 Critical, 0 High, 1 Medium, 1 Low. Live files satisfy AC1-AC4; minor remediation required on the Phase 0 verification artifacts. -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: COMPLETE — Path A, handed to Claude AI for QA]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code

### Remediation content

**Per-finding status table:**

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| F1 | Medium | **FIXED** | (this commit) | PHASE_0.md:181 reworded. The residue-grep test is now described as `src/`-only regression coverage, with the authoritative AC1 evidence being the four-row manual drift grep results table. A Phase A' follow-up item is queued to close the automation gap by adding a repo-wide residue verifier covering `src/ + Characters/ + Vision/` with the Phase 0 exclusion list. |
| F2 | Low | **FIXED** | (this commit) | `Docs/Phase_0_Verification_Report_2026-04-11.md` header and §1 opening now carry `[HISTORICAL — SUPERSEDED BY §11]` markers. The historical sections (§1–§10) are preserved as the audit trail of what the verification originally found pre-remediation; §11 is declared the authoritative final state. Header `State:` field updated from "Verification complete, remediation pending..." to "COMPLETE — all acceptance criteria MET after 10-commit remediation sequence (dc085d5–b322b1d); ready for Claude AI QA." |

**Push-backs:** none. Both findings were accepted on their face — they are accurate observations about artifact quality rather than disputes about the canon remediation. F1 correctly identifies a language imprecision in my Step 2 execution log; F2 correctly identifies a reader-experience problem in the verification report.

**Deferrals:** one Phase A' follow-up item queued from F1 — add a checked-in repo-wide residue verifier covering `src/ + Characters/ + Vision/` with the same exclusion list the Phase 0 manual pass used. This is the automation gap that F1 surfaced; deferring is appropriate because (a) the test infrastructure change is larger than the artifact-language fix F1 requires, and (b) it does not block Phase 0 shipping because the manual drift grep results table already provides authoritative evidence for the broader scope.

**Re-run drift grep delta:** no re-run needed — Step 4 remediation only touched markdown artifacts (`PHASE_0.md` Step 2 log language and `Phase_0_Verification_Report_2026-04-11.md` header/§1 markers), not production canon files. The drift-grep state from Step 2 is unchanged and still passes.

**Self-assessment:** Codex's Round 1 audit produced 0 Critical and 0 High findings. F1 (Medium) and F2 (Low) are both closed in this commit. No new architectural surface introduced. Phase 0 remediation is substantively complete.

### Path decision

**Chosen path: Path A (clean remediation).** The Step 4 changes are two markdown-only wording fixes in the Phase 0 verification artifacts. No production canon files touched, no tests modified, no schema or interface changes. No new architectural surface that would benefit from a Codex re-audit. Claude Code is handing directly to Claude AI for Step 5 QA per the AGENTS.md Path A protocol.

<!-- HANDSHAKE: Claude Code → Claude AI | Remediation Round 1 complete, Path A (clean). F1 and F2 both FIXED in this commit. Ready for Step 5 QA. -->

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
