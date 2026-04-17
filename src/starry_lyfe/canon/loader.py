"""Load and validate canon through Pydantic schemas.

Phase 10.5c (2026-04-16): ``load_all_canon()`` now constructs the 7 narrow
Pydantic objects from rich per-character YAMLs + ``shared_canon.yaml`` in
memory. Zero runtime reads of the legacy narrow canon YAML files
(archived in C3). The 7 narrow Pydantic schemas in
``schemas/`` keep their shape exactly — only the hydration source changes.
Per the single-source-of-truth principle ratified by Project Owner
2026-04-16: every narrow field maps to ONE authoritative rich location.

Drift between the prior narrow YAML state and the post-rewire output is
not a bug — it's intentional rationalization toward the authoritative
rich source. The drift-review test at
``tests/unit/test_canon_loader_rewire.py`` carries an
``EXPECTED_DRIFT_RATIONALIZATIONS`` allowlist documenting each rationalized
diff (voice temperature axioms per CLAUDE.md §16, diacritics restored,
Bina astrology surfaced, pair classifications migrated to shared_canon, etc.).
"""

from __future__ import annotations

import datetime
import logging
import time
from dataclasses import dataclass
from typing import cast

from .rich_loader import load_all_rich_characters, load_shared_canon
from .rich_schema import RichCharacter
from .schemas import (
    CanonCharacters,
    CanonDyads,
    CanonInterlocks,
    CanonPairs,
    CanonProtocols,
    CanonRoutines,
    CanonVoiceParameters,
)
from .shared_schema import SharedCanon

logger = logging.getLogger(__name__)

NARROW_VERSION = "7.1"


@dataclass(frozen=True)
class Canon:
    """Complete validated canon state."""

    characters: CanonCharacters
    pairs: CanonPairs
    dyads: CanonDyads
    protocols: CanonProtocols
    interlocks: CanonInterlocks
    voice_parameters: CanonVoiceParameters
    routines: CanonRoutines


class CanonValidationError(ValueError):
    """Raised when ``load_all_canon(validate_on_load=True)`` finds cross-reference errors.

    Per REMEDIATION_2026-04-13.md R-1.3: invalid canon must fail loud at
    startup, not silently at inference. The error carries the full list
    of errors for structured handling.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = list(errors)
        super().__init__(self.format_errors())

    def format_errors(self) -> str:
        """Human-readable multiline error report."""
        return "Canon validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)


def compute_age_from_birthdate(birthdate: str, *, today: datetime.date | None = None) -> int:
    """Compute current age in years from an ISO ``birthdate`` string.

    Phase 10.5c: birthdate is the durable source of truth so ages do not
    stagnate. Hydration prefers ``birthdate`` over authored ``age``; this
    helper does the date math. Optional ``today`` parameter allows
    deterministic test fixtures to pin a reference date.
    """
    bd = datetime.date.fromisoformat(birthdate)
    ref = today if today is not None else datetime.date.today()
    years = ref.year - bd.year - ((ref.month, ref.day) < (bd.month, bd.day))
    return years


def _identity(rc: RichCharacter) -> dict[str, object]:
    """Type-narrowing helper: identity is permissive ``dict[str, object]``."""
    return rc.identity


def _str_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _build_character_entry(rc: RichCharacter) -> dict[str, object]:
    """Build a single narrow ``Character`` dict from a woman's rich YAML."""
    ident = _identity(rc)
    heritage_block = cast(dict[str, object], ident["heritage"])
    profession_block = cast(dict[str, object], ident["profession"])
    business_block = cast("dict[str, object] | None", ident.get("business"))
    languages_block = cast(dict[str, object], ident["languages"])
    parents_block = cast(dict[str, object], ident["parents"])

    # Rich parents nest narrow_profession alongside the prose `profession`; use narrow form.
    parents_out: dict[str, dict[str, str]] = {}
    for parent_key, parent_data in parents_block.items():
        pdict = cast(dict[str, object], parent_data)
        parents_out[parent_key] = {
            "name": str(pdict["name"]),
            "origin": str(pdict["origin"]),
            "profession": str(pdict.get("narrow_profession", pdict["profession"])),
        }

    children_in = cast("list[dict[str, object]]", ident.get("children", []))
    children_out: list[dict[str, object]] = []
    for child in children_in:
        ce: dict[str, object] = {
            "name": str(child["name"]),
            "relationship": str(child["relationship"]),
        }
        if "birthdate" in child and child["birthdate"]:
            ce["birthdate"] = str(child["birthdate"])
            ce["age"] = compute_age_from_birthdate(str(child["birthdate"]))
        else:
            ce["age"] = int(cast(int, child["age"]))
        children_out.append(ce)

    # Birthdate-derived age (or fall back to authored age if birthdate absent).
    birthdate = _str_or_none(ident.get("birthdate"))
    age = compute_age_from_birthdate(birthdate) if birthdate else int(cast(int, ident["age"]))

    epithet = getattr(rc.meta, "epithet", None) or cast(
        dict[str, object], rc.meta.model_dump()
    ).get("epithet", "")
    out: dict[str, object] = {
        "full_name": rc.meta.full_name,
        "role": "character",
        "epithet": str(epithet),
        "age": age,
        "birthdate": birthdate,
        "mbti": str(ident["mbti"]),
        "heritage": str(heritage_block["canonical_label"]),
        "birthplace": str(ident["birthplace"]),
        "raised_in": str(ident["raised_in"]),
        "current_residence": str(ident["current_residence"]),
        "is_resident": bool(ident["is_resident"]),
        "operational_travel": _str_or_none(ident.get("operational_travel")),
        "pair_name": str(ident["pair_name"]),
        "profession": str(profession_block["canonical_label"]),
        "business": str(business_block["canonical_label"]) if business_block else None,
        "employer": _str_or_none(ident.get("employer")),
        "unit": _str_or_none(ident.get("unit")),
        "languages": list(cast(list[object], languages_block["canonical_list"])),
        "parents": parents_out,
        "children": children_out,
        "cognitive_function_stack": list(cast(list[str], ident["cognitive_function_stack"])),
        "dominant_function": str(ident["dominant_function"]),
        "spouse": _str_or_none(ident.get("spouse")),
        "family_notes": ident.get("family_notes"),
        "siblings": ident.get("siblings_narrow_list"),
        "astrology": ident.get("astrology"),
    }
    return out


