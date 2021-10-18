# Written by Gabriel Wang 2018
# Modified by Cynthia Dong (Fall 2019-Spring 2020)
# Modified by Matthew Chau (Spring 2021)
# Modified by Roberto Franzosi (Spring-Fall 2021)
# Modified by Cynthia Dong (Fall 2021)

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
from subprocess import call

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
import IO_csv_util
import Stanford_CoreNLP_coreference_util
import Stanford_CoreNLP_annotator_util
import semantic_role_labeling_senna
import reminders_util

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


# svo_CoreNLP_single_file is the individual file when processing a directory;
# svo_CoreNLP_merged_file is the merged svo csv file
def extract_CoreNLP_SVO(svo_triplets, svo_CoreNLP_single_file, svo_CoreNLP_merged_file, field_names, document_index, Document):
    """
    Extract SVO triplets form a Sentence object.
    """
    global lemmalib
    global notSure
    global added

    result = IO_files_util.openCSVFile(svo_CoreNLP_single_file, 'w')
    if not result:
        return
    svo_writer = csv.DictWriter(result, fieldnames=field_names)
    svo_writer.writeheader()
    if svo_CoreNLP_merged_file:
        merge_result = IO_files_util.openCSVFile(svo_CoreNLP_merged_file, 'a')
        if not merge_result:
            return
        svo_CoreNLP_writer = csv.DictWriter(merge_result, fieldnames=field_names)
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
                                         'V': svo[3], 'O': svo[4],
                                         'Time': svo[6], 'Location': each_location, 'Person': svo[7],
                                         'Time stamp': svo[8], field_names[10]: svo[1]
                                         })
                    if svo_CoreNLP_merged_file:
                        svo_CoreNLP_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                    'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
                                                    'S': svo[2], 'V': svo[3], 'O': svo[4],
                                                    'Time': svo[6], 'Location': each_location, 'Person': svo[7],
                                                    'Time stamp': svo[8], field_names[10]: svo[1]
                                                    })
            else:
                svo_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                     'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document), 'S': svo[2],
                                     'V': svo[3], 'O': svo[4],
                                     'Time': svo[6], 'Location': svo[5], 'Person': svo[7], 'Time stamp': svo[8],
                                     field_names[10]: svo[1]
                                     })
                if svo_CoreNLP_merged_file:
                    svo_CoreNLP_writer.writerow({'Document ID': str(document_index), 'Sentence ID': str(svo[0]),
                                                'Document': IO_csv_util.dressFilenameForCSVHyperlink(Document),
                                                'S': svo[2], 'V': svo[3], 'O': svo[4],
                                                'Time': svo[6], 'Location': svo[5], 'Person': svo[7],
                                                'Time stamp': svo[8],
                                                field_names[10]: svo[1]
                                                })
            added.add((svo[0], svo[3], svo[4], svo[6], svo[5], svo[7], svo[8], svo[1]))


