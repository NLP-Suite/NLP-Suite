# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "charts_util",
                                                 ['csv', 'os', 'collections', 're', 'tkinter', 'openpyxl', 'pandas',
                                                  'numpy', 'matplotlib', 'plotly', 'seaborn']) == False:
    sys.exit(0)

import plotly
from plotly.subplots import make_subplots

import numpy as np
import re

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import warnings
warnings.simplefilter(action='ignore', category=RuntimeWarning)

import tkinter.messagebox as mb
from collections import Counter
import pandas as pd
import os

import IO_csv_util
import IO_user_interface_util
import charts_Plotly_util
import charts_Excel_util
import statistics_csv_util


# Prepare the data (data_to_be_plotted) to be used in charts_Excel_util.create_excel_chart with the format:
#   one series: [[['Name1','Frequency'], ['A', 7]]]
#   two series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]]]
#   three series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]], [['Name3','Frequency'], ['C', 9]]]
#   more series: ..........
# inputFilename has the full path
# columns_to_be_plotted is a double list [[0, 1], [0, 2], [0, 3]]

# returns a double list of dataframes
def prepare_data_to_be_plotted_inExcel(inputFilename, columns_to_be_plotted, chart_type_list,
                                       count_var=0, column_yAxis_field_list=[]):
    # TODO temporary to measure process time
    # startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running Excel prepare_data_to_be_plotted_inExcel at',
    #                                              True, '', True, '', True)

    # index_col see https://stackoverflow.com/questions/12960574/pandas-read-csv-index-col-none-not-working-with-delimiters-at-the-end-of-each-li

    try:
        data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except:
        try:
            data = pd.read_csv(inputFilename, encoding='ISO-8859-1', on_bad_lines='skip')
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Warning',
                                               'Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 in reading into pandas the csv file ' + inputFilename)
            print(
                "Excel-util encountered errors with utf-8 encoding and switched to ISO-8859-1 encoding in reading into pandas the csv file " + inputFilename)
        except ValueError as err:
            if 'codec' in str(err):
                err = str(
                    err) + '\n\nExcel-util encountered errors with both utf-8 and ISO-8859-1 encoding in the function \'prepare_data_to_be_plotted_inExcel\' while reading into pandas the csv file\n\n' + inputFilename + '\n\nPlease, check carefully the data in the csv file; it may contain filenames with non-utf-8/ISO-8859-1 characters; less likely, the data in the txt files that generated the csv file may also contain non-compliant characters. Run the utf-8 compliance algorithm and, perhaps, run the cleaning algorithm that converts apostrophes.\n\nNO EXCEL CHART PRODUCED.'
            mb.showwarning(title='Input file read error',
                           message=str(err))
            return

    headers = list(data.columns.values)
    withHeader_var = False
    if len(headers)>0:
        withHeader_var = True
    if ('byDoc' in inputFilename and 'hyperlinks' in inputFilename) and (not 'group' in inputFilename):
        # sort by document ID and relevant column in headers[columns_to_be_plotted[0][0]]
        #   use [0][1] if saving with Index=False
        data = data.sort_values([headers[0], headers[columns_to_be_plotted[0][0]]])
        # save sorted data to inputFilename for later use
        data.to_csv(inputFilename, index=False)

    if len(data) == 0:
        return None
    headers = list(headers)
    count_msg, withHeader_msg = build_timed_alert_message(chart_type_list[0], withHeader_var, count_var)
    if count_var == 1:
        dataRange = get_dataRange(columns_to_be_plotted, data)
        # TODO hover_over_values not being passed, neither are any potential aggregate columns
        #   get_data_to_be_plotted_with_counts is less general than
        data_to_be_plotted = get_data_to_be_plotted_with_counts(inputFilename, withHeader_var, headers,
                                                                columns_to_be_plotted, column_yAxis_field_list,
                                                                dataRange)
    else:
        data_to_be_plotted = get_data_to_be_plotted_NO_counts(inputFilename, withHeader_var, headers,
                                                              columns_to_be_plotted, data)
    # TODO temporary to measure process time
    # IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running Excel prepare_data_to_be_plotted_inExcel at',
    #                                    True, '', True, startTime, True)

    return data_to_be_plotted


# bar chart aggregated by group  -----------------------------------------------------------------
#         plotList = ['Frequency']
# plot the words contained in each groupBy field values (e.g, the word 'Rome' in POS tag PPN)
# must first run compute_csv_column_frequencies_with_aggregation
# columns_to_be_plotted_yAxis=['Form']
def visualize_chart_byGroup(inputFilename, outputDir, chartPackage, dataTransformation, filesToOpen,
                            columns_to_be_plotted_byGroup, groupByList,
                            chart_title, columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis):
    pivot = False
    filesToOpen = []

    # the function compute_csv_column_frequencies produces plots
    # @@@ 9/29/2023
    outputFiles = statistics_csv_util.compute_csv_column_frequencies(GUI_util.window,
                                                                     inputFilename, None, outputDir, False,
                                                                     chartPackage, dataTransformation,
                                                                     # plot_cols=columns_to_be_plotted_numeric,
                                                                     plot_cols=columns_to_be_plotted_yAxis,
                                                                     hover_col=[],
                                                                     group_cols=groupByList,
                                                                     complete_sid=False,
                                                                     chart_title=chart_title,
                                                                     fileNameType=
                                                                     columns_to_be_plotted_yAxis[0],
                                                                     chartType='',
                                                                     pivot=pivot)
    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # new_inputFilename = chart_outputFilename[0]

    # temp_outputFilename[0] is the frequency filename (with no hyperlinks)
    # count_var = 0
    # remove_hyperlinks = False  # already removed in compute frequencies
    # headers = IO_csv_util.get_csvfile_headers_pandas(new_inputFilename)

    # 0 is the groupBy field with no-hyperlinks (e.g., NER)
    # 1 is the column plotted (e.g., Form)
    # 2 is the Document ID
    # 3 is the Document
    # 4 is Frequency
    # sel_column_name = IO_csv_util. = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document', inputFilename)(headers, 1)
    headers = IO_csv_util.get_csvfile_headers(inputFilename, ask_Question=False)
    docCol = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document', inputFilename)
    groupBy_Field = IO_csv_util.get_columnNumber_from_headerValue(headers, columns_to_be_plotted_yAxis[0],
                                                                  inputFilename)

    # columns_to_be_plotted_byGroup = [[docCol, groupBy_Field, 3]]  # will give different bars for each value
    columns_to_be_plotted_byGroup = [[docCol, groupBy_Field]]  # will give different bars for each value
    # columns_to_be_plotted_byGroup = [[2, 0, 3]]  # will give different bars for each value
    # columns_to_be_plotted_byGroup = [[1, 4, 0, 2, 3]] # will give different bars for each value
    # outputFileLabel='by_' + str(groupByList[0])
    # chart_title='Frequency Distribution of ' + str(columns_to_be_plotted_yAxis[0]) + ' by ' + str(groupByList[0])
    # hover_label=[]
    column_yAxis_label = 'Frequencies'
    # if chartPackage == "Excel":
    #     column_name = IO_csv_util.get_headerValue_from_columnNumber(headers, 1)
    # chart is visualized in compute_csv_column_frequencies
    # number_column_entries = len(IO_csv_util.get_csv_field_values(new_inputFilename, column_name))
    # # in visualize_chart_byGroup
    # outputFiles = run_all(columns_to_be_plotted_byGroup, new_inputFilename, outputDir,
    #                                           outputFileLabel=outputFileLabel, # outputFileNameType + 'byDoc', #outputFileLabel,
    #                                           chartPackage=chartPackage,
    #                                           dataTransformation=dataTransformation,
    #                                           chart_type_list=['bar'],
    #                                           chart_title=chart_title,
    #                                           column_xAxis_label_var='',
    #                                           column_yAxis_label_var=column_yAxis_label,
    #                                           hover_info_column_list=hover_label,
    #                                           # count_var is set in the calling function
    #                                           #     0 for numeric fields;
    #                                           #     1 for non-numeric fields
    #                                           count_var=count_var,
    #                                           remove_hyperlinks=remove_hyperlinks)
    # if outputFiles!=None:
    #     if len(chart_outputFilename) > 0:
    #         filesToOpen.append(chart_outputFilename)
    return filesToOpen


# def visualize_chart_byDoc(inputFilename, outputDir, outputFileNameType, chartPackage, dataTransformation, filesToOpen,
#                         columns_to_be_plotted_byDoc, columns_to_be_plotted_yAxis,
#                         count_var, pivot, chart_title, hover_label):
#     column_yAxis_label = 'Frequencies'
#     remove_hyperlinks = True
#     # by DOCUMENT counting the qualitative values ---------------------------------------------------------------------------
#     if count_var == 1:  # for alphabetic fields that need to be counted for display in a chart
#         # TODO TONY using this function, the resulting output file is in the wrong format and would need to be pivoted to be used
#         # temp_outputFilename = statistics_csv_util.compute_csv_column_frequencies(inputFilename, ["Document ID",'Document'], ['POS'], outputDir, chart_title, graph=False,
#         #                              complete_sid=False,  chartPackage='Excel', dataTransformation='No transformation')
#
#         # TODO TONY the compute_csv_column_frequencies_with_aggregation should export the distinct values of a column
#         #   in separate columns so that they will be plotted with different colors as separate series
#
#         # in visualize_chart_byDoc
#         temp_outputFilename = statistics_csv_util.compute_csv_column_frequencies(
#             GUI_util.window,
#             inputFilename, None, outputDir,
#             False, chartPackage, dataTransformation,
#             # plot_cols=columns_to_be_plotted_numeric,
#             plot_cols=columns_to_be_plotted_yAxis,
#             hover_col=[],
#             chart_title=chart_title + ' by Document',
#             group_cols=['Document ID', 'Document'],
#             complete_sid=False,
#             fileNameType=columns_to_be_plotted_yAxis[0], chartType='', pivot=pivot)
#         new_inputFilename = temp_outputFilename[0]
#         # temp_outputFilename[0] is the frequency filename (with no hyperlinks)
#         remove_hyperlinks = False  # already removed in compute frequencies
#         # 2,3 are the Document and Frequency columns in temp_outputFilename
#         # columns_to_be_plotted_byDoc = [[2,3]] # document 2, first item; frequencies 3 second item
#         # columns_to_be_plotted_byDoc = [[1,2],[1,3]]
#         # pivot = True
#
#         headers = IO_csv_util.get_csvfile_headers_pandas(new_inputFilename)
#
#         if pivot == True:
#             columns_to_be_plotted_byDoc_len = len(columns_to_be_plotted_byDoc[0])
#             columns_to_be_plotted_byDoc = []
#             for i in range(columns_to_be_plotted_byDoc_len, len(headers)):
#                 columns_to_be_plotted_byDoc.append([columns_to_be_plotted_byDoc_len - 1, i])
#         else:
#             # 1 is the Document with no-hyperlinks,
#             # 2 is the column plotted (e.g., Gender) in temp_outputFilename
#             # 3 is Frequency,
#             # TODO TONY we should ask the same type of question for columns that are already in quantitative form if we want to compute a single MEAN value
#             sel_column_name = IO_csv_util.get_headerValue_from_columnNumber(headers, 2)
#             # item 1 is the column of Document with no-hyperlinks,
#             # item 2 is the column plotted (e.g., Gender) in temp_outputFilename
#             # item 3 is the column of Frequency,
#             columns_to_be_plotted_byDoc = [[2, 0, 3]]  # will give different bars for each value
#             # TODO temporarily disconnected until we figure out a way to not repeat this questions several times
#             # if chartPackage == "Excel":
#                 # column_name = IO_csv_util.get_headerValue_from_columnNumber(headers, 1)
#                 # number_column_entries = len(
#                 #     IO_csv_util.get_csv_field_values(new_inputFilename, column_name))
#                 # if number_column_entries > 1:
#                 #     answer = tk.messagebox.askyesno("Warning", "For the chart of '" + sel_column_name + "' by document, do you want to:\n\n  (Y) sum the values across all " + str(number_column_entries) + " '" + column_name + "';\n  (N) use all " + str(number_column_entries) + " distinct column values.")
#                 #     if answer:
#                 #         # [[1, 3]] will give one bar for each doc, the sum of all values in plot_colsumn to be plotted
#                 #         columns_to_be_plotted_byDoc = [[1, 3]]
#                 #     else:
#                 #         # [[1, 3, 2]] will give different bars for each value
#                 #         # Document, Field to be plotted (e.g., POS), Sentence ID
#                 #         columns_to_be_plotted_byDoc = [[1, 3, 2]]
#                 # reset the original value to be used in charts by sentence index
#
#     # by DOCUMENT NOT counting; quantitative values ---------------------------------------------------------------------------
#     else:
#         new_inputFilename = inputFilename
#
#     if outputFileNameType != '':
#         outputFileLabel = 'byDoc_' + outputFileNameType
#     else:
#         outputFileLabel = 'byDoc'
#
#     # TODO Tony when plotting bar charts in Plotly with documents in the X-axis we need to remove the path and just keep the tail
#     #   or the display is too messy; it works like that in Excel
#
#     # in visualize_chart_byDoc
#     outputFiles = run_all(columns_to_be_plotted_byDoc, new_inputFilename, outputDir,
#                                    outputFileLabel=outputFileLabel,
#                                    # outputFileNameType + 'byDoc', #outputFileLabel,
#                                    chartPackage=chartPackage,
#                                    dataTransformation=dataTransformation,
#                                    chart_type_list=['bar'],
#                                    chart_title=chart_title + ' by Document',
#                                    column_xAxis_label_var='',
#                                    column_yAxis_label_var=column_yAxis_label,
#                                    hover_info_column_list=hover_label,
#                                    # count_var is set in the calling function
#                                    #     0 for numeric fields;
#                                    #     1 for non-numeric fields
#                                    count_var=0,
#                                    remove_hyperlinks=remove_hyperlinks)
#     if outputFiles!=None:
#         if len(chart_outputFilename) > 0:
#             filesToOpen.append(chart_outputFilename)
#     return filesToOpen

def visualize_chart_bySent(inputFilename, outputDir, chartPackage, dataTransformation, filesToOpen, n_documents,
                           columns_to_be_plotted_byDoc, columns_to_be_plotted_yAxis, count_var, pivot):
    # TODO temporary to measure process time
    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running Excel bySent at',
                                                   True, '', True, '', True)
    # inputFilename = data_pivot(inputFilename, 'Sentence ID', 'Yngve score')
    # columns_to_be_plotted_bySent = [[columns_to_be_plotted_bySent[0][0]]]
    if count_var == 1:  # for alphabetic fields that need to be counted for display in a chart
        temp_outputFilename = statistics_csv_util.compute_csv_column_frequencies(
            GUI_util.window,
            inputFilename,
            None, outputDir,
            False,

            chartPackage,
            dataTransformation,
            plot_cols=columns_to_be_plotted_numeric,
            hover_col=[],
            group_cols=[['Document ID', 'Document', 'Sentence ID']],
            complete_sid=True,
            fileNameType='CSV',
            chartType='',
            pivot=pivot)
        inputFilename = temp_outputFilename[0]
        if pivot:
            inputFilename = statistics_csv_util.csv_data_pivot(temp_outputFilename[0], 'Sentence ID',
                                                               'Gender', no_hyperlinks=True)
        else:
            # Using the output from statistics_csv_util.compute_csv_column_frequencies
            #   Document, Frequency, Sentence ID, Field to be plotted (e.g., POS)
            # columns_to_be_plotted_bySent = [[1, 4, 2, 3]]
            columns_to_be_plotted_bySent = [[2, 4]]
    else:  # numeric values of field(s) to be plotted
        columns_to_be_plotted_bySent = []
        if n_documents > 1:
            for i in range(0, len(columns_to_be_plotted_numeric)):
                # For multiple series, by document & sentence IDs any combinations of Document, Frequency, Sentence ID, Field to be plotted
                #       does not work
                # Only the following works:
                #   YES [[Document, Column 1 to be plotted], [Document, Column 2 to be plotted], ...]
                # NO [[Document, Column 1 to be plotted, Sentence ID], [Document, Column 2 to be plotted, Sentence ID], ...]
                #   sentence IDs are repeated on X-axis rather than Docs
                # NO [[Document, Sentence ID, Column 1 to be plotted], [Document, Sentence ID, Column 2 to be plotted], ...]
                #   frequencies or scores on X-axis
                # NO [[Document, Column 1 to be plotted, Column 2 to be plotted, Sentence ID]]
                #   only one series plotted with Docs on X-axis
                columns_to_be_plotted_bySent.append([docCol + 1, columns_to_be_plotted_numeric[i][0]])
        else:
            # Sentence ID, Frequency
            columns_to_be_plotted_bySent.append([sentCol, columns_to_be_plotted_numeric[i][0]])

    if n_documents > 1:
        chart_title = chart_title + ' by Document & Sentence Index'
        xAxis_label = ''
    else:
        chart_title = chart_title + ' by Sentence Index'
        xAxis_label = 'Sentence index'

    if outputFileNameType != '':
        outputFileLabel = 'bySent_' + outputFileNameType
    else:
        outputFileLabel = 'bySent'

    outputFiles = run_all(columns_to_be_plotted_bySent, inputFilename, outputDir,
                          outputFileLabel=outputFileLabel,
                          chartPackage=chartPackage,
                          dataTransformation=dataTransformation,
                          chart_type_list=['line'],
                          chart_title=chart_title,
                          column_xAxis_label_var=xAxis_label,
                          column_yAxis_label_var=column_yAxis_label,
                          hover_info_column_list=hover_label,
                          count_var=0,  # always 0 when plotting by sentence index
                          complete_sid=True,
                          remove_hyperlinks=True)

    if outputFiles != None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    # TODO temporary to measure process time
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running Excel bySent at',
                                       True, '', True, startTime, True)


# TODO columns_to_be_plotted comes in a single list to be exported to run_all as double list
# columns_to_be_plotted, columns_to_be_plotted_bySent, columns_to_be_plotted_byDoc
#   all double lists [[]]
#   BUT they are passed by calling functions as single lists []
#       and converted to double lists for run_all
#       e.g., columns_to_be_plotted_xAxis=[],
#             columns_to_be_plotted_yAxis=['Sentiment score (Median)', 'Arousal score (Median)', 'Dominance score (Median)']
#       e.g., columns_to_be_plotted_xAxis=[],
#             columns_to_be_plotted_yAxis=['Yngve score', 'Frazier score']
#       e.g., columns_to_be_plotted_xAxis=[],
#             columns_to_be_plotted_yAxis=['Yngve score']
# the variable groupByList,plotList, chart_title_label are used to compute column statistics
#   groupByList is typically the list ['Document ID', 'Document'] or just ['Document']
#   plotList is the list of fields to be plotted
#   chart_title_label is used as part of the chart_title when plotting the fields statistics (Mean, Mode, Skewness,...)
# X-axis

def _bin_numeric_columns_for_chart(inputFilename, outputDir, value_col_indices, threshold=20, max_bins=10):
    """Numeric X-axis binning (the 'TODO Naman' note): for a FREQUENCY bar chart of numeric values,
    when a plotted column holds more than `threshold` distinct numeric values, replace those values
    with ordered range labels (e.g. '03: 24.6-36.4') so the chart shows ~max_bins value CLASSES
    instead of a forest of individual-value bars. Writes a binned copy of the csv and returns its
    path if anything was binned; returns None otherwise (non-numeric column, few distinct values, or
    any error), so the caller falls back to the original file unchanged."""
    try:
        import numpy as np
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        return None
    binned_any = False
    for idx in value_col_indices:
        try:
            if idx is None or idx < 0 or idx >= len(df.columns):
                continue
            col = df.columns[idx]
            s = pd.to_numeric(df[col], errors='coerce')
            if s.notna().sum() == 0:                 # not a numeric column -> leave alone
                continue
            if s.dropna().nunique() <= threshold:    # few enough distinct values already
                continue
            vmin, vmax = float(s.min()), float(s.max())
            if vmin == vmax:
                continue
            edges = np.linspace(vmin, vmax, max_bins + 1)
            # ordered, self-describing labels; the zero-padded prefix keeps them sortable
            labels = [f"{j + 1:02d}: {edges[j]:.4g}-{edges[j + 1]:.4g}" for j in range(max_bins)]
            df[col] = pd.cut(s, bins=edges, labels=labels, include_lowest=True).astype(str)
            binned_any = True
        except Exception:
            continue
    if not binned_any:
        return None
    try:
        outFile = os.path.join(outputDir, 'NLP_binned_' + os.path.basename(inputFilename))
        df.to_csv(outFile, index=False)
        return outFile
    except Exception:
        return None


