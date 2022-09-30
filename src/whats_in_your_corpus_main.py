#written by Roberto Franzosi August 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"what\'s in your corpus",['os','tkinter','subprocess'])==False:
    sys.exit(1)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_user_interface_util
import IO_files_util
import statistics_txt_util
import knowledge_graphs_WordNet_util
import Stanford_CoreNLP_util
import wordclouds_util
import GIS_pipeline_util
import topic_modeling_gensim_util
import topic_modeling_mallet_util
import reminders_util
import file_checker_util
import file_cleaner_util
import file_spell_checker_util
import abstract_concreteness_analysis_util

# RUN section ______________________________________________________________________________________________________________________________________________________

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_chart_output_checkbox.get(),
                            GUI_util.charts_dropdown_field.get(),
                            utf8_var.get(),
                            ASCII_var.get(),
                            corpus_statistics_var.get(),
                            corpus_statistics_options_menu_var.get(),
                            corpus_text_options_menu_var.get(),
                            wordclouds_var.get(),
                            open_wordclouds_GUI_var.get(),
                            topics_var.get(),
                            topics_Mallet_var.get(),
                            topics_Gensim_var.get(),
                            open_tm_GUI_var.get(),
                            language_var.get(),
                            memory_var.get(),
                            document_length_var.get(),
                            limit_sentence_length_var.get(),
                            what_else_var.get(),
                            what_else_menu_var.get(),
                            quote_var.get(),
                            GIS_var.get(),
                            open_GIS_GUI_var.get(),
                            SVO_var.get(),
                            open_SVO_GUI_var.get())

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename,inputDir, outputDir,
        openOutputFiles,
        createCharts,
        chartPackage,
        utf8_var,
        ASCII_var,
        corpus_statistics_var,
        corpus_statistics_options_menu_var,
        corpus_text_options_menu_var,
        wordclouds_var,
        open_wordclouds_GUI_var,
        topics_var,
        topics_Mallet_var,
        topics_Gensim_var,
        open_tm_GUI_var,
        language_var,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
        what_else_var,
        what_else_menu_var,
        single_quote,
        GIS_var,
        open_GIS_GUI_var,
        SVO_var,
        open_SVO_GUI_var):

    filesToOpen=[]
    openOutputFilesSV=openOutputFiles
    openOutputFiles=False # to make sure files are only opened at the end of this multi-tool script

    if (utf8_var==False and \
        ASCII_var == False and \
        corpus_statistics_var==False and \
        ((wordclouds_var == False) and (wordclouds_var == True and open_wordclouds_GUI_var==False)) and \
        ((topics_var==False) and (topics_var==True and topics_Mallet_var==False and topics_Gensim_var==False and open_tm_GUI_var==False)) and \
        what_else_var==False and \
        ((GIS_var == False) and (GIS_var == True and open_GIS_GUI_var == False)) and \
        ((SVO_var == False) and (SVO_var == True and open_SVO_GUI_var == False))):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    if (what_else_var and ('*' in what_else_menu_var or 'locations' in what_else_menu_var)) and (GIS_var and open_GIS_GUI_var == False):
        reminders_util.checkReminder(config_filename,
            reminders_util.title_options_GIS_redundancy,
            reminders_util.message_GIS_redundancy,
            True)

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='corpus', silent=True)
    if outputDir == '':
        return

    if utf8_var==True:
        file_checker_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles)

    if ASCII_var==True:
        result=file_cleaner_util.convert_quotes(GUI_util.window,inputFilename, inputDir)
        if result==False:
            return

    if corpus_statistics_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py')==False:
            return

        # compute corpus statistics: -------------------------------

        lemmatize = False
        stopwords = False

        if '*' in corpus_text_options_menu_var or 'stopwords' in corpus_text_options_menu_var:
            stopwords = True
        if '*' in corpus_text_options_menu_var or 'Lemmatize' in corpus_text_options_menu_var:
            lemmatize=True

        if '*' in corpus_statistics_options_menu_var or 'statistics' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.compute_corpus_statistics(window, inputFilename, inputDir, outputDir, False,
                                  createCharts, chartPackage,
                                  stopwords, lemmatize)
            # append because output contains a list of files rather than a single file string
            if output!=None:
                filesToOpen.append(output)

        # compute ngrams ----------------------------------------------------

        # if '*' in corpus_statistics_options_menu_var or 'grams' in corpus_statistics_options_menu_var:
        #     excludePunctuation = True
        #     n_grams_size = 3
        #     frequency = False
        #     normalize = False
        #
        #     statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
        #                                                       outputDir, n_grams_size, normalize, excludePunctuation, 1,
        #                                                       frequency, openOutputFiles,
        #                                                       createCharts, chartPackage)

        # compute sentence length ----------------------------------------------------

        if 'sentence length' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.compute_sentence_length(config_filename, inputFilename,inputDir, outputDir, createCharts, chartPackage)

            if output!=None:
                filesToOpen.append(output)

        # compute line length ----------------------------------------------------

        if 'line length' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.compute_line_length(window, config_filename, inputFilename, inputDir, outputDir, False,
                                                   createCharts, chartPackage)
            if output!=None:
                filesToOpen.append(output)

        if '*' == corpus_statistics_options_menu_var:
            output = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createCharts, chartPackage)
            if output != None:
                filesToOpen.append(output)
        if '*' == corpus_statistics_options_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createCharts, chartPackage)
            if output != None:
                filesToOpen.append(output)
        if 'detection' in corpus_statistics_options_menu_var:
            output = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir,
                                                                         openOutputFiles, createCharts, chartPackage)
            if output != None:
                filesToOpen.append(output)
        if 'capital' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir,
                                                                   openOutputFiles, createCharts, chartPackage,corpus_statistics_options_menu_var)
            if output != None:
                filesToOpen.append(output)
        if 'Short' in corpus_statistics_options_menu_var:
            output=statistics_txt_util.process_words(window,inputFilename,inputDir, outputDir, openOutputFiles, createCharts, chartPackage,corpus_statistics_options_menu_var)
            if output != None:
                filesToOpen.append(output)

        if 'Vowel' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.process_words(window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,corpus_statistics_options_menu_var)
            if output != None:
                filesToOpen.append(output)

        if 'Punctuation' in corpus_statistics_options_menu_var:
            output=statistics_txt_util.process_words(window,inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage,corpus_statistics_options_menu_var)
            if output != None:
                filesToOpen.append(output)

        if '*' == corpus_statistics_options_menu_var or 'Yule' in corpus_statistics_options_menu_var:
            filesToOpen=statistics_txt_util.yule(window, inputFilename, inputDir, outputDir)
            if output != None:
                filesToOpen.append(output)

        if '*' == corpus_statistics_options_menu_var or 'Unusual' in corpus_statistics_options_menu_var:
            output=file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir, False, createCharts, chartPackage)
            if output != None:
                filesToOpen.append(output)
        if '*' == corpus_statistics_options_menu_var or 'Abstract' in corpus_statistics_options_menu_var:
            # ABSTRACT/CONCRETENESS _______________________________________________________
            output = abstract_concreteness_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, processType='')
            if output != None:
                filesToOpen.append(output)

        if '*' in corpus_statistics_options_menu_var or 'complexity' in corpus_statistics_options_menu_var:
            output = statistics_txt_util.compute_sentence_complexity(GUI_util.window, inputFilename,
                                                                     inputDir, outputDir,
                                                                     openOutputFiles, createCharts, chartPackage)
            if output != None:
                filesToOpen.append(output)


        # compute ngrams ----------------------------------------------------
        if '*' == corpus_statistics_options_menu_var or 'grams' in corpus_statistics_options_menu_var:
            ngramType = 1
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            ngramsNumber=3
            frequency=0
            normalize = False
            excludePunctuation = False
            bySentenceIndex_var=False

            # n-grams
            output = statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, ngramsNumber, normalize,
                                                              excludePunctuation, ngramType, frequency,
                                                              openOutputFiles, createCharts, chartPackage,
                                                              bySentenceIndex_var)
            if output != None:
                filesToOpen.append(output)

    # wordclouds --------------------------------------------------------------

    if wordclouds_var==True:
        if open_wordclouds_GUI_var == True:
            call("python wordclouds_main.py", shell=True)
        else:
            # run with all default values;
            use_contour_only = False
            max_words = 100
            font = 'Default'
            prefer_horizontal = .9
            lemmatize = False
            exclude_stopwords = True
            exclude_punctuation = True
            lowercase = False
            differentPOS_differentColors = False
            differentColumns_differentColors = False
            csvField_color_list = []
            doNotListIndividualFiles = True
            collocation = True

            output=wordclouds_util.python_wordCloud(inputFilename, inputDir, outputDir, selectedImage="", use_contour_only=use_contour_only, prefer_horizontal=prefer_horizontal, font=font, max_words=max_words, lemmatize=lemmatize, exclude_stopwords=exclude_stopwords, exclude_punctuation=exclude_punctuation, lowercase=lowercase, differentPOS_differentColors=differentPOS_differentColors, differentColumns_differentColors=differentColumns_differentColors, csvField_color_list=csvField_color_list, doNotListIndividualFiles=doNotListIndividualFiles,openOutputFiles=False, collocation=collocation)
            if output != None:
                filesToOpen.append(output)

