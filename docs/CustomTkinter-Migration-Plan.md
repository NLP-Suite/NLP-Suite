# CustomTkinter Migration Plan

**Goal:** migrate every NLP Suite GUI from plain `tkinter` to
[CustomTkinter](https://customtkinter.tomschimansky.com/) (CTk) — a modern, consistent, HiDPI-aware
look, retiring the absolute-pixel layout that makes the current GUIs janky and platform-divergent.

**Converting a GUI? Work from §3 (widget map) and §6 (checklist).** The rest is context.

---

## 0. Design premise: color is a signal, not styling

**Current rule** (cut 3, 2026-07-18) — ⚠️ *needs Roberto's sign-off before it goes past pilot 2*:

- **Brand red `#b10a0a` = ENABLED** (default fill of every interactive widget).
- **Flat grey = DISABLED** (applied automatically on `state='disabled'`).

Color is **information, not decoration**; encoded in `nlp_suite_theme.json` plus `accent=`/`muted=`
opt-ins in `GUI_theme_util`. Two earlier cuts were reverted: **cut 1** (solid red everywhere) read as
noise and overwrote the load-bearing convention that a red *Open TIPS/videos/reminders* dropdown
signals a resource *exists*; **cut 2** (neutral-grey default, red only for RUN + availability
dropdowns) made every GUI read as disabled. Cut 3 keeps Roberto's availability cue (empty dropdown
greys out; red = "a resource exists") but doesn't solve "the wall of red reads as noise" — a deliberate
trade by Cora. Two one-liner fallbacks if Roberto prefers: flip the theme JSON fills to neutral (cut 2),
or to a light bordered surface (red border + text, solid red for RUN/signal only).

**Mechanics:** CTk does *not* repaint on `state='disabled'` — it swaps `text_color_disabled` and leaves
the fill. `GUI_theme_util._StateFillMixin` closes the gap: captures the enabled fill at construction and
repaints on every state change, restoring a *call-site* color on re-enable. Call sites keep plain
`configure(state=…)` unchanged — which matters, since the suite toggles disabled state constantly (§5.4).

---

## 1. Current state (audit)

Measured on `current-stable`, July 2026.

| Fact | Value |
|---|---|
| Files in `src/` importing tkinter | 146 |
| GUI entry scripts (`*_main.py`, each a separate process) | ~50 |
| Shared GUI framework | `GUI_util.py` (1,683 lines) + `GUI_IO_util.py` (1,516 lines) |
| `tk.IntVar` / `tk.StringVar` | 386 / 377 |
| `tk.Label` / `Checkbutton` / `Button` / `OptionMenu` / `Entry` | 335 / 307 / 246 / 200 / 133 |
| `ttk.Combobox` / `Style` / `Frame` / `Notebook` | 56 / 9 / 7 / 1 |
| Raw `.place(x=…, y=…)` outside the helper | 140 in `data_visualization_main.py` alone |

### 1.1 How a GUI is built today

1. `import GUI_util` **creates the root window as a module-level side effect** (`window = tk.Tk()`,
   `GUI_util.py:17`); every widget parents to this singleton.
2. Widgets built at module top level (no classes/functions), with module-level `StringVar`/`IntVar`
   globals and `.trace('w', …)` callbacks for reactivity.
3. Positioned via `GUI_IO_util.placeWidget(window, x_coordinate, y_multiplier_integer, widget, …)` — an
   absolute pixel grid, hard-coded 40 px line height, X-constants in parallel `darwin`/Windows blocks.
4. Shared chrome from `GUI_top(…)` (I/O row) and `GUI_bottom(…)` (Read Me / videos / TIPS / reminders /
   Setup / RUN / Close); a left-edge column of `?` HELP buttons via `place_help_button`; tooltips via
   `hover_over_widget` (reconstructs positions from the same coordinates).
5. GUIs launch each other as **separate processes** (`run_script_util.run_script`) — no shared root, no
   multi-window state.

**Why it looks janky:** nothing reflows on resize; long labels overlap entries; each Mac/Windows
difference needs its own constant; default tk widgets look 1990s on Windows; the 40 px grid forces tall
GUIs off-screen (the "scrollbar does not scroll" TODO). No dark mode, no HiDPI story.

### 1.2 Packaging constraints (read before touching anything)

The suite ships as a PyInstaller bundle (`NLP_Suite.spec`) with a **portable python-build-standalone
interpreter** in `python-env/` that **statically embeds Tcl/Tk**, so `PIL.ImageTk` **crashes**
(`invalid command name "PyImagingPhoto"`). The in-tree workaround `GUI_util.tk_image_from_pil`
(`GUI_util.py:192`) feeds Tk base64-PNG bytes through plain `tk.PhotoImage(data=…)`. **CTk's `CTkImage`
uses `PIL.ImageTk` internally** — see §5.1. `Pillow` is pinned to `10.4.0` (12.x breaks bundled Tcl/Tk
8.6); CTk is compatible, its only hard dep is `darkdetect`.

