# written by Rafael Piloto October 2021
# re-written by Roberto Franzosi October 2021
# completed by Austin Cai October 2021

import os
import tkinter.messagebox as mb
import pandas as pd
import csv
import numpy as np
import pprint
# from Stanza_functions_util import word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza
import stanza

import GUI_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import constants_util

"""
NGramsCoOccurrences implements the ability to generate NGram and CoOccurrences data
"""

def processSearchWords(inputStr):
    word_list = []
    if inputStr.find("\"") == -1:
        # no quotation mark
        word_list += inputStr.split(",")
    else:
        # contains quotation mark
        curWord = ""
        i = 0
        while i < len(inputStr):
            if inputStr[i] == " ":
                if curWord != "":
                    word_list.append(curWord)
                curWord = ""
            elif inputStr[i] == "\"":
                endIndex = inputStr.index("\"", i + 1)
                word_list.append(inputStr[i + 1: endIndex])
                i = endIndex
            else:
                curWord = curWord + inputStr[i]
            i += 1
    return word_list

def process_date(search_wordsLists, temporal_aggregation):
    # it will iterate through i = 0, 1, 2, …., n-1
    # this assumes the data are in this format: temporal_aggregation, frequency of search-word_1, frequency of search-word_2, ...
    i = 0
    j = 0
    columns_to_be_plotted_yAxis=[]
    ngram_list = processSearchWords(search_wordsLists)
    ngram_list = ['-checkNGrams'] + ngram_list
    while i < (len(ngram_list) - 1):
        if temporal_aggregation == "quarter" or temporal_aggregation == "month":
            if i == 0:
                j = j + 3
            columns_to_be_plotted_yAxis.append([0, j])
        else:
            columns_to_be_plotted_yAxis.append([0, i + 1])
        i += 1
        j += 1
    return columns_to_be_plotted_yAxis

