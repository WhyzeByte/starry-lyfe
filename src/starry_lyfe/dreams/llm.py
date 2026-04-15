"""Protocol Droid BD-1: outbound HTTP client for LLM completions.

Wraps ``httpx.AsyncClient`` with mandatory timeouts, exponential-backoff
retries, and a per-client circuit breaker. Used by Dreams content
generators; Phase 7 HTTP service will reuse this wrapper for live
Claude calls via OpenRouter.

``StubBDOne`` is provided for tests — deterministic canned responses
keyed by a hash of ``(system_prompt, user_prompt)``.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from .errors import DreamsLLMError

# ---------------------------------------------------------------------------
# Tunable defaults. Units: seconds for timeout, count for max_retries.
# Module-level constants are preferred over magic numbers in bodies so that
# tests and ops tuning can override cleanly.
# ---------------------------------------------------------------------------

_DEFAULT_TIMEOUT_S: float = 60.0
_DEFAULT_MAX_RETRIES: int = 3
_DEFAULT_BACKOFF_BASE_S: float = 1.0
_DEFAULT_BACKOFF_MAX_S: float = 30.0
_DEFAULT_CIRCUIT_THRESHOLD: int = 5  # consecutive failures → open circuit
_DEFAULT_BASE_URL: str = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL: str = "anthropic/claude-sonnet-4-6"


@dataclass(frozen=True)
class BDOneSettings:
    """Configuration for the BD-1 HTTP client.

    Production callers resolve these from environment via
    ``STARRY_LYFE__BD1__*`` and ``STARRY_LYFE__DREAMS__LLM_MODEL``.
    """

    base_url: str = _DEFAULT_BASE_URL
    api_key: str = ""
    model: str = _DEFAULT_MODEL
    timeout_s: float = _DEFAULT_TIMEOUT_S
    max_retries: int = _DEFAULT_MAX_RETRIES
    circuit_threshold: int = _DEFAULT_CIRCUIT_THRESHOLD

    @classmethod
    def from_env(cls) -> BDOneSettings:
        """Load from environment variables."""
        return cls(
            base_url=os.getenv("STARRY_LYFE__BD1__BASE_URL", _DEFAULT_BASE_URL),
            api_key=os.getenv("STARRY_LYFE__BD1__API_KEY", ""),
            model=os.getenv("STARRY_LYFE__DREAMS__LLM_MODEL", _DEFAULT_MODEL),
            timeout_s=float(os.getenv("STARRY_LYFE__BD1__TIMEOUT", _DEFAULT_TIMEOUT_S)),
            max_retries=int(os.getenv("STARRY_LYFE__BD1__MAX_RETRIES", _DEFAULT_MAX_RETRIES)),
            circuit_threshold=int(
                os.getenv("STARRY_LYFE__BD1__CIRCUIT_THRESHOLD", _DEFAULT_CIRCUIT_THRESHOLD)
            ),
        )


@dataclass(frozen=True)
class BDOneCompletion:
    """Result of a single BD-1 completion call."""

    text: str
    input_tokens: int
    output_tokens: int
    model: str


# ---------------------------------------------------------------------------
# Retry / circuit-breaker primitive
# ---------------------------------------------------------------------------


def _backoff_seconds(attempt: int, base: float, max_s: float) -> float:
    """Exponential backoff with jitter, clamped at ``max_s``."""
    expo: float = min(max_s, base * float(2 ** max(0, attempt - 1)))
    jitter: float = random.uniform(0.0, expo * 0.25)
    return float(expo + jitter)


# ---------------------------------------------------------------------------
# BDOne client
# ---------------------------------------------------------------------------


class BDOne:
    """Outbound HTTP client for LLM completions.

    Example:
        >>> settings = BDOneSettings.from_env()
        >>> client = BDOne(settings)
        >>> completion = await client.complete(system_prompt="...", user_prompt="...")
    """

    def __init__(self, settings: BDOneSettings) -> None:
        self._settings = settings
        self._consecutive_failures = 0
        self._circuit_open = False

    @property
    def settings(self) -> BDOneSettings:
        return self._settings

    @property
    def circuit_open(self) -> bool:
        """True when the circuit breaker has tripped; further calls short-circuit."""
        return self._circuit_open

    def reset_circuit(self) -> None:
        """Manually close the circuit breaker. Used by tests + operator recovery."""
        self._circuit_open = False
        self._consecutive_failures = 0

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> BDOneCompletion:
        """Call the LLM; retry on transient failures; open circuit on N consecutive failures.

        Raises:
            DreamsLLMError: if the circuit is open, or retries exhausted.
        """
        if self._circuit_open:
            raise DreamsLLMError(
                f"BD-1 circuit breaker is open "
                f"(after {self._consecutive_failures} consecutive failures). "
                "Call reset_circuit() after fixing the upstream issue."
            )

        payload = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
        }

        last_exc: Exception | None = None
        for attempt in range(1, self._settings.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._settings.timeout_s) as client:
                    response = await client.post(
                        f"{self._settings.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()
                completion = _parse_completion(data, self._settings.model)
                self._consecutive_failures = 0
                return completion
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                last_exc = exc
                if attempt < self._settings.max_retries:
                    import asyncio
                    sleep_s = _backoff_seconds(
                        attempt, _DEFAULT_BACKOFF_BASE_S, _DEFAULT_BACKOFF_MAX_S
                    )
                    await asyncio.sleep(sleep_s)

        # Retries exhausted.
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._settings.circuit_threshold:
            self._circuit_open = True
        raise DreamsLLMError(
            f"BD-1 completion failed after {self._settings.max_retries} attempts: "
            f"{type(last_exc).__name__}: {last_exc}"
        ) from last_exc

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream LLM text deltas as they arrive (Phase 7).

        Yields raw text fragments from the upstream OpenAI-compatible
        ``/v1/chat/completions`` SSE stream. Each yielded string is the
        ``choices[0].delta.content`` of one upstream chunk; the caller
        is responsible for re-wrapping them in the local SSE envelope.

        Shares retry/circuit-breaker state with ``complete()``: opens
        the circuit on N consecutive failures, refuses to call when
        already open. Note: streaming starts before the response is
        complete, so the first failure surfaces at connect/HTTP time;
        once a chunk has been yielded, subsequent network failures
        bubble up as ``DreamsLLMError`` mid-stream rather than
        retrying (we cannot replay the partial output the caller has
        already consumed).

        Raises:
            DreamsLLMError: circuit open, connect retries exhausted, or
                upstream returned a non-2xx initial response.
        """
        if self._circuit_open:
            raise DreamsLLMError(
                f"BD-1 circuit breaker is open "
                f"(after {self._consecutive_failures} consecutive failures). "
                "Call reset_circuit() after fixing the upstream issue."
            )

        payload = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        # Pre-stream connect with retries. Once the upstream stream is
        # open and yielding bytes, errors bubble up without retry.
        last_exc: Exception | None = None
        client: httpx.AsyncClient | None = None
        response_cm: Any = None
        response: httpx.Response | None = None
        for attempt in range(1, self._settings.max_retries + 1):
            try:
                client = httpx.AsyncClient(timeout=self._settings.timeout_s)
                response_cm = client.stream(
                    "POST",
                    f"{self._settings.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response = await response_cm.__aenter__()
                response.raise_for_status()
                last_exc = None
                break
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                last_exc = exc
                if response_cm is not None:
                    with contextlib.suppress(Exception):
                        await response_cm.__aexit__(None, None, None)
                if client is not None:
                    await client.aclose()
                response_cm = None
                client = None
                response = None
                if attempt < self._settings.max_retries:
                    import asyncio
                    sleep_s = _backoff_seconds(
                        attempt, _DEFAULT_BACKOFF_BASE_S, _DEFAULT_BACKOFF_MAX_S
                    )
                    await asyncio.sleep(sleep_s)

        if last_exc is not None or response is None or client is None or response_cm is None:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._settings.circuit_threshold:
                self._circuit_open = True
            raise DreamsLLMError(
                f"BD-1 stream connect failed after {self._settings.max_retries} attempts: "
                f"{type(last_exc).__name__}: {last_exc}"
            ) from last_exc

        try:
            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                delta = (
                    chunk.get("choices") or [{}]
                )[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield str(content)
            self._consecutive_failures = 0
        finally:
            with contextlib.suppress(Exception):
                await response_cm.__aexit__(None, None, None)
            await client.aclose()


def _parse_completion(data: dict[str, Any], model: str) -> BDOneCompletion:
    """Extract text + token counts from an OpenRouter/Anthropic-compatible response."""
    choices = data.get("choices") or []
    if not choices:
        msg = f"BD-1 response has no choices: keys={list(data.keys())}"
        raise ValueError(msg)
    message = choices[0].get("message") or {}
    text = message.get("content") or ""
    usage = data.get("usage") or {}
    return BDOneCompletion(
        text=str(text),
        input_tokens=int(usage.get("prompt_tokens", 0)),
        output_tokens=int(usage.get("completion_tokens", 0)),
        model=str(data.get("model", model)),
    )


# ---------------------------------------------------------------------------
# StubBDOne — deterministic stub for tests
# ---------------------------------------------------------------------------


_StubResponder = Callable[[str, str], str]


@dataclass
class StubBDOne:
    """Deterministic BD-1 stub.

    Responses are keyed by a hash of ``(system_prompt, user_prompt)`` so
    identical calls always return identical text. A ``responder`` callable
    can override the default hash-to-text mapping for tests that need
    specific outputs.

    Tracks ``call_count`` so tests can assert how many LLM calls a
    generator made.
    """

    responder: _StubResponder | None = None
    default_text: str = "stub-response"
    fail_next_n: int = 0
    call_count: int = 0
    stream_call_count: int = 0
    fail_history: list[str] = field(default_factory=list)
    model: str = "stub/claude-sonnet-4-6"
    # When > 0, ``stream_complete`` yields the canned text in N
    # equally-sized chunks. Defaults to 4 so tests can assert that
    # multiple chunks arrive.
    stream_chunk_count: int = 4

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> BDOneCompletion:
        self.call_count += 1

        if self.fail_next_n > 0:
            self.fail_next_n -= 1
            self.fail_history.append(system_prompt[:40])
            raise DreamsLLMError("StubBDOne configured to fail this call")

        if self.responder is not None:
            text = self.responder(system_prompt, user_prompt)
        else:
            key = hashlib.sha256((system_prompt + "|" + user_prompt).encode("utf-8")).hexdigest()[:8]
            text = f"{self.default_text} [{key}]"

        return BDOneCompletion(
            text=text,
            input_tokens=len(system_prompt.split()) + len(user_prompt.split()),
            output_tokens=len(text.split()),
            model=self.model,
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream the canned response in ``stream_chunk_count`` pieces.

        Mirrors the BDOne contract for tests + dry-run sample
        generation. ``fail_next_n`` is honored — a configured failure
        raises before any chunks are yielded.
        """
        self.stream_call_count += 1

        if self.fail_next_n > 0:
            self.fail_next_n -= 1
            self.fail_history.append(system_prompt[:40])
            raise DreamsLLMError("StubBDOne configured to fail this call")

        if self.responder is not None:
            text = self.responder(system_prompt, user_prompt)
        else:
            key = hashlib.sha256(
                (system_prompt + "|" + user_prompt).encode("utf-8")
            ).hexdigest()[:8]
            text = f"{self.default_text} [{key}]"

        if self.stream_chunk_count <= 0 or not text:
            yield text
            return

        # Split into roughly equal chunks. Edge case: text shorter than
        # chunk count → yield each character individually.
        chunk_count = min(self.stream_chunk_count, len(text))
        chunk_size = max(1, len(text) // chunk_count)
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]

    @property
    def circuit_open(self) -> bool:
        return False

    def reset_circuit(self) -> None:
        """No-op for the stub."""


# Attach ``complete`` awaitable type hint for clarity when assigning to BDOne union.
_complete_signature: Callable[[BDOne | StubBDOne, str, str], Awaitable[BDOneCompletion]]
