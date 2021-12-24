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
import pandas as pd
import time
import Stanford_CoreNLP_clause_util
import IO_csv_util
import file_splitter_ByLength_util
import IO_files_util
import IO_user_interface_util
import Excel_util
import annotator_dictionary_util
import SVO_enhanced_dependencies_util # Enhanced++ dependencies
import reminders_util

import GUI_IO_util
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
                     openOutputFiles, createExcelCharts,
                     annotator_params,
                     DoCleanXML,
                     memory_var,
                     # print_json = False,
                     document_length=90000,
                     sentence_length=1000, # unless otherwise specified; sentence length limit does not seem to work for parsers only for NER and POS but then it is useless
                     print_json = True,
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

    # check for Java and Java version JDK 8
    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('Stanford CoreNLP')
    if errorFound:
        return filesToOpen

    # check available memory
    IO_libraries_util.check_avaialable_memory('Stanford CoreNLP')

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True)

    # decide on directory or single file
    if inputDir != '':
        inputFilename = inputDir
    # decide on to provide output or to return value

    # global extract_date_from_text_var, extract_date_from_filename_var
    extract_date_from_text_var=False
    extract_date_from_filename_var=False
    date_format = ''
    date_separator_var = ''
    date_position_var = 0
    date_str = ''
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
        'SVO':{"annotators": ['tokenize','ssplit','pos','depparse','natlog','lemma', 'ner']},
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
        'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document'],
        # TODO NER with date for dynamic GIS; modified below
        # 'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document', 'Date'],
        'sentiment': ['Document ID', 'Document','Sentence ID', 'Sentence', 'Sentiment score', 'Sentiment label'],
        'DepRel': ["ID", "Form", "Head", "DepRel", "Record ID", "Sentence ID", "Document ID", "Document"],
        'quote': ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Number of Quotes', 'Speakers'],
        'coref': 'text',
        'coref table': ["Pronoun", "Reference", "Reference Start ID in Sentence",
                        "First Reference Sentence ID", "First Reference Sentence", "Pronoun Start ID in Reference Sentence", "Sentence ID", "Sentence", "Document ID", "Document"],
        'gender':['Word', 'Gender', 'Sentence','Sentence ID', 'Document ID', 'Document'],
        'normalized-date':["Word", "Normalized date", "tid","Information","Sentence ID", "Sentence", "Document ID", "Document"],
        'SVO':['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O', "Negation","Location",'Person','Time','Time normalized NER','Sentence'],
        'OpenIE':['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O', "Location", 'Person', 'Time',
                   'Time normalized NER', 'Sentence'],
        # Chen
        # added Deps column
        'parser (pcfg)':["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"],
        'parser (nn)':["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps","Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document"]
    }
    param_number = 0
    param_number_NN = 0
    files = []#storing names of txt files
    nDocs = 0#number of input documents

    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    # for file in inputDocs:
    #     listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,'Stanford CoreNLP',file)
    #     files.extend(listOfFiles)
    #     nDocs = len(files)
    if nDocs==0:
        return filesToOpen

    # get corresponding func, output format and annotator params from upper 3 dicts
    # routine_list is a list of 4 items:
    #   annotator [0], e.g., NER
    #   output format [2]( headers), typically a single list [], and in the case of POS annotator for WordNet, a douuble list [[].[]]
    # Neural_Network = False
    routine_list = []#storing the annotator, output format (column titles of csv), output
    if not isinstance(annotator_params,list):
        annotator_params = [annotator_params]
    param_string = ''#the input string of nlp annotator properties
    param_string_NN = ''
    # param_list = []
    # param_list_NN = []
    for annotator in annotator_params:
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
            routine_list.append([annotator, routine,output_format,[],parse_model])
        else:
            for param in annotators_:
                if not param in param_string: #the needed annotator property is not containted in the string
                    param_number += 1
                    if param_string == '':
                        param_string = param
                    else:
                        param_string = param_string + ", " + param
            routine_list.insert(0, [annotator, routine,output_format,[],parse_model])

    # the third item in routine_list is typ[ically a single lit [], but for POS it becomes a double list ['Verbs'],[Nouns]]
    # the case needs special handling
    POS_WordNet=False
    if isinstance(routine_list[0][2][0],list):
        run_output = [[], []]
        POS_WordNet=True
    else:
        run_output = []
        POS_WordNet=False

    params = {'annotators':param_string,
                'parse.model': 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz',
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
        CoreNLP_nlp = subprocess.Popen(
            ['java', '-mx' + str(memory_var) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
             'edu.stanford.nlp.pipeline.StanfordCoreNLPServer',  '-parse.maxlen' + str(sentence_length), '-timeout', '999999'])
    else:
        CoreNLP_nlp = subprocess.Popen(
            ['java', '-mx' + str(memory_var) + "g", '-d64', '-cp',  os.path.join(CoreNLPdir, '*'),
             'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-parse.maxlen' + str(sentence_length),'-timeout', '999999'])

    time.sleep(5)

    if 'POS' in str(annotator_params) or 'NER' in str(annotator_params):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_CoreNLP_POS_NER_maxlen,
            reminders_util.message_CoreNLP_POS_NER_maxlen,
            True)

    if 'quote' in str(annotator_params):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_CoreNLP_quote_annotator,
            reminders_util.message_CoreNLP_quote_annotator,
            True)

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
        split_file = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,config_filename,docName,'',document_length)
        split_docID = 0
        nSplitDocs = len(split_file)
        for doc in split_file:
            split_docID = split_docID + 1
            annotated_length = 0#the number of tokens
            # doc_start_time = time.time()
            model_switch = False
            head, tail = os.path.split(doc)
            if docName != doc:
                print("   Processing split file " + str(split_docID) + "/" + str(nSplitDocs) + ' ' + tail)
            text = open(doc, 'r', encoding='utf-8', errors='ignore').read().replace("\n", " ")
            if "%" in text:
                reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_percent,
                                             reminders_util.message_CoreNLP_percent, True)
                text=text.replace("%","percent")
            nlp = StanfordCoreNLP('http://localhost:9000')
            # nlp = StanfordCoreNLP('http://point.dd.works:9000')

            #if there's only one annotator and it uses neural nerwork model, skip annoatiting with PCFG to save time
            if param_string != '':
                # text = open(doc, 'r', encoding='utf-8', errors='ignore').read().replace("\n", " ")
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
                #print out the json output of CoreNLP to a txt file
                if print_json:
                    jsonFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt',
                                                                           'CoreNLP_' + str(
                                                                               annotator_params) + '_json_output_NN')
                    with open(jsonFilename, "a+", encoding='utf-8', errors='ignore') as json_out:
                        json.dump(CoreNLP_output, json_out, indent=4)
                    # no need to open the Json file
                    # if jsonFilename not in filesToOpen:
                    #     filesToOpen.append(jsonFilename)
            else: CoreNLP_output = ""

            # routine_list contains all annotators
            for run in routine_list:
                annotator_start_time = time.time()
                # params = run[0]
                annotator_chosen = run[0]
                routine = run[1]
                output_format = run[2]
                parse_model = run[4]
                if parse_model == "NN" and model_switch == False:
                    model_switch = True
                    params_NN = params
                    params_NN['parse.model'] = 'edu/stanford/nlp/models/parser/nndep/english_UD.gz'
                    params_NN['annotators'] = param_string_NN
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
                    #print out the json output of CoreNLP (model: neural network) to a txt file
                    if print_json:
                        jsonFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt',
                                                                               'CoreNLP_' + str(
                                                                                   annotator_params) + '_json_output_NN')
                        with open(jsonFilename, "a+", encoding='utf-8', errors='ignore') as json_out_nn:
                            json.dump(CoreNLP_output, json_out_nn, indent=4)
                        # no need to open the Json file
                        # if jsonFilename not in filesToOpen:
                        #     filesToOpen.append(jsonFilename)

                #generating output from json file for specific annotators
                if "parser" in annotator_chosen:
                    if "pcfg" in annotator_chosen:
                        sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID, True,CoreNLP_output, **kwargs)
                    else:
                        sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID, False,CoreNLP_output, **kwargs)
                elif "All POS" in annotator_chosen or "Lemma" in annotator_chosen:
                    sub_result, recordID = routine(config_filename, docID, docName, sentenceID, recordID,
                                               CoreNLP_output, **kwargs)
                # elif "DepRel" in annotator_chosen or "All POS" in annotator_chosen or "Lemma" in annotator_chosen:
                #      sub_result, recordID = routine(config_filename,docID, docName, sentenceID, recordID, CoreNLP_output, **kwargs)
                else:
                    sub_result = routine(config_filename,docID, docName, sentenceID, CoreNLP_output, **kwargs)
                
                # sentenceID = new_sentenceID
                
                if output_format == 'text':
                    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt',
                                                                             'CoreNLP_'+ str(annotator_chosen))
                    with open(outputFilename, "a+", encoding='utf-8', errors='ignore') as text_file:
                        if processing_doc != docTitle:
                            text_file.write("\n<@#" + docTitle + "#@>\n")
                            processing_doc = docTitle
                        text_file.write(sub_result)
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
    #generate output csv files and write output
    output_start_time = time.time()
    # print("Length of Files to Open after generating output: ", len(filesToOpen))
    outputFilename_tag = ''
    for run in routine_list:
        annotator_chosen = run[0]
        routine = run[1]
        output_format = run[2]
        if POS_WordNet == False:
            run_output = run[3]
        # skip coreferenced file
        if output_format == "text":
            continue
        if isinstance(output_format[0],list): # multiple outputs
            for index, sub_output in enumerate(output_format):
                if POS_WordNet:
                    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                             'CoreNLP_'+annotator_chosen+'_lemma_'+output_format[index][0])
                else:
                    outputFilename = IO_files_util.generate_output_file_name(str(doc), inputDir, outputDir,'.csv',
                                                                              'CoreNLP_'+annotator_chosen+'_lemma'+output_format[index][0])
                filesToOpen.append(outputFilename)
                df = pd.DataFrame(run_output[index], columns=output_format[index])
                df.to_csv(outputFilename, index=False)
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
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                                 'CoreNLP_NER_'+outputFilename_tag)
            elif "parser" in annotator_chosen:#CoNLL
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'CoreNLP', 'CoNLL')

            elif output_format != 'text':
                # TODO any changes in the way the CoreNLP_annotator generates output filenames for sentiment analysis
                #    will affect the shape of stories algorithms (search TODO there)
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                             'CoreNLP_'+annotator_chosen)
            filesToOpen.append(outputFilename)
            if output_format != 'text' and not isinstance(output_format[0],list): # output is csv file
                # when NER values (notably, locations) are extracted with the date option
                #   for dynamic GIS maps (as called from GIS_main with date options)
                if extract_date_from_text_var or extract_date_from_filename_var:
                    # output_format=['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document','Date']
                    output_format.append("Date")
                # if NER_sentence_var == 1:
                #     df = Excel_util.add_missing_IDs(df)
                df = pd.DataFrame(run_output, columns=output_format)
                df.to_csv(outputFilename, index=False)
    # print("Length of Files to Open after generating files: ", len(filesToOpen))
    # set filesToVisualize because filesToOpen will include xlsx files otherwise
    filesToVisualize=filesToOpen
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True, '', True, startTime)

    # generate visualization output ----------------------------------------------------------------

    for j in range(len(filesToVisualize)):
        #02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j])
            file_df_name = os.path.split(filesToVisualize[j])[1]
            if not file_df.empty:
                if 'Lemma' in str(file_df_name):
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[2, 2]], 'bar',
                                          'Frequency Distribution of Lemmas', 1, [], 'lemma_bar','Lemma')
                elif 'All POS' in str(file_df_name):
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[2, 2]], 'bar',
                                          'Frequency Distribution of POS Tag Values', 1, [], 'POS_bar','POS tag')
                elif 'gender' in str(file_df_name):
                    filesToOpen = visualize_html_file(inputFilename, inputDir, outputDir, filesToVisualize[j], filesToOpen)
    
                    filesToOpen = visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen,
                                                        [[1, 1]], 'bar',
                                                        'Frequency Distribution of Gender Types', 1, [],
                                                        'gender_types','Gender')

                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen,
                                                      [[0, 0]], 'bar',
                                          'Frequency Distribution of Words by Gender Type', 1, ['Gender'], 'gender_words','')

                elif 'quote' in str(file_df_name):
                    filesToOpen = visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen,
                                                        [[5, 5]], 'bar',
                                                        'Frequency Distribution of Speakers', 1, [],
                                                        'quote_bar', 'Speaker')
                elif 'date' in str(file_df_name):
                    # TODO put values hover-over values to pass to Excel chart as a list []
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[1, 1]], 'bar',
                                          'Frequency Distribution of Normalized Dates', 1, [], 'NER_date_bar','Normalized date type')
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[3, 3]], 'bar',
                                                      'Frequency Distribution of Information of Normalized Dates', 1, [], 'NER_info_bar','Date type')
                elif 'NER' in str(file_df_name):
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[1, 1]], 'bar',
                                          'Frequency Distribution of NER Tags', 1, [], 'NER_tag_bar','NER tag')
                    # ner tags are _ separated; individual NER tags at most have 2 _ (e.g., STATE_OR_PROVINCE)
                    if len(kwargs['NERs'])>1:
                        ner_tags = 'Multi-tags'
                    else:
                        ner_tags = str(kwargs['NERs'][0])
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[0, 0]], 'bar',
                                          'Frequency Distribution of Words by NER ' +ner_tags, 1, ['NER Value'], 'NER_word_bar','') #NER ' +ner_tags+ ' Word
                elif 'SVO' in str(file_df_name) or 'OpenIE' in str(file_df_name):
                    # pie chart of SVO
                    # filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[3, 3],[4,4],[5,5]], 'pie',
                    #                       'Frequency Distribution of SVOs', 1, [], 'SVO_pie','SVOs')
                    filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[3, 3]], 'bar',
                                          'Frequency Distribution of Subjects (unfiltered)', 1, [], 'S_bar','Subjects (unfiltered)')
                    filesToOpen = visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[4, 4]], 'bar',
                                                        'Frequency Distribution of Verbs (unfiltered)', 1, [], 'V_bar', 'Verbs (unfiltered)')
                    filesToOpen = visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[5, 5]], 'bar',
                                                        'Frequency Distribution of Objects (unfiltered)', 1, [], 'O_bar', 'Objects (unfiltered)')
    CoreNLP_nlp.kill()
    # print("Length of Files to Open after visualization: ", len(filesToOpen))
    if len(filesError)>0:
        mb.showwarning("Stanford CoreNLP Error", 'Stanford CoreNLP ' +annotator_chosen+ ' annotator has found '+str(len(filesError)-1)+' files that could not be processed by Stanford CoreNLP.\n\nPlease, read the error output file carefully to see the errors generated by CoreNLP.')
        errorFile = os.path.join(outputDir,
                                           IO_files_util.generate_output_file_name(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename), inputDir, outputDir, '.csv',
                                                                                   'CoreNLP', 'file_ERRORS'))
        IO_csv_util.list_to_csv(GUI_util.window, filesError, errorFile)
        filesToOpen.append(errorFile)
    # record the time consumption of generating outputfiles and visualization
    # record the time consumption of running the whole analysis
    total_time_elapsed = time.time() - start_time
    # speed_assessment.append(["Total Operation", -1, total_time_elapsed,'', '', 0])
    speed_assessment.append([-1, "Total Operation", total_time_elapsed,total_length, ", ".join(annotator_params), len(annotator_params)])
    speed_csv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                           'CoreNLP_speed_assessment')
    df = pd.DataFrame(speed_assessment, columns=speed_assessment_format)
    df.to_csv(speed_csv, index=False)
    # filesToOpen.append(speed_csv) NO NEED TO OPEN THE SPED ASSESSMENT FILE; NOT A FILE FOR USERS
    if len(inputDir) != 0:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Output warning', 'The output filename generated by Stanford CoreNLP is the name of the directory processed in input, rather than any individual file in the directory. The output file(s) include all ' + str(nDocs) + ' files in the input directory processed by CoreNLP.\n\nThe different files are listed in the output csv file under the headers \'Document ID\' and \'Document\'.')

    return filesToOpen


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

