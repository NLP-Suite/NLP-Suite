
#!/usr/bin/python
# Python version target: 3.6.3 Anaconda

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Newspaper titles",['os','re','nltk','glob','pandas','string','tkinter'])==False:
    sys.exit(0)

import glob
import os
from nltk.tokenize import sent_tokenize
import pandas as pd
import string
import tkinter.messagebox as mb
import re

import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import IO_csv_util

# inputFilename contains path
def remove_blank_lines(window,inputFilename,input_main_dir_path, output_dir_path='',openOutputFiles=False):
    if inputFilename!="":
        input_main_dir_path, tail = os.path.split(inputFilename)
    output_dir_path = os.path.join(input_main_dir_path,"NoBlankLines")
    if IO_files_util.make_directory(output_dir_path)==False:
        return
    files = []
    files=IO_files_util.getFileList(inputFilename, input_main_dir_path, fileType='txt')
    for file in files:
        head, tail = os.path.split(file)
        outputFilename=os.path.join(output_dir_path,tail)
        with open(file,encoding='utf_8',errors='ignore') as infile, open(outputFilename, 'w',encoding='utf_8',errors='ignore') as outfile:
            for line in infile:
                if not line.strip(): continue  # skip the empty line
                outfile.write(line)  # non-empty line. Write it to output
    if inputFilename!="":
        mb.showwarning(title='Blank lines removed',
                       message='Blank lines were removed from the input file.\n\nThe new file was saved in a subdirectory of the input file\n  '+output_dir_path)
    else:
        mb.showwarning(title='Blank lines removed',
                       message='Blank lines were removed from '+str(len(files)) +' files in the input directory.\n\nThe new files were saved in a subdirectory of the input directory\n  '+output_dir_path)

# criteria for title are no puntuation and
#	a shorter (user determined) sentence in number of words

#Title_length_limit = int(sys.argv[1])
#TITLENESS = sys.argv[2]
#input_dir_path = sys.argv[3]
#output_dir_path = sys.argv[4]


# Check whether a sentence is title
# criteria for title are no puntuation and a shorter (user determined) sentence
def isTitle(sentence,Title_length_limit):
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

def newspaper_titles(window,inputFilename,input_dir_path,output_dir_path,openOutputFiles):

    if input_dir_path=='' and inputFilename!='':
        NUM_DOCUMENT=1
    else:
        NUM_DOCUMENT = len(glob.glob(os.path.join(input_dir_path, '*.txt')))
    if NUM_DOCUMENT==0:
        return
    Title_length_limit = 100

    # Title length pop up widget
    # window, textCaption, lower_bound, upper_bound, default_value
    val = GUI_IO_util.slider_widget(GUI_util.window,
                                         "Please, select the value for number of characters in a document title. The suggested value is " + str(
                                             Title_length_limit) + ".", 1, 1000, 100)
    Title_length_limit = val

    TITLENESS = 'NO'

    titleness = True
    if TITLENESS == "NO":
        titleness = False

    # DOCUMENTS WITH TITLES
    count = 0
    titles = []

    if inputFilename!="":
        input_main_dir_path, tail = os.path.split(inputFilename)
    path_aritclesWithTitles = os.path.join(input_dir_path,'documentsWithTitles')
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
            file_path = os.path.join(path_aritclesWithTitles,filename)
            with open(file_path, 'w', encoding='utf-8',errors='ignore') as out:
                for sentence in sentences:
                    if isTitle(sentence,Title_length_limit):
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
    path_documents = os.path.join(input_dir_path,'documentsWithoutTitles')
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
            file_path = os.path.join(path_documents,filename)
            # file_path = '/Users/apple/Desktop/Roberto-Research/TitleExtractor/output/data%d__%s' %(count, filename)
            with open(file_path, 'w', encoding='utf-8',errors='ignore') as out:
                title = []
                for sentence in sentences:
                    if isTitle(sentence,Title_length_limit):
                        title.append(sentence)
                    else:
                        for one in sent_tokenize(sentence):#.decode('utf-8')):
                            out.write(one)
                            out.write(' ')
                titles.append((title,filename))
        count += 1
        # print(count)


    # TITLES ONLY
    path_title = os.path.join(input_dir_path,'titles')
    if not os.path.exists(path_title):
        os.makedirs(path_title)
    path_title = os.path.join(path_title,'titles.txt')
    with open(path_title,'w',encoding='utf_8',errors='ignore') as output:
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

    if count==0:
        if NUM_DOCUMENT==1:
            msgString="The document has not generated separate titles."
        else:
            msgString="No documents have generated separate titles."
    else:
        msgString == "%s documents out of %d have generated titles." % (NUM_DOCUMENT,count) + "\n\nThe percentage of documents processed is %f" % ((float(count)/NUM_DOCUMENT) * 100)
    # msgString=" %s documents out of %d have generated titles." % (NUM_DOCUMENT, count)
    if count>0:
        if inputFilename!="":
            msgString=msgString+"\n\nThe files were saved in subdirectories of the input file directory\n\n  "+input_dir_path
        else:
            msgString=msgString+"\n\nThe files were saved in subdirectories of the input directory\n\n  "+input_dir_path

    mb.showwarning(title='Document titles', message=msgString)