def run(inputDir="relative_path_here",
        outputDir="relative_path_here",
        configFileName='',
        createCharts=True, chartPackage='Excel',
        n_grams_viewer=False,
        CoOcc_Viewer=True,
        search_wordsLists=None,
        language_list=['English'],
        useLemma=False,
        dateOption=False,
        temporal_aggregation='year',
        number_of_years=0,
        dateFormat="mm-dd-yyyy",
        itemsDelimiter="_",
        datePos=2,
        viewer_options_list=[]):

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'N-Grams start',
                                       'Started running Words/Characters N-Grams VIEWER at',
                                       True, '', True, '', False)

    from Stanza_functions_util import word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

    if search_wordsLists is None:
        search_wordsLists = []
    checkCoOccList = False

    lang_dict = dict(constants_util.languages)
    lang = ''
    lang_list = []
    for k,v in lang_dict.items():
        if v == language_list[0]:
            lang = k
            lang_list.append(lang)
            break
    try:
        if useLemma:
            stanzaPipeLine = stanza.Pipeline(lang=lang, processors='tokenize, lemma')
        else:
            stanzaPipeLine = stanza.Pipeline(lang=lang, processors='tokenize')
    except:
        mb.showwarning(title='Warning', message='You must enter an integer value. The value ' + str(result[0]) + ' is not an integer.')
        return
    case_sensitive = False
    normalize = False
    scaleData = False
    useLemma = False
    fullInfo = False
    # print(str(viewer_options_list))
    if 'sensitive' in str(viewer_options_list):
        case_sensitive = True
    if 'insensitive' in str(viewer_options_list):
        case_sensitive = False
    if 'Normalize' in str(viewer_options_list):
        normalize = True
    if 'Scale' in str(viewer_options_list):
        scaleData = True
    if 'Lemmatize' in str(viewer_options_list):
        useLemma = True


    ################################## OPTIONS NEEDED TO BE ADDED TO GUI #################################################
    byNumberOfYears = 0
    byYear = False
    byQuarter = False
    byMonth = False
    if temporal_aggregation=='group of years':
        byNumberOfYears = number_of_years  # number of years in one aggregated chunk
        byYear = True  # set to True if want to aggregate by years
        aggregateBy = 'year'
    elif temporal_aggregation=='year':
        byYear = True  # set to True if want to aggregate by years
        aggregateBy = 'year'
    elif temporal_aggregation=='quarter':
        byQuarter = True  # set to True if want to aggregate by years
        aggregateBy = 'quarter'
    elif temporal_aggregation=='month':
        byMonth = True  # set to True if want to aggregate by years
        aggregateBy = 'month'
    files = IO_files_util.getFileList('', inputDir, ".txt", silent=False, configFileName=configFileName)  # get all input files
    original_search_word = search_wordsLists + ""
    search_word_list = search_wordsLists.split(',')
    ngram_results = {}
    for i in range(len(search_word_list)):
        if not case_sensitive:
            search_word_list[i] = search_word_list[i].lstrip().lower()
        else:
            search_word_list[i] = search_word_list[i].lstrip()

    if (n_grams_viewer or CoOcc_Viewer) and byYear and dateOption:
        yearList = []
        docIndex = 1
        print("Create file list -------------------------------------------------------------\n")
        for file in files:  # iterate over each file
            head, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(len(files)) + ' ' + tail)
            docIndex += 1
            date, dateStr, month, day, year = IO_files_util.getDateFromFileName(file, dateFormat, itemsDelimiter, datePos)
            yearList.append(year)
        yearList = sorted(np.unique(yearList))
        for word in search_word_list:
            ngram_results[word] = {}
            for y in yearList:
                ngram_results[word][y] = {"Search Word(s)": word,
                                          "Frequency": 0}

        # pprint.pprint(ngram_results)
        # print()
        docIndex = 1
        print("\nProcess files for YEAR date option  -------------------------------------------------------------\n")
        for file in files:  # iterate over each file
            head, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(len(files)) + ' ' + tail)
            docIndex += 1
            # extract the date from the file name
            date, dateStr, month, day, year = IO_files_util.getDateFromFileName(file, dateFormat, itemsDelimiter, datePos)
            if date == '':
                continue  # TODO: getDate warns user is this file has a bad date
            year = int(year)
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            if not case_sensitive:
                docText = docText.lower()
            tokens_ = word_tokenize_stanza(stanzaPipeLine(docText))
            for collocationIndex in range(len(tokens_)):
                token = tokens_[collocationIndex]
                for search_word in search_word_list:
                    iterations = search_word.count(' ')
                    split_search_word = search_word.split(' ')
                    # split_search_word=str(split_search_word).
                    length_of_search_list = len(split_search_word)
                    checker = False
                    if iterations > 0:
                        for i in range(length_of_search_list):
                            if i == 0:
                                if split_search_word[i] == token:
                                    checker = True
                            else:
                                if checker and (collocationIndex + i) < len(tokens_):
                                    if split_search_word[i] == tokens_[collocationIndex + i]:
                                        checker = True
                                    else:
                                        checker = False
                        if checker:
                            ngram_results[search_word][year]["Frequency"] += 1
                    else:
                        if search_word == token:
                            ngram_results[search_word][year]["Frequency"] += 1

