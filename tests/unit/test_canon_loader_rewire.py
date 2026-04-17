"""Phase 10.5c C2 — narrow canon loader rewire tests.

Two enforcement surfaces:

1. **Path-guard** (AC-10.5c.2): ``load_all_canon()`` must NOT open any of
   the legacy narrow YAML files. After C3 archive these YAMLs are gone
   entirely; before C3 the path-guard catches accidental re-import.

2. **Drift-review** (AC-10.5c.4 amended): per-object diff between
   pre-rewire fixtures (captured in C2.1) and post-rewire output.
   Every diff line must be in ``EXPECTED_DRIFT_RATIONALIZATIONS`` —
   the allowlist is the human-reviewed surface where Project Owner
   ratifies each intentional rationalization toward single-source-of-truth.
   Unexpected drift is either a hydration bug (fix in ``_build_*``) or
   a missed rich-YAML authoring (fix in YAML).
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any

import pytest

from starry_lyfe.canon import loader as canon_loader
from starry_lyfe.canon.loader import load_all_canon

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "phase_10_5c_pre_rewire"
FIXTURE_SNAPSHOT_DATE = datetime.date(2026, 4, 16)
NARROW_YAMLS = (
    "characters.yaml",
    "pairs.yaml",
    "dyads.yaml",
    "protocols.yaml",
    "interlocks.yaml",
    "voice_parameters.yaml",
    "routines.yaml",
)


# ----------------------------------------------------------------------
# C2.3 — path-guard test
# ----------------------------------------------------------------------


def _is_forbidden_open(path_str: str) -> bool:
    """Return True if ``path_str`` points at a legacy narrow canon YAML."""
    norm = path_str.replace(os.sep, "/")
    return any(f"/canon/{name}" in norm for name in NARROW_YAMLS)


def test_load_all_canon_does_not_read_narrow_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 10.5c AC-10.5c.2: load_all_canon() opens zero narrow canon YAMLs.

    Patches both Path.read_text (used by rich_loader._load_yaml_file) and
    Path.open (the original loader._load_yaml mechanism) to track every
    file opened during a full ``load_all_canon()`` call. Asserts none of
    them point at the archived narrow canon YAML filenames.
    """
    opens: list[str] = []
    real_read_text = Path.read_text
    real_open = Path.open

    def tracking_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        opens.append(str(self))
        return real_read_text(self, *args, **kwargs)

    def tracking_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        opens.append(str(self))
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", tracking_read_text, raising=False)
    monkeypatch.setattr(Path, "open", tracking_open, raising=False)

    load_all_canon(validate_on_load=False)

    narrow_opens = sorted({p for p in opens if _is_forbidden_open(p)})
    assert not narrow_opens, (
        "Phase 10.5c regression: load_all_canon() opened legacy narrow canon YAML(s):\n  "
        + "\n  ".join(narrow_opens)
    )


# ----------------------------------------------------------------------
# C2.4 — drift-review test
# ----------------------------------------------------------------------


