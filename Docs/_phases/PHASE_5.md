# Phase 5: Scene Director

**Date opened:** 2026-04-14
**Depends on:** Phase F (Scene-Aware Section Retrieval, SHIPPED 2026-04-13), Phase A'' (Communication-Mode-Aware Pruning, SHIPPED 2026-04-13), Phase F-Fidelity (Positive Fidelity Harness, SHIPPED 2026-04-14)
**Replaces:** n/a — first implementation of `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8 (Scene Director)
**Status:** SHIPPED 2026-04-14 (R1 2026-04-14 closes Codex Round 1 F1/F2/F3; R2 2026-04-14 closes Codex Round 2 R2-F1/R2-F2)
**Last touched:** 2026-04-14 by Claude Code (remediation-2)

---

## 1. Context

Every `assemble_context()` call until Phase 5 required the caller to
manually construct a `SceneState`. Tests and scripts did this inline;
there was no automatic front door. Phase 5 lands the **Scene Director**:
the pre-assembly module that turns caller inputs into a `SceneState`
ready for `assemble_context()` to consume, and scores which woman
speaks next in multi-character Crew Conversations.

Per `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8, the Scene Director has two
responsibilities:

1. **Scene classification** — take caller inputs (user message, present
   characters, residence flag, optional hints) and produce a
   fully-populated `SceneState`. Uses the Phase F `SceneType` /
   `SceneModifiers` / `CommunicationMode` infrastructure.
2. **Next-speaker selection** — score present women per the
   Talk-to-Each-Other Mandate (Vision §6, §7) and Rule of One, using
   dyad state (memory tier 4, `dyad_state_internal` table) as a
   fitness input.

Per Project Owner decision this phase:
- Scope: classifier + full next-speaker scoring (not stubbed).
- Classifier approach: rule-based heuristics, no LLM call.
- Integration: new `src/starry_lyfe/scene/` package with callable API.

---

## 2. Public API

```python
# src/starry_lyfe/scene/

@dataclass(frozen=True)
class SceneDirectorHints:
    forced_scene_type: SceneType | None = None
    forced_modifiers: SceneModifiers | None = None
    scene_description: str | None = None
    communication_mode: CommunicationMode | None = None

@dataclass(frozen=True)
class SceneDirectorInput:
    user_message: str
    present_characters: list[str]
    alicia_home: bool = True
    hints: SceneDirectorHints = field(default_factory=SceneDirectorHints)

def classify_scene(director_input: SceneDirectorInput) -> SceneState: ...


@dataclass(frozen=True)
class TurnEntry:
    speaker: str         # character name or "whyze"
    addressed_to: str
    turn_index: int

@dataclass(frozen=True)
class NextSpeakerInput:
    scene_state: SceneState
    turn_history: list[TurnEntry]
    dyad_state_provider: DyadStateProvider
    in_turn_already_spoken: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class NextSpeakerDecision:
    speaker: str
    scores: dict[str, float]
    reasons: list[str]

def select_next_speaker(speaker_input: NextSpeakerInput) -> NextSpeakerDecision: ...


class DyadStateProvider(Protocol):
    def get(self, char_a: str, char_b: str) -> DyadStateInternal | None: ...

class DictDyadStateProvider:  # concrete dict-backed impl
    ...

def build_dyad_state_provider(rows: list[DyadStateInternal]) -> DictDyadStateProvider:
    """Wrap a list from ``_retrieve_internal_dyads`` into a sync provider."""
```

Hints ALWAYS win over rule-based inference. This is the escape hatch for
the HTTP endpoint (Phase 7) when the UI already knows the scene type,
and for tests that need to exercise a specific branch.

---

## 3. Classifier rules

### 3.1 CommunicationMode

Order: `hints.communication_mode` → message keywords (`"phone call"`,
`"letter"`, `"video call"`) → default `IN_PERSON`.

### 3.2 Alicia residence gate

If `"alicia" ∈ present_characters AND NOT alicia_home AND comm_mode == IN_PERSON`,
raise `AliciaAwayContradictionError` with a message naming the three
fixes (remove alicia, set alicia_home, or set a remote comm mode). This
fires BEFORE scene-type inference — an unsatisfiable scene should never
produce a prompt.

The assembler has its own defense-in-depth check (`AliciaAwayError`)
that fires if an invalid `SceneState` reaches it by some other path.

### 3.3 SceneType (hint → keyword → presence-count → DOMESTIC)

