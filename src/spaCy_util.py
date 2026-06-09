import GUI_util
import IO_libraries_util
import sys

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"spaCy_util",['os','spacy','tkinter','pandas','warnings','subprocess'])==False:
    sys.exit(0)

import tkinter.messagebox as mb

# import spacy will trigger tensorflow
try:
    import spacy
except Exception as e:
    # print(err)
    mb.showwarning(title='Warning',message='The NLP Suite encountered an error in importing spacy, most likely due to tensorflow.\n\nERROR: ' + str(e))
    sys.exit(0)

from spacytextblob.spacytextblob import SpacyTextBlob
import pandas as pd
import os
import warnings
import subprocess

import IO_files_util
import IO_csv_util
import GUI_util
import IO_user_interface_util
import constants_util
import parsers_annotators_visualization_util
import reminders_util

warnings.simplefilter(action='ignore', category=FutureWarning)

# list available languages of spaCy
def list_all_languages():
    # listed at the bottom of this script
    languages = sorted(spacy_available_lang)
    langs_full = sorted([dict(constants_util.languages)[x] for x in languages])
    return langs_full

def open_spaCy_website(message, lang_list):
    url='https://spacy.io/usage/models'
    Stanza_web = '\n\nLanguage and annotator options for spaCy are listed at the spaCy website\n\n' + url
    website_name = 'spaCy website'
    message_title = 'spaCy website'
    message = message + Stanza_web + '\n\nWould you like to open the spaCy website for annotator availability for the various languages supported by spaCy?'
    import IO_libraries_util
    IO_libraries_util.open_url(website_name, url, ask_to_open=True, message_title=message_title, message=message)

def check_spaCy_available_languages(language):
    available_language = False
    lang_list=[]
    not_available_lang_list=[]
    language_list = list_all_languages() # language_list available in spaCy as long names: English, Chinese, ...
    for short, long in constants_util.languages:
        if long == language[0]:
            if long in language_list:
                available_language = True
                lang_list.append(short)
                break
    if not available_language:
        open_spaCy_website('The ' + str(language[0]) + ' language is not available for NLP processing in spaCy.', lang_list)
    return available_language, lang_list

