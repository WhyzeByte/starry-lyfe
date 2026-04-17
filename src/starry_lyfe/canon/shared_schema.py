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
    """Phase 10.5c: ``birthdate`` is the durable source of truth (age is derived).

    Authored ``age`` remains as a cached value for current consumers but
    will go stale; hydration prefers ``birthdate`` when authored.
    """

    subject: str
    biological_parents: list[str] | None = None
    legal_parents: list[str] | None = None
    birthdate: str | None = None
    age: int | None = None


class PropertyFact(_Permissive):
    location: str
    layout_summary: str | None = None


class TimelineAnchor(_Permissive):
    id: str
    date: str | None = None
    description: str


class SharedPair(_Permissive):
    """Phase 10.5c expansion: SharedPair carries all narrow ``Pair`` fields.

    Per Phase 10.5c §2.5 single-source-of-truth decision: narrow
    ``CanonPairs.pairs[*]`` hydrates exclusively from this surface.
    Per-woman ``pair_architecture`` blocks remain POV prose for prompt
    assembly and DO NOT hydrate the typed Pair object.
    """

    canonical_name: str
    classification: str | None = None
    mechanism: str | None = None
    # --- Phase 10.5c additions (single-source for narrow Pair) ---
    character: str | None = None
    shared_functions: str | None = None
    what_she_provides: str | None = None
    how_she_breaks_spiral: str | None = None
    core_metaphor: str | None = None
    cadence: str | None = None


class MemoryTierEntry(_Permissive):
    """Phase 10.5c: a single memory-tier definition.

    Per Phase 10.5c §2.4: 7 system-level memory tiers (Canon Facts,
    Character Baseline, Dyad State Whyze/Internal, Episodic, Open Loops,
    Transient Somatic). Hydrates narrow ``CanonDyads.memory_tiers``.
    """

    name: str
    tier: int
    mutable: bool
    description: str


class DyadDimension(_Permissive):
    """Phase 10.5c: a single dyad dimension baseline triplet."""

    baseline: float
    min: float
    max: float


class DyadDimensionsBlock(_Permissive):
    """Phase 10.5c: the five canonical dyad dimensions."""

    trust: DyadDimension
    intimacy: DyadDimension
    conflict: DyadDimension
    unresolved_tension: DyadDimension
    repair_history: DyadDimension


class DyadBaseline(_Permissive):
    """Phase 10.5c: a single dyad baseline entry.

    Per Phase 10.5c §2.4 D1: 10 entries (6 inter-woman + 4 Whyze-pair).
    Hydrates narrow ``CanonDyads.dyads``.
    """

    members: list[str]
    type: str
    subtype: str | None = None
    interlock: str | None = None
    pair: str | None = None
    is_currently_active: bool | None = None
    dimensions: DyadDimensionsBlock


class InterlockEntry(_Permissive):
    """Phase 10.5c: a single cross-partner interlock entry.

    Per Phase 10.5c §2.4 I2: 6 interlocks centralized as objective
    taxonomy. Hydrates narrow ``CanonInterlocks.interlocks``. Per-woman
    ``family_and_other_dyads`` blocks remain POV prose.
    """

    key: str
    name: str
    members: list[str]
    description: str
    tone: str
    type: str
    origin: str | None = None
    canonical_disagreement: str | None = None


class SharedCanon(_Permissive):
    """Top-level schema for ``shared_canon.yaml``.

    Phase 10.5c expansion: gains ``memory_tiers``, ``dyads_baseline``,
    ``interlocks`` blocks for cross-character objective taxonomies that
    have no per-character home.
    """

    version: str
    marriage: MarriageRecord | None = None
    signature_scenes: list[SignatureSceneAnchor] | None = None
    genealogy: list[GenealogyFact] | None = None
    property: PropertyFact | None = None
    timeline: list[TimelineAnchor] | None = None
    pairs: list[SharedPair] | None = None
    # --- Phase 10.5c additions (cross-character objective taxonomies) ---
    memory_tiers: list[MemoryTierEntry] | None = None
    dyads_baseline: dict[str, DyadBaseline] | None = None
    interlocks: list[InterlockEntry] | None = None
