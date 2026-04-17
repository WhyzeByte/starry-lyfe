"""Phase 10.6 C2: Per-character voice mode coverage invariants.

Asserts each character's rich YAML carries ≥ N distinct VoiceMode
values across `voice.few_shots.examples[].mode`, matching the Phase E
coverage commitment:

- Adelia: ≥6 modes including `silent`
- Bina: ≥5 modes
- Reina: ≥7 modes including escalation-level
- Alicia: ≥6 modes including `warm_refusal` + `group_temperature`

Per ``Docs/_phases/PHASE_10.md §Phase 10.6`` spec §2.
"""

from __future__ import annotations

import contextlib

from starry_lyfe.canon.rich_loader import load_rich_character
from starry_lyfe.context.types import VoiceMode


def _distinct_modes(character_id: str) -> set[VoiceMode]:
    rc = load_rich_character(character_id)
    fs = rc.voice.few_shots
    modes: set[VoiceMode] = set()
    if fs is None or not fs.examples:
        return modes
    for raw in fs.examples:
        if not isinstance(raw, dict):
            continue
        mode_str = str(raw.get("mode", ""))
        for m in mode_str.split(","):
            m = m.strip()
            if m:
                with contextlib.suppress(ValueError):
                    modes.add(VoiceMode(m))
    return modes


class TestVoiceModeCoverage:
    """AC-10.x: per-character voice mode counts hit Phase E floor."""

    def test_adelia_has_at_least_six_modes(self) -> None:
        modes = _distinct_modes("adelia")
        assert len(modes) >= 6, f"Adelia has {len(modes)} modes: {sorted(m.value for m in modes)}"

    def test_bina_has_at_least_five_modes(self) -> None:
        modes = _distinct_modes("bina")
        assert len(modes) >= 5, f"Bina has {len(modes)} modes: {sorted(m.value for m in modes)}"

    def test_reina_has_at_least_seven_modes(self) -> None:
        modes = _distinct_modes("reina")
        assert len(modes) >= 7, f"Reina has {len(modes)} modes: {sorted(m.value for m in modes)}"

    def test_alicia_has_at_least_six_modes(self) -> None:
        modes = _distinct_modes("alicia")
        assert len(modes) >= 6, f"Alicia has {len(modes)} modes: {sorted(m.value for m in modes)}"


class TestVoiceModeRequiredKeys:
    """Spec-required specific mode names per character (Phase 10.6 §2).

    Phase 10.6 closeout F3 (2026-04-17): converted from `pytest.skip(...)`
    to hard assertions. The Phase 10.6 spec explicitly requires these
    modes; the previous skip pattern silently passed when authoring was
    incomplete, masking real coverage gaps. The assertions now enforce
    the spec contract — if a required mode is removed from a rich YAML,
    the test fails loudly instead of skipping.
    """

    def test_adelia_has_silent_mode(self) -> None:
        modes = _distinct_modes("adelia")
        assert any("silent" in m.value for m in modes), (
            f"Adelia rich YAML missing required `silent` voice mode "
            f"(Phase 10.6 §2 + Phase E coverage commitment). "
            f"Present modes: {sorted(m.value for m in modes)}"
        )

    def test_alicia_has_warm_refusal_and_group_temperature(self) -> None:
        modes = _distinct_modes("alicia")
        mode_values = {m.value for m in modes}
        has_warm_refusal = any("refusal" in v for v in mode_values)
        has_group_temperature = any("group_temperature" in v for v in mode_values)
        assert has_warm_refusal, (
            f"Alicia rich YAML missing required `warm_refusal` voice mode "
            f"(Phase 10.6 §2). Present: {sorted(mode_values)}"
        )
        assert has_group_temperature, (
            f"Alicia rich YAML missing required `group_temperature` voice mode "
            f"(Phase 10.6 §2). Present: {sorted(mode_values)}"
        )

    def test_reina_has_escalation_mode(self) -> None:
        modes = _distinct_modes("reina")
        assert any("escal" in m.value for m in modes), (
            f"Reina rich YAML missing required escalation-level voice mode "
            f"(Phase 10.6 §2 + Phase E coverage commitment). "
            f"Present modes: {sorted(m.value for m in modes)}"
        )
