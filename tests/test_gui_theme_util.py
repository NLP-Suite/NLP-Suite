"""Unit tests for GUI_theme_util -- the CustomTkinter compatibility layer (CTk migration Phase 1).

Covers the *pure* logic: the character/line -> pixel width translation, the tk-kwargs -> CTk-kwargs
translation (validated against the real CustomTkinter 6.0.0 class signatures via introspection, no
display needed), and the ``set_values`` menu-repopulation helper. Widget construction and the
ToolTip surface need a live Tk display and are exercised by tests/gui_smoke.py, not here.

customtkinter is import-skipped so the suite still collects on a box without it installed.
"""

import pytest

ctk = pytest.importorskip("customtkinter")

import GUI_theme_util as gtu  # noqa: E402  (import after importorskip on purpose)


# ── char_width_to_px ─────────────────────────────────────────────────────────
class TestCharWidthToPx:
    def test_basic_chars_to_pixels(self):
        assert gtu.char_width_to_px(10) == 10 * gtu._PX_PER_CHAR

    def test_custom_px_per_char_and_padding(self):
        assert gtu.char_width_to_px(5, px_per_char=10, padding=4) == 54

    @pytest.mark.parametrize("bad", [0, -3, None, "", "abc"])
    def test_missing_or_nonpositive_returns_none(self, bad):
        assert gtu.char_width_to_px(bad) is None

    def test_large_char_width_still_multiplied(self):
        # No magnitude cutoff: a wide legacy entry (e.g. a 115-char file-path field) must be scaled
        # to pixels like any other char width, not passed through as ~115px. Pixel-holding callers
        # opt out via width_is_chars=False in translate_kwargs, not via a magic size threshold.
        assert gtu.char_width_to_px(115) == 115 * gtu._PX_PER_CHAR

    def test_numeric_string_is_accepted(self):
        assert gtu.char_width_to_px("12") == 12 * gtu._PX_PER_CHAR


# ── line_height_to_px ────────────────────────────────────────────────────────
class TestLineHeightToPx:
    def test_single_line_floors_to_min_widget_px(self):
        assert gtu.line_height_to_px(1) == gtu._MIN_WIDGET_PX

    def test_two_line_button_taller_than_min(self):
        assert gtu.line_height_to_px(2) == max(gtu._MIN_WIDGET_PX, 2 * gtu._PX_PER_LINE)

    @pytest.mark.parametrize("bad", [0, -1, None, "x"])
    def test_missing_or_nonpositive_returns_none(self, bad):
        assert gtu.line_height_to_px(bad) is None

    def test_large_line_count_still_multiplied(self):
        # Same rule as width: no magnitude cutoff. Pixel-holding heights bypass via
        # height_is_lines=False (see test_entry_height_not_line_translated_when_flag_off).
        assert gtu.line_height_to_px(20) == max(gtu._MIN_WIDGET_PX, 20 * gtu._PX_PER_LINE)


# ── translate_kwargs (against real CTk 6.0.0 signatures) ─────────────────────
class TestTranslateKwargs:
    def test_foreground_and_fg_rename_to_text_color(self):
        assert gtu.translate_kwargs(ctk.CTkButton, {"foreground": "red"}) == {"text_color": "red"}
        assert gtu.translate_kwargs(ctk.CTkButton, {"fg": "red"}) == {"text_color": "red"}

    def test_width_translated_to_pixels(self):
        out = gtu.translate_kwargs(ctk.CTkEntry, {"width": 30})
        assert out == {"width": 30 * gtu._PX_PER_CHAR}

    def test_height_translated_to_pixels(self):
        out = gtu.translate_kwargs(ctk.CTkButton, {"height": 2})
        assert out["height"] == max(gtu._MIN_WIDGET_PX, 2 * gtu._PX_PER_LINE)

    def test_entry_height_not_line_translated_when_flag_off(self):
        # create_entry passes height_is_lines=False; a raw pixel height must survive unchanged.
        out = gtu.translate_kwargs(ctk.CTkEntry, {"height": 40}, height_is_lines=False)
        assert out["height"] == 40

    def test_width_not_char_translated_when_flag_off(self):
        # The pixel escape hatch: a CTk-aware caller passes width_is_chars=False and its raw pixel
        # width must survive unmultiplied (this replaces the old magnitude-guess passthrough).
        out = gtu.translate_kwargs(ctk.CTkEntry, {"width": 920}, width_is_chars=False)
        assert out["width"] == 920

    def test_zero_width_is_dropped_not_zeroed(self):
        # width<=0 -> None -> drop, so CTk keeps its own default sizing rather than a 0px widget.
        assert "width" not in gtu.translate_kwargs(ctk.CTkButton, {"width": 0})

    def test_native_tk_chrome_dropped(self):
        out = gtu.translate_kwargs(
            ctk.CTkButton,
            {
                "relief": "raised",
                "bd": 2,
                "borderwidth": 2,
                "bg": "white",
                "highlightthickness": 0,
                "activebackground": "gray",
            },
        )
        assert out == {}

    def test_unsupported_ctk_kwarg_dropped(self):
        # CTk 6.0.0 CTkLabel has no `justify`; it must be dropped, not passed to the constructor.
        assert "justify" not in gtu.translate_kwargs(ctk.CTkLabel, {"justify": "left"})
        # ...but CTkComboBox *does* accept justify, so there it survives.
        assert gtu.translate_kwargs(ctk.CTkComboBox, {"justify": "left"}) == {"justify": "left"}

    def test_accepted_passthrough_preserved(self):
        out = gtu.translate_kwargs(ctk.CTkButton, {"text": "RUN", "state": "disabled"})
        assert out == {"text": "RUN", "state": "disabled"}

    def test_text_color_wins_over_dropped_bg(self):
        out = gtu.translate_kwargs(ctk.CTkButton, {"foreground": "red", "bg": "white"})
        assert out == {"text_color": "red"}


