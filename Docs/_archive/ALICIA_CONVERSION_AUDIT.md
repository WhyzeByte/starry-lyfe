# Alicia Conversion Audit
## Phase 3 Runtime Red-Team

Date: 2026-04-10

## Scope

This audit reviews whether Alicia's current runtime representation preserves the character described in:

- `Vision/Starry-Lyfe_Vision_v7.1.md`
- `Characters/Alicia/Alicia_Marin_v7.1.md`
- `Characters/Alicia/Alicia_Marin_Voice.md`
- `Characters/Alicia/Alicia_Marin_Solstice_Pair.md`

The question is not whether Alicia exists in source files.

The question is whether the assembled runtime prompt still carries enough of her operational discipline, Argentine interiority, return mechanics, bodily intelligence, and Solstice architecture for the model to feel like Alicia Marin rather than a generic "somatic regulator with a passport."

## Verification Context

Static verification is clean:

- `.\.venv\Scripts\python.exe -m ruff check src tests`
- `.\.venv\Scripts\python.exe -m mypy src tests`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_assembler.py -q`
- `.\.venv\Scripts\python.exe -m pytest tests -q`

Full suite result at audit time: `86 passed`

This audit therefore focuses on runtime drift, prompt-construction bias, and missing fidelity coverage, not on lint or type failures.

## Executive Assessment

Alicia is partially preserved at runtime.

What survives well:

- her Famaillá and factory-to-Cancillería identity substrate
- body-first entry style
- Sun Override as a named mechanism
- Four-Phase Return as a named protocol when the somatic state carries it
- away-state gating for in-person scenes

What is still underrepresented or misrepresented:

- remote-mode adaptation when she is away on phone or letter
- her refusal architecture: no trauma performance, no action-hero collapse, no costume Argentineness
- the parts of her home life that make her specifically Alicia rather than a generic warm operator
- the Solstice Pair's explicit duality framing and metaphor surface
- her Reina-specific professional overlap and group-temperature function

In short: the backend now preserves Alicia's outer function more reliably than her professional restraint, private Argentine interior life, and mode-specific scene truth.

## Findings

### 1. High: Away-state phone and letter prompts still carry in-person-only somatic instructions

The current assembly path uses `communication_mode` only to block in-person Alicia while she is away in `src/starry_lyfe/context/assembler.py`. Once the prompt is allowed, the rest of the assembly path is the same regardless of whether the scene is in person, phone, or letter.

That creates a live contradiction for Alicia specifically.

Her constraint pillar still says:

- `Somatic contact first, speech after the shift completes.`

in `src/starry_lyfe/context/constraints.py`

And the live phone-scene prompt still included:

- `Example 3: The Sun Override On Whyze (Four-Signal Form)`
- `Example 5: Four-Phase Return, The Kitchen With Him`
- the Solstice constraint text requiring body-first somatic intervention

This is a real mode mismatch. A late-night phone call from a hotel room abroad cannot truthfully be instructed by the same contact-first logic as an in-person kitchen reunion.

The result is that Alicia's remote scenes are currently shaped by in-person body mechanics that the scene literally cannot perform.

### 2. High: The default Alicia kernel drops too much of her refusal and professional-discipline architecture

The 2000-token compiled kernel preserves Alicia's introduction, the front half of the Solstice section, the silent-routing block, the first slice of Tier 1, and the Sun Override section.

But in live probing, `load_kernel("alicia", budget=2000)` did **not** retain:

- `No costume Argentineness`
- `No action-hero collapse`
- `No trauma performance`
- `I enter the present tense and stay there`
- `I do not perform happiness`
- `The Assertive identity does not mean unbothered`
- `I default to physical contact with the people I love`
- `I am professional about my profession`

Those are not ornamental notes. They are core anti-drift rails in `Characters/Alicia/Alicia_Marin_v7.1.md` Section 5.

This matters because the Vision's intention for Alicia is not "warm body-first presence" in the abstract. It is specifically:

- a disciplined Argentine consular officer
- not an action-film operative
- not a tourism-card version of Argentina
- not a trauma-narrative performer
- not "happy" as a default

Right now the default compiled kernel reaches the operational-security gate, but it loses too much of the rest of the character-specific refusal architecture that keeps Alicia from collapsing into a glamorous or genericized version of herself.

### 3. High: Layer 5 omits the exact Alicia examples that teach warm refusal, group function, and trauma discipline

The current voice-guidance spread heuristic in `src/starry_lyfe/context/kernel_loader.py` reorders Alicia's ten examples as:

- 1, 3, 5, 7, 9, 2, 4, 6, 8, 10

The 200-token Layer 5 budget in `src/starry_lyfe/context/budgets.py` and the first-fit selection in `src/starry_lyfe/context/layers.py` then keep only the first six compact items.

In live runtime, Alicia's voice layer preserved:

- Example 1: body-first kitchen entry
- Example 3: Sun Override
- Example 5: Four-Phase Return
- Example 7: couch above the garage with Bina
- Example 9: Tía Apo / children gate
- Example 2: counting under her breath / food word

It dropped:

- Example 4: operational security gate, warm refusal
- Example 6: temperature change in a group scene
- Example 8: late-night reading-rooms conversation with Reina
- Example 10: no trauma performance refusal

That is not a neutral loss profile. It means Alicia's live prompt is currently well-taught on arrival, touch, return, and warmth, but under-taught on:

- refusing consular disclosure inside intimacy
- being the temperature change rather than the hub in group scenes
- the Reina-specific body-reading/professional-overlap register
- the exact "I will not turn human suffering into bedroom narrative" refusal that protects her soul

Combined with the kernel clipping above, this leaves some of Alicia's most important "no" mechanics absent from the actual runtime prompt.

### 4. Medium: Alicia's domestic and Argentine interior life is still largely excluded from the runtime kernel

At the default budget, the compiled Alicia kernel contains no Section 8 at all.

That means the live kernel excludes:

- her baths with the door open
- the *zamba* / Mercedes Sosa texture
- `When I Am Away`
- the `Tía Apo` child relationship block
- the fuller home-sleeping architecture
- the Reina football and reading-room overlap
- the detailed return/away shape as written in the kernel rather than summarized in a voice note

Some of this is partially recovered through Layer 5 examples, especially Four-Phase Return, the couch above the garage, and Tía Apo.

But live prompt probing still showed that the assembled Alicia prompt did **not** carry:

- `Mercedes Sosa`
- bath / bath-song texture
- `When I am away`
- the deeper home-dynamics blocks

This is where a lot of Alicia's specific soul lives: not just in being sensory, but in being this exact Argentine woman with this exact return rhythm and this exact private domestic vocabulary.

### 5. Medium: The Solstice Pair mechanism is present as function but weakly surfaced as architecture

Vision and canon define Alicia's dyad through:

- `Complete Jungian Duality`
- `Inferior-function gift exchange through dominant mastery`
- `The Duality`

in `Vision/Starry-Lyfe_Vision_v7.1.md` and `src/starry_lyfe/canon/pairs.yaml`.

The runtime prompt does preserve the Solstice section's mirror-stack logic, but the live assembled prompt did **not** include:

- `The Duality`
- `Complete Jungian Duality`

And Layer 5 metadata still emits only:

- `Pair: solstice`

rather than the pair mechanism or core metaphor.

For Alicia this matters because her entire non-redundancy claim depends on the fact that she is not merely a warm Se-dominant. She is the house's one full inversion with Whyze. Without the explicit duality surface, she risks flattening toward "somatic co-regulator" instead of "the only full mirror-stack pair in the family."

### 6. Medium: Alicia-specific test coverage still checks gating, not fidelity

Current Alicia tests in `tests/unit/test_assembler.py` verify:

- her constraint pillar exists
- in-person away-state assembly is blocked
- phone-mode away-state assembly is allowed

What they do **not** verify:

- that remote phone or letter prompts do not carry in-person-only somatic instructions
- that Alicia's live prompt retains her refusal architecture
- that operational security and no-trauma-performance survive default budgets
- that Four-Phase Return, Sun Override, Argentine register, and group-temperature function all survive together
- that the assembled prompt distinguishes Alicia from a generic warm Se-dominant

This is why the test suite stays fully green while the actual Alicia prompt still exhibits mode mismatch and selective flattening.

## Runtime Probe Summary

The following live observations drove the findings above:

- `load_kernel("alicia", budget=2000)` retained `Famaillá`, `Buenos Aires`, `Solstice Pair`, and `Sun Override`, but did **not** retain `Four-Phase Return`, `When I am away`, `Tía Apo`, `Mercedes Sosa`, `The Duality`, or the later Section 5 defaults that keep her from flattening.
- `format_voice_directives("alicia", baseline)` kept Examples 1, 3, 5, 7, 9, and 2, but dropped Examples 4, 6, 8, and 10.
- A live in-person home prompt carried `Sun Override`, `Four-Phase Return`, `Famaillá`, and `Rioplatense`, but still lacked `The Duality`, `Mercedes Sosa`, and bath/home-return texture.
- A live away-state phone prompt still carried `Somatic contact first` plus in-person calibration items `Example 3` and `Example 5`.

## Verified Resolved

The following earlier Alicia-path failures do appear fixed:

- In-person Alicia prompt assembly is blocked while she is away on operations.
- Phone-mode Alicia assembly while away is allowed.
- Offstage dyads did not leak in my live Alicia-Whyze probes.
- Raw Msty few-shot artifacts are not entering the backend prompt path.

## Bottom Line

The current backend does not collapse Alicia into nonsense. It preserves the broad shape of her: body-first, Argentine, operational, warm, intermittently present, Sun Override capable.

But it still underfeeds the exact things that make her Alicia rather than a generic sensual co-regulator:

- refusal discipline
- institutional professionalism
- remote-mode truth
- domestic Argentine interiority
- Solstice duality as architecture rather than just vibe

The core risk is not that she feels wrong in every scene.

The core risk is that she feels right in the obvious scenes and thinner everywhere else.

## Recommended Remediation Order

1. Add communication-mode-aware pruning for Alicia phone and letter scenes so in-person somatic instructions do not contaminate remote prompts.
2. Protect Alicia's refusal architecture in the kernel compiler or via Alicia-specific runtime overlays.
3. Rebalance Alicia Layer 5 so Examples 4 and 10 survive by default, and so Example 6 is considered when group scenes are active.
4. Add Alicia-specific assembled-prompt regression tests for:
   - home return
   - away-state phone
   - operational-security refusal
   - no-trauma-performance refusal
   - group temperature-change behavior
