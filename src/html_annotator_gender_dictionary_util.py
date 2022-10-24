import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_packages(GUI_util.window,"Stanford_CoreNLP_clause_util",['tkinter','pandas','stanza']):
    sys.exit(0)

import os
import pandas as pd
from tkinter import messagebox as mb
from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
import csv

import GUI_IO_util
import IO_files_util
import IO_csv_util
import Stanford_CoreNLP_util

# put the script of generate two big csvs into this file


def text_generate(inputFilename, inputDir):
    articles = []
    if inputFilename == '':
        for folder, subs, files in os.walk(inputDir):
            print("\nProcessing folder: ",os.path.basename(os.path.normpath(folder)))
            for filename in files:
                if not filename.endswith('.txt'):
                    continue
                print("  Processing file:",filename)
                with open(os.path.join(folder, filename), 'r', encoding='utf-8', errors='ignore') as src:
                    text = src.read().replace("\n", " ")
                # sentences = tokenize.sent_tokenize(text)
                sentences = sent_tokenize_stanza(stanzaPipeLine(text))
                # articles.append([sentences, filename])
                articles.append([sentences, IO_csv_util.dressFilenameForCSVHyperlink(filename)])
                # name, sentence, sentenceID, documentID, documentName

    else:
        inputDir = inputFilename
        if not inputFilename.endswith('.txt'):
            mb.showwarning('Input File Error', 'The file selected is not a txt file. Please check again.')
        else:
            with open(inputFilename,  'r', encoding='utf-8', errors='ignore') as src:
                text = src.read().replace("\n", " ")
            # sentences = tokenize.sent_tokenize(text)
            sentences = sent_tokenize_stanza(stanzaPipeLine(text))
            articles.append([sentences, inputFilename])
    return articles, inputDir


def dictionary_annotate(config_filename, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, memory_var, dictionary_file, personal_pronouns_var):

    document_length_var = 90000
    limit_sentence_length_var = 100
    extract_date_from_text_var = False
    extract_date_from_filename_var = False
    date_format = ''
    date_separator_var = ''
    date_position_var = ''

    tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                        openOutputFiles, createCharts, chartPackage,
                                                        'NER',
                                                        NERs=['PERSON'],
                                                        DoCleanXML=False,
                                                        memory_var=memory_var,
                                                        document_length=document_length_var,
                                                        sentence_length=limit_sentence_length_var,
                                                        dateExtractedFromFileContent=extract_date_from_text_var,
                                                        filename_embeds_date_var=extract_date_from_filename_var,
                                                        date_format=date_format,
                                                        date_separator_var=date_separator_var,
                                                        date_position_var=date_position_var)

    if len(tempOutputFiles)==0:
        return tempOutputFiles
    else:
        NER_fileName = tempOutputFiles[0]
        with open(NER_fileName,encoding='utf-8',errors='ignore') as infile:
            reader = csv.reader(x.replace('\0', '') for x in infile)
            headers = next(reader)
        header_indices = [i for i, item in enumerate(headers) if item]
        ners = pd.read_csv(NER_fileName, usecols=[0,1],encoding='utf-8')

    articles, inputDir = text_generate(inputFilename, inputDir)

    people = []
    for article_num, article in enumerate(articles):
        for sentence_num, sentence in enumerate(article[0]):
                for ner in ners:
                    if ner[1] == 'PERSON':
                        people.append([ner[0], sentence, sentence_num + 1, article_num + 1, article[1]])
                if personal_pronouns_var:
                    # tokens = word_tokenize(sentence)
                    tokens = word_tokenize_stanza(stanzaPipeLine(sentence))
                    for token in tokens:
                        if token in ['his','His','He','he','Him','him']:
                            people.append([token, 'Male', sentence, sentence_num+1,article_num+1,article[1]])
                        if token in ['She','she','Her','her']:
                            people.append([token, 'Female', sentence, sentence_num+1,article_num+1,article[1]])

    dict_df = pd.read_csv(dictionary_file)
    for person in people:
        if len(person) == 5:
            temp = dict_df[dict_df['Name'] == person[0]]['Gender']
            if temp.empty:
                gender = 'Not Found'
            else:
                gender = temp.values[0]
            person.insert(1, gender)
            print(person)
    annotated = pd.DataFrame(people,columns=['Name','Gender','Sentence','SentenceID','DocumentID','Document'])
    output_dir = IO_files_util.generate_output_file_name('',inputDir, outputDir, '.csv', 'gender', 'annotated')
    annotated.to_csv(output_dir, encoding='utf-8')
    return tempOutputFiles


