"""Phase 7 auth integration tests (G6)."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.context.types import AssembledPrompt, LayerContent
from starry_lyfe.dreams.llm import StubBDOne


class _StubEmbedding:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


@pytest.fixture
def auth_client(
    monkeypatch: pytest.MonkeyPatch,
    engine: AsyncEngine,
    setup_database: None,
) -> TestClient:
    async def _fake(*args: object, **kwargs: object) -> AssembledPrompt:
        return AssembledPrompt(
            prompt="<P>x</P>",
            character_id="adelia",
            layers=[LayerContent(name="x", text="x", estimated_tokens=1, layer_number=1)],
            total_tokens=1,
            constraint_block_position="terminal",
        )

    monkeypatch.setattr(
        "starry_lyfe.api.orchestration.pipeline.assemble_context", _fake
    )
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    app = create_app(
        ApiSettings(api_key="secret-key"),
        state_overrides={
            "engine": engine,
            "session_factory": factory,
            "canon": load_all_canon(),
            "embedding_service": _StubEmbedding(),
            "llm_client": StubBDOne(),
        },
    )
    return TestClient(app)


def _payload() -> dict[str, Any]:
    return {
        "model": "adelia",
        "messages": [{"role": "user", "content": "hi"}],
        "stream": True,
    }


class TestAuth:
    def test_missing_key_returns_401(self, auth_client: TestClient) -> None:
        with auth_client:
            r = auth_client.post("/v1/chat/completions", json=_payload())
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "UNAUTHORIZED"

    def test_wrong_key_returns_401(self, auth_client: TestClient) -> None:
        with auth_client:
            r = auth_client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "WRONG"},
                json=_payload(),
            )
        assert r.status_code == 401

    def test_correct_key_returns_200(self, auth_client: TestClient) -> None:
        with auth_client:
            r = auth_client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "secret-key"},
                json=_payload(),
            )
        assert r.status_code == 200

    def test_health_remains_public(self, auth_client: TestClient) -> None:
        with auth_client:
            assert auth_client.get("/health/live").status_code == 200
            assert auth_client.get("/health/ready").status_code == 200

    def test_models_remains_public(self, auth_client: TestClient) -> None:
        with auth_client:
            assert auth_client.get("/v1/models").status_code == 200

    def test_metrics_remains_public(self, auth_client: TestClient) -> None:
        with auth_client:
            assert auth_client.get("/metrics").status_code == 200
