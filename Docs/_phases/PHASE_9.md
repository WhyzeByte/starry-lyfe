# Phase 9: DyadStateInternal LLM Evaluator

**Master plan reference:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §6 (Model Routing) + §7 crosscut — inter-woman dyad track
**Phase identifier:** `9`
**Depends on:** Phase 8 SEALED 2026-04-15 (LLM evaluator pattern, `relationship_prompts.py` architecture, `BDOne` wiring, `_NumericValue`/`_reject_bool` Pydantic primitives)
**Blocks:** None identified
**Status:** STEP 3'' AUDIT ROUND 3 COMPLETE — Project Owner-authorized AGENTS.md Path C direct Codex doc-only remediation applied; gate PASS
**Last touched:** 2026-04-15 by Codex (Round 3 doc-only remediation applied directly under AGENTS.md Path C; no production code changes; ready for Step 5 QA)

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
| 4 | 2026-04-15 | Claude Code | Codex | Step 2 Execute COMPLETE. Three-commit chain on main: `a3148f5` + `3449335` + `4b50132`. Test suite 1058 → 1113 (+55). 15/15 ACs MET pre-audit. Phase 8 R1-F1/R1-F2/R1-F3 lessons applied proactively. Ready for Round 1 audit. |
| 5 | 2026-04-15 | Codex | Claude Code | Round 1 audit complete on the committed Phase 9 chain. **Gate FAIL.** Three findings: F1 (High) speaker identity dropped from live prompt; F2 (High) Alicia-orbital remote-turn path unreachable; F3 (Medium) PHASE_9.md Step 1 internal inconsistency + scheduler-shape narrative drift. |
| 6 | 2026-04-15 | Project Owner | Claude Code | Round 1 remediation plan approved via ExitPlanMode. F2 approach = Hybrid (canonical prose preserved + scope narrowed to deferred future-phase). Three-commit chain authorized. |
| 7 | 2026-04-15 | Claude Code | Codex | Round 1 remediation COMPLETE. Three-commit chain on main: `b301b16` (RT1 F1 speaker identity + regression suite, +6 tests) + `2906ed3` (RT2 F2 doc-narrow Alicia-orbital remote-turn) + `11a8af6` (RT3 F3 + Step 4 record + downstream sync). Test suite 1113 → 1119; ruff + mypy --strict clean across 103 source files. Path B classification (F1 substantive). Ready for Round 2 re-audit. |
| 8 | 2026-04-15 | Codex | Claude Code | Round 2 re-audit complete on the remediation chain `b301b16` + `2906ed3` + `11a8af6`; gate PASS WITH MINOR FIXES. F1 and F2 are genuinely closed; remaining issues are low-severity doc drift in the phase record and downstream sync surfaces (duplicate handshake row, stale 1118/residue-failure claims, placeholder commit references). |
| 9 | 2026-04-15 | Codex | Claude Code | Round 3 re-audit complete on the current post-Round-2 state. No new remediation commit or Step 4' artifact is visible beyond the prior Round 2 audit append in this file. Gate remains PASS WITH MINOR FIXES; the same 3 low-severity doc findings remain open unchanged. |
| 10 | 2026-04-15 | Project Owner (via chat) | Codex | Authorized AGENTS.md Path C direct Codex doc-only remediation for the 3 Round 3 low-severity Phase 9 documentation findings. |
| 11 | 2026-04-15 | Codex | Claude AI | Path C remediation applied directly in `PHASE_9.md`, `Docs/CHANGELOG.md`, `CLAUDE.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, and `Docs/ARCHITECTURE.md`. Round 3 closed with no remaining findings; gate PASS; ready for Step 5 QA. |

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

> **R1-F2 closure (2026-04-15) — scope clarification for the three Alicia-orbital sections that follow.**
>
> Each Alicia-orbital pair section below carries an **Alicia-orbital note** describing how the dyad should respond on remote turns (letter / phone / video) when `is_currently_active=false`. **Phase 9 ships the active-only behavior** described in AC-9.11: the SQL gate `is_currently_active.is_(True)` filters dormant orbital dyads out before any LLM call, so the remote-turn paths in the canonical prose below are **not yet reachable in the runtime**. The canonical prose is preserved verbatim per CLAUDE.md §19 quality directive (canonical content is never trimmed) and remains load-bearing for a future phase.
>
> **Deferred to future phase:** thread `communication_mode` from `PipelineResult.scene_state` through `schedule_post_turn_tasks` → `evaluate_and_update_internal`; relax the SQL gate for orbital dyads on remote turns; surface `intimacy+ (letter/phone/video)` register cues to the LLM. See the Closing Block "Not in scope (deferred)" bullet for the carry-forward record.

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

**[STATUS: COMPLETE]** *(R1-F3 closure 2026-04-15: status flipped from `NOT STARTED`; placeholder line removed; pending handshake replaced with real handshake referencing log row 3.)*
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
| AC-9.11 | Alicia-orbital gate: `evaluate_and_update_internal()` skips write (returns no update record) for any dyad where `is_currently_active=False`. *(R1-F2 closure 2026-04-15: active-only behavior; remote-turn handling for dormant Alicia-orbital dyads — described aspirationally in the canonical Pre-execution `Alicia-orbital note` blocks — is explicitly deferred to a future phase. The runtime gate is unconditional in Phase 9.)* |
| AC-9.12 | Test baseline ≥ 1075 passed (1058 + ≥17 new). ruff + mypy --strict clean. |
| AC-9.13 | No new Alembic migration required (`DyadStateInternal` schema unchanged). |
| AC-9.14 | `OPERATOR_GUIDE.md §14` documents the 1 new env var + cost envelope (one extra BDOne round-trip per active inter-woman dyad per turn — up to 3 for a resident-continuous scene, 0-3 for scenes including Alicia). |
| AC-9.15 | Structured log events: `internal_llm_eval_parsed_proposal` on success, `internal_llm_eval_fallback_to_heuristic` on fallback, with `dyad_key` + `reason`. |

### Key design decisions (pre-resolved for Claude Code)

- **Do not duplicate `_clamp_delta` or `_NumericValue`/`_reject_bool`.** Import from Phase 8 modules.
- **`build_internal_eval_prompt()` takes `dyad_key`, `member_a`, `member_b`, `response_text`, plus a kw-only `speaker_id`.** The system prompt carries the register notes; the user turn identifies which dyad and **explicitly which woman spoke** via the `Speaker:` line. *(R1-F1 closure 2026-04-15: `speaker_id` was added to the live prompt surface in commit `b301b16` so the LLM can resolve directional pair signals. Pre-fix the prompt dropped speaker identity.)*
- **Heuristic fallback** (`_propose_internal_deltas`) should use the same substring-match pattern as Phase 8's `_propose_deltas`, extended with `_CONFLICT_POSITIVE` / `_CONFLICT_NEGATIVE` signal banks for the fifth dimension.
- **`post_turn.py` scheduling:** after the focal character's Whyze-dyad update fires, schedule a **single** `evaluate_and_update_internal()` `asyncio.create_task` for the focal character. The evaluator internally retrieves the focal character's active inter-woman dyads from `DyadStateInternal` via a SELECT with `is_currently_active.is_(True)` predicate and fans out one LLM call per active dyad. *(R1-F3 closure 2026-04-15: prior wording said "fire one create_task per active dyad", which contradicted the shipped single-task-with-internal-fan-out design. Reconciled to the shipped reality.)* Alicia-orbital gate is enforced at the SQL boundary inside `evaluate_and_update_internal()`, not in the scheduler.

### Estimated commits

Three-commit chain per Phase 8 precedent:

1. `feat(phase_9): internal_relationship_prompts + evaluator modules + Pydantic schema + parser`
2. `feat(phase_9): wire evaluate_and_update_internal into post_turn + evaluator tests`
3. `docs(phase_9): Step 2 execution log + OPERATOR_GUIDE §14 + CHANGELOG + CLAUDE.md §19 + IMPLEMENTATION_PLAN §3 + ARCHITECTURE.md`

### Open questions

None outstanding. The three pre-resolved micro-decisions held in Step 2:

1. **Prompt shape**: 4-arg `build_internal_eval_prompt(dyad_key, member_a, member_b, response_text)` shipped as specified; later extended in R1-F1 closure to add `speaker_id` (kw-only) per Codex Round 1 finding.
2. **Scheduling per-dyad fan-out**: single `asyncio.create_task` for the evaluator; fan-out happens inside via the SELECT filter; Alicia-orbital gate in the SQL predicate.
3. **Settings reuse**: `relationship_eval_max_tokens` + `relationship_eval_temperature` reused; only `internal_relationship_eval_llm` toggle is new.

<!-- HANDSHAKE: Claude Code → Project Owner | Step 1 Plan complete; approved via ExitPlanMode 2026-04-15 (see handshake log row 3). -->

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
| 3 | `4b50132` | `docs(phase_9): Step 2 execution log + OPERATOR_GUIDE §14 + CHANGELOG + CLAUDE.md §19 + IMPLEMENTATION_PLAN §3 + ARCHITECTURE.md` | PHASE_9.md + CLAUDE.md + ARCHITECTURE.md + CHANGELOG.md + IMPLEMENTATION_PLAN_v7.1.md + OPERATOR_GUIDE.md + PHASE_8.md (SEALED markers) |

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

<!-- HANDSHAKE: Claude Code → Codex | Step 2 Execute COMPLETE. Three-commit chain on main: a3148f5 + 3449335 + 4b50132. Test suite 1058 → 1113, ruff + mypy --strict clean. 15/15 ACs MET pre-audit with proactive application of Phase 8 R1-F1/R1-F2/R1-F3 lessons. Ready for Round 1 audit. -->

---

## Step 3: Audit (Codex) — Round 1

**[STATUS: COMPLETE — gate FAIL]**

**Owner:** Codex
**Invocation note:** Round 1 audit of the committed Phase 9 execution chain `a3148f5` + `3449335` + `4b50132` against the shared phase record, the shipped implementation, and the Phase 8 hardening lessons Claude Code claimed were carried forward proactively.

### Audit content

**Scope:** Reviewed `Docs/_phases/PHASE_9.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, `Docs/ARCHITECTURE.md`, `CLAUDE.md`, `Docs/OPERATOR_GUIDE.md`, `.env.example`, `src/starry_lyfe/api/orchestration/internal_relationship_prompts.py`, `internal_relationship.py`, `post_turn.py`, `pipeline.py`, `chat.py`, `memory_extraction.py`, `config.py`, `__init__.py`, `src/starry_lyfe/db/models/dyad_state_internal.py`, `tests/unit/api/test_internal_relationship_prompts.py`, `test_internal_relationship_evaluator.py`, and `test_post_turn.py`.

