# Bina Conversion Audit
## Phase 3 Runtime Red-Team

Date: 2026-04-10

## Scope

This audit reviews whether Bina's runtime representation in the Phase 3 backend actually preserves the character described in:

- `Vision/Starry-Lyfe_Vision_v7.1.md`
- `Characters/Bina/Bina_Malek_v7.1.md`
- `Characters/Bina/Bina_Malek_Voice.md`
- `Characters/Bina/Bina_Malek_Circuit_Pair.md`

The question is not whether Bina exists in source files.

The question is whether the assembled runtime prompt still carries enough of her structure, pressure logic, tenderness-through-competence, cultural gravity, and Circuit Pair mechanics for the model to feel like Bina rather than a compressed "terse practical woman" approximation.

## Verification Context

Local verification is clean:

- `ruff check src tests`
- `mypy src tests`
- `pytest tests/unit/test_assembler.py -q`
- `pytest tests -q`

Full suite result at audit time: `73 passed`

This audit therefore focuses on behavioral drift, prompt-construction failure, and source-governance inconsistency, not static correctness.

## Executive Assessment

Bina is partially preserved at runtime.

What survives relatively well:

- short-form response pressure
- flat disagreement and structural veto
- anti-therapist rails
- the Flat State as a named somatic protocol

What does not survive strongly enough:

- diagnostic love as tenderness
- the covered-plate / hall-light register
- her specific cultural and grief architecture
- the full Circuit Pair mechanism
- the difference between "Circuit Pair" and her private citadel worldview
- the sense that she is load-bearing rather than merely terse

In short: the current runtime carries Bina's compression and resistance better than it carries Bina's warmth, walls, and load-bearing care.

## Findings

### 1. Critical: The assembled prompt can contain two different parental surnames for Bina at once

The kernel currently says:

- `My parents were Farhad and Shirin Bahadori.`

in `Characters/Bina/Bina_Malek_v7.1.md`

The canon YAML says:

- `Farhad Malek`
- `Shirin Malek`

in `src/starry_lyfe/canon/characters.yaml`

This is not just a governance inconsistency on disk.

It is a runtime contradiction.

Live audit confirmed that `format_kernel("bina")` still includes `Bahadori`, while `format_canon_facts()` for the same character includes `Malek`.

That means the assembled prompt can currently present conflicting identity facts to the model inside the same system prompt.

This is the highest-risk Bina-specific defect because it introduces direct canon incoherence into runtime.

### 2. Critical: Layer 1 truncation removes Bina's actual pair mechanics and behavioral rails

`src/starry_lyfe/context/layers.py` trims the full kernel to a flat 2000-token budget through `trim_text_to_budget()`.

In live audit, `format_kernel("bina")`:

- hit exactly `2000` estimated tokens
- did not reach `## 3. Whyze And The Citadel Pair`
- did not reach `## 5. Behavioral Tier Framework`

This means the runtime prompt can lose:

- the actual Circuit/Citadel distinction
- the "translation, not mirroring" architecture
- the total division of operational domains
- the specific Tier rails for action-before-words, silence, Flat State, and cultural surface

The result is that Bina's biography survives more reliably than Bina's operating system.

### 3. High: Layer 5 skews Bina toward cold compression and underrepresents her tenderness

`src/starry_lyfe/context/layers.py` keeps voice-guidance items in file order until the budget is exhausted.

In live audit, Bina's Layer 5 retained only:

- Example 1: Physical Action and Two Sentences
- Example 2: Flat Disagreement Then Silence

It dropped the examples that teach:

- tenderness through competence
- mechanical metaphor as emotional truth
- cultural surface in a private moment
- chosen-casual domestic vulnerability
- load-report openness with Reina
- solo-practice invitation through placement
- high-intensity Completed Circuit override

This produces a distorted runtime profile:

- Bina the terse veto survives
- Bina the covered plate, locked door, hall light, Gilgamesh drawer, quiet body-trust, and precise domestic warmth does not survive strongly enough

