"""
Python 3 script
author: Jian Chen, January 2019, based on original vba code by Roberto Franzosi
modified by Jack Hester and Roberto Franzosi, February, June 2019, November 2021
modified by Siyan Pu November 2021
"""

import sys
import GUI_util
import IO_libraries_util
import pandas as pd

if IO_libraries_util.install_all_packages(GUI_util.window, "Verb Analysis",
										  ['csv', 'os', 'collections', 'tkinter']) == False:
	sys.exit(0)

from collections import Counter
from tkinter import filedialog
import tkinter.messagebox as mb
import tkinter as tk

import CoNLL_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import charts_util
import statistics_csv_util
import Stanford_CoreNLP_tags_util
import reminders_util

dict_POSTAG, dict_DEPREL = Stanford_CoreNLP_tags_util.dict_POSTAG, Stanford_CoreNLP_tags_util.dict_DEPREL

# global recordID_position, documentID_position #, data, data_divided_sents
recordID_position = 9  # NEW CoNLL_U
sentenceID_position = 10  # NEW CoNLL_U
documentID_position = 11  # NEW CoNLL_U

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
	global form_list, postag_list, postag_counter, deprel_list, deprel_counter
	form_list = []
	form_list = [i[1] for i in data]
	form_list = []
	postag_list = [i[3] for i in data]
	deprel_list = [i[6] for i in data]
	postag_counter = Counter(postag_list)
	deprel_counter = Counter(deprel_list)
	return form_list, postag_list, postag_counter, deprel_list, deprel_counter


# VERB VOICE ----------------------------------------------------------------------------------------------

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

	verb_voice_stats = [['Verb Voice', 'Frequencies'],
				  ['Passive', len(auxp_VBN_organize)],
				  ['Active', len(aux_VBN_organize) + len(_active_)]]
	return auxp_VBN_organize, aux_VBN_organize, _active_, verb_voice_stats


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


def voice_output(voice_word_list, data_divided_sents):
	voice_pass, voice_act_aux, voice_act, voice_stats = verb_voice_compute_frequencies(
		voice_word_list)  # passive active analysis
	voice = voice_pass + voice_act_aux + voice_act  # join
	# voice = [i + [IO_CoNLL_util.Sentence_searcher(data_divided_sents, i[documentID_position], i[sentenceID_position])] for i in
	# 		 voice]  # get full sentence
	voice_sorted = sorted(voice, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
	voice_pass = sorted(voice_pass, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
	voice_act_aux = sorted(voice_act_aux, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
	voice_act = sorted(voice_act, key=lambda x: int(x[recordID_position]))  # sort in ascending record id order
	return voice_sorted, voice_stats, voice_pass, voice_act_aux, voice_act

def verb_voice_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createCharts, chartPackage):
	filesToOpen = []  # Store all files that are to be opened once finished
	# print ("\nRun verb voice analysis")
	data_prep = verb_voice_data_preparation(data)

	verb_voice_list, voice_stats, vocie_pass, voice_aux, vocie_act = voice_output(data_prep, data_divided_sents)
	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Voice',
																'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
																	'Verb Voice', 'stats')

	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
											verb_voice_list,
											verb_file_name)
	if errorFound == True:
		return
	filesToOpen.append(verb_file_name)

	# modified by Siyan Pu November 2021
	# temporary headers added, not sure why the verb_voice_list doesn't have headers
	df = pd.read_csv(verb_file_name, header=None)
	df.to_csv(verb_file_name,
				header=["ID", "FORM", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
						"Verb Voice"])
	errorFound = IO_csv_util.list_to_csv(GUI_util.window, voice_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	# filesToOpen.append(verb_stats_file_name)

	if createCharts == True:
		columns_to_be_plotted=[[0,1]]
		count_var=0
		chart_outputFilename = charts_util.run_all(columns_to_be_plotted, verb_stats_file_name, outputDir,
														 outputFileLabel='verb_voice',
														 chartPackage=chartPackage,
														 chart_type_list=['bar'],
														 chart_title="Frequency Distribution of Verb Voice",
														 column_xAxis_label_var='Verb Voice',
														 hover_info_column_list=[],
														 count_var=count_var)
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)

		columns_to_be_plotted=[[11,14]] # sentence ID field comes first [11
		count_var=0
		chart_outputFilename = charts_util.run_all(columns_to_be_plotted, verb_file_name, outputDir,
														 outputFileLabel='verb_voice',
														 chartPackage=chartPackage,
														 chart_type_list=['line'],
														 chart_title="Frequency Distribution of Verb Voice by Sentence Index",
														 column_xAxis_label_var='Verb Voice',
														 hover_info_column_list=[],
														 count_var=count_var,
														 complete_sid=True)
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)

	return filesToOpen