> **Version note:** the suite pins **`customtkinter==6.0.0`** (not `5.2.x`). All wrapper work targets the
> 6.0.0 API (`CTkLabel` has no `justify`; `CTkEntry` has neither `justify` nor `anchor`).
> `GUI_theme_util.translate_kwargs` filters kwargs against each CTk class's real 6.0.0 signature.

---

## 2. Migration strategy

### 2.1 Compatibility layer, not 50 rewrites

With ~50 scripts and ~1,600 widget instantiations, hand-crafting CTk layouts guarantees regressions.
Instead:

> **Keep the `placeWidget(...)` signature and the row-counter idiom every GUI uses, but reimplement it
> (and the widget constructors) inside the shared modules.** GUI scripts then need only mechanical,
> greppable edits.

**`src/GUI_theme_util.py`** owns: (1) CTk setup — appearance mode, theme (§0), widget-scaling;
(2) factory wrappers so scripts stop calling `tk.Button(...)` directly (`create_button`,
`create_open_file_button`, `create_checkbox`, `create_label`, `create_entry`, `create_option_menu`,
`create_combobox`, `create_slider`, `create_textbox`) — each takes *old tk-style args* (char-based
`width=`, etc.) and translates them; (3) a real `ToolTip` class replacing `hover_over_widget`.

Shared functions are rewritten in place: `GUI_util.window` → `customtkinter.CTk()` (same singleton);
`placeWidget` keeps its signature but maps onto `grid()`; `GUI_top`/`GUI_bottom`/`place_help_button`
rebuilt on the new layout. Because all 50 GUIs funnel through these, most visual change lands in two files.

### 2.2 Layout: absolute pixels → semantic grid

The old system already *is* a grid: `y_multiplier_integer` is a row counter, the x-constants cluster into
columns.

| Grid column | Replaces | Content |
|---|---|---|
| 0 | `help_button_x_coordinate` | `?` HELP button |
| 1 | `labels_x_coordinate`, `labels_x_indented_coordinate` (as `padx`) | labels, checkboxes |
| 2 | `entry_box_x_coordinate` | entries, dropdowns, file paths |
| 3–6 | per-GUI ad-hoc constants | trailing small buttons (`+`, `Reset`, `Show`, open-file) |

`placeWidget` translation: `y_multiplier_integer` → `row=`; `sameY=True` → same row, next free column;
`x_coordinate` → nearest semantic column via lookup (old constants keep working *unedited*); `y_step=40`
→ `pady` + natural height; `centerX=True` → `columnspan` + `sticky=''`. The body lives in a
**`CTkScrollableFrame`**, fixing "GUI taller than the screen".

Two load-bearing grid helpers: **`_column_for(row, x)`** bumps a widget to the next free column if its
band is taken (so two widgets never stack in one cell); **`apply_row_spans(window)`** lets each widget
span to the next occupied column on its row (grid columns are shared by *all* rows, so one long label
alone on a row inflated the columns dense rows use — spanning restores pre-grid semantics). Called once
per GUI by `GUI_bottom`. Raw `.place()` calls bypassing the helper are converted by hand (Phase 4).

### 2.3 Deliberately NOT changed

Out of scope: the module-level `tk.Tk()`-at-import architecture and top-level script style; the
`StringVar`/`IntVar` + `.trace('w', …)` pattern (CTk accepts the same `variable=`/`textvariable=`
objects — optionally modernize `.trace('w')` → `.trace_add('write')` in files touched anyway, never as a
standalone sweep); the subprocess-per-GUI launch model; any `run()` logic, config formats, or I/O
behavior; `tk.Menu` menu bars (CTk cannot theme native menus).

---

## 3. Widget mapping table

| Today | Becomes | Notes / gotchas |
|---|---|---|
| `tk.Tk()` | `customtkinter.CTk()` | One place: `GUI_util.py:17`. |
| `tk.Toplevel` | `CTkToplevel` | Popups: `enter_value_widget`, `message_box_widget`, sliders. Children still accept `.pack()`. |
| `tk.Label` | `CTkLabel` | `foreground=` → `text_color=`. **Bound labels must go through `create_label`** (§6). |
| `tk.Button` | `CTkButton` | **`width` is pixels, not chars** — wrapper multiplies char widths by ~8 px. |
| `tk.Button(width=1, text='')` (open-file sliver) | `create_open_file_button` | 📂 glyph at 32 px. See `docs/ctk_empty_button_status.md`. |
| `tk.Checkbutton` | `CTkCheckBox` | Same `variable=`/`onvalue=`/`offvalue=`/`command=`. `trace_checkbox` label-swap works via `.configure(text=…)`. |
| `tk.Entry` | `CTkEntry` | **`width` in pixels** + 14 px chrome the factory adds. `placeholder_text` for hints. |
| `tk.OptionMenu` (200) | `CTkOptionMenu` | Dynamic items: `menu = w["menu"]; menu.delete(...)` → `set_values(w, values)`. **Grep `["menu"]`.** Numeric choices → strings. |
| `ttk.Combobox` (56) | `CTkComboBox` | `w['values'] = …` → `set_values(...)`; **`textvariable=` → `variable=`** (`create_combobox` renames). No `<<ComboboxSelected>>` — use `command=`. |
| `tk.Scale` (9) | `CTkSlider` | No value label (wrapper adds one). `.get()` returns `float` — use `integer=True`. |
| `tk.Text` / scrolled text | `CTkTextbox` | Built-in scrollbar; drop manual `tk.Scrollbar` pairs. |
| `tk.Frame` / `ttk.Frame` | `CTkFrame` | A `ttk.Frame` **cannot parent CTk children** — CTk reads bg off the master. |
| `ttk.Notebook` (1) | `CTkTabview` | `.add("name")` returns a frame. Single call site (`NLP_menu_main`), done. |
| `tk.Listbox` | keep, or `CTkScrollableFrame` of buttons | CTk has **no Listbox**. A styled `tk.Listbox` in a `CTkFrame` is acceptable. |
| `tkinter.messagebox` / `tk.filedialog` | **keep stdlib** | Native dialogs/pickers honor the OS. Don't add CTk clones. |
| `tkcolorpicker` (4 files) | keep initially | Works under a CTk root; delete its `ttk.Style(...)`/`theme_use('clam')` lines. |
| `ttk.Style` / `theme_use('clam')` (9) | **delete** | ttk styling fights CTk. |
| `tk.PhotoImage` via `tk_image_from_pil` | **keep as-is** | See §5.1. `CTkLabel` accepts a plain `PhotoImage` with a console warning. |
| `GUI_IO_util.hover_over_widget` | `GUI_theme_util.ToolTip` | Bind to the widget, not coordinates. `x_coordinate_hover_over` params accepted-and-ignored until Phase 5. |

