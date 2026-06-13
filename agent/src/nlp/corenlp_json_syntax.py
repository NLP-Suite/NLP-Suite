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

import json
import logging
import os
import string

import IO_csv_util

# not using stanfordcorenlp because it is not recognizing sentiment annotator
import pandas as pd
import Stanford_CoreNLP_clause_util
import Stanford_CoreNLP_SVO_enhanced_dependencies_util  # Enhanced++ dependencies
from corenlp_json_common import check_sentence_length
from corenlp_json_discourse import process_json_gender, process_json_quote
from corenlp_json_gis import similar_string_floor_filter, visualize_GIS_maps
from corenlp_json_ner import check_NER_tokenBegin_tokenEnd
from IO_files_util import date_in_filename

logger = logging.getLogger(__name__)

language_encoding = "utf-8"


def process_json_sentence(config_filename, documentID, document, sentenceID, json, **kwargs):
    temp = []
    for sentence in json["sentences"]:  # traverse output of each sentence
        sentence_length = 0
        number_punctuations = 0
        complete_sent = ""  # build sentence string
        for token in sentence["tokens"]:
            # check for basic symbols that make long sentences
            if (
                token["word"] == ","
                or token["word"] == ";"
                or token["word"] == "("
                or token["word"] == ")"
                or token["word"] == "-"
            ):
                number_punctuations = number_punctuations + 1
            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]
            sentence_length = sentence_length + 1
        sentenceID = sentenceID + 1
        temp.append(
            [
                sentenceID,
                complete_sent,
                sentence_length,
                number_punctuations,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
            ]
        )
    return temp


