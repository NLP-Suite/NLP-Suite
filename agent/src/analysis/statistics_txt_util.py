# Written by Roberto Franzosi November 2019
# Edited by Josh Karol
import collections
import logging
import os
import re
import string
from collections import Counter

import IO_libraries_util

logger = logging.getLogger(__name__)
import stanza
from nltk.stem.porter import PorterStemmer

# Docker Directories
STANZA_RESOURCES_DIR = os.environ.get(
    "STANZA_RESOURCES_DIR", "/root/stanza_resources"
)  # second argument is a fall back
EN_MODEL_PATH = os.path.join(STANZA_RESOURCES_DIR, "en")
NLTK_DATA_DIR = os.environ.get("NLTK_DATA", "/root/nltk_data")

try:
    os.makedirs(STANZA_RESOURCES_DIR, exist_ok=False)

except Exception:
    logger.info("Stanza directory already exists")


if not os.path.exists(EN_MODEL_PATH):
    try:
        logger.info("Stanza English models not found. Downloading...")
        stanza.download("en", model_dir=STANZA_RESOURCES_DIR)
        logger.info("Download complete!")
    except Exception:
        # Handle no internet / failed download````
        import IO_internet_util

        IO_internet_util.check_internet_availability_warning("statistics_txt_util.py (stanza.download('en'))")
else:
    logger.info("English model")


try:
    os.makedirs(NLTK_DATA_DIR, exist_ok=False)

except Exception:
    logger.info("NLTK Directory already exists")


#

# Sentence Complexity
import csv
from itertools import groupby

import nltk
import pandas as pd
import sentence_complexity_node_util as Node
import tree
from nltk.draw import TreeView
from nltk.tree import Tree

# For objectivity/subjectivity

# whether stopwordst were already downloaded can be tested, see stackoverflow
#   https://stackoverflow.com/questions/23704510/how-do-i-test-whether-an-nltk-resource-is-already-installed-on-the-machine-runni
#   see also caveats

# check stopwords
# check punkt
IO_libraries_util.import_nltk_resource("tokenizers/punkt", "punkt")

import charts_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import reminders_util
import statistics_csv_util
import textstat
from model_cache import get_spacy_model, get_stanza_pipeline
from nltk.corpus import wordnet

# https://github.com/nltk/nltk/wiki/Frequently-Asked-Questions-(Stackoverflow-Edition)
# to compute bigrams, 3-grams, ...


# https://stackoverflow.com/questions/24347029/python-nltk-bigrams-trigrams-fourgrams
# def compute_word_ngrams(inputFilename,outputFilename):
#     for grams in grams2 :
#     for grams in grams3 :
#     for grams in grams4 :

# returns a frequency distribution of words in text,
#    in the format {"chapman's": 1, 'carried': 1, 'hinesville': 1, 'broke': 1, 'an': 3,...


def get_wordnet_pos(word):  # from https://www.machinelearningplus.com/nlp/lemmatization-examples-python/
    # https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    # assign pos value to one word
    # sometimes the accuracy will be affected: for example, lemmatization of leaves can be both verb(leave) and noun(leaf)
    # this function put noun ahead of verb when assigning pos tags
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


# def lemmatizing(word):#lemmatization with pos value


def lemmatizing(word):  # edited by Claude Hu 08/2020
    # https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    pos = ["n", "v", "a", "s", "r"]  # list of postags
    result = word
    for _p in pos:
        # if lemmatization with any postag gives different result from the word itself
        # that lemmatization is returned as result
        from Stanza_functions_util import lemmatize_stanza, stanzaPipeLine

        lemma = lemmatize_stanza(stanzaPipeLine(word))
        if lemma != word:
            result = lemma
            break
    return result


def word_count(text):
    counts = dict()
    words = text.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts


def excludeStopWords_list(words):
    from app_constants import WORD_LISTS_DIR

    fin = open(WORD_LISTS_DIR / "stopwords.txt")
    stop_words = set(fin.read().splitlines())
    fin.close()
    # since stop_words are lowercase exclude initial-capital words (He, I)
    words_excludeStopWords = [word for word in words if word.lower() not in stop_words]
    words = words_excludeStopWords
    # exclude punctuation
    words_excludePunctuation = [word for word in words if word not in string.punctuation]
    words = words_excludePunctuation
    return words