# topic modeling ---------------------------------------------------------------------------------
    if topics_var==True:
        outputDir_TM = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='topic_modeling',
                                                           silent=True)
        if outputDir_TM == '':
            return
        if topics_Gensim_var==True:
            if IO_libraries_util.check_inputPythonJavaProgramFile('topic_modeling_gensim_main.py')==False:
                return
            routine_options = reminders_util.getReminders_list(config_filename)
            reminders_util.checkReminder(config_filename,
                                         reminders_util.title_options_topic_modeling_gensim,
                                         reminders_util.message_topic_modeling_gensim,
                                         True)
            routine_options = reminders_util.getReminders_list(config_filename)

            if open_tm_GUI_var == True:
                call("python topic_modeling_gensim_main.py", shell=True)
            else:
                if language_var != 'English':
                    reminders_util.checkReminder(
                        config_filename,
                        reminders_util.title_options_English_language_Gensim,
                        reminders_util.message_English_language_Gensim,
                        True)
                else:
                    # run with all default values; do not run MALLET
                    output = topic_modeling_gensim_util.run_Gensim(GUI_util.window, inputDir, outputDir_TM, num_topics=20,
                                                          remove_stopwords_var=1, lemmatize=1, nounsOnly=0, run_Mallet=False, openOutputFiles=openOutputFiles,createCharts=createCharts, chartPackage=chartPackage)
                    if output!=None:
                        filesToOpen.append(output)

        if topics_Mallet_var==True:
            if open_tm_GUI_var == True:
                call("python topic_modeling_mallet_main.py", shell=True)
            else:
                if language_var != 'English':
                    reminders_util.checkReminder(
                        config_filename,
                        reminders_util.title_options_English_language_MALLET,
                        reminders_util.message_English_language_MALLET,
                        True)
                else:
                    # running with default values
                    output = topic_modeling_mallet_util.run(inputDir, outputDir_TM, openOutputFiles=openOutputFiles, createCharts=createCharts, chartPackage=chartPackage, OptimizeInterval=True, numTopics=20)
                    if output != None:
                        filesToOpen.append(output)