# VERB MODALITY ----------------------------------------------------------------------------------------------
# written by Tony Chen Gu Mar 2022
# add an extra column describing verb modality
def verb_modality_data_preparation(data):
	obl_row = []
	will_row = []
	can_row = []
	verb_postags = ['MD']
	obligation_keywords = ['must', 'need', 'form', 'should', 'ought', 'shall']
	will_would_keywords = ['will', 'would', 'll', '\'d']
	can_may_keywords = ['can', 'could', 'may', 'might']

	for i in data:
		if(i[1] in obligation_keywords and i[3] in verb_postags):
			obl_row.append(i+["Obligation"])
		elif(i[1] in will_would_keywords and i[3] in verb_postags):
			will_row.append(i+["Will/Would"])
		elif(i[1] in can_may_keywords and i[3] in verb_postags):
			can_row.append(i+["Can/May"])
	dat = obl_row + will_row + can_row
	verb_modality_stats = [['Verb Modality', 'Frequencies'],
				  ['Obligation', len(obl_row)],
				  ['Will/Would', len(will_row)],
				  ['Can/May', len(can_row)]]
	dat = sorted(dat, key=lambda x: int(x[recordID_position]))
	return dat, verb_modality_stats

# modality compute frequencies of modality categories
# def verb_modality_compute_categories(data, data_divided_sents):
# 	num_obligation_mod = 0
# 	num_will_would_mod = 0
# 	num_can_may_mod = 0
# 	num_unclassified = 0
# 	verb_modality_list = []
# 	obligation_keywords = ['must', 'need', 'form', 'should', 'ought', 'shall']
# 	will_would_keywords = ['will', 'would', 'll', '\'d']
# 	can_may_keywords = ['can', 'could', 'may', 'might']

# 	try:
# 		verb_postags = ['MD']
# 		obligation_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in obligation_keywords)]
# 		will_would_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in will_would_keywords)]
# 		can_may_list = [tok[1] for tok in data if (tok[3] in verb_postags and tok[1] in can_may_keywords)]

# 		verb_modality_list = [['Verb Modality', 'Frequencies'],
# 					  ['Obligation', len(obligation_list)],
# 					  ['Will/would', len(will_would_list)],
# 					  ['Can/may', len(can_may_list)]]

# 		obligation_counter = len(obligation_list)
# 		will_would_counter = len(will_would_list)
# 		can_may_counter = len(can_may_list)

# 		return obligation_counter, will_would_counter, can_may_counter, obligation_list, will_would_list
# 	except:
# 		print("ERROR: INPUT MUST BE THE CoNLL TABLE CONTAINING THE SENTENCE ID. Program will exit.")
# 		mb.showinfo("ERROR",
# 					"INPUT MUST BE THE MERGED CoNLL TABLE CONTAINING THE SENTENCE ID. Please use the merge option when generating your CoNLL table in the StanfordCoreNLP.py routine. Program will exit.")
# 		return

