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
import os
import time

import file_splitter_ByLength_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_libraries_util
import IO_user_interface_util

# not using stanfordcorenlp because it is not recognizing sentiment annotator
import pandas as pd
import parsers_annotators_visualization_util
import reminders_util
from app_constants import CORENLP_URL
from pycorenlp import StanfordCoreNLP

logger = logging.getLogger(__name__)

url = "https://stanfordnlp.github.io/CoreNLP/human-languages.html"
CoreNLP_web = (
    "\n\nLanguage and annotator options for Stanford CoreNLP are listed at the Stanford CoreNLP website\n\n" + url
)

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


# when multiple annotators are selected (e.g., quote, gender, normalized-date)
#   output must go to the appropriate subdirectory
# the function creates the subdirectory for a given annotator
# outputDirSV is the original output directory listed in the
def create_output_directory(
    inputFilename,
    inputDir,
    outputDir,
    config_filename,
    export_json_var,
    annotator,
    silent,
    Json_question_already_asked,
):
    outputJsonDir = ""
    outputDirSV = GUI_IO_util.output_folder
    if outputDirSV != outputDir:
        # create output subdirectory
        outputDir = IO_files_util.make_output_subdirectory(
            "", "", outputDir, label=annotator + "_CoreNLP", silent=silent
        )
    else:
        # when coming from coref annotator, the outputDir will contain an unnecessary NLP_CoreNLP_coref_ string
        # if 'NLP_CoreNLP_coref_' in inputFilename:
        outputDir = IO_files_util.make_output_subdirectory(
            inputFilename,
            inputDir,
            outputDir,
            label=annotator + "_CoreNLP",
            silent=silent,
        )
    # create a subdirectory of the output directory
    outputJsonDir = ""
    if export_json_var:
        outputJsonDir = IO_files_util.make_output_subdirectory(
            inputFilename, inputDir, outputDir, label="Json", silent=silent
        )
    return outputDir, outputJsonDir


def check_CoreNLP_available_languages(language):
    available_language = True
    if language not in available_languages:
        available_language = False
        website_name = "CoreNLP website"
        message_title = "CoreNLP website"
        message = (
            language + " is not available in Stanford CoreNLP."
            "\n\nAvailable languages are: Arabic, Chinese, English, French, German, Hungarian, Italian, Spanish. \n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the 'Setup NLP package and corpus language' to open the GUI where you can change the language option."
            + CoreNLP_web
            + "\n\nWould you like to open the Stanford CoreNLP website for annotator availability for the various languages supported by CoreNLP?"
        )
        IO_libraries_util.open_url(
            website_name,
            url,
            ask_to_open=True,
            message_title=message_title,
            message=message,
        )
    return available_language


def check_CoreNLP_annotator_availability(config_filename, annotator, language):
    not_available = False
    if "lemma" in annotator:
        if language != "English":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP LEMMA annotator is only available for English." + CoreNLP_web,
            )
            not_available = True
    elif "normalized" in annotator:
        if language != "English":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP NORMALIZED NER annotator is only available for English." + CoreNLP_web,
            )
            not_available = True
    elif "gender" in annotator:
        if language != "English":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP GENDER annotator is only available for English." + CoreNLP_web,
            )
            not_available = True
    elif "quote" in annotator:
        if language != "English":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP QUOTE annotator is only available for English." + CoreNLP_web,
            )
            not_available = True
    elif "OpenIE" in annotator:
        if language != "English":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP OPENIE annotator is only available for English." + CoreNLP_web,
            )
            not_available = True
    elif "sentiment" in annotator:
        if language != "English" and language != "Chinese":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP SENTIMENTT ANALYSIS annotator is only available for Chinese and English."
                + CoreNLP_web,
            )
            not_available = True
    elif "coreference" in annotator:
        if language != "English" and language != "Chinese":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP COREFERENCE RESOLUTION annotator is only available for Chinese and English."
                + CoreNLP_web,
            )
            not_available = True
    elif "PCFG" in annotator:
        if language == "English" or language == "German":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP PCFG PARSER is not available for German and Hungarian." + CoreNLP_web,
            )
            not_available = True
    elif "neural network" in annotator:  # parser
        if language == "Arabic" or language == "Hungarian":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP NEURAL NETWORK PARSER is not available for Arabic and Hungarian." + CoreNLP_web,
            )
            not_available = True
    elif "SVO" in annotator:  # parser
        if language == "Arabic" or language == "Hungarian":
            logger.info(
                "%s %s",
                str(annotator).upper() + " annotator availability for " + language,
                "The Stanford CoreNLP SVO annotator is not available for Arabic and Hungarian." + CoreNLP_web,
            )
            not_available = True
    if not_available:
        head, scriptName = os.path.split(os.path.basename(__file__))
        reminder_status = reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_website,
            reminders_util.message_CoreNLP_website,
            True,
        )
        if reminder_status == "Yes" or reminder_status == "ON":  # 'Yes' the old way of saving reminders
            # open website
            website_name = "CoreNLP website"
            message_title = "CoreNLP website"
            message = "Would you like to open the Stanford CoreNLP website for annotator availability for the various languages supported by CoreNLP?"
            IO_libraries_util.open_url(
                website_name,
                url,
                ask_to_open=True,
                message_title=message_title,
                message=message,
            )
    return not (not_available)  # failed


