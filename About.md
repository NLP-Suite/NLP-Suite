# About

## Mission Statement & Target Audience

In an age of BIG DATA, the purpose of the NLP Suite is rather to provide humanists and social scientists a wide range of **computational tools for the analysis and visualization of smaller datasets,** the more typical datasets humanists and social scientists use (e.g., the works of one Nobel Prize winner, a handful of in-depth interviews, a few thousand newspaper articles).

Furthermore, the NLP Suite is designed for non-specialists, for scholars with **no knowledge or little knowledge of Natural Language Processing.**

The NLP Suite was developed by **Roberto Franzosi** at **Emory University** with the help of many current and past **Emory undergraduate students**. Visit [**The NLP Suite Team**](https://github.com/NLP-Suite/NLP-Suite/wiki/The-NLP-Suite-Team) page for more information In the Summer of 2026, Claude Code improved many of the scripts, extended the functionality of the NLP Suite, and finally solved the problem of the NLP Suite installation via PyInstaller.

---

## What the NLP Suite does

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

### Sentiment & Emotion Analysis

The NLP Suite offers a comprehensive range of sentiment and emotion analysis tools:

* **Neural network approaches:** BERT (English and Multilingual models), Stanford CoreNLP, Stanza, spaCy (TextBlob)
* **Dictionary-based approaches:** VADER, SentiWordNet, ANEW (sentiment/arousal/dominance), hedonometer, NRC Emotion Wheel (8-emotion analysis with Plutchik wheel visualization)
* **Shape of stories** — compute and visualize how sentiments fluctuate across documents using hierarchical clustering, SVD, and NMF; also track sentiment fluctuations across actors (people, organizations) and/or locations in your corpus

### Knowledge Bases & Word Aggregation

* **WordNet** — aggregate nouns and verbs into higher-level semantic categories (e.g., walk/run/flee → motion) using NLTK WordNet (no Java or external download required); disaggregate categories into specific terms
* **DBpedia** and **YAGO** knowledge-base annotators
* **Word Sense Induction** via BERT word embeddings and K-means clustering

### Information Extraction

* **Subject-Verb-Object (SVO) extractor** (via Stanford CoreNLP, spaCy, Stanza)
* **Coreference resolution** (via Stanford CoreNLP, Stanza)
* **Topic modeling** (via MALLET and Gensim LDA)
* **Word embeddings** (via BERT and Gensim Word2Vec with similarity measures)

### GIS & Mapping

* **Geocoding and mapping** — automatically going from texts to maps via NER extraction (Stanza, spaCy, or BERT), geocoding (Nominatim or Google), and visualization:
  * Google Earth Pro (KML maps)
  * Google Maps (interactive web maps)
  * **Folium** (interactive HTML pin maps and heatmaps — no Google account required)
  * Proportional circle maps

### Data Visualization

The NLP Suite provides a unified visualization GUI with seven tabs that reflect the data type to be visualized:

* **Categorical:** colormaps/heatmaps, comparative bar charts, grouped bar charts, stacked bar charts, sunburst charts, treemaps, waffle charts
* **Geographic:** interactive maps (Folium pin maps, heatmaps, KML maps via Google Earth)
* **Hierarchical tree:** tree diagrams and dendrograms for hierarchical data
* **Numeric:** boxplots, bubble charts, correlation heatmaps, Excel/Plotly charts, histograms, violin plots
* **Relational:** network graphs (Gephi, vis.js), Sankey diagrams
* **Temporal:** interactive timelines (TimeMapper), timeline plots, calendar heatmaps
* **Wordclouds:** word frequency visualizations

Plus: all standard chart types via Excel and Plotly.

### Corpus & Text Analysis

* N-grams and co-occurrences with related viewer
* **Collocation statistics** — PMI, log-likelihood, chi-squared, t-score, Dice coefficient for statistically significant word pairs
* **TF-IDF ranking** — most distinctive words per document with cosine similarity matrix
* **Lexical diversity** — TTR, Root TTR, Log TTR, MTLD, vocd-D per document
* **Readability and sentence complexity** — Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, Coleman-Liau, Automated Readability Index, plus Yngve and Frazier sentence complexity measures
* **Word frequency distribution** — rank-frequency tables with Zipf's Law visualization and cumulative coverage curves
* Nominalization analysis
* Style analysis (concreteness, iconicity)
* Document similarities

### Character & Entity Analysis

* **Character Emotion Arcs** — track per-character emotions across a narrative using NER (Stanza) + NRC emotion scoring, with Plutchik emotion comparison plots
* **NER Entity Timeline** — visualize when and where people, places, and organizations appear across a narrative with frequency charts, scatter timelines, and entity presence heatmaps

### Pre-Processing Tools

* File type converters (PDF/DOCX/RTF to TXT)
* File mergers and splitters
* File checkers and cleaners (UTF-8 compliance, spelling)
* Data handling scripts, including database and SQL queries
* PC-ACE relational database analysis tools

The tools in the NLP Suite operate at the **corpus** level, i.e., on a large set of documents, at the **individual document** level, and at the **sentence level**.

### All Native Python — No Java, No External Dependencies

A major architectural goal of the NLP Suite is to run **entirely in Python** with no external runtime dependencies:

* **Stanza** replaces Stanford CoreNLP for parsing, NER, sentiment analysis, and coreference resolution — same quality, pure Python, no Java installation required
* **NLTK WordNet** replaces the Java-based MIT JWI library — noun/verb aggregation and disaggregation now run natively with no WordNet download or Java needed
* **SQLite + Pandas** provide relational database querying — no external database server required
* **Folium** provides interactive HTML maps — no Google Earth Pro or Google Maps API key needed
* **Gensim** provides topic modeling and word embeddings — no MALLET or external tools needed

The result: **download, extract, double-click.** Everything works out of the box.

### Unique Selling Proposition (USP)

The **Unique Selling Proposition (USP)** of the NLP Suite is its **easiness of use**. The NLP Suite interacts with the user with a set of user-friendly GUIs (**Graphical User Interface**) (over 50 GUIs at present), each GUI with `? HELP buttons` on most widgets, `hover-over help`, `ReadMe buttons`, `reminder messages` that the user can turn On and Off, `videos`, and `TIPS files` for extensive explanations of the algorithms behind the GUIs (over 150 TIPS files for all GUIs at present).

The NLP Suite is distributed as a **standalone application** for Windows and macOS — no Python, Anaconda, or Java installation required. Download, extract, and double-click.

Click [**here**](https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Architecture) for more information on the NLP Suite architecture.

---

## License

The NLP Suite is licensed under a [GNU License Agreement](https://www.gnu.org/licenses/gpl-3.0.en.html) Version 1.0, January 2020.

---

## How to Cite the NLP Suite

Franzosi, Roberto. 2020. NLP Suite: A collection of natural language processing and visualization tools GitHub: [https://github.com/NLP-Suite/NLP-Suite/wiki](https://github.com/NLP-Suite/NLP-Suite/wiki).

The following papers are based on the NLP Suite tools.

**Published papers**:

* Franzosi, Roberto. 2020. "What's in a Text? Bridging the Gap Between Quality and Quantity in the Digital Era." Quality & Quantity. DOI: [https://doi.org/10.1007/s11135-020-01067-6](https://doi.org/10.1007/s11135-020-01067-6)
* Franzosi, Roberto, Wenqin Dong, Yilin Dong. 2021. "Qualitative and Quantitative Research in the Humanities and Social Sciences: How Natural Language Processing (NLP) Can Help." Quality & Quantity. DOI: [https://doi.org/10.1007/s11135-021-01235-2](https://doi.org/10.1007/s11135-021-01235-2)
* Franzosi, Roberto. 2021. "Of Narrative Time and Space: Geography Meets History in the Digital Era via Linguistics." Digital Scholarship in the Humanities. DOI: [https://doi.org/10.1093/llc/fqab090](https://doi.org/10.1093/llc/fqab090)
* Franzosi, Roberto and Shuyang Bian. 2026. "Decoding China's government work report (CGWR): A natural language processing (NLP) approach." Quality & Quantity. DOI: [https://doi.org/10.1007/s11135-026-02604-5](https://doi.org/10.1007/s11135-020-01067-6)

**Unpublished papers**:

* Franzosi, Roberto, Wenqin Dong, Ziyang Hu, Wei Dai, Rafael Piloto, Gabriel Wang. 2020. "Automatic Information Extraction and Visualization of the Narrative Elements Who, What, When, and Where." Unpublished manuscript.
* Franzosi, Roberto, Wenqin Dong, Alberto Purpura. 2020. "The Shape of Stories." Unpublished manuscript.

![](https://github.com/NLP-Suite/NLP-Suite/raw/current-stable/lib/images/logo-small.png?raw=true)

### A freeware, open-source package for Natural Language Processing and visualization
