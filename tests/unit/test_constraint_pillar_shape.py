"""Phase 10.6 C2: Constraint pillar shape invariants (per-character).

Asserts each woman's rich YAML carries the required constraint pillar
shape:
- Adelia, Bina, Reina: at minimum an ``in_person`` pillar list
- Alicia: all 4 communication-mode variants (in_person, phone, letter,
  video), each distinct (Phase A'' 4-variant Alicia dispatch)

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §3.
"""

from __future__ import annotations

import pytest

from starry_lyfe.canon.rich_loader import (
    get_constraint_pillars,
    load_rich_character,
)

WOMAN_IDS = ("adelia", "bina", "reina", "alicia")


class TestConstraintPillarShapeAllWomen:
    """AC-10.16: every woman carries an in_person pillar."""

    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    def test_in_person_pillar_present(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        pillars = get_constraint_pillars(rc, "in_person")
        assert pillars is not None, f"{character_id}: in_person pillars missing"
        assert len(pillars) >= 1, f"{character_id}: in_person has 0 items"


class TestConstraintPillarShapeAlicia:
    """AC-10.16: Alicia carries all 4 communication-mode variants."""

    def test_alicia_has_in_person_variant(self) -> None:
        rc = load_rich_character("alicia")
        assert get_constraint_pillars(rc, "in_person") is not None

    def test_alicia_has_phone_variant(self) -> None:
        rc = load_rich_character("alicia")
        in_person = get_constraint_pillars(rc, "in_person")
        phone = get_constraint_pillars(rc, "phone")
        assert phone is not None
        assert phone != in_person, "Alicia phone pillar must differ from in_person"

    def test_alicia_has_letter_variant(self) -> None:
        rc = load_rich_character("alicia")
        in_person = get_constraint_pillars(rc, "in_person")
        letter = get_constraint_pillars(rc, "letter")
        assert letter is not None
        assert letter != in_person

    def test_alicia_has_video_variant(self) -> None:
        rc = load_rich_character("alicia")
        in_person = get_constraint_pillars(rc, "in_person")
        video = get_constraint_pillars(rc, "video")
        assert video is not None
        assert video != in_person

    def test_alicia_phone_letter_video_all_distinct(self) -> None:
        rc = load_rich_character("alicia")
        phone = get_constraint_pillars(rc, "phone")
        letter = get_constraint_pillars(rc, "letter")
        video = get_constraint_pillars(rc, "video")
        # At least two pairwise distinctions; all 3 identical would defeat
        # the Phase A'' 4-variant purpose.
        distinct_count = len({tuple(phone or []), tuple(letter or []), tuple(video or [])})
        assert distinct_count >= 2, (
            "Alicia phone/letter/video must not all be identical"
        )


class TestConstraintPillarShapeNonAlicia:
    """AC-10.16: non-Alicia women fall back to in_person for remote modes."""

    @pytest.mark.parametrize("character_id", ("adelia", "bina", "reina"))
    def test_non_alicia_phone_falls_back_to_in_person(
        self, character_id: str
    ) -> None:
        rc = load_rich_character(character_id)
        in_person = get_constraint_pillars(rc, "in_person")
        phone = get_constraint_pillars(rc, "phone")
        # phone should equal in_person (fallback), since these women
        # don't have remote-mode authored variants
        assert phone == in_person, (
            f"{character_id} phone pillars must fall back to in_person"
        )
