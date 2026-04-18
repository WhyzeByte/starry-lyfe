"""Msty Crew semantics in the HTTP pipeline.

Starry-Lyfe no longer fans a single request out into multiple speakers.
Msty Crew owns persona-per-bubble orchestration client-side. The backend
still reads Crew roster/history for scene context, but every request
returns exactly one routed persona response.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.context.types import AssembledPrompt, LayerContent
from starry_lyfe.dreams.llm import StubBDOne


@dataclass
class _DummyResult:
    def scalar(self) -> int:
        return 1

    def scalars(self) -> _DummyResult:
        return self

    def first(self) -> None:
        return None


class _DummySession:
    def __init__(self) -> None:
        self.info: dict[str, object] = {}

    async def execute(self, *args: object, **kwargs: object) -> _DummyResult:
        return _DummyResult()

    def add(self, _row: object) -> None:
        # chat_session.upsert_session calls .add(row) when no chat_sessions
        # row exists yet. The DummyResult.scalars().first() returns None
        # via the "missing attribute" path, so upsert_session takes the
        # insert branch. No-op here keeps the assertion focused on
        # LLM-call counts rather than DB writes.
        return None

    async def flush(self) -> None: ...

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


def _stub_assembled_prompt(character_id: str) -> AssembledPrompt:
    layer = LayerContent(
        name="persona_kernel",
        text=f"stub kernel for {character_id}",
        estimated_tokens=4,
        layer_number=1,
    )
    return AssembledPrompt(
        prompt=f"<PERSONA_KERNEL>\nstub for {character_id}\n</PERSONA_KERNEL>",
        character_id=character_id,
        layers=[layer],
        total_tokens=4,
        constraint_block_position="terminal",
    )


@pytest.fixture
def crew_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    from starry_lyfe.api.orchestration import pipeline as pipeline_module

    async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
        char_id = kwargs.get("character_id", "adelia")
        return _stub_assembled_prompt(str(char_id))

    async def _fake_alicia_home(_session: object) -> bool:
        return True

    async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
        return None

    monkeypatch.setattr(
        "starry_lyfe.api.orchestration.pipeline.assemble_context",
        _fake_assemble_context,
    )
    monkeypatch.setattr(pipeline_module, "retrieve_alicia_home", _fake_alicia_home)
    monkeypatch.setattr(pipeline_module, "retrieve_memories", _fake_retrieve_memories)
    monkeypatch.setattr(
        "starry_lyfe.api.endpoints.chat.schedule_post_turn_tasks",
        lambda *args, **kwargs: None,
    )

    app = create_app(
        ApiSettings(api_key="dev", default_character="adelia", crew_max_speakers=3),
        state_overrides={
            "session_factory": _DummyFactory(),
            "llm_client": StubBDOne(default_text="crew-response", stream_chunk_count=2),
            "engine": None,
            "canon": None,
            "embedding_service": None,
        },
    )
    with TestClient(app) as client:
        yield client


class TestMstyCrewRequests:
    def test_crew_request_returns_one_routed_persona_response(
        self, crew_app: TestClient
    ) -> None:
        response = crew_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "dev"},
            json={
                "model": "bina",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are speaking as one member of a crew "
                            "that includes adelia, bina, reina, alicia."
                        ),
                    },
                    {"role": "assistant", "name": "adelia", "content": "The kitchen's warm."},
                    {"role": "user", "content": "What do you think?"},
                ],
                "stream": True,
            },
        )
        assert response.status_code == 200
        assert response.headers["X-Character-ID"] == "bina"
        assert response.headers["X-Routing-Source"] == "model_field"
        assert "**Adelia:**" not in response.text
        assert "**Bina:**" not in response.text

    def test_legacy_all_marker_is_stripped_but_does_not_fan_out(
        self, crew_app: TestClient
    ) -> None:
        response = crew_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "dev"},
            json={
                "model": "reina",
                "messages": [
                    {
                        "role": "system",
                        "content": "crew: adelia bina reina alicia",
                    },
                    {"role": "user", "content": "/all talk about dinner"},
                ],
                "stream": True,
            },
        )
        assert response.status_code == 200
        assert response.headers["X-Character-ID"] == "reina"
        assert "**Reina:**" not in response.text

    def test_prior_persona_history_does_not_create_extra_llm_calls(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from starry_lyfe.api.orchestration import pipeline as pipeline_module

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            char_id = kwargs.get("character_id", "adelia")
            return _stub_assembled_prompt(str(char_id))

        async def _fake_alicia_home(_session: object) -> bool:
            return True

        async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
            return None

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )
        monkeypatch.setattr(pipeline_module, "retrieve_alicia_home", _fake_alicia_home)
        monkeypatch.setattr(pipeline_module, "retrieve_memories", _fake_retrieve_memories)
        monkeypatch.setattr(
            "starry_lyfe.api.endpoints.chat.schedule_post_turn_tasks",
            lambda *args, **kwargs: None,
        )

        recorded: list[tuple[str, str]] = []

        def _responder(system_prompt: str, user_prompt: str) -> str:
            recorded.append((system_prompt, user_prompt))
            return "single-speaker"

        stub = StubBDOne(responder=_responder, stream_chunk_count=1)
        app = create_app(
            ApiSettings(api_key="dev", default_character="adelia", crew_max_speakers=3),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )

        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "alicia",
                    "messages": [
                        {
                            "role": "system",
                            "content": "crew: adelia bina reina alicia",
                        },
                        {"role": "assistant", "name": "adelia", "content": "I can make tea."},
                        {"role": "assistant", "name": "bina", "content": "I've already boiled water."},
                        {"role": "user", "content": "Alicia, your take?"},
                    ],
                    "stream": True,
                },
            )

        assert response.status_code == 200
        assert stub.stream_call_count == 1, (
            f"expected exactly one streamed chat completion, got {stub.stream_call_count}"
        )
        # Phase 11 (AD-009): prior personas' responses are now injected into
        # the focal user_prompt as a `[Earlier in this conversation: ...]`
        # frame so the focal persona can riff on what the prior personas
        # said. The bare user message still appears at the end of the prompt.
        prompt_seen = recorded[0][1]
        assert "**adelia:**" in prompt_seen
        assert "I can make tea." in prompt_seen
        assert "**bina:**" in prompt_seen
        assert "I've already boiled water." in prompt_seen
        assert prompt_seen.rstrip().endswith("Alicia, your take?")

    def test_crew_roster_still_reaches_scene_state(
        self, crew_app: TestClient
    ) -> None:
        with crew_app as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "bina",
                    "messages": [
                        {
                            "role": "system",
                            "content": "crew: adelia bina reina alicia",
                        },
                        {"role": "assistant", "name": "adelia", "content": "I'm here."},
                        {"role": "user", "content": "Bina?"},
                    ],
                    "stream": True,
                },
            )
        assert response.status_code == 200
        result = crew_app.app.state.last_pipeline_result  # type: ignore[attr-defined]
        assert result is not None
        assert result.scene_state is not None
        assert result.scene_state.present_characters == [
            "adelia",
            "bina",
            "reina",
            "alicia",
            "whyze",
        ]