#  what else ---------------------------------------------------------------------------------
    nouns_var=False
    verbs_var=False
    dialogues_var = False
    people_organizations_var = False
    gender_var = False
    times_var = False
    locations_var = False
    sentiments_var = False
    nature_var = False

    if what_else_var and what_else_menu_var == '*':
        nouns_var = True
        verbs_var = True

    if 'noun' in what_else_menu_var.lower():
        nouns_var = True
    if 'verb' in what_else_menu_var.lower():
        verbs_var = True
    if 'dialogue' in what_else_menu_var.lower():
        dialogues_var = True
    if 'people' in what_else_menu_var.lower():
        people_organizations_var = True
    if 'male' in what_else_menu_var.lower():
        gender_var = True
    if 'date & time' in what_else_menu_var.lower():
        times_var = True
    if 'location' in what_else_menu_var.lower():
        locations_var=True
    if 'sentiments' in what_else_menu_var.lower():
        sentiments_var=True
    if 'nature' in what_else_menu_var.lower():
        nature_var=True

    inputFilenameSV=inputFilename #inputFilename value is changed in the WordNet function

    if (what_else_var and what_else_menu_var == '*') or nouns_var==True or verbs_var==True or people_organizations_var==True or gender_var==True or dialogues_var==True or times_var==True or locations_var==True or sentiments_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py')==False:
            return
        if what_else_var and what_else_menu_var == '*':
            outputDir_what_else = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                                  label='what_else',
                                                                  silent=True)
        if nouns_var or verbs_var:
            if nouns_var or verbs_var or what_else_menu_var == '*':
                WordNetDir, missing_external_software = IO_libraries_util.get_external_software_dir('whats_in_your_corpus', 'WordNet')
                if WordNetDir == None:
                    return
                if language_var != 'English':
                    reminders_util.checkReminder(
                        config_filename,
                        reminders_util.title_options_English_language_WordNet,
                        reminders_util.message_English_language_WordNet,
                        True)
                else:
                    annotator = ['POS']
                    files = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                outputDir_what_else, openOutputFiles, createCharts, chartPackage,
                                                annotator, False, language_var, memory_var, document_length_var, limit_sentence_length_var)
                    if len(files) > 0:
                            noun_verb=''
                            if verbs_var == True:
                                inputFilename = files[0] # Verbs but... double check
                                if "verbs" in inputFilename.lower():
                                    noun_verb='VERB'
                                else:
                                    return
                                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir_what_else, config_filename, noun_verb,
                                                                            openOutputFiles, createCharts, chartPackage, language_var)
                                if output!=None:
                                    filesToOpen.append(output)

                            if nouns_var == True:
                                inputFilename = files[1]  # Nouns but... double check
                                if "nouns" in inputFilename.lower():
                                    noun_verb='NOUN'
                                else:
                                    return
                                output = knowledge_graphs_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir_what_else, config_filename, noun_verb,
                                                                            openOutputFiles, createCharts, chartPackage, language_var)
                                if output!=None:
                                    filesToOpen.append(output)
                    else:
                        if (what_else_var and what_else_menu_var == '*'):
                            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Missing WordNet',
                                                               'The analysis of \'What else is in your corpus\' will skip the nouns and verbs classification requiring WordNet and will continue with all other CoreNLP annotators')

        if what_else_var and what_else_menu_var == '*':
            inputFilename=inputFilenameSV

            annotator_list = ['NER', 'gender', 'quote', 'normalized-date']
            NER_list=['PERSON','ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator_list, False,
                                                                      language_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                      NERs=NER_list)
            if output != None:
                filesToOpen.append(output)

        if people_organizations_var == True:
            annotator = 'NER'
            NER_list=['PERSON','ORGANIZATION']

            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator, False,
                                                                      language_var, memory_var, document_length_var,
                                                                      limit_sentence_length_var,
                                                                      NERs=NER_list)
            if output != None:
                filesToOpen.append(output)

        if gender_var == True:
            annotator = 'gender'
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator, False, language_var, memory_var, document_length_var, limit_sentence_length_var)

            if output != None:
                filesToOpen.append(output)

        if dialogues_var==True:
            annotator = 'quote'
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator, False, language_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                      single_quote_var = single_quote)
            if output != None:
                filesToOpen.append(output)

        if times_var==True:
            annotator='normalized-date'
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir_what_else,
                        openOutputFiles, createCharts, chartPackage,
                        annotator, False, language_var, memory_var, document_length_var, limit_sentence_length_var)
            if output != None:
                filesToOpen.append(output)

        if locations_var == True:
            annotator = 'NER'
            NER_list = ['CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']

            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator, False,
                                                                      language_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                      NERs=NER_list)
            if output != None:
                filesToOpen.append(output)

        if sentiments_var == True:
            annotator = 'sentiment'
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      createCharts, chartPackage,
                                                                      annotator, False,
                                                                      memory_var, document_length_var,
                                                                      limit_sentence_length_var)
            if output != None:
                filesToOpen.append(output)
