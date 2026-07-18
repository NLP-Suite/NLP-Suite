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

## 0. Design premise: color is a signal, not styling (read first)

**The current rule** (cut 3, set on pilot 2, 2026-07-18) — ⚠️ *needs Roberto's sign-off before it
goes past pilot 2*:

- **Brand red `#b10a0a` = ENABLED.** Every interactive widget's default fill.
- **Flat grey = DISABLED.** Applied automatically whenever `state='disabled'` is set.

Color here is **information, not decoration** — that premise is fixed even though the encoding has
moved twice. The theme JSON plus the `accent=`/`muted=` opt-ins in `GUI_theme_util` are what encode
it (§3).

### 0.1 How we got here — two reverted cuts

**Cut 1: solid red on every widget.** Shipped briefly, reverted. It read as noise, and more
fundamentally it **overwrote a load-bearing convention**: in this suite **red already means
something** — a red *Open TIPS* / *Watch videos* / *Open reminders* dropdown signals that the
resource *exists for this GUI*, grey means none is available (the in-app tooltips literally promise
"when TIPS are available the widget is red, otherwise black"). A blanket-red theme erases that
signal, and no amount of layout polish restores it. — *Roberto, 2026-07*

**Cut 2: neutral grey default, red reserved for RUN + the availability dropdowns.** Also shipped,
also reverted — the mirror-image failure. With every ordinary control a filled mid-grey, **the whole
GUI read as disabled**: grey is the universal "you can't click this" cue, and the neutral theme spent
it on the majority of live controls, so nothing looked actionable.

**Why cut 3 does not simply re-break cut 1.** Roberto's objection had two parts. Part (a), the erased
availability cue, survives intact: a TIPS / videos / reminders dropdown with nothing behind it *is*
an inactive control, so it greys out, and a red one still means "a resource exists here" — the old
convention becomes a special case of the general rule rather than a casualty of it. Part (b), "the
wall of red reads as noise", is **not** answered: red is no longer *salient*, so RUN and the
available dropdowns no longer stand out from ordinary buttons. That is a deliberate trade made by
Cora on the pilot. Two one-liner fallbacks if Roberto prefers otherwise: flip the theme JSON's fills
back to neutral (cut 2), or to a light bordered surface (red border + red text, solid red kept for
RUN/signal only).

### 0.2 What makes it work mechanically

CustomTkinter does *not* repaint a widget on `state='disabled'` — it only swaps in
`text_color_disabled` and leaves the fill alone, so a disabled button would be indistinguishable from
an enabled one and the scheme would collapse. `GUI_theme_util._StateFillMixin` closes that gap: it
captures the enabled fill at construction and repaints on every state change, whether at construction
or via a later `configure(state=…)`. Call sites keep using plain `configure(state=…)` unchanged,
which matters because the suite toggles disabled state constantly (§5.4). It also restores a
*call-site* color on re-enable, so a custom fill is not lost.

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
with the bundled Tcl/Tk 8.6 runtime. CustomTkinter is compatible with that pin — its only hard
dep is `darkdetect`.

> **Version note (Phase 1):** the suite pins **`customtkinter==6.0.0`** — the version installed
> in the dev/build environment and validated green by the Phase 0 bundle smoke test — *not* the
> `5.2.x` this document first assumed. All widget-mapping and factory-wrapper work targets the
> **6.0.0** API (e.g. `CTkLabel` has no `justify`, `CTkEntry` has neither `justify` nor `anchor`);
> `GUI_theme_util.translate_kwargs` filters kwargs against each CTk class's real 6.0.0 signature
> so this stays correct if the pin moves.

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

1. Owns `customtkinter` setup: appearance mode, the NLP Suite theme, and widget-scaling defaults.
   Per §0 the theme fills interactive widgets with the brand red `#b10a0a` (the color at
   `GUI_util.py:188-190`) as the **enabled** state and flat grey as **disabled**, the latter applied
   automatically by `_StateFillMixin` (§0.2).
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

