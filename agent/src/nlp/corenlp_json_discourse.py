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
import string

import IO_csv_util

# not using stanfordcorenlp because it is not recognizing sentiment annotator
from corenlp_json_common import build_sentence_string, check_sentence_length
from IO_files_util import date_in_filename

logger = logging.getLogger(__name__)


def process_json_coref(config_filename, documentID, document, sentenceID, json, **kwargs):
    logger.info("   Processing Json output file for COREF annotator")

    def resolve(corenlp_output):
        """Transfer the word form of the antecedent to its associated pronominal anaphor(s)"""
        for coref in corenlp_output["corefs"]:
            mentions = corenlp_output["corefs"][coref]
            antecedent = mentions[0]  # the antecedent is the first mention in the coreference chain
            for j in range(1, len(mentions)):
                mention = mentions[j]
                if mention["type"] == "PRONOMINAL":
                    # get the attributes of the target mention in the corresponding sentence
                    target_sentence = mention["sentNum"]
                    target_token = mention["startIndex"] - 1
                    # transfer the antecedent's word form to the appropriate token in the sentence
                    corenlp_output["sentences"][target_sentence - 1]["tokens"][target_token]["word"] = antecedent[
                        "text"
                    ]

    # when possessive pronouns are substituted by an antecedent noun, the noun must be followed by 's
    #   unless the noun already has the gerund 's
    #   Mary took her exam; Mary took Mary's exam
    def get_resolved(corenlp_output, sentenceID):
        """get the "resolved" output as String"""
        result = ""
        # possessive pronouns: my, mine, his, her(s), its, our(s), their, yours
        possessives = [
            "her",
            "hers",
            "his",
            "its",
            "our",
            "ours",
            "their",
            "theirs",
            "your",
            "yours",
        ]
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
        for sentence in corenlp_output["sentences"]:
            sentenceID += 1
            for token in sentence["tokens"]:
                output_word = token["word"]
                # check lemmas as well as tags for possessive pronouns in case of tagging errors
                if token["lemma"] in possessives or token["pos"] == "PRP$":
                    if "'s" not in output_word and output_word not in pronouns:
                        output_word += "'s"  # add the possessive morpheme
                output_word += token["after"]
                if output_word == ". ":
                    if result[-1] == ".":
                        continue
                result = result + output_word
            check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        return result

    resolve(json)
    output_text = get_resolved(json, sentenceID)
    return output_text


# def count_pronoun(json):
#     for sentence in json['sentences']:
#         for token in sentence['tokens']:
#             if token["pos"] == "PRP$" or token["pos"] == "PRP":


def process_json_coref_table(config_filename, documentID, document, sentenceID, json, **kwargs):
    result = []  # the collection of information of each coreference
    for coref in json["corefs"]:
        mentions = json["corefs"][coref]
        reference = mentions[0]  # First Referent in context

        ref_sent = json["sentences"][reference["sentNum"] - 1]
        ref_sent_ID = reference["sentNum"]  # First Referent Sentence ID
        ref_sent_string = build_sentence_string(ref_sent)  # First Referent Sentence
        ref_start_ID = reference["startIndex"]  # Referent Start ID in Sentence
        ref_text = reference["text"]  # first Referent
        for j in range(1, len(mentions)):
            mention = mentions[j]

            if mention["type"] == "PRONOMINAL":  # extract only pronouns
                ment_text = mention["text"]
                ment_sent = json["sentences"][mention["sentNum"] - 1]
                ment_sent_ID = mention["sentNum"]  # sentence ID
                ment_sent_string = build_sentence_string(ment_sent)  # sentence
                ment_start_ID = mention["startIndex"]  # start ID in sentence
                result.append(
                    [
                        ment_text,
                        ref_text,
                        ref_start_ID,
                        ref_sent_ID,
                        ref_sent_string,
                        ment_start_ID,
                        ment_sent_ID,
                        ment_sent_string,
                        documentID,
                        IO_csv_util.dressFilenameForCSVHyperlink(document),
                    ]
                )
    return result


# December.10 Yi: Modify process_json_gender to provide one more column(complete sentence)
def process_json_gender(config_filename, documentID, document, start_sentenceID, json, **kwargs):

    logger.info("   Processing Json output file for GENDER annotator")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    mentions = []
    sent_dict = {}
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
        sentenceID = sentence["index"] + 1

        check_sentence_length(len(sentence["tokens"]), sentenceID, config_filename)

        sent_dict[sentenceID] = complete_sent
    for _num, res in json["corefs"].items():
        mentions.append(res)
    for mention in mentions:
        for elmt in mention:
            if elmt["gender"] in ["NEUTRAL", "UNKNOWN"]:
                continue
            else:
                # get complete sentence
                complete = sent_dict[elmt["sentNum"]]
                if filename_embeds_date_var:
                    result.append(
                        [
                            elmt["text"],
                            elmt["gender"],
                            elmt["sentNum"] + start_sentenceID,
                            complete,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                            date_str,
                        ]
                    )
                else:
                    result.append(
                        [
                            elmt["text"],
                            elmt["gender"],
                            elmt["sentNum"] + start_sentenceID,
                            complete,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(document),
                        ]
                    )

    return sorted(
        result, key=lambda x: x[3]
    )  # this function did not add each row in order of sentence, so the output needs sorting by sentenceID


def process_json_quote(config_filename, documentID, document, sentenceID, json, **kwargs):
    logger.info("   Processing Json output file for QUOTE annotator")
    filename_embeds_date_var = False
    for key, value in kwargs.items():
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    quoted_sentences = {}
    speakers = {}  # the speakers of each quote
    for quote in json["quotes"]:
        # to find all sentences with quotes
        sentenceIDs = list(range(quote["beginSentence"], quote["endSentence"] + 1))
        for sent in sentenceIDs:
            quoted_sentences[sent] = quoted_sentences.get(sent, 0) + 1
            if sent in speakers.keys():
                speakers[sent].append(quote["speaker"])
            else:
                speakers[sent] = [quote["speaker"]]
    # iterate over those sentence indexes and find its complete sentence
    for quoted_sent_id, number_of_quotes in quoted_sentences.items():
        sentenceID = quoted_sent_id + 1
        sentence_data = json["sentences"][quoted_sent_id]
        # for sentence in CoreNLP_output['sentences']:
        complete_sent = ""
        for token in sentence_data["tokens"]:
            if token["originalText"] in string.punctuation:
                complete_sent = complete_sent + token["originalText"]
            else:
                if token["index"] == 1:
                    complete_sent = complete_sent + token["originalText"]
                else:
                    complete_sent = complete_sent + " " + token["originalText"]

        check_sentence_length(len(sentence_data["tokens"]), sentenceID, config_filename)

        if filename_embeds_date_var:
            # TODO MINO: rearrange the columns
            temp = [
                str(speakers[quoted_sent_id][0]),
                number_of_quotes,
                sentenceID,
                complete_sent,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
                date_str,
            ]
        else:
            temp = [
                str(speakers[quoted_sent_id][0]),
                number_of_quotes,
                sentenceID,
                complete_sent,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(document),
            ]
        result.append(temp)
    return result
