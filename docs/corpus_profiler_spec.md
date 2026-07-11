# Corpus Profiler — Specification (draft for review)

**Script:** `corpus_profiler_main.py` (GUI + `run()`) · `corpus_profiler_util.py` (orchestration + report)
**Output:** `<outputDir>/NLP_corpus_profile.html` — the **one** file auto-opened; everything else stays in subfolders.
**Replaces:** `whats_in_your_corpus_main.py` (retire + repoint the menu once this is ready).

---

## 1. Purpose (the framing we agreed on)

A **Corpus Profiler**: run a battery of analyses with sensible **defaults** to give a fast overview of a corpus. Its deliverable is a single navigable **HTML report** with headline stats + links to every underlying output file. The 200+ output files become **depth on demand** hanging off the report — not a flood. This is the one thing the main menu can't do (the menu only *opens* tools), and it's the natural onboarding/overview front door.

---

## 2. GUI design — grouped checkbox + dropdown (question-taxonomy)

One **checkbox + dropdown** per category (like the NER dropdowns). Each dropdown has a `*` (run all in category); a top-level "run everything" is the union of the ticked categories with `*`. Labels are **user questions**, not technology. Rule: **cap each dropdown ≤ ~12 items**; if a category exceeds that, split it.

| # | Checkbox (question) | Dropdown items | Invocation |
|---|---|---|---|
| 1 | **How big / how varied?** (Counts & measures) | statistics (sentences/words/syllables), n-grams, hapax legomena, sentence length, line length, language detection | **batch** |
| 2 | **What's the vocabulary like?** (Vocabulary) | vocabulary richness (TTR / Yule's K), short / vowel / capital-initial words, punctuation-as-pathos, unusual words (NLTK), abstract/concrete | **batch** |
| 3 | **Grammar & structure** (Syntax) | POS, dependency (CoNLL), clause, noun/verb/adjective/adverb, function words, **sentence complexity**, **text readability** † | **batch** (parse → CoNLL → analyzers) |
| 4 | **What do the words mean?** (Semantics) | WordNet/VerbNet/FrameNet classes, WSD, word embeddings, semantic similarity, nominalization | **mixed** (WordNet classes batch; embeddings/WSD open-GUI for now) |
| 5 | **What is it about?** (Topics) | Topic modeling (BERT / Gensim / MALLET) | **open-GUI** |
| 6 | **Who, what, where, when** (Entities) | people & organizations, gender, dates & time, locations, nature | **batch** (CoreNLP/Stanza NER) |
| 7 | **Who did what to whom?** (Narrative) | SVO, **SRL**, coreference, dialogue/quotes, 5 Ws | **mixed** (SVO batch; SRL isolated-env batch; coref open-GUI) |
| 8 | **How does it feel?** (Sentiment) | BERT / Stanza / spaCy / VADER / NRC / SentiWordNet | **open-GUI** (some batchable) |
| — | **Where? (maps)** (GIS) | geocode + maps + distances | open-GUI / pipeline |
| — | **See it** (Visualization) | data visualization GUI | open-GUI |

Per category: the **checkbox runs with defaults**; a small **"⚙ open GUI"** affordance jumps to the full tool for options (keeps *run* vs *open* unambiguous — the mistake to avoid).