**Verification context:** Independent verification on the committed Phase 9 state:

- `.\.venv\Scripts\python.exe -m pytest tests/unit/api/test_internal_relationship_prompts.py tests/unit/api/test_internal_relationship_evaluator.py tests/unit/api/test_post_turn.py -q` -> `62 passed`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/api -q` -> `199 passed`
- `.\.venv\Scripts\python.exe -m pytest -q` -> `1113 passed`
- `.\.venv\Scripts\ruff.exe check src tests` -> clean
- `.\.venv\Scripts\python.exe -m mypy --strict src` -> clean

**Executive assessment:** Phase 9 successfully carries forward most of the Phase 8 parser/prompt hardening: the new parser fails closed on non-object JSON and booleans, the prompt surface escapes delimiter injection, the 5-dimension schema is live, the SQL-side active-row gate exists, and the full suite remains green at `1113 passed`.

Two architectural gaps still block a PASS. First, the internal LLM prompt never tells the model which woman actually spoke, even though the evaluator has `character_id` and the phase plan explicitly says the user turn identifies which woman spoke. This makes the live prompt ambiguous for directional, actor-specific pair signals across all six dyads. Second, the canonical adelia×alicia remote-turn path described in the hand-authored pre-execution notes is impossible in the shipped design: dormant Alicia dyads are filtered out before evaluation, and no communication-mode signal reaches the post-turn evaluator. The shared phase record also still misstates its own Step 1 state and scheduler shape. Gate is therefore **FAIL**.

**Findings (numbered, severity-tagged):**

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| 1 | High | The internal LLM prompt drops speaker identity. `evaluate_and_update_internal()` receives `character_id`, but `_llm_propose_internal_deltas()` builds the user prompt with only `dyad_key`, `member_a`, `member_b`, and `response_text`. The plan text at `PHASE_9.md` says the user turn identifies which woman spoke, but the live prompt does not. In a runtime probe, the same `bina_reina` text produced identical prompts whether `character_id='bina'` or `character_id='reina'`. That makes many register cues directionally ambiguous in practice (for example who left the hall light on, who called the other “the witness,” who delivered the structural veto). | [internal_relationship.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship.py:272), [internal_relationship.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship.py:336), [internal_relationship_prompts.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship_prompts.py:387), [internal_relationship_prompts.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship_prompts.py:422), [internal_relationship_prompts.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship_prompts.py:424), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:200) | Thread the focal speaker through the live prompt surface. The minimal repair is to add a `speaker_id` argument to `build_internal_eval_prompt()` and include an explicit `Speaker:` line in the user prompt, then add a regression proving prompts differ for the same dyad/text when the speaker differs. |
| 2 | High | The canonical adelia×alicia remote-turn path is impossible in the shipped Phase 9 surface. The hand-authored pre-execution note says that when Alicia is away and `is_currently_active=false`, evaluator outputs for this dyad should still fire on communication-mode turns (`letter`, `phone`, `video`). The shipped evaluator cannot do that: `evaluate_and_update_internal()` accepts no communication-mode input, the query hard-filters `is_currently_active.is_(True)`, and the post-turn scheduler passes only `full_response_text`. A runtime probe with letter/phone-style text while the dyad was dormant produced zero updates. | [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:99), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:158), [internal_relationship.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship.py:272), [internal_relationship.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/internal_relationship.py:316), [post_turn.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/post_turn.py:49), [post_turn.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/orchestration/post_turn.py:110), [chat.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/api/endpoints/chat.py:164) | Resolve the source-of-truth conflict explicitly. Either implement the remote exception for adelia×alicia by threading communication mode into post-turn evaluation and relaxing the dormant-row gate for that dyad on remote turns, or revise the canonical pre-execution note / AC language so the phase record no longer describes a path the runtime can never take. |
| 3 | Medium | The canonical Phase 9 workflow record is internally inconsistent before audit. Step 1 contains a substantive plan body, but it is still marked `NOT STARTED`, still says Claude Code will fill estimated commits/open questions later, and still ends with the pending Step 1 handshake. The same Step 1 section also says `post_turn.py` should fire one `evaluate_and_update_internal()` create_task per active dyad, while Step 2 later says the shipped shape is a single task that fans out internally. Step 2 / the implementation plan then overclaim that `PHASE_9.md` already carries a complete Step 1 plan. | [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:144), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:146), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:202), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:204), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:206), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:259), [IMPLEMENTATION_PLAN_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/IMPLEMENTATION_PLAN_v7.1.md:40) | Repair the shared phase record before ship. Mark Step 1 complete with the real approval/handshake state, fill the deferred plan fields, and reconcile the Step 1 scheduler wording with the actual shipped single-task fan-out design. |

**Runtime probe summary:**

- Prompt-surface probe: `build_internal_eval_prompt('bina_reina', 'bina', 'reina', 'I left the hall light on for her when she got home.')` yields only `Dyad:` + `Members:` + `response_text`; there is no `Speaker:` field.
- Speaker-identity red team: running `evaluate_and_update_internal(... character_id='bina' ...)` and `evaluate_and_update_internal(... character_id='reina' ...)` against the same `bina_reina` row and same text produced identical `user_prompt` strings captured by `StubBDOne`.
- Dormant Alicia remote probe: a letter/phone-style adelia×alicia turn while the dyad was inactive produced `0` update records because the evaluator sees only rows selected through `is_currently_active.is_(True)`.
- Hardening probes passed: delimiter-injection payloads remain escaped, non-object JSON returns `None`, and the parser still rejects boolean numerics through the shared `_NumericValue` validator.

**Drift against specification:**

- AC-9.5, AC-9.6, AC-9.7, AC-9.9, AC-9.10, AC-9.12, AC-9.14, and AC-9.15 are materially implemented as described.
- AC-9.8 / Step 1’s prompt-shape explanation drift from reality: the plan text says the user turn identifies which woman spoke, but the live prompt does not.
- The Phase 9 file contains an unresolved internal conflict between the hand-authored adelia×alicia remote-turn note and AC-9.11’s blanket inactive-row gate.
- Governance drift remains in the canonical Step 1 record and the scheduler-shape narrative.

**Verified resolved:**

- Phase 8 R1-F1 lesson carried forward: `parse_internal_eval_response()` fails closed on malformed JSON, non-object JSON, missing fields, and boolean numerics via `isinstance(raw, dict)` + shared `_NumericValue`.
- Phase 8 R1-F2 lesson carried forward: `InternalRelationshipEvalResponse.model_validate()` is the live validator, not dead schema code.
- Phase 8 R1-F3 lesson carried forward: `build_internal_eval_prompt()` escapes interpolated `response_text`, so injected `</response_text>` content stays trapped inside the prompt frame.
- The new env var, cost envelope, scheduler task count, and full-suite baseline are documented consistently in `OPERATOR_GUIDE.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, and `CLAUDE.md`.

