# Phase 5: Scene Director

**Date opened:** 2026-04-14
**Depends on:** Phase F (Scene-Aware Section Retrieval, SHIPPED 2026-04-13), Phase A'' (Communication-Mode-Aware Pruning, SHIPPED 2026-04-13), Phase F-Fidelity (Positive Fidelity Harness, SHIPPED 2026-04-14)
**Replaces:** n/a — first implementation of `Docs/IMPLEMENTATION_PLAN_v7.1.md` §8 (Scene Director)
**Status:** SHIPPED 2026-04-14
**Last touched:** 2026-04-14 by Claude Code (ship)

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