**Appearance mode:** `set_appearance_mode("system")` + `set_default_color_theme(nlp_suite_theme.json)`.
Persist a user override via `config_util`; expose in the setup GUIs later.

---

## 4. Phases and PR breakdown

Each phase is one or more independently shippable PRs. **The suite must run at every merge point** — the
compat layer makes that possible, since CTk and tk widgets coexist under a `CTk` root.

### Phase 0 — Groundwork ✅

Pin `customtkinter==6.0.0` in `requirements.txt` **only**; ship `nlp_suite_theme.json` under `src/` with
an explicit PyInstaller datas entry; add `collect_data_files('customtkinter')` +
`customtkinter`/`darkdetect` hiddenimports to the spec. Bundle-risk work (`tests/ctk_bundle_smoke.py` +
`src/ctk_bundle_util.py`) landed first. ⏳ **Windows bundle smoke run still pending** (§5.1).

### Phase 1 — Shared framework ✅ (mostly)

- **PR 1** (#1641) — `GUI_theme_util` compat layer + Phase 0 groundwork.
- **Slice 2a** (#1645) — root → `CTk()`, shared-chrome factories, `GUI_top` intro widget; kept
  `.place()`. Added `create_open_file_button`.
- **Slice 2b** (#1648) — `placeWidget` → `grid()`; tooltips bind `ToolTip`.
- **Slice 3** (`ctk/phase1-popups`) — 4 of 5 popups → `CTkToplevel`: `slider_widget` (integer steps),
  `dropdown_menu_widget`/`2`, `enter_value_widget` (was a second bare `tk.Tk()` + `mainloop()`; now
  parented + `wait_window()`).
- **Accent-signal slice** — implemented cut 2, since superseded by cut 3 (§0); its `accent=`/`muted=`
  opt-ins remain in use.

> **Deferred to Phase 4** (both carry in-code markers): `message_box_widget` (buttons/countdown labels
> `.place()`d at offsets, fires every RUN — needs on-screen QA); `combobox_with_search_widget`
> (unfinished, only call site commented out).
> **Deferred, not blockers:** window geometry still tuned to the old layout; dead `hover_over_widget`
> machinery awaits Phase 5; per-GUI Mac+Windows / light+dark QA outstanding.

### Phase 2 — Pilot GUIs ✅ (2026-07-18)

Three pilots proved the recipe: **`wordclouds_main`** (checkbox label-tracing, dynamic OptionMenu,
disabled-state toggling, tkcolorpicker, Combobox), **`NLP_menu_main`** (front door; logo path, the
suite's only `ttk.Notebook`), **`NLP_setup_IO_main`** (config plumbing). **Every durable finding is now a
§6 checklist item.** Two findings worth keeping:

1. **`tests/gui_smoke.py` had stubbed `customtkinter` as a blanket `MagicMock`**, absorbing all three
   idiom bugs silently (wordclouds passed while broken, 0 widgets). Replaced with a hand-written stub
   reproducing the real contracts, pinned against real CTk in `tests/test_gui_theme_util.py`.
2. **Verify config-touching GUIs by equivalence, not by eye.** Pilot 3 drove the
   `get_IO_options_list`/`get_IO_options_str` round-trip across all checkbox states, byte-identical.
   Reuse for the remaining `NLP_setup_*` GUIs.

`NLP_setup_IO_main`'s `activate_fields()` now runs once after build (`warn=False`). **Outstanding:
Windows QA, and Roberto's call on §0.**

### Phase 3 — Batch conversion ✅ (fully complete except deferrals)

Per-file recipe: swap `tk.X(` → `create_x(`; convert `["menu"]` → `set_values(...)`; delete
`ttk.Style`/`theme_use`; run the GUI and walk §6; screenshot before/after. Every tranche below was
verified per §6 (`pytest` + `gui_smoke` clean, launched on macOS). **Windows QA outstanding on every
tranche.** Only *new* shared-layer gaps (each now a §6 item) and still-open items are listed.

| Tranche (branch) | Scope | New shared-layer gap | Still open / fixes |
|---|---|---|---|
| **`NLP_welcome_main`** (`ctk/welcome-gui`) | only hand-`grid()`ed GUI, last all-raw-tk | (1) pixel budget → char `width=` (`create_label(width_is_chars=False)`); (2) overlapping/phantom `columnspan`s; (3) `tk.Canvas` needs hand-painting (`background=window_bg()`, `highlightthickness=0`) | `KNOWN_SKIP` — verify by launching |
| **File tools** (`ctk/phase3-file-tools[-2]`) | 11 GUIs, ~116 ctors, 22 OptionMenus | `.configure(width=N)` post-construction bypasses factory → `set_char_width()` | `file_checker_pre_processing_pipeline` `KNOWN_SKIP`. Fixed: `file_classifier.run()` unset `startTime` NameError every RUN |
| **CoNLL tools** (`ctk/phase3-conll-tools`) | `parsers_annotators`, `CoNLL_table_analyzer`, `NER`, `coreference`, `sentence_analysis`, `syntactic_analysis_ALL`, `nominalization`, `SVO`; ~113 ctors | none | `CoNLL_table_analyzer_main` had all three silent idioms at once (worked example) |
| **Sentiment/annotator/semantic** (`ctk/phase3-sentiment-annotator`) | `sentiment_analysis`, `sentiments_emotions_ALL`, `shape_of_stories`, `html_annotator[_gender]`, `semantic_analysis`, `semantic_aggregation`; ~107 ctors | `tk.Scale.get()`→int but `CTkSlider.get()`→float (breaks at RUN, CoreNLP `-mx6.0g`) → `create_slider(integer=True)` | `gui_smoke` blindness: mid-import `sys.exit(0)` was `SMOKE_OK`, now `UNCOV` — exposed 11 GUIs with zero coverage. `semantic_aggregation_main` had four silent idioms at once |
| **GIS tools** (`ctk/phase3-gis-tools`) | `GIS_main`, `GIS_distance`, `GIS_symbolic`, `GIS_Google_Earth`; ~137 ctors (46 in Google_Earth) | none | `GIS_Google_Earth_main` overflows +388px + live §5.1 `ImageTk` icon preview (untouched, for bundle pass); `GIS_main` needs full Anaconda env to launch (**user verifying**). Fixed: `run()`-breaking `UnboundLocalError` in Google_Earth |
| **DB/SQL + PCACE** (`ctk/phase3-db-pcace`) | `DB_SQL_main`, `DB_PCACE_data_validation`, `DB_PCACE_data_analysis` (1663/1401/1915 lines); ~119 ctors, 17 Comboboxes, first `create_textbox`/`CTkToplevel` uses | (1) `create_textbox` silently dropped `state=` (CTkTextbox `**kwargs` catch-all) → pull `_valid_tk_text_attributes` out before filter; (2) `CTkComboBox` has no `<<ComboboxSelected>>` → move handler to `command=` | Overflow: validation **0** (was +59); analysis +297; **`DB_SQL_main` +167** → Phase 4 row-splitting. `DB_PCACE_data_validation` `UNCOV` |
| **Statistical/visualization** (`ctk/phase3-stats-viz`) | `topic_modeling`, `statistics_txt`, `style_analysis`, `word2vec`, `corpus_profiler`, `NGrams_CoOccurrences`; ~120 ctors, 15 OptionMenus | none | **`charts_Excel_main` deferred** (classic-Mac CR-only line endings). Fixed: `NGrams_CoOccurrences` `+K` entry bound to an x-coord expr, RUN always read `0`. `style_analysis` `UNCOV` |
| **Remaining setup GUIs** (`ctk/phase3-setup-gui`) | `NLP_setup_external_software`, `NLP_setup_package_language`; 37 ctors, 3 sliders | none | Overflow: external_software **0**; **`NLP_setup_package_language` +731** → Phase 4. Both `UNCOV`. Fixed in package_language: vestigial `.pack()` next to each of 3 `tk.Scale`s (GUI couldn't open); `changed_NLP_package_set_parsers()` recreated labels without destroying predecessors (+640px column); `parsers_display_area['text']` read → `.cget('text')`; two `['values'] = …` → `set_values` |
| **Final tranche — misc tools** (`ctk/phase3-remaining-tools`) | `SRL_main`, `sample_corpus_main`, `knowledge_graphs_DBpedia_YAGO_main`, `corpus_checker_PCACE_data_main`, `data_manipulation_main`, `statistics_csv_main` — 6 GUIs never in an earlier tranche; ~90 ctors, first `int`/`float` `OptionMenu` choices converted | ⭐ **`CTkOptionMenu`/`CTkComboBox` crash outright on non-string `values=`** (date positions `1..5`, thresholds `.1..0.9`): CTk's `DropdownMenu._add_menu_commands` calls `value.ljust(...)` unconditionally, so a straight `values=[1,2,3]` port raises `AttributeError` on build (found via real-Tk+real-CTk, not `gui_smoke`) → `create_option_menu`/`create_combobox`/`set_values` now `str()`-coerce every item; `gui_smoke`'s fake CTk stub extended to raise the same way | Overflow: `data_manipulation_main` **+157**, `sample_corpus_main` **+419** → Phase 4. Last 3 empty open-file sites cleared — `ctk_empty_button_status.md` now empty. `data_manipulation_main`'s body sits behind `if __name__ == '__main__':` so `gui_smoke` reports 0 widgets; verified via `runpy.run_path(run_name='__main__')` (54 widgets). Other 5 verified clean under real Tk+CTk. **No `src/` GUI remains unconverted outside the Phase 4 hard cases.** |

### Phase 4 — Hard cases (1 PR each) ✅

- ✅ **`data_visualization_main.py`** (`ctk/phase4-data-visualization`, 2026-07-21) — last GUI still
  hand-`.place()`ing (~140 calls across a 7-tab `ttk.Notebook`). Notebook → **`CTkTabview`** (its
  `.add(name)` frames are real `CTkFrame`s, valid CTk masters, §3); every absolute-pixel row rebuilt as
  a grid row via two helpers, `tab_row(tab, i)` (a transparent `CTkFrame` in column 0 whose widgets pack
  left-to-right, keeping each row's columns independent — the §2.2 shared-column pitfall) and
  `tab_help(tab, i, msg)` (the per-row `? HELP` button). All ~126 ctors → factories; `changed_filename`
  repopulation (11 `["menu"]` + 10 `["values"]` writes, silent no-ops on CTk) → `set_values`; run
  dispatch's `notebook.index(notebook.select())` → a name→index map over `CTkTabview.get()`; deleted the
  notebook's `ttk.Style`/`theme_use` and two tkcolorpicker `ttk.Style`/`theme_use('clam')` lines; cleared
  2 empty open-file buttons. Verified under **real Tk+CTk** (stubbed `gui_smoke` can't measure geometry):
  no geometry-manager conflict, **overflow −10** (fits), `changed_filename` + tab dispatch exercised
  across all 7 tabs with a real csv. `pytest` + `gui_smoke` clean (126 widgets). **macOS launch + Windows
  QA outstanding.**
- ✅ **Row-splitting** for the overflow backlog (`ctk/phase4-row-splitting`, 2026-07-22): `DB_SQL_main`
  (+167→0), `NLP_setup_package_language` (+731→0), `DB_PCACE_data_analysis` (+297→0), `GIS_Google_Earth`
  (+276→0), `sample_corpus_main` (+419→**-10**), `data_manipulation_main` (+157→**-178**) — full
  before/after and the three new failure modes this surfaced (a `+.5` half-row nudge broken by Python's
  round-half-to-even; widgets recreated on every callback without destroying/reconfiguring the previous
  instance, leaking grid-column claims; a widget built after `GUI_bottom` already ran, missing
  `apply_row_spans`) are in `docs/ctk_GUI_overflow_status.md`. This was the item **deliberately deferred
  to run LAST** (user's call, 2026-07-22) — now done. Four GUIs outside this named backlog
  (`file_search_byWord_main`, `wordclouds_main`, `file_manager_main`, `SVO_main`; +191/+169/+103/+48 per
  the 2026-07-18 measurement) were left as a follow-up — closed below.
- ✅ **`narrative_analysis_ALL_main.py`**, **`license_GUI.py`**, **`charts_Excel_main.py`**
  (`ctk/phase4-remaining-hard-cases`, 2026-07-22) — the last three unconverted GUIs in `src/`.
  `charts_Excel_main.py` normalized first (pure-CR classic-Mac line endings, no `\n` in the file at
  all; converting to `\n` is a full-file diff but changes no bytes' meaning). All three follow the
  standard §6 recipe: `tk.Label/Entry/Button/Checkbutton` → factories; the 4 `tk.OptionMenu` sites
  (3 in `charts_Excel_main.py` fed from a dynamic `range()`/csv-headers list, 1 static) →
  `create_option_menu(values=[...])`; `charts_Excel_main.py`'s 3-site dynamic `widget["menu"]`
  repopulation (`changed_Excel_filename`) → `set_values(...)`; ~66 `.config(` → `.configure(`
  (`charts_Excel_main.py` alone); `.trace('w', …)` → `.trace_add('write', …)` throughout all three
  (heavily touched anyway). One dead vestige removed: `charts_Excel_main.py` had a masterless
  `column_yAxis_lb = tk.Label()` immediately shadowed 76 lines later by the real widget — deleted
  rather than converted (a `create_label()` call needs a `master` argument this line never had any
  use for). Verified: `pytest` 184 passed, `gui_smoke` 38 ok/0 crashed/0 missing golden (both
  `charts_Excel_main.py` and `narrative_analysis_ALL_main.py` show up `OK`; `license_GUI.py` isn't
  matched by `gui_smoke`'s `*_main.py` glob, so it was verified separately via
  `runpy.run_path(run_name='__main__')` under real Tk+CTk, 9 widgets, no crash) plus the same
  real-Tk+CTk harness exercised `narrative_analysis_ALL_main.py`'s "GUIs available" checkbox/dropdown
  gating and `charts_Excel_main.py`'s X/Y-axis cascading enable-disable chain and non-string
  `set_values` coercion, all correct. `ruff check` on all three: identical violation set before and
  after (16/79/27 pre-existing legacy hits respectively, e.g. `==True`/`==False` comparisons, unused
  locals) — confirms the conversion added zero new lint debt; per the legacy-backlog rule these were
  left alone rather than swept.
- ✅ **`message_box_widget` countdown timers, `combobox_with_search_widget`, Listbox sites**
  (`ctk/phase1-grid`, 2026-07-22) — the last named Phase 4 backlog item, closing the plan.
  `message_box_widget` (`GUI_IO_util.py`, fires on every RUN's Started/Finished notice via
  `IO_user_interface_util.timed_alert` — 97 call sites across the suite): `tk.Toplevel` →
  `CTkToplevel`, `tk.Message`/`Label`/`Button` → `create_label`/`create_button`; the pixel-offset
  `.place()` layout (computed from the packed `tk.Message`'s measured height, plus 5 Mac/Windows
  `countdownLabel*_X` constants) replaced by a plain grid — the button row now lays itself out, no
  height measurement or per-platform constants needed, so the 5 dead constants were deleted from both
  platform blocks in `GUI_IO_util.py` (confirmed single-use via grep first). All three button modes
  (OK / Yes-No / Yes-No-Cancel) exercised under real Tk+CTk by invoking each button programmatically
  (`gui_smoke`'s stub can't drive a modal `wait_window` loop) — correct return value each time.
  `combobox_with_search_widget` (`GUI_IO_util.py`) was a second, unfinished prototype (own
  `tk.Tk()`/`mainloop()`, `ttk.Combobox`) whose only reference anywhere in `src/` was already a
  commented-out line in `knowledge_graphs_main.py`, immediately followed by a live
  `create_combobox(...)` call doing the same job — deleted outright (function + the dead call-site
  comment) rather than reskinned, since nothing calls it. The one genuine Listbox site,
  `IO_files_util.select_path_from_list` (file-picker popup used by CoNLL/GIS/semantic_aggregation),
  kept its `tk.Listbox`/`tk.Scrollbar` per §3 (no CTk equivalent) but the surrounding chrome
  (`tk.Toplevel`/`Frame`/`Label`/`Button`) converted to `CTkToplevel`/`CTkFrame`/factories; the
  CTkFrame parents the plain-tk Listbox/Scrollbar without issue (`CTkFrame` is a real `tkinter.Frame`
  subclass). Verified end-to-end under real Tk+CTk (Select/Yes/Cancel button paths, `wait_window`
  round-trip). `pytest` 184 passed, `gui_smoke` unchanged (38 ok/0 crashed/0 missing golden;
  `knowledge_graphs_main.py` still builds, 19 widgets). `ruff check` on the three touched files:
  identical violation count before/after (106) — zero new lint debt.
- ✅ **Last four overflowing GUIs** (`ctk/phase1-grid`, 2026-07-22) — closes
  `docs/ctk_GUI_overflow_status.md`'s outstanding-overflow list (§8 acceptance criterion 4). Re-measured
  first, since the doc's 2026-07-18 numbers came from a different machine (font-metric drift shifts
  `reqwidth` by tens of px): `file_manager_main.py` and `SVO_main.py` already fit (0 overflow) with no
  code change; `file_search_byWord_main.py` (measured +79) and `wordclouds_main.py` (measured +57) still
  had the classic packed-row pattern (an `x+N`-offset chain / a set of per-GUI positioning constants each
  landing in its own unshared column) and were row-split the same way as the Phase 4 row-splitting
  backlog — down to **0** and **−32** respectively, 1 matching extra `?` HELP button each. Also measured
  `GIS_main.py` (previously un-measurable without a full Anaconda env, §5.5/below): **0**, 50 widgets, no
  collisions. **Every GUI in `src/` now fits at 0 or negative overflow.** Verified: `pytest` 184 passed,
  `gui_smoke` unchanged (38 ok/0 crashed/0 missing golden), the two split rows' enable/disable
  choreography and variable round-trips exercised under real Tk+CTk (correct), `ruff check` on both
  touched files identical before/after (57) — zero new lint debt.

### Phase 5 — Cleanup and polish (1–2 PRs)

Delete the dead x-coordinate constant blocks from `GUI_IO_util.py` (both platform branches) and the
ignored tooltip-coordinate params from `placeWidget` + all call sites (mechanical, once nothing reads
them). Add an appearance-mode toggle in the Setup GUI persisted via `config_util`. Refresh `docs/` and
wiki screenshots. Final packaging pass: rebuild installers on Mac + Windows, full bundle QA.

> **Build-pipeline note:** `.github/workflows/build-installers.yml` checks out `ref: roberto`, so Phase 0
> and Phase 5 spec/requirements changes must also reach `roberto` to affect installer builds.

---

## 5. Risks and mitigations

**5.1 ⚠️ `CTkImage` vs. the bundled portable Python (highest risk).** `CTkImage` goes through
`PIL.ImageTk`, which **crashes** under the shipped interpreter (§1.2). CTk *widgets* don't need ImageTk
(they draw with the canvas), but any code path handing CTk a `CTkImage` dies in the bundle while working
in a dev venv. **Phase 0 result (2026-07-15, macOS aarch64):** `tests/ctk_bundle_smoke.py` confirms CTk
core is fine but raw `CTkImage` fails as predicted. **Fix landed:** `patch_ctk_image_for_bundle()`
monkeypatches the two `CTkImage` methods that touch ImageTk to use the base64-PNG path — smoke green on
Mac. ⏳ **Windows run pending.** Call it **once at startup, before any `CTkImage`** (idempotent; raises
loudly if a CTk upgrade moves the methods). If bundle smoke ever fails for CTk itself, fall back to plain
tk in the bundle (runtime feature flag in `GUI_theme_util`: factories return tk widgets when CTk can't
initialize).

**5.2 Pixel-vs-character widths.** `tk.Entry(width=30)` = 30 chars; `CTkEntry(width=300)` = 300 px. ~380
`width=` sites. Factories translate (chars × ~8 px, tuned per class, + 14 px chrome on entries) so call
sites don't all need editing — but expect a tail of "too narrow" fixes, and watch the post-construction
`.configure(width=…)` variant (§6), which bypasses the factory.

**5.3 The tooltip/help system.** `hover_over_widget` positions from absolute coordinates, meaningless
under grid; the `ToolTip` class landed with the `placeWidget` rewrite. `text_info` strings must be
preserved **verbatim** — the suite's main in-app documentation.

**5.4 Disabled-state churn.** GUIs toggle `state='disabled'/'normal'` constantly. CTk supports
`configure(state=…)` on all mapped widgets, but *visual* feedback depends on `_StateFillMixin` (§0) —
verify each GUI's enable/disable choreography by eye, including its startup sync.

**5.5 Window geometry.** Every GUI calls `GUI_util.set_window(size, …)` with hard-coded `"WxH"` strings
tuned to the old layout. `_fit_window_to_content()` grows a GUI to fit, clamps at screen width, then
`_shrink_wide_fields_to_fit()` narrows wide entries. Per-GUI status: **`docs/ctk_GUI_overflow_status.md`**.

**5.6 Platform drift.** CTk draws its own widgets, so Mac/Windows metrics converge — but **every phase
must be smoke-tested on both**, because today's per-platform constants sometimes hide real behavioral
differences.

**5.7 Version pins.** `customtkinter==6.0.0` in `requirements.txt` only (§1.2, Phase 0). Its deps must
stay compatible with `Pillow==10.4.0`; they are, since CTk does not require Pillow ≥ 11.

---

## 6. Per-GUI conversion checklist (Phases 2–4)

For each `*_main.py` PR. **Starred items are silent failures — no exception, no visual cue.**

- [ ] All `tk.`/`ttk.` constructors replaced with `GUI_theme_util` factories (grep: `tk.Button(`,
      `tk.Checkbutton(`, `tk.Label(`, `tk.Entry(`, `tk.OptionMenu(`, `ttk.Combobox(`, `tk.Scale(`).
- [ ] **No `.config(` left** (grep `\.config\(` → `.configure(`). CTk's `config()` *only raises*. Highest
      volume — 53 sites in the first pilot.
- [ ] **No `widget['option']` reads left** (grep `\w\['`) — e.g. `menu['state']`. CTk resolves
      `__getitem__` against the tk frame → `TclError`. Use `widget.cget('option')`.
- [ ] ⭐ **No `widget['values'] = …` / `widget[k] = v` writes left.** tkinter's `__setitem__` →
      `configure({k: v})`, which lands the dict on CTk's first positional `require_redraw` — *silently
      does nothing*. Use `set_values(...)` / `widget.configure(k=v)`. **The `["menu"]` grep misses this.**
- [ ] ⭐ **No `textvariable=` left on a converted Combobox.** `CTkComboBox` has only `variable=`;
      `translate_kwargs` drops unknown kwargs silently → **no bound variable**, killing every `.trace`.
      `create_combobox` renames it; check combobox sites go through the factory.
- [ ] ⭐ **No `<<ComboboxSelected>>` bind on a converted Combobox.** `CTkComboBox` never fires it —
      permanent no-op. Move the handler to `command=` at construction.
- [ ] ⭐ **Labels bound to a variable go through `create_label`** (grep `tk.Label(.*textvariable`).
      `CTkLabel` forwards `textvariable` out of `**kwargs`, invisible to the signature filter — a raw
      call drops it and shows CTk's literal `"CTkLabel"` forever.
- [ ] ⭐ **No post-construction `.configure(width=…)` left** (grep `\.configure\(.*width=`). Bypasses the
      factory; CTk reads the number as **pixels**. Use `set_char_width(widget, chars)`.
- [ ] ⭐ **No `width=` fed from a PIXEL source through the char default** (grep `width=` for
      `get_GUI_width`, `winfo_*`, screen metrics). Factories multiply by ~8 px → ~8× oversized widget.
      Pass `width_is_chars=False` (`create_label`).
- [ ] ⭐ **`create_textbox` state:** `state=` is honored (fixed in DB/PCACE), but verify a textbox meant
      to start disabled actually does.
- [ ] ⭐ **`tk.Scale` over an integral range converted with `integer=True`** (grep `tk.Scale(`).
      `tk.Scale.get()` → `int`, `CTkSlider.get()` → `float`; a stray `6.0` breaks only at RUN (CoreNLP's
      `-mx6.0g`, float `n_clusters`). `create_slider(..., resolution=1, integer=True)`.
- [ ] ⭐ **`tk.OptionMenu`/Combobox numeric choices → strings** — CTk crashes on non-string `values=`
      (`value.ljust(...)`, Phase 3 final tranche). Factories `str()`-coerce; keep the bound `IntVar`.
- [ ] **No `.pack()` / `.place()` left on a widget `placeWidget` will grid** — mixing geometry managers
      raises `TclError` (`.pack`) or `ValueError` (`.place(width=…)`); `.place` also silently teleports
      to (0,0). Delete it. `gui_smoke` **cannot** catch this (its fake `tkinter` no-ops geometry).
- [ ] **No empty open-file buttons left** (grep `tk.Button(.*text=''`) — use `create_open_file_button`.
      Inventory: `docs/ctk_empty_button_status.md`.
- [ ] **No widget re-placed on top of one `GUI_top`/`GUI_bottom` already lays out.** Absolute layout hid
      the duplicate; grid renders it twice. Bind a `ToolTip` to the shared widget instead
      (`GUI_util.IO_path_labels` publishes the INPUT path labels).
- [ ] **Startup state sync:** any `activate_fields`-style routine must run once *after* build (under §0
      an un-synced widget is mislabeled as clickable). Suppress the user-facing warning on that first call.
- [ ] **Collapse dead `if x != v: OptionMenu(*x) else OptionMenu(x)` branches** — a placeholder that only
      ever holds one value makes both branches identical.
- [ ] No `["menu"]` OptionMenu manipulation left (grep `["menu"]`); no `ttk.Style`/`theme_use` left; no
      `ttk.Frame` parenting CTk children.
- [ ] No new `CTkImage`/`ImageTk` usage (grep). `tk.Canvas` kept? — set `background=window_bg()` +
      `highlightthickness=0`.
- [ ] GUI opens; scroll works; window resizes sanely; nothing overlaps or is clipped right (§5.5). Every
      `?` HELP button shows its text; hover tooltips appear on the right widgets.
- [ ] All enable/disable choreography works (toggle every gating checkbox/dropdown); dynamic dropdown
      repopulation works (select a csv input where applicable).
- [ ] **RUN executes with a known-good input**; output files open; Close exits cleanly
      (`NLP_SUITE_OPEN_WINDOWS` bookkeeping intact). Escape-key `clear` still resets bottom-bar dropdowns.
- [ ] If the GUI writes config, verify by **equivalence** against the pre-conversion file, not by eye.
- [ ] `pytest` and `python tests/gui_smoke.py` clean (0 crashed, 0 missing golden). **A GUI listed
      `UNCOV` was not smoke-tested at all** (exited during import) — verify by launching, or re-run with
      the exiting module stubbed to prove the widgets construct.
- [ ] Checked on macOS **and** Windows (dev venv), light **and** dark appearance.
- [ ] Before/after screenshots attached to the PR.

---

## 7. Estimated effort

| Phase | Size | Notes |
|---|---|---|
| 0 — groundwork + bundle smoke | 1–2 days | Smoke test is the long pole (both OSes). |
| 1 — shared framework | 1.5–2 weeks | Highest-skill work; everything depends on it. |
| 2 — pilots (3 GUIs) | 3–4 days | Includes refining wrappers + writing the recipe. |
| 3 — batch (~45 GUIs) | 3–4 weeks | ~0.5 day/GUI incl. two-OS QA; parallelizable once the recipe is stable. |
| 4 — hard cases | 1 week | `data_visualization_main.py` dominates. |
| 5 — cleanup/polish | 3–4 days | Mostly deletion + screenshots + installer rebuild. |

Total: roughly **6–8 calendar weeks** for one person, less wall-clock if Phase 3 tranches are farmed out.

---

## 8. Acceptance criteria

1. No file in `src/` instantiates a bare `tk.Button/Checkbutton/Label/Entry/OptionMenu` or `ttk.Combobox`
   outside the sanctioned exceptions (`Listbox`, menus, messagebox, filedialog, the logo label).
2. The platform-specific x-coordinate constant blocks in `GUI_IO_util.py` are deleted.
3. Every GUI passes §6 on macOS and Windows, light and dark, from a dev venv **and** the PyInstaller
   bundle.
4. ✅ `docs/ctk_GUI_overflow_status.md` and `docs/ctk_empty_button_status.md` are empty of open items
   (2026-07-22: last four overflowing GUIs closed; empty-button inventory cleared 2026-07-21).
5. Installers built from `roberto` ship and launch the CTk UI on clean machines.
