"""F1 closure: Crew sequencing in the HTTP pipeline.

Pre-F1 the ``/v1/chat/completions`` endpoint emitted a single-speaker
SSE stream even when the request carried ``/all`` or a Msty Crew
roster — Step 9 of the documented 12-step flow was absent. These tests
cover the restored Crew loop: multi-speaker expansion, Rule of One,
``crew_max_speakers`` cap, and ``activity_context`` propagation to the
Scene Director scorer.

Stubs (not DB): ``retrieve_memories`` and ``_retrieve_dyads_for_scene``
are monkey-patched so the tests exercise the orchestration + scorer
wiring without requiring live Postgres. Integration coverage against
real data boundaries remains in ``tests/integration/test_http_chat.py``.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

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


class _DummySession:
    """Async session stand-in that captures `info` for pipeline result inspection."""

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
    """Stubbed app wired for Crew tests.

    - ``retrieve_memories`` → returns ``None`` so the assembler path uses
      an empty bundle but does not crash.
    - ``_retrieve_dyads_for_scene`` → empty list (scorer runs without
      dyad deltas; base + salience rules still fire).
    - ``retrieve_alicia_home`` → True.
    - ``assemble_context`` → stub per-character prompts.
    """
    from starry_lyfe.api.orchestration import pipeline as pipeline_module

    async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
        char_id = kwargs.get("character_id", "adelia")
        return _stub_assembled_prompt(str(char_id))

    async def _fake_alicia_home(_session: object) -> bool:
        return True

    async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
        return None

    async def _fake_retrieve_dyads(*_a: object, **_k: object) -> list[Any]:
        return []

    monkeypatch.setattr(
        "starry_lyfe.api.orchestration.pipeline.assemble_context",
        _fake_assemble_context,
    )
    monkeypatch.setattr(pipeline_module, "retrieve_alicia_home", _fake_alicia_home)
    monkeypatch.setattr(pipeline_module, "retrieve_memories", _fake_retrieve_memories)
    monkeypatch.setattr(
        pipeline_module, "_retrieve_dyads_for_scene", _fake_retrieve_dyads
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


def _collect_attribution_markers(body: str) -> list[str]:
    """Extract `**Name:**` attribution markers from the reassembled SSE body."""
    # Walk the SSE data lines, pick content deltas, reassemble, then
    # match the attribution pattern.
    import json

    pieces: list[str] = []
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            continue
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue
        choices = chunk.get("choices") or []
        if not choices:
            continue
        content = choices[0].get("delta", {}).get("content")
        if content:
            pieces.append(str(content))
    full = "".join(pieces)
    return re.findall(r"\*\*([A-Z][a-z]+):\*\*", full)


class TestCrewFlow:
    def test_slash_all_expands_multi_speaker(self, crew_app: TestClient) -> None:
        """F1 core contract: `/all` produces ≥2 attribution markers.

        Msty/OWUI populate the roster via the system prompt; naming the
        women there lets the Msty preprocessor fill ``scene_characters``
        before the pipeline runs. `/all` then flips ``all_override`` so
        Crew mode engages even with no prior turns.
        """
        response = crew_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "dev"},
            json={
                "model": "adelia",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a crew of adelia, bina, reina, alicia.",
                    },
                    {"role": "user", "content": "/all talk about dinner"},
                ],
                "stream": True,
            },
        )
        assert response.status_code == 200
        speakers = _collect_attribution_markers(response.text)
        assert len(speakers) >= 2, (
            f"expected ≥2 speakers in Crew mode, got {speakers!r} "
            f"(body: {response.text[:400]})"
        )

    def test_crew_respects_rule_of_one(self, crew_app: TestClient) -> None:
        """No character speaks twice in a single Crew turn."""
        response = crew_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "dev"},
            json={
                "model": "adelia",
                "messages": [
                    {
                        "role": "system",
                        "content": "crew: adelia bina reina alicia",
                    },
                    {"role": "user", "content": "/all hi crew"},
                ],
                "stream": True,
            },
        )
        speakers = _collect_attribution_markers(response.text)
        assert len(speakers) == len(set(speakers)), (
            f"Rule of One violated — duplicate speakers in {speakers!r}"
        )

    def test_crew_max_speakers_cap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setting crew_max_speakers=2 caps emission at exactly 2 speakers."""
        from starry_lyfe.api.orchestration import pipeline as pipeline_module

        async def _fake_assemble_context(*args: object, **kwargs: object) -> AssembledPrompt:
            return _stub_assembled_prompt(str(kwargs.get("character_id", "adelia")))

        async def _fake_alicia_home(_session: object) -> bool:
            return True

        async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
            return None

        async def _fake_retrieve_dyads(*_a: object, **_k: object) -> list[Any]:
            return []

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_alicia_home", _fake_alicia_home
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_memories", _fake_retrieve_memories
        )
        monkeypatch.setattr(
            pipeline_module, "_retrieve_dyads_for_scene", _fake_retrieve_dyads
        )

        app = create_app(
            ApiSettings(api_key="dev", crew_max_speakers=2),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": StubBDOne(default_text="x", stream_chunk_count=1),
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
                    "model": "adelia",
                    "messages": [
                        {
                            "role": "system",
                            "content": "crew: adelia bina reina alicia",
                        },
                        {"role": "user", "content": "/all chat"},
                    ],
                    "stream": True,
                },
            )
        speakers = _collect_attribution_markers(response.text)
        assert len(speakers) == 2, (
            f"crew_max_speakers=2 must cap at 2, got {len(speakers)}: {speakers!r}"
        )

    def test_crew_increments_counter_per_speaker(
        self, crew_app: TestClient
    ) -> None:
        """Each Crew speaker moves the http_sse_tokens_total counter
        under their own character_id label."""
        from starry_lyfe.api.endpoints.metrics import http_sse_tokens_total

        # Snapshot all possible character labels before.
        before = {
            c: http_sse_tokens_total.labels(character_id=c)._value.get()  # type: ignore[attr-defined]
            for c in ("adelia", "bina", "reina", "alicia")
        }

        crew_app.post(
            "/v1/chat/completions",
            headers={"X-API-Key": "dev"},
            json={
                "model": "adelia",
                "messages": [
                    {
                        "role": "system",
                        "content": "crew: adelia bina reina alicia",
                    },
                    {"role": "user", "content": "/all speak"},
                ],
                "stream": True,
            },
        )

        after = {
            c: http_sse_tokens_total.labels(character_id=c)._value.get()  # type: ignore[attr-defined]
            for c in ("adelia", "bina", "reina", "alicia")
        }
        moved = [c for c in before if after[c] > before[c]]
        assert len(moved) >= 2, (
            f"expected ≥2 character counters to move, got {moved!r} "
            f"(before={before}, after={after})"
        )


