"""Unit tests for the exponential decay pure function."""

from __future__ import annotations

import math

from starry_lyfe.db.decay import apply_decay


def test_zero_elapsed_returns_current() -> None:
    """No time elapsed means no decay."""
    assert apply_decay(1.0, 8.0, 0.0) == 1.0


def test_one_half_life_halves_value() -> None:
    """After one half-life, value should be approximately 0.5."""
    result = apply_decay(1.0, 8.0, 8.0)
    assert math.isclose(result, 0.5, rel_tol=1e-9)


def test_two_half_lives_quarters_value() -> None:
    """After two half-lives, value should be approximately 0.25."""
    result = apply_decay(1.0, 8.0, 16.0)
    assert math.isclose(result, 0.25, rel_tol=1e-9)


def test_negative_elapsed_returns_current() -> None:
    """Negative elapsed time is a no-op."""
    assert apply_decay(0.8, 8.0, -5.0) == 0.8


def test_zero_half_life_returns_current() -> None:
    """Zero half-life is a no-op (prevents division by zero)."""
    assert apply_decay(0.8, 0.0, 10.0) == 0.8


def test_negative_half_life_returns_current() -> None:
    """Negative half-life is a no-op."""
    assert apply_decay(0.8, -1.0, 10.0) == 0.8


def test_partial_half_life() -> None:
    """After 4 hours with 8-hour half-life, value should be ~0.707."""
    result = apply_decay(1.0, 8.0, 4.0)
    expected = 0.5 ** 0.5  # sqrt(0.5)
    assert math.isclose(result, expected, rel_tol=1e-9)


def test_decay_from_nonunit_starting_value() -> None:
    """Decay works correctly from values other than 1.0."""
    result = apply_decay(0.6, 24.0, 24.0)
    assert math.isclose(result, 0.3, rel_tol=1e-9)


def test_result_clamped_to_zero() -> None:
    """Very large elapsed time decays to effectively zero, clamped at 0.0."""
    result = apply_decay(1.0, 1.0, 1000.0)
    assert result >= 0.0
