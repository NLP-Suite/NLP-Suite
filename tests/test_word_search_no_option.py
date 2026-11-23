"""Word search: RUN with no search option ticked warns (#1767).

run() tested `extra_GUIs_var == False` on the tkinter IntVar itself, which is never equal to False, so the "No search
options have been selected" warning could never show. run() is pulled out of the GUI module and executed with the
widgets mocked (a mock, like an IntVar, is not == False; its .get() returns the value).
"""

import ast
import builtins
import os
from unittest.mock import MagicMock

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


class _Namespace(dict):
    def __missing__(self, name):
        if hasattr(builtins, name):
            return getattr(builtins, name)
        self[name] = MagicMock()
        return self[name]


def _var(value):
    var = MagicMock()
    var.get.return_value = value
    return var


def test_run_with_nothing_selected_warns_and_stops():
    source = open(os.path.join(SRC, "file_search_byWord_main.py"), encoding="utf-8").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "run")
    namespace = _Namespace(
        extra_GUIs_var=_var(0),
        search_by_dictionary_var=_var(0),
        search_by_keyword_var=_var(0),
    )
    exec(compile(ast.Module(body=[node], type_ignores=[]), "file_search_byWord_main.py", "exec"), namespace)
    namespace["run"]()
    mb = namespace["mb"]
    assert mb.showwarning.call_count == 1
    assert "No search options" in str(mb.showwarning.call_args)
    assert namespace["file_search_byWord_util"].search_sentences_documents.call_count == 0