def visualize_chart(chartPackage, dataTransformation, inputFilename, outputDir,
                    columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis,
                    chart_title, count_var, hover_label, outputFileNameType, column_xAxis_label,
                    groupByList, plotList, chart_title_label, column_yAxis_label='Frequencies', pivot=False):
    outputFiles= []
    filesToOpen = []
    columns_to_be_plotted_numeric = []
    columns_to_be_plotted_byDoc = []
    columns_to_be_plotted_bySent = []

    if chartPackage != 'No charts':
        chart_outputFilenameSV = ''
    else:
        return

        # the run_all always expects a double list with 2 values, e.g., [[0,0], [1,1]
        #   so, when only one field is passed, we add the same field twice
        # TODO
        # columns_to_be_plotted_numeric = [[1, 1], [3, 3]]  # for complexity scores; duplicates columns gives right plot
        # columns_to_be_plotted_numeric = [[1, 3]]  # for complexity scores; duplicates columns gives right plot
        # columns_to_be_plotted_numeric = [[0, 2], [0, 3]]  # for ngrams

    # pivot = True will list for every document all the separate values of the selected item to be plotted
    #       = False will sum all the individual values
    # count_var should always be TRUE to get frequency distributions

    # in the bar charts columns_to_be_plotted, when numeric data are passed,
    #   the first item is the column of numeric values
    #   the second item is the X-axis
    #   see the example of call in get_ngramlist
    headers = IO_csv_util.get_csvfile_headers_pandas(inputFilename)
    if len(headers) == 0:
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Empty csv file',
                                           'The file\n\n' + inputFilename + '\n\nis empty. No charts can be produced using this csv file.\n\nPlease, check the file and try again.',
                                           True, '', True, '', False)
        # mb.showwarning(title='Empty file', message='The file\n\n' + inputFilename + '\n\nis empty. No charts can be produced using this csv file.\n\nPlease, check the file and try again.')
        print(
            'The file\n\n' + inputFilename + '\n\nis empty. No charts can be produced using this csv file.\n\nPlease, check the file and try again.')
        return filesToOpen
    # A file with headers but no data rows (e.g. an empty word-class subcategory such as modal verbs
    # on a Stanza table) cannot be plotted; skip it gracefully rather than erroring in the plotting code.
    try:
        if pd.read_csv(inputFilename, nrows=1).shape[0] == 0:
            print('The file\n\n' + inputFilename + '\n\nhas no data rows; skipping chart.')
            return filesToOpen
    except Exception:
        pass
    field_number_xAxis = None
    if len(columns_to_be_plotted_xAxis) == 1:
        field_number_xAxis = IO_csv_util.get_columnNumber_from_headerValue(headers, columns_to_be_plotted_xAxis[0],
                                                                           inputFilename)

    if "Document" in str(groupByList): # regardless of Document or Document ID
        docCol = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Document', inputFilename)
        # we need to visualize the doc filename
        byDoc = True
    else:
        byDoc = False
    if "Sentence ID" in headers:
        sentCol = IO_csv_util.get_columnNumber_from_headerValue(headers, 'Sentence ID', inputFilename)
        bySent = True
    else:
        bySent = False

    # in visualize_chart
    for i in range(0, len(columns_to_be_plotted_yAxis)):
        # get numeric value of header, necessary for run_all
        field_number_yAxis = IO_csv_util.get_columnNumber_from_headerValue(headers, columns_to_be_plotted_yAxis[i],
                                                                           inputFilename)
        if field_number_yAxis == None:
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
        # columns_to_be_plotted_numeric[0].pop(0)
        # columns_to_be_plotted_numeric[0].insert(0, docCol + 1)
        # columns_to_be_plotted_byDoc = columns_to_be_plotted_numeric

        # numeric X-axis binning (the former 'TODO Naman' note) is implemented below, just before the
        # bar chart is built, via _bin_numeric_columns_for_chart: a numeric column with many distinct
        # values is grouped into ~10 range classes so the X-axis is readable rather than a forest of bars.

    # when pivoting data
    # columns_to_be_plotted_bySent = []
    # for i in range(1, n_documents):
    #     columns_to_be_plotted_bySent.append([0, i])
    count_var_SV = count_var

    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename)

    # numeric X-axis binning (TODO Naman): for a frequency bar chart of a numeric column with many
    # distinct values, plot ~10 value CLASSES instead of a forest of individual-value bars. Narrowly
    # gated (frequency counts, no explicit X-axis field) and confined to this bar chart -- byDoc/bySent
    # and every other path keep the original file untouched.
    chartInputFilename = inputFilename
    if count_var == 1 and len(columns_to_be_plotted_xAxis) == 0:
        binnedFilename = _bin_numeric_columns_for_chart(inputFilename, outputDir,
                                                        [pair[1] for pair in columns_to_be_plotted_numeric])
        if binnedFilename:
            chartInputFilename = binnedFilename

    # standard bar chart ------------------------------------------------------------------------------
    # Form	Lemma	POS	Record ID	Sentence ID	Document ID	Document
    # columns_to_be_plotted_numeric = [[0,0], [1,1]] with count_var = 1 since these values need to be counted
    # @@@ 12/22/2024
    if isinstance(columns_to_be_plotted_numeric, list): # only plot if not empty list
        outputFiles = run_all(columns_to_be_plotted_numeric, chartInputFilename, outputDir,
                              outputFileLabel=outputFileNameType,
                              chartPackage=chartPackage,
                              dataTransformation=dataTransformation,
                              chart_type_list=['bar'],
                              chart_title=chart_title,
                              column_xAxis_label_var=column_xAxis_label,
                              column_yAxis_label_var=column_yAxis_label,
                              hover_info_column_list=hover_label,
                              count_var=count_var)  # always 1 to get frequencies of values, except for n-grams where we already pass stats

        if outputFiles != None:
            chart_outputFilenameSV = outputFiles
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
        else:
            # no point continuing to process more charts if an error was encountered and None was returned
            #   typically because of too many rows for Excel to handle, when Excel is used
            return

    n_documents=0
    # by DOCUMENT
    if byDoc:
        # TODO depends on how many documents we have;
        #   no point charting one document since these charts would be the same as no document
        n_documents = IO_csv_util.GetMaxValueInCSVField(inputFilename, 'visualize_charts_util', 'Document ID')
        if n_documents > 1:
            column_yAxis_label = 'Frequencies'
            columns_to_be_plotted_byGroup = []
            chart_title = chart_title + ' by Document'
            for header in groupByList:
                groupCol = IO_csv_util.get_columnNumber_from_headerValue(headers, header, inputFilename)
                columns_to_be_plotted_byGroup.append([groupCol, field_number_yAxis])

            # by DOCUMENT
            outputFiles = visualize_chart_byGroup(inputFilename, outputDir,
                                                  chartPackage, dataTransformation,
                                                  filesToOpen,
                                                  columns_to_be_plotted_byGroup, groupByList,
                                                  chart_title,
                                                  columns_to_be_plotted_xAxis,
                                                  columns_to_be_plotted_yAxis)

            if outputFiles != None:
                chart_outputFilenameSV = outputFiles
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
    # bar chart aggregated by group  (e.g., form values by POS tags) -----------------------------------------------------------------
    #   avoid plotting by ['Document ID', 'Document'] as groupBy; done in chart byDoc
    if n_documents > 1 and len(groupByList) > 0 and groupByList != ['Document ID', 'Document']:
        columns_to_be_plotted_byGroup = []
        for header in groupByList:
            groupCol = IO_csv_util.get_columnNumber_from_headerValue(headers, header, inputFilename)
            # [POS, Form]
            columns_to_be_plotted_byGroup.append([groupCol, field_number_yAxis])
        outputFiles = visualize_chart_byGroup(inputFilename, outputDir, chartPackage, dataTransformation,
                                              filesToOpen,
                                              columns_to_be_plotted_byGroup, groupByList, chart_title,
                                              columns_to_be_plotted_xAxis, columns_to_be_plotted_yAxis)

        if outputFiles != None:
            chart_outputFilenameSV = outputFiles
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # line plots by SENTENCE index -----------------------------------------------------------------------
    # sentence index value are the first item in the list [[7,2]] i.e. 7
    #   plot values are the second item in the list [[7,2]] i.e. 2
    count_var = count_var_SV
    # not all csv output contain the Sentence ID (e.g., line length function)
    # TODO Samir; to test the add_missing_IDs you must change bySent=False to bySent=True
    bySent = False
    if bySent:
        fileToOpen = visualize_chart_bySent(inputFilename, outputDir, chartPackage, filesToOpen, n_documents,
                                            columns_to_be_plotted_byDoc, columns_to_be_plotted_yAxis, count_var, pivot)

    # compute field STATISTICS (mean, median, skeweness, kurtosis...)--------------------------------------------------------------
    # TODO THE FIELD MUST CONTAIN NUMERIC VALUES
    # plotList (a list []) contains the columns headers to be used to compute their stats
    if len(groupByList) > 0 and not isinstance(outputFiles, str):  # compute only if list is not empty
        if count_var == 1:
            if len(outputFiles) == 0:
                return filesToOpen # []
            temp_inputFilename = outputFiles[0]
        else:
            temp_inputFilename = inputFilename
        if plotList == ['Frequency']:
            plotList = ['Frequency_' + str(columns_to_be_plotted_yAxis[0])]
        outputFiles = statistics_csv_util.compute_csv_column_statistics(GUI_util.window, temp_inputFilename,
                                                                        outputDir,
                                                                        outputFileNameType, groupByList,
                                                                        plotList, chart_title_label,
                                                                        chartPackage, dataTransformation)

        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

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
#             columns_to_be_plotted_yAxis=['Sentiment score (Median)', 'Arousal score (Median)', 'Dominance score (Median)']
#       e.g., columns_to_be_plotted_xAxis=[],
#             columns_to_be_plotted_yAxis=['Yngve score', 'Frazier score']
#       e.g., columns_to_be_plotted_xAxis=[],
#             columns_to_be_plotted_yAxis=['Yngve score']
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

def run_all(columns_to_be_plotted, inputFilename, outputDir, outputFileLabel,
            chartPackage, dataTransformation, chart_type_list, chart_title, column_xAxis_label_var,
            hover_info_column_list=[],
            count_var=0,
            column_yAxis_label_var='Frequencies',
            column_yAxis_field_list=[],
            reverse_column_position_for_series_label=False,
            series_label_list=[], second_y_var=0, second_yAxis_label='',
            complete_sid=False, remove_hyperlinks=False, csv_field_Y_axis_list=[], X_axis_var=[]):
    # get the chart type from the GUI user selection
    chart_type_list = [GUI_util.charts_type_options_widget.get().split(' ')[0]]

    use_Plotly = 'plotly' in chartPackage.lower()
    # added by Tony, May 2022 for complete sentence index
    # the file should have a column named Sentence ID
    # the extra parameter "complete_sid" is set to True by default to avoid extra code mortification elsewhere
    if complete_sid:
        # TODO Samir
        inputFilename = add_missing_IDs(inputFilename, inputFilename)
        # complete_sentence_index(inputFilename)
    if use_Plotly:
        if 'static' in chartPackage.lower():
            static_flag = True
        else:
            static_flag = False
        # TODO Tony when plotting bar charts with documents in the X-axis we need to remove the path and just keep the tail
        #   or the display is too messy; it works well with Excel
        if 'Kurtosis' in chart_title:
            chart_type_list = ["Bar"]
        Plotly_outputFilename = charts_Plotly_util.create_Plotly_chart(inputFilename=inputFilename,
                                                                       outputDir=outputDir,
                                                                       chart_title=chart_title,
                                                                       chart_type_list=chart_type_list,
                                                                       cols_to_plot=columns_to_be_plotted,
                                                                       column_xAxis_label=column_xAxis_label_var,
                                                                       column_yAxis_label=column_yAxis_label_var,
                                                                       remove_hyperlinks=remove_hyperlinks,
                                                                       static_flag=static_flag,
                                                                       csv_field_Y_axis_list=csv_field_Y_axis_list,
                                                                       X_axis_var=X_axis_var)
        return Plotly_outputFilename

    data_to_be_plotted = prepare_data_to_be_plotted_inExcel(inputFilename,
                                                            columns_to_be_plotted,
                                                            chart_type_list, count_var,
                                                            column_yAxis_field_list)
    def list_of_lists_to_csv(data, csv_file_path):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_csv(csv_file_path, index=False)

    data_to_be_plotted_2 = []
    if len(data_to_be_plotted)>0:
        if type(data_to_be_plotted[0]) == list:
            list_of_lists_to_csv(data_to_be_plotted[0], "temptemp2.csv")
            df = statistics_csv_util.data_transformation('temptemp2.csv', dataTransformation)
            os.remove('temptemp2.csv')
            data_to_be_plotted_2 = [[df.columns.tolist()] + df.values.tolist()]
    if len(data_to_be_plotted_2) == len(data_to_be_plotted):
        data_to_be_plotted = data_to_be_plotted_2
    if data_to_be_plotted == None or data_to_be_plotted == []:
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
    if data_to_be_plotted == None:
        return
    else:
        withHeader_var = IO_csv_util.csvFile_has_header(inputFilename)  # check if the file has header
        data, headers = IO_csv_util.get_csv_data(inputFilename, withHeader_var)  # get the data and header

        # the lines below handle specifically the "Form-Lemma" annotator because "form-lemma" is not processed in statistics_csv_util.py
        def double_level_grouping_and_frequency(data, plot_cols, group_cols):
            # Calculate the counts for each column
            group_cols_count = data[group_cols[0]].value_counts().reset_index()
            group_cols_count.columns = [group_cols[0], f'Frequency_{group_cols[0]}']
            plot_cols_count = data.groupby(group_cols)[plot_cols[0]].value_counts().reset_index(
                name=f'Frequency_{plot_cols[0]}')
            # Merge the counts back into the original dataframe
            data_final = pd.merge(group_cols_count, plot_cols_count, how='inner', on=group_cols[0])
            data_final = data_final.drop_duplicates()  # Remove potential duplicate rows
            return data_final
            # Convert DataFrame into list of lists
            # data_list = data_final.values.tolist()
            # Extract 2nd and 3rd column into one list of lists and 4th and 5th into another
            # list_1 = [[row[2], row[3]] for row in data_list]
            # list_2 = [[row[0], row[1]] for row in data_list]
            # list_1.insert(0, ['Form values', 'Frequencies of Form'])
            # list_2.insert(0, ['Lemma values', 'Frequencies of Lemma'])
            # return [list_1, list_2]

        if len(data_to_be_plotted) == 2 and data_to_be_plotted[0][0] == ['Form values', 'Frequencies of Form'] and \
                data_to_be_plotted[1][0] == ['Lemma values', 'Frequencies of Lemma']:
            data = pd.DataFrame(data, columns=headers)
            data_to_be_plotted = double_level_grouping_and_frequency(data, ['Form'], ['Lemma'])
            data_to_be_plotted.to_csv("Temptemp.csv", index=False)
            data_final = statistics_csv_util.data_transformation("Temptemp.csv", dataTransformation)
            data_list = data_final.values.tolist()
            list_1 = [[row[2], row[3]] for row in data_list]
            list_2 = [[row[0], row[1]] for row in data_list]
            list_1.insert(0, ['Form values', 'Frequencies of Form' + "_" + dataTransformation])
            list_2.insert(0, ['Lemma values', 'Frequencies of Lemma' + "_" + dataTransformation])
            data_to_be_plotted = [list_1, list_2]
            os.remove("Temptemp.csv")

        chart_title = chart_title
        outputFiles = charts_Excel_util.create_excel_chart(GUI_util.window, data_to_be_plotted,
                                                           inputFilename, outputDir,
                                                           outputFileLabel, chart_title, chart_type_list,
                                                           column_xAxis_label_var, column_yAxis_label_var,
                                                           hover_info_column_list,
                                                           reverse_column_position_for_series_label,
                                                           series_label_list, second_y_var, second_yAxis_label)

    return outputFiles


def build_timed_alert_message(chart_type, withHeader_var, count_var):
    if withHeader_var == 1:
        withHeader_msg = 'WITH HEADERS'
    else:
        withHeader_msg = 'WITHOUT HEADERS'
    if count_var == 1:
        count_msg = 'WITH COUNTS'
    else:
        count_msg = 'WITHOUT COUNTS'
    return withHeader_msg, count_msg


# split the pairs of gui x y values into two separate lists of x axis values and y axis value
def get_xaxis_yaxis_values(columns_to_be_plotted):
    x = [a[0] for a in columns_to_be_plotted]  # select all the x axis number and put them in a list
    y = [a[1] for a in columns_to_be_plotted]  # select all the y axis number and put them in a list
    x1 = [int(b) for b in x]  # convert them into int type
    y1 = [int(b) for b in y]  # convert them into int type
    return x1, y1


def get_dataRange(columns_to_be_plotted, data):
    dataRange = []
    for i in range(len(columns_to_be_plotted)):
        for row in data.itertuples(index=False):
            try:
                value = row[columns_to_be_plotted[0][0]]

                dataRange.append(value)
            except IndexError:
                continue
    dataRange = [dataRange[i:i + len(data)] for i in range(0, len(dataRange), len(data))]
    return dataRange


# TODO if hover_over columns are passed, it should concatenate all values, instead of displaying the first one only
#   (e.g. an example run the going UP function in WordNet)
# this function seems to be less general than def compute_csv_column_frequencies; that function handl;es aggregation and hover over effects
# we should consolidate the two and use the most general one under the heading get_data_to_be_plotted_with_counts

# def get_data_to_be_plotted_with_counts(inputFileName,withHeader_var,headers,columns_to_be_plotted,column_yAxis_field_list,dataRange):
#     CALL compute_column_frequencies(columns_to_be_plotted, dataRange, headers,column_yAxis_field_list)
#
#     CALLED compute_column_frequencies(columns_to_be_plotted, data_list, headers,specific_column_value_list=[]):


# -----------------------------------------------------------------
# MUST COMPUTE HOVER OVER VALUES!!! see below

# create a list of unique words to be displayed in hover over
# result = IO_files_util.openCSVFile(outputFilenameCSV1, 'r', 'utf-8')
# DataCaptured = csv.reader(result)
# words = set()
# for row in DataCaptured:
#     words.add(row[0])
# also IO_csv_util.get_csv_field_values(inputfile_name, column_name)


def get_data_to_be_plotted_with_counts(inputFilename, withHeader_var, headers, columns_to_be_plotted,
                                       specific_column_value_list, data_list):
    data_to_be_plotted = []
    # data_to_be_plotted = compute_column_frequencies_4Excel(columns_to_be_plotted, dataRange, headers, column_yAxis_field_list)

    column_list = []
    column_frequencies = []
    column_stats = []
    specific_column_value = ''
    complete_column_frequencies = []
    if len(data_list) != 0:
        for k in range(len(columns_to_be_plotted)):
            res = []
            if len(specific_column_value_list) > 0:
                specific_column_value = specific_column_value_list[k]
            # get all the values in the selected column
            try:
                #  TODO the datalist is like [['NN','NN'], ...] so the code produces bad results
                #       when multiple series side-by-side (e.g., form and lemma values) need to be plotted
                if 'Search Word' in str(headers):
                    column_list = [i[0] for i in data_list[k]] # works for search function
                else:
                    column_list = []
                    for val in data_list[k]:
                        column_list.append(val)
            except IndexError:
                continue
            counts = list(Counter(column_list).most_common())
            if len(headers) > 0:
                id_name_num = columns_to_be_plotted[k][0]
                id_name = headers[id_name_num]
                column_name_num = columns_to_be_plotted[k][1]
                column_name = headers[column_name_num]
                if len(specific_column_value_list) == 0:
                    column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
                else:
                    for y in range(len(specific_column_value_list)):
                        column_frequencies = [[id_name,
                                               "Frequencies of " + str(specific_column_value) + " in Column " + str(
                                                   column_name)]]
            else:
                id_name_num = columns_to_be_plotted[k][0]
                id_name = "column_" + str(id_name_num + 1)
                column_name_num = columns_to_be_plotted[k][1]
                column_name = "column_" + str(column_name_num + 1)
                if len(specific_column_value) == 0:
                    column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
                else:
                    for y in range(len(specific_column_value_list)):
                        column_frequencies = [[id_name,
                                               "Frequencies of " + str(specific_column_value) + " in Column_" + str(
                                                   column_name_num + 1)]]
            if len(specific_column_value) == 0:
                for value, count in counts:
                    column_frequencies.append([value, count])
            else:
                for i in range(len(column_list)):
                    if column_list[i] == specific_column_value:
                        res.append(1)
                    else:
                        res.append(0)
                for j in range(len(data_list[k])):
                    column_frequencies.append([data_list[k][j][0], res[j]])
            data_to_be_plotted.append(column_frequencies)

    return data_to_be_plotted


# [[0,2]], [0], [2]
def get_data_to_be_plotted_NO_counts(inputFilename, withHeader_var, headers, columns_to_be_plotted, data):
    data_to_be_plotted = []
    for gp in columns_to_be_plotted:
        data.iloc[:, gp[1]].replace('N/A', 0)
        # data.iloc[:, gp[1]].astype('float')
        tempData = data.iloc[:, gp]
        data_to_be_plotted.append(data.iloc[:, gp])
    # retruns a double list, first list of a dataframe of plot columns (e.g., sentiment score, sentiment frequencies), the second another dataframe of Document and doc freq
    # select columns from dataframe
    # complete this
    # for colNumber in columns_to_be_plotted: #colNumber [3, 4]
    #     colname = data.columns[colNumber[0]] # [columns_to_be_plotted[0][1]]
    #     data_to_be_plotted = data[colname]
    return data_to_be_plotted


# header_check moved to IO_csv_util (single canonical copy); call IO_csv_util.header_check(...)


# TODO Samir very slow
def process_sentenceID_record(Row_list, Row_list_new, index,
                              start_sentence, end_sentence,
                              header, sentenceID_pos, docCol_pos, docName_pos, frequency_pos,
                              save_current):
    # TODO temporary to measure process time
    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running Excel process_sentenceID_record at',
                                                   True, '', True, '', True)
    # range(start, stop, step)
    # end_sentence is always skipped; the range of integers end at end_sentence – 1
    for i in range(start_sentence, end_sentence, 1):
        temp = [''] * len(header)
        # loop through headers for Sentence ID, Document ID, and Document to insert missing values
        for j in range(len(header)):
            if j == sentenceID_pos:
                # insert Sentence ID
                temp[j] = i
                # when adding a new Sentence ID, insert a frequency value of 0,
                #   in every occurrence of a frequency column, whatever the name may be (Frequency, Frequencies, Number of, Score)
                for k in range(0, len(frequency_pos)):
                    if frequency_pos[k] != '':
                        temp[frequency_pos[i]] = 0
            elif j == docCol_pos:
                # insert Document ID
                temp[j] = Row_list[index][docCol_pos]
            elif j == docName_pos:
                # insert Document
                temp[j] = Row_list[index][docName_pos]
        Row_list_new.append(temp)

    if save_current:
        Row_list_new.append(Row_list[index])
    # TODO temporary to measure process time
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running Excel process_sentenceID_record at',
                                       True, '', True, startTime, True)

    return Row_list_new


# written by Yi Wang
# rewritten by Roberto July 2022

# input can be a csv filename or a dataFrame
# output is a csv file
# TODO Samir very slow
def add_missing_IDs(input, outputFilename):
    from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text
    # TODO temporary to measure process time
    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running Excel Add missing IDs at',
                                                   True, '', True, '', True)
    if isinstance(input, pd.DataFrame):
        df = input
    else:
        df = pd.read_csv(input, encoding='utf-8', on_bad_lines='skip')
    # define variables
    start_sentence = 1  # first sentence in loop
    end_sentence = 1  # last sentence in loop
    number_sentences = []
    Row_list_new = []
    sentenceID_pos, docCol_pos, docName_pos, frequency_pos, header = IO_csv_util.header_check(input)
    Row_list = IO_csv_util.df_to_list(df)
    len_Row_list = len(Row_list)
    for index, row in enumerate(Row_list):
        newDoc = False
        if index == 0:  # first record
            newDoc = True
        else:  # index > 0; all successive records
            if Row_list[index][docCol_pos] - Row_list[index - 1][docCol_pos] > 0:
                newDoc = True

        if newDoc:
            start_sentence = 1
            end_sentence = Row_list[index][sentenceID_pos]
            inputFilename = Row_list[index][docName_pos]
            inputFilename = IO_csv_util.undressFilenameForCSVHyperlink(inputFilename)
            text = (open(inputFilename, "r", encoding="utf-8", errors='ignore').read())
            sentences = sentence_split_stanza_text(stanzaPipeLine(text))
            number_sentences.append([inputFilename, len(sentences)])

            # check whether the last sentence for the previous doc was less than number of sentences
            if index == 0:  # first record in df
                Row_list_new = process_sentenceID_record(Row_list, Row_list_new, index,
                                                         start_sentence,
                                                         end_sentence,
                                                         header, sentenceID_pos, docCol_pos, docName_pos, frequency_pos,
                                                         save_current=True)
            else:  # index>0 all other records
                # select the number of sentences for the right document
                for i in range(len(number_sentences)):
                    # TODO hyperlinks should be removed in file before passing it to add_missing_IDs
                    if IO_csv_util.undressFilenameForCSVHyperlink(Row_list[index - 1][docName_pos]) == \
                            number_sentences[i][0]:
                        n_sentences = number_sentences[i][1]
                if Row_list[index - 1][sentenceID_pos] < n_sentences:
                    start_sentence = Row_list[index - 1][sentenceID_pos] + 1
                    end_sentence = n_sentences + 1
                    # pass index-1 as argument since we are adding sentence IDs to the previous document
                    Row_list_new = process_sentenceID_record(Row_list, Row_list_new, index - 1,
                                                             start_sentence, end_sentence,
                                                             header, sentenceID_pos, docCol_pos, docName_pos,
                                                             frequency_pos,
                                                             save_current=False)
                    # do NOT save current; already saved when first processing the record
                # now process the current record
                start_sentence = 1
                end_sentence = Row_list[index][sentenceID_pos]
                Row_list_new = process_sentenceID_record(Row_list, Row_list_new, index,
                                                         start_sentence,
                                                         end_sentence,
                                                         header, sentenceID_pos, docCol_pos, docName_pos, frequency_pos,
                                                         save_current=True)
        else:  # same document
            # check that current sentence is not just one sentence greater than previous one
            #   in which case start and end are the same
            if Row_list[index][sentenceID_pos] == Row_list[index - 1][sentenceID_pos] + 1:
                start_sentence = Row_list[index][sentenceID_pos]
                end_sentence = Row_list[index][sentenceID_pos]
            else:
                start_sentence = Row_list[index - 1][sentenceID_pos]
                end_sentence = Row_list[index][sentenceID_pos]
            Row_list_new = process_sentenceID_record(Row_list, Row_list_new, index,
                                                     start_sentence, end_sentence,
                                                     header, sentenceID_pos, docCol_pos, docName_pos, frequency_pos,
                                                     save_current=True)

    df = pd.DataFrame(Row_list_new, columns=header)
    df.sort_values(by=['Document ID', 'Sentence ID'], ascending=True, inplace=True)
    df.to_csv(outputFilename, encoding='utf-8', index=False)
    # TODO temporary to measure process time
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running Excel Add missing IDs at',
                                       True, '', True, startTime, True)
    return outputFilename


# Tony Chen Gu written at April 2022 mortified at May 2022
# edited by Roberto June 2022 for sorting df
# function no longer used since it does not insert sentences in the right document
# use instead add_missing_IDs

def complete_sentence_index(file_path):
    data = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
    if not 'Sentence ID' in data:
        head, tail = os.path.split(file_path)
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Wrong csv file',
                                           'The csv file\n' + tail + '\n does not contain a "Sentence ID" header. A sentence ID value cannot be added.',
                                           True, '', True, '', False)
        return
    if (len(data) == 1):
        return data
    max_sid = max(data["Sentence ID"]) + 1
    sid_list = list(range(1, max_sid))
    df_sid = pd.DataFrame(sid_list, columns=['Sentence ID'])
    # use merge to accelerate the process
    data = data.merge(right=df_sid, how="right", on="Sentence ID")
    data = data.fillna(0)
    # headers=IO_csv_util.get_csvfile_headers_pandas(file_path)
    data.sort_values(by=['Document ID', 'Sentence ID'], ascending=True, inplace=True)
    data.to_csv(file_path, encoding='utf-8', index=False)
    return


# data_to_be_plotted contains the values to be plotted
#   the variable has this format:
#   this includes both headers AND data
#   one series: [[['Name1','Frequency'], ['A', 7]]]
#   two series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]]]
#   three series: [[['Name1','Frequency'], ['A', 7]], [['Name2','Frequency'], ['B', 4]], [['Name3','Frequency'], ['C', 9]]]
#   more series: ..........
# chart_title is the name of the sheet
# num_label number of bars, for instance, that will be displayed in a bar chart
# second_y_var is a boolean that tells the function whether a second y axis is needed
#   because it has a different scale and plotted values would otherwise be "masked"
#   ONLY 2 y-axes in a single chart are allowed by openpyxl
# chart_type_list is in form ['line', 'line','bar']... one for each of n series plotted
# when called from scripts other than Excel_charts, the list can be of length 1 although more series may be plotted
#   in which case values are filled below
# output_file_name MUST be of xlsx type, rather tan csv

# when NO hover-over data are displayed the Excel filename extension MUST be xlsx and NOT xlsm (becauuse no macro VBA is enabled in this case)

