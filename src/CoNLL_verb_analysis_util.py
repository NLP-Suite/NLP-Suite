"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019
"""

import sys

import GUI_IO_util
import IO_files_util
import GUI_util
import IO_libraries_util
import IO_csv_util
import IO_user_interface_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Noun Verb Analysis",
								['csv', 'os', 'collections', 'tkinter']) == False:
	sys.exit(0)

import csv
import os
from collections import Counter
from tkinter import filedialog
import tkinter.messagebox as mb
import tkinter as tk

import IO_CoNLL_util
import Excel_util
import statistics_csv_util
import Excel_util
import Stanford_CoreNLP_tags_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

global recordID_position, documentId_position #, data, data_divided_sents
recordID_position = 8
documentId_position = 10

# Following are used if running all analyses to prevent redundancy
# filesToOpen = []  # Store all files that are to be opened once finished
inputFilename = ''
outputDir = ''
cla_open_csv = False  # if run from command line, will check if they want to open the CSV

"""
    SUPPORTING COMMANDS FOR MAIN FUNCTIONS
"""


# to avoid key value error

# Take in file name, output is a list of rows each with columns 1->11 in the conll table
# Used to divide sentences etc.


def compute_stats(data):
	global postag_list, postag_counter, deprel_list, deprel_counter
	postag_list = [i[3] for i in data]
	deprel_list = [i[6] for i in data]
	postag_counter = Counter(postag_list)
	deprel_counter = Counter(deprel_list)
	return postag_list, postag_counter, deprel_list, deprel_counter


# for voice analysis
def verb_voice_compute_frequencies(list_all_tok):
	# print ("\n------- VERB VOICE ANALYSIS -------")
	# print ("\n############### VERB VOICE ANALYSIS ##############")
	rootAuxiliary = False
	rootPassive = False
	InsertData = False
	aux_helper = ''
	_aux_VBN = []
	_auxp_VBN = []
	_active_ = []
	num_passive = 0
	num_active = 0

	for ind, tok in enumerate(list_all_tok):
		if tok[6] == 'aux':
			rootAuxiliary = True
			rootPassive = False
			aux_helper = tok
		elif tok[6] == 'aux:pass':
			rootAuxiliary = False
			rootPassive = True
			aux_helper = tok
		else:
			if tok[3] == 'VBN':
				if rootPassive:
					num_passive += 1
					_auxp_VBN.append([aux_helper, tok])
					voiceType = 'Passive'
				elif rootAuxiliary:
					voiceType = 'Active'
					num_active += 1
					_aux_VBN.append([aux_helper, tok])
				else:
					num_active += 1
					_active_.append(tok)
			else:
				voiceType = 'Active'
				rootAuxiliary = False
				rootPassive = False
				num_active += 1
				_active_.append(tok)

	auxp_VBN_organize = []
	aux_VBN_organize = []
	for pair in _auxp_VBN:
		auxp_form = pair[0][1]
		vbn_form = pair[1][1]
		pair[1][1] = auxp_form + " " + vbn_form
		pair[1] = pair[1] + ['Passive']
		auxp_VBN_organize.append(pair[1])
	for pair in _aux_VBN:
		pair[1][1] = pair[0][1] + " " + pair[1][1]
		pair[1] = pair[1] + ['Active']
		aux_VBN_organize.append(pair[1])
	_active_ = [i + ['Active'] for i in _active_]

	voice_list = [['Verb Voice', 'Frequencies'],
				  ['Passive', len(auxp_VBN_organize)],
				  ['Active', len(aux_VBN_organize) + len(_active_)]]
	return auxp_VBN_organize, aux_VBN_organize, _active_, voice_list


# verb voice; compute frequencies
def verb_voice_data_preparation(data):
	try:
		verb_postags = ['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ']
		verb_deprel = ['aux:pass', 'aux']
		data_2 = [tok for tok in data if (tok[3] in verb_postags or tok[6] in verb_deprel)]
		return data_2
	except:
		print("ERROR: INPUT MUST BE THE CoNLL TABLE CONTAINING THE SENTENCE ID. Program will exit.")
		mb.showinfo("ERROR",
					"INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
		return


def voice_output(voice_word_list,data_divided_sents):
	voice_pass, voice_act_aux, voice_act, voice_stats = verb_voice_compute_frequencies(
		voice_word_list)  # passive active analysis
	voice = voice_pass + voice_act_aux + voice_act  # join
	voice = [i + [IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentId_position], i[9])] for i in
			 voice]  # get full sentence
	voice_sorted = sorted(voice, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
	return voice_sorted, voice_stats


def verb_voice_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts):
	filesToOpen = []  # Store all files that are to be opened once finished

	# print ("\nRun verb voice analysis")

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running VERB VOICE analysis at', True)

	data_prep = verb_voice_data_preparation(data)

	voice_list, voice_stats = voice_output(data_prep,data_divided_sents)

	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Voice', 'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Voice', 'stats')

	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
									 IO_CoNLL_util.sort_output_list('Verb Voice', voice_list, documentId_position),
									 verb_file_name)
	if errorFound == True:
		return
	filesToOpen.append(verb_file_name)

	errorFound = IO_csv_util.list_to_csv(GUI_util.window, voice_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_stats_file_name)

	if createExcelCharts == True:
		Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
															 data_to_be_plotted=[voice_stats],
															 inputFilename=verb_stats_file_name,
															 outputDir=outputDir,
															 scriptType='Verb_Voice',
															 chartTitle="Frequency Distribution of Verb Voice",
															 chart_type_list=["pie"],
															 column_xAxis_label="Verb voice values",
															 column_yAxis_label="Frequency")

		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

		# line plots by sentence index
		outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
																	   verb_file_name,
																	   '',
																	   outputDir,
																	   openOutputFiles,
																	   createExcelCharts,
																	   [[1, 4]],
																	   ['Verb Voice'],
																		   ['FORM', 'Sentence'],
																		   ['Document ID', 'Sentence ID',
																			'Document'],
																	   'NVA', 'line')
		if len(outputFiles) > 0:
			filesToOpen.extend(outputFiles)

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running VERB VOICE analysis at', True)

	return filesToOpen

# modality compute frequencies of modality categories
def verb_modality_compute_categories(data,data_divided_sents):
	num_obligation_mod = 0
	num_will_would_mod = 0
	num_can_may_mod = 0
	num_unclassified = 0
	modality_list = []
	obligation_keywords = ['must', 'need', 'form', 'should', 'ought', 'shall']
	will_would_keywords = ['will', 'would', 'll', '\'d']
	can_may_keywords = ['can', 'could', 'may', 'might']

	for i in data:
		if i[3] != 'MD':
			continue
		else:
			if i[1].lower() in obligation_keywords:
				num_obligation_mod += 1
				modality_list.append(i + ['Obligation', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							 i[documentId_position],
																							 i[9])])
			elif i[1].lower() in will_would_keywords:
				num_will_would_mod += 1
				modality_list.append(i + ['Will/Would', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							 i[documentId_position],
																							 i[9])])
			elif i[1].lower() in can_may_keywords:
				num_can_may_mod += 1
				modality_list.append(i + ['Can/May', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																						  i[documentId_position],
																						  i[9])])
			else:
				num_unclassified += 1
				modality_list.append(i + ['Non-classified Modal Type',
										  IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																			   i[documentId_position], i[9])])

	modality_stats = [['Verb Modality', 'Frequencies'],
					  ['Obligation', num_obligation_mod],
					  ['Will/Would', num_will_would_mod],
					  ['Can/May', num_can_may_mod],
					  ['Non-classified modal type', num_unclassified]]

	return modality_list, modality_stats


def verb_modality_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts):
	filesToOpen = []  # Store all files that are to be opened once finished

	# print ("\nRun verb modality analysis")
	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running VERB MODALITY analysis at', True)

	modality_list, modality_stats = verb_modality_compute_categories(data,data_divided_sents)

	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Modality', 'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Modality', 'stats')

	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
									 IO_CoNLL_util.sort_output_list('Verb Modality', modality_list, documentId_position),
									 verb_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_file_name)

	errorFound = IO_csv_util.list_to_csv(GUI_util.window, modality_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_stats_file_name)

	if createExcelCharts == True:
		Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
															 data_to_be_plotted=[modality_stats],
															 inputFilename=verb_stats_file_name,
															 outputDir=outputDir,
															 scriptType='Verb_Modal',
															 chartTitle="Frequency Distribution of Verb Modality",
															 chart_type_list=["pie"],
															 column_xAxis_label="Verb Modality",
															 column_yAxis_label="Frequency")
		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

		# line plots by sentence index
		outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
																	   verb_file_name,
																	   '',
																	   outputDir,
																	   openOutputFiles,
																	   createExcelCharts,
																	   [[1, 4]],
																	   ['Verb Modality'],['FORM', 'Sentence'],['Document ID', 'Sentence ID', 'Document'],
																	   'NVA','line')
		if len(outputFiles) > 0:
			filesToOpen.extend(outputFiles)

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running VERB MODALITY analysis at',
									   True)  # TODO: if this fails, try putting it in its own function

	return filesToOpen

# tense analysis; compute frequencies
def verb_tense_compute_frequencies(CoNLL_table, data_divided_sents):
	future_mod = ['\'ll', 'shall', 'will']
	num_present_tense = 0
	num_future_tense = 0
	num_gerundive_tense = 0
	num_infinitive_tense = 0
	num_past_tense = 0
	num_past_principle_tense = 0

	verb_tense_list = []

	for i in CoNLL_table:
		if i[3] == 'MD':
			if i[1].lower() in future_mod:
				num_future_tense += 1
				verb_tense_list.append(i + ['Future', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																						   i[documentId_position],
																						   i[9])])
			else:
				num_present_tense += 1
				verb_tense_list.append(i + ['Present', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							i[documentId_position],
																							i[9])])
		else:
			if i[3] == 'VBG':
				num_gerundive_tense += 1
				verb_tense_list.append(i + ['Gerundive', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							  i[documentId_position],
																							  i[9])])
			elif i[3] == 'VB':
				num_infinitive_tense += 1
				verb_tense_list.append(i + ['Infinitive', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							   i[documentId_position],
																							   i[9])])
			elif i[3] == 'VBD':
				num_past_tense += 1
				verb_tense_list.append(i + ['Past', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																						 i[documentId_position], i[9])])
			elif i[3] == 'VBN':
				num_past_principle_tense += 1
				verb_tense_list.append(i + ['Past Principle/Passive',
											IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																				 i[documentId_position], i[9])])
			elif i[3] in ['VBP', 'VBZ']:
				num_present_tense += 1
				verb_tense_list.append(i + ['Present', IO_CoNLL_util.Sentence_searcher(data_divided_sents,
																							i[documentId_position],
																							i[9])])

	tense_stats = [['Verb Tense', 'Frequencies'],
				   ['Future', num_future_tense],
				   ['Gerundive', num_gerundive_tense],
				   ['Infinitive', num_infinitive_tense],
				   ['Past', num_past_tense],
				   ['Past Principle/Passive', num_past_principle_tense],
				   ['Present', num_present_tense]]

	return verb_tense_list, tense_stats


def verb_tense_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createExcelCharts):
	filesToOpen = []  # Store all files that are to be opened once finished

	# inputFilename = GUI_util.inputFilename.get()
	# outputDir = GUI_util.outputFilename.get()

	# print ("\nRun verb tense analysis")

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running VERB TENSE analysis at', True)

	tense_list, tense_stats = verb_tense_compute_frequencies(data, data_divided_sents)

	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Tense', 'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '',  outputDir, '.csv', 'NVA', 'Verb Tense', 'stats')

	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
									 IO_CoNLL_util.sort_output_list('Verb Tense', tense_list, documentId_position),
									 verb_file_name)
	if errorFound == True:
		return

	errorFound = IO_csv_util.list_to_csv(GUI_util.window, tense_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_stats_file_name)

	if createExcelCharts == True:

		Excel_outputFilename = Excel_util.create_excel_chart(GUI_util.window,
															 data_to_be_plotted=[tense_stats],
															 inputFilename=verb_stats_file_name,
															 outputDir=outputDir,
															 scriptType='Verb_Tense',
															 chartTitle="Frequency Distribution of Verb Tense",
															 chart_type_list=["pie"],
															 column_xAxis_label="Verb Tense",
															 column_yAxis_label="Frequency")

		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

		# line plots by sentence index
		outputFiles = Excel_util.compute_csv_column_frequencies(GUI_util.window,
																	   verb_file_name,
																	   '',
																	   outputDir,
																	   openOutputFiles,
																	   createExcelCharts,
																	   [[1, 4]],
																	   ['Verb Tense'], ['FORM', 'Sentence'], ['Document ID', 'Sentence ID','Document'],
																	   'NVA', 'line')
		if len(outputFiles) > 0:
			filesToOpen.extend(outputFiles)

	IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running VERB TENSE analysis at', True)

	return filesToOpen