"""
Author:

Performs iconicity analysis on a text file using Winter et al. 2024 iconicity ratings.
a 7-point rating scale going from (1) “Not iconic at all” and (7) “Very iconic.”

min_rating is hard coded at to list the most-iconic words
	min_rating=5.0
rating standard deviation set at 2
 	max_rating_sd = 2

Parameters:
    --dir [path of input directory]
        specifies directory of files to analyze
        LEAVE BLANK WHEN ANALYZING SNGLE FILE --file OPTION
    --file [path of text file]
        specifies location of specific file to analyze
        LEAVE BLANK WHEN ANALYZING ALL FILES IN A DIRECTORY --dir OPTION
    --out [path of directory]
        specifies directory to create output files
Uses iconicity measures by for 14,000+ English words.” Behavioral Research Methods, Vol. 56, pp. 1640–1655. https://doi.org/10.3758/s13428-023-02112-6

#a 7-point rating scale going from (1) “Not iconic at all” and (7) “Very iconic.”

"""
# add parameter to exclude duplicates? also mean or median analysis

import sys

import GUI_util
import IO_libraries_util
import IO_files_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "Iconicity Analysis",
										  ['os', 'csv', 'statistics', 'argparse', 'pandas', 'tkinter',
										   'time', 'stanza']) == False:
	sys.exit(0)

import csv
import os
import statistics
import time
import argparse
import pandas as pd
import tkinter.messagebox as mb
import IO_user_interface_util
import lib_util

# from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text, tokenize_stanza_text, lemmatize_stanza_word

import GUI_IO_util
import IO_csv_util
import charts_util
import statistics_csv_util

fin = open('../lib/wordLists/stopwords.txt', 'r')
stops = set(fin.read().splitlines())

# a 7-point rating scale going from (1) “Not iconic at all” and (7) “Very iconic.”
ratings = GUI_IO_util.iconicity_libPath + os.sep + "iconicity_ratings.csv"
if not os.path.isfile(ratings):
	print(
		"The file " + ratings + " could not be found. The ICONICITY analysis routine expects a csv dictionary file 'iconicity_ratings.csv' in a directory 'lib' expected to be a subdirectory of the directory where the style_analysis_iconicity_analysis_util.py script is stored.\n\nPlease, check your lib directory and try again.")
	mb.showerror(title='File not found',
				 message="The ICONICITY analysis routine expects a csv dictionary file 'iconicity_ratings.csv' in a directory 'lib' expected to be a subdirectory of the directory where the style_analysis_iconicity_analysis_util.py script is stored.\n\nPlease, check your lib directory and try again.")
	sys.exit()
data = pd.read_csv(ratings,encoding='utf-8',on_bad_lines='skip')
data_dict = {col: list(data[col]) for col in data.columns}


