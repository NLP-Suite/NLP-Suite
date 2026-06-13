import logging

# Written by Yuhang Feng November 2019
# Edited by Roberto Franzosi
import charts_Excel_util
import charts_util
import IO_csv_util
import IO_files_util

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_excelCharts(
    inputFilename_name,
    outputDir,
    openOutputFiles,
    selected_series,
    column_xAxis_label_var,
    column_yAxis_label_var,
    count_var,
    column_yAxis_field_list,
    second_y_var,
    second_y_var_list,
    second_yAxis_label_var,
    chart_type,
    chart_type_list,
    chart_title,
    hover_var_list,
    hover_info_column_list,
):

    filesToOpen = []  # Store all files that are to be opened once finished

    if len(chart_type) == 0:
        logger.info(
            "Chart type erorr, No chart type was specified (e.g., line, bubble). The chart cannot be created. Please, select a chart type and try again!"
        )
        return True
    if hover_var_list and all(check == 1 for check in hover_var_list):
        if second_y_var_list and all(var == 0 for var in second_y_var_list):
            output_file_name = IO_files_util.generate_output_file_name(
                inputFilename_name, outputDir, ".xlsm", "EC", "chart"
            )
        else:
            logger.info(
                "Hover var and Second Y-axis var error, Hovering feature is not available for chart with two Y-axes. The system indicates that you tick both the hover and the second Y-axis check boxes.\n\nPlease, check your input and try again!"
            )
            return True
    elif hover_var_list and all(check == 0 for check in hover_var_list):
        output_file_name = IO_files_util.generate_output_file_name(
            inputFilename_name, outputDir, ".xlsx", "EC", "chart"
        )
    else:
        logger.info(
            "Hover var error, Hover feature applies to all the groups when multiple groups of data are selected. The system indicates that at least one of the groups seleted did not tick the hover checkbox.\n\nPlease, check your input and try again!"
        )
        return True
    len(selected_series)
    # # The 2 functions get_data_to_be_plotted check for data with/without headers
    if count_var == 1:  # counting y-axis
        if hover_var_list and all(check == 0 for check in hover_var_list):
            data_to_be_plotted = charts_util.prepare_data_to_be_plotted_inExcel(
                inputFilename_name,
                selected_series,
                chart_type,
                1,
                column_yAxis_field_list,
            )
        else:
            logger.info(
                "Hover var and Count var error, Hovering feature is not available for chart with counting feature. The system indicates that you tick both the hover and the count check boxes.\n\nPlease, check your input and try again!"
            )
            return True
    else:  # NOT counting y-axis
        data_to_be_plotted = charts_util.prepare_data_to_be_plotted_inExcel(
            inputFilename_name, selected_series, chart_type, 0
        )

    errorFound = IO_csv_util.list_to_csv(data_to_be_plotted, output_file_name)
    if errorFound:
        return
    reverse_column_postion_for_series_label = False

    series_label_list = []
    for _i in range(len(selected_series)):
        series_label_list.append("")
    logger.info("series_label_list %s", series_label_list)
    if charts_Excel_util.create_excel_chart(
        data_to_be_plotted,
        output_file_name,
        chart_title,
        chart_type_list,
        column_xAxis_label_var,
        column_yAxis_label_var,
        hover_info_column_list,
        reverse_column_postion_for_series_label,
        series_label_list,
        second_y_var,
        second_yAxis_label_var,
    ):
        return
    filesToOpen.append(output_file_name)

    return filesToOpen
