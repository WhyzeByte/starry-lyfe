"""Shared per-character fidelity test runner.

Reads the rubric and scene libraries for a character, parametrizes
across (scene, dimension) pairs, runs each through the live assembler
with stubbed memory, and scores the assembled prompt against the rubric.
Failures attach the FidelityScore.reasons to the assertion message so
operators can see exactly which canonical markers were missing.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.kernel_loader import clear_kernel_cache
from starry_lyfe.validation.fidelity import score_rubric
from tests.fidelity.conftest import (
    StubEmbeddingService,
    build_scene_state,
    load_rubrics,
    load_scenes,
    make_bundle,
)


def parametrize_cases(character_id: str) -> list[tuple[str, str]]:
    """Yield (scene_name, dimension_name) pairs for parametrized testing."""
    scenes = load_scenes(character_id)
    cases: list[tuple[str, str]] = []
    for scene in scenes:
        for dim in scene.get("rubric_dimensions_tested", []):
            cases.append((scene["name"], dim))
    return cases


async def run_fidelity_case(
    character_id: str,
    scene_name: str,
    dimension: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Assemble one (character, scene, dimension) prompt and score it."""
    rubrics = load_rubrics(character_id)
    scenes = load_scenes(character_id)
    rubric = rubrics[dimension]
    scene_spec = next(s for s in scenes if s["name"] == scene_name)

    scene_state = build_scene_state(scene_spec["scene_state"])

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return make_bundle(character_id)

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)
    clear_kernel_cache()

    prompt = await assemble_context(
        character_id=character_id,
        scene_context=scene_spec.get("scene_context", "Fidelity probe."),
        scene_state=scene_state,
        session=cast(AsyncSession, None),
        embedding_service=cast(Any, StubEmbeddingService()),
    )

    score = score_rubric(prompt.prompt, rubric)
    if not score.passed():
        details = "\n".join(f"  - {r}" for r in score.reasons)
        pytest.fail(
            f"Fidelity FAIL: {score.summary()}\n"
            f"Scene: {scene_name}\n"
            f"Reasons:\n{details}"
        )
    clear_kernel_cache()
