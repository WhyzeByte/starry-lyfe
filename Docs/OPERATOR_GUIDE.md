# Operator Guide: Character Markdown -> Runtime Prompt

**Version:** 1.1 (2026-04-13)
**Scope:** Accurate walkthrough of how character-source material becomes the seven-layer runtime prompt.
**Audience:** Project Owner, operators, and anyone who needs the runtime map without re-reading the whole codebase.

---

## 1. What This Document Is (And Is Not)

**Is:** A runtime-oriented guide. It starts with the canonical character corpus and ends at the XML-wrapped prompt returned by `assemble_context()`.

**Is not:**
- An authoring guide. For phase-by-phase buildout rules, see `Docs/IMPLEMENTATION_PLAN_v7.1.md`.
- A governance spec. For character-behavior rules, see `Docs/Persona_Tier_Framework_v7.1.md`.
- A four-agent workflow guide. For SDLC rules, see `AGENTS.md`.
- A canonical phase-status document. For shipped vs planned subsystem status, see `Docs/IMPLEMENTATION_PLAN_v7.1.md`. For the concise module and schema index, see `Docs/ARCHITECTURE.md`.

This document was audited directly against the current code on 2026-04-13. The references below describe what the runtime actually does now, not what earlier phases intended to do.

---

## 2. Canonical Character Corpus vs Direct Runtime Inputs

Each resident character currently has four canonical markdown files under `Characters/`:

| Role | Filename Pattern | Example | Runtime Status |
|------|------------------|---------|----------------|
| Kernel | `{Character}_v7.1.md` | `Adelia_Raye_v7.1.md` | Loaded directly at runtime |
| Voice | `{Character}_Voice.md` | `Adelia_Raye_Voice.md` | Loaded directly at runtime |
| Knowledge Stack | `{Character}_Knowledge_Stack.md` | `Adelia_Raye_Knowledge_Stack.md` | Authoring source only; distilled into soul cards / soul essence |
| Pair | `{Character}_{PairName}_Pair.md` | `Adelia_Raye_Entangled_Pair.md` | Authoring source only; distilled into soul cards / soul essence |

That distinction matters:

- The runtime loader in [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:14) directly reads only the kernel and voice files.
- Pair and knowledge markdown are not live-loaded by `assemble_context()`. Their runtime products are:
  - [soul_essence.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_essence.py:1)
  - [src/starry_lyfe/canon/soul_cards/](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_cards)

### 2.1 Current File Layout

Character markdown now lives flat in `Characters/`:

- [Adelia_Raye_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Adelia_Raye_v7.1.md:1)
- [Bina_Malek_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Bina_Malek_v7.1.md:1)
- [Reina_Torres_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Reina_Torres_v7.1.md:1)
- [Alicia_Marin_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Alicia_Marin_v7.1.md:1)

The kernel and voice loaders still support a legacy nested fallback layout for backward compatibility; see `KERNEL_PATHS` and `VOICE_PATHS` in [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:14).

### 2.2 The Four Characters

| Character ID | Full Name | Pair | MBTI |
|--------------|-----------|------|------|
| `adelia` | Adelia Raye | Entangled | ENFP-A |
| `bina` | Bina Malek | Circuit | ISFJ-A |
| `reina` | Reina Torres | Kinetic | ESTP-A |
| `alicia` | Alicia Marin | Solstice | ESFP-A |

### 2.3 `<!-- PRESERVE -->` Markers

The block-aware trimmer recognizes `<!-- PRESERVE -->` markers anywhere in kernel text, though they are typically used in Section 2 (`Core Identity`).

```markdown
<!-- PRESERVE -->
I am Adelia Raye. I build fire for a living...
<!-- /PRESERVE -->
```

Important runtime behavior:

- `parse_markdown_blocks()` and `trim_text_to_budget()` in [budgets.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/budgets.py:138) protect the next content block from normal drop-priority trimming.
- In strict kernel compilation paths, a preserved block that cannot fit its section budget raises `KernelCompilationError` instead of being silently dropped.
- Promoted fill-tier sections use permissive trimming, so the strongest non-trimmable mechanism is now soul essence, not markdown preservation.

---

## 3. The Runtime Surface: What The Model Receives

Every prompt returned by `assemble_context()` is seven XML-wrapped layers joined with `\n\n` in this fixed order:

| # | Marker | Layer | Runtime Source |
|---|--------|-------|----------------|
| 1 | `<PERSONA_KERNEL>` | Persona kernel | Soul essence + compiled kernel body + pair soul cards |
| 2 | `<CANON_FACTS>` | Canon facts | `retrieve_memories().canon_facts` |
| 3 | `<MEMORY_FRAGMENTS>` | Episodic memory | `retrieve_memories().episodic_memories` |
| 4 | `<SENSORY_GROUNDING>` | Somatic grounding | `retrieve_memories().somatic_state` + active protocol prose |
| 5 | `<VOICE_DIRECTIVES>` | Voice directives | Pair metadata + optional baseline + selected voice exemplars |
| 6 | `<SCENE_CONTEXT>` | Scene context | Whyze dyads + internal dyads + open loops + knowledge soul cards |
| 7 | `<CONSTRAINTS>` | Terminal constraints | Tier 1 axioms + character pillar + scene-conditional gates |

Layer markers are defined in [assembler.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/assembler.py:30).

### 3.1 Terminal Anchoring

Layer 7 is always last. That is enforced by:

- Layer ordering inside [assemble_context()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/assembler.py:51)
- `AssembledPrompt.is_terminally_anchored` in [types.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/types.py:132)

The structural check is literal: the final prompt must end with `</CONSTRAINTS>`.

---

## 4. Layer 1: Kernel Path (`v7.1.md` -> compiled kernel)

### 4.1 Loading

`KERNEL_PATHS` in [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:18) maps each character ID to candidate kernel paths. `_load_raw_kernel()` at [line 295](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:295) resolves the first existing path and reads it as UTF-8.

`_sanitize_kernel_text()` at [line 117](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:117) removes frontend-only scaffolding such as `# SYSTEM_ROLE:`, `**Version:**`, and `**Target:**`.

### 4.2 Section Parsing

`_parse_kernel_sections()` at [line 134](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:134) splits on `^## (\d+)\.` and returns `(section_number, section_text)` tuples.

All four current kernels use 11 numbered sections:

| Section | Typical Name | Example Evidence |
|---------|--------------|------------------|
| 1 | Runtime Directives | [Adelia_Raye_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Adelia_Raye_v7.1.md:6) |
| 2 | Core Identity | [Bina_Malek_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Bina_Malek_v7.1.md:16) |
| 3 | Whyze / Pair | [Reina_Torres_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Reina_Torres_v7.1.md:41) |
| 4 | Silent Routing | [Alicia_Marin_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Alicia_Marin_v7.1.md:55) |
| 5 | Behavioral Tier Framework | [Adelia_Raye_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Adelia_Raye_v7.1.md:69) |
| 6 | Voice Architecture / Voice Signature | [Alicia_Marin_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Alicia_Marin_v7.1.md:99) |
| 7 | Character-specific framework section | [Reina_Torres_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Reina_Torres_v7.1.md:120) |
| 8 | Intimacy / orientation section | [Bina_Malek_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Bina_Malek_v7.1.md:166) |
| 9 | Family Dynamics | [Adelia_Raye_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Adelia_Raye_v7.1.md:207) |
| 10 | What This Is Not | [Reina_Torres_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Reina_Torres_v7.1.md:240) |
| 11 | Astrological Architecture | [Alicia_Marin_v7.1.md](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Characters/Alicia_Marin_v7.1.md:199) |