# ── set_values ───────────────────────────────────────────────────────────────
class _FakeMenu:
    def __init__(self):
        self.configured = None
        self.selected = None

    def configure(self, **kwargs):
        self.configured = kwargs

    def set(self, value):
        self.selected = value


class TestSetValues:
    def test_configures_values_and_returns_list(self):
        w = _FakeMenu()
        result = gtu.set_values(w, ("a", "b", "c"))
        assert w.configured == {"values": ["a", "b", "c"]}
        assert result == ["a", "b", "c"]
        assert w.selected is None  # no default -> selection untouched

    def test_default_selects_item(self):
        w = _FakeMenu()
        gtu.set_values(w, ["x", "y"], default="x")
        assert w.selected == "x"


# ── set_char_width ───────────────────────────────────────────────────────────
class TestSetCharWidth:
    def test_translates_chars_to_pixels(self):
        w = _FakeMenu()
        px = gtu.set_char_width(w, 10)
        assert px == gtu.char_width_to_px(10)
        assert w.configured == {"width": px}

    def test_entry_gets_the_same_chrome_allowance_as_create_entry(self):
        entry = ctk.CTkEntry.__new__(ctk.CTkEntry)  # no display needed; isinstance is all that matters
        entry.configure = lambda **kwargs: recorded.update(kwargs)
        recorded = {}
        px = gtu.set_char_width(entry, 4)
        assert px == gtu.char_width_to_px(4, padding=gtu._ENTRY_PADDING_PX)
        assert recorded == {"width": px}

    @pytest.mark.parametrize("bad", [None, 0, -3, "wide"])
    def test_unusable_width_leaves_the_widget_alone(self, bad):
        w = _FakeMenu()
        assert gtu.set_char_width(w, bad) is None
        assert w.configured is None


# ── _accepted_params sanity ──────────────────────────────────────────────────
def test_accepted_params_excludes_self_and_varargs():
    params = gtu._accepted_params(ctk.CTkButton)
    assert "self" not in params and "master" not in params
    assert "text" in params and "command" in params


# ── the theme JSON loads, and the default fill is the brand RED (regression) ──
# Two things this guards:
#   1. CTk's load_theme requires every top-level key to be a dict (it does theme[key].keys()); a
#      stray "_comment" string key raised AttributeError and silently fell back to CTk's blue theme,
#      shipping the whole suite in blue. We confirm the file's own colors reached ThemeManager.
#   2. The default (enabled) widget fill must be the brand red: the theme encodes red = ACTIVE,
#      grey = INACTIVE (see plan §0 and the pilot-2 note in §4).
_CTK_BLUE_FALLBACK = {"#3B8ED0", "#1F6AA5"}  # CTk's stock "blue" CTkButton fg -- the bug's fingerprint


