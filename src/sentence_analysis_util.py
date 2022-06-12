import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "sentence_analysis_util",
										  ['nltk', 'csv', 'tkinter', 'os', 'collections', 'subprocess', 'textstat',
										   'itertools', 'ast']) == False:
	sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
import collections
from collections import Counter
import os
import csv
import nltk
# from nltk import tokenize
# from nltk import word_tokenize
from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
# from gensim.utils import lemmatize
from itertools import groupby
import pandas as pd
import ast
import textstat
import subprocess
import spacy
from nltk.tree import Tree
from nltk.draw import TreeView
from PIL import Image

# Sentence Complexity
import tree
import node_sentence_complexity as Node
import stanza

import charts_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_util
import statistics_csv_util
import TIPS_util
import GUI_IO_util


def Extract(lst):
	return [item[0] for item in lst]

def dictionary_items_bySentenceID(window, inputFilename, inputDir, outputDir, createCharts, chartPackage, openOutputFiles=True,
								  input_dictionary_file='', chartTitle=''):
	filesToOpen = []
	DictionaryList = []
	file_list = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
	nFile = len(file_list)
	if nFile == 0:
		return
	# when running the function w/o a GUI, as currently is mostly the case,
	#   we would not be able to pass a dictionary file to the function
	if input_dictionary_file == '':
		initialFolder = os.path.dirname(os.path.abspath(__file__))
		input_dictionary_file = tk.filedialog.askopenfilename(title="Select dictionary csv file",
															  initialdir=initialFolder,
															  filetypes=[("csv files", "*.csv")])
		if len(input_dictionary_file) == 0:
			return

	if IO_csv_util.get_csvfile_numberofColumns(input_dictionary_file) == 2:
		dic = pd.read_csv(input_dictionary_file)
		dic_value = dic.iloc[:, 0].tolist()
		dic_sec_value = dic.iloc[:, 1].tolist()
		dic = [(dic_value[i], dic_sec_value[i]) for i in range(len(dic_value))]
		if chartTitle == '':
			chartTitle = "Dictionary value"
		documentID = 0
		container = []
		for file in file_list:
			documentID += 1
			head, tail = os.path.split(file)
			print("Processing file ", str(documentID), "\\", str(nFile), tail)
			text = (open(file, "r", encoding="utf-8", errors='ignore').read())
			# Process each word in txt
			Sentence_ID = 0
			# sentences = tokenize.sent_tokenize(text)
			sentences = sent_tokenize_stanza(stanzaPipeLine(text))
			# word  frequency sentenceID DocumentID FileName
			for each_sentence in sentences:
				In = []
				Sentence_ID += 1
				# token=nltk.word_tokenize(each_sentence)
				token = word_tokenize_stanza(stanzaPipeLine(each_sentence))
				for word in token:
					for dict_word in dic:
						if word == dict_word[0].rstrip():
							In.append([word, dict_word[1], Sentence_ID, each_sentence, documentID, file])
							break
						else:
							continue
				container.extend(In)

			ctr = collections.Counter(Extract(container))
			for word in container:
				word.insert(2, ctr.get(word[0]))
			for word in container:
				if word[0] not in Extract(DictionaryList):
					DictionaryList.append(word)

			DictionaryList.insert(0, ['Dict_value', 'Dict_second_value', 'Frequency', 'Sentence ID', 'Sentence',
									  'Document ID', 'Document'])
	else:
		dic = pd.read_csv(input_dictionary_file)
		dic_value = dic.iloc[:, 0].tolist()
		if chartTitle == '':
			chartTitle = "Dictionary value"
		documentID = 0
		container = []
		for file in file_list:
			documentID += 1
			head, tail = os.path.split(file)
			print("Processing file ", str(documentID), "\\", str(nFile), tail)
			text = (open(file, "r", encoding="utf-8", errors='ignore').read())
			# Process each word in txt
			Sentence_ID = 0
			# sentences = tokenize.sent_tokenize(text)
			sentences = sent_tokenize_stanza(stanzaPipeLine(text))
			# word  frequency sentenceID DocumentID FileName
			for each_sentence in sentences:
				In = []
				Sentence_ID += 1
				# token = nltk.word_tokenize(each_sentence)
				token = word_tokenize_stanza(stanzaPipeLine(each_sentence))
				for word in token:
					for dict_word in dic_value:
						if word == dict_word.rstrip():
							In.append([word, Sentence_ID, each_sentence, documentID, IO_csv_util.undressFilenameForCSVHyperlink(file)])
							break
						else:
							continue
				container.extend(In)

			ctr = collections.Counter(Extract(container))
			for word in container:
				word.insert(1, ctr.get(word[0]))
			for word in container:
				if word[0] not in Extract(DictionaryList):
					DictionaryList.append(word)

			DictionaryList.insert(0, ['Dict_value', 'Frequency', 'Sentence ID', 'Sentence',
									  'Document ID', 'Document'])

		outputFilename = IO_files_util.generate_output_file_name(file, inputDir, outputDir, '.csv',
																 str(Sentence_ID) + '-Dict_value', 'stats', '', '', '',
																 False, True)
		filesToOpen.append(outputFilename)
		IO_csv_util.list_to_csv(window, DictionaryList, outputFilename)
		outputFilename = IO_files_util.generate_output_file_name(file, inputDir, outputDir, '.xlsx',
																 str(Sentence_ID) + '-Dict_value', 'chart', '', '', '',
																 False, True)
		filesToOpen.append(outputFilename)
		charts_Excel_util.create_excel_chart(GUI_util.window, [DictionaryList], outputFilename, chartTitle, ["bar"])

	if openOutputFiles == True:
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)


