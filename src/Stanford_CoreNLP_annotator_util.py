#If there's an error that interrupted the operation within this script, PLEASE
#1. (In Terminal) Type in sudo lsof -i tcp:9000 see the PID of the subprocess occupying the port
#2. Type in kill -9 ***** to kill that subprocess
#P.S ***** is the 5 digit PID

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoreNLP_annotator", ['os', 'tkinter','time','json','re','subprocess','string','pandas','pycorenlp','nltk'])==False:
    sys.exit(0)

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

import IO_csv_util
import file_splitter_ByLength_util
import IO_files_util
import IO_user_interface_util
import Excel_util
import annotator_dictionary_util

# central CoreNLP_annotator function that pulls together our approach to processing many files,
# splitting them if necessary, and, depending upon annotator (NER date, quote, gender, sentiment)
# perhaps call different subfunctions, and pulling together the output


# CHOOSE YOUR OPTION FOR variable: annotator_params in option below
# tokenize: tokenize
# ssplit:  tokenize,ssplit
# MWT: tokenize,ssplit,mwt
# POS: tokenize,ssplit,pos
# lemma: tokenize,ssplit,pos,lemma
# NER: tokenize,ssplit,pos,lemma,ner
# coref: tokenize,ssplit,pos,lemma,ner,parse,coref
# sentiment:
# input cleanXML = 1 to add cleanXML to your annotator

# ner GIS, date

