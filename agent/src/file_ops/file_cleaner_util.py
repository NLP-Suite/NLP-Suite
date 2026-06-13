#!/usr/bin/python
# Python version target: 3.6.3 Anaconda

import glob
import logging
import os
import re
import string

import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util

logger = logging.getLogger(__name__)


def create_input_subdir(inputDir, label):
    # create a subdirectory of the input directory
    inputDirBase = os.path.basename(inputDir)
    outputDir = inputDir + os.sep + inputDirBase + label
    outputDir = IO_files_util.make_output_subdirectory("", "", outputDir, label="", silent=True)
    return outputDir


# get all the paragraphs in the file fn based on hard returns \r
# the function returns a list [] of paragraphs
def get_paragraphs(fn):
    paragraphs = []
    paragraphs = fn.read().split("\r")  # carriage return/hard return
    lst = []
    for paragraph in paragraphs:
        for s in paragraph.split("\n"):
            lst.append(s)
    paragraphs = lst
    paragraphs = [fn.strip() for fn in paragraphs if fn.strip()]
    return paragraphs


# the function checks for end of paragraph punctuation
#   where a paragraph is any chunk of text followed by a carriage return/hard return
#   the function checks for double quotation and single quotation first, then check for .!?
#   if .?| or ." ?" |" or .' ?' |' then a full stop . is added
#   The reason is that if many successive paragraphs have no end-of-paragraph punctuation, Stanford CoreNLP will string all of them together
#       potentially creating unduly long sentences that may lead to efficiency issues
#       https://stanfordnlp.github.io/CoreNLP/memory-time.html


# extra parameters passed to uniform the funct call
# paragraphs are separated by hard returns \r
def add_full_stop_to_paragraph(
    window,
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    openOutputFiles,
    chartPackage="Excel",
    dataTransformation="No transformation",
):
    # if result==False:

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the add fullstop function at",
        True,
        "",
        True,
        "",
        False,
    )

    label = "_FullStops"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, label)

    # collecting input txt files
    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(inputDocs)
    docID = 0
    if nDocs == 0:
        return

    # DOCUMENTS WITH FULL STOPS ADDED
    count = 0
    docID = 0

    for filename in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(filename)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        edited = False
        with open(filename, encoding="utf-8", errors="ignore") as fn:
            # add_full_stop_to_paragraph
            outfile = outputDir + os.sep + tail.replace(".txt", label + ".txt")
            paragraphs = get_paragraphs(fn)
            with open(outfile, "w", encoding="utf-8", errors="ignore") as out:
                for paragraph in paragraphs:
                    check_index = -1
                    if paragraph and paragraph[-1] in ["'", '"']:
                        if len(paragraph) >= 2:
                            check_index = -2
                    # check for enf of paragraph punctuation, quotation and single quotation first, then check for .!?
                    if paragraph and paragraph[check_index] not in [".", "!", "?"]:
                        out.write(paragraph + ".\n")
                        edited = True
                    else:
                        out.write(paragraph)
                        out.write("\n")
        if edited:
            count += 1

    msgString = ""
    if count == 0:
        if nDocs == 1:
            msgString = "The document has no added full stops."
        else:
            msgString = "No documents have been edited for added full stops."
    else:
        msgString = (
            f"{nDocs} documents out of {count} have been edited for full stops."
            + f"\n\nThe percentage of documents processed is {(float(count) / nDocs) * 100:.2f}"
        )
    if count > 0:
        if inputFilename != "":
            msgString = msgString + "\n\nAll edits were saved directly in the input file."
        else:
            msgString = msgString + "\n\nAll edits were saved directly in all affected input files."

    logger.info("End of paragraph punctuation" + msgString)
    # always open outputDir
    IO_files_util.openExplorer(window, head)
    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the add fullstop function at",
        True,
        "",
        True,
        startTime,
        False,
    )


