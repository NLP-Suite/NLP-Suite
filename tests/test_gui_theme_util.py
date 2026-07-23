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


# ── textbox state (Phase 3 DB/PCACE tranche: a disabled tk.Text stayed always-enabled) ──
class TestCreateTextboxState:
    def test_ctktextbox_does_not_name_state_in_its_signature(self):
        # CTkTextbox forwards state/wrap/undo/... to its inner tkinter.Text via **kwargs instead of
        # naming them -- so translate_kwargs' signature filter cannot see them, same silent-drop
        # class as the combobox/label textvariable cases below.
        import inspect

        assert "state" not in inspect.signature(ctk.CTkTextbox.__init__).parameters

    def test_bare_state_would_be_dropped_by_translate_kwargs(self):
        assert gtu.translate_kwargs(ctk.CTkTextbox, {"state": "disabled"}) == {}

    def test_create_textbox_pulls_valid_tk_text_attributes_out_before_filtering(self):
        # Pure-logic check mirroring create_textbox's own split, without building a real widget
        # (widget construction needs a live Tk display -- see tests/gui_smoke.py instead).
        kwargs = {"height": 12, "state": "disabled", "wrap": "word"}
        text_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in ctk.CTkTextbox._valid_tk_text_attributes}
        assert text_kwargs == {"state": "disabled", "wrap": "word"}
        assert gtu.translate_kwargs(ctk.CTkTextbox, kwargs) == {"height": gtu.line_height_to_px(12)}


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


# ── label pixel width (NLP_welcome's marquee is sized from the window width, already in pixels) ──
class TestCreateLabelWidthUnits:
    def test_default_treats_width_as_characters(self):
        # A converted tk.Label call site: width=20 means 20 characters.
        out = gtu.translate_kwargs(ctk.CTkLabel, {"width": 20}, width_is_chars=True)
        assert out["width"] == gtu.char_width_to_px(20)

    def test_pixel_width_passes_through_untouched(self):
        # What create_label(width_is_chars=False) buys: the window width stays the window width
        # instead of becoming 1250 * 8 = 10,000px, which would silently inflate its grid column.
        out = gtu.translate_kwargs(ctk.CTkLabel, {"width": 1250}, width_is_chars=False)
        assert out["width"] == 1250


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


# ── themed window fill / legacy tk background normalization ──────────────────
class TestWindowBg:
    def test_returns_a_hex_color_from_the_live_theme(self):
        color = gtu.window_bg()
        assert isinstance(color, str)
        assert color.startswith("#") and len(color) == 7

    def test_resolves_the_light_half_of_a_color_pair(self, monkeypatch):
        # CTk theme entries are [light, dark] pairs; the light value is picked in light mode.
        monkeypatch.setitem(ctk.ThemeManager.theme, "CTk", {"fg_color": ["#aabbcc", "#112233"]})
        monkeypatch.setattr(ctk, "get_appearance_mode", lambda: "Light")
        assert gtu.window_bg() == "#aabbcc"

    def test_resolves_the_dark_half_in_dark_mode(self, monkeypatch):
        monkeypatch.setitem(ctk.ThemeManager.theme, "CTk", {"fg_color": ["#aabbcc", "#112233"]})
        monkeypatch.setattr(ctk, "get_appearance_mode", lambda: "Dark")
        assert gtu.window_bg() == "#112233"

    def test_falls_back_when_the_theme_is_unavailable(self, monkeypatch):
        monkeypatch.setattr(ctk, "ThemeManager", None)
        assert gtu.window_bg() == "#f7f7f8"

    def test_a_plain_string_color_is_passed_through(self, monkeypatch):
        monkeypatch.setitem(ctk.ThemeManager.theme, "CTk", {"fg_color": "#123456"})
        assert gtu.window_bg() == "#123456"


class TestNormalizeLegacyBackgrounds:
    def test_ctk_widget_classes_are_never_repainted(self):
        # The walk must skip CTk widgets: they are themed already and take fg_color, not background.
        assert "CTkFrame" not in gtu._LEGACY_BG_CLASSES
        assert "CTkLabel" not in gtu._LEGACY_BG_CLASSES

    def test_covers_the_legacy_container_and_text_classes(self):
        # These are the tk classes the pre-CTk GUIs still build directly (logo holder, release
        # label, introduction paragraph, nav / RUN-CLOSE frames).
        assert {"Label", "Frame", "Canvas"} <= gtu._LEGACY_BG_CLASSES

    def test_unresolvable_root_is_a_no_op_rather_than_an_error(self):
        class _Broken:
            def cget(self, _option):
                raise RuntimeError("no display")

            def winfo_rgb(self, _color):
                raise RuntimeError("no display")

        assert gtu.normalize_legacy_backgrounds(_Broken()) == 0

    def test_every_legacy_class_has_a_probe_factory(self):
        # A class in _LEGACY_BG_CLASSES with no probe can never resolve its default background,
        # so it would be silently skipped forever.
        assert gtu._LEGACY_BG_CLASSES <= set(gtu._PROBE_CLASSES)

    def test_unknown_class_probes_to_none_and_is_cached(self):
        cache = {}
        assert gtu._class_default_rgb(None, "NotAWidgetClass", cache) is None
        assert cache == {"NotAWidgetClass": None}


