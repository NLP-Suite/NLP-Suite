# CustomTkinter Migration Plan

**Goal:** migrate every NLP Suite GUI from plain `tkinter` to
[CustomTkinter](https://customtkinter.tomschimansky.com/) (CTk) — a modern, consistent, HiDPI-aware
look, and the retirement of the absolute-pixel layout system that makes the current GUIs look janky
and break differently on Mac vs. Windows.

**If you are converting a GUI, work from §3 (widget mapping) and §6 (checklist).** Everything else is
context.

---

## 0. Design premise: color is a signal, not styling

**Current rule** (cut 3, set on pilot 2, 2026-07-18) — ⚠️ *needs Roberto's sign-off before it goes
past pilot 2*:

- **Brand red `#b10a0a` = ENABLED.** Every interactive widget's default fill.
- **Flat grey = DISABLED.** Applied automatically whenever `state='disabled'` is set.

Color here is **information, not decoration** — that premise is fixed even though the encoding has
moved twice. `nlp_suite_theme.json` plus the `accent=`/`muted=` opt-ins in `GUI_theme_util` encode it.

### 0.1 Two reverted cuts

- **Cut 1 — solid red everywhere.** Reverted: it read as noise, and it **overwrote a load-bearing
  convention**. Red already means something here — a red *Open TIPS* / *videos* / *reminders*
  dropdown signals the resource *exists for this GUI* (the tooltips literally promise it). — *Roberto*
- **Cut 2 — neutral grey default, red for RUN + availability dropdowns.** Reverted: the mirror-image
  failure. With every ordinary control a filled mid-grey, **the whole GUI read as disabled**.

**Why cut 3 isn't just cut 1 again.** Roberto's objection (a) — the erased availability cue —
survives: a dropdown with nothing behind it *is* inactive, so it greys out; a red one still means "a
resource exists here". The old convention becomes a special case of the general rule. Objection (b) —
"the wall of red reads as noise" — is **not** answered: red is no longer salient, so RUN doesn't stand
out. A deliberate trade by Cora. Two one-liner fallbacks if Roberto prefers otherwise: flip the theme
JSON's fills back to neutral (cut 2), or to a light bordered surface (red border + text, solid red for
RUN/signal only).

### 0.2 What makes it work mechanically

CTk does *not* repaint on `state='disabled'` — it swaps `text_color_disabled` and leaves the fill
alone, so a disabled button would be indistinguishable from an enabled one.
`GUI_theme_util._StateFillMixin` closes the gap: it captures the enabled fill at construction and
repaints on every state change, at construction or via a later `configure(state=…)`. Call sites keep
using plain `configure(state=…)` unchanged — which matters, because the suite toggles disabled state
constantly (§5.4). It also restores a *call-site* color on re-enable.

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

1. `import GUI_util` — **creates the root window as a module-level side effect**
   (`window = tk.Tk()`, `GUI_util.py:17`). All widgets parent to this singleton.
2. Widgets are built at module top level (no classes, no functions), with module-level
   `tk.StringVar`/`IntVar` globals and `.trace('w', …)` callbacks for reactivity.
3. Positioned via `GUI_IO_util.placeWidget(window, x_coordinate, y_multiplier_integer, widget, …)` —
   an absolute pixel grid with a hard-coded 40 px line height.
4. X-coordinates come from **hundreds of hard-coded, platform-specific constants** in `GUI_IO_util.py`
   — one block for `darwin`, a parallel block for Windows.
5. Shared chrome from `GUI_util.GUI_top(…)` (I/O row) and `GUI_bottom(…)` (Read Me / videos / TIPS /
   reminders / Setup / RUN / Close).
6. A column of `?` HELP buttons down the left edge via `GUI_IO_util.place_help_button`.
7. Tooltips via `GUI_IO_util.hover_over_widget`, which reconstructs positions from the same coordinates.
8. GUIs launch each other as **separate processes** (`run_script_util.run_script`), so each owns its
   own root — no multi-window state to worry about.

### 1.2 Why it looks janky

Nothing reflows on resize; long labels overlap entry boxes; every Mac/Windows difference needs its own
constant. Default tk widgets look 1990s on Windows. The 40 px row grid forces tall GUIs off-screen
(there is a long-standing "scrollbar does not scroll" TODO at `GUI_util.py:66-80`). No dark mode, no
HiDPI story.

