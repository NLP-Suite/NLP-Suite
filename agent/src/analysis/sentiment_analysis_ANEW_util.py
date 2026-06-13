"""
Author: Doris Zhou September 29, 2017
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019
Ported to the web agent June 2026 (tkinter dialogs removed, lexicon loaded
lazily into a dict, sentence IDs fixed to increment in every mode).

Performs sentiment analysis on a text file using ANEW (Affective Norms for
English Words): ratings of pleasure (pleasant/unpleasant), arousal
(calm/excited), and dominance (controlled/in control), each rated out of 9
possible points. Needs EnglishShortenedANEW.csv in lib/sentimentLib.

Bradley, M.M. & Lang, P.J. (2017). Affective Norms for English Words (ANEW):
Instruction manual and affective ratings. Technical Report C-3. Gainesville,
FL:UF Center for the Study of Emotion and Attention.
"""

import csv
import logging
import os

import charts_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import numpy as np

logger = logging.getLogger(__name__)

_anew_dict = None
_stops = None


def _get_anew_dict():
    global _anew_dict
    if _anew_dict is None:
        import pandas as pd

        anew = GUI_IO_util.sentiment_libPath + os.sep + "EnglishShortenedANEW.csv"
        data = pd.read_csv(anew, encoding="utf-8", on_bad_lines="skip")
        _anew_dict = {
            row["Word"]: (float(row["valence"]), float(row["arousal"]), float(row["dominance"]))
            for _, row in data.iterrows()
        }
    return _anew_dict


def _get_stops():
    global _stops
    if _stops is None:
        with open(os.path.join(GUI_IO_util.wordLists_libPath, "stopwords.txt"), encoding="utf-8") as fin:
            _stops = set(fin.read().splitlines())
    return _stops


def _sentiment_label(score):
    if score < 3:
        return "very unpleasant"
    elif score < 5:
        return "unpleasant"
    elif score == 5:
        return "neutral"
    elif score < 8:
        return "pleasant"
    elif score <= 9:
        return "very pleasant"
    return "neutral"


def _arousal_label(score):
    if score < 3:
        return "very calm"
    elif score < 5:
        return "calm"
    elif score == 5:
        return "neutral"
    elif score < 8:
        return "excited"
    elif score <= 9:
        return "very excited"
    return "neutral"


def _dominance_label(score):
    if score < 3:
        return "very controlled"
    elif score < 5:
        return "controlled"
    elif score == 5:
        return "neutral"
    elif score < 8:
        return "in control"
    elif score <= 9:
        return "very much in control"
    return "neutral"