# print data_dict
# performs Iconicity analysis on inputFile using the Winter et al. 2024 Iconicity ratings, outputting results to a new CSV file in outputDir
# min_rating is hard coded at to list the most-iconic words
# 	min_rating=5.0
# rating standard deviation set at 2
#  	max_rating_sd = 2
def analyzefile(inputFilename, inputDir, outputDir, outputFilename,  documentID, documentName, min_rating, max_rating_sd):
	"""
	Performs iconicity analysis on the text file given as input using the Winter et al. 2024 iconicity ratings.
		ratings are on a 7-point rating scale going from (1) “Not iconic at all” and (7) “Very iconic.”
	min_rating is hard coded at to list the most-iconic words
		min_rating=5.0
	rating standard deviation set at 2
 		max_rating_sd = 2
	Outputs results to a new CSV file in outputDir.
	:param inputFilename: path of .txt file to analyze
	:param outputDir: path of directory to create new output file
	:return:
	"""

	global total_words

	# from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word
	# read file into string
	with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as myfile:
		fulltext = myfile.read()
	# end method if file is empty
	if len(fulltext) < 1:
		mb.showerror(title='File empty',
					 message='The file ' + inputFilename + ' is empty.\n\nPlease, use anoter file and try again.')
		print('Empty file ', inputFilename)
		return

	# otherwise, split into sentences
	# sentences = tokenize.sent_tokenize(fulltext)
	sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

	# check each word in sentence for iconicity and write to outputFilename
	# analyze each sentence for iconicity
	i = 0  # to store sentence index
	for s in sentences:
		i = i + 1
		# print("S" + str(i) +": " + s)
		all_words = []
		found_words = []
		score_list = []  # use the rating as scores to calculate the iconicity

		# search for each valid word's iconicity ratings
		words = tokenize_stanza_text(stanzaPipeLine(s.lower()))

		filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
		total_words = total_words + len(filtered_words)
		for index, w in enumerate(filtered_words):
			# don't process stopwords
			# if w in stops:
			# 	continue
			lemma = lemmatize_stanza_word(stanzaPipeLine(w))
			all_words.append(str(lemma))
			if lemma in data_dict['word']:
				index = data_dict['word'].index(lemma)
				# ratings are on a 7-point rating scale going from (1) “Not iconic at all” and (7) “Very iconic.”
				score = round(float(data_dict['rating'][index]), 2)
				score_sd = round(float(data_dict['rating_sd'][index]), 3)
				found_words.append('(' + str(lemma) + ', ' + str(score) + ')')
				# min_rating is hard coded at to list the most-iconic words
				# 	min_rating=5.0
				# rating standard deviation set at 2
				# 	rating_sd = 2
				if score > min_rating and score_sd < max_rating_sd:
					iconic_words.append([lemma, str(score), documentID, IO_csv_util.dressFilenameForCSVHyperlink(documentName)])
					iconic_words_list.append(lemma)
				score_list.append(score)
				# print('score: '+ str(score) + ' LEMMA: ' + str(lemma))
			else:
				continue
		# else:  # output iconicity info for this sentence
		if len(score_list) > 0:
			iconic_median = round(float(statistics.median(score_list)), 2)
			iconic_mean = round(float(statistics.mean(score_list)), 2)
			if len(score_list) == 1:
				iconic_sd = 0
			else:
				iconic_sd = round(float(statistics.stdev(score_list)), 2)
			# should sort by Document ID and Sentence ID
			if iconic_median!=0 and iconic_mean!=0:
				writer.writerow({'Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)': iconic_mean,
								 'Sentence iconicity (Median score: 1 Not iconic-7 Very iconic)': iconic_median,
								 'Standard Deviation': iconic_sd,
								 '# Words Found': "%d out of %d" % (len(found_words), len(all_words)),
								 'Percentage': str(100 * (round(float(len(found_words)) / float(len(all_words)), 2))) + '%',
								 'Found Words': ', '.join(found_words),
								 'All Words': ', '.join(all_words),
								 'Sentence ID': i,
								 'Sentence': s,
								 'Document ID': documentID,
								 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName)
								 })

	return outputFilename  # LINE ADDED

filesToOpen = []  # LINE ADDED

