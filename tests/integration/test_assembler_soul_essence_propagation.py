"""R-1.1 integration acceptance: unknown character propagates SoulEssenceNotFoundError.

Spec: Docs/_phases/REMEDIATION_2026-04-13.md §1.R-1.1 acceptance:
  "New integration test: context assembly for an unregistered character
  fails loudly, does not emit a prompt."

This exercises the chain `assemble_context` -> `format_kernel` ->
`load_kernel` -> `compile_kernel_with_soul` -> `format_soul_essence`.
If any intermediate layer silently catches the error, this test fails.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.soul_essence import SoulEssenceNotFoundError
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

    Setup: simulate a character whose kernel exists but soul essence is
    missing (which is the failure mode R-1.1 prevents from silently
    shipping). Monkeypatch SOUL_ESSENCES rather than using an unregistered
    character ID — the latter would be caught by KERNEL_PATHS first.
    """
    from starry_lyfe.canon import soul_essence as soul_essence_module

    # Remove adelia's soul essence for the duration of the test
    patched_registry = dict(soul_essence_module.SOUL_ESSENCES)
    patched_registry.pop("adelia")
    monkeypatch.setattr(soul_essence_module, "SOUL_ESSENCES", patched_registry)

    # Also clear kernel cache so the next load call re-executes
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

    scene = SceneState(
        present_characters=["adelia", "whyze"],
        scene_description="A scene that will never assemble.",
        communication_mode=CommunicationMode.IN_PERSON,
    )

    with pytest.raises(SoulEssenceNotFoundError):
        await assemble_context(
            character_id="adelia",
            scene_context="Does not matter.",
            scene_state=scene,
            session=cast(AsyncSession, None),
            embedding_service=cast(Any, _StubEmbeddingService()),
        )

    # Cleanup: clear cache again since the broken monkeypatch may have leaked
    _kernel_cache.clear()
