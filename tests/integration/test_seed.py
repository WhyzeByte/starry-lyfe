"""Gate 2 verification: seed pipeline produces correct row counts and data."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.db.models.character_baseline import CharacterBaseline
from starry_lyfe.db.models.dyad_state_internal import DyadStateInternal
from starry_lyfe.db.models.dyad_state_whyze import DyadStateWhyze
from starry_lyfe.db.models.transient_somatic import TransientSomaticState


async def test_seed_produces_exactly_4_character_baselines(seeded_session: AsyncSession) -> None:
    """Gate 2: Seeding produces exactly 4 character baseline rows."""
    result = await seeded_session.execute(select(func.count()).select_from(CharacterBaseline))
    assert result.scalar() == 4


async def test_seed_character_ids_correct(seeded_session: AsyncSession) -> None:
    """Gate 2: Seeded character IDs are exactly {adelia, bina, reina, alicia}."""
    result = await seeded_session.execute(select(CharacterBaseline.character_id))
    ids = {row[0] for row in result}
    assert ids == {"adelia", "bina", "reina", "alicia"}


async def test_dyad_state_internal_has_6_rows(seeded_session: AsyncSession) -> None:
    """Gate 2: Dyad State Internal has exactly 6 rows."""
    result = await seeded_session.execute(select(func.count()).select_from(DyadStateInternal))
    assert result.scalar() == 6


async def test_internal_dyad_subtypes(seeded_session: AsyncSession) -> None:
    """Gate 2: 3 resident_continuous + 3 alicia_orbital."""
    result = await seeded_session.execute(select(DyadStateInternal))
    dyads = result.scalars().all()
    resident = [d for d in dyads if d.subtype == "resident_continuous"]
    orbital = [d for d in dyads if d.subtype == "alicia_orbital"]
    assert len(resident) == 3
    assert len(orbital) == 3


async def test_alicia_orbital_default_inactive(seeded_session: AsyncSession) -> None:
    """Gate 2: Alicia-orbital dyads default to is_currently_active=False."""
    result = await seeded_session.execute(
        select(DyadStateInternal).where(DyadStateInternal.subtype == "alicia_orbital")
    )
    for dyad in result.scalars():
        assert dyad.is_currently_active is False


async def test_alicia_orbital_persists_across_residence_changes(seeded_session: AsyncSession) -> None:
    """Gate 2: Alicia-orbital dimension values persist through active/inactive cycles."""
    result = await seeded_session.execute(
        select(DyadStateInternal).where(DyadStateInternal.dyad_key == "adelia_alicia")
    )
    dyad = result.scalars().first()
    assert dyad is not None

    original_trust = dyad.trust

    # Simulate return: activate and update
    dyad.is_currently_active = True
    dyad.trust = min(1.0, original_trust + 0.02)
    await seeded_session.flush()

    # Simulate departure: deactivate
    dyad.is_currently_active = False
    await seeded_session.flush()

    # Simulate return: reactivate
    dyad.is_currently_active = True
    await seeded_session.flush()

    # Dimensions must persist, not reset
    await seeded_session.refresh(dyad)
    assert dyad.trust == pytest.approx(original_trust + 0.02)


async def test_whyze_dyads_seeded_correctly(seeded_session: AsyncSession) -> None:
    """Gate 2: Dyad State Whyze has exactly 4 rows."""
    result = await seeded_session.execute(select(func.count()).select_from(DyadStateWhyze))
    assert result.scalar() == 4


async def test_transient_somatic_seeded(seeded_session: AsyncSession) -> None:
    """Gate 2: Transient Somatic State has exactly 4 rows with zero initial values."""
    result = await seeded_session.execute(select(TransientSomaticState))
    states = result.scalars().all()
    assert len(states) == 4
    for state in states:
        assert state.fatigue == 0.0
        assert state.stress_residue == 0.0
        assert state.injury_residue == 0.0


async def test_no_canonical_drift_in_seeded_baselines(seeded_session: AsyncSession) -> None:
    """Gate 2: No v7.0 residue tokens in seeded character data."""
    from tests.unit.test_residue_grep import V70_RESIDUE_TOKENS

    result = await seeded_session.execute(select(CharacterBaseline))
    for baseline in result.scalars():
        text_fields = [
            baseline.full_name,
            baseline.epithet,
            baseline.heritage,
            baseline.profession,
            baseline.pair_name,
        ]
        for field_val in text_fields:
            for token in V70_RESIDUE_TOKENS:
                assert token not in field_val, (
                    f"v7.0 residue '{token}' found in {baseline.character_id}.{field_val}"
                )