# Dec. 21
def process_json_SVO_enhanced_dependencies(config_filename, documentID, document, sentenceID, json, **kwargs):
    # extract date from file name
    filename_embeds_date_var = False
    gender_var = False
    quote_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True
        if key == "gender_var" and value:
            gender_var = True
        if key == "quote_var" and value:
            quote_var = True

    date_str = date_in_filename(document, **kwargs)

    # get gender information for this document
    if gender_var:
        raw_gender_info = process_json_gender(config_filename, documentID, document, 0, json, **kwargs)
        gender_info = []
        for row in raw_gender_info:
            gender_info.append([row[0], row[1], row[3], row[4]])

    # get quote information for this document
    if quote_var:
        raw_quote_info = process_json_quote(config_filename, documentID, document, sentenceID, json, **kwargs)
        # TODO MINO: process quotes with pandas without for-loop, and rearrange the columns
        if filename_embeds_date_var:
            quote_columns = [
                "Speakers",
                "Number of Quotes",
                "Sentence ID",
                "Sentence",
                "Document ID",
                "Document",
                "Date",
            ]
        else:
            quote_columns = [
                "Speakers",
                "Number of Quotes",
                "Sentence ID",
                "Sentence",
                "Document ID",
                "Document",
            ]
        quote_df = pd.DataFrame(raw_quote_info, columns=quote_columns)
        quote_df = quote_df[["Speakers", "Number of Quotes", "Sentence ID", "Document ID"]]

    SVO_enhanced_dependencies = []
    SVO_brief = []
    locations = []  # a list of [sentence, sentence id, [location_text, ner_value]]
    for sentence in json["sentences"]:  # traverse output of each sentence
        sent_data = Stanford_CoreNLP_SVO_enhanced_dependencies_util.SVO_enhanced_dependencies_sent_data_reorg(
            sentence
        )  # reorganize the output into a dictionary in which each content (also dictionary) contains information of a token
        # including a dictionary (govern_dictionary) indicating the index of tokens whose syntactical head is the current token

        complete_sent = ""  # build sentence string
        for token in sentence["tokens"]:
            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]

        sentenceID = sentenceID + 1
        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        # TODO MINO: add Date Type columns
        # CYNTHIA: feed another information sentence['entitymentions'] to SVO_extraction to get locations
        #
        (
            SVO,
            location_list,
            loc_NER_value,
            T,
            T_S,
            T_T,
            per_NER_value,
            org_NER_value,
            person_list,
            organization_list,
            N,
        ) = Stanford_CoreNLP_SVO_enhanced_dependencies_util.SVO_extraction(
            sent_data, sentence["entitymentions"]
        )  # main function
        # per_NER_value currently not used
        nidx = 0
        location_list = []
        person_list = []
        organization_list = []
        person = []
        organization = []
        new_NER_value = []

        # PROCESS LOCATION LIST --------------------------------------------------------------
        for el in loc_NER_value:
            # need to recompute location list in case locations have been regrouped
            #   e.g., Denmark Street (COUNTRY, LOCATION) regrouped as Denmark Street
            new_NER_value.append(
                [
                    el[0],
                    el[1],
                    el[2],
                    el[3],
                    sentenceID,
                    complete_sent,
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                ]
            )
        # loc_NER_value is now added elements [['Shanklin','LOCATION',24,25, Sentence ID, Sentence, Document ID, Document]]
        loc_NER_value = check_NER_tokenBegin_tokenEnd(new_NER_value)
        # recompute location_list as NER values may have changed
        for el in loc_NER_value:
            # need to recompute location list in case locations have been regrouped
            #   e.g., Denmark Street (COUNTRY, LOCATION) regrouped as Denmark Street
            location_list.append(el[0])
            # if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True and len(location_list) != 0:
            # produce an intermediate location file
            locations.append(el)

        # PROCESS PERSON LIST --------------------------------------------------------------
        new_NER_value = []
        # Person
        for el in per_NER_value:
            # need to recompute Person list in case Person & organization have been regrouped
            #   e.g., Mao Zedong regrouped as Mao Zedong
            new_NER_value.append(
                [
                    el[0],
                    el[1],
                    el[2],
                    el[3],
                    sentenceID,
                    complete_sent,
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                ]
            )
        #
        # per_NER_value is now added elements [['World Bank','ORGANIZATION',22,24, Sentence ID, Sentence, Document ID, Document]]
        per_NER_value = check_NER_tokenBegin_tokenEnd(new_NER_value)
        # recompute Person list as NER values may have changed
        for el in per_NER_value:
            # need to recompute Person & organization list in case Person & organization have been regrouped
            #   e.g., Mao Zedong regrouped as Mao Zedong
            person_list.append(el[0])
            person.append(el)

        # PROCESS ORGANIZATION LIST --------------------------------------------------------------
        new_NER_value = []
        # organization
        for el in org_NER_value:
            # need to recompute Person & organization list in case Person & organization have been regrouped
            #   e.g., Mao Zedong regrouped as Mao Zedong
            new_NER_value.append(
                [
                    el[0],
                    el[1],
                    el[2],
                    el[3],
                    sentenceID,
                    complete_sent,
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                ]
            )
        #
        # per_NER_value is now added elements [['World Bank','ORGANIZATION',22,24, Sentence ID, Sentence, Document ID, Document]]
        org_NER_value = check_NER_tokenBegin_tokenEnd(new_NER_value)
        # recompute Person & organization list as NER values may have changed
        for el in org_NER_value:
            # need to recompute Person & organization list in case Person & organization have been regrouped
            #   e.g., Mao Zedong regrouped as Mao Zedong
            organization_list.append(el[0])
            organization.append(el)

        # CYNTHIA: added list of locations in SVO output (e.g., Los Angeles; New York; Washington)
        # TODO Mino: add Date Type columns
        for row in SVO:
            SVO_brief.append(
                [
                    row[0],
                    row[1],
                    row[2],
                    sentenceID,
                    complete_sent,
                    documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document),
                ]
            )
            # TODO MINO: only add one value because the list includes duplicates.
            if len(T_S) > 1:
                tmp_T_S = T_S[0]
                tmp_T_T = T_T[0]
            else:
                tmp_T_S = "; ".join(T_S)
                tmp_T_T = "; ".join(T_T)
            if filename_embeds_date_var:
                SVO_enhanced_dependencies.append(
                    [
                        row[0],
                        row[1],
                        row[2],
                        N[nidx],
                        "; ".join(location_list),
                        "; ".join(person_list),
                        "; ".join(organization_list),
                        " ".join(T),
                        tmp_T_S,
                        tmp_T_T,
                        sentenceID,
                        complete_sent,
                        documentID,
                        IO_csv_util.dressFilenameForCSVHyperlink(document),
                        date_str,
                    ]
                )
            else:
                SVO_enhanced_dependencies.append(
                    [
                        row[0],
                        row[1],
                        row[2],
                        N[nidx],
                        "; ".join(location_list),
                        "; ".join(person_list),
                        "; ".join(organization_list),
                        " ".join(T),
                        tmp_T_S,
                        tmp_T_T,
                        sentenceID,
                        complete_sent,
                        documentID,
                        IO_csv_util.dressFilenameForCSVHyperlink(document),
                    ]
                )
            nidx += 1
        # # for each sentence, get locations
        # if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True and len(location_list) != 0:
        #     # produce an intermediate location file
        #

    # TODO Mino
    if "google_earth_var" in kwargs and kwargs["google_earth_var"]:
        visualize_GIS_maps(kwargs, locations, documentID, document, date_str)

    # merge gender information with SVO information
    if gender_var:
        SVO_df = pd.DataFrame(
            SVO_brief,
            columns=[
                "Subject (S)",
                "Verb (V)",
                "Object (O)",
                "Sentence ID",
                "Sentence",
                "Document ID",
                "Document",
            ],
        )
        gender_df = pd.DataFrame(
            gender_info,
            columns=["Subject (S)", "S Gender", "Sentence Set", "Document ID"],
        )
        merge_df = pd.merge(SVO_df, gender_df, on=["Subject (S)", "Document ID"], how="left")

        gender_df = pd.DataFrame(
            gender_info,
            columns=["Object (O)", "O Gender", "Sentence Set", "Document ID"],
        )
        merge_df = pd.merge(merge_df, gender_df, on=["Object (O)", "Document ID"], how="left")

        columns = [
            "Subject (S)",
            "S Gender",
            "Verb (V)",
            "Object (O)",
            "O Gender",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ]
        merge_df = merge_df[columns]
        merge_df = merge_df.drop_duplicates()
        # TODO unfortunately, saving the file in the proper directory runs into problems with visualization
        # save the output file in the gender subdirectory
        # # remove the file, add the gender subdirectory, and re-add the file
        # # remove SVO from tail and .csv
        # # remove NLP_
        # # save the output file in the quote subdirectory
        fn = kwargs["gender_filename"]
        # TODO MINO: properly read and save csv without additional row of headers
        if os.path.isfile(fn):
            original_df = pd.read_csv(fn, encoding=language_encoding, on_bad_lines="skip")
            merge_df = pd.concat([original_df, merge_df], ignore_index=True)
        IO_csv_util.df_to_csv(merge_df, fn, columns, False, language_encoding)
        # merge_df.to_csv(fn, index=False, encoding=language_encoding)

    if quote_var:
        SVO_df = pd.DataFrame(
            SVO_brief,
            columns=[
                "Subject (S)",
                "Verb (V)",
                "Object (O)",
                "Sentence ID",
                "Sentence",
                "Document ID",
                "Document",
            ],
        )
        merge_df = pd.merge(SVO_df, quote_df, on=["Sentence ID", "Document ID"], how="left")
        columns = [
            "Subject (S)",
            "Verb (V)",
            "Object (O)",
            "Speakers",
            "Number of Quotes",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ]
        merge_df = merge_df[columns]
        merge_df = merge_df.drop_duplicates()

        # TODO unfortunately, saving the file in the proper directory runs into problems with visualization
        # save the output file in the gender subdirectory
        # remove the file, add the gender subdirectory, and re-add the file
        # # remove SVO from tail and .csv
        # # remove NLP_
        # # save the output file in the quote subdirectory
        fn = kwargs["quote_filename"]
        # TODO MINO: properly read and save csv without additional row of headers
        if os.path.isfile(fn):
            original_df = pd.read_csv(fn, encoding=language_encoding, on_bad_lines="skip")
            merge_df = pd.concat([original_df, merge_df], ignore_index=True)
        IO_csv_util.df_to_csv(merge_df, fn, columns, False, language_encoding)
        # merge_df.to_csv(fn, index=False, encoding=language_encoding)

    return SVO_enhanced_dependencies