### 4.3 Section Budgets and Orders

Baseline section budgets live in `SECTION_TOKEN_TARGETS` at [kernel_loader.py:62](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:62):

| Section | Target Tokens |
|---------|---------------|
| 1 | 300 |
| 2 | 900 |
| 3 | 1000 |
| 4 | 250 |
| 5 | 900 |
| 7 | 550 |
| 6 | 300 |

Assembly orders live at [kernel_loader.py:72-74](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:72):

- `PRIMARY_SECTION_ORDER = [1, 2, 3, 4, 5, 7, 6]`
- `EXPANSION_SECTION_ORDER = [2, 3, 5, 7, 6, 8, 9, 10, 11]`
- `FILL_SECTION_ORDER = [8, 9, 10, 11]`

### 4.4 Scene-Aware Section Promotion

`scene_type_to_promoted_sections()` at [kernel_loader.py:92](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:92) maps `SceneType` to promoted sections:

| SceneType | Promoted Sections |
|-----------|-------------------|
| `DOMESTIC` | 7, 9 |
| `INTIMATE` | 8, 3 |
| `CONFLICT` | 5, 7 |
| `REPAIR` | 8, 9 |
| `PUBLIC` | 10, 5 |
| `GROUP` | 6, 9 |
| `SOLO_PAIR` | 3, 8 |
| `TRANSITION` | none |

Sections already in the primary set stay primary; promotion only changes behavior for fill-tier sections 8-11.

### 4.5 Compilation

`compile_kernel()` at [kernel_loader.py:160](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:160) runs three stages:

1. Baseline allocation to primary sections.
2. Expansion into higher-priority sections while budget remains.
3. Final assembly with strict trimming for original primary sections and permissive trimming for promoted fill-tier sections.

`load_kernel()` at [kernel_loader.py:308](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:308) caches by `(character_id, budget, profile_name, promote_sections)`.

---

## 5. Soul Essence and Soul Cards

### 5.1 Soul Essence

Soul essence is hand-authored Python, not live-loaded markdown. See [soul_essence.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_essence.py:1).

The `SoulEssence` dataclass supports four block families:

- `identity`
- `pair`
- `behavioral`
- `intimacy`

`compile_kernel_with_soul()` at [kernel_loader.py:274](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:274) prepends this content to the compiled kernel body.

Important current-state note:

- The formatter supports all four headings.
- The checked-in essences currently populate `identity` and `pair`.
- `behavioral` and `intimacy` are defined in the type but are presently empty in the concrete registry, so `format_soul_essence()` currently emits only the non-empty sections for each character.

See [format_soul_essence()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_essence.py:865).

### 5.2 Soul Cards

Soul cards are YAML-fronted markdown files under [src/starry_lyfe/canon/soul_cards/](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_cards).

Current directories:

- `pair/` contains one always-on card per character
- `knowledge/` contains scene-conditional cards

Loader and activation code lives in [soul_cards.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/soul_cards.py:65).

Supported activation rules:

| Rule | Fires When |
|------|------------|
| `always: true` | Always active |
| `communication_mode: [...]` | Current communication mode matches |
| `with_character: [...]` | A listed character is present |
| `scene_keyword: [...]` | A listed keyword appears in `scene_state.scene_description` |

Activation is OR-based across rule types: the first matching rule activates the card.

### 5.3 Runtime Wiring

In [assemble_context()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/assembler.py:51):

- Pair cards are formatted and appended to Layer 1.
- Knowledge cards are formatted and appended to Layer 6.
- Token reservations happen before host-layer formatting so these merges do not silently blow past layer ceilings.

---

## 6. Layer 5: Pair Metadata, Baseline, and Voice Exemplars

### 6.1 Pair Metadata

Structured pair metadata lives in [pairs.yaml](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/pairs.yaml:1). The runtime loader is [pairs_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/pairs_loader.py:1).

`format_pair_metadata()` at [pairs_loader.py:87](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/pairs_loader.py:87) currently surfaces six fields:

- `PAIR`
- `CLASSIFICATION`
- `MECHANISM`
- `CORE METAPHOR`
- `WHAT SHE PROVIDES`
- `HOW SHE BREAKS HIS SPIRAL`

`shared_functions` and `cadence` stay in YAML but are intentionally omitted from Layer 5.

### 6.2 Character Baseline

If Phase 2 retrieval returns a `CharacterBaseline`, `format_voice_directives()` also adds a compact metadata paragraph using:

- `full_name`
- `epithet`
- `mbti`
- `dominant_function`
- `pair_name`
- `heritage`
- `profession`
- `voice_params`

Model definition: [character_baseline.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/db/models/character_baseline.py:16)

### 6.3 Voice.md Structure

Voice files are loaded via `VOICE_PATHS` in [kernel_loader.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:33).

Each example block is expected to look like this:

```markdown
## Example 1: Mid-Thought Tangent That Resolves

<!-- mode: domestic, solo_pair -->
<!-- communication_mode: in_person -->

**What it teaches the model:** Teaching prose...

**User:** Prompt text...

**Assistant:** Full response...

**Abbreviated:** First abbreviated line...
Continuation lines are allowed here.
```

Two important parser details:

- `**Abbreviated:**` is not restricted to a single line. `_extract_voice_examples()` continues collecting subsequent non-header lines into the same abbreviated block.
- File-order position is preserved as `index`, so tie-breaks are based on actual file order, not the example number text alone.

Parser entry points:

- [load_voice_guidance()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:399)
- [_extract_voice_examples()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:463)
- [load_voice_examples()](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/kernel_loader.py:568)

### 6.4 Mode-Aware Exemplar Selection

`derive_active_voice_modes()` in [layers.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/layers.py:90) derives the active mode set from `SceneState`.

`_select_voice_exemplars()` at [layers.py:130](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/layers.py:130) then:

1. Filters by `communication_mode`.
2. Keeps examples whose modes overlap the active modes.
3. Ranks by:
   - count of non-`DOMESTIC` overlaps
   - total overlap count
   - file order
4. Returns the top two.
5. Falls back to file-order selection if no mode match survives.

`format_voice_directives()` at [layers.py:337](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/layers.py:337) emits:

- `Voice rhythm exemplars:` when the mode-aware path fires
- `Voice calibration guidance:` when it falls back to the older teaching-note path

### 6.5 VoiceMode Glossary: What The Tags Actually Do

The mode tags are Layer 5 selector metadata, not standalone prompt blocks. They work like this:

- `SceneState` activates one or more `VoiceMode` values through `scene_type`, modifiers, or an explicit `voice_modes` override.
- `_select_voice_exemplars()` then prefers examples whose tags overlap the active set.
- Non-`DOMESTIC` overlaps outrank generic domestic ties, so a specific tag like `warm_refusal` or `group_temperature` beats a generic domestic example when both are available.

