"""Exponential decay logic for Transient Somatic State (Tier 7)."""

from __future__ import annotations


def apply_decay(current_value: float, half_life_hours: float, elapsed_hours: float) -> float:
    """Apply exponential decay: value * 0.5^(elapsed / half_life).

    Args:
        current_value: The current field value (0.0 to 1.0).
        half_life_hours: Hours for the value to halve.
        elapsed_hours: Hours since last decay application.

    Returns:
        The decayed value, clamped to [0.0, 1.0].
    """
    if half_life_hours <= 0 or elapsed_hours <= 0:
        return current_value
    decayed = current_value * (0.5 ** (elapsed_hours / half_life_hours))
    clamped: float = max(0.0, min(1.0, decayed))
    return clamped