def analyzefile(inputFilename, writer, mode, Document_ID, Document):
    """Score each sentence of inputFilename against ANEW and write rows to the csv writer."""
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

    anew_dict = _get_anew_dict()
    stops = _get_stops()
    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    # analyze each sentence for sentiment
    for i, s in enumerate(sentences, start=1):
        found_words = []
        total_words = 0
        v_list = []  # holds valence scores
        a_list = []  # holds arousal scores
        d_list = []  # holds dominance scores
        neg = False

        words = tokenize_stanza_text(stanzaPipeLine(s.lower()))
        filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
        for index, w in enumerate(filtered_words):
            if w in stops:
                continue

            # check for negation in 3 words before current word
            neg = False
            j = index - 1
            while j >= 0 and j >= index - 3:
                if filtered_words[j] == "not" or filtered_words[j] == "no":
                    neg = True
                j -= 1

            lemma = lemmatize_stanza_word(stanzaPipeLine(w))
            total_words += 1

            scores = anew_dict.get(lemma)
            if scores is not None:
                found_words.append("neg-" + lemma if neg else lemma)
                v_list.append(scores[0])
                a_list.append(scores[1])
                d_list.append(scores[2])

        if len(found_words) == 0:  # no words found in ANEW for this sentence
            continue

        row = {
            "Found Words": f"{len(found_words)} out of {total_words}",
            "Word List": ", ".join(found_words),
            "Sentence ID": i,
            "Sentence": s,
            "Document ID": Document_ID,
            "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
        }
        if mode == "mean" or mode == "both":
            Sentiment_mean_score = np.mean(v_list)
            Arousal_mean_score = np.mean(a_list)
            Dominance_mean_score = np.mean(d_list)
            if neg:  # reverse polarity (upstream behavior: keyed to the last word's negation flag)
                Sentiment_mean_score = 5 - (Sentiment_mean_score - 5)
                Arousal_mean_score = 5 - (Arousal_mean_score - 5)
                Dominance_mean_score = 5 - (Dominance_mean_score - 5)
            row["Sentiment score (Mean)"] = Sentiment_mean_score
            row["Sentiment label (Mean)"] = _sentiment_label(Sentiment_mean_score)
            row["Arousal score (Mean)"] = Arousal_mean_score
            row["Arousal label (Mean)"] = _arousal_label(Arousal_mean_score)
            row["Dominance score (Mean)"] = Dominance_mean_score
            row["Dominance label (Mean)"] = _dominance_label(Dominance_mean_score)
        if mode == "median" or mode == "both":
            Sentiment_median_score = np.median(v_list)
            Arousal_median_score = np.median(a_list)
            Dominance_median_score = np.median(d_list)
            if neg:  # reverse polarity (upstream behavior: keyed to the last word's negation flag)
                Sentiment_median_score = 5 - (Sentiment_median_score - 5)
                Arousal_median_score = 5 - (Arousal_median_score - 5)
                Dominance_median_score = 5 - (Dominance_median_score - 5)
            row["Sentiment score (Median)"] = Sentiment_median_score
            row["Sentiment label (Median)"] = _sentiment_label(Sentiment_median_score)
            row["Arousal score (Median)"] = Arousal_median_score
            row["Arousal label (Median)"] = _arousal_label(Arousal_median_score)
            row["Dominance score (Median)"] = Dominance_median_score
            row["Dominance label (Median)"] = _dominance_label(Dominance_median_score)
        writer.writerow(row)


def main(inputFilename, inputDir, outputDir, mode, chartPackage="Excel", dataTransformation="No transformation"):
    """Run ANEW over a single txt file or a directory of txt files."""
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_ANEW", silent=True
    )
    if outputDir == "":
        return

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "ANEW", "", "", "", "", False, True
    )

    mean_fields = [
        "Sentiment score (Mean)",
        "Sentiment label (Mean)",
        "Arousal score (Mean)",
        "Arousal label (Mean)",
        "Dominance score (Mean)",
        "Dominance label (Mean)",
    ]
    median_fields = [
        "Sentiment score (Median)",
        "Sentiment label (Median)",
        "Arousal score (Median)",
        "Arousal label (Median)",
        "Dominance score (Median)",
        "Dominance label (Median)",
    ]
    if mode == "both":
        score_fields = mean_fields + median_fields
    elif mode == "median":
        score_fields = median_fields
    else:
        score_fields = mean_fields

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
            columns_to_be_plotted_yAxis = [
                "Sentiment score (Mean)",
                "Arousal score (Mean)",
                "Dominance score (Mean)",
                "Sentiment score (Median)",
                "Arousal score (Median)",
                "Dominance score (Median)",
            ]
        elif mode == "median":
            columns_to_be_plotted_yAxis = [
                "Sentiment score (Median)",
                "Arousal score (Median)",
                "Dominance score (Median)",
            ]
        else:
            columns_to_be_plotted_yAxis = ["Sentiment score (Mean)", "Arousal score (Mean)", "Dominance score (Mean)"]

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
            chart_title="Frequency of ANEW Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="",
            column_xAxis_label="Sentiment score",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=columns_to_be_plotted_yAxis,
            chart_title_label="ANEW Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