| VoiceMode | What It Means In Practice | Typical Activation Path |
|-----------|---------------------------|-------------------------|
| `domestic` | Ordinary household/private baseline. No special pressure, no formal public witness, no explicit conflict requirement. This is the everyday home register. | Default `SceneType.DOMESTIC`; also rides along with `SceneType.SOLO_PAIR` and many two-person fallback scenes |
| `conflict` | Disagreement, veto, friction, challenge, or pushback. The character is resisting, correcting, or forcing a sharper frame. | `SceneType.CONFLICT` or explicit `voice_modes` override |
| `intimate` | Adult romantic, sensual, or high-closeness register. Not automatically explicit sexual content; it is the physical/romantic proximity band. | `SceneType.INTIMATE` or explicit override |
| `public` | Outside-household or witnessed register where discretion matters. The voice stays compatible with public-scene constraints and reduced intimacy surface. | `SceneType.PUBLIC` or legacy `public_scene=True` fallback |
| `group` | Multi-woman room dynamics. The focal woman is contributing inside a group field rather than operating in a one-on-one register. | `SceneType.GROUP` or domestic fallback when more than two characters are present |
| `repair` | Reconciliation, decompression, aftercare, or post-intensity re-regulation. The scene is about settling, mending, or holding the aftermath. | `SceneType.REPAIR` or `post_intensity_crash_active=True` |
| `silent` | Minimal-verbal register. Meaning is carried by stillness, touch, placement, or one short line rather than extended speech. | `SceneType.REPAIR`, `silent_register_active=True`, or explicit override |
| `solo_pair` | Focused one-on-one pair register. The scene is centered on the focal woman and Whyze rather than the group. | `SceneType.SOLO_PAIR`, `SceneType.INTIMATE`, or domestic fallback when exactly two characters are present |
| `escalation` | Deliberate increase in intimate pressure or forward movement. The character is actively advancing the charge of the scene rather than just inhabiting intimacy. | `pair_escalation_active=True` or explicit override |
| `warm_refusal` | Firm boundary held without coldness. The character says no, but the no preserves care, attachment, or professionalism instead of becoming a rupture. | `warm_refusal_required=True` or explicit override |
| `group_temperature` | Group-scene temperature change rather than conversational hub behavior. The character changes the feel of the room without taking over the room. | `group_temperature_shift=True` or explicit override |

Two current-state nuances:

- These modes are not guaranteed to exist in every character's corpus. Coverage depends on what that character's `Voice.md` actually tags.
- As of 2026-04-13, the checked-in Voice.md corpus contains no explicit `public`-tagged exemplars, even though `PUBLIC` is a valid runtime `VoiceMode`. When `PUBLIC` activates without a dedicated public exemplar, the selector now applies a public-safety ranking so Layer 5 prefers non-private examples over intimate, escalation, or solo-pair fallbacks unless a more specific active mode such as `warm_refusal` is explicitly in play.

---

## 7. `SceneState`: The Runtime Control Surface

`SceneState` is defined in [types.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/types.py:92).

### 7.1 Fields

| Field | Primary Effects |
|-------|-----------------|
| `present_characters` | Layer 6 dyad visibility, domestic-context Layer 5 mode accumulation, Layer 7 talk-to-each-other mandate |
| `public_scene` | Public-scene gate in Layer 7, domestic-context `PUBLIC` activation in Layer 5 |
| `alicia_home` | Alicia in-person assembly preflight |
| `scene_description` | Layer 4 and Layer 6 prose, soul-card `scene_keyword` activation |
| `communication_mode` | Layer 5 filtering, Alicia mode-specific constraint pillar, soul-card `communication_mode` activation |
| `recalled_dyads` | Layer 6 absent-dyad inclusion |
| `voice_modes` | Explicit VoiceMode override |
| `scene_type` | Layer 1 section promotion and Layer 5 mode derivation |
| `modifiers` | Layer 5 additive modes, Layer 6 absent-dyad override, Layer 7 conditional gates |

### 7.2 SceneType -> VoiceMode

`_SCENE_TYPE_VOICE_MODES` lives at [layers.py:52](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/layers.py:52):

| SceneType | Active VoiceModes |
|-----------|-------------------|
| `DOMESTIC` | `DOMESTIC` |
| `INTIMATE` | `INTIMATE`, `SOLO_PAIR` |
| `CONFLICT` | `CONFLICT` |
| `REPAIR` | `REPAIR`, `SILENT` |
| `PUBLIC` | `PUBLIC` |
| `GROUP` | `GROUP` |
| `SOLO_PAIR` | `SOLO_PAIR`, `DOMESTIC` |
| `TRANSITION` | `DOMESTIC` |

### 7.3 Modifier -> VoiceMode Accumulation

These stack on top of the `scene_type` result:

| Modifier | Adds |
|----------|------|
| `pair_escalation_active` | `ESCALATION` |
| `warm_refusal_required` | `WARM_REFUSAL` |
| `silent_register_active` | `SILENT` |
| `group_temperature_shift` | `GROUP_TEMPERATURE` |
| `post_intensity_crash_active` | `REPAIR` |

### 7.4 Modifier -> Layer 7 Effects

Layer 7 injections come from [constraints.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/constraints.py:102):

| Modifier / Field | Effect |
|------------------|--------|
| `public_scene` or `work_colleagues_present` | Public-scene gate |
| `post_intensity_crash_active` | Character-specific crash protocol |
| `pair_escalation_active` | Admissibility protocol |
| `communication_mode` for Alicia | Phone / letter / video-specific pillar |

### 7.5 Legacy Domestic Fallback

When:

- `voice_modes` is `None`
- `scene_type == DOMESTIC`
- no modifiers are active

`derive_active_voice_modes()` falls back to domestic-context cues:

- add `PUBLIC` if `public_scene=True`
- add `SOLO_PAIR` when exactly 2 characters are present
- add `GROUP` when more than 2 are present

That preserves older callers that still rely on `present_characters` and `public_scene` rather than explicit `scene_type`.

### 7.6 Phase 5: Scene Director Produces `SceneState` Automatically

Until Phase 5 every caller manually constructed a `SceneState` from raw inputs. The **Scene Director** at `src/starry_lyfe/scene/` is the production front door that turns caller inputs into a `SceneState` ready for `assemble_context()`.

```python
from starry_lyfe.scene import classify_scene, SceneDirectorInput

scene_state = classify_scene(
    SceneDirectorInput(
        user_message="adelia and bina are in the kitchen making dinner",
        present_characters=["adelia", "bina", "whyze"],  # Whyze-included convention
        alicia_home=True,
    )
)
# scene_state.present_characters is ["adelia", "bina", "whyze"] and is ready
# for assemble_context(). If the caller omits "whyze", the classifier
# auto-appends it so downstream Layer 5 mode accumulation counts correctly.
```

The classifier is rule-based — keyword tables for `CommunicationMode`, `SceneType`, and each of the seven `SceneModifiers` flags. Hints (`SceneDirectorHints`) always win over inference for callers that already know the answer (HTTP UI, tests).

