"""Cross-file referential integrity validator for canon YAML.

Runnable as: python -m starry_lyfe.canon.validator
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .loader import load_all_canon
from .schemas.enums import CharacterID, PairName

if TYPE_CHECKING:
    from .loader import Canon


def validate_cross_references(canon: Canon | None = None) -> list[str]:
    """Run all cross-file validations. Returns a list of error messages (empty = pass).

    If ``canon`` is provided, validate that instance. If None, load a fresh
    canon without running validation (to avoid recursion when called from
    ``load_all_canon(validate=True)``).
    """
    errors: list[str] = []
    if canon is None:
        canon = load_all_canon(validate=False)

    # Build the set of valid character IDs and operator handles
    char_ids = {c.value for c in canon.characters.characters}
    operator_handles = {op.handle.lower() for op in canon.characters.operator.values()}
    all_people = char_ids | operator_handles

    # 1. Pair character references resolve to characters.yaml
    for pair_name, pair in canon.pairs.pairs.items():
        if pair.character.value not in char_ids:
            errors.append(f"pairs.yaml: pair '{pair_name}' references unknown character '{pair.character}'")

    # 2. Pair names in characters.yaml match pairs.yaml
    defined_pairs = {p.value for p in canon.pairs.pairs}
    for char_id, char in canon.characters.characters.items():
        if char.pair_name.value not in defined_pairs:
            errors.append(f"characters.yaml: character '{char_id}' has pair '{char.pair_name}' not in pairs.yaml")

    # 3. Dyad members resolve to known people
    for dyad_name, dyad in canon.dyads.dyads.items():
        for member in dyad.members:
            if member not in all_people:
                errors.append(f"dyads.yaml: dyad '{dyad_name}' references unknown member '{member}'")

    # 4. Protocol primary_character resolves
    for proto_name, proto in canon.protocols.protocols.items():
        if proto.primary_character not in all_people:
            errors.append(
                f"protocols.yaml: protocol '{proto_name}' references unknown character '{proto.primary_character}'"
            )
        for sec in proto.secondary_characters:
            if sec not in all_people:
                errors.append(f"protocols.yaml: protocol '{proto_name}' secondary '{sec}' unknown")

    # 5. Interlock members resolve to characters
    for ilock_name, ilock in canon.interlocks.interlocks.items():
        for member in ilock.members:
            if member not in char_ids:
                errors.append(f"interlocks.yaml: interlock '{ilock_name}' references unknown character '{member}'")

    # 6. Dyad interlock references resolve to interlocks.yaml keys
    interlock_keys = set(canon.interlocks.interlocks.keys())
    for dyad_name, dyad in canon.dyads.dyads.items():
        if dyad.interlock is not None and dyad.interlock not in interlock_keys:
            errors.append(f"dyads.yaml: dyad '{dyad_name}' interlock '{dyad.interlock}' not in interlocks.yaml")

    # 7. Whyze-pair dyad pair references resolve to pairs.yaml keys
    pair_keys = set(canon.pairs.pairs.keys())
    for dyad_name, dyad in canon.dyads.dyads.items():
        if dyad.pair is not None and dyad.pair.value not in pair_keys:
            errors.append(f"dyads.yaml: dyad '{dyad_name}' pair '{dyad.pair}' not in pairs.yaml")

    # 8. Protocol recovery_architecture characters resolve to known people
    for proto_name, proto in canon.protocols.protocols.items():
        if proto.recovery_architecture is not None:
            for role_name in ("first_responder", "second_responder", "third_responder"):
                role = getattr(proto.recovery_architecture, role_name)
                if role.character not in all_people:
                    errors.append(
                        f"protocols.yaml: protocol '{proto_name}' recovery {role_name} "
                        f"references unknown character '{role.character}'"
                    )

    # 9. Voice parameter keys match character IDs
    voice_ids = {vp.value for vp in canon.voice_parameters.voice_parameters}
    expected_ids = {c.value for c in CharacterID}
    if voice_ids != expected_ids:
        errors.append(f"voice_parameters.yaml: expected characters {sorted(expected_ids)}, got {sorted(voice_ids)}")

    # 10. Exact counts
    if len(canon.characters.characters) != 4:
        errors.append(f"Expected 4 characters, got {len(canon.characters.characters)}")
    if len(canon.characters.operator) != 1:
        errors.append(f"Expected 1 operator, got {len(canon.characters.operator)}")
    if len(canon.pairs.pairs) != 4:
        errors.append(f"Expected 4 pairs, got {len(canon.pairs.pairs)}")
    if len(canon.dyads.dyads) != 10:
        errors.append(f"Expected 10 dyads, got {len(canon.dyads.dyads)}")
    if len(canon.dyads.memory_tiers) != 7:
        errors.append(f"Expected 7 memory tiers, got {len(canon.dyads.memory_tiers)}")
    if len(canon.interlocks.interlocks) != 6:
        errors.append(f"Expected 6 interlocks, got {len(canon.interlocks.interlocks)}")

    # 11. All four pair names are present
    expected_pairs = {p.value for p in PairName}
    actual_pairs = set(canon.pairs.pairs.keys())
    if actual_pairs != expected_pairs:
        errors.append(f"Expected pairs {sorted(expected_pairs)}, got {sorted(actual_pairs)}")

    return errors


def main() -> None:
    """CLI entry point for canon validation."""
    print("Validating canon YAML...")
    try:
        errors = validate_cross_references()
    except Exception as e:
        print(f"FATAL: Canon loading failed: {e}")
        sys.exit(1)

    if errors:
        print(f"FAILED: {len(errors)} cross-reference error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASSED: All canon cross-references valid.")


if __name__ == "__main__":
    main()
