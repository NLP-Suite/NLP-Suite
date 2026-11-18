"""Shape of Stories opens without an "Input directory error".

The GUI ran its I/O check when it opened. With its default options (data reduction ticked, Sentiment analysis
not) and the download's sample folder of txt files, that check warned at once that the folder "does not
contain any csv files", before the user had chosen anything. The same check still runs at RUN and when
Sentiment analysis is ticked.
"""

import ast
import os

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _module_level_calls(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return [
        node.lineno
        for node in tree.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == name
    ]


def test_no_io_check_when_the_window_opens():
    assert _module_level_calls(os.path.join(_SRC, "shape_of_stories_main.py"), "check_IO_requirements") == []


def test_run_still_checks_the_io():
    source = open(os.path.join(_SRC, "shape_of_stories_main.py"), encoding="utf-8").read()
    run = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "run")
    calls = [n.func.id for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "check_IO_requirements" in calls
