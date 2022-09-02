import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "sentence_analysis_util",
										  ['tkinter', 'os', 'collections','stanza']) == False:
	sys.exit(0)

import tkinter as tk
import collections
import os
from Stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza
import pandas as pd
import IO_csv_util
import IO_files_util


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
		dic = pd.read_csv(input_dictionary_file, encoding='utf-8', error_bad_lines=False)
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
				token = word_tokenize_stanza(stanzaPipeLine(each_sentence))
				for word in token:
					for dict_word in dic:
						if word == dict_word[0].rstrip():
							In.append([word, dict_word[1], Sentence_ID, each_sentence, documentID, file])
							break
						else:
							continue
				container.append(In)

			ctr = collections.Counter(Extract(container))
			for word in container:
				word.insert(2, ctr.get(word[0]))
			for word in container:
				if word[0] not in Extract(DictionaryList):
					DictionaryList.append(word)

			DictionaryList.insert(0, ['Dict_value', 'Dict_second_value', 'Frequency', 'Sentence ID', 'Sentence',
									  'Document ID', 'Document'])
	else:
		dic = pd.read_csv(input_dictionary_file, encoding='utf-8', error_bad_lines=False)
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
				token = word_tokenize_stanza(stanzaPipeLine(each_sentence))
				for word in token:
					for dict_word in dic_value:
						if word == dict_word.rstrip():
							In.append([word, Sentence_ID, each_sentence, documentID, IO_csv_util.undressFilenameForCSVHyperlink(file)])
							break
						else:
							continue
				container.append(In)

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