def main(window, inputFilename, inputDir, outputDir,  configFileName, openOutputFiles,chartPackage, dataTransformation, processType=''):
	"""
	Runs analyzefile on the appropriate files, provided that the input paths are valid.
	:param inputFilename:
	:param inputDir:
	:param outputDir:
	:return:
	"""

	if lib_util.checklibFile(
			GUI_IO_util.iconicity_libPath + os.sep + 'iconicity_ratings.csv',
			'style_analysis_iconicity_analysis_util.py') == False:
		return

	if len(outputDir) < 0 or not os.path.exists(outputDir):  # empty output
		print('No output directory specified, or path does not exist')
		sys.exit(0)
	elif len(inputFilename) == 0 and len(inputDir) == 0:  # empty input
		print('No input specified. Please give either a single file or a directory of files to analyze.')
		sys.exit(1)

	global total_words
	global iconic_words
	global iconic_words_list
	total_words = 0
	iconic_words = [] # with iconic ratings > 5
	iconic_words_list = []
	# create a subdirectory of the output directory
	outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='iconicity',
													   silent=False)
	if outputDir == '':
		return

	# min_rating is hard coded at to list the most-iconic words
	# 	min_rating=5.0
	# rating standard deviation set at 2
	#  	max_rating_sd = 2

	min_rating=5.0
	max_rating_sd=2.0
	min_rating = GUI_IO_util.slider_widget(window, "Please, select the minimum value of the iconicity rating. The suggested value is " + str(min_rating), 1, 7, min_rating)
	max_rating_sd = GUI_IO_util.slider_widget(window, "Please, select the maximum value of the iconicity rating standard deviation. The suggested value is " + str(max_rating_sd), 0, 3, max_rating_sd)

	global stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word
	from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text, tokenize_stanza_text, lemmatize_stanza_word

	startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
	                                               'Started running Iconicity Analysis at', True,silent=True)
	outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
																			   '.csv', 'iconicity-vocab', '')
	with open(outputFilename, 'w', encoding='utf-8', errors='ignore') as csvfile:
		fieldnames = ['Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)',
					  'Sentence iconicity (Median score: 1 Not iconic-7 Very iconic)',
					  'Standard Deviation',
					  '# Words Found', 'Percentage', 'Found Words', 'All Words',
					  'Sentence ID', 'Sentence','Document ID', 'Document']
		global writer
		# writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
		writer.writeheader()

		if len(inputFilename) > 0:  # handle single file
			head, tail = os.path.split(inputFilename)
			print("Processing file 1/1 " + tail)
			chart_title = tail
			if os.path.exists(inputFilename):
				filesToOpen.append(analyzefile(inputFilename, inputDir, outputDir, outputFilename, 1, inputFilename, min_rating, max_rating_sd))
			else:
				print('Input file "' + inputFilename + '" is invalid.')
				sys.exit(0)
		elif len(inputDir) > 0:  # handle directory
			head, tail = os.path.split(inputDir)
			chart_title = "Directory: " + tail
			documentID = 0
			inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt', silent=False, configFileName=configFileName)

			Ndocs = len(inputDocs)
			if Ndocs == 0:
				return filesToOpen

			index = 0
			if os.path.isdir(inputDir):
				directory = os.fsencode(inputDir)
				for file in inputDocs:
					filename = os.path.join(inputDir, os.fsdecode(file))
					if filename.endswith(".txt"):
						index = index + 1
						head, tail = os.path.split(filename)
						print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
						documentID += 1
						analyzefile(filename, inputDir, outputDir, outputFilename, documentID,
														   filename, min_rating, max_rating_sd)  # LINE ADDED (edited)
			else:
				print('Input directory "' + inputDir + '" is invalid.')
				sys.exit(0)

		outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilename, outputDir,
												  columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=[
				'Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)'],
												  # columns_to_be_plotted_bySent= [[10, 7, 0]],
												  chart_title='Frequency Distribution of Sentence Iconicity Scores (1 Not iconic-7 Very iconic)',
												  count_var=1,  # 0 for numeric field
												  hover_label=[],
												  outputFileNameType='',
												  column_xAxis_label='Sentence iconicity scores',
												  groupByList=['Document'],
												  plotList=[],
												  chart_title_label='Sentence Iconicity Statistics')
		if outputFiles != None:
			if isinstance(outputFiles, str):
				filesToOpen.append(outputFiles)
			else:
				filesToOpen.extend(outputFiles)

		if len(iconic_words) > 0:
			iconic_words_set = set(iconic_words_list) # the set has only distinct words
			mb.showwarning(title='Warning',
						   message='The iconicity script has found ' + str(len(iconic_words)) + ' iconic words, ' + str(len(iconic_words_set)) + ' of which distinct, (out of ' + str(total_words) + ' words in your input), using the Winter et al., 2024, scale of iconic English words.\n\nThe minimum threshold for iconicity has been set to 5.0. You may wish to increase that value.')

			print(str('\n\n' + str(len(iconic_words))) + ' iconic words found, ' + str(len(iconic_words_set)) + ' of which distinct, (out of ' + str(total_words) + ' words in your input), using the Winter et al., 2024, scale of iconic English words. The minimum threshold for iconicity has been set to 5.0. You may wish to increase that value.')

			temp_outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
																	 'iconic-words')
			iconic_words.insert(0,['Word','Iconicity rating','Document ID','Document'])
			IO_error = IO_csv_util.list_to_csv(0, iconic_words, temp_outputFilename)
			if not IO_error:
				filesToOpen.append(temp_outputFilename)
				outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, temp_outputFilename, outputDir,
																   columns_to_be_plotted_xAxis=[],
														  		   columns_to_be_plotted_yAxis=['Word'],
																   # columns_to_be_plotted_bySent= [[10, 7, 0]],
																   chart_title='Frequency Distribution of Iconic Words',
																   count_var=1, # 0 for numeric field
																   hover_label=[],
																   outputFileNameType='',
																   column_xAxis_label='Word',
																   groupByList=['Document'],
																   plotList=[],
																   chart_title_label='Iconic Words')
				if outputFiles!=None:
					if isinstance(outputFiles, str):
						filesToOpen.append(outputFiles)
					else:
						filesToOpen.extend(outputFiles)

	IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
	                                       'Finished running Iconicity Analysis at', True, '', True, startTime, False)

	return filesToOpen

if __name__ == '__main__':
	# get arguments from command line
	parser = argparse.ArgumentParser(description='Iconicity analysis with iconicity ratings by Winter et al. 2024')
	parser.add_argument('--file', type=str, dest='inputFilename', default='',
						help='a string to hold the path of one file to process')
	parser.add_argument('--dir', type=str, dest='inputDir', default='',
						help='a string to hold the path of a directory of files to process')
	parser.add_argument('--out', type=str, dest='outputDir', default='',
						help='a string to hold the path of the output directory')
	parser.add_argument('--outfile', type=str, dest='outputFilename', default='',
						help='output file name')

	args = parser.parse_args()

	# run main
	sys.exit(main(args.inputFilename, args.inputDir, args.outputDir, args.outputFilename))

# example: a single file
# python ConcretenessAnalysis.py --file "C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\MURPHY\Murphy Miracles thicker than fog CORENLP.txt" --out C:\Users\rfranzo\Desktop\NLP_output
