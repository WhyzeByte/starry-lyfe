# Operator Guide — Starry-Lyfe

**Version:** 2.1.0
**Date:** 2026-04-17
**Status:** Operator runtime walkthrough for the post-Phase-11 (Cross-Persona Context Injection) tree.
**Audience:** the operator (Whyze) and any engineer who has to run, monitor, or troubleshoot Starry-Lyfe day-to-day.
**Companion documents:** `Docs/ARCHITECTURE.md` (top-down as-built reference); `Docs/_phases/` (chronological delivery record); `CLAUDE.md` (governance).
**Runtime baseline:** 1267 passed / 41 environmental Postgres skips / 0 failed / 0 xfailed (target — see PHASE_11.md for the post-merge count).

---

## 0. How to read this guide

This document teaches you how to **operate** the system. It does not re-document architecture (that's `ARCHITECTURE.md`) and it does not record history (that's `Docs/_phases/`). Each section answers an operator question:

- "How do I run this locally?" → §1 Quickstart
- "What happens when Msty sends a request?" → §2 Request walkthrough
- "How do I set up Msty?" → §3 Msty Persona Studio
- "What does this log line mean?" → §4 Logging and §13 Glossary
- "Did the nightly Dreams pass succeed?" → §5 Dreams operations
- "There's a pin in `dyad_state_pins` — what do I do?" → §6 Phase 10.7 QA workflow
- "An evaluator emitted `dreams_qa_pin_blocked` — is that bad?" → §7 Relationship evaluators
- "I edited a character YAML — now what?" → §8 Canon edit workflow
- "Health check is red." → §9 Health and metrics
- "Something's broken." → §10 Troubleshooting
- "How do I back up the DB?" → §11 Backup and restore
- "How do I commit a change?" → §12 Dev workflow

Each example uses live repo paths and Windows/PowerShell-safe commands unless explicitly marked illustrative.

---

## 1. Quickstart

### 1.1 First-time setup

```powershell
# 1. Create venv + install (uses requirements-dev.txt + editable install)
make install

# 2. Bring up the database container (PostgreSQL 16 + pgvector)
make docker-up

# 3. Apply migrations (head = 005_phase_10_7_dreams_qa)
make db-migrate

# 4. Seed Tier 1-4 + Tier 7 from the rich YAMLs
make db-seed
```

The runtime env must exist before steps 3–4. Ensure `.env` carries at least:

- `STARRY_LYFE__API__API_KEY` — any non-empty value (Msty must send this in `X-API-Key`).
- `STARRY_LYFE__BD1__API_KEY` — the BD-1 provider key actually read by `BDOneSettings.from_env()`.
- `STARRY_LYFE__BD1__BASE_URL` — optional if you are using the default `https://openrouter.ai/api/v1`.
- `STARRY_LYFE__DREAMS__LLM_MODEL` — optional if you are using the default model.

LM Studio (for embeddings) should be running locally on port 1234 with the model `text-embedding-nomic-embed-text-v1.5@q5_k_m` loaded. The writer path falls back to a zero vector if LM Studio is unreachable, but similarity search will be inert for those rows.

### 1.2 Daily startup (already-installed system)

```powershell
# Database
make docker-up   # idempotent; skips if already running

# HTTP service (foreground, watchable logs)
.venv/Scripts/python -m starry_lyfe.api.main
# Or via uvicorn's factory mode:
.venv/Scripts/python -m uvicorn starry_lyfe.api.app:create_app --factory --host 0.0.0.0 --port 8001

# Dreams daemon (separate terminal — long-running)
.venv/Scripts/python -m starry_lyfe.dreams
```

### 1.3 Smoke check after boot

```powershell
# Liveness (always 200 if process is alive)
curl.exe http://localhost:8001/health/live

# Readiness (200 only if R5 + BD-1 reachable)
curl.exe http://localhost:8001/health/ready

# Models registry (5 entries: starry-lyfe + 4 character IDs)
curl.exe http://localhost:8001/v1/models

# Real chat (replace YOUR_KEY)
curl.exe -N http://localhost:8001/v1/chat/completions `
  -H "X-API-Key: YOUR_KEY" `
  -H "Content-Type: application/json" `
  --data-raw '{
    "model": "adelia",
    "stream": true,
    "messages": [{"role":"user","content":"Hey, how was the porch this morning?"}]
  }'
