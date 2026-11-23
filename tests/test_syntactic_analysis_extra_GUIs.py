"""Syntactic analysis: each entry of the "GUIs available for more analyses" menu opens one GUI, the right one.

The menu callback matched "Ngrams", which is not in "N-grams & Co-Occurrences (Open GUI)", so that GUI never
opened, and matched "Corpus" in both "Corpus statistics" and "Corpus Profiler", so the profiler opened two GUIs.
"""

import ast
import os

import syntactic_analysis_util

MAIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "syntactic_analysis_ALL_main.py"
)


def _menu_entries():
    with open(MAIN, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "OptionMenu"
            and len(node.args) > 2
            and isinstance(node.args[1], ast.Name)
            and node.args[1].id == "extra_GUIs_menu_var"
        ):
            return [a.value for a in node.args[2:] if isinstance(a, ast.Constant)]
    raise AssertionError("extra_GUIs_menu not found")


def test_each_menu_entry_opens_one_existing_GUI():
    entries = _menu_entries()
    assert entries
    for entry in entries:
        script = syntactic_analysis_util.extra_GUI_script(entry)
        assert script, entry
        assert os.path.isfile(os.path.join(os.path.dirname(MAIN), script)), script


def test_the_right_GUIs():
    assert (
        syntactic_analysis_util.extra_GUI_script("N-grams & Co-Occurrences (Open GUI)")
        == "NGrams_CoOccurrences_main.py"
    )
    assert syntactic_analysis_util.extra_GUI_script("Corpus Profiler (Open GUI)") == "corpus_profiler_main.py"
    assert syntactic_analysis_util.extra_GUI_script("Corpus statistics (Open GUI)") == "statistics_txt_main.py"
    assert syntactic_analysis_util.extra_GUI_script("") == ""
