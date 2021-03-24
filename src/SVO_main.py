#Written by Gabriel Wang 2018
##########################################
#Modified by Cynthia Dong (Fall 2019-Spring 2020)
##########################################

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"SVO extractor",['unittest','subprocess','os','tkinter','ntpath','stanfordnlp','difflib','csv','random'])==False:
    sys.exit(0)

from collections import defaultdict
import os
import nltk
from nltk.tree import *
import nltk.draw
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import csv
import tkinter as tk
from tkinter import *
import tkinter.messagebox as mb
import subprocess
# to install stanfordnlp, first install
#   pip3 install torch===1.3.1 torchvision===0.4.2 -f https://download.pytorch.org/whl/torch_stable.html
#   pip3 install stanfordnlp
import stanfordnlp


import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import Gephi_util
import GIS_pipeline_util
import wordclouds_util
import GUI_util
import file_merger_util
import file_utf8_compliance_util
import file_cleaner_util
import IO_csv_util
import Stanford_CoreNLP_coreference_util as stanford_coref
import Stanford_CoreNLP_annotator_util
import semantic_role_labeling_senna
# RUN section ______________________________________________________________________________________________________________________________________________________

# Pipeline needs the en model. To install "en" model:
# Open your command prompt or terminal, type in following commands one at a time
# python
# import stanfordnlp
# stanfordnlp.download("en")
# exit()
# After you are done with these steps, you can comment out the following line


try:
    nlp = stanfordnlp.Pipeline(processors='tokenize,mwt,pos,lemma')
except:
    stanfordnlp.download('en')
    nlp = stanfordnlp.Pipeline(processors='tokenize,mwt,pos,lemma')

lemmalib = {}
voLib = {}
notSure = set()
added = set()

caps = "([A-HJ-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"



def extract_svo(svo_triplets, svo_result, svo_merge_filename, subject_list, verb_list, object_list, field_names, document_index, Document):
    """
    Extract SVO triplets form a Sentence object.
    """
    global lemmalib
    global notSure
    global added
    lemmatizer = WordNetLemmatizer()
    result = IO_files_util.openCSVFile(svo_result, 'w')
    if result=='':
        return
    svo_writer = csv.DictWriter(result, fieldnames=field_names)
    svo_writer.writeheader()
    if len(svo_merge_filename) > 0:
        merge_result = IO_files_util.openCSVFile(svo_merge_filename, 'a')
        if merge_result == '':
            return
        svo_merge_writer = csv.DictWriter(merge_result, fieldnames=field_names)
    for svo in svo_triplets:
        # RF if len(svo[2]) == 0 or len(svo[3]) == 0:
        if len(svo[2]) == 0 or len(svo[3]) == 0 or len(svo[4]) == 0:
                continue
        # check if the triple needs to be included
        flag = False
        # RF if len(subject_list) == 0 and len(verb_list) == 0:
        if len(subject_list) == 0 and len(verb_list) == 0 and len(object_list) == 0:
            # no filter
            flag = True
        else:
            if len(subject_list) != 0:
                # filter subject
                if svo[2] in lemmalib:  # subject
                    lemma1 = lemmalib[svo[2]]
                else:
                    #lemma1 = nlp(svo[2]).sentences[0].words[0].lemma
                    lemma1 = lemmatizer.lemmatize(svo[2], 'n')
                    lemmalib[svo[2]] = lemma1
                if lemma1 in subject_list:
                    flag = True
            elif len(verb_list) != 0:
                # filter verb
                if svo[3] in lemmalib:  #verb
                    lemma2 = lemmalib[svo[3]]
                else:
                    #lemma2 = nlp(svo[3]).sentences[0].words[0].lemma
                    lemma2 = lemmatizer.lemmatize(svo[3], 'v')
                    lemmalib[svo[3]] = lemma2
                if lemma2 in verb_list:
                    flag = True
            # RF comment these lines out
            else:
                # filter object
                if svo[4] in lemmalib:  # object
                    lemma3 = lemmalib[svo[4]]
                else:
                    #lemma3 = nlp(svo[4]).sentences[0].words[0].lemma
                    lemma3 = lemmatizer.lemmatize(svo[4], 'n')
                    lemmalib[svo[4]] = lemma3
                if lemma3 in object_list:
                    flag = True

        if flag:
            if svo[2] == "Someone?" and (svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]) not in added:
                notSure.add((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))
                continue
            if svo[2] != "Someone?":
                if (svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]) in notSure:
                    notSure.remove((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))
                # before writing row, split location
                if " " in svo[5]:
                    location_list = svo[5].split(" ")
                    for each_location in location_list:
                        svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]), 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                             'TIME': svo[6], 'LOCATION': each_location, 'PERSON': svo[7],
                                             'TIME_STAMP': svo[8], field_names[10]: svo[1]
                                             })
                        if len(svo_merge_filename) > 0:
                            svo_merge_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]), 'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                             'TIME': svo[6], 'LOCATION': each_location, 'PERSON': svo[7],
                                             'TIME_STAMP': svo[8], field_names[10]: svo[1]
                                             })
                else:
                    svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),  'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                         'TIME': svo[6], 'LOCATION': svo[5], 'PERSON': svo[7], 'TIME_STAMP': svo[8],
                                         field_names[10]: svo[1]
                                         })
                    if len(svo_merge_filename) > 0:
                        svo_merge_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),  'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                         'TIME': svo[6], 'LOCATION': svo[5], 'PERSON': svo[7], 'TIME_STAMP': svo[8],
                                         field_names[10]: svo[1]
                                         })
                added.add((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))

