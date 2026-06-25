import sys
import GUI_util
# import IO_libraries_util
#
# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "CoNLL_util",
# 								['os', 'io','tkinter','pandas','time']) == False:
# 	sys.exit(0)

import os
import tkinter.messagebox as mb
import time
import io
import pandas as pd


import IO_user_interface_util
import Stanford_CoreNLP_tags_util
import IO_csv_util

global sentenceID_position, documentID_position, document_position

clause_position = 8 # NEW CoNLL_U
sentenceID_position = 10  # NEW CoNLL_U
documentID_position = 11  # NEW CoNLL_U
document_position = 12 # NEW CoNLL_U

# Canonical column order — all CoNLL tables are normalized to this layout
# so that positional indexing works regardless of source package
CANONICAL_COLUMNS = ["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel",
                     "Deps", "Clause Tag", "Record ID", "Sentence ID",
                     "Document ID", "Document"]
# Minimum columns every valid CoNLL table must have
REQUIRED_COLUMNS = {'ID', 'Form', 'Lemma', 'POS', 'NER', 'Head', 'DepRel',
                    'Sentence ID', 'Document ID', 'Document'}


def detect_CoNLL_package(headers):
    """Detect which NLP package generated the CoNLL table."""
    if 'feats' in headers:
        return 'Stanza'
    elif 'Deps' in headers:
        return 'CoreNLP'
    elif 'Clause Tag' in headers:
        return 'CoreNLP'
    elif 'Sentence' in headers and 'Multi-Word Expression' in headers:
        return 'spaCy'
    return 'unknown'


def normalize_to_canonical(headers, data):
    """Reorder columns from any CoNLL format to canonical (CoreNLP) order.

    Missing columns (Deps, Clause Tag, Record ID) are filled with empty
    strings.  Record ID is auto-generated when absent so that downstream
    sorts by Record ID still work.

    An optional 14th column (Year/Date) is preserved if present.

    Returns (canonical_headers, normalized_data).
    """
    source_positions = {h: i for i, h in enumerate(headers)}

    # Build target column list — canonical + optional Date/Year
    target_cols = list(CANONICAL_COLUMNS)
    # Check for optional Year/Date column (some CoreNLP tables have it)
    extra_col = None
    for candidate in ('Year', 'Date'):
        if candidate in source_positions:
            extra_col = candidate
            target_cols.append(candidate)
            break

    # Build mapping: for each target column, the source column index (or None)
    mapping = []
    for col in target_cols:
        mapping.append(source_positions.get(col))

    record_id_canon_idx = CANONICAL_COLUMNS.index('Record ID')  # 9
    need_record_id = mapping[record_id_canon_idx] is None

    normalized = []
    for row_num, row in enumerate(data):
        new_row = []
        for src_pos in mapping:
            if src_pos is not None and src_pos < len(row):
                new_row.append(row[src_pos])
            else:
                new_row.append('')
        # Auto-generate Record ID when missing (e.g. spaCy tables)
        if need_record_id:
            new_row[record_id_canon_idx] = str(row_num + 1)
        normalized.append(new_row)

    return target_cols, normalized

def find_full_postag(__form__, __postag__):
    if __postag__ in Stanford_CoreNLP_tags_util.dict_POSTAG:
        return Stanford_CoreNLP_tags_util.dict_POSTAG[__postag__]
    else:
        #return __form__
        return "Not found in CoNLL POSTAG list"

def find_full_deprel(__form__, __deprel__):
    if __deprel__ in Stanford_CoreNLP_tags_util.dict_DEPREL:
        return Stanford_CoreNLP_tags_util.dict_DEPREL[__deprel__]
    else:
        #return __form__
        return "Not found in CoNLL DEPREL list"


def find_full_clausalTag(__form__, __clausalTag__):
    if __clausalTag__ in Stanford_CoreNLP_tags_util.dict_CLAUSALTAG:
        return Stanford_CoreNLP_tags_util.dict_CLAUSALTAG[__clausalTag__]
    else:
        #return __form__
        return "Not found in CoNLL CLausal_Tag list"

