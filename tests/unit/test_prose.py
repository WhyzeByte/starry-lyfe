"""Phase G: Dramaturgical prose renderer tests.

Tests the per-character prose module (prose.py) and verifies that
Layers 2, 4, and 6 now render character-voiced narrative rather than
flat data blocks.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from starry_lyfe.context.prose import (
    render_canon_prose,
    render_dyad_internal_prose,
    render_dyad_whyze_prose,
    render_protocol_prose,
    render_somatic_prose,
)

# ---------------------------------------------------------------------------
# Helpers: minimal mock DB models
# ---------------------------------------------------------------------------


def _whyze_dyad(
    pair_name: str = "entangled",
    trust: float = 0.85,
    intimacy: float = 0.80,
    conflict: float = 0.05,
    tension: float = 0.08,
) -> MagicMock:
    d = MagicMock()
    d.pair_name = pair_name
    d.trust = trust
    d.intimacy = intimacy
    d.conflict = conflict
    d.unresolved_tension = tension
    return d


def _internal_dyad(
    member_a: str = "bina",
    member_b: str = "reina",
    interlock: str = "Shield Wall",
    trust: float = 0.88,
    intimacy: float = 0.85,
    conflict: float = 0.04,
) -> MagicMock:
    d = MagicMock()
    d.member_a = member_a
    d.member_b = member_b
    d.interlock = interlock
    d.trust = trust
    d.intimacy = intimacy
    d.conflict = conflict
    return d


def _somatic(
    character_id: str = "bina",
    fatigue: float = 0.82,
    stress: float = 0.20,
    injury: float = 0.00,
    active_protocols: list[str] | None = None,
) -> MagicMock:
    s = MagicMock()
    s.character_id = character_id
    s.fatigue = fatigue
    s.stress_residue = stress
    s.injury_residue = injury
    s.active_protocols = active_protocols or []
    return s


def _canon_facts(*pairs: tuple[str, str]) -> list[MagicMock]:
    facts = []
    for key, val in pairs:
        f = MagicMock()
        f.fact_key = key
        f.fact_value = val
        facts.append(f)
    return facts

# ---------------------------------------------------------------------------
# G1: Same canonical dyad state renders as four distinct prose strings
# ---------------------------------------------------------------------------


def test_g1_dyad_prose_is_distinct_across_characters() -> None:
    """G1: same trust/intimacy values produce four different prose strings."""
    dyad = _whyze_dyad(trust=0.85, intimacy=0.82)
    results = {char: render_dyad_whyze_prose(char, dyad) for char in ("adelia", "bina", "reina", "alicia")}
    # All four must differ
    assert len(set(results.values())) == 4


def test_g1_dyad_prose_contains_numeric_block() -> None:
    """G1: all dyad prose outputs contain the parenthesized numeric block."""
    dyad = _whyze_dyad(trust=0.85, intimacy=0.82, conflict=0.06, tension=0.10)
    for char in ("adelia", "bina", "reina", "alicia"):
        out = render_dyad_whyze_prose(char, dyad)
        assert "(trust=" in out
        assert "intimacy=" in out
        assert "conflict=" in out


# ---------------------------------------------------------------------------
# G2: Per-character somatic prose contains canonical phrases
# ---------------------------------------------------------------------------


def test_g2_bina_high_fatigue_contains_grid_phrase() -> None:
    """G2: Bina's somatic prose for fatigue>0.7 contains the canonical grid phrase."""
    state = _somatic("bina", fatigue=0.82)
    out = render_somatic_prose("bina", state)
    assert "grid" in out.lower()


def test_g2_adelia_high_fatigue_contains_chemistry_phrase() -> None:
    """G2: Adelia's somatic prose for fatigue>0.7 contains chemistry/backup language."""
    state = _somatic("adelia", fatigue=0.75)
    out = render_somatic_prose("adelia", state)
    assert "chemistry" in out.lower() or "backup" in out.lower()


def test_g2_reina_high_fatigue_contains_admissibility_phrase() -> None:
    """G2: Reina's somatic prose for fatigue>0.7 references admissibility gate."""
    state = _somatic("reina", fatigue=0.80)
    out = render_somatic_prose("reina", state)
    assert "admissibility" in out.lower() or "spent" in out.lower()


def test_g2_alicia_high_fatigue_contains_ni_grip_phrase() -> None:
    """G2: Alicia's somatic prose for fatigue>0.7 references Ni-grip."""
    state = _somatic("alicia", fatigue=0.78)
    out = render_somatic_prose("alicia", state)
    assert "ni-grip" in out.lower() or "words have stopped" in out.lower()


