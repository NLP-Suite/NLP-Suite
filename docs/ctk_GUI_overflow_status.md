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

## Still overflowing

These are wider than the screen even after every shrinkable entry hits the 150px floor — their width
is driven by things the shrink pass leaves alone (long labels, checkbox text, dropdowns, button rows).
Fixing them needs per-GUI layout work (shorter labels, moving widgets to another row), not a
general-purpose knob.

| GUI | overflow (px) |
|---|---|
| `sample_corpus_main.py` | +426 |
| `html_annotator_main.py` | +379 |
| `DB_PCACE_data_analysis_main.py` | +301 |
| `file_search_byWord_main.py` | +191 |
| `wordclouds_main.py` | +169 |
| `DB_SQL_main.py` | +139 |
| `file_manager_main.py` | +103 |
| `DB_PCACE_data_validation_main.py` | +59 |
| `SVO_main.py` | +48 |
| `semantic_aggregation_main.py` | +34 |

`NLP_welcome_main.py` reports +8656 but is a false positive: its content is `.place()`d, not gridded,
so `reqwidth` is not meaningful there.

Every other GUI measured zero or negative (fits with room to spare).

## Re-measuring

Import a GUI with `mainloop` stubbed out, call `window.update()` to flush the `after_idle`
fit-to-content pass, then compare `window.winfo_reqwidth()` against the geometry width. Note the
numbers are screen-size dependent — a wider screen shows less overflow.
