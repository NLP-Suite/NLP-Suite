"""Data visualization, Numeric tab: Boxplot calls charts_util.boxplot the way it is defined (#1758).

run_numeric passed complete_sid=, csv_field_Y_axis_list= and X_axis_var= to charts_util.boxplot, which takes none of
them, and the output folder where boxplot expects an output file name, so every boxplot stopped with TypeError. The
Boxplot row's own options ("Data" points, "Split data by category", its csv field and color field) were never passed.

run_numeric is pulled out of the GUI module and run with charts_util.boxplot replaced by a mock that keeps the real
function's signature; boxplot itself is run with plotly.express mocked to check how the "Data" menu values reach Plotly.
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
