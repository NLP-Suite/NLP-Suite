import sys

import stanza
from stanza.pipeline.multilingual import MultilingualPipeline
import pandas as pd
import tkinter.messagebox as mb
import os
import re
import warnings
import tkinter as tk

# from tenacity import retry_unless_exception_type

import IO_files_util
import IO_csv_util
import GUI_util
import GUI_IO_util
import IO_user_interface_util
import constants_util
import parsers_annotators_visualization_util

warnings.simplefilter(action='ignore', category=FutureWarning)

import json
import stanza.resources.common
DEFAULT_MODEL_DIR = stanza.resources.common.DEFAULT_MODEL_DIR

# https://stanfordnlp.github.io/stanza/available_models.html
# language_var.set('English')
# language_list.append('English')
# LIST OF LANGUAGES AVAILABLE IN STANZA
def list_all_languages():
    with open(os.path.join(DEFAULT_MODEL_DIR, 'resources.json')) as fin:
        resources = json.load(fin)
    #languages = [lang for lang in resources if 'alias' not in resources[lang]]
    #languages = sorted(languages)
        # Extracting language codes and corresponding names from resources.json
    languages_from_resources = []
    for key, value in resources.items():
        if isinstance(value, dict) and "lang_name" in value:
            languages_from_resources.append(value["lang_name"])
    languages_from_resources.sort()
    #langs_full = sorted([dict(constants_util.languages)[x] for x in languages])
   # print(langs_full)
    return languages_from_resources

def open_Stanza_website(message, lang_list):
    url='https://stanfordnlp.github.io/stanza/available_models.html'
    Stanza_web = '\n\nLanguage and annotator options for Stanza are listed at the Stanza website\n\n' + url
    website_name = 'Stanza website'
    message_title = 'Stanza website'
    message = message + Stanza_web + '\n\nWould you like to open the Stanza website for annotator availability for the various languages supported by Stanza?'
    import IO_libraries_util
    IO_libraries_util.open_url(website_name, url, ask_to_open=True, message_title=message_title, message=message)

def get_language_list(language):
    if len(language) == 1 and language[0] != 'multilingual':
        lang = ''
    short_lang_list = []
    long_lang_list = []
    # short_lang is the abbreviated language, e.g., la
    # long_lang is the long language, e.g., Latin
    for short_lang, long_lang in lang_dict.items():
        if long_lang == language[0]:
            short_lang_list.append(short_lang)
            long_lang_list.append(long_lang)
            break
    return short_lang_list, long_lang_list

# https://stanfordnlp.github.io/stanza/available_models.html
def check_Stanza_available_languages(language):
    available_language = False
    lang_list=[]
    # language_list available in Stanza as long names: English, Chinese, ...
    language_list = list_all_languages()
    for short, long in constants_util.languages:
        if long == language[0]:
            if long in language_list:
                available_language = True
                lang_list.append(short)
                break
    available_language = True
    if not available_language:
        open_Stanza_website(str(lang_list) + ' language is not available for NLP processing in Stanza.', lang_list)
    return available_language

# check if allowed combinations of annotator and language is available in Stanza
def check_Stanza_annotator_availability(annotator_params, short_lang, long_lang, silent=False):
    annotator_available = True
    for annotator in annotator_params:
        if (short_lang not in available_NER and annotator == 'NER') \
                or (short_lang not in available_ud and annotator == 'depparse') \
                or (short_lang not in available_sentiment and annotator == 'sentiment'):
            if not silent:
                open_Stanza_website('Stanza does not currently support the ' + annotator + ' annotator for ' + long_lang + '.' + \
                                    '\n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the "Setup NLP package and corpus language" to open the GUI where you can change the language option.', [long_lang])
            annotator_available = False
    return annotator_available

