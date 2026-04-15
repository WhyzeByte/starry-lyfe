"""CLI entry point: ``python -m starry_lyfe.api`` starts uvicorn on port 8001.

Production deployments invoke this module directly. Tests import
``create_app`` and use FastAPI's TestClient instead.
"""

from __future__ import annotations

import logging

import uvicorn

from .app import create_app
from .config import get_api_settings


def main() -> None:
    """Boot the HTTP service with settings loaded from environment."""
    settings = get_api_settings()
    logging.basicConfig(level=logging.INFO)
    app = create_app(settings)
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
