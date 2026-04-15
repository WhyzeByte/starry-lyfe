"""Unit tests for ``BDOne.stream_complete`` + ``StubBDOne.stream_complete``.

The tests exercise the StubBDOne contract directly (no httpx) plus
the BDOne circuit-breaker behavior (which is fully covered without
calling out — circuit_open is set in-process).
"""

from __future__ import annotations

import pytest

from starry_lyfe.dreams.errors import DreamsLLMError
from starry_lyfe.dreams.llm import BDOne, BDOneSettings, StubBDOne


class TestStubBDOneStreaming:
    async def test_stream_yields_deltas(self) -> None:
        stub = StubBDOne(default_text="hello world from the stub")
        chunks: list[str] = []
        async for chunk in stub.stream_complete("system", "user"):
            chunks.append(chunk)
        # Default chunk count is 4; expect at least 2 chunks for any
        # text longer than the chunk-size threshold.
        assert len(chunks) >= 2
        # Each chunk is non-empty.
        assert all(c for c in chunks)
        # Total reassembled text starts with the canned prefix.
        assert "".join(chunks).startswith("hello world from the stub")

    async def test_stream_full_text_matches_complete(self) -> None:
        # Streaming the same prompt should produce the same total text
        # as a non-streaming complete() call.
        stub = StubBDOne(default_text="response body")
        completion = await stub.complete("sys", "user")
        full = ""
        async for chunk in stub.stream_complete("sys", "user"):
            full += chunk
        assert full == completion.text

    async def test_stream_call_count_increments(self) -> None:
        stub = StubBDOne()
        async for _ in stub.stream_complete("a", "b"):
            pass
        async for _ in stub.stream_complete("a", "b"):
            pass
        assert stub.stream_call_count == 2

    async def test_stream_failure_raises_before_yield(self) -> None:
        stub = StubBDOne(fail_next_n=1)
        with pytest.raises(DreamsLLMError):
            async for _ in stub.stream_complete("sys", "user"):
                pytest.fail("should not have yielded any chunk")

    async def test_stream_responder_override(self) -> None:
        stub = StubBDOne(responder=lambda s, u: "fixed response text")
        full = ""
        async for chunk in stub.stream_complete("a", "b"):
            full += chunk
        assert full == "fixed response text"

    async def test_chunk_count_one_yields_whole_text(self) -> None:
        stub = StubBDOne(default_text="hi", stream_chunk_count=1)
        chunks: list[str] = []
        async for chunk in stub.stream_complete("a", "b"):
            chunks.append(chunk)
        assert len(chunks) == 1


class TestBDOneCircuitBreakerOnStream:
    async def test_open_circuit_short_circuits_before_request(self) -> None:
        client = BDOne(BDOneSettings(api_key="x"))
        # Force the circuit open.
        client._circuit_open = True  # type: ignore[reportPrivateUsage]
        with pytest.raises(DreamsLLMError, match="circuit breaker is open"):
            async for _ in client.stream_complete("sys", "user"):
                pytest.fail("should not have started streaming")

    async def test_reset_circuit_clears_state(self) -> None:
        client = BDOne(BDOneSettings(api_key="x"))
        client._circuit_open = True  # type: ignore[reportPrivateUsage]
        client._consecutive_failures = 5  # type: ignore[reportPrivateUsage]
        client.reset_circuit()
        assert client.circuit_open is False
