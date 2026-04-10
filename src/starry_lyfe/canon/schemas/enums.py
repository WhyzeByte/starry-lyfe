"""Shared enum types for canon YAML schemas."""

from enum import StrEnum


class CharacterID(StrEnum):
    """The four canonical characters."""

    ADELIA = "adelia"
    BINA = "bina"
    REINA = "reina"
    ALICIA = "alicia"


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