def CoreNLP_annotate(inputFilename,
                     inputDir, outputDir,
                     openOutputFiles, createExcelCharts,
                     annotator_params,
                     DoCleanXML,
                     memory_var, **kwargs):

    filesToOpen = []
    # check that the CoreNLPdir as been setup
    CoreNLPdir=IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_annotator', 'Stanford CoreNLP')
    if CoreNLPdir== '':
        return filesToOpen

    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('SVO extractor')
    if errorFound:
        return filesToOpen

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True, "You can follow CoreNLP annotator in command line.")

    # decide on directory or single file
    if inputDir != '':
        inputFilename = inputDir
    # decide on to provide output or to return value

    produce_split_files=False
    # @ change coref-text to coref, change coref-spreadsheet to gender@
    params_option = {
        'tokenize': {'annotators':'tokenize'},
        'ssplit': {'annotators':'tokenize, ssplit'},
        'MWT': {'annotators':'tokenize,ssplit,mwt'},
        'POS': {'annotators':'tokenize,ssplit,pos,lemma'},
        'NER': {'annotators':'tokenize,ssplit,pos,lemma,ner'},
        'quote': {'annotators': 'tokenize,ssplit,pos,lemma,ner,depparse,coref,quote'},
        'coref': {'annotators':'dcoref'},
        'gender': {'annotators': 'dcoref'},
        'sentiment': {'annotators':'sentiment'},
        'normalized-date': {'annotators': 'tokenize,ssplit,ner'},
        'openIE':{"annotators": "tokenize,ssplit,pos,depparse,natlog,openie"}
    }
    # @ change coref-text to coref, change coref-spreadsheet to gender@
    
    routine_option = {
        'sentiment': process_json_sentiment,
        'POS':process_json_postag,
        'NER': process_json_ner,
        'quote': process_json_quote,
        'coref': process_json_coref,
        'gender': process_json_gender,
        'normalized-date':process_json_normalized_date,
        # Dec. 21
        'openIE':process_json_openIE
    }
    #@ change coref-text to coref, change coref-spreadsheet to gender@
    output_format_option = {
        'POS':[['Verbs'],['Nouns']],
        'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document'],
        # TODO NER with date for dynamic GIS; modified below
        # 'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document', 'Date'],
        'sentiment': ['Document ID', 'Document','Sentence ID', 'Sentence', 'Sentiment number', 'Sentiment label'],
        'quote': ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Number of Quotes'],
        'coref': 'text',
        'gender':['Word', 'Gender', 'Sentence','Sentence ID', 'Document ID', 'Document'],
        'normalized-date':["Word", "Normalized date", "tid","Tense","Information","Sentence ID", "Sentence", "Document ID", "Document"],
        #  Document ID, Sentence ID, Document, S, V, O/A, Sentence
        # Dec. 21
        'openIE':['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'Sentence']
    }

    files = []#storing names of txt files
    Ndocs = 0#number of input documents
    
    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    for file in inputDocs:
        listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,'Stanford CoreNLP',file)
        files.extend(listOfFiles)
        Ndocs = len(files)
    if Ndocs==0:
        return filesToOpen

    # get corresponding func, output format and annotator params from upper 3 dicts
    routine_list = []#storing the annotator, output format (column titles of csv), output
    if not isinstance(annotator_params,list):
        annotator_params = [annotator_params]
    param_string = ''#the input string of nlp annotator properties
    for annotator in annotator_params:
        routine = routine_option.get(annotator)
        output_format = output_format_option.get(annotator)
        #building annotator input string
        params = params_option.get(annotator)["annotators"]
        annotators_ = params.split(',')  # nltk.word_tokenize(params)
        annotators_[:] = (value for value in annotators_ if value != ',')#tokenize each property
        for param in annotators_:
            if not param in param_string: #the needed annotator property is not containted in the string
                if param_string == '':
                    param_string = param
                else:
                    param_string = param_string + ", " + param
        routine_list.append([annotator, routine,output_format,[]])
        
    params = {'annotators':param_string}
    if DoCleanXML:
        params['annotators'] = params['annotators'] + ',cleanXML'

    p = subprocess.Popen(
        ['java', '-mx' + str(memory_var) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    time.sleep(5)
    nlp = StanfordCoreNLP('http://localhost:9000')

    #annotating each input file
    docID=0
    for doc in files:
        docID = docID + 1
        head, tail = os.path.split(doc)
        print("\nProcessing file " + str(docID) + "/" + str(Ndocs) + ' ' + tail)
        text = open(doc, 'r', encoding='utf-8', errors='ignore').read().replace("\n", " ")
        tempVar = nlp.annotate(text, properties=params)

        try:
            parsedjson = json.loads(tempVar)
        except:
            mb.showwarning('Stanford CoreNLP annotator Error',
                               'The Stanford CoreNLP CoreNLP Annotator failed to process the input document\n  ' + tail + '\nexiting with the following error:\n\n' + tempVar + '\n\nTHE ERROR MAY HAPPEN WHEN CoreNLP HANGS. REBOOT YOUR MACHINE AND TRY AGAIN.\n\nTHE ERROR IS ALSO LIKELY TO HAPPEN WHEN THE STANFORD CORENLP HAS BEEN STORED TO A CLOUD SERVICE (e.g., OneDrive) OR INSIDE THE /NLP/src DIRECTORY. TRY TO MOVE THE STANFORD CORENLP FOLDER TO A DIFFERENT LOCATION.')
            continue # process next document
        # routine_list contains all annotators
        for run in routine_list:
            # params = run[0]
            annotator_chosen = run[0]
            routine = run[1]
            output_format = run[2]
            run_output = run[3]

            #generating output from json file for specific annotators
            sub_result = routine(docID, doc, parsedjson, **kwargs)
            #write html file from txt input
            if output_format == 'text':
                outputFilename = IO_files_util.generate_output_file_name(doc, '', outputDir, '.txt', 'CoreNLP_'+annotator_chosen)
                with open(outputFilename, "w") as text_file:
                    text_file.write(sub_result)
                filesToOpen.append(outputFilename)
            else:
                    #add output to the ouptut storage list in routine_list
                    run_output.extend(sub_result)
    
    #generate output csv files and write output 
    for run in routine_list:
        annotator_chosen = run[0]
        routine = run[1]
        output_format = run[2]
        run_output = run[3]
        if isinstance(output_format[0],list): # multiple outputs
            for index, sub_output in enumerate(output_format):
                outputFilename = IO_files_util.generate_output_file_name(str(doc), '', outputDir,
                                                                          '.csv',
                                                                          'CoreNLP_'.join(annotator_chosen),
                                                                          output_format[index][0],'lemma')
                filesToOpen.append(outputFilename)
                df = pd.DataFrame(run_output[index], columns=output_format[index])
                df.to_csv(outputFilename, index=False)

        else:
            # generate output file name
            if annotator_chosen == 'NER':
                print("Annotator: NER")
                ner = '_'.join(kwargs['NERs'])
                outputFilename_tag=str(ner)
                if ner=='CITY_STATE_OR_PROVINCE_COUNTRY':
                    outputFilename_tag=ner.replace('CITY_STATE_OR_PROVINCE_COUNTRY','LOCATIONS')
                elif ner=='COUNTRY_STATE_OR_PROVINCE_CITY':
                    # when called from GIS_main
                    outputFilename_tag=ner.replace('COUNTRY_STATE_OR_PROVINCE_CITY','LOCATIONS')
                elif len(ner)>10: # if all NER tags have been selected the filename would become way too long!
                    outputFilename_tag='tags'

                outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                 'CoreNLP_NER_'+outputFilename_tag)
            else:
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                             'CoreNLP_'+annotator_chosen)
            filesToOpen.append(outputFilename)
            if output_format != 'text': # output is csv file
                if extract_date_from_text_var or extract_date_from_filename_var:
                    output_format=['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID','Document','Date']
                # if NER_sentence_var == 1:
                #     df = Excel_util.add_missing_IDs(df)
                df = pd.DataFrame(run_output, columns=output_format)
                df.to_csv(outputFilename, index=False)

    # set filesToVisualize because filesToOpen will include xlsx files otherwise
    filesToVisualize=filesToOpen
    #generate visualization output
    for j in range(len(filesToVisualize)):
        if 'gender' in str(filesToVisualize[j]):
            filesToOpen = visualize_html_file(inputFilename, inputDir, outputDir, filesToVisualize[j], filesToOpen)

            filesToOpen = visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen,
                                                [[1, 1]], 'bar',
                                                'Frequency Distribution of Gender Types', 1, [],
                                                'gender_bar','Gender')
        elif 'date' in str(filesToVisualize[j]):
            # TODO put values hover-over values to pass to Excel chart as a list []
            filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[1, 1]], 'bar',
                                  'Frequency Distribution of Normalized Dates', 1, [], 'NER_date_bar','Date type')
            filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[3, 3]], 'bar',
                                  'Frequency Distribution of Tenses of Normalized Dates', 1, [], 'NER_tense_bar','Date type')
            filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[4, 4]], 'bar',
                                              'Frequency Distribution of Information of Normalized Dates', 1, [], 'NER_info_bar','Date type')
        elif 'NER'  in str(filesToVisualize[j]):
            filesToOpen=visualize_Excel_chart(createExcelCharts, filesToVisualize[j], outputDir, filesToOpen, [[1, 1]], 'bar',
                                  'Frequency Distribution of NER Tags', 1, [], 'NER_tag_bar','NER tag')

    p.kill()

    if len(inputDir) != 0:
        mb.showwarning(title='Warning', message='The output filename generated by Stanford CoreNLP is the name of the directory processed in input, rather than any individual file in the directory. The output file(s) include all ' + str(Ndocs) + ' files in the input directory processed by CoreNLP.\n\nThe different files are listed in the output csv file under the headers \'Document ID\' and \'Document\'.')

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Stanford CoreNLP ' + str(annotator_params) + ' annotator at', True)
    return filesToOpen

