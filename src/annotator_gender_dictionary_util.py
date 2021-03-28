import sys
import GUI_util
import IO_libraries_util

if not IO_libraries_util.install_all_packages(GUI_util.window,"Stanford_CoreNLP_clause_util",['tkinter','nltk','time','pandas','stanfordcorenlp','subprocess']):
    sys.exit(0)

import subprocess
import time
import os
import pandas as pd
from tkinter import messagebox as mb
from stanfordcorenlp import StanfordCoreNLP
from nltk import tokenize
IO_libraries_util.import_nltk_resource(GUI_util.window,'tokenizers/punkt','punkt')

import GUI_IO_util
import IO_files_util
import IO_csv_util
import IO_csv_util


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
                sentences = tokenize.sent_tokenize(text)
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
            sentences = tokenize.sent_tokenize(text)
            articles.append([sentences, inputFilename])
    return articles, inputDir


def dictionary_annotate(inputFilename, inputDir, outputDir, dictionary_file, personal_pronouns_var):
    fileToOpen=[]
    CoreNLPdir = IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_coreference_util', 'Stanford CoreNLP')
    p = subprocess.Popen(
        ['java', '-mx' + str(5) + "g", '-cp', os.path.join(CoreNLPdir, '*'),
         'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    time.sleep(5)
    nlp = StanfordCoreNLP('http://localhost', port=9000)

    articles, inputDir = text_generate(inputFilename, inputDir)

    people = []
    for article_num, article in enumerate(articles):
        for sentence_num, sentence in enumerate(article[0]):
                ners = nlp.ner(sentence)
                for ner in ners:
                    if ner[1] == 'PERSON':
                        people.append([ner[0], sentence, sentence_num + 1, article_num + 1, article[1]])
                if personal_pronouns_var:
                    tokens = nlp.word_tokenize(sentence)
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
    annotated.to_csv(output_dir)
    p.kill()
    return fileToOpen




def SSA_annotate(year_state_var,firstName_entry_var,outputDir):
    df1 = pd.read_csv(GUI_IO_util.namesGender_libPath + os.sep + 'SS_state_year.csv')
    df2 = pd.read_csv(GUI_IO_util.namesGender_libPath + os.sep + 'SS_yearOfBirth.csv')
    target1 = df1[df1['Name'] == firstName_entry_var]
    target2 = df2[df2['Name'] == firstName_entry_var]
    if year_state_var == 'State':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1 = target1.drop(columns=['Year'])
        group1 = target1.groupby(['State', 'Gender']).sum()
        group1.insert(0, 'Name', firstName_entry_var)
        group1.reset_index().to_csv(output_path, index=False)
        return [output_path]
    elif year_state_var == 'Year':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1 = target1.drop(columns=['State'])
        group1 = target1.groupby(['Year', 'Gender']).sum()
        group1.insert(0, 'Name', firstName_entry_var)
        group1.reset_index().to_csv(output_path, index=False)
        return [output_path]
    elif year_state_var == 'State & Year':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target1.to_csv(output_path, index=False)
        return [output_path]
    elif year_state_var == 'Year of birth':
        output_path = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															  firstName_entry_var)
        target2.to_csv(output_path, index=False)
        return [output_path]
    else:
        output_path1 = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															   firstName_entry_var,'state_year')
        output_path2 = IO_files_util.generate_output_file_name('', '', outputDir, '.csv', year_state_var,
															   firstName_entry_var,'yob')
        target1.to_csv(output_path1,index=False)
        target2.to_csv(output_path2,index=False)
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
    df.to_csv('../lib/namesGender'+os.sep+'SS_yearOfBirth.csv', index=False)


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
    df.to_csv('../lib/namesGender' + os.sep + 'SS_state_year.csv', index=False)


def get_date():
    df = pd.read_csv('../lib/namesGender/SS_state_year.csv')
    lastest_date = df.iloc[-2]['Year']
    return int(lastest_date)