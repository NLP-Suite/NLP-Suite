"""
Author: Doris Zhou February 19, 2018
Modified by Gabriel Wang May 2018
Modified by Roberto Franzosi February 2019
Modified by Josh Karol October 2019

Performs concreteness analysis on a text file using Brysbaert et al. concreteness ratings.
Parameters:
    --dir [path of input directory]
        specifies directory of files to analyze
        LEAVE BLANK WHEN ANALYZING SNGLE FILE --file OPTION
    --file [path of text file]
        specifies location of specific file to analyze
        LEAVE BLANK WHEN ANALYZING ALL FILES IN A DIRECTORY --dir OPTION
    --out [path of directory]
        specifies directory to create output files
Uses concreteness measures by Brysbaert, Marc, Amy Beth Warriner, and Victor Kuperman. 2014.
	“Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas.” 
	Behavioral Research Methods, Vol. 46, No. 3, pp. 904–911.  

#a 5-point rating scale going from abstract to concrete

"""
# add parameter to exclude duplicates? also mean or median analysis

import sys

from py import process
import GUI_util
import IO_libraries_util
import IO_files_util
import charts_Excel_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Concreteness Analysis",
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


from stanza_functions import stanzaPipeLine, word_tokenize_stanza, sent_tokenize_stanza, lemmatize_stanza

import GUI_IO_util
import IO_csv_util

fin = open('../lib/wordLists/stopwords.txt', 'r')
stops = set(fin.read().splitlines())

ratings = GUI_IO_util.concreteness_libPath + os.sep + "Concreteness_ratings_Brysbaert_et_al_BRM.csv"
if not os.path.isfile(ratings):
	print(
		"The file " + ratings + " could not be found. The CONCRETENESS analysis routine expects a csv dictionary file 'Concreteness_ratings_Brysbaert_et_al_BRM.csv' in a directory 'lib' expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again.")
	mb.showerror(title='File not found',
				 message='The concreteness analysis routine expects a csv dictionary file "Concreteness_ratings_Brysbaert_et_al_BRM.csv" in a directory "lib" expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again')
	sys.exit()
data = pd.read_csv(ratings)
data_dict = {col: list(data[col]) for col in data.columns}


# print data_dict
# performs concreteness analysis on inputFile using the Brysbaert et al. concreteness ratings, outputting results to a new CSV file in outputDir
def analyzefile(inputFilename, outputDir, outputFilename,  documentID, documentName):
	"""
	Performs concreteness analysis on the text file given as input using the Brysbaert et al. concreteness ratings.
	Outputs results to a new CSV file in outputDir.
	:param inputFilename: path of .txt file to analyze
	:param outputDir: path of directory to create new output file
	:return:
	"""

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
	sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))

	i = 1  # to store sentence index
	# check each word in sentence for concreteness and write to outputFilename

	# analyze each sentence for concreteness
	for s in sentences:
		# print("S" + str(i) +": " + s)
		all_words = []
		found_words = []
		total_words = 0
		score_list = []  # use the Conc.M as scores to calculate the concreteness

		# search for each valid word's concreteness ratings
		# words = nlp.pos_tag(s.lower())
		# words = word_tokenize(s.lower())
		words = word_tokenize_stanza(stanzaPipeLine(s.lower()))

		filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
		for index, w in enumerate(filtered_words):
			# don't process stopwords
			if w in stops:
				continue

			# lemmatize word
			# lmtzr = WordNetLemmatizer()
			# lemma = lmtzr.lemmatize(w, pos='v')
			lemma = lemmatize_stanza(stanzaPipeLine(w))
			# if lemma == w:
			# 	lemma = lmtzr.lemmatize(w, pos='n')

			all_words.append(str(lemma))

			if lemma in data_dict['Word']:
				index = data_dict['Word'].index(lemma)
				score = float(data_dict['Conc.M'][index])
				found_words.append('(' + str(lemma) + ', ' + str(score) + ')')
				score_list.append(score)
			# print('score: '+ str(score) + ' LEMMA: ' + str(lemma))

			# search for lemmatized word in Brysbaert et al. concreteness ratings
			if len(found_words) == 0:  # no words found in Brysbaert et al. concreteness ratings for this sentence
				# writer.writerow({'Concreteness (Mean score)': 'N/A',
				# 				 'Concreteness (Median score)': 'N/A',
				# 				 'Standard Deviation': 'N/A',
				writer.writerow({'Concreteness (Mean score)': 0,
								 'Concreteness (Median score)': 0,
							     'Standard Deviation': 0,
								 '# Words Found': 0,
								 'Percentage': '0.0%',
								 'Found Words': 0,
								 'All Words': all_words,
								 'Sentence ID': i,
								 'Sentence': s, 'Document ID': documentID,
								 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName)
								 })
				i += 1
		else:  # output concreteness info for this sentence

			# print('score_list: '+ str(score_list) + ' LEMMA: ' + str(lemma))

			if len(score_list) > 1:
				conc_median = statistics.median(score_list)
				conc_mean = statistics.mean(score_list)
				conc_sd = statistics.stdev(score_list)
				# conc_sd = 'N/A'
				# if len(score_list) > 1:
				# print(conc_m,conc_sd)
				writer.writerow({'Concreteness (Mean score)': conc_mean,
								 'Concreteness (Median score)': conc_median,
								 'Standard Deviation': conc_sd,
								 '# Words Found': "%d out of %d" % (len(found_words), len(all_words)),
								 'Percentage': str(100 * (float(len(found_words)) / float(len(all_words)))) + '%',
								 'Found Words': ', '.join(found_words),
								 'All Words': ', '.join(all_words),
								 'Sentence ID': i,
								 'Sentence': s,
								 'Document ID': documentID,
								 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName)
								 })

			i += 1


	return outputFilename  # LINE ADDED

