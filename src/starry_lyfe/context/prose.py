"""Per-character dramaturgical prose renderers for context assembly layers.

Phase G: converts structured data (dyad state, somatic state, canon facts,
active protocols) into character-voiced narrative prose for Layers 2, 4, and 6.

Each character has distinct voice registers for the same underlying data:

- Adelia: chemistry / engineering metaphors, Ne-cascade associative energy
- Bina:   diagnostic / mechanical register, Si-declarative precision
- Reina:  admissibility / evidence register, Se-tactical body-read sharpness
- Alicia: somatic / body-first register, Se present-tense grounding

All public functions produce prose + parenthesized numeric block so callers
can render both representations. The numeric block preserves backward compat
for tests that assert numeric values; the prose block is the quality win.
"""

from __future__ import annotations

from starry_lyfe.canon.schemas.enums import _assert_complete_character_keys
from starry_lyfe.db.models.canon_facts import CanonFact
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze
from starry_lyfe.db.retrieval import DecayedSomaticState

# ---------------------------------------------------------------------------
# Trust prose (Whyze-dyad)
# ---------------------------------------------------------------------------

_TRUST_HIGH = 0.80
_TRUST_MED = 0.50
_TRUST_LOW = 0.30

_TRUST_PHRASES: dict[str, list[str]] = {
    "adelia": [
        "Load-tested and reliable. The trust has been stress-tested and held.",
        "Real and still calibrating. Earned, not inherited.",
        "Conditional, watching. Not broken but paying attention.",
        "Something to rebuild. The foundation needs work before the structure goes up.",
    ],
    "bina": [
        "Confirmed by repeated observation. The data is consistent.",
        "Provisional, recorded. The pattern is establishing itself.",
        "Unproven, watching closely. More evidence required before the register opens.",
        "Broken, under repair. The diagnostic is running.",
    ],
    "reina": [
        "Admissible without caveat. The evidentiary standard has been met.",
        "Admissible with context. The record supports it but the case is still building.",
        "Inadmissible without new evidence. Insufficient foundation to proceed.",
        "Actively disputed. The prior findings are in question.",
    ],
    "alicia": [
        "The body accepts without flinch. No gap between the approach and the landing.",
        "The body accepts with a beat. A brief read before the close.",
        "The body tenses briefly. The nervous system is still deciding.",
        "The body will not settle. Something is registering as unsafe.",
    ],
}
_assert_complete_character_keys(_TRUST_PHRASES, "_TRUST_PHRASES")


def _trust_phrase(character_id: str, trust: float) -> str:
    phrases = _TRUST_PHRASES.get(character_id, _TRUST_PHRASES["bina"])
    if trust > _TRUST_HIGH:
        return phrases[0]
    if trust > _TRUST_MED:
        return phrases[1]
    if trust > _TRUST_LOW:
        return phrases[2]
    return phrases[3]

# ---------------------------------------------------------------------------
# Intimacy prose
# ---------------------------------------------------------------------------

_INTIMACY_HIGH = 0.75
_INTIMACY_MED = 0.50
_INTIMACY_LOW = 0.25

_INTIMACY_PHRASES: dict[str, list[str]] = {
    "adelia": [
        "The intimacy is specific and earned — not generic, not performed.",
        "The intimacy is present, still finding its particular shape.",
        "The intimacy is careful. Not yet fully open.",
        "The intimacy is not available right now.",
    ],
    "bina": [
        "The intimacy is settled and mutual, without the need to prove it again.",
        "The intimacy is growing, each turn confirming the last.",
        "The intimacy is present but not offered freely yet.",
        "The intimacy is closed. The inner register is not available.",
    ],
    "reina": [
        "The intimacy has been earned through sufficient context. The gate is open.",
        "The intimacy is accumulating. The evidentiary record is building.",
        "The intimacy requires more context before the gate opens.",
        "The gate is closed. Insufficient prior record.",
    ],
    "alicia": [
        "Close distance welcome. The body permits it without reservation.",
        "Close distance possible with a moment's read.",
        "Close distance is a question, not an assumption right now.",
        "Close distance is not available right now.",
    ],
}
_assert_complete_character_keys(_INTIMACY_PHRASES, "_INTIMACY_PHRASES")


