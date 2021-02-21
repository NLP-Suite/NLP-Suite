#Written by Cynthia Dong October 2019
#Edited Roberto Franzosi

import sys
import IO_files_util
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Stanford_CoreNLP_parser",['pycorenlp','os','csv','json','subprocess','time','tkinter'])==False:
    sys.exit(0)

import pycorenlp
from pycorenlp import StanfordCoreNLP
import tkinter.messagebox as mb

import csv
#import io
import time
#import logging
import json
import subprocess
from subprocess import call
import os

import IO_CoNLL_util
import Stanford_CoreNLP_clausal_util
import file_splitter_ByLength_util
import IO_csv_util
import IO_user_interface_util

# the function processes one file (with path) at a time
#   checking for the max length allowed by CoreNLP
#   90000 in number of characters
def prepare_text(filename_path):
    # # split the input file into the path part (head)
    # #   the head will be used as the new output path
    # #   since split files are stored as a subfolder of the input dir
    # head, file_name = os.path.split(filename_path)
    # listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,filename_path,file_name,head)
    listOfFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window,'Stanford CoreNLP',filename_path)
    return listOfFiles

# dateInclude indicates whether there is date embedded in the file name. 
# 1: included 0: not included
def run(inputFilename, inputDir, outputDir, parser_menu_var, openOutputFiles, createExcelCharts, memory_var, compute_sentence, dateInclude, sep = "_", date_field_position = 3, dateFormat = "mm-dd-yyyy"):
    # collecting all files that needs to be processed
    # when processing a directory as input
    #   Document is the directory name
    #   rather than single filename in directory
    filesToOpen = []  # Store all files that are to be opened once finished

    # check that the CoreNLPdir as been setup
    CoreNLPdir=IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_parser', 'Stanford CoreNLP')
    if CoreNLPdir== '':
        return filesToOpen

    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('SVO extractor')
    if errorFound:
        return filesToOpen

    if len(inputDir) != 0:
        inputDocs = [os.path.join(inputDir, f) for f in os.listdir(inputDir) if f[:2] != '~$' and f[-4:] == '.txt']
        if len(inputDocs) == 0:
            mb.showwarning("Warning", "There are no txt files in the input directory.\n\nPlease, select a different directory and try again.\n\nThe program will exit.")
            print("There are no txt files in the input directory. The program will exit.")
            return
        # head contains the path only
        head, Document = os.path.split(inputDir)
    else:
        inputDocs = [inputFilename]
        # head contains the path only
        head, Document = os.path.split(inputFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Stanford CoreNLP start',
                                       'Started running Stanford CoreNLP parser at', True,
                                       'You can follow CoreNLP in command line.')

    nDocs=len(inputDocs)

    # run the command java -mx5g -cp "stanford corenlp directory" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000
    # connect to server
    p = subprocess.Popen(
        ['java', '-mx' + str(memory_var) + "g", '-cp', os.path.join(CoreNLPdir,'*'), 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    # wait for subprocess
    time.sleep(5)
    nlpObject = StanfordCoreNLP('http://localhost:9000')
    # nlpProps = {'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,regexner,NormalizedNamedEntityTagAnnotation','outputFormat': 'json', 'outputDirectory': outputDir, 'replaceExtension': True}
    if parser_menu_var == 'Probabilistic Context Free Grammar (PCFG)':
        nlpProps = {'annotators': 'tokenize,ssplit,pos,lemma,ner, parse,regexner,', 'parse.model': 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz','outputFormat': 'json', 'outputDirectory': outputDir, 'replaceExtension': True}
    elif parser_menu_var == 'Neural Network':
        nlpProps = {'annotators': 'tokenize,ssplit,pos,lemma,ner, depparse,regexner,', 'parse.model': 'edu/stanford/nlp/models/parser/nndep/english_UD.gz','outputFormat': 'json', 'outputDirectory': outputDir, 'replaceExtension': True}
    outputCoNLLfilePath = os.path.join(outputDir,
                                       IO_files_util.generate_output_file_name(Document, '', outputDir, '.csv', 'CoreNLP', 'CoNLL'))
    
    with open(outputCoNLLfilePath, "w",newline = "", encoding='utf-8',errors='ignore') as csvFile:
        writer = csv.writer(csvFile)
        if dateInclude == 0:
            writer.writerow(["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Clausal Tag", "Record ID", "Sentence ID", "Document ID", "Document"])
        else:
            writer.writerow(
                ["ID", "Form", "Lemma", "POStag", "NER", "Head", "DepRel", "Clausal Tag", "Record ID", "Sentence ID",
                 "Document ID", "Document", "Date"])
    recordID = 1
    DocumentID = 1
    for file in inputDocs:
        # process file for CoreNLP server max-allowed file lenght of 90,000 characters
        # split_file is the same as file if file is shorter than 90,000 characters
        split_file = prepare_text(file)
        sentenceID = 1
        filesError=[]
        if dateInclude == 1:
        	date, dateStr = IO_files_util.getDateFromFileName(file, sep, date_field_position, dateFormat)
        for doc in split_file:
            # split doc to get filename only - tail - for display purposes
            head, tail = os.path.split(doc)
            print("\nProcessing file " + str(DocumentID) + "/" + str(nDocs) + ' ' + tail)
            f = open(doc, "r",encoding='utf-8',errors='ignore')
            fullText = f.read()
            f.close()
            nlpObject = StanfordCoreNLP('http://localhost:9000')
            CoreNLP_output = nlpObject.annotate(fullText, nlpProps)
            errorFound, filesError, CoreNLP_output = IO_user_interface_util.process_CoreNLP_error(GUI_util.window, CoreNLP_output, doc, nDocs, filesError)
            if errorFound: continue # process next document
            if parser_menu_var == 'Probabilistic Context Free Grammar (PCFG)':
                sent_list_clause = [Stanford_CoreNLP_clausal_util.clausal_info_extract_from_string(parsed_sent['parse'])
                        for parsed_sent in CoreNLP_output['sentences']]
            with open(outputCoNLLfilePath, "a",newline = "", encoding='utf-8',errors='ignore') as csvFile:
                writer = csv.writer(csvFile)
                for i in range(len(CoreNLP_output["sentences"])):
                    if parser_menu_var == 'Probabilistic Context Free Grammar (PCFG)':
                        cur_clause = sent_list_clause[i]
                    clauseID = 0
                    tokens = CoreNLP_output["sentences"][i]["tokens"]
                    dependencies = CoreNLP_output["sentences"][i]["enhancedDependencies"]
                    depLib = {}
                    keys = []
                    for item in dependencies:
                        depLib[item['dependent']] = (item['dep'], item['governor'])
                        keys.append(item['dependent'])
                    depID = 1
                    for row in tokens:
                        # if row["ner"]=="DATE":
                        #     print("NER normalized DATE ",row["normalizedNER"])
                        tmp = []
                        tmp.append(row["index"])
                        tmp.append(row["word"])
                        tmp.append(row["lemma"])
                        tmp.append(row["pos"])
                        tmp.append(row["ner"])
                        if depID not in depLib:
                            tmp.append("")
                            tmp.append("")
                        else:
                            tmp.append(depLib[depID][1])
                            tmp.append(depLib[depID][0])
                        depID += 1
                        if parser_menu_var == 'Probabilistic Context Free Grammar (PCFG)':
                            tmp.append(cur_clause[clauseID][0])
                        else:
                            tmp.append("")
                        # tmp.append(" ")
                        clauseID += 1
                        tmp.append(str(recordID))
                        recordID += 1
                        tmp.append(str(sentenceID))
                        tmp.append(str(DocumentID))
                        # tmp.append(file)
                        tmp.append(IO_csv_util.dressFilenameForCSVHyperlink(doc))
                        if dateInclude == 1 and dateStr!='DATE ERROR!!!':
                            tmp.append(dateStr)
                        writer.writerow(tmp)
                    sentenceID += 1
        DocumentID += 1

    csvFile.close()
    p.kill()  #close the Stanford server
    if len(filesError)>0:
        errorFile = os.path.join(outputDir,
                                           IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv',
                                                                                   'CoreNLP', 'file_ERRORS'))
        mb.showwarning("Stanford CoreNLP Error", 'Stanford CoreNLP parser has found '+str(len(filesError))+' files that could not be processed by Stanford CoreNLP.\n\nPlease, read the error output file carefully to see the errors generated by CoreNLP.')
        print(str(len(filesError)) +' files could not be processed by Stanford CoreNLP. Error file saved to ' + errorFile)
        IO_csv_util.list_to_csv(GUI_util.window, filesError, errorFile)
        filesToOpen.append(errorFile)

    filesToOpen.append(outputCoNLLfilePath)

    if IO_csv_util.GetNumberOfRecordInCSVFile(outputCoNLLfilePath) == 1: # contains headers line only
        mb.showwarning("CoNLL table output", outputCoNLLfilePath + ' CoNLL table produced by Stanford CoreNLP is empty.')
        print("\nEmpty CoNLL table output written to: ", outputCoNLLfilePath)
    else:
        print("\nCoNLL table output written to: ", outputCoNLLfilePath)
        if len(inputDir) != 0:
            mb.showwarning(title='Warning',
                           message='The output filename generated by Stanford CoreNLP is the name of the directory processed in input, rather than any individual file in the directory. The output CoNLL table includes all ' + str(
                               DocumentID - 1) + ' files in the input directory processed by CoreNLP.\n\nThe different files are listed in the output csv file under the headers \'Document ID\' and \'Document\'.')
        if compute_sentence:
            if IO_csv_util.GetNumberOfRecordInCSVFile(outputCoNLLfilePath)==1:
                sentence_table=IO_CoNLL_util.compute_sentence_table(outputCoNLLfilePath,outputDir)
                filesToOpen.append(sentence_table)

    if openOutputFiles==True:
    	IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Stanford CoreNLP end',
                                       'Finished running Stanford CoreNLP parser at', True)

    return outputCoNLLfilePath