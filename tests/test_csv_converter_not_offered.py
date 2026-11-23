"""File checker/converter/cleaner: the unfinished csv -> txt converter is not offered (#1768).

file_converter_util.csv_converter answers every csv with "The function is still under construction. Sorry!", yet
"Document converter (csv --> txt)" was the first item of the Convert Files menu. It is out of the menu and of the
option -> function map until it exists.
"""

import ast
import os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
SOURCE = open(os.path.join(SRC, "file_checker_converter_cleaner_main.py"), encoding="utf-8").read()


def _convert_menu_values():
    for n in ast.walk(ast.parse(SOURCE)):
        if (
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", None) == "OptionMenu"
            and any(isinstance(a, ast.Name) and a.id == "convert_tools_var" for a in n.args)
        ):
            return [a.value for a in n.args if isinstance(a, ast.Constant)]
    raise AssertionError("Convert Files menu not found")


def test_csv_converter_is_not_in_the_convert_menu():
    values = _convert_menu_values()
    assert "Document converter (docx --> txt)" in values
    assert not any("csv" in v for v in values)


def test_csv_converter_is_not_mapped():
    assert "csv_converter" not in SOURCE
