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
| `data_manipulation_main.py` | +157 | **-178** (fits with room to spare) |
| `sample_corpus_main.py` | +419 | **-10** (fits) |
| `DB_PCACE_data_analysis_main.py` | +297 | **0** |
| `GIS_Google_Earth_main.py` | +276 (was +388) | **0** |
| `NLP_setup_package_language_main.py` | +731 | **0** |
| `DB_SQL_main.py` | +167 | **0** |

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

## Fixed: the deferred row-splitting backlog (Phase 4, `ctk/phase4-row-splitting`, 2026-07-22)

The six GUIs below were deliberately left for last (per the migration plan's Phase 4 note) since each
needed real per-GUI layout surgery, not a shared-code fix. All six are now at 0 or negative overflow.
Beyond the packed-row splits the row-splitting technique above already describes, this pass surfaced
three **new** failure modes worth naming, since they'll bite again wherever similar patterns exist:

1. **A `y_multiplier_integer += .5` "half-row nudge"**, a leftover from the old pixel `.place()` system,
   is fatal under grid. `placeWidget` computes `row = int(round(float(y_multiplier_integer)))`, and
   Python's *round-half-to-even* on a repeating `x.5` sequence collapses every OTHER pair of subsequent
   widget-groups onto the SAME grid row for the rest of the GUI — each collision then bumps a whole
   group (or a stray `?` HELP button) sideways into brand-new columns nothing else uses.
   `sample_corpus_main.py` had exactly one such nudge (mirrored once in its `help_buttons()`); deleting
   both dropped it from +419 to **-10** — the single largest fix in this backlog.
   A **one-time** fractional jump (e.g. `+4.5`, used to skip a deliberate multi-row gap) is just as
   fragile: its landing row depends on the *parity* of the counter at that point, so an unrelated
   upstream edit (any row split!) can silently flip it by a whole extra row. `DB_SQL_main.py` had one
   guarding the gap before its "Open output files" row; fixed by replacing `+4.5`/`+4.5` with a plain
   `+4` in both the main body and its `help_buttons()` mirror.
2. **A widget recreated on every callback without destroying (or reconfiguring) the previous instance**
   is a leaked-widget bug even under the OLD `.place()` layout (harmless there — the old one just sat
   invisibly underneath), but under grid it's also a WIDTH bug: `GUI_IO_util`'s per-row column-claim
   tracking is monotonic (never released on `.destroy()`), so each rebuild on the same row burns its old
   column pair and gets bumped further right, dragging its full pixel width into a brand-new column.
   `GIS_Google_Earth_main.py`'s icon-preview label and `NLP_setup_package_language_main.py`'s
   `parsers_lb`/`parsers_display_area` (previously "fixed" by destroy-before-recreate, which stops the
   double-draw but NOT the column drift) both had this. The robust fix is to **reconfigure the existing
   widget's text/image in place** instead of destroy+recreate+re-`placeWidget`, so the column claim is
   made exactly once for the widget's lifetime.
3. **A widget built and gridded AFTER `GUI_util.GUI_bottom()` already ran** never benefits from
   `apply_row_spans` (called once, by `GUI_bottom`, on whatever exists at that moment) and can visually
   collide with an earlier widget that WAS spanned expecting to share its row.
   `NLP_setup_package_language_main.py`'s `package_display_area` was built at the very end of the file
   (after `GUI_bottom`) specifically to avoid an unrelated bug where its own `placeWidget` call
   reassigned the module's running row counter with `global y_multiplier_integer` — clobbering
   `GUI_bottom`'s row argument. Fixed by scoping that one `placeWidget` call's return value locally
   (not `global`) and moving the widget's construction back to before `GUI_bottom`, where it belongs.

| GUI | overflow before | driver | fix |
|---|---|---|---|
| `data_manipulation_main.py` | +157 | one 8-widget operations row (WHERE/+/+/OK all sharing a far-right column band) **plus** a `create_option_menu(..., width=125)` — 125 is CHARACTERS not pixels (the factory has no `width_is_chars` escape hatch for OptionMenu), so a basename-only dropdown was 1000px wide | row-split into 2 rows (§ row-splitting technique); `width=125` → `width=30` |
| `sample_corpus_main.py` | +419 | the `+.5` half-row nudge (see above) collapsing every other row-pair for the rest of the GUI | deleted the nudge (both copies) |
| `DB_PCACE_data_analysis_main.py` | +297 | two 8-widget rows (Complex-object and Simplex-object checkboxes) each using a chain of `x+N` offsets bumping into new columns | row-split each into 2 rows; 2 matching extra `?` HELP buttons added |
| `GIS_Google_Earth_main.py` | +276 | an 11-widget "group" row (same `x+N` chain pattern) **plus** a leaked `image_lb` recreated on every icon change (also a genuine grid collision, independent of width) | row-split into 3 rows, 3 matching extra `?` HELP buttons; `image_lb.configure(image=...)` in place instead of destroy+recreate |
| `NLP_setup_package_language_main.py` | +731 | `package_display_area` (525px) and `parsers_display_area` (640px) landing in DIFFERENT, non-overlapping columns so their widths compounded instead of sharing; both were also drifting columns on every rebuild (failure mode 2 above) | reconfigure both labels in place (no more destroy+recreate); moved `package_display_area`'s construction before `GUI_bottom` and stopped it from clobbering the module's row counter |
| `DB_SQL_main.py` | +167 | a 9-widget row (DB tables/fields/Templates/Distinct/Import/Save) with the same `x+N` chain, **plus** the one-time `+4.5` parity bug (failure mode 1) once the row-split shifted the counter's parity | row-split into 2 rows, 1 matching extra `?` HELP button; `+4.5` → `+4` (both copies) |

All six verified via a real Tk+CTk harness (`mainloop` stubbed, `window.update()` flushes the
`after_idle` fit-to-content + shrink pass, then compare `winfo_reqwidth()` against geometry width and
scan `grid_slaves()` for cell collisions — the same technique the "Re-measuring" section below
describes) plus `pytest` (184 passed) and `gui_smoke` (0 crashed, 0 missing golden) after every change.
`ruff check` before/after each file showed an identical violation set (line numbers only shifted) —
confirms no new lint debt from either the layout edits or the bug fixes.

## Still overflowing

These four were never part of the Phase 4 row-splitting backlog above (that list — see the migration
plan's §4 — named exactly the six GUIs just fixed) and remain genuinely unaddressed. Each is wider than
the screen even after every shrinkable entry hits the 150px floor; fixing them needs the same per-GUI
row-splitting work as above, not a general-purpose knob.

| GUI | overflow (px) |
|---|---|
| `file_search_byWord_main.py` | +191 |
| `wordclouds_main.py` | +169 |
| `file_manager_main.py` | +103 |
| `SVO_main.py` | +48 |

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

The final Phase 3 tranche's other 4 GUIs (`ctk/phase3-remaining-tools`, 2026-07-21) all measured
clean on the 1470x956 reference screen: `SRL_main.py` (-88), `knowledge_graphs_DBpedia_YAGO_main.py`
(-236), `corpus_checker_PCACE_data_main.py` (-224), `statistics_csv_main.py` (-58).

Every other GUI measured zero or negative (fits with room to spare).

## Re-measuring

Import a GUI with `mainloop` stubbed out, call `window.update()` to flush the `after_idle`
fit-to-content pass, then compare `window.winfo_reqwidth()` against the geometry width. Note the
numbers are screen-size dependent — a wider screen shows less overflow.
