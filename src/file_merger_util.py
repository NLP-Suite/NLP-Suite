# Written by Roberto Franzosi October 2019, revised October 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"file_merger_util",['os','tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk

import IO_files_util
import IO_user_interface_util

# In Windows, document merge can be done in command prompt:
# 1.  Go to the corpus directory: cd...
# 2.  Type:      copy *.txt combined.txt
# 3.  Click enter
# 4.  You should have a file in the corpus directory called combined.txt with all of the text from every text file.

#The script merges together in a single document several txt documents found in a directory (txt ---> txt)
#can insert filename or not
def file_merger(window,inputdirectory,outputdirectory,openOutputFiles, processSubdir=None,saveFilenameInOutput=None,merge_separator=False,startString='<@#',endString='@#>',embedSubdir=None,separator='__', writeRootDirectory=True):
    docNum=0
    if processSubdir==None:
        processSubdir = tk.messagebox.askyesnocancel("Process sub-directories", "Do you want to process for files in subdirectories?")
    if processSubdir==None: #cancel
        return        
    if processSubdir:
        tmpList = IO_files_util.getFileList_SubDir('',inputdirectory,'.txt')
    else:
        tmpList = IO_files_util.getFileList('',inputdirectory,'.txt')
    docList = [f for f in tmpList if f[:2] != '~$' and f[-4:] == '.txt']
    numberOfDocs = len(docList)

    if numberOfDocs == 0:
        tk.messagebox.showwarning(title='Warning',
                                  message="There are no txt files in your input directory.\n\nThe program will exit.")
        return

    if saveFilenameInOutput==None:
        saveFilenameInOutput = tk.messagebox.askyesnocancel("Save input filename in output", "Do you want to save the input filename in the output merged file at the beginning of each new input document?\n\nEach input filename will be saved enclosed in <@# #@>. for easy identification and search.\n\nCAVEAT! While having input filenames in the merged output file will make searches easy, if you are then using the merged file as input to the Stanford CoreNLP parser, these lines will also be parsed.")
    if saveFilenameInOutput is None: #cancel
        return
    # rootDir contains the last item of a directory path
    rootDir=os.path.basename(os.path.normpath(inputdirectory))
    outFilename=os.path.join(outputdirectory,'merged_Dir_'+rootDir +'.txt')
    fileError=0
    fileLengthError=0
    with open(outFilename, 'w',encoding="utf-8",errors='ignore') as outfile:
        # https://stackoverflow.com/questions/4813061/non-alphanumeric-list-order-from-os-listdir
        # https://stackoverflow.com/questions/38104264/order-of-filenames-from-os-listdir
        # https://docs.python.org/3/library/os.html#os.listdir
        # The list of os.listdir is in arbitrary order. The order has to do with the way the files are indexed on your FileSystem.
        # Must be sorted.
        # sorted will be lexically stable, but keep in mind that it's case sensitive. So A.jpg and a.jpg will be nowhere near each other, and C.jpg will show up before b.jpg. There's also issues like 1.jpg vs. 02.jpg.

        if writeRootDirectory:
            outfile.write('Root directory processed ' + inputdirectory + '.\n\n')
        # doc includes path
        for doc in docList:
            if IO_files_util.checkDirectory(os.path.join(inputdirectory, doc), message = False):
                continue
            docNum=docNum+1
            head, docName = os.path.split(doc)
            print ('Processing file ' + str(docNum) + " (out of " + str(numberOfDocs) + ") " + docName)
            if saveFilenameInOutput == True:
                if embedSubdir==True:
                    subDir = os.path.basename(os.path.normpath(head))
                    docName = doc[:-4]  # remove .txt from file name
                    # add the last part of the directory name to the filename
                    tempFilename=docName +str(separator)+str(subDir)+'.txt'
                    tempFilename=os.path.join(head,tempFilename)
                else:
                    tempFilename=doc
                outfile.write('\n' + startString + tempFilename + endString + '.\n')
            try:
                with open(doc,'r', encoding="utf-8",errors='ignore') as infile:
                    outfile.write(infile.read())
            except:
                fileError+=1
                if fileError<=1:
                    IO_user_interface_util.timed_alert(window, 700, 'Input file error', 'An error was encountered processing input file\n\n' + str(inputFilename) + "\n\nProcessing other files will continue but, please, check the corrupt input file. Files in error will be listed in command line.")
                print('File in error: ' + str(doc))
                if len(doc)>256:
                    fileLengthError+=1
                fileError+=1
        msg=str(numberOfDocs) + " files have been processed in input.\n\n"
        if fileError>0:
            msg=msg + str(fileError) + " files have errors.\n\n"
            if fileLengthError>0:
                msg=msg+ str(fileLengthError) + " files have combined path + filename greater than Windows limit of 260 characters.\n\n"
            msg=msg+"Files with errors have been listed in command line.\n\nPlease, check these files carefully and try again."
        else:
            msg=msg+"All files have been merged successfully."
        tk.messagebox.showwarning(title='Warning', message=msg)

    if openOutputFiles==True:
        IO_files_util.openFile(window, outFilename)