def run(inputFilename, inputDir, outputDir,
        utf8_var,
        ASCII_var,
        Coref,
        Coref_Option,
        memory_var,
        Manual_Coref_var,
        date_extractor_var,
        CoreNLP_SVO_extractor_var,
        SENNA_SVO_extractor_var,
        subjects_dict_var,
        verbs_dict_var,
        objects_dict_var,
        gephi_var,
        wordcloud_var,
        google_earth_var,
        openOutputFiles,createExcelCharts):

    memory_var = 64

    filesToOpen = []

    merge_file_option = None
    save_intermediate_file = False

    if len(inputDir) > 0:
        msgbox_merge_file = mb.askyesno("Merge File Option", "You selected to process a directory of files.\n\n" +
                                    "DO YOU WANT TO MERGE FILES INTO A SINGLE ONE AND PROCESS THE MERGED FILE?\n\n" +
                                    "WARNING! Merging files leads to faster processing time but... " +
                                    "your laptop may run out of memory; if that's the case, allocate as much memory as possible using the memory slidebar and try again.\n\nAlternatively, do not use the merge option.\n\nDo you still want to merge files?",default='no')
        if msgbox_merge_file:
            merge_file_option = True
        else:
            merge_file_option = False

        if not msgbox_merge_file:
            save_intermediate_file = mb.askyesno("Save Intermediate File Option", "You selected to process a directory of files,\n\nDo you want to save the csv output for each single file?\n\nClick No if you only want to keep a final merged output csv file. The merged file will contain both the name and ID of every document processed, so there is really no need to save intermediate files.\n\nDo you still want to save individual output files?",default='no')

    if inputFilename[-4:] == '.txt':
        if (CoreNLP_SVO_extractor_var == False and SENNA_SVO_extractor_var == False) and (gephi_var == True or wordcloud_var == True or google_earth_var == True):
            mb.showerror(title='Inputfile/option error',
                         message="The data visualization option(s) you have selected require either an _svo.csv/_SVO_Result file in input or CoreNLP OpenIE and/or SENNA selected.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return
    elif inputFilename[-4:] == '.csv':
        if inputFilename[-8:] != '-svo.csv':
            mb.showerror(title='Inputfile error',
                         message="The selected input is a csv file, but... not an _svo.csv file.\n\nPlease, select an _svo.csv file (or a txt file) and try again.")
            return
        if (utf8_var == True or Coref == True or Coref_Option == True or memory_var == True or Manual_Coref_var == True or date_extractor_var == True or CoreNLP_SVO_extractor_var == True):
            mb.showerror(title='Inputfile/option error',
                         message="The data analysis option(s) you have selected require in input a txt file, rather than a csv file.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return

    if 'svo.csv' in inputFilename:
        fileExtension=".csv"
    else:
        fileExtension="-svo.csv"

    if merge_file_option:
        file_merger_util.file_merger(GUI_util.window, inputDir, outputDir, False, processSubdir=False,saveFilenameInOutput=False, embedSubdir=False, writeRootDirectory=False)
        rootDir = os.path.basename(os.path.normpath(inputDir))
        inputFilename = os.path.join(outputDir,'merged_Dir_'+rootDir +'.txt')
        inputDir = ""


    # if IO_libraries_util.inputProgramFileCheck('annotator_colorfulYAGO_util')==False or IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_OpenIE.jar')==False:
    #     return
    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('SVO extractor')
    if errorFound:
        return

    Coref_Option = Coref_Option.lower()

    if utf8_var==True:
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                            'Started running utf8 compliance test at', True)
        file_utf8_compliance_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles)

    if ASCII_var == True:
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                                           'Started running characters conversion at', True)
        file_cleaner_util.convert_quotes(GUI_util.window, inputFilename, inputDir)

    isFile = True
    inputFileBase = ""
    inputDirBase = ""
    inputBaseList = []
    svo_result_list = []
    document_index = 1
    svo_merge_filename = ""

    if len(inputFilename) > 0:
        inputFileBase = os.path.basename(inputFilename)[0:-4] # without .csv or .txt
    else:
        isFile = False
        inputDirBase = os.path.basename(inputDir)
        outputDir = os.path.join(outputDir, inputDirBase + "_output")
        # if not os.path.exists(os.path.dirname(outputDir)):
        #     os.makedirs(os.path.dirname(outputDir))
        if not os.path.exists(outputDir):       # Changed by Matthew on Mar.13
            os.makedirs(outputDir)

    # CoRef _____________________________________________________

    # field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'PERSON', 'TIME', 'TIME_STAMP', 'Sentence']
    if isFile:
        feed_to_svo = inputFilename
    else:
        feed_to_svo = inputDir
    if Coref:
        # field_names[10] = "Corefed Sentence"
        if not isFile:
            outputCorefedDir = os.path.join(outputDir, "CoRefed_Files")
            if not os.path.exists(os.path.dirname(outputCorefedDir)):
                os.makedirs(os.path.dirname(outputCorefedDir))
            file_open, error = stanford_coref.run(inputFilename, inputDir, outputCorefedDir, openOutputFiles, createExcelCharts,
                                                  memory_var, Coref_Option,
                                              Manual_Coref_var)
        else:
            file_open, error = stanford_coref.run(inputFilename, inputDir, outputDir,
                                                  openOutputFiles, createExcelCharts,
                                                  memory_var, Coref_Option,
                                                  Manual_Coref_var)
            if len(file_open) > 0:
                filesToOpen.append(file_open)

        if error == 0:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Stanford CoreNLP Co-Reference Resolution',
                                'Finished running Stanford CoreNLP Co-Reference Resolution using the ' + Coref_Option + ' approach at',
                                               True)
            if isFile:
                feed_to_svo = os.path.join(outputDir, inputFileBase + "-CoRefed.txt")
            else:
                feed_to_svo = outputCorefedDir
        else:
            msgbox_exit = tk.messagebox.askyesno("Co-Reference Resolution Error",
                                                 "Stanford CoreNLP Co-Reference Resolution throws error, " +
                                                 "and you either didn't choose manual Co-Reference Resolution or manual Co-Referenece Resolution fails as well.\n\n " +
                                                 "Do you want to use the original file to continue SVO process? If not, the process ends now.")
            if msgbox_exit:
                if isFile:
                    feed_to_svo = inputFilename
                else:
                    feed_to_svo = inputDir
            else:
                sys.exit()


    # Date extractor _____________________________________________________

    if date_extractor_var:
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                            'Started running Stanford CoreNLP date annotator at', True)
        files = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, inputDir, outputDir,
                                                                 openOutputFiles, createExcelCharts,
                                                            'normalized-date', False, memory_var)
        filesToOpen.extend(files)


        #date_extractor.run(CoreNLPdir, inputFilename, inputDir, outputDir, False, False, True)
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis end',
                            'Finished running Stanford CoreNLP date annotator at', True)
        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

    if not isFile:
        outputSVODir = os.path.join(outputDir, "SVO_Result")
    else:
        outputSVODir = ''

    # TODO When both OpenIE and SENNA are run, must export 2 csv files
    #   one file with the frequency of same SVOs, same SVs, different SVOs, different SVs
    #   a second file with the same SVO listings of document ID, sentence ID, ..., S, V, O, ... but with a first column Package with values OpenIE or SENNA

    # SENNA _____________________________________________________
    if SENNA_SVO_extractor_var==True:
        # TODO must use the coreferenced input file if the user selected that option
        # TODO must filter SVO results by social actors if the user selected that option
        #   both options run correctly for OppenIE
        files = []
        if save_intermediate_file:
            for file in IO_files_util.getFileList(inputFile=inputFilename, inputDir=inputDir, fileType='.txt'):
                files += semantic_role_labeling_senna.run_senna(inputFilename=file, inputDir='', outputDir=outputDir, openOutputFiles=openOutputFiles, createExcelCharts=createExcelCharts)
        else:
            files = semantic_role_labeling_senna.run_senna(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts)
        filesToOpen.extend(files)
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis end',
                                           'Finished running Senna at', True)
        if openOutputFiles:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

        for file in files:
            svo_result_list.append(file)

    # CoreNLP OpenIE _____________________________________________________
    if CoreNLP_SVO_extractor_var==True:
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                            'Started running Stanford CoreNLP OpenIE to extract SVOs at', True,'You can follow CoreNLP in command line.\n\nContrary to the Stanford CoreNLP parser, OpenIE does not display in command line the chuncks of text being currently processed.')
        if isFile:
            subprocess.call(['java', '-jar', '-Xmx'+str(memory_var)+"g", 'Stanford_CoreNLP_OpenIE.jar', '-inputFile', feed_to_svo, '-outputDir', outputDir])
        else:
            if not os.path.exists(outputSVODir):       # Is os.path.dirname(outputSVODir) the same as outputSVODir?
                try:
                    os.makedirs(outputSVODir)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            subprocess.call(
                ['java', '-jar', '-Xmx' + str(memory_var) + "g", 'Stanford_CoreNLP_OpenIE.jar', '-inputDir',
                 feed_to_svo, '-outputDir', outputSVODir])
        IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis end',
                            'Finished running Stanford CoreNLP OpenIE to extract SVOs at', True)
        toProcess_list = []

        field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'PERSON', 'TIME', 'TIME_STAMP', 'Sentence']
        if isFile & Coref:
            toProcess_list.append(os.path.join(outputDir, inputFileBase + "-CoRefed-svoResult-woFilter.txt"))
        elif isFile:
            toProcess_list.append(os.path.join(outputDir, inputFileBase + "-svoResult-woFilter.txt"))
        else:
            for tmp in os.listdir(outputSVODir):
                if Coref and "-CoRefed-svoResult-woFilter.txt" in tmp:
                    toProcess_list.append(tmp)
                elif (not Coref) and ("-svoResult-woFilter.txt" in tmp) and ("-CoRefed" not in tmp):
                    toProcess_list.append(tmp)
        original_toProcess = {}
        if isFile: # input is a file (including merged directory)
            original_toProcess[toProcess_list[0]] = inputFilename
        else: # input is a directory
            for tmp in os.listdir(outputSVODir):
                if Coref and "-CoRefed-svoResult-woFilter.txt" in tmp:
                    original_toProcess[tmp] = os.path.join(inputDir, tmp.replace("-CoRefed-svoResult-woFilter", ""))
                elif (not Coref) and ("-svoResult-woFilter.txt" in tmp) and ("-CoRefed" not in tmp):
                    original_toProcess[tmp] = os.path.join(inputDir, tmp.replace("-svoResult-woFilter", ""))

        if merge_file_option == False:
            # create a single merged file
            svo_merge_filename = os.path.join(outputSVODir, inputDirBase + "-merge-svo.csv")
            result = IO_files_util.openCSVFile(svo_merge_filename, 'w')
            if result == '':
                return
            svo_merge_writer = csv.DictWriter(result, fieldnames=field_names)
            svo_merge_writer.writeheader()
            result.close()
            filesToOpen.append(svo_merge_filename)
            svo_result_list.append(svo_merge_filename)

        SVOerror=0
        for proc_file in toProcess_list:
            # check if svo file is empty
            if isFile:
                outputSVODir = outputDir
            if not os.path.exists(os.path.join(outputSVODir, proc_file)):
                error_msg = "Stanford OpenIE throws an error while processing your document: " + original_toProcess[proc_file] + \
                            "\n\nPlease refer to command line prompt (or terminal) for more details. Most likely, your laptop runs out of memory."
                if merge_file_option:
                    error_msg += "\n\nYou have chosen merge file option to process the directory. You can try not using merge file option."
                mb.showwarning("Stanford OpenIE error", error_msg)
                continue

            f = open(os.path.join(outputSVODir, proc_file), "r",encoding='utf-8',errors='ignore')
            svo_wofilter = f.read()
            f.close()
            if svo_wofilter == "":
                SVOerror=SVOerror+1
                print("\nSVO error while extracting SVOs from " +str(proc_file))

            # Filter SVO _____________________________________________________

            # process filter list
            subject_list = []
            if subjects_dict_var != '':
                f = open(subjects_dict_var, 'r', encoding='utf-8-sig', errors='ignore')
                subject_list = f.read().split('\n')

            verb_list = []
            if verbs_dict_var != '':
                f = open(verbs_dict_var, 'r', encoding='utf-8-sig', errors='ignore')
                verb_list = f.read().split('\n')

            object_list = []
            if objects_dict_var != '':
                f = open(objects_dict_var, 'r', encoding='utf-8-sig', errors='ignore')
                object_list = f.read().split('\n')


            fileHandler = open(os.path.join(outputSVODir, proc_file),encoding='utf-8',errors='ignore')
            listOfLines = fileHandler.readlines()
            fileHandler.close()
            svo_triplets = []
            for line in listOfLines:
                spl = line.split("|")
                # RF why 9??? this excludes wife gave glance
                if len(spl) != 9:
                    continue
                spl[0] = int(spl[0])
                svo_triplets.append(spl)
            svo_triplets = sorted(svo_triplets)

            baseName = os.path.basename(proc_file)
            last_index = baseName.rindex("-")
            baseName = baseName[0:last_index]
            second_last_index = baseName.rindex("-")
            baseName = baseName[0:second_last_index]
            SVOfilename = os.path.join(outputSVODir, baseName + "-svo.csv")


            extract_svo(svo_triplets, SVOfilename, svo_merge_filename, subject_list, verb_list, object_list, field_names, document_index, original_toProcess[proc_file])
            result = IO_files_util.openCSVFile(SVOfilename, 'a')
            if merge_file_option == False:
                result_merge = IO_files_util.openCSVFile(svo_merge_filename, 'a')
                svo_merge_writer = csv.DictWriter(result_merge, fieldnames=field_names)
            if result != '':  # permission error for result = ''
                svo_writer = csv.DictWriter(result, fieldnames=field_names)
                for svo in notSure:
                    if " " in svo[4]:
                        location_list = svo[4].split(" ")
                        for each_location in location_list:
                            svo_writer.writerow(
                                {'Document ID': str(document_index), 'Sentence ID': str(svo[0]), 'Document': IO_csv_util.dressFilenameForCSVHyperlink(original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                 'TIME': svo[3], 'LOCATION': each_location, 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                 field_names[10]: svo[7]})
                            if merge_file_option == False:
                                svo_merge_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]), 'Document': IO_csv_util.dressFilenameForCSVHyperlink(original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                 'TIME': svo[3], 'LOCATION': each_location, 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                 field_names[10]: svo[7]})
                    else:
                        svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),'Document': IO_csv_util.dressFilenameForCSVHyperlink(original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                             'TIME': svo[3], 'LOCATION': svo[4], 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                             field_names[10]: svo[7]})
                        if merge_file_option == False:
                            svo_merge_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),'Document': IO_csv_util.dressFilenameForCSVHyperlink(original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                             'TIME': svo[3], 'LOCATION': svo[4], 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                             field_names[10]: svo[7]})
                result.close()
                if merge_file_option == False:
                    result_merge.close()

            document_index += 1
            if merge_file_option == False:
                if not save_intermediate_file:
                    # delete svofilename
                    os.remove(SVOfilename)
                else:
                    svo_result_list.append(SVOfilename)
                continue
            svo_result_list.append(SVOfilename)
            filesToOpen.append(SVOfilename)

        if SVOerror>0:
            print("\n\nErrors were encountered in extracting SVOs from " + str(SVOerror) + " files out of "+str(len(toProcess_list)) +" files processed.")
            mb.showwarning("SVO extraction error", "Errors were encountered in extracting SVOs from " + str(SVOerror) + " files out of " +str(len(toProcess_list))+" files processed.\n\nPlease, check the command line to see the files.")

        # delete intermediate txt svo files produced by java
        if not merge_file_option:
            svo_result_dir = os.path.join(outputDir, "SVO_Result")
            if os.path.exists(svo_result_dir):
                txt_files = [os.path.join(svo_result_dir, f) for f in os.listdir(svo_result_dir) if f.endswith('.txt')]
                for f in txt_files:
                    os.remove(f)

    # you can visualize data using an svo.csv file in input
    if (inputFilename[-8:] == '-svo.csv') or (len(svo_result_list) > 0):
        # Gephi network graphs _________________________________________________
        if gephi_var == True:
            IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                                'Started running Gephi network graphs at', True)

            if isFile:
                if inputFilename[-4:] == ".csv":
                    gexf_file = Gephi_util.create_gexf(inputFileBase, outputDir, inputFilename)
                else:
                    gexf_file = Gephi_util.create_gexf(inputFileBase, outputDir, svo_result_list[0])
                filesToOpen.append(gexf_file)
            else:
                for f in svo_result_list:
                    gexf_file = Gephi_util.create_gexf(os.path.basename(f)[:-4], outputDir, f)
                    if "-merge-svo" in f or "SENNA_SVO" in f:
                        filesToOpen.append(gexf_file)
                    if not save_intermediate_file:
                        gexf_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if f.endswith('.gexf')]
                        for f in gexf_files:
                            if "-merge-svo" not in f and "SENNA_SVO" not in f:
                                os.remove(f)

        # wordcloud  _________________________________________________
        if wordcloud_var == True:
            IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                                'Started running Wordclouds at', True)
            if inputFilename[-4:] == ".csv":
                myfile = IO_files_util.openCSVFile(inputFilename, 'r')
                currenttext, color_to_words = wordclouds_util.processColorList("", defaultdict(list),
                                                                               ['S', '(255, 0, 0)', '|', 'V',
                                                                                '(0, 0, 255)', '|', 'O/A',
                                                                                '(0, 128, 0)', '|'], myfile)
                out_file = wordclouds_util.display_wordCloud_sep_color(inputFilename, outputDir, currenttext,
                                                                       color_to_words, "")
                myfile.close()
                filesToOpen.append(out_file)
            else:
                for f in svo_result_list:
                    myfile = IO_files_util.openCSVFile(f, "r")
                    currenttext, color_to_words = wordclouds_util.processColorList("", defaultdict(list),
                                                                                   ['S', '(255, 0, 0)', '|', 'V',
                                                                                    '(0, 0, 255)', '|', 'O/A',
                                                                                    '(0, 128, 0)', '|'], myfile)
                    out_file = wordclouds_util.display_wordCloud_sep_color(f, outputDir, currenttext, color_to_words,
                                                                           "")
                    myfile.close()
                    if "-merge-svo" in f or "SENNA_SVO" in f:
                        filesToOpen.append(out_file)
                    if not merge_file_option and not save_intermediate_file:
                        png_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if f.endswith('.png')]
                        for f in png_files:
                            if "-merge-svo" not in f and "SENNA_SVO" not in f:
                                os.remove(f)
        # GIS maps _____________________________________________________

        if google_earth_var == True:
            out_file = ''
            kmloutputFilename = ''
            if (inputFilename[-4:] == ".csv") or (len(svo_result_list) > 0):
                # out_file is a list []
                #   containing several csv files of geocoded locations and non geocoded locations
                # kmloutputFilename is a string; empty when the kml file fails to be created

                IO_user_interface_util.timed_alert(GUI_util.window, 7000, 'Analysis start',
                                                   'Started running Geocoding at', True)

            for f in svo_result_list:
                # out_file is a list []
                #   containing several csv files of geocoded locations and non geocoded locations
                # kmloutputFilename is a string; empty when the kml file fails to be created

                out_file, kmloutputFilename = GIS_pipeline_util.GIS_pipeline(GUI_util.window, f,
                                                                                outputDir,
                                                                                'Nominatim', 'Google Earth Pro',
                                                                                True, False,
                                                                                "south, north, west, east, los, new, san, las, la, hong",
                                                                                "city, island",
                                                                                False, False,
                                                                                0, 6,
                                                                                "LOCATION",
                                                                                'utf-8',
                                                                                1, 1, 1, [1], [1],
                                                                                'LOCATION',
                                                                                0, [''], [''],
                                                                                ['Pushpins'], ['red'],
                                                                                [0], ['1'], [0], [''],
                                                                                [1], ['Sentence'])

            if len(out_file) > 0:
                # since out_file produced by KML is a list cannot use append
                filesToOpen=filesToOpen+out_file
            if len(kmloutputFilename)>0:
                filesToOpen.append(kmloutputFilename)

        if openOutputFiles == True and len(filesToOpen) > 0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
            # if google_earth_var == True:
            #     if kmloutputFilename != '':
            #         IO_files_util.open_kmlFile(kmloutputFilename)

        if len(inputDir) > 1: # when processing a directory, the output changes
            mb.showwarning("Output directory", "All output files have been saved to a subdirectory of the selected output directory at\n\n"+str(outputDir)+"\n\nThe IO widget 'Select OUTPUT files directory' has been updated to reflect the change.")
            GUI_util.output_dir_path.set(outputDir)