# def df_to_list_w_header(df):
#     res = []
#     header = list(df.columns)
#     res.append(header)
#     for index, row in df.iterrows():
#         temp = [row[tag] for tag in header]
#         res.append(temp)
#     return res
#
#
# def df_to_list(df):
#     res = []
#     header = list(df.columns)
#     for index, row in df.iterrows():
#         temp = [row[tag] for tag in header]
#         res.append(temp)
#     return res
#
#
# def list_to_df(tag_list):
#     header = tag_list[0]
#     df = pd.DataFrame(tag_list[1:], columns=header)
#     return df
#
#
# def header_check(inputFile):
#     sentenceID_pos=''
#     docCol_pos=''
#     docName_pos=''
#
#     if isinstance(inputFile, pd.DataFrame):
#         header = list(inputFile.columns)
#     else:
#         header = IO_csv_util.get_csvfile_headers(inputFile)
#     if 'Sentence ID' in header:
#         sentenceID_pos = header.index('Sentence ID')
#     else:
#         pass
#
#     if 'Document ID' in header:
#         docCol_pos = header.index('Document ID')
#     else:
#         pass
#
#     if 'Document' in header:
#         docName_pos = header.index('Document')
#     else:
#         pass
#     return sentenceID_pos, docCol_pos, docName_pos, header
#


# written by Samir Kaddoura, March 2023

# Returns a grid of barcharts for each algorithm.
# Algorithms are horizontally organized based on the order on which they are inputted
# datalist is list of algorithms
# var is variable of choice
# ntopchoices is the n max values
def multiple_barchart(datalist, outputFilename, var, ntopchoices):
    if pd.__version__[0] == '2':
        mb.showwarning(title='Warning',
                       message='The multiple_barchart algorithm is incompatible with a version of pandas higher than 2.0\n\nIn command line, please, pip unistall pandas and pip install pandas==1.5.2 (or even pip install pandas==1.4.4).\n\nMake sure you are in the right NLP environment by typing conda activate NLP')
        return

    tempdatalist = []
    for i in datalist:
        tempdatalist.append(pd.read_csv(i, encoding='utf-8', on_bad_lines='skip'))
    newDatalist = []
    for i in tempdatalist:
        newDatalist.append(
            pd.DataFrame(i[var].value_counts()).reset_index().rename(columns={'index': var, var: 'Frequency'}).head(
                ntopchoices))
    fig = make_subplots(rows=2, cols=int(len(datalist) / 2) + len(datalist) % 2)
    cols = 1
    for i in range(0, len(newDatalist)):
        if i < int(len(datalist) / 2) + len(datalist) % 2:
            fig.add_trace(go.Bar(x=newDatalist[i][var], y=newDatalist[i]['Frequency'], name='Algorithm ' + str(i + 1)),
                          row=1, col=cols)
            cols = cols + 1
    cols = 1
    for i in range(0, len(newDatalist)):
        if i >= int(len(datalist) / 2) + len(datalist) % 2:
            fig.add_trace(go.Bar(x=newDatalist[i][var], y=newDatalist[i]['Frequency'], name='Algorithm ' + str(i + 1)),
                          row=2, col=cols)
            cols = cols + 1
    fig.write_html(outputFilename)
    return outputFilename


# written by Samir Kaddoura, March 2023

# var is the variable of choice to apply the boxplot on
# bycategory is a boolean that chooses whether we want to split it by category along a categorical variable, determined by the following category argument
# points is the choice to represent all points of data, the outliers, or none of them, it should be given through a dropdown menu
# color is another choice of categorical variable to split the data along
def boxplot(data, outputFilename, var, points, bycategory=None, category=None, color=None):
    if points == 'All points':
        points = 'all'
    elif points == 'no points':
        points = False
    elif points == 'outliers only':
        points = 'outliers'
    if color == '':
        color = None

    if type(data) == str:
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')

    if not 'int' in str(type(data[var][0])) and not 'float' in str(type(data[var][0])):
        mb.showwarning(title='Warning',
                       message='The "Boxplots" option requires a numeric field.\n\nPlease, use the dropdown menu to select a numeric csv file field for visualization and try again.')
        return

    if bycategory != 0 and bycategory != None and category != None:
        if not 'str' in str(type(data[category][0])):
            mb.showwarning(title='Warning',
                           message='The "Split data by category" Boxplots option requires a CATEGORICAL "csv file field"".\n\nPlease, use the "csv file field" dropdown menu to select a CATEGORICAL field and try again.')
            return

    if color != None:
        if not 'str' in str(type(data[color][0])):
            mb.showwarning(title='Warning',
                           message='The Boxplots with "Split data by category" and color options requires a secodn CATEGORICAL "csv file field" for the color option".\n\nPlease, use the second "csv file field" dropdown menu to select a CATEGORICAL field and try again.')
            return

    if bycategory == False:
        fig = px.box(data, y=var, points=points)
    else:
        fig = px.box(data, x=category, y=var, points=points, color=color)
    fig.write_html(outputFilename)
    return outputFilename


def histogram(data, outputFilename, var, nbins=0, category=None, color=None, marginal=None):
    if type(data) == str:
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')

    if not 'int' in str(type(data[var].dropna().iloc[0])) and not 'float' in str(type(data[var].dropna().iloc[0])):
        mb.showwarning(title='Warning',
                       message='The "Histogram" option requires a numeric field.\n\nPlease, select a numeric csv file field and try again.')
        return

    kwargs = {'x': var}
    if nbins > 0:
        kwargs['nbins'] = nbins
    if category and category in data.columns:
        kwargs['color'] = category
    if marginal:
        kwargs['marginal'] = marginal

    fig = px.histogram(data, **kwargs)
    fig.update_layout(bargap=0.05)
    fig.write_html(outputFilename)
    return outputFilename


def violin_plot(data, outputFilename, var, points='all', category=None, color=None):
    if points == 'None' or points == '':
        points = False

    if type(data) == str:
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')

    if not 'int' in str(type(data[var].dropna().iloc[0])) and not 'float' in str(type(data[var].dropna().iloc[0])):
        mb.showwarning(title='Warning',
                       message='The "Violin plot" option requires a numeric field.\n\nPlease, select a numeric csv file field and try again.')
        return

    if color == '':
        color = None

    if category and category in data.columns:
        fig = px.violin(data, x=category, y=var, points=points, color=color, box=True)
    else:
        fig = px.violin(data, y=var, points=points, box=True)
    fig.write_html(outputFilename)
    return outputFilename


def correlation_heatmap(inputFilename, outputDir, columns=None):
    """Build an interactive correlation heatmap for numeric columns.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    columns : list or None   Specific columns to include. If None, all numeric columns are used.

    Returns
    -------
    str or ''   Path to output HTML file.
    """
    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return ''

    if columns:
        numeric_df = df[columns].select_dtypes(include='number')
    else:
        numeric_df = df.select_dtypes(include='number')

    if numeric_df.shape[1] < 2:
        mb.showwarning('Warning', 'The correlation heatmap requires at least 2 numeric columns.\n\nPlease, select a csv file with numeric data and try again.')
        return ''

    corr = numeric_df.corr()

    fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r',
                    zmin=-1, zmax=1, aspect='auto',
                    labels=dict(color='Correlation'))
    fig.update_layout(title=f'Correlation heatmap ({numeric_df.shape[1]} variables)',
                      width=max(600, numeric_df.shape[1] * 60 + 200),
                      height=max(500, numeric_df.shape[1] * 50 + 200))

    import re as _re
    base = _re.sub(r'[<>:"/\\|?*]', '_',
                   os.path.splitext(os.path.basename(inputFilename))[0]).replace(' ', '_')
    out_path = os.path.join(outputDir, f'{base}_correlation_heatmap.html')
    fig.write_html(out_path)
    print(f"Data visualization saved as {out_path}")
    return out_path


def heatmap_calendar(inputFilename, outputDir, date_col, value_col=None, date_format='mm-dd-yyyy'):
    """Build a calendar heatmap showing daily values or event counts.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    date_col : str   Column containing dates.
    value_col : str or None   Numeric column for values. If None, counts events per day.
    date_format : str   Date format string (mm-dd-yyyy, dd-mm-yyyy, yyyy-mm-dd, etc.)

    Returns
    -------
    str or ''   Path to output HTML file.
    """
    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return ''

    if date_col not in df.columns:
        mb.showwarning('Warning', f'Column "{date_col}" not found in the csv file.')
        return ''

    fmt_map = {
        'mm-dd-yyyy': '%m-%d-%Y', 'mm/dd/yyyy': '%m/%d/%Y',
        'dd-mm-yyyy': '%d-%m-%Y', 'dd/mm/yyyy': '%d/%m/%Y',
        'yyyy-mm-dd': '%Y-%m-%d', 'yyyy/mm/dd': '%Y/%m/%d',
        'yyyy-dd-mm': '%Y-%d-%m', 'yyyy-mm': '%Y-%m',
    }
    py_fmt = fmt_map.get(date_format, None)

    dates = pd.to_datetime(df[date_col], format=py_fmt, errors='coerce')
    valid_mask = dates.notna()
    if valid_mask.sum() == 0:
        mb.showwarning('Warning', f'No valid dates found in column "{date_col}" with format "{date_format}".\n\nPlease, check the date format and try again.')
        return ''

    df_work = pd.DataFrame({'date': dates[valid_mask]})

    if value_col and value_col in df.columns and value_col != '':
        df_work['value'] = df[value_col][valid_mask].values
        daily = df_work.groupby(df_work['date'].dt.date)['value'].sum().reset_index()
        daily.columns = ['date', 'value']
        color_label = value_col
    else:
        daily = df_work.groupby(df_work['date'].dt.date).size().reset_index()
        daily.columns = ['date', 'value']
        color_label = 'Count'

    daily['date'] = pd.to_datetime(daily['date'])
    daily['weekday'] = daily['date'].dt.weekday
    daily['week'] = daily['date'].dt.isocalendar().week.astype(int)
    daily['year'] = daily['date'].dt.year
    daily['month'] = daily['date'].dt.month
    daily['day_name'] = daily['date'].dt.strftime('%a')
    daily['date_str'] = daily['date'].dt.strftime('%Y-%m-%d')

    years = sorted(daily['year'].unique())

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=len(years), cols=1,
                        subplot_titles=[str(y) for y in years],
                        vertical_spacing=0.08)

    for row_idx, year in enumerate(years, 1):
        yr_data = daily[daily['year'] == year].copy()
        yr_data['week_of_year'] = (yr_data['date'] - pd.Timestamp(f'{year}-01-01')).dt.days // 7

        fig.add_trace(
            go.Heatmap(
                x=yr_data['week_of_year'],
                y=yr_data['weekday'],
                z=yr_data['value'],
                text=yr_data['date_str'],
                hovertemplate='%{text}<br>' + color_label + ': %{z}<extra></extra>',
                colorscale='YlOrRd',
                showscale=(row_idx == 1),
                colorbar=dict(title=color_label) if row_idx == 1 else None,
            ),
            row=row_idx, col=1
        )
        fig.update_yaxes(
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            row=row_idx, col=1
        )
        fig.update_xaxes(
            tickvals=list(range(0, 53, 4)),
            ticktext=[f'W{w}' for w in range(0, 53, 4)],
            row=row_idx, col=1
        )

    fig.update_layout(
        title=f'Calendar heatmap: {color_label} by date',
        height=max(300, 250 * len(years)),
        width=900
    )

    import re as _re
    base = _re.sub(r'[<>:"/\\|?*]', '_',
                   os.path.splitext(os.path.basename(inputFilename))[0]).replace(' ', '_')
    safe_col = _re.sub(r'[<>:"/\\|?*]', '_', date_col).replace(' ', '_')
    out_path = os.path.join(outputDir, f'{base}_calendar_{safe_col}.html')
    fig.write_html(out_path)
    print(f"Data visualization saved as {out_path}")
    return out_path


