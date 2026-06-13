# add parameter to exclude duplicates? also mean or median analysis
import argparse
import csv
import logging
import os
import statistics
import sys

import charts_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import lib_util
import pandas as pd
from app_constants import WORD_LISTS_DIR
from util import collect

logger = logging.getLogger(__name__)
fin = open(WORD_LISTS_DIR / "stopwords.txt")
stops = set(fin.read().splitlines())
fin.close()

ratings = GUI_IO_util.concreteness_libPath + os.sep + "Concreteness_ratings_Brysbaert_et_al_BRM.csv"
if not os.path.isfile(ratings):
    logger.info(
        "The file "
        + ratings
        + " could not be found. The CONCRETENESS analysis routine expects a csv dictionary file 'Concreteness_ratings_Brysbaert_et_al_BRM.csv' in a directory 'lib' expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again."
    )
    logger.info(
        "File not found, The concreteness analysis routine expects a csv dictionary file 'Concreteness_ratings_Brysbaert_et_al_BRM.csv' in a directory 'lib' expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again"
    )
    sys.exit()
data = pd.read_csv(ratings, encoding="utf-8", on_bad_lines="skip")
data_dict = {col: list(data[col]) for col in data.columns}
_word_index = {w: i for i, w in enumerate(data_dict["Word"])}


# performs concreteness analysis on inputFile using the Brysbaert et al. concreteness ratings, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, outputFilename, documentID, documentName):
    """
    Performs concreteness analysis on the text file given as input using the Brysbaert et al. concreteness ratings.
    Outputs results to a new CSV file in outputDir.
    :param inputFilename: path of .txt file to analyze
    :param outputDir: path of directory to create new output file
    :return:
    """

    from Stanza_functions_util import (
        lemmatize_stanza_word,
        sentence_split_stanza_text,
        stanzaPipeLine,
        tokenize_stanza_text,
    )

    # read file into string
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        logger.info(f"Error: The file '{inputFilename}' is empty.\n\nPlease, use another file and try again.")
        logger.info("Empty file  %s", inputFilename)
        return

    # otherwise, split into sentences
    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    # check each word in sentence for concreteness and write to outputFilename
    # analyze each sentence for concreteness
    i = 0  # to store sentence index
    for s in sentences:
        i = i + 1
        all_words = []
        found_words = []
        score_list = []  # use the Conc.M as scores to calculate the concreteness

        # search for each valid word's concreteness ratings
        words = tokenize_stanza_text(stanzaPipeLine(s.lower()))

        filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
        for w in filtered_words:
            # don't process stopwords
            if w in stops:
                continue
            lemma = lemmatize_stanza_word(stanzaPipeLine(w))
            all_words.append(str(lemma))
            if lemma in _word_index:
                score = round(float(data_dict["Conc.M"][_word_index[lemma]]), 2)
                found_words.append("(" + str(lemma) + ", " + str(score) + ")")
                score_list.append(score)
            else:
                continue
        # else:  # output concreteness info for this sentence
        if len(score_list) > 0:
            conc_median = round(float(statistics.median(score_list)), 2)
            conc_mean = round(float(statistics.mean(score_list)), 2)
            if len(score_list) == 1:
                conc_sd = 0
            else:
                conc_sd = round(float(statistics.stdev(score_list)), 2)
            # should sort by Document ID and Sentence ID
            if conc_median != 0 and conc_mean != 0:
                writer.writerow(
                    {
                        "Concreteness (Mean score)": conc_mean,
                        "Concreteness (Median score)": conc_median,
                        "Standard Deviation": conc_sd,
                        "# Words Found": f"{len(found_words):d} out of {len(all_words):d}",
                        "Percentage": str(100 * (round(float(len(found_words)) / float(len(all_words)), 2))) + "%",
                        "Found Words": ", ".join(found_words),
                        "All Words": ", ".join(all_words),
                        "Sentence ID": i,
                        "Sentence": s,
                        "Document ID": documentID,
                        "Document": IO_csv_util.dressFilenameForCSVHyperlink(documentName),
                    }
                )

    return outputFilename  # LINE ADDED


filesToOpen = []  # LINE ADDED