def check_typesetting_hyphenation(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):
    filesToOpen = []
    docID = 0
    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        hyphenated_lines = 0
        lines = []
        with open(infile, encoding="utf-8", errors="ignore") as source:
            for line in source.readlines():
                line = line.rstrip("\n")
                if line.endswith("-"):
                    if len(line) >= 2:
                        if line[-2] == " ":
                            continue
                    hyphenated_lines += 1
                    lin, _, e = line.rpartition(" ")
                    lines.append(line)

        if hyphenated_lines > 0:
            logger.info(
                "Warning: There are "
                + str(hyphenated_lines)
                + " typesetting hyphenated lines in the input file(s).\n\nPlease, check carefully the output csv file to make sure that there are no legitimate end-of-line hyphens (e.g., pretty-smart) that should not be joined together. In such legitimate cases, please, manually move the line end to the next line."
            )
            outputFilename = IO_files_util.generate_output_file_name(
                inputFilename, inputDir, outputDir, ".csv", "lines with end hyphen"
            )
            lines.insert(0, "Line ending with -")
            IO_error = IO_csv_util.list_to_csv(window, lines, outputFilename)
            if not IO_error:
                filesToOpen.append(outputFilename)
            # if openOutputFiles:
        else:
            logger.info(
                "Warning: There are " + str(hyphenated_lines) + " typesetting hyphenated lines in the input file(s)."
            )


# replace - followed by a hard carriage return \r at the end of a line with a blank joined to the beginning of the next line
def remove_typeseting_hyphenation(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the typesetting hyphenation function at",
        True,
        "",
        True,
        "",
        False,
    )

    label = "_NoHyph"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, "_NoHyph")

    message = "The input file(s) may contain legitimate end-of-line hyphens (e.g., pretty-smart with pretty- at the end of a line and smart at the beginning of the next line). In such legitimate cases, the two-parts of the hyphenated compound should not be joined together (rather, the line end, pretty- should be manually moved to the next line.\n\nDo you want to check, first, that there are no legitimate uses of end-of-line hyphens, before removing them all automatically, whether legitimate or not?"
    logger.info(message)
    answer = "yes"
    if answer:
        check_typesetting_hyphenation(
            window,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage="Excel",
            dataTransformation="No transformation",
            configFileName=configFileName,
        )
        return

    docID = 0
    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        removed_hyphens = 0
        # remove_typeseting_hyphenation
        if inputDir != "":
            # do not modify the filename when processing multiple files in a directory
            #   this way, they can be copied directly over the inputDir
            outfile = outputDir + os.sep + tail
        else:
            outfile = outputDir + os.sep + tail.replace(".txt", label + ".txt")
        with (
            open(infile, encoding="utf-8", errors="ignore") as source,
            open(outfile, "w", encoding="utf-8", errors="ignore") as dest,
        ):
            holdover = ""
            for line in source.readlines():
                line = line.rstrip("\n")
                if line.endswith("-"):
                    if len(line) >= 2:
                        if line[-2] == " ":  # do not convert - preceded by a space
                            continue
                    removed_hyphens += 1
                    lin, _, e = line.rpartition(" ")
                else:
                    lin, e = line, ""
                dest.write(f"{holdover}{lin}\n")
                holdover = e[:-1]
    if removed_hyphens > 0:
        if inputDir != "":
            save_msg = (
                "\n\nOutput files saved in the subdirectory " + outputDir + " of the same directory of input files."
            )
        else:
            save_msg = "\n\nOutput file saved in the same directory of the input file with " + label + ".txt ending."
    else:
        save_msg = ""
    logger.info(
        "Warning: " + str(removed_hyphens) + " end-line typesetting hyphens removed from the input file(s)." + save_msg
    )
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the typesetting hyphenation function at",
        True,
        "",
        True,
        startTime,
        False,
    )


def remove_hard_carriage_returns(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the hard-carriage returns function at",
        True,
        "",
        True,
        "",
        False,
    )

    label = "_NoHcR"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, label)

    message = "The input file(s) may contain legitimate hard-carriage returns at the end of pargraphs (e.g., pretty-smart with pretty- at the end of a line and smart at the beginning of the next line). In such legitimate cases, the two-parts of the hyphenated compound should not be joined together (rather, the line end, pretty- should be manually moved to the next line.\n\nDo you want to check, first, that there are no legitimate uses of end-of-line hyphens, before removing them all automatically, whether legitimate or not?"
    logger.info(message)
    answer = "yes"
    if answer:
        check_typesetting_hyphenation(
            window,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage="Excel",
            dataTransformation="No transformation",
            configFileName=configFileName,
        )
        return

    docID = 0
    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        removed_hard_returns = 0
        if inputDir != "":
            # do not modify the filename when processing multiple files in a directory
            #   this way, they can be copied directly over the inputDir
            outfile = outputDir + os.sep + tail
        else:
            outfile = head + os.sep + tail.replace(".txt", label + ".txt")
        new_paragraph = ""
        with open(infile, encoding="utf-8", errors="ignore") as fn:
            paragraphs = get_paragraphs(fn)
            with open(outfile, "w", encoding="utf-8", errors="ignore") as out:
                for paragraph in paragraphs:
                    new_paragraph = new_paragraph + paragraph + " "
                    removed_hard_returns += 1
                out.write(new_paragraph)
        out.close()
    if removed_hard_returns > 0:
        if inputDir != "":
            save_msg = (
                "\n\nOutput files saved in the subdirectory " + outputDir + " of the same directory of input files."
            )
        else:
            save_msg = "\n\nOutput file saved in the same directory of the input file with " + label + ".txt ending."
    else:
        save_msg = ""
    logger.info(
        "Warning" + str(removed_hard_returns) + " hard-carriage returns removed from the input file(s)." + save_msg
    )
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the hard-carriage returns function at",
        True,
        "",
        True,
        startTime,
        False,
    )


