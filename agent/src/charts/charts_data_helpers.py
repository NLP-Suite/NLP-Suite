# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023
import logging
import os
from collections import Counter

import IO_csv_util
import IO_user_interface_util
import pandas as pd

logger = logging.getLogger(__name__)


def build_timed_alert_message(chart_type, withHeader_var, count_var):
    if withHeader_var == 1:
        withHeader_msg = "WITH HEADERS"
    else:
        withHeader_msg = "WITHOUT HEADERS"
    if count_var == 1:
        count_msg = "WITH COUNTS"
    else:
        count_msg = "WITHOUT COUNTS"
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
        for row in data:
            try:
                rowValues = list(row[w] for w in columns_to_be_plotted[i])
                dataRange.append(rowValues)
            except IndexError:
                continue
    dataRange = [dataRange[i : i + len(data)] for i in range(0, len(dataRange), len(data))]
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
# for row in DataCaptured:
# also IO_csv_util.get_csv_field_values(inputfile_name, column_name)


def get_data_to_be_plotted_with_counts(
    headers,
    columns_to_be_plotted,
    specific_column_value_list,
    data_list,
):
    data_to_be_plotted = []

    column_list = []
    column_frequencies = []
    specific_column_value = ""
    if len(data_list) != 0:
        for k in range(len(columns_to_be_plotted)):
            res = []
            if len(specific_column_value_list) > 0:
                specific_column_value = specific_column_value_list[k]
            # get all the values in the selected column
            try:
                #  TODO the datalist is like [['NN','NN'], ...] so the code produces bad results
                #       when multiple series side-by-side (e.g., form and lemma values) need to be plotted
                column_list = [i[1] for i in data_list[k]]
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
                    for _y in range(len(specific_column_value_list)):
                        column_frequencies = [
                            [
                                id_name,
                                "Frequencies of " + str(specific_column_value) + " in Column " + str(column_name),
                            ]
                        ]
            else:
                id_name_num = columns_to_be_plotted[k][0]
                id_name = "column_" + str(id_name_num + 1)
                column_name_num = columns_to_be_plotted[k][1]
                column_name = "column_" + str(column_name_num + 1)
                if len(specific_column_value) == 0:
                    column_frequencies = [[column_name + " values", "Frequencies of " + column_name]]
                else:
                    for _y in range(len(specific_column_value_list)):
                        column_frequencies = [
                            [
                                id_name,
                                "Frequencies of "
                                + str(specific_column_value)
                                + " in Column_"
                                + str(column_name_num + 1),
                            ]
                        ]
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


def get_data_to_be_plotted_NO_counts(inputFilename, withHeader_var, headers, columns_to_be_plotted, data):
    data_to_be_plotted = []
    for gp in columns_to_be_plotted:
        data.iloc[:, gp[1]].replace("N/A", 0)
        data.iloc[:, gp]
        data_to_be_plotted.append(data.iloc[:, gp])
    return data_to_be_plotted


def header_check(inputFile):
    sentenceID_pos = ""
    docCol_pos = ""
    docName_pos = ""
    frequency_pos = []

    if isinstance(inputFile, pd.DataFrame):
        header = list(inputFile.columns)
    else:
        header = IO_csv_util.get_csvfile_headers(inputFile)
    if "Sentence ID" in header:
        sentenceID_pos = header.index("Sentence ID")
    else:
        pass

    if "Document ID" in header:
        docCol_pos = header.index("Document ID")
    else:
        pass

    if "Document" in header:
        docName_pos = header.index("Document")
    else:
        pass

    # Frequenc to capture Frequency and Frequencies
    # str added since the header may contain several instances of the searched item (e.g., Mean score, Median score)
    #   in which case it would not be found
    str_header = str(", ".join(header))
    if "Frequenc" in str_header or "Number of" in str_header or "score" in str_header or "Score" in str_header:
        # the code would break with the wrong header item (e.g., no Frequency in header to get the index
        # We do 2 things here:
        #   1. get the right header value (e.g., Number of words, or Score, instead of Frequency)
        #   2. Loop through the header containing a specific value (e.g., score) and get all its positions (e.g., Mean score, Median score)
        #   frequency_pos needs to be a list [] rather than a string to accommodate for multiple instances
        # https://stackoverflow.com/questions/64127075/how-to-retrieve-partial-matches-from-a-list-of-strings
        result = list(
            filter(
                lambda x: "Frequenc" in x or "Number of" in x or "Score" in x or "score" in x,
                header,
            )
        )
        try:
            for i in range(0, len(result)):
                frequency_pos.append(header.index(result[i]))
        except Exception:
            pass
    else:
        pass
    return sentenceID_pos, docCol_pos, docName_pos, frequency_pos, header


# TODO Samir very slow
def process_sentenceID_record(
    Row_list,
    Row_list_new,
    index,
    start_sentence,
    end_sentence,
    header,
    sentenceID_pos,
    docCol_pos,
    docName_pos,
    frequency_pos,
    save_current,
):
    # TODO temporary to measure process time
    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running Excel process_sentenceID_record at",
        True,
        "",
        True,
        "",
        True,
    )
    # end_sentence is always skipped; the range of integers end at end_sentence – 1
    for i in range(start_sentence, end_sentence, 1):
        temp = [""] * len(header)
        # loop through headers for Sentence ID, Document ID, and Document to insert missing values
        for j in range(len(header)):
            if j == sentenceID_pos:
                # insert Sentence ID
                temp[j] = i
                # when adding a new Sentence ID, insert a frequency value of 0,
                #   in every occurrence of a frequency column, whatever the name may be (Frequency, Frequencies, Number of, Score)
                for k in range(0, len(frequency_pos)):
                    if frequency_pos[k] != "":
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
    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running Excel process_sentenceID_record at",
        True,
        "",
        True,
        startTime,
        True,
    )

    return Row_list_new


