"""Re-embed all rows in ``episodic_memories`` via the configured EmbeddingService.

Use this after swapping embedding providers (e.g. Ollama -> LM Studio).
Existing embeddings from a different model occupy the same Vector(768)
shape but live in an incomparable vector space; cosine similarity
between old and new rows is meaningless. This script rewrites every
``embedding`` column in place using ``event_summary`` as the source
text, batched to keep LM Studio requests reasonable.

Run:
    python scripts/reembed_episodic_memories.py
    python scripts/reembed_episodic_memories.py --batch-size 64 --dry-run

Reads DB + embedding config from STARRY_LYFE__* env vars (see .env.example).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from uuid import UUID

from sqlalchemy import select, update

from starry_lyfe.db.embed import EmbeddingService, LMStudioEmbeddingService
from starry_lyfe.db.engine import build_engine, build_session_factory, close_db
from starry_lyfe.db.models.episodic_memory import EpisodicMemory

logger = logging.getLogger("reembed")


async def _reembed(batch_size: int, dry_run: bool) -> int:
    engine = build_engine()
    session_factory = build_session_factory(engine)
    embedding_service: EmbeddingService = LMStudioEmbeddingService()

    rewritten = 0
    try:
        async with session_factory() as session:
            total = (
                await session.execute(select(EpisodicMemory.id))
            ).scalars().all()
            logger.info("found %d rows in episodic_memories", len(total))

            for start in range(0, len(total), batch_size):
                batch_ids: list[UUID] = list(total[start : start + batch_size])
                rows = (
                    await session.execute(
                        select(EpisodicMemory.id, EpisodicMemory.event_summary).where(
                            EpisodicMemory.id.in_(batch_ids)
                        )
                    )
                ).all()
                if not rows:
                    continue
                texts = [row.event_summary for row in rows]
                logger.info(
                    "batch %d-%d: embedding %d rows",
                    start,
                    start + len(rows) - 1,
                    len(rows),
                )
                vectors = await embedding_service.embed_batch(texts)
                if len(vectors) != len(rows):
                    raise RuntimeError(
                        f"embedding count mismatch: got {len(vectors)} vectors for {len(rows)} rows"
                    )
                if dry_run:
                    rewritten += len(rows)
                    continue
                for row, vector in zip(rows, vectors, strict=True):
                    await session.execute(
                        update(EpisodicMemory)
                        .where(EpisodicMemory.id == row.id)
                        .values(embedding=vector)
                    )
                await session.commit()
                rewritten += len(rows)
    finally:
        await close_db(engine)
    return rewritten


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = _parse_args()
    rewritten = asyncio.run(_reembed(args.batch_size, args.dry_run))
    verb = "would rewrite" if args.dry_run else "rewrote"
    logger.info("%s %d rows", verb, rewritten)
    return 0


if __name__ == "__main__":
    sys.exit(main())
