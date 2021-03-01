"""
Author: Matthew Chau November 2019
Edited: Roberto Franzosi, Claude Hu August 2020
The script takes an input txt file that contains section headings (e.g., chapter titles)
    and splits it into sub-documents, 
    one document for each of the headings listed in a TOC file (Table of Content)
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"File_splitter_ByTOC",['os','io','re','ntpath','tkinter','shutil'])==False:
    sys.exit(0)

import io
import os
import re
import tkinter.messagebox as mb
import ntpath
import shutil

import IO_csv_util
import IO_files_util

def splitDocument_byTOC(window,inputDocumentTobeSplit,inputTOCfile,outputPath,openOutputFiles):

    print("nputDocumentTobeSplit",inputDocumentTobeSplit)

    outputHeadingsNotfound=''
    
    inputDocNoExtension=inputDocumentTobeSplit[:-4]
    inputDocNoPathNoExtension=ntpath.basename(inputDocNoExtension)
    if outputHeadingsNotfound=='':
        outputHeadingsNotfound=inputDocNoPathNoExtension+"_HeadingsNotFound.csv"

    if not IO_files_util.checkFile(inputTOCfile):
        outputHeadingsNotfound=''
        return

    # Get current directory and create "chapters folder"
    # newOutputPath = inputDir + os.sep + "split_files_" + split_docLength + "_" + title

    head, tail = os.path.split(inputDocumentTobeSplit) # head contains the path part of the filename
    # tail contains the filename only

    newOutputPath = os.path.join(head, inputDocNoPathNoExtension+'_sections')
    if not os.path.exists(newOutputPath):
        os.mkdir(newOutputPath)
    outputHeadingsNotfound=os.path.join(newOutputPath,outputHeadingsNotfound)

    filesToOpen=[]
    headings = []
    count = 0
    j = 0
    headingsNotFoundInBook=[]
    # Fill headings list
    # utf-8-sig
    with io.open(inputTOCfile, "r", encoding="utf-8", errors='ignore') as file:
        for heading in file:
            headings.append(heading.strip())
    # Extract text content for each heading
    for i in range(len(headings)):
        count += 1
        sectionContent = extractSection(inputDocumentTobeSplit, headings[i], headings[i + 1]) if i < len(headings) - 1 \
            else extractSection(inputDocumentTobeSplit, headings[i], None)
        if sectionContent:
            #split file saved in the document_section folder with filename = document name + section name
            sectionFileName=os.path.join(newOutputPath, inputDocNoPathNoExtension + "_" + headings[i] + '.txt')
            newFile = io.open(sectionFileName, "w+", encoding='utf-8', errors='ignore')
            newFile.write(sectionContent.strip())
        else:
            headingsNotFoundInBook.append([headings[i]])
            j = j + 1
    errorFound=IO_csv_util.list_to_csv(window,headingsNotFoundInBook,outputHeadingsNotfound)
    if errorFound==True:
        outputHeadingsNotfound=''
    if j>0:
        mb.showwarning(title='Output split files', message=str(count) + " headings from the TOC file were processed and exported to the directory " + newOutputPath + ".\n\n" + str(j) + " headings were not found in the main document \'" + inputDocumentTobeSplit + "\'\n\nPlease, check the list of headings in the TOC file against the document content.")
    else:
        mb.showwarning(title='Error found', message=str(count) + " headings from the TOC file were all successfully processed and all sections exported to the directory " + newOutputPath)
        outputHeadingsNotfound=''
    if outputHeadingsNotfound!=None:
        filesToOpen.append(outputHeadingsNotfound)
        if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
    return outputHeadingsNotfound

def extractSection(doc, documentHeading, nextheading):
    """
    :param doc: the main input text file
    :param documentHeading: the heading of the document section that is to be extracted
    :param nextheading: the heading of the next section
    :return the content of the section as string
            return nothing if section heading does not exist in doc
    """
    global pattern
    file = io.open(doc, "r", encoding="utf-8", errors='ignore')
    fileContent = file.read()
    if documentHeading is not None and nextheading is not None:
        # pattern = re.compile(r'(?<=' + re.escape(documentHeading) + r')' + r'.+(?=' + re.escape(nextheading) + r')',
        #     flags = re.DOTALL | re.IGNORECASE)
        pattern = re.compile(r'(' + re.escape(documentHeading)+  r'[\s*\W*]*' +r'\n'+ r'.+)' + r'(?=' + re.escape(nextheading) + r'[\s*\W*]*'+r'\n)',
                    flags = re.DOTALL | re.IGNORECASE)
    elif documentHeading is not None:
        # pattern = re.compile(re.escape(documentHeading) + r'.+', flags = re.DOTALL | re.IGNORECASE)
        pattern = re.compile(re.escape(documentHeading) + r'[\s*\W*]*' +r'\n'+ r'.+', flags = re.DOTALL | re.IGNORECASE)
    match = re.findall(pattern, fileContent)
    if match:
        return match[0]
