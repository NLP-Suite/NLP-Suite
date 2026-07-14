# CustomTkinter Migration Plan

**Goal:** migrate every NLP Suite GUI from plain `tkinter` to
[CustomTkinter](https://customtkinter.tomschimansky.com/) (CTk) so the suite gets a modern,
consistent, HiDPI-aware look (rounded themed widgets, light/dark appearance modes) and — just as
importantly — so we can retire the fragile absolute-pixel layout system that makes the current
GUIs look janky and break differently on Mac vs. Windows.

This document is the working plan: an audit of what exists today, the migration strategy, a
widget-by-widget mapping table, the phase breakdown with PR-sized chunks, known risks specific to
this codebase (there are several non-obvious ones, especially around PyInstaller), and a per-GUI
testing checklist.

---

## 1. Current state (audit)

Numbers below were measured on `current-stable` (July 2026).

| Fact | Value |
|---|---|
| Files in `src/` importing tkinter | **146** |
| GUI entry scripts (`*_main.py`, each a separate process) | **~50** |
| Shared GUI framework | `GUI_util.py` (1,683 lines) + `GUI_IO_util.py` (1,516 lines) |
| `tk.IntVar` / `tk.StringVar` instances | 386 / 377 |
| `tk.Label` / `tk.Checkbutton` / `tk.Button` / `tk.OptionMenu` / `tk.Entry` | 335 / 307 / 246 / 200 / 133 |
| `ttk.Combobox` / `ttk.Style` / `ttk.Frame` / `ttk.Notebook` | 56 / 9 / 7 / 1 |
| Raw `.place(x=…, y=…)` outside the helper (worst file: `data_visualization_main.py`) | 140 in that file alone |

### 1.1 How a GUI is built today

Every `*_main.py` follows the same recipe:

1. `import GUI_util` — **this creates the root window as a module-level side effect**
   (`window = tk.Tk()` at `GUI_util.py:17`). All widgets are parented to this singleton.
2. The script builds its widgets at module top level (no classes, no functions), using
   module-level `tk.StringVar`/`tk.IntVar` globals and `.trace('w', …)` callbacks for reactivity.
3. Widgets are positioned with `GUI_IO_util.placeWidget(window, x_coordinate,
   y_multiplier_integer, widget, …)`, which calls `.place(x=…, y=90 + 40*row)` — an absolute
   pixel grid with a hard-coded 40 px line height (`GUI_IO_util.py:318`).
4. The x-coordinates come from **hundreds of hard-coded, platform-specific constants** in
   `GUI_IO_util.py` — one whole block for `darwin`, a parallel block for Windows
   (`labels_x_coordinate`, `entry_box_x_coordinate`, per-GUI constants like
   `wordclouds_select_csv_field`, `SVO_1st_column`, …).
5. Shared chrome is added by `GUI_util.GUI_top(…)` (I/O configuration row) and
   `GUI_util.GUI_bottom(…)` (Read Me / videos / TIPS / reminders / Setup / RUN / Close row).
6. A column of `?` HELP buttons is placed down the left edge via
   `GUI_IO_util.place_help_button`, one per GUI row, positioned by the same row counter.
7. Hover-over tooltips are implemented by `GUI_IO_util.hover_over_widget` /
   `display_widget_info`, which reconstruct widget positions from the same absolute coordinates.
8. GUIs launch each other as **separate Python processes** via `run_script_util.run_script`,
   so each GUI owns its own `tk.Tk()` — there is no multi-window state to worry about.

### 1.2 Why it looks and feels janky

- Absolute pixel placement means nothing reflows: resize the window and widgets stay put;
  long labels overlap entry boxes; every Mac/Windows difference needs its own constant.
- Default `tk` widgets get the 1990s native look on Windows and an inconsistent mix on macOS.
- The 40 px row grid wastes vertical space and forces tall GUIs off-screen — there is a
  long-standing "scrollbar does not scroll" TODO comment block in `GUI_util.py:66-80`.
- No dark mode, no HiDPI scaling story.

### 1.3 Packaging constraints (critical — read before touching anything)

The suite ships as a PyInstaller bundle (`NLP_Suite.spec`) with a **portable
python-build-standalone interpreter** in `python-env/` for the subprocess-spawned GUIs. That
interpreter **statically embeds Tcl/Tk**, which means `PIL.ImageTk` **crashes** with
`invalid command name "PyImagingPhoto"`. The workaround already in the tree is
`GUI_util.tk_image_from_pil` (`GUI_util.py:192`), which feeds Tk base64-encoded PNG bytes
through the plain `tk.PhotoImage(data=…)` API, bypassing `_imagingtk` entirely.

**This matters because CTk's `CTkImage` uses `PIL.ImageTk` internally.** See §5.1.

Also: `Pillow` is pinned to `10.4.0` in `requirements.txt` because Pillow 12.x is incompatible
with the bundled Tcl/Tk 8.6 runtime. CustomTkinter (5.2.x) is compatible with that pin — its
only hard deps are `darkdetect` and `packaging`.

---

## 2. Migration strategy

### 2.1 The core decision: compatibility layer, not 50 rewrites

With ~50 GUI scripts and ~1,600 widget instantiations, editing every file into a hand-crafted
CTk layout is months of work and guarantees regressions. Instead:

> **Keep the `placeWidget(window, x_coordinate, y_multiplier_integer, widget, …)` call
> signature and the row-counter idiom that every GUI already uses, but reimplement it (and the
> widget constructors) inside the shared modules.** Individual GUI scripts then need only
> mechanical, greppable edits.

Concretely, we introduce one new shared module, **`src/GUI_theme_util.py`** (name open to
debate), that:

1. Owns `customtkinter` setup: appearance mode, the NLP Suite theme (accent red `#b10a0a`,
   the suite's brand color per the note at `GUI_util.py:188-190`), and widget-scaling defaults.
2. Exposes thin factory wrappers so GUI scripts stop calling `tk.Button(...)` directly:
   `create_button`, `create_checkbox`, `create_label`, `create_entry`, `create_option_menu`,
   `create_combobox`, `create_slider`, `create_textbox`. Each wrapper accepts the *old tk-style
   arguments* (e.g., character-based `width=`) and translates them to CTk equivalents
   (pixel-based `width=`), so call sites read almost unchanged.
3. Provides a real `ToolTip` class (bind on `<Enter>`/`<Leave>` of the widget itself) to
   replace the coordinate-based `hover_over_widget` machinery.

And we rewrite the internals of the existing shared functions in place:

- `GUI_util.window` becomes `customtkinter.CTk()` (same module-level singleton — changing the
  import-time side effect is a bigger refactor we explicitly do **not** attempt here).
- `GUI_IO_util.placeWidget` keeps its signature but maps onto **`grid()`** (see §2.2).
- `GUI_util.GUI_top` / `GUI_bottom` / `place_help_button` are rebuilt on the new layout.

Because all 50 GUIs funnel through these functions, most of the visual transformation lands in
two files.

### 2.2 Layout: from absolute pixels to a semantic grid

The old system already *is* a grid in disguise: `y_multiplier_integer` is a row counter, and the
x-coordinate constants cluster into a handful of columns. We formalize that:

| Grid column | Replaces constants | Content |
|---|---|---|
| 0 | `help_button_x_coordinate` | `?` HELP button |
| 1 | `labels_x_coordinate`, `labels_x_indented_coordinate` (as `padx` indent) | labels, checkboxes |
| 2 | `entry_box_x_coordinate` | entries, dropdowns, file paths |
| 3–6 | per-GUI ad-hoc constants (`wordclouds_add_button`, `reset_button`, …) | trailing small buttons (`+`, `Reset`, `Show`, open-file) |

`placeWidget`'s translation rules:

- `y_multiplier_integer` → `row=` (the `sameY=True` flag → same row, next free column).
- `x_coordinate` → nearest semantic column, resolved by comparing against the old column
  constants (a lookup table inside `placeWidget`; per-GUI oddball constants map to columns 3–6).
  GUI scripts that pass constants keep working *unedited* during the transition.
- Fixed `y_step = 40` → `pady=4` + natural widget height (CTk widgets are 28 px tall by
  default; rows become content-sized).
- `centerX=True` → `columnspan` + `sticky=''`.
- The whole body lives inside a **`CTkScrollableFrame`** as the content root, which finally
  fixes the "GUI taller than the screen" problem for the big GUIs (SVO, sentiment, GIS).

Raw `.place()` calls that bypass the helper (140 of them in `data_visualization_main.py`, a few
in `narrative_analysis_ALL_main.py`, `DB_SQL_main.py`, `license_GUI.py`) must be converted by
hand — they are called out in Phase 4.

### 2.3 What we deliberately do NOT change in this migration

Scope discipline is what makes this tractable. Out of scope:

- The module-level `tk.Tk()`-at-import architecture and top-level script style. Ugly, but
  orthogonal to the reskin; changing it would touch every line of every GUI.
- The `tk.StringVar`/`tk.IntVar` + `.trace('w', …)` reactivity pattern. CTk widgets accept the
  same `variable=`/`textvariable=` objects. (Optionally modernize `.trace('w')` →
  `.trace_add('write')` in files we touch anyway, since the old form is deprecated — but never
  as a standalone sweep.)
- The subprocess-per-GUI launch model (`run_script_util`).
- Any `run()` business logic, config-file formats, or I/O behavior.
- `tk.Menu` menu bars — CTk cannot theme native menus; they stay stock and that is fine.

---

## 3. Widget mapping table

| Today | Becomes | Notes / gotchas |
|---|---|---|
| `tk.Tk()` | `customtkinter.CTk()` | One place: `GUI_util.py:17`. |
| `tk.Toplevel` | `customtkinter.CTkToplevel` | Popups: `enter_value_widget`, `message_box_widget`, sliders. |
| `tk.Label` | `CTkLabel` | Drop `foreground=` → `text_color=`. |
| `tk.Button` | `CTkButton` | **`width` is pixels, not characters** — the factory wrapper multiplies char widths by ~8 px. `state='disabled'` works the same. |
| `tk.Checkbutton` | `CTkCheckBox` | Same `variable=`, `onvalue=`, `offvalue=`, `command=`. The `trace_checkbox` label-swapping helpers keep working via `.configure(text=…)`. Consider `CTkSwitch` for on/off toggles later — not in the mechanical pass. |
| `tk.Entry` | `CTkEntry` | **`width` in pixels.** `state='disabled'` supported; use `placeholder_text` where we currently pre-fill hint strings. |
| `tk.OptionMenu` (200 uses) | `CTkOptionMenu` | Different API for dynamic items: today code does `menu = widget["menu"]; menu.delete(0,"end"); menu.add_command(…)` (e.g., `wordclouds_main.py` `changed_filename`). CTk equivalent is `widget.configure(values=[…])`. The factory wrapper should expose a `set_values(widget, values)` helper and all dynamic-menu sites must be converted by hand — **grep for `["menu"]` to find them all.** |
| `ttk.Combobox` (56 uses) | `CTkComboBox` | Same idea; `widget['values'] = …` → `.configure(values=…)`. CTkComboBox is editable by default (matches Combobox). |
| `tk.Scale` (9 uses) | `CTkSlider` | CTkSlider has no built-in value label; the wrapper adds a small `CTkLabel` bound to the variable (the existing `slider_widget` popup already does this manually). |
| `tk.Text` / scrolled text areas | `CTkTextbox` | Built-in scrollbar; drop the manual `tk.Scrollbar` pairings. |
| `tk.Frame` / `ttk.Frame` | `CTkFrame` | |
| `ttk.Notebook` (1 use) | `CTkTabview` | Different API (`.add("name")` returns a frame); single call site. |
| `tk.Listbox` | keep, or `CTkScrollableFrame` of `CTkButton`s | CTk has **no Listbox**. Only used in shared helpers (`GUI_util.py`) — decide per call site; keeping a styled `tk.Listbox` inside a `CTkFrame` is acceptable. |
| `tkinter.messagebox` (`mb.show…`) | **keep stdlib** | Used everywhere; native dialogs are fine and honor the OS. Do not add a `CTkMessagebox` third-party dep in the mechanical pass. |
| `tk.filedialog` | **keep stdlib** | Native file pickers are better than any themed clone. |
| `tkcolorpicker` (4 files) | keep initially | Works under CTk root. Its `ttk.Style(window); style.theme_use('clam')` lines must be deleted (see below). Replace with a CTk-styled picker only as a later nicety. |
| `ttk.Style` / `theme_use('clam')` (9 uses) | **delete** | ttk styling fights CTk and is only there to make `tkcolorpicker`/Combobox look less broken. |
| `tk.PhotoImage` via `tk_image_from_pil` | **keep as-is** | Do NOT switch to `CTkImage` — see §5.1. `CTkLabel` accepts a plain `PhotoImage` with a console warning; if the warning is noisy, keep the logo on a plain `tk.Label` inside a `CTkFrame`. |
| `GUI_IO_util.hover_over_widget` | new `ToolTip` class | Bind to the widget, not to coordinates. Delete the `x_coordinate_hover_over` plumbing from `placeWidget` signature *last* (it is threaded through every call site as positional args — leave it accepted-and-ignored until Phase 5 cleanup). |

**Appearance mode:** start with `customtkinter.set_appearance_mode("system")` and
`set_default_color_theme(<path to nlp_suite_theme.json>)`. Persist a user override in the
existing config system (`config_util`) and expose it in `NLP_setup_*` GUIs later.

---

## 4. Phases and PR breakdown

Each phase is one or more independently shippable PRs against `current-stable`. **The suite must
run at every merge point** — the compat layer is what makes that possible: CTk and tk widgets
can coexist under a `CTk` root during the transition.

### Phase 0 — Groundwork (1 PR, small)

- Add `customtkinter==5.2.*` (+ transitive `darkdetect`) to `requirements.txt`,
  `requirements-mac.txt`, `requirements-windows.txt`, and the setup-app dependency probe
  (`setup-app` scans source imports — verify it picks up `customtkinter`).
- Add `nlp_suite_theme.json` (CTk color theme: accent `#b10a0a`, neutral grays) under
  `src/` or `config/` so PyInstaller ships it.
- PyInstaller: add `collect_data_files('customtkinter')` to `NLP_Suite.spec` datas and
  `darkdetect` to hiddenimports; same for `NetworkGraphViewer.spec` if it grows a CTk UI.
- **Bundle smoke test on both OSes before anything else lands** (see §5.1 — this is the
  make-or-break risk, so it goes first).

### Phase 1 — Shared framework (2–3 PRs, the heart of the migration)

1. `GUI_theme_util.py`: theme loading, factory wrappers, `ToolTip` class.
2. `GUI_util.py`: root window → `CTk()`; `GUI_top`, `GUI_bottom`,
   `display_about_release_team_cite_buttons`, logo display, `IO_config_setup_brief/full`
   rebuilt with wrappers + grid.
3. `GUI_IO_util.py`: `placeWidget` → grid translation (with the x-constant → column lookup);
   `place_help_button`; `message_box_widget`, `enter_value_widget`, `slider_widget`,
   `dropdown_menu_widget*`, `combobox_with_search_widget` popups → CTkToplevel + wrappers.

After Phase 1, **every GUI already looks substantially better** (new chrome, themed top/bottom
bars, help column, scrollable body) even though its own widgets are still plain tk.

### Phase 2 — Pilot GUIs (1 PR each)

Prove the mechanical conversion recipe end-to-end and refine the wrappers:

1. **`wordclouds_main.py`** — mid-complexity, exercises checkbox label-tracing, dynamic
   OptionMenu repopulation, disabled-state toggling, tkcolorpicker, Combobox.
2. **`NLP_menu_main.py`** — the front door; highest visual payoff, includes the logo path.
3. One setup GUI (**`NLP_setup_IO_main.py`**) — exercises the config plumbing.

Write down every deviation the pilots force into the per-file checklist (§6) before mass
conversion.

### Phase 3 — Batch conversion (~6–8 PRs, 5–8 GUIs each)

Mechanical per-file recipe (greppable, reviewable):

1. `tk.Button(` → `GUI_theme_util.create_button(` (etc. for the other widget classes).
2. Convert `["menu"]`-style OptionMenu manipulation → `set_values(...)`.
3. Delete `ttk.Style` / `theme_use` lines.
4. Run the GUI; walk the testing checklist; screenshot before/after for the PR.

Suggested tranches (group by shared quirks): file tools; CoNLL tools; sentiment/annotator
tools; GIS tools; DB/SQL + PCACE; statistical/visualization tools; remaining setup GUIs.

### Phase 4 — Hard cases (1 PR each)

- **`data_visualization_main.py`** — 140 raw `.place()` calls; needs a genuine re-layout.
- **`narrative_analysis_ALL_main.py`**, **`DB_SQL_main.py`**, **`license_GUI.py`** — few raw
  `.place()` calls each.
- `message_box_widget` countdown timers, `combobox_with_search_widget`, any Listbox sites.

### Phase 5 — Cleanup and polish (1–2 PRs)

- Delete the now-dead x-coordinate constant blocks from `GUI_IO_util.py` (both platform
  branches — several hundred lines) and the ignored tooltip-coordinate parameters from
  `placeWidget`'s signature and all call sites (mechanical sed once nothing reads them).
- Appearance-mode toggle in the Setup GUI, persisted via `config_util`.
- Refresh screenshots in `docs/` and the wiki.
- Final packaging pass: rebuild installers on Mac + Windows, full bundle QA.

> **Build-pipeline note:** `.github/workflows/build-installers.yml` checks out `ref: roberto`,
> so the Phase 0 and Phase 5 spec/requirements changes must also reach the `roberto` branch to
> affect installer builds.

---

## 5. Risks and mitigations

### 5.1 ⚠️ `CTkImage` vs. the bundled portable Python (highest risk)

CTk's `CTkImage` (and its HiDPI image handling) goes through `PIL.ImageTk`, which **crashes**
under the shipped python-build-standalone interpreter because its statically embedded Tcl/Tk
can't load `_imagingtk` (`invalid command name "PyImagingPhoto"` — the exact problem
`GUI_util.tk_image_from_pil` exists to solve). CustomTkinter's *widgets* don't require ImageTk
(they draw with the canvas), but any code path we write that hands CTk a `CTkImage` will die in
the bundle while working fine in a dev venv.

**Mitigations:**
- Phase 0 ships a trivial CTk "hello" window and we run it **inside the built bundle** on both
  OSes before committing to the migration.
- Rule for the whole migration: images go through `tk_image_from_pil` → plain `PhotoImage`,
  never `CTkImage`. Enforce with a grep in code review.
- If the bundle smoke test fails for CTk itself (e.g., its font/scaling probing), the fallback
  is to keep the bundled-app path on plain tk (runtime feature flag in `GUI_theme_util`:
  factories return tk widgets when CTk can't initialize) — the wrappers make this cheap.

### 5.2 Pixel-vs-character widths

`tk.Entry(width=30)` means 30 characters; `CTkEntry(width=300)` means 300 px. There are ~380
`width=` call sites. The factory wrappers translate (chars × ~8 px, tuned per widget class) so
call sites don't all need editing on day one — but expect a tail of "this entry is now too
narrow" fixes during Phase 3 QA.

### 5.3 The tooltip/help system

`hover_over_widget` positions its popup from the same absolute coordinates as `placeWidget`.
Once widgets are grid-managed those coordinates are meaningless. The `ToolTip` class must land
in the same PR as the `placeWidget` rewrite, and `text_info` strings must be preserved verbatim
— they are the suite's main in-app documentation.

### 5.4 Disabled-state churn

GUIs toggle `widget.config(state='disabled'/'normal')` constantly (see
`wordclouds_main.py`'s `activate_Python_options`). CTk supports `configure(state=…)` on all
mapped widgets, but disabled *visual* feedback differs; verify each pilot GUI's enable/disable
choreography by eye.

### 5.5 Window geometry

Every GUI calls `GUI_util.set_window(size, …)` with hard-coded `"WxH"` strings tuned to the old
absolute layout. With content-sized grid rows the right height changes. Plan: `set_window`
keeps accepting the old strings but treats them as *minimums*, and the scrollable content frame
absorbs the difference. Revisit per-GUI sizes only where obviously wrong.

### 5.6 Platform drift

The old system had separate Mac/Windows coordinate blocks because native widget metrics differ.
CTk draws its own widgets, so metrics converge — that's a win — but **every Phase must be
smoke-tested on both macOS and Windows**, because today's per-platform constants sometimes
hide real behavioral differences (e.g., different button texts fitting).

### 5.7 Version pins

Pin `customtkinter==5.2.2` (or latest 5.2.x at Phase 0 time) in all three requirements files.
Its deps must stay compatible with `Pillow==10.4.0` (they are — CTk does not require Pillow ≥11).

---

## 6. Per-GUI conversion checklist (used in Phases 2–4)

For each `*_main.py` PR:

- [ ] All `tk.`/`ttk.` widget constructors replaced with `GUI_theme_util` factories
      (grep: `tk.Button(`, `tk.Checkbutton(`, `tk.Label(`, `tk.Entry(`, `tk.OptionMenu(`,
      `ttk.Combobox(`, `tk.Scale(`, `tk.Text(`).
- [ ] No `["menu"]` OptionMenu manipulation left (grep `["menu"]`).
- [ ] No `ttk.Style`/`theme_use` left.
- [ ] No new `CTkImage`/`ImageTk` usage (grep).
- [ ] GUI opens; scroll works; window resizes sanely; nothing overlaps.
- [ ] Every `?` HELP button shows its text; hover tooltips appear on the right widgets.
- [ ] All enable/disable choreography works (toggle every checkbox/dropdown that gates others).
- [ ] Dynamic dropdown repopulation works (select a csv input where applicable).
- [ ] RUN executes with a known-good input; output files open; Close button exits cleanly
      (`NLP_SUITE_OPEN_WINDOWS` bookkeeping intact).
- [ ] Escape-key `clear` binding still resets the bottom-bar dropdowns.
- [ ] Checked on macOS **and** Windows (dev venv), light **and** dark appearance.
- [ ] Before/after screenshots attached to the PR.

---

## 7. Estimated effort

| Phase | Size | Notes |
|---|---|---|
| 0 — groundwork + bundle smoke test | 1–2 days | The smoke test is the long pole (needs both OSes). |
| 1 — shared framework | 1.5–2 weeks | Highest-skill work; everything else depends on it. |
| 2 — pilots (3 GUIs) | 3–4 days | Includes refining wrappers + writing the recipe. |
| 3 — batch (~45 GUIs) | 3–4 weeks | ~0.5 day/GUI including two-OS QA; parallelizable across contributors once the recipe is stable. |
| 4 — hard cases | 1 week | `data_visualization_main.py` dominates. |
| 5 — cleanup/polish | 3–4 days | Mostly deletion + screenshots + installer rebuild. |

Total: roughly **6–8 calendar weeks** for one person, substantially less wall-clock if Phase 3
tranches are farmed out — the whole design of the compat layer is to make Phase 3 safe for
contributors who don't know the framework internals.

---

## 8. Acceptance criteria

The migration is done when:

1. No file in `src/` instantiates a bare `tk.Button/Checkbutton/Label/Entry/OptionMenu` or
   `ttk.Combobox` outside the sanctioned exceptions (`Listbox`, menus, messagebox, filedialog,
   the logo label).
2. The platform-specific x-coordinate constant blocks in `GUI_IO_util.py` are deleted.
3. Every GUI passes the §6 checklist on macOS and Windows, in light and dark mode, both from a
   dev venv and from the PyInstaller bundle.
4. Installers built from `roberto` ship and launch the CTk UI on clean machines.