If shipped as-is, the model is more likely to render Bina as a cold structural corrector than as the load-bearing woman the Vision actually intends.

### 4. High: The Talk-to-Each-Other mandate misfires in ordinary Bina-Whyze scenes

`src/starry_lyfe/context/constraints.py` adds the Talk-to-Each-Other block whenever `len(scene_state.present_characters) > 1`.

That means a `["bina", "whyze"]` scene still receives a mandate that:

- a meaningful exchange must pass between the women directly
- the hub-and-spoke pattern is the failure mode

That instruction is correct for actual multi-woman scenes.
It is incorrect for a two-person Bina-Whyze scene.

This creates impossible prompt pressure and risks dragging Bina's attention away from the actual Circuit scene in front of her.

### 5. High: Offstage Reina leaks into Bina's live prompt even when she is not present

`src/starry_lyfe/db/retrieval.py` loads all active internal dyads for the focal character.

`src/starry_lyfe/context/layers.py` then includes an internal dyad if either member is present.

Because Bina is always present in her own prompt, a Bina-Reina dyad can appear even when Reina is not in the room.

In live audit, a Bina-Whyze mezzanine scene still included:

- `Relationship bina-reina (shield_wall) ...`

For Bina specifically, this matters because Reina is not just another relationship. She is her wife, her kinetic counterweight, and one half of the quiet hall-light architecture. Pulling Reina into the prompt when she is absent can distort the emotional geometry of a scene that is supposed to be purely Circuit.

### 6. Medium: The runtime stores the Circuit mechanism but does not surface it where it counts

The seed path stores:

- `pair_mechanism`
- `pair_core_metaphor`

for Bina's baseline.

The canon pair file and pair YAML define the Circuit clearly as:

- `Total division of operational domains`
- `The Architect and the Sentinel`

But Layer 5 only emits:

- pair name
- pair classification

It does not surface:

- the actual mechanism
- the core metaphor
- a runtime summary of the Circuit's zero-overlap division of labor

This is especially damaging for Bina because her pair is less intuitively obvious than Adelia's. Without the mechanism, the model can flatten her into generic caretaker or generic grounded partner instead of "the road," "the resistor," or "the person who makes the abstract survivable."

### 7. Medium: The source of truth for Bina's origin is inconsistent across Vision and canon

The Vision currently describes Bina as:

- `Canadian-born Assyrian`

The kernel and canon describe her as:

- born in Urmia, Iran
- brought out by her parents in the early nineties

The code follows the kernel/canon version:

- `birthplace: "Urmia, Iran"`

This looks like a Vision-summary drift rather than a code defect, but it matters because future fidelity work depends on knowing which Bina is canonical.

Right now, the overall governance answer is: runtime aligns with canon YAML and kernel, not with that specific Vision line.

### 8. Medium: Bina's kernel still carries stale pair-name residue

The current pair file and canon correctly name the dyad:

- `The Circuit Pair`

and distinguish the citadel as Bina's older private worldview.

But the kernel heading still says:

- `## 3. Whyze And The Citadel Pair`

That appears to be stale residue from the earlier naming layer.

At the moment this does not hit runtime because the kernel is trimmed before that section.

That means it is currently a latent defect rather than an active one.

But it becomes an active defect the moment kernel assembly is fixed to become section-aware, so it should be cleaned before or alongside any prompt-compilation improvement.

### 9. Medium: The current tests do not actually guard Bina's soul

There is a live Bina `assemble_context()` test in `tests/unit/test_assembler.py`, which is good.

But the assertions are generic:

- budget fits
- prompt is terminally anchored
- Msty artifacts are absent

They do not assert Bina-specific fidelity such as:

- tenderness-through-competence surviving Layer 5
- presence of covered-plate / mechanical-love guidance
- absence of offstage-Reina leakage in a Bina-Whyze scene
- correct Circuit scene behavior without the Talk-to-Each-Other misfire