# Check that a csv file is a valid CoNLL table.
# Accepts tables produced by CoreNLP, Stanza, or spaCy.
# returns False if filename is NOT CoNLL
def check_CoNLL(filename, skipWarning=False):
    headers = IO_csv_util.get_csvfile_headers(filename)
    header_set = set(headers)
    missing = REQUIRED_COLUMNS - header_set
    if missing:
        if not skipWarning:
            mb.showwarning(title='Input file error',
                           message='The CoNLL table is missing required columns: '
                                   + ', '.join(sorted(missing))
                                   + '.\n\nRequired columns are: '
                                   + ', '.join(sorted(REQUIRED_COLUMNS))
                                   + '.\n\nPlease, select a valid CoNLL file and try again.')
        return False
    return True


def _default_output_dir():
    """The Suite's default 'Output files directory', read from config/NLP_default_IO_config.csv (where the parser
    auto-creates its output subdirectories). Returns '' if it cannot be read."""
    try:
        import GUI_IO_util
        import csv as _csv
        path = os.path.join(GUI_IO_util.configPath, 'NLP_default_IO_config.csv')
        if os.path.isfile(path):
            with open(path, 'r', newline='', encoding='utf-8', errors='ignore') as fh:
                for row in _csv.reader(fh):
                    if row and row[0].strip() == 'Output files directory':
                        return row[1].strip() if len(row) > 1 else ''
    except Exception:
        pass
    return ''


def _corpus_search_roots(outputDir, inputFilename='', inputDir=''):
    """Directories to search for a corpus's CoNLL table: the output dir, the input dir, the input file's folder,
    and the Suite's default output dir from config/NLP_default_IO_config.csv (where the parser auto-creates its
    output subdirectories) - deduped, existing only. The parser may write the CoNLL to any of these per setup."""
    roots = []
    for d in (outputDir, inputDir, os.path.dirname(inputFilename) if inputFilename else '', _default_output_dir()):
        if d and os.path.isdir(d) and d not in roots:
            roots.append(d)
    return roots


def find_corpus_CoNLL(outputDir, inputFilename='', inputDir=''):
    """Return a newest-first list of valid CoNLL csv tables found for the current corpus.

    Searches the output dir, the input dir, and the input file's folder (see _corpus_search_roots); keeps every
    .csv whose path contains 'CoNLL' and that validates as a CoNLL table (look-alikes such as saved I/O
    configuration files are rejected by check_CoNLL), and - when a corpus name is known - narrows to files whose
    name contains it. Used by the Semantic Aggregation hub to hand a corpus's CoNLL to the CoNLL Table Analyzer."""
    # corpus stem: a single txt file's base name, else the input directory name
    stem = ''
    if inputFilename and inputFilename.lower().endswith('.txt'):
        stem = os.path.basename(inputFilename)[:-4]
    elif inputDir:
        stem = os.path.basename(os.path.normpath(inputDir))
    matches = []
    seen = set()
    for base in _corpus_search_roots(outputDir, inputFilename, inputDir):
        for root, dirs, files in os.walk(base):
            for f in files:
                if not f.lower().endswith('.csv'):
                    continue
                path = os.path.join(root, f)
                if 'conll' not in path.lower() or path in seen:
                    continue
                seen.add(path)
                try:
                    if check_CoNLL(path, True):
                        matches.append(path)
                except Exception:
                    pass
    if stem:
        # match the corpus name anywhere in the path: the parser's auto-created subdir carries the corpus name
        # even when the CoNLL filename itself is mangled (e.g. the parser's own typo 'newspperArticles')
        narrowed = [m for m in matches if stem.lower() in m.lower()]
        if narrowed:
            matches = narrowed
    matches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return matches


