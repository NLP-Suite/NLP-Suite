
# Created on Tue Oct 25 2020
# author: Brett Landau

import tkinter.messagebox as mb

import os
import IO_files_util
import GUI_util

def extract_fileContent_and_fileName(outputPath, fileContent, separator_begin, separator_end):
    ID=0
    lines = fileContent.splitlines()
    begin_len = len(separator_begin)
    file_to_save = ""
    for l in lines:
        if l[0:begin_len] == separator_begin:
            ID+=1
            file_to_save = os.path.split(l.split(separator_begin)[1].split(separator_end)[0])[1]
            print("Processing file "+str(ID)+"/"+str(len(lines))+ " for output:",file_to_save)
        else:
            if file_to_save != "" and l!="":
                subfilePath = os.path.join(outputPath, file_to_save)
                subfile = open(subfilePath, "a", encoding='utf-8', errors='ignore')
                subfile.write(l+"\n")
                subfile.close()
    return ID

def run(inputfile, separator_begin, separator_end, outputDir):
    global count
    nFiles=0
    head, tail = os.path.split(inputfile)
    tail=tail[:-4]
    # create a subdirectory in the output directory
    outputPath = outputDir + os.sep + tail + "_split"
    if not IO_files_util.make_directory(outputPath):
        return
    file = open(inputfile, "r", encoding="utf-8", errors='ignore')
    fileContent = file.read()
    count_begin = fileContent.count(separator_begin)
    if separator_begin==separator_end:
        count_begin=count_begin/2
    count_end = fileContent.count(separator_end)
    if separator_begin==separator_end:
        count_end = count_end / 2
    file.close()
    if count_begin>0 and count_end>0:
        nFiles = extract_fileContent_and_fileName(outputPath, fileContent, separator_begin, separator_end)
    else:
        mb.showwarning(title='Merged file',
                       message='The input merged file does not contain matching beginning and ending file separators:\n\n   '+separator_begin+ '\n   '+ separator_end+'\n\nPlease, check your merged file and try again.')
    return outputPath, nFiles
