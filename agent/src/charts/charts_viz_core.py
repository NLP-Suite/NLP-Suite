# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023
import io
import logging
import os

import charts_Excel_util
import charts_Plotly_util
import IO_csv_util
import IO_user_interface_util
import pandas as pd
import statistics_csv_util
from charts_data_helpers import (
    add_missing_IDs,
    build_timed_alert_message,
    get_data_to_be_plotted_NO_counts,
    get_data_to_be_plotted_with_counts,
    get_dataRange,
)
from util import collect

logger = logging.getLogger(__name__)


def prepare_data_to_be_plotted_inExcel(
    inputFilename,
    columns_to_be_plotted,
    chart_type_list,
    count_var=0,
    column_yAxis_field_list=None,
    inputFileData="",  # Optional parameter with default value
):
    # Check if inputFileData is provided; if so, use it instead of inputFilename
    if column_yAxis_field_list is None:
        column_yAxis_field_list = []
    if inputFileData:
        try:
            # Convert inputFileData to a DataFrame
            data = pd.read_csv(io.StringIO(inputFileData), encoding="utf-8", on_bad_lines="skip")
        except ValueError as err:
            logger.info("Input data read error %s", str(err))
            return None
        headers = list(data.columns)
        withHeader_var = True
    else:
        withHeader_var = IO_csv_util.csvFile_has_header(
            inputFilename, inputFileData=inputFileData
        )  # check if the file has header
        data, headers = IO_csv_util.get_csv_data(
            inputFilename, withHeader_var, inputFileData=inputFileData
        )  # get the data and header
        if len(data) == 0:
            return None
        headers = list(headers)

    count_msg, withHeader_msg = build_timed_alert_message(chart_type_list[0], withHeader_var, count_var)
    if count_var == 1:
        dataRange = get_dataRange(columns_to_be_plotted, data)
        # Get data with counts
        data_to_be_plotted = get_data_to_be_plotted_with_counts(
            headers,
            columns_to_be_plotted,
            column_yAxis_field_list,
            dataRange,
        )
    else:
        try:
            if not inputFileData:
                data = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines="skip")
        except Exception:
            try:
                if not inputFileData:  # Handle encoding fallback only for inputFilename
                    data = pd.read_csv(inputFilename, encoding="ISO-8859-1", on_bad_lines="skip")
                    IO_user_interface_util.timed_alert(
                        2000,
                        "Warning",
                        "Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 in reading into pandas the csv file "
                        + inputFilename,
                    )
                    logger.info(
                        "Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 encoding in reading into pandas the csv file "
                        + inputFilename
                    )
            except ValueError as err:
                if "codec" in str(err):
                    err = (
                        str(err)
                        + "\n\nExcel-util encountered errors with both utf-8 and ISO-8859-1 encoding in the function 'prepare_data_to_be_plotted_inExcel' while reading into pandas the csv file\n\n"
                        + inputFilename
                        + "\n\nPlease, check carefully the data in the csv file; it may contain filenames with non-utf-8/ISO-8859-1 characters; less likely, the data in the txt files that generated the csv file may also contain non-compliant characters. Run the utf-8 compliance algorithm and, perhaps, run the cleaning algorithm that converts apostrophes.\n\nNO EXCEL CHART PRODUCED."
                    )
                logger.info("Input file read error %s", str(err))
                return None
        data_to_be_plotted = get_data_to_be_plotted_NO_counts(
            inputFilename if not inputFileData else None,
            withHeader_var,
            headers,
            columns_to_be_plotted,
            data,
        )

    return data_to_be_plotted


