"""``GET /v1/models`` — five-entry registry.

Per CLAUDE.md §14: legacy ``starry-lyfe`` (default character routing) plus
one entry per canonical character. The four canonical IDs match the
character names exactly so Msty's ``model`` field can route directly.
"""

from __future__ import annotations

from fastapi import APIRouter

from starry_lyfe.canon.schemas.enums import CharacterID

from ..schemas.models import ModelEntry, ModelListResponse

router = APIRouter()

# Fixed creation epoch (2026-04-15 ship date for Phase 7) — clients that
# care about the ``created`` field just need a stable value.
_PHASE_7_CREATED_EPOCH = 1776816000


@router.get("/v1/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """Return the 5-entry model registry."""
    entries: list[ModelEntry] = [
        ModelEntry(id="starry-lyfe", created=_PHASE_7_CREATED_EPOCH),
    ]
    entries.extend(
        ModelEntry(id=char_id, created=_PHASE_7_CREATED_EPOCH)
        for char_id in CharacterID.all_strings()
    )
    return ModelListResponse(data=entries)