# ["Word", "Normalized date", "tid","tense","information","Sentence ID", "Sentence", "Document ID", "Document"],
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
            temp = [ner['text'], ner['ner'], sentenceID, complete_sent,  ner['tokenBegin'],
                    ner['tokenEnd'],documentID,
                    IO_csv_util.dressFilenameForCSVHyperlink(document)]
            # check in NER value column
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
                            print("normalizedNER not found.")
                            norm_date = ""
                        temp.append(norm_date)
                        NER.append(temp)
                    else:
                        NER.append(temp)
    result = []
    index = 0
    while index < len(NER):
        temp = NER[index]
        if NER[index][1] == 'CITY':
            if index < len(NER)-1: # NER[index + 1] would break the code
                # check if a city is followed by EITHER state/province OR country e.g., Atlanta, Georgia or Atlanta, United States
                if NER[index + 1][1] == 'STATE_OR_PROVINCE' or NER[index + 1][1] == 'COUNTRY':
                    temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
                    index = index + 1
                    # check if a city and state/province are also followed by country e.g., Atlanta, Georgia, United States
                    if index < len(NER) - 1:
                        if NER[index + 1][1] == 'COUNTRY':
                            temp[0] = temp[0] + ', ' + NER[index + 1][0]
                            index = index + 1
        elif NER[index][1] == 'STATE_OR_PROVINCE':
            if index < len(NER)-1: # NER[index + 1] would break the code
                # check if a state/province  is followed by a country e.g., Georgia, United States
                if NER[index + 1][1] == 'COUNTRY':
                    temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
                    index = index + 1
        result.append(temp)
        index = index + 1
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
            temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), sentence['index'] + 1, text, sentence["sentimentValue"], sentence["sentiment"].lower(), date_str]
        else:
            temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), sentence['index'] + 1, text, sentence["sentimentValue"], sentence["sentiment"].lower()]
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

    def get_resolved(corenlp_output, sentenceID):
        """ get the "resolved" output as String """
        result = ''
        possessives = ['hers', 'his', 'their', 'theirs']
        for sentence in corenlp_output['sentences']:
            sentenceID += 1
            for token in sentence['tokens']:
                output_word = token['word']
                # check lemmas as well as tags for possessive pronouns in case of tagging errors
                if token['lemma'] in possessives or token['pos'] == 'PRP$':
                    output_word += "'s"  # add the possessive morpheme
                output_word += token['after']
                result = result + output_word

            check_sentence_length(len(sentence['tokens']), sentenceID, config_filename)

        return result

    resolve(json)
    output_text = get_resolved(json, sentenceID)
    return output_text


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
                    result.append([elmt['text'], elmt['gender'], complete, elmt['sentNum'] + start_sentenceID, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), date_str])
                else:
                    result.append([elmt['text'], elmt['gender'], complete, elmt['sentNum'] + start_sentenceID, documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])

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
            temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), sentenceID,
                    complete_sent, number_of_quotes, str(speakers[quoted_sent_id][0]),date_str]
        else:
            temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), sentenceID,
                    complete_sent, number_of_quotes, str(speakers[quoted_sent_id][0])]
        result.append(temp)
    return result

