import os
import platform
import re
import subprocess

import pandas as pd
import json
import stanza

import GUI_util
import GUI_IO_util
import IO_csv_util
import IO_files_util
import IO_libraries_util
import IO_user_interface_util
import reminders_util

# stanza.download('en')
lemmatizer = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma')
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


def check_system():
    system = platform.system().lower()
    if "linux" in system:
        return "linux"
    elif system == "windows":
        return "win"
    elif system == "darwin":
        return "mac"


def run_senna(inputFilename=None, inputDir=None, outputDir=None, openOutputFiles=False, createExcelCharts=False,
              filter_svo=('', '', '')) -> list:
    """
    Run the senna-osx with input type either file or directory
    :param inputFilename: name of the input text file
    :param inputDir: name of the input directory
    :param outputDir: name of the output file
    :param createExcelCharts: whether to create excel charts right after running
    :param filter_svo: a tuple with three strings, each representing a dictionary file for filtering s, v or o
    :return: a list of the files to be opened
    """
    formatted_table = []
    document_lengths = []
    filesToOpen = []
    doc_id = 0

    # check that the SENNA dir as been setup
    SENNAdir, missing_external_software = IO_libraries_util.get_external_software_dir('SVO SENNA', 'SENNA')

    if SENNAdir is None:
        return filesToOpen

    # record the time consumption before annotating text in each file
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
                                       'Started running SENNA to extract SVOs at', True,
                                       'You can follow SENNA in command line.')

    SENNA_output_file_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                     'SENNA_SVO')

    # rename a filename coreferenced by CoreNLP to obtain the correct SENNA filename
    SENNA_output_file_name = SENNA_output_file_name.replace("CoreNLP_SENNA_SVO_coref", "coref")

    if inputDir:
        # If the input is a directory
        input_docs = IO_files_util.getFileList(inputFile=inputFilename, inputDir=inputDir, fileType='.txt')

        for file in input_docs:
            doc_id += 1
            head, tail = os.path.split(file)
            print("Processing file " + str(doc_id) + '/' + str(len(input_docs)) + ' ' + tail)
            result = senna_single_file(SENNAdir, os.path.join(inputDir, file))
            formatted_table += [[os.path.join(inputDir, file)] + row for row in result]
            document_lengths.append(len(result) if not document_lengths else len(result) + document_lengths[-1])
    else:
        # If the input is a file
        head, tail = os.path.split(inputFilename)
        print('Processing file 1/1 ' + tail)
        result = senna_single_file(SENNAdir, inputFilename)
        formatted_table += [[os.path.join(inputDir, inputFilename)] + row for row in result]
        document_lengths.append(len(result))

    try:
        max_length = max([len(row) for row in formatted_table])
    except ValueError:
        reminders_util.checkReminder(config_filename, reminders_util.title_options_non_utf8,
                                     reminders_util.message_options_non_utf8, True)
        return []

    document_index = 0

    for index, row in enumerate(formatted_table):
        while len(row) < max_length:
            row.append('O')
        row.insert(0, document_index + 1)
        if index == document_lengths[document_index] - 1:
            document_index += 1

    senna_df = pd.DataFrame(formatted_table, columns=['Col %s' % i for i in range(len(formatted_table[0]))])
    print(senna_df)
    # Result of SENNA

    convert_to_svo(senna_df, SENNA_output_file_name, createExcelCharts, filter_svo)
    filesToOpen.append(SENNA_output_file_name)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running SENNA to extract SVOs at', True)
    return filesToOpen


