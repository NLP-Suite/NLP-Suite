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

To update to a newer version:

1. Download the latest artifact from GitHub Actions (same process as above)
2. Extract the new zip to a new folder
3. Delete the old folder (or keep it as a backup)

Your output files and any external data are not stored inside the NLP Suite folder, so they are not affected by updates.

> **Tip:** Your I/O configuration will reset to defaults after an update. The first-launch auto-config will set up new defaults automatically.

## What's Bundled

The standalone build includes:

- Python runtime and all packages (Stanza, spaCy, NLTK, BERT, Plotly, matplotlib, etc.)
- WordNet lexical database (via NLTK)
- NRC Emotion Lexicon
- Sample data for testing
- TIPS documentation and reminders

No separate installation of Python, Anaconda, Java, or WordNet is required.

See the [Install page](https://github.com/NLP-Suite/NLP-Suite/wiki/Install-the-NLP-Suite#whats-included) for details on what is and is not included.