def process_json_sentence(config_filename, documentID, document, sentenceID, json, **kwargs):
    temp = []
    # ['Document ID', 'Document', 'Sentence ID', 'Sentence'],
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
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    date_str = date_in_filename(document, **kwargs)
    SVO_enhanced_dependencies = []
    locations = [] # a list of [sentence, sentence id, [location_text, ner_value]]
    for sentence in json['sentences']:#traverse output of each sentence 
        sent_data = SVO_enhanced_dependencies_util.SVO_enhanced_dependencies_sent_data_reorg(sentence)#reorganize the output into a dictionary in which each content (also dictionary) contains information of a token
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
        SVO, L, NER_value, T, T_S, P, N = SVO_enhanced_dependencies_util.SVO_extraction(sent_data, sentence['entitymentions'])# main function
        nidx = 0

        #CYNTHIA: " ".join(L) => "; ".join(L)
        # ; added list of locations in SVO output (e.g., Los Angeles; New York; Washington)
        for row in SVO:
            if extract_date_from_filename_var:
                SVO_enhanced_dependencies.append([documentID, sentenceID, IO_csv_util.dressFilenameForCSVHyperlink(document), row[0], row[1], row[2], N[nidx], "; ".join(L), " ".join(P), " ".join(T), " ".join(T_S),complete_sent, date_str])
            else:
                SVO_enhanced_dependencies.append([documentID, sentenceID, IO_csv_util.dressFilenameForCSVHyperlink(document), row[0], row[1], row[2], N[nidx], "; ".join(L), " ".join(P), " ".join(T), " ".join(T_S),complete_sent])
            nidx += 1

        if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True and len(L) != 0:
            # produce an intermediate location file
            locations.append([sentenceID, complete_sent, [[x,y] for x,y in zip(L,NER_value)]])

    if "google_earth_var" in kwargs and kwargs["google_earth_var"] == True:
        # columns: Location, NER Value, Sentence ID, Sentence, Document ID, Document
        to_write = []
        for sent in locations:
            for locs in sent[2]:
                to_write.append([locs[0], locs[1], sent[0], sent[1], documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])
        df = pd.DataFrame(to_write, columns=["Location", "NER Value", "Sentence ID", "Sentence", "Document ID", "Document"])
        if documentID == 1:
            df.to_csv(kwargs["location_filename"], header='column_names', index=False)
        else:
            df.to_csv(kwargs["location_filename"], mode='a', header=False, index=False)

    return SVO_enhanced_dependencies