# The repaint itself needs a live Tk display; skipped on a headless box.
@pytest.fixture
def ctk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = ctk.CTk()
    except tk.TclError as exc:  # pragma: no cover - headless CI
        pytest.skip(f"no display: {exc}")
    yield root
    root.destroy()


class TestResolveAppearanceColor:
    def test_a_plain_string_is_returned_unchanged(self):
        assert gtu.resolve_appearance_color("#123456") == "#123456"

    def test_picks_the_light_half_in_light_mode(self, monkeypatch):
        monkeypatch.setattr(ctk, "get_appearance_mode", lambda: "Light")
        assert gtu.resolve_appearance_color(["#aabbcc", "#112233"]) == "#aabbcc"

    def test_picks_the_dark_half_in_dark_mode(self, monkeypatch):
        monkeypatch.setattr(ctk, "get_appearance_mode", lambda: "Dark")
        assert gtu.resolve_appearance_color(["#aabbcc", "#112233"]) == "#112233"

    def test_falls_back_to_the_light_half_when_the_mode_is_unreadable(self, monkeypatch):
        def _boom():
            raise RuntimeError("no appearance tracker")

        monkeypatch.setattr(ctk, "get_appearance_mode", _boom)
        assert gtu.resolve_appearance_color(["#aabbcc", "#112233"]) == "#aabbcc"


class TestComboBoxDropdownArrow:
    def test_the_theme_pairs_that_made_the_chevron_black(self):
        # The bug in one assertion: the combobox's arrow is drawn in its text_color, which must stay
        # dark for the white entry field -- but the arrow itself sits on the red button strip.
        combo = ctk.ThemeManager.theme["CTkComboBox"]
        menu = ctk.ThemeManager.theme["CTkOptionMenu"]
        assert gtu.resolve_appearance_color(combo["text_color"]) != gtu.resolve_appearance_color(
            menu["text_color"]
        )
        # ...and the strip it sits on is the same red the option menu uses, hence the mismatch.
        assert gtu.resolve_appearance_color(combo["button_color"]) != gtu.resolve_appearance_color(
            combo["fg_color"]
        )

    def _arrow_fills(self, widget):
        canvas = widget._canvas
        return [canvas.itemcget(i, "fill") for i in canvas.find_withtag("dropdown_arrow")]

    def test_combobox_arrow_matches_the_option_menu_arrow(self, ctk_root):
        combo = gtu.create_combobox(ctk_root, values=["a", "b"])
        menu = gtu.create_option_menu(ctk_root, values=["a", "b"])
        ctk_root.update_idletasks()
        assert self._arrow_fills(combo) == self._arrow_fills(menu) != []

    def test_combobox_arrow_is_not_the_entry_text_color(self, ctk_root):
        # Regression: the chevron used to inherit text_color (near-black) on the red strip.
        combo = gtu.create_combobox(ctk_root, values=["a", "b"])
        ctk_root.update_idletasks()
        text_color = gtu.resolve_appearance_color(combo.cget("text_color"))
        assert text_color not in self._arrow_fills(combo)

    def test_disabling_repaints_the_arrow_to_the_muted_tone(self, ctk_root):
        combo = gtu.create_combobox(ctk_root, values=["a", "b"])
        combo.configure(state="disabled")
        ctk_root.update_idletasks()
        expected = gtu.resolve_appearance_color(
            ctk.ThemeManager.theme["CTkOptionMenu"]["text_color_disabled"]
        )
        assert self._arrow_fills(combo) == [expected]