def run(inputFilename, inputDir, outputDir,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
        Coref,
        Manual_Coref_var,
        date_extractor_var,
        CoreNLP_SVO_extractor_var,
        SENNA_SVO_extractor_var,
        CoreNLP_OpenIE_var,
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

    if Coref == False and date_extractor_var == False and CoreNLP_SVO_extractor_var == False and SENNA_SVO_extractor_var == False and CoreNLP_OpenIE_var == False:
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
                         message="The selected input is a csv file, but... not an _svo.csv file.\n\nPlease, select an _svo.csv file (or txt file(s)) and try again.")
            return
        if (
                utf8_var == True or Coref == True or memory_var == True or Manual_Coref_var == True or date_extractor_var == True or CoreNLP_SVO_extractor_var == True):
            mb.showerror(title='Inputfile/option error',
                         message="The data analysis option(s) you have selected require in input a txt file, rather than a csv file.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return

    # Coref_Option = Coref_Option.lower()

    isFile = True
    inputFileBase = ""
    inputDirBase = ""
    inputBaseList = []
    svo_result_list = []
    document_index = 1
    svo_CoreNLP_merged_file = ""
    svo_SENNA_file = ''
    svo_CoreNLP_single_file = ''

    if len(inputFilename) > 0:
        isFile = True
        save_intermediate_file = False
    else:  # directory input
        save_intermediate_file = False
        isFile = False

    # CoRef _____________________________________________________

    # field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O', 'LOCATION', 'PERSON', 'TIME', 'TIME_STAMP', 'Sentence']

    if Coref:
        # field_names[10] = "Corefed Sentence"
        # ANY CHANGES IN THE COREREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING IN SVO
        # THE SUBSCRIPT _coref_ IS CHECKED BELOW
        if isFile:
            inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
            outputCorefedDir = os.path.join(outputDir, "coref_" + inputFileBase)  # + "_CoRefed_files")
            # change input for all scripts - CoreNLP ++, SENNA, Gephi, wordclouds, Google Earth
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDirBase = os.path.basename(inputDir)
            outputCorefedDir = os.path.join(outputDir, "coref_Dir_" + inputDirBase)

        if not IO_files_util.make_directory(outputCorefedDir):
            return

        # inputFilename and inputDir are the original txt files to be coreferenced
        # 2 items are returned: filename string and true/False for error
        file_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename, inputFilename, inputDir, outputCorefedDir,
                                       openOutputFiles, createExcelCharts,
                                       memory_var,
                                       Manual_Coref_var)
        if error_indicator != 0:
            return

        if isFile:
            inputFilename = str(file_open)
            inputDir = ''
        else:
            # processing a directory
            inputFilename = ''
            inputDir = outputCorefedDir

        if len(file_open) > 0:
            filesToOpen.extend(file_open)

            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Stanford CoreNLP Co-Reference Resolution',
                                               'Finished running Stanford CoreNLP Co-Reference Resolution using the Neural Network approach at',
                                               True)

    # Date extractor _____________________________________________________

    if date_extractor_var:
        files = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                                 openOutputFiles, createExcelCharts,
                                                                 'normalized-date', False, memory_var, document_length_var, limit_sentence_length_var)
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

      # CoreNLP _____________________________________________________
    if CoreNLP_SVO_extractor_var:

        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_annotator_util.py') == False:
            return

        tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                       outputDir, openOutputFiles,
                                                                       createExcelCharts,
                                                                       'SVO', False,
                                                                       memory_var, document_length_var, limit_sentence_length_var,
                                                                       extract_date_from_filename_var=False,
                                                                       date_format='',
                                                                       date_separator_var='',
                                                                       date_position_var=0)
        if len(tempOutputFiles)>0:
            filesToOpen.extend(tempOutputFiles)
            svo_result_list.append(tempOutputFiles[0])

        toProcess_list = []
        field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O', 'Location', 'Person', 'Time',
                       'Time stamp', 'Sentence']
        if isFile & Coref:
            # ANY CHANGES IN THE COREFERENCED OUTPUT FILENAMES (_coref_) WILL AFFECT DATA PROCESSING BELOW
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
            # svo_CoreNLP_merged_file=''
            svo_CoreNLP_merged_file = os.path.join(outputSVODir, "NLP_CoreNLP_SVO_" + inputFileBase + ".csv")
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
            svo_CoreNLP_merged_file = os.path.join(outputSVODir, "NLP_CoreNLP_SVO_Dir_" + inputDirBase + ".csv")

    # SENNA _____________________________________________________

    if SENNA_SVO_extractor_var:
        # TODO must filter SVO results by social actors if the user selected that option
        #   both options run correctly for CoreNLP ++
        svo_SENNA_files = []
        svo_SENNA_file = semantic_role_labeling_senna.run_senna(inputFilename, inputDir, outputDir, openOutputFiles,
                                                                createExcelCharts=True)
        if len(svo_SENNA_file) > 0:
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

    # next lines create summaries of comparative results from CoreNLP and SENNA
    if SENNA_SVO_extractor_var and CoreNLP_SVO_extractor_var:
        if svo_CoreNLP_merged_file and svo_SENNA_file:
            CoreNLP_PlusPlus_file = svo_CoreNLP_merged_file
            freq_csv = SVO_util.count_frequency_two_svo(CoreNLP_PlusPlus_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
            combined_csv = SVO_util.combine_two_svo(CoreNLP_PlusPlus_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
            filesToOpen.extend(freq_csv)
            filesToOpen.append(combined_csv)

    # CoreNLP OpenIE _____________________________________________________
    if CoreNLP_OpenIE_var:
        tempOutputFiles = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                           outputDir, openOutputFiles,
                                                                           createExcelCharts,
                                                                           'OpenIE', 
                                                                           False,
                                                                           memory_var, document_length_var, limit_sentence_length_var,
                                                                           extract_date_from_filename_var=False,
                                                                           date_format='',
                                                                           date_separator_var='',
                                                                           date_position_var=0)
        
        if len(tempOutputFiles)>0:
            filesToOpen.extend(tempOutputFiles)

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
                        if "CoreNLP" in f or "SENNA_SVO" in f:
                            filesToOpen.append(gexf_file)
                        if not save_intermediate_file:
                            gexf_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if
                                          f.endswith('.gexf')]
                            for f in gexf_files:
                                if "CoreNLP" not in f and "SENNA_SVO" not in f:
                                    os.remove(f)

        # wordcloud  _________________________________________________
        if wordcloud_var:
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                               'Started running Wordclouds at', True)
            if inputFilename[-4:] == ".csv":
                if IO_csv_util.GetNumberOfRecordInCSVFile(inputFilename) > 1:  # including headers; file is empty
                    myfile = IO_files_util.openCSVFile(inputFilename, 'r')
                    #CYNTHIA
                    out_file = wordclouds_util.SVOWordCloud(myfile, inputFilename, outputDir, "", prefer_horizontal=.9)
                    myfile.close()
                    filesToOpen.append(out_file)
            else:
                for f in svo_result_list:
                    if IO_csv_util.GetNumberOfRecordInCSVFile(f) > 1:  # including headers; file is empty
                        myfile = IO_files_util.openCSVFile(f, "r")
                        #CYNTHIA
                        out_file = wordclouds_util.SVOWordCloud(myfile, f, outputDir, "", prefer_horizontal=.9)
                        myfile.close()
                        if "SVO" in f or "SENNA_SVO" in f:
                            filesToOpen.append(out_file)
                        # if not merge_txt_file_option and not save_intermediate_file:
                        #     png_files = [os.path.join(outputDir, f) for f in os.listdir(outputDir) if
                        #                  f.endswith('.png')]
                        #     for f in png_files:
                        #         if "CoreNLP_SVO" not in f and "SENNA_SVO" not in f:
                        #             os.remove(f)
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

                    reminders_util.checkReminder(config_filename, reminders_util.title_options_geocoder,
                                                 reminders_util.message_geocoder, True)
                    # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
                    out_file, kmloutputFilename = GIS_pipeline_util.GIS_pipeline(GUI_util.window,
                                 config_filename, f,
                                 outputDir,
                                 'Nominatim', 'Google Earth Pro & Google Maps',
                                 False,
                                 'Location',
                                 'utf-8',
                                 0, 1, [''], [''], # group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                                 ['Pushpins'], ['red'], # icon_var_list, specific_icon_var_list,
                                 [0], ['1'], [0], [''], # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                                 [1], [1]) # bold_var_list, italic_var_list

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

    if len(inputDir) > 1 and len(filesToOpen) > 0 and outputSVODir!='':  # when processing a directory, the output changes
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
                                 memory_var.get(),
                                 document_length_var.get(),
                                 limit_sentence_length_var.get(),
                                 CoRef_var.get(),
                                 manual_Coref_var.get(),
                                 date_extractor_var.get(),
                                 CoreNLP_SVO_extractor_var.get(),
                                 SENNA_SVO_extractor_var.get(),
                                 CoreNLP_OpenIE_var.get(),
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
GUI_height=670 # height of GUI with full I/O display

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
    CoRef_var.set(0)
    manual_Coref_checkbox.configure(state='disabled')
    manual_Coref_var.set(0)
    subjects_var.set(0)
    verbs_var.set(0)
    objects_var.set(0)
    subjects_dict_var.set('')
    verbs_dict_var.set('')
    objects_dict_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

CoRef_var = tk.IntVar()
memory_var = tk.StringVar()
manual_Coref_var = tk.IntVar()
date_extractor_var = tk.IntVar()
CoreNLP_SVO_extractor_var = tk.IntVar()
SENNA_SVO_extractor_var = tk.IntVar()
CoreNLP_OpenIE_var = tk.IntVar()
subjects_var = tk.IntVar()
objects_var = tk.IntVar()
verbs_var = tk.IntVar()
subjects_dict_var = tk.StringVar()
verbs_dict_var = tk.StringVar()
objects_dict_var = tk.StringVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               pre_processing_button)
# memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 100, y_multiplier_integer,
                                               memory_var, True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+150, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 370, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate() + 550, y_multiplier_integer,
                                               limit_sentence_length_var)