# ["Word", "Normalized date", "tid","tense","information","Sentence ID", "Sentence", "Document ID", "Document"],
def process_json_normalized_date(documentID, document, json, **kwargs):
    print("   Processing Json output file for NER NORMALIZED DATE annotator")

    result = []
    temp = []
    for sentence in json['sentences']:
        complete_sent = ''
        sentenceID = sentence['index'] + 1
        words = ''
        norm_date = ''
        tid = ''
        tense = ''
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
                    tense = date_get_tense(norm_date)
                    info = date_get_info(norm_date)
                    words = word + words
                elif token['normalizedNER'] != norm_date:
                    # writer.writerow([words,norm_date, sentence_id, sent_str, documentID,file])
                    temp = [words, norm_date, tid, tense, info, sentenceID, complete_sent, documentID,
                                     IO_csv_util.dressFilenameForCSVHyperlink(document)]
                    result.append(temp)
                    words = word
                    norm_date = token['normalizedNER']
                    try:
                        tid = token['timex']['tid']
                    except:
                        print('   tid error')
                        tid=''
                    tense = date_get_tense(norm_date)
                    info = date_get_info(norm_date)
                    words = word + words
                else:
                    if word in string.punctuation:
                        words = words + word
                    else:
                        words = words + " " + word
            else:
                if words != '' or norm_date != '':
                    # writer.writerow([words,norm_date, sentence_id, sent_str, documentID, file])
                    temp = [words, norm_date, tid, tense, info, sentenceID, complete_sent, documentID,
                                     IO_csv_util.dressFilenameForCSVHyperlink(document)]
                    result.append(temp)
                    words = ''
                    norm_date = ''
                    tid = ''
                    tense = ''
                    info = ''

    return result