def open_analyzer_for_current_corpus(run_parser=False):
    """Hand the current corpus's CoNLL table to the CoNLL Table Analyzer GUI (the 'CoNLL handoff').

    run_parser=True: open the Parsers/Annotators GUI (parsers_annotators_main.py), which parses the corpus
    with the configured package (Stanford CoreNLP / Stanza / spaCy) and itself opens the analyzer preloaded
    with the fresh CoNLL - we reuse that canonical pipeline rather than duplicate the 3-way parser dispatch.

    run_parser=False: look in the current IO output directory for a CoNLL table matching the corpus; if found,
    open the analyzer pre-loaded with it (run_script forwards the path as argv, read at the analyzer's startup,
    CoNLL_table_analyzer_main.py lines ~1012-1031). If none is found, offer to open the analyzer so the user
    can select one. Returns the CoNLL path opened (or None). The launcher widget is placed/wired in the hub."""
    import run_script_util
    if run_parser:
        run_script_util.run_script("parsers_annotators_main.py", "open_analyzer")
        return None
    outputDir = GUI_util.output_dir_path.get()
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    matches = find_corpus_CoNLL(outputDir, inputFilename, inputDir)
    if matches:
        conll = matches[0]  # newest
        run_script_util.run_script("CoNLL_table_analyzer_main.py", conll)
        return conll
    roots = _corpus_search_roots(outputDir, inputFilename, inputDir)
    where = '\n   '.join(roots) if roots else '(no input/output directory is set)'
    ans = mb.askyesno(title='No CoNLL table found',
                      message="No CoNLL table was found for the current corpus. I searched:\n\n   " + where + "\n\n"
                              "(A CoNLL table is one produced by parsing your corpus with Stanford CoreNLP, Stanza, or spaCy; "
                              "look-alike files such as saved I/O configurations are ignored.)\n\n"
                              "If your CoNLL table is elsewhere, click YES to open the CoNLL Table Analyzer and select it manually.\n"
                              "Click NO to cancel (or tick 'Run the default parser' to parse your corpus first).")
    if ans:
        run_script_util.run_script("CoNLL_table_analyzer_main.py")
    return None


# The function builds a double list of all records in the CoNLL table
def CoNLL_record_division(list_csv_rows):

    try:
        list_sentences = []
        Sentence_ID_prev = 1  # Sentence_ID of previous row
        Document_ID_prev = '1.0'  # Document_ID of previous row
        current_sentence = []

        for _index_, item in enumerate(list_csv_rows):
            Sentence_ID = int(item[sentenceID_position])
            Document_ID = item[documentID_position]
            # This includes the last sentence
            if _index_ + 1 == len(list_csv_rows):
                list_sentences.append(current_sentence)
                current_sentence.append(item)
                return list_sentences
            if Sentence_ID == Sentence_ID_prev and Document_ID == Document_ID_prev:
                current_sentence.append(item)
                continue
            else:
                Sentence_ID_prev = Sentence_ID
                Document_ID_prev = Document_ID
                list_sentences.append(current_sentence)
                current_sentence = []
                current_sentence.append(item)
        if len(list_sentences) == 0:
            currentScript = os.path.basename(__file__)
            mb.showinfo("Fatal error",
                        "The sentence_division function in " + currentScript + " failed.\n\nPlease, check your data and/or the python scripts.\n\nIf the problem persists, please inform the script developers of the problem.\n\nProgram will exit.")
        return list_sentences
    except:
        print(
            "FATAL ERROR: INPUT MUST BE A CoNLL TABLE generated by Stanford CoreNLP, Stanza, or spaCy. Please, select a CoNLL table and try again.")
        mb.showinfo("Fatal error",
                    "INPUT MUST BE A CoNLL TABLE generated by Stanford CoreNLP, Stanza, or spaCy.\n\nPlease, select a CoNLL table and try again.")

