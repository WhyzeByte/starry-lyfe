"""Unit tests for the /metrics endpoint + middleware."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings


class _SessionStub:
    def __init__(self) -> None:
        self.info: dict[str, Any] = {}

    async def execute(self, *args: object, **kwargs: object) -> Any:  # noqa: ANN401
        class _R:
            def scalar(self) -> int:
                return 1

        return _R()

    async def rollback(self) -> None: ...

    async def commit(self) -> None: ...

    async def close(self) -> None: ...


class _FactoryCtx:
    def __init__(self) -> None:
        self._s = _SessionStub()

    async def __aenter__(self) -> _SessionStub:
        return self._s

    async def __aexit__(self, *_: object) -> None: ...


class _Factory:
    def __call__(self) -> _FactoryCtx:
        return _FactoryCtx()


class _LLMStub:
    circuit_open = False

    def reset_circuit(self) -> None: ...


@pytest.fixture
def metrics_app() -> TestClient:
    app = create_app(
        ApiSettings(api_key="dev"),
        state_overrides={
            "session_factory": _Factory(),
            "llm_client": _LLMStub(),
            "engine": None,
            "canon": None,
            "embedding_service": None,
        },
    )
    return TestClient(app)


class TestMetricsEndpoint:
    def test_returns_prometheus_format(self, metrics_app: TestClient) -> None:
        with metrics_app:
            response = metrics_app.get("/metrics")
        assert response.status_code == 200
        # Prometheus exposition format is text/plain with version label.
        assert "text/plain" in response.headers["content-type"]
        # All 5 named series are registered (visible in HELP/TYPE comments).
        body = response.text
        for series in (
            "http_requests_total",
            "http_chat_completions_total",
            "http_sse_tokens_total",
            "http_request_duration_seconds",
            "http_chat_ttfb_seconds",
        ):
            assert f"# HELP {series}" in body, f"missing series: {series}"
            assert f"# TYPE {series}" in body

    def test_metrics_endpoint_no_auth_required(self, metrics_app: TestClient) -> None:
        # /metrics MUST be public so Prometheus can scrape without
        # sharing the API key.
        with metrics_app:
            response = metrics_app.get("/metrics")
        assert response.status_code == 200

    def test_request_counter_increments_on_other_routes(
        self, metrics_app: TestClient
    ) -> None:
        # Prometheus counters are process-global, so other tests in the
        # session may have already incremented these series. Snapshot
        # before → call → snapshot after and assert on the delta.
        import re

        def _read_counter(body: str, path: str) -> float:
            pattern = re.compile(
                r'http_requests_total\{method="GET",path="' + re.escape(path)
                + r'",status="200"\}\s+([\d.]+)'
            )
            for line in body.splitlines():
                match = pattern.search(line)
                if match:
                    return float(match.group(1))
            return 0.0

        with metrics_app:
            before = metrics_app.get("/metrics").text
            live_before = _read_counter(before, "/health/live")
            models_before = _read_counter(before, "/v1/models")

            metrics_app.get("/health/live")
            metrics_app.get("/health/live")
            metrics_app.get("/v1/models")
            after = metrics_app.get("/metrics").text

        live_after = _read_counter(after, "/health/live")
        models_after = _read_counter(after, "/v1/models")
        assert live_after - live_before == 2.0, (
            f"/health/live counter expected +2, got +{live_after - live_before}"
        )
        assert models_after - models_before == 1.0, (
            f"/v1/models counter expected +1, got +{models_after - models_before}"
        )

    def test_metrics_endpoint_does_not_self_count(
        self, metrics_app: TestClient
    ) -> None:
        with metrics_app:
            # Hit /metrics 3 times — counter for /metrics path should not appear.
            metrics_app.get("/metrics")
            metrics_app.get("/metrics")
            response = metrics_app.get("/metrics")
        body = response.text
        # No http_requests_total for /metrics path.
        for line in body.splitlines():
            assert not line.startswith('http_requests_total{method="GET",path="/metrics"'), (
                f"middleware should skip self-instrumentation, got: {line}"
            )
