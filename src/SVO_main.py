# Written by Gabriel Wang 2018
# Modified by Cynthia Dong (Fall 2019-Spring 2020)
# Modified by Matthew Chau (Spring 2021)
# Modified by Roberto Franzosi (Spring-Fall 2021, Fall 2022)
# Modified by Cynthia Dong (Fall 2021)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "SVO main",
                                          ['subprocess', 'os', 'tkinter']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

# to install stanfordnlp, first install
#   pip3 install torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html
#   pip3 install stanfordnlp
# import stanfordnlp

import config_util
import GUI_IO_util
import IO_files_util
import Gephi_util
import GIS_pipeline_util
import wordclouds_util
import IO_csv_util
import SVO_util
import Stanza_util
import Stanford_CoreNLP_coreference_util
import Stanford_CoreNLP_util
import SENNA_util
import spaCy_util
import reminders_util
import knowledge_graphs_WordNet_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,
        Coref,
        Manual_Coref_var,
        normalized_NER_date_extractor_var,
        package_var,
        gender_var,
        quote_var,
        subjects_dict_var,
        verbs_dict_var,
        objects_dict_var,
        lemmatize_subjects,
        lemmatize_verbs,
        lemmatize_objects,
        gephi_var,
        wordcloud_var,
        google_earth_var):

    # pull the widget names from the GUI since the scripts change the IO values
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()

    outputCorefedDir = ''
    outputSVODir = ''
    outputLocations = []

    filesToOpen = []
    files_to_open = []

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')
    extract_date_from_filename_var, date_format_var, date_separator_var, date_position_var = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    # the merge option refers to merging the txt files into one
    merge_txt_file_option = False

    if Coref == False and package_display_area_value == '':
        mb.showwarning(title='No option selected',
                       message="No option has been selected.\n\nPlease, select an option and try again.")
        return

    if inputFilename[-4:] == '.txt':
        if (package_var=='') and (
                gephi_var == True or wordcloud_var == True or google_earth_var == True):
            mb.showerror(title='Input file/option error',
                         message="The data visualization option(s) you have selected require either an _svo.csv/_SVO_Result file in input or CoreNLP OpenIE and/or SENNA selected.\n\nPlease, check your input file and/or algorithm selections and try again.")
            return
    elif inputFilename[-4:] == '.csv':
        if not 'SVO_' in inputFilename:
            mb.showerror(title='Input file error',
                         message="The selected input is a csv file, but... not an _svo.csv file.\n\nPlease, select an _svo.csv file (or txt file(s)) and try again.")
            return
        if (Coref == True or Manual_Coref_var == True or
                normalized_NER_date_extractor_var == True or package_var!=''):
            mb.showerror(title='Input file/option error',
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
    location_filename=''
    outputDirSV=outputDir

    if len(inputFilename) > 0:
        isFile = True
        save_intermediate_file = False
    else:  # directory input
        save_intermediate_file = False
        isFile = False

    if package_var=='Stanford CoreNLP':
        # simplify the name since it is then used in output files/folders
        package_var = 'CoreNLP'
    if 'OpenIE' in package_var:
        package_var = 'OpenIE'

    # the actual directory is created in the CoreNLP_annotator_util
    #   all we need here is the name of the directory
    if inputFilename != '':
        inputBaseName = os.path.basename(inputFilename)[0:-4]  # without .txt
    else:
        inputBaseName = os.path.basename(inputDir)
    if Coref:
        outputCorefDir = os.path.join(outputDirSV, package_var+ '_coref_' + inputBaseName)
        outputSVODir = os.path.join(outputDir, package_var + '_SVO_coref_' + inputBaseName)
    else:
        outputCorefDir = ''
        outputSVODir = os.path.join(outputDir, package_var + '_SVO_' + inputBaseName)

    # create an SVO subdirectory of the output directory
    outputSVODir = IO_files_util.make_output_subdirectory('','',outputSVODir, label='',
                                                              silent=False)
    if outputSVODir == '':
        return

    if Coref:
        # create a subdirectory of the output directory
        outputCorefDir = IO_files_util.make_output_subdirectory('', '', outputCorefDir, '',
                                                            silent=False)

    outputDir = outputSVODir # outputDir is the main subdir inside the main output directory inside which will go gender,
    # the outputDir folder inside the main output folder will contain subdir SVO, gender, GIS, quote, etc.

    if package_var=='OpenIE' or package_var=='SENNA':
        outputSVOSVODir = outputSVODir + os.sep + package_var
    else:
        outputSVOSVODir = outputSVODir + os.sep + 'SVO'

# CoRef _____________________________________________________

    # field_names = ['Document ID', 'Sentence ID', 'Document', 'S', 'V', 'O', 'LOCATION', 'PERSON', 'TIME', 'TIME_STAMP', 'Sentence']

    if Coref:
        # must be changed
        if language_var != 'English' and language_var != 'Chinese':
            mb.showwarning(title='Language',
                           message='The Stanford CoreNLP coreference resolution annotator is only available for English and Chinese.')
            return
        # inputFilename and inputDir are the original txt files to be coreferenced
        # 2 items are returned: filename string and true/False for error
        files_to_open, error_indicator = Stanford_CoreNLP_coreference_util.run(config_filename,
                                       inputFilename, inputDir, outputCorefDir,
                                       openOutputFiles, createCharts, chartPackage,
                                       language_var,
                                       Manual_Coref_var)
        if error_indicator != 0:
            return
        for file in files_to_open:
            # visualize the data produced under coref table
            if 'chart' in file or '.csv' in file:
                filesToOpen.append(file)

        # changed the inputDir to the coreferenced dir
        inputDir = outputCorefDir + os.sep + 'coref'
        # only the inputDir will be used when coreferencing, whether it will contain a set of files or just one file
        inputFilename=''

 # Date extractor _____________________________________________________
    # TODO no longer used as an option
    if normalized_NER_date_extractor_var:
        files = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                                 openOutputFiles, createCharts, chartPackage,
                                                                 'normalized-date', False, language_var,  memory_var, document_length_var, limit_sentence_length_var)
        if len(files)>0:
            filesToOpen.extend(files)

    if lemmatize_subjects or lemmatize_verbs or lemmatize_objects:
        WordNetDir, missing_external_software = IO_libraries_util.get_external_software_dir('SVO_main',
                                                                                            'WordNet')
        if WordNetDir == None:
            return

    if google_earth_var:
        # create a GIS subdirectory of the output directory
        outputGISDir = IO_files_util.make_output_subdirectory('', '', outputSVODir,
                                                              label='GIS',
                                                              silent=True)
        location_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputGISDir, '.csv',
                                                                     'CoreNLP_SVO_LOCATIONS')
        outputLocations.append(location_filename)