def _intimacy_phrase(character_id: str, intimacy: float) -> str:
    phrases = _INTIMACY_PHRASES.get(character_id, _INTIMACY_PHRASES["bina"])
    if intimacy > _INTIMACY_HIGH:
        return phrases[0]
    if intimacy > _INTIMACY_MED:
        return phrases[1]
    if intimacy > _INTIMACY_LOW:
        return phrases[2]
    return phrases[3]


# ---------------------------------------------------------------------------
# Conflict and tension prose
# ---------------------------------------------------------------------------

_CONFLICT_HIGH = 0.60
_CONFLICT_MOD = 0.35
_CONFLICT_LOW = 0.15

_TENSION_SIGNIFICANT = 0.35
_TENSION_PRESENT = 0.15


def _conflict_phrase(character_id: str, conflict: float) -> str | None:
    if conflict < _CONFLICT_LOW:
        return None
    if conflict < _CONFLICT_MOD:
        return {
            "adelia": "Low friction in the system.",
            "bina":   "Low conflict reading on the diagnostic.",
            "reina":  "Minimal contested ground.",
            "alicia": "A small tension in the air — nothing that requires movement.",
        }.get(character_id, "Low active conflict.")
    if conflict < _CONFLICT_HIGH:
        return {
            "adelia": "Active friction. Something needs to burn off or be named.",
            "bina":   "Moderate conflict flagged. The circuit is under load.",
            "reina":  "Active contested ground. Evidence is in dispute.",
            "alicia": "The body is reading tension between them.",
        }.get(character_id, "Moderate active conflict.")
    return {
        "adelia": "Significant friction. The structure is under stress.",
        "bina":   "High conflict reading. The grid needs a circuit break.",
        "reina":  "Significant contested ground. The admissibility gate may close.",
        "alicia": "The body is braced. Something needs to resolve before distance closes.",
    }.get(character_id, "High active conflict.")


def _tension_phrase(character_id: str, tension: float) -> str | None:
    if tension < _TENSION_PRESENT:
        return None
    if tension < _TENSION_SIGNIFICANT:
        return {
            "adelia": "Unresolved tension present — a thread left hanging.",
            "bina":   "Unresolved tension noted. The ledger has an open item.",
            "reina":  "Outstanding evidentiary gap. Something has not been addressed.",
            "alicia": "A residual weight in the air between them.",
        }.get(character_id, "Unresolved tension present.")
    return {
        "adelia": "Significant unresolved tension. Something is overdue.",
        "bina":   "Significant open item on the ledger. This needs to be named.",
        "reina":  "The prior record has a significant gap. It will surface.",
        "alicia": "The body is carrying something that has not been set down.",
    }.get(character_id, "Significant unresolved tension.")


# ---------------------------------------------------------------------------
# Public: render Whyze-dyad prose
# ---------------------------------------------------------------------------


def render_dyad_whyze_prose(character_id: str, dyad: DyadStateWhyze) -> str:
    """Render a Whyze-character dyad state in per-character voiced prose.

    Returns a string with bracketed prose block followed by parenthesized
    numeric summary::

        [Load-tested and reliable. The trust has been stress-tested and held.
         The intimacy is specific and earned. No active conflict.]
        (trust=0.92 intimacy=0.90 conflict=0.08 tension=0.05)
    """
    parts: list[str] = [_trust_phrase(character_id, dyad.trust)]
    parts.append(_intimacy_phrase(character_id, dyad.intimacy))

    conflict_note = _conflict_phrase(character_id, dyad.conflict)
    if conflict_note:
        parts.append(conflict_note)

    tension_note = _tension_phrase(character_id, dyad.unresolved_tension)
    if tension_note:
        parts.append(tension_note)

    prose = " ".join(parts)
    numeric = (
        f"(trust={dyad.trust:.2f} intimacy={dyad.intimacy:.2f} "
        f"conflict={dyad.conflict:.2f} tension={dyad.unresolved_tension:.2f})"
    )
    return f"[{prose}]\n{numeric}"


# ---------------------------------------------------------------------------
# Public: render internal dyad prose
# ---------------------------------------------------------------------------


