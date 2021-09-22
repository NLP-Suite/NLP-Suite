"""
Author: Jack Hester, Spring 2019
Edited: Cynthia Dong, Roberto Franzosi, Spring 2020

"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"File splitter by TOC",['os','io','re','ntpath','tkinter','shutil'])==False:
    sys.exit(0)

import io
import os
import re
import tkinter.messagebox as mb
import ntpath
import shutil

import GUI_util
from nltk.tokenize import sent_tokenize, word_tokenize

import IO_user_interface_util
import reminders_util

#Jack Hester
#the function is used to split a document longer than 100K characters since Stanford CoreNLP can only deal with text files of 100K characters max.
def splitAt(text,index):
    #consider ." !" ?" for speech 
    #   otherwise you end up with an unaccounted " in the next chunk of text
    limit = sys.getrecursionlimit()
    first_limit = limit
    while True:
        try:
            if text[index] in ['.', '!', '?']:
                return index
            else:
                return splitAt(text,index-1)
        except RecursionError:
            mb.showwarning("Warning", "The file being split is a VERY large (" + str(len(text)) + " characters) file.\n\nTo deal with such large a file, the system recursion limit will be temporarily doubled, then restored to its original limit.\n\nClick OK to continue processing...")
            limit = limit * 2
            sys.setrecursionlimit(limit)
    sys.setrecursionlimit(first_limit)

#Jack Hester
#edited by Cynthia Dong and Roberto Franzosi
#the function is used to check the lenght of a document 
#   and split the document
#   since Stanford CoreNLP can only deal with text files of 100K characters max.
#   90000 in number of characters
# input_path is a path where files are store
# files is a list  ['C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs/The Three Little Pigs.txt']
# filesToReturn is also a list ['C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs\\split_files\\The Three Little Pigs_1.txt', 'C:/Users/rfranzo/Desktop/CORPUS DATA/Three little pigs\\split_files\\The Three Little Pigs_2.txt']

# filename contains file WITH path
# called by Stanford_CoreNL_parser
# called by annotators DBpedia, YAGO utils
#   In DBpedia and YAGO the temporary split files are deleted
#def splitDocument_byLength(window,filename,output_path, maxLength=90000, inWords=False):
def splitDocument_byLength(window, software, filename_path,output_path='', maxLength=90000, inWords=False):
    # a new folder is created in output
    #   as a subfolder of the input folder and/or file
    #   the subfolder will be named split_files_9000_filename (no extension)
    filesToReturn=[]
    
    head, filename = os.path.split(filename_path)
    # Stanford_CoreNLP_parser_util does not pass the output dir
    if output_path=='':
        output_path=head
    new_splitFiles_folder = output_path+os.sep+"split_files_"+str(maxLength)+"_"+filename[:-4]
    with open(filename_path, 'r',encoding='utf-8',errors='ignore') as F:
        text = F.read()
        length = len(text)
        if inWords:
            length = len(text.split())
            # print("length",length)
    F.close()
    if length > maxLength:
        # IO_user_interface_util.timed_alert(window, 3000, 'File split warning', 'The file ' + filename_path + ' was too long for ' + software + ' to process, and was split into sub-files and stored in the split_files sub-folder:\n\n' + new_splitFiles_folder)
        if os.path.exists(new_splitFiles_folder):
            shutil.rmtree(new_splitFiles_folder)
        try:
            os.mkdir(new_splitFiles_folder)
        except Exception as e:
            print ("error: ", e.__doc__)
        splits = [-1]#start at -1 not 0 because of +1 later in loop
        if inWords:
            i = maxLength-5
        else:
            i = maxLength-2
        while(i<length):
            i = splitAt(text,i)
            splits.append(i)
            if inWords:
                i = i + maxLength-5
            else:
                i = i + maxLength-2
        splits.append(length-1)
        for i in range(1, len(splits)):
            # write output file
            fname=os.path.basename(os.path.normpath(filename_path))

            # SplitFile=os.path.join(output_path,fname).split('.txt')[0]+'_'+str(i)+'.txt'
            SplitFile=os.path.join(new_splitFiles_folder,fname).split('.txt')[0]+'_'+str(i)+'.txt'
            with open(SplitFile, 'w+',newline = "", encoding='utf-8',errors='ignore') as sf:
                sf.write(text[splits[i-1]+1:splits[i]+1])
                filesToReturn.append(SplitFile)
            sf.close()
        title=['Split files']
        message=str(i) + ' split files were created in the split_files sub-folder:\n\n' + output_path + "\n\nIf you are processing files in a directory, other files may similarly need to be split and the message display may become annoying."
        reminders_util.checkReminder(software, title,
                                      message, True)
        # IO_user_interface_util.timed_alert(window, 3000, 'File split warning', str(i) + ' Split files were created in the split_files sub-folder:\n\n' + output_path)
    else:
        filesToReturn.append(filename_path)
    # print("filesToReturn",filesToReturn)
    return filesToReturn

# called from file_splitter_main
# a new folder is created in output
#   as a subfolder of the input folder and/or file
#   the subfolder will be named split_files_9000_filename (no extension)
# contrary to the function splitDocument_byLength that carries out
#   making the split_files subdirectory, for this function
#   the creation of the directory is carried out in the calling script
def split_byLength(window,input_path,filename,output_path, maxLength, inSentence=False):
    #inSentence: no incomplete sentence in subfiles
    docname = os.path.split(filename)[1]
    title = docname.partition('.')[0]#get the title of the file(without path and .txt)
    with open(filename, 'r',encoding='utf-8',errors='ignore') as F:
        text = F.read()
        sentences = sent_tokenize(text)#sentnece list of the input txt
    F.close()
    if maxLength > len(word_tokenize(text)):
        IO_user_interface_util.timed_alert(window, 3000, 'File split warning', 'The length of file ' + filename + ' is less than ' + str(maxLength))
        subfile = open(output_path+"/"+title+"_1"+".txt", 'w',encoding='utf-8',errors='ignore')
        subfile.write(text)
        return
    splitText = ''
    subfileIndex = 1
    l = 0
    for sent in sentences:
        words = word_tokenize(sent)
        if l + len(words) < maxLength:
            splitText += sent + " "
            l += len(words)
        elif l + len(words) == maxLength:
            splitText += sent 
            subfile = open(output_path+"/"+title+"_"+str(subfileIndex)+".txt", 'w',encoding='utf-8',errors='ignore')
            subfile.write(splitText)
            subfileIndex +=1
            splitText = ''
            l = 0
        else:
            if inSentence:#the subfile's word count is less than max limit, but contain no incomplete sentences
                subfile = open(output_path+"/"+title+"_"+str(subfileIndex)+".txt", 'w',encoding='utf-8',errors='ignore')
                subfile.write(splitText)
                subfileIndex +=1
                splitText = sent + " "
                l = len(words)
            else:
                diff = maxLength - l#the index of the last word of this subfile in the sentence
                if words.index(words[diff-1]) == diff - 1: #no other same word in the setence or that's the first occurrence of the word
                    splitText += sent.partition(words[diff-1])[0]+sent.partition(words[diff-1])[1]
                    subfile = open(output_path+"/"+title+"_"+str(subfileIndex)+".txt", 'w',encoding='utf-8',errors='ignore')
                    subfile.write(splitText)
                    subfileIndex +=1
                    splitText = sent.partition(words[diff-1])[2]   + " "     
                    l = len(words) - diff
                else:
                    subsent = ''
                    restsent = sent
                    while len(word_tokenize(subsent)) <= diff:#check each same word until the previous text reached the maxLength
                        subsent += restsent.partition(words[diff-1])[0]+restsent.partition(words[diff-1])[1]
                        restsent = restsent.partition(words[diff-1])[2]
                    subfile = open(output_path+"/"+title+"_"+str(subfileIndex)+".txt", 'w',encoding='utf-8',errors='ignore')
                    subfile.write(splitText + subsent)
                    subfileIndex += 1
                    splitText = restsent + " "
                    l = len(word_tokenize(restsent))
                    
    if len(splitText) > 0:
        subfile = open(output_path+"/"+title+"_"+str(subfileIndex)+".txt", 'w',encoding='utf-8',errors='ignore')
        subfile.write(splitText)
