### NLP Suite  ![GitHub release (latest by date)](https://img.shields.io/github/v/release/NLP-Suite/NLP-Suite?color=Green&label=Latest%20Version)  

## Quick Install (recommended)

The NLP Suite is distributed as a standalone application: no Python, Anaconda, or Java installation required.

### 1. Download

1. Go to [Releases](https://github.com/NLP-Suite/NLP-Suite/releases)
2. Download the latest zip for your platform:
   - `NLP-Suite-windows-x64` (Windows 10/11)
   - `NLP-Suite-mac-arm64` (macOS on Apple Silicon: M1/M2/M3/M4/M5)

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
| Release zip | About 750 MB (Mac) to 800 MB (Windows) | Initial download |
| Extracted application | A few GB | On extraction |
| Stanza English model | About 1 GB | First time you run a Stanza analysis |
| spaCy English model | ~50 MB | First time you run a spaCy analysis |
| NLTK data (wordnet, punkt, etc.) | A few MB | Downloaded automatically the first time a tool needs it |
| BERT models (NER, similarity, topic modeling, WSI) | Up to ~3 GB | Only if you use BERT features, downloaded on first use of each |
| MALLET (topic modeling) | ~50 MB | Only if you use MALLET; external download (see below) |
| Stanford CoreNLP | ~550 MB | Only if you use CoreNLP instead of Stanza; the Java runtime it needs is included |
| Google Earth Pro | ~50 MB | Only if you use KML/Google Earth visualizations; Folium (included) is an alternative |

### 2. Extract

There is no installer: just extract the zip.

- **Windows:** Right-click the downloaded zip → **Extract All** → choose a folder you can write to (Desktop or `C:\NLP_Suite`; not Program Files and not inside OneDrive, or the NLP Suite cannot update itself)
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

When you close the NLP Suite it checks for a new release. If there is one, it asks whether to download and install it (a progress window shows the download and you can cancel). Your settings (the `config` folder) and any files of your own inside the NLP Suite folder are kept. If you edited a file that came with the NLP Suite, the previous version is kept next to the new one as `NLP_Suite_previous`; otherwise it is deleted when the new version starts.

The NLP Suite can only update a folder it can write to: not Program Files, and preferably not inside OneDrive.

**Release 1.6.40 or older:** these cannot update themselves. Download the latest zip from [Releases](https://github.com/NLP-Suite/NLP-Suite/releases), unzip it in place of your current folder and copy your `config` folder across. You only need to do this once.

---

## What's Included

The standalone distribution bundles everything the NLP Suite needs:

- **Python runtime** and all Python packages (Stanza, spaCy, NLTK, the BERT libraries, Plotly, matplotlib, etc.). The BERT and Stanza language models themselves download on first use
- **A Java runtime** (for the optional Stanford CoreNLP tools)
- **WordNet** lexical database (via NLTK; its data downloads automatically on first use)
- **Word lists and lexicons:** NRC Emotion Lexicon, concreteness and iconicity ratings, the names/gender database, sentiment lexicons
- **Sample data** for testing (`lib/sampleData/`)
- **TIPS** documentation (150+ files) and reminders

### What is NOT included

| Tool | When needed | What to do |
|------|------------|------------|
| Stanford CoreNLP | Only if you select CoreNLP as your NLP package, or use a CoreNLP-only annotator (gender, quote, normalized dates, OpenIE) | [Download from Stanford](https://stanfordnlp.github.io/CoreNLP/). Java is already included. **Stanza** (included) covers parsing, NER and sentiment without it |
| MALLET | Only for MALLET topic modeling | Download from the Setup external software window, or use **Gensim** (included) |
| Google Earth Pro | Only for KML/Google Earth map visualizations | [Download](https://www.google.com/earth/about/versions/#earth-pro), or use **Folium** (included) as an alternative |
| Google Maps API key | Only for Google Maps visualizations | [Get an API key](https://developers.google.com/maps/documentation/javascript/get-api-key), or use **Folium** (included) |
| Gephi | Only for network graph visualization | [Download](https://gephi.org/users/download/) |

> **Tip:** For most users, the bundled tools (Stanza, Folium, vis.js) cover all functionality without any additional downloads. See [Install External Software](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-External-Software).

---

## The Config Folder

The `config` folder, created on first run, stores your settings. Updates keep it.

- `NLP_default_IO_config.csv`: your input and output folders (change them in I/O Configuration)
- `NLP_default_package_language_config.csv`: your NLP package and language (change them in Setup)
- One file per analysis you run (named after its input, e.g. `newspaperArticles.csv`), so you can re-run it with the same settings
- `Google-geocode-API_config.csv`, `Google-Maps-API_config.csv`: your Google API keys, if you use the GIS tools or Google Maps
- `NLP_setup_external_software_config.csv`: where the optional external tools (Stanford CoreNLP, MALLET, etc.) are installed

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
| `roberto` | Integration branch: all pull requests target it |
| `current-stable` | What users get. A source checkout on this branch updates itself with Git when you close the NLP Suite |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Windows: "Windows protected your PC" (SmartScreen) | Click **More info** → **Run anyway**. Or right-click **NLP_Suite.exe** → **Properties** → tick **Unblock** (bottom right) → **OK** |
| macOS: "cannot be opened because it is from an unidentified developer" | Right-click **Launch NLP Suite (Mac).command** → **Open** → **Open** (first time only) |
| macOS: "NLP_Suite is damaged and can't be opened" or "code signature not valid" | Start the NLP Suite with **Launch NLP Suite (Mac).command**, not the `NLP_Suite` file. If that doesn't work, open Terminal and run: `xattr -cr /path/to/NLP_Suite` (the extracted folder) |
| First run: no config files found | Normal: the app creates them automatically. If it doesn't, check that your Documents folder is writable |
| Stanza model download fails | Check your internet connection. Stanza downloads language models on first use (about 1 GB for English) |

More in [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting).

---

## Need Help?

- Click the **?** buttons next to each option in any GUI for explanations
- Use the **TIPS** and **README** buttons at the bottom of each GUI
- Visit the [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting) wiki page
- [Report an issue](https://github.com/NLP-Suite/NLP-Suite/issues)

---

Visit the [**NLP Suite Architecture**](https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Architecture) page for information on the NLP Suite design.
