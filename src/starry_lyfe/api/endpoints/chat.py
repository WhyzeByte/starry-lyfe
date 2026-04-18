"""``POST /v1/chat/completions`` — OpenAI-compatible SSE streaming chat.

Pipeline ownership: this handler resolves auth + routing + Msty
preprocessing, then hands a fully-built ``PipelineContext`` to
``run_chat_pipeline`` and wraps the resulting async generator in a
``StreamingResponse``.

Auth: ``X-API-Key`` header required. Missing or wrong key → 401 with
the structured error envelope. Other endpoints (health, models,
metrics) remain public per CLAUDE.md §14.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Header, Request
from fastapi.responses import StreamingResponse

from ..deps import CanonDep, EmbeddingDep, LLMDep, SessionDep, SettingsDep
from ..errors import AuthError
from ..orchestration.pipeline import (
    PipelineContext,
    PipelineResult,
    run_chat_pipeline,
)
from ..orchestration.post_turn import schedule_post_turn_tasks
from ..orchestration.session import upsert_session
from ..routing.character import resolve_character_id
from ..routing.msty import preprocess_msty_request
from ..schemas.chat import ChatCompletionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_session_id(provided: str | None, openai_user: str | None) -> uuid.UUID:
    """Pick a stable session UUID for this request.

    Priority: explicit X-Session-ID header > OpenAI ``user`` field
    (hashed into a UUID5) > random UUID4. The header is the canonical
    Msty session token surface; the OpenAI ``user`` field is a
    documented OpenAI hook for tracking end users.
    """
    if provided:
        try:
            return uuid.UUID(provided)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_URL, provided)
    if openai_user:
        return uuid.uuid5(uuid.NAMESPACE_URL, openai_user)
    return uuid.uuid4()


def _detect_client_type(user_agent: str | None, has_force_header: bool) -> str:
    """Coarse client classification for observability.

    Msty uses model field + assistant.name; any other client uses the
    X-SC-Force-Character header. Anything else (curl, custom scripts)
    reports as "other".
    """
    if has_force_header:
        return "owui"
    if user_agent and "msty" in user_agent.lower():
        return "msty"
    return "other"


def _extract_bearer_token(authorization: str | None) -> str | None:
    """Pull the token out of an ``Authorization: Bearer <token>`` header.

    Standard OpenAI-compatible clients (Msty Studio, the openai SDK,
    LangChain, etc.) send the API key as an Authorization Bearer token,
    not as ``X-API-Key``. Returns the token if the header is present
    and well-formed, else None.
    """
    if not authorization:
        return None
    parts = authorization.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _enforce_api_key(
    x_api_key: str | None,
    authorization: str | None,
    expected: str,
) -> None:
    """Raise ``AuthError`` unless the request carries the configured key.

    Accepts EITHER ``X-API-Key: <key>`` (the legacy header used by curl
    smoke tests and dev tools) OR ``Authorization: Bearer <key>`` (the
    standard OpenAI-compatible auth that Msty Studio and other clients
    send by default).

    A missing key is treated the same as a wrong key — both produce
    401 with the same envelope shape.
    """
    if not expected:
        # Deployment chose not to set an API key. Reject loud rather
        # than silently accept anything — matches the lesson-#2
        # "no silent fallback" pattern.
        raise AuthError("server has no STARRY_LYFE__API__API_KEY configured")
    bearer_token = _extract_bearer_token(authorization)
    if x_api_key == expected or bearer_token == expected:
        return
    raise AuthError(
        "missing or invalid API key — send X-API-Key: <key> or "
        "Authorization: Bearer <key>"
    )


@router.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    fast_request: Request,
    settings: SettingsDep,
    canon: CanonDep,
    session: SessionDep,
    embedding: EmbeddingDep,
    llm: LLMDep,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_sc_force_character: str | None = Header(default=None, alias="X-SC-Force-Character"),
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> StreamingResponse:
    """Handle a single chat completion request, returning an SSE stream."""
    _enforce_api_key(x_api_key, authorization, settings.api_key)

    msty = preprocess_msty_request(request.messages)
    routing = resolve_character_id(
        header=x_sc_force_character,
        model_field=request.model,
        user_message=msty.user_message,
        settings=settings,
    )

    # Upsert the chat_sessions row before streaming so observability has
    # a record of the request even if the LLM call fails downstream.
    session_id = _resolve_session_id(x_session_id, request.user)
    client_type = _detect_client_type(user_agent, x_sc_force_character is not None)
    try:
        await upsert_session(
            session,
            session_id=session_id,
            client_type=client_type,
            character_id=routing.character_id,
            scene_characters=msty.scene_characters or [routing.character_id],
        )
        await session.commit()
    except Exception as exc:  # noqa: BLE001 — session tracking is best-effort
        logger.warning("upsert_session_failed", exc_info=exc)
        await session.rollback()

    ctx = PipelineContext(
        request=request,
        routing=routing,
        msty=msty,
        session=session,
        canon=canon,
        llm_client=llm,
        embedding_service=embedding,
        settings=settings,
    )

    session_factory = fast_request.app.state.session_factory

    async def _stream_with_post_turn() -> AsyncIterator[bytes]:
        """Run the pipeline, then schedule post-turn tasks (E5).

        Tasks run as ``asyncio.create_task`` so the SSE response
        terminates BEFORE the extraction + relationship updates
        complete (AC-7.10). Failure isolation is in
        ``schedule_post_turn_tasks._log_task_outcome``.
        """
        async for chunk in run_chat_pipeline(ctx):
            yield chunk
        result_obj = ctx.session.info.get("pipeline_result")
        result: PipelineResult | None = result_obj if isinstance(result_obj, PipelineResult) else None
        # F2 2026-04-15: stash on app.state so tests can inspect the
        # resolved SceneState (alicia_home, present_characters, etc.)
        # without instrumenting the session object itself. Production
        # code never reads this field — see PipelineResult docstring.
        if result is not None:
            fast_request.app.state.last_pipeline_result = result
        if result is not None and result.full_response_text:
            schedule_post_turn_tasks(
                session_factory,
                character_id=result.character_id,
                user_message=msty.user_message,
                full_response_text=result.full_response_text,
                chat_session_id=session_id,
                llm_client=llm,
                settings=settings,
            )

    return StreamingResponse(
        _stream_with_post_turn(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Request-ID": ctx.request_id,
            "X-Character-ID": routing.character_id,
            "X-Routing-Source": routing.source,
            "X-Session-ID": str(session_id),
        },
    )
