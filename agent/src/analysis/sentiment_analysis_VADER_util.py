"""
Author: Doris Zhou September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019
Ported to the web agent June 2026 (tkinter dialogs removed, lexicon staged
from lib/sentimentLib, dead per-word loop dropped).

Performs sentiment analysis on a text file using NLTK's VADER sentiment
analysis function. VADER (Valence Aware Dictionary and sEntiment Reasoner)
works well with social-media style text.

The VADER algorithm outputs sentiment scores to 4 classes of sentiments
  https://github.com/nltk/nltk/blob/develop/nltk/sentiment/vader.py:
neg/neu/pos and compound (aggregated score ranging from -1 most negative
to 1 most positive), which provides a single measure of polarity.
"""

import csv
import logging
import os

import charts_util
import GUI_IO_util
import IO_csv_util
import IO_files_util

logger = logging.getLogger(__name__)

_analyzer = None


def _get_analyzer():
    # nltk's SentimentIntensityAnalyzer resolves its lexicon through nltk.data,
    # but the nltk vader_lexicon resource is not bundled in the agent image:
    # stage the copy shipped in lib/sentimentLib under the nltk data path so no
    # download is needed.
    global _analyzer
    if _analyzer is None:
        import nltk.data
        from nltk.sentiment.vader import SentimentIntensityAnalyzer

        staged = os.path.join(nltk.data.path[0], "sentiment", "vader_lexicon", "vader_lexicon.txt")
        if not os.path.isfile(staged):
            os.makedirs(os.path.dirname(staged), exist_ok=True)
            with open(GUI_IO_util.sentiment_libPath + os.sep + "vader_lexicon.txt", encoding="utf-8") as src:
                # nltk 3.8 chokes on blank lines, so drop the trailing newline
                content = src.read().rstrip("\n")
            with open(staged, "w", encoding="utf-8") as dst:
                dst.write(content)
        _analyzer = SentimentIntensityAnalyzer(lexicon_file="sentiment/vader_lexicon/vader_lexicon.txt")
    return _analyzer


def analyzefile(inputFilename, writer, Document_ID, Document):
    """Score each sentence of inputFilename with VADER and write rows to the csv writer."""
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    if len(fulltext) < 1:
        logger.warning("Empty file %s", inputFilename)
        return

    from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))
    sid = _get_analyzer()

    # analyze each sentence s for sentiment
    for i, s in enumerate(sentences, start=1):
        ss = sid.polarity_scores(s)
        # "compound" score, ranging from -1 (most neg) to 1 (most pos)
        #   negative = compound score < -0.05
        #   positive = compound score > 0.05
        #   neutral = (compound score >= -0.05) and (compound score <= 0.05)
        sentiment = ss["compound"]
        label = "neutral"
        if sentiment > 0.05:
            label = "positive"
        elif sentiment < -0.05:
            label = "negative"

        writer.writerow(
            {
                "Sentiment score": sentiment,
                "Sentiment label": label,
                "Sentence ID": i,
                "Sentence": s,
                "Document ID": Document_ID,
                "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
            }
        )


def main(inputFilename, inputDir, outputDir, mode, chartPackage="Excel", dataTransformation="No transformation"):
    """Run VADER over a single txt file or a directory of txt files."""
    # VADER computes a single compound score per sentence; mode (mean/median) does not apply
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_VADER", silent=True
    )
    if outputDir == "":
        return

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "VADER", "", "", "", "", False, True
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
            documentID = 0
            for file in sorted(os.listdir(inputDir)):
                filename = os.path.join(inputDir, file)
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
            chart_title="Frequency of VADER Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="VADER",
            column_xAxis_label="Sentiment label",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=["Sentiment Score"],
            chart_title_label="VADER Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