def waffle_chart(inputFilename, outputDir, category_col, top_n=10, grid_size=10):
    """Build a waffle chart showing proportions of a categorical variable.

    Each square in a 10x10 grid represents 1% of the total.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return ''

    if category_col not in df.columns:
        mb.showwarning('Warning', f'Column "{category_col}" not found in the csv file.')
        return ''

    counts = df[category_col].value_counts().head(top_n)
    total = counts.sum()
    if total == 0:
        return ''

    proportions = (counts / total * grid_size * grid_size).round().astype(int)
    diff = grid_size * grid_size - proportions.sum()
    if diff != 0:
        proportions.iloc[0] += diff

    colors = plt.cm.tab10(np.linspace(0, 1, len(proportions)))
    grid = np.zeros(grid_size * grid_size, dtype=int)
    idx = 0
    for i, count in enumerate(proportions):
        grid[idx:idx + count] = i
        idx += count
    grid = grid.reshape(grid_size, grid_size)

    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(grid_size):
        for j in range(grid_size):
            rect = plt.Rectangle((j, grid_size - 1 - i), 0.9, 0.9,
                                  facecolor=colors[grid[i, j]], edgecolor='white', linewidth=1)
            ax.add_patch(rect)

    ax.set_xlim(-0.1, grid_size)
    ax.set_ylim(-0.1, grid_size)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Waffle chart: {category_col} (top {len(proportions)})', fontsize=14)

    legend_patches = [mpatches.Patch(color=colors[i],
                      label=f'{proportions.index[i]} ({counts.iloc[i]})')
                      for i in range(len(proportions))]
    ax.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1.02, 1),
              fontsize=9, title=category_col, title_fontsize=10)

    import re as _re
    safe = _re.sub(r'[<>:"/\\|?*]', '_', category_col).replace(' ', '_')
    base = _re.sub(r'[<>:"/\\|?*]', '_',
                   os.path.splitext(os.path.basename(inputFilename))[0]).replace(' ', '_')
    out_path = os.path.join(outputDir, f'{base}_waffle_{safe}.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Data visualization saved as {out_path}")
    return out_path


def bubble_chart(inputFilename, outputDir, y_column, X_axis_var='', color_column=''):
    import charts_Plotly_util
    return charts_Plotly_util.bubble_chart(inputFilename, outputDir, y_column, X_axis_var, color_column)


# written by Samir Kaddoura, March 2023

# var1 is the first categorical variable, lengthvar1 is the amount of var 1: should take values of 5 or 10
# var2 is the second categorical variable, lengthvar2 is the amount of var 2: should take values of 5,10 or 20
# var3 is the third categorical variable, lengthvar3 is the amount of var 3: should take values of 5,10, 20 or 30
# All these recommendations are for performance
# three_way_Sankey is a boolean variable that dictates whether the returned Sankey is 2way or 3way. True for 3 variables, false for 2 variables
def Sankey(data, outputFilename, var1, lengthvar1, var2, lengthvar2, three_way_Sankey, var3=None, lengthvar3=None):
    # if pd.__version__[0] == '2':
    #     mb.showwarning(title='Warning',
    #                    message='The Sankey algorithm is incompatible with a version of pandas higher than 2.0\n\nIn command line, please, pip unistall pandas and pip install pandas==1.5.2.\n\nMake sure you are in the right NLP environment by typing conda activate NLP')
    #     return

    if type(data) == str:
        try:
            data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')
        except:
            mb.showwarning(title='Warning',
                           message='The input file ' + data + ' is empty.\n\nNo Sankey flowchart can be produced.\n\nPlease, check your input file and try again.')
            return

    if type(data[var1][0])!=float: # nan values are float, but do not need to be checked here
        if type(data[var1][0]) != str or type(data[var2][0]) != str:
            mb.showwarning("Warning",
                       "All csv file fields should be CATEGORICAL for a Sankey flowchart.\n\nPlease, select categorical field(s) (i.e., fields with string values), rather than continuous numeric field(s), and try again.")

    if three_way_Sankey:
        # 3 variables
        data[var1] = data[var1].str.lower()
        tempframe = pd.DataFrame(data[var1].value_counts().head(lengthvar1)).reset_index()
        try:
            finalframe = data[data[var1].isin(list(set(tempframe['index'])))]
        except:
            if len(finalframe) == 0:
                mb.showwarning(title='Warning',
                               message='The dataframe computed by the Sankey flowchart is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2')
                return
            finalframe = data[data[var1].isin(list(set(tempframe.index)))]
        tempframe2 = pd.DataFrame(finalframe[var2]).value_counts().head(lengthvar2).reset_index()
        tempframe3 = pd.DataFrame(finalframe[var3]).value_counts().head(lengthvar3).reset_index()
        finalframe = finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        finalframe = finalframe[finalframe[var3].isin(list(set(tempframe3[var3])))]
        finalframe = finalframe.reset_index(drop=True)
        sourcelist = list(range(0, len(set(finalframe[var1])) + len(set(finalframe[var2]))))
        source = [item for item in sourcelist for _ in range(len(set(finalframe[var2])) + len(set(finalframe[var3])))]
        target1 = list(range(0, len(set(finalframe[var2])) + len(set(finalframe[var3]))))
        target2 = [x + len(set(finalframe[var1])) for x in target1]
        target = target2 * len(sourcelist)

        labelvector = sorted(set(finalframe[var1])) + sorted(set(finalframe[var2])) + sorted(set(finalframe[var3]))
        valuevector = []

        for i in sorted(list(set(finalframe[var1]))):
            tempvec = []
            tempframe = finalframe[finalframe[var1] == i]
            wantedframe = pd.DataFrame(tempframe[var2].value_counts()).reset_index().rename(
                columns={'index': var2, var2: 'Frequency'})
            for j in sorted(list(set(finalframe[var2]))):
                if j not in list(wantedframe[var2]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var2] == j]['Frequency'])[0])
            tempvec = tempvec + list(np.repeat(0, len(target2) - len(tempvec)))
            valuevector = valuevector + tempvec
        for i in sorted(list(set(finalframe[var2]))):
            tempvec = []
            tempframe = finalframe[finalframe[var2] == i]
            wantedframe = pd.DataFrame(tempframe[var3].value_counts()).reset_index().rename(
                columns={'index': var3, var3: 'Frequency'})
            tempvec = list(np.repeat(0, len(set(finalframe[var2]))))
            for j in sorted(list(set(finalframe[var3]))):
                if j not in list(wantedframe[var3]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var3] == j]['Frequency'])[0])
            valuevector = valuevector + tempvec

    else:
        # 2 variables

        data[var1] = data[var1].str.lower()
        tempframe = data[var1].value_counts().head(lengthvar1).reset_index()
        tempframe.columns = [var1, "Frequency"]
        finalframe = data[data[var1].isin(tempframe[var1])]

        tempframe2 = finalframe[var2].value_counts().head(lengthvar2).reset_index()
        tempframe2.columns = [var2, "Frequency"]
        finalframe = finalframe[finalframe[var2].isin(tempframe2[var2])]
        finalframe.reset_index(drop=True, inplace=True)

        source = []
        target = []
        valuevector = []

        for i, val1 in enumerate(finalframe[var1].unique()):
            for j, val2 in enumerate(finalframe[var2].unique()):
                source.append(i)
                target.append(j + len(finalframe[var1].unique()))
                valuevector.append(
                    len(finalframe[(finalframe[var1] == val1) & (finalframe[var2] == val2)])
                )

        labelvector = list(finalframe[var1].unique()) + list(finalframe[var2].unique())

        # data[var1] = data[var1].str.lower()
        # tempframe = pd.DataFrame(data[var1].value_counts().head(lengthvar1)).reset_index()
        # try:
        #     finalframe = data[data[var1].isin(list(set(tempframe['index'])))]
        # except:
        #     mb.showwarning(title='Warning',
        #                    message='The dataframe computed by the Sankey flowchart is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2')
        #     return
        #     finalframe = tempframe  # data[data[var1].isin(list(set(tempframe['count'])))]
        # tempframe2 = pd.DataFrame(finalframe[var2]).value_counts().head(lengthvar2).reset_index()
        # finalframe = finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        # finalframe = finalframe.reset_index(drop=True)
        # sourcelist = list(range(0, len(set(finalframe[var1]))))
        #
        # source = [item for item in sourcelist for _ in range(len(set(finalframe[var2])))]
        # target1 = list(range(0, len(set(finalframe[var2]))))
        # target2 = [x + len(set(finalframe[var1])) for x in target1]
        # target = target2 * len(set(finalframe[var1]))
        # labelvector = sorted(list(set(finalframe[var1]))) + sorted(list(set(finalframe[var2])))
        # valuevector = []
        #
        # for i in sorted(list(set(finalframe[var1]))):
        #     tempvec = []
        #     tempdata = pd.DataFrame(finalframe[finalframe[var1] == i][var2].value_counts()).reset_index().rename(
        #         columns={'index': var2, var2: 'Frequency'})
        #     # tempvec = tempvec + list(np.repeat(0, len(target2) - len(tempvec)))
        #     # tempvec = list(np.repeat(0, len(set(finalframe[var2]))))
        #     for j in sorted(list(set(tempdata[var2]))):
        #         if j not in list(tempdata[var2]):
        #             # valuevector.append(0)
        #             tempvec.append(0)
        #         else:
        #             # valuevector.append(list(tempdata[tempdata[var2] == j]['Frequency'])[0])
        #             tempvec.append(list(tempdata[tempdata[var2] == j]['Frequency'])[0])
        #     tempvec = tempvec + list(np.repeat(0, len(target2) - len(tempvec)))
        #     valuevector = valuevector + tempvec

    fig = go.Figure(go.Sankey(link=dict(source=source, target=target, value=valuevector),
                              node=dict(label=labelvector, pad=35, thickness=10)))
    fig.write_html(outputFilename)

    return outputFilename


# created by Samir Kaddoura, November 2022

# Function creates a new column that identifies the documents based on a specific interest variable
# two inputs taken: data is the dataset in question, interest is a vector that the user will have to define, as it changes depending on the corpus

def separator(data, interest, algorithm):
    interestvector = []  # empty interest vector
    id_list = []  # empty id list in which we record every entry in the dataset that contains one of the interest inputs

    for i in range(0, len(data)):  # check every entry in dataset
        for j in range(0, len(interest)):  # check every interest vector
            if re.search('.*' + interest[j] + '[^.]', data['Document'][
                i]):  # if the name of the document contains a word of intersest, we append that word to a vector
                interestvector.append(interest[j])
                id_list.append(i)  # append the index of the row that contains the interest value

    # finaldata=data.loc[id_list] #filter dataset by row with interest values
    finaldata = data.loc[id_list, :]  # filter dataset by row with interest values
    finaldata['interest'] = interestvector  # add interest column
    if finaldata.empty:
        mb.showwarning("Warning",
                       "The " + algorithm + " algorithm has produced an empty dataframe.\n\nPlease, make sure that the 'Filename label/part' you have entered are in the document name under the Document field of your input file.\n\nREMEMBER THAT SEARCH WORDS ARE CASE SENSITIVE.\n\nPlease, try again.")
    return finaldata


# written by Samir Kaddoura, March 2023

# Returns sunburst piechart. Input a dataframe provided by the NLP suite as data, interest is a vector including interest separation based on separator (as defined above)
# label is a categorical variable we're interested in
# first_sentences is the n first sentences
# last_sentences is the n last sentences
# half_text is a boolean defining whether to split the text in half or not
# beginning_and_end is a boolean that dictates if its a two-level or three level Sunburst
def Sunburst(data, outputFilename, outputDir, case_sensitive, interest, label, beginning_and_end=False,
             first_sentences=None, last_sentences=None, half_text=None):
    if type(data) == str:
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')
        # @@@ nan values will break the code
        data = data.fillna('Blank/missing value')
    # The presence of a Nan value will classify the object as float
    if type(data[label][0]) != str:
        mb.showwarning("Warning",
                       "The csv file field selected should be categorical.\n\nYou should select a categorical field, rather than a continuous numeric field, and try again.")
        # return
    # the last 3 arguments are optional. If first_sentences is specified and last_sentences is not or vice versa, we return a message stating they must both be specified or absent at the same time
    if (first_sentences == None and last_sentences != None) or (first_sentences != None and last_sentences == None):
        return 'both number of first sentences and number of last sentences have to be specified or absent at the same time'
    else:  # Otherwise, we run the Sunburst

        tempdata = separator(data, interest, "Sunburst")  # Create "interest" variable
        if beginning_and_end == False:
            if half_text == True or (
                    first_sentences == None and last_sentences == None):  # If half text is true or both number of first sentences and last sentences is absent, we split each text in half and attribute a "beginning" half and "end" half

                first_docID = tempdata['Document ID'].iloc[0]
                ogdata = tempdata[tempdata['Document ID'] == first_docID]  # take the first document

                ogdata1 = ogdata[ogdata['Sentence ID'] <= len(ogdata) / 2]  # split the document by first half
                oglist1 = list(np.repeat('Beginning', len(ogdata1)))
                ogdata1['Beginning or End'] = oglist1  # add list "Beginning" the length of the first half

                ogdata2 = ogdata[ogdata['Sentence ID'] > len(ogdata) / 2]  # split the document by first half
                oglist2 = list(np.repeat('End', len(ogdata2)))
                ogdata2['Beginning or End'] = oglist2  # add list "End" the length of the first half

                finaldata = pd.concat([ogdata1, ogdata2])  # merge dataframes
                if not finaldata.empty:
                    for i in range(2, max(data['Document ID']) + 1):  # iterate same process for each document
                        intermediatedata = tempdata[tempdata['Document ID'] == i]

                        intermediatedata1 = intermediatedata[
                            intermediatedata['Sentence ID'] <= len(intermediatedata) / 2]
                        intermediatelist1 = list(np.repeat('Beginning', len(intermediatedata1)))
                        intermediatedata1['Beginning or End'] = intermediatelist1

                        finaldata = pd.concat([finaldata, intermediatedata1])

                        intermediatedata2 = intermediatedata[
                            intermediatedata['Sentence ID'] > len(intermediatedata) / 2]
                        intermediatelist2 = list(np.repeat('End', len(intermediatedata2)))
                        intermediatedata2['Beginning or End'] = intermediatelist2

                        finaldata = pd.concat([finaldata, intermediatedata2])
                    # finaldata not empty
                    # @@@ nan values will break the code
                    finaldata = finaldata.fillna('Blank/missing value')
                    fig = px.sunburst(finaldata, path=['interest', 'Beginning or End', label])  # return Sunburst
                else:
                    if finaldata.empty:
                        mb.showwarning("Warning",
                                       "The Sunburst algorithm has produced an empty dataframe.\n\nPlease, make sure that the 'Filename label/part' you have entered are in the document name under the Document field of your input file.\n\nREMEMBER THAT SEARCH WORDS ARE CASE SENSITIVE.\n\nPlease, try again.")
                # return Plotly.offline.plot(fig)

            else:
                tempdata1 = tempdata[
                    tempdata['Sentence ID'] <= first_sentences]  # all observations with the first n sentences

                list1 = list(np.repeat('Beginning', len(tempdata1)))  # List repeating 'Beginning'

                for i in range(1, max(data['Document ID']) + 1):
                    intermediatedata1 = tempdata[tempdata['Document ID'] == i]
                    intermediatedata2 = intermediatedata1[
                        intermediatedata1['Sentence ID'] > (len(intermediatedata1) - last_sentences)]
                    tempdata1 = pd.concat([tempdata1, intermediatedata2]).reset_index().drop(
                        columns={'index'})  # all observations with last n sentences
                    if len(tempdata1) == 0:
                        mb.showwarning(title='Warning',
                                       message='The dataframe computed by theSunburst chart algorithm is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2')
                        return

                list2 = list(np.repeat('End', len(tempdata1) - len(list1)))  # List repeating 'End'
                finallist = list1 + list2  # Create a vector defining if the sentence is at the beginning or the end
                finaldata = tempdata1
                finaldata['Beginning or End'] = finallist

                fig = px.sunburst(finaldata, path=['interest', 'Beginning or End', label])  # create sunburst chart
        else:
            # @@@ nan values will break the code
            tempdata = tempdata.fillna('Blank/missing value')
            fig = px.sunburst(tempdata, path=['interest', label])
            finaldata = tempdata
        if finaldata.empty:
            outputFilename = None
        else:
            fig.write_html(outputFilename)

        return outputFilename


# written by Samir Kaddoura, March 2023

# This function takes the data, an interest vector defined the same way as in the Sunburst function,
#   a variable of choice (should be categorical) var,
#   a boolean variable to dictate if the user wants to observe an additional variable with "extra_dimension_average",
#   the numerical variable of choice average_variable

# The graph shows the frequencies of each group by default depending on the interest vector and the initial variable of choice. If specified, it shows the average of average_variable per group
def Treemap(data, outputFilename, interest, csv_file_field, extra_dimension_average, average_variable=None):
    if type(data) == str:  # convert data to dataframe
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')
    # The presence of a Nan value will classify the object as float
    if type(data[csv_file_field][0]) != str:
        mb.showwarning("Warning",
                       "The csv file field selected should be categorical.\n\nYou should select a categorical field, rather than a continuous numeric field, and try again.")
        # return
    if extra_dimension_average and type(data[average_variable][0]) != np.float64:
        mb.showwarning("Warning",
                       "The csv file field selected should be numeric.\n\nYou should select a numeric field, rather than an alphabetic field, and try again.")
        return
    data = separator(data, interest, "Treemap")  # use separator function to create interest vector
    if data.empty:
        outputFilename = None
    else:
        if extra_dimension_average == False:  # return regular 2 variable graph if false
            fig = px.treemap(data, path=[px.Constant('Total Frequency'), 'interest', csv_file_field])
        else:  # return graph with extra variable if true
            fig = px.treemap(data, path=[px.Constant('Total Frequency'), 'interest', csv_file_field],
                             color=average_variable, color_continuous_scale='RdBu')
        fig.write_html(outputFilename)
    return outputFilename


# written by Samir Kaddoura, March 2023

# choose a data set, a variable to show the evolution through time, outputFilename to save output, monthly and yearly are boolean variables
# If both are passed as false, return daily graph
# if monthly or yearly is passed as true, return monthly or yearly graph respectively
# Both cannot be simultaneously true

# import pandas as pd
# import re
# import numpy as np
# import Plotly.express as px

def TimeMapper(data, outputFilename, var, date_format_var, cumulative, monthly=None, yearly=None, date_col=None):
    headers = IO_csv_util.get_csvfile_headers(data)
    if date_col and date_col in headers:
        date_field = date_col
    elif 'Date' in headers:
        date_field = 'Date'
    elif 'Document' in headers:
        date_field = 'Document'
    else:
        mb.showwarning(title="Warning",
                       message="The time mapper algorithm requires a csv input file with a date column.\n\nYou can select the date column using the 'csv file field for dynamic graph' dropdown, or the csv file must have a 'Date' or 'Document' column.\n\nPlease, try again.")
        return
    if type(data) == str:
        data = pd.read_csv(data, encoding='utf-8', on_bad_lines='skip')
    date = []
    year = []
    month = []
    day = []

    if date_format_var == 'yyyy':  # creates year variable based on yyyy format
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', data[date_field][i])[0])
            data['year'] = year
    elif date_format_var == 'mm-yyyy':  # creates year and month variable in yyyy-mm format
        for i in range(0, len(data[date_field])):
            date.append(re.search('\d.*\d', data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + '-' + date[i][0:2])
        data['year'] = year
        data['month'] = month
    elif date_format_var == 'yyyy-mm':  # creates year and month variable in yyyy-mm format
        for i in range(0, len(data[date_field])):
            date.append(re.search('\d.*\d', data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + '-' + date[i][-2:])
        data['year'] = year
        data['month'] = month
    elif date_format_var == 'dd-mm-yyyy':  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search('\d.*\d', data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + '-' + date[i][3:5])
        for i in range(0, len(data[date_field])):
            day.append(month[i] + '-' + date[i][0:2])
        data['day'] = day
        data['year'] = year
        data['month'] = month
    elif date_format_var == 'mm-dd-yyyy':  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            try:
                date.append(re.search('\d.*\d', data[date_field][i])[0])
            except:
                continue
        for i in range(0, len(data[date_field])):
            try:
                year.append(re.search('\d{4}', date[i])[0])
            except:
                continue
        for i in range(0, len(data[date_field])):
            try:
                month.append(year[i] + '-' + date[i][0:2])
            except:
                continue
        for i in range(0, len(data[date_field])):
            try:
                day.append(month[i] + '-' + date[i][3:5])
            except:
                continue
        data['year'] = year
        data['month'] = month
        data['day'] = day
    elif date_format_var == 'yyyy-mm-dd':  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search('\d.*\d', data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + '-' + date[i][5:7])
        data['year'] = year
        data['month'] = month
        data['day'] = date
    elif date_format_var == 'yyyy-dd-mm':  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search('\d.*\d', data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search('\d{4}', date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + '-' + date[i][-2:])
        for i in range(0, len(data[date_field])):
            day.append(month[i] + '-' + date[i][5:7])
        data['year'] = year
        data['month'] = month
        data['day'] = day

    # Compute a fixed Y-axis category order from the full dataset so that
    # bar positions stay stable as the animation slider moves.
    _total_freq = data[var].value_counts()
    _fixed_categories = _total_freq.sort_values(ascending=True).index.tolist()

    def _build_finalframe(data, var, time_col, cumulative):
        """Build the animation dataframe for a given time granularity."""
        data = data.sort_values(time_col)
        finalframe = pd.DataFrame()
        for period in sorted(set(data[time_col])):
            if cumulative:
                subset = data[data[time_col] <= period]
            else:
                subset = data[data[time_col] == period]
            tester = pd.DataFrame(
                subset[var].value_counts()
            ).reset_index().rename(columns={'index': var, var: 'Frequency'})
            # Ensure all categories are present in every frame
            for j in set(data[var]):
                if j not in set(tester[var]):
                    temp = pd.DataFrame(
                        [[j, 0]], columns=[var, 'Frequency'])
                    tester = pd.concat([tester, temp])
            tester = tester.sort_values(var).reset_index(drop=True)
            tester['date'] = period
            finalframe = pd.concat([finalframe, tester])
        return finalframe

    def _make_fig(finalframe, var, fixed_cats):
        """Create the animated bar chart with a locked Y-axis."""
        max_freq = finalframe['Frequency'].max() if len(finalframe) > 0 else 1
        fig = px.bar(finalframe, y=var, x='Frequency',
                     animation_frame='date', orientation='h',
                     range_x=[0, max_freq])
        fig.update_yaxes(categoryorder='array', categoryarray=fixed_cats)
        return fig

    # Plot corresponding graph depending on the options
    if cumulative == False:
        if monthly == True and yearly == True:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"
        elif monthly == True:
            finalframe = _build_finalframe(data, var, 'month', False)
            fig = _make_fig(finalframe, var, _fixed_categories)
        elif yearly == True:
            finalframe = _build_finalframe(data, var, 'year', False)
            fig = _make_fig(finalframe, var, _fixed_categories)
        else:
            finalframe = _build_finalframe(data, var, 'day', False)
            fig = _make_fig(finalframe, var, _fixed_categories)
    else:
        if monthly == True and yearly == True:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"
        elif yearly == True:
            finalframe = _build_finalframe(data, var, 'year', True)
            fig = _make_fig(finalframe, var, _fixed_categories)
        elif monthly == True:
            finalframe = _build_finalframe(data, var, 'month', True)
            fig = _make_fig(finalframe, var, _fixed_categories)
        else:
            finalframe = _build_finalframe(data, var, 'day', True)
            fig = _make_fig(finalframe, var, _fixed_categories)
    fig = fig.update_geos(projection_type="equirectangular", visible=True, resolution=110)
    fig.write_html(outputFilename)

    return outputFilename


# written by Simon Bian
# September 2023

def process_and_aggregate_data(data, **kwargs):
    conditions = kwargs.get('where_column', {})  # WHERE conditions
    agg_column = kwargs.get('groupby_column')  # GROUP BY column
    select_columns = kwargs.get('select_column', [])  # SELECT columns
    for col, value in conditions.items():
        if isinstance(value, (list, tuple)):
            data = data[data[col].isin(value)]
        else:
            data = data[data[col] == value]

    if not select_columns:
        select_columns = [col for col in data.columns if col != agg_column]
        # If agg_column is not specified, we cannot proceed with grouping; handle this case as needed
    if not agg_column:
        raise ValueError("The 'groupby_column' parameter is required for aggregation.")
        print("Due to exception in missing groupby_column parameter required for aggregation, the function is aborted")
        return

    # Group by the specified column along with select_columns and calculate the count
    agg_data = data.groupby([agg_column, select_columns]).size().reset_index(name='Count')
    # Pivot the table. If select_columns is empty, this will consider all other columns.
    pivot_data = agg_data.pivot_table(index=select_columns, columns=agg_column, values='Count', fill_value=0)
    return pivot_data


def transform_data(pivot_data, transformation='min-max'):
    if transformation == 'min-max':
        min_val = pivot_data.min().min()
        max_val = pivot_data.max().max()
        return (pivot_data - min_val) / (max_val - min_val)
    elif transformation == 'square-root':
        return np.sqrt(pivot_data)
    elif transformation == 'log':
        return np.log1p(pivot_data)
    elif transformation == 'z-score':
        means = pivot_data.mean()
        stds = pivot_data.std()
        # Skip columns with std very close to zero
        z_scores = pivot_data.subtract(means, axis='columns').divide(stds.where(stds > 1e-5, 1), axis='columns')
        # Replace inf and -inf values with NaN for safety
        z_scores.replace([np.inf, -np.inf], np.nan, inplace=True)
        return z_scores
    else:
        return pivot_data  # return original data if no recognized transformation is given


def visualize_colormap_data(data, top_n=60, figsize=(15, 10), y_label='Lemma', x_label='Document', normalize='log',
                   color='YlOrBr', outputname='output_figure'):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    numeric_data = data.select_dtypes(include=[np.number])
    sorted_columns = numeric_data.columns.sort_values()
    sorted_pivot_data = numeric_data[sorted_columns][::-1]
    sorted_rows = numeric_data.sum(axis=1).sort_values(ascending=False).index
    sorted_pivot_data = sorted_pivot_data.loc[sorted_rows]
    transposed_data = sorted_pivot_data.head(top_n)
    # print("doing calculations...complete!")
    plt.figure(figsize=figsize)
    try:
        sns.heatmap(transposed_data, annot=False, fmt='.2f', cmap=color, cbar_kws={'label': normalize})
    except:
        print("There appears to be ann error with cmap; we revert to default ")
        sns.heatmap(transposed_data, annot=False, fmt='.2f', cmap='YlOrBr', cbar_kws={'label': normalize})
    ax = plt.gca()
    ax.set_yticks(np.arange(len(transposed_data.index)))
    ax.set_yticklabels(transposed_data.index)
    ax.set_xticks(np.arange(len(transposed_data.columns)))
    ax.set_xticklabels(transposed_data.columns, rotation=90)
    ax.set_ylabel(y_label)
    x_label = x_label.replace('Real_','')
    ax.set_xlabel(x_label)
    ax.set_title('Colormap/heatmap of ' + y_label + ' Frequency by ' + x_label + ' Values (' + normalize + ' Scale)')
    plt.savefig(outputname + '.png')
    print(f"Data visualization saved as {outputname}.png.")
    # plt.show() // we don't need to show it because we have that other option


def visualize_stacked_bar(crosstab_data, top_n=20, figsize=(12, 6),
                          x_label='Category', y_label='Count',
                          title='Stacked bar chart', outputname='output_stacked_bar',
                          grouped=False):
    """Horizontal stacked or grouped bar chart from a crosstab DataFrame.

    Parameters
    ----------
    crosstab_data : pd.DataFrame
        Rows = group labels, columns = segment labels, values = counts.
    top_n : int
        Show only the top N groups by total count.
    x_label, y_label, title : str
    outputname : str
        Output path without extension (.png appended automatically).
    grouped : bool
        If True, draw side-by-side (grouped) bars instead of stacked.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    totals = crosstab_data.sum(axis=1).sort_values(ascending=False)
    plot_data = crosstab_data.loc[totals.head(top_n).index]

    fig_w = max(figsize[0], len(plot_data) * 0.6 + 4)
    fig_h = max(figsize[1], len(plot_data) * 0.3 + 2)
    ax = plot_data.plot.barh(stacked=not grouped, figsize=(fig_w, fig_h), width=0.8)
    ax.set_xlabel(y_label)
    ax.set_ylabel(x_label)
    ax.set_title(title)
    ax.legend(title=crosstab_data.columns.name or '',
              bbox_to_anchor=(1.02, 1), loc='upper left',
              fontsize=7, title_fontsize=8)
    plt.tight_layout()
    fig_obj = ax.get_figure()
    fig_obj.savefig(outputname + '.png', dpi=150, bbox_inches='tight')
    plt.close(fig_obj)
    print(f"Data visualization saved as {outputname}.png.")


def extract_file_name(link_string):
    import re
    match = re.search(r'\/([^\/]+)\.txt', link_string)
    return match.group(1) if match else link_string


def renamedf(df):
    raw_names = [extract_file_name(col) for col in df.columns]
    sorted_names = sorted(raw_names)
    df.columns = sorted_names


# csv_file_categorical_field_list is a double list with each list containing the combination csv field & search values
#   for example, [[Document | Mao, Deng, Xi][NER | PERSON][WORD|'']
# params is a single lst with the max number of rows and RGB color, e.g., [20, 255 166 0]

def read_filename_color(inputFilename):
    try:
        # print("Thank you. Data reading success.\n")
        dataFrame = pd.read_csv(inputFilename)
        # Displaying some basic statistics
        # print(f"Number of Columns: {dataFrame.shape[1]}")
        # print(f"Number of Rows: {dataFrame.shape[0]}\n")

        # print(f"Column names: {dataFrame.columns.tolist()}\n")

        # Display the datatypes
        # print("Data types for each column:")
        # print(dataFrame.dtypes, "\n")

        # Checking for missing values
        missing_values = dataFrame.isnull().sum()
        if missing_values.any():
            print("Number of missing values for each column:")
            print(missing_values[missing_values > 0], "\n")
        else:
            print("There are no missing values in the dataset.\n")
        return dataFrame
        # Display summary statistics for numeric columns
    # choice = input("Would you like summary statistics for numeric columns? (y/n): ").strip().lower()
    # if choice == 'y':
    #     print("\nSummary Statistics:")
    #     print(dataFrame.describe())

    # Display top 5 rows
    # choice = input("\nWould you like to see the first 5 rows of the data? (y/n): ").strip().lower()
    # if choice == 'y':
    #     print(dataFrame.head())

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


def get_transformation_choice(choice=5):
    transformations = {
        1: 'min-max',
        2: 'square-root',
        3: 'log',
        4: 'z-score',
        5: None
    }
    return transformations.get(choice, None)


def further_group(df, major_parm, small_prm):
    ## majro_parm = str, small_prm = list of string to be regexed against a
    ## as we need to check suffix of string for GROUP BY
    col = df[major_parm].value_counts().index.tolist()
    mps_suffix = {}
    for i in col:
        for j in small_prm:
            if re.search('.*' + str(j) + '.*', str(i)):
                mps_suffix[str(i)] = str(j)
    df['Real_' + major_parm] = df[major_parm].map(mps_suffix)


def sql_commands(s, dataFrame):
    '''
    In sql, we all know the famous quote, SELECT * FROM any_sort_of_datatable WHERE * GROUP BY *
    This command is in effect doing that.
    The  WHERE command, in which you know at which point ROWS you'd like to filter fow
    The  GROUP BY command, in which COLUMN's FIELDS you know you would like to aggregate the RESULT upon
    The SELECT command, in which you know which COLUMNS you'd like to present to the viewers
    The return is, in essence, a pythonic database searching command that achieves this effect
    '''
    WHERE_s = s[1:-1]
    GROUPBY_s = s[0][0].split('|')
    GROUPBY = GROUPBY_s[0]
    add = GROUPBY_s[1]
    if add:
        all_values = add.split(', ')
        further_group(dataFrame, GROUPBY, all_values)
        print("The function detected string values in input, and they were mapped accordingly")
        GROUPBY = 'Real_' + GROUPBY
    SELECT = s[-1][0].split('|')
    if SELECT[1]!='':
        mb.showwarning(title='Search values ignored',
                       message='The search values\n   ' + str(SELECT[1]) + '\nentered for the last selected csv file field ' + str(SELECT[0]) + ' will be ignored.\n\nThe field values for a last selected field of a colormap should be left blank.')
    SELECT = SELECT[0]
    WHERE = {}
    if WHERE_s:
        for condition in WHERE_s:
            cmd = condition[0].split('|')
            mtc = cmd[1].split(', ')
            WHERE[cmd[0]] = mtc
    return WHERE, GROUPBY, SELECT


def special_sql_commands(s, dataFrame):
    '''
    THIS IS FOR sunburst / treemaps only
    For the first parameter, it should be fixed to be partial match or none
    For all other parameters, it should be fixed to fixed match or none
    Example:
        Given: NY_1_piggy, NY_2_bank, NY_3_piggy, NY_2_bank
        Entering piggy would yield partial match: NY_1_piggy, NY_3_piggy aggregates
        .............. would yield fixed match: None. Only if entering NY_1_piggy would yield crrect
    Example2:
        In NER, entering O would yield partial match: PERSON, ORGANIZATION, IDEOLOGY, O....
        Entering O would yield fixed match: O only.
    '''
    WHERE_s = s[1:]
    GROUPBY_s = s[0][0].split('|')
    GROUPBY = GROUPBY_s[0]
    add = GROUPBY_s[1]
    if add:
        all_values = add.split(', ')
        further_group(dataFrame, GROUPBY, all_values)
        print("The function detected string values in input, and they were mapped accordingly")
        GROUPBY = 'Real_' + GROUPBY
    WHERE = {}
    if WHERE_s:
        for condition in WHERE_s:
            cmd = condition[0].split('|')
            mtc = cmd[1].split(', ')
            WHERE[cmd[0]] = mtc
    return WHERE, GROUPBY


import numpy as np
from matplotlib.colors import LinearSegmentedColormap


def interpolate_colors(color1, color2, num_colors):
    color1, color2 = [x / 255. for x in color1], [x / 255. for x in color2]
    return [np.array(color1) * (1 - ratio) + np.array(color2) * ratio for ratio in np.linspace(0, 1, num_colors)]


def cmaps(start_color, end_color):
    colors = interpolate_colors(start_color, end_color, 256)
    cmap_custom = LinearSegmentedColormap.from_list("custom", colors, N=256)
    try:
        return cmap_custom
    except:
        return 'YlOrBr'


def colormap(inputFilename, outputDir, csv_file_categorical_field_list, params):
    filesToOpen = []
    dataFrame = read_filename_color(inputFilename)

    WHERE, GROUPBY, SELECT = sql_commands(csv_file_categorical_field_list, dataFrame)
    # step1 is a dataframe
    step1 = process_and_aggregate_data(dataFrame, where_column=WHERE, groupby_column=GROUPBY, select_column=SELECT)
    if step1.empty:
        mb.showwarning(title='No search values found',
                       message='No combination of csv file fields and search values were found in your input file.\n\n' + str(csv_file_categorical_field_list) + '\n\nPlease, make sure to check whether\n   1. you have not entered the same field twice;\n   2. you are using a case sensitive search option.\n\nPlease, click on the Reset button and start again.')
        return
    colormap_dataframe_csv_filename =outputDir + os.sep + "colormap_dataframe.csv"
    filesToOpen.append(colormap_dataframe_csv_filename)
    # add headers to dataframe
    if GROUPBY == 'Document':
        if len(WHERE)==0:
            for i in range(len(list(step1.columns.values))):
                header = list(step1.columns.values)[i]
                head, tail = os.path.split(header)
                step1 = step1.rename(columns={header: 'Frequency in: ' + tail})
    step1.to_csv(colormap_dataframe_csv_filename, index=True)

    # val = 1 #get_transformation_choice(), but we will connect it....
    step2 = transform_data(step1)  # There needs to be a GUI to allow transformation, but...
    # We proceed with default instead perhaps...
    if GROUPBY == 'Document':
        # if len(WHERE)==0:
            # when a specific document part (e.g., Book1 for Harry Potter) is not entered by the user
            #   the document will contain the entire path along with an hypewrlink and this may be very cumbersome to display in the X axis
            #   must remove hyperlink and display document tail only
            # print('Must REMOVE hyperlink and display document tail only, not path')
            # for i in range(len(list(step2.columns.values))):
            #     header=list(step2.columns.values)[i]
            #     head, tail = os.path.split(header)
            #     step2 = step2.rename(columns = {header:tail})
        renamedf(step2)  # We rename to file relative location, not absolute location
    try:
        cmap = cmaps(eval(params[1]), eval(params[2]))
    except:
        cmap = cmaps((135, 207, 236), (0, 0, 255))
    import IO_files_util
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.html', 'colormap')

    visualize_colormap_data(step2, top_n=params[0], y_label = SELECT, x_label = GROUPBY,
                   normalize=params[-1], color=cmap, outputname=outputFilename)  # There is no GUI yet...
    filesToOpen.append(outputFilename)
    return filesToOpen


def select_and_counting(df, select_and_count):
    grouped = df.groupby(select_and_count).size()
    counts_df = grouped.reset_index(name='values')
    new_df = pd.merge(df, counts_df, on=select_and_count, how='left')
    return new_df
    # This one tells us for each word, how many times it appear
    # THIS IS FOR SUNBURST ? TREE MAP


def where_data(data, **kwargs):
    conditions = kwargs.get('where_column', {})  # WHERE conditions
    for col, values in conditions.items():
        if values == '' or values == ['']:
            continue
        if isinstance(values, (list, tuple)):
            data = data[data[col].isin(values)]
    # THIS FUNCTION IS DOING: SELECT FROM DATA WHERE cond_1, cond_2, ... con_n for ** kwargs
    return data


def fixed_transform_helper(df, prt, nms):
    nms = int(nms)
    top_X_items = list(df[prt].value_counts()[0:nms].keys())
    df = df[df[prt].isin(top_X_items)]
    return df


def fixed_transform(df, fixed_value):
    for col in df.columns:
        if col != 'counts':
            df = fixed_transform_helper(df, col, fixed_value)
    return df


def rate_prop_helper(df, prt, nms):
    nms = int(nms)
    top_X_items = list(df[prt].value_counts()[0:nms].keys())
    df = df[df[prt].isin(top_X_items)]
    return df


def rate_prop(df, rt, base):
    for col in df.columns:
        if col != 'counts':
            df = rate_prop_helper(df, col, base)
            base = base * rt
    return df


