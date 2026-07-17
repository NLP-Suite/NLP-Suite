"""GUI_theme_util -- CustomTkinter compatibility layer for the NLP Suite.

Part of the CustomTkinter migration (docs/CustomTkinter-Migration-Plan.md, Phase 1). This module is
the single place that owns CTk setup and the thin factory wrappers that let ~50 legacy GUI scripts
stop calling ``tk.Button(...)`` / ``tk.OptionMenu(...)`` directly and instead call
``GUI_theme_util.create_button(...)`` etc. The wrappers accept the *old tk-style keyword arguments*
(character-based ``width=``, ``foreground=``, tk-only chrome like ``relief=``/``bd=``) and translate
them to CustomTkinter equivalents (pixel-based ``width=``, ``text_color=``, unsupported kwargs
dropped), so the mechanical per-file conversion in later phases is a near-verbatim call-site rename.

Design notes
------------
* **Introspection-driven translation.** Rather than hand-maintaining a per-widget allow/deny list
  (which drifts as CustomTkinter changes -- e.g. CTk 6.0.0's ``CTkLabel`` has no ``justify``, and
  ``CTkEntry`` has neither ``justify`` nor ``anchor``), every wrapper filters the translated kwargs
  against the *actual* accepted parameters of the target CTk class, read once via
  ``inspect.signature``. A tk-only kwarg that has no CTk home is silently dropped rather than
  crashing the constructor.
* **Character widths -> pixels.** Legacy ``tk.Entry(width=30)`` means 30 characters;
  ``CTkEntry(width=300)`` means 300 pixels. ``char_width_to_px`` / ``line_height_to_px`` do the
  conversion (§5.2 of the plan). These are pure and unit-tested.
* **No import-time side effects beyond importing CTk.** Loading a theme and setting the appearance
  mode happen only when ``init_appearance()`` is called (from the CTk bootstrap in Phase 2's
  GUI_util rewrite), never at import, so this module can be imported headlessly in tests.

This module is a pure addition in Phase 1 PR 1: nothing in ``src/`` imports it yet. Phase 1 PR 2
wires ``GUI_util`` / ``GUI_IO_util`` onto it.
"""

import inspect
import tkinter as tk
import warnings

import customtkinter as ctk

import ctk_bundle_util

# NLP Suite brand accent (see GUI_util.py "RGB red is #b10a0a"). Mirrored in nlp_suite_theme.json.
NLP_SUITE_ACCENT = "#b10a0a"

# Legacy tk widths are in characters; CTk widths are in pixels. Rough average glyph advance for the
# suite's UI font. Tuned once here; per-call-site tweaks happen during the pilot/batch phases.
_PX_PER_CHAR = 8
# Legacy tk heights (buttons/labels/text) are in text lines; CTk heights are in pixels.
_PX_PER_LINE = 22
# A CTk widget's natural (default) height, used as the floor when translating small line counts.
_MIN_WIDGET_PX = 28

# tk keyword -> CTk keyword renames. (Colors: tk ``foreground``/``fg`` -> CTk ``text_color``.)
_RENAME = {
    "foreground": "text_color",
    "fg": "text_color",
}

# tk keywords that describe native-widget chrome CTk draws itself (or the theme owns). Dropped
# outright so they never reach a CTk constructor even if some future CTk class grows a like-named
# parameter with different semantics. Background colors are dropped rather than mapped to
# ``fg_color`` so a legacy ``bg='SystemButtonFace'`` can't stomp the themed accent.
_DROP = frozenset(
    {
        "bg",
        "background",
        "activebackground",
        "activeforeground",
        "disabledforeground",
        "highlightbackground",
        "highlightcolor",
        "highlightthickness",
        "bd",
        "borderwidth",
        "relief",
        "overrelief",
        "offrelief",
        "selectcolor",
        "indicatoron",
        "padx",
        "pady",
        "takefocus",
        "repeatdelay",
        "repeatinterval",
        "cursor",
        "underline",
        "default",
        "wraplength",  # tk wraplength is in pixels but rarely matched to CTk metrics; let CTk reflow.
    }
)


def char_width_to_px(char_width, px_per_char=_PX_PER_CHAR, padding=0):
    """Translate a legacy tk character-based width into a CTk pixel width.

    The input is *always* treated as a character count -- there is no magnitude cutoff that guesses
    "this looks big, it must already be pixels". Legacy char widths in the suite run past 200 (wide
    file-path and search entries), so any such guess would shrink exactly the widest fields. A caller
    that genuinely holds a pixel width bypasses this multiply via ``width_is_chars=False`` in
    :func:`translate_kwargs` (see :func:`create_slider`) instead.

    Returns ``None`` for a missing / non-positive / non-numeric width so the caller can drop the
    ``width`` kwarg entirely and let CTk use its own default sizing.
    """
    try:
        n = int(char_width)
    except (TypeError, ValueError):
        return None
    if n <= 0:
        return None
    return n * px_per_char + padding


