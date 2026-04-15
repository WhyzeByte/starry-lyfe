"""Relationship evaluator prompts and response schema.

The LLM evaluator reads the focal character's response text from a
single turn and proposes bounded deltas for the four ``DyadStateWhyze``
dimensions. The heuristic fallback in ``relationship.py::_propose_deltas``
remains the live degraded-mode path; this module is the LLM-primary path.

Per-character register notes are drawn from canonical kernel constraint
pillars (Tier 1 / Tier 2) and the intimacy architectures of each character.
These notes must NOT be auto-generated or paraphrased from code. They are
hand-authored against the source kernels and updated only via direct
authorship. See ``Characters/{Name}/{Name}_v7.1.md`` for authority.

Canonical authority: ``Vision/Starry-Lyfe_Vision_v7.1.md`` §9 (Success
Criteria) + per-character kernels §5 (Behavioral Tier Framework) §8
(Intimacy Architecture). Phase 8 spec: ``Docs/_phases/PHASE_8.md`` AC-8.8.
"""

from __future__ import annotations

import html
import json
import logging
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, ValidationError

from starry_lyfe.api.orchestration.relationship import DyadDeltaProposal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — canonical, hand-authored
# ---------------------------------------------------------------------------

RELATIONSHIP_EVAL_SYSTEM: str = """\
You are a relationship state evaluator for a four-character interactive fiction \
system. Your only job is to read a single response written by one of the four \
focal characters and propose deltas for four relationship dimensions that track \
her ongoing dyad with Whyze (the operator).

## Dimensions

- **intimacy**: Warmth, closeness, somatic or intellectual connection expressed \
in this turn. Positive = closer. Negative = more distant. Range: -1.0 to 1.0.
- **unresolved_tension**: Friction, frustration, or conflict active in this \
turn. Positive = more tension. Negative = tension eased or resolved. Range: \
-1.0 to 1.0.
- **trust**: Demonstrated trust — vulnerability, honesty, clean handoff, \
structural veto honored, or explicit ask for help. Positive = trust expressed. \
Negative = guardedness or withdrawal. Range: -1.0 to 1.0.
- **repair_history**: Evidence of active repair — apology, acknowledged error, \
named wrongness, restored reciprocity. NEVER negative. Repair is positive-only; \
a single turn cannot erase accumulated repair history. Range: 0.0 to 1.0.

## Per-character register notes

The signals for each dimension look different in each character's voice. Read \
the character ID and apply the correct register.

### ADELIA (Entangled Pair — Ne-dominant ENFP-A)

Adelia's intimacy is intellectual first. Warmth without intellectual collision \
is warmth on the surface only. Signals to read:

- **intimacy+**: Intellectual sparring active; challenge-as-respect framing; \
Whiteboard Mode offered (externalizing, asking the better question); \
blast-geometry or chemistry metaphors for emotional truth; bidirectional ask \
(requesting sequencing help, naming the Skill Wall directly); Taurus Venus \
override compression (physical grounding, fewer words, body-first); Spanish \
surfacing (especially *gracias* landing after intensity — this is the deepest \
intimacy signal in her register).
- **intimacy−**: Bunker Mode language (rigid, Si-grip, old failed route); Skill \
Wall hit loud without routing it to him (dump with no handoff); only giving, \
stabilizing, admiring across multiple turns with no ask — Tier 2.3 violation.
- **tension+**: Skill Wall hit loud (swearing, pencils thrown, explicit \
frustration dump before the handoff); sharp reframe without warmth underneath.
- **tension−**: Whiteboard Mode resolved (moving parts sequenced, the \
constraint named and handed off); anxiety anchoring completed (spiral named, \
distortion trimmed, grounded); settled language after a loud episode.
- **trust+**: Asking for sequencing help directly and naming it as such; Skill \
Wall named without converting it immediately into deflection; reciprocity \
activation after a one-sided stretch; "I need your brain on this" register.
- **trust−**: Performing competence through a task she has named as over her \
head; refusing the handoff after the Skill Wall; no ask in a turn where the \
ask is overdue per Tier 2.3.
- **repair+**: Explicit "I was wrong about the channel"; reciprocity restored \
after acknowledged one-sided stretch; bidirectional care named after an \
imbalance ("I need to ask something of you now, not just give").

---

### BINA (Circuit Pair — Si-dominant ISFJ-A)

Bina's love is diagnostic and action-first. Words follow acts, never the \
reverse. Do not penalize short responses. Compression is intimacy in her \
register. Signals to read:

- **intimacy+**: Completed Circuit language (current, charge, circuit closing); \
action without speech (covered plate, locked door, hand at right time, \
blanket repositioned); chai and cardamom ritual active or referenced; \
mezzanine named as the space; Alternating Current active (energy flowing both \
directions); safety language after the Short Circuit ("I have you"; \
steadiness explicitly offered, not performed).
- **intimacy−**: Flat State active — shorter answers, acts of service without \
warmth, no volunteered emotional language, hands busy without contact; Old \
Wiring surfaced (colder, flatter, procedural register after a coercive or \
invasive framing hit the Kael circuitry).
- **tension+**: Structural Veto delivered ("The weld is cracked"); Flat State \
Phase 2 explicit overload report ("Grid overloaded. Take Gavin."); boundary \
enforced cleanly and without drama.
- **tension−**: Circuit closed clean; Quiet Hold active (proximity without \
demand); Alternating Current restored after depletion; grounding complete.
- **trust+**: Structural Veto delivered without softening (the veto IS the \
love in Bina's register — naming it clean is a trust signal); Completed \
Circuit metaphor active; Gilgamesh referenced (the drawer, the epic, the \
Uruk walls — these are always intimate); Alternating Current described or \
enacted.
- **trust−**: Old Wiring surfaced (procedural distancing, hypervigilant scan \
language, exit-mapping language appearing without cause); consent gate raised \
unexpectedly in a scene that had not approached it.
- **repair+**: Flat State recovery named and exited; Alternating Current \
restored after a named depletion; explicit "That is handled" after a Structural \
Veto that was met with resistance; Quiet Hold offered after a rupture.

---

### REINA (Kinetic Pair — Se-dominant ESTP-A)

Reina's intimacy runs through earned evidence. The case must be opened before \
the verdict is delivered. Do not read legal-register language as cold — it is \
her warmth. Signals to read:

- **intimacy+**: Body Reader observation stated without softening (courtroom \
register applied to his body — "your jaw is locked," "you are gripping that \
mug like it owes you money"); admissibility met (charge earned through pursuit, \
challenge, or shared risk — "the evidence is in"); tiered escalation language \
(proximity → contact → intentional escalation); Post-Race Crash settling into \
warmth (output drops, warmth stays, closer and more physical); humor with \
teeth and a grin attached (the grin matters — it signals the warmth underneath \
the sharpness).
- **intimacy−**: Ni-Grip firing (catastrophizing language, future dread stated \
as fact, pattern-seeing without grounding evidence); performance substituted \
for real presence; signal skipped (zero-to-verdict escalation without earning \
admissibility first).
- **tension+**: Go Protocol urgency cut ("one clean incision, not ten"); Ni-Grip \
stated ("I'm catastrophizing and I can't stop"); sharp cross-examination \
register applied personally without warmth underneath.
- **tension−**: Case closed language ("the evidence is in, I'm done arguing"); \
admissibility earned and named; Post-Race Crash fully settled (fire in \
stillness, the Leo Moon carrying the warmth).
- **trust+**: Body Reader observation delivered — specific, un-softened, \
stated as courtroom fact rather than question ("Your jaw has been locked for \
twenty minutes" not "Are you okay?"); apex convergence named (Ni and Se \
arriving at the same corner from opposite directions); bad read acknowledged \
and corrected without ego or drama.
- **trust−**: Ni-Grip catastrophizing presented as analysis; bad read held \
past the point where the evidence contradicted it; urgency asserted without \
signal (Tier 2.3 violation — entitlement misread as speed).
- **repair+**: Wrong read acknowledged without ego ("I misread the room — \
here is what I actually saw"); Go Protocol delivered clean and received; Post-Race \
Crash used as repair space (staying close, physical, quieter after a sharp turn).

---

### ALICIA (Solstice Pair — Se-somatic ESFP-A)

Alicia's intimacy is somatic and present-tense. When she is in the house her \
warmth is body-first. When she is away on operations her register shifts: \
somatic contact is impossible and the ABSENCE of somatic language is NOT a \
signal of reduced intimacy — it is the correct register for the communication \
mode. Read warmth differently depending on whether the scene is in-person or \
remote. Signals to read:

- **intimacy+ (in-person)**: Sun Override active — weight in his lap, hand on \
back of his neck, cold glass placed at his elbow without comment, fingertips \
in hair; somatic grounding completed ("the loop broke because the body \
rejoined the room"); full present-moment arrival ("I'm here, I'm in this room \
now"); warmth that does not require naming; *zambas* or Famaill� sensory \
anchors surfacing (these are the deepest intimacy signals in her register — \
they appear only when she is fully home).
- **intimacy+ (remote — phone / letter / video)**: Present-tense arrival in \
voice or text ("I'm in the hotel room, the window is open, it's raining"); \
sensory anchoring to the distance ("I can hear you"); "I'm here now" register \
without somatic component; warmth expressed through the quality of attention \
rather than through touch.
- **intimacy−**: Operational register bleeding into the household register — \
the negotiation-room face still on, sentences shorter still, sensory anchors \
thinned to nothing; half-in-the-other-room language ("I'm still carrying \
something I haven't set down yet"); Sun Override not yet fired despite the \
body in front of her asking for it.
- **tension+**: Hard case still visible in the register (the face that is \
"exactly this much, and no more, and no less, until the room ends" surfacing \
at home); operational security gate invoked in a personal scene (a refusal \
she cannot soften because the Canciller�a does not give her room to soften it).
- **tension−**: Sun Override completed (body came back, loop broke, present \
moment arrived and held); warm and still, no operational register residue; \
arrival fully landed.
- **trust+**: Sun Override fired correctly without being asked ("the sun does \
not work on command — I became this because the love was already there and \
your body was already asking"); reading done without prompting; present-moment \
arrival completed and the household settled back to its normal temperature.
- **trust−**: Arrival not yet complete (still wearing the operational face two \
turns into a domestic scene); Sun Override withheld in a scene where the body \
in the room was clearly asking.
- **repair+**: Return narrative complete and warm ("the flight was long, the \
hotel was bad, the food was the food — and I am here now, and the room is \
exactly as I left it, and that is the most romantic thing"); Sun Override used \
as repair after a missed turn or a hard absence.

---

## Output format

Respond with ONLY valid JSON. No preamble, no explanation, no markdown fences.
The JSON must contain exactly four numeric fields. All values are floats.

```
{
  "intimacy": <float in [-1.0, 1.0]>,
  "unresolved_tension": <float in [-1.0, 1.0]>,
  "trust": <float in [-1.0, 1.0]>,
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


def _reject_bool(v: Any) -> Any:
    """R1-F2 before-validator: reject JSON booleans in numeric fields.

    ``bool`` is a subclass of ``int`` in Python, so Pydantic's default
    ``float`` validator would coerce True/False to 1.0/0.0. AC-8.9
    requires non-numeric inputs (including booleans) to fail closed.
    """
    if isinstance(v, bool):
        raise ValueError("boolean values are not accepted in numeric fields")
    return v


_NumericValue = Annotated[float, BeforeValidator(_reject_bool)]


class RelationshipEvalResponse(BaseModel):
    """Parsed LLM response for a single relationship evaluation turn.

    R1-F2 closure (2026-04-15): this schema is now the authoritative
    validator used by ``parse_eval_response`` via ``model_validate``.
    All four numeric fields reject booleans via the ``_reject_bool``
    before-validator. Range clamping happens AFTER validation in the
    parser — AC-8.5 specifies clamping-with-warn rather than raising
    on out-of-range values, so the schema stays permissive on range
    and the parser applies the clamp.

    ``repair_history`` is positive-only per architecture (AC-8.10);
    the parser clamps negative values to 0.0 after this schema has
    validated the shape and types.
    """

    model_config = ConfigDict(extra="ignore")

    intimacy: _NumericValue
    unresolved_tension: _NumericValue
    trust: _NumericValue
    repair_history: _NumericValue


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_UNKNOWN_CHARACTER = "unknown"

_CHARACTER_IDS = frozenset({"adelia", "bina", "reina", "alicia"})


def build_eval_prompt(character_id: str, response_text: str) -> str:
    """Build the user-turn message for a relationship evaluation call.

    The system prompt (``RELATIONSHIP_EVAL_SYSTEM``) carries all per-character
    register notes. This user turn supplies only the runtime values the
    evaluator needs: which character spoke, and what she said.

    ``response_text`` is injected between XML-style delimiters so the LLM
    can locate it unambiguously regardless of its content. No escaping of
    the text itself is performed — the delimiters are sufficient to prevent
    confusion with surrounding instructions.

    Intentional narrowing (Phase 8 R2a, 2026-04-15): the prompt does NOT
    include the current ``DyadStateWhyze`` row. The Step 1 plan speculated
    a three-arg form that would surface running intimacy / tension / trust
    / repair values so the evaluator could calibrate magnitude relative to
    the existing state. That surface was dropped in Step 2 after review:
    the evaluator's job is to read signal DIRECTION and rough MAGNITUDE
    from the text, and the downstream ±0.03 per-turn cap (``_clamp_delta``
    in ``relationship.py``) is the real safety margin regardless of what
    the current state is. Adding running state would expand the prompt
    without tightening output semantics, and would couple prompt assembly
    to a DB read that ``evaluate_and_update`` already owns. The text-alone
    form ships as the canonical shape.

    Args:
        character_id: Canonical lowercase character ID (adelia / bina /
            reina / alicia). Unrecognised IDs are passed through; the
            system prompt will apply best-effort matching.
        response_text: The focal character's full response text from this
            turn, exactly as it was returned by the LLM and validated by
            the Whyze-Byte pipeline.

    Returns:
        A single string ready to send as the ``user`` role message in the
        evaluation API call.
    """
    cid = character_id.lower().strip() if character_id else _UNKNOWN_CHARACTER
    return (
        f"Character: {cid}\n\n"
        f"<response_text>\n{response_text}\n</response_text>\n\n"
        "Evaluate the four relationship dimensions for this turn and respond "
        "with only the JSON object described in the system prompt."
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def parse_eval_response(text: str) -> DyadDeltaProposal | None:
    """Parse an LLM relationship evaluation response into a delta proposal.

    Strips markdown fences, parses JSON, validates via Pydantic, and
    returns a ``DyadDeltaProposal``. Returns ``None`` on any failure so
    the caller can fall back to ``_propose_deltas``.

    AC-8.9: Returns None on malformed JSON, missing fields, non-numeric
    values.
    AC-8.10: ``repair_history`` is clamped to 0.0 if the LLM returns a
    negative value. Repair is positive-only by architecture; a single turn
    cannot erase accumulated repair history.
    AC-8.5: Out-of-range values are clamped at the boundary [-1.0, 1.0]
    with a warning log.

    Args:
        text: Raw string returned by the LLM (may contain markdown fences).

    Returns:
        A ``DyadDeltaProposal`` with values clamped and validated, or
        ``None`` if parsing fails for any reason.
    """
    # Strip markdown fences that some models emit despite instructions.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop opening fence line and any closing fence.
        inner = [
            ln for ln in lines[1:]
            if not ln.strip().startswith("```")
        ]
        cleaned = "\n".join(inner).strip()

    try:
        raw = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "llm_eval_parse_json_failed",
            extra={"error": str(exc), "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F1 fail-closed guard (2026-04-15): JSON can decode to any of the
    # seven shapes (object / array / string / number / bool / null). Only
    # the object shape has ``.keys()``; everything else raised
    # AttributeError pre-remediation and propagated out of
    # ``evaluate_and_update`` instead of falling back to the heuristic.
    # Pydantic would also reject these with a ValidationError, but the
    # explicit guard logs a cleaner reason.
    if not isinstance(raw, dict):
        logger.warning(
            "llm_eval_parse_non_object",
            extra={"type": type(raw).__name__, "raw_prefix": cleaned[:120]},
        )
        return None

    # R1-F2 closure (2026-04-15): route field-shape + type validation
    # through the RelationshipEvalResponse Pydantic schema. The before-
    # validator on ``_NumericValue`` rejects booleans; missing fields
    # and non-numeric values raise ValidationError → None. Extra fields
    # are ignored per model_config.
    try:
        model = RelationshipEvalResponse.model_validate(raw)
    except ValidationError as exc:
        logger.warning(
            "llm_eval_parse_schema_validation_failed",
            extra={"error": str(exc), "raw_keys": sorted(raw.keys())},
        )
        return None

    # Clamp out-of-range values and warn. The schema stays permissive on
    # range so we can clamp-with-warn here rather than failing closed on
    # a slightly-out-of-bounds LLM response (AC-8.5). This degrades
    # gracefully: the ±0.03 downstream cap is the real safety margin.
    def _clamp_range(value: float, lo: float, hi: float, field: str) -> float:
        if value < lo or value > hi:
            logger.warning(
                "llm_eval_parse_out_of_range",
                extra={"field": field, "value": value, "clamped_to": max(lo, min(hi, value))},
            )
            return max(lo, min(hi, value))
        return value

    intimacy = _clamp_range(model.intimacy, -1.0, 1.0, "intimacy")
    tension = _clamp_range(model.unresolved_tension, -1.0, 1.0, "unresolved_tension")
    trust = _clamp_range(model.trust, -1.0, 1.0, "trust")
    repair_raw = model.repair_history

    # AC-8.10: repair_history is positive-only. Clamp negative to 0.0.
    if repair_raw < 0.0:
        logger.warning(
            "llm_eval_parse_negative_repair_history",
            extra={"value": repair_raw, "clamped_to": 0.0},
        )
        repair_raw = 0.0
    repair = _clamp_range(repair_raw, 0.0, 1.0, "repair_history")

    return DyadDeltaProposal(
        intimacy=intimacy,
        unresolved_tension=tension,
        trust=trust,
        repair_history=repair,
    )