# Option 1: Fixed Parameter Filtering 50-100 (default 50)
# Option 2: Rate-Propagating Parameter Filtering: 2 values Rate filtering 3 value Base filtering value def = 40
# Option 3: No filter at all


# THIS IS AN ABBREVIATED VERSION FOR The sunburst / treemap
# suntree = 1 for sunburst 0 for treemap
# returns two files: a csv fle of intermediate results and an html file for the Sunburst_Treemap chart
def Sunburst_Treemap(inputFilename, outputFilename, outputDir, csv_file_categorical_field_list, suntree,
                     fixed_param_var, rate_param_var, base_param_var, filter_options_var, case_sensitive=False):
    filesToOpen = []

    print(fixed_param_var, rate_param_var, base_param_var, filter_options_var, case_sensitive)
    # print("======")
    data = pd.read_csv(inputFilename)

    if not case_sensitive:
        data = data.astype(str).apply(lambda s: s.str.lower())

    WHERE, GROUPBY = special_sql_commands(csv_file_categorical_field_list, data)
    if not case_sensitive:
        for key, query in WHERE.items():
            WHERE[key] = [q.lower() for q in query]
    data = where_data(data, where_column=WHERE)
    select_and_count = [GROUPBY]
    select_and_count.extend(list(WHERE.keys()))
    df = select_and_counting(data, select_and_count)
    df_grouped = df.groupby(select_and_count).size().reset_index(name='counts')
    intermediate_csv_filename =outputDir + os.sep + "sunburst_treemap_intermediate.csv"
    filesToOpen.append(intermediate_csv_filename)
    df_grouped.to_csv(intermediate_csv_filename, index=False)
    # df_grouped.head(5)
    if filter_options_var == 'Fixed parameter':
        df_grouped = fixed_transform(df_grouped, int(fixed_param_var))
        print("Fixed parameter applied")
    if filter_options_var == 'Propagating parameter':
        df_grouped = rate_prop(df_grouped, int(rate_param_var), int(base_param_var))
        print("Propagating parameter applied")
    print('df_grouped:',df_grouped)
    if df_grouped.empty:
        mb.showwarning(title='No search values found',
                       message='No combination of csv file fields and search values were found in your input file.\n\nPlease, make sure to check whether you are using a case sensitive search option.')
        return
    if suntree == 0 or suntree == 3: # treemap
        fig = px.treemap(df_grouped, path=select_and_count, values='counts')
        if outputFilename == '':
            import IO_files_util
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'treemap')
        fig.write_html(outputFilename)
        filesToOpen.append(outputFilename)
        outputFilename = ''
    if suntree==1 or suntree == 3: # sunburst
        fig = px.sunburst(df_grouped, path=select_and_count, values='counts')  # Ensure the hierarchy levels are correct
        if outputFilename == '':
            import IO_files_util
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                 '.html', 'sunburst')
        fig.write_html(outputFilename)
        filesToOpen.append(outputFilename)
    return filesToOpen


# ═══════════════════════════════════════════════════════════════════════
# Standalone visualization functions
# Extracted from auto_chart_cross_complex for use in data_visualization GUIs
# ═══════════════════════════════════════════════════════════════════════

def network_graph_visjs(inputFilename, outputDir, col1, col2, col3,
                        date_col=None, top_n_per_role=15):
    """Build an interactive vis.js network graph from three relational CSV columns.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    col1, col2, col3 : str   Column names for node1, edge, node2 (e.g. S, V, O).
    date_col : str or None   Optional date column for time-slider animation.
    top_n_per_role : int     Max values per role column to keep the graph readable.

    Returns
    -------
    list of str   Paths to output files (HTML + optional .gexf).
    """
    import json as _json
    import math as _math

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return []

    svo_cols = [col1, col2, col3]
    for c in svo_cols:
        if c not in df.columns:
            print(f"  WARNING: Column '{c}' not found in {inputFilename}")
            return []

    _has_dates = date_col and date_col in df.columns
    _net_cols = list(svo_cols)
    if _has_dates:
        _net_cols.append(date_col)

    net_df = df[_net_cols].dropna(subset=svo_cols, how='all').copy()
    for sc in svo_cols:
        net_df[sc] = net_df[sc].fillna('').astype(str)
    if net_df.empty:
        return []

    palette = {'S': '#E04040', 'V': '#4060E0', 'O': '#30A030'}
    role_keys = ['S', 'V', 'O']
    role_labels = [col1, col2, col3]
    role_of = {}
    top_per_role = {}
    for idx_r, sc in enumerate(svo_cols):
        rk = role_keys[idx_r]
        top_vals = net_df[sc].value_counts().head(top_n_per_role).index.tolist()
        top_per_role[sc] = set(top_vals)
        for v in top_vals:
            if v and v not in role_of:
                role_of[v] = rk

    mask = net_df.apply(
        lambda row: all(row[c] in top_per_role[c] or row[c] == ''
                        for c in svo_cols), axis=1)
    net_df = net_df[mask]
    if net_df.empty:
        return []

    edges = {}
    edge_dates = {}
    edge_labels = {}
    for _, row in net_df.iterrows():
        vals = [row[c] for c in svo_cols if row[c]]
        row_date = None
        if _has_dates and pd.notna(row.get(date_col)):
            row_date = pd.to_datetime(row[date_col], errors='coerce')
            if pd.isna(row_date):
                row_date = None
        for i in range(len(vals) - 1):
            key = (vals[i], vals[i + 1])
            edges[key] = edges.get(key, 0) + 1
            if row_date is not None:
                edge_dates.setdefault(key, []).append(row_date)
        if len(vals) >= 3:
            verb = row[svo_cols[1]]
            if verb:
                edge_labels.setdefault((vals[0], vals[-1]), set()).add(verb)
                for i in range(len(vals) - 1):
                    edge_labels.setdefault((vals[i], vals[i + 1]), set()).add(verb)

    triplet_counts = {}
    for _, row in net_df.iterrows():
        vals = tuple(row[c] for c in svo_cols)
        if any(v == '' for v in vals):
            continue
        triplet_counts[vals] = triplet_counts.get(vals, 0) + 1

    node_triplets = {}
    for triplet, cnt in triplet_counts.items():
        for val in triplet:
            node_triplets.setdefault(val, []).append(list(triplet) + [cnt])

    all_nodes = set()
    for (s, t) in edges:
        all_nodes.add(s)
        all_nodes.add(t)

    node_freq = {}
    for sc in svo_cols:
        for val, cnt in net_df[sc].value_counts().items():
            if val:
                node_freq[val] = node_freq.get(val, 0) + cnt

    if not all_nodes:
        return []

    print(f"  Network graph: {len(all_nodes)} nodes, {len(edges)} edges, {len(triplet_counts)} unique triplets")

    freq_vals = [node_freq.get(n, 1) for n in all_nodes]
    max_freq = max(freq_vals)
    min_freq = min(freq_vals)
    SIZE_MIN, SIZE_MAX = 8, 45

    def _node_size(freq):
        if max_freq == min_freq:
            return (SIZE_MIN + SIZE_MAX) / 2
        log_ratio = _math.log(1 + freq - min_freq) / _math.log(1 + max_freq - min_freq)
        return SIZE_MIN + log_ratio * (SIZE_MAX - SIZE_MIN)

    node_id_map = {n: i for i, n in enumerate(sorted(all_nodes))}
    vis_nodes = []
    for n, nid in node_id_map.items():
        rk = role_of.get(n, role_keys[-1])
        freq = node_freq.get(n, 1)
        sz = round(_node_size(freq), 1)
        fsz = max(10, min(22, int(10 + (sz - SIZE_MIN) / (SIZE_MAX - SIZE_MIN) * 12)))
        vis_nodes.append({
            'id': nid, 'label': n,
            'color': palette.get(rk, '#888'),
            'font': {'size': fsz},
            'shape': 'dot', 'size': sz,
            'title': '{} (freq: {})'.format(n, freq),
            'role': rk})

    all_verbs = sorted(set(v for labels in edge_labels.values() for v in labels))
    edge_color_palette = [
        '#E04040', '#4060E0', '#30A030', '#E0A020', '#9040C0',
        '#20B0B0', '#E06090', '#808000', '#FF6020', '#6080FF',
        '#A05030', '#00A060', '#C04080', '#5090A0', '#D0D030',
        '#8060C0', '#40C080', '#E08040', '#6060A0', '#B04040']
    verb_color_map = {}
    for i, v in enumerate(all_verbs):
        verb_color_map[v] = edge_color_palette[i % len(edge_color_palette)]

    vis_edges = []
    for (s, t), w in edges.items():
        labels_for_edge = edge_labels.get((s, t), set())
        if len(labels_for_edge) == 1:
            ec = verb_color_map[next(iter(labels_for_edge))]
        else:
            ec = '#aaaaaa'
        label_str = ', '.join(sorted(labels_for_edge)) if labels_for_edge else ''
        title_parts = ['{} → {}'.format(s, t)]
        if label_str:
            title_parts.append('via: {}'.format(label_str))
        title_parts.append('count: {}'.format(w))
        e_entry = {
            'from': node_id_map[s], 'to': node_id_map[t],
            'value': w,
            'title': ' | '.join(title_parts),
            'label': label_str if len(labels_for_edge) == 1 else '',
            'color': {'color': ec, 'highlight': '#333333'},
            'edgeVerb': label_str}
        if _has_dates and (s, t) in edge_dates:
            e_entry['dates'] = sorted(set(
                d.strftime('%Y-%m-%d') for d in edge_dates[(s, t)]))
        vis_edges.append(e_entry)

    _all_dates_set = set()
    if _has_dates:
        for dlist in edge_dates.values():
            for d in dlist:
                _all_dates_set.add(d.strftime('%Y-%m-%d'))
        node_dates = {}
        for (s, t), dlist in edge_dates.items():
            for d in dlist:
                ds = d.strftime('%Y-%m-%d')
                node_dates.setdefault(node_id_map[s], set()).add(ds)
                node_dates.setdefault(node_id_map[t], set()).add(ds)
        for vn in vis_nodes:
            nid = vn['id']
            if nid in node_dates:
                vn['dates'] = sorted(node_dates[nid])
    _all_dates_sorted = sorted(_all_dates_set) if _all_dates_set else []

    js_node_triplets = {}
    for label, trips in node_triplets.items():
        nid = node_id_map.get(label)
        if nid is not None:
            trips_sorted = sorted(trips, key=lambda x: -x[-1])[:30]
            js_node_triplets[nid] = trips_sorted

    _role_initials = {'S': 'S', 'V': 'V', 'O': 'O'}
    _svo_label = 'Network'
    _role_arrow_label = ' → '.join(role_labels)
    _role_arrow_short = ' → '.join(role_keys)

    _role_css = {}
    for idx_r, rl in enumerate(role_labels):
        _role_css[rl] = role_keys[idx_r].lower()

    _th = []
    for _i, _rc in enumerate(role_labels):
        if _i > 0:
            _th.append('<th></th>')
        _th.append('<th>{}</th>'.format(_rc))
    _th.append('<th>Count</th>')
    _table_header_html = ''.join(_th)

    _td = []
    for _i, _rc in enumerate(role_labels):
        _css = _role_css.get(_rc, '')
        if _i > 0:
            _td.append("'<td>&rarr;</td>'")
        _td.append("'<td class=\"{}\">' + t[{}] + '</td>'".format(_css, _i))
    _td.append("'<td>' + t[{}] + '</td>'".format(len(svo_cols)))
    _table_row_js = ' + '.join(_td)

    _info_click = ' &rarr; '.join(role_keys)
    _no_triplets = ' → '.join(role_keys)

    legend_parts = []
    for rk, rl in zip(role_keys, role_labels):
        legend_parts.append(
            '<span class="leg" style="background:{}"></span>{}'.format(palette[rk], rl))
    if all_verbs:
        legend_parts.append('&nbsp;&nbsp;|&nbsp;&nbsp;<b>Edges:</b>')
        for v in all_verbs[:12]:
            legend_parts.append(
                '<span class="leg-e" style="background:{}"></span>{}'.format(verb_color_map[v], v))
        if len(all_verbs) > 12:
            legend_parts.append('… +{} more'.format(len(all_verbs) - 12))
    legend_html = '  '.join(legend_parts)

    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{svo_label} Network</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; margin: 0; }}
  #network {{ width: 100%; height: {network_height}; border: 1px solid #ccc; }}
  #title {{ text-align: center; padding: 8px; font-size: 16px; font-weight: bold; }}
  #legend {{ text-align: center; padding: 4px; font-size: 13px; }}
  .leg {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%;
          vertical-align: middle; margin: 0 3px 0 12px; }}
  .leg-e {{ display: inline-block; width: 20px; height: 4px;
            vertical-align: middle; margin: 0 3px 0 10px; border-radius: 2px; }}
  #time-slider-container {{ display: {slider_display}; padding: 6px 20px;
           background: #f8f8f8; border-top: 1px solid #ddd; text-align: center; }}
  #time-slider-container label {{ font-size: 13px; margin-right: 8px; }}
  #time-slider {{ width: 60%; vertical-align: middle; }}
  #time-label {{ font-weight: bold; font-size: 13px; margin-left: 8px; min-width: 100px;
                 display: inline-block; }}
  #time-slider-container button {{ margin-left: 12px; font-size: 12px; padding: 2px 10px;
                                    cursor: pointer; }}
  #info {{ padding: 8px 16px; font-size: 13px; color: #333;
           max-height: 18vh; overflow-y: auto; border-top: 1px solid #ccc; }}
  #info table {{ border-collapse: collapse; margin: 4px auto; }}
  #info th, #info td {{ padding: 2px 10px; text-align: left; }}
  #info th {{ border-bottom: 1px solid #999; }}
  .s {{ color: #E04040; font-weight: bold; }}
  .v {{ color: #4060E0; font-weight: bold; }}
  .o {{ color: #30A030; font-weight: bold; }}
</style>
</head><body>
<div id="title">{svo_label} (top {top_n} per role) &mdash; click a node to see full {role_arrow_label} chains</div>
<div id="legend">{legend_html} &nbsp;&nbsp;&nbsp; <span style="font-size:12px;color:#666">&#9679; Node size = frequency</span></div>
<div id="time-slider-container">
  <label>Timeline:</label>
  <input type="range" id="time-slider" min="0" max="0" value="0" step="1">
  <span id="time-label">All dates</span>
  <button id="time-play">&#9654; Play</button>
  <button id="time-reset">Show All</button>
</div>
<div id="network"></div>
<div id="info">Click a node to see its {role_arrow_short} relationships.</div>
<script>
var allDates = {all_dates_json};
var nodes = new vis.DataSet({nodes_json});
var edges = new vis.DataSet({edges_json});
var nodeTriplets = {triplets_json};
var container = document.getElementById('network');
var gdata = {{ nodes: nodes, edges: edges }};
var options = {{
  physics: {{ solver: 'forceAtlas2Based',
              forceAtlas2Based: {{ gravitationalConstant: -60, springLength: 150,
                                  springConstant: 0.04, damping: 0.5 }},
              stabilization: {{ iterations: 200 }} }},
  interaction: {{ hover: true, tooltipDelay: 100 }},
  nodes: {{ scaling: {{ min: 8, max: 45 }} }},
  edges: {{ arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
            smooth: {{ type: 'continuous' }}, scaling: {{ min: 1, max: 6 }},
            font: {{ size: 10, color: '#555', strokeWidth: 2, strokeColor: '#fff', align: 'top' }} }}
}};
var network = new vis.Network(container, gdata, options);
var origNodeProps = {{}};
nodes.forEach(function(n) {{
  origNodeProps[n.id] = {{ size: n.size, fontSize: n.font ? n.font.size : 14 }};
}});
var origEdgeColors = {{}};
edges.forEach(function(e) {{
  origEdgeColors[e.id] = e.color && e.color.color ? e.color.color : '#aaaaaa';
}});
function resetAll() {{
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                    font: {{ size: orig.fontSize, color: '#333' }} }});
  }});
  edges.forEach(function(e) {{
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
  }});
}}
var slider = document.getElementById('time-slider');
var timeLabel = document.getElementById('time-label');
var playBtn = document.getElementById('time-play');
var resetBtn = document.getElementById('time-reset');
var playInterval = null;
if (allDates.length > 0) {{
  slider.max = allDates.length;
  slider.value = 0;
  slider.addEventListener('input', function() {{ applyTimeFilter(parseInt(this.value)); }});
  resetBtn.addEventListener('click', function() {{ slider.value = 0; applyTimeFilter(0); stopPlay(); }});
  playBtn.addEventListener('click', function() {{
    if (playInterval) {{ stopPlay(); return; }}
    if (parseInt(slider.value) >= allDates.length) slider.value = 0;
    playInterval = setInterval(function() {{
      var v = parseInt(slider.value) + 1;
      if (v > allDates.length) {{ stopPlay(); return; }}
      slider.value = v;
      applyTimeFilter(v);
    }}, 800);
    playBtn.textContent = '\\u275A\\u275A Pause';
  }});
}}
function stopPlay() {{
  if (playInterval) {{ clearInterval(playInterval); playInterval = null; }}
  playBtn.textContent = '\\u25B6 Play';
}}
function applyTimeFilter(idx) {{
  if (idx === 0 || allDates.length === 0) {{
    timeLabel.textContent = 'All dates';
    resetAll();
    return;
  }}
  var cutoff = allDates[idx - 1];
  timeLabel.textContent = cutoff;
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    var dates = n.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    if (visible) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: orig.fontSize, color: '#333' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.05, size: Math.max(4, orig.size * 0.3),
                      font: {{ size: 6, color: '#ddd' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var dates = e.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (visible) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eee', opacity: 0.03 }} }});
    }}
  }});
}}
var labelToId = {{}};
nodes.forEach(function(n) {{ labelToId[n.label] = n.id; }});
network.on("click", function(params) {{
  var infoDiv = document.getElementById('info');
  if (params.nodes.length === 0) {{
    resetAll();
    infoDiv.innerHTML = 'Click a node to see its {info_click_msg} relationships.';
    return;
  }}
  var clickedId = params.nodes[0];
  var clickedNode = nodes.get(clickedId);
  var trips = nodeTriplets[clickedId] || [];
  var involvedIds = new Set();
  involvedIds.add(clickedId);
  trips.forEach(function(t) {{
    for (var i = 0; i < t.length - 1; i++) {{
      var nid = labelToId[t[i]];
      if (nid !== undefined) involvedIds.add(nid);
    }}
  }});
  var involvedEdgeIds = new Set();
  edges.forEach(function(e) {{
    if (involvedIds.has(e.from) && involvedIds.has(e.to)) {{
      involvedEdgeIds.add(e.id);
    }}
  }});
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    if (involvedIds.has(n.id)) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: Math.max(orig.fontSize, 14), color: '#000' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.10, size: Math.max(6, orig.size * 0.5),
                      font: {{ size: 8, color: '#ccc' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (involvedEdgeIds.has(e.id)) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eee', opacity: 0.08 }} }});
    }}
  }});
  if (trips.length === 0) {{
    infoDiv.innerHTML = '<b>' + clickedNode.label + '</b>: no full {no_triplets_msg} tuples.';
    return;
  }}
  var html = '<b>' + clickedNode.label + '</b> &mdash; '
           + trips.length + ' tuple(s):<br>'
           + '<table><tr>{table_header_html}</tr>';
  trips.forEach(function(t) {{
    html += '<tr>' + {table_row_js} + '</tr>';
  }});
  html += '</table>';
  infoDiv.innerHTML = html;
}});
</script>
</body></html>"""

    html = html.format(
        svo_label=_svo_label,
        role_arrow_label=_role_arrow_label,
        role_arrow_short=_role_arrow_short,
        info_click_msg=_info_click,
        no_triplets_msg=_no_triplets,
        table_header_html=_table_header_html,
        table_row_js=_table_row_js,
        top_n=top_n_per_role,
        legend_html=legend_html,
        nodes_json=_json.dumps(vis_nodes),
        edges_json=_json.dumps(vis_edges),
        triplets_json=_json.dumps(js_node_triplets),
        all_dates_json=_json.dumps(_all_dates_sorted),
        network_height='70vh' if _all_dates_sorted else '75vh',
        slider_display='block' if _all_dates_sorted else 'none')

    import re as _re
    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    base = _safe_fn(os.path.splitext(os.path.basename(inputFilename))[0])
    output_files = []
    network_file = os.path.join(outputDir, '{}_network.html'.format(base))
    with open(network_file, 'w', encoding='utf-8') as fh:
        fh.write(html)
    output_files.append(network_file)
    print(f"  Network saved: {network_file}")

    # Gephi .gexf export
    try:
        import Gephi_util as _gephi

        rgb_map = {'S': (224, 64, 64), 'V': (64, 96, 224), 'O': (48, 160, 48)}
        _gexf_dynamic = _has_dates and len(edge_dates) > 0
        _gexf_mode = "dynamic" if _gexf_dynamic else "static"
        _gexf_tf = "date" if _gexf_dynamic else ""

        gexf = _gephi.Gexf("NLP Suite", "Network")
        graph = gexf.addGraph("directed", _gexf_mode, "Network", timeformat=_gexf_tf)
        role_attr_id = graph.addNodeAttribute("Role", role_keys[-1], "string", "static")

        _node_spells = {}
        if _gexf_dynamic:
            for (s, t), dlist in edge_dates.items():
                for d in dlist:
                    ds = d.strftime('%Y-%m-%d')
                    _node_spells.setdefault(s, []).append({"start": ds, "end": ds})
                    _node_spells.setdefault(t, []).append({"start": ds, "end": ds})

        for n, nid in node_id_map.items():
            rk = role_of.get(n, role_keys[-1])
            freq = node_freq.get(n, 1)
            r, g_c, b = rgb_map.get(rk, (128, 128, 128))
            spells = _node_spells.get(n, []) if _gexf_dynamic else []
            node = graph.addNode(str(nid), n,
                                 r=str(r), g=str(g_c), b=str(b),
                                 size=str(max(10, freq)), spells=spells)
            node.addAttribute(role_attr_id, rk)

        for eidx, ((s, t), w) in enumerate(edges.items()):
            espells = []
            if _gexf_dynamic and (s, t) in edge_dates:
                for d in edge_dates[(s, t)]:
                    ds = d.strftime('%Y-%m-%d')
                    espells.append({"start": ds, "end": ds})
            graph.addEdge(str(eidx), str(node_id_map[s]), str(node_id_map[t]),
                          weight=str(w), label='{} → {}'.format(s, t), spells=espells)

        gexf_file = os.path.join(outputDir, '{}_network.gexf'.format(base))
        with open(gexf_file, 'wb') as gf:
            gexf.write(gf, print_stat=False)
        output_files.append(gexf_file)
        print(f"  Gephi .gexf saved: {gexf_file}")
    except ImportError:
        pass
    except Exception as ge:
        print(f"  WARNING: Gephi .gexf export: {ge}")

    return output_files


def hierarchical_tree(inputFilename, outputDir, parent_col, child_col,
                      label_col=None, info_col=None, color_col=None):
    """Build an interactive D3.js hierarchical tree from parent-child CSV columns.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    parent_col : str      Column with parent node names.
    child_col : str       Column with child node names.
    label_col : str       Optional column for display labels (defaults to child_col).
    info_col : str        Optional column for tooltip/detail text (e.g., dates, attributes).
    color_col : str       Optional column for node color grouping.

    Returns
    -------
    list of str   Paths to output files (HTML).
    """
    import json as _json
    import re as _re

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(inputFilename, encoding='ISO-8859-1', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return []

    if parent_col not in df.columns or child_col not in df.columns:
        print(f"  WARNING: Required columns '{parent_col}' and/or '{child_col}' not found.")
        return []

    df = df[[c for c in [parent_col, child_col, label_col, info_col, color_col] if c and c in df.columns]].dropna(subset=[child_col])
    df[parent_col] = df[parent_col].fillna('').astype(str).str.strip()
    df[child_col] = df[child_col].astype(str).str.strip()

    children_of = {}
    node_info = {}
    node_label = {}
    node_group = {}
    all_children = set()

    for _, row in df.iterrows():
        parent = row[parent_col]
        child = row[child_col]
        if not child or parent == child:
            continue
        children_of.setdefault(parent, []).append(child)
        all_children.add(child)
        if label_col and label_col in df.columns and pd.notna(row.get(label_col)):
            node_label[child] = str(row[label_col])
        if info_col and info_col in df.columns and pd.notna(row.get(info_col)):
            node_info[child] = str(row[info_col])
        if color_col and color_col in df.columns and pd.notna(row.get(color_col)):
            node_group[child] = str(row[color_col])

    all_parents = set(children_of.keys()) - {''}
    roots = (all_parents - all_children) | ({''} if '' in children_of else set())
    if not roots:
        roots = all_parents - all_children
    if not roots:
        roots = {next(iter(children_of))} if children_of else set()

    group_palette = [
        '#5B8C6E', '#8B6B4E', '#4A7B9D', '#C17C4E', '#7B6B8D',
        '#5A9E8F', '#B85C5C', '#6E8B3D', '#9B7DB8', '#CC9E4F']
    all_groups = sorted(set(node_group.values()))
    group_color = {g: group_palette[i % len(group_palette)] for i, g in enumerate(all_groups)}

    def build_tree(node_name, _visited=None):
        if _visited is None:
            _visited = set()
        if node_name in _visited:
            return None
        _visited.add(node_name)
        label = node_label.get(node_name, node_name)
        info = node_info.get(node_name, '')
        grp = node_group.get(node_name, '')
        color = group_color.get(grp, '#5B8C6E')
        initials = ''.join(w[0].upper() for w in label.split() if w)[:2]
        result = {
            'name': label, 'initials': initials,
            'info': info, 'group': grp, 'color': color}
        kids = children_of.get(node_name, [])
        if kids:
            child_nodes = [build_tree(c, _visited.copy()) for c in kids]
            result['children'] = [c for c in child_nodes if c is not None]
        return result

    if len(roots) == 1:
        root_name = next(iter(roots))
        if root_name == '':
            direct_children = children_of.get('', [])
            if len(direct_children) == 1:
                tree_data = build_tree(direct_children[0])
            else:
                tree_data = {'name': 'Root', 'initials': 'R', 'info': '', 'group': '', 'color': '#888',
                             'children': [build_tree(c) for c in direct_children]}
        else:
            tree_data = build_tree(root_name)
    else:
        tree_data = {'name': 'Root', 'initials': 'R', 'info': '', 'group': '', 'color': '#888',
                     'children': [build_tree(r) for r in sorted(roots) if r]}

    legend_html = ''
    if all_groups:
        parts = []
        for g in all_groups:
            parts.append('<span class="leg" style="background:{}"></span>{}'.format(group_color[g], g))
        legend_html = '  '.join(parts)

    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f0eb; }}
  #title {{ text-align: center; padding: 16px; font-size: 20px; font-weight: bold; color: #333; }}
  #legend {{ text-align: center; padding: 4px 16px 12px; font-size: 13px; }}
  .leg {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%;
          vertical-align: middle; margin: 0 3px 0 12px; }}
  #hint {{ text-align: center; padding: 0 16px 8px; font-size: 12px; color: #999; }}
  #tree-container {{ width: 100%; overflow: auto; padding: 20px; text-align: center; }}
  #tree-container svg {{ display: inline-block; }}
  svg {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  .link {{ fill: none; stroke: #c5b9a8; stroke-width: 1.5px; }}
  .node-circle {{ cursor: pointer; stroke: #fff; stroke-width: 2px; }}
  .node-circle-collapsed {{ stroke: #333; stroke-width: 2.5px; stroke-dasharray: 3,2; }}
  .node-label {{ font-size: 12px; fill: #333; font-weight: 500; }}
  .node-initials {{ font-size: 11px; fill: #fff; font-weight: bold; text-anchor: middle;
                     dominant-baseline: central; pointer-events: none; }}
  .tooltip {{ position: absolute; background: #fff; border: 1px solid #ccc; border-radius: 6px;
              padding: 8px 12px; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
              pointer-events: none; max-width: 280px; }}
  .badge {{ font-size: 10px; fill: #fff; font-weight: bold; text-anchor: middle;
            dominant-baseline: central; pointer-events: none; }}
</style>
</head><body>
<div id="title">{title}</div>
<div id="legend">{legend_html}</div>
<div id="hint">Click to expand/collapse complex children &bull; Double-click to show/hide simplex fields</div>
<div id="tree-container"></div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
var treeData = {tree_json};
var margin = {{ top: 30, right: 40, bottom: 30, left: 40 }};
var nodeRadius = 22;
var levelHeight = 120;
var nodeSpacing = 60;

// Separate simplex children from complex children in the data
function separateSimplexes(node) {{
  if (!node.children) return;
  node._simplexes = [];
  var complexKids = [];
  node.children.forEach(function(c) {{
    if (c.group === 'Simplex') {{
      node._simplexes.push(c);
    }} else {{
      complexKids.push(c);
      separateSimplexes(c);
    }}
  }});
  node.children = complexKids.length > 0 ? complexKids : null;
}}
separateSimplexes(treeData);

var svg = d3.select('#tree-container').append('svg');
var gRoot = svg.append('g');

var tooltip = d3.select('body').append('div').attr('class', 'tooltip')
    .style('display', 'none');

// Build hierarchy from complex-only tree
var root = d3.hierarchy(treeData, function(d) {{ return d.children; }});

// Collapse below depth 2
root.each(function(d) {{
  if (d.depth >= 3 && d.children) {{
    d._collapsed = d.children;
    d.children = null;
  }}
}});

var i = 0;
var duration = 400;

// Track which nodes have simplex panel open
var simplexVisible = {{}};

function update(source) {{
  var treemap = d3.tree().nodeSize([nodeSpacing, levelHeight]);
  treemap(root);

  var nodes = root.descendants();
  var links = root.links();

  var minX = d3.min(nodes, function(d) {{ return d.x; }});
  var maxX = d3.max(nodes, function(d) {{ return d.x; }});
  var maxY = d3.max(nodes, function(d) {{ return d.y; }});
  var treeWidth = (maxX - minX) + margin.left + margin.right + nodeSpacing;
  var treeHeight = maxY + margin.top + margin.bottom + 120;

  svg.attr('width', Math.max(treeWidth, 600))
     .attr('height', Math.max(treeHeight, 300));

  var offsetX = -minX + margin.left + nodeSpacing / 2;
  gRoot.attr('transform', 'translate(' + offsetX + ',' + margin.top + ')');

  // Clear and redraw
  gRoot.selectAll('path.link').remove();
  gRoot.selectAll('g.node').remove();
  gRoot.selectAll('g.simplex-panel').remove();

  // Links
  gRoot.selectAll('path.link')
      .data(links)
      .enter().append('path')
      .attr('class', 'link')
      .attr('d', function(d) {{
        return 'M' + d.source.x + ',' + d.source.y
             + ' C' + d.source.x + ',' + (d.source.y + d.target.y) / 2
             + ' ' + d.target.x + ',' + (d.source.y + d.target.y) / 2
             + ' ' + d.target.x + ',' + d.target.y;
      }});

  // Nodes
  var node = gRoot.selectAll('g.node')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .attr('transform', function(d) {{ return 'translate(' + d.x + ',' + d.y + ')'; }});

  node.append('circle')
      .attr('r', nodeRadius)
      .attr('fill', function(d) {{ return d.data.color || '#5B8C6E'; }})
      .attr('class', function(d) {{
        return 'node-circle' + (d._collapsed ? ' node-circle-collapsed' : '');
      }})
      .on('click', function(event, d) {{
        event.stopPropagation();
        if (d._collapsed) {{
          d.children = d._collapsed;
          d._collapsed = null;
        }} else if (d.children) {{
          d._collapsed = d.children;
          d.children = null;
        }}
        update(d);
      }})
      .on('dblclick', function(event, d) {{
        event.stopPropagation();
        event.preventDefault();
        var sxList = d.data._simplexes;
        if (!sxList || sxList.length === 0) return;
        var key = d.data.name;
        simplexVisible[key] = !simplexVisible[key];
        update(d);
      }})
      .on('mouseover', function(event, d) {{
        var html = '<b>' + d.data.name + '</b>';
        var nSx = d.data._simplexes ? d.data._simplexes.length : 0;
        var nCx = 0;
        if (d._collapsed) nCx = d._collapsed.length;
        else if (d.children) nCx = d.children.length;
        if (nCx > 0) html += '<br>' + nCx + ' complex children';
        if (d._collapsed) html += ' (click to expand)';
        if (nSx > 0) html += '<br>' + nSx + ' simplex fields (double-click to show)';
        tooltip.html(html).style('display', 'block')
               .style('left', (event.pageX + 12) + 'px')
               .style('top', (event.pageY - 20) + 'px');
      }})
      .on('mouseout', function() {{ tooltip.style('display', 'none'); }});

  node.append('text')
      .attr('class', 'node-initials')
      .text(function(d) {{ return d.data.initials; }});

  // Badge for collapsed complex children
  node.each(function(d) {{
    if (d._collapsed) {{
      var g = d3.select(this);
      g.append('circle')
        .attr('class', 'badge-bg')
        .attr('cx', nodeRadius - 4).attr('cy', -nodeRadius + 4)
        .attr('r', 9).attr('fill', '#c0392b');
      g.append('text')
        .attr('class', 'badge')
        .attr('x', nodeRadius - 4).attr('y', -nodeRadius + 4)
        .text(d._collapsed.length);
    }}
  }});

  // Badge for simplex count (blue, bottom-right)
  node.each(function(d) {{
    var nSx = d.data._simplexes ? d.data._simplexes.length : 0;
    if (nSx > 0) {{
      var g = d3.select(this);
      g.append('circle')
        .attr('class', 'badge-bg')
        .attr('cx', nodeRadius - 4).attr('cy', nodeRadius - 4)
        .attr('r', 9).attr('fill', '#2980b9');
      g.append('text')
        .attr('class', 'badge')
        .attr('x', nodeRadius - 4).attr('y', nodeRadius - 4)
        .text(nSx);
    }}
  }});

  // Labels (complex only)
  node.append('text')
      .attr('class', 'node-label')
      .attr('y', nodeRadius + 16).attr('text-anchor', 'middle')
      .text(function(d) {{ return d.data.name; }});

  // Simplex panels for nodes that have been double-clicked
  nodes.forEach(function(d) {{
    var sxList = d.data._simplexes;
    if (!sxList || sxList.length === 0) return;
    if (!simplexVisible[d.data.name]) return;

    var panel = gRoot.append('g')
        .attr('class', 'simplex-panel')
        .attr('transform', 'translate(' + (d.x + nodeRadius + 30) + ',' + (d.y - 10) + ')');

    var lineH = 18;
    var padX = 10, padY = 6;
    var maxW = 0;
    sxList.forEach(function(s) {{ maxW = Math.max(maxW, s.name.length * 7); }});
    var boxW = maxW + padX * 2 + 10;
    var boxH = sxList.length * lineH + padY * 2;

    panel.append('rect')
      .attr('x', 0).attr('y', 0)
      .attr('width', boxW).attr('height', boxH)
      .attr('rx', 6).attr('ry', 6)
      .attr('fill', '#fff').attr('stroke', '#c5b9a8').attr('stroke-width', 1);

    panel.append('line')
      .attr('x1', -30).attr('y1', 10)
      .attr('x2', 0).attr('y2', 10)
      .attr('stroke', '#c5b9a8').attr('stroke-width', 1);

    sxList.forEach(function(s, idx) {{
      panel.append('circle')
        .attr('cx', padX + 6).attr('cy', padY + idx * lineH + lineH / 2)
        .attr('r', 5).attr('fill', s.color || '#8B6B4E');
      panel.append('text')
        .attr('x', padX + 16).attr('y', padY + idx * lineH + lineH / 2 + 4)
        .attr('font-size', '11px').attr('fill', '#555')
        .text(s.name);
    }});
  }});
}}

root.each(function(d) {{ d.id = ++i; }});
update(root);
</script>
</body></html>"""

    title = os.path.splitext(os.path.basename(inputFilename))[0].replace('_', ' ')

    html = html.format(
        title=title,
        legend_html=legend_html,
        tree_json=_json.dumps(tree_data))

    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    base = _safe_fn(os.path.splitext(os.path.basename(inputFilename))[0])
    output_file = os.path.join(outputDir, '{}_tree.html'.format(base))
    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f"  Hierarchical tree saved: {output_file}")
    return [output_file]


