# If there's an error that interrupted the operation within this script, PLEASE
#1. (In Terminal) Type in sudo lsof -i tcp:9000 see the PID of the subprocess occupying the port
#2. Type in kill -9 ***** to kill that subprocess
#P.S ***** is the 5 digit PID

"""
TODO
https://stanfordnlp.github.io/CoreNLP/memory-time.html
Check out the CoreNLP website to see their recommendation on using the -filelist flag
(e.g., java -cp "$STANFORD_CORENLP_HOME/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -filelist all-files.txt -outputFormat json)
and -parse.maxlen 70 or 100 to limit sentence length
there is also kbp.maxlen, ner.maxlen, and pos.maxlen but they be less necessary than the parse one
WE DO NOT USE ANY OF THESE RECOMMENDATIONS
"""

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoreNLP_annotator", ['os', 'tkinter','time','json','re','subprocess','string','pandas','pycorenlp','nltk'])==False:
    sys.exit(0)

from typing import Any, Tuple
# import pprint
import json
import os
import re
import subprocess
import string
# not using stanfordcorenlp because it is not recognizing sentiment annotator
import nltk
from pycorenlp import StanfordCoreNLP
from tkinter import messagebox as mb
import tkinter as tk
import pandas as pd
import time
import Stanford_CoreNLP_clause_util
import csv

import IO_csv_util
import file_splitter_ByLength_util
import file_splitter_merged_txt_util
import IO_files_util
import IO_user_interface_util
import Stanford_CoreNLP_SVO_enhanced_dependencies_util # Enhanced++ dependencies
import reminders_util
import NLP_parsers_annotators_visualization_util
import charts_util

# when multiple annotators are selected (e.g., quote, gender, normalized-date)
#   output must go to the appropriate subdirectory
# the function creates the subdirectory for a given annotator
def create_output_directory(inputFilename, inputDir, outputDirSV, config_filename,
                            export_json_toTxt, annotator,silent, Json_question_already_asked):
    outputJsonDir = ''
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDirSV,
                                                       label="CoreNLP_" + annotator,
                                                       silent=False)
    # Json_question_already_asked to avoid repeating the reminders question when multiple annotators are used
    if (outputDir !='') and (export_json_toTxt and not Json_question_already_asked):
        # check reminder
        reminder_status = reminders_util.checkReminder(config_filename,
                                                       reminders_util.title_options_CoreNLP_Json,
                                                       reminders_util.message_CoreNLP_Json,
                                                       True, silent)
        if reminder_status == 'Yes' or reminder_status == 'ON':  # 'Yes' the old way of saving reminders
            # create a subdirectory of the output directory
            outputJsonDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                                   label='Json',
                                                                   silent=True)
        else:
            export_json_toTxt = False

    return outputDir, outputJsonDir, export_json_toTxt

def check_CoreNLP_language(config_filename,annotator,language):
    not_available = False
    url = 'https://stanfordnlp.github.io/CoreNLP/human-languages.html'
    CoreNLP_web='\n\nLanguage and annotator options for Stanford CoreNLP are listed at the Stanford CoreNLP website ' + url
    if "lemma" in annotator.lower():
        if language != 'English':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP LEMMA annotator is only available for English.'+CoreNLP_web)
            not_available = True
    elif "normalized" in annotator.lower():
        if language != 'English':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP NORMALIZED NER annotator is only available for English.'+CoreNLP_web)
            not_available = True
    elif "gender" in annotator.lower():
        if language != 'English':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP GENDER annotator is only available for English.'+CoreNLP_web)
            not_available = True
    elif "quote" in annotator.lower():
        if language != 'English':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP QUOTE annotator is only available for English.'+CoreNLP_web)
            not_available = True
    elif "OpenIE" in annotator.lower():
        if language != 'English':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP OPENIE annotator is only available for English.'+CoreNLP_web)
            not_available = True
    elif "sentiment" in annotator.lower():
        if language != 'English' and language != 'Chinese':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP SENTIMENTT ANALYSIS annotator is only available for Chinese and English.' + CoreNLP_web)
            not_available = True
    elif "coreference" in annotator.lower():
        if language != 'English' and language != 'Chinese':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP COREFERENCE RESOLUTION annotator is only available for Chinese and English.' + CoreNLP_web)
            not_available = True
    elif "PCFG" in annotator.lower():
        if language == 'English' or language == 'German':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP PCFG PARSER is not available for German and Hungarian.'+CoreNLP_web)
            not_available = True
    elif "neural network" in annotator.lower(): #parser
        if language == 'Arabic' or language == 'Hungarian':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP NEURAL NETWORK PARSER is not available for Arabic and Hungarian.'+CoreNLP_web)
            not_available = True
    elif "SVO" in annotator.lower(): #parser
        if language == 'Arabic' or language == 'Hungarian':
            mb.showwarning(title=str(annotator).upper() + ' annotator availability for ' + language,
                           message='The Stanford CoreNLP SVO annotator is not available for Arabic and Hungarian.'+CoreNLP_web)
            not_available = True
    if not_available:
        reminder_status = reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_CoreNLP_website,
                                     reminders_util.message_CoreNLP_website,
                                     True)
        if reminder_status == 'Yes' or reminder_status == 'ON': # 'Yes' the old way of saving reminders
            # open website
            website_name = 'CoreNLP website'
            message_title = 'CoreNLP website'
            message="Would you like to open the Stanford CoreNLP website for annotator availability for the various languages supported by CoreNLP?"
            IO_libraries_util.open_url(website_name, url, ask_to_open=True, message_title=message_title, message=message)
    return not(not_available) # failed

# from operator import itemgetter, attrgetter
# central CoreNLP_annotator function that pulls together our approach to processing many files,
# splitting them if necessary, and, depending upon annotator (NER date, quote, gender, sentiment)
# perhaps call different subfunctions, and pulling together the output

# CHOOSE YOUR OPTION FOR variable: annotator_params in option below
# tokenize: tokenize
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

