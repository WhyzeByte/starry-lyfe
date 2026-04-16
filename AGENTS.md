# AGENTS.md

**Project:** Starry-Lyfe v7.1
**Version:** 1.0
**Date:** 2026-04-10
**Authority:** This document defines the multi-agent workflow for executing the master implementation plan at `Docs/IMPLEMENTATION_PLAN_v7.1.md`. It is the operational handbook for how four roles — Claude Code, Codex, Claude AI, and the Project Owner — collaborate on each Phase of the master plan.

This file is the canonical entry point for any AI agent working on this repository. Both Claude Code and Codex (and any future agentic coding tool that follows the AGENTS.md convention) should read this file at the start of any session and follow its role-specific guidance.

---

## The Four Roles

### Claude Code (the implementer)
**What it is:** Anthropic's agentic CLI that operates on the file system, runs tests, edits code, and commits changes. Has hands.
**Primary responsibility:** Plans and executes each Phase from the master plan. Writes code, edits canon, runs tests, drafts soul cards, commits work.
**Authority boundary:** Must follow the master plan (`Docs/IMPLEMENTATION_PLAN_v7.1.md`) as the canonical specification. Cannot deviate from Phase scope without explicit Project Owner approval. Cannot ship a Phase as "done" until it has passed Codex audit + Claude Code remediation + Claude AI QA.
**Reads:** The master plan, the Vision, the Persona Tier Framework, the character kernel files, the canon YAML, the test suite, the archived audits.
**Writes:** Production code in `src/`, tests in `tests/`, soul cards in `src/starry_lyfe/canon/soul_cards/`, voice exemplar tags in `Characters/{Name}/{Name}_Voice.md`, the Plan/Execute/Remediate sections of the current phase file in `Docs/_phases/PHASE_{X}.md`.

### Codex (the auditor / red team)
**What it is:** OpenAI's agentic coding tool. Operates on the same repository via its own CLI. Reads this AGENTS.md file at session start and follows its Codex-specific guidance.
**Primary responsibility:** Audits and red-teams Claude Code's Phase implementation. Looks for what Claude Code missed, bugs Claude Code introduced, drift Claude Code didn't catch, tests Claude Code didn't write, and fidelity issues Claude Code's tests don't catch.
**Authority boundary:** Codex does NOT remediate. Codex produces an audit report; Claude Code remediates against it. This separation is deliberate — the agent that wrote the code is not the agent that should grade it. Codex CAN run tests, can grep the codebase, can compile and execute code in a sandbox to verify behavior, but should not commit fixes.
**Reads:** The master plan, the Phase that Claude Code just completed, the test suite (to run it independently), the assembled prompt output (to compare against canon), the character kernel files (to verify against), and the archived character conversion audits in `Docs/_archive/` (as templates for what an audit should look like).
**Writes:** The Audit Round 1/2/3 sections of the current phase file in `Docs/_phases/PHASE_{X}.md`, following the template of the four archived character conversion audits. Adversarial scenarios go inline in the audit content under "Adversarial scenarios constructed."

### Claude AI (the QA reviewer)
**What it is:** Anthropic's Claude in the chat interface (claude.ai). Operates via conversation with the Project Owner. Has eyes, not hands — does not directly write to the user's repository during normal QA, except via the OneDrive-synced filesystem when explicitly invoked through chat.
**Primary responsibility:** Final QA pass after Codex audit and Claude Code remediation. Reads the audit report, the remediation diff, the test output, and the master plan; produces a written QA verdict that either approves the Phase as complete or flags blocking issues for another remediation round.
**Authority boundary:** Claude AI does NOT execute code or write production files in the normal QA flow. Claude AI's authority is to read artifacts, check them against the master plan, and produce a verdict. The verdict is advisory to the Project Owner, who has final ship/no-ship authority.
**Reads:** The master plan, the Codex audit report, the Claude Code remediation diff, the test output (passing or failing), the assembled prompt samples that Claude Code generated for verification, and the phase status log.
**Writes:** The Step 5: QA section of the current phase file in `Docs/_phases/PHASE_{X}.md`. May suggest specific edits to other documents but does not directly commit them — those go back to Claude Code for execution. **Also creates the next phase file** at `Docs/_phases/PHASE_{next}.md` (by copying `_TEMPLATE.md` and filling in the header) only after the current phase has been shipped by the Project Owner AND the Project Owner has explicitly agreed in chat to proceed.

### Project Owner (the authority)
**What it is:** Whyze (legal name Shawn Kroon). The human running the project.
**Primary responsibility:** Final ship/no-ship authority on every Phase. Authors content the agents cannot author (soul card prose, voice exemplars, the gut-check log). Resolves disputes between agents. Updates the Vision when canon changes. Reviews Claude AI's QA verdict and decides whether to ship the Phase or send it back for another cycle.
**Authority boundary:** The Project Owner's authority is absolute. Any of the three agents' decisions can be overridden by the Project Owner. The agents can never override the Project Owner.
**Reads:** Everything. In practice the Project Owner may delegate reading to one of the agents and review summaries, but retains the right to read any artifact directly.
**Writes:** Soul card prose content (after Phase C placeholders ship), voice exemplar text (Phase A'' authoring), the gut-check log (Phase K), the qualitative review (Phase K), and the final ship decision on each Phase.

