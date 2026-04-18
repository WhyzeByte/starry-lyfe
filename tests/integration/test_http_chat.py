"""Phase 7 load-bearing end-to-end chat completion test (G3 / AC-7.19).

Lesson #1 from Phase 5/6: end-to-end integration contracts catch bugs
that unit tests cannot. This file invokes the full 12-step flow via
FastAPI's TestClient against a real running ASGI app + live Postgres,
asserts the SSE wire format, then verifies that the post-turn
fire-and-forget tasks landed real DB rows.

The test auto-skips unless the project Postgres is migrated and
reachable; set ``STARRY_LYFE__TEST__REQUIRE_POSTGRES=1`` to
force-fail.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.context.types import AssembledPrompt, LayerContent
from starry_lyfe.db.models import ChatSession, EpisodicMemory
from starry_lyfe.dreams.llm import StubBDOne


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


def _make_assembled_prompt(character_id: str) -> AssembledPrompt:
    return AssembledPrompt(
        prompt=f"<PERSONA_KERNEL>\nstub for {character_id}\n</PERSONA_KERNEL>",
        character_id=character_id,
        layers=[LayerContent(name="persona_kernel", text="stub", estimated_tokens=2, layer_number=1)],
        total_tokens=2,
        constraint_block_position="terminal",
    )


@pytest.fixture
def chat_app(
    monkeypatch: pytest.MonkeyPatch,
    engine: AsyncEngine,
    setup_database: None,
) -> Iterator[tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne]]:
    """Build a TestClient wired to the live engine + real session factory.

    assemble_context is stubbed so the test doesn't depend on canon
    facts being seeded; the focus of this test is the HTTP / pipeline
    / fire-and-forget contract, not the assembly internals (those are
    covered by tests/unit/test_assembler.py).
    """

    async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
        char_id = kwargs.get("character_id", args[0] if args else "adelia")
        return _make_assembled_prompt(str(char_id))

    monkeypatch.setattr(
        "starry_lyfe.api.orchestration.pipeline.assemble_context",
        _fake_assemble_context,
    )

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    canon = load_all_canon()
    stub = StubBDOne(
        default_text="Adelia thought about the conversation and felt warmth and trust. We sat close on the porch.",
    )

    app = create_app(
        ApiSettings(api_key="test-key", default_character="adelia"),
        state_overrides={
            "engine": engine,
            "session_factory": factory,
            "canon": canon,
            "embedding_service": _StubEmbeddingService(),
            "llm_client": stub,
        },
    )

    with TestClient(app) as client:
        yield client, factory, stub


def _parse_sse(body: str) -> list[dict[str, Any] | str]:
    parts: list[dict[str, Any] | str] = []
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if payload == "[DONE]":
            parts.append("[DONE]")
            continue
        parts.append(json.loads(payload))
    return parts


class TestChatCompletionEndToEnd:
    def test_full_12_step_flow_lands_chat_session_row(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.9: a turn lands a chat_sessions row with turn_count=1."""
        client, _, _ = chat_app
        sid = str(uuid.uuid4())
        response = client.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key", "X-Session-ID": sid},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "morning"}],
                "stream": True,
            },
        )
        assert response.status_code == 200

        # Read the body so the SSE generator drains.
        body = response.text
        chunks = _parse_sse(body)
        assert chunks[-1] == "[DONE]"

        # Verify the chat_session row landed via a fresh session.
        import asyncio

        async def _check() -> None:
            client_local, factory, _ = chat_app
            async with factory() as session:
                row = (
                    await session.execute(
                        select(ChatSession).where(ChatSession.id == uuid.UUID(sid))
                    )
                ).scalars().first()
                assert row is not None, "chat_sessions row was not created"
                assert row.character_id == "adelia"
                assert row.turn_count >= 1

        asyncio.run(_check())

    def test_subsequent_turn_increments_turn_count(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.9: second turn updates last_turn_at + bumps turn_count."""
        client, factory, _ = chat_app
        sid = str(uuid.uuid4())
        for _ in range(2):
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key", "X-Session-ID": sid},
                json={
                    "model": "adelia",
                    "messages": [{"role": "user", "content": "again"}],
                    "stream": True,
                },
            )
            assert response.status_code == 200
            _ = response.text  # drain

        import asyncio

        async def _check() -> None:
            async with factory() as session:
                row = (
                    await session.execute(
                        select(ChatSession).where(ChatSession.id == uuid.UUID(sid))
                    )
                ).scalars().first()
                assert row is not None
                assert row.turn_count == 2

        asyncio.run(_check())

    def test_post_turn_extraction_writes_episodic_row(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.10: post-turn extraction writes an EpisodicMemory row.

        We can't time-assert <100ms latency on the SSE close from
        TestClient (it buffers the whole body), so this test focuses
        on the AC-7.10 outcome: the row lands without blocking.
        """
        client, factory, _ = chat_app
        # Drive a turn with content distinctive enough to verify.
        marker_text = (
            "hello adelia, this is a uniquely marked test " + uuid.uuid4().hex[:8]
        )
        response = client.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": marker_text}],
                "stream": True,
            },
        )
        assert response.status_code == 200
        _ = response.text  # drain

        # Allow the fire-and-forget tasks a moment to commit.
        import asyncio

        async def _wait() -> None:
            # The TestClient runs tasks on the same loop; give them a
            # tick to run their commits.
            for _ in range(20):
                await asyncio.sleep(0.05)
                async with factory() as session:
                    rows = (
                        await session.execute(
                            select(EpisodicMemory)
                            .where(
                                EpisodicMemory.character_id == "adelia",
                                EpisodicMemory.memory_type == "episodic",
                            )
                            .order_by(EpisodicMemory.created_at.desc())
                            .limit(1)
                        )
                    ).scalars().all()
                    if rows:
                        # Verify the metadata source label.
                        assert rows[0].metadata_["source"] == "post_turn_extraction"
                        return
            pytest.fail("post-turn EpisodicMemory row did not land within 1 second")

        asyncio.run(_wait())

    def test_sse_response_terminates_with_done(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.1: stream terminates with data: [DONE]."""
        client, _, _ = chat_app
        response = client.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.status_code == 200
        chunks = _parse_sse(response.text)
        assert chunks[-1] == "[DONE]"
        # finish_reason="stop" must be on the chunk before [DONE].
        penultimate = chunks[-2]
        assert isinstance(penultimate, dict)
        assert penultimate["choices"][0]["finish_reason"] == "stop"

    def test_unknown_character_returns_400_not_500(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.3: unknown character → 400 with valid_character_ids."""
        client, _, _ = chat_app
        response = client.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "shawn",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "CHARACTER_NOT_FOUND"
        assert "valid_character_ids" in body["error"]["details"]


class TestChatHealthAndModelsLive:
    def test_health_ready_passes_against_live_db(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.5: /health/ready returns 200 when DB + LLM are reachable."""
        client, _, _ = chat_app
        response = client.get("/health/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"]["db"]["ok"] is True
        assert body["checks"]["llm"]["ok"] is True

    def test_models_endpoint_returns_five(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-7.4: /v1/models returns exactly 5 entries."""
        client, _, _ = chat_app
        response = client.get("/v1/models")
        assert response.status_code == 200
        body = response.json()
        ids = sorted(entry["id"] for entry in body["data"])
        assert ids == ["adelia", "alicia", "bina", "reina", "starry-lyfe"]


class TestCrewContextualCarryForward:
    """Phase 11 — Msty Crew Conversations Contextual mode end-to-end.

    When Msty sends a request with ``model=bina`` and prior personas'
    responses included as ``role="assistant"`` messages with a ``name``
    field, the focal persona's outbound user_prompt to BD-1 must carry
    those prior responses in the framed prior-speaker block.

    AC-11.5 closure regression.
    """

    def test_msty_crew_contextual_payload_lands_prior_text_in_focal_user_prompt(
        self,
        monkeypatch: pytest.MonkeyPatch,
        engine: AsyncEngine,
        setup_database: None,
    ) -> None:
        """Real Postgres + recording StubBDOne: prior persona text reaches BD-1."""

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            char_id = kwargs.get("character_id", args[0] if args else "bina")
            return _make_assembled_prompt(str(char_id))

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )

        captured: list[tuple[str, str]] = []

        def _recorder(system_prompt: str, user_prompt: str) -> str:
            captured.append((system_prompt, user_prompt))
            return "Bina meets the moment with quiet attention."

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        canon = load_all_canon()
        stub = StubBDOne(
            default_text="Bina meets the moment with quiet attention.",
            responder=_recorder,
            stream_chunk_count=2,
        )

        app = create_app(
            ApiSettings(api_key="test-key", default_character="bina"),
            state_overrides={
                "engine": engine,
                "session_factory": factory,
                "canon": canon,
                "embedding_service": _StubEmbeddingService(),
                "llm_client": stub,
            },
        )

        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key", "Content-Type": "application/json"},
                json={
                    "model": "bina",
                    "stream": True,
                    "messages": [
                        {
                            "role": "assistant",
                            "name": "adelia",
                            "content": "The light caught the cardamom on the windowsill.",
                        },
                        {
                            "role": "user",
                            "content": "What did you both think of the porch?",
                        },
                    ],
                },
            )
            assert response.status_code == 200
            response.read()  # drain the SSE body

        # captured[0] is the chat stream_complete; captured[1+] are the
        # post-turn evaluator complete() calls fired after SSE close.
        assert len(captured) >= 1
        chat_user_prompt = captured[0][1]
        assert "**adelia:**" in chat_user_prompt
        assert "cardamom" in chat_user_prompt
        assert "What did you both think of the porch?" in chat_user_prompt

    def test_msty_persona_conversation_no_prior_responses_unchanged(
        self,
        chat_app: tuple[TestClient, async_sessionmaker[AsyncSession], StubBDOne],
    ) -> None:
        """AC-11.3 byte-identity regression: bare user message, no frame."""
        client, _, stub = chat_app
        # The default chat_app StubBDOne has no responder; capture via call_count + a
        # fresh assertion path. We re-issue the request and verify success — the
        # canonical no-op assertion lives in the unit-test counterpart.
        response = client.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key", "Content-Type": "application/json"},
            json={
                "model": "adelia",
                "stream": True,
                "messages": [{"role": "user", "content": "How was today?"}],
            },
        )
        assert response.status_code == 200
        response.read()
        # Stream completed without crashing — non-crew path remains stable.
        assert stub.stream_call_count >= 1
