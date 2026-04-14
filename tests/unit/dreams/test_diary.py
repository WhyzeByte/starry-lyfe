"""Unit tests for the diary generator (Phase 6 commit 5)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.prose import render_diary_prose
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_diary


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


def _ctx(
    character_id: str,
    canon: Any,
    *,
    llm_client: Any | None = None,
    snapshot: SessionSnapshot | None = None,
) -> GenerationContext:
    return GenerationContext(
        character_id=character_id,
        canon=canon,
        routines=get_routines(character_id),
        prior_session=snapshot or SessionSnapshot(character_id=character_id),
        llm_client=llm_client or StubBDOne(),
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )


class TestRenderDiaryProse:
    def test_wraps_content_with_per_character_frame(self) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            rendered = render_diary_prose(char, "Today was full.")
            assert "Today was full." in rendered
            # Three-paragraph structure: opener + body + closer.
            assert rendered.count("\n\n") == 2

    def test_openers_are_character_distinct(self) -> None:
        adelia = render_diary_prose("adelia", "x").split("\n\n")[0]
        bina = render_diary_prose("bina", "x").split("\n\n")[0]
        reina = render_diary_prose("reina", "x").split("\n\n")[0]
        alicia = render_diary_prose("alicia", "x").split("\n\n")[0]
        assert len({adelia, bina, reina, alicia}) == 4

    def test_empty_content_falls_back_to_placeholder(self) -> None:
        rendered = render_diary_prose("adelia", "")
        assert "[no reflection today]" in rendered


class TestGenerateDiary:
    async def test_returns_rendered_prose_wrapped_in_phase_g_frame(
        self, canon: Any
    ) -> None:
        stub = StubBDOne(default_text="It was a calm day of work.")
        ctx = _ctx("adelia", canon, llm_client=stub)
        out = await generate_diary(ctx)
        assert out.kind == "diary"
        # Phase G wrapping should be applied.
        assert out.rendered_prose.count("\n\n") == 2
        # Raw text should be what StubBDOne returned (hash-keyed prefix).
        assert "calm day of work" in out.raw_llm_text
        assert out.raw_llm_text in out.rendered_prose

    async def test_all_four_characters_produce_diary_output(self, canon: Any) -> None:
        stub = StubBDOne(default_text="One line of diary content.")
        for char in ("adelia", "bina", "reina", "alicia"):
            out = await generate_diary(_ctx(char, canon, llm_client=stub))
            assert out.rendered_prose  # non-empty
            assert out.input_tokens > 0
            assert out.output_tokens > 0

    async def test_llm_failure_returns_warning_not_exception(self, canon: Any) -> None:
        failing = StubBDOne(fail_next_n=1)
        out = await generate_diary(_ctx("adelia", canon, llm_client=failing))
        assert out.warnings
        assert any("diary LLM failed" in w for w in out.warnings)
        assert out.raw_llm_text == ""

    async def test_user_prompt_uses_only_focal_character_data(
        self, canon: Any
    ) -> None:
        """Lesson #2 anti-contamination: the user prompt must include only
        the focal character's data, never cross-character session material."""
        captured: dict[str, str] = {}

        def recorder(system: str, user: str) -> str:
            captured["system"] = system
            captured["user"] = user
            return "response"

        stub = StubBDOne(responder=recorder)
        ctx = _ctx("adelia", canon, llm_client=stub)
        await generate_diary(ctx)

        # Focal character IS in the system prompt.
        assert "Adelia" in captured["system"]
        # No other canonical women should appear in the system prompt for Adelia.
        for other in ("Bina", "Reina", "Alicia"):
            assert other not in captured["system"], (
                f"Adelia's diary system prompt leaked {other}"
            )