```

### 1.4 Run the test suite

```powershell
make check          # current Makefile gate: ruff + mypy + unit pytest bundle
make test           # unit only
make test-integration  # integration only (skips when Postgres unreachable)
.venv/Scripts/python -m pytest -q  # full suite
```

Current baseline: **1,258 passed / 39 environmental Postgres skips / 0 failed / 0 xfailed**.

---

## 2. Request walkthrough — what Msty sends → what the model receives

The 12-step pipeline lives at `src/starry_lyfe/api/orchestration/pipeline.py:run_chat_pipeline()` (line 137). Here is one concrete request traced end-to-end.

### 2.1 The HTTP request

Msty Persona Conversation sends:

```json
POST /v1/chat/completions
X-API-Key: <key>
Content-Type: application/json
{
  "model": "adelia",
  "stream": true,
  "messages": [
    {"role": "user", "content": "Hey, how was the porch this morning?"}
  ]
}
```

For Crew Conversations, Msty also includes:
- An empty `system` message (Persona Studio System Prompt Mode = `Replace`, blank in production per **AD-001**).
- Prior persona responses as `assistant` messages with a `name` field (e.g., `{"role": "assistant", "name": "bina", "content": "..."}`).
- The current user message for the persona bubble being generated.

### 2.2 What the pipeline does (steps 1–12)

| # | What | Observable surface |
|---|---|---|
| 1 | Endpoint validates `X-API-Key`, preprocesses the Msty payload, resolves routing, upserts `chat_sessions` best-effort | Response headers `X-Request-ID`, `X-Character-ID`, `X-Routing-Source`, `X-Session-ID`; `chat.py` |
| 1b | `preprocess_msty_request()` extracts prior responses + system-prompt roster hints | No dedicated success log today; inspect `api/routing/msty.py` or the downstream scene-context behavior |
| 2a | `retrieve_alicia_home()` reads Tier 8 `life_states.is_away` | Success is silent; failure logs `alicia_home_resolution_failed` |
| 2b | `classify_scene()` returns a `SceneState` (8 scene types × 6 modifiers) | Success is silent; failure logs `scene_classification_failed` |
| 3 | `retrieve_memories()` pulls canon facts + baseline + dyad states + semantic episodic top-k + open loops + somatic + life state + Dreams activities into `MemoryBundle` | Success is silent; failure logs `memory_retrieval_failed` |
| 4 | `MemoryBundle.activities` remains available inside retrieval / assembly context | No dedicated log today |
| 5 | `assemble_context()` builds the 7-layer prompt for the focal character | Success is silent; failure logs `context_assembly_failed`; see §2.3 |
| 6 | `BDOne.stream_complete()` opens the upstream SSE stream | Success is silent; failures log `upstream_stream_failed` |
| 7 | LLM honors Layer 7 terminal constraints; backend has no client-side enforcement at this stage | — |
| 8 | `validate_response()` runs Whyze-Byte on the buffered response | Tier-1 FAIL produces terminal SSE chunk `WHYZE_BYTE_FAIL`; unexpected validator exception logs `validation_failed_unexpectedly` |
| 9 | Msty handles Crew bubble sequencing client-side; backend returns one routed persona response per request | No dedicated backend event beyond the normal single-speaker path |
| 10 | SSE stream terminates with `finish_reason` + `data: [DONE]` | Client-visible SSE close; no dedicated completion log today |
| 11 | (Msty-side Shadow Persona bookkeeping; backend not involved.) | — |
| 12 | `schedule_post_turn_tasks()` spawns 3 fire-and-forget `asyncio.create_task` jobs: `extract_episodic`, Phase 8 `evaluate_and_update`, Phase 9 `evaluate_and_update_internal` | No dedicated schedule event; downstream failures log `post_turn_task_failed`, and evaluator/memory subtasks emit their own events |

The HTTP response closes after step 10. Steps 11–12 happen after the user has already received the streamed reply.

### 2.3 The 7-layer assembled prompt (concrete example)

Each layer is wrapped in an XML-style marker. Markers come from `context/assembler.py:38::LAYER_MARKERS`. The assembled prompt looks like this (truncated for readability):

```
<PERSONA_KERNEL>
Adelia Raye. ENFP-A, lives at the property, runs Ozone & Ember (Adelia's
business)...
[soul essence — guaranteed surcharge, never trimmed]
[pair callbacks — guaranteed surcharge]
[kernel body, 11 numbered sections, trimmable to per-character budget]
</PERSONA_KERNEL>

<CANON_FACTS>
- Marriage year: 2022
- Property: Foothills County near Priddis, Alberta
- Children: Isla (b. 2019-07-31), Daphne (b. 2021-08-18); childcare always assumed
...
</CANON_FACTS>

<MEMORY_FRAGMENTS>
- 2026-04-15 (diary): "The kitchen smelled like cardamom..."
- 2026-04-16 (off_screen): "Alicia called from Buenos Aires; mode=phone"
...
</MEMORY_FRAGMENTS>

<SENSORY_GROUNDING>
fatigue=0.32, stress_residue=0.15, injury_residue=0.00 (decayed read)
life_state: mood=settled, energy=medium, focus=family
</SENSORY_GROUNDING>

<VOICE_DIRECTIVES>
Inference parameters: temperature=0.82, top_p=0.95, frequency_penalty=0.4, presence_penalty=0.3
Mode: domestic
[2-4 voice exemplars matching mode]
</VOICE_DIRECTIVES>

<SCENE_CONTEXT>
Today's Dreams scene opener: "..."
[Activated knowledge soul cards based on scene_keyword/comm_mode/with_character]
[Open loops with status='open']
</SCENE_CONTEXT>

<CONSTRAINTS>
[Tier 1 axioms + per-character YAML constraint pillars + scene/modifier gates — terminal anchor, NEVER trimmed]
</CONSTRAINTS>
```

Token budget per layer (defaults, `context/budgets.py:38::LayerBudgets`):

| Layer | Budget | Notes |
|---|---|---|
| 1 Kernel | 6,000 | scaled per-character (Adelia 6,300 / Bina 7,200 / Reina 6,900 / Alicia 5,100) PLUS guaranteed soul-essence surcharge (~1,750–2,050) PLUS pair-callbacks surcharge |
| 2 Canon facts | 600 | |
| 3 Episodic | 1,200 | |
| 4 Somatic | 500 | |
| 5 Voice | 900 | |
| 6 Scene | 2,400 | doubled Phase C 2026-04-12 to fit knowledge soul cards |
| 7 Constraints | 900 | terminal anchor — NEVER trimmed |

**Effective Layer 1 ceiling per character:**

| Character | Kernel budget | Soul essence | L1 ceiling |
|---:|---:|---:|---:|
| Adelia | 6,300 | ~1,900 | ~8,200 |
| Bina | 7,200 | ~1,900 | ~9,100 |
| Reina | 6,900 | ~1,750 | ~8,650 |
| Alicia | 5,100 | ~2,050 | ~7,150 |

### 2.4 What you can change at request time

- **`model` field** routes to the focal character (`adelia` | `bina` | `reina` | `alicia` | `starry-lyfe` legacy). Production Msty path.
- **Inline override** at the start of the user message: `/adelia`, `/bina`, `/reina`, `/alicia`. Stripped before the LLM sees it. Dev/test path; not used in production Msty.
- **`X-SC-Force-Character`** header — dev/test only. Highest precedence; bypasses model field. Never set this in production Msty.

If Alicia is currently away on operations, scenes set in-person will raise `AliciaAwayContradictionError` at the classifier (HTTP 400). Use `/alicia` only when she is home or use `communication_mode` keywords (phone / letter / video_call) to route to a remote-mode scene.

---

## 3. Msty Persona Studio integration

### 3.1 Per-character Persona setup (production)

For each of Adelia, Bina, Reina, Alicia:

1. **Persona Studio → New Persona**.
2. **Name:** the character's display name (e.g., "Adelia Raye").
3. **Model ID:** `adelia` (or `bina`, `reina`, `alicia`). Must match the canonical character IDs exactly — case-sensitive lowercase.
4. **System Prompt Mode:** `Replace` (this is the load-bearing setting per **AD-001**).
5. **System Prompt content:** **leave blank** in production. The backend is the sole voice authority; any content here will fight the assembled prompt.
6. **Endpoint URL:** `http://localhost:8001/v1/chat/completions` (or wherever the API is reachable).
7. **Headers:** add `X-API-Key: <your-key>` matching `STARRY_LYFE__API__API_KEY`.
8. **Streaming:** enabled (SSE).
9. **Temperature / top_p / penalties:** the canonical voice parameters live in the rich YAML `voice.inference_parameters` surface and render into Layer 5, but the live chat pipeline still passes `request.temperature` through to BD-1 when the client supplies it (default `0.7` otherwise). So Msty-side API params are not hard-overridden by canon today.

