"""Load and validate canon YAML files through Pydantic schemas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from .schemas import (
    CanonCharacters,
    CanonDyads,
    CanonInterlocks,
    CanonPairs,
    CanonProtocols,
    CanonRoutines,
    CanonVoiceParameters,
)

T = TypeVar("T", bound=BaseModel)

CANON_DIR = Path(__file__).resolve().parent


def _load_yaml(filename: str) -> dict[str, object]:
    """Load a YAML file from the canon directory."""
    path = CANON_DIR / filename
    with path.open(encoding="utf-8") as f:
        data: dict[str, object] = yaml.safe_load(f)
    return data


def _parse(filename: str, model: type[T]) -> T:
    """Load a YAML file and parse through a Pydantic model."""
    data = _load_yaml(filename)
    return model.model_validate(data)


def load_characters() -> CanonCharacters:
    """Load and validate characters.yaml."""
    return _parse("characters.yaml", CanonCharacters)


def load_pairs() -> CanonPairs:
    """Load and validate pairs.yaml."""
    return _parse("pairs.yaml", CanonPairs)


def load_dyads() -> CanonDyads:
    """Load and validate dyads.yaml."""
    return _parse("dyads.yaml", CanonDyads)


def load_protocols() -> CanonProtocols:
    """Load and validate protocols.yaml."""
    return _parse("protocols.yaml", CanonProtocols)


def load_interlocks() -> CanonInterlocks:
    """Load and validate interlocks.yaml."""
    return _parse("interlocks.yaml", CanonInterlocks)


def load_voice_parameters() -> CanonVoiceParameters:
    """Load and validate voice_parameters.yaml."""
    return _parse("voice_parameters.yaml", CanonVoiceParameters)


def load_routines() -> CanonRoutines:
    """Load and validate routines.yaml (Phase 6 Dreams canonical source)."""
    return _parse("routines.yaml", CanonRoutines)


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


def load_all_canon(validate_on_load: bool = True) -> Canon:
    """Load and validate the entire canon directory. Fail-closed on any error.

    When ``validate_on_load`` is True (default), cross-file referential
    integrity checks run via ``validator.validate_cross_references()``
    and any errors raise ``CanonValidationError``. Pass
    ``validate_on_load=False`` only for recursion-safe use inside the
    validator itself, or for test fixtures that deliberately construct
    broken canon. (R-1.3 remediation.)
    """
    import time
    start = time.perf_counter()
    canon = Canon(
        characters=load_characters(),
        pairs=load_pairs(),
        dyads=load_dyads(),
        protocols=load_protocols(),
        interlocks=load_interlocks(),
        voice_parameters=load_voice_parameters(),
        routines=load_routines(),
    )
    if validate_on_load:
        from .validator import validate_cross_references
        errors = validate_cross_references(canon)
        if errors:
            raise CanonValidationError(errors)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    import logging
    logging.getLogger(__name__).info(
        "load_all_canon completed in %.1fms (validate_on_load=%s)",
        elapsed_ms,
        validate_on_load,
    )
    return canon