filesToOpen = []  # LINE ADDED

def main(window, inputFilename, inputDir, outputDir, openOutputFiles,createExcelCharts, processType=''):
	"""
	Runs analyzefile on the appropriate files, provided that the input paths are valid.
	:param inputFilename:
	:param inputDir:
	:param outputDir:
	:return:
	"""

	if len(outputDir) < 0 or not os.path.exists(outputDir):  # empty output
		print('No output directory specified, or path does not exist')
		sys.exit(0)
	elif len(inputFilename) == 0 and len(inputDir) == 0:  # empty input
		print('No input specified. Please give either a single file or a directory of files to analyze.')
		sys.exit(1)
	outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
																			   '.csv', 'abstr-concret-vocab', 'stats')
	with open(outputFilename, 'w', encoding='utf-8', errors='ignore') as csvfile:
		fieldnames = ['Concreteness (Mean score)', 'Concreteness (Median score)',
					  'Standard Deviation',
					  '# Words Found', 'Percentage', 'Found Words', 'All Words',
					  'Sentence ID', 'Sentence','Document ID', 'Document']
		global writer
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
		writer.writeheader()

		if len(inputFilename) > 0:  # handle single file
			head, tail = os.path.split(inputFilename)
			print("Processing file 1/1 " + tail)
			chart_title = tail
			if os.path.exists(inputFilename):
				filesToOpen.append(analyzefile(inputFilename, outputDir, outputFilename, 1, inputFilename))
			else:
				print('Input file "' + inputFilename + '" is invalid.')
				sys.exit(0)
		elif len(inputDir) > 0:  # handle directory
			head, tail = os.path.split(inputDir)
			chart_title = "Directory: " + tail
			documentID = 0
			inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')

			Ndocs = str(len(inputDocs))
			index = 0
			if os.path.isdir(inputDir):
				directory = os.fsencode(inputDir)
				for file in os.listdir(directory):
					filename = os.path.join(inputDir, os.fsdecode(file))
					if filename.endswith(".txt"):
						index = index + 1
						head, tail = os.path.split(filename)
						print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
						documentID += 1
						analyzefile(filename, outputDir, outputFilename, documentID,
														   filename)  # LINE ADDED (edited)
			else:
				print('Input directory "' + inputDir + '" is invalid.')
				sys.exit(0)
	if createExcelCharts == True:
		inputFilename = outputFilename
		columns_to_be_plotted = [[7, 0], [7, 1]]
		hover_label = ['Sentence', 'Sentence']
		# Tony Chen Gu
		# what is needed here is the new compute_csv_column_frequencies
		Excel_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
														 outputFileLabel='Concret',
														 chart_type_list=["line"],
														 chart_title='Concreteness Scores by Sentence Index\n' + chart_title,
														 column_xAxis_label_var='Sentence index',
														 hover_info_column_list=hover_label,
														 count_var=0,
														 column_yAxis_label_var='Scores')
		if Excel_outputFilename != "":
			filesToOpen.append(Excel_outputFilename)

	return filesToOpen  # LINE ADDED

if __name__ == '__main__':
	# get arguments from command line
	parser = argparse.ArgumentParser(description='Concreteness analysis with Concreteness ratings by Brysbaert et al.')
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
