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

## Still overflowing

These are wider than the screen even after every shrinkable entry hits the 150px floor — their width
is driven by things the shrink pass leaves alone (long labels, checkbox text, dropdowns, button rows).
Fixing them needs per-GUI layout work (shorter labels, moving widgets to another row), not a
general-purpose knob — see the row-splitting technique above.

| GUI | overflow (px) |
|---|---|
| `sample_corpus_main.py` | +426 |
| `DB_PCACE_data_analysis_main.py` | +301 |
| `file_search_byWord_main.py` | +191 |
| `wordclouds_main.py` | +169 |
| `DB_SQL_main.py` | +139 |
| `file_manager_main.py` | +103 |
| `DB_PCACE_data_validation_main.py` | +59 |
| `SVO_main.py` | +48 |

`NLP_welcome_main.py` reports +8656 but is a false positive: its content is `.place()`d, not gridded,
so `reqwidth` is not meaningful there.

Every other GUI measured zero or negative (fits with room to spare).

## Re-measuring

Import a GUI with `mainloop` stubbed out, call `window.update()` to flush the `after_idle`
fit-to-content pass, then compare `window.winfo_reqwidth()` against the geometry width. Note the
numbers are screen-size dependent — a wider screen shows less overflow.