#the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                utf8_var.get(),
                                ASCII_var.get(),
                                CoRef_var.get(),
                                CoRef_menu_var.get(),
                                memory_var.get(),
                                manual_Coref_var.get(),
                                date_extractor_var.get(),
                                CoreNLP_SVO_extractor_var.get(),
                                SENNA_SVO_extractor_var.get(),
                                subjects_dict_var.get(),
                                verbs_dict_var.get(),
                                objects_dict_var.get(),
                                gephi_var.get(),
                                wordcloud_var.get(),
                                google_earth_var.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_Excel_chart_output_checkbox.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1300x630'
GUI_label='Graphical User Interface (GUI) for Subject-Verb-Object (SVO) Extraction & Visualization'
config_filename='SVO-config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir 0 no dir 1 dir
#   input secondary dir 0 no dir 1 dir
#   output file 0 no file 1 file
#   output dir 0 no dir 1 dir
config_option=[0,6,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# location of this src python file
scriptPath = GUI_IO_util.scriptPath
#one folder UP, the NLP folder
NLPPath=GUI_IO_util.NLPPath
#subdirectory of script directory where config files are saved
# libPath = GUI_IO_util.libPath +os.sep+'wordLists'

# GUI CHANGES add following lines to every special GUI
# +3 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename)

def clear(e):
    subjects_var.set(0)
    verbs_var.set(0)
    objects_var.set(0)
    subjects_dict_var.set('')
    verbs_dict_var.set('')
    objects_dict_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

utf8_var=tk.IntVar()
ASCII_var=tk.IntVar()
CoRef_var=tk.IntVar()
CoRef_menu_var=tk.StringVar()
memory_var=tk.StringVar()
manual_Coref_var=tk.IntVar()
date_extractor_var=tk.IntVar()
CoreNLP_SVO_extractor_var=tk.IntVar()
SENNA_SVO_extractor_var=tk.IntVar()
subjects_var=tk.IntVar()
objects_var=tk.IntVar()
verbs_var=tk.IntVar()
subjects_dict_var=tk.StringVar()
verbs_dict_var=tk.StringVar()
objects_dict_var=tk.StringVar()
gephi_var=tk.IntVar()
wordcloud_var=tk.IntVar()
google_earth_var=tk.IntVar()

utf8_var.set(0)
utf8_checkbox = tk.Checkbutton(window, text='Check input corpus for utf-8 encoding ', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,utf8_checkbox,True)

ASCII_var.set(0)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,ASCII_checkbox)

