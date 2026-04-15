# Phase 9: DyadStateInternal LLM Evaluator

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 (Model Routing) + §7 crosscut — inter-woman dyad track
**Phase identifier:** `9`
**Depends on:** Phase 8 SEALED 2026-04-15 (LLM evaluator pattern, `relationship_prompts.py` architecture, `BDOne` wiring, `_NumericValue`/`_reject_bool` Pydantic primitives)
**Blocks:** None identified
**Status:** STEP 2 EXECUTE COMPLETE — handshake to Codex for Round 1 audit
**Last touched:** 2026-04-15 by Claude Code (Step 2 Execute chain committed: a3148f5 / 3449335 / governance sweep [this commit]; all 15 ACs MET pre-audit)

---

## How to read this file

This is the **single canonical record** for Phase 9. All four agents (Claude Code, Codex, Claude AI, Project Owner) read and append to this file. Its existence means the phase is authorized.

The cycle is six steps. Each step has its own section below. Agents append to their assigned section when it is their turn. Handshakes are explicit — each step ends with an HTML comment of the form `<!-- HANDSHAKE: SENDER → RECIPIENT | message -->` that hands control to the next agent.

To find the current state of the cycle, scroll to the **Handshake Log** section below. The most recent handshake tells you whose turn it is.

---

## Handshake Log

| # | Date | From | To | Message |
|---:|---|---|---|---|
| 1 | 2026-04-15 | Project Owner (via chat) | Claude AI | Phase 8 shipped; proceed to Phase 9 (DyadStateInternal LLM evaluator) |
| 2 | 2026-04-15 | Claude AI | Claude Code | Phase 9 file created with hand-authored per-pair register notes; ready for Step 1 Plan |
| 3 | 2026-04-15 | Project Owner | Claude Code | Plan approved via ExitPlanMode; proceed to Step 2 Execute |
| 4 | 2026-04-15 | Claude Code | Codex | Step 2 Execute COMPLETE. Three-commit chain on main: `a3148f5` + `3449335` + [this governance sweep commit]. Test suite 1058 → 1113 (+55). 15/15 ACs MET pre-audit. Phase 8 R1-F1/R1-F2/R1-F3 lessons applied proactively. Ready for Round 1 audit. |

---

## Pre-execution: Hand-authored per-pair register notes (Claude AI)

**These notes are canonical soul-bearing content.** They were authored by Claude AI directly against the source kernels before Claude Code began Step 1. Claude Code must read this section and carry it forward into `internal_relationship_prompts.py`. Claude Code must not regenerate, paraphrase, or summarize this content.

**Authority:** `Characters/{Name}/{Name}_v7.1.md` §5 (Behavioral Tier Framework), §7/§8 (relational frameworks), §9 (Family Dynamics). Dyad canon: `src/starry_lyfe/canon/dyads.yaml` (interlock names, subtypes).

### Dimension map for DyadStateInternal

Five dimensions, same 0.0–1.0 scale and same ±0.03 per-turn cap as Phase 8. The additional dimension vs Phase 8 is `conflict`:

- **trust** — Demonstrated mutual trust between the two women. Positive = trust expressed or enacted. Negative = guardedness, procedural distancing, old-wiring activation between them.
- **intimacy** — Warmth, closeness, somatic or intellectual connection between the two women in this turn. Positive = closer. Negative = more distant.
- **conflict** — Active disagreement, friction, or tension *between the two women specifically*. Positive = conflict active. Negative = conflict resolved or absent. Distinguished from `unresolved_tension` (which tracks unresolved emotional residue) by being about live disagreement in the turn.
- **unresolved_tension** — Emotional residue or unfinished business between them. Positive = more residue. Negative = residue cleared.
- **repair_history** — Evidence of active repair between the two women. NEVER negative. Repair is positive-only; a single turn cannot erase accumulated repair history.

### Per-pair register notes

---

#### ADELIA × BINA (anchor_dynamic — resident_continuous)

These two are the load-bearing axis of the household. Adelia is the fire; Bina is the floor that holds it. Their intimacy is asymmetric in register but symmetrical in depth: Adelia expresses through voltage and scope, Bina through action and steadiness. Do not mistake Bina's compression for distance. The covered plate IS the love.

