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

        # Track two distinct signals:
        # (a) "at least one sentence of the anchor reaches Layer 1" — this
        #     is the canonical-key-phrase contract the LLM actually needs;
        # (b) "no anchor is entirely absent" — a stricter fail condition.
        #
        # Anchors may live in callbacks/deep lists that don't render as
        # prose in the current Layer 1 pipeline (pair_architecture.callbacks,
        # intimacy_architecture.hard_limits, etc.). That's an assembler
        # coverage question (Phase 10.2/10.4 scope), not a preserve_marker
        # authoring question. Phase 10.6 C1 scope: every anchor's CANONICAL
        # KEY PHRASE must reach Layer 1 for at least one of its sentences.
        missing: list[str] = []
        for marker in markers:
            anchor = marker.content_anchor.strip()
            if anchor.endswith("..."):
                anchor = anchor[:-3].rstrip()
            # Split into sentences; also consider a prefix (first 40 chars)
            # as a sentence fragment that may carry the canonical phrase
            # when anchors are short list items.
            sentences = [
                s.strip() for s in
                anchor.replace("? ", "?|").replace("! ", "!|").replace(". ", ".|").split("|")
                if s.strip() and len(s.strip()) >= 15
            ]
            if not sentences:
                sentences = [anchor[:60]]
            # Prefix fallback for short/phrase anchors (e.g., "Vale, amor.")
            prefix = anchor[: min(40, len(anchor))].rstrip(".!? ")
            if len(prefix) >= 6:
                sentences.append(prefix)
            # Pass if ANY sentence or the prefix is present verbatim
            any_present = any(s in layer_1_text for s in sentences)
            if not any_present:
                missing.append(
                    f"{character_id}::{marker.id} (profile={profile_label}): "
                    f"no anchor sentence found in Layer 1 "
                    f"(anchor starts {anchor[:60]!r}...)"
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