# spaCy annotate functions
def spaCy_annotate(configFilename, inputFilename, inputDir,
                    outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
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

    if not isinstance(language,list):
        language=[language]
    available_language, lang_list = check_spaCy_available_languages(language)
    if not available_language:
        return filesToOpen
    else:
        lang=lang_list[0]

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running spaCy ' + str(annotator_params[0]) + ' annotator at',
                                            True, '', True, '', False)
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
    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(scriptName, reminders_util.title_options_spaCy_parameters,
                                 reminders_util.message_spaCy_parameters, True)

    # iterate through kwarg items
    extract_date_from_text_var = False
    filename_embeds_date_var = False
    google_earth_var = False
    for key, value in kwargs.items():
        if key == 'extract_date_from_text_var' and value == True:
            extract_date_from_text_var = True
        if key == 'filename_embeds_date_var' and value == True:
            filename_embeds_date_var = True
        if key == 'google_earth_var' and value == True:
            google_earth_var = True

    # annotating each input file
    docID = 0

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
        # a CoNLL table is exported automatically for spaCy and Stanza
        outputDir = IO_files_util.make_output_subdirectory('', '', outputDir,
                                                           label=annotator + "_CoNLL",
                                                           silent=True)
    else:
        outputDir = create_output_directory(inputFilename, inputDir, outputDir, annotator)

    # set up spaCy pipeline
    # load selected spaCy language model (download only if not already installed)
    model_default = "_core_web_sm"
    model_name = lang + model_default
    try:
        nlp = spacy.load(model_name)
    except OSError:
        # model not installed yet — download once
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            nlp = spacy.load(model_name)
        except Exception:
            mb.showinfo("Warning",
                         "spaCy encountered an error trying to download the language pack " + str(language) + "\n\nCheck if this language is available in spaCy.")
            return filesToOpen
    try:
        if "sentiment" in annotator_params:
            nlp.add_pipe('spacytextblob')
    except Exception:
        mb.showinfo("Warning",
                     "spaCy encountered an error adding the sentiment pipeline for " + str(language) + ".")
        return filesToOpen

    # different outputFilename if SVO is selected
    if "SVO" in annotator_params:
        svo_df = pd.DataFrame()
        svo_df_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                        'SVO_spaCy')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                            'CoNLL_SpaCy')
    else:
        # TODO annotator_params is always passed as a string rather than a list
        if 'depparse' in annotator_params:
            annotator_label='CoNLL'
        else:
            annotator_label=annotator
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                 annotator_label+'_SpaCy')
    # collect per-document DataFrames in lists, concat once at the end (avoids O(n²) concat)
    all_dfs = []
    all_svo_dfs = []

    # iterate corpus
    for doc in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(doc)
        # extract date in file_name
        if filename_embeds_date_var:
            global date_str
            date_str = date_in_filename(doc, **kwargs)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)

        # open file and extract text
        text = open(doc, 'r', encoding=language_encoding, errors='ignore').read().replace("\n", " ")

        # process given text with spaCy annotator
        try:
            Spacy_output = nlp(text)
        except Exception:
            mb.showinfo("Warning",
                        "spaCy encountered an error processing " + tail + " with language " + str(language) + "\n\nTry manually selecting the appropriate language rather than multilingual.")
            return filesToOpen

        # convert Doc to DataFrame
        temp_df = convertSpacyDoctoDf(Spacy_output, inputFilename, inputDir, tail, int(docID), annotator_params, lang_list)
        all_dfs.append(temp_df)

        # SVO extraction if selected
        if "SVO" in annotator_params:
            temp_svo_df = extractSVO(Spacy_output, int(docID), inputFilename, inputDir, tail, filename_embeds_date_var)
            all_svo_dfs.append(temp_svo_df)

    # concatenate all results at once and save
    df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    df.to_csv(outputFilename, index=False, encoding=language_encoding)
    filesToOpen.append(outputFilename)

    if "SVO" in annotator_params and all_svo_dfs:
        svo_df = pd.concat(all_svo_dfs, ignore_index=True)
        svo_df.to_csv(svo_df_outputFilename, index=False, encoding=language_encoding)
        filesToOpen.append(svo_df_outputFilename)

        # create locations file if GIS visualization is selected
        if google_earth_var is True:
            loc_df = visualize_GIS_maps_spaCy(svo_df)
            loc_df_outputFilename = kwargs["location_filename"]
            loc_df.to_csv(loc_df_outputFilename, index=False, encoding=language_encoding)
            filesToOpen.append(loc_df_outputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running spaCy ' + str(annotator_params[0]) + ' annotator at',
                                       True,'',True, startTime)

    # deduplicate before visualization (each file only needs to be visualized once)
    filesToVisualize = list(dict.fromkeys(filesToOpen))
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
                    chartPackage,dataTransformation)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

    return filesToOpen