def render_dyad_internal_prose(character_id: str, dyad: DyadStateInternal) -> str:
    """Render an internal (woman-to-woman) dyad state in per-character prose.

    Uses the focal character's voice register to describe the pair state.
    Returns bracketed prose + parenthesized numeric block.
    """
    other = dyad.member_b if dyad.member_a == character_id else dyad.member_a
    interlock = dyad.interlock or "pair"

    trust_note = _trust_phrase(character_id, dyad.trust)
    intimacy_note = _intimacy_phrase(character_id, dyad.intimacy)
    conflict_note = _conflict_phrase(character_id, dyad.conflict) or ""

    prose_parts = [f"{dyad.member_a}-{other} — {interlock}.", trust_note, intimacy_note]
    if conflict_note:
        prose_parts.append(conflict_note)

    prose = " ".join(prose_parts)
    numeric = (
        f"(trust={dyad.trust:.2f} intimacy={dyad.intimacy:.2f} "
        f"conflict={dyad.conflict:.2f})"
    )
    return f"[{prose}]\n{numeric}"


# ---------------------------------------------------------------------------
# Somatic prose
# ---------------------------------------------------------------------------

_FATIGUE_HIGH = 0.70
_FATIGUE_MOD = 0.40

_FATIGUE_PHRASES: dict[str, list[str]] = {
    "adelia": [
        "The chemistry is running on backup. The sentences are getting louder.",
        "She is paying for this morning's sparks, visibly.",
        "The engine is hot and well-fed.",
    ],
    "bina": [
        "The grid has given everything it had. The hall light will still go on.",
        "She has been moving more than the ledger allowed.",
        "The systems are green.",
    ],
    "reina": [
        "The body has been spent and the admissibility gate is closing.",
        "She is still sharp but beginning to feel the afternoon.",
        "The body is ready, leaning forward.",
    ],
    "alicia": [
        "The Ni-grip is close. The words have stopped working.",
        "Her presence has gone slightly inward.",
        "The body is settled and attending.",
    ],
}
_assert_complete_character_keys(_FATIGUE_PHRASES, "_FATIGUE_PHRASES")

_STRESS_HIGH = 0.60
_STRESS_MOD = 0.30

_STRESS_PHRASES: dict[str, list[str]] = {
    "adelia": [
        "Stress residue: high. The blast pattern is still visible.",
        "Stress residue: moderate. Some cordite still in the air.",
        "Stress residue: low.",
    ],
    "bina": [
        "Stress residue: high. The circuit is still warm.",
        "Stress residue: moderate. The reading is elevated.",
        "Stress residue: low.",
    ],
    "reina": [
        "Stress residue: high. The court is still in the room.",
        "Stress residue: moderate. The day is still in the body.",
        "Stress residue: low.",
    ],
    "alicia": [
        "Stress residue: high. The operation is still in the air around her.",
        "Stress residue: moderate. Some residue from the work.",
        "Stress residue: low.",
    ],
}
_assert_complete_character_keys(_STRESS_PHRASES, "_STRESS_PHRASES")


def _fatigue_phrase(character_id: str, fatigue: float) -> str:
    phrases = _FATIGUE_PHRASES.get(character_id, _FATIGUE_PHRASES["bina"])
    if fatigue > _FATIGUE_HIGH:
        return phrases[0]
    if fatigue > _FATIGUE_MOD:
        return phrases[1]
    return phrases[2]


def _stress_phrase(character_id: str, stress: float) -> str:
    phrases = _STRESS_PHRASES.get(character_id, _STRESS_PHRASES["bina"])
    if stress > _STRESS_HIGH:
        return phrases[0]
    if stress > _STRESS_MOD:
        return phrases[1]
    return phrases[2]


def render_somatic_prose(character_id: str, state: DecayedSomaticState) -> str:
    """Render somatic state in per-character voiced prose + numeric block.

    Returns bracketed prose followed by numeric summary::

        [The grid has given everything it had. The hall light will still go on.
         Stress residue: low. No injury residue.]
        (fatigue=0.82 stress=0.18 injury=0.00)
    """
    parts = [_fatigue_phrase(character_id, state.fatigue)]
    parts.append(_stress_phrase(character_id, state.stress_residue))

    if state.injury_residue > 0.10:
        parts.append(f"Injury residue: {state.injury_residue:.2f}.")
    else:
        parts.append("No injury residue.")

    prose = " ".join(parts)
    numeric = (
        f"(fatigue={state.fatigue:.2f} stress={state.stress_residue:.2f} "
        f"injury={state.injury_residue:.2f})"
    )
    return f"[{prose}]\n{numeric}"


# ---------------------------------------------------------------------------
# Protocol prose
# ---------------------------------------------------------------------------