def line_height_to_px(char_height):
    """Translate a legacy tk line-based height (e.g. a 2-line RUN button) into a CTk pixel height.

    Like :func:`char_width_to_px`, the input is always treated as a line count -- pixel-holding
    callers use ``height_is_lines=False`` in :func:`translate_kwargs` (as :func:`create_entry` does)
    rather than relying on a magnitude guess.

    Returns ``None`` for a missing / non-positive / non-numeric height so the caller drops the
    ``height`` kwarg and CTk uses its default widget height.
    """
    try:
        n = int(char_height)
    except (TypeError, ValueError):
        return None
    if n <= 0:
        return None
    return max(_MIN_WIDGET_PX, n * _PX_PER_LINE)


def _accepted_params(cls):
    """The set of keyword parameters ``cls.__init__`` accepts (minus self/master/*args/**kwargs)."""
    params = inspect.signature(cls.__init__).parameters
    return {
        name
        for name, p in params.items()
        if name not in ("self", "master", "args", "kwargs") and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    }


def translate_kwargs(cls, kwargs, width_is_chars=True, height_is_lines=True):
    """Translate legacy tk widget kwargs into kwargs valid for CustomTkinter class ``cls``.

    Pure function (no widget is created), so it is unit-testable against the real CTk classes via
    signature introspection without a display. Rules:

    * ``foreground``/``fg`` -> ``text_color``.
    * ``width`` (characters) -> pixels via :func:`char_width_to_px` when ``width_is_chars``.
    * ``height`` (lines) -> pixels via :func:`line_height_to_px` when ``height_is_lines``.
    * native-tk chrome kwargs (``relief``, ``bd``, ``bg``, ...) are dropped.
    * anything the target CTk class does not accept is dropped (never passed through blindly).
    """
    accepted = _accepted_params(cls)
    out = {}
    for key, value in kwargs.items():
        if key in _DROP:
            continue
        if key == "width" and width_is_chars:
            value = char_width_to_px(value)
            if value is None:
                continue
        elif key == "height" and height_is_lines:
            value = line_height_to_px(value)
            if value is None:
                continue
        key = _RENAME.get(key, key)
        if key in accepted:
            out[key] = value
        # else: a tk-only kwarg with no CTk equivalent -- drop it silently.
    return out


# ---------------------------------------------------------------------------------------------
# Widget factories. Each mirrors the tk constructor call signature its call sites already use
# (master first, then keyword args) so the mechanical conversion is a name swap.
# ---------------------------------------------------------------------------------------------


def create_button(master, **kwargs):
    return ctk.CTkButton(master, **translate_kwargs(ctk.CTkButton, kwargs))


def create_label(master, **kwargs):
    return ctk.CTkLabel(master, **translate_kwargs(ctk.CTkLabel, kwargs))


def create_entry(master, **kwargs):
    # tk.Entry has no height; only width is character-based.
    return ctk.CTkEntry(master, **translate_kwargs(ctk.CTkEntry, kwargs, height_is_lines=False))


def create_checkbox(master, **kwargs):
    return ctk.CTkCheckBox(master, **translate_kwargs(ctk.CTkCheckBox, kwargs))


def create_option_menu(master, variable=None, values=None, command=None, **kwargs):
    """tk.OptionMenu(master, var, *choices) -> CTkOptionMenu(master, variable=, values=[...]).

    The legacy call passes the choices as varargs; call sites converting to this factory pass them
    as ``values=[...]``. Repopulate a live menu with :func:`set_values` (never the old
    ``widget["menu"]`` mutation).
    """
    translated = translate_kwargs(ctk.CTkOptionMenu, kwargs)
    if variable is not None:
        translated["variable"] = variable
    if values is not None:
        translated["values"] = list(values)
    if command is not None:
        translated["command"] = command
    return ctk.CTkOptionMenu(master, **translated)


def create_combobox(master, values=None, **kwargs):
    translated = translate_kwargs(ctk.CTkComboBox, kwargs)
    if values is not None:
        translated["values"] = list(values)
    return ctk.CTkComboBox(master, **translated)


