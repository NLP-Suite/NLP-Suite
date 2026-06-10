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
9. [GIS Multi-Package NER](#9-gis-multi-package-ner-2026-06-09)
10. [NLP Package Performance Comparison](#10-nlp-package-performance-comparison-2026-06-09)
11. [CoNLL Table Multi-Package Support](#11-conll-table-multi-package-support-2026-06-09)

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

### CoreNLP-Only Annotators Not Available in Stanza (verified 2026-06-10)

As of Stanza v1.11, the following CoreNLP annotators have **no native Stanza equivalent**:

| Annotator | CoreNLP | Stanza native | Stanza via CoreNLPClient |
|---|---|---|---|
| **Quote attribution** | Yes (quote annotator) | No | Yes (requires Java + CoreNLP server) |
| **Gender** | Yes (gender annotator) | No | Yes (requires Java + CoreNLP server) |
| **NER normalized date (SUTime)** | Yes (via ner annotator) | No | Yes (requires Java + CoreNLP server) |

Stanza's native processors (v1.11): tokenize, MWT, POS, lemma, depparse, NER, sentiment, constituency, coref.

These three annotators can only be accessed through Stanza's `CoreNLPClient` wrapper, which still requires Java and the CoreNLP server running — not a true migration away from CoreNLP. Until Stanza adds native support, any NLP Suite features using quote attribution, gender, or normalized dates must continue to call CoreNLP.

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

## 11. CoNLL Table Multi-Package Support (2026-06-09)

### Problem

The CoNLL Table Analyzer GUI (`CoNLL_table_analyzer_main.py`) was locked to Stanford
CoreNLP CoNLL tables only. The GUI explicitly blocked Stanza and spaCy tables, and
`check_CoNLL()` enforced exactly 13-14 columns. This was unnecessary because:

1. All analysis scripts (noun, verb, adjective, adverb, function words, k-sentences,
   ratio) use only the **common** columns: Form, Lemma, POS, NER, Head, DepRel,
   Sentence ID, Document ID, Document — all present in every package's output.
2. No analysis script uses `Clause Tag` or `Deps` (CoreNLP-specific columns).
3. Clause analysis is the **only** script that requires CoreNLP (needs Clause Tag).

### Column Layout Differences

| Position | CoreNLP (13 cols) | Stanza (13 cols) | spaCy (12 cols) |
|----------|-------------------|-------------------|-----------------|
| 0-4 | ID, Form, Lemma, POS, NER | ID, Form, Lemma, POS, NER | ID, Form, Lemma, POS, NER |
| 5 | Head | feats | Multi-Word Expression |
| 6 | DepRel | Multi-Word Expression | Head |
| 7 | Deps | Head | DepRel |
| 8 | Clause Tag | DepRel | Sentence ID |
| 9 | Record ID | Record ID | Sentence |
| 10 | Sentence ID | Sentence ID | Document ID |
| 11 | Document ID | Document ID | Document |
| 12 | Document | Document | — |

### Solution: Column Normalization

Added `normalize_to_canonical(headers, data)` in `CoNLL_util.py`. This function:

1. Detects which package generated the table (via `detect_CoNLL_package()`)
2. Reorders all columns to the **canonical (CoreNLP) layout** at read time
3. Fills missing columns (Deps, Clause Tag) with empty strings
4. Auto-generates Record ID when absent (e.g., spaCy tables)

After normalization, all existing positional code works unchanged — `row[3]` is
always POS, `row[6]` is always DepRel, `row[10]` is always Sentence ID, etc.

### Files Modified

- **`CoNLL_util.py`**: Added `CANONICAL_COLUMNS`, `REQUIRED_COLUMNS`,
  `detect_CoNLL_package()`, `normalize_to_canonical()`. Updated `check_CoNLL()`
  to validate required columns (not column count). Updated `compute_sentence()`
  and `compute_sentence_table()` to use column names instead of positions.
- **`CoNLL_table_analyzer_main.py`**: Calls `normalize_to_canonical()` after
  reading data. Clause analysis auto-skipped for non-CoreNLP tables. GUI
  restriction removed — accepts CoreNLP, Stanza, spaCy tables.
- **`CoNLL_adjective_analysis_util.py`**, **`CoNLL_adverb_analysis_util.py`**,
  **`CoNLL_noun_analysis_util.py`**, **`CoNLL_ratio_analysis_util.py`**: Updated
  DataFrame column names to reference `CoNLL_util.CANONICAL_COLUMNS`.

### Remaining Limitation

- **Clause analysis** remains CoreNLP-only (requires Clause Tag column from PCFG parser).
  Auto-skipped with an informative message when a non-CoreNLP table is used.