# aggregate by groups of years

        if byNumberOfYears > 1:
            # pprint.pprint(ngram_results)
            curYear = yearList[0]
            newYear = curYear + byNumberOfYears - 1
            newYearStringList = []
            newYearIntList = []
            while curYear < yearList[-1]:
                yearChunk = str(curYear) + "-" + str(newYear)
                newYearStringList.append(yearChunk)
                newYearIntList.append((curYear, newYear))
                curYear = newYear + 1
                newYear = curYear + byNumberOfYears - 1
            aggregated_ngram_results = {}
            for word in search_word_list:
                aggregated_ngram_results[word] = {}
                for y in newYearStringList:
                    aggregated_ngram_results[word][y] = {"Search Word(s)": word,
                                                         "Frequency": 0}
                for year in yearList:
                    for i in range(len(newYearIntList)):
                        if newYearIntList[i][0] <= year <= newYearIntList[i][1]:
                            aggregated_ngram_results[word][newYearStringList[i]]["Frequency"] += \
                                ngram_results[word][year]["Frequency"]
            ngram_results = aggregated_ngram_results
            # pprint.pprint(aggregated_ngram_results)

    if (n_grams_viewer or CoOcc_Viewer) and dateOption and (byMonth or byQuarter):
        monthList = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        yearList = []
        docIndex = 1
        print("\nProcess files for YEAR date option  -------------------------------------------------------------\n")
        for file in files:  # iterate over each file
            head, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(len(files)) + ' ' + tail)
            docIndex += 1
            date, dateStr, month, day, year = IO_files_util.getDateFromFileName(file, dateFormat, itemsDelimiter, datePos)
            yearList.append(year)
        yearList = sorted(np.unique(yearList))

        for word in search_word_list:
            ngram_results[word] = {}
            for y in yearList:
                ngram_results[word][str(y)] = {}
                for m in monthList:
                    ngram_results[word][str(y)][m] = {"Search Word(s)": word,
                                                      "Frequency": 0}
        # pprint.pprint(ngram_results)
        # print()
        docIndex = 1
        print("\nProcess files for date option -------------------------------------------------------------\n")
        for file in files:  # iterate over each file
            head, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(len(files)) + ' ' + tail)
            docIndex += 1
            # extract the date from the file name
            date, dateStr, month, day, year = IO_files_util.getDateFromFileName(file, dateFormat, itemsDelimiter, datePos)
            if date == '':
                continue  # TODO: getDate warns user is this file has a bad date
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            if not case_sensitive:
                docText = docText.lower()
            tokens_ = word_tokenize_stanza(stanzaPipeLine(docText))
            for collocationIndex in range(len(tokens_)):
                token = tokens_[collocationIndex]
                for search_word in search_word_list:
                    iterations = search_word.count(' ')
                    split_search_word = search_word.split(' ')
                    # split_search_word=str(split_search_word).
                    length_of_search_list = len(split_search_word)
                    checker = False
                    if iterations > 0:
                        for i in range(length_of_search_list):
                            if i == 0:
                                if "Chinese" in language_list:
                                    if split_search_word[i] in token:
                                        checker = True
                                else:
                                    if split_search_word[i] == token:
                                        checker = True
                            else:
                                if checker and (collocationIndex + i) < len(tokens_):
                                    if split_search_word[i] == tokens_[collocationIndex + i]:
                                        checker = True
                                    else:
                                        checker = False
                        if checker:
                            ngram_results[search_word][str(year)][str(month).zfill(2)]["Frequency"] += 1
                    else:
                        if "Chinese" in language_list:
                            if search_word in token:
                                ngram_results[search_word][str(year)][str(month).zfill(2)]["Frequency"] += 1
                        else:
                            if search_word == token:
                                ngram_results[search_word][str(year)][str(month).zfill(2)]["Frequency"] += 1

