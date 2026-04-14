"""Per-tier memory retrieval API for context assembly."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import case, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .decay import apply_decay
from .embed import EmbeddingService
from .models.canon_facts import CanonFact
from .models.character_baseline import CharacterBaseline
from .models.dyad_state_internal import DyadStateInternal
from .models.dyad_state_whyze import DyadStateWhyze
from .models.episodic_memory import EpisodicMemory
from .models.open_loop import OpenLoop
from .models.transient_somatic import TransientSomaticState


class DecayConfigIncompleteError(ValueError):
    """Raised when a somatic state's decay_config is missing required keys.

    Per REMEDIATION_2026-04-13.md R-2.2: decay configuration must be
    complete at the data-record level. Silent .get(key, default)
    fallbacks would mask a misconfigured DB row and ship wrong decay
    behavior for that character without any audit trail.
    """


REQUIRED_DECAY_KEYS: set[str] = {"fatigue", "stress_residue", "injury_residue"}


@dataclass
class DecayedSomaticState:
    """Transient somatic state with decay applied at read time."""

    character_id: str
    fatigue: float
    stress_residue: float
    injury_residue: float
    active_protocols: list[str]
    protocol_metadata: dict[str, object]
    custom_fields: dict[str, object]


@dataclass
class MemoryBundle:
    """All retrieved memories for a character in a scene, grouped by tier."""

    canon_facts: list[CanonFact] = field(default_factory=list)
    character_baseline: CharacterBaseline | None = None
    dyad_states_whyze: list[DyadStateWhyze] = field(default_factory=list)
    dyad_states_internal: list[DyadStateInternal] = field(default_factory=list)
    episodic_memories: list[EpisodicMemory] = field(default_factory=list)
    open_loops: list[OpenLoop] = field(default_factory=list)
    somatic_state: DecayedSomaticState | None = None


async def _retrieve_canon_facts(session: AsyncSession, character_id: str) -> list[CanonFact]:
    """Tier 1: Load all canon facts for this character."""
    result = await session.execute(
        select(CanonFact).where(
            CanonFact.entity_type == "character",
            CanonFact.entity_key == character_id,
        )
    )
    return list(result.scalars().all())


async def _retrieve_baseline(session: AsyncSession, character_id: str) -> CharacterBaseline | None:
    """Tier 2: Load the character baseline."""
    result = await session.execute(
        select(CharacterBaseline).where(CharacterBaseline.character_id == character_id)
    )
    return result.scalars().first()


async def _retrieve_whyze_dyad(session: AsyncSession, character_id: str) -> list[DyadStateWhyze]:
    """Tier 3: Load the Whyze-to-character dyad."""
    result = await session.execute(
        select(DyadStateWhyze).where(DyadStateWhyze.character_id == character_id)
    )
    return list(result.scalars().all())


async def _retrieve_internal_dyads(
    session: AsyncSession, character_id: str
) -> list[DyadStateInternal]:
    """Tier 4: Load all active internal dyads where this character is a member."""
    result = await session.execute(
        select(DyadStateInternal).where(
            (DyadStateInternal.member_a == character_id) | (DyadStateInternal.member_b == character_id),
            DyadStateInternal.is_currently_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def _retrieve_episodic(
    session: AsyncSession,
    embedding_service: EmbeddingService,
    scene_context: str,
    character_id: str,
    top_k: int,
) -> list[EpisodicMemory]:
    """Tier 5: Semantic search for relevant episodic memories."""
    query_embedding = await embedding_service.embed(scene_context)
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    result = await session.execute(
        text(
            "SELECT * FROM starry_lyfe.episodic_memories "
            "WHERE character_id = :char_id "
            "ORDER BY embedding <=> CAST(:embedding AS vector) "
            "LIMIT :top_k"
        ),
        {"char_id": character_id, "embedding": embedding_str, "top_k": top_k},
    )
    rows = result.fetchall()

    if not rows:
        return []
    # Preserve similarity ranking: re-fetch ORM objects and sort by original order
    ranked_ids = [row.id for row in rows]
    orm_result = await session.execute(
        select(EpisodicMemory).where(EpisodicMemory.id.in_(ranked_ids))
    )
    orm_map = {m.id: m for m in orm_result.scalars().all()}
    return [orm_map[id_] for id_ in ranked_ids if id_ in orm_map]


async def _retrieve_open_loops(session: AsyncSession, character_id: str) -> list[OpenLoop]:
    """Tier 6: Load active open loops for this character."""
    now = datetime.now(UTC)
    urgency_rank = case(
        (OpenLoop.urgency == "high", 3),
        (OpenLoop.urgency == "medium", 2),
        (OpenLoop.urgency == "low", 1),
        else_=0,
    )
    result = await session.execute(
        select(OpenLoop)
        .where(
            OpenLoop.character_id == character_id,
            OpenLoop.status == "open",
            OpenLoop.expires_at > now,
        )
        .order_by(
            urgency_rank.desc(),
            OpenLoop.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def _retrieve_somatic(session: AsyncSession, character_id: str) -> DecayedSomaticState | None:
    """Tier 7: Load somatic state with read-time decay applied."""
    result = await session.execute(
        select(TransientSomaticState).where(TransientSomaticState.character_id == character_id)
    )
    state = result.scalars().first()
    if state is None:
        return None

    now = datetime.now(UTC)
    elapsed_hours = (now - state.last_decayed_at).total_seconds() / 3600.0
    config: dict[str, float] = state.decay_config

    # R-2.2: decay_config must be complete. Silent defaults would mask a
    # misconfigured DB row and ship wrong decay behavior for that character.
    missing = REQUIRED_DECAY_KEYS - set(config.keys())
    if missing:
        raise DecayConfigIncompleteError(
            f"decay_config for character_id={state.character_id!r} is missing "
            f"required keys: {sorted(missing)}. Expected all of: {sorted(REQUIRED_DECAY_KEYS)}"
        )

    return DecayedSomaticState(
        character_id=state.character_id,
        fatigue=apply_decay(state.fatigue, config["fatigue"], elapsed_hours),
        stress_residue=apply_decay(state.stress_residue, config["stress_residue"], elapsed_hours),
        injury_residue=apply_decay(state.injury_residue, config["injury_residue"], elapsed_hours),
        active_protocols=state.active_protocols,
        protocol_metadata=state.protocol_metadata,
        custom_fields=state.custom_fields,
    )


async def retrieve_memories(
    session: AsyncSession,
    embedding_service: EmbeddingService,
    scene_context: str,
    character_id: str,
    present_characters: list[str] | None = None,
    top_k_per_tier: int = 5,
) -> MemoryBundle:
    """Retrieve all relevant memories for a character in a scene context.

    This is the primary retrieval API that Phase 3 (Context Assembly) will consume.
    """
    bundle = MemoryBundle()
    bundle.canon_facts = await _retrieve_canon_facts(session, character_id)
    bundle.character_baseline = await _retrieve_baseline(session, character_id)
    bundle.dyad_states_whyze = await _retrieve_whyze_dyad(session, character_id)
    bundle.dyad_states_internal = await _retrieve_internal_dyads(session, character_id)
    bundle.episodic_memories = await _retrieve_episodic(
        session, embedding_service, scene_context, character_id, top_k_per_tier
    )
    bundle.open_loops = await _retrieve_open_loops(session, character_id)
    bundle.somatic_state = await _retrieve_somatic(session, character_id)
    return bundle