# add space between punctuation and quotation marks
def process_text_add_blank(text):
    text = re.sub(r'([.!?"])(?=")', r"\1 ", text)
    # Remove spaces between periods in ellipses #(e.g., Max add a couple of short examples)
    text = re.sub(r"\.\s*\.\s*\.\s*", "...", text)
    # Remove ¨C # (Max has this got to do with blanks? ????)
    text = text.replace("¨C", "")
    # Add space after any punctuation if followed by a letter (e.g., ) #(e.g., Max add a couple of short examples)
    text = re.sub(r'([.!?])([A-Za-z"])', r"\1 \2", text)
    # shrink 2 spaces into 1 # (Max add a couple of examples, although this is very clear)
    text = re.sub(r"\s{2,}", " ", text)
    return text


def add_missing_blank_after_punctuation(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the add missing blank after punctuation function at",
        True,
        "",
        True,
        "",
        False,
    )

    label = "_add_blank"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, label)

    docID = 0
    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    blanks_added = 0
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        if inputDir != "":
            # do not modify the filename when processing multiple files in a directory
            #   this way, they can be copied directly over the inputDir
            outfile = outputDir + os.sep + tail
        else:
            outfile = head + os.sep + tail.replace(".txt", label + ".txt")
        with open(infile, encoding="utf-8", errors="ignore") as infile:
            text = infile.read()
            processed_text = process_text_add_blank(text)
            if processed_text != text:
                blanks_added += 1
                with open(outfile, "w", encoding="utf-8", errors="ignore") as outfile:
                    outfile.write(processed_text)
                outfile.close()
    if blanks_added > 0:
        if inputDir != "":
            save_msg = (
                "\n\nOutput files saved in the subdirectory " + outputDir + " of the same directory of input files."
            )
        else:
            save_msg = "\n\nOutput file saved in the same directory of the input file with " + label + ".txt ending."
    else:
        save_msg = ""
    logger.info(
        "Warning, Missing blanks were inserted after punctuation in " + str(blanks_added) + " input file(s)." + save_msg
    )
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the add missing blank after punctuation function at",
        True,
        "",
        True,
        startTime,
        False,
    )