### 3.2 Crew Conversation setup

1. **Persona Studio → New Crew**.
2. **Add 2-4 personas** from the per-character set above.
3. **Crew System Prompt:** leave blank (same rule).
4. **Endpoint:** same as persona conversations.
5. **Context: Contextual** (per Msty docs step 5 — *"Contextual where they are aware of persona responses before theirs"*). This is the load-bearing setting for normal conversation behavior. With **Independent**, each persona answers as if speaking alone.
6. **Trigger: Auto** so personas respond automatically in roster order on each user turn.

**How the cross-persona thread reaches the backend (Phase 11, AD-009).** Msty owns the persona-per-bubble sequencing — it fans out one HTTP request per persona's turn, with the prior personas' responses included as `role="assistant"` messages with a `name` field. The backend's `_format_crew_prior_block` helper extracts those into a framed `[Earlier in this conversation: …]` block prepended to the focal persona's `user_prompt`, so each new persona sees what the prior personas said and can riff on it. When `prior_responses` is empty (single-persona Persona Conversations), the helper is a no-op.

### 3.3 Helper script

`scripts/seed_msty_persona_studio.py` produces ready-to-paste persona definitions from the rich YAMLs. Run as:

```powershell
.venv/Scripts/python scripts/seed_msty_persona_studio.py
```

Output is JSON the operator can hand-import into Persona Studio. The current script emits all four women's few-shot configs in one payload; there is no `--character` filter today.

---

## 4. Logging and observability

### 4.1 What's logged

The current tree uses standard Python `logging`, not `structlog`. Both entry points (`starry_lyfe.api.main` and `starry_lyfe.dreams.daemon`) boot with `logging.basicConfig(level=logging.INFO)`, write to stdout/stderr by default, and attach selected `extra={...}` fields on some events. There is no env-driven log-level hookup wired into boot today.

### 4.2 Key event names by subsystem

| Subsystem | Event name | Level | Meaning |
|---|---|---|---|
| API request | `upsert_session_failed` | WARNING | `chat_sessions` write failed before streaming; request still proceeds |
| Pipeline | `alicia_home_resolution_failed` | WARNING | Tier 8 `life_states` read failed; pipeline defaulted Alicia to home |
| Pipeline | `scene_classification_failed` | WARNING | Scene classification raised; pipeline emits terminal SSE error chunk |
| Pipeline | `memory_retrieval_failed` | WARNING | `retrieve_memories()` failed; pipeline degrades with empty bundle |
| Pipeline | `context_assembly_failed` | WARNING | Prompt assembly raised; pipeline emits terminal SSE error chunk |
| Stream | `upstream_stream_failed` | WARNING | BD-1 stream connect/start failed; pipeline emits terminal SSE error chunk |
| Validation | `validation_failed_unexpectedly` | WARNING | Whyze-Byte raised unexpectedly on the single-speaker path |
| Post-turn | `post_turn_task_failed` / `post_turn_task_cancelled` | WARNING | Fire-and-forget task failed or was cancelled after the SSE response closed |
| Extraction | `extract_episodic_unknown_character` / `extract_episodic_llm_failed` | WARNING | Episodic extraction skipped due to bad character id or BD-1 failure |
| Phase 8 | `llm_eval_parsed_proposal` | INFO | Successful Phase 8 LLM eval; 4-field proposal attached |
| Phase 8 | `llm_eval_fallback_to_heuristic` | INFO | Phase 8 fell back; `reason` explains why |
| Phase 9 | `internal_llm_eval_parsed_proposal` | INFO | Successful Phase 9 LLM eval; 5-field proposal attached |
| Phase 9 | `internal_llm_eval_fallback_to_heuristic` | INFO | Phase 9 fell back; `reason` explains why |
| Phase 10.7 | `dreams_qa_verdict` | INFO/WARNING/ERROR | Per-relationship verdict; level scales by verdict (healthy=INFO, drift=WARNING, contradiction=ERROR) |
| Phase 10.7 | `dreams_qa_pin_created` | INFO | New pin written to `dyad_state_pins` |
| Phase 10.7 | `dreams_qa_pin_blocked` | WARNING | Phase 9 evaluator skipped one or more pinned dimensions; `dyad_key`, `blocked_fields`, `speaker_id` in extras |
| Phase 10.7 | `dreams_qa_auto_promoted` | WARNING | 3-night drift threshold hit; verdict promoted to `factual_contradiction` |
| Phase 10.7 | `dreams_qa_memory_lookup_failed` | WARNING | Per-relationship memory window unavailable; QA pass continues with empty memories |
| Phase 10.7 | `dreams_qa_markdown_lock_unavailable` | WARNING | File lock not acquired (stripped Python build); ledger writes proceed unsynchronized |
| Dreams | `dreams_run_started` | INFO | Nightly pass beginning; `run_id` in extras |
| Dreams | `dreams_run_complete` | INFO | Pass finished; `total_input_tokens`, `total_output_tokens`, `warnings_count`, `qa_pass_completed` |
| Dreams | `dreams_consistency_qa_failed` | ERROR | The QA pass threw an unhandled exception (does NOT crash the rest of the pass) |
| Dreams | `dreams_qa_scene_fodder_routing_failed` | ERROR | F1 routing helper failed (fodder routing is best-effort) |
| Dreams | `dreams_qa_weekly_digest_emitted` | INFO | Sunday-UTC weekly digest written; `path` in extras |
| Dreams | `dreams_scheduler_started` | INFO | apscheduler started; `schedule` cron + `misfire_grace_s` in extras |
| Dreams | `dreams_scheduler_disabled` | WARNING | `STARRY_LYFE__DREAMS__ENABLED=false` — scheduler idles |
| Dreams | `dreams_cli_pass_complete` | INFO | `--once` pass finished; aggregate result |
| Health | (no events; structured response is the signal) | | |

### 4.3 What to grep for

```powershell
# If you redirected stdout/stderr to .\logs\starry-lyfe.log:

# Did Phase 9 skip any pinned writes today?
Select-String -Path .\logs\starry-lyfe.log -Pattern "dreams_qa_pin_blocked"

# Did the QA pass succeed last night?
Select-String -Path .\logs\starry-lyfe.log -Pattern "dreams_run_complete" | Select-Object -Last 1

# Was either evaluator falling back to heuristics?
Select-String -Path .\logs\starry-lyfe.log -Pattern "llm_eval_fallback_to_heuristic|internal_llm_eval_fallback_to_heuristic" | Select-Object -Last 10

# Did any post-turn task die after the client already received a reply?
Select-String -Path .\logs\starry-lyfe.log -Pattern "post_turn_task_failed"
```