def animated_migration_map(inputFilename, outputDir, entity_col, location_col,
                           date_col=None, sequence_col=None, lat_col=None, lon_col=None,
                           doc_col=None):
    """Build an animated Leaflet migration map with timeline slider.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    entity_col : str      Column with entity/person names.
    location_col : str    Column with location names.
    date_col : str        Optional column with dates (used for ordering and labels).
    sequence_col : str    Optional column with numeric ordering (e.g., chapter, sentence index).
                          If neither date_col nor sequence_col, row order is used.
    lat_col, lon_col : str  Optional pre-geocoded coordinate columns.
    doc_col : str         Optional column with document names (adds a document filter dropdown).

    Returns
    -------
    list of str   Paths to output files (HTML).
    """
    import json as _json
    import re as _re

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(inputFilename, encoding='ISO-8859-1', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return []

    for c in [entity_col, location_col]:
        if c not in df.columns:
            print(f"  WARNING: Column '{c}' not found in CSV.")
            return []

    has_coords = lat_col and lon_col and lat_col in df.columns and lon_col in df.columns

    if not doc_col and 'Document' in df.columns:
        doc_col = 'Document'
    has_doc = doc_col and doc_col in df.columns

    keep_cols = [entity_col, location_col]
    if date_col and date_col in df.columns:
        keep_cols.append(date_col)
    if sequence_col and sequence_col in df.columns:
        keep_cols.append(sequence_col)
    if has_coords:
        keep_cols.extend([lat_col, lon_col])
    if has_doc:
        keep_cols.append(doc_col)
    df = df[keep_cols].dropna(subset=[entity_col, location_col]).copy()
    df[entity_col] = df[entity_col].astype(str).str.strip()
    df[location_col] = df[location_col].astype(str).str.strip()

    if sequence_col and sequence_col in df.columns:
        df = df.sort_values(sequence_col)
        df['_order_label'] = df[sequence_col].astype(str)
    elif date_col and date_col in df.columns:
        df['_parsed_date'] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.sort_values('_parsed_date')
        df['_order_label'] = df[date_col].astype(str)
    else:
        df['_order_label'] = [str(i) for i in range(len(df))]

    if not has_coords:
        try:
            from geopy.geocoders import Nominatim
            import time as _time
        except ImportError:
            print("  WARNING: geopy not available for geocoding. Provide lat/lon columns or install geopy.")
            return []

        geocoder = Nominatim(user_agent="NLP_Suite_migration_map", timeout=10)
        unique_locs = df[location_col].unique()
        loc_coords = {}
        print(f"  Geocoding {len(unique_locs)} unique locations...")
        for loc in unique_locs:
            if not loc:
                continue
            try:
                result = geocoder.geocode(loc)
                if result:
                    loc_coords[loc] = (result.latitude, result.longitude)
                else:
                    print(f"    Could not geocode: {loc}")
            except Exception as ge:
                print(f"    Geocoding error for '{loc}': {ge}")
            _time.sleep(1.1)

        df['_lat'] = df[location_col].map(lambda x: loc_coords.get(x, (None, None))[0])
        df['_lon'] = df[location_col].map(lambda x: loc_coords.get(x, (None, None))[1])
    else:
        df['_lat'] = pd.to_numeric(df[lat_col], errors='coerce')
        df['_lon'] = pd.to_numeric(df[lon_col], errors='coerce')

    df = df.dropna(subset=['_lat', '_lon'])
    if df.empty:
        print("  WARNING: No geocoded locations found.")
        return []

    entity_palette = [
        '#2E8B57', '#8B4513', '#4682B4', '#CD853F', '#6A5ACD',
        '#20B2AA', '#DC143C', '#6B8E23', '#9370DB', '#DAA520']
    all_entities = sorted(df[entity_col].unique())
    entity_color = {e: entity_palette[i % len(entity_palette)] for i, e in enumerate(all_entities)}

    all_docs = sorted(df[doc_col].astype(str).unique()) if has_doc else []

    migration_data = {}
    for entity in all_entities:
        edf = df[df[entity_col] == entity]
        stops = []
        for _, row in edf.iterrows():
            stop = {
                'location': row[location_col],
                'lat': round(float(row['_lat']), 6),
                'lon': round(float(row['_lon']), 6),
                'label': row['_order_label']
            }
            if has_doc:
                stop['doc'] = str(row[doc_col])
            stops.append(stop)
        seen = set()
        unique_stops = []
        for s in stops:
            key = (s['location'], s['label'])
            if key not in seen:
                seen.add(key)
                unique_stops.append(s)
        migration_data[entity] = {
            'color': entity_color[entity],
            'stops': unique_stops
        }

    all_labels = []
    for entity in all_entities:
        for s in migration_data[entity]['stops']:
            if s['label'] not in all_labels:
                all_labels.append(s['label'])

    all_lats = df['_lat'].tolist()
    all_lons = df['_lon'].tolist()
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)

    legend_parts = []
    for e in all_entities:
        legend_parts.append(
            '<span class="leg-dot" style="background:{}"></span>{}'.format(entity_color[e], e))
    legend_html = '  '.join(legend_parts)

    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Migration Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
  #title {{ text-align: center; padding: 10px; font-size: 18px; font-weight: bold; color: #333; }}
  #legend {{ text-align: center; padding: 4px 16px 8px; font-size: 13px; }}
  .leg-dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%;
              vertical-align: middle; margin: 0 3px 0 10px; }}
  #map {{ width: 100%; height: 65vh; }}
  #controls {{ display: flex; align-items: center; justify-content: center;
               padding: 10px 20px; background: #f8f8f8; border-top: 1px solid #ddd; gap: 12px; }}
  #controls button {{ font-size: 16px; padding: 4px 14px; cursor: pointer; border: 1px solid #ccc;
                       border-radius: 4px; background: #fff; }}
  #controls button:hover {{ background: #e8e8e8; }}
  .speed-btn {{ font-size: 13px !important; padding: 2px 8px !important; }}
  .speed-btn.active {{ background: #4682B4 !important; color: #fff; border-color: #4682B4 !important; }}
  #slider {{ flex: 1; max-width: 60%; }}
  #time-display {{ font-weight: bold; font-size: 15px; min-width: 100px; text-align: center; }}
  #doc-filter {{ padding: 4px 8px; font-size: 13px; border: 1px solid #ccc; border-radius: 4px;
                 max-width: 250px; }}
  #filter-bar {{ text-align: center; padding: 4px 16px; font-size: 13px; background: #f0f0f0;
                  border-bottom: 1px solid #ddd; }}
  #info {{ padding: 8px 16px; font-size: 13px; color: #555; text-align: center; }}
</style>
</head><body>
<div id="title">{title}</div>
<div id="legend">{legend_html}</div>
{doc_filter_html}
<div id="map"></div>
<div id="controls">
  <button id="play-btn">&#9654;</button>
  <button class="speed-btn active" data-speed="1">1x</button>
  <button class="speed-btn" data-speed="2">2x</button>
  <button class="speed-btn" data-speed="4">4x</button>
  <input type="range" id="slider" min="0" max="{max_step}" value="0" step="1">
  <span id="time-display">{first_label}</span>
</div>
<div id="info">Click play or drag the slider to animate migration paths.</div>
<script>
var migrationData = {migration_json};
var allLabels = {labels_json};
var entityNames = {entities_json};
var allDocs = {docs_json};
var hasDocFilter = allDocs.length > 0;

function getFilteredData() {{
  if (!hasDocFilter) return {{ data: migrationData, labels: allLabels, entities: entityNames }};
  var sel = document.getElementById('doc-filter');
  var docVal = sel ? sel.value : '';
  if (!docVal) return {{ data: migrationData, labels: allLabels, entities: entityNames }};
  var filtered = {{}};
  var filteredEntities = [];
  var filteredLabels = [];
  entityNames.forEach(function(name) {{
    var stops = migrationData[name].stops.filter(function(s) {{ return s.doc === docVal; }});
    if (stops.length > 0) {{
      filtered[name] = {{ color: migrationData[name].color, stops: stops }};
      filteredEntities.push(name);
      stops.forEach(function(s) {{
        if (filteredLabels.indexOf(s.label) === -1) filteredLabels.push(s.label);
      }});
    }}
  }});
  return {{ data: filtered, labels: filteredLabels, entities: filteredEntities }};
}}

var map = L.map('map').setView([{center_lat}, {center_lon}], 7);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}@2x.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  maxZoom: 18
}}).addTo(map);

var entityLayers = {{}};
entityNames.forEach(function(name) {{
  entityLayers[name] = {{
    pathLine: null,
    markers: [],
    currentMarker: null,
    labelMarker: null
  }};
}});

var slider = document.getElementById('slider');
var timeDisplay = document.getElementById('time-display');
var playBtn = document.getElementById('play-btn');
var speedBtns = document.querySelectorAll('.speed-btn');
var playInterval = null;
var speed = 1;

speedBtns.forEach(function(btn) {{
  btn.addEventListener('click', function() {{
    speed = parseInt(this.dataset.speed);
    speedBtns.forEach(function(b) {{ b.classList.remove('active'); }});
    this.classList.add('active');
  }});
}});

function clearAll() {{
  entityNames.forEach(function(name) {{
    var el = entityLayers[name];
    if (el.pathLine) {{ map.removeLayer(el.pathLine); el.pathLine = null; }}
    el.markers.forEach(function(m) {{ map.removeLayer(m); }});
    el.markers = [];
    if (el.currentMarker) {{ map.removeLayer(el.currentMarker); el.currentMarker = null; }}
    if (el.labelMarker) {{ map.removeLayer(el.labelMarker); el.labelMarker = null; }}
  }});
}}

function onDocFilterChange() {{
  var f = getFilteredData();
  var maxStep = Math.max(0, f.labels.length - 1);
  slider.max = maxStep;
  slider.value = 0;
  showStep(0);
}}

function showStep(stepIdx) {{
  clearAll();
  if (stepIdx < 0) return;
  var f = getFilteredData();
  var labels = f.labels;
  var cutoffLabel = labels[Math.min(stepIdx, labels.length - 1)];
  timeDisplay.textContent = cutoffLabel || '';

  f.entities.forEach(function(name) {{
    var data = f.data[name];
    var visibleStops = data.stops.filter(function(s) {{
      return labels.indexOf(s.label) <= stepIdx;
    }});
    if (visibleStops.length === 0) return;

    var coords = visibleStops.map(function(s) {{ return [s.lat, s.lon]; }});
    var el = entityLayers[name];

    if (coords.length > 1) {{
      el.pathLine = L.polyline(coords, {{
        color: data.color, weight: 3, opacity: 0.7, dashArray: '8, 4'
      }}).addTo(map);
    }}

    visibleStops.forEach(function(s, i) {{
      var isLast = (i === visibleStops.length - 1);
      var radius = isLast ? 10 : 6;
      var opacity = isLast ? 1.0 : 0.5;
      var marker = L.circleMarker([s.lat, s.lon], {{
        radius: radius, fillColor: data.color, color: '#fff',
        weight: 2, fillOpacity: opacity
      }}).bindTooltip(s.location + ', ' + s.label, {{ permanent: false }}).addTo(map);
      el.markers.push(marker);

      if (isLast) {{
        el.currentMarker = L.circleMarker([s.lat, s.lon], {{
          radius: 14, fillColor: data.color, color: '#fff',
          weight: 3, fillOpacity: 0.9
        }}).addTo(map);
        el.labelMarker = L.tooltip({{
          permanent: true, direction: 'right', offset: [16, 0],
          className: 'entity-label'
        }}).setLatLng([s.lat, s.lon])
          .setContent('<b>' + name + '</b> &middot; &rarr; ' + s.location)
          .addTo(map);
      }}
    }});
  }});
}}

slider.addEventListener('input', function() {{
  showStep(parseInt(this.value));
}});

playBtn.addEventListener('click', function() {{
  if (playInterval) {{
    clearInterval(playInterval);
    playInterval = null;
    playBtn.textContent = '\\u25B6';
    return;
  }}
  if (parseInt(slider.value) >= parseInt(slider.max)) slider.value = 0;
  playBtn.textContent = '\\u275A\\u275A';
  playInterval = setInterval(function() {{
    var v = parseInt(slider.value) + 1;
    if (v > parseInt(slider.max)) {{
      clearInterval(playInterval);
      playInterval = null;
      playBtn.textContent = '\\u25B6';
      return;
    }}
    slider.value = v;
    showStep(v);
  }}, 1200 / speed);
}});

