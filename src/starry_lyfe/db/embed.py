"""Embedding service protocol and implementations for pgvector episodic memory."""

from __future__ import annotations

from typing import Protocol

import httpx

from .config import EmbeddingSettings, get_embedding_settings


class EmbeddingService(Protocol):
    """Protocol for embedding text into vectors. Implementations are swappable."""

    async def embed(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class LMStudioEmbeddingService:
    """Embedding via LM Studio's OpenAI-compatible API (POST /v1/embeddings).

    LM Studio exposes an OpenAI-compatible server on a configurable port
    (default 1234). The embeddings endpoint accepts ``{"model": str,
    "input": str | list[str]}`` and returns ``{"data": [{"embedding":
    [...], "index": int}, ...]}``. Order is preserved across batch input.
    """

    def __init__(self, settings: EmbeddingSettings | None = None) -> None:
        if settings is None:
            settings = get_embedding_settings()
        self._model = settings.model
        self._base_url = settings.base_url.rstrip("/")
        self._dimension = settings.dimension

    async def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
            vector: list[float] = data["data"][0]["embedding"]
            return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single request, preserving input order."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
            data = response.json()
            rows = sorted(data["data"], key=lambda row: row["index"])
            return [row["embedding"] for row in rows]
