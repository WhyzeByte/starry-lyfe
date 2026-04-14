# Remediation Spec — Phase 2 Audit + Conversion Assessment Consolidation

**Authored:** 2026-04-13
**Author:** Claude AI (Step 5 QA)
**Status:** **APPROVED — ready for Claude Code Tier 1 handoff**
**Resolutions:** All open questions resolved by Project Owner 2026-04-13. See §9.
**Source findings:**
- `PHASE_2_AUDIT_2026-04-13.md` (Claude Code self-audit, CHANGELOG Phases 1–2)
- `character_conversion_assessment.md` (external review, 2026-04-14, unsigned)

**Scope note:** This remediation covers foundation hardening for CHANGELOG Phases 1 (Canon YAML) and 2 (Memory Service). It runs **parallel to** the currently-executing Foundry Phase D and does not block it. The two workstreams touch different surfaces.

---

## 0. Executive Summary

The Phase 2 audit surfaces real anti-regression work. Sample drift is clean on every dimension across all four characters — the runtime is delivering Vision today. The findings are about **preventing silent failure**, not fixing existing breakage.

Four critical findings (C1–C4), five high (H1–H5), six polish (M1–M4, L1–L2). This spec lands them in three tiers. It also consolidates three high-value ideas from the conversion assessment that do **not** conflict with canon, and explicitly rejects the recommendations that do.

**Gate:** Tier 1 (C1+C2+C3) is a precondition for declaring "Phase 2 end truly shipped." Tier 2 is a follow-up commit. Tier 3 folds into post-Phase-D planning.

---

## 1. Tier 1 — Mandatory Hardening (ship before next assembly work compounds)

### R-1.1 — Soul essence must fail loud on missing character [audit C1]

**File:** `src/starry_lyfe/canon/soul_essence.py`

**Current behavior:** `format_soul_essence(character_id)` returns `""` when the character is not in `_SOUL_ESSENCE_REGISTRY`. The assembler at `kernel_loader.py:287` unconditionally prepends this to the kernel body. A missing soul essence ships as a silent regression.

**Vision threat:** V6 (cognitive hand-off integrity), V7 (talk-to-each-other non-redundancy), V8 (4-woman distinctness), V9 (Entangled Pair gravitational center) all depend on the soul essence substrate being present. A silently-dropped essence produces the exact "woman who could apply to any of them" failure mode the Vision calls out.

**Required change:**

```python
class SoulEssenceNotFoundError(ValueError):
    """Raised when format_soul_essence is called with an unregistered character_id."""

def format_soul_essence(character_id: str) -> str:
    if character_id not in _SOUL_ESSENCE_REGISTRY:
        raise SoulEssenceNotFoundError(
            f"No soul essence registered for character_id={character_id!r}. "
            f"Registered: {sorted(_SOUL_ESSENCE_REGISTRY.keys())}"
        )
    # ... existing formatting logic unchanged
```

**Callsite update:** `kernel_loader.py:287` must propagate the raise without catching it. **Strict propagation is the canonical pattern. No intermediate `try/except` blocks anywhere in the assembly chain.**

Rationale: any intermediate catch is a future attenuation point. A later well-meaning refactor could turn ERROR into WARN and silently reintroduce the exact failure mode this fix exists to prevent. Zero-catch propagation is the only form resistant to that drift.

**Call-site audit (required as part of this change):** identify every code path that currently calls the context assembler assuming it is infallible. Each such path must be updated to explicitly handle `SoulEssenceNotFoundError`. Acceptable explicit handlers:

- Production runtime: let it propagate to the turn boundary and fail the turn loudly. Do not substitute a degraded prompt.
- CLI / sample generation: let it propagate to the CLI boundary and exit non-zero with the error message.
- Tests: assert the raise, or use an explicitly registered test fixture character.
- Batch jobs: fail the item, log with full context, move to next. Never silently skip.

**Not acceptable:** bare `except` that logs and returns None. Catching `SoulEssenceNotFoundError` to return a default prompt. Any form of soft degradation.

Diagnostic context (character_id, profile, budget) can be added via a top-level wrapper in a future commit if needed. Tier 1 does not add that wrapper — Tier 1's job is making the raise impossible to silence, and any wrapper added now would become the first attenuation point.