**Adversarial scenarios constructed:**

1. Same dyad, same text, different focal speaker (`bina_reina`, Bina vs Reina).
Result: prompts were identical; the LLM cannot tell who spoke.
2. Dormant adelia×alicia remote-turn text mentioning a letter / phone-style signal.
Result: no update record; the inactive-row SQL gate makes the documented remote path unreachable.
3. Prompt-injection payload containing `</response_text>`.
Result: escaped correctly; wrapper stayed intact.
4. Non-object JSON / boolean numerics from the LLM.
Result: parser returned `None`; fail-closed behavior held.

**Recommended remediation order:**

1. Fix the speaker-identity gap in the live prompt surface and add regression coverage proving prompts differ by focal speaker.
2. Resolve the adelia×alicia remote-turn conflict one way or the other: either implement communication-mode-aware dormant handling or explicitly narrow the canonical note/spec to the shipped active-only behavior.
3. Repair the Step 1 workflow record so `PHASE_9.md` is a truthful canonical artifact before QA.

**Gate recommendation:** **FAIL**

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 1 complete on the committed Phase 9 chain. Gate FAIL. Remediate F1 speaker identity in the live prompt surface, F2 the unreachable adelia×alicia remote path / source-of-truth conflict, and F3 the Step 1 governance drift. -->

