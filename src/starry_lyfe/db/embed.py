"""Embedding service protocol and implementations for pgvector episodic memory."""

from __future__ import annotations

from typing import Protocol

import httpx

from .config import EmbeddingSettings, get_embedding_settings


class EmbeddingService(Protocol):
    """Protocol for embedding text into vectors. Implementations are swappable."""

    async def embed(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class OllamaEmbeddingService:
    """Embedding via Ollama API (lightweight, no PyTorch dependency)."""

    def __init__(self, settings: EmbeddingSettings | None = None) -> None:
        if settings is None:
            settings = get_embedding_settings()
        self._model = settings.model
        self._base_url = settings.base_url
        self._dimension = settings.dimension

    async def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings: list[list[float]] = data["embeddings"]
            return embeddings[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single request."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
            data = response.json()
            result: list[list[float]] = data["embeddings"]
            return result
