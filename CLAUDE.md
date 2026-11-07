# CLAUDE.md — NLP Suite

How to work in this repo. Open work, known bugs and tech debt live in **[PLAN.md](PLAN.md)**; keep both files current.

## What it is

A Tkinter-GUI toolkit for text analysis in the social sciences and humanities. A research codebase, not a library. Entry point: **`src/NLP_menu_main.py`**. About 220 modules in `src/`: ~55 `*_main.py` (GUIs), ~140 `*_util.py` (logic), plus shared helpers.

| Path | Contents |
|---|---|
| `src/` | All code |
| `lib/` | Data: word lists (`lib/wordLists`), dictionaries, reference CSVs, `release_version.txt`. Resolve via `GUI_IO_util.libPath` |
| `TIPS/`, `TIPS docx/` | PDF help files shown by each GUI's TIPS menu, and their editable `.docx` sources |
| `tests/` | pytest suite plus standalone GUI checks |
| `docs/` | Wiki pages and design notes |
| `setup_Windows/`, `setup_Mac/` | Installers |
| `NLP_Suite.spec` | PyInstaller build (`dist/`, `build/` are output) |
| `CHANGELOG.md` | Release notes; the top section becomes the GitHub release text |

## Architecture

- **A tool is a pair:** `X_main.py` (GUI + `run()`) and `X_util.py` (logic). `run_script_command = lambda: run(widget.get(), ...)` is bound to `GUI_util.run_button`; read widgets inside the lambda so values are current at RUN. Open another tool with `run_script_util.run_script("Y_main.py")`.
- **Layout is hand-placed** with `GUI_IO_util.placeWidget(...)` and its x/y constants. Change callbacks and logic, not placement, unless asked.
- **Importing a module has side effects.** `GUI_util` creates a `tkinter.Tk()` at import; most modules call `IO_libraries_util.install_all_Python_packages(...)`, which runs `pip` and may `sys.exit(0)`. Tests stub these (see Testing). Never run a `*_util.py` directly; the GUI is the entry point.
- **Parsers:** the user picks the package (Stanford CoreNLP, Stanza, spaCy) and language in `NLP_setup_package_language_main`; read them with `config_util.read_NLP_package_language_config()`. Never hardcode a parser. Flow: text → configured parser → CoNLL table (csv) → analysis. Work on CoNLL tables through `CoNLL_util`.
- **SRL** runs in its own Python 3.8 env (`transformer_srl`) via subprocess. Keep it out of the main env.

## Conventions

- **No silent failures.** Report problems with `tkinter.messagebox.showwarning/showerror`. No bare `except:`, no `except: pass`.
- Output files are named `NLP_...`, go to the configured output folder, and open via `IO_files_util.OpenOutputFiles`. Each label is added once.
- Table/column identifiers: lowercase with underscores.
- Cross-platform (Windows + Mac): use `os.path` / `os.sep`. Tests must pass on Linux (CI).

## Fixing an issue

1. Write a minimal failing test first, with synthetic data if needed.
2. Before changing a shared structure (CoNLL columns, DataFrame schemas, chart inputs, `GUI_IO_util` layout constants), grep the whole repo for every use and list them in the plan.
3. Fix it. Pull testable logic out of GUI callbacks into a `_util` function.
4. Run `pytest tests/`. After any GUI edit, also run `tests/gui_smoke.py`, and after a layout change, `tests/gui_layout_gate.py`.
5. One branch per issue, `fix/<issue-number>-<slug>`, PR against `roberto`. Reference the issue in the PR body (`Fixes #N`) so GitHub closes it on merge.
6. Update PLAN.md (move the item to Done) and add a user-facing line to CHANGELOG.md.

## Testing

- **New code comes with tests.** Target pure helpers; full GUI flows aren't unit-testable here.
- `pytest tests/`: `tests/conftest.py` puts `MagicMock` stubs for `GUI_util`, `IO_libraries_util` and the heavy NLP libs into `sys.modules` before import, so production code needs no changes. Stdlib stays real. `tests/_real_pandas.py` gives a test real pandas when it needs it.
- `python tests/gui_smoke.py`: imports every `src/*_main.py` in a subprocess under fake Tk to catch construction crashes, plus GOLDEN widget-label checks that catch a silently dropped row. GUIs in `KNOWN_SKIP` must be checked by launching.
- `python tests/gui_layout_gate.py`: builds each GUI under real Tk and fails on widgets that overflow the window or overlap. It measures this machine's Windows fonts only; Mac needs a person to look.
- The two GUI checks need the Anaconda NLP env with `Library/bin` on PATH.
- CI (`.github/workflows/tests.yml`): pytest on Ubuntu, Python 3.10, on push/PR to `roberto`.

## Lint and types

Ruff (lint + format, line length 120, target py39) and Pyright (standard mode, missing imports off) run through pre-commit on touched files only. Config: `pyproject.toml`, `pyrightconfig.json`, `.pre-commit-config.yaml`. Changed code must pass both.

## Environment

- Use the project's Anaconda environment; library versions are pinned in `requirements*.txt` (see the comments there for why, e.g. Pillow 10.4.0 for Tcl/Tk 8.6).
- Run: `python src/NLP_menu_main.py`, or one tool: `python src/X_main.py`.

## Branches and releases

- **`roberto`** is the integration branch: all PRs, yours and collaborators', target it. **`current-stable`** is what users get. The app's update check (`GUI_util.get_GitHub_release_version`) and `NLP_setup_update_util` read it. Only Roberto promotes `roberto` → `current-stable`.
- Don't edit files already changed by an open PR.
- **Release:** promote to `current-stable`, set `lib/release_version.txt` to the version (tag minus the `v`; CI fails the build if they differ), put the version's section at the top of `CHANGELOG.md`, then tag `v*` on `current-stable`. `build-installers.yml` builds the tagged commit. Before tagging, unzip the built artifacts and confirm the Windows entry point, the Mac `Launch NLP Suite (Mac).command`, and that the app imports. Pushing a tag is Roberto's call.
