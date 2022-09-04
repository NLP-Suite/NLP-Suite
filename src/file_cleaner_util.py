
#!/usr/bin/python
# Python version target: 3.6.3 Anaconda

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Newspaper titles",['os','re','stanza','glob','pandas','string','tkinter'])==False:
    sys.exit(0)

import glob
import os
from Stanza_functions_util import stanzaPipeLine, sent_tokenize_stanza
import string
import tkinter as tk
import tkinter.messagebox as mb
import re

import IO_files_util
import GUI_IO_util
import IO_user_interface_util
import IO_csv_util
import file_filename_util


# the function checks for end of paragraph punctuation
#   where a paragraph is any chunk of text followed by a carriage return/hard return
#   the function checks for double quotation and single quotation first, then check for .!?
#   if .?| or ." ?" |" or .' ?' |' then a full stop . is added
#   The reason is that if many successive paragraphs have no end-of-paragraph punctuation, Stanford CoreNLP will string all of them together
#       potentially creating unduly long sentences that may lead to efficiency issues
#       https://stanfordnlp.github.io/CoreNLP/memory-time.html

# extra parameters passed to uniform the funct call
def add_full_stop_to_paragraph(window, inputFilename, inputDir, outputDir, openOutputFiles,createCharts=False,chartPackage='Excel'):
    result=file_filename_util.backup_files(inputFilename, inputDir)
    if result==False:
        return

    # collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    docID = 0
    if nDocs == 0:
        return

    # DOCUMENTS WITH FULL STOPS ADDED
    count = 0
    docID = 0

    for filename in inputDocs:
        docID = docID + 1
        _, tail = os.path.split(filename)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        edited = False
        with open(filename, 'r', encoding='utf-8', errors='ignore') as each:
            paragraphs = []
            paragraphs = each.read().split('\r') # carriage return/hard return
            lst = []
            for paragraph in paragraphs:
                for s in paragraph.split('\n'):
                    lst.append(s)
            paragraphs = lst
            paragraphs = [each.strip() for each in paragraphs if each.strip()]
            with open(filename, 'w', encoding='utf-8', errors='ignore') as out:
                for paragraph in paragraphs:
                    check_index = -1
                    if paragraph and paragraph[-1] in ['\'', '"']:
                        if (len(paragraph) >= 2):
                            check_index = -2
                    # check for enf of paragraph punctuation, quotation and single quotation first, then check for .!?
                    if paragraph and paragraph[check_index] not in ['.', '!', '?']:
                        out.write(paragraph + '.\n')
                        edited = True
                    else:
                        out.write(paragraph)
                        out.write('\n')
        if (edited):
            count += 1

    msgString = ''
    if count==0:
        if nDocs==1:
            msgString="The document has no added full stops."
        else:
            msgString="No documents have been edited for added full stops."
    else:
        msgString = "%s documents out of %d have been edited for full stops." % (nDocs,count) + "\n\nThe percentage of documents processed is %.2f" % ((float(count)/nDocs) * 100)
    if count>0:
        if inputFilename!="":
            msgString=msgString+"\n\nAll edits were saved directly in the input file."
        else:
            msgString=msgString+"\n\nAll edits were saved directly in all affected input files."

    mb.showwarning(title='End of paragraph punctuation', message=msgString)

def check_typesetting_hyphenation(window,inputFilename,inputDir, outputDir='',openOutputFiles=False,createCharts=False,chartPackage='Excel'):
    filesToOpen=[]
    docID = 0
    files=IO_files_util.getFileList(inputFilename, inputDir, fileType='txt')
    nDocs = len(files)
    if nDocs==0:
        return
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        hyphenated_lines=0
        lines=[]
    with open(infile, encoding='utf-8', errors='ignore') as source:
        for line in source.readlines():
            line = line.rstrip("\n")
            if line.endswith("-"):
                if len(line)>=2:
                    if line[-2]==' ':
                        continue
                hyphenated_lines += 1
                lin, _, e = line.rpartition(" ")
                lines.append(line)

    if hyphenated_lines > 0:
        mb.showwarning('Warning', 'There are ' + str(
            hyphenated_lines) + ' typesetting hyphenated lines in the input file(s).\n\nPlease, check carefully the output csv file to make sure that there are no legitimate end-of-line hyphens (e.g., pretty-smart) that should not be joined together. In such legitimate cases, please, manually move the line end to the next line.')
        outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'lines with end hyphen')
        lines.insert(0,'Line ending with -')
        IO_error = IO_csv_util.list_to_csv(window, lines, outputFilename)
        if not IO_error:
            filesToOpen.append(outputFilename)
        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
    else:
        mb.showwarning('Warning', 'There are ' + str(hyphenated_lines) + ' typesetting hyphenated lines in the input file(s).')

