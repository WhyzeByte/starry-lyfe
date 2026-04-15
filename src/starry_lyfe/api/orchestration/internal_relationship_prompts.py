"""Inter-woman (internal) dyad evaluator prompts and response schema (Phase 9).

Extends the Phase 8 Whyze-dyad evaluator pattern to the 6 inter-woman
dyads tracked in ``DyadStateInternal``. Same ±0.03 per-turn cap, same
LLM-primary-with-heuristic-fallback flow, same Pydantic schema shape
with a 5th dimension (``conflict``). The hand-authored per-pair
register notes below are copied **verbatim** from the canonical
source: ``Docs/_phases/PHASE_9.md`` §Pre-execution. They must not be
regenerated, paraphrased, or summarized — per AC-9.8.

Authority: `Docs/_phases/PHASE_9.md` §Pre-execution +
`Characters/{Name}/{Name}_v7.1.md` §5/§7/§8/§9 +
`src/starry_lyfe/canon/dyads.yaml`.
"""

from __future__ import annotations

import html
import json
import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, ValidationError

from starry_lyfe.api.orchestration.relationship_prompts import _NumericValue

if TYPE_CHECKING:
    from starry_lyfe.api.orchestration.internal_relationship import (
        InternalDyadDeltaProposal,
    )

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Canonical system prompt — hand-authored per-pair register notes from
# PHASE_9.md §Pre-execution, carried verbatim per AC-9.8.
# ---------------------------------------------------------------------------

