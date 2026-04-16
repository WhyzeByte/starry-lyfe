"""Phase 10.6 C2: Cross-reference integrity invariants.

Consolidates and extends the cross-reference validation from
``test_rich_loader.py``:

1. Perspective symmetry: every ``family_and_other_dyads.with_{X}`` in
   character A's YAML has a matching ``with_{A}`` in character X.
2. Pair POV resolution: every woman's ``pair_architecture.name``
   resolves to an entry in ``shared_canon.yaml::pairs[].canonical_name``.
3. Signature scene anchor resolution: every ``anchor_id`` referenced
   by a per-character POV block resolves to an entry in
   ``shared_canon.yaml::signature_scenes[].id``.

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §4 + AC-10.2.
"""

from __future__ import annotations

from starry_lyfe.canon.rich_loader import (
    load_all_rich_characters,
    load_shared_canon,
    validate_rich_cross_references,
)

WOMAN_IDS = ("adelia", "bina", "reina", "alicia")


class TestPerspectiveSymmetry:
    """AC-10.2: every with_{X} in A has matching with_{A} in X."""

    def test_validator_returns_zero_errors(self) -> None:
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        # Filter to perspective-symmetry errors only.
        sym_errors = [e for e in errors if "symmetry" in e.lower() or "with_" in e]
        assert not sym_errors, f"Perspective symmetry errors: {sym_errors}"


class TestPairPOVResolution:
    """AC-10.2: every pair name resolves in shared_canon.yaml.pairs."""

    def test_validator_returns_zero_pair_errors(self) -> None:
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        errors = validate_rich_cross_references(chars, shared)
        pair_errors = [e for e in errors if "pair_architecture" in e]
        assert not pair_errors, f"Pair POV errors: {pair_errors}"

    def test_each_woman_has_pair_name_field(self) -> None:
        chars = load_all_rich_characters()
        for cid in WOMAN_IDS:
            rc = chars[cid]
            pa = rc.pair_architecture
            assert pa is not None, f"{cid}: pair_architecture is None"
            assert pa.name, f"{cid}: pair_architecture.name missing"


class TestSignatureSceneAnchorResolution:
    """AC-10.2 extended: signature scene anchor_ids resolve in shared_canon.

    Current rich YAMLs may not carry typed ``signature_scenes[].anchor_id``
    references under ``relationships.{other}.signature_scenes[]`` yet —
    the schema accepts them via extra=allow. When authored, anchor_ids
    must resolve. Test walks every woman's family_and_other_dyads blocks
    looking for anchor_id fields; each must resolve in shared_canon.
    """

    def test_anchor_ids_resolve_when_present(self) -> None:
        chars = load_all_rich_characters()
        shared = load_shared_canon()
        shared_scene_ids = {s.id for s in (shared.signature_scenes or [])}
        errors: list[str] = []
        for cid in WOMAN_IDS:
            rc = chars[cid]
            fad = rc.family_and_other_dyads or {}
            for other_key, block in fad.items():
                # block may be InterWomanDyad with extra fields
                extras = getattr(block, "__pydantic_extra__", None) or {}
                # Check common places anchor_ids might live
                for field_name in ("signature_scenes", "anchor_ids"):
                    refs = extras.get(field_name)
                    if isinstance(refs, list):
                        for ref in refs:
                            if isinstance(ref, dict):
                                aid = ref.get("anchor_id")
                                if aid and aid not in shared_scene_ids:
                                    errors.append(
                                        f"{cid}::{other_key}::{field_name}: "
                                        f"anchor_id {aid!r} does not resolve "
                                        f"in shared_canon.yaml"
                                    )
        assert not errors, f"Scene anchor resolution errors: {errors}"


class TestSharedCanonPairsCoverage:
    """shared_canon.yaml carries all 4 canonical pair names."""

    def test_four_pairs_present(self) -> None:
        shared = load_shared_canon()
        assert shared.pairs is not None
        pair_names = {p.canonical_name for p in shared.pairs}
        expected = {
            "The Entangled Pair",
            "The Circuit Pair",
            "The Kinetic Pair",
            "The Solstice Pair",
        }
        assert pair_names >= expected, (
            f"shared_canon missing canonical pairs: {expected - pair_names}"
        )
