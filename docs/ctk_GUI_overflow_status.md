# CTk GUI width-overflow status

Tracking which GUIs render wider than the window they are given, i.e. content is clipped off the
right edge. Generated on a **1470x956** Mac screen (2026-07-18) — `overflow` is
`window.winfo_reqwidth() - geometry_width` measured *after* `GUI_util._fit_window_to_content()` has
run, so a positive number is real clipping the user sees.

## Background

`GUI_util._fit_window_to_content()` grows a GUI to fit its content but clamps at the screen width,
then calls `_shrink_wide_fields_to_fit()` to narrow wide text fields so the content fits anyway.

That shrink pass was a **no-op under CustomTkinter**: it selected candidates with
`winfo_class() in {'Entry','Text',...}`, but a `CTkEntry` is a *Frame* wrapping an inner tk `Entry`,
so it reports class `Frame` and was never selected. The only widget the filter did match was the
inner tk `Entry`, whose `width` is in **characters** — shrinking it leaves the outer frame's pixel
width untouched. So the loop ran 400 no-op iterations and every over-wide CTk GUI stayed clipped.
Fixed by selecting CTk widgets via `isinstance` and shrinking their **pixel** width.

`CTkOptionMenu` is deliberately *not* shrinkable: unlike an entry it does not scroll, so narrowing
one clips its label with no way to read it.

## Fixed

| GUI | before | after |
|---|---|---|
| `NER_main.py` | +132 | **0** |
| `CoNLL_table_analyzer_main.py` | +106 | **0** |
| `html_annotator_main.py` | +687 (reqwidth 2157 vs. 1470 screen) | **0** (reqwidth 1420) |
| `semantic_aggregation_main.py` | not clipped, but only 34px from the screen edge (reqwidth 1436) | **0**, 51px margin (reqwidth 1419) |
| `semantic_analysis_main.py` | +164 (reqwidth 1634 vs. 1470 screen; missed by the sweep below — found via a bug report about the 'maximum number of keywords' slider) | **0** (reqwidth 1426) |
| `DB_PCACE_data_validation_main.py` | +59 | **0**, 58px margin (reqwidth 1412) |

`DB_PCACE_data_validation_main.py` fits **incidentally** to the Phase 3 DB/PCACE-tranche widget-factory
conversion (`tk.Combobox`/`Entry`/`Button` → `create_combobox`/`create_entry`/`create_button`), not via
row-splitting — the char→px translation happened to net narrower than the raw tk widths it replaced on
this particular GUI. Contrast `DB_SQL_main.py` below, where the same conversion made the overflow worse.

Fixed via **per-GUI row-splitting**, the technique the "still overflowing" section below calls for: a
legacy row crammed many widgets onto one line via `sameY=True` chaining, and since grid columns are
shared by the whole window (see `apply_row_spans` in `GUI_IO_util.py`), each widget whose
`x_coordinate` collided with one already used *on that row* got bumped into a brand-new column nothing
else in the GUI reused — summing to far more width than the screen. The fix: end the row earlier
(`sameY=False`) and give the trailing widgets their own row, reusing an `x_coordinate` that already
lands in a column an *earlier* row pays for (so the shared column costs nothing extra). Splitting a row
this way adds a content row that the GUI's local `help_buttons()` counter doesn't know about — that
counter is independent of the main `y_multiplier_integer` sequence, and `GUI_bottom`'s own trailing
widgets are positioned off the row `help_buttons()` returns, so an unsynced split causes the *next*
symptom: new content silently overlapping `GUI_bottom`'s row instead of running off-screen. Every row
split must add one matching `place_help_button(...)` call (reusing the same message) to keep the two
counters aligned. Verified with a real (not stubbed) Tk instance and `mainloop` patched to a no-op —
the stubbed `tests/gui_smoke.py` harness can't measure pixel geometry since its fake tkinter never lays
anything out.

## Partial fix: the I/O summary label

`GUI_util.IO_config_setup_brief`'s `IO_setup_brief_display_area` (the "INPUT DIR: .../OUTPUT DIR: ..."
box on the top row of every brief-mode GUI) was a `CTkLabel` fixed at `width=44` chars (352px), sized
for a worst-case long path. Brief mode only ever shows a directory *basename*, so on GIS_Google_Earth_main
this rendered ~110px of dead space after the printed text and pushed every column to its right —
visibly, the "Select csv field" dropdown on the group row was clipped flush against the window's right
edge (user report). Narrowed the default to `width=30`; a `CTkLabel`'s width is a floor, not a cap (an
unusually long path still renders in full, just wider), so this only tightens the common case. This is
shared code, so every brief-mode GUI gets a bit of the gap closed, not just GIS_Google_Earth_main (whose
overflow dropped +388 → +276 — the row-splitting fix below is still needed to reach 0).