### 1.3 Packaging constraints (read before touching anything)

The suite ships as a PyInstaller bundle (`NLP_Suite.spec`) with a **portable
python-build-standalone interpreter** in `python-env/`. That interpreter **statically embeds Tcl/Tk**,
so `PIL.ImageTk` **crashes** with `invalid command name "PyImagingPhoto"`. The in-tree workaround is
`GUI_util.tk_image_from_pil` (`GUI_util.py:192`), which feeds Tk base64-encoded PNG bytes through
plain `tk.PhotoImage(data=…)`, bypassing `_imagingtk`. **CTk's `CTkImage` uses `PIL.ImageTk`
internally** — see §5.1.

`Pillow` is pinned to `10.4.0` (Pillow 12.x is incompatible with the bundled Tcl/Tk 8.6). CTk is
compatible with that pin; its only hard dep is `darkdetect`.

> **Version note:** the suite pins **`customtkinter==6.0.0`**, not the `5.2.x` this document first
> assumed. All wrapper work targets the **6.0.0** API (e.g. `CTkLabel` has no `justify`; `CTkEntry`
> has neither `justify` nor `anchor`). `GUI_theme_util.translate_kwargs` filters kwargs against each
> CTk class's real 6.0.0 signature, so this stays correct if the pin moves.

---

## 2. Migration strategy

### 2.1 Compatibility layer, not 50 rewrites

With ~50 GUI scripts and ~1,600 widget instantiations, hand-crafting CTk layouts is months of work and
guarantees regressions. Instead:

> **Keep the `placeWidget(...)` call signature and the row-counter idiom every GUI already uses, but
> reimplement it (and the widget constructors) inside the shared modules.** Individual GUI scripts
> then need only mechanical, greppable edits.

**`src/GUI_theme_util.py`** owns:

1. CTk setup — appearance mode, the NLP Suite theme (§0), widget-scaling defaults.
2. Factory wrappers so GUI scripts stop calling `tk.Button(...)` directly: `create_button`,
   `create_open_file_button`, `create_checkbox`, `create_label`, `create_entry`,
   `create_option_menu`, `create_combobox`, `create_slider`, `create_textbox`. Each accepts the *old
   tk-style arguments* (e.g. character-based `width=`) and translates them, so call sites read almost
   unchanged.
3. A real `ToolTip` class (bound to `<Enter>`/`<Leave>` on the widget) replacing the coordinate-based
   `hover_over_widget` machinery.

And the existing shared functions are rewritten in place: `GUI_util.window` → `customtkinter.CTk()`
(same module-level singleton — changing the import-time side effect is explicitly out of scope);
`GUI_IO_util.placeWidget` keeps its signature but maps onto `grid()`; `GUI_top` / `GUI_bottom` /
`place_help_button` rebuilt on the new layout.

Because all 50 GUIs funnel through these, most of the visual change lands in two files.

### 2.2 Layout: absolute pixels → semantic grid

The old system already *is* a grid in disguise: `y_multiplier_integer` is a row counter and the
x-constants cluster into a few columns.

| Grid column | Replaces | Content |
|---|---|---|
| 0 | `help_button_x_coordinate` | `?` HELP button |
| 1 | `labels_x_coordinate`, `labels_x_indented_coordinate` (as `padx`) | labels, checkboxes |
| 2 | `entry_box_x_coordinate` | entries, dropdowns, file paths |
| 3–6 | per-GUI ad-hoc constants | trailing small buttons (`+`, `Reset`, `Show`, open-file) |

`placeWidget` translation rules: `y_multiplier_integer` → `row=` (`sameY=True` → same row, next free
column); `x_coordinate` → nearest semantic column via a lookup table, so GUI scripts passing the old
constants keep working *unedited*; fixed `y_step=40` → `pady` + natural widget height;
`centerX=True` → `columnspan` + `sticky=''`. The body lives inside a **`CTkScrollableFrame`**, which
finally fixes "GUI taller than the screen".

Two grid-specific helpers that turned out to be load-bearing:

- **`_column_for(row, x)`** bumps a widget right to the next free column if its band is taken, so two
  widgets never stack in one cell.
- **`apply_row_spans(window)`** lets each widget span from its column to the next occupied one on its
  row. Grid columns are shared by *all* rows, so one long label alone on its row was inflating the
  columns that dense option rows also use, pushing them off the right edge. Spanning restores the
  pre-grid semantics — on `wordclouds_main` it took requested width from 2183 px to 1496 px. Called
  once per GUI by `GUI_bottom`.

