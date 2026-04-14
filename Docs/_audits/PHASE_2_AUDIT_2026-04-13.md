# Phase 2 End Audit (2026-04-13)

**Auditor:** Claude Code (self-audit at Project Owner request)
**Scope:** CHANGELOG Phase 1 (Canon YAML) + Phase 2 (Memory Service). Excludes Phase 3 context assembly.
**Gate recommendation:** **PASS WITH MANDATORY FIXES**
**Critical findings:** 4
**High findings:** 5
**Medium findings:** 4
**Low findings:** 2
**Sample drift audit:** All 4 Phase F samples PASS all 8 dimensions.

---

## Executive Summary

Foundation is solid but accumulating silent-failure risk. Five load-bearing invariants from Vision §5-§7 and PTF §2.1 are enforceable in the architecture but not all verified at startup. Sample drift audit of all 4 Phase F assembled prompts came back **clean on every check** (character distinctness, diacritic preservation, canonical markers, pair metadata, terminal anchoring, Layer 7 modifier effects). The risk is not in what's shipping today — it's in the failure modes that masquerade as success.


Four critical findings must land before Phase 3 assembly work can be trusted to compound safely.

---

## Scope Clarification

"Up to Phase 2 end" maps to **CHANGELOG Phase 1 + Phase 2**:

- **Phase 1** — Canon YAML scaffolding (`src/starry_lyfe/canon/`): characters.yaml, pairs.yaml, dyads.yaml, protocols.yaml, interlocks.yaml, voice_parameters.yaml, validator, soul_essence, soul_cards, pairs_loader.
- **Phase 2** — Memory Service (`src/starry_lyfe/db/`): PostgreSQL + pgvector, 7-tier memory schema, exponential decay, Alembic migrations, retrieval.

Excluded: Phase 3 context assembly (kernel_loader, layers, assembler, constraints), Phase E/F execution work. That code is the delivery mechanism; this audit examines the *foundations* the delivery sits on.

---

## Vision Invariants (The Checklist That Must Never Break)

From `Docs/IMPLEMENTATION_PLAN_v7.1.md` §5-§7 and `Docs/Persona_Tier_Framework_v7.1.md` §2.1-§2.7:

| # | Invariant | Source | Enforcement Mechanism |
|---|-----------|--------|----------------------|
| V1 | Public-scene gate — erotic content shuts off when witnesses present | PTF §2.1 | `constraints.py:119` (`public_scene` or `work_colleagues_present`) |
| V2 | No internal disclosure (framework, XML tags, protocols) | PTF §2.2 | Tier 1 axiom + anti-echo directive |
| V3 | No AI mention | PTF §2.3 | Tier 1 axiom |
| V4 | No cross-character speech | PTF §2.4 | Tier 1 axiom |
| V5 | Polyamory as architecture, never re-litigated | PTF §2.7 | Tier 1 axiom |
| V6 | Cognitive Hand-Off Integrity — no function poaching | Vision §7 | **Not enforced in code** — relies on soul essence + voice exemplars |
| V7 | Talk-to-Each-Other mandate (multi-woman scenes) | Vision §6 | `constraints.py:145` (≥2 canonical women) |
| V8 | Non-redundancy of 4 characters | Vision §6 | Pair metadata + per-character voice exemplars + soul essence |
| V9 | Entangled Pair as gravitational center | Vision §5 | Soul essence `pair` block + pair soul cards |
| V10 | Intermittent-presence integrity (Alicia) | Vision §6 | `AliciaAwayError` check in assembler |

**V6 is the weakest enforcement.** "Cognitive Hand-Off Integrity" has no code-level tripwire — only prompt-level guidance. Acceptable at Phase 2 end but must be watched for drift as scale increases.

---

## Critical Findings (FAIL-threatening)

### C1. Soul essence silently returns empty string for missing character

**File:** `src/starry_lyfe/canon/soul_essence.py:849-851`

`format_soul_essence()` returns `""` when a character is not registered. The assembler at `kernel_loader.py:287` unconditionally prepends this to the kernel body. **Result:** Layer 1 ships without the load-bearing soul substrate, and nothing flags the regression.

**Threat to Vision:** Directly threatens V6-V9. A missing soul essence means the character loses her canonical identity substrate. She becomes "a woman who could apply to any of them" — the exact FAIL condition Vision §7 calls out.