1. `hints.forced_scene_type` wins verbatim.
2. Keyword chain, first match wins:
   - `CONFLICT` — fight, argument, pushback, shutdown, conflict, snapped at
   - `REPAIR` — apology, apologize, make up, re-approach, repair, i was wrong
   - `INTIMATE` — in bed, sex, undress, kissing, intimate, naked
   - `TRANSITION` — in transit, driving, on the road, travel, in the car
   - `PUBLIC` — work, colleagues, office, courthouse, public, restaurant
3. Presence-count fallback:
   - `len(women_present) >= 3` → `GROUP`
   - `len(women_present) == 1` → `SOLO_PAIR`
4. Default → `DOMESTIC`.

### 3.4 SceneModifiers

If `hints.forced_modifiers` is set, it wholly replaces inference
(never merged — caller is explicit). Otherwise each of the 7 flags has
its own keyword scan. Patterns mirror the Layer 7 constraint triggers
in `src/starry_lyfe/context/constraints.py:122-199`.

`explicitly_invoked_absent_dyad` specifically scans for named-absent-pair
mentions (`"missing reina"`, `"thinking about bina"`, etc.) and returns
a `frozenset[str]` of names. These feed directly into
`SceneState.recalled_dyads`.

### 3.5 scene_description

`hints.scene_description` if set else `user_message` truncated to 200
chars. The truncation keeps Layer 6 sensory grounding clean without
dumping the full message body into the scene description field.

### 3.6 public_scene flag

Mirrors `SceneType.PUBLIC` OR `modifiers.work_colleagues_present`. Both
paths trigger the Layer 7 public-scene pillar in `constraints.py:122`,
so either must set the flag.

---

## 4. Next-speaker scoring

Per candidate in `scene_state.present_characters` (excluding `"whyze"`):

1. **Residence zero-out** — if `candidate == "alicia"` AND
   `not scene_state.alicia_home` AND `comm_mode == IN_PERSON` → 0.0.
2. **Rule of One** — if `candidate in in_turn_already_spoken` → 0.0.
3. **Talk-to-Each-Other** — if last 2 turns both addressed Whyze:
   reward candidates who could break the chain (+0.25) OR penalize when
   no other woman is present (-0.10).
4. **Woman-to-woman continuation** — if last turn was w2w: reward (+0.15).
5. **Dyad-state fitness** — for each other present woman:
   score += `dyad.intimacy * 0.10 + dyad.unresolved_tension * 0.05`.
6. **Recency suppression** — if candidate just spoke non-whyze: -0.05.

Base score: 0.50. Composite weights are module-level `# TUNABLE:`
constants in `next_speaker.py`. Unit tests assert RELATIVE score
differentials so minor tuning does not churn the suite.

Ties broken by stable canonical order (`adelia → bina → reina → alicia`)
matching `canon/schemas/enums.py:CharacterID`. If all candidates zero
out, raise `NoValidSpeakerError` with the full reasons trace for debug.

**Caller contract for Rule of One:** the caller (future HTTP endpoint,
Crew response orchestration) must track which candidates have already
spoken in the current turn bundle and pass them via
`in_turn_already_spoken`. The scoring function itself is stateless.

---

## 5. Work items

| WI | Description | Status |
|----|-------------|--------|
| 1 | `src/starry_lyfe/scene/` package with 6 files | SHIPPED |
| 2 | Input/output dataclasses + `DyadStateProvider` Protocol | SHIPPED |
| 3 | `AliciaAwayContradictionError`, `NoValidSpeakerError` | SHIPPED |
| 4 | `classify_scene()` full pipeline | SHIPPED |
| 5 | `select_next_speaker()` with all 6 rules | SHIPPED |
| 6 | Keyword constant tables | SHIPPED |
| 7 | `build_dyad_state_provider()` adapter for db/retrieval.py output | SHIPPED |
| 8 | Unit tests (64) | SHIPPED |
| 9 | Integration test (6 cases) | SHIPPED |
| 10 | Fidelity regression | PASSING (37/37) |
| 11 | This phase doc | SHIPPED |
| 12 | OPERATOR_GUIDE Scene Director section | SHIPPED |
| 13 | CHANGELOG entry | SHIPPED |
| 14 | CLAUDE.md §19 shipped list | SHIPPED |

---

## 6. Acceptance criteria

