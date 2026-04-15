"""FastAPI application factory.

``create_app`` returns a fully-wired ``FastAPI`` instance. Used by the
production uvicorn boot path (``api.main``) and by tests via
``fastapi.testclient.TestClient``. All shared singletons (canon, DB
engine + session factory, embedding service, BD-1 client) are
constructed in the lifespan startup hook and stashed on
``app.state``; ``api.deps`` providers route per-request access to them.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from starry_lyfe.canon.loader import load_all_canon
from starry_lyfe.db.embed import EmbeddingService, OllamaEmbeddingService
from starry_lyfe.db.engine import build_engine, build_session_factory, close_db, init_db
from starry_lyfe.dreams.llm import BDOne, BDOneSettings, StubBDOne

from .config import ApiSettings, get_api_settings
from .endpoints import chat_router, health_router, models_router
from .errors import register_exception_handlers

logger = logging.getLogger(__name__)


def _build_default_state(settings: ApiSettings) -> dict[str, Any]:
    """Build the default production state for ``app.state``.

    Tests override individual entries (e.g. swap BDOne for StubBDOne) by
    passing ``state_overrides`` to ``create_app``.
    """
    canon = load_all_canon()
    engine = build_engine()
    session_factory = build_session_factory(engine)
    embedding_service: EmbeddingService = OllamaEmbeddingService()
    llm_client: BDOne | StubBDOne = BDOne(BDOneSettings.from_env())
    return {
        "settings": settings,
        "canon": canon,
        "engine": engine,
        "session_factory": session_factory,
        "embedding_service": embedding_service,
        "llm_client": llm_client,
    }


def create_app(
    settings: ApiSettings | None = None,
    *,
    state_overrides: dict[str, Any] | None = None,
) -> FastAPI:
    """Construct a FastAPI app instance with all routes + state wired.

    Args:
        settings: Optional settings override (defaults to env-loaded).
        state_overrides: Optional partial state mapping merged over the
            default-built state. Tests use this to swap in stubs.
    """
    settings = settings or get_api_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Build default state, then apply test overrides.
        state = _build_default_state(settings)
        if state_overrides:
            state.update(state_overrides)
        for key, value in state.items():
            setattr(app.state, key, value)
        # Verify DB connectivity + ensure pgvector extension.
        engine = app.state.engine
        try:
            await init_db(engine)
        except Exception as exc:  # noqa: BLE001 — startup-time failure must surface
            logger.warning("init_db_failed_at_startup: %s", exc)
        try:
            yield
        finally:
            engine = getattr(app.state, "engine", None)
            if engine is not None:
                await close_db(engine)

    app = FastAPI(
        title="starry-lyfe",
        version="7.1",
        description="Phase 7 HTTP service — OpenAI-compatible chat API.",
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(chat_router)

    return app
