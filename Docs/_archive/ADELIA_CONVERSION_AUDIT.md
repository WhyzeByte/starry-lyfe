# Adelia Conversion Audit
## Phase 3 Runtime Red-Team

Date: 2026-04-10

## Scope

This audit reviews whether Adelia's runtime representation in the Phase 3 backend actually preserves the character described in:

- `Vision/Starry-Lyfe_Vision_v7.1.md`
- `Characters/Adelia/Adelia_Raye_v7.1.md`
- `Characters/Adelia/Adelia_Raye_Voice.md`
- `Characters/Adelia/Adelia_Raye_Entangled_Pair.md`

The question is not whether Adelia exists in source files. She does.

The question is whether the assembled runtime prompt still carries enough of her structure, pressure points, pair mechanics, register, and behavioral rails for the model to feel like Adelia rather than a flattened approximation.

## Verification Context

Local verification is clean:

- `ruff check src tests`
- `mypy src tests`
- `pytest tests/unit/test_assembler.py -q`
- `pytest tests -q`

Full suite result at audit time: `73 passed`

This audit therefore focuses on behavioral drift and prompt-construction failure, not static correctness.

## Executive Assessment

Adelia's markdown canon is strong.

Her runtime conversion is not yet strong enough.

The backend currently preserves a meaningful amount of her biography and some top-level cadence, but it systematically over-compresses or omits the exact material that the Vision treats as load-bearing:

- the Entangled Pair as the system's gravitational center
- the Whyze hand-off mechanic
- the quiet and seismograph versions of her voice
- the domestic and erotic registers that distinguish warmth from generic romance
- the specific Valencian-Australian cultural surface
- the correct scene-level routing rules for when other women are and are not actually present

In short: Adelia is present in the repo, but not yet fully present in runtime.

## Findings

### 1. Critical: Layer 1 truncation removes the parts of Adelia that most matter

`src/starry_lyfe/context/layers.py` trims the entire kernel to a flat 2000-token budget through `trim_text_to_budget()`.

In live audit, `format_kernel("adelia")` hit exactly `2000` estimated tokens and cut off before:

- `## 3. Whyze And The Entangled Pair`
- `## 5. Behavioral Tier Framework`

That means the assembled prompt can lose:

- the actual Whyze-Adelia interlock
- the explicit "I bring the destination, he brings the route" architecture
- the specific behavioral tier rails that are supposed to keep her from collapsing into generic warmth

This is the largest single drift from the Vision.

The Vision says the Entangled Pair is not a feature. It is the reason the system exists. If the runtime prompt routinely loses that material, the backend is preserving Adelia's biography more reliably than Adelia's purpose.

### 2. High: Layer 5 skews Adelia toward one narrow slice of her voice

`src/starry_lyfe/context/layers.py` keeps voice-guidance items in file order until the budget is exhausted.

In live audit, Adelia's Layer 5 retained only:

- Example 1: Mid-Thought Tangent That Resolves
- Example 2: Challenges Through A Better Question

It dropped the examples that teach:

- near-silent seismograph response
- direct reciprocity and asking for Whyze's brain
- cultural surface under pressure
- domestic hoodie-couch warmth
- competence-triggered erotic ignition
- solo-practice placement-as-message

The result is a runtime bias toward "talk fast, tangent, reframe" while underrepresenting:

- quiet
- embodied devotion
- load-bearing domesticity
- calibrated erotic escalation
- pressure-language surfacing

This is not a small stylistic issue. It changes the felt shape of the character.

### 3. High: The Talk-to-Each-Other mandate misfires in ordinary Adelia-Whyze scenes

`src/starry_lyfe/context/constraints.py` adds the Talk-to-Each-Other block whenever `len(scene_state.present_characters) > 1`.

That means an `["adelia", "whyze"]` scene still receives a mandate that:

- a meaningful exchange must pass between the women directly
- the hub-and-spoke pattern is the failure mode

That instruction is correct for actual multi-woman scenes.
It is incorrect for a two-person Adelia-Whyze scene.

This creates impossible prompt pressure and can distort generation by asking the model to satisfy a scene rule that does not match the scene.

### 4. High: Offstage women leak into Adelia's live prompt even when they are not present

`src/starry_lyfe/db/retrieval.py` loads all active internal dyads for the focal character.

`src/starry_lyfe/context/layers.py` then includes an internal dyad if either member is present.

Because Adelia is always present in her own prompt, an Adelia-Bina or Adelia-Reina dyad can appear even when Bina or Reina are not in the room.

In live audit, an Adelia-Whyze warehouse scene still included:

- `Relationship adelia-bina (...)`

This matters because the prompt begins to imply social pressure or relational context that does not exist in the immediate scene.

For a character whose voice is supposed to be scene-honest and relationally precise, this is a real fidelity problem.

### 5. Medium: The Entangled Pair architecture is stored in memory but not surfaced where it counts