def senna_single_file(SENNAdir, inputFilename: str) -> list:
    """
    Run senna-osx using the input from the inputFilename
    :param SENNAdir: the directory of Senna
    :param inputFilename: the name of a text file
    :return: a list of lists where each list is a row in the output senna table
    """
    senna_table = []

    # Read the input file
    try:
        with open(inputFilename, 'r', encoding='utf-8') as file:
            input_text = file.read().strip()
            file.close()
    except UnicodeDecodeError:
        reminders_util.checkReminder('SVO', reminders_util.title_options_non_utf8,
                                     reminders_util.message_non_utf8, True)
        return []

    encoded_input = input_text.replace('\n', ' ').encode()

    if check_system() == 'mac':
        senna_exec = './senna-osx'
    elif check_system() == 'win':
        senna_exec = 'senna-win32.exe'
    elif check_system() == 'linux':
        senna_exec = 'senna-linux64'

    origin_path = os.getcwd()
    # senna_exec = os.path.join(SENNAdir, senna_exec)
    # w/o changing dir SENNA will not produce an output table
    os.chdir(SENNAdir)
    cmd = subprocess.Popen([senna_exec, '-ner', '-pos', '-srl', '-psg'], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)  # Input the text to stdin

    output = cmd.communicate(input=encoded_input)[0].decode()  # Get the output from stdout

    # Process the output
    for e in re.split('[ 	|\n]', output):
        if e != '':
            senna_table.append(e.strip().strip('\t'))

    os.chdir(origin_path)

    result = []
    temp = []

    for ele in senna_table:
        if len(ele) == 0:
            continue
        if ele[-1] != ')' and ele[-1] != '*':
            temp.append(ele)
        else:
            result.append(temp)

            temp = []

    return result


def extract_sentence_index(senna_df: pd.DataFrame):
    end_signs = {'.', '?', '!'}
    sentence_start_index = []

    # Identifying sentences
    for i in range(0, len(senna_df)):
        token = senna_df.iloc[i, 2]
        if token in end_signs or token[-1] == '.':
            while i + 1 < len(senna_df) and senna_df.iloc[i + 1, 2] == '"':
                i += 1
            sentence_start_index.append(i)

    sentence_start_index = [0] + [index + 1 for index in sentence_start_index]
    return sentence_start_index


def check_ner(ner: str, word: str, SVO: dict):
    if ner == 'LOC':
        SVO['LOCATION'].append(word)
    elif ner == 'PER':
        SVO['PERSON'].append(word)


def get_verb_root(verb: str):
    doc = lemmatizer(verb).sentences[-1]
    word = doc.words[-1]
    return word.lemma


def process_verb_obj_obl(sent_len, mapping, df, sent_col, start_index):
    with open(os.path.join(GUI_IO_util.CoreNLP_enhanced_dependencies_libPath, "verb_obj_obl_json.txt")) as f:
        verb_obj_obl = json.load(f)

    verb_index = sent_col.index('S-V') if 'S-V' in sent_col else sent_col.index('B-V')
    verb = df.iloc[verb_index, 2]
    verb = get_verb_root(verb)

    if verb in verb_obj_obl.keys() and verb_index < sent_len - 2:
        for obj_obl in verb_obj_obl[verb]:
            word1, word2 = df.iloc[verb_index + 1, 2], df.iloc[verb_index + 2, 2]
            if obj_obl['obj'] == word1 and obj_obl['obl'] == word2:
                mapping[verb_index + 1] = 'V'
                mapping[verb_index + 2] = 'V'


def process_verb_prep(sent_len, mapping, df, sent_col, start_index):
    with open(os.path.join(GUI_IO_util.CoreNLP_enhanced_dependencies_libPath, "verb_prep_json.txt")) as f:
        verb_prep = json.load(f)

    verb_index = sent_col.index('S-V') if 'S-V' in sent_col else sent_col.index('B-V')
    verb = df.iloc[verb_index, 2]
    verb = get_verb_root(verb)

    for offset in range(sent_len):
        word_index = start_index + offset
        word = df.iloc[word_index, 2]

        if word in verb_prep.keys():
            if verb in verb_prep[word]:
                mapping[word_index] = 'V'


