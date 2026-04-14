"""Gate 1 verification tests for Phase 1 canon YAML scaffolding."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from starry_lyfe.canon import validator as canon_validator
from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.schemas.dyads import DimensionBaseline, Dyad, DyadDimensions
from starry_lyfe.canon.schemas.enums import CharacterID, DyadType, InterlockType, PairName
from starry_lyfe.canon.schemas.interlocks import Interlock
from starry_lyfe.canon.schemas.protocols import (
    ALLOWED_PROTOCOL_EXTENSION_SOURCES,
    VISION_SECTION_7_PROTOCOLS,
    CanonProtocols,
)


def test_all_yaml_files_parse_and_validate() -> None:
    """Every YAML file in canon/ loads without error through its Pydantic schema."""
    canon = load_all_canon()
    assert canon is not None


def test_character_count_is_exactly_five() -> None:
    """4 women + 1 operator = 5 total people."""
    canon = load_all_canon()
    assert len(canon.characters.characters) == 4
    assert len(canon.characters.operator) == 1


def test_pair_count_is_exactly_four() -> None:
    """Entangled, Circuit, Kinetic, Solstice."""
    canon = load_all_canon()
    assert len(canon.pairs.pairs) == 4
    assert set(canon.pairs.pairs.keys()) == set(PairName)


def test_memory_tier_count_is_exactly_seven() -> None:
    """Canon Facts through Transient Somatic State."""
    canon = load_all_canon()
    assert len(canon.dyads.memory_tiers) == 7
    tier_numbers = [t.tier for t in canon.dyads.memory_tiers]
    assert tier_numbers == [1, 2, 3, 4, 5, 6, 7]


def test_protocol_inventory_is_vision_set_plus_sourced_extensions() -> None:
    """The real canon is the Vision set plus explicitly sourced extensions only."""
    canon = load_all_canon()
    protocol_keys = set(canon.protocols.protocols.keys())
    missing = VISION_SECTION_7_PROTOCOLS - protocol_keys
    assert not missing, f"Missing Vision section 7 protocols: {sorted(missing)}"

    extra_protocols = protocol_keys - VISION_SECTION_7_PROTOCOLS
    assert extra_protocols == {"warlord_mode"}
    for protocol_name in extra_protocols:
        assert canon.protocols.protocols[protocol_name].source in ALLOWED_PROTOCOL_EXTENSION_SOURCES


def test_interlock_count_is_exactly_six() -> None:
    """Six cross-partner interlocks."""
    canon = load_all_canon()
    assert len(canon.interlocks.interlocks) == 6


def test_dyad_count_is_ten() -> None:
    """6 inter-woman + 4 Whyze = 10 total dyads."""
    canon = load_all_canon()
    assert len(canon.dyads.dyads) == 10

    inter_woman = [d for d in canon.dyads.dyads.values() if d.type.value == "inter_woman"]
    whyze_pairs = [d for d in canon.dyads.dyads.values() if d.type.value == "whyze_pair"]
    assert len(inter_woman) == 6
    assert len(whyze_pairs) == 4


def test_alicia_is_resident_with_operational_travel() -> None:
    """Alicia is a resident who travels frequently for consular operations."""
    canon = load_all_canon()
    alicia = canon.characters.characters[CharacterID.ALICIA]
    assert alicia.is_resident is True
    assert alicia.operational_travel is not None


def test_alicia_inference_parameters() -> None:
    """Alicia: temp 0.73-0.78, think_lightly, low frequency_penalty."""
    canon = load_all_canon()
    alicia_voice = canon.voice_parameters.voice_parameters[CharacterID.ALICIA]
    low, high = alicia_voice.temperature.range
    assert low == 0.73
    assert high == 0.78
    assert alicia_voice.temperature.midpoint == 0.75
    assert alicia_voice.thinking_effort.value == "think_lightly"
    assert alicia_voice.distinctive_sampling == "low_frequency_penalty"
    assert alicia_voice.frequency_penalty > 0.0


def test_alicia_orbital_dyads_have_active_flag() -> None:
    """Alicia-orbital dyads have is_currently_active=false."""
    canon = load_all_canon()
    orbital_dyads = [
        d for d in canon.dyads.dyads.values()
        if d.subtype is not None and d.subtype.value == "alicia_orbital"
    ]
    assert len(orbital_dyads) == 3
    for dyad in orbital_dyads:
        assert dyad.is_currently_active is False


def test_cross_file_referential_integrity() -> None:
    """All cross-file references resolve."""
    errors = canon_validator.validate_cross_references()
    assert not errors, "Cross-reference errors:\n" + "\n".join(f"  - {e}" for e in errors)


def test_v70_residue_grep_returns_zero_matches(src_dir: Path) -> None:
    """Re-run residue grep as part of Gate 1 suite."""
    from tests.unit.test_residue_grep import _scan_src_for_residue

    matches = _scan_src_for_residue(src_dir)
    assert not matches, f"v7.0 residue found: {matches}"


def test_emdash_ban_passes(canon_dir: Path) -> None:
    """Re-run em-dash ban as part of Gate 1 suite."""
    em_dash = "\u2014"
    en_dash = "\u2013"
    for filepath in sorted(canon_dir.glob("*.yaml")):
        text = filepath.read_text(encoding="utf-8")
        assert em_dash not in text, f"Em-dash found in {filepath.name}"
        assert en_dash not in text, f"En-dash found in {filepath.name}"


def test_bina_reina_married() -> None:
    """Bina and Reina are married to each other."""
    canon = load_all_canon()
    bina = canon.characters.characters[CharacterID.BINA]
    reina = canon.characters.characters[CharacterID.REINA]
    assert bina.spouse == "reina"
    assert reina.spouse == "bina"


def test_temperature_ordering() -> None:
    """Temperature spread: Adelia > Alicia > Reina > Bina."""
    canon = load_all_canon()
    vp = canon.voice_parameters.voice_parameters
    assert vp[CharacterID.ADELIA].temperature.midpoint > vp[CharacterID.ALICIA].temperature.midpoint
    assert vp[CharacterID.ALICIA].temperature.midpoint > vp[CharacterID.REINA].temperature.midpoint
    assert vp[CharacterID.REINA].temperature.midpoint > vp[CharacterID.BINA].temperature.midpoint


# --- Negative tests for validator hardening (R-01, R-02, R-05) ---

_STUB_DIMS = DyadDimensions(
    trust=DimensionBaseline(baseline=0.5, min=0.0, max=1.0),
    intimacy=DimensionBaseline(baseline=0.5, min=0.0, max=1.0),
    conflict=DimensionBaseline(baseline=0.1, min=0.0, max=1.0),
    unresolved_tension=DimensionBaseline(baseline=0.1, min=0.0, max=1.0),
    repair_history=DimensionBaseline(baseline=0.5, min=0.0, max=1.0),
)


def test_dyad_rejects_duplicate_members() -> None:
    """A dyad with two identical members must fail validation."""
    with pytest.raises(ValidationError, match="distinct"):
        Dyad(members=["adelia", "adelia"], type=DyadType.INTER_WOMAN, dimensions=_STUB_DIMS)


def test_interlock_rejects_duplicate_members() -> None:
    """An interlock with two identical members must fail validation."""
    with pytest.raises(ValidationError, match="distinct"):
        Interlock(
            name="Bad Interlock",
            members=["bina", "bina"],
            description="test",
            tone="test",
            type=InterlockType.RESIDENT_CONTINUOUS,
        )


def test_protocol_extension_requires_source_tag(canon_dir: Path) -> None:
    """Extra protocols must be explicitly tagged with an approved source."""
    data = yaml.safe_load((canon_dir / "protocols.yaml").read_text(encoding="utf-8"))
    data["protocols"]["surprise_protocol"] = {
        "name": "Surprise Protocol",
        "primary_character": "adelia",
        "secondary_characters": [],
        "category": "protective",
        "description": "A test-only extension without source metadata.",
        "entry_conditions": "Never",
    }

    with pytest.raises(ValidationError, match="must declare"):
        CanonProtocols.model_validate(data)


def test_validator_rejects_missing_dyad_interlock() -> None:
    """Dyad interlock references must resolve to interlocks.yaml keys."""
    canon = load_all_canon()
    del canon.interlocks.interlocks["anchor_dynamic"]

    errors = canon_validator.validate_cross_references(canon)
    assert "dyads.yaml: dyad 'adelia_bina' interlock 'anchor_dynamic' not in interlocks.yaml" in errors


def test_validator_rejects_missing_whyze_pair_key() -> None:
    """Whyze-pair dyads must point at a defined pair key."""
    canon = load_all_canon()
    del canon.pairs.pairs[PairName.ENTANGLED]

    errors = canon_validator.validate_cross_references(canon)
    assert "dyads.yaml: dyad 'whyze_adelia' pair 'entangled' not in pairs.yaml" in errors


def test_validator_rejects_unknown_recovery_architecture_character() -> None:
    """Recovery responders must resolve to known household members."""
    canon = load_all_canon()
    recovery = canon.protocols.protocols["bunker_mode"].recovery_architecture
    assert recovery is not None
    recovery.first_responder.character = "ghost"

    errors = canon_validator.validate_cross_references(canon)
    assert (
        "protocols.yaml: protocol 'bunker_mode' recovery first_responder "
        "references unknown character 'ghost'"
    ) in errors


# --- C3 remediation: load_all_canon(validate=True) fails on corruption ---


def test_load_all_canon_with_validate_true_raises_on_corruption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """load_all_canon(validate=True) must raise when cross-references are broken."""
    from starry_lyfe.canon import loader as canon_loader

    # Load a real interlocks instance then delete a referenced key, mirroring
    # the existing monkeypatch pattern used in the validator tests above.
    base_interlocks = canon_loader.load_interlocks()
    del base_interlocks.interlocks["anchor_dynamic"]
    monkeypatch.setattr(canon_loader, "load_interlocks", lambda: base_interlocks)

    with pytest.raises(ValueError, match="Canon validation failed"):
        canon_loader.load_all_canon(validate=True)


def test_load_all_canon_with_validate_false_skips_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """load_all_canon(validate=False) must NOT invoke validator (recursion safety)."""
    from starry_lyfe.canon import loader as canon_loader
    from starry_lyfe.canon import validator as cv

    call_count = {"n": 0}

    def counting_validator(canon: object | None = None) -> list[str]:
        call_count["n"] += 1
        return []

    monkeypatch.setattr(cv, "validate_cross_references", counting_validator)
    canon_loader.load_all_canon(validate=False)
    assert call_count["n"] == 0


def test_load_all_canon_default_validates() -> None:
    """load_all_canon() with no args must validate by default."""
    # Canon is currently valid, so this should succeed without error.
    canon = load_all_canon()
    assert canon is not None


# --- C4 remediation: assert_complete_character_coverage helper ---


def test_c4_assert_complete_character_coverage_catches_missing() -> None:
    """Missing character in a per-character dict must raise."""
    from starry_lyfe.canon.schemas.enums import assert_complete_character_coverage

    with pytest.raises(ValueError, match="missing"):
        assert_complete_character_coverage(
            {"adelia": 1, "bina": 1, "reina": 1}, "test_dict"
        )


def test_c4_assert_complete_character_coverage_catches_extra() -> None:
    """Extra character key in a per-character dict must raise."""
    from starry_lyfe.canon.schemas.enums import assert_complete_character_coverage

    with pytest.raises(ValueError, match="extra"):
        assert_complete_character_coverage(
            {"adelia": 1, "bina": 1, "reina": 1, "alicia": 1, "shawn": 1},
            "test_dict",
        )


def test_c4_assert_complete_character_coverage_passes_for_complete_dict() -> None:
    """Exact coverage of CharacterID must pass."""
    from starry_lyfe.canon.schemas.enums import assert_complete_character_coverage

    assert_complete_character_coverage(
        {"adelia": 1, "bina": 1, "reina": 1, "alicia": 1}, "test_dict"
    )


def test_c4_assert_complete_character_coverage_works_on_sets() -> None:
    """Helper accepts sets in addition to dicts."""
    from starry_lyfe.canon.schemas.enums import assert_complete_character_coverage

    assert_complete_character_coverage(
        {"adelia", "bina", "reina", "alicia"}, "test_set"
    )
    with pytest.raises(ValueError, match="missing"):
        assert_complete_character_coverage({"adelia", "bina"}, "test_set")