def CoreNLP_annotate(config_filename,inputFilename,
                     inputDir, outputDir,
                     openOutputFiles, createCharts, chartPackage,
                     annotator_params,
                     DoCleanXML,
                     language,
                     memory_var,
                     document_length=90000,
                     sentence_length=1000, # unless otherwise specified; sentence length limit does not seem to work for parsers only for NER and POS but then it is useless
                     export_json_toTxt = True,
                     **kwargs):
    silent=True
    start_time = time.time()
    speed_assessment = []#storing the information used for speed assessment
    speed_assessment_format = ['Document ID', 'Document','Time', 'Tokens to Annotate', 'Params', 'Number of Params']#the column titles of the csv output of speed assessment
    # start_time = time.time()#start time
    filesToOpen = []
    # check that the CoreNLPdir has been setup
    CoreNLPdir, missing_external_software=IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_annotator', 'Stanford CoreNLP')
    if CoreNLPdir== None:
        return filesToOpen
    # check the version of CoreNLP
    IO_libraries_util.check_CoreNLPVersion(CoreNLPdir)

    # check for Java
    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('Stanford CoreNLP')
    if errorFound:
        return filesToOpen

    # check available memory
    IO_libraries_util.check_avaialable_memory('Stanford CoreNLP')

    # decide on directory or single file
    if inputDir != '':
        inputFilename = inputDir
    # decide on to provide output or to return value

    # global extract_date_from_text_var, extract_date_from_filename_var
    extract_date_from_text_var=False
    extract_date_from_filename_var=False
    single_quote_var = False
    date_format = ''
    date_separator_var = ''
    date_position_var = 0
    date_str = ''
    # language initialized here and reset later in language = value
    NERs = []
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            extract_date_from_text_var = True
        if key == 'NERs':
            NERs = value
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
        if key == 'date_format':
            date_format = value
        if key == 'date_separator_var':
            date_separator_var = value
        if key == 'date_position_var':
            date_position_var = value
        if key == 'single_quote_var':
            single_quote_var = value

    global language_encoding
    if language == 'English':
        language_encoding='utf-8'
    else:
        language_encoding='utf-8-sig'

    produce_split_files=False


    params_option = {
        'Sentence': {'annotators':['ssplit']},
        'tokenize': {'annotators':['tokenize']},
        'MWT': {'annotators': ['tokenize','ssplit','mwt']},
        'Lemma': {'annotators': ['lemma']},
        'POS': {'annotators': ['tokenize','ssplit','pos','lemma']},
        'All POS':{'annotators': ['tokenize','ssplit','pos','lemma']},
        'DepRel': {'annotators': ['parse']},
        'NER': {'annotators':['tokenize','ssplit','pos','lemma','ner']},
        'quote': {'annotators': ['tokenize','ssplit','pos','lemma','ner','depparse','coref','quote']},
        'coref': {'annotators': ['coref']},
        'coref table': {'annotators': ['coref']},
        'gender': {'annotators': ['coref']},
        'sentiment': {'annotators':['sentiment']},
        'normalized-date': {'annotators': ['tokenize','ssplit','ner']},
        'SVO':{"annotators": ['tokenize','ssplit','pos','depparse','natlog','lemma', 'ner', 'coref', 'quote']},
        'OpenIE':{"annotators": ['tokenize','ssplit','natlog','openie','ner']},
        'parser (pcfg)':{"annotators": ['tokenize','ssplit','pos','lemma','ner', 'parse','regexner']},
        'parser (nn)' :{"annotators": ['tokenize','ssplit','pos','lemma','ner','depparse','regexner']}
    }

    routine_option = {
        'Sentence': process_json_sentence,
        'sentiment': process_json_sentiment,
        'Lemma': process_json_lemma,
        'POS':process_json_postag,
        'All POS':process_json_all_postag,
        'NER': process_json_ner,
        'DepRel':process_json_deprel,
        'quote': process_json_quote,
        'coref': process_json_coref,
        'coref table': process_json_coref_table,
        'gender': process_json_gender,
        'normalized-date':process_json_normalized_date,
        'OpenIE':process_json_openIE,
        'SVO':process_json_SVO_enhanced_dependencies,
        'parser (pcfg)': process_json_parser,
        'parser (nn)': process_json_parser
    }
    #@ change coref-text to coref, change coref-spreadsheet to gender@
    output_format_option = {
        'Sentence': ['Sentence ID', 'Sentence','Sentence Length (Number of Tokens)','Number of Intra-Sentence Punctuation Symbols (),;-', 'Document ID', 'Document'],
        'Lemma': ["ID", "Form", "Lemma", "Record ID", "Sentence ID", "Document ID", "Document"],
        'POS':[['Verbs'],['Nouns']],
        'All POS':["ID", "Form", "POStag", "Record ID", "Sentence ID", "Document ID", "Document"],
        'NER': ['Word', 'NER Tag', 'tokenBegin', 'tokenEnd', 'Sentence ID', 'Sentence', 'Document ID','Document'],
        # TODO NER with date for dynamic GIS; modified below
        # 'NER': ['Word', 'NER Tag', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document', 'Date'],
        'DepRel': ["ID", "Form", "Head", "DepRel", "Record ID", "Sentence ID", "Document ID", "Document"],
        'sentiment': ['Sentiment score', 'Sentiment label', 'Sentence ID', 'Sentence', 'Document ID', 'Document'],
        'quote': ['Speakers', 'Number of Quotes', 'Sentence ID', 'Sentence', 'Document ID', 'Document'],
        'coref': 'text',
        'coref table': ["Pronoun", "Reference", "Reference Start ID in Sentence",
                        "First Reference Sentence ID", "First Reference Sentence", "Pronoun Start ID in Reference Sentence", "Sentence ID", "Sentence", "Document ID", "Document"],
        'gender':['Word', 'Gender', 'Sentence ID', 'Sentence','Document ID', 'Document'],
        'normalized-date':["Word", "Normalized date", "tid","Date type","Sentence ID", "Sentence", "Document ID", "Document"],
        'SVO':['Subject (S)', 'Verb (V)', 'Object (O)', "Negation","Location",'Person','Time','Time normalized NER','Sentence ID', 'Sentence','Document ID', 'Document'],
        'OpenIE':['Subject (S)', 'Verb (V)', 'Object (O)', "Negation", "Location", 'Person', 'Time',
                   'Time normalized NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document'],
        # Chen
        # added Deps column
        'parser (pcfg)':["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"],
        # neural network parser does not contain clause tags
        'parser (nn)':["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"]
    }

    if not isinstance(annotator_params,list):
        annotator_params = [annotator_params]
    outputDirSV=outputDir
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True)


    lang_models = language_models(CoreNLPdir, language)
    if lang_models == None:
        return filesToOpen
    param_number = 0
    param_number_NN = 0
    files = []#storing names of txt files
    nDocs = 0#number of input documents

    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # get corresponding func, output format and annotator params from upper 3 dicts
    # routine_list is a list of 4 items:
    #   annotator [0], e.g., NER
    #   output format [2]( headers), typically a single list [], and in the case of POS annotator for WordNet, a douuble list [[].[]]
    # Neural_Network = False
    routine_list = []#storing the annotator, output format (column titles of csv), output
    # if not isinstance(annotator_params,list):
    #     annotator_params = [annotator_params]
    param_string = ''#the input string of nlp annotator properties
    param_string_NN = ''
    # param_list = []
    # param_list_NN = []
    corefed_pronouns = 0#pronouns that are corefed
    Json_question_already_asked = False
    for annotator in annotator_params:
        if not check_CoreNLP_language(config_filename, annotator, language):
            continue
        if "gender" in annotator or "quote" in annotator or "coref" in annotator or "SVO" in annotator or "OpenIE" in annotator or ("parser" in annotator and "nn" in annotator):
            print("Using neural network model")
            neural_network = True
            parse_model = "NN"
        else:
            neural_network = False
            parse_model = "PCFG"
        routine = routine_option.get(annotator)
        output_format = output_format_option.get(annotator)
        annotators_ = params_option.get(annotator)["annotators"]
        # annotators_ = params_option.get(annotator).get("annotators")
        #tokenize each property
        # put all annotators whose parse model is neural network at the end of the list
        # so that the model would just need be switched once
        if neural_network:
            # param_number_NN = 0
            for param in annotators_:
                if not param in param_string_NN: #the needed annotator property is not containted in the string
                    param_number_NN += 1
                    if param_string_NN == '':
                        param_string_NN = param
                    else:
                        param_string_NN = param_string_NN + ", " + param
                        param_string_NN = param_string_NN + ", " + param
            # when multiple annotators are selected (e.g., quote, gender, normalized-date)
            #   output must go to the appropriate subdirectory and added to routine_list
            output_dir, outputJsonDir, export_json_toTxt = create_output_directory(inputFilename, inputDir, outputDirSV, config_filename, export_json_toTxt, annotator, silent, Json_question_already_asked)
            if output_dir == '':
                return filesToOpen
            # when running the SVO annotator in combination with gender and quote,
            #   you want to put the gender and quote folders inside the SVO folder
            if 'SVO' in annotator and ("gender" in annotator_params or "quote" in annotator_params):
                outputDirSV=output_dir
            Json_question_already_asked = True
            routine_list.append([annotator, routine,output_format,[],parse_model, output_dir, outputJsonDir])
        else:
            for param in annotators_:
                if not param in param_string: #the needed annotator property is not containted in the string
                    param_number += 1
                    if param_string == '':
                        param_string = param
                    else:
                        param_string = param_string + ", " + param
            # when multiple annotators are selected (e.g., quote, gender, normalized-date)
            #   output must go to the appropriate subdirectory and added to routine_list
            output_dir, outputJsonDir, export_json_toTxt = create_output_directory(inputFilename, inputDir, outputDirSV, config_filename, export_json_toTxt, annotator, silent, Json_question_already_asked)
            if output_dir == '':
                return filesToOpen
            # when running the SVO annotator in combination with gender and quote,
            #   you want to put the gender and quote folders inside the SVO folder
            if 'SVO' in annotator and ("gender" in annotator_params or "quote" in annotator_params):
                outputDirSV=output_dir
            Json_question_already_asked = True
            routine_list.insert(0, [annotator, routine,output_format,[],parse_model, output_dir, outputJsonDir])

    # the third item in routine_list is typically a single list [],
    #   but for POS it becomes a double list ['Verbs'],[Nouns]]
    #   the case needs special handling
    POS_WordNet=False
    if routine_list==[]: # when the language check fails for an annotator
        return filesToOpen
    if isinstance(routine_list[0][2][0],list):
        run_output = [[], []]
        POS_WordNet=True
    else:
        run_output = []
        POS_WordNet=False

    params = {'annotators':param_string,
                'parse.model': lang_models['pcfg'],
                'outputFormat': 'json',
                'outputDirectory': outputDir,
                'replaceExtension': True,
                'parse.maxlen': str(sentence_length),
                'ner.maxlen': str(sentence_length),
                'pos.maxlen': str(sentence_length)}

    if DoCleanXML:
        params['annotators'] = params['annotators'] + ',cleanXML'
        param_string_NN = param_string_NN + ',cleanXML'

    # -d64 to use 64 bits JAVA, normally set to 32 as default; option not recognized in Mac
    if sys.platform == 'darwin':  # Mac OS
        # mx is the same as Xmx and refers to maximum Java heap size
        # '-props spanish',
        if language == 'English':
            CoreNLP_nlp = subprocess.Popen(
                ['java', '-mx' + str(memory_var) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
                 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer',  '-parse.maxlen' + str(sentence_length), '-timeout', '999999'])
        else:
            CoreNLP_nlp = subprocess.Popen(
                ['java', '-mx' + str(memory_var) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
                 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer','-props', language.lower(),
                 '-parse.maxlen' + str(sentence_length), '-timeout', '999999'])

    else:
        # CoreNLP_nlp = subprocess.Popen(
        #     ['java', '-mx' + str(memory_var) + "g", '-d64', '-cp',  os.path.join(CoreNLPdir, '*'),
        #      'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-parse.maxlen' + str(sentence_length),'-timeout', '999999'])
        if language == 'English':
            CoreNLP_nlp = subprocess.Popen(
                ['java', '-mx' + str(memory_var) + "g", '-cp',  os.path.join(CoreNLPdir, '*'),
                 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-parse.maxlen' + str(sentence_length),'-timeout', '999999'])
        else:
            CoreNLP_nlp = subprocess.Popen(
                ['java', '-mx' + str(memory_var) + "g", '-cp',  os.path.join(CoreNLPdir, '*'),
                 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-props', language.lower(),
                 '-parse.maxlen' + str(sentence_length),'-timeout', '999999'])

    time.sleep(5)

    if 'POS' in str(annotator_params) or 'NER' in str(annotator_params):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_CoreNLP_POS_NER_maxlen,
            reminders_util.message_CoreNLP_POS_NER_maxlen,
            True)

    # CLAUSAL TAGS (the neural-network parser does not produce clausal tags)

    if 'parser (nn)' in str(annotator_params):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_CoreNLP_nn_parser,
            reminders_util.message_CoreNLP_nn_parser,
            True)

    if 'quote' in str(annotator_params):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_CoreNLP_quote_annotator,
            reminders_util.message_CoreNLP_quote_annotator,
            True)

    # record the number of pronouns
    all_pronouns = 0
    # annotating each input file
    docID=0
    recordID = 0
    filesError=[]
    # json = True
    errorFound=False
    total_length = 0
    # record the time consumption before annotating text in each file
    processing_doc = ''
    for docName in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(docName)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        docTitle = os.path.basename(docName)
        sentenceID = 0
        # if the file is too long, it needs splitting to allow processing by the Stanford CoreNLP
        #   which has a maximum 100,000 characters doc size limit
        if ("SVO" in str(annotator_params) or "OpenIE" in str(annotator_params)) and "coref" in docName.split("_"):
            split_file = file_splitter_merged_txt_util.run(docName, "<@#", "#@>", outputDir)
            if len(split_file)>1:
                split_file = IO_files_util.getFileList("", split_file[0], fileType=".txt")
        else:
            split_file = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,config_filename,docName,'',document_length)
        nSplitDocs = len(split_file)
        split_docID = 0
        for doc in split_file:
            split_docID = split_docID + 1
            annotated_length = 0#the number of tokens
            # doc_start_time = time.time()
            model_switch = False
            head, tail = os.path.split(doc)
            if docName != doc:
                print("   Processing split file " + str(split_docID) + "/" + str(nSplitDocs) + ' ' + tail)
            text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")
            if "%" in text:
                reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_percent,
                                             reminders_util.message_CoreNLP_percent, True)
                text=text.replace("%","percent")
            nlp = StanfordCoreNLP('http://localhost:9000')
            # nlp = StanfordCoreNLP('http://point.dd.works:9000')

            #if there's only one annotator and it uses neural nerwork model, skip annoatiting with PCFG to save time
            if param_string != '':
                annotator_start_time = time.time()
                CoreNLP_output = nlp.annotate(text, properties=params)
                errorFound, filesError, CoreNLP_output = IO_user_interface_util.process_CoreNLP_error(GUI_util.window,
                                                    CoreNLP_output,
                                                    doc,
                                                    nDocs,
                                                    filesError,
                                                    text,
                                                    silent)
                if errorFound:
                    errorFound=False
                    continue  # move to next document
                annotator_time_elapsed = time.time() - annotator_start_time
                file_length=len(text)
                total_length += file_length
                speed_assessment.append(
                    [docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), annotator_time_elapsed, file_length,
                     param_string, param_number])
                #output the json output of CoreNLP to a txt file
                # TODO regardless of annotator,
                #   when for instance three are passed with * from NLP_parsers_annotators_main using annotators dropdown menu,
                #   we always process only the first one in the list
                exportJson(export_json_toTxt, tail, outputJsonDir, CoreNLP_output,
                               language_encoding, annotator_params[0]) # only one annotator
            else: CoreNLP_output = ""

            # routine_list contains all annotators
            # loop through all annotators for the same document
            for run in routine_list:
                annotator_start_time = time.time()
                # params = run[0]
                annotator_chosen = run[0]
                routine = run[1]
                output_format = run[2]
                parse_model = run[4]
                # when multiple annotators are selected (e.g., quote, gender, normalized-date)
                #   charts output must go to the appropriate subdirectory
                outputDir_chosen = run[5]
                outputJsonDir = run[6]
                if parse_model == "NN" and model_switch == False:
                    model_switch = True
                    params_NN = params
                    params_NN['parse.model'] = lang_models['nn']
                    params_NN['annotators'] = param_string_NN
                    if "quote" in param_string_NN and single_quote_var:
                        print("debugging: Include Single Quote")
                        params_NN["quote.singleQuotes"] = True
                    NN_start_time = time.time()
                    CoreNLP_output = nlp.annotate(text, properties=params_NN)
                    errorFound, filesError, CoreNLP_output = IO_user_interface_util.process_CoreNLP_error(
                        GUI_util.window, CoreNLP_output, doc, nDocs, filesError, text, silent)
                    if errorFound:
                        continue  # move to next document; this only continues to next routine_list
                    NN_time_elapsed = time.time() - NN_start_time
                    file_length = len(text)
                    total_length += file_length
                    speed_assessment.append(
                        [docID, IO_csv_util.dressFilenameForCSVHyperlink(doc), NN_time_elapsed, file_length,
                         param_string_NN, param_number_NN])
                    # export Json file to a txt file
                    # TODO regardless of annotator, when for instance three are passed, we always process only the first one in the list
                    # exportJson(export_json_toTxt, tail, outputJsonDir, CoreNLP_output,
                    #            language_encoding, #annotator_params[0])
                    exportJson(export_json_toTxt, tail, outputJsonDir, CoreNLP_output,
                               language_encoding, annotator_chosen)

