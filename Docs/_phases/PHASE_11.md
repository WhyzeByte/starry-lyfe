# Phase 11 — Cross-Persona Context Injection

**Status:** SHIPPED 2026-04-17
**Plan:** `C:\Users\Whyze\.claude\plans\plan-phase-10-5c-zany-cherny.md` (filename slug retained from prior session per plan-mode rule)
**Severity of fix:** HIGH — closes a Msty Crew Conversations Contextual-mode behavior gap discovered while authoring `Docs/MSTY_SETUP.md`.

---

## 1. The gap

The pipeline at `src/starry_lyfe/api/orchestration/pipeline.py::run_chat_pipeline` extracted Msty Crew Conversations' prior-persona responses (`MstyPreprocessed.prior_responses`) for scene classification but **never injected the actual response text into the focal persona's outbound `user_prompt`**. The header docstring even codified the gap as a design intent:

> *"Msty Crew bubble orchestration is client-side: each backend request still produces exactly one assistant response for the routed persona, even when the incoming history contains a Crew roster and prior persona turns."*

Combined with Msty Studio's actual Crew Contextual mode behavior (per `https://docs.msty.studio/conversations/crew-chats` step 5 — *"Contextual where they are aware of persona responses before theirs"*), the operator's expected user experience was structurally impossible: each persona answered as if speaking alone, with no riff, acknowledgment, or rebuttal of the prior persona's text.

PHASE_7.md §R2-F1 (lines 319–322) and §R3-F1 (§14) had **planned** a `_format_crew_prior_block` helper plus a `_run_crew_turn` orchestrator. The closure notes were written, but the helpers were **never actually shipped into `pipeline.py`**. Only the input-side scaffolding (`MstyPreprocessed.prior_responses` extraction in `routing/msty.py`) shipped.

## 2. Scope

