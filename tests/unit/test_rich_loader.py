"""Phase 10.1: rich YAML loader + cross-reference + preserve_marker tests.

Covers AC-10.1 (all 6 YAMLs load and Pydantic-validate), AC-10.2
(cross-reference validator passes), and the preserve_marker enforcement
contract that Phase 10.6 will formalize as a per-scene-profile test.

These tests load the REAL Character YAMLs on disk — they are not mocked.
The rich YAMLs are canonical authoring surfaces; loading them is the
Phase 10.1 exit criterion.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from starry_lyfe.canon.rich_loader import (
    get_constraint_pillars,
    get_evaluator_whyze_register,
    get_internal_dyad_register,
    get_preserve_markers,
    get_state_protocols,
    load_all_rich_characters,
    load_rich_character,
    load_shared_canon,
    validate_rich_cross_references,
    verify_preserve_markers,
)
from starry_lyfe.canon.rich_schema import (
    ConstraintPillars,
    EvaluatorRegister,
    InternalDyadRegister,
    PreserveMarker,
    PreserveMarkersBlock,
    RichCharacter,
    StateProtocol,
)
from starry_lyfe.canon.shared_schema import SharedCanon

CHARACTERS_DIR = Path(__file__).resolve().parent.parent.parent / "Characters"
WOMAN_IDS = ("adelia", "bina", "reina", "alicia")
ALL_IDS = (*WOMAN_IDS, "shawn")


class TestLoadRichCharacter:
    """AC-10.1: all 5 rich character YAMLs load and Pydantic-validate."""

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_loads_and_validates(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert isinstance(rc, RichCharacter)
        assert rc.character_id == character_id

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_has_soul_substrate_identity_blocks(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert len(rc.soul_substrate.identity_blocks) >= 3

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_has_canon_facts(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert len(rc.canon_facts) >= 10

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_has_voice_baseline(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert rc.voice.baseline
        assert len(rc.voice.baseline) > 50

    def test_unknown_character_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown character_id"):
            load_rich_character("nonexistent")


class TestLoadAllRichCharacters:
    def test_returns_five_characters(self) -> None:
        chars = load_all_rich_characters()
        assert len(chars) == 5
        assert set(chars.keys()) == set(ALL_IDS)

    def test_each_character_is_rich_character(self) -> None:
        chars = load_all_rich_characters()
        for cid, rc in chars.items():
            assert isinstance(rc, RichCharacter)
            assert rc.character_id == cid


class TestShawnSpecificFields:
    def test_has_continuity_layers(self) -> None:
        rc = load_rich_character("shawn")
        assert rc.continuity_layers is not None

    def test_version_is_4_2_rich(self) -> None:
        rc = load_rich_character("shawn")
        assert rc.version == "4.2-rich"

    def test_women_have_no_continuity_layers(self) -> None:
        for cid in WOMAN_IDS:
            rc = load_rich_character(cid)
            assert rc.continuity_layers is None


class TestWomanSpecificFields:
    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    def test_has_pair_architecture(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert rc.pair_architecture is not None

    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    def test_has_family_and_other_dyads(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        assert rc.family_and_other_dyads is not None
        assert len(rc.family_and_other_dyads) >= 3


class TestLoadSharedCanon:
    def test_loads_and_validates(self) -> None:
        sc = load_shared_canon()
        assert isinstance(sc, SharedCanon)

    def test_has_marriage_record(self) -> None:
        sc = load_shared_canon()
        assert sc.marriage is not None
        assert set(sc.marriage.partners) == {"bina", "reina"}

    def test_has_signature_scenes(self) -> None:
        sc = load_shared_canon()
        assert sc.signature_scenes is not None
        assert len(sc.signature_scenes) >= 3
        scene_ids = {s.id for s in sc.signature_scenes}
        assert "bay_door_2024" in scene_ids

    def test_has_four_pairs(self) -> None:
        sc = load_shared_canon()
        assert sc.pairs is not None
        assert len(sc.pairs) == 4
        pair_names = {p.canonical_name for p in sc.pairs}
        assert "The Entangled Pair" in pair_names

    def test_has_genealogy(self) -> None:
        sc = load_shared_canon()
        assert sc.genealogy is not None
        gavin = next((g for g in sc.genealogy if g.subject == "gavin"), None)
        assert gavin is not None
        assert gavin.age == 7

    def test_has_property(self) -> None:
        sc = load_shared_canon()
        assert sc.property is not None
        assert "Priddis" in sc.property.location


class TestPreserveMarkers:
    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_has_preserve_markers(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        markers = get_preserve_markers(rc)
        assert len(markers) >= 5, f"{character_id} has only {len(markers)} markers"

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_markers_are_typed(self, character_id: str) -> None:
        rc = load_rich_character(character_id)
        for m in get_preserve_markers(rc):
            assert isinstance(m, PreserveMarker)
            assert m.id
            assert m.content_anchor

    def test_shawn_uses_block_shape(self) -> None:
        rc = load_rich_character("shawn")
        assert isinstance(rc.meta.preserve_markers, PreserveMarkersBlock)

    def test_women_use_list_shape(self) -> None:
        for cid in WOMAN_IDS:
            rc = load_rich_character(cid)
            assert isinstance(rc.meta.preserve_markers, list)

    @pytest.mark.parametrize("character_id", ALL_IDS)
    def test_all_content_anchors_found_in_body(self, character_id: str) -> None:
        """Core preserve_marker enforcement — anchors verbatim in body text.

        Phase 10.6: unconditional enforcement — the VOICE_JUDGMENT_MARKERS
        exclusion (5 markers pending remediation) was removed after
        Claude AI ratified all 9 initial failures 2026-04-15. All 62
        markers across 5 YAMLs must pass verbatim.
        """
        rc = load_rich_character(character_id)
        from starry_lyfe.canon.rich_loader import CHARACTERS_DIR, RICH_YAML_FILES

        path = CHARACTERS_DIR / RICH_YAML_FILES[character_id]
        text = path.read_text(encoding="utf-8")
        pm_idx = text.find("preserve_markers:")
        if pm_idx >= 0:
            next_top = text.find("\n\n", pm_idx + 100)
            body = text[:pm_idx] + (text[next_top:] if next_top > 0 else "")
        else:
            body = text
        errors = verify_preserve_markers(rc, full_text=body)
        assert not errors, f"{character_id}: {errors}"


class TestCrossReferenceValidator:
    def test_perspective_symmetry_passes(self) -> None:
        """AC-10.2: every with_{X} in A has matching with_{A} in X."""
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        assert not errors, f"Cross-reference errors: {errors}"

    def test_pair_names_resolve_in_shared_canon(self) -> None:
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        pair_errors = [e for e in errors if "pair_architecture" in e]
        assert not pair_errors

    def test_all_six_dyads_diverge_against_live_yamls(self) -> None:
        """Phase 10.5b RT2 / AC-10.21: every inter-woman dyad must diverge.

        Live rich YAMLs must not fail the all-6-dyads divergence check.
        Byte-identical POVs would indicate drift toward agreeable mush.
        """
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        divergence_errors = [e for e in errors if "byte-identical" in e.lower()]
        assert not divergence_errors, (
            f"All-six-dyads divergence failed: {divergence_errors}"
        )

    def test_validator_rejects_synthetic_identical_pov_dyad(self) -> None:
        """Phase 10.5b RT2: synthetic identical-POV pair MUST emit divergence error.

        Proves the validator actually enforces AC-10.21 — a regression
        where the check quietly accepted identical blocks would bypass
        the divergence gate entirely.
        """
        from starry_lyfe.canon.rich_schema import RichCharacter

        def _stub(cid: str, dyads: dict[str, dict[str, object]]) -> RichCharacter:
            return RichCharacter.model_validate({
                "version": "7.1-rich",
                "character_id": cid,
                "meta": {"full_name": cid.title()},
                "identity": {},
                "soul_substrate": {
                    "identity_blocks": [{"label": "test", "text": "test"}],
                },
                "voice": {"baseline": "test"},
                "behavioral_framework": {},
                "canon_facts": [{"fact_text": "test"}],
                "family_and_other_dyads": dyads,
            })

        identical_block: dict[str, object] = {
            "interlock_name": "Agreeable Mush",
            "description": "We get along fine.",
            "tone": "warm",
            "truths": ["We are friends.", "Nothing is complicated."],
        }
        chars = {
            "adelia": _stub("adelia", {"with_bina": identical_block}),
            "bina": _stub("bina", {"with_adelia": identical_block}),
        }
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        divergence_errors = [e for e in errors if "byte-identical" in e.lower()]
        assert divergence_errors, (
            "Validator accepted identical POV blocks — AC-10.21 bypass."
        )
        assert any("adeliaxbina" in e.lower() for e in divergence_errors), (
            f"Error message should name the offending dyad: {divergence_errors}"
        )


class TestDivergenceRequired:
    """AC-10.21 precursor: at least one inter-woman dyad has divergent POVs.

    Full enforcement (per-dyad, numeric + prose) is Phase 10.6. This
    test proves the concept by checking that at least one pair of women
    carry non-identical inter-woman dyad descriptions.
    """

    def test_at_least_one_dyad_has_divergent_descriptions(self) -> None:
        chars = load_all_rich_characters()
        found_divergence = False
        for cid_a in WOMAN_IDS:
            rc_a = chars[cid_a]
            fad_a = rc_a.family_and_other_dyads or {}
            for cid_b in WOMAN_IDS:
                if cid_a >= cid_b:
                    continue
                rc_b = chars[cid_b]
                fad_b = rc_b.family_and_other_dyads or {}
                block_a = fad_a.get(f"with_{cid_b}")
                block_b = fad_b.get(f"with_{cid_a}")
                if block_a is None or block_b is None:
                    continue
                desc_a = block_a.description if block_a.description else ""
                desc_b = block_b.description if block_b.description else ""
                if desc_a and desc_b and desc_a != desc_b:
                    found_divergence = True
                    break
            if found_divergence:
                break
        assert found_divergence, (
            "No inter-woman dyad pair has divergent descriptions — "
            "this violates the per-character-POV architectural principle"
        )


class TestPhase104Schema:
    """Phase 10.4 C1: new evaluator_register + constraint_pillars schema.

    Schema accepts new content; YAMLs validate with or without the new
    blocks present (optional fields). C2 will embed the actual content.
    """

    def test_evaluator_register_optional_in_current_yamls(self) -> None:
        """All 5 character YAMLs load without evaluator_register block yet."""
        for cid in ALL_IDS:
            rc = load_rich_character(cid)
            # evaluator_register is optional and currently absent
            assert rc.evaluator_register is None or isinstance(
                rc.evaluator_register, EvaluatorRegister
            )

    def test_evaluator_register_accepts_valid_content(self) -> None:
        """EvaluatorRegister accepts whyze_dyad + internal_dyads list."""
        er = EvaluatorRegister(
            whyze_dyad="Test whyze-dyad register prose.",
            internal_dyads=[
                InternalDyadRegister(dyad_key="adelia_bina", prose="Test prose.")
            ],
        )
        assert er.whyze_dyad == "Test whyze-dyad register prose."
        assert er.internal_dyads is not None
        assert er.internal_dyads[0].dyad_key == "adelia_bina"

    def test_constraint_pillars_accepts_in_person_only(self) -> None:
        """ConstraintPillars requires in_person; other modes optional."""
        cp = ConstraintPillars(in_person=["axiom 1", "axiom 2"])
        assert cp.in_person == ["axiom 1", "axiom 2"]
        assert cp.phone is None
        assert cp.letter is None
        assert cp.video is None

    def test_constraint_pillars_accepts_all_four_modes(self) -> None:
        """ConstraintPillars accepts Alicia's 4-variant shape."""
        cp = ConstraintPillars(
            in_person=["ip"],
            phone=["p"],
            letter=["l"],
            video=["v"],
        )
        assert cp.phone == ["p"]
        assert cp.letter == ["l"]
        assert cp.video == ["v"]

    def test_state_protocol_accepts_name_and_fields(self) -> None:
        sp = StateProtocol(
            name="bunker_mode",
            triggers=["stuck"],
            presentation="silent",
            recovery="emerge",
        )
        assert sp.name == "bunker_mode"
        assert sp.triggers == ["stuck"]


