"""HTTP endpoint routers for the Phase 7 service."""

from __future__ import annotations

from .chat import router as chat_router
from .health import router as health_router
from .metrics import MetricsMiddleware
from .metrics import router as metrics_router
from .models import router as models_router

__all__ = [
    "MetricsMiddleware",
    "chat_router",
    "health_router",
    "metrics_router",
    "models_router",
]