def get_mwe(out_df):
    # enter Record and Sentence IDs
    i = 0
    sidx = 1
    max_idx = len(out_df) - 1
    for row in out_df.iterrows():
        # if i != 0 and row[1]['is_sent_start'] == True:
        #     sidx+=1
        # # out_df.at[i, 'Record ID'] = int(row[1]['id'])
        # out_df.at[i, 'Sentence ID'] = int(sidx)

        # process IOB tags for Multi-Word Expression column
        mwe = out_df.at[i, 'Multi-Word Expression']
        if mwe == 'B':
            tmp = mwe
            tmp_idx = i
            # find the last index of this MWE
            while tmp != 'O' and tmp_idx < max_idx:
                tmp = out_df.at[tmp_idx, 'Multi-Word Expression']
                tmp_idx += 1
            # if the tag of the next token is B or if it's a single tag with one B, MWE is itself
            if i == max_idx and out_df.at[i, 'Multi-Word Expression'] == 'B':
                out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                # out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Word']
            elif tmp_idx == i + 2 or (i <= max_idx and out_df.at[i + 1, 'Multi-Word Expression'] == 'B'):
                out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Form']
                # out_df.at[i, 'Multi-Word Expression'] = out_df.at[i, 'Word']
            else:
                # iterate reversely from the last tag to the first tag, and update the MWE
                for j in reversed(range(i, tmp_idx - 1)):
                    if j == tmp_idx - 2:
                        out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j, 'Form']
                        # out_df.at[j, 'Multi-Word Expression'] = out_df.at[j - 1, 'Word'] + ' ' + out_df.at[j, 'Word']
                    elif out_df.at[j, 'Multi-Word Expression'] == 'B':
                        out_df.at[j, 'Multi-Word Expression'] = out_df.at[j + 1, 'Multi-Word Expression']
                        # when finally reach the first tag (B), update existing MWE with complete MWE
                        for k in reversed(range(i, tmp_idx - 1)):
                            if k == i:
                                out_df.at[k, 'Multi-Word Expression'] = out_df.at[j, 'Multi-Word Expression']
                            else:
                                out_df.at[k, 'Multi-Word Expression'] = 'O'
                    elif out_df.at[j, 'Multi-Word Expression'] == 'I':
                        out_df.at[j, 'Multi-Word Expression'] = out_df.at[j-1, 'Form'] + ' ' + out_df.at[j+1 , 'Multi-Word Expression']
                        # out_df.at[j, 'Multi-Word Expression'] = out_df.at[j - 1, 'Word'] + ' ' + out_df.at[
                        #     j + 1, 'Multi-Word Expression']
        i += 1
    # drop 'is_sent_start' column
    out_df = out_df.drop(columns=['is_sent_start'])
    return out_df