**Absent-dyad normalization:** when the message invokes an absent woman (e.g., "thinking about reina"), the modifier field `explicitly_invoked_absent_dyad` records the bare name, and `SceneState.recalled_dyads` is populated with the dyad-key shape `"<present_woman>-<absent_name>"` that Layer 6's `format_scene_blocks()` reads at `src/starry_lyfe/context/layers.py:535-541`.

For Crew Conversations, `select_next_speaker(speaker_input)` scores present women per the Talk-to-Each-Other Mandate (Vision §6, §7), Rule of One, dyad-state fitness (memory tier 4), and narrative salience. The narrative-salience rule reads `scene_state.scene_description` and the optional `speaker_input.activity_context` (Phase 6 Dreams-sourced) — a candidate named in either receives a small score boost. Dyad state is injected via a `DyadStateProvider` Protocol — the production wiring uses `build_dyad_state_provider(rows)` to wrap a list returned by `_retrieve_internal_dyads()`.

See [`Docs/_phases/PHASE_5.md`](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/PHASE_5.md) for the full design (rules, weights, deferred items, known limitations).

| Symbol | File:line |
|--------|-----------|
| `classify_scene()` | `src/starry_lyfe/scene/classifier.py:120` |
| `select_next_speaker()` | `src/starry_lyfe/scene/next_speaker.py:115` |
| `AliciaAwayContradictionError` | `src/starry_lyfe/scene/errors.py:6` |
| `DyadStateProvider` Protocol | `src/starry_lyfe/scene/next_speaker.py:56` |
| `build_dyad_state_provider()` | `src/starry_lyfe/scene/next_speaker.py:271` |

---

## 8. Budgeting

### 8.1 Default Layer Budgets

`DEFAULT_BUDGETS` lives at [budgets.py:56](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/budgets.py:56):

| Layer | Budget |
|-------|--------|
| 1 kernel | 6000 |
| 2 canon facts | 600 |
| 3 episodic | 1200 |
| 4 somatic | 500 |
| 5 voice | 900 |
| 6 scene | 2400 |
| 7 constraints | 900 |

### 8.2 Scene Profiles

`SCENE_PROFILES` lives at [budgets.py:90](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/budgets.py:90):

| Profile | Kernel | Scene | Voice |
|---------|--------|-------|-------|
| `default` | 6000 | 2400 | 900 |
| `pair_intimate` | 8000 | 1800 | 700 |
| `multi_woman_group` | 5500 | 3200 | 1000 |
| `solo` | 7000 | 1800 | 900 |

### 8.3 Per-Character Kernel Scaling

`resolve_kernel_budget()` at [budgets.py:66](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/budgets.py:66) applies:

| Character | Multiplier | From base 6000 |
|-----------|------------|----------------|
| Adelia | 1.05 | 6300 |
| Bina | 1.20 | 7200 |
| Reina | 1.15 | 6900 |
| Alicia | 0.85 | 5100 |

### 8.4 Soul-Essence Surcharge

Soul essence is outside the trimmable kernel budget. The actual current surcharge can be inspected with `soul_essence_token_estimate()` at [soul_essence.py:874](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/canon/soul_essence.py:874).

As of 2026-04-13, the checked-in estimates are:

| Character | Soul Essence Tokens |
|-----------|---------------------|
| Adelia | 1886 |
| Bina | 1876 |
| Reina | 1701 |
| Alicia | 2112 |

### 8.5 Trimming

`trim_text_to_budget()` lives at [budgets.py:406](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/budgets.py:406).

Drop strategy:

1. Remove horizontal rules.
2. Remove trailing content blocks.
3. Remove trailing `h3` sections.
4. Remove trailing `h2` sections.
5. Fall back to word-level trimming when not in strict mode.

Strict mode is used for core kernel compilation. Promoted fill-tier sections use permissive trimming.

---

## 9. End-to-End Flow (`assemble_context()`)

Entry point: [assembler.py:51](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/src/starry_lyfe/context/assembler.py:51)

Signature:

```python
assemble_context(
    character_id,
    scene_context,
    scene_state,
    session,
    embedding_service,
    canon=None,
    scene_profile="default",
)
```

Two inputs are easy to confuse:

- `scene_context`: retrieval query text passed into `retrieve_memories()`
- `scene_state.scene_description`: descriptive scene text used by Layer 4, Layer 6, and soul-card keyword activation

Runtime sequence:

1. Load canon if the caller did not pass it.
2. If Alicia is being assembled for an in-person scene while `alicia_home=False`, raise `AliciaAwayError`.
3. Call `retrieve_memories()` for canon facts, baseline, dyads, episodic memories, open loops, and somatic state.
4. Resolve the scene budget profile and per-character kernel scaling.
5. Activate soul cards and split them into pair cards and knowledge cards.
6. Reserve token space for those card bodies.
7. Build Layer 1 through Layer 6.
8. Merge pair cards into Layer 1 and knowledge cards into Layer 6.
9. Build Layer 7 from `build_constraint_block(character_id, scene_state)`.
10. XML-wrap all seven layers and join them with `\n\n`.
11. Return `AssembledPrompt(prompt, character_id, layers, total_tokens, constraint_block_position)`.

---

## 10. Reference Map