CoRef_var.set(0)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP)', variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,CoRef_checkbox,True)

CoRef_menu_var.set("Neural Network")
CoRef_menu = tk.OptionMenu(window,CoRef_menu_var,'Deterministic','Statistical','Neural Network')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,CoRef_menu,True)

#memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700,y_multiplier_integer,memory_var_lb,True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+770,y_multiplier_integer,memory_var)

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,manual_Coref_checkbox)

def activateCoRefOptions(*args):
    if CoRef_var.get()==1:
        CoRef_menu.configure(state='normal')
        memory_var.configure(state='normal')
        manual_Coref_checkbox.configure(state='normal')
        manual_Coref_var.set(1)
    else:
        CoRef_menu.configure(state='disabled')
        # memory_var.configure(state='disabled')
        manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(0)
CoRef_var.trace('w',activateCoRefOptions)

activateCoRefOptions()

date_extractor_checkbox = tk.Checkbutton(window, text='Extract normalized NER dates (via Stanford CoreNLP)', variable=date_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,date_extractor_checkbox)

CoreNLP_SVO_extractor_var.set(1)
SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs (via Stanford CoreNLP OpenIE)', variable=CoreNLP_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SVO_extractor_checkbox,True)

SENNA_SVO_extractor_var.set(1)
SENNA_SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs & SVs (via SENNA)', variable=SENNA_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,SENNA_SVO_extractor_checkbox)

