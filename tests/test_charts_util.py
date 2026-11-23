"""Tests for src/charts_util.py, one file per module (folded from 3 files, 23 Nov 2026).

From test_dataviz_boxplot_call.py:

Data visualization, Numeric tab: Boxplot calls charts_util.boxplot the way it is defined (#1758).

run_numeric passed complete_sid=, csv_field_Y_axis_list= and X_axis_var= to charts_util.boxplot, which takes none of
them, and the output folder where boxplot expects an output file name, so every boxplot stopped with TypeError. The
Boxplot row's own options ("Data" points, "Split data by category", its csv field and color field) were never passed.

run_numeric is pulled out of the GUI module and run with charts_util.boxplot replaced by a mock that keeps the real
function's signature; boxplot itself is run with plotly.express mocked to check how the "Data" menu values reach Plotly.

From test_dataviz_sankey_filename.py:

Data visualization, Relational tab: the Sankey chart gets a real output file name (#1756).

run_relational passed outputFilename="" to charts_util.Sankey, whose fig.write_html("") wrote to "." and stopped with
IsADirectoryError, so no Sankey chart could be made from this GUI. run_relational is pulled out of the GUI module and
run with charts_util.Sankey replaced by a mock that keeps the real function's signature.

From test_network_timeline_batched.py:

The vis.js network pages' timeline must update the graph ONCE per step.

Roberto, 4 Oct 2026, on a network of ~1,900 nodes and edges: "The time bar does not move". Every step called
nodes.update / edges.update once per item, and each call makes vis-network redraw and re-run its physics, so the page
froze after a step or two. The templates are checked as text: charts_util imports the heavy libraries the tests
stub, so the page cannot be generated here.
"""

import ast
import os
from unittest.mock import MagicMock, create_autospec

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _function(filename, name, namespace):
    source = open(os.path.join(SRC, filename), encoding="utf-8-sig").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(ast.get_source_segment(source, node), namespace)
    return namespace[name]


def _run_numeric(points="all", split=0, category="", color=""):
    real_boxplot = _function("charts_util.py", "boxplot", {})
    charts_util = MagicMock()
    charts_util.boxplot = create_autospec(real_boxplot, return_value=None)
    io_files = MagicMock()
    io_files.generate_output_file_name.side_effect = lambda inputFilename, inputDir, outputDir, ext, *labels, **kw: (
        os.path.join(outputDir, "NLP_" + "_".join(labels) + ext)
    )
    mb = MagicMock()
    namespace = {"os": os, "mb": mb, "charts_util": charts_util, "IO_files_util": io_files, "GUI_util": MagicMock()}
    run_numeric = _function("data_visualization_main.py", "run_numeric", namespace)
    # inputFilename, outputDir, openOutputFiles, visualizations_menu_var, csv_field_visualization_var, X_axis_var,
    # csv_file_field_Y_axis_list, points_var, split_data_byCategory_var, csv_field_boxplot_var,
    # csv_field_boxplot_color_var, X_axis_bubble_var, color_1_style_var, histogram_nbins_var,
    # histogram_category_var, histogram_marginal_var, violin_points_var, violin_category_var
    run_numeric(
        "/corpus/NLP_VADER.csv", "/out", False, "Boxplot", "Sentiment score", "", [],
        points, split, category, color, "", "", "", "", "", "all", "",
    )  # fmt: skip
    return charts_util.boxplot, mb


def test_boxplot_is_called_with_its_own_arguments():
    boxplot, _ = _run_numeric()
    assert boxplot.call_count == 1
    bound = boxplot.call_args
    assert bound.args[0] == "/corpus/NLP_VADER.csv"
    assert bound.args[1].endswith(".html") and os.path.dirname(bound.args[1]) == "/out"
    assert bound.args[2] == "Sentiment score"


def test_boxplot_split_by_category_passes_the_category_and_color_fields():
    boxplot, _ = _run_numeric(points="outliers", split=1, category="Document", color="Sentiment label")
    kwargs = boxplot.call_args.kwargs
    assert kwargs["points"] == "outliers"
    assert kwargs["bycategory"] == 1
    assert kwargs["category"] == "Document"
    assert kwargs["color"] == "Sentiment label"


def test_boxplot_split_without_a_category_field_warns_instead_of_running():
    boxplot, mb = _run_numeric(split=1, category="")
    assert boxplot.call_count == 0
    assert mb.showwarning.call_count == 1


@pytest.mark.parametrize("menu_value, plotly_value", [("all", "all"), ("None", False), ("outliers", "outliers")])
def test_boxplot_data_menu_values_reach_plotly(tmp_path, menu_value, plotly_value):
    px = MagicMock()
    boxplot = _function("charts_util.py", "boxplot", {"px": px, "mb": MagicMock(), "pd": MagicMock()})
    out = str(tmp_path / "box.html")
    assert boxplot({"Sentiment score": [0.5, -0.2, 0.1]}, out, "Sentiment score", menu_value) == out
    assert px.box.call_args.kwargs["points"] == plotly_value


# ---- formerly tests/test_dataviz_sankey_filename.py ---------------------------------------------------------

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


# ---- formerly tests/test_network_timeline_batched.py --------------------------------------------------------

import re  # noqa: E402

SRC_network_timeline_batched = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "charts_util.py"
)


def _src():
    with open(SRC_network_timeline_batched, encoding="utf-8-sig") as f:
        return f.read()


def test_no_per_item_update_in_the_network_templates():
    s = _src()
    assert not re.search(r"nodes\.update\(\{\{ id: n\.id", s)
    assert not re.search(r"edges\.update\(\{\{ id: e\.id", s)


def test_every_batch_is_flushed_once():
    s = _src()
    declared = s.count("var nu = [], eu = [];")
    assert declared >= 3
    assert s.count("nodes.update(nu); edges.update(eu);") == declared


def test_each_template_defines_the_edge_colours_it_uses():
    s = _src()
    # the second template used origEdgeColors in its timeline without defining it
    for m in re.finditer(r"function applyTimeFilter\(idx\)", s):
        before = s[: m.start()]
        start = before.rfind("new vis.Network(")
        assert start >= 0
        assert "var origEdgeColors = {{}};" in before[start:], "template at offset %d" % m.start()
