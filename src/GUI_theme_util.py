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
from typing import TYPE_CHECKING
import warnings

import customtkinter as ctk

import ctk_bundle_util

# NLP Suite brand accent (see GUI_util.py "RGB red is #b10a0a"), and the theme's default fill for
# every ENABLED interactive widget. The rule the theme encodes is **red = active, grey = inactive**:
# an enabled control is brand red, a disabled one is a flat grey (see _StateFillMixin, which does the
# repaint CTk itself does not do).
#
# History, because this reverses twice (plan §0): the first migration cut painted every widget red;
# that was reverted to a neutral-grey default on reviewer instruction, because red carried the
# availability cue on the TIPS / videos / reminders dropdowns (red = a resource exists for this GUI,
# grey = none) and a blanket red erased it. The neutral cut then read as *disabled everywhere*, so
# red-active/grey-inactive is the third position: it keeps the availability cue working, since a
# dropdown with nothing behind it is exactly an inactive control, but it does spend the red that
# used to make RUN and the TIPS dropdowns stand out. That trade is deliberate and needs Roberto's
# sign-off -- see the pilot-2 note in the plan's §4.
#
# Light-mode value first, dark-mode second (CTk color pairs); appearance is pinned "light" in Phase 1
# but both are supplied so the accent survives a later dark-mode enable.
NLP_SUITE_ACCENT = "#b10a0a"
_ACCENT_FG = ["#b10a0a", "#c81414"]
_ACCENT_HOVER = ["#8a0808", "#9e0d0d"]
_ACCENT_TEXT = ["#FFFFFF", "#F5E9E9"]
# The OptionMenu arrow-button portion is a shade darker than the body, matching CTk's convention.
_ACCENT_MENU_BUTTON = ["#8a0808", "#9e0d0d"]
_ACCENT_MENU_BUTTON_HOVER = ["#6d0606", "#7a0a0a"]

# Hover-tooltip surface. The tips are an *overlay* on top of the GUI, not a document element, so
# they invert against the light window rather than sitting on it: a dark charcoal card reads as
# floating and, unlike the classic pale-yellow sticky note, never competes with the content it
# covers. Square corners and a hairline border rather than a rounded card with a drop shadow --
# an ``overrideredirect`` Toplevel has no per-pixel alpha on Windows or Linux, so a radius would
# render as light corner triangles; the border supplies the edge definition the shadow would.
_TIP_BG = "#24262b"
_TIP_TEXT = "#f2f3f5"
_TIP_BORDER = "#3a3d44"

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
        if name not in ("self", "master", "args", "kwargs")
        and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    }