def activateFilters(*args):
    if CoreNLP_SVO_extractor_var.get()==1:
        subjects_checkbox.configure(state='normal')
        verbs_checkbox.configure(state='normal')
        objects_checkbox.configure(state='normal')
        gephi_var.set(1)
        wordcloud_var.set(1)
        google_earth_var.set(1)
        gephi_checkbox.configure(state='normal')
        wordcloud_checkbox.configure(state='normal')
        google_earth_checkbox.configure(state='normal')
    else:
        SENNA_SVO_extractor_checkbox.configure(state='normal')
        if SENNA_SVO_extractor_var.get()==True:
            subjects_checkbox.configure(state='normal')
            verbs_checkbox.configure(state='normal')
            objects_checkbox.configure(state='disabled')
            gephi_var.set(1)
            wordcloud_var.set(1)
            google_earth_var.set(1)
            gephi_checkbox.configure(state='normal')
            wordcloud_checkbox.configure(state='normal')
            google_earth_checkbox.configure(state='normal')
        else:
            SVO_extractor_checkbox.configure(state='normal')
            subjects_checkbox.configure(state='disabled')
            verbs_checkbox.configure(state='disabled')
            objects_checkbox.configure(state='disabled')
            gephi_var.set(0)
            wordcloud_var.set(0)
            google_earth_var.set(0)
            gephi_checkbox.configure(state='disabled')
            wordcloud_checkbox.configure(state='disabled')
            google_earth_checkbox.configure(state='disabled')