def remove_characters_between_characters(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
    startCharacter="",
    endCharacter="",
):

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the remove characters between characters function at",
        True,
        "",
        True,
        "",
        False,
    )

    # if not IO_user_interface_util.input_output_save('Remove all characters between characters'):

    label = "_NoChars"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, label)
    else:
        head, tail = os.path.split(inputFilename)
        outputDir = head

    if startCharacter == "":
        startCharacter, useless = GUI_IO_util.enter_value_widget(
            "Enter the single start character (e.g., [)", "", 1, "", "", ""
        )
        if startCharacter == "":
            logger.info("Blank start character, No start character entered. Routine aborted.")
            return
        endCharacter, useless = GUI_IO_util.enter_value_widget(
            "Enter the single end character (e.g., ])", "", 1, "", "", ""
        )
        if endCharacter == "":
            logger.info("Blank end character, No end character entered. Routine aborted.")
            return

    No_files_edited = 0
    No_odd_pairs = 0
    edited_files_list = []
    odd_pairs_files_list = []
    file_sizes = []
    docID = 0
    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    for file in files:
        docID = docID + 1
        head, tail = os.path.split(file)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        with open(file, encoding="utf_8", errors="ignore") as infile:
            fullText = infile.read()
            number_of_characters_start = fullText.count(startCharacter)
            if number_of_characters_start == 0:
                IO_user_interface_util.timed_alert(
                    1000,
                    "Warning",
                    "   No Start character " + startCharacter + " was found in the input file " + tail + ".",
                    True,
                    "",
                    True,
                    "",
                    True,
                )
                continue  # skip to next file
            number_of_characters_end = fullText.count(endCharacter)
            if number_of_characters_end == 0:
                IO_user_interface_util.timed_alert(
                    1000,
                    "Warning",
                    "   No End character " + endCharacter + " was found in the input file " + tail + ".",
                    True,
                    "",
                    True,
                    "",
                    True,
                )
                continue  # skip to next file
            if startCharacter == endCharacter:
                if number_of_characters_start % 2 != 0:  # ODD integer
                    IO_user_interface_util.timed_alert(
                        1000,
                        "Warning",
                        "   ODD NUMBER of "
                        + startCharacter
                        + " and "
                        + endCharacter
                        + " was found in the input file "
                        + tail
                        + ".\n   File skipped. Please, check carefully the input file for start/end pairs.",
                        True,
                        "",
                        True,
                        "",
                        True,
                    )
                    No_odd_pairs += 1
                    odd_pairs_files_list.append(tail)
                    continue  # skip to next file

                number_of_characters_pairs = int(number_of_characters_start / 2)
            else:
                number_of_characters_pairs = int(number_of_characters_start)
            i = 0
            while i < number_of_characters_pairs:
                split_string_A = fullText.split(startCharacter, 1)  # Split into "ab" and "cd"
                split_string_A = split_string_A[0]
                split_string_B = fullText.split(endCharacter, 1)  # Split into "ab" and "cd"
                if len(split_string_B) > 1:
                    split_string_B = split_string_B[1]
                    if startCharacter == endCharacter:
                        split_string_B = split_string_B.split(endCharacter, 1)  # Split into "ab" and "cd"
                        split_string_B = split_string_B[1]
                else:
                    split_string_B = split_string_B[0]

                fullText = split_string_A + split_string_B
                i += 1
            # remove_characters_between_characters

            if inputDir != "":
                # do not modify the filename when processing multiple files in a directory
                #   this way, they can be copied directly over the inputDir
                outfile = outputDir + os.sep + tail
            else:
                outfile = outputDir + os.sep + tail.replace(".txt", label + ".txt")
            with open(outfile, "w+", encoding="utf_8", errors="ignore") as out:
                out.write(fullText)

                file_sizes.append(
                    [
                        IO_csv_util.dressFilenameForCSVHyperlink(file),
                        IO_csv_util.dressFilenameForCSVHyperlink(outfile),
                        str(os.stat(file).st_size),
                        str(os.stat(outfile).st_size),
                        str(os.stat(file).st_size - os.stat(outfile).st_size),
                    ]
                )
                logger.info(
                    "   FILE SIZES (in bytes) - ORIGINAL  %s  EDITED  %s",
                    os.stat(file).st_size,
                    os.stat(outfile).st_size,
                )

                if inputDir != "":
                    No_files_edited += 1
                    edited_files_list.append(tail)
                    IO_user_interface_util.timed_alert(
                        1000,
                        "Warning",
                        "   "
                        + str(i)
                        + " substrings contained between "
                        + startCharacter
                        + " "
                        + endCharacter
                        + " were removed.",
                        True,
                        "",
                        True,
                        "",
                        True,
                    )
                else:
                    logger.info(
                        "Edits saved: "
                        + str(i)
                        + " substrings contained between "
                        + startCharacter
                        + " "
                        + endCharacter
                        + " were removed.\n\nThe edits were saved to the file \n\n"
                        + str(outfile)
                        + "\n\nin the input directory\n\n"
                        + inputDir
                    )

    if inputDir != "":
        if No_files_edited > 0:
            logger.info(
                "Warning"
                + str(No_files_edited)
                + " files were edited removing ALL substrings contained between "
                + startCharacter
                + " "
                + endCharacter
                + ".\n\nThe edits were saved to files in a subdirectory of the input directory\n\n"
                + head
                + "\n\nList of edited files:\n\n"
                + str(edited_files_list)
            )
            logger.info(
                str(No_files_edited)
                + " files edited removing ALL substrings between "
                + startCharacter
                + " "
                + endCharacter
                + ".\n"
                + str(edited_files_list)
            )
            header = [
                "Original file",
                "Edited file",
                "Original file size in bytes",
                "Edited file size in bytes",
                "Difference in bytes (should be >0)",
            ]
            file_sizes.insert(0, header)
            IO_csv_util.list_to_csv(window, file_sizes, outputDir + os.sep + "file_sizes.csv")
            IO_files_util.openFile(window, outputDir + os.sep + "file_sizes.csv")

    if No_odd_pairs > 0:
        logger.info(
            "Warning, ODD PAIRS of start/end values "
            + startCharacter
            + " "
            + endCharacter
            + " were found in "
            + str(No_odd_pairs)
            + " files.\n\nTHE FILES WERE SKIPPED FROM PROCESSING. PLEASE, CHECK THOSE FILES CAREFULLY.\n\n"
            + str(odd_pairs_files_list)
        )
        logger.info(
            "\n\nODD PAIRS of start/end values "
            + startCharacter
            + " "
            + endCharacter
            + " were found in "
            + str(No_odd_pairs)
            + " files. FILES WERE SKIPPED FROM PROCESSING. CHECK CAREFULLY.\n   "
            + str(odd_pairs_files_list)
        )

    # \n\nThe edits were saved to the files in the subdirectory\n\n' + str(outputDir) + '\n\nof the input directory\n\n'+inputDir
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the remove characters between characters function at",
        True,
        "",
        True,
        startTime,
        False,
    )


