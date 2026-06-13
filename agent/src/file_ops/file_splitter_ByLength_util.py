import logging

"""
Author: Jack Hester, Spring 2019
Edited: Cynthia Dong, Roberto Franzosi, Spring 2020

"""

import os
import shutil
import sys

import IO_user_interface_util
import reminders_util

logger = logging.getLogger(__name__)


# Jack Hester
# the function is used to split a document longer than 100K characters since Stanford CoreNLP can only deal with text files of 100K characters max.
def splitAt(text, index):
    # consider ." !" ?" for speech
    #   otherwise you end up with an unaccounted " in the next chunk of text
    limit = sys.getrecursionlimit()
    first_limit = limit
    while True:
        try:
            if text[index] in [".", "!", "?"]:
                return index
            else:
                return splitAt(text, index - 1)
        except RecursionError:
            IO_user_interface_util.timed_alert(
                4000,
                "Warning",
                "The file being split is a VERY large ("
                + str(len(text))
                + " characters) file.\n\nTo deal with such large a file, the system recursion limit will be temporarily doubled, then restored to its original limit.",
                False,
                "",
                True,
                "",
                False,
            )
            limit = limit * 2
            sys.setrecursionlimit(limit)
    sys.setrecursionlimit(first_limit)


# Jack Hester
# edited by Cynthia Dong and Roberto Franzosi
# the function is used to check the lenght of a document
#   and split the document
#   since Stanford CoreNLP can only deal with text files of 100K characters max.
#   90000 in number of characters
# input_path is a path where files are store
# files is a list  ['C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs/The Three Little Pigs.txt']
# filesToReturn is also a list ['C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs\\split_files\\The Three Little Pigs_1.txt', 'C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs\\split_files\\The Three Little Pigs_2.txt']


# filename contains file WITH path
# called by Stanford_CoreNL_parser
# called by annotators DBpedia, YAGO utils
#   In DBpedia and YAGO the temporary split files are deleted
def splitDocument_byLength(config_filename, filename_path, output_path="", maxLength=90000, inWords=False):
    # a new folder is created in output
    #   as a subfolder of the input folder and/or file
    #   the subfolder will be named split_files_9000_filename (no extension)
    filesToReturn = []

    head, filename = os.path.split(filename_path)
    # Stanford_CoreNLP_parser_util does not pass the output dir
    if output_path == "":
        output_path = head
    new_splitFiles_folder = output_path + os.sep + "split_files_" + str(maxLength) + "_" + filename[:-4]
    with open(filename_path, encoding="utf-8", errors="ignore") as F:
        text = F.read()
        length = len(text)
        if inWords:
            length = len(text.split())
    F.close()
    if length > maxLength:
        if os.path.exists(new_splitFiles_folder):
            shutil.rmtree(new_splitFiles_folder)
        try:
            os.mkdir(new_splitFiles_folder)
        except Exception as e:
            logger.info("error:  %s", e.__doc__)
        splits = [-1]  # start at -1 not 0 because of +1 later in loop
        if inWords:
            i = maxLength - 5
        else:
            i = maxLength - 2
        while i < length:
            i = splitAt(text, i)
            splits.append(i)
            if inWords:
                i = i + maxLength - 5
            else:
                i = i + maxLength - 2
        splits.append(length - 1)
        for i in range(1, len(splits)):
            # write output file
            fname = os.path.basename(os.path.normpath(filename_path))

            SplitFile = os.path.join(new_splitFiles_folder, fname).split(".txt")[0] + "_" + str(i) + ".txt"
            with open(SplitFile, "w+", newline="", encoding="utf-8", errors="ignore") as sf:
                sf.write(text[splits[i - 1] + 1 : splits[i] + 1])
                filesToReturn.append(SplitFile)
            sf.close()
        head, scriptName = os.path.split(os.path.basename(__file__))
        if (
            "SVO" in config_filename
            or "NER" in config_filename
            or "CoreNLP" in config_filename
            or "coref" in config_filename
        ):
            reminders_util.checkReminder(
                scriptName,
                reminders_util.title_options_CoreNLP_split_files,
                reminders_util.message_CoreNLP_split_files,
                True,
            )
        else:
            reminders_util.checkReminder(
                scriptName,
                reminders_util.title_options_Output_directory_of_split_files,
                reminders_util.message_Output_directory_of_split_files,
                True,
            )
    else:
        filesToReturn.append(filename_path)
    return filesToReturn


