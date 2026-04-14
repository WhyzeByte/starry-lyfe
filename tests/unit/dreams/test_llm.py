"""Unit tests for BDOne HTTP client wrapper (Phase 6 Subsystem C)."""

from __future__ import annotations

import pytest

from starry_lyfe.dreams import BDOne, BDOneSettings, DreamsLLMError, StubBDOne


class TestBDOneSettings:
    def test_defaults(self) -> None:
        settings = BDOneSettings()
        assert settings.base_url.startswith("https://")
        assert settings.timeout_s == 60.0
        assert settings.max_retries == 3

    def test_from_env_reads_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("STARRY_LYFE__BD1__API_KEY", "test-key")
        monkeypatch.setenv("STARRY_LYFE__BD1__TIMEOUT", "10.0")
        monkeypatch.setenv("STARRY_LYFE__BD1__MAX_RETRIES", "1")
        settings = BDOneSettings.from_env()
        assert settings.api_key == "test-key"
        assert settings.timeout_s == 10.0
        assert settings.max_retries == 1


class TestBDOneCircuitBreaker:
    def test_fresh_client_circuit_closed(self) -> None:
        client = BDOne(BDOneSettings(api_key="test"))
        assert not client.circuit_open

    def test_reset_circuit_after_trip(self) -> None:
        client = BDOne(BDOneSettings(api_key="test"))
        # Simulate trip by setting private state directly for this unit test.
        client._circuit_open = True  # type: ignore[attr-defined]
        client._consecutive_failures = 5  # type: ignore[attr-defined]
        assert client.circuit_open
        client.reset_circuit()
        assert not client.circuit_open
        assert client._consecutive_failures == 0  # type: ignore[attr-defined]

    async def test_complete_raises_when_circuit_open(self) -> None:
        client = BDOne(BDOneSettings(api_key="test"))
        client._circuit_open = True  # type: ignore[attr-defined]
        with pytest.raises(DreamsLLMError, match="circuit breaker is open"):
            await client.complete(system_prompt="s", user_prompt="u")


class TestStubBDOne:
    async def test_deterministic_for_identical_inputs(self) -> None:
        stub = StubBDOne()
        a = await stub.complete(system_prompt="hello", user_prompt="world")
        b = await stub.complete(system_prompt="hello", user_prompt="world")
        assert a.text == b.text

    async def test_different_prompts_yield_different_text(self) -> None:
        stub = StubBDOne()
        a = await stub.complete(system_prompt="hello", user_prompt="world")
        b = await stub.complete(system_prompt="different", user_prompt="world")
        assert a.text != b.text

    async def test_call_count_tracks_invocations(self) -> None:
        stub = StubBDOne()
        assert stub.call_count == 0
        await stub.complete(system_prompt="a", user_prompt="b")
        await stub.complete(system_prompt="c", user_prompt="d")
        assert stub.call_count == 2

    async def test_responder_override_produces_custom_text(self) -> None:
        def canned(system: str, user: str) -> str:
            return f"CANNED[{system}|{user}]"

        stub = StubBDOne(responder=canned)
        result = await stub.complete(system_prompt="sys", user_prompt="usr")
        assert result.text == "CANNED[sys|usr]"

    async def test_fail_next_n_raises_dreams_llm_error(self) -> None:
        stub = StubBDOne(fail_next_n=2)
        with pytest.raises(DreamsLLMError):
            await stub.complete(system_prompt="s", user_prompt="u")
        with pytest.raises(DreamsLLMError):
            await stub.complete(system_prompt="s", user_prompt="u")
        # Third call succeeds.
        result = await stub.complete(system_prompt="s", user_prompt="u")
        assert "stub-response" in result.text

    async def test_returns_token_counts(self) -> None:
        stub = StubBDOne()
        result = await stub.complete(
            system_prompt="one two three", user_prompt="four five"
        )
        assert result.input_tokens == 5  # 3 + 2
        assert result.output_tokens > 0

    async def test_circuit_open_always_false_on_stub(self) -> None:
        stub = StubBDOne()
        assert not stub.circuit_open
        stub.reset_circuit()  # no-op
        assert not stub.circuit_open


class TestBackoff:
    def test_backoff_increases_with_attempt(self) -> None:
        from starry_lyfe.dreams.llm import _backoff_seconds

        # Monotonic increase (modulo jitter). Run multiple samples to account
        # for jitter upper-bound randomness.
        a_vals = [_backoff_seconds(1, 1.0, 30.0) for _ in range(20)]
        b_vals = [_backoff_seconds(3, 1.0, 30.0) for _ in range(20)]
        assert max(a_vals) < max(b_vals)

    def test_backoff_clamped_at_max(self) -> None:
        from starry_lyfe.dreams.llm import _backoff_seconds

        # Large attempt should be clamped; jitter adds up to 25% over max_s.
        result = _backoff_seconds(attempt=100, base=1.0, max_s=5.0)
        assert result <= 5.0 * 1.25 + 0.01