---

## Step 4: Remediate (Claude Code) — Round 1

**[STATUS: COMPLETE — three-commit remediation chain landed 2026-04-15]**
**Owner:** Claude Code
**Prerequisite:** Codex Round 1 audit complete (handshake log row 5); Project Owner approved remediation plan via ExitPlanMode (handshake log row 6).
**Path classification:** Path B (substantive code change for F1; doc-only narrowing for F2 and F3 — Path B applies overall because of F1).

### Remediation log

**Commits made:**

| # | Hash | Message | Files touched |
|---:|---|---|---|
| RT1 | `b301b16` | `fix(phase_9): R1-F1 — thread speaker identity through internal eval prompt + regression test` | `internal_relationship_prompts.py` + `internal_relationship.py` + `test_internal_relationship_prompts.py` + `test_internal_relationship_evaluator.py` |
| RT2 | `2906ed3` | `docs(phase_9): R1-F2 — narrow Alicia-orbital remote-turn note to deferred future-phase scope` | `PHASE_9.md` only (canonical Pre-execution prose preserved verbatim; new R1-F2 closure callout above orbital sections + AC-9.11 inline parenthetical + new "Not in scope (deferred)" Closing Block section) |
| RT3 | `11a8af6` | `docs(phase_9): R1-F3 + Step 4 governance — repair PHASE_9.md Step 1 record + Step 4 remediation log + downstream sync` | `PHASE_9.md` (Step 1 status + scheduler narrative reconcile + Step 4 Round 1 record + handshake row 6) + `Docs/IMPLEMENTATION_PLAN_v7.1.md §3` + `Docs/CHANGELOG.md` + `CLAUDE.md §19` + `Docs/ARCHITECTURE.md` (version bump) |

