# written by Rafael Piloto October 2021
# re-written by Roberto Franzosi October 2021
# completed by Austin Cai October 2021

import os
import IO_files_util
import IO_csv_util
import csv
# import pprint
from nltk.tokenize import sent_tokenize, word_tokenize

"""
NGramsCoOccurrences implements the ability to generate NGram and CoOccurrences data
"""


def run(inputDir="relative_path_here",
        outputDir="relative_path_here",
        n_grams_viewer=False,
        CoOcc_Viewer=True,
        search_wordsLists=None,
        dateOption=False,
        datePos=2,
        dateFormat="mm-dd-yyyy",
        itemsDelimiter="_",
        temporalAggregation="",
        viewer_options_list=[]):

    if search_wordsLists is None:
        search_wordsLists = []
    checkCoOccList = False

    case_sensitive = False
    normalize=False
    scaleData=False
    useLemma=False
    fullInfo=False
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


    files = IO_files_util.getFileList('', inputDir, ".txt")  # get all input files
    original_search_word = search_wordsLists + ""
    search_word_list = search_wordsLists.split(',')

    for i in range(len(search_word_list)):
        if not case_sensitive:
            search_word_list[i] = search_word_list[i].lstrip().lower()
        else:
            search_word_list[i] = search_word_list[i].lstrip()

    if not n_grams_viewer:
        ngram_results = None
    else:
        ngram_results = {}  # prepare ngram results
        # preparation
        for word in search_word_list:
            ngram_results[word] = []
    if not CoOcc_Viewer:
        coOcc_results = None  # prepare co-occurrences results
    else:
        coOcc_results = {}
    docIndex = 1
    coOcc_results_binary = {}
    for file in files:  # iterate over each file
        coOcc_results_binary[file] = {"Search Word(s)": original_search_word, "CO-Occurrence": "NO",
                                      "Document ID": docIndex,
                                      "Document": IO_csv_util.undressFilenameForCSVHyperlink(file)}
        docIndex += 1
        collocation = ''
        collocation_found = False
        index = 0
        # extract the date from the file name
        if dateOption:
            date, dateStr = IO_files_util.getDateFromFileName(file, itemsDelimiter, datePos, dateFormat)
            if date == '':
                continue  # TODO: Warn user this file has a bad date; done in getDate
        else:
            date = ''
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            if not case_sensitive:
                docText = docText.lower()
            tokens_ = word_tokenize(docText)
            coOcc_results = {}
            for collocationIndex in range(len(tokens_)):
                if coOcc_results_binary[file]["CO-Occurrence"] == "YES":
                    break
                token = tokens_[collocationIndex]
                if n_grams_viewer:
                    if token in search_word_list:  # add word if in search list
                        ngram_results[token].append([token, date, os.path.join(inputDir, file)])
                # check if generating co-occurrences
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
                            if search_word == token:
                                # print(search_word, 'FOUND!!!!!', file)
                                coOcc_results[search_word] = 1
                    co_occurrence_checker = True
                    for word in search_word_list:
                        if word not in list(coOcc_results.keys()):
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
                writer.writerow([res["Search Word(s)"], res["CO-Occurrence"], res["Document ID"], IO_csv_util.dressFilenameForCSVHyperlink(res["Document"])])

    return NgramsFileName, coOccFileName

# Test NGramsCoOccurrences logic
# if __name__ == "__main__":
#     inputDir = "relative_path_here"
#     outputDir = "relative_path_here"
#     dateFormat = "mm-dd-yyyy"
#     datePos = 4
#     wordsLists = []
#     checkCoOccList = False
#     groupingOption = ""
#     itemsDelimiter = "_"
#     docPCIDCouplesFilePath = ""
#     scaleData = False
#     normalizeByPCID = False
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