# The function builds a double list of each sentence in the CoNLL table
# [['The','President',...]['Ladies','and','Gentlemen']...]]
# searchedCoNLLField FORM or LEMMA
def sentence_division(list_csv_rows,searchedCoNLLField):

    try:
        list_sentences = []
        Sentence_ID_prev = 1  # Sentence_ID of previous row
        Document_ID_prev = '1.0'  # Document_ID of previous row
        current_sentence = []
        index=1
        if searchedCoNLLField == 'LEMMA':
            index = 2
        for _index_, item in enumerate(list_csv_rows):
            Sentence_ID = int(item[sentenceID_position])
            Document_ID = item[documentID_position]
            # This includes the last sentence
            if _index_ + 1 == len(list_csv_rows):
                list_sentences.append(current_sentence)
                # current_sentence.append(item[1])
                return list_sentences
            if Sentence_ID == Sentence_ID_prev and Document_ID == Document_ID_prev:
                current_sentence.append(item[index])
                continue
            else:
                Sentence_ID_prev = Sentence_ID
                Document_ID_prev = Document_ID
                # skip empty sentence at the very beginning
                # TODO Document_ID should be an integer!
                if Sentence_ID == 1 and Document_ID == '1' and len(current_sentence)==0:
                    continue
                list_sentences.append(current_sentence)
                current_sentence = []
                current_sentence.append(item[index])
        if len(list_sentences) == 0:
            currentScript = os.path.basename(__file__)
            mb.showinfo("Fatal error",
                        "The sentence_division function in " + currentScript + " failed.\n\nPlease, check your data and/or the python scripts.\n\nIf the problem persists, please inform the script developers of the problem.\n\nProgram will exit.")
        return list_sentences
    except:
        print(
            "FATAL ERROR: INPUT MUST BE A CoNLL TABLE generated by Stanford CoreNLP, Stanza, or spaCy. Please, select a CoNLL table and try again.")
        mb.showinfo("Fatal error",
                    "INPUT MUST BE A CoNLL TABLE generated by Stanford CoreNLP, Stanza, or spaCy.\n\nPlease, select a CoNLL table and try again.")

# searching for a specific sentence sent_id in a specific document Document_ID
def Sentence_searcher(list_all_sents, Document_ID, sent_id):
    for sent in list_all_sents:
        if len(sent) > 0:
            if sent[0][documentID_position] == Document_ID and int(sent[0][sentenceID_position]) == int(sent_id):
                sent_str = " ".join([i[1] for i in sent])
                break
    return sent_str

# used by all CoNLL_*_analysis_util scripts

# label is the header displayed (e.g., verb voice, modality)
# in input the function takes _voice_sorted_ created by the various CoNLL analyses functions
# in input it contains the CoNLL table entries with the addition of the label (modallity, tense...) followed by the full sentence
# in output, the label is placed FIRST
def sort_output_list(label, _voice_sorted_):
    output_list = [
        [label, 'TOKEN_INDEX', 'FORM', 'LEMMA', 'POSTAG', 'POSTAG-DESCRIPTION', 'DEPREL', 'DEPREL-DESCRIPTION',
         'CLAUSAL TAG', 'CLAUSAL TAG-DESCRIPTION', 'Sentence ID', 'Sentence', 'Document ID', 'Document']]
    #the earlier new CoNLL routine always had the extra header date, whether there or not;
    #   so need to test not to break the code

    # recordID_position = 8
    # documentID_position = 10

    # NEW
    # recordID_position = 9
    # sentence_ID position = 10

    # the i[#] refer too the position in the CoNLL table
    # 12/13 is the label: modality, tense, ... (Displayed as the first column of the output csv file)

    # NEW
    # 13/14 is the label: modality, tense, ... (Displayed as the first column of the output csv file)

    # 0 is INDEX
    # 1 form
    # 2 lemma
    # 3 postag
    # 6 deprel

    # 7 clause
    # 9 Sentence_ID
    # 10 Document_ID/documentID_position
    # 11 document name

    # NEW
    # 8 clause
    # 10 Sentence_ID
    # 11 Document_ID/documentID_position
    # 12 document name

    # 12/13 label: modality, tense, ...
    # 13/14 full sentence

    # NEW
    # 13/14 label: modality, tense, ...
    # 14/15 full sentence

    try:
        _list_sorted_ = [
            [i[14], i[0], i[1], i[2], i[3], find_full_postag(i[1],i[3]), i[6], find_full_deprel(i[1],i[6]), i[clause_position],
                find_full_clausalTag(i[1],i[clause_position]), i[sentenceID_position], i[documentID_position], i[documentID_position], i[15]]
        for i in _voice_sorted_]
    except:
        try:
            _list_sorted_ = [
                [i[13], i[0], i[1], i[2], i[3], find_full_postag(i[1],i[3]), i[6], find_full_deprel(i[1],i[6]), i[clause_position],
                 find_full_clausalTag(i[1],i[clause_position]), i[sentenceID_position], i[documentID_position], i[documentID_position], i[14]] for i in _voice_sorted_]
        except:
            mb.showwarning(title="CoNLLL table ill formed",
                           message="The CoNLL table is ill formed. You may have tinkered with it. Please, rerun the parser since many scripts rely on the CoNLL table.")
            return
    output_list += _list_sorted_
    return output_list

