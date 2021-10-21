# written by Rafael Piloto October 2021
# re-written by Roberto Franzosi October 2021
# completed by Austin Cai October 2021

import os
import IO_files_util
import IO_csv_util
import csv
import pprint
from nltk.tokenize import word_tokenize

"""
NGramsCoOccurrences implements the ability to generate NGram and CoOccurrences data
"""


def run(inputDir="relative_path_here",
        outputDir="relative_path_here",
        n_grams_viewer=False,
        CoOcc_Viewer=True,
        search_wordsLists=None,
        dateOption=False,
        datePos=4,
        dateFormat="mm-dd-yyyy",
        itemsDelimiter="_",
        groupingOption="",
        viewer_options_list=[]):

    case_sensitive = False
    normalize = True
    scaleData = False
    lemma = False

    for viewer_option in viewer_options_list:
        if viewer_option == 'Case sensitive':
            case_sensitive = True
        elif viewer_option == "Normalize results":  # not available yet
            normalize = True
        elif viewer_option == "Scale results":   # not available yet
            scaleData = True
        elif viewer_option == "Lemmatize words":  # not available yet
            lemmatize = True

    files = IO_files_util.getFileList('', inputDir, ".txt")  # get all input files
    nFile = len(files)
    if nFile == 0:
        return

    original_search_word = search_wordsLists + ""
    search_word_list = search_wordsLists.split(',')
    for i in range(len(search_word_list)):
        search_word_list[i] = search_word_list[i].lstrip()
    if n_grams_viewer == False:
        ngram_results = None
    else:
        ngram_results = {}  # prepare ngram results
        # preparation
        for word in search_word_list:
            ngram_results[word] = []
    if CoOcc_Viewer == False:
        coOcc_results = None  # prepare co-occurrences results
    else:
        coOcc_results = {}
    docIndex = 1
    coOcc_results_binary = {}
    for file in files:  # iterate over each file
        docIndex += 1
        print("Processing file " + str(docIndex) + "/" + str(nFile) + " " + file)
        coOcc_results_binary[file] = {"Search Word(s)": original_search_word, "CO-Occurrence": "NO", "Document ID": docIndex, "Document": IO_csv_util.undressFilenameForCSVHyperlink(file)}
        collocation = ''
        collocation_found = False
        index = 0
        # extract the date from the file name
        if dateOption:
            date, dateStr = IO_files_util.getDateFromFileName(file, itemsDelimiter, datePos, dateFormat)
            if date == '':
                continue
        else:
            date = ''
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            tokens_ = word_tokenize(docText)
            coOcc_results = {}
            for collocationIndex in range(len(tokens_)):
                if coOcc_results_binary[file]["CO-Occurrence"] == "YES":
                    break
                token = tokens_[collocationIndex]
                token = token.lower()
                if n_grams_viewer:
                    if token in search_word_list:  # add word if in search list
                        ngram_results[token].append([token, date, os.path.join(inputDir, file)])
                # check if generating co-occurrences
                if CoOcc_Viewer:
                    for search_word in search_word_list:
                        search_word = search_word.lower()
                        iterations = search_word.count(' ')
                        split_search_word = search_word.split(' ')
                        # split_search_word=str(split_search_word).
                        length_of_search_list = len(split_search_word)
                        checker = False
                        if iterations > 0:
                            for i in range(length_of_search_list):
                                if i == 0:
                                    if split_search_word[i] == token:
                                        # print("yes")
                                        checker = True
                                else:
                                    if checker and (collocationIndex + i) < len(tokens_):
                                        if split_search_word[i] == tokens_[collocationIndex + i]:
                                            # print("yes")
                                            checker = True
                                        else:
                                            checker = False
                            if checker:
                                coOcc_results[search_word] = 2
                        else:
                            if search_word == token or collocation_found:
                                # print(search_word, 'FOUND!!!!!', file)
                                coOcc_results[search_word] = 1
                    co_occurrence_checker = True
                    for word in search_word_list:
                        if word not in coOcc_results.keys():
                            co_occurrence_checker = False
                            break
                    if co_occurrence_checker:
                        coOcc_results_binary[file]["CO-Occurrence"] = "YES"
                        break
    # pprint.pprint(coOcc_results_binary)
    NgramsFileName, coOccFileName = save(inputDir, outputDir, ngram_results, coOcc_results_binary)
    return NgramsFileName, coOccFileName

"""
    Saves the data passed in the expected format of `NGramsCoOccurrences.run()`
    
    ngrams_results: dict
            The ngram results in the following format: {word : [word, date, file] }
        coOcc_results: dict
            The co-occurrence results in the following format: {combination : [combination, date, file] }
"""


def save(inputDir, outputDir, ngram_results, coOcc_results):
    NgramsFileName=''
    if ngram_results is not None:
        NgramsFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'N-grams')
        # outputFileName='Ngrams'
        with open(NgramsFileName, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["word", "date", "file"])
            # To find frequency, use `len(res)`
            for label, res in ngram_results.items():
                writer.writerows(res)

    coOccFileName = ''
    if coOcc_results is not None:
        coOccFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'Co-Occ')
        # with open(os.path.join(WCOFileName, outputDir), 'w', encoding='utf-8') as f:
        with open(coOccFileName, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Search Word(s)", "CO-Occurrence", "Document ID", "Document"])
            for label, res in coOcc_results.items():
                writer.writerow([res["Search Word(s)"], res["CO-Occurrence"], res["Document ID"], res["Document"]])

    return NgramsFileName, coOccFileName

# Test NGramsCoOccurrences logic
# if __name__ == "__main__":
#     inputDir = "relative_path_here"
#     outputDir = "relative_path_here"
#     dateFormat = "mm-dd-yyyy"
#     datePos = 4
#     wordsLists = []
#     groupingOption = ""
#     itemsDelimiter = "_"
#     scaleData = False
#     lemma = False
#     fullInfo = False
#     considerAsSeparateGroups = True
#     normalize = True
#
#     ng = NGramsCoOccurrences(outputDir, inputDir, dateFormat, datePos, wordsLists, checkCoOccList,
#                  groupingOption, itemsDelimiter, docPCIDCouplesFilePath, scaleData, normalizeByPCID,
#                  lemma, fullInfo, considerAsSeparateGroups, normalize)
#     ngr, cor = ng.run()
#     ng.save(ngr, cor)