**Test suite delta:**

- Before remediation: 1113 passed (post-Phase-9-Step-2 baseline).
- After RT1 (F1 speaker identity + regression suite): 1119 passed (+6 new tests).
- After RT2 (F2 doc-only): 1119 unchanged.
- After RT3 (F3 governance + downstream sync): 1119 unchanged.
- **Final: 1119 passed, 0 failed.**
- `ruff` + `mypy --strict` clean across **103 source files**.

### Per-finding closure table

| # | Severity | Original Codex finding | Status | Closure evidence |
|---:|---|---|---|---|
| F1 | High | The internal LLM prompt drops speaker identity. Same `bina_reina` text produced identical prompts whether the focal speaker was Bina or Reina, making directional pair signals ambiguous. | **FIXED** via RT1 (`b301b16`) | `build_internal_eval_prompt()` gains kw-only `speaker_id` parameter; `Speaker: {speaker_id}` line injected above `Dyad:` in the user prompt template; `_llm_propose_internal_deltas()` threads `character_id` through to the prompt builder. Two key regression tests pin the post-fix contract: `test_same_dyad_different_speaker_yields_different_prompts` (prompt-shape level) and `test_same_dyad_distinct_focal_speakers_yield_distinct_prompts` (integration-style with recording `StubBDOne` responder — replicates the exact Codex red-team probe). |
| F2 | High | The canonical adelia×alicia remote-turn path described in the hand-authored pre-execution notes is unreachable in the shipped Phase 9 surface. | **FIXED** via RT2 (`2906ed3`) — Project Owner choice = Hybrid (canonical prose preserved, scope narrowed) | Canonical `Alicia-orbital note` blocks in §Pre-execution preserved verbatim per CLAUDE.md §19 quality directive. New R1-F2 closure callout immediately above the three Alicia-orbital pair sections clarifies the active-only runtime behavior. AC-9.11 row in Step 1 acceptance criteria gains an inline parenthetical. New "Not in scope (deferred to a future phase)" section in the Closing Block carries a future-phase implementation sketch (thread `communication_mode` from `PipelineResult.scene_state` through scheduler → evaluator; relax SQL gate for orbital dyads on remote turns). |
| F3 | Medium | `PHASE_9.md` Step 1 inconsistencies: status `NOT STARTED` despite substantive plan body; scheduler-shape language ("one create_task per active dyad") contradicted Step 2 reality ("single task that fans out internally"); IMPLEMENTATION_PLAN overclaim. | **FIXED** via RT3 (`11a8af6`) | Step 1 status flipped to `[STATUS: COMPLETE]` with R1-F3 closure parenthetical. Placeholder line "Claude Code fills in the rest of this section" removed and replaced with real Estimated commits + Open questions subsections. Pending Step 1 handshake replaced with a real handshake referencing log row 3. Scheduler-shape language reconciled: now says "single `asyncio.create_task` for the focal character; the evaluator internally retrieves the focal character's active inter-woman dyads … and fans out one LLM call per active dyad". Build prompt narrative updated to mention the new `speaker_id` kw-only param. IMPLEMENTATION_PLAN_v7.1.md §3 Phase 9 bullet flipped to "Step 4 Round 1 Remediation COMPLETE 2026-04-15". CLAUDE.md §19 Open ship gate flipped from "Step 2 Execute COMPLETE" to "Step 4 Round 1 Remediation COMPLETE; handshake to Codex for Round 2 re-audit". CHANGELOG.md gets new top section. ARCHITECTURE.md version bumped 0.9.0 → 0.9.1. |

### Phase 8 R1-F4 lesson reapplied

This Step 4 record was populated **at remediation time**, not retrospectively. RT3 commits the populated record alongside the downstream governance sync — the Step 4 remediation surface and the downstream surfaces (CLAUDE.md §19, IMPLEMENTATION_PLAN, CHANGELOG, ARCHITECTURE) all flip to the Round 1 Remediation COMPLETE state in the same commit. No drift gap.

### Known deviations from Step 4 plan

None. All three commits landed as scoped in the approved playbook (`C:\Users\Whyze\.claude\plans\declarative-exploring-stearns.md`).

### Open questions for Codex Round 2

None outstanding. F1 closure ships substantive code change with the exact Codex-described red-team replicated as a regression test. F2 closure is the explicit Project Owner choice (Hybrid) — canonical prose preserved, scope narrowed, future-phase carry-forward documented. F3 closure repairs the canonical phase record so it is now an internally-consistent artifact.

<!-- HANDSHAKE: Claude Code → Codex | Round 1 remediation complete; F1 substantive code fix (b301b16) + F2 doc-narrow (2906ed3) + F3 governance + Step 4 record (11a8af6). Test suite 1113 → 1119. Ready for Round 2 re-audit. -->

---

## Step 3': Audit (Codex) — Round 2 (only if Path B)

**[STATUS: COMPLETE — gate PASS WITH MINOR FIXES]**

**Owner:** Codex
**Invocation note:** Round 2 re-audit of the Phase 9 remediation chain `b301b16` + `2906ed3` + `11a8af6` against the Round 1 findings, the updated canonical phase record, and the downstream governance surfaces Claude Code claimed to sync in RT3.

