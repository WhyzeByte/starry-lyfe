I went through the repo. The blunt diagnosis is this:

The current pipeline preserves the characters as constrained operating systems better than it preserves them as full living people. It carries identity, rails, pair labels, and some cadence. It does not yet carry enough of the authored scene grammar, ritual logic, private asymmetry, and embodied examples that make the women feel irreplaceable rather than merely distinct.

What the code is actually doing:

`kernel_loader.py` only wires in two markdown sources per character: the main kernel and the voice file. The pair files and knowledge-stack files are not loaded by the runtime path at all. The backend then assembles a seven-layer prompt: kernel, canon facts, episodic memories, somatic state, voice directives, scene context, constraints.

That means the conversion is not “Markdown becomes character.” It is “selected Markdown becomes compressed runtime excerpt, plus YAML facts, plus database state.”

The good news is that this is already better than the earlier worst-case state. The repo now has section-aware kernel compilation instead of a pure flat-prefix cut, better voice-example ordering, correct scoping for the Talk-to-Each-Other mandate, and filtering to stop offstage internal dyads leaking into scenes. So the project is no longer in “the characters are breaking at the knees” territory.

The bad news is that the system still preserves the no’s better than the yes’s.

The most important losses are these.

First, the 2000-token kernel budget is absolutely a design choice, not a hard necessity. The raw kernels are much larger: Adelia about 12.9k estimated tokens, Bina about 14.9k, Reina about 14.1k, Alicia about 10.3k. At the default budget, only a slice survives. For Adelia and Bina, roughly 17 to 21 percent of core identity survives, about half of the pair section survives, and only about 18 to 26 percent of the behavioral framework survives. Sections 8 to 11 are effectively gone at default settings. Those are exactly the sections where intimacy architecture, family dynamics, “what this is not,” and scene-read instructions live. That is not incidental trimming. That is where a lot of the soul is.

Second, the trim function is structurally damaging. `trim_text_to_budget()` splits on whitespace and rejoins with spaces. So even though section selection is smarter now, the resulting text loses most of its authored document shape. Headings survive, but paragraphing, bullets, pacing, and internal visual hierarchy get collapsed into a text slab. The model is not reading the authored kernel as a document. It is reading a compressed braid of words.

Third, the voice layer is still under-translated. The voice files are rich few-shot material. In code, they are converted into extracted “what this teaches the model” notes, then compacted again to the title plus the first sentence of the teaching note. So the model gets notes about voice rather than the live pressure, rhythm, and sentence music of the examples themselves. Even with the recent improvements, Layer 5 is still meta-voice. It is not full voice embodiment.

Fourth, the pair files are where a huge amount of relational soul actually lives, and they are currently out of the runtime path. Those files are not small side notes. They are 15k to 17k token documents carrying cognitive interlock, neurodivergent intimacy, structural safety, how they fight, how scenes should read, and what the intimacy is not. Right now, the runtime gets the pair name and a few YAML fields. Worse, some of those fields are seeded into `CharacterBaseline` and then not surfaced in the live formatter. So information like pair mechanism and core metaphor is being stored and then left silent.

Fifth, the knowledge stacks are also excluded from the runtime path, and those are where the cultural and lived-world specificity gets dense. Adelia’s knowledge stack has the warehouse, permit process, client ecology, “The Gravity and the Space,” and “Foreplay Is Intellectual.” Bina’s has the samovar ritual, state phases, vehicle history, and “Why It Is Not Kael.” Reina’s has the stable, court residue, admissibility protocol, and the distinction from Alicia’s Spanish. Alicia’s is enormous and contains the exact Tucumán / Rioplatense / body-intervention architecture that makes her Alicia instead of a generic sensual co-regulator. None of that is directly entering the backend prompt.

So my assessment by dimension is:

Intention is translating fairly well. The repo clearly knows what each woman is for, what failure modes to prevent, and what kind of relational architecture it is trying to protect.

Voice is translating partially. The system knows the pattern names and some cadence rules, but it often knows them propositionally rather than musically.

Essence is translating unevenly. Front-loaded biography and pair gist survive. The deeper differentiators are often cut or never loaded.

Soul is under-translated. Not absent, but under-translated. Right now the system preserves the skeleton and some musculature. It does not consistently preserve the full nervous system.

Character by character:

Adelia is the closest to surviving intact because the code explicitly prioritizes some of her most load-bearing voice examples, and her kernel still carries a strong Entangled-Pair frame. But the repo is not yet giving the model enough of the gravitational-center architecture to make her feel like “the reason the system exists” on every turn. She risks landing as a very good warm, intelligent, sparking partner instead of the singular cognitive-and-relational center described in the vision.