Raw `.place()` calls that bypass the helper must be converted by hand — see Phase 4.

### 2.3 Deliberately NOT changed

Scope discipline is what makes this tractable. Out of scope: the module-level `tk.Tk()`-at-import
architecture and top-level script style; the `StringVar`/`IntVar` + `.trace('w', …)` reactivity
pattern (CTk accepts the same `variable=`/`textvariable=` objects — optionally modernize `.trace('w')`
→ `.trace_add('write')` in files touched anyway, never as a standalone sweep); the subprocess-per-GUI
launch model; any `run()` logic, config formats, or I/O behavior; `tk.Menu` menu bars (CTk cannot
theme native menus — they stay stock, and that is fine).

---

## 3. Widget mapping table

| Today | Becomes | Notes / gotchas |
|---|---|---|
| `tk.Tk()` | `customtkinter.CTk()` | One place: `GUI_util.py:17`. |
| `tk.Toplevel` | `CTkToplevel` | Popups: `enter_value_widget`, `message_box_widget`, sliders. |
| `tk.Label` | `CTkLabel` | `foreground=` → `text_color=`. **Bound labels must go through `create_label`** — see §6. |
| `tk.Button` | `CTkButton` | **`width` is pixels, not characters** — the wrapper multiplies char widths by ~8 px. |
| `tk.Button(width=1, text='')` (open-file sliver) | `create_open_file_button` | Renders a 📂 glyph at 32 px. See `docs/ctk_empty_button_status.md`. |
| `tk.Checkbutton` | `CTkCheckBox` | Same `variable=`/`onvalue=`/`offvalue=`/`command=`. `trace_checkbox` label-swapping keeps working via `.configure(text=…)`. |
| `tk.Entry` | `CTkEntry` | **`width` in pixels**, plus a 14 px chrome allowance the factory adds. Use `placeholder_text` where hint strings are pre-filled today. |
| `tk.OptionMenu` (200) | `CTkOptionMenu` | Dynamic items differ: `menu = w["menu"]; menu.delete(...)` → `GUI_theme_util.set_values(w, values)`. **Grep `["menu"]`.** Numeric choices must become strings. |
| `ttk.Combobox` (56) | `CTkComboBox` | `w['values'] = …` → `set_values(...)`; **`textvariable=` → `variable=`** (`create_combobox` renames it). |
| `tk.Scale` (9) | `CTkSlider` | No built-in value label; the wrapper adds a `CTkLabel` bound to the variable. |
| `tk.Text` / scrolled text | `CTkTextbox` | Built-in scrollbar; drop the manual `tk.Scrollbar` pairings. |
| `tk.Frame` / `ttk.Frame` | `CTkFrame` | A `ttk.Frame` **cannot parent CTk children** — CTk reads its background off the master. |
| `ttk.Notebook` (1) | `CTkTabview` | `.add("name")` returns a frame. Single call site (`NLP_menu_main`), done. |
| `tk.Listbox` | keep, or `CTkScrollableFrame` of buttons | CTk has **no Listbox**. Only in shared helpers; a styled `tk.Listbox` in a `CTkFrame` is acceptable. |
| `tkinter.messagebox` | **keep stdlib** | Native dialogs honor the OS. Do not add a `CTkMessagebox` dep. |
| `tk.filedialog` | **keep stdlib** | Native pickers beat any themed clone. |
| `tkcolorpicker` (4 files) | keep initially | Works under a CTk root; delete its `ttk.Style(...)`/`theme_use('clam')` lines. |
| `ttk.Style` / `theme_use('clam')` (9) | **delete** | ttk styling fights CTk. |
| `tk.PhotoImage` via `tk_image_from_pil` | **keep as-is** | See §5.1. `CTkLabel` accepts a plain `PhotoImage` with a console warning. |
| `GUI_IO_util.hover_over_widget` | `GUI_theme_util.ToolTip` | Bind to the widget, not coordinates. Leave the `x_coordinate_hover_over` params accepted-and-ignored until Phase 5. |

**Appearance mode:** `set_appearance_mode("system")` + `set_default_color_theme(nlp_suite_theme.json)`.
Persist a user override via `config_util` and expose it in the setup GUIs later.

---

## 4. Phases and PR breakdown