### 4.4 Prometheus metrics

`GET /metrics` exposes (no auth):

| Series | Labels | Meaning |
|---|---|---|
| `http_requests_total` | `method`, `path`, `status` | Standard Prom counter |
| `http_chat_completions_total` | `character_id`, `routing_source`, `outcome` | Per-chat request counter from response headers |
| `http_sse_tokens_total` | `character_id` | Per labeled character. Counts upstream LLM stream deltas, not model tokens (name retained for series stability). |
| `http_request_duration_seconds` | `method`, `path` | Total request-duration histogram |
| `http_chat_ttfb_seconds` | `character_id` | Chat-route TTFB approximation (currently observed as request duration) |

---

## 5. Dreams operations

### 5.1 Daemon vs `--once`

```powershell
# Production (long-running daemon, default schedule "30 3 * * *" = 03:30 daily in the scheduler's local timezone)
.venv/Scripts/python -m starry_lyfe.dreams

# Manual one-shot (smoke test, catch-up after crash, ad-hoc QA pass)
.venv/Scripts/python -m starry_lyfe.dreams --once

# Dry-run with StubBDOne (no LLM calls, no DB writes — fast smoke test)
.venv/Scripts/python -m starry_lyfe.dreams --once --dry-run
```

### 5.2 Environment variables

| Var | Default | Purpose |
|---|---|---|
| `STARRY_LYFE__DREAMS__SCHEDULE` | `30 3 * * *` | Cron expression (5-field) |
| `STARRY_LYFE__DREAMS__ENABLED` | `true` | `false` makes the daemon idle (logs `dreams_scheduler_disabled`) |
| `STARRY_LYFE__DREAMS__DRY_RUN` | `false` | Persistent dry-run mode (vs the per-invocation `--dry-run` flag) |
| `STARRY_LYFE__DREAMS__MAX_TOKENS_PER_CHAR` | `8000` | Per-character generator budget |
| `STARRY_LYFE__DREAMS__MISFIRE_GRACE_S` | `3600` | apscheduler grace window for missed runs |

### 5.3 What runs each night

For each canonical character (Adelia, Bina, Reina, Alicia), in parallel via `asyncio.gather`:

1. `default_snapshot_loader` reads 24h of memories, open loops, dyad states, life state.
2. Five generators run concurrently: `schedule`, `off_screen`, `diary`, `open_loops`, `activity_design`.
3. Writers persist the outputs inside a `session.begin()` transaction.
4. Consolidation helpers run on the same session: somatic decay, loop expiry, addressed-loop resolution.

After all per-character passes complete, the **Phase 10.7 Consistency QA** runs across the 10 relationships (6 inter-woman + 4 woman-Whyze). See §6.

On Sunday UTC, the `weekly_qa_digest()` hook fires and writes `Docs/_dreams_qa/_weekly/YYYY-WW.md`.

### 5.4 Verifying a pass succeeded

```bash
# Grep the most recent run
grep "dreams_run_complete" /path/to/log | tail -1

# Or check the DB
psql -U starry_lyfe -d starry_lyfe -c "
  SELECT run_id, count(*) AS rows
  FROM starry_lyfe.dreams_qa_log
  WHERE created_at >= now() - interval '1 day'
  GROUP BY run_id;
"
# Expect: 10 rows (one per relationship)
```

### 5.5 Dry-run without polluting state

`--dry-run` swaps `BDOne` for `StubBDOne` (canned responses) and short-circuits writes. Use it for:
- Verifying the daemon boots cleanly after a config change
- Validating new character YAML loads without breaking the pipeline
- Local development without burning LLM budget

---

## 6. Phase 10.7 Consistency QA workflow

### 6.1 What gets written each night

Per nightly Dreams pass:
- **`dreams_qa_log`** — exactly 10 rows per `run_id` (one per relationship). Verdict + summary + contradictions JSONB + scene_fodder JSONB.
- **`dyad_state_pins`** — zero or more rows for `factual_contradiction` verdicts. Each row pins one `(relationship_key, pov_character_id, field_name)` with `operator_resolved_at IS NULL`.
- **`open_loops`** — one row per non-empty `scene_fodder` string from `healthy_divergence` verdicts, anchored on the relationship's `pov_a`, with `loop_type="dreams_qa_scene_seed:dreams_qa"` and `best_next_speaker=pov_b`.
- **Daily markdown ledger** at `Docs/_dreams_qa/YYYY-MM-DD_consistency.md` with three sections: `## Healthy`, `## Drift watch`, `## Operator review required`.

### 6.2 Reading the daily ledger

The operator should review the ledger each morning. Skip the Healthy section unless a fodder string is interesting; skim the Drift watch section for accumulating concerns; act on the Operator review required section immediately.

A `factual_contradiction` entry looks like:

```markdown
- **whyze_alicia**
  - Alicia recalls the marriage year as 2023.
  - Contradictions:
    - `marriage_year` (alicia): observed '2023' vs canonical '2022' (shared_canon.marriage.year)
```

That entry corresponds to a row in `dyad_state_pins` blocking Phase 9 from updating `marriage_year` until the operator resolves.

### 6.3 Resolving a pin

Phase 10.7 ships with no operator UI for pin resolution. The CLI path uses the `pinning` module directly:

```python
# Resolve a pin from a Python REPL or one-off script
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from starry_lyfe.db.config import get_db_settings
from starry_lyfe.db.engine import build_engine, build_session_factory
from starry_lyfe.dreams.consistency.pinning import unpin_field, list_active_pins

async def main():
    engine = build_engine(get_db_settings())
    Session = build_session_factory(engine)
    async with Session() as session, session.begin():
        # See what's pinned
        active = await list_active_pins(session)
        for p in active:
            print(p["id"], p["relationship_key"], p["field_name"], p["pinned_value"])

        # Resolve one active pin by id
        pin_id = active[0]["id"]
        await unpin_field(
            session,
            pin_id=pin_id,
            operator_resolution_note="Operator confirmed the canonical value; runtime updates may resume.",
        )
    await engine.dispose()

asyncio.run(main())
```