# Each entry is a path-prefix the diff line must START with to be allowed.
# Liberal matching is intentional: the goal is to catch UNEXPECTED drift,
# not police the format of expected diffs. Project Owner ratified each
# rationalization 2026-04-16 (recorded in PHASE_10.md §Phase 10.5c C1
# Execution Record + PHASE_10_5c_MAPPING.md R1 §2 + §6.2).
EXPECTED_DRIFT_RATIONALIZATIONS: dict[str, list[str]] = {
    # Path prefixes use the FULL nested path including the wrapping
    # object key (e.g. "voice_parameters.voice_parameters.bina.X"
    # because the root has a `voice_parameters` key containing the dict).
    #
    # Voice temperatures aligned to CLAUDE.md §16 axioms (Bina 0.58, Reina 0.72, Alicia 0.75).
    # Plus thinking_effort + top_p + response_length corrections per same source.
    "voice_parameters": [
        "voice_parameters.voice_parameters.bina.temperature",
        "voice_parameters.voice_parameters.bina.thinking_effort",
        "voice_parameters.voice_parameters.reina.temperature",
        "voice_parameters.voice_parameters.reina.top_p",
        "voice_parameters.voice_parameters.reina.thinking_effort",
        "voice_parameters.voice_parameters.reina.response_length",
        "voice_parameters.voice_parameters.alicia.temperature",
        "voice_parameters.voice_parameters.alicia.top_p",
        "voice_parameters.voice_parameters.alicia.thinking_effort",
    ],
    # Pair classifications/mechanisms migrated to shared_canon.pairs[] strings
    # (Phase 10.5b R2-F3 made shared_canon the Layer 5 anchor; C1.4 §2.5 extended
    # to narrow Pair hydration).
    "pairs": [
        "pairs.pairs.entangled.classification",
        "pairs.pairs.entangled.mechanism",
        "pairs.pairs.circuit.classification",
        "pairs.pairs.circuit.mechanism",
        "pairs.pairs.kinetic.classification",
        "pairs.pairs.kinetic.mechanism",
        "pairs.pairs.solstice.classification",
        "pairs.pairs.solstice.mechanism",
    ],
    "characters": [
        # Astrology surfaces from rich for women whose narrow had null
        # (Bina was authoring oversight; Reina/Alicia same pattern — rich layers.astrology
        # had the values, narrow had null. C1.4 promoted to identity.astrology.)
        "characters.characters.bina.astrology",
        "characters.characters.reina.astrology",
        "characters.characters.alicia.astrology",
        # Bina birthdate (canonical-constraint inference 1985-12-27, Project Owner ratified)
        "characters.characters.bina.birthdate",
        # Children gain birthdate (Project Owner directive 2026-04-16)
        "characters.characters.bina.children[0].birthdate",
        "characters.operator.whyze.children[0].birthdate",
        "characters.operator.whyze.children[1].birthdate",
        # Shawn full_name + disc: rich (longer/fuller form) preserved over narrow per §2
        "characters.operator.whyze.full_name",
        "characters.operator.whyze.disc",
        # Rich identity has fuller raised_in / current_residence strings
        # (e.g., "Marrickville, Inner West, Sydney, Australia" vs narrow "Marrickville, Sydney, Australia";
        # Bina rich "Loft above Loth Wolf Hypersport on the Foothills County property, Alberta, Canada"
        # vs narrow "Foothills County, Alberta"; Reina rich "Gracia, Barcelona, in a flat above Rafael's bar
        # near Placa de la Virreina" vs narrow "Gracia, Barcelona"). Per single-source: rich wins.
        "characters.characters.adelia.raised_in",
        "characters.characters.bina.raised_in",
        "characters.characters.reina.raised_in",
        "characters.characters.adelia.current_residence",
        "characters.characters.bina.current_residence",
        "characters.characters.reina.current_residence",
        "characters.characters.alicia.current_residence",
        # Alicia parent origins gain ", Argentina" suffix in rich
        "characters.characters.alicia.parents.father.origin",
        "characters.characters.alicia.parents.mother.origin",
    ],
    # No drift expected for these — verbatim lifts from narrow → rich/shared_canon.
    "dyads": [],
    "protocols": [],
    "interlocks": [],
    "routines": [],
}


def _matches_expected(diff_path: str, allowlist: list[str]) -> bool:
    """Return True if the diff path starts with any allowlist prefix."""
    return any(diff_path.startswith(prefix) for prefix in allowlist)