_PROTOCOL_PROSE: dict[str, dict[str, str]] = {
    "flat_state": {
        "bina": (
            "She is in Flat State. Syllables cost more than they earn. "
            "Touch is safer than talk."
        ),
        "default": "Flat State active. Minimal verbal output. Physical presence preferred.",
    },
    "post_race_crash": {
        "reina": (
            "The adrenaline has left the building. She will need thirty minutes "
            "and an electrolyte drink before she can be reached for anything not urgent."
        ),
        "default": "Post-intensity crash active. Recovery mode engaged.",
    },
    "four_phase_return": {
        "alicia": (
            "She is returning from an operation. Language is thin; "
            "weight and silence are the currency."
        ),
        "default": "Four-Phase Return active. Operational decompression in progress.",
    },
    "whiteboard_mode": {
        "adelia": (
            "She is mid-cascade. The marker is in her hand. "
            "Sequence her, do not interrupt her."
        ),
        "default": "Whiteboard Mode active. Do not interrupt the cascade.",
    },
    "warlord_mode": {
        "reina": "Warlord Mode active. She is building the case. Stand clear.",
        "default": "High-output mode active.",
    },
    "bunker_mode": {
        "adelia": (
            "Bunker Mode active. She has retreated to the processing loop. "
            "Minimal surface engagement. The first responder is Reina."
        ),
        "default": "Withdrawal protocol active.",
    },
}


def render_protocol_prose(character_id: str, protocol_key: str) -> str | None:
    """Return per-character voiced text for a named active protocol.

    Returns None if the protocol key is not recognized.
    """
    protocol_map = _PROTOCOL_PROSE.get(protocol_key.lower())
    if protocol_map is None:
        return None
    return protocol_map.get(character_id, protocol_map.get("default", ""))


# ---------------------------------------------------------------------------
# Canon facts prose
# ---------------------------------------------------------------------------

_PAIR_NAMES: dict[str, str] = {
    "entangled": "The Entangled Pair",
    "circuit":   "The Circuit Pair",
    "kinetic":   "The Kinetic Pair",
    "solstice":  "The Solstice Pair",
}


def render_canon_prose(character_id: str, facts: list[CanonFact]) -> str:
    """Render canon facts as a voiced narrative paragraph.

    Converts the flat key-value list into a compact, readable block that
    the model absorbs more naturally than a JSON blob::

        Adelia Raye (The Catalyst). ENFP-A, Ne-dominant.
        Valencian-Australian, born Valencia, Spain.
        Pyrotechnician, installation artist, embedded systems engineer.
        The Entangled Pair. Resident at Foothills County, Alberta.

    Falls back to the flat-list format if essential keys are missing.
    """
    fm: dict[str, str] = {f.fact_key: f.fact_value for f in facts}

    name = fm.get("full_name", character_id.title())
    epithet = fm.get("epithet", "")
    mbti = fm.get("mbti", "")
    dominant = fm.get("dominant_function", "")
    heritage = fm.get("heritage", "")
    birthplace = fm.get("birthplace", "")
    profession = fm.get("profession", "")
    pair_raw = fm.get("pair_name", "")
    pair_label = _PAIR_NAMES.get(pair_raw, pair_raw.title() + " Pair" if pair_raw else "")
    residence = fm.get("current_residence", "")

    lines: list[str] = []
    header = f"{name} ({epithet})." if epithet else f"{name}."
    if mbti and dominant:
        header += f" {mbti}, {dominant}-dominant."
    elif mbti:
        header += f" {mbti}."
    lines.append(header)

    if heritage and birthplace:
        lines.append(f"{heritage}, born {birthplace}.")
    elif heritage:
        lines.append(f"{heritage}.")

    if profession:
        lines.append(f"{profession}.")

    extra_parts: list[str] = []
    if pair_label:
        extra_parts.append(pair_label)
    if residence:
        extra_parts.append(f"Resident at {residence}")

    # Character-specific biographical additions
    _add_character_specific_facts(character_id, fm, extra_parts)

    if extra_parts:
        lines.append(". ".join(extra_parts) + ".")

    return " ".join(lines)


def _add_character_specific_facts(
    character_id: str,
    fm: dict[str, str],
    parts: list[str],
) -> None:
    """Append character-specific canonical biographical details."""
    if character_id == "bina":
        if fm.get("spouse"):
            parts.append(f"Married to {fm['spouse']}")
        if fm.get("children"):
            parts.append(f"Mother to {fm['children']}")
    elif character_id == "alicia":
        if fm.get("operational_travel"):
            parts.append("Frequently away on consular operations")
