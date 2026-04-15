"""HTTP-specific exception hierarchy + FastAPI exception handlers.

Maps domain errors (CharacterNotFoundError, AliciaAwayContradictionError,
DreamsLLMError, AliciaAwayError) onto the canonical HTTP error envelope
defined in CLAUDE.md §10::

    {"error": {"code": "SCREAMING_SNAKE", "message": "...", "details": {}}}
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from starry_lyfe.canon.schemas.enums import CharacterNotFoundError
from starry_lyfe.context.assembler import AliciaAwayError
from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.scene.errors import (
    AliciaAwayContradictionError,
    NoValidSpeakerError,
)

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base class for HTTP-layer errors with structured envelope fields."""

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthError(ApiError):
    code = "UNAUTHORIZED"
    status_code = 401


class BadRequestError(ApiError):
    code = "BAD_REQUEST"
    status_code = 400


def _envelope(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_exception_handlers(app: FastAPI) -> None:
    """Wire exception handlers onto a FastAPI app."""

    @app.exception_handler(ApiError)
    async def _handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(CharacterNotFoundError)
    async def _handle_character_not_found(_: Request, exc: CharacterNotFoundError) -> JSONResponse:
        from starry_lyfe.canon.schemas.enums import CharacterID

        return JSONResponse(
            status_code=400,
            content=_envelope(
                "CHARACTER_NOT_FOUND",
                str(exc),
                {"valid_character_ids": CharacterID.all_strings()},
            ),
        )

    @app.exception_handler(AliciaAwayContradictionError)
    async def _handle_alicia_away_contradiction(
        _: Request, exc: AliciaAwayContradictionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_envelope("ALICIA_AWAY_CONTRADICTION", str(exc)),
        )

    @app.exception_handler(AliciaAwayError)
    async def _handle_alicia_away_assembly(
        _: Request, exc: AliciaAwayError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=_envelope("ALICIA_AWAY_ASSEMBLY", str(exc)),
        )

    @app.exception_handler(NoValidSpeakerError)
    async def _handle_no_valid_speaker(_: Request, exc: NoValidSpeakerError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_envelope("NO_VALID_SPEAKER", str(exc)),
        )

    @app.exception_handler(DreamsLLMError)
    async def _handle_dreams_llm(_: Request, exc: DreamsLLMError) -> JSONResponse:
        # Surface upstream LLM failures without leaking provider details.
        logger.warning("upstream_llm_error: %s", exc)
        return JSONResponse(
            status_code=502,
            content=_envelope("UPSTREAM_LLM_ERROR", str(exc)),
        )