# GIS --------------------------------------------------------------------------------
    if GIS_var==True:
        if open_GIS_GUI_var == True:
            call("python GIS_main.py", shell=True)
        else:
            # run with all default values;
            # checking for txt: NER=='LOCATION', provide a csv output with column: [Locations]
            NERs = ['COUNTRY', 'STATE_OR_PROVINCE', 'CITY', 'LOCATION']
            extract_date_from_text_var = False
            extract_date_from_filename_var = False
            date_format = ''
            date_separator_var = ''
            date_position_var = 0
            locations = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                         outputDir_what_else, openOutputFiles,
                                                                         createCharts, chartPackage, 'NER',
                                                                         False,
                                                                         language_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                         NERs=NERs,
                                                                         extract_date_from_text_var=extract_date_from_text_var,
                                                                         extract_date_from_filename_var=extract_date_from_filename_var,
                                                                         date_format=date_format,
                                                                         date_separator_var=date_separator_var,
                                                                         date_position_var=date_position_var)

            if len(locations) == 0:
                mb.showwarning("No locations",
                               "There are no NER locations to be geocoded and mapped in the selected input txt file.\n\nPlease, select a different txt file and try again.")
                return
            else:
                NER_outputFilename = locations[0]

        geocoder = 'Nominatim'
        GIS_package_var='Google Earth Pro & Google Maps'
        datePresent = False
        country_bias = ''
        box_tuple = ''
        restrict_var = False
        locationColumnName = 'Word'
        encoding_var = 'utf-8'

        # create a subdirectory of the output directory
        outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir_what_else, label='GIS',
                                                           silent=True)
        if outputDir_temp == '':
            return

        # locationColumnName where locations to be geocoded (or geocoded) are stored in the csv file;
        #   any changes to the columns will result in error
        out_file = GIS_pipeline_util.GIS_pipeline(GUI_util.window, config_filename,
                        NER_outputFilename,inputDir, outputDir_temp,
                        geocoder, GIS_package_var, createCharts, chartPackage,
                        datePresent,
                        country_bias,
                        box_tuple,
                        restrict_var,
                        locationColumnName,
                        encoding_var,
                        0, 1, [''], [''],# group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                        ['Pushpins'], ['red'], # icon_var_list, specific_icon_var_list,
                        [0], ['1'], [0], [''], # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                        [1],[1]) # bold_var_list, italic_var_list)

        if out_file != None:
            if len(out_file) > 0:
                filesToOpen.extend(out_file)

# SVO ------------------------------------------------------------------------------------

    if SVO_var==True:
        outputDir_SVO = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                               label='SVO',
                                                               silent=True)
        if outputDir_SVO == '':
            return

        outputLocations = []
        if open_SVO_GUI_var == True:
            call("python SVO_main.py", shell=True)
        else:
            # run with all default values;
            location_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                        'CoreNLP_SVO_LOCATIONS')
            gender_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                      'CoreNLP_SVO_gender')
            quote_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                     'CoreNLP_SVO_quote')
            outputLocations.append(location_filename)
            extract_date_from_text_var = False
            extract_date_from_filename_var = False
            date_format_var = ''
            date_separator_var = ''
            date_position_var = 0
            google_earth_var = True
            location_filename = location_filename
            gender_var = True
            gender_filename = gender_filename
            quote_var = True
            quote_filename = quote_filename
            output = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                               outputDir_SVO, openOutputFiles,
                                                                               createCharts, chartPackage,
                                                                               'SVO', False,
                                                                               language_var,
                                                                               memory_var=memory_var,
                                                                               document_length_var=document_length_var,
                                                                               limit_sentence_length_var=limit_sentence_length_var,
                                                                               extract_date_from_text_var=extract_date_from_text_var,
                                                                               extract_date_from_filename_var=extract_date_from_filename_var,
                                                                               date_format=date_format_var,
                                                                               date_separator_var=date_separator_var,
                                                                               date_position_var=date_position_var,
                                                                               google_earth_var=google_earth_var,
                                                                               location_filename=location_filename,
                                                                               gender_var=gender_var,
                                                                               gender_filename=gender_filename,
                                                                               quote_var=quote_var,
                                                                               quote_filename=quote_filename)
            if output != None:
                filesToOpen.append(output)

    openOutputFiles=openOutputFilesSV
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=590, # height at brief display
                             GUI_height_full=630, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for a Sweeping View of Your Corpus (Single/Multiple Document(s)) - A Pipeline'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

