# Reina Conversion Audit

## Scope

This audit reviews how Reina Torres is converted from markdown canon into the Phase 3 runtime prompt assembly path. The target is not schema correctness. The target is fidelity: whether the live system carries the parts of Reina that make her feel like Reina, in line with `Vision/Starry-Lyfe_Vision_v7.1.md` and her source markdowns.

Files reviewed:

- `Vision/Starry-Lyfe_Vision_v7.1.md`
- `Characters/Reina/Reina_Torres_v7.1.md`
- `Characters/Reina/Reina_Torres_Voice.md`
- `Characters/Reina/Reina_Torres_Kinetic_Pair.md`
- `src/starry_lyfe/context/kernel_loader.py`
- `src/starry_lyfe/context/layers.py`
- `src/starry_lyfe/context/budgets.py`
- `src/starry_lyfe/context/constraints.py`
- `src/starry_lyfe/canon/characters.yaml`
- `src/starry_lyfe/canon/pairs.yaml`
- `src/starry_lyfe/canon/voice_parameters.yaml`
- `tests/unit/test_assembler.py`

## Executive Assessment

Reina is not broken at the surface level. The runtime already preserves her tactical sharpness, the Admissibility frame, the post-intensity crash concept, and the no-offstage-dyad fix. But the default runtime prompt still over-compresses the parts of her that make her more than "the sharp one." The live assembly keeps operator energy and some Barcelona substrate, but it still underrepresents:

- the Cuatrecasas-to-defence-law pivot
- the stable and horse-world specificity
- the Mediterranean reset and daily domestic return
- the Kinetic Pair metaphor beyond the bare label
- the staged, deliberate architecture of how she escalates intimacy

The result is that the system can produce a recognizable Reina surface, but it still risks rendering a narrowed Reina: incisive, kinetic, and flirt-capable, without enough of the deeper geography, discipline, and domestic choreography that the Vision treats as load-bearing.

## Findings

### 1. Medium: The default runtime kernel still drops too much of Reina's later identity substrate

The kernel compiler allocates fixed per-section budgets and then trims each section by prefix using `trim_text_to_budget()` in `src/starry_lyfe/context/kernel_loader.py:29-40`, `src/starry_lyfe/context/kernel_loader.py:109-166`, and `src/starry_lyfe/context/budgets.py:59-91`. That means Reina's runtime kernel does not fail because the wrong sections are selected. It fails because the right sections are still clipped too early inside each section.

In source canon, Reina's identity includes:

- the Cuatrecasas years and the deliberate break from corporate law in `Characters/Reina/Reina_Torres_v7.1.md:26-28`
- the stable and horse domain with Bishop and Vex in `Characters/Reina/Reina_Torres_v7.1.md:34`
- courtroom register applied outside court in `Characters/Reina/Reina_Torres_v7.1.md:96`
- Mediterranean reset behavior in `Characters/Reina/Reina_Torres_v7.1.md:100` and `Characters/Reina/Reina_Torres_v7.1.md:165`

In live probing of `load_kernel("reina", budget=2000)`, the runtime kernel still omitted `Cuatrecasas`, `Bishop`, `Vex`, `courtroom voice`, and `Mediterranean reset`, even while retaining `Barcelona`, `Kinetic Pair`, `Post-Race Crash`, and `Real Madrid scarf`.

Impact:

- The runtime preserves Reina as fast, precise, and physical.
- It underpreserves Reina as a lawyer who chose against prestige, a horse-and-stable woman with real domain ownership, and a woman with a canonical home-return rhythm.
- This drifts from the Vision's description of her as a Barcelona-born criminal defence lawyer and body reader with a specific action architecture in `Vision/Starry-Lyfe_Vision_v7.1.md:58`, not merely a generalized kinetic initiator.

### 2. Medium: Layer 5 still drops the Reina voice examples that carry her deepest domestic and escalation registers

Layer 5 is capped at 200 tokens in `src/starry_lyfe/context/budgets.py:16`. For non-Adelia characters, voice guidance is reordered by spread heuristic in `src/starry_lyfe/context/kernel_loader.py:278-282`, then included until the Layer 5 budget is exhausted in `src/starry_lyfe/context/layers.py:179-199`.

That helps mode coverage in theory, but the live Reina prompt still loses the exact examples that carry her strongest private architecture:

- `Example 6: Home Dynamics And The Courthouse Shedding` in `Characters/Reina/Reina_Torres_Voice.md:84-98`
- `Example 8: Solo Practice And The Staged Mezzanine Arrival` in `Characters/Reina/Reina_Torres_Voice.md:114-127`
- `Example 10: Escalation With Whyze At The Trailhead` in `Characters/Reina/Reina_Torres_Voice.md:151-167`

In live probing of `format_voice_directives("reina", baseline)` and `assemble_context()`, the final voice layer retained Examples 1, 3, 5, 7, 9, and part of 2/4, but not 6, 8, or 10.

Impact:

- The runtime keeps Reina's sharpness, cross-examination flirtation, and public-risk appetite.
- It drops the suit-to-hoodie reset, the staged-arrival architecture with Bina, and the competence-triggered trailhead escalation with Whyze.
- That narrows Reina toward tactical incision and away from the precise private choreography that her voice file treats as canonical.

