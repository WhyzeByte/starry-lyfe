# Phase 8: LLM Relationship Evaluator

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 (Model Routing) + §7 (Whyze-Byte Validation Pipeline) crosscut
**Phase identifier:** `8` (first phase to adhere to `Docs/_phases/_TEMPLATE.md` six-step structure from the outset — closes the Phase 7 AC-7.20 governance gap going forward)
**Depends on:** Phase 7 SEALED 2026-04-15 (HTTP service, evaluator fire-and-forget scheduling, BDOne wrapper, `DyadStateWhyze` row)
**Blocks:** Phase 9 (if any) — the DyadStateInternal LLM evaluator candidate identified as a separate future phase
**Status:** PLAN APPROVED; pre-execution
**Last touched:** 2026-04-15 by Claude Code (plan seeded)

---

## How to read this file

This is the **single canonical record** for Phase 8. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-15 | Project Owner (via chat) | Claude Code | Phase 8 scope authorized (LLM relationship evaluator); phase file created; ready for plan review |
| 2 | 2026-04-15 | Claude Code | Project Owner | Plan ready for review and approval (see §1 Step 1 Plan below) |

---

## Step 1: Plan (Claude Code)

**[STATUS: COMPLETE — PLAN READY]**
**Owner:** Claude Code
**Reads:** Master plan §6 + §7, Vision §6 (Talk-to-Each-Other Mandate / Relationship Architecture), CLAUDE.md §16 (±0.03 per-turn cap axiom), PHASE_7.md §15 Final Accept (carry-forward citation), the existing heuristic at `src/starry_lyfe/api/orchestration/relationship.py`, `src/starry_lyfe/db/models/dyad_state_whyze.py`, `src/starry_lyfe/dreams/llm.py` (BDOne + StubBDOne), the 16 existing cases in `tests/unit/api/test_relationship_evaluator.py`.

### Plan content

**Files Claude Code intends to create or modify:**

| File | Action | Scope |
|------|--------|-------|
| `src/starry_lyfe/api/orchestration/relationship.py` | Modify | Internals rewrite; public API unchanged |
| `src/starry_lyfe/api/orchestration/relationship_prompts.py` | **Create** | System prompt + Pydantic response schema + `build_eval_prompt` + `parse_eval_response` |
| `src/starry_lyfe/api/orchestration/__init__.py` | Modify | Export new helpers for testability |
| `src/starry_lyfe/api/config.py` | Modify | Add `relationship_eval_llm: bool = True`, `relationship_eval_max_tokens: int = 200`, `relationship_eval_temperature: float = 0.2` |
| `src/starry_lyfe/api/orchestration/post_turn.py` | Modify | Thread `settings` + `llm_client` into the fire-and-forget scheduling so `evaluate_and_update` can reach BDOne |
| `.env.example` | Modify | Document the 3 new env vars |
| `tests/unit/api/test_relationship_evaluator.py` | Modify | Extend existing 16-case suite; add LLM-path tests with StubBDOne |
| `tests/unit/api/test_relationship_prompts.py` | **Create** | Prompt build + parse coverage |
| `Docs/OPERATOR_GUIDE.md §14` | Modify | Document new env vars + heuristic fallback behavior |
| `Docs/CHANGELOG.md` | Modify | Phase 8 entry under [Unreleased] at ship time |
| `CLAUDE.md §19` | Modify | Phase 8 status transitions PLANNED → SHIPPED at ship time |
| `Docs/IMPLEMENTATION_PLAN_v7.1.md` | Modify | Phase 8 status bullet in the phase-by-phase list |

**Test cases Claude Code intends to add:**

In `tests/unit/api/test_relationship_prompts.py`:
- `test_build_eval_prompt_contains_character_id_and_state`
- `test_build_eval_prompt_escapes_response_text_safely`
- `test_parse_valid_json_returns_proposal`
- `test_parse_malformed_json_returns_none`
- `test_parse_missing_field_returns_none`
- `test_parse_out_of_range_value_clamps_at_boundary`
- `test_parse_non_numeric_value_returns_none`
- `test_parse_negative_repair_history_clamps_to_zero`

