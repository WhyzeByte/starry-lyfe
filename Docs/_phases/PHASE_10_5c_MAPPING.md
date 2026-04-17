# PHASE 10.5c — Narrow Canon → Rich YAML Field Mapping

**Status:** C1 deliverable, Project Owner ratified (2026-04-16, REVISED).
**Author:** Claude Code, Phase 10.5c C1 pre-flight audit.
**Companion:** Plan at `C:\Users\Whyze\.claude\plans\plan-phase-10-5c-zany-cherny.md`. Spec at `Docs/_phases/PHASE_10.md` §Phase 10.5c.
**Scope:** Map every field of all 7 narrow Pydantic objects to ONE authoritative source location in rich YAML or `shared_canon.yaml`. Identify authoring gaps. NO code changes in this phase.

**Revision history:**
- **R0 (2026-04-16, draft):** Initial mapping proposed a `runtime` block per character to mirror narrow values where rich shapes diverged. Project Owner course-correction: that approach preserves drift instead of eliminating it. The whole point of YAML migration is ONE authoritative source per field. Redrafted.
- **R1 (2026-04-16):** Single-source-of-truth principle applied. No parallel mirror blocks. Where rich and narrow values disagree, rich wins; current narrow values that conflict are rationalized. Bit-identical fixture regression becomes a drift-review tool, not a preservation gate.
- **R1-ratified (2026-04-16):** Project Owner ratified §2 architectural decisions + the two open calls in §6.2:
  - **Heritage/profession/business/languages narrow source:** explicit `canonical_label` / `canonical_list` sub-field per character (not hardcoded adapter derivation). Rationale: each character's narrow identity descriptor is author-chosen and follows different patterns ("Valencian-Australian", "Assyrian-Iranian Canadian", "Argentine"); explicit authoring honors that authorial choice and avoids brittle string rules across 4 divergent rich shapes.
  - **Bina's `astrology`:** rename `identity.zodiac` → `identity.astrology` for cross-character field-name consistency; let the values surface to narrow. Rationale: Bina has authored zodiac data (Capricorn/Cancer/Virgo) and the current narrow `null` is an authoring oversight, not deliberate. All four other characters carry astrology; excluding Bina is asymmetric. Character fidelity > preserving an arbitrary `null`.

---

## 1. Executive summary

The 7 narrow Pydantic objects (`CanonCharacters`, `CanonPairs`, `CanonDyads`, `CanonProtocols`, `CanonInterlocks`, `CanonVoiceParameters`, `CanonRoutines`) currently hydrate from 7 narrow YAML files. Phase 10.5c rewires `load_all_canon()` to construct them from rich YAML + `shared_canon.yaml` instead.

**Governing principle (Project Owner directive 2026-04-16):** The rich YAML files are the single authoritative source per field. No drift. No parallel surfaces. Where rich shape differs from narrow shape, code derives narrow from rich. Where rich and narrow values disagree, rich wins; current narrow values that diverge are intentional rationalizations recorded at fixture review.

C1 audit findings (revised):

- Most narrow fields map to ONE existing rich location (see §3).
- Where the rich block lacks a narrow-required field (e.g., `cognitive_function_stack`), the field gets authored into the SEMANTICALLY CORRECT existing rich block — `identity`, `voice.runtime_sampling_hints` (renamed `voice.inference_parameters`), `pair_architecture`, `behavioral_framework`. NOT a parallel `runtime.identity_flat` mirror.
- Where rich currently uses a different shape than narrow (e.g., `identity.heritage` is dict, narrow is string), an adapter in `_build_*` derives narrow from rich. The derivation rule is the documented authority.
- Where rich and narrow CURRENTLY DISAGREE on a value (heritage, pair classification, etc.), the rich value becomes canonical. The fixture diff at C2 captures the rationalization for Project Owner review.
- `shared_canon.yaml` gains `memory_tiers`, `dyads_baseline`, `interlocks` (cross-character objective taxonomies). `shared_canon.pairs[]` expands to carry all narrow `Pair` fields. These are objective facts that have no per-character home.
- Routines remain as per-character `runtime.routines` blocks per Option A pre-decision (verbatim from `routines.yaml`). This is the only `runtime`-prefixed block; routines genuinely don't exist anywhere else in rich.

Section 2 surfaces the architectural decisions for ratification. Section 3 details per-object mappings. Section 4 inventories the authoring required.

---

## 2. Architectural decisions for ratification

### 2.1 ONE authoritative source per field

**Decision:** No `runtime.identity_flat`/`runtime.voice_parameters`/`runtime.pairs_yaml` blocks. Every narrow field maps to ONE rich location, the semantically-correct one. Where adapters are needed (rich-dict → narrow-string), the adapter is documented in the mapping table and implemented in `_build_*`.

**Implications:**

- Adding missing narrow fields means extending existing rich blocks (`identity` gains `cognitive_function_stack`, `voice.runtime_sampling_hints` gains the 5 missing voice params, etc.).
- Where rich and narrow values disagree today (e.g., adelia heritage rich="Valencian-Spanish" vs narrow="Valencian-Australian"), rich wins. Either the adapter derivation produces the rich value (rationalizing narrow), or the rich field gets edited to produce a deliberately-chosen value.
- The bit-identical fixture regression becomes a DRIFT-REVIEW TOOL — every diff at C2 is documented and Project Owner approved.

### 2.2 `voice.runtime_sampling_hints` → `voice.inference_parameters`

**Decision:** Rename the existing `voice.runtime_sampling_hints` block to `voice.inference_parameters` and extend it with 5 currently-missing narrow fields.

**Rationale:** "Inference parameters" is the canonical term used in CLAUDE.md §16 ("Per-character model parameters (temperature, top_p, penalties) in `personas/registry.py`"). The rename aligns naming with the canonical concept. The block becomes the single home for all 10 narrow `VoiceParameter` fields.

**Schema (post-extension):**