# called from file_splitter_main
# a new folder is created in output
#   as a subfolder of the input folder and/or file
#   the subfolder will be named split_files_9000_filename (no extension)
# contrary to the function splitDocument_byLength that carries out
#   making the split_files subdirectory, for this function
#   the creation of the directory is carried out in the calling script
def split_byLength(input_path, filename, output_path, maxLength, inSentence=False):
    from Stanza_functions_util import (
        sent_tokenize_stanza,
        stanzaPipeLine,
        word_tokenize_stanza,
    )

    # inSentence: no incomplete sentence in subfiles
    docname = os.path.split(filename)[1]
    title = docname.partition(".")[0]  # get the title of the file(without path and .txt)
    with open(filename, encoding="utf-8", errors="ignore") as F:
        text = F.read()
        sentences = sent_tokenize_stanza(stanzaPipeLine(text))  # sentnece list of the input txt
    F.close()
    if maxLength > len(word_tokenize_stanza(stanzaPipeLine(text))):
        IO_user_interface_util.timed_alert(
            2000,
            "File split warning",
            "The length of file " + filename + " is less than " + str(maxLength),
        )
        subfile = open(
            output_path + "/" + title + "_1" + ".txt",
            "w",
            encoding="utf-8",
            errors="ignore",
        )
        subfile.write(text)
        return
    splitText = ""
    subfileIndex = 1
    word_count = 0
    for sent in sentences:
        words = word_tokenize_stanza(stanzaPipeLine(sent))
        if word_count + len(words) < maxLength:
            splitText += sent + " "
            word_count += len(words)
        elif word_count + len(words) == maxLength:
            splitText += sent
            subfile = open(
                output_path + "/" + title + "_" + str(subfileIndex) + ".txt",
                "w",
                encoding="utf-8",
                errors="ignore",
            )
            subfile.write(splitText)
            subfileIndex += 1
            splitText = ""
            word_count = 0
        else:
            if inSentence:  # the subfile's word count is less than max limit, but contain no incomplete sentences
                subfile = open(
                    output_path + "/" + title + "_" + str(subfileIndex) + ".txt",
                    "w",
                    encoding="utf-8",
                    errors="ignore",
                )
                subfile.write(splitText)
                subfileIndex += 1
                splitText = sent + " "
                word_count = len(words)
            else:
                diff = maxLength - word_count  # the index of the last word of this subfile in the sentence
                if (
                    words.index(words[diff - 1]) == diff - 1
                ):  # no other same word in the setence or that's the first occurrence of the word
                    splitText += sent.partition(words[diff - 1])[0] + sent.partition(words[diff - 1])[1]
                    subfile = open(
                        output_path + "/" + title + "_" + str(subfileIndex) + ".txt",
                        "w",
                        encoding="utf-8",
                        errors="ignore",
                    )
                    subfile.write(splitText)
                    subfileIndex += 1
                    splitText = sent.partition(words[diff - 1])[2] + " "
                    word_count = len(words) - diff
                else:
                    subsent = ""
                    restsent = sent
                    while (
                        len(word_tokenize_stanza(stanzaPipeLine(text))) <= diff
                    ):  # check each same word until the previous text reached the maxLength
                        subsent += restsent.partition(words[diff - 1])[0] + restsent.partition(words[diff - 1])[1]
                        restsent = restsent.partition(words[diff - 1])[2]
                    subfile = open(
                        output_path + "/" + title + "_" + str(subfileIndex) + ".txt",
                        "w",
                        encoding="utf-8",
                        errors="ignore",
                    )
                    subfile.write(splitText + subsent)
                    subfileIndex += 1
                    splitText = restsent + " "
                    word_count = len(word_tokenize_stanza(stanzaPipeLine(restsent)))

    if len(splitText) > 0:
        subfile = open(
            output_path + "/" + title + "_" + str(subfileIndex) + ".txt",
            "w",
            encoding="utf-8",
            errors="ignore",
        )
        subfile.write(splitText)
