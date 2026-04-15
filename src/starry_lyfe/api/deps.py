"""FastAPI ``Depends()`` providers.

Resolves shared application state (settings, canon, DB session factory,
embedding service, BD-1 client) for endpoint handlers. The actual
singletons are constructed in ``app.create_app`` and stashed on
``app.state``; these helpers just route requests to them so endpoints
can be unit-tested in isolation.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from starry_lyfe.canon.loader import Canon
from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.dreams.llm import BDOne, StubBDOne

from .config import ApiSettings


def get_settings(request: Request) -> ApiSettings:
    settings: ApiSettings = request.app.state.settings
    return settings


def get_canon(request: Request) -> Canon:
    canon: Canon = request.app.state.canon
    return canon


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    return factory


async def get_db_session(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncIterator[AsyncSession]:
    """Yield a per-request DB session; commit on success, rollback on error."""
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_embedding_service(request: Request) -> EmbeddingService:
    service: EmbeddingService = request.app.state.embedding_service
    return service


def get_llm_client(request: Request) -> BDOne | StubBDOne:
    client: BDOne | StubBDOne = request.app.state.llm_client
    return client


SettingsDep = Annotated[ApiSettings, Depends(get_settings)]
CanonDep = Annotated[Canon, Depends(get_canon)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
EmbeddingDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
LLMDep = Annotated["BDOne | StubBDOne", Depends(get_llm_client)]
