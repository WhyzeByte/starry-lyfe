"""``GET /metrics`` — Prometheus exposition + per-request middleware.

Five named series:
- ``http_requests_total`` (counter, labeled by method + path + status)
- ``http_chat_completions_total`` (counter, labeled by character_id +
  routing source + outcome)
- ``http_sse_tokens_total`` (counter, labeled by character_id) — tracks
  cumulative streamed deltas
- ``http_request_duration_seconds`` (histogram, labeled by method +
  path) — total request latency
- ``http_chat_ttfb_seconds`` (histogram, labeled by character_id) —
  time to first SSE byte (currently approximated as request duration
  since the chat endpoint already buffers no upstream latency in
  test mode; production is fine to compare against this baseline)

Public endpoint, no auth. Per CLAUDE.md §14 metrics scrape works
without an API key so Prometheus operators don't need to share secrets.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

router = APIRouter()

# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests processed by the Phase 7 service.",
    labelnames=("method", "path", "status"),
)
http_chat_completions_total = Counter(
    "http_chat_completions_total",
    "Total number of /v1/chat/completions requests, partitioned by routing.",
    labelnames=("character_id", "routing_source", "outcome"),
)
http_sse_tokens_total = Counter(
    "http_sse_tokens_total",
    # Semantic note: "tokens" is a misnomer retained for Prometheus series
    # stability — this counter tracks per-delta LLM emissions, not LLM
    # tokens. R2-F2 2026-04-15: one inc per upstream LLM stream delta in
    # BOTH single-speaker and Crew paths. Attribution markers (``**Name:**``)
    # and separators (``\n\n``) emitted around Crew speakers are SSE frame
    # content, not LLM output — they do NOT increment this counter.
    (
        "Cumulative LLM stream deltas per labeled character "
        "(speaker in Crew mode, focal character otherwise; "
        "one inc per upstream delta)."
    ),
    labelnames=("character_id",),
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Total request duration in seconds.",
    labelnames=("method", "path"),
    # Buckets sized for the chat path (sub-second through 30s upstream calls).
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)
http_chat_ttfb_seconds = Histogram(
    "http_chat_ttfb_seconds",
    "Time to first SSE byte for /v1/chat/completions.",
    labelnames=("character_id",),
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus exposition. Public; no auth."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class MetricsMiddleware(BaseHTTPMiddleware):
    """Records ``http_requests_total`` + ``http_request_duration_seconds``."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Skip self-instrumentation for the /metrics endpoint to avoid
        # spamming the counters with scrape traffic.
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:
            # Record + re-raise so FastAPI's exception handlers can still
            # produce the canonical envelope.
            http_requests_total.labels(
                method=request.method, path=request.url.path, status="500"
            ).inc()
            http_request_duration_seconds.labels(
                method=request.method, path=request.url.path
            ).observe(time.monotonic() - start)
            raise

        duration = time.monotonic() - start
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status=str(response.status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method, path=request.url.path
        ).observe(duration)

        # Chat-specific labeling: character_id + routing source come back
        # via response headers set by the chat endpoint. TTFB is treated
        # as request duration here (StreamingResponse closes after the
        # last byte; refining this would need an instrumented stream
        # wrapper).
        if request.url.path == "/v1/chat/completions":
            character = response.headers.get("X-Character-ID", "unknown")
            source = response.headers.get("X-Routing-Source", "unknown")
            outcome = "ok" if response.status_code == 200 else "error"
            http_chat_completions_total.labels(
                character_id=character, routing_source=source, outcome=outcome
            ).inc()
            http_chat_ttfb_seconds.labels(character_id=character).observe(duration)

        return response