def process_json_openIE(config_filename, documentID, document, sentenceID, json, **kwargs):
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True
    date_str = date_in_filename(document, **kwargs)

    openIE = []
    locations = []  # a list of [sentence, sentence id, [location_text, ner_value]]
    for sentence in json["sentences"]:
        entitymentions = sentence["entitymentions"]
        complete_sent = ""
        location_list = []  # list that stores the location information appear in sentences
        NER_value = []
        T = []  # list that stores the time information appear in sentences
        T_S = []  # list that stores normalized form of the time information appear in sentences
        person_list = []  # list that stores person names appear in sentences
        # CYNTHIA: get locations from entitymentions
        for item in entitymentions:
            if item["ner"] is not None and item["ner"] in [
                "STATE_OR_PROVINCE",
                "COUNTRY",
                "CITY",
                "LOCATION",
            ]:
                location_list.append(item["text"])
                NER_value.append(item["ner"])
        for token in sentence["tokens"]:
            if token["ner"] == "TIME" or token["ner"] == "DATE":
                T.append(token["word"])
                try:
                    T_S.append(token["normalizedNER"])
                except Exception:
                    logger.info("normalizedNER not available.")
            if token["ner"] == "PERSON":
                person_list.append(token["word"])

            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]
        sentenceID = sentenceID + 1

        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        SVOs = []
        for openie in sentence["openie"]:
            # Document ID, Sentence ID, Document, S, V, O, Sentence
            SVOs.append([openie["subject"], openie["relation"], openie["object"]])
        container = []
        for SVO_value in SVOs:
            redundant_flag = False
            remainder = [elmt for elmt in SVOs if elmt != SVO_value]
            for SVO_base in remainder:
                SVO_value_str = SVO_value[0] + " " + SVO_value[1] + " " + SVO_value[2]
                SVO_base_str = SVO_base[0] + " " + SVO_base[1] + " " + SVO_base[2]
                if SVO_value[0] == SVO_base[0] and similar_string_floor_filter(SVO_value_str, SVO_base_str):
                    redundant_flag = True
                    break
                else:
                    continue
            if not redundant_flag:
                container.append(SVO_value)
        if len(container) > 0:
            for row in container:
                if filename_embeds_date_var:
                    openIE.append(
                        [
                            row[0],
                            row[1],
                            row[2],
                            "N/A",
                            "; ".join(location_list),
                            "; ".join(person_list),
                            " ".join(T),
                            "; ".join(T_S),
                            date_str,
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                        ]
                    )
                else:
                    openIE.append(
                        [
                            row[0],
                            row[1],
                            row[2],
                            "N/A",
                            "; ".join(location_list),
                            "; ".join(person_list),
                            " ".join(T),
                            "; ".join(T_S),
                            sentenceID,
                            complete_sent,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                        ]
                    )
        # for each sentence, get locations
        if "google_earth_var" in kwargs and kwargs["google_earth_var"] and len(location_list) != 0:
            # produce an intermediate location file
            locations.append(
                [
                    sentenceID,
                    complete_sent,
                    [[x, y] for x, y in zip(location_list, NER_value)],
                ]
            )

    if "google_earth_var" in kwargs and kwargs["google_earth_var"]:
        visualize_GIS_maps(kwargs, locations, documentID, document, date_str)

    return openIE