# Stanza annotate functions
def Stanza_annotate(configFilename, inputFilename, inputDir,
                    outputDir,
                    openOutputFiles, createCharts, chartPackage,
                    annotator_params,
                    DoCleanXML,
                    language, # a list
                    memory_var,
                    document_length=90000,
                    sentence_length=1000,
                    print_json = True,
                    **kwargs):

    language_encoding='utf-8'
    filesToOpen = []

    if len(language)==0:
        mb.showerror("Warning",
                     "The language list is empty.\n\nPlease, select a language and try again.")
        return filesToOpen

    available_language = check_Stanza_available_languages(language)
    if not available_language:
        return filesToOpen

    # iterate through kwarg items
    extract_date_from_text_var = False
    filename_embeds_date_var = False
    google_earth_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            extract_date_from_text_var = True
        if key == 'filename_embeds_date_var' and value == True:
            filename_embeds_date_var = True
        if (key == 'google_earth_var' and value == True):
            google_earth_var = True

    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFilename)
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    tempfile=inputFilename
    if tempfile=='':
        tempfile=inputDir
    head, tail = os.path.split(tempfile)
    tail=tail.replace('.txt','')

    # annotating each input file
    docID=0
    recordID = 0
    filesError=[]
    # json = True
    errorFound=False
    total_length = 0
    # record the time consumption before annotating text in each file
    processing_doc = ''

    short_lang_list, long_lang_list = get_language_list(language)
    short_lang=short_lang_list[0]
    long_lang=long_lang_list[0]
    # check if selected language is only one and NOT multilingual
    if len(language) == 1 and language[0] != 'multilingual':

        # test if the selected language model is already downloaded, if not, download
        # IMPORTANT: no need to manually download language package after Stanza v1.4.0,
        #            if Stanza gives error for downloading, check the current version of Stanza
        nlp = stanza.Pipeline(short_lang, processors='tokenize', verbose=False)

        if "Lemma"  in annotator_params:
            annotator = 'Lemma'
            processors='tokenize,lemma,pos'
        elif "NER" in annotator_params:
            annotator = 'NER'
            processors='tokenize,ner'
        elif "All POS" in annotator_params:
            annotator = 'POS'
            processors='tokenize,pos'
        elif "depparse" in annotator_params or "SVO" in annotator_params:
            if short_lang not in available_NER:
                processors = 'tokenize,mwt,pos,lemma,depparse'  # add NER when parser option selected
            else:
                processors='tokenize,mwt,pos,ner,lemma,depparse' # add NER when parser option selected
            if "SVO" in annotator_params:
                annotator = 'SVO'
            else:
                annotator = 'depparse'
                # annotator_params = "DepRel_SVO"
        elif "sentiment" in annotator_params:
            annotator = 'sentiment'
            processors='tokenize,sentiment'

        annotator_available = check_Stanza_annotator_availability([annotator],short_lang, long_lang)
        if not annotator_available:
            return

        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                       'Started running Stanza ' + str(
                                                           annotator_params) + ' annotator at',
                                                       True, '', True, '', False)

        if 'SVO' in annotator:
            NER_available = check_Stanza_annotator_availability(['NER'], short_lang, long_lang, silent=True)
        # create the appropriate subdirectory to better organize output files
        if annotator=='depparse':
            file_label='parser (dep)'
        else:
            file_label=annotator
        outputDir = create_output_directory(inputFilename, inputDir, outputDir, file_label)

        nlp = stanza.Pipeline(lang=short_lang, processors=processors, verbose=False)

    # if only 'multilingual' is selected
    elif len(language) == 1 and language[0] == 'multilingual':
        lang_list = []
        lang_list.append('multilingual')
        nlp = MultilingualPipeline()

    # if more than one language is selected (with manual selection).
    elif len(language) > 1:
        lang_list = []
        for k,v in lang_dict.items():
            if v in language:
                lang_list.append(k)
                # stanza.download(k) # no need to manually download language package after Stanza v1.4.0
        nlp = MultilingualPipeline(lang_id_config={"langid_lang_subset":lang_list})


    df = pd.DataFrame()
    # different outputFilename if SVO is selected
    if "SVO" in annotator_params:
        svo_df = pd.DataFrame()
        svo_df_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                        'SVO_Stanza')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                'CoNLL_Stanza')
    else:
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                file_label+'_Stanza')

    for doc in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(doc)

        # extract date in file_name
        if filename_embeds_date_var:
            global date_str
            date_str = date_in_filename(doc, **kwargs)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)

        if len(language) > 1 or 'multilingual' in language: # if language detection + annotation, need to open a txt file into a list
            with open(doc, encoding=language_encoding) as f:
                text = f.read()
                if text == '':
                    mb.showinfo("Warning",
                                "The input file\n" + tail + "\nis empty. The file will be skipped from processing.\n\nPlease, check the file and try again.")
                    break
                text = text.split('\n\n')
                text = [t for t in text if not re.match(r'^\s*$', t)]
        else: # if regular annotation, open file with as string
            text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")

        if "%" in text:
            text = text.replace("%","percent")

        # process given text with customed Stanza pipeline
        Stanza_output = []
        try:
            Stanza_output = nlp(text)
        except:
            if 'multilingual' in language:
                try:
                    nlp = MultilingualPipeline(lang_id_config={"langid_lang_subset":["en", "multilingual"]})
                    Stanza_output = nlp(text)
                except:
                    mb.showinfo("Warning",
                                "Stanza encountered an error trying to download the language pack " + str(language) + "\n\nTry manually selecting the appropriate language rather than multilingual.")
                    return
            else:
                mb.showinfo("Warning",
                            "Stanza encountered an error trying to download the selected language pack " + str(language))
                return

        temp_df = convertStanzaDoctoDf(Stanza_output, inputFilename, inputDir, tail, docID, annotator_params, short_lang)
        df = pd.concat([df, temp_df], ignore_index=True, axis=0)

        # extract SVO
        if "SVO" in annotator_params:
            temp_svo_df = extractSVO(Stanza_output, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available) if len(language)==1 and 'multilingual' not in language \
                else extractSVOMultilingual(Stanza_output, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available)
            svo_df = pd.concat([svo_df, temp_svo_df], ignore_index=True, axis=0)

    df.to_csv(outputFilename, index=False, encoding=language_encoding)
    filesToOpen.append(outputFilename)

    # SVO extraction
    if "SVO" in annotator_params:

        svo_df.to_csv(svo_df_outputFilename, index=False, encoding=language_encoding)
        filesToOpen.append(svo_df_outputFilename)

        if google_earth_var is True:
            loc_df = visualize_GIS_maps_Stanza(svo_df)
            loc_df_outputFilename = kwargs["location_filename"]
            loc_df.to_csv(loc_df_outputFilename, index=False, encoding=language_encoding)
            filesToOpen.append(loc_df_outputFilename)

    # Filter + Visualization.
    language_list=IO_csv_util.get_csv_field_values(outputFilename, 'Language')
    if len(language_list)>1:
        # callback function for dropdown_menu_widget2()
        def callback(selected_language: str):
            return
        # open the dropdown menu to filter the original output with selected language
        selected_language = GUI_IO_util.dropdown_menu_widget2(GUI_util.window,
                                                    "Please, select the language you wish to use for your charts (dropdown menu on the right; press OK to accept selection; press ESCape to process all languages).",
                                                    language_list, 'Stanza languages', callback)
        # filter with selected language (using Pandas dataframe)
        selected_lang_df = df.loc[df['Language']==selected_language]
        selected_lang_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                            'Stanza_' + f'{selected_language}' + '_' + annotator_params)
        selected_lang_df.to_csv(selected_lang_outputFilename, index=False, encoding=language_encoding)
        filesToOpen.append(selected_lang_outputFilename)

    if "Lemma" in str(annotator_params) and 'Lemma' in outputFilename:
        vocab_df = excludePOS(df)
        vocab_df_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                    'Stanza_' + 'Lemma_Vocab')
        vocab_df.to_csv(vocab_df_outputFilename, index=False, encoding=language_encoding)
        filesToOpen.append(vocab_df_outputFilename)

    filesToVisualize=filesToOpen

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Stanza ' + str(annotator_params) + ' annotator at', True, '', True, startTime, False)

    for j in range(len(filesToVisualize)):
            #02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j])
            if not file_df.empty:
                # inputFilename is the original file
                # outputFilename is the csv file containing the fields to be visualized
                outputFilename = filesToVisualize[j]
                outputFiles = parsers_annotators_visualization_util.parsers_annotators_visualization(
                    configFilename, inputFilename, inputDir, outputDir,
                    outputFilename, annotator_params, kwargs, createCharts,
                    chartPackage)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    return filesToOpen

