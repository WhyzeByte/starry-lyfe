"""F3 closure: /health/ready performs live BD-1 HEAD probe.

Pre-F3 the endpoint only inspected ``llm_client.circuit_open`` and could
false-positive 200 for an unreachable provider whose circuit had not yet
tripped. These tests cover the new probe branch: reachable → 200,
unreachable → 503 with structured reason.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from starry_lyfe.api import create_app
from starry_lyfe.api.config import ApiSettings
from starry_lyfe.dreams.errors import DreamsLLMError


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


class _ReachableLLMStub:
    circuit_open = False

    async def ping(self, *, timeout_s: float = 1.5) -> None:
        return None

    def reset_circuit(self) -> None: ...


class _UnreachableLLMStub:
    circuit_open = False

    async def ping(self, *, timeout_s: float = 1.5) -> None:
        raise DreamsLLMError("simulated connection refused")

    def reset_circuit(self) -> None: ...


class _OpenCircuitLLMStub:
    circuit_open = True

    async def ping(self, *, timeout_s: float = 1.5) -> None:
        # Should NOT be called when circuit is open — fast-path covers it.
        raise AssertionError("ping must not be called while circuit_open")

    def reset_circuit(self) -> None: ...


def _build_app(llm: object, probe_enabled: bool = True) -> TestClient:
    return TestClient(
        create_app(
            ApiSettings(api_key="dev", health_bd1_probe=probe_enabled),
            state_overrides={
                "session_factory": _Factory(),
                "llm_client": llm,
                "engine": None,
                "canon": None,
                "embedding_service": None,
            },
        )
    )


class TestReadinessProbe:
    def test_ready_200_when_bd1_reachable(self) -> None:
        with _build_app(_ReachableLLMStub()) as client:
            response = client.get("/health/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"]["llm"]["ok"] is True

    def test_ready_503_when_bd1_unreachable(self) -> None:
        """F3 core contract: probe failure surfaces as 503."""
        with _build_app(_UnreachableLLMStub()) as client:
            response = client.get("/health/ready")
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "not_ready"
        assert body["checks"]["llm"]["ok"] is False
        assert "simulated connection refused" in body["checks"]["llm"]["reason"]

    def test_ready_503_when_circuit_open_without_probe(self) -> None:
        """Fast-path: open circuit short-circuits without calling ping()."""
        with _build_app(_OpenCircuitLLMStub()) as client:
            response = client.get("/health/ready")
        assert response.status_code == 503
        body = response.json()
        assert body["checks"]["llm"]["ok"] is False
        assert "circuit breaker" in body["checks"]["llm"]["reason"].lower()

    def test_probe_toggle_disables_network_call(self) -> None:
        """When health_bd1_probe=False, unreachable LLM still returns 200."""
        with _build_app(_UnreachableLLMStub(), probe_enabled=False) as client:
            response = client.get("/health/ready")
        # Probe disabled → skipped → llm.ok reports True without network.
        assert response.status_code == 200
        assert response.json()["checks"]["llm"]["ok"] is True
