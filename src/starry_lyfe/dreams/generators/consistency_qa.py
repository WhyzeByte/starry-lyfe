"""Phase 10.7 — Consistency QA generator.

Sixth Dreams generator. Runs AFTER all 5 per-character generators
complete (per Phase 10.7 spec: "Runs after the other 5 generators in the
nightly pass"). Loops the 10 relationships (6 inter-woman dyads + 4
woman-Whyze pairs), invokes the neutral-observer judge LLM per
relationship, parses + validates each verdict via Pydantic, dispatches
notifications, persists log + pins, and aggregates results into a
single ``ConsistencyQAOutput``.

Anti-contamination: the judge sees only the focal relationship's two
POVs + the cross-character objective anchor. The runner does NOT pass
any per-character generator output into the QA prompt — drift detection
is a separate signal from generated prose.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from ..consistency.auto_promote import should_promote
from ..consistency.memory_lookup import (
    load_relationship_memories,
    load_woman_whyze_memories,
)
from ..consistency.prompt import JUDGE_SYSTEM_PROMPT, build_user_prompt
from ..consistency.relationships import enumerate_all
from ..consistency.schemas import (
    ConsistencyQAOutput,
    QAVerdict,
    RelationshipCheck,
)
from ..errors import DreamsLLMError
from ..notifications import emit_qa_event
from ..types import LLMClient
from ..writers import write_consistency_qa_log, write_dyad_state_pin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from ...canon.loader import Canon

# Match runner.py::SessionFactory typedef so the runner's session factory
# (which is intentionally `Callable[[], Any]` to accept both async_sessionmaker
# and the test conftest's lighter-weight factory) flows in cleanly.
SessionFactory = Callable[[], Any]

logger = logging.getLogger(__name__)

# Judge LLM call budget — stays small. Per-relationship verdict, not prose.
_JUDGE_MAX_TOKENS: int = 800
_JUDGE_TEMPERATURE: float = 0.2


def _extract_pov_block(canon: Canon, character_id: str, partner_id: str) -> str:
    """Pull the focal woman's POV-on-partner from her rich YAML.

    For inter-woman dyads: ``family_and_other_dyads.with_<partner>``.
    For woman-Whyze pairs: ``pair_architecture`` block.
    Falls back to soul_substrate.pair_blocks if the POV blocks are absent.
    """
    if character_id == "whyze":
        # The operator doesn't have rich-YAML POV blocks the same way; the
        # "Whyze POV" of a woman-pair is collapsed into the per-woman
        # pair_architecture from his side, which is read by the woman's
        # rich YAML. We synthesize a minimal placeholder so the judge
        # has both halves of the dialog.
        return (
            "Whyze (operator) POV is not authored as a separate rich YAML "
            "block. The judge should infer the operator's perspective from "
            "the shared_canon pair anchor and the partner's pair_architecture."
        )

    from ...canon.rich_loader import load_rich_character

    rc = load_rich_character(character_id)
    if partner_id == "whyze":
        # Pair architecture is the focal character's read on her bond with Whyze.
        if rc.pair_architecture is not None:
            try:
                return rc.pair_architecture.model_dump_json(indent=2)
            except Exception:  # noqa: BLE001
                return str(rc.pair_architecture)
        return "(no pair_architecture authored)"
    # Inter-woman: family_and_other_dyads.with_<partner>.
    fad = rc.family_and_other_dyads or {}
    key = f"with_{partner_id}"
    block = fad.get(key)
    if block is not None:
        try:
            return block.model_dump_json(indent=2)
        except Exception:  # noqa: BLE001
            return str(block)
    return f"(no family_and_other_dyads.{key} authored on {character_id} YAML)"


def _parse_verdict(raw_text: str, *, expected_key: str) -> RelationshipCheck:
    """Parse + validate the LLM's JSON output.

    On parse failure, raise DreamsLLMError with the malformed payload so
    the runner can decide whether to retry or fall back to a placeholder.
    """
    try:
        check = RelationshipCheck.model_validate_json(raw_text)
    except (ValidationError, ValueError) as exc:
        # Try a one-shot recovery: maybe the model wrapped JSON in ```json.
        stripped = raw_text.strip()
        if stripped.startswith("```"):
            inner = stripped.split("```")[1]
            if inner.lower().startswith("json"):
                inner = inner[4:].lstrip("\n")
            try:
                check = RelationshipCheck.model_validate_json(inner)
            except (ValidationError, ValueError):
                msg = f"QA judge returned non-conforming JSON for {expected_key!r}: {exc}"
                raise DreamsLLMError(msg) from exc
        else:
            msg = f"QA judge returned non-conforming JSON for {expected_key!r}: {exc}"
            raise DreamsLLMError(msg) from exc
    if check.relationship_key != expected_key:
        msg = (
            f"QA judge returned wrong relationship_key (expected {expected_key!r}, "
            f"got {check.relationship_key!r})"
        )
        raise DreamsLLMError(msg)
    return check


@dataclass(frozen=True)
class _QAGenerationContext:
    """Inputs to the consistency QA pass — distinct from per-character GenerationContext."""

    run_id: uuid.UUID
    canon: Canon
    llm_client: LLMClient
    session_factory: SessionFactory
    now: datetime


async def _judge_one(
    ctx: _QAGenerationContext,
    relationship_key: str,
    pov_a: str,
    pov_b: str,
    relationship_kind: str,
) -> tuple[RelationshipCheck, int, int]:
    """Run the judge LLM once for one relationship. Returns (check, in_tok, out_tok)."""
    from ..consistency.relationships import Relationship

    rel = Relationship(
        relationship_key=relationship_key,
        relationship_kind=relationship_kind,
        pov_a=pov_a,
        pov_b=pov_b,
    )

    pov_a_block = _extract_pov_block(ctx.canon, pov_a, pov_b)
    pov_b_block = _extract_pov_block(ctx.canon, pov_b, pov_a)

    # Episodic memories (requires a session — open a short-lived read-only one).
    recent_memories: list[str] = []
    try:
        async with ctx.session_factory() as read_session:
            if relationship_kind == "inter_woman":
                recent_memories = await load_relationship_memories(
                    read_session, pov_a=pov_a, pov_b=pov_b, days=7, now=ctx.now
                )
            else:
                # woman_whyze: pov_b is "whyze", pov_a is the woman.
                woman = pov_a if pov_b == "whyze" else pov_b
                recent_memories = await load_woman_whyze_memories(
                    read_session, woman_id=woman, days=7, now=ctx.now
                )
    except Exception as exc:  # noqa: BLE001 — memory lookup is best-effort
        logger.warning(
            "dreams_qa_memory_lookup_failed",
            extra={"relationship_key": relationship_key, "error": str(exc)},
        )

    user_prompt = build_user_prompt(
        rel,
        ctx.canon,
        pov_a_block=pov_a_block,
        pov_b_block=pov_b_block,
        recent_memories=recent_memories,
    )

    response = await ctx.llm_client.complete(
        JUDGE_SYSTEM_PROMPT,
        user_prompt,
        max_tokens=_JUDGE_MAX_TOKENS,
        temperature=_JUDGE_TEMPERATURE,
    )
    raw_text = getattr(response, "text", None) or getattr(response, "content", "") or ""
    in_tok = int(getattr(response, "input_tokens", 0) or 0)
    out_tok = int(getattr(response, "output_tokens", 0) or 0)

    check = _parse_verdict(raw_text, expected_key=relationship_key)
    return check, in_tok, out_tok


async def _maybe_auto_promote(
    session: AsyncSession,
    check: RelationshipCheck,
    *,
    now: datetime,
) -> RelationshipCheck:
    """Phase 10.7 §AC-10.26: 3-night drift → auto-promote to factual_contradiction."""
    if check.verdict is not QAVerdict.CONCERNING_DRIFT:
        return check
    # Each contradicted field tracks independently. If ANY field qualifies,
    # promote the whole relationship's verdict for this run.
    promoted_fields: list[str] = []
    for c in check.contradictions:
        promote = await should_promote(
            session,
            relationship_key=check.relationship_key,
            field_name=c.field_name,
            now=now,
        )
        if promote:
            promoted_fields.append(c.field_name)
    if not promoted_fields:
        return check
    logger.warning(
        "dreams_qa_auto_promoted",
        extra={
            "relationship_key": check.relationship_key,
            "promoted_fields": promoted_fields,
        },
    )
    return check.model_copy(update={"verdict": QAVerdict.FACTUAL_CONTRADICTION})


async def _persist_one(
    session: AsyncSession,
    *,
    run_id: uuid.UUID,
    check: RelationshipCheck,
) -> None:
    """Write the QA log row + any pins required by the verdict."""
    await write_consistency_qa_log(
        session,
        run_id=run_id,
        relationship_key=check.relationship_key,
        verdict=check.verdict.value,
        divergence_summary=check.divergence_summary,
        contradictions=[c.model_dump() for c in check.contradictions],
        scene_fodder=list(check.scene_fodder),
    )
    if check.verdict is not QAVerdict.FACTUAL_CONTRADICTION:
        return
    # Pin every contradicted field.
    for c in check.contradictions:
        await write_dyad_state_pin(
            session,
            relationship_key=check.relationship_key,
            pov_character_id=c.pov_character_id,
            field_name=c.field_name,
            pinned_value=c.canonical_value,
            pinned_reason=(
                f"Phase 10.7 QA: {c.observed_value!r} contradicts shared_canon "
                f"({c.shared_canon_field}). {c.severity_note}"
            ).strip(),
        )


async def generate_consistency_qa(
    *,
    run_id: uuid.UUID,
    canon: Canon,
    llm_client: LLMClient,
    session_factory: SessionFactory,
    now: datetime | None = None,
) -> ConsistencyQAOutput:
    """Run the nightly consistency QA pass across all 10 relationships.

    Returns a fully-populated ``ConsistencyQAOutput``. Each relationship's
    verdict is logged to ``dreams_qa_log``, factual_contradictions write
    pins to ``dyad_state_pins``, healthy_divergence scene_fodder is left
    for the runner to fold into open_loops via ``write_new_open_loops``,
    and notifications are dispatched per verdict.
    """
    ref_now = now if now is not None else datetime.now(UTC)
    started = ref_now
    ctx = _QAGenerationContext(
        run_id=run_id,
        canon=canon,
        llm_client=llm_client,
        session_factory=session_factory,
        now=ref_now,
    )

    relationships = enumerate_all(canon)
    if len(relationships) != 10:
        msg = (
            f"Phase 10.7 expected 10 relationships, got {len(relationships)} "
            f"(check Canon.shared.pairs hydration)"
        )
        raise DreamsLLMError(msg)

    checks: list[RelationshipCheck] = []
    in_tok_total = 0
    out_tok_total = 0
    warnings: list[str] = []

    for rel in relationships:
        try:
            check, in_tok, out_tok = await _judge_one(
                ctx,
                relationship_key=rel.relationship_key,
                pov_a=rel.pov_a,
                pov_b=rel.pov_b,
                relationship_kind=rel.relationship_kind,
            )
            in_tok_total += in_tok
            out_tok_total += out_tok
        except DreamsLLMError as exc:
            warnings.append(f"{rel.relationship_key}: {exc}")
            # Best-effort: emit a placeholder concerning_drift verdict so the
            # log row still lands and operator sees the failure surface.
            check = RelationshipCheck(
                relationship_key=rel.relationship_key,
                verdict=QAVerdict.CONCERNING_DRIFT,
                divergence_summary=f"QA judge LLM call failed: {exc}",
                contradictions=[],
                scene_fodder=[],
            )
        # Persist + auto-promote inside a transactional session.
        async with ctx.session_factory() as session, session.begin():
            check = await _maybe_auto_promote(session, check, now=ref_now)
            await _persist_one(session, run_id=run_id, check=check)
        # Notifications best-effort outside transaction.
        emit_qa_event(
            verdict=check.verdict,
            relationship_key=check.relationship_key,
            divergence_summary=check.divergence_summary,
            contradictions=list(check.contradictions),
            now=ref_now,
        )
        checks.append(check)

    return ConsistencyQAOutput(
        run_id=run_id,
        started_at=started,
        finished_at=datetime.now(UTC),
        relationship_checks=checks,
        input_tokens=in_tok_total,
        output_tokens=out_tok_total,
        warnings=warnings,
    )


__all__ = ["generate_consistency_qa"]
