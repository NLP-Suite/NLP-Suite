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

import logging
import re
import string

import IO_csv_util

# not using stanfordcorenlp because it is not recognizing sentiment annotator
from corenlp_json_common import check_sentence_length
from IO_files_util import date_in_filename

logger = logging.getLogger(__name__)


def date_get_tense(norm_date):
    tense = ""
    if (len(norm_date) >= 9 and "PREV" in norm_date) or "OFFSET person_list" in norm_date or "PAST" in norm_date:
        tense = "PAST"
    elif (len(norm_date) >= 6 and "OFFSET" in norm_date) or "FUTURE" in norm_date:
        tense = "FUTURE"
    elif "THIS" in norm_date or "PRESENT" in norm_date:
        tense = "PRESENT"
    elif "NEXT" in norm_date:
        tense = "NEXT"
    else:
        tense = "OTHER"  # TODO separate out days of week, months of year
    return tense


# def date_get_tense(norm_date):


def process_json_normalized_date(config_filename, documentID, document, sentenceID, json, **kwargs):
    logger.info("   Processing Json output file for NER NORMALIZED DATE annotator")
    filename_embeds_date_var = False

    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    temp = []
    for sentence in json["sentences"]:
        complete_sent = ""
        sentenceID = sentenceID + 1
        words = ""
        norm_date = ""
        tid = ""
        info = ""
        for token in sentence["tokens"]:
            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]
            word = token["word"]
            if token["ner"] == "DATE":
                if norm_date == "":
                    norm_date = token["normalizedNER"]
                    try:
                        tid = token["timex"]["tid"]
                    except Exception:
                        logger.info("   tid error")
                        tid = ""
                    info = date_get_info(norm_date)
                    if info == "OTHER":
                        info = date_get_tense(norm_date)
                    words = word + words
                elif token["normalizedNER"] != norm_date:
                    if filename_embeds_date_var:
                        temp = [
                            words,
                            norm_date,
                            tid,
                            info,
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                            date_str,
                        ]
                    else:
                        temp = [
                            words,
                            norm_date,
                            tid,
                            info,
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                        ]
                    result.append(temp)
                    words = word
                    norm_date = token["normalizedNER"]
                    try:
                        tid = token["timex"]["tid"]
                    except Exception:
                        logger.info("   tid error")
                        tid = ""
                    info = date_get_info(norm_date)
                    if info == "OTHER":
                        info = date_get_tense(norm_date)
                    words = word + words
                else:
                    if word in string.punctuation:
                        words = words + word
                    else:
                        words = words + " " + word
            else:
                if words != "" or norm_date != "":
                    if filename_embeds_date_var:
                        temp = [
                            words,
                            norm_date,
                            tid,
                            info,
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                            date_str,
                        ]

                    else:
                        temp = [
                            words,
                            norm_date,
                            tid,
                            info,
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                        ]
                    result.append(temp)
                    words = ""
                    norm_date = ""
                    tid = ""
                    info = ""

        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

    return result


def date_get_info(norm_date):
    norm_date = norm_date.strip()
    tense = "OTHER"
    if norm_date.isdigit() or (norm_date[0] == "-" and norm_date.replace("-", "").isdigit()):
        tense = "YEAR"
    elif norm_date[-2:] == "XX" and (
        norm_date[0:-2].isdigit() or (norm_date[0] == "-" and norm_date[0:-2].replace("-", "").isdigit())
    ):
        tense = "CENTURY"
    elif len(norm_date) == 7 and norm_date[-2:].isdigit() and norm_date[4] == "-":
        tense = "MONTH"
    elif (
        norm_date.replace("-", "").isdigit()
        or norm_date.replace("/", "").isdigit()
        or ("XXXX" in norm_date and norm_date.split("XXXX")[1].replace("-", "").isdigit())
    ):  # (len(norm_date) > 4 and norm_date[0:4] == 'XXXX' and norm_date[4:].replace("-", '').isdigit()):#specific year,month, day
        tense = "DATE"
    elif "WXX" in norm_date or "WE" in norm_date:  # weekdays
        tense = "DAY"
    elif "SP" in norm_date or "SU" in norm_date or "FA" in norm_date or "WI" in norm_date:
        tense = "SEASON"
    return tense


# check if an NER tag is part of a multi-line tag (e.g., for locations, Soviet Union, United States;
#   for PERSON Mao Zedung)
#   when they are, the tokenEnd in current row is equal to tokenBegin of next row


def check_NER_tokenBegin_tokenEnd(NER):
    index = 0
    new_NER = []
    beginToken_currenRow = -1
    currNERtag = ""
    while index < len(NER):
        # NER[index][1] contains the tag value, e.g., PERSON, CITY, ...
        if beginToken_currenRow == -1:
            beginToken_currenRow = NER[index][2]
        endToken_currenRow = NER[index][3]
        NERtag_currenRow = NER[index][1]
        try:
            beginToken_nextRow = NER[index + 1][2]
            NERtag_nextRow = NER[index + 1][1]
        except Exception:
            beginToken_nextRow = None
            NERtag_nextRow = None
        # the NER values but have the same beginning/ending values AND
        #   be of the same tag type (e.g., PERSON)
        #   unless LOCATION is the type; e.g., Denmark Street, is tagged as COUNTRY and LOCATION
        if (
            ((endToken_currenRow == beginToken_nextRow) or (beginToken_nextRow is None))
            and (NERtag_currenRow == NERtag_nextRow)
            or (
                (NERtag_currenRow != NERtag_nextRow)
                and (
                    NERtag_currenRow == "COUNTRY"
                    or NERtag_currenRow == "STATE_OR_PROVINCE"
                    or NERtag_currenRow == "CITY"
                    or NERtag_currenRow == "LOCATION"
                )
                and (
                    NERtag_nextRow is None
                    or NERtag_nextRow == "COUNTRY"
                    or NERtag_nextRow == "STATE_OR_PROVINCE"
                    or NERtag_nextRow == "CITY"
                    or NERtag_nextRow == "LOCATION"
                )
            )
        ):
            if currNERtag != "":
                currNERtag = currNERtag + " " + str(NER[index][0])
            else:
                currNERtag = str(NER[index][0])
            if beginToken_nextRow is None:
                NER[index][0] = currNERtag
                NER[index][2] = beginToken_currenRow
                new_NER.append(NER[index])
            index = index + 1
            continue
        else:
            if currNERtag != "":
                currNERtag = currNERtag + " " + str(NER[index][0])
            else:
                currNERtag = str(NER[index][0])
            NER[index][0] = currNERtag
            new_NER.append(NER[index])
            beginToken_currenRow = -1
            currNERtag = ""
            index = index + 1
    return new_NER


def process_json_ner(config_filename, documentID, document, sentenceID, json, **kwargs):
    logger.info("   Processing Json output file for NER annotator")
    # establish the kwarg local vars
    extract_date_from_text_var = False
    filename_embeds_date_var = False
    request_NER = []
    # process the optional values in kwargs
    for key, value in kwargs.items():
        if key == "extract_date_from_text_var" and value:
            extract_date_from_text_var = True
        if key == "NERs":
            request_NER = value
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True
        # if key == 'date_format':
        # if key == 'items_separator_var':
        # if key == 'date_position_var':
    NER = []
    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    # if date_str!='':
    # if filename_embeds_date_var:
    #     date, date_str = IO_files_util.getDateFromFileName(document, items_separator_var, date_position_var,
    #                                                        date_format)

    for sentence in json["sentences"]:
        complete_sent = ""
        for token in sentence["tokens"]:
            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]
        # TODO to be checked; formerly commented out but then the Sentence ID field was always displayed as 0
        sentenceID = sentence["index"] + 1
        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        for ner in sentence["entitymentions"]:
            temp = [
                ner["text"],
                ner["ner"],
                ner["tokenBegin"],
                ner["tokenEnd"],
                sentenceID,
                complete_sent,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
            ]
            # check in NER tag column
            if temp[1] in request_NER:
                if filename_embeds_date_var:
                    temp.append(date_str)
                    NER.append(temp)
                else:
                    if extract_date_from_text_var:
                        # annotated is a string in json format, we can retrieve normalizedNER from it
                        try:
                            # Attempt to pull out normalizedNER
                            date_val = ner["normalizedNER"]
                            # Check if date is valid
                            # Use regex to see if data follows YYYY-MM-DD format
                            # (4 digits - 2 digits - 2 digits)
                            if re.match(r"\d{4}-\d{2}-\d{2}", date_val):
                                norm_date = date_val
                            else:
                                # date did not match required format
                                norm_date = ""
                        except Exception:
                            logger.info("normalizedNER not available.")
                            norm_date = ""
                        temp.append(norm_date)
                        NER.append(temp)
                    else:
                        NER.append(temp)

    # check tokenBegin & tokenEnd in current and next sentence
    new_NER = check_NER_tokenBegin_tokenEnd(NER)

    return new_NER


def process_json_sentiment(config_filename, documentID, document, sentenceID, json, **kwargs):
    logger.info("   Processing Json output file for SENTIMENT annotator")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    sentiment = []
    for sentence in json["sentences"]:
        sentenceID += 1
        text = ""
        for token in sentence["tokens"]:
            if token["originalText"] in string.punctuation:
                text = text + token["originalText"]
            else:
                if token["index"] == 1:
                    text = text + token["originalText"]
                else:
                    text = text + " " + token["originalText"]

        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        if filename_embeds_date_var:
            temp = [
                sentence["sentimentValue"],
                sentence["sentiment"].lower(),
                date_str,
                sentence["index"] + 1,
                text,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
            ]
        else:
            temp = [
                sentence["sentimentValue"],
                sentence["sentiment"].lower(),
                sentence["index"] + 1,
                text,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
            ]
        sentiment.append(temp)
    return sentiment
