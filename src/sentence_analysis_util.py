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

import charts_Excel_util
import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_Excel_util
import charts_plotly_util
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
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# written by Yi Wang April 2020
# ConllTable is the inputFilename
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
		outputFiles = charts_Excel_util.compute_csv_column_frequencies(GUI_util.window,
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


# def compute_sentence_length(inputFilename, inputDir, outputDir):
# 	inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
# 	Ndocs = len(inputDocs)
# 	if Ndocs == 0:
# 		return
# 	startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
# 												   'Started running sentence length algorithm at',
# 												   True, '', True, '', False)

# 	fileID = 0
# 	long_sentences = 0
# 	outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
# 															 'sentence_length')
# 	csv_headers = ['Sentence length (in words)', 'Sentence ID', 'Sentence', 'Document ID', 'Document']

# 	with open(outputFilename, 'w', newline="", encoding='utf-8', errors='ignore') as csvOut:
# 		writer = csv.writer(csvOut)
# 		writer.writerow(csv_headers)
# 		for doc in inputDocs:
# 			sentenceID = 0
# 			fileID = fileID + 1
# 			head, tail = os.path.split(doc)
# 			print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
# 			with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
# 				text = inputFile.read().replace("\n", " ")
# 				# sentences = tokenize.sent_tokenize(text)
# 				sentences = sent_tokenize_stanza(stanzaPipeLine(text))
# 				for sentence in sentences:
# 					# tokens = nltk.word_tokenize(sentence)
# 					tokens = word_tokenize_stanza(stanzaPipeLine(sentence))
# 					if len(tokens) > 100:
# 						long_sentences = long_sentences + 1
# 					sentenceID = sentenceID + 1
# 					writer.writerow(
# 						[len(tokens), sentenceID, sentence, fileID, IO_csv_util.dressFilenameForCSVHyperlink(doc)])
# 		csvOut.close()
# 		answer = tk.messagebox.askyesno("TIPS file on memory issues", str(Ndocs) + " file(s) processed in input.\n\n" +
# 										"Output csv file written to the output directory " + outputDir + "\n\n" +
# 										str(
# 											long_sentences) + " SENTENCES WERE LONGER THAN 100 WORDS (the average sentence length in modern English is 20 words).\n\nMore to the point... Stanford CoreNLP would heavily tax memory resources with such long sentences.\n\nYou should consider editing these sentences if Stanford CoreNLP takes too long to process the file or runs out of memory.\n\nPlease, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nDo you want to open the TIPS file now?")
# 		if answer:
# 			TIPS_util.open_TIPS('TIPS_NLP_Stanford CoreNLP memory issues.pdf')
# 	return [outputFilename]

# # wordList is a string
# def extract_sentences(window, inputFilename, inputDir, outputDir, inputString):
# 	filesToOpen=[]
# 	inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
# 	Ndocs = len(inputDocs)
# 	if Ndocs == 0:
# 		return

# 	# Win/Mac may use different quotation, we replace any directional quotes to straight ones
# 	right_double = u"\u201C"  # “
# 	left_double = u"\u201D"  # ”
# 	straight_double = u"\u0022"  # "
# 	if (right_double in inputString) or (left_double in inputString):
# 		inputString = inputString.replace(right_double, straight_double)
# 		inputString = inputString.replace(left_double, straight_double)
# 	if inputString.count(straight_double) == 2:
# 		# Append ', ' to the end of search_words_var so that literal_eval creates a list
# 		inputString += ', '
# 	# convert the string inputString to a list []
# 	def Convert(inputString):
# 		wordList = list(inputString.split(","))
# 		return wordList

# 	wordList = Convert(inputString)

# 	# wordList = ast.literal_eval(inputString)
# 	# print('wordList',wordList)
# 	# try:
# 	# 	wordList = ast.literal_eval(inputString)
# 	# except:
# 	# 	mb.showwarning(title='Search error',message='The search function encountered an error. If you have entered multi-word expressions (e.g. beautiful girl make sure to enclose them in double quotes "beautiful girl"). Also, make sure to separate single-word expressions, with a comma (e.g., go, come).')
# 	# 	return
# 	caseSensitive = mb.askyesno("Python", "Do you want to process your search word(s) as case sensitive?")

# 	if inputFilename!='':
# 		inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
# 		outputDir_sentences = os.path.join(outputDir, "sentences_" + inputFileBase)
# 	else:
# 		# processing a directory
# 		inputDirBase = os.path.basename(inputDir)
# 		outputDir_sentences = os.path.join(outputDir, "sentences_Dir_" + inputDirBase)

# 	# create a subdirectory in the output directory
# 	outputDir_sentences_extract = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract', silent=True)
# 	if outputDir_sentences_extract == '':
# 		return
# 	outputDir_sentences_extract_minus = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='extract_minus', silent=True)
# 	if outputDir_sentences_extract_minus == '':
# 		return

# 	startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
# 												   'Started running the Word search function at',
# 												   True, '', True)

# 	fileID = 0
# 	file_extract_written = False
# 	file_extract_minus_written = False
# 	nDocsExtractOutput = 0
# 	nDocsExtractMinusOutput = 0

# 	for doc in inputDocs:
# 		wordFound = False
# 		fileID = fileID + 1
# 		head, tail = os.path.split(doc)
# 		print("Processing file " + str(fileID) + "/" + str(Ndocs) + ' ' + tail)
# 		with open(doc, 'r', encoding='utf-8', errors='ignore') as inputFile:
# 			text = inputFile.read().replace("\n", " ")
# 		outputFilename_extract = os.path.join(outputDir_sentences_extract,tail[:-4]) + "_extract.txt"
# 		outputFilename_extract_minus = os.path.join(outputDir_sentences_extract_minus,tail[:-4]) + "_extract_minus.txt"
# 		with open(outputFilename_extract, 'w', encoding='utf-8', errors='ignore') as outputFile_extract, open(
# 				outputFilename_extract_minus, 'w', encoding='utf-8', errors='ignore') as outputFile_extract_minus:
# 			# sentences = tokenize.sent_tokenize(text)
# 			sentences = sent_tokenize_stanza(stanzaPipeLine(text))
# 			n_sentences_extract = 0
# 			n_sentences_extract_minus = 0
# 			for sentence in sentences:
# 				wordFound = False
# 				sentenceSV = sentence
# 				nextSentence = False
# 				for word in wordList:
# 					if nextSentence == True:
# 						# go to next sentence; do not write the same sentence several times if it contains several words in wordList
# 						break
# 					#
# 					if caseSensitive==False:
# 						sentence = sentence.lower()
# 						word = word.lower()
# 					if word in sentence:
# 						wordFound = True
# 						nextSentence = True
# 						n_sentences_extract += 1
# 						outputFile_extract.write(sentenceSV + " ")  # write out original sentence
# 						file_extract_written = True
# 						# if none of the words in wordList are found in a sentence write the sentence to the extract_minus file
# 				if wordFound == False:
# 					n_sentences_extract_minus += 1
# 					outputFile_extract_minus.write(sentenceSV + " ")  # write out original sentence
# 					file_extract_minus_written = True
# 		if file_extract_written == True:
# 			# filesToOpen.append(outputFilename_extract)
# 			nDocsExtractOutput += 1
# 			file_extract_written = False
# 		outputFile_extract.close()
# 		if n_sentences_extract == 0: # remove empty file
# 			os.remove(outputFilename_extract)
# 		if file_extract_minus_written:
# 			# filesToOpen.append(outputFilename_extract_minus)
# 			nDocsExtractMinusOutput += 1
# 			file_extract_minus_written = False
# 		outputFile_extract_minus.close()
# 		if n_sentences_extract_minus == 0: # remove empty file
# 			os.remove(outputFilename_extract_minus)
# 	if Ndocs == 1:
# 		msg1 = str(Ndocs) + " file was"
# 	else:
# 		msg1 = str(Ndocs) + " files were"
# 	if nDocsExtractOutput == 1:
# 		msg2 = str(nDocsExtractOutput) + " file was"
# 	else:
# 		msg2 = str(nDocsExtractOutput) + " files were"
# 	if nDocsExtractMinusOutput == 1:
# 		msg3 = str(nDocsExtractMinusOutput) + " file was"
# 	else:
# 		msg3 = str(nDocsExtractMinusOutput) + " files were"
# 	mb.showwarning("Warning", msg1 + " processed in input.\n\n" +
# 				   msg2 + " written with _extract in the filename.\n\n" +
# 				   msg3 + " written with _extract_minus in the filename.\n\n" +
# 				   "Files were written to the subdirectories " + outputDir_sentences_extract + " and " + outputDir_sentences_extract_minus + " of the output directory." +
# 				   "\n\nPlease, check the output subdirectories for filenames ending with _extract.txt and _extract_minus.txt.")

# 	IO_files_util.openExplorer(window, outputDir_sentences)


# 	IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
# 								   'Finished running the Word search unction at', True)


# # https://pypi.org/project/textstat/
# def sentence_text_readability(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage):
# 	filesToOpen = []
# 	documentID = 0

# 	files = IO_files_util.getFileList(inputFilename, inputDir, '.txt')
# 	nFile = len(files)
# 	if nFile == 0:
# 		return

# 	startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
# 												   'Started running Text Readability at',
# 												   True, '\nYou can follow Text Readability in command line.')

# 	if nFile > 1:
# 		outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
# 																	'stats')
# 		outputFilenameCsv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
# 																	'stats')
# 	else:
# 		outputFilenameTxt = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.txt', 'READ',
# 																	'stats')
# 		outputFilenameCsv = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'READ',
# 																	'stats')
# 	filesToOpen.append(outputFilenameTxt)
# 	filesToOpen.append(outputFilenameCsv)

# 	fieldnames = ['Sentence ID', 'Sentence',
# 				  'Document ID', 'Document',
# 				  'Flesch Reading Ease formula',
# 				  'Flesch-Kincaid Grade Level',
# 				  'Fog Scale (Gunning FOG Formula)',
# 				  'SMOG (Simple Measure of Gobbledygook) Index',
# 				  'Automated Readability Index',
# 				  'Coleman-Liau Index',
# 				  'Linsear Write Formula',
# 				  'Dale-Chall Readability Score',
# 				  'Overall readability consensus',
# 				  'Grade level']

# 	with open(outputFilenameCsv, 'w', encoding='utf-8', errors='ignore', newline='') as outputCsvFile:
# 		writer = csv.DictWriter(outputCsvFile, fieldnames=fieldnames)
# 		writer.writeheader()

# 		# already shown in NLP.py
# 		# IO_util.timed_alert(GUI_util.window,3000,'Analysis start','Started running NLTK unusual words at',True,'You can follow NLTK unusual words in command line.')

# 		# open txt output file
# 		outputTxtFile = open(outputFilenameTxt, "w")
# 		documentID = 0
# 		for file in files:
# 			# read txt file
# 			text = (open(file, "r", encoding="utf-8", errors="ignore").read())

# 			documentID = documentID + 1
# 			head, tail = os.path.split(file)
# 			print("Processing file " + str(documentID) + "/" + str(nFile) + ' ' + tail)

# 			# write text files ____________________________________________

# 			outputTxtFile.write("TEXT READABILITY SCORES (by Python library textstat)" + "\n\n")
# 			outputTxtFile.write(file + "\n\n")

# 			# This legenda is now available as a TIPS file
# 			# outputTxtFile.write ("LEGENDA -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
# 			# outputTxtFile.write ("Text readability measures the understandability of a text.\n")
# 			# outputTxtFile.write ("The different measures of readability map on the U.S grade level (1 through 12) needed to comprehend a text.\n\n  12 readability score requires HIGHSCHOOL education;\n  16 readability score requires COLLEGE education;\n  18 readability score requires MASTER education;\n  24 readability score requires DOCTORAL education;\n  >24 readability score requires POSTDOC education.\n\n")

# 			# outputTxtFile.write ("Automated Readability Index (ARI) outputs a number that approximates the grade level needed to comprehend the text. For example if the ARI is 6.5, then the grade level to comprehend the text is 6th to 7th grade.\n\n")
# 			# outputTxtFile.write ("Coleman-Liau Index, Linsear Write Formula, Flesch-Kincaid Grade, SMOG index, Fog Scale (Gunning FOG Formula) are grade formula in that a score of 9.3 means that a ninth grader would be able to read the document.\n\n")

# 			# outputTxtFile.write ("The Flesch Reading Ease formula has the following range of values (the maximum score is 121.22; there is no limit on how low the score can be, with a negative score being valid):\n")
# 			# outputTxtFile.write ("  0-30 College\n")
# 			# outputTxtFile.write ("  50-60 High School\n")
# 			# outputTxtFile.write ("  90-100 Fourth Grade\n\n")

# 			# outputTxtFile.write ("The Dale-Chall index has the following range of values (different from other tests, since it uses a lookup table of the most commonly used 3000 English words and returns the grade level using the New Dale-Chall Formula):\n")
# 			# outputTxtFile.write ("  4.9 or lower    easily understood by an average 4th-grade student or lower\n")
# 			# outputTxtFile.write ("  5.0–5.9 easily understood by an average 5th or 6th-grade student\n")
# 			# outputTxtFile.write ("  6.0–6.9 easily understood by an average 7th or 8th-grade student\n")
# 			# outputTxtFile.write ("  7.0–7.9 easily understood by an average 9th or 10th-grade student\n")
# 			# outputTxtFile.write ("  8.0–8.9 easily understood by an average 11th or 12th-grade student\n")
# 			# outputTxtFile.write ("  9.0–9.9 easily understood by an average 13th to 15th-grade (college) student\n\n")

# 			outputTxtFile.write(
# 				"RESULTS -----------------------------------------------------------------------------------------------------------------------------------------------\n\n")
# 			# Syllable count
# 			str_value = "Syllable count " + str(textstat.syllable_count(text, lang='en_US'))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("\n\nSyllable count ",textstat.syllable_count(text, lang='en_US'))
# 			# Lexicon count
# 			str_value = "Lexicon count " + str(textstat.lexicon_count(text, removepunct=True))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Lexicon count ",textstat.lexicon_count(text, removepunct=True))
# 			# Sentence count
# 			str_value = "Sentence count " + str(textstat.sentence_count(text))
# 			outputTxtFile.write(str_value + "\n\n")
# 			# print("Sentence count ",textstat.sentence_count(text))

# 			# The Flesch Reading Ease formula
# 			str_value = "Flesch Reading Ease formula " + str(textstat.flesch_reading_ease(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Flesch Reading Ease formula",textstat.flesch_reading_ease(text))
# 			# The Flesch-Kincaid Grade Level
# 			str_value = "Flesch-Kincaid Grade Level " + str(textstat.flesch_kincaid_grade(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Flesch-Kincaid Grade Level",textstat.flesch_kincaid_grade(text))
# 			# The Fog Scale (Gunning FOG Formula)
# 			str_value = "Fog Scale (Gunning FOG Formula) " + str(textstat.gunning_fog(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Fog Scale (Gunning FOG Formula)",textstat.gunning_fog(text))
# 			# The SMOG Index
# 			str_value = "SMOG (Simple Measure of Gobbledygook) Index " + str(textstat.smog_index(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("SMOG (Simple Measure of Gobbledygook) Index",textstat.smog_index(text))
# 			# Automated Readability Index
# 			str_value = "Automated Readability Index " + str(textstat.automated_readability_index(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Automated Readability Index",textstat.automated_readability_index(text))
# 			# The Coleman-Liau Index
# 			str_value = "Coleman-Liau Index " + str(textstat.coleman_liau_index(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Coleman-Liau Index",textstat.coleman_liau_index(text))
# 			# Linsear Write Formula
# 			str_value = "Linsear Write Formula " + str(textstat.linsear_write_formula(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Linsear Write Formula",textstat.linsear_write_formula(text))
# 			# Dale-Chall Readability Score
# 			str_value = "Dale-Chall Readability Score " + str(textstat.dale_chall_readability_score(text))
# 			outputTxtFile.write(str_value + "\n")
# 			# print("Dale-Chall Readability Score",textstat.dale_chall_readability_score(text))
# 			# Readability Consensus based upon all the above tests
# 			str_value = "\n\nReadability Consensus Level based upon all the above tests: " + str(
# 				textstat.text_standard(text, float_output=False) + '\n\n')
# 			outputTxtFile.write(str_value + "\n")
# 			# print("\n\nReadability Consensus based upon all the above tests: ",textstat.text_standard(text, float_output=False))

# 			# write csv files ____________________________________________

# 			# split into sentences
# 			# sentences = nltk.sent_tokenize(text)
# 			sentences = sentences = sent_tokenize_stanza(stanzaPipeLine(text))
# 			# analyze each sentence in text for readability
# 			sentenceID = 0  # to store sentence index
# 			for sent in sentences:
# 				sentenceID = sentenceID + 1
# 				# Flesch Reading Ease formula
# 				str1 = str(textstat.flesch_reading_ease(sent))
# 				# The Flesch-Kincaid Grade Level
# 				str2 = str(textstat.flesch_kincaid_grade(sent))
# 				# Th3 Fog Scale (Gunning FOG Formula)
# 				str3 = str(textstat.gunning_fog(sent))
# 				# The SMOG Index
# 				str4 = str(textstat.smog_index(sent))
# 				# Automated Readability Index
# 				str5 = str(textstat.automated_readability_index(sent))
# 				# The Coleman-Liau Index
# 				str6 = str(textstat.coleman_liau_index(sent))
# 				# Linsear Write Formula
# 				str7 = str(textstat.linsear_write_formula(sent))
# 				# Dale-Chall Readability Score
# 				str8 = str(textstat.dale_chall_readability_score(sent))
# 				# Overall summary measure
# 				str9 = str(textstat.text_standard(sent, float_output=False))
# 				if str9 == "-1th and 0th grade":
# 					sortOrder = 0
# 				elif str9 == "0th and 1st grade":
# 					sortOrder = 1
# 				elif str9 == "1st and 2nd grade":
# 					sortOrder = 2
# 				elif str9 == "2nd and 3rd grade":
# 					sortOrder = 3
# 				elif str9 == "3rd and 4th grade":
# 					sortOrder = 4
# 				elif str9 == "4th and 5th grade":
# 					sortOrder = 5
# 				elif str9 == "5th and 6th grade":
# 					sortOrder = 6
# 				elif str9 == "6th and 7th grade":
# 					sortOrder = 7
# 				elif str9 == "7th and 8th grade":
# 					sortOrder = 8
# 				elif str9 == "8th and 9th grade":
# 					sortOrder = 9
# 				elif str9 == "9th and 10th grade":
# 					sortOrder = 10
# 				elif str9 == "10th and 11th grade":
# 					sortOrder = 11
# 				elif str9 == "11th and 12th grade":
# 					sortOrder = 12
# 				elif str9 == "12th and 13th grade":
# 					sortOrder = 13
# 				elif str9 == "13th and 14th grade":
# 					sortOrder = 14
# 				elif str9 == "14th and 15th grade":
# 					sortOrder = 15
# 				elif str9 == "15th and 16th grade":
# 					sortOrder = 16
# 				elif str9 == "16th and 17th grade":
# 					sortOrder = 17
# 				elif str9 == "17th and 18th grade":
# 					sortOrder = 18
# 				elif str9 == "18th and 19th grade":
# 					sortOrder = 19
# 				elif str9 == "19th and 20th grade":
# 					sortOrder = 20
# 				elif str9 == "20th and 21st grade":
# 					sortOrder = 21
# 				elif str9 == "21st and 22nd grade":
# 					sortOrder = 22
# 				elif str9 == "22nd and 23rd grade":
# 					sortOrder = 23
# 				elif str9 == "23rd and 24th grade":
# 					sortOrder = 24
# 				else:
# 					str9 = 'Unclassified'
# 					sortOrder = 25
# 				# rowValue=[[documentID,file,sentenceID,sent,str1,str2,str3,str4,str5,str6,str7,str8,str9,sortOrder]]
# 				rowValue = [
# 					[str1, str2, str3, str4, str5, str6, str7, str8, str9, sortOrder, sentenceID, sent, documentID, IO_csv_util.dressFilenameForCSVHyperlink(file)]]
# 				writer = csv.writer(outputCsvFile)
# 				writer.writerows(rowValue)
# 		# at least 12th grade level HIGH-SCHOOL EDUCATION
# 		# at least 16th grade level UNDERGRADUATE COLLEGE EDUCATION
# 		# at least 18th grade level MA EDUCATION
# 		# at least 24th grade level PhD EDUCATION
# 		# > 24th grade level PostDoc EDUCATION

# 		# TODO YI not sure what to pass to the sort function;
# 		# IO filenames should be computed here
# 		# outputFilename1=IO_util.generate_output_file_name(inputFilename,outputDir,'.csv','READ','stats1')
# 		# IO_util.sort_csvFile_by_columns(outputFilenameCsv, outputFilenameCsv, ['Document ID','Sort order'])
# 		outputTxtFile.close()
# 		outputCsvFile.close()
# 		result = True

# 		# readability
# 		if createCharts == True:
# 			result = True
# 			# if nFile>10:
# 			#     result = mb.askyesno("Excel charts","You have " + str(nFile) + " files for which to compute Excel charts for each file.\n\nTHIS WILL TAKE A LONG TIME TO PRODUCE.\n\nAre you sure you want to do that?")
# 			if result == True:
# 				# 0 (Flesch Reading Ease) has a different scale and 3 (SMOG) is often 0
# 				#	do NOT plot on the same chart these two measures
# 				#	plot all other 6 measures
# 				columns_to_be_plotted = [[10, 1], [10, 2], [10, 4], [10, 5], [10, 6],[10, 7]]
# 				# multiple lines with hover-over effects the sample line chart produces wrong results
# 				# hover_label = ['Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence', 'Sentence']
# 				hover_label = []

# 				chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
# 																 outputFileLabel='READ',
# 																 chartPackage=chartPackage,
# 																 chart_type_list=["line"],
# 																 chart_title='Text Readability (6 Readability Measures)',
# 																 column_xAxis_label_var='Sentence index',
# 																 hover_info_column_list=hover_label,
# 																 count_var=0,
# 																 column_yAxis_label_var='6 Readability measures')

# 				if chart_outputFilename != "":
# 					# rename filename not be overwritten by next line plot
# 					try:
# 						chart_outputFilename_new = chart_outputFilename.replace("line_chart", "ALL_line_chart")
# 						os.rename(chart_outputFilename, chart_outputFilename_new)
# 					except:
# 						# the file already exists and must be removed
# 						if os.path.isfile(chart_outputFilename_new):
# 							os.remove(chart_outputFilename_new)
# 						os.rename(chart_outputFilename, chart_outputFilename_new)

# 					filesToOpen.append(chart_outputFilename_new)

# 				# outputFilenameXLSM_1 = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
# 				#                                           outputFilenameCsv, chart_type_list=["line"],
# 				#                                           chart_title="Text Readability",
# 				#                                           column_xAxis_label_var='Sentence Index',
# 				#                                           column_yAxis_label_var='Readability grade level',
# 				#                                           outputExtension='.xlsm', label1='READ', label2='line',
# 				#                                           label3='charts', label4='', label5='', useTime=False,
# 				#                                           disable_suffix=True,
# 				#                                           count_var=0, column_yAxis_field_list=[],
# 				#                                           reverse_column_position_for_series_label=False,
# 				#                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
# 				#                                           hover_var=1, hover_info_column_list=hover_label)
# 				# if outputFilenameXLSM_1 != "":
# 				#     filesToOpen.append(outputFilenameXLSM_1)

# 				# plot overall grade level
# 				columns_to_be_plotted = [[10, 9]]
# 				hover_label = ['Sentence']
# 				chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
# 																 outputFileLabel='READ',
# 																 chartPackage=chartPackage,
# 																 chart_type_list=["line"],
# 																 chart_title='Text Readability (Readability Grade Level)',
# 																 column_xAxis_label_var='Sentence index',
# 																 hover_info_column_list=hover_label,
# 																 count_var=0,
# 																 column_yAxis_label_var='Readability grade level')

# 				if chart_outputFilename != "":
# 					filesToOpen.append(chart_outputFilename)

# 				# outputFilenameXLSM_2 = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
# 				#                                           outputFilenameCsv, chart_type_list=["line"],
# 				#                                           chart_title="Text Readability",
# 				#                                           column_xAxis_label_var='Sentence Index',
# 				#                                           column_yAxis_label_var='Readability grade level',
# 				#                                           outputExtension='.xlsm', label1='READ', label2='line',
# 				#                                           label3='chart', label4='', label5='', useTime=False,
# 				#                                           disable_suffix=True,
# 				#                                           count_var=0, column_yAxis_field_list=[],
# 				#                                           reverse_column_position_for_series_label=False,
# 				#                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
# 				#                                           hover_var=1, hover_info_column_list=hover_label)
# 				# if outputFilenameXLSM_2 != "":
# 				#     filesToOpen.append(outputFilenameXLSM_2)

# 			# bar chart of the frequency of sentences by grade levels
# 			columns_to_be_plotted = [[10, 8]]
# 			hover_label = []

# 			chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, outputFilenameCsv, outputDir,
# 															 outputFileLabel='READ',
# 															 chartPackage=chartPackage,
# 															 chart_type_list=["bar"],
# 															 chart_title='Frequency of Sentences by Readability Consensus of Grade Level',
# 															 column_xAxis_label_var='',
# 															 hover_info_column_list=hover_label,
# 															 count_var=1)
# 			if chart_outputFilename != "":
# 				filesToOpen.append(chart_outputFilename)

# 			# outputFilenameXLSM_3 = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
# 			#                                           outputFilenameCsv, chart_type_list=["bar"],
# 			#                                           chart_title="Frequency of Sentences by Readability Consensus of Grade Level",
# 			#                                           column_xAxis_label_var='', column_yAxis_label_var='Frequency',
# 			#                                           outputExtension='.xlsm', label1='READ', label2='bar',
# 			#                                           label3='chart', label4='', label5='', useTime=False,
# 			#                                           disable_suffix=True,
# 			#                                           count_var=1, column_yAxis_field_list=[],
# 			#                                           reverse_column_position_for_series_label=False,
# 			#                                           series_label_list=[''], second_y_var=0, second_yAxis_label='',
# 			#                                           hover_var=1, hover_info_column_list=hover_label)
# 			# if outputFilenameXLSM_3 != "":
# 			#     filesToOpen.append(outputFilenameXLSM_3)

# 	IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end', 'Finished running Text Readability at',
# 									   True, '', True, startTime)

# 	if len(inputDir) != 0:
# 		mb.showwarning(title='Warning',
# 					   message='The output filenames generated by Textstat readability contain the name of the directory processed in input, rather than the name of any individual file in the directory.\n\nBoth txt & csv files include all ' + str(
# 						   nFile) + ' files in the input directory processed by Textstat.')
# 	if openOutputFiles == True:
# 		IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)


# # written by Siyan Pu October 2021
# # edited by Roberto Franzosi October 2021
# def sentence_structure_tree(inputFilename, outputDir):
# 	if inputFilename == '':
# 		sentences = GUI_IO_util.enter_value_widget(
# 			'Enter sentence                                                                               ', 'Enter', 1)
# 		sent = [sentences[0]]
# 		if len(sent) == 0:
# 			return
# 		else:
# 			sentences = sent
# 		maxNum = 1
# 	else:
# 		# split into sentences
# 		text = (open(inputFilename, "r", encoding="utf-8", errors='ignore').read())
# 		sentences = nltk.sent_tokenize(text)
# 		maxNum = GUI_IO_util.enter_value_widget('Enter number of sentences to be visualized', 'Enter', 1)
# 		maxNum = str(maxNum[0])
# 		if maxNum == '':
# 			return
# 		maxNum = int(maxNum)
# 		if maxNum >= 10:
# 			result = mb.askyesno('Warning',
# 								 "The number of sentences entered is quite large. The tree graph algorithm will produce a png file for every sentence.\n\nAre you sure you want to continue?")
# 			if result == False:  # yes no False
# 				return

# 	sentenceID = 0  # to store sentence index

# 	spacy_nlp = spacy.load("en_core_web_sm")

# 	for sent in sentences:
# 		sentenceID = sentenceID + 1
# 		if sentenceID == maxNum + 1:
# 			return

# 		doc = spacy_nlp(sent)

# 		def token_format(token):
# 			return "_".join([token.orth_, token.tag_, token.dep_])

# 		def to_nltk_tree(node):
# 			if node.n_lefts + node.n_rights > 0:
# 				return Tree(token_format(node),
# 							[to_nltk_tree(child)
# 							 for child in node.children]
# 							)
# 			else:
# 				return token_format(node)

# 		tree = [to_nltk_tree(sent.root) for sent in doc.sents]

# 		cf = TreeView(tree[0])._cframe

# 		if inputFilename == '':
# 			cf.print_to_file(outputDir + 'NLP_sentence_tree.ps')
# 		else:
# 			cf.print_to_file(outputDir + '/' + os.path.basename(inputFilename) + '_' + str(sentenceID) + '_tree.ps')

# # written by Mino Cha March/April 2022
# def sentence_complexity(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage):
# 	## list for csv file
# 	documentID = []
# 	document = []
# 	documentName = []

# 	all_input_docs = {}
# 	dId = 0

# 	filesToOpen = []

# 	startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
# 												   'Started running Sentence Complexity at', True)
# 	if len(inputFilename) > 0:
# 		numFiles = 1
# 		doc = inputFilename
# 		if doc.endswith('.txt'):
# 			with open(doc, 'r', encoding='utf-8', errors='ignore') as file:
# 				dId += 1
# 				head, tail = os.path.split(doc)
# 				print("Processing file " + str(dId) + '/' + str(numFiles) + tail)
# 				text = file.read()
# 				documentID.append(dId)
# 				document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
# 				all_input_docs[dId] = text
# 	else:
# 		numFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
# 		if numFiles == 0:
# 			mb.showerror(title='Number of files error',
# 						 message='The selected input directory does NOT contain any file of txt type.\n\nPlease, select a different directory and try again.')
# 			return

# 		for doc in os.listdir(inputDir):
# 			if doc.endswith('.txt'):
# 				head, tail = os.path.split(doc)
# 				with open(os.path.join(inputDir, doc), 'r', encoding='utf-8', errors='ignore') as file:
# 					dId += 1
# 					print("Importing filename " + str(dId) + '/' + str(numFiles) + tail)
# 					text = file.read()
# 					documentID.append(dId)
# 					document.append(IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(inputDir, doc)))
# 					all_input_docs[dId] = text
# 	document_df = pd.DataFrame({'Document ID': documentID, 'Document': document})
# 	document_df = document_df.astype('str')

# 	nlp = stanza.Pipeline(lang='en', processors='tokenize,pos, constituency',use_gpu=False)
# 	op = pd.DataFrame(
# 		columns=['Sentence length (No. of words)', 'Yngve score', 'Yngve sum', 'Frazier score', 'Frazier sum',
# 				 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
# 	for idx, txt in enumerate(all_input_docs.items()):
# 		doc = nlp(txt[1])
# 		tail = os.path.split(IO_csv_util.undressFilenameForCSVHyperlink(document[idx]))[1]
# 		print("Processing file " + str(dId) + '/' + str(numFiles) + tail)
# 		for i, sentence in enumerate(doc.sentences):
# 			sent = str(sentence.constituency)
# 			root1 = tree.make_tree(sent)
# 			root2 = tree.make_tree(sent)
# 			leaves_list = tree.getLeavesAsList(root1)
# 			# print(i)
# 			# print(sentence.text)
# 			sentence_length = len(sentence.words)
# 			# print(sentence_length)

# 			newRoot1 = Node.Node(root1)
# 			newRoot2 = Node.Node(root2)
# 			newRoot1.calY()
# 			newRoot2.calF()
# 			leaf = len(leaves_list)

# 			words = str(sentence).split(" ")
# 			size = len(words) - 1

# 			ySum = newRoot1.sumY()
# 			yAvg = round(ySum / leaf, 2)
# 			# print(f"Yngve: {yAvg}, {ySum}")

# 			fSum = newRoot2.sumF()
# 			fAvg = round(fSum / leaf, 2)
# 			# print(f"Frazier: {fAvg}, {fSum}\n")

# 			# new ordering
# 			op = op.append({
# 				'Sentence length (No. of words)': sentence_length,
# 				'Yngve score': yAvg,
# 				'Yngve sum': ySum,
# 				'Frazier score': fAvg,
# 				'Frazier sum': fSum,
# 				'Sentence ID': i + 1,
# 				'Sentence': sentence.text,
# 				'Document ID': idx + 1,
# 				'Document': document[idx],
# 			},
# 				ignore_index=True)

# 	outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
# 															 'SentenceComplexity')
# 	op.to_csv(outputFilename, index=False)
# 	filesToOpen.append(outputFilename)

# 	if createCharts == True:
# 		inputFilename = outputFilename
# 		columns_to_be_plotted = [[5, 1], [5, 3]]
# 		# hover_label = ['Sentence', 'Sentence']
# 		hover_label = []
# 		chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
# 														 outputFileLabel='Complex',
# 														 chartPackage=chartPackage,
# 														 chart_type_list=["line"],
# 														 chart_title='Complexity Scores (Yngve, Frazier) by Sentence Index',
# 														 column_xAxis_label_var='Sentence index',
# 														 #hover_info_column_list=hover_label,
# 														 #count_var=0,
# 														 column_yAxis_label_var='Scores')
# 		if chart_outputFilename != "":
# 			filesToOpen.append(chart_outputFilename)


# 	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
# 									   'Finished running Sentence Complexity at', True, '', True, startTime)
# 	if openOutputFiles == True:
# 		IO_files_util.OpenOutputFiles(window, openOutputFiles, filesToOpen)
	return filesToOpen
