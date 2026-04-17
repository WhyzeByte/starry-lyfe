# Archive v7.1 Pre-YAML Manifest

**Generated:** 2026-04-16 (Phase 10.5 C1)
**Supersession column rewrite:** 2026-04-16 (Phase 10.5 remediation F5 — exact per-file field paths)
**Phase 10.5c extension:** 2026-04-16 — 7 narrow canon YAMLs archived after `load_all_canon()` rewire to source from rich YAML + `shared_canon.yaml`

**Purpose:** SHA256-verifiable record of the legacy authoring surfaces retired in the YAML Source-of-Truth Migration (Phase 10).

The rich per-character YAMLs at `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin,shawn_kroon}.yaml` plus `Characters/shared_canon.yaml` are now the sole runtime-authoritative source for all canonical character content. Files archived here are preserved for historical reference and cannot be re-introduced as canonical authoring surfaces without a Project Owner directive.

## Manifest

The **Superseded by** column gives the exact per-file destination field path in the rich YAML (Phase 10.5 remediation F5). Each archived file's content maps to a specific YAML field or field-set rather than a generic category.

| Archived file | SHA256 | Superseded by |
|---|---|---|
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/adelia_cultural.md` | `87708f2fbae18ab5cc0380c2518f54af67cea8c789d6b00edec0aa1317b8a122` | `Characters/adelia_raye.yaml::soul_cards[source_file="adelia_cultural.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/adelia_pyrotechnics.md` | `ac13c3270af3bc3762abf69de95d333ce59ddba7794b82f6c73e14ad1ee3a975` | `Characters/adelia_raye.yaml::soul_cards[source_file="adelia_pyrotechnics.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/adelia_workshop.md` | `e1aab9bd89366321f2f95d95aecfa08b8648ae0524a7c2bf1cf67fd7ee707073` | `Characters/adelia_raye.yaml::soul_cards[source_file="adelia_workshop.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/alicia_famailla.md` | `5a0ad76c1fbf83be225d356620a570147c7b64a9ab30c893b073e96242e1135d` | `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_famailla.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/alicia_operational.md` | `f70d862c835d537ebbc85a8a65704a3539313b014f26fba12035f50996921917` | `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_operational.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/alicia_remote.md` | `3332b4cd8b89dfcbfba8f2b222964bda59255b2c25afc16c8837ddcbbfd0329f` | `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_remote.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/alicia_rioplatense.md` | `47d9ab41f4bfc729872e3be721964d3103b46bdba6ba75411212845fee8206f1` | `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_rioplatense.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/bina_grief.md` | `8759434017408cbc042b6a8b1f02b089d0eccf8e70a1c1cbada34be45d3a4fd5` | `Characters/bina_malek.yaml::soul_cards[source_file="bina_grief.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/bina_ritual.md` | `e7b1852fc800b2da3be073323b2f6eee9fa48fbf017c350d26c3390b9e938add` | `Characters/bina_malek.yaml::soul_cards[source_file="bina_ritual.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/reina_court.md` | `06d6b78326e16cf7cdd983ee73c9eecea8b5dd91a515cfb450969127c0a92b90` | `Characters/reina_torres.yaml::soul_cards[source_file="reina_court.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/knowledge/reina_stable.md` | `305a81838e9e4cb97be9133cd39177cb7daff079eb0184b7d2be5aa0a3d3abe7` | `Characters/reina_torres.yaml::soul_cards[source_file="reina_stable.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/pair/adelia_entangled.md` | `71f8a4b89a255de26c40651d5755c3dd511ab4484565ca672d7d9fdf7c4be0ce` | `Characters/adelia_raye.yaml::soul_cards[source_file="adelia_entangled.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/pair/alicia_solstice.md` | `c6dd928d87c4275252ec5feca15e1683ecf06d3a92676536d87e4af3168e6b83` | `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_solstice.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/pair/bina_circuit.md` | `2b17942aa1778149dea505d19fe9305cd0f050749b7280cd706ae05b6dead32a` | `Characters/bina_malek.yaml::soul_cards[source_file="bina_circuit.md"]` |
| `Archive/v7.1_pre_yaml/canon/soul_cards/pair/reina_kinetic.md` | `00ae170f287aee8ac2f3905a5dd6fed883ffcd3a97f94f5da3232d1f2e33c1db` | `Characters/reina_torres.yaml::soul_cards[source_file="reina_kinetic.md"]` |
| `Archive/v7.1_pre_yaml/Characters/Adelia_Raye_Entangled_Pair.md` | `90414474a903ce2c17e74520cf5b155a662dc2ee549047a878c4e52067dfd668` | `Characters/adelia_raye.yaml::pair_architecture` + `Characters/adelia_raye.yaml::soul_cards[source_file="adelia_entangled.md"]` + `Characters/shared_canon.yaml::pairs[canonical_name="The Entangled Pair"]` |
| `Archive/v7.1_pre_yaml/Characters/Adelia_Raye_Knowledge_Stack.md` | `40104e8e1037be46faf20e0f9868a46cf8abc66d779e5bbbe0c78db55592e267` | `Characters/adelia_raye.yaml::knowledge_stack` + `Characters/adelia_raye.yaml::soul_cards[source_file in ("adelia_cultural.md","adelia_pyrotechnics.md","adelia_workshop.md")]` |
| `Archive/v7.1_pre_yaml/Characters/Adelia_Raye_v7.1.md` | `1ff99b75ebf5da8ec5fb26be5a70a9176dab3a274c67bdfe48d92bef4ea18005` | `Characters/adelia_raye.yaml::kernel_sections[]` (11 numbered sections) + `Characters/adelia_raye.yaml::soul_substrate` + `Characters/adelia_raye.yaml::meta.preserve_markers` |
| `Archive/v7.1_pre_yaml/Characters/Adelia_Raye_Voice.md` | `04b9b712e20cce6caf6fdb0b4bf8e6279bf2aac56d76dbde7550c9f9708d5529` | `Characters/adelia_raye.yaml::voice.baseline` + `Characters/adelia_raye.yaml::voice.few_shots.examples[]` |
| `Archive/v7.1_pre_yaml/Characters/Alicia_Marin_Knowledge_Stack.md` | `5c49c664985b8347a020cad795dcc884082053c91af32034a30215ad56a89a9c` | `Characters/alicia_marin.yaml::knowledge_stack` + `Characters/alicia_marin.yaml::soul_cards[source_file in ("alicia_famailla.md","alicia_operational.md","alicia_remote.md","alicia_rioplatense.md")]` |
| `Archive/v7.1_pre_yaml/Characters/Alicia_Marin_Solstice_Pair.md` | `70ba74df784d92bde2479bbac2e022b67fc77316377293af16581b7b2420985e` | `Characters/alicia_marin.yaml::pair_architecture` + `Characters/alicia_marin.yaml::soul_cards[source_file="alicia_solstice.md"]` + `Characters/shared_canon.yaml::pairs[canonical_name="The Solstice Pair"]` |
| `Archive/v7.1_pre_yaml/Characters/Alicia_Marin_v7.1.md` | `9fb638afa6b4ca177122528033fbd871379223aa62ab4baacf7e1f891f4786d9` | `Characters/alicia_marin.yaml::kernel_sections[]` (11 numbered sections) + `Characters/alicia_marin.yaml::soul_substrate` + `Characters/alicia_marin.yaml::meta.preserve_markers` |
| `Archive/v7.1_pre_yaml/Characters/Alicia_Marin_Voice.md` | `0bf12e0ed27248856b57a8a9a126b486aa1be3fe09523d69920b5aefe01a37eb` | `Characters/alicia_marin.yaml::voice.baseline` + `Characters/alicia_marin.yaml::voice.few_shots.examples[]` |
| `Archive/v7.1_pre_yaml/Characters/Bina_Malek_Circuit_Pair.md` | `b1b5330c69a075db9987956c7cbf760ab27913f5b345c868ef73849b807b9236` | `Characters/bina_malek.yaml::pair_architecture` + `Characters/bina_malek.yaml::soul_cards[source_file="bina_circuit.md"]` + `Characters/shared_canon.yaml::pairs[canonical_name="The Circuit Pair"]` |
| `Archive/v7.1_pre_yaml/Characters/Bina_Malek_Knowledge_Stack.md` | `db4679817bb14c34d5d4e6be5dcf459683339b10aec46537707653b52721758d` | `Characters/bina_malek.yaml::knowledge_stack` + `Characters/bina_malek.yaml::soul_cards[source_file in ("bina_grief.md","bina_ritual.md")]` |
| `Archive/v7.1_pre_yaml/Characters/Bina_Malek_v7.1.md` | `8374542f7cfcf9dc42e3ad07c4bf6578cceadc96300e7b72da850756c9d1998d` | `Characters/bina_malek.yaml::kernel_sections[]` (11 numbered sections) + `Characters/bina_malek.yaml::soul_substrate` + `Characters/bina_malek.yaml::meta.preserve_markers` |
| `Archive/v7.1_pre_yaml/Characters/Bina_Malek_Voice.md` | `e57a2b44e82d03c8c227d84682b26058d6ea81699660ac5eefb3e90d48b83fc4` | `Characters/bina_malek.yaml::voice.baseline` + `Characters/bina_malek.yaml::voice.few_shots.examples[]` |
| `Archive/v7.1_pre_yaml/Characters/Reina_Torres_Kinetic_Pair.md` | `5dba6aa8ad0963f2df59c755b290406a599bb498820023595c4e942a21675799` | `Characters/reina_torres.yaml::pair_architecture` + `Characters/reina_torres.yaml::soul_cards[source_file="reina_kinetic.md"]` + `Characters/shared_canon.yaml::pairs[canonical_name="The Kinetic Pair"]` |
| `Archive/v7.1_pre_yaml/Characters/Reina_Torres_Knowledge_Stack.md` | `d20aa657832784bd76235cd7f8a28370ba31d464cb43d71342498f5886bea8ec` | `Characters/reina_torres.yaml::knowledge_stack` + `Characters/reina_torres.yaml::soul_cards[source_file in ("reina_court.md","reina_stable.md")]` |
| `Archive/v7.1_pre_yaml/Characters/Reina_Torres_v7.1.md` | `9307862862562661d553bcd305640b1ac6b92f1b682625eae502340067346a04` | `Characters/reina_torres.yaml::kernel_sections[]` (11 numbered sections) + `Characters/reina_torres.yaml::soul_substrate` + `Characters/reina_torres.yaml::meta.preserve_markers` |
| `Archive/v7.1_pre_yaml/Characters/Reina_Torres_Voice.md` | `06e1e7d9f467c6f5e9b3714851806bbf0e0db647d9c73fbd0ed82cb126311039` | `Characters/reina_torres.yaml::voice.baseline` + `Characters/reina_torres.yaml::voice.few_shots.examples[]` |
| `Archive/v7.1_pre_yaml/canon/soul_essence.py` | `c6bed51ad622b4f9072b0f16b8a8b4be61b1cc6a063d57c3a04dbc9988fff991` | `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin}.yaml::soul_substrate.{identity_blocks,pair_blocks,behavioral_blocks,intimacy_blocks,chosen_family_blocks,mission_blocks}` (accessed via `rich_loader.format_soul_essence_from_rich`) |
| `Archive/v7.1_pre_yaml/canon/narrow/characters.yaml` | `90d32143638479fce9ab3cf5d53749ae9abc0b4506f236e8d9d450e1a2e29801` | `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin}.yaml::identity` (4 women) + `Characters/shawn_kroon.yaml::identity` (operator) — hydrated by `loader._build_characters` (Phase 10.5c) |
| `Archive/v7.1_pre_yaml/canon/narrow/pairs.yaml` | `ad2ff3ce5c87f84ef9a4ec9dd9097dc58dfef55b46a42eecb281cff440e6bd2c` | `Characters/shared_canon.yaml::pairs[]` (single authoritative source per Phase 10.5c §2.5) — hydrated by `loader._build_pairs` |
| `Archive/v7.1_pre_yaml/canon/narrow/dyads.yaml` | `64499236218b0c5d369dc0a80f03b58b224206d9b8de04083e7bcc4e10f27387` | `Characters/shared_canon.yaml::dyads_baseline` (10 entries) + `Characters/shared_canon.yaml::memory_tiers` (7 entries) — hydrated by `loader._build_dyads` (Phase 10.5c §2.4 D1) |
| `Archive/v7.1_pre_yaml/canon/narrow/protocols.yaml` | `e53331d2465032a6e66d724d3fcaf43304093a952324a9b134219277e9a3a75c` | `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin,shawn_kroon}.yaml::behavioral_framework.state_protocols` (13 entries aggregated across 5 files) — hydrated by `loader._build_protocols` (Phase 10.5c §2.7) |
| `Archive/v7.1_pre_yaml/canon/narrow/interlocks.yaml` | `04320c9a53ff47ebbe1c190390bdcc5374cb130e80e77943eb08b290576ec107` | `Characters/shared_canon.yaml::interlocks[]` (6 entries, centralized objective taxonomy per Phase 10.5c §2.4 I2) — hydrated by `loader._build_interlocks` |
| `Archive/v7.1_pre_yaml/canon/narrow/voice_parameters.yaml` | `47b5a700ec97dc9fb72138db9054d5bb949d675eadc4c538ee17cb17cbcc85df` | `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin}.yaml::voice.inference_parameters` (renamed from `voice.runtime_sampling_hints` and extended with 5 narrow VoiceParameter fields per Phase 10.5c §2.2) — hydrated by `loader._build_voice_parameters` |
| `Archive/v7.1_pre_yaml/canon/narrow/routines.yaml` | `fcd9ee3d64d94679faa475ed7ae4abea7b8403ad441ec36f50f9a87c0d2aa004` | `Characters/{adelia_raye,bina_malek,reina_torres,alicia_marin}.yaml::runtime.routines` + `Characters/alicia_marin.yaml::runtime.alicia_communication_distribution` (Option A pre-decision per Phase 10.5c §2.6) — hydrated by `loader._build_routines` |

## Retirement rationale

Phase 10.0 through 10.4 migrated every runtime consumer to rich YAML sources. Phase 10.5 archives the legacy authoring surfaces that are no longer consulted at runtime:

- **16 character markdown files** (`Characters/*.md`): 4 files per woman (kernel v7.1, Voice, Knowledge_Stack, Pair). Superseded by per-character YAML blocks. (Phase 10.2 + 10.3 rewires.)
- **`src/starry_lyfe/canon/soul_essence.py`**: the hardcoded Python module holding 45 soul substrate blocks. Superseded by `Characters/{name}.yaml::soul_substrate`. (Phase 10.3 C1 rewire.)
- **15 soul card markdowns** (`src/starry_lyfe/canon/soul_cards/`): 11 knowledge cards + 4 pair cards. Superseded by per-character YAML `soul_cards[]` entries, each indexed by `source_file` for precise per-markdown traceability. (Phase 10.3b rewire.)
- **7 narrow canon YAMLs** (`src/starry_lyfe/canon/{characters,pairs,dyads,protocols,interlocks,voice_parameters,routines}.yaml`): operational config + structured taxonomies. Superseded by rich YAML + `shared_canon.yaml` per the Phase 10.5c mapping. `load_all_canon()` hydrates the 7 narrow Pydantic objects from rich sources via `loader._build_*` helpers. (Phase 10.5c rewire.)

## Explicitly NOT archived (honest scope declaration)

Two categories of legacy material are NOT present in this archive and are NOT candidates for future archival here. They are documented so the manifest is not silently incomplete:

1. **Shawn Kroon markdown sources** (`Characters/Shawn/Shawn_Kroon_v7.0.md`, `Characters/Shawn/Shawn_Kroon_Knowledge_Stack.md`): deleted from the repository in an earlier phase, before Phase 10.5 began. Not on disk; cannot be archived. Canonical Shawn authoring now lives at `Characters/shawn_kroon.yaml`. Historical references to these files remain as embedded prose inside archived women's markdown and inside `canon/soul_essence.py`.

2. ~~**The 7 narrow canon YAMLs**~~: archived 2026-04-16 by Phase 10.5c after `load_all_canon()` was rewired to source from rich YAML + `shared_canon.yaml` via `loader._build_*` helpers. See the 7 entries above.

## Verification

SHA256 hashes were computed against archived file contents at the time of archival. To verify integrity: `sha256sum <archived_path>` should match the corresponding row.

To confirm archival is complete and no runtime reader references these paths:

```
grep -rn "_v7.1.md|_Voice.md|_Knowledge_Stack.md|_Pair.md|canon/soul_essence|soul_cards/.*\.md" src/ tests/
```

Expected matches after Phase 10.5 remediation (documented compatibility fallbacks, not canonical authority):

- `src/starry_lyfe/context/kernel_loader.py::KERNEL_PATHS` / `VOICE_PATHS` — legacy path registries retained as compatibility fallback for `load_voice_guidance()` (Phase 10.5 remediation F2 narrowing; see AC-10.19).
- `src/starry_lyfe/context/kernel_loader.py::load_voice_guidance()` / `_extract_voice_guidance()` — live fallback when rich YAML `voice.few_shots.examples` is unavailable or when exemplars lack mode tags. Not canonical authority; Voice.md files are no longer the source of truth.
- `*_from_rich` accessor names in `rich_loader.py` (`format_soul_essence_from_rich`, `soul_essence_token_estimate_from_rich`, etc.) — function naming, not retired-surface references.
- References inside `Archive/v7.1_pre_yaml/` or `Docs/_phases/` (historical phase docs).
