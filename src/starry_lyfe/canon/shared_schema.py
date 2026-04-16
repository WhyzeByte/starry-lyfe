"""Pydantic v2 schemas for ``shared_canon.yaml`` (Phase 10.1).

``shared_canon.yaml`` holds the small set of objective facts that are
not anyone's perspective — dates, genealogy, property, timeline anchors,
and canonical pair names. Content where divergence between two per-
character YAMLs would create a continuity contradiction.

Per-character YAML blocks may *reference* shared_canon entries (via
``anchor_id``) but must not *contradict* them. Phase 10.6 adds a test
(``test_shared_canon_purity.py``) that enforces this invariant.

Authority: ``Docs/_phases/PHASE_10.md`` §1.4 + §Phase 10.1 WI2 +
``Docs/_phases/PHASE_10_GAP_AUDIT.md`` §4.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Permissive(BaseModel):
    model_config = ConfigDict(extra="allow")


class MarriageRecord(_Permissive):
    partners: list[str]
    year: int | None = None
    canonical_scene_id: str | None = None


class SignatureSceneAnchor(_Permissive):
    id: str
    date: str | None = None
    participants: list[str]
    objective_description: str


class GenealogyFact(_Permissive):
    subject: str
    biological_parents: list[str] | None = None
    legal_parents: list[str] | None = None
    age: int | None = None


class PropertyFact(_Permissive):
    location: str
    layout_summary: str | None = None


class TimelineAnchor(_Permissive):
    id: str
    date: str | None = None
    description: str


class SharedPair(_Permissive):
    canonical_name: str
    classification: str | None = None
    mechanism: str | None = None


class SharedCanon(_Permissive):
    """Top-level schema for ``shared_canon.yaml``."""

    version: str
    marriage: MarriageRecord | None = None
    signature_scenes: list[SignatureSceneAnchor] | None = None
    genealogy: list[GenealogyFact] | None = None
    property: PropertyFact | None = None
    timeline: list[TimelineAnchor] | None = None
    pairs: list[SharedPair] | None = None
