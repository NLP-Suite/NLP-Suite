import os
import platform
import re
import subprocess

import GUI_IO_util
import GUI_util
import IO_files_util
import IO_libraries_util
import IO_user_interface_util
import pandas as pd
import IO_csv_util


def check_system():
    system = platform.system().lower()
    if "linux" in system:
        return "linux"
    elif system == "windows":
        return "win"
    elif system == "darwin":
        return "mac"


def run_senna(inputFilename=None, inputDir=None, outputDir=None, openOutputFiles=False, createExcelCharts=False) -> list:
    """
    Run the senna-osx with input type either file or directory
    :param inputFilename: name of the input text file
    :param inputDir: name of the input directory
    :param outputDir: name of the output file
    :return:
    """
    formatted_table = []
    document_lengths = []
    filesToOpen = []
    doc_id = 0

    # check that the SENNA dir as been setup
    SENNAdir = IO_libraries_util.get_external_software_dir('SVO SENNA', 'SENNA')
    if SENNAdir == None:
        return filesToOpen

    # record the time consumption before annotating text in each file
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
                                       'Started running SENNA to extract SVOs at', True,
                                       'You can follow SENNA in command line.')

    SENNA_output_file_name = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                     'SENNA_SVO')
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

    max_length = max([len(row) for row in formatted_table])

    document_index = 0

    for index, row in enumerate(formatted_table):
        while len(row) < max_length:
            row.append('O')
        row.insert(0, document_index + 1)
        if index == document_lengths[document_index] - 1:
            document_index += 1

    senna_df = pd.DataFrame(formatted_table, columns=['Col %s' % i for i in range(len(formatted_table[0]))])

    convert_to_svo(senna_df, SENNA_output_file_name, createExcelCharts)
    filesToOpen.append(SENNA_output_file_name)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running SENNA to extract SVOs at', True)
    return filesToOpen


