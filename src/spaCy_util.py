import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"spaCy_util",['os','spacy','tkinter','pandas','warnings','subprocess'])==False:
    sys.exit(0)

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import pandas as pd
import tkinter.messagebox as mb
import os
import warnings
import subprocess

import IO_files_util
import IO_csv_util
import charts_util
import file_splitter_ByLength_util
import GUI_util
import GUI_IO_util
import IO_user_interface_util
import constants_util

warnings.simplefilter(action='ignore', category=FutureWarning)

# spaCy annotate functions
def spaCy_annotate(config_filename, inputFilename, inputDir,
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

    # instantiate variables for input/output handling settings
    language_encoding = 'utf-8'
    filesToOpen = []
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running spaCy at',
                                            True, '', True, '', False)
    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # annotating each input file
    docID = 0

    # check if selected language is one.
    lang = ''
    lang_list = []
    for k,v in lang_dict.items():
        if v == language:
            lang = k
            lang_list.append(lang)
            break
    # check if selected language is available in spaCy
    if lang not in spacy_available_lang:
        mb.showerror("Warning",
                    "spaCy does not currently support the " + annotator_params + " annotator for " + language + ".\n\nPlease, select a different annotator or a different language.")

    # set up spaCy pipeline
    # download selected spaCy language models
    model_default = "_core_web_sm"
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", lang+model_default])
        nlp = spacy.load(lang+model_default)
        if "sentiment" in annotator_params:
            nlp.add_pipe('spacytextblob')
    except:
        mb.showinfo("Warning",
                     "spaCy encountered an error trying to download the language pack " + str(language) + "\n\nCheck if this language is available in spaCy.")
        return

    # different outputFilename if SVO is selected
    if "SVO" in annotator_params:
        svo_df = pd.DataFrame()
        svo_df_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                        'SpaCy_' + 'SVO')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                            'SpaCy_')
    else:
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'SpaCy_' + annotator_params)
    # create output df
    df = pd.DataFrame()

    # iterate corpus
    for doc in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)

        # open file and extract text
        text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")

        # process given text with spaCy annotator
        try:
            Spacy_output = nlp(text)
        except:
            mb.showinfo("Warning",
                        "spaCy encountered an error trying to download the language pack " + str(language) + "\n\nTry manually selecting the appropriate language rather than multilingual.")
            return

        # convert Doc to DataFrame
        temp_df = convertSpacyDoctoDf(Spacy_output, inputFilename, inputDir, tail, docID, annotator_params, lang_list)
        df = pd.concat([df, temp_df], ignore_index=True, axis=0)

        # SVO extraction if selected
        if "SVO" in annotator_params:
            temp_svo_df = extractSVO(Spacy_output, docID, inputFilename, inputDir, tail)
            svo_df = pd.concat([svo_df, temp_svo_df], ignore_index=True, axis=0)

    # save dataframe to csv
    df.to_csv(outputFilename, index=False, encoding = language_encoding)
    filesToOpen.append(outputFilename)

    # save SVO dataframe
    if "SVO" in annotator_params:
        svo_df.to_csv(svo_df_outputFilename, index=False, encoding = language_encoding)
        filesToOpen.append(svo_df_outputFilename)

    return filesToOpen

# Convert spaCy doc to pandas dataframe
def convertSpacyDoctoDf(spacy_doc, inputFilename, inputDir, tail, docID, annotator_params, language):

    # output dataframe
    out_df = pd.DataFrame()

    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # if only one language is selected (not multilingual)
    # if len(language)==1 and language[0]!='multilingual':
    out_df = pd.DataFrame()

    for i, token in enumerate(spacy_doc):
        out_df.at[i, 'ID'] = token.i + 1
        out_df.at[i,'Form'] = token.text
        out_df.at[i,'Lemma'] = token.lemma_
        out_df.at[i,'POStag'] = token.pos_
        out_df.at[i,'DepRel'] = token.dep_
        out_df.at[i, 'is_sent_start'] = token.is_sent_start
        if "sentiment" in annotator_params:
            out_df.at[i,'sentiment_score_token'] = round(token._.blob.polarity,2)
            out_df.at[i,'sentiment_score_sent'] = 0 # will be replaced later
        if hasattr(token, 'ent_type_'): # check if NER is annotated for each token
            out_df.at[i,'NER'] = token.ent_type_

    # add necessary columns after the loop
    out_df['Record ID'] = None
    out_df['Sentence ID'] = None
    out_df['Document ID'] = docID
    out_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    # get sentence sentiment
    if "sentiment" in annotator_params:
        sentence_sentiment = [round(sent._.blob.polarity,2) for sent in spacy_doc.sents]

    # enter Record and Sentence IDs
    i = 0
    sidx = 1
    for row in out_df.iterrows():
        if i != 0 and row[1]['is_sent_start'] == True:
            sidx+=1
        if "sentiment" in annotator_params:
            out_df.at[i, 'sentiment_score_sent'] = sentence_sentiment[sidx-1]
        out_df.at[i, 'Record ID'] = row[1]['ID']
        out_df.at[i, 'Sentence ID'] = sidx
        i+=1

    # drop 'is_sent_start' column
    out_df = out_df.drop(columns=['is_sent_start'])

    # extract list of identified token language
    tmp_lang_lst = [lang_dict[token.lang_] for token in spacy_doc]
    out_df['Language'] = tmp_lang_lst


    return out_df

# extract and returns SVO from spaCy doc
# input: spaCy Document
def extractSVO(doc, docID, inputFilename, inputDir, tail):
    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # output: svo_df
    svo_df = pd.DataFrame(columns={'Subject (S)','VERB (V)','Object (O)'})

    # subject,verb and object constants
    SUBJECT_DEPS = {"nsubj", "nsubjpass", "csubj", "agent", "expl"}
    VERB_POS = {"VERB", "AUX"}
    OBJECT_DEPS = {"obj", "iobj", "dobj", "dative", "attr", "oprd"}

    # extract SVOs
    c = 0
    svo_df = pd.DataFrame(columns={'Subject (S)','VERB (V)','Object (O)'})
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in SUBJECT_DEPS or token.head.dep_ in SUBJECT_DEPS:
                svo_df.at[c, 'Subject (S)'] = token.text
            if token.pos_ in VERB_POS:
                svo_df.at[c, 'VERB (V)'] = token.text
            if token.dep_ in OBJECT_DEPS or token.head.dep_ in OBJECT_DEPS:
                svo_df.at[c, 'Object (O)'] = token.text
        c+=1

    # csv output columns
    svo_df['Document ID'] = docID
    svo_df['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)
    # replace NaN values accordingly
    for index, row in svo_df.iterrows():
        svo_df.at[index, 'Subject (S)'] = '?' if pd.isna(row['Subject (S)']) else row['Subject (S)']
        svo_df.at[index, 'VERB (V)'] = '' if pd.isna(row['VERB (V)']) else row['VERB (V)']
        svo_df.at[index, 'Object (O)'] = '' if pd.isna(row['Object (O)']) else row['Object (O)']

    return svo_df

# Python dictionary of language (values) and their acronyms (keys)
lang_dict  = dict(constants_util.languages)

spacy_available_lang = [
    "xx", # mult-language has different rest of model name
    "ca",
    "zh",
    "hr",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "el",
    "it",
    "ja",
    "ko",
    "lt",
    "mk",
    "nb",
    "pl",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "",
    "",
]