CoRef_var.set(0)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP - Neural Network)',
                                variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoRef_checkbox)

# CoRef_menu_var.set("Neural Network")
# CoRef_menu = tk.OptionMenu(window, CoRef_menu_var, 'Deterministic', 'Statistical', 'Neural Network')
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer, CoRef_menu)

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               manual_Coref_checkbox)

def activateCoRefOptions(*args):
    if CoRef_var.get() == 1:
        # CoRef_menu.configure(state='normal')
        if input_main_dir_path.get()!='':
            manual_Coref_checkbox.configure(state='disabled')
        else:
            manual_Coref_checkbox.configure(state='normal')
            manual_Coref_var.set(1)
        memory_var.configure(state='normal')
        # manual_Coref_checkbox.configure(state='disabled')
    else:
        # CoRef_menu.configure(state='disabled')
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
CoreNLP_SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs & SVs (via CoreNLP Enhanced++ Dependencies)',
                                                variable=CoreNLP_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoreNLP_SVO_extractor_checkbox, True)

SENNA_SVO_extractor_var.set(0)
SENNA_SVO_extractor_checkbox = tk.Checkbutton(window, text='Extract SVOs & SVs (via SENNA)',
                                              variable=SENNA_SVO_extractor_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.SVO_2nd_column, y_multiplier_integer,
                                               SENNA_SVO_extractor_checkbox, True)

