import stanza
import pandas as pd
import tkinter.messagebox as mb
import os

import IO_files_util
import IO_csv_util
import file_splitter_merged_txt_util
import file_splitter_ByLength_util
import GUI_util
import IO_user_interface_util
import constants_util

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
    for k,v in lang_dict.items():
        if v == language:
            lang = k
            break
    for annotator in annotator_params:
        # TODO MINO must expand the check for the allowed combinations of annotator and language
        if (lang not in available_NER and annotator=='NER') \
            or (lang not in available_ud and annotator=='depparse')\
                or (lang not in available_sentiment and annotator=='sentiment'):
            mb.showinfo("Warning",
                        "Stanza does not currently support the " + annotator + " annotator for " + language + ".\n\nPlease, select a different annotator or a different language.")
            return filesToOpen
        # routine = routine_option.get(annotator)
        output_format = output_format_option.get(annotator)

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

    # test if the selected language model is already downloaded, if not, download
    try:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize', verbose=False)
    except:
        stanza.download(lang)

    if "Lemma"  in annotator_params:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,lemma', verbose=False)
    elif "NER" in annotator_params:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,ner',  verbose=False)
    elif "All POS" in annotator_params:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,pos', verbose=False)
    # elif "sentiment" in annotator_params:
    #     nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')
    elif "depparse" in annotator_params:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,mwt,pos,lemma,depparse', verbose=False)
    elif "sentiment" in annotator_params:
        # print("$$\__**^_^**__/$$ testing sentiment analysis $$\__**^_^**__/$$")
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,sentiment')

    df = pd.DataFrame()
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'Stanza_' + 'DepRel' + '_' + annotator_params)                                                
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

            text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")
            
            if "%" in text:
                text=text.replace("%","percent")

            Stanza_output = nlp(text)

            temp_df = convertStanzaDoctoDf(Stanza_output, inputFilename, inputDir, tail, docID, annotator_params)
            df = pd.concat([df, temp_df], ignore_index=True, axis=0)
            # df = df.reset_index(drop=True)
    
    df.to_csv(outputFilename, index=False, encoding = language_encoding)
    filesToOpen.append(outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Stanza ' + str(annotator_params) + ' annotator at', True, '', True, startTime, False)

    return filesToOpen

# Convert Stanza doc to pandas Dataframe
def convertStanzaDoctoDf(stanza_doc, inputFilename, inputDir, tail, docID, annotator_params):
    out_df = pd.DataFrame()

    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + tail
    
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

    out_df = out_df.drop(
        ['xpos', 'start_char', 'end_char', 'multi_ner', 'feats'],
        axis=1,
        errors='ignore'
        )
    out_df = out_df.reset_index(drop=True)
    
    if annotator_params == 'depparse':
        out_df.columns = [ 
            "ID",
            "Form",
            # "Lemma",
            "POStag",
            "Head",
            "DepRel",
            "NER",
                        ]
    elif annotator_params == 'Lemma':
        out_df.columns = [ 
            "ID",
            "Form",
            "Lemma",
                        ]
    elif annotator_params == 'NER':
        out_df.columns = [ 
            "ID",
            "Form",
            "NER",
                        ]
    elif annotator_params == 'All POS':
        out_df.columns = [ 
            "ID",
            "Form",
            "POStag",
                        ]
    elif annotator_params == 'sentiment':
        out_df.columns = [ 
            "ID",
            "Form",
            "sentiment_score",
                        ]                                    
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