### Audit content

**Scope:** Re-reviewed `Docs/_phases/PHASE_9.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, `Docs/ARCHITECTURE.md`, `CLAUDE.md`, `Docs/CHANGELOG.md`, `src/starry_lyfe/api/orchestration/internal_relationship_prompts.py`, `internal_relationship.py`, `tests/unit/api/test_internal_relationship_prompts.py`, and `test_internal_relationship_evaluator.py`.

**Verification context:** Independent verification on the remediated Phase 9 state:

- `.\.venv\Scripts\python.exe -m pytest tests/unit/api/test_internal_relationship_prompts.py tests/unit/api/test_internal_relationship_evaluator.py tests/unit/api/test_post_turn.py -q` -> `68 passed`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/api -q` -> `205 passed`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_residue_grep.py -q` -> `2 passed`
- `.\.venv\Scripts\python.exe -m pytest -q` -> `1119 passed`
- `.\.venv\Scripts\ruff.exe check src tests` -> clean
- `.\.venv\Scripts\python.exe -m mypy --strict src` -> clean

**Executive assessment:** The substantive remediation is real. F1 is closed in code: the prompt now carries focal speaker identity all the way to the LLM surface, and the exact Round 1 red-team probe now produces distinct prompts for Bina vs Reina. F2 is also closed on the chosen scope path: the runtime remains active-only for Alicia-orbital dyads, but the canonical record now explicitly marks the remote-turn behavior as deferred rather than pretending the shipped surface can do it.

What remains is documentation drift introduced by the remediation sweep itself. The shared phase record still has a duplicate Round 1 handshake row, several Phase 9 docs still report the old `1118` baseline and a residue-grep failure that no longer reproduces, and placeholder commit references (`this commit`, `<this commit>`, `[this governance sweep commit]`) remain in the canonical record and changelog. These are doc-only issues, so the gate moves from FAIL to **PASS WITH MINOR FIXES**.

**Findings (numbered, severity-tagged):**

| # | Severity | Finding | Evidence | Recommended fix |
|---:|---|---|---|---|
| 1 | Low | The canonical Phase 9 handshake log is still internally inconsistent. RT3 claimed the governance repair was complete, but the log now contains two different row-5 Codex audit entries, leaving the shared phase record out of sequence and duplicative. | [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:30), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:33) | Remove the duplicate row and keep a single Round 1 Codex handshake entry so the phase log is a truthful chronological record. |
| 2 | Low | The remediation verification story is stale across the canonical Phase 9 record and downstream sync docs. They still report `1118 passed`, `+5` tests, and a pre-existing residue-grep failure, but the live repo now verifies at `1119 passed`, `tests/unit/test_residue_grep.py` is green, and the RT1 test diff adds 6 tests (4 in `TestF1SpeakerIdentity`, 2 in `TestF1SpeakerThreading`). | [test_internal_relationship_prompts.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/tests/unit/api/test_internal_relationship_prompts.py:50), [test_internal_relationship_evaluator.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/tests/unit/api/test_internal_relationship_evaluator.py:436), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:391), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:394), [IMPLEMENTATION_PLAN_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/IMPLEMENTATION_PLAN_v7.1.md:40), [ARCHITECTURE.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/ARCHITECTURE.md:23), [CLAUDE.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/CLAUDE.md:383), [CHANGELOG.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/CHANGELOG.md:19) | Refresh the Phase 9 remediation baseline and downstream summaries to the actually verified `1119 passed` / residue-clean state, and correct the RT1 test delta from `+5` to `+6`. |
| 3 | Low | Commit-traceability placeholders remain in Phase 9 governance surfaces. The shared phase record and changelog still use `this commit`, `<this commit>`, and `[this governance sweep commit]` in places where the real hash `11a8af6` is now known. | [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:8), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:29), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:251), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:386), [PHASE_9.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_9.md:417), [CHANGELOG.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/CHANGELOG.md:17) | Replace placeholder commit labels with the landed hash `11a8af6` anywhere the remediation/governance sweep is now being cited as evidence. |

**Runtime probe summary:**

- Prompt-surface probe: `build_internal_eval_prompt(..., speaker_id='bina')` now emits `Speaker: bina` above `Dyad:`, and the same dyad/text produces a different prompt when `speaker_id='reina'`.
- Evaluator-level probe: capturing `StubBDOne` prompts from `evaluate_and_update_internal(... character_id='bina' ...)` vs `character_id='reina'` now yields two distinct user prompts; the Round 1 F1 failure no longer reproduces.
- Dormant Alicia probe: inactive adelia/alicia still yields `0` updates on a remote-style text payload, which now matches the explicitly deferred scope recorded in the Phase 9 docs.
- Verification probe: `tests/unit/test_residue_grep.py` passed (`2 passed`), so the remediation record’s “pre-existing residue failure” note is no longer true on the current working tree.

**Drift against specification:**

- Round 1 F1 is genuinely closed in code and tests.
- Round 1 F2 is closed on the explicitly chosen governance path: the runtime remains active-only, and the canonical prose is now honestly marked as future-phase scope.
- Round 1 F3’s core Step 1 inconsistency is closed, but the remediation sweep left behind new low-severity governance drift in the handshake log and downstream sync surfaces.

**Verified resolved:**

- F1 closed: the prompt builder now takes kw-only `speaker_id`, emits a `Speaker:` line, and the exact Codex red-team is pinned by [test_internal_relationship_prompts.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/tests/unit/api/test_internal_relationship_prompts.py:66) and [test_internal_relationship_evaluator.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/tests/unit/api/test_internal_relationship_evaluator.py:470).
- F2 closed: the Phase 9 record now explicitly defers communication-mode-aware dormant Alicia-orbital updates instead of overclaiming that the shipped runtime supports them.
- Parser/schema/prompt hardening from the original Phase 9 implementation still holds under re-audit: fail-closed non-object JSON handling, boolean rejection, and delimiter escaping all remained intact.

**Adversarial scenarios constructed:**

1. Same dyad, same text, different focal speaker (`bina_reina`, Bina vs Reina).
Result: prompts now differ and carry the correct `Speaker:` line.
2. Dormant adelia/alicia remote-style turn text.
Result: still no update record, now matching the explicitly deferred scope.
3. Prompt-injection payload containing `</response_text>`.
Result: escaped correctly; wrapper remained intact.
4. Residue-grep verification path.
Result: `tests/unit/test_residue_grep.py` passed; the claimed pre-existing failure did not reproduce.

**Recommended remediation order:**

1. Fix the handshake-log duplication in `PHASE_9.md`.
2. Refresh the Phase 9 test baseline / residue narrative to the actually verified `1119 passed` state across `PHASE_9.md`, `IMPLEMENTATION_PLAN_v7.1.md`, `ARCHITECTURE.md`, `CLAUDE.md`, and `CHANGELOG.md`.
3. Replace remaining Phase 9 placeholder commit references with `11a8af6`.

**Gate recommendation:** **PASS WITH MINOR FIXES**

<!-- HANDSHAKE: Codex → Claude Code | Audit Round 2 complete on the remediation chain `b301b16` + `2906ed3` + `11a8af6`. Gate PASS WITH MINOR FIXES. All substantive/runtime findings are closed; remaining issues are low-severity Phase 9 doc-traceability drift only. -->

---

## Step 4': Remediate (Claude Code) — Round 2 (only if Round 2 audit fires)

**[STATUS: SKIPPED — no Claude Code Round 2 remediation pass occurred; the Round 2 low-severity findings were carried into Round 3 and later closed via Project Owner-authorized AGENTS.md Path C direct Codex doc-only remediation]**

<!-- HANDSHAKE: SKIPPED | No Claude Code Round 2 remediation pass occurred. The Round 2 low-severity findings were closed in Step 3'' under Project Owner-authorized AGENTS.md Path C direct Codex doc-only remediation on 2026-04-15. -->

---

## Step 3'': Audit (Codex) — Round 3 (final before escalation)

**[STATUS: COMPLETE — gate PASS]**

**Owner:** Codex
**Invocation note:** Round 3 re-audit of the current post-Round-2 Phase 9 state. The Project Owner explicitly authorized AGENTS.md Path C direct Codex doc-only remediation for the 3 low-severity documentation findings in this pass.

### Audit content

**Scope:** Re-reviewed `Docs/_phases/PHASE_9.md`, `Docs/CHANGELOG.md`, `Docs/ARCHITECTURE.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, `CLAUDE.md`, `src/starry_lyfe/api/orchestration/internal_relationship_prompts.py`, `src/starry_lyfe/api/orchestration/internal_relationship.py`, `tests/unit/api/test_internal_relationship_prompts.py`, `tests/unit/api/test_internal_relationship_evaluator.py`, and `tests/unit/test_residue_grep.py`.

