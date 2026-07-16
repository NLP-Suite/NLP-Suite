# CLAUDE.md — NLP Suite

Guidance for Claude (and humans) working in this repo. Keep it current as the architecture evolves.

## What this is

The **NLP Suite** is a large, GUI-driven natural-language-processing toolkit aimed at social-science / humanities text analysis. It is a **research codebase**, not a library: ~200 Python modules under `src/`, each tool a Tkinter GUI. Entry point is the menu **`src/NLP_menu_main.py`**.

Scale: `src/` has **~50 `*_main.py`** (GUIs) + **~122 `*_util.py`** (logic) + shared utilities (~201 `.py` total).

## Repository layout

| Path | Contents |
|---|---|
| `src/` | All code: `*_main.py` (GUIs) + `*_util.py` (logic) + shared utils |
| `lib/` | Data resources (word lists, dictionaries, reference CSVs). Resolve via `GUI_IO_util.libPath`; word lists under `lib/wordLists` |
| `TIPS/` | PDF help docs shown by the GUIs' TIPS dropdown; **`TIPS docx/`** holds their editable `.docx` sources |
| `docs/`, `videos/`, `config/`, `reminders/` | Documentation, tutorial videos, config, reminder text |
| `setup_Mac/`, `setup_Windows/`, `setup-app/` | Installers / environment setup |
| `dist/`, `build/` | PyInstaller output (spec is `NLP_Suite.spec` at repo root) |
| `tests/` | pytest suite (introduced in PR #1635) |

## Architecture & conventions

### The GUI-tool pattern
- A tool is usually a pair: **`X_main.py`** (the GUI + a `run()` function) and **`X_util.py`** (the logic).
- GUIs are built with Tkinter through **`GUI_util`** and **`GUI_IO_util`** (the latter provides `placeWidget(...)` and x/y coordinate constants). Widget **placement/layout is hand-managed** — when changing a GUI, prefer editing logic/callbacks and leave widget placement alone unless explicitly asked.
- **`run()` pattern:** each `X_main.py` defines `run(...)`; a `run_script_command = lambda: run(widget.get(), ...)` is bound to `GUI_util.run_button`. Read widget values as `widget.get()` *inside* the lambda so they're current at RUN time.
- Open another tool's GUI with `run_script_util.run_script("Y_main.py")`.

### Import-time coupling (important for testing)
Importing a module is **not** side-effect-free:
- `GUI_util` creates a `tkinter.Tk()` window at import.
- Most modules begin with `IO_libraries_util.install_all_Python_packages(...)` which shells out to `pip` and may `sys.exit(0)`.

So legacy modules are GUI/infra-coupled. Tests work around this by stubbing these in `sys.modules` *before* import (see **Testing**).

### NLP parser pipeline
- The default **NLP package** (parser: *Stanford CoreNLP* / *Stanza* / *spaCy*) and corpus **language** are set in **`NLP_setup_package_language_main`** and read via **`config_util.read_NLP_package_language_config()`** (returns `package`, `language`, memory/encoding options, …).
- Parsers produce **CoNLL tables** (csv). Operate on them with **`CoNLL_util`** (e.g. `check_CoNLL`, `get_nouns_verbs_CoNLL`).
- **Do not hardcode a parser** — honor the configured `package`. The canonical flow for raw text is **text → configured parser → CoNLL table → analysis** (`parsers_annotators_main`, `Stanza_util` / `Stanford_CoreNLP_util` / `spaCy_util`).
- **SRL** runs in an isolated **Python 3.8** env (`transformer_srl`, pinned legacy stack) invoked via subprocess — keep it out of the main env.

### General conventions
- **No silent failures** — surface problems with `tkinter.messagebox` (`showwarning`/`showerror`); don't swallow exceptions.
- Output files use an `NLP_...` naming scheme, are written to the configured output dir, and opened via `IO_files_util.OpenOutputFiles`.
- DB/table column identifiers are lowercase with underscores.

## Environment & running
- Use the project's **Anaconda** environment (the suite pins specific NLP library versions); activate it before running Python.
- Run the menu: `python src/NLP_menu_main.py` (or a specific tool: `python src/X_main.py`).
- Packaging: **PyInstaller** via `NLP_Suite.spec` (release builds are tag-triggered).

## Testing (PR #1635)
- **Everything added should have associated unit tests** — new helpers, functions, or logic land together with tests that cover them (extract testable logic out of GUI callbacks so it can be tested).
- Run with `pytest tests/`.
- `tests/conftest.py` replaces `GUI_util`, `IO_libraries_util`, and the heavy NLP libs (Stanza/spaCy/NLTK/pandas/…) with `MagicMock` stubs in `sys.modules` **before** the module under test is imported — neutralizing the import-time guards **without changing production code**. Real stdlib (`re`, `string`, `collections`, …) is left intact.
- **Target pure, stdlib-only helpers** (e.g. `statistics_txt_util` word/diversity helpers, `CoNLL_util`, `semantic_aggregation_util`, regex builders). Full GUI flows are not unit-testable here.
- CI: `.github/workflows/tests.yml` runs the suite on push/PR.
- **GUI construction smoke test** (standalone, like `tests/ctk_bundle_smoke.py`; no pytest): `python tests/gui_smoke.py` imports every `src/*_main.py` in a subprocess under Tk / GUI_util / heavy-lib stubs to catch **construction crashes** across all ~50 GUIs, plus **GOLDEN widget-label checks** for key GUIs (DB_SQL, corpus_profiler) that catch a **silently-dropped row** (the DB_SQL "Select INPUT CSV file" regression is what motivated it). **Run it after ANY GUI edit** (needs the Anaconda env with `Library/bin` on PATH). Exit 0 = clean; a real crash or a missing golden label = non-zero. A few deeply GUI_util-coupled GUIs are in `KNOWN_SKIP` — verify those by launching.

## Linting & type-checking (PR #1636)
- **Ruff** (lint + format) and **Pyright** run through **pre-commit**, **gated on touched files** — the ~200-file legacy backlog won't block commits, but anything you change is enforced.
- Config: `pyproject.toml` (Ruff; line length **120**, target **py39**, pyflakes/isort/pyupgrade/bugbear + Pylint port), `pyrightconfig.json` (standard mode; missing-import reports off so legacy bare imports don't drown real type errors).
- New or changed code should pass Ruff + Pyright.

## Key subsystems (pointers)
- **Semantic aggregation** — `semantic_aggregation_main` + `semantic_aggregation_util` (+ `semantic_aggregation_WordNet_util`): WordNet / VerbNet / FrameNet via a "Knowledge base" dispatcher; category lists in `lib/VerbNet_classes.csv`, `lib/FrameNet_frames.csv`.
- **SRL** — `SRL_worker` (isolated 3.8 env) + `SRL_util`; SemLink maps under `lib/SRL/`.
- **Parsers / annotators** — `parsers_annotators_main`; `Stanza_util`, `Stanford_CoreNLP_util`, `spaCy_util`.
- **CoNLL** — `CoNLL_util`, `CoNLL_table_analyzer_main`.
- **Dictionary annotation** — `html_annotator_dictionary_util`.
- **Style / statistics** — `statistics_txt_util`, `style_analysis_main`.

## Working notes
- Branches: feature work lands via PRs against **`roberto`** — the integration/release branch the installer workflow (`build-installers.yml`) checks out and that `v*` release tags are built from. (`current-stable` is an older snapshot behind `roberto`; don't target it.) Avoid editing files already owned by an open PR.
- The suite is Windows/Mac cross-platform; prefer `os.path`/`os.sep` and avoid platform-specific assumptions.