# https://www.nltk.org/book/ch02.html
# For the Gutenberg Corpus they provide the programming code to do it. section 1.9   Loading your own Corpus.
# see also https://people.duke.edu/~ccc14/sta-663/TextProcessingSolutions.html
def compute_corpus_statistics(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    excludeStopWords=True,
    lemmatizeWords=True,
):
    filesToOpen = []

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="corpus_stats", silent=False
    )
    if outputDir == "":
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "corpus_stats", ""
    )
    filesToOpen.append(outputFilename)
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )

    Ndocs = str(len(inputDocs))
    fieldnames = [
        "Number of documents in corpus",
        "Document ID",
        "Document",
        "Number of Sentences in Document",
        "Number of Words in Document",
        "Number of Syllables in Document",
        "Word1",
        "Frequency1",
        "Word2",
        "Frequency2",
        "Word3",
        "Frequency3",
        "Word4",
        "Frequency4",
        "Word5",
        "Frequency5",
        "Word6",
        "Frequency6",
        "Word7",
        "Frequency7",
        "Word8",
        "Frequency8",
        "Word9",
        "Frequency9",
        "Word10",
        "Frequency10",
        "Word11",
        "Frequency11",
        "Word12",
        "Frequency12",
        "Word13",
        "Frequency13",
        "Word14",
        "Frequency14",
        "Word15",
        "Frequency15",
        "Word16",
        "Frequency16",
        "Word17",
        "Frequency17",
        "Word18",
        "Frequency18",
        "Word19",
        "Frequency19",
        "Word20",
        "Frequency20",
    ]
    if IO_csv_util.openCSVOutputFile(outputFilename):
        return

    startTime = IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running document(s) statistics at", True, "", True, "", False
    )

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        documentID = 0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID = documentID + 1
            logger.info("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            f = open(doc, encoding="utf-8", errors="ignore")
            docText = f.read()
            f.close()
            Nsentences = textstat.sentence_count(docText)

            Nwords = textstat.lexicon_count(docText, removepunct=True)

            Nsyllables = textstat.syllable_count(docText, lang="en_US")

            from Stanza_functions_util import (
                lemmatize_stanza,
                stanzaPipeLine,
                word_tokenize_stanza,
            )

            words = word_tokenize_stanza(stanzaPipeLine(docText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                text_vocab = []
                for w in words:
                    if w.isalpha():
                        from Stanza_functions_util import (
                            lemmatize_stanza,
                            stanzaPipeLine,
                            word_tokenize_stanza,
                        )

                        text_vocab.append(lemmatize_stanza(stanzaPipeLine(w.lower())))

                words = text_vocab

            word_counts = Counter(words)

            # 20 most frequent words in the document
            # for item in word_counts.most_common(20):
            currentLine = [
                [Ndocs, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc), Nsentences, Nwords, Nsyllables]
            ]
            for item in word_counts.most_common(20):
                currentLine[0].append(item[0])  # word
                currentLine[0].append(item[1])  # frequency
            writer = csv.writer(csvfile)
            writer.writerows(currentLine)

        csvfile.close()

        IO_user_interface_util.timed_alert(
            2000, "Analysis end", "Finished running document(s) statistics at", True, "", True, startTime, False
        )

    # number of sentences in input ---------------------------------------------------------------------
    # number of words in input ---------------------------------------------------------------------
    # number of syllables in input ---------------------------------------------------------------------
    columns_list = [
        ["Document", "Number of Sentences in Document"],
        ["Document", "Number of Words in Document"],
        ["Document", "Number of Syllables in Document"],
    ]

    columns_to_be_plotted_numeric = statistics_csv_util.get_columns_to_be_plotted(outputFilename, columns_list)
    outputFiles = charts_util.run_all(
        columns_to_be_plotted_numeric,
        outputFilename,
        outputDir,
        outputFileLabel="sent-word-syll",
        chartPackage=chartPackage,
        dataTransformation=dataTransformation,
        chart_type_list=["bar"],
        chart_title="Number of Sentences, Words, Syllables by Document",
        column_xAxis_label_var="Document",
        column_yAxis_label_var="Frequencies",
        hover_info_column_list=[],
        count_var=0,
    )  # always 1 to get frequencies of values, except for n-grams where we already pass stats

    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    # compute and chart mean, mode, skewness, kurtosis
    #   need at least 3 values, i.e., 3 documents, to compute skewness and kurtosis
    # do not use the compute_csv_column_statistics_groupBy function since only one value is available for
    #   each document
    columns_list = [
        ["Document", "Number of Sentences in Document"],
        ["Document", "Number of Words in Document"],
        ["Document", "Number of Syllables in Document"],
    ]
    columns_to_be_plotted_numeric = statistics_csv_util.get_columns_to_be_plotted(outputFilename, columns_list)

    # convert columns_to_be_plotted_numeric double list to list
    flat_list = []
    for row in columns_to_be_plotted_numeric:
        flat_list.extend(row)
    columns_to_be_plotted_numeric = flat_list

    outputFiles = statistics_csv_util.compute_csv_column_statistics_NoGroupBy(
        outputFilename, outputDir, False, chartPackage, dataTransformation, columns_to_be_plotted_numeric
    )

    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    # TODO
    #   we should create 10 classes of values by distance to the median of
    #       each value in the Number of Words in Document Col. E
    #   -0-10 11-20 21-30,… 91-100
    #   and plot them as column charts.

    # if openOutputFiles==True:
    return filesToOpen, outputDir


def Extract(lst):
    return [item[0] for item in lst]


def same_document_check(jgram):
    documentID = jgram[0][1]
    for token in jgram:
        if token[1] != documentID:
            return False
        else:
            continue
    return True


def compute_sentence_length(inputFilename, inputDir, outputDir, configFileName, chartPackage, dataTransformation):
    filesToOpen = []
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )
    Ndocs = len(inputDocs)
    if Ndocs == 0:
        return
    IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running sentence length algorithm at", True, "", True, "", False
    )

    fileID = 0
    long_sentences = 0
    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "sentence_length"
    )
    csv_headers = ["Sentence length (in words)", "Sentence ID", "Sentence", "Document ID", "Document"]

    with open(outputFilename, "w", newline="", encoding="utf-8", errors="ignore") as csvOut:
        writer = csv.writer(csvOut)
        writer.writerow(csv_headers)
        for doc in inputDocs:
            sentenceID = 0
            fileID = fileID + 1
            head, tail = os.path.split(doc)
            logger.info("Processing file " + str(fileID) + "/" + str(Ndocs) + " " + tail)
            with open(doc, encoding="utf-8", errors="ignore") as inputFile:
                text = inputFile.read().replace("\n", " ")
                from Stanza_functions_util import (
                    sent_tokenize_stanza,
                    stanzaPipeLine,
                    word_tokenize_stanza,
                )

                sentences = sent_tokenize_stanza(stanzaPipeLine(text))
                if len(sentences) == 0:
                    logger.info(
                        "Warning %s",
                        "The input file\n\n" + doc + "\n\nappears to be empty. Please, check the file and try again.",
                    )
                    return filesToOpen
                for sentence in sentences:
                    tokens = word_tokenize_stanza(stanzaPipeLine(sentence))
                    if len(tokens) > 100:
                        long_sentences = long_sentences + 1
                    sentenceID = sentenceID + 1
                    writer.writerow(
                        [len(tokens), sentenceID, sentence, fileID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]
                    )
        csvOut.close()
        head, scriptName = os.path.split(os.path.basename(__file__))
        reminders_util.checkReminder(
            scriptName, reminders_util.title_options_TIPS_file, reminders_util.message_TIPS_file, True
        )
    filesToOpen.append(outputFilename)

    outputFiles = charts_util.visualize_chart(
        chartPackage,
        dataTransformation,
        outputFilename,
        outputDir,
        columns_to_be_plotted_xAxis=[],
        columns_to_be_plotted_yAxis=["Sentence length (in words)"],
        chart_title="Sentence Length (In Words)",
        count_var=1,
        hover_label=[],
        outputFileNameType="Sent",  #'line_bar',
        column_xAxis_label="Sentence length",
        groupByList=["Document"],
        plotList=["Sentence length (in words)"],
        chart_title_label="Sentence Lenghts",
    )

    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    return filesToOpen


def compute_line_length(
    configFileName, inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation
):
    filesToOpen = []
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, ".csv", "line_length")
    filesToOpen.append(outputFilename)
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )
    Ndocs = str(len(inputDocs))
    if Ndocs == 0:
        return
    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(
        scriptName, reminders_util.title_options_line_length, reminders_util.message_line_length, True
    )
    fieldnames = ["Line length (in characters)", "Line length (in words)", "Line ID", "Line", "Document ID", "Document"]
    if IO_csv_util.openCSVOutputFile(outputFilename):
        return
    startTime = IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running line length analysis at", True, "", True, "", True
    )

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer = csv.writer(csvfile)
        documentID = 0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID += 1
            logger.info("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            with open(doc, encoding="utf-8", errors="ignore") as file:
                lineID = 0
                try:
                    line = file.readline()
                except OSError as e:
                    logger.info(str(e))
                    if "UnicodeDecodeError" in str(e):
                        logger.info(
                            "Input file error %s",
                            "The file\n\n"
                            + doc
                            + "\n\ncontains an invalid character. Please, check the file and try again. You may need to run the script to clean apostrophes and quotes.",
                        )
                    line = "THE LINE CONTAINS ILLEGAL, NON UTF-8 CHARACTERS. PLEASE, CHECK."
                    logger.info("    %s", line)
                    # continue
                while line:
                    lineID += 1
                    from Stanza_functions_util import (
                        stanzaPipeLine,
                        word_tokenize_stanza,
                    )

                    words = word_tokenize_stanza(stanzaPipeLine(line))
                    currentLine = [
                        [
                            len(line),
                            len(words),
                            lineID,
                            line.strip(),
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(doc),
                        ]
                    ]
                    writer.writerows(currentLine)
                    line = file.readline()
    csvfile.close()

    IO_user_interface_util.timed_alert(
        2000, "Analysis end", "Finished running line length analysis at", True, "", True, startTime, True
    )

    # produce all charts
    outputFiles = charts_util.visualize_chart(
        chartPackage,
        dataTransformation,
        outputFilename,
        outputDir,
        columns_to_be_plotted_xAxis=[],
        columns_to_be_plotted_yAxis=["Line length (in words)"],
        chart_title="Frequency Distribution of Line Length",
        count_var=1,
        hover_label=[],
        outputFileNameType="",  #'line_bar', column_xAxis_label='Line length',
        column_xAxis_label="Line length",
        groupByList=["Document"],
        plotList=["Line length (in words)"],
        chart_title_label="Line Length",
    )

    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    return filesToOpen


# compute_character_word_ngrams works for BOTH character and word ngrams
# https://stackoverflow.com/questions/18658106/quick-implementation-of-character-n-grams-for-word
# ngrams is the type of ngrams wanted 2grams,3grams,4grams,5grams MAX

# frequency = 0 n-grams
# frequency = 1 hapax


def compute_character_word_ngrams(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    ngramsNumber,
    frequency,
    hapax_words,
    normalize,
    lemmatize=False,
    excludePunctuation=True,
    excludeArticles=True,
    excludeDeterminers=False,
    excludeStopWords=False,
    wordgram=True,  # word as opposed to character n-grams
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
    bySentenceID=False,
):
    # hapax have ngramsNumber = 1 and frequency = 1

    if inputFilename == "" and inputDir == "":
        logger.info(
            "Input error No input file or input directory have been specified.\n\nThe function will exit.\n\nPlease, enter the required input options and try again."
        )
        return

    startTime = IO_user_interface_util.timed_alert(
        3000, "N-Grams start", "Started running Word/Characters N-Grams at", True, "", True, "", False
    )

    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return

    if ngramsNumber == 1 and frequency == 1:  # hapax
        hapax_label = "_hapax"
    else:
        hapax_label = ""

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="Ngrams" + hapax_label, silent=True
    )
    if outputDir == "":
        return

    if wordgram is None:
        wordgram = 0

    if bySentenceID is None:
        result = 0
        if result:
            bySentenceID = 1
        else:
            bySentenceID = 0

    outputFiles = get_ngramlist(
        inputFilename,
        inputDir,
        outputDir,
        configFileName,
        ngramsNumber,
        frequency,
        hapax_words,
        normalize,
        lemmatize,
        excludePunctuation,
        excludeArticles,
        excludeDeterminers,
        excludeStopWords,
        wordgram,
        bySentenceID,
        chartPackage,
        dataTransformation,
    )

    IO_user_interface_util.timed_alert(
        2000, "Analysis end", "Finished running Word/Characters N-Grams at", True, "", True, startTime, False
    )

    return outputFiles, outputDir