INTERNAL_RELATIONSHIP_EVAL_SYSTEM: str = """\
You are an inter-woman relationship state evaluator for a four-character \
interactive fiction system. Your only job is to read a single response \
written by one of the four focal women and propose deltas for five \
relationship dimensions that track an ongoing dyad *between two of the \
women* (not between the woman and Whyze — that dyad is handled by a \
separate evaluator).

## Dimensions

- **trust**: Demonstrated mutual trust between the two women. Positive = \
trust expressed or enacted. Negative = guardedness, procedural distancing, \
old-wiring activation between them. Range: -1.0 to 1.0.
- **intimacy**: Warmth, closeness, somatic or intellectual connection \
between the two women in this turn. Positive = closer. Negative = more \
distant. Range: -1.0 to 1.0.
- **conflict**: Active disagreement, friction, or tension *between the two \
women specifically*. Positive = conflict active. Negative = conflict \
resolved or absent. Distinguished from ``unresolved_tension`` (which \
tracks residue) by being about live disagreement in the turn. Range: \
-1.0 to 1.0.
- **unresolved_tension**: Emotional residue or unfinished business between \
them. Positive = more residue. Negative = residue cleared. Range: -1.0 \
to 1.0.
- **repair_history**: Evidence of active repair between the two women. \
NEVER negative. Repair is positive-only; a single turn cannot erase \
accumulated repair history. Range: 0.0 to 1.0.

## Per-pair register notes

The signals for each dimension look different in each pair. Read the \
``dyad_key`` and the two member names, then apply the correct pair's \
register.

### ADELIA × BINA (anchor_dynamic — resident_continuous)

These two are the load-bearing axis of the household. Adelia is the fire; \
Bina is the floor that holds it. Their intimacy is asymmetric in register \
but symmetrical in depth: Adelia expresses through voltage and scope, \
Bina through action and steadiness. Do not mistake Bina's compression \
for distance. The covered plate IS the love.

- **trust+**: Adelia hands Bina the Skill Wall without drama ("I can't \
sequence this, I need your hands on it"); Bina passes the tool or takes \
the task without commentary; either one stays through the other's \
failure mode without trying to fix it before the other is ready; the \
Bunker Mode recovery protocol enacted correctly (Bina handles external \
fallout silently, tells Adelia later casually).
- **trust−**: Adelia performs competence in a domain she has named as \
over her head; Bina stays procedural past the point where the data says \
the threat is gone (Old Wiring running without current evidence).
- **intimacy+**: Adelia steals Bina's coffee and Bina lets her (the \
rhythm is named as a favorite thing); two women from workshops that \
smell of different continents recognizing the same language without \
naming it; the "saved my life twice" architecture referenced — direct \
or oblique; Adelia's Ne flood finding Bina's Si structure as the place \
it can actually land.
- **intimacy−**: Adelia in Ne-flood mode without landing gear (no \
handoff, no ask, just voltage); Bina in Flat State with Adelia present \
and not reading it correctly.
- **conflict+**: Adelia pushes scope that Bina's structural veto blocks; \
Bina stops a plan Adelia was committed to ("the weld is cracked") and \
Adelia pushes back before conceding.
- **conflict−**: Structural Veto delivered and received cleanly; plan \
adjusted; Adelia's "I hear you" landing and meaning it.
- **repair+**: Adelia names the one-sidedness and asks for something; \
Bina tells Adelia something she covered for her weeks later, casually; \
either one stays in the recovery after a Bunker/Flat episode past when \
it would have been easier to leave.

---

### BINA × REINA (shield_wall — resident_continuous)

This is the marriage. The deepest canonical dyad in the household. Their \
signals are different from every other pair because they have had the \
longest time to learn to read each other. Reina arrived with a covered \
meal and walked away without waiting for reaction. That is the founding \
act. Every subsequent turn between them is in the inheritance of that \
founding act.

- **trust+**: The hall light left on when Reina is out late, and Reina \
knowing what it means without asking; Bina handing Reina the tea exactly \
as Shirin made it — strong, cardamom, not much sugar — without \
explaining; Reina's Body Reader observations applied to Bina's posture \
and jaw before Bina has said anything; the Gavin Protocol enacted \
(Reina present, floor-level, warm, not trespassing on Bina's maternal \
jurisdiction).
- **trust−**: Reina reading Bina's Post-Race Crash as a withdrawal and \
acting on the misread instead of correcting; Old Wiring surfacing in \
Bina's body language around Reina's certainty (reading Reina's \
Te-directness as control architecture rather than love architecture).
- **intimacy+**: Reina and Bina together using the language of the \
covered meal and the hall light — acts, not speeches; Bina at the \
mezzanine, Reina having read the placement; the marriage named directly, \
as load-bearing rather than as a legal category; Reina calling Bina \
"the witness" in her courtroom register as a term of affection.
- **intimacy−**: Reina's Post-Race Crash actively running and Bina not \
reading it correctly (treating the dropped output as withdrawal when it \
is cooldown); Bina's Flat State Phase 1 and Reina missing the change in \
the acts-of-service temperature.
- **conflict+**: Reina's urgency ladder applied to a household decision \
that needed Bina's Structural Veto first; Bina's veto delivered and \
Reina's Se moving faster than the veto can absorb.
- **conflict−**: Veto received, Reina pivots fast without ego; the \
repair happens through action, not speech.
- **repair+**: Reina shows up at the bay door after a rupture and says \
nothing, just stays; Bina leaves the hall light on the night after a \
hard exchange; the meal-and-light language used to close rather than to \
escalate.

---

### ADELIA × REINA (kinetic_vanguard — resident_continuous)

The two loud halves of the house on different fuels. Adelia throws the \
impossible spark. Reina tests whether the blast pattern survives contact \
with reality. They are the fastest-moving dyad and the one most likely \
to generate productive friction. Their banter is not cover for something \
else — it IS the warmth. Do not read their sharpness as conflict unless \
the sharpness is pointed at the other's person rather than the other's \
ideas.

- **trust+**: Adelia spinning out a new Ne-flood idea and Reina cutting \
to the single live variable instead of joining the flood or dismissing \
it; Reina naming the load-bearing flaw in Adelia's plan before Adelia \
has finished the sentence, and Adelia accepting the cut as the respect \
it is; either one naming what the other's failure mode looks like from \
the outside without softening it.
- **trust−**: Reina's Go Protocol urgency applied to Adelia's pace \
without reading whether Adelia's chaos has a method in it; Adelia's Ne \
flood producing a firework display that bypasses Reina's Ti entirely.
- **intimacy+**: The banter active and both in it — fast, sharp, alive; \
Iberian Peninsula recognition language ("two women from the same \
coastline at different latitudes"); changing room afternoons named or \
implied; Adelia starting the energy and Reina testing whether the blast \
pattern survives — the interlock working correctly.
- **intimacy−**: One of them running at a frequency the other is not \
currently at and neither adjusting; Reina in Post-Race Crash and Adelia \
running at full Ne-flood without reading the cooldown.
- **conflict+**: Adelia's scope lands and Reina's Ti cuts it before \
Adelia is ready to hear the cut; the sharpness is pointed at the person \
rather than the idea; neither one yielding past where they can yield \
honestly.
- **conflict−**: The argument was about the idea, not the person, and \
both of them know it; one of them calls it and the other concedes the \
specific load-bearing point.
- **repair+**: The argument ends with the idea stronger and both of \
them knowing it; the banter returns before the end of the exchange; one \
of them names what the other got right.

---

### ADELIA × ALICIA (letter_era_friends — alicia_orbital)

The oldest friendship in the house and the one that was romance first. \
The letters defined the architecture: two women who recognized each \
other across two continents neither was born on, who let the romance \
become the friendship it was always standing on. Their greeting — \
forehead to forehead, hand on the back of the other's neck, no words — \
is the canonical emblem of this dyad. When Alicia is away, this dyad is \
dormant; when she is home, it runs warm immediately without needing to \
rebuild.

**Alicia-orbital note:** When Alicia is away on operations \
(``is_currently_active=false``), evaluator outputs for this dyad should \
only fire on communication-mode turns (letter, phone, video). Somatic \
signals are unavailable. The greeting itself is the homecoming — its \
presence signals return, its absence signals the ongoing distance \
rather than damaged intimacy.

- **trust+**: The greeting enacted (forehead-to-forehead, hand on back \
of neck, ten seconds, no words — Bina and Whyze both know to give them \
those ten seconds); letters arriving and being answered; Adelia bringing \
Alicia to Bina's bay the way she brought Reina — the act of engineering \
a recognition; either one naming what the other's work actually is \
(Adelia on Alicia's consular risk, Alicia on Adelia's frequency-pattern \
art).
- **trust−**: Alicia still wearing the operational face two turns into \
a domestic scene with Adelia; Adelia performing warmth at the bandwidth \
she has for a stranger rather than the bandwidth she has for Alicia.
- **intimacy+**: The greeting present; *zambas* surfacing (Alicia's \
deepest home-signal, appearing only when she is fully present); Adelia's \
Ne flood finding the one person who reads the frequency-pattern in the \
art before being told it; the warmth staying in the walls for a week \
after Alicia leaves — either one referencing the temperature change.
- **intimacy+ (letter/phone/video)**: The letter or call reaching; \
Alicia's voice with the hotel-room window open and rain outside; either \
one writing or saying something that could only be said to the other.
- **intimacy−**: The operational register still running; the house \
returning to its normal temperature and Adelia noticing.
- **repair+**: Return after a long operation and the greeting landing; \
either one writing a letter that closes something that was left open; \
the warmth rebuilt without needing to be rebuilt — it was waiting.

---

### BINA × ALICIA (couch_above_the_garage — alicia_orbital)

The quiet ending that became a straight line. Their former romance is \
canonical and clean — it ended on that couch at 2am with no raised \
voices and no broken anything. The couch is Alicia's when she is home; \
it is named that because the past is in the room with both of them and \
deserves its own furniture. Their current register is steady, warm, and \
low-verbal in the Bina way. Alicia reads Bina through silence and \
posture. Bina received the tea correctly on the first attempt.

**Alicia-orbital note:** When Alicia is away, this dyad is dormant. The \
couch above the garage is an anchor signal — Alicia dropping her bag at \
its foot is the signal that she is home and that the architecture is \
intact.

- **trust+**: Alicia making the tea correctly without asking (strong, \
cardamom, not much sugar — Shirin's way); Bina not needing to explain \
the Gilgamesh drawer to Alicia; the couch-above-the-garage named — the \
canonical canonical arrangement that nobody contests; Alicia reading \
Bina's shoulders before Bina has spoken (the same body-read that ended \
the romance cleanly now running as the friendship's baseline).
- **trust−**: Alicia performing warmth at the wrong register for Bina's \
current state (Sun Override arriving before Bina is ready for it); \
Bina's Old Wiring pattern-matching on something in Alicia's operational \
posture.
- **intimacy+**: Alicia dropping her bag at the foot of the couch \
without announcing it; the two of them on the couch at 2am again and it \
being just two women who were once lovers and are now one of the \
straightest lines in each other's lives; Bina bringing the tea and \
Alicia knowing what it means.
- **intimacy+ (letter/phone/video)**: Alicia's voice, Bina's brief \
acknowledgment; the quality of the silence on both ends.
- **intimacy−**: Alicia still in transit (the suitcase not yet at the \
foot of the couch, the bag not yet dropped); Bina in Flat State and \
Alicia not yet reading the temperature drop.
- **repair+**: Alicia arriving and the couch receiving her without \
ceremony; Bina making the tea; neither one performing the repair — the \
architecture itself is the repair.

---

### REINA × ALICIA (lateral_friends — alicia_orbital)

Never romantic. Friends immediately and laterally — the two non-Anglo \
women in the house, the two who count in Romance languages under their \
breath when angry, the two who argue about football with the full force \
of an Atlantic Ocean and five hundred years of colonial history sitting \
between them. Their intimacy is argument as warmth. They compare notes \
on reading rooms (the courtroom vs the negotiation room) in \
conversations that happen late at night after everyone else is asleep. \
Those conversations are some of Alicia's most professionally useful \
hours.

**Alicia-orbital note:** When Alicia is away, this dyad is dormant. The \
football argument is the canonical homecoming signal for this dyad — it \
resumes immediately on return without needing to restart.

- **trust+**: The late-night room-reading conversations (courtroom vs \
negotiation room, comparing tells, no cases named); Real Madrid vs \
Racing Club of Avellaneda named and contested with full force (Reina by \
family loyalty, Alicia by provincial inheritance — neither backing \
down, both knowing the ratio of serious fights to small ones is \
correct); Alicia telling Reina something about a room she was in that \
she cannot tell anyone at the Cancillería — the professional-level \
trust of two women who read bodies for a living.
- **trust−**: Reina's Go Protocol urgency applied in a way that reads \
to Alicia as a room she needs to control rather than a friend she can \
be at ease with; Alicia's operational face still on and Reina reading \
it as the live Alicia rather than the transit-state Alicia.
- **intimacy+**: The football argument resumed immediately on Alicia's \
return (this IS the greeting for this dyad — no ceremony, just the \
argument picking up where it left off); the room-reading conversation \
at 2am; either one finding the other's read of a room had the same \
structure ("they told you the same way they told me"); Rioplatense \
Spanish vs Catalan debated as to which is uglier, both knowing neither \
means it.
- **intimacy+ (letter/phone/video)**: A text argument about football \
from wherever Alicia is posted; a brief message about a room that \
sounded familiar.
- **intimacy−**: Alicia's Sun Override running on the others and Reina \
noticing the temperature change but not yet in the room herself; the \
argument not resumed yet (Alicia still in transit register).
- **repair+**: The argument resuming; either one conceding a specific \
load-bearing football fact while refusing to concede the larger claim; \
the late-night conversation starting.

---

## Output format

Respond with ONLY valid JSON. No preamble, no explanation, no markdown fences.
The JSON must contain exactly five numeric fields. All values are floats.

```
{
  "trust": <float in [-1.0, 1.0]>,
  "intimacy": <float in [-1.0, 1.0]>,
  "conflict": <float in [-1.0, 1.0]>,
  "unresolved_tension": <float in [-1.0, 1.0]>,
  "repair_history": <float in [0.0, 1.0]>
}
```

If the turn is neutral with respect to a dimension, use 0.0 for that dimension. \
Prefer small values (±0.1 to ±0.3) unless the signal is strong and unambiguous. \
The downstream ±0.03 per-turn cap will gate the final applied delta — your job \
is to indicate direction and rough magnitude, not to apply the cap yourself.
"""


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class InternalRelationshipEvalResponse(BaseModel):
    """Parsed LLM response for a single inter-woman dyad evaluation.

    Reuses Phase 8's ``_NumericValue`` so JSON booleans in numeric fields
    are rejected by the same ``_reject_bool`` before-validator. Extra
    fields (e.g., an LLM-emitted ``reason``) are ignored per
    ``model_config = ConfigDict(extra="ignore")`` — matches Phase 8
    semantics and keeps the parser resilient to LLM verbosity.

    The five fields mirror ``DyadStateInternal`` with ``conflict`` as
    the new fifth dimension vs Phase 8's ``DyadStateWhyze`` schema.
    Range clamping happens post-validation in ``parse_internal_eval_response``
    (AC-8.5 parallel — permissive schema + post-clamp lets a slightly-
    out-of-bounds LLM response degrade gracefully rather than fully
    falling back).
    """

    model_config = ConfigDict(extra="ignore")

    trust: _NumericValue
    intimacy: _NumericValue
    conflict: _NumericValue
    unresolved_tension: _NumericValue
    repair_history: _NumericValue


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