Once `operator_resolved_at` is set, the unique partial index `(relationship_key, pov_character_id, field_name) WHERE operator_resolved_at IS NULL` releases the slot — Phase 9 can write the dimension again on the next post-turn evaluation.

A future operator-tools phase will turn this into a CLI subcommand. Until then, this is the path. (Acceptable per Phase 10.7 plan §Out of scope.)

### 6.4 The 3-night auto-promotion heuristic

If the same `(relationship_key, field_name)` is flagged as `concerning_drift` in each of the last 2 nightly passes (within a 36-hour window per night to tolerate cron jitter and DST), the **third** flag's verdict auto-promotes to `factual_contradiction` and lands a pin. You'll see `dreams_qa_auto_promoted` in the logs and a new entry in the daily ledger's Operator review required section.

If a relationship is genuinely drifting in canonical-acceptable ways (e.g., the relationship is supposed to evolve), unpin and document why in `resolution_note`.

### 6.5 Weekly trajectory digest

Every Sunday UTC, `consistency/digest.py::build_weekly()` reads the last 7 daily ledger files and emits a per-relationship trajectory at `Docs/_dreams_qa/_weekly/YYYY-WW.md`.

Trajectory labels:
- **`improving`** — drift score this week is lower than the prior 7-day window
- **`stable`** — drift score within ±1 of the prior window
- **`drifting`** — drift score higher than the prior window

A "drifting" trend on a relationship is a structural signal; review the underlying daily ledger entries to see which fields are repeatedly flagged.

### 6.6 What to do if QA itself fails

The runner wraps the QA pass in a try/except (`dreams/runner.py`). If `generate_consistency_qa` throws, you'll see `dreams_consistency_qa_failed` at ERROR level and a `consistency_qa: <exc>` warning in `dreams_run_complete`. The rest of the Dreams pass (the 5 per-character generators) still completed successfully.

Common causes:
- BD-1 is failing upstream or already circuit-open; the QA judge will surface this as `consistency_qa: DreamsLLMError: ...` in the run warnings.
- A rich YAML is malformed and `enumerate_all(canon)` couldn't enumerate 10 relationships. Check the loader on next boot.
- `shared_canon.dyads_baseline` keys drifted from the seniority precedence (`adelia=0/bina=1/reina=2/alicia=3`). Run `make validate-canon`.

---

## 7. Relationship evaluators

### 7.1 What fires after each turn

The HTTP response closes after step 10. Then `schedule_post_turn_tasks()` spawns three independent `asyncio.create_task` jobs:

1. `extract_episodic()` — pulls memorable beats from the last turn into `episodic_memories` with embedding via LM Studio.
2. `evaluate_and_update()` — Phase 8 Whyze-dyad evaluator. The row stores 5 fields, but the evaluator currently updates 4 of them (`trust`, `intimacy`, `unresolved_tension`, `repair_history`), each capped at ±0.03.
3. `evaluate_and_update_internal()` — Phase 9 inter-woman evaluator. Updates each active inter-woman dyad the focal character is part of, ±0.03 each, **with Phase 10.7 pin-consult** before each dimension write.

All three are fire-and-forget. A failure in any one cannot delay or corrupt the user-visible reply (AC-7.10). Failures land in the log via `add_done_callback(_log_task_outcome)`.

### 7.2 LLM-primary, heuristic-fallback

Both Phase 8 and Phase 9 evaluators try the LLM path first. They fall back to the heuristic `_propose_*` function on any of:

1. Settings opt-out (`STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM=false` or `INTERNAL_RELATIONSHIP_EVAL_LLM=false`)
2. No `llm_client` available
3. `llm_client.circuit_open` is already true
4. LLM raises `DreamsLLMError`
5. Parser returns `None` (malformed JSON)

Both paths feed `_clamp_delta()` (final ±0.03 gate) and `_bound01()` ([0, 1] clamp). The cap is a hard invariant (**AD-004**) — no path bypasses it.

### 7.3 Reading `dreams_qa_pin_blocked`

When you see `WARNING dreams_qa_pin_blocked dyad_key=adelia_bina blocked_fields=['trust'] speaker_id=adelia`, this is **not** an error. It means:

> Phase 9 wanted to update one or more fields on `adelia_bina` based on Adelia's latest turn, but `dyad_state_pins` carries an active symmetric pin on those dimensions. The write was skipped. The pin is the operator's standing instruction that those dimensions should not move until they resolve.

If you see this event repeatedly for the same field, it means Phase 9 keeps trying to drift the dimension and the pin keeps blocking it. That's the system working as designed — the pin is doing its job. Resolve the pin (§6.3) only if you have the canonical truth that should replace the pinned value.

### 7.4 Cost envelope

Per-turn, fire-and-forget:
- 1 BD-1 call for episodic extraction (~300 tokens prompt + a short response).
- 1 BD-1 call for Phase 8 (~200 tokens, temperature 0.2).
- Up to 3 BD-1 calls for Phase 9 — one per active inter-woman dyad the focal character is part of:
  - **Resident-continuous focal character with Alicia home:** up to 3 calls (e.g., Adelia's evaluator updates `adelia_bina`, `adelia_reina`, `adelia_alicia`).
  - **Resident focal character with Alicia away:** up to 2 (Alicia-orbital dyads gate out).
  - **Alicia herself with all three orbital dyads dormant:** 0 (the SQL gate filters).

Disable Phase 8 with `STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM=false` or Phase 9 with `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM=false` — the heuristic path runs in both cases.

---

## 8. Canon edit workflow

### 8.1 Where to edit

The terminal 6-file canonical authoring surface (post-Phase-10.5c):

| File | What you edit |
|---|---|
| `Characters/adelia_raye.yaml` | Adelia's identity, kernel sections, soul substrate, voice, soul cards, pair architecture, family/dyad POV blocks, knowledge stack, state protocols, runtime routines |
| `Characters/bina_malek.yaml` | Same shape for Bina |
| `Characters/reina_torres.yaml` | Same shape for Reina |
| `Characters/alicia_marin.yaml` | Same shape + Alicia-orbital travel data |
| `Characters/shawn_kroon.yaml` | Operator's identity surface |
| `Characters/shared_canon.yaml` | Marriage facts, genealogy, signature scenes, property, timeline, pairs (4), dyads_baseline (10), interlocks (6), memory_tiers, normalization_notes |

**Do NOT** create new markdown character files, new narrow canon YAMLs, or any file under `src/starry_lyfe/canon/*.yaml`. Those are archived.

### 8.2 The edit cycle

```bash
# 1. Edit the YAML in your editor of choice
# 2. Validate the schema + cross-references
make validate-canon

# 3. If you changed structured DB-relevant content (canon_facts, character_baselines,
#    dyad_state_*), reseed:
make db-seed

# 4. If you changed kernel_sections / soul_substrate / soul_cards, the next
#    request will see the change because rich_loader keys its cache on rich-YAML
#    mtime (Phase 10.5b RT3). No restart needed.

# 5. Run the regression bundle to confirm assembled prompts didn't drift
#    in unexpected ways:
.venv/Scripts/python -m pytest tests/regression/ -v

# 6. Commit + push (per §12)
```

### 8.3 Preserve markers

The load-bearing contract is `meta.preserve_markers[].content_anchor`, not the HTML marker alone. The enforcement bundle checks that each anchor's sentence-level canonical units still reach assembled Layer 1 for the four women (and that Shawn's anchors still exist in his YAML body).