def test_theme_json_loads_red_default_not_blue_fallback():
    import json
    import os

    theme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "nlp_suite_theme.json")
    assert os.path.isfile(theme_path), "nlp_suite_theme.json must ship in src/"

    # Every top-level value must be a dict, or CTk's load_theme raises on theme[key].keys().
    data = json.loads(open(theme_path, encoding="utf-8").read())
    non_dict = [k for k, v in data.items() if not isinstance(v, dict)]
    assert not non_dict, f"top-level theme keys must all be dicts; offenders: {non_dict}"

    # Load for real through CTk and confirm the FILE's colors reached ThemeManager (not blue fallback).
    ctk.set_default_color_theme(theme_path)
    from customtkinter import ThemeManager

    for cls in ("CTkButton", "CTkOptionMenu"):
        loaded_fg = ThemeManager.theme[cls]["fg_color"]
        assert loaded_fg == data[cls]["fg_color"], f"{cls} fg didn't load from the file (blue fallback?)"
        assert not _CTK_BLUE_FALLBACK.intersection(loaded_fg), f"{cls} is on the blue fallback"
        # The premise: red = ACTIVE, so an enabled control's default fill is the brand red.
        assert gtu.NLP_SUITE_ACCENT in loaded_fg, f"{cls} default fill must be the brand red"


# ── the accent is red, and the inactive greys are distinct from it ──
def test_accent_is_brand_red_and_distinct_from_the_inactive_greys():
    assert gtu.NLP_SUITE_ACCENT in gtu._ACCENT_FG
    # "inactive" must never be confusable with "active": disabled fill, the muted
    # nothing-available fill, and the accent are three distinct values.
    assert gtu.NLP_SUITE_ACCENT not in gtu._DISABLED_FILL
    assert gtu._ACCENT_FG != gtu._MUTED_FG
    assert gtu.NLP_SUITE_ACCENT != gtu._MUTED_FG


# ── grey means inactive: the fill repaint CTk does not do by itself ──
class _Recorder:
    """Stand-in for a CTk widget: records the color options configure() applies."""

    def __init__(self, **colors):
        self.colors = dict(colors)

    def configure(self, require_redraw=False, **kwargs):
        self.colors.update(kwargs)

    def cget(self, attribute_name):
        return self.colors.get(attribute_name)


class _FakeButton(gtu._StateFillMixin, _Recorder):
    # At runtime _StateFillMixin's base is `object`, so super() lands on _Recorder here -- letting
    # the state logic be exercised headlessly, with no display and no real CTk widget.
    _STATE_FILL_KEYS = ("fg_color", "border_color")


class TestStateFillMixin:
    def test_disabled_at_construction_is_painted_grey(self):
        w = _FakeButton(fg_color=gtu._ACCENT_FG, border_color="#8a0808", state="disabled")
        assert w.colors["fg_color"] == gtu._DISABLED_FILL
        assert w.colors["border_color"] == gtu._DISABLED_BORDER

    def test_enabled_widget_keeps_its_theme_fill(self):
        w = _FakeButton(fg_color=gtu._ACCENT_FG, border_color="#8a0808")
        assert w.colors["fg_color"] == gtu._ACCENT_FG

    def test_configure_disabled_then_normal_round_trips(self):
        # The choreography in §5.4: GUIs flip state constantly, and re-enabling must restore the
        # ORIGINAL fill -- including a call site's custom color, not a hardcoded theme default.
        custom = ["#123456", "#123456"]
        w = _FakeButton(fg_color=custom, border_color="#654321")
        w.configure(state="disabled")
        assert w.colors["fg_color"] == gtu._DISABLED_FILL
        w.configure(state="normal")
        assert w.colors["fg_color"] == custom
        assert w.colors["border_color"] == "#654321"

    def test_configure_without_state_does_not_repaint(self):
        w = _FakeButton(fg_color=gtu._ACCENT_FG, border_color="#8a0808")
        w.configure(state="disabled")
        w.configure(text="new label")
        assert w.colors["fg_color"] == gtu._DISABLED_FILL, "a non-state configure must not re-enable"