def _build_operator_entry(rc_shawn: RichCharacter) -> dict[str, object]:
    """Build the single narrow ``Operator`` dict from Shawn's rich YAML."""
    ident = _identity(rc_shawn)
    neurotype = cast("dict[str, object] | None", ident.get("neurotype"))
    clinical_block = cast("dict[str, object] | None",
                          neurotype.get("narrow_clinical") if neurotype else None)

    children_in = cast("list[dict[str, object]]", ident.get("children", []))
    children_out: list[dict[str, object]] = []
    for child in children_in:
        ce: dict[str, object] = {
            "name": str(child["name"]),
            "relationship": str(child["relationship"]),
        }
        if "birthdate" in child and child["birthdate"]:
            ce["birthdate"] = str(child["birthdate"])
            ce["age"] = compute_age_from_birthdate(str(child["birthdate"]))
        else:
            ce["age"] = int(cast(int, child["age"]))
        children_out.append(ce)

    birthdate = _str_or_none(ident.get("birthdate"))
    age = compute_age_from_birthdate(birthdate) if birthdate else int(cast(int, ident["age"]))

    return {
        "full_name": rc_shawn.meta.full_name,
        "handle": str(ident["runtime_alias"]),
        "role": "operator",
        "age": age,
        "mbti": str(ident["mbti"]),
        "cognitive_function_stack": list(cast(list[str], ident["cognitive_function_stack"])),
        "dominant_function": str(ident["dominant_function"]),
        "clinical": clinical_block,
        "disc": _str_or_none(ident.get("disc")),
        "astrology": ident.get("astrology"),
        "children": children_out,
        "profile_file": str(ident["profile_file"]),
        "profile_version": str(ident["profile_version"]),
    }


def _build_characters(
    rich_chars: dict[str, RichCharacter],
    _shared: SharedCanon,
) -> CanonCharacters:
    """Build narrow ``CanonCharacters`` from rich character YAMLs."""
    women = ("adelia", "bina", "reina", "alicia")
    chars_out = {wid: _build_character_entry(rich_chars[wid]) for wid in women}
    operator_out = {"whyze": _build_operator_entry(rich_chars["shawn"])}
    return CanonCharacters.model_validate({
        "version": NARROW_VERSION,
        "characters": chars_out,
        "operator": operator_out,
    })


