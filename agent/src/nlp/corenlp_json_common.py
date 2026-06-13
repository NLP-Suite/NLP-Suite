# Helpers shared by the corenlp_json_* processors and Stanford_CoreNLP_util.
# Kept in a leaf module (no intra-project imports besides reminders_util) so the
# json processors can import them without creating a cycle through
# Stanford_CoreNLP_util, which imports the json processors at its bottom.

import logging
import os
import string

import reminders_util

logger = logging.getLogger(__name__)


def check_sentence_length(sentence_length, sentenceID, config_filename):
    # WARNING for sentences with > 100 tokens
    if sentence_length > 100:
        order = "th"
        if sentenceID % 10 == 1:
            order = "st"
        elif sentenceID % 10 == 2:
            order = "nd"
            if sentenceID == 12:
                order = "th"
        elif sentenceID % 10 == 3:
            order = "rd"

        logger.info(
            "   Warning: The %s%s sentence has %s words, more than the 100 max recommended by CoreNLP for best performance.",
            sentenceID,
            order,
            sentence_length,
        )
        head, scriptName = os.path.split(os.path.basename(__file__))
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_sentence_length,
            reminders_util.message_CoreNLP_sentence_length,
            True,
        )


def build_sentence_string(sentence):
    complete_sent = ""
    for token in sentence["tokens"]:
        if token["originalText"] in string.punctuation:
            complete_sent = complete_sent + token["originalText"]
        else:
            if token["index"] == 1:
                complete_sent = complete_sent + token["originalText"]
            else:
                complete_sent = complete_sent + " " + token["originalText"]
    return complete_sent
