"""Unit tests for Phase 6 open_loops generator (R4 remediation)."""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.prose import render_open_loop_prose
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_open_loops
from starry_lyfe.dreams.generators.open_loops import _parse_llm_output


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


def _ctx(
    character_id: str,
    canon: Any,
    *,
    llm_text: str | None = None,
    is_away: bool = False,
) -> GenerationContext:
    stub = StubBDOne(
        default_text=llm_text
        or "NEW: check in on the shop order.\nNEW: raise the trip plan."
    )
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


class TestRenderOpenLoopProse:
    def test_wraps_loops_with_per_character_frame(self) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            rendered = render_open_loop_prose(
                char, [{"summary": "follow up tomorrow", "urgency": "high"}]
            )
            assert "follow up tomorrow" in rendered
            assert rendered.count("\n\n") == 2

    def test_empty_loops_yields_placeholder(self) -> None:
        assert "[no new open loops]" in render_open_loop_prose("adelia", [])


class TestParseLLMOutput:
    def test_extracts_new_prefixed_lines(self) -> None:
        raw = "NEW: one thing.\nNEW: another thing."
        result = _parse_llm_output(raw)
        assert len(result) == 2
        assert result[0]["summary"] == "one thing."

    def test_ignores_non_new_lines(self) -> None:
        raw = "reflection on yesterday.\nNEW: something to raise."
        result = _parse_llm_output(raw)
        assert len(result) == 1

    def test_caps_at_three_loops(self) -> None:
        raw = "\n".join(f"NEW: loop {i}" for i in range(10))
        result = _parse_llm_output(raw)
        assert len(result) == 3

    def test_tolerates_bullet_prefixes(self) -> None:
        raw = "- NEW: one.\n1. NEW: two."
        result = _parse_llm_output(raw)
        assert len(result) == 2


class TestGenerateOpenLoops:
    async def test_all_four_characters_produce_output(self, canon: Any) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            out = await generate_open_loops(_ctx(char, canon))
            assert out.kind == "open_loops"
            assert out.rendered_prose
            assert isinstance(out.structured_data["new_loops"], list)

    async def test_new_loops_extracted_from_llm_response(self, canon: Any) -> None:
        out = await generate_open_loops(_ctx("adelia", canon))
        new_loops = out.structured_data["new_loops"]
        # Default LLM stub text has 2 NEW lines.
        assert len(new_loops) == 2
        for loop in new_loops:
            assert "summary" in loop

    async def test_llm_failure_yields_warning(self, canon: Any) -> None:
        failing = StubBDOne(fail_next_n=1)
        snapshot = SessionSnapshot(
            character_id="bina", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="bina",
            canon=canon,
            routines=get_routines("bina"),
            prior_session=snapshot,
            llm_client=failing,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        out = await generate_open_loops(ctx)
        assert any("open_loops LLM failed" in w for w in out.warnings)
        assert out.structured_data["new_loops"] == []

    async def test_alicia_away_carries_communication_mode(self, canon: Any) -> None:
        out = await generate_open_loops(_ctx("alicia", canon, is_away=True))
        assert out.structured_data.get("communication_mode") in {
            "phone",
            "letter",
            "video_call",
        }

    async def test_cross_character_contamination_absent(self, canon: Any) -> None:
        captured: dict[str, str] = {}

        def recorder(system: str, user: str) -> str:
            captured["system"] = system
            return "NEW: follow up."

        stub = StubBDOne(responder=recorder)
        snapshot = SessionSnapshot(
            character_id="reina", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="reina",
            canon=canon,
            routines=get_routines("reina"),
            prior_session=snapshot,
            llm_client=stub,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        await generate_open_loops(ctx)
        for other in ("Adelia", "Bina", "Alicia"):
            assert other not in captured["system"]
