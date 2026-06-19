# Install the NLP Suite

## Quick Install (recommended)

The NLP Suite is distributed as a standalone application — no Python, Anaconda, or Java installation required.

### 1. Download

Go to the [latest workflow run](https://github.com/NLP-Suite/NLP-Suite/actions/workflows/build-installers.yml) and download the artifact for your platform:

| Platform | Artifact |
|----------|----------|
| Windows 10/11 (64-bit) | `NLP-Suite-windows-x64` |
| macOS (Apple Silicon — M1/M2/M3/M4) | `NLP-Suite-mac-arm64` |

> **Note:** You need a GitHub account to download workflow artifacts. If a tagged release is available, you can also find the zip files on the [Releases](https://github.com/NLP-Suite/NLP-Suite/releases) page (no login required).

### System Requirements

| Resource | Minimum |
|----------|---------|
| Free disk space | **5 GB minimum** without BERT features; **8 GB** with all BERT features (see breakdown below) |
| Internet | Required for first run (model downloads) and for optional features (geocoding, web scraping) |
| RAM | 4 GB (8 GB recommended for large corpora) |

#### Disk space breakdown

| Component | Size | When downloaded |
|-----------|------|-----------------|
| Installer zip | ~1.5–2 GB | Initial download |
| Extracted application | ~3.5 GB | On extraction |
| Stanza English model | ~525 MB | First time you run a Stanza analysis |
| spaCy English model | ~50 MB | First time you run a spaCy analysis |
| NLTK data (wordnet, punkt, etc.) | Bundled | Already included in the installer |
| BERT models (NER, similarity, topic modeling, WSI) | Up to ~3 GB | Only if you use BERT features, downloaded on first use of each |
| MALLET (topic modeling) | ~50 MB | Only if you use MALLET; external download (see below) |

### 2. Extract

- **Windows:** Right-click the downloaded zip → **Extract All**
- **macOS:** Double-click the zip in Finder

### 3. Run

#### Windows

Double-click **NLP_Suite.exe** in the extracted folder.

If Windows shows **"Windows protected your PC"**:
1. Click **More info**
2. Click **Run anyway**

This only happens the first time.

#### macOS

The download includes **NLP Suite Mac Setup.app** — use it to launch the NLP Suite for the first time:

1. Double-click **NLP Suite Mac Setup**
2. Click **Select NLP Suite Folder** and point it to the extracted `NLP_Suite` folder
3. Click **Remove Quarantine from Executable** — this clears the macOS Gatekeeper block
4. Click **Remove Quarantine from Folder** — allows all bundled files to run
5. Click **Open NLP Suite**

After the first launch, you can also run **NLP_Suite** directly by double-clicking it.

> **Why is this needed?** macOS blocks unsigned applications downloaded from the internet (Gatekeeper). The Setup app removes this quarantine flag so the NLP Suite can run. This is a one-time step.

### 4. First Run

On the very first launch, the NLP Suite automatically creates two default configuration files so you can start testing right away:

| Setting | Default value |
|---------|--------------|
| Input folder | `lib/sampleData/newspaperArticles` (bundled sample texts) |
| Output folder | `~/Documents/NLP_output` (your Documents folder) |
| NLP package | Stanza |
| Language | English |

You can change these at any time via the **I/O Configuration** options at the top of the main window.

---

## What's Included

The standalone distribution bundles everything the NLP Suite needs:

- **Python runtime** and all Python packages (Stanza, spaCy, NLTK, BERT, Plotly, matplotlib, etc.)
- **WordNet** lexical database (via NLTK — no separate download needed)
- **NRC Emotion Lexicon** for emotion analysis
- **Sample data** for testing (`lib/sampleData/`)
- **TIPS** documentation and reminders

### What is NOT included

| Tool | When needed | What to do |
|------|------------|------------|
| Stanford CoreNLP | Only if you select CoreNLP as your NLP package | [Download from Stanford](https://stanfordnlp.github.io/CoreNLP/) — but **Stanza** (included) does the same things without Java |
| Java | Only if you use Stanford CoreNLP | [Download JDK](https://www.oracle.com/java/technologies/downloads/) |
| Google Earth Pro | Only for KML/Google Earth map visualizations | [Download](https://www.google.com/earth/about/versions/#earth-pro) — or use **Folium** (included) as an alternative |
| Google Maps API key | Only for Google Maps visualizations | [Get an API key](https://developers.google.com/maps/documentation/javascript/get-api-key) — or use **Folium** (included) |
| Gephi | Only for network graph visualization | [Download](https://gephi.org/users/download/) |

> **Tip:** For most users, the bundled tools (Stanza, Folium, vis.js) cover all functionality without any additional downloads.

---

## Developer Setup (run from source)

If you want to modify the NLP Suite source code or contribute to development:

### Prerequisites

- [Anaconda](https://www.anaconda.com/download) (Python 3.10+)
- [Git](https://git-scm.com/downloads)

### Steps

```bash
# Clone the repository
git clone https://github.com/NLP-Suite/NLP-Suite.git
cd NLP-Suite

# Create a conda environment
conda create -n NLP python=3.10 -y
conda activate NLP

# Install dependencies
pip install pandas numpy scipy scikit-learn openpyxl xlrd
pip install stanza spacy nltk gensim textblob textstat nrclex
pip install langdetect langid autocorrect pyspellchecker fuzzywuzzy
pip install transformers sentence-transformers
pip install matplotlib plotly seaborn wordcloud mpld3 kaleido
pip install folium geopy simplekml shapely geopandas
pip install requests beautifulsoup4 lxml chardet tqdm psutil
pip install pdfminer.six python-docx striprtf
pip install Pillow SPARQLWrapper

# Run the NLP Suite
python NLP_Suite_main.py
```

### Branch structure

| Branch | Purpose |
|--------|---------|
| `roberto` | Active development — latest features |
| `current-stable` | Stable release — mirrors `roberto` after testing |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Windows: "Windows protected your PC" | Click **More info** → **Run anyway** |
| macOS: "cannot be opened because it is from an unidentified developer" | Use the **NLP Suite Mac Setup** app to remove quarantine, then click **Open NLP Suite** |
| macOS: "NLP_Suite is damaged and can't be opened" | Use the Mac Setup app to remove quarantine. If that doesn't work, open Terminal and run: `xattr -cr /path/to/NLP_Suite` |
| First run: no config files found | Normal — the app creates them automatically. If it doesn't, check that your Documents folder is writable |
| Stanza model download fails | Check your internet connection. Stanza downloads language models on first use (~525 MB for English) |

---

## Need Help?

- Click the **?** buttons next to each option in any GUI for explanations
- Use the **TIPS** and **README** buttons at the bottom of each GUI
- Visit the [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting) wiki page
- [Report an issue](https://github.com/NLP-Suite/NLP-Suite/issues)

---

Visit the [**NLP Suite Architecture**](https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Architecture) page for information on the NLP Suite design.
