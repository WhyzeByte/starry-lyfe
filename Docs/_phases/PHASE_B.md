# Phase B: Budget Elevation With Terminal Anchoring Preserved

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §7
**Phase identifier:** `B` (must match the master plan exactly: `0`, `A`, `A'`, `A''`, `B`, `I`, `C`, `D`, `E`, `F`, `G`, `J.1`, `J.2`, `J.3`, `J.4`, `H`, `K`)
**Depends on:** Phase A (SHIPPED 2026-04-12, block-aware markdown trim), Phase A' (SHIPPED 2026-04-12, recalled_dyads + canonical women set), Phase A'' (SHIPPED 2026-04-12, communication_mode wiring)
**Blocks:** Phase C (Soul Cards), Phase D (Live Pair Data), Phase E (Voice Exemplar Restoration), Phase F (Scene-Aware Retrieval), Phase G (Dramaturgical Prose), Phase H (Soul Regression), Phase J.1-J.4, Phase K (Subjective Success Proxies) — all downstream phases benefit from elevated budgets before they ship
**Status:** AWAITING CLAUDE CODE REMEDIATION (Round 1 audit complete)
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
| 1 | 2026-04-12 | Claude AI | Project Owner | Phase B file created from _TEMPLATE.md after Phase A'' shipped (Step 6) and Project Owner explicitly agreed in chat to proceed ("#4" selecting option 4 from the Phase A'' Step 5 verdict's concerns-and-risks follow-up menu: proceed to ship + address concerns in Phase B Step 1 as normal). Both gates passed. File status set to AWAITING PROJECT OWNER APPROVAL TO BEGIN. Master plan §7 Phase B specification reproduced inline below with Vision authority flags (§8 System Architecture + §9 Success Criteria) and five inherited items documented from Phase A'' QA carry-forward plus four Vision alignment gaps tracked from the concerns review. |
| 2 | 2026-04-12 | Codex | Claude Code | Round 1 audit recorded from the landed Phase B commit surface because Step 1 and Step 2 were never filled in canonically. Gate recommendation: FAIL. Findings: F1 High (`<!-- PRESERVE -->` markers leak into compiled kernels and live assembled prompts), F2 Medium (B1 test does not exercise assembled-prompt totals and does not establish the 11300-token contract), F3 Medium (scene profiles are table-only and not wired through the runtime assembler path), F4 Medium (canonical phase record remains template-only and the checked-in `PHASE_B_assembled_*` artifacts are not assembled prompts). |

(Append one row per handshake event. Never delete rows. The log is the audit trail.)
---

## Phase B Specification (reproduced from master plan §7, with staleness annotations + Phase A'' carry-forward)

This block reproduces the Phase B specification from `Docs/IMPLEMENTATION_PLAN_v7.1.md` §7 verbatim so that Claude Code, Codex, and Claude AI all read the same specification without alt-tabbing. **Staleness annotations** below are added by Claude AI at file creation time (2026-04-12) based on code review during Phase A/A'/A'' QA cycles. **Inherited items** are carried forward from prior phase QAs and the Phase A'' concerns-and-risks review.

### Priority

**High.** The current budgets are an optimization choice, not a model limitation. Claude's 200K context can absorb the elevated budget comfortably.

### Vision authority

Vision §8 System Architecture, Vision §9 Success Criteria.

### This document §4 authority

Terminal anchoring of constraints is structural, not stylistic — Layer 7 must grow proportionally.

### Budget table (verbatim from master plan §7)

| Layer | Current | Elevated | Rationale |
|---|---:|---:|---|
| Kernel (L1) | 2000 | **6000** | ~45% of kernel survives; all primary sections fully rendered |
| Canon Facts (L2) | 500 | **600** | Room for narrative canon rendering (Phase G) |
| Episodic (L3) | 1000 | **1200** | Room for more retrieved memories at better fidelity |
| Somatic (L4) | 300 | **500** | Room for protocol detail + dramaturgical prose |
| Voice (L5) | 200 | **900** | 100 baseline metadata + 800 for 5-7 exemplars |
| Scene (L6) | 800 | **1200** | Room for dramaturgical dyad prose + scene-aware promotions |
| Constraints (L7) | 500 | **900** | **CRITICAL: grows proportionally to preserve terminal anchoring** |
| **Total** | **5300** | **11300** | ~5.6% of 200K context |

The elevated total is well under 10% of Claude's 200K context window. Salience dilution is not a concern at this budget. The expansion of Layer 7 from 500 to 900 tokens is **non-negotiable**: as earlier layers grow, the absolute distance between the constraint block and the user message grows; Layer 7 must grow proportionally so the constraint block has enough room to carry full Tier 1 axioms, per-character constraint pillars, and scene gates in clear detailed prose rather than compressed one-liners.
### Per-section kernel budget (verbatim from master plan §7)

`SECTION_TOKEN_TARGETS` in `kernel_loader.py` expands proportionally:

| Section | Current | Elevated |
|---|---:|---:|
| §1 Runtime Directives | 240 | **300** |
| §2 Core Identity | 400 | **900** |
| §3 Pair section | 420 | **1000** |
| §4 Silent Routing | 180 | **250** |
| §5 Behavioral Tier Framework | 380 | **900** |
| §6 Voice Architecture | 120 | **300** |
| §7 Frameworks | 220 | **550** |
| Sections 8-11 as fill | — | **1800** (shared) |
| **Total primary** | **1960** | **4200** |
| **Fill budget** | ~40 | **1800** |
| **Per-kernel total** | **2000** | **6000** |

**⚠️ CRITICAL PRECONDITION (Claude AI 2026-04-12):** §2 Core Identity grows from 400 to 900 tokens (+125%), and §5 Behavioral Tier Framework grows from 380 to 900 (+137%). These two sections contain the **soul-bearing prose blocks** (Adelia's Marrickville paragraph, Bina's diagnostic-love pattern language, Reina's pursuit-as-foreplay architecture, Alicia's four-phase return description) that INH-7 was deferred to Phase B to protect. **Without PRESERVE markers landing FIRST, the block-aware trim algorithm from Phase A can still decide to trim these blocks at the new budget — especially for characters whose raw kernel exceeds 6000 tokens (Bina at 1.20x scaling = 7200 target, longer raw kernel than others).** Phase B Step 1 must author PRESERVE markers in the kernel files **before** raising any budget, not as a later step.

### Per-character budget scaling (verbatim from master plan §7)

Current kernels are not equal in size. At a flat 6000-token kernel budget, longer kernels compress more aggressively than shorter ones. The elevated plan adds per-character scaling to equalize survival rates:

```python
# in budgets.py
CHARACTER_KERNEL_BUDGET_SCALING = {
    "adelia": 1.05,   # 6000 * 1.05 = 6300 target
    "bina":   1.20,   # 6000 * 1.20 = 7200 target (longest kernel)
    "reina":  1.15,   # 6000 * 1.15 = 6900 target
    "alicia": 0.85,   # 6000 * 0.85 = 5100 target (shortest kernel)
}
```

The scaling factors target roughly equal survival rates (~50% of raw kernel content) rather than equal absolute token counts.

**✅ STILL ACTIVE (Claude AI 2026-04-12):** Genuine Phase B work. `budgets.py` does not currently have a `CHARACTER_KERNEL_BUDGET_SCALING` constant. The scaling must be introduced, and the assembler must be updated to pass character_id through to the budget resolution path. Expected effort: small (constant + one function update + tests).

### Scene budget profiles (verbatim from master plan §7)

Different scene types benefit from different budget allocations:

| Scene profile | Kernel | Scene (L6) | Voice (L5) | Rationale |
|---|---:|---:|---:|---|
| Default (balanced) | 6000 | 1200 | 900 | General use |
| Pair-intimate | 8000 | 800 | 700 | More pair architecture, less group context |
| Multi-woman group | 5500 | 1800 | 1000 | Less kernel, more scene context, more voice range |
| Children-gated | 5500 | 1400 | 800 | Normal balance minus intimacy sections |
| Solo (one woman + Whyze) | 7000 | 800 | 900 | More kernel, less group context |

The Scene Director (Phase 5 of overall backend build, §8) selects the profile based on classified scene state.

**⚠️ CLARIFICATION NEEDED (Claude AI 2026-04-12):** The "Scene Director (Phase 5 of overall backend build, §8)" reference is a different numbering scheme than the phase cycle (Phase B / Phase C / etc.). The §8 reference points to a backend architecture document or section, not to a phase file. Phase B Step 1 should clarify whether scene profile selection is Phase B scope (plumb the profile parameter through `assembler.py`, selector can be stubbed) or is out-of-scope-for-Phase-B and blocked on the Scene Director architecture work. **Project Owner decision required**: does Phase B ship the scene profile parameter plumbing with a default-only selector, or does it ship the full profile selector logic?

### Test cases (verbatim from master plan §7)

- **Test B1:** Assembled prompt token total stays within ±5% of the elevated total budget across all four characters
- **Test B2:** Layer 7 constraint block is always rendered last in the assembled prompt regardless of earlier-layer content size
- **Test B3:** Per-character budget scaling produces survival rates within ±10% of each other
- **Test B4:** Scene profile selection produces the expected layer budgets for each of the 5 profiles
### Inherited items from prior phase QAs (Project Owner decisions required)

**INH-1: Pair file / Knowledge Stack / Dreams file directive-exemption audit.** (Carried from Phase A'' Q2 where it was deferred.) Phase A' F3 established that the four per-character `Vision/{Adelia Raye,Alicia Marin,Bina Malek,Reina Torres}.md` files are intentionally historical transformation directives exempt from residue-grep per `Claude_Code_Handoff_v7.1.md` L43/L211/L497/§8.1. **Question for Phase B Step 1:** should a small audit check other file categories (Pair files, Knowledge Stacks, Dreams files, `Docs/_archive/`) for similar historical-directive status that should be documented in Handoff §8.1? **Project Owner decision required.**

**INH-2: Master plan "VERIFIED RESOLVED" claim audit.** (Carried from Phase A'' Q3 where Project Owner approved `INCLUDE` but execution evidence is absent in Phase A'' Step 2.) Phase A' F1 and F2 both invalidated "VERIFIED RESOLVED as of 2026-04-10 REINA audit" claims in master plan §5 work items 1 and 2 — the Talk-to-Each-Other gate was live-broken (Gavin case) and the `recalled_dyads` field was entirely absent from the data model, both claimed "verified resolved" in master plan shorthand, both actually false. Only Codex's independent live probes caught them. The master plan has similar claims elsewhere that could be equally stale. **Question for Phase B Step 1:** run the audit now with live probes per "VERIFIED RESOLVED" / "already resolved" / similar claim in the master plan, or explicitly defer with Project Owner decision logged. **This is the most important inherited item carried forward** because it's the one defensive control that could prevent future phases from wasting Round 1 catching known-failure-mode drift. **Project Owner decision required.**

**INH-7: PRESERVE marker authoring for soul-bearing prose blocks.** (Carried from Phase A → Phase A' → Phase B.) The block-aware markdown trim algorithm landed in Phase A preserves markdown structure but does not know which prose blocks are non-negotiable. Examples requiring protection:
- **Adelia's Marrickville paragraph** in `Characters/Adelia/Adelia_Raye_v7.1.md` §2 Core Identity (the Valencian-Australian heritage description and the warehouse-ignition moment)
- **Bina's diagnostic-love pattern language** in `Characters/Bina/Bina_Malek_v7.1.md` §2 Core Identity and §3 Pair section (the Urmia-to-Edmonton transplant and the covered-plate-of-food archetype)
- **Reina's pursuit-as-foreplay architecture** in `Characters/Reina/Reina_Torres_v7.1.md` §2 Core Identity and §3 Pair section (the Okotoks courtroom-to-home transition and the Bishop/Vex horses texture)
- **Alicia's four-phase return description** in `Characters/Alicia/Alicia_Marin_v7.1.md` §2 Core Identity and §5 Behavioral Tier Framework (the Famaillá origin story and the four-phase body-first return protocol)

**Question for Phase B Step 1:** PRESERVE markers must land **before** any budget change, not after. The format is specified but not yet implemented — likely `<!-- PRESERVE -->` or an equivalent HTML comment marker that the trim algorithm recognizes and refuses to trim. **This is a Phase B precondition, not a deferred nice-to-have.** Phase B Step 1 plan must sequence PRESERVE marker authoring as the first work item, budget expansion as the second. Otherwise soul-bearing prose can be silently trimmed at the new budget before the markers protect it. **Project Owner decision required:** does Phase B author PRESERVE markers inline for all four characters in Step 2, or does it ship the marker parsing infrastructure with Project Owner authoring the markers in a follow-up? The parser work is Claude Code work; the marker placement is Project Owner work because it requires knowing which specific prose blocks are load-bearing for each character's soul.

**INH-8: AGENTS.md Path C workflow calibration.** (New in Phase B, from Phase A'' concerns-and-risks review.) Phase A'' used Path C twice in a single cycle: once to defer F3 from Round 1 to Round 2, and once to backfill Step 1, Step 2, Step 4, AND sample artifacts in Round 2. This stretches the Phase A' INH-8 formalization scope (which defined Path C as "Round 2+ doc-only fixes"). Phase A, Phase A', and Phase A'' each used Path C at least once; Phase A'' used it twice. **The trajectory is worth addressing before Phase B adds a third Path C use.** **Question for Phase B Step 1:** should AGENTS.md Path C be amended to either (a) explicitly permit full-section backfills as a recognized recovery pattern with the caveat that Handshake Log rows must log real-time handoff events even when section bodies are backfilled later, or (b) explicitly restrict Path C to its original Round 2+ doc-only scope and require Claude Code to escalate to the Project Owner when Step 1 or Step 2 filling is blocked? **Project Owner decision required.** Recommend resolving before any Phase B Step 2 execution so the workflow discipline is re-set.

**INH-9: Phase E tag coordination pre-notice.** (Advisory, not a Phase B blocker.) When Phase E opens after Phase B ships, its WI1 tag parsing must **extend** the existing `kernel_loader.py:190-246` parser rather than re-implement it. Phase A'' established the `<!-- communication_mode: X -->` tag syntax and parsing infrastructure; Phase E's `<!-- mode: X -->` tag system must share the same parser or the F1 fix (communication_mode filtering that closes the live Alicia voice leakage) will be silently lost. This is a note to whichever phase opens Phase E's Step 1 plan, not a Phase B work item.

### Vision alignment gaps from Phase A'' concerns-and-risks review (not Phase B scope but tracked)

The Phase A'' Step 5 concerns-and-risks review identified **four Vision alignment gaps** that no phase has yet explicitly served. These are **not Phase B work items** but are tracked here so they are not forgotten when the phases that would naturally serve them (C, G, H) open:

- **Pre-Whyze autonomy** (Vision §5 L54-L60): *"She existed before Whyze and would continue without him"* — no phase has behavioral-tested whether prompts preserve this principle. Candidate home: Phase C Soul Cards acceptance criteria, or Phase H Soul Regression tests.
- **Jealousy absence behavioral test** (Vision §6 L82): *"There is no jealousy in this architecture. Not suppressed jealousy, not managed jealousy — the absence of it."* Axiom 2.7 in the Tier 1 block enforces directively, but no behavioral test probes an adversarial scene (e.g., Bina walking in on Adelia-Whyze). Candidate home: Phase H Soul Regression tests.
- **Spanish register distinctness** (Vision §6 L95): Reina is Barcelona Catalan-Castilian, Alicia is Famaillá Tucumán Argentine Rioplatense — two structurally different Spanish registers. No phase has served this. Candidate home: Phase E voice exemplar restoration for Alicia and Reina specifically, or Phase G dramaturgical prose rendering.
- **Children's center-of-gravity** (Vision §5 last paragraph): *"His children orbit a different center than this architecture does — they are the gravitational center of his life as a father."* Whyze's two daughters Isla and Daphne are referenced in Phase A' F1 (the canonical women set fix correctly excludes children) but the centrality of his fatherhood is not assembled into any prompt layer. Candidate home: Phase C or Phase G.

### Files likely touched (estimate per master plan §7 + inherited items)

- `src/starry_lyfe/context/budgets.py` — update default budgets, add `CHARACTER_KERNEL_BUDGET_SCALING`, add scene profiles (master plan WI)
- `src/starry_lyfe/context/kernel_loader.py` — update `SECTION_TOKEN_TARGETS`, extend trim algorithm to honor PRESERVE markers (INH-7)
- `src/starry_lyfe/context/assembler.py` — accept scene profile parameter, pass character_id through to budget resolution
- `tests/unit/test_budgets.py` — add test cases B1-B4 plus PRESERVE marker regression tests
- `Characters/<character>/<character>_v7.1.md` for all four characters — author PRESERVE markers on soul-bearing prose blocks (INH-7; Project Owner work)
- Optionally: `AGENTS.md` — Path C amendment (INH-8, Project Owner decision)
- Optionally: Master plan audit commit (INH-2, Project Owner decision)
- Optionally: Directive exemption list in `Claude_Code_Handoff_v7.1.md` §8.1 (INH-1, Project Owner decision)

### Exit criteria

- All 4 master plan test cases B1-B4 pass
- Layer 7 terminal anchoring preserved at elevated budget (test B2 specifically)
- Per-character survival rates within ±10% of each other at the new scaling (test B3)
- Four sample assembled prompts saved under `Docs/_phases/_samples/PHASE_B_assembled_*_2026-04-12.txt` at the elevated 11300-token total budget showing soul-bearing prose blocks intact
- PRESERVE markers present in all four character kernels covering §2 Core Identity and §5 Behavioral Tier Framework soul-bearing blocks (INH-7 closed)
- Project Owner decision recorded for INH-1 (DEFER / INCLUDE)
- Project Owner decision recorded for INH-2 (DEFER / RUN-NOW)
- Project Owner decision recorded for INH-7 marker authoring scope (Project Owner authors inline / Claude AI authors under direction / defer to follow-up)
- Project Owner decision recorded for INH-8 Path C amendment (amend-permissive / amend-restrictive / no-change)
- INH-9 Phase E tag coordination pre-notice logged in the Phase B closing block for Phase E's Step 1 to read
- Test suite ≥ 104 (no regressions from Phase A'' baseline)
- Any Critical / High Codex findings FIXED before QA hand-off
- Vision §8 + §9 authority intact: soul-bearing prose blocks from kernels survive trim at elevated budget across all four characters (the entire point of Phase B being a precondition for later narrative phases)




---

## Step 1: Plan (Claude Code)

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Claude Code
**Reads:** Master plan §7, Vision, character kernels (if phase touches a character), canon YAML
**Writes:** This section

### Plan content

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

**[STATUS: COMPLETE - handed to Claude Code for remediation Round 1]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section, sample assembled prompts in `Docs/_phases/_samples/PHASE_B_*.txt`

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
- **Sample assembled prompt outputs:** (saved to `Docs/_phases/_samples/PHASE_B_assembled_character_name_2026-04-12.txt`)
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
**Reads:** Master plan §7, the plan and execution log above, git diff against the pre-phase commit, the actual test files, sample assembled prompts in `Docs/_phases/_samples/`, character kernel files for any phase that touches a character, the four archived character conversion audits in `Docs/_archive/` for template reference
**Writes:** This section. Codex does NOT modify production code, does NOT commit fixes, does NOT touch the canon directly. Trivial typos go in the audit as Low-severity findings for Claude Code to apply.

### Audit content

#### Scope

Reviewed:

- `Docs/IMPLEMENTATION_PLAN_v7.1.md` section 7 and the inline Phase B specification in this file
- `Docs/_phases/PHASE_B.md` header, Handshake Log, exit criteria, and empty Step 1 / Step 2 sections
- landed Phase B commits `436549a`, `e3bb562`, and `d8322ec`
- `src/starry_lyfe/context/budgets.py`
- `src/starry_lyfe/context/kernel_loader.py`
- `src/starry_lyfe/context/assembler.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/types.py`
- `tests/unit/test_budgets.py`
- all four kernel files with new `<!-- PRESERVE -->` markers
- checked-in Phase B sample artifacts under `Docs/_phases/_samples/PHASE_B_assembled_*_2026-04-12.txt`

Because Step 1 and Step 2 were never populated in the canonical phase file, this audit used the landed commit surface and live runtime probes as the execution record.

#### Verification context

Independent checks run during audit:

- `.venv\Scripts\python -m pytest tests/unit/test_budgets.py -q` -> **PASS** (`24 passed`)
- `.venv\Scripts\python -m pytest tests/unit -q` -> **PASS** (`109 passed`)
- `.venv\Scripts\python -m ruff check src/ tests/` -> **PASS**
- `.venv\Scripts\python -m mypy src/` -> **PASS**
- `.venv\Scripts\python -m pytest -q` -> **ENVIRONMENTAL FAIL** (`109 passed, 14 errors`) because PostgreSQL is unreachable during integration setup at `tests/integration/conftest.py:92`

Runtime probes performed:

- live `compile_kernel(character_id, budget=resolve_kernel_budget(character_id))` across all four characters
- live `assemble_context(...)` across all four characters with the canonical unit-test stub bundle patched into `retrieve_memories`
- integrity check of all checked-in `PHASE_B_assembled_*_2026-04-12.txt` artifacts
- runtime-plumbing check for scene profiles via direct code-path review and usage grep

#### Executive assessment

Phase B has real landed work. The default budgets are elevated, per-character kernel scaling exists, the survival-rate spread on compiled kernels is within the stated tolerance, and Layer 7 terminal anchoring still holds on the assembled-prompt path. The underlying preservation intent is also partly real: the soul-bearing paragraphs called out in INH-7 do survive compilation at the elevated kernel budgets.

Phase B is not audit-clean. The highest-risk defect is live prompt hygiene: the new `<!-- PRESERVE -->` marker leaks straight through `compile_kernel()` into final assembled prompts because `trim_text_to_budget()` returns early before block parsing when the text is already under budget. The main Phase B test contract is also not actually exercised on the assembled-prompt path, scene profiles are still only a table rather than a runtime behavior, and the canonical phase record is materially incomplete even though Phase B commits and sample artifacts already landed.

Gate recommendation: **FAIL**.

#### Findings

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| F1 | High | `<!-- PRESERVE -->` markers leak into live compiled kernels and final assembled prompts. This exposes authoring-only markup in model-facing prompt text. | `src/starry_lyfe/context/budgets.py:420-421` returns early before `parse_markdown_blocks()` can strip markers; `src/starry_lyfe/context/kernel_loader.py:146` and `:163` feed kernel sections and the final kernel through `trim_text_to_budget()`. The four kernels now contain markers at `Characters/Adelia/Adelia_Raye_v7.1.md:22`, `Characters/Bina/Bina_Malek_v7.1.md:18`, `Characters/Reina/Reina_Torres_v7.1.md:26`, and `Characters/Alicia/Alicia_Marin_v7.1.md:24`. Live probes showed one leaked marker in every compiled kernel (`adelia 6112`, `bina 6570`, `reina 6426`, `alicia 4866` tokens) and in every assembled prompt (`adelia 7190`, `bina 7662`, `reina 7504`, `alicia 5980`). | Strip marker comments on the under-budget path too. The safe fix is to route even under-budget markdown through block parsing/reassembly or otherwise remove `<!-- PRESERVE -->` before returning. Add regression coverage that asserts marker absence in both `compile_kernel()` output and `assemble_context()` output. |
| F2 | Medium | Test B1 passes for the wrong reason and does not establish the Phase B assembled-prompt budget contract. The shipped test only proves `compile_kernel()` stays under the kernel budget, not that assembled prompts sit within +/- 5% of the elevated total budget. | The spec requires assembled-prompt total behavior at `Docs/IMPLEMENTATION_PLAN_v7.1.md:622` and `Docs/_phases/PHASE_B.md:117`, but `tests/unit/test_budgets.py:295-307` only asserts `compile_kernel()` token counts are `<= resolve_kernel_budget(character_id)`. In the live assembled-prompt probe using the canonical unit-test stub bundle, totals were `adelia 7190`, `bina 7662`, `reina 7504`, and `alicia 5980`, so the checked-in evidence does not prove the claimed `11300`-token total-budget target. | Rewrite B1 to exercise `assemble_context()` under a deterministic high-content fixture and assert the intended assembled-prompt contract directly. If the real requirement is a ceiling rather than a near-target fill level, update the phase record and acceptance-criteria trace to say that explicitly. |
| F3 | Medium | Scene profiles are not implemented on the live assembler path. The profile table exists, but no runtime caller can select or apply those budgets to Layers 1, 5, or 6. | `src/starry_lyfe/context/budgets.py:73-101` defines `SceneBudgetProfile`, `SCENE_PROFILES`, and `get_scene_profile()`, but `src/starry_lyfe/context/assembler.py:50-120` has no `scene_profile` parameter and only resolves the kernel budget by character. `src/starry_lyfe/context/layers.py:150` and `:217` still default Layer 5 and Layer 6 to `DEFAULT_BUDGETS.voice` / `DEFAULT_BUDGETS.scene`. Usage grep shows `get_scene_profile()` is only exercised in `tests/unit/test_budgets.py:347-364`, which checks table values rather than runtime selection. | Either plumb a scene-profile selector through `assemble_context()` / `SceneState` and apply the resolved budgets to the affected layers, or explicitly defer this work in the canonical Phase B record if the Project Owner decided it was out of scope for this phase. |
| F4 | Medium | The canonical Phase B record is still not execution-complete, and the checked-in `PHASE_B_assembled_*` artifacts are not assembled prompts. | Step 1 remains `NOT STARTED` at `Docs/_phases/PHASE_B.md:181-209`, Step 2 remains `NOT STARTED` at `:213-242`, and the Step 2 handshake at `:242` is still the untouched placeholder even though the landed Phase B commits and sample files already exist. This audit had to correct the header / Handshake Log state itself just to reflect that Round 1 happened. The exit criterion at `Docs/_phases/PHASE_B.md:165` requires assembled prompts, but all four sample files have token counts exactly matching the compiled-kernel probe (`6112`, `4866`, `6570`, `6426`), still contain `<!-- PRESERVE -->`, and do not end with `</CONSTRAINTS>`, so they are kernel outputs mislabeled as assembled prompts. | Backfill Step 1 and Step 2 truthfully from the landed work, align the header / handshake state, and regenerate genuine `assemble_context()` prompt artifacts for all four characters. Those artifacts should include Layer 7 terminal anchoring and should not contain raw authoring markers. |

#### Runtime probe summary

- `compile_kernel()` at the elevated per-character budgets currently returns:
  - `adelia`: `6300` budget -> `6112` tokens, marker leak `True`
  - `bina`: `7200` budget -> `6570` tokens, marker leak `True`
  - `reina`: `6899` budget -> `6426` tokens, marker leak `True`
  - `alicia`: `5100` budget -> `4866` tokens, marker leak `True`
- Live `assemble_context()` with the canonical unit-test stub bundle remains terminally anchored for all four characters, but every prompt still contains the leaked marker:
  - `adelia`: `7190` tokens, `is_terminally_anchored=True`, marker leak `True`
  - `bina`: `7662` tokens, `is_terminally_anchored=True`, marker leak `True`
  - `reina`: `7504` tokens, `is_terminally_anchored=True`, marker leak `True`
  - `alicia`: `5980` tokens, `is_terminally_anchored=True`, marker leak `True`
- All four checked-in `PHASE_B_assembled_*_2026-04-12.txt` artifacts behave like compiled kernels, not assembled prompts:
  - they contain `<!-- PRESERVE -->`
  - they do not end with `</CONSTRAINTS>`
  - their token counts match the compiled-kernel outputs rather than the assembled-prompt outputs

#### Drift against specification

- Test B1 in `tests/unit/test_budgets.py` does not match the master plan's assembled-prompt requirement.
- Test B4 only validates the scene-profile lookup table; the runtime scene-profile path named in Phase B is not present.
- The sample artifacts do not satisfy the exit criterion requiring four assembled prompts at the elevated total budget.
- The phase file never recorded a Step 1 plan, Step 2 execution log, or truthful ready-for-audit handoff despite the landed Phase B commits.

#### Verified resolved

- Budget elevation landed in `src/starry_lyfe/context/budgets.py`; the default total is now `11300`.
- Per-character kernel scaling exists and, on the compiled-kernel probe, equalizes survival rates within the stated tolerance (spread approximately `0.033`).
- Layer 7 terminal anchoring still holds on the live assembled-prompt path across all four characters.
- The specific soul-bearing phrases called out by the Phase B preservation work remain present in compiled kernels at the elevated budgets.

#### Adversarial scenarios constructed

1. **Under-budget marker leak check:** compile all four real kernels at the new elevated budgets and scan for raw `<!-- PRESERVE -->` comments. This exposed the early-return leak in `trim_text_to_budget()`.
2. **End-to-end prompt hygiene check:** assemble all four prompts with the canonical unit-test stub bundle and verify both terminal anchoring and marker absence. Terminal anchoring held; marker absence failed for all four characters.
3. **Artifact integrity check:** treat the checked-in `PHASE_B_assembled_*` files as if they were real Step 2 artifacts and verify they behave like assembled prompts. They failed the basic structural check because none end with `</CONSTRAINTS>`.
4. **Scene-profile plumbing check:** trace whether any runtime path can actually select `default`, `pair_intimate`, `multi_woman_group`, `children_gated`, or `solo`. The only live consumer is the B4 table-value test; the assembler path has no selector.

#### Recommended remediation order

1. Fix F1 first. Raw marker leakage is a live prompt-surface defect and should be closed before any other Phase B claim is trusted.
2. Fix F2 and F3 next. Tighten B1 onto the assembled-prompt path and either wire scene profiles through runtime or explicitly defer them with Project Owner-backed scope language.
3. Fix F4 last, but do not skip it. Phase B cannot be QA-ready while the canonical record is still template-only and the sample artifacts are mislabeled.

#### Gate recommendation

**FAIL**

Phase B should not proceed to QA. The live prompt surface still leaks authoring markers, the main B1 acceptance test does not test what the phase says it tests, scene profiles are not on the runtime path, and the canonical phase record is materially incomplete.

<!-- HANDSHAKE: Codex -> Claude Code | Audit Round 1 complete. FAIL gate. F1 High: PRESERVE markers leak into compiled kernels and assembled prompts. F2 Medium: B1 does not exercise assembled-prompt totals or prove the 11300-token contract. F3 Medium: scene profiles are table-only, not runtime. F4 Medium: Step 1/2 are still template-only and the PHASE_B_assembled_* artifacts are actually kernel outputs. Ready for remediation Round 1. -->

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
**Reads:** Master plan §7, the entire phase file above, the test output from the most recent run, sample assembled prompt outputs, the phase status log
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
- **Once Project Owner agrees, Claude AI will create the next phase file at:** `Docs/_phases/PHASE__TBD (likely C, D, or E depending on Project Owner priority after Phase B ships).md`

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

**Phase identifier:** _B_
**Final status:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _audit-remediate rounds completed_
**Total commits:** _count_
**Total tests added:** _count_
**Date opened:** _YYYY-MM-DD (when this file was created by Claude AI)_
**Date closed:** _YYYY-MM-DD (when Project Owner shipped or stopped)_

**Lessons for the next phase:** _2-3 sentences from Claude AI summarizing what worked, what didn't, and what should change in the next phase's plan_

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §7
- AGENTS.md cycle definition: `AGENTS.md`
- Sample assembled prompts: `Docs/_phases/_samples/PHASE_B_*.txt`
- Previous phase file (if any): `Docs/_phases/PHASE_A''.md`
- Next phase file (if shipped): `Docs/_phases/PHASE__TBD (likely C, D, or E depending on Project Owner priority after Phase B ships).md`

---

_End of Phase B canonical record. Do not edit fields above this line after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