**Acceptance criteria:**
- `format_soul_essence("nonexistent")` raises `SoulEssenceNotFoundError`.
- Error message includes character_id and sorted list of registered characters.
- Assembler surfaces the error with character_id in the traceback.
- **Call-site audit completed:** every caller of the context assembler has been identified and either (a) lets the raise propagate, or (b) catches `SoulEssenceNotFoundError` with an explicit, reviewed, documented handler. No silent catches anywhere in the chain.
- Existing test suite still passes (127 passed baseline).
- New unit test: `test_soul_essence_raises_on_missing_character` in `tests/unit/canon/test_soul_essence.py`.
- New unit test: `test_soul_essence_error_message_lists_registered_characters`.
- New integration test: context assembly for an unregistered character fails loudly, does not emit a prompt.
- New regression test: grep the codebase for `except SoulEssenceNotFoundError` and assert every match is annotated with a rationale comment.

---

### R-1.2 — Kernel cache key must include scene profile [audit C2]

**File:** `src/starry_lyfe/context/kernel_loader.py:316–322`

**Current behavior:** Cache key is `f"{character_id}:{budget}:{promote_tuple}"`. Two different scene profiles that resolve to the same numeric budget share cache entries. First call for `pair_intimate` at 3200 tokens populates the cache; second call for `default` that also resolves to 3200 tokens hits that cache entry and receives the wrong compression.

**Vision threat:** V8 (non-redundancy via differentiated scene compression) becomes unreliable under cache hits. The wrong section promotion/demotion ships, and sample drift audits will not catch it because the bug is keyed on request sequence, not content.

**Required change:**

```python
cache_key = f"{character_id}:{budget}:{profile_name}:{promote_tuple}"
```

Where `profile_name` is the canonical profile identifier (`default`, `pair_intimate`, `multi_woman_group`, `children_gated`, `solo`). If the loader is called without a profile, default to the literal string `"default"` so key shape is stable.

**Acceptance criteria:**
- Cache key includes profile name.
- Regression test: load Adelia at budget=X profile=default, then load Adelia at budget=X profile=pair_intimate, assert the two results differ in their promoted sections and are **not** the same cached object.
- Existing cache hit behavior for identical (character, budget, profile, promote_tuple) tuples preserved.

---

### R-1.3 — Startup canon validation must be on by default [audit C3]

**File:** `src/starry_lyfe/canon/validator.py` + wherever `load_all_canon()` is defined (likely `src/starry_lyfe/canon/__init__.py` or a loader module).

**Current behavior:** The validator exists and is correct. It only runs via CLI. `load_all_canon()` does not invoke it. Invalid canon (cross-reference breakage, duplicate IDs, schema violations) ships to production.

**Vision threat:** V8 and V9 depend on pairs.yaml, dyads.yaml, interlocks.yaml all cross-referencing consistent character IDs. Silent drift here can ship wrong pair metadata for weeks before a sample audit catches it.

**Required change:**

```python
def load_all_canon(validate_on_load: bool = True) -> CanonBundle:
    bundle = _load_raw_canon()
    if validate_on_load:
        report = validate_canon(bundle)
        if not report.ok:
            raise CanonValidationError(
                f"Canon validation failed:\n{report.format_errors()}"
            )
    return bundle
```

**Note:** `validate_on_load=False` is allowed for test fixtures that intentionally construct broken canon, but the production entry points must not pass it.

**Acceptance criteria:**
- Default path validates at load.
- `CanonValidationError` carries a human-readable error list.
- Test: introduce a deliberate broken canon fixture, confirm production loader raises, confirm test-with-`validate_on_load=False` still loads it.
- Startup time increase measured and logged. If >200ms, consider a cached validation result keyed on canon file mtimes.

---

## 2. Tier 2 — Silent Failure Elimination Commit (bundle)

Land as one commit after Tier 1. These are all the same flavor: "fail loud instead of silently defaulting."

### R-2.1 — Pair loader collects all missing entries before raising [audit H1]

**File:** `src/starry_lyfe/canon/pairs_loader.py:56–71`

**Change:** During first load, iterate over the expected pair manifest (`_CHARACTER_TO_PAIR`). Collect every missing YAML entry into a list. If any are missing, raise a single error listing all of them. Do not defer to per-access `ValueError`.

**Acceptance:** authoring a new character without a corresponding pairs.yaml entry fails at import time with a complete list of what's missing, not on first access.

---

### R-2.2 — Decay config must be complete or raise [audit H2]

**File:** `src/starry_lyfe/db/retrieval.py:156–162`

