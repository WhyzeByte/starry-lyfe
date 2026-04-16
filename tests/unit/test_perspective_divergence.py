"""Phase 10.6 C2: Per-dyad perspective divergence enforcement.

Per-character POV authoring is canonical: two women's perspectives on
the same relationship are expected to diverge. Identical POVs indicate
drift toward "agreeable mush" and FAIL the test.

For each of the 6 inter-woman dyads, assert EITHER:
- At least one numeric field (trust/intimacy/conflict/repair_history)
  differs by ≥0.05 between the two members' POV blocks, OR
- At least one lived-mechanic prose block (description, tone, truths
  text) is non-identical between the two POVs.

When POV blocks don't carry typed numeric scores, prose-divergence is
the required path.

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §5 + AC-10.21.
"""

from __future__ import annotations

import pytest

from starry_lyfe.canon.rich_loader import load_all_rich_characters

INTER_WOMAN_DYADS: list[tuple[str, str]] = [
    ("adelia", "bina"),
    ("bina", "reina"),
    ("adelia", "reina"),
    ("adelia", "alicia"),
    ("bina", "alicia"),
    ("reina", "alicia"),
]


def _pov_block(character_id: str, other_id: str) -> object:
    chars = load_all_rich_characters()
    rc = chars[character_id]
    fad = rc.family_and_other_dyads or {}
    return fad.get(f"with_{other_id}")


def _truths_text(block: object) -> str:
    """Normalize `truths` to a single string for comparison."""
    if block is None:
        return ""
    truths = getattr(block, "truths", None)
    if isinstance(truths, list):
        return "\n".join(str(t) for t in truths)
    if isinstance(truths, str):
        return truths
    return ""


def _prose_signature(block: object) -> tuple[str, str, str]:
    if block is None:
        return ("", "", "")
    return (
        str(getattr(block, "description", "") or ""),
        str(getattr(block, "tone", "") or ""),
        _truths_text(block),
    )


def _numeric_fields(block: object) -> dict[str, float]:
    """Extract typed trust/intimacy/conflict/repair_history if present."""
    if block is None:
        return {}
    out: dict[str, float] = {}
    extras = getattr(block, "__pydantic_extra__", None) or {}
    for key in ("trust", "intimacy", "conflict", "repair_history"):
        v = extras.get(key)
        if isinstance(v, (int, float)):
            out[key] = float(v)
    return out


class TestPerDyadDivergence:
    """AC-10.21: each dyad has at least one divergent POV field."""

    @pytest.mark.parametrize("cid_a,cid_b", INTER_WOMAN_DYADS)
    def test_dyad_has_divergent_povs(self, cid_a: str, cid_b: str) -> None:
        block_a = _pov_block(cid_a, cid_b)
        block_b = _pov_block(cid_b, cid_a)

        if block_a is None or block_b is None:
            pytest.skip(
                f"{cid_a}×{cid_b}: one or both POV blocks absent — "
                "perspective symmetry tested separately"
            )

        # Numeric divergence path
        num_a = _numeric_fields(block_a)
        num_b = _numeric_fields(block_b)
        shared_keys = set(num_a) & set(num_b)
        numeric_diverged = any(
            abs(num_a[k] - num_b[k]) >= 0.05 for k in shared_keys
        )

        # Prose divergence path
        sig_a = _prose_signature(block_a)
        sig_b = _prose_signature(block_b)
        prose_diverged = any(
            a and b and a != b for a, b in zip(sig_a, sig_b, strict=False)
        )
        # Also count missing-on-one-side as divergence (asymmetric authoring)
        asymmetric = any(bool(a) != bool(b) for a, b in zip(sig_a, sig_b, strict=False))

        assert numeric_diverged or prose_diverged or asymmetric, (
            f"{cid_a}×{cid_b}: POVs are IDENTICAL on every checked field. "
            "This indicates drift toward agreeable mush — per-character "
            "POV authoring is canonical and divergence is required."
        )


class TestAtLeastOneDivergence:
    """Weak-form AC-10.21: at least one dyad has divergent descriptions."""

    def test_at_least_one_dyad_has_divergent_descriptions(self) -> None:
        found = False
        for cid_a, cid_b in INTER_WOMAN_DYADS:
            block_a = _pov_block(cid_a, cid_b)
            block_b = _pov_block(cid_b, cid_a)
            desc_a = str(getattr(block_a, "description", "") or "")
            desc_b = str(getattr(block_b, "description", "") or "")
            if desc_a and desc_b and desc_a != desc_b:
                found = True
                break
        assert found, (
            "No inter-woman dyad has divergent description blocks — "
            "per-character POV architecture is not operative"
        )