def process_json_lemma(config_filename, documentID, document, sentenceID, recordID, json, **kwargs):
    logger.info("   Processing Json output file for Lemma")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        sentenceID += 1

        clauseID = 0
        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            temp.append(row["lemma"])
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if filename_embeds_date_var:
                temp.append(date_str)
            result.append(temp)

        check_sentence_length(len(tokens), sentenceID, config_filename)
    return result, recordID


def process_json_postag(config_filename, documentID, document, sentenceID, json, **kwargs):
    # only processes verbs and nouns
    Verbs = []
    Nouns = []
    for sentence in json["sentences"]:
        sentenceID += 1
        # if len(sentence)> 20:
        for token in sentence["tokens"]:
            if token["pos"] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                Verbs.append(token["lemma"])
            elif token["pos"] in ["NN", "NNP", "NNS"]:
                Nouns.append(token["lemma"])

        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

    return Verbs, Nouns


# floor filter: if edit distance is smaller than 5
# (round-up average length of one English word, check this reference:
# https://wolfgarbe.medium.com/the-average-word-length-in-english-language-is-4-7-35750344870f)
# return True, which means the two strings are very similar
def process_json_all_postag(config_filename, documentID, document, sentenceID, recordID, json, **kwargs):
    logger.info("   Processing Json output file for All POS tags")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        sentenceID += 1

        clauseID = 0
        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            temp.append(row["pos"])
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if filename_embeds_date_var:
                temp.append(date_str)
            result.append(temp)
            # if dateInclude == 1 and dateStr!='DATE ERROR!!!':

        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID


def process_json_deprel(config_filename, documentID, document, sentenceID, recordID, json, **kwargs):
    logger.info("   Processing Json output file for DepRel")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    for i in range(len(json["sentences"])):
        sentenceID += 1
        clauseID = 0
        tokens = json["sentences"][i]["tokens"]
        dependencies = json["sentences"][i]["enhancedDependencies"]
        depLib = {}
        keys = []
        for item in dependencies:
            depLib[item["dependent"]] = (item["dep"], item["governor"])
            keys.append(item["dependent"])
        depID = 1
        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])

            if depID not in depLib:
                temp.append("")
                temp.append("")
            else:
                temp.append(depLib[depID][1])
                temp.append(depLib[depID][0])
            depID += 1
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if filename_embeds_date_var:
                temp.append(date_str)
            result.append(temp)

        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID


# processes both lemma and POS
def process_json_single_annotation(
    config_filename, documentID, document, sentenceID, recordID, annotation, json, **kwargs
):
    logger.info("   Processing Json output file for All POS tags and Lemma")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        sentenceID += 1

        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            if "All POS" in annotation:
                temp.append(row["pos"])
            elif "Lemma" in annotation:
                temp.append(row["lemma"])
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if filename_embeds_date_var:
                temp.append(date_str)
            result.append(temp)

        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID


def process_json_parser(config_filename, documentID, document, sentenceID, recordID, pcfg, json, **kwargs):
    logger.info("   Processing Json output file for Parser")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    # neural network parser does not contain clausal tags (e.g., NP, VP,...)
    if pcfg:
        sent_list_clause = [
            Stanford_CoreNLP_clause_util.clausal_info_extract_from_string(parsed_sent["parse"])
            for parsed_sent in json["sentences"]
        ]
    # else: a reminder is posted at the end
    for i in range(len(json["sentences"])):
        sentenceID += 1
        # neural network parser does not contain clause tags
        if pcfg:
            cur_clause = sent_list_clause[i]
        clauseID = 0
        tokens = json["sentences"][i]["tokens"]
        dependencies = json["sentences"][i]["enhancedDependencies"]
        # try enhancedPlusPlus instead
        depLib = {}
        enhancedDepLib = {}
        keys = []
        for item in dependencies:
            depLib[item["dependent"]] = (item["dep"], item["governor"])

            # create an enhanced dependency list
            if item["dependent"] in enhancedDepLib:
                enhancedDepLib[item["dependent"]].append((item["dep"], item["governor"]))
            else:
                enhancedDepLib[item["dependent"]] = [(item["dep"], item["governor"])]

            keys.append(item["dependent"])
        depID = 1
        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            temp.append(row["lemma"])
            temp.append(row["pos"])
            temp.append(row["ner"])
            if depID not in depLib:
                temp.append("")
                temp.append("")
                temp.append("")
            else:
                temp.append(depLib[depID][1])
                temp.append(depLib[depID][0])
                # Add enhanced dep here
                depString = ""
                dep: tuple[int, str]
                for dep in enhancedDepLib[depID]:
                    if len(depString) != 0:
                        depString = depString + "|"
                    depString = depString + str(dep[1]) + ":" + str(dep[0])
                temp.append(depString)

            depID += 1
            if pcfg:
                temp.append(cur_clause[clauseID][0])
            else:  # neural network parser does not contain clause tags
                temp.append("")
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if filename_embeds_date_var:
                temp.append(date_str)
            result.append(temp)

    return result, recordID


def exportJson(
    export_json_var,
    inputFilename,
    outputJsonDir,
    CoreNLP_output,
    language_encoding,
    annotator_params,
):
    if not export_json_var:
        return
    if outputJsonDir != "":
        jsonFilename = os.path.join(outputJsonDir, inputFilename[:-4] + "_" + str(annotator_params) + ".txt")
        with open(jsonFilename, "a+", encoding=language_encoding, errors="ignore") as json_out_nn:
            json.dump(CoreNLP_output, json_out_nn, indent=4, ensure_ascii=False)
    # no need to open the Json file
    # if jsonFilename not in filesToOpen:
