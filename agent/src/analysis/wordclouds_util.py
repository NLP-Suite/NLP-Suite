# written by Cynthia Dong November 2019
# edited by Tony Chen Gu Spring 2022
# ported to the headless web agent June 2026: tkinter/GUI dependencies removed,
#   stanza models are pre-downloaded in the Docker image (see agent/Dockerfile)

import csv
import logging
import os
from collections import Counter, defaultdict

import matplotlib

matplotlib.use("Agg")  # headless container: no display
import IO_files_util
import IO_user_interface_util
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from wordcloud import STOPWORDS, WordCloud

# The script uses Andreas Christian Mueller WordCloud package
# https://amueller.github.io/word_cloud/

logger = logging.getLogger(__name__)


# font directories searched per platform; the agent normally runs in a Linux container
def get_font_dirs():
    candidates = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
        "C:/Windows/Fonts",
    ]
    return [d for d in candidates if os.path.isdir(d)]


def get_font_list():
    # 'Default' means no font_path is passed to WordCloud, which then uses its bundled font
    font_list = ["Default"]
    for font_dir in get_font_dirs():
        for _root, _dirs, files in os.walk(font_dir):
            for name in files:
                if name.lower().endswith((".ttf", ".otf")):
                    font_list.append(os.path.splitext(name)[0])
    return font_list


# when users select a font, search every font directory for a matching .ttf/.otf file
# returns the FULL path (WordCloud's font_path opens the file directly);
# None for 'Default' or when no file matches, falling back to the bundled font
def get_font_path(font):
    if not font or font == "Default":
        return None
    for font_dir in get_font_dirs():
        for root, _dirs, files in os.walk(font_dir):
            for name in files:
                if name.lower().endswith((".ttf", ".otf")) and name[: len(font)] == font:
                    return os.path.join(root, name)
    logger.warning("Font '%s' not found on this machine; using the default WordCloud font", font)
    return None


# Added by Tony
# change the transparent pixel to white
# user could use a website such as https://www.remove.bg/ to remove the background
def changeTransparentToWhite(img):
    """
    :param img: the Image to be changed
    :return: the Image with transparent pixel changed to white
    """
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[3] == 0:  # if alpha value is zero, it is transparent
            newData.append((255, 255, 255, 255))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def changeWhiteToTransparent(img):
    """
    :param img: the Image to be changed
    :return: the Image with white pixel changed to transparent"""
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:  # if it is white
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


class GroupedColorFunc:
    """Create a color function object which assigns DIFFERENT SHADES of
    specified colors to certain words based on the color to words mapping.

    Parameters
    ----------
    color_to_words : dict(str -> list(str))
      A dictionary that maps a color to the list of words.

    default_color : str
      Color that will be assigned to a word that's not a member
      of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (self.get_single_color(color), set(words)) for (color, words) in color_to_words.items()
        ]

        self.default_color_func = self.get_single_color(default_color)

    def get_single_color(self, color):
        color = color[1:-1]
        color_list = color.split(", ")
        return f"rgb({int(color_list[0]):.0f}, {int(color_list[1]):.0f}, {int(color_list[2]):.0f})"

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(color_func for (color_func, words) in self.color_func_to_words if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)


def get_wordcloud_title(inputFilename, inputDir, wordcloud_title):
    if wordcloud_title == "":
        if inputFilename != "":
            head, tail = os.path.split(inputFilename)
        else:
            head, tail = os.path.split(inputDir)
        wordcloud_title = "Wordcloud for " + str(tail)
    return wordcloud_title


# CYNTHIA: wordcloud function particularly designed for SVO
# collocations set to False to avoid repetition of words
# wordcloud_title = 'Wordcloud of Subject (red), Verb (blue), Object (green)'
def SVOWordCloud(svoFile, inputFilename, outputDir, transformed_image_mask, wordcloud_title, prefer_horizontal):
    wordcloud_title = get_wordcloud_title(inputFilename, "", wordcloud_title)

    # read SVO result in
    svo_df = pd.read_csv(svoFile, encoding="utf-8", on_bad_lines="skip")
    svo_df = svo_df.fillna("")
    words_list = []
    # RGB color codes: red for S, blue for V, green for O
    red_code = "(250, 0, 0)"
    blue_code = "(0, 0, 250)"
    green_code = "(0, 250, 0)"
    default_code = "(169, 169, 169)"  # grey
    color_list = {red_code: [], blue_code: [], green_code: []}
    for _, row in svo_df.iterrows():
        if row["Subject (S)"] != "":
            # check if the strings contains special character
            words_list.append(
                " ".join(["".join(filter(str.isalnum, s)) for s in row["Subject (S)"].lower().split(" ")])
            )
            color_list[red_code].append(
                " ".join(["".join(filter(str.isalnum, s)) for s in row["Subject (S)"].lower().split(" ")])
            )
        if row["Verb (V)"] != "":
            words_list.append(
                " " + (" ".join(["".join(filter(str.isalnum, s)) for s in row["Verb (V)"].lower().split(" ")]))
            )
            color_list[blue_code].append(
                " " + (" ".join(["".join(filter(str.isalnum, s)) for s in row["Verb (V)"].lower().split(" ")]))
            )
        if row["Object (O)"] != "":
            words_list.append(
                (" ".join(["".join(filter(str.isalnum, s)) for s in row["Object (O)"].lower().split(" ")])) + " "
            )
            color_list[green_code].append(
                (" ".join(["".join(filter(str.isalnum, s)) for s in row["Object (O)"].lower().split(" ")])) + " "
            )
    words_count_dict = Counter(words_list)
    max_words = 1000  # TODO MINO: make max_words bigger to include generally lower frequency "Object (O)" words
    if len(transformed_image_mask) != 0:
        wc = WordCloud(
            width=800,
            height=800,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            collocations=False,
            mask=transformed_image_mask,
            contour_width=3,
            contour_color="firebrick",
            background_color="white",
        ).generate_from_frequencies(words_count_dict)
    else:
        wc = WordCloud(
            width=800,
            height=800,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            collocations=False,
            contour_width=3,
            background_color="white",
        ).generate_from_frequencies(words_count_dict)
    grouped_color_func = GroupedColorFunc(color_list, default_code)
    wc.recolor(color_func=grouped_color_func)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wc, interpolation="bilinear")
    plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
    plt.axis("off")
    output_file_name = IO_files_util.generate_output_file_name(inputFilename, "", outputDir, ".png", "WC", "img")
    wc.to_file(output_file_name)
    plt.close("all")
    return output_file_name


# for label separate column with separate color only
def processColorList(currenttext, lowercase, color_to_words, csvField_color_list, myfile):
    cur_list = []
    column_color = {}

    for item in csvField_color_list:
        if item != "|":
            cur_list.append(item)
        else:
            for key in cur_list[:-1]:
                column_color[key] = cur_list[-1]
            cur_list = []

    reader = csv.DictReader(myfile)  # read rows into a dictionary format
    for row in reader:  # read a row as {column name1: color value1, column name2: color value2,...}
        for k, v in row.items():  # go over each column name and color value
            # in Excel, the first column header contains non utf encoding ﻿ and must be removed
            #   or the first column would never be processed
            k = k.replace("﻿", "")
            if lowercase:
                v = v.lower()
            if k in column_color:
                if " " in v:
                    words = ["".join(filter(str.isalnum, s)) for s in v.split(" ")]
                else:
                    words = ["".join(filter(str.isalnum, v))]

                color = column_color[k]
                color_index = list(column_color.values()).index(color)  # Find the index of the color
                suffix = "_" * (color_index + 1)  # Create the suffix based on the color's position
                color_to_words[color] += [word + suffix for word in words]

                # Update currenttext with the suffixed word(s)
                currenttext += " ".join([word + suffix for word in words]) + " "

    return currenttext, color_to_words


def display_wordCloud_sep_color(
    inputFilename,
    inputDir,
    outputDir,
    text,
    color_to_words,
    transformed_image_mask,
    max_words,
    collocation,
    wordcloud_title,
    prefer_horizontal,
    bg_image=None,
    bg_image_flag=False,
    font=None,
):
    wordcloud_title = get_wordcloud_title(inputFilename, inputDir, wordcloud_title)

    # stopwords dealt with in main function
    stopwords = ""
    c_wid = 0 if bg_image_flag else 3

    if len(transformed_image_mask) != 0:
        wc = WordCloud(
            collocations=collocation,
            width=800,
            height=800,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            stopwords=stopwords,
            mask=transformed_image_mask,
            contour_width=c_wid,
            contour_color="firebrick",
            background_color="white",
            font_path=font,
        ).generate(text)
    else:
        wc = WordCloud(
            collocations=collocation,
            width=800,
            height=800,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            stopwords=stopwords,
            contour_width=c_wid,
            background_color="white",
            font_path=font,
        ).generate(text)
    default_color = "(169, 169, 169)"  # dark grey; black is 0,0,0
    grouped_color_func = GroupedColorFunc(color_to_words, default_color)
    wc = wc.recolor(color_func=grouped_color_func)
    # strip the per-color '_' suffixes added by processColorList before rendering
    w = []
    for item in wc.layout_:
        x = item[0]
        x = (x[0].replace("_", ""), x[1])
        w.append((x, item[1], item[2], item[3], item[4]))
    wc.layout_ = w

    plt.figure(figsize=(8, 8), facecolor=None)
    # name per-document outputs after the document, not the directory, so they don't overwrite each other
    output_file_name = IO_files_util.generate_output_file_name(
        inputFilename, "" if inputFilename else inputDir, outputDir, ".png", "WC", "img"
    )
    if bg_image_flag and bg_image is not None:
        img = changeWhiteToTransparent(wc.to_image())
        img = img.resize(bg_image.size)
        img = Image.alpha_composite(bg_image, img)
        plt.imshow(img, interpolation="bilinear")
        plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
        plt.axis("off")
        # title must be set before layout
        plt.tight_layout(pad=0)
        # Save the image in the output folder
        plt.figure()
        plt.axis("off")
        plt.imshow(img, interpolation="nearest")
        plt.savefig(output_file_name, bbox_inches="tight", pad_inches=0, format="png", dpi=300)
    else:
        plt.imshow(wc.to_image(), interpolation="bilinear")
        plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
        plt.axis("off")
        plt.savefig(output_file_name)
    plt.close("all")
    return output_file_name


# called by python_wordCloud
# inputFilename is only used to create an appropriate name for the image file;
# the texts to be processed is contained in textToProcess
def display_wordCloud(
    inputFilename,
    inputDir,
    outputDir,
    textToProcess,
    doNotListIndividualFiles,
    transformed_image_mask,
    stopwords,
    collocation,
    wordcloud_title,
    prefer_horizontal,
    bg_image=None,
    bg_image_flag=True,
    font=None,
    max_words=100,
):
    if textToProcess == "":
        return
    c_wid = 0 if bg_image_flag else 3
    if len(transformed_image_mask) != 0:
        wordcloud = WordCloud(
            width=800,
            height=800,
            background_color="white",
            max_words=max_words,
            mask=transformed_image_mask,
            prefer_horizontal=prefer_horizontal,
            stopwords=stopwords,
            contour_width=c_wid,
            contour_color="firebrick",
            collocations=collocation,
            font_path=font,
        ).generate(textToProcess)
    else:
        wordcloud = WordCloud(
            width=800,
            height=800,
            background_color="white",
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            stopwords=stopwords,
            contour_width=c_wid,
            collocations=collocation,
            font_path=font,
        ).generate(textToProcess)
    wordcloud_title = get_wordcloud_title(inputFilename, inputDir, wordcloud_title)
    # name per-document outputs after the document, not the directory, so they don't overwrite each other
    output_file_name = IO_files_util.generate_output_file_name(
        inputFilename, "" if inputFilename else inputDir, outputDir, ".png", "WC", "img"
    )
    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    if bg_image_flag and bg_image is not None:
        img = changeWhiteToTransparent(wordcloud.to_image())
        img = img.resize(bg_image.size)
        img = Image.alpha_composite(bg_image, img)
        plt.imshow(img, interpolation="bilinear")
        plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
        plt.axis("off")
        # title must be set before layout
        plt.tight_layout(pad=0)
        # Save the image in the output folder
        plt.figure()
        plt.imshow(img, interpolation="nearest")
        plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
        plt.axis("off")
        plt.savefig(output_file_name, bbox_inches="tight", pad_inches=0, format="png", dpi=300)
    else:
        plt.title(wordcloud_title, fontsize=14, fontweight="bold", pad=20)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        if len(output_file_name) > 255:
            plt.close("all")
            return
        plt.savefig(output_file_name, bbox_inches="tight", pad_inches=0, format="png", dpi=300)
    plt.close("all")
    return output_file_name


# check if file is empty
# 2 returned boolean
#   the first one tells the caller that the run MUST stop;
#   the second that a file is empty and processing moves to the next file
def check_file_empty(currenttext, inputFilename, nDocs, NumEmptyDocs):
    if len(currenttext) == 0:
        NumEmptyDocs = NumEmptyDocs + 1
        if nDocs == 1:
            raise RuntimeError("The file " + inputFilename + " is empty. Please, use another file and try again.")
        logger.warning("The file %s is empty.", inputFilename)
        return False, True, NumEmptyDocs
    else:
        return False, False, NumEmptyDocs


# Modified by Tony 01/23/2022  add bg_image and bg_image_flag
def processCsvColumns(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    csvField_color_list,
    doNotListIndividualFiles,
    max_words,
    lowercase,
    collocation,
    wordcloud_title,
    prefer_horizontal,
    bg_image=None,
    bg_image_flag=False,
):
    transformed_image_mask = []
    currenttext = ""
    tempOutputfile = ""
    color_to_words = defaultdict(list)
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        if len(csvField_color_list) != 0:
            # process csvField_color_list
            currenttext, color_to_words = processColorList(
                currenttext, lowercase, color_to_words, csvField_color_list, myfile
            )
            if currenttext != "":
                tempOutputfile = display_wordCloud_sep_color(
                    inputFilename,
                    inputDir,
                    outputDir,
                    currenttext,
                    color_to_words,
                    transformed_image_mask,
                    max_words,
                    collocation,
                    wordcloud_title,
                    prefer_horizontal,
                    bg_image=bg_image,
                    bg_image_flag=bg_image_flag,
                )
    return tempOutputfile


def save_wordcloud(
    filesToOpen,
    differentPOS_differentColors,
    inputFilename,
    inputDir,
    outputDir,
    doNotListIndividualFiles,
    textToProcess,
    color_to_words,
    transformed_image_mask,
    stopwords,
    collocation,
    wordcloud_title,
    prefer_horizontal,
    img,
    use_contour_only,
    font,
    max_words,
):
    if differentPOS_differentColors:
        tempOutputfile = display_wordCloud_sep_color(
            inputFilename,
            inputDir,
            outputDir,
            textToProcess,
            color_to_words,
            transformed_image_mask,
            max_words=max_words,
            collocation=collocation,
            wordcloud_title=wordcloud_title,
            prefer_horizontal=prefer_horizontal,
            bg_image=img,
            bg_image_flag=use_contour_only,
            font=font,
        )
    else:
        # when stopwords = '' stopwords will be INCLUDED in the output visual
        tempOutputfile = display_wordCloud(
            inputFilename,
            inputDir,
            outputDir,
            textToProcess,
            doNotListIndividualFiles,
            transformed_image_mask,
            stopwords,
            collocation,
            wordcloud_title,
            prefer_horizontal,
            bg_image=img,
            bg_image_flag=use_contour_only,
            font=font,
            max_words=max_words,
        )
    if tempOutputfile is not None:
        filesToOpen.append(tempOutputfile)
    return filesToOpen


# TOP-level function for wordclouds
# called by wordcloud_visual.run_wordcloud
def python_wordCloud(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    selectedImage,
    use_contour_only,
    wordcloud_title,
    prefer_horizontal,
    font,
    max_words,
    lemmatize,
    exclude_stopwords,
    exclude_punctuation,
    lowercase,
    differentPOS_differentColors,
    differentColumns_differentColors,
    csvField_color_list,
    doNotListIndividualFiles,
    openOutputFiles,
    collocation,
):
    # https://www.geeksforgeeks.org/generating-word-cloud-python/
    filesToOpen = []

    if differentColumns_differentColors or inputFilename[-3:] == "csv":
        fileType = ".csv"
    else:
        fileType = ".txt"

    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType, silent=False, configFileName=configFileName
    )
    nDocs = len(inputDocs)
    if nDocs == 0:
        return filesToOpen

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="wordcloud", silent=True
    )
    if outputDir == "":
        return filesToOpen

    font = get_font_path(font)

    transformed_image_mask = []

    use_contour_only = not use_contour_only

    if prefer_horizontal == 0:
        prefer_horizontal = 0.9
    else:
        prefer_horizontal = 1

    img = None

    if len(selectedImage) != 0:
        # In order to create a shape for your wordcloud, first, you need to find a PNG file to become the mask.
        # The way the masking functions works is that it requires all white part of the mask should be 255 not 0
        #   (integer type). This value represents the "intensity" of the pixel. Values of 255 are pure white,
        #   whereas values of 1 are black.
        try:
            img = Image.open(selectedImage)
        except Exception as exc:
            raise RuntimeError(
                "An error was encountered opening the input image file "
                + selectedImage
                + ". Please, use another image file and try again."
            ) from exc
        img = changeTransparentToWhite(img)
        image_mask = np.array(img)
        numberImages = len(image_mask.shape)
        if numberImages > 3:
            return filesToOpen
        transformed_image_mask = image_mask

    # can only process a single conll table or a csv file (e.g., SVO results where the user selects the columns to be used for color display)
    if len(inputDir) > 0:
        fileType = ".txt"

    # RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, GREY for ADVERBS
    #   YELLOW for anything else; no longer used
    # RGB color codes
    red_code = "(250, 0, 0)"
    blue_code = "(0, 0, 250)"
    green_code = "(0, 250, 0)"
    grey_code = "(80, 80, 80)"
    yellow_code = "(255, 255, 0)"
    color_to_words = {
        red_code: [],  # red/nouns
        blue_code: [],  # blue/verbs
        green_code: [],  # green/adjs
        grey_code: [],  # grey/advs
        yellow_code: [],  # all other word POS types; no longer used
    }
    combinedtext = ""
    textToProcess = ""
    stopwords = ""
    NumEmptyDocs = 0
    i = 0
    startTime = ""

    runStanza = False
    stannlp = None
    if fileType == ".txt":
        # imported here so that the csv/CoNLL path works without stanza installed
        from model_cache import get_stanza_pipeline

        # always tokenize to convert each token to lowercase
        #   to avoid the same improper word to appear with lower and upper case at the beginning of a sentence
        runStanza = True
        processors = "tokenize, mwt"
        if lemmatize:
            processors = processors + ", lemma"
        if exclude_punctuation or differentPOS_differentColors:
            processors = processors + ", pos"
        stannlp = get_stanza_pipeline(lang="en", processors=processors)

    if runStanza:
        startTime = IO_user_interface_util.timed_alert(
            3000,
            "Running STANZA & wordcloud",
            "Started running STANZA and wordcloud at",
            True,
            "Please, be patient. Depending upon the number of documents processed this may take a few minutes.",
            True,
            "",
            False,
        )

    # with stopwords = '' stopwords will be included in the output visual
    # do not process stopwords when processing by POS tag value
    if exclude_stopwords or differentPOS_differentColors:
        stopwords = set(STOPWORDS)  # STOPWORDS are all lowercase, so any exclusion will have to be converted

    for doc in inputDocs:
        i = i + 1
        textToProcess = ""
        head, tail = os.path.split(doc)
        logger.info("Processing file %d/%d %s", i, nDocs, tail)
        if doc[-4:] == ".csv":
            startTime = IO_user_interface_util.timed_alert(
                3000,
                "Running wordcloud on csv file",
                "Started running wordcloud at",
                True,
                "Please, be patient. Depending upon the number of documents processed this may take a few minutes.",
                True,
                "",
                False,
            )
            import CoNLL_util

            # check that input file is a CoNLL table
            if not CoNLL_util.check_CoNLL(doc, True):
                # not a CoNLL table: process the csv columns selected by the user, each in its own color
                if differentColumns_differentColors:
                    tempOutputfile = processCsvColumns(
                        doc,
                        inputDir,
                        outputDir,
                        openOutputFiles,
                        csvField_color_list,
                        doNotListIndividualFiles,
                        max_words,
                        lowercase,
                        collocation,
                        wordcloud_title,
                        prefer_horizontal,
                        bg_image=img,
                        bg_image_flag=use_contour_only,
                    )
                    if tempOutputfile != "":
                        filesToOpen.append(tempOutputfile)
            else:
                # processing a CoNLL table with Form, Lemma, POS columns
                try:
                    df = pd.read_csv(doc, encoding="utf-8", on_bad_lines="skip")
                    df = df.dropna(subset=["Form", "Lemma", "POS"])
                    text_words = []
                    for row in df.itertuples():
                        word = row.Lemma if lemmatize else row.Form
                        pos = row.POS
                        pos_prefix = pos[:2] if len(pos) >= 2 else pos
                        color = None
                        if pos_prefix.startswith("VB"):
                            color = blue_code
                        elif pos_prefix.startswith("NN"):
                            color = red_code
                        elif pos_prefix == "JJ":
                            color = green_code
                        elif pos_prefix == "RB":
                            color = grey_code
                        if color:
                            color_to_words[color].append(word)
                            text_words.append(str(word))
                    textToProcess = " ".join(text_words)
                except Exception as exc:
                    raise RuntimeError(
                        doc
                        + " is not a CoNLL table. Please, select in input a proper csv CoNLL file with Form, Lemma, and POS columns and try again."
                    ) from exc

        elif doc[-4:] == ".txt":
            with open(doc, encoding="utf-8", errors="ignore") as myfile:
                textToProcess = ""
                currenttext = myfile.read()
                # check for empty file
                error, error2, NumEmptyDocs = check_file_empty(currenttext, doc, nDocs, NumEmptyDocs)
                if error:
                    return filesToOpen
                if error2:
                    continue
                if runStanza:
                    textToProcess = ""
                    annotated = stannlp(currenttext)
                    for sent_id in range(len(annotated.sentences)):
                        for word in annotated.sentences[sent_id].words:
                            if word.text.lower() == "'s" or word.text.lower() == "’s" or word.text.lower() == "s":
                                continue  # do not process the s of a saxon genitive
                            # RED for NOUNS, BLUE for VERBS, GREEN for ADJECTIVES, GREY for ADVERBS
                            if lemmatize:
                                word_str = word.lemma
                                # if no lemma, use form value
                                if word_str is None:
                                    word_str = word.text
                            else:
                                word_str = word.text
                            if exclude_stopwords:
                                if (
                                    word_str.lower() in stopwords
                                ):  # STOPWORDS are all lowercase, so any exclusion will have to be converted
                                    continue  # do not process stopwords & punctuation marks
                            # convert to lower case for same improper words that may appear after a full stop
                            if lowercase:
                                if word_str is not None:
                                    word_str = word_str.lower()
                            if exclude_punctuation:
                                if word.pos == "PUNCT":
                                    continue  # do not process punctuation marks
                            if word.pos == "NOUN" or word.pos == "PROPN":
                                color_to_words[red_code].append(word_str)
                            elif word.pos == "VERB":
                                color_to_words[blue_code].append(word_str)
                            elif word.pos == "ADJ":
                                color_to_words[green_code].append(word_str)
                            elif word.pos == "ADV":
                                color_to_words[grey_code].append(word_str)
                            if differentPOS_differentColors:
                                if (
                                    word.pos != "NOUN"
                                    and word.pos != "PROPN"
                                    and word.pos != "VERB"
                                    and word.pos != "ADJ"
                                    and word.pos != "ADV"
                                ):
                                    continue

                            if word_str is not None:
                                textToProcess = textToProcess + " " + word_str

                    if len(textToProcess) == 0:
                        textToProcess = currenttext

            if not doNotListIndividualFiles:
                filesToOpen = save_wordcloud(
                    filesToOpen,
                    differentPOS_differentColors,
                    doc,
                    inputDir,
                    outputDir,
                    doNotListIndividualFiles,
                    textToProcess,
                    color_to_words,
                    transformed_image_mask,
                    stopwords,
                    collocation,
                    wordcloud_title,
                    prefer_horizontal,
                    img,
                    use_contour_only,
                    font,
                    max_words,
                )
                # write an output txt file that can be used for internet wordclouds services
                if (lemmatize or exclude_stopwords) and filesToOpen:
                    with open(filesToOpen[-1][:-8] + ".txt", "w", encoding="utf-8", errors="ignore") as f:
                        f.write(textToProcess)
        # accumulate text from both the txt and CoNLL-csv paths for the combined wordcloud
        combinedtext = combinedtext + textToProcess

    # when processing individual files in a directory combinedtext will be empty
    if combinedtext != "":
        if len(inputDir) > 0:
            doc = ""  # doc would otherwise have the value of the last document read in the inputDir
        filesToOpen = save_wordcloud(
            filesToOpen,
            differentPOS_differentColors,
            doc,
            inputDir,
            outputDir,
            doNotListIndividualFiles,
            combinedtext,
            color_to_words,
            transformed_image_mask,
            stopwords,
            collocation,
            wordcloud_title,
            prefer_horizontal,
            img,
            use_contour_only,
            font,
            max_words,
        )

        # write an output txt file that can be used for internet wordclouds services
        if (lemmatize or exclude_stopwords) and filesToOpen:
            with open(filesToOpen[-1][:-8] + ".txt", "w", encoding="utf-8", errors="ignore") as f:
                f.write(combinedtext)
            nDocsRewritten = 1
            if not doNotListIndividualFiles:
                nDocsRewritten = nDocs + 1
            IO_user_interface_util.timed_alert(
                4000,
                "Python wordclouds txt files output",
                "The Python 3 wordclouds algorithm has produced "
                + str(nDocsRewritten)
                + " txt file(s) without stopwords, punctuation, and with lemmatized words, depending upon your selected filter options.\n\nYou will find the file(s) in your output directory.\n\nYou can use the file(s) to produce wordclouds using any of the internet wordcloud services.",
            )

    if NumEmptyDocs > 0:
        if NumEmptyDocs == nDocs:
            raise RuntimeError(
                "All "
                + str(NumEmptyDocs)
                + " txt files in your input directory "
                + str(inputDir)
                + " are empty. Please, check your directory and try again."
            )
        logger.warning(
            "%d file(s) empty in the input directory %s. Empty file(s) listed above; please, make sure to check the file(s) content.",
            NumEmptyDocs,
            inputDir,
        )

    IO_user_interface_util.timed_alert(
        3000, "Analysis end", "Finished running wordcloud at", True, "", True, startTime, False
    )
    return filesToOpen