The seed path stores pair mechanism and pair metaphor in `character_baselines`:

- `pair_mechanism`
- `pair_core_metaphor`

But Layer 5 only emits:

- pair name
- pair classification

It does not surface:

- the actual mechanism
- the "Compass and the Gravity" metaphor
- any runtime summary of why Adelia and Whyze work the way they work

So even when the data exists in the database, the assembled prompt does not make useful use of it.

Combined with kernel truncation, this leaves the runtime version of Adelia with an underpowered pair model.

### 6. Medium: Adelia's Spanish register is canonically preserved but runtime-weak

The canon correctly stores Adelia as:

- Valencian-Australian
- Valencian-inflected Castilian via Sydney diaspora

The Vision also explicitly requires that her Spanish not collapse into generic Spanish.

At runtime, however, the prompt usually reduces this to:

- a heritage label
- one profession line
- possibly one or two early voice examples that do not strongly express her pressure-register or private-language behavior

The most useful examples for teaching the rare, earned, non-costume use of language are among the items that get dropped first under the current Layer 5 budget.

### 7. Medium: Flat token trimming destroys the structure of character documents

`trim_text_to_budget()` trims by splitting on whitespace and cutting at a token estimate.

That means a structured document becomes a flat prefix.

For Adelia this is especially damaging because her kernel uses section boundaries to separate:

- identity
- pair mechanics
- silent routing
- behavioral rails
- family dynamics
- intimacy architecture

Even when the right content survives, it survives as a compressed text wall rather than as a structured operating document.

This makes the surviving material less legible to the model and less faithful to the authored hierarchy.

### 8. Medium: The current tests do not guard the Adelia-specific failure path

The Phase 3 test suite is green, but the live `assemble_context()` coverage currently targets:

- Bina
- Alicia

There is no equivalent regression test asserting that an actual Adelia assembly preserves:

- Entangled Pair content
- correct dyadic scene rules
- absence of offstage-woman leakage
- sufficient voice-mode diversity beyond the first two examples

This is why the suite can stay green while Adelia still drifts at runtime.

## Runtime Probe Summary

The following live observations drove the findings above:

- `format_kernel("adelia")` returned `2000` estimated tokens and ended with `[Kernel trimmed to token budget.]`
- The resulting kernel text did not reach Adelia's Entangled Pair section
- `format_voice_directives("adelia", baseline)` returned `165` estimated tokens and retained only the first two voice-guidance examples
- `assemble_context()` for an Adelia-Whyze warehouse scene still injected a Talk-to-Each-Other mandate
- The same probe still injected an Adelia-Bina internal-dyad block even though Bina was not present

## Drift Against Vision and Intent

The key drift is this:

The Vision wants Adelia to be the gravitational center of the system through a specific interlock with Whyze.

The current runtime more reliably preserves:

- biography
- labels
- MBTI metadata
- top-level profession and heritage
- generic anti-assistant guardrails

than it preserves:

- the actual entanglement mechanic
- her hand-off dependence on Whyze's sequencing mind
- her load-bearing quietness
- her domestic warmth that is not generic romance
- her specific cultural register
- her correct scene discipline

That is not total failure, but it is enough drift to matter.

If shipped as-is, the likely runtime failure mode is not "this sounds nothing like Adelia."

It is subtler:

"This sounds like a smart, warm, fast, mildly embodied ENFP-shaped persona who has Adelia's biography but not enough of Adelia's actual operating system."

## Recommended Remediation Order

1. Replace flat kernel clipping with section-aware compilation.
   Keep Runtime Directives, Whyze/Entangled Pair, Silent Routing, Tier rails, and selected family/intimacy sections by design.

2. Redesign Adelia's Layer 5 selection logic.
   Do not keep only the first examples by file order.
   Force coverage across voice modes:
   - tangent
   - reframing challenge
   - near-silent mode
   - reciprocity / asks for his brain
   - cultural-pressure register
   - domestic register
   - competence-triggered escalation

3. Fix the Talk-to-Each-Other mandate trigger.
   Only apply it when at least two women are actually present in the scene.

4. Filter internal dyads by actual present counterpart, not by the focal character alone.

5. Surface pair mechanism and pair core metaphor in the assembled prompt.
   The Entangled Pair cannot live only in seed data.

6. Add Adelia-specific regression tests around real assembled output.

## Gate Recommendation

Phase 3 should not be treated as fully character-faithful for Adelia until the following are true:

- an assembled Adelia prompt reliably contains Entangled Pair runtime content
- her voice layer includes more than the first two examples
- Adelia-Whyze scenes do not receive multi-woman mandates
- offstage women do not appear in Layer 6 unless actually present or explicitly recalled
- tests lock those conditions in

## Conclusion

Adelia's markdown canon is not the problem.

The current problem is the conversion layer between canon and runtime.

The backend is close enough to preserve her outline, but not yet disciplined enough to preserve her center of mass.

That center of mass is the entire point of the system.
