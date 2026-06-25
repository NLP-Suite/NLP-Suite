# Design Spec — Semantic Aggregation GUI (WordNet · VerbNet · FrameNet)

A single hub to classify/aggregate corpus words into semantic categories using the three pillars of
lexical semantics, and to build word lists from those categories. Replaces "which resource do I open?"
with one Resource selector. The mature WordNet GUI stays as-is and is **linked**, not dismantled.

Proposed scripts: `knowledge_graphs_main.py` + `knowledge_graphs_util.py`.
Menu label: **"Semantic aggregation (WordNet, VerbNet, FrameNet)"**.
Existing `knowledge_graphs_WordNet_*` becomes the linked **advanced WordNet workbench**.

---

## 1. The unifying model — 2 operations × 3 resources × 2 word classes

| | builds on | NOUN | VERB | shape |
|---|---|---|---|---|
| **WordNet**  | hypernym hierarchy | yes | yes (shallow) | HIERARCHICAL — climb to an anchor at ANY level |
| **VerbNet**  | Levin classes      | no  | yes | FLAT — verb *is in* class (e.g. murder-42.1) |
| **FrameNet** | semantic frames    | yes (event nouns!) | yes | FLAT — word *evokes* frame (e.g. Killing) |

Two operations:
- **(A) Aggregate a corpus** (Zoom OUT/UP): word list -> each word's category + frequency chart.
- **(B) Build a word list** (Zoom IN/DOWN): a category -> all words in it.

The asymmetry matters for the UI: WordNet asks "which anchor / what level?"; VerbNet/FrameNet just map
to the class/frame (no levels), but add a **meta-category** layer to roll classes/frames up into YOUR labels.

---

## 2. GUI panels (functional — you place the widgets)

Standard NLP Suite I/O header (input file/dir, output dir, config).

**Panel 1 — Knowledge base & word class**
- Dropdown **Knowledge base**: WordNet | VerbNet | FrameNet
- Dropdown **Word class**: NOUN | VERB
- Auto-constrain: VerbNet greys out NOUN; the rest allow both. (logic = mine)

**Panel 2 — Operation** (two checkboxes/radio)
- (A) Aggregate corpus words into categories
- (B) Build a word list from a category

**Panel 3 — Category / anchor specification** (context-sensitive on Panel 1):
- WordNet: **Anchor synset(s)** entry (e.g. `person, artifact, ethnic_group`) + the top-level supersense dropdown — same behaviour as today's "YOUR synset(s)" / "Top-level synset". Blank = top supersenses.
- VerbNet: **VerbNet class(es)** entry (e.g. `42.1, 18.1`) — blank = each verb's own class.
- FrameNet: **Frame(s)** entry (e.g. `Killing, Attack`) — blank = each word's own frame.

**Panel 4 — Meta-categories (the key new layer)**
- File selector: a **meta-category map** CSV with columns `category,label`
  e.g. `Killing,Violence` / `Attack,Violence` / `murder-42.1,Violence` / `person,People` / `artifact,Things`.
- Optional. If present, output adds a **Meta-label** column and rolls frequencies up by label.
- This is what turns frames/classes/synsets into YOUR content-analysis codes.

**Panel 5 — Disambiguation** (VerbNet/FrameNet only):
- Radio: **Sense disambiguation** = "From SRL output (disambiguated)" | "Unambiguous only (gated)" | "First sense".
  - "From SRL output" is enabled when the input csv has a `VerbNet class` / `FrameNet frame` column (i.e. an SRL result) — uses it directly, no guessing.
  - For plain lemma lists, "Unambiguous only" (recommended) vs "First sense".

**Panel 6 — Link to the WordNet workbench**
- Button **"Open WordNet tools (advanced)"** -> launches existing `knowledge_graphs_WordNet_main` for WordNet-only depth (proper/improper noun extraction, rich hyponym list builder, by-sentence viz). Nothing removed from there.

**Panel 7 — Validation mode (PC-ACE hand codes)** (optional checkbox)
- File selector: a **hand-coded** CSV `word,hand_label`.
- Output: for each word, the resource-derived category + meta-label vs the hand_label, flagging mismatches — turns 20 years of hand coding into something checkable.

Standard footer: charts package, data transformation, RUN, open-output.

---

## 3. Inputs / Outputs

Inputs:
- Operation A: csv with a **word column** (lemmatized) — the noun/verb lemma lists the Suite already
  extracts from a CoNLL table, OR an **SRL output csv** (for disambiguated VerbNet/FrameNet).
- Operation B: just the category spec (Panel 3).
- Optional: meta-category map csv (Panel 4); hand-code csv (Panel 7).

Outputs (uniform across resources):
- **Aggregation csv**: `Word, Category, [Meta-label], [Intermediate synsets — WordNet only], Document`.
- **Frequency chart**: by Category, and by Meta-label when provided.
- **List csv** (Operation B): terms in the category (one-column + a verbose version, as WordNet does now).
- **Validation csv** (Panel 7): `Word, Resource category, Meta-label, Hand label, Match?`.

