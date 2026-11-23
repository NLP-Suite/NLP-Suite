"""N-grams: "Character" is no longer offered, and asking for it says so instead of running nothing (#1763).

The character branch of NGrams_CoOccurrences_main.run was commented out, and statistics_txt_util's
compute_character_word_ngrams/get_ngramlist accept a wordgram flag but only ever build word N-grams, so with
"Character" selected RUN wrote nothing and said nothing. "Character" is out of the N-grams type menu, and run() warns
if the value reaches it anyway (an old setting, a script).

run() is pulled out of the GUI module and executed against a namespace whose missing names are mocks.
"""

import ast
import builtins
import os
from unittest.mock import MagicMock

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
SOURCE = open(os.path.join(SRC, "NGrams_CoOccurrences_main.py"), encoding="utf-8").read()


def _var(value):
    var = MagicMock()
    var.get.return_value = value
    return var


class _Namespace(dict):
    """Globals for run(): names not given are mocks; builtins stay builtins."""

    def __missing__(self, name):
        if hasattr(builtins, name):
            return getattr(builtins, name)
        self[name] = MagicMock()
        return self[name]


def _run(ngrams_type):
    namespace = _Namespace(
        ngrams_options_list=[],
        viewer_options_list=[],
        Ngrams_compute_var=_var(1),
        ngrams_menu_var=_var(ngrams_type),
        csv_file_var=_var(""),
        ngrams_viewer_var=_var(0),
        CoOcc_Viewer_var=_var(0),
        Ngrams_search_var=_var(0),
        ngrams_size=_var(3),
        language_list=["English"],
    )
    namespace["config_util"].get_date_options.return_value = (0, "", "", 0, True)
    node = next(n for n in ast.parse(SOURCE).body if isinstance(n, ast.FunctionDef) and n.name == "run")
    exec(compile(ast.Module(body=[node], type_ignores=[]), "NGrams_CoOccurrences_main.py", "exec"), namespace)
    stats = MagicMock()
    stats.compute_character_word_ngrams.return_value = ([], "")
    import sys

    saved = sys.modules.get("statistics_txt_util")
    sys.modules["statistics_txt_util"] = stats
    try:
        namespace["run"]()
    finally:
        if saved is None:
            del sys.modules["statistics_txt_util"]
        else:
            sys.modules["statistics_txt_util"] = saved
    return namespace["mb"], stats


def test_character_ngrams_warn_instead_of_doing_nothing():
    mb, stats = _run("Character")
    assert stats.compute_character_word_ngrams.call_count == 0
    assert mb.showwarning.call_count == 1
    assert "Character" in str(mb.showwarning.call_args)


def test_word_ngrams_still_run():
    mb, stats = _run("Word")
    assert stats.compute_character_word_ngrams.call_count == 1


def test_the_ngrams_type_menu_offers_no_character_ngrams():
    menus = [
        n
        for n in ast.walk(ast.parse(SOURCE))
        if isinstance(n, ast.Call)
        and getattr(n.func, "attr", None) == "OptionMenu"
        and any(isinstance(a, ast.Name) and a.id == "ngrams_menu_var" for a in n.args)
    ]
    assert len(menus) == 1
    values = [a.value for a in menus[0].args if isinstance(a, ast.Constant)]
    assert "Character" not in values and "Word" in values
