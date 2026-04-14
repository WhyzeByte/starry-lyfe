"""Phase F-Fidelity: Alicia Marin rubric tests."""

from __future__ import annotations

import pytest

from tests.fidelity._runner import parametrize_cases, run_fidelity_case

CHARACTER_ID = "alicia"


@pytest.mark.parametrize(("scene_name", "dimension"), parametrize_cases(CHARACTER_ID))
async def test_alicia_fidelity(
    scene_name: str, dimension: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    await run_fidelity_case(CHARACTER_ID, scene_name, dimension, monkeypatch)