#  generate output from json file for specific annotators ------------------------------------

                if "parser" in annotator_chosen:
                    if "pcfg" in annotator_chosen:
                        sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID, True,CoreNLP_output, **kwargs)
                    else:
                        # neural network parser does not contain clause tags
                        sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID, False,CoreNLP_output, **kwargs)
                elif "All POS" in annotator_chosen or "Lemma" in annotator_chosen:
                    sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID,
                                               CoreNLP_output, **kwargs)
                # elif "DepRel" in annotator_chosen or "All POS" in annotator_chosen or "Lemma" in annotator_chosen:
                #      sub_result, recordID = routine(config_filename,docID, docName, sentenceID, recordID, CoreNLP_output, **kwargs)
                elif ("SVO" in str(annotator_params) or "OpenIE" in str(annotator_params)) and "coref" in docName.split("_"):
                    sub_result = routine(config_filename, split_docID, doc, sentenceID, CoreNLP_output, **kwargs)
                else:
                    sub_result = routine(config_filename,docID, docName, sentenceID, CoreNLP_output, **kwargs)

                if output_format == 'text':
                    #count pronouns number:
                    all_pronouns += count_pronouns(CoreNLP_output)
                    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,
                                                                             outputDir_chosen, '.txt',
                                                                             'CoreNLP_'+ str(annotator_chosen))
                    with open(outputFilename, "a+", encoding=language_encoding, errors='ignore') as output_text_file:
                        # insert the separators <@# #@> in the the output file so that the file can then be split on the basis of these characters
                        if processing_doc != docTitle:
                            output_text_file.write("\n<@#" + docTitle + "#@>\n")
                            processing_doc = docTitle
                        output_text_file.write(sub_result)
                    if outputFilename not in filesToOpen:
                        filesToOpen.append(outputFilename)
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
                    errorFound=False
                    continue  # move to next document; this only continues to next routine_list
                sentenceID_SV = sentenceID
                sentenceID += len(CoreNLP_output["sentences"])#update the sentenceID of the first sentence of the next split file
            except:
                print("Error processing sentence #: ",sentenceID_SV+1," in document ",tail)

