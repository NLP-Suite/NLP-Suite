"""
Author Roberto Franzosi Cynthia Dong May 2020
Ported to the web agent June 2026 (tkinter dialogs removed, nltk resources
checked lazily at run time instead of import time).

Performs sentiment analysis on a text file using NLTK's SentiWordNet
sentiment analysis function. The routine relies on the WordNet dictionary.

https://stackoverflow.com/questions/38263039/sentiwordnet-scoring-with-python
https://github.com/aesuli/sentiwordnet
http://www.nltk.org/howto/sentiwordnet.html
"""

import csv
import logging
import os

import charts_util
import IO_csv_util
import IO_files_util
import IO_libraries_util

logger = logging.getLogger(__name__)

_resources_checked = False


def _ensure_nltk_resources():
    global _resources_checked
    if not _resources_checked:
        IO_libraries_util.import_nltk_resource("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger")
        IO_libraries_util.import_nltk_resource("tokenizers/punkt", "punkt")
        IO_libraries_util.import_nltk_resource("corpora/wordnet", "wordnet")
        IO_libraries_util.import_nltk_resource("corpora/omw-1.4", "omw-1.4")
        IO_libraries_util.import_nltk_resource("corpora/sentiwordnet", "sentiwordnet")
        _resources_checked = True


def penn_to_wn(tag):
    """Convert between the PennTreebank tags to simple Wordnet tags."""
    from nltk.corpus import wordnet as wn

    if tag.startswith("J"):
        return wn.ADJ
    elif tag.startswith("N"):
        return wn.NOUN
    elif tag.startswith("R"):
        return wn.ADV
    elif tag.startswith("V"):
        return wn.VERB
    return None


def analyzefile(inputFilename, writer, Document_ID, Document):
    """Score each sentence of inputFilename with SentiWordNet and write rows to the csv writer."""
    from nltk import pos_tag, word_tokenize
    from nltk.corpus import sentiwordnet as swn
    from nltk.corpus import wordnet as wn

    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    if len(fulltext) < 1:
        logger.warning("Empty file %s", inputFilename)
        return

    from Stanza_functions_util import lemmatize_stanza_word, sentence_split_stanza_text, stanzaPipeLine

    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    # analyze each sentence s for sentiment
    for sentenceID, s in enumerate(sentences, start=1):
        tagged_sentence = pos_tag(word_tokenize(s))
        sentiment = 0
        tokens_count = 0
        for word, tag in tagged_sentence:
            wn_tag = penn_to_wn(tag)
            if wn_tag not in (wn.NOUN, wn.ADJ, wn.ADV):
                continue

            lemma = lemmatize_stanza_word(stanzaPipeLine(word))
            if not lemma:
                continue

            synsets = wn.synsets(lemma, pos=wn_tag)
            if not synsets:
                continue

            # Take the first sense, the most common
            synset = synsets[0]
            swn_synset = swn.senti_synset(synset.name())
            sentiment += swn_synset.pos_score() - swn_synset.neg_score()
            tokens_count += 1

        if not tokens_count:
            sentiment = 2
            label = "neutral"
        elif sentiment / tokens_count >= 0:
            sentiment = 3
            label = "positive"
        else:
            sentiment = 1
            label = "negative"

        writer.writerow(
            {
                "Sentiment score": sentiment,
                "Sentiment label": label,
                "Sentence ID": sentenceID,
                "Sentence": s,
                "Document ID": Document_ID,
                "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
            }
        )


def main(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    mode,
    chartPackage="Excel",
    dataTransformation="No transformation",
):
    """Run SentiWordNet over a single txt file or a directory of txt files."""
    # SentiWordNet computes a single sentiment score per sentence; mode (mean/median) does not apply
    filesToOpen = []

    _ensure_nltk_resources()

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_sentiWN", silent=True
    )
    if outputDir == "":
        return

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "SentiWordNet", "", "", "", "", False, True
    )

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        fieldnames = ["Sentiment score", "Sentiment label", "Sentence ID", "Sentence", "Document ID", "Document"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if inputFilename != "":  # handle single file
            if not os.path.exists(inputFilename):
                logger.warning('Input file "%s" is invalid.', inputFilename)
                return
            analyzefile(inputFilename, writer, 1, inputFilename)
        else:  # handle directory
            if not os.path.isdir(inputDir):
                logger.warning('Input directory "%s" is invalid.', inputDir)
                return
            inputDocs = IO_files_util.getFileList(
                inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
            )
            if len(inputDocs) == 0:
                return
            documentID = 0
            for file in inputDocs:
                filename = os.path.join(inputDir, os.fsdecode(file))
                if filename.endswith(".txt"):
                    documentID += 1
                    analyzefile(filename, writer, documentID, filename)
    filesToOpen.append(outputFilename)

    if chartPackage != "No charts":
        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Sentiment score"],
            chart_title="Frequency of SentiWordNet Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="SentiWordNet",
            column_xAxis_label="Sentiment score",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=["Sentiment score"],
            chart_title_label="SentiWordNet Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