# ── the CTk widget contracts that broke legacy tk idioms during the Phase 2 pilot ──
# These pin behaviours of the REAL customtkinter that a tk->CTk conversion trips over, and that
# tests/gui_smoke.py's hand-written CTk stub deliberately reproduces. If a CustomTkinter upgrade
# changes any of them, these fail here -- telling us the smoke stub has drifted from reality --
# instead of the smoke suite quietly going blind to a whole class of conversion bug.
class TestCTkLegacyIdiomContracts:
    def test_config_raises_so_conversions_must_use_configure(self):
        # ~50 legacy .config(...) call sites per GUI; CTk implements config() only to raise.
        with pytest.raises(AttributeError, match="configure"):
            ctk.CTkButton.config(object(), state="disabled")

    def test_configure_first_positional_is_require_redraw(self):
        # This is why `widget['values'] = [...]` SILENTLY no-ops instead of raising: tkinter's
        # __setitem__ does configure({key: value}), landing the dict on require_redraw.
        import inspect

        for cls in (ctk.CTkComboBox, ctk.CTkOptionMenu):
            params = list(inspect.signature(cls.configure).parameters)
            assert params[1] == "require_redraw", f"{cls.__name__}.configure signature changed"

    def test_set_values_is_the_supported_repopulation_path(self):
        # The positive counterpart: configure(values=...) is a real keyword on both menu classes.
        import inspect

        for cls in (ctk.CTkComboBox, ctk.CTkOptionMenu):
            assert "values" in inspect.signature(cls.__init__).parameters

    def test_combobox_takes_variable_not_textvariable(self):
        # Phase 2 pilot 2: every legacy ttk.Combobox binds its var as `textvariable=`, but
        # CTkComboBox only has `variable=` -- so translate_kwargs would drop it SILENTLY, leaving a
        # widget whose .trace callbacks never fire. create_combobox renames it; this pins the CTk
        # side of that contract (and that CTkCheckBox keeps BOTH names with different meanings,
        # which is why the rename can't live in the global _RENAME table).
        import inspect

        combobox_params = inspect.signature(ctk.CTkComboBox.__init__).parameters
        assert "variable" in combobox_params
        assert "textvariable" not in combobox_params

        checkbox_params = inspect.signature(ctk.CTkCheckBox.__init__).parameters
        assert {"variable", "textvariable"} <= set(checkbox_params)


class TestCreateCombobox:
    def test_textvariable_is_renamed_to_variable(self):
        out = gtu.translate_kwargs(ctk.CTkComboBox, {"variable": "VAR", "width": 80})
        assert out["variable"] == "VAR"

    def test_bare_textvariable_would_be_dropped_by_translate_kwargs(self):
        # The failure create_combobox exists to prevent: no rename -> no variable at all.
        assert gtu.translate_kwargs(ctk.CTkComboBox, {"textvariable": "VAR"}) == {}


# ── label textvariable (Phase 2 pilot 3: path labels rendered the literal "CTkLabel") ──
class TestCreateLabelTextvariable:
    def test_ctklabel_does_not_name_textvariable_in_its_signature(self):
        # The CTk contract create_label works around: CTkLabel *supports* textvariable, but only by
        # forwarding it to its inner tk.Label out of **kwargs -- so a signature-based filter like
        # translate_kwargs cannot see it. Same silent-drop class as the combobox rename above.
        import inspect

        assert "textvariable" not in inspect.signature(ctk.CTkLabel.__init__).parameters

    def test_bare_textvariable_would_be_dropped_by_translate_kwargs(self):
        assert gtu.translate_kwargs(ctk.CTkLabel, {"textvariable": "VAR"}) == {}

    def test_ctklabel_placeholder_text_is_not_empty(self):
        # Why create_label must blank `text` when a variable is bound: CTk's default is a visible
        # placeholder, and it is applied before the tk attributes, so it would win on screen.
        import inspect

        default = inspect.signature(ctk.CTkLabel.__init__).parameters["text"].default
        assert default and default != ""


# ── entry width chrome allowance (Phase 2 pilot: a 4-char box clipped "100" to "10C") ──
class TestEntryWidthPadding:
    def test_translate_kwargs_adds_width_padding(self):
        out = gtu.translate_kwargs(ctk.CTkEntry, {"width": 4}, height_is_lines=False, width_padding=14)
        assert out["width"] == gtu.char_width_to_px(4) + 14

    def test_width_padding_defaults_to_zero_for_other_widgets(self):
        # Only entries opt in; a button's width translation must be unchanged.
        assert gtu.translate_kwargs(ctk.CTkButton, {"width": 4})["width"] == gtu.char_width_to_px(4)

    def test_padding_is_not_applied_to_a_dropped_width(self):
        # A non-positive/non-numeric width still drops out entirely rather than becoming bare padding.
        assert "width" not in gtu.translate_kwargs(
            ctk.CTkEntry, {"width": 0}, height_is_lines=False, width_padding=14
        )