# def date_get_tense(norm_date):

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

def date_get_info(norm_date):
    tense = ''
        # print(norm_date)
    if norm_date.isdigit() or norm_date.replace('/', '').isdigit() or ("XXXX" in norm_date and norm_date.split("XXXX")[1].replace("-", '').isdigit()):#(len(norm_date) > 4 and norm_date[0:4] == 'XXXX' and norm_date[4:].replace("-", '').isdigit()):#specific year,month, day
        tense = "DATE"
        # print("date")
    elif 'WXX' in norm_date:#weekdays
        tense = "DAY"
        # print("day")
    elif 'SP' in norm_date or 'SU' in norm_date or 'FA' in norm_date or 'WI' in norm_date:
        tense = "SEASON"
        # print("season")
    else:
        tense = "OTHER"
    return tense

# TODO fix the documentID value in csv output
def process_json_ner(documentID, document, json, **kwargs):
    print("   Processing Json output file for NER annotator")
    # establish the kwarg local vars
    global extract_date_from_text_var, extract_date_from_filename_var
    extract_date_from_text_var = False
    extract_date_from_filename_var = False
    request_NER = []
    date_format = ''
    date_separator_var = ''
    date_position_var = 0
    date_str = ''
    # process the optional values in kwargs
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            # TODO when saving the data, we need to use an NER output_format with an extra 'Date' column for dynamic GIS
            extract_date_from_text_var = True
        if key == 'NERs':
            request_NER = value
        if key == 'extract_date_from_filename_var' and value == True:
            # TODO when saving the data, we need to use an NER output_format with an extra 'Date' column for dynamic GIS
            extract_date_from_filename_var = True
        if key == 'date_format':
            date_format = value
        if key == 'date_separator_var':
            date_separator_var = value
        if key == 'date_position_var':
            date_position_var = value
    NER = []
    # get date string of this sub file
    if extract_date_from_filename_var:
        date, date_str = IO_files_util.getDateFromFileName(document, date_separator_var, date_position_var,
                                                           date_format)

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
        sentenceID = sentence['index'] + 1
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
        if index == len(NER) - 1:
            break
        if NER[index][1] == 'CITY':
            if NER[index + 1][1] == 'STATE_OR_PROVINCE' and NER[index][1] == NER[index + 1][1] and abs(
                    NER[index + 1][4] - NER[index][5]) <= 2:
                temp = NER[index]
                temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
                result.append(temp)
                index = index + 2
            elif NER[index + 1][1] == 'COUNTRY' and NER[index][1] == NER[index + 1][1] and abs(
                    NER[index + 1][4] - NER[index][5]) <= 2:
                temp = NER[index]
                temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
                result.append(temp)
                index = index + 2
            else:
                result.append(NER[index])
                index = index + 1
        elif NER[index][1] == 'STATE_OR_PROVINCE':
            if NER[index + 1][1] == 'COUNTRY' and NER[index][1] == NER[index + 1][1] and abs(
                    NER[index + 1][4] - NER[index][5]) <= 2:
                temp = NER[index]
                temp[0] = NER[index][0] + ', ' + NER[index + 1][0]
                result.append(temp)
                index = index + 2
            else:
                result.append(NER[index])
                index = index + 1
        else:
            result.append(NER[index])
            index = index + 1
    return result