# inputFilename contains path
# remove extra blank lines in input files
def remove_blank_lines(
    window,
    inputFilename,
    inputDir,
    outputDir="",
    configFileName="",
    openOutputFiles=False,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the remove blank lines function at",
        True,
        "",
        True,
        "",
        False,
    )

    label = "_NoBlanks"
    if inputDir != "":
        outputDir = create_input_subdir(inputDir, label)

    # if result==False:

    files = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType="txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(files)
    if nDocs == 0:
        return
    docID = 0
    filesWithEmptyLines = 0
    for file in files:
        docID = docID + 1
        head, tail = os.path.split(file)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        withEmptyLines = False
        outputLines = ""
        with open(file, encoding="utf_8", errors="ignore") as infile:
            for line in infile.read().split("\n"):  # check if any line is empty line
                if line.strip() == "":
                    withEmptyLines = True
                else:
                    outputLines += line + "\n"
        # remove_blank_lines
        if inputDir != "":
            # do not modify the filename when processing multiple files in a directory
            #   this way, they can be copied directly over the inputDir
            outfile = outputDir + os.sep + tail
        else:
            outfile = outputDir + os.sep + tail.replace(".txt", label + ".txt")
        with open(outfile, "w+", encoding="utf_8", errors="ignore") as outfile:
            outfile.write(outputLines[:-1])  # non-empty line. Write it to output
        if withEmptyLines:  # if there is any empty line, increment count
            filesWithEmptyLines += 1
    if inputFilename != "":
        if filesWithEmptyLines == 0:
            logger.info("Blank lines removed, No blank lines were removed from the input file.")
        else:
            logger.info("Blank lines removed, Blank lines were removed from the input file.")
    else:
        if filesWithEmptyLines == 0:
            logger.info(
                "Blank lines removed, No files contained blank lines"
                + " out of "
                + str(nDocs)
                + " files in the input directory."
            )
        else:
            logger.info(
                "Blank lines removed, Blank lines were removed from "
                + str(filesWithEmptyLines)
                + " out of "
                + str(nDocs)
                + " files in the input directory."
            )
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the remove blank lines function at",
        True,
        "",
        True,
        startTime,
        False,
    )


# criteria for title are no punctuation and
# a shorter (user determined) sentence in number of words


# Check whether a sentence is title
# criteria for title are no puntuation and a shorter (user determined) sentence
def isTitle(sentence, Title_length_limit):
    if sentence[-1] not in string.punctuation:
        if len(sentence) < Title_length_limit:
            return True
    if sentence.isupper():
        return True
    if sentence.istitle():
        return True