| Concern | File | Symbol | Line |
|---------|------|--------|------|
| Kernel paths | `src/starry_lyfe/context/kernel_loader.py` | `KERNEL_PATHS` | 18 |
| Voice paths | `src/starry_lyfe/context/kernel_loader.py` | `VOICE_PATHS` | 37 |
| Section budgets | `src/starry_lyfe/context/kernel_loader.py` | `SECTION_TOKEN_TARGETS` | 62 |
| Section orders | `src/starry_lyfe/context/kernel_loader.py` | `PRIMARY_SECTION_ORDER` / `EXPANSION_SECTION_ORDER` / `FILL_SECTION_ORDER` | 72-74 |
| Scene promotion map | `src/starry_lyfe/context/kernel_loader.py` | `scene_type_to_promoted_sections()` | 92 |
| Kernel compilation | `src/starry_lyfe/context/kernel_loader.py` | `compile_kernel()` | 160 |
| Soul-wrapped kernel | `src/starry_lyfe/context/kernel_loader.py` | `compile_kernel_with_soul()` | 274 |
| Kernel cache entry | `src/starry_lyfe/context/kernel_loader.py` | `load_kernel()` | 308 |
| Legacy voice-guidance parse | `src/starry_lyfe/context/kernel_loader.py` | `load_voice_guidance()` | 409 |
| Structured voice-example parse | `src/starry_lyfe/context/kernel_loader.py` | `_extract_voice_examples()` | 487 |
| Voice-example cache | `src/starry_lyfe/context/kernel_loader.py` | `load_voice_examples()` | 592 |
| Soul essence formatter | `src/starry_lyfe/canon/soul_essence.py` | `format_soul_essence()` | 865 |
| Soul essence estimate | `src/starry_lyfe/canon/soul_essence.py` | `soul_essence_token_estimate()` | 905 |
| Pair metadata load | `src/starry_lyfe/canon/pairs_loader.py` | `get_pair_metadata()` | 91 |
| Pair metadata format | `src/starry_lyfe/canon/pairs_loader.py` | `format_pair_metadata()` | 102 |
| Soul-card load | `src/starry_lyfe/context/soul_cards.py` | `load_soul_card()` | 65 |
| Soul-card activation | `src/starry_lyfe/context/soul_cards.py` | `find_activated_cards()` | 100 |
| Soul-card format | `src/starry_lyfe/context/soul_cards.py` | `format_soul_cards()` | 142 |
| Voice-mode derivation | `src/starry_lyfe/context/layers.py` | `derive_active_voice_modes()` | 101 |
| Exemplar ranking | `src/starry_lyfe/context/layers.py` | `_select_voice_exemplars()` | 141 |
| Layer 1 formatter | `src/starry_lyfe/context/layers.py` | `format_kernel()` | 284 |
| Layer 5 formatter | `src/starry_lyfe/context/layers.py` | `format_voice_directives()` | 397 |
| Layer 6 formatter | `src/starry_lyfe/context/layers.py` | `format_scene_blocks()` | 508 |
| Layer 7 builder | `src/starry_lyfe/context/constraints.py` | `build_constraint_block()` | 104 |
| Layer markers | `src/starry_lyfe/context/assembler.py` | `LAYER_MARKERS` | 35 |
| Assembler entry | `src/starry_lyfe/context/assembler.py` | `assemble_context()` | 56 |
| Communication mode enum | `src/starry_lyfe/context/types.py` | `CommunicationMode` | 9 |
| Scene type enum | `src/starry_lyfe/context/types.py` | `SceneType` | 18 |
| Scene modifiers | `src/starry_lyfe/context/types.py` | `SceneModifiers` | 37 |
| Voice modes | `src/starry_lyfe/context/types.py` | `VoiceMode` | 55 |
| Scene state | `src/starry_lyfe/context/types.py` | `SceneState` | 93 |
| Terminal-anchor check | `src/starry_lyfe/context/types.py` | `AssembledPrompt.is_terminally_anchored` | 132 |
| Default budgets | `src/starry_lyfe/context/budgets.py` | `DEFAULT_BUDGETS` | 61 |
| Per-character scaling | `src/starry_lyfe/context/budgets.py` | `resolve_kernel_budget()` | 74 |
| Scene profiles | `src/starry_lyfe/context/budgets.py` | `SCENE_PROFILES` | 98 |
| Budget trimmer | `src/starry_lyfe/context/budgets.py` | `trim_text_to_budget()` | 414 |
| Soul essence raise | `src/starry_lyfe/canon/soul_essence.py` | `SoulEssenceNotFoundError` | 27 |
| Canon validation raise | `src/starry_lyfe/canon/loader.py` | `CanonValidationError` | 81 |
| Canonical character ID | `src/starry_lyfe/canon/schemas/enums.py` | `CharacterID` | 21 |
| Character lookup raise | `src/starry_lyfe/canon/schemas/enums.py` | `CharacterNotFoundError` | 7 |
| Coverage assertion helper | `src/starry_lyfe/canon/schemas/enums.py` | `_assert_complete_character_keys()` | 41 |
| Fidelity rubric type | `src/starry_lyfe/validation/fidelity.py` | `FidelityRubric` | 41 |
| Fidelity scoring entry | `src/starry_lyfe/validation/fidelity.py` | `score_rubric()` | 152 |

---

## 11. Observability and Sample Artifacts

### 11.1 DEBUG Logging

`_select_voice_exemplars()` emits DEBUG logs from `starry_lyfe.context.layers` with keys such as:

- `character_id`
- `active_modes`
- `candidates_count`
- `mode_matched_count`
- `selected_titles`

The steady-state event is `voice_exemplar_selection`; fallback branches emit explicit fallback variants.

### 11.2 Canonical Sample Prompts

Current checked-in sample prompts live in [Docs/_phases/_samples](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/Docs/_phases/_samples).

Useful sets:

- `PHASE_B_assembled_*` for budget-elevated Layer 1 behavior
- `PHASE_C_assembled_*` for soul-card activation
- `PHASE_D_assembled_*` for pair metadata in Layer 5
- `PHASE_E_assembled_*` for mode-aware voice exemplars
- `PHASE_F_assembled_*` for section promotion and full VoiceMode reachability

### 11.3 Regeneration Scripts

Checked-in sample regeneration scripts:

- [scripts/generate_phase_e_samples.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/scripts/generate_phase_e_samples.py:1)
- [scripts/generate_phase_f_samples.py](/C:/Users/Whyze/OneDrive/Cosmology/0_ARCHE/0.4_FOUNDRY/Starry-Lyfe/scripts/generate_phase_f_samples.py:1)

These are not production codepaths. They are probe harnesses that call the real assembler with local canonical sample data standing in for PostgreSQL retrieval.

---

## 12. What This Guide Does Not Cover

| Topic | See |
|-------|-----|
| Phase history and audit trail | `Docs/_phases/PHASE_*.md` |
| Tier-framework doctrine | `Docs/Persona_Tier_Framework_v7.1.md` |
| Backend vs Msty voice authority split | `Docs/ADR_001_Voice_Authority_Split.md` |
| Msty few-shot seeding | `scripts/seed_msty_persona_studio.py` |
| Retrieval implementation details | `src/starry_lyfe/db/retrieval.py` |
| Canonical phase and subsystem status | `Docs/IMPLEMENTATION_PLAN_v7.1.md` |
| Module and schema index | `Docs/ARCHITECTURE.md` |

---

## 13. Dreams Engine (Phase 6)

The Dreams Engine is the nightly batch life-simulation process that gives the characters lives between sessions. It is the only execution surface without a user in the loop: all other backend subsystems are reactive to a Whyze message; Dreams runs autonomously overnight.

Master plan reference: `Docs/IMPLEMENTATION_PLAN_v7.1.md` §9. Full phase record: `Docs/_phases/PHASE_6.md`.

### 13.1 Public API

```python
from starry_lyfe.dreams import run_dreams_pass, DreamsSettings, BDOne, StubBDOne
from starry_lyfe.canon.loader import load_all_canon

canon = load_all_canon()  # includes new canon.routines field
llm_client = BDOne(BDOneSettings.from_env())  # or StubBDOne() for tests

result = await run_dreams_pass(
    session_factory=my_session_factory,
    llm_client=llm_client,
    canon=canon,
)
```

`run_dreams_pass()` at `src/starry_lyfe/dreams/runner.py:65` iterates all 4 canonical characters via `CharacterID.all_strings()` with `_assert_complete_character_keys()` coverage invariant on the result. Per character: fetch session snapshot → run 5 generators → aggregate warnings and token counts.

### 13.2 CLI

```
# Start the apscheduler daemon (nightly at 03:30 local by default):
python -m starry_lyfe.dreams

# Run one pass and exit (smoke test or manual catch-up):
python -m starry_lyfe.dreams --once

# Dry-run with StubBDOne (no LLM calls, no DB writes):
python -m starry_lyfe.dreams --once --dry-run
```