def SSA_annotate(year_state_var,firstName_entry_var,outputDir):
    if year_state_var!= 'Year of birth':
        return
        df1 = pd.read_csv(GUI_IO_util.namesGender_libPath + os.sep + 'SS_state_year.csv')
        target1 = df1[df1['Name'] == firstName_entry_var]
    df2 = pd.read_csv(GUI_IO_util.namesGender_libPath + os.sep + 'SS_yearOfBirth.csv')
    target2 = df2[df2['Name'] == firstName_entry_var]
    if year_state_var == 'State':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1 = target1.drop(columns=['Year'])
        group1 = target1.groupby(['State', 'Gender']).sum()
        group1.insert(0, 'Name', firstName_entry_var)
        group1.reset_index().to_csv(output_path, encoding='utf-8', index=False)
        return [output_path]
    elif year_state_var == 'Year':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1 = target1.drop(columns=['State'])
        group1 = target1.groupby(['Year', 'Gender']).sum()
        group1.insert(0, 'Name', firstName_entry_var)
        group1.reset_index().to_csv(output_path, encoding='utf-8', index=False)
        return [output_path]
    elif year_state_var == 'State & Year':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1.to_csv(output_path, encoding='utf-8', index=False)
        return [output_path]
    elif year_state_var == 'Year of birth':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target2.to_csv(output_path, encoding='utf-8', index=False)
        return [output_path]
    else:
        output_path1 = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															   firstName_entry_var,'state_year')
        output_path2 = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															   firstName_entry_var,'yob')
        target1.to_csv(output_path1,encoding='utf-8', index=False)
        target2.to_csv(output_path2,encoding='utf-8', index=False)
        return [output_path1, output_path2]

def build_dictionary_yob(source_file_path):
    result = []
    for folder, subs, files in os.walk(source_file_path):
        for filename in files:
            if filename.endswith('.txt') == False and filename.endswith('.TXT') == False:
                continue
            with open(os.path.join(folder, filename), 'r', encoding='utf-8', errors='ignore') as src:
                text = src.read().replace("\n", " ")
                temp = list(text.split(' '))
                for elmt in temp:
                    if elmt == ' ':
                        continue
                    temp_list = list(elmt.split(','))
                    yob = filename.split('.')[0][3:]
                    temp_list.append(yob)
                    result.append(temp_list)
    source_name = source_file_path.split('/')[-1]
    df = pd.DataFrame(result, columns=['Name', 'Gender', 'Frequency', 'YearOfBirth'])
    if os.path.exists('../lib/namesGender/SS_yearOfBirth.csv'):
        os.remove('../lib/namesGender/SS_yearOfBirth.csv')
    df.to_csv('../lib/namesGender'+os.sep+'SS_yearOfBirth.csv', encoding='utf-8', index=False)


def build_dictionary_state_year(source_file_path):
    result = []
    for folder, subs, files in os.walk(source_file_path):
        for filename in files:
            if filename.endswith('.TXT') == False and filename.endswith('.txt') == False:
                continue
            else:
                with open(os.path.join(folder, filename), 'r', encoding='utf-8', errors='ignore') as src:
                    text = src.read().replace("\n", " ")
                    temp = list(text.split(' '))
                    for elmt in temp:
                        if elmt == ' ':
                            continue
                        temp_list = list(elmt.split(','))
                        result.append(temp_list)
    source_name = source_file_path.split('/')[-1]
    df = pd.DataFrame(result, columns=['State', 'Gender', 'Year', 'Name', 'Frequency'])
    if os.path.exists('../lib/namesGender/SS_state_year.csv'):
        os.remove('../lib/namesGender/SS_state_year.csv')
    df.to_csv('../lib/namesGender' + os.sep + 'SS_state_year.csv', encoding='utf-8', index=False)


def get_date():
    df = pd.read_csv('../lib/namesGender/SS_state_year.csv')
    lastest_date = df.iloc[-2]['Year']
    return int(lastest_date)