def _build_pairs(shared: SharedCanon) -> CanonPairs:
    """Build narrow ``CanonPairs`` from ``shared_canon.pairs[]`` (single source per §2.5)."""
    if shared.pairs is None:
        msg = "shared_canon.pairs is missing — required for narrow CanonPairs hydration"
        raise CanonValidationError([msg])

    # Map canonical_name → narrow PairName enum key.
    name_to_key = {
        "The Entangled Pair": "entangled",
        "The Circuit Pair": "circuit",
        "The Kinetic Pair": "kinetic",
        "The Solstice Pair": "solstice",
    }

    pairs_out: dict[str, dict[str, object]] = {}
    for sp in shared.pairs:
        key = name_to_key.get(sp.canonical_name)
        if key is None:
            msg = f"Unknown shared_canon pair canonical_name: {sp.canonical_name!r}"
            raise CanonValidationError([msg])
        pairs_out[key] = {
            "character": str(sp.character) if sp.character else "",
            "full_name": sp.canonical_name,
            "classification": sp.classification or "",
            "shared_functions": sp.shared_functions or "",
            "mechanism": sp.mechanism or "",
            "what_she_provides": sp.what_she_provides or "",
            "how_she_breaks_spiral": sp.how_she_breaks_spiral or "",
            "core_metaphor": sp.core_metaphor or "",
            "cadence": sp.cadence or "continuous",
        }
    return CanonPairs.model_validate({"version": NARROW_VERSION, "pairs": pairs_out})


def _build_dyads(shared: SharedCanon) -> CanonDyads:
    """Build narrow ``CanonDyads`` from ``shared_canon.dyads_baseline`` + ``memory_tiers``."""
    if shared.dyads_baseline is None:
        raise CanonValidationError(["shared_canon.dyads_baseline missing"])
    if shared.memory_tiers is None:
        raise CanonValidationError(["shared_canon.memory_tiers missing"])

    dyads_out: dict[str, dict[str, object]] = {}
    for key, db in shared.dyads_baseline.items():
        dyads_out[key] = {
            "members": list(db.members),
            "type": db.type,
            "subtype": db.subtype,
            "interlock": db.interlock,
            "pair": db.pair,
            "is_currently_active": db.is_currently_active,
            "dimensions": db.dimensions.model_dump(),
        }

    tiers_out = [
        {
            "name": mt.name,
            "tier": mt.tier,
            "mutable": mt.mutable,
            "description": mt.description,
        }
        for mt in shared.memory_tiers
    ]

    return CanonDyads.model_validate({
        "version": NARROW_VERSION,
        "dyads": dyads_out,
        "memory_tiers": tiers_out,
    })


def _build_protocols(rich_chars: dict[str, RichCharacter]) -> CanonProtocols:
    """Aggregate per-character ``behavioral_framework.state_protocols`` into narrow CanonProtocols."""
    aggregated: dict[str, dict[str, object]] = {}
    for char_id, rc in rich_chars.items():
        bf = cast("dict[str, object] | None", rc.behavioral_framework)
        if bf is None:
            continue
        sp_block = cast("dict[str, dict[str, object]] | None", bf.get("state_protocols"))
        if sp_block is None:
            continue
        for proto_key, proto_data in sp_block.items():
            if proto_key in aggregated:
                msg = (
                    f"Duplicate protocol key {proto_key!r} — first defined in "
                    f"a prior character file, redefined in {char_id}"
                )
                raise CanonValidationError([msg])
            aggregated[proto_key] = dict(proto_data)

    return CanonProtocols.model_validate({
        "version": NARROW_VERSION,
        "protocols": aggregated,
    })


def _build_interlocks(shared: SharedCanon) -> CanonInterlocks:
    """Build narrow ``CanonInterlocks`` from ``shared_canon.interlocks``."""
    if shared.interlocks is None:
        raise CanonValidationError(["shared_canon.interlocks missing"])

    interlocks_out: dict[str, dict[str, object]] = {}
    for entry in shared.interlocks:
        interlocks_out[entry.key] = {
            "name": entry.name,
            "members": list(entry.members),
            "description": entry.description,
            "tone": entry.tone,
            "type": entry.type,
            "origin": entry.origin,
            "canonical_disagreement": entry.canonical_disagreement,
        }

    return CanonInterlocks.model_validate({
        "version": NARROW_VERSION,
        "interlocks": interlocks_out,
    })


