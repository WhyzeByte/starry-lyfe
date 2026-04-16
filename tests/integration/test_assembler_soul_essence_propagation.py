"""R-1.1 integration acceptance: missing soul essence propagates SoulEssenceNotFoundError.

Spec: Docs/_phases/REMEDIATION_2026-04-13.md §1.R-1.1 acceptance:
  "New integration test: context assembly for an unregistered character
  fails loudly, does not emit a prompt."

Phase 10.3 update: the soul essence path now reads from rich YAML
(``format_soul_essence_from_rich``) instead of the Python module.
This test patches the YAML-based format function to raise
``SoulEssenceNotFoundError`` and verifies the error propagates
through the full assembly chain unchanged.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.rich_loader import SoulEssenceNotFoundError
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.types import CommunicationMode, SceneState


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


async def test_assemble_context_missing_soul_essence_propagates_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing soul essence for a valid character must propagate SoulEssenceNotFoundError.

    R-1.1 strict propagation: the error raised in format_soul_essence must
    surface unchanged through the full assembly chain. If any intermediate
    layer silently catches and returns a degraded prompt, this test fails.

    Phase 10.3: patches ``format_soul_essence_from_rich`` to raise the
    error, simulating a character whose rich YAML has no soul_substrate.
    """
    from starry_lyfe.context.kernel_loader import _kernel_cache
    _kernel_cache.clear()

    async def stub_retrieve_memories(*args: Any, **kwargs: Any) -> Any:
        return SimpleNamespace(
            canon_facts=[],
            episodic_memories=[],
            somatic_state=None,
            character_baseline=None,
            dyad_states_whyze=[],
            dyad_states_internal=[],
            open_loops=[],
        )

    monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)

    def _raise_missing(_rc: Any) -> str:
        raise SoulEssenceNotFoundError("Simulated missing soul essence for test")

    scene = SceneState(
        present_characters=["adelia", "whyze"],
        scene_description="A scene that will never assemble.",
        communication_mode=CommunicationMode.IN_PERSON,
    )

    with (
        patch(
            "starry_lyfe.context.kernel_loader.format_soul_essence_from_rich",
            side_effect=_raise_missing,
        ),
        pytest.raises(SoulEssenceNotFoundError),
    ):
        await assemble_context(
            character_id="adelia",
            scene_context="Does not matter.",
            scene_state=scene,
            session=cast(AsyncSession, None),
            embedding_service=cast(Any, _StubEmbeddingService()),
        )

    _kernel_cache.clear()
