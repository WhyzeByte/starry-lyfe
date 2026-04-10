"""Gate 2 verification: retrieval ordering and bundle assembly behave correctly."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from starry_lyfe.db.embed import EmbeddingService
from starry_lyfe.db.models.episodic_memory import EMBEDDING_DIMENSION, EpisodicMemory
from starry_lyfe.db.models.open_loop import OpenLoop
from starry_lyfe.db.retrieval import (
    _retrieve_episodic,
    _retrieve_open_loops,
    retrieve_memories,
)


def _vector(first: float, second: float = 0.0) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    vector[0] = first
    vector[1] = second
    return vector


class StubEmbeddingService(EmbeddingService):
    async def embed(self, text: str) -> list[float]:
        return _vector(1.0, 0.0)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(text) for text in texts]


async def test_episodic_retrieval_preserves_similarity_order(db_session: AsyncSession) -> None:
    """Gate 2: episodic results stay in cosine-similarity order after ORM re-fetch."""
    now = datetime.now(UTC)
    memories = [
        EpisodicMemory(
            id=uuid.uuid4(),
            session_id=None,
            character_id="adelia",
            participant_ids={"ids": ["adelia", "whyze"]},
            event_summary="exact match",
            emotional_temperature=0.4,
            memory_type="scene",
            importance_score=0.8,
            embedding=_vector(1.0, 0.0),
            metadata_={"rank": 1},
            created_at=now,
            decayed_at=None,
        ),
        EpisodicMemory(
            id=uuid.uuid4(),
            session_id=None,
            character_id="adelia",
            participant_ids={"ids": ["adelia", "whyze"]},
            event_summary="close match",
            emotional_temperature=0.4,
            memory_type="scene",
            importance_score=0.7,
            embedding=_vector(0.8, 0.2),
            metadata_={"rank": 2},
            created_at=now,
            decayed_at=None,
        ),
        EpisodicMemory(
            id=uuid.uuid4(),
            session_id=None,
            character_id="adelia",
            participant_ids={"ids": ["adelia", "whyze"]},
            event_summary="far match",
            emotional_temperature=0.4,
            memory_type="scene",
            importance_score=0.6,
            embedding=_vector(0.0, 1.0),
            metadata_={"rank": 3},
            created_at=now,
            decayed_at=None,
        ),
    ]
    db_session.add_all(memories)
    await db_session.flush()

    retrieved = await _retrieve_episodic(
        db_session,
        StubEmbeddingService(),
        scene_context="adelia remembers a direct match",
        character_id="adelia",
        top_k=3,
    )

    assert [memory.event_summary for memory in retrieved] == [
        "exact match",
        "close match",
        "far match",
    ]


async def test_open_loops_rank_high_medium_low_then_newest(db_session: AsyncSession) -> None:
    """Gate 2: open loops rank by urgency first, then recency inside the same urgency."""
    now = datetime.now(UTC)
    loops = [
        OpenLoop(
            id=uuid.uuid4(),
            character_id="adelia",
            loop_summary="older medium",
            loop_type="memory",
            urgency="medium",
            best_next_speaker="adelia",
            suggested_scene=None,
            source_session_id=None,
            status="open",
            resolved_by=None,
            ttl_hours=48,
            created_at=now - timedelta(hours=3),
            expires_at=now + timedelta(days=1),
            resolved_at=None,
        ),
        OpenLoop(
            id=uuid.uuid4(),
            character_id="adelia",
            loop_summary="high priority",
            loop_type="memory",
            urgency="high",
            best_next_speaker="adelia",
            suggested_scene=None,
            source_session_id=None,
            status="open",
            resolved_by=None,
            ttl_hours=48,
            created_at=now - timedelta(hours=2),
            expires_at=now + timedelta(days=1),
            resolved_at=None,
        ),
        OpenLoop(
            id=uuid.uuid4(),
            character_id="adelia",
            loop_summary="newer medium",
            loop_type="memory",
            urgency="medium",
            best_next_speaker="adelia",
            suggested_scene=None,
            source_session_id=None,
            status="open",
            resolved_by=None,
            ttl_hours=48,
            created_at=now - timedelta(hours=1),
            expires_at=now + timedelta(days=1),
            resolved_at=None,
        ),
        OpenLoop(
            id=uuid.uuid4(),
            character_id="adelia",
            loop_summary="low priority",
            loop_type="memory",
            urgency="low",
            best_next_speaker="adelia",
            suggested_scene=None,
            source_session_id=None,
            status="open",
            resolved_by=None,
            ttl_hours=48,
            created_at=now,
            expires_at=now + timedelta(days=1),
            resolved_at=None,
        ),
    ]
    db_session.add_all(loops)
    await db_session.flush()

    retrieved = await _retrieve_open_loops(db_session, "adelia")

    assert [loop.loop_summary for loop in retrieved] == [
        "high priority",
        "newer medium",
        "older medium",
        "low priority",
    ]


async def test_retrieve_memories_returns_all_seeded_tiers(seeded_session: AsyncSession) -> None:
    """Gate 2: top-level retrieval returns seeded memory tiers plus live episodic/open-loop data."""
    now = datetime.now(UTC)
    episodic = EpisodicMemory(
        id=uuid.uuid4(),
        session_id=None,
        character_id="adelia",
        participant_ids={"ids": ["adelia", "whyze"]},
        event_summary="bundle memory",
        emotional_temperature=0.5,
        memory_type="scene",
        importance_score=0.9,
        embedding=_vector(1.0, 0.0),
        metadata_={"source": "test"},
        created_at=now,
        decayed_at=None,
    )
    open_loop = OpenLoop(
        id=uuid.uuid4(),
        character_id="adelia",
        loop_summary="bundle loop",
        loop_type="memory",
        urgency="high",
        best_next_speaker="adelia",
        suggested_scene=None,
        source_session_id=None,
        status="open",
        resolved_by=None,
        ttl_hours=48,
        created_at=now,
        expires_at=now + timedelta(days=1),
        resolved_at=None,
    )
    seeded_session.add_all([episodic, open_loop])
    await seeded_session.flush()

    bundle = await retrieve_memories(
        seeded_session,
        StubEmbeddingService(),
        scene_context="adelia needs her bundle",
        character_id="adelia",
    )

    assert bundle.canon_facts
    assert bundle.character_baseline is not None
    assert bundle.character_baseline.character_id == "adelia"
    assert len(bundle.dyad_states_whyze) == 1
    assert bundle.dyad_states_internal
    assert all(dyad.is_currently_active for dyad in bundle.dyad_states_internal)
    assert bundle.episodic_memories[0].event_summary == "bundle memory"
    assert bundle.open_loops[0].loop_summary == "bundle loop"
    assert bundle.somatic_state is not None
    assert bundle.somatic_state.character_id == "adelia"
