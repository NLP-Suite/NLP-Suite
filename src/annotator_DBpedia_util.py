# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi, Zhangyi Pan

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"annotator_DBpedia.py",['os','subprocess','time'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
from subprocess import call
from time import sleep

import IO_user_interface_util
import file_splitter_ByLength_util
import GUI_IO_util
import IO_files_util


"""
A simple python wrapper for DBpedia spotlight

This relies on DBpedia's own web server to run

It is also possible to create a local server via:
    
    1) wget http://downloads.DBpedia-spotlight.org/spotlight/DBpedia-spotlight-0.7.1.jar
    2) wget http://downloads.DBpedia-spotlight.org/2016-04/en/model/en.tar.gz
    3) tar xzf en.tar.gz
    4) java -jar DBpedia-spotlight-latest.jar en http://localhost:2222/rest

Eventual implementation of local server would be more reliable/faster...
...but would require extra downloads/setup on students' behalf

# The script handles text annotation via DBpedia (outputs html)
# inputDir is .txt files to annotate
# outputDir is location to save .html annotated files
# annotationTypes = ['Person','WrittenWork'] # example used in chong (fast)

# annotation types should be user-provided via GUI
# details on all supported annotation types can be found at: 
# https://github.com/DBpedia-spotlight/DBpedia-spotlight/wiki/User's-manual
# or at https://www.DBpedia-spotlight.org/demo/
"""

#from urllib.request import urlopen

# TODO possible to annotate different types in different colors?
def DBpedia_annotate(inputFile, inputDir, outputDir, openOutputFiles, annotationTypes, confidence_level=0.5):

    # check for internet; DBpedia accesses the DBpedia server
    #if not IO_util.check_internet_availability_warning("DBpedia annotator"):
    #    return
    # turn annotation types list into string compatible with DBpedia
    filesToOpen = []
    annotationOpts = ''
    splitTxtFileList=[] 
    n = len(annotationTypes)
    # on owl https://www.w3.org/TR/owl-ref/#:~:text=Like%20RDF%20classes%2C%20every%20OWL,equal%20to%20its%20class%20extension.
    # Two OWL class identifiers are predefined, 
    #   namely the classes owl:Thing and owl:Nothing.
    #   The class extension of owl:Thing is the set of all individuals. 
    #   The class extension of owl:Nothing is the empty set. Consequently, every OWL class is a subclass of owl:Thing and owl:Nothing is a subclass of every class (for the meaning of the subclass relation, see the section on rdfs:subClassOf).

    if n ==0:
        annotationTypes= ['owl#Thing', 'unknown']
        # annotationTypes= []
    if n ==1:
        if annotationTypes==['Thing']:
            annotationTypes=['owl#Thing', 'unknown']
            n=0

    for i in range(n):
        if i==n-1:
            annotationOpts = annotationOpts+annotationTypes[i]
        else:
            annotationOpts = annotationOpts+annotationTypes[i]+','

    # loop through every file and annotate via request to DBpedia
    files=IO_files_util.getFileList(inputFile, inputDir, '.txt')
    nFile=len(files)
    if nFile==0:
        return

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start', 'Started running DBpedia annotator at', True, '\nAnnotating types: ' + str(annotationTypes) + '\nConfidence level: ' + str(confidence_level))
    print('\n\nAnnotating types: ', annotationTypes, 'with confidence level', str(confidence_level))

    i=0
    for file in files:
        splitHtmlFileList=[] 
        i=i+1
        print("Processing file " + str(i) + "/" + str(nFile) + " " + file)
        # Windows error: The command line is too long.
        # 32767 characters max https://support.thoughtworks.com/hc/en-us/articles/213248526-Getting-around-maximum-command-line-length-is-32767-characters-on-Windows
        # https://stackoverflow.com/questions/3205027/maximum-length-of-command-line-string
        # https://stackoverflow.com/questions/55969620/how-do-i-fix-the-error-the-command-line-is-too-long-if-i-want-to-have-the-outp
        # https://stackoverflow.com/questions/49607998/the-command-line-is-too-longwindows
        adjust='\n\nIf DBpedia fails and returns in command line "The command line is too long", lower the value of the file size using the slider widget and try again.'
        if sys.platform == 'win32':
            defaultSize = 7000
            minsize=4000
            maxsize=30000
            message='Windows/DBpedia can process files of size smaller than the Windows command line. In Windows, 32767 seems to be the command line size but ' + str(defaultSize) + ' sometimes fails. ' + adjust
        else:
            defaultSize = 30000
            minsize = 20000
            maxsize=100000
            message='Mac/DBpedia set a limit to the file size that it can process.' + adjust
        contents = open(file, 'r', encoding='utf-8',errors='ignore').read()
        if len(contents)>defaultSize:
            splitFileValue=GUI_IO_util.slider_widget(GUI_util.window,message, minsize, maxsize, defaultSize)
        else:
            splitFileValue=defaultSize

        listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,'DBpedia',file,outputDir, splitFileValue)
        # else:
        #     listOfFiles=[file]
        
        subFile=0
        for doc in listOfFiles:
            outFilename = os.path.join(outputDir,"NLP_DBpedia_annotated_" + os.path.split(doc)[1].split('.txt')[0]+'.html')
            splitHtmlFileList.append(outFilename)
            if len(listOfFiles)>1:
                splitTxtFileList.append(doc)
                subFile=subFile+1
                print("   Processing split-file " + str(subFile) + "/" + str(len(listOfFiles)) + " " + doc)

            contents = open(doc, 'r', encoding='utf-8',errors='ignore').read()
            contents = contents.replace('\0', '') # remove null bytes
            contents = contents.replace("\"", '') # remove quotations

            if sys.platform == 'win32': # windows friendly commands
                # necessary for Windows only
                contents = contents.replace('\n', ' ') # remove new lines 
                outFilename = "\"" + outFilename + "\"" #solution to permission error
                # https://github.com/dbpedia-spotlight/dbpedia-spotlight-model
                # under call our web service
                contents_url = contents.replace("\n","%20")
                contents_url = contents_url.replace(" ","%20")
                #cmd = ["curl http://model.dbpedia-spotlight.org/en/annotate --data-ascii \"text="+contents+"\" --data \"confidence="+str(confidence_level)+"\" --data \"support=20\" --data \"types="+annotationOpts+"\""]
                cmd = ["curl -X GET \"https://api.dbpedia-spotlight.org/en/annotate?text="+contents_url+"&confidence="+str(confidence_level)+"&types="+annotationOpts+"\" -H \"accept: text/html\""]
                cmd_str = 'cmd /c '
                for item in cmd:
                    cmd_str = cmd_str+item
                cmd_str = cmd_str + ' -o ' + outFilename
                msg=os.system(cmd_str)
                sleep(2)
                # the " were added to make DBpedia work but...
                #   they become part of the filename and not recognized
                #   in the OpenOutputFiles function io IO_util 
                for letter in outFilename:
                    if letter == '"':
                        outFilename = outFilename.replace(letter,"")
                if not IO_files_util.checkFile(outFilename,'.html',True):
                    mb.showwarning(title='Warning',
                                   message='The DBpedia annotator did not produce any output file.\n\nMost likely, the filesize value of ' + str(splitFileValue) + ' is too large for DBpedia to handle.\n\nPlease, check in command line for a possible error \'The command line is too long.\' If so, reduce the filesize value and try again.')
                    return
            else:
                #cmd = ["curl http://model.dbpedia-spotlight.org/en/annotate --data-ascii \"text="+contents+"\" --data \"confidence="+str(confidence_level)+"\" --data \"support=20\" --data \"types="+annotationOpts+"\"", "-o \""+outFilename+"\""]
                contents_url = contents.replace("\n","%20")
                contents_url = contents_url.replace(" ","%20")
                cmd = ["curl -X GET \"https://api.dbpedia-spotlight.org/en/annotate?text="+contents_url+"&confidence="+str(confidence_level)+"&types="+annotationOpts+"\" -H \"accept: text/html\""]
                with open(outFilename, 'w+') as output:
                    call(cmd,shell=True,stdout=output)
                    output.close()
                sleep(2)
        if subFile>0:
            # outFilename here is the combined html file from the split files
            outFilename=os.path.join(outputDir,"NLP_DBpedia_annotated_" + os.path.split(file)[1].split('.txt')[0]+'.html')
            with open(outFilename, 'w',encoding="utf-8",errors='ignore') as outfile:
                for htmlDoc in splitHtmlFileList:
                    with open(htmlDoc,'r', encoding="utf-8",errors='ignore') as infile:
                        for line in infile:
                            outfile.write(line)
                    infile.close()
                    os.remove(htmlDoc) # delete temporary split html file from output directory
        filesToOpen.append(outFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running DBpedia annotator at', True)

    return filesToOpen