# non-ASCII apostrophes and quotes (e.g., those coming from Windows Words) will show up in a csv file (not in Excel or Mac) as weird characters
#	although they do not break any script coode
# % will break the CoreNLP code
# The reasons are explained here: https://docs.oracle.com/javase/8/docs/api/java/net/URLDecoder.html
#   The character "%" is allowed but is interpreted as the start of a special escaped sequence.
# Needs special handling https://stackoverflow.com/questions/6067673/urldecoder-illegal-hex-characters-in-escape-pattern-for-input-string
# https://stackoverflow.com/questions/7395789/replacing-a-weird-single-quote-with-blank-string-in-python
def convert_quotes(window,inputFilename, inputDir,temp1='',temp2=''):
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs=len(inputDocs)
    index=0
    result= IO_user_interface_util.input_output_save("Convert apostrophes/quotes/%")
    if result ==False:
        return
    docError = 0
    for doc in inputDocs:
        index = index + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)
        with open(doc, 'r+',encoding='utf_8',errors='ignore') as file:
            fullText = file.read()
            # https://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
            # if u"\u2018" in fullText:
            # 	print("u\u2018")
            # if u"\u2019" in fullText:
            # 	print("u\u2019")
            # if u"\u201C" in fullText:
            # 	print("u\u201C")
            # if u"\u201D" in fullText:
            # 	print("u\u201D")
            if (u"%" in fullText) or (u"\u2018" in fullText) or (u"\u2019" in fullText) or (u"\u201C" in fullText) or (u"\u201D" in fullText):
                # u0027 apostrophe
                fullText = str(fullText).replace("%", "percent")  # left single quote
                fullText = str(fullText).replace(u"\u2018", u"\u0027")  # left single quote
                fullText = str(fullText).replace(u"\u2019", u"\u0027")  # right single quote
                fullText = str(fullText).replace(u"\u201C", '"') #left double quote
                fullText = str(fullText).replace(u"\u201D", '"') #right double quote
                docError = docError + 1
                file.seek(0)
                file.write(fullText)
                file.close()

    if docError>0:
        if docError==1:
            mb.showwarning(title='Non-ASCII punctuations converted',message=str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' document was edited to convert non-ASCII apostrophes and/or quotes and % to percent.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE.')
        else:
            mb.showwarning(title='Non-ASCII punctuations converted',message=str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' documents were edited to convert non-ASCII apostrophes and/or quotes and % to percent.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILES.')
    else:
        mb.showwarning(title='Non-ASCII punctuations converted', message=str(Ndocs) + ' document(s) processed.\n\nNo documents were found with non-ASCII apostrophes or quotes and % to percent.')


# TODO to be completed w/o opening and closing the txt file for every string processed
#Finished
# def find_replace_string_csvINPUT(window, inputFilename_txt, inputFilename_csv, outputDir, openOutputFiles):
# 	df = pd.read_csv(inputFilename_csv)
# 	try:
# 		original = df['Original']
# 		corrected = df['Corrected']
# 	except:
# 		mb.showwarning(title='CSV Spelling File',
# 					   message='Please, select a csv file with spelling correction information, or check the headers of that csv file for Original and Corrected')
# 		print(
# 			"Please select a csv file with spelling correction information, or check the header of that csv file for Original and Corrected")
# 		return

# 	# loop through input spelling csv file for each spelling error to replaced
# 	l = len(original)
# 	outputstring = ''
# 	outputFilename = IO_files_util.generate_output_file_name(inputFilename_txt, '', outputDir, '.txt', "spelling","corrected")
# 	with open(inputFilename_txt, 'r+',encoding='utf_8',errors='ignore') as file:
# 		fullText = file.read()
# 	for i in range(l):
# 		if corrected[i] != '':
# 			print('Original: ', original[i], ' Corrected: ', corrected[i])
# # 			find_replace_string(window, inputFilename_txt, inputDir, outputDir, openOutputFiles,
# # 												  string_IN=original[i], string_OUT=corrected[i])