† **text readability** is filed under Syntax (it's largely a sentence-structure measure) but arguably belongs in **Semantics** — it's about how *understandable* the text is. Open decision (§8.1).

**Change log vs first draft:** the old "Style & vocabulary" category was split — a standalone **Vocabulary** group (2) holds the word-level lexical measures, while **sentence complexity** and **text readability** moved up to **Syntax** (3) as sentence-level structure. "Style" as a bucket dissolves into those two.

Standard I/O row: input = corpus dir of `.txt` (or a single file), output dir, and the **configured NLP package + language** (read once, not per-tool).

---

## 3. Architecture — how it actually runs

### 3.1 Config is owned by the profiler, read once
```
config_filename                                     = GUI_util.config_filename_selected_config.get()
package, language, memory_var, export_json_var,
  document_length_var, limit_sentence_length_var,…  = config_util.read_NLP_package_language_config()
date options                                        = config_util.get_date_options(...)
inputDir / inputFilename                            = corpus (txt)
outputDir                                           = make_output_subdirectory(..., 'corpus_profile')
chartPackage / dataTransformation                   = GUI defaults ('Excel' / 'No transformation')
openOutputFiles = False   # CRITICAL: tools must NOT open their own files; only the report opens
```

### 3.2 Two invocation types (the crux)
The current `whats_in_your_corpus.run()` already proves both:

- **BATCH** — call the underlying `*_util` function directly with explicit args; collect the returned file list. These run headless and give us files for the report. *(This is the bulk and is what makes a real profile possible.)*
- **OPEN-GUI** — `run_script_util.run_script("X_main.py")` just opens the tool's window. Cannot be batched into the report without refactoring that tool to expose a headless entry point.

**Design rule:** the profiler's `*` auto-run includes only **batch** analyses. Open-GUI analyses are surfaced in the report as **"open the X tool"** buttons (and their category checkbox opens the GUI rather than claiming to have run it). We migrate open-GUI → batch tool-by-tool over time (this dovetails with the run()/lambda refactor).

### 3.3 The registry (`corpus_profiler_util.py`)
A single table maps `analysis_id → { category, kind: 'batch'|'gui', fn, default_kwargs, label }`. `corpus_profiler_util.run_profile(selection, ctx)`:
1. For each selected batch analysis, `fn(**ctx, **default_kwargs)` → append `(analysis_id, returned_files)`.
2. For each selected gui analysis, record a "open GUI" entry (no run).
3. Build `NLP_corpus_profile.html` from the collected results + corpus header stats.
4. Open **only** the report.

`ctx` carries the shared args (window, inputFilename, inputDir, outputDir, config_filename, openOutputFiles=False, chartPackage, dataTransformation, language, package, memory_var, …).

> The registry can be **lifted almost verbatim** from `whats_in_your_corpus.run()` — it already contains the exact working calls (below). We're refactoring that dispatch into a clean table, not inventing calls.

---

## 4. Batch registry — harvested from the current `run()` (grounded, not guessed)

Common context args abbreviated as `⟨ctx⟩ = (window, inputFilename, inputDir, outputDir, config_filename, openOutputFiles=False, chartPackage, dataTransformation)`.

| Analysis | Function call | Notes |
|---|---|---|
| Corpus statistics | `statistics_txt_util.compute_corpus_statistics(window, inputFilename, inputDir, outputDir, config_filename, False, …)` | sentences/words/syllables |
| n-grams | `statistics_txt_util.compute_character_word_ngrams(window, inputFilename, inputDir, …)` | |
| Sentence length | `statistics_txt_util.compute_sentence_length(inputFilename, inputDir, outputDir, config_filename, chartPackage, dataTransformation)` | |
| Line length | `statistics_txt_util.compute_line_length(window, config_filename, inputFilename, inputDir, outputDir, False, …)` | |
| Language detection | `file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir, config_filename, …)` | |
| Sentence complexity | `statistics_txt_util.compute_sentence_complexity(window, inputFilename, …)` | |
| Vocabulary richness (Yule/TTR) | `statistics_txt_util.yule(window, inputFilename, inputDir, outputDir, config_filename)` | |
| Word-shape (short/vowel/capital/punctuation) | `statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir, config_filename, False, chartPackage, dataTransformation, <which>)` | one fn, switched by the menu string |
| Unusual words | `file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir, config_filename, False, chartPackage, dataTransformation)` | |
| Abstract/concrete | `style_analysis_abstract_concreteness_analysis_util.main(window, inputFilename, inputDir, outputDir, config_filename, False, chartPackage, dataTransformation, processType='')` | |
| Noun/verb WordNet classes | parse `['POS']` via `Stanford_CoreNLP_util.CoreNLP_annotate(...)` → `semantic_aggregation_WordNet_util.aggregate_GoingUP(WordNetDir='', <verbs_or_nouns_file>, outputDir, config_filename, 'VERB'\|'NOUN', False, chartPackage, dataTransformation, language)` | English + WordNet only |
| Entities (people/org, gender, dates, locations) | `Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir, False, chartPackage, dataTransformation, ['NER','gender','quote','normalized-date'], False, language, export_json_var, memory_var, document_length_var, limit_sentence_length_var, NERs=['PERSON','ORGANIZATION','CITY','STATE_OR_PROVINCE','COUNTRY','LOCATION'])` | one CoreNLP pass yields several |
| People & orgs (any package) | `_annotate_NER_by_package(package, config_filename, inputFilename, inputDir, outputDir, False, chartPackage, dataTransformation, …)` | honors configured package |

**Open-GUI (v1: surface as links, migrate later):** topic modeling (`topic_modeling_main.py`), word embeddings (`word2vec_main.py`), sentiment (`sentiment_analysis_main.py`), coreference (`coreference_main.py`), data visualization (`data_visualization_main.py`). **To wire as batch next:** SVO (`SVO_util.lemmatize_filter_svo` + parse), SRL (isolated py3.8 worker), syntactic hub (parse → CoNLL analyzers), semantic hub.

---

## 5. Report layout — `NLP_corpus_profile.html`

Self-contained (inline CSS/JS), theme-aware, link targets open on click (relative paths from the report at the output root, or `file://`). Structure:

1. **Header / corpus at a glance** — corpus name, # documents, # words, # sentences, language(s), (if dates found) date span, avg sentence length. *(These come cheaply from the statistics + NER-date outputs.)*
2. **Sticky category nav** (jump links).
3. **One collapsible `<details>` per category** — for each, in order run:
   - a **headline number or two** (e.g., "12 340 words · 641 sentences"; "Top date type: PRESENT"),
   - an optional **thumbnail** of the key chart (embedded `<img>` — Phase 3),
   - a **table of links** to every output file that analysis produced (csv / xlsx / png / Sankey-sunburst-GIS html / kml), labelled.
4. **"Open the full tool"** buttons for the open-GUI analyses in that category.
5. **Footer** — run config (package, language, date), total files produced, note that per-file detail lives in the subfolders.

The report **is** the fix for the "too many files to open" problem we hit all week (SRL/SVO/GIS >10-file logic): auto-open the report only.

---

## 6. Output organization

```
<outputDir>/corpus_profile_<corpus>/
    NLP_corpus_profile.html          ← the only auto-opened file
    counts/            …csv/xlsx/png from category 1
    style/             …
    syntax/            …
    semantics/         …
    entities/          …
    narrative/         …
    sentiment/         …
```
Each batch analysis already writes into a labelled subdir; the profiler passes the category subdir as its `outputDir` so the tree stays tidy and the report links resolve.

---

## 7. Build phases

- **Phase 0 — skeleton:** `corpus_profiler_main.py` GUI (categories 1, 2, 6 only) + `corpus_profiler_util.run_profile` that runs those **batch** analyses, collects files, and emits a **bare linked** `NLP_corpus_profile.html` (header stats + per-category link tables, no thumbnails). Prove end-to-end on `newspaperArticles`.
- **Phase 1 — breadth:** add categories 3 (syntax) and the batch parts of 4/7; wire the open-GUI ones as link buttons.
- **Phase 2 — enrich:** headline numbers per section, then chart thumbnails.
- **Phase 3 — migrate:** convert high-value open-GUI analyses (SVO, SRL, sentiment) to batch entry points so `*` truly profiles them.
- **Phase 4 — flip:** repoint the menu from `whats_in_your_corpus` to `corpus_profiler`; retire the old file (its broken `clear()` becomes moot).

---

## 8. Open decisions for you (red-pen here)

1. **Taxonomy tweaks** — **text readability**: Syntax (current) or Semantics ("understanding the text")? · **coreference**: own "Discourse" or under Narrative? · **nature**: Entities or Semantics? · **language detection**: Counts (current) or its own tiny thing?
2. **Open-GUI in `*`** — when `*` includes a category whose tools are open-GUI only, do we (a) skip them silently, (b) list them as "open manually" in the report, or (c) actually pop their GUIs? I lean (b).
3. **Headline stats depth** — Phase 2 pulls a couple of numbers per section from the csv outputs. Which numbers matter most to you per category? (You know the tools; I'll wire what you name.)
4. **Report styling** — plain-and-fast, or should it match a house style? (Fine to start plain.)
5. **Single file vs directory input** — profiler is corpus-first (a directory). OK to require a directory (not a single file) for the `*` run?
