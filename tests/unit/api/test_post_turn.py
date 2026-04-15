"""Unit tests for memory_extraction + post_turn fire-and-forget scheduler.

The scheduler is the load-bearing seam: when the SSE response closes,
post-turn tasks must run as ``asyncio.create_task`` (not awaited) so
the response body terminates first. AC-7.10 enforces this; the
unit test below proves the contract via timing.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from starry_lyfe.api.orchestration.memory_extraction import extract_episodic
from starry_lyfe.api.orchestration.post_turn import (
    await_post_turn_tasks,
    schedule_post_turn_tasks,
)
from starry_lyfe.dreams.llm import StubBDOne

# --- Fake session factory that records add() calls -------------------------


class _RecordingSession:
    def __init__(self, store: list[Any]) -> None:
        self._store = store
        self.info: dict[str, Any] = {}

    async def execute(self, *args: object, **kwargs: object) -> Any:  # noqa: ANN401
        return _NoneScalars()

    def add(self, instance: Any) -> None:
        self._store.append(instance)

    async def flush(self) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def close(self) -> None: ...

    def begin(self) -> _BeginCtx:
        return _BeginCtx()

    async def __aenter__(self) -> _RecordingSession:
        return self

    async def __aexit__(self, *_: object) -> None: ...


class _NoneScalars:
    def scalars(self) -> _NoneInner:
        return _NoneInner()


class _NoneInner:
    def first(self) -> None:
        return None


class _BeginCtx:
    async def __aenter__(self) -> None: ...
    async def __aexit__(self, *_: object) -> None: ...


class _RecordingFactory:
    def __init__(self) -> None:
        self.added: list[Any] = []

    def __call__(self) -> _RecordingSession:
        return _RecordingSession(self.added)


class TestExtractEpisodic:
    async def test_writes_episodic_row_to_session(self) -> None:
        factory = _RecordingFactory()
        stub = StubBDOne(default_text="that conversation lit something up.")
        new_id = await extract_episodic(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            user_message="hey",
            full_response_text="hello back",
            chat_session_id=uuid.uuid4(),
            llm_client=stub,
        )
        assert new_id is not None
        assert len(factory.added) == 1
        row = factory.added[0]
        assert row.character_id == "adelia"
        assert row.memory_type == "episodic"
        assert "lit something up" in row.event_summary
        assert row.metadata_["source"] == "post_turn_extraction"

    async def test_unknown_character_returns_none(self) -> None:
        factory = _RecordingFactory()
        result = await extract_episodic(
            factory,  # type: ignore[arg-type]
            character_id="shawn",
            user_message="hey",
            full_response_text="hi",
            chat_session_id=None,
            llm_client=StubBDOne(),
        )
        assert result is None
        assert factory.added == []

    async def test_empty_response_returns_none(self) -> None:
        factory = _RecordingFactory()
        result = await extract_episodic(
            factory,  # type: ignore[arg-type]
            character_id="bina",
            user_message="hey",
            full_response_text="   \n   ",
            chat_session_id=None,
            llm_client=StubBDOne(),
        )
        assert result is None
        assert factory.added == []

    async def test_llm_failure_returns_none_no_write(self) -> None:
        factory = _RecordingFactory()
        failing = StubBDOne(fail_next_n=1)
        result = await extract_episodic(
            factory,  # type: ignore[arg-type]
            character_id="reina",
            user_message="hey",
            full_response_text="court was sharp today",
            chat_session_id=None,
            llm_client=failing,
        )
        assert result is None
        assert factory.added == []


class TestSchedulePostTurnTasks:
    async def test_returns_three_running_tasks(self) -> None:
        """Phase 9 (2026-04-15): three fire-and-forget tasks per turn —
        extract_episodic + evaluate_and_update (Whyze-dyad) +
        evaluate_and_update_internal (inter-woman dyads)."""
        factory = _RecordingFactory()
        stub = StubBDOne(default_text="reflective summary line.")
        tasks = schedule_post_turn_tasks(
            factory,  # type: ignore[arg-type]
            character_id="adelia",
            user_message="hi",
            full_response_text="we sat warm and close on the porch",
            chat_session_id=uuid.uuid4(),
            llm_client=stub,
        )
        assert len(tasks) == 3
        # All three tasks have descriptive names for log correlation.
        assert any("extract_episodic" in t.get_name() for t in tasks)
        assert any(
            "evaluate_and_update[" in t.get_name() for t in tasks
        ), "whyze evaluator task missing"
        assert any(
            "evaluate_and_update_internal" in t.get_name() for t in tasks
        ), "inter-woman evaluator task missing"
        # Drain so pytest doesn't warn about unawaited tasks.
        await await_post_turn_tasks(tasks)

    async def test_caller_does_not_block_on_completion(self) -> None:
        """AC-7.10: schedule_post_turn_tasks returns synchronously fast.

        The two tasks may take measurable time but the call site
        returns within ms, regardless of task duration.
        """
        factory = _RecordingFactory()
        stub = StubBDOne(default_text="one liner")
        start = time.monotonic()
        tasks = schedule_post_turn_tasks(
            factory,  # type: ignore[arg-type]
            character_id="bina",
            user_message="hi",
            full_response_text="logged for the record",
            chat_session_id=None,
            llm_client=stub,
        )
        scheduled_in = time.monotonic() - start
        # Scheduling MUST be near-instant — well under the 100ms AC.
        assert scheduled_in < 0.1, f"schedule took {scheduled_in:.3f}s; AC-7.10 demands <100ms"
        # Drain to clean up.
        await await_post_turn_tasks(tasks)

    async def test_failing_task_does_not_propagate(self) -> None:
        factory = _RecordingFactory()
        failing = StubBDOne(fail_next_n=10)  # ample failures
        tasks = schedule_post_turn_tasks(
            factory,  # type: ignore[arg-type]
            character_id="alicia",
            user_message="hi",
            full_response_text="body knows the way",
            chat_session_id=None,
            llm_client=failing,
        )
        # Awaiting must not raise even though the extraction LLM failed.
        await await_post_turn_tasks(tasks)
        # Tasks ran but no exception leaked to the caller.
        for t in tasks:
            # done() is True; exceptions are silently logged via callback.
            assert t.done()