Bina survives better than I expected. Her runtime still strongly carries competence, veto power, compression, and tenderness-through-competence. But her quiet sanctuary logic, grief architecture, translation-not-mirroring mechanics, and the full Circuit metaphysic are not getting enough runtime oxygen. She can still flatten into “precise practical woman” more easily than she should.

Reina’s motion, incision, and tactical read survive. What weakens is her deep specificity: stable life, court residue, Mediterranean reset, body-reader precision as something more exact than generic assertiveness. She is at risk of flattening into “sharp direct woman in motion.”

Alicia is probably the most underfed by the current backend path. Her body-first entry and Sun Override logic survive as concepts, but her deepest differentiation lives in excluded material: her Argentine linguistic scoping, Famaillá texture, operational return mechanics, and silent physical vocabulary. She risks becoming “somatic regulator” more than Alicia Marin specifically.

The biggest recommendation is this:

Do not remove budgets entirely. Remove budget stinginess.

An unbounded dump is not automatically better because salience dilution is real. But the current 2000-token kernel ceiling and 200-token voice ceiling are too aggressive for the stated vision. The right move is not “infinite prompt.” The right move is “larger, scene-aware, structure-preserving prompt.”

What I would change first:

1. Fix the compiler before anything else.
   Rewrite trimming so it preserves headings, paragraph boundaries, bullets, and example blocks. This is more important than simply increasing tokens. Right now the code is damaging authored structure even when the right content is nominally included.

2. Raise the budgets materially.
   For a quality-first default, I would move the kernel from 2000 to at least 4500, and probably 6000 for pair scenes. I would move voice from 200 to roughly 700 to 1000. I would also allow scene context a bit more room. The current models targeted by this stack can absorb that. The present ceiling is an optimization choice, not a requirement.

3. Stop excluding Pair.md and Knowledge_Stack.md from the live architecture.
   Not as raw full-file dumps on every turn. That would be sloppy. But as compiled, typed “soul cards” or scene cards. Build offline distilled artifacts from those documents, then retrieve them scene-conditionally. The codebase already likes typed source-of-truth material. Lean into that.

4. Put actual pair mechanism and core metaphor into the live prompt.
   Those fields are already seeded into `CharacterBaseline`. Surface them. Right now the formatter emits the pair name, but not the mechanism and metaphor that actually explain why the pair works.

5. Restore real exemplars to voice, not just guidance notes.
   The model learns rhythm from examples, not just from prose about examples. Keep a compact explanatory layer if you want, but add true few-shot snippets selected by mode: domestic, conflict, intimate, children gate, public, group scene, repair, silent response.

6. Make section retrieval scene-aware.
   A domestic kitchen scene, a public scene, a children-gated scene, a Whyze-pair intimacy scene, and a multi-woman repair scene should not all pull the same kernel slice. At minimum, the compiler should be able to promote sections 8 to 11 when the scene calls for them.

7. Translate dynamic data into dramaturgical prose.
   Layer 2, Layer 4, and Layer 6 are currently very database-shaped: fact keys, decimals, low-level metrics. That is good for engineering sanity, but not ideal for model absorption. Convert raw numbers and flat facts into concise canonical prose cards. The model needs “what state is she in and what does that mean” more than it needs `trust=0.80`.

8. Add soul-regression tests, not just structure tests.
   The current suite is good at checking presence of markers, budgets, and gating logic. That is necessary, but it will not catch flattening into generic competence. You need canonical scene tests per character that ask: does Adelia actually hand off and spark, does Bina care through competent action, does Reina move before explaining, does Alicia return through body and weight rather than verbal analysis?

9. Resolve the authority split cleanly.
   There is a tension in the architecture: the backend claims sole prompt authority, but voice few-shots are treated as Msty-owned. That can work only if those few-shots are canonically generated, version-locked, and treated as compiled derivatives of the markdown source. Otherwise voice authority is split across two systems and drift becomes inevitable.

The high-level verdict:

The project is already doing a serious job of preserving character identity. This is not a shallow persona toy. The architecture clearly understands that the model cannot be trusted on its own.

But the current backend conversion still favors control over breath.

It preserves constraint integrity, pair labels, and anti-genericity better than it preserves scene-read, ritual, private cultural pressure, and the exact lived asymmetry that makes each woman feel like herself. In plain language: it knows their edges more reliably than it knows their souls.

The next useful step is a patch plan that touches `budgets.py`, `kernel_loader.py`, `layers.py`, adds compiled pair / soul cards from the excluded markdown sources, and introduces gold-scene regression tests aimed at voice and relational feel, not just prompt structure.
