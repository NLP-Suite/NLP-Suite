"""
Author: Doris Zhou September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019
Ported to the web agent June 2026 (tkinter dialogs removed, lexicon loaded
lazily into a dict instead of a per-word linear scan).

Performs sentiment analysis on a text file using the Hedonometer; needs the
file hedonometer.json in lib/sentimentLib. Works best with social media texts,
NY Times editorials, movie reviews, and product reviews.

The structure of the json file has the format explained here
https://hedonometer.org/words.html
"""

import csv
import json
import logging
import os
import statistics

import charts_util
import GUI_IO_util
import IO_csv_util
import IO_files_util

logger = logging.getLogger(__name__)

_happs_dict = None
_stops = None


def _get_happs_dict():
    global _happs_dict
    if _happs_dict is None:
        database = GUI_IO_util.sentiment_libPath + os.sep + "hedonometer.json"
        with open(database, encoding="utf-8") as f:
            parsed_data = json.load(f)
        _happs_dict = {record["word"].casefold(): record["happs"] for record in parsed_data["objects"]}
    return _happs_dict


def _get_stops():
    global _stops
    if _stops is None:
        with open(os.path.join(GUI_IO_util.wordLists_libPath, "stopwords.txt"), encoding="utf-8") as fin:
            _stops = set(fin.read().splitlines())
    return _stops


def _score_label(sentiment):
    if sentiment > 7.5:
        return "very positive"
    elif sentiment > 6:
        return "positive"
    elif sentiment < 2.5:
        return "very negative"
    elif sentiment < 4.5:
        return "negative"
    return "neutral"


def analyzefile(inputFilename, writer, mode, Document_ID, Document):
    """Score each sentence of inputFilename with the Hedonometer and write rows to the csv writer."""
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    if len(fulltext) < 1:
        logger.warning("Empty file %s", inputFilename)
        return

    from Stanza_functions_util import (
        lemmatize_stanza_word,
        sentence_split_stanza_text,
        stanzaPipeLine,
        tokenize_stanza_text,
    )

    happs = _get_happs_dict()
    stops = _get_stops()
    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    # analyze each sentence for sentiment
    for i, s in enumerate(sentences, start=1):
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores

        words = tokenize_stanza_text(stanzaPipeLine(s.lower()))
        filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
        for w in filtered_words:
            if w in stops:
                continue
            lemma = lemmatize_stanza_word(stanzaPipeLine(w))
            total_words += 1
            score = happs.get(lemma.casefold())
            if score is not None:
                v_list.append(score)
                found_words.append(lemma)

        row = {
            "Sentence ID": i,
            "Sentence": s,
            "Document ID": Document_ID,
            "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
        }

        if len(found_words) == 0:  # no words found for this sentence
            if mode in ("mean", "both"):
                row["Sentiment score (Mean)"] = 0
                row["Sentiment label (Mean)"] = ""
            if mode in ("median", "both"):
                row["Sentiment score (Median)"] = 0
                row["Sentiment label (Median)"] = ""
            writer.writerow(row)
            continue

        row["Found Words"] = f"{len(found_words)} out of {total_words}"
        row["Word List"] = ", ".join(found_words)
        if mode == "mean" or mode == "both":
            sentiment_mean = statistics.mean(v_list)
            row["Sentiment score (Mean)"] = sentiment_mean
            row["Sentiment label (Mean)"] = _score_label(sentiment_mean)
        if mode == "median" or mode == "both":
            sentiment_median = statistics.median(v_list)
            row["Sentiment score (Median)"] = sentiment_median
            row["Sentiment label (Median)"] = _score_label(sentiment_median)
        writer.writerow(row)


def main(inputFilename, inputDir, outputDir, mode, chartPackage="Excel", dataTransformation="No transformation"):
    """Run the Hedonometer over a single txt file or a directory of txt files."""
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_hedo", silent=True
    )
    if outputDir == "":
        return

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "Hedo", "", "", "", "", False, True
    )

    if mode == "both":
        score_fields = [
            "Sentiment score (Mean)",
            "Sentiment label (Mean)",
            "Sentiment score (Median)",
            "Sentiment label (Median)",
        ]
    elif mode == "median":
        score_fields = ["Sentiment score (Median)", "Sentiment label (Median)"]
    else:
        score_fields = ["Sentiment score (Mean)", "Sentiment label (Mean)"]

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        fieldnames = score_fields + ["Found Words", "Word List", "Sentence ID", "Sentence", "Document ID", "Document"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if inputFilename != "":  # handle single file
            if not os.path.exists(inputFilename):
                logger.warning('Input file "%s" is invalid.', inputFilename)
                return
            analyzefile(inputFilename, writer, mode, 1, inputFilename)
        else:  # handle directory
            if not os.path.isdir(inputDir):
                logger.warning('Input directory "%s" is invalid.', inputDir)
                return
            Document_ID = 0
            for file in sorted(os.listdir(inputDir)):
                filename = os.path.join(inputDir, file)
                if filename.endswith(".txt"):
                    Document_ID += 1
                    analyzefile(filename, writer, mode, Document_ID, filename)
    filesToOpen.append(outputFilename)

    if chartPackage != "No charts":
        if mode == "both":
            columns_to_be_plotted_yAxis = ["Sentiment score (Mean)", "Sentiment score (Median)"]
        elif mode == "median":
            columns_to_be_plotted_yAxis = ["Sentiment score (Median)"]
        else:
            columns_to_be_plotted_yAxis = ["Sentiment score (Mean)"]

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
            chart_title="Frequency of Hedonometer Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="Hedo",
            column_xAxis_label="Sentiment score",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=["Sentiment Score"],
            chart_title_label="Hedonometer Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
