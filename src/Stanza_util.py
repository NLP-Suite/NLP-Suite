import stanza
from stanza.pipeline.multilingual import MultilingualPipeline
import pandas as pd
import tkinter.messagebox as mb
import os
import re
import warnings
import tkinter as tk

from tenacity import retry_unless_exception_type

import IO_files_util
import IO_csv_util
import charts_util
import file_splitter_ByLength_util
import GUI_util
import GUI_IO_util
import IO_user_interface_util
import constants_util

warnings.simplefilter(action='ignore', category=FutureWarning)

# Stanza annotate functions
def Stanza_annotate(config_filename, inputFilename, inputDir,
                    outputDir,
                    openOutputFiles, createCharts, chartPackage,
                    annotator_params,
                    DoCleanXML,
                    language,
                    memory_var,
                    document_length=90000,
                    sentence_length=1000,
                    print_json = True,
                    **kwargs):

    language_encoding = 'utf-8'
    filesToOpen = []

    output_format_option = {
        'DepRel': ["ID", "Form", "Head", "DepRel", "Record ID", "Sentence ID", "Document ID", "Document"],
    }
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running Stanza at',
                                            True, '', True, '', False)

    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # annotating each input file
    docID=0
    recordID = 0
    filesError=[]
    # json = True
    errorFound=False
    total_length = 0
    # record the time consumption before annotating text in each file
    processing_doc = ''

    # check if selected language is one.
    if len(language) == 1 and language[0] != 'multilingual':
        lang = ''
        lang_list = []
        for k,v in lang_dict.items():
            if v == language[0]:
                lang = k
                lang_list.append(lang)
                break
        # check if allowed combinations of annotator and language is available in Stanza
        for annotator in annotator_params:
            if (lang not in available_NER and annotator=='NER') \
                or (lang not in available_ud and annotator=='depparse')\
                    or (lang not in available_sentiment and annotator=='sentiment'):
                mb.showerror("Warning",
                            "Stanza does not currently support the " + annotator + " annotator for " + language[0] + ".\n\nPlease, select a different annotator or a different language.")
                return filesToOpen
            # routine = routine_option.get(annotator)
            # elif lang == ""
            # output_format = output_format_option.get(annotator)

        # test if the selected language model is already downloaded, if not, download
        # IMPORTANT: no need to manually download language package after Stanza v1.4.0,
        #            if Stanza gives error for downloading, check the current version of Stanza
        nlp = stanza.Pipeline(lang=lang, processors='tokenize', verbose=False)


        if "Lemma"  in annotator_params:
            processors='tokenize,lemma'
        elif "NER" in annotator_params:
            processors='tokenize,ner'
        elif "All POS" in annotator_params:
            processors='tokenize,pos'
        elif "depparse" in annotator_params:
            processors='tokenize,mwt,pos,lemma,depparse'
        elif "sentiment" in annotator_params:
            processors='tokenize,sentiment'

        nlp = stanza.Pipeline(lang=lang, processors=processors, verbose=False)

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
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'Stanza_' + annotator_params)
    for docName in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(docName)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        docTitle = os.path.basename(docName)
        sentenceID = 0
        # if ("SVO" in annotator_params or "OpenIE" in annotator_params) and "coref" in docName.split("_"):
        #     split_file = file_splitter_merged_txt_util.run(docName, "<@#", "#@>", outputDir)
        #     if len(split_file)>1:
        #         split_file = IO_files_util.getFileList("", split_file[0], fileType=".txt")
        if "Sentence" in annotator_params:
            split_file = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,config_filename,docName,'',document_length)
        else:
            split_file = []
            split_file.append(docName)

        nSplitDocs = len(split_file)
        split_docID = 0

        for doc in split_file:
            split_docID = split_docID + 1
            head, tail = os.path.split(doc)

            if docName != doc:
                print("   Processing split file " + str(split_docID) + "/" + str(nSplitDocs) + ' ' + tail)

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

            temp_df = convertStanzaDoctoDf(Stanza_output, inputFilename, inputDir, tail, docID, annotator_params, lang_list)
            df = pd.concat([df, temp_df], ignore_index=True, axis=0)

    df.to_csv(outputFilename, index=False, encoding = language_encoding)
    filesToOpen.append(outputFilename)

    # Filter + Visualization.
    language_list=IO_csv_util.get_csv_field_values(outputFilename, 'Language')
    if len(language_list)>1:
        # callback function for dropdown_menu_widget2()
        def callback(selected_language: str):
            return
        # open the drop down menu to filter the original output with selected language
        selected_language = GUI_IO_util.dropdown_menu_widget2(GUI_util.window,
                                                    "Please, select the language you wish to use for your charts (dropdown menu on the right; press OK to accept selection; press ESCape to process all languages).",
                                                    language_list, 'Stanza languages', callback)
        # filter with selected language (using Pandas dataframe)
        selected_lang_df = df.loc[df['Language']==selected_language]
        selected_lang_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                            'Stanza_' + f'{selected_language}' + '_' + annotator_params)
        selected_lang_df.to_csv(selected_lang_outputFilename, index=False, encoding = language_encoding)
        filesToOpen.extend(selected_lang_outputFilename)
    if "Lemma" in str(annotator_params) and 'Lemma' in outputFilename:
        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted=['Form'],
                                                           chartTitle='Frequency Distribution of Form Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='Form',  # 'POS_bar',
                                                           column_xAxis_label='Form values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Form Values')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

        chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                           outputDir,
                                                           columns_to_be_plotted=['Lemma'],
                                                           chartTitle='Frequency Distribution of Lemma Values',
                                                           # count_var = 1 for columns of alphabetic values
                                                           count_var=1, hover_label=[],
                                                           outputFileNameType='Lemma',  # 'POS_bar',
                                                           column_xAxis_label='Lemma values',
                                                           groupByList=['Document ID', 'Document'],
                                                           plotList=['Frequency'],
                                                           chart_title_label='Lemma Values')

        if chart_outputFilename != None:
            if len(chart_outputFilename) > 0:
                filesToOpen.extend(chart_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Stanza ' + str(annotator_params) + ' annotator at', True, '', True, startTime, False)

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
    if len(language) > 1 or language[0]=='multilingual':
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
                if annotator_params=='sentiment':
                    temp_df['sentiment_score'] = sentiment_dictionary[i]
                out_df = out_df.append(temp_df)

    # Stanza doc to Pandas DataFrame conversion logic for single language annotation
    else:
        # check if the annotator is sentiment
        if annotator_params=='sentiment':
            sentiment_dictionary = {}
            for i, sentence in enumerate(stanza_doc.sentences):
                sentiment_dictionary[i] = sentence.sentiment

        dicts = stanza_doc.to_dict()
        for i in range(len(dicts)):
            temp_df = pd.DataFrame.from_dict(dicts[i])
            if annotator_params=='sentiment':
                temp_df['sentiment_score'] = sentiment_dictionary[i]
            out_df = out_df.append(temp_df)

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
            'id':'ID',
            'text':'Form',
            'lemma':'Lemma',
            'upos':'POStag',
            'head':'Head',
            'deprel':'DepRel',
            'ner':'NER',
            'lang':'Language',
            'sentiment_score':'Sentiment score'
        }
    )
    out_df['Record ID'] = None
    out_df['Sentence ID'] = None
    out_df['Document ID'] = docID
    out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    i = 0
    sidx = 1
    for row in out_df.iterrows():
        if i != 0 and row[1]['ID'] == 1 :
            sidx+=1

        out_df.at[i, 'Record ID'] = row[1]['ID']
        out_df.at[i, 'Sentence ID'] = sidx

        i+=1

    if 'Language' in out_df.columns:
        out_df = out_df[ [ col for col in out_df.columns if col != 'Language' ] + ['Language'] ]
        for idx in range(len(out_df)):
            temp_lang = out_df.at[idx, 'Language']
            out_df.at[idx, 'Language'] = lang_dict[temp_lang]
    print('')

    return out_df

# Python dictionary of language (values) and their acronyms (keys)
lang_dict  = dict(constants_util.languages)

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
