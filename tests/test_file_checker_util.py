"""File checker/converter/cleaner: every menu option calls its function with arguments it accepts (#1759).

file_checker_converter_cleaner_main maps each menu option to a function (pydict) and calls it with one of a few fixed
argument lists. "Check empty file" got (window, inputFilename, inputDir, outputDir, config_filename), but
check_empty_file takes (inputFilename, inputDir, configFileName): TypeError. The same check found
"Find & Replace string (via csv file)" (spelling_checker_cleaner takes 6 arguments, was given 8: TypeError), and two
that ran with the wrong values: predict_encoding got the config file name as its number of lines, and
check_utf8_compliance got it as openOutputFiles.

The argument lists now come from file_checker_util.dispatcher_arguments. For every function in pydict, the test reads
its signature from the source (the modules import chardet, nltk, docx... which CI does not install) and binds the
arguments the dispatcher gives it.
"""

import ast
import inspect
import os
import re

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
MAIN = "file_checker_converter_cleaner_main.py"


def _source(filename):
    return open(os.path.join(SRC, filename), encoding="utf-8-sig").read()


def _function_node(filename, name):
    nodes = [n for n in ast.parse(_source(filename)).body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert nodes, f"{name} not found in {filename}"
    return nodes[-1]


def _signature_only(filename, name):
    """The function with its real signature and an empty body."""
    node = _function_node(filename, name)
    node.body = [ast.Pass()]
    node.decorator_list = []
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), filename, "exec"), namespace)
    return namespace[name]


def _dispatcher():
    namespace = {}
    exec(
        ast.get_source_segment(
            _source("file_checker_util.py"), _function_node("file_checker_util.py", "dispatcher_arguments")
        ),
        namespace,
    )
    return namespace["dispatcher_arguments"]


def _mapped_functions():
    return re.findall(r'^pydict\[(".*?")\] = \[\s*"(\w+)\.(\w+)"', _source(MAIN), re.M | re.S)


# check_for_typo is refused before dispatch: run() tells the user to use the spell checker GUI instead
REFUSED = {"check_for_typo"}


@pytest.mark.parametrize("option, module, function", _mapped_functions())
def test_each_menu_function_accepts_the_dispatched_arguments(option, module, function):
    if function in REFUSED:
        assert f'"{function}" in function_to_run' in _source(MAIN)
        return
    args = _dispatcher()(
        function, "WINDOW", "in.txt", "/in", "/out", "NLP_default_IO_config.csv", True, "Excel", "No transformation"
    )
    inspect.signature(_signature_only(module + ".py", function)).bind(*args)


def test_check_empty_file_gets_file_dir_and_config():
    args = _dispatcher()(function="check_empty_file", window="W", inputFilename="in.txt", inputDir="/in",
                         outputDir="/out", config_filename="cfg.csv", openOutputFiles=True, chartPackage="Excel",
                         dataTransformation="No transformation")  # fmt: skip
    assert args == ("in.txt", "/in", "cfg.csv")


def test_predict_encoding_and_utf8_check_do_not_get_the_config_file_as_another_argument():
    dispatch = _dispatcher()
    common = ("W", "in.txt", "/in", "/out", "cfg.csv", False, "Excel", "No transformation")
    assert "cfg.csv" not in dispatch("predict_encoding", *common)
    assert dispatch("check_utf8_compliance", *common) == ("W", "in.txt", "/in", "/out", False)


def test_run_uses_the_dispatcher():
    run_source = ast.get_source_segment(_source(MAIN), _function_node(MAIN, "run"))
    assert "dispatcher_arguments(" in run_source
