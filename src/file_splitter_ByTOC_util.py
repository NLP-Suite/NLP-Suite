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

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"File_splitter_ByTOC",['os','io','re','ntpath','tkinter','shutil'])==False:
    sys.exit(0)

import io
import os
import re
import tkinter.messagebox as mb
import ntpath
import shutil

import IO_csv_util
import IO_files_util

def splitDocument_byTOC(window,inputDocumentTobeSplit,inputTOCfile,outputDir,openOutputFiles):

    # print("nputDocumentTobeSplit",inputDocumentTobeSplit)
    #

    inputDocNoExtension=inputDocumentTobeSplit[:-4]
    inputDocNoPathNoExtension=ntpath.basename(inputDocNoExtension)
    outputHeadingsNotfound=inputDocNoPathNoExtension+"_HeadingsNotFound.csv"

    # check that TOC file exists
    if not IO_files_util.checkFile(inputTOCfile):
        outputHeadingsNotfound=''
        return

    # Get current directory and create "chapters folder"
    # newoutputDir = inputDir + os.sep + "split_files_" + split_docLength + "_" + title

    head, tail = os.path.split(inputDocumentTobeSplit) # head contains the path part of the filename
    # tail contains the filename only

    newoutputDir = os.path.join(head, inputDocNoPathNoExtension+'_sections')
    if not os.path.exists(newoutputDir):
        os.mkdir(newoutputDir)
    outputHeadingsNotfound=os.path.join(newoutputDir,outputHeadingsNotfound)

    filesToOpen=[]
    headings = []
    count = 0
    j = 0
    headingsNotFoundInBook=[]

    # Read TOC file and fill headings list
    with io.open(inputTOCfile, "r", encoding="utf-8", errors='ignore') as file:
        # loop through each line of the TOC file, expecting one TOC entry per line
        for heading in file:
            # Remove spaces at the beginning and at the end of the string
            headings.append(heading.strip())

    # Read text file
    fileContent = io.open(inputDocumentTobeSplit, "r", encoding="utf-8", errors='ignore').read()

    # Extract text content for each heading
    for i in range(len(headings)):
        print('Processing heading ' + str(i) + ': '+headings[i])
        count += 1
        sectionContent = extractSection(fileContent, headings[i], headings[i + 1]) if i < len(headings) - 1 \
            else extractSection(fileContent, headings[i], None)
        if sectionContent:
            #split file saved in the document_section folder with filename = document name + section name
            sectionFileName=os.path.join(newoutputDir, inputDocNoPathNoExtension + "_" + headings[i] + '.txt')
            newFile = io.open(sectionFileName, "w+", encoding='utf-8', errors='ignore')
            newFile.write(sectionContent.strip())
        else:
            print('   Heading not found in main document')
            headingsNotFoundInBook.append([headings[i]])
            j = j + 1
    errorFound=IO_csv_util.list_to_csv(window,headingsNotFoundInBook,outputHeadingsNotfound)
    if errorFound==True:
        outputHeadingsNotfound=''
    if j>0:
        mb.showwarning(title='Output split files', message=str(count) + " headings from the TOC file were processed and exported to the directory " + newoutputDir + ".\n\n" + str(j) + " headings were not found in the main document \'" + inputDocumentTobeSplit + "\'\n\nPlease, check the list of headings in the TOC file against the document content.")
        filesToOpen.append(outputHeadingsNotfound)
        # open the csv file containing the list of TOC headings not found in the text
        if openOutputFiles==True:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
    else:
        mb.showwarning(title='Error found', message=str(count) + " headings from the TOC file were all successfully processed and all sections exported to the directory " + newoutputDir)
        outputHeadingsNotfound=''
    return outputHeadingsNotfound

def extractSection(fileContent, documentHeading, nextheading):
    """
    :param doc: the main input text file
    :param documentHeading: the heading of the document section that is to be extracted
    :param nextheading: the heading of the next section
    :return the content of the section as string
            return nothing if section heading does not exist in doc
    """
    global pattern
    if documentHeading is not None and nextheading is not None:
        # pattern = re.compile(r'(?<=' + re.escape(documentHeading) + r')' + r'.+(?=' + re.escape(nextheading) + r')',
        #     flags = re.DOTALL | re.IGNORECASE)
        # \s\w+ will match a space and the immediate word \n hard return
        # DOTALL is a flag related to multiline text. Normally the dot character . matches everything in the input text except a newline character. The flag allows dot to match newlines as well.
        pattern = re.compile(r'(' + re.escape(documentHeading) + r'[\s*\W*]*' +r'\n'+ r'.+)' + r'(?=' + re.escape(nextheading) + r'[\s*\W*]*'+r'\n)',
                    flags = re.DOTALL | re.IGNORECASE)
    elif documentHeading is not None:
        # pattern = re.compile(re.escape(documentHeading) + r'.+', flags = re.DOTALL | re.IGNORECASE)
        pattern = re.compile(re.escape(documentHeading) + r'[\s*\W*]*' +r'\n'+ r'.+', flags = re.DOTALL | re.IGNORECASE)
    # findall() module is used to search for “all” occurrences that match a given pattern.
    # In contrast, search() module will only return the first occurrence that matches the specified pattern.
    # findall() will iterate over all the lines of the file and will return all non-overlapping matches of pattern in a single step.
    match = re.findall(pattern, fileContent)
    if match:
        return match[0]
