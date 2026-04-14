"""Unit tests for Phase 6 off_screen generator (R3 remediation)."""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.prose import render_off_screen_prose
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_off_screen


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


def _ctx(
    character_id: str, canon: Any, *, llm_text: str | None = None, is_away: bool = False
) -> GenerationContext:
    stub = StubBDOne(default_text=llm_text or "Morning run at Ironclad. Coffee on the porch.")
    snapshot = SessionSnapshot(
        character_id=character_id,
        life_state=types.SimpleNamespace(is_away=is_away),
    )
    return GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=snapshot,
        llm_client=stub,
        now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
    )


class TestRenderOffScreenProse:
    def test_wraps_events_with_per_character_frame(self) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            rendered = render_off_screen_prose(char, [{"summary": "ate breakfast"}])
            assert "ate breakfast" in rendered
            assert rendered.count("\n\n") == 2

    def test_empty_events_yields_placeholder(self) -> None:
        rendered = render_off_screen_prose("adelia", [])
        assert "[no off-screen events recorded]" in rendered

    def test_openers_are_distinct(self) -> None:
        frames = {
            render_off_screen_prose(c, [{"summary": "x"}]).split("\n\n")[0]
            for c in ("adelia", "bina", "reina", "alicia")
        }
        assert len(frames) == 4


class TestGenerateOffScreen:
    async def test_all_four_characters_produce_events(self, canon: Any) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            out = await generate_off_screen(_ctx(char, canon))
            assert out.kind == "off_screen"
            events = out.structured_data["events"]
            assert isinstance(events, list)
            assert out.rendered_prose
            assert out.input_tokens > 0

    async def test_llm_failure_yields_warning(self, canon: Any) -> None:
        failing = StubBDOne(fail_next_n=1)
        snapshot = SessionSnapshot(
            character_id="adelia", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="adelia",
            canon=canon,
            routines=get_routines("adelia"),
            prior_session=snapshot,
            llm_client=failing,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        out = await generate_off_screen(ctx)
        assert out.warnings
        assert any("off_screen LLM failed" in w for w in out.warnings)

    async def test_alicia_away_carries_communication_mode(self, canon: Any) -> None:
        out = await generate_off_screen(_ctx("alicia", canon, is_away=True))
        assert out.structured_data.get("communication_mode") in {
            "phone",
            "letter",
            "video_call",
        }

    async def test_non_alicia_leaves_communication_mode_null(self, canon: Any) -> None:
        for char in ("adelia", "bina", "reina"):
            out = await generate_off_screen(_ctx(char, canon, is_away=True))
            assert out.structured_data.get("communication_mode") is None

    async def test_cross_character_contamination_absent(self, canon: Any) -> None:
        """Lesson #2: focal character's system prompt excludes all others."""
        captured: dict[str, str] = {}

        def recorder(system: str, user: str) -> str:
            captured["system"] = system
            return "event one.\nevent two."

        stub = StubBDOne(responder=recorder)
        snapshot = SessionSnapshot(
            character_id="adelia", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="adelia",
            canon=canon,
            routines=get_routines("adelia"),
            prior_session=snapshot,
            llm_client=stub,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        await generate_off_screen(ctx)
        for other in ("Bina", "Reina", "Alicia"):
            assert other not in captured["system"], (
                f"Adelia's off_screen system prompt leaked {other}"
            )
