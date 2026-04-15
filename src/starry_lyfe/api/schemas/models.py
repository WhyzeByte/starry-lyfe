"""Schema for ``GET /v1/models`` — OpenAI-compatible model list shape."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ModelEntry(BaseModel):
    """A single OpenAI-compatible model registry entry."""

    id: str
    object: Literal["model"] = "model"
    created: int  # epoch seconds; arbitrary fixed value is fine for non-OpenAI backends
    owned_by: Literal["starry-lyfe"] = "starry-lyfe"


class ModelListResponse(BaseModel):
    """OpenAI-compatible response envelope."""

    object: Literal["list"] = "list"
    data: list[ModelEntry] = Field(default_factory=list)
