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
import parsers_annotators_visualization_util

warnings.simplefilter(action='ignore', category=FutureWarning)

# list available languages of spaCy
def list_all_languages():
    languages = ['ca', 'zh', 'hr', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'el', 'it', 'ja', 'ko', 'lt', 'mk', 'xx', 'nb', 'pl', 'pt', 'ro', 'ru', 'es', 'sv', 'uk']
    languages = sorted(languages)
    langs_full = sorted([dict(constants_util.languages)[x] for x in languages])
    return langs_full

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
    language_encoding='utf-8'
    filesToOpen = []
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running spaCy at',
                                            True, '', True, '', False)
    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    if nDocs==0:
        return filesToOpen

    # iterate through kwarg items
    extract_date_from_text_var = False
    extract_date_from_filename_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            extract_date_from_text_var = True
        if key == 'extract_date_from_filename_var' and value == True:
            extract_date_from_filename_var = True

    # annotating each input file
    docID = 0

    if "Lemma" in annotator_params:
        annotator = 'Lemma'
    elif "NER" in annotator_params:
        annotator = 'NER'
    elif "All POS" in annotator_params:
        annotator = 'POS'
    elif "SVO" in annotator_params:
        annotator = 'SVO'
    elif "depparse" in annotator_params:
        annotator = 'depparse'
    elif "sentiment" in annotator_params:
        annotator = 'sentiment'
    # create the appropriate subdirectory to better organize output files
    outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                       label=annotator,
                                                       silent=False)

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
        if len(annotator_params)>1:
            annotator_string=''
        else:
            annotator_string = annotator_params[0]
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                             'SpaCy_' + annotator_string)
    # create output df
    df = pd.DataFrame()

    # iterate corpus
    for doc in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(doc)
        # extract date in file_name
        if extract_date_from_filename_var:
            global date_str
            date_str = date_in_filename(doc, **kwargs)
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
            temp_svo_df = extractSVO(Spacy_output, docID, inputFilename, inputDir, tail, extract_date_from_filename_var)
            svo_df = pd.concat([svo_df, temp_svo_df], ignore_index=True, axis=0)

    # save dataframe to csv
    df.to_csv(outputFilename, index=False, encoding=language_encoding)
    filesToOpen.append(outputFilename)

    # save SVO dataframe
    if "SVO" in annotator_params:
        svo_df.to_csv(svo_df_outputFilename, index=False, encoding=language_encoding)
        filesToOpen.append(svo_df_outputFilename)

    #TODO MINO
    filesToVisualize=filesToOpen
    for j in range(len(filesToVisualize)):
        #02/27/2021; eliminate the value error when there's no information from certain annotators
        if filesToVisualize[j][-4:] == ".csv":
            file_df = pd.read_csv(filesToVisualize[j])
            if not file_df.empty:
                outputFilename = filesToVisualize[j]
                chart_outputFilename = parsers_annotators_visualization_util.parsers_annotators_visualization(
                    config_filename, inputFilename, inputDir, outputDir,
                    outputFilename, annotator_params, kwargs, createCharts,
                    chartPackage)
                if chart_outputFilename!=None:
                    if len(chart_outputFilename) > 0:
                        filesToOpen.extend(chart_outputFilename)

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
        out_df.at[i,'Head'] = token.head.i # add Head index
        out_df.at[i,'DepRel'] = token.dep_
        out_df.at[i, 'is_sent_start'] = token.is_sent_start
        if "sentiment" in annotator_params:
            out_df.at[i,'Sentiment score (token)'] = round(token._.blob.polarity,2)
            out_df.at[i,'Sentiment score (sentence)'] = 0 # will be replaced later
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
            out_df.at[i, 'Sentiment score (sentence)'] = sentence_sentiment[sidx-1]
        out_df.at[i, 'Record ID'] = row[1]['ID']
        out_df.at[i, 'Sentence ID'] = sidx
        i+=1

    # drop 'is_sent_start' column
    out_df = out_df.drop(columns=['is_sent_start'])

    # extract list of identified token language
    tmp_lang_lst = [lang_dict[token.lang_] for token in spacy_doc]
    out_df['Language'] = tmp_lang_lst

    out_df = out_df[['ID', 'Form', 'Lemma', 'POStag', 'NER', 'Head', 'DepRel', 'Record ID', 'Sentence ID', 'Document ID', 'Document']]

    return out_df

# extract and returns SVO from spaCy doc
# input: spaCy Document
def extractSVO(doc, docID, inputFilename, inputDir, tail, extract_date_from_filename_var):
    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # output: svo_df
    if extract_date_from_filename_var:
        svo_df = pd.DataFrame(columns={'Subject (S)','Verb (V)','Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Date'})
    else:
        svo_df = pd.DataFrame(columns={'Subject (S)','Verb (V)','Object (O)', 'Location', 'Person', 'Time', 'Sentence ID'})

    # subject,verb and object constants
    SUBJECT_DEPS = {"nsubj", "nsubjpass", "csubj", "agent", "expl"}
    VERB_POS = {"VERB", "AUX"}
    OBJECT_DEPS = {"obj", "iobj", "dobj", "dative", "attr", "oprd"}
    # NER tags dictionary for location, person and time
    NER_LOCATION = {"GPE", "LOC"}
    NER_PERSON = {"PERSON"}
    NER_TIME = {"TIME", "DATE"}

    # set-ups to extract SVOs
    c = 0
    SVO_found = False
    NER_found = False
    empty_verb_idx = []
    # extract SVOs
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in SUBJECT_DEPS or token.head.dep_ in SUBJECT_DEPS:
                svo_df.at[c, 'Subject (S)'] = token.text
                SVO_found = True
            if token.pos_ in VERB_POS:
                svo_df.at[c, 'Verb (V)'] = token.text
                SVO_found = True
            if token.dep_ in OBJECT_DEPS or token.head.dep_ in OBJECT_DEPS:
                svo_df.at[c, 'Object (O)'] = token.text
                SVO_found = True
            # extract NER tags
            if SVO_found is True or NER_found is True:
                if token.ent_type_ in  NER_LOCATION:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Location', NER_found)
                elif token.ent_type_ in  NER_PERSON:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Person', NER_found)
                elif token.ent_type_ in  NER_TIME:
                    svo_df, NER_found = extractNER(token, svo_df, c, 'Time', NER_found)
        # check if SVO is found, then add Sentence ID
        if SVO_found:
            svo_df.at[c, 'Sentence ID'] = c+1
            SVO_found = False
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
    if extract_date_from_filename_var:
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Document ID', 'Document', 'Date']]
        svo_df['Date'] = date_str
    else:
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Time', 'Sentence ID', 'Document ID', 'Document']]

    return svo_df

# extract NERs
def extractNER(word, df, idx, column, NER_bool):
    if isinstance(df.at[idx, column], str):
        tempNER = df.at[idx, column]
        currentNER = word.text
        df.at[idx, column] = tempNER + '; ' + currentNER
    else:
        df.at[idx, column] = word.text

    return df, NER_bool

# extract date in filename from Stanford_CoreNLP_util
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