**Verification context:** Verification after the direct doc-only remediation:

- `.\.venv\Scripts\python.exe -m pytest tests/unit/api/test_internal_relationship_prompts.py tests/unit/api/test_internal_relationship_evaluator.py tests/unit/api/test_post_turn.py -q` -> `68 passed`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_residue_grep.py -q` -> `2 passed`
- `.\.venv\Scripts\python.exe -m pytest -q` -> `1119 passed`
- `.\.venv\Scripts\ruff.exe check src tests` -> clean
- `.\.venv\Scripts\python.exe -m mypy --strict src` -> clean

**Executive assessment:** No new functional or architectural issue surfaced in Round 3. The remaining items from Round 2 were purely documentation-traceability drift, and they are directly remediated in this pass under the Project Owner-authorized AGENTS.md Path C exception: the duplicate Row 5 handshake is removed, all Phase 9 verification/status surfaces now reflect the live `1119 passed` / `+6` RT1 regression delta / residue-clean state, and the placeholder governance hashes are replaced with `11a8af6`. With those doc-only issues closed, the Phase 9 gate is **PASS** and the phase is ready for Claude AI Step 5 QA.

**Findings (historical, directly remediated under Path C):**

| # | Severity | Finding | Historical evidence | Disposition |
|---:|---|---|---|---|
| 1 | Low | Duplicate Round 1 Row 5 Codex handshake entry in the canonical Phase 9 record. | Step 3' Round 2 finding #1. | Directly remediated by Codex under Project Owner-authorized Path C: the duplicate Row 5 entry was removed from the handshake log, preserving a single truthful Round 1 Codex audit row. |
| 2 | Low | Stale verification/count narrative (`1118 passed`, `+5`, residue-failure note) across the Phase 9 remediation surfaces. | Step 3' Round 2 finding #2. | Directly remediated by Codex under Project Owner-authorized Path C: `PHASE_9.md`, `Docs/CHANGELOG.md`, `CLAUDE.md`, `Docs/IMPLEMENTATION_PLAN_v7.1.md`, and `Docs/ARCHITECTURE.md` now all reflect `1119 passed`, `+6` RT1 regression tests, and no residue-grep failure claim. |
| 3 | Low | Placeholder commit references (`this commit`, `<this commit>`, `[this governance sweep commit]`) remained in the Phase 9 governance surfaces after the landed hashes were known. | Step 3' Round 2 finding #3. | Directly remediated by Codex under Project Owner-authorized Path C: the placeholders are replaced with `4b50132` for the Step 2 governance commit and `11a8af6` for the RT3 governance sweep. |

**Runtime probe summary:**

- Functional behavior remains unchanged and green: the F1 speaker-identity fix is still live, and the dormant Alicia-orbital path remains explicitly deferred rather than overclaimed.
- `tests/unit/test_residue_grep.py` remains green (`2 passed`), matching the corrected doc narrative.
- No production code or test files changed in this Path C remediation pass.

**Drift against specification:**

- None remains after the direct doc-only remediation. The substantive Round 1 closures still hold, and the Round 2 documentation drifts are now corrected.

**Verified resolved:**

- Round 1 F1 remains closed in code and tests.
- Round 1 F2 remains closed on the chosen deferred-scope governance path.
- Round 1 F3 remains closed in the shared phase record and downstream governance sync surfaces.
- Round 3 low-severity doc drifts are now closed directly under the Project Owner-authorized AGENTS.md Path C exception.

**Adversarial scenarios constructed:**

1. No-change remediation audit.
Result: no new Phase 9 code commit was required; the remaining issues were doc-only and are now corrected directly in the canonical/doc surfaces.
2. Residue-grep verification re-run.
Result: `tests/unit/test_residue_grep.py` passed (`2 passed`), matching the corrected documentation.
3. Downstream doc claim sweep.
Result: stale `1118` / `+5` / placeholder-hash claims are removed from the Phase 9 governance surfaces.

**Gate recommendation:** **PASS**

**Path C remediation note:** The Project Owner explicitly authorized Codex to apply the three Round 3 low-severity documentation fixes directly under the AGENTS.md Path C exception. No production code or tests changed in this direct-remediation pass.

<!-- HANDSHAKE: Codex → Claude AI | Audit Round 3 closed. Project Owner authorized AGENTS.md Path C direct Codex doc-only remediation for the three low-severity findings; fixes applied. Gate PASS. Ready for Step 5 QA. -->

---

## Step 4'': Remediate (Claude Code) — Round 3

**[STATUS: SKIPPED — Project Owner authorized AGENTS.md Path C direct Codex doc-only remediation; no Claude Code Round 3 remediation required]**

<!-- HANDSHAKE: SKIPPED | Project Owner authorized AGENTS.md Path C direct Codex doc-only remediation on 2026-04-15; no Claude Code Round 3 remediation pass occurred. -->

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

## Not in scope (deferred to a future phase)

- **Communication-mode-aware dormant Alicia-orbital dyad updates.** The hand-authored canonical `Alicia-orbital note` blocks in §Pre-execution describe how the three orbital dyads should respond on remote turns (letter / phone / video) when `is_currently_active=false`. **R1-F2 closure 2026-04-15** confirmed this path is unreachable in Phase 9's runtime: the SQL gate `is_currently_active.is_(True)` filters dormant orbital dyads out before any LLM call, and no `communication_mode` signal is threaded through the chat → scheduler → evaluator path. The canonical prose stays verbatim per CLAUDE.md §19 quality directive (canonical content is never trimmed) and remains load-bearing for a future phase. **Future-phase implementation sketch:** thread `communication_mode` from `PipelineResult.scene_state` (already populated at chat time) → `schedule_post_turn_tasks(communication_mode=...)` → `evaluate_and_update_internal(communication_mode=...)`; relax the SQL gate to `is_currently_active=True OR (dyad_key IN ALICIA_ORBITAL_DYAD_KEYS AND communication_mode IN ('phone', 'letter', 'video'))`; add `intimacy+ (letter/phone/video)` cues to the LLM prompt for those branches; add 4–6 regression tests covering the dormant-orbital-with-remote-mode path.
- **Per-speaker Crew evaluator fan-out.** Already deferred per the Phase 9 original scope: a Crew multi-speaker turn currently fires one evaluator call per focal character, not one per speaker. Future-phase candidate; out of Phase 9 scope.
- **Changes to the ±0.03 cap.** Project axiom per CLAUDE.md §16. Untouched in Phase 9.
- **Changes to `DyadStateInternal` schema.** AC-9.13 invariant. No Alembic migration in Phase 9.

---

_End of Phase 9 canonical record._