### 3. Medium: The Kinetic Pair mechanism and core metaphor are still weakly surfaced in the assembled prompt

The Vision defines the Kinetic Pair as `Temporal collision converted to engine heat` and `The Mastermind and the Operator` in `Vision/Starry-Lyfe_Vision_v7.1.md:70-73`. Canon mirrors that in `src/starry_lyfe/canon/pairs.yaml:31-34`.

But Layer 5 metadata still emits only the bare pair label in `src/starry_lyfe/context/layers.py:163-170`, specifically `Pair: {baseline.pair_name}.`

The richer pair architecture does exist in reference material:

- `The Mastermind and the Operator` in `Characters/Reina/Reina_Torres_Kinetic_Pair.md:64-66`
- `The right moment is now` in `Characters/Reina/Reina_Torres_Kinetic_Pair.md:324`
- the Mediterranean reset as dyadic geography in `Characters/Reina/Reina_Torres_Kinetic_Pair.md:300-302`

In live probing, the assembled prompt carried `Kinetic Pair` but did not carry `The Mastermind and the Operator`.

Impact:

- The runtime preserves the label of the pair but not enough of its operating metaphor.
- This weakens the part of Reina that is specifically Whyze's action-conversion interface, which the Vision treats as one of the four core pair architectures rather than optional flavor.

### 4. Medium: Reina-specific regression coverage is still too weak to protect fidelity

Current Reina-specific tests only assert that her constraint block mentions Admissibility in `tests/unit/test_assembler.py:201-205`. The real assembled-prompt regression remains a Bina path in `tests/unit/test_assembler.py:360-402`.

There is currently no Reina-specific assembled-prompt test asserting that:

- her default kernel retains enough legal-career and stable-domain substrate
- Layer 5 retains at least one of the private domestic or escalation modes from Examples 6, 8, or 10
- the prompt carries more of the Kinetic architecture than the bare pair label

Impact:

- The current suite can stay green while Reina narrows into a tactically correct but emotionally thinner rendering.
- This is exactly the kind of drift that Phase 3 verification is supposed to catch and currently does not.

### 5. Low: Reina's pair markdown still carries stale governance residue that can mislead future conversion work

`Characters/Reina/Reina_Torres_Kinetic_Pair.md` still points at `Reina_Torres_v7.0.md` as the companion document in `Characters/Reina/Reina_Torres_Kinetic_Pair.md:6`.

More importantly, the chosen-family ecosystem section still contains stale Alicia framing:

- `Alicia Marin, non-resident, based in Madrid as a Spanish consular officer and visiting the property twice yearly between operations` in `Characters/Reina/Reina_Torres_Kinetic_Pair.md:254-256`

That no longer matches current Vision governance, where Alicia is resident at the property with frequent operational travel in `Vision/Starry-Lyfe_Vision_v7.1.md:12`.

Impact:

- This does not directly corrupt the current runtime, because the pair markdown is not directly ingested.
- It does create a documentation trap for future fidelity work by leaving stale v7.0-era world state inside a character reference file that is still treated as canonical support material.

## Verified Resolved

Some previously known Reina-path failures appear fixed:

- Solo `Reina + Whyze` scenes do not get the `TALK-TO-EACH-OTHER` mandate. The gate lives in `src/starry_lyfe/context/constraints.py:104` and the current test coverage exists in `tests/unit/test_assembler.py:229-240`.
- Offstage dyads do not appear to leak into Layer 6. Internal dyads are only included when the other woman is present in `src/starry_lyfe/context/layers.py:232-240`, and live probing did not surface `reina-bina` in a `Reina + Whyze` scene.
- Reina's per-persona inference specialization exists in canon, including `high_presence_penalty`, in `src/starry_lyfe/canon/voice_parameters.yaml:32-44`.
- The Admissibility frame still exists in runtime governance via the constraint path and test in `tests/unit/test_assembler.py:201-205`.

## Bottom Line

Reina is directionally correct in code, but not yet fully alive at the default runtime window.

The current system renders:

- tactical
- body-reading
- flirt-capable
- fast-moving

It still under-renders:

- the lawyer who deliberately abandoned prestige
- the woman whose stable, horses, and movement discipline are part of identity rather than scene props
- the Mediterranean domestic-return rhythm
- the staged, precise architecture of her private escalation
- the full Kinetic Pair metaphor that explains why her dynamic with Whyze feels structurally different from the others

That is not a schema bug. It is a fidelity bug caused by budget compression, weak pair-surface formatting, and missing Reina-specific regression coverage.

## Verification Method

Static review plus live prompt probes:

- `load_kernel("reina", budget=2000)`
- `load_voice_guidance("reina")`
- `format_voice_directives("reina", baseline)`
- `assemble_context()` with a stubbed `Reina + Whyze` in-person scene

The existing repo verification state remained clean during audit:

- `ruff check src tests`
- `mypy src tests`
- `pytest tests/unit/test_assembler.py -q`
- `pytest tests -q`

Those gates currently prove structural correctness. They do not yet prove Reina fidelity.