utf8_var= tk.IntVar()
ASCII_var= tk.IntVar()
corpus_statistics_var= tk.IntVar()
corpus_statistics_options_menu_var = tk.StringVar()
corpus_text_options_menu_var = tk.StringVar()
wordclouds_var = tk.IntVar()
open_wordclouds_GUI_var = tk.IntVar()
topics_var= tk.IntVar()
topics_Mallet_var= tk.IntVar()
topics_Gensim_var= tk.IntVar()
open_tm_GUI_var= tk.IntVar()

language_var= tk.StringVar()
memory_var = tk.IntVar()
nouns_var= tk.IntVar()
verbs_var= tk.IntVar()

what_else_var= tk.IntVar()
what_else_menu_var= tk.StringVar()
people_organizations_var= tk.IntVar()
locations_var= tk.IntVar()
times_var= tk.IntVar()
dialogues_var= tk.IntVar()
nature_var= tk.IntVar()
quote_var = tk.IntVar()
GIS_var = tk.IntVar()
SVO_var = tk.IntVar()
open_GIS_GUI_var = tk.IntVar()
open_SVO_GUI_var = tk.IntVar()

y_multiplier_integer_SV=0 # used to set the quote_var widget on the proper GUI line

def clear(e):
    corpus_statistics_var.set(1)
    corpus_statistics_options_menu_var.set('*')
    corpus_text_options_menu_var.set('*')
    what_else_var.set(1)
    what_else_menu_var.set('*')
    quote_checkbox.place_forget()  # invisible
    wordclouds_var.set(1)
    open_wordclouds_GUI_var.set(0)
    open_wordclouds_GUI_checkbox.configure(state='normal')
    GIS_var.set(1)
    open_GIS_GUI_var.set(0)
    open_GIS_GUI_checkbox.configure(state='normal')
    SVO_var.set(1)
    open_SVO_GUI_var.set(0)
    open_SVO_GUI_checkbox.configure(state='normal')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

utf8_var.set(1)
utf8_checkbox = tk.Checkbutton(window, text='Check input document(s) for utf-8 encoding', variable=utf8_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,utf8_checkbox)

ASCII_var.set(1)
ASCII_checkbox = tk.Checkbutton(window, text='Convert non-ASCII apostrophes & quotes and % to percent', variable=ASCII_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,ASCII_checkbox)

corpus_statistics_var.set(1)
corpus_statistics_checkbox = tk.Checkbutton(window,text="Document(s) linguistic features", variable=corpus_statistics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,corpus_statistics_checkbox,True)

corpus_statistics_options_menu_var.set('*')
corpus_statistics_options_menu_lb = tk.Label(window, text='NLP tools options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,corpus_statistics_options_menu_lb,True)
corpus_statistics_options_menu = tk.OptionMenu(window, corpus_statistics_options_menu_var,
                                               '*',
                                               'Compute statistics (sentences, words, syllables)',
                                               'Compute n-grams'
                                               'Compute Hapax legomena (once-occurring words)',
                                               'Compute sentence length',
                                               'Compute line length',
                                               '',
                                               'Abstract/concrete vocabulary',
                                               'Vocabulary richness (word type/token ratio or Yule’s K)',
                                               'Sentence complexity',
                                               'Punctuation as figures of pathos (? !)',
                                               'Short words (<4 characters)',
                                               'Vowel words',
                                               'Words with capital initial (proper nouns)',
                                               'Unusual words (via NLTK)'
                                               )
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+570,y_multiplier_integer,corpus_statistics_options_menu, True)

corpus_text_options_menu_var.set('*')
corpus_options_menu_lb = tk.Label(window, text='Text options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 680,y_multiplier_integer,corpus_options_menu_lb,True)
corpus_options_menu = tk.OptionMenu(window, corpus_text_options_menu_var, '*','Lemmatize words', 'Exclude stopwords & punctuation')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 780,y_multiplier_integer,corpus_options_menu)

wordclouds_var.set(1)
wordclouds_checkbox = tk.Checkbutton(window,text="Wordclouds", variable=wordclouds_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,wordclouds_checkbox, True)