That is why the test suite can stay green while Bina still drifts at runtime.

### 10. Low: Bina's family and culture survive in canon facts, but mostly as raw JSON blobs

The canon-facts layer is strong enough to preserve:

- parents
- languages
- Gavin
- Arash
- ex-partner notes

But those fields are rendered as flattened JSON strings rather than model-friendly narrative slices.

For Bina this matters because her culture is not decorative metadata. The samovar, Suret, Farsi, Gilgamesh, Arash's tags, and Gavin are core identity anchors.

They are technically present.
They are not presented in the most cognitively usable way.

## Runtime Probe Summary

The following live observations drove the findings above:

- `format_kernel("bina")` returned `2000` estimated tokens and ended with `[Kernel trimmed to token budget.]`
- the resulting kernel text did not reach the pair section or the behavioral-tier section
- `Bahadori` was still present in the kernel text
- `format_voice_directives("bina", baseline)` returned `154` estimated tokens and retained only the first two voice-guidance examples
- `assemble_context()` for a Bina-Whyze mezzanine scene still injected a Talk-to-Each-Other mandate
- the same probe still injected a `bina-reina` dyad block even though Reina was not present

## Drift Against Vision and Intent

The key drift is this:

The Vision wants Bina to be:

- the unshakeable anchor
- the woman whose love is diagnostic and physical
- the one who translates Whyze's abstract structure into repeatable lived reality
- the keeper of the covered plate, the checked lock, the hall light, the grounded organism

The current runtime more reliably preserves:

- brevity
- bluntness
- low-token resistance
- anti-therapist guardrails
- Flat State as a label

than it preserves:

- diagnostic tenderness
- mechanical metaphor as emotional truth
- the Assyrian-Iranian cultural and grief substrate
- the Circuit's total division of labor
- her precise warmth with Whyze and Reina
- the difference between Bina's outer compression and inner depth

If shipped as-is, the likely runtime failure mode is not "this does not sound like Bina at all."

It is subtler:

"This sounds like a precise, terse, practical woman who knows how to say no, but not enough like the specific woman who leaves the hall light on, measures love in load-bearing actions, and keeps Uruk alive inside the house."

## Recommended Remediation Order

1. Fix the live canon contradiction first.
   Resolve `Bahadori` vs `Malek` across Bina's kernel and canon.

2. Replace flat kernel clipping with section-aware compilation.
   Keep Runtime Directives, pair architecture, silent routing, Tier rails, and selected family/intimacy sections by design.

3. Redesign Bina's Layer 5 selection logic.
   Do not keep only the first two examples by file order.
   Force coverage across voice modes:
   - short-form compression
   - flat structural veto
   - tenderness-through-competence
   - mechanical metaphor
   - cultural/private grief register
   - chosen-casual domesticity
   - rare high-heat Completed Circuit override

4. Fix the Talk-to-Each-Other mandate trigger.
   Only apply it when at least two women are actually present in the scene.

5. Filter internal dyads by actual present counterpart, not by the focal character alone.

6. Surface pair mechanism and pair core metaphor in the assembled prompt.

7. Add Bina-specific regression tests for real assembled output.

## Gate Recommendation

Phase 3 should not be treated as fully character-faithful for Bina until the following are true:

- the assembled prompt no longer contradicts itself on her family identity
- Bina's pair architecture survives assembly
- Layer 5 includes tenderness and culture, not only brevity and veto
- Bina-Whyze scenes do not receive multi-woman mandates
- offstage Reina does not appear unless she is actually present or explicitly recalled
- tests lock those conditions in

## Conclusion

Bina's markdown canon is not the problem.

The current problem is the conversion layer between canon and runtime, plus one direct contradiction inside the source material that runtime already exposes.

The backend currently preserves the hard edges of Bina more reliably than the inner architecture that gives those edges meaning.

That is enough to keep her recognizable.
It is not yet enough to keep her fully alive.