# CoreNLP Dependencies ++ _____________________________________________________

    if package_var=='CoreNLP':

        if language_var == 'Arabic' or language_var == 'Hungarian':
            mb.showwarning(title='Language',
                           message='The Stanford CoreNLP dependency parsing is is not available for Arabic and Hungarian.')
            return

        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
            return
        gender_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputSVODir + os.sep + 'gender', '.csv',
                                                                       'CoreNLP_SVO_gender')


        gender_filename_html = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputSVODir + os.sep + 'gender', '.html',
                                                          'dict_annotated_gender')

        quote_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputSVODir + os.sep + 'quote', '.csv',
                                                                       'CoreNLP_SVO_quote')

        params = ['SVO']
        if gender_var:
            params.append("gender")
        if quote_var:
            params.append("quote")

        # annotator_params are different from gender_var and quote_var
        # annotator_params will run the annotator for SVO and run the gender and quote placing results inside the SVO output folder
        # gender_var and quote_var are used in CoreNLP_annotate to add gender and quote columns to the SVO csv output file
        # they can be passed independently, but it is useful to have both arguments
        tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                   outputSVODir, openOutputFiles,
                                   createCharts,
                                   chartPackage,
                                   params, False,
                                   language_var, memory_var, document_length_var, limit_sentence_length_var,
                                   extract_date_from_text_var=extract_date_from_text_var,
                                   extract_date_from_filename_var=extract_date_from_filename_var,
                                   date_format=date_format_var,
                                   date_separator_var=date_separator_var,
                                   date_position_var=date_position_var,
                                   google_earth_var=google_earth_var,
                                   location_filename = location_filename,
                                   gender_var = gender_var, gender_filename = gender_filename, gender_filename_html = gender_filename_html,
                                   quote_var = quote_var, quote_filename = quote_filename)

        # Filtering SVO
        if len(tempOutputFiles)!=0:
            SVO_filename=tempOutputFiles[0]
            filesToOpen.extend(tempOutputFiles)
            svo_result_list.append(tempOutputFiles[0])

# CoreNLP OpenIE _____________________________________________________
    if 'OpenIE' in package_var:
        if language_var != 'English':
            mb.showwarning(title='Language',
                           message='The Stanford CoreNLP OpenIE annotator is only available for English.')
            return

        tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                           outputSVODir, openOutputFiles,
                                                                           createCharts,
                                                                           chartPackage,
                                                                           'OpenIE',
                                                                           False,
                                                                           language_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                           extract_date_from_text_var=extract_date_from_text_var,
                                                                           extract_date_from_filename_var=extract_date_from_filename_var,
                                                                           date_format=date_format_var,
                                                                           date_separator_var=date_separator_var,
                                                                           date_position_var=date_position_var,
                                                                           google_earth_var = google_earth_var,
                                                                           location_filename = location_filename)

        # Filtering SVO
        if len(tempOutputFiles)!=0:
            SVO_filename=tempOutputFiles[0]
            filesToOpen.extend(tempOutputFiles)
            svo_result_list.append(tempOutputFiles[0])

# SENNA _____________________________________________________
    if package_var=='SENNA':
        if language_var != 'English':
            mb.showwarning(title='Language',
                           message='SENNA is only available for English.')
            return
        # TODO must filter SVO results by social actors if the user selected that option
        #   both options run correctly for CoreNLP ++
        svo_SENNA_files = []
        svo_SENNA_file = SENNA_util.run_senna(inputFilename, inputDir, outputSVODir, openOutputFiles,
                                                                createCharts, chartPackage)
        if svo_SENNA_file!='':
            SVO_filename=svo_SENNA_file
            svo_result_list.append(svo_SENNA_file)

        if save_intermediate_file:
            for file in IO_files_util.getFileList(inputFile=inputFilename, inputDir=inputDir, fileType='.txt'):
                svo_SENNA_files += SENNA_util.run_senna(inputFilename=file, inputDir='',
                                                                          outputDir=os.path.join(outputDir,
                                                                                                 outputSVODir),
                                                                          openOutputFiles=openOutputFiles,
                                                                          createCharts=createCharts,
                                                                          chartPackage=chartPackage)
        else:
            svo_SENNA_files = [svo_SENNA_file]

        filesToOpen.extend(svo_SENNA_files)

        # # Filtering SVO
        #
        # if filter_subjects_var.get() or filter_verbs_var.get() or filter_objects_var.get() or lemmatize_subjects or lemmatize_verbs or lemmatize_objects:
        #     for file in svo_SENNA_files:
        #         output = SVO_util.filter_svo(window,file, subjects_dict_var, verbs_dict_var, objects_dict_var,
        #                             lemmatize_subjects, lemmatize_verbs, lemmatize_objects,
        #                             outputSVOSVODir, createCharts, chartPackage)
        #         if output != None:
        #             filesToOpen.extend(output)

        # for file in svo_SENNA_files:
        #     SVO_filename=file
        #     svo_result_list.append(file)
        #
        # testing that SENNA output directory is not empty, probably because the data matrix is too large for the computer memory

        # # Getting the list of directories
        if len(os.listdir(outputSVODir))==0:
            mb.showwarning(title='Warning',message='It looks like the SENNA algorithm did not produce any output. The output directory\n' + outputSVODir + '\nis empty.\n\nDepending upon the input corpus size, the SENNA output data matrix may simply be too big for the memory available on your machine (all the more true for an 8GB machine).')

    # next lines create summaries of comparative results from CoreNLP and SENNA
    # if SENNA_SVO_extractor_var and SVO_extractor_var:
    #     if len(os.listdir(outputSVODir)) > 0:
    #         if svo_CoreNLP_merged_file and svo_SENNA_file:
    #             CoreNLP_PlusPlus_file = svo_CoreNLP_merged_file
    #             freq_csv, compare_outout_name = SVO_util.count_frequency_two_svo(CoreNLP_PlusPlus_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
    #             combined_csv = SVO_util.combine_two_svo(CoreNLP_PlusPlus_file, svo_SENNA_file, inputFileBase, inputDir, outputDir)
    #             filesToOpen.append(freq_csv)
    #             filesToOpen.append(combined_csv)

