import pytest

try:
    import pandas as pd
    from boxplot_chart import run as run_boxplot
except (ImportError, SystemExit):
    pytest.skip("boxplot_chart dependencies not available", allow_module_level=True)


def test_boxplot_valence(fixture_csv, tmp_output):
    input_data = pd.read_csv(fixture_csv, encoding="utf-8-sig", on_bad_lines="skip")
    run_boxplot(
        inputFilename=str(fixture_csv),
        outputDir=str(tmp_output),
        csv_field_visualization_var="valence",
        points_var="All points",
        split_data_byCategory_var=False,
        csv_field_boxplot_var="",
        csv_field_boxplot_color_var="",
        inputFileData=input_data,
    )