def extract_column_labels(sent_len, SVO, mapping, df, sent_col, start_index):
    for offset in range(sent_len):
        word_index = start_index + offset
        word = df.iloc[word_index, 2]
        word_label = sent_col[offset]

        if word_label != 'O' and (
                word_label.count('-') == 1 or word_label.count('-') > 1 and word_label[-1].isnumeric()):
            last_label = word_label.split('-')[-1]
            mapping.update({word_index: last_label})
        elif word_label[-3:] == 'TMP':
            SVO['TIME'].append(word)
        elif word_label[-3:] == 'NEG' or word.lower() == 'never':
            SVO['NEGATION'].append(word)


def extract_svo(clause, SVO, mapping, df, noun_postag):
    verb_index = [clause.index('V'), ''.join(clause).rindex('V') - 1]

    s_cont_noun, s_has_noun = True, False
    o_cont_noun, o_has_noun = True, False

    # S-V or V-S Structures
    if verb_index[0] == 0 or verb_index[1] == len(clause) - 1:
        for key in mapping.keys():
            word = df.iloc[key, 2]
            postag = df.iloc[key, 3]
            ner = df.iloc[key, 4]
            if mapping[key] != 'V':  # S
                if postag in noun_postag and (not s_has_noun or s_cont_noun):
                    s_has_noun = s_cont_noun = True
                    SVO['S'].append(word)
                else:
                    s_cont_noun = False
                SVO['S(NP)'].append(word)

                check_ner(ner, word, SVO)
            else:  # V
                SVO['V'].append(word)

    # S-V-O or O-V-S Structures
    else:
        try:
            before_verb = int(clause[0][-1])  # Phrase before verb
            after_verb = int(clause[-1][-1])  # Phrase after verb
        except ValueError:
            return
        mapping_keys = list(mapping.keys())

        for key in mapping_keys:
            word = df.iloc[key, 2]
            postag = df.iloc[key, 3]
            ner = df.iloc[key, 4]

            if mapping_keys.index(key) < verb_index[0]:
                if postag in noun_postag:
                    if before_verb > after_verb:  # O
                        if not o_has_noun or o_cont_noun:
                            o_has_noun = o_cont_noun = True
                            SVO['O'].append(word)
                    else:  # S
                        if not s_has_noun or s_cont_noun:
                            s_has_noun = s_cont_noun = True
                            SVO['S'].append(word)
                else:
                    o_cont_noun = s_cont_noun = False
                if before_verb > after_verb:  # O
                    SVO['O(NP)'].append(word)
                else:
                    SVO['S(NP)'].append(word)

                check_ner(ner, word, SVO)
            elif mapping_keys.index(key) > verb_index[1]:
                if postag in noun_postag:
                    if before_verb > after_verb:
                        if not s_has_noun or s_cont_noun:
                            s_has_noun = s_cont_noun = True
                            SVO['S'].append(word)
                    else:
                        if not o_has_noun or o_cont_noun:
                            o_has_noun = o_cont_noun = True
                            SVO['O'].append(word)
                else:
                    s_cont_noun = o_cont_noun = False
                if before_verb > after_verb:
                    SVO['S(NP)'].append(word)
                else:
                    SVO['O(NP)'].append(word)

                check_ner(ner, word, SVO)
            else:
                SVO['V'].append(word)


