"""OpenAI-compatible chat completion schemas.

Only the subset of the OpenAI shape that Msty actually sends
is modeled. Stream responses use ``ChatCompletionChunk`` per OpenAI's SSE
contract: each ``data:`` line carries one chunk; the stream terminates
with ``data: [DONE]``.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """A single message in a chat completion request.

    Msty Crew Conversations replay prior persona responses with
    ``role="assistant"`` and a ``name`` field set to the persona id.
    """

    role: Literal["system", "user", "assistant"]
    content: str
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible request body for ``POST /v1/chat/completions``.

    ``model`` participates in character routing per CLAUDE.md §14 — see
    ``api.routing.character.resolve_character_id``.
    """

    model_config = ConfigDict(extra="allow")

    model: str
    messages: list[ChatMessage]
    stream: bool = True
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    # OpenAI permits arbitrary extra fields; Msty sometimes attaches
    # ``user``, ``stop``, etc. Capture them so observability can log them
    # without requiring an explicit schema entry.
    user: str | None = None
    stop: list[str] | str | None = None


class ChatCompletionDelta(BaseModel):
    """Per-chunk delta payload — content is appended to the prior chunks."""

    role: Literal["assistant"] | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    """Single choice slot in a streaming chunk (always index 0 for us)."""

    index: int = 0
    delta: ChatCompletionDelta
    finish_reason: Literal["stop", "length", "content_filter"] | None = None


class ChatCompletionChunk(BaseModel):
    """A single SSE chunk in the OpenAI streaming format.

    Stream protocol: each chunk is wrapped in ``data: <json>\\n\\n``;
    the stream terminates with ``data: [DONE]\\n\\n``.
    """

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice] = Field(default_factory=list)

    def to_sse_data(self) -> str:
        """Render this chunk as an SSE ``data:`` line (no trailing newlines)."""
        return self.model_dump_json(exclude_none=True)


class ChatCompletionErrorEnvelope(BaseModel):
    """Terminal error chunk emitted when validation or the LLM fails mid-stream."""

    error: dict[str, Any]