# aggregate by quarter
        if byQuarter:
            quarter_ngram_results = {}
            for word, yearDict in ngram_results.items():
                quarter_ngram_results[word] = {}
                for year, monthDict in yearDict.items():
                    q1Sum, q2Sum, q3Sum, q4Sum = 0, 0, 0, 0
                    quarter_ngram_results[word][year] = {}
                    for month, freqDict in monthDict.items():
                        if 1 <= int(month) <= 3:
                            q1Sum += freqDict["Frequency"]
                        if 4 <= int(month) <= 6:
                            q2Sum += freqDict["Frequency"]
                        if 7 <= int(month) <= 9:
                            q3Sum += freqDict["Frequency"]
                        if 10 <= int(month) <= 12:
                            q4Sum += freqDict["Frequency"]
                    quarter_ngram_results[word][year]["quarter 1"] = {"Search Word(s)": word,
                                                                      "Frequency": q1Sum}
                    quarter_ngram_results[word][year]["quarter 2"] = {"Search Word(s)": word,
                                                                      "Frequency": q2Sum}
                    quarter_ngram_results[word][year]["quarter 3"] = {"Search Word(s)": word,
                                                                      "Frequency": q3Sum}
                    quarter_ngram_results[word][year]["quarter 4"] = {"Search Word(s)": word,
                                                                      "Frequency": q4Sum}
            # pprint.pprint(quarter_ngram_results)
            ngram_results = quarter_ngram_results
    if not CoOcc_Viewer:
        # prepare co-occurrences results
        coOcc_results_binary = {}
    else:
        docIndex = 1
        coOcc_results_binary = {}
        docIndex = 1
        print("\nProcess files for co-occurrence option -------------------------------------------------------------\n")
        for file in files:  # iterate over each file
            head, tail = os.path.split(file)
            print("Processing file " + str(docIndex) + "/" + str(len(files)) + ' ' + tail)
            coOcc_results_binary[file] = {"Search Word(s)": original_search_word, "Co-Occurrence": "NO",
                                          "Document ID": docIndex,
                                          "Document": IO_csv_util.undressFilenameForCSVHyperlink(file)}
            docIndex += 1
            collocation = ''
            collocation_found = False
            index = 0
            # extract the date from the file name
            date = ''
            if dateOption:
                date, dateStr, month, day, year = IO_files_util.getDateFromFileName(file, dateFormat, itemsDelimiter, datePos)
                if date == '':
                    continue  # TODO: getDate warns user is this file has a bad date
            # else:
            # date = ''
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            if not case_sensitive:
                docText = docText.lower()
            tokens_ = word_tokenize_stanza(stanzaPipeLine(docText))
            coOcc_results = {}
            for collocationIndex in range(len(tokens_)):
                if coOcc_results_binary[file]["Co-Occurrence"] == "YES":
                    break
                token = tokens_[collocationIndex]
                if CoOcc_Viewer:
                    for search_word in search_word_list:
                        iterations = search_word.count(' ')
                        split_search_word = search_word.split(' ')
                        # split_search_word=str(split_search_word).
                        length_of_search_list = len(split_search_word)
                        checker = False
                        if iterations > 0:
                            for i in range(length_of_search_list):
                                if i == 0:
                                    if "Chinese" in language_list:
                                        if split_search_word[i] in token:
                                            checker = True
                                    else:
                                        if split_search_word[i] == token:
                                            checker = True
                                else:
                                    if checker and (collocationIndex + i) < len(tokens_):
                                        if split_search_word[i] == tokens_[collocationIndex + i]:
                                            checker = True
                                        else:
                                            checker = False
                            if checker:
                                coOcc_results[search_word] = 2
                        else:
                            if "Chinese" in language_list:
                                if search_word in token:
                                    coOcc_results[search_word] = 1
                            else:
                                if search_word == token:
                                    coOcc_results[search_word] = 1
                    co_occurrence_checker = True
                    for word in search_word_list:
                        if word not in list(coOcc_results.keys()):
                            co_occurrence_checker = False
                            break
                    if co_occurrence_checker:
                        coOcc_results_binary[file]["Co-Occurrence"] = "YES"
                        break

    NgramsFileName=''
    coOccFileName=''

    if n_grams_viewer:
        if 'group' in temporal_aggregation:
            label='group_'+str(byNumberOfYears)
        else:
            label=temporal_aggregation
        NgramsFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv',
                                                                 'N-grams_' + label)

    if CoOcc_Viewer:
        coOccFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'Co-Occ')

# save the N-grams/Co-occurrence output file

    # pprint.pprint(coOcc_results_binary)
    NgramsFileName, coOccFileName, temp_fileName = save(NgramsFileName, coOccFileName, ngram_results, coOcc_results_binary, aggregateBy, temporal_aggregation)

    filesToOpen = []

# plot Ngrams --------------------------------------------------------------------------

    if n_grams_viewer:
        import charts_util
        if createCharts == True and NgramsFileName != '':
            xlsxFilename = NgramsFileName
            filesToOpen.append(NgramsFileName)
            xAxis = temporal_aggregation
            chartTitle = 'N-Grams Viewer'
            columns_to_be_plotted_xAxis = []
            columns_to_be_plotted_yAxis = []
            # it will iterate through i = 0, 1, 2, …., n-1
            # this assumes the data are in this format: temporal_aggregation, frequency of search-word_1, frequency of search-word_2, ...
            i = 0
            j = 0
            columns_to_be_plotted_yAxis = process_date(search_wordsLists, temporal_aggregation)
            hover_label = []
            chart_outputFilename = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                                       'n-grams_viewer',
                                                       chartPackage=chartPackage,
                                                       chart_type_list=["line"],
                                                       chart_title=chartTitle, column_xAxis_label_var=xAxis,
                                                       hover_info_column_list=hover_label)
            if chart_outputFilename != None:
                filesToOpen.append(chart_outputFilename)  # chart_outputFilename is a string, must use append
                # if len(chart_outputFilename) > 0:
                #     filesToOpen.extend(chart_outputFilename)