Entry point: `src/starry_lyfe/dreams/daemon.py:main()`.

### 13.3 Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `STARRY_LYFE__DREAMS__SCHEDULE` | `"30 3 * * *"` | Cron expression for the nightly run |
| `STARRY_LYFE__DREAMS__ENABLED` | `true` | Ops kill-switch for the scheduler loop |
| `STARRY_LYFE__DREAMS__DRY_RUN` | `false` | Skip DB writes |
| `STARRY_LYFE__DREAMS__MAX_TOKENS_PER_CHAR` | `8000` | Aggregate per-character LLM token budget |
| `STARRY_LYFE__DREAMS__MISFIRE_GRACE_S` | `3600` | apscheduler catch-up window after missed fire |
| `STARRY_LYFE__DREAMS__LLM_MODEL` | `anthropic/claude-sonnet-4-6` | Model passed to BDOne |
| `STARRY_LYFE__BD1__BASE_URL` | `https://openrouter.ai/api/v1` | LLM endpoint |
| `STARRY_LYFE__BD1__API_KEY` | `""` | OpenRouter / Anthropic API key |
| `STARRY_LYFE__BD1__TIMEOUT` | `60` | Per-call timeout (seconds) |
| `STARRY_LYFE__BD1__MAX_RETRIES` | `3` | Retries before circuit-break |
| `STARRY_LYFE__BD1__CIRCUIT_THRESHOLD` | `5` | Consecutive failures before circuit opens |

### 13.4 Retroactive soul-preservation wiring

Dreams output passes through three retroactive invariants:

- **Phase G (prose rendering):** every narrative text from a generator routes through a per-character prose renderer before being returned. Diary entries use `render_diary_prose(character_id, raw_content)` at `src/starry_lyfe/context/prose.py` — wraps raw LLM text in a three-paragraph opener/body/closer frame matched to the character's voice register.
- **Phase A'' (Alicia-away tagging):** when Alicia's `life_state.is_away=True`, Dreams generators tag emitted artifacts with `communication_mode ∈ {phone, letter, video_call}` sampled from the canonical `alicia_communication_distribution` (0.45 / 0.20 / 0.35) in `routines.yaml`. The `episodic_memories` and `activities` tables carry a nullable `communication_mode` column (Alembic migration 003).
- **Phase H (regression bundle):** `tests/unit/dreams/test_dreams_regression_per_character.py` runs parametrized regressions across all 4 characters — opener presence, cross-character contamination negatives, 3-paragraph structure, Alicia-away comm-mode invariants.

### 13.5 Consolidation invariants

- **Somatic decay:** `refresh_somatic_decay(session, character_id, now)` at `src/starry_lyfe/dreams/consolidation.py` applies exponential decay via the existing `apply_decay()` helper; updates `last_decayed_at`.
- **Dyad delta cap:** `apply_overnight_dyad_deltas()` caps per-dimension deltas at **±0.10 per Dreams pass** (vs. ±0.03 per-turn runtime per `evaluate_and_update`). Over-cap requests are clamped with a warning logged.
- **Loop expiry:** `expire_stale_loops(session, now)` transitions `open_loops.status` from `"open"` to `"expired"` when `expires_at < now`.
- **Loop resolution:** `resolve_addressed_loops(session, character_id, loop_ids, now)` marks addressed loops as `resolved_by="dreams"`.

### 13.6 File:line reference for key symbols

| Symbol | File:line |
|--------|-----------|
| `run_dreams_pass()` | `src/starry_lyfe/dreams/runner.py:65` |
| `DreamsSettings` / `.from_env()` | `src/starry_lyfe/dreams/config.py:22` |
| `BDOne` / `StubBDOne` | `src/starry_lyfe/dreams/llm.py:96` / `:208` |
| `generate_diary()` | `src/starry_lyfe/dreams/generators/diary.py:89` |
| `generate_schedule()` | `src/starry_lyfe/dreams/generators/schedule.py:16` |
| `pick_alicia_communication_mode()` | `src/starry_lyfe/dreams/alicia_mode.py:20` |
| `render_diary_prose()` | `src/starry_lyfe/context/prose.py:502` |
| `refresh_somatic_decay()` / `apply_overnight_dyad_deltas()` | `src/starry_lyfe/dreams/consolidation.py:57` / `:156` |
| Alembic migrations | `alembic/versions/002_phase_6_dreams_tables.py`, `003_phase_6_episodic_comm_mode.py` |

---

## 14. HTTP Service (Phase 7)

The HTTP service exposes the Starry-Lyfe backend on **port 8001** as an OpenAI-compatible chat API. Consumed by Msty AI (direct). SHIPPED 2026-04-15.

### 14.1 Boot

```
python -m starry_lyfe.api
```

`starry_lyfe.api.__main__` invokes `main.py::main()`, which loads `ApiSettings` from environment, builds the FastAPI app via `create_app()`, and starts uvicorn on the configured host/port. Lifespan startup builds the canon, DB engine + session factory, embedding service, and BD-1 client; shutdown disposes the engine.

### 14.2 Environment variables

| Variable | Default | Required? |
|----------|---------|-----------|
| `STARRY_LYFE__API__HOST` | `0.0.0.0` | no |
| `STARRY_LYFE__API__PORT` | `8001` | no |
| `STARRY_LYFE__API__API_KEY` | `""` | yes (or chat 401s) |
| `STARRY_LYFE__API__CORS_ORIGINS` | `""` (no CORS) | no — comma-separated list |
| `STARRY_LYFE__API__DEFAULT_CHARACTER` | `adelia` | no — must be a canonical character |
| `STARRY_LYFE__API__HEALTH_BD1_PROBE` | `true` | no — F3 closure 2026-04-15. When true, `/health/ready` issues a live HEAD probe against the BD-1 provider URL (1.5s timeout). Set `false` to skip the network call. |
| `STARRY_LYFE__API__CREW_MAX_SPEAKERS` | `3` | no — F1 closure 2026-04-15. Crew-mode multi-speaker cap (project axiom: "Max 3 choices per decision point"). |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM` | `true` | no — Phase 8 2026-04-15. When true, the post-turn relationship evaluator uses BD-1 as its primary delta-proposal source; heuristic `_propose_deltas` runs only as fallback. Set `false` to force the heuristic path (offline dev / test environments). |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_MAX_TOKENS` | `200` | no — Phase 8. `max_tokens` passed to `BDOne.complete()` for the relationship evaluation call. 200 is enough for the required 4-field JSON response + minimal slack. |
| `STARRY_LYFE__API__RELATIONSHIP_EVAL_TEMPERATURE` | `0.2` | no — Phase 8. Low temperature keeps evaluator output stable across runs. The ±0.03 cap absorbs residual noise regardless. |
| `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM` | `true` | no — Phase 9 2026-04-15. When true, the post-turn inter-woman dyad evaluator (`evaluate_and_update_internal`) uses BD-1 as its primary delta-proposal source for each active `DyadStateInternal` row the focal character is a member of; heuristic `_propose_internal_deltas` runs only as fallback. Set `false` to force the heuristic path (offline dev / test environments). The ±0.03 cap and Alicia-orbital active-gate apply identically either way. Reuses the Phase 8 `relationship_eval_max_tokens` + `relationship_eval_temperature` settings — Phase 9 does not introduce its own size/temperature knobs. |

