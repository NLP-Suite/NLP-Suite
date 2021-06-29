# Written by Gabriel Wang 2018
##########################################
# Modified by Cynthia Dong (Fall 2019-Spring 2020)
##########################################

import sys

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "SVO extractor",
                                          ['subprocess', 'os', 'tkinter', 'csv']) == False:
    sys.exit(0)

from collections import defaultdict
import os
import SVO_util
import csv
import tkinter as tk
import tkinter.messagebox as mb
import subprocess
# to install stanfordnlp, first install
#   pip3 install torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html
#   pip3 install stanfordnlp
# import stanfordnlp


import GUI_IO_util
import IO_files_util
import IO_user_interface_util
import Gephi_util
import GIS_pipeline_util
import wordclouds_util
import GUI_util
import file_utf8_compliance_util
import file_cleaner_util
import IO_csv_util
import Stanford_CoreNLP_coreference_util as stanford_coref
import Stanford_CoreNLP_annotator_util
import semantic_role_labeling_senna

# RUN section ______________________________________________________________________________________________________________________________________________________


lemmalib = {}
voLib = {}
notSure = set()
added = set()
file_open = []

caps = "([A-HJ-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


# svo_OpenIE_single_file is the individual file when processing a directory;
# svo_OpenIE_merged_file is the merged svo csv file
def extract_OpenIE_svo(svo_triplets, svo_OpenIE_single_file, svo_OpenIE_merged_file, field_names, document_index, Document):
    """
    Extract SVO triplets form a Sentence object.
    """
    global lemmalib
    global notSure
    global added

    result = IO_files_util.openCSVFile(svo_OpenIE_single_file, 'w')
    if not result:
        return
    svo_writer = csv.DictWriter(result, fieldnames=field_names)
    svo_writer.writeheader()
    if svo_OpenIE_merged_file:
        merge_result = IO_files_util.openCSVFile(svo_OpenIE_merged_file, 'a')
        if not merge_result:
            return
        svo_OpenIE_writer = csv.DictWriter(merge_result, fieldnames=field_names)
    for svo in svo_triplets:
        # RF if len(svo[2]) == 0 or len(svo[3]) == 0:
        if not (svo[2] and svo[3] and svo[4]):
            continue
        # check if the triple needs to be included

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
                    svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                         'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'S': svo[2],
                                         'V': svo[3], 'O/A': svo[4],
                                         'TIME': svo[6], 'LOCATION': each_location, 'PERSON': svo[7],
                                         'TIME_STAMP': svo[8], field_names[10]: svo[1]
                                         })
                    if svo_OpenIE_merged_file:
                        svo_OpenIE_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                    'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
                                                    'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                                    'TIME': svo[6], 'LOCATION': each_location, 'PERSON': svo[7],
                                                    'TIME_STAMP': svo[8], field_names[10]: svo[1]
                                                    })
            else:
                svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                     'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'S': svo[2],
                                     'V': svo[3], 'O/A': svo[4],
                                     'TIME': svo[6], 'LOCATION': svo[5], 'PERSON': svo[7], 'TIME_STAMP': svo[8],
                                     field_names[10]: svo[1]
                                     })
                if svo_OpenIE_merged_file:
                    svo_OpenIE_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
                                                'S': svo[2], 'V': svo[3], 'O/A': svo[4],
                                                'TIME': svo[6], 'LOCATION': svo[5], 'PERSON': svo[7],
                                                'TIME_STAMP': svo[8],
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
        openOutputFiles, createExcelCharts):
    # pull the widget names from the GUI since the scripts change the IO values
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()

    outputCorefedDir = ''
    outputSVODir = ''

    filesToOpen = []

    # the merge option refers to merging the txt files into one
    merge_txt_file_option = False

    if utf8_var == False and ASCII_var == False and Coref == False and date_extractor_var == False and CoreNLP_SVO_extractor_var == False and SENNA_SVO_extractor_var == False:
        mb.showwarning(title='No option selected',
                       message="No option has been selected.\n\nPlease, select an option and try again.")
        return

    if inputFilename[-4:] == '.txt':
        if (CoreNLP_SVO_extractor_var == False and SENNA_SVO_extractor_var == False) and (
                gephi_var == True or wordcloud_var == True or google_earth_var == True):
            mb.showerror(title='Inputfile/option error',
                         message="The data visualization option(s) you have selected require either an _svo.csv/_SVO_Result file in input or CoreNLP OpenIE and/or SENNA selected.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return
    elif inputFilename[-4:] == '.csv':
        if not 'SVO_' in inputFilename:
            mb.showerror(title='Inputfile error',
                         message="The selected input is a csv file, but... not an _svo.csv file.\n\nPlease, select an _svo.csv file (or a txt file) and try again.")
            return
        if (
                utf8_var == True or Coref == True or Coref_Option == True or memory_var == True or Manual_Coref_var == True or date_extractor_var == True or CoreNLP_SVO_extractor_var == True):
            mb.showerror(title='Inputfile/option error',
                         message="The data analysis option(s) you have selected require in input a txt file, rather than a csv file.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return

    errorFound, error_code, system_output = IO_libraries_util.check_java_installation('SVO extractor')
    if errorFound:
        return

    Coref_Option = Coref_Option.lower()

    if utf8_var:
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Started running utf8 compliance test at', True)
        file_utf8_compliance_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,
                                                        openOutputFiles)

    if ASCII_var:
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Started running characters conversion at', True)
        file_cleaner_util.convert_quotes(GUI_util.window, inputFilename, inputDir)

    isFile = True
    inputFileBase = ""
    inputDirBase = ""
    inputBaseList = []
    svo_result_list = []
    document_index = 1
    svo_OpenIE_merged_file = ""
    svo_SENNA_file = ''
    svo_OpenIE_single_file = ''

    if len(inputFilename) > 0:
        isFile = True
        save_intermediate_file = False
    else:  # directory input
        save_intermediate_file = False
        isFile = False

    # CoRef _____________________________________________________

    # field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'PERSON', 'TIME', 'TIME_STAMP', 'Sentence']

    if Coref:
        # field_names[10] = "Corefed Sentence"
        # ANY CHANGES IN THE COREREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING IN SVO
        # THE SUBSCRIPT _coref_ IS CHECKED BELOW
        if isFile:
            inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
            outputCorefedDir = os.path.join(outputDir, "coref_" + inputFileBase)  # + "_CoRefed_files")
            # change input for all scripts - OpenIE, SENNA, Gephi, wordclouds, Google Earth
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDirBase = os.path.basename(inputDir)
            outputCorefedDir = os.path.join(outputDir, "coref_Dir_" + inputDirBase)

        if not IO_files_util.make_directory(outputCorefedDir):
            return

        # inputFilename and inputDir are the original txt files to be coreferenced
        file_open = stanford_coref.run(inputFilename, inputDir, outputCorefedDir,
                                       openOutputFiles, createExcelCharts,
                                       memory_var, Coref_Option,
                                       Manual_Coref_var)
        if file_open is None:
            return

        if isFile:
            inputFilename = str(file_open[0])  # os.path.join(outputDir, inputFileBase + "-CoRefed.txt")
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDir = outputCorefedDir

        # file_open[0] contains the coreferenced txt file
        # file_open[1] contains the csv file of running time

        if len(file_open) > 0:
            filesToOpen.extend(file_open[0])

            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Stanford CoreNLP Co-Reference Resolution',
                                               'Finished running Stanford CoreNLP Co-Reference Resolution using the ' + Coref_Option + ' approach at',
                                               True)

    # Date extractor _____________________________________________________

    if date_extractor_var:
        files = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, inputDir, outputDir,
                                                                 openOutputFiles, createExcelCharts,
                                                                 'normalized-date', False, memory_var)
        filesToOpen.extend(files)

    if SENNA_SVO_extractor_var or CoreNLP_SVO_extractor_var:
        if isFile:
            inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
            # remove NLP_CoreNLP_ from filename (could have been added to filename in case of coref)
            # the replace will be ignored when there is no NLP_CoreNLP_ in the filename
            inputFileBase = inputFileBase.replace("NLP_CoreNLP_", "")
            outputSVODir = os.path.join(outputDir, "SVO_" + inputFileBase)
        else:
            inputDirBase = os.path.basename(inputDir)
            outputSVODir = os.path.join(outputDir, "SVO_Dir_" + inputDirBase)

        outputDir = outputSVODir
        if not IO_files_util.make_directory(outputSVODir):
            return

    # SENNA _____________________________________________________
    if SENNA_SVO_extractor_var:
        # TODO must filter SVO results by social actors if the user selected that option
        #   both options run correctly for OpenIE
        svo_SENNA_files = []
        svo_SENNA_file = semantic_role_labeling_senna.run_senna(inputFilename, inputDir, outputDir, openOutputFiles,
                                                                createExcelCharts=True)

        svo_SENNA_file = svo_SENNA_file[0]

        if save_intermediate_file:
            for file in IO_files_util.getFileList(inputFile=inputFilename, inputDir=inputDir, fileType='.txt'):
                svo_SENNA_files += semantic_role_labeling_senna.run_senna(inputFilename=file, inputDir='',
                                                                          outputDir=os.path.join(outputDir,
                                                                                                 outputSVODir),
                                                                          openOutputFiles=openOutputFiles,
                                                                          createExcelCharts=createExcelCharts)
        else:
            svo_SENNA_files = [svo_SENNA_file]

        # Filtering SVO
        if subjects_dict_var or verbs_dict_var or objects_dict_var:
            for file in svo_SENNA_files:
                SVO_util.filter_svo(file, subjects_dict_var, verbs_dict_var, objects_dict_var)
        filesToOpen.extend(svo_SENNA_files)

        for file in svo_SENNA_files:
            svo_result_list.append(file)

    # CoreNLP OpenIE _____________________________________________________
    if CoreNLP_SVO_extractor_var:


        answer=mb.askyesno("OpenIE script","Do you want to use the\n   Python version of OpenIE (YES) (still under development)\n   Java version of OpenIE (NO)")
        if answer ==True:
            if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_annotator_util.py') == False:
                return

            IO_user_interface_util.script_under_development('Stanford CoreNLP OpenIE')

            tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, inputDir,
                                                                           outputDir, openOutputFiles,
                                                                           createExcelCharts,
                                                                           'openIE', False,
                                                                           memory_var,
                                                                           extract_date_from_filename_var=False,
                                                                           date_format='',
                                                                           date_separator_var='',
                                                                           date_position_var=0)
            if len(tempOutputFiles)>0:
                filesToOpen.extend(tempOutputFiles)

        else:

            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                               'Started running Stanford CoreNLP OpenIE to extract SVOs at', True,
                                               'Contrary to the Stanford CoreNLP parser, OpenIE does not display in command line the chuncks of text being currently processed.')
            # Calling the source OpenIE file
            if isFile:
                subprocess.call(
                    ['java', '-jar', '-Xmx' + str(memory_var) + "g", 'Stanford_CoreNLP_OpenIE.jar', '-inputFile',
                     inputFilename, '-outputDir', outputDir])
            else:
                subprocess.call(
                    ['java', '-jar', '-Xmx' + str(memory_var) + "g", 'Stanford_CoreNLP_OpenIE.jar', '-inputDir',
                     inputDir, '-outputDir', outputDir])
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                               'Finished running Stanford CoreNLP OpenIE to extract SVOs at', True)

            # Adding output files to toProcess_list
            # process the txt files created by the OpenIE Java script to create a csv output file
            toProcess_list = []
            field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O/A', 'LOCATION', 'PERSON', 'TIME',
                           'TIME_STAMP', 'Sentence']
            if isFile & Coref:
                # ANY CHANGES IN THE COREREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING BELOW
                # NLP_CoreNLP_coref_The Three Little Pigs-svoResult-woFilter.txt
                # inputFileBase contains _coref
                # fName is the filename returned by Java SVO -svoResult-woFilter.txt files will be removed below
                fName = os.path.join(outputDir, "NLP_CoreNLP_" + inputFileBase + "-svoResult-woFilter.txt")
                toProcess_list.append(fName)
            elif isFile:
                # fName is the filename returned by Java SVO The Three Little Pigs SHORT-svoResult-woFilter.txt
                fName = os.path.join(outputDir, inputFileBase + "-svoResult-woFilter.txt")
                toProcess_list.append(fName)
            else:
                for tmp in os.listdir(outputSVODir):
                    # ANY CHANGES IN THE COREREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING BELOW
                    # THE SUBSCRIPT _coref_ IS CHECKED BELOW
                    if Coref and "-svoResult-woFilter.txt" in tmp:
                        toProcess_list.append(tmp)
                    elif (not Coref) and ("-svoResult-woFilter.txt" in tmp) and ("-coref" not in tmp):
                        toProcess_list.append(tmp)

            original_toProcess = {}
            if isFile:  # input is a file (including merged directory)
                original_toProcess[toProcess_list[0]] = inputFilename
                # svo_OpenIE_merged_file=''
                svo_OpenIE_merged_file = os.path.join(outputSVODir, "NLP_OpenIE_SVO_" + inputFileBase + ".csv")
            else:  # input is a directory
                for tmp in os.listdir(outputSVODir):
                    # ANY CHANGES IN THE COREREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING BELOW
                    # THE SUBSCRIPT _coref_ IS CHECKED BELOW
                    # "-svoResult-woFilter.txt"  is the filename produced by JAVA
                    # original_toProcess is the txt files in the original inputDir
                    if Coref and "-svoResult-woFilter.txt" in tmp:
                        original_toProcess[tmp] = os.path.join(inputDir, tmp.replace("-svoResult-woFilter", ""))
                    elif (not Coref) and ("-svoResult-woFilter.txt" in tmp) and ("-coref" not in tmp):
                        original_toProcess[tmp] = os.path.join(inputDir, tmp.replace("-svoResult-woFilter", ""))
                svo_OpenIE_merged_file = os.path.join(outputSVODir, "NLP_OpenIE_SVO_Dir_" + inputDirBase + ".csv")

            # when not merging a text file that will be processed as a unique file
            #   the single svo csv files should always be merged together in a single file
            #   currently, a merged csv file is the only option; no reason to produce potentially thousands of files
            if not merge_txt_file_option:
                result = IO_files_util.openCSVFile(svo_OpenIE_merged_file, 'w')
                if result == '':
                    return
                svo_OpenIE_writer = csv.DictWriter(result, fieldnames=field_names)
                svo_OpenIE_writer.writeheader()
                result.close()
                filesToOpen.append(svo_OpenIE_merged_file)
                svo_result_list.append(svo_OpenIE_merged_file)

            SVOerror = 0
            for proc_file in toProcess_list:
                # proc_file is the current -svoResult-woFilter produced by the Java OpenIE
                # check if svo file is empty
                # proc_file does not have path when processing an inputDir
                if not os.path.exists(os.path.join(outputSVODir, proc_file)):
                    error_msg = "Stanford CoreNLP OpenIE has failed to process your document: " + original_toProcess[
                        proc_file] + \
                                "\n\nPlease refer to command line prompt (or terminal) for more details. Most likely, your laptop runs out of memory."
                    if merge_txt_file_option:
                        error_msg += "\n\nYou have chosen merge file option to process the directory. You can try not using merge file option."
                    mb.showwarning("Stanford OpenIE error", error_msg)
                    continue

                f = open(os.path.join(outputSVODir, proc_file), "r", encoding='utf-8', errors='ignore')
                svo_wofilter = f.read()
                f.close()
                if svo_wofilter == "":
                    SVOerror = SVOerror + 1
                    print("\nOpenIE SVO error (empty SVO output file) while extracting SVOs from " + str(proc_file))

                fileHandler = open(os.path.join(outputSVODir, proc_file), encoding='utf-8', errors='ignore')
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
                # remove NLP_CoreNLP_ from filename, added to filename in case of coref
                baseName = baseName.replace("NLP_CoreNLP_", "")
                svo_OpenIE_single_file = os.path.join(outputSVODir, "NLP_OpenIE_SVO_temp_" + baseName + ".csv")

                extract_OpenIE_svo(svo_triplets, svo_OpenIE_single_file, svo_OpenIE_merged_file, field_names, document_index, original_toProcess[proc_file])

                # Filter SVO
                if subjects_dict_var or verbs_dict_var or objects_dict_var:
                    SVO_util.filter_svo(svo_OpenIE_single_file, subjects_dict_var, verbs_dict_var, objects_dict_var)
                    if svo_OpenIE_merged_file:
                        SVO_util.filter_svo(svo_OpenIE_merged_file, subjects_dict_var, verbs_dict_var, objects_dict_var)

                result = IO_files_util.openCSVFile(svo_OpenIE_single_file, 'a')
                if not merge_txt_file_option:
                    result_merge = IO_files_util.openCSVFile(svo_OpenIE_merged_file, 'a')
                    svo_OpenIE_writer = csv.DictWriter(result_merge, fieldnames=field_names)
                if result != '':  # permission error for result = ''
                    svo_writer = csv.DictWriter(result, fieldnames=field_names)
                    for svo in notSure:
                        if " " in svo[4]:
                            location_list = svo[4].split(" ")
                            for each_location in location_list:
                                svo_writer.writerow(
                                    {'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                     'Document': IO_csv_util.dressFilenameForCSVHyperlink(original_toProcess[proc_file]),
                                     'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                     'TIME': svo[3], 'LOCATION': each_location, 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                     field_names[10]: svo[7]})
                                if not merge_txt_file_option:
                                    svo_OpenIE_writer.writerow(
                                        {'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                         'Document': IO_csv_util.dressFilenameForCSVHyperlink(
                                             original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1], 'O/A': svo[2],
                                         'TIME': svo[3], 'LOCATION': each_location, 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                         field_names[10]: svo[7]})
                        else:
                            svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                 'Document': IO_csv_util.dressFilenameForCSVHyperlink(
                                                     original_toProcess[proc_file]), 'S': "Someone?", 'V': svo[1],
                                                 'O/A': svo[2],
                                                 'TIME': svo[3], 'LOCATION': svo[4], 'PERSON': svo[5], 'TIME_STAMP': svo[6],
                                                 field_names[10]: svo[7]})
                            if not merge_txt_file_option:
                                svo_OpenIE_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                            'Document': IO_csv_util.dressFilenameForCSVHyperlink(
                                                                original_toProcess[proc_file]), 'S': "Someone?",
                                                            'V': svo[1], 'O/A': svo[2],
                                                            'TIME': svo[3], 'LOCATION': svo[4], 'PERSON': svo[5],
                                                            'TIME_STAMP': svo[6],
                                                            field_names[10]: svo[7]})
                    result.close()
                    if not merge_txt_file_option:
                        result_merge.close()
                document_index += 1
                if not merge_txt_file_option:
                    if not save_intermediate_file:  # set to false when processing a directory
                        # delete intermediate individual svofilename
                        os.remove(svo_OpenIE_single_file)
                    else:
                        if not isFile:
                            # do not append the single file and merged file when processing a txt file in input, since they will both have the same name
                            svo_result_list.append(svo_OpenIE_single_file)
                    continue
                else:
                    svo_result_list.append(svo_OpenIE_single_file)
                # do not append the single file and merged file when processing a txt file in input, since they will both have the same name
                # if not isFile:
                #     filesToOpen.append(svo_OpenIE_single_file)
                #     inputFilename = svo_OpenIE_single_file

            if SVOerror > 0:
                print("\n\nErrors were encountered in extracting SVOs from " + str(SVOerror) + " files out of " + str(
                    len(toProcess_list)) + " files processed.")
                mb.showwarning("SVO extraction error",
                               "Errors were encountered in extracting SVOs from " + str(SVOerror) + " files out of " + str(
                                   len(
                                       toProcess_list)) + " files processed.\n\nPlease, check the command line to see the files.")

            # delete intermediate -svoResult-woFilter.txt files produced by java
            if not merge_txt_file_option:
                if os.path.exists(outputSVODir):
                    txt_files = [os.path.join(outputSVODir, f) for f in os.listdir(outputSVODir) if
                                 f.endswith('-svoResult-woFilter.txt')]
                    # txt_files contain the temporary -svoResult-woFilter files with | generated by th Java script
                    #   no reason to keep them
                    for f in txt_files:
                        os.remove(f)

    # next lines create summaries of comparative results from CoreNLP and SENNA
    if SENNA_SVO_extractor_var and CoreNLP_SVO_extractor_var:
        if svo_OpenIE_merged_file and svo_SENNA_file:
            # the current SVO always produces a merged csv output file
            # OpenIe_file = svo_OpenIE_single_file if isFile else svo_OpenIE_merged_file
            OpenIe_file = svo_OpenIE_merged_file
            freq_csv = SVO_util.count_frequency_two_svo(OpenIe_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
            combined_csv = SVO_util.combine_two_svo(OpenIe_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
            filesToOpen.extend(freq_csv)
            filesToOpen.append(combined_csv)

    # you can visualize data using an svo.csv file in input --------------------------------------------------

    # the SVO script can take in input a csv SVO file previously computed: inputFilename
    # results currently produced are in svo_result_list
    if ('SVO_' in inputFilename) or (len(svo_result_list) > 0):

        # Gephi network graphs _________________________________________________
        if gephi_var:
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                               'Started running Gephi network graphs at', True)
            # previous svo csv files can be entered in input to display networks, wordclouds or GIS maps
            if inputFilename[-4:] == ".csv":
                if IO_csv_util.GetNumberOfRecordInCSVFile(inputFilename) > 1:  # including headers; file is empty
                    gexf_file = Gephi_util.create_gexf(inputFileBase, outputDir, inputFilename)
                    filesToOpen.append(gexf_file)
                else:
                    if IO_csv_util.GetNumberOfRecordInCSVFile(
                            svo_result_list[0]) > 1:  # including headers; file is empty
                        gexf_file = Gephi_util.create_gexf(inputFileBase, outputDir, svo_result_list[0])
                        filesToOpen.append(gexf_file)
            else:  # txt input file
                for f in svo_result_list:
                    if IO_csv_util.GetNumberOfRecordInCSVFile(f) > 1:  # including headers; file is empty
                        gexf_file = Gephi_util.create_gexf(os.path.basename(f)[:-4], outputDir, f)
                        if "OpenIE_SVO" in f or "SENNA_SVO" in f:
                            filesToOpen.append(gexf_file)
                        if not save_intermediate_file:
                            gexf_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if
                                          f.endswith('.gexf')]
                            for f in gexf_files:
                                if "OpenIE_SVO" not in f and "SENNA_SVO" not in f:
                                    os.remove(f)

        # wordcloud  _________________________________________________
        if wordcloud_var:
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                               'Started running Wordclouds at', True)
            if inputFilename[-4:] == ".csv":
                if IO_csv_util.GetNumberOfRecordInCSVFile(inputFilename) > 1:  # including headers; file is empty
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
                    if IO_csv_util.GetNumberOfRecordInCSVFile(f) > 1:  # including headers; file is empty
                        myfile = IO_files_util.openCSVFile(f, "r")
                        currenttext, color_to_words = wordclouds_util.processColorList("", defaultdict(list),
                                                                                       ['S', '(255, 0, 0)', '|', 'V',
                                                                                        '(0, 0, 255)', '|', 'O/A',
                                                                                        '(0, 128, 0)', '|'], myfile)
                        out_file = wordclouds_util.display_wordCloud_sep_color(f, outputDir, currenttext,
                                                                               color_to_words,
                                                                               "",False)
                        myfile.close()
                        if "OpenIE_SVO" in f or "SENNA_SVO" in f:
                            filesToOpen.append(out_file)
                        if not merge_txt_file_option and not save_intermediate_file:
                            png_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if
                                         f.endswith('.png')]
                            for f in png_files:
                                if "OpenIE_SVO" not in f and "SENNA_SVO" not in f:
                                    os.remove(f)
        # GIS maps _____________________________________________________

        # SENNA locations are not really geocodable locations
        if google_earth_var:
            out_file = ''
            kmloutputFilename = ''
            # if (inputFilename[-4:] == ".csv") or (len(svo_result_list) > 0):
                # out_file is a list []
                #   containing several csv files of geocoded locations and non geocoded locations
                # kmloutputFilename is a string; empty when the kml file fails to be created

                # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                #                                    'Started running Geocoding at', True)

            for f in svo_result_list:
                if (not 'SENNA' in f) and IO_csv_util.GetNumberOfRecordInCSVFile(
                        f) > 1:  # including headers; file is empty
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
                        filesToOpen = filesToOpen + out_file
                    if len(kmloutputFilename) > 0:
                        filesToOpen.append(kmloutputFilename)

    if openOutputFiles == True and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        # if google_earth_var == True:
        #     if kmloutputFilename != '':
        #         IO_files_util.open_kmlFile(kmloutputFilename)

    if len(inputDir) > 1 and len(filesToOpen) > 0:  # when processing a directory, the output changes
        # not a good idea to change the IO widget output because if you run the script again without first closing the GUI
        #   the new output dir becomes the new output in an infinite loop
        # mb.showwarning("Output directory", "All output files have been saved to a subdirectory of the selected output directory at\n\n"+str(outputDir)+"\n\nThe IO widget 'Select OUTPUT files directory' has been updated to reflect the change.")
        # GUI_util.output_dir_path.set(outputDir)
        if outputSVODir != '':
            outputFileDir = outputSVODir
        elif outputCorefedDir != '':
            outputFileDir = outputCorefedDir
        mb.showwarning("Output directory",
                       "All output files have been saved to a subdirectory of the selected output directory at\n\n" + str(
                           outputFileDir))


# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
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

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1300
GUI_height=630 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label = 'Graphical User Interface (GUI) for Subject-Verb-Object (SVO) Extraction & Visualization Pipeline'
config_filename = 'SVO-config.txt'
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
config_option = [0, 6, 1, 0, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# location of this src python file
scriptPath = GUI_IO_util.scriptPath
# one folder UP, the NLP folder
NLPPath = GUI_IO_util.NLPPath
# subdirectory of script directory where config files are saved
# libPath = GUI_IO_util.libPath +os.sep+'wordLists'

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options, config_filename,IO_setup_display_brief)


def clear(e):
    subjects_var.set(0)
    verbs_var.set(0)
    objects_var.set(0)
    subjects_dict_var.set('')
    verbs_dict_var.set('')
    objects_dict_var.set('')
    GUI_util.clear("Escape")


window.bind("<Escape>", clear)

utf8_var = tk.IntVar()
ASCII_var = tk.IntVar()
CoRef_var = tk.IntVar()
CoRef_menu_var = tk.StringVar()
memory_var = tk.StringVar()
manual_Coref_var = tk.IntVar()
date_extractor_var = tk.IntVar()
CoreNLP_SVO_extractor_var = tk.IntVar()
SENNA_SVO_extractor_var = tk.IntVar()
subjects_var = tk.IntVar()
objects_var = tk.IntVar()
verbs_var = tk.IntVar()
subjects_dict_var = tk.StringVar()
verbs_dict_var = tk.StringVar()
objects_dict_var = tk.StringVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