```yaml
voice:
  inference_parameters:
    temperature_midpoint: <float>
    temperature_range: [<low>, <high>]
    top_p: <float>
    thinking_effort: "think_lightly" | "think_moderately"
    response_length: "short" | "short_to_medium" | "medium"
    # NEW (currently missing):
    distinctive_sampling: "<str>" | null
    presence_penalty: <float>
    frequency_penalty: <float>
    response_length_range: "<str>"
    dominant_function_descriptor: "<str>"
```

### 2.3 Identity block extensions

**Decision:** Each woman's `identity` block gains the 6 narrow `Character` fields not currently present:

- `cognitive_function_stack: [<fn>, <fn>, <fn>, <fn>]`
- `dominant_function: "<fn>"`
- `is_resident: <bool>`
- `operational_travel: "<str>" | null` (Alicia only — null elsewhere)
- `spouse: "<character_id>" | null` (Bina/Reina only — null elsewhere)
- (`family_notes`, `siblings` — author into the EXISTING richer rich shapes if not narrow-flat: Bina's `identity.family.twin_brother` already exists in richer form; the adapter derives narrow `family_notes`. Alicia's siblings need authoring — into `identity.siblings` directly.)

Shawn's `identity` gains the 2 narrow `Operator` fields:

- `cognitive_function_stack: ["Ni", "Te", "Fi", "Se"]`
- `dominant_function: "Ni"`

**Rationale:** Rich `identity` is the canonical home for character-identity facts. Adding the 4-element cognitive function stack here matches the semantic role of the block.

### 2.4 `shared_canon.yaml` expansion (system-level taxonomies)

**Decision:** `Characters/shared_canon.yaml` gains 4 new top-level blocks for objective cross-character facts:

- **`memory_tiers`** (7 entries): The system-level memory tier taxonomy. Hydrates `CanonDyads.memory_tiers`. Lifted verbatim from `dyads.yaml::memory_tiers`.
- **`dyads_baseline`** (10 entries): Per-dyad members + type + subtype + interlock + pair + is_currently_active + dimension baselines. Hydrates `CanonDyads.dyads`. Lifted verbatim from `dyads.yaml::dyads`. Dyad baselines are objective state, not character POV — `shared_canon` is the right home.
- **`interlocks`** (6 entries): Per-interlock name + members + description + tone + type + origin + canonical_disagreement. Hydrates `CanonInterlocks.interlocks`. Lifted verbatim from `interlocks.yaml::interlocks`. Per-woman `family_and_other_dyads.with_<other>` blocks remain pure POV prose (perspective-divergence-required principle from Phase 10.5b RT2).
- **`pairs[]` expansion**: each entry gains `character`, `shared_functions`, `what_she_provides`, `how_she_breaks_spiral`, `core_metaphor`, `cadence` fields. Carries the SINGLE authoritative value per Pair field. Hydrates `CanonPairs.pairs`.

**Rationale:** All four are cross-character objective facts. They have no natural per-character home. `shared_canon.yaml` already houses cross-character facts (marriage, genealogy, property, timeline, pairs); these four extend that role.

### 2.5 Pair fields source from `shared_canon.pairs[]` (single source)

**Decision:** Narrow `Pair` fields source ONLY from `shared_canon.pairs[]`. Per-woman `pair_architecture` blocks remain rich POV prose for prompt assembly — they DO NOT hydrate the typed narrow `Pair` object. This eliminates the three-way drift (narrow `pairs.yaml` vs `shared_canon.pairs[]` vs per-woman `pair_architecture`).

**Drift rationalization required:** Currently:

| Pair | Narrow `pairs.yaml` | `shared_canon.pairs[]` | Per-woman `pair_architecture` |
|---|---|---|---|
| Entangled | "Intuitive Symbiosis" | "generator-governor polarity" | Adelia: "Intuitive Symbiosis" |
| Circuit | "Orthogonal Opposition" | "diagnostic love" | Bina: "Orthogonal Opposition / Asymmetrical Leverage / Superego Relation" |
| Kinetic | "Asymmetrical Leverage" | "kinetic-vanguard" | Reina: "Asymmetrical leverage / strategy-tactics dyad / Mastermind and Operator" |
| Solstice | "Complete Jungian Duality" | "Complete functional inversion / Socionics duality" | Alicia: "Complete functional inversion / Socionics duality" |

Phase 10.5b R2-F3 ratified `shared_canon.pairs[]` as the Layer 5 objective anchor. By the same logic, `shared_canon.pairs[]` is the canonical objective source for narrow `Pair` fields too. The current shared_canon strings ("generator-governor polarity", "diagnostic love", "kinetic-vanguard", "Complete functional inversion / Socionics duality") become the canonical values. The narrow YAML strings ("Intuitive Symbiosis" etc.) get retired.

**Project Owner judgment call at C2 fixture review:** the diff between pre-rewire (narrow strings) and post-rewire (shared_canon strings) surfaces the rationalization. Project Owner can either approve the rationalization as-is OR direct edits to `shared_canon.pairs[]` if a better canonical string exists. The principle stays: ONE source.

### 2.6 Per-character `runtime.routines` (per Option A pre-decision)

**Decision:** Each woman's rich YAML gains a top-level `runtime.routines` block. Verbatim lift from `routines.yaml::routines.<woman>`. This is the only `runtime`-prefixed block in the architecture (routines have no other rich home).

Alicia's YAML additionally gains `runtime.alicia_communication_distribution` for the `phone`/`letter`/`video_call` weights.

### 2.7 Per-character `behavioral_framework.state_protocols`

**Decision:** Each character's protocol-owning entries (Adelia: 4, Bina: 1, Reina: 2, Alicia: 2, Shawn: 4 — totaling 13) live in `behavioral_framework.state_protocols` as a dict matching the narrow `Protocol` shape. Hydration aggregates across all 5 character files into `CanonProtocols.protocols`.