CoreNLP_OpenIE_var.set(0)
CoreNLP_OpenIE_checkbox = tk.Checkbutton(window, text='Extract relation triples (via CoreNLP OpenIE)', variable=CoreNLP_OpenIE_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               CoreNLP_OpenIE_checkbox, False)

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
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where in maps (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               google_earth_checkbox)

TIPS_lookup = {'SVO extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'Stanford CoreNLP memory issues':'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'Stanford CoreNLP date extractor': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP enhanced dependencies parser (SVO)':'TIPS_NLP_Stanford CoreNLP enhanced dependencies parser (SVO).pdf',
               'CoNLL table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'Stanford CoreNLP coreference resolution': "TIPS_NLP_Stanford CoreNLP coreference resolution.pdf",
               "Google Earth Pro": "TIPS_NLP_Google Earth Pro.pdf", "Geocoding": "TIPS_NLP_Geocoding.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf",
               'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'SVO extraction and visualization', 'utf-8 encoding', 'Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor', 'Stanford CoreNLP OpenIE', 'Stanford CoreNLP parser', 'Stanford CoreNLP enhanced dependencies parser (SVO)', 'CoNLL table', 'Stanford CoreNLP coreference resolution', 'Google Earth Pro', 'Geocoding', 'Gephi network graphs', 'Java download install run'


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
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+2), "Help",
                                  "The Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+3), "Help",
                                  "Please, tick the checkbox to run the Stanford CoreNLP coreference resolution annotator using the Neural Network approach.\n\n\Please, BE PATIENT. Depending upon size and number of documents to be coreferenced the algorithm may take a long a time.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+4), "Help",
                                  "Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nThe option is not available when processing a directory of files. You can always use the 'Stanford_CoreNLP_coreference_main' GUI to\n   1. open a merged coreferenced file;\n   2. split merged coreferenced files.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+5), "Help",
                                  "Please, tick the checkbox if you wish to run the Stanford CoreNLP normalized NER date annotator to extract standard dates from text in the yyyy-mm-dd format (e.g., 'the day before Christmas' extracted as 'xxxx-12-24').\n\nThis will display time plots of dates, visualizing the WHEN of the 5 Ws of narrative."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+6), "Help",
                                  "Please, tick the checkboxes if you wish to run the Stanford CoreNLP neural network Enhanced++ Dependencies parser and/or SENNA to extract SVO triplets and SV pairs. Tick the checkbox 'Extract relation triples (via OpenIE)' if you wish to run the Stanford CoreNLP OpenIE annotator to extract any relation triples (not just SVOs).\n\nSENNA can be downloaded at https://ronan.collobert.com/senna/download.html\n\nIn INPUT CoreNLP and/or SENNA can process a single txt file or a directory containing a set of txt files.\n\nIn OUTPUT CoreNLP and/or SENNA will produce a csv file of SVO results and, if the appropriate visualization options are selected, a Gephi gexf network file, png word cloud file, and Google Earth Pro kml file (GIS maps are not produced when running SVO with SENNA; SENNA, by and large, does not produce geocodable locations.\n\nWHEN PROCESSING A DIRECTORY, ALL OUTPUT FILES WILL BE SAVED IN A SUBDIRECTORY OF THE SELECTED OUTPUT DIRECTORY WITH THE NAME OF THE INPUT DIRECTORY."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+7), "Help",
                                  "Please, tick the checkbox to filter all SVO extracted triplets for Subjects, Verbs, and Objects via dictionary filter files.\n\nFor instance, you can filter SVO by social actors and social action. In fact, the file \'social-actor-list.csv\', created via WordNet with keyword person and saved in the \'lib/wordLists\' subfolder, will be automatically loaded as the DEFAULT dictionary file (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly automatically loaded as the DEFAULT dictionary file for verbs.\n\nDictionary filter files can be created via WordNet and saved in the \'lib/wordLists\' subfolder. You can edit that list, adding and deleting entries at any time, using any text editor.\n\nWordNet produces thousands of entries for nouns and verbs. For more limited domains, you way want to pair down the number to a few hundred entries."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+8), "Help",
                                  "The three widgets display the currently selected dictionary filter files for Subjects, Verbs, and Objects (Objects share the same file as Subjects and you may wish to change that).\n\nThe filter file social-actor-list, created via WordNet with person as keyword and saved in the \'lib/wordLists\' subfolder, will be automatically set as the DEFAULT filter for subjects (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly set as the DEFAULT dictionary file for verbs.\n\nThe widgets are disabled because you are not allowed to tamper with these values. If you wish to change a selected file, please tick the appropriate checkbox in the line above (e.g., Filter Subject) and you will be prompted to select a new file."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+9), "Help",
                                  "Please, tick the checkboxes:\n\n  1. to visualize SVO relations in network graphs via Gephi;;\n\n  2. to visualize SVO relations in a wordcloud;\n\n  3. to use the NER location values to extract the WHERE part of the 5 Ws of narrative (Who, What, When, Where, Why); locations will be automatically geocoded (i.e., assigned latitude and longitude values) and visualized as maps via Google Earth Pro (as point map) and Google Maps (as heat map). ONLY THE LOCATIONS FOUND IN THE EXTRACTED SVO WILL BE DISPLAYED, NOT ALL THE LOCATIONS PRESENT IN THE TEXT.\n\nThe GIS algorithm uses Nominatim, rather than Google, as the default geocoder tool. If you wish to use Google for geocoding, please, use the GIS_main script."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+10), "Help",
                                  GUI_IO_util.msg_openOutputFiles)

