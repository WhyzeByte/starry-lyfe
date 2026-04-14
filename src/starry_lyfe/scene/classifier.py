"""Rule-based scene classifier (Phase 5).

``classify_scene`` turns caller inputs (user message, present characters,
residence flag, optional hints) into a fully-populated ``SceneState``
that ``assemble_context`` can consume directly.

Design: pure function, deterministic, no LLM calls. Hints always win over
rule-based inference so callers (HTTP endpoint, tests) can force any
classification. This matches Phase F-Fidelity's static-scoring discipline
and keeps Phase 5 shippable without BD-1 integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..context.types import (
    CommunicationMode,
    SceneModifiers,
    SceneState,
    SceneType,
)
from .errors import AliciaAwayContradictionError

# ---------------------------------------------------------------------------
# Keyword tables
# ---------------------------------------------------------------------------
# TUNABLE: edit these tables to adjust classifier sensitivity. Every value
# is a lowercase substring checked against the lowercased user message.

_COMM_MODE_KEYWORDS: dict[CommunicationMode, tuple[str, ...]] = {
    CommunicationMode.PHONE: ("phone call", "on the phone", "called me", "she calls"),
    CommunicationMode.LETTER: ("letter", "wrote me", "her letter", "airmail"),
    CommunicationMode.VIDEO_CALL: ("video call", "video chat", "on video", "zoom call", "facetime"),
}

# SceneType keyword chain — first match wins when iterated in this order.
# Order matters: more specific patterns come first.
_SCENE_TYPE_KEYWORDS: tuple[tuple[SceneType, tuple[str, ...]], ...] = (
    (SceneType.CONFLICT, ("fight", "argument", "pushback", "shutdown", "conflict", "snapped at")),
    (SceneType.REPAIR, ("apology", "apologize", "make up", "re-approach", "repair", "i was wrong")),
    (SceneType.INTIMATE, ("in bed", "sex", "undress", "kissing", "intimate", "naked")),
    (SceneType.TRANSITION, ("in transit", "driving", "on the road", "travel", "in the car")),
    (SceneType.PUBLIC, ("work", "colleagues", "office", "courthouse", "public", "restaurant")),
)

_MODIFIER_KEYWORDS: dict[str, tuple[str, ...]] = {
    "work_colleagues_present": ("colleagues", "coworker", "co-worker", "office with", "team meeting"),
    "post_intensity_crash_active": (
        "post-crash", "after we fought", "she's crashing", "crash after", "coming down from",
    ),
    "pair_escalation_active": ("escalation", "admissibility", "pair is flaring", "pair flare", "pair escalating"),
    "warm_refusal_required": ("no, warmly", "warmly declining", "warm refusal", "refusing softly"),
    "silent_register_active": ("silent", "wordless", "without speaking", "no words", "just presence"),
    "group_temperature_shift": ("temperature shift", "room went cold", "mood shift", "atmosphere changed"),
}

# Dyads that can be explicitly invoked when absent — e.g. "missing reina"
# while Reina is not in present_characters.
_CANONICAL_WOMEN: frozenset[str] = frozenset({"adelia", "bina", "reina", "alicia"})

_ABSENT_DYAD_PATTERNS: tuple[str, ...] = (
    "missing {name}",
    "thinking about {name}",
    "wishing {name} were",
    "if {name} were here",
)


# ---------------------------------------------------------------------------
# Input dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SceneDirectorHints:
    """Optional explicit hints from the caller. Hints ALWAYS win over inference.

    Use hints when:
    - The HTTP endpoint already knows the scene type from a UI control.
    - A test needs to exercise a specific scene type regardless of the
      message content.
    - The user message is ambiguous and the caller has out-of-band context.
    """

    forced_scene_type: SceneType | None = None
    forced_modifiers: SceneModifiers | None = None
    scene_description: str | None = None
    communication_mode: CommunicationMode | None = None


@dataclass(frozen=True)
class SceneDirectorInput:
    """Inputs to the Scene Director classifier.

    Attributes:
        user_message: The raw text of Whyze's message for this turn. Used
            both to infer scene type / modifiers and to synthesize the
            ``scene_description`` field when no hint is provided.
        present_characters: Lowercase character names present in the
            scene (e.g. ``["adelia", "bina", "whyze"]``). ``"whyze"`` is
            the runtime-canonical convention (every pre-Phase-5
            ``assemble_context`` caller includes Whyze explicitly). The
            classifier auto-appends ``"whyze"`` if the caller omits it,
            so both input shapes are accepted and produce the same
            ``SceneState.present_characters`` shape downstream.
        alicia_home: Whether Alicia is physically at home right now.
            When False, in-person scenes where Alicia is marked present
            raise AliciaAwayContradictionError.
        hints: Optional caller-provided overrides.
    """

    user_message: str
    present_characters: list[str]
    alicia_home: bool = True
    hints: SceneDirectorHints = field(default_factory=SceneDirectorHints)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_scene(director_input: SceneDirectorInput) -> SceneState:
    """Classify a conversation turn into a SceneState.

    Pipeline:
    1. Determine CommunicationMode (hint → keyword → IN_PERSON default).
    2. Alicia residence gate (raises if contradictory).
    3. Determine SceneType (hint → keyword chain → presence-count → DOMESTIC).
    4. Determine SceneModifiers (hint wholly overrides, else keyword scans).
    5. Synthesize scene_description.
    6. Build and return SceneState.

    Raises:
        AliciaAwayContradictionError: Alicia present but away and mode is IN_PERSON.
    """
    text = director_input.user_message.lower()
    women_present = [c for c in director_input.present_characters if c in _CANONICAL_WOMEN]

    # (1) CommunicationMode
    comm_mode = _classify_communication_mode(text, director_input.hints)

    # (2) Alicia residence gate
    if (
        "alicia" in director_input.present_characters
        and not director_input.alicia_home
        and comm_mode == CommunicationMode.IN_PERSON
    ):
        raise AliciaAwayContradictionError(
            "Scene Director: Alicia is marked present and away "
            "(alicia_home=False) but communication_mode is IN_PERSON. "
            "Remove alicia from present_characters, set alicia_home=True, "
            "or provide hints.communication_mode of phone/letter/video_call."
        )

    # (3) SceneType
    scene_type = _classify_scene_type(text, women_present, director_input.hints)

    # (4) SceneModifiers
    modifiers = _classify_modifiers(text, director_input.hints)

    # (5) scene_description
    scene_description = _synthesize_scene_description(director_input.user_message, director_input.hints)

    # (6) Normalize present_characters to runtime convention (Whyze included).
    # Every pre-Phase-5 assemble_context caller passes Whyze explicitly;
    # layers.py:75-84 derives GROUP/SOLO_PAIR from raw len(present_characters).
    # Auto-appending here keeps the classifier lenient for both input shapes
    # while producing the single runtime-canonical SceneState shape.
    normalized_present = list(director_input.present_characters)
    if "whyze" not in normalized_present:
        normalized_present.append("whyze")

    # (7) Normalize recalled_dyads to dyad-key shape that layers.format_scene_blocks()
    # actually consumes. The modifier field keeps the bare-name shape (it is
    # literally "the names of absent dyads that were invoked"); SceneState's
    # runtime-facing field gets "<present_woman>-<absent_name>" pairs so
    # Layer 6 internal-dyad prose actually renders. See PHASE_5.md Round 1
    # remediation F1.
    recalled_dyads = _to_dyad_keys(
        modifiers.explicitly_invoked_absent_dyad,
        present_women=women_present,
    )

    # (8) Build SceneState
    # public_scene flag mirrors SceneType.PUBLIC or work_colleagues_present
    # modifier so Layer 7 constraints.py fires the right pillar.
    public_scene = scene_type == SceneType.PUBLIC or modifiers.work_colleagues_present

    return SceneState(
        present_characters=normalized_present,
        public_scene=public_scene,
        alicia_home=director_input.alicia_home,
        scene_description=scene_description,
        communication_mode=comm_mode,
        recalled_dyads=recalled_dyads,
        voice_modes=None,
        scene_type=scene_type,
        modifiers=modifiers,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _classify_communication_mode(
    text: str, hints: SceneDirectorHints
) -> CommunicationMode:
    if hints.communication_mode is not None:
        return hints.communication_mode
    for mode, patterns in _COMM_MODE_KEYWORDS.items():
        if any(p in text for p in patterns):
            return mode
    return CommunicationMode.IN_PERSON


def _classify_scene_type(
    text: str, women_present: list[str], hints: SceneDirectorHints
) -> SceneType:
    if hints.forced_scene_type is not None:
        return hints.forced_scene_type
    # Explicit keyword chain, first match wins
    for scene_type, patterns in _SCENE_TYPE_KEYWORDS:
        if any(p in text for p in patterns):
            return scene_type
    # Presence-count fallback
    if len(women_present) >= 3:
        return SceneType.GROUP
    if len(women_present) == 1:
        # Exactly one woman + Whyze → SOLO_PAIR (the canonical dyad frame)
        return SceneType.SOLO_PAIR
    # 0 or 2 women default to DOMESTIC
    return SceneType.DOMESTIC


def _classify_modifiers(text: str, hints: SceneDirectorHints) -> SceneModifiers:
    if hints.forced_modifiers is not None:
        # Hints wholly replace inference (never merged). Caller is explicit.
        return hints.forced_modifiers

    flags: dict[str, bool | frozenset[str]] = {
        flag: any(p in text for p in patterns)
        for flag, patterns in _MODIFIER_KEYWORDS.items()
    }
    flags["explicitly_invoked_absent_dyad"] = _detect_absent_dyads(text)

    return SceneModifiers(**flags)  # type: ignore[arg-type]


def _detect_absent_dyads(text: str) -> frozenset[str]:
    """Scan for named-absent-pair mentions like 'missing reina'.

    Returns BARE NAMES of the absent characters (e.g. ``{"reina"}``).
    ``_to_dyad_keys`` below normalizes this to the dyad-key shape
    (``{"adelia-reina"}``) that Layer 6 consumes. The modifier field keeps
    bare names so the semantic "who was invoked" data stays readable.
    """
    hits: set[str] = set()
    for name in _CANONICAL_WOMEN:
        for pattern in _ABSENT_DYAD_PATTERNS:
            needle = pattern.format(name=name)
            if needle in text:
                hits.add(name)
                break
    return frozenset(hits)


def _to_dyad_keys(
    absent_names: frozenset[str], present_women: list[str]
) -> set[str]:
    """Normalize absent-dyad bare names to the dyad-key shape Layer 6 reads.

    For each absent name ``N``, emit ``"<W>-<N>"`` for every canonical
    woman ``W`` in ``present_women`` (excluding ``N`` itself). Layer 6
    (``format_scene_blocks`` in ``layers.py:535-541``) silently ignores
    keys that do not match any loaded internal-dyad row, so emitting
    one key per present woman covers all reasonable focal characters
    without requiring the classifier to know who the focal is.

    Example:
        absent={"reina"}, present=["adelia", "bina"]
        -> {"adelia-reina", "bina-reina"}

    When assembling for Adelia: the "adelia-reina" key matches her
    internal-dyad row and the prose renders. When assembling for Bina:
    "bina-reina" matches. Other keys are inert.
    """
    keys: set[str] = set()
    for absent in absent_names:
        for woman in present_women:
            if woman != absent and woman != "whyze":
                keys.add(f"{woman}-{absent}")
    return keys


def _synthesize_scene_description(
    user_message: str, hints: SceneDirectorHints
) -> str:
    if hints.scene_description is not None:
        return hints.scene_description
    # Truncate raw message to ~200 chars so Layer 6 sensory grounding has
    # a usable scene hook without dumping the full message body into the
    # scene description field.
    return user_message.strip()[:200]