def newspaper_titles(
    window,
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    openOutputFiles,
    chartPackage,
    dataTransformation,
):
    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text

    if inputDir == "" and inputFilename != "":
        NUM_DOCUMENT = 1
    else:
        NUM_DOCUMENT = len(glob.glob(os.path.join(inputDir, "*.txt")))
    if NUM_DOCUMENT == 0:
        return
    Title_length_limit = 100

    # Title length pop up widget
    # window, textCaption, lower_bound, upper_bound, default_value
    val = Title_length_limit
    # val = GUI_IO_util.slider_widget(GUI_util.window,
    #                                      "Please, select the value for number of characters in a document title. The suggested value is " + str(
    #                                          Title_length_limit) + ".", 1, 1000, 100)
    Title_length_limit = val

    TITLENESS = "NO"

    titleness = True
    if TITLENESS == "NO":
        titleness = False

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running the newspaper titles function at",
        True,
        "",
        True,
        "",
        False,
    )

    # DOCUMENTS WITH TITLES
    count = 0
    titles = []

    if inputFilename != "":
        temp_inputDir, tail = os.path.split(inputFilename)
    else:
        temp_inputDir = inputDir

    path_aritclesWithTitles = os.path.join(temp_inputDir, "documents_with_titles")

    if not os.path.exists(path_aritclesWithTitles):
        os.makedirs(path_aritclesWithTitles)

    # collecting input txt files
    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )
    nDocs = len(inputDocs)
    docID = 0
    if nDocs == 0:
        return
    logger.info("\n\nProcessing documents with titles...\n\n")
    for filename in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(filename)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        with open(filename, encoding="utf-8", errors="ignore") as fn:
            # newspaper_titles
            paragraphs = get_paragraphs(fn)
            file_path = os.path.join(path_aritclesWithTitles, tail)
            with open(file_path, "w", encoding="utf-8", errors="ignore") as out:
                for paragraph in paragraphs:
                    if isTitle(paragraph, Title_length_limit):
                        if paragraph and paragraph[-1] != ".":
                            out.write(paragraph + ".\n")
                        else:
                            out.write(paragraph)
                    else:
                        # for one in sent_tokenize(paragraph):#.decode('utf-8')):
                        for one in tokenize_stanza_text(stanzaPipeLine(paragraph)):
                            out.write(one)  # .encode('utf-8'))
                            out.write(" ")
                        out.write("\n")
        count += 1

    # DOCUMENTS WITHOUT TITLES
    count = 0
    titles = []
    docID = 0

    path_documents = os.path.join(temp_inputDir, "documents_no_titles")
    if not os.path.exists(path_documents):
        os.makedirs(path_documents)
    for filename in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(filename)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        with open(filename, encoding="utf-8", errors="ignore") as fn:
            # newspaper_titles
            paragraphs = get_paragraphs(fn)
            file_path = os.path.join(path_documents, tail)
            with open(file_path, "w", encoding="utf-8", errors="ignore") as out:
                title = []
                for paragraph in paragraphs:
                    if isTitle(paragraph, Title_length_limit):
                        title.append(paragraph)
                    else:
                        # for one in sent_tokenize(paragraph):#.decode('utf-8')):
                        for one in tokenize_stanza_text(stanzaPipeLine(paragraph)):
                            out.write(one)
                            out.write(" ")
                        out.write("\n")
                titles.append((title, filename))
        count += 1

    # TITLES ONLY
    path_title = os.path.join(temp_inputDir, "document_titles_only")
    if not os.path.exists(path_title):
        os.makedirs(path_title)
    titles_file = os.path.join(path_title, "titles.txt")
    with open(titles_file, "w", encoding="utf_8", errors="ignore") as output:
        count = 0
        for i, title in enumerate(titles):
            if title:
                count += 1
            output.write("\n")
            # a boundary can be added
            if titleness:
                output.write(f"Document {i}: {title[1]} ")
            output.write("\n")
            for t in title[0]:
                if t and t[-1] != ".":
                    t = t + ". \n"
                output.write(t)
                output.write("\n")

    msgString = ""
    if count == 0:
        if NUM_DOCUMENT == 1:
            msgString = "The document has not generated separate titles."
        else:
            msgString = "No documents have generated separate titles."
    else:
        msgString = (
            f"{NUM_DOCUMENT} documents out of {count} have generated titles."
            + f"\n\nThe percentage of documents processed is {(float(count) / nDocs) * 100:.2f}"
        )
    if count > 0:
        if inputFilename != "":
            msgString = (
                msgString
                + "\n\nThe files were saved in the subdirectory\n\n"
                + str(path_documents)
                + "\n\nof the input file directory\n\n"
                + inputDir
            )
        else:
            msgString = (
                msgString
                + "\n\nThe files were saved in the subdirectory\n\n"
                + str(path_documents)
                + "\n\nof the input directory\n\n"
                + inputDir
            )

    logger.info("Document titles" + msgString)
    # always open outputDir
    IO_files_util.openExplorer(window, head)

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running the newspaper titles function at",
        True,
        "",
        True,
        startTime,
        False,
    )


