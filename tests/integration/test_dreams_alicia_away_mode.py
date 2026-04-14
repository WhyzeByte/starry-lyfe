"""Phase 6 J10 — Alicia away-mode end-to-end tagging contract.

Verifies the Phase A'' retroactive pass through the full Dreams runner:
when Alicia's life_state.is_away=True and the runner processes the 4
canonical characters, her diary output carries a communication_mode tag
in {phone, letter, video_call} while the other 3 characters do not.

This is AC-5 of the Phase 6 plan.
"""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_diary


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


def _make_ctx(
    character_id: str, canon: Any, *, is_away: bool
) -> GenerationContext:
    return GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=SessionSnapshot(
            character_id=character_id,
            life_state=types.SimpleNamespace(is_away=is_away),
        ),
        llm_client=StubBDOne(default_text="reflection for the evening."),
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )


async def test_alicia_away_full_pass_tags_only_alicia(canon: Any) -> None:
    """Running generate_diary for all 4 characters with Alicia.is_away=True
    produces a communication_mode tag ONLY on Alicia's output."""
    # Alicia away; everyone else home (as is canonical).
    tags: dict[str, str | None] = {}
    for character_id in ("adelia", "bina", "reina", "alicia"):
        is_away = character_id == "alicia"
        out = await generate_diary(_make_ctx(character_id, canon, is_away=is_away))
        tags[character_id] = out.structured_data.get("communication_mode")

    assert tags["alicia"] in {"phone", "letter", "video_call"}
    assert tags["adelia"] is None
    assert tags["bina"] is None
    assert tags["reina"] is None


async def test_alicia_home_full_pass_leaves_all_tags_null(canon: Any) -> None:
    """When Alicia is home, no character's diary carries a comm-mode tag."""
    for character_id in ("adelia", "bina", "reina", "alicia"):
        out = await generate_diary(_make_ctx(character_id, canon, is_away=False))
        assert out.structured_data.get("communication_mode") is None


async def test_alicia_away_sampling_deterministic_within_one_moment(
    canon: Any,
) -> None:
    """Two invocations with the same ``now`` produce the same tag (stable
    sampling; AC-5 Alicia-away reproducibility invariant)."""
    a = await generate_diary(_make_ctx("alicia", canon, is_away=True))
    b = await generate_diary(_make_ctx("alicia", canon, is_away=True))
    assert (
        a.structured_data["communication_mode"]
        == b.structured_data["communication_mode"]
    )


async def test_alicia_away_tag_matches_distribution_across_many_runs(
    canon: Any,
) -> None:
    """Across 40 simulated passes (distinct ``now`` values) we should see
    all three communication modes — proving the distribution isn't stuck."""
    seen: set[str] = set()
    for i in range(40):
        now = datetime(2026, 4, 14, 22, i % 60, tzinfo=UTC)
        ctx = GenerationContext(
            character_id="alicia",
            canon=canon,
            routines=get_routines("alicia"),
            prior_session=SessionSnapshot(
                character_id="alicia",
                life_state=types.SimpleNamespace(is_away=True),
            ),
            llm_client=StubBDOne(),
            now=now,
        )
        out = await generate_diary(ctx)
        tag = out.structured_data.get("communication_mode")
        assert tag in {"phone", "letter", "video_call"}
        seen.add(str(tag))
    # The 0.45/0.20/0.35 distribution should produce all three across 40
    # samples with near-certainty.
    assert seen == {"phone", "letter", "video_call"}
