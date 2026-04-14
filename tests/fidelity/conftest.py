"""Phase F-Fidelity test fixtures: load rubrics + scenes from YAML.

Provides:
- ``load_rubrics(character_id) -> dict[dimension_name, FidelityRubric]``
- ``load_scenes(character_id) -> list[dict]``
- ``make_bundle(character_id) -> SimpleNamespace`` (memory stub for assemble_context)
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from starry_lyfe.context.types import CommunicationMode, SceneState, SceneType
from starry_lyfe.validation.fidelity import FidelityRubric

FIDELITY_DIR = Path(__file__).resolve().parent
RUBRICS_DIR = FIDELITY_DIR / "rubrics"
SCENES_DIR = FIDELITY_DIR / "scenes"


def load_rubrics(character_id: str) -> dict[str, FidelityRubric]:
    """Load all rubrics for a character from tests/fidelity/rubrics/{character}.yaml."""
    path = RUBRICS_DIR / f"{character_id}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["character_id"] == character_id

    rubrics: dict[str, FidelityRubric] = {}
    for dimension, spec in data["rubrics"].items():
        rubrics[dimension] = FidelityRubric(
            dimension=dimension,
            character_id=character_id,
            canonical_markers=tuple(spec.get("canonical_markers", [])),
            anti_patterns=tuple(spec.get("anti_patterns", [])),
            required_structural=tuple(spec.get("required_structural", [])),
            min_score=float(spec.get("min_score", 0.7)),
        )
    return rubrics


def load_scenes(character_id: str) -> list[dict[str, Any]]:
    """Load all scenes for a character from tests/fidelity/scenes/{character}.yaml."""
    path = SCENES_DIR / f"{character_id}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["character_id"] == character_id
    return list(data["scenes"])


def build_scene_state(spec: dict[str, Any]) -> SceneState:
    """Construct a SceneState from a YAML scene spec."""
    raw = dict(spec)
    if "scene_type" in raw:
        raw["scene_type"] = SceneType(raw["scene_type"].lower())
    if "communication_mode" in raw:
        raw["communication_mode"] = CommunicationMode(raw["communication_mode"].lower())
    return SceneState(**raw)


# Per-character profile data for memory bundle stubs. Mirrors the
# tests/unit/test_assembler.py::_make_bundle pattern.
PROFILES: dict[str, dict[str, str]] = {
    "adelia": {
        "full_name": "Adelia Raye", "epithet": "The Catalyst", "mbti": "ENFP-A",
        "dominant_function": "Ne", "pair_name": "entangled",
        "pair_classification": "asymmetrical cognitive interlock",
        "pair_mechanism": "Chaos-to-structure handoff",
        "pair_core_metaphor": "The Gravity and the Space",
        "heritage": "Valencian-Australian",
        "profession": "Pyrotechnic artist / ethical hacker",
        "response_length_range": "2-4 paragraphs",
        "dominant_function_descriptor": "energy-first, tangent-resolving ideation",
        "internal_member": "bina",
    },
    "bina": {
        "full_name": "Bina Malek", "epithet": "The Sentinel", "mbti": "ISFJ-A",
        "dominant_function": "Si", "pair_name": "circuit",
        "pair_classification": "structural complement",
        "pair_mechanism": "Total division of operational domains",
        "pair_core_metaphor": "The Architect and the Sentinel",
        "heritage": "Assyrian-Iranian Canadian", "profession": "Mechanic",
        "response_length_range": "2-4 sentences",
        "dominant_function_descriptor": "Si-dominant declarative steadiness",
        "internal_member": "reina",
    },
    "reina": {
        "full_name": "Reina Torres", "epithet": "The Operator", "mbti": "ESTP-A",
        "dominant_function": "Se", "pair_name": "kinetic",
        "pair_classification": "asymmetrical leverage",
        "pair_mechanism": "Temporal collision converted to engine heat",
        "pair_core_metaphor": "The Mastermind and the Operator",
        "heritage": "Barcelona Catalan-Castilian",
        "profession": "Criminal defence lawyer",
        "response_length_range": "1-3 paragraphs",
        "dominant_function_descriptor": "Se-dominant tactical presence",
        "internal_member": "bina",
    },
    "alicia": {
        "full_name": "Alicia Marin", "epithet": "The Solstice", "mbti": "ESFP-A",
        "dominant_function": "Se", "pair_name": "solstice",
        "pair_classification": "structural complement",
        "pair_mechanism": "Inferior-function gift exchange",
        "pair_core_metaphor": "The Duality",
        "heritage": "Argentine", "profession": "Operative",
        "response_length_range": "Short-to-medium",
        "dominant_function_descriptor": "Se-dominant somatic co-regulation",
        "internal_member": "adelia",
    },
}


def make_bundle(character_id: str) -> SimpleNamespace:
    """Memory bundle stub matching tests/unit/test_assembler.py pattern."""
    profile = PROFILES[character_id]
    baseline = SimpleNamespace(
        full_name=profile["full_name"], epithet=profile["epithet"],
        mbti=profile["mbti"], dominant_function=profile["dominant_function"],
        pair_name=profile["pair_name"],
        pair_classification=profile["pair_classification"],
        pair_mechanism=profile["pair_mechanism"],
        pair_core_metaphor=profile["pair_core_metaphor"],
        heritage=profile["heritage"], profession=profile["profession"],
        voice_params={
            "response_length_range": profile["response_length_range"],
            "dominant_function_descriptor": profile["dominant_function_descriptor"],
        },
    )
    return SimpleNamespace(
        canon_facts=[
            SimpleNamespace(fact_key=f"fact_{i}", fact_value="value")
            for i in range(24)
        ],
        character_baseline=baseline,
        dyad_states_whyze=[
            SimpleNamespace(
                pair_name=baseline.pair_name,
                trust=0.80, intimacy=0.65, conflict=0.15, unresolved_tension=0.25,
            )
        ],
        dyad_states_internal=[
            SimpleNamespace(
                member_a=character_id, member_b=profile["internal_member"],
                interlock="anchor_dynamic", trust=0.72, intimacy=0.55, conflict=0.20,
            )
        ],
        episodic_memories=[
            SimpleNamespace(
                event_summary=f"Memory summary {i} " * 6,
                emotional_temperature=0.30 + (i * 0.05),
            )
            for i in range(8)
        ],
        open_loops=[
            SimpleNamespace(urgency="high", loop_summary="Follow up on the kitchen conversation."),
            SimpleNamespace(urgency="medium", loop_summary="Revisit the unresolved shop scheduling detail."),
        ],
        somatic_state=SimpleNamespace(
            character_id=character_id, fatigue=0.42,
            stress_residue=0.18, injury_residue=0.00, active_protocols=[],
        ),
    )


class StubEmbeddingService:
    """Embedding stub for fidelity tests (no real embedding calls)."""

    async def embed(self, text: str) -> list[float]:
        return [0.0] * 384