# central CoreNLP_annotator function that pulls together our approach to processing many files,
# splitting them if necessary, and, depending upon annotator (NER date, quote, gender, sentiment)
# perhaps call different subfunctions, and pulling together the output

# CHOOSE YOUR OPTION FOR variable: annotator_params in option below
# ssplit:  tokenize,ssplit
# MWT: tokenize,ssplit,mwt
# lemma: tokenize,ssplit,pos,lemma
# POS: tokenize,ssplit,pos
# lemma: tokenize,ssplit,pos,lemma
# NER: tokenize,ssplit,pos,lemma,ner
# coref: tokenize,ssplit,pos,lemma,ner,parse,coref
# sentiment:
# input cleanXML = 1 to add cleanXML to your annotator

# ner GIS, date


def CoreNLP_annotate(
    config_filename,
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    annotator_params,
    DoCleanXML,
    language,
    export_json_var=0,
    memory_var=6,
    document_length=90000,
    sentence_length=1000,  # unless otherwise specified; sentence length limit does not seem to work for parsers only for NER and POS but then it is useless
    export_json_toTxt=True,
    silent=False,
    **kwargs,
):

    # These values can be zero if the setup has specified e.g., spaCy but in SVO or other annotators, the user selects to run CoreNLP
    if memory_var < 4:
        memory_var = 4
    if document_length < 50000:
        document_length = 90000
    if sentence_length < 50:
        sentence_length = 100  # unless otherwise specified; sentence length limit does not seem to work for parsers only for NER and POS but then it is useless

    start_time = time.time()
    speed_assessment = []  # storing the information used for speed assessment
    speed_assessment_format = [
        "Document ID",
        "Document",
        "Time",
        "Tokens to Annotate",
        "Params",
        "Number of Params",
    ]  # the column titles of the csv output of speed assessment
    filesToOpen = []

    available_language = check_CoreNLP_available_languages(language)
    if not available_language:
        return filesToOpen

    # check if selected language is available in CoreNLP
    annotator_available = check_CoreNLP_annotator_availability(config_filename, annotator_params, language)
    if not annotator_available:
        return filesToOpen

    # decide on directory or single file
    # TODO why these lines?
    # if inputDir != '':
    # decide on to provide output or to return value

    # global extract_date_from_text_var, filename_embeds_date_var
    extract_date_from_text_var = False
    filename_embeds_date_var = False
    single_quote_var = False
    # language initialized here and reset later in language = value

    for key, value in kwargs.items():
        if key == "extract_date_from_text_var" and value:
            extract_date_from_text_var = True
        if key == "NERs":
            pass
        if key == "filename_embeds_date_var" and value:
            filename_embeds_date_var = True
        if key == "date_format":
            pass
        if key == "items_separator_var":
            pass
        if key == "date_position_var":
            pass
        if key == "single_quote_var":
            single_quote_var = value

    global language_encoding
    if language == "English":
        language_encoding = "utf-8"
    else:
        language_encoding = "utf-8-sig"

    # more annotators may be added to SVO later depending upon the annotators_params passed to SVO
    #   you do not want to add coref, quote, gender, unless required
    SVO_annotators = ["tokenize", "ssplit", "pos", "depparse", "natlog", "lemma", "ner"]
    for key, value in kwargs.items():
        if key == "gender_var" and value:
            SVO_annotators.append("coref")
        if key == "quote_var" and value:
            SVO_annotators.append("quote")

    params_option = {
        "Sentence": {"annotators": ["ssplit"]},
        "tokenize": {"annotators": ["tokenize"]},
        "MWT": {"annotators": ["tokenize", "ssplit", "mwt"]},
        "Lemma": {"annotators": ["lemma"]},
        "POS": {"annotators": ["tokenize", "ssplit", "pos", "lemma"]},
        "All POS": {"annotators": ["tokenize", "ssplit", "pos", "lemma"]},
        "DepRel": {"annotators": ["parse"]},
        "NER": {"annotators": ["tokenize", "ssplit", "pos", "lemma", "ner"]},
        "quote": {
            "annotators": [
                "tokenize",
                "ssplit",
                "pos",
                "lemma",
                "ner",
                "depparse",
                "coref",
                "quote",
            ]
        },
        "coref": {"annotators": ["coref"]},
        "coref table": {"annotators": ["coref"]},
        "gender": {"annotators": ["coref"]},
        "sentiment": {"annotators": ["sentiment"]},
        "normalized-date": {"annotators": ["tokenize", "ssplit", "ner"]},
        # more annotators may be added to SVO later depending upon the annotators_params passed to SVO
        #   you do not want to add coref, quote, gender, unless required
        "SVO": {"annotators": SVO_annotators},
        "OpenIE": {"annotators": ["tokenize", "ssplit", "natlog", "openie", "ner"]},
        "parser (pcfg)": {
            "annotators": [
                "tokenize",
                "ssplit",
                "pos",
                "lemma",
                "ner",
                "parse",
                "regexner",
            ]
        },
        "parser (nn)": {
            "annotators": [
                "tokenize",
                "ssplit",
                "pos",
                "lemma",
                "ner",
                "depparse",
                "regexner",
            ]
        },
    }

    routine_option = {
        "Sentence": process_json_sentence,
        "sentiment": process_json_sentiment,
        "Lemma": process_json_lemma,
        "POS": process_json_postag,
        "All POS": process_json_all_postag,
        "NER": process_json_ner,
        "DepRel": process_json_deprel,
        "quote": process_json_quote,
        "coref": process_json_coref,
        "coref table": process_json_coref_table,
        "gender": process_json_gender,
        "normalized-date": process_json_normalized_date,
        "OpenIE": process_json_openIE,
        "SVO": process_json_SVO_enhanced_dependencies,
        "parser (pcfg)": process_json_parser,
        "parser (nn)": process_json_parser,
    }
    # @ change coref-text to coref, change coref-spreadsheet to gender@
    output_format_option = {
        "Sentence": [
            "Sentence ID",
            "Sentence",
            "Sentence Length (Number of Tokens)",
            "Number of Intra-Sentence Punctuation Symbols (),;-",
            "Document ID",
            "Document",
        ],
        "Lemma": [
            "ID",
            "Form",
            "Lemma",
            "Record ID",
            "Sentence ID",
            "Document ID",
            "Document",
        ],
        "POS": [["Verbs"], ["Nouns"]],
        "All POS": [
            "ID",
            "Form",
            "POS",
            "Record ID",
            "Sentence ID",
            "Document ID",
            "Document",
        ],
        "NER": [
            "Word",
            "NER",
            "tokenBegin",
            "tokenEnd",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        # TODO NER with date for dynamic GIS; modified below
        "DepRel": [
            "ID",
            "Form",
            "Head",
            "DepRel",
            "Record ID",
            "Sentence ID",
            "Document ID",
            "Document",
        ],
        "sentiment": [
            "Sentiment score",
            "Sentiment label",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "quote": [
            "Speakers",
            "Number of Quotes",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "coref": "text",
        "coref table": [
            "Pronoun",
            "Referent",
            "Referent Start ID in Sentence",
            "First Referent Sentence ID",
            "First Referent Sentence",
            "Pronoun Start ID in Referent Sentence",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "gender": [
            "Word",
            "Gender",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "normalized-date": [
            "Date expression",
            "Normalized date",
            "tid",
            "Date type",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "SVO": [
            "Subject (S)",
            "Verb (V)",
            "Object (O)",
            "Negation",
            "Location",
            "Person",
            "Organization",
            "Date expression",
            "Normalized date",
            "Date type",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        "OpenIE": [
            "Subject (S)",
            "Verb (V)",
            "Object (O)",
            "Negation",
            "Location",
            "Person",
            "Organization",
            "Date expression",
            "Normalized date",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ],
        # Chen
        # added Deps column
        "parser (pcfg)": [
            "ID",
            "Form",
            "Lemma",
            "POS",
            "NER",
            "Head",
            "DepRel",
            "Deps",
            "Clause Tag",
            "Record ID",
            "Sentence ID",
            "Document ID",
            "Document",
        ],
        # neural network parser does not contain clause tags
        "parser (nn)": [
            "ID",
            "Form",
            "Lemma",
            "POS",
            "NER",
            "Head",
            "DepRel",
            "Deps",
            "Clause Tag",
            "Record ID",
            "Sentence ID",
            "Document ID",
            "Document",
        ],
    }

    if not isinstance(annotator_params, list):
        annotator_params = [annotator_params]

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running Stanford CoreNLP " + str(annotator_params) + " annotator at",
        True,
    )

    head, scriptName = os.path.split(os.path.basename(__file__))

    # display the timing of various algorithms
    if "coref" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_coref_timing,
            reminders_util.message_CoreNLP_coref_timing,
            True,
        )
    if "SVO" in str(annotator_params) and "gender" in str(annotator_params) and "quote" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_SVO_gender_quote_timing,
            reminders_util.message_CoreNLP_SVO_gender_quote_timing,
            True,
        )
    if (
        "SVO" in str(annotator_params)
        and "gender" not in str(annotator_params)
        and "quote" not in str(annotator_params)
    ):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_SVO_timing,
            reminders_util.message_CoreNLP_SVO_timing,
            True,
        )
    if "gender" in str(annotator_params) and "SVO" not in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_gender_timing,
            reminders_util.message_CoreNLP_gender_timing,
            True,
        )
    if "quote" in str(annotator_params) and "SVO" not in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_quote_timing,
            reminders_util.message_CoreNLP_quote_timing,
            True,
        )
    if "parser (nn)" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_nn_parser_timing,
            reminders_util.message_CoreNLP_nn_parser_timing,
            True,
        )
    if "parser (pcfg)" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_PCFG_parser_timing,
            reminders_util.message_CoreNLP_PCFG_parser_timing,
            True,
        )
    if "All POS" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_POS_timing,
            reminders_util.message_CoreNLP_POS_timing,
            True,
        )
    if "NER" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_NER_timing,
            reminders_util.message_CoreNLP_NER_timing,
            True,
        )
    if "normalized-date" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_normalized_date_timing,
            reminders_util.message_CoreNLP_normalized_date_timing,
            True,
        )

    lang_models = language_models(GUI_IO_util.external_software, language)
    if lang_models is None:
        return filesToOpen
    param_number = 0
    param_number_NN = 0
    nDocs = 0  # number of input documents

    # collecting input txt files
    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=config_filename,
    )
    nDocs = len(inputDocs)
    if nDocs == 0:
        return filesToOpen

    # get corresponding func, output format and annotator params from upper 3 dicts
    # routine_list is a list of 4 items:
    #   annotator [0], e.g., NER
    #   output format [2]( headers), typically a single list [], and in the case of POS annotator for WordNet, a douuble list [[].[]]
    routine_list = []  # storing the annotator, output format (column titles of csv), output
    # if not isinstance(annotator_params,list):
    param_string = ""  # the input string of nlp annotator properties
    param_string_NN = ""
    Json_question_already_asked = False
    for annotator in annotator_params:
        # if not check_CoreNLP_annotator_availability(config_filename, annotator, language):
        #     continue
        if "coref" in annotator and "coref" not in SVO_annotators:
            reminders_util.checkReminder(
                scriptName,
                reminders_util.title_options_CoreNLP_coref_timing,
                reminders_util.message_CoreNLP_coref_timing,
                True,
            )
            SVO_annotators.append("coref")
        if "quote" in annotator and "quote" not in SVO_annotators:
            SVO_annotators.append("quote")
        if "gender" in annotator and "gender" not in SVO_annotators:
            SVO_annotators.append("gender")
        if (
            "gender" in annotator
            or "quote" in annotator
            or "coref" in annotator
            or "SVO" in annotator
            or "OpenIE" in annotator
            or ("parser" in annotator and "nn" in annotator)
        ):
            logger.info("Using neural network model")
            neural_network = True
            parse_model = "NN"
        else:
            neural_network = False
            parse_model = "PCFG"
        routine = routine_option.get(annotator)
        output_format = output_format_option.get(annotator)
        annotators_ = params_option.get(annotator)["annotators"]
        # tokenize each property
        # put all annotators whose parse model is neural network at the end of the list
        # so that the model would just need be switched once
        if neural_network:
            for param in annotators_:
                if param not in param_string_NN:  # the needed annotator property is not containted in the string
                    param_number_NN += 1
                    if param_string_NN == "":
                        param_string_NN = param
                    else:
                        param_string_NN = param_string_NN + ", " + param
                        param_string_NN = param_string_NN + ", " + param
            # when multiple annotators are selected (e.g., quote, gender, normalized-date)
            #   output must go to the appropriate subdirectory and added to routine_list
            output_dir, outputJsonDir = create_output_directory(
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                export_json_var,
                annotator,
                silent,
                Json_question_already_asked,
            )
            if output_dir == "":
                return filesToOpen
            # when running the SVO annotator in combination with gender and quote,
            #   you want to put the gender and quote folders inside the SVO folder
            if "SVO" in annotator and ("gender" in annotator_params or "quote" in annotator_params):
                pass
            Json_question_already_asked = True
            routine_list.append(
                [
                    annotator,
                    routine,
                    output_format,
                    [],
                    parse_model,
                    output_dir,
                    outputJsonDir,
                ]
            )
        else:
            for param in annotators_:
                if param not in param_string:  # the needed annotator property is not containted in the string
                    param_number += 1
                    if param_string == "":
                        param_string = param
                    else:
                        param_string = param_string + ", " + param
            # when multiple annotators are selected (e.g., quote, gender, normalized-date)
            #   output must go to the appropriate subdirectory and added to routine_list
            output_dir, outputJsonDir = create_output_directory(
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                export_json_var,
                annotator,
                silent,
                Json_question_already_asked,
            )
            if output_dir == "":
                return filesToOpen
            # when running the SVO annotator in combination with gender and quote,
            #   you want to put the gender and quote folders inside the SVO folder
            if "SVO" in annotator and ("gender" in annotator_params or "quote" in annotator_params):
                pass
            Json_question_already_asked = True
            routine_list.insert(
                0,
                [
                    annotator,
                    routine,
                    output_format,
                    [],
                    parse_model,
                    output_dir,
                    outputJsonDir,
                ],
            )

    # the third item in routine_list is typically a single list [],
    #   but for POS it becomes a double list ['Verbs'],[Nouns]]
    #   the case needs special handling
    POS_WordNet = False
    if routine_list == []:  # when the language check fails for an annotator
        return filesToOpen
    if isinstance(routine_list[0][2][0], list):
        run_output = [[], []]
        POS_WordNet = True
    else:
        run_output = []
        POS_WordNet = False

    params = {
        "annotators": param_string,
        "parse.model": lang_models["pcfg"],
        "outputFormat": "json",
        "outputDirectory": outputDir,
        "replaceExtension": True,
        "parse.maxlen": str(sentence_length),
        "ner.maxlen": str(sentence_length),
        "pos.maxlen": str(sentence_length),
    }

    if DoCleanXML:
        params["annotators"] = params["annotators"] + ",cleanXML"
        param_string_NN = param_string_NN + ",cleanXML"

    if "POS" in str(annotator_params) or "NER" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_POS_NER_maxlen,
            reminders_util.message_CoreNLP_POS_NER_maxlen,
            True,
        )

    # CLAUSAL TAGS (the neural-network parser does not produce clausal tags)

    if "parser (nn)" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_nn_parser,
            reminders_util.message_CoreNLP_nn_parser,
            True,
        )

    if "quote" in str(annotator_params):
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_CoreNLP_quote_annotator,
            reminders_util.message_CoreNLP_quote_annotator,
            True,
        )

    # record the number of pronouns
    all_pronouns = 0
    # annotating each input file
    docID = 0
    recordID = 0
    filesError = []
    errorFound = False
    total_length = 0
    # record the time consumption before annotating text in each file

    # The following options were tested to expedite processing time of CoreNLP
    # WORKED! 35% time reduction Test whether calling the local host inside or outside the for-loop is faster for various documents
    # DOES NOT WORK Increase and decrease the total amount of words within file and test the performance
    # DOES NOT WORK Test to see if file splitting process influences the performance

    nlp = StanfordCoreNLP(CORENLP_URL)

    # local test
    #     The corpus you have selected is too small for data reduction algorithms. These algorithms require a LARGE number of files.

    # Please, select a different corpus directory and try again.
    for docName in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(docName)
        logger.info("Processing file " + str(docID) + "/" + str(nDocs) + " " + tail)
        os.path.basename(docName)
        sentenceID = 0
        # if the file is too long, it needs splitting to allow processing by the Stanford CoreNLP
        #   which has a maximum 100,000 characters doc size limit
        # if ("SVO" in str(annotator_params) or "OpenIE" in str(annotator_params)) and "coref" in docName.split("_"):
        #     if len(split_file)>1:
        split_file = file_splitter_ByLength_util.splitDocument_byLength(config_filename, docName, "", document_length)
        nSplitDocs = len(split_file)
        split_docID = 0
        for doc_split in split_file:
            split_docID = split_docID + 1
            model_switch = False
            head_split, tail_split = os.path.split(doc_split)
            if docName != doc_split:
                logger.info("   Processing split file " + str(split_docID) + "/" + str(nSplitDocs) + " " + tail_split)
            text = open(doc_split, encoding=language_encoding, errors="ignore").read().replace("\n", " ")
            if "%" in text:
                reminders_util.checkReminder(
                    scriptName,
                    reminders_util.title_options_CoreNLP_percent,
                    reminders_util.message_CoreNLP_percent,
                    True,
                )
                text = text.replace("%", "percent")

            # if there's only one annotator and it uses neural nerwork model, skip annoatiting with PCFG to save time
            if param_string != "":
                annotator_start_time = time.time()
                CoreNLP_output = nlp.annotate(text, properties=params)
                errorFound, filesError, CoreNLP_output = IO_user_interface_util.process_CoreNLP_error(
                    CoreNLP_output, doc_split, nDocs, filesError, text, silent
                )
                if errorFound:
                    errorFound = False
                    continue  # move to next document
                annotator_time_elapsed = time.time() - annotator_start_time
                file_length = len(text)
                total_length += file_length
                speed_assessment.append(
                    [
                        docID,
                        IO_csv_util.dressFilenameForCSVHyperlink(doc_split),
                        annotator_time_elapsed,
                        file_length,
                        param_string,
                        param_number,
                    ]
                )
                # output the json output of CoreNLP to a txt file
                # TODO regardless of annotator,
                #   when for instance three are passed with * from NLP_parsers_annotators_main using annotators dropdown menu,
                #   we always process only the first one in the list
                exportJson(
                    export_json_var,
                    tail,
                    outputJsonDir,
                    CoreNLP_output,
                    language_encoding,
                    annotator_params[0],
                )  # only one annotator
            else:
                CoreNLP_output = ""

            # routine_list contains all annotators
            # loop through all annotators for the same document
            for run in routine_list:
                if errorFound:
                    continue  # move to next document; this only continues to next routine_list
                annotator_start_time = time.time()
                annotator_chosen = run[0]
                routine = run[1]
                output_format = run[2]
                parse_model = run[4]
                # when multiple annotators are selected (e.g., quote, gender, normalized-date)
                #   charts output must go to the appropriate subdirectory
                outputDir_chosen = run[5]
                outputJsonDir = run[6]
                if parse_model == "NN" and not model_switch:
                    model_switch = True
                    params_NN = params
                    params_NN["parse.model"] = lang_models["nn"]
                    params_NN["annotators"] = param_string_NN
                    if "quote" in param_string_NN and single_quote_var:
                        params_NN["quote.singleQuotes"] = True
                    NN_start_time = time.time()
                    CoreNLP_output = nlp.annotate(text, properties=params_NN)
                    errorFound, filesError, CoreNLP_output = IO_user_interface_util.process_CoreNLP_error(
                        CoreNLP_output, doc_split, nDocs, filesError, text, silent
                    )
                    if errorFound:
                        continue  # move to next document; this only continues to next routine_list
                    NN_time_elapsed = time.time() - NN_start_time
                    file_length = len(text)
                    total_length += file_length
                    speed_assessment.append(
                        [
                            docID,
                            IO_csv_util.dressFilenameForCSVHyperlink(doc_split),
                            NN_time_elapsed,
                            file_length,
                            param_string_NN,
                            param_number_NN,
                        ]
                    )
                    # export Json file to a txt file
                    # TODO regardless of annotator, when for instance three are passed,
                    #   we always process only the first one in the list
                    # exportJson(export_json_toTxt, tail, outputJsonDir, CoreNLP_output,
                    exportJson(
                        export_json_var,
                        tail_split,
                        outputJsonDir,
                        CoreNLP_output,
                        language_encoding,
                        annotator_chosen,
                    )

                #  generate output from json file for specific annotators ------------------------------------

                if "parser" in annotator_chosen:
                    if "pcfg" in annotator_chosen:
                        sub_result, recordID = routine(
                            config_filename, docID, docName, sentenceID, recordID, True, CoreNLP_output, **kwargs
                        )
                    else:
                        # neural network parser does not contain clause tags
                        sub_result, recordID = routine(
                            config_filename, docID, docName, sentenceID, recordID, False, CoreNLP_output, **kwargs
                        )
                elif "All POS" in annotator_chosen or "Lemma" in annotator_chosen:
                    sub_result, recordID = routine(
                        config_filename, docID, docName, sentenceID, recordID, CoreNLP_output, **kwargs
                    )
                elif ("SVO" in str(annotator_params) or "OpenIE" in str(annotator_params)) and "coref" in docName.split(
                    "_"
                ):
                    sub_result = routine(config_filename, split_docID, doc_split, sentenceID, CoreNLP_output, **kwargs)
                else:
                    sub_result = routine(config_filename, docID, docName, sentenceID, CoreNLP_output, **kwargs)
                if output_format == "text":  # this type of output format is for 'coref' annotator only
                    # coreference produces a text output;
                    # the coreferenced document should not include the prefix NLP_CoreNLP_coref
                    # (if the filename contains a date; the date position would change as a result and the code would break)
                    # count pronouns number:
                    all_pronouns += count_pronouns(CoreNLP_output)
                    outputFilename = outputDir_chosen + os.sep + tail
                    if sub_result != "":
                        with open(
                            outputFilename,
                            "a+",
                            encoding=language_encoding,
                            errors="ignore",
                        ) as output_text_file:
                            # insert the separators <@# #@> in the the output file so that the file can then be split on the basis of these characters
                            # for merging coreferenced files into a single merged file
                            # if processing_doc != docTitle:
                            output_text_file.write(sub_result)
                            ###
                        filesToOpen.append(outputFilename)
                    else:
                        IO_user_interface_util.timed_alert(
                            2000,
                            "Coreference resolution",
                            "The coreference resolution function did not produce any output for the input file "
                            + docName,
                            False,
                            "",
                            True,
                            "",
                            False,
                        )
                else:
                    # add output to the output storage list in routine_list
                    # for the special case of POS values of a double list [['Verbs'],[Nouns']] you need special handling
                    if POS_WordNet:
                        for i in range(0, len(run[2])):
                            for j in sub_result[i]:
                                run_output[i].append(j)
                    else:
                        run[3].extend(sub_result)
            try:
                if errorFound:
                    errorFound = False
                    continue  # move to next document; this only continues to next routine_list
                sentenceID_SV = sentenceID
                sentenceID += len(
                    CoreNLP_output["sentences"]
                )  # update the sentenceID of the first sentence of the next split file
            except Exception:
                logger.info("Error processing sentence #:  %s  in document  %s", sentenceID_SV + 1, tail)

    # generate output csv files and write output -----------------------------------------------

    time.time()
    outputFilename_tag = ""
    for run in routine_list:
        annotator_chosen = run[0]
        routine = run[1]
        output_format = run[2]
        # when multiple annotators are selected (e.g., quote, gender, normalized-date)
        #   charts output must go to the appropriate subdirectory
        outputDir_chosen = run[5]
        outputJsonDir = run[6]
        if not POS_WordNet:
            run_output = run[3]
        # skip coreferenced file
        if output_format == "text":
            continue
        if isinstance(output_format[0], list):  # multiple outputs
            for index, _sub_output in enumerate(output_format):
                if POS_WordNet:
                    outputFilename = IO_files_util.generate_output_file_name(
                        inputFilename,
                        inputDir,
                        outputDir_chosen,
                        ".csv",
                        "CoreNLP_" + annotator_chosen + "_lemma_" + output_format[index][0],
                    )
                else:
                    # @@@
                    outputFilename = IO_files_util.generate_output_file_name(
                        inputFilename,
                        inputDir,
                        outputDir_chosen,
                        ".csv",
                        "CoreNLP_" + annotator_chosen + "_lemma" + output_format[index][0],
                    )
                filesToOpen.append(outputFilename)
                df = pd.DataFrame(run_output[index], columns=output_format[index])
                df.to_csv(outputFilename, index=False, encoding=language_encoding)
        else:  # single, merged output
            # generate output file name
            if annotator_chosen == "NER":
                logger.info("Stanford CoreNLP annotator: NER")
                if len(kwargs["NERs"]) == 1:
                    outputFilename_tag = str(kwargs["NERs"][0])
                elif len(kwargs["NERs"]) > 10 and len(kwargs["NERs"]) < 20:
                    outputFilename_tag = "MISC"
                elif len(kwargs["NERs"]) > 20:
                    outputFilename_tag = "ALL_NER"
                else:
                    if (
                        "CITY" in str(kwargs["NERs"])
                        and "STATE_OR_PROVINCE"
                        and str(kwargs["NERs"])
                        and "COUNTRY" in str(kwargs["NERs"])
                        and "LOCATION" in str(kwargs["NERs"])
                    ):
                        outputFilename_tag = "LOCATIONS"
                    elif (
                        "NUMBER" in str(kwargs["NERs"])
                        and "ORDINAL"
                        and str(kwargs["NERs"])
                        and "PERCENT" in str(kwargs["NERs"])
                    ):
                        outputFilename_tag = "NUMBERS"
                    elif "PERSON" in str(kwargs["NERs"]) and "ORGANIZATION" in str(kwargs["NERs"]):
                        outputFilename_tag = "ACTORS"
                    elif (
                        "DATE" in str(kwargs["NERs"])
                        and "TIME" in str(kwargs["NERs"])
                        and "DURATION" in str(kwargs["NERs"])
                        and "SET" in str(kwargs["NERs"])
                    ):
                        outputFilename_tag = "DATES"
                outputFilename = IO_files_util.generate_output_file_name(
                    inputFilename,
                    inputDir,
                    outputDir_chosen,
                    ".csv",
                    "CoreNLP_NER_" + outputFilename_tag,
                )
            elif "parser" in annotator_chosen:
                if "pcfg" in annotator_chosen:
                    parser_label = "PCFG"
                else:
                    parser_label = "nn"
                outputFilename = IO_files_util.generate_output_file_name(
                    inputFilename,
                    inputDir,
                    outputDir_chosen,
                    ".csv",
                    "CoreNLP",
                    parser_label,
                    "CoNLL",
                )

            elif output_format != "text":
                # TODO any changes in the way the CoreNLP_annotator generates output filenames for sentiment analysis
                #    will affect the shape of stories algorithms (search TODO there)
                outputFilename = IO_files_util.generate_output_file_name(
                    inputFilename,
                    inputDir,
                    outputDir_chosen,
                    ".csv",
                    "CoreNLP_" + annotator_chosen,
                )
            filesToOpen.append(outputFilename)
            if output_format != "text" and not isinstance(output_format[0], list):  # output is csv file
                # when NER tags (notably, locations) are extracted with the date option
                #   for dynamic GIS maps (as called from GIS_main with date options)
                if extract_date_from_text_var or filename_embeds_date_var:
                    # 'Date' added at the end of the column list for SVO, for instance
                    output_format.append("Date")
                # save csv file with the expected header (i.e., output_format)
                df = pd.DataFrame(run_output, columns=output_format)
                IO_csv_util.df_to_csv(df, outputFilename, headers=output_format, index=False)
                # count the number of corefed pronouns (COREF annotator)
                if annotator_chosen == "coref table":
                    df.shape[0]

    # set filesToVisualize because filesToOpen will include xlsx files otherwise
    filesToVisualize = filesToOpen
    if "coref" in str(annotator_params):
        IO_user_interface_util.timed_alert(
            2000,
            "Analysis end",
            "Finished running Stanford CoreNLP " + str(annotator_params) + " annotator at",
            True,
            "The coreference annotator produces a coref subdirectory inside the main output directory containing 2 separate subdirectories in turn containing, respectively, the coreferenced input text files, and statistics csv and chart files with coreference data.",
            True,
            startTime,
        )
    else:
        IO_user_interface_util.timed_alert(
            2000,
            "Analysis end",
            "Finished running Stanford CoreNLP " + str(annotator_params) + " annotator at",
            True,
            "",
            True,
            startTime,
        )

    # generate visualization output ----------------------------------------------------------------

    for j in range(len(filesToVisualize)):
        # 02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j], encoding="utf-8", on_bad_lines="skip")
            if not file_df.empty:
                outputFilename = filesToVisualize[j]
                # when multiple annotators are selected (e.g., quote, gender, normalized-date)
                #   charts output must go to the appropriate subdirectory
                outputDir_chosen = os.path.dirname(outputFilename)
                outputFiles = parsers_annotators_visualization_util.parsers_annotators_visualization(
                    config_filename,
                    inputFilename,
                    inputDir,
                    outputDir_chosen,
                    outputFilename,
                    annotator_params,
                    kwargs,
                    chartPackage,
                    dataTransformation,
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

    # filesErroris a double list [[]] of headers and errors
    if len(filesError) > 0:
        IO_user_interface_util.timed_alert(
            2000,
            "Stanford CoreNLP Error",
            "Stanford CoreNLP "
            + annotator_chosen
            + " annotator has found "
            + str(len(filesError) - 1)
            + " files that could not be processed by Stanford CoreNLP.\n\nPlease, read the error output file carefully to see the errors generated by CoreNLP.",
            False,
            "",
            True,
            "",
            False,
        )
        errorFile = os.path.join(
            outputDir_chosen,
            IO_files_util.generate_output_file_name(
                IO_csv_util.dressFilenameForCSVHyperlink(inputFilename),
                inputDir,
                outputDir_chosen,
                ".csv",
                "CoreNLP",
                "file_ERRORS",
            ),
        )
        IO_csv_util.list_to_csv(filesError, errorFile, encoding=language_encoding)
        filesToOpen.append(errorFile)
    # record the time consumption of generating outputfiles and visualization
    # record the time consumption of running the whole analysis
    total_time_elapsed = time.time() - start_time
    speed_assessment.append(
        [
            -1,
            "Total Operation",
            total_time_elapsed,
            total_length,
            str(annotator_params),
            len(annotator_params),
        ]
    )
    speed_csv = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir_chosen, ".csv", "CoreNLP_speed_assessment"
    )
    df = pd.DataFrame(speed_assessment, columns=speed_assessment_format)
    df.to_csv(speed_csv, index=False, encoding=language_encoding)
    # if len(inputDir) != 0:

    return filesToOpen