def senna_single_file(SENNAdir, inputFilename: str) -> list:
    """
    Run senna-osx using the input from the inputFilename
    :param inputFilename: the name of a text file
    :return: a list of lists where each list is a row in the output senna table
    """
    senna_table = []

    # Read the input file
    with open(inputFilename, 'r') as file:
        input_text = file.read().strip()
        file.close()
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
    cmd = subprocess.Popen([senna_exec, '-pos', '-srl', '-psg'], stdin=subprocess.PIPE,
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


def convert_to_svo(input_df: pd.DataFrame, output_file_name: str, createExcelCharts: bool) -> str:
    """
    Converts a csv file with SRL results to SVO results
    :param input_df: a df file with SRL results
    :param output_file_name: the path of the output file
    :return:
    """
    end_signs = {'.', '?', '!'}

    sentence_start_index = []
    df = input_df
    new_df = pd.DataFrame(columns=['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'TIME', 'Sentence'])
    document_id, sent_id = 0, 0

    # Identifying sentences
    for i in range(0, len(df)):
        token = df.iloc[i, 2]
        if token in end_signs or token[-1] == '.':
            while i + 1 < len(df) and df.iloc[i + 1, 2] == '"':
                i += 1
            sentence_start_index.append(i)

    sentence_start_index = [index + 1 for index in sentence_start_index]
    sentence_start_index = [0] + sentence_start_index

    # Iterating each sentence
    for a in range(len(sentence_start_index) - 1):
        sentence = ' '.join(df.iloc[sentence_start_index[a]:sentence_start_index[a + 1], 2]) + ' '
        sent_id = 1 if document_id != df.iloc[sentence_start_index[a], 0] else sent_id
        document_id = df.iloc[sentence_start_index[a], 0]

        # Iterating each column
        for i in range(4, len(df.iloc[1, :])):
            SVO = {'S': [], 'V': [], 'O': [], 'LOCATION': [], 'TIME': []}
            noun_postag = {'PRP', 'NN', 'NNS', 'NNP', 'WP'}

            sent_col = df.iloc[sentence_start_index[a]:sentence_start_index[a + 1], i]
            sent_col = sent_col.tolist()
            mapping = {}

            # Adding {row_index: label} to mapping
            for j in range(len(sent_col)):
                if sent_col[j] != 'X' and sent_col[j] != 'O' and (
                        sent_col[j].count('-') == 1 or sent_col[j].count('-') > 1 and sent_col[j][-1].isnumeric()):
                    label = sent_col[j].split('-')[-1]
                    mapping.update({sentence_start_index[a] + j: label})
                elif sent_col[j][-3:] == 'LOC':
                    SVO['LOCATION'].append(df.iloc[sentence_start_index[a] + j, 2])
                elif sent_col[j][-3:] == 'TMP':
                    SVO['TIME'].append(df.iloc[sentence_start_index[a] + j, 2])

            # Converting signs to '--S--', '--V--' and '--O--'
            temp = {}  # {col_index: converted signs} for this sentence

            # Filling in temp
            for j in range(len(sent_col)):
                if j + sentence_start_index[a] in mapping.keys():
                    temp.update({j + sentence_start_index[a]: mapping[j + sentence_start_index[a]]})

            if temp:
                clause = list(temp.values())

                if 'V' in clause and len(clause) > 1:
                    verb_index = [clause.index('V'), clause.index('V') + clause.count('V') - 1]
                    s_cont_noun, s_has_noun = True, False
                    o_cont_noun, o_has_noun = True, False
                    # S-V or V-S Structures
                    if verb_index[0] == 0 or verb_index[1] == len(clause) - 1:
                        for key in temp.keys():
                            word = df.iloc[key, 2]
                            postag = df.iloc[key, 3]
                            if temp[key] != 'V':    # S
                                if postag in noun_postag and (not s_has_noun or s_cont_noun):
                                    s_has_noun = s_cont_noun = True
                                    SVO['S'].append(word)
                                    SVO.update({'S': SVO['S']})
                                else:
                                    s_cont_noun = False
                            else:      # V
                                SVO['V'].append(word)
                                SVO.update({'V': SVO['V']})

                    # S-V-O or O-V-S Structures
                    else:
                        try:
                            before_verb = int(clause[0][-1])  # Phrase before verb
                            after_verb = int(clause[-1][-1])  # Phrase after verb
                        except ValueError:
                            continue
                        temp_keys = list(temp.keys())
                        # Replacing the labels
                        for key in temp_keys:
                            word = df.iloc[key, 2]
                            postag = df.iloc[key, 3]

                            if temp_keys.index(key) < verb_index[0]:
                                if postag in noun_postag:
                                    if before_verb > after_verb:   # O
                                        if not o_has_noun or o_cont_noun:
                                            o_has_noun = o_cont_noun = True
                                            SVO['O'].append(word)
                                            SVO.update({'O': SVO['O']})
                                    else:   # S
                                        if not s_has_noun or s_cont_noun:
                                            s_has_noun = s_cont_noun = True
                                            SVO['S'].append(word)
                                            SVO.update({'S': SVO['S']})
                                else:
                                    o_cont_noun = s_cont_noun = False
                            elif temp_keys.index(key) > verb_index[1]:
                                if postag in noun_postag:
                                    if before_verb > after_verb:
                                        if not s_has_noun or s_cont_noun:
                                            s_has_noun = s_cont_noun = True
                                            SVO['S'].append(word)
                                            SVO.update({'S': SVO['S']})
                                    else:
                                        if not o_has_noun or o_cont_noun:
                                            o_has_noun = o_cont_noun = True
                                            SVO['O'].append(word)
                                            SVO.update({'O': SVO['O']})
                                else:
                                    s_cont_noun = o_cont_noun = False
                            else:
                                SVO['V'].append(word)
                                SVO.update({'V': SVO['V']})

            for key in temp.keys():
                df.iloc[key, i] = temp[key]

            # Append new row to new df
            if SVO['V']:
                SVO['S'] = ' '.join(SVO['S'])
                SVO['V'] = ' '.join(SVO['V'])
                SVO['O'] = ' '.join(SVO['O'])
                SVO['LOCATION'] = ' '.join(SVO['LOCATION'])
                SVO['TIME'] = ' '.join(SVO['TIME'])

                formatted_input_file_name = IO_csv_util.dressFilenameForCSVHyperlink(df.iloc[a, 1])
                new_row = pd.DataFrame(
                    [[document_id, sent_id, formatted_input_file_name, SVO['S'], SVO['V'], SVO['O'],
                      SVO['LOCATION'], SVO['TIME'], sentence]],
                    columns=['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'TIME', 'Sentence'])
                new_df = new_df.append(new_row, ignore_index=True)

        sent_id += 1

    if createExcelCharts:
        new_df.to_csv(output_file_name, index=False)
    return output_file_name


if __name__ == '__main__':
    dir_name = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/SRL/test'
    file_name = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/SRL/test.txt'
    output_dir = '/Users/admin/Desktop/EMORY/Academics/Spring_2021/SOC497R/'
    run_senna(inputDir=dir_name, outputDir=output_dir, openOutputFiles=True, createExcelCharts=True)
