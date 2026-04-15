"""2-1B protocol: ``/health/live`` (liveness) + ``/health/ready`` (deps).

* ``/health/live`` — always 200; verifies the process is up. Used by
  container orchestrators / curl smoke tests.
* ``/health/ready`` — verifies that R5 (DB) and BD-1 (LLM) are reachable.
  Returns 503 with a structured reason in the body when either is down.

F3 closure (2026-04-15): the LLM branch now issues a live HEAD probe via
``BDOne.ping()`` when ``settings.health_bd1_probe`` is True. The circuit-
breaker short-circuit is preserved as a fast-path for known-bad state.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from starry_lyfe.dreams.errors import DreamsLLMError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health/live")
async def live() -> dict[str, str]:
    """Liveness probe — returns 200 as long as the event loop is alive."""
    return {"status": "live"}


@router.get("/health/ready")
async def ready(request: Request) -> JSONResponse:
    """Readiness probe — checks that all critical deps are reachable."""
    state = request.app.state
    checks: dict[str, dict[str, Any]] = {}
    overall_ok = True

    # R5: ping DB with SELECT 1.
    factory = getattr(state, "session_factory", None)
    if factory is None:
        checks["db"] = {"ok": False, "reason": "session_factory missing"}
        overall_ok = False
    else:
        try:
            async with factory() as session:
                await session.execute(text("SELECT 1"))
            checks["db"] = {"ok": True}
        except Exception as exc:  # noqa: BLE001 — bubble reason up to caller
            checks["db"] = {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}
            overall_ok = False

    # BD-1: circuit-breaker fast-path + live HEAD probe. Fast-path keeps
    # known-bad state cheap; probe resolves the false-positive gap the
    # original circuit-only check left (F3 closure 2026-04-15). The HEAD
    # call costs zero tokens and uses a 1.5s timeout so scrapes stay cheap.
    llm = getattr(state, "llm_client", None)
    settings = getattr(state, "settings", None)
    probe_enabled = getattr(settings, "health_bd1_probe", True) if settings else True
    if llm is None:
        checks["llm"] = {"ok": False, "reason": "llm_client missing"}
        overall_ok = False
    elif getattr(llm, "circuit_open", False):
        checks["llm"] = {"ok": False, "reason": "BD-1 circuit breaker open"}
        overall_ok = False
    elif probe_enabled and hasattr(llm, "ping"):
        try:
            await llm.ping()
            checks["llm"] = {"ok": True}
        except DreamsLLMError as exc:
            checks["llm"] = {"ok": False, "reason": f"BD-1 probe failed: {exc}"}
            overall_ok = False
    else:
        checks["llm"] = {"ok": True}

    body = {"status": "ready" if overall_ok else "not_ready", "checks": checks}
    return JSONResponse(status_code=200 if overall_ok else 503, content=body)