# non-ASCII apostrophes and quotes (e.g., those coming from Windows Words) will show up in a csv file (not in Excel or Mac) as weird characters
# although they do not break any script coode
# % will break the CoreNLP code
# The reasons are explained here: https://docs.oracle.com/javase/8/docs/api/java/net/URLDecoder.html
#   The character "%" is allowed but is interpreted as the start of a special escaped sequence.
# Needs special handling https://stackoverflow.com/questions/6067673/urldecoder-illegal-hex-characters-in-escape-pattern-for-input-string
# https://stackoverflow.com/questions/7395789/replacing-a-weird-single-quote-with-blank-string-in-python
def convert_2_ASCII(window, inputFilename, inputDir, outputDir, configFileName):
    import file_filename_util

    result = file_filename_util.backup_files(
        inputFilename, inputDir, "Convert non-ASCII quotes", ".txt", configFileName
    )
    if not result:
        return False

    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )
    Ndocs = len(inputDocs)
    index = 0
    if Ndocs == 0:
        return
    result = IO_user_interface_util.input_output_save("Convert apostrophes/quotes/%")
    if not result:
        return False

    docError = 0
    IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running characters conversion at",
        True,
        "",
        True,
        "",
        True,
    )
    for doc in inputDocs:
        index = index + 1
        head, tail = os.path.split(doc)
        logger.info("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
        with open(doc, "r+", encoding="utf_8", errors="ignore") as file:
            fullText = file.read()
            # https://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
            # if u"\u2018" in fullText:
            # if u"\u2019" in fullText:
            # if u"\u201C" in fullText:
            # if u"\u201D" in fullText:
            if (
                ("%" in fullText)
                or ("\u2018" in fullText)
                or ("\u2019" in fullText)
                or ("\u201c" in fullText)
                or ("\u201d" in fullText)
            ):
                # u0027 apostrophe
                fullText = str(fullText).replace("%", " percent")  # left single quote
                fullText = str(fullText).replace("\u2018", "\u0027")  # left single quote
                fullText = str(fullText).replace("\u2019", "\u0027")  # right single quote
                fullText = str(fullText).replace("\u201c", '"')  # left double quote
                fullText = str(fullText).replace("\u201d", '"')  # right double quote
                docError = docError + 1
                file.seek(0)
                file.write(fullText)
                file.close()

    if docError > 0:
        if docError == 1:
            logger.info(
                "Non-ASCII punctuations converted"
                + str(Ndocs)
                + " document(s) processed.\n\n"
                + str(docError)
                + " document was edited to convert non-ASCII apostrophes and/or quotes and % to percent.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE."
            )
        else:
            logger.info(
                "Non-ASCII punctuations converted"
                + str(Ndocs)
                + " document(s) processed.\n\n"
                + str(docError)
                + " documents were edited to convert non-ASCII apostrophes and/or quotes and % to percent.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILES."
            )
    else:
        logger.info(
            "Non-ASCII punctuations converted"
            + str(Ndocs)
            + " document(s) processed.\n\nNo documents were found with non-ASCII apostrophes or quotes and % to percent."
        )
    return True


# TODO to be completed w/o opening and closing the txt file for every string processed
# Finished
# def find_replace_string_csvINPUT(window, inputFilename_txt, inputFilename_csv, outputDir, openOutputFiles):
# 	except:
# 		mb.showwarning(title='CSV Spelling File',
# 					   message='Please, select a csv file with spelling correction information, or check the headers of that csv file for Original and Corrected')
# 		print(
# 			"Please select a csv file with spelling correction information, or check the header of that csv file for Original and Corrected")

# 	# loop through input spelling csv file for each spelling error to replaced
# 	with open(inputFilename_txt, 'r+',encoding='utf_8',errors='ignore') as file:
# 	for i in range(l):
# 		if corrected[i] != '':
# # 			find_replace_string(window, inputFilename_txt, inputDir, outputDir, openOutputFiles,
# # 												  string_IN=original[i], string_OUT=corrected[i])

# 		if (string_IN in fullText):


def find_replace_string(
    window,
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    openOutputFiles=True,
    string_IN=None,
    string_OUT=None,
    silent=False,
):
    # edited by Claude Hu 02/2021
    # string_IN=[],string_OUT=[], in the form as list so that running this function can finish replacement of multiple strings without open one file repetitively
    import file_filename_util

    if string_OUT is None:
        string_OUT = []
    if string_IN is None:
        string_IN = []
    result = file_filename_util.backup_files(inputFilename, inputDir, "Find and replace string", ".txt", configFileName)
    if not result:
        return

    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )
    filesToOpen = []
    Ndocs = len(inputDocs)
    index = 0
    filesToOpen = []
    result = IO_user_interface_util.input_output_save("Find & Replace")
    if not result:
        return

    if string_IN == []:  # if string_IN empty, string_IN and string_OUT will be typed in
        string_in, string_out = GUI_IO_util.enter_value_widget(
            "Enter the FIND & REPLACE strings (CASE SENSITIVE)",
            "Find",
            2,
            "",
            "Replace",
            "",
        )

        # put input strings into list so that they can be processed
        string_IN = [string_in]
        string_OUT = [string_out]
    elif len(string_IN) != len(
        string_OUT
    ):  # make sure the list of FIND strings and REPLACE strings have same length, so that each can be matched
        logger.info(
            "Different number of FIND & REPLACE strings, The Find & Replace string function requires same number of FIND & REPLACE strings."
        )
        return
    if string_IN == []:  # if still empty
        logger.info(
            "Missing string, The Find & Replace string function requires a non-empty FIND string.\n\nPlease, enter the FIND string and try again."
        )
        return

    string_count = len(string_IN)
    docError = 0
    indexSV = 0
    changed_values = []
    for doc in inputDocs:
        index = index + 1
        head, tail = os.path.split(doc)
        logger.info("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)

        with open(doc, "r+", encoding="utf_8", errors="ignore") as file:
            fullText = file.read()
            # process the range of words when coming with the values in a csv file
            for i in range(string_count):
                if str(string_IN[i]) in str(fullText):
                    # # use regular expression replace to check for distinct words (e.g., he not in held)
                    # \b beginning and ending of word
                    # \w word character including numbers and characters
                    fullText = re.sub(
                        rf"\b(?=\w){str(string_IN[i])}\b(?!\w)",
                        str(string_OUT[i]),
                        fullText,
                    )
                    # fullText = re.sub(rf”(?<=\w) {str(string_IN[i])} (?<=\W)”, str(string_OUT[i]), fullText)
                    if index != indexSV:
                        docError = docError + 1
                        indexSV = index
                    file.seek(0)
                    # clear the input file; for some bizarre reason it appends the search word otherwise
                    file.truncate(0)
                    file.write(fullText)
                    changed_values.append(
                        [
                            [
                                string_IN[i],
                                string_OUT[i],
                                index,
                                IO_csv_util.dressFilenameForCSVHyperlink(doc),
                            ]
                        ]
                    )
            file.close()

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, ".csv", "find_replace")
    header = ["Find string", "Replace string", "Document ID", "Document"]
    changed_values.insert(0, header)
    IO_error = IO_csv_util.list_to_csv(window, changed_values, outputFilename)

    if docError > 0:
        if len(string_IN) == 1 and docError == 1:  # if only one FIND string, it can be typed in the message box
            if not silent:
                logger.info(
                    "String edit"
                    + str(Ndocs)
                    + " document(s) processed.\n\n"
                    + str(docError)
                    + " document was edited to replace the string "
                    + str(string_IN[0])
                    + " with the string "
                    + str(string_OUT)
                    + "\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE."
                )
            else:
                logger.info(
                    str(Ndocs)
                    + " document(s) processed.\n\n"
                    + str(docError)
                    + " document was edited to replace the string "
                    + str(string_IN[0])
                    + " with the string "
                    + str(string_OUT[0])
                    + "\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE."
                )
        else:  # when the length of FIND / REPLACE strings > 1, no actual string will be typed in the message box or printout information
            if not silent:
                logger.info(
                    "String edit"
                    + str(Ndocs)
                    + " document(s) processed.\n\n"
                    + str(docError)
                    + " document(s) edited replacing strings.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE(S)."
                )
            else:
                logger.info(
                    str(Ndocs)
                    + " document(s) processed.\n\n"
                    + str(docError)
                    + " document(s) edited replacing strings.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE(S)."
                )
    else:
        if not silent:
            logger.info(
                title="String edit"
                + str(Ndocs)
                + " document(s) processed.\n\nNo documents were found with the input string(s)."
            )
        else:
            logger.info(str(Ndocs) + " document(s) processed but zero input string(s) found.")

    if not IO_error:
        filesToOpen.append(outputFilename)