---

## 4. Backend I build (logic; routes through machinery we already have)

- Dispatcher `aggregate(resource, pos, words, spec, meta_map, disambig, srl_cols)`.
- **WordNet**: reuse `aggregate_GoingUP` + `_climb_to_target` (DONE).
- **VerbNet**: `aggregate_verbnet(words)` — NLTK `verbnet.classids(lemma)`; if input is SRL output, use its `VerbNet class` column (disambiguated). Gating for lemma lists.
- **FrameNet**: `aggregate_framenet(words, pos)` — NLTK `framenet`; if SRL output, use its `FrameNet frame` column; else the gated `fn_lemma_frame` table (extend it to include unambiguous **nouns** — currently verbs only).
- **Meta rollup**: apply `{category -> label}` and re-aggregate frequencies.
- **Validation**: join hand-codes to derived categories, flag mismatches.

---

## 5. Data sources
- WordNet, VerbNet, FrameNet all via NLTK (`wordnet`, `verbnet`, `framenet_v17`). VerbNet/FrameNet need
  the NLTK data downloaded once (add to the Suite's nltk-resource bootstrap).
- The SRL side already bundles the SemLink maps for disambiguation; this GUI's lemma-list route uses NLTK directly (polysemous -> gated).

---

## 6. Phased plan
1. **Hub + Operation A** (aggregate) for all three resources on lemma lists, + the WordNet link. Reuses existing backends. Smallest useful slice.
2. **Meta-categories** (Panel 4 rollup).
3. **Validation mode** (Panel 7 — PC-ACE hand codes).
4. **Operation B** unified (build list across resources); **FrameNet event-noun** aggregation; optionally migrate WordNet options into the hub.

---

## 7. Open design choices for you
- Keep Operation B (list building) in the hub, or leave it solely in the WordNet workbench for now?
- Meta-category map as a file only, or also an in-GUI editable table?
- Should "Word class" auto-switch the Knowledge base options, or just grey out invalid combos?

---

## 8. Word Sense Disambiguation (this GUI) vs Word Sense Induction (Word2Vec GUI)

These are **different tasks**, not duplicates — persisted here so the distinction is never lost again.

### This GUI — Word Sense **Disambiguation** (WSD)
Given a word **in context**, assign it to a sense from a **known, predefined inventory** (a WordNet **synset**, VerbNet **class**, or FrameNet **frame**). The point is aggregation **precision**: pick the right predefined category so the wrong sense doesn't pollute the counts (e.g. *bank* → the financial-institution synset, not the river bank; *hang* → the correct VerbNet class).
- **WordNet**: Lesk-family WSD via **`pywsd`** — disambiguate each noun/verb against its sentence, then aggregate to the chosen synset's category. Needs context → operates on text / a CoNLL table, **not** a bare lemma list.
- **VerbNet / FrameNet**: already disambiguated by the **SRL / SemLink** route (PropBank sense → VerbNet class → FrameNet frame); for those the WSD checkbox is a no-op — use the SRL output.
- It maps **into** a lexical resource; it is the precision layer for aggregation.

### Word2Vec GUI — Word Sense **Induction** (WSI), BERT-based
**Unsupervised, no predefined inventory.** Uses **BERT contextual embeddings + clustering** to **discover** how many distinct senses a word has **in your corpus** and which occurrences belong to which. It does not map to WordNet/VerbNet/FrameNet — it **induces** senses from the data itself.

### One line
WSD asks *"which **known** sense is this?"* (resource-anchored, for aggregation). WSI asks *"what senses does this word have **in my corpus**?"* (data-driven discovery). Complementary, not redundant.

### References
- Lesk, M. (1986). *Automatic sense disambiguation using machine readable dictionaries: how to tell a pine cone from an ice cream cone.* SIGDOC.
- Banerjee, S. & Pedersen, T. (2002). *An adapted Lesk algorithm for word sense disambiguation using WordNet.* CICLing.
- Tan, L. (2014). *pywsd: Python Implementations of Word Sense Disambiguation (WSD) technologies.* github.com/alvations/pywsd
- Navigli, R. (2009). *Word Sense Disambiguation: A Survey.* ACM Computing Surveys 41(2). (WSD vs WSI overview)
- Devlin, J. et al. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.* NAACL. (the contextual embeddings behind the Word2Vec GUI's WSI)

---

## 9. CoNLL handoff — consolidating CoNLL-based aggregation (PROPOSED, not yet decided)

**Problem.** Several hub options *demand a CoNLL table* (Extract nouns/verbs, **WSD**, **Zoom OUT/UP by Sentence ID**). That's confusing in an "aggregation" GUI, and those operations are exactly what the **CoNLL Table Analyzer** is for (it already has the multi-resource "Classification of Nouns & Verbs via WordNet/VerbNet/FrameNet").

**Decision (shape).** CoNLL-input work gets **one home** — the CoNLL Table Analyzer. The hub keeps only the *no-CoNLL* resource/word-list work (Zoom IN/DOWN, Zoom OUT/UP from a lemma-list csv, Annotate). The analyzer's checkbox becomes a **dropdown: "Classify nouns & verbs (WordNet · VerbNet · FrameNet)" → { first-sense (fast) | sense-disambiguated / WSD | by sentence index }**, all sharing the one CoNLL input; its hover/?HELP names the lexical databases (inbound discoverability).

**The hub launcher (outbound discoverability + smooth pipeline).** A single hub control — *"CoNLL-based tools of semantic aggregation: run the default parser and open the CoNLL Table Analyzer."* On activation:
1. **Look for an existing CoNLL** for the current corpus: glob the current IO **output dir** for `*_CoNLL*.csv` matching the corpus base name (the parser auto-writes CoNLL into a `<annotator>_CoNLL` subdir — `Stanza_util.make_output_subdirectory(label=annotator+"_CoNLL")`).
   - **exactly one** → grab it.
   - **none** → ask: *1. run the parser  ·  2. open the analyzer and select a CoNLL* (don't silently re-parse a big corpus).
   - **several** (different annotators) → newest, or ask.
2. **Open the analyzer preloaded** with that CoNLL via the existing launch plumbing: `run_script("CoNLL_table_analyzer_main.py", conll_path)` — `run_script(script, *extra_args)` already forwards args as argv (`cmd=[python, script_path]+list(extra_args)`).
3. **Analyzer argv intake** (~3 lines at GUI startup): if a CoNLL path is on `sys.argv`, set the input-file var. The analyzer reads input from the shared IO config today and does **not** read argv — this is the only new code in the analyzer. (Chosen over writing the shared config, which would mutate state every other GUI reads.)

**Resolved seams.** The by-sentence **second input** (the aggregation dictionary from Zoom OUT/UP) is no longer the hub's concern — the analyzer's dropdown prompts for it when that option is picked. No duplicated WSD/by-sentence logic; deleting those two hub checkboxes also *shrinks the row stack* and removes part of the ?HELP-alignment problem.

**Connective tissue.** The shared **"Lexical databases (WordNet, VerbNet, FrameNet)"** TIPS states the pipeline once: *text → parse → CoNLL → CoNLL analyzer (classify / WSD / by-sentence); category/word-list work → Semantic Aggregation hub.*

**Status / ownership.** Logic (glob-match, launcher helper, argv intake) = mine; **widget placement of the launcher control = user's** (layout). First tryable slice: the argv intake + the glob-and-launch helper, wired by the user to a control they place; nothing moved/deleted until the handoff is proven.

### 9a. Port spec — WSD + by-Sentence-ID into the CoNLL Table Analyzer (NOT lost, just relocating)

The hub's WSD and by-Sentence-ID checkboxes are now commented out (vars kept `=0` so `run()` stays valid; handlers dormant). **The algorithms are NOT in those commented lines** — they live in intact, importable util functions. The analyzer just calls them, behind a dropdown **"Classify nouns & verbs" → { first-sense (existing analyzer classify) | sense-disambiguated / WSD | by sentence index }**. The analyzer's input is already a CoNLL, so the `check_CoNLL` guard becomes trivially satisfied.

**WSD option** (from semantic_aggregation_main.py:166-180):
```
outputFiles = semantic_aggregation_util.wsd_aggregate_WordNet(csv_file, outputDir, noun_verb, chartPackage, dataTransformation)
# returns a list -> filesToOpen.extend(outputFiles)
```
Needs: `noun_verb` (NOUN/VERB selector), `chartPackage`, `dataTransformation` — all present in the analyzer. WordNet-only (VerbNet/FrameNet = SRL route).

**by-Sentence-ID option** (from semantic_aggregation_main.py:153-164 + the second-input prompt at 772-803):
```
outputFilename = IO_files_util.generate_output_file_name(csv_file, outputDir, '.csv', 'WordNet', 'conll')
outputFiles = semantic_aggregation_WordNet_util.Wordnet_bySentenceID(
                  csv_file, dict_WordNet_filename_var, outputFilename, outputDir,
                  noun_verb, openOutputFiles, chartPackage, dataTransformation)
# return may be str OR list -> append if str else extend
```
**The seam:** by-Sentence-ID needs a SECOND input — the **aggregation-dictionary csv** (the Zoom OUT/UP output that classified lemmas into categories), prompted into `dict_WordNet_filename_var`. In the hub this was a two-step prompt (CoNLL, then dict file). In the analyzer the CoNLL is already the input, so only the **dict-file prompt** moves over (fired when the by-sentence dropdown option is chosen). The dict must contain the same NOUN/VERB class as selected.

Both `Wordnet_bySentenceID` (semantic_aggregation_WordNet_util) and `wsd_aggregate_WordNet` (semantic_aggregation_util) are unchanged and stay where they are; only the dispatch + the dict-file prompt relocate into the analyzer.