- Add `customtkinter==6.0.0` (+ transitive `darkdetect`) to `requirements.txt`, and the setup-app
  dependency probe (`setup-app/Resources/environment_probe.py` scans source imports — once
  `GUI_theme_util` `import customtkinter`, the probe requires it, which is why the pin lands here).
  The per-OS `requirements-mac.txt` / `requirements-windows.txt` are installed *in addition* to the
  base file, so the pin goes in `requirements.txt` **only** (adding it to all three would just
  double-install).
- Add `nlp_suite_theme.json` (CTk color theme, encoding the §0 rule) under `src/` so PyInstaller
  ships it (the spec's `src` collection is `.py`-only, so it needs an explicit datas entry — done).
- PyInstaller: add `collect_data_files('customtkinter')` to `NLP_Suite.spec` datas and
  `customtkinter`/`darkdetect` to hiddenimports; same for `NetworkGraphViewer.spec` if it grows a
  CTk UI.
- **Bundle smoke test on both OSes before anything else lands** (see §5.1 — this is the
  make-or-break risk, so it goes first).

> **Status (2026-07):** Phase 0's *bundle risk* work landed first (commits `19e490f2`, `24554889`:
> `tests/ctk_bundle_smoke.py` + `src/ctk_bundle_util.py`). The remaining Phase 0 *groundwork* above
> (requirements pin, theme JSON, spec datas/hiddenimports) was folded into **Phase 1 PR 1**
> alongside `GUI_theme_util`, since that PR is the first thing to actually `import customtkinter`.
> ⏳ Windows bundle smoke run still pending before Phase 0 is fully signed off (§5.1).

### Phase 1 — Shared framework (2–3 PRs, the heart of the migration)

1. `GUI_theme_util.py`: theme loading, factory wrappers, `ToolTip` class.
2. `GUI_util.py`: root window → `CTk()`; `GUI_top`, `GUI_bottom`,
   `display_about_release_team_cite_buttons`, logo display, `IO_config_setup_brief/full`
   rebuilt with wrappers + grid.
3. `GUI_IO_util.py`: `placeWidget` → grid translation (with the x-constant → column lookup);
   `place_help_button`; `message_box_widget`, `enter_value_widget`, `slider_widget`,
   `dropdown_menu_widget*`, `combobox_with_search_widget` popups → CTkToplevel + wrappers.