### 14.3 Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET    | `/health/live` | Liveness probe (always 200) | None |
| GET    | `/health/ready` | DB + BD-1 reachability (200/503 with structured `checks` body) | None |
| GET    | `/v1/models` | 5 OpenAI-compatible entries | None |
| POST   | `/v1/chat/completions` | OpenAI-compatible SSE streaming chat | `X-API-Key` |
| GET    | `/metrics` | Prometheus exposition | None |

### 14.4 Character routing priority

`api/routing/character.py::resolve_character_id` resolves the focal character in this order:

1. `model` field matching a canonical id — **the Msty production path**. Msty Studio sends the active Persona's model name (`adelia`, `bina`, `reina`, `alicia`) in the `model` field of every request. Characters are always loaded through Personas in Msty, never through headers. Multi-character (Crew) conversations are handled by Msty Crew Mode — see §14.9.
2. Inline `/<char>` or `/all` override at user message start — dev/test convenience.
3. `X-SC-Force-Character` header — dev/test override only. Not used in production Msty. Useful for `curl`, observability dashboards, and non-Msty clients.
4. `STARRY_LYFE__API__DEFAULT_CHARACTER` (default `adelia`) — fallback when no character is identifiable from any of the above.

Returns a frozen `CharacterRoutingDecision` with `source` audit field (`model_field` | `inline_override` | `header` | `default`). Unknown character IDs raise `CharacterNotFoundError` → 400 with `valid_character_ids` in the body.

### 14.4.1 Cost envelope (Phase 8 — 2026-04-15; Phase 9 update — 2026-04-15)

The Whyze-dyad relationship evaluator (Step 12 below) issues one additional `BDOne.complete()` call per chat turn. At the default `relationship_eval_max_tokens=200` + `relationship_eval_temperature=0.2`, the round-trip averages ~300 tokens (prompt + response). Because the evaluator runs as `asyncio.create_task` after the SSE close (fire-and-forget), it does NOT contribute to user-visible latency. It DOES contribute to BD-1 request volume: at N chat turns/day, expect ~N extra evaluator calls/day. Set `STARRY_LYFE__API__RELATIONSHIP_EVAL_LLM=false` to suppress the extra traffic and force the heuristic path; the ±0.03 cap semantics are identical either way.

**Phase 9 inter-woman fan-out (added 2026-04-15).** A second evaluator (`evaluate_and_update_internal`) runs as a third fire-and-forget task per turn. It selects all `DyadStateInternal` rows where the focal character is `member_a` or `member_b` AND `is_currently_active = true`, then issues one `BDOne.complete()` call per active inter-woman dyad. Per-character ceiling (Alicia home): up to **3** extra calls per turn (e.g., an Adelia turn fans out to adelia×bina + adelia×reina + adelia×alicia). With Alicia on operational travel (orbital dyads dormant via Tier 8 `life_states`), the fan-out drops to **2** for resident-continuous focal characters and **0** for Alicia herself. Across a single Crew turn with 3 speakers: maximum 9 extra calls (3 speakers × 3 active dyads), down to 6 with Alicia away. Set `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM=false` to suppress the inter-woman fan-out and force the heuristic path; the ±0.03 cap and Alicia-orbital gate apply identically either way. The Whyze-dyad evaluator and the inter-woman evaluator are independently togglable.

### 14.5 12-step request flow (debugging)

| # | Step | Where to look |
|---|------|---------------|
| 1 | POST received | `api/endpoints/chat.py::chat_completions` (request log + X-Request-ID header) |
| 2 | Msty preprocess + scene classify | `api/routing/msty.py::preprocess_msty_request` + `scene/classify_scene` |
| 2a | Resolve `alicia_home` from Tier 8 `life_states` | `db/retrieval.py::retrieve_alicia_home` (F2 closure 2026-04-15; defaults to True when row absent) |
| 3 | Memory retrieval | `db/retrieval.py::retrieve_memories` called at pipeline boundary so the `MemoryBundle` is shared between assembler and Crew loop |
| 4-5 | 7-layer prompt assembly | `context/assembler.py::assemble_context` (Layer 6 includes Tier 8 Dreams activities); optional `memory_bundle=` kwarg skips the internal fetch |
| 6-7 | LLM stream | `dreams/llm.py::BDOne.stream_complete` (single-speaker path) |
| 8 | Whyze-Byte validation | `validation/whyze_byte.py::validate_response` (Tier 1 FAIL emits terminal error chunk) |
| 9 | Crew sequencing (F1 closure 2026-04-15; R2-F1 carry-forward closure 2026-04-15; direct R3-F1 hardening 2026-04-15) | `api/orchestration/pipeline.py::_run_crew_turn` — loops `select_next_speaker()` up to `crew_max_speakers` times when `_is_crew_mode(ctx)` fires. Multi-speaker SSE uses inline `**Name:** ` attribution between speakers. Each speaker after the first receives the earlier speakers' validated text as a `[Earlier this turn: …]` block prepended to their `user_prompt` via `_format_crew_prior_block`, so speaker B can respond to speaker A rather than generate in isolation (the "prevents NPC Competition collapse" contract from `IMPLEMENTATION_PLAN §7`). If a prior speaker trips a Whyze-Byte FAIL, that speaker's text is not carried forward. |
| 10 | SSE response | `api/orchestration/pipeline.py::run_chat_pipeline` (`StreamingResponse`) |
| 12 | Post-turn fire-and-forget (Phase 8 closure 2026-04-15; Phase 9 fan-out 2026-04-15) | `api/orchestration/post_turn.py::schedule_post_turn_tasks` schedules **three** detached coroutines: (a) episodic memory extraction via `memory_extraction.py::extract_episodic`, (b) Whyze-dyad relationship evaluation via `relationship.py::evaluate_and_update`, and (c) inter-woman dyad evaluation via `internal_relationship.py::evaluate_and_update_internal`. The Whyze-dyad evaluator is LLM-primary by default — builds a canonical 4-dimension prompt via `relationship_prompts.py::build_eval_prompt`, calls `BDOne.complete()`, parses the JSON response through `parse_eval_response`, and applies the proposal through the existing ±0.03 `_clamp_delta` gate. Falls back to heuristic `_propose_deltas` on any of five conditions: `relationship_eval_llm=false` toggle, missing llm_client, circuit-breaker open, `DreamsLLMError`, parser returning None. Structured log events: `llm_eval_parsed_proposal` on success (includes all four delta values), `llm_eval_fallback_to_heuristic` on fallback (includes the `reason` field). The inter-woman evaluator (Phase 9) does the same work for the focal character's active `DyadStateInternal` rows, fanning out one `BDOne.complete()` call per active dyad with the 5-dimension `InternalRelationshipEvalResponse` schema (adds `conflict` to Phase 8's 4 dimensions). Alicia-orbital gate enforced at the SQL boundary via `is_currently_active.is_(True)`. Toggle: `STARRY_LYFE__API__INTERNAL_RELATIONSHIP_EVAL_LLM=false`. Structured log events: `internal_llm_eval_parsed_proposal` and `internal_llm_eval_fallback_to_heuristic`. |

