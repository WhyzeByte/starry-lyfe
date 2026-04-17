"""Phase 10.7 — enumerate the 10 relationships the QA judge inspects.

10 = 6 inter-woman dyads + 4 woman-Whyze pairs.

The 6 inter-woman dyad keys are deterministic from the 4 women in
``CharacterID``: every unordered pair (alphabetical order). The 4
woman-Whyze pair keys are the canonical pair names from
``shared_canon.pairs[]`` (per Phase 10.5b R2-F3 + 10.5c §2.5 single-source-of-truth).

Each relationship_key is the durable identifier the QA log + pinning
table key on, so the 10 names below ARE the canonical taxonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ...canon.loader import Canon
from ...canon.schemas.enums import CharacterID

WOMEN: tuple[CharacterID, ...] = (
    CharacterID.ADELIA,
    CharacterID.BINA,
    CharacterID.REINA,
    CharacterID.ALICIA,
)

# Canonical seniority order for dyad-key construction. Matches the keys
# already authored in `Characters/shared_canon.yaml::dyads_baseline`:
# adelia/bina/reina/alicia precedence (Adelia first, then resident pair,
# then orbital Alicia). Keys join lower-rank first.
_DYAD_KEY_PRECEDENCE: dict[str, int] = {
    CharacterID.ADELIA.value: 0,
    CharacterID.BINA.value: 1,
    CharacterID.REINA.value: 2,
    CharacterID.ALICIA.value: 3,
}


@dataclass(frozen=True)
class Relationship:
    """One QA-tracked relationship.

    ``relationship_key`` is the durable id used by ``dreams_qa_log`` +
    ``dyad_state_pins``. ``relationship_kind`` distinguishes inter-woman
    (both POVs are women) from woman-whyze pair (one POV is a woman,
    the other is the operator).
    """

    relationship_key: str
    relationship_kind: str  # "inter_woman" | "woman_whyze"
    pov_a: str
    pov_b: str  # "whyze" for woman_whyze; the other woman id for inter_woman


def _inter_woman_dyad_key(a: CharacterID, b: CharacterID) -> str:
    """Symmetric key — precedence-ordered to match shared_canon.dyads_baseline keys."""
    lo, hi = sorted(
        [a.value, b.value],
        key=lambda v: _DYAD_KEY_PRECEDENCE.get(v, 99),
    )
    return f"{lo}_{hi}"


def enumerate_inter_woman_dyads() -> list[Relationship]:
    """6 unordered pairs across the 4 women.

    Ordering matches `Characters/shared_canon.yaml::dyads_baseline` keys:
    adelia/bina/reina/alicia seniority, lower-rank first in the joined key.
    """
    out: list[Relationship] = []
    for a, b in combinations(WOMEN, 2):
        lo, hi = sorted(
            [a.value, b.value],
            key=lambda v: _DYAD_KEY_PRECEDENCE.get(v, 99),
        )
        out.append(
            Relationship(
                relationship_key=f"{lo}_{hi}",
                relationship_kind="inter_woman",
                pov_a=lo,
                pov_b=hi,
            )
        )
    return out


def enumerate_woman_whyze_pairs(canon: Canon) -> list[Relationship]:
    """4 pair codenames from ``canon.shared.pairs[]`` (Phase 10.5c terminal source).

    Returns one Relationship per pair, with relationship_key = ``whyze_<woman_id>``
    so the keying convention matches ``dyads_baseline`` (whyze_adelia, etc.).
    """
    if not canon.shared.pairs:
        msg = "canon.shared.pairs is empty — Phase 10.5c hydration broken"
        raise RuntimeError(msg)
    out: list[Relationship] = []
    for pair in canon.shared.pairs:
        woman_id = (pair.character or "").strip()
        if not woman_id:
            continue
        out.append(
            Relationship(
                relationship_key=f"whyze_{woman_id}",
                relationship_kind="woman_whyze",
                pov_a="whyze",
                pov_b=woman_id,
            )
        )
    return out


def enumerate_all(canon: Canon) -> list[Relationship]:
    """All 10 QA-tracked relationships. Order: inter-woman first, then pairs."""
    return enumerate_inter_woman_dyads() + enumerate_woman_whyze_pairs(canon)
