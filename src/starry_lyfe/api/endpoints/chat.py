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

from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse

from ..deps import CanonDep, EmbeddingDep, LLMDep, SessionDep, SettingsDep
from ..errors import AuthError
from ..orchestration.pipeline import PipelineContext, run_chat_pipeline
from ..routing.character import resolve_character_id
from ..routing.msty import preprocess_msty_request
from ..schemas.chat import ChatCompletionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


def _enforce_api_key(provided: str | None, expected: str) -> None:
    """Raise ``AuthError`` unless the request carries the configured key.

    A missing key is treated the same as a wrong key — both produce
    401 with the same envelope shape. We deliberately do not return
    404 for a missing key (some setups suggest hiding existence
    behind 404, but our endpoints are public-discoverable via
    /v1/models so the masquerade is pointless).
    """
    if not expected:
        # Deployment chose not to set an API key. Reject loud rather
        # than silently accept anything — matches the lesson-#2
        # "no silent fallback" pattern.
        raise AuthError("server has no STARRY_LYFE__API__API_KEY configured")
    if provided is None or provided != expected:
        raise AuthError("missing or invalid X-API-Key header")


@router.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    settings: SettingsDep,
    canon: CanonDep,
    session: SessionDep,
    embedding: EmbeddingDep,
    llm: LLMDep,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_sc_force_character: str | None = Header(default=None, alias="X-SC-Force-Character"),
) -> StreamingResponse:
    """Handle a single chat completion request, returning an SSE stream."""
    _enforce_api_key(x_api_key, settings.api_key)

    msty = preprocess_msty_request(request.messages)
    routing = resolve_character_id(
        header=x_sc_force_character,
        model_field=request.model,
        user_message=msty.user_message,
        settings=settings,
    )

    ctx = PipelineContext(
        request=request,
        routing=routing,
        msty=msty,
        session=session,
        canon=canon,
        llm_client=llm,
        embedding_service=embedding,
    )

    return StreamingResponse(
        run_chat_pipeline(ctx),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Request-ID": ctx.request_id,
            "X-Character-ID": routing.character_id,
            "X-Routing-Source": routing.source,
        },
    )