def convert_to_svo(input_df: pd.DataFrame, output_file_name: str, createExcelCharts: bool, filter_svo: tuple) -> str:
    """
    Converts a csv file with SRL results to SVO results
    :param input_df: a df file with SRL results
    :param output_file_name: the path of the output file
    :param createExcelCharts: whether to create excel charts right after running
    :param filter_svo: a tuple with three strings, each representing a dictionary file for filtering s, v or o
    :return: the path of the output file
    """

    df = input_df
    new_df = pd.DataFrame(
        columns=['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'S(NP)', 'O(NP)', 'PERSON', 'LOCATION',
                 'TIME', 'NEGATION', 'Sentence'])
    document_id, sent_id = 0, 0
    sentence_start_index = extract_sentence_index(df)

    # Iterating each sentence
    for sentence_index in range(len(sentence_start_index) - 1):
        # Retrieving sentence
        start_index, end_index = sentence_start_index[sentence_index], sentence_start_index[sentence_index + 1]
        sentence = ' '.join(df.iloc[start_index:end_index, 2]) + ' '
        sent_id = 1 if document_id != df.iloc[start_index, 0] else sent_id
        document_id = df.iloc[sentence_start_index[sentence_index], 0]

        # Iterating each column (the first 4 rows are irrelevant)
        for col_index in range(4, len(df.columns)):
            # Result dict
            SVO = {'S': [], 'V': [], 'O': [], 'PERSON': [], 'LOCATION': [], 'TIME': [], 'NEGATION': [], 'S(NP)': [],
                   'O(NP)': []}
            noun_postag = {'PRP', 'NN', 'NNS', 'NNP', 'WP'}

            sent_col = list(df.iloc[start_index:end_index, col_index])
            sent_len = len(sent_col)
            mapping = {}

            # Adding {row_index: label} to mapping
            extract_column_labels(sent_len, SVO, mapping, df, sent_col, start_index)

            # Extracting SVO
            if mapping:
                clause = list(mapping.values())

                # Extract only if verb exists
                if 'V' in clause and len(clause) > 1:
                    if os.path.exists(os.path.join(GUI_IO_util.CoreNLP_enhanced_dependencies_libPath, "verb_obj_obl_json.txt")):
                        process_verb_obj_obl(sent_len, mapping, df, sent_col, start_index)
                    if os.path.exists(os.path.join(GUI_IO_util.CoreNLP_enhanced_dependencies_libPath, "verb_prep_json.txt")):
                        process_verb_prep(sent_len, mapping, df, sent_col, start_index)
                        clause = list(mapping.values())  # update clause since mapping has been updated
                    extract_svo(clause, SVO, mapping, df, noun_postag)

            for key in mapping.keys():
                df.iloc[key, col_index] = mapping[key]

            # Append new row to new df
            if SVO['V']:
                SVO['S'] = ' '.join(SVO['S'])
                SVO['V'] = ' '.join(SVO['V'])
                SVO['O'] = ' '.join(SVO['O'])
                SVO['PERSON'] = ', '.join(SVO['PERSON'])
                SVO['LOCATION'] = ', '.join(SVO['LOCATION'])
                SVO['TIME'] = ' '.join(SVO['TIME'])
                SVO['NEGATION'] = ', '.join(SVO['NEGATION'])
                SVO['S(NP)'] = ' '.join(SVO['S(NP)'])
                SVO['O(NP)'] = ' '.join(SVO['O(NP)'])
                # print(SVO)

                formatted_input_file_name = IO_csv_util.dressFilenameForCSVHyperlink(df.iloc[sentence_index, 1])
                new_row = pd.DataFrame(
                    [[document_id, sent_id, formatted_input_file_name, SVO['S'], SVO['V'], SVO['O'], SVO['S(NP)'],
                      SVO['O(NP)'], SVO['PERSON'], SVO['LOCATION'], SVO['TIME'], SVO['NEGATION'], sentence]],
                    columns=['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'S(NP)', 'O(NP)', 'PERSON',
                             'LOCATION', 'TIME', 'NEGATION', 'Sentence'])
                new_df = new_df.append(new_row, ignore_index=True)
        sent_id += 1

    if createExcelCharts:
        new_df.to_csv(output_file_name, index=False)

    return output_file_name


if __name__ == '__main__':
    dir_name = ''
    file_name = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/test.txt'
    output_dir = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/'
    run_senna(file_name, dir_name, output_dir, openOutputFiles=False, createExcelCharts=False)
    # get_verb_root('taking')