if (hasDocFilter) {{
  var docSel = document.getElementById('doc-filter');
  if (docSel) docSel.addEventListener('change', onDocFilterChange);
}}
showStep(0);
</script>
</body></html>"""

    title = os.path.splitext(os.path.basename(inputFilename))[0].replace('_', ' ')
    first_label = all_labels[0] if all_labels else ''

    if all_docs:
        doc_options = '<option value="">All documents</option>'
        for d in all_docs:
            doc_options += '<option value="{0}">{0}</option>'.format(d)
        doc_filter_html = '<div id="filter-bar">Document: <select id="doc-filter">{}</select></div>'.format(doc_options)
    else:
        doc_filter_html = ''

    html = html.format(
        title=title,
        legend_html=legend_html,
        doc_filter_html=doc_filter_html,
        migration_json=_json.dumps(migration_data),
        labels_json=_json.dumps(all_labels),
        entities_json=_json.dumps(all_entities),
        docs_json=_json.dumps(all_docs),
        center_lat=round(center_lat, 4),
        center_lon=round(center_lon, 4),
        max_step=max(0, len(all_labels) - 1),
        first_label=first_label)

    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    base = _safe_fn(os.path.splitext(os.path.basename(inputFilename))[0])
    output_file = os.path.join(outputDir, '{}_migration_map.html'.format(base))
    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f"  Migration map saved: {output_file}")

    return [output_file]


def proportional_circle_map(inputFilename, outputDir, location_col):
    """Build a Leaflet.js proportional circle map for a location column.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    location_col : str    Column containing location names to geocode.

    Returns
    -------
    str or ''   Path to output HTML file, or empty string on failure.
    """
    try:
        import folium
        from geopy.geocoders import Nominatim
        import time as _time
    except ImportError as e:
        print(f"  Note: folium/geopy not available for map generation: {e}")
        return ''

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return ''

    if location_col not in df.columns:
        print(f"  WARNING: Column '{location_col}' not found")
        return ''

    lat_col = None
    lon_col = None
    for c in df.columns:
        cl = c.lower().strip()
        if cl in ('latitude', 'lat'):
            lat_col = c
        elif cl in ('longitude', 'lon', 'lng'):
            lon_col = c

    geo_rows = []

    if lat_col and lon_col:
        subset = df[[location_col, lat_col, lon_col]].dropna()
        if subset.empty:
            return ''
        freq = subset[location_col].value_counts().head(50)
        for loc_name, count in freq.items():
            row = subset[subset[location_col] == loc_name].iloc[0]
            try:
                lat, lon = float(row[lat_col]), float(row[lon_col])
            except (ValueError, TypeError):
                continue
            geo_rows.append((loc_name, lat, lon, count))
    else:
        loc_data = df[location_col].dropna().astype(str)
        if loc_data.empty:
            return ''
        freq = loc_data.value_counts().head(50)
        if freq.empty:
            return ''
        geolocator = Nominatim(user_agent='NLP_Suite_visualization')
        _geo_cache = {}
        for loc_name, count in freq.items():
            if loc_name in _geo_cache:
                lat, lon = _geo_cache[loc_name]
            else:
                try:
                    result = geolocator.geocode(loc_name, timeout=5)
                    if result:
                        lat, lon = result.latitude, result.longitude
                        _geo_cache[loc_name] = (lat, lon)
                    else:
                        continue
                    _time.sleep(1.1)
                except Exception:
                    continue
            geo_rows.append((loc_name, lat, lon, count))

    if not geo_rows:
        print("  No locations could be geocoded")
        return ''

    avg_lat = sum(r[1] for r in geo_rows) / len(geo_rows)
    avg_lon = sum(r[2] for r in geo_rows) / len(geo_rows)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4,
                   tiles='CartoDB positron')
    max_count = max(r[3] for r in geo_rows)
    for loc_name, lat, lon, count in geo_rows:
        radius = max(5, (count / max_count) * 40)
        folium.CircleMarker(
            location=[lat, lon], radius=radius,
            color='#3388ff', fill=True,
            fill_color='#3388ff', fill_opacity=0.6,
            popup='{}: {}'.format(loc_name, count),
            tooltip='{} ({})'.format(loc_name, count)
        ).add_to(m)

    import re as _re
    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    base = _safe_fn(os.path.splitext(os.path.basename(inputFilename))[0])
    safe_col = _safe_fn(location_col)
    map_file = os.path.join(outputDir, '{}_{}_map.html'.format(base, safe_col))
    m.save(map_file)
    print(f"  Proportional circle map: {len(geo_rows)} locations geocoded for {location_col}")
    return map_file


def stacked_bar_from_csv(inputFilename, outputDir, group_col, segment_col, top_n=20, grouped=False):
    """Build a stacked bar chart from two categorical CSV columns.

    Parameters
    ----------
    inputFilename : str   CSV file path.
    outputDir : str
    group_col : str       Column for bar groups (Y-axis labels).
    segment_col : str     Column for bar segments (stacked colors).
    top_n : int           Show only the top N groups by total count.

    Returns
    -------
    str or ''   Path to output PNG file, or empty string on failure.
    """
    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV: {e}")
        return ''

    for c in [group_col, segment_col]:
        if c not in df.columns:
            print(f"  WARNING: Column '{c}' not found")
            return ''

    pairs = df[[group_col, segment_col]].dropna()
    if pairs.empty:
        return ''

    ct = pd.crosstab(pairs[group_col], pairs[segment_col])
    ct.columns.name = segment_col

    import re as _re
    def _safe_fn(s):
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    base = _safe_fn(os.path.splitext(os.path.basename(inputFilename))[0])
    safe_g = _safe_fn(group_col)
    safe_s = _safe_fn(segment_col)
    mode = 'grouped' if grouped else 'stacked'
    out_base = os.path.join(outputDir,
        '{}_{}_{}_{}'.format(base, mode, safe_g, safe_s))
    chart_title = '{} bar: {} by {}'.format('Grouped' if grouped else 'Stacked', group_col, segment_col)
    visualize_stacked_bar(ct, top_n=top_n,
                          x_label=group_col, y_label='Count',
                          title=chart_title,
                          outputname=out_base, grouped=grouped)
    png_file = out_base + '.png'
    if os.path.isfile(png_file):
        return png_file
    return ''


# ═══════════════════════════════════════════════════════════════════════
# Auto-charting for cross-complex / SVO query results
# Shared by DB_SQL_main.py and DB_PCACE_data_analysis_main.py
# ═══════════════════════════════════════════════════════════════════════

def auto_chart_cross_complex(csv_path, outputDir, chartPackage, filesToOpen):
    """Auto-generate charts from cross-complex or SVO query CSV results.

    Produces: bar charts, Sankey, sunburst, treemap, network graph,
    heatmap, word clouds, and proportional circle map.
    """
    import re as _re
    def _safe_filename(s):
        """Sanitize a string for use in Windows filenames."""
        return _re.sub(r'[<>:"/\\|?*]', '_', s).replace(' ', '_')

    try:
        _px = px
    except Exception:
        _px = None

    try:
        df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"  WARNING: Could not read CSV for charting: {e}")
        return

    if df.empty:
        return

    # Identify chartable columns: keep only final simplex text values
    # Exclude: _ID columns, _Simplex columns, Order columns, and purely numeric columns
    skip_cols = set()
    for c in df.columns:
        if c.endswith('_ID') or c == 'Source_ID' or c == 'Target_ID':
            skip_cols.add(c)
        elif c.endswith('_Simplex'):
            skip_cols.add(c)
        elif c.endswith(' Order') or c == 'Order':
            skip_cols.add(c)
        elif c.endswith(' Identifier'):
            skip_cols.add(c)

    candidate_cols = [c for c in df.columns if c not in skip_cols]

    # Further exclude columns that are purely numeric (IDs stored without _ID suffix)
    # or that have only one unique value (e.g., "Complex type" always = "Vertenza")
    value_cols = []
    skipped_empty = []
    skipped_numeric = []
    skipped_constant = []
    for c in candidate_cols:
        col_data = df[c].dropna()
        if col_data.empty:
            skipped_empty.append(c)
            continue
        # Skip constant columns — only one unique value, nothing to chart
        if col_data.nunique() <= 1:
            skipped_constant.append(c)
            continue
        # Check if all non-null values are numeric
        str_vals = col_data.astype(str)
        numeric_ratio = str_vals.str.match(r'^-?\d+\.?\d*$').mean()
        if numeric_ratio < 0.9:  # keep column only if <90% numeric
            value_cols.append(c)
        else:
            skipped_numeric.append(c)
    if skipped_constant:
        print(f"  Skipping constant columns (1 unique value): {skipped_constant}")

    if not value_cols:
        return

    print(f"  Auto-charting {len(value_cols)} text columns")

    # Drop NaN rows for charting
    df_clean = df.dropna(subset=value_cols, how='all').copy()
    if df_clean.empty:
        return

    # Convert value columns to string for categorical charting
    for col in value_cols:
        df_clean[col] = df_clean[col].fillna('').astype(str)
        df_clean[col] = df_clean[col].replace('', pd.NA)
    df_clean = df_clean.dropna(subset=value_cols, how='all')
    if df_clean.empty:
        return

    base_name = _safe_filename(os.path.splitext(os.path.basename(csv_path))[0])

    # For datasets with many columns, pick a small set of "key" columns
    # that represent the main S-V-O or source-target relationship.
    # Heuristic: prefer columns with "Value" in the name, or the shortest
    # column names (they tend to be the primary ones like Source_Value, Target_Value).
    # Limit bar charts and word clouds to at most 6 columns.
    MAX_CHART_COLS = 6
    if len(value_cols) > MAX_CHART_COLS:
        # Prefer columns containing common simplex-value keywords (multi-language)
        primary = [c for c in value_cols if any(kw.lower() in c.lower() for kw in
                   ['Value', 'Verbal', 'verbale', 'Name', 'nome', 'Frase',
                    'Participant', 'Partecipant', 'Process', 'Processo'])]
        if not primary:
            primary = value_cols
        chart_cols = primary[:MAX_CHART_COLS]
    else:
        chart_cols = value_cols

    # For Sankey/sunburst/treemap/network/heatmap, merge all sub-columns
    # per SVO role into one combined column.  The real data has many
    # sub-columns per role (e.g., 14 Participant-S columns), each very
    # sparse.  We coalesce them: first non-null value across all
    # sub-columns for that role → single "Subject" / "Verb" / "Object".
    def _merge_svo(dataframe, all_cols):
        """Create merged Subject, Verb, Object columns from sparse sub-cols.
        Returns (new_df, svo_col_names) where svo_col_names is a list of
        the 2-3 merged column names actually created."""
        # Match on column PREFIX (part before first '>') to avoid
        # false matches like 'Verbal phrase' matching 'Verb' patterns.
        # For columns without '>' (e.g., Source_Value), match the full name.
        def _prefix(col):
            return col.split(' > ')[0].strip()

        # For each SVO role, prefer columns whose names suggest the "main" value:
        #   Subject/Object: Name, Nome, individual, individuo, actor, attore
        #   Verb: Verbal, verbale, Frase, phrase
        # Columns matching these keywords are sorted first so coalesce picks them.
        _so_keywords = ['name', 'nome', 'individual', 'individuo', 'actor', 'attore', 'collective', 'collettivo']
        _v_keywords = ['verbal', 'verbale', 'frase', 'phrase']

        role_map = [
            ('Subject', ['Participant-S', 'PARTECIPANTE-S', 'Partecipante-S',
                         'Subject', 'Source_Value'], _so_keywords),
            ('Verb',    ['Process', 'PROCESSO', 'Processo',
                         'Simple process', 'Processo semplice'], _v_keywords),
            ('Object',  ['Participant-O', 'PARTECIPANTE-O', 'Partecipante-O',
                         'Object', 'Target_Value'], _so_keywords),
        ]
        new_df = dataframe.copy()
        created = []
        for role_name, patterns, preferred_kw in role_map:
            # Case-insensitive prefix matching: startswith to handle
            # variants like "Processo semplice" matching "Processo"
            role_cols = [c for c in all_cols
                         if any(p.lower() == _prefix(c).lower()
                                or _prefix(c).lower().startswith(p.lower())
                                or p.lower() == c.lower()
                                for p in patterns)]
            if not role_cols:
                continue
            # Sort: columns matching preferred keywords first
            def _priority(col):
                cl = col.lower()
                return 0 if any(kw in cl for kw in preferred_kw) else 1
            role_cols.sort(key=_priority)
            print(f"    {role_name} columns (priority-sorted): {role_cols}")
            # Coalesce: first non-null across role_cols for each row
            merged = new_df[role_cols[0]].copy()
            for rc in role_cols[1:]:
                merged = merged.fillna(new_df[rc])
            merged = merged.astype(str).replace('nan', pd.NA)
            new_df[role_name] = merged
            created.append(role_name)
        return new_df, created

    df_svo, svo_cols = _merge_svo(df_clean, value_cols)
    # Dynamic label: "SV" when only Subject+Verb, "SVO" when all three
    _role_initials = {'Subject': 'S', 'Verb': 'V', 'Object': 'O'}
    _svo_label = ''.join(_role_initials.get(c, c[0]) for c in svo_cols) or 'SV'
    _role_arrow_label = ' → '.join(svo_cols)               # "Subject → Verb" or "Subject → Verb → Object"
    _role_arrow_short = ' → '.join(_role_initials.get(c, c[0]) for c in svo_cols)  # "S → V" or "S → V → O"
    print(f"  Merged {_svo_label} columns: {svo_cols}")
    if svo_cols:
        for sc in svo_cols:
            nn = df_svo[sc].dropna().shape[0]
            print(f"    {sc}: {nn}/{len(df_svo)} non-null")

    # ── 1. Bar charts: frequency distribution of key Value columns ──────
    if _px:
        for col in chart_cols:
            col_data = df_clean[col].dropna().astype(str)
            if col_data.empty:
                continue
            freq = col_data.value_counts().head(30)
            if freq.empty:
                continue
            freq_df = freq.reset_index()
            freq_df.columns = [col, 'Frequency']
            safe_col = _safe_filename(col)
            try:
                fig = _px.bar(freq_df, x=col, y='Frequency',
                             title='Top 30 Frequency: {}'.format(col))
                # Force categorical x-axis so Plotly doesn't auto-detect
                # city names or other text as dates
                fig.update_xaxes(type='category')
                bar_file = os.path.join(outputDir, 'SQL_{}_bar.html'.format(safe_col))
                fig.write_html(bar_file)
                filesToOpen.append(bar_file)
            except Exception as e:
                print(f"  WARNING: Bar chart for {col}: {e}")

    # ── 2. Sankey diagram: flow between merged S-V-O columns ─────────────
    if len(svo_cols) >= 2:
        sankey_df = df_svo[svo_cols].dropna(how='all').copy()
        for sc in svo_cols:
            sankey_df[sc] = sankey_df[sc].fillna('(none)').astype(str)
        # Limit to top N values per column for readability
        TOP_SANKEY = 10
        for sc in svo_cols:
            top_vals = sankey_df[sc].value_counts().head(TOP_SANKEY).index.tolist()
            sankey_df = sankey_df[sankey_df[sc].isin(top_vals + ['(none)'])]
        sankey_df = sankey_df.reset_index(drop=True)
        if not sankey_df.empty and len(sankey_df) > 0:
            try:
                three_way = len(svo_cols) >= 3
                sankey_out = os.path.join(outputDir, '{}_sankey.html'.format(base_name))
                print(f"  Sankey: using columns {svo_cols}, {len(sankey_df)} rows")
                Sankey(
                    data=sankey_df,
                    outputFilename=sankey_out,
                    var1=svo_cols[0],
                    lengthvar1=10,
                    var2=svo_cols[1],
                    lengthvar2=10,
                    three_way_Sankey=three_way,
                    var3=svo_cols[2] if three_way else None,
                    lengthvar3=10 if three_way else None)
                if os.path.exists(sankey_out):
                    filesToOpen.append(sankey_out)
                    print(f"  Sankey saved: {sankey_out}")
            except Exception as e:
                import traceback
                print(f"  WARNING: Sankey chart failed: {e}")
                traceback.print_exc()

    # ── 3. Sunburst & Treemap: hierarchical view of merged S-V-O ─────────
    if _px and len(svo_cols) >= 2:
        hier_df = df_svo[svo_cols].dropna(how='all').copy()
        for sc in svo_cols:
            hier_df[sc] = hier_df[sc].fillna('(none)').astype(str)
        print(f"  Sunburst/Treemap: columns={svo_cols}, rows={len(hier_df)}")
        if not hier_df.empty:
            # Limit to top values per column to keep charts readable
            TOP_N = 20
            for sc in svo_cols:
                top_vals = hier_df[sc].value_counts().head(TOP_N).index.tolist()
                hier_df = hier_df[hier_df[sc].isin(top_vals + ['(none)'])]
            grouped = hier_df.groupby(svo_cols).size().reset_index(name='Count')
            if not grouped.empty and len(grouped) > 0:
                # Sunburst — show all levels expanded
                try:
                    fig = _px.sunburst(grouped, path=svo_cols, values='Count',
                                      title='Sunburst: {}'.format(' → '.join(svo_cols)),
                                      maxdepth=-1)
                    fig.update_traces(maxdepth=-1)
                    sunburst_file = os.path.join(outputDir, '{}_sunburst.html'.format(base_name))
                    fig.write_html(sunburst_file)
                    filesToOpen.append(sunburst_file)
                    print(f"  Sunburst saved: {sunburst_file}")
                except Exception as e:
                    import traceback
                    print(f"  WARNING: Sunburst chart: {e}")
                    traceback.print_exc()

                # Treemap — show all levels expanded
                try:
                    fig = _px.treemap(grouped, path=svo_cols, values='Count',
                                     title='Treemap: {}'.format(' → '.join(svo_cols)),
                                     maxdepth=-1)
                    fig.update_traces(maxdepth=-1)
                    treemap_file = os.path.join(outputDir, '{}_treemap.html'.format(base_name))
                    fig.write_html(treemap_file)
                    filesToOpen.append(treemap_file)
                    print(f"  Treemap saved: {treemap_file}")
                except Exception as e:
                    import traceback
                    print(f"  WARNING: Treemap chart: {e}")
                    traceback.print_exc()
        else:
            print(f"  Sunburst/Treemap skipped: no rows after filtering on {svo_cols}")

    # ── Detect a date column for time-dependent visualizations ───────────
    _date_col = None
    _date_candidates = ['Date', 'Newspaper date', 'Newspaper Date',
                        'Data giornale', 'Data del giornale', 'Action date']
    for _dc in _date_candidates:
        if _dc in df.columns:
            _parsed = pd.to_datetime(df[_dc], errors='coerce')
            if _parsed.notna().sum() > 0:
                _date_col = _dc
                break
    if _date_col:
        print(f"  Date column for time slider: '{_date_col}'")

    # ── 4. Interactive network graph (vis.js) ─────────────────────────────
    # Click a node → highlight the full S→V→O chains that pass through it
    # and list them in the info panel (e.g. "mob → shot → Negro (12)").
    TOP_NET_PER_ROLE = 15
    if len(svo_cols) >= 2:
        try:
            _net_cols = list(svo_cols)
            if _date_col and _date_col in df_svo.columns:
                _net_cols.append(_date_col)
            net_df = df_svo[_net_cols].dropna(subset=svo_cols, how='all').copy()
            for _sc in svo_cols:
                net_df[_sc] = net_df[_sc].fillna('').astype(str)
            if not net_df.empty:
                palette = {'S': '#E04040', 'V': '#4060E0', 'O': '#30A030'}
                role_of = {}
                top_per_role = {}
                role_keys = ['S', 'V', 'O']
                for idx_r, sc in enumerate(svo_cols):
                    rk = role_keys[idx_r] if idx_r < len(role_keys) else role_keys[-1]
                    top_vals = net_df[sc].value_counts().head(TOP_NET_PER_ROLE).index.tolist()
                    top_per_role[sc] = set(top_vals)
                    for v in top_vals:
                        if v and v not in role_of:
                            role_of[v] = rk

                mask = net_df.apply(
                    lambda row: all(row[c] in top_per_role[c] or row[c] == ''
                                    for c in svo_cols), axis=1)
                net_df = net_df[mask]

                # Build edge dict with weights and date lists
                edges = {}
                edge_dates = {}
                _has_dates = _date_col and _date_col in net_df.columns
                for _, row in net_df.iterrows():
                    vals = [row[c] for c in svo_cols if row[c]]
                    row_date = None
                    if _has_dates and pd.notna(row.get(_date_col)):
                        row_date = pd.to_datetime(row[_date_col], errors='coerce')
                        if pd.isna(row_date):
                            row_date = None
                    for i in range(len(vals) - 1):
                        key = (vals[i], vals[i + 1])
                        edges[key] = edges.get(key, 0) + 1
                        if row_date is not None:
                            edge_dates.setdefault(key, []).append(row_date)

                # Build triplet counts for the info panel
                # triplet_counts["mob|shot|Negro"] = 12
                triplet_counts = {}
                triplet_dates = {}
                for _, row in net_df.iterrows():
                    vals = tuple(row[c] for c in svo_cols)
                    if any(v == '' for v in vals):
                        continue
                    triplet_counts[vals] = triplet_counts.get(vals, 0) + 1
                    if _has_dates:
                        row_date = None
                        if pd.notna(row.get(_date_col)):
                            row_date = pd.to_datetime(row[_date_col], errors='coerce')
                            if pd.isna(row_date):
                                row_date = None
                        if row_date is not None:
                            triplet_dates.setdefault(vals, []).append(row_date)

                # Index: for each node label, which triplets contain it?
                # node_triplets["mob"] = [["mob","shot","Negro",12], ...]
                node_triplets = {}
                for triplet, cnt in triplet_counts.items():
                    for val in triplet:
                        node_triplets.setdefault(val, []).append(list(triplet) + [cnt])

                all_nodes = set()
                for (s, t) in edges:
                    all_nodes.add(s)
                    all_nodes.add(t)

                # Compute frequency per node value across all SVO columns
                import math as _math
                node_freq = {}
                for sc in svo_cols:
                    for val, cnt in net_df[sc].value_counts().items():
                        if val:
                            node_freq[val] = node_freq.get(val, 0) + cnt

                print(f"  Network graph: {len(all_nodes)} nodes, {len(edges)} edges, {len(triplet_counts)} unique triplets")
                if all_nodes:
                    import json as _json

                    # Scale node sizes: log-based, min=8, max=45
                    freq_vals = [node_freq.get(n, 1) for n in all_nodes]
                    max_freq = max(freq_vals) if freq_vals else 1
                    min_freq = min(freq_vals) if freq_vals else 1
                    SIZE_MIN, SIZE_MAX = 8, 45

                    def _node_size(freq):
                        if max_freq == min_freq:
                            return (SIZE_MIN + SIZE_MAX) / 2
                        # log scale so high-frequency nodes don't dwarf everything
                        log_ratio = _math.log(1 + freq - min_freq) / _math.log(1 + max_freq - min_freq)
                        return SIZE_MIN + log_ratio * (SIZE_MAX - SIZE_MIN)

                    node_id_map = {n: i for i, n in enumerate(sorted(all_nodes))}
                    vis_nodes = []
                    for n, nid in node_id_map.items():
                        rk = role_of.get(n, role_keys[min(len(svo_cols), 3) - 1])
                        freq = node_freq.get(n, 1)
                        sz = round(_node_size(freq), 1)
                        # Font size scales with node: bigger nodes get bigger labels
                        fsz = max(10, min(22, int(10 + (sz - SIZE_MIN) / (SIZE_MAX - SIZE_MIN) * 12)))
                        vis_nodes.append({
                            'id': nid, 'label': n,
                            'color': palette.get(rk, '#888'),
                            'font': {'size': fsz},
                            'shape': 'dot',
                            'size': sz,
                            'title': '{} (freq: {})'.format(n, freq),
                            'role': rk})
                    vis_edges = []
                    for (s, t), w in edges.items():
                        e_entry = {
                            'from': node_id_map[s],
                            'to': node_id_map[t],
                            'value': w,
                            'title': '{} → {} ({})'.format(s, t, w),
                            'color': {'color': '#aaaaaa', 'highlight': '#333333'}}
                        if _has_dates and (s, t) in edge_dates:
                            e_entry['dates'] = sorted(set(
                                d.strftime('%Y-%m-%d') for d in edge_dates[(s, t)]))
                        vis_edges.append(e_entry)

                    # Collect all unique dates across the dataset for the time slider
                    _all_dates_set = set()
                    if _has_dates:
                        for dlist in edge_dates.values():
                            for d in dlist:
                                _all_dates_set.add(d.strftime('%Y-%m-%d'))
                        # Also attach dates to nodes
                        node_dates = {}
                        for (s, t), dlist in edge_dates.items():
                            for d in dlist:
                                ds = d.strftime('%Y-%m-%d')
                                node_dates.setdefault(node_id_map[s], set()).add(ds)
                                node_dates.setdefault(node_id_map[t], set()).add(ds)
                        for vn in vis_nodes:
                            nid = vn['id']
                            if nid in node_dates:
                                vn['dates'] = sorted(node_dates[nid])
                    _all_dates_sorted = sorted(_all_dates_set) if _all_dates_set else []

                    # Build JS-friendly triplet index keyed by node id
                    # nodeTriplets[nodeId] = [[s,v,o,count], ...]
                    js_node_triplets = {}
                    for label, trips in node_triplets.items():
                        nid = node_id_map.get(label)
                        if nid is not None:
                            # Sort by count descending, keep top 30
                            trips_sorted = sorted(trips, key=lambda x: -x[-1])[:30]
                            js_node_triplets[nid] = trips_sorted

                    role_labels = ['Subject', 'Verb', 'Object'][:len(svo_cols)]

                    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{svo_label} Network</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; margin: 0; }}
  #network {{ width: 100%; height: {network_height}; border: 1px solid #ccc; }}
  #title {{ text-align: center; padding: 8px; font-size: 16px; font-weight: bold; }}
  #legend {{ text-align: center; padding: 4px; font-size: 13px; }}
  .leg {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%;
          vertical-align: middle; margin: 0 3px 0 12px; }}
  .leg-e {{ display: inline-block; width: 20px; height: 4px;
            vertical-align: middle; margin: 0 3px 0 10px; border-radius: 2px; }}
  #time-slider-container {{ display: {slider_display}; padding: 6px 20px;
           background: #f8f8f8; border-top: 1px solid #ddd; text-align: center; }}
  #time-slider-container label {{ font-size: 13px; margin-right: 8px; }}
  #time-slider {{ width: 60%; vertical-align: middle; }}
  #time-label {{ font-weight: bold; font-size: 13px; margin-left: 8px; min-width: 100px;
                 display: inline-block; }}
  #time-slider-container button {{ margin-left: 12px; font-size: 12px; padding: 2px 10px;
                                    cursor: pointer; }}
  #info {{ padding: 8px 16px; font-size: 13px; color: #333;
           max-height: 18vh; overflow-y: auto; border-top: 1px solid #ccc; }}
  #info table {{ border-collapse: collapse; margin: 4px auto; }}
  #info th, #info td {{ padding: 2px 10px; text-align: left; }}
  #info th {{ border-bottom: 1px solid #999; }}
  .s {{ color: #E04040; font-weight: bold; }}
  .v {{ color: #4060E0; font-weight: bold; }}
  .o {{ color: #30A030; font-weight: bold; }}
</style>
</head><body>
<div id="title">{svo_label} Network (top {top_n} per role) &mdash; click a node to see full {role_arrow_label} chains</div>
<div id="legend">{legend_html} &nbsp;&nbsp;&nbsp; <span style="font-size:12px;color:#666">&#9679; Node size = frequency</span></div>
<div id="time-slider-container">
  <label>Timeline:</label>
  <input type="range" id="time-slider" min="0" max="0" value="0" step="1">
  <span id="time-label">All dates</span>
  <button id="time-play">&#9654; Play</button>
  <button id="time-reset">Show All</button>
</div>
<div id="network"></div>
<div id="info">Click a node to see its {role_arrow_short} relationships.</div>
<script>
var allDates = {all_dates_json};
var nodes = new vis.DataSet({nodes_json});
var edges = new vis.DataSet({edges_json});
var nodeTriplets = {triplets_json};
var container = document.getElementById('network');
var gdata = {{ nodes: nodes, edges: edges }};
var options = {{
  physics: {{ solver: 'forceAtlas2Based',
              forceAtlas2Based: {{ gravitationalConstant: -60, springLength: 150,
                                  springConstant: 0.04, damping: 0.5 }},
              stabilization: {{ iterations: 200 }} }},
  interaction: {{ hover: true, tooltipDelay: 100 }},
  nodes: {{ scaling: {{ min: 8, max: 45 }} }},
  edges: {{ arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
            smooth: {{ type: 'continuous' }}, scaling: {{ min: 1, max: 6 }} }}
}};
var network = new vis.Network(container, gdata, options);

// Store original sizes/fonts for reset
var origNodeProps = {{}};
nodes.forEach(function(n) {{
  origNodeProps[n.id] = {{ size: n.size, fontSize: n.font ? n.font.size : 14 }};
}});

function resetAll() {{
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                    font: {{ size: orig.fontSize, color: '#333' }} }});
  }});
  edges.forEach(function(e) {{
    edges.update({{ id: e.id, color: {{ color: '#aaaaaa', opacity: 1.0 }} }});
  }});
}}

// ── Time slider logic ──
var slider = document.getElementById('time-slider');
var timeLabel = document.getElementById('time-label');
var playBtn = document.getElementById('time-play');
var resetBtn = document.getElementById('time-reset');
var playInterval = null;
if (allDates.length > 0) {{
  // Slider range: 0 = "all", 1..N = each date
  slider.max = allDates.length;
  slider.value = 0;
  slider.addEventListener('input', function() {{ applyTimeFilter(parseInt(this.value)); }});
  resetBtn.addEventListener('click', function() {{ slider.value = 0; applyTimeFilter(0); stopPlay(); }});
  playBtn.addEventListener('click', function() {{
    if (playInterval) {{ stopPlay(); return; }}
    if (parseInt(slider.value) >= allDates.length) slider.value = 0;
    playInterval = setInterval(function() {{
      var v = parseInt(slider.value) + 1;
      if (v > allDates.length) {{ stopPlay(); return; }}
      slider.value = v;
      applyTimeFilter(v);
    }}, 800);
    playBtn.textContent = '\\u275A\\u275A Pause';
  }});
}}
function stopPlay() {{
  if (playInterval) {{ clearInterval(playInterval); playInterval = null; }}
  playBtn.textContent = '\\u25B6 Play';
}}
function applyTimeFilter(idx) {{
  if (idx === 0 || allDates.length === 0) {{
    timeLabel.textContent = 'All dates';
    resetAll();
    return;
  }}
  var cutoff = allDates[idx - 1];
  timeLabel.textContent = cutoff;
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    var dates = n.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    if (visible) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: orig.fontSize, color: '#333' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.05, size: Math.max(4, orig.size * 0.3),
                      font: {{ size: 6, color: '#ddd' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var dates = e.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (visible) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eee', opacity: 0.03 }} }});
    }}
  }});
}}

// Build a lookup: label → id
var labelToId = {{}};
nodes.forEach(function(n) {{ labelToId[n.label] = n.id; }});

network.on("click", function(params) {{
  var infoDiv = document.getElementById('info');
  if (params.nodes.length === 0) {{
    resetAll();
    infoDiv.innerHTML = 'Click a node to see its {info_click_msg} relationships.';
    return;
  }}
  var clickedId = params.nodes[0];
  var clickedNode = nodes.get(clickedId);
  var trips = nodeTriplets[clickedId] || [];

  // Collect all node ids involved in the triplets
  var involvedIds = new Set();
  involvedIds.add(clickedId);
  trips.forEach(function(t) {{
    for (var i = 0; i < t.length - 1; i++) {{
      var nid = labelToId[t[i]];
      if (nid !== undefined) involvedIds.add(nid);
    }}
  }});

  // Collect all edges between involved nodes
  var involvedEdgeIds = new Set();
  edges.forEach(function(e) {{
    if (involvedIds.has(e.from) && involvedIds.has(e.to)) {{
      involvedEdgeIds.add(e.id);
    }}
  }});

  // Dim / highlight — preserve original sizes for highlighted nodes
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    if (involvedIds.has(n.id)) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: Math.max(orig.fontSize, 14), color: '#000' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.10, size: Math.max(6, orig.size * 0.5),
                      font: {{ size: 8, color: '#ccc' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (involvedEdgeIds.has(e.id)) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eee', opacity: 0.08 }} }});
    }}
  }});

  // Build info table showing full role tuples
  if (trips.length === 0) {{
    infoDiv.innerHTML = '<b>' + clickedNode.label + '</b>: no full {no_triplets_msg} tuples.';
    return;
  }}
  var html = '<b>' + clickedNode.label + '</b> &mdash; '
           + trips.length + ' tuple(s):<br>'
           + '<table><tr>{table_header_html}</tr>';
  trips.forEach(function(t) {{
    html += '<tr>' + {table_row_js} + '</tr>';
  }});
  html += '</table>';
  infoDiv.innerHTML = html;
}});
</script>
</body></html>"""

                    legend_parts = []
                    for rk, rl in zip(['S', 'V', 'O'], role_labels):
                        legend_parts.append(
                            '<span class="leg" style="background:{}"></span>{}'.format(
                                palette[rk], rl))
                    legend_html = '  '.join(legend_parts)

                    # ── Build dynamic JS template fragments for the info panel ──
                    _role_css = {'Subject': 's', 'Verb': 'v', 'Object': 'o'}
                    # Table header:  <th>Subject</th><th></th><th>Verb</th><th>Count</th>
                    _th = []
                    for _i, _rc in enumerate(svo_cols):
                        if _i > 0:
                            _th.append('<th></th>')
                        _th.append('<th>{}</th>'.format(_rc))
                    _th.append('<th>Count</th>')
                    _table_header_html = ''.join(_th)
                    # Row expression (JS): '<td class="s">' + t[0] + '</td><td>→</td>...'
                    _td = []
                    for _i, _rc in enumerate(svo_cols):
                        _css = _role_css.get(_rc, '')
                        if _i > 0:
                            _td.append("'<td>&rarr;</td>'")
                        _td.append("'<td class=\"{}\">' + t[{}] + '</td>'".format(_css, _i))
                    _td.append("'<td>' + t[{}] + '</td>'".format(len(svo_cols)))
                    _table_row_js = ' + '.join(_td)
                    # Info-panel messages
                    _info_click = ' &rarr; '.join(
                        _role_initials.get(c, c[0]) for c in svo_cols)
                    _no_triplets = ' → '.join(
                        _role_initials.get(c, c[0]) for c in svo_cols)

                    html = html.format(
                        svo_label=_svo_label,
                        role_arrow_label=_role_arrow_label,
                        role_arrow_short=_role_arrow_short,
                        info_click_msg=_info_click,
                        no_triplets_msg=_no_triplets,
                        table_header_html=_table_header_html,
                        table_row_js=_table_row_js,
                        top_n=TOP_NET_PER_ROLE,
                        legend_html=legend_html,
                        nodes_json=_json.dumps(vis_nodes),
                        edges_json=_json.dumps(vis_edges),
                        triplets_json=_json.dumps(js_node_triplets),
                        all_dates_json=_json.dumps(_all_dates_sorted),
                        network_height='70vh' if _all_dates_sorted else '75vh',
                        slider_display='block' if _all_dates_sorted else 'none')

                    network_file = os.path.join(outputDir, '{}_network.html'.format(base_name))
                    with open(network_file, 'w', encoding='utf-8') as fh:
                        fh.write(html)
                    filesToOpen.append(network_file)
                    print(f"  Network saved: {network_file}")

                    # ── 4b. Gephi .gexf export ──────────────────────────────
                    # Export the same network as a .gexf file for Gephi.
                    # Uses the Gexf classes from Gephi_util directly (no Gephi
                    # install required — just produces the XML file).
                    try:
                        import Gephi_util as _gephi

                        rgb_map = {
                            'S': (224, 64, 64),    # red
                            'V': (64, 96, 224),    # blue
                            'O': (48, 160, 48),    # green
                        }

                        _gexf_dynamic = _has_dates and len(edge_dates) > 0
                        _gexf_mode = "dynamic" if _gexf_dynamic else "static"
                        _gexf_tf = "date" if _gexf_dynamic else ""

                        gexf = _gephi.Gexf("NLP Suite", "{} Network".format(_svo_label))
                        graph = gexf.addGraph("directed", _gexf_mode,
                                              "{} Network".format(_svo_label),
                                              timeformat=_gexf_tf)
                        # Node attribute: role
                        _default_role = role_keys[-1] if role_keys else 'S'
                        role_attr_id = graph.addNodeAttribute("Role", _default_role, "string", "static")

                        # Build node spells from edge_dates
                        _node_spells = {}
                        if _gexf_dynamic:
                            for (s, t), dlist in edge_dates.items():
                                for d in dlist:
                                    ds = d.strftime('%Y-%m-%d')
                                    _node_spells.setdefault(s, []).append(
                                        {"start": ds, "end": ds})
                                    _node_spells.setdefault(t, []).append(
                                        {"start": ds, "end": ds})

                        # Add nodes with role-colored dots and frequency-based size
                        for n, nid in node_id_map.items():
                            rk = role_of.get(n, role_keys[min(len(svo_cols), 3) - 1])
                            freq = node_freq.get(n, 1)
                            r, g_c, b = rgb_map.get(rk, (128, 128, 128))
                            spells = _node_spells.get(n, []) if _gexf_dynamic else []
                            node = graph.addNode(str(nid), n,
                                                 r=str(r), g=str(g_c), b=str(b),
                                                 size=str(max(10, freq)),
                                                 spells=spells)
                            node.addAttribute(role_attr_id, rk)

                        # Add edges with weight and spells
                        for eidx, ((s, t), w) in enumerate(edges.items()):
                            espells = []
                            if _gexf_dynamic and (s, t) in edge_dates:
                                for d in edge_dates[(s, t)]:
                                    ds = d.strftime('%Y-%m-%d')
                                    espells.append({"start": ds, "end": ds})
                            graph.addEdge(str(eidx),
                                          str(node_id_map[s]),
                                          str(node_id_map[t]),
                                          weight=str(w),
                                          label='{} → {}'.format(s, t),
                                          spells=espells)

                        gexf_file = os.path.join(outputDir, '{}_network.gexf'.format(base_name))
                        with open(gexf_file, 'wb') as gf:
                            gexf.write(gf, print_stat=False)
                        filesToOpen.append(gexf_file)
                        print(f"  Gephi .gexf saved: {gexf_file}")
                    except ImportError:
                        print("  Gephi_util not available — skipping .gexf export")
                    except Exception as ge:
                        print(f"  WARNING: Gephi .gexf export: {ge}")

        except Exception as e:
            import traceback
            print(f"  WARNING: Network graph: {e}")
            traceback.print_exc()

    # ── 5. Heatmap: cross-tabulation of first two role columns ────────────
    if _px and len(svo_cols) >= 2:
        try:
            heat_df = df_svo[[svo_cols[0], svo_cols[1]]].dropna(how='all').fillna('(none)').astype(str)
            if not heat_df.empty:
                ctab = pd.crosstab(heat_df[svo_cols[0]], heat_df[svo_cols[1]])
                top_rows = ctab.sum(axis=1).nlargest(30).index
                top_cols_ct = ctab.sum(axis=0).nlargest(30).index
                ctab = ctab.loc[ctab.index.isin(top_rows), ctab.columns.isin(top_cols_ct)]
                if not ctab.empty:
                    fig = _px.imshow(ctab, text_auto=True, aspect='auto',
                                    title='Heatmap: {} × {}'.format(svo_cols[0], svo_cols[1]),
                                    labels=dict(x=svo_cols[1], y=svo_cols[0], color='Count'))
                    heatmap_file = os.path.join(outputDir, '{}_heatmap.html'.format(base_name))
                    fig.write_html(heatmap_file)
                    filesToOpen.append(heatmap_file)
        except Exception as e:
            print(f"  WARNING: Heatmap: {e}")

    # ── 6. Word cloud: role colored (S=red, V=blue, O=green) ──────────────
    # Reproduces the logic from wordclouds_util.SVOWordCloud inline so we
    # avoid importing wordclouds_util (which triggers stanza downloads).
    svo_wc_done = False
    if len(svo_cols) >= 2:
        try:
            from wordcloud import WordCloud as _WC
            from collections import Counter as _Counter
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as _plt

            # Grouped color function (same as wordclouds_util.GroupedColorFunc)
            class _GroupedColor:
                def __init__(self, color_to_words, default_color):
                    self.mapping = [
                        ('rgb({},{},{})'.format(*[int(x) for x in col.strip('()').split(',')]),
                         set(words))
                        for col, words in color_to_words.items()]
                    dc = [int(x) for x in default_color.strip('()').split(',')]
                    self.default = 'rgb({},{},{})'.format(*dc)
                def __call__(self, word, **kw):
                    for rgb, words in self.mapping:
                        if word in words:
                            return rgb
                    return self.default

            red   = "(250, 0, 0)"     # Subject
            blue  = "(0, 0, 250)"     # Verb
            green = "(0, 250, 0)"     # Object
            grey  = "(169, 169, 169)"
            color_map = {red: [], blue: [], green: []}

            svo_wc_df = df_svo[svo_cols].dropna(how='all').fillna('').astype(str)
            words_list = []

            def _clean_phrase(val):
                """Strip punctuation per word but keep multi-word phrases together
                by joining with underscores (WordCloud treats _ as part of a word).
                Underscores are rendered visually as spaces via _normalize_underscores."""
                words = []
                for w in val.lower().split():
                    cleaned = ''.join(filter(str.isalnum, w))
                    if cleaned:
                        words.append(cleaned)
                return '_'.join(words) if words else ''

            for _, row in svo_wc_df.iterrows():
                s_val = row.get('Subject', '')
                v_val = row.get('Verb', '')
                o_val = row.get('Object', '')
                if s_val:
                    clean = _clean_phrase(s_val)
                    if clean:
                        words_list.append(clean)
                        color_map[red].append(clean)
                if v_val:
                    clean = _clean_phrase(v_val)
                    if clean:
                        words_list.append(clean)
                        color_map[blue].append(clean)
                if o_val:
                    clean = _clean_phrase(o_val)
                    if clean:
                        words_list.append(clean)
                        color_map[green].append(clean)

            if words_list:
                freq = _Counter(words_list)
                # Replace underscores with thin spaces in display keys so
                # "white_woman" renders as "white woman" with minimal gap
                # Use THIN SPACE (U+2009) to keep multi-word phrases
                # visually tight — much narrower gap than a regular space
                _THIN = ' '
                freq_display = {k.replace('_', _THIN): v for k, v in freq.items()}
                # Update color_map keys to match the display form
                color_map_display = {}
                for color_key, wlist in color_map.items():
                    color_map_display[color_key] = [w.replace('_', _THIN) for w in wlist]

                # regexp: include thin space (U+2009) so phrases stay as one token
                wc = _WC(width=800, height=800, max_words=1000,
                         prefer_horizontal=0.9, collocations=False,
                         regexp=r"[\w][\w ]+",
                         contour_width=3, background_color='white'
                         ).generate_from_frequencies(freq_display)
                wc.recolor(color_func=_GroupedColor(color_map_display, grey))
                _plt.figure(figsize=(8, 8), facecolor=None)
                _plt.imshow(wc, interpolation='bilinear')
                _wc_legend_parts = []
                _wc_colors = {'Subject': 'red', 'Verb': 'blue', 'Object': 'green'}
                for _rc in svo_cols:
                    _wc_legend_parts.append('{} ({})'.format(_rc, _wc_colors.get(_rc, 'grey')))
                _wc_title = '{} Word Cloud:  {}'.format(_svo_label, '  —  '.join(_wc_legend_parts))
                _plt.title(_wc_title, fontsize=12, fontweight='bold', pad=20)
                _plt.axis('off')
                wc_file = os.path.join(outputDir, 'SQL_{}_wordcloud.png'.format(_svo_label))
                wc.to_file(wc_file)
                filesToOpen.append(wc_file)
                _plt.close()
                print(f"  {_svo_label} Word Cloud saved: {wc_file}")
                svo_wc_done = True
        except ImportError:
            pass
        except Exception as e:
            import traceback
            print(f"  WARNING: {_svo_label} Word Cloud failed: {e}")
            traceback.print_exc()

    # Fall back to plain word clouds if SVO word cloud was not produced
    if not svo_wc_done:
        try:
            from wordcloud import WordCloud as _WC2
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as _plt2

            for col in chart_cols:
                col_data = df_clean[col].dropna().astype(str)
                if col_data.empty or len(col_data) < 2:
                    continue
                non_numeric = col_data[~col_data.str.match(r'^-?\d+\.?\d*$')]
                if non_numeric.empty:
                    continue
                # Use generate_from_frequencies to keep multi-word phrases intact
                # Replace regular spaces with THIN SPACE (U+2009) for tighter rendering
                from collections import Counter as _Counter2
                phrase_freq_raw = _Counter2(non_numeric.str.strip().str.lower().tolist())
                phrase_freq = {k.replace(' ', ' '): v for k, v in phrase_freq_raw.items()}
                # Remove empty keys
                phrase_freq.pop('', None)
                phrase_freq.pop('nan', None)
                if not phrase_freq:
                    continue
                try:
                    wc = _WC2(width=800, height=400, background_color='white',
                              max_words=100, collocations=False,
                              regexp=r"[\w][\w ]+"
                              ).generate_from_frequencies(phrase_freq)
                    safe_col = _safe_filename(col)
                    wc_file = os.path.join(outputDir, 'SQL_{}_wordcloud.png'.format(safe_col))
                    wc.to_file(wc_file)
                    filesToOpen.append(wc_file)
                except Exception as e:
                    print(f"  WARNING: Word cloud for {col}: {e}")
        except ImportError:
            pass

    # ── 7. Proportional circle map (Leaflet.js via folium) ───────────────
    _LOCATION_KEYWORDS = {'city', 'state', 'country', 'location', 'place', 'town',
                          'province', 'region', 'county', 'municipality'}
    location_cols = [c for c in value_cols
                     if any(kw in c.lower() for kw in _LOCATION_KEYWORDS)]
    if location_cols:
        try:
            import folium
            from geopy.geocoders import Nominatim
            import time as _time

            geolocator = Nominatim(user_agent='NLP_Suite_cross_complex')
            _geo_cache = {}

            for loc_col in location_cols:
                loc_data = df_clean[loc_col].dropna().astype(str)
                if loc_data.empty:
                    continue
                freq = loc_data.value_counts().head(50)
                if freq.empty:
                    continue

                geo_rows = []
                for loc_name, count in freq.items():
                    if loc_name in _geo_cache:
                        lat, lon = _geo_cache[loc_name]
                    else:
                        try:
                            result = geolocator.geocode(loc_name, timeout=5)
                            if result:
                                lat, lon = result.latitude, result.longitude
                                _geo_cache[loc_name] = (lat, lon)
                            else:
                                continue
                            _time.sleep(1.1)
                        except Exception:
                            continue
                    geo_rows.append((loc_name, lat, lon, count))

                if not geo_rows:
                    continue

                avg_lat = sum(r[1] for r in geo_rows) / len(geo_rows)
                avg_lon = sum(r[2] for r in geo_rows) / len(geo_rows)
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4,
                               tiles='CartoDB positron')
                max_count = max(r[3] for r in geo_rows)
                for loc_name, lat, lon, count in geo_rows:
                    radius = max(5, (count / max_count) * 40)
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        color='#3388ff',
                        fill=True,
                        fill_color='#3388ff',
                        fill_opacity=0.6,
                        popup='{}: {}'.format(loc_name, count),
                        tooltip='{} ({})'.format(loc_name, count)
                    ).add_to(m)

                safe_col = _safe_filename(loc_col)
                map_file = os.path.join(outputDir, '{}_{}_map.html'.format(base_name, safe_col))
                m.save(map_file)
                filesToOpen.append(map_file)
                print(f"  Proportional circle map: {len(geo_rows)} locations geocoded for {loc_col}")

        except ImportError as e:
            print(f"  Note: Folium/geopy not available for map generation: {e}")
        except Exception as e:
            print(f"  WARNING: Proportional circle map: {e}")