utf8_var.set(0)
utf8_checkbox = tk.Checkbutton(window, text='Check input corpus for utf-8 encoding ', variable=utf8_var, onvalue=1,
                               offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               utf8_checkbox, True)

ASCII_var.set(0)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent',
                                variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, ASCII_checkbox)

CoRef_var.set(0)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP)',
                                variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoRef_checkbox, True)

CoRef_menu_var.set("Neural Network")
CoRef_menu = tk.OptionMenu(window, CoRef_menu_var, 'Deterministic', 'Statistical', 'Neural Network')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, CoRef_menu, True)

# memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 700, y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 770, y_multiplier_integer,
                                               memory_var)

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               manual_Coref_checkbox)


def activateCoRefOptions(*args):
    if CoRef_var.get() == 1:
        CoRef_menu.configure(state='normal')
        memory_var.configure(state='normal')
        manual_Coref_checkbox.configure(state='normal')
        # manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(1)
    else:
        CoRef_menu.configure(state='disabled')
        # memory_var.configure(state='disabled')
        manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(0)


CoRef_var.trace('w', activateCoRefOptions)

activateCoRefOptions()

date_extractor_checkbox = tk.Checkbutton(window, text='Extract normalized NER dates (via Stanford CoreNLP)',
                                         variable=date_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               date_extractor_checkbox)