# plot co-occurrences -----------------------------------------------------------------------------

    if CoOcc_Viewer:
        if createCharts and coOccFileName != '':
            import charts_util
            xlsxFilename = coOccFileName
            filesToOpen.append(coOccFileName)
            if temp_fileName!='':
                filesToOpen.append(temp_fileName)
            chartTitle = 'Co-Occurrences Viewer: ' + search_wordsLists
            if dateOption == 0:
                xAxis = 'Document'
            else:
                xAxis = temporal_aggregation
            hover_label = []
            columns_to_be_plotted_byDoc = [[1, 2, 0]]
            freq_file = aggregate_YES_NO(xlsxFilename, ["Co-Occurrence"])
            chart_outputFilename = charts_util.run_all(columns_to_be_plotted_byDoc, freq_file, outputDir,
                                           outputFileLabel='byDoc_',
                                           # outputFileNameType + 'byDoc', #outputFileLabel,
                                           chartPackage=chartPackage,
                                           chart_type_list=['bar'],
                                           chart_title=chartTitle + ' by Document',
                                           column_xAxis_label_var='',
                                           column_yAxis_label_var='Frequency',
                                           hover_info_column_list=hover_label,
                                           # count_var is set in the calling function
                                           #     0 for numeric fields;
                                           #     1 for non-numeric fields
                                           count_var=0,
                                           remove_hyperlinks=True)
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.append(chart_outputFilename)

            chartTitle = 'Co-occurrence Viewer'
            columns_to_be_plotted_yAxis = process_date(search_wordsLists, temporal_aggregation)
            hover_label = []
            chartTitle = 'Frequency Distribution of Co-Occurring Words'
            chart_outputFilename = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                                       'co-occ_viewer',
                                                       chartPackage=chartPackage,
                                                       chart_type_list=["bar"],
                                                       count_var=1,
                                                       chart_title=chartTitle,
                                                       column_xAxis_label_var='Word list: ' + search_wordsLists,
                                                       hover_info_column_list=hover_label)
            if chart_outputFilename != None:
                filesToOpen.append(chart_outputFilename)  # chart_outputFilename is a string, must use append

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running Words/Characters N-Grams VIEWER at', True, '', True, startTime, False)


    return filesToOpen

"""
    Instead of direct aggregation by document, take YES as 1 and NO as 0, and then sum it by document.
"""
def aggregate_YES_NO(inputFilename, column):
    cols = ["Document ID", "Document"] + column
    df = pd.read_csv(inputFilename)
    df = df.replace('YES', 1)
    df = df.replace('NO', 0)
    # create a new data frame with Document ID, Document, and the sum of the column
    df = df[cols].groupby(["Document ID", "Document"]).sum()
    # rename 'column' to Frequency
    df = df.rename(columns={column[0]: "Frequency"})
    df = df.reset_index()
    # save the new data frame to a new file, parse the inputfilename and add _frequency to the end
    newFilename = inputFilename.split(".")[0] + "_frequency.csv"
    # save the new data frame to a new file
    df.to_csv(newFilename, index=False)
    _, newFilename = IO_csv_util.remove_hyperlinks(newFilename)
    return newFilename



"""
    Saves the data passed in the expected format of `NGramsCoOccurrences.run()`
    
    ngrams_results: dict
            The ngram results in the following format: {word : [word, date, file] }
        coOcc_results: dict
            The co-occurrence results in the following format: {combination : [combination, date, file] }
"""