CoreNLP_SVO_extractor_var.trace('w',activateFilters)
SENNA_SVO_extractor_var.trace('w',activateFilters)

def getDictFile(checkbox_var,dict_var,checkbox_value,dictFile):
    filePath = ''
    if checkbox_value==1:
        if dictFile == 'Subject' or dictFile == 'Object':
            filePath = GUI_IO_util.wordLists_libPath + os.sep + 'social-actor-list.csv'
        elif dictFile == 'Verb':
            filePath = GUI_IO_util.wordLists_libPath + os.sep + 'social-action-list.csv'
        initialFolder = GUI_IO_util.wordLists_libPath
        filePath = tk.filedialog.askopenfilename(title='Select INPUT csv ' + dictFile + ' dictionary filter file', initialdir = initialFolder, filetypes = [("csv files", "*.csv")])
        if len(filePath)==0:
            checkbox_var.set(0)
    dict_var.set(filePath)

subjects_var.set(1)
subjects_checkbox = tk.Checkbutton(window, text='Filter Subject', variable=subjects_var, onvalue=1, offvalue=0,command=lambda:getDictFile(subjects_var,subjects_dict_var,subjects_var.get(),'Subject'))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,subjects_checkbox,True)

#setup a button to open Windows Explorer on the subjects file
openInputFile_subjects_button = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, subjects_dict_var.get()))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+140, y_multiplier_integer,openInputFile_subjects_button,True)