open_wordclouds_GUI_var.set(0) # wordclouds GUI
open_wordclouds_GUI_checkbox = tk.Checkbutton(window,text="Open wordclouds GUI", state='disabled', variable=open_wordclouds_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,open_wordclouds_GUI_checkbox)

def activate_wordclouds_GUI(*args):
    if wordclouds_var.get():
        open_wordclouds_GUI_checkbox.configure(state='normal')
    else:
        open_wordclouds_GUI_checkbox.configure(state='disabled')
wordclouds_var.trace('w', activate_wordclouds_GUI)

activate_wordclouds_GUI()

topics_checkbox = tk.Checkbutton(window,text="What are the topics? (Topic modeling)", variable=topics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,topics_checkbox,True)

def changed_filename(*args):
    if inputFilename.get()!='':
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_topic_modeling,
                                     reminders_util.message_topic_modeling,
                                     True)
        topics_var.set(0)
        topics_checkbox.configure(state='disabled')
    else:
        topics_var.set(1)
        topics_checkbox.configure(state='normal')
inputFilename.trace('w',changed_filename)
# input_main_dir_path.trace('w',changed_filename)

topics_Mallet_var.set(0)
topics_Mallet_checkbox = tk.Checkbutton(window,text="via MALLET", variable=topics_Mallet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,topics_Mallet_checkbox,True)

topics_Gensim_var.set(1)
topics_Gensim_checkbox = tk.Checkbutton(window,text="via Gensim", variable=topics_Gensim_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+570,y_multiplier_integer,topics_Gensim_checkbox,True)

open_tm_GUI_var.set(0) # topic modeling GUI
open_GUI_checkbox = tk.Checkbutton(window,text="Open Gensim/MALLET GUI", variable=open_tm_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+700,y_multiplier_integer,open_GUI_checkbox)

def activate_topics(*args):
    if topics_var.get()==True:
        topics_Mallet_checkbox.configure(state='normal')
        topics_Gensim_checkbox.configure(state='normal')
        open_GUI_checkbox.configure(state='normal')
    else:
        topics_Mallet_checkbox.configure(state='disabled')
        topics_Gensim_checkbox.configure(state='disabled')
        open_GUI_checkbox.configure(state='disabled')
topics_var.trace('w',activate_topics)

def activate_Mallet(*args):
    if topics_var.get()==True:
        topics_Gensim_var.set(0)
        if topics_Mallet_var.get()==True:
            open_GUI_checkbox.configure(state='normal')
            topics_Gensim_checkbox.configure(state='disabled')
            open_GUI_checkbox.configure(state='normal')
        else:
            open_tm_GUI_var.set(0)
            topics_Gensim_checkbox.configure(state='normal')
            open_GUI_checkbox.configure(state='disabled')
topics_Mallet_var.trace('w',activate_Mallet)

def activate_Gensim(*args):
    if topics_var.get()==True:
        if topics_Gensim_var.get()==True:
            open_GUI_checkbox.configure(state='normal')
            topics_Mallet_checkbox.configure(state='disabled')
            open_GUI_checkbox.configure(state='normal')
        else:
            open_GUI_checkbox.configure(state='disabled')
            topics_Mallet_checkbox.configure(state='normal')
            open_GUI_checkbox.configure(state='disabled')
topics_Gensim_var.trace('w',activate_Gensim)

def activate_allOptions(*args):
    if open_tm_GUI_var.get()==True:
        corpus_statistics_var.set(0)
        corpus_statistics_checkbox.configure(state='disabled')
        what_else_var.set(0)
        topics_Mallet_checkbox.configure(state='disabled')
        topics_Gensim_checkbox.configure(state='disabled')
        what_else_checkbox.configure(state='disabled')
    else:
        corpus_statistics_var.set(1)
        corpus_statistics_checkbox.configure(state='normal')
        what_else_var.set(1)
        topics_Mallet_checkbox.configure(state='normal')
        topics_Gensim_checkbox.configure(state='normal')
        what_else_checkbox.configure(state='normal')
open_tm_GUI_var.trace('w',activate_allOptions)

# language options
language_var_lb = tk.Label(window, text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               language_var_lb, True)

language_var.set('English')
language_menu = tk.OptionMenu(window, language_var, 'Arabic','Chinese', 'English', 'German','Hungarian','Italian','Spanish')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+70,
                                               y_multiplier_integer, language_menu, True)
# memory options
memory_var_lb = tk.Label(window, text='Memory')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+210, y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 280, y_multiplier_integer,
                                               memory_var, True)

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+210, y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+330, y_multiplier_integer,
                                               document_length_var,True)

limit_sentence_length_var_lb = tk.Label(window, text='Limit sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 530, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 680, y_multiplier_integer,
                                               limit_sentence_length_var)

what_else_var.set(1)
what_else_checkbox = tk.Checkbutton(window,text="What else is in your document(s)? (via Stanford CoreNLP and WordNet)", variable=what_else_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,what_else_checkbox,True)