def save(NgramsFileName, coOccFileName, ngram_results, coOcc_results, aggregateBy, temporal_aggregation):
    temp_fileName = ''
    if len(ngram_results)>0:
        dfList = []  # create a list of dataframes: one df for one search word
        if aggregateBy == 'year':
            for word, yearDict in ngram_results.items():
                df = pd.DataFrame(columns=[word, temporal_aggregation])
                for year, freqDict in yearDict.items():
                    df = df.append({word: freqDict["Frequency"], temporal_aggregation: year}, ignore_index=True)
                dfList.append(df)
            newdfCur = dfList[0].copy()  # let newdfCur be the first df in the dfList
            newdf = newdfCur.copy()
            for i in range(1, len(dfList)):  # one by one join next search word's dataframe with the current dataframe
                newdfNext = dfList[i].copy()  # get the next dataframe
                newdf = newdfCur.merge(newdfNext, on=temporal_aggregation, how="left")  # join on year
                newdfCur = newdf.copy()

            # these 3 lines will move the 'year' column to position 0, which is the left most position
            # inserting headers
            newdf.insert(0, 'year_temp', newdf[temporal_aggregation])
            newdf.drop(temporal_aggregation, axis=1, inplace=True)
            newdf.rename(columns={'year_temp': temporal_aggregation}, inplace=True)
        else:
            # aggregating by quarter or month
            for word, yearDict in ngram_results.items():
                df = pd.DataFrame(columns=[word, 'year', temporal_aggregation, "year-" + temporal_aggregation])
                for year, monthDict in yearDict.items():
                    for month, freqDict in monthDict.items():
                        if temporal_aggregation == 'quarter':
                            df = df.append({word: freqDict["Frequency"], "year": year, temporal_aggregation: month, "year-" + temporal_aggregation: year + "-Q" + month[-1]}, ignore_index=True)
                        else:
                            df = df.append({word: freqDict["Frequency"], "year": year, temporal_aggregation: month, "year-" + temporal_aggregation: year + "-" + month}, ignore_index=True)
                dfList.append(df)
            newdfCur = dfList[0].copy()
            newdf = newdfCur.copy()
            for i in range(1, len(dfList)):
                newdfNext = dfList[i].copy()
                newdf = newdfCur.merge(newdfNext, on=['year', temporal_aggregation, "year-" + temporal_aggregation],
                                       how="left")
                newdfCur = newdf.copy()
            # these 9 lines will move the 'year', 'month' or 'quarter', and 'year-month' column to the left most position
            newdf.insert(0, 'month_temp', newdf[temporal_aggregation])
            newdf.insert(0, 'year_temp', newdf['year'])
            newdf.insert(0, 'yearMonth_temp', newdf["year-" + temporal_aggregation])
            newdf.drop(temporal_aggregation, axis=1, inplace=True)
            newdf.drop('year', axis=1, inplace=True)
            newdf.drop("year-" + temporal_aggregation, axis=1, inplace=True)
            newdf.rename(columns={'month_temp': temporal_aggregation}, inplace=True)
            newdf.rename(columns={'year_temp': 'year'}, inplace=True)
            newdf.rename(columns={'yearMonth_temp': 'year-' + temporal_aggregation}, inplace=True)

        if coOccFileName!='':
            temp_fileName=coOccFileName[:-4]+'_1.csv'
            newdf.to_csv(temp_fileName, encoding='utf-8', index=False)
        else:
            newdf.to_csv(NgramsFileName, encoding='utf-8', index=False)
    if len(coOcc_results)>0:
        # with open(os.path.join(WCOFileName, outputDir), 'w', encoding='utf-8') as f:
        with open(coOccFileName, 'w', newline='', encoding='utf-8', errors='ignore') as f:
            writer = csv.writer(f)
            writer.writerow(["Search Word(s)", "Co-Occurrence", "Document ID", "Document"])
            for label, res in coOcc_results.items():
                writer.writerow([res["Search Word(s)"], res["Co-Occurrence"], res["Document ID"],
                                 IO_csv_util.dressFilenameForCSVHyperlink(res["Document"])])

    return NgramsFileName, coOccFileName, temp_fileName