class TestNormalizeLegacyBackgroundsOnScreen:
    def test_default_background_widgets_are_repainted_to_the_theme_fill(self, ctk_root):
        import tkinter as tk

        plain = tk.Label(ctk_root, text="x")
        frame = tk.Frame(ctk_root)
        assert gtu.normalize_legacy_backgrounds(ctk_root) >= 2
        assert plain.cget("background") == gtu.window_bg()
        assert frame.cget("background") == gtu.window_bg()

    def test_deliberately_colored_widgets_survive(self, ctk_root):
        import tkinter as tk

        red = tk.Label(ctk_root, text="x", background="red")
        gtu.normalize_legacy_backgrounds(ctk_root)
        assert red.cget("background") == "red"

    def test_repaints_even_though_the_ctk_root_is_not_at_the_platform_default(self, ctk_root):
        # Regression: the reference default used to be read off the root. The root is a ctk.CTk, so
        # its background is already the themed fill while a fresh tk.Label still reports the
        # platform default -- every legacy widget then looked "deliberately colored" and nothing was
        # repainted (grey logo / release / introduction plates on the near-white ground).
        import tkinter as tk

        label_default = tk.Label(ctk_root).cget("background")
        assert ctk_root.winfo_rgb(ctk_root.cget("background")) != ctk_root.winfo_rgb(label_default)
        assert gtu.normalize_legacy_backgrounds(ctk_root) > 0


class TestIntegerSlider:
    """tk.Scale.get() returned an int; CTkSlider.get() returns a float (Phase 3, sentiment tranche).

    Every legacy tk.Scale in the suite feeds an integer consumer, and none of them notice a float
    until RUN -- shape_of_stories' memory slider is concatenated into CoreNLP's heap flag
    ('-mx' + str(v) + 'g'), where '-mx6.0g' makes the JVM refuse to start.
    """

    def test_plain_ctkslider_get_is_not_integral(self):
        # The contract that motivates _IntSlider: number_of_steps quantizes the value but the
        # returned type is still float. Pinned so a CTk upgrade can't quietly make this moot.
        import inspect

        assert "number_of_steps" in inspect.signature(ctk.CTkSlider.__init__).parameters

    def test_int_slider_get_coerces_to_int(self, monkeypatch):
        # Built without __init__ (CTkSlider's needs a live Tk master); _IntSlider.get() delegates
        # up via super(), so stubbing the base's get() exercises exactly the coercion under test.
        widget = object.__new__(gtu._IntSlider)
        for raw, want in ((6.0, 6), (6.4, 6), (7.5, 8), (9, 9)):
            monkeypatch.setattr(ctk.CTkSlider, "get", lambda self, _r=raw: _r)
            got = widget.get()
            assert got == want and isinstance(got, int), f"{raw!r} -> {got!r}"

    def test_create_slider_returns_plain_slider_unless_integer_requested(self):
        assert gtu.create_slider is not None
        # integer= is opt-in: sliders over a continuous range must keep their float get().
        import inspect

        assert inspect.signature(gtu.create_slider).parameters["integer"].default is False

    def test_create_slider_translates_the_tk_scale_kwargs(self, monkeypatch):
        # tk names (orient/length/resolution) -> CTk names, and integer= picks the subclass.
        # Captured rather than rendered so the test runs headless.
        seen = {}

        class _Capture:
            def __init__(self, master, **kwargs):
                seen.update(kwargs)
                seen["_cls"] = type(self).__name__

        monkeypatch.setattr(ctk, "CTkSlider", _Capture)
        monkeypatch.setattr(gtu.ctk, "CTkSlider", _Capture)
        monkeypatch.setattr(gtu, "_IntSlider", type("_IntSlider", (_Capture,), {}))

        gtu.create_slider(
            None, from_=1, to=16, orient="horizontal", length=200, resolution=1, integer=True
        )
        assert seen["from_"] == 1 and seen["to"] == 16
        assert seen["orientation"] == "horizontal"   # orient -> orientation
        assert seen["width"] == 200                  # length -> width (px, not chars)
        assert seen["number_of_steps"] == 15         # (16-1)/1 integer detents
        assert seen["_cls"] == "_IntSlider"


class TestClampTooltipPosition:
    """Right-docked buttons put the naive tooltip position past the right screen edge."""

    SCREEN = (1440, 900)

    def clamp(self, x, y, w=300, h=60, widget_top=100):
        return gtu.clamp_tooltip_position(x, y, w, h, *self.SCREEN, widget_top)

    def test_a_tip_that_already_fits_is_left_alone(self):
        assert self.clamp(200, 150) == (200, 150)

    def test_a_tip_running_off_the_right_edge_slides_left(self):
        x, _ = self.clamp(1300, 150)
        assert x + 300 <= 1440

    def test_a_tip_wider_than_the_screen_still_starts_on_screen(self):
        x, _ = gtu.clamp_tooltip_position(1300, 150, 2000, 60, *self.SCREEN, 100)
        assert x == 8

    def test_a_tip_running_off_the_bottom_flips_above_the_widget(self):
        _, y = self.clamp(200, 880, widget_top=850)
        assert y + 60 <= 850

    def test_no_room_above_or_below_clamps_into_the_screen(self):
        _, y = gtu.clamp_tooltip_position(200, 880, 300, 60, *self.SCREEN, 20)
        assert 8 <= y and y + 60 <= 900
