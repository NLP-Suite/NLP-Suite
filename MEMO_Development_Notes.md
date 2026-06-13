# NLP Suite — Development Notes

Cumulative technical notes across development sessions. This file is committed
to the repo so it is never lost.

---

## Table of Contents

1. [PyInstaller Packaging](#1-pyinstaller-packaging-2026-06-04)
2. [Column Name Standardization](#2-column-name-standardization-2026-06-05)
3. [Cross-Complex Query](#3-cross-complex-query-2026-06-05)
4. [Grammar Rename/Remove/Merge](#4-grammar-renameremovemerge)
5. [Data Validation GUI](#5-data-validation-gui)
6. [CoreNLP to Stanza Migration](#6-corenlp-to-stanza-migration-2026-06-09)
7. [spaCy Performance Fixes](#7-spacy-performance-fixes-2026-06-09)
8. [Sentiment Analysis Review](#8-sentiment-analysis-review-2026-06-09)
9. [GIS Pipeline — Multi-Package NER Extraction](#9-gis-pipeline--multi-package-ner-extraction-2026-06-09)
10. [NLP Package Performance Comparison](#10-nlp-package-performance-comparison-2026-06-09)
11. [Code Quality Review](#11-code-quality-review-2026-06-10)
12. [Strategic Direction — Traditional NLP vs LLMs](#12-strategic-direction--traditional-nlp-vs-llms-2026-06-10)
13. [WordNet Java→NLTK Migration](#13-wordnet-javanltk-migration-2026-06-12)
14. [NRC Emotion Wheel Integration](#14-nrc-emotion-wheel-integration-2026-06-12)
15. [Character Emotion Arcs](#15-character-emotion-arcs-2026-06-13)
16. [TF-IDF, Lexical Diversity, Collocation Statistics](#16-tf-idf-lexical-diversity-collocation-statistics-2026-06-13)
17. [NER Entity Timeline](#17-ner-entity-timeline-2026-06-13)
18. [Readability Scores](#18-readability-scores-2026-06-13)

---

## 1. PyInstaller Packaging (2026-06-04)

### Build Command

Always clear caches first:
```
Remove-Item -Recurse -Force build, src\__pycache__ -Confirm:$false
C:\Users\rfranzo\AppData\Local\anaconda3\envs\NLP\python.exe -m PyInstaller NLP_Suite.spec --noconfirm --clean
C:\Users\rfranzo\AppData\Local\anaconda3\envs\NLP\python.exe post_build_fixup.py
```

### Status

**Windows build SUCCEEDED** — `dist/NLP_Suite/NLP_Suite.exe` (1.2 GB total).
- Python 3.8.13 (NLP conda env)
- Excluded: tensorflow, torch, bertopic, nltk (hook incompatible), pyLDAvis, gmaps
- Data dirs (lib, config, TIPS, reminders, src/*.py) go at exe root, NOT `_internal/`
- DLL copies: tk86t.dll, tcl86t.dll, sqlite3.dll, liblzma.dll + tcl/tk library dirs

### Fixes Applied (12 items)

1. `pygit2` import made optional (warning dialog)
2. All `call("python X.py")` replaced with `run_script_util.run_script()` across 32 files
3. Anaconda Python discovery for subprocess calls
4. WindowsApps alias filtered out
5. `config_input_output_alphabetic_options` NameError fixed (module-level init + global)
6. `local_release_version` UnboundLocalError (default '0.0.0')
7. Config option quote stripping fixed
8. `GUI_IO_util.py` frozen mode detection for `NLPPath`/`scriptPath`
9. `IO_setup_brief_display_area` stored as module-level global
10. Parsers checkbox re-checks config after setup GUI closes
11. External software checkbox unticks when config missing
12. Spec file: `pygit2` excluded, `run_script_util` in hidden imports

### Known Limitation

Sub-GUIs launch via subprocess. Target machine needs Python (system or Anaconda).

### Key Files

- `NLP_Suite.spec` — entry point: src/NLP_menu_main.py
- `src/run_script_util.py` — Python finder + script launcher
- `post_build_fixup.py` — copies data dirs, DLLs, .py files to dist
- `.github/workflows/build-installers.yml` — CI for Win + Mac Intel + Mac ARM

---

## 2. Column Name Standardization (2026-06-05)

### Convention

All internal column IDs: `ID_{setup|data}_[xref_]{table_table}` — **all lowercase, underscores only**.

Examples: `ID_setup_xref_complex_complex` (was `ID_setup_xref_complex-complex`),
`ID_data_complex_higher` (was `ID_data_complex_HIGHER`),
`ID_data_simplex` (was `ID_datat_simplex` — typo fix).

### How It Works

1. **xlsx files keep original ACCESS names** (never modified)
2. **`reading_list`** in `DB_PCACE_data_analysis_util.py` renames at load time (single source of truth)
3. **`_save_setup_table()`** reverses renames before writing xlsx
4. **`_PKL_VERSION`** (currently 5) forces pkl regeneration when mappings change

### Safety Net

`_save_setup_table()` calls `_reverse_column_renames()` before writing xlsx. All direct `.to_excel()` calls migrated to use it. Prevents the corruption that had affected 22 xlsx files across 5 databases.

### If Column Renames Change

1. Bump `_PKL_VERSION`
2. Delete `_pkl_version.txt` and all `*.pkl` in each database directory
3. Close all NLP Suite GUIs before reopening

---

## 3. Cross-Complex Query (2026-06-05)

Lives on `roberto` branch. 4 unlabeled comboboxes: Source Complex, Source Simplex, Target Complex, Target Simplex. Plus checkboxes, + button for extra pairs, "Generate SQL query" button.

### Drill-Down Mechanism

- `> ChildName` prefix in simplex dropdown = drill into
- `<< Parent` = go back up
- `checkmark ChildName` = multi-selected children
- Enter to toggle, click to drill

### Key Functions

`_populate_simplex_menu`, `_drill_into_child`, `_go_back_to_children`,
`_handle_simplex_drill`, `_handle_simplex_enter`, `_generate_cross_complex_query`

Related util: `DB_PCACE_data_analysis_util.generate_cross_complex_query`

---

## 4. Grammar Rename/Remove/Merge

The data_analysis GUI supports renaming, removing empty, and merging duplicate grammar objects. See `DB_PCACE_data_analysis_util.py`.

---

## 5. Data Validation GUI

New GUI for lemmatizing simplex values, validating aggregate codes, side-by-side comparison. Uses Stanza lemmatizer (not CoreNLP).

---

## 6. CoreNLP to Stanza Migration (2026-06-09)

### Motivation

- CoreNLP: Java dependency, complex subprocess management, not updated since ~2021
- Stanza: Pure Python, same Stanford NLP group, pip installable, simpler PyInstaller distribution
- Stanza coref is better than CoreNLP coref

### What Was Done

**Coreference resolution** (`Stanza_coref()` in `Stanza_util.py`, ~150 lines):
- Requires Stanza >= 1.7.0, uses XLM-RoBERTa with LoRA (peft library)
- Pipeline: `tokenize,mwt,pos,lemma,depparse,coref`
- Iterates coref chains, finds canonical (non-pronoun) mention, replaces pronouns
- Produces `coref_table_Stanza.csv`
- Reuses CoreNLP's `manualCoref()` split-screen editor
- Key API detail: `CorefMention` has `start_word`, `end_word`, `sentence` (no `.text` attribute);
  extract text via `' '.join(w.text for w in doc.sentences[m.sentence].words[m.start_word:m.end_word])`

**Enhanced SVO extraction** (replaced minimal `extractSVO()`, ~450 lines):
- `_build_govern_dict(sentence)` — UD dep tree to CoreNLP-style govern_dict
- `_negation_detect()` — recursive negation through govern_dict children
- `_conj_string()`, `_s_o_formation()` — conjunction handling ("A, B, and C")
- `_verb_root_svo_building()` — single-verb S/V/O with phrasal verbs, LVC, oblique objects
- `_verb_obj_obl()` — LVC detection; searches BOTH verb's AND object noun's govern_dict
  (Stanza puts `nmod:of` on the object noun, not the verb — key difference from CoreNLP)
- `_linking_verb_LVC_extraction()` — "be responsible for" patterns (ADJ, not VERB in Stanza)
- `_pred_root()` — copular/predicative nominative
- `_advcl_extraction()` — recursive adverbial/clausal modifier extraction
- `_verb_root()` — conjunct verb processing with shared-argument inheritance
- `_replace_words_with_full_names()` — MWE entity name replacement
- `_extract_ner_entities()` — uses Stanza's entity API
- `extractSVO()` — main function, now outputs Negation column

**GUI updates** (`coreference_main.py`):
- Dropdown: added Stanza option alongside CoreNLP
- `run()`: branches on `'Stanza' in Coref` vs CoreNLP path
- TIPS and hover-over text updated

### Environment (Python 3.8)

Working package combination: PyTorch 2.4.1, Stanza 1.10.1, spaCy 3.4.4, pydantic 1.9.2, typing_extensions 4.5.0

### Test Results

All 8 SVO test cases pass: basic S/V/O, negation, conjunction, passive voice, linking verb LVC, relative clauses, verb+obj+obl LVC, copular. Coref: 4 chains correctly identified.

### Still Needed

- Python 3.8 -> 3.10+ upgrade (deferred; would resolve all version pinning)
- Remove CoreNLP subprocess calls once Stanza fully validated in production

---

## 7. spaCy Performance Fixes (2026-06-09)

### Problem

Students reported spaCy running extremely slowly despite spaCy being the fastest NLP library.

### Root Causes & Fixes (spaCy_util.py)

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | `subprocess spacy download` on every call | 5-15s wasted per run | Try `spacy.load()` first; download only on `OSError` |
| 2 | `get_mwe()` called inside sentence loop | O(n^2) — full DataFrame scanned per sentence | Single call after all sentences |
| 3 | Cell-by-cell `df.at[]` in token loops | Extreme Python overhead per token | List-of-dicts + single `pd.DataFrame(rows)` |
| 4 | `out_df['Document ID'] = docID` inside token loop | Full-column assignment per token | Set once per row in dict |
| 5 | `pd.concat` inside document loop | O(n^2) for total rows across docs | Collect in list, one `pd.concat` at end |
| 6 | SVO CSV rewritten after every document | Repeated full I/O | Single write after all docs |
| 7 | Two `iterrows()` passes for NaN/semicolons | Slow Python loops | Vectorized pandas ops + correct defaults |
| 8 | Duplicate filenames in `filesToOpen` | Redundant visualization | Deduplicated before visualization |

---

## 8. Sentiment Analysis Review (2026-06-09)

### Algorithm Comparison

| Algorithm | Type | Scale | Classes | Language |
|-----------|------|-------|---------|----------|
| Stanford CoreNLP | Neural (RNTN) | 0-4 integer | 5 | English only |
| Stanza | Neural (CNN) | 0-2 integer | 3 | Multilingual |
| BERT (English) | LLM | varies | 3 | English |
| BERT (Multilingual) | LLM | varies | 3 | Multilingual |
| spaCy (TextBlob) | Dictionary | -1.0 to 1.0 | 3 | Multilingual |
| VADER | Dictionary | -1.0 to 1.0 | 3 | English |
| SentiWordNet | Dictionary | varies | 3 | English |
| ANEW | Dictionary | 1-9 | 5 | English |
| hedonometer | Dictionary | 0-10 | 3 | English |

### Key Finding: spaCy Misclassified

spaCy sentiment uses TextBlob (pattern-based dictionary), NOT a neural network.
Was listed under "Neural network approaches" — moved to "Dictionary approaches"
and renamed "spaCy (TextBlob)". Added informational popup.

### Recommendations

1. **Best accuracy:** Stanford CoreNLP (5-class RNTN) or BERT
2. **Fast + multilingual neural:** Stanza (3-class, pure Python)
3. **Dictionary baseline:** VADER > TextBlob on most benchmarks
4. **Future:** Consider Stanza sentiment normalization (0/1/2 -> 0-4 or -1 to +1)

### Stanza Sentiment Fix

Replaced cell-by-cell `.at[]` loop with list-of-dicts pattern (same optimization as spaCy).

---

## 9. GIS Pipeline — Multi-Package NER Extraction (2026-06-09)

### Problem

The GIS pipeline (text → NER → geocode → map) was hardcoded to Stanford CoreNLP for
NER location extraction. CoreNLP requires Java, supports limited languages, and uses
an older CRF architecture.

### NER Quality Comparison for Location Tagging

| | CoreNLP NER | Stanza NER | spaCy NER |
|--|-------------|------------|-----------|
| Architecture | CRF (2014) | BiLSTM-CRF + char embeddings (2020) | Transformer/CNN |
| English F1 (OntoNotes) | ~86% | ~89% | ~86% |
| Location tag granularity | CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION (4 classes) | GPE, LOC (2 classes) | GPE, LOC (2 classes) |
| Languages with NER | ~7 | 30+ | 20+ |
| Multi-word entities | Requires 70+ lines of custom joining logic in Suite | Pre-joined by model (single entity span) | Pre-joined via IOB tags |
| Java required | Yes | No | No |

### Key Insight

The 4-class CoreNLP granularity (CITY vs COUNTRY vs STATE_OR_PROVINCE) is **not used
downstream** — the geocoder (Nominatim/Google) geocodes the location string regardless
of its sub-type. All location tags are treated identically in the GIS pipeline.

Stanza's biggest practical advantage: multi-word entities like "United States of America"
come pre-joined from the model. CoreNLP returns individual tokens that must be stitched
together with error-prone custom logic.

### Changes Made (GIS_main.py)

1. Added NER package dropdown: BERT, **Stanza** (default), spaCy, Stanford CoreNLP
2. All NER tags (GPE, LOC) are mapped to LOCATION for uniform downstream processing
3. Multi-Word Expression column from Stanza/spaCy is used when available (pre-joined entities)
4. BERT uses `aggregation_strategy="simple"` which also pre-joins entities
5. Help text updated with package comparison and accuracy/speed tradeoffs
6. Default set to Stanza (best accuracy/speed tradeoff + multilingual + no Java dependency)

### Column Normalization

| Source | Word column | NER tags | Entity joining |
|--------|-------------|----------|----------------|
| BERT | `Word` | LOC → mapped to LOCATION | Pre-joined by `aggregation_strategy="simple"` |
| CoreNLP | `Word` | CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION | Custom logic in `Stanford_CoreNLP_util.py` |
| Stanza | `Form` → renamed `Word` | GPE, LOC → mapped to LOCATION | `Multi-Word Expression` column |
| spaCy | `Form` → renamed `Word` | GPE, LOC → mapped to LOCATION | `Multi-Word Expression` column |

---

## 10. NLP Package Performance Comparison (2026-06-09)

### NER Accuracy (English, OntoNotes/CoNLL benchmarks)

| Package | Architecture | F1 Score | Speed (relative) | Languages | Java? |
|---------|-------------|----------|-------------------|-----------|-------|
| **BERT** (`xlm-roberta-large-finetuned-conll03-english`) | Transformer (XLM-RoBERTa) | ~92% | Slowest (5-10x Stanza) | Multilingual (102 langs) | No |
| **Stanza** | BiLSTM-CRF + char embeddings | ~89% | Fast | 30+ | No |
| **spaCy** (`_core_web_sm`) | CNN | ~86% | Fastest | 20+ | No |
| **spaCy** (`_core_web_trf`) | Transformer | ~90% | Slow | ~5 | No |
| **Stanford CoreNLP** | CRF | ~86% | Medium | ~7 | Yes |

### Sentiment Analysis Quality

| Package | Architecture | Scale | Quality | Speed |
|---------|-------------|-------|---------|-------|
| **BERT** (cardiffnlp models) | RoBERTa transformer | 3-class | Best on most benchmarks | Slow |
| **Stanford CoreNLP** | Recursive Neural Tensor Network | 5-class (finest granularity) | Very good | Medium (Java) |
| **Stanza** | CNN classifier | 3-class (0/1/2) | Good, but coarse | Fast |
| **spaCy (TextBlob)** | Dictionary (pattern-based) | -1.0 to +1.0 | Mediocre (not neural) | Fast |
| **VADER** | Dictionary (rule-based) | -1.0 to +1.0 | Good for social media | Fastest |

### Coreference Resolution

| Package | Architecture | Quality | Notes |
|---------|-------------|---------|-------|
| **Stanza** (v1.7+) | XLM-RoBERTa with LoRA | State of the art | Already transformer-based; adding BERT coref would be redundant |
| **Stanford CoreNLP** | Statistical model (2017) | Good but dated | Java required |

### Performance Bugs Fixed (2026-06-09)

**spaCy_util.py** — 8 fixes (see Section 7):
- `spacy download` subprocess on every run (5-15s waste)
- `get_mwe()` in sentence loop (O(n^2))
- Cell-by-cell `df.at[]` instead of list-of-dicts
- `pd.concat` in document loop (O(n^2))
- SVO CSV rewritten per document
- `iterrows()` instead of vectorized ops
- Full-column assignment per token
- Duplicate files in visualization list

**BERT_util.py** — 1 critical fix:
- `pipeline("ner", ...)` was called inside the **sentence loop**, recreating the
  entire NER pipeline per sentence. This is extremely expensive — each call
  reinitializes the model. Moved to a single call before the loop.

**Stanza_util.py** — 1 fix:
- Sentiment output built cell-by-cell with `df.at[]`; replaced with list-of-dicts.

### Recommendations by Use Case

| Task | Best Choice | Why |
|------|-------------|-----|
| **NER (small corpus, max accuracy)** | BERT | ~92% F1, pre-joined entities |
| **NER (large corpus, multilingual)** | Stanza | ~89% F1, fast, 30+ languages, no Java |
| **NER (speed priority)** | spaCy (`_core_web_sm`) | Fastest, ~86% F1 |
| **Sentiment (accuracy)** | BERT | Best on benchmarks |
| **Sentiment (granularity)** | CoreNLP | 5-class scale (only option with "very positive/negative") |
| **Sentiment (speed + multilingual)** | Stanza | Fast, 3-class, many languages |
| **Coreference** | Stanza | Already uses transformer (XLM-RoBERTa); no need for separate BERT coref |
| **SVO extraction** | Stanza (enhanced) | Full port of CoreNLP logic; no Java needed |
| **GIS pipeline** | Stanza (default) or BERT (precision) | Stanza for speed+multilingual; BERT for max accuracy |

---

## 11. Code Quality Review (2026-06-10)

Systematic review of ~30 scripts across the codebase. The same anti-patterns appeared
repeatedly — this section catalogs them so future development avoids reintroducing them.

### Common Anti-Patterns Found and Fixed

| # | Anti-Pattern | Why It's Bad | Correct Pattern |
|---|-------------|--------------|-----------------|
| 1 | `fin = open(path)` without `.close()` or `with` | File handle leak — exhausts OS file descriptors on large corpora | `with open(path) as f:` |
| 2 | `open('../lib/wordLists/stopwords.txt')` (relative path) | Breaks when working directory differs from script location | `os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', ...)` |
| 3 | `sum = 0` / `dict = {}` / `str = ...` | Shadows Python builtins — hides bugs, confuses tools | Use `total`, `data_dict`, `text`, etc. |
| 4 | `pd.concat([df, new_row])` inside a loop | O(n²) — copies the entire DataFrame every iteration | Collect rows as list-of-dicts, single `pd.DataFrame(rows)` at end |
| 5 | `df.append(row)` | Deprecated since pandas 1.4, removed in 2.0 | Same as #4: list-of-dicts + single construction |
| 6 | `df.at[i, col] = value` cell-by-cell in a loop | Extreme Python overhead per cell | Build row as dict, append to list, single DataFrame at end |
| 7 | `iterrows()` for mutation or aggregation | Slow Python loop, returns copies not views | Vectorized pandas ops (`.apply()`, boolean indexing) |
| 8 | `applymap()` | Deprecated since pandas 2.1 | `.apply(pd.to_numeric, errors='coerce')` or `.map()` |
| 9 | `nltk.download('resource')` at module level | Runs on every import (5-10s), blocks startup | Use `import_nltk_resource()` which checks before downloading |
| 10 | `file.close()` after `with open(...) as file:` | Redundant — `with` already closes on exit | Remove the extra `.close()` |
| 11 | CSV write inside document loop | Rewrites ALL accumulated rows every iteration | Move write after the loop |
| 12 | Debug `print()` left in production code | Clutters output, confuses users | Remove |
| 13 | `pd.read_csv(path, names=[...])` on files WITH headers | Overrides existing headers, turns the real header into a data row | Use default `header=0`, then rename columns |

### Files Fixed — Batch 1 (commit 961fb5d)

| File | Fixes |
|------|-------|
| `word2vec_util.py` | File handle leaks (×3), `pd.concat` in loop, `df.append` |
| `html_annotator_dictionary_util.py` | File handle leak |
| `html_annotator_main.py` | File handle leak |
| `html_annotator_util.py` | File handle leaks (×2), `pd.concat` in loop |
| `html_annotator_gender_guesser_util.py` | File handle leak |
| `html_annotator_BERT_util.py` | File handle leak |
| `NGrams_util.py` | `pd.concat` in loop, `df.append` |
| `NGrams_CoOccurrences_util.py` | `df.at[]` cell-by-cell in loop |
| `knowledge_graphs_WordNet_util.py` | File handle leak |
| `knowledge_graphs_OpenIE_util.py` | File handle leak |
| `knowledge_graphs_DBpedia_util.py` | File handle leak |

### Files Fixed — Batch 2 (commit abe46fd)

| File | Fixes |
|------|-------|
| `charts_matplotlib_seaborn_util.py` | `pd.read_csv(names=)` overriding headers (#13), `applymap` (#8), `iterrows` hack, missing `plt.close()` |
| `topic_modeling_gensim_util.py` | `df.append` (#5), `pd.concat` in loop (#4), redundant `file.close()` (#10), bug: `optimal_coherence` never updated |
| `sentence_analysis_util.py` | File handle leaks (×2, `open().read()` without close) |
| `nominalization_util.py` | Module-level `nltk.download` (×2, #9), file handle leak (#1), CSV write inside loop (#11), debug `print('wrong')` (#12) |

### Files Fixed — Batch 3 (commit e91d53d)

| File | Fixes |
|------|-------|
| `style_analysis_abstract_concreteness_analysis_util.py` | File handle leak + relative path (#1, #2) for stopwords.txt |
| `style_analysis_iconicity_analysis_util.py` | File handle leak + relative path (#1, #2) for stopwords.txt |
| `shape_of_stories_clustering_util.py` | File handle leak (#1), `sum` shadows builtin (#3) |
| `shape_of_stories_vectorizer_util.py` | `sum` shadows builtin (#3) |

### Files Reviewed — No Fixes Needed

GUI boilerplate (main.py files) and clean utility code:
`topic_modeling_mallet_util.py`, `topic_modeling_bert_util.py`, `topic_modeling_main.py`,
`sentence_analysis_main.py`, `sentence_complexity_node_util.py`, `nominalization_main.py`,
`style_analysis_main.py`, `shape_of_stories_main.py`, `shape_of_stories_visualization_util.py`,
all `knowledge_graphs_*_main.py`, `html_annotator_annotator_main.py`

### Checklist for Future Scripts

Before committing new code, verify:
- [ ] No `open()` without `with` (or explicit close in a `finally`)
- [ ] No relative paths like `../lib/` — use `os.path.dirname(os.path.abspath(__file__))`
- [ ] No variable names that shadow builtins (`sum`, `dict`, `list`, `str`, `type`, `id`, `input`, `map`, `filter`)
- [ ] No `pd.concat` or `df.append` inside loops — collect then build
- [ ] No `df.at[]` cell-by-cell — use list-of-dicts
- [ ] No module-level `nltk.download()` — use `import_nltk_resource()`
- [ ] No `applymap()` — use `.map()` or `.apply()`
- [ ] CSV/Excel writes happen AFTER the processing loop, not inside it

---

## 12. Strategic Direction — Traditional NLP vs LLMs (2026-06-10)

### Why the Suite Still Matters

1. **Reproducibility.** When a researcher publishes "we used Stanza NER (BiLSTM-CRF,
   F1 ~89%) with VADER sentiment," that is a citable, deterministic method another lab
   can replicate exactly. An LLM prompt gives different results across runs, model
   versions, and temperature settings. Peer-reviewed research requires method transparency.

2. **Structured, auditable output.** The Suite produces tabular CSV/Excel data that feeds
   directly into statistical analysis — every token tagged, every score traceable. LLMs
   produce prose; extracting structured data from prose adds a fragile extra step.

3. **Specific measurement scales.** ANEW (1–9), CoreNLP sentiment (5-class), Brysbaert
   concreteness (1–5), iconicity (1–7) — these are published psycholinguistic instruments
   with known properties. LLMs cannot produce scores on these scales without the underlying
   dictionaries and models the Suite already integrates.

4. **Cost and access.** The Suite runs offline on student laptops with no API fees. A class
   of 30 students processing 10,000 documents each would cost hundreds of dollars in API
   calls. Local models (Stanza, spaCy) cost nothing per token.

5. **Teaching value.** Students learn what NER, SVO, sentiment, and coreference actually
   are by seeing each step. An LLM that returns "positive sentiment" teaches nothing about
   how sentiment is measured.

### Where LLMs Are Genuinely Better

- **Judgment and context:** Sarcasm, irony, implicit meaning, pragmatic inference
- **Zero-shot classification:** Tasks you haven't built a pipeline for
- **Summarization and narrative analysis:** Thematic coding, discourse structure
- **Flexible multilingual:** One model handles any language without separate downloads
- **Ambiguity:** When the task doesn't fit neat categories or requires world knowledge

### Strategic Path Forward

The Suite's real value is not any single algorithm — it is the **framework**: file handling,
batch processing, CSV/Excel output, visualization, PC-ACE database integration, and the
GUI that makes NLP accessible to non-programmers. That infrastructure does not become
obsolete; it becomes the scaffolding that LLMs plug into.

**Concrete next step:** Add an LLM-based annotator option (local models like Llama/Mistral,
or API-based like GPT-4/Claude) as another choice in existing dropdowns — so a user can
run sentiment analysis with VADER, Stanza, *or* an LLM and compare the outputs in the
same CSV format. The Suite already does this with BERT vs Stanza vs spaCy vs CoreNLP;
an LLM option is a natural extension of the same multi-engine architecture.

### Decision Matrix

| Criterion | Traditional NLP (Stanza/spaCy/dictionaries) | LLMs |
|-----------|----------------------------------------------|------|
| Reproducibility | Deterministic, citable | Non-deterministic across runs |
| Cost per token | Zero (local) | $0.01–$0.06 per 1K tokens (API) |
| Offline use | Yes | Only with local models (hardware-intensive) |
| Structured output | Native (CSV rows per token) | Requires prompt engineering + parsing |
| Specific scales | Yes (ANEW, concreteness, iconicity, etc.) | No — cannot replicate validated instruments |
| Speed on large corpora | Fast (thousands of docs/minute) | Slow and expensive at scale |
| Contextual understanding | Limited (sentence-level) | Excellent (document-level) |
| Zero-shot flexibility | None — needs a pipeline | Excellent |
| Teaching transparency | High — each step visible | Black box |
| Multilingual | Per-model (Stanza 30+, spaCy 20+) | Universal |

### Conclusion

**Not Suite OR LLMs — Suite AND LLMs.** Keep the deterministic pipelines for reproducible
research. Add LLM options for exploratory analysis and tasks that need judgment. Let the
user compare both approaches on the same data, in the same output format. The Suite is the
chassis; algorithms (traditional and LLM) are interchangeable engines.

---

## 13. WordNet Java→NLTK Migration (2026-06-12)

### What Changed

Replaced two Java JAR files (`WordNet_Search_DOWN.jar`, `WordNet_Search_UP.jar`) with pure Python implementations using `nltk.corpus.wordnet`.

**Before:** Users needed Java JDK installed + standalone WordNet downloaded (Mac 3.0 or Windows 2.1) + JAR files in `src/`. Functions called Java via `subprocess.call()`.

**After:** NLTK bundles WordNet 3.0 as a corpus. First run calls `nltk.download('wordnet')` automatically (a few MB). No Java, no standalone WordNet installer, no platform-specific paths.

### Functions Rewritten

| Function | Old (Java) | New (NLTK) |
|----------|-----------|------------|
| `disaggregate_GoingDOWN()` | `subprocess.call(['java', '-jar', 'WordNet_Search_DOWN.jar', ...])` | Recursive `synset.hyponyms()` traversal |
| `aggregate_GoingUP()` | `subprocess.call(['java', '-jar', 'WordNet_Search_UP.jar', ...])` | `synset.hypernyms()` climbing via `lexname()` to 25 noun / 15 verb top-level synsets |

### CSV Output Format (unchanged)

- **DOWN simple:** Term, WordNet Category
- **DOWN verbose:** Term, WordNet Category, Definition, Frequency, Examples
- **UP synsets:** Word, WordNet Category, Intermediate synset 1, 2, ...
- **UP frequency:** WordNet Category, Frequency

### Files Modified

- `knowledge_graphs_WordNet_util.py` — core rewrite
- `knowledge_graphs_WordNet_main.py` — removed `external_software_install('WordNet')` gate

### Files Deleted

- `src/WordNet_Search_DOWN.jar` (170 KB)
- `src/WordNet_Search_UP.jar` (171 KB)

### Callers (no changes needed)

All pass `WordNetDir=''` (parameter kept for signature compatibility):
- `CoNLL_table_analyzer_main.py`
- `SVO_main.py`
- `whats_in_your_corpus_main.py`
- `knowledge_graphs_WordNet_main.py`

### TODO

- Update TIPS PDF for WordNet (remove Java/download instructions)
- Update ? HELP messages in `knowledge_graphs_WordNet_main.py` (remove references to Java, JAR files, WordNet install)

---

## 14. NRC Emotion Wheel Integration (2026-06-12)

### What Was Added

New dictionary-based sentiment analysis option: **NRC (emotion wheel)** using the `nrclex` Python package (bundles the NRC Emotion Lexicon).

Scores text for Plutchik's 8 basic emotions: anger, anticipation, disgust, fear, joy, sadness, surprise, trust.

### Output

1. **CSV** — per-sentence scores for all 8 emotions + dominant emotion label
2. **NRC radar chart** (PNG) — polar plot of average emotion proportions
3. **Plutchik wheel** (PNG) — 8-petal intensity wheel (mild/basic/intense) with scores overlaid

### Files

- `sentiment_analysis_NRC_util.py` — new util (scoring, radar chart, Plutchik wheel)
- `sentiment_analysis_main.py` — added `NRC (emotion wheel)` to dictionary approaches dropdown
- `.github/workflows/build-installers.yml` — added `nrclex` to pip installs

### Origin

Based on two student homework scripts (NRC emotion wheel + Plutchik wheel), refactored into a proper util following the VADER/ANEW/hedonometer pattern.

---

## 15. Character Emotion Arcs (2026-06-13)

### What Was Added

New tool that combines **NER (person extraction)** with **NRC emotion scoring** to track per-character emotion arcs across narratives.

### How It Works

1. **Stanza NER** (`tokenize,ner` pipeline) extracts PERSON entities from each sentence
2. **NRC emotion scoring** (via `nrclex`) scores each sentence for Plutchik's 8 basic emotions
3. Emotions are **attributed to the characters** mentioned in each sentence
4. Character names are **normalized** (e.g., "Mr. Smith" and "Smith" merge to same entity)
5. Sentences with no named character are attributed to `_NARRATOR/UNATTRIBUTED_`
6. Results are **smoothed** with a rolling window and plotted as arcs

### Output

1. **CSV** — per-sentence, per-character emotion scores (8 emotions)
2. **Character emotion arcs** (PNG) — per-character line plots of all 8 emotions across narrative position
3. **Dominant emotion timeline** (PNG) — horizontal bar showing which emotion dominates at each sentence
4. **Character comparison plots** (PNG) — overlay of multiple characters on the same emotion (joy, anger, fear, sadness)
5. **Character summary CSV** — average emotion scores and dominant emotion per character

### Files

- `character_emotion_arcs_util.py` — new util (NER extraction, NRC scoring, arc plotting, comparison charts)
- `sentiment_analysis_main.py` — added `Character Emotion Arcs (NER + NRC)` to dropdown under new "Character-level" category

### Limitations

- English only (NRC Emotion Lexicon is English; Stanza NER works best in English)
- No coreference resolution yet — pronoun-only sentences are attributed to NARRATOR. Adding Stanza coref would improve attribution but significantly increase processing time.
- Character name normalization is heuristic (substring matching), not ML-based

---

## 16. TF-IDF, Lexical Diversity, Collocation Statistics (2026-06-13)

Three new corpus analysis tools, all pure Python with no new dependencies.

### TF-IDF (Term Frequency–Inverse Document Frequency)

Identifies the **most distinctive words per document** — words that are frequent in a document but rare across the corpus. Uses scikit-learn's `TfidfVectorizer`.

**Output:**
- TF-IDF score matrix (documents × words) CSV
- Top 20 most distinctive words per document CSV
- Top 20 distinctive words bar chart (PNG)
- Document similarity matrix CSV + heatmap (PNG) — cosine similarity from TF-IDF vectors

**Location:** `statistics_corpus_tfidf_util.py`, wired into `statistics_txt_main.py` dropdown

### Lexical Diversity

Measures how varied the vocabulary is in each document. Implements five standard measures:

| Measure | Formula |
|---------|---------|
| **TTR** (Type-Token Ratio) | unique_types / total_tokens |
| **Root TTR** (Guiraud) | unique_types / √total_tokens |
| **Log TTR** (Herdan) | log(unique_types) / log(total_tokens) |
| **MTLD** | Measure of Textual Lexical Diversity — sequential TTR factoring |
| **vocd-D** | Curve-fitting approach to vocabulary diversity |

**Output:** CSV with all measures per document + comparison bar charts (PNG)

**Location:** `statistics_corpus_lexical_diversity_util.py`, wired into `statistics_txt_main.py` dropdown

### Collocation Statistics

Identifies **statistically significant word pairs** beyond raw co-occurrence counts. Computes five association measures:

| Measure | What it captures |
|---------|-----------------|
| **PMI** (Pointwise Mutual Information) | How much more often words co-occur than expected by chance |
| **Log-Likelihood** | Statistical significance of the association |
| **Chi-Squared** | Independence test between the two words |
| **T-Score** | Association strength adjusted for frequency |
| **Dice Coefficient** | Overlap coefficient |

**Output:** Full collocation table CSV + top-N CSV per measure + 4-panel bar chart (PNG)

**Location:** `NGrams_collocation_statistics_util.py`, wired into `NGrams_CoOccurrences_main.py` compute options dropdown

---

## 17. NER Entity Timeline (2026-06-13)

Tracks **when and where named entities appear** across a narrative or corpus. Uses Stanza NER to extract PERSON, GPE, LOC, ORG, DATE, EVENT, NORP, FAC entities with narrative position (0=beginning, 1=end).

**Outputs:**
- Entity timeline CSV (every mention with document, sentence, position)
- Frequency bar chart (top 20 entities across all types, color-coded)
- Per-type scatter timelines (PERSON, GPE, ORG, LOC — when each entity appears)
- Entity presence heatmap (top 15 entities binned across 10 narrative segments)
- Per-document entity counts (multi-document mode only)

**Location:** `NER_entity_timeline_util.py`, wired into `NER_main.py` via "NER Entity Timeline (Stanza)" dropdown option

---

## 18. Readability Scores (2026-06-13)

Computes five standard readability indices per document:

| Measure | What it captures |
|---------|-----------------|
| **Flesch Reading Ease** | 0–100 score (higher = easier); maps to grade level |
| **Flesch-Kincaid Grade** | US school grade level needed to understand the text |
| **Gunning Fog Index** | Years of education needed; penalizes polysyllabic words |
| **Coleman-Liau Index** | Grade level based on character counts (no syllable counting) |
| **Automated Readability Index** | Grade level based on characters-per-word and words-per-sentence |

Uses regex-based syllable counting (no external NLP dependencies).

**Output:** CSV with all five scores per document + interpretation + bar chart comparison (PNG)

**Location:** `statistics_corpus_readability_util.py`, wired into `statistics_txt_main.py` dropdown