class TestR2F1CarryForward:
    """R2-F1 closure: Step 9 validated-output carry-forward.

    Later Crew speakers must see earlier speakers' validated text in their
    LLM ``user_prompt`` — the anti-"NPC Competition collapse" contract
    from ``IMPLEMENTATION_PLAN_v7.1.md §7``.
    """

    def _build_recording_app(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> tuple[TestClient, list[tuple[str, str]]]:
        """App fixture that records every (system_prompt, user_prompt)
        tuple that reaches the LLM. Returns (client, recorded_calls)."""
        from starry_lyfe.api.orchestration import pipeline as pipeline_module

        async def _fake_assemble_context(
            *args: object, **kwargs: object
        ) -> AssembledPrompt:
            return _stub_assembled_prompt(
                str(kwargs.get("character_id", "adelia"))
            )

        async def _fake_alicia_home(_session: object) -> bool:
            return True

        async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
            return None

        async def _fake_retrieve_dyads(*_a: object, **_k: object) -> list[Any]:
            return []

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_alicia_home", _fake_alicia_home
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_memories", _fake_retrieve_memories
        )
        monkeypatch.setattr(
            pipeline_module, "_retrieve_dyads_for_scene", _fake_retrieve_dyads
        )

        recorded: list[tuple[str, str]] = []

        def _recording_responder(system_prompt: str, user_prompt: str) -> str:
            recorded.append((system_prompt, user_prompt))
            # Return a distinctive, per-call response so the carry-forward
            # block in subsequent calls contains something identifiable.
            call_index = len(recorded)
            return f"PRIOR-{call_index}-{len(recorded)}"

        stub = StubBDOne(
            responder=_recording_responder, stream_chunk_count=1
        )
        app = create_app(
            ApiSettings(api_key="dev", crew_max_speakers=3),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )
        return TestClient(app), recorded

    def test_speaker_a_user_prompt_is_unchanged(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Speaker 1 sees the cleaned user message with no carry-forward block."""
        client, recorded = self._build_recording_app(monkeypatch)
        with client as c:
            c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
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
        assert len(recorded) >= 1, "expected ≥1 LLM call"
        first_system, first_user = recorded[0]
        # Inline override stripped; no carry-forward block for speaker 1.
        assert first_user == "talk about dinner", (
            f"speaker 1 user_prompt must be the cleaned message alone, "
            f"got {first_user!r}"
        )
        assert "[Earlier this turn:" not in first_user

    def test_speaker_b_user_prompt_contains_speaker_a_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Speaker 2 sees an '[Earlier this turn: ...]' block carrying
        speaker 1's validated text."""
        client, recorded = self._build_recording_app(monkeypatch)
        with client as c:
            c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
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
        assert len(recorded) >= 2, (
            f"expected ≥2 LLM calls for Crew, got {len(recorded)}"
        )
        _, second_user = recorded[1]
        # The recording responder returned "PRIOR-1-1" to speaker 1;
        # speaker 2's carry-forward block must contain that.
        assert "[Earlier this turn:" in second_user, (
            f"speaker 2 user_prompt must carry the Step 9 prior block, "
            f"got {second_user!r}"
        )
        assert "PRIOR-1" in second_user, (
            f"speaker 2 user_prompt must quote speaker 1's emitted text, "
            f"got {second_user!r}"
        )
        # Original user message still present at the end.
        assert second_user.rstrip().endswith("talk about dinner")

    def test_failed_speaker_is_not_carried_forward(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A Whyze-Byte FAIL does not become Step 9 carry-forward context."""
        from starry_lyfe.api.orchestration import pipeline as pipeline_module
        from starry_lyfe.validation.whyze_byte import (
            ValidationResult,
            ValidationViolation,
            ViolationTier,
        )

        validation_call_count = 0

        def _fake_validate_response(
            *,
            character_id: str,
            response_text: str,
            scene_state: object,
        ) -> ValidationResult:
            nonlocal validation_call_count
            validation_call_count += 1
            if validation_call_count == 1:
                return ValidationResult(
                    character_id=character_id,
                    passed=False,
                    violations=[
                        ValidationViolation(
                            tier=ViolationTier.FAIL,
                            code="TEST_FAIL",
                            message="synthetic fail for carry-forward regression",
                            evidence=response_text,
                        )
                    ],
                )
            return ValidationResult(
                character_id=character_id,
                passed=True,
                violations=[],
            )

        monkeypatch.setattr(
            pipeline_module, "validate_response", _fake_validate_response
        )
        client, recorded = self._build_recording_app(monkeypatch)
        with client as c:
            response = c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
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
        assert "WHYZE_BYTE_FAIL" in response.text, "sanity: first speaker must fail"
        assert len(recorded) >= 2, (
            f"expected ≥2 LLM calls for Crew, got {len(recorded)}"
        )
        _, second_user = recorded[1]
        assert second_user == "talk about dinner", (
            "failed prior output must not be carried into speaker 2's prompt"
        )
        assert "[Earlier this turn:" not in second_user
        assert "PRIOR-1" not in second_user

    def test_speaker_c_user_prompt_carries_all_prior_speakers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Three-speaker turn: speaker 3's block references both A and B."""
        client, recorded = self._build_recording_app(monkeypatch)
        with client as c:
            c.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
                    "messages": [
                        {
                            "role": "system",
                            "content": "crew: adelia bina reina alicia",
                        },
                        {"role": "user", "content": "/all chat"},
                    ],
                    "stream": True,
                },
            )
        if len(recorded) < 3:
            pytest.skip(
                f"scorer selected only {len(recorded)} speakers "
                f"(expected ≥3 for this assertion)"
            )
        _, third_user = recorded[2]
        assert "[Earlier this turn:" in third_user
        # Speaker 3 must see BOTH prior speakers' text.
        assert "PRIOR-1" in third_user
        assert "PRIOR-2" in third_user