To intentionally retire a preserve marker, remove the marker AND the sentence at the same time, then add a normalization note to `shared_canon.yaml::normalization_notes`. The test reads the ledger and exempts removed markers.

### 8.4 OneDrive transient lock

Editing a YAML while OneDrive is mid-sync sometimes throws `PermissionError` to the loader. The loader has a bounded retry (`_load_yaml_file`, 50/100/200/400 ms backoff) that handles this transparently. If you see `OSError` propagated, OneDrive held the file for >750 ms — wait a few seconds and retry the request.

### 8.5 What never to edit

- `Archive/v7.1_pre_yaml/` — read-only historical reference. Editing here changes nothing in the runtime.
- `src/starry_lyfe/canon/*.yaml` — these were retired in Phase 10.5c and should not exist on a current checkout. If they reappear, it's a merge accident; delete them.

---

## 9. Health and metrics

### 9.1 `/health/live`

Always returns 200 if the FastAPI process is alive. Use it to verify "is the container up". Does not touch DB or BD-1.

### 9.2 `/health/ready`

Returns 200 only if:
- R5 pool is open and a trivial query succeeds.
- BD-1 is reachable (a HEAD probe to `STARRY_LYFE__BD1__BASE_URL`) **if** `STARRY_LYFE__API__HEALTH_BD1_PROBE=true` (default).

503 with structured reason otherwise:

```json
{
  "status": "not_ready",
  "checks": {
    "db": {"ok": true},
    "llm": {"ok": false, "reason": "BD-1 circuit breaker open"}
  }
}
```

If `checks.llm.reason` says the circuit breaker is open, the BD-1 client tripped after consecutive failures. Phase 8/9 evaluators will keep falling back to heuristics, and live chat generation will not recover until BD-1 recovers or you restart the API service.

### 9.3 `/v1/models`

Returns 5 entries: `starry-lyfe` (legacy default routing) plus the four character IDs (`adelia`, `bina`, `reina`, `alicia`). All carry the same fixed epoch `1776816000` (2026-04-15 Phase 7 ship). No auth.

### 9.4 `/metrics`

Prometheus exposition. See §4.4 for the series list.

---

## 10. Troubleshooting

### 10.1 "Chat completion returns an upstream error or dies mid-stream"

Likely causes (check in order):
1. `/health/ready` is 503. Check `checks.db` and `checks.llm`.
2. The stream emitted a terminal `UPSTREAM_LLM_ERROR` chunk after starting. Inspect `upstream_stream_failed`.
3. BD-1 is down or circuit-open. Restart the API service after fixing upstream access, or wait for the upstream issue to clear.
4. R5 pool exhausted or DB unavailable. Check active connections and the readiness payload.

### 10.2 "Chat completion succeeds but the response is wrong character"

Check character routing precedence (`api/routing/character.py:resolve_character_id`):
1. Was an `X-SC-Force-Character` header sent? It wins over everything.
2. Did the user message start with `/<char>`? It wins over `model`.
3. What did `model` resolve to? Misspellings fall back to the configured default.

Check the response headers instead: `X-Character-ID` tells you the winner, and `X-Routing-Source` tells you which surface won (`header`, `inline_override`, `model_field`, `default`).

### 10.3 "Crew Conversation only produces one speaker"

Msty Crew bubble sequencing is client-side now. If only one persona answered, check Msty-side crew settings first:

- Response behavior is `Auto`, not `Manual`
- The missing persona is actually included in the crew
- The conversation is `Contextual` if you expect prior persona replies to influence later bubbles

### 10.4 "Voice mode mismatch — Adelia is being too formal"

The classifier and assembler do not emit dedicated success-path logs for voice-mode selection today. If the mode is wrong:
- Did the user message contain a keyword that triggered an unexpected `SceneType`? (e.g., "cancellation" → `transition`)
- Are present_characters wrong? `assemble_context` may be inferring `solo_pair` vs `group` mistakenly.

### 10.5 "AliciaAwayContradictionError"