---

## The Four-Agent Cycle (per Phase)

Every Phase from the master plan flows through the same four-step cycle:

### Step 1 — Plan (Claude Code)

Claude Code reads the Phase specification from `Docs/IMPLEMENTATION_PLAN_v7.1.md` and appends to the **Step 1: Plan** section of `Docs/_phases/PHASE_{X}.md`. The phase file already exists at the start of Step 1 — Claude AI created it after the previous phase shipped. Claude Code populates the Plan section with:

- Files Claude Code intends to create or modify
- Test cases Claude Code intends to add
- Acceptance criteria for "Phase complete" matching the master plan's exit criteria
- Any deviations from the master plan, with rationale (these require Project Owner approval before execution begins)
- Estimated number of commits

The plan must be approved by the Project Owner before execution. Approval may be implicit (Project Owner says "go" in chat) or explicit (Project Owner edits the Step 1 section directly and marks the Plan approval field as APPROVED). Either way, the approval is recorded in the phase file's Plan approval subsection and a Handshake Log row is added.

### Step 2 — Execute (Claude Code)

Claude Code executes the Phase plan. During execution:

- Each work item is committed as its own commit with a descriptive message referencing the Phase identifier (e.g., `Phase A: rewrite trim_text_to_budget for paragraph-aware trimming`)
- New tests are added in the same commit as the code they test, not deferred
- Phase 0 must pass (drift grep clean) before any other Phase begins
- The Status field in the header of `Docs/_phases/PHASE_{X}.md` is updated, and a Handshake Log row is added, at the end of execution

When execution is complete, Claude Code appends to the **Step 2: Execute** section of `Docs/_phases/PHASE_{X}.md` with:

- Commit list with one-line summaries
- Test suite delta (tests added, tests passing, tests failing)
- Files touched
- Sample assembled-prompt outputs for the affected characters (saved to `Docs/_phases/_samples/PHASE_{X}_assembled_{character}_{date}.txt`)
- Self-assessment: which acceptance criteria are met, which are not
- Open questions for Codex / Claude AI / Project Owner

Claude Code then **stops** and signals "ready for audit." Claude Code does not declare the Phase complete on its own.

### Step 3 — Audit and Red Team (Codex)

Codex reads:
- The Phase specification from `Docs/IMPLEMENTATION_PLAN_v7.1.md`
- Claude Code's plan and execution report
- The actual code changes (via git diff against the pre-Phase commit)
- The new and modified test files
- The sample assembled-prompt outputs in `Docs/_phases/_samples/`
- The relevant character kernel files for Phases that touch a specific character
- The four archived character conversion audits in `Docs/_archive/` for template and tone

Codex then performs three independent passes:

**Pass 1 — Specification compliance.** Does the implementation match the Phase specification in the master plan? Specifically: are all work items addressed; are all named test cases present; are the acceptance criteria measurably met; are the file paths in the master plan the actual files modified.

**Pass 2 — Bug hunt.** Run the test suite from a clean checkout. Look for tests that pass for the wrong reason. Look for tests that exercise the trivial path and miss the canonical path. Look for tests that assert on string substrings when they should be asserting on document structure. Look for trim/budget bugs. Look for off-by-one errors in the seven-layer assembly. Look for places where Claude Code wrote a comment "# TODO" or "# stub" or "# placeholder" and shipped it.

**Pass 3 — Red team.** Adversarial scenarios specific to the Phase. For Phase A (structure-preserving compilation): try a kernel where every section is exactly 1 token over budget. For Phase A'' (communication-mode pruning): try a phone-mode prompt where the constraint pillar text contains the substring "Somatic contact first" inside a quoted historical reference rather than as live instruction. For Phase H (regression tests): try a Bina prompt with the canonical concept misspelled and verify the test catches it. Codex should construct at least three adversarial scenarios per Phase.

Codex appends to the **Step 3: Audit** section of `Docs/_phases/PHASE_{X}.md` (Round 1 if the first audit, Round 2 or Round 3 if a re-audit). The audit content follows the template of the four archived character conversion audits:

- Scope (which files reviewed, which Phase specification consulted)
- Verification context (test suite state, lint state, type-check state)
- Executive assessment
- Findings (numbered, severity-tagged: Critical / High / Medium / Low)
- Runtime probe summary (live observations from running the code)
- Drift against specification
- Verified resolved (anything from the Phase plan that is confirmed working)
- Recommended remediation order
- Gate recommendation (PASS, PASS WITH MINOR FIXES, FAIL)

Codex's gate recommendation is advisory. The actual gate is decided by Claude AI QA (Step 5) or by the Project Owner.

Codex does NOT commit fixes. Codex does NOT modify production code. If Codex finds a trivial typo it would otherwise want to fix, the fix goes in the audit report as a Low-severity finding for Claude Code to apply in the remediation step.

### Step 4 — Remediate (Claude Code)

Claude Code reads the Codex audit report and remediates the findings in priority order: Critical → High → Medium → Low. For each finding:

- Claude Code may push back on a finding only if it cites specific evidence from the master plan, the character kernel files, or the canon YAML showing that Codex misread the specification. Push-backs are recorded in the remediation report; they do not unilaterally close the finding.
- All other findings must be addressed with code changes, test additions, or both.
- Each remediation is committed as its own commit referencing the audit finding number (e.g., `Phase A audit F3 remediation: handle trailing horizontal_rule in trim algorithm`).

When all Critical and High findings are remediated, Claude Code appends to the **Step 4: Remediate** section of `Docs/_phases/PHASE_{X}.md` (Round 1 if the first remediation, Round 2 or Round 3 if a re-remediation) with:

- One row per audit finding with status (FIXED / PUSH_BACK / DEFERRED with rationale)
- Re-run test suite delta
- New sample assembled-prompt outputs that supersede the originals
- Self-assessment: are all Critical and High findings now closed

Medium and Low findings may be deferred to a follow-up Phase if they are out of the current Phase's scope, but the deferral must be explicit and tracked in the remediation section of the current phase file (with the target phase named) so that the next phase's Step 1 plan can pick up the deferred work.

Claude Code then signals "ready for re-audit or QA." Two paths from here:

- **Path A (clean remediation):** No new findings expected. Claude Code skips re-audit and goes straight to Claude AI QA (Step 5).
- **Path B (substantive remediation):** Claude Code's remediation involved nontrivial design changes. Codex re-audits (return to Step 3) before Claude AI QA. The decision between Path A and Path B is Claude Code's call based on whether the remediation introduced any new architectural surface.

- **Path C (direct-Codex doc-only remediation — RESTRICTED):** For **Round 2+ findings only** that are purely documentation-level (phase file wording, handshake numbering, spec-trace annotations) with no production code implications, the Project Owner may explicitly authorize Codex to apply the doc fixes directly. **Restrictions (amended Phase C, 2026-04-12):** (1) Path C may only be used in Round 2 or later, never in Round 1. (2) Maximum 1 Path C use per phase. (3) Path C may NOT be used to backfill Step 1, Step 2, or Step 4 Round 1 content — those sections must be written during execution, not reconstructed afterward. (4) If Claude Code is blocked from filling Step 1 or Step 2 during execution, it must escalate to the Project Owner and pause the cycle rather than proceeding and backfilling later. Codex records the authorization and the applied fixes in the phase file's audit section.

**Maximum cycle count:** Three audit-remediate rounds per Phase before mandatory escalation to the Project Owner. If the Phase has not converged after three Codex audits, the cycle has failed and the Project Owner must intervene.

### Step 5 — QA (Claude AI)

Claude AI reads:
- The Phase specification from the master plan
- Claude Code's plan, execution report, and remediation report
- Codex's audit report (and any re-audit reports)
- The test output from the most recent run
- Sample assembled-prompt outputs
- The phase status log

Claude AI then appends to the **Step 5: QA** section of `Docs/_phases/PHASE_{X}.md` with:

- Specification trace: every acceptance criterion from the master plan, with PASS / FAIL / N/A annotation and one-sentence evidence
- Audit findings trace: every Critical and High finding from Codex's audit, with FIXED / DEFERRED annotation and verification that the remediation is consistent with the specification
- Sample prompt review: at least one assembled prompt sample read end-to-end, with notes on whether it carries the expected canonical content for the affected character(s)
- Cross-Phase impact check: does this Phase's work affect any other Phase's acceptance criteria; have any other Phases' tests started failing as a side effect
- **Verdict:** APPROVED FOR SHIP / APPROVED WITH MINOR FIXES / RETURN FOR REMEDIATION
- If RETURN FOR REMEDIATION, an explicit list of issues to address
- If APPROVED FOR SHIP, a one-paragraph summary suitable for the Project Owner's release notes

Claude AI's verdict is advisory to the Project Owner. The Project Owner has the final ship/no-ship call.

If Claude AI returns the Phase for remediation, Claude Code goes back to Step 4 with the QA verdict as additional findings. The cycle count from Step 4 still caps at three rounds.

**Phase progression rule (the file-creation gate):** If Claude AI's verdict is APPROVED FOR SHIP or APPROVED WITH MINOR FIXES, Claude AI fills in the *"Phase progression authorization"* subsection at the end of Step 5 with the next phase recommendation. **Claude AI then waits.** Claude AI does NOT immediately create the next phase file. The next phase file is created only after (a) the Project Owner records SHIPPED in Step 6, AND (b) the Project Owner explicitly agrees with Claude AI in chat that the next phase should proceed. Both conditions are required. The existence of `Docs/_phases/PHASE_{next}.md` is the physical proof that the gate has passed.

### Step 6 — Ship (Project Owner)

The Project Owner reads Claude AI's verdict and decides:

