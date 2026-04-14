"""Custom exceptions for the Phase 6 Dreams Engine."""

from __future__ import annotations


class DreamsRunError(RuntimeError):
    """Raised when a full Dreams pass cannot complete.

    Per-generator failures are caught + logged (warning) and do NOT raise
    this error; it only fires when orchestration itself cannot proceed
    (e.g., session_factory unreachable, canon load fails).
    """


class DreamsLLMError(RuntimeError):
    """Raised by BDOne when retries are exhausted or the circuit breaker opens.

    Downstream generators catch this and degrade gracefully (their
    ``GenerationOutput`` carries a warning string instead of content).
    """


class DreamsScheduleError(RuntimeError):
    """Raised by the daemon when the apscheduler configuration is invalid.

    (e.g., cron expression does not parse; misfire_grace_time is negative.)
    """
