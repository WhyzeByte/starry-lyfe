"""Shared enum types for canon YAML schemas."""

from enum import StrEnum
from typing import Any


class CharacterID(StrEnum):
    """The four canonical characters."""

    ADELIA = "adelia"
    BINA = "bina"
    REINA = "reina"
    ALICIA = "alicia"

    @classmethod
    def all(cls) -> list["CharacterID"]:
        """Return all CharacterID members as a list (R-3.1)."""
        return list(cls)

    @classmethod
    def all_strings(cls) -> list[str]:
        """Return all CharacterID string values as a list (R-3.1)."""
        return [c.value for c in cls]


def _assert_complete_character_keys(
    d: dict[str, Any] | set[str],
    source_name: str,
) -> None:
    """Raise ValueError if ``d`` does not exactly cover ``CharacterID`` membership.

    Per REMEDIATION_2026-04-13.md R-3.2 (spec-canonical name): every
    per-character dict or set scattered across the codebase (kernel
    paths, voice paths, budget scaling, pair mapping, prose banks,
    constraint pillars, soul essence registry) must be validated at
    module-import time to prevent silent drift when a character is
    added, removed, or renamed.
    """
    expected = set(CharacterID.all_strings())
    actual = set(d.keys()) if isinstance(d, dict) else set(d)
    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        raise ValueError(
            f"{source_name}: character coverage mismatch. "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )


# Backward-compat alias for the pre-R-3.2 name. New code should use
# _assert_complete_character_keys per spec.
assert_complete_character_coverage = _assert_complete_character_keys


class PairName(StrEnum):
    """The four Whyze-to-character pair names."""

    ENTANGLED = "entangled"
    CIRCUIT = "circuit"
    KINETIC = "kinetic"
    SOLSTICE = "solstice"


class MBTIType(StrEnum):
    """MBTI types used in the household."""

    ENFP_A = "ENFP-A"
    ISFJ_A = "ISFJ-A"
    ESTP_A = "ESTP-A"
    ESFP_A = "ESFP-A"
    INTJ_T = "INTJ-T"


class CognitiveFunction(StrEnum):
    """Jungian cognitive functions."""

    NE = "Ne"
    NI = "Ni"
    SE = "Se"
    SI = "Si"
    FE = "Fe"
    FI = "Fi"
    TE = "Te"
    TI = "Ti"


class ThinkingEffort(StrEnum):
    """Msty Persona Studio thinking-effort labels."""

    THINK_LIGHTLY = "think_lightly"
    THINK_MODERATELY = "think_moderately"


class DyadType(StrEnum):
    """Dyad relationship type."""

    INTER_WOMAN = "inter_woman"
    WHYZE_PAIR = "whyze_pair"


class DyadSubtype(StrEnum):
    """Inter-woman dyad subtypes."""

    RESIDENT_CONTINUOUS = "resident_continuous"
    ALICIA_ORBITAL = "alicia_orbital"


class PairCadence(StrEnum):
    """Pair operational cadence."""

    CONTINUOUS = "continuous"
    INTERMITTENT = "intermittent"


class InterlockType(StrEnum):
    """Cross-partner interlock types."""

    RESIDENT_CONTINUOUS = "resident_continuous"
    ALICIA_ORBITAL = "alicia_orbital"


class ProtocolCategory(StrEnum):
    """Protocol categories."""

    BIOLOGICAL_LIMIT = "biological_limit"
    CO_REGULATION = "co_regulation"
    COGNITIVE_SUPPORT = "cognitive_support"
    RELATIONAL = "relational"
    RESIDENCE_TRANSITION = "residence_transition"
    PROTECTIVE = "protective"