# bar chart aggregated by group  -----------------------------------------------------------------
# plot the words contained in each groupBy field values (e.g, the word 'Rome' in POS tag PPN)
# must first run compute_csv_column_frequencies_with_aggregation
def visualize_chart_byGroup(
    inputFilename,
    outputDir,
    chartPackage,
    dataTransformation,
    filesToOpen,
    columns_to_be_plotted_byGroup,
    groupByList,
    chart_title,
    columns_to_be_plotted_xAxis,
    columns_to_be_plotted_yAxis,
):
    pivot = False
    filesToOpen = []

    # the function compute_csv_column_frequencies produces plots
    # @@@ 9/29/2023
    outputFiles = statistics_csv_util.compute_csv_column_frequencies(
        inputFilename,
        None,
        outputDir,
        False,
        chartPackage,
        dataTransformation,
        plot_cols=columns_to_be_plotted_yAxis,
        hover_col=[],
        group_cols=groupByList,
        complete_sid=False,
        chart_title=chart_title,
        fileNameType=columns_to_be_plotted_yAxis[0],
        chartType="",
        pivot=pivot,
    )
    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    # temp_outputFilename[0] is the frequency filename (with no hyperlinks)

    # 0 is the groupBy field with no-hyperlinks (e.g., NER)
    # 1 is the column plotted (e.g., Form)
    # 2 is the Document ID
    # 3 is the Document
    # 4 is Frequency
    # sel_column_name = IO_csv_util. = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document', inputFilename)(headers, 1)
    # @@@
    headers = IO_csv_util.get_csvfile_headers(inputFilename, ask_Question=False)
    IO_csv_util.get_columnNumber_from_headerValue(headers, "Document", inputFilename)
    IO_csv_util.get_columnNumber_from_headerValue(headers, columns_to_be_plotted_yAxis[0], inputFilename)

    # if chartPackage == "Excel":
    # chart is visualized in compute_csv_column_frequencies
    # # in visualize_chart_byGroup
    # outputFiles = run_all(columns_to_be_plotted_byGroup, new_inputFilename, outputDir,
    #                                           # count_var is set in the calling function
    #                                           #     0 for numeric fields;
    #                                           #     1 for non-numeric fields
    #                                           remove_hyperlinks=remove_hyperlinks)
    # if outputFiles!=None:
    #     if len(chart_outputFilename) > 0:
    return filesToOpen


# TODO columns_to_be_plotted comes in a single list to be exported to run_all as double list
# columns_to_be_plotted, columns_to_be_plotted_bySent, columns_to_be_plotted_byDoc
#   all double lists [[]]
#   BUT they are passed by calling functions as single lists []
#       and converted to double lists for run_all
#       e.g., columns_to_be_plotted_xAxis=[],
#       e.g., columns_to_be_plotted_xAxis=[],
#       e.g., columns_to_be_plotted_xAxis=[],
# the variable groupByList,plotList, chart_title_label are used to compute column statistics
#   groupByList is typically the list ['Document ID', 'Document'] or just ['Document']
#   plotList is the list of fields to be plotted
#   chart_title_label is used as part of the chart_title when plotting the fields statistics (Mean, Mode, Skewness,...)
# X-axis