**Change:** Remove `.get(key, default)` fallbacks. Either the DB record has all required decay parameters (fatigue, stress, injury, plus any others defined by schema) or loading raises `DecayConfigIncompleteError`. Move defaults to the Alembic migration seed.

**Acceptance:** seed data round-trips correctly; deleting a decay key from the DB produces a loud error at next retrieval, not silent use of a hardcoded default.

---

### R-2.3 — Soul card activation gets a Pydantic model [audit H3]

**File:** `src/starry_lyfe/context/soul_cards.py:33, 77`

**Change:** Define `SoulCardActivation` as a Pydantic model with strict fields (scene_types, character_ids, modes, priority, token_budget, whatever the current activation dict carries). Validate at `load_soul_card()` time. Invalid frontmatter fails at load, not at activation.

**Acceptance:** every existing soul card in `src/starry_lyfe/canon/soul_cards/` loads cleanly under the new model. Introducing a malformed card fails at load with a Pydantic validation error identifying the offending field.

---

### R-2.4 — Post-assembly budget reconciliation [audit H4]

**Files:** `src/starry_lyfe/context/budgets.py:55–62`, `src/starry_lyfe/context/assembler.py:107–115`

**Change:** After assembly, compute actual Layer 1 and Layer 6 token counts. Assert against reserved budgets:

```python
layer_1_actual = estimate_tokens(assembled.layer_1.text)
layer_1_ceiling = kernel_budget + soul_essence_token_estimate(character_id)
if layer_1_actual > layer_1_ceiling:
    logger.warning(
        f"Layer 1 overrun: {character_id} used {layer_1_actual} "
        f"vs ceiling {layer_1_ceiling}"
    )
```

Warning, not raise — the effective ceiling is `kernel_budget + soul_essence_surcharge` and minor overruns from token estimation drift are not fatal. But they must be visible.

**Acceptance:** regression test forces an overrun and confirms the warning fires. Normal assembly produces no warnings.

---

### R-2.5 — Seed script prints tracebacks [audit H5]

**File:** `src/starry_lyfe/db/seed.py:247–251`

**Change:** `traceback.print_exc()` before `sys.exit(1)`. One-line fix.

**Acceptance:** intentionally breaking seed data produces a full traceback on stderr.

---

## 3. Tier 3 — Single Source of Truth for Character List [audit C4]

This is a larger refactor. It is not a Tier 1 blocker, but it **is** a hard precondition for any fifth-character onboarding.

### R-3.1 — Introduce `CharacterID` enum as single source

**New file:** `src/starry_lyfe/canon/schemas/enums.py`

```python
from enum import Enum

class CharacterID(str, Enum):
    ADELIA = "adelia"
    BINA = "bina"
    REINA = "reina"
    ALICIA = "alicia"

    @classmethod
    def all(cls) -> list["CharacterID"]:
        return list(cls)

    @classmethod
    def all_strings(cls) -> list[str]:
        return [c.value for c in cls]
```

### R-3.2 — All six scattered dicts validate against `CharacterID` at module load

Affected files:
- `src/starry_lyfe/context/budgets.py` (`CHARACTER_KERNEL_BUDGET_SCALING`)
- `src/starry_lyfe/context/kernel_loader.py` (`KERNEL_PATHS`, `VOICE_PATHS`)
- `src/starry_lyfe/canon/pairs_loader.py` (`_CHARACTER_TO_PAIR`)
- `src/starry_lyfe/context/prose.py` (per-character prose dicts)
- `src/starry_lyfe/context/constraints.py` (per-character pillars)
- `src/starry_lyfe/canon/soul_essence.py` (`_SOUL_ESSENCE_REGISTRY`)

Each module gains a load-time assertion:

```python
from starry_lyfe.canon.schemas.enums import CharacterID

_assert_complete_character_keys(
    CHARACTER_KERNEL_BUDGET_SCALING,
    source_name="CHARACTER_KERNEL_BUDGET_SCALING",
)
```

Where `_assert_complete_character_keys` is a shared helper that asserts the dict's keys exactly equal `CharacterID.all_strings()` — no missing characters, no unknown keys, at import time.

**Acceptance:**
- Removing any canonical character from any of the six dicts fails at module import.
- Adding an unknown character to any of the six dicts fails at module import.
- Existing 127-test baseline still passes.
- New test: `test_character_id_coverage` iterates over every module and asserts complete coverage.

