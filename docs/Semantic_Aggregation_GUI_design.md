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
