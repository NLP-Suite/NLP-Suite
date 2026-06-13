import logging

import charts_util
import IO_csv_util
from util import collect

logger = logging.getLogger(__name__)


def run_excel_plotly_charts(
    inputFilename,
    outputDir,
    csv_field_visualization_var,
    X_axis_var,
    csv_file_field_Y_axis_list,
    # TODO: add these params:
    charts_type_options,  # A list, currently delimited by spaces
    chart_package,
    data_transformation,
    inputFileData,
):
    """Render Plotly charts from a csv file."""
    filesToOpen = []

    outputFiles = ""
    # if extra_GUIs_var.get()==False and csv_field_visualization_var == '':

    # if extra_GUIs_var.get()==False and visualizations_menu_var=='':

    # if csv_field_visualization_var=='':

    # Excel/Plotly charts --------------------------------------------------------------------------------
    if X_axis_var == "":
        logger.info(
            "Warning, No X-axis variable has been selected.\n\nPlease, use the dropdown menu to select the csv file column to be used as X-axis and try again."
        )
        return

    if "bar" in charts_type_options.lower() or "line" in charts_type_options.lower():
        # TODO: implement warnings in frontend
        if X_axis_var == "" and len(csv_file_field_Y_axis_list) < 1:
            return
    if "scatter" in charts_type_options.lower():
        if len(csv_file_field_Y_axis_list) < 1:
            return
    if "bubble" in charts_type_options.lower() or "radar" in charts_type_options.lower():
        if len(csv_file_field_Y_axis_list) < 3:
            # print(title='Warning',message='A '+str(GUI_util.charts_type_options_widget.get().lower()+' chart requires at least THREE Y-axis variables.\n\nPlease, select the expected number of variables and try again.'))
            return
    headers = IO_csv_util.get_csvfile_headers(inputFilename, inputFileData=inputFileData)
    col_num = IO_csv_util.get_columnNumber_from_headerValue(
        headers,
        csv_field_visualization_var,
        inputFilename="",
        inputFileData=inputFileData,
    )

    columns_to_be_plotted_yAxis = [[col_num, col_num]]
    count_var = 1
    chart_type_list = [charts_type_options.split(" ")[0]]
    outputFiles = charts_util.run_all(
        columns_to_be_plotted_yAxis,
        inputFilename,
        outputDir,
        outputFileLabel="",
        chartPackage=chart_package,
        dataTransformation=data_transformation,
        chart_type_list=chart_type_list,
        chart_title="Frequency Distribution of " + csv_field_visualization_var,
        column_xAxis_label_var=X_axis_var,  # csv_field_visualization_var,
        hover_info_column_list=[],
        count_var=count_var,
        complete_sid=False,
        csv_field_Y_axis_list=csv_file_field_Y_axis_list,
        X_axis_var=X_axis_var,
        inputFileData=inputFileData,
    )  # TODO to be changed
    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    return outputFiles


def main():
    inputFilename = "dogs.csv"
    outputDir = "C:/Users/sherry/OneDrive/Desktop/QTM446W/Ouput"
    inputFileData = """Obs,Name,Gender,Fixed,Color,Heritage,Age,Weight,Size
1,Max,Male,Yes,Dark brown,"Designer/deliberate mix (e.g., labradoodles)",7,70,Large
2,Isla,Female,Yes,Black,Single breed,8,13,Small
3,Tyson,Male,No,Black,Mixed breed/unknown,0.33,24,Large
4,Lexi,Female,Yes,Light brown,"Designer/deliberate mix (e.g., labradoodles)",6,24,Small
5,,Male,Yes,Light brown,Mixed breed/unknown,6,45,Large
6,Lola,Female,Yes,Black,Mixed breed/unknown,14,85,Large
7,Lady,Female,Yes,Black,Single breed,11,22,Small
8,Leo,Male,Yes,Reddish,Single breed,15,14,Small"""

    run_excel_plotly_charts(
        inputFilename=inputFilename,
        outputDir=outputDir,
        visualizations_menu_var="Excel",
        csv_field_visualization_var="Color",
        X_axis_var="Heritage",
        csv_file_field_Y_axis_list=["Age, Fixed, Weight"],
        # TODO: add these params:
        charts_type_options="Pie",
        chart_package="Excel",
        data_transformation="None",
        inputFileData=inputFileData,
    )


if __name__ == "__main__":
    main()
