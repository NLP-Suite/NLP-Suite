import os
import re
import IO_files_util
import csv

from nltk.tokenize import sent_tokenize, word_tokenize

"""
NGramsCoOccurrences implements the ability to generate NGram and CoOccurrences data
"""
class NGramsCoOccurrences():
    outputFileName = "N-Grams_CoOccurrences_Statistics.csv";
    fileToPlotName = "Searched_N-Grams.csv";
    WCOFileName = "Searched_CoOccurrences.csv";
    docPCIDCouplesFilePath = "";
    scaleData = False;
    normalizeByPCID = False;
    lemma = False;
    fullInfo = False;
    considerAsSeparateGroups = True;
    normalize = True;

    """
        Creates an NGramsCoOccurrences class which can be used to generate the queried data and/or save it
        
        outputDir: str
            The folder in which to save the output data to
        inputDir: str
            The input folder in which to find the input data
        dateFormat: str
            The format to extract the date from the file name
        datePos: str
            The position in which the date can be extracted split by the itemsDelimiter
        wordsLists: list
            The input list to generate NGrams or CoOccurrences
        checkCoOccList: bool
            Should we check for co-occurrences
        groupingOption: bool
            TODO: Implement this
        itemsDelimiter: str
            The delimiter for file names used to extract the date
        docPCIDCouplesFilePath: str
            TODO: Implement this
        scaleData: bool
            TODO: Implement this
        normalizeByPCID: bool
            TODO: Implement this
        lemma: bool
            TODO: Implement this
        fullInfo: bool
            TODO: Implement this
        considerAsSeparateGroups: bool
            TODO: Implement this
        normalize: bool
            TODO: Implement this

        Finds all NGrams and/or CoOccurrences using the specified data at the time of construction
        
        Returns:
            ngrams_results: dict
                The ngram results in the following format: {word : [word, date, file] }
            coOcc_results: dict
                The co-occurrence results in the following format: {combination : [combination, date, file] }
                TODO: support multi-co-occurrence combinations; only 2 word combinations supported
    """

def run(inputDir = "relative_path_here",
    outputDir = "relative_path_here",
    n_grams_viewer = False,
    CoOcc_Viewer = True,
    search_wordsLists = [],
    dateOption = False,
    datePos = 4,
    dateFormat = "mm-dd-yyyy",
    itemsDelimiter = "_",
    groupingOption = "",
    # docPCIDCouplesFilePath = "",
    scaleData = False,
    # normalizeByPCID = False,
    lemma = False,
    fullInfo = False,
    # considerAsSeparateGroups = True,
    normalize = True):

    checkCoOccList = False

    files = IO_files_util.getFileList('', inputDir, ".txt")  # get all input files
    search_word_list = search_wordsLists.split(',')

    # for word in search_wordsLists:
    #     search_word_list.append(re.split(","))
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

    for file in files:  # iterate over each file
        docIndex = 0
        collocation = ''
        collocation_found = False
        index = 0
        # extract the date from the file name
        if dateOption:
            date, dateStr = IO_files_util.getDateFromFileName(file, itemsDelimiter, datePos, dateFormat)
            if date == '':
                continue # TODO: Warn user this file has a bad date
        else:
            date=''
            # read the file
            # with open(os.path.join(inputDir, file), 'r') as f:
            #     try:
            #         lines = f.readlines() # read input
            #     except:
            #         continue
            #
            f = open(file, "r", encoding='utf-8', errors='ignore')
            docText = f.read()
            f.close()
            # sentences_ = sent_tokenize(docText)#the list of sentences in corpus
            tokens_ = word_tokenize(docText)

            # for sent in sentences_:
            #     tokens_ = word_tokenize(sent)
            for token in tokens_:
                token=token.lower()
                if token=='united':
                    print('@')
                if token=='states':
                    print('@')
                if n_grams_viewer:
                    if token in search_word_list:  # add word if in search list
                        ngram_results[token].append([token, date, os.path.join(inputDir, file)])
                # check if generating co-occurrences
                if CoOcc_Viewer:
                    for search_word in search_word_list:
                        # if coOcc_results[search_word] is None:  # instantiate empty list if not yet seen
                        #     coOcc_results[search_word] = []
                        search_word = search_word.lower()
                        iterations=search_word.count(' ')
                        split_search_word=search_word.split(' ')
                        # split_search_word=str(split_search_word).
                        if iterations>0:
                            if search_word == token:
                                if collocation=='':
                                    collocation=token
                                else:
                                    collocation = collocation + ' ' + token
                                index += 1
                                if index<=iterations:
                                    break
                                else:
                                    collocation_found = True
                        if search_word == token or collocation_found:
                            print(search_word, 'FOUND!!!!!',file)
                            collocation=''
                            collocation_found=False
                            index=0
                            docIndex += 1
                            coOcc_results[search_word].append(
                                     [search_word, docIndex, date, file])
    if CoOcc_Viewer:
        outputFilename=save(inputDir, outputDir, ngram_results, coOcc_results)
    else:
        outputFilename = ''
    return outputFilename # ngram_results, coOcc_results  # return results

"""
    Saves the data passed in the expected format of `NGramsCoOccurrences.run()`
    
    ngrams_results: dict
            The ngram results in the following format: {word : [word, date, file] }
        coOcc_results: dict
            The co-occurrence results in the following format: {combination : [combination, date, file] }
"""
def save(inputDir, outputDir, ngram_results, coOcc_results):
    if coOcc_results is not None:
        WCOFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'Co-Occ')
        # with open(os.path.join(WCOFileName, outputDir), 'w', encoding='utf-8') as f:
        with open(WCOFileName, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["combination", "date", "file"])
            for label, res in coOcc_results.items():
                writer.writerows(res)

    if ngram_results is not None:
        outputFileName = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'N-grams')
        # outputFileName='Ngrams'
        with open(outputFileName, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["word", "date", "file"])
            # To find frequency, use `len(res)`
            for label, res in ngram_results.items():
                writer.writerows(res)
    return

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