def remove_typeseting_hyphenation(window,inputFilename,inputDir, outputDir='',openOutputFiles=False,createCharts=False,chartPackage='Excel'):

    # if not IO_user_interface_util.input_output_save('Remove end-of-line typesetting hyphenation and join split parts'):
    #     return

    message='The input file(s) may contain legitimate end-of-line hyphens (e.g., pretty-smart with pretty- at the end of a line and smart at the beginning of the next line). In such legitimate cases, the two-parts of the hyphenated compound should not be joined together (rather, the line end, pretty- should be manually moved to the next line.\n\nDo you want to check, first, that there are no legitimate uses of end-of-line hyphens, before removing them all automatically, whether legitimate or not?'
    answer = tk.messagebox.askyesno("Warning", message)
    if answer:
        check_typesetting_hyphenation(window, inputFilename, inputDir, outputDir, openOutputFiles,
                                      createCharts=False, chartPackage='Excel')
        return

    docID = 0
    files=IO_files_util.getFileList(inputFilename, inputDir, fileType='txt')
    nDocs = len(files)
    if nDocs==0:
        return
    for infile in files:
        docID = docID + 1
        head, tail = os.path.split(infile)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        removed_hyphens=0
        outfile = infile.replace('.txt','_1.txt')
        with open(infile, encoding='utf-8', errors='ignore') as source, open(outfile, "w", encoding='utf-8', errors='ignore') as dest:
            holdover = ""
            for line in source.readlines():
                line = line.rstrip("\n")
                if line.endswith("-"):
                    if len(line) >= 2:
                        if line[-2] == ' ': # do not convert - preceded by a space
                            continue
                    removed_hyphens +=1
                    lin, _, e = line.rpartition(" ")
                else:
                    lin, e = line, ""
                dest.write(f"{holdover}{lin}\n")
                holdover = e[:-1]
    if removed_hyphens > 0:
        save_msg = '\n\nOutput file(s) saved in the same directory of input file(s) with _1.txt ending.'
    else:
        save_msg = ''
    mb.showwarning('Warning',str(removed_hyphens) + ' end-line typesetting hyphens removed from the input file(s).'+ save_msg)

def remove_characters_between_characters(window,inputFilename,inputDir, outputDir='',openOutputFiles=False, startCharacter='', endCharacter=''):

    if not IO_user_interface_util.input_output_save('Remove all characters between characters'):
        return

    if startCharacter=='':
        startCharacter, useless = GUI_IO_util.enter_value_widget("Enter the single start character (e.g., [)", '',
                                                               1, '', '', '')
        if startCharacter == '':
            mb.showwarning(title='Blank start character',
                           message='No start character entered. Routine aborted.')
            return
        endCharacter, useless = GUI_IO_util.enter_value_widget("Enter the single end character (e.g., ])", '',
                                                               1, '', '', '')
        if endCharacter == '':
            mb.showwarning(title='Blank end character',
                           message='No end character entered. Routine aborted.')
            return

    docID = 0
    files=IO_files_util.getFileList(inputFilename, inputDir, fileType='txt')
    nDocs = len(files)
    if nDocs==0:
        return
    for file in files:
        docID = docID + 1
        head, tail = os.path.split(file)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        with open(file,encoding='utf_8',errors='ignore') as infile:
            fullText = infile.read()
            number_of_characters_start = fullText.count(startCharacter)
            if number_of_characters_start == 0:
                mb.showwarning(title='Start character not found',
                               message='No Start character ' + startCharacter + ' was found in the input file ' + tail + '.\n\nRoutine aborted.')
                return
            number_of_characters_end = fullText.count(endCharacter)
            if number_of_characters_end == 0:
                mb.showwarning(title='End character not found',
                               message='No End character ' + endCharacter + ' was found in the input file ' + tail + '.\n\nRoutine aborted.')
                return
            if number_of_characters_start != number_of_characters_end:
                mb.showwarning(title='Unmatched start and end characters',
                               message='The number of start and end characters are not matched (start =' + str(number_of_characters_start) + '; end = ' + str(number_of_characters_end) + ') in the input file ' + tail)
                continue
            i = 0
            while i < number_of_characters_start:
                split_string_A = fullText.split(startCharacter, 1) # Split into "ab" and "cd"
                split_string_A = split_string_A[0]
                # print("split_string_A",split_string_A)
                split_string_B = fullText.split(endCharacter, 1) # Split into "ab" and "cd"
                split_string_B = split_string_B[1]
                # print("split_string_B",split_string_B)
                fullText = split_string_A + split_string_B
                # print("cleaned_text",fullText)
                i +=1
        with open(file, 'w+',encoding='utf_8',errors='ignore') as outfile:
            outfile.write(fullText)
            mb.showwarning(title='Edits saved', message=str(i) + ' substrings contained between ' + startCharacter + ' ' + endCharacter + ' were removed and saved directly in the input file ' + tail)