def main(inputFilename, inputDir, outputDir, configFileName, chartPackage, dataTransformation, processType=""):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param inputDir:
    :param outputDir:
    :return:
    """

    if not lib_util.checklibFile(
        GUI_IO_util.concreteness_libPath + os.sep + "Concreteness_ratings_Brysbaert_et_al_BRM.csv",
        "style_analysis_style_analysis_abstract_concreteness_analysis_util.py",
    ):
        return

    if len(outputDir) < 0 or not os.path.exists(outputDir):  # empty output
        logger.info("No output directory specified, or path does not exist")
        sys.exit(0)
    elif len(inputFilename) == 0 and len(inputDir) == 0:  # empty input
        logger.info("No input specified. Please give either a single file or a directory of files to analyze.")
        sys.exit(1)

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="abstr-concret", silent=True
    )
    if outputDir == "":
        return

    startTime = IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running CONCRETENESS Analysis at", True, silent=True
    )
    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "abstr-concret-vocab", "stats"
    )
    with open(outputFilename, "w", encoding="utf-8", errors="ignore") as csvfile:
        fieldnames = [
            "Concreteness (Mean score)",
            "Concreteness (Median score)",
            "Standard Deviation",
            "# Words Found",
            "Percentage",
            "Found Words",
            "All Words",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ]
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        if len(inputFilename) > 0:  # handle single file
            head, tail = os.path.split(inputFilename)
            logger.info("Processing file 1/1 " + tail)
            if os.path.exists(inputFilename):
                filesToOpen.append(analyzefile(inputFilename, outputDir, outputFilename, 1, inputFilename))
            else:
                logger.info('Input file "' + inputFilename + '" is invalid.')
                sys.exit(0)
        elif len(inputDir) > 0:  # handle directory
            head, tail = os.path.split(inputDir)
            "Directory: " + tail
            documentID = 0
            inputDocs = IO_files_util.getFileList(
                inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
            )

            Ndocs = len(inputDocs)
            if Ndocs == 0:
                return filesToOpen

            index = 0
            if os.path.isdir(inputDir):
                os.fsencode(inputDir)
                for file in inputDocs:
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        index = index + 1
                        head, tail = os.path.split(filename)
                        logger.info("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
                        documentID += 1
                        analyzefile(filename, outputDir, outputFilename, documentID, filename)  # LINE ADDED (edited)
            else:
                logger.info('Input directory "' + inputDir + '" is invalid.')
                sys.exit(0)

        # should sort by Document ID and Sentence ID

    outputFiles = charts_util.visualize_chart(
        chartPackage,
        dataTransformation,
        outputFilename,
        outputDir,
        columns_to_be_plotted_xAxis=[],
        columns_to_be_plotted_yAxis=["Concreteness (Mean score)"],
        chart_title="Frequency Distribution of Abstract/Concrete Scores",
        count_var=1,  # 0 for numeric field
        hover_label=[],
        outputFileNameType="",
        column_xAxis_label="Concreteness scores",
        groupByList=["Document"],
        plotList=["Concreteness (Mean score)"],
        chart_title_label="Concreteness Statistics",
    )
    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    IO_user_interface_util.timed_alert(
        2000, "Analysis end", "Finished running CONCRETENESS Analysis at", True, "", True, startTime, True
    )

    return filesToOpen


if __name__ == "__main__":
    # get arguments from command line
    parser = argparse.ArgumentParser(description="Concreteness analysis with Concreteness ratings by Brysbaert et al.")
    parser.add_argument(
        "--file", type=str, dest="inputFilename", default="", help="a string to hold the path of one file to process"
    )
    parser.add_argument(
        "--dir",
        type=str,
        dest="inputDir",
        default="",
        help="a string to hold the path of a directory of files to process",
    )
    parser.add_argument(
        "--out", type=str, dest="outputDir", default="", help="a string to hold the path of the output directory"
    )
    parser.add_argument("--outfile", type=str, dest="outputFilename", default="", help="output file name")

    args = parser.parse_args()

    # run main
    sys.exit(main(args.inputFilename, args.inputDir, args.outputDir, args.outputFilename))

# example: a single file
# python ConcretenessAnalysis.py --file "C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\MURPHY\Murphy Miracles thicker than fog CORENLP.txt" --out C:\Users\rfranzo\Desktop\NLP_output