Each phase is one or more independently shippable PRs. **The suite must run at every merge point** —
the compat layer makes that possible, since CTk and tk widgets coexist under a `CTk` root.

### Phase 0 — Groundwork ✅

Pin `customtkinter==6.0.0` in `requirements.txt` **only** (the per-OS files install *in addition*, so
adding it to all three double-installs); ship `nlp_suite_theme.json` under `src/` with an explicit
PyInstaller datas entry (the spec's `src` collection is `.py`-only); add
`collect_data_files('customtkinter')` + `customtkinter`/`darkdetect` hiddenimports to the spec.

> **Status:** the *bundle risk* work landed first (`19e490f2`, `24554889`:
> `tests/ctk_bundle_smoke.py` + `src/ctk_bundle_util.py`). The remaining groundwork folded into
> Phase 1 PR 1, the first thing to actually `import customtkinter`.
> ⏳ **Windows bundle smoke run still pending** before Phase 0 is fully signed off (§5.1).

### Phase 1 — Shared framework ✅ (mostly)

> - **PR 1** (#1641) — `GUI_theme_util` compat layer + Phase 0 groundwork.
> - **Slice 2a** (#1645) — root → `CTk()`, shared-chrome factory conversions, `GUI_top` intro widget;
>   kept `.place()`. Added `create_open_file_button` and a tightened logo column.
> - **Slice 2b** (#1648) — `placeWidget` → `grid()`; tooltips bind `ToolTip`. Cleared the front-door
>   GUI's reflow artifacts and the `IO_config_setup_brief()` duplicate-INPUT-box overflow.
> - **Slice 3** (`ctk/phase1-popups`) — 4 of 5 popups → `CTkToplevel`: `slider_widget` (integer steps,
>   returns `int` to match `tk.Scale`), `dropdown_menu_widget`/`2`, `enter_value_widget` (was a second
>   bare `tk.Tk()` with its own `mainloop()`; now parented to `GUI_util.window` + `wait_window()`).
> - **Accent-signal slice** — implemented cut 2, since superseded by cut 3 (§0.1). Its
>   `accent=`/`muted=` opt-ins remain in use.
>
> **Deferred to Phase 4** (both carry an in-code marker): `message_box_widget` — its buttons and
> countdown labels are `.place()`d at offsets computed from the packed `tk.Message`'s height and it
> fires on every RUN, so the geometry needs on-screen QA — and `combobox_with_search_widget`, which is
> unfinished with its only call site commented out.
>
> **Deferred, not blockers:** window geometry is still tuned to the old absolute layout (revisit
> `set_window` sizing); the dead `hover_over_widget` machinery awaits Phase 5; per-GUI visual QA on
> Mac + Windows, light + dark, is outstanding throughout.

### Phase 2 — Pilot GUIs ✅ (complete 2026-07-18)

Three pilots proved the recipe: **`wordclouds_main`** (mid-complexity: checkbox label-tracing, dynamic
OptionMenu, disabled-state toggling, tkcolorpicker, Combobox), **`NLP_menu_main`** (the front door;
highest visual payoff, the logo path, the suite's only `ttk.Notebook`), and **`NLP_setup_IO_main`**
(the config plumbing).

**Every durable finding is now a §6 checklist item.** Each pilot added at least one *silent-failure*
item to it — the three legacy idioms CTk rejects (`.config(`, `widget['state']`,
`widget['values'] = …`), the `textvariable=`-dropped-by-`CTkComboBox` trap, the
`create_label(textvariable=…)` trap, and the "widget re-placed on top of shared chrome" duplicate.
Two findings worth keeping outside the checklist:

1. **`tests/gui_smoke.py` stubbed `customtkinter` as a blanket `MagicMock`**, which answers every call
   and subscript and so absorbed *all three* idiom bugs silently — wordclouds passed a smoke run while
   broken, recording **0 widgets**. Replaced with a hand-written stub reproducing the real contracts,
   pinned against real CTk in `tests/test_gui_theme_util.py` so a CTk upgrade can't drift them apart.
   **This is a prerequisite for trusting Phase 3**, not a nicety.
2. **Verify config-touching GUIs by equivalence, not by eye.** Pilot 3 drove the
   `get_IO_options_list` / `get_IO_options_str` round-trip across all checkbox states against the
   pre-conversion file, byte-identical. **Reuse this for the remaining `NLP_setup_*` GUIs** — a widget
   swap that quietly changes what lands in a config file is invisible on screen.

One deliberate behavior change: `NLP_setup_IO_main`'s `activate_fields()` was never called at startup
(the call sat commented out), so date widgets began life *visually* enabled. Harmless under stock tk;
under §0's rule the GUI was lying about what is clickable. Now called once after build, with
`warn=False`.

**Outstanding: Windows QA, and Roberto's call on §0.**

### Phase 3 — Batch conversion (~6–8 PRs, 5–8 GUIs each)

Per-file recipe: swap `tk.X(` → `GUI_theme_util.create_x(`; convert `["menu"]` manipulation →
`set_values(...)`; delete `ttk.Style`/`theme_use`; run the GUI and walk §6; screenshot before/after.

Tranches group by shared quirks: file tools ✅; CoNLL tools ✅; sentiment/annotator tools; GIS tools;
DB/SQL + PCACE; statistical/visualization tools; remaining setup GUIs.

> **✅ File tools (2026-07-18, `ctk/phase3-file-tools` + `-2`)** — all 11 file GUIs. ~116 constructors
> → factories, 22 `tk.OptionMenu` → `create_option_menu`. The recipe held; the tranche surfaced **one
> new shared-layer gap** and **two pre-existing bugs**:
>
> 1. **`.configure(width=N)` after construction bypasses the factory** and CTk reads N as *pixels* — a
>    `width=2` dropdown became a 2 px sliver, a 60-char entry 60 px. Silent. New
>    `GUI_theme_util.set_char_width()` + a §6 item. 11 sites across `file_manager`, `file_splitter`,
>    `file_search_byWord`.
> 2. `file_classifier_main.run()` referenced an unset `startTime` — **every RUN ended in a
>    `NameError`**. Found only because §6 demands an actual RUN.
> 3. `file_classifier`'s similarity-index dropdown listed `0.45`/`0.5` twice.
>
> Note `file_checker_pre_processing_pipeline` is in `gui_smoke`'s `KNOWN_SKIP` — verify by launching.
>
> **✅ CoNLL tools (2026-07-18, `ctk/phase3-conll-tools`)** — `parsers_annotators`,
> `CoNLL_table_analyzer`, `NER`, `coreference`, `sentence_analysis`, `syntactic_analysis_ALL`,
> `nominalization`, `SVO`. ~113 constructors → factories, 6 OptionMenus, 4 Comboboxes. No new bug
> classes: every non-mechanical edit was one of the already-known shared-layer patterns.
> `CoNLL_table_analyzer_main.py` had **all three at once** — worth reading as the worked example.
> `parsers_annotators_main.py` also had a `try: lb.config(...) except NameError: lb = tk.Label(...)`
> lazy-init pattern, preserved as-is in factory form.
>
> Verified per tranche: `pytest` (56 passed), `gui_smoke.py` (48 ok / 0 missing golden). The one
> `gui_smoke` crash, `topic_modeling_main.py`, is a pre-existing missing `pdfminer` import, untouched.
> All files launched on macOS. **Windows QA outstanding on every tranche.**

### Phase 4 — Hard cases (1 PR each)

- **`data_visualization_main.py`** — 140 raw `.place()` calls; needs a genuine re-layout.
- **`narrative_analysis_ALL_main.py`**, **`DB_SQL_main.py`**, **`license_GUI.py`** — a few each.
- `message_box_widget` countdown timers, `combobox_with_search_widget`, any Listbox sites.

### Phase 5 — Cleanup and polish (1–2 PRs)

Delete the dead x-coordinate constant blocks from `GUI_IO_util.py` (both platform branches, several
hundred lines) and the ignored tooltip-coordinate parameters from `placeWidget` and all call sites
(mechanical, once nothing reads them). Add an appearance-mode toggle in the Setup GUI persisted via
`config_util`. Refresh `docs/` and wiki screenshots. Final packaging pass: rebuild installers on Mac +
Windows, full bundle QA.

> **Build-pipeline note:** `.github/workflows/build-installers.yml` checks out `ref: roberto`, so the
> Phase 0 and Phase 5 spec/requirements changes must also reach `roberto` to affect installer builds.

---

## 5. Risks and mitigations

### 5.1 ⚠️ `CTkImage` vs. the bundled portable Python (highest risk)

`CTkImage` goes through `PIL.ImageTk`, which **crashes** under the shipped python-build-standalone
interpreter (§1.3). CTk's *widgets* don't need ImageTk (they draw with the canvas), but any code path
handing CTk a `CTkImage` dies in the bundle while working fine in a dev venv.

**Phase 0 result (2026-07-15, macOS aarch64, cpython-3.10.15):** `tests/ctk_bundle_smoke.py` under the
bundled interpreter confirms CTk core is fine, but **raw `CTkImage` fails exactly as predicted**
(`TypeError: bad argument type for built-in operation` from `PIL.ImageTk`). **Fix landed:**
`ctk_bundle_util.patch_ctk_image_for_bundle()` monkeypatches the two `CTkImage` methods that touch
ImageTk to build their Tk image through the same base64-PNG path as `tk_image_from_pil`. With the
patch the smoke test is **green on Mac**. ⏳ **Still pending: the same run on Windows.**

- Call `patch_ctk_image_for_bundle()` **once at startup, before any `CTkImage`**. Idempotent; raises
  loudly if a CTk upgrade moves the patched methods. This supersedes the earlier "never use
  `CTkImage`" rule.
- If the bundle smoke test ever fails for CTk itself, the fallback is to keep the bundled path on
  plain tk (runtime feature flag in `GUI_theme_util`: factories return tk widgets when CTk can't
  initialize) — the wrappers make this cheap.

### 5.2 Pixel-vs-character widths

`tk.Entry(width=30)` means 30 characters; `CTkEntry(width=300)` means 300 px. ~380 `width=` call sites.
The factories translate (chars × ~8 px, tuned per class, plus a 14 px chrome allowance on entries) so
call sites don't all need editing — but expect a tail of "this entry is now too narrow" fixes, and
watch for the post-construction `.configure(width=…)` variant (§6), which bypasses the factory.

### 5.3 The tooltip/help system

`hover_over_widget` positions from the same absolute coordinates as `placeWidget`, meaningless under
grid. The `ToolTip` class landed in the same PR as the `placeWidget` rewrite. `text_info` strings must
be preserved **verbatim** — they are the suite's main in-app documentation.

### 5.4 Disabled-state churn

GUIs toggle `state='disabled'/'normal'` constantly. CTk supports `configure(state=…)` on all mapped
widgets, but the *visual* feedback depends on `_StateFillMixin` (§0.2) — verify each GUI's
enable/disable choreography by eye, including its startup sync.

### 5.5 Window geometry

Every GUI calls `GUI_util.set_window(size, …)` with hard-coded `"WxH"` strings tuned to the old
layout. `_fit_window_to_content()` grows a GUI to fit, clamps at screen width, then
`_shrink_wide_fields_to_fit()` narrows wide entries. Per-GUI status:
**`docs/ctk_GUI_overflow_status.md`**.

### 5.6 Platform drift

The old system had separate Mac/Windows coordinate blocks because native widget metrics differ. CTk
draws its own widgets, so metrics converge — a win — but **every phase must be smoke-tested on both
macOS and Windows**, because today's per-platform constants sometimes hide real behavioral differences.

### 5.7 Version pins

`customtkinter==6.0.0` in `requirements.txt` only — see §1.3 and Phase 0. Its deps must stay
compatible with `Pillow==10.4.0`; they are, since CTk does not require Pillow ≥ 11.

---

## 6. Per-GUI conversion checklist (Phases 2–4)

For each `*_main.py` PR. **The starred items are silent failures — no exception, no visual cue.**

- [ ] All `tk.`/`ttk.` widget constructors replaced with `GUI_theme_util` factories (grep:
      `tk.Button(`, `tk.Checkbutton(`, `tk.Label(`, `tk.Entry(`, `tk.OptionMenu(`, `ttk.Combobox(`,
      `tk.Scale(`).
- [ ] **No `.config(` left** (grep `\.config\(` → `.configure(`). CTk implements `config()` *only to
      raise* `AttributeError`. Highest-volume edit in a conversion — 53 sites in the first pilot alone.
- [ ] **No `widget['option']` reads left** (grep `\w\['`) — e.g. `menu['state']`. CTk resolves
      `__getitem__` against the underlying tk frame, which has no such option → `TclError`. Use
      `widget.cget('option')`.
- [ ] ⭐ **No `widget['values'] = …` / `widget[k] = v` writes left.** tkinter's `__setitem__` calls
      `configure({k: v})`, which lands the dict on CTk's **first positional parameter
      `require_redraw`** — so it *silently does nothing*. Use `GUI_theme_util.set_values(...)` /
      `widget.configure(k=v)`. **The `["menu"]` grep below does not catch this.**
- [ ] ⭐ **No `textvariable=` left on a converted Combobox.** `CTkComboBox` has only `variable=`, and
      `translate_kwargs` drops unknown kwargs silently — the widget renders fine with **no bound
      variable**, killing every `.trace` on it. `create_combobox` renames it; the check is that
      combobox sites go through the factory (grep `ttk.Combobox(`).
- [ ] ⭐ **Labels bound to a variable go through `create_label`** (grep `tk.Label(.*textvariable`).
      `CTkLabel` forwards `textvariable` out of `**kwargs`, so it is invisible to `translate_kwargs`'
      signature filter — a raw call drops it and the label displays CTk's literal `"CTkLabel"` forever.
- [ ] ⭐ **No post-construction `.configure(width=…)` left** (grep `\.configure\(.*width=`). The
      factories translate `width=` on the way in, but a legacy GUI often builds a widget bare and sizes
      it afterwards — that call bypasses the factory and CTk reads the number as **pixels**. Use
      `GUI_theme_util.set_char_width(widget, chars)`.
- [ ] **`tk.OptionMenu` int choices converted to strings** (grep `tk.OptionMenu(` for numeric varargs).
      `CTkOptionMenu` renders `values` as text and writes selections back as strings; the bound
      `IntVar` can stay as-is.
- [ ] **No empty open-file buttons left** (grep `tk.Button(.*text=''`) — use
      `create_open_file_button`. Inventory: `docs/ctk_empty_button_status.md`.
- [ ] **No widget re-placed on top of one `GUI_top`/`GUI_bottom` already lays out.** Several GUIs stack
      a duplicate on the shared chrome's widget to attach their own hover text — absolute layout hid
      it, the grid renders it twice. Bind a `ToolTip` to the shared widget instead
      (`GUI_util.IO_path_labels` publishes the INPUT path labels for exactly this).
- [ ] **Startup state sync:** if the GUI has an `activate_fields`-style enable/disable routine, it must
      run once *after* the widgets are built. Under §0's rule an un-synced widget is actively
      mislabeled as clickable. Suppress any user-facing warning on that first call.
- [ ] No `["menu"]` OptionMenu manipulation left (grep `["menu"]`).
- [ ] No `ttk.Style`/`theme_use` left; no `ttk.Frame` parenting CTk children.
- [ ] No new `CTkImage`/`ImageTk` usage (grep).
- [ ] GUI opens; scroll works; window resizes sanely; nothing overlaps; nothing clipped on the right
      (§5.5).
- [ ] Every `?` HELP button shows its text; hover tooltips appear on the right widgets.
- [ ] All enable/disable choreography works (toggle every checkbox/dropdown that gates others).
- [ ] Dynamic dropdown repopulation works (select a csv input where applicable).
- [ ] **RUN executes with a known-good input**; output files open; Close exits cleanly
      (`NLP_SUITE_OPEN_WINDOWS` bookkeeping intact).
- [ ] If the GUI writes config, verify by **equivalence** against the pre-conversion file, not by eye.
- [ ] Escape-key `clear` binding still resets the bottom-bar dropdowns.
- [ ] `pytest` and `python tests/gui_smoke.py` clean (0 missing golden labels).
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

Total: roughly **6–8 calendar weeks** for one person, substantially less wall-clock if Phase 3
tranches are farmed out — the whole design of the compat layer is to make Phase 3 safe for
contributors who don't know the framework internals.

---

## 8. Acceptance criteria

1. No file in `src/` instantiates a bare `tk.Button/Checkbutton/Label/Entry/OptionMenu` or
   `ttk.Combobox` outside the sanctioned exceptions (`Listbox`, menus, messagebox, filedialog, the
   logo label).
2. The platform-specific x-coordinate constant blocks in `GUI_IO_util.py` are deleted.
3. Every GUI passes §6 on macOS and Windows, light and dark, from a dev venv **and** the PyInstaller
   bundle.
4. `docs/ctk_GUI_overflow_status.md` and `docs/ctk_empty_button_status.md` are empty of open items.
5. Installers built from `roberto` ship and launch the CTk UI on clean machines.
