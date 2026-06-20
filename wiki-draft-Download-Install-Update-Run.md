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

- **Windows:** Right-click → **Extract All** → choose a location (e.g., Desktop or Program Files)
- **macOS:** Double-click the zip in Finder

That's it. The extracted folder contains everything the NLP Suite needs.

## Run

### Windows

Double-click **NLP_Suite.exe**. If Windows shows "Windows protected your PC," click **More info** → **Run anyway** (first time only).

### macOS

1. Double-click **NLP Suite Mac Setup** (included in the download)
2. Click **Select NLP Suite Folder** and point it to the extracted folder
3. Click **Remove Quarantine from Executable** and **Remove Quarantine from Folder** — this clears the macOS Gatekeeper block so the app can run
4. Click **Open NLP Suite**

> **Note:** The Mac Setup app is included in the download alongside NLP_Suite. It replaces the manual System Settings → Privacy & Security workaround. See [Troubleshooting](https://github.com/NLP-Suite/NLP-Suite/wiki/Troubleshooting) if you run into issues.

### First run

On the very first launch, the NLP Suite automatically creates default configuration files:

- **Input folder:** `lib/sampleData/newspaperArticles` (bundled sample texts)
- **Output folder:** `~/Documents/NLP_output`
- **NLP package:** Stanza
- **Language:** English

You can change these at any time in the I/O Configuration area at the top of the main window.

## Update

The NLP Suite automatically checks for new versions when you close the main window. If a newer release is available, it will prompt you to download and install it.

**Manual update:** If you want to skip the automatic check, go to [Releases](https://github.com/NLP-Suite/NLP-Suite/releases) and download the latest version, then extract it to a new folder.

Your output files and any external data are not stored inside the NLP Suite folder, so they are not affected by updates.

> **Note:** Your I/O configuration will reset to defaults after an update. The first-launch auto-config will set up new defaults automatically.

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
- GIS settings and configuration templates

**Enhancement files:**
- CoreNLP enhanced dependencies — parsing enhancement files for SVO extraction and linguistic analysis

## The Config Folder

The `config/` folder (created on first run in your home directory) stores your analysis settings and preferences:

**Default configurations:**
- `NLP_default_IO_config.csv` — your default input/output folders (so you don't have to re-select them each time)
- `NLP_default_package_language_config.csv` — your NLP package choice (Stanza, spaCy, or CoreNLP) and language preference

**Analysis settings:**
- Each analysis you run creates a config file that stores its parameters, allowing you to re-run analyses with identical settings later

**API keys:**
- `Google-geocode-API_config.csv` — Google Geocoding API key (if you use the GIS tools)
- `Google-Maps-API_config.csv` — Google Maps API key (if you use Google Maps visualization)
- `Pytesseract.csv` — Tesseract OCR settings (if you use PDF text extraction)

**External software:**
- `NLP_setup_external_software_config.csv` — paths to optional external tools (Stanford CoreNLP, MALLET, etc.)

The config folder is your personal settings hub — it persists across updates, so your preferences are preserved.

No separate installation of Python, Anaconda, Java, or WordNet is required.

See the [Install page](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite#whats-included) for details on what is and is not included.