# written by Yi Wang
# rewritten by Roberto July 2022


# input can be a csv filename or a dataFrame
# output is a csv file
# TODO Samir very slow
def add_missing_IDs(input, outputFilename):
    from Stanza_functions_util import sent_tokenize_stanza, stanzaPipeLine

    # TODO temporary to measure process time
    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running Excel Add missing IDs at",
        True,
        "",
        True,
        "",
        True,
    )
    if isinstance(input, pd.DataFrame):
        logger.info("YES")
        df = input
    else:
        df = pd.read_csv(input, encoding="utf-8", on_bad_lines="skip")
    # define variables
    start_sentence = 1  # first sentence in loop
    end_sentence = 1  # last sentence in loop
    number_sentences = []
    Row_list_new = []
    sentenceID_pos, docCol_pos, docName_pos, frequency_pos, header = header_check(input)
    Row_list = IO_csv_util.df_to_list(df)
    len(Row_list)
    for index, _row in enumerate(Row_list):
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
            text = open(inputFilename, encoding="utf-8", errors="ignore").read()
            sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            number_sentences.append([inputFilename, len(sentences)])

            # check whether the last sentence for the previous doc was less than number of sentences
            if index == 0:  # first record in df
                Row_list_new = process_sentenceID_record(
                    Row_list,
                    Row_list_new,
                    index,
                    start_sentence,
                    end_sentence,
                    header,
                    sentenceID_pos,
                    docCol_pos,
                    docName_pos,
                    frequency_pos,
                    save_current=True,
                )
            else:  # index>0 all other records
                # select the number of sentences for the right document
                for i in range(len(number_sentences)):
                    # TODO hyperlinks should be removed in file before passing it to add_missing_IDs
                    if (
                        IO_csv_util.undressFilenameForCSVHyperlink(Row_list[index - 1][docName_pos])
                        == number_sentences[i][0]
                    ):
                        n_sentences = number_sentences[i][1]
                if Row_list[index - 1][sentenceID_pos] < n_sentences:
                    start_sentence = Row_list[index - 1][sentenceID_pos] + 1
                    end_sentence = n_sentences + 1
                    # pass index-1 as argument since we are adding sentence IDs to the previous document
                    Row_list_new = process_sentenceID_record(
                        Row_list,
                        Row_list_new,
                        index - 1,
                        start_sentence,
                        end_sentence,
                        header,
                        sentenceID_pos,
                        docCol_pos,
                        docName_pos,
                        frequency_pos,
                        save_current=False,
                    )
                    # do NOT save current; already saved when first processing the record
                # now process the current record
                start_sentence = 1
                end_sentence = Row_list[index][sentenceID_pos]
                Row_list_new = process_sentenceID_record(
                    Row_list,
                    Row_list_new,
                    index,
                    start_sentence,
                    end_sentence,
                    header,
                    sentenceID_pos,
                    docCol_pos,
                    docName_pos,
                    frequency_pos,
                    save_current=True,
                )
        else:  # same document
            # check that current sentence is not just one sentence greater than previous one
            #   in which case start and end are the same
            if Row_list[index][sentenceID_pos] == Row_list[index - 1][sentenceID_pos] + 1:
                start_sentence = Row_list[index][sentenceID_pos]
                end_sentence = Row_list[index][sentenceID_pos]
            else:
                start_sentence = Row_list[index - 1][sentenceID_pos]
                end_sentence = Row_list[index][sentenceID_pos]
            Row_list_new = process_sentenceID_record(
                Row_list,
                Row_list_new,
                index,
                start_sentence,
                end_sentence,
                header,
                sentenceID_pos,
                docCol_pos,
                docName_pos,
                frequency_pos,
                save_current=True,
            )

    df = pd.DataFrame(Row_list_new, columns=header)
    df.sort_values(by=["Document ID", "Sentence ID"], ascending=True, inplace=True)
    df.to_csv(outputFilename, encoding="utf-8", index=False)
    # TODO temporary to measure process time
    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running Excel Add missing IDs at",
        True,
        "",
        True,
        startTime,
        True,
    )
    return outputFilename


# Tony Chen Gu written at April 2022 mortified at May 2022
# edited by Roberto June 2022 for sorting df
# function no longer used since it does not insert sentences in the right document
# use instead add_missing_IDs


def complete_sentence_index(file_path):
    data = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
    if "Sentence ID" not in data:
        head, tail = os.path.split(file_path)
        IO_user_interface_util.timed_alert(
            2000,
            "Wrong csv file",
            "The csv file\n"
            + tail
            + '\n does not contain a "Sentence ID" header. A sentence ID value cannot be added.',
            True,
            "",
            True,
            "",
            False,
        )
        return
    if len(data) == 1:
        return data
    max_sid = max(data["Sentence ID"]) + 1
    sid_list = list(range(1, max_sid))
    df_sid = pd.DataFrame(sid_list, columns=["Sentence ID"])
    # use merge to accelerate the process
    data = data.merge(right=df_sid, how="right", on="Sentence ID")
    data = data.fillna(0)
    data.sort_values(by=["Document ID", "Sentence ID"], ascending=True, inplace=True)
    data.to_csv(file_path, encoding="utf-8", index=False)
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
