"""Fire-and-forget scheduler for post-turn tasks (E5/E6).

After the SSE response closes, the chat endpoint hands the captured
``PipelineResult`` to ``schedule_post_turn_tasks``. The function
spawns the memory extraction + relationship evaluator coroutines via
``asyncio.create_task`` with an ``add_done_callback`` that logs any
exception to MSE-6. The HTTP response has already returned by the
time these tasks run.

Failure isolation contract: an exception in either task MUST NOT
affect the next request. The done callback catches everything.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Iterable
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.dreams.llm import BDOne, StubBDOne

from .internal_relationship import evaluate_and_update_internal
from .memory_extraction import extract_episodic
from .relationship import evaluate_and_update

if TYPE_CHECKING:
    from starry_lyfe.api.config import ApiSettings

logger = logging.getLogger(__name__)


def _log_task_outcome(task: asyncio.Task[object]) -> None:
    """Drain task results so unhandled exceptions hit MSE-6 logs."""
    if task.cancelled():
        logger.warning("post_turn_task_cancelled", extra={"task_name": task.get_name()})
        return
    exc = task.exception()
    if exc is not None:
        logger.warning(
            "post_turn_task_failed",
            extra={"task_name": task.get_name(), "error": str(exc), "error_type": type(exc).__name__},
        )


def schedule_post_turn_tasks(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    character_id: str,
    user_message: str,
    full_response_text: str,
    chat_session_id: uuid.UUID | None,
    llm_client: BDOne | StubBDOne,
    settings: ApiSettings | None = None,
) -> list[asyncio.Task[object]]:
    """Spawn the post-turn coroutines as detached tasks.

    Returns the list of created tasks for tests to assert against;
    production code does not need to keep references — the tasks live
    on the event loop until they complete.
    """
    tasks: list[asyncio.Task[object]] = []

    # AC-7.10: extraction MUST not block the SSE close. asyncio.create_task
    # schedules the coroutine; control returns immediately.
    extraction_task = asyncio.create_task(
        extract_episodic(
            session_factory,
            character_id=character_id,
            user_message=user_message,
            full_response_text=full_response_text,
            chat_session_id=chat_session_id,
            llm_client=llm_client,
        ),
        name=f"post_turn_extract_episodic[{character_id}]",
    )
    extraction_task.add_done_callback(_log_task_outcome)
    tasks.append(extraction_task)

    # AC-7.11: relationship evaluator with ±0.03 cap.
    # Phase 8 (2026-04-15): llm_client + settings are threaded through so
    # the evaluator can take the LLM-primary path. Both are optional —
    # when omitted the evaluator falls back to the heuristic path.
    relationship_task = asyncio.create_task(
        evaluate_and_update(
            session_factory,
            character_id=character_id,
            response_text=full_response_text,
            llm_client=llm_client,
            settings=settings,
        ),
        name=f"post_turn_evaluate_and_update[{character_id}]",
    )
    relationship_task.add_done_callback(_log_task_outcome)
    tasks.append(relationship_task)

    # Phase 9 AC-9.1 (2026-04-15): inter-woman (internal) relationship
    # evaluator — one fire-and-forget task per character turn. The
    # evaluator iterates the focal character's ACTIVE inter-woman dyads
    # internally and fans out; Alicia-orbital dormant dyads are
    # filtered at the DB boundary (AC-9.11) so they never consume LLM
    # budget. Fire-and-forget contract identical to Phase 8.
    internal_task = asyncio.create_task(
        evaluate_and_update_internal(
            session_factory,
            character_id=character_id,
            response_text=full_response_text,
            llm_client=llm_client,
            settings=settings,
        ),
        name=f"post_turn_evaluate_and_update_internal[{character_id}]",
    )
    internal_task.add_done_callback(_log_task_outcome)
    tasks.append(internal_task)

    return tasks


async def await_post_turn_tasks(tasks: Iterable[asyncio.Task[object]]) -> None:
    """Test helper: await all post-turn tasks to completion.

    Production never calls this — fire-and-forget means no waiting.
    Tests use it to assert that side effects landed before tearing
    the fixture down.
    """
    await asyncio.gather(*tasks, return_exceptions=True)