help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), GUI_IO_util.get_basic_y_coordinate(),
             GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message = "This set of Python 3 scripts extract automatically most of the elements of a story grammar and visualize the results in network graphs and GIS maps. A story grammar – basically, the 5Ws + H of modern journalism: Who, What, When, Where, Why, and How – provides the basic building blocks of narrative.\n\nThe set of scripts assembled here for this purpose ranges from testing for utf-8 compliance of the input text, to resolution for pronominal coreference, extraction of normalized NER dates (WHEN), visualized in various Excel charts, extraction, geocoding, and mapping in Google Earth Pro of NER locations.\n\nAt the heart of the SVO approach are two scripts, one based on the Stanford CoreNLP enhanced dependencies parser and another script based on SENNA. For passive sentences, the pipeline swaps S and O to transform the triplet into active voice. Thus, the WHO, WHAT (WHOM) are extracted from a text. Each component of the SVO triplet can be filtered via specific dictionaries (e.g., filtering for social actors and social actions, only). The set of SVO triplets are then visualized in dynamic network graphs (via Gephi).\n\nThe WHY and HOW of narrative are still beyond the reach of the current set of SVO scripts.\n\nIn INPUT the scripts expect a txt file to run utf-8 check, coreference resolution, date extraction, and CoreNLP. You can also enter a csv file, the output of a previous run with CoreNLP/SENNA (_svo.csv/_SVO_Result) marked file) if all you want to do is to visualize results.\n\nIn OUTPUT, the scripts will produce several csv files, a png image file, and a KML file depending upon the options selected."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer, readMe_command, TIPS_lookup, TIPS_options, IO_setup_display_brief)


def warnUser(*args):
    if GUI_util.input_main_dir_path.get() != '':
        reminders_util.checkReminder(config_filename, reminders_util.title_options_SVO_corpus,
                                     reminders_util.message_SVO_corpus, True)
        # manual_Coref_var.set(0)
        # manual_Coref_checkbox.configure(state='disabled')

GUI_util.input_main_dir_path.trace('w', warnUser)

warnUser()

GUI_util.window.mainloop()
