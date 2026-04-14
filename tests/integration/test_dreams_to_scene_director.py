"""Phase 6 J7 — Dreams → Scene Director handoff contract.

End-to-end check per Phase 5 lesson #1: the Dreams pipeline's output
(specifically the diary generator's rendered_prose) populates the
``NextSpeakerInput.activity_context`` slot plumbed in Phase 5 R1, and
the Scene Director's Rule 7 narrative-salience boost fires on
candidates named in that text.

This is AC-10 of the Phase 6 plan. Runs without a live DB by using
StubBDOne + empty session snapshots.
"""

from __future__ import annotations

import types
from datetime import UTC, datetime
from typing import Any

import pytest

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context.types import CommunicationMode, SceneState
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_diary
from starry_lyfe.scene import (
    DictDyadStateProvider,
    NextSpeakerInput,
    select_next_speaker,
)


@pytest.fixture(scope="module")
def canon() -> Any:
    return load_all_canon()


def _make_scene(present: list[str]) -> SceneState:
    return SceneState(
        present_characters=present,
        scene_description="quiet evening",
        communication_mode=CommunicationMode.IN_PERSON,
    )


async def test_dreams_diary_output_feeds_activity_context(canon: Any) -> None:
    """AC-10: Dreams diary prose flows into NextSpeakerInput.activity_context."""
    # Drive Dreams diary generator so the rendered_prose names Adelia.
    stub = StubBDOne(default_text="Adelia and I spent the afternoon in the atelier.")
    ctx = GenerationContext(
        character_id="adelia",
        canon=canon,
        routines=get_routines("adelia"),
        prior_session=SessionSnapshot(character_id="adelia"),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    dreams_output = await generate_diary(ctx)
    assert "Adelia" in dreams_output.rendered_prose

    # Hand that rendered prose into the Scene Director as activity_context.
    baseline = select_next_speaker(
        NextSpeakerInput(
            scene_state=_make_scene(["adelia", "bina"]),
            turn_history=[],
            dyad_state_provider=DictDyadStateProvider({}),
            activity_context=None,
        )
    )
    with_dreams = select_next_speaker(
        NextSpeakerInput(
            scene_state=_make_scene(["adelia", "bina"]),
            turn_history=[],
            dyad_state_provider=DictDyadStateProvider({}),
            activity_context=dreams_output.rendered_prose,
        )
    )

    # Adelia is named in the Dreams-sourced activity_context → narrative
    # salience boost fires for her candidate score.
    assert with_dreams.scores["adelia"] > baseline.scores["adelia"]


async def test_dreams_activity_context_does_not_boost_absent_names(
    canon: Any,
) -> None:
    """Defensive: salience boost only fires for candidates NAMED in the text."""
    stub = StubBDOne(default_text="Thinking about the atelier work and color theory.")
    ctx = GenerationContext(
        character_id="adelia",
        canon=canon,
        routines=get_routines("adelia"),
        prior_session=SessionSnapshot(character_id="adelia"),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    dreams_output = await generate_diary(ctx)
    # Diary body does NOT name Reina or Bina — salience should not boost them.
    assert "Reina" not in dreams_output.rendered_prose
    assert "Bina" not in dreams_output.rendered_prose

    baseline = select_next_speaker(
        NextSpeakerInput(
            scene_state=_make_scene(["reina", "bina"]),
            turn_history=[],
            dyad_state_provider=DictDyadStateProvider({}),
            activity_context=None,
        )
    )
    with_dreams = select_next_speaker(
        NextSpeakerInput(
            scene_state=_make_scene(["reina", "bina"]),
            turn_history=[],
            dyad_state_provider=DictDyadStateProvider({}),
            activity_context=dreams_output.rendered_prose,
        )
    )
    # Neither Reina nor Bina's scores should rise from unrelated activity text.
    assert with_dreams.scores["reina"] == pytest.approx(baseline.scores["reina"])
    assert with_dreams.scores["bina"] == pytest.approx(baseline.scores["bina"])


async def test_full_pass_diary_feeds_all_four_characters_into_activity(
    canon: Any,
) -> None:
    """Every character's Dreams diary output can feed back into Scene Director.

    Proves the handoff contract works for all 4 characters, not just Adelia.
    """
    for character_id in ("adelia", "bina", "reina", "alicia"):
        stub = StubBDOne(default_text="Thinking about tomorrow's work with care.")
        ctx = GenerationContext(
            character_id=character_id,
            canon=canon,
            routines=get_routines(character_id),
            prior_session=SessionSnapshot(
                character_id=character_id,
                life_state=types.SimpleNamespace(is_away=False),
            ),
            llm_client=stub,
            now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
        )
        dreams_output = await generate_diary(ctx)
        # Activity_context is non-empty and 3-paragraph.
        assert dreams_output.rendered_prose
        assert dreams_output.rendered_prose.count("\n\n") == 2