def _compute_field_diffs(
    expected: object,
    actual: object,
    path: str = "",
) -> list[str]:
    """Recursive deep-diff producing human-readable path-prefixed change strings."""
    diffs: list[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        all_keys = set(expected.keys()) | set(actual.keys())
        for k in sorted(all_keys):
            sub_path = f"{path}.{k}" if path else k
            if k not in expected:
                diffs.append(f"{sub_path}: <missing> -> {actual[k]!r}")
            elif k not in actual:
                diffs.append(f"{sub_path}: {expected[k]!r} -> <missing>")
            else:
                diffs.extend(_compute_field_diffs(expected[k], actual[k], sub_path))
    elif isinstance(expected, list) and isinstance(actual, list):
        for i in range(max(len(expected), len(actual))):
            sub_path = f"{path}[{i}]"
            if i >= len(expected):
                diffs.append(f"{sub_path}: <missing> -> {actual[i]!r}")
            elif i >= len(actual):
                diffs.append(f"{sub_path}: {expected[i]!r} -> <missing>")
            else:
                diffs.extend(_compute_field_diffs(expected[i], actual[i], sub_path))
    elif expected != actual:
        diffs.append(f"{path}: {expected!r} -> {actual!r}")
    return diffs


def test_compute_age_from_birthdate_is_deterministic_with_explicit_today() -> None:
    """Birthdate-derived ages must be stable when tests pin the reference date."""
    assert canon_loader.compute_age_from_birthdate(
        "1992-04-27",
        today=datetime.date(2026, 4, 26),
    ) == 33
    assert canon_loader.compute_age_from_birthdate(
        "1992-04-27",
        today=datetime.date(2026, 4, 27),
    ) == 34


def test_canon_drift_against_pre_rewire(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 10.5c AC-10.5c.4 (amended): every diff is in the allowlist.

    Reframed from bit-identical preservation (R0) to drift-review
    rationalization (R1, ratified 2026-04-16). Each diff line is either
    (a) in EXPECTED_DRIFT_RATIONALIZATIONS — Project Owner ratified
    rationalization toward single-source-of-truth — or (b) an unintended
    hydration bug / missed authoring that the test surfaces here.

    The pre-rewire fixtures were captured on 2026-04-16, so the comparison
    pins age derivation to that same snapshot date. Live runtime hydration
    still uses today's date; only the fixture-review gate is time-stabilized.
    """
    real_compute_age = canon_loader.compute_age_from_birthdate

    def pinned_compute_age(birthdate: str, *, today: datetime.date | None = None) -> int:
        del today
        return real_compute_age(birthdate, today=FIXTURE_SNAPSHOT_DATE)

    monkeypatch.setattr(canon_loader, "compute_age_from_birthdate", pinned_compute_age)

    canon = load_all_canon(validate_on_load=False)
    objs: dict[str, object] = {
        "characters": canon.characters,
        "pairs": canon.pairs,
        "dyads": canon.dyads,
        "protocols": canon.protocols,
        "interlocks": canon.interlocks,
        "voice_parameters": canon.voice_parameters,
        "routines": canon.routines,
    }
    unexpected_drifts: dict[str, list[str]] = {}

    for obj_name, obj in objs.items():
        actual_json = obj.model_dump_json(indent=2)  # type: ignore[attr-defined]
        actual = json.loads(actual_json)
        # Re-canonicalize (sort_keys) to match the fixture format.
        actual_canonical = json.loads(
            json.dumps(actual, indent=2, sort_keys=True, ensure_ascii=False)
        )
        expected = json.loads((FIXTURE_DIR / f"{obj_name}.json").read_text(encoding="utf-8"))

        diffs = _compute_field_diffs(expected, actual_canonical, path=obj_name)
        unexpected = [
            d for d in diffs
            if not _matches_expected(d.split(":")[0], EXPECTED_DRIFT_RATIONALIZATIONS.get(obj_name, []))
        ]
        if unexpected:
            unexpected_drifts[obj_name] = unexpected

    if unexpected_drifts:
        report_lines: list[str] = ["Unexpected drift detected (not in EXPECTED_DRIFT_RATIONALIZATIONS):"]
        for obj_name, diffs in unexpected_drifts.items():
            report_lines.append(f"  {obj_name}:")
            for d in diffs:
                report_lines.append(f"    - {d}")
        pytest.fail("\n".join(report_lines))