# generate output csv files and write output -----------------------------------------------

    output_start_time = time.time()
    # print("Length of Files to Open after generating output: ", len(filesToOpen))
    outputFilename_tag = ''
    for run in routine_list:
        annotator_chosen = run[0]
        routine = run[1]
        output_format = run[2]
        # when multiple annotators are selected (e.g., quote, gender, normalized-date)
        #   charts output must go to the appropriate subdirectory
        outputDir_chosen = run[5]
        outputJsonDir = run[6]
        if POS_WordNet == False:
            run_output = run[3]
        # skip coreferenced file
        if output_format == "text":
            continue
        if isinstance(output_format[0],list): # multiple outputs
            for index, sub_output in enumerate(output_format):
                if POS_WordNet:
                    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_chosen, '.csv',
                                                                             'CoreNLP_'+annotator_chosen+'_lemma_'+output_format[index][0])
                else:
                    outputFilename = IO_files_util.generate_output_file_name(str(doc), inputDir, outputDir_chosen,'.csv',
                                                                              'CoreNLP_'+annotator_chosen+'_lemma'+output_format[index][0])
                filesToOpen.append(outputFilename)
                df = pd.DataFrame(run_output[index], columns=output_format[index])
                df.to_csv(outputFilename, index=False, encoding=language_encoding)
        else: # single, merged output
            # generate output file name
            if annotator_chosen == 'NER':
                print("Stanford CoreNLP annotator: NER")
                if len(kwargs['NERs']) == 1:
                    outputFilename_tag = str(kwargs['NERs'][0])
                elif len(kwargs['NERs'])>10 and len(kwargs['NERs'])<20:
                    outputFilename_tag = 'MISC'
                elif len(kwargs['NERs'])>20:
                    outputFilename_tag = 'ALL_NER'
                else:
                    if 'CITY' in str(kwargs['NERs']) and 'STATE_OR_PROVINCE' and str(kwargs['NERs']) and 'COUNTRY' in str(kwargs['NERs']) and 'LOCATION' in str(kwargs['NERs']):
                        outputFilename_tag='LOCATIONS'
                    elif 'NUMBER' in str(kwargs['NERs']) and 'ORDINAL' and str(kwargs['NERs']) and 'PERCENT' in str(kwargs['NERs']):
                        outputFilename_tag = 'NUMBERS'
                    elif 'PERSON' in str(kwargs['NERs']) and 'ORGANIZATION' in str(kwargs['NERs']):
                        outputFilename_tag = 'ACTORS'
                    elif 'DATE' in str(kwargs['NERs']) and 'TIME' in str(kwargs['NERs']) and 'DURATION' in str(kwargs['NERs']) and 'SET' in str(kwargs['NERs']):
                        outputFilename_tag = 'DATES'
                    # else:
                    #     outputFilename_tag = 'Multi-tags'
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_chosen, '.csv',
                                                                                 'CoreNLP_NER_'+outputFilename_tag)
            elif "parser" in annotator_chosen:
                if "pcfg" in annotator_chosen:
                    parser_label = 'PCFG'
                else:
                    parser_label = 'nn'
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,
                                                    outputDir_chosen, '.csv', 'CoreNLP', parser_label, 'CoNLL')

            elif output_format != 'text':
                # TODO any changes in the way the CoreNLP_annotator generates output filenames for sentiment analysis
                #    will affect the shape of stories algorithms (search TODO there)
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,
                                                                         outputDir_chosen, '.csv',
                                                                         'CoreNLP_'+annotator_chosen)
            filesToOpen.append(outputFilename)
            if output_format != 'text' and not isinstance(output_format[0],list): # output is csv file
                # when NER tags (notably, locations) are extracted with the date option
                #   for dynamic GIS maps (as called from GIS_main with date options)
                if extract_date_from_text_var or extract_date_from_filename_var:
                    # 'Date' added at the end of the column list for SVO, for instance
                    output_format.append("Date")
                # save csv file with the expected header (i.e., output_format)
                df = pd.DataFrame(run_output, columns=output_format)
                IO_csv_util.df_to_csv(GUI_util.window, df, outputFilename, headers=output_format, index=True)
                #count the number of corefed pronouns (COREF annotator)
                if annotator_chosen == 'coref table':
                    corefed_pronouns = df.shape[0]

    # print("Length of Files to Open after generating files: ", len(filesToOpen))
    # set filesToVisualize because filesToOpen will include xlsx files otherwise
    filesToVisualize=filesToOpen
    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True, '', True, startTime)

    # generate visualization output ----------------------------------------------------------------

    for j in range(len(filesToVisualize)):
        #02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j])
            if not file_df.empty:
                outputFilename = filesToVisualize[j]
                # when multiple annotators are selected (e.g., quote, gender, normalized-date)
                #   charts output must go to the appropriate subdirectory
                outputDir_chosen = os.path.dirname(outputFilename)
                chart_outputFilename = NLP_parsers_annotators_visualization_util.parsers_annotators_visualization(
                    config_filename, inputFilename, inputDir, outputDir_chosen,
                    outputFilename, annotator_params, kwargs, createCharts,
                    chartPackage)
                if chart_outputFilename!=None:
                    if len(chart_outputFilename) > 0:
                        filesToOpen.extend(chart_outputFilename)

    CoreNLP_nlp.kill()
    # print("Length of Files to Open after visualization: ", len(filesToOpen))
    if len(filesError)>0:
        mb.showwarning("Stanford CoreNLP Error", 'Stanford CoreNLP ' +annotator_chosen+ ' annotator has found '+str(len(filesError)-1)+' files that could not be processed by Stanford CoreNLP.\n\nPlease, read the error output file carefully to see the errors generated by CoreNLP.')
        errorFile = os.path.join(outputDir,
                                           IO_files_util.generate_output_file_name(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename), inputDir, outputDir, '.csv',
                                                                                   'CoreNLP', 'file_ERRORS'))
        IO_csv_util.list_to_csv(GUI_util.window, filesError, errorFile, encoding=language_encoding)
        filesToOpen.append(errorFile)
    # record the time consumption of generating outputfiles and visualization
    # record the time consumption of running the whole analysis
    total_time_elapsed = time.time() - start_time
    # speed_assessment.append(["Total Operation", -1, total_time_elapsed,'', '', 0])
    speed_assessment.append([-1, "Total Operation", total_time_elapsed,total_length, str(annotator_params), len(annotator_params)])
    speed_csv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_chosen, '.csv',
                                                                           'CoreNLP_speed_assessment')
    df = pd.DataFrame(speed_assessment, columns=speed_assessment_format)
    df.to_csv(speed_csv, index=False, encoding=language_encoding)
    # if len(inputDir) != 0:
    #     IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Output warning', 'The output filename generated by Stanford CoreNLP is the name of the directory processed in input, rather than any individual file in the directory. The output file(s) include all ' + str(nDocs) + ' files in the input directory processed by CoreNLP.\n\nThe different files are listed in the output csv file under the headers \'Document ID\' and \'Document\'.')

    return filesToOpen


def language_models(CoreNLPdir, language: str):
    if language == 'English':
        pcfg_model = 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'
        nn_model = 'edu/stanford/nlp/models/parser/nndep/english_UD.gz'
    else:
        head, tail = os.path.split(CoreNLPdir)
        language_file = os.path.join(CoreNLPdir, tail + "-models-" + language.lower() + ".jar")
        CoreNLP_download = "https://stanfordnlp.github.io/CoreNLP/human-languages.html"
        if not os.path.isfile(language_file):
            answer = tk.messagebox.askyesno(title='Language pack', message="You have selected to work with the " + language.upper() + " language. But the language model " +
                                language_file + " was not found in the main directory of Stanford CoreNLP " +
                                CoreNLPdir + "\n\nPlease, download the " + language.upper() + " language pack from the Stanford NLP website " + CoreNLP_download + " and move it to the main Stanford CoreNLP directory.\n\nWould you like to do that now?")
            if answer:
                if not IO_libraries_util.open_url('Stanford CoreNLP', CoreNLP_download):
                    return
            return
        pcfg_model = 'edu/stanford/nlp/models/srparser/' + language.lower() + 'SR.beam.ser.gz'
        nn_model = 'edu/stanford/nlp/models/parser/nndep/UD_' + language  +'.gz'
    result = {}
    result['pcfg'] = pcfg_model
    result['nn'] = nn_model
    return result


def check_sentence_length(sentence_length, sentenceID, config_filename):
    # WARNING for sentences with > 100 tokens
    if sentence_length > 100:
        order = "th"
        if sentenceID % 10 == 1:
            order = "st"
        elif sentenceID % 10 == 2:
            order = "nd"
        elif sentenceID % 10 == 3:
            order = "rd"

        print("   Warning: The", str(sentenceID) + order, "sentence has " + str(sentence_length) + " words, more than the 100 max recommended by CoreNLP for best performance.")
        reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_sentence_length,
                                     reminders_util.message_CoreNLP_sentence_length, True)


def build_sentence_string (sentence):
    complete_sent = ''
    for token in sentence['tokens']:
        if token['originalText'] in string.punctuation:
            complete_sent = complete_sent + token['originalText']
        else:
            if token['index'] == 1:
                complete_sent = complete_sent + token['originalText']
            else:
                complete_sent = complete_sent + ' ' + token['originalText']
    return complete_sent

def date_in_filename(document, **kwargs):
    extract_date_from_filename_var = False
    date_format = ''
    date_separator_var = ''
    date_position_var = 0
    date_str = ''
    # process the optional values in kwargs
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
        if key == 'date_format':
            date_format = value
        if key == 'date_separator_var':
            date_separator_var = value
        if key == 'date_position_var':
            date_position_var = value
    if extract_date_from_filename_var:
        date, date_str = IO_files_util.getDateFromFileName(document, date_separator_var, date_position_var,
                                                           date_format)
    return date_str

# ["Word", "Normalized date", "tid","tense","Date type","Sentence ID", "Sentence", "Document ID", "Document"],
def date_get_tense(norm_date):
    tense = ''
    # print(norm_date)
    if (len(norm_date) >= 9 and 'OFFSET P-' in norm_date) or "PAST" in norm_date:
        # print('past')
        tense = 'PAST'
    elif len(norm_date) >= 6 and 'OFFSET' in norm_date:
        # print("future")
        tense = 'FUTURE'
    elif 'THIS' in norm_date or 'PRESENT' in norm_date:
        tense = 'PRESENT'
        # print('present')
    else:
        tense = "OTHER" # TODO separate out days of week, months of year
    return tense

