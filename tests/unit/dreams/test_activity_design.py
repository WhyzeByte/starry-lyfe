"""Unit tests for Phase 6 activity_design generator (R5 remediation)."""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.prose import render_activity_prose
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_activity_design
from starry_lyfe.dreams.generators.activity_design import _parse_llm_output


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
        or (
            "Morning light in the kitchen. Coffee is steeping. "
            "The day has not started yet.\n"
            "Branch: sit and watch the steam.\n"
            "Branch: start the kettle over and make it right.\n"
            "Branch: step onto the porch with the mug."
        )
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


class TestRenderActivityProse:
    def test_wraps_narrator_script(self) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            rendered = render_activity_prose(char, "Morning in the kitchen.")
            assert "Morning in the kitchen." in rendered
            assert rendered.count("\n\n") == 2

    def test_empty_script_yields_placeholder(self) -> None:
        assert "[no activity designed]" in render_activity_prose("adelia", "")


class TestParseLLMOutput:
    def test_splits_narrator_and_branches(self) -> None:
        raw = (
            "Morning light. Coffee on the stove.\n"
            "Branch: pour the coffee.\n"
            "Branch: sit and wait."
        )
        narrator, tree = _parse_llm_output(raw)
        assert "Morning light" in narrator
        assert isinstance(tree, dict)
        branches = tree["branches"]
        assert len(branches) == 2
        assert branches[0]["option"] == "pour the coffee."

    def test_caps_branches_at_three(self) -> None:
        raw = "narrator.\n" + "\n".join(f"Branch: option {i}" for i in range(10))
        _, tree = _parse_llm_output(raw)
        assert len(tree["branches"]) == 3

    def test_no_branches_falls_through_to_full_narrator(self) -> None:
        raw = "Just a narrator line with no branches."
        narrator, tree = _parse_llm_output(raw)
        assert narrator == "Just a narrator line with no branches."
        assert tree["branches"] == []


class TestGenerateActivityDesign:
    async def test_all_four_characters_produce_output(self, canon: Any) -> None:
        for char in ("adelia", "bina", "reina", "alicia"):
            out = await generate_activity_design(_ctx(char, canon))
            assert out.kind == "activity_design"
            assert out.rendered_prose
            assert out.structured_data["narrator_script"]
            assert isinstance(out.structured_data["choice_tree"]["branches"], list)

    async def test_llm_failure_yields_warning(self, canon: Any) -> None:
        failing = StubBDOne(fail_next_n=1)
        snapshot = SessionSnapshot(
            character_id="reina", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="reina",
            canon=canon,
            routines=get_routines("reina"),
            prior_session=snapshot,
            llm_client=failing,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        out = await generate_activity_design(ctx)
        assert any("activity_design LLM failed" in w for w in out.warnings)

    async def test_alicia_away_carries_communication_mode(self, canon: Any) -> None:
        out = await generate_activity_design(_ctx("alicia", canon, is_away=True))
        assert out.structured_data.get("communication_mode") in {
            "phone",
            "letter",
            "video_call",
        }

    async def test_cross_character_contamination_absent(self, canon: Any) -> None:
        captured: dict[str, str] = {}

        def recorder(system: str, user: str) -> str:
            captured["system"] = system
            return "Morning setting.\nBranch: option one."

        stub = StubBDOne(responder=recorder)
        snapshot = SessionSnapshot(
            character_id="bina", life_state=types.SimpleNamespace(is_away=False)
        )
        ctx = GenerationContext(
            character_id="bina",
            canon=canon,
            routines=get_routines("bina"),
            prior_session=snapshot,
            llm_client=stub,
            now=datetime(2026, 4, 14, 3, 30, tzinfo=UTC),
        )
        await generate_activity_design(ctx)
        for other in ("Adelia", "Reina", "Alicia"):
            assert other not in captured["system"]
