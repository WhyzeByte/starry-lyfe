"""Phase 6 → Phase 7 Dreams glue (AC-7.8 / G7).

Proves that Dreams-written Activity rows reach Layer 6 of the assembled
prompt on the next chat turn. This is the final closure of the Phase 6
deferred glue: Phase 6 R3-F2 wired the consumer path through
``MemoryBundle.activities``; this test proves it round-trips through
the live chat endpoint.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.db.models import Activity
from starry_lyfe.dreams.llm import StubBDOne


class _StubEmbedding:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


@pytest_asyncio.fixture
async def seeded_with_dreams_activity(
    engine: AsyncEngine,
    setup_database: None,
) -> tuple[Activity, async_sessionmaker[AsyncSession]]:
    """Insert a Dreams-style Activity row for Adelia, return it + factory.

    The activity carries a uniquely-marked ``narrator_script`` so the
    test can assert that string appears in the assembled prompt body.
    """
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    marker = "MORNING-OPENER-MARKER-FROM-DREAMS"
    async with factory() as session, session.begin():
        # Clear any prior Activity rows so the test's row is the
        # newest.
        existing = (
            await session.execute(select(Activity).where(Activity.character_id == "adelia"))
        ).scalars().all()
        for row in existing:
            await session.delete(row)

        activity = Activity(
            character_id="adelia",
            scene_description="Adelia is sketching at the atelier.",
            narrator_script=f"{marker}: the workbench is cool, light coming sideways.",
            choice_tree={"branches": [{"label": "approach", "summary": "ask what she's working on"}]},
            communication_mode=None,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        session.add(activity)
    return activity, factory


@pytest.fixture
def dreams_glue_client(
    seeded_with_dreams_activity: tuple[Activity, async_sessionmaker[AsyncSession]],
    engine: AsyncEngine,
) -> tuple[TestClient, list[str]]:
    """Build a chat client that captures the assembled prompt body.

    We monkeypatch a wrapper around assemble_context that records the
    prompt body so the test can assert the Activity narrator_script
    landed in Layer 6.
    """
    _activity, factory = seeded_with_dreams_activity
    captured_prompts: list[str] = []

    # The real assemble_context will load the Dreams-written Activity
    # via MemoryBundle.activities → format_scene_blocks (Phase 6 R3-F2)
    # → Layer 6. We capture the prompt by wrapping the real call.
    from starry_lyfe.context import assembler as _assembler_mod

    real_assemble = _assembler_mod.assemble_context

    async def _capturing(*args: object, **kwargs: object) -> Any:  # noqa: ANN401
        prompt = await real_assemble(*args, **kwargs)
        captured_prompts.append(prompt.prompt)
        return prompt

    import starry_lyfe.api.orchestration.pipeline as _pipeline_mod

    _pipeline_mod.assemble_context = _capturing  # type: ignore[assignment]

    app = create_app(
        ApiSettings(api_key="dev"),
        state_overrides={
            "engine": engine,
            "session_factory": factory,
            "canon": load_all_canon(),
            "embedding_service": _StubEmbedding(),
            "llm_client": StubBDOne(),
        },
    )
    return TestClient(app), captured_prompts


class TestDreamsActivitySurfacesIntoChat:
    def test_dreams_activity_lands_in_layer_6(
        self,
        dreams_glue_client: tuple[TestClient, list[str]],
    ) -> None:
        """AC-7.8: Dreams-written Activity rows auto-populate Layer 6 on the
        next chat turn. Closes the deferred Phase 6 glue."""
        client, captured = dreams_glue_client
        with client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
                    "messages": [{"role": "user", "content": "morning"}],
                    "stream": True,
                },
            )
            assert response.status_code == 200
            _ = response.text  # drain so the SSE generator runs assemble_context
        assert captured, "assemble_context was never called"
        full_prompt = captured[-1]
        assert "MORNING-OPENER-MARKER-FROM-DREAMS" in full_prompt, (
            "the Dreams Activity narrator_script did not reach the assembled prompt"
        )
        # The Phase 6 R3-F2 header MUST also be present so future drift
        # in the consumer path surfaces here.
        assert "Today's Dreams scene opener" in full_prompt
