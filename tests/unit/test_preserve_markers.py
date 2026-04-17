"""Phase 10.6 C1: preserve_marker enforcement in assembled Layer 1 output.

Strictly stronger than the YAML-body check in ``test_rich_loader.py``:
runs the full ``assemble_context()`` pipeline for each of the 4 women
across realistic scene profiles and asserts each ``content_anchor``
appears verbatim in the Layer 1 rendered text. This catches any
regression where Phase A structure-preserving trim, soul essence
prepend, soul card activation, or other Layer 1 transforms drop a
canonical phrase under budget pressure.

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §1 + AC-10.3 +
AC-10.11 + AC-10.12.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from starry_lyfe.canon.rich_loader import (
    get_preserve_markers,
    load_rich_character,
    verify_preserve_markers,
)
from starry_lyfe.context import assembler as assembler_module
from starry_lyfe.context.assembler import assemble_context
from starry_lyfe.context.types import CommunicationMode, SceneState

_WHITESPACE_RE = re.compile(r"\s+")
# Sentence boundary: terminal punctuation followed by whitespace + uppercase
# OR end-of-text. Conservative — does not split on abbreviations like "Mr."
# because anchors don't currently use them.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")

# Phase 10.6 closeout F2 known-gap allowlist (2026-04-17): anchors where the
# canonical KEY sentence reaches Layer 1 via a guaranteed surcharge surface
# (e.g., pair_architecture.callbacks) but an elaboration sentence in the
# longer kernel-section prose may be trimmed by Phase A under budget. These
# are deliberate authoring decisions: the callbacks block is the canonical
# Layer 1 home for the load-bearing key, and the elaboration is contextual
# prose that can absorb trim. Any anchor here MUST have its first sentence
# (the canonical key) in Layer 1 verbatim — only later-elaboration sentences
# may be allowed to fall out.
#
# Format: {(character_id, marker_id): [<elaboration sentence prefix>, ...]}
# Listed sentences are EXEMPTED from the verbatim-in-Layer-1 requirement
# IFF at least one earlier sentence of the same anchor IS present in Layer 1.
_LAYER_1_KNOWN_ELABORATION_GAPS: dict[tuple[str, str], list[str]] = {
    ("reina", "fighting_is_the_affection"): [
        "Two Mediterranean women far from the coast",
    ],
}


def _normalize_whitespace(text: str) -> str:
    """Collapse all whitespace runs (spaces, tabs, newlines) to single spaces.

    Phase 10.6 closeout F2 (2026-04-17): preserve_markers carry block-scalar
    text from YAML where line wraps + indentation insert non-canonical
    whitespace. Layer 1 assembly emits prose with different wraps. Comparing
    both sides through this normalizer keeps the verbatim contract honest
    against formatting variation while still failing on actual word changes.
    """
    return _WHITESPACE_RE.sub(" ", text).strip()


def _anchor_sentences(anchor: str) -> list[str]:
    """Split an anchor into sentence-level units for individual verbatim checks.

    Phase 10.6 closeout F2: returns each sentence (≥10 chars) as an
    independent unit. The Layer 1 verification then requires each unit
    individually present, catching drift that the prior "any sentence"
    pass would miss while honoring synthesis anchors that interpolate
    other prose between key sentences.
    """
    parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(anchor) if p.strip()]
    return [p for p in parts if len(p) >= 10] or [anchor.strip()]

WOMAN_IDS = ("adelia", "bina", "reina", "alicia")


class _StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]


def _empty_bundle() -> SimpleNamespace:
    """Minimal retrieve_memories stub that yields a clean MemoryBundle shape."""
    return SimpleNamespace(
        canon_facts=[],
        character_baseline=None,
        dyad_states_whyze=[],
        dyad_states_internal=[],
        episodic_memories=[],
        open_loops=[],
        somatic_state=None,
        activities=[],
    )


# Scene profiles to exercise Layer 1 across varied budget/activation paths.
# (profile_label, SceneState-kwargs) — the assembler derives scene type
# from present_characters + communication_mode.
_SCENE_PROFILES: list[tuple[str, dict[str, Any]]] = [
    (
        "solo_default",
        {
            "present_characters_include_whyze": True,
            "scene_description": "{character} alone with Whyze at the property.",
            "communication_mode": CommunicationMode.IN_PERSON,
        },
    ),
    (
        "multi_woman",
        {
            "present_characters_include_whyze": True,
            "extra_present": ["bina", "reina"],
            "scene_description": "{character} at the property with Bina and Reina.",
            "communication_mode": CommunicationMode.IN_PERSON,
        },
    ),
]


def _build_scene_state(character_id: str, profile: dict[str, Any]) -> SceneState:
    present: list[str] = [character_id]
    if profile.get("present_characters_include_whyze"):
        present.append("whyze")
    for extra in profile.get("extra_present", []):
        if extra != character_id and extra not in present:
            present.append(extra)
    # Alicia in-person assembly requires alicia_home=True (P3-02 contract).
    alicia_home = character_id == "alicia" or "alicia" in present
    return SceneState(
        present_characters=present,
        scene_description=str(profile["scene_description"]).format(character=character_id),
        communication_mode=profile["communication_mode"],
        alicia_home=alicia_home,
    )


class TestPreserveMarkersInAssembledLayer1:
    """AC-10.3: preserve_marker content_anchors verbatim in Layer 1 output."""

    @pytest.mark.parametrize("character_id", WOMAN_IDS)
    @pytest.mark.parametrize("profile_label,profile", _SCENE_PROFILES)
    async def test_anchors_verbatim_in_layer_1(
        self,
        monkeypatch: pytest.MonkeyPatch,
        character_id: str,
        profile_label: str,
        profile: dict[str, Any],
    ) -> None:
        """Each content_anchor must appear verbatim in the assembled Layer 1 text.

        Asserts the full canonical promise: not just that the anchor
        exists in YAML, but that it survives Phase A trim + soul essence
        prepend + pair-architecture callbacks block + soul card
        activation and reaches the LLM prompt.
        """
        async def stub_retrieve_memories(*args: object, **kwargs: object) -> Any:
            return _empty_bundle()

        monkeypatch.setattr(assembler_module, "retrieve_memories", stub_retrieve_memories)

        scene_state = _build_scene_state(character_id, profile)
        prompt = await assemble_context(
            character_id=character_id,
            scene_context=scene_state.scene_description,
            scene_state=scene_state,
            session=None,
            embedding_service=_StubEmbeddingService(),
        )
        layer_1 = next(layer for layer in prompt.layers if layer.layer_number == 1)
        layer_1_text = layer_1.text

        rc = load_rich_character(character_id)
        markers = get_preserve_markers(rc)

        # Phase 10.6 closeout re-audit F2 (2026-04-17): tightened to require
        # EVERY SENTENCE of each anchor verbatim in Layer 1 (with whitespace
        # normalization). The earlier "any sentence OR 40-char prefix" pass
        # was too loose: a red-team probe showed a 40-char prefix like
        # "I am Bina Malek. Forty. First-generation" would satisfy the test
        # even though the rest of the canonical paragraph was missing.
        #
        # Why per-sentence (not whole-block-contiguous): some authored
        # anchors are syntheses of key sentences from a longer kernel
        # paragraph (e.g., Adelia's `soul_mate_anchor` is "He is my soul
        # mate. We are each other's everything." but the rendered prose
        # interpolates "I love no one else in the world more than him. He
        # feels the same way." between the two sentences). The synthesis
        # anchors are deliberate canonical key-phrase digests; the right
        # contract is "every constituent sentence individually present in
        # Layer 1", which catches drift while honoring the synthesis design.
        missing: list[str] = []
        layer_1_normalized = _normalize_whitespace(layer_1_text)
        for marker in markers:
            anchor = marker.content_anchor.strip()
            if anchor.endswith("..."):
                anchor = anchor[:-3].rstrip()
            sentences = _anchor_sentences(anchor)
            if not sentences:
                continue
            allowed_gaps = _LAYER_1_KNOWN_ELABORATION_GAPS.get(
                (character_id, marker.id), []
            )
            absent: list[str] = []
            present_count = 0
            for s in sentences:
                if _normalize_whitespace(s) in layer_1_normalized:
                    present_count += 1
                    continue
                # Elaboration-gap exemption: only valid if at least one
                # earlier sentence is already present in Layer 1, so the
                # canonical key is verifiable.
                if present_count > 0 and any(s.startswith(g) for g in allowed_gaps):
                    continue
                absent.append(s)
            if absent:
                missing.append(
                    f"{character_id}::{marker.id} (profile={profile_label}): "
                    f"{len(absent)}/{len(sentences)} sentence(s) not in Layer 1 verbatim "
                    f"(missing: {[s[:60] for s in absent]!r})"
                )

        assert not missing, "\n".join(missing)


# ----------------------------------------------------------------------
# Phase 10.6 closeout (2026-04-17): Shawn preserve_marker coverage
# ----------------------------------------------------------------------

# Shawn is the operator, not a renderable character — there is no
# `assemble_context()` Layer 1 path for him. His preserve_markers
# enforce verbatim presence in his rich YAML body itself, via the
# rich_loader.verify_preserve_markers helper. This closes the
# Phase 10.6 audit gap (2026-04-17) where the original test only
# iterated WOMAN_IDS and left Shawn's 18 canonical anchors uncovered.

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SHAWN_YAML_PATH = REPO_ROOT / "Characters" / "shawn_kroon.yaml"


def test_shawn_preserve_markers_appear_verbatim_in_yaml_body() -> None:
    """Phase 10.6 closeout AC: Shawn's preserve_marker.content_anchor strings
    must each appear verbatim somewhere in shawn_kroon.yaml. Catches any
    edit that paraphrases or removes a load-bearing canonical phrase."""
    shawn = load_rich_character("shawn")
    markers = get_preserve_markers(shawn)
    assert markers, "Shawn rich YAML expected to carry preserve_markers (18 anchors as of 2026-04-17)"

    full_text = SHAWN_YAML_PATH.read_text(encoding="utf-8")
    errors = verify_preserve_markers(shawn, full_text=full_text)
    assert not errors, (
        "Shawn preserve_marker drift — anchors missing from YAML body:\n  "
        + "\n  ".join(errors)
    )