CoreNLP_SVO_extractor_var.set(1)
CoreNLP_SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs (via Stanford CoreNLP OpenIE)',
                                                variable=CoreNLP_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoreNLP_SVO_extractor_checkbox, True)

SENNA_SVO_extractor_var.set(1)
SENNA_SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs & SVs (via SENNA)',
                                              variable=SENNA_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer,
                                               SENNA_SVO_extractor_checkbox)


def activateFilters(*args):
    gephi_var.set(1)
    wordcloud_var.set(1)
    google_earth_var.set(1)
    gephi_checkbox.configure(state='normal')
    wordcloud_checkbox.configure(state='normal')
    google_earth_checkbox.configure(state='normal')
    if CoreNLP_SVO_extractor_var.get() == True or SENNA_SVO_extractor_var.get() == True:
        # SVO_extractor_checkbox.configure(state='normal')
        # SENNA_SVO_extractor_checkbox.configure(state='normal')
        subjects_checkbox.configure(state='normal')
        verbs_checkbox.configure(state='normal')
        objects_checkbox.configure(state='normal')
    if CoreNLP_SVO_extractor_var.get() == True and SENNA_SVO_extractor_var.get() == False:
        # CoreNLP_SVO_extractor_checkbox.configure(state='normal')
        # SENNA_SVO_extractor_checkbox.configure(state='disabled')
        subjects_checkbox.configure(state='normal')
        verbs_checkbox.configure(state='normal')
        objects_checkbox.configure(state='normal')
    if CoreNLP_SVO_extractor_var.get() == False and SENNA_SVO_extractor_var.get() == True:
        # CoreNLP_SVO_extractor_checkbox.configure(state='disabled')
        # SENNA_SVO_extractor_checkbox.configure(state='normal')
        subjects_checkbox.configure(state='normal')
        verbs_checkbox.configure(state='normal')
        objects_checkbox.configure(state='normal')
    if CoreNLP_SVO_extractor_var.get() == False and SENNA_SVO_extractor_var.get() == False:
        CoreNLP_SVO_extractor_checkbox.configure(state='normal')
        SENNA_SVO_extractor_checkbox.configure(state='normal')
        subjects_var.set(0)
        verbs_var.set(0)
        objects_var.set(0)
        subjects_checkbox.configure(state='disabled')
        verbs_checkbox.configure(state='disabled')
        objects_checkbox.configure(state='disabled')
        gephi_var.set(0)
        wordcloud_var.set(0)
        google_earth_var.set(0)
        gephi_checkbox.configure(state='disabled')
        wordcloud_checkbox.configure(state='disabled')
        google_earth_checkbox.configure(state='disabled')


