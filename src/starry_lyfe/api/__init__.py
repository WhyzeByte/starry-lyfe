"""Phase 7 HTTP service.

The Starry-Lyfe HTTP service exposes the v7.1 character backend as an
OpenAI-compatible chat API on port 8001. Five endpoints:

* ``GET /health/live`` — liveness probe (always 200)
* ``GET /health/ready`` — readiness (DB + BD-1 reachable)
* ``GET /v1/models`` — 5 model entries (legacy + per-character)
* ``POST /v1/chat/completions`` — SSE streaming chat (auth required)
* ``GET /metrics`` — Prometheus exposition

The 12-step request flow from IMPLEMENTATION_PLAN_v7.1 §10 is implemented
in ``orchestration/pipeline.py``. Per CLAUDE.md §14, character routing
priority is: ``X-SC-Force-Character`` header > inline ``/<char>`` override
in user message > ``model`` field matching canonical name > settings
default.
"""

from __future__ import annotations

from .app import create_app
from .config import ApiSettings, get_api_settings

__all__ = [
    "ApiSettings",
    "create_app",
    "get_api_settings",
]