# def date_get_tense(norm_date):

def process_json_normalized_date(config_filename,documentID, document, sentenceID,json, **kwargs):
    print("   Processing Json output file for NER NORMALIZED DATE annotator")
    extract_date_from_filename_var = False

    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    temp = []
    for sentence in json['sentences']:
        complete_sent = ''
        # sentenceID = sentence['index'] + 1
        sentenceID = sentenceID + 1
        words = ''
        norm_date = ''
        tid = ''
        #tense = ''
        info = ''
        for token in sentence['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']
            word = token['word']
            if token['ner'] == 'DATE':
                if norm_date == '':
                    norm_date = token['normalizedNER']
                    try:
                        tid = token['timex']['tid']
                    except:
                        print('   tid error')
                        tid=''
                    #tense = date_get_tense(norm_date)
                    info = date_get_info(norm_date)
                    if info == "OTHER":
                        info = date_get_tense(norm_date)
                    words = word + words
                elif token['normalizedNER'] != norm_date:
                    # writer.writerow([words,norm_date, sentence_id, sent_str, documentID,file])
                    if extract_date_from_filename_var:
                        temp = [words, norm_date, tid,  info, sentenceID, complete_sent, documentID,
                                             IO_csv_util.dressFilenameForCSVHyperlink(document), date_str]
                    else:
                        temp = [words, norm_date, tid, info, sentenceID, complete_sent, documentID,
                                         IO_csv_util.dressFilenameForCSVHyperlink(document)]
                    result.append(temp)
                    words = word
                    norm_date = token['normalizedNER']
                    try:
                        tid = token['timex']['tid']
                    except:
                        print('   tid error')
                        tid=''
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
                if words != '' or norm_date != '':
                    # writer.writerow([words,norm_date, sentence_id, sent_str, documentID, file])
                    if extract_date_from_filename_var:
                        temp = [words, norm_date, tid, info, sentenceID, complete_sent, documentID,
                                         IO_csv_util.dressFilenameForCSVHyperlink(document), date_str]

                    else:
                        temp = [words, norm_date, tid, info, sentenceID, complete_sent, documentID,
                                         IO_csv_util.dressFilenameForCSVHyperlink(document)]
                    result.append(temp)
                    words = ''
                    norm_date = ''
                    tid = ''
                    #tense = ''
                    info = ''

        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

    return result

def date_get_info(norm_date):
    norm_date = norm_date.strip()
    tense = 'OTHER'
        # print(norm_date)
    if norm_date.isdigit() or (norm_date[0] == "-" and norm_date.replace('-', '').isdigit()):
        tense = "YEAR"
    elif norm_date[-2:] == "XX" and (norm_date[0:-2].isdigit() or (norm_date[0] == "-" and norm_date[0:-2].replace('-', '').isdigit())):
        tense = "CENTURY"
    elif len(norm_date) == 7 and norm_date[-2:].isdigit() and norm_date[4] == "-":
        tense = "MONTH"
    elif norm_date.replace('-', '').isdigit() or norm_date.replace('/', '').isdigit() or ("XXXX" in norm_date and norm_date.split("XXXX")[1].replace("-", '').isdigit()):#(len(norm_date) > 4 and norm_date[0:4] == 'XXXX' and norm_date[4:].replace("-", '').isdigit()):#specific year,month, day
        tense = "DATE"
        # print("date")
    elif 'WXX' in norm_date or "WE" in norm_date:#weekdays
        tense = "DAY"
        # print("day")
    elif 'SP' in norm_date or 'SU' in norm_date or 'FA' in norm_date or 'WI' in norm_date:
        tense = "SEASON"
        # print("season")
    # else:
    #     tense = "OTHER"
    return tense

def process_json_ner(config_filename,documentID, document, sentenceID, json, **kwargs):
    print("   Processing Json output file for NER annotator")
    # establish the kwarg local vars
    extract_date_from_text_var = False
    extract_date_from_filename_var = False
    request_NER = []
    # date_format = ''
    # date_separator_var = ''
    # date_position_var = 0
    # date_str = ''
    # process the optional values in kwargs
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            extract_date_from_text_var = True
        if key == 'NERs':
            request_NER = value
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
        # if key == 'date_format':
        #     date_format = value
        # if key == 'date_separator_var':
        #     date_separator_var = value
        # if key == 'date_position_var':
        #     date_position_var = value
    # print("With date embed in titles: ", extract_date_from_filename_var)
    # print("With date embed in text contents: ", extract_date_from_text_var)
    NER = []
    result = []
    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    if date_str!='':
        print("Date in this file: ", date_str)
    # if extract_date_from_filename_var:
    #     date, date_str = IO_files_util.getDateFromFileName(document, date_separator_var, date_position_var,
    #                                                        date_format)

    for sentence in json['sentences']:
        complete_sent = ''
        for token in sentence['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']
        # TODO to be checked; formerly commented out but then the Sentence ID field was always displayed as 0
        sentenceID = sentence['index'] + 1
        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        for ner in sentence['entitymentions']:
            temp = [ner['text'], ner['ner'], ner['tokenBegin'],
                    ner['tokenEnd'],sentenceID, complete_sent,  documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document)]
            # check in NER tag column
            if temp[1] in request_NER:
                if extract_date_from_filename_var:
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
                            if re.match(r'\d{4}-\d{2}-\d{2}', date_val):
                                norm_date = date_val
                            else:
                                # date did not match required format
                                norm_date = ""
                        except:
                            print("normalizedNER not available.")
                            norm_date = ""
                        temp.append(norm_date)
                        NER.append(temp)
                    else:
                        NER.append(temp)
                result.append(temp)

    #    disconnect the next lines because they are causing more problems than solutions
    # index = 0
    # while index < len(NER):
    #     temp = NER[index]
    #     if NER[index][1] == 'CITY':
    #         if index < len(NER)-1: # NER[index + 1] would break the code
    #             # check if a city is followed by EITHER state/province OR country e.g., Atlanta, Georgia or Atlanta, United States
    #             if NER[index + 1][1] == 'STATE_OR_PROVINCE' or NER[index + 1][1] == 'COUNTRY':
    #                 temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
    #                 index = index + 1
    #                 # check if a city and state/province are also followed by country e.g., Atlanta, Georgia, United States
    #                 if index < len(NER) - 1:
    #                     if NER[index + 1][1] == 'COUNTRY':
    #                         temp[0] = temp[0] + ', ' + NER[index + 1][0]
    #                         index = index + 1
    #     elif NER[index][1] == 'STATE_OR_PROVINCE':
    #         if index < len(NER)-1: # NER[index + 1] would break the code
    #             # check if a state/province  is followed by a country e.g., Georgia, United States
    #             if NER[index + 1][1] == 'COUNTRY':
    #                 temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
    #                 index = index + 1
    #     result.append(temp)
    #     index = index + 1
    return result

def process_json_sentiment(config_filename,documentID, document, sentenceID,json, **kwargs):
    print("   Processing Json output file for SENTIMENT annotator")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    sentiment = []
    for sentence in json["sentences"]:
        sentenceID += 1
        text = ""
        for token in sentence['tokens']:
           if token['originalText'] in string.punctuation:
               text = text + token['originalText']
           else:
               if token['index'] == 1:
                   text = text + token['originalText']
               else:
                   text = text + ' ' + token['originalText']

        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        if extract_date_from_filename_var:
            temp = [sentence["sentimentValue"], sentence["sentiment"].lower(), date_str, sentence['index'] + 1, text,documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)]
        else:
            temp = [sentence["sentimentValue"], sentence["sentiment"].lower(), sentence['index'] + 1, text, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)]
        sentiment.append(temp)
    return sentiment


def process_json_coref(config_filename,documentID, document, sentenceID, json, **kwargs):
    print("   Processing Json output file for COREF annotator")

    def resolve(corenlp_output):
        """ Transfer the word form of the antecedent to its associated pronominal anaphor(s) """
        for coref in corenlp_output['corefs']:
            mentions = corenlp_output['corefs'][coref]
            antecedent = mentions[0]  # the antecedent is the first mention in the coreference chain
            for j in range(1, len(mentions)):
                mention = mentions[j]
                if mention['type'] == 'PRONOMINAL':
                    # get the attributes of the target mention in the corresponding sentence
                    target_sentence = mention['sentNum']
                    target_token = mention['startIndex'] - 1
                    # transfer the antecedent's word form to the appropriate token in the sentence
                    corenlp_output['sentences'][target_sentence - 1]['tokens'][target_token]['word'] = antecedent[
                        'text']

    # when possessive pronouns are substituted by an antecedent noun, the noun must be followed by 's
    #   unless the noun already has the gerundive 's
    #   Mary took her exam; Mary took Mary's exam
    def get_resolved(corenlp_output, sentenceID):
        """ get the "resolved" output as String """
        result = ''
        # possessive pronouns: my, mine, his, her(s), its, our(s), their, yours
        possessives = ["her", "hers", "his", "its", "our", "ours", "their", "theirs", "your", "yours"]
        pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "her", "him", "us", "them", "my", "mine",
                             "hers", "his", "its", "our", "ours", "their", "your", "yours", "myself", "yourself", "himself", "herself",
                             "oneself", "itself", "ourselves", "yourselves", "themselves"]
        for sentence in corenlp_output['sentences']:
            sentenceID += 1
            for token in sentence['tokens']:
                output_word = token['word']
                # check lemmas as well as tags for possessive pronouns in case of tagging errors
                if token['lemma'] in possessives or token['pos'] == 'PRP$':
                    if not "'s" in output_word and output_word not in pronouns:
                        output_word += "'s"  # add the possessive morpheme
                output_word += token['after']
                if output_word == ". ":
                    if result[-1] == ".":
                        continue
                result = result + output_word
            check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        return result

    resolve(json)
    output_text = get_resolved(json, sentenceID)
    return output_text

