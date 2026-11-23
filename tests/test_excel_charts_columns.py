"""Excel charts GUI: a csv with headers can be charted (#1757).

The GUI fills its X/Y menus with the csv's header names and keeps them in selected_series (e.g.
[["Sentence ID", "Sentiment score"]]), but charts_util.get_data_to_be_plotted_NO_counts picks the columns with
data.iloc[:, [x, y]], which takes positions: pandas stopped with "Location based indexing can only have [integer,
integer slice ...] types". run() now turns the names into positions first
(charts_Excel_util.series_names_to_column_positions).

Behind that, run() called charts_Excel_util.create_excel_chart with its arguments out of order (the output folder got
the chart title) and wrote the data to a file name built with generate_output_file_name's arguments shifted by one;
it now calls create_excel_chart as it is defined and opens the chart file it returns.

charts_Excel_main builds its GUI at import and charts_Excel_util imports openpyxl (not installed in CI), so the
functions are pulled out of the source with ast and run against mocks.
"""

import ast
import os
from unittest.mock import MagicMock, create_autospec

import _real_pandas
import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _function(filename, name, namespace):
    # charts_Excel_main.py has old-Mac CR line endings: read with universal newlines
    source = open(os.path.join(SRC, filename), encoding="utf-8-sig").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(ast.get_source_segment(source, node), namespace)
    return namespace[name]


def test_series_names_become_column_positions():
    to_positions = _function("charts_Excel_util.py", "series_names_to_column_positions", {})
    headers = ["Sentiment score", "Sentiment label", "Sentence ID", "Sentence", "Document ID", "Document"]
    positions, missing = to_positions(headers, [["Sentence ID", "Sentiment score"], ["Document ID", "Sentence ID"]])
    assert positions == [[2, 0], [4, 2]]
    assert missing == []


def test_series_names_not_in_the_csv_are_reported():
    to_positions = _function("charts_Excel_util.py", "series_names_to_column_positions", {})
    positions, missing = to_positions(["a", "b"], [["a", "c"]])
    assert missing == ["c"]


def test_positions_select_the_columns_in_a_csv_with_headers():
    try:
        pd, saved = _real_pandas.swap_in()
    except ImportError as exc:
        pytest.skip(f"real pandas not available: {exc}")
    try:
        get_data = _function("charts_util.py", "get_data_to_be_plotted_NO_counts", {})
        to_positions = _function("charts_Excel_util.py", "series_names_to_column_positions", {})
        data = pd.DataFrame({"Sentiment score": [0.5, -0.1], "Sentence ID": [1, 2]})
        with pytest.raises((ValueError, IndexError, TypeError)):  # the bug: names where iloc takes positions
            get_data("in.csv", True, list(data.columns), [["Sentence ID", "Sentiment score"]], data)
        positions, _ = to_positions(list(data.columns), [["Sentence ID", "Sentiment score"]])
        (frame,) = get_data("in.csv", True, list(data.columns), positions, data)
        assert list(frame.columns) == ["Sentence ID", "Sentiment score"]
    finally:
        _real_pandas.swap_out(saved)


def _var(value):
    var = MagicMock()
    var.get.return_value = value
    return var


def test_run_charts_by_position_and_calls_create_excel_chart_in_its_order(tmp_path):
    csv_file = tmp_path / "NLP_VADER.csv"
    csv_file.write_text("Sentiment score,Sentence ID\n0.5,1\n-0.1,2\n", encoding="utf-8")

    real_create = _function("charts_Excel_util.py", "create_excel_chart", {})
    charts_Excel_util = MagicMock()
    charts_Excel_util.create_excel_chart = create_autospec(real_create, return_value=str(tmp_path / "chart.xlsx"))
    charts_Excel_util.series_names_to_column_positions = _function(
        "charts_Excel_util.py", "series_names_to_column_positions", {}
    )
    charts_util = MagicMock()
    charts_util.prepare_data_to_be_plotted_inExcel.return_value = [
        [["Sentence ID", "Sentiment score"], [1, 0.5], [2, -0.1]]
    ]
    gui = MagicMock()
    gui.inputFilename.get.return_value = str(csv_file)
    gui.output_dir_path.get.return_value = str(tmp_path)
    gui.open_csv_output_checkbox.get.return_value = 0
    io_csv = MagicMock()
    io_csv.get_csvfile_headers.return_value = ["Sentiment score", "Sentence ID"]
    namespace = {
        "GUI_util": gui,
        "IO_csv_util": io_csv,
        "IO_files_util": MagicMock(),
        "IO_user_interface_util": MagicMock(),
        "charts_util": charts_util,
        "charts_Excel_util": charts_Excel_util,
        "mb": MagicMock(),
        "scriptName": "charts_Excel_main.py",
        "selected_series": [["Sentence ID", "Sentiment score"]],
        "column_xAxis_label_var": _var(""),
        "column_yAxis_label_var": _var(""),
        "count_var": _var(0),
        "column_yAxis_field_list": [],
        "second_yAxis_var": _var(0),
        "second_yAxis_var_list": [0],
        "second_yAxis_label_var": _var(""),
        "chart_type": _var("line"),
        "chart_type_list": ["line"],
        "chart_title_var": _var("Sentiment"),
        "hover_var_list": [0],
        "column_hover_list": [],
    }
    run = _function("charts_Excel_main.py", "run", namespace)
    run()

    prepare = charts_util.prepare_data_to_be_plotted_inExcel.call_args
    assert prepare.args[1] == [[1, 0]]  # Sentence ID is column 1, Sentiment score column 0
    create = charts_Excel_util.create_excel_chart.call_args
    assert create.args[2] == str(csv_file)  # inputFilename
    assert create.args[3] == str(tmp_path)  # outputDir
    assert create.args[5] == "Sentiment"  # chart_title
    assert create.args[6] == ["line"]  # chart_type_list