# inputFilename contains path
def remove_blank_lines(window,inputFilename,inputDir, outputDir='',openOutputFiles=False,createCharts=False,chartPackage='Excel'):
    result=file_filename_util.backup_files(inputFilename, inputDir)
    if result==False:
        return

    files=IO_files_util.getFileList(inputFilename, inputDir, fileType='txt')
    nDocs = len(files)
    if nDocs==0:
        return
    docID = 0
    filesWithEmptyLines=0
    for file in files:
        docID = docID + 1
        head, tail = os.path.split(file)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        withEmptyLines = False
        outputLines = ""
        with open(file,encoding='utf_8',errors='ignore') as infile:
            for line in infile.read().split("\n"): # check if any line is empty line
                if line.strip() == '':
                    withEmptyLines = True
                else:
                    outputLines += line + "\n"
        with open(file, 'w+',encoding='utf_8',errors='ignore') as outfile:
            outfile.write(outputLines[:-1])  # non-empty line. Write it to output
        if withEmptyLines: # if there is any empty line, increment count
            filesWithEmptyLines += 1
    if inputFilename!="":
        if filesWithEmptyLines==0:
            mb.showwarning(title='Blank lines removed',
                           message='No blank lines were removed from the input file.')
        else:
            mb.showwarning(title='Blank lines removed',
                           message='Blank lines were removed from the input file.')
    else:
        if filesWithEmptyLines==0:
            mb.showwarning(title='Blank lines removed',
                           message='No files contained blank lines' + ' out of ' + str(
                               nDocs) + ' files in the input directory.')
        else:
            mb.showwarning(title='Blank lines removed',
                       message='Blank lines were removed from ' +str(filesWithEmptyLines) +' out of '+str(nDocs) +' files in the input directory.')

# criteria for title are no punctuation and
#	a shorter (user determined) sentence in number of words

#Title_length_limit = int(sys.argv[1])
#TITLENESS = sys.argv[2]
#inputDir = sys.argv[3]
#outputDir = sys.argv[4]


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