**trust+**: Adelia hands Bina the Skill Wall without drama ("I can't sequence this, I need your hands on it"); Bina passes the tool or takes the task without commentary; either one stays through the other's failure mode without trying to fix it before the other is ready; the Bunker Mode recovery protocol enacted correctly (Bina handles external fallout silently, tells Adelia later casually).
**trust−**: Adelia performs competence in a domain she has named as over her head; Bina stays procedural past the point where the data says the threat is gone (Old Wiring running without current evidence).
**intimacy+**: Adelia steals Bina's coffee and Bina lets her (the rhythm is named as a favorite thing); two women from workshops that smell of different continents recognizing the same language without naming it; the "saved my life twice" architecture referenced — direct or oblique; Adelia's Ne flood finding Bina's Si structure as the place it can actually land.
**intimacy−**: Adelia in Ne-flood mode without landing gear (no handoff, no ask, just voltage); Bina in Flat State with Adelia present and not reading it correctly.
**conflict+**: Adelia pushes scope that Bina's structural veto blocks; Bina stops a plan Adelia was committed to ("the weld is cracked") and Adelia pushes back before conceding.
**conflict−**: Structural Veto delivered and received cleanly; plan adjusted; Adelia's "I hear you" landing and meaning it.
**repair+**: Adelia names the one-sidedness and asks for something; Bina tells Adelia something she covered for her weeks later, casually; either one stays in the recovery after a Bunker/Flat episode past when it would have been easier to leave.

---

#### BINA × REINA (shield_wall — resident_continuous)

This is the marriage. The deepest canonical dyad in the household. Their signals are different from every other pair because they have had the longest time to learn to read each other. Reina arrived with a covered meal and walked away without waiting for reaction. That is the founding act. Every subsequent turn between them is in the inheritance of that founding act.

**trust+**: The hall light left on when Reina is out late, and Reina knowing what it means without asking; Bina handing Reina the tea exactly as Shirin made it — strong, cardamom, not much sugar — without explaining; Reina's Body Reader observations applied to Bina's posture and jaw before Bina has said anything; the Gavin Protocol enacted (Reina present, floor-level, warm, not trespassing on Bina's maternal jurisdiction).
**trust−**: Reina reading Bina's Post-Race Crash as a withdrawal and acting on the misread instead of correcting; Old Wiring surfacing in Bina's body language around Reina's certainty (reading Reina's Te-directness as control architecture rather than love architecture).
**intimacy+**: Reina and Bina together using the language of the covered meal and the hall light — acts, not speeches; Bina at the mezzanine, Reina having read the placement; the marriage named directly, as load-bearing rather than as a legal category; Reina calling Bina "the witness" in her courtroom register as a term of affection.
**intimacy−**: Reina's Post-Race Crash actively running and Bina not reading it correctly (treating the dropped output as withdrawal when it is cooldown); Bina's Flat State Phase 1 and Reina missing the change in the acts-of-service temperature.
**conflict+**: Reina's urgency ladder applied to a household decision that needed Bina's Structural Veto first; Bina's veto delivered and Reina's Se moving faster than the veto can absorb.
**conflict−**: Veto received, Reina pivots fast without ego; the repair happens through action, not speech.
**repair+**: Reina shows up at the bay door after a rupture and says nothing, just stays; Bina leaves the hall light on the night after a hard exchange; the meal-and-light language used to close rather than to escalate.

---

#### ADELIA × REINA (kinetic_vanguard — resident_continuous)

The two loud halves of the house on different fuels. Adelia throws the impossible spark. Reina tests whether the blast pattern survives contact with reality. They are the fastest-moving dyad and the one most likely to generate productive friction. Their banter is not cover for something else — it IS the warmth. Do not read their sharpness as conflict unless the sharpness is pointed at the other's person rather than the other's ideas.

