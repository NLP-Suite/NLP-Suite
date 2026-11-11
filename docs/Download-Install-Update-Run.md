### NLP Suite  ![GitHub release (latest by date)](https://img.shields.io/github/v/release/NLP-Suite/NLP-Suite?color=Green&label=Latest%20Version)  

# Download, Install, Update, Run the NLP Suite

> **This page is for the standalone (PyInstaller) build.** If you want to run from source code, see the [Developer Setup](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite#developer-setup-run-from-source) section on the Install page.

## Download

1. Go to [Releases](https://github.com/NLP-Suite/NLP-Suite/releases)
2. Download the latest zip for your platform:
   - `NLP-Suite-windows-x64` (Windows 10/11)
   - `NLP-Suite-mac-arm64` (macOS Apple Silicon)

No GitHub account needed.

## Install

There is no installer — just extract the zip:

- **Windows:** Right-click → **Extract All** → choose a location you can write to (e.g., Desktop or `C:\NLP_Suite`; not Program Files and not inside OneDrive, or the NLP Suite cannot update itself)
- **macOS:** Double-click the zip in Finder

That's it. The extracted folder contains everything the NLP Suite needs.

## Run

### Windows

Double-click **NLP_Suite.exe**. If Windows shows "Windows protected your PC," click **More info** → **Run anyway** (first time only).

### macOS

1. Open the extracted folder and double-click **Launch NLP Suite (Mac).command**. It clears the macOS download quarantine and starts the NLP Suite.
2. The first time, macOS may block the launcher ("cannot be opened because it is from an unidentified developer"). Right-click (or Control-click) **Launch NLP Suite (Mac).command** → **Open** → **Open**. After that, a normal double-click works.

Do **not** double-click the `NLP_Suite` file itself: without the launcher it fails with a "code signature not valid" error.

See [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting) if you run into issues.

### First run

On the very first launch, the NLP Suite automatically creates default configuration files:

- **Input folder:** `lib/sampleData/newspaperArticles` (bundled sample texts)
- **Output folder:** `~/Documents/NLP_output`
- **NLP package:** Stanza
- **Language:** English

You can change these at any time in the I/O Configuration area at the top of the main window.

## Update

When you close the NLP Suite it checks for a new release. If there is one, it asks whether to download and install it (about 1.5 GB; a progress window shows the download and you can cancel). Your settings (`config` folder) and any files of your own inside the NLP Suite folder are kept. The previous version stays next to the new one as `NLP_Suite_previous` until the new one starts, and is then deleted.

The NLP Suite can only update a folder it can write to: not Program Files, and preferably not inside OneDrive.

**Release 1.6.40 or older:** these cannot update themselves. Go to [Releases](https://github.com/NLP-Suite/NLP-Suite/releases), download the latest zip, unzip it in place of your current folder and copy your `config` folder across. You only need to do this once.

## What's Bundled

The standalone build includes everything you need to run the NLP Suite:

**Runtime and packages:**
- Python runtime and all NLP packages (Stanza, spaCy, NLTK, BERT, Plotly, matplotlib, pandas, numpy, etc.)

**Linguistic databases and libraries:**
- WordNet lexical database (via NLTK) — word aggregation and semantic categories
- NRC Emotion Lexicon — 8-emotion analysis
- Concreteness ratings database (Brysbaert et al.) — concreteness analysis
- Iconicity ratings database — iconic language analysis
- Gender/name association database (namesGender) — gender annotation
- Sentiment analysis lexicons (sentimentLib) — dictionary-based sentiment scoring
- Word lists for various NLP tasks

**Sample data and documentation:**
- Sample texts: 5 literary stories (Bunin, Faulkner, Murphy, etc.) for testing
- Sample newspaper articles: 5 book reviews from major publications for corpus analysis
- TIPS documentation (150+ files explaining algorithms and features)
- Sample visualizations (charts, heatmaps) showing output formats

**Enhancement files:**
- CoreNLP enhanced dependencies — parsing enhancement files for SVO extraction and linguistic analysis

## The Config Folder

The `config/` folder (created on first run) stores your analysis settings and preferences.

**Auto-created defaults for new users:**
On your very first launch, the NLP Suite automatically creates two default config files:
- `NLP_default_IO_config.csv` — sets your input folder to `lib/sampleData/newspaperArticles` and output folder to `~/Documents/NLP_output` (you can change these anytime via I/O Configuration)
- `NLP_default_package_language_config.csv` — sets your NLP package to Stanza and language to English (you can change these via Setup)

These defaults let you start testing right away without configuration.

**Additional configs created as you work:**
- Each time you run an analysis, the NLP Suite saves a config file for that specific analysis (e.g., `newspaperArticles.csv`, `Harry P corpus.csv`), allowing you to quickly re-run the same analysis with identical settings without reconfiguring

**API keys:**
- `Google-geocode-API_config.csv` — Google Geocoding API key (if you use the GIS tools)
- `Google-Maps-API_config.csv` — Google Maps API key (if you use Google Maps visualization)

**External software:**
- `NLP_setup_external_software_config.csv` — paths to optional external tools (Stanford CoreNLP, MALLET, etc.)

The config folder is your personal settings hub — it persists across updates, so your preferences are preserved.

No separate installation of Python, Anaconda, Java, or WordNet is required (a Java runtime is bundled; WordNet data downloads automatically on first use).

See the [Install page](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite#whats-included) for details on what is and is not included.