Extended in `tests/unit/api/test_relationship_evaluator.py`:
- `test_llm_path_applies_parsed_deltas_under_cap`
- `test_llm_path_clamps_deltas_above_cap`
- `test_llm_failure_falls_back_to_heuristic`
- `test_llm_malformed_response_falls_back_to_heuristic`
- `test_llm_toggle_false_uses_heuristic_directly`
- `test_circuit_open_falls_back_to_heuristic`

Existing 16 heuristic cases stay — the toggle path ensures they remain exercised.

**Acceptance criteria (mirror master plan exit criteria + Phase 7 §15 carry-forward contract):**

| AC | Description | Status |
|----|-------------|--------|
| AC-8.1 | `evaluate_and_update()` public signature unchanged (same kwargs, same return type, same fire-and-forget contract via `asyncio.create_task`) | PENDING |
| AC-8.2 | `DyadDeltaProposal` dataclass unchanged — field names + frozen dataclass semantics preserved | PENDING |
| AC-8.3 | ±0.03 per-dimension per-turn cap unchanged; `_clamp_delta` still the final safety gate; no path bypasses it | PENDING |
| AC-8.4 | LLM call lives in `relationship.py::evaluate_and_update` via `BDOne.complete()` with `max_tokens` + `temperature` from `ApiSettings`; fire-and-forget scheduling unaffected | PENDING |
| AC-8.5 | Structured output parsed via Pydantic `RelationshipEvalResponse` model; four float fields in [-1.0, 1.0]; out-of-range values clamp at boundary + log warning | PENDING |
| AC-8.6 | On ANY LLM failure (DreamsLLMError, parse failure, empty response, circuit open), fall back to `_propose_deltas()` — the heuristic path stays in the file as a named fallback, not dead code | PENDING |
| AC-8.7 | `STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM=false` toggle forces heuristic path (offline dev + test suite) | PENDING |
| AC-8.8 | System prompt in `relationship_prompts.py::RELATIONSHIP_EVAL_SYSTEM` includes per-character register notes (Adelia / Bina / Reina / Alicia) drawn from canonical constraint pillars in `IMPLEMENTATION_PLAN §7` | PENDING |
| AC-8.9 | Parser helper `parse_eval_response(text: str) -> DyadDeltaProposal \| None` returns `None` on malformed JSON, missing fields, non-numeric values; caller interprets None as "fall back" | PENDING |
| AC-8.10 | `repair_history` field clamps negative LLM outputs to 0.0 per spec (repair is positive-only; a single turn can never erase repair history) | PENDING |
| AC-8.11 | Test baseline ≥ 1025 passed (1015 + ≥10 new); ruff + mypy --strict clean across all source files | PENDING |
| AC-8.12 | `OPERATOR_GUIDE.md §14` documents the 3 new env vars + cost envelope (one extra BDOne round-trip per turn, ~300 tokens) + fallback semantics | PENDING |
| AC-8.13 | PHASE_8.md follows `_TEMPLATE.md` six-step structure with handshake log + Step 1-6 sections — closes the Phase 7 AC-7.20 governance gap | PENDING |
| AC-8.14 | No schema change (DyadStateWhyze unchanged); no Alembic migration required | PENDING |
| AC-8.15 | Structured log event emitted per evaluation: `llm_eval_parsed_proposal` on success, `llm_eval_fallback_to_heuristic` on fallback, with `character_id` + reason | PENDING |

**Deviations from the master plan:**

- **None.** The master plan does not specify the evaluator implementation strategy at this level of detail. This phase operationalizes the §7 pipeline's "relationship evaluator" component without contradicting any existing architectural commitment. The ±0.03 cap is preserved verbatim.

**Estimated commits:**

3 commits:
1. `feat(phase_8): relationship_prompts module + Pydantic schema + parser`
2. `feat(phase_8): evaluate_and_update rewires to LLM-primary with heuristic fallback`
3. `docs(phase_8): OPERATOR_GUIDE §14 + CHANGELOG + CLAUDE.md §19 + IMPLEMENTATION_PLAN §37 + PHASE_8.md §2-§6`

**Open questions for the Project Owner before execution:**