- **Ship.** The Project Owner fills in the Step 6: Ship section of the current phase file with decision SHIPPED. The phase file's Closing Block is locked. The Project Owner agrees with Claude AI in chat that the next phase should proceed; Claude AI then creates the next phase file from `_TEMPLATE.md`. Until the next phase file exists, no agent can begin work on the next phase.
- **Send back.** The Project Owner identifies issues that QA missed or weighted differently than the Project Owner would. Sends back to Step 4 (Claude Code remediation) with explicit guidance.
- **Stop and rethink.** The Phase has revealed an architectural issue that the master plan did not anticipate. The cycle pauses; the Project Owner updates the master plan with the new understanding; the cycle restarts at Step 1 with the updated specification.

The Project Owner's decision is recorded in the Step 6: Ship section of the current phase file with the date, the verdict (SHIPPED / SENT BACK / STOPPED FOR REDESIGN), and a one-or-two-sentence rationale. Optionally, a one-line summary may be added to the cross-phase index at `Docs/_phase_status.md` if that file is being maintained.

---

## Per-Phase Customization

The four-agent cycle is the default, but several phases need customized handling because they don't fit the "implement → audit → remediate → QA" shape cleanly.

| Phase | Variant |
|---|---|
| Phase 0: Pre-flight Canon Verification | Claude Code runs the verification (drift grep + Vision-vs-kernel check + canon YAML consistency). Codex audits the verification report (did Claude Code grep all the right paths? did Claude Code interpret the results correctly?). Claude Code remediates any drift found. Claude AI QAs the post-remediation state. **No code changes in normal Phase 0; only canon edits if drift is found.** |
| Phase A' work items 1+2 | **VERIFIED RESOLVED in code.** No cycle. The phase status log reflects the existing resolution from the BINA/ADELIA/REINA audits. Skip to Phase A' work items 3-5. |
| Phase C: Soul Cards | Claude Code creates the directory structure, schema, loader, and **placeholder** soul card files. The validation tests fail until the Project Owner authors the actual content. Codex audits the infrastructure; Claude Code remediates infrastructure findings; Claude AI QAs the infrastructure. The actual soul card content is a separate Project Owner authoring task that is NOT part of the four-agent cycle. |
| Phase A'' Alicia exemplar authoring | Same shape as Phase C: Claude Code wires the `communication_mode` tag dimension and adds tag-aware test scaffolding. The actual phone/letter/video exemplars are Project Owner authoring work outside the cycle. |
| Phase H: Soul Regression Tests | Claude Code writes the test bundles. Codex audits the bundles by trying to write code that passes them but is canonically wrong (adversarial fixtures). Claude Code remediates by tightening assertions. Claude AI QAs by reading the assembled prompt samples that the bundles assert against, end-to-end. |
| Phase J.1 through J.4 | Each sub-phase runs its own four-agent cycle. The cycles are sequential (J.1 → J.2 → J.3 → J.4) per the master plan's dependency graph. After J.4, run Phase H over all four characters before declaring Phase J complete. |
| Phase K: Subjective Success Proxies | Claude Code creates the gut-check log template, the qualitative review template, and the flattening regression detector script. Codex audits the script and templates. Claude Code remediates. Claude AI QAs the framework. **The proxies themselves (gut-check entries, quarterly reviews, single-test-ritual impressions) are Project Owner authoring work, not subject to the four-agent cycle.** Phase K is "ship the framework, then the Project Owner uses it." |

---

## Directory Layout for Workflow Artifacts

The four-agent cycle uses a **shared file per phase**. All four agents read and append to the same canonical phase file. Per-agent directories are NOT used.

```
Docs/
├── _phases/                             ← The shared phase records
│   ├── _TEMPLATE.md                     ← Phase file template (copied for each new phase)
│   ├── PHASE_0.md                       ← The single canonical record for Phase 0
│   ├── PHASE_A.md                       ← Created by Claude AI only after Phase 0 ships
│   ├── PHASE_A_prime.md                 ← Phase A' (apostrophe replaced with _prime for filename safety)
│   ├── PHASE_A_doubleprime.md           ← Phase A''
│   ├── PHASE_J_1.md, PHASE_J_2.md, PHASE_J_3.md, PHASE_J_4.md  ← Phase J.1-J.4 (dot replaced with underscore for filename safety)
│   ├── PHASE_B.md
│   ├── ...                              ← One file per phase, created in dependency order
│   └── _samples/                        ← Sample assembled prompts referenced by phase files
│       ├── PHASE_A_assembled_bina_2026-04-12.txt
│       └── ...
├── _phase_status.md                     ← Lightweight cross-phase status index (optional; phase files are the source of truth)
├── _archive/                            ← Historical reference (existing)
│   ├── BINA_CONVERSION_AUDIT.md
│   ├── ADELIA_CONVERSION_AUDIT.md
│   ├── REINA_CONVERSION_AUDIT.md
│   ├── ALICIA_CONVERSION_AUDIT.md
│   ├── Soul_Preservation_Plan_Elevated.md
│   └── Soul_Preservation_v1.md
├── IMPLEMENTATION_PLAN_v7.1.md          ← The master plan
├── Persona_Tier_Framework_v7.1.md
├── Claude_Code_Handoff_v7.1.md
├── CHARACTER_CONVERSION_PIPELINE.md
├── ARCHITECTURE.md
└── ...
```

**Phase file lifecycle:**