**Rationale:** The spec at PHASE_10.md §Phase 10.5c expected mapping highlights names this exact location. Existing rich `behavioral_framework.stress_modes` blocks (Adelia's `bunker_mode`, `warlord_mode`) get migrated into the new `state_protocols` block with narrow-shape entries. Existing rich prose (`triggers`, `presentation`, `exit_rule`) collapses into the narrow `Protocol.description` field, OR is preserved alongside `state_protocols` if Project Owner judges the prose worth keeping for separate prompt-assembly purposes — but in that case prose lives in a different sub-block to keep `state_protocols` itself the sole authority for narrow Protocol hydration.

### 2.8 Bit-identical fixture regression becomes drift-review

**Decision:** Reframe AC-10.5c.4. The pre-rewire fixture captures `load_all_canon()` output BEFORE C2. After C2 rewires, the diff between pre-rewire and post-rewire output is reviewed by Project Owner per-field. Each diff is either:

- **Intentional drift rationalization** (e.g., pair classification migrating from "Intuitive Symbiosis" to "generator-governor polarity") — approved at review.
- **Hydration bug** (rich source authored, but `_build_*` derivation produced wrong value) — fixed in `_build_*`.
- **Missed authoring** (rich source not yet carrying the narrow value) — fixed in rich YAML.

This means C2 is no longer "bit-identical exit criterion" — it's "every diff justified" exit criterion. The spec at PHASE_10.md AC-10.5c.4 needs amendment in C3 governance pass.

---

## 3. Per-object field mapping

For each narrow Pydantic root object, every field with its single authoritative rich source. Three columns: **Narrow field**, **Authoritative rich source**, **Notes / Authoring action**.

### 3.1 `CanonCharacters`

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Set by `_build_characters()`. |
| `characters` | iterate `load_all_rich_characters()` for women only | Construct `dict[CharacterID, Character]` — adelia/bina/reina/alicia. |
| `operator` | `load_all_rich_characters()["shawn"]` | Construct `dict[str, Operator]` with single key `"whyze"`. |

#### `Character` (per woman)

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `full_name` | `meta.full_name` | Direct. |
| `role` | constant `"character"` | Static literal. |
| `epithet` | `meta.epithet` | Direct. |
| `age` | `identity.age` | Direct. |
| `birthdate` | `identity.birthdate` | Direct (may be `null`). |
| `mbti` | `identity.mbti` | Direct. |
| `heritage` | `identity.heritage` (rich dict) | **ADAPTER** — derive narrow string from rich dict. Proposed rule (per character, document in mapping): adelia: `f"{primary.split('-')[0]}-{secondary.split(' ')[0]}"`; bina: `f"{primary} {current_national_identity}"`; reina/alicia: TBD per current rich shape. ALTERNATIVE: rationalize rich `identity.heritage.flat` field that holds the canonical narrow string explicitly authored once. **Recommendation: add `identity.heritage.canonical_label` field per character**, populated once at C1.4, to avoid brittle string-manipulation rules. The `canonical_label` is the single source for narrow `Character.heritage`. |
| `birthplace` | `identity.birthplace` (Adelia/Reina/Alicia) or derive from `identity.family_origin` (Bina) | Bina-only adapter: `f"{family_origin.city}, {family_origin.country}"`. Or author `identity.birthplace` for Bina directly. |
| `raised_in` | `identity.raised_in` | Direct. |
| `current_residence` | `identity.current_residence` | Direct (rich vs narrow value drift addressed at fixture review). |
| `is_resident` | `identity.is_resident` | **AUTHORING GAP** — add to each woman's identity. All 4 women: `true`. |
| `operational_travel` | `identity.operational_travel` | **AUTHORING GAP** — Alicia: `"Frequently away on consular operations"`; others omit (defaults to `null`). |
| `pair_name` | `identity.pair_name` | Direct. |
| `profession` | `identity.profession` (rich dict) | **ADAPTER** — narrow string is `identity.profession.primary` plus comma-joined `identity.profession.secondary`. Or author `identity.profession.canonical_label` for explicit authority. **Recommendation: canonical_label**. |
| `business` | `identity.business` (rich dict) | **ADAPTER** — narrow string is `identity.business.name` (women) or `identity.business.legal_name` (Shawn). Author `identity.business.canonical_label` for explicit authority where the derivation is non-trivial. |
| `employer` | `identity.employer` | **AUTHORING GAP** — Alicia only: `"Argentine Cancillería (MRECIC)"`; author into Alicia's identity. Others omit. |
| `unit` | `identity.unit` | **AUTHORING GAP** — Alicia only: `"Dirección General de Asuntos Consulares, crisis response"`; author into Alicia's identity. Others omit. |
| `languages` | `identity.languages` (rich shape) | **ADAPTER** — rich uses `default_public_language` + `private_register`/`heritage_registers` + `language_rules`. Narrow uses `[{register, context}]`. Adapter derives the list. **Recommendation: add `identity.languages.canonical_list`** as the explicit authored narrow shape, since rich has 4-5 different shape variants across the 4 women and a generic adapter is brittle. |
| `parents` | `identity.parents` (rich dict, has extra `carried_truth`) | **ADAPTER** — strip `carried_truth` from each parent dict; output `{father: {name, origin, profession}, mother: {...}}`. Direct projection. |
| `children` | `identity.children` (NEW canonical narrow-shape field) | **AUTHORING GAP** — Bina rich has `identity.family.son.name="Gavin"` (different shape); Adelia/Reina/Alicia rich has no children. **Author `identity.children` directly as narrow shape `[{name, age, relationship}]`.** Bina: `[{name: "Gavin", age: 7, relationship: "biological son from prior relationship"}]`. Others: `[]`. The richer Bina `identity.family.son` block can stay for prose context OR get retired. |
| `cognitive_function_stack` | `identity.cognitive_function_stack` | **AUTHORING GAP** — author into each woman's identity. Adelia: `["Ne","Fi","Te","Si"]`; Bina: `["Si","Fe","Ti","Ne"]`; Reina: `["Se","Ti","Fe","Ni"]`; Alicia: `["Se","Fi","Te","Ni"]`. |
| `dominant_function` | `identity.dominant_function` | **AUTHORING GAP** — same authoring pass; equals `cognitive_function_stack[0]`. |
| `spouse` | `identity.spouse` | **AUTHORING GAP** — Bina: `"reina"`; Reina: `"bina"`; Adelia/Alicia omit. Bina rich has `identity.family.wife.name="Reina Torres"` — different shape, and uses display name. Author `identity.spouse` as character_id directly. |
| `family_notes` | `identity.family_notes` (NEW canonical narrow-shape field) | **AUTHORING GAP** — Bina only. Author `{twin_brother: {name: "Arash", status: "MIA (Canadian Armed Forces)"}, parents_status: "Both deceased", ex_partner: {name: "Kael", status: "No contact, restraining order"}}`. The richer rich blocks (`identity.family.twin_brother`, soul_substrate prose about Arash, etc.) stay for prose context. |
| `siblings` | `identity.siblings` | **AUTHORING GAP** — Alicia only: `[{name: "Joaquin", location: "Famaillá", occupation: "Ferretería owner"}, {name: "Carmen", location: "Rosario", occupation: "Night-shift nurse"}]`. Author into Alicia's identity. |
| `astrology` | `identity.astrology` (Adelia/Reina/Alicia) — derive `null` for Bina | **ADAPTER** — Bina rich has `identity.zodiac` but narrow is `null`. Per single-source: rename Bina's `identity.zodiac` → `identity.astrology` (one canonical field name across all 4 women) BUT explicitly leave Bina's narrow `astrology` as `null` until Project Owner decides to surface it. C1.4 just renames `zodiac` → `astrology`; hydration adapter sets bina narrow to `null` until shared_canon or operator decision says otherwise. ALTERNATIVE simpler: leave bina narrow as `null` by hydrating only Adelia/Reina/Alicia. Mark this as a Project Owner ratification call: should Bina's astrology values from rich `identity.zodiac` flow through to narrow, breaking the current narrow `null`? |

#### `Operator` (Shawn only)

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `full_name` | `meta.full_name` | Direct. |
| `handle` | `identity.runtime_alias` | `"Whyze"`. |
| `role` | constant `"operator"` | Static. |
| `age` | `identity.age` | Direct. |
| `mbti` | `identity.mbti` | `"INTJ-T"`. |
| `cognitive_function_stack` | `identity.cognitive_function_stack` | **AUTHORING GAP** — author `["Ni", "Te", "Fi", "Se"]`. |
| `dominant_function` | `identity.dominant_function` | **AUTHORING GAP** — `"Ni"`. |
| `clinical` | `identity.neurotype` | **ADAPTER** — derive narrow `{asd_level, twice_exceptional}` from rich `identity.neurotype.clinical_identity` list (string-match on "ASD Level X" and "Twice-exceptional"). OR explicitly author `identity.neurotype.narrow_clinical = {asd_level: 2, twice_exceptional: true}`. **Recommendation: explicit narrow field** — string-matching across enum-like prose is fragile. |
| `disc` | `identity.disc` | Currently rich="CD with atypical Action extension"; narrow="CD with Action extension". **Drift** — rich wins. Fixture diff at C2 review. |
| `astrology` | `identity.astrology` | **AUTHORING GAP** — author `{sun: "Libra", moon: "Scorpio", venus: "Scorpio"}` into Shawn's identity (currently absent). |
| `children` | `identity.children` (NEW canonical narrow-shape field) | **AUTHORING GAP** — Shawn rich has `identity.spouse_and_children.daughters` (rich nested with born/ASD diagnosis/prose). Author `identity.children: [{name: "Isla", age: 6, relationship: "daughter"}, {name: "Daphne", age: 4, relationship: "daughter"}]`. The rich `spouse_and_children.daughters` stays for prose context. |
| `profile_file` | `identity.profile_file` | **AUTHORING GAP** — author `"Characters/Shawn/Shawn_Kroon_v7.0.md"` into Shawn's identity. |
| `profile_version` | `identity.profile_version` | **AUTHORING GAP** — author `"7.0"`. |

### 3.2 `CanonPairs`

Per §2.5 decision: all `Pair` fields source from `shared_canon.pairs[]` (expanded). Per-woman `pair_architecture` blocks do NOT hydrate narrow Pair.

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `pairs` | iterate `shared_canon.pairs[]` | 4 pairs total. |

#### `Pair` (per pair, sourced from expanded `shared_canon.pairs[]`)

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `character` | `shared_canon.pairs[].character` | **AUTHORING GAP** — add field. Adelia=adelia, Circuit=bina, Kinetic=reina, Solstice=alicia. |
| `full_name` | `shared_canon.pairs[].canonical_name` | Existing field; matches narrow `full_name` ("The Entangled Pair" etc.). |
| `classification` | `shared_canon.pairs[].classification` | Existing field. **DRIFT — rich wins per §2.5.** Current shared_canon values become canonical. |
| `shared_functions` | `shared_canon.pairs[].shared_functions` | **AUTHORING GAP** — add field, lift verbatim from `pairs.yaml::pairs.<key>.shared_functions`. |
| `mechanism` | `shared_canon.pairs[].mechanism` | Existing field. **DRIFT — rich wins.** |
| `what_she_provides` | `shared_canon.pairs[].what_she_provides` | **AUTHORING GAP** — add field, lift verbatim from pairs.yaml. |
| `how_she_breaks_spiral` | `shared_canon.pairs[].how_she_breaks_spiral` | **AUTHORING GAP** — add field, lift verbatim from pairs.yaml. |
| `core_metaphor` | `shared_canon.pairs[].core_metaphor` | **AUTHORING GAP** — add field, lift verbatim from pairs.yaml. |
| `cadence` | `shared_canon.pairs[].cadence` | **AUTHORING GAP** — add field. Entangled/Circuit/Kinetic: `"continuous"`; Solstice: `"intermittent"`. Verbatim from pairs.yaml. |

### 3.3 `CanonDyads`

Per §2.4 D1 decision: `dyads_baseline` lives in `shared_canon.yaml`.

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `dyads` | `shared_canon.dyads_baseline` | **AUTHORING GAP** — add block to shared_canon. 10 entries verbatim from `dyads.yaml::dyads`. |
| `memory_tiers` | `shared_canon.memory_tiers` | **AUTHORING GAP** — add block. 7 entries verbatim from `dyads.yaml::memory_tiers`. |

#### `Dyad` (per entry)

All fields direct from `shared_canon.dyads_baseline.<key>`: `members`, `type`, `subtype`, `interlock`, `pair`, `is_currently_active`, `dimensions.{trust,intimacy,conflict,unresolved_tension,repair_history}.{baseline,min,max}`. Verbatim from `dyads.yaml`.

#### `MemoryTier` (per entry)

Direct from `shared_canon.memory_tiers[]`. Verbatim from `dyads.yaml`.

### 3.4 `CanonProtocols`

Per §2.7 decision: per-character `behavioral_framework.state_protocols` dict.

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `protocols` | aggregate `behavioral_framework.state_protocols` from all 5 character YAMLs | 13 entries: 4 Adelia + 1 Bina + 2 Reina + 2 Alicia + 4 Shawn. |

#### `Protocol` (per entry — author into each character's `behavioral_framework.state_protocols`)

Direct field mapping per `Protocol` schema:

```yaml
behavioral_framework:
  state_protocols:
    bunker_mode:                     # dict key
      name: "Bunker Mode"
      primary_character: "adelia"
      secondary_characters: ["reina", "whyze", "bina"]
      category: "biological_limit"
      description: "Si-grip failure state. Rigid, trapped in past, convinced old failed route is live."
      entry_conditions: "Under stress, Si-grip fires"
      recovery_architecture:
        first_responder: {character: "reina", role: "Physical intervention, breaks the loop"}
        second_responder: {character: "whyze", role: "Structural, gives one clear path forward"}
        third_responder: {character: "bina", role: "Silent logistics, handles external fallout"}
      source: null
```

Verbatim values from `protocols.yaml::protocols.<key>`. Existing rich `behavioral_framework.stress_modes` block (currently in Adelia) gets RETIRED — its content folds into `state_protocols.bunker_mode.description` + `recovery_architecture` directly. Soul-bearing prose from `stress_modes` (`triggers`, `presentation`, `exit_rule`) collapses into a richer description string OR moves to a new `behavioral_framework.protocol_prose` sub-block if Project Owner judges the prose worth preserving outside the typed `state_protocols` shape.

**Per-character ownership** (verbatim from `protocols.yaml::primary_character`):

- adelia: `taurus_venus_override`, `whiteboard_mode`, `bunker_mode`, `warlord_mode` (4)
- bina: `flat_state` (1)
- reina: `post_race_crash`, `admissibility_protocol` (2)
- alicia: `four_phase_return`, `sun_override` (2)
- whyze (Shawn, operator): `red_team_stabilization`, `perfection_anchoring`, `alexithymia_protocol`, `interoceptive_override` (4)

Total: 13 (12 Vision-section-7 + 1 character_kernel-sourced `warlord_mode`).

### 3.5 `CanonInterlocks`

Per §2.4 I2 decision: `shared_canon.interlocks`.

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `interlocks` | `shared_canon.interlocks` | **AUTHORING GAP** — add block. 6 entries verbatim from `interlocks.yaml::interlocks`. |

#### `Interlock` (per entry)

Direct from `shared_canon.interlocks[]`: `name`, `members`, `description`, `tone`, `type`, `origin`, `canonical_disagreement`. Verbatim from `interlocks.yaml`.

Per-woman `family_and_other_dyads.with_<other>` blocks remain pure POV prose for prompt assembly — they DO NOT hydrate `Interlock`. This isolates objective taxonomy (shared_canon) from per-woman perspective (rich pair POV) cleanly.

### 3.6 `CanonVoiceParameters`

Per §2.2 decision: `voice.runtime_sampling_hints` → `voice.inference_parameters` (extended).

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `voice_parameters` | iterate women, build per-character from `voice.inference_parameters` | 4 entries. |

#### `VoiceParameter` (per woman, sourced from extended `voice.inference_parameters`)

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `character` | woman's `character_id` | Direct. |
| `temperature.range` | `voice.inference_parameters.temperature_range` | Renamed from `voice.runtime_sampling_hints.temperature_range`. |
| `temperature.midpoint` | `voice.inference_parameters.temperature_midpoint` | Renamed. |
| `top_p` | `voice.inference_parameters.top_p` | Renamed. |
| `thinking_effort` | `voice.inference_parameters.thinking_effort` | Renamed. |
| `distinctive_sampling` | `voice.inference_parameters.distinctive_sampling` | **AUTHORING GAP** — add field. Adelia/Bina: `null`; Reina: `"high_presence_penalty"`; Alicia: `"low_frequency_penalty"`. |
| `presence_penalty` | `voice.inference_parameters.presence_penalty` | **AUTHORING GAP** — Adelia/Bina/Alicia: `0.0`; Reina: `0.8`. |
| `frequency_penalty` | `voice.inference_parameters.frequency_penalty` | **AUTHORING GAP** — Adelia/Bina/Reina: `0.0`; Alicia: `0.2`. |
| `response_length` | `voice.inference_parameters.response_length` | Renamed. |
| `response_length_range` | `voice.inference_parameters.response_length_range` | **AUTHORING GAP** — see narrow `voice_parameters.yaml` for verbatim values per character. |
| `dominant_function_descriptor` | `voice.inference_parameters.dominant_function_descriptor` | **AUTHORING GAP** — Adelia: `"Ne-dominant associative leaps"`; Bina: `"Si-dominant declarative steadiness"`; Reina: `"Se-dominant tactical motion"`; Alicia: `"Se-dominant somatic co-regulation"`. |

### 3.7 `CanonRoutines`

Per §2.6 decision: per-character `runtime.routines` (Option A pre-decision).

#### Root

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `version` | constant `"7.1"` | Static. |
| `routines` | iterate women, build from `runtime.routines` | 4 entries. |
| `alicia_communication_distribution` | `Characters/alicia_marin.yaml::runtime.alicia_communication_distribution` | Author into Alicia only. |

#### `CharacterRoutines` (per woman)

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `character` | woman's `character_id` | Direct. |
| `weekday` | `runtime.routines.weekday` | **AUTHORING GAP** — verbatim lift from `routines.yaml::routines.<woman>.weekday`. |
| `weekend` | `runtime.routines.weekend` | Same. |
| `recurring_events` | `runtime.routines.recurring_events` | Same. |

#### `AliciaCommunicationDistribution`

| Narrow field | Authoritative source | Notes |
|---|---|---|
| `phone` | `Characters/alicia_marin.yaml::runtime.alicia_communication_distribution.phone` | `0.45` |
| `letter` | same | `0.20` |
| `video_call` | same | `0.35` |

---

## 4. Authoring gap inventory (by file)

Concise list of every authoring change needed in C1.4. Each rich character YAML extends EXISTING blocks (no new mirror blocks) plus a new `runtime.routines` block. shared_canon gains 4 new top-level blocks plus expanded `pairs[]` entries.

### 4.1 `Characters/adelia_raye.yaml`

**Extend `identity`:**
- `is_resident: true`
- `cognitive_function_stack: ["Ne", "Fi", "Te", "Si"]`
- `dominant_function: "Ne"`
- `children: []`  (canonical narrow-shape field)
- `heritage.canonical_label: "Valencian-Australian"`  (explicit narrow-source label; rich dict stays)
- `profession.canonical_label: "Pyrotechnician, installation artist, embedded systems engineer"`
- `business.canonical_label: "Ozone & Ember"`
- `languages.canonical_list: [{register, context}, ...]` (verbatim from characters.yaml::adelia.languages)

**Extend `voice.inference_parameters`** (rename from `runtime_sampling_hints`, add 5):
- `distinctive_sampling: null`
- `presence_penalty: 0.0`
- `frequency_penalty: 0.0`
- `response_length_range: "2-4 paragraphs"`
- `dominant_function_descriptor: "Ne-dominant associative leaps"`

**Extend `behavioral_framework.state_protocols`** (new dict, narrow-shape Protocol entries):
- `taurus_venus_override`, `whiteboard_mode`, `bunker_mode` (Vision section 7), `warlord_mode` (with `source: "character_kernel"`)
- Existing `behavioral_framework.stress_modes` block retires (its content collapses into `state_protocols.bunker_mode.description` + `recovery_architecture`)

**Add top-level `runtime.routines`:**
- Verbatim lift from `routines.yaml::routines.adelia` (weekday, weekend, recurring_events)

### 4.2 `Characters/bina_malek.yaml`

**Extend `identity`:**
- `is_resident: true`
- `cognitive_function_stack: ["Si", "Fe", "Ti", "Ne"]`
- `dominant_function: "Si"`
- `spouse: "reina"`
- `family_notes: {twin_brother: {name: "Arash", status: "MIA (Canadian Armed Forces)"}, parents_status: "Both deceased", ex_partner: {name: "Kael", status: "No contact, restraining order"}}`
- `children: [{name: "Gavin", age: 7, relationship: "biological son from prior relationship"}]`
- `birthplace: "Urmia, Iran"` (or rename `family_origin` adapter)
- `heritage.canonical_label: "Assyrian-Iranian Canadian"`
- `profession.canonical_label: "Red Seal mechanic"`
- `business.canonical_label: "Loth Wolf Hypersport"`
- `languages.canonical_list: [3 entries — English / Suret / Farsi per narrow shape]`
- Rename `identity.zodiac` → `identity.astrology` (no value change; rename for cross-character consistency)

**Extend `voice.inference_parameters`:**
- `distinctive_sampling: null`
- `presence_penalty: 0.0`
- `frequency_penalty: 0.0`
- `response_length_range: "2-4 sentences"`
- `dominant_function_descriptor: "Si-dominant declarative steadiness"`

**Extend `behavioral_framework.state_protocols`:**
- `flat_state` (Vision section 7)

**Add top-level `runtime.routines`:**
- Verbatim from `routines.yaml::routines.bina`

### 4.3 `Characters/reina_torres.yaml`

**Extend `identity`:**
- `is_resident: true`
- `cognitive_function_stack: ["Se", "Ti", "Fe", "Ni"]`
- `dominant_function: "Se"`
- `spouse: "bina"`
- `children: []`
- `heritage.canonical_label: "Barcelona Catalan-Castilian"`
- `profession.canonical_label: "Criminal defence lawyer"`
- `business.canonical_label: "Solo practice, Okotoks"`
- `languages.canonical_list: [3 entries — English / Catalan / European peninsular Castilian]`

**Extend `voice.inference_parameters`:**
- `distinctive_sampling: "high_presence_penalty"`
- `presence_penalty: 0.8`
- `frequency_penalty: 0.0`
- `response_length_range: "Short-to-medium with freedom to compress into one clean incision"`
- `dominant_function_descriptor: "Se-dominant tactical motion"`

**Extend `behavioral_framework.state_protocols`:**
- `post_race_crash`, `admissibility_protocol`

**Add top-level `runtime.routines`:**
- Verbatim from `routines.yaml::routines.reina`

### 4.4 `Characters/alicia_marin.yaml`

**Extend `identity`:**
- `is_resident: true`
- `operational_travel: "Frequently away on consular operations"`
- `employer: "Argentine Cancillería (MRECIC)"`
- `unit: "Dirección General de Asuntos Consulares, crisis response"`
- `cognitive_function_stack: ["Se", "Fi", "Te", "Ni"]`
- `dominant_function: "Se"`
- `siblings: [{name: "Joaquin", location: "Famaillá", occupation: "Ferretería owner"}, {name: "Carmen", location: "Rosario", occupation: "Night-shift nurse"}]`
- `children: []`
- `heritage.canonical_label: "Argentine"`
- `profession.canonical_label: "Senior consular officer"`
- (no `business`; she works for an employer)
- `languages.canonical_list: [2 entries — Argentine Rioplatense / English]`

**Extend `voice.inference_parameters`:**
- `distinctive_sampling: "low_frequency_penalty"`
- `presence_penalty: 0.0`
- `frequency_penalty: 0.2`
- `response_length_range: "Short-to-medium, body-first with sensory anchors, no exclamation points"`
- `dominant_function_descriptor: "Se-dominant somatic co-regulation"`

**Extend `behavioral_framework.state_protocols`:**
- `four_phase_return`, `sun_override`

**Add top-level `runtime.routines`:**
- Verbatim from `routines.yaml::routines.alicia`

**Add top-level `runtime.alicia_communication_distribution`:**
- `{phone: 0.45, letter: 0.20, video_call: 0.35}`

### 4.5 `Characters/shawn_kroon.yaml`

**Extend `identity`:**
- `cognitive_function_stack: ["Ni", "Te", "Fi", "Se"]`
- `dominant_function: "Ni"`
- `astrology: {sun: "Libra", moon: "Scorpio", venus: "Scorpio"}` (currently absent at identity level)
- `children: [{name: "Isla", age: 6, relationship: "daughter"}, {name: "Daphne", age: 4, relationship: "daughter"}]` (canonical narrow-shape field; rich `spouse_and_children.daughters` stays for prose)
- `profile_file: "Characters/Shawn/Shawn_Kroon_v7.0.md"`
- `profile_version: "7.0"`
- `neurotype.narrow_clinical: {asd_level: 2, twice_exceptional: true}` (explicit narrow shape; rich `clinical_identity` list stays)

**Extend `behavioral_framework.state_protocols`:**
- `red_team_stabilization`, `perfection_anchoring`, `alexithymia_protocol`, `interoceptive_override`

(No `runtime` block. Shawn has no routines or pair_architecture.)

### 4.6 `Characters/shared_canon.yaml`

**Add 4 new top-level blocks:**

```yaml
memory_tiers:
  # 7 entries verbatim from dyads.yaml::memory_tiers
  - {name: "Canon Facts", tier: 1, mutable: false, description: "..."}
  - {name: "Character Baseline", tier: 2, mutable: false, description: "..."}
  - {name: "Dyad State (Whyze)", tier: 3, mutable: true, description: "..."}
  - {name: "Dyad State (Internal)", tier: 4, mutable: true, description: "..."}
  - {name: "Episodic Memories", tier: 5, mutable: true, description: "..."}
  - {name: "Open Loops", tier: 6, mutable: true, description: "..."}
  - {name: "Transient Somatic State", tier: 7, mutable: true, description: "..."}

dyads_baseline:
  # 10 entries verbatim from dyads.yaml::dyads
  adelia_bina: {members, type, subtype, interlock, dimensions: {trust, intimacy, conflict, unresolved_tension, repair_history}}
  bina_reina: {...}
  adelia_reina: {...}
  adelia_alicia: {is_currently_active: false, ...}
  bina_alicia: {is_currently_active: false, ...}
  reina_alicia: {is_currently_active: false, ...}
  whyze_adelia: {type: "whyze_pair", pair: "entangled", ...}
  whyze_bina: {pair: "circuit", ...}
  whyze_reina: {pair: "kinetic", ...}
  whyze_alicia: {pair: "solstice", is_currently_active: false, ...}

interlocks:
  # 6 entries verbatim from interlocks.yaml::interlocks
  - {key: "anchor_dynamic", name: "The Anchor Dynamic", members: ["adelia", "bina"], description: "...", tone: "...", type: "resident_continuous"}
  - {key: "shield_wall", ...}
  - {key: "kinetic_vanguard", ...}
  - {key: "letter_era_friends", ..., origin: "October 2019, gallery opening in Inglewood"}
  - {key: "couch_above_the_garage", ...}
  - {key: "lateral_friends", ..., canonical_disagreement: "European vs South American football, ..."}
```

**Expand `pairs[]`** — each existing entry gains 6 new fields:

```yaml
pairs:
  - canonical_name: "The Entangled Pair"
    classification: "generator-governor polarity"            # existing
    mechanism: "Ne flood meets Si structure; ..."            # existing
    character: "adelia"                                       # NEW
    shared_functions: "Fi-Te axis (direct bridge)"          # NEW (verbatim from pairs.yaml)
    what_she_provides: "Emotional buoyancy, divergent ideation, the destination"   # NEW
    how_she_breaks_spiral: "Injects warmth and play (Ne)"   # NEW
    core_metaphor: "The Compass and the Gravity"            # NEW
    cadence: "continuous"                                    # NEW
  - canonical_name: "The Circuit Pair"
    ...
  # 2 more, fully populated
```

### 4.7 Schema additions

**`src/starry_lyfe/canon/rich_schema.py`:**
- `Identity` (or whichever class models `identity`): gain optional `is_resident`, `operational_travel`, `cognitive_function_stack`, `dominant_function`, `spouse`, `family_notes`, `siblings`, `astrology`, `children`, `employer`, `unit`, `profile_file`, `profile_version`, `birthplace` (Bina). For dict fields gaining `canonical_label`/`canonical_list` sub-keys, those go via `extra="allow"` already permitted.
- New `RichRuntime` class with `routines: CharacterRoutines | None`, `alicia_communication_distribution: AliciaCommunicationDistribution | None` (Alicia only). Use the narrow Pydantic types from `schemas/routines.py` directly for shape consistency.
- `RichCharacter`: `runtime: RichRuntime | None = None`.
- `Voice` schema: `inference_parameters: VoiceInferenceParams | None` (replacing or extending `runtime_sampling_hints`).
- `BehavioralFramework`: `state_protocols: dict[str, Protocol] | None = None`.

**`src/starry_lyfe/canon/shared_schema.py`:**
- `SharedCanon`: gain `memory_tiers: list[MemoryTier] | None`, `dyads_baseline: dict[str, Dyad] | None`, `interlocks: list[Interlock] | None`. Reuse narrow types from `schemas/{dyads,interlocks}.py`.
- `SharedPair`: gain `character`, `shared_functions`, `what_she_provides`, `how_she_breaks_spiral`, `core_metaphor`, `cadence` fields.

---

## 5. C1 exit criteria checklist

- [x] **AC-C1.1** This mapping doc exists at `Docs/_phases/PHASE_10_5c_MAPPING.md` with 100% mapping coverage. Single-source principle applied.
- [ ] **AC-C1.2** All authoring gaps closed per §4. Each rich character YAML extended; `shared_canon.yaml` extended. **PENDING C1.4 turn after Project Owner ratifies §2.**
- [ ] **AC-C1.3** `runtime.routines` blocks authored verbatim from `routines.yaml`.
- [ ] **AC-C1.4** The 5 rich YAMLs still load via `load_all_rich_characters()` and Pydantic-validate green after authoring changes.
- [ ] **AC-C1.5** Project Owner ratifies §2 decisions (single source of truth principle + 7 specific architectural calls).

---

## 6. Risks and notes (revised)

### 6.1 Bit-identical fixture regression reframed (§2.8)

AC-10.5c.4 in the spec at `PHASE_10.md` reads "Bit-identical output from rewired `load_all_canon()` against pre-rewire fixtures". This wording presumes drift preservation. Per §2.8 it's reframed: every diff between pre-rewire and post-rewire is a drift rationalization reviewed at C2. The spec at `PHASE_10.md` AC-10.5c.4 is amended in C3 governance pass to reflect the new exit criterion: "Every diff between pre-rewire and post-rewire `load_all_canon()` output is documented and Project Owner approved."

### 6.2 Drift rationalizations to expect at C2 review

Pre-known diffs the C2 fixture review will surface:

- **Pair classifications**: narrow → shared_canon strings (e.g., "Intuitive Symbiosis" → "generator-governor polarity"). Per §2.5.
- **Pair mechanisms**: same migration.
- **Pair shared_functions**: e.g., "Fi-Te axis (direct bridge)" — this stays as the canonical string (lifted from pairs.yaml into shared_canon).
- **Heritage strings**: each character's narrow string vs derivation from rich dict. If the `canonical_label` sub-field is authored, derivation is exact and no drift.
- **Shawn `disc`**: rich "CD with atypical Action extension" → narrow "CD with atypical Action extension" (rich wins; narrow currently says "CD with Action extension").
- **Bina `astrology`**: currently narrow `null`; if Bina's rich `identity.zodiac` is renamed and surfaces, narrow becomes `{sun: "Capricorn", moon: "Cancer", venus: "Virgo"}`. **Project Owner ratification call.**

### 6.3 Stale ages in narrow `children`

Bina's son Gavin at age 7, Shawn's daughters Isla 6 / Daphne 4. These are stale relative to birthdates. C1 captures verbatim narrow values into `identity.children`. A future phase may compute from birthdates.

### 6.4 Adapter complexity for shape mismatches

For `heritage`, `profession`, `business`, `languages` — rich uses dict shapes; narrow uses flat strings or simpler lists. Two options per field:

- **Adapter rule**: hardcode derivation in `_build_*` (e.g., `f"{primary} {current_national_identity}"` for heritage). Brittle if rich shape varies across characters.
- **Explicit narrow-source field**: add `identity.heritage.canonical_label` (single string) authored once. Stays as the documented narrow source. Rich dict stays for prompt assembly.

**Recommendation: explicit narrow-source field** (per §3.1 table). It's still ONE source of truth (one authored value per character) — just authored explicitly rather than derived. This minimizes adapter complexity and avoids drift if rich dict structure evolves.

### 6.5 OneDrive transient lock retry

Phase 10.5b R2-F1's `_load_yaml_file()` retry covers all rich YAML reads. C2 hydration inherits the resilience.

### 6.6 The `version` mismatch between rich and narrow

Rich character YAMLs use `version: "7.1-rich"`. Narrow YAMLs use `version: "7.1"`. The narrow Pydantic root objects' `version` field is set as a literal in `_build_*` helpers. Intentional.

### 6.7 Rich `pair_architecture.classification` strings remain in rich YAMLs

Per §2.5, `pair_architecture.classification` is per-woman POV prose. It does NOT hydrate narrow Pair. The strings remain in rich for prompt assembly. They are NOT a source of drift relative to narrow because narrow no longer reads from them.

### 6.8 Rich `behavioral_framework.stress_modes` retirement

Adelia's existing `behavioral_framework.stress_modes` (with `bunker_mode`, `warlord_mode`) gets RETIRED at C1.4 — its content folds into `state_protocols.bunker_mode` (and `warlord_mode`) per §2.7. If any soul-bearing prose in the existing block is judged worth preserving (e.g., the rich `triggers` and `presentation` lists for Bunker Mode), it can move to a separate `behavioral_framework.protocol_prose` sub-block — but `state_protocols` itself remains the SOLE narrow Protocol hydration source.

---

## 7. Next steps after Project Owner ratification

1. **C1.4** — Author all extensions per §4 into the 5 rich character YAMLs and `shared_canon.yaml`. Update `RichCharacter`, `Voice`, `BehavioralFramework`, `SharedCanon`, `SharedPair` Pydantic schemas. Verify `load_all_rich_characters()` + `load_shared_canon()` stay green.
2. **C2** — Capture pre-rewire fixtures. Rewire `load_all_canon()` per §3 mappings. Build path-guard test (AC-10.5c.2). Build diff-review test (re-named from bit-identical) that produces a per-object JSON diff against pre-rewire, with Project Owner approving every diff line.
3. **C3** — Archive the 7 narrow YAMLs. Extend MANIFEST. Update governance docs (CLAUDE.md A19, IMPLEMENTATION_PLAN A3, Vision Appendix B, PHASE_10.md AC-10.5c.4 amendment). Cutover entry in journal.txt.

This mapping doc is the canonical reference for C2 hydration logic. Each `_build_*` helper traces back to one row in §3.

---

**End of PHASE_10_5c_MAPPING.md (R1)**