# def count_pronoun(json):
#     nn = 0
#     for sentence in json['sentences']:
#         # sentenceID = sentenceID + 1
#         for token in sentence['tokens']:
#             if token["pos"] == "PRP$" or token["pos"] == "PRP":
#                 nn += 1
#     return nn


def process_json_coref_table(config_filename, documentID, document, sentenceID, json, **kwargs):
    result = []  # the collection of information of each coreference
    for coref in json['corefs']:
        mentions = json['corefs'][coref]
        reference = mentions[0]  # First Reference in context

        ref_sent = json['sentences'][reference["sentNum"] - 1]
        ref_sent_ID = reference["sentNum"]  # First Reference Sentence ID
        ref_sent_string = build_sentence_string(ref_sent)  # First Reference Sentence
        ref_start_ID = reference["startIndex"]  # Reference Start ID in Sentence
        ref_text = reference["text"]  # first reference
        for j in range(1, len(mentions)):

            mention = mentions[j]

            if mention["type"] == "PRONOMINAL":  # extract only pronouns
                ment_text = mention["text"]
                ment_sent = json['sentences'][mention["sentNum"] - 1]
                ment_sent_ID = mention["sentNum"]  # sentence ID
                ment_sent_string = build_sentence_string(ment_sent)  # sentence
                ment_start_ID = mention["startIndex"]  # start ID in sentence
                result.append([ment_text, ref_text, ref_start_ID, ref_sent_ID, ref_sent_string,
                               ment_start_ID, ment_sent_ID, ment_sent_string,
                               documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
    return result

# December.10 Yi: Modify process_json_gender to provide one more column(complete sentence)
def process_json_gender(config_filename,documentID, document, start_sentenceID, json, **kwargs):

    # print("CoreNLP output: ")
    # pprint.pprint(json)
    print("   Processing Json output file for GENDER annotator")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    mentions = []
    sent_dict = {}
    for sentence in json['sentences']:
        # sentenceID = sentenceID + 1
        complete_sent = ''
        for token in sentence['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']
        sentenceID = sentence['index'] + 1

        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        sent_dict[sentenceID] = complete_sent
    # print("Coreference: ")
    # pprint.pprint(json['corefs'])
    for num, res in json['corefs'].items():
        mentions.append(res)
    for mention in mentions:
        for elmt in mention:
            if elmt['gender'] in ['NEUTRAL', 'UNKNOWN']:
                continue
            else:
                # get complete sentence
                complete = sent_dict[elmt['sentNum']]
                if extract_date_from_filename_var:
                    result.append([elmt['text'], elmt['gender'], elmt['sentNum'] + start_sentenceID, complete, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), date_str])
                else:
                    result.append([elmt['text'], elmt['gender'], elmt['sentNum'] + start_sentenceID, complete, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])

    # return result
    return sorted(result, key=lambda x:x[3]) # this function did not add each row in order of sentence, so the output needs sorting by sentenceID


def process_json_quote(config_filename,documentID, document, sentenceID, json, **kwargs):
    print("   Processing Json output file for QUOTE annotator")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    quoted_sentences = {}
    speakers = {}#the speakers of each quote
    for quote in json['quotes']:
        # quote_text = quote['text']
        # to find all sentences with quotes
        sentenceIDs = list(range(quote['beginSentence'], quote['endSentence'] + 1))
        for sent in sentenceIDs:
            quoted_sentences[sent] = quoted_sentences.get(sent, 0) + 1
            if sent in speakers.keys():
                speakers[sent].append(quote['speaker'])
            else:
                speakers[sent] = [quote['speaker']]
    # iterate over those sentence indexes and find its complete sentence
    for quoted_sent_id, number_of_quotes in quoted_sentences.items():
        sentenceID = quoted_sent_id+1
        sentence_data = json['sentences'][quoted_sent_id]
        # for sentence in CoreNLP_output['sentences']:
        complete_sent = ''
        for token in sentence_data['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']

        check_sentence_length(len(sentence_data['tokens']), sentenceID, config_filename)

        if extract_date_from_filename_var:
            temp = [str(speakers[quoted_sent_id][0]), number_of_quotes, date_str, sentenceID,
                    complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)]
        else:
            temp = [str(speakers[quoted_sent_id][0]), number_of_quotes, sentenceID, complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)]
        result.append(temp)
    return result