| AC | Description | Status |
|----|-------------|--------|
| AC-5.1 | `classify_scene()` deterministic (property test) | PASS |
| AC-5.2 | Every `SceneType` value reachable from some input (8 total) | PASS |
| AC-5.3 | Every `SceneModifiers` flag (7 total) independently settable | PASS |
| AC-5.4 | Alicia-away + present + IN_PERSON raises `AliciaAwayContradictionError` | PASS |
| AC-5.5 | `hints.*` overrides rule-based inference | PASS |
| AC-5.6 | Classifier-produced SceneState → assembler yields byte-identical prompt to hand-constructed equivalent | PASS |
| AC-5.7 | `select_next_speaker` penalizes 2-turn Whyze chain (≥ 0.20 differential) | PASS |
| AC-5.8 | `select_next_speaker` rewards w2w continuation | PASS |
| AC-5.9 | Alicia scores 0.0 when away + IN_PERSON | PASS |
| AC-5.10 | Rule of One: `in_turn_already_spoken` candidate scores 0.0 | PASS |
| AC-5.11 | Dyad-state fitness wired via injected provider | PASS |
| AC-5.12 | All 651 pre-phase tests still pass; ≥ 60 new tests | PASS (737 total) |
| AC-5.13 | ruff clean, mypy `--strict` clean | PASS |
| AC-5.14 | Fidelity rubric regression: 37/37 pass | PASS |
| AC-5.15 | CHANGELOG `[Unreleased]` records landing | PASS |

---

## 7. Deferred to future phases

- **LLM-classifier fallback** (Phase 5.2) — hybrid approach where the
  rule-based classifier handles the obvious cases and an LLM call
  disambiguates edge cases. Current scope kept to rule-based per PO
  directive; escape hatch is `hints.*` overrides.
- **Real async DyadStateProvider** (Phase 7) — the current provider is
  synchronous by design so the scoring function stays pure. Phase 7
  HTTP endpoint will `await _retrieve_internal_dyads()` then wrap via
  `build_dyad_state_provider()` before calling `select_next_speaker()`.
- **Turn history persistence** (Phase 7) — `TurnEntry` records are
  caller-managed for now. Phase 7 will source them from session state.
- **Learned scoring weights** (future) — current weights are authored.
  A future phase could tune them from Whyze-Byte output and subjective
  success proxies.

---

## 8. Known limitations

- **Rule-based classifier has blind spots.** A scene that mixes
  conflict keywords with intimate keywords picks the first match in
  the keyword chain (CONFLICT wins). Callers with ambiguous input
  should pass `hints.forced_scene_type` rather than trusting inference.
- **Dyad-state fitness requires pre-fetched data.** The caller must
  load the relevant dyad rows before calling `select_next_speaker`.
  Missing rows produce `None` and contribute 0.0 to the composite —
  no error, no fallback heuristic.
- **Rule of One is caller-enforced.** The scoring function is stateless
  across turn bundles. The caller must thread `in_turn_already_spoken`
  correctly when orchestrating a multi-speaker response.

---

## 9. Operational notes

**Run scene unit tests:** `pytest tests/unit/scene -v`
**Run integration:** `pytest tests/integration/test_scene_director_to_assembler.py -v`
**Regenerate Phase F samples with classifier in the loop:** edit
`scripts/generate_phase_*_samples.py` to call `classify_scene()` before
`assemble_context()`. Diff against existing samples for zero drift.

**Debug a classification:** inspect returned `SceneState` fields and
compare to the keyword tables in `classifier.py`. Every inference branch
is traceable to a module-level constant tuple.

**Debug a next-speaker decision:** read `decision.reasons` — every rule
that fires logs a one-line trace showing candidate, sign, weight, and
cause. Dump the list and read top-to-bottom.

---

## 10. Closing Block (locked)

**Phase identifier:** 5
**Final status:** SHIPPED 2026-04-14
**Total cycle rounds:** 1 (no Codex audit cycle; direct ship under Project Owner direct-remediation authority — PO-approved plan at `C:\Users\Whyze\.claude\plans\fizzy-napping-whisper.md`)
**Total commits:** 1 (feat(phase_5): Scene Director — classifier + next-speaker scoring)
**Total tests added:** 86 (64 unit + 6 integration + 16 minor coverage improvements absorbed into the count; 651 pre-phase → 737 post-phase)
**Date opened:** 2026-04-14
**Date closed:** 2026-04-14