# spaCY _____________________________________________________

    if package_var == 'spaCy':
        document_length_var = 1
        limit_sentence_length_var = 1000
        annotator = 'SVO'
        tempOutputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputSVODir,
                                                    openOutputFiles,
                                                    createCharts, chartPackage,
                                                    annotator, False,
                                                    language,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    extract_date_from_filename_var=extract_date_from_filename_var,
                                                    date_format=date_format_var,
                                                    date_separator_var=date_separator_var,
                                                    date_position_var=date_position_var)

        if tempOutputFiles != None:
            filesToOpen.extend(tempOutputFiles)
            # the SVO output file is in tempOutputFiles[1] tempOutputFiles[0] contains the parser output
            SVO_filename = tempOutputFiles[1]
            svo_result_list.append(tempOutputFiles[1])

# Stanza _____________________________________________________

    if package_var == 'Stanza':
        document_length_var = 1
        limit_sentence_length_var = 1000
        annotator = 'SVO'
        tempOutputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputSVODir,
                                                      openOutputFiles,
                                                      createCharts, chartPackage,
                                                      annotator, False,
                                                      language_list,
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      extract_date_from_filename_var=extract_date_from_filename_var,
                                                      date_format=date_format_var,
                                                      date_separator_var=date_separator_var,
                                                      date_position_var=date_position_var)

        if tempOutputFiles != None:
            filesToOpen.extend(tempOutputFiles)
            # the SVO output file is in tempOutputFiles[1] tempOutputFiles[0] contains the parser output
            SVO_filename = tempOutputFiles[1]
            svo_result_list.append(tempOutputFiles[1])

    # Filtering SVO for all packages
    if len(svo_result_list)>0:
        if filter_subjects_var.get() or filter_verbs_var.get() or filter_objects_var.get() or \
                lemmatize_subjects or lemmatize_verbs or lemmatize_objects:
            output = SVO_util.filter_svo(window,SVO_filename,
                                subjects_dict_var, verbs_dict_var, objects_dict_var,
                                lemmatize_subjects, lemmatize_verbs, lemmatize_objects,
                                outputSVOSVODir, createCharts, chartPackage)
            if output != None:
                filesToOpen.extend(output)

        if lemmatize_verbs:
            # tempOutputFiles[0] is the filename with lemmatized SVO values
            # we want to aggregate with WordNet the verbs in column 'V'
            # check that SVO output file contains records
            nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(SVO_filename,
                                                                                   encodingValue='utf-8')
            if nRecords > 1:
                # create a subdirectory of the output directory
                outputWNDir = IO_files_util.make_output_subdirectory('', '', outputSVODir,
                                                                     label='WordNet',
                                                                     silent=True)
                outputFilename = IO_csv_util.extract_from_csv(SVO_filename, outputWNDir, '', ['Verb (V)'])
                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, outputFilename, outputWNDir,
                                                                         config_filename, 'VERB',
                                                                         openOutputFiles, createCharts,
                                                                         chartPackage, language_var)
                os.remove(outputFilename)
                if output != None:
                    filesToOpen.extend(output)

                outputFilename = IO_csv_util.extract_from_csv(SVO_filename, outputWNDir, '',
                                                              ['Subject (S)', 'Object (O)'])
                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir, outputFilename, outputWNDir,
                                                                         config_filename, 'NOUN',
                                                                         openOutputFiles, createCharts,
                                                                         chartPackage, language_var)
                os.remove(outputFilename)
                if output != None:
                    filesToOpen.extend(output)
            else:
                reminders_util.checkReminder(config_filename, reminders_util.title_options_no_SVO_records,
                                             reminders_util.message_no_SVO_records, True)

        # filesToOpen.extend(tempOutputFiles)
        # svo_result_list.append(tempOutputFiles[0])

    reminders_util.checkReminder(config_filename, reminders_util.title_options_SVO_someone,
                                 reminders_util.message_SVO_someone, True)
    # the SVO script can take in input a csv SVO file previously computed: inputFilename
    # results currently produced are in svo_result_list
    if ('SVO_' in inputFilename) or (len(svo_result_list) > 0):
        # Gephi network graphs _________________________________________________
        if gephi_var:
            # previous svo csv files can be entered in input to display networks, wordclouds or GIS maps
            if inputFilename[-4:] == ".csv":
                nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename, encodingValue='utf-8')
                if nRecords > 1:   # including headers; file is empty
                    gexf_file = Gephi_util.create_gexf(window,inputFileBase, outputSVOSVODir, inputFilename, "Subject (S)", "Verb (V)", "Object (O)",
                                                       "Sentence ID")
                    filesToOpen.append(gexf_file)
                else:
                    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(svo_result_list[0])
                    if nRecords > 1:  # including headers; file is empty
                        gexf_file = Gephi_util.create_gexf(window,inputFileBase, outputSVOSVODir, svo_result_list[0],
                                                           "Subject (S)", "Verb (V)", "Object (O)", "Sentence ID")
                        filesToOpen.append(gexf_file)
            else:  # txt input file
                for f in svo_result_list:
                    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(f)
                    if nRecords > 1:  # including headers; file is empty
                        gexf_file = Gephi_util.create_gexf(window,os.path.basename(f)[:-4], outputSVOSVODir, f, "Subject (S)", "Verb (V)", "Object (O)",
                                                           "Sentence ID")
                        if "CoreNLP" in f or "SENNA_SVO" in f or "SpaCy" in f or "Stanza" in f:
                            filesToOpen.append(gexf_file)
                        if not save_intermediate_file:
                            gexf_files = [os.path.join(outputDir, f) for f in os.listdir(outputSVOSVODir) if
                                          f.endswith('.gexf')]
                            for f in gexf_files:
                                if "CoreNLP" not in f and "SENNA_SVO" not in f and "SpaCy" not in f and "Stanza" not in f: #CoreNLP accounts for both ++ and OpenIE
                                    os.remove(f)