Response headers for observability:
- `X-Request-ID` (correlate with MSE-6 logs)
- `X-Character-ID` (focal character)
- `X-Routing-Source` (`header|inline_override|model_field|default`)
- `X-Session-ID` (chat_sessions row id)

### 14.6 Curl reference

```bash
# Health
curl -s http://localhost:8001/health/live | jq
curl -s http://localhost:8001/health/ready | jq

# Models registry
curl -s http://localhost:8001/v1/models | jq

# SSE streaming chat
curl -N -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $STARRY_LYFE__API__API_KEY" \
  -d '{"model":"adelia","messages":[{"role":"user","content":"morning"}],"stream":true}'

# Force-character via header (dev/test only — not the Msty production path)
curl -N -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $STARRY_LYFE__API__API_KEY" \
  -H "X-SC-Force-Character: bina" \
  -d '{"model":"starry-lyfe","messages":[{"role":"user","content":"hi"}],"stream":true}'

# Prometheus scrape
curl -s http://localhost:8001/metrics | head -30
```

### 14.7 Prometheus series

| Series | Type | Labels |
|--------|------|--------|
| `http_requests_total` | counter | `method`, `path`, `status` |
| `http_chat_completions_total` | counter | `character_id`, `routing_source`, `outcome` |
| `http_sse_tokens_total` | counter | `character_id` — counts upstream **LLM stream deltas**, not tokens. Label semantics: focal character in single-speaker mode, actual speaker in Crew mode. Name retained for Prometheus series stability. |
| `http_request_duration_seconds` | histogram | `method`, `path` |
| `http_chat_ttfb_seconds` | histogram | `character_id` |

### 14.9 Msty Studio Integration Architecture

Msty is the only consumer of this backend. Two Msty features map to two distinct backend paths.

#### Single-character: Persona Conversations

Each character has a dedicated Persona in Msty's Persona Studio:

| Msty Persona | System Prompt Mode | System Prompt Content | model field |
|---|---|---|---|
| Adelia Raye | Replace | Blank (backend is voice authority per ADR-001) | `adelia` |
| Bina Malek | Replace | Blank | `bina` |
| Reina Torres | Replace | Blank | `reina` |
| Alicia Marin | Replace | Blank | `alicia` |

When a user opens a Persona Conversation, Msty sends `model: "<character-id>"` to `/v1/chat/completions`. The backend reads the `model` field, assembles the seven-layer prompt for that character, generates the response, and validates it through Whyze-Byte. The character's voice, memory, and constraints are entirely backend-sourced — the blank Msty system prompt is the production invariant, enforced by ADR-001.

The `# SYSTEM_ROLE:` header line in each kernel file (e.g., `# SYSTEM_ROLE: Adelia RAYE (The Catalyst)`) is a Msty Persona Studio authoring artifact. At runtime `_sanitize_kernel_text()` in `kernel_loader.py` strips it along with `**Version:**` and `**Target:**` before the kernel reaches the model. It never appears in the assembled prompt.

#### Multi-character: Crew Conversations

Crew Mode is Msty's multi-persona feature. A Crew is a named group of Personas. When a Crew Conversation is active:

1. Msty manages the turn-taking UI and sends the full message history to the backend with each request.
2. Prior speaker turns arrive as `role="assistant"` messages with a `name` field set to the persona id (e.g., `name: "adelia"`). The Msty system prompt may carry a roster header naming the active crew members.
3. `preprocess_msty_request()` in `api/routing/msty.py` narrows this wide payload: it extracts the scene roster (`scene_characters`), the prior persona responses (`prior_responses`), and the latest user message. The system prompt is stripped per ADR-001.
4. The backend's `select_next_speaker()` (Phase 5 Scene Director) scores which woman should speak next based on the Talk-to-Each-Other Mandate, Rule of One, dyad-state fitness, and narrative salience.
5. `_run_crew_turn()` in `pipeline.py` loops up to `CREW_MAX_SPEAKERS` times, streaming each speaker's turn inline with `**Name:** ` attribution. Each speaker after the first receives the validated text of earlier speakers as a `[Earlier this turn: …]` block, so speaker B can actually respond to speaker A.

Characters are never "forced" into a Crew by headers. The Crew roster is assembled in Msty by the operator choosing which Personas belong to the Crew.

#### `SYSTEM_ROLE` headers are Persona Studio artifacts, not runtime directives

The `# SYSTEM_ROLE:` lines at the top of each kernel file are Msty Persona Studio display labels — they appear in the Persona authoring UI and are stripped at runtime. They are not HTTP headers. They are not injected into the assembled prompt. Operators editing kernels do not need to preserve them; they exist only for Msty's UI display layer.

#### File:line reference for Msty integration

| Symbol | File:line |
|--------|-----------|
| `preprocess_msty_request()` | `src/starry_lyfe/api/routing/msty.py:88` |
| `MstyPreprocessed` | `src/starry_lyfe/api/routing/msty.py:45` |
| `resolve_character_id()` | `src/starry_lyfe/api/routing/character.py:60` |
| `_sanitize_kernel_text()` | `src/starry_lyfe/context/kernel_loader.py:117` |
| `_run_crew_turn()` | `src/starry_lyfe/api/orchestration/pipeline.py` |
| `select_next_speaker()` | `src/starry_lyfe/scene/next_speaker.py:115` |
| ADR-001 (voice authority) | `Docs/ADR_001_Voice_Authority_Split.md` |

---



| Symbol | File:line |
|--------|-----------|
| `create_app()` | `src/starry_lyfe/api/app.py:43` |
| `main()` (uvicorn entry) | `src/starry_lyfe/api/main.py:14` |
| `ApiSettings` | `src/starry_lyfe/api/config.py:9` |
| `resolve_character_id()` | `src/starry_lyfe/api/routing/character.py:60` |
| `CharacterRoutingDecision` | `src/starry_lyfe/api/routing/character.py:39` |
| `preprocess_msty_request()` | `src/starry_lyfe/api/routing/msty.py:88` |
| `chat_completions()` endpoint | `src/starry_lyfe/api/endpoints/chat.py:94` |
| `run_chat_pipeline()` | `src/starry_lyfe/api/orchestration/pipeline.py:135` |
| `upsert_session()` | `src/starry_lyfe/api/orchestration/session.py:21` |
| `extract_episodic()` | `src/starry_lyfe/api/orchestration/memory_extraction.py:79` |
| `evaluate_and_update()` | `src/starry_lyfe/api/orchestration/relationship.py:97` |
| `schedule_post_turn_tasks()` | `src/starry_lyfe/api/orchestration/post_turn.py:43` |
| `MetricsMiddleware` | `src/starry_lyfe/api/endpoints/metrics.py:74` |
| `BDOne.stream_complete()` | `src/starry_lyfe/dreams/llm.py:189` |
| Alembic migration | `alembic/versions/004_phase_7_chat_sessions.py` |

**End of Operator Guide.**