def MALLET_heatmap(composition_file, topics_file, outputDir, fig_set={"figure.figsize": (8, 6), "figure.dpi": 300},
                   show_topics=True):
    """
    Uses Seaborn to create a heatmap of topics generated using MALLET topic modeling

    Args:
        composition_file r(str): File name and directory of MALLET topic composition file. Usually NLP-MALLET_Output_Keys.csv.
        topics_file r(str): File name and directory of MALLET topic keys file. Usually NLP-MALLET_Output_Composition.csv.
        fig_set{} (rcParams): Matplotlib figure size parameters. 8in by 6in at 300 DPI by default. Warning: changing dimension values could impact readability of topics.
        show_topics (bool): Controls if topic keys should be displayed under heatmap. True by default. Useful to set as false when using many topics.

    Returns:
        heatmap (object): Seaborn heatmap plot object.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt


    try:
        topics = pd.read_csv(topics_file, encoding='utf-8', on_bad_lines='skip')
    except:
        topics = pd.read_csv(topics_file, encoding="ISO-8859-1", on_bad_lines='skip')
    topics.columns = ["Topic", "Weight", "Keys"]

    try:
        composition = pd.read_csv(composition_file, encoding='utf-8', on_bad_lines='skip')
    except:
        composition = pd.read_csv(composition_file, encoding="ISO-8859-1", on_bad_lines='skip')
    num_topics = len(composition.columns) - 2
    composition.columns = ["Document ID", "Document"] + [f"Topic {i}" for i in range(1, num_topics + 1)]

    composition.drop(["Document ID"], axis=1, inplace=True)
    composition.reset_index(drop=True, inplace=True)

    composition["Document"] = composition["Document"].apply(
        lambda d: os.path.split(d.replace('file:' + os.sep, ''))[1])

    document_titles = composition["Document"]  # Clean hyperlinks function here

    sns.set(rc=fig_set)  # Set figure dimensions and resolution

    heatmap = sns.heatmap(composition.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0),
                          vmin=0, vmax=1,  # Range 0-1
                          annot=True,  # Display values inside heatmap
                          yticklabels=document_titles,  # Document name labels
                          fmt='0.2f',  # Rounding
                          annot_kws={"size": 8})
    plt.suptitle("Topic Composition and Keys", fontsize=18)  # Title

    # Add topics labels to heatmap x-axis
    # if show_topics:
    #     size = plt.gcf().get_size_inches()  # Figure dimensions to align topics under chart
    #     topic_num = 1
    #     for keys in topics["Keys"]:
    #         plt.text(-size[0] * 0.4,  # adjust for left indent
    #                  -size[1] * 0.25 - topic_num * 0.5,  # adjust for vertical position
    #                  f"Topic {topic_num}: {keys}",
    #                  ha="left", va="top", fontsize=8)  # change fontsize
    #         topic_num += 1

    if show_topics:
        size = plt.gcf().get_size_inches()  # Figure dimensions to align topics under chart
        topic_num = 1
        for keys in topics["Keys"]:
            plt.text(min(size) - max(size),  # Left indent
                     max(size) + (topic_num * 0.25),  # 0.25 spacing between topics
                     f"Topic {topic_num}: {keys}",  # Naming topics on x-axis
                     ha="left", va="bottom")  # Align text on left
            topic_num += 1

    outputFilename = os.path.join(outputDir, "MALLET_topics.png")
    plt.savefig(outputFilename, bbox_inches="tight")
    plt.close()
    return outputFilename

# seaborn
# https://seaborn.pydata.org/examples/different_scatter_variables.html