- **Q1:** Is OpenRouter (or whichever provider `STARRY_LYFE__EXT__SFW_PROVIDER_URL` points at) acceptable as the relationship evaluator's LLM, or should Phase 8 route evaluations through LM Studio's local model instead? (Local keeps costs zero and avoids external dependency; OpenRouter keeps capability higher.) **Proposed default:** use the existing `BDOneSettings.from_env()` — whatever the chat path uses is what the evaluator uses. Evaluator inherits, not forks.
- **Q2:** Should the evaluator read the *prior* response text (the focal character's turn) or the *user message* (Whyze's input that prompted the turn)? **Proposed default:** the focal character's response text, matching the existing heuristic semantics. Whyze's message context is implicit in the response and surfacing it would complicate the prompt without changing outcomes for well-behaved turns.
- **Q3:** Any objection to the `_propose_deltas` heuristic staying as a named fallback path rather than being removed? **Proposed default:** keep. It is the load-bearing degraded-mode path. Removing it would mean LLM outages leave the `DyadStateWhyze` row untouched — worse than applying a coarse but bounded update.

### Plan approval

**Project Owner approval:** APPROVED 2026-04-15 (approved via `C:\Users\Whyze\.claude\plans\declarative-exploring-stearns.md`; `ExitPlanMode` accepted).

<!-- HANDSHAKE: Claude Code → Project Owner | Plan ready for review and approval — approval already recorded via chat; proceeding to Step 2 on next invocation -->

---

## Step 2: Execute (Claude Code)

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED by Project Owner (done 2026-04-15)
**Reads:** The approved plan above, the master plan, the canon, the existing test suite
**Writes:** Production code in `src/`, tests in `tests/`, this section

### Execution log

_Claude Code fills in this subsection during and after execution. Required fields at the end of execution:_

- **Commits made (one row per commit):**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | _pending_ | _pending_ | _pending_ |

- **Test suite delta:**
  - Tests added: _list with names_
  - Tests passing: _1015 before → count after_
  - Tests failing: _list with names + reason, or "none"_
- **Self-assessment against acceptance criteria:** _per criterion: MET / NOT MET / PARTIAL with one-sentence evidence_
- **Open questions for Codex / Claude AI / Project Owner:** _list, or "none"_

<!-- HANDSHAKE: Claude Code → Codex | Execution complete, ready for audit (Round 1) [PENDING] -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Codex
**Prerequisite:** Step 2 execution complete with handshake to Codex

### Audit content

_Codex fills in this subsection. Required fields:_

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

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete, ready for remediation [PENDING] -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Step 3 audit complete with handshake to Claude Code

### Remediation content

_Claude Code fills in this subsection. Required fields:_

- **Per-finding status table** (one row per finding from the audit):

| Finding # | Severity | Status | Commit hash | Notes |
|---:|---|---|---|---|
| 1 | _from audit_ | FIXED / PUSH_BACK / DEFERRED | _pending_ | _rationale or deferral target_ |

- **Push-backs:** Each push-back must cite specific evidence from the master plan, character kernel files, or canon YAML.
- **Deferrals:** Each deferral must specify the target phase or follow-up work item.
- **Re-run test suite delta:** _tests passing before remediation → tests passing after_
- **Self-assessment:** _are all Critical and High findings now closed?_

### Path decision

_Claude Code must choose one of the two paths from AGENTS.md:_

- **Path A (clean remediation):** No new architectural surface introduced. Skip re-audit, hand directly to Claude AI QA.
- **Path B (substantive remediation):** Nontrivial design changes. Codex re-audits before Claude AI QA.

**Chosen path:** _A or B — pending_

<!-- HANDSHAKE: Claude Code → {Codex if Path B / Claude AI if Path A} | Remediation Round 1 complete, ready for {re-audit / QA} [PENDING] -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B)

**[STATUS: NOT STARTED]**

_Same structure as Round 1. Invoked only if Step 4 chose Path B._

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 2 complete [PENDING, conditional] -->

---

## Step 4': Remediate (Claude Code) — Round 2 (only if Round 2 audit fires)

**[STATUS: NOT STARTED]**

_Same structure as Round 1._

<!-- HANDSHAKE: Claude Code → {Codex / Claude AI} | Remediation Round 2 complete [PENDING, conditional] -->

---

## Step 3'': Audit (Codex) — Round 3 (final before escalation)

**[STATUS: NOT STARTED]**