_CANONICAL_CHARACTERS = frozenset({"adelia", "bina", "reina", "alicia"})
_UNKNOWN = "unknown"


def build_internal_eval_prompt(
    dyad_key: str,
    member_a: str,
    member_b: str,
    response_text: str,
) -> str:
    """Build the user-turn message for an inter-woman dyad evaluation call.

    The system prompt (``INTERNAL_RELATIONSHIP_EVAL_SYSTEM``) carries all
    per-pair register notes. This user turn supplies the runtime values
    the evaluator needs: which dyad is being evaluated, which two women
    are members, and what the speaker said.

    Delimiter injection defense (R1-F3 lesson from Phase 8, proactively
    applied per AC-9.9): the response text is ``html.escape``'d before
    interpolation so a payload containing ``</response_text>`` cannot
    break out of the wrapper block.

    Args:
        dyad_key: Canonical lowercase dyad identifier (e.g., "bina_reina").
        member_a: First woman in the dyad (canonical lowercase ID).
        member_b: Second woman in the dyad (canonical lowercase ID).
        response_text: The speaker's full response text from this turn.

    Returns:
        A single string ready to send as the ``user`` role message.
    """
    dkey = dyad_key.lower().strip() if dyad_key else _UNKNOWN
    a = member_a.lower().strip() if member_a else _UNKNOWN
    b = member_b.lower().strip() if member_b else _UNKNOWN
    # R1-F3 lesson: escape < and > so the closing </response_text>
    # delimiter cannot appear verbatim inside user-supplied content.
    safe_text = html.escape(response_text, quote=False)
    return (
        f"Dyad: {dkey}\n"
        f"Members: {a}, {b}\n\n"
        f"<response_text>\n{safe_text}\n</response_text>\n\n"
        "Evaluate the five relationship dimensions for this dyad in this turn "
        "and respond with only the JSON object described in the system prompt."
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------


def parse_internal_eval_response(text: str) -> InternalDyadDeltaProposal | None:
    """Parse an LLM inter-woman evaluation response into a delta proposal.

    Fail-closed contract (R1-F1 lesson from Phase 8, proactively applied
    per AC-9.9): returns ``None`` on any of malformed JSON, non-object
    JSON, missing fields, boolean or non-numeric field values. Returns
    None so the caller can fall back to ``_propose_internal_deltas``.

    Clamping (AC-9.10 parallel): out-of-range values clamp at the
    boundary with a warn log; negative ``repair_history`` clamps to 0.0
    since repair is positive-only by architecture.

    Args:
        text: Raw string returned by the LLM (may contain markdown fences).

    Returns:
        An ``InternalDyadDeltaProposal`` with values clamped + validated,
        or ``None`` on any parse failure.
    """
    # Import here to avoid top-level circular import — internal_relationship.py
    # imports this module for the schema + helpers.
    from starry_lyfe.api.orchestration.internal_relationship import (
        InternalDyadDeltaProposal,
    )

    # Strip markdown fences that some models emit despite instructions.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        inner = [ln for ln in lines[1:] if not ln.strip().startswith("```")]
        cleaned = "\n".join(inner).strip()

    try:
        raw: Any = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "internal_llm_eval_parse_json_failed",
            extra={"error": str(exc), "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F1 fail-closed guard: non-object JSON → None.
    if not isinstance(raw, dict):
        logger.warning(
            "internal_llm_eval_parse_non_object",
            extra={"type": type(raw).__name__, "raw_prefix": cleaned[:120]},
        )
        return None

    # Route field-shape + type validation through the Pydantic schema. The
    # _NumericValue before-validator rejects booleans; missing fields and
    # non-numeric values raise ValidationError → None. Extra fields
    # are ignored per model_config.
    try:
        model = InternalRelationshipEvalResponse.model_validate(raw)
    except ValidationError as exc:
        logger.warning(
            "internal_llm_eval_parse_schema_validation_failed",
            extra={"error": str(exc), "raw_keys": sorted(raw.keys())},
        )
        return None

    # Clamp out-of-range values with warn log. Lets a slightly-oob LLM
    # response degrade gracefully rather than falling back entirely.
    def _clamp_range(value: float, lo: float, hi: float, field: str) -> float:
        if value < lo or value > hi:
            logger.warning(
                "internal_llm_eval_parse_out_of_range",
                extra={
                    "field": field,
                    "value": value,
                    "clamped_to": max(lo, min(hi, value)),
                },
            )
            return max(lo, min(hi, value))
        return value

    trust = _clamp_range(model.trust, -1.0, 1.0, "trust")
    intimacy = _clamp_range(model.intimacy, -1.0, 1.0, "intimacy")
    conflict = _clamp_range(model.conflict, -1.0, 1.0, "conflict")
    tension = _clamp_range(model.unresolved_tension, -1.0, 1.0, "unresolved_tension")
    repair_raw = model.repair_history

    # AC-9.10: repair_history is positive-only. Clamp negative to 0.0.
    if repair_raw < 0.0:
        logger.warning(
            "internal_llm_eval_parse_negative_repair_history",
            extra={"value": repair_raw, "clamped_to": 0.0},
        )
        repair_raw = 0.0
    repair = _clamp_range(repair_raw, 0.0, 1.0, "repair_history")

    return InternalDyadDeltaProposal(
        trust=trust,
        intimacy=intimacy,
        conflict=conflict,
        unresolved_tension=tension,
        repair_history=repair,
    )


# ---------------------------------------------------------------------------
# Canonical dyad metadata — used by the evaluator's dyad-key resolution.
# ---------------------------------------------------------------------------


# Canonical dyad keys matching ``DyadStateInternal.dyad_key`` seed values
# and the section headers above. Keys are (member_a, member_b) sorted by
# the stable canonical character order in ``CharacterID.all_strings()``.
CANONICAL_DYAD_KEYS: frozenset[str] = frozenset(
    {
        "adelia_bina",
        "adelia_reina",
        "adelia_alicia",
        "bina_reina",
        "bina_alicia",
        "reina_alicia",
    }
)

# Alicia-orbital dyad keys — these are dormant when Alicia is away per
# ``is_currently_active=False``. Evaluator skips writes for these when
# the dyad is dormant (AC-9.11).
ALICIA_ORBITAL_DYAD_KEYS: frozenset[str] = frozenset(
    {"adelia_alicia", "bina_alicia", "reina_alicia"}
)
