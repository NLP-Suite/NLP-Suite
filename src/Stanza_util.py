import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Stanza_util.py",['stanza','os','tkinter','multiprocessing','pandas','gensim','spacy','pyLDAvis','matplotlib','logging','IPython'])==False:
    sys.exit(0)

import os as _os
import stanza
try:
    _stanza_model_dir = _os.path.join(_os.path.expanduser('~'), 'stanza_resources', 'en')
    if not _os.path.isdir(_stanza_model_dir):
        import IO_user_interface_util
        IO_user_interface_util.timed_alert(GUI_util.window, 6000, 'Stanza model download',
            'Downloading the Stanza language model for the first time (~525 MB).\n\nThis is a one-time download. Please be patient, it may take several minutes depending on your internet connection.',
            False)
    stanza.download('en')
except:
    pass

from stanza.pipeline.multilingual import MultilingualPipeline

import pandas as pd
import tkinter.messagebox as mb
import sys
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
import Stanford_CoreNLP_clause_util

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

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
            language_name=value["lang_name"]
            # reverse the names to have them in proper sort order
            # should do the same for Greek, Hebrew, and other languages
            # CHINESE
            if "_Chinese" in language_name:
                # reconstruct name from, e.g., Simplified_Chinese to Chinese_Simplified so that all Chinese are sorted together
                language_name=value["lang_name"].split('_')[-1]+'_'+value["lang_name"].split('_')[0]
            # Chinese_Traditional has very limited annotators; might as well remove it not to confuse the user
            # FRENCH
            if "_French" in language_name:
                # reconstruct name from, so that all French are sorted together
                language_name=value["lang_name"].split('_')[-1]+'_'+value["lang_name"].split('_')[0]
            # GREEK
            if "_Greek" in language_name:
                # reconstruct name from, so that all Greek are sorted together
                language_name=value["lang_name"].split('_')[-1]+'_'+value["lang_name"].split('_')[0]
            # HEBREW
            if "_Hebrew" in language_name:
                # reconstruct name from, so that all Hebrew are sorted together
                language_name=value["lang_name"].split('_')[-1]+'_'+value["lang_name"].split('_')[0]
            # RUSSIAN
            if "_Russian" in language_name:
                # reconstruct name from, so that all Hebrew are sorted together
                language_name=value["lang_name"].split('_')[-1]+'_'+value["lang_name"].split('_')[0]
            # do not process Chinese_Traditional since it can handle very few annotators
            if not "Chinese_Traditional" in language_name:
                languages_from_resources.append(language_name)

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
        # reverse the names to have them in proper sort order
        # should do the same for Greek, Hebrew, and other languages
        if long_lang=='Simplified_Chinese':
            long_lang='Chinese_Simplified'
        if long_lang=='Traditional_Chinese':
            long_lang='Chinese_Traditional'
        if long_lang=='Old_French':
            long_lang='French_Old'
        if long_lang=='Ancient_Greek':
            long_lang='Greek_Ancient'
        if long_lang=='Ancient_Hebrew':
            long_lang='Hebrew_Ancient'
        if long_lang=='Old_Russian':
            long_lang='Russian_Old'
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
                    openOutputFiles, chartPackage, dataTransformation,
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

    if len(short_lang_list)==0:
        mb.showinfo("Warning",
                    "The selected language\n" + " ".join(language) + "\nis not supported with this name in Stanza. Please, make sure you have not entered the wrong language name in the NLP_setup_package_language_main GUI (perhaps, a left over after selecting Stanza after a differrent package).\n\nPlease, check the language and try again.")
        return
    short_lang=short_lang_list[0]
    long_lang=long_lang_list[0]
    # check if selected language is only one and NOT multilingual
    if len(language) == 1 and language[0] != 'multilingual':

        # test if the selected language model is already downloaded, if not, download
        # IMPORTANT: no need to manually download language package after Stanza v1.4.0,
        #            if Stanza gives error for downloading, check the current version of Stanza
        nlp = stanza.Pipeline(short_lang, processors='tokenize', verbose=False)

        if "Lemma" in annotator_params:
            annotator = 'Lemma'
            processors='tokenize,lemma,pos'
        elif "All POS" in annotator_params or "POS" in annotator_params:
            annotator = 'POS'
            processors = 'tokenize,pos'
        elif "NER" in annotator_params:
            annotator = 'NER'
            processors='tokenize,ner'
        elif "depparse" in annotator_params or "SVO" in annotator_params:
            constituency_ok = short_lang in available_constituency
            if short_lang not in available_NER:
                if short_lang not in available_mwt:
                    processors = 'tokenize,pos,lemma,depparse'
                else:
                    processors = 'tokenize,pos,mwt,lemma,depparse'
            else:
                if short_lang not in available_mwt:
                    processors = 'tokenize,pos,ner,lemma,depparse'
                else:
                    processors = 'tokenize,pos,mwt,ner,lemma,depparse'
            if constituency_ok:
                processors += ',constituency'

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

        if "Lemma" in annotator_params:
            annotator = 'Lemma'
            label = 'Lemma'
        elif "NER" in annotator_params:
            annotator = 'NER'
            label = 'NER'
        elif "All POS" in annotator_params:
            annotator = 'POS'
            label = 'POS'
        elif "SVO" in annotator_params:
            annotator = 'SVO'
        elif "depparse" in annotator_params:
            annotator = 'depparse'
            label = 'parser (dep)'
        elif "sentiment" in annotator_params:
            annotator = 'sentiment'
            label = 'sentiment'

        # create the appropriate subdirectory to better organize output files                                               silent=False)

        if annotator == 'SVO':
            NER_available = check_Stanza_annotator_availability(['NER'], short_lang, long_lang, silent=True)
            # a CoNLL table is exported automatically for spaCy and Stanza
            outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                               label=annotator + "_CoNLL",
                                                               silent=True)
        else:
            outputDir = create_output_directory(inputFilename, inputDir, outputDir, annotator)

        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                       'Started running Stanza ' + str(annotator_params) +
                                                       (' extraction' if 'SVO' in str(annotator_params).upper()
                                                        else ' annotator') + ' at',
                                                       True, '', True, '', False)

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

    # different outputFilename if SVO is selected
    if "SVO" in annotator_params:
        svo_df = pd.DataFrame()
        svo_df_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                        'SVO_Stanza')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                'CoNLL_Stanza')
    else:
        if 'depparse' in annotator_params:
            annotator_label='CoNLL'
        else:
            annotator_label=annotator
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                annotator_label+'_Stanza')

    # create output df
    df = pd.DataFrame()

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

        # the dt dataframe when running SVO is the CoNLL table, saved later, after processing all input files
        # it needs to be added here so as to know exactly the place of the CoNLL table in the output files list
        filesToOpen.append(outputFilename)

        # SVO extraction
        if "SVO" in annotator_params:

            # extract SVO
            temp_svo_df = extractSVO(Stanza_output, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available) if len(language)==1 and 'multilingual' not in language \
                else extractSVOMultilingual(Stanza_output, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available)
            svo_df = pd.concat([svo_df, temp_svo_df], ignore_index=True, axis=0)

            svo_df.to_csv(svo_df_outputFilename, index=False, encoding=language_encoding)
            filesToOpen.append(svo_df_outputFilename)

            if google_earth_var is True:
                loc_df = visualize_GIS_maps_Stanza(svo_df)
                loc_df_outputFilename = kwargs["location_filename"]
                loc_df.to_csv(loc_df_outputFilename, index=False, encoding=language_encoding)
                filesToOpen.append(loc_df_outputFilename)

    # filter NER output to the user-selected tags (when a subset is selected);
    # only for a standalone NER run (the SVO/parse df is a CoNLL table, not to be filtered)
    if "NER" in str(annotator_params) and "SVO" not in str(annotator_params) \
            and "parse" not in str(annotator_params):
        df = filter_NER_output_by_tags(df, kwargs.get('NERs', ''), short_lang)

    # save dataframe to csv
    df.to_csv(outputFilename, index=False, encoding=language_encoding)

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

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Stanza ' + str(annotator_params) + (' extraction' if 'SVO' in str(annotator_params).upper() else ' annotator') + ' at', True, '', True, startTime, False)

    filesToVisualize=filesToOpen

    for j in range(len(filesToVisualize)):
            #02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j],encoding='utf-8',on_bad_lines='skip')
            if not file_df.empty:
                # inputFilename is the original file
                # outputFilename is the csv file containing the fields to be visualized
                outputFilename = filesToVisualize[j]
                outputFiles = parsers_annotators_visualization_util.parsers_annotators_visualization(
                    configFilename, inputFilename, inputDir, outputDir,
                    outputFilename, annotator_params, kwargs, 
                    chartPackage, dataTransformation)
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
    if 'sentiment' not in annotator_params and len(language) > 1 or language[0]=='multilingual' or type(stanza_doc) is list:
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
                out_df = pd.concat([out_df, temp_df], ignore_index=True)
        except:
            dicts = stanza_doc.to_dict()
            for i in range(len(dicts)):
                temp_df = pd.DataFrame.from_dict(dicts[i])
                # if annotator_params=='sentiment':
                #     temp_df['sentiment_score'] = sentiment_dictionary[i]
                out_df = pd.concat([out_df, temp_df], ignore_index=True)

    # Stanza doc to Pandas DataFrame conversion logic for single language annotation
    elif 'sentiment' not in annotator_params:
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
            out_df = pd.concat([out_df, temp_df], ignore_index=True)

    if 'sentiment' in annotator_params:
        # Stanza sentiment returns 0 (negative), 1 (neutral), 2 (positive) — a coarse 3-class scale
        doc_hyperlink = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)
        sent_rows = []
        for i, sentence in enumerate(stanza_doc.sentences):
            s = sentence.sentiment
            sent_rows.append({
                'Sentiment score': s,
                'Sentiment label': 'positive' if s > 1 else ('negative' if s < 1 else 'neutral'),
                'Sentence ID': i + 1,
                'Sentence': sentence.text,
                'Document ID': docID,
                'Document': doc_hyperlink
            })
        out_df = pd.DataFrame(sent_rows, columns=[
            'Sentiment score', 'Sentiment label', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])

    else:
        # drop the columns that don't correspond to Stanford CoreNLP output
        # out_df = out_df.drop(
        #     ['xpos', 'start_char', 'end_char', 'multi_ner', 'feats'],
        #     axis=1,
        #     errors='ignore'
        #     )
        # feats allows you to study verb mood
        out_df = out_df.drop(
            ['xpos', 'start_char', 'end_char', 'multi_ner'],
            axis=1,
            errors='ignore'
            )
        out_df = out_df.reset_index(drop=True)

        # rename the columns created by Stanza
        out_df = out_df.rename(
            columns = {
                'id':'ID',
                'text':'Form',
                'lemma':'Lemma',
                'upos':'POS',
                'head':'Head',
                'deprel':'DepRel',
                'ner':'NER',
                'feats':'feats',
                'lang':'Language',
                'sentiment_score':'Sentiment score'
            }
        )
        out_df['Multi-Word Expression'] = None
        out_df['Record ID'] = None
        out_df['Sentence ID'] = None
        out_df['Document ID'] = docID
        out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

        # Extract clause tags from constituency parse trees (when available)
        out_df['Clause Tag'] = ''
        if ("depparse" in str(annotator_params) or "SVO" in str(annotator_params)):
            has_constituency = False
            try:
                sentences = stanza_doc.sentences if not isinstance(stanza_doc, list) else [s for doc in stanza_doc for s in doc.sentences]
                if len(sentences) > 0 and hasattr(sentences[0], 'constituency') and sentences[0].constituency is not None:
                    has_constituency = True
            except:
                pass
            if has_constituency:
                clause_tags_all = []
                for sent in sentences:
                    tree_str = str(sent.constituency)
                    try:
                        full_list, _ = Stanford_CoreNLP_clause_util.clausal_info_extract_from_string(tree_str)
                        for tag_list in full_list:
                            clause_tags_all.append(tag_list[0] if isinstance(tag_list, list) else '')
                    except:
                        for _ in sent.words:
                            clause_tags_all.append('')
                if len(clause_tags_all) == len(out_df):
                    out_df['Clause Tag'] = clause_tags_all

        i = 0
        sidx = 1
        max_idx = len(out_df)-1
        for row in out_df.iterrows():
            if i != 0 and row[1]['ID'] == 1:
                sidx+=1
            out_df.at[i, 'Record ID'] = i+1
            out_df.at[i, 'Sentence ID'] = sidx
            if "NER" in annotator_params and language == 'la':
                open_Stanza_website(
                    'Stanza does not currently support the NER annotator for Latin.' + \
                    '\n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the "Setup NLP package and corpus language" to open the GUI where you can change the language option.')
            if ("NER" in annotator_params or "depparse" in str(annotator_params)) and language != 'la':
                curr_ner = str(out_df.at[i, 'NER'])
                # process each  NER tag based on BIOES representation
                if curr_ner.startswith('S'):
                    # print(out_df.at[i, 'Form'])
                    out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                elif curr_ner.startswith('B'):
                    tmp_ner = curr_ner
                    tmp_idx = i
                    # find the final index that starts with E
                    # if tmp_ner=='B-Time':
                    #     print('@@@ 1')
                    while str(tmp_ner).startswith('E') is False:
                        tmp_ner = out_df.at[tmp_idx, 'NER']
                        tmp_idx+=1
                    tmp_idx+=1
                    # handle possible edge case where the next NER tag starts with S or current tag is a single tag
                    if tmp_idx==i+1 or (i<=max_idx and str(out_df.at[i+1, 'NER']).startswith('S')):
                        out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                    else:
                        # reversely iterate through the MWE from final index to current index, and update MWE accordingly
                        for j in reversed(range(i, tmp_idx-1)):
                            if j == tmp_idx-2:
                                out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j, 'Form']
                            elif str(out_df.at[j, 'NER']).startswith('B') or str(out_df.at[j, 'NER']).startswith('S'):
                                out_df.at[j, 'Multi-Word Expression'] = out_df.at[j+1, 'Multi-Word Expression']
                                # when finally reach the first tag (B), update existing MWE with complete MWE
                                for k in reversed(range(i, tmp_idx-1)):
                                    if k==i:
                                        out_df.at[k, 'Multi-Word Expression'] = out_df.at[j, 'Multi-Word Expression']
                                    else:
                                        out_df.at[k, 'Multi-Word Expression'] = ''
                            elif str(out_df.at[j, 'NER']).startswith('I'):
                                if (out_df.at[j + 1, 'Multi-Word Expression']) is None:
                                    out_df.at[j, 'Multi-Word Expression'] = out_df.at[j - 1, 'Form'] + ' '
                                else:
                                    try:
                                        out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j+1 , 'Multi-Word Expression']
                                    except:
                                        print()
            i+=1

        if 'Language' in out_df.columns:
            out_df = out_df[ [ col for col in out_df.columns if col != 'Language' ] + ['Language'] ]
            for idx in range(len(out_df)):
                temp_lang = out_df.at[idx, 'Language']
                out_df.at[idx, 'Language'] = lang_dict[temp_lang]

    if "Lemma" in annotator_params:
        # out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'Lemma', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "NER" in annotator_params:
        # out_df = out_df[['ID', 'Form', 'NER', 'Multi-Word Expression','Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'NER', 'Multi-Word Expression','Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "All POS" in annotator_params:
        # out_df = out_df[['ID', 'Form', 'POS', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        out_df = out_df[['Form', 'POS', 'feats', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "depparse" in annotator_params or "SVO" in annotator_params:
        if language not in available_NER:
            out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'feats', 'Head', 'DepRel', 'Clause Tag', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
        else:
            out_df = out_df[['ID', 'Form', 'Lemma', 'POS', 'NER', 'feats', 'Multi-Word Expression', 'Head', 'DepRel', 'Clause Tag', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]
    elif "sentiment" in annotator_params:
        out_df = out_df[['Sentiment score', 'Sentiment label', 'Sentence ID', 'Sentence', 'Document ID', 'Document']]
    return out_df

# extract SVO from Stanza doc (depparse)
# input: Stanza Document
# ─────────────────────────────────────────────────────────────────────
# Enhanced SVO extraction for Stanza
# Ported from Stanford_CoreNLP_SVO_enhanced_dependencies_util.py
# ─────────────────────────────────────────────────────────────────────

# Negation words recognised by the SVO extractor
_NEGATION_TOKENS = {"no", "not", "n't", "seldom", "without", "never", "hardly", "neither", "nor"}
# Dependency relations whose children may carry negation
_NEGATION_DEPS = {"advmod", "det", "cc:preconj", "cc", "mark", "aux"}


def _build_govern_dict(sentence):
    """Build a CoreNLP-style govern_dict from a Stanza sentence.

    For each word in *sentence* we produce a dict keyed by word.id
    containing:
        word, pos, lemma, ner, deprel, id, govern_dict

    govern_dict maps  dep_label → child_id  (or list of child_ids when
    multiple children share the same label).

    Stanza uses Universal Dependencies (UD) labels which map almost 1-to-1
    to CoreNLP enhanced++ dependencies.  Key differences handled here:
        UD  obl          → CoreNLP obl:<case>     (we attach the case marker)
        UD  nmod         → CoreNLP nmod:<case>
        UD  conj         → CoreNLP conj:<cc>
    """
    sent_data = {}
    # First pass: basic per-word info
    for word in sentence.words:
        ner_tag = 'O'
        # Stanza stores NER on tokens, not words.  Map via start_char.
        if hasattr(word, 'parent') and hasattr(word.parent, 'ner'):
            ner_tag = word.parent.ner if word.parent.ner else 'O'
        sent_data[word.id] = {
            'id': word.id,
            'word': word.text,
            'pos': word.xpos if word.xpos else word.upos,
            'upos': word.upos,
            'lemma': word.lemma,
            'ner': ner_tag,
            'deprel': word.deprel,
            'head': word.head,
            'govern_dict': {},
        }

    # Second pass: build govern_dict (children grouped under their head)
    # Also refine dep labels by attaching case/cc markers
    for word in sentence.words:
        head_id = word.head
        if head_id == 0:
            continue  # ROOT — no governor
        dep = word.deprel
        gd = sent_data[head_id]['govern_dict']
        # For obl / nmod attach the case marker to the label
        if dep in ('obl', 'nmod'):
            case_word = _find_case_marker(word.id, sentence)
            if case_word:
                dep = dep + ':' + case_word
        # For conj attach the cc word
        elif dep == 'conj':
            cc_word = _find_cc_marker(word.id, head_id, sentence)
            if cc_word:
                dep = 'conj:' + cc_word
        # nsubj:pass  (Stanza already uses this label)
        # obl:agent   (Stanza uses obl + "by" case — already handled above → obl:by)
        # We remap obl:by when it looks like a passive agent
        if dep == 'obl:by':
            # If the head verb has a nsubj:pass child, then obl:by is the agent
            head_has_pass = any(
                w.deprel == 'nsubj:pass' and w.head == head_id
                for w in sentence.words
            )
            if head_has_pass:
                dep = 'obl:agent'

        # Store in govern_dict
        if dep in gd:
            existing = gd[dep]
            if isinstance(existing, list):
                existing.append(word.id)
            else:
                gd[dep] = [existing, word.id]
        else:
            gd[dep] = word.id

    return sent_data


def _find_case_marker(word_id, sentence):
    """Find the case/mark dependent of word_id to refine obl/nmod labels."""
    for w in sentence.words:
        if w.head == word_id and w.deprel in ('case', 'mark'):
            return w.lemma.lower()
    return None


def _find_cc_marker(conj_id, head_id, sentence):
    """Find the coordinating conjunction between head and conjunct."""
    for w in sentence.words:
        if w.head == head_id and w.deprel == 'cc':
            return w.lemma.lower()
        # Sometimes cc attaches to the conjunct itself
        if w.head == conj_id and w.deprel == 'cc':
            return w.lemma.lower()
    return None


# ── Negation detection (recursive, mirrors CoreNLP version) ────────

def _negation_detect(token, sent_data):
    """Return True if negation is associated with this token."""
    gd = token['govern_dict']
    if not gd:
        return False
    for dep in _NEGATION_DEPS:
        if dep not in gd:
            continue
        ids = gd[dep] if isinstance(gd[dep], list) else [gd[dep]]
        for idx in ids:
            if sent_data[idx]['word'].lower() in _NEGATION_TOKENS:
                return True
            if _negation_detect(sent_data[idx], sent_data):
                return True
    return False


def _content_negation(content, sent_data):
    """Check negation within a subject or object span."""
    if isinstance(content, list):
        for idx in content:
            if _negation_detect(sent_data[idx], sent_data):
                return True
        return False
    return _negation_detect(sent_data[content], sent_data)


# ── Multi-token formation (conjuncts, compounds) ──────────────────

def _token_connect(keys, sent_data):
    """Join multiple tokens with spaces."""
    if isinstance(keys, list):
        return ' '.join(sent_data[k]['word'] for k in keys)
    return sent_data[keys]['word']


def _conj_string(subjects, sent_data):
    """Connect conjugate subjects/objects into 'A, B, and C'."""
    subj = subjects[0]
    result = sent_data[subj]['word']
    start_result = result
    gd = sent_data[subj]['govern_dict']
    for key in gd:
        if 'conj' in key:
            conj = key[5:] if len(key) > 5 else 'and'
            dep_val = gd[key]
            if isinstance(dep_val, list):
                if dep_val == subjects[1:]:
                    for i in range(1, len(subjects) - 1):
                        result += ', ' + sent_data[subjects[i]]['word']
                    result += ', ' + conj + ' ' + sent_data[subjects[-1]]['word']
                    break
            else:
                if len(subjects) == 2 and subjects[-1] == dep_val:
                    result += ' ' + conj + ' ' + sent_data[subjects[-1]]['word']
                    break
    if result == start_result:
        result = _token_connect(subjects, sent_data)
    return result


def _s_o_formation(subjects, sent_data):
    """Process subject/object — may be single word or conjunct list."""
    if isinstance(subjects, list):
        return _conj_string(subjects, sent_data), subjects[0]
    return sent_data[subjects]['word'], subjects


# ── Verb helpers ──────────────────────────────────────────────────

def _verb_index_conj(key, token, gov_dict, sent_data):
    """Extract conjunct verbs and the conjunction word."""
    verb_list = [key]
    conj_word = ''
    dep = ''
    for label in ('conj:or', 'conj:and', 'conj:nor'):
        if label in gov_dict:
            dep = label
            conj_word = label[5:]
            break
    if dep:
        val = gov_dict[dep]
        if isinstance(val, list):
            verb_list.extend(val)
        else:
            verb_list.append(val)
    return verb_list, conj_word


def _load_lvc_json(filename):
    """Load an LVC / verb-prep JSON dictionary from lib."""
    filepath = os.path.join(GUI_IO_util.CoreNLP_enhanced_dependencies_libPath, filename)
    if not os.path.isfile(filepath):
        return {}
    with open(filepath) as f:
        try:
            return json.load(f)
        except ValueError:
            return {}


def _verb_obj_obl(token, sent_data, v_obj_obl_json):
    """Check if verb is part of a Light Verb Construction (LVC).

    Handles both CoreNLP-style (obl on verb) and Stanza-style (nmod on object noun)
    dependency structures.
    """
    new_v, new_o, key = '', '', ''
    gd = token['govern_dict']
    lemma = token['lemma']
    if lemma not in v_obj_obl_json or 'obj' not in gd:
        return new_v, new_o, key
    obj_text = _s_o_formation(gd['obj'], sent_data)[0]
    obj_id = gd['obj'][0] if isinstance(gd['obj'], list) else gd['obj']
    obj_gd = sent_data[obj_id]['govern_dict']  # object noun's govern_dict

    for conb in v_obj_obl_json[lemma]:
        if conb.get('obj', '').lower() != obj_text.lower():
            continue
        obl_key = 'obl' if 'obl' in conb else ('nmod' if 'nmod' in conb else None)
        if obl_key is None:
            continue
        obl_prep = obl_key + ':' + conb[obl_key]
        # Also try alternate key forms (Stanza may use nmod where CoreNLP uses obl)
        alt_prep = ('nmod:' + conb[obl_key]) if obl_key == 'obl' else ('obl:' + conb[obl_key])

        start_idx = token['id']
        end_idx = obj_id
        new_v = ''
        for i in range(start_idx, end_idx + 1):
            if i in sent_data:
                new_v += sent_data[i]['word'] + ' '
        new_v += conb[obl_key]

        # Look for the real object: first on verb's govern_dict, then on object noun's
        found = False
        for search_gd, search_key in [(gd, obl_prep), (gd, alt_prep),
                                       (obj_gd, obl_prep), (obj_gd, alt_prep)]:
            if search_key in search_gd:
                new_o = _s_o_formation(search_gd[search_key], sent_data)[0]
                key = search_key
                found = True
                break
        if not found and 'downwards' in conb:
            dkey = conb['downwards']
            if dkey in gd:
                dval = gd[dkey]
                if isinstance(dval, int) and dval in sent_data:
                    new_gd = sent_data[dval]['govern_dict']
                    for try_key in (obl_prep, alt_prep):
                        if try_key in new_gd:
                            new_o = _s_o_formation(new_gd[try_key], sent_data)[0]
                            found = True
                            break
            key = dkey
    return new_v, new_o, key


def _linking_verb_LVC_extraction(token, gov_dict, sent_data, linking_verb_LVC_json):
    """Extract LVCs starting with a linking verb (e.g. 'be responsible for')."""
    s, v, o = '', '', ''
    negation = _negation_detect(token, sent_data)
    lemma = token['lemma']
    if lemma not in linking_verb_LVC_json:
        return s, v, o, negation
    for conb in linking_verb_LVC_json[lemma]:
        start_idx = end_idx = token['id']
        matched = True
        for key in conb:
            if key == 'prep':
                continue
            dep = conb[key]
            if dep not in gov_dict or isinstance(gov_dict[dep], list):
                matched = False
                break
            negation = negation or _content_negation(gov_dict[dep], sent_data)
            current = sent_data[gov_dict[dep]]
            if current['lemma'] != key:
                matched = False
                break
            start_idx = min(start_idx, current['id'])
            end_idx = max(end_idx, current['id'])
        if not matched:
            continue
        if 'prep' in conb:
            for prep_dep in conb['prep']:
                if prep_dep in gov_dict:
                    for i in range(start_idx, end_idx + 1):
                        if i in sent_data:
                            v += sent_data[i]['word'] + ' '
                    v += prep_dep.split(':')[1] if ':' in prep_dep else prep_dep
                    o = _s_o_formation(gov_dict[prep_dep], sent_data)[0]
                    negation = negation or _content_negation(gov_dict[prep_dep], sent_data)
                    if 'nsubj' in gov_dict:
                        s = _s_o_formation(gov_dict['nsubj'], sent_data)[0]
                        negation = negation or _content_negation(gov_dict['nsubj'], sent_data)
                    break
    return s, v, o, negation


def _pred_root(token, gov_dict, sent_data):
    """Extract subject–linking verb–predicative nominative."""
    s = 'Inferred_Subject_Passive'
    v, o = '', ''
    negation = _negation_detect(token, sent_data)
    if 'nsubj' in gov_dict:
        s = _s_o_formation(gov_dict['nsubj'], sent_data)[0]
        negation = negation or _content_negation(gov_dict['nsubj'], sent_data)
    if 'cop' in gov_dict:
        v = _token_connect(gov_dict['cop'], sent_data) + ' ' + v
        negation = negation or _content_negation(gov_dict['cop'], sent_data)
    if 'aux' in gov_dict and v:
        v = _token_connect(gov_dict['aux'], sent_data) + ' ' + v
        negation = negation or _content_negation(gov_dict['aux'], sent_data)
    o = token['word']
    if 'case' in gov_dict and v:
        v = v + ' ' + _token_connect(gov_dict['case'], sent_data)
    return s, v, o, negation


# ── Single-verb SVO building ─────────────────────────────────────

def _verb_root_svo_building(verb_id, sent_data, v_obj_obl_json, v_prep_json):
    """Extract S, V, O for a single verb token."""
    s = 'Inferred_Subject_Passive'
    o = ''
    s_idx = -1
    o_idx = -1
    vtoken = sent_data[verb_id]
    v_string = vtoken['word']
    v_lemma = vtoken['lemma']
    vgd = vtoken['govern_dict']

    negation = _negation_detect(vtoken, sent_data)

    # Phrasal verbs: compound:prt
    if 'compound:prt' in vgd:
        v_string += ' ' + _token_connect(vgd['compound:prt'], sent_data)

    # ── Subject extraction ──
    s_dep = ''
    if 'nsubj' in vgd:
        s, s_idx = _s_o_formation(vgd['nsubj'], sent_data)
        s_dep = 'nsubj'
    elif 'obl:agent' in vgd:
        s, s_idx = _s_o_formation(vgd['obl:agent'], sent_data)
        s_dep = 'obl:agent'
    elif 'nsubj:xsubj' in vgd:
        s, s_idx = _s_o_formation(vgd['nsubj:xsubj'], sent_data)
        s_dep = 'nsubj:xsubj'

    if s_dep:
        negation = negation or _content_negation(vgd[s_dep], sent_data)

    # ── Object extraction ──
    o_dep = ''
    if 'nsubj:pass' in vgd:
        o_dep = 'nsubj:pass'
        o, o_idx = _s_o_formation(vgd['nsubj:pass'], sent_data)
    elif 'iobj' in vgd:
        o_dep = 'iobj'
        o, o_idx = _s_o_formation(vgd['iobj'], sent_data)
    elif 'obj' in vgd:
        new_v, new_o, new_o_dep = _verb_obj_obl(vtoken, sent_data, v_obj_obl_json)
        if new_v:
            v_string = new_v
            o = new_o
            o_dep = new_o_dep
        else:
            o_dep = 'obj'
            o, o_idx = _s_o_formation(vgd['obj'], sent_data)
    else:
        # Object via preposition (obl:*)
        obl_preps = [k for k in vgd if k.startswith('obl:')
                     and k[4:] not in ('tmod', 'agent', 'by')]
        if len(obl_preps) == 1:
            o_dep = obl_preps[0]
            o, o_idx = _s_o_formation(vgd[obl_preps[0]], sent_data)
            v_string += ' ' + obl_preps[0][4:].replace('_', ' ')
        elif len(obl_preps) > 1:
            for oblp in obl_preps:
                prep = oblp[4:]
                if prep in v_prep_json and v_lemma.lower() in v_prep_json[prep]:
                    o_dep = oblp
                    o, o_idx = _s_o_formation(vgd[oblp], sent_data)
                    v_string += ' ' + prep
                    break
            if not o_dep:
                for oblp in obl_preps:
                    if '_' in oblp[4:]:
                        o_dep = oblp
                        o, o_idx = _s_o_formation(vgd[oblp], sent_data)
                        v_string += ' ' + oblp[4:].replace('_', ' ')
                        break

    if o_dep:
        negation = negation or _content_negation(vgd.get(o_dep, []), sent_data) if o_dep in vgd else negation

    return s, v_string, o, negation, o_idx


# ── Adverbial / clausal modifiers ────────────────────────────────

def _advcl_extraction(token, sent_data, p_s, p_o, v_obj_obl_json, v_prep_json):
    """Recursively extract SVO from adverbial clause modifiers."""
    result = []
    negation_result = []
    gd = token['govern_dict']
    for dep in list(gd.keys()):
        if 'advcl' in dep or 'xcomp' in dep or dep == 'dep':
            advcl_ids = gd[dep] if isinstance(gd[dep], list) else [gd[dep]]
            for idx in advcl_ids:
                advcl_token = sent_data[idx]
                if 'VB' not in advcl_token['pos'] and advcl_token['upos'] != 'VERB':
                    continue
                s, v, o, neg, o_idx = _verb_root_svo_building(idx, sent_data, v_obj_obl_json, v_prep_json)
                # Passive advcl: parent subject becomes default object
                if advcl_token['pos'] in ('VBN',) and o == '':
                    o = p_s
                elif s == 'Inferred_Subject_Passive':
                    s = p_s
                result.append([s, v, o])
                negation_result.append(neg)
                # Recurse
                sub_r, sub_n = _advcl_extraction(advcl_token, sent_data, s, o, v_obj_obl_json, v_prep_json)
                result.extend(sub_r)
                negation_result.extend(sub_n)
    return result, negation_result


# ── Conjunct verb processing ─────────────────────────────────────

def _verb_root(verb_list, conj_word, token, sent_data, v_obj_obl_json, v_prep_json):
    """Extract SVO for a verb and its conjuncts (shared arguments)."""
    svo = []
    negation_list = []
    s_set = False
    o_set = False
    o_share_idx = -1
    s_share = 'Inferred_Subject_Passive'
    o_share = ''
    for verb_id in verb_list:
        s, v, o, negation, o_idx = _verb_root_svo_building(verb_id, sent_data, v_obj_obl_json, v_prep_json)
        if verb_id > o_share_idx:
            o_set = False
        if negation_list and negation_list[0] and conj_word == 'or':
            negation = True
        if not s_set and s != 'Inferred_Subject_Passive':
            s_set = True
            s_share = s
        if not o_set and o != '':
            o_set = True
            o_share = o
            o_share_idx = o_idx
        if s == 'Inferred_Subject_Passive':
            s = s_share
        if o == '' and verb_id < o_share_idx:
            o = o_share
        negation_list.append(negation)
        svo.append([s, v, o])
        # Extract adverbial clause modifiers
        vtok = sent_data[verb_id]
        advcl_svo, advcl_neg = _advcl_extraction(vtok, sent_data, s, o, v_obj_obl_json, v_prep_json)
        svo.extend(advcl_svo)
        negation_list.extend(advcl_neg)
    return svo, negation_list


# ── MWE replacement (multi-word entity names) ────────────────────

def _replace_words_with_full_names(sentence, full_names):
    """Replace single tokens with full NER names (e.g. 'shek' → 'Chiang Kai-shek')."""
    if not full_names:
        return sentence
    words = sentence.split()
    available = full_names.copy()
    result = []
    for word in words:
        replaced = False
        for name in available:
            if word in str(name.split()):
                result.append(name)
                available.remove(name)
                replaced = True
                break
        if not replaced:
            result.append(word)
    return ' '.join(result)


# ── NER extraction from Stanza entities ──────────────────────────

def _extract_ner_entities(sentence):
    """Extract location, person, organization, time entities from a Stanza sentence."""
    locations, persons, organizations = [], [], []
    loc_ner, per_ner, org_ner = [], [], []
    # Use sentence.entities if available (Stanza NER)
    if hasattr(sentence, 'entities'):
        for ent in sentence.entities:
            # Stanza emits GPE (en/zh), LOC (most languages), LOCATION (vi) for places;
            # the CoreNLP-style CITY/COUNTRY/STATE_OR_PROVINCE tags are never produced by Stanza
            if ent.type in ('GPE', 'LOC', 'LOCATION'):
                if ent.text not in locations:
                    locations.append(ent.text)
                    loc_ner.append([ent.text, ent.type, ent.start_char, ent.end_char])
            elif ent.type == 'PERSON':
                if ent.text not in persons:
                    persons.append(ent.text)
                    per_ner.append([ent.text, ent.type, ent.start_char, ent.end_char])
            elif ent.type in ('ORG', 'ORGANIZATION'):
                if ent.text not in organizations:
                    organizations.append(ent.text)
                    org_ner.append([ent.text, ent.type, ent.start_char, ent.end_char])
    return locations, persons, organizations, loc_ner, per_ner, org_ner


# ── Main SVO extraction function (enhanced) ──────────────────────

def extractSVO(doc, docID, inputFilename, inputDir, tail, filename_embeds_date_var, NER_available):
    """Enhanced SVO extraction from a Stanza document.

    Mirrors the logic of Stanford_CoreNLP_SVO_enhanced_dependencies_util:
      - Negation detection (recursive)
      - Conjunction handling (shared S/O across conjunct verbs)
      - Phrasal verbs (compound:prt)
      - Light verb constructions (3 LVC dictionaries)
      - Relative/adverbial clause recursion
      - Copular/predicative nominative constructions
      - Oblique objects with preposition disambiguation
      - MWE name replacement from NER
    """
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # Load LVC dictionaries (same ones used by CoreNLP SVO)
    v_obj_obl_json = _load_lvc_json('LVC_verb_obj_obl_json.txt')
    v_prep_json = _load_lvc_json('verb_prep_json.txt')
    linking_verb_LVC_json = _load_lvc_json('linking_verb_LVC_json.txt')

    # Output columns
    base_cols = ['Subject (S)', 'Verb (V)', 'Object (O)', 'Negation',
                 'Location', 'Location_NER', 'Person', 'Organization', 'Time',
                 'Sentence ID', 'Sentence', 'Document ID', 'Document']
    if filename_embeds_date_var:
        base_cols.append('Date')

    rows = []

    for sent_idx, sentence in enumerate(doc.sentences):
        # Build CoreNLP-style govern_dict from Stanza deps
        sent_data = _build_govern_dict(sentence)

        # Extract NER entities for this sentence
        locations, persons, organizations = [], [], []
        if NER_available:
            locations, persons, organizations, loc_ner, per_ner, org_ner = _extract_ner_entities(sentence)

        # Collect NER text for columns
        loc_str = '; '.join(locations) if locations else ''
        # Build NER type mapping: location text -> NER type
        loc_ner_map = {item[0]: item[1] for item in loc_ner}
        loc_ner_types = [loc_ner_map.get(loc, 'LOCATION') for loc in locations]
        loc_ner_str = '; '.join(loc_ner_types) if loc_ner_types else ''

        per_str = '; '.join(persons) if persons else ''
        org_str = '; '.join(organizations) if organizations else ''
        time_words = []
        for wid in sent_data:
            tok = sent_data[wid]
            if tok['ner'] in ('TIME', 'DATE', 'S-TIME', 'B-TIME', 'I-TIME', 'E-TIME',
                              'S-DATE', 'B-DATE', 'I-DATE', 'E-DATE'):
                time_words.append(tok['word'])
        time_str = '; '.join(time_words) if time_words else ''

        collected_verbs = []
        SVO = []
        N = []

        for wid in sent_data:
            token = sent_data[wid]
            gd = token['govern_dict']
            pos = token['pos']
            upos = token['upos']
            deprel = token['deprel']

            # ── Process verbs (skip advcl/xcomp/acl — handled recursively) ──
            is_verb = 'VB' in pos or upos == 'VERB'
            is_special_dep = any(x in deprel for x in ('advcl', 'xcomp', 'acl')) or deprel == 'dep'

            if is_verb and not is_special_dep and wid not in collected_verbs:
                verb_list, conj_word = _verb_index_conj(wid, token, gd, sent_data)
                collected_verbs.extend(verb_list)
                svo_list, neg_list = _verb_root(verb_list, conj_word, token, sent_data,
                                                v_obj_obl_json, v_prep_json)
                for i, triple in enumerate(svo_list):
                    s, v, o = triple
                    if s != 'Inferred_Subject_Passive' or o != '':
                        SVO.append([s, v, o])
                        N.append(neg_list[i])

            elif not is_verb:
                # ── Linking verb LVC ──
                s, v, o, neg = _linking_verb_LVC_extraction(token, gd, sent_data, linking_verb_LVC_json)
                if v and (s != 'Inferred_Subject_Passive' or o != ''):
                    if [s, v, o] not in SVO:
                        SVO.append([s, v, o])
                        N.append(neg)
                # ── Predicative nominative ──
                elif deprel in ('root', 'parataxis', 'ROOT') and \
                        ('NN' in pos or pos == 'PRP' or upos == 'NOUN' or upos == 'PRON'):
                    s, v, o, neg = _pred_root(token, gd, sent_data)
                    if v and (s != 'Inferred_Subject_Passive' or o != ''):
                        if [s, v, o] not in SVO:
                            SVO.append([s, v, o])
                            N.append(neg)

            # ── Clausal modifier (acl / acl:relcl) ──
            acl_key = ''
            if 'acl' in gd:
                acl_key = 'acl'
            elif 'acl:relcl' in gd:
                acl_key = 'acl:relcl'
            elif 'dep' in gd:
                acl_key = 'dep'
            if acl_key:
                acl_ids = gd[acl_key] if isinstance(gd[acl_key], list) else [gd[acl_key]]
                for v_id in acl_ids:
                    vtok = sent_data[v_id]
                    if 'VB' in vtok['pos'] or vtok['upos'] == 'VERB':
                        collected_verbs.append(v_id)
                        acl_svo, acl_neg = _verb_root([v_id], '', vtok, sent_data,
                                                       v_obj_obl_json, v_prep_json)
                        if acl_svo and acl_svo[0][0] == 'Inferred_Subject_Passive':
                            acl_svo[0][0] = token['word']
                        SVO.extend(acl_svo)
                        N.extend(acl_neg)

        # ── MWE name replacement ──
        for idx, triple in enumerate(SVO):
            SVO[idx][0] = _replace_words_with_full_names(triple[0], persons)
            SVO[idx][0] = _replace_words_with_full_names(SVO[idx][0], organizations)
            SVO[idx][0] = _replace_words_with_full_names(SVO[idx][0], locations)
            SVO[idx][2] = _replace_words_with_full_names(triple[2], persons)
            SVO[idx][2] = _replace_words_with_full_names(SVO[idx][2], organizations)
            SVO[idx][2] = _replace_words_with_full_names(SVO[idx][2], locations)

        # ── Build output rows ──
        for i, triple in enumerate(SVO):
            row = {
                'Subject (S)': triple[0] if triple[0] != 'Inferred_Subject_Passive' else '?',
                'Verb (V)': triple[1],
                'Object (O)': triple[2],
                'Negation': N[i] if i < len(N) else False,
                'Location': loc_str,
                'Location_NER': loc_ner_str,
                'Person': per_str,
                'Organization': org_str,
                'Time': time_str,
                'Sentence ID': sent_idx + 1,
                'Sentence': sentence.text,
                'Document ID': docID,
                'Document': IO_csv_util.dressFilenameForCSVHyperlink(inputFilename),
            }
            if filename_embeds_date_var:
                row['Date'] = date_str
            rows.append(row)

    svo_df = pd.DataFrame(rows, columns=base_cols)
    # Drop rows with empty verbs
    svo_df = svo_df[svo_df['Verb (V)'].str.strip() != '']
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
        out_df = pd.concat([out_df, temp_svo], ignore_index=True)

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

# ─────────────────────────────────────────────────────────────────────
# Stanza Coreference Resolution
# Requires Stanza >= 1.7.0 (coref processor)
# ─────────────────────────────────────────────────────────────────────

# Pronouns handled (same set as CoreNLP coref in NLP Suite):
#   nominative: I, you, he, she, it, we, they
#   possessive: my, mine, our, ours, his, her, hers, their, its, yours
#   objective:  me, you, him, her, it, them
#   reflexive:  myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves

_PRONOUNS = {
    # nominative
    'i', 'you', 'he', 'she', 'it', 'we', 'they',
    # possessive
    'my', 'mine', 'our', 'ours', 'his', 'her', 'hers', 'their', 'theirs', 'its', 'yours',
    # objective
    'me', 'him', 'them',
    # reflexive
    'myself', 'yourself', 'himself', 'herself', 'oneself', 'itself',
    'ourselves', 'yourselves', 'themselves',
}


def _check_coref_available():
    """Return True if the installed Stanza version supports the coref processor."""
    import stanza
    major, minor = 0, 0
    try:
        parts = stanza.__version__.split('.')
        major, minor = int(parts[0]), int(parts[1])
    except Exception:
        pass
    if major < 1 or (major == 1 and minor < 7):
        mb.showerror(title='Stanza version too old',
                     message='Stanza coreference resolution requires Stanza 1.7.0 or later.\n\n'
                             'Your installed version is ' + stanza.__version__ + '.\n\n'
                             'To upgrade, open a terminal and run:\n'
                             '   conda activate NLP\n'
                             '   pip install --upgrade stanza')
        return False
    return True


def Stanza_coref(config_filename, inputFilename, inputDir, outputDir,
                 openOutputFiles, chartPackage, dataTransformation,
                 language_var, manual_Coref):
    """
    Run Stanza coreference resolution on input txt file(s).

    Returns (corefed_files, errorFound) to match the signature expected
    by coreference_main.run().

    For each input txt file the function produces:
      1.  A coreferenced txt file with pronouns replaced by their referent.
      2.  A coref_table csv with antecedent–referent pairs.

    If manual_Coref is True, the CoreNLP split-screen editor is reused
    for manual editing (single-file input only).
    """
    if not _check_coref_available():
        return [], True

    corefed_files = []
    errorFound = False

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir,
                                          fileType='.txt', silent=False,
                                          configFileName=config_filename)
    if len(inputDocs) == 0:
        return [], True

    # Determine language code
    short_lang_list, long_lang_list = get_language_list([language_var])
    if len(short_lang_list) == 0:
        mb.showerror(title='Language error',
                     message='The selected language "' + language_var +
                             '" is not supported by Stanza.\n\nPlease check your language settings.')
        return [], True
    short_lang = short_lang_list[0]

    # Currently Stanza coref is only available for English
    if short_lang != 'en':
        mb.showwarning(title='Language not supported',
                       message='Stanza coreference resolution is currently available only for English.\n\n'
                               'The selected language is ' + language_var + '.')
        return [], True

    # Build output subdirectory
    if inputFilename != '':
        inputBaseName = os.path.basename(inputFilename)[0:-4]
    else:
        inputBaseName = os.path.basename(inputDir)
    outputCorefDir = os.path.join(outputDir, 'coref_Stanza_' + inputBaseName)
    outputCorefedDir = IO_files_util.make_output_subdirectory('', '', outputCorefDir, '', silent=False)
    if outputCorefedDir == '':
        return [], True

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running Stanza coreference resolution at', True, '', True, '', False)

    # Build pipeline with coref
    try:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,coref', verbose=False)
    except Exception as e:
        mb.showerror(title='Stanza coref pipeline error',
                     message='Failed to create the Stanza coreference pipeline.\n\n' + str(e))
        return [], True

    # Coref table rows: [Pronoun, Referent, Sentence ID, Sentence, Document ID, Document]
    coref_rows = []

    nDocs = len(inputDocs)
    for docID, doc_path in enumerate(inputDocs, 1):
        head, tail = os.path.split(doc_path)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)

        text = open(doc_path, 'r', encoding='utf-8', errors='ignore').read()
        if text.strip() == '':
            print("  Skipping empty file: " + tail)
            continue

        try:
            doc = nlp(text)
        except Exception as e:
            print("  Error processing " + tail + ": " + str(e))
            errorFound = True
            continue

        # ── Build coreferenced text ──────────────────────────────
        # Collect pronoun → referent replacements from coref chains
        # Each chain: list of mentions; the first mention with a non-pronoun
        # head is the canonical referent.
        replacements = {}  # token key (sent_idx, word_idx) → replacement string

        if hasattr(doc, 'coref') and doc.coref is not None:
            for chain in doc.coref:
                # Find the canonical (non-pronoun) mention
                canonical = None
                for mention in chain.mentions:
                    # CorefMention has start_word, end_word, sentence (indices)
                    sent = doc.sentences[mention.sentence]
                    mention_text = ' '.join(
                        w.text for w in sent.words[mention.start_word:mention.end_word])
                    if mention_text and mention_text.lower() not in _PRONOUNS:
                        canonical = mention_text
                        break
                if canonical is None:
                    continue  # all mentions are pronouns; nothing to resolve

                # Mark each pronoun mention for replacement
                for mention in chain.mentions:
                    sent = doc.sentences[mention.sentence]
                    mention_text = ' '.join(
                        w.text for w in sent.words[mention.start_word:mention.end_word])
                    if mention_text and mention_text.lower() in _PRONOUNS:
                        # Record for coref table
                        sent_idx = mention.sentence
                        sent_text = sent.text
                        coref_rows.append([mention_text, canonical,
                                           sent_idx + 1, sent_text,
                                           docID, doc_path])

                        # Collect token-level replacements
                        for wi in range(mention.start_word, mention.end_word):
                            replacements[(sent_idx, wi)] = \
                                (canonical if wi == mention.start_word else '')

        # Reconstruct text with replacements
        corefed_tokens = []
        for si, sent in enumerate(doc.sentences):
            sent_tokens = []
            for wi, word in enumerate(sent.words):
                key = (si, wi)
                if key in replacements:
                    rep = replacements[key]
                    if rep:  # first token of replaced mention
                        sent_tokens.append(rep)
                    # else: subsequent tokens of multi-word pronoun mention → skip
                else:
                    sent_tokens.append(word.text)
            corefed_tokens.append(' '.join(sent_tokens))
        corefed_text = ' '.join(corefed_tokens)

        # Save coreferenced txt file
        corefed_filename = os.path.join(outputCorefedDir, tail)
        with open(corefed_filename, 'w', encoding='utf-8') as f:
            f.write(corefed_text)
        corefed_files.append(corefed_filename)

    # Save coref table csv
    if len(coref_rows) > 0:
        coref_table_filename = os.path.join(outputCorefedDir, 'coref_table_Stanza.csv')
        coref_df = pd.DataFrame(coref_rows,
                                columns=['Pronoun (antecedent)', 'Referent',
                                         'Sentence ID', 'Sentence',
                                         'Document ID', 'Document'])
        coref_df.to_csv(coref_table_filename, index=False, encoding='utf-8')
        corefed_files.append(coref_table_filename)

    IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis end',
        'Finished running Stanza coreference resolution at', True, '', True, startTime, False)

    # Manual editing (reuse CoreNLP split-screen editor)
    if manual_Coref:
        if len(inputDir) == 0 and len(inputFilename) > 0:
            import Stanford_CoreNLP_coreference_util
            for file in corefed_files:
                if file.endswith('.txt'):
                    Stanford_CoreNLP_coreference_util.manualCoref(inputFilename, file, file)
        else:
            IO_user_interface_util.timed_alert(
                GUI_util.window, 2000, 'Feature Not Available',
                'Manual coreference is only available when processing a single file, not an input directory.')

    return corefed_files, errorFound