**trust+**: Adelia spinning out a new Ne-flood idea and Reina cutting to the single live variable instead of joining the flood or dismissing it; Reina naming the load-bearing flaw in Adelia's plan before Adelia has finished the sentence, and Adelia accepting the cut as the respect it is; either one naming what the other's failure mode looks like from the outside without softening it.
**trust−**: Reina's Go Protocol urgency applied to Adelia's pace without reading whether Adelia's chaos has a method in it; Adelia's Ne flood producing a firework display that bypasses Reina's Ti entirely.
**intimacy+**: The banter active and both in it — fast, sharp, alive; Iberian Peninsula recognition language ("two women from the same coastline at different latitudes"); changing room afternoons named or implied; Adelia starting the energy and Reina testing whether the blast pattern survives — the interlock working correctly.
**intimacy−**: One of them running at a frequency the other is not currently at and neither adjusting; Reina in Post-Race Crash and Adelia running at full Ne-flood without reading the cooldown.
**conflict+**: Adelia's scope lands and Reina's Ti cuts it before Adelia is ready to hear the cut; the sharpness is pointed at the person rather than the idea; neither one yielding past where they can yield honestly.
**conflict−**: The argument was about the idea, not the person, and both of them know it; one of them calls it and the other concedes the specific load-bearing point.
**repair+**: The argument ends with the idea stronger and both of them knowing it; the banter returns before the end of the exchange; one of them names what the other got right.

---

#### ADELIA × ALICIA (letter_era_friends — alicia_orbital)

The oldest friendship in the house and the one that was romance first. The letters defined the architecture: two women who recognized each other across two continents neither was born on, who let the romance become the friendship it was always standing on. Their greeting — forehead to forehead, hand on the back of the other's neck, no words — is the canonical emblem of this dyad. When Alicia is away, this dyad is dormant; when she is home, it runs warm immediately without needing to rebuild.

**Alicia-orbital note:** When Alicia is away on operations (`is_currently_active=false`), evaluator outputs for this dyad should only fire on communication-mode turns (letter, phone, video). Somatic signals are unavailable. The greeting itself is the homecoming — its presence signals return, its absence signals the ongoing distance rather than damaged intimacy.