what_else_menu_var.set('*')
what_else_menu = tk.OptionMenu(window,  what_else_menu_var, '*', 'Dialogues (CoreNLP Neural Network)','Noun and verb classes (CoreNLP NER & WordNet)', 'People & organizations (CoreNLP NER)', 'Females & males (CoreNLP Neural Network)',
                               'References to date & time (CoreNLP normalized NER dates)',
                               'References to geographical locations (CoreNLP NER)',
                               'References to nature (CoreNLP & WordNet)',
                               'Sentiments expressed (CoreNLP)')
what_else_menu.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate() + 440, y_multiplier_integer,
                                               what_else_menu, True)

# set value of current GUI line to display correctly the single quotes widget
y_multiplier_integer_SV = y_multiplier_integer

quote_checkbox = tk.Checkbutton(window, text='Include single quotes',
                                       variable=quote_var,
                                       onvalue=1, offvalue=0)
def activate_what_else_menu(*args):
    global y_multiplier_integer, y_multiplier_integer_SV
    if what_else_var.get()==True:
        what_else_menu.config(state='normal')
        if "*" in what_else_menu_var.get() or "Dialogues" in what_else_menu_var.get():
            if y_multiplier_integer_SV!=0:
                y_multiplier_integer = y_multiplier_integer_SV
            quote_var.set(0)
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 500,
                                                           y_multiplier_integer,
                                                           quote_checkbox)
            quote_checkbox.configure(state='normal')
        else:
            quote_checkbox.place_forget()  # invisible
    else:
        what_else_menu.config(state='disabled')
        quote_checkbox.place_forget()  # invisible

what_else_var.trace('w',activate_what_else_menu)
what_else_menu_var.trace('w',activate_what_else_menu)

activate_what_else_menu()

GIS_var.set(1)
GIS_checkbox = tk.Checkbutton(window,text="GIS (Geographic Information System) pipeline", variable=GIS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,GIS_checkbox, True)

open_GIS_GUI_var.set(0) # GIS GUI
open_GIS_GUI_checkbox = tk.Checkbutton(window,text="Open GIS GUI", state='disabled', variable=open_GIS_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,open_GIS_GUI_checkbox)

def activate_GIS_GUI(*args):
    if GIS_var.get():
        open_GIS_GUI_checkbox.configure(state='normal')
    else:
        open_GIS_GUI_checkbox.configure(state='disabled')
        open_GIS_GUI_var.set(0)
GIS_var.trace('w', activate_GIS_GUI)

activate_GIS_GUI()

SVO_var.set(1)
SVO_checkbox = tk.Checkbutton(window,text="SVO (Subject-Verb-Object) pipeline", variable=SVO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SVO_checkbox, True)

open_SVO_GUI_var.set(0) # SVO GUI
open_SVO_GUI_checkbox = tk.Checkbutton(window,text="Open SVO GUI", state='disabled', variable=open_SVO_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+440,y_multiplier_integer,open_SVO_GUI_checkbox)

def activate_SVO_GUI(*args):
    if SVO_var.get():
        open_SVO_GUI_checkbox.configure(state='normal')
    else:
        open_SVO_GUI_checkbox.configure(state='disabled')
        open_SVO_GUI_var.set(0)
SVO_var.trace('w', activate_SVO_GUI)

