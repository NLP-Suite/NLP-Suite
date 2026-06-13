# If there's an error that interrupted the operation within this script, PLEASE
# 1. (In Terminal) Type in sudo lsof -i tcp:9000 see the PID of the subprocess occupying the port
# 2. Type in kill -9 ***** to kill that subprocess
# person_list.S ***** is the 5 digit PID

# originally designed by Yi Wang March 2020
# extensively edited and finalized by Claude Hu Fall 2020-2021
# edited for SVO by Cynthia Dong Fall 2020
# Edited by Roberto, Mino Cha, Jeongrok Yu, Seong Kim Fall 2022

"""
TODO
https://stanfordnlp.github.io/CoreNLP/memory-time.html
Check out the CoreNLP website to see their recommendation on using the -filelist flag
(e.g., java -cp "$STANFORD_CORENLP_HOME/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -filelist all-files.txt -outputFormat json)
and -parse.maxlen 70 or 100 to limit sentence length
there is also kbp.maxlen, ner.maxlen, and pos.maxlen but they be less necessary than the parse one
WE DO NOT USE ANY OF THESE RECOMMENDATIONS
"""

import csv
import logging
import os

import charts_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import nltk

# not using stanfordcorenlp because it is not recognizing sentiment annotator
import pandas as pd
import reminders_util
from util import collect

logger = logging.getLogger(__name__)

language_encoding = "utf-8"


def similar_string_floor_filter(str1, str2):
    dist = nltk.edit_distance(str1, str2)
    if dist <= 5:
        return True
    else:
        return False


# From Tony Chen Gu to Everyone 10:03 PM
def get_csv_column_unique_val_list(inputFilename, col):
    """
    inputFilename (str) : csv file path
    col (int)           : the column number of the desired colum
    returns (list)      : list of unique values in the csv file
    """
    data = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines="skip")
    return list(set(data.iloc[:col]))


def visualize_GIS_maps(kwargs, locations, documentID, document, date_str):
    # columns: Location, NER, tokenBegin, tokenEnd, Sentence ID, Sentence, Document ID, Document
    to_write = []
    for sent in locations:
        if ("extract_date_from_text_var" in kwargs and kwargs["extract_date_from_text_var"]) or (
            "filename_embeds_date_var" in kwargs and kwargs["filename_embeds_date_var"]
        ):
            # we need to check sent[5] for tokenBegin & tokenEnd
            to_write.append(
                [
                    sent[0],
                    sent[1],
                    sent[2],
                    sent[3],
                    sent[4],
                    sent[5],
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                    date_str,
                ]
            )
        else:
            to_write.append(
                [
                    sent[0],
                    sent[1],
                    sent[2],
                    sent[3],
                    sent[4],
                    sent[5],
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                ]
            )
    columns = [
        "Location",
        "NER",
        "tokenBegin",
        "tokenEnd",
        "Sentence ID",
        "Sentence",
        "Document ID",
        "Document",
    ]
    if ("extract_date_from_text_var" in kwargs and kwargs["extract_date_from_text_var"]) or (
        "filename_embeds_date_var" in kwargs and kwargs["filename_embeds_date_var"]
    ):
        columns = [
            "Location",
            "NER",
            "tokenBegin",
            "tokenEnd",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
            "Date",
        ]

    df = pd.DataFrame(to_write, columns=columns)
    outputFilename = kwargs["location_filename"]
    if not os.path.exists(outputFilename):
        outputFilename = IO_csv_util.df_to_csv(df, outputFilename, columns, False, language_encoding)
    else:
        df.to_csv(
            outputFilename,
            mode="a",
            header=False,
            index=False,
            encoding=language_encoding,
        )


def count_pronouns(json):
    result = 0
    for sentence in json["sentences"]:
        for token in sentence["tokens"]:
            if token["pos"] == "PRP$" or token["pos"] == "PRP":
                result += 1
    return result


