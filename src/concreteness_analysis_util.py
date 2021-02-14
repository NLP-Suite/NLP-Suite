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
    --mode [mode]
        takes either "median" or "mean"; determines which is used to calculate sentence concreteness values
Uses concreteness measures by Brysbaert, Marc, Amy Beth Warriner, and Victor Kuperman. 2014. 
	“Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas.” 
	Behavioral Research Methods, Vol. 46, No. 3, pp. 904–911.  

#a 5-point rating scale going from abstract to concrete

"""
# add parameter to exclude duplicates? also mean or median analysis

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "Concreteness Analysis",
										  ['nltk', 'os', 'csv', 'statistics', 'argparse', 'pandas', 'tkinter',
										   'time']) == False:
	sys.exit(0)

import csv
import os
import statistics
import time
import argparse
import pandas as pd
import tkinter.messagebox as mb

from nltk import tokenize
from nltk import word_tokenize

# check Punkt
IO_libraries_util.import_nltk_resource(GUI_util.window, 'tokenizers/punkt', 'punkt')
# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/WordNet', 'WordNet')
from nltk.stem.wordnet import WordNetLemmatizer

# check stopwords
IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/stopwords', 'stopwords')

from nltk.corpus import stopwords

import GUI_IO_util
import IO_csv_util

stops = set(stopwords.words("english"))
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
def analyzefile(input_file, output_dir, output_file, mode, documentID, documentName):
	"""
	Performs concreteness analysis on the text file given as input using the Brysbaert et al. concreteness ratings.
	Outputs results to a new CSV file in output_dir.
	:param input_file: path of .txt file to analyze
	:param output_dir: path of directory to create new output file
	:param mode: determines how concreteness values for a sentence are computed (median or mean)
	:return:
	"""

	# read file into string
	with open(input_file, 'r', encoding='utf-8', errors='ignore') as myfile:
		fulltext = myfile.read()
	# end method if file is empty
	if len(fulltext) < 1:
		mb.showerror(title='File empty',
					 message='The file ' + input_file + ' is empty.\n\nPlease, use anoter file and try again.')
		print('Empty file ' + input_file)
		return

	# otherwise, split into sentences
	sentences = tokenize.sent_tokenize(fulltext)
	i = 1  # to store sentence index
	# check each word in sentence for concreteness and write to output_file

	# analyze each sentence for concreteness
	for s in sentences:
		# print("S" + str(i) +": " + s)
		all_words = []
		found_words = []
		total_words = 0
		score_list = []  # use the Conc.M as scores to calculate the concreteness

		# search for each valid word's concreteness ratings
		# words = nlp.pos_tag(s.lower())
		words = word_tokenize(s.lower())

		filtered_words = [word for word in words if word.isalpha()]  # strip out words with punctuation
		for index, w in enumerate(filtered_words):
			# don't process stopwords
			if w in stops:
				continue

			# lemmatize word
			lmtzr = WordNetLemmatizer()
			lemma = lmtzr.lemmatize(w, pos='v')
			if lemma == w:
				lemma = lmtzr.lemmatize(w, pos='n')

			all_words.append(str(lemma))

			if lemma in data_dict['Word']:
				index = data_dict['Word'].index(lemma)
				score = float(data_dict['Conc.M'][index])
				found_words.append('(' + str(lemma) + ', ' + str(score) + ')')
				score_list.append(score)
			# print('score: '+ str(score) + ' LEMMA: ' + str(lemma))

			# search for lemmatized word in Brysbaert et al. concreteness ratings
			if len(found_words) == 0:  # no words found in Brysbaert et al. concreteness ratings for this sentence
				writer.writerow({'Document ID': documentID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName),
								 'Sentence ID': i,
								 'Sentence': s,
								 'Concreteness (Mean score)': 'N/A',
								 'Concreteness (Median score)': 'N/A',
								 'Standard Deviation': 'N/A',
								 '# Words Found': 0,
								 'Percentage': '0.0%',
								 'Found Words': 'N/A',
								 'All Words': all_words,

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
				writer.writerow({'Document ID': documentID, 'Document': IO_csv_util.dressFilenameForCSVHyperlink(documentName),
								 'Sentence ID': i,
								 'Sentence': s,
								 'Concreteness (Mean score)': conc_mean,
								 'Concreteness (Median score)': conc_median,
								 'Standard Deviation': conc_sd,
								 '# Words Found': "%d out of %d" % (len(found_words), len(all_words)),
								 'Percentage': str(100 * (float(len(found_words)) / float(len(all_words)))) + '%',
								 'Found Words': ', '.join(found_words),
								 'All Words': ', '.join(all_words)

								 })

			i += 1


	return output_file  # LINE ADDED

fileNamesToPass = []  # LINE ADDED


def main(input_file, input_dir, output_dir, output_file, mode):
	"""
	Runs analyzefile on the appropriate files, provided that the input paths are valid.
	:param input_file:
	:param input_dir:
	:param output_dir:
	:param mode:
	:return:
	"""

	if len(output_dir) < 0 or not os.path.exists(output_dir):  # empty output
		print('No output directory specified, or path does not exist')
		sys.exit(0)
	elif len(input_file) == 0 and len(input_dir) == 0:  # empty input
		print('No input specified. Please give either a single file or a directory of files to analyze.')
		sys.exit(1)
	with open(output_file, 'w', encoding='utf-8', errors='ignore') as csvfile:
		fieldnames = ['Document ID', 'Document','Sentence ID', 'Sentence', 'Concreteness (Mean score)', 'Concreteness (Median score)',
					  'Standard Deviation',
					  '# Words Found', 'Percentage', 'Found Words', 'All Words']
		global writer
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
		writer.writeheader()

		if len(input_file) > 0:  # handle single file
			if os.path.exists(input_file):
				fileNamesToPass.append(analyzefile(input_file, output_dir, output_file, mode, 1, input_file))
				# output_file = analyzefile(input_file, output_dir, output_file, mode)
			else:
				print('Input file "' + input_file + '" is invalid.')
				sys.exit(0)
		elif len(input_dir) > 0:  # handle directory
			documentID = 0
			if os.path.isdir(input_dir):
				directory = os.fsencode(input_dir)
				for file in os.listdir(directory):
					filename = os.path.join(input_dir, os.fsdecode(file))
					if filename.endswith(".txt"):
						start_time = time.time()
						print("Started CONCRETENESS analysis of " + filename + "...")
						documentID += 1
						analyzefile(filename, output_dir, output_file, mode, documentID,
														   filename)  # LINE ADDED (edited)
						print("Finished CONCRETENESS analysis " + filename + " in " + str(
							(time.time() - start_time)) + " seconds")
			else:
				print('Input directory "' + input_dir + '" is invalid.')
				sys.exit(0)

	return fileNamesToPass  # LINE ADDED

if __name__ == '__main__':
	# get arguments from command line
	parser = argparse.ArgumentParser(description='Concreteness analysis with Concreteness ratings by Brysbaert et al.')
	parser.add_argument('--file', type=str, dest='input_file', default='',
						help='a string to hold the path of one file to process')
	parser.add_argument('--dir', type=str, dest='input_dir', default='',
						help='a string to hold the path of a directory of files to process')
	parser.add_argument('--out', type=str, dest='output_dir', default='',
						help='a string to hold the path of the output directory')
	parser.add_argument('--outfile', type=str, dest='output_file', default='',
						help='output file name')
	parser.add_argument('--mode', type=str, dest='mode', default='mean',
						help='mode with which to calculate concreteness in the sentence: mean or median')

	args = parser.parse_args()

	# run main
	sys.exit(main(args.input_file, args.input_dir, args.output_dir, args.output_file, args.mode))

# example: a single file
# python ConcretenessAnalysis.py --file "C:\Users\rfranzo\Documents\ACCESS Databases\PC-ACE\NEW\DATA\CORPUS DATA\MURPHY\Murphy Miracles thicker than fog CORENLP.txt" --out C:\Users\rfranzo\Desktop\NLP_output