**Gate:** **This refactor must land before any fifth-character work begins.** If a fifth character is added before this, the asymmetric-failure risk the audit describes materializes immediately.

---

## 4. Deferred — Polish [audit M1–M4, L1–L2]

Defer to a dedicated polish pass. Not in this remediation commit.

| ID | File | Fix |
|---|---|---|
| M1 | `budgets.py:45` | Remove stale `"raised from 1200"` comment or replace with dated changelog reference |
| M2 | `budgets.py:201` | Replace `# type: ignore` with walrus-operator pattern `if (m := _HEADING_RE.match(line))` |
| M3 | `kernel_loader.py:568, 399` | Add `logger.warning` on missing Voice.md |
| M4 | `layers.py` | Emit one-time WARN on first load of legacy (non-mode-tagged) voice examples |
| L1 | `_select_voice_exemplars` | Document defense-in-depth branch or add real-data test |
| L2 | Error classes | Define `CharacterNotFoundError(ValueError)`, unify ValueError/KeyError usage |

---

## 5. Conversion Assessment Folds

Three ideas from `character_conversion_assessment.md` are strong enough to carry forward. Each is scoped for a **future** Foundry phase, not this remediation commit.

### R-5.1 — Positive Fidelity Test Harness (candidate Phase E)

**Problem identified by conversion assessment:** Whyze-Byte is a negative filter. It catches breaks. It cannot say "this genuinely sounds like her."