> **Status (2026-07):**
>
> - **PR 1** — `GUI_theme_util` compat layer + Phase 0 groundwork. Merged to `roberto` as **#1641**.
> - **Slice 2a** (`ctk/phase1-core`, **#1645**) — root → `CTk()`, shared-chrome factory conversions,
>   `GUI_top` intro widget; kept the `.place()` layout. Also `create_open_file_button` (the
>   open file/directory buttons were rendering as empty ~8 px slivers, `width=1, text=''`) and a
>   tightened logo column (logo 85×50 → 58×34, column-0 minsize 210 → 122).
> - **Slice 2b** (`ctk/phase1-grid`, **#1648**) — `placeWidget` → `grid()`: x-coordinate → coarse
>   semantic column band, row counter → grid row; tooltips bind `GUI_theme_util.ToolTip`; `GUI_top`'s
>   intro gridded into the header row. Also cleared the reflow artifacts on the front-door GUI
>   (gridded notebook, SETUP checkbox grouped with its wide button, folder glyphs on the blank
>   open-config buttons, Courier → native UI font, top-nav buttons moved to a 2×2 `place()`d
>   top-right block) and the `IO_config_setup_brief()` duplicate-INPUT-box overflow.
> - **Slice 3** (`ctk/phase1-popups`, base `ctk/phase1-grid`) — 4 of the 5 popups → `CTkToplevel` +
>   wrappers: `slider_widget` (CTkSlider plus a value label, since CTkSlider has no built-in readout;
>   integer steps, returns `int` to match `tk.Scale`), `dropdown_menu_widget`/`2`, and
>   `enter_value_widget` (was a second bare `tk.Tk()` with its own `mainloop()`; now parented to
>   `GUI_util.window` and driven by `wait_window()`).
> - **Accent-signal slice** (`ctk/phase1-accent-signal`) — implemented the cut-2 neutral theme, since
>   **superseded by cut 3** on pilot 2 (§0.1). The `accent=`/`muted=` opt-ins it added to
>   `create_button` / `create_option_menu` remain in use.
>
> **Deferred out of slice 3 to Phase 4** (both carry an in-code marker): `message_box_widget` — its
> buttons and countdown labels are `.place()`d at offsets computed from the packed `tk.Message`'s
> height and it fires on every RUN, so the geometry needs on-screen QA — and
> `combobox_with_search_widget`, which is unfinished and whose only call site is commented out.
>
> **Deferred out of #1648, not blockers:** window geometry is still tuned to the old absolute layout
> (~35% empty on the right on some GUIs — revisit `set_window` sizing); multi-column GUIs (SVO, GIS)
> and the raw-`.place()` GUIs (`data_visualization_main.py`, 140 sites) are unvalidated against the
> column bucketing (Phase 4); the now-dead `hover_over_widget` machinery awaits Phase 5 cleanup; and
> per-GUI visual QA on Mac + Windows, light + dark, is outstanding throughout.

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

> **Status: Phase 2 complete (2026-07-18).** All three pilots done. Every durable finding below is
> already a §6 checklist item — **§6 plus the §3 mapping, not this narrative, is what a Phase 3
> contributor works from.** Each pilot added at least one *silent-failure* item to it.
>
> **Pilot 1 — `wordclouds_main.py`** (`ctk/phase2-wordclouds`). 29 constructors → factories, 3
> `OptionMenu` → `create_option_menu(values=[...])`, open-image sliver → `create_open_file_button`,
> `ttk.Style`/`theme_use` dropped, dynamic csv-field repopulation → `set_values`. Surfaced the three
> legacy idioms CTk rejects — `.config(` (raises; 53 sites in this file alone), `widget['state']`
> (raises), `widget['values'] = …` (**silently no-ops**, and *not* caught by the `["menu"]` grep).
> Assume every Phase 3 file has all three. Two shared-layer fixes forced:
> 1. `create_entry` now adds a 14 px chrome allowance to the char→px width translation (new
>    `width_padding` arg on `translate_kwargs`) — CTkEntry reserves internal padding, so small
>    entries lost ~2 cells and the 4-char "Max no. of words" box rendered `100` as `10C`. The §5.2
>    tail arriving; expect more.
> 2. `tests/gui_smoke.py` stubbed `customtkinter` as a **blanket MagicMock**, which answers every call
>    and subscript and so absorbed *all three* idiom bugs silently — wordclouds passed a smoke run
>    while broken, recording **0 widgets**. Replaced with a hand-written stub reproducing the real
>    contracts, pinned against real CTk in `tests/test_gui_theme_util.py` so a CTk upgrade can't drift
>    them apart. **This is a prerequisite for trusting Phase 3**, not a nicety: without it the smoke
>    suite goes progressively blind as the other ~45 GUIs convert.
>
> **Pilot 2 — `NLP_menu_main.py`** (`ctk/phase2-menu`). 8 buttons + 3 checkboxes → factories, 3
> open-config buttons, 7 `ttk.Combobox` → `create_combobox`, and the suite's **only `ttk.Notebook` →
> `CTkTabview`**, which took the `ttk.Style`/`theme_use('clam')` block and the now-unused ttk import
> with it; the seven `.place()`d tab rows became a 3-column grid per tab frame. Two findings, both
> silent-failure:
> 1. **`textvariable=` is dropped by `CTkComboBox`** — it has only `variable=`, and all ~56 legacy
>    `ttk.Combobox` sites bind with `textvariable=`. `translate_kwargs` filters unknown kwargs
>    silently, so the widget renders fine with **no bound variable**: every `.trace` dead, RUN
>    dispatch quietly broken. `create_combobox` now renames it — it can't go in the global `_RENAME`
>    table because `CTkCheckBox` has *both* names with different meanings (`textvariable` = its label).
> 2. **`CTkTabview` tab frames, not `ttk.Frame`s, must parent CTk children** — CTk reads its
>    background off the master and a `ttk.Frame` has no queryable `bg`. Converting the notebook was
>    the fix.
>
> This pilot is also where the theme reversed to cut 3 (§0.1) — the neutral theme read as "everything
> disabled" on screen.
>
> **Pilot 3 — `NLP_setup_IO_main.py`** (`ctk/phase2-setup-io`). Smallest by widget count (13) but the
> only one exercising the **config plumbing**, so it was verified by *equivalence* rather than by eye:
> the `get_IO_options_list` / `get_IO_options_str` round-trip driven across all three checkbox states
> against the pre-conversion file, byte-identical output. **Reuse that check for the remaining
> `NLP_setup_*` GUIs** — a widget swap that quietly changes what lands in a config file is invisible
> on screen. Three findings:
> 1. **`create_label(textvariable=…)` dropped the variable.** `CTkLabel` supports it, but only by
>    forwarding out of `**kwargs` — it is not a named parameter of `__init__`, so the signature filter
>    dropped it and the path labels rendered CTk's literal `"CTkLabel"`. Fixed in `create_label`.
>    "CTk accepts this kwarg" and "`translate_kwargs` passes it through" are different questions.
>    7 more raw `tk.Label(…textvariable=…)` sites remain suite-wide.
> 2. **`tk.OptionMenu` int choices must become strings** — `CTkOptionMenu` renders `values` as text
>    and writes selections back as strings. The bound `IntVar` can stay as-is.
> 3. **Widgets that used to overlap *exactly* now sit side by side.** This GUI stacked a second label
>    on the one `GUI_top` lays out, purely to carry a richer date tooltip; absolute placement made the
>    two coincide, the grid renders the path **twice**. Fixed rather than re-stacked:
>    `GUI_util.IO_path_labels` publishes the canonical labels and the GUI binds a `ToolTip` to them —
>    what the coordinate-free class was for. Expect more wherever a GUI re-places a shared-chrome
>    widget.
>
> One deliberate behavior change: `activate_fields()` was never called at startup (the call sat
> commented out), so date widgets began life *visually* enabled. Harmless under stock tk; under §0's
> red-active/grey-inactive rule the GUI was lying about what is clickable. Now called once after
> build, with `warn=False` so the startup sync doesn't fire a popup at a user who has touched nothing.
>
> **Verified across the pilots:** `tests/gui_smoke.py` (44 ok, 0 missing golden), `pytest` (50
> passed), plus a headless harness for pilot 3 (it is in `KNOWN_SKIP`); all three launched on macOS.
> **Outstanding: Windows QA, Roberto's call on §0, and the deferred #1648 window-geometry item.**

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

**Phase 0 result (2026-07-15, macOS aarch64, cpython-3.10.15 python-build-standalone):**
`tests/ctk_bundle_smoke.py` run under the bundled interpreter confirms CTk core is fine (root,
Label/Button/OptionMenu/Frame, appearance toggle) but **raw `CTkImage` fails exactly as predicted**
— `TypeError: bad argument type for built-in operation` from `PIL.ImageTk`. **Fix landed:**
`ctk_bundle_util.patch_ctk_image_for_bundle()` monkeypatches the two `CTkImage` methods that touch
ImageTk (`_get_scaled_light_photo_image` / `_get_scaled_dark_photo_image`) to build their Tk image
through the same base64-PNG path as `GUI_util.tk_image_from_pil`. With the patch applied the smoke
test is **green on Mac**; `CTkImage` is now usable in the bundle. ⏳ **Still pending: the same run on
Windows** (different Tcl/Tk build) before Phase 0 is fully signed off.

**Mitigations:**
- Phase 0 ships `tests/ctk_bundle_smoke.py` (CTk root, widgets, OptionMenu repopulation, **`CTkImage`
  via the patch**, appearance toggle) and we run it **inside the built bundle** on both OSes before
  committing to the migration.
- Call `ctk_bundle_util.patch_ctk_image_for_bundle()` **once at startup, before any `CTkImage`**
  (fold into the CTk bootstrap / `GUI_theme_util` init in Phase 1). It is idempotent and raises
  loudly if a CustomTkinter upgrade moves the patched methods. This supersedes the earlier
  "never use `CTkImage`" rule — with the patch, CTk's native image idiom is safe in the bundle.
- If the bundle smoke test ever fails for CTk itself (e.g., its font/scaling probing), the fallback
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

`customtkinter==6.0.0` in `requirements.txt` only — see §1.3 (why that version, and its API
implications) and Phase 0 (why the base file only). Its deps must stay compatible with
`Pillow==10.4.0`; they are, since CTk does not require Pillow ≥11.

---

## 6. Per-GUI conversion checklist (used in Phases 2–4)

For each `*_main.py` PR:

- [ ] All `tk.`/`ttk.` widget constructors replaced with `GUI_theme_util` factories
      (grep: `tk.Button(`, `tk.Checkbutton(`, `tk.Label(`, `tk.Entry(`, `tk.OptionMenu(`,
      `ttk.Combobox(`, `tk.Scale(`, `tk.Text(`).
- [ ] **No `.config(` left** (grep `\.config\(` → `.configure(`). CTk implements `config()` *only to
      raise* `AttributeError`. This is the single highest-volume edit in a conversion — 53 sites in
      the first pilot alone.
- [ ] **No `widget['option']` reads left** (grep `\w\['`) — e.g. `menu['state']`. CTk resolves
      `__getitem__` against the underlying tk frame, which has no such option → `TclError`.
      Use `widget.cget('option')`.
- [ ] **No `widget['values'] = …` / `widget[k] = v` writes left.** The dangerous one: tkinter's
      `__setitem__` calls `configure({k: v})`, which lands the dict on CTk's **first positional
      parameter `require_redraw`** — so it *silently does nothing*, no exception. Use
      `GUI_theme_util.set_values(...)` / `widget.configure(k=v)`. **The `["menu"]` grep below does
      not catch this** (it is the `ttk.Combobox` analogue).
- [ ] **No `textvariable=` left on a converted Combobox.** `CTkComboBox` has only `variable=`, and
      `translate_kwargs` drops unknown kwargs silently — so the widget renders fine with **no bound
      variable**, killing every `.trace` on it with no error. `create_combobox` renames it; the check
      is that combobox call sites go through the factory (grep `ttk.Combobox(`).
- [ ] **Labels bound to a variable go through `create_label`** (grep `tk.Label(.*textvariable`).
      `CTkLabel` forwards `textvariable` to its inner tk label out of `**kwargs`, so it is invisible
      to `translate_kwargs`' signature filter — a raw call drops it and the label displays CTk's
      literal `"CTkLabel"` placeholder forever. Third member of the silent-drop family.
- [ ] **`tk.OptionMenu` int choices converted to strings** (grep `tk.OptionMenu(` for numeric
      varargs). `CTkOptionMenu` renders `values` as text and writes selections back as strings; the
      bound `IntVar` can stay as-is.
- [ ] **No widget re-placed on top of one `GUI_top`/`GUI_bottom` already lays out.** Several GUIs
      stack a duplicate on the shared chrome's widget to attach their own hover text — the absolute
      layout hid it, the grid renders it twice. Bind a `GUI_theme_util.ToolTip` to the shared widget
      instead (`GUI_util.IO_path_labels` publishes the INPUT path labels for exactly this).
- [ ] **Startup state sync:** if the GUI has an `activate_fields`-style enable/disable routine, it
      must run once *after* the widgets are built. Under §0's red-active/grey-inactive theme a
      widget that starts un-synced is actively mislabeled as clickable. Suppress any user-facing
      warning on that first call.
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
