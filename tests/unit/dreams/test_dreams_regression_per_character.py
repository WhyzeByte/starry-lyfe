"""Phase H retroactive — per-character Dreams regression bundle.

For each of the four canonical women, assert that Dreams diary output:
1. Carries the character's canonical voice register markers (opener/closer).
2. Does NOT carry any other character's canonical voice markers
   (cross-character contamination negative — lesson #2).
3. Honors the Phase G three-paragraph structure.
4. For Alicia-away scenarios, carries a communication_mode tag in the
   structured_data payload.

Pattern mirrors tests/unit/test_soul_regression_*.py. Full-pass Dreams
runner output is covered by commit 8's test_dreams_alicia_away_mode.py
integration test; this file focuses on the generator-level invariants.
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
    character_id: str,
    canon: Any,
    *,
    is_away: bool = False,
    llm_text: str = "end-of-day reflection recorded for the log.",
) -> GenerationContext:
    """Build a GenerationContext with an optional Alicia-away life_state."""
    life_state = types.SimpleNamespace(is_away=is_away)
    snapshot = SessionSnapshot(character_id=character_id, life_state=life_state)
    return GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=snapshot,
        llm_client=StubBDOne(default_text=llm_text),
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )


# Per-character canonical opener markers — must appear in Phase G wrapped
# output for that character, and must NOT appear for any other character.
_OPENER_MARKERS: dict[str, str] = {
    "adelia": "The evening cooled off",
    "bina": "The log for today",
    "reina": "Entry for the record",
    "alicia": "The body is still and the house is quiet",
}


class TestPerCharacterDiaryVoice:
    """Phase H retroactive — every character's diary keeps her voice register."""

    @pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
    async def test_character_opener_present(
        self, canon: Any, character_id: str
    ) -> None:
        out = await generate_diary(_make_ctx(character_id, canon))
        assert _OPENER_MARKERS[character_id] in out.rendered_prose

    @pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
    async def test_other_characters_openers_absent(
        self, canon: Any, character_id: str
    ) -> None:
        """Cross-character contamination negative — lesson #2."""
        out = await generate_diary(_make_ctx(character_id, canon))
        for other_id, other_marker in _OPENER_MARKERS.items():
            if other_id == character_id:
                continue
            assert other_marker not in out.rendered_prose, (
                f"{character_id}'s diary contaminated with {other_id}'s opener"
            )

    @pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
    async def test_phase_g_three_paragraph_structure(
        self, canon: Any, character_id: str
    ) -> None:
        out = await generate_diary(_make_ctx(character_id, canon))
        assert out.rendered_prose.count("\n\n") == 2

    @pytest.mark.parametrize("character_id", ["adelia", "bina", "reina", "alicia"])
    async def test_rendered_prose_contains_llm_body(
        self, canon: Any, character_id: str
    ) -> None:
        """The LLM's response body must appear inside the rendered prose."""
        out = await generate_diary(
            _make_ctx(character_id, canon, llm_text="the specific body content.")
        )
        assert "specific body content" in out.rendered_prose


class TestAliciaAwayCommunicationMode:
    """Phase A'' retroactive — Alicia-away diary entries carry a tag."""

    async def test_alicia_away_diary_carries_communication_mode(
        self, canon: Any
    ) -> None:
        out = await generate_diary(_make_ctx("alicia", canon, is_away=True))
        mode = out.structured_data.get("communication_mode")
        assert mode in {"phone", "letter", "video_call"}

    async def test_alicia_home_diary_leaves_mode_null(self, canon: Any) -> None:
        out = await generate_diary(_make_ctx("alicia", canon, is_away=False))
        assert out.structured_data.get("communication_mode") is None

    @pytest.mark.parametrize("character_id", ["adelia", "bina", "reina"])
    async def test_non_alicia_diary_leaves_mode_null_even_with_is_away_true(
        self, canon: Any, character_id: str
    ) -> None:
        """Defensive: is_away=True on a non-Alicia life_state must NOT tag.

        is_away is Alicia-only by canonical convention, but the schema
        allows the bool on any row. The tag helper is a lesson-#2-style
        narrow check: only tag when character IS Alicia.
        """
        out = await generate_diary(
            _make_ctx(character_id, canon, is_away=True)
        )
        assert out.structured_data.get("communication_mode") is None
