# Sentiment Analysis — Implementation Review & Performance Audit

**Date:** 2026-06-09
**Author:** Claude (code review), Roberto Franzosi (project lead)

## Overview

The NLP Suite offers 8 sentiment analysis algorithms across three categories:
LLM (BERT), neural network (Stanford CoreNLP, Stanza), and dictionary-based
(ANEW, hedonometer, SentiWordNet, VADER, spaCy/TextBlob).

This memo documents the quality and accuracy of the three neural-network-style
implementations (CoreNLP, Stanza, spaCy) and records changes made.

---

## Algorithm Comparison

### Stanford CoreNLP — Gold Standard

- **Model:** Recursive Neural Tensor Network (Socher et al. 2013)
- **Scale:** 0–4 integer + text labels (very negative / negative / neutral / positive / very positive)
- **Granularity:** 5-class — the finest among the three
- **Quality:** Best-in-class for sentence-level sentiment; trained on Stanford Sentiment Treebank
- **Limitation:** Requires Java, English only in the NLP Suite

### Stanza

- **Model:** CNN-based classifier
- **Scale:** 0 (negative), 1 (neutral), 2 (positive)
- **Granularity:** 3-class — very coarse
- **Quality:** Adequate for rough positive/negative classification but lacks nuance. No fine-grained sentiment (no "very positive" or "very negative"). Suitable for large-scale corpus-level trends but not for close reading of individual sentences.
- **Languages:** English + several others (see `available_sentiment` in Stanza_util.py)

### spaCy (TextBlob) — Reclassified as Dictionary-Based

- **Model:** TextBlob pattern-based lookup (NOT neural network)
- **Scale:** -1.0 to +1.0 continuous float
- **Granularity:** 3-class after thresholding (negative < 0, neutral = 0, positive > 0)
- **Quality:** TextBlob uses a simple dictionary of word polarities inherited from the Pattern library. It does NOT use any neural network or deep learning. On most benchmarks it performs comparably to or worse than VADER.
- **Previous problem:** Was listed under "Neural network approaches" in the GUI dropdown, which was misleading. Has been moved to "Dictionary approaches" and renamed "spaCy (TextBlob)" to clarify the underlying method.

---

## Scale Summary

| Algorithm        | Type       | Scale       | Classes | Language     |
|------------------|------------|-------------|---------|--------------|
| Stanford CoreNLP | Neural net | 0–4 integer | 5       | English only |
| Stanza           | Neural net | 0–2 integer | 3       | Multilingual |
| BERT (English)   | LLM        | varies      | 3       | English      |
| BERT (Multilingual)| LLM     | varies      | 3       | Multilingual |
| spaCy (TextBlob) | Dictionary | -1.0 to 1.0| 3       | Multilingual |
| VADER            | Dictionary | -1.0 to 1.0| 3       | English      |
| SentiWordNet     | Dictionary | varies      | 3       | English      |
| ANEW             | Dictionary | 1–9         | 5       | English      |
| hedonometer      | Dictionary | 0–10        | 3       | English      |

---

## Code Changes (2026-06-09)

### 1. spaCy_util.py — Major Performance Fixes

**Problem:** Students reported spaCy running extremely slowly.

**Root causes and fixes:**

| Issue | Impact | Fix |
|-------|--------|-----|
| `subprocess spacy download` ran on every call | 5–15s wasted per run | Try `spacy.load()` first; download only on `OSError` |
| `get_mwe()` called inside sentence loop | O(n^2) on full DataFrame per sentence | Single call after all sentences collected |
| Cell-by-cell `df.at[]` in token loops | Extreme Python overhead | List-of-dicts + single `pd.DataFrame(rows)` |
| `out_df['Document ID'] = docID` inside token loop | Full-column assignment per token | Set once per row in the dict |
| `pd.concat` inside document loop | O(n^2) for total rows | Collect in list, one `pd.concat` at end |
| SVO CSV rewritten after every document | Repeated full I/O | Single write after all docs processed |
| Two `iterrows()` passes in SVO for NaN/semicolons | Slow Python loops | Vectorized pandas ops + correct defaults |
| Duplicate filenames in `filesToOpen` | Redundant visualization passes | Deduplicated before visualization |

### 2. Stanza_util.py — Sentiment Performance Fix

**Problem:** Sentiment output built with cell-by-cell `df.at[]` in a loop.

**Fix:** Replaced with list-of-dicts + single `pd.DataFrame()` constructor (same pattern as spaCy fix).

### 3. sentiment_analysis_main.py — GUI Reclassification

**Problem:** spaCy sentiment was listed under "Neural network approaches" despite using TextBlob (a dictionary-based method).

**Fix:**
- Moved "spaCy" from "Neural network approaches" to "Dictionary approaches"
- Renamed to "spaCy (TextBlob)" to clarify the underlying algorithm
- Added an informational popup when user selects spaCy explaining that it is dictionary-based and suggesting CoreNLP/Stanza for neural-network accuracy or VADER for a better dictionary approach
- Updated Shape-of-Stories activation logic to match the renamed option

---

## Recommendations

1. **For accuracy:** Use Stanford CoreNLP (5-class, English) or BERT for best results.
2. **For speed + multilingual:** Use Stanza (3-class, fast, pure Python, no Java).
3. **For quick dictionary baseline:** Use VADER over spaCy/TextBlob — VADER is purpose-built for sentiment and generally outperforms TextBlob.
4. **Future:** Consider adding a Stanza sentiment normalization option to map its 0/1/2 scale to a 0–4 or -1 to +1 range for easier comparison with other algorithms.
