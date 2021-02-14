
# Created on Tue Oct 25 2020
# author: Brett Landau

import os
import IO_files_util
import GUI_util

def extract_fileContent_and_fileName(outputPath, fileContent, separator_begin, separator_end):
    nFiles = 0
    lines = fileContent.splitlines()
    begin_len = len(separator_begin)
    file_to_save = ""
    for l in lines:
        if l[0:begin_len] == separator_begin:
            nFiles+=1
            file_to_save = os.path.split(l.split(separator_begin)[1].split(separator_end)[0])[1]
            print("Processing file "+str(nFiles)+"/"+str(count)+ " for output:",file_to_save)
        else:
            if file_to_save != "" and l!="":
                subfilePath = os.path.join(outputPath, file_to_save)
                subfile = open(subfilePath, "a", encoding='utf-8', errors='ignore')
                subfile.write(l+"\n")
                subfile.close()
    return nFiles

def run(inputfile, separator_begin, separator_end, outputDir):
    global count
    head, tail = os.path.split(inputfile)
    tail=tail[:-4]
    # create a subdirectory in the output directory
    outputPath = outputDir + os.sep + tail + "_split"
    if not IO_files_util.make_directory(outputPath):
        return
    file = open(inputfile, "r", encoding="utf-8", errors='ignore')
    fileContent = file.read()
    count = fileContent.count(separator_begin)
    if separator_begin==separator_end:
        count=count/2
    file.close()
    nFiles = extract_fileContent_and_fileName(outputPath, fileContent, separator_begin, separator_end)
    return outputPath, nFiles