CoreNLP_SVO_extractor_var.trace('w', activateFilters)
SENNA_SVO_extractor_var.trace('w', activateFilters)


def getDictFile(checkbox_var, dict_var, checkbox_value, dictFile):
    filePath = ''
    if checkbox_value == 1:
        if dictFile == 'Subject' or dictFile == 'Object':
            filePath = GUI_IO_util.wordLists_libPath + os.sep + 'social-actor-list.csv'
        elif dictFile == 'Verb':
            filePath = GUI_IO_util.wordLists_libPath + os.sep + 'social-action-list.csv'
        initialFolder = GUI_IO_util.wordLists_libPath
        filePath = tk.filedialog.askopenfilename(title='Select INPUT csv ' + dictFile + ' dictionary filter file',
                                                 initialdir=initialFolder, filetypes=[("csv files", "*.csv")])
        if len(filePath) == 0:
            checkbox_var.set(0)
    dict_var.set(filePath)


subjects_var.set(1)
subjects_checkbox = tk.Checkbutton(window, text='Filter Subject', variable=subjects_var, onvalue=1, offvalue=0,
                                   command=lambda: getDictFile(subjects_var, subjects_dict_var, subjects_var.get(),
                                                               'Subject'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               subjects_checkbox, True)

# setup a button to open Windows Explorer on the subjects file
openInputFile_subjects_button = tk.Button(window, width=3, text='',
                                          command=lambda: IO_files_util.openFile(window, subjects_dict_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 140, y_multiplier_integer,
                                               openInputFile_subjects_button, True)

verbs_var.set(1)
verbs_checkbox = tk.Checkbutton(window, text='Filter Verb', variable=verbs_var, onvalue=1, offvalue=0,
                                command=lambda: getDictFile(verbs_var, verbs_dict_var, verbs_var.get(), 'Verb'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, verbs_checkbox, True)

# setup a button to open Windows Explorer on the verbs file
openInputFile_verbs_button = tk.Button(window, width=3, text='',
                                       command=lambda: IO_files_util.openFile(window, verbs_dict_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 520, y_multiplier_integer,
                                               openInputFile_verbs_button, True)

objects_var.set(0)
objects_checkbox = tk.Checkbutton(window, text='Filter Object', variable=objects_var, onvalue=1, offvalue=0,
                                  command=lambda: getDictFile(objects_var, objects_dict_var, objects_var.get(),
                                                              'Object'))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               objects_checkbox, True)

# setup a button to open Windows Explorer on the objects file
openInputFile_objects_button = tk.Button(window, width=3, text='',
                                         command=lambda: IO_files_util.openFile(window, objects_dict_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 930, y_multiplier_integer,
                                               openInputFile_objects_button)

subjects_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-actor-list.csv'))
subjects_dict_entry = tk.Entry(window, width=60, state="disabled", textvariable=subjects_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               subjects_dict_entry, True)

verbs_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-action-list.csv'))
verbs_dict_entry = tk.Entry(window, width=60, state="disabled", textvariable=verbs_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, verbs_dict_entry, True)

objects_dict_var.set('')
objects_dict_entry = tk.Entry(window, width=60, state="disabled", textvariable=objects_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               objects_dict_entry)

gephi_var.set(1)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ',
                                variable=gephi_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               gephi_checkbox, True)

wordcloud_var.set(1)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, wordcloud_checkbox,
                                               True)

google_earth_var.set(1)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where in GIS maps (via Google Earth Pro) ',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               google_earth_checkbox)

TIPS_lookup = {'SVO extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'Stanford CoreNLP date extractor': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'CoNLL table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'Stanford CoreNLP coreference resolution': "TIPS_NLP_Stanford CoreNLP coreference resolution.pdf",
               "Google Earth Pro": "TIPS_NLP_Google Earth Pro.pdf", "Geocoding": "TIPS_NLP_Geocoding.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf",
               'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'SVO extraction and visualization', 'utf-8 encoding', 'Stanford CoreNLP date extractor', 'Stanford CoreNLP OpenIE', 'Stanford CoreNLP parser', 'CoNLL table', 'Stanford CoreNLP coreference resolution', 'Google Earth Pro', 'Geocoding', 'Gephi network graphs', 'Java download install run'


# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, basic_y_coordinate, y_step):
    if IO_setup_display_brief==False:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      "Please, select either a txt file to be analyzed and extract SVO triplets from it, or a csv file of previously extracted SVOs if all you want to do is to visualize the previously computed results." + GUI_IO_util.msg_openFile)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step, "Help",
                                      GUI_IO_util.msg_corpusData)
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * 2, "Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+1), "Help",
                                  "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.\n\nTick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  "Please, using the dropdown menu, select the type of Stanford coreference you wish to use for coreference Resolution (Deterministic is fastest but less accurate; Neural Network is slowest but most accurate; recommended!\n\nThe co-reference resolution algorithm is a memory hog. You may not have enough memory on your machine.\n\nWhile CoreNLP can resolve different coreference types (e.g., nominal, pronominal), the SVO script filters only pronominal types. Pronominal coreference refers to such cases as 'John said that he would...'; 'he' would be substituted by 'John'.\n\nPlease, select the memory size Stanford CoreNLP will use to resolve coreference. Default = 6. Lower this value if CoreNLP runs out of resources. Increase the value for larger files.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  "Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+4), "Help",
                                  "Please, tick the checkbox if you wish to run the Stanford CoreNLP normalized NER date annotator to extract standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\nThis will display time plots of dates, visualizing the WHEN of the 5 Ws of narrative.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+5), "Help",
                                  "Please, tick the checkboxes if you wish to run the Stanford CoreNLP OpenIE and/or SENNA to extract SVO triplets or SVO triplets and SV pairs.\n\nSENNA can be downloaded at https://ronan.collobert.com/senna/download.html\n\nContrary to the Stanford CoreNLP parser, OpenIE does not display in command line the chunks of text being currently processed.\n\nIn INPUT OpenIE and/or SENNA can process a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT OpenIE and/or SENNA will produce a csv file of SVO results and, if the appropriate visualization options are selected, a Gephi gexf network file, png word cloud file, and Google Earth Pro kml file (GIS maps are not produced when running SVO with SENNA; SENNA, by and large, does not produce geocodable locations.\n\nWHEN PROCESSING A DIRECTORY, ALL OUTPUT FILES WILL BE SAVED IN A SUBDIRECTORY OF THE SELECTED OUTPUT DIRECTORY WITH THE NAME OF THE INPUT DIRECTORY.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
                                  "Please, tick the checkbox to filter all SVO extracted triplets for Subjects, Verbs, and Objects via dictionary filter files.\n\nFor instance, you can filter SVO by social actors and social action. In fact, the file \'social-actor-list.csv\', created via WordNet with keyword person and saved in the \'lib/wordLists\' subfolder, will be automatically loaded as the DEFAULT dictionary file (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly automatically loaded as the DEFAULT dictionary file for verbs.\n\nDictionary filter files can be created via WordNet and saved in the \'lib/wordLists\' subfolder. You can edit that list, adding and deleting entries at any time, using any text editor.\n\nWordNet produces thousands of entries for nouns and verbs. For more limited domains, you way want to pair down the number to a few hundred entries.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+7), "Help",
                                  "The three widgets display the currently selected dictionary filter files for Subjects, Verbs, and Objects (Objects share the same file as Subjects and you may wish to change that).\n\nThe filter file social-actor-list, created via WordNet with person as keyword and saved in the \'lib/wordLists\' subfolder, will be automatically set as the DEFAULT filter for subjects (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly set as the DEFAULT dictionary file for verbs.\n\nThe widgets are disabled because you are not allowed to tamper with these values. If you wish to change a selected file, please tick the appropriate checkbox in the line above (e.g., Filter Subject) and you will be prompted to select a new file.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+8), "Help",
                                  "Please, tick the checkboxes:\n\n  1. to visualize SVO relations in network graphs via Gephi;;\n\n  2. to visualize SVO relations in a wordcloud;\n\n  3. to use the NER location values to extract the WHERE part of the 5 Ws of narrative (Who, What, When, Where, Why); locations will be automatically geocoded (i.e., assigned latitude and longitude values) and visualized as maps via Google Earth Pro. ONLY THE LOCATIONS FOUND IN THE EXTRACTED SVO WILL BE DISPLAYED, NOT ALL THE LOCATIONS PRESENT IN THE TEXT.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+9), "Help",
                                  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This set of Python 3 and Java scripts extract automatically most of the elements of a story grammar and visualize the results in network graphs and GIS maps. A story grammar – basically, the 5Ws + H of modern journalism: Who, What, When, Where, Why, and How – provides the basic building blocks of narrative.\n\nThe set of scripts assembled here for this purpose ranges from testing for utf-8 compliance of the input text, to resolution for pronominal coreference, extraction of normalized NER dates (WHEN), visualized in various Excel charts, extraction, geocoding, and mapping in Google Earth Pro of NER locations.\n\nAt the heart of the SVO approach are two scripts, a java script - SVO_pipeline.jar - that extracts from the text all the OpenIE relations via Stanford CoreNLP and another script based on SENNA. The Java pipeline iterates through each relation, extracts the enhanced dependencies, checking for valid SVO triplets. For passive sentences, the pipeline swaps S and O to transform the triplet into active voice. Thus, the WHO, WHAT (WHOM) are extracted from a text. Each component of the SVO triplet can be filtered via specific dictionaries (e.g., filtering for social actors and social actions, only). The set of SVO triplets are then visualized in dynamic network graphs (via Gephi).\n\nThe WHY and HOW of narrative are still beyond the reach of the current set of SVO scripts.\n\nIn INPUT the scripts expect a txt file to run utf-8 check, coreference resolution, date extraction, and OpenIE. You can also enter a csv file, the output of a previous run with OpenIE/SENNA (_svo.csv/_SVO_Result) marked file) if all you want to do is to visualize results.\n\nIn OUTPUT, the scripts will produce several csv files, a png image file, and a KML file depending upon the options selected."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief)


def warnUser(*args):
    if GUI_util.input_main_dir_path.get() != '':
        mb.showwarning(title='Warning',
                       message='You have selected to work with a set of txt files in a directory (your corpus).\n\nBeware that SVO extraction is computationally demanding. Furthermore, depending upon the options you choose (manual coreference editing, GIS maps), it may require manual input on each input file processed.\n\nDepending upon corpus size, manual coreference editing may also not be possible, due to memory requirements..')
        # manual_Coref_var.set(0)
        # manual_Coref_checkbox.configure(state='disabled')

GUI_util.input_main_dir_path.trace('w', warnUser)

warnUser()

GUI_util.window.mainloop()