def create_slider(master, from_=None, to=None, length=None, orient=None, resolution=None, **kwargs):
    """tk.Scale(...) -> CTkSlider(...).

    Maps the tk names CTk renamed: ``length`` (px long dimension) -> ``width``, ``orient`` ->
    ``orientation``, and ``resolution`` (step size) -> ``number_of_steps`` when a range is known.
    CTkSlider has no built-in value label; call sites that need one add a small CTkLabel bound to
    the same variable (the legacy ``slider_widget`` popup already does this by hand).
    """
    translated = translate_kwargs(ctk.CTkSlider, kwargs, width_is_chars=False, height_is_lines=False)
    if from_ is not None:
        translated["from_"] = from_
    if to is not None:
        translated["to"] = to
    if length is not None:
        translated["width"] = length
    if orient is not None:
        translated["orientation"] = orient
    if resolution and from_ is not None and to is not None:
        try:
            steps = int(round((float(to) - float(from_)) / float(resolution)))
            if steps > 0:
                translated["number_of_steps"] = steps
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    return ctk.CTkSlider(master, **translated)


def create_textbox(master, **kwargs):
    # tk.Text width is characters, height is lines; CTkTextbox has a built-in scrollbar so the
    # manual tk.Scrollbar pairing at the call site is dropped during conversion.
    return ctk.CTkTextbox(master, **translate_kwargs(ctk.CTkTextbox, kwargs))


def set_values(widget, values, default=None):
    """Repopulate a CTkOptionMenu / CTkComboBox's items -- the CTk replacement for the legacy
    ``menu = widget["menu"]; menu.delete(0, "end"); menu.add_command(...)`` idiom.

    Pass ``default`` to also select an item (e.g. the first) after repopulating. Returns the
    normalized list actually set.
    """
    values = list(values)
    widget.configure(values=values)
    if default is not None:
        widget.set(default)
    return values


class ToolTip:
    """Lightweight hover tooltip bound to a widget's ``<Enter>``/``<Leave>`` events.

    Replaces the coordinate-based ``GUI_IO_util.hover_over_widget`` / ``display_widget_info``
    machinery, which reconstructed popup positions from the same absolute pixel constants the grid
    migration removes. Bind to the widget itself instead; the ``text`` strings (the suite's main
    in-app documentation) are preserved verbatim by the callers. The tooltip surface is a plain
    ``tk.Toplevel`` (the classic yellow tip), which renders fine under a CTk root and needs no CTk
    theming of its own.
    """

    def __init__(self, widget, text, delay_ms=500, wraplength=420):
        self.widget = widget
        self.text = text or ""
        self.delay_ms = delay_ms
        self.wraplength = wraplength
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        if self.text:
            self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip is not None or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        except Exception:
            return
        self._tip = tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tip,
            text=self.text,
            justify="left",
            background="#ffffe0",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength,
        )
        label.pack(ipadx=4, ipady=3)

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def _theme_path():
    """Absolute path to nlp_suite_theme.json, or ``None`` if it can't be located.

    Resolves through ``GUI_IO_util.scriptPath`` (which is frozen-bundle aware -- the theme ships to
    ``<exe>/src`` via NLP_Suite.spec) and falls back to this module's own directory for a dev
    checkout. Imported lazily so this module has no import-time dependency on GUI_IO_util (which the
    unit-test harness stubs).
    """
    import os

    candidates = []
    try:
        import GUI_IO_util

        candidates.append(os.path.join(GUI_IO_util.scriptPath, "nlp_suite_theme.json"))
    except Exception:
        pass
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nlp_suite_theme.json"))
    for path in candidates:
        try:
            if os.path.isfile(path):
                return path
        except Exception:
            pass
    return None


_initialized = False


def init_appearance(appearance_mode="system"):
    """One-time, idempotent CustomTkinter bootstrap. Call once at startup, before creating any CTk
    widget or CTkImage.

    Order matters: the bundle ImageTk patch (``ctk_bundle_util.patch_ctk_image_for_bundle``) must
    run before any CTkImage is built, and the color theme must be set before any widget is created
    (CTk snapshots theme colors at construction). Falls back to CTk's stock ``blue`` theme if the
    NLP Suite theme file can't be found or fails to load, so a bad/missing data file degrades
    appearance instead of crashing the launch -- but the failure is printed, NOT swallowed silently,
    because a silent fallback previously hid a malformed-theme bug (CTk rejects a top-level JSON key
    whose value is not a dict, e.g. a ``"_comment"`` string) that shipped the whole suite in blue.
    """
    global _initialized
    if _initialized:
        return
    ctk_bundle_util.patch_ctk_image_for_bundle()
    path = _theme_path()
    if path:
        try:
            ctk.set_default_color_theme(path)
        except Exception as exc:
            warnings.warn(
                f"failed to load NLP Suite theme '{path}' ({exc}); falling back to the stock 'blue' theme.",
                stacklevel=2,
            )
            ctk.set_default_color_theme("blue")
    else:
        warnings.warn("nlp_suite_theme.json not found; falling back to the stock 'blue' theme.", stacklevel=2)
        ctk.set_default_color_theme("blue")
    try:
        ctk.set_appearance_mode(appearance_mode)
    except Exception:
        pass
    _initialized = True