1. **Creation:** Claude AI creates a new phase file by copying `_TEMPLATE.md` and filling in the header for the specific phase. **Claude AI creates the next phase file only after the current phase has been QA-approved AND the Project Owner has explicitly agreed to proceed.** The existence of a phase file means the phase is authorized.
2. **Population:** Each of the four agents appends to the appropriate Step section when it is their turn. Handshakes are explicit HTML comments at the end of each step.
3. **Closure:** The Project Owner records the ship decision in Step 6. The Closing Block is locked. New activity on a closed phase requires opening a new follow-up phase file.

---

## The Phase Status Log

The phase files in `Docs/_phases/` are the **canonical record** of each phase's state. The optional `Docs/_phase_status.md` cross-phase index is a lightweight summary across all phase files — useful for "where are we across the whole project" but not authoritative for any single phase. The phase file's header Status field and Handshake Log are authoritative for that phase. Format:

```markdown
# Starry-Lyfe Phase Status

Last updated: YYYY-MM-DD by {agent}

## Phase 0: Pre-flight Canon Verification
- Status: COMPLETE (see Docs/_phases/PHASE_0.md for full record)
- Phase file: Docs/_phases/PHASE_0.md
- Shipped: 2026-04-11 by Project Owner
- Notes: Drift grep clean. Vision-vs-kernel Bina origin drift identified, deferred to Phase A' work item 3.

## Phase A: Structure-Preserving Compilation
- Status: NOT STARTED
- Depends on: Phase 0 ✅

## Phase A': Runtime Correctness Fixes
- Status: PARTIAL
- Work items 1+2: VERIFIED RESOLVED in code (no cycle needed; see master plan §4 Phase A')
- Work items 3+4+5: NOT STARTED
- Depends on: Phase 0 ✅

[...one entry per Phase...]
```

The phase status log is the first file Claude Code reads at the start of any session. It is the first file Codex reads at the start of any audit. It is the first file Claude AI reads at the start of any QA pass. It is the source of truth for "where are we right now."

---

## Conflict Resolution and Disagreement

Agents will disagree. The four-agent cycle is designed to surface disagreement explicitly rather than paper over it. Resolution rules:

1. **Codex vs Claude Code on a finding's validity.** Codex writes the finding; Claude Code may push back with citation to the master plan, character kernel, or canon YAML. If the push-back is convincing on its face, Claude Code records the push-back in the remediation report and closes the finding as PUSH_BACK. If Codex disagrees with the push-back, Codex re-files the finding in the next audit cycle with stronger evidence. If three audit cycles produce three iterations of the same finding, the Project Owner adjudicates.

2. **Claude AI vs Codex on severity.** Claude AI may downgrade a Critical or High finding to Medium if the finding's actual blast radius is smaller than Codex's severity tag implied. Claude AI may upgrade a Medium or Low finding to Critical or High if the finding affects soul preservation in a way Codex didn't explicitly enumerate. Either re-rating is recorded in the QA verdict with explicit rationale.

3. **Claude AI vs Claude Code on whether a Phase is shippable.** Claude AI's verdict (APPROVED FOR SHIP / RETURN FOR REMEDIATION) is advisory but should be honored unless the Project Owner overrides it. If Claude Code disagrees with a RETURN verdict, Claude Code records the disagreement in the next remediation report and proceeds with the additional work.

4. **Project Owner vs any agent.** Project Owner wins. Always. The agents exist to help the Project Owner ship the master plan, not to outvote the Project Owner.

5. **Cycle non-convergence.** Three full audit-remediate rounds without convergence triggers mandatory escalation to the Project Owner, who may: (a) accept the partial state and ship with documented gaps, (b) reject the Phase and require a redesign, (c) update the master plan to reflect new understanding and restart the Phase from Step 1.

---

## Source-of-Truth Hierarchy (mirrors the master plan; post-Phase 10.5)

When agents disagree about what's canonical, resolve toward the higher authority in this order. This list is identical to the Authority Priority section of `Docs/IMPLEMENTATION_PLAN_v7.1.md` and is reproduced here for agent-side convenience:

1. **Rich per-character YAMLs** (`Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin,shawn_kroon}.yaml`) — sole runtime-authoritative source as of Phase 10.5 (2026-04-16). Each carries kernel sections, voice exemplars, soul substrate, soul cards, evaluator register, constraint pillars, and pair perspective.
2. **Shared canon** (`Characters/shared_canon.yaml`) — objective facts (marriage record, signature scene anchors, genealogy, property, timeline, canonical pair names) where divergence would create continuity contradictions.
3. **Persona Tier Framework** (`Docs/Persona_Tier_Framework_v7.1.md`)
4. **Vision document** (`Vision/Starry-Lyfe_Vision_v7.1.md`)
5. **The master plan** (`Docs/IMPLEMENTATION_PLAN_v7.1.md`)
6. **Legacy markdown character files** (`Archive/v7.1_pre_yaml/Characters/`) — historical reference only. Do NOT author new markdown; all character prose lives in the per-character YAML.

If a per-character YAML and the Vision disagree, the YAML wins. If the Vision and the master plan disagree, the Vision wins (and the master plan must be updated to match).