**Lessons for the next phase:** Keeping the scoring function
synchronous and DB-free via the injected `DyadStateProvider` Protocol
pattern paid off immediately — unit tests stub with deterministic
values, fidelity regression runs in microseconds, and the production
HTTP endpoint (Phase 7) has a clean seam to wrap the async retrieval.
The rule-based classifier shipped in a single commit because we
treated hints as a first-class escape hatch rather than a last resort
— that's the pattern to reuse when a future phase needs a
deterministic front door over fuzzy inference.

**Cross-references:**
- Spec source: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8
- Phase F scene infrastructure: `src/starry_lyfe/context/types.py:18-109`
- Phase F section promotion: `src/starry_lyfe/context/kernel_loader.py:80-92`
- Dyad-state memory tier 4: `src/starry_lyfe/db/models/dyad_state_internal.py`, `src/starry_lyfe/db/retrieval.py:88-98`
- Vision V6 Cognitive Hand-Off Integrity: also covered positively by Phase F-Fidelity rubrics (`Docs/_phases/PHASE_F_FIDELITY.md`)

---

## 11. Codex Audit â€” Round 1 (post-ship)

**Date:** 2026-04-14  
**Auditor:** Codex  
**Scope reviewed:** `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8, this phase record, `src/starry_lyfe/scene/{classifier,next_speaker,turn_history,errors,__init__}.py`, `src/starry_lyfe/context/{assembler,layers,types}.py`, `tests/unit/scene/*`, `tests/integration/test_scene_director_to_assembler.py`, and `Docs/OPERATOR_GUIDE.md`.

### Verification context

- `pytest tests/unit/scene tests/integration/test_scene_director_to_assembler.py -q` -> `70 passed`
- `pytest -q` with hard DB mode -> `737 passed`
- `ruff check src tests` -> passed
- `python -m mypy src` -> passed

### Executive assessment

The Phase 5 surface is real and the package is broadly well-structured, but the shipped implementation is not fully spec-safe. Two red-team probes found concrete live-path defects that the current suite misses: absent-dyad inference does not survive the classifier -> assembler path, and the public `present_characters` contract disagrees with downstream runtime semantics in a way that can mis-route Layer 5 for two-woman domestic scenes. There is also one lower-severity architecture drift: the scorer does not consume current activity context despite §8 still naming it as a fitness input.

### Findings

| ID | Severity | Finding | Evidence | Recommended remediation |
|----|----------|---------|----------|--------------------------|
| F1 | High | Scene Director absent-dyad inference is broken on the live classifier -> assembler path. | `classifier.py:229-238` returns bare names like `reina`; `classifier.py:173` copies them into `SceneState.recalled_dyads`; `layers.py:533-540` only honors dyad keys like `adelia-reina` / `reina-adelia`. Live probe: `classify_scene(SceneDirectorInput(user_message='adelia and i are in the kitchen, thinking about reina', present_characters=['adelia', 'whyze']))` produced `recalled_dyads={'reina'}`, but `assemble_context()` with a stubbed `adelia-reina` internal dyad rendered no dyad prose in Layer 6. Current tests stop at the classifier surface (`tests/unit/scene/test_classifier.py:322`, `tests/unit/scene/test_director.py:70`) and never verify classifier-inferred absent dyads reach Layer 6. | Normalize inferred absent-dyad output to the dyad-key shape that `format_scene_blocks()` actually consumes, or update Layer 6 to accept name-level recalls. Add an integration regression that asserts classifier-inferred absent dyads render the intended internal dyad prose end-to-end. |
| F2 | Medium | The public `present_characters` contract is inconsistent with downstream runtime semantics, and the mismatch can mis-route Layer 5 voice selection. | The public API docstring says `"whyze" is implicit and should NOT appear in this list` at `classifier.py:100-102`, and the operator guide example follows that contract at `Docs/OPERATOR_GUIDE.md:431-437`. But domestic-context mode accumulation still keys off raw `len(scene.present_characters)` at `layers.py:75-84`. Live probe: `classify_scene(SceneDirectorInput(user_message='adelia and bina are in the kitchen making dinner', present_characters=['adelia', 'bina']))` yields active modes `['domestic', 'solo_pair']`, while the same scene with `['adelia', 'bina', 'whyze']` yields `['domestic', 'group']`. The current integration tests only cover 1-woman+Whyze classifier cases (`tests/integration/test_scene_director_to_assembler.py:53`, `:75`, `:117`, `:141`, `:170`) and never exercise the documented "Whyze implicit" path against Layer 5 behavior. | Make the contract explicit and consistent: either require Whyze in `present_characters` everywhere, or normalize the classifier output so downstream code sees the same shape regardless of caller convention. Add a regression proving the public API example produces the intended Layer 5 mode path for two-woman domestic scenes. |
| F3 | Low | Phase 5 still does not implement the full §8 scoring inputs described in the master plan. | `IMPLEMENTATION_PLAN_v7.1.md:998-1016` says next-speaker selection draws on dyad state, current activity context, and recent turn history. But `NextSpeakerInput` in `next_speaker.py:67-81` carries no activity-context input beyond `scene_state`, and the scoring loop at `next_speaker.py:115-217` never consults `scene_state.scene_description` or `scene_state.scene_type`. The phase file narrowed the implementation narrative to dyad state + turn history at `Docs/_phases/PHASE_5.md:27-30`, but that narrowing is not reflected back into the canonical spec. | Either add an explicit activity-context input to the scorer, or record the reduction as an approved deviation in the canonical spec/phase record so future implementers are not misled about what Phase 5 actually shipped. |

### Runtime probe summary

1. **Absent dyad probe:** classifier inferred `recalled_dyads={'reina'}` from `thinking about reina`, but the assembled Layer 6 block still rendered only `Current activity: ...` and omitted the stubbed `adelia-reina` dyad prose.
2. **Whyze-implicit probe:** the documented public API example shape (`present_characters=['adelia', 'bina']`) yields `['domestic', 'solo_pair']`; the runtime-internal shape used elsewhere (`['adelia', 'bina', 'whyze']`) yields `['domestic', 'group']` for the same domestic scene.
3. **Verification integrity:** all scene tests, full `pytest`, `ruff`, and `mypy` still pass, which confirms the two defects are currently outside the checked-in regression surface rather than caught-and-waived behavior.

### Verified resolved

- The Scene Director package exists and exports the promised public surface.
- Alicia-away contradiction handling is real and fires before prompt assembly.
- Rule of One zero-out, Whyze-chain handling, recency suppression, and dyad-provider injection are all implemented and covered by the checked-in suite.
- The broader repo remains green under full-suite verification (`737 passed`).

### Recommended remediation order

1. Fix absent-dyad normalization end-to-end (F1).
2. Normalize the `present_characters` contract and add the missing Layer 5 regression (F2).
3. Decide whether current activity context is a real scoring requirement or a stale architectural promise, then update code or canon accordingly (F3).

### Gate recommendation

**FAIL.** Phase 5 should not remain treated as fully clean while F1 and F2 are open. The implementation is close, but the current suite passes without exercising two important front-door contracts.

---

## 12. Round 1 Remediation (2026-04-14)

**Author:** Claude Code under Project Owner direct-remediation authority
**Plan:** `C:\Users\Whyze\.claude\plans\fizzy-napping-whisper.md` (approved 2026-04-14)
**Commit:** `fix(phase_5): Round 1 remediation — close F1/F2/F3 from Codex audit`

### Fixes landed

**F1 — Absent-dyad normalization (HIGH)**

- `src/starry_lyfe/scene/classifier.py` gains `_to_dyad_keys()` helper.
- The modifier field `explicitly_invoked_absent_dyad` keeps bare names (semantic "who was invoked").
- The runtime-facing `SceneState.recalled_dyads` is now populated with dyad-key shape (`"<W>-<N>"` for every present woman `W` not equal to `N`). Layer 6's string-equality check in `format_scene_blocks()` at `layers.py:535-541` now matches classifier-inferred recalls.
- Integration regression added at `tests/integration/test_scene_director_to_assembler.py::test_f1_classifier_absent_dyad_renders_in_layer_6` — stubs an `adelia-reina` internal-dyad row, classifies `"thinking about reina"`, asserts the assembled prompt contains `"adelia-reina"` (the internal-dyad prose marker).

**F2 — `present_characters` contract (MEDIUM)**

- `classify_scene()` now auto-appends `"whyze"` to `present_characters` when the caller omits it.
- `SceneDirectorInput` docstring updated to reflect the Whyze-included runtime convention (every pre-Phase-5 `assemble_context` test passes Whyze explicitly — the classifier's original "whyze implicit" claim was aspirational and wrong).
- Caller may still pass Whyze explicitly; not double-appended.
- Integration regression added at `tests/integration/test_scene_director_to_assembler.py::test_f2_two_woman_domestic_routes_as_group` — classifies the documented public-API example (`["adelia", "bina"]`) and asserts Layer 5 mode accumulation emits `GROUP`, not `SOLO_PAIR`.

**F3 — Current activity context (LOW)**

- `NextSpeakerInput` gains `activity_context: str | None = None`.
- `select_next_speaker()` adds Rule (7) narrative salience: `+0.05` when the candidate's name appears in `scene_state.scene_description` OR `speaker_input.activity_context`.
- Three unit tests added at `tests/unit/scene/test_next_speaker.py::TestActivityContext`.
- `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8 updated with a Phase 5 implementation note confirming all three §8 scoring inputs (dyad state, turn history, activity context) now ship.

### Verification

- `pytest tests/unit tests/integration tests/fidelity -q` → **746 passed** (+9 new vs 737 pre-remediation baseline).
- `ruff check src tests` → clean.
- `mypy --strict src` → clean.
- Round 1 live probes re-run: both F1 and F2 paths now produce the expected downstream behavior.

### Updated acceptance criteria

| AC | Description | Status |
|----|-------------|--------|
| AC-R1.1 | `classify_scene()` absent-dyad output is dyad-key shape | PASS |
| AC-R1.2 | End-to-end Layer 6 renders internal-dyad prose for classifier-inferred recalls | PASS |
| AC-R1.3 | `classify_scene()` auto-appends `"whyze"`; preserves when supplied | PASS |
| AC-R1.4 | Documented public API example routes as GROUP, not SOLO_PAIR | PASS |
| AC-R1.5 | `NextSpeakerInput.activity_context: str \| None = None` field exists | PASS |
| AC-R1.6 | Rule (7) +0.05 boost when candidate named in scene_description or activity_context | PASS |
| AC-R1.7 | 737 pre-remediation tests still pass; ≥ 8 new | PASS (746 total) |
| AC-R1.8 | ruff + mypy --strict clean | PASS |
| AC-R1.9 | Existing `test_absent_dyad_detected` expects dyad-key shape | PASS |
| AC-R1.10 | This phase file records Round 1 remediation + updated closing block | PASS |
| AC-R1.11 | `OPERATOR_GUIDE.md` §7.6 example reflects corrected contract | PASS |
| AC-R1.12 | `IMPLEMENTATION_PLAN_v7.1.md` §8 records Phase 5 implementation note | PASS |
| AC-R1.13 | `CHANGELOG.md` records Round 1 remediation | PASS |

### Updated closing block

**Final status:** SHIPPED 2026-04-14 (feat commit `fc9b3ed` + remediation-1 commit)
**Total cycle rounds:** 2 (1 ship + 1 Codex audit + remediation)
**Total commits:** 2 (fc9b3ed + Round 1 remediation)
**Total tests added:** 95 (86 original + 9 Round 1 regressions)
**Date opened:** 2026-04-14
**Date closed:** 2026-04-14

**Lessons for the next phase:** Codex red-team live probes caught two defects (F1, F2) that the original test suite missed because the suite did not exercise the full classifier-to-assembler path. Next phase should include at least one end-to-end regression per documented public-API contract, not just a unit test per rule. The classifier-as-normalizer pattern (F1 dyad-key shape, F2 whyze-append) is the right architecture: keep downstream consumers strict about shape, let the front-door layer absorb caller-shape variance.

---

## 13. Round 2 Audit (2026-04-14)

**Author:** Codex
**Scope:** Re-audit of Round 1 remediation for F1/F2/F3 across `src/starry_lyfe/scene/classifier.py`, `src/starry_lyfe/scene/next_speaker.py`, `tests/unit/scene/`, `tests/integration/test_scene_director_to_assembler.py`, `Docs/OPERATOR_GUIDE.md`, and `Docs/IMPLEMENTATION_PLAN_v7.1.md`.

### Verification context

- `pytest tests/unit/scene tests/integration/test_scene_director_to_assembler.py -q` -> **79 passed**
- `pytest -q` with `STARRY_LYFE__TEST__REQUIRE_POSTGRES=1` -> **746 passed**
- `ruff check src tests` -> clean
- `python -m mypy src` -> clean

### Executive assessment

The Round 1 remediation is real and it closes the three original audit findings. The absent-dyad path now reaches Layer 6 end-to-end, the `present_characters` contract is normalized at the classifier boundary, and next-speaker scoring now consumes activity context. Two smaller issues remain: the canonical master plan still contradicts the shipped Phase 5 state in several status/index sections, and the absent-dyad detector can still falsely mark a present woman as "absent" when her name appears in an absent-dyad phrase.

### Findings

| ID | Severity | Finding | Evidence | Recommended remediation |
|----|----------|---------|----------|-------------------------|
| R2-F1 | Medium | The canonical master plan still contradicts the shipped Phase 5 state. | `Docs/IMPLEMENTATION_PLAN_v7.1.md:36`, `:74`, `:1450`, and `:1537` still mark Scene Director / Phase 5 as planned or not implemented, even though `Docs/_phases/PHASE_5.md` is shipped and `Docs/IMPLEMENTATION_PLAN_v7.1.md:1017` now carries a shipped implementation note. Because `AGENTS.md` treats the master plan as canonical, this is still control-plane drift. | Update the master-plan status tables and scope notes so every Phase 5 status surface agrees that Scene Director is shipped. |
| R2-F2 | Low | `_detect_absent_dyads()` can falsely classify a present woman as absent. | Live probe: `classify_scene(SceneDirectorInput(user_message='thinking about adelia while adelia and bina are in the kitchen', present_characters=['adelia', 'bina']))` returned `explicitly_invoked_absent_dyad={'adelia'}` and `recalled_dyads={'bina-adelia'}` even though Adelia is present. The detector at `src/starry_lyfe/scene/classifier.py:253-268` scans text for names but does not subtract `present_characters`. Current regression coverage in `tests/unit/scene/test_classifier.py:322-336` proves positive detection only; it does not assert that present women never appear in absent-dyad fields. | Filter `_detect_absent_dyads()` or the normalization step against the actually-present women, and add a regression that proves present women cannot appear in absent-dyad outputs. |

### Runtime probe summary

1. Original F1 live path is fixed: `classify_scene(... 'thinking about reina' ...)` now emits `recalled_dyads={'adelia-reina'}` for Adelia scenes, and the integration regression renders the internal-dyad prose in Layer 6.
2. Original F2 live path is fixed: the documented public API shape `present_characters=['adelia', 'bina']` now normalizes to `['adelia', 'bina', 'whyze']` and yields `['domestic', 'group']`, not `['domestic', 'solo_pair']`.
3. Original F3 contract is fixed: `NextSpeakerInput.activity_context` exists and the checked-in `test_next_speaker.py` coverage proves the salience boost fires from both `scene_description` and `activity_context`.
4. New probe: absent-dyad false positives are still possible when an "absent" name is also listed in `present_characters`.

### Drift against specification

- Round 1 remediation aligns the live code with the original three Codex findings.
- The remaining spec drift is documentation-level: the master plan still exports stale "Phase 5 planned" status in multiple canonical summary sections.

### Verified resolved

- F1 absent-dyad normalization is implemented in `classifier.py` and verified end-to-end by `tests/integration/test_scene_director_to_assembler.py`.
- F2 `present_characters` normalization is implemented at the classifier boundary and verified by unit + integration coverage.
- F3 activity-context scoring is implemented in `next_speaker.py` and covered by the new `TestActivityContext` unit tests.

### Recommended remediation order

1. Fix the master-plan Phase 5 status drift (R2-F1).
2. Tighten absent-dyad detection so present women cannot be mislabeled absent (R2-F2).

### Gate recommendation

**PASS WITH MINOR FIXES.** The original Phase 5 remediation is technically successful and the repo is green, but the canonical status surfaces still need cleanup and there is one remaining low-blast-radius classifier semantic bug.

---

## 14. Round 2 Remediation (2026-04-14)

**Author:** Claude Code under Project Owner direct-remediation authority
**Plan:** `C:\Users\Whyze\.claude\plans\fizzy-napping-whisper.md` (approved 2026-04-14, Round 2 revision)
**Commit:** `fix(phase_5): Round 2 remediation — close R2-F1/R2-F2 from Codex re-audit`

### Fixes landed

**R2-F1 — master-plan status sync (MEDIUM)**

Four canonical status surfaces in `Docs/IMPLEMENTATION_PLAN_v7.1.md` updated to reflect the shipped Phase 5 state:

- `:36` (status summary bullet list) — `Phase 5 (Scene Director) — PLANNED` → `COMPLETE. Shipped 2026-04-14 (Round 1 remediation 2026-04-14, Round 2 remediation 2026-04-14)` with pointer to runtime surface and `PHASE_5.md`.
- `:74` (Vision Alignment matrix) — `(Phase 5 planned; Phase F adds scene type infrastructure)` → `Phase 5 (complete)`.
- `:1450` (Architectural Layers table) — `PLANNED (Phase 5)` → `COMPLETE (Phase 5)` with updated note explaining the Scene Director consumes Phase F infrastructure.
- `:1537` (What This Plan Does Not Do) — the `"It does not implement the Scene Director (Phase 5)"` bullet dropped entirely. The "does not do" list is a live scope contract, not a historical log; Phase 5's shipping is already recorded in the status summary (§36) and in §8's implementation note (:1017).

Post-fix grep confirms zero remaining `Phase 5.*planned` occurrences in the master plan.

**R2-F2 — classifier false-positive on present women (LOW)**

`_detect_absent_dyads()` at `src/starry_lyfe/scene/classifier.py` now skips women whose names appear in `present_characters` before the keyword scan. Phrases like `"thinking about adelia"` while Adelia is in the room are narrative color, not a recall-absent-dyad trigger.

- Signature change: `_detect_absent_dyads(text: str, present_characters: list[str])`.
- `_classify_modifiers()` threads `present_characters` through; `classify_scene()` passes `director_input.present_characters`.
- Hint override path (`hints.forced_modifiers`) still wholly replaces inference, preserving R1 AC-5.5 (caller's explicit intent wins).

Two regression tests added at `tests/unit/scene/test_classifier.py::TestModifiersInference`:

- `test_present_woman_not_marked_absent_even_when_mentioned` — Codex's exact live probe. Post-fix: `explicitly_invoked_absent_dyad=frozenset()`, `recalled_dyads=set()`.
- `test_mixed_present_and_absent_only_absent_in_recall` — mixed scene (Adelia present but mentioned + Reina absent). Only Reina lands in the modifier/recalled sets.

### Verification

- `pytest tests/unit tests/integration tests/fidelity -q` → **748 passed** (+2 vs 746 Round 1 baseline).
- `ruff check src tests` → clean.
- `mypy --strict src` → clean.
- Live probe post-fix: `classify_scene(user_message="thinking about adelia while adelia and bina are in the kitchen", present_characters=["adelia", "bina"])` returns `explicitly_invoked_absent_dyad=frozenset()` as expected.
- Master-plan grep: no remaining `Phase 5.*planned` / `PLANNED` matches.

### Updated acceptance criteria

| AC | Description | Status |
|----|-------------|--------|
| AC-R2.1 | `_detect_absent_dyads(text, present_characters)` skips present women | PASS |
| AC-R2.2 | Codex live probe returns empty absent-dyad fields | PASS |
| AC-R2.3 | Mixed scene returns only truly-absent women | PASS |
| AC-R2.4 | `hints.forced_modifiers` still wholly overrides inference (R1 AC-5.5 preserved) | PASS |
| AC-R2.5 | All 4 master-plan lines updated; no remaining "Phase 5 planned" | PASS |
| AC-R2.6 | `PHASE_5.md` §14 Round 2 block records R2-F1 + R2-F2 fixes | PASS |
| AC-R2.7 | 746 pre-R2 tests still pass; 2 new regressions added (748 total) | PASS |
| AC-R2.8 | ruff + mypy --strict clean | PASS |
| AC-R2.9 | CHANGELOG + CLAUDE.md + memory index all reflect R2 landing | PASS |

### Updated closing block

**Final status:** SHIPPED 2026-04-14 (feat commit `fc9b3ed` + R1 commit `90c4d82` + R2 commit)
**Total cycle rounds:** 3 (1 ship + 2 Codex audits + 2 remediations)
**Total commits:** 3 (fc9b3ed + 90c4d82 + R2)
**Total tests added:** 97 (86 original + 9 R1 + 2 R2)
**Date opened:** 2026-04-14
**Date closed:** 2026-04-14

**Lessons for the next phase:** A passing gate ("PASS WITH MINOR FIXES") is not a skip signal — the master plan is canonical per AGENTS.md, and doc drift in canonical surfaces is control-plane noise that propagates. When landing a phase, sweep every status surface (summary bullets, vision matrix, architectural layers table, "does not do" scope contract) in a single pass. For rule-based detectors that scan user-supplied text, always subtract the narrow context (present_characters) from the wide pattern space before claiming detection — "does the phrase appear in text" is not equivalent to "is this claim true about the scene."
