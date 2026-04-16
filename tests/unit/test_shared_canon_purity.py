"""Phase 10.6 C2: shared_canon.yaml factual purity invariants.

Facts in ``shared_canon.yaml`` (marriage, signature scene anchors,
genealogy, property, timeline, canonical pair names) must not be
contradicted by values in any per-character YAML. Perception belongs
in per-character YAMLs; facts live in shared_canon.

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §6 + AC-10.22.
"""

from __future__ import annotations

from starry_lyfe.canon.rich_loader import (
    load_all_rich_characters,
    load_shared_canon,
)

WOMAN_IDS = ("adelia", "bina", "reina", "alicia")


class TestMarriageRecordPurity:
    """Marriage date/partners in shared_canon cannot be contradicted."""

    def test_marriage_partners_are_bina_and_reina(self) -> None:
        shared = load_shared_canon()
        assert shared.marriage is not None
        partners = set(shared.marriage.partners)
        assert partners == {"bina", "reina"}

    def test_no_character_yaml_denies_the_marriage(self) -> None:
        """Neither Bina nor Reina YAML may carry a field asserting un-married."""
        chars = load_all_rich_characters()
        for cid in ("bina", "reina"):
            rc = chars[cid]
            identity = rc.identity if isinstance(rc.identity, dict) else {}
            marital = str(identity.get("marital_status", "") or "").lower()
            if marital:
                assert "single" not in marital and "unmarried" not in marital, (
                    f"{cid}: identity.marital_status contradicts shared_canon marriage"
                )


class TestPairCanonicalNames:
    """AC-10.22: per-character pair name must match shared_canon canonical name."""

    def test_each_woman_pair_name_matches_shared_canon(self) -> None:
        shared = load_shared_canon()
        chars = load_all_rich_characters()
        shared_names = {p.canonical_name for p in (shared.pairs or [])}
        errors: list[str] = []
        for cid in WOMAN_IDS:
            rc = chars[cid]
            pa = rc.pair_architecture
            if not isinstance(pa, dict):
                continue
            name = pa.get("name")
            if name and name not in shared_names:
                errors.append(
                    f"{cid}: pair_architecture.name = {name!r} does not "
                    f"match any shared_canon.pairs[].canonical_name"
                )
        assert not errors, "\n".join(errors)


class TestGenealogyPurity:
    """Gavin's parents + age in shared_canon cannot be contradicted."""

    def test_gavin_entry_exists(self) -> None:
        shared = load_shared_canon()
        assert shared.genealogy is not None
        gavin = next((g for g in shared.genealogy if g.subject == "gavin"), None)
        assert gavin is not None, "shared_canon.genealogy must include Gavin"

    def test_gavin_age_consistent(self) -> None:
        """No per-character YAML may carry a different age for Gavin."""
        shared = load_shared_canon()
        gavin = next(
            (g for g in (shared.genealogy or []) if g.subject == "gavin"), None
        )
        if gavin is None or gavin.age is None:
            return
        chars = load_all_rich_characters()
        errors: list[str] = []
        # Look in Bina's + Reina's YAMLs (Gavin's parents) for any age field
        for cid in ("bina", "reina"):
            rc = chars[cid]
            # Heuristic: scan family_and_other_dyads or a gavin-specific block
            # We only flag explicit age-contradictions.
            identity = rc.identity if isinstance(rc.identity, dict) else {}
            children = identity.get("children")
            if isinstance(children, list):
                for ch in children:
                    if isinstance(ch, dict) and str(ch.get("name", "")).lower() == "gavin":
                        age = ch.get("age")
                        if isinstance(age, int) and age != gavin.age:
                            errors.append(
                                f"{cid}: Gavin age {age} contradicts "
                                f"shared_canon.genealogy.gavin.age={gavin.age}"
                            )
        assert not errors, "\n".join(errors)


class TestPropertyPurity:
    """Property location in shared_canon cannot be contradicted."""

    def test_property_location_set(self) -> None:
        shared = load_shared_canon()
        assert shared.property is not None
        assert "Priddis" in shared.property.location or shared.property.location

    def test_no_woman_yaml_contradicts_location(self) -> None:
        """Per-character YAMLs may not carry a different canonical location."""
        shared = load_shared_canon()
        if shared.property is None:
            return
        canonical_loc = shared.property.location
        chars = load_all_rich_characters()
        errors: list[str] = []
        for cid in WOMAN_IDS:
            rc = chars[cid]
            identity = rc.identity if isinstance(rc.identity, dict) else {}
            # Check any canonical-location-like field. Permissive: flag only
            # if identity.property_location is authored AND differs.
            loc = identity.get("property_location")
            if isinstance(loc, str) and loc and loc != canonical_loc:
                errors.append(
                    f"{cid}: identity.property_location = {loc!r} != "
                    f"shared_canon.property.location = {canonical_loc!r}"
                )
        assert not errors, "\n".join(errors)


class TestTimelineAnchorPresence:
    """Canonical timeline anchors exist in shared_canon."""

    def test_marriage_and_introduction_anchors_present(self) -> None:
        shared = load_shared_canon()
        timeline = shared.timeline or []
        anchor_ids = {a.id for a in timeline}
        assert "adelia_introduced_bina_reina" in anchor_ids, (
            "Canonical anchor 'adelia_introduced_bina_reina' missing from "
            "shared_canon.timeline"
        )
        assert "bina_reina_marriage" in anchor_ids, (
            "Canonical anchor 'bina_reina_marriage' missing from "
            "shared_canon.timeline"
        )