def process_punctuation(inputFilename, inputDir, excludePunctuation, ngrams_list, ctr_document, documentID):
    ngrams_list = []

    for item in ctr_document:  # item is every token in the document
        if item in string.punctuation and excludePunctuation:
            continue
        if inputDir == "":
            ngrams_list.append(
                [item, ctr_document[item], documentID, IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)]
            )
        else:
            # insert 0 for corpus frequency to be updated at a later point
            ngrams_list.append(
                [item, ctr_document[item], 0, documentID, IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)]
            )
    return ngrams_list


import NGrams_util
from util import collect

# hapax_words is True when the user selevcts too export ONLY words, False when hapax will also include numebrs, symbiols, etc.


def get_ngramlist(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    ngramsNumber,
    frequency=None,
    hapax_words=False,
    normalize=True,
    lemmatize=False,
    excludePunctuation=True,
    excludeArticles=True,
    excludeDeterminers=True,
    excludeStopWords=True,
    wordgram=1,
    bySentenceID=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)

    import hashfile

    o2 = (
        os.path.dirname(outputDir)
        + "art"
        + str(excludeArticles)
        + "punc"
        + str(excludePunctuation)
        + "stp"
        + str(excludeStopWords)
    )
    if hashfile.checkOut(o2):
        hashmap = hashfile.getcache(o2)
    else:
        hashmap = {}
    documents = []
    for index, file in enumerate(files):
        if hashfile.calculate_checksum(file) in hashmap:
            tokens_ = hashmap[hashfile.calculate_checksum(file)]
            head, tail = os.path.split(file)
            logger.info(" cache auto:  Processing file " + str(index + 1) + "/" + str(len(files)) + " " + tail)
        else:
            tokens_ = NGrams_util.readandsplit(
                file,
                excludePunctuation,
                excludeArticles,
                excludeDeterminers,
                excludeStopWords,
                len(files),
                lemmatize,
                index,
            )
            hashfile.storehash(hashmap, hashfile.calculate_checksum(file), tokens_)
            hashfile.writehash(hashmap, o2)
        documents.append(tokens_)
    # we allow as many n-grams as the user selects
    filesToOpen = []
    results, hapax_result = NGrams_util.operate(documents, files, int(ngramsNumber), hapax_words)
    if hapax_result is not None:
        outputDirSV = outputDir
        outputDir = IO_files_util.make_output_subdirectory("", "", outputDir, label="Hapax", silent=True)
        if outputDir == "":
            return
        hapax_result = hapax_result.values.tolist()
        hapax_result.insert(
            0, ["1-grams Hapax", "Frequency in Document", "Frequency in Corpus", "Document ID", "Document"]
        )
        csv_outputFilename = IO_files_util.generate_output_file_name(
            inputFilename,
            inputDir,
            outputDir,
            ".csv",
            "n-grams" + str(1) + "_Word_Hapax",
            "stats",
            "",
            "",
            "",
            False,
            True,
        )
        errorFound = IO_csv_util.list_to_csv(hapax_result, csv_outputFilename)
        if not errorFound:
            filesToOpen.append(csv_outputFilename)

        outputDir = outputDirSV

    outputDirSV = outputDir
    for index, result in enumerate(results):
        # create a subdirectory of the output directory by N-grams, 1, 2, 3, ...
        outputDir = IO_files_util.make_output_subdirectory(
            "", "", outputDirSV, label="Ngrams_" + str(index + 1), silent=True
        )
        if outputDir == "":
            return

        corpus_ngramsList = result.values.tolist()
        if index + 1 == 1:
            corpus_ngramsList_vocab = []
            for row in corpus_ngramsList:
                # Extract the first and third element (index 0 and 2) of each row and append to the new list
                corpus_ngramsList_vocab.append([row[0], row[2]])
            csv_vocab_outputFilename = IO_files_util.generate_output_file_name(
                inputFilename,
                inputDir,
                outputDir,
                ".csv",
                "n-grams" + str(index + 1) + "_vocab_Word",
                "stats",
                "",
                "",
                "",
                False,
                True,
            )
            corpus_ngramsList_vocab.insert(0, [str(index + 1) + "-grams", "Frequency in Corpus"])

            errorFound = IO_csv_util.list_to_csv(corpus_ngramsList_vocab, csv_vocab_outputFilename)

            if not errorFound and chartPackage != "No charts":
                filesToOpen.append(csv_vocab_outputFilename)
                columns_to_be_plotted_xAxis = [str(index + 1) + "-grams"]
                columns_to_be_plotted_yAxis = ["Frequency in Corpus"]
                # this variable is not right....
                outputFiles = charts_util.visualize_chart(
                    chartPackage,
                    dataTransformation,
                    csv_vocab_outputFilename,
                    outputDir,
                    columns_to_be_plotted_xAxis=columns_to_be_plotted_xAxis,
                    columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                    chart_title="Frequency of " + str(index + 1) + "-gram",
                    count_var=0,
                    hover_label=[],  # hover_label,
                    outputFileNameType="",
                    column_xAxis_label=str(index + 1) + "-gram",
                    groupByList=[],  # ['Document'],
                    plotList=[],  # ['Frequency in Document'],
                    chart_title_label=str(index + 1) + "-gram",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

        corpus_ngramsList.insert(
            0, [str(index + 1) + "-grams", "Frequency in Document", "Frequency in Corpus", "Document ID", "Document"]
        )
        csv_outputFilename = IO_files_util.generate_output_file_name(
            inputFilename,
            inputDir,
            outputDir,
            ".csv",
            "n-grams" + str(index + 1) + "_Word",
            "stats",
            "",
            "",
            "",
            False,
            True,
        )
        errorFound = IO_csv_util.list_to_csv(corpus_ngramsList, csv_outputFilename)

        if not errorFound and chartPackage != "No charts":
            filesToOpen.append(csv_outputFilename)

            columns_to_be_plotted_xAxis = [str(index + 1) + "-grams"]
            if inputDir == "":
                columns_to_be_plotted_yAxis = ["Frequency in Document"]
            else:
                columns_to_be_plotted_yAxis = ["Frequency in Document", "Frequency in Corpus"]
            # this variable is not right....
            outputFiles = charts_util.visualize_chart(
                chartPackage,
                dataTransformation,
                csv_outputFilename,
                outputDir,
                columns_to_be_plotted_xAxis=columns_to_be_plotted_xAxis,
                columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                chart_title="Frequency of " + str(index + 1) + "-gram",
                count_var=0,
                hover_label=[],  # hover_label,
                outputFileNameType="",
                column_xAxis_label=str(index + 1) + "-gram",
                groupByList=["Document"],
                plotList=["Frequency in Document"],
                chart_title_label=str(index + 1) + "-gram",
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)
    return filesToOpen


def tokenize(s):
    tokens = re.split(r"[^0-9A-Za-z\-'_]+", s)
    return tokens


# measures lexical diversity
# see code in cophi https://github.com/cophi-wue/cophi-toolbox
# code from https://gist.github.com/magnusnissel/d9521cb78b9ae0b2c7d6#file-lexical_diversity_yule-py
def get_yules_k_i(s):
    """
    Returns a tuple with Yule's K and Yule's I.
    (cf. Oakes, M.P. 1998. Statistics for Corpus Linguistics.
    International Journal of Applied Linguistics, Vol 10 Issue 2)

    In production this needs exception handling.
    """
    tokens = tokenize(s)
    token_counter = collections.Counter(tok.upper() for tok in tokens)
    m1 = sum(token_counter.values())
    m2 = sum([freq**2 for freq in token_counter.values()])
    i = (m1 * m1) / (m2 - m1)
    k = 1 / i * 10000
    return (k, i)


# https://swizec.com/blog/measuring-vocabulary-richness-with-python/swizec/2528
def yule(inputFilename, inputDir, outputDir, configFileName, hideMessage=False):
    # yule's I measure (the inverse of yule's K measure)
    # higher number is higher diversity - richer vocabulary
    filesToOpen = []
    Yule_value_list = []
    headers = ["Yule's K Value", "Document ID", "Document"]
    index = 0
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )

    Ndocs = str(len(inputDocs))
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, ".csv", "Yule K")
    Yule_value_list.insert(0, headers)
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        d = {}
        index = index + 1
        logger.info("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
        fullText = open(doc, encoding="utf-8", errors="ignore").read()
        words = filter(
            lambda w: len(w) > 0,
            [w.strip("0123456789!:,.?(){}[]") for w in fullText.translate(string.punctuation).lower().split()],
        )
        stemmer = PorterStemmer()
        for w in words:
            w = stemmer.stem(w).lower()
            try:
                d[w] += 1
            except KeyError:
                d[w] = 1
        # TODO
        # get freq of unique words and print it in the end
        M1 = float(len(d))
        M2 = sum([len(list(g)) * (freq**2) for freq, g in groupby(sorted(d.values()))])

        try:
            result = round((M1 * M1) / (M2 - M1), 2)
        except ZeroDivisionError:
            result = 0

        if inputFilename != "" and not hideMessage:
            IO_user_interface_util.timed_alert(
                4000,
                message_title="Yule’s K Vocabulary richness",
                message_text="The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: "
                + str(result)
                + "\n\nValue range: 0-100. The higher the value, the richer the vocabulary.",
            )
            logger.info(
                "The value for the vocabulary richness statistics (word type/token ratio or Yule’s K) is: "
                + str(result)
                + "\n\nThe higher the value (0-100) and the richer is the vocabulary.\n\nValue range: 0-100. The higher the value, the richer the vocabulary."
            )
        temp = [result, index, IO_csv_util.dressFilenameForCSVHyperlink(doc)]
        Yule_value_list.append(temp)
    IO_error = IO_csv_util.list_to_csv(Yule_value_list, outputFilename)
    if not IO_error:
        filesToOpen.append(outputFilename)

    return filesToOpen


def print_results(
    words, class_word_list, header, inputFilename, outputDir, excludestowords, fileLabel, hideMessage, filesToOpen
):
    if excludestowords:
        stopMsg = "(excluding stopwords)"
    else:
        stopMsg = "(including stopwords)"
    # if IO_error:

    if not hideMessage:
        # do not count header
        logger.info(
            "Results %s",
            "Total word count "
            + stopMsg
            + ": "
            + str(len(words))
            + "\n\nTotal word count for "
            + header
            + " "
            + stopMsg
            + ": "
            + str(len(class_word_list) - 1),
        )
    logger.info("\nTotal word count " + stopMsg + ": " + str(len(words)))
    # do not count header
    logger.info("Total word count for " + header + " " + stopMsg + ": " + str(len(class_word_list) - 1))
    logger.info("%s %s", "\n\nList of " + header + " " + stopMsg + "\n\n", class_word_list)
    # if outputFilename != '':


# called by sentence_analysis_main and style_analysis_main
def process_words(
    configFileName,
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    processType="",
    language="English",
    excludeStopWords=True,
    word_length=3,
    excludePunctuation=True,
    excludeArticles=True,
    wordgram=1,
    lemmatize=False,
):
    filesToOpen = []
    documentID = 0
    multiple_punctuation = 0
    exclamation_punctuation = 0
    question_punctuation = 0
    punctuation_docs = []
    header = []
    fileLabel = ""
    columns_to_be_plotted_yAxis = []
    chart_title_label = ""
    column_xAxis_label = ""
    word_list = []

    word_list_temp = []

    fin = open("../lib/wordLists/stopwords.txt")
    set(fin.read().splitlines())
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )

    Ndocs = str(len(inputDocs))
    if Ndocs == 0:
        return

    if processType != "":
        pass
    else:
        pass
    if Ndocs == 1:
        pass
    else:
        pass

    # ngrams already display the started running... No need to duplicate
    if "unigrams" not in processType:
        startTime = IO_user_interface_util.timed_alert(
            2000, "Analysis start", "Started running " + processType + " at", True
        )

    # process separately outside the loop through documents which is carried out inside compute_character_word_ngrams
    if (
        processType == ""
        or "N-grams" in processType
        or "hapax" in processType.lower()
        or "unigrams" in processType.lower()
    ):
        hapax_words = False
        if "hapax" in processType.lower():
            ngramsNumber = 1
            frequency = 1  # hapax
            if "hapax legomena (once-occurring words)" in processType.lower():
                hapax_words = True
        elif "unigrams" in processType.lower():
            ngramsNumber = 1
            frequency = 0
        else:
            frequency = 0  # N-grams
        normalize = False
        excludeDeterminers = False
        excludePunctuation = True
        wordgram = True
        bySentenceID = False
        outputFiles, tempoutputDir = compute_character_word_ngrams(
            inputFilename,
            inputDir,
            outputDir,
            configFileName,
            ngramsNumber,
            frequency,
            hapax_words,
            normalize,
            lemmatize,
            excludePunctuation,
            excludeArticles,
            excludeDeterminers,
            excludeStopWords,
            wordgram,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            bySentenceID,
        )
        # Excel charts are generated in compute_character_word_ngrams; return to exit here

        return outputFiles

    # For the user input of K sentences or words to be analyzed
    if "Repetition: Words" in processType or "Repetition: Last" in processType:
        if "*" in processType:
            k_str = "4"  # when processing all style algorithms, set the k_str not to stop the process
        else:
            k_str = ""
            # do not activate the reminder when processing ALL style options
            head, scriptName = os.path.split(os.path.basename(__file__))
            reminders_util.checkReminder(
                scriptName,
                reminders_util.title_options_only_CoreNLP_CoNLL_repetition_finder,
                reminders_util.message_only_CoreNLP_CoNLL_repetition_finder,
            )
        if "Repetition: Last" in processType and k_str == "":
            k_str, useless = GUI_IO_util.enter_value_widget(
                "Enter the number of words, K, to be analyzed (Repetition finder)", "K", 1, "", "", ""
            )
        elif "Repetition: Words" in processType and k_str == "":
            k_str, useless = GUI_IO_util.enter_value_widget(
                "Enter the number of sentences, K, to be analyzed (Repetition finder)", "K", 1, "", "", ""
            )
        if k_str == "":
            return
        k = int(k_str)

    # load the spaCy subjectivity pipeline once, not per sentence
    subjectivity_nlp = None
    if "Objectivity/subjectivity" in processType:
        subjectivity_nlp = get_spacy_model("en_core_web_sm")
        if "spacytextblob" not in subjectivity_nlp.pipe_names:
            subjectivity_nlp.add_pipe("spacytextblob")

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        logger.info("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        fullText = open(doc, encoding="utf-8", errors="ignore").read()
        fullText = fullText.replace("\n", " ")
        from Stanza_functions_util import sent_tokenize_stanza, stanzaPipeLine, word_tokenize_stanza

        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))

        rep_words_first = []
        rep_words_last = []
        word_list_temp = []

        sentenceID = 0  # to store sentence index
        # check each word in sentence for concreteness and write to outputFilename

        # analyze each sentence
        for s in sentences:
            sentenceID = sentenceID + 1
            s.count(" ") + 1

            from Stanza_functions_util import sent_tokenize_stanza, stanzaPipeLine

            words = word_tokenize_stanza(stanzaPipeLine(s))
            words_with_stop = [word for word in words if word.isalpha()]
            # don't process stopwords
            filtered_words = words
            if processType != "" and "punctuation" not in processType.lower():
                if excludeStopWords:
                    words = excludeStopWords_list(words)
                    filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
            # for wordID, word in enumerate(filtered_words):

            # SUBJECTIVITY/OBJECTIVITY PER SENTENCE---------------------------------------------------------------------------------------------

            if "Objectivity/subjectivity" in processType:
                header = ["Subjectivity Score", "Sentence ID", "Sentence", "Document ID", "Document"]
                fileLabel = "Objectivity_subjectivity per sentence"
                columns_to_be_plotted_yAxis = ["Subjectivity Score"]
                chart_title_label = "Frequency of subjectivity scores"
                column_xAxis_label = "Subjectivity scores"

                d = subjectivity_nlp(s)
                subjectivity_score = d._.blob.subjectivity

                word_list.append(
                    [subjectivity_score, sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)]
                )

            # Lower case words after end-of-sentence punctuation --------------------------------------------------------------------------

            for wordID, word in enumerate(filtered_words):
                if processType == "Lower case words after end-of-sentence punctuation":
                    header = [
                        "Word",
                        "Sentence ID 1",
                        "Sentence 1",
                        "Sentence ID 2",
                        "Sentence 2",
                        "Document ID",
                        "Document",
                    ]
                    if word and (word == "." or word == "!" or word == "?"):
                        # check beginning of next word in next sentence since the end-of-sentence character will have split the sentence
                        # exclude numbers from list
                        if (
                            sentenceID < len(sentences)
                            and sentences[sentenceID][0].isalpha()
                            and sentences[sentenceID][0].islower()
                        ):
                            word_list.append(
                                [
                                    str(sentences[sentenceID].split()[0]),
                                    sentenceID,
                                    s,
                                    sentenceID + 1,
                                    sentences[sentenceID],
                                    documentID,
                                    IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                ]
                            )
                        fileLabel = "sent_split"
                        columns_to_be_plotted_yAxis = ["Word"]
                        chart_title_label = ""
                        column_xAxis_label = "Words"

                # WORD LENGTH --------------------------------------------------------------------------

                if processType == "" or "word length" in processType.lower():
                    header = [
                        "Word",
                        "Word length (in characters)",
                        "Word ID (in sentence)",
                        "Number of words in sentence",
                        "Sentence ID",
                        "Sentence",
                        "Document ID",
                        "Document",
                    ]
                    fileLabel = "word_length"
                    columns_to_be_plotted_yAxis = ["Word length"]  # bar chart
                    chart_title_label = "Frequency of Word Lengths (in Characters)"
                    column_xAxis_label = "Word length (in characters)"

                    # exclude numbers from list
                    if word and word.isalpha():
                        word_list.append(
                            [
                                word,
                                len(word),
                                wordID + 1,
                                len(words),
                                sentenceID,
                                s,
                                documentID,
                                IO_csv_util.dressFilenameForCSVHyperlink(doc),
                            ]
                        )

                # INITIAL-CAPITAL WORDS --------------------------------------------------------------------------

                if processType == "" or "capital" in processType.lower():
                    header = [
                        "Initial-capital words",
                        "Word ID (in sentence)",
                        "Number of words in sentence",
                        "Sentence ID",
                        "Sentence",
                        "Document ID",
                        "Document",
                    ]
                    fileLabel = "init_cap_words"
                    columns_to_be_plotted_yAxis = ["Initial-capital words"]  # bar chart
                    chart_title_label = "Frequency of Initial-Capital Words"
                    column_xAxis_label = "Initial-capital words"

                    if word and word and word[0].isupper():
                        word_list.append(
                            [
                                word,
                                wordID + 1,
                                len(words),
                                sentenceID,
                                s,
                                documentID,
                                IO_csv_util.dressFilenameForCSVHyperlink(doc),
                            ]
                        )
                        # word_list.append([word, wordID + 1, len(words), sentenceID, s, documentID,
                        #           IO_csv_util.dressFilenameForCSVHyperlink(doc)])

                # INITIAL-VOWEL WORDS --------------------------------------------------------------------------

                if processType == "" or "vowel" in processType.lower():
                    header = [
                        "Initial vowel",
                        "Word ID (in sentence)",
                        "Number of words in sentence",
                        "Sentence ID",
                        "Sentence",
                        "Document ID",
                        "Document",
                    ]
                    fileLabel = "vowel_words"
                    columns_to_be_plotted_yAxis = ["Initial vowel"]  # bar chart
                    chart_title_label = "Frequency of Initial-Vowel Words"
                    column_xAxis_label = "Initial-vowel words"
                    if word and word and word[0].lower() in "aeiou" and word.isalpha():
                        word_list.append(
                            [
                                word,
                                wordID + 1,
                                len(words),
                                sentenceID,
                                s,
                                documentID,
                                IO_csv_util.dressFilenameForCSVHyperlink(doc),
                            ]
                        )

                # PUNCTUATION SYMBOLS --------------------------------------------------------------------------

                if processType == "" or "pathos" in processType.lower():
                    header = [
                        "Punctuation symbols of pathos (?!)",
                        "Word ID (in sentence)",
                        "Number of words in sentence",
                        "Sentence ID",
                        "Sentence",
                        "Document ID",
                        "Document",
                    ]
                    fileLabel = "punctuation"
                    columns_to_be_plotted_yAxis = ["Punctuation symbols of pathos (?!)"]  # bar chart
                    chart_title_label = "Frequency of Punctuation Symbols of Pathos (?!)"
                    column_xAxis_label = "Punctuation symbols of pathos (?!)"
                    if word != "!" and word != "?":
                        continue
                    word_list.append(
                        [
                            word,
                            wordID + 1,
                            len(words),
                            sentenceID,
                            s,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(doc),
                        ]
                    )
                    if doc not in punctuation_docs:
                        punctuation_docs.append(doc)
                    if "!" in word and "?" in word:
                        multiple_punctuation = multiple_punctuation + 1
                    elif "!" in word:
                        exclamation_punctuation = exclamation_punctuation + 1
                    elif "?" in word:
                        question_punctuation = question_punctuation + 1

                # REPEATED WORDS FIRST K SENTENCES/LAST K SENTENCES  -------------------------------------------------------------------------------
                if "Repetition: Words" in processType:
                    for wrdID, wrd in enumerate(filtered_words):
                        header = [
                            "First/Last Sentence",
                            "K Value",
                            "Word",
                            "Word ID",
                            "Sentence ID",
                            "Sentence",
                            "Document ID",
                            "Document",
                        ]
                        fileLabel = str(k) + "_K_Sentences"
                        "Rep_Words_First_Last_" + str(k) + "_K_Sentences_byDoc"
                        columns_to_be_plotted_yAxis = ["Word"]
                        chart_title_label = f"Frequency of Repeated Words in First and Last K ({k}) Sentences"
                        column_xAxis_label = "Words"

                        if sentenceID <= k:
                            word_list_temp.append(
                                [
                                    "First",
                                    k,
                                    wrd,
                                    wrdID + 1,
                                    sentenceID,
                                    s,
                                    documentID,
                                    IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                ]
                            )
                            rep_words_first.append(wrd)

                        elif sentenceID > len(sentences) - k:
                            word_list_temp.append(
                                [
                                    "Last",
                                    k,
                                    wrd,
                                    wrdID + 1,
                                    sentenceID,
                                    s,
                                    documentID,
                                    IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                ]
                            )
                            rep_words_last.append(wrd)

                if "Repetition: Words" in processType:
                    word_list.extend(
                        [
                            sublist
                            for sublist in word_list_temp
                            if sublist[2] in rep_words_first and sublist[2] in rep_words_last
                        ]
                    )

                # REPEATED WORDS END OF SENTENCE/BEGINNING NEXT SENTENCE  --------------------------------------------------------------------------
                if "Repetition: Last" in processType:
                    for wrdID, wrd in enumerate(words_with_stop):
                        header = [
                            "First/Last Sentence",
                            "K Value",
                            "Word",
                            "Word ID",
                            "Sentence ID",
                            "Sentence",
                            "Document ID",
                            "Document",
                        ]
                        fileLabel = str(k) + "_K words"
                        "Last/First_" + str(k) + "_k_words_byDoc"
                        columns_to_be_plotted_yAxis = ["Word"]
                        chart_title_label = (
                            "Frequency of Last K ("
                            + str(k)
                            + ") words of a sentence and first K words of next sentence"
                        )
                        (
                            "Frequency of Last K ("
                            + str(k)
                            + ") words of a sentence and first K words of next sentence by Document"
                        )
                        (
                            "Frequency of Last K ("
                            + str(k)
                            + ") words of a sentence and first K words of next sentence by Sentence Index"
                        )
                        column_xAxis_label = "Words"
                        if sentenceID == 1:
                            if wrdID + 1 > len(words_with_stop) - k:
                                word_list.append(
                                    [
                                        "Last",
                                        k,
                                        wrd,
                                        wrdID + 1,
                                        sentenceID,
                                        s,
                                        documentID,
                                        IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                    ]
                                )

                        else:
                            if wrdID + 1 <= k:
                                word_list.append(
                                    [
                                        "First",
                                        k,
                                        wrd,
                                        wrdID + 1,
                                        sentenceID,
                                        s,
                                        documentID,
                                        IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                    ]
                                )
                            elif wrdID + 1 > len(words_with_stop) - k:
                                word_list.append(
                                    [
                                        "Last",
                                        k,
                                        wrd,
                                        wrdID + 1,
                                        sentenceID,
                                        s,
                                        documentID,
                                        IO_csv_util.dressFilenameForCSVHyperlink(doc),
                                    ]
                                )

    # N-GRAMS & HAPAX --------------------------------------------------------------------------
    # hapax and ngrams are processed above outside the for doc loop
    #    a for doc loop is already carried out in the function compute_character_word_ngrams

    if len(word_list) == 0:
        IO_user_interface_util.timed_alert(
            2000, "Empty file", "The " + processType + " algorithm has not generated any output."
        )
        return filesToOpen

    word_list.insert(0, header)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, ".csv", fileLabel)
    IO_error = IO_csv_util.list_to_csv(word_list, outputFilename)

    if not IO_error:
        filesToOpen.append(outputFilename)

    if chartPackage != "No charts":
        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
            chart_title=chart_title_label,
            count_var=1,
            hover_label=[],
            outputFileNameType="",  # 'line_bar',
            column_xAxis_label=column_xAxis_label,
            groupByList=["Document"],
            plotList=["Frequency"],
            chart_title_label=column_xAxis_label,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # ngrams already display the started running... No need to duplicate
    if "unigrams" not in processType:
        IO_user_interface_util.timed_alert(
            2000, "Analysis end", "Finished running " + processType + " at", True, "", True, startTime
        )

    return filesToOpen


