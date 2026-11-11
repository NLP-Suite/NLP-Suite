### NLP Suite  ![GitHub release (latest by date)](https://img.shields.io/github/v/release/NLP-Suite/NLP-Suite?color=Green&label=Latest%20Version)  

## Standalone Application (PyInstaller build)

### Windows

| Problem | Solution |
|---------|----------|
| **"Windows protected your PC"** (SmartScreen) | Click **More info** → **Run anyway**. This only appears the first time. |
| **"VCRUNTIME140.dll not found"** or similar DLL error | Install the [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) (free, one-time install), then try again. |
| **Antivirus blocks or quarantines NLP_Suite.exe** | Some antivirus programs flag unsigned PyInstaller executables. Add the NLP_Suite folder to your antivirus exclusion list. |
| **App starts but immediately closes** | Open a Command Prompt, navigate to the NLP_Suite folder, and run `NLP_Suite.exe` from the command line to see the error message. |
| **"Permission denied" writing output files** | Make sure your output folder (default: `Documents\NLP_output`) is not read-only. Try running as Administrator if the problem persists. |

### macOS

| Problem | Solution |
|---------|----------|
| **"NLP_Suite cannot be opened because it is from an unidentified developer"** | Start the NLP Suite with **Launch NLP Suite (Mac).command** (included in the download); it removes the quarantine. The first time, right-click it → **Open** → **Open**. |
| **"NLP_Suite is damaged and can't be opened"** or **"code signature not valid"** | You started the `NLP_Suite` file directly. Use **Launch NLP Suite (Mac).command** instead. If that doesn't work, open Terminal and run: `xattr -cr /path/to/NLP_Suite` (drag the extracted NLP_Suite folder into Terminal to get the path). |
| **"NLP_Suite cannot be opened because Apple cannot check it for malicious software"** | Same fix — start it with **Launch NLP Suite (Mac).command**. |
| **The launcher itself is blocked** | Right-click **Launch NLP Suite (Mac).command** in Finder → **Open** → click **Open** in the dialog. This is only needed once. |
| **App crashes on launch with no error** | Open Terminal, drag **Launch NLP Suite (Mac).command** into it and press Enter to see the error output. |

### Both Platforms

| Problem | Solution |
|---------|----------|
| **First run: "No config file found"** | Normal — the app creates default config files automatically on first launch. If it fails, check that your Documents folder exists and is writable. |
| **Stanza model download fails** | Stanza downloads language models on first use (~525 MB for English). Check your internet connection. If behind a proxy, set the `HTTPS_PROXY` environment variable. |
| **spaCy model download fails** | Same as Stanza — requires internet on first use (~50 MB for the English model). Run the NLP Suite once with a working connection to download the models. |
| **BERT model download is slow** | BERT models (up to ~3 GB total) are downloaded from Hugging Face on first use of each BERT feature. This is normal and only happens once per model. Check your internet connection if the download stalls. |
| **Charts/visualizations don't open** | Check that your default browser is set. Plotly charts open as HTML files in your browser. PNG charts open in your default image viewer. |
| **"No module named X" error** | This should not happen with the standalone build. If it does, [report the issue](https://github.com/NLP-Suite/NLP-Suite/issues) with the full error message. |
| **Output files are empty** | Check that your input files are valid (UTF-8 encoded txt or csv). Check the output folder — files may have been written to a subdirectory. |

### Updating

| Problem | Solution |
|---------|----------|
| **"The pygit2 library is not available"** when closing | You have release 1.6.40 or older, which cannot update itself. Download the latest zip from [Releases](https://github.com/NLP-Suite/NLP-Suite/releases), unzip it in place of your current folder and copy your `config` folder across. |
| **The update says it cannot write to the folder** | Move the NLP Suite folder out of Program Files (e.g., to Desktop or `C:\NLP_Suite`) and try again. |
| **The update warns about OneDrive** | Move the NLP Suite folder out of OneDrive; a syncing folder can lock files during the update. |

---

## Running from Source (developer setup)

If you are running the NLP Suite from source code rather than the standalone build:

### Verify your environment

```bash
# Check Python version (the NLP Suite is built and tested on 3.10)
python --version

# Check that key packages are installed
python -c "import stanza; print(stanza.__version__)"
python -c "import nltk; print(nltk.__version__)"
python -c "import plotly; print(plotly.__version__)"
```

### Common errors

| Problem | Solution |
|---------|----------|
| **ModuleNotFoundError** | From the repository folder, in your `NLP` environment: `pip install -r requirements.txt`. |
| **NLTK resource not found** | Run `python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"` |
| **Tkinter not found** | On Linux: `sudo apt install python3-tk`. On macOS with Homebrew Python: `brew install python-tk`. Anaconda includes tkinter by default. |
| **Stanford CoreNLP connection refused** | CoreNLP requires Java (from source: install a Java 17 runtime, e.g. [Temurin](https://adoptium.net); the standalone build bundles one). Consider using **Stanza** instead (pure Python, no Java). |

---

## Reporting Issues

If your problem is not listed above:

1. Note the **exact error message** (copy-paste from the terminal/command line)
2. Note your **platform** (Windows 10/11, macOS version, Intel/Apple Silicon)
3. Note whether you are using the **standalone build** or **running from source**
4. [Open an issue](https://github.com/NLP-Suite/NLP-Suite/issues) with this information