def process_json_openIE(config_filename,documentID, document, sentenceID, json, **kwargs):
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True
    date_str = date_in_filename(document, **kwargs)
    
    openIE = []
    for sentence in json['sentences']:
        entitymentions = sentence['entitymentions']
        complete_sent = ''
        L = []  # list that stores the location information appear in sentences
        T = []  # list that stores the time information appear in sentences
        T_S = []  # list that stores normalized form of the time information appear in sentences
        P = []  # list that stores person names appear in sentences
        # CYNTHIA: get locations from entitymentions
        for item in entitymentions:
            if item["ner"] is not None and item["ner"] in ['STATE_OR_PROVINCE', 'COUNTRY', "CITY", "LOCATION"]:
                L.append(item["text"])
        for token in sentence['tokens']:
            if token["ner"] == "TIME" or token["ner"] == "DATE":
                T.append(token["word"])

                T_S.append(token['normalizedNER'])

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
                    openIE.append([documentID, sentenceID, IO_csv_util.dressFilenameForCSVHyperlink(document), row[0], row[1], row[2],"; ".join(L), " ".join(P), " ".join(T), " ".join(T_S),complete_sent, date_str])
                else:
                    openIE.append([documentID, sentenceID, IO_csv_util.dressFilenameForCSVHyperlink(document), row[0], row[1], row[2],"; ".join(L), " ".join(P), " ".join(T), " ".join(T_S),complete_sent])
    # print(openIE)

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
    if pcfg:
        sent_list_clause = [Stanford_CoreNLP_clause_util.clausal_info_extract_from_string(parsed_sent['parse'])
                            for parsed_sent in json['sentences']]
    for i in range(len(json["sentences"])):
        # print("*************")
        # print("The ", i, "th Sentence in ", document)
        # print("OutputSentenceID: ", )
        sentenceID += 1
        # print("OutputSentenceID: ", sentenceID)
        #result = []
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
            else:
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
            # print("Row in the CSV: ")
            # print(temp)
            # if dateInclude == 1 and dateStr!='DATE ERROR!!!':
            #     temp.append(d
            #         check_sentence_length(len(tokens), sentenceID, config_filename)
            #
            #         # print("The result after adding the ", sentenceID, "th sentence: ")
            #         # pprint.pprint(result)
            #
            #     return result, recordIDateStr)

    return result, recordID