def visualize_chart(
    chartPackage,
    dataTransformation,
    inputFilename,
    outputDir,
    columns_to_be_plotted_xAxis,
    columns_to_be_plotted_yAxis,
    chart_title,
    count_var,
    hover_label,
    outputFileNameType,
    column_xAxis_label,
    groupByList,
    plotList,
    chart_title_label,
    column_yAxis_label="Frequencies",
    pivot=False,
):
    filesToOpen = []
    columns_to_be_plotted_numeric = []
    columns_to_be_plotted_byDoc = []
    columns_to_be_plotted_bySent = []

    if chartPackage != "No charts":
        pass
    else:
        return

        # the run_all always expects a double list with 2 values, e.g., [[0,0], [1,1]
        #   so, when only one field is passed, we add the same field twice
        # TODO

    # pivot = True will list for every document all the separate values of the selected item to be plotted
    #       = False will sum all the individual values
    # count_var should always be TRUE to get frequency distributions

    # in the bar charts columns_to_be_plotted, when numeric data are passed,
    #   the first item is the column of numeric values
    #   the second item is the X-axis
    #   see the example of call in get_ngramlist
    headers = IO_csv_util.get_csvfile_headers_pandas(inputFilename)
    if len(headers) == 0:
        IO_user_interface_util.timed_alert(
            2000,
            "Empty csv file",
            "The file\n\n"
            + inputFilename
            + "\n\nis empty. No charts can be produced using this csv file.\n\nPlease, check the file and try again.",
            True,
            "",
            True,
            "",
            False,
        )
        logger.info(
            "The file\n\n"
            + inputFilename
            + "\n\nis empty. No charts can be produced using this csv file.\n\nPlease, check the file and try again."
        )
        return filesToOpen
    field_number_xAxis = None
    if len(columns_to_be_plotted_xAxis) == 1:
        field_number_xAxis = IO_csv_util.get_columnNumber_from_headerValue(
            headers, columns_to_be_plotted_xAxis[0], inputFilename
        )

    if "Document" in str(groupByList):
        docCol = IO_csv_util.get_columnNumber_from_headerValue(headers, "Document", inputFilename)
        # we need to visualize the doc filename
        byDoc = True
    else:
        byDoc = False
    if "Sentence ID" in headers:
        sentCol = IO_csv_util.get_columnNumber_from_headerValue(headers, "Sentence ID", inputFilename)
        bySent = True
    else:
        bySent = False

    # in visualize_chart
    for i in range(0, len(columns_to_be_plotted_yAxis)):
        # get numeric value of header, necessary for run_all
        field_number_yAxis = IO_csv_util.get_columnNumber_from_headerValue(
            headers, columns_to_be_plotted_yAxis[i], inputFilename
        )
        if field_number_yAxis is None:
            return filesToOpen

        if len(columns_to_be_plotted_xAxis) == 0:  # no x-Axis field
            columns_to_be_plotted_numeric.append([field_number_yAxis, field_number_yAxis])
        else:  # there is an X-Axis (e.g., ngrams values)
            columns_to_be_plotted_numeric.append([field_number_xAxis, field_number_yAxis])

        if byDoc:
            columns_to_be_plotted_byDoc.append([docCol, field_number_yAxis])
        if bySent:
            columns_to_be_plotted_bySent.append([sentCol, field_number_yAxis])

        # remove first item in list, the X-axis label substituted by doc

        # TODO Naman for numeric data build classes of values, rather than individual values, to be displayed in the X-axis
        # https://stackoverflow.com/questions/49382207/how-to-map-numeric-data-into-categories-bins-in-pandas-dataframe
        # if count_var == 0: # numeric variable
        #     # create classes of values
        #     for j in range(1,len(bins)):

    # when pivoting data
    # for i in range(1, n_documents):
    count_var_SV = count_var

    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename)

    logger.info("\n\n\nRecords in inputfile (in charts_util) %s    %s", nRecords, inputFilename)

    # standard bar chart ------------------------------------------------------------------------------
    # Form	Lemma	POS	Record ID	Sentence ID	Document ID	Document
    # columns_to_be_plotted_numeric = [[0,0], [1,1]] with count_var = 1 since these values need to be counted
    # @@@ 9/29/2023
    if len(columns_to_be_plotted_numeric[0]) > 0:  # compute only if the double list is not empty
        outputFiles = run_all(
            columns_to_be_plotted_numeric,
            inputFilename,
            outputDir,
            outputFileLabel=outputFileNameType,
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            chart_type_list=["bar"],
            chart_title=chart_title,
            column_xAxis_label_var=column_xAxis_label,
            column_yAxis_label_var=column_yAxis_label,
            hover_info_column_list=hover_label,
            count_var=count_var,
        )  # always 1 to get frequencies of values, except for n-grams where we already pass stats

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)
        else:
            # no point continuing to process more charts if an error was encountered and None was returned
            #   typically because of too many rows for Excel to handle, when Excel is used
            return

    # by DOCUMENT
    if byDoc:
        # TODO depends on how many documents we have;
        #   no point charting one document since these charts would be the same as no document
        n_documents = IO_csv_util.GetMaxValueInCSVField(inputFilename, "visualize_charts_util", "Document ID")
        if n_documents > 1:
            column_yAxis_label = "Frequencies"
            columns_to_be_plotted_byGroup = []
            chart_title = chart_title + " by Document"
            for header in groupByList:
                groupCol = IO_csv_util.get_columnNumber_from_headerValue(headers, header, inputFilename)
                columns_to_be_plotted_byGroup.append([groupCol, field_number_yAxis])

            # by DOCUMENT
            outputFiles = visualize_chart_byGroup(
                inputFilename,
                outputDir,
                chartPackage,
                dataTransformation,
                filesToOpen,
                columns_to_be_plotted_byGroup,
                groupByList,
                chart_title,
                columns_to_be_plotted_xAxis,
                columns_to_be_plotted_yAxis,
            )

            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

    # bar chart aggregated by group  (e.g., form values by POS tags) -----------------------------------------------------------------
    #   avoid plotting by ['Document ID', 'Document'] as groupBy; done in chart byDoc
    if len(groupByList) > 0 and groupByList != ["Document ID", "Document"]:
        columns_to_be_plotted_byGroup = []
        for header in groupByList:
            groupCol = IO_csv_util.get_columnNumber_from_headerValue(headers, header, inputFilename)
            columns_to_be_plotted_byGroup.append([groupCol, field_number_yAxis])

        outputFiles = visualize_chart_byGroup(
            inputFilename,
            outputDir,
            chartPackage,
            dataTransformation,
            filesToOpen,
            columns_to_be_plotted_byGroup,
            groupByList,
            chart_title,
            columns_to_be_plotted_xAxis,
            columns_to_be_plotted_yAxis,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    count_var = count_var_SV

    # compute field STATISTICS (mean, median, skeweness, kurtosis...)--------------------------------------------------------------
    # TODO THE FIELD MUST CONTAIN NUMERIC VALUES
    # plotList (a list []) contains the columns headers to be used to compute their stats
    if len(groupByList) > 0 and not isinstance(outputFiles, str):  # compute only if list is not empty
        if count_var == 1:
            if len(outputFiles) == 0:
                return filesToOpen  # []
            temp_inputFilename = outputFiles[0]
        else:
            temp_inputFilename = inputFilename
        if plotList == ["Frequency"]:
            plotList = ["Frequency_" + str(columns_to_be_plotted_yAxis[0])]

        outputFiles = statistics_csv_util.compute_csv_column_statistics(
            temp_inputFilename,
            outputDir,
            outputFileNameType,
            groupByList,
            plotList,
            chart_title_label,
            chartPackage,
            dataTransformation,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    return filesToOpen


# best approach when all the columns to be plotted are already in the file
#   otherwise, use statistics_csv_util.compute_csv_column_frequencies
# only one hover-over column per series can be selected
# each series plotted has its own hover-over column
#   if the column is the same (e.g., sentence), this must be repeated as many times as there are series

# columns_to_be_plotted is a double list of 2 items for each list [[0, 1], [0, 2], [0, 3]] where
#   the first number refers to the x-axis value and the second to the y-axis value (i.e., a frequency field)
# when count_var=1 the second number gets counted (non numeric values MUST be counted)
# the complete sid need to be tested as na would be filled with 0
# if you need to aggregate fields displaying results grouped by a specific field (e.g., words by NER tag, NER tag by Document ID),
#   you need to run first statistics_csv_util.compute_csv_column_frequencies_with_aggregationgroupBy and then run_all
#   Examples of this can be found in parsers_annotators_visualization in parsers_annotators_visualization
#   and in visualize_chart in charts_util


# TODO columns_to_be_plotted comes in a single list to be exported to run_all as double list
# columns_to_be_plotted, columns_to_be_plotted_bySent, columns_to_be_plotted_byDoc
#   all double lists [[]]
#   BUT they are passed by calling functions as single lists []
#       and converted to double lists for run_all
#       e.g., columns_to_be_plotted_xAxis=[],
#       e.g., columns_to_be_plotted_xAxis=[],
#       e.g., columns_to_be_plotted_xAxis=[],
# the variable groupByList,plotList, chart_title_label are used to compute column statistics
#   groupByList is typically the list ['Document ID', 'Document'] or just ['Document']

# Form values	Frequencies of Form	Lemma values	Frequencies of Lemma
# [[0,0], [1,1]] will plot two series, 1 and 2 (e.g., Form & Lemma values) as bar charts, one bar next the other

# Suppose to have a csv file with the following headers:
#   Document ID, Document, Frequency_Document, NER, Frequency_NER
# The order of items in the list columns_to_be_plotted matters:
#   columns_to_be_plotted = [[3, 4], [1, 2]] will display documents in the X-Axis with 2 bars for document frequency and NER frequency
#   columns_to_be_plotted = [[1, 2], [3, 4]] will display NER tags in the X-Axis with 2 bars for document frequency and NER frequency
#   THE LAST ITEM IN THE DOUBLE LIST DETERMINES WHAT GOES ON THE X AXIS:
#   e.g. [1, 2] DISPLAYS Document as X axis and Frequency_Document as Y axis
#   e.g. [3, 4] DISPLAYS NER as X axis and Frequency_NER as Y axis

#   plotList is the list of fields to be plotted


def run_all(
    columns_to_be_plotted,
    inputFilename,
    outputDir,
    outputFileLabel,
    chartPackage,
    dataTransformation,
    chart_type_list,
    chart_title,
    column_xAxis_label_var,
    hover_info_column_list=None,
    count_var=0,
    column_yAxis_label_var="Frequencies",
    column_yAxis_field_list=None,
    reverse_column_position_for_series_label=False,
    series_label_list=None,
    second_y_var=0,
    second_yAxis_label="",
    complete_sid=False,
    remove_hyperlinks=False,
    csv_field_Y_axis_list=None,
    X_axis_var=None,
    inputFileData="",
):
    from io import StringIO

    # get the chart type from the GUI user selection
    # TODO:

    if X_axis_var is None:
        X_axis_var = []
    if csv_field_Y_axis_list is None:
        csv_field_Y_axis_list = []
    if series_label_list is None:
        series_label_list = []
    if column_yAxis_field_list is None:
        column_yAxis_field_list = []
    if hover_info_column_list is None:
        hover_info_column_list = []
    use_Plotly = "plotly" in chartPackage.lower()
    # added by Tony, May 2022 for complete sentence index
    # the file should have a column named Sentence ID
    # the extra parameter "complete_sid" is set to True by default to avoid extra code mortification elsewhere
    if complete_sid:
        # TODO Samir
        inputFilename = add_missing_IDs(pd.read_csv(StringIO(inputFileData)), inputFilename)
    if use_Plotly:
        if "static" in chartPackage.lower():
            static_flag = True
        else:
            static_flag = False
        # TODO Tony when plotting bar charts with documents in the X-axis we need to remove the path and just keep the tail
        #   or the display is too messy; it works well with Excel
        if "Kurtosis" in chart_title:
            chart_type_list = ["Bar"]
        Plotly_outputFilename = charts_Plotly_util.create_Plotly_chart(
            inputFilename=inputFilename,
            outputDir=outputDir,
            chart_title=chart_title,
            chart_type_list=chart_type_list,
            cols_to_plot=columns_to_be_plotted,
            column_xAxis_label=column_xAxis_label_var,
            column_yAxis_label=column_yAxis_label_var,
            remove_hyperlinks=remove_hyperlinks,
            static_flag=static_flag,
            csv_field_Y_axis_list=csv_field_Y_axis_list,
            X_axis_var=X_axis_var,
            inputFileData=inputFileData,
        )
        logger.info("Visualized using plotly")
        return Plotly_outputFilename
    data_to_be_plotted = prepare_data_to_be_plotted_inExcel(
        inputFilename,
        columns_to_be_plotted,
        chart_type_list,
        count_var,
        column_yAxis_field_list,
        inputFileData=inputFileData,
    )

    def list_of_lists_to_csv(data, csv_file_path):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_csv(csv_file_path, index=False)

    if isinstance(data_to_be_plotted[0], list):
        list_of_lists_to_csv(data_to_be_plotted[0], "temptemp2.csv")
        df = statistics_csv_util.data_transformation("temptemp2.csv", dataTransformation)
        os.remove("temptemp2.csv")
        data_to_be_plotted = [[df.columns.tolist()] + df.values.tolist()]

    if data_to_be_plotted is None:
        logger.info("Data to be plotted was none!")
        return

    transform_list = []
    # the following is deciding which type of data is returned from prepare_data_to_be_plotted_inExcel
    # for the function prepare_data_to_be_plotted_inExcel branch into two different data handling functions which retruns different data type
    # and due to complexity reasons, we keep them in this way:
    # check the data type for the return value and decide which step to take next
    if not (isinstance(data_to_be_plotted[0], list)):
        for df in data_to_be_plotted:
            header = list(df.columns)
            # when running topic modeling the topic number which is an integer gets converted to a decimal and plotted as a decimal
            #   the following command is doing that
            data = df.values.tolist()
            data.insert(0, header)
            transform_list.append(data)
            data_to_be_plotted = transform_list
    if data_to_be_plotted is None:
        logger.info("Data to be plotted was none x2!")
        return
    else:
        # the lines below handle specifically the "Form-Lemma" annotator because "form-lemma" is not processed in statistics_csv_util.py
        withHeader_var = IO_csv_util.csvFile_has_header(
            inputFilename, inputFileData=inputFileData
        )  # check if the file has header
        data, headers = IO_csv_util.get_csv_data(
            inputFilename, withHeader_var, inputFileData=inputFileData
        )  # get the data and header

        def double_level_grouping_and_frequency(data, plot_cols, group_cols):
            # Calculate the counts for each column
            group_cols_count = data[group_cols[0]].value_counts().reset_index()
            group_cols_count.columns = [group_cols[0], f"Frequency_{group_cols[0]}"]
            plot_cols_count = (
                data.groupby(group_cols)[plot_cols[0]].value_counts().reset_index(name=f"Frequency_{plot_cols[0]}")
            )
            # Merge the counts back into the original dataframe
            data_final = pd.merge(group_cols_count, plot_cols_count, how="inner", on=group_cols[0])
            data_final = data_final.drop_duplicates()  # Remove potential duplicate rows
            return data_final
            # Convert DataFrame into list of lists
            # Extract 2nd and 3rd column into one list of lists and 4th and 5th into another

        if (
            len(data_to_be_plotted) == 2
            and data_to_be_plotted[0][0] == ["Form values", "Frequencies of Form"]
            and data_to_be_plotted[1][0] == ["Lemma values", "Frequencies of Lemma"]
        ):
            data = pd.DataFrame(data, columns=headers)
            data_to_be_plotted = double_level_grouping_and_frequency(data, ["Form"], ["Lemma"])
            data_to_be_plotted.to_csv("Temptemp.csv", index=False)
            data_final = statistics_csv_util.data_transformation("Temptemp.csv", dataTransformation)
            data_list = data_final.values.tolist()
            list_1 = [[row[2], row[3]] for row in data_list]
            list_2 = [[row[0], row[1]] for row in data_list]
            list_1.insert(0, ["Form values", "Frequencies of Form" + "_" + dataTransformation])
            list_2.insert(0, ["Lemma values", "Frequencies of Lemma" + "_" + dataTransformation])
            data_to_be_plotted = [list_1, list_2]
            os.remove("Temptemp.csv")

        chart_title = chart_title
        outputFiles = charts_Excel_util.create_excel_chart(
            data_to_be_plotted,
            inputFilename,
            outputDir,
            outputFileLabel,
            chart_title,
            chart_type_list,
            column_xAxis_label_var,
            column_yAxis_label_var,
            hover_info_column_list,
            reverse_column_position_for_series_label,
            series_label_list,
            second_y_var,
            second_yAxis_label,
            inputFileData=inputFileData,
        )

    return outputFiles
