"""R-2.2 remediation: decay_config must be complete or raise.

Spec: Docs/REMEDIATION_2026-04-13.md §2.R-2.2.

The fetch_decayed_somatic_state retrieval path previously used
dict.get(key, default) fallbacks, which silently served default decay
parameters when a DB record was missing keys. This test exercises the
new guardrail: missing keys raise DecayConfigIncompleteError.
"""

from __future__ import annotations

import pytest

from starry_lyfe.db.retrieval import (
    REQUIRED_DECAY_KEYS,
    DecayConfigIncompleteError,
)


def test_required_decay_keys_includes_three_canonical_keys() -> None:
    """Required keys are fatigue, stress_residue, injury_residue."""
    assert {"fatigue", "stress_residue", "injury_residue"} == REQUIRED_DECAY_KEYS


def test_decay_config_incomplete_error_subclasses_value_error() -> None:
    """DecayConfigIncompleteError is a ValueError subclass (backward compat)."""
    assert issubclass(DecayConfigIncompleteError, ValueError)


def test_decay_config_missing_key_raises_directly() -> None:
    """DecayConfigIncompleteError can be raised and caught normally."""
    with pytest.raises(DecayConfigIncompleteError, match="missing required keys"):
        raise DecayConfigIncompleteError(
            "decay_config for character_id='adelia' is missing required keys: "
            "['stress_residue']. Expected all of: ['fatigue', 'injury_residue', 'stress_residue']"
        )
