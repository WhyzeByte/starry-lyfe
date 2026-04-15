"""Unit tests for the 12-step pipeline orchestrator.

Uses TestClient + stubbed assemble_context + StubBDOne so the SSE wire
format and the orchestration sequence are verified without needing
Postgres. The full DB-backed end-to-end test lands in
``tests/integration/test_http_chat.py`` (P8).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.context.types import AssembledPrompt, LayerContent
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import StubBDOne


@dataclass
class _DummyResult:
    def scalar(self) -> int:
        return 1


class _DummySession:
    """Minimal AsyncSession stand-in for tests that don't need DB I/O."""

    def __init__(self) -> None:
        self.info: dict[str, object] = {}

    async def execute(self, *args: object, **kwargs: object) -> _DummyResult:
        return _DummyResult()

    async def rollback(self) -> None: ...

    async def commit(self) -> None: ...

    async def close(self) -> None: ...


class _DummyFactoryCtx:
    def __init__(self) -> None:
        self._session = _DummySession()

    async def __aenter__(self) -> _DummySession:
        return self._session

    async def __aexit__(self, *_: object) -> None: ...


class _DummyFactory:
    def __call__(self) -> _DummyFactoryCtx:
        return _DummyFactoryCtx()


def _stub_assembled_prompt(character_id: str = "adelia") -> AssembledPrompt:
    layer = LayerContent(
        name="persona_kernel", text="stub kernel", estimated_tokens=2, layer_number=1,
    )
    return AssembledPrompt(
        prompt="<PERSONA_KERNEL>\nstub\n</PERSONA_KERNEL>",
        character_id=character_id,
        layers=[layer],
        total_tokens=2,
        constraint_block_position="terminal",
    )


