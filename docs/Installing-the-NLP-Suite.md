### NLP Suite  ![GitHub release (latest by date)](https://img.shields.io/github/v/release/NLP-Suite/NLP-Suite?color=Green&label=Latest%20Version)  

# Install the NLP Suite

## Quick Install (recommended)

The NLP Suite is distributed as a standalone application — no Python, Anaconda, or Java installation required.

### 1. Download

1. Go to [Releases](https://github.com/NLP-Suite/NLP-Suite/releases)
2. Download the latest zip for your platform:
   - `NLP-Suite-windows-x64` (Windows 10/11)
   - `NLP-Suite-mac-arm64` (macOS Apple Silicon — M1/M2/M3/M4/M5)

No GitHub account needed.

### System Requirements

| Resource | Minimum |
|----------|---------|
| Free disk space | **5 GB minimum**; **8 GB** with BERT features; **~10 GB** with all optional software (see breakdown below) |
| Internet | Required for first run (model downloads) and for optional features (geocoding, web scraping) |
| RAM | 4 GB (8 GB recommended for large corpora) |

#### Disk space breakdown

| Component | Size | When downloaded |
|-----------|------|-----------------|
| Installer zip | ~1.5–2 GB | Initial download |
| Extracted application | ~3.5 GB | On extraction |
| Stanza English model | ~525 MB | First time you run a Stanza analysis |
| spaCy English model | ~50 MB | First time you run a spaCy analysis |
| NLTK data (wordnet, punkt, etc.) | A few MB | Downloaded automatically the first time a tool needs it |
| BERT models (NER, similarity, topic modeling, WSI) | Up to ~3 GB | Only if you use BERT features, downloaded on first use of each |
| MALLET (topic modeling) | ~50 MB | Only if you use MALLET; external download (see below) |
| Stanford CoreNLP | ~550 MB | Only if you use CoreNLP instead of Stanza; the Java runtime it needs is included |
| Google Earth Pro | ~50 MB | Only if you use KML/Google Earth visualizations; Folium (included) is an alternative |

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

1. Open the extracted folder and double-click **Launch NLP Suite (Mac).command**. It clears the macOS download quarantine and starts the NLP Suite.
2. The first time, macOS may block the launcher ("cannot be opened because it is from an unidentified developer"). Right-click (or Control-click) **Launch NLP Suite (Mac).command** → **Open** → **Open**. After that, a normal double-click works.

Do **not** double-click the `NLP_Suite` file itself: without the launcher it fails with a "code signature not valid" error.

> **Why is this needed?** macOS blocks unsigned applications downloaded from the internet (Gatekeeper). The launcher removes this quarantine flag so the NLP Suite can run.

### 4. First Run

On the very first launch, the NLP Suite automatically creates two default configuration files so you can start testing right away:

| Setting | Default value |
|---------|--------------|
| Input folder | `lib/sampleData/newspaperArticles` (bundled sample texts) |
| Output folder | `~/Documents/NLP_output` (your Documents folder) |
| NLP package | Stanza |
| Language | English |

You can change these at any time via the **I/O Configuration** options at the top of the main window.

### 5. Updates

From release 1.6.41, closing the NLP Suite offers to download and install a new release when one is out (about 1.5 GB, with a progress window). Your settings and your own files are kept; the previous version stays next to the new one as `NLP_Suite_previous` until the new one starts.

For this to work, extract the NLP Suite to a folder you can write to (Desktop or `C:\NLP_Suite`, not Program Files) and not inside OneDrive. Releases 1.6.40 and older cannot update themselves: download the new zip, unzip it in place of your current folder and copy your `config` folder across.

---

## What's Included

The standalone distribution bundles everything the NLP Suite needs:

- **Python runtime** and all Python packages (Stanza, spaCy, NLTK, BERT, Plotly, matplotlib, etc.)
- **A Java runtime** (for the optional Stanford CoreNLP tools)
- **WordNet** lexical database (via NLTK; its data downloads automatically on first use)
- **NRC Emotion Lexicon** for emotion analysis
- **Sample data** for testing (`lib/sampleData/`)
- **TIPS** documentation and reminders

### What is NOT included

| Tool | When needed | What to do |
|------|------------|------------|
| Stanford CoreNLP | Only if you select CoreNLP as your NLP package, or use a CoreNLP-only annotator (gender, quote, normalized dates, OpenIE) | [Download from Stanford](https://stanfordnlp.github.io/CoreNLP/). Java is already included. **Stanza** (included) covers parsing, NER and sentiment without it |
| MALLET | Only for MALLET topic modeling | Download from the Setup external software window — or use **Gensim** (included) |
| Google Earth Pro | Only for KML/Google Earth map visualizations | [Download](https://www.google.com/earth/about/versions/#earth-pro) — or use **Folium** (included) as an alternative |
| Google Maps API key | Only for Google Maps visualizations | [Get an API key](https://developers.google.com/maps/documentation/javascript/get-api-key) — or use **Folium** (included) |
| Gephi | Only for network graph visualization | [Download](https://gephi.org/users/download/) |

> **Tip:** For most users, the bundled tools (Stanza, Folium, vis.js) cover all functionality without any additional downloads.

---

## Developer Setup (run from source)

If you want to modify the NLP Suite source code or contribute to development:

### Prerequisites

- [Anaconda](https://www.anaconda.com/download) (the NLP Suite is built and tested on Python 3.10)
- [Git](https://git-scm.com/downloads)

### Steps

```bash
# Clone the repository
git clone https://github.com/NLP-Suite/NLP-Suite.git
cd NLP-Suite

# Create a conda environment
conda create -n NLP python=3.10 -y
conda activate NLP

# Install dependencies (the file pins the versions the NLP Suite needs)
pip install -r requirements.txt
pip install -r requirements-windows.txt   # on a Mac: requirements-mac.txt
python -m spacy download en_core_web_sm

# Run the NLP Suite
python src/NLP_menu_main.py
```

### Branch structure

| Branch | Purpose |
|--------|---------|
| `roberto` | Integration branch — all pull requests target it |
| `current-stable` | What users get. A source checkout on this branch updates itself with Git when you close the NLP Suite |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Windows: "Windows protected your PC" (SmartScreen) | Click **More info** → **Run anyway**. Or right-click **NLP_Suite.exe** → **Properties** → tick **Unblock** (bottom right) → **OK** |
| macOS: "cannot be opened because it is from an unidentified developer" | Right-click **Launch NLP Suite (Mac).command** → **Open** → **Open** (first time only) |
| macOS: "NLP_Suite is damaged and can't be opened" or "code signature not valid" | Start the NLP Suite with **Launch NLP Suite (Mac).command**, not the `NLP_Suite` file. If that doesn't work, open Terminal and run: `xattr -cr /path/to/NLP_Suite` (the extracted folder) |
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