def verb_modality_stats(config_filename, inputFilename, outputDir, data, data_divided_sents, openOutputFiles,
						createCharts, chartPackage):
	reminders_util.checkReminder(config_filename,
								 reminders_util.title_options_CoNLL_table_verb_modality,
								 reminders_util.message_CoNLL_table_verb_modality,
								 True)

	filesToOpen = []  # Store all files that are to be opened once finished

	obligation_list, modality_stats = verb_modality_data_preparation(data)
	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
															 'Verb Modality', 'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
																   'Verb Modality', 'stats')

	# errorFound = IO_csv_util.list_to_csv(GUI_util.window,
	# 								 CoNLL_util.sort_output_list('Verb Modality', modality_list),
	# 								 verb_file_name)
	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
										 obligation_list,
										 verb_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_file_name)

	errorFound = IO_csv_util.list_to_csv(GUI_util.window, modality_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_stats_file_name)

	if createCharts == True:
		columns_to_be_plotted=[[0,1]]
		count_var=0
		chart_outputFilename = charts_util.run_all(columns_to_be_plotted, verb_stats_file_name, outputDir,
														 outputFileLabel='verb_modality',
														 chartPackage=chartPackage,
														 chart_type_list=['bar'],
														 chart_title="Frequency Distribution of Verb Modality",
														 column_xAxis_label_var='Verb Modality',
														 hover_info_column_list=[],
														 count_var=count_var)
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)

		# temporary headers added, not sure why the verb_voice_list doesn't have headers
		df = pd.read_csv(verb_file_name, header=None)
		df.to_csv(verb_file_name,
				  header=["ID", "FORM", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
					  "Verb Modality"])

		# line plots by sentence index
		chart_outputFilename = statistics_csv_util.compute_csv_column_frequencies(inputFilename=verb_file_name,
															outputDir=outputDir,
															select_col=['Verb Modality'],
															group_col=['Sentence ID'],
															chartTitle="Frequency Distribution of Verb Modality",
															chartPackage=chartPackage)
		
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)


	return filesToOpen


# VERB TENSE ----------------------------------------------------------------------------------------------
# written by Tony Chen Gu Mar 2022
# add an extra column describing verb tense
def verb_tense_data_preparation(data):
	dat = []
	vbg_counter = 0
	vbd_counter = 0
	vbn_counter = 0
	vbp_counter = 0
	vb_counter = 0
	verb_tense_list = ['VBG', 'VBD', 'VB', 'VBN', 'VBP']
	
	for i in data:
		if(i[3] in verb_tense_list):
			tense = i[3]
			if(tense == 'VBG'):
				tense_col = 'Gerundive'
				vbg_counter+=1
			elif(tense == 'VBD'):
				tense_col = 'Past'
				vbd_counter+=1
			elif(tense == 'VB'):
				tense_col = 'Infinitive'
				vb_counter+=1
			elif(tense == 'VBN'):
				tense_col = 'Past Principle/Passive'
				vbn_counter+=1
			elif(tense == 'VBP'):
				tense_col = 'Present'
				vbp_counter+=1
			dat.append(i+[tense_col])
	verb_tense_stats = [['Verb Tense', 'Frequencies'],
					['Gerundive', vbg_counter],
					['Infinitive', vbg_counter],
					['Past', vbd_counter],
					['Past Principle/Passive', vbn_counter],
					['Present', vbp_counter]]
	dat = sorted(dat, key=lambda x: int(x[recordID_position]))
	return dat, verb_tense_stats

# tense analysis; compute frequencies
# def verb_tense_compute_frequencies(data, data_divided_sents):
# 	global postag_counter
# 	verb_future_list = []
# 	verb_gerundive_list = []
# 	verb_infinitive_list = []
# 	verb_past_list = []
# 	verb_past_principle_list = []
# 	verb_present_list = []
# 	# must be sorted in descending order
# 	form_list, postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
# 	verb_tense_stats = [['Verb Tense', 'Frequencies'],
# 				   # ['Future', postag_counter['VBD']],
# 				   ['Gerundive', postag_counter['VBG']],
# 				   ['Infinitive', postag_counter['VB']],
# 				   ['Past', postag_counter['VBD']],
# 				   ['Past Principle/Passive', postag_counter['VBN']],
# 				   ['Present', postag_counter['VBP']]]

# 	return verb_tense_list, verb_tense_stats