def test_g2_somatic_prose_contains_numeric_block() -> None:
    """G2: somatic prose always has the parenthesized numeric block."""
    state = _somatic("bina", fatigue=0.50, stress=0.25, injury=0.00)
    out = render_somatic_prose("bina", state)
    assert "(fatigue=" in out
    assert "stress=" in out
    assert "injury=" in out


# ---------------------------------------------------------------------------
# G3: Layer 6 has both prose block and numeric block
# ---------------------------------------------------------------------------


def test_g3_dyad_whyze_prose_has_bracketed_and_numeric() -> None:
    """G3: rendered Whyze dyad block has bracketed prose AND numeric."""
    dyad = _whyze_dyad()
    out = render_dyad_whyze_prose("bina", dyad)
    assert out.startswith("[")
    assert "]\n(" in out or "]\n(" in out.replace("\r\n", "\n")


def test_g3_dyad_internal_prose_has_bracketed_and_numeric() -> None:
    """G3: rendered internal dyad block has bracketed prose AND numeric."""
    dyad = _internal_dyad()
    out = render_dyad_internal_prose("bina", dyad)
    assert out.startswith("[")
    assert "(trust=" in out


# ---------------------------------------------------------------------------
# G4: Canon facts render as narrative paragraph
# ---------------------------------------------------------------------------


def test_g4_canon_prose_is_narrative_not_json_blob() -> None:
    """G4: canon facts render as a readable narrative, not a flat-list blob."""
    facts = _canon_facts(
        ("full_name", "Bina Malek"),
        ("epithet", "The Sentinel"),
        ("mbti", "ISFJ-A"),
        ("dominant_function", "Si"),
        ("heritage", "Assyrian-Iranian Canadian"),
        ("birthplace", "Urmia, Iran"),
        ("profession", "Red Seal mechanic"),
        ("pair_name", "circuit"),
    )
    out = render_canon_prose("bina", facts)
    # Must NOT look like a flat key-value list
    assert "fact_key" not in out
    assert "- full_name:" not in out
    # Must contain name and pair
    assert "Bina Malek" in out
    assert "Circuit Pair" in out
    assert "ISFJ-A" in out


def test_g4_canon_prose_four_characters_all_distinct() -> None:
    """G4: four characters produce distinct canonical narrative paragraphs."""
    results = {}
    for char, full_name, mbti, pair in [
        ("adelia", "Adelia Raye", "ENFP-A", "entangled"),
        ("bina", "Bina Malek", "ISFJ-A", "circuit"),
        ("reina", "Reina Torres", "ESTP-A", "kinetic"),
        ("alicia", "Alicia Marin", "ESFP-A", "solstice"),
    ]:
        facts = _canon_facts(
            ("full_name", full_name),
            ("mbti", mbti),
            ("pair_name", pair),
        )
        results[char] = render_canon_prose(char, facts)
    assert len(set(results.values())) == 4


# ---------------------------------------------------------------------------
# Protocol prose
# ---------------------------------------------------------------------------


def test_protocol_prose_bina_flat_state() -> None:
    """Flat State renders Bina's canonical voiced text."""
    out = render_protocol_prose("bina", "flat_state")
    assert out is not None
    assert "Flat State" in out
    assert "syllables" in out.lower() or "touch" in out.lower()


def test_protocol_prose_reina_post_race_crash() -> None:
    out = render_protocol_prose("reina", "post_race_crash")
    assert out is not None
    assert "adrenaline" in out.lower()


def test_protocol_prose_alicia_four_phase_return() -> None:
    out = render_protocol_prose("alicia", "four_phase_return")
    assert out is not None
    assert "returning" in out.lower() or "operation" in out.lower()


def test_protocol_prose_adelia_whiteboard_mode() -> None:
    out = render_protocol_prose("adelia", "whiteboard_mode")
    assert out is not None
    assert "cascade" in out.lower() or "marker" in out.lower()


def test_protocol_prose_unknown_returns_none() -> None:
    assert render_protocol_prose("bina", "nonexistent_protocol") is None


# ---------------------------------------------------------------------------
# Reina + Alicia non-redundancy (trust-prose level)
# ---------------------------------------------------------------------------


def test_reina_and_alicia_trust_prose_are_distinct() -> None:
    """The two Se-dominants use distinct trust registers — not interchangeable."""
    dyad = _whyze_dyad(trust=0.85)
    reina_out = render_dyad_whyze_prose("reina", dyad)
    alicia_out = render_dyad_whyze_prose("alicia", dyad)
    assert reina_out != alicia_out
    # Reina should have admissibility language
    assert "admissible" in reina_out.lower()
    # Alicia should have body/somatic language
    assert "body" in alicia_out.lower()
