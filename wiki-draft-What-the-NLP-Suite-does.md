# What the NLP Suite Does

The NLP Suite provides an **easy-to-use one-stop shop for many Natural Language Processing (NLP) tasks**. The NLP Suite relies on three different freeware cutting-edge parsers and annotators — [spaCy](https://spacy.io/), [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/), [Stanza](https://stanfordnlp.github.io/stanza/) — to carry out many of these tasks, in particular:

* sentence splitting
* tokenizing
* lemmatizing
* Part-of-Speech (POS) tagging
* DepRel (Dependency Relations)
* NER (Named Entity Recognition)
* parser (via several different types of parsing algorithms: spaCy, Stanford CoreNLP, Stanza)
* specialized annotators (e.g., gender, dialogue, normalized time references, coreference resolution, sentiment analysis)

> **Note:** Stanza (pure Python) is the recommended NLP package. It covers all the same tasks as Stanford CoreNLP without requiring Java. The NLP Suite standalone build bundles Stanza — no installation needed.

## Sentiment & Emotion Analysis

The NLP Suite offers a comprehensive range of sentiment and emotion analysis tools:

* **Neural network approaches:** BERT (English and Multilingual models), Stanford CoreNLP, Stanza, spaCy (TextBlob)
* **Dictionary-based approaches:** VADER, SentiWordNet, ANEW (sentiment/arousal/dominance), hedonometer, NRC Emotion Wheel (8-emotion analysis with Plutchik wheel visualization)
* **Shape of stories** — compute and visualize how sentiments fluctuate across documents using hierarchical clustering, SVD, and NMF; also track sentiment fluctuations across actors (people, organizations) and/or locations in your corpus

## Knowledge Bases & Word Aggregation

* **WordNet** — aggregate nouns and verbs into higher-level semantic categories (e.g., walk/run/flee → motion) using NLTK WordNet (no Java or external download required); disaggregate categories into specific terms
* **DBpedia** and **YAGO** knowledge-base annotators
* **Word Sense Induction** via BERT word embeddings and K-means clustering

## Information Extraction

* **Subject-Verb-Object (SVO) extractor** (via Stanford CoreNLP, spaCy, Stanza)
* **Coreference resolution** (via Stanford CoreNLP, Stanza)
* **Topic modeling** (via MALLET and Gensim LDA)
* **Word embeddings** (via BERT and Gensim Word2Vec with similarity measures)

## GIS & Mapping

* **Geocoding and mapping** — automatically going from texts to maps via NER extraction (Stanza, spaCy, or BERT), geocoding (Nominatim or Google), and visualization:
  * Google Earth Pro (KML maps)
  * Google Maps (interactive web maps)
  * **Folium** (interactive HTML pin maps and heatmaps — no Google account required)
  * Proportional circle maps

## Data Visualization

The NLP Suite provides a unified visualization GUI with seven tabs that reflect the data type to be visualized:

* **Categorical:** colormaps/heatmaps, comparative bar charts, grouped bar charts, stacked bar charts, sunburst charts, treemaps, waffle charts
* **Geographic:** interactive maps (Folium pin maps, heatmaps, KML maps via Google Earth)
* **Hierarchical tree:** tree diagrams and dendrograms for hierarchical data
* **Numeric:** boxplots, bubble charts, correlation heatmaps, Excel/Plotly charts, histograms, violin plots
* **Relational:** network graphs (Gephi, vis.js), Sankey diagrams
* **Temporal:** interactive timelines (TimeMapper), timeline plots, calendar heatmaps
* **Wordclouds:** word frequency visualizations

Plus: all standard chart types via Excel and Plotly.

## Corpus & Text Analysis

* N-grams and co-occurrences with related viewer
* **Collocation statistics** — PMI, log-likelihood, chi-squared, t-score, Dice coefficient for statistically significant word pairs
* **TF-IDF ranking** — most distinctive words per document with cosine similarity matrix
* **Lexical diversity** — TTR, Root TTR, Log TTR, MTLD, vocd-D per document
* **Readability and sentence complexity** — Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, Coleman-Liau, Automated Readability Index, plus Yngve and Frazier sentence complexity measures
* **Word frequency distribution** — rank-frequency tables with Zipf's Law visualization and cumulative coverage curves
* Nominalization analysis
* Style analysis (concreteness, iconicity)
* Document similarities

## Character & Entity Analysis

* **Character Emotion Arcs** — track per-character emotions across a narrative using NER (Stanza) + NRC emotion scoring, with Plutchik emotion comparison plots
* **NER Entity Timeline** — visualize when and where people, places, and organizations appear across a narrative with frequency charts, scatter timelines, and entity presence heatmaps

## Pre-Processing Tools

* File type converters (PDF/DOCX/RTF to TXT)
* File mergers and splitters
* File checkers and cleaners (UTF-8 compliance, spelling)
* Data handling scripts, including database and SQL queries
* PC-ACE relational database analysis tools

The tools in the NLP Suite operate at the **corpus** level, i.e., on a large set of documents, at the **individual document** level, and at the **sentence level**.