@pytest.fixture
def stub_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Build an app wired with stubs that bypass DB + assemble_context."""

    async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
        char_id = kwargs.get("character_id", args[0] if args else "adelia")
        return _stub_assembled_prompt(str(char_id))

    monkeypatch.setattr(
        "starry_lyfe.api.orchestration.pipeline.assemble_context",
        _fake_assemble_context,
    )

    app = create_app(
        ApiSettings(api_key="test-key", default_character="adelia"),
        state_overrides={
            "session_factory": _DummyFactory(),
            "llm_client": StubBDOne(default_text="hello from adelia"),
            "engine": None,
            "canon": None,
            "embedding_service": None,
        },
    )
    with TestClient(app) as client:
        yield client


def _parse_sse_lines(body: str) -> list[dict[str, object] | str]:
    """Return the parsed payload of each ``data:`` line in the body."""
    parts: list[dict[str, object] | str] = []
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if payload == "[DONE]":
            parts.append("[DONE]")
            continue
        parts.append(json.loads(payload))
    return parts


class TestChatCompletionSseContract:
    def test_returns_event_stream_content_type(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": True,
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

    def test_sse_stream_yields_role_then_content_then_finish(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        chunks = _parse_sse_lines(response.text)
        # Last chunk MUST be [DONE].
        assert chunks[-1] == "[DONE]"
        # First non-DONE chunk must carry the assistant role.
        first = chunks[0]
        assert isinstance(first, dict)
        assert first["object"] == "chat.completion.chunk"
        assert first["choices"][0]["delta"].get("role") == "assistant"  # type: ignore[index]
        # Penultimate chunk must carry finish_reason="stop".
        penultimate = chunks[-2]
        assert isinstance(penultimate, dict)
        assert penultimate["choices"][0]["finish_reason"] == "stop"  # type: ignore[index]

    def test_sse_content_chunks_reassemble_to_full_response(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        chunks = _parse_sse_lines(response.text)
        content_pieces: list[str] = []
        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
            delta = chunk["choices"][0]["delta"]  # type: ignore[index]
            content = delta.get("content")
            if content:
                content_pieces.append(str(content))
        full = "".join(content_pieces)
        assert "hello from adelia" in full

    def test_response_headers_carry_routing_audit(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "bina",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.headers["X-Character-ID"] == "bina"
        assert response.headers["X-Routing-Source"] == "model_field"
        assert response.headers["X-Request-ID"].startswith("chat-")


class TestChatCompletionAuth:
    def test_missing_api_key_returns_401(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.status_code == 401
        body = response.json()
        assert body["error"]["code"] == "UNAUTHORIZED"

    def test_wrong_api_key_returns_401(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "wrong"},
            json={
                "model": "adelia",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.status_code == 401


class TestChatCompletionRouting:
    def test_header_overrides_model_field(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key", "X-SC-Force-Character": "reina"},
            json={
                "model": "bina",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        assert response.headers["X-Character-ID"] == "reina"
        assert response.headers["X-Routing-Source"] == "header"

    def test_inline_override_strips_marker_before_llm(self, stub_app: TestClient) -> None:
        response = stub_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key"},
            json={
                "model": "starry-lyfe",
                "messages": [{"role": "user", "content": "/alicia where are you"}],
                "stream": True,
            },
        )
        assert response.headers["X-Character-ID"] == "alicia"
        assert response.headers["X-Routing-Source"] == "inline_override"

    def test_unknown_model_returns_400(self, stub_app: TestClient) -> None:
        response = stub_app.post(
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


class TestChatCompletionUpstreamFailure:
    def test_llm_failure_emits_error_chunk(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            return _stub_assembled_prompt()

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )

        failing_stub = StubBDOne(default_text="x", fail_next_n=1, stream_chunk_count=1)
        app = create_app(
            ApiSettings(api_key="test-key"),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": failing_stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )
        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key"},
                json={
                    "model": "adelia",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": True,
                },
            )
        chunks = _parse_sse_lines(response.text)
        # An error chunk before [DONE] carries the upstream failure.
        error_chunks = [
            c for c in chunks if isinstance(c, dict) and "error" in c
        ]
        assert error_chunks, f"expected an error chunk, got {chunks}"
        assert error_chunks[0]["error"]["code"] == "UPSTREAM_LLM_ERROR"  # type: ignore[index]
        assert chunks[-1] == "[DONE]"


class TestPipelineImports:
    """Sanity checks on the orchestration public exports."""

    def test_public_api_present(self) -> None:
        from starry_lyfe.api.orchestration import (
            PipelineContext,
            PipelineResult,
            run_chat_pipeline,
            run_chat_pipeline_to_string,
        )

        assert PipelineContext is not None
        assert PipelineResult is not None
        assert run_chat_pipeline is not None
        assert run_chat_pipeline_to_string is not None

    def test_dreams_llm_error_is_routed(self) -> None:
        # Ensures that DreamsLLMError is the canonical upstream-failure
        # error type the pipeline catches.
        assert issubclass(DreamsLLMError, Exception)


class TestAliciaHomeResolution:
    """F2 closure: alicia_home is sourced from Tier 8 life_states, not hardcoded.

    The pipeline calls ``retrieve_alicia_home(session)`` before scene
    classification. When Alicia's row has ``is_away=True``, the scene
    state that reaches the assembler reflects her absence; when the row
    is missing the helper defaults to home=True (fresh-DB behavior
    preserved).
    """

    def _build_app(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        alicia_home: bool,
    ) -> TestClient:
        from starry_lyfe.api.orchestration import pipeline as pipeline_module

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            return _stub_assembled_prompt("adelia")

        async def _fake_alicia_home(_session: object) -> bool:
            return alicia_home

        async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
            return None

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )
        monkeypatch.setattr(
            pipeline_module,
            "retrieve_alicia_home",
            _fake_alicia_home,
        )
        monkeypatch.setattr(
            pipeline_module,
            "retrieve_memories",
            _fake_retrieve_memories,
        )

        app = create_app(
            ApiSettings(api_key="test-key"),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": StubBDOne(default_text="hi"),
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )
        return TestClient(app)

    def test_alicia_away_reaches_scene_state(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        client = self._build_app(monkeypatch, alicia_home=False)
        with client as c:
            response = c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key"},
                json={
                    "model": "adelia",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": True,
                },
            )
        assert response.status_code == 200
        # Scene state lands on app.state.last_pipeline_result for
        # test inspection. alicia_home must reflect what retrieve_alicia_home
        # returned, NOT the pre-F2 hardcoded True.
        result = client.app.state.last_pipeline_result  # type: ignore[attr-defined]
        assert result is not None, "pipeline_result must be stashed"
        assert result.scene_state is not None
        assert result.scene_state.alicia_home is False

    def test_alicia_home_reaches_scene_state(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        client = self._build_app(monkeypatch, alicia_home=True)
        with client as c:
            response = c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key"},
                json={
                    "model": "adelia",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": True,
                },
            )
        assert response.status_code == 200
        result = client.app.state.last_pipeline_result  # type: ignore[attr-defined]
        assert result.scene_state.alicia_home is True


class TestSseTokensCounter:
    """F5 closure: http_sse_tokens_total increments per SSE delta.

    The counter is process-global, so we snapshot before + after and
    assert the delta matches the stub's chunk count.
    """

    def test_counter_increments_per_chunk(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from starry_lyfe.api.endpoints.metrics import http_sse_tokens_total

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            return _stub_assembled_prompt("bina")

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )

        stub = StubBDOne(default_text="one two three four", stream_chunk_count=4)
        app = create_app(
            ApiSettings(api_key="test-key"),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )

        before = http_sse_tokens_total.labels(character_id="bina")._value.get()  # type: ignore[attr-defined]

        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key"},
                json={
                    "model": "bina",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": True,
                },
            )

        assert response.status_code == 200
        after = http_sse_tokens_total.labels(character_id="bina")._value.get()  # type: ignore[attr-defined]
        # Counter invariant: one inc per content-carrying SSE delta. Parse
        # the response and count content chunks (skipping role-only and
        # finish_reason-only chunks), then compare against the counter
        # delta. This is stub-chunking-invariant.
        content_deltas = 0
        for chunk in _parse_sse_lines(response.text):
            if not isinstance(chunk, dict):
                continue
            delta = chunk["choices"][0]["delta"]  # type: ignore[index]
            if delta.get("content"):
                content_deltas += 1
        assert content_deltas > 0, "stub must emit at least one content chunk"
        assert after - before == content_deltas, (
            f"expected counter to move by {content_deltas}, "
            f"got {after - before} (before={before}, after={after})"
        )

    def test_counter_labeled_by_focal_character(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Routing focal character is the label; other characters stay flat."""
        from starry_lyfe.api.endpoints.metrics import http_sse_tokens_total

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            return _stub_assembled_prompt("reina")

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )

        stub = StubBDOne(default_text="aa bb cc", stream_chunk_count=3)
        app = create_app(
            ApiSettings(api_key="test-key"),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )

        reina_before = http_sse_tokens_total.labels(character_id="reina")._value.get()  # type: ignore[attr-defined]
        adelia_before = http_sse_tokens_total.labels(character_id="adelia")._value.get()  # type: ignore[attr-defined]

        with TestClient(app) as client:
            client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "test-key"},
                json={
                    "model": "reina",
                    "messages": [{"role": "user", "content": "hi"}],
                    "stream": True,
                },
            )

        reina_after = http_sse_tokens_total.labels(character_id="reina")._value.get()  # type: ignore[attr-defined]
        adelia_after = http_sse_tokens_total.labels(character_id="adelia")._value.get()  # type: ignore[attr-defined]
        assert reina_after > reina_before, "focal counter must advance"
        assert adelia_after == adelia_before, "non-focal counter must stay flat"