verbs_var.set(1)
verbs_checkbox = tk.Checkbutton(window, text='Filter Verb', variable=verbs_var, onvalue=1, offvalue=0,command=lambda:getDictFile(verbs_var,verbs_dict_var,verbs_var.get(),'Verb'))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,verbs_checkbox,True)

#setup a button to open Windows Explorer on the verbs file
openInputFile_verbs_button = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, verbs_dict_var.get()))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+520, y_multiplier_integer,openInputFile_verbs_button,True)

objects_var.set(0)
objects_checkbox = tk.Checkbutton(window, text='Filter Object', variable=objects_var, onvalue=1, offvalue=0,command=lambda:getDictFile(objects_var,objects_dict_var,objects_var.get(),'Object'))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+800,y_multiplier_integer,objects_checkbox,True)

#setup a button to open Windows Explorer on the objects file
openInputFile_objects_button = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, objects_dict_var.get()))
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+930, y_multiplier_integer,openInputFile_objects_button)

subjects_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath,'social-actor-list.csv'))
subjects_dict_entry = tk.Entry(window, width=60,state="disabled",textvariable=subjects_dict_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,subjects_dict_entry,True)

verbs_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath,'social-action-list.csv'))
verbs_dict_entry = tk.Entry(window, width=60,state="disabled",textvariable=verbs_dict_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,verbs_dict_entry,True)

objects_dict_var.set('')
objects_dict_entry = tk.Entry(window, width=60,state="disabled",textvariable=objects_dict_var)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+800,y_multiplier_integer,objects_dict_entry)

gephi_var.set(1)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ', variable=gephi_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,gephi_checkbox,True)

wordcloud_var.set(1)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+400,y_multiplier_integer,wordcloud_checkbox,True)

google_earth_var.set(1)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where in GIS maps (via Google Earth Pro) ', variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+800,y_multiplier_integer,google_earth_checkbox)

