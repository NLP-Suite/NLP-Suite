# CTk empty-button status

Tracking widgets that render with **no visible content** — the small blank slivers and unlabeled
squares users read as "the GUI is broken". First audited 2026-07-18 against `ctk/phase1-grid`;
re-measured 2026-07-18 against `ctk/phase3-gis-tools` (`e860eb9d`). **Fully cleared 2026-07-21**
against `ctk/phase3-remaining-tools`.

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

## Open-file buttons (all cleared)

All were the `width=1, text=''` pattern above unless noted. Line numbers are unchanged from the
first audit for files not yet touched at the time.

> **GIS tools (2026-07-18, `ctk/phase3-gis-tools`)** cleared their 3 sites (`GIS_main.py` 535 + 779,
> `GIS_distance_main.py` 259, `GIS_symbolic_main.py` 310) via `create_open_file_button`, and the
> `GIS_main.py:774` placeholder (see below) is now `= None`.

> **DB/PCACE tools (2026-07-20, `ctk/phase3-db-pcace`)** cleared their 2 sites (`DB_SQL_main.py` 1433,
> `DB_PCACE_data_validation_main.py` 546) via `create_open_file_button`.

> **Statistical/visualization tools (2026-07-21, `ctk/phase3-stats-viz`)** cleared their 2 sites
> (`NGrams_CoOccurrences_main.py` 740, `word2vec_main.py` 301) via `create_open_file_button`.

> **Remaining setup GUIs (2026-07-21, `ctk/phase3-setup-gui`)** cleared their 4 sites
> (`NLP_setup_external_software_main.py` 77 + 118 + 153, `NLP_setup_package_language_main.py` 161)
> via `create_open_file_button`.

> **data_visualization (2026-07-21, `ctk/phase4-data-visualization`)** cleared its 2 sites (the
> `open_input_csv_file_button` on the window's csv-file row, and `openInputFile_button_comparative`
> on the Categorical tab's Comparative row) via `create_open_file_button`, as part of the Phase 4
> re-layout of the whole GUI (7 notebook tabs, ~140 `.place()` calls → `CTkTabview` + grid rows).

> **Final Phase 3 tranche (2026-07-21, `ctk/phase3-remaining-tools`)** cleared the last 3 sites
> (`sample_corpus_main.py` 161, `SRL_main.py` 109, `data_manipulation_main.py` 221) via
> `create_open_file_button`. **This table is now empty** -- every GUI in `src/` has been converted
> except the Phase 4 hard cases (`charts_Excel_main.py`, `narrative_analysis_ALL_main.py`,
> `license_GUI.py`), which were never counted here since they were always tracked separately.

> **Phase 4 hard cases (`ctk/phase4-remaining-hard-cases`)** converted: none of the three had an
> open-file-button sliver to begin with (checked both the `tk.Button(.*text='')` grep and the
> cross-line scan below) -- nothing to clear, just confirming the last unconverted GUIs are clean.

All sites cleared.

## Secondary: placeholder `tk.Button()` forward declarations

Four sites construct a **master-less, argument-less** button purely to declare the name before a
conditional branch reassigns it:

| File | line | reassigned at |
|---|---|---|
| `GUI_util.py` | 198 | 1020–1035 (`select_inputFilename_button`, per input type) |
| `GUI_util.py` | 199–201 | later in `IO_config_setup_*` (dir-select buttons) |

`tk.Button()` with no master attaches to Tk's **default root**, not to `GUI_util.window`. Today they
are never placed, so nothing renders — but they are live widgets on a root the suite does not manage,
and under a `CTk()` root they are the kind of thing that produces a stray window if Tk's default-root
resolution ever changes. Replace with `= None` when the surrounding GUI is converted; it costs
nothing and removes the hazard.

## Secondary: unlabeled checkboxes

✅ **Cleared (2026-07-20, `ctk/phase3-db-pcace`).** All ten sites now carry a short inline label
(`identifiers_checkbox` → "IDs", `extended_headers_checkbox` → "Ext hdrs", `parents_children_checkbox`
→ "Par/child", `document_sources_checkbox` → "Docs", `comments_checkbox` → "Comments",
`simplex_export_values_checkbox` → "Values", `simplex_charts_checkbox` → "Charts",
`simplex_timechart_checkbox` → "Timechart", `simplex_GIS_checkbox` → "GIS map" in
`DB_PCACE_data_analysis_main.py`; `expand_complex_cb` → "Expand" in `DB_SQL_main.py`), so each reads on
its own instead of depending on positional correspondence with an explanatory label a row up. The
adjacent full-sentence label and hover tooltip are unchanged.

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