def verb_tense_stats(inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createCharts, chartPackage):
	global postag_counter
	filesToOpen = []  # Store all files that are to be opened once finished

	# inputFilename = GUI_util.inputFilename.get()
	# outputDir = GUI_util.outputFilename.get()
	# form_list, postag_list, postag_counter, deprel_list, deprel_counter = compute_stats(data)
	# verb_tense_stats = [['Verb Tense', 'Frequencies'],
	# 			   # ['Future', postag_counter['VBD']],
	# 			   ['Gerundive', postag_counter['VBG']],
	# 			   ['Infinitive', postag_counter['VB']],
	# 			   ['Past', postag_counter['VBD']],
	# 			   ['Past Principle/Passive', postag_counter['VBN']],
	# 			   ['Present', postag_counter['VBP']]]
	
	verb_tense_list, verb_tense_stats = verb_tense_data_preparation(data)

	# output file names
	verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA', 'Verb Tense',
															 'list')
	verb_stats_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NVA',
																   'Verb Tense', 'stats')

	# errorFound = IO_csv_util.list_to_csv(GUI_util.window,
	# 								 CoNLL_util.sort_output_list('Verb Tense', tense_list),
	# 								 verb_file_name)
	errorFound = IO_csv_util.list_to_csv(GUI_util.window,
										 verb_tense_list,
										 verb_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_file_name)

	errorFound = IO_csv_util.list_to_csv(GUI_util.window, verb_tense_stats, verb_stats_file_name)
	if errorFound == True:
		return filesToOpen
	filesToOpen.append(verb_stats_file_name)

	if createCharts == True:
		columns_to_be_plotted=[[0,1]]
		count_var=0
		chart_outputFilename = charts_util.run_all(columns_to_be_plotted, verb_stats_file_name, outputDir,
														 outputFileLabel='verb_tense',
														 chartPackage=chartPackage,
														 chart_type_list=['bar'],
														 chart_title="Frequency Distribution of Verb Tense",
														 column_xAxis_label_var='Verb Tense',
														 hover_info_column_list=[],
														 count_var=count_var)
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)

		# # temporary headers added, not sure why the verb_voice_list doesn't have headers
		df = pd.read_csv(verb_file_name, header=None)
		df.to_csv(verb_file_name,
				  header=["ID", "FORM", "Lemma", "POStag", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID", "Document ID", "Document",
					  "Verb Tense"])
		
		# line plots by sentence index
		chart_outputFilename = statistics_csv_util.compute_csv_column_frequencies(inputFilename=verb_file_name,
													outputDir=outputDir,
													select_col=['Verb Tense'],
													group_col=['Sentence ID'],
													chartTitle="Frequency Distribution of Verb Tense",
													chartPackage=chartPackage)
		
		if chart_outputFilename != None:
			if len(chart_outputFilename) > 0:
				filesToOpen.append(chart_outputFilename)

	return filesToOpen


def verb_stats(config_filename, inputFilename, outputDir, data, data_divided_sents, openOutputFiles, createCharts, chartPackage):
	filesToOpen = []  # Store all files that are to be opened once finished

	startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
												   'Started running VERB ANALYSES at',
												   True, '', True, '', True)

	outputFiles = verb_voice_stats(inputFilename, outputDir, data, data_divided_sents,
								   openOutputFiles, createCharts, chartPackage)

	if outputFiles != None:
		filesToOpen.extend(outputFiles)

	outputFiles = verb_modality_stats(config_filename, inputFilename, outputDir, data, data_divided_sents,
									  openOutputFiles, createCharts, chartPackage)
	if outputFiles != None:
		filesToOpen.extend(outputFiles)

	outputFiles = verb_tense_stats(inputFilename, outputDir, data, data_divided_sents,
								   openOutputFiles, createCharts, chartPackage)
	if outputFiles != None:
		filesToOpen.extend(outputFiles)

	IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running VERB ANALYSES at', True,
									   '', True, startTime, True)

	return filesToOpen

#=======================================================================================================================
#Debug use
#=======================================================================================================================
# def main():
# 	file = "C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn.csv"
# 	# debug use
# 	data, header = IO_csv_util.get_csv_data(file, True)
# 	# end debug use
# 	a,b = verb_modality_data_preparation(data)

# if __name__ == "__main__":
# 	main()