**Proposed shape:** per-character canonical test scenes scored against rubrics for:
- voice authenticity (rhythm, register, lexicon vs `*_Voice.md`)
- pair authenticity with Whyze (handoff mechanics vs pair file)
- correct cognitive function expression (Ne/Si/Se-tactical/Se-somatic)
- body register (match to character's canonical somatic patterns)
- conflict register
- repair register
- autonomy outside the pair (friction, work, admin — not just romance)

**Why this matters:** complements Whyze-Byte. Moves the test suite from "did not violate" to "sounds like her." Addresses V6 (cognitive hand-off integrity) which currently has no code-level tripwire — this would give it one.

**Deferred to:** Phase E spec authoring. Do not start until Phase D ships.

---

### R-5.2 — Two-Layer Daily Memory (diary + operational journal)

**Problem identified by conversion assessment:** current memory is summary-shaped. It tracks what changed. It does not capture how each woman privately metabolized what changed. "They were thinking about you while you were gone" is aspirational, not runtime.

**Proposed shape per woman:**
- **Layer A — diary:** what mattered emotionally, what shifted with Whyze, what was carried from the household, what was not said aloud, bodily state. First-person, hand-authored or model-authored with hand-review.
- **Layer B — operational journal:** work completed, legal/shop/diplomatic actions, household changes, open loops, promises, next actions. Third-person or shorthand.

Plus shared artifacts:
- shared milestones ledger
- shared open-loops file

**Storage suggestion:** Markdown per day per woman under `memory/diaries/<name>/YYYY-MM-DD.md` and `memory/journals/<name>/YYYY-MM-DD.md`. Indexed in the existing pgvector memory service for retrieval. **Do not replace Markdown with summaries.** The Markdown IS the memory; embeddings are retrieval handles.

**Why this matters:** this is the single most interesting gap either audit identifies. It is the bridge between canon and interiority. Without it, continuity stays operational and the women never develop the kind of private carryover that makes off-screen life feel real.

**Deferred to:** needs its own Vision pass before spec. Not a mechanical addition. Candidate for a Phase F or F' scope.

---

### R-5.3 — Source-to-Runtime Traceability Manifests

**Problem identified by conversion assessment:** runtime artifacts (soul essence blocks, soul cards, voice exemplars) currently have implicit lineage back to source markdowns. Future audits cannot cheaply verify "this runtime block still matches its source section."

**Proposed shape:** per-character YAML manifest mapping every runtime artifact to source Markdown sections (file + anchor).

```yaml
# src/starry_lyfe/canon/manifests/adelia.yaml
adelia:
  soul_essence_blocks:
    identity:
      source:
        - Characters/Adelia/Adelia_Raye_v7.1.md#core-identity
        - Characters/Adelia/Adelia_Raye_v7.1.md#what-this-is-not
    pair:
      source:
        - Characters/Adelia/Adelia_Raye_Entangled_Pair.md#part-ii
        - Characters/Adelia/Adelia_Raye_Entangled_Pair.md#part-v
  pair_card:
    source:
      - Characters/Adelia/Adelia_Raye_Entangled_Pair.md#part-xiii
      - Characters/Adelia/Adelia_Raye_Entangled_Pair.md#part-xiv
  voice_exemplars:
    - Characters/Adelia/Adelia_Raye_Voice.md#example-1
    - Characters/Adelia/Adelia_Raye_Voice.md#example-4
```

**Why this matters:** turns drift audits from manual reads into mechanical checks. Every future phase spec can reference manifests to prove its preserved substrate still traces back to source.

**Deferred to:** polish item, can land alongside R-5.1 or R-5.2.

---

## 6. Explicitly Rejected Recommendations

Three recommendations from the conversion assessment conflict with canonical architecture decisions and are **not** adopted. Logged here so the decisions are visible.

### REJECT — Moving `soul_essence.py` prose into Markdown fragments

**Conversion assessment position:** the 45 hand-authored blocks in `soul_essence.py` are a maintainability risk because "prose in Python" is an anti-pattern. Recommends extracting to `canon/soul_blocks/*.md`.

**Rejection rationale:**
1. Violates canon rule: *"Soul-bearing prose is hand-authored. No LLM auto-distillation of canonical content."* The Python registry is the deliberate home of hand-authored prose, not an auto-distilled cache.
2. The Python form is a conscious atomicity tradeoff. Type-checked at import, one-shot loaded, test-integrated. Moving to Markdown trades atomicity for editability — not obviously a win.
3. Extraction would regress Phases A, B, and C, all of which shipped with the Python registry as load-bearing architecture.
4. The real risk the conversion assessment points at (drift between source Markdown and `soul_essence.py`) is better solved by R-5.3 (traceability manifests), which keeps the Python form and adds verification instead of relocating the content.

**Revisit conditions:** if traceability manifests prove insufficient and drift between source and registry becomes chronic, reopen this decision with evidence.

---

### REJECT — Treating soul essence + soul card redundancy as drift

**Conversion assessment position:** pair labels appearing in both soul essence blocks and soul cards is duplication that should be deduplicated.

**Rejection rationale:**
Directly contradicts canon rule: *"Soul redundancy: pair labels live in soul essence AND soul cards by design. Never deduplicate."* This is load-bearing redundancy. Soul essence ships unconditionally; soul cards activate by scene profile. A pair label present in both survives the failure of either layer.

**Not negotiable.**

---

### REJECT — 4-phase migration plan in conversion assessment §Practical migration strategy

**Conversion assessment position:** proposes a parallel 4-phase plan (stabilize authority → strengthen pair runtime → deepen continuity → deepen inter-woman life).

**Rejection rationale:**
1. Ignores Foundry Phase D currently in execution.
2. Parallel-universe phase numbering creates confusion with the CHANGELOG phase scheme AND the Foundry phase letters. We already have two numbering systems; a third would be actively harmful.
3. Cherry-picked the strong ideas (R-5.1, R-5.2, R-5.3). The plan structure itself offers no additional value.

**Replacement:** continue IMPLEMENTATION_PLAN_v7.1. Fold R-5.1/R-5.2/R-5.3 into the appropriate upcoming phase.

---

### REJECT — Folder reshape (`Characters/Adelia/kernel.md` flattened names)

**Conversion assessment position:** rename `*_v7.1.md` to `kernel.md`, pair files to `pair_<name>.md`, etc.

**Rejection rationale:** cosmetic churn. Breaks every path constant in `kernel_loader.py` and every existing reference in phase specs, CLAUDE.md, and the transcript archive. Zero runtime benefit. The `_v7.1.md` suffix is a version anchor, not a flaw.

---

## 7. Execution Plan

**Tier 1 commit (R-1.1 → R-1.3):** single commit, small. Claude Code executes via standard 4-agent cycle (plan → execute → Codex audit → Claude AI QA → ship). Expected test baseline: 127 pass + new tests for each R-1.x. Target: 130+ pass, 0 failed.

**Tier 2 commit (R-2.1 → R-2.5):** single commit after Tier 1 ships. Same cycle.

**Tier 3 commit (R-3.1 → R-3.2):** larger refactor, its own commit. Gate: must precede any fifth-character work. No current pressure but do not defer indefinitely.

**Tier 4 (polish, R-M1 → R-L2):** bundled polish commit, whenever convenient. Non-blocking.

**Folds (R-5.1 → R-5.3):** not in this remediation. Fold into Phase E/F spec authoring when their time comes.

---

## 8. QA Checklist for This Remediation (Step 5 gates)

When Claude Code returns each tier for QA, Claude AI verifies:

**Tier 1:**
- [ ] `format_soul_essence` raises on missing character
- [ ] `SoulEssenceNotFoundError` defined and exported
- [ ] Assembler callsite handles the raise cleanly (documented choice: propagate or defensive catch)
- [ ] Kernel cache key includes profile name
- [ ] Regression test proves profile-keyed cache separation
- [ ] `load_all_canon(validate_on_load=True)` is the default
- [ ] `CanonValidationError` carries human-readable error list
- [ ] Test suite: 127 baseline preserved, new tests green
- [ ] All 4 character samples regenerate cleanly at `Docs/_phases/_samples/`
- [ ] Terminal anchoring: all samples end at `</WHYZE_BYTE_CONSTRAINTS>`
- [ ] Vision invariants V1–V10 spot-checked: no regression

**Tier 2:**
- [ ] Pair loader raises with complete missing-entry list
- [ ] Decay config fails loud on incomplete record
- [ ] Soul card activation is a Pydantic model; all existing cards load
- [ ] Post-assembly budget reconciliation fires warning on overrun, silent on normal
- [ ] Seed script prints traceback on failure
- [ ] Test suite green

**Tier 3:**
- [ ] `CharacterID` enum defined in `canon/schemas/enums.py`
- [ ] All 6 character-keyed dicts assert complete coverage at import
- [ ] `test_character_id_coverage` added
- [ ] Test suite green
- [ ] Removing any one character from any one dict produces import-time failure (verify manually or in test)

---

## 9. Resolved Decisions (Project Owner, 2026-04-13)

All previously-open questions resolved. Vision-first: take time for quality, skip no steps.

### D-1 — Assembler callsite: **strict propagation**

`format_soul_essence` raises `SoulEssenceNotFoundError`; the assembler does not catch it; every call site is audited and updated to propagate or handle explicitly. See R-1.1 above for full specification. No diagnostic wrapper is added in Tier 1 — Tier 1's job is making the raise impossible to silence, and any wrapper would become the first attenuation point.

### D-2 — Codex review of Phase 2 audit: **not required**

Project Owner override. Tier 1 proceeds on Claude Code self-audit + Claude AI remediation spec. Normal cycle discipline resumes at Tier 1 execution (Claude Code plans → executes → Codex audits the execution → Claude AI QAs → Project Owner ships).

### D-3 — Conversion assessment provenance: **ChatGPT Pro, advisory only**

Authored by ChatGPT Pro. Outside the 4-agent Foundry cycle. Weight for future reviews: advisory. Good ideas get folded through Claude AI QA against canon rules; bad ideas get rejected with citations. Same treatment as this round. Future external reviews should be dated, signed, and acknowledged as external when folded in.

### D-4 — Traceability manifests (R-5.3): **independent phase item**

Not bundled with positive fidelity tests (R-5.1). Each gets its own full spec, plan, execution, audit, and QA. Bundling for convenience would design both shallower. Slot into the IMPLEMENTATION_PLAN_v7.1 phase queue as a standalone item when its time comes.

### D-5 — Diary/journal memory (R-5.2): **requires Vision addendum before spec**

This is interior architecture, not mechanical. Before any Python gets written, a new Vision document — `Vision/Interior_Memory_Architecture_v7.1.md` — must be authored and approved. That addendum must answer, at minimum:

- Does each woman's diary voice differ from her conversational voice? If yes, how?
- Authorship model: hand-authored, model-authored with hand-review, or model-authored live?
- Integration with the existing 7-tier memory schema — diary as a new tier, or as a cross-cutting substrate?
- Whyze access: strictly private, selectively private, or fully legible to Whyze?
- Anti-summary-drift discipline: what prevents diaries from collapsing back into summary-shape under scale?
- Voice differentiation guarantee: when the same model drafts all four diaries, what keeps Adelia's interior voice from leaking into Bina's?
- Temporal discipline: Alicia's away days vs Bina's home days have different textures — how is that encoded?
- Retrieval semantics: diaries indexed in pgvector? If yes, what are the retrieval queries and who issues them?

Claude AI authors this Vision addendum as a separate deliverable when Project Owner is ready. Until then, R-5.2 remains deferred.

---

**End of remediation spec.**
