"""GIS: renaming the 'Frequency of Locations' chart to ...LOCATIONS_found... must never stop the run.

The rename added 6 characters after the output path had been shortened; with a long (OneDrive) output folder
the new path passed Windows' 260-character limit and os.rename raised WinError 3, so no map was made (found
while checking the HW 4 tools). The function is pulled out of the source because the GIS modules import the GUI.
"""

import ast
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _rename():
    source = open(os.path.join(SRC, "GIS_pipeline_util.py"), encoding="utf-8-sig").read()
    namespace = {"os": os, "sys": sys}
    for node in ast.parse(source).body:
        names = [t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)]
        if getattr(node, "name", None) == "rename_found_locations_chart" or "WINDOWS_MAX_PATH" in names:
            exec(ast.get_source_segment(source, node), namespace)
    return namespace["rename_found_locations_chart"]


def test_renames_the_chart(tmp_path):
    chart = tmp_path / "NLP_GIS_LOCATIONS_bar.xlsx"
    chart.write_text("x")
    new = _rename()(str(chart))
    assert new == str(tmp_path / "NLP_GIS_LOCATIONS_found_bar.xlsx")
    assert os.path.isfile(new) and not chart.exists()


def test_keeps_the_name_when_the_new_path_would_be_too_long(tmp_path, monkeypatch):
    chart = tmp_path / "NLP_GIS_LOCATIONS_bar.xlsx"
    chart.write_text("x")
    monkeypatch.setattr(sys, "platform", "win32")
    limit = len(os.path.abspath(str(chart))) + 3  # the new name is 6 characters longer
    assert _rename()(str(chart), max_path=limit) == str(chart)
    assert chart.exists()


def test_keeps_the_name_when_the_rename_fails(tmp_path):
    missing = str(tmp_path / "gone" / "NLP_GIS_LOCATIONS_bar.xlsx")
    assert _rename()(missing) == missing  # no exception