activate_SVO_GUI()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf', 'Lemmas & stopwords':'TIPS_NLP_NLP Basic Language.pdf', 'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf', 'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf', 'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf', 'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf','N-Grams (word & character)':'TIPS_NLP_Ngram (word & character).pdf','Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf','NLP Suite Ngram and Word Co-Occurrence Viewer':'TIPS_NLP_Ngram and Word Co-Occurrence Viewer.pdf','Style analysis':'TIPS_NLP_Style analysis.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Style analysis':'TIPS_NLP_Style analysis.pdf','Wordclouds':'TIPS_NLP_Wordclouds Visualizing word clouds.pdf','Topic modeling':'TIPS_NLP_Topic modeling.pdf','Topic modeling and corpus size':'TIPS_NLP_Topic modeling and corpus size.pdf','Topic modeling (Gensim)':'TIPS_NLP_Topic modeling Gensim.pdf','Topic modeling (Mallet)':'TIPS_NLP_Topic modeling Mallet.pdf','Mallet installation':'TIPS_NLP_Topic modeling Mallet installation.pdf','NER (Named Entity Recognition)':'TIPS_NLP_NER (Named Entity Recognition).pdf','The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf','Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf','Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',"Stanford CoreNLP Gender annotator":"TIPS_NLP_Gender annotator.pdf",'GIS (Geographic Information System): Mapping Locations':'TIPS_NLP_GIS (Geographic Information System).pdf','SVO extraction and visualization':'TIPS_NLP_SVO extraction and visualization.pdf','Stanford CoreNLP enhanced dependencies parser (SVO)':'TIPS_NLP_Stanford CoreNLP enhanced dependencies parser (SVO).pdf','WordNet':'TIPS_NLP_WordNet.pdf'}
TIPS_options='Text encoding (utf-8)','Excel - Enabling Macros', 'csv files - Problems & solutions', 'Statistical measures', 'English Language Benchmarks', 'Things to do with words: Overall view', 'Lemmas & stopwords', 'N-Grams (word & character)','Google Ngram Viewer','NLP Suite Ngram and Word Co-Occurrence Viewer','Style analysis','Wordclouds','Topic modeling','Topic modeling and corpus size','Topic modeling (Gensim)','Topic modeling (Mallet)','Mallet installation','NER (Named Entity Recognition)','The world of emotions and sentiments','Sentiment analysis','Stanford CoreNLP date extractor (NER normalized date)','Stanford CoreNLP Gender annotator','GIS (Geographic Information System): Mapping Locations','SVO extraction and visualization','Stanford CoreNLP enhanced dependencies parser (SVO)','WordNet'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to check your input corpus for utf-8 encoding.\n   Non utf-8 compliant texts are likely to lead to code breakdown.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to convert non-ASCII apostrophes & quotes and % to percent.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdon of Stanford CoreNLP.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to compute corpus statistics: number of documents, number of sentences and words, word n-grams by document.\n\nFOR N-GRAMS, THERE IS A SEPARATE SCRIPT WITH MORE GENERAL OPTIONS: NGrams_CoOccurrences_Viewer_main.\n\nThe * option will lemmatize words and exclude stopwords and punctuation. IT WILL COMPUTE BASIC WORD N-GRAMS. IT WILL NOT COMPUTE LINE LENGTH. YOU WOULD NEED TO RUN THE LINE LENGTH OPTION SEPARATELY.\n\nLine length in a typical document mostly depends upon typesetting formats. Only for poetry or music lyrics does the line-length measure make sense; in fact, you could use the option the detect those documents in your corpus characterized by different typesetting formats (.g., a poem document among narrative documents).\n\nRUN THE LINE-LENGTH OPTION ONLY IF IT MAKES SENSE FOR YOUR CORPUS.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to draw wordclouds using the Wordcloud Python script.\n\nThe wordclouds function in this GUI is based on the following set of default options: \
            \n  do not use images \
            \n  set max number of words to 100 \
            \n  use default font \
            \n  do NOT use horizontal layout \
            \n  do NOT lemmatize \
            \n  exclude stopwords \
            \n  exclude punctuation \
            \n  do NOT convert to lowercase \
            \n  do NOT use different colors for different POS tags \
            \n  do NOT use different colors for different columns \
            \n  process together common MWE (e.g, South Carolina) \
            \n  do not list individual files when processing a directory \
            \n\nTo set different options, use the wordclouds GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the Mallet or Gensim checkboxes to run run LDA Topic Modeling to find out the main topics of your corpus.\n\nTick the \'open GUI\' checkbox to open the specialized Gensim topic modeling GUI that offers more options. Mallet can only be run via its GUI")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the language to be used: English, Arabic, Chinese, German, Hungarian, Italian, or Spanish.\n\nNot all annotators are available for all languages, in fact, most are not. Please, read the TIPS file TIPS_NLP_Stanford CoreNLP supported languages.pdf.\n\nThe Stanford CoreNLP performance is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default = 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the value when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to analyze your corpus for a variety of tools. Select the default \'*\' to run all options. Allternatively, select the specific option to run.\n\nThe NLP tools will allow you to answer questions such as:\n  1. Are there dialogues in your corpus? The CoreNLP QUOTE annotator extracts quotes from text and attributes the quote to the speaker. The default CoreNLP parameter is DOUBLE quotes. If you want to process both DOUBLE and SINGLE quotes, plase tick the checkbox 'Include single quotes.'\n  .2 Do nouns and verbs cluster in specific aggregates (e.g., communication, movement)?\n  3. Does the corpus contain references to people (by gender) and organizations?\n  4.  References to dates and times?\n  5. References to geographical locations that could be placed on a map?\n  6. References to nature (e.g., weather, seasons, animals, plants)?")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to run the GIS pipeline to extract locations from your input document(s) and map them in Google Earth Pro and Google Maps.\n\nThe GIS function in this GUI is based on the following default options:" \
            "\n  use Nominatim for geocoding "\
            "\n  use Google Earth Pro & Google Maps for mapping "\
            "\n  do NOT extract date from text" \
            "\n  do NOT extract date from filename" \
            "\n  no country bias used "\
            "\n  no area restriction used"\
            "\n  use utf-8 encoding "\
            "\n\nTo set different options, use the GIS GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", "Please, tick the checkbox to run the SVO pipeline to extract Subject-Verb-Object information from your input document(s) and visualize the results in a variety of ways (e.g., charts, GIS maps, network models, wordclouds).\n\nThe SVO function in this GUI is based on the following default options:\n" \
            "  document length =90000 " \
            "\n  sentence length = 100" \
            "\n  do NOT extract date from text" \
            "\n  do NOT extract date from filename" \
            "\n  use Google Earth Pro for pin maps" \
            "\n  extract gender information" \
            "\n  extract dialogue information" \
            "\n\nTo set different options, use the SVO GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of a corpus, automatically extracting all relevant data from texts and visualizing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, Excel charts, and HTML files)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