_Same structure. Final audit round before mandatory escalation to Project Owner per AGENTS.md cycle limit._

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 3 complete [PENDING, conditional] -->

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: NOT STARTED]**

_If convergence is not reached after this round, Claude Code MUST escalate to the Project Owner instead of starting Round 4._

<!-- HANDSHAKE: Claude Code → {Project Owner if not converged / Claude AI if converged} | Remediation Round 3 complete [PENDING, conditional] -->

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**
**Owner:** Claude AI
**Prerequisite:** Step 4 (or 4', or 4'') remediation complete with handshake to Claude AI, AND Project Owner has brought the phase artifacts to Claude AI in chat

### QA verdict content

_Claude AI fills in this subsection. Required fields:_

- **Specification trace** (every AC-8.* above with PASS / FAIL / N/A + one-sentence evidence):

| Criterion | Status | Evidence |
|---|---|---|
| AC-8.1 | _pending_ | _pending_ |

- **Audit findings trace:**

| Finding # | Original severity | Final status | Evidence |
|---:|---|---|---|
| 1 | _from audit_ | FIXED / DEFERRED / PUSH_BACK_ACCEPTED | _one sentence_ |

- **Sample prompt review:** _Claude AI inspects at least one rendered `build_eval_prompt` output and confirms character register content is correct_
- **Cross-Phase impact check:** _any other Phase's tests started failing as a side effect_
- **Severity re-rating (if any):** _explicit rationale if Claude AI upgrades or downgrades a Codex finding_
- **Open questions for the Project Owner:** _list, or "none"_

### Verdict

**Verdict:** _APPROVED FOR SHIP / APPROVED WITH MINOR FIXES / RETURN FOR REMEDIATION — pending_

### Phase progression authorization

_Claude AI fills in only if verdict is APPROVED FOR SHIP or APPROVED WITH MINOR FIXES:_

- **Next phase recommendation:** _TBD (candidate: Phase 9 — DyadStateInternal LLM evaluator for inter-woman dyads, or operational phases per CLAUDE.md §19)_
- **Awaiting Project Owner agreement to proceed:** YES / NO
- **Once Project Owner agrees, Claude AI will create the next phase file at:** `Docs/_phases/PHASE_9.md`

<!-- HANDSHAKE: Claude AI → Project Owner | QA verdict ready, awaiting ship decision [PENDING] -->

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**
**Owner:** Project Owner (Whyze Byte / Shawn Kroon)
**Prerequisite:** Step 5 QA verdict ready
**Reads:** The entire phase file

### Ship decision

**Decision:** _SHIPPED / SENT BACK / STOPPED FOR REDESIGN — pending_

- **Date:** _pending_
- **Decided by:** Project Owner (Whyze)
- **Decision rationale:** _pending_

### If SHIPPED

- **Phase marked complete in master plan execution status:** YES
- **Agreement with Claude AI to proceed to next phase:** YES / NO
- **Next phase to begin:** _pending_
- **Next phase file to be created by Claude AI:** _pending_

<!-- HANDSHAKE: Project Owner → CLOSED | Phase shipped, work complete [PENDING] -->

---

## Closing Block (locked once shipped)

**Phase identifier:** 8
**Final status:** _pending — SHIPPED / SENT BACK / STOPPED FOR REDESIGN_
**Total cycle rounds:** _pending_
**Total commits:** _pending — estimate 3_
**Total tests added:** _pending — estimate ≥10_
**Date opened:** 2026-04-15 (phase file created)
**Date closed:** _pending_

**Lessons for the next phase:** _Claude AI will fill 2-3 sentences at ship: what worked, what didn't, what should change in Phase 9's plan._

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 + §7
- AGENTS.md cycle definition: `AGENTS.md`
- Planning artifact: `C:\Users\Whyze\.claude\plans\declarative-exploring-stearns.md`
- Previous phase file: `Docs/_phases/PHASE_7.md` (HTTP Service, SEALED 2026-04-15)
- Next phase file (if shipped): _pending — candidate `Docs/_phases/PHASE_9.md` (DyadStateInternal LLM evaluator)_

---

_End of Phase 8 canonical record. Do not edit fields above the Closing Block after Project Owner ships. New activity on this phase requires opening a new follow-up phase file._