**Fix:** `format_soul_essence()` must `raise ValueError(f"No soul essence registered for {character_id}")`. Callers must handle explicitly or let it propagate to surface the regression.

### C2. Kernel cache key omits scene profile

**File:** `src/starry_lyfe/context/kernel_loader.py:316-322`

Cache key is `f"{character_id}:{budget}:{promote_tuple}"`. When two different profile paths coincidentally resolve to the same numeric budget, the cached result from one profile serves the other. Silent budget misalignment.

**Threat to Vision:** V8 (non-redundancy via differentiated kernel content) becomes unreliable under cache hits. Wrong section compression ships.

**Fix:** Include profile name in the key: `f"{character_id}:{budget}:{profile_name}:{promote_tuple}"`. Or explicitly bust the cache when scene profile changes.

### C3. No startup canon validation

**File:** `src/starry_lyfe/canon/validator.py` (exists but only runnable via CLI)

`load_all_canon()` does not invoke the validator. Invalid canon (missing cross-references, schema violations, duplicate IDs) ships to production. Comprehensive cross-reference checks only fire when an operator remembers to run them.

**Threat to Vision:** V9 and V8 depend on pairs.yaml, dyads.yaml, interlocks.yaml all referencing consistent character IDs. Silent drift here means the wrong pair metadata could ship for a character without anyone noticing until a sample audit catches it weeks later.

**Fix:** Add `validate_on_load: bool = True` parameter to `load_all_canon()`. Fail loud at startup, not quietly at inference.

### C4. Hardcoded character list scattered across 6 modules

**Files:**
- `src/starry_lyfe/context/budgets.py:59-62` (`CHARACTER_KERNEL_BUDGET_SCALING`)
- `src/starry_lyfe/context/kernel_loader.py:14-50` (`KERNEL_PATHS`, `VOICE_PATHS`)
- `src/starry_lyfe/canon/pairs_loader.py:34-39` (`_CHARACTER_TO_PAIR`)
- `src/starry_lyfe/context/prose.py:33-58` (per-character prose dicts)
- `src/starry_lyfe/context/constraints.py` (per-character pillars, Alicia mode-conditional)
- `src/starry_lyfe/canon/soul_essence.py` (per-character `SoulEssence` registry)

Adding a fifth character means updating at least 6 locations. Missing one silently breaks that feature for that character.

**Threat to Vision:** V8 (non-redundancy) assumes all character-keyed systems are in sync. Partial onboarding creates asymmetric failure modes tests won't catch.

**Fix:** Single source of truth — `src/starry_lyfe/canon/schemas/enums.py::CharacterID`. All other dicts validate their keys against it at module load time.

---

## High-Severity Findings

### H1. Pair loader silently skips missing YAML entries
**File:** `src/starry_lyfe/canon/pairs_loader.py:56-71`
Sets `_yaml_loaded=True` after first call. Second call for missing pair raises `ValueError` at access time rather than load time. Authoring errors discovered late.
**Fix:** Collect missing pairs during load, raise with full list if any are missing.

### H2. Decay config silently defaults to hardcoded values
**File:** `src/starry_lyfe/db/retrieval.py:156-162`
`.get(key, default)` for decay parameters (fatigue=8.0h, stress=24.0h, injury=72.0h). If DB record omits a key, defaults silently apply. No log, no audit trail.
**Fix:** Raise if decay_config schema is incomplete. Move defaults to migration seed, not runtime fallback.

### H3. Type safety gap — `activation: dict[str, Any]`
**File:** `src/starry_lyfe/context/soul_cards.py:33, 77`
Soul card activation rules use `dict[str, Any]` with no Pydantic validation at load time. Invalid frontmatter only discovered when a card fails to activate.
**Fix:** Define `SoulCardActivation` Pydantic model with strict fields. Validate at `load_soul_card()`.

### H4. Budget reservations not reconciled against actual emission
**Files:** `src/starry_lyfe/context/budgets.py:55-62`, `src/starry_lyfe/context/assembler.py:107-115`
Assembler reserves `pair_card_tokens` and `knowledge_card_tokens` but no post-assembly assertion confirms Layer 1 and Layer 6 respect those budgets.
**Fix:** Post-assembly invariant: `assert estimate_tokens(layer_1.text) <= kernel_budget + soul_essence_surcharge`. WARN on overrun.