# wordcloud  _________________________________________________

        if wordcloud_var:
            if inputFilename[-4:] == ".csv":
                nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename)
                if nRecords > 1:  # including headers; file is empty
                    if IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename) > 1:  # including headers; file is empty
                        myfile = IO_files_util.openCSVFile(inputFilename, 'r')
                        #CYNTHIA
                        out_file = wordclouds_util.SVOWordCloud(myfile, inputFilename, outputSVODir + os.sep + 'SVO', "", prefer_horizontal=.9)
                        myfile.close()
                        filesToOpen.append(out_file)
            else:
                for f in svo_result_list:
                    nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(f)
                    if nRecords > 1:  # including headers; file is empty
                        myfile = IO_files_util.openCSVFile(f, "r")
                        #CYNTHIA
                        # out_file = wordclouds_util.SVOWordCloud(myfile, f, outputSVODir + os.sep + 'SVO', "", prefer_horizontal=.9)
                        out_file = wordclouds_util.SVOWordCloud(myfile, f, outputSVOSVODir, "", prefer_horizontal=.9)
                        myfile.close()
                        if "CoreNLP" in f or "SENNA_SVO" in f:
                            filesToOpen.append(out_file)

# GIS maps _____________________________________________________

        # SENNA locations are not really geocodable locations
        if google_earth_var:
            # for f in svo_result_list:
                # SENNA and OpenIE do not have a location field
            if (package_var=='SENNA') and os.path.isfile(location_filename):
                reminders_util.checkReminder(config_filename, reminders_util.title_options_GIS_OpenIE_SENNA,
                                             reminders_util.message_GIS_OpenIE_SENNA, True)
            else:
                if (package_var != 'SENNA') and os.path.isfile(location_filename):
                    reminders_util.checkReminder(config_filename, reminders_util.title_options_geocoder,
                                                 reminders_util.message_geocoder, True)
                    # locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
                    date_present = (extract_date_from_text_var == True) or (extract_date_from_filename_var == True)
                    country_bias = ''
                    area_var = ''
                    restrict = False
                    for location_filename in outputLocations:
                        out_file = GIS_pipeline_util.GIS_pipeline(GUI_util.window,
                                     config_filename, location_filename, inputDir,
                                     outputGISDir,
                                     'Nominatim', 'Google Earth Pro & Google Maps', createCharts, chartPackage,
                                     date_present,
                                     country_bias,
                                     area_var,
                                     restrict,
                                     'Location',
                                     'utf-8',
                                     0, 1, [''], [''], # group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                                     ['Pushpins'], ['red'], # icon_var_list, specific_icon_var_list,
                                     [0], ['1'], [0], [''], # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                                     [1], [1]) # bold_var_list, italic_var_list

                        if out_file!=None:
                            if len(out_file) > 0:
                                # since out_file produced by KML is a list cannot use append
                                filesToOpen = filesToOpen + out_file

# generate subset of files to be opened

    if openOutputFiles == True and len(filesToOpen) > 0:
        filesToOpenSubset = []
        # add the SVO main file
        filesToOpenSubset.append(SVO_filename)
        for file in filesToOpen:
            # open all charts, all Google Earth and Google Maps maps, Gephi gexf network graph, html files, and wordclouds png files
            if file[-4:] == '.kml' or file[-5:] == '.html' or file[-4:] == '.png' or file[-5:] == '.gexf' or \
                file[-5:] == '.xlsx':
                filesToOpenSubset.append(file)
        filesToOpenSubset_string = ", \n   ".join(filesToOpenSubset)
        print("Subset of the " + str(len(filesToOpenSubset)) + " SVO files from the different subfolders to be opened:\n   " + str(filesToOpenSubset_string))
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName, filesToOpenSubset)

# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_dropdown_field.get(),
                                 CoRef_var.get(),
                                 manual_Coref_var.get(),
                                 normalized_NER_date_extractor_var.get(),
                                 package_var.get(),
                                 gender_var.get(),
                                 quote_var.get(),
                                 subjects_dict_var.get(),
                                 verbs_dict_var.get(),
                                 objects_dict_var.get(),
                                 lemmatize_subjects_var.get(),
                                 lemmatize_verbs_var.get(),
                                 lemmatize_objects_var.get(),
                                 gephi_var.get(),
                                 wordcloud_var.get(),
                                 google_earth_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=550, # height at brief display
                             GUI_height_full=590, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display