# 		if (string_IN in fullText):
# 			fullText = str(fullText).replace(str(string_IN), str(string_OUT))
# 			docError = docError + 1
# 			file.seek(0)
# 			file.write(fullText)
# 			file.close()

def find_replace_string(window,inputFilename, inputDir, outputDir, openOutputFiles,string_IN=[],string_OUT=[],silent=False):
    #edited by Claude Hu 02/2021
    #string_IN=[],string_OUT=[], in the form as list so that running this function can finish replacement of multiple strings without open one file repetitively
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    filesToOpen=[]
    Ndocs=len(inputDocs)
    index=0
    filesToOpen=[]
    result= IO_user_interface_util.input_output_save("Find & Replace")
    if result ==False:
        return
    if string_IN == []:#if string_IN empty, string_IN and string_OUT will be typed in
        string_in, string_out = GUI_IO_util.enter_value_widget("Enter the FIND & REPLACE strings (CASE SENSITIVE)", 'Find',2,'','Replace','')
        #put input strings into list so that they can be processed
        string_IN = [string_in]
        string_OUT = [string_out]
    elif len(string_IN) != len(string_OUT):#make sure the list of FIND strings and REPLACE strings have same length, so that each can be matched
        mb.showwarning(title='Different number of FIND & REPLACE strings', message='The Find & Replace string function requires same number of FIND & REPLACE strings.')
        return
    if string_IN == []:#if still empty
        mb.showwarning(title='Missing string', message='The Find & Replace string function requires a non-empty FIND string.\n\nPlease, enter the FIND string and try again.')
        return

    l = len(string_IN)
    docError = 0
    indexSV=0
    csv_output=[]
    changed_values=[]
    for doc in inputDocs:
        index = index + 1
        head, tail = os.path.split(doc)
        print("Processing file " + str(index) + "/" + str(Ndocs) + " " + tail)

        with open(doc, 'r+',encoding='utf_8',errors='ignore') as file:
            fullText = file.read()
            # process the range of words when coming with the values in a csv file
            for i in range(l):
                if (str(string_IN[i]) in str(fullText)):
                    # # use regular expression replace to check for distinct words (e.g., he not in held)
                    # \b beginning and ending of word
                    # \w word character including numbers and characters
                    fullText = re.sub(rf"\b(?=\w){str(string_IN[i])}\b(?!\w)", str(string_OUT[i]), fullText)
                    # fullText = re.sub(rf”(?<=\w) {str(string_IN[i])} (?<=\W)”, str(string_OUT[i]), fullText)
                    if index!=indexSV:
                        docError = docError + 1
                        indexSV = index
                    file.seek(0)
                    # clear the input file; for some bizarre reason it appends the search word otherwise
                    file.truncate(0)
                    file.write(fullText)
                    changed_values.extend([[string_IN[i],string_OUT[i],index, IO_csv_util.dressFilenameForCSVHyperlink(doc)]])
            file.close()

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'find_replace')
    header = ['Find string', 'Replace string', 'Document ID', 'Document']
    changed_values.insert(0, header)
    IO_error = IO_csv_util.list_to_csv(window, changed_values, outputFilename)

    if docError>0:
        if len(string_IN) == 1 and docError == 1:#if only one FIND string, it can be typed in the message box
            if silent == False:
                mb.showwarning(title='String edit',message=str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' document was edited to replace the string '+ str(string_IN[0]) + ' with the string ' + str(string_OUT) + '\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE.')
            else:
                print(str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' document was edited to replace the string '+ str(string_IN[0]) + ' with the string ' + str(string_OUT[0]) + '\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE.')
        else:#when the length of FIND / REPLACE strings > 1, no actual string will be typed in the message box or printout information
            if silent == False:
                mb.showwarning(title='String edit',message=str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' document(s) edited replacing strings.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE(S).')
            else:
                print(str(Ndocs) + ' document(s) processed.\n\n' + str(docError)+' document(s) edited replacing strings.\n\nCHANGES WERE MADE DIRECTLY IN THE INPUT FILE(S).')
    else:
        if silent == False:
            # mb.showwarning(title='String edit', message=str(Ndocs) + ' document(s) processed.\n\nNo documents were found with the input string ' +str( string_IN))
            mb.showwarning(title='String edit', message=str(Ndocs) + ' document(s) processed.\n\nNo documents were found with the input string(s).')
        else:
            print(str(Ndocs) + ' document(s) processed but zero input string(s) found.')

    if not IO_error:
        filesToOpen.append(outputFilename)
    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