## Still overflowing

These are wider than the screen even after every shrinkable entry hits the 150px floor — their width
is driven by things the shrink pass leaves alone (long labels, checkbox text, dropdowns, button rows).
Fixing them needs per-GUI layout work (shorter labels, moving widgets to another row), not a
general-purpose knob — see the row-splitting technique above.

| GUI | overflow (px) |
|---|---|
| `sample_corpus_main.py` | +426 |
| `DB_PCACE_data_analysis_main.py` | +297 (was +301, essentially unchanged by the Phase 3 DB/PCACE widget-factory conversion) |
| `GIS_Google_Earth_main.py` | +276 (was +388; narrowing `IO_setup_brief_display_area` above closed part of it) |
| `NLP_setup_package_language_main.py` | +731 (uncoverable before this tranche — the GUI crashed on open, see below) |
| `file_search_byWord_main.py` | +191 |
| `wordclouds_main.py` | +169 |
| `DB_SQL_main.py` | +167 (was +139; the Phase 3 DB/PCACE widget-factory conversion made this one WORSE — CTk's char→px multiplier for its many comboboxes/buttons nets wider than the raw tk widths it replaced. Needs the same row-splitting technique as the fixed GUIs above.) |
| `file_manager_main.py` | +103 |
| `SVO_main.py` | +48 |

`NLP_setup_package_language_main.py` (remaining-setup-GUIs tranche, `ctk/phase3-setup-gui`) is driven by two disabled "display value" `CTkLabel`s the shrink pass doesn't touch (it only targets Entry-like widgets, §Background above): `package_display_area` (`width=package_display_area_width`, 60/80 chars → up to 640px) and `parsers_display_area` (`width=80` chars, 640px), both recreated on every NLP-package change. Before this tranche the GUI could not even be measured — a vestigial `.pack()` next to each of its three `tk.Scale`s (the same class of bug fixed in the sentiment/annotator/semantic tranche) raised `TclError` the moment `placeWidget` grids the window, so it crashed on open. Converting to `create_slider` and dropping the three `.pack()` calls fixed the crash and, along the way, surfaced a second pre-existing bug: `changed_NLP_package_set_parsers()` re-creates `parsers_lb`/`parsers_display_area` on every call (3x during startup alone) without destroying the previous instance -- under old `.place()` the leftovers just sat invisibly on top of each other, but under grid each one that lands on an already-occupied column band gets bumped into a fresh column, so the leaks alone were adding ~1280px. Fixed by destroying the previous pair before creating the new one. The remaining +731 is genuine layout width from the two display labels and needs the row-splitting technique other overflowing GUIs above are waiting on.

`NLP_welcome_main.py` reports +8656 but is a false positive: its content is `.place()`d, not gridded,
so `reqwidth` is not meaningful there.

`data_visualization_main.py` (Phase 4, `ctk/phase4-data-visualization`) measured **−10** (fits) after
its re-layout. Before Phase 4 it was in the same `.place()`d-content boat as `NLP_welcome` — its ~140
widgets were absolutely positioned inside `ttk.Notebook` tab frames, so `reqwidth` was meaningless. The
conversion to a `CTkTabview` with grid rows (each row a transparent `CTkFrame` whose widgets pack
left-to-right) makes it measurable, and it fits on the 1470×956 reference screen with room to spare —
no row-splitting needed. The tabview is a fixed 320px tall (a floor for its 7-row Numeric tab); if a
future row is added the height may need bumping so the last row is not clipped by the tab body.

`GIS_main.py` (Phase 3 GIS tranche, `ctk/phase3-gis-tools`) could not be measured in this sandbox —
its module-level `Stanza_util`/`spaCy_util`/`Stanford_CoreNLP_util`/`BERT_util` imports pull in
multi-hundred-MB models and exit before the window builds when optional ML deps (`sentencepiece`,
`tensorflow`, ...) are missing, same pre-existing gap as its `gui_smoke` `UNCOV` status. Needs
measuring in a full Anaconda env. `GIS_distance_main.py` (+0) and `GIS_symbolic_main.py` (-88) measured
clean on the 1470x956 reference screen.

Every other GUI measured zero or negative (fits with room to spare).

## Re-measuring

Import a GUI with `mainloop` stubbed out, call `window.update()` to flush the `after_idle`
fit-to-content pass, then compare `window.winfo_reqwidth()` against the geometry width. Note the
numbers are screen-size dependent — a wider screen shows less overflow.
