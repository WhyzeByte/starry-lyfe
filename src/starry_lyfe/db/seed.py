"""Seed canon YAML data into the PostgreSQL memory tiers.

Seeds Tiers 1 (Canon Facts), 2 (Character Baselines), 3 (Dyad State Whyze),
4 (Dyad State Internal), and 7 (Transient Somatic State) from the Phase 1 canon YAML.
Tiers 5 (Episodic) and 6 (Open Loops) grow from conversation data and Dreams.

Runnable as: python -m starry_lyfe.db.seed
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.canon.loader import Canon, load_all_canon

from .config import get_db_settings
from .engine import build_engine, build_session_factory, init_db
from .models.canon_facts import CanonFact
from .models.character_baseline import CharacterBaseline
from .models.dyad_state_internal import DyadStateInternal
from .models.dyad_state_whyze import DyadStateWhyze
from .models.transient_somatic import DEFAULT_DECAY_CONFIG, TransientSomaticState


def _flatten_canon_facts(canon: Canon) -> list[dict[str, str]]:
    """Flatten canon entities into (entity_type, entity_key, fact_key, fact_value) rows."""
    rows: list[dict[str, str]] = []
    version = canon.characters.version

    # Characters
    for char_id, char in canon.characters.characters.items():
        for field_name, field_value in char.model_dump().items():
            if isinstance(field_value, (dict, list)):
                import json

                val = json.dumps(field_value, ensure_ascii=False)
            else:
                val = str(field_value) if field_value is not None else ""
            rows.append({
                "entity_type": "character",
                "entity_key": char_id.value,
                "fact_key": field_name,
                "fact_value": val,
                "canon_version": version,
            })

    # Operator
    for op_key, op in canon.characters.operator.items():
        for field_name, field_value in op.model_dump().items():
            if isinstance(field_value, (dict, list)):
                import json

                val = json.dumps(field_value, ensure_ascii=False)
            else:
                val = str(field_value) if field_value is not None else ""
            rows.append({
                "entity_type": "operator",
                "entity_key": op_key,
                "fact_key": field_name,
                "fact_value": val,
                "canon_version": version,
            })

    return rows


async def _seed_canon_facts(session: AsyncSession, canon: Canon) -> int:
    """Seed Tier 1: Canon Facts. Returns row count."""
    rows = _flatten_canon_facts(canon)
    for row in rows:
        stmt = pg_insert(CanonFact).values(
            id=uuid.uuid4(),
            entity_type=row["entity_type"],
            entity_key=row["entity_key"],
            fact_key=row["fact_key"],
            fact_value=row["fact_value"],
            canon_version=row["canon_version"],
        ).on_conflict_do_update(
            constraint="uq_canon_fact_entity_fact",
            set_={"fact_value": row["fact_value"], "canon_version": row["canon_version"]},
        )
        await session.execute(stmt)
    return len(rows)


async def _seed_character_baselines(session: AsyncSession, canon: Canon) -> int:
    """Seed Tier 2: Character Baselines. Returns row count."""
    count = 0
    for char_id, char in canon.characters.characters.items():
        pair = canon.pairs.pairs[char.pair_name]
        voice = canon.voice_parameters.voice_parameters[char_id]

        stmt = pg_insert(CharacterBaseline).values(
            id=uuid.uuid4(),
            character_id=char_id.value,
            full_name=char.full_name,
            epithet=char.epithet,
            mbti=char.mbti.value,
            cognitive_stack=[f.value for f in char.cognitive_function_stack],
            dominant_function=char.dominant_function.value,
            voice_params=voice.model_dump(mode="json"),
            pair_name=char.pair_name.value,
            pair_classification=pair.classification,
            pair_mechanism=pair.mechanism,
            pair_core_metaphor=pair.core_metaphor,
            heritage=char.heritage,
            profession=char.profession,
            is_resident=char.is_resident,
            operational_travel=char.operational_travel,
            canon_version=canon.characters.version,
        ).on_conflict_do_update(
            index_elements=["character_id"],
            set_={
                "full_name": char.full_name,
                "epithet": char.epithet,
                "mbti": char.mbti.value,
                "cognitive_stack": [f.value for f in char.cognitive_function_stack],
                "dominant_function": char.dominant_function.value,
                "voice_params": voice.model_dump(mode="json"),
                "pair_name": char.pair_name.value,
                "pair_classification": pair.classification,
                "pair_mechanism": pair.mechanism,
                "pair_core_metaphor": pair.core_metaphor,
                "heritage": char.heritage,
                "profession": char.profession,
                "is_resident": char.is_resident,
                "operational_travel": char.operational_travel,
                "canon_version": canon.characters.version,
            },
        )
        await session.execute(stmt)
        count += 1
    return count


async def _seed_dyad_state_whyze(session: AsyncSession, canon: Canon) -> int:
    """Seed Tier 3: Dyad State (Whyze). Returns row count."""
    count = 0
    for dyad_key, dyad in canon.dyads.dyads.items():
        if dyad.type.value != "whyze_pair":
            continue
        character_id = [m for m in dyad.members if m != "whyze"][0]
        stmt = pg_insert(DyadStateWhyze).values(
            id=uuid.uuid4(),
            dyad_key=dyad_key,
            character_id=character_id,
            pair_name=dyad.pair.value if dyad.pair else "",
            trust=dyad.dimensions.trust.baseline,
            intimacy=dyad.dimensions.intimacy.baseline,
            conflict=dyad.dimensions.conflict.baseline,
            unresolved_tension=dyad.dimensions.unresolved_tension.baseline,
            repair_history=dyad.dimensions.repair_history.baseline,
        ).on_conflict_do_nothing(index_elements=["dyad_key"])
        await session.execute(stmt)
        count += 1
    return count


async def _seed_dyad_state_internal(session: AsyncSession, canon: Canon) -> int:
    """Seed Tier 4: Dyad State (Internal). Returns row count."""
    count = 0
    for dyad_key, dyad in canon.dyads.dyads.items():
        if dyad.type.value != "inter_woman":
            continue
        is_active = dyad.is_currently_active if dyad.is_currently_active is not None else True
        stmt = pg_insert(DyadStateInternal).values(
            id=uuid.uuid4(),
            dyad_key=dyad_key,
            member_a=dyad.members[0],
            member_b=dyad.members[1],
            subtype=dyad.subtype.value if dyad.subtype else "resident_continuous",
            interlock=dyad.interlock,
            trust=dyad.dimensions.trust.baseline,
            intimacy=dyad.dimensions.intimacy.baseline,
            conflict=dyad.dimensions.conflict.baseline,
            unresolved_tension=dyad.dimensions.unresolved_tension.baseline,
            repair_history=dyad.dimensions.repair_history.baseline,
            is_currently_active=is_active,
        ).on_conflict_do_nothing(index_elements=["dyad_key"])
        await session.execute(stmt)
        count += 1
    return count


async def _seed_transient_somatic(session: AsyncSession, canon: Canon) -> int:
    """Seed Tier 7: Transient Somatic State. Returns row count."""
    count = 0
    for char_id in canon.characters.characters:
        stmt = pg_insert(TransientSomaticState).values(
            id=uuid.uuid4(),
            character_id=char_id.value,
            fatigue=0.0,
            stress_residue=0.0,
            injury_residue=0.0,
            active_protocols=[],
            protocol_metadata={},
            custom_fields={},
            decay_config=DEFAULT_DECAY_CONFIG,
        ).on_conflict_do_nothing(index_elements=["character_id"])
        await session.execute(stmt)
        count += 1
    return count


async def seed_database() -> None:
    """Run the full seed pipeline."""
    canon = load_all_canon()

    settings = get_db_settings()
    engine = build_engine(settings)
    await init_db(engine)

    session_factory = build_session_factory(engine)
    async with session_factory() as session, session.begin():
        facts = await _seed_canon_facts(session, canon)
        baselines = await _seed_character_baselines(session, canon)
        whyze_dyads = await _seed_dyad_state_whyze(session, canon)
        internal_dyads = await _seed_dyad_state_internal(session, canon)
        somatic = await _seed_transient_somatic(session, canon)

    # Verify counts
    async with session_factory() as session:
        baseline_count = (await session.execute(select(CharacterBaseline))).scalars().all()
        internal_count = (await session.execute(select(DyadStateInternal))).scalars().all()

        assert len(baseline_count) == 4, f"Expected 4 baselines, got {len(baseline_count)}"
        assert len(internal_count) == 6, f"Expected 6 internal dyads, got {len(internal_count)}"

    await engine.dispose()

    print("Seed complete:")
    print(f"  Tier 1 (Canon Facts): {facts} rows")
    print(f"  Tier 2 (Character Baselines): {baselines} rows")
    print(f"  Tier 3 (Dyad State Whyze): {whyze_dyads} rows")
    print(f"  Tier 4 (Dyad State Internal): {internal_dyads} rows")
    print(f"  Tier 7 (Transient Somatic): {somatic} rows")


def main() -> None:
    """CLI entry point."""
    try:
        asyncio.run(seed_database())
    except Exception as e:
        print(f"Seed failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