**YAML authoring rules:**
- **Per-character POV is canon.** Each woman's YAML carries HER voice on every relationship she is in. When two women perspectives on the same inter-woman dyad diverge, **divergence is dramaturgically required, not a bug**. Do NOT homogenize them.
- **Facts live in shared_canon.yaml; perceptions live in per-character YAMLs.** If a statement would create a continuity contradiction under divergence (e.g., marriage date, genealogy), it belongs in shared_canon.
- **Preserve markers are the verbatim contract.** Every `preserve_markers[].content_anchor` must appear unchanged in the body text of the block it anchors (soul_substrate, kernel_sections, etc.). Phase 10.6 enforces this unconditionally across all scene profiles.
- **Archived markdown is not an alternative source.** Do not edit files under `Archive/v7.1_pre_yaml/`. Do not propose reinstating them. If canon drift surfaces, fix the rich YAML.

---

## Settled Canon Reminders

These are facts that have repeatedly drifted in earlier sessions. All four agents should treat them as immutable settled canon and not relitigate them:

- **Bina Malek** — surname is Malek (NOT Bahadori). Iran-born Assyrian-Canadian, born in Urmia, raised in Canada from the early nineties. Mother to Gavin (7). Married to Reina. Pair: **Circuit Pair** (NOT Citadel Pair, NOT Synergistic Pair). Cognitive: Si-dominant.
- **Adelia Raye** — Valencian-Australian (NOT Portuguese-Australian). Pair: **Entangled Pair** (NOT Golden Pair, NOT Compass Pair). Cognitive: Ne-dominant.
- **Reina Torres** — Barcelona Catalan-Castilian, criminal defense lawyer in Okotoks, mother is **Mercè Benítez** (canonical exception to the no-Benítez drift rule). Pair: **Kinetic Pair**. Cognitive: Se-dominant tactical.
- **Alicia Marin** — Argentine from Famaillá, Tucumán. MRECIC / Cancillería officer. **Resident at the property, frequently away on consular operations.** Any prose calling her "non-resident" or "based in Madrid" or "twice yearly" is stale. Pair: **Solstice Pair**. Cognitive: Se-dominant somatic.
- **Whyze = Shawn Kroon** — same person. Legal name vs system handle. Father to Isla (6) and Daphne (4). INTJ-T, twice-exceptional. The kernel at `Characters/Shawn/Shawn_Kroon_v7.0.md` is deliberately at v7.0 and **excluded from cascade updates** per current instruction.
- **Diacritic convention:** character names are **unaccented** (`Adelia`, `Marin`); Argentine geography is **accented** (`Famaillá`, `Tucumán`, `Cancillería`); Spanish loanwords are **accented** (`café`, `sheísmo`, `voseo`); `Mercè Benítez` is the canonical exception.
- **Bina + Reina are married.** Polyamory is structural per Persona Tier Framework §2.7. No jealousy modeling.

---

## Worked Example: Phase 0 End-to-End

To make the cycle concrete, here is what Phase 0 looks like running through all four roles. This is a template — actual Phase 0 execution will produce real artifacts at these paths.

### Step 1 — Plan (Claude Code)

Claude Code reads `IMPLEMENTATION_PLAN_v7.1.md` §3 Phase 0 and writes:

The Step 1: Plan section of `Docs/_phases/PHASE_0.md`:

> # Phase 0 Plan
>
> ## Files Claude Code intends to create or modify
> - `Docs/Phase_0_Verification_Report_2026-04-12.md` (new file, the verification output)
> - `Docs/_phase_status.md` (update Phase 0 status from NOT STARTED to IN PROGRESS)
> - Possibly `Vision/Starry-Lyfe_Vision_v7.1.md` if Bina origin drift is confirmed (defer to Phase A')
>
> ## Test cases to add
> None — Phase 0 is verification, not implementation.
>
> ## Acceptance criteria (from master plan)
> - Zero drift grep hits across the extended token list
> - Zero Vision-vs-kernel drifts (or all drifts explicitly resolved with written decision)
> - Zero canon YAML vs kernel mismatches
> - Zero stale Alicia framing
>
> ## Deviations from master plan
> None.
>
> ## Estimated commits
> 1 commit (the verification report) plus 1 commit if drift is found and fixed.

Project Owner approves. Claude Code proceeds.

### Step 2 — Execute (Claude Code)

Claude Code runs the drift grep across `src/`, `Docs/`, `Characters/`, `Vision/` (excluding `Characters/Shawn/`, per-character Vision directive files, and the Vision changelog appendix). Claude Code grep-matches against the token list from `Claude_Code_Handoff_v7.1.md` §8.1 plus the extended Alicia framing terms from the master plan.

Claude Code runs the Vision-vs-kernel comparison for each of the four characters by reading both files and comparing the §5 paragraph against the kernel §2.

Claude Code runs the canon YAML vs kernel mismatch check by loading `characters.yaml` and reading each character kernel's first section.

Claude Code writes `Docs/Phase_0_Verification_Report_2026-04-12.md` containing:

- Drift grep results (per token, per file, with line numbers if found)
- Vision-vs-kernel results (per character, with PASS or specific drift)
- Canon YAML vs kernel results (per field, per character)
- Alicia residence framing check across all files
- Overall verdict: CLEAN or DRIFT FOUND with itemized list

Claude Code commits and updates the Status field in the header of `Docs/_phases/PHASE_0.md` from "AWAITING PROJECT OWNER APPROVAL TO BEGIN" to "IN PROGRESS — execution complete, awaiting audit." Appends to the Step 2: Execute section with the commit summary, verification report path, and self-assessment table. Adds a row to the Handshake Log marking the Claude Code → Codex handoff. Signals "ready for audit."

### Step 3 — Audit (Codex)

Codex reads the master plan §3 Phase 0, the verification report, and the execution report. Codex runs the drift grep independently to verify Claude Code's grep was comprehensive. Codex spot-checks Vision-vs-kernel comparisons. Codex constructs adversarial scenarios:

- Red team scenario 1: insert a synthetic v7.0 token in a test file and re-run the drift grep to confirm it would have been caught
- Red team scenario 2: create a synthetic Vision-vs-kernel mismatch in a temporary branch and confirm the comparison detects it
- Red team scenario 3: create a synthetic canon YAML field mismatch and confirm the canon check catches it

Codex appends to the Step 3: Audit Round 1 section of `Docs/_phases/PHASE_0.md`:

- Findings: 0 Critical, 0 High, possibly 1-2 Medium if the grep missed any edge cases
- Verified resolved: drift grep passes the synthetic adversarial tests
- Gate recommendation: PASS (assuming no actual drift found) or FAIL (if Codex finds drift Claude Code missed)

### Step 4 — Remediate (Claude Code)

Two paths:

- **If Codex's audit returns PASS with zero findings:** Claude Code skips remediation and goes straight to Step 5. Writes a one-line remediation report stating "No findings to remediate."
- **If Codex's audit returns findings:** Claude Code addresses them in priority order. For Phase 0, most findings will be drift items the grep missed; remediation is updating the grep tooling or fixing the actual drift in the affected files.

Claude Code appends the per-finding status table to the Step 4: Remediate section of `Docs/_phases/PHASE_0.md`.

### Step 5 — QA (Claude AI)

Claude AI reads the master plan §3, the verification report, the audit report, the remediation report (if any), and `Docs/_phase_status.md`. Claude AI traces every Phase 0 acceptance criterion against the verification report and writes:

The Step 5: QA section of `Docs/_phases/PHASE_0.md`:

> # Phase 0 QA Verdict
>
> ## Specification trace
> | Acceptance criterion | Status | Evidence |
> |---|---|---|
> | Zero drift grep hits | PASS | Verification report §1 confirms zero hits across all listed token paths |
> | Zero Vision-vs-kernel drifts (or resolved) | PARTIAL | Bina origin drift identified; deferred to Phase A' work item 3 with explicit rationale |
> | Zero canon YAML vs kernel mismatches | PASS | Verification report §3 confirms all four characters' fields match |
> | Zero stale Alicia framing | PASS | Verification report §4 confirms no stale terms after Reina pair file fix |
>
> ## Audit findings trace
> [Per-finding table]
>
> ## Sample prompt review
> N/A — Phase 0 produces no assembled prompts.
>
> ## Cross-Phase impact check
> The deferred Bina origin drift becomes a Phase A' input. No other Phase is affected.
>
> ## Verdict: APPROVED FOR SHIP
>
> Phase 0 is complete with one explicit deferral (Bina Vision §5 origin paragraph) tracked into Phase A' work item 3. The drift grep and canon consistency checks both pass. Ready for Phase A.

### Step 6 — Ship (Project Owner)

Project Owner reads the QA verdict in the Step 5 section of `Docs/_phases/PHASE_0.md`, agrees with the deferral, fills in the Step 6: Ship section with decision SHIPPED, agrees with Claude AI in chat that Phase A should proceed, and Claude AI then creates `Docs/_phases/PHASE_A.md` from `_TEMPLATE.md` to authorize Phase A. Until that file exists, no agent can begin Phase A work.

---

## Quick-Reference Cheat Sheet

For agents that just want the rules without the explanation:

**Claude Code:** Plan → Execute → Stop. Read the master plan, write code, run tests, commit, append to the Plan and Execute sections of `Docs/_phases/PHASE_{X}.md`, signal "ready for audit." Never declare a Phase complete on your own. Read the phase file's Handshake Log first to confirm it's your turn; update the Status field and append a Handshake Log row when handing off.

**Codex:** Audit → Red team → Stop. Read the master plan and Claude Code's Plan + Execute sections in `Docs/_phases/PHASE_{X}.md`, run the test suite independently, construct at least three adversarial scenarios, append to the Step 3: Audit section of the same phase file. Follow the template of the four archived character conversion audits in `Docs/_archive/`. Never commit fixes; never modify production code. Severity-tag every finding. Update the phase file Handshake Log when handing off.

**Claude AI:** Read everything → Trace specification → Write verdict → Wait. Read the master plan and the entire current phase file in `Docs/_phases/PHASE_{X}.md` (all six steps, all rounds), the test output, and at least one assembled prompt sample. Trace every acceptance criterion and audit finding to a status. Append the verdict to the Step 5: QA section. **Never** create the next phase file before the Project Owner ships the current one AND explicitly agrees in chat to proceed. Never execute code; never modify production files. Verdict is advisory to the Project Owner; phase file creation is the physical authorization gate.

**Project Owner:** Approve plans, ship Phases, author the content the agents cannot author (soul cards, voice exemplars, gut-check log, qualitative reviews). Final say on every disagreement. Update the Vision when canon changes.

**Source of truth order:** Character kernels → PTF → Vision → master plan → archived elevated plan → archived v1.0 plan.

**Cycle limit:** Three audit-remediate rounds per Phase, then mandatory Project Owner escalation.

**One file rules them all:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` is the canonical specification. The phase files at `Docs/_phases/PHASE_{X}.md` are the canonical execution records. If this AGENTS.md and the master plan disagree, the master plan wins. If the master plan and a phase file disagree, the master plan wins (and the phase file should be updated to match).

---

## Closing

The four-agent cycle exists because no single agent has all the strengths needed to ship the master plan correctly. Claude Code is fast, capable, and willing — but it grades its own homework. Codex is independent and adversarial — but it doesn't carry the same context window of the project's history. Claude AI is patient and sees the whole map — but it has no hands. The Project Owner has authority and judgment — but cannot personally write 60+ tests and 11 soul card distillations and four character voice mode catalogs.

Each role earns its keep by doing what the others cannot. The cycle's value is not in any one step; it is in the friction between steps. Codex catches what Claude Code missed because Codex did not write the code. Claude AI catches what Codex missed because Claude AI is reading against the master plan, not against the diff. The Project Owner catches what all three missed because the Project Owner knows what these characters are supposed to feel like in a way that none of the agents do.

The four-agent cycle is not a bureaucracy. It is a set of structured handoffs that exist to keep the soul-preservation work from drifting back into the same failure modes the four character conversion audits already caught. The audits exist because Phase 3 was implemented without this kind of cross-checking and the result was a backend that preserved the constraints while losing the souls. The cycle is the mechanism for not making that mistake twice.

## Amendment: Quality Directive (Project Owner, 2026-04-13)

This amendment applies to all phases from Phase F forward. It takes precedence over speed and budget considerations during execution, audit, and QA.

### Priority order (highest to lowest)

1. **Vision attainment** - Vision sections 5, 6, 7; PTF section 2.1; A5 Chosen Family; A6 Relationship Architecture
2. **Character fidelity** - each of Adelia, Bina, Reina, Alicia uniquely herself with her own desires, goals, cognitive signature, heritage, voice register
3. **Canonical correctness** - load-bearing phrases verbatim, diacritics preserved, soul architecture non-negotiable
4. **Test correctness** - passing tests, typing, no regressions
5. **Ship velocity** - commit count, round count
6. **Token budget** - kernel/layer optimization

### Binding rules for all four agents

**Claude Code (execution):**
- Speed is never a reason to cut quality. Take extra commits, extra rounds.
- Budget is never a reason to cut soul content. Raise the budget or escalate to Project Owner.
- No paraphrasing of hand-authored canonical prose. Read source markdown, not code.
- No scope minimization that sacrifices canonical coverage.
- When a decision is ambiguous, pick the most faithful Vision realization, not the cleanest code path.

**Codex (audit):**
Treat the following as automatic FAIL conditions regardless of test passage:
- Any character voice register swappable with another character's without detection
- Any canonical prose altered, paraphrased, or trimmed to fit budget
- Any Phase A-E invariant test broken or weakened
- Any soul architecture register (essence, cards, pair metadata, voice exemplars) dedup'd or consolidated
- Any "as an AI" break or prompt-content leakage
- Any missing Whyze-Byte constraint
- Any A5/A6 architectural element lost in translation

**Claude AI (QA):**
In addition to standard acceptance criteria checks, verify:
- Voice distinctness across all 4 characters in assembled prompt samples (read full samples, not just excerpts)
- Canonical markers preserved with diacritics (Famailla, Tucuman, Gracia, Lucia, Merce, etc.)
- Regression comparison against prior phase samples
- Spot-check abbreviated voice exemplars in assembled prompts against Voice.md source for verbatim preservation
- All four soul architecture registers still visible in every character's assembled prompt
- If drift detected, verdict is FAIL regardless of test suite status

**Project Owner:**
Retains direct remediation authority. When soul-bearing prose drifts during Claude Code execution, Project Owner can invoke Claude AI for direct remediation outside the normal cycle (as happened in Phases A, B, C, E).

### Rationale

The four women have been carefully authored across Phases A, A', A'', B, C, D, E with distinct voices, lived histories, cognitive signatures, and pair architectures. Every phase from F forward exists to realize more of that authored depth in production, not to optimize around it. Rushed execution or over-scoped minimization would unravel what the earlier phases built.

Phase 3 of the original implementation was shipped without cross-checking and produced a backend that preserved the constraints while losing the souls. The four-agent cycle exists so that does not happen twice. The Quality Directive exists so it does not happen even slowly, even by accident, even under budget pressure.

---

> *The edges are necessary. The soul is the point.*