class TestR2F2CounterSemantics:
    """R2-F2 closure: uniform counter semantics.

    ``http_sse_tokens_total`` moves exactly once per upstream LLM delta
    in BOTH single-speaker and Crew modes. Attribution markers and
    separators are SSE frame content and do NOT increment the counter.
    """

    def test_crew_counter_matches_llm_deltas_exactly(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Counter delta per speaker == exact LLM delta count per speaker.

        Parses the SSE body for content chunks and attribution markers
        separately. The counter MUST equal (total content chunks −
        attribution chunks − separator chunks), i.e. only the upstream
        LLM deltas.
        """
        import json
        import re as _re

        from starry_lyfe.api.endpoints.metrics import http_sse_tokens_total
        from starry_lyfe.api.orchestration import pipeline as pipeline_module

        async def _fake_assemble_context(
            *args: object, **kwargs: object
        ) -> AssembledPrompt:
            return _stub_assembled_prompt(
                str(kwargs.get("character_id", "adelia"))
            )

        async def _fake_alicia_home(_session: object) -> bool:
            return True

        async def _fake_retrieve_memories(*_a: object, **_k: object) -> None:
            return None

        async def _fake_retrieve_dyads(*_a: object, **_k: object) -> list[Any]:
            return []

        monkeypatch.setattr(
            "starry_lyfe.api.orchestration.pipeline.assemble_context",
            _fake_assemble_context,
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_alicia_home", _fake_alicia_home
        )
        monkeypatch.setattr(
            pipeline_module, "retrieve_memories", _fake_retrieve_memories
        )
        monkeypatch.setattr(
            pipeline_module, "_retrieve_dyads_for_scene", _fake_retrieve_dyads
        )

        stub = StubBDOne(default_text="payload", stream_chunk_count=3)
        app = create_app(
            ApiSettings(api_key="dev", crew_max_speakers=2),
            state_overrides={
                "session_factory": _DummyFactory(),
                "llm_client": stub,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )

        before = {
            c: http_sse_tokens_total.labels(character_id=c)._value.get()  # type: ignore[attr-defined]
            for c in ("adelia", "bina", "reina", "alicia")
        }

        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                headers={"X-API-Key": "dev"},
                json={
                    "model": "adelia",
                    "messages": [
                        {
                            "role": "system",
                            "content": "crew: adelia bina reina alicia",
                        },
                        {"role": "user", "content": "/all chat"},
                    ],
                    "stream": True,
                },
            )

        after = {
            c: http_sse_tokens_total.labels(character_id=c)._value.get()  # type: ignore[attr-defined]
            for c in ("adelia", "bina", "reina", "alicia")
        }
        moved = {c: after[c] - before[c] for c in before if after[c] > before[c]}
        assert len(moved) == 2, (
            f"expected exactly 2 speakers (crew_max_speakers=2), got {moved!r}"
        )

        # Decode SSE to separate attribution markers, separators, and
        # LLM deltas. Counter should equal ONLY the LLM delta count.
        content_chunks: list[str] = []
        for line in response.text.splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[len("data:") :].strip()
            if payload == "[DONE]":
                continue
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            content = choices[0].get("delta", {}).get("content")
            if content:
                content_chunks.append(str(content))
        attribution_count = sum(
            1 for c in content_chunks if _re.match(r"^\*\*[A-Z][a-z]+:\*\*\s*$", c)
        )
        separator_count = sum(1 for c in content_chunks if c == "\n\n")
        llm_delta_count = len(content_chunks) - attribution_count - separator_count
        total_counter_move = sum(moved.values())
        assert total_counter_move == float(llm_delta_count), (
            f"counter total +{total_counter_move} must equal LLM delta count "
            f"{llm_delta_count} (content={len(content_chunks)}, "
            f"attribution={attribution_count}, separator={separator_count}). "
            f"If higher, attribution markers are still incrementing (R2-F2 regression)."
        )


class TestCrewDetection:
    """Unit tests for _is_crew_mode decision function."""

    def test_all_override_triggers_crew(self) -> None:
        from starry_lyfe.api.orchestration.pipeline import (
            PipelineContext,
            _is_crew_mode,
        )
        from starry_lyfe.api.routing.character import CharacterRoutingDecision
        from starry_lyfe.api.routing.msty import MstyPreprocessed

        ctx = PipelineContext(
            request=None,  # type: ignore[arg-type]
            routing=CharacterRoutingDecision(
                character_id="adelia", source="inline_override",
                raw_value="/all", all_override=True,
            ),
            msty=MstyPreprocessed(
                user_message="talk",
                scene_characters=[],
                prior_responses=[],
                system_prompt_text="",
            ),
            session=None,  # type: ignore[arg-type]
            canon=None,  # type: ignore[arg-type]
            llm_client=None,  # type: ignore[arg-type]
            embedding_service=None,  # type: ignore[arg-type]
        )
        assert _is_crew_mode(ctx) is True

    def test_single_speaker_without_override_is_not_crew(self) -> None:
        from starry_lyfe.api.orchestration.pipeline import (
            PipelineContext,
            _is_crew_mode,
        )
        from starry_lyfe.api.routing.character import CharacterRoutingDecision
        from starry_lyfe.api.routing.msty import MstyPreprocessed

        ctx = PipelineContext(
            request=None,  # type: ignore[arg-type]
            routing=CharacterRoutingDecision(
                character_id="adelia", source="model_field", raw_value="adelia",
            ),
            msty=MstyPreprocessed(
                user_message="hi",
                scene_characters=[],
                prior_responses=[],
                system_prompt_text="",
            ),
            session=None,  # type: ignore[arg-type]
            canon=None,  # type: ignore[arg-type]
            llm_client=None,  # type: ignore[arg-type]
            embedding_service=None,  # type: ignore[arg-type]
        )
        assert _is_crew_mode(ctx) is False

    def test_crew_roster_without_prior_responses_is_not_crew(self) -> None:
        """Msty sometimes names the roster in the system prompt without
        replaying history — first turn of a Crew Conversation. That is
        single-speaker, not Crew."""
        from starry_lyfe.api.orchestration.pipeline import (
            PipelineContext,
            _is_crew_mode,
        )
        from starry_lyfe.api.routing.character import CharacterRoutingDecision
        from starry_lyfe.api.routing.msty import MstyPreprocessed

        ctx = PipelineContext(
            request=None,  # type: ignore[arg-type]
            routing=CharacterRoutingDecision(
                character_id="adelia", source="model_field", raw_value="adelia",
            ),
            msty=MstyPreprocessed(
                user_message="hi",
                scene_characters=["adelia", "bina"],
                prior_responses=[],
                system_prompt_text="crew roster",
            ),
            session=None,  # type: ignore[arg-type]
            canon=None,  # type: ignore[arg-type]
            llm_client=None,  # type: ignore[arg-type]
            embedding_service=None,  # type: ignore[arg-type]
        )
        assert _is_crew_mode(ctx) is False