# Cynthia Dong & Roberto Franzosi 11/28/2019
# compute a whole sentence from an input CoNLL table for a specific sentenceID and documentID
# called by the geocoder
def compute_sentence(CoNLL_table, recordID, sentenceID, documentID):
    """
    :type documentID: object
    """
    # Open ConLL
    df = pd.read_csv(io.open(CoNLL_table, 'rb'), sep=',', index_col=False, encoding='utf-8',on_bad_lines='skip')
    df = df[df["Sentence ID"] == sentenceID]
    df = df[df["Document ID"] == documentID]
    rows = []  # Store data
    sent_str = ""  # Build string
    index = recordID
    for recordID in range(df.shape[0]):  # For every row in the ConLL table starting from RecordID
        row = df.iloc[recordID, :]
        if sentenceID == row['Sentence ID'] and documentID == row['Document ID']:
            if row['DepRel'] == "punct":
                sent_str = sent_str + str(row['Form'])
            else:
                sent_str = sent_str + " " + str(row['Form'])
        else:
            if row['Sentence ID'] > sentenceID or row['Document ID'] > documentID:
                break
        index = index + 1
    return index, sent_str

# the function computes a sentence table from a conll table
# TODO must check for old and new CoNLL
def compute_sentence_table(CoNLL_table, output_path):
    RunningCoreNLPFromCommandLine = False
    startTime = time.localtime()
    # print ("")
    # print("Started computing the Sentence table at " + str(startTime[3]) + ':' + str(startTime[4]))  #Time when merge started, for future reference
    # print ("")
    if RunningCoreNLPFromCommandLine != True:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start', 'Started computing the Sentence table at', True)
    # tk.messagebox.showinfo("Stanford CoreNLP has finished", "Started computing the Sentence table at " + str(startTime[3]) + ':' + str(startTime[4]))
    # df = pd.read_csv(io.open(os.path.join(output_path,CoNLL_table), 'rb'), sep='\t', header=None, index_col=False) # Open ConLL
    df = pd.read_csv(io.open(os.path.join(output_path, CoNLL_table), 'rb'), sep=',', index_col=False, encoding='utf-8',on_bad_lines='skip')  # Open ConLL
    rows = []  # Store data
    sent_str = ""  # Build string
    # Keep track of variables — use column names for package-independence
    sent_index = df.iloc[0]['Sentence ID']
    doc_id = df.iloc[0]['Document ID']
    current_file = df.iloc[0]['Document']

    for index, row in df.iterrows():  # For every row in the ConLL
        if sent_index == row['Sentence ID'] and doc_id == row['Document ID']:
            if row['DepRel'] == "punct":
                sent_str = sent_str + str(row['Form'])
            else:
                sent_str = sent_str + " " + str(row['Form'])
        else:  # End the sentence, add it to the array and move onto the next one
            arr = [len(sent_str.split(" ")),
                   len(list(sent_str)), sent_index, sent_str, doc_id, current_file]
            rows.append(arr)
            sent_index = row['Sentence ID']
            sent_str = row['Form']
            current_file = row['Document']
            doc_id = row['Document ID']

    # Construct and save the table
    col_names = ['Sentence length (Number of words/tokens)',
                 'Sentence length (Number of characters)', 'Sentence ID', 'Sentence', 'Document ID', 'Document']
    df2 = pd.DataFrame(columns=col_names, data=rows)

    outputFilename = os.path.join(output_path, CoNLL_table[:-4] + "_sentence" + ".csv")
    df2.to_csv(outputFilename, encoding='utf-8',
               index=False)  # os.path.join(output_path,outputFilename), sep='\t', encoding='utf-8')
    if RunningCoreNLPFromCommandLine != True:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis end', 'Finished computing the Sentence table at', True)
    # tk.messagebox.showinfo("Stanford CoreNLP has finished", "Finished computing the Sentence table at " + str(endTime[3]) + ':' + str(endTime[4])  + ". \n\nSentence table exported as: " + outputFilename) #os.path.join(output_path,outputFilename))
    endTime = time.localtime()
    print ("\nSentence table output written to: " + outputFilename)  # os.path.join(output_path,outputFilename))     #Time when compute sentence table finished, for future reference
    return outputFilename

