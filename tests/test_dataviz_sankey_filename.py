"""Data visualization, Relational tab: the Sankey chart gets a real output file name (#1756).

run_relational passed outputFilename="" to charts_util.Sankey, whose fig.write_html("") wrote to "." and stopped with
IsADirectoryError, so no Sankey chart could be made from this GUI. run_relational is pulled out of the GUI module and
run with charts_util.Sankey replaced by a mock that keeps the real function's signature.
"""

import ast
import os
from unittest.mock import MagicMock, create_autospec

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _function(filename, name, namespace):
    source = open(os.path.join(SRC, filename), encoding="utf-8-sig").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(ast.get_source_segment(source, node), namespace)
    return namespace[name]


def _sankey_call(fields):
    real_sankey = _function("charts_util.py", "Sankey", {})
    charts_util = MagicMock()
    charts_util.Sankey = create_autospec(real_sankey, return_value=None)
    io_files = MagicMock()
    io_files.generate_output_file_name.side_effect = lambda inputFilename, inputDir, outputDir, ext, *labels, **kw: (
        os.path.join(outputDir, "NLP_" + "_".join(labels) + ext)
    )
    namespace = {"os": os, "mb": MagicMock(), "charts_util": charts_util, "IO_files_util": io_files}
    run_relational = _function("data_visualization_main.py", "run_relational", namespace)
    run_relational("/corpus/NLP_SVO.csv", "/out", False, "Sankey", "", fields, "", 5, 10, 20)
    assert charts_util.Sankey.call_count == 1
    return charts_util.Sankey.call_args


def test_three_way_sankey_writes_an_html_file_in_the_output_folder():
    call = _sankey_call(["Subject (S)", "Verb (V)", "Object (O)"])
    outputFilename = call.args[1]
    assert outputFilename.endswith(".html")
    assert os.path.dirname(outputFilename) == "/out"
    assert "Sankey" in os.path.basename(outputFilename)


def test_two_way_sankey_writes_an_html_file_in_the_output_folder():
    call = _sankey_call(["Subject (S)", "Object (O)"])
    assert call.args[1].endswith(".html") and os.path.dirname(call.args[1]) == "/out"