# Convert spaCy doc to pandas dataframe
def convertSpacyDoctoDf(spacy_doc, inputFilename, inputDir, tail, docID, annotator_params, language):

    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    doc_hyperlink = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)

    if "sentiment" in str(annotator_params):
        rows = []
        for c, sent in enumerate(spacy_doc.sents):
            score = round(sent._.blob.polarity, 2)
            label = 'positive' if score > 0 else ('negative' if score < 0 else 'neutral')
            rows.append({
                'Sentiment score': score,
                'Sentiment label': label,
                'Sentence ID': int(c + 1),
                'Sentence': sent.text,
                'Document ID': int(docID),
                'Document': doc_hyperlink
            })
        out_df = pd.DataFrame(rows, columns=[
            'Sentiment score', 'Sentiment label', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
        return out_df

    if "NER" in str(annotator_params):
        rows = []
        sent_ID = 1
        for sent in spacy_doc.sents:
            sent_text = sent.text
            for token in sent:
                rows.append({
                    'Form': token.text,
                    'NER': token.ent_type_,
                    'is_sent_start': token.is_sent_start,
                    'Multi-Word Expression': token.ent_iob_,
                    'Sentence ID': sent_ID,
                    'Sentence': sent_text,
                    'Document ID': docID,
                    'Document': doc_hyperlink
                })
            sent_ID += 1
        out_df = pd.DataFrame(rows)
        # process MWE IOB tags once on the complete DataFrame (not per-sentence)
        out_df = get_mwe(out_df)
        out_df = out_df[['Form', 'NER', 'Multi-Word Expression', 'Sentence ID', 'Sentence', 'Document ID', 'Document']]
        return out_df

    if "parse" in str(annotator_params) or "SVO" in str(annotator_params):
        rows = []
        for i, sent in enumerate(spacy_doc.sents):
            sent_text = sent.text
            for j, token in enumerate(sent):
                rows.append({
                    'ID': int(j),
                    'Form': token.text,
                    'Lemma': token.lemma_,
                    'POS': token.pos_,
                    'Head': token.head.i,
                    'DepRel': token.dep_,
                    'is_sent_start': token.is_sent_start,
                    'NER': token.ent_type_,
                    'Multi-Word Expression': token.ent_iob_,
                    'Sentence ID': i + 1,
                    'Sentence': sent_text,
                    'Document ID': docID,
                    'Document': doc_hyperlink
                })
        out_df = pd.DataFrame(rows)
        # process MWE IOB tags once on the complete DataFrame (not per-sentence)
        out_df = get_mwe(out_df)
        out_df = out_df[
            ['ID', 'Form', 'Lemma', 'POS', 'NER', 'Multi-Word Expression', 'Head', 'DepRel', 'Sentence ID', 'Sentence',
             'Document ID', 'Document']]
        return out_df

    return pd.DataFrame()

# extract and returns SVO from spaCy doc
# input: spaCy Document
def extractSVO(doc, docID, inputFilename, inputDir, tail, filename_embeds_date_var):
    # check if the input is a single file or directory
    if inputDir != '':
        inputFilename = inputDir + os.sep + tail

    # subject,verb and object constants
    SUBJECT_DEPS = {"nsubj", "nsubjpass", "csubj", "agent", "expl"}
    VERB_POS = {"VERB", "AUX"}
    OBJECT_DEPS = {"obj", "iobj", "dobj", "dative", "attr", "oprd"}
    # NER tags dictionary for location, person and time
    NER_LOCATION = {"GPE", "LOC"}
    NER_PERSON = {"PERSON"}
    NER_ORGANIZATION = {"ORG"}
    NER_TIME = {"TIME", "DATE"}

    # collect SVO rows as list of dicts (much faster than cell-by-cell df.at[])
    svo_rows = []
    c = 0
    for sent in doc.sents:
        row = {}
        SVO_found = False
        loc_ent_iob_ = ''
        per_ent_iob_ = ''
        org_ent_iob_ = ''
        tim_ent_iob_ = ''
        for token in sent:
            if token.dep_ in SUBJECT_DEPS or token.head.dep_ in SUBJECT_DEPS:
                row['Subject (S)'] = token.text
                SVO_found = True
            if token.pos_ in VERB_POS:
                row['Verb (V)'] = token.text
                SVO_found = True
            if token.dep_ in OBJECT_DEPS or token.head.dep_ in OBJECT_DEPS:
                row['Object (O)'] = token.text
                SVO_found = True
            # extract NER tags
            if SVO_found:
                ent = token.ent_type_
                iob = token.ent_iob_
                if ent in NER_LOCATION:
                    row['Location'], loc_ent_iob_ = _append_ner(row.get('Location'), token.text, iob, loc_ent_iob_)
                elif ent in NER_PERSON:
                    row['Person'], per_ent_iob_ = _append_ner(row.get('Person'), token.text, iob, per_ent_iob_)
                elif ent in NER_ORGANIZATION:
                    row['Organization'], org_ent_iob_ = _append_ner(row.get('Organization'), token.text, iob, org_ent_iob_)
                elif ent in NER_TIME:
                    row['Time'], tim_ent_iob_ = _append_ner(row.get('Time'), token.text, iob, tim_ent_iob_)
        # only keep sentences where an SVO was found and a verb is present
        if SVO_found and 'Verb (V)' in row:
            row.setdefault('Subject (S)', '?')
            row.setdefault('Object (O)', '')
            row['Sentence ID'] = c + 1
            row['Sentence'] = sent.text
            row['Document ID'] = docID
            row['Document'] = IO_csv_util.dressFilenameForCSVHyperlink(inputFilename)
            svo_rows.append(row)
        c += 1

    # build DataFrame from collected rows
    base_cols = ['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Organization', 'Time',
                 'Sentence ID', 'Sentence', 'Document ID', 'Document']
    svo_df = pd.DataFrame(svo_rows, columns=base_cols) if svo_rows else pd.DataFrame(columns=base_cols)

    # add trailing semicolons to NER columns for GIS visualization (vectorized)
    for col in ('Location', 'Person', 'Organization', 'Time'):
        mask = svo_df[col].notna() & svo_df[col].astype(str).str.len().gt(0)
        svo_df.loc[mask, col] = svo_df.loc[mask, col].astype(str).where(
            svo_df.loc[mask, col].astype(str).str.endswith(';'),
            svo_df.loc[mask, col].astype(str) + ';')

    # add date from filename
    if filename_embeds_date_var:
        svo_df['Date'] = date_str
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Organization', 'Time',
                          'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date']]
    else:
        svo_df = svo_df[['Subject (S)', 'Verb (V)', 'Object (O)', 'Location', 'Person', 'Organization', 'Time',
                          'Sentence ID', 'Sentence', 'Document ID', 'Document']]

    return svo_df


