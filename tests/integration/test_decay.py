"""Gate 2 verification: transient somatic state decays per configured half-lives."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.db.models.transient_somatic import DEFAULT_DECAY_CONFIG, TransientSomaticState
from starry_lyfe.db.retrieval import DecayConfigIncompleteError, _retrieve_somatic


async def test_somatic_decay_after_one_fatigue_half_life(db_session: AsyncSession) -> None:
    """Gate 2: Fatigue decays to ~0.5 after one half-life (8 hours)."""
    eight_hours_ago = datetime.now(UTC) - timedelta(hours=8)
    state = TransientSomaticState(
        id=uuid.uuid4(),
        character_id="adelia_decay",
        fatigue=1.0,
        stress_residue=0.0,
        injury_residue=0.0,
        active_protocols=[],
        protocol_metadata={},
        custom_fields={},
        decay_config=DEFAULT_DECAY_CONFIG,
        last_decayed_at=eight_hours_ago,
    )
    db_session.add(state)
    await db_session.flush()

    decayed = await _retrieve_somatic(db_session, "adelia_decay")
    assert decayed is not None
    assert decayed.fatigue == pytest.approx(0.5, abs=0.05)


async def test_stress_residue_decays_over_24_hours(db_session: AsyncSession) -> None:
    """Gate 2: Stress residue decays to ~0.5 after 24 hours."""
    twenty_four_hours_ago = datetime.now(UTC) - timedelta(hours=24)
    state = TransientSomaticState(
        id=uuid.uuid4(),
        character_id="bina_decay",
        fatigue=0.0,
        stress_residue=1.0,
        injury_residue=0.0,
        active_protocols=[],
        protocol_metadata={},
        custom_fields={},
        decay_config=DEFAULT_DECAY_CONFIG,
        last_decayed_at=twenty_four_hours_ago,
    )
    db_session.add(state)
    await db_session.flush()

    decayed = await _retrieve_somatic(db_session, "bina_decay")
    assert decayed is not None
    assert decayed.stress_residue == pytest.approx(0.5, abs=0.05)


async def test_missing_decay_key_raises_on_retrieval(db_session: AsyncSession) -> None:
    """R-2.2: missing decay_config keys must fail on the live retrieval path."""
    character_id = "reina_decay_miss"
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    state = TransientSomaticState(
        id=uuid.uuid4(),
        character_id=character_id,
        fatigue=0.3,
        stress_residue=0.2,
        injury_residue=0.1,
        active_protocols=[],
        protocol_metadata={},
        custom_fields={},
        decay_config={
            "fatigue": 8.0,
            "injury_residue": 72.0,
        },
        last_decayed_at=one_hour_ago,
    )
    db_session.add(state)
    await db_session.flush()

    with pytest.raises(DecayConfigIncompleteError, match="stress_residue"):
        await _retrieve_somatic(db_session, character_id)