def newspaper_titles(window,inputFilename,inputDir,outputDir,openOutputFiles,createCharts,chartPackage):

    if inputDir=='' and inputFilename!='':
        NUM_DOCUMENT=1
    else:
        NUM_DOCUMENT = len(glob.glob(os.path.join(inputDir, '*.txt')))
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

    if inputFilename != "":
        temp_inputDir, tail = os.path.split(inputFilename)
    else:
        temp_inputDir = inputDir

    path_aritclesWithTitles = os.path.join(temp_inputDir, 'documents_with_titles')

    if not os.path.exists(path_aritclesWithTitles):
        os.makedirs(path_aritclesWithTitles)

    #collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    docID = 0
    if nDocs==0:
        return
    print("\n\nProcessing documents with titles...\n\n")
    for filename in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(filename)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        with open(filename,'r', encoding='utf-8', errors='ignore') as each:
            paragraphs = []
            paragraphs = each.read().split('\r') # carriage return/hard return
            lst = []
            for paragraph in paragraphs:
                for s in paragraph.split('\n'):
                    lst.append(s)
            paragraphs = lst
            paragraphs = [each.strip() for each in paragraphs if each.strip()]
            file_path = os.path.join(path_aritclesWithTitles,tail)
            with open(file_path, 'w', encoding='utf-8',errors='ignore') as out:
                for paragraph in paragraphs:
                    if isTitle(paragraph,Title_length_limit):
                        if paragraph and paragraph[-1]!='.':
                            out.write(paragraph + '.\n')
                        else:
                            out.write(paragraph)
                    else:
                        # for one in sent_tokenize(paragraph):#.decode('utf-8')):
                        for one in sent_tokenize_stanza(stanzaPipeLine(paragraph)):
                            out.write(one)#.encode('utf-8'))
                            out.write(' ')
                        out.write('\n')
                # titles.append((title,filename))
        count += 1

    # DOCUMENTS WITHOUT TITLES
    count = 0
    titles = []
    docID = 0

    path_documents = os.path.join(temp_inputDir,'documents_no_titles')
    print("\n\nProcessing documents without titles...\n\n")
    if not os.path.exists(path_documents):
        os.makedirs(path_documents)
    for filename in inputDocs:
        docID = docID + 1
        head, tail = os.path.split(filename)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        with open(filename,'r', encoding='utf-8', errors='ignore') as each:
            paragraphs = []
            paragraphs = each.read().split('\r') # carriage return/hard return
            lst = []
            for paragraph in paragraphs:
                for s in paragraph.split('\n'):
                    lst.append(s)
            paragraphs = lst
            paragraphs = [each.strip() for each in paragraphs if each.strip()]
            file_path = os.path.join(path_documents,tail)
            with open(file_path, 'w', encoding='utf-8',errors='ignore') as out:
                title = []
                for paragraph in paragraphs:
                    if isTitle(paragraph,Title_length_limit):
                        title.append(paragraph)
                    else:
                        # for one in sent_tokenize(paragraph):#.decode('utf-8')):
                        for one in sent_tokenize_stanza(stanzaPipeLine(paragraph)):
                            out.write(one)
                            out.write(' ')
                        out.write('\n')
                titles.append((title,filename))
        count += 1
        # print(count)

    # TITLES ONLY
    print("\n\nProcessing documents with titles...\n\n")
    path_title = os.path.join(temp_inputDir,'document_titles_only')
    if not os.path.exists(path_title):
        os.makedirs(path_title)
    titles_file = os.path.join(path_title,'titles.txt')
    with open(titles_file,'w',encoding='utf_8',errors='ignore') as output:
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
                    t = t + '. \n'
                output.write(t)
                output.write('\n')

    msgString = ''
    if count==0:
        if NUM_DOCUMENT==1:
            msgString="The document has not generated separate titles."
        else:
            msgString="No documents have generated separate titles."
    else:
        msgString = "%s documents out of %d have generated titles." % (NUM_DOCUMENT,count) + "\n\nThe percentage of documents processed is %.2f" % ((float(count)/nDocs) * 100)
    # msgString=" %s documents out of %d have generated titles." % (NUM_DOCUMENT, count)
    if count>0:
        if inputFilename!="":
            msgString=msgString+"\n\nThe files were saved in the subdirectory\n\n" + str(path_documents) + "\n\nof the input file directory\n\n"+inputDir
        else:
            msgString=msgString+"\n\nThe files were saved in the subdirectory\n\n" + str(path_documents) + "\n\nof the input directory\n\n"+inputDir

    mb.showwarning(title='Document titles', message=msgString)

# non-ASCII apostrophes and quotes (e.g., those coming from Windows Words) will show up in a csv file (not in Excel or Mac) as weird characters
#	although they do not break any script coode
# % will break the CoreNLP code
# The reasons are explained here: https://docs.oracle.com/javase/8/docs/api/java/net/URLDecoder.html
#   The character "%" is allowed but is interpreted as the start of a special escaped sequence.
# Needs special handling https://stackoverflow.com/questions/6067673/urldecoder-illegal-hex-characters-in-escape-pattern-for-input-string
# https://stackoverflow.com/questions/7395789/replacing-a-weird-single-quote-with-blank-string-in-python
def convert_quotes(window,inputFilename, inputDir,temp1='',temp2=''):
    result=file_filename_util.backup_files(inputFilename, inputDir)
    if result==False:
        return False

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    Ndocs=len(inputDocs)
    index=0
    if Ndocs==0:
        return
    result= IO_user_interface_util.input_output_save("Convert apostrophes/quotes/%")
    if result ==False:
        return False

    docError = 0
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                       'Started running characters conversion at',
                                                 True, '', True, '', True)
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
    return True

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

def find_replace_string(window,inputFilename, inputDir, outputDir, openOutputFiles=True,string_IN=[],string_OUT=[],silent=False):
    #edited by Claude Hu 02/2021
    #string_IN=[],string_OUT=[], in the form as list so that running this function can finish replacement of multiple strings without open one file repetitively
    result=file_filename_util.backup_files(inputFilename, inputDir)
    if result==False:
        return

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
                    changed_values.append([[string_IN[i],string_OUT[i],index, IO_csv_util.dressFilenameForCSVHyperlink(doc)]])
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
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