def _build_voice_parameters(rich_chars: dict[str, RichCharacter]) -> CanonVoiceParameters:
    """Build narrow ``CanonVoiceParameters`` from each woman's ``voice.inference_parameters``."""
    women = ("adelia", "bina", "reina", "alicia")
    vp_out: dict[str, dict[str, object]] = {}
    for wid in women:
        rc = rich_chars[wid]
        voice_extra = rc.voice.model_dump()
        ip = cast("dict[str, object] | None", voice_extra.get("inference_parameters"))
        if ip is None:
            raise CanonValidationError([f"{wid}: voice.inference_parameters missing"])
        temp_range = cast("list[float]", ip["temperature_range"])
        vp_out[wid] = {
            "character": wid,
            "temperature": {
                "range": tuple(temp_range),
                "midpoint": float(cast(float, ip["temperature_midpoint"])),
            },
            "top_p": float(cast(float, ip["top_p"])),
            "thinking_effort": str(ip["thinking_effort"]),
            "distinctive_sampling": ip.get("distinctive_sampling"),
            "presence_penalty": float(cast(float, ip["presence_penalty"])),
            "frequency_penalty": float(cast(float, ip["frequency_penalty"])),
            "response_length": str(ip["response_length"]),
            "response_length_range": str(ip["response_length_range"]),
            "dominant_function_descriptor": str(ip["dominant_function_descriptor"]),
        }

    return CanonVoiceParameters.model_validate({
        "version": NARROW_VERSION,
        "voice_parameters": vp_out,
    })


def _build_routines(rich_chars: dict[str, RichCharacter]) -> CanonRoutines:
    """Build narrow ``CanonRoutines`` from each woman's ``runtime.routines``."""
    women = ("adelia", "bina", "reina", "alicia")
    routines_out: dict[str, dict[str, object]] = {}
    for wid in women:
        rc = rich_chars[wid]
        if rc.runtime is None or rc.runtime.routines is None:
            raise CanonValidationError([f"{wid}: runtime.routines missing"])
        rt = rc.runtime.routines
        routines_out[wid] = {
            "character": wid,
            "weekday": [b.model_dump() for b in rt.weekday],
            "weekend": [b.model_dump() for b in rt.weekend],
            "recurring_events": (
                [re.model_dump() for re in rt.recurring_events]
                if rt.recurring_events else []
            ),
        }

    alicia_rt = rich_chars["alicia"].runtime
    if alicia_rt is None or alicia_rt.alicia_communication_distribution is None:
        raise CanonValidationError(
            ["alicia: runtime.alicia_communication_distribution missing"]
        )
    acd = alicia_rt.alicia_communication_distribution

    return CanonRoutines.model_validate({
        "version": NARROW_VERSION,
        "routines": routines_out,
        "alicia_communication_distribution": {
            "phone": acd.phone,
            "letter": acd.letter,
            "video_call": acd.video_call,
        },
    })


def load_all_canon(validate_on_load: bool = True) -> Canon:
    """Load and validate the entire canon, sourced from rich YAML + shared_canon.

    Phase 10.5c rewire (2026-04-16): zero runtime reads of
    the archived narrow canon YAML files. The 7 narrow Pydantic objects
    hydrate from rich per-character YAMLs + ``Characters/shared_canon.yaml``
    via per-object ``_build_*`` helpers. The 7 narrow schemas in
    ``schemas/`` keep their shape — only their hydration source changes.

    When ``validate_on_load`` is True (default), cross-file referential
    integrity checks run via ``validator.validate_cross_references()``
    and any errors raise ``CanonValidationError``. Pass
    ``validate_on_load=False`` only for recursion-safe use inside the
    validator itself, or for test fixtures that deliberately construct
    broken canon.
    """
    start = time.perf_counter()
    rich_chars = load_all_rich_characters()
    shared = load_shared_canon()
    canon = Canon(
        characters=_build_characters(rich_chars, shared),
        pairs=_build_pairs(shared),
        dyads=_build_dyads(shared),
        protocols=_build_protocols(rich_chars),
        interlocks=_build_interlocks(shared),
        voice_parameters=_build_voice_parameters(rich_chars),
        routines=_build_routines(rich_chars),
    )
    if validate_on_load:
        from .validator import validate_cross_references
        errors = validate_cross_references(canon)
        if errors:
            raise CanonValidationError(errors)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        "load_all_canon completed in %.1fms (validate_on_load=%s, source=rich)",
        elapsed_ms,
        validate_on_load,
    )
    return canon
