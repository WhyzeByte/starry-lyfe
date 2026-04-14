"""Phase 6 J8 — Dreams → Assembler handoff contract.

End-to-end check that Dreams diary output can land in
``SceneState.scene_description`` and reach the assembler's Layer 4
(Sensory Grounding) / Layer 6 (Scene Context) on a next turn.

This is AC-11 of the Phase 6 plan. Runs without a live DB by stubbing
``assembler.retrieve_memories``; proves the seam, not the DB round-trip
(which is covered by commit 8's live-DB harness in a follow-up session).

Note: full write-path integration (Dreams → activities table → retrieval
→ Layer 6) lands once the writer subsystem and retrieval-bundle
extension ship. This test proves the text-level handoff contract that
Phase 7's HTTP endpoint will use.
"""

from __future__ import annotations

import types
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.canon.routines_loader import get_routines
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.types import CommunicationMode, SceneState
from starry_lyfe.dreams import GenerationContext, SessionSnapshot, StubBDOne
from starry_lyfe.dreams.generators import generate_diary


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


@pytest.fixture(scope="module")
def canon_loaded() -> Any:
    return load_all_canon()


@pytest.fixture
def stub_memories(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _stub(*args: Any, **kwargs: Any) -> Any:
        return SimpleNamespace(
            canon_facts=[],
            episodic_memories=[],
            somatic_state=None,
            character_baseline=None,
            dyad_states_whyze=[],
            dyad_states_internal=[],
            open_loops=[],
        )

    monkeypatch.setattr(assembler_module, "retrieve_memories", _stub)


async def test_dreams_diary_reaches_assembler_scene_description(
    canon_loaded: Any, stub_memories: None
) -> None:
    """AC-11: Dreams-generated diary prose used as scene_description
    reaches the assembled prompt."""
    # Generate a diary entry.
    stub = StubBDOne(
        default_text="Today the atelier smelled like solvent and resolve."
    )
    ctx = GenerationContext(
        character_id="adelia",
        canon=canon_loaded,
        routines=get_routines("adelia"),
        prior_session=SessionSnapshot(character_id="adelia"),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    diary = await generate_diary(ctx)

    # Stuff the rendered diary into the SceneState scene_description.
    scene = SceneState(
        present_characters=["adelia", "whyze"],
        scene_description=diary.rendered_prose,
        communication_mode=CommunicationMode.IN_PERSON,
    )

    prompt = await assemble_context(
        character_id="adelia",
        scene_context=diary.rendered_prose,
        scene_state=scene,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )

    assert prompt.is_terminally_anchored
    # The distinctive phrase from the diary body should reach the prompt.
    assert "solvent and resolve" in prompt.prompt


async def test_dreams_activity_rendered_prose_non_empty_for_all_characters(
    canon_loaded: Any, stub_memories: None
) -> None:
    """Every character's Dreams output can feed the assembler's scene_description.

    This is the public-API contract proof: invoke the diary generator
    for each character, plug the output into a fresh scene, and confirm
    the assembler accepts it and terminally anchors.
    """
    for character_id in ("adelia", "bina", "reina", "alicia"):
        stub = StubBDOne(default_text="A quiet thread ran through today's work.")
        ctx = GenerationContext(
            character_id=character_id,
            canon=canon_loaded,
            routines=get_routines(character_id),
            prior_session=SessionSnapshot(
                character_id=character_id,
                life_state=types.SimpleNamespace(is_away=False),
            ),
            llm_client=stub,
            now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
        )
        diary = await generate_diary(ctx)

        # Alicia home=True is required when assembling in-person; the
        # other three characters do not carry that gate.
        scene = SceneState(
            present_characters=[character_id, "whyze"],
            scene_description=diary.rendered_prose,
            communication_mode=CommunicationMode.IN_PERSON,
            alicia_home=True,
        )
        prompt = await assemble_context(
            character_id=character_id,
            scene_context=diary.rendered_prose,
            scene_state=scene,
            session=cast(AsyncSession, None),
            embedding_service=cast(Any, _StubEmbeddingService()),
        )
        assert prompt.is_terminally_anchored
        assert prompt.character_id == character_id


async def test_alicia_away_diary_assembles_with_remote_comm_mode(
    canon_loaded: Any, stub_memories: None
) -> None:
    """Alicia-away scenario: diary with communication_mode tag assembles
    when scene.communication_mode is phone/letter/video_call."""
    stub = StubBDOne(default_text="The operation is winding down and the cadence is changing.")
    ctx = GenerationContext(
        character_id="alicia",
        canon=canon_loaded,
        routines=get_routines("alicia"),
        prior_session=SessionSnapshot(
            character_id="alicia",
            life_state=types.SimpleNamespace(is_away=True),
        ),
        llm_client=stub,
        now=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    diary = await generate_diary(ctx)
    mode_tag = diary.structured_data["communication_mode"]
    assert mode_tag in {"phone", "letter", "video_call"}

    # Scene must use the matching remote communication_mode so Phase A''
    # filtering in layers.py honors it and the assembler accepts Alicia-away.
    scene_mode = CommunicationMode(mode_tag)
    scene = SceneState(
        present_characters=["alicia", "whyze"],
        scene_description=diary.rendered_prose,
        communication_mode=scene_mode,
        alicia_home=False,
    )
    prompt = await assemble_context(
        character_id="alicia",
        scene_context=diary.rendered_prose,
        scene_state=scene,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, _StubEmbeddingService()),
    )
    assert prompt.is_terminally_anchored
