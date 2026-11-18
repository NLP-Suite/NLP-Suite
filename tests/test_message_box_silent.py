"""NLP_SILENT also covers the timed alerts ("Started running ...") and the Yes/No reminders.

They go through GUI_IO_util.message_box_widget, which opened a window and waited out its countdown even in
silent mode, so a headless sweep showed a popup at every RUN and paused for it.
"""

import importlib.util
import os
from unittest import mock

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


@pytest.fixture(scope="module")
def gui_io():
    pytest.importorskip("tkinter")
    # conftest replaces GUI_IO_util with a stub; load the real file under another name
    spec = importlib.util.spec_from_file_location("GUI_IO_util_real", os.path.join(_SRC, "GUI_IO_util.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("button_type", ["OK", "Yes-No", "Yes-No-Cancel"])
def test_silent_mode_prints_and_opens_no_window(gui_io, monkeypatch, capsys, button_type):
    monkeypatch.setenv("NLP_SILENT", "1")
    with mock.patch.object(gui_io.tk, "Toplevel", side_effect=AssertionError("opened a window")):
        answer = gui_io.message_box_widget(None, "Analysis start", "Started running X at 9:30.", button_type, 2000)
    assert answer == ""  # what a timeout answers: a reminder keeps its status
    assert "Started running X" in capsys.readouterr().out


def test_without_silent_mode_the_window_still_opens(gui_io, monkeypatch):
    monkeypatch.delenv("NLP_SILENT", raising=False)
    with mock.patch.object(gui_io.tk, "Toplevel", side_effect=RuntimeError("window")), pytest.raises(RuntimeError):
        gui_io.message_box_widget(None, "Analysis start", "Started running X.", "OK", 2000)