CoreNLP_available_lang = ["Arabic, Chinese, English, French, German, Hungarian, Italian, Spanish"]

# https://stanfordnlp.github.io/CoreNLP/human-languages.html
# POS all languages
# lemma English only
# NER NOT available for Arabic
# constituency parsing NOT available for German
# dependency parsing NOT available for Arabic, and Hungarian
# sentiment analysis available for English
# mention detection available for Chinese, English
# coreference resolution available for Chinese, English
# OpenIE available for English
# def check_CoreNLP_annotator_availability(annotator_params, language, silent=False):
#     if language not in CoreNLP_available_lang:
#         if not silent:
#             mb.showerror("Warning",
#                          "Stanford CoreNLP does not currently support the " + str(
#                              annotator_params) + " annotator for " + language + ".\n\nPlease, select a different annotator or a different language.\n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the 'Setup NLP package and corpus language' to open the GUI where you can change the language option.")


def language_models(CoreNLPdir, language: str):
    if language == "English":
        pcfg_model = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        nn_model = "edu/stanford/nlp/models/parser/nndep/english_UD.gz"
    else:
        head, tail = os.path.split(CoreNLPdir)
        language_file = os.path.join(CoreNLPdir, tail + "-models-" + language.lower() + ".jar")
        CoreNLP_download = "https://stanfordnlp.github.io/CoreNLP/human-languages.html"
        if not os.path.isfile(language_file):
            logger.info(
                "Language pack %s",
                "You have selected to work with the "
                + language.upper()
                + " language. But the language model "
                + language_file
                + " was not found in the main directory of Stanford CoreNLP "
                + CoreNLPdir
                + "\n\nPlease, download the "
                + language.upper()
                + " language pack from the Stanford NLP website "
                + CoreNLP_download
                + " and move it to the main Stanford CoreNLP directory.\n\nWould you like to do that now?",
            )
            return
        pcfg_model = "edu/stanford/nlp/models/srparser/" + language.lower() + "SR.beam.ser.gz"
        nn_model = "edu/stanford/nlp/models/parser/nndep/UD_" + language + ".gz"

    result = {}
    result["pcfg"] = pcfg_model
    result["nn"] = nn_model
    return result


date_in_filename = IO_files_util.date_in_filename


from corenlp_json_discourse import (
    process_json_coref,
    process_json_coref_table,
    process_json_gender,
    process_json_quote,
)
from corenlp_json_gis import (
    count_pronouns,
)
from corenlp_json_ner import (
    process_json_ner,
    process_json_normalized_date,
    process_json_sentiment,
)
from corenlp_json_syntax import (
    exportJson,
    process_json_all_postag,
    process_json_deprel,
    process_json_lemma,
    process_json_openIE,
    process_json_parser,
    process_json_postag,
    process_json_sentence,
    process_json_SVO_enhanced_dependencies,
)
from util import collect