TIPS_lookup = {'SVO extraction and visualization':'TIPS_NLP_SVO extraction and visualization.pdf','utf-8 compliance':'TIPS_NLP_Text encoding.pdf','Stanford CoreNLP date extractor':'TIPS_NLP_Stanford CoreNLP date extractor.pdf','Stanford CoreNLP OpenIE':'TIPS_NLP_Stanford CoreNLP OpenIE.pdf','Stanford CoreNLP parser':'TIPS_NLP_Stanford CoreNLP parser.pdf','CoNLL table':"TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",'Stanford CoreNLP coreference resolution':"TIPS_NLP_Stanford CoreNLP coreference resolution.pdf","Google Earth Pro":"TIPS_NLP_Google Earth Pro.pdf","Geocoding":"TIPS_NLP_Geocoding.pdf","Gephi network graphs":"TIPS_NLP_Gephi network graphs.pdf",'Java download install run':'TIPS_NLP_Java download install run.pdf'}
TIPS_options='SVO extraction and visualization','utf-8 compliance','Stanford CoreNLP date extractor','Stanford CoreNLP OpenIE','Stanford CoreNLP parser','CoNLL table','Stanford CoreNLP coreference resolution','Google Earth Pro','Geocoding','Gephi network graphs','Java download install run'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", "Please, select either a txt file to be analyzed and extract SVO triplets from it, or a csv file of previously extracted SVOs if all you want to do is to visualize the previously computed results."+GUI_IO_util.msg_openFile)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", GUI_IO_util.msg_corpusData)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 3, "Help",
                                  "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.\n\nTick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","Please, using the dropdown menu, select the type of Stanford coreference you wish to use for coreference Resolution (Deterministic is fastest but less accurate; Neural Network is slowest but most accurate; recommended!\n\nThe co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nWhile CoreNLP can resolve different coreference types (e.g., nominal, pronominal), the SVO script filters only pronominal types. Pronominal coreference refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'.\n\nPlease, select the memory size Stanford CoreNLP will use to resolve coreference. Default = 6. Lower this value if CoreNLP runs out of resources. Increase the value for larger files.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help","Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","Please, tick the checkbox if you wish to run the Stanford CoreNLP normalized NER date annotator to extract standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\nThis will display time plots of dates, visualizing the WHEN of the 5 Ws of narrative.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help","Please, tick the checkboxes if you wish to run the Stanford CoreNLP OpenIE and/or SENNA to extract SVO triplets or SVO triplets and SV pairs.\n\nSENNA can be downloaded at https://ronan.collobert.com/senna/download.html\n\nContrary to the Stanford CoreNLP parser, OpenIE does not display in command line the chunks of text being currently processed.\n\nIn INPUT OpenIE and/or SENNA can process a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT OpenIE and/or SENNA will produce a csv file of SVO results and, if the appropriate visualization options are selected, a Gephi gexf network file, png word cloud file, and Google Earth Pro kml file.\n\nWHEN PROCESSING A DIRECTORY, ALL OUTPUT FILES WILL BE SAVED IN A SUBDIRECTORY OF THE SELECTED OUTPUT DIRECTORY WITH THE NAME OF THE INPUT DIRECTORY.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help","Please, tick the checkbox to filter all SVO extracted triplets for Subjects, Verbs, and Objects via dictionary filter files.\n\nFor instance, you can filter SVO by social actors and social action. In fact, the file \'social-actor-list.csv\', created via WordNet with keyword person and saved in the \'lib/wordLists\' subfolder, will be automatically loaded as the DEFAULT dictionary file (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly automatically loaded as the DEFAULT dictionary file for verbs.\n\nDictionary filter files can be created via WordNet and saved in the \'lib/wordLists\' subfolder. You can edit that list, adding and deleting entries at any time, using any text editor.\n\nWordNet produces thousands of entries for nouns and verbs. For more limited domains, you way want to pair down the number to a few hundred entries.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help","The three widgets display the currently selected dictionary filter files for Subjects, Verbs, and Objects (Objects share the same file as Subjects and you may wish to change that).\n\nThe filter file social-actor-list, created via WordNet with person as keyword and saved in the \'lib/wordLists\' subfolder, will be automatically set as the DEFAULT filter for subjects (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly set as the DEFAULT dictionary file for verbs.\n\nThe widgets are disabled because you are not allowed to tamper with these values. If you wish to change a selected file, please tick the appropriate checkbox in the line above (e.g., Filter Subject) and you will be prompted to select a new file.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*10,"Help","Please, tick the checkboxes:\n\n  1. to visualize SVO relations in network graphs via Gephi;;\n\n  2. to visualize SVO relations in a wordcloud;\n\n  3. to use the NER location values to extract the WHERE part of the 5 Ws of narrative (Who, What, When, Where, Why); locations will be automatically geocoded (i.e., assigned latitude and longitude values) and visualized as maps via Google Earth Pro. ONLY THE LOCATIONS FOUND IN THE EXTRACTED SVO WILL BE DISPLAYED, NOT ALL THE LOCATIONS PRESENT IN THE TEXT.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*11,"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate()-20,GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This set of Python 3 and Java scripts extract automatically most of the elements of a story grammar and visualize the results in network graphs and GIS maps. A story grammar – basically, the 5Ws + H of modern journalism: Who, What, When, Where, Why, and How – provides the basic building blocks of narrative.\n\nThe set of scripts assembled here for this purpose ranges from testing for utf-8 compliance of the input text, to resolution for pronominal coreference, extraction of normalized NER dates (WHEN), visualized in various Excel charts, extraction, geocoding, and mapping in Google Earth Pro of NER locations.\n\nAt the heart of the SVO approach are two scripts, a java script - SVO_pipeline.jar - that extracts from the text all the OpenIE relations via Stanford CoreNLP and another script based on SENNA. The Java pipeline iterates through each relation, extracts the enhanced dependencies, checking for valid SVO triplets. For passive sentences, the pipeline swaps S and O to transform the triplet into active voice. Thus, the WHO, WHAT (WHOM) are extracted from a text. Each component of the SVO triplet can be filtered via specific dictionaries (e.g., filtering for social actors and social actions, only). The set of SVO triplets are then visualized in dynamic network graphs (via Gephi).\n\nThe WHY and HOW of narrative are still beyond the reach of the current set of SVO scripts.\n\nIn INPUT the scripts expect a txt file to run utf-8 check, coreference resolution, date extraction, and OpenIE. You can also enter a csv file, the output of a previous run with OpenIE/SENNA (_svo.csv/_SVO_Result) marked file) if all you want to do is to visualize results.\n\nIn OUTPUT, the scripts will produce several csv files, a png image file, and a KML file depending upon the options selected."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

def warnUser(*args):
    if GUI_util.input_main_dir_path.get()!='':
        mb.showwarning(title='Warning', message='You have selected to work with a set of txt files in a directory (your corpus).\n\nBeware that SVO extraction is computationally demanding. Furthermore, depending upon the options you choose (manual coreference editing, GIS maps), it may require manual input on each input file processed.\n\nThe option of manual coref editing has been disabled.')
        manual_Coref_var.set(0)
        manual_Coref_checkbox.configure(state='disabled')
GUI_util.input_main_dir_path.trace('w',warnUser)

warnUser()

GUI_util.window.mainloop()