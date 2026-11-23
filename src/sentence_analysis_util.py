import sys

import GUI_util
import IO_libraries_util

if (
    IO_libraries_util.install_all_Python_packages(
        GUI_util.window, "sentence_analysis_util", ["tkinter", "os", "collections", "stanza"]
    )
    == False
):
    sys.exit(0)

import collections
import os
import re
import tkinter as tk

import pandas as pd

import IO_csv_util
import IO_files_util


def sentences_with_and_without_words(sentences, search_words):
    """Split sentences into those that contain one of the comma-separated search words (or collocations, e.g.
    "coming out") and those that do not. The match is on whole words and case sensitive, as in Word search's
    default options."""
    words = [w.strip() for w in search_words.split(",") if w.strip()]
    patterns = [re.compile(r"(?<!\w)" + re.escape(w) + r"(?!\w)") for w in words]
    found, not_found = [], []
    for sentence in sentences:
        (found if any(p.search(sentence) for p in patterns) else not_found).append(sentence)
    return found, not_found


# File splitter, "Split by word(s) (extract sentences)": for each input file, NLP_<file>_extract.txt has the sentences
#   with the search word(s), NLP_<file>_extract_wo-searchword.txt the sentences without; returns the files written
def extract_sentences(window, inputFilename, inputDir, outputDir, search_words, configFileName=""):
    from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)
    filesToOpen = []
    for file in files:
        with open(file, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        found, not_found = sentences_with_and_without_words(
            sentence_split_stanza_text(stanzaPipeLine(text)), search_words
        )
        name = os.path.splitext(os.path.basename(file))[0]
        if not name.startswith("NLP_"):
            name = "NLP_" + name
        for suffix, sentences in (("_extract.txt", found), ("_extract_wo-searchword.txt", not_found)):
            outputFilename = os.path.join(outputDir, name + suffix)
            with open(outputFilename, "w", encoding="utf-8", errors="ignore") as f:
                f.write("\n".join(sentences) + ("\n" if sentences else ""))
            filesToOpen.append(outputFilename)
    return filesToOpen


def Extract(lst):
    return [item[0] for item in lst]


def dictionary_items_bySentenceID(
    window,
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    chartPackage,
    dataTransformation,
    openOutputFiles=True,
    input_dictionary_file="",
    chart_title="",
):
    from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine, tokenize_stanza_text

    filesToOpen = []
    DictionaryList = []
    file_list = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)
    nFile = len(file_list)
    if nFile == 0:
        return
    # when running the function w/o a GUI, as currently is mostly the case,
    #   we would not be able to pass a dictionary file to the function
    if input_dictionary_file == "":
        initialFolder = os.path.dirname(os.path.abspath(__file__))
        input_dictionary_file = tk.filedialog.askopenfilename(
            title="Select dictionary csv file", initialdir=initialFolder, filetypes=[("csv files", "*.csv")]
        )
        if len(input_dictionary_file) == 0:
            return

    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(input_dictionary_file)

    if nColumns == 2:
        dic = pd.read_csv(input_dictionary_file, encoding="utf-8", on_bad_lines="skip")
        dic_value = dic.iloc[:, 0].tolist()
        dic_sec_value = dic.iloc[:, 1].tolist()
        dic = [(dic_value[i], dic_sec_value[i]) for i in range(len(dic_value))]
        if chart_title == "":
            chart_title = "Dictionary value"
        documentID = 0
        container = []
        for file in file_list:
            documentID += 1
            head, tail = os.path.split(file)
            print("Processing file ", str(documentID), "\\", str(nFile), tail)
            with open(file, encoding="utf-8", errors="ignore") as _f:
                text = _f.read()
            # Process each word in txt
            Sentence_ID = 0
            # sentences = tokenize.sent_tokenize(text)
            sentences = sentence_split_stanza_text(stanzaPipeLine(text))
            # word  frequency sentenceID DocumentID FileName
            for each_sentence in sentences:
                In = []
                Sentence_ID += 1
                token = tokenize_stanza_text(stanzaPipeLine(each_sentence))
                for word in token:
                    for dict_word in dic:
                        if word == dict_word[0].rstrip():
                            In.append([word, dict_word[1], Sentence_ID, each_sentence, documentID, file])
                            break
                        else:
                            continue
                container.append(In)

            ctr = collections.Counter(Extract(container))
            for word in container:
                word.insert(2, ctr.get(word[0]))
            for word in container:
                if word[0] not in Extract(DictionaryList):
                    DictionaryList.append(word)

            DictionaryList.insert(
                0,
                ["Dict_value", "Dict_second_value", "Frequency", "Sentence ID", "Sentence", "Document ID", "Document"],
            )
    else:
        dic = pd.read_csv(input_dictionary_file, encoding="utf-8", on_bad_lines="skip")
        dic_value = dic.iloc[:, 0].tolist()
        if chart_title == "":
            chart_title = "Dictionary value"
        documentID = 0
        container = []
        for file in file_list:
            documentID += 1
            head, tail = os.path.split(file)
            print("Processing file ", str(documentID), "\\", str(nFile), tail)
            with open(file, encoding="utf-8", errors="ignore") as _f:
                text = _f.read()
            # Process each word in txt
            Sentence_ID = 0
            # sentences = tokenize.sent_tokenize(text)
            sentences = sentence_split_stanza_text(stanzaPipeLine(text))
            # word  frequency sentenceID DocumentID FileName
            for each_sentence in sentences:
                In = []
                Sentence_ID += 1
                token = tokenize_stanza_text(stanzaPipeLine(each_sentence))
                for word in token:
                    for dict_word in dic_value:
                        if word == dict_word.rstrip():
                            In.append(
                                [
                                    word,
                                    Sentence_ID,
                                    each_sentence,
                                    documentID,
                                    IO_csv_util.undressFilenameForCSVHyperlink(file),
                                ]
                            )
                            break
                        else:
                            continue
                container.append(In)

            ctr = collections.Counter(Extract(container))
            for word in container:
                word.insert(1, ctr.get(word[0]))
            for word in container:
                if word[0] not in Extract(DictionaryList):
                    DictionaryList.append(word)

            DictionaryList.insert(0, ["Dict_value", "Frequency", "Sentence ID", "Sentence", "Document ID", "Document"])

        outputFilename = IO_files_util.generate_output_file_name(
            file, inputDir, outputDir, ".csv", str(Sentence_ID) + "-Dict_value", "stats", "", "", "", False, True
        )
        filesToOpen.append(outputFilename)
        IO_csv_util.list_to_csv(window, DictionaryList, outputFilename)
        import charts_Excel_util

        # the arguments in the order create_excel_chart takes them (the chart file name is made from the csv's)
        chartFilename = charts_Excel_util.create_excel_chart(
            GUI_util.window, [DictionaryList], outputFilename, outputDir, "Dict_value", chart_title, ["bar"]
        )
        if chartFilename:
            filesToOpen.append(chartFilename)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