# the function extracts DISTINCT nouns and verbs from the CoNLL table in both form and lemma
# inputFilename contains path
def get_nouns_verbs_CoNLL(inputFilename,output_dir):

    conll_table = pd.read_csv(inputFilename, encoding='utf-8',on_bad_lines='skip')

    verb_form_set = set()
    verb_lemma_set = set()
    noun_form_set = set()
    noun_lemma_set = set()

    for index, row in conll_table.iterrows():
        # Check if cell value has length greq. than 2 since we're looking for VB* and NN*
        if len(conll_table['POS'][index]) >= 2:
            # Check if begins with VB
            if "VB" in conll_table['POS'][index][0:2]:
                # Starts with VB, add to verb set
                verb_form_set.add(conll_table['Form'][index])
                verb_lemma_set.add(conll_table['Lemma'][index])
            # Check if begins with NN
            elif 'NN' in conll_table['POS'][index][0:2]:
                noun_form_set.add(conll_table['Form'][index])
                noun_lemma_set.add(conll_table['Lemma'][index])

    verbs_form_df = pd.DataFrame(verb_form_set, columns = ['Verbs'])
    verbs_lemma_df = pd.DataFrame(verb_lemma_set, columns = ['Verbs'])
    nouns_form_df = pd.DataFrame(noun_form_set, columns = ['Nouns'])
    nouns_lemma_df = pd.DataFrame(noun_lemma_set, columns = ['Nouns'])

    nouns_form_csv=os.path.join(output_dir,os.path.basename(inputFilename[:-4])+"_nouns_form.csv")
    nouns_lemma_csv=os.path.join(output_dir,os.path.basename(inputFilename[:-4])+"_nouns_lemma.csv")
    verbs_form_csv=os.path.join(output_dir,os.path.basename(inputFilename[:-4])+"_verbs_form.csv")
    verbs_lemma_csv=os.path.join(output_dir,os.path.basename(inputFilename[:-4])+"_verbs_lemma.csv")

    nouns_form_df.to_csv(nouns_form_csv, encoding='utf-8', index=False)
    nouns_lemma_df.to_csv(nouns_lemma_csv, encoding='utf-8', index=False)
    verbs_form_df.to_csv(verbs_form_csv, encoding='utf-8', index=False)
    verbs_lemma_df.to_csv(verbs_lemma_csv, encoding='utf-8', index=False)

    return nouns_form_csv, nouns_lemma_csv, verbs_form_csv, verbs_lemma_csv