GUI_label = 'Graphical User Interface (GUI) for Subject-Verb-Object (SVO) Extraction & Visualization Pipeline - Extracting 4 of the 5 Ws of Narrative: Who, What, When, Where'

# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir
config_input_output_numeric_options=[6,1,0,1]
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

# location of this src python file
scriptPath = GUI_IO_util.scriptPath
# one folder UP, the NLP folder
NLPPath = GUI_IO_util.NLPPath
# subdirectory of script directory where config files are saved
# libPath = GUI_IO_util.libPath +os.sep+'wordLists'

window = GUI_util.window
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)


def clear(e):
    CoRef_var.set(0)
    manual_Coref_checkbox.configure(state='disabled')
    manual_Coref_var.set(0)
    subjects_checkbox.configure(state='normal')
    verbs_checkbox.configure(state='normal')
    objects_checkbox.configure(state='normal')
    filter_subjects_var.set(1)
    filter_verbs_var.set(1)
    filter_objects_var.set(0)
    activate_filter_dictionaries()
    lemmatize_subjects_checkbox.configure(state='normal')
    lemmatize_verbs_checkbox.configure(state='normal')
    lemmatize_objects_checkbox.configure(state='normal')
    lemmatize_subjects_var.set(0)
    lemmatize_verbs_var.set(1)
    lemmatize_objects_var.set(0)
    gephi_var.set(1)
    wordcloud_var.set(1)
    google_earth_var.set(1)
    gephi_checkbox.configure(state='normal')
    wordcloud_checkbox.configure(state='normal')
    google_earth_checkbox.configure(state='normal')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

package_display_area_value = tk.StringVar()
language_var = tk.StringVar()
language_list = []
CoRef_var = tk.IntVar()

manual_Coref_var = tk.IntVar()
package_var = tk.StringVar()
normalized_NER_date_extractor_var = tk.IntVar()
gender_var = tk.IntVar()
quote_var = tk.IntVar()
SRL_var = tk.IntVar()
filter_subjects_var = tk.IntVar()
filter_objects_var = tk.IntVar()
filter_verbs_var = tk.IntVar()
subjects_dict_var = tk.StringVar()
verbs_dict_var = tk.StringVar()
objects_dict_var = tk.StringVar()
lemmatize_subjects_var = tk.IntVar()
lemmatize_objects_var = tk.IntVar()
lemmatize_verbs_var = tk.IntVar()
gephi_var = tk.IntVar()
wordcloud_var = tk.IntVar()
google_earth_var = tk.IntVar()

def open_GUI():
    call("python file_checker_converter_cleaner_main.py", shell=True)

pre_processing_button = tk.Button(window, text='Pre-processing tools (Open file checking & cleaning GUI)',width=50,command=lambda:open_GUI())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                   pre_processing_button,
                                   False, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate(),
                                   "Click on the button to open the GUI")

# NLP packages & languages ------------------------------------------------------------------------------------------------------

CoRef_var.set(0)
CoRef_checkbox = tk.Checkbutton(window, text='Coreference Resolution, PRONOMINAL (via Stanford CoreNLP - Neural Network)',
                                variable=CoRef_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               CoRef_checkbox)

# CoRef_menu_var.set("Neural Network")
# CoRef_menu = tk.OptionMenu(window, CoRef_menu_var, 'Deterministic', 'Statistical', 'Neural Network')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer, CoRef_menu)

manual_Coref_var.set(0)
manual_Coref_checkbox = tk.Checkbutton(window, text='Manually edit coreferenced document ', variable=manual_Coref_var,
                                       onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_indented_coordinate(), y_multiplier_integer,
                                               manual_Coref_checkbox)

def activateCoRefOptions(*args):
    if CoRef_var.get() == 1:
        # CoRef_menu.configure(state='normal')
        if input_main_dir_path.get()!='':
            reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_coref,
                                         reminders_util.message_CoreNLP_coref, True)
            manual_Coref_var.set(0)
            manual_Coref_checkbox.configure(state='disabled')
        else:
            manual_Coref_checkbox.configure(state='normal')
            manual_Coref_var.set(1)
        # manual_Coref_checkbox.configure(state='disabled')
    else:
        manual_Coref_checkbox.configure(state='disabled')
        manual_Coref_var.set(0)

CoRef_var.trace('w', activateCoRefOptions)

activateCoRefOptions()

def changed_filename(tracedInputFile):
    activateCoRefOptions()
GUI_util.input_main_dir_path.trace('w', lambda x, y, z: changed_filename(GUI_util.input_main_dir_path.get()))
# must trace on input_main_dir_path, rather than inputFilename,
#   because inputFilename is set BEFORE input_main_dir_path in GUI_util and it is not up-to-date

package_var.set('Stanford CoreNLP')
package_lb = tk.Label(window, text='SVO package')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               package_lb, True)
package_menu = tk.OptionMenu(window, package_var, 'spaCy','Stanford CoreNLP', 'Stanza', 'OpenIE (via Stanford CoreNLP)', 'SENNA')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 120, y_multiplier_integer,
                                               package_menu)

def activate_filter_dictionaries(*args):
    if not filter_subjects_var.get():
        subjects_dict_var.set('')
    else:
        subjects_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-actor-list.csv'))
    if not filter_verbs_var.get():
        verbs_dict_var.set('')
    else:
        verbs_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-action-list.csv'))
    if not filter_objects_var.get():
        objects_dict_var.set('')
    else:
        objects_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-actor-list.csv'))