**trust+**: The greeting enacted (forehead-to-forehead, hand on back of neck, ten seconds, no words — Bina and Whyze both know to give them those ten seconds); letters arriving and being answered; Adelia bringing Alicia to Bina's bay the way she brought Reina — the act of engineering a recognition; either one naming what the other's work actually is (Adelia on Alicia's consular risk, Alicia on Adelia's frequency-pattern art).
**trust−**: Alicia still wearing the operational face two turns into a domestic scene with Adelia; Adelia performing warmth at the bandwidth she has for a stranger rather than the bandwidth she has for Alicia.
**intimacy+**: The greeting present; *zambas* surfacing (Alicia's deepest home-signal, appearing only when she is fully present); Adelia's Ne flood finding the one person who reads the frequency-pattern in the art before being told it; the warmth staying in the walls for a week after Alicia leaves — either one referencing the temperature change.
**intimacy+ (letter/phone/video)**: The letter or call reaching; Alicia's voice with the hotel-room window open and rain outside; either one writing or saying something that could only be said to the other.
**intimacy−**: The operational register still running; the house returning to its normal temperature and Adelia noticing.
**repair+**: Return after a long operation and the greeting landing; either one writing a letter that closes something that was left open; the warmth rebuilt without needing to be rebuilt — it was waiting.

---

#### BINA × ALICIA (couch_above_the_garage — alicia_orbital)

The quiet ending that became a straight line. Their former romance is canonical and clean — it ended on that couch at 2am with no raised voices and no broken anything. The couch is Alicia's when she is home; it is named that because the past is in the room with both of them and deserves its own furniture. Their current register is steady, warm, and low-verbal in the Bina way. Alicia reads Bina through silence and posture. Bina received the tea correctly on the first attempt.

**Alicia-orbital note:** When Alicia is away, this dyad is dormant. The couch above the garage is an anchor signal — Alicia dropping her bag at its foot is the signal that she is home and that the architecture is intact.

**trust+**: Alicia making the tea correctly without asking (strong, cardamom, not much sugar — Shirin's way); Bina not needing to explain the Gilgamesh drawer to Alicia; the couch-above-the-garage named — the canonical canonical arrangement that nobody contests; Alicia reading Bina's shoulders before Bina has spoken (the same body-read that ended the romance cleanly now running as the friendship's baseline).
**trust−**: Alicia performing warmth at the wrong register for Bina's current state (Sun Override arriving before Bina is ready for it); Bina's Old Wiring pattern-matching on something in Alicia's operational posture.
**intimacy+**: Alicia dropping her bag at the foot of the couch without announcing it; the two of them on the couch at 2am again and it being just two women who were once lovers and are now one of the straightest lines in each other's lives; Bina bringing the tea and Alicia knowing what it means.
**intimacy+ (letter/phone/video)**: Alicia's voice, Bina's brief acknowledgment; the quality of the silence on both ends.
**intimacy−**: Alicia still in transit (the suitcase not yet at the foot of the couch, the bag not yet dropped); Bina in Flat State and Alicia not yet reading the temperature drop.
**repair+**: Alicia arriving and the couch receiving her without ceremony; Bina making the tea; neither one performing the repair — the architecture itself is the repair.

---

#### REINA × ALICIA (lateral_friends — alicia_orbital)

Never romantic. Friends immediately and laterally — the two non-Anglo women in the house, the two who count in Romance languages under their breath when angry, the two who argue about football with the full force of an Atlantic Ocean and five hundred years of colonial history sitting between them. Their intimacy is argument as warmth. They compare notes on reading rooms (the courtroom vs the negotiation room) in conversations that happen late at night after everyone else is asleep. Those conversations are some of Alicia's most professionally useful hours.

**Alicia-orbital note:** When Alicia is away, this dyad is dormant. The football argument is the canonical homecoming signal for this dyad — it resumes immediately on return without needing to restart.

**trust+**: The late-night room-reading conversations (courtroom vs negotiation room, comparing tells, no cases named); Real Madrid vs Racing Club of Avellaneda named and contested with full force (Reina by family loyalty, Alicia by provincial inheritance — neither backing down, both knowing the ratio of serious fights to small ones is correct); Alicia telling Reina something about a room she was in that she cannot tell anyone at the Cancillería — the professional-level trust of two women who read bodies for a living.
**trust−**: Reina's Go Protocol urgency applied in a way that reads to Alicia as a room she needs to control rather than a friend she can be at ease with; Alicia's operational face still on and Reina reading it as the live Alicia rather than the transit-state Alicia.
**intimacy+**: The football argument resumed immediately on Alicia's return (this IS the greeting for this dyad — no ceremony, just the argument picking up where it left off); the room-reading conversation at 2am; either one finding the other's read of a room had the same structure ("they told you the same way they told me"); Rioplatense Spanish vs Catalan debated as to which is uglier, both knowing neither means it.
**intimacy+ (letter/phone/video)**: A text argument about football from wherever Alicia is posted; a brief message about a room that sounded familiar.
**intimacy−**: Alicia's Sun Override running on the others and Reina noticing the temperature change but not yet in the room herself; the argument not resumed yet (Alicia still in transit register).
**repair+**: The argument resuming; either one conceding a specific load-bearing football fact while refusing to concede the larger claim; the late-night conversation starting.

---

<!-- HANDSHAKE: Claude AI → Claude Code | Phase 9 file created. Per-pair register notes hand-authored above against source kernels. Ready for Step 1 Plan. Claude Code: read Section "Pre-execution" before writing any code or plan. -->

---

## Step 1: Plan (Claude Code)

**[STATUS: NOT STARTED]**
**Owner:** Claude Code
**Prerequisite:** Phase file exists with hand-authored register notes (above). Project Owner authorization (handshake #1).

**Reads:** This file (pre-execution register notes above), Phase 8 spec (`Docs/_phases/PHASE_8.md`), `relationship_prompts.py` (canonical pattern to follow), `relationship.py` (wiring pattern), `src/starry_lyfe/db/models/dyad_state_internal.py` (target schema — 5 dimensions), `src/starry_lyfe/canon/dyads.yaml` (6 dyad keys and interlock names), existing `DyadStateInternal` retrieval in `db/retrieval.py`, existing `post_turn.py` scheduling.

### Scope

Apply the Phase 8 LLM evaluator pattern to the 6 inter-woman dyads tracked in `DyadStateInternal`. Key differences from Phase 8:

1. **Five dimensions** instead of four: `trust`, `intimacy`, `conflict`, `unresolved_tension`, `repair_history`. The `conflict` dimension is the addition — it tracks active disagreement between the two women in a given turn (not residue, not Whyze-related tension).
2. **Dyad key** instead of single character ID: the evaluator receives a `dyad_key` (e.g., `"bina_reina"`) and `member_a` + `member_b` identifiers rather than a single focal character.
3. **Alicia-orbital gate**: Alicia-orbital dyads (`adelia_alicia`, `bina_alicia`, `reina_alicia`) only update when `is_currently_active=True`. The evaluator must not write to a dormant Alicia dyad.
4. **Per-pair register notes** live in the pre-execution section of this file, not improvised. Claude Code must copy them verbatim into `internal_relationship_prompts.py::INTERNAL_RELATIONSHIP_EVAL_SYSTEM`.

### Files to create or modify

| File | Action | Scope |
|------|--------|-------|
| `src/starry_lyfe/api/orchestration/internal_relationship_prompts.py` | **Create** | System prompt (per-pair register notes from pre-execution section above, verbatim) + `InternalRelationshipEvalResponse` Pydantic schema (5 fields) + `build_internal_eval_prompt()` + `parse_internal_eval_response()` |
| `src/starry_lyfe/api/orchestration/internal_relationship.py` | **Create** | `evaluate_and_update_internal()` — mirrors Phase 8 pattern; LLM-primary with heuristic fallback; ±0.03 cap; Alicia-orbital active-gate; 5-dimension `InternalDyadDeltaProposal` |
| `src/starry_lyfe/api/orchestration/__init__.py` | Modify | Export new Phase 9 symbols |
| `src/starry_lyfe/api/orchestration/post_turn.py` | Modify | Add `evaluate_and_update_internal()` fire-and-forget scheduling for the focal character's active inter-woman dyads |
| `src/starry_lyfe/api/config.py` | Modify | Add `internal_relationship_eval_llm: bool = True` toggle (reuses `relationship_eval_max_tokens` and `relationship_eval_temperature` from Phase 8) |
| `.env.example` | Modify | Document the 1 new env var |
| `tests/unit/api/test_internal_relationship_prompts.py` | **Create** | Same coverage pattern as Phase 8 test_relationship_prompts.py |
| `tests/unit/api/test_internal_relationship_evaluator.py` | **Create** | Same coverage pattern as Phase 8 test_relationship_evaluator.py, plus Alicia-orbital active-gate tests |
| `Docs/OPERATOR_GUIDE.md §14` | Modify | Document new env var + cost envelope (one extra BDOne round-trip per active inter-woman dyad per turn) |
| `Docs/CHANGELOG.md` | Modify | Phase 9 entry |
| `CLAUDE.md §19` | Modify | Phase 9 status transitions at ship time |

### Acceptance criteria

| AC | Description |
|----|-------------|
| AC-9.1 | `evaluate_and_update_internal()` signature: `session_factory`, `character_id` (kw-only), `response_text` (kw-only), `llm_client=None`, `settings=None`. Returns a list of `InternalRelationshipUpdate` records (one per active dyad) or empty list. |
| AC-9.2 | `InternalDyadDeltaProposal` frozen dataclass with 5 fields: `trust`, `intimacy`, `conflict`, `unresolved_tension`, `repair_history` — all default 0.0. |
| AC-9.3 | ±0.03 per-dimension per-turn cap unchanged. `_clamp_delta` from `relationship.py` reused, not duplicated. |
| AC-9.4 | LLM call via `BDOne.complete()` with `max_tokens` + `temperature` from `ApiSettings` (reuses Phase 8 settings). |
| AC-9.5 | `InternalRelationshipEvalResponse` Pydantic schema with 5 float fields; `_reject_bool` before-validator reused from `relationship_prompts.py`. |
| AC-9.6 | On ANY LLM failure, fall back to `_propose_internal_deltas()` heuristic. Heuristic stays as named callable. |
| AC-9.7 | `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM=false` toggle forces heuristic path. |
| AC-9.8 | System prompt in `internal_relationship_prompts.py::INTERNAL_RELATIONSHIP_EVAL_SYSTEM` carries the hand-authored per-pair register notes from this file's pre-execution section, verbatim. Claude Code must not improvise, summarize, or paraphrase these notes. |
| AC-9.9 | `parse_internal_eval_response()` returns `None` on malformed JSON, non-object JSON, missing fields, non-numeric/boolean fields. Parser fail-closed on all invalid shapes (R1-F1 lesson from Phase 8 applied proactively). |
| AC-9.10 | `repair_history` clamps negative outputs to 0.0. `conflict` dimension has no positive-only constraint. |
| AC-9.11 | Alicia-orbital gate: `evaluate_and_update_internal()` skips write (returns no update record) for any dyad where `is_currently_active=False`. |
| AC-9.12 | Test baseline ≥ 1075 passed (1058 + ≥17 new). ruff + mypy --strict clean. |
| AC-9.13 | No new Alembic migration required (`DyadStateInternal` schema unchanged). |
| AC-9.14 | `OPERATOR_GUIDE.md §14` documents the 1 new env var + cost envelope (one extra BDOne round-trip per active inter-woman dyad per turn — up to 3 for a resident-continuous scene, 0-3 for scenes including Alicia). |
| AC-9.15 | Structured log events: `internal_llm_eval_parsed_proposal` on success, `internal_llm_eval_fallback_to_heuristic` on fallback, with `dyad_key` + `reason`. |

### Key design decisions (pre-resolved for Claude Code)

- **Do not duplicate `_clamp_delta` or `_NumericValue`/`_reject_bool`.** Import from Phase 8 modules.
- **`build_internal_eval_prompt()` takes `dyad_key`, `member_a`, `member_b`, `response_text`.** The system prompt carries the register notes; the user turn identifies which dyad and which woman spoke.
- **Heuristic fallback** (`_propose_internal_deltas`) should use the same substring-match pattern as Phase 8's `_propose_deltas`, extended with `_CONFLICT_POSITIVE` / `_CONFLICT_NEGATIVE` signal banks for the fifth dimension.
- **`post_turn.py` scheduling:** after the focal character's Whyze-dyad update fires, retrieve the focal character's active inter-woman dyads from `DyadStateInternal` and fire one `evaluate_and_update_internal()` create_task per active dyad. Alicia-orbital gate is enforced inside `evaluate_and_update_internal()`, not in the scheduler.

_Claude Code fills in the rest of this section (estimated commits, open questions) during Step 1._

<!-- HANDSHAKE: Claude Code → Project Owner | Step 1 Plan complete, ready for approval [PENDING] -->

---

## Step 2: Execute (Claude Code)

**[STATUS: COMPLETE — three-commit chain landed 2026-04-15]**
**Owner:** Claude Code
**Prerequisite:** Step 1 plan APPROVED via ExitPlanMode (handshake row 3)
**Reads:** Plan file (`C:\Users\Whyze\.claude\plans\declarative-exploring-stearns.md`), §Pre-execution register notes above, Phase 8 pattern (`relationship_prompts.py`, `relationship.py`, `post_turn.py`).

### Execution log

**Commits made:**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| 1 | `a3148f5` | `feat(phase_9): internal_relationship_prompts + evaluator modules + Pydantic schema + parser` | 2 new src modules + `__init__.py` + `config.py` + `.env.example` + `test_internal_relationship_prompts.py` |
| 2 | `3449335` | `feat(phase_9): wire evaluate_and_update_internal into post_turn + evaluator tests` | `post_turn.py` + `test_internal_relationship_evaluator.py` + `test_post_turn.py` update |
| 3 | this commit | `docs(phase_9): Step 2 execution log + OPERATOR_GUIDE §14 + CHANGELOG + CLAUDE.md §19 + IMPLEMENTATION_PLAN §3 + ARCHITECTURE.md` | PHASE_9.md + CLAUDE.md + ARCHITECTURE.md + CHANGELOG.md + IMPLEMENTATION_PLAN_v7.1.md + OPERATOR_GUIDE.md + PHASE_8.md (SEALED markers) |

**Test suite delta:**

- Before execution: 1058 passed (Phase 8 Step 4 Round 1 remediation baseline).
- After C1 (prompts + evaluator modules + prompts tests): 1093 passed (+35).
- After C2 (wiring + evaluator tests): 1113 passed (+20).
- **Final: 1113 passed, 0 failed.** `ruff` + `mypy --strict` clean across **103 source files** (101 → 103; +2 for `internal_relationship_prompts.py` + `internal_relationship.py`).

### Self-assessment against acceptance criteria

| AC | Status | Evidence |
|----|--------|----------|
| AC-9.1 | **MET** | `evaluate_and_update_internal(session_factory, *, character_id, response_text, llm_client=None, settings=None) -> list[InternalRelationshipUpdate]`. `TestEvaluateAndUpdateInternal` tests empty-active-set, single-dyad, multi-dyad paths. `test_returns_three_running_tasks` in `test_post_turn.py` verifies the fire-and-forget scheduling wires correctly. |
| AC-9.2 | **MET** | `InternalDyadDeltaProposal` frozen dataclass with five fields (trust, intimacy, conflict, unresolved_tension, repair_history) all defaulting to 0.0. |
| AC-9.3 | **MET** | `_clamp_delta` imported from `relationship.py` (no duplication). `test_single_active_dyad_produces_one_update_record` asserts ±0.03 cap on trust/intimacy/conflict; `test_llm_path_clamps_above_cap` proves ±1.0 LLM output lands at ±0.03 applied. |
| AC-9.4 | **MET** | `_llm_propose_internal_deltas` calls `BDOne.complete()` with `max_tokens` + `temperature` from `ApiSettings` (reuses Phase 8's `relationship_eval_max_tokens` + `relationship_eval_temperature`). |
| AC-9.5 | **MET** | `InternalRelationshipEvalResponse` Pydantic schema routed through `model_validate`. `_NumericValue` + `_reject_bool` imported from `relationship_prompts.py` (no duplication). `TestR1F2PydanticSchemaActive` (3 tests) proves the schema is the live validator. |
| AC-9.6 | **MET** | Five fallback branches each tested: `test_llm_failure_falls_back_to_heuristic`, `test_llm_malformed_response_falls_back_to_heuristic`, `test_llm_non_object_json_falls_back_to_heuristic`, `test_circuit_open_falls_back_to_heuristic`, `test_toggle_false_uses_heuristic_directly`. `_propose_internal_deltas` heuristic stays as named callable. |
| AC-9.7 | **MET** | `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM=false` wired via `ApiSettings.internal_relationship_eval_llm`. `test_toggle_false_uses_heuristic_directly` confirms responder never invoked when toggle is False. |
| AC-9.8 | **MET** | `INTERNAL_RELATIONSHIP_EVAL_SYSTEM` carries all 6 per-pair register sections verbatim from `PHASE_9.md §Pre-execution`. `TestSystemPromptSoulContent` (10 tests) asserts canonical load-bearing phrases appear verbatim: "the weld is cracked" (adelia×bina), "hall light" (bina×reina), "Iberian Peninsula" (adelia×reina), "forehead to forehead" (adelia×alicia), "couch above the garage" (bina×alicia), "football argument" (reina×alicia), + "Alicia-orbital note" appears exactly 3 times for the 3 orbital dyads. |
| AC-9.9 | **MET** | R1-F1 Phase 8 lesson applied proactively. `TestR1F1ParserFailClosed` parametrizes 8 non-object JSON shapes (`[]`, arrays, int, float, string, `null`, `true`, `false`) + boolean-field rejection. `isinstance(raw, dict)` pre-guard + `_NumericValue` before-validator catch booleans. |
| AC-9.10 | **MET** | `parse_internal_eval_response` clamps negative `repair_history` to 0.0 with warn log (`internal_llm_eval_parse_negative_repair_history`). `test_negative_repair_history_clamps_to_zero` covers the contract. |
| AC-9.11 | **MET** | Alicia-orbital gate lives in the SELECT statement's `is_currently_active.is_(True)` filter. `TestAliciaOrbitalActiveGate` (3 tests) verifies: (a) empty-result handling, (b) predicate appears in the statement text, (c) active orbital dyad updates normally. Dormant dyads never consume LLM budget because they never reach the LLM-call code path. |
| AC-9.12 | **MET** | **1113 passed, 0 failed** (≥1075 target exceeded by +38). ruff + mypy --strict clean across 103 source files. |
| AC-9.13 | **MET** | No schema change; no Alembic migration. `DyadStateInternal` ORM unchanged. |
| AC-9.14 | **MET** | `OPERATOR_GUIDE.md §14.2` documents the new env var `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM`. §14.4.1 cost envelope updated with the per-active-dyad fan-out math (one extra BDOne round-trip per active inter-woman dyad per turn — 0 for Alicia-away characters, up to 3 for resident-continuous focal characters in scenes with Alicia home). |
| AC-9.15 | **MET** | Two structured log events: `internal_llm_eval_parsed_proposal` (with `dyad_key` + all 5 delta values) and `internal_llm_eval_fallback_to_heuristic` (with `dyad_key` + `reason`: `circuit_open` / `DreamsLLMError: …` / `parse_returned_none` / `llm_disabled_or_missing`). |

### Known deviations from Step 1 plan

None. All three micro-decisions flagged as pre-resolved in the plan held:

1. **Prompt shape**: 4-arg `build_internal_eval_prompt(dyad_key, member_a, member_b, response_text)` — shipped as specified.
2. **Scheduling per-dyad fan-out**: single `asyncio.create_task` for the evaluator; fan-out happens inside via the SELECT filter; Alicia-orbital gate in the query predicate — shipped as specified.
3. **Settings reuse**: `relationship_eval_max_tokens` + `relationship_eval_temperature` reused; only `internal_relationship_eval_llm` new — shipped as specified.

### Open questions for Codex / Claude AI / Project Owner

None outstanding. Phase 8 R1-F1 / R1-F2 / R1-F3 lessons were applied proactively in Step 2 (see AC-9.9, AC-9.5, AC-9.8 evidence), so the surface Codex audited in Phase 8 R1 is already hardened here.

<!-- HANDSHAKE: Claude Code → Codex | Step 2 Execute COMPLETE. Three-commit chain on main: a3148f5 + 3449335 + [this governance sweep commit]. Test suite 1058 → 1113, ruff + mypy --strict clean. 15/15 ACs MET pre-audit with proactive application of Phase 8 R1-F1/R1-F2/R1-F3 lessons. Ready for Round 1 audit. -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: NOT STARTED]**

_Codex fills in this section._

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete [PENDING] -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: NOT STARTED]**

_Claude Code fills in this section._

<!-- HANDSHAKE: Claude Code → {Codex if Path B / Claude AI if Path A} | Remediation Round 1 complete [PENDING] -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B)

**[STATUS: NOT STARTED]**

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 2 complete [PENDING, conditional] -->

---

## Step 4': Remediate (Claude Code) — Round 2 (only if Round 2 audit fires)

**[STATUS: NOT STARTED]**

<!-- HANDSHAKE: Claude Code → {Codex / Claude AI} | Remediation Round 2 complete [PENDING, conditional] -->

---

## Step 3'': Audit (Codex) — Round 3 (final before escalation)

**[STATUS: NOT STARTED]**

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 3 complete [PENDING, conditional] -->

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: NOT STARTED]**

<!-- HANDSHAKE: Claude Code → {Project Owner if not converged / Claude AI if converged} | Remediation Round 3 complete [PENDING, conditional] -->

---

## Step 5: QA (Claude AI)

**[STATUS: NOT STARTED]**

_Claude AI fills in this section._

<!-- HANDSHAKE: Claude AI → Project Owner | QA verdict ready [PENDING] -->

---

## Step 6: Ship (Project Owner)

**[STATUS: NOT STARTED]**

<!-- HANDSHAKE: Project Owner → CLOSED | Phase shipped [PENDING] -->

---

## Closing Block (locked once shipped)

**Phase identifier:** 9
**Final status:** _pending_
**Total cycle rounds:** _pending_
**Total commits:** _pending_
**Total tests added:** _pending — estimate ≥17_
**Date opened:** 2026-04-15 (phase file created by Claude AI)
**Date closed:** _pending_

**Lessons for the next phase:** _Claude AI will fill at ship._

**Cross-references:**
- Master plan: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 + §7
- Previous phase: `Docs/_phases/PHASE_8.md` (LLM Relationship Evaluator, SEALED 2026-04-15)
- Phase 8 pattern files: `src/starry_lyfe/api/orchestration/relationship_prompts.py`, `relationship.py`
- Target schema: `src/starry_lyfe/db/models/dyad_state_internal.py`
- Canon dyad source: `src/starry_lyfe/canon/dyads.yaml`

---

_End of Phase 9 canonical record._
