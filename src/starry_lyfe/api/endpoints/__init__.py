"""HTTP endpoint routers for the Phase 7 service."""

from __future__ import annotations

from .health import router as health_router
from .models import router as models_router

__all__ = [
    "health_router",
    "models_router",
]