filter_subjects_var.trace('w',activate_filter_dictionaries)
filter_verbs_var.trace('w',activate_filter_dictionaries)
filter_objects_var.trace('w',activate_filter_dictionaries)

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

filter_subjects_var.set(1)
subjects_checkbox = tk.Checkbutton(window, text='Filter Subject', variable=filter_subjects_var, onvalue=1, offvalue=0,
                                   command=lambda: getDictFile(filter_subjects_var, subjects_dict_var, filter_subjects_var.get(),
                                                               'Subject'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                   subjects_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate(),
                                   "The option for filtering subjects via WordNet for social actors is available only for the English language.\nBut you can choose a different special-purpose file.")

# setup a button to open Windows Explorer on the subjects file
openInputFile_subjects_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                          command=lambda: IO_files_util.openFile(window, subjects_dict_var.get()))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_S_dictionary, y_multiplier_integer,
                                               openInputFile_subjects_button, True, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate() + 140, "Open csv file containing SUBJECT filters")

lemmatize_subjects_checkbox = tk.Checkbutton(window, text='Lemmatize Subject', variable=lemmatize_subjects_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.lemmatize_S, y_multiplier_integer,
                                               lemmatize_subjects_checkbox, True)


filter_verbs_var.set(1)
verbs_checkbox = tk.Checkbutton(window, text='Filter Verb', variable=filter_verbs_var, onvalue=1, offvalue=0,
                                command=lambda: getDictFile(filter_verbs_var, verbs_dict_var, filter_verbs_var.get(), 'Verb'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer,
                                   verbs_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.SVO_2nd_column,
                                   "The option for filtering verbs for social actions via WordNet is available only for the English language.\nBut you can choose a different special-purpose file.")

# setup a button to open Windows Explorer on the verbs file
openInputFile_verbs_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                       command=lambda: IO_files_util.openFile(window, verbs_dict_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_V_dictionary, y_multiplier_integer,
                                               openInputFile_verbs_button, True, False, True, False, 90, GUI_IO_util.get_labels_x_coordinate() + 520, "Open csv file containing VERB filters")

lemmatize_verbs_var.set(1)
lemmatize_verbs_checkbox = tk.Checkbutton(window, text='Lemmatize Verb', variable=lemmatize_verbs_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.lemmatize_V, y_multiplier_integer,
                                               lemmatize_verbs_checkbox, True)

filter_objects_var.set(0)
objects_checkbox = tk.Checkbutton(window, text='Filter Object', variable=filter_objects_var, onvalue=1, offvalue=0,
                                  command=lambda: getDictFile(filter_objects_var, objects_dict_var, filter_objects_var.get(),
                                                              'Object'))
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_3rd_column, y_multiplier_integer,
                                   objects_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.SVO_2nd_column,
                                   "The option for filtering objects for social actors via WordNet is available only for the English language.\nBut you can choose a different special-purpose file.")

# setup a button to open Windows Explorer on the objects file
openInputFile_objects_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                         command=lambda: IO_files_util.openFile(window, objects_dict_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_O_dictionary, y_multiplier_integer,
                                               openInputFile_objects_button,True, False, True, False, 90, GUI_IO_util.open_O_dictionary, "Open csv file containing OBJECT filters")

lemmatize_objects_checkbox = tk.Checkbutton(window, text='Lemmatize Object', variable=lemmatize_objects_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.lemmatize_O, y_multiplier_integer,
                                               lemmatize_objects_checkbox)

subjects_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-actor-list.csv'))
subjects_dict_entry = tk.Entry(window, width=GUI_IO_util.dictionary_S_width, state="disabled", textvariable=subjects_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               subjects_dict_entry, True)

verbs_dict_var.set(os.path.join(GUI_IO_util.wordLists_libPath, 'social-action-list.csv'))
verbs_dict_entry = tk.Entry(window, width=GUI_IO_util.dictionary_V_width, state="disabled", textvariable=verbs_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer, verbs_dict_entry, True)

objects_dict_var.set('')
objects_dict_entry = tk.Entry(window, width=GUI_IO_util.dictionary_O_width, state="disabled", textvariable=objects_dict_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_3rd_column, y_multiplier_integer,
                                               objects_dict_entry)

gender_var.set(0)
gender_checkbox = tk.Checkbutton(window, text='S & O gender',
                                                variable=gender_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               gender_checkbox, True)

def activateGender(*args):

    if gender_var.get() and ((package_var.get() != 'Stanford CoreNLP') or (package_var.get() == 'Stanford CoreNLP' and 'English' not in str(language_list))):
        reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_gender,
                                     reminders_util.message_CoreNLP_gender, True)
gender_var.trace('w', activateGender)

activateGender()

quote_var.set(0)
quote_checkbox = tk.Checkbutton(window, text='S & O quote/speaker',
                                                variable=quote_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer,
                                               quote_checkbox, True)

def activateQuote(*args):
    if quote_var.get() and ((package_var.get() != 'Stanford CoreNLP') or (package_var.get() == 'Stanford CoreNLP' and 'English' not in str(language_list))):
        reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_quote,
                                     reminders_util.message_CoreNLP_quote, True)
quote_var.trace('w', activateQuote)

activateQuote()

SRL_var.set(0)
SRL_checkbox = tk.Checkbutton(window, text='SRL (Semantic Role Labeling)',
                                                variable=SRL_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_3rd_column, y_multiplier_integer,
                                               SRL_checkbox)
SRL_checkbox.configure(state='disabled')

gephi_var.set(1)
gephi_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in network graphs (via Gephi) ',
                                variable=gephi_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               gephi_checkbox, True)

wordcloud_var.set(1)
wordcloud_checkbox = tk.Checkbutton(window, text='Visualize SVO relations in wordcloud', variable=wordcloud_var,
                                    onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.SVO_2nd_column, y_multiplier_integer, wordcloud_checkbox,
                                               True)