def check_pronouns(
    config_filename,
    inputFilename,
    outputDir,
    filesToOpen,
    chartPackage,
    dataTransformation,
    option,
    corefed_pronouns,
    all_pronouns: int,
):
    return_files = []
    df = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines="skip")
    if df.empty:
        return return_files
    # pronoun cases:
    #   nominative: I, you, he/she, it, we, they
    #   objective: me, you, him, her, it, them
    #   possessive: my, mine, his/her(s), its, our(s), their, your, yours
    #   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves
    pronouns = [
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "her",
        "him",
        "us",
        "them",
        "my",
        "mine",
        "hers",
        "his",
        "its",
        "our",
        "ours",
        "their",
        "your",
        "yours",
        "myself",
        "yourself",
        "himself",
        "herself",
        "oneself",
        "itself",
        "ourselves",
        "yourselves",
        "themselves",
    ]
    total_count = 0
    pronouns_count = {
        "i": 0,
        "you": 0,
        "he": 0,
        "she": 0,
        "it": 0,
        "we": 0,
        "they": 0,
        "me": 0,
        "her": 0,
        "him": 0,
        "us": 0,
        "them": 0,
        "my": 0,
        "mine": 0,
        "hers": 0,
        "his": 0,
        "its": 0,
        "our": 0,
        "ours": 0,
        "their": 0,
        "your": 0,
        "yours": 0,
        "myself": 0,
        "yourself": 0,
        "himself": 0,
        "herself": 0,
        "oneself": 0,
        "itself": 0,
        "ourselves": 0,
        "yourselves": 0,
        "themselves": 0,
    }
    for _, row in df.iterrows():
        if option == "SVO":
            if (not pd.isna(row["Subject (S)"])) and (str(row["Subject (S)"]).lower() in pronouns):
                total_count += 1
                pronouns_count[str(row["Subject (S)"]).lower()] += 1
            if (not pd.isna(row["Object (O)"])) and (str(row["Object (O)"]).lower() in pronouns):
                total_count += 1
                pronouns_count[str(row["Object (O)"]).lower()] += 1
        elif option == "CoNLL":
            if (not pd.isna(row["Form"])) and (row["Form"].lower() in pronouns):
                total_count += 1
                pronouns_count[row["Form"].lower()] += 1
        elif option == "coref table":
            if not pd.isna(row["Pronoun"]):
                total_count += 1
                try:
                    # some pronouns extracted by CoreNLP coref as such may not be in the list
                    #   e.g., "we both" leading to error
                    pronouns_count[row["Pronoun"].lower()] += 1
                except Exception:
                    continue
        else:
            logger.info("Wrong Option value!")
            return []
    pronouns_count["I"] = pronouns_count.pop("i")
    if total_count > 0:
        if option != "coref table":
            head, scriptName = os.path.split(os.path.basename(__file__))
            reminders_util.checkReminder(
                scriptName,
                reminders_util.title_options_CoreNLP_pronouns,
                reminders_util.message_CoreNLP_pronouns,
                True,
            )
            return return_files
        else:
            # for coref, total count = number of resolved pronouns, the all_pronouns in the input is the number
            #   of all pronouns in the text
            coref_rate = round((corefed_pronouns / all_pronouns) * 100, 2)
            IO_user_interface_util.timed_alert(
                3000,
                "Coreference results",
                "Number of pronouns: "
                + str(all_pronouns)
                + "\nNumber of coreferenced pronouns: "
                + str(corefed_pronouns)
                + "\nPronouns coreference rate: "
                + str(coref_rate),
            )
            # save to csv file and run visualization
            outputFilename = IO_files_util.generate_output_file_name(inputFilename, "", outputDir, ".csv", "coref-sum")
            with open(outputFilename, "w", newline="", encoding="utf-8", errors="ignore") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(
                    [
                        "Number of Pronouns",
                        "Number of Coreferenced Pronouns",
                        "Pronouns Coreference Rate",
                    ]
                )
                writer.writerow([all_pronouns, corefed_pronouns, coref_rate])
                csvFile.close()
            # no need to display since the chart will contain the values

            if chartPackage != "No charts":
                columns_to_be_plotted_yAxis = [
                    "Number of Pronouns",
                    "Number of Coreferenced Pronouns",
                    "Pronouns Coreference Rate",
                ]
                outputFiles = charts_util.visualize_chart(
                    chartPackage,
                    dataTransformation,
                    outputFilename,
                    outputDir,
                    columns_to_be_plotted_xAxis=[],
                    columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                    chart_title="Coreferenced Pronouns",
                    # count_var = 1 for columns of alphabetic values
                    count_var=0,
                    hover_label=[],
                    outputFileNameType="",  #'pronouns_bar',
                    column_xAxis_label="Coreference values",
                    groupByList=[],
                    plotList=[],
                    chart_title_label="",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)
    return return_files


available_languages = [
    "Arabic",
    "Chinese",
    "English",
    "French",
    "German",
    "Hungarian",
    "Italian",
    "Spanish",
]

available_coreference = [
    # "Arabic",
    "Chinese",
    "English",
    # "French",
    # "German",
    # "Hungarian",
    # "Italian",
    # "Spanish",
]

available_lemma = [
    # "Arabic",
    # "Chinese",
    "English",
    # "French",
    # "German",
    # "Hungarian",
    # "Italian",
    # "Spanish",
]

available_NER = [
    # "Arabic",
    "Chinese",
    "English",
    "French",
    "German",
    "Hungarian",
    "Italian",
    "Spanish",
]

available_parsing_dep = [
    # "Arabic",
    "Chinese",
    "English",
    "French",
    "German",
    # "Hungarian",
    "Italian",
    "Spanish",
]

available_parsing_const = [
    "Arabic",
    "Chinese",
    "English",
    "French",
    # "German",
    "Hungarian",
    "Italian",
    "Spanish",
]

available_sentiment = [
    # "Arabic",
    # "Chinese",
    "English",
    # "French",
    # "German",
    # "Hungarian",
    # "Italian",
    # "Spanish",
]

NER_list = [
    "PERSON",
    "ORGANIZATION",
    "MISC",
    "MONEY",
    "NUMBER",
    "ORDINAL",
    "PERCENT",
    "DATE",
    "TIME",
    "DURATION",
    "SET",
    "EMAIL",
    "URL",
    "CITY",
    "STATE_OR_PROVINCE",
    "COUNTRY",
    "LOCATION",
    "NATIONALITY",
    "RELIGION",
    "TITLE",
    "IDEOLOGY",
    "CRIMINAL_CHARGE",
    "CAUSE_OF_DEATH",
]