The classifier raised this because:
- Alicia is in `present_characters`,
- AND `alicia_home=False` (she's on operations per Tier 8 `life_states`),
- AND `communication_mode` resolved to `IN_PERSON`.

Either set Alicia home (update `life_states.is_away=false` if she's actually back), or re-route to a remote-mode scene by adding "phone", "letter", or "video_call" keywords to the user message.

### 10.6 "Soul card not activating in a scene I expected"

Soul cards activate via four gates (`context/soul_cards.py:127::find_activated_cards`):
1. `always` flag
2. `communication_mode` substring match (phone / letter / video_call / in_person)
3. `with_character` in present characters set
4. `scene_keyword` substring match in scene_description (case-insensitive)

There is no dedicated success-path `context_assembled` event today. Walk the card's YAML activation rules against the actual `scene_description`, `communication_mode`, and `present_characters` that reached `find_activated_cards()`.

### 10.7 "Phase 10.7 QA pass produced 9 rows, not 10"

`dreams_qa_memory_lookup_failed` alone is **not** enough to drop a row; the QA generator still writes a real or placeholder verdict for that relationship. Fewer than 10 rows means the QA pass or a DB write path failed partway through. Check `dreams_consistency_qa_failed`, `dreams_run_complete`, and any database exception around `_persist_one()`.

### 10.8 "Pin keeps blocking writes I want to allow"

The pin is doing its job. Either:
- Resolve the pin (§6.3), OR
- Update the canonical value in `shared_canon.yaml` so the LLM judge stops flagging the contradiction. (Then the next nightly QA pass produces `healthy_divergence` and no new pin.)

### 10.9 "Test suite reports environmental Postgres skips on a green run"

Expected. Integration tests that need real Postgres are skip-gated. If Postgres is unreachable (e.g., `make docker-up` not run), the integration suite skips. Run `make docker-up` then re-run if you want full coverage. The unit suite should always pass regardless.

### 10.10 "Markdown ledger entries appear out of order"

`_emit_markdown` serializes writes via `_file_lock` (msvcrt on Windows, fcntl on POSIX). If you see `dreams_qa_markdown_lock_unavailable` warnings, the lock primitive isn't importable on this Python build — the write happened anyway but unsynchronized. Concurrent runs on the same UTC date may have collided. Manual repair if needed.

---

## 11. Backup and restore

### 11.1 What needs backing up

- **`starry-lyfe-pgdata` Docker volume** — all DB content (canon facts, episodic memories, dyad state, somatic state, life state, pins, QA log, sessions). This is the only piece that cannot be regenerated.
- **`Characters/*.yaml`** — under git already; commit + push regularly.
- **`.env`** — secrets. Keep a sealed copy somewhere out-of-band.
- **`Docs/_dreams_qa/*.md`** — runtime artifacts (gitignored). Daily ledgers + weekly digests. Lose-able if you trust the underlying DB tables (`dreams_qa_log`).

### 11.2 Backing up the DB

```powershell
# Hot dump while container runs (recommended)
docker exec Starry-Lyfe pg_dump -U starry_lyfe -d starry_lyfe -F c -f /tmp/starry_lyfe.dump
$stamp = Get-Date -Format yyyyMMdd
docker cp Starry-Lyfe:/tmp/starry_lyfe.dump "./backups/starry_lyfe_$stamp.dump"
```

### 11.3 Restoring

```powershell
# Drop + recreate the schema, then load the dump
Get-Content .\backups\starry_lyfe_YYYYMMDD.dump -AsByteStream | docker exec -i Starry-Lyfe pg_restore -U starry_lyfe -d starry_lyfe -c
```

### 11.4 Docker safety rules (CLAUDE.md §2)

- **Never** `docker compose down -v` — this destroys the named volume `starry-lyfe-pgdata` and every row with it.
- **Never** `docker volume prune` while the container is stopped.
- Use the project's rebuild script (`scripts/rebuild.ps1` or `make docker-rebuild` if defined) which knows to preserve the volume.
- After any rebuild/restart, verify the startup log shows existing data, not the empty-database warning.

### 11.5 Worst-case recovery

If the DB is gone and there's no recent dump:
1. `make docker-down` (NOT `-v`).
2. `make docker-up` to bring up a fresh Postgres on the existing volume — if the volume survived, your data is back.
3. If the volume is gone, you've lost all runtime state. You can re-seed the immutable tiers (1, 2, 3, 4, 7) from the rich YAMLs via `make db-seed`, but episodic memories, open loops, dyad state drift, life state, pins, and QA history are unrecoverable. This is why backups matter.

---

## 12. Dev workflow

### 12.1 Branch + commit

```powershell
git checkout -b feat/some-scope-description-of-change
# ... edits ...
make check                               # current Makefile gate: ruff + mypy + unit pytest bundle
git add <specific files>                 # never `git add -A` (sensitive files)
git commit -m "feat(scope): one-line summary

Body explaining WHY, not WHAT.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git push -u origin HEAD
```

Conventional Commit prefixes (CLAUDE.md §6): `feat`, `fix`, `refactor`, `docs`, `chore`, `test`. Scope is mandatory.

### 12.2 PR

```bash
gh pr create --title "scope: short title" --body "## Summary
- bullet 1
- bullet 2

## Test plan
- [ ] make check green
- [ ] manual smoke against /v1/chat/completions"
```

### 12.3 The Foundry SDLC

Six phases (CLAUDE.md §2): Hydration → Execution → WAF → Audit → Remediation → Merge Gate.
- **Hydration:** scope the blast radius before writing code.
- **Execution:** write code in the bounding box. Tests first for integration paths.
- **WAF:** `make check` is a gate, not a conversation.
- **Audit:** Codex (or self-audit) reviews against acceptance criteria.
- **Remediation:** fix audit findings (max 3 attempts per cycle).
- **Merge Gate:** Project Owner ships.

### 12.4 What to update on a PR that changes structure

Per CLAUDE.md §2 standing orders:
- Touched a file → verify its docstring still matches reality.
- Created a file → register in `Docs/ARCHITECTURE.md` Module Registry.
- Deleted a file → remove from imports + ARCHITECTURE.md.
- Modified a protocol droid → verify all implementations conform.
- Changed an endpoint, env var, or migration → update ARCHITECTURE.md AND `.env.example`.

---

## 13. Glossary

| Term | Meaning |
|---|---|
| **AD-NNN** | Architectural decision (numbered). Live in `Docs/ARCHITECTURE.md` §21. |
| **AC-N.M** | Acceptance criterion (numbered per phase). Live in `Docs/_phases/PHASE_N.md`. |
| **BD-1** | Outbound HTTP client protocol droid. `dreams/llm.py::BDOne`. Always `httpx.AsyncClient`. |
| **Bounding Box** | The phase-defined scope a code change is allowed to touch. |
| **Canon** | The frozen `Canon` dataclass returned by `load_all_canon()`. Single in-memory source of truth. |
| **Canon facts** | Tier 1 — flattened immutable facts seeded from rich YAML. |
| **Communication mode** | `phone` / `letter` / `video_call` / `in_person`. Tags Alicia-away artifacts and gates soul card activation. |
| **Crew Mode** | Msty-side multi-character conversation. Each persona request lands as its own backend call / bubble. |
| **Dyad** | A two-party relationship. Six inter-woman dyads (`dyad_state_internal`) + four woman-Whyze dyads (`dyad_state_whyze`). |
| **Dyad key** | Canonical key per relationship. Inter-woman keys use seniority order (`adelia_bina`, `bina_alicia` — not alphabetical). |
| **Episodic memory** | Tier 5 — pgvector-embedded events extracted post-turn. Runtime retrieval is semantic top-k, not a hard 24h window. |
| **F1 / F2 / F3 / F4 / F5** | Audit findings (numbered per audit round). |
| **Focal character** | The character whose POV the current request is built around. Determined by character routing precedence. |
| **GNK** | Config protocol droid. All env access through `*/config.py` modules, never `os.environ` elsewhere. |
| **Healthy divergence** | Phase 10.7 QA verdict — POV gap is canonical and dramaturgically correct. Scene fodder routes to `open_loops`. |
| **Heuristic fallback** | The `_propose_*` substring-bank scoring functions used by Phase 8/9 evaluators when LLM path is unavailable or fails. |
| **In-person** | A scene with all parties physically together. Triggers Alicia-residence gate. |
| **Knowledge soul card** | One of 11 per character. Activates conditionally in Layer 6 via scene_keyword / communication_mode / with_character / always. |
| **Layer N** | One of seven prompt layers in `assemble_context`. Layer 7 is the terminal Whyze-Byte constraint anchor. |
| **MSE-6** | Observability protocol droid. In the current tree this is standard Python logging to stdout/stderr plus Prometheus metrics. |
| **Msty Persona** | A single-character conversation handle in Msty Persona Studio. Routes via `model` field. |
| **Operator** | Whyze. The human at the keyboard. Also a canonical character (`shawn`) in the canon — distinct concepts. |
| **Pair** | A woman-Whyze relationship. Four pairs: Entangled (Adelia), Circuit (Bina), Kinetic (Reina), Solstice (Alicia). |
| **Pair callbacks** | Short canonical phrases from `pair_architecture.callbacks` rendered as a guaranteed-surcharge Layer 1 block. |
| **Pair soul card** | One of 4 per character (one per other-woman + one per Whyze). Always-on in Layer 1 for the focal character. |
| **Phase H** | The assembled-prompt regression bundle. First-class ship gate per **AD-008**. |
| **Pin** | A row in `dyad_state_pins` blocking Phase 9 from updating a dimension until operator-resolved. |
| **POV** | "Point of view" — a character's perspective on a relationship or event. Per-character POV is enforced divergent. |
| **Preserve marker** | `meta.preserve_markers[].content_anchor` metadata marking load-bearing canonical phrases. The HTML `<!-- PRESERVE -->` marker can still appear in authored prose, but the enforced contract is the anchor text. |
| **R5-D4** | Database protocol droid. `db/engine.py` async pool. |
| **Rich YAML** | One of the 5 per-character `Characters/{id}.yaml` files. Authoritative canonical source. |
| **Run ID** | UUID assigned per Dreams run. Joins `dreams_qa_log` rows to a single nightly pass. |
| **Scene Director** | Pre-assembly subsystem (`scene/`) centered on scene classification. The legacy next-speaker scorer remains in-tree but is not part of the active HTTP chat path. |
| **`SceneState`** | The dataclass output of `classify_scene()`. Drives layer assembly + voice mode + soul card activation. |
| **`shared_canon`** | The single cross-character objective anchor file. `pairs`, `dyads_baseline`, `interlocks`, `memory_tiers`, marriage, genealogy. |
| **Soul cards** | YAML blocks with activation rules. 4 pair (always) + 11 knowledge (conditional) per character. |
| **Soul essence** | Per-character `soul_substrate` block from rich YAML. Guaranteed-surcharge in Layer 1. |
| **Symmetric pin** | A pin with `pov_character_id=NULL`. Blocks all POVs on that dimension. |
| **Talk-to-Each-Other Mandate** | Legacy speaker-selection heuristic retained in `scene/next_speaker.py` tests; not part of the active HTTP chat path. |
| **Tier N** | One of 7 memory tiers. Tier 1 canon facts, Tier 7 transient somatic state. |
| **Voice mode** | A category of voice exemplar selection (`domestic`, `intimate`, `conflict`, `repair`, `public`, `group`, `silent`, `solo_pair`, `escalation`, `warm_refusal`, `group_temperature`). |
| **WAF** | Workflow Acceptance Framework. In the current Makefile, `make check` = ruff + mypy + unit pytest; run `pytest -q` separately for the full suite. |
| **WED-15** | Error / retry protocol droid. Circuit breaker + exponential backoff. |
| **Whyze-Byte** | The two-tier response validator. FAIL = hard stop. WARN = soft finding. |
| **2-1B** | Health-check protocol droid. `/health/live` + `/health/ready`. |

---

## 14. Operator axiom cheat sheet (CLAUDE.md §16 distilled)

**Character integrity.** Characters are people, not assistants. No "As an AI…". No hard-coded phrases. No phrase repetition within 3 exchanges. Reciprocity is structural — characters have genuine needs and ask for help.

**Relationships.**
- Whyze's primary romantic partner is **Adelia Raye**.
- Bina and Reina are married to each other (Adelia introduced them in 2021).
- All four women are intimate with Whyze in canonical and negotiated configurations.
- **No jealousy** — structural absence, not managed tension. Do not introduce tension that is not there.

**Activity distribution.** ~60% Adelia alone, ~15% Adelia + Bina, ~10% Bina alone, ~15% Reina solo or with another resident. Alicia integrates when home, pauses naturally during operational travel.

**Pipeline.**
- Whyze-Byte is mandatory on all outputs. No deliberate bypass.
- Request-driven. Each message = full pipeline. Only Dreams runs in the background (nightly).
- Routing precedence: header > inline > model field > default. Production Msty uses model field.
- Canonical voice inference parameters live in the rich YAML `voice.inference_parameters` surface and render into Layer 5, but the live chat path still honors `request.temperature` when the client provides it (default `0.7` otherwise).
- ±0.03 per-turn delta cap on relationship evaluators is a hard invariant.

**Activities.**
- Max 3 choices per decision point.
- Children are never present in scenes. Childcare always assumed.

**Operator profile.**
- Strengths-first framing. Never frame cognitive characteristics as deficits.
- No em-dashes / en-dashes as sentence interrupters. Use commas, parentheses, colons, or restructure.

---

## 15. Where to look next

- **`Docs/ARCHITECTURE.md`** — the top-down as-built map.
- **`Docs/_phases/PHASE_N.md`** — what shipped in each phase, with audit + remediation history.
- **`Docs/_phases/PHASE_10.md`** — Phase 10.7 spec + Step 10 self-audit + remediation record.
- **`journal.txt`** — Phase 10 YAML migration ledger.
- **`CLAUDE.md`** — governance, axioms, the sacred text.
- **`Docs/IMPLEMENTATION_PLAN_v7.1.md`** — the master plan; phase chronology + cross-phase dependencies.
- **`Docs/Persona_Tier_Framework_v7.1.md`** — character architecture deep dive.
- **`Vision/Starry-Lyfe_Vision_v7.1.md`** — Vision sections 5/6/7 (chosen-family architecture).

If you're new to the system: read this guide §1–§3, then scan `ARCHITECTURE.md` §1–§6, then come back here for whichever subsystem you need to operate.
