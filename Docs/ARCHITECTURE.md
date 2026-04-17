# Starry-Lyfe Architecture

**Version:** 1.0.0
**Date:** 2026-04-17
**Status:** As-built reference for the v7 terminal architectural state. Supersedes the 0.9.x stub chain.
**Consumer:** Msty AI (exclusive). No Open WebUI, no web UI, no other HTTP client.
**Commit baseline:** `8a7163e` (Phase 10.7 + audit remediation). 1,257 passed / 38 environmental Postgres skips / 0 failed / 0 xfailed. `ruff` + `mypy --strict` clean across 115 source files.

> This document describes *what the code is*. The chronological delivery record (phase-by-phase scope, audits, remediation cycles) lives in `Docs/_phases/`. The operator runtime walkthrough (markdown → assembled prompt) lives in `Docs/OPERATOR_GUIDE.md`. Governance authority lives in `CLAUDE.md`. On conflict, **CLAUDE.md wins** (per CLAUDE.md §2 Escalation); this document is then wrong and must be corrected.

---

## 1. Executive summary

Starry-Lyfe is a character AI backend for four canonical v7 persona kernels — **Adelia Raye** (ENFP-A, resident, Whyze's partner), **Bina Malek** (ISFJ-A, resident, married to Reina), **Reina Torres** (ESTP-A, resident, married to Bina), **Alicia Marin** (ESFP-A, resident, Argentine consular officer who travels frequently for operations) — plus the operator **Whyze** (Shawn). It serves Msty AI on port 8001 via an OpenAI-compatible SSE-streaming `/v1/chat/completions` endpoint.

The architecture is distinctive in four ways. **First**, canonical content is single-source-of-truth: five rich per-character YAMLs plus `shared_canon.yaml` are the sole runtime-authoritative authoring surface (post-Phase-10.5c terminal). **Second**, each prompt is assembled through a deterministic seven-layer pipeline with a guaranteed-surcharge budget (soul essence + pair callbacks never trimmed) and a terminal Whyze-Byte constraint anchor. **Third**, a nightly Dreams Engine runs six content generators per canonical character, including a cross-character Consistency QA judge (Phase 10.7) that detects drift between POV perspectives and pins contradicted fields against Phase 9 drift compounding. **Fourth**, two runtime LLM relationship evaluators (Phase 8 for Whyze-dyads, Phase 9 for inter-woman dyads) fire post-turn with a ±0.03-per-dimension delta cap, consulting the pinning table before each write.

The system is "architecturally complete" for v7: Phases 0 through 10.7 are shipped, sealed, and audit-synchronized. Remaining work is operational (deployment automation, observability dashboards, Msty persona/crew model-card authoring), not architectural.

---

## 2. Context

**Consumer model.** Msty AI loads each character as a Persona (Persona Studio, System Prompt Mode = `Replace`, blank in production per **AD-001**). Single-character conversations use the Msty Persona path (`model` field → character). Multi-character scenes use Msty Crew Mode, where prior persona responses arrive as `name`-tagged assistant messages and are preprocessed into a crew roster. Character routing precedence (first match wins): (1) `X-SC-Force-Character` header (dev/test only), (2) inline `/<char>` override at message start (dev/test only), (3) `model` field (production Msty path), (4) configured default.

**Canonical cast.** Four women plus the operator, architecturally "chosen family" — not permission slip. See CLAUDE.md §16 Project Axioms for the load-bearing operator directives: Adelia is Whyze's primary romantic partner; Bina and Reina are married to each other (Adelia introduced them in 2021); all four women are intimate with Whyze in canonical and negotiated configurations; no jealousy (structural absence, not managed tension); children are never present in scenes (childcare always assumed).

**Relationship taxonomy: 10 relationships.** Six inter-woman dyads (adelia_bina, adelia_reina, bina_reina, adelia_alicia, bina_alicia, reina_alicia) plus four woman-Whyze pairs (whyze_adelia → "Entangled", whyze_bina → "Circuit", whyze_reina → "Kinetic", whyze_alicia → "Solstice"). Dyad keys follow seniority precedence `adelia=0, bina=1, reina=2, alicia=3` matching `shared_canon.dyads_baseline` keys exactly.

**Activity distribution.** Approximately 60% Adelia alone, 15% Adelia + Bina, 10% Bina alone, 15% Reina solo or Reina + one other resident. Alicia's activity share folds in when home and pauses naturally during operational travel.

---

## 3. System map

```
                                       ┌─────────────────────────────────┐
                                       │            Msty AI              │
                                       │   (Persona path / Crew mode)    │
                                       └───────────────┬─────────────────┘
                                                       │  HTTPS
                                                       │  POST /v1/chat/completions
                                                       ▼
                                  ┌───────────────────────────────────────┐
                                  │  FastAPI app on port 8001             │
                                  │  (X-API-Key auth, SSE streaming)      │
                                  └───────────────┬───────────────────────┘
                                                  │
                                                  ▼
                              Character routing (4-stage precedence)
                                                  │
                                                  ▼
                              Msty preprocess (Crew roster + prior responses)
                                                  │
                                                  ▼
                              Scene classification (8 scene types × 6 modifiers)
                                                  │
                                                  ▼
                              Memory retrieval (canon facts · episodic · dyad
                                                  state · somatic · life state)
                                                  │
                                                  ▼
                              7-layer context assembly (terminal-anchored,
                                                  guaranteed-surcharge)
                                                  │
                                                  ▼
                              BD-1 → OpenRouter/Anthropic SFW completion
                                                  │
                                                  ▼
                              Whyze-Byte validation (2-tier FAIL/WARN)
                                                  │
                                                  ▼
                              SSE response → Msty ──(close)──▶ fire-and-forget:
                                                                • Episodic memory extraction
                                                                • Phase 8 Whyze-dyad evaluator
                                                                • Phase 9 inter-woman evaluator
                                                                    (both gated by Phase 10.7
                                                                     is_pinned() consult)

          ┌────────────────────────────────────────────────────────────────────────┐
          │  Nightly (apscheduler daemon or `python -m starry_lyfe.dreams --once`) │
          │                                                                        │
          │  For each canonical character, parallel `asyncio.gather`:              │
          │    schedule · off_screen · diary · open_loops · activity_design        │
          │                                                                        │
          │  After all 5 per-character passes complete:                            │
          │    Phase 10.7 Consistency QA — 10 relationships, 3 verdicts            │
          │    (healthy_divergence → open_loops `source='dreams_qa'`;              │
          │     concerning_drift → log + 3-night auto-promote;                     │
          │     factual_contradiction → `dyad_state_pins`)                         │
          │                                                                        │
          │  Weekly (Sunday UTC): trajectory digest                                │
          │    Docs/_dreams_qa/_weekly/YYYY-WW.md                                  │
          └────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Request path — twelve-step pipeline

Entry point: `src/starry_lyfe/api/orchestration/pipeline.py:run_chat_pipeline()` (line 468).

| Step | Responsibility | Location |
|---|---|---|
| 1 | HTTP receive + Msty preprocessing (system-prompt stripping, prior-response extraction, crew roster parsing) | `api/endpoints/chat.py:91`; `api/routing/msty.py:preprocess_msty_request()` |
| 2a | Resolve `alicia_home` flag from Tier 8 `life_states` | `api/orchestration/pipeline.py:481` |
| 2b | Scene classification (pure sync, 8 scene types × 6 modifiers) | `scene/classifier.py:classify_scene()` |
| 3 | Memory retrieval (canon + episodic + dyad state + somatic + life state + Dreams activities) | `db/retrieval.py`; called at `pipeline.py:500` |
| 4 | Activity-context auto-population from `MemoryBundle.activities` | Inline in `pipeline.py` |
| 5 | Seven-layer context assembly | `context/assembler.py:assemble_context()` (line 59) |
| 6 | BD-1 streaming completion | `dreams/llm.py:BDOne` (shared client) |
| 7 | LLM honors Layer 7 terminal constraints (unenforced client-side) | Upstream |
| 8 | Whyze-Byte validation on buffered response | `validation/whyze_byte.py:validate_response()` (line 329) |
| 9 | Crew loop: `_run_crew_turn` iterates next speakers up to `crew_max_speakers`, per-speaker assemble + validate + attribution | `api/orchestration/pipeline.py:297` |
| 10 | SSE stream terminator (finish_reason + `[DONE]`) | `pipeline.py:623` |
| 11 | Shadow-Persona bookkeeping (Msty-side, not backend) | n/a |
| 12 | Post-turn fire-and-forget: episodic extraction + Phase 8 + Phase 9 evaluators | `api/orchestration/post_turn.py:schedule_post_turn_tasks()` (line 49) |

**Crew-mode carry-forward:** Later speakers see earlier validated text prepended via `_format_crew_prior_block()`. Attribution (`**Name:** `) is SSE frame content, not LLM output, so it does not increment token metrics. Per-speaker validation FAIL emits an error chunk but does not abort the loop.

**Post-turn isolation:** `schedule_post_turn_tasks()` spawns `asyncio.create_task()` with `add_done_callback(_log_task_outcome)`. The HTTP response closes before any post-turn task completes (AC-7.10). A failing evaluator cannot delay or corrupt the user-visible reply.

Operator-facing walkthrough: `Docs/OPERATOR_GUIDE.md` §3–§9 (render order, layer semantics, per-scene examples).

---

## 5. Module registry

**115 Python source files** under `src/starry_lyfe/`. Organized by subsystem:

### `canon/` — authoritative canon loader

| Module | Purpose | Protocol droid |
|---|---|---|
| `canon/loader.py` | `load_all_canon()` → frozen `Canon(characters, pairs, dyads, protocols, interlocks, voice_parameters, routines, shared)` built from rich YAML + shared_canon | GNK |
| `canon/rich_loader.py` | `load_rich_character()`, `load_shared_canon()`, `load_all_rich_characters()`, `format_soul_essence_from_rich()`, `format_pair_callbacks_from_rich()`, OneDrive transient-lock retry | GNK |
| `canon/rich_schema.py` | `RichCharacter` Pydantic v2 model (kernel_sections, soul_substrate, voice, soul_cards, pair_architecture, family_and_other_dyads, relationships, knowledge_stack, state_protocols, runtime.routines) | — |
| `canon/shared_schema.py` | `SharedCanon` Pydantic v2 model (pairs, dyads_baseline, interlocks, memory_tiers, marriage, genealogy, signature_scenes, timeline, property, normalization_notes) | — |
| `canon/validator.py` | Cross-reference validator + CLI entry point (`make validate-canon`) | GNK |
| `canon/soul_cards.py` | `load_all_soul_cards()` iterator returning `list[SoulCard]` keyed by character + card_type | — |
| `canon/pairs_loader.py` | `get_pair(pair_key)` builds CanonPair from rich pair_architecture + shared_canon anchor | — |
| `canon/routines_loader.py` | `get_routines(character_id)` pulls `runtime.routines` from the per-character rich YAML | — |
| `canon/schemas/*.py` | Narrow Pydantic models for each canon shape (`CanonCharacters`, `CanonPairs`, `CanonDyads`, `CanonProtocols`, `CanonInterlocks`, `CanonVoiceParameters`, `CanonRoutines`) + shared `StrEnum` types | — |

### `db/` — memory persistence

| Module | Purpose | Protocol droid |
|---|---|---|
| `db/base.py` | SQLAlchemy DeclarativeBase, `starry_lyfe` schema constant, `TZDateTime` custom type | — |
| `db/config.py` | `DatabaseSettings.from_env()` | GNK |
| `db/engine.py` | `build_engine()`, `build_session_factory()`, `init_db()`, `close_db()`, pgvector extension bootstrap | R5 |
| `db/models/*.py` | 15 ORM models (see §7 Data model) | R5 |
| `db/decay.py` | Pure exponential-decay function for Tier 7 somatic state | — |
| `db/embed.py` | `EmbeddingService` Protocol + `LMStudioEmbeddingService` OpenAI-compatible client | BD-1 |
| `db/seed.py` | Seed Tiers 1/2/3/4/7 from rich YAML; idempotent rerun safe | R5, GNK |
| `db/retrieval.py` | Per-tier retrieval with read-time decay; `MemoryBundle` pipeline contract | R5 |

### `context/` — seven-layer assembler

| Module | Purpose | Protocol droid |
|---|---|---|
| `context/assembler.py` | `assemble_context()` (line 59) — terminal-anchored 7-layer pipeline; `LAYER_MARKERS` XML-tag dictionary at line 38 | — |
| `context/budgets.py` | `LayerBudgets` dataclass (defaults: kernel 6000 / canon_facts 600 / episodic 1200 / somatic 500 / voice 900 / scene 2400 / constraints 900 — total 12,500); `CHARACTER_KERNEL_BUDGET_SCALING` (adelia 1.05, bina 1.20, reina 1.15, alicia 0.85); `resolve_kernel_budget()`; markdown-block-aware trimming via `BlockType` enum | — |
| `context/kernel_loader.py` | `compile_kernel()` (line 152), `compile_kernel_with_soul()` (line 268), `load_voice_guidance()`, cache keyed on rich YAML mtime (Phase 10.5b RT3) | GNK |
| `context/layers.py` | Per-layer formatters; `VoiceMode` selection matrix; scene-block rendering; pair-callbacks Layer 1 block | — |
| `context/constraints.py` | Layer 7 character pillars and scene-gated constraint blocks (terminal anchor — never trimmed) | — |
| `context/prose.py` | Dramaturgical prose renderers for canon facts, dyads, protocols, somatic state | — |
| `context/soul_cards.py` | `find_activated_cards()` (line 127) — activation gates: `always`, `communication_mode`, `with_character`, `scene_keyword` | — |
| `context/types.py` | `AssembledPrompt`, `SceneState`, `SceneType`, `SceneModifiers`, `CommunicationMode`, `VoiceMode` | — |

### `validation/` — Whyze-Byte and fidelity

| Module | Purpose |
|---|---|
| `validation/whyze_byte.py` | `validate_response()` (line 329) — two-tier validator (FAIL vs WARN): AI-ism, framework leak, repetition, em-dash hygiene, cross-character contamination, hand-off detector |
| `validation/fidelity.py` | Positive fidelity rubrics — 7 dimensions × 4 characters = 28 rubrics; static scoring; `<10s` test budget |

### `scene/` — Scene Director

| Module | Purpose |
|---|---|
| `scene/classifier.py` | `classify_scene()` (line 124) — pure sync; 8 scene types × 6 stackable modifiers; Alicia-residence gate raises `AliciaAwayContradictionError` |
| `scene/next_speaker.py` | `select_next_speaker()` (line 130) — 7-rule scoring (residence zero-out, Rule of One, Talk-to-Each-Other mandate, w2w continuation, dyad-state fitness, recency suppression, narrative salience); injected `DyadStateProvider` Protocol |
| `scene/errors.py` | `AliciaAwayContradictionError`, `NoValidSpeakerError` |

### `dreams/` — Dreams Engine

| Module | Purpose | Protocol droid |
|---|---|---|
| `dreams/runner.py` | `run_dreams_pass()` (line 171) — parallel 5-generator-per-character fan-out, then Phase 10.7 QA pass; `_route_qa_scene_fodder_to_open_loops()` post-F1-remediation helper; session-bounded transactions | R5, BD-1 |
| `dreams/daemon.py` | apscheduler daemon + `python -m starry_lyfe.dreams [--once]` entry point | — |
| `dreams/config.py` | `DreamsSettings.from_env()` | GNK |
| `dreams/llm.py` | `BDOne` (production OpenRouter/Anthropic client) + `StubBDOne` (test double); circuit breaker; retry with backoff | BD-1, WED-15 |
| `dreams/consolidation.py` | `refresh_somatic_decay()`, `expire_stale_loops()`, `resolve_addressed_loops()`, `weekly_qa_digest()` | R5 |
| `dreams/alicia_mode.py` | `pick_alicia_communication_mode()` sampler (phone/letter/video per canonical distribution) | — |
| `dreams/generators/schedule.py` | Deterministic daily schedule from `runtime.routines` | — |
| `dreams/generators/off_screen.py` | LLM-backed overnight event generator | BD-1 |
| `dreams/generators/diary.py` | LLM-backed per-character diary entry | BD-1 |
| `dreams/generators/open_loops.py` | LLM-backed unresolved-thread generator | BD-1 |
| `dreams/generators/activity_design.py` | LLM-backed scene-opener + narrator_script + choice_tree for next session | BD-1 |
| `dreams/generators/consistency_qa.py` | Phase 10.7 neutral-observer judge across 10 relationships | BD-1 |
| `dreams/writers.py` | `write_diary_entry`, `write_activity`, `write_new_open_loops` (Phase 10.7: `source` kwarg), `write_off_screen_events`, `write_consolidation_log`, `write_consistency_qa_log`, `write_dyad_state_pin` | R5 |
| `dreams/notifications.py` | `emit_qa_event` dispatcher (structlog INFO/WARNING/ERROR + file-locked daily markdown ledger via `_file_lock` cross-platform context manager) | MSE-6 |
| `dreams/consistency/schemas.py` | `QAVerdict` enum, `Contradiction`, `RelationshipCheck`, `ConsistencyQAOutput` (exactly 10 checks) | — |
| `dreams/consistency/relationships.py` | `enumerate_all(canon)` → 10 `Relationship` rows (seniority-ordered keys) | — |
| `dreams/consistency/prompt.py` | `JUDGE_SYSTEM_PROMPT` + `build_user_prompt()` with Phase 8 R1-F3 sanitation (`_sanitize_for_evidence_block`) | — |
| `dreams/consistency/pinning.py` | `is_pinned()`, `pin_field()`, `unpin_field()`, `list_active_pins()` | R5 |
| `dreams/consistency/auto_promote.py` | `should_promote()` — 3-night threshold, 36h window, DB-side timestamps | R5 |
| `dreams/consistency/digest.py` | `build_weekly()` — ISO-week trajectory digest (improving / stable / drifting) | — |
| `dreams/consistency/memory_lookup.py` | `load_relationship_memories()`, `load_woman_whyze_memories()` — 7-day windows | R5 |

### `api/` — HTTP service

| Module | Purpose | Protocol droid |
|---|---|---|
| `api/app.py` | `create_app()` FastAPI factory + lifespan (loads canon, DB engine, embedding service, BD-1 client; stashes on `app.state`) | — |
| `api/main.py` | `main()` uvicorn entry point | — |
| `api/config.py` | `ApiSettings` + `get_api_settings()` | GNK |
| `api/deps.py` | Per-request dependency providers (session, canon, embedding, llm_client) | — |
| `api/errors.py` | Exception handlers — OpenAI-shaped error payloads | — |
| `api/endpoints/chat.py` | `chat_completions()` — POST `/v1/chat/completions` (X-API-Key auth, SSE) | — |
| `api/endpoints/health.py` | `/health/live` + `/health/ready` (R5 + BD-1 probe) | 2-1B |
| `api/endpoints/models.py` | GET `/v1/models` — 5 entries (legacy `starry-lyfe` + 4 character IDs) | — |
| `api/endpoints/metrics.py` | `MetricsMiddleware` + GET `/metrics` (Prometheus) | MSE-6 |
| `api/routing/character.py` | `resolve_character_id()` — 4-stage precedence | — |
| `api/routing/msty.py` | `preprocess_msty_request()` → `MstyPreprocessed` (stripped prompt, prior responses, roster, canonical ordering) | — |
| `api/orchestration/pipeline.py` | 12-step `run_chat_pipeline()` + `_run_crew_turn` | — |
| `api/orchestration/post_turn.py` | `schedule_post_turn_tasks()` fire-and-forget task factory | — |
| `api/orchestration/relationship.py` | Phase 8 `evaluate_and_update()` — Whyze-dyad deltas, ±0.03 cap, LLM-primary + heuristic fallback | — |
| `api/orchestration/relationship_prompts.py` | `RELATIONSHIP_EVAL_SYSTEM`, `build_eval_prompt()`, `parse_eval_response()`, `RelationshipEvalResponse` | — |
| `api/orchestration/internal_relationship.py` | Phase 9 `evaluate_and_update_internal()` — inter-woman deltas, ±0.03 cap, Alicia-orbital SQL gate, Phase 10.7 per-dimension `is_pinned()` consult | — |
| `api/orchestration/internal_relationship_prompts.py` | `INTERNAL_RELATIONSHIP_EVAL_SYSTEM`, `build_internal_eval_prompt()` (html.escape injection defense), `parse_internal_eval_response()`, 5-field Pydantic response | — |
| `api/orchestration/memory_extraction.py` | `extract_episodic()` post-turn memory extractor | BD-1 |
| `api/orchestration/session.py` | `upsert_session()` — `chat_sessions` table | R5 |
| `api/schemas/chat.py` | OpenAI-compatible request/response schemas | — |

### `personas/` and misc

`personas/registry.py` — per-character inference parameters (temperature spread Adelia 0.82 > Alicia 0.75 > Reina 0.72 > Bina 0.58, top_p, frequency_penalty, presence_penalty).

---

## 6. Seven-layer context assembly

Entry: `context/assembler.py:assemble_context()` (line 59). Terminal constraint anchoring: Layer 7 is always last; its content is NEVER trimmed.

| # | Layer | Source | Base budget | Char-scaled? | Always included? |
|---|---|---|---|---|---|
| 1 | Persona kernel (kernel body + guaranteed soul essence surcharge + guaranteed pair-callbacks surcharge) | `Characters/{id}.yaml::kernel_sections`, `soul_substrate`, `pair_architecture.callbacks` | 6,000 | ✓ (Adelia 6,300 / Bina 7,200 / Reina 6,900 / Alicia 5,100) | ✓ |
| 2 | Canon facts | Tier 1 `canon_facts` | 600 | — | ✓ |
| 3 | Episodic memory | Tier 5 `episodic_memories` (24h window + pgvector retrieval) | 1,200 | — | ✓ |
| 4 | Somatic state + life state | Tier 7 `transient_somatic_states` + `life_states` | 500 | — | ✓ |
| 5 | Voice directives (inference parameters + mode-tagged exemplars) | `voice.inference_parameters` + `voice.few_shots.examples[]` | 900 | — | ✓ |
| 6 | Scene context (Tier 6 open loops + 11 knowledge soul cards, scene-conditional) | `open_loops` + `soul_cards[]` | 2,400 | — | ✓ |
| 7 | Whyze-Byte constraints (terminal anchor) | `canon_facts` constraint pillars | 900 | — | ✓ NEVER trimmed |

**Base total:** 12,500 tokens + per-character kernel scaling + guaranteed surcharges.

**Budget semantic (post-Phase-B):**

- `kernel_budget` governs only the **trimmable** kernel body.
- Soul essence from `format_soul_essence_from_rich()` is a **guaranteed surcharge** (~1,750–2,050 tokens per character).
- Pair callbacks from `format_pair_callbacks_from_rich()` are a **guaranteed surcharge** (short-form canonical phrases rendered as a dedicated Layer 1 block).
- Effective Layer 1 ceiling = `resolve_kernel_budget(character) + soul_essence_token_estimate_from_rich(character) + pair_callbacks_token_estimate_from_rich(character)`.

**Per-character effective Layer 1 (tokens):**

| Character | Kernel budget | Soul essence | Effective L1 ceiling |
|---:|---:|---:|---:|
| Adelia | 6,300 | ~1,900 | ~8,200 |
| Bina | 7,200 | ~1,900 | ~9,100 |
| Reina | 6,900 | ~1,750 | ~8,650 |
| Alicia | 5,100 | ~2,050 | ~7,150 |

**VoiceMode selection.** `SceneType` (8 values: `domestic`, `intimate`, `conflict`, `repair`, `public`, `group`, `solo_pair`, `transition`) × `SceneModifiers` (6 stackable flags) resolves to a `VoiceMode` (`domestic`, `conflict`, `intimate`, `public`, `group`, `repair`, `silent`, `solo_pair`, `escalation`, `warm_refusal`, `group_temperature`). `VoiceMode` gates which `few_shots.examples[]` activate in Layer 5.

**Soul-card activation (Layer 6 pair-always-on or knowledge-conditional).** `find_activated_cards()` gates each card on:

- `always` flag (unconditional activation)
- `communication_mode` substring match (phone / letter / video_call / in_person)
- `with_character` in present characters set
- `scene_keyword` substring match (case-insensitive) in scene_description

Of 15 soul cards per character, 4 pair-always-on cards reserve from the Layer 1 budget; 11 knowledge cards activate scene-conditionally in Layer 6.

**Alicia-presence gate.** Assembling an in-person Alicia prompt while `alicia_home=False` raises `AliciaAwayContradictionError` (`scene/errors.py`). The classifier enforces the same gate one step earlier.

---

## 7. Data model

**Schema:** `starry_lyfe` in PostgreSQL 16. **Total tables:** 17 (15 with SQLAlchemy ORM models in `db/models/`; 2 raw-SQL Phase 10.7 additions). **pgvector:** HNSW index on `episodic_memories.embedding` (`Vector(768)`).

### Seven-tier memory hierarchy (the canonical layer model)

| Tier | Table | ORM file | Mutability | Purpose |
|---|---|---|---|---|
| 1 | `canon_facts` | `canon_facts.py` | Immutable at runtime | Flattened canon facts seeded from rich YAML |
| 2 | `character_baselines` | `character_baseline.py` | Immutable at runtime | Per-character identity (4 rows: Adelia, Bina, Reina, Alicia) |
| 3 | `dyad_state_whyze` | `dyad_state_whyze.py` | Mutable (Phase 8 evaluator) | 4 woman-Whyze dyads × 5 dimensions |
| 4 | `dyad_state_internal` | `dyad_state_internal.py` | Mutable (Phase 9 evaluator) | 6 inter-woman dyads × 5 dimensions; `is_currently_active` gates Alicia-orbital |
| 5 | `episodic_memories` | `episodic_memory.py` | Grows + decays | pgvector embedded, 24h primary retrieval window, `communication_mode` tag |
| 6 | `open_loops` | `open_loop.py` | TTL-expiry | Unresolved threads; Phase 10.7 healthy-divergence scene fodder lands here with `loop_type` carrying `:dreams_qa` qualifier |
| 7 | `transient_somatic_states` | `transient_somatic.py` | Exponential decay | Per-character fatigue / stress / injury residues |

### Dreams persistence (Phase 6 + Phase 10.7)

| Table | ORM file | Mutability | Purpose |
|---|---|---|---|
| `life_states` | `life_state.py` | Mutable (Dreams) | Per-character mood / energy / focus + Alicia residency (`is_away`, `away_since`, `expected_return`) |
| `activities` | `activity.py` | 24h TTL | Tomorrow's scene opener (`scene_description`, `narrator_script`, `choice_tree`, `communication_mode`) |
| `consolidated_memories` | `consolidated_memory.py` | Mutable (Dreams) | Post-consolidation narrative summaries with `consolidated_from` provenance |
| `consolidation_log` | `consolidation_log.py` | Append-only | Per-run audit trail (`run_id`, `outputs_written`, `warnings`) |
| `drive_states` | `drive_state.py` | Mutable (Dreams) | Per-character drive/craving state (Phase 6) |
| `proactive_intents` | `proactive_intent.py` | TTL-expiry | Character-initiated scene seeds |
| `session_health` | `session_health.py` | Mutable (Dreams) | Per-session health heuristics |
| **`dreams_qa_log`** | (raw SQL, Alembic 005) | Append-only | Phase 10.7 per-run verdict per relationship (10 rows max per run) |
| **`dyad_state_pins`** | (raw SQL, Alembic 005) | Append + operator-resolve | Phase 10.7 pinned contradicting fields. Unique partial index `(relationship_key, pov_character_id, field_name) WHERE operator_resolved_at IS NULL` |

### HTTP service (Phase 7)

| Table | ORM file | Purpose |
|---|---|---|
| `chat_sessions` | `chat_session.py` | Per-HTTP-session bookkeeping (`session_id`, `character_id`, `created_at`, last-activity timestamps) |

### Alembic migration chain (head = `005`)

| Revision | File | Tables created | Notes |
|---|---|---|---|
| 001 | `001_create_memory_schema.py` | `canon_facts`, `character_baselines`, `dyad_state_whyze`, `dyad_state_internal`, `episodic_memories`, `open_loops`, `transient_somatic_states` | Tier 1–7 base |
| 002 | `002_phase_6_dreams_tables.py` | `life_states`, `activities`, `consolidated_memories`, `consolidation_log`, `drive_states`, `proactive_intents`, `session_health` | Phase 6 Dreams persistence |
| 003 | `003_phase_6_episodic_comm_mode.py` | — | Adds `communication_mode` column to `episodic_memories` + `activities` (Alicia-away Phase A'' retroactive) |
| 004 | `004_phase_7_chat_sessions.py` | `chat_sessions` | Phase 7 HTTP service |
| 005 | `005_phase_10_7_dreams_qa.py` | `dreams_qa_log`, `dyad_state_pins` | Phase 10.7 Consistency QA (head) |

*Note: the CLAUDE.md §13 table-name list carries three legacy names (`character_responses`, `relationship_state`, `pipeline_validations`) that never materialized as tables, and omits `character_baselines`, `dyad_state_whyze`, `dyad_state_internal`, `transient_somatic_states`. This document's table list is authoritative per AD-001 on-conflict rule reversed for database schema — CLAUDE.md §13 is stale here.*

---

## 8. Canon authority — terminal six-file YAML surface

Post-Phase-10.5c, **six files** are the sole runtime-authoritative source for every canonical character and every piece of structured cross-character config:

| File | Purpose | Authoritative fields (summary) |
|---|---|---|
| `Characters/adelia_raye.yaml` | Adelia's identity + voice + soul + pair + dyads + runtime | `identity`, `kernel_sections` (11 numbered sections), `soul_substrate` (4 blocks), `voice` (few_shots.examples + inference_parameters), `soul_cards` (4 pair + 11 knowledge), `pair_architecture` (POV + callbacks), `family_and_other_dyads.with_{bina,reina,alicia}`, `relationships`, `knowledge_stack`, `behavioral_framework.state_protocols`, `runtime.routines` |
| `Characters/bina_malek.yaml` | Bina's authoring surface | Same shape as Adelia |
| `Characters/reina_torres.yaml` | Reina's authoring surface | Same shape as Adelia |
| `Characters/alicia_marin.yaml` | Alicia's authoring surface | Same shape + Alicia-orbital travel data |
| `Characters/shawn_kroon.yaml` | Operator's identity (fifth rich character) | Identity, perspective blocks referenced by women's POVs |
| `Characters/shared_canon.yaml` | Cross-character objective anchors (single-source-of-truth for everything cross-POV) | `version`, `marriage` (2022), `signature_scenes`, `genealogy` (Gavin birthdate 2018-09-12, age derived), `property` (Foothills County near Priddis), `timeline`, `pairs[]` (4 entries with canonical_name, classification, mechanism, shared_functions, what_she_provides, how_she_breaks_spiral, core_metaphor, cadence), `dyads_baseline` (10 entries × 5 dimensions), `interlocks[]` (6 cross-partner interlocks), `memory_tiers` (7-tier system taxonomy), `normalization_notes` (Phase 10.6 audit ledger) |

**`Canon` dataclass shape** (`canon/loader.py:46`, 8 fields frozen): `characters`, `pairs`, `dyads`, `protocols`, `interlocks`, `voice_parameters`, `routines`, `shared`. Every narrow field hydrates from exactly one authoritative rich-YAML location; no dual-source contradictions possible.

**Loader entry points.** `load_all_canon(validate_on_load=True)` → `Canon` (`loader.py:426`). `load_rich_character(id)` → `RichCharacter` (`rich_loader.py:92`). `load_shared_canon()` → `SharedCanon` (`rich_loader.py:108`). `get_preserve_markers(rc)` extracts all preserve markers for the enforcement test.

**OneDrive transient-lock retry.** `_load_yaml_file()` uses a bounded exponential backoff (50/100/200/400 ms across a ~750 ms window) to tolerate transient `PermissionError` / `OSError` raised when OneDrive is holding a file during sync (Phase 10.5b R2-F1).

**Archive.** Every pre-YAML canonical source lives at `Archive/v7.1_pre_yaml/` with a SHA256 `MANIFEST.md`: 16 legacy character markdown files, 15 soul card markdowns, `soul_essence.py`, 7 narrow canon YAMLs. Supersession column in the manifest points each archived file at its exact terminal rich-YAML field path.

**Preserve-marker enforcement.** `scripts/phase_0_verification.py` + `tests/unit/test_preserve_markers.py` enforce sentence-level canonical-unit integrity across the 6 authoritative files. Known-gap exemption rule is documented in the test header.

---

## 9. Soul architecture reaching the model

Four layers of canonical substrate ride every assembled prompt:

1. **Soul essence** — rendered from `Characters/{name}.yaml::soul_substrate` via `rich_loader.format_soul_essence_from_rich()`. Prepended to Layer 1 by `compile_kernel_with_soul()`. **Guaranteed surcharge** — never trimmed regardless of kernel budget pressure.
2. **Pair callbacks** — rendered from `Characters/{name}.yaml::pair_architecture.callbacks` via `format_pair_callbacks_from_rich()`. Short-form canonical phrases (e.g., *"The plate will always be covered."*, *"Neither of us is the load the other carries."*) rendered as a dedicated "Canonical Callbacks (pair architecture)" block in Layer 1. **Guaranteed surcharge.**
3. **Kernel body** — trimmable, budget-bounded, rendered from `Characters/{name}.yaml::kernel_sections` (11 numbered sections per character, 300–1,000 tokens each) via `compile_kernel()`. Shaped further by `compile_kernel_with_soul()` so the guaranteed surcharges ride on top without displacing trimmable content.
4. **Soul cards** — rendered from `Characters/{name}.yaml::soul_cards[]` via `soul_cards.load_all_soul_cards()`. 4 pair cards always-on in Layer 1 for the focal character; 11 knowledge cards scene-conditional in Layer 6 via `scene_keyword` / `communication_mode` / `with_character` / `always` activation.

The legacy `soul_essence.py` Python module, the 15 per-character soul card markdown files, and the `{Name}_v7.1.md` legacy markdown kernels were all archived on 2026-04-16 (Phase 10.5). No runtime code reads them.

---

## 10. Dreams Engine

Entry: `dreams/runner.py:run_dreams_pass()` (line 171). Scheduled by `dreams/daemon.py` via apscheduler; manual invocation via `python -m starry_lyfe.dreams --once`.

### Six generators

| Generator | Kind | LLM? |
|---|---|---|
| `generators/schedule.py::generate_schedule` | Deterministic daily schedule from `runtime.routines` | No |
| `generators/off_screen.py::generate_off_screen` | Overnight events during Whyze absence | BD-1 |
| `generators/diary.py::generate_diary` | Per-character reflective prose entry | BD-1 |
| `generators/open_loops.py::generate_open_loops` | Unresolved threads for next session | BD-1 |
| `generators/activity_design.py::generate_activity_design` | Tomorrow's scene opener + narrator script + choice tree | BD-1 |
| `generators/consistency_qa.py::generate_consistency_qa` | Phase 10.7 cross-relationship judge across 10 relationships | BD-1 |

### Orchestration

Per canonical character, in parallel via `asyncio.gather(..., return_exceptions=True)`:
1. `default_snapshot_loader` reads 24h of episodic memories, open loops, dyad states, life state.
2. Generators fan out; each raises are captured and converted to per-character warnings.
3. Writers run inside a `session.begin()` transaction.
4. Consolidation helpers on the same session: `refresh_somatic_decay`, `expire_stale_loops`, `resolve_addressed_loops`.

**After all per-character passes complete**, the runner invokes `generate_consistency_qa` over the 10 relationships. Its output is captured into `DreamsPassResult.consistency_qa`. Then `_route_qa_scene_fodder_to_open_loops()` iterates healthy-divergence verdicts and writes one `OpenLoop` row per non-empty `scene_fodder` string (Phase 10.7 F1 remediation) with `source="dreams_qa"`, which the writer qualifies as `loop_type="dreams_qa_scene_seed:dreams_qa"` (the `open_loops` table has no `source` column today, so the compat path encodes source via `loop_type`).

**Weekly (Sunday UTC):** `dreams/consolidation.py::weekly_qa_digest()` no-op short-circuit unless `ref.isoweekday() == 7`; otherwise calls `consistency/digest.py::build_weekly()` which reads the last 7 daily ledger files and emits `Docs/_dreams_qa/_weekly/YYYY-WW.md` with per-relationship trajectory labels.

### Writers (seven)

`write_diary_entry`, `write_activity`, `write_new_open_loops` (Phase 10.7: optional `source: str = "dreams"` kwarg), `write_off_screen_events`, `write_consolidation_log`, `write_consistency_qa_log`, `write_dyad_state_pin` (the latter a thin pass-through to `consistency/pinning.py::pin_field`).

### Failure isolation

Every exception from the QA pass, the scene-fodder routing, and the weekly digest is caught and converted into a warning entry on `DreamsPassResult.warnings`. The nightly Dreams pass never crashes because of a QA-pipeline fault.

---

## 11. Phase 10.7 Consistency QA sub-pipeline

**Ten-relationship enumeration** (`consistency/relationships.py::enumerate_all`). Dyad keys use seniority precedence `adelia=0, bina=1, reina=2, alicia=3` so inter-woman keys match `shared_canon.dyads_baseline` exactly (`bina_alicia`, not `alicia_bina`). Woman-Whyze keys are `whyze_{woman}`.

**Three verdicts and their routing:**

| Verdict | Routing |
|---|---|
| `healthy_divergence` | Gap is canonical and dramaturgically correct. `scene_fodder[]` strings flow into `open_loops` with `source="dreams_qa"` as scene seeds for next time both halves of the relationship are present. |
| `concerning_drift` | POVs wandering from shared anchor but not yet contradictory. Logged to `dreams_qa_log`. If the same `(relationship_key, field_name)` is flagged on 3 nights running (THRESHOLD_NIGHTS=3, 36h window), `should_promote()` returns True and the verdict is auto-promoted to `factual_contradiction`. |
| `factual_contradiction` | POV contradicts a `shared_canon.yaml` anchor. Pinned to the canonical value via `dyad_state_pins` (symmetric: `pov_character_id=None`). Phase 9 evaluator then refuses to update the pinned dimension until operator resolves. `dreams_qa_pin_blocked` structlog event fires on every subsequent blocked write. |

**Judge prompt.** `consistency/prompt.py::JUDGE_SYSTEM_PROMPT` frames the model as a neutral observer; the user prompt injects the `shared_canon` objective anchor, both POV blocks extracted from the rich YAMLs (via `_extract_pov_block`), and the 7-day episodic memory window. All memory text is sanitized through `_sanitize_for_evidence_block`: truncated to a char cap, `html.escape`'d, then line-prefixed with `> ` so no memory content can steer the prompt (Phase 8 R1-F3 pattern — **AD-006**). JSON-only output contract enforced by `RelationshipCheck.model_validate_json`; `_parse_verdict` unwraps markdown fences.

**Auto-promote heuristic.** `consistency/auto_promote.py::should_promote()` uses DB-side timestamps (`NOW()`) for clock-skew defense. `THRESHOLD_NIGHTS=3`, `NIGHT_WINDOW_HOURS=36` (tolerates DST + cron jitter).

**Notifications.** `dreams/notifications.py::emit_qa_event` dispatches to two destinations:
1. MSE-6 structlog at INFO / WARNING / ERROR by verdict severity.
2. Daily markdown ledger at `Docs/_dreams_qa/YYYY-MM-DD_consistency.md` with three sections (Healthy / Drift watch / Operator review required). The read-modify-write critical section is serialized by `_file_lock` (msvcrt.locking on Windows, fcntl.flock on POSIX, no-op fallback with warning on stripped builds — Phase 10.7 F2 remediation).

**Weekly digest.** `consistency/digest.py::build_weekly()` reads the last 7 daily ledger files, compares 7-day drift score against prior 7-day window, emits `Docs/_dreams_qa/_weekly/YYYY-WW.md` with per-relationship trajectory labels (`improving` / `stable` / `drifting`).

---

## 12. Relationship evaluators

Two post-turn evaluators run in fire-and-forget mode after the HTTP response closes. Both are gated by the Phase 10.7 pin-consult (**AD-005**).

### Phase 8 — Whyze-dyads (`api/orchestration/relationship.py::evaluate_and_update`)

Updates the focal character's `dyad_state_whyze` row. Four relationships × 5 dimensions (`trust`, `intimacy`, `conflict`, `unresolved_tension`, `repair_history`, each `[0, 1]`). **Delta cap: ±0.03 per turn per dimension** (hard invariant, **AD-004**).

LLM-primary via `BDOne.complete()` + `relationship_prompts.parse_eval_response`. Heuristic fallback (`_propose_deltas`) fires on any of:
1. Settings opt-out (`relationship_eval_llm=False`)
2. No `llm_client` supplied
3. Circuit breaker open
4. LLM raises `DreamsLLMError`
5. Parser returns `None` (malformed JSON)

Both paths feed `_clamp_delta()` (final ±0.03 gate) and `_bound01()` ([0, 1] clamp). Shared with Phase 9.

### Phase 9 — inter-woman dyads (`api/orchestration/internal_relationship.py::evaluate_and_update_internal`)

Updates `dyad_state_internal` rows. Six relationships × 5 dimensions. Same ±0.03 cap. **Alicia-orbital SQL gate:** only rows with `is_currently_active=True` are updated, so dormant Alicia dyads neither spend LLM budget nor accumulate drift (AC-9.11).

**Phase 10.7 pin-consult** (`internal_relationship.py:372`–`388`). Before each of the 5 dimension writes, the evaluator calls `is_pinned(session, relationship_key, pov_character_id=None, field_name)`. If the dimension is pinned, the evaluator zeroes the delta, accumulates the blocked field name, and emits a `dreams_qa_pin_blocked` structlog event with the offending field. Surviving deltas then apply. This is symmetric pinning (`pov_character_id=None`): one pin blocks all POV writes on that dimension for that relationship.

### Scheduling

`api/orchestration/post_turn.py::schedule_post_turn_tasks()` spawns both evaluators plus `extract_episodic()` as `asyncio.create_task()` with `add_done_callback(_log_task_outcome)`. The HTTP SSE stream closes before any post-turn task completes — failures never delay or corrupt the user-visible reply (AC-7.10).

---

## 13. Whyze-Byte validation and fidelity

**Entry:** `validation/whyze_byte.py::validate_response()` (line 329).

**Two-tier structure:**
- **Tier 1 (FAIL):** hard stops — AI-isms ("As an AI…"), framework leakage, XML-tag bleed, prompt marker echoes in response. Any FAIL triggers regeneration (single-speaker) or per-speaker error chunk (crew).
- **Tier 2 (WARN):** soft findings — repetition, cognitive drift, hand-offs, em-dash hygiene, cross-character contamination (e.g., Bina using Alicia markers). Collected; caller decides regenerate or log.

Result object: `ValidationResult(character_id, passed, violations)`. Gated at pipeline step 8 (single-speaker) and per-speaker inside `_run_crew_turn` (step 9). Crew FAIL emits an error chunk but does not abort the loop; only validated text persists into the next speaker's context.

**Fidelity rubrics** (`validation/fidelity.py`). 7 dimensions × 4 characters = 28 rubrics. Static scoring with no LLM calls: per-character marker presence + anti-pattern absence + structural markers. Composite score = `0.5×markers + 0.3×anti_pattern + 0.2×structural`. Full suite completes in under 10 seconds.

---

## 14. Scene Director

Two pure-synchronous functions (no DB, no LLM, test-friendly).

**`scene/classifier.py::classify_scene()`** (line 124). Ingests user message + present characters + `alicia_home` flag + optional caller hints. Emits a fully-populated `SceneState` with:

- `CommunicationMode` — hint → keyword (`in_person` / `phone` / `letter` / `video_call`) → `IN_PERSON` default
- Alicia residence gate — Alicia present + away + IN_PERSON → `AliciaAwayContradictionError`
- `SceneType` — 8 values (`domestic`, `intimate`, `conflict`, `repair`, `public`, `group`, `solo_pair`, `transition`); hint → keyword chain → presence count → DOMESTIC default
- `SceneModifiers` — 6 stackable flags
- `scene_description` — synthesized canonical string

**`scene/next_speaker.py::select_next_speaker()`** (line 130). Injected `DyadStateProvider` Protocol so tests stub and production wraps R5. Seven-rule scoring (order matters):
1. Residence zero-out (Alicia away + in-person → 0)
2. Rule of One (already spoke this turn → 0)
3. Talk-to-Each-Other mandate (last 2 turns both to Whyze → reward w2w candidates, penalize others)
4. Woman-to-woman continuation (last turn w2w → reward)
5. Dyad-state fitness (intimacy/tension with other present women)
6. Recency suppression (just spoke non-Whyze → penalty)
7. Narrative salience (Rule 7 — candidate name in scene_description or activity_context → boost)

Highest score wins; ties broken by stable canonical ordering (adelia, bina, reina, alicia). Raises `NoValidSpeakerError` if every candidate is zeroed.

---

## 15. API surface

Port 8001. `X-API-Key` header required on `POST /v1/chat/completions`; other endpoints are public.

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/health/live` | Liveness probe (always 200 if process alive) | None |
| GET | `/health/ready` | Readiness — verifies R5 pool open; if `HEALTH_BD1_PROBE=true`, issues a HEAD against the SFW provider | None |
| GET | `/v1/models` | 5 entries (`starry-lyfe` legacy + 4 character IDs) with fixed epoch 1776816000 | None |
| POST | `/v1/chat/completions` | OpenAI-compatible chat, SSE streaming. Requests: `{model, messages, stream}`. Responses: `data: {choices: [{delta: {role, content}}]}` chunks terminated with `data: [DONE]`. Crew mode adds inline `**Name:**\n\n` attribution between speakers. | `X-API-Key` |
| GET | `/metrics` | Prometheus scrape | None |

**FastAPI factory:** `api/app.py::create_app()` (line 59) — lifespan loads `Canon`, DB engine + session factory, `LMStudioEmbeddingService`, `BDOne` client; all stashed on `app.state`. `state_overrides` test hook swaps in stubs.

**Request/response schemas:** `api/schemas/chat.py` (OpenAI-compatible `ChatCompletionsRequest`, `ChatCompletionChunk`, `ChatCompletionDelta`).

**Character routing** (`api/routing/character.py::resolve_character_id`). Four-stage precedence:
1. `X-SC-Force-Character` header (dev/test)
2. Inline `/<char>` or `/all` override at message start (stripped before LLM sees it)
3. `model` field — the Msty Persona path (production)
4. `settings.default_character` fallback (`adelia` default)

Unknown IDs raise `CharacterNotFoundError` (HTTP 400).

**Crew preprocessing** (`api/routing/msty.py::preprocess_msty_request`). Strips the (empty in production) system prompt, extracts prior persona responses from `name`-tagged assistant messages or `"<character>:"` prefixes, computes the scene roster as the intersection of system-prompt mentions and prior-speaker canonical IDs, returns stable canonical ordering in `MstyPreprocessed`.

---

## 16. Configuration

**Namespace:** `STARRY_LYFE__{CATEGORY}__{NAME}`. GNK-mediated; no `os.environ` access outside `config.py` files.

### Required

| Variable | Purpose |
|---|---|
| `STARRY_LYFE__API__PORT` | 8001 in production |
| `STARRY_LYFE__API__API_KEY` | X-API-Key validation; absent → readiness 503 |
| `STARRY_LYFE__DB__HOST`, `__PORT`, `__NAME`, `__USER`, `__PASSWORD` | PostgreSQL connection |
| `STARRY_LYFE__EXT__SFW_PROVIDER_URL`, `__SFW_PROVIDER_KEY` | OpenRouter / Anthropic SFW completion endpoint |

### Optional (with defaults)

| Variable | Default | Purpose |
|---|---|---|
| `STARRY_LYFE__API__HOST` | `0.0.0.0` | Bind interface |
| `STARRY_LYFE__API__CORS_ORIGINS` | (empty) | Empty disables CORS |
| `STARRY_LYFE__API__DEFAULT_CHARACTER` | `adelia` | Fallback when routing precedence exhausts |
| `STARRY_LYFE__API__HEALTH_BD1_PROBE` | `true` | `/health/ready` HEAD probe against BD-1 provider |
| `STARRY_LYFE__API__CREW_MAX_SPEAKERS` | `3` | Crew loop iteration cap (CLAUDE.md §16 axiom) |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM` | `true` | Phase 8 toggle; false forces heuristic |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_MAX_TOKENS` | `200` | Phase 8 LLM budget |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_TEMPERATURE` | `0.2` | Phase 8 LLM temperature |
| `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM` | `true` | Phase 9 toggle |
| `STARRY_LYFE__EXT__SFW_MODEL` | `deepseek/deepseek-v3.2` | SFW model id |
| `STARRY_LYFE__EXT__EMBEDDING_MODEL` | `text-embedding-nomic-embed-text-v1.5@q5_k_m` | LM Studio embedding model |
| `STARRY_LYFE__EXT__EMBEDDING_DIMENSION` | `768` | Must match `episodic_memories.embedding` column |
| `STARRY_LYFE__EXT__EMBEDDING_BASE_URL` | `http://localhost:1234/v1` | LM Studio OpenAI-compatible base |
| `STARRY_LYFE__LOG__LEVEL` | `INFO` | MSE-6 structlog level |
| `STARRY_LYFE__ENV` | `development` | Env tag for structured logs |

The authoritative list always lives in `.env.example`. Drift detection (CLAUDE.md §2 standing order): any env var used in code must be in `.env.example`, and this document's §Configuration must match.

---

## 17. Infrastructure

**Runtime stack** (see `pyproject.toml`):
- Python 3.11+ (cap `<4.0` via dependency pins)
- Pydantic v2 (`pydantic>=2.0,<3.0`, `pydantic-settings>=2.0,<3.0`)
- SQLAlchemy 2.0+ async + `asyncpg` driver + `pgvector>=0.3`
- Alembic 1.13+ for migrations
- FastAPI 0.115+ + `uvicorn[standard]` + `sse-starlette`
- `apscheduler` for Dreams daemon
- `httpx>=0.27` for all outbound HTTP (no `requests`)
- `prometheus-client` for `/metrics`
- `mypy>=1.10 --strict`, `ruff>=0.4`, `pytest>=8.0` + `pytest-asyncio`

**Database.** `docker/docker-compose.yml` runs a single `postgres` service using `pgvector/pgvector:pg16`. Container name `Starry-Lyfe`. Port 5432 → host. Named volume `starry-lyfe-pgdata`. Healthcheck via `pg_isready -U starry_lyfe -d starry_lyfe` (10s interval, 5s timeout, 5 retries). Network `starry-lyfe-net`.

**Embedding provider.** LM Studio running the Nomic embedding model via OpenAI-compatible `/v1/embeddings` at `http://localhost:1234/v1`. Dimension 768. The writer path uses a zero-vector default if the real embedder is unavailable; similarity search is inert for zero-vector rows but does not error.

**SFW completion provider.** OpenRouter or Anthropic endpoint via `BDOne` (`dreams/llm.py`). Default model `deepseek/deepseek-v3.2`; override via env. 30-second default timeout. Circuit breaker tracks consecutive failures; backoff + jitter on retry.

**No API Dockerfile today.** `uvicorn` runs locally against the containerized Postgres. Containerizing the API service is deferred operational work.

---

## 18. Protocol droid registry

Per CLAUDE.md §5, core infrastructure concerns are cast as codenamed "droids" — either explicit `typing.Protocol` classes or module-level conventions implemented across the codebase.

| Droid | Concern | Implementation |
|---|---|---|
| **GNK** | Config, env, secrets | `{api,dreams,db}/config.py` (`ApiSettings`, `DreamsSettings`, `DatabaseSettings`). Resolution: env → `.env` → defaults. No `os.environ` outside `config.py`. |
| **R5-D4** | DB connectivity | `db/engine.py` — async engine + session factory + pool lifecycle; all queries parameterized; `asyncpg` + SQLAlchemy 2.0+. |
| **BD-1** | HTTP client | `dreams/llm.py::BDOne` (prod) + `StubBDOne` (test double). All outbound HTTP uses `httpx.AsyncClient` with mandatory timeout. Circuit breaker + retry. |
| **MSE-6** | Observability | `structlog` throughout. Levels DEBUG / INFO / WARNING / ERROR. Every entry carries `service`, `timestamp`, `level`, plus contextual keys. Never logs secrets. Prometheus metrics middleware at `api/endpoints/metrics.py`. |
| **2-1B** | Health checks | `api/endpoints/health.py` — `/health/live` + `/health/ready` (verifies R5 + optionally probes BD-1). Under 5s response. |
| **WED-15** | Error handling / retry | `dreams/llm.py` (circuit breaker + exponential-backoff retry + retryable vs terminal classification) and per-subsystem error hierarchies rooted at `ServiceError` (`api/errors.py`). |

No dedicated `src/starry_lyfe/protocols/` sub-package today; droid surfaces are integrated inline with module-level conventions. This is documented as-built; adding a formal `protocols/` package is not on the architectural track.

---

## 19. Test architecture

**Current baseline:** 1,257 passed / 0 failed / 38 environmental Postgres skips / 0 xfailed.
**WAF gate:** `make check` = `ruff check` + `mypy --strict` + `pytest` (full suite). Clean on commit `8a7163e`.

### Taxonomy

| Location | Mocking | Purpose |
|---|---|---|
| `tests/unit/` | Mock freely | Isolated function/class behavior |
| `tests/integration/` | **Forbidden** on R5 / BD-1 / GNK | Real DB + real HTTP stubs only where the LLM is the *outbound* target. All R5-dependent tests are skip-gated when Postgres is unreachable. |
| `tests/fidelity/` | Static only | Per-character rubrics — voice axioms, canonical marker presence, anti-pattern absence, pair authenticity |
| `tests/regression/` | Static | Phase H assembled-prompt bundle (regression against prior baselines) |

### Key patterns

- **`seeded_session` fixture** (`tests/integration/conftest.py`) — real Postgres session with seeded Tier 1–4 + Tier 7 state. Skip-gated if Postgres unreachable. Standard integration entry point.
- **Repo-local scratch dirs** — `.test_tmp/` under the repo root. Windows `%TEMP%` has an ACL fault that breaks pytest's `tmp_path`; all tests needing scratch space use `_make_repo_local_tempdir()` instead (**AD-007**).
- **Stub LLM clients** — `StubBDOne` (production test double) and `_SyntheticStubBDOne` (QA-judge-specific canned-verdict stub) replace the BD-1 *outbound* target. They are not mocks of BD-1 itself; they mock the upstream LLM endpoint that BD-1 would call.
- **Phase H regression bundle** — `tests/regression/` re-baselined assembled-prompt comparisons. A first-class ship gate on every subsequent phase (**AD-008**).

Historical per-phase test deltas live in `Docs/_phases/`.

---

## 20. Governance

**Authority hierarchy** (highest to lowest):
1. `CLAUDE.md` — the sacred text. Part 1 (§1–§10 universal) is shared across repos; Part 2 (§11–§19 project) is starry-lyfe specific. On conflict, CLAUDE.md wins.
2. This document (`Docs/ARCHITECTURE.md`) — as-built reference. Updated on merge per CLAUDE.md §2 standing order.
3. Phase reports (`Docs/_phases/`) — chronological delivery record with audit + remediation history.
4. Operator runtime walkthrough (`Docs/OPERATOR_GUIDE.md`) — markdown-to-prompt trace, per-scene examples.
5. Chronological migration ledger (`journal.txt` at repo root) — Phase 10 YAML-authority migration entries, with F1/F2/F3 audit remediation notes.
6. Other specs: `Docs/IMPLEMENTATION_PLAN_v7.1.md`, `Docs/Persona_Tier_Framework_v7.1.md`, `Vision/Starry-Lyfe_Vision_v7.1.md`.

**Plan-mode plans** live at `C:\Users\Whyze\.claude\plans\`. Ephemeral Claude Code scripts (patches, inspections) live at `C:\Users\Whyze\.claude\scripts\` per the user-global CLAUDE.md. Never in the project root, never in the home directory.

**Foundry SDLC (CLAUDE.md §2).** Six phases: Hydration → Execution → WAF → Audit → Remediation → Merge Gate. Owners: Armorer (Chief of Architecture), Kuiil (Claude Code execution), Paz Vizsla (Codex audit), Project Owner (Shawn).

**Conventional Commits** (CLAUDE.md §6). Branches `feat|fix|refactor|docs|chore/{scope}-{description}`. Every commit ends with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.

**Quality directive (CLAUDE.md §19 priority order):** Vision attainment → character fidelity → canonical correctness → test correctness → ship velocity → token budget. Speed never trumps quality; budget never trumps soul content.

---

## 21. Architectural decisions

No separate `Docs/decisions/` ADR tree; decisions live inline here and in phase reports.

- **AD-001 — Backend is the sole voice authority.** Msty Persona `System Prompt Mode = Replace`, blank in production. The 7-layer assembled prompt is the entire voice surface; nothing leaks from the Msty UI. (Phase 7.)

- **AD-002 — Per-character POV with enforced divergence.** Inter-woman dyads have intentionally non-identical POV prose. AC-10.21 fails the build if any two POV blocks become byte-identical — "drift toward agreeable mush" is the regression direction. The dramaturgical reason: the gap between POVs IS the story. (Phase 10.5b RT2.)

- **AD-003 — Terminal 6-file YAML authoring surface.** Five rich per-character YAMLs plus `shared_canon.yaml` are the sole runtime-authoritative source for every canonical character and every cross-character structured fact. Narrow canon YAMLs retired to `Archive/v7.1_pre_yaml/canon/narrow/`. Single-source-of-truth principle enforced at the loader. (Phase 10.5c.)

- **AD-004 — LLM-primary / heuristic-fallback + ±0.03 delta cap.** Relationship evaluators try the LLM path first; fall back to heuristic `_propose_*` functions on any failure. Final clamp at ±0.03 per dimension per turn is a hard invariant independent of path. (Phase 8 + Phase 9.)

- **AD-005 — Symmetric pinning blocks drift compounding.** Phase 10.7 `dyad_state_pins` uses `pov_character_id=None` for symmetric pins that block both POVs on a dimension. Phase 9 consults `is_pinned()` before each of 5 dimension writes; blocked writes emit `dreams_qa_pin_blocked`. (Phase 10.7.)

- **AD-006 — Phase 8 R1-F3 input-sanitation pattern.** Any untrusted content entering an LLM prompt (episodic memories in the QA judge, user-supplied register prose, etc.) is truncated → `html.escape`d → line-prefixed with `> `. Applied universally after the R1-F3 finding. (Phase 8 R1, Phase 10.7.)

- **AD-007 — Repo-local test scratch dirs.** Tests needing filesystem scratch space write to `.test_tmp/` under the repo root, not `%TEMP%`. Windows ACL fault on `%TEMP%/pytest-of-Whyze` makes `tmp_path` unreliable in this workspace. (Phase 10.7 F2; pattern originated in `tests/unit/test_residue_grep.py`.)

- **AD-008 — Phase H regression bundle is a first-class ship gate.** Every phase that touches prompt assembly must re-run the Phase H regression and produce byte-identical output on the unchanged code paths. Drift in assembled prompts is a regression regardless of test count. (Phase H; reaffirmed every phase through 10.7.)

---

## 22. Evolution summary

The v7 architectural track spans phases 0 → 10.7, shipped across 2026-04-12 to 2026-04-17. Major clusters (see `Docs/_phases/` for detailed records):

- **Phase 0 – K (lettered track, 2026-04-12 → 2026-04-13)** — Canon YAML, memory service, structure-preserving kernel compilation, budget elevation, live pair data, voice exemplars, scene-aware section retrieval, dramaturgical prose rendering, fidelity harness, hybrid regression methodology, subjective success proxies. Twelve sub-phases.
- **Phase 4 (Whyze-Byte Validation Pipeline, 2026-04-13)** — two-tier validator.
- **Phase 5 (Scene Director, 2026-04-14)** — classifier + next-speaker scoring.
- **Phase 6 (Dreams Engine, 2026-04-15)** — nightly batch, five generators + writers + consolidation.
- **Phase 7 (HTTP Service on Port 8001, 2026-04-15)** — FastAPI, SSE, Crew mode, Msty preprocessing.
- **Phase 8 (LLM Relationship Evaluator, sealed 2026-04-15)** — Whyze-dyads; shared Pydantic primitives.
- **Phase 9 (Inter-woman DyadStateInternal evaluator, sealed 2026-04-16)** — six dyads, Alicia-orbital gate, all-six divergence.
- **Phase 10.0 – 10.7 (YAML Source-of-Truth Migration + Dreams Consistency QA, 2026-04-16 → 2026-04-17)** — gap audit, schema+loader, kernel/voice cutover, soul essence + cards cutover, constraint pillars, archive + governance (10.5), schema hardening (10.5b), narrow-canon loader rewire to terminal 6-file surface (10.5c), preserve-marker enforcement hardening (10.6), Dreams Consistency QA + Phase 9 pin-consult + audit remediation (10.7).

Chronological migration ledger: `journal.txt` at repo root.

---

## 23. Changelog

### [1.0.0] — 2026-04-17

- **Clean-slate rewrite** as a comprehensive production reference for the v7 terminal architectural state (commit `8a7163e`).
- Replaces the 156-line 0.9.2 stub dated 2026-04-15 (pre-Phase-8-seal).
- Covers 23 sections: executive summary, context, system map, 12-step request path, 115-file module registry, 7-layer assembly with guaranteed surcharges, 17-table data model with 5-migration Alembic chain, terminal 6-file canon authority, soul architecture (4 layers reaching the model), Dreams Engine (6 generators), Phase 10.7 Consistency QA sub-pipeline, Phase 8/9/10.7 relationship evaluators, Whyze-Byte validation, Scene Director, API surface, configuration, infrastructure, protocol droid registry, test architecture (1,257 passed / 38 environmental Postgres skips), governance, 8 architectural decisions, evolution summary.
- Phase reports in `Docs/_phases/` remain the authoritative chronological delivery record.

### [0.9.x] — pre-1.0

Prior minor-version history preserved in git log; content superseded by the 1.0.0 rewrite.