def similar_string_floor_filter(str1, str2):
    dist = nltk.edit_distance(str1, str2)
    if dist <= 5:
        return True
    else:
        return False


def visualize_html_file(inputFilename, inputDir, outputDir, dictFilename, filesToOpen):
    # annotate the input file(s) for gender values
    csvValue_color_list = ['Gender', '|', 'FEMALE', 'red', '|', 'MALE', 'blue', '|']
    bold_var = True
    tagAnnotations = ['<span style="color: blue; font-weight: bold">', '</span>']

    tempFilename = annotator_dictionary_util.dictionary_annotate(inputFilename, inputDir, outputDir,
                                                             dictFilename,'',
                                                             csvValue_color_list, bold_var, tagAnnotations,
                                                             fileType='.txt')
    # the annotator returns a list rather than a string
    if len(tempFilename) > 0:
        filesToOpen.append(tempFilename[0])

    return filesToOpen

def visualize_Excel_chart(createExcelCharts,inputFilename,outputDir,filesToOpen, columns_to_be_plotted, chartType, chartTitle, count_var, hover_label, outputFileNameType, column_xAxis_label):
    if createExcelCharts == True:
        Excel_outputFilename = Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel=outputFileNameType,
                                                  chart_type_list=[chartType],
                                                  chart_title=chartTitle,
                                                  column_xAxis_label_var=column_xAxis_label,
                                                  hover_info_column_list=hover_label,
                                                  count_var=count_var)
        if Excel_outputFilename!=None:
            if len(Excel_outputFilename) > 0:
                filesToOpen.append(Excel_outputFilename)

        # by sentence index
        #
        #     # line plots by sentence index
        #     outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
        #                                                                    inputFilename,
        #                                                                    '',
        #                                                                    outputDir,
        #                                                                    openOutputFiles,
        #                                                                    createExcelCharts,
        #                                                                    [[1, 2]],
        #                                                                    ['Normalized date'],['Word', 'Sentence'],['Document ID', 'Sentence ID','Document'],
        #                                                                    'date', 'line')
        #
        #     if len(outputFiles) > 0:
        #         filesToOpen.extend(outputFiles)

    return filesToOpen


# def visualize_date_distribution(inputFileName):