def translate_kwargs(cls, kwargs, width_is_chars=True, height_is_lines=True, width_padding=0):
    """Translate legacy tk widget kwargs into kwargs valid for CustomTkinter class ``cls``.

    Pure function (no widget is created), so it is unit-testable against the real CTk classes via
    signature introspection without a display. Rules:

    * ``foreground``/``fg`` -> ``text_color``.
    * ``width`` (characters) -> pixels via :func:`char_width_to_px` when ``width_is_chars``,
      plus ``width_padding`` px of chrome allowance (see :func:`create_entry`).
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
            value = char_width_to_px(value, padding=width_padding)
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
# Grey means INACTIVE.
#
# The theme paints enabled controls as a light surface with a border (they read as pressable) and
# reserves a flat grey fill for disabled ones. CustomTkinter does not do that second half by itself:
# ``state='disabled'`` only swaps in ``text_color_disabled`` and leaves the fill untouched, so a
# disabled button would look identical to an enabled one. The mixin below closes that gap -- it
# repaints the fill whenever ``state`` is set, at construction or later via ``configure(state=...)``.
#
# It lives in the shared layer rather than at call sites because the suite toggles disabled state
# constantly (plan §5.4) through plain ``configure(state=...)`` calls, which keep working unchanged.
# ---------------------------------------------------------------------------------------------

_DISABLED_FILL = ["#DFE1E4", "#2F3336"]
_DISABLED_BORDER = ["#CBCFD3", "#3A3E42"]

# CTkBaseClass (not a concrete widget class) so the mixin's bind/unbind signatures stay
# compatible with every widget it is combined with.
_MixinBase = ctk.CTkBaseClass if TYPE_CHECKING else object


# At runtime this is a plain mixin (base `object`), so it composes with whichever concrete CTk widget
# class it is combined with -- and so tests/gui_smoke.py's hand-written CTk stub, which has no widget
# base class to inherit from, can still import this module. The type-checking-only base just tells
# Pyright where the cget/configure it calls come from.
class _StateFillMixin(_MixinBase):
    """Repaint a CTk widget's fill to the flat 'inactive' grey while its state is ``disabled``.

    ``_STATE_FILL_KEYS`` names the color options a subclass wants swapped; the enabled values are
    captured from the live widget at construction, so a call site that passed its own ``fg_color``
    (e.g. the accent red on RUN) gets that color back when it is re-enabled.
    """

    _STATE_FILL_KEYS = ("fg_color",)

    def __init__(self, *args, **kwargs):
        state = kwargs.get("state", "normal")
        super().__init__(*args, **kwargs)
        self._enabled_fill = {key: self.cget(key) for key in self._STATE_FILL_KEYS}
        if str(state) == "disabled":
            self._paint_for_state("disabled")

    def configure(self, require_redraw=False, **kwargs):
        state = kwargs.get("state")
        super().configure(require_redraw, **kwargs)
        if state is not None:
            self._paint_for_state(str(state))

    def _paint_for_state(self, state):
        if state == "disabled":
            colors = {key: _DISABLED_FILL for key in self._STATE_FILL_KEYS}
            if "border_color" in colors:
                colors["border_color"] = _DISABLED_BORDER
        else:
            colors = dict(self._enabled_fill)
        # No 'state' key here, so this cannot recurse back into _paint_for_state.
        super().configure(require_redraw=True, **colors)


class _ThemedButton(_StateFillMixin, ctk.CTkButton):
    _STATE_FILL_KEYS = ("fg_color", "border_color")


class _ThemedOptionMenu(_StateFillMixin, ctk.CTkOptionMenu):
    _STATE_FILL_KEYS = ("fg_color", "button_color")


class _ThemedComboBox(_StateFillMixin, ctk.CTkComboBox):
    _STATE_FILL_KEYS = ("fg_color", "button_color")


# ---------------------------------------------------------------------------------------------
# Widget factories. Each mirrors the tk constructor call signature its call sites already use
# (master first, then keyword args) so the mechanical conversion is a name swap.
# ---------------------------------------------------------------------------------------------


def create_button(master, accent=False, **kwargs):
    """tk.Button(...) -> CTkButton(...).

    ``accent=True`` paints the button in the brand red instead of the neutral theme default -- used
    for the single RUN primary-action button per GUI (the one control that earns the accent among
    buttons; see the plan's §0). An explicit ``fg_color``/``hover_color``/``text_color`` at the call
    site still wins, so the accent is only a default.
    """
    translated = translate_kwargs(ctk.CTkButton, kwargs)
    if accent:
        translated.setdefault("fg_color", _ACCENT_FG)
        translated.setdefault("hover_color", _ACCENT_HOVER)
        translated.setdefault("text_color", _ACCENT_TEXT)
    return _ThemedButton(master, **translated)


# The small "open the selected file / directory" affordance. The legacy `width=1, text=''` rendered
# these as ~8px empty slivers (the red bars / gray box users read as broken). A folder glyph plus a
# real width makes them read as buttons. Kept in one place so the glyph can be swapped in a single
# edit if a platform's Tk font renders emoji as a tofu box (fallback: '...').
OPEN_FILE_GLYPH = "\U0001f4c2"  # 📂


def create_open_file_button(master, command=None, width=32, **kwargs):
    """Small themed icon button for the 'open selected file/directory' action.

    Built directly on CTkButton (not via :func:`create_button`) so ``width`` is honoured as pixels:
    the char->px translation in ``create_button`` treats any width <= 60 as a character count, so a
    ~30px icon button can't be expressed through it. Any leftover legacy ``text``/``width`` kwargs
    are dropped in favour of the fixed glyph and the pixel width.
    """
    kwargs.pop("text", None)
    kwargs.pop("width", None)
    translated = translate_kwargs(ctk.CTkButton, kwargs)
    translated["width"] = width
    return _ThemedButton(master, text=OPEN_FILE_GLYPH, command=command, **translated)


def create_label(master, **kwargs):
    """tk.Label(...) -> CTkLabel(...).

    ``textvariable=`` is forwarded by hand. CTkLabel supports it, but only by passing it on to its
    inner ``tkinter.Label`` out of ``**kwargs`` -- it is not a named parameter of
    ``CTkLabel.__init__``, so :func:`translate_kwargs`' signature filter drops it *silently*. The
    label then renders CTk's literal ``"CTkLabel"`` placeholder and never tracks the variable, which
    is what the file/directory path labels did on first conversion. Same silent-drop class as the
    ``textvariable`` rename in :func:`create_combobox`.

    The placeholder is also blanked whenever a variable is bound: CTkLabel sets its ``text`` before
    configuring the tk attributes, so a leftover default would otherwise win until the variable's
    next write.
    """
    textvariable = kwargs.pop("textvariable", None)
    translated = translate_kwargs(ctk.CTkLabel, kwargs)
    if textvariable is not None:
        translated["textvariable"] = textvariable
        translated.setdefault("text", "")
    return ctk.CTkLabel(master, **translated)


# A CTkEntry reserves internal horizontal padding around its text area, so a bare chars*px width
# yields fewer usable character cells than the legacy tk.Entry did. That is invisible on the wide
# file-path entries but clips the small ones: the Phase 2 pilot's 4-char "Max no. of words" box
# rendered "100" as "10C". Add the chrome back so a width=N entry still shows N characters.
_ENTRY_PADDING_PX = 14


def create_entry(master, **kwargs):
    # tk.Entry has no height; only width is character-based.
    return ctk.CTkEntry(
        master,
        **translate_kwargs(
            ctk.CTkEntry, kwargs, height_is_lines=False, width_padding=_ENTRY_PADDING_PX
        ),
    )


# CTk's default checkbox box is 24x24 with a 3px border -- chunky next to the suite's 13pt label
# font (the box out-measures the text's cap height, reading as oversized). Size the box to the text
# instead: ~18px square with a 2px border tracks the 13pt glyphs. Set here (not the theme JSON, which
# has no checkbox_width/height keys) as overridable defaults so a call site can still request its own.
_CHECKBOX_BOX_PX = 16
_CHECKBOX_BORDER_PX = 2


def create_checkbox(master, **kwargs):
    translated = translate_kwargs(ctk.CTkCheckBox, kwargs)
    translated.setdefault("checkbox_width", _CHECKBOX_BOX_PX)
    translated.setdefault("checkbox_height", _CHECKBOX_BOX_PX)
    translated.setdefault("border_width", _CHECKBOX_BORDER_PX)
    return ctk.CTkCheckBox(master, **translated)


# The TIPS / videos / reminders dropdowns carry the availability cue:
#   * accent=True -> brand RED: a resource IS available for this GUI (the legacy "red" state). Under
#     the red-active theme this is also the default fill, so accent= is now a no-op for buttons; it
#     is kept because it documents intent at the call site and survives a theme change.
#   * muted=True  -> the inactive GREY: explicitly "nothing available for this GUI".
# muted deliberately matches the disabled palette (_DISABLED_FILL): a dropdown with nothing behind it
# IS an inactive control, so it should read exactly like one. Light-mode values first.
_MUTED_FG = "#DFE1E4"
_MUTED_BUTTON = "#D2D5D8"
_MUTED_BUTTON_HOVER = "#C6C9CC"
_MUTED_TEXT = "#8A9099"


def create_option_menu(master, variable=None, values=None, command=None, muted=False, accent=False, **kwargs):
    """tk.OptionMenu(master, var, *choices) -> CTkOptionMenu(master, variable=, values=[...]).

    The legacy call passes the choices as varargs; call sites converting to this factory pass them
    as ``values=[...]``. Repopulate a live menu with :func:`set_values` (never the old
    ``widget["menu"]`` mutation).

    The theme default is a neutral grey (red is not the default fill -- see the plan's §0). The two
    flags opt into the availability cue on the TIPS / videos / reminders dropdowns:

    * ``accent=True`` -> brand RED, i.e. a resource IS available for this GUI.
    * ``muted=True``  -> a lighter grey, i.e. nothing is available for this GUI.

    They are complements; passing neither leaves the neutral default (used by ordinary dropdowns like
    the Setup and I/O-config menus). ``accent`` takes precedence if both are somehow passed.
    """
    translated = translate_kwargs(ctk.CTkOptionMenu, kwargs)
    if accent:
        translated.setdefault("fg_color", _ACCENT_FG)
        translated.setdefault("button_color", _ACCENT_MENU_BUTTON)
        translated.setdefault("button_hover_color", _ACCENT_MENU_BUTTON_HOVER)
        translated.setdefault("text_color", _ACCENT_TEXT)
    elif muted:
        translated.setdefault("fg_color", _MUTED_FG)
        translated.setdefault("button_color", _MUTED_BUTTON)
        translated.setdefault("button_hover_color", _MUTED_BUTTON_HOVER)
        translated.setdefault("text_color", _MUTED_TEXT)
    if variable is not None:
        translated["variable"] = variable
    if values is not None:
        translated["values"] = list(values)
    if command is not None:
        translated["command"] = command
    return _ThemedOptionMenu(master, **translated)


def create_combobox(master, values=None, **kwargs):
    """ttk.Combobox(...) -> CTkComboBox(...).

    ``textvariable=`` is renamed to CTk's ``variable=``. This rename lives here rather than in the
    global ``_RENAME`` table because the two names mean *different* things on other classes:
    CTkCheckBox has both, where ``textvariable`` drives its label and ``variable`` its value. Without
    the rename the kwarg is silently dropped (it is not in CTkComboBox's signature), leaving a
    combobox with no bound variable -- so every ``.trace`` on it stops firing and the widget looks
    fine while doing nothing. Same silent-failure class as the ``widget['values'] = ...`` write in
    the plan's §6 checklist.
    """
    if "textvariable" in kwargs and "variable" not in kwargs:
        kwargs["variable"] = kwargs.pop("textvariable")
    translated = translate_kwargs(ctk.CTkComboBox, kwargs)
    if values is not None:
        translated["values"] = list(values)
    return _ThemedComboBox(master, **translated)


def create_slider(
    master, from_=None, to=None, length=None, orient=None, resolution=None, **kwargs
):
    """tk.Scale(...) -> CTkSlider(...).

    Maps the tk names CTk renamed: ``length`` (px long dimension) -> ``width``, ``orient`` ->
    ``orientation``, and ``resolution`` (step size) -> ``number_of_steps`` when a range is known.
    CTkSlider has no built-in value label; call sites that need one add a small CTkLabel bound to
    the same variable (the legacy ``slider_widget`` popup already does this by hand).
    """
    translated = translate_kwargs(
        ctk.CTkSlider, kwargs, width_is_chars=False, height_is_lines=False
    )
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


def set_char_width(widget, char_width):
    """Resize an already-built widget to a legacy tk *character* width.

    The factories translate ``width=`` on the way in, but a legacy GUI often builds a widget bare and
    sizes it afterwards -- ``menu.configure(width=2)``, ``entry.configure(width=widget_width_long)``.
    That call bypasses the factory entirely and CTk reads the number as **pixels**, so a ``width=2``
    dropdown collapses to a 2px sliver and a 60-char entry to 60px. No exception, just a widget too
    small to read: the same silent-failure family as the dropped ``textvariable``.

    Entries get the same chrome allowance :func:`create_entry` adds, so N characters stay N
    characters whichever path sized the widget.
    """
    padding = _ENTRY_PADDING_PX if isinstance(widget, ctk.CTkEntry) else 0
    px = char_width_to_px(char_width, padding=padding)
    if px is not None:
        widget.configure(width=px)
    return px


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
    ``tk.Toplevel`` -- a dark charcoal card (see ``_TIP_BG``), which renders fine under a CTk root
    and needs no CTk theming of its own.
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
        tip.configure(background=_TIP_BORDER)  # 1px of the Toplevel shows through as the border
        tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tip,
            text=self.text,
            justify="left",
            background=_TIP_BG,
            foreground=_TIP_TEXT,
            borderwidth=0,
            wraplength=self.wraplength,
        )
        # The border is drawn by the parent's background rather than relief='solid': Tk's solid
        # relief paints a black frame that reads as heavy against a dark fill.
        label.pack(padx=1, pady=1, ipadx=8, ipady=6)

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def window_bg():
    """The current CTk window fill as a ``#rrggbb`` string, for painting legacy tk widgets.

    Reads the live theme rather than a constant so it tracks nlp_suite_theme.json and the appearance
    mode. Falls back to the light-mode default if CTk's theme is not loaded (headless tests).
    """
    try:
        color = ctk.ThemeManager.theme["CTk"]["fg_color"]
    except Exception:
        return "#f7f7f8"
    if isinstance(color, (list, tuple)):
        index = 1 if str(ctk.get_appearance_mode()).lower() == "dark" else 0
        color = color[index]
    return color


# Plain-tk widgets left over from the pre-CTk GUIs (the logo holder, the release label, the
# introduction paragraph, the nav/RUN-CLOSE container frames) default to the *platform's* button
# face -- roughly #ececec on macOS. That was invisible against the old gray92 window; against the
# lightened near-white ground of the CTk theme it reads as a set of grey plates floating on white.
# ``normalize_legacy_backgrounds`` repaints them to the themed window fill.
#
# Only widgets still sitting at the platform default are touched, identified by comparing the
# resolved RGB of their current background against the root's own default. A widget any call site
# deliberately colored (a red flag label, a white text field, the dark tooltip card) differs from
# that default and is left exactly as it is.
_LEGACY_BG_CLASSES = frozenset({"Label", "Frame", "Canvas", "Checkbutton", "Radiobutton", "Toplevel"})


def normalize_legacy_backgrounds(root):
    """Repaint default-background legacy tk widgets under *root* to the themed window fill.

    Walks the whole widget tree; CTk widgets are skipped (they are themed already, and their
    ``configure`` does not take a tk ``background``). Best-effort: any widget that refuses the
    option is left alone rather than raising into GUI construction.
    """
    target = window_bg()
    try:
        default_rgb = root.winfo_rgb(root.cget("background"))
        target_rgb = root.winfo_rgb(target)
    except Exception:
        return 0

    repainted = 0
    stack = [root]
    while stack:
        widget = stack.pop()
        try:
            stack.extend(widget.winfo_children())
        except Exception:
            continue
        if isinstance(widget, ctk.CTkBaseClass) or widget.winfo_class() not in _LEGACY_BG_CLASSES:
            continue
        try:
            current = widget.winfo_rgb(widget.cget("background"))
        except Exception:
            continue
        if current != default_rgb or current == target_rgb:
            continue
        try:
            widget.configure(background=target)
            repainted += 1
        except tk.TclError:
            pass
    return repainted


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
    candidates.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nlp_suite_theme.json")
    )
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
        warnings.warn(
            "nlp_suite_theme.json not found; falling back to the stock 'blue' theme.",
            stacklevel=2,
        )
        ctk.set_default_color_theme("blue")
    try:
        ctk.set_appearance_mode(appearance_mode)
    except Exception:
        pass
    _initialized = True