# Helper: accumulate NER text using IOB tags (replaces the old extractNER + iterrows approach)
def _append_ner(current_val, text, iob, prev_iob):
    """Append a NER token to the running value, respecting IOB boundaries."""
    if current_val is None or (not isinstance(current_val, str)):
        return text, iob
    if iob == 'B':
        return current_val + '; ' + text, iob
    elif iob == 'I':
        return current_val + ' ' + text, iob
    return current_val, iob

# extract NERs
# spaCy uses IOB tags for entities (Inside-Outside-Beginning)
def extractNER(word, df, idx, column, NER_bool, ent_iob):
    if isinstance(df.at[idx, column], str):
        if word.ent_iob_ == 'B':
            tempNER = df.at[idx, column]
            currentNER = word.text
            df.at[idx, column] = tempNER + '; ' + currentNER
        elif word.ent_iob_ == 'I':
            tempNER = df.at[idx, column]
            currentNER = word.text
            df.at[idx, column] = tempNER + ' ' + currentNER
    else:
        df.at[idx, column] = word.text

    ent_iob = word.ent_iob_

    return df, NER_bool, ent_iob

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
        date, date_str, month, day, year = IO_files_util.getDateFromFileName(document, date_format, items_separator_var, date_position_var)
    return date_str

# create locations file for GIS
def visualize_GIS_maps_spaCy(svo_df):
    loc_df = pd.DataFrame(columns=['Location', 'NER', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
    for _,row in svo_df.iterrows():
        if isinstance(row['Location'], str):
            loc_list = row['Location'].split(';')
            for loc in loc_list:
                if loc != '':
                    loc_df.loc[len(loc_df.index)] = [loc, 'LOCATION', row['Sentence ID'], row['Sentence'], row['Document ID'], row['Document']]
    return loc_df

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
                                                           label=annotator_label + "_spaCy",
                                                           silent=True)

    return outputDir

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
    "uk",
]

NER_dict = [
    "PERSON", # - People, including fictional.
    "NORP", # - Nationalities or religious or political groups.
    "FAC", # - Buildings, airports, highways, bridges, etc.
    "ORG", # - Companies, agencies, institutions, etc.
    "GPE", # - Countries, cities, states.
    "LOC", # - Non-GPE locations, mountain ranges, bodies of water.
    "PRODUCT", # - Objects, vehicles, foods, etc. (Not services.)
    "EVENT", # - Named hurricanes, battles, wars, sports events, etc.
    "WORK_OF_ART", # - Titles of books, songs, etc.
    "LAW", # - Named documents made into laws.
    "LANGUAGE", # - Any named language.
    "DATE", # - Absolute or relative dates or periods.
    "TIME", # - Times smaller than a day.
    "PERCENT", # - Percentage, including "%".
    "MONEY", # - Monetary values, including unit.
    "QUANTITY", # - Measurements, as of weight or distance.
    "ORDINAL", # - "first", "second", etc.
    "CARDINAL", # - Numerals that do not fall under another type.]}
    ]