# written by Yi Wang April 2020
# ConnlTable is the inputFilename
def Wordnet_bySentenceID(ConnlTable, wordnetDict, outputFilename, outputDir, noun_verb, openOutputFiles,
						 createCharts, chartPackage):
	filesToOpen = []
	startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
												   'Started running WordNet charts by sentence index at',
												   True, '', True, '', False)

	if noun_verb == 'NOUN':
		checklist = ['NN', 'NNP', 'NNPS', 'NNS']
	else:
		checklist = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
	# read in the CoreNLP CoNLL table
	connl = pd.read_csv(ConnlTable)
	# read in the dictionary file to be used to filter CoNLL values
	# The file is expected to have 2 columns with headers: Word, WordNet Category
	try:
		dict = pd.read_csv(wordnetDict)
	except:
		mb.showwarning("Warning",
					   "The file \n\n" + wordnetDict + "\n\ndoes not have the expected 2 columns: Word, WordNet Category. You may have selected the wrong input file.\n\nPlease, select the right input file and try again.")
		return
	# set up the double list conll from the conll data
	try:
		connl = connl[['Form', 'Lemma', 'POStag', 'Sentence ID', 'Document ID', 'Document']]
	except:
		mb.showwarning("Warning",
					   "The file \n\n" + ConnlTable + "\n\ndoes not appear to be a CoNLL table with expected column names: Form,Lemma,Postag, SentenceID, DocumentID, Document.\n\nPlease, select the right input file and try again.")
		return
	# filter the list by noun or verb
	connl = connl[connl['Postag'].isin(checklist)]
	# eliminate any duplicate value in Word (Form))
	dict = dict.drop_duplicates().rename(columns={'Word': 'Lemma', 'WordNet Category': 'Category'})
	# ?
	connl = connl.merge(dict, how='left', on='Lemma')
	# the CoNLL table value is not found in the dictionary Word value
	connl.fillna('Not in INPUT dictionary for ' + noun_verb, inplace=True)
	# add the WordNet category to the conll list
	connl = connl[['Form', 'Lemma', 'POStag', 'Category', 'Sentence ID', 'Document ID', 'Document']]
	# put headers on conll list
	connl.columns = ['Form', 'Lemma', 'POStag', 'Category', 'Sentence ID', 'Document ID', 'Document']

	Row_list = []
	# Iterate over each row
	for index, rows in connl.iterrows():
		# Create list for the current row
		my_list = [rows.word, rows.lemma, rows.postag, rows.Category, rows.SentenceID, rows.DocumentID, rows.Document]
		# append the list to the final list
		Row_list.append(my_list)
	for index, row in enumerate(Row_list):
		if index == 0 and Row_list[index][4] != 1:
			for i in range(Row_list[index][4] - 1, 0, -1):
				Row_list.insert(0, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
		else:
			if index < len(Row_list) - 1 and Row_list[index + 1][4] - Row_list[index][4] > 1:
				for i in range(Row_list[index + 1][4] - 1, Row_list[index][4], -1):
					Row_list.insert(index + 1, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
	df = pd.DataFrame(Row_list,
					  index=['Form', 'Lemma', 'POStag', 'WordNet Category', 'Sentence ID', 'Document ID', 'Document'])
	df = charts_Excel_util.add_missing_IDs(df)
	df.to_csv(outputFilename, index=False)

	if createCharts:
		outputFiles = statistics_csv_util.compute_csv_column_frequencies(GUI_util.window,
																	   ConnlTable,
																	   df,
																	   outputDir,
																	   openOutputFiles,
																	   createCharts,
																	   chartPackage,
																	   [[4, 5]],
																	   ['WordNet Category'], ['Form'],
																	   ['Sentence ID', 'Document ID', 'Document'],
																	   )
		if len(outputFiles) > 0:
			filesToOpen.extend(outputFiles)
	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
									   'Finished running WordNet charts by sentence index at', True, '', True,
									   startTime)

	return filesToOpen