# n is n most common words
# text is the plain text read in from a file
def n_most_common_words(n, text):
    cleaned_words, common_words = [], []
    for word in text.split():
        fin = open("../lib/wordLists/stopwords.txt")
        stop_words = set(fin.read().splitlines())
        if word not in stop_words and "'" not in word and '"' not in word:
            cleaned_words.append(word)
    counts = Counter(cleaned_words)
    for key, value in counts.most_common(n):
        common_words.append([key, value])
    return common_words


def convert_txt_file(inputFilename, inputDir, outputDir, openOutputFiles, excludeStopWords=True, lemmatizeWords=True):
    filesToOpen = []
    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".txt", "corpus", "lemma_stw"
    )
    filesToOpen.append(outputFilename)

    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=GUI_IO_util.configFileName
    )

    Ndocs = str(len(inputDocs))

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running txt conversion (lemmatization & stopwords) at",
        True,
        "",
        True,
        "",
        True,
    )

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline=""):
        documentID = 0
        for doc in inputDocs:
            head, tail = os.path.split(doc)
            documentID = documentID + 1
            logger.info("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)
            fullText = open(doc, encoding="utf-8", errors="ignore").read()

            str(textstat.sentence_count(fullText))

            str(textstat.lexicon_count(fullText, removepunct=True))

            textstat.syllable_count(fullText, lang="en_US")

            from Stanza_functions_util import (
                lemmatize_stanza,
                stanzaPipeLine,
                word_tokenize_stanza,
            )

            words = word_tokenize_stanza(stanzaPipeLine(fullText))

            if excludeStopWords:
                words = excludeStopWords_list(words)

            if lemmatizeWords:
                from Stanza_functions_util import (
                    lemmatize_stanza,
                    stanzaPipeLine,
                    word_tokenize_stanza,
                )

                set(lemmatize_stanza(stanzaPipeLine(w.lower())) for w in fullText.split(" ") if w.isalpha())
                words = set(lemmatizing(w.lower()) for w in words if w.isalpha())  # fullText.split(" ") if w.isalpha())


# https://pypi.org/project/textstat/
def compute_sentence_text_readability(
    inputFilename, inputDir, outputDir, configFileName, openOutputFiles, chartPackage, dataTransformation
):
    filesToOpen = []
    documentID = 0

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="readability", silent=True
    )
    if outputDir == "":
        return

    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)

    nFile = len(files)
    if nFile == 0:
        return

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running Text Readability at",
        True,
        "\nYou can follow Text Readability in command line.",
    )

    if nFile > 1:
        outputFilenameTxt = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".txt", "READ", "stats"
        )
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".csv", "READ", "stats"
        )
    else:
        outputFilenameTxt = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".txt", "READ", "stats"
        )
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".csv", "READ", "stats"
        )
    filesToOpen.append(outputFilenameTxt)
    filesToOpen.append(outputFilename)

    fieldnames = [
        "Flesch Reading Ease formula",
        "Flesch-Kincaid Grade Level",
        "Fog Scale (Gunning FOG Formula)",
        "SMOG (Simple Measure of Gobbledygook) Index",
        "Automated Readability Index",
        "Coleman-Liau Index",
        "Linsear Write Formula",
        "Dale-Chall Readability Score",
        "Overall readability consensus",
        "Grade level",
        "Sentence ID",
        "Sentence",
        "Document ID",
        "Document",
    ]

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as outputCsvFile:
        writer = csv.DictWriter(outputCsvFile, fieldnames=fieldnames)
        writer.writeheader()

        # already shown in NLP.py

        # open txt output file
        outputTxtFile = open(outputFilenameTxt, "w")
        documentID = 0
        for file in files:
            # read txt file
            text = open(file, encoding="utf-8", errors="ignore").read()

            documentID = documentID + 1
            head, tail = os.path.split(file)
            logger.info("Processing file " + str(documentID) + "/" + str(nFile) + " " + tail)

            # write text files ____________________________________________

            outputTxtFile.write("TEXT READABILITY SCORES (by Python library textstat)" + "\n\n")
            outputTxtFile.write(file + "\n\n")

            # This legenda is now available as a TIPS file

            outputTxtFile.write(
                "RESULTS -----------------------------------------------------------------------------------------------------------------------------------------------\n\n"
            )
            # Syllable count
            str_value = "Syllable count " + str(textstat.syllable_count(text, lang="en_US"))
            outputTxtFile.write(str_value + "\n")
            # Lexicon count
            str_value = "Lexicon count " + str(textstat.lexicon_count(text, removepunct=True))
            outputTxtFile.write(str_value + "\n")
            # Sentence count
            str_value = "Sentence count " + str(textstat.sentence_count(text))
            outputTxtFile.write(str_value + "\n\n")

            # The Flesch Reading Ease formula
            str_value = "Flesch Reading Ease formula " + str(textstat.flesch_reading_ease(text))
            outputTxtFile.write(str_value + "\n")
            # The Flesch-Kincaid Grade Level
            str_value = "Flesch-Kincaid Grade Level " + str(textstat.flesch_kincaid_grade(text))
            outputTxtFile.write(str_value + "\n")
            # The Fog Scale (Gunning FOG Formula)
            str_value = "Fog Scale (Gunning FOG Formula) " + str(textstat.gunning_fog(text))
            outputTxtFile.write(str_value + "\n")
            # The SMOG Index
            str_value = "SMOG (Simple Measure of Gobbledygook) Index " + str(textstat.smog_index(text))
            outputTxtFile.write(str_value + "\n")
            # Automated Readability Index
            str_value = "Automated Readability Index " + str(textstat.automated_readability_index(text))
            outputTxtFile.write(str_value + "\n")
            # The Coleman-Liau Index
            str_value = "Coleman-Liau Index " + str(textstat.coleman_liau_index(text))
            outputTxtFile.write(str_value + "\n")
            # Linsear Write Formula
            str_value = "Linsear Write Formula " + str(textstat.linsear_write_formula(text))
            outputTxtFile.write(str_value + "\n")
            # Dale-Chall Readability Score
            str_value = "Dale-Chall Readability Score " + str(textstat.dale_chall_readability_score(text))
            outputTxtFile.write(str_value + "\n")
            # Readability Consensus based upon all the above tests
            str_value = "\n\nReadability Consensus Level based upon all the above tests: " + str(
                textstat.text_standard(text, float_output=False) + "\n\n"
            )
            outputTxtFile.write(str_value + "\n")

            # write csv files ____________________________________________

            # split into sentences
            from Stanza_functions_util import (
                sent_tokenize_stanza,
                stanzaPipeLine,
            )

            sentences = sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            # analyze each sentence in text for readability
            sentenceID = 0  # to store sentence index
            for sent in sentences:
                sentenceID = sentenceID + 1
                # Flesch Reading Ease formula
                str1 = str(textstat.flesch_reading_ease(sent))
                # The Flesch-Kincaid Grade Level
                str2 = str(textstat.flesch_kincaid_grade(sent))
                # Th3 Fog Scale (Gunning FOG Formula)
                str3 = str(textstat.gunning_fog(sent))
                # The SMOG Index
                str4 = str(textstat.smog_index(sent))
                # Automated Readability Index
                str5 = str(textstat.automated_readability_index(sent))
                # The Coleman-Liau Index
                str6 = str(textstat.coleman_liau_index(sent))
                # Linsear Write Formula
                str7 = str(textstat.linsear_write_formula(sent))
                # Dale-Chall Readability Score
                str8 = str(textstat.dale_chall_readability_score(sent))
                # Overall summary measure
                str9 = str(textstat.text_standard(sent, float_output=False))
                if str9 == "-1th and 0th grade":
                    sortOrder = 0
                elif str9 == "0th and 1st grade":
                    sortOrder = 1
                elif str9 == "1st and 2nd grade":
                    sortOrder = 2
                elif str9 == "2nd and 3rd grade":
                    sortOrder = 3
                elif str9 == "3rd and 4th grade":
                    sortOrder = 4
                elif str9 == "4th and 5th grade":
                    sortOrder = 5
                elif str9 == "5th and 6th grade":
                    sortOrder = 6
                elif str9 == "6th and 7th grade":
                    sortOrder = 7
                elif str9 == "7th and 8th grade":
                    sortOrder = 8
                elif str9 == "8th and 9th grade":
                    sortOrder = 9
                elif str9 == "9th and 10th grade":
                    sortOrder = 10
                elif str9 == "10th and 11th grade":
                    sortOrder = 11
                elif str9 == "11th and 12th grade":
                    sortOrder = 12
                elif str9 == "12th and 13th grade":
                    sortOrder = 13
                elif str9 == "13th and 14th grade":
                    sortOrder = 14
                elif str9 == "14th and 15th grade":
                    sortOrder = 15
                elif str9 == "15th and 16th grade":
                    sortOrder = 16
                elif str9 == "16th and 17th grade":
                    sortOrder = 17
                elif str9 == "17th and 18th grade":
                    sortOrder = 18
                elif str9 == "18th and 19th grade":
                    sortOrder = 19
                elif str9 == "19th and 20th grade":
                    sortOrder = 20
                elif str9 == "20th and 21st grade":
                    sortOrder = 21
                elif str9 == "21st and 22nd grade":
                    sortOrder = 22
                elif str9 == "22nd and 23rd grade":
                    sortOrder = 23
                elif str9 == "23rd and 24th grade":
                    sortOrder = 24
                else:
                    str9 = "Unclassified"
                    sortOrder = 25
                rowValue = [
                    [
                        str1,
                        str2,
                        str3,
                        str4,
                        str5,
                        str6,
                        str7,
                        str8,
                        str9,
                        sortOrder,
                        sentenceID,
                        sent,
                        documentID,
                        IO_csv_util.dressFilenameForCSVHyperlink(file),
                    ]
                ]
                writer = csv.writer(outputCsvFile)
                writer.writerows(rowValue)
        # at least 12th grade level HIGH-SCHOOL EDUCATION
        # at least 16th grade level UNDERGRADUATE COLLEGE EDUCATION
        # at least 18th grade level MA EDUCATION
        # at least 24th grade level PhD EDUCATION
        # > 24th grade level PostDoc EDUCATION

        # TODO YI not sure what to pass to the sort function;
        # IO filenames should be computed here
        outputTxtFile.close()
        outputCsvFile.close()

        result = True

        # readability
        if chartPackage != "No charts":
            result = True
            # if nFile>10:
            if result:
                # overall qualitative grade level (e.g., 4th)
                outputFiles = charts_util.visualize_chart(
                    chartPackage,
                    dataTransformation,
                    outputFilename,
                    outputDir,
                    columns_to_be_plotted_xAxis=[],
                    columns_to_be_plotted_yAxis=["Overall readability consensus"],
                    chart_title="Text Readability\nFrequencies of Overall Readability Consensus",
                    count_var=1,
                    hover_label=[],
                    outputFileNameType="cons",  # 'READ_bar',
                    column_xAxis_label="Consensus readability level",
                    groupByList=[],
                    plotList=[],
                    chart_title_label="",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

                # 0 (Flesch Reading Ease) has a different scale and 3 (SMOG) is often 0
                # do NOT plot on the same chart these two measures
                # plot all other 6 measures
                columns_to_be_plotted_yAxis = [
                    "Flesch-Kincaid Grade Level",
                    "Fog Scale (Gunning FOG Formula)",
                    "Automated Readability Index",
                    "Coleman-Liau Index",
                    "Linsear Write Formula",
                    "Dale-Chall Readability Score",
                ]
                # multiple lines with hover-over effects the sample line chart produces wrong results

                outputFiles = charts_util.visualize_chart(
                    chartPackage,
                    dataTransformation,
                    outputFilename,
                    outputDir,
                    columns_to_be_plotted_xAxis=[],
                    columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                    chart_title="Text Readability\nFrequencies of 6 Readability Measures",
                    count_var=0,
                    hover_label=[],
                    outputFileNameType="",  # 'READ_bar',
                    column_xAxis_label="Readability scores",
                    groupByList=[],
                    plotList=[],
                    chart_title_label="",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

                # overall numeric grade level
                outputFiles = charts_util.visualize_chart(
                    chartPackage,
                    dataTransformation,
                    outputFilename,
                    outputDir,
                    columns_to_be_plotted_xAxis=[],
                    columns_to_be_plotted_yAxis=["Grade level"],
                    chart_title="Text Readability\nFrequencies of Overall Grade Level",
                    count_var=0,
                    hover_label=[],
                    outputFileNameType="grade",  # 'READ_bar',
                    column_xAxis_label="Grade level",
                    groupByList=["Document"],
                    plotList=["Grade level"],
                    chart_title_label="Readability Grade Level",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

    IO_user_interface_util.timed_alert(
        2000, "Analysis end", "Finished running Text Readability at", True, "", True, startTime
    )

    if len(inputDir) != 0:
        logger.info(
            "Warning %s",
            "The output filenames generated by Textstat readability contain the name of the directory processed in input, rather than the name of any individual file in the directory.\n\nBoth txt & csv files include all "
            + str(nFile)
            + " files in the input directory processed by Textstat.",
        )
    return filesToOpen


# written by Siyan Pu October 2021
# edited by Roberto Franzosi October 2021
def sentence_structure_tree(inputFilename, outputDir, num_sentences):
    if inputFilename == "":
        logger.info("No input file")
        return
        #     'Enter sentence                                                                               ', 'Enter', 1)
        # if len(sent) == 0:
    else:
        # split into sentences
        text = open(inputFilename, encoding="utf-8", errors="ignore").read()
        sentences = nltk.sent_tokenize(text)
        maxNum = num_sentences
        maxNum = num_sentences
        if maxNum == 0:
            return

        if maxNum >= 10:
            logger.info(
                "Warning The number of sentences entered is quite large. The tree graph algorithm will produce a png file for every sentence"
            )

    sentenceID = 0  # to store sentence index

    spacy_nlp = get_spacy_model("en_core_web_sm")

    for sent in sentences:
        sentenceID = sentenceID + 1
        if sentenceID == maxNum + 1:
            return

        doc = spacy_nlp(sent)

        def token_format(token):
            return "_".join([token.orth_, token.tag_, token.dep_])

        def to_nltk_tree(node):
            if node.n_lefts + node.n_rights > 0:
                return Tree(token_format(node), [to_nltk_tree(child) for child in node.children])
            else:
                return token_format(node)

        tree = [to_nltk_tree(sent.root) for sent in doc.sents]

        cf = TreeView(tree[0])._cframe

        if inputFilename == "":
            cf.print_to_file(outputDir + "NLP_sentence_tree.ps")
        else:
            cf.print_to_file(outputDir + "/" + os.path.basename(inputFilename) + "_" + str(sentenceID) + "_tree.ps")


# written by Mino Cha March/April 2022
def compute_sentence_complexity(
    inputFilename, inputDir, outputDir, configFileName, openOutputFiles, chartPackage, dataTransformation
):
    ## list for csv file
    columns = []
    documentID = []
    document = []

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="complexity", silent=True
    )
    if outputDir == "":
        return

    all_input_docs = {}
    dId = 0

    filesToOpen = []

    startTime = IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running Sentence Complexity at", True
    )
    if len(inputFilename) > 0:
        numFiles = 1
        doc = inputFilename
        if doc.endswith(".txt"):
            with open(doc, encoding="utf-8", errors="ignore") as file:
                dId += 1
                head, tail = os.path.split(doc)
                logger.info("Processing file " + str(dId) + "/" + str(numFiles) + tail)
                text = file.read()
                documentID.append(dId)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                all_input_docs[dId] = text
    else:
        # if numFiles == 0:
        #     mb.showerror(title='Number of files error',
        #                  message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')

        inputDocs = IO_files_util.getFileList(
            inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
        )
        numFiles = len(inputDocs)
        if numFiles == 0:
            return

        for doc in inputDocs:
            if doc.endswith(".txt"):
                head, tail = os.path.split(doc)
                with open(os.path.join(inputDir, doc), encoding="utf-8", errors="ignore") as file:
                    dId += 1
                    logger.info("Importing filename " + str(dId) + "/" + str(numFiles) + " " + tail)
                    text = file.read()
                    documentID.append(dId)
                    document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
                    all_input_docs[dId] = text
    document_df = pd.DataFrame({"Document ID": documentID, "Document": document})
    document_df = document_df.astype("str")

    columns = [
        "Sentence length (No. of words)",
        "Yngve score",
        "Yngve sum",
        "Frazier score",
        "Frazier sum",
        "Sentence ID",
        "Sentence",
        "Document ID",
        "Document",
    ]
    try:
        nlp = get_stanza_pipeline(lang="en", processors="tokenize,pos,constituency", use_gpu=False)
    except Exception:
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "stanza==1.4.0"])
        nlp = get_stanza_pipeline(lang="en", processors="tokenize,pos,constituency", use_gpu=False)
    op = pd.DataFrame(columns=columns)
    for idx, txt in enumerate(all_input_docs.items()):
        doc = nlp(txt[1])
        tail = os.path.split(IO_csv_util.undressFilenameForCSVHyperlink(document[idx]))[1]
        logger.info("Processing file " + str(idx + 1) + "/" + str(numFiles) + " " + tail)
        for i, sentence in enumerate(doc.sentences):
            sent = str(sentence.constituency)
            root1 = tree.make_tree(sent)
            root2 = tree.make_tree(sent)
            leaves_list = tree.getLeavesAsList(root1)
            sentence_length = len(sentence.words)

            newRoot1 = Node.Node(root1)
            newRoot2 = Node.Node(root2)
            newRoot1.calY()
            newRoot2.calF()
            leaf = len(leaves_list)

            words = str(sentence).split(" ")
            len(words) - 1

            ySum = newRoot1.sumY()
            yAvg = round(ySum / leaf, 2)

            fSum = newRoot2.sumF()
            fAvg = round(fSum / leaf, 2)

            # new ordering
            #     'Sentence length (No. of words)': sentence_length,
            #     'Yngve score': yAvg,
            #     'Yngve sum': ySum,
            #     'Frazier score': fAvg,
            #     'Frazier sum': fSum,
            #     'Sentence ID': i + 1,
            #     'Document ID': idx + 1,
            # },ignore_index=True)
            # op = op.append({ deprecated
            # https://stackoverflow.com/questions/75956209/dataframe-object-has-no-attribute-append
            op = pd.concat(
                [
                    op,
                    pd.DataFrame(
                        [
                            {
                                "Sentence length (No. of words)": sentence_length,
                                "Yngve score": yAvg,
                                "Yngve sum": ySum,
                                "Frazier score": fAvg,
                                "Frazier sum": fSum,
                                "Sentence ID": i + 1,
                                "Sentence": sentence.text,
                                "Document ID": idx + 1,
                                "Document": document[idx],
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
    # not necessary sorted already

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "SentenceComplexity"
    )
    IO_csv_util.df_to_csv(op, outputFilename, columns, False, "utf-8")
    filesToOpen.append(outputFilename)

    # TODO we need an X-axis to plot these scores against
    # , 'Frazier score'
    outputFiles = charts_util.visualize_chart(
        chartPackage,
        dataTransformation,
        outputFilename,
        outputDir,
        columns_to_be_plotted_xAxis=[],
        columns_to_be_plotted_yAxis=["Yngve score"],
        chart_title="Frequency Distribution of Complexity Scores\n(Yngve & Frazier)",
        count_var=0,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
        hover_label=[],
        outputFileNameType="",  #'' #'complexity_bar',
        column_xAxis_label="Complexity scores",
        column_yAxis_label="Scores",
        groupByList=["Document"],
        plotList=["Yngve score", "Frazier score"],
        chart_title_label="Complexity Scores",
    )
    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    IO_user_interface_util.timed_alert(
        2000, "Analysis end", "Finished running Sentence Complexity at", True, "", True, startTime
    )
    return filesToOpen