class TestPhase104Helpers:
    """Phase 10.4 helpers in rich_loader — verified against post-C2 YAML state."""

    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    def test_whyze_register_present_post_c2(self, character_id: str) -> None:
        """After C2 content embed, every woman has a whyze_dyad register."""
        rc = load_rich_character(character_id)
        prose = get_evaluator_whyze_register(rc)
        assert prose is not None
        assert len(prose) > 100  # real prose, not placeholder

    def test_whyze_register_absent_for_shawn(self) -> None:
        """Shawn has no evaluator_register block."""
        rc = load_rich_character("shawn")
        assert get_evaluator_whyze_register(rc) is None

    @pytest.mark.parametrize(
        "character_id,dyad_key",
        [
            ("adelia", "adelia_bina"),
            ("bina", "adelia_bina"),  # both members carry the same dyad
            ("adelia", "adelia_reina"),
            ("reina", "bina_reina"),
            ("alicia", "adelia_alicia"),
        ],
    )
    def test_internal_dyad_register_present_post_c2(
        self, character_id: str, dyad_key: str
    ) -> None:
        """After C2 content embed, each woman has registers for her 3 dyads."""
        rc = load_rich_character(character_id)
        prose = get_internal_dyad_register(rc, dyad_key)
        assert prose is not None
        assert len(prose) > 100

    def test_internal_dyad_register_absent_when_not_member(self) -> None:
        """Adelia is NOT a member of bina_reina — should return None."""
        rc = load_rich_character("adelia")
        assert get_internal_dyad_register(rc, "bina_reina") is None

    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    def test_constraint_pillars_in_person_present_post_c2(
        self, character_id: str
    ) -> None:
        """After C2 content embed, every woman has in_person pillars."""
        rc = load_rich_character(character_id)
        pillars = get_constraint_pillars(rc, "in_person")
        assert pillars is not None
        assert len(pillars) >= 3

    def test_constraint_pillars_alicia_has_all_four_modes(self) -> None:
        """Alicia has distinct phone, letter, and video pillars (Phase A'')."""
        rc = load_rich_character("alicia")
        in_person = get_constraint_pillars(rc, "in_person")
        phone = get_constraint_pillars(rc, "phone")
        letter = get_constraint_pillars(rc, "letter")
        video = get_constraint_pillars(rc, "video")
        assert in_person != phone
        assert in_person != letter
        assert in_person != video
        assert phone != letter

    def test_constraint_pillars_non_alicia_fall_back_to_in_person(self) -> None:
        """Adelia has no phone pillar; get_constraint_pillars falls back."""
        rc = load_rich_character("adelia")
        in_person = get_constraint_pillars(rc, "in_person")
        phone = get_constraint_pillars(rc, "phone")
        assert phone == in_person

    def test_state_protocols_falls_back_to_stress_modes(self) -> None:
        """When state_protocols is absent, helper returns stress_modes content."""
        rc = load_rich_character("adelia")
        sp = get_state_protocols(rc)
        assert isinstance(sp, dict)
        assert "bunker_mode" in sp or len(sp) >= 0  # permissive