# Convert Stanza doc to pandas Dataframe
def convertStanzaDoctoDf(stanza_doc, inputFilename, inputDir, tail, docID, annotator_params, language):

    # output dataframe
    out_df = pd.DataFrame()

    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # check if more than one language has been annotated
    # Stanza doc to Pandas DataFrame conversion logic for multilingual annotation
    if annotator_params!='sentiment' and len(language) > 1 or language[0]=='multilingual' or type(stanza_doc) is list:
        try:
            dicts = []
            for doc in stanza_doc:
                temp_dicts = doc.to_dict()
                for di in temp_dicts:
                    for d in di:
                        d['lang'] = doc.lang
                        dicts.append(d)
            for i in range(len(dicts)):
                temp_df = pd.DataFrame.from_dict([dicts[i]])
                out_df = out_df.append(temp_df)
        except:
            dicts = stanza_doc.to_dict()
            for i in range(len(dicts)):
                temp_df = pd.DataFrame.from_dict(dicts[i])
                # if annotator_params=='sentiment':
                #     temp_df['sentiment_score'] = sentiment_dictionary[i]
                out_df = out_df.append(temp_df)

    # Stanza doc to Pandas DataFrame conversion logic for single language annotation
    elif annotator_params!='sentiment':
        # check if the annotator is sentiment
        # if annotator_params=='sentiment':
        #     sentiment_dictionary = {}
        #     sentence_dictionary = {}
        #     for i, sentence in enumerate(stanza_doc.sentences):
        #         sentiment_dictionary[i] = sentence.sentiment
        #         sentence_dictionary[i] = sentence.text
        dicts = stanza_doc.to_dict()
        for i in range(len(dicts)):
            temp_df = pd.DataFrame.from_dict(dicts[i])
            # if annotator_params=='sentiment':
            #     temp_df['sentiment_score'] = sentiment_dictionary[i]
            #     temp_df['Sentence'] = sentence_dictionary[i]
            out_df = out_df.append(temp_df)

    if annotator_params=='sentiment':
        for i, sentence in enumerate(stanza_doc.sentences):
            out_df.at[i, 'Sentiment score'] = sentence.sentiment
            out_df.at[i, 'Sentiment label'] = 'positive' if sentence.sentiment > 1 else 'negative' if sentence.sentiment < 1 else 'neutral'
            out_df.at[i, 'Sentence ID'] = i+1
            out_df.at[i, 'Sentence'] = sentence.text
        out_df['Document ID'] = docID
        out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    else:
        # drop the columns that don't correspond to Stanford CoreNLP output
        out_df = out_df.drop(
            ['xpos', 'start_char', 'end_char', 'multi_ner', 'feats'],
            axis=1,
            errors='ignore'
            )
        out_df = out_df.reset_index(drop=True)

        # rename the columns created by Stanza
        out_df = out_df.rename(
            columns = {
                # 'id':'ID',
                'text':'Form',
                'lemma':'Lemma',
                'upos':'POS',
                'head':'Head',
                'deprel':'DepRel',
                'ner':'NER',
                'lang':'Language',
                'sentiment_score':'Sentiment score'
            }
        )
        out_df['Multi-Word Expression'] = None
        out_df['Record ID'] = None
        out_df['Sentence ID'] = None
        out_df['Document ID'] = docID
        out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

        i = 0
        sidx = 1
        max_idx = len(out_df)-1
        for row in out_df.iterrows():
            # if i != 0 and row[1]['ID'] == 1 :
            if i != 0 and row[1]['id'] == 1:
                    sidx+=1

            # out_df.at[i, 'Record ID'] = row[1]['ID']
            out_df.at[i, 'Sentence ID'] = sidx
            if "NER" in annotator_params:
                curr_ner = out_df.at[i, 'NER']
                # process each NER tag based on BIOES representation
                if curr_ner.startswith('S'):
                    out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                elif curr_ner.startswith('B'):
                    tmp_ner = curr_ner
                    tmp_idx = i
                    # find the final index that starts with E
                    while tmp_ner.startswith('E') is False:
                        tmp_ner = out_df.at[tmp_idx, 'NER']
                        tmp_idx+=1
                    tmp_idx+=1
                    # handle possible edge case where the next NER tag starts with S or current tag is a single tag
                    if tmp_idx==i+1 or (i<=max_idx and out_df.at[i+1, 'NER'].startswith('S')):
                        out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                    else:
                        # reversely iterate through the MWE from final index to current index, and update MWE accordingly
                        for j in reversed(range(i, tmp_idx-1)):
                            if j == tmp_idx-2:
                                out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j, 'Form']
                            elif out_df.at[j, 'NER'].startswith('B') or out_df.at[j, 'NER'].startswith('S'):
                                out_df.at[j, 'Multi-Word Expression'] = out_df.at[j+1, 'Multi-Word Expression']
                                # when finally reach the first tag (B), update existing MWE with complete MWE
                                for k in reversed(range(i, tmp_idx-1)):
                                    if k==i:
                                        out_df.at[k, 'Multi-Word Expression'] = out_df.at[j, 'Multi-Word Expression']
                                    else:
                                        out_df.at[k, 'Multi-Word Expression'] = ''
                            elif out_df.at[j, 'NER'].startswith('I'):
                                out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j+1 , 'Multi-Word Expression']
            i+=1

        if 'Language' in out_df.columns:
            out_df = out_df[ [ col for col in out_df.columns if col != 'Language' ] + ['Language'] ]
            for idx in range(len(out_df)):
                temp_lang = out_df.at[idx, 'Language']
                out_df.at[idx, 'Language'] = lang_dict[temp_lang]

    if "Lemma"  in annotator_params:
        # out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'Lemma', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "NER" in annotator_params:
        # out_df = out_df[['ID', 'Form', 'NER', 'Multi-Word Expression','Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'NER', 'Multi-Word Expression','Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "All POS" in annotator_params:
        # out_df = out_df[['ID', 'Form', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "depparse" in annotator_params or "SVO" in annotator_params:
        if language not in available_NER:
            # out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'Head', 'DepRel', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
            out_df = out_df[['Form', 'Lemma', 'POS', 'Head', 'DepRel', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        else:
            # out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'NER', 'Head', 'DepRel', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
            out_df = out_df[['Form', 'Lemma', 'POS', 'NER', 'Head', 'DepRel', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "sentiment" in annotator_params:
        out_df = out_df[['Sentiment score', 'Sentiment label', 'Sentence ID', 'Sentence', 'Document ID', 'Document']]
    return out_df

# extract SVO from Stanza doc (depparse)
# input: Stanza Document
def extractSVO(doc, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available):
    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # output: svo_df
    if filename_embeds_date_var:
        svo_df = pd.DataFrame(columns=['Subject (S)','Verb (V)','Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Sentence', 'Date'])
    else:
        svo_df = pd.DataFrame(columns=['Subject (S)','Verb (V)','Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Sentence'])
    empty_verb_idx = []
    SVO_found = False
    NER_found = False # boolean value for NER tags

    # object and subject constants
    OBJECT_DEPS = {"obj", "iobj", "dobj", "dative", "attr", "oprd"}
    SUBJECT_DEPS = {"nsubj", "nsubj:pass", "csubj", "agent"} #, "expl"}
    # NER tags dictionary for location, person and time
    NER_LOCATION = {"S-GPE", "B-GPE", "I-GPE", "E-GPE", "S-LOC", "B-LOC", "I-LOC", "E-LOC"}
    NER_PERSON = {"S-PERSON", "B-PERSON", "I-PERSON", "E-PERSON"}
    NER_TIME = {"S-TIME", "B-TIME", "I-TIME", "E-TIME", "S-DATE", "B-DATE", "I-DATE", "E-DATE",}

    # extraction of SVOs
    c = 0
    for sentence in doc.sentences:
        sent_dict = sentence.to_dict()
        S_found = False
        V_found = False
        O_found = True
        for w,word in enumerate(sentence.words):
            # tmp_head = sentence.words[word.head-1].deprel if word.head > 0 else "root"
            # if (word.deprel in SUBJECT_DEPS or tmp_head in SUBJECT_DEPS) and (SVO_found):
            if (word.deprel in SUBJECT_DEPS) and (O_found):
                svo_df.at[c, 'Subject (S)'] = word.text
                S_found = True
                O_found = False
            if word.pos=='VERB':
                if S_found:
                    svo_df.at[c, 'Verb (V)'] = word.text
                    V_found = True
            # if word.deprel in OBJECT_DEPS or tmp_head in OBJECT_DEPS:
            if word.deprel in OBJECT_DEPS:
                if S_found:
                    svo_df.at[c, 'Object (O)'] = word.text
                    O_found = True
            # extract NER values
            if (SVO_found or NER_found) and NER_available:
                token = sent_dict[w]
                if token['ner'] in NER_LOCATION:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Location', NER_found)
                elif token['ner'] in NER_PERSON:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Person', NER_found)
                elif token['ner'] in NER_TIME:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Time', NER_found)
            # check if SVO is found, then add Sentence ID
            if S_found and V_found and O_found:
                svo_df.at[c, 'Sentence'] =  sentence.text
                svo_df.at[c, 'Sentence ID'] =  c+1
                S_found = False
                V_found = False
                O_found = False
                c+=1

    # csv output columns
    svo_df['Document ID'] = docID
    svo_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    # replace NaN values accordingly
    for index, row in svo_df.iterrows():
        svo_df.at[index, 'Subject (S)'] = '?' if pd.isna(row['Subject (S)']) else row['Subject (S)']
        svo_df.at[index, 'Verb (V)'] = '' if pd.isna(row['Verb (V)']) else row['Verb (V)']
        svo_df.at[index, 'Object (O)'] = '' if pd.isna(row['Object (O)']) else row['Object (O)']
        # save empty verb indices
        if pd.isna(row['Verb (V)']):
            empty_verb_idx.append(index)
    # drop empty Verb rows
    svo_df = svo_df.drop(empty_verb_idx)

    # set the S-V-O sequence in order
    # add date from filename
    if filename_embeds_date_var:
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date']]
        svo_df['Date'] = date_str
    else:
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Sentence', 'Document ID', 'Document']]

    return svo_df

# only different word will be separated by semi-colon
# extract NERs
# stanza returns NER tags with BIOES representation of the entities
# i.e) "Doctor" -> "Doctor" : "S-PERSON"
# i.e) "Chris Manning" -> "Chris" : "B-PERSON", "Manning" : "E-PERSON"
# i.e) "the Bay Area" -> "the" : "B-LOC", "Bay" : "I-LOC", "Area" : "E-LOC"
def extractNER(word, df, idx, column, NER_bool):
    if word['ner'].startswith("B") or word['ner'].startswith("I"):
        # change NER boolean value
        if word['ner'].startswith("B"):
            NER_bool = True
        tempNER = df.at[idx, column]
        currentNER = word['text']
        if not isinstance(tempNER, str):
            df.at[idx, column] = currentNER
        else:
            df.at[idx, column] = tempNER + ' ' + currentNER
    elif word['ner'].startswith("S") or word['ner'].startswith("E"):
        tempNER = df.at[idx, column]
        currentNER = word['text']
        if not isinstance(tempNER, str):
            df.at[idx, column] = currentNER + ';'
        else:
            df.at[idx, column] = tempNER + ' ' + currentNER + ';'
        NER_bool = False
    elif isinstance(df.at[idx, column], str):
        tempNER = df.at[idx, column]
        currentNER = word['text']
        if not isinstance(tempNER, str):
            df.at[idx, column] = currentNER
        else:
            df.at[idx, column] = tempNER + ' ' + currentNER
    else:
        df.at[idx, column] = word['text']

    return df, NER_bool

# extract SVO from multilingual doc
def extractSVOMultilingual(stanza_doc, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available):
    # output dataframe
    out_df = pd.DataFrame()

    # stanza doc to dict
    for doc in stanza_doc:
        temp_svo = extractSVO(doc, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available)
        out_df = out_df.append(temp_svo)

    return out_df

# input: Stanza DF
def excludePOS(df, postag={'NUM', 'PUNCT'}):
    for p in postag:
        df = df[df["POS"].str.contains(p)==False]
    return df

# extract date in filename from Stanford_CoreNLP_util
def date_in_filename(document, **kwargs):
    filename_embeds_date_var = False
    date_format = ''
    items_separator_var = ''
    date_position_var = 0
    date_str = ''
    # process the optional values in kwargs
    for key, value in kwargs.items():
        if key == 'filename_embeds_date_var' and value == True:
            filename_embeds_date_var = True
        if key == 'date_format':
            date_format = value
        if key == 'items_separator_var':
            items_separator_var = value
        if key == 'date_position_var':
            date_position_var = value
    if filename_embeds_date_var:
        date, date_str, month, day, year = IO_files_util.getDateFromFileName(document,  date_format, items_separator_var, date_position_var)
    return date_str

# create locations file for GIS
def visualize_GIS_maps_Stanza(svo_df):
    loc_df = pd.DataFrame(columns=['Location', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
    for _,row in svo_df.iterrows():
        if isinstance(row['Location'], str):
            loc_list = row['Location'].split(';')
            for loc in loc_list:
                if loc != '':
                    loc_df.loc[len(loc_df.index)] = [loc, 'LOCATION', row['Sentence ID'], row['Sentence'], row['Document ID'], 'Document']
    return loc_df

# modified from StanfordCoreNLP_util
def create_output_directory(inputFilename, inputDir, outputDir,
                            annotator):
    outputDirSV=GUI_util.output_dir_path.get()
    if outputDirSV != outputDir:
        # create output subdirectory
        outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                           label=annotator,
                                                           silent=True)
    else:
        outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                           label=annotator + "_Stanza",
                                                           silent=True)

    return outputDir

# Python dictionary of language (values) and their acronyms (keys)
lang_dict = {}
lang_dict_rev = {}
# lang_dict_rev will use alias, instead of lang_name, as found in resources.json
# e.g., stanza.download(Stanza_util.lang_dict_rev['en'])
import stanza.resources.common

EFAULT_MODEL_DIR = stanza.resources.common.DEFAULT_MODEL_DIR
resources_path = os.path.join(DEFAULT_MODEL_DIR, 'resources.json')
if not os.path.exists(resources_path):
    mb.showwarning(title='Warning',
                   message='Stanza does not seem to be installed in your machine. The file-path\n\n' + resources_path + '\n\ncould not be found.\n\nPlease, open terminal, type conda activate NLP (Enter) and then type pip install stanza (Enter) and try again.')
    sys.exit()

with open(os.path.join(DEFAULT_MODEL_DIR, 'resources.json')) as fin:
    resources = json.load(fin)
for key, value in resources.items():
    if isinstance(value, dict) and "lang_name" in value:
        lang_dict[key]=value["lang_name"]
        lang_dict_rev[value['lang_name']]=key

# Available Stanza models for languages
available_ud = [
    "af",
    "grc",
    "ar",
    "hy",
    "eu",
    "be",
    "bg",
    "ca",
    "zh",
    "zh-hant",
    "lzh",
    "cop",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "et",
    "fi",
    "fr",
    "gl",
    "de",
    "got",
    "el",
    "he",
    "hi",
    "hu",
    "id",
    "ga",
    "it",
    "ja",
    "ko",
    "la",
    "lv",
    "lt",
    "mt",
    "mr",
    "sme",
    "no",
    "nb",
    "nn",
    "cu",
    "fro",
    "orv",
    "fa",
    "pl",
    "pt",
    "ro",
    "ru",
    "gd",
    "sr",
    "sk",
    "sl",
    "es",
    "sv",
    "ta",
    "te",
    "tr",
    "uk",
    "ur",
    "ug",
    "vi",
    "wo",
]

available_sentiment = [
    "en",
    "zh",
    "de"
]

available_NER = [
    "af",
    "ar",
    "bg",
    "zh",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "hu",
    "it",
    "ja",
    "my",
    "nb",
    "nn",
    "fa",
    "ru",
    "es",
    "sv",
    "tr",
    "uk",
    "vi",
    ]

NER_dict = {
    "fr": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "en": [
        "CARDINAL",
        "DATE",
        "EVENT",
        "FAC",
        "GPE",
        "LANGUAGE",
        "LAW",
        "LOC",
        "MONEY",
        "NORP",
        "ORDINAL",
        "ORG",
        "PERCENT",
        "PERSON",
        "PRODUCT",
        "QUANTITY",
        "TIME",
        "WORK_OF_ART"
    ],
    "zh-hans": [
        "CARDINAL",
        "DATE",
        "EVENT",
        "FAC",
        "GPE",
        "LANGUAGE",
        "LAW",
        "LOC",
        "MONEY",
        "NORP",
        "ORDINAL",
        "ORG",
        "PERCENT",
        "PERSON",
        "PRODUCT",
        "QUANTITY",
        "TIME",
        "WORK_OF_ART"
    ],
    "ru": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "uk": [
        "LOC",
        "MISC",
        "ORG",
        "PERS"
    ],
    "ar": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "hu": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "af": [
        "LOC",
        "MISC",
        "ORG",
        "PERS"
    ],
    "bg": [
        "EVT",
        "LOC",
        "ORG",
        "PER",
        "PRO"
    ],
    "fi": [
        "DATE",
        "EVENT",
        "LOC",
        "ORG",
        "PER",
        "PRO"
    ],
    "my": [
        "LOC",
        "NE",
        "NUM",
        "ORG",
        "PNAME",
        "RACE",
        "TIME"
    ],
    "it": [
        "LOC",
        "ORG",
        "PER"
    ],
    "de": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "nl": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ],
    "vi": [
        "LOCATION",
        "MISCELLANEOUS",
        "ORGANIZATION",
        "PERSON"
    ],
    "es": [
        "LOC",
        "MISC",
        "ORG",
        "PER"
    ]
}
