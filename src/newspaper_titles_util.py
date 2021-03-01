#!/usr/bin/python
# Python version target: 3.6.3 Anaconda

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Newspaper titles",['os','re','nltk','glob','string'])==False:
    sys.exit(0)

import glob
import os
from nltk.tokenize import sent_tokenize
import string

# criteria for title are no puntuation and 
#	a shorter (user determined) sentence in number of words

#Title_length_limit = int(sys.argv[1])
#TITLENESS = sys.argv[2]
#input_dir_path = sys.argv[3]
#output_dir_path = sys.argv[4]


# Check whether a sentence is title
# criteria for title are no puntuation and a shorter (user determined) sentence
def isTitle(sentence):
	if sentence[-1] not in string.punctuation:
		if len(sentence) < Title_length_limit:
			# print sentence
			return True
	if sentence.isupper():
		# print sentence
		return True
	if sentence.istitle():
		# print sentence
		return True

def newspaper_titles(window,input_dir_path,output_dir_path,openOutputFiles):

	NUM_DOCUMENT = len(glob.glob(os.path.join(input_dir_path, '*.txt')))

	Title_length_limit = 100
	TITLENESS = 'NO'

	titleness = True
	if TITLENESS == "NO":
		titleness = False

	# DOCUMENTS WITH TITLES
	count = 0
	titles = []
	path_aritclesWithTitles = output_dir_path + '/documentsWithTitles'
	if not os.path.exists(path_aritclesWithTitles):
	    os.makedirs(path_aritclesWithTitles)
	for filename in glob.glob(os.path.join(input_dir_path, '*.txt')):
		print("Processing file " + filename)
		with open(filename,'r', encoding='utf-8', errors='ignore') as each:
			sentences = []
			sentences = each.read().split('\r')
			lst = []
			for sentence in sentences:
				for s in sentence.split('\n'):
					lst.append(s)
			sentences = lst
			sentences = [each.strip() for each in sentences if each.strip()] 
			filename = filename.split('\\')[-1]
			file_path = path_aritclesWithTitles + '/%s' % filename
			with open(file_path, 'w', encoding='utf-8') as out:
				for sentence in sentences:
					if isTitle(sentence):
						if sentence and sentence[-1]!='.':
							out.write(sentence + '.')
						else:
							out.write(sentence)
					else:
						for one in sent_tokenize(sentence):#.decode('utf-8')):
							out.write(one)#.encode('utf-8'))
							out.write(' ')
				# titles.append((title,filename))
		count += 1

	# DOCUMENTS WITHOUT TITLES
	count = 0
	titles = []
	path_documents = output_dir_path + '/documentsWithoutTitles'
	if not os.path.exists(path_documents):
		os.makedirs(path_documents)
	for filename in glob.glob(os.path.join(input_dir_path, '*.txt')):
		print("Processing file " + filename)
		with open(filename,'r', encoding='utf-8', errors='ignore') as each:
			sentences = []
			sentences = each.read().split('\r')
			lst = []
			for sentence in sentences:
				for s in sentence.split('\n'):
					lst.append(s)
			sentences = lst
			sentences = [each.strip() for each in sentences if each.strip()] 
			filename = filename.split('\\')[-1]
			file_path = path_documents + '/%s' % filename
			# file_path = '/Users/apple/Desktop/Roberto-Research/TitleExtractor/output/data%d__%s' %(count, filename)
			with open(file_path, 'w', encoding='utf-8') as out:
				title = []
				for sentence in sentences:
					if isTitle(sentence):
						title.append(sentence)
					else:
						for one in sent_tokenize(sentence):#.decode('utf-8')):
							out.write(one)
							out.write(' ')
				titles.append((title,filename))
		count += 1
		# print(count)


	# TITLES ONLY
	path_title = output_dir_path + '/titles'
	if not os.path.exists(path_title):
	    os.makedirs(path_title)
	path_title = path_title + '/titles.txt'
	with open(path_title,'w') as output:
		count = 0
		for i,title in enumerate(titles):
			if title:
				count += 1
			output.write('\n')
			# a boundary can be added
			if titleness:
				output.write('Document %d: %s ' % (i,title[1]))

			output.write('\n')
			for t in title[0]:
				if t and t[-1]!='.':
					output.write(t + '.')
				else:
					output.write(t)
				output.write('\n')

	print(" %s documents out of %d have generated titles." % (NUM_DOCUMENT,count))
	print("The percentage of documents processed is %f" % ((float(count)/NUM_DOCUMENT) * 100))

#newspaper_titles(window,input_dir_path,output_dir_path,openOutputFiles)