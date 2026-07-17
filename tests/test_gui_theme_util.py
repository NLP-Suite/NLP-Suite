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


# ── _accepted_params sanity ──────────────────────────────────────────────────
def test_accepted_params_excludes_self_and_varargs():
    params = gtu._accepted_params(ctk.CTkButton)
    assert "self" not in params and "master" not in params
    assert "text" in params and "command" in params


# ── the theme JSON actually loads and applies the accent (regression) ─────────
# CTk's load_theme requires every top-level key to be a dict (it does theme[key].keys()); a stray
# "_comment" string key raised AttributeError and silently fell back to CTk's blue theme, shipping
# the whole suite in blue. This test loads the real file and asserts the accent red is applied.
def test_theme_json_loads_and_applies_accent():
    import json
    import os

    theme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "nlp_suite_theme.json")
    assert os.path.isfile(theme_path), "nlp_suite_theme.json must ship in src/"

    # Every top-level value must be a dict, or CTk's load_theme raises on theme[key].keys().
    data = json.loads(open(theme_path, encoding="utf-8").read())
    non_dict = [k for k, v in data.items() if not isinstance(v, dict)]
    assert not non_dict, f"top-level theme keys must all be dicts; offenders: {non_dict}"

    # Load for real through CTk and confirm the brand red reached CTkButton (not the blue fallback).
    ctk.set_default_color_theme(theme_path)
    from customtkinter import ThemeManager

    button_fg = ThemeManager.theme["CTkButton"]["fg_color"]
    assert gtu.NLP_SUITE_ACCENT in button_fg, f"expected accent {gtu.NLP_SUITE_ACCENT} in {button_fg}"
