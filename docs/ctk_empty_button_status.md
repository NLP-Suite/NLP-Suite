# CTk empty-button status

Tracking widgets that render with **no visible content** — the small blank slivers and unlabeled
squares users read as "the GUI is broken". First audited 2026-07-18 against `ctk/phase1-grid`;
re-measured 2026-07-18 against `ctk/phase3-gis-tools` (`e860eb9d`).

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

## ✅ Fixed since the first audit

The **sentiment / annotator / semantic tranche** (`d297d1d1`, PR #13) cleared 5 of the original 21
sites, all via the `create_open_file_button` swap:

| GUI | was line | what it opened |
|---|---|---|
| `html_annotator_main.py` | 226 | annotator dictionary file (started `state='disabled'`) |
| `html_annotator_gender_main.py` | 229 | annotator dictionary file (started `state='disabled'`) |
| `semantic_aggregation_main.py` | 316 | input csv file |
| `semantic_analysis_main.py` | 516 | input csv file |
| `semantic_analysis_main.py` | 642 | WSI keywords file |

That leaves **one** `state='disabled'` site open (`DB_SQL_main.py:1433`) — the two annotator ones are
done. The remaining `html_annotator_gender_main.py:374` grep hit is a **commented-out** line, not a
live widget.

## Remaining empty open-file buttons

**17 sites across 15 files.** All are the `width=1, text=''` pattern above unless noted. Line numbers
are unchanged from the first audit — none of the remaining files have been touched yet.

| GUI | line | what it opens |
|---|---|---|
| `data_visualization_main.py` | 569 | input csv file |
| `data_visualization_main.py` | 1015 | comparative csv (literal `width=1`, parented to `tab_categorical`) |
| `DB_SQL_main.py` | 1433 | input file (starts `state='disabled'`) |
| `DB_PCACE_data_validation_main.py` | 546 | input file |
| `GIS_main.py` | 535 | input csv file |
| `GIS_main.py` | 779 | API config file (also a `tk.Button()` placeholder at 774 — see below) |
| `GIS_distance_main.py` | 259 | input file |
| `GIS_symbolic_main.py` | 310 | input file |
| `NGrams_CoOccurrences_main.py` | 740 | input csv file |
| `NLP_setup_external_software_main.py` | 77 | config file |
| `NLP_setup_external_software_main.py` | 118 | software website |
| `NLP_setup_external_software_main.py` | 153 | software directory |
| `NLP_setup_package_language_main.py` | 161 | config file |
| `sample_corpus_main.py` | 161 | sample corpus file |
| `SRL_main.py` | 109 | input csv file |
| `data_manipulation_main.py` | 221 | input file |
| `word2vec_main.py` | 301 | word-distance file |

> The four `GIS_*` rows (and the `GIS_main.py:774` placeholder below) are **in flight** on
> `ctk/phase3-gis-tools` as of this re-measure — expect them to clear with that tranche.

The one remaining `state='disabled'` site starts grey under the CTk theme, correctly — but grey *and*
blank is still unreadable. The glyph is what makes the disabled state legible as "this button has
nothing to open yet".

## Secondary: placeholder `tk.Button()` forward declarations

All five sites still open. Each constructs a **master-less, argument-less** button purely to declare
the name before a conditional branch reassigns it:

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

All ten still open (the DB/PCACE tranche has not landed). Each `tk.Checkbutton(window, text='', ...)`
renders as a bare square whose meaning lives only in an adjacent explanatory label and its hover
tooltip:

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
grep -n "tk\.Button()" src/*.py             # placeholder declarations
grep -n "tk\.Checkbutton(.*text=''" src/*.py
```

⚠️ **Do not** count empty open-file buttons with `grep -n "tk\.Button(.*text=''"`. Most of these
constructors wrap across lines, with `text=''` on a line of its own — that grep under-reports (it
misses `GIS_main.py:779`, among others) and so can report a GUI clean while the sliver is still
there. Scan across lines instead:

```
python3 - <<'EOF'
import glob, os, re
pat = re.compile(r"tk\.Button\(\s*[^)]*?text\s*=\s*''[^)]*?\)", re.S)
for f in sorted(glob.glob('src/*.py')):
    src = open(f, encoding='utf-8', errors='replace').read()
    lines = src.split('\n')
    for m in pat.finditer(src):
        n = src[:m.start()].count('\n') + 1
        tag = ' [COMMENTED]' if lines[n-1].lstrip().startswith('#') else ''
        print(f"{os.path.basename(f)}:{n}{tag}")
EOF
```

A converted GUI should return **zero** live hits from that scan and from the `tk.Button()` grep.
Note that `create_open_file_button` discards any `text`/`width` passed to it, so a converted site
cannot regress silently.
