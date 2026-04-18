# Starry-Lyfe API service Dockerfile
# Multi-stage build: deps compiled in builder, slim runtime layer.
#
# Built and run by docker/docker-compose.yml. Source code lives at
# /app inside the container; the compose file bind-mounts the host
# repo over /app at runtime so character YAML edits propagate
# without a rebuild. Dependency changes (requirements.txt) require
# `docker compose build --no-cache api`.

# ---------- builder ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build deps for any wheels that need compilation (asyncpg etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

# ---------- runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Runtime libs only (no build toolchain).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Python deps from the builder stage.
COPY --from=builder /install /usr/local

# Source. The compose file bind-mounts the host repo over this at
# runtime so on-disk edits flow in immediately. The COPY is a fallback
# for `docker run` without a mount (e.g. CI smoke).
COPY pyproject.toml ./
COPY src/ ./src/
COPY Characters/ ./Characters/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Non-root user (Foundry §8 standard).
RUN useradd --create-home --uid 1000 starry \
 && chown -R starry:starry /app
USER starry

EXPOSE 8001

# uvicorn factory mode lets the lifespan hook build per-process state.
CMD ["python", "-m", "starry_lyfe.api.main"]
