# CTk empty-button status

Tracking widgets that render with **no visible content** — the small blank slivers and unlabeled
squares users read as "the GUI is broken". Audited 2026-07-18 against `ctk/phase1-grid`.

## Background

The legacy idiom for the small "open the file/directory you just selected" affordance is:

```python
tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=...)
```

`open_file_directory_button_width` is **1** on Mac (`GUI_IO_util.py:580`) and **3** on Windows
(`GUI_IO_util.py:971`), and `text` is empty — so the button paints as an ~8 px blank rectangle with
no glyph, no label, and no tooltip of its own. Under stock tk it read as a stray artifact; under the
CTk theme (§0 of the migration plan: red = enabled, grey = disabled) it reads as a **red bar or grey
box**, which is worse — the color now actively claims it is a meaningful control.

**The fix already exists:** `GUI_theme_util.create_open_file_button()` (`GUI_theme_util.py:305`)
drops the legacy `text`/`width` kwargs and substitutes a folder glyph (`OPEN_FILE_GLYPH`, 📂) at a
real 32 px pixel width. Converting a site is a one-line swap:

```python
openInputFile_button = GUI_theme_util.create_open_file_button(
    window, command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
```

Every GUI already converted in Phases 2–3 went through this swap. The sites below are the ones
remaining in **unconverted** GUIs — they will be fixed as their tranche lands, so this doc is a
checklist for those tranches rather than separate work.

## Remaining empty open-file buttons

21 sites across 18 files. All are the `width=1, text=''` pattern above unless noted.

| GUI | line | what it opens |
|---|---|---|
| `data_visualization_main.py` | 569 | input csv file |
| `data_visualization_main.py` | 1015 | comparative csv (literal `width=1`, parented to `tab_categorical`) |
| `DB_SQL_main.py` | 1433 | input file |
| `DB_PCACE_data_validation_main.py` | 546 | input file |
| `GIS_main.py` | 535 | input csv file |
| `GIS_main.py` | 779 | API config file (also a `tk.Button()` placeholder at 774 — see below) |
| `GIS_distance_main.py` | 259 | input file |
| `GIS_symbolic_main.py` | 310 | input file |
| `html_annotator_main.py` | 226 | annotator dictionary file (starts `state='disabled'`) |
| `html_annotator_gender_main.py` | 229 | annotator dictionary file (starts `state='disabled'`) |
| `NGrams_CoOccurrences_main.py` | 740 | input csv file |
| `NLP_setup_external_software_main.py` | 77 | config file |
| `NLP_setup_external_software_main.py` | 118 | software website |
| `NLP_setup_external_software_main.py` | 153 | software directory |
| `NLP_setup_package_language_main.py` | 161 | config file |
| `sample_corpus_main.py` | 161 | sample corpus file |
| `semantic_aggregation_main.py` | 316 | input csv file |
| `semantic_analysis_main.py` | 516 | input csv file |
| `semantic_analysis_main.py` | 642 | WSI keywords file |
| `SRL_main.py` | 109 | input csv file |
| `data_manipulation_main.py` | 221 | input file |
| `word2vec_main.py` | 301 | word-distance file |

Three of these carry `state='disabled'` at construction, so under the CTk theme they correctly start
grey — but grey *and* blank is still unreadable. The glyph is what makes the disabled state legible
as "this button has nothing to open yet".

## Secondary: placeholder `tk.Button()` forward declarations

Five sites construct a **master-less, argument-less** button purely to declare the name before a
conditional branch reassigns it:

| File | line | reassigned at |
|---|---|---|
| `GUI_util.py` | 198 | 1020–1035 (`select_inputFilename_button`, per input type) |
| `GUI_util.py` | 199–201 | later in `IO_config_setup_*` (dir-select buttons) |
| `GIS_main.py` | 774 | 779 (`open_API_config_button`) |

`tk.Button()` with no master attaches to Tk's **default root**, not to `GUI_util.window`. Today they
are never placed, so nothing renders — but they are live widgets on a root the suite does not manage,
and under a `CTk()` root they are the kind of thing that produces a stray window if Tk's default-root
resolution ever changes. Replace with `= None` when the surrounding GUI is converted; it costs
nothing and removes the hazard.

## Secondary: unlabeled checkboxes

Ten `tk.Checkbutton(window, text='', ...)` sites render as bare squares whose meaning lives only in
an adjacent explanatory label and their hover tooltips:

| GUI | lines |
|---|---|
| `DB_PCACE_data_analysis_main.py` | 971, 979, 987, 996, 1007 (mode selectors) |
| `DB_PCACE_data_analysis_main.py` | 1135, 1143, 1151, 1159 (simplex export options) |
| `DB_SQL_main.py` | 831 (`expand_complex_cb`) |

These are **not** a grid-migration regression — they are placed with `sameY=True`, so `_column_for`
bumps each to the next free column and left-to-right order (the order the explanatory label names
them in) is preserved. But a labelless checkbox depending on positional correspondence with a
sentence one row up is fragile, and it is invisible to the golden-label checks in
`tests/gui_smoke.py`. Worth giving each a short inline label when the DB/PCACE tranche lands.

## Re-measuring

```
grep -n "tk\.Button(.*text=''" src/*.py     # empty open-file buttons
grep -n "tk\.Button()" src/*.py             # placeholder declarations
grep -n "tk\.Checkbutton(.*text=''" src/*.py
```

A converted GUI should return **zero** hits for the first two. Note that `create_open_file_button`
discards any `text`/`width` passed to it, so a converted site cannot regress silently.
