import os
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

import IO_files_util
import IO_csv_util

def sample_doc_beginning_middle_end(window, config_filename, inputFilename,inputDir,outputDir, openOutputFiles, createCharts, chartPackage, Begin_K_sent, End_K_sent):
    result_first_last = []
    result_middle = []
    header = ["First/Last Sentence", "K Value", "Sentence ID", "Sentence", "Document ID", "Document"]
    fileLabel_first_last = "first_last k"
    fileLabel_middle = "middle"
    filesToOpen = []
    fin = open('../lib/wordLists/stopwords.txt', 'r')
    stops = set(fin.read().splitlines())
    inputDocs=IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

    Ndocs=str(len(inputDocs))

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        fullText = (open(doc, "r", encoding="utf-8", errors="ignore").read())
        fullText = fullText.replace('\n', ' ')
        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))

        sentenceID = 0  # to store sentence index

        # analyze each sentence
        for s in sentences:
            sentenceID = sentenceID + 1

            if sentenceID <= Begin_K_sent or sentenceID > len(sentences) - End_K_sent:
                if sentenceID <= Begin_K_sent:
                    result_first_last.append(["First", Begin_K_sent, sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
                else:
                    result_first_last.append(["Last", End_K_sent, sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])

            else:
                result_middle.append([f"Between first {Begin_K_sent} and last {End_K_sent}", f"{Begin_K_sent}, {End_K_sent}", sentenceID, s, documentID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])


    result_first_last.insert(0, header)
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel_first_last)
    IO_error=IO_csv_util.list_to_csv(window, result_first_last, outputFilename)
    if not IO_error:
        filesToOpen.append(outputFilename)

    result_middle.insert(0, header)
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', fileLabel_middle)
    IO_error=IO_csv_util.list_to_csv(window, result_middle, outputFilename)
    if not IO_error:
        filesToOpen.append(outputFilename)

    return filesToOpen