google_earth_var.set(1)
google_earth_checkbox = tk.Checkbutton(window, text='Visualize Where in maps (via Google Maps & Google Earth Pro)',
                                       variable=google_earth_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 800, y_multiplier_integer,
                                               google_earth_checkbox)

def activateFilters(*args):

    if package_var.get()!='':
        subjects_checkbox.configure(state='normal')
        verbs_checkbox.configure(state='normal')
        objects_checkbox.configure(state='normal')
    if package_var.get()=='':
        filter_subjects_var.set(0)
        filter_verbs_var.set(0)
        filter_objects_var.set(0)

        activate_filter_dictionaries()

        subjects_checkbox.configure(state='disabled')
        verbs_checkbox.configure(state='disabled')
        objects_checkbox.configure(state='disabled')
        gephi_var.set(0)
        wordcloud_var.set(0)
        google_earth_var.set(0)
        gephi_checkbox.configure(state='disabled')
        wordcloud_checkbox.configure(state='disabled')
        google_earth_checkbox.configure(state='disabled')
    # SENNA does not produce geocodable locations
    if package_var.get()=='SENNA':
        google_earth_checkbox.configure(state='disabled')
        google_earth_var.set(0)

package_var.trace('w', activateFilters)

activateFilters()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'SVO extraction and visualization': 'TIPS_NLP_SVO extraction and visualization.pdf',
               'Stanford CoreNLP supported languages':'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP memory issues':'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'Stanford CoreNLP date extractor': 'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               'Stanford CoreNLP OpenIE': 'TIPS_NLP_Stanford CoreNLP OpenIE.pdf',
               'Stanford CoreNLP parser': 'TIPS_NLP_Stanford CoreNLP parser.pdf',
               'Stanford CoreNLP enhanced dependencies parser (SVO)':'TIPS_NLP_Stanford CoreNLP enhanced dependencies parser (SVO).pdf',
               'Stanford CoreNLP coreference resolution': "TIPS_NLP_Stanford CoreNLP coreference resolution.pdf",
               'CoNLL table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'SENNA': 'TIPS_NLP_SVO SENNA.pdf',
               "Google Earth Pro": "TIPS_NLP_Google Earth Pro.pdf",
               "Geocoding": "TIPS_NLP_Geocoding.pdf",
               "Geocoding: How to Improve Nominatim":"TIPS_NLP_Geocoding Nominatim.pdf",
               "Gephi network graphs": "TIPS_NLP_Gephi network graphs.pdf"}
               # 'Java download install run': 'TIPS_NLP_Java download install run.pdf'}
TIPS_options = 'utf-8 encoding', 'Excel - Enabling Macros', 'Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures', 'English Language Benchmarks', 'Things to do with words: Overall view', 'SVO extraction and visualization', 'Stanford CoreNLP supported languages', 'Stanford CoreNLP performance & accuracy','Stanford CoreNLP memory issues', 'Stanford CoreNLP date extractor', 'Stanford CoreNLP OpenIE', 'Stanford CoreNLP parser', 'Stanford CoreNLP enhanced dependencies parser (SVO)', 'Stanford CoreNLP coreference resolution', 'SENNA', 'CoNLL table',  'Google Earth Pro', 'Geocoding', 'Geocoding: How to Improve Nominatim', 'Gephi network graphs' #, 'Java download install run'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      "Please, select either a txt file to be analyzed and extract SVO triplets from it, or a csv file of previously extracted SVOs if all you want to do is to visualize the previously computed results." + GUI_IO_util.msg_openFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to run the Stanford CoreNLP coreference resolution annotator using the Neural Network approach.\n\nOnly pronominal, and not nominal, coreference resolution is implemented for four different types of PRONOUNS:\n   nominative: I, you, he/she, it, we, they;\n   possessive: my, mine, our(s), his/her(s), their, its, yours;\n   objective: me, you, him, her, it, them;\n   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves.\n\nPlease, BE PATIENT. Depending upon size and number of documents to be coreferenced the algorithm may take a long a time.\n\nIn INPUT the algorithm expects a single txt file or a directory of txt files.\n\nIn OUTPUT the algorithm will produce txt-format copies of the same input txt files but co-referenced."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to resolve manually cases of unresolved or wrongly resolved coreferences.\n\nThe option is not available when processing a directory of files. You can always use the 'Stanford_CoreNLP_coreference_main' GUI to\n   1. open a merged coreferenced file;\n   2. split merged coreferenced files.\n\nIf manual edit is selected, the script will also display a split-screen file for manual editing. On the left-hand side, pronouns cross-referenced by CoreNLP are tagged in YELLOW; pronouns NOT cross-referenced by CoreNLP are tagged in BLUE. On the right-hand side, pronouns cross-referenced by CoreNLP are tagged in RED, with the pronouns replaced by the referenced nouns.\n\nMANUAL EDITING REQUIRES A LOT OF MEMORY SINCE BOTH ORIGINAL AND CO-REFERENCED FILE ARE BROUGHT IN MEMORY. DEPENDING UPON FILE SIZES, YOU MAY NOT HAVE ENOUGH MEMORY FOR THIS STEP."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the NLP package to be used to extract SVOs from your corpus."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to filter all SVO extracted triplets for Subjects, Verbs, and Objects via dictionary filter files.\n\nFor instance, you can filter SVO by social actors and social action. In fact, the file \'social-actor-list.csv\', created via WordNet with keyword person and saved in the \'lib/wordLists\' subfolder, will be automatically loaded as the DEFAULT dictionary file (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly automatically loaded as the DEFAULT dictionary file for verbs.\n\nDictionary filter files can be created via WordNet and saved in the \'lib/wordLists\' subfolder. You can edit that list, adding and deleting entries at any time, using any text editor.\n\nWordNet produces thousands of entries for nouns and verbs. For more limited domains, you way want to pair down the number to a few hundred entries.\n\nThe Lemmatize options will produce lemmatized subjects, verbs, or objects. When verbs are lemmatized, the algorithm will aggregate the verbs into WordNet top synset verb categories."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The three widgets display the currently selected dictionary filter files for Subjects, Verbs, and Objects (Objects share the same file as Subjects and you may wish to change that).\n\nThe filter file social-actor-list, created via WordNet with person as keyword and saved in the \'lib/wordLists\' subfolder, will be automatically set as the DEFAULT filter for subjects (Press ESCape to clear selection); the file \'social-action-list.csv\' is similarly set as the DEFAULT dictionary file for verbs.\n\nThe widgets are disabled because you are not allowed to tamper with these values. If you wish to change a selected file, please tick the appropriate checkbox in the line above (e.g., Filter Subject) and you will be prompted to select a new file."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the S & O gender checkbox if you wish to run Stanford CoreNLP gender annotator to extract the gender (female, male) for every Subject and Object extracted by the SVO script.\n\n"
                                  "Tick the S & O quote/speaker checkbox if you wish to run Stanford CoreNLP quote annotator to extract the speaker involved in direct discourse for every Subject and Object extracted by the SVO script.\n\n"
                                  "THE GENDER AND QUOTE/SPEAKER ANNOTATORS ARE AVAILABLE FOR STANFORD CORENLP AND ENGLISH LANGUAGE ONLY.\n\n"
                                  "Tick the SRL checkbox if you wish to run Jinho Choi's SRL (Semantic Role Labeling) algorithm (https://github.com/emorynlp/elit/blob/main/docs/semantic_role_labeling.md). THE OPTION IS CURRENTLY DISABLED."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkboxes:\n\n  1. to visualize SVO relations in network graphs via Gephi;\n\n  2. to visualize SVO relations in a wordcloud (Subjects in red; Verbs in blue; Objects in green);\n\n  3. to use the NER location values to extract the WHERE part of the 5 Ws of narrative (Who, What, When, Where, Why); locations will be automatically geocoded (i.e., assigned latitude and longitude values) and visualized as maps via Google Earth Pro (as point map) and Google Maps (as heat map). ONLY THE LOCATIONS FOUND IN THE EXTRACTED SVO WILL BE DISPLAYED, NOT ALL THE LOCATIONS PRESENT IN THE TEXT.\n\nThe GIS algorithm uses Nominatim, rather than Google, as the default geocoder tool. If you wish to use Google for geocoding, please, use the GIS_main script.\n\nThe GIS mapping option is not available for SENNA or CoreNLP OpenIE."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)