# create locations file for GIS
def visualize_GIS_maps_Stanza(svo_df):
    # carry the Date (extracted from the filename during SVO extraction) into the location file
    # so the geocoder/KML/folium popups can show it (CoNLL_checker keys datePresent on a 'Date' column)
    has_date = 'Date' in svo_df.columns
    cols = ['Location', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
    if has_date:
        cols.append('Date')
    loc_df = pd.DataFrame(columns=cols)
    for _,row in svo_df.iterrows():
        if isinstance(row['Location'], str):
            loc_list = row['Location'].split(';')
            ner_list = row.get('Location_NER', '').split(';') if isinstance(row.get('Location_NER'), str) else []
            for idx, loc in enumerate(loc_list):
                if loc.strip() != '':
                    ner_type = ner_list[idx].strip() if idx < len(ner_list) else 'LOCATION'
                    # Geocode geopolitical entities (GPE = countries/cities/states); skip generic LOC (mountains, rivers)
                    if ner_type == 'GPE':
                        rowvals = [loc.strip(), ner_type, row['Sentence ID'], row['Sentence'], row['Document ID'], row['Document']]
                        if has_date:
                            rowvals.append(row.get('Date', ''))
                        loc_df.loc[len(loc_df.index)] = rowvals
    return loc_df

# keep only NER rows whose tag is in the user-selected set.
# Stanza stores tags in BIOES form (e.g. 'S-GPE', 'B-PERSON', 'O'); we match on the
# tag portion after the prefix. If the selection covers the full tag set (or is
# empty/unparseable), the dataframe is returned unchanged.
def filter_NER_output_by_tags(df, NERs, short_lang='en'):
    if df is None or len(df) == 0 or 'NER' not in df.columns:
        return df
    selected = {t.strip() for t in str(NERs).replace(',', ' ').split() if t.strip() and '---' not in t}
    if not selected:
        return df
    full_set = set(NER_dict.get(short_lang, []))
    if full_set and selected >= full_set:  # all tags selected -> no filtering
        return df
    def _tag(ner):
        ner = str(ner)
        if ner in ('', 'O', 'None', 'nan'):
            return ''
        return ner.split('-')[-1]
    return df[df['NER'].apply(_tag).isin(selected)].reset_index(drop=True)

# modified from StanfordCoreNLP_util
def create_output_directory(inputFilename, inputDir, outputDir,
                            annotator):
    outputDirSV=GUI_util.output_dir_path.get()
    if 'parse' in annotator:
        annotator_label = 'parser (dep)'
    else:
        annotator_label = annotator
    if outputDirSV != outputDir:
        # create output subdirectory
        outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                           label=annotator_label,
                                                           silent=True)
    else:
        outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                           label=annotator_label + "_Stanza",
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
    "zh", # has an alias called zh-hans
    "zh-hans", # has an alias called zh-hans
    # "zh-hant", traditional_chinese has hardly any processes
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

available_mwt = [
    "ar",
    "ca",
    "cop",
    "cs",
    "de"
    "en",
    "es",
    "fa",
    "fi",
    "fr",
    "gl",
    "he",
    "hy",
    "it",
    "kk",
    "mr",
    "pl",
    "pt",
    "ta",
    "tr",
    "uk",
    "wo"
]
available_sentiment = [
    "de",
    "en",
    "zh",
    "zh-hans"
]

# Languages with constituency parsing models in Stanza
# https://stanfordnlp.github.io/stanza/constituency.html
available_constituency = [
    "da",
    "de",
    "en",
    "es",
    "fr",
    "it",
    "ja",
    "nb",
    "pt",
    "tr",
    "vi",
    "zh",
    "zh-hans",
]

available_NER = [
    "af",
    "ar",
    "bg",
    "zh",
    "zh-hans",
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
# zh-hans has an alias called zh; same thing
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