def process_json_sentence(config_filename, documentID, document, sentenceID, json, **kwargs):
    temp = []
    # [ 'Sentence ID', 'Sentence', 'Document ID', 'Document'],
    for sentence in json['sentences']:  # traverse output of each sentence
        sentence_length=0
        number_punctuations = 0
        complete_sent = ''  # build sentence string
        for token in sentence['tokens']:
            # check for basic symbols that make long sentences
            if token['word']==',' or token['word']==';' or token['word']=='(' or token['word']==')' or token['word']=='-':
                number_punctuations=number_punctuations+1
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']
            sentence_length=sentence_length+1
        sentenceID = sentenceID + 1
        temp.append([sentenceID, complete_sent, sentence_length, number_punctuations, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
    return temp



# Dec. 21
def process_json_SVO_enhanced_dependencies(config_filename,documentID, document, sentenceID, json, **kwargs):
    #extract date from file name
    extract_date_from_filename_var = False
    gender_var = False
    quote_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
        if key == "gender_var" and value == True:
            gender_var = True
        if key == "quote_var" and value == True:
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
        quote_info = []
        for row in raw_quote_info:
            # quote_info.append([row[0], row[1], row[2], row[3], row[4], row[5]])
            quote_info.append([row[0], row[1], row[2], row[4]])

    SVO_enhanced_dependencies = []
    SVO_brief = []
    locations = [] # a list of [sentence, sentence id, [location_text, ner_value]]
    for sentence in json['sentences']:#traverse output of each sentence
        sent_data = Stanford_CoreNLP_SVO_enhanced_dependencies_util.SVO_enhanced_dependencies_sent_data_reorg(sentence)#reorganize the output into a dictionary in which each content (also dictionary) contains information of a token
        #including a dictionary (govern_dictionary) indicating the index of tokens whose syntactical head is the current token

        complete_sent = ''#build sentence string
        for token in sentence['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']

        sentenceID = sentenceID + 1
        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        # CYNTHIA: feed another information sentence['entitymentions'] to SVO_extraction to get locations
        SVO, L, NER_value, T, T_S, P, N = Stanford_CoreNLP_SVO_enhanced_dependencies_util.SVO_extraction(sent_data, sentence['entitymentions'])# main function
        nidx = 0

        #CYNTHIA: " ".join(L) => "; ".join(L)
        # ; added list of locations in SVO output (e.g., Los Angeles; New York; Washington)
        for row in SVO:
            # SVO_brief.append([sentenceID, complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), row[0], row[1], row[2]])
            SVO_brief.append([row[0], row[1], row[2], sentenceID, complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
            if extract_date_from_filename_var:
                SVO_enhanced_dependencies.append([row[0], row[1], row[2], N[nidx], "; ".join(L), "; ".join(P), " ".join(T), "; ".join(T_S), sentenceID,complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document),date_str])
            else:
                SVO_enhanced_dependencies.append([row[0], row[1], row[2], N[nidx], "; ".join(L), "; ".join(P), " ".join(T), "; ".join(T_S), sentenceID,complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
            nidx += 1
        # for each sentence, get locations
        if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True and len(L) != 0:
            # produce an intermediate location file
            locations.append([sentenceID, complete_sent, [[x,y] for x,y in zip(L,NER_value)]])

    if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True:
        visualize_GIS_maps(kwargs, locations, documentID, document, date_str)

    # merge gender information with SVO information
    if gender_var:
        SVO_df = pd.DataFrame(SVO_brief, columns=['Subject (S)', 'Verb (V)', 'Object (O)', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
        gender_df = pd.DataFrame(gender_info, columns=["Subject (S)", "S Gender", "Sentence Set", "Document ID"])
        merge_df = pd.merge(SVO_df, gender_df, on=["Subject (S)", "Document ID"], how='left')

        gender_df = pd.DataFrame(gender_info, columns=["Object (O)", "O Gender", "Sentence Set", "Document ID"])
        merge_df = pd.merge(merge_df, gender_df, on=["Object (O)", "Document ID"], how='left')

        merge_df = merge_df[['Subject (S)', 'S Gender', 'Verb (V)', 'Object (O)', 'O Gender', 'Sentence ID','Sentence', 'Document ID', 'Document']]
        merge_df = merge_df.drop_duplicates()
        # TODO unfortunately, saving the file in the proper directory runs into problems with visualization
        # save the output file in the gender subdirectory
        # # remove the file, add the gender subdirectory, and re-add the file
        # head, tail = os.path.split(kwargs["gender_filename"])
        # # remove SVO from tail and .csv
        # temp_outputDir = tail.replace('_SVO', '')[:-4]
        # # remove NLP_
        # temp_outputDir = temp_outputDir[4:]
        # fn = head + os.sep + temp_outputDir + os.sep + tail
        # # save the output file in the quote subdirectory
        fn = kwargs["gender_filename"]
        merge_df.to_csv(fn, index=False, mode="a", encoding=language_encoding)

    if quote_var:
        SVO_df = pd.DataFrame(SVO_brief, columns=['Subject (S)', 'Verb (V)', 'Object (O)', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
        quote_df = pd.DataFrame(quote_info, columns=["Speakers", "Number of Quotes", "Sentence ID", "Document ID"])
        merge_df = pd.merge(SVO_df, quote_df, on=["Sentence ID", "Document ID"], how='left')
        merge_df = merge_df[['Subject (S)', 'Verb (V)', 'Object (O)', "Speakers", "Number of Quotes", "Sentence ID", "Sentence", "Document ID", "Document"]]
        merge_df = merge_df.drop_duplicates()

        # TODO unfortunately, saving the file in the proper directory runs into problems with visualization
        # save the output file in the gender subdirectory
        # remove the file, add the gender subdirectory, and re-add the file
        # head, tail = os.path.split(kwargs["gender_filename"])
        # # remove SVO from tail and .csv
        # temp_outputDir = tail.replace('_SVO', '')[:-4]
        # # remove NLP_
        # temp_outputDir = temp_outputDir[4:]
        # fn = head + os.sep + temp_outputDir + os.sep + tail
        # # save the output file in the quote subdirectory
        fn = kwargs["quote_filename"]
        merge_df.to_csv(fn, index=False, mode="a", encoding=language_encoding)

    return SVO_enhanced_dependencies

def process_json_openIE(config_filename,documentID, document, sentenceID, json, **kwargs):
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
    date_str = date_in_filename(document, **kwargs)

    openIE = []
    locations = [] # a list of [sentence, sentence id, [location_text, ner_value]]
    for sentence in json['sentences']:
        entitymentions = sentence['entitymentions']
        complete_sent = ''
        N = []  # list that stores the Negation information appear in sentences
        L = []  # list that stores the location information appear in sentences
        NER_value = []
        T = []  # list that stores the time information appear in sentences
        T_S = []  # list that stores normalized form of the time information appear in sentences
        P = []  # list that stores person names appear in sentences
        # CYNTHIA: get locations from entitymentions
        for item in entitymentions:
            if item["ner"] is not None and item["ner"] in ['STATE_OR_PROVINCE', 'COUNTRY', "CITY", "LOCATION"]:
                L.append(item["text"])
                NER_value.append(item["ner"])
        for token in sentence['tokens']:
            if token["ner"] == "TIME" or token["ner"] == "DATE":
                T.append(token["word"])
                # T_S.append(token['normalizedNER'])
                try:
                    T_S.append(token['normalizedNER'])
                except:
                    print("normalizedNER not available.")
            if token["ner"] == "PERSON":
                P.append(token["word"])

            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']
        sentenceID = sentenceID + 1

        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        SVOs = []
        for openie in sentence['openie']:
            # Document ID, Sentence ID, Document, S, V, O, Sentence
            SVOs.append([openie['subject'],openie['relation'],openie['object']])
        container = []
        for SVO_value in SVOs:
            redundant_flag = False
            remainder = [elmt for elmt in SVOs if elmt != SVO_value]
            for SVO_base in remainder:
                SVO_value_str = SVO_value[0] + ' ' + SVO_value[1] + ' ' + SVO_value[2]
                SVO_base_str = SVO_base[0] + ' ' + SVO_base[1] + ' ' + SVO_base[2]
                if SVO_value[0] == SVO_base[0] and similar_string_floor_filter(SVO_value_str,SVO_base_str):
                    redundant_flag = True
                    break
                else:
                    continue
            if not redundant_flag:
               container.append(SVO_value)
        if len(container) > 0:
            for row in container:
                if extract_date_from_filename_var:
                    openIE.append([row[0], row[1], row[2], 'N/A', "; ".join(L), "; ".join(P), " ".join(T), "; ".join(T_S),date_str, sentenceID, complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
                else:
                    openIE.append([row[0], row[1], row[2], 'N/A', "; ".join(L), "; ".join(P), " ".join(T), "; ".join(T_S), sentenceID, complete_sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
                # nidx += 1
        # for each sentence, get locations
        if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True and len(L) != 0:
            # produce an intermediate location file
            locations.append([sentenceID, complete_sent, [[x,y] for x,y in zip(L,NER_value)]])

    if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True:
        visualize_GIS_maps(kwargs, locations, documentID, document, date_str)

    return openIE

def process_json_lemma(config_filename, documentID, document, sentenceID, recordID, json, **kwargs):
    print("   Processing Json output file for Lemma")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []

        clauseID = 0
        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            #     print("NER normalized DATE ",row["normalizedNER"])
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            temp.append(row["lemma"])
            # temp.append(" ")
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            # temp.append(file)
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if extract_date_from_filename_var:
                temp.append(date_str)
            result.append(temp)

        check_sentence_length(len(tokens), sentenceID, config_filename)
    return result, recordID

def process_json_postag(config_filename,documentID, document, sentenceID, json, **kwargs):
    # only processes verbs and nouns
    Verbs = []
    Nouns = []
    for sentence in json['sentences']:
        sentenceID += 1
        # if len(sentence)> 20:
        #     print("WAY TOO LOONG!")
        for token in sentence['tokens']:
            if token['pos'] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
                Verbs.append(token['lemma'])
            elif token['pos'] in ['NN','NNP','NNS']:
                Nouns.append(token['lemma'])

        check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

    return Verbs, Nouns


# floor filter: if edit distance is smaller than 5
# (round-up average length of one English word, check this reference:
# https://wolfgarbe.medium.com/the-average-word-length-in-english-language-is-4-7-35750344870f)
# return True, which means the two strings are very similar
def process_json_all_postag(config_filename,documentID, document, sentenceID, recordID, json, **kwargs):
    print("   Processing Json output file for All Postags")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []

        clauseID = 0
        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            #     print("NER normalized DATE ",row["normalizedNER"])
            temp = []
            temp.append(row["index"])
            temp.append(row["word"])
            temp.append(row["pos"])
            # temp.append(" ")
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            # temp.append(file)
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if extract_date_from_filename_var:
                temp.append(date_str)
            result.append(temp)
            # print("Row in the CSV: ")
            # print(temp)
            # if dateInclude == 1 and dateStr!='DATE ERROR!!!':
            #     temp.append(dateStr)

        # print("The result after adding the ", sentenceID, "th sentence: ")
        # pprint.pprint(result)

        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID

def process_json_deprel(config_filename,documentID, document, sentenceID, recordID,json, **kwargs):
    print("   Processing Json output file for DepRel")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []
        clauseID = 0
        tokens = json["sentences"][i]["tokens"]
        dependencies = json["sentences"][i]["enhancedDependencies"]
        depLib = {}
        keys = []
        for item in dependencies:
            depLib[item['dependent']] = (item['dep'], item['governor'])
            keys.append(item['dependent'])
        depID = 1
        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            #     print("NER normalized DATE ",row["normalizedNER"])
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
            # temp.append(file)
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if extract_date_from_filename_var:
                temp.append(date_str)
            result.append(temp)

        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID

# processes both lemma and POS
def process_json_single_annotation(config_filename, documentID, document, sentenceID, recordID, annotation, json, **kwargs):
    print("   Processing Json output file for All Postags and Lemma")
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []

    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []

        tokens = json["sentences"][i]["tokens"]

        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            #     print("NER normalized DATE ",row["normalizedNER"])
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
            # temp.append(file)
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if extract_date_from_filename_var:
                temp.append(date_str)
            result.append(temp)


        check_sentence_length(len(tokens), sentenceID, config_filename)

    return result, recordID

def process_json_parser(config_filename, documentID, document, sentenceID, recordID, pcfg, json, **kwargs):
    print("   Processing Json output file for Parser")
    old_recordID = recordID
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # get date string of this sub file
    date_str = date_in_filename(document, **kwargs)
    result = []
    # neural network parser does not contain clausal tags (e.g., NP, VP,...)
    if pcfg:
        sent_list_clause = [Stanford_CoreNLP_clause_util.clausal_info_extract_from_string(parsed_sent['parse'])
                            for parsed_sent in json['sentences']]
    # else: a reminder is posted at the end
    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []
        # neural network parser does not contain clause tags
        if pcfg:
            cur_clause = sent_list_clause[i]
        clauseID = 0
        tokens = json["sentences"][i]["tokens"]
        dependencies = json["sentences"][i]["enhancedDependencies"]
        #try enhancedPlusPlus instead
        #dependencies = json["sentences"][i]["enhancedPlusPlusDependencies"]
        depLib = {}
        enhancedDepLib = {}
        keys = []
        for item in dependencies:
            depLib[item['dependent']] = (item['dep'], item['governor'])

            #create an enhanced dependency list
            if item['dependent'] in enhancedDepLib:
                enhancedDepLib[item['dependent']].append((item['dep'], item['governor']))
            else:
                enhancedDepLib[item['dependent']] = [(item['dep'], item['governor'])]


            keys.append(item['dependent'])
        depID = 1
        for row in tokens:
            recordID += 1
            # if row["ner"]=="DATE":
            #     print("NER normalized DATE ",row["normalizedNER"])
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
                #Add enhanced dep here
                depString = ""
                dep: Tuple[int, str]
                for dep in enhancedDepLib[depID]:
                    if len(depString) != 0:
                        depString = depString + "|"
                    depString = depString + str(dep[1]) + ":" + str(dep[0])
                temp.append(depString)

            depID += 1
            if pcfg:
                temp.append(cur_clause[clauseID][0])
            else: # neural network parser does not contain clause tags
                temp.append("")
            # temp.append(" ")
            clauseID += 1
            temp.append(str(recordID))
            temp.append(str(sentenceID))
            temp.append(str(documentID))
            # temp.append(file)
            temp.append(IO_csv_util.dressFilenameForCSVHyperlink(document))
            if extract_date_from_filename_var:
                temp.append(date_str)
            result.append(temp)

    return result, recordID


def exportJson(export_json_toTxt, inputFilename, outputJsonDir, CoreNLP_output,
               language_encoding, annotator_params):
        if not export_json_toTxt:
            return
        if outputJsonDir!='':
            jsonFilename = os.path.join(outputJsonDir, inputFilename[:-4] + "_" + str(annotator_params) + ".txt")
            with open(jsonFilename, "a+", encoding=language_encoding, errors='ignore') as json_out_nn:
                json.dump(CoreNLP_output, json_out_nn, indent=4, ensure_ascii=False)
        # no need to open the Json file
        # if jsonFilename not in filesToOpen:
        #     filesToOpen.append(jsonFilename)


def similar_string_floor_filter(str1, str2):
    dist = nltk.edit_distance(str1, str2)
    if dist <= 5:
        return True
    else:
        return False

# From Tony Chen Gu to Everyone 10:03 PM
def get_csv_column_unique_val_list(inputFilename, col):
    '''
    inputFilename (str) : csv file path
    col (int)           : the column number of the desired colum
    returns (list)      : list of unique values in the csv file
    '''
    data = pd.read_csv(inputFilename, encoding='utf-8')
    return list(set(data.iloc[:col]))


def visualize_GIS_maps(kwargs, locations, documentID, document, date_str):
    # columns: Location, NER Tag, Sentence ID, Sentence, Document ID, Document
    to_write = []
    for sent in locations:
        for locs in sent[2]:
            if ("extract_date_from_text_var" in kwargs and kwargs["extract_date_from_text_var"] == True) \
                    or (
                    "extract_date_from_filename_var" in kwargs and kwargs["extract_date_from_filename_var"] == True):
                to_write.append(
                    [locs[0], locs[1], sent[0], sent[1], documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), date_str]
                )
            else:
                to_write.append(
                    [locs[0], locs[1], sent[0], sent[1], documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
    columns = ["Location", "NER Tag", "Sentence ID", "Sentence", "Document ID", "Document"]
    if ("extract_date_from_text_var" in kwargs and kwargs["extract_date_from_text_var"] == True) \
        or ("extract_date_from_filename_var" in kwargs and kwargs["extract_date_from_filename_var"] == True):
        columns = ["Location", "NER Tag", "Sentence ID", "Sentence", "Document ID", "Document", "Date"]

    df = pd.DataFrame(to_write, columns=columns)

    if not os.path.exists(kwargs["location_filename"]):
        df.to_csv(kwargs["location_filename"], header='column_names', index=False, encoding=language_encoding)
    else:
        df.to_csv(kwargs["location_filename"], mode='a', header=False, index=False, encoding=language_encoding)

def count_pronouns(json):
    result = 0
    for sentence in json['sentences']:
        # sentenceID = sentenceID + 1
        for token in sentence['tokens']:
            if token["pos"] == "PRP$" or token["pos"] == "PRP":
                result += 1
    return result


def check_pronouns(config_filename, inputFilename, outputDir, filesToOpen, createCharts,chartPackage, option, corefed_pronouns, all_pronouns: int):
    return_files = []
    df = pd.read_csv(inputFilename)
    if df.empty:
        return return_files
    # pronoun cases:
    #   nominative: I, you, he/she, it, we, they
    #   objective: me, you, him, her, it, them
    #   possessive: my, mine, his/her(s), its, our(s), their, your, yours
    #   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves
    pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "her", "him", "us", "them", "my", "mine", "hers", "his", "its", "our", "ours", "their", "your", "yours", "myself", "yourself", "himself", "herself", "oneself", "itself", "ourselves", "yourselves", "themselves"]
    total_count = 0
    pronouns_count = {"i": 0, "you": 0, "he": 0, "she": 0, "it": 0, "we": 0, "they": 0, "me": 0, "her": 0, "him": 0, "us": 0, "them": 0, "my": 0, "mine": 0, "hers": 0, "his": 0, "its": 0, "our": 0, "ours": 0, "their": 0, "your": 0, "yours": 0, "myself": 0, "yourself": 0, "himself": 0, "herself": 0, "oneself": 0, "itself": 0, "ourselves": 0, "yourselves": 0, "themselves": 0}
    for _, row in df.iterrows():
        if option == "SVO":
            if (not pd.isna(row["Subject (S)"])) and (str(row["Subject (S)"]).lower() in pronouns):
                total_count+=1
                pronouns_count[str(row["Subject (S)"]).lower()] += 1
            if (not pd.isna(row["Object (O)"])) and (str(row["Object (O)"]).lower() in pronouns):
                total_count+=1
                pronouns_count[str(row["Object (O)"]).lower()] += 1
        elif option == "CoNLL":
            if (not pd.isna(row["Form"])) and (row["Form"].lower() in pronouns):
                total_count+=1
                pronouns_count[row["Form"].lower()] += 1
        elif option == "coref table":
            if (not pd.isna(row["Pronoun"])):
                total_count += 1
                try:
                    # some pronouns extracted by CoreNLP coref as such may not be in the list
                    #   e.g., "we both" leading to error
                    pronouns_count[row["Pronoun"].lower()] += 1
                except:
                    continue
        else:
            print ("Wrong Option value!")
            return []
    pronouns_count["I"] = pronouns_count.pop("i")
    if total_count > 0:
        if option != "coref table":
            reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_pronouns,
                                         reminders_util.message_CoreNLP_pronouns, True)
            return return_files
        else:
            #for coref, total count = number of resolved pronouns, the all_pronouns in the input is the number
            #   of all pronouns in the text
            coref_rate = round((corefed_pronouns / all_pronouns) * 100, 2)
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Coreference results',
                "Number of pronouns: " + str(
                all_pronouns) + "\nNumber of coreferenced pronouns: " + str(
                corefed_pronouns) + "\nPronouns coreference rate: " + str(coref_rate))
            # save to csv file and run visualization
            outputFilename= IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv','coref-sum')
            with open(outputFilename, "w", newline="", encoding='utf-8', errors='ignore') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(
                    ["Number of Pronouns", "Number of Coreferenced Pronouns", "Pronouns Coreference Rate"])
                writer.writerow([all_pronouns, corefed_pronouns, coref_rate])
                csvFile.close()
            # no need to display since the chart will contain the values
            # return_files.append(outputFilename)

            if createCharts:
                columns_to_be_plotted_xAxis=[]
                columns_to_be_plotted_yAxis=["Number of Pronouns", "Number of Coreferenced Pronouns", "Pronouns Coreference Rate"]
                chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                                   outputDir,
                                                                   columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                                   chartTitle='Coreferenced Pronouns',
                                                                   # count_var = 1 for columns of alphabetic values
                                                                   count_var=0, hover_label=[],
                                                                   outputFileNameType='', #'pronouns_bar',
                                                                   column_xAxis_label='Coreference values',
                                                                   groupByList=[],
                                                                   plotList=[],
                                                                   chart_title_label='')
                if chart_outputFilename != None:
                    if len(chart_outputFilename) > 0:
                        return_files.extend(chart_outputFilename)
    return return_files
