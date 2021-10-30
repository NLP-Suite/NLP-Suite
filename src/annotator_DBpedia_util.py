# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi October 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "annotator_DBpedia.py",
                                          ['os', 'subprocess', 'time']) == False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
from subprocess import call
from time import sleep
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import urllib
import urllib.parse

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


# from urllib.request import urlopen

# TODO possible to annotate different types in different colors?
def DBpedia_annotate(inputFile, inputDir, outputDir, openOutputFiles, annotationTypes, confidence_level=0.5):
    # check for internet; DBpedia accesses the DBpedia server
    # if not IO_util.check_internet_availability_warning("DBpedia annotator"):
    #    return
    # turn annotation types list into string compatible with DBpedia
    filesToOpen = []
    annotationOpts = ''
    splitTxtFileList = []
    n = len(annotationTypes)
    # on owl https://www.w3.org/TR/owl-ref/#:~:text=Like%20RDF%20classes%2C%20every%20OWL,equal%20to%20its%20class%20extension.
    # Two OWL class identifiers are predefined,
    #   namely the classes owl:Thing and owl:Nothing.
    #   The class extension of owl:Thing is the set of all individuals.
    #   The class extension of owl:Nothing is the empty set. Consequently, every OWL class is a subclass of owl:Thing and owl:Nothing is a subclass of every class (for the meaning of the subclass relation, see the section on rdfs:subClassOf).

    if n == 0:
        annotationTypes = ['owl#Thing', 'unknown']
        # annotationTypes= []
    if n == 1:
        if annotationTypes == ['Thing']:
            annotationTypes = ['owl#Thing', 'unknown']
            n = 0

    for i in range(n):
        if i == n - 1:
            annotationOpts = annotationOpts + annotationTypes[i]
        else:
            annotationOpts = annotationOpts + annotationTypes[i] + ','

    # loop through every file and annotate via request to DBpedia
    files = IO_files_util.getFileList(inputFile, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running DBpedia annotator at', True,
                                                   '\nAnnotating types: ' + str(
                                                       annotationTypes) + '\nConfidence level: ' + str(
                                                       confidence_level))
    print('\n\nAnnotating types: ', annotationTypes, 'with confidence level', str(confidence_level))

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    adjust = '\n\nIf DBpedia fails and returns in command line "The command line is too long", lower the value of the file size using the slider widget and try again.'
    if sys.platform == 'win32':
        defaultSize = 7000
        minsize = 4000
        maxsize = 30000
        message = 'Windows/DBpedia can process files of size smaller than the Windows command line. In Windows, 32767 seems to be the command line size but ' + str(
            defaultSize) + ' sometimes fails. ' + adjust
    else:
        defaultSize = 3000
        minsize = 3000
        maxsize = 100000
        message = 'Mac/DBpedia set a limit to the file size that it can process.' + adjust

    i = 0
    for file in files:
        splitHtmlFileList = []
        i = i + 1
        head, tail = os.path.split(file)
        print("Processing file " + str(i) + "/" + str(nFile) + " " + tail)
        outFilename = os.path.join(outputDir,
                                   "NLP_DBpedia_annotated_" + os.path.split(file)[1].split('.txt')[0] + '.html')
        # Windows error: The command line is too long.
        # 32767 characters max https://support.thoughtworks.com/hc/en-us/articles/213248526-Getting-around-maximum-command-line-length-is-32767-characters-on-Windows
        # https://stackoverflow.com/questions/3205027/maximum-length-of-command-line-string
        # https://stackoverflow.com/questions/55969620/how-do-i-fix-the-error-the-command-line-is-too-long-if-i-want-to-have-the-outp
        # https://stackoverflow.com/questions/49607998/the-command-line-is-too-longwindows
        contents = open(file, 'r', encoding='utf-8', errors='ignore').read()
        splitFileValue = defaultSize
        subFile = 0
        listOfFiles=files
        # listOfFiles.remove(file)
        j=0
        while j < len(listOfFiles):
            doc=listOfFiles[j]
            if subFile>0:
                if listOfFiles[0]==file:
                    # do not process the first large file and process only split files
                    continue
                head, tail = os.path.split(doc)
                print('  Processing split file ' + str(j+1) + "/" + str(len(listOfFiles)) + ' ' + tail + ' with DBpedia size ' + str(defaultSize))
                split_outFilename = os.path.join(outputDir,
                                           "NLP_DBpedia_annotated_" + tail[:-4] + '.html')
                # splitHtmlFileList.append(split_outFilename)
            contents = open(doc, 'r', encoding='utf-8', errors='ignore').read()
            # for doc in listOfFiles: # processing split subfiles
            BASE_URL = 'http://api.dbpedia-spotlight.org/en/annotate?text={text}&confidence={confidence}&support={support}'

            CONFIDENCE = confidence_level
            SUPPORT = '20'
            REQUEST = BASE_URL.format(
                text=urllib.parse.quote_plus(contents),
                confidence=CONFIDENCE,
                support=SUPPORT
            )
            print('REQUEST',REQUEST) # REQUEST contains the url to the html annotated input file
            HEADERS = {'Accept': 'application/json'}
            all_urls = []

            r = requests.get(url=REQUEST, headers=HEADERS)
            # print('RESPONSE r.status_code', r.status_code)
            # 200 = OK
            # 400 bad request
            # 414 line too long
            if r.status_code == requests.codes['ok']:
                splitHtmlFileList.append(REQUEST)
                response = r.json()
                resources = response['Resources']
                for res in resources:
                    all_urls.append(res['@URI'])
                    # print(all_urls)
                    # print('      DBpedia resource',res['@URI'])
            else:
                if r.status_code == 414: # line too long
                    if defaultSize == 7000: # avoid repeating message
                        mb.showwarning(title='Warning',
                                       message='The DBpedia annotator did not produce any annotated output file for the document\n\n' + doc + '\n\nMost likely, the filesize value of ' + str(
                                           splitFileValue) + ' is too large for DBpedia to handle.\n\nPlease, check in command line for a possible error \'The command line is too long.\' If so, reduce the filesize value and try again.')
                    # set new default value to avoid repeating warning
                    print('Line too long ',str(len(contents)),'(current split size', str(defaultSize), ') for document',doc,' Document to be split.')
                    defaultSize=defaultSize-1000
                    splitFileValue=defaultSize
                if defaultSize < 2000: # other errors have occurred
                    print('Split size below 2000. Algorithm exiting...')
                    return
                listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window, 'DBpedia',
                                                                                 doc, outputDir,
                                                                                 splitFileValue)
                subFile=len(listOfFiles)
                j=-1
            j = j + 1
        if subFile > 0:
            # outFilename here is the combined html file from the split files
            with open(outFilename, 'w', encoding="utf-8", errors='ignore') as outfile:
                for url in splitHtmlFileList:
                    import ssl
                    from urllib.request import urlopen
                    url = ssl.SSLContext()  # Only for url
                    content = urllib.request.urlopen(url).read()
                    outfile.write(content)
                outfile.close()
                # os.remove(htmlDoc)  # delete temporary split html file from output directory
        j = 0
        subFile=0
        filesToOpen.append(outFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running DBpedia annotator at',
                                       True, '', True, startTime)

    return filesToOpen