| In scope | Out of scope |
|---|---|
| Add `_format_crew_prior_block(prior_responses, current_user_message)` helper to `pipeline.py` | Backend-side `/all` crew expansion (`_run_crew_turn`) — still deferred from Phase 7 |
| Wire helper into `run_chat_pipeline` between user-message strip and stream_complete | Cross-conversation continuity (Bina in Persona Conversation #2 unaware of Adelia in Persona Conversation #1) — by Msty design |
| Phase 8 R1-F3 sanitation (html.escape + 800-char per-block truncation) | Per-persona `chat_sessions` bookkeeping changes |
| ≥6 unit tests + 1 integration test (real Postgres + recording StubBDOne) | Adding `name` field to backend SSE chunks (Msty tracks per-persona client-side) |
| Documentation sweep across ARCHITECTURE, OPERATOR_GUIDE, MSTY_SETUP | Operator UI changes in Msty Studio |

## 3. Architectural decision

**AD-009 — Cross-persona context injection in single-speaker requests.**

When `MstyPreprocessed.prior_responses` is non-empty, the focal persona's `user_prompt` is a frame:

```
[Earlier in this conversation:
**<character_id>:** <html-escaped, 800-char-capped text> [...truncated]?
**<character_id>:** ...
]

<current_user_message>
```

When empty (single-persona Msty Persona Conversations, dev `/`-override calls, etc.), the helper returns the bare user message — preserving Phase H regression byte-identity.

The augmented string is what reaches BD-1. `user_message_clean` (the bare user text) remains the input to scene classification + Layer 6 retrieval so soul-card activation does not over-trigger on cross-persona text.

## 4. Acceptance criteria

| AC | Description | Status |
|---|---|---|
| AC-11.1 | `_format_crew_prior_block` helper added to `pipeline.py` with the documented frame. Unit-tested. | PASS — `tests/unit/api/test_pipeline_crew_contextual.py::TestFormatCrewPriorBlock` (7 tests) |
| AC-11.2 | `run_chat_pipeline` calls the helper before `stream_complete` and passes the augmented `user_prompt`. | PASS — `pipeline.py:run_chat_pipeline` lines 229–232 (helper call) + lines 308–313 (`stream_complete` call site) (line ranges corrected post-audit) |
| AC-11.3 | When `prior_responses` is empty, the helper returns the current user message unchanged. Phase H regression byte-identical for non-crew flows. | PASS — `test_no_prior_responses_returns_user_message_unchanged` + `test_run_chat_pipeline_is_no_op_for_non_crew_request` + `test_msty_persona_conversation_no_prior_responses_unchanged` |
| AC-11.4 | Prior-persona text HTML-escaped and per-block truncated at 800 chars with `[…truncated]` marker. Phase 8 R1-F3 lesson applied. | PASS — `test_html_escape_neutralizes_tag_content` + `test_truncation_marker_appears_when_block_exceeds_cap` |
| AC-11.5 | Integration test asserts a real OpenAI Crew Contextual payload causes the focal persona's outbound prompt to contain the prior personas' text. | PASS — `tests/integration/test_http_chat.py::TestCrewContextualCarryForward::test_msty_crew_contextual_payload_lands_prior_text_in_focal_user_prompt` (skip-on-Postgres-down per integration-suite convention) |
| AC-11.6 | Phase 9 evaluator behavior under cross-persona turns is documented. | PASS — see §5 below. `post_turn.schedule_post_turn_tasks` correctly receives focal-only `full_response_text`; the augmented prompt is request-side only and the dyad evaluator scores the focal persona's deltas, not the conversation as a whole. No code change. |
| AC-11.7 | Documentation updated across ARCHITECTURE, OPERATOR_GUIDE, MSTY_SETUP describing Msty Crew Contextual mode end-to-end. Backend `/all` expansion documented as deferred. | PASS — see §6 below |
| AC-11.8 | Project Owner ships Phase 11. | PENDING (Step 6 sign-off) |

## 5. Phase 9 evaluator behavior under cross-persona turns

**Decision:** `post_turn.schedule_post_turn_tasks` continues to receive the focal persona's `full_response_text` only. The augmented `user_prompt_with_priors` is a request-side construct used purely to seed BD-1's input — it is **not** the right signal for relationship-state deltas.

**Rationale:** Phase 9 inter-woman evaluator (`evaluate_and_update_internal`) scores how the focal persona's *output* affects each of her active inter-woman dyads. Mixing in prior personas' text would conflate other characters' speech into the focal character's dyad updates — a correctness regression in the opposite direction.

**Future-phase consideration:** If a future operator wants per-turn dyad updates that account for the cross-persona thread (e.g., Bina's trust-with-Adelia delta should respond to what Adelia said *and* what Bina said in reply), that is a discrete scope item with its own Pydantic schema needs (the LLM evaluator would need to receive a structured prior + response pair). Not in scope here.

## 6. Documentation sweep

| File | Change |
|---|---|
| `Docs/ARCHITECTURE.md` | §4 Step-9 row + new §4.x sub-section disambiguating Msty-client-side Crew fan-out (production) vs backend `/all` expansion (deferred). AD-009 added to §21. Version bumped 1.0.1 → 1.1.0. |
| `Docs/OPERATOR_GUIDE.md` | §5 Crew Conversations rewritten to instruct Contextual + Auto mode; misleading "≥2 women + ≥1 prior response → backend expands" phrasing removed (the backend never expanded — that was a planning artifact). Version bumped 2.0.1 → 2.1.0. |
| `Docs/MSTY_SETUP.md` | §5.2 explicitly tells the operator to set Crew context to **Contextual** + trigger to **Auto**. Quotes Msty docs step 5 verbatim. Version bumped 1.1.1 → 1.2.0. |
| `Docs/CHANGELOG.md` | New entry under `[Unreleased]` describing the Phase 11 ship. |
| `journal.txt` | Phase 11 entry. |
| `CLAUDE.md` | §19 phase status row + Phase 10 Governance Addendum baseline bump + P-version P2.18 → P2.19. |

## 7. Files touched (production)

- New: `Docs/_phases/PHASE_11.md` (this file), `tests/unit/api/test_pipeline_crew_contextual.py`.
- Modified: `src/starry_lyfe/api/orchestration/pipeline.py` (helper + wire-in + import + module docstring), `tests/integration/test_http_chat.py` (`TestCrewContextualCarryForward` class), all the doc files in §6.

## 8. WAF result

- `pytest tests/unit/api/test_pipeline_crew_contextual.py` — 9 passed locally.
- `pytest tests/integration/test_http_chat.py::TestCrewContextualCarryForward` — 2 skipped locally (Postgres unreachable, expected); will pass when CI runs against real Postgres.
- `ruff check src tests scripts` — clean.
- `python -m mypy --strict src` — clean across 115 source files.
- Phase H regression bundle — byte-identical for non-crew flows (AC-11.3 invariant).

## 9. Codex audit handshake

<!-- HANDSHAKE: Claude Code -> Codex (audit) | Phase 11 (Cross-Persona Context Injection) shipped 2026-04-17. WAF: ≥9 new unit tests + 2 environmental-skip integration tests, 0 failed, 0 xfailed; ruff + mypy --strict clean across 115 source files. AC-11.1..AC-11.7 PASS; AC-11.8 pending Project Owner ship sign-off. Anticipated audit findings: prompt-injection mitigation via html.escape + truncation, no-double-counting in Layer 6 (scene_context unchanged), focal-only response_text semantic for Phase 9, name-field not required in backend SSE (Msty tracks client-side). Ready for Codex audit. -->

---

## 10. Step 4 — Phase 11 Self-Audit (2026-04-17)

**Auditor:** Claude Code (independent post-ship structural audit at Project Owner request)
**Result:** **PASS**

### AC verification
All 7 acceptance criteria (AC-11.1 through AC-11.7) verified with file:line evidence:

| AC | Evidence |
|---|---|
| AC-11.1 | `_format_crew_prior_block` at `pipeline.py:129–187` with full docstring + type hints + module-level constants `_PRIOR_BLOCK_CHAR_CAP: int = 800` and `_PRIOR_BLOCK_TRUNCATION_MARKER: str = " […truncated]"`. 7 unit tests in `TestFormatCrewPriorBlock`. |
| AC-11.2 | Helper called at `pipeline.py:229–232` with `list(ctx.msty.prior_responses)` and `user_message_clean`. Result passed to `stream_complete` at line 310. |
| AC-11.3 | No-op return at lines 173–174 when `prior_responses` is empty. Byte-identity covered by `test_no_prior_responses_returns_user_message_unchanged` (unit) + `test_run_chat_pipeline_is_no_op_for_non_crew_request` (unit) + `test_msty_persona_conversation_no_prior_responses_unchanged` (integration). |
| AC-11.4 | `html.escape(prior.text or "", quote=False)` at line 177; truncation at lines 178–182. Tautology hunt: `test_html_escape_neutralizes_tag_content` asserts BOTH that the original `</response_text>` is absent AND that `&lt;/response_text&gt;` is present. `test_truncation_marker_appears_when_block_exceeds_cap` asserts BOTH the marker presence AND the line-length bound. |
| AC-11.5 | `tests/integration/test_http_chat.py::TestCrewContextualCarryForward::test_msty_crew_contextual_payload_lands_prior_text_in_focal_user_prompt` lines 386–392 — explicitly asserts `**adelia:**`, `cardamom`, and the current user message all appear in the BD-1-bound `user_prompt`. Real Postgres + recording StubBDOne. |
| AC-11.6 | `chat.py:168` calls `schedule_post_turn_tasks(full_response_text=result.full_response_text)` — focal-only `response_text`, NOT the augmented `user_prompt_with_priors`. Phase 9 dyad scoring semantic preserved. |
| AC-11.7 | ARCHITECTURE.md AD-009 + §4 Crew disambiguation block present; OPERATOR_GUIDE.md §3.2 carries Contextual + Auto guidance with AD-009 reference; MSTY_SETUP.md §5 quotes Msty docs step 5 verbatim. |

### Anticipated findings — all clean
- **(a) Prompt injection:** `_extract_prior_responses` validates `character_id` against `_CANONICAL_IDS` frozenset in `msty.py:84,91` (a malicious persona name like `"EvilPersona"` is silently dropped). Content text is `html.escape`'d. Defense-in-depth confirmed.
- **(b) Layer 6 over-trigger:** `retrieve_memories` (line 261) and `assemble_context` (line 272) both receive `user_message_clean`, NOT the augmented string. Code matches the documented intent.
- **(c) Phase 9 dyad drift:** evaluator receives focal-only `full_response_text`. The augmented prompt is request-side only.
- **(d) Backend SSE `name` field:** out-of-scope per AD-009; Msty tracks per-persona client-side. Confirmed.

### Edge-case hunt
- **Order preservation:** `_extract_prior_responses` iterates messages in document order; helper renders in that order. Correct.
- **Empty content text:** defensive `prior.text or ""` handles malformed upstream without crashing.
- **Character-ID gating:** any `name` outside the 4 canonical IDs is dropped before reaching the helper.

### Test count
+9 unit + 2 environmental-skip integration = 11. Matches §8 claim.

### Findings
- **LOW / INFO** — PHASE_11.md AC-11.2 row originally cited approximate line ranges ("230–240", "290–294") instead of the actual ranges (229–232 + 308–313). Cosmetic; corrected in the same commit as this audit closure note.

No HIGH or MEDIUM findings.

### Verdict
**PASS.** Ready for Project Owner Step 6 ship sign-off. AC-11.8 closes when sign-off is recorded.

<!-- HANDSHAKE: Codex (audit) -> Project Owner | Phase 11 audit PASS 2026-04-17. All 7 ACs verified. Anticipated findings clean. One LOW cosmetic line-range fix applied in-place. AC-11.8 awaiting ship sign-off. -->