### H5. Seed script exception handler swallows tracebacks
**File:** `src/starry_lyfe/db/seed.py:247-251`
Catches any exception, prints brief message to stderr, exits code 1. Operators debugging a bad seed get no traceback.
**Fix:** `traceback.print_exc()` before exit.

---

## Medium-Severity Findings

### M1. Stale/unclear comments
- `budgets.py:45` — `"raised from 1200"` references change history without tracking when/why.

### M2. `# type: ignore` without rationale
**File:** `src/starry_lyfe/context/budgets.py:201`
If the regex changes, `.group(1)` fails at runtime and the ignore masks the static warning that would have caught it.
**Fix:** Use walrus operator: `if (m := _HEADING_RE.match(line)): m.group(1)`.

### M3. Silent None-return in load_voice_examples / load_voice_guidance
**File:** `src/starry_lyfe/context/kernel_loader.py:568, 399`
Returns `None` when Voice.md doesn't exist. Acceptable during bootstrap but should WARN-log since missing voice files degrade V8.
**Fix:** Add `logger.warning(f"Voice.md not found for {character_id}")` at fall-through.

### M4. No observability for fallback activations
**File:** `src/starry_lyfe/context/layers.py`
`load_voice_guidance()` fallback path (pre-Phase-E, no mode tags) has no observability. An operator cannot tell from logs which characters are still on the legacy path.
**Fix:** Emit one-time WARN at first load if Voice.md has zero mode-tagged examples.

---

## Low-Severity Findings

### L1. Dead branch in `_select_voice_exemplars` communication_mode filter
Fallback `examples[:max_exemplars]` when communication_mode filter removes all candidates is unreachable in current data shape. Tests cover synthetic only.
**Fix:** Document branch as defense-in-depth or add real test scenario.

### L2. Inconsistent error classes
`ValueError` for missing character in one place, `KeyError` in another.
**Fix:** Define `CharacterNotFoundError(ValueError)`.

---

## Sample Drift Audit — All Passing

All four Phase F sample artifacts pass every drift dimension:

| Dimension | adelia | bina | reina | alicia |
|-----------|:---:|:---:|:---:|:---:|
| Voice distinctness (Ne/Si/Se-tactical/Se-somatic) | PASS | PASS | PASS | PASS |
| Canonical markers (with diacritics) | PASS | PASS | PASS | PASS |
| Pair metadata 6-field block | PASS | PASS | PASS | PASS |
| Voice rhythm exemplars header | PASS | PASS | PASS | PASS |
| Scene-type promotion visible | PASS | PASS | PASS | PASS |
| Terminal anchoring | PASS | PASS | PASS | PASS |
| Soul essence sections | PASS | PASS | PASS | PASS |
| Layer 7 modifier effects (where applicable) | n/a | n/a | PASS (CRASH) | PASS (GATE) |

Canonical markers verified with diacritics: **Marrickville, Valencia, Las Fallas, Héroes del Silencio, mascletà, Urmia, Gilgamesh, tahchin, Arash, Gràcia, Okotoks, Cuatrecasas, Plaça de la Virreina, granaínos, Famaillá, Tucumán, azahar, zafra, porteños, ferretería, ISEN, Cancillería**. Zero diacritic loss.

This is the strongest positive signal in the audit. The runtime surface is delivering the Vision correctly **today**. The critical findings are about preventing silent regression, not about existing breakage.

---

## Recommended Remediation Order

1. **Land C1 (soul essence raises)** before Phase 3 assembly work compounds. Single highest-leverage defense against character dilution.
2. **Land C3 (startup canon validation)** to catch authoring errors before they ship.
3. **Land C4 (single-source character list)** before any fifth-character onboarding.
4. **Land C2 (cache key fix)** during the next kernel_loader pass.
5. **Bundle H1-H5** into a single "silent failure elimination" commit.
6. **Defer M1-M4 and L1-L2** to polish phases.

None of these block Phase 3 work from starting, but C1-C4 should be a precondition for declaring Phase 2 end "truly shipped." The Vision is attainable; the foundation needs tighter failure semantics.

---

**End of audit.**