def process_json_sentiment(documentID, document, json, **kwargs):
    print("   Processing Json output file for SENTIMENT annotator")
    sentiment = []
    for s in json["sentences"]:
        text = " ".join([t["word"] for t in s["tokens"]])
        temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document),s['index'] + 1, text, s["sentimentValue"], s["sentiment"].lower()]
        print(temp)
        sentiment.append(temp)
    return sentiment


def process_json_coref(documentID, document, json, **kwargs):
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

    def get_resolved(corenlp_output):
        """ get the "resolved" output as String """
        result = ''
        possessives = ['hers', 'his', 'their', 'theirs']
        for sentence in corenlp_output['sentences']:
            for token in sentence['tokens']:
                output_word = token['word']
                # check lemmas as well as tags for possessive pronouns in case of tagging errors
                if token['lemma'] in possessives or token['pos'] == 'PRP$':
                    output_word += "'s"  # add the possessive morpheme
                output_word += token['after']
                result = result + output_word
        return result
    resolve(json)
    output_text = get_resolved(json)
    return output_text


# December.10 Yi: Modify process_json_gender to provide one more column(complete sentence)
def process_json_gender(documentID, document, json, **kwargs):
    print("   Processing Json output file for GENDER annotator")
    result = []
    mentions = []
    sent_dict = {}
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
        sentenceID = sentence['index'] + 1
        sent_dict[sentenceID] = complete_sent
    for num, res in json['corefs'].items():
        mentions.append(res)
    for mention in mentions:
        for elmt in mention:
            if elmt['gender'] in ['NEUTRAL', 'UNKNOWN']:
                continue
            else:
                # get complete sentence
                complete = sent_dict[elmt['sentNum']]
                result.append([elmt['text'], elmt['gender'], complete, elmt['sentNum'], documentID, IO_csv_util.dressFilenameForCSVHyperlink(document)])

    return result


def process_json_quote(documentID, document, json, **kwargs):
    print("   Processing Json output file for QUOTE annotator")
    result = []
    quoted_sentences = {}
    for quote in json['quotes']:
        # quote_text = quote['text']
        # to find all sentences with quotes
        sentenceIDs = list(range(quote['beginSentence'], quote['endSentence'] + 1))
        for sent in sentenceIDs:
            quoted_sentences[sent] = quoted_sentences.get(sent, 0) + 1

    # iterate over those sentence indexes and find its complete sentence
    for quoted_sent_id, number_of_quotes in quoted_sentences.items():
        sentence_data = json['sentences'][quoted_sent_id]
        # for sentence in parsedjson['sentences']:
        complete_sent = ''
        for token in sentence_data['tokens']:
            if token['originalText'] in string.punctuation:
                complete_sent = complete_sent + token['originalText']
            else:
                if token['index'] == 1:
                    complete_sent = complete_sent + token['originalText']
                else:
                    complete_sent = complete_sent + ' ' + token['originalText']

        sentenceID = quoted_sent_id
        # leave out the filename for now
        # path, file_name = os.path.split(document)
        temp = [documentID, IO_csv_util.dressFilenameForCSVHyperlink(document), sentenceID,
                complete_sent, number_of_quotes]
        result.append(temp)
    return result


# Dec. 21
def process_json_openIE(documentID, document, json, **kwargs):
    openIE = []
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
        sentenceID = sentence['index'] + 1
        SVOs = []
        for openie in sentence['openie']:
            # Document ID, Sentence ID, Document, S, V, O/A, Sentence
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
                openIE.append([documentID, sentenceID, document, row[0], row[1], row[2], complete_sent])
    # print(openIE)

    return openIE


def process_json_postag(documentID, document, json, **kwargs):

    Verbs = []
    Nouns = []
    for sentence in json['sentences']:
        for token in sentence['tokens']:
            if token['pos'] in ['VB','VBD','VBG','VBN','VBP','VBZ']:
                Verbs.append(token['lemma'])
            elif token['pos'] in ['NN','NNP','NNS']:
                Nouns.append(token['lemma'])
    return Verbs, Nouns
# floor filter: if edit distance is smaller than 5
# (round-up average length of one English word, check this reference:
# https://wolfgarbe.medium.com/the-average-word-length-in-english-language-is-4-7-35750344870f)
# return True, which means the two strings are very similar

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
                                                             dictFilename,
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
    