# change the value of the readMe_message
readMe_message = "This set of Python 3 scripts extract automatically most of the elements of a story grammar and visualize the results in network graphs and GIS maps. A story grammar – basically, the 5Ws + H of modern journalism: Who, What, When, Where, Why, and How – provides the basic building blocks of narrative.\n\nThe set of scripts assembled here for this purpose ranges from testing for utf-8 compliance of the input text, to resolution for pronominal coreference, extraction of normalized NER dates (WHEN), visualized in various Excel charts, extraction, geocoding, and mapping in Google Earth Pro of NER locations.\n\nAt the heart of the SVO approach are several NLP packages to choose from. For passive sentences, the pipeline swaps S and O to transform the triplet into active voice. Thus, the WHO, WHAT (WHOM) are extracted from a text. Each component of the SVO triplet can be filtered via specific dictionaries (e.g., filtering for social actors and social actions, only). The set of SVO triplets are then visualized in dynamic network graphs (via Gephi).\n\nThe WHY and HOW of narrative are still beyond the reach of the current set of SVO scripts.\n\nIn INPUT the scripts expect a txt file to run utf-8 check, coreference resolution, date extraction, and CoreNLP. You can also enter a csv file, the output of a previous run with any of the NLP packages (_svo.csv/_SVO_Result) marked file) if all you want to do is to visualize results.\n\nIn OUTPUT, the scripts will produce several files (txt, csv, png, HTML, KML), depending upon the options selected."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName, False, package_display_area_value)

def warnUser(*args):
    reminders_util.checkReminder(config_filename, reminders_util.title_options_SVO_default,
                                 reminders_util.message_SVO_default, True)
    if GUI_util.input_main_dir_path.get() != '':
        reminders_util.checkReminder(config_filename, reminders_util.title_options_SVO_corpus,
                                     reminders_util.message_SVO_corpus, True)
GUI_util.input_main_dir_path.trace('w', warnUser)

# outside trace since it is not dependent on corpus type
reminders_util.checkReminder(config_filename, reminders_util.title_options_SVO_output,
                             reminders_util.message_SVO_output, True)

warnUser()


def activate_NLP_options(*args):
    global error, package, language_list, y_multiplier_integer

    # after update no display
    error, package, parsers, package_basics, language, package_display_area_value, package_display_area_value_new, encoding_var, memory_var, document_length_var, limit_sentence_length_var=GUI_util.handle_setup_options(y_multiplier_integer, scriptName)
    language_list = [language]
    package_var.set(package)
    if language!='English':
        filter_subjects_var.set(0)
        filter_verbs_var.set(0)
        filter_objects_var.set(0)
        subjects_dict_var.set('')
        verbs_dict_var.set('')
        objects_dict_var.set('')
    else:
        filter_subjects_var.set(1)
        filter_verbs_var.set(1)
        filter_objects_var.set(1)
        activate_filter_dictionaries()
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup next the default NLP package and language options.")
    call("python NLP_setup_package_language_main.py", shell=True)
    # this will display the correct hover-over info after the python call, in case options were changed
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()


GUI_util.window.mainloop()
