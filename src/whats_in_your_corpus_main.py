#written by Roberto Franzosi August 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"what\'s in your corpus",['os','tkinter','subprocess'])==False:
    sys.exit(1)

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_user_interface_util
import IO_files_util
import config_util
import statistics_txt_util
import semantic_aggregation_WordNet_util
import Stanford_CoreNLP_util
import Stanza_util
# import wordclouds_util
import GIS_pipeline_util
import topic_modeling_gensim_util
import topic_modeling_mallet_util
import reminders_util
import file_checker_util
import file_cleaner_util
import file_spell_checker_util
import style_analysis_abstract_concreteness_analysis_util
import run_script_util

# --- Parser-aware annotation helpers ---------------------------------------------------------------
# Honor the NLP package the user selected in Setup (spaCy / Stanford CoreNLP / Stanza). NER (and,
# later, POS & sentiment) run on the selected package. A few annotators (gender, dialogue/quote,
# normalized dates) exist ONLY in Stanford CoreNLP; those verify CoreNLP is installed and warn the
# user that CoreNLP is being used because the option is CoreNLP-only.

def _selected_package(package):
    p = (package or '').lower()
    if 'stanza' in p:
        return 'Stanza'
    if 'spacy' in p:
        return 'spaCy'
    return 'CoreNLP'   # Stanford CoreNLP (and the fallback)


def _CoreNLP_only_ok(option_label, package):
    """For a CoreNLP-only option: check Stanford CoreNLP is installed and, when the user's selected
    package is not CoreNLP, warn that CoreNLP will be used because the option requires it.
    Returns True to proceed (CoreNLP available), False to skip (not installed)."""
    CoreNLPdir, software_url, missing_external_software, errorFound = \
        IO_libraries_util.get_external_software_dir('whats_in_your_corpus_main', 'Stanford CoreNLP',
                                                    silent=True, only_check_missing=True)
    if CoreNLPdir is None or CoreNLPdir == '':
        mb.showwarning('Stanford CoreNLP not installed',
                       'The option "' + option_label + '" is available ONLY via Stanford CoreNLP, '
                       'but Stanford CoreNLP does not appear to be installed.\n\n'
                       'Please, install Stanford CoreNLP using the Setup dropdown menu at the bottom '
                       'of the GUI (Software DOWNLOAD / Software INSTALL) and try again.\n\n'
                       'This option will be skipped.')
        return False
    if _selected_package(package) != 'CoreNLP':
        IO_user_interface_util.timed_alert(GUI_util.window, 6000, 'Running Stanford CoreNLP',
                       'The option "' + option_label + '" is available ONLY via Stanford CoreNLP.\n\n'
                       'Although your selected NLP package is ' + str(package) + ', this option will '
                       'run with Stanford CoreNLP.', False)
    return True


def _annotate_NER_by_package(package, config_filename, inputFilename, inputDir, outputDir,
                             openOutputFiles, chartPackage, dataTransformation,
                             language_var, language_list, export_json_var, memory_var,
                             document_length_var, limit_sentence_length_var,
                             corenlp_NERs, ontonotes_NERs, **extra_kwargs):
    """Route NER extraction to the user-selected package. corenlp_NERs is a list (CoreNLP scheme:
    PERSON/ORGANIZATION/CITY/...); ontonotes_NERs is a comma-separated string (spaCy/Stanza
    OntoNotes scheme: PERSON/ORG/GPE/LOC/...). extra_kwargs (e.g. date-extraction options) are
    forwarded verbatim to the selected engine."""
    pkg = _selected_package(package)
    if pkg == 'Stanza':
        return Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    'NER', False, language_list, memory_var,
                    document_length_var, limit_sentence_length_var,
                    NERs=ontonotes_NERs, **extra_kwargs)
    elif pkg == 'spaCy':
        import spaCy_util
        return spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    ['NER'], False, language_var, memory_var,
                    document_length_var, limit_sentence_length_var,
                    NERs=ontonotes_NERs, **extra_kwargs)
    else:
        return Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    'NER', False, language_var, export_json_var, memory_var,
                    document_length_var, limit_sentence_length_var,
                    NERs=corenlp_NERs, **extra_kwargs)


def _NER_word_column(package):
    """The column holding the token/word in NER output differs by engine: CoreNLP writes 'Word',
    spaCy & Stanza write 'Form'. Consumers that read the NER csv by column name (e.g. the GIS
    pipeline) must use this to stay engine-agnostic."""
    return 'Word' if _selected_package(package) == 'CoreNLP' else 'Form'


def _annotate_SVO_by_package(package, config_filename, inputFilename, inputDir, outputDir,
                             openOutputFiles, chartPackage, dataTransformation,
                             language_var, language_list, export_json_var, memory_var,
                             document_length_var, limit_sentence_length_var, **extra_kwargs):
    """Route the SVO (Subject-Verb-Object) pipeline to the user-selected package. SVO extraction and
    location extraction (google_earth_var/location_filename) exist in all three engines; the bundled
    gender & quote extraction is Stanford CoreNLP-only. When the selected package is not CoreNLP, the
    gender_var/quote_var kwargs are dropped (Stanza/spaCy ignore them) and the caller is expected to
    have warned the user."""
    pkg = _selected_package(package)
    if pkg == 'Stanza':
        return Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    'SVO', False, language_list, memory_var,
                    document_length_var, limit_sentence_length_var, **extra_kwargs)
    elif pkg == 'spaCy':
        import spaCy_util
        return spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    ['SVO'], False, language_var, memory_var,
                    document_length_var, limit_sentence_length_var, **extra_kwargs)
    else:
        return Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    'SVO', False, language_var, export_json_var, memory_var,
                    document_length_var, limit_sentence_length_var, **extra_kwargs)


# RUN section ______________________________________________________________________________________________________________________________________________________

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            GUI_util.data_transformation_options_widget.get(),
                            check_clean_var.get(),
                            check_clean_menu_var.get(),
                            corpus_statistics_var.get(),
                            corpus_statistics_options_menu_var.get(),
                            corpus_text_options_menu_var.get(),
                            wordclouds_var.get(),
                            open_wordclouds_GUI_var.get(),
                            topics_var.get(),
                            what_else_var.get(),
                            what_else_menu_var.get(),
                            quote_var.get(),
                            GIS_var.get(),
                            open_GIS_GUI_var.get(),
                            SVO_var.get(),
                            open_SVO_GUI_var.get(),
                            open_word2vec_GUI_var.get(),
                            open_sentiment_GUI_var.get())

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename,inputDir, outputDir,
        openOutputFiles,
        
        chartPackage,
        dataTransformation,
        check_clean_var,
        check_clean_menu_var,
        corpus_statistics_var,
        corpus_statistics_options_menu_var,
        corpus_text_options_menu_var,
        wordclouds_var,
        open_wordclouds_GUI_var,
        topics_var,
        what_else_var,
        what_else_menu_var,
        single_quote,
        GIS_var,
        open_GIS_GUI_var,
        SVO_var,
        open_SVO_GUI_var,
        open_word2vec_GUI_var,
        open_sentiment_GUI_var):

    config_filename = GUI_util.config_filename_selected_config.get()
    filesToOpen=[]

    openOutputFilesSV=openOutputFiles
    openOutputFiles=False # to make sure files are only opened at the end of this multi-tool script


    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return


    if (check_clean_var==False and \
        corpus_statistics_var==False and \
        wordclouds_var == False and \
        # ((topics_var==False) or (topics_var==True and topics_Mallet_var==False and topics_Gensim_var==False and open_tm_GUI_var==False)) and \
        topics_var==False and \
        what_else_var==False and \
        # ((GIS_var == False) or (GIS_var == True and open_GIS_GUI_var == False)) and \
        GIS_var == False and \
        # ((SVO_var == False) or (SVO_var == True and open_SVO_GUI_var == False))):
        SVO_var == False and \
        open_word2vec_GUI_var == False and \
        open_sentiment_GUI_var == False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    if (what_else_var and ('*' in what_else_menu_var or 'locations' in what_else_menu_var)) and (GIS_var and open_GIS_GUI_var == False):
        reminders_util.checkReminder(scriptName,
            reminders_util.title_options_GIS_redundancy,
            reminders_util.message_GIS_redundancy,
            True)

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                       label='corpus', silent=True)
    if outputDir == '':
        return

    # print(check_clean_menu_var)

    if check_clean_var==True and ('*' in check_clean_menu_var or 'utf-8' in check_clean_menu_var):
        file_checker_util.check_utf8_compliance(GUI_util.window, inputFilename, inputDir, outputDir,openOutputFiles,True)

    if check_clean_var == True and ('*' in check_clean_menu_var or 'ASCII' in check_clean_menu_var):
        result=file_cleaner_util.convert_2_ASCII(GUI_util.window,inputFilename, inputDir, outputDir, config_filename)
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
            # keep the returned (deeper) dir OUT of outputDir so the later sub-analyses
            # (n-grams, what_else, GIS) nest under the corpus_ base as SIBLINGS rather than
            # inside each other -- the cumulative nesting was overflowing Windows' 255-char path.
            outputFiles, _ = statistics_txt_util.compute_corpus_statistics(window, inputFilename, inputDir, outputDir, config_filename, False,
                                  chartPackage, dataTransformation,
                                  stopwords, lemmatize)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

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
        #                                                       chartPackage, dataTransformation)

        # compute sentence length ----------------------------------------------------

        if 'sentence length' in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_sentence_length(inputFilename,inputDir, outputDir, config_filename, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        # compute line length ----------------------------------------------------

        if 'line length' in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_line_length(window, config_filename, inputFilename, inputDir, outputDir, False,
                                                   chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == corpus_statistics_options_menu_var:
            outputFiles = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir, config_filename,
                                                                   openOutputFiles, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if '*' == corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename,inputFilename, inputDir, outputDir, config_filename,
                                                                   openOutputFiles, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if 'detection' in corpus_statistics_options_menu_var:
            outputFiles = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir, config_filename,
                                                                         openOutputFiles, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if 'capital' in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir, config_filename,
                                                                   openOutputFiles, chartPackage, dataTransformation, corpus_statistics_options_menu_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if 'Short' in corpus_statistics_options_menu_var:
            outputFiles=statistics_txt_util.process_words(window,config_filename,inputFilename,inputDir, outputDir, config_filename,
                                                     openOutputFiles, chartPackage, dataTransformation, corpus_statistics_options_menu_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if 'Vowel' in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir, config_filename,
                                                       openOutputFiles, chartPackage, dataTransformation, corpus_statistics_options_menu_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if 'Punctuation' in corpus_statistics_options_menu_var:
            outputFiles=statistics_txt_util.process_words(window,config_filename,inputFilename, inputDir, outputDir, config_filename,
                                                     openOutputFiles, chartPackage, dataTransformation, corpus_statistics_options_menu_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == corpus_statistics_options_menu_var or 'Yule' in corpus_statistics_options_menu_var:
            outputFiles=statistics_txt_util.yule(window, inputFilename, inputDir, outputDir, config_filename)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == corpus_statistics_options_menu_var or 'Unusual' in corpus_statistics_options_menu_var:
            outputFiles=file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir, config_filename, False, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
        if '*' == corpus_statistics_options_menu_var or 'Abstract' in corpus_statistics_options_menu_var:
            # ABSTRACT/CONCRETENESS _______________________________________________________
            outputFiles = style_analysis_abstract_concreteness_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation, processType='')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in corpus_statistics_options_menu_var or 'complexity' in corpus_statistics_options_menu_var:
            outputFiles = statistics_txt_util.compute_sentence_complexity(GUI_util.window, inputFilename,
                                                                     inputDir, outputDir, config_filename,
                                                                     openOutputFiles, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)


        # compute ngrams ----------------------------------------------------
        if '*' == corpus_statistics_options_menu_var or 'grams' in corpus_statistics_options_menu_var:
            ngramType = 1
            if IO_libraries_util.check_inputPythonJavaProgramFile('statistics_txt_util.py') == False:
                return
            hapax_words = False
            ngramsNumber=3
            frequency=0
            normalize = True
            lemmatize = True
            excludePunctuation = True
            excludeArticles = True
            excludeDeterminers = False
            excludeStopWords = False
            wordgram = 1
            bySentenceIndex_var=False

            # n-grams
            case_sensitive=False
            outputFiles, _ = statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
                                                              outputDir, config_filename,
                                                              ngramsNumber, frequency, hapax_words,
                                                              normalize, lemmatize, case_sensitive,
                                                              excludePunctuation, excludeArticles,
                                                              excludeDeterminers, excludeStopWords,
                                                              wordgram,
                                                              openOutputFiles, chartPackage, dataTransformation,
                                                              bySentenceIndex_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    # wordclouds --------------------------------------------------------------

    if wordclouds_var==True:
        if open_wordclouds_GUI_var == True:
            run_script_util.run_script("data_visualization_main.py")
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
            collocation = False
            import wordclouds_util
            outputFiles=wordclouds_util.python_wordCloud(inputFilename, inputDir, outputDir, config_filename, selectedImage="", use_contour_only=use_contour_only, wordcloud_title='', prefer_horizontal=prefer_horizontal, font=font, max_words=max_words, lemmatize=lemmatize, exclude_stopwords=exclude_stopwords, exclude_punctuation=exclude_punctuation, lowercase=lowercase, differentPOS_differentColors=differentPOS_differentColors, differentColumns_differentColors=differentColumns_differentColors, csvField_color_list=csvField_color_list, doNotListIndividualFiles=doNotListIndividualFiles,openOutputFiles=False, collocation=collocation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

# topic modeling ---------------------------------------------------------------------------------
    if topics_var==True:
        run_script_util.run_script("topic_modeling_main.py")

    # Word2Vec
    if open_word2vec_GUI_var:
        run_script_util.run_script("word2vec_main.py")

    # Sentiment analysis
    if open_sentiment_GUI_var:
        run_script_util.run_script("sentiment_analysis_main.py")

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

    if 'coreference' in what_else_menu_var.lower():
        run_script_util.run_script("coreference_main.py")
        return

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

    if (what_else_var and what_else_menu_var == '*') or nouns_var==True or verbs_var==True or people_organizations_var==True or gender_var==True or dialogues_var==True or times_var==True or locations_var==True or nature_var or sentiments_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py')==False:
            return
    if what_else_var and what_else_menu_var == '*':
        outputDir_what_else = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                              label='what_else',
                                                              silent=True)
    else:
        outputDir_what_else = outputDir

# WordNet ----------------------------------
        if nature_var:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Nature via CoreNLP and WordNet',
                                               'The analysis of references to nature via Stanford CoreNLP and WordNet has not been implemented yet.\n"What else is in your corpus" will continue with all other CoreNLP annotators')

        if nouns_var or verbs_var:
            if nouns_var or verbs_var or what_else_menu_var == '*':
                if language_var != 'English':
                    reminders_util.checkReminder(
                        scriptName,
                        reminders_util.title_options_English_language_WordNet,
                        reminders_util.message_English_language_WordNet,
                        True)
                else:
                    annotator = ['POS']
                    files = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                outputDir_what_else, openOutputFiles, chartPackage, dataTransformation,
                                                annotator, False, language_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var)
                    if len(files) > 0:
                        # the WordNet installation directory is now checked in aggregate_GoingUP
                        WordNetDir = ''
                        noun_verb=''
                        if verbs_var == True:
                            inputFilename = files[0] # Verbs but... double check
                            if "verbs" in inputFilename.lower():
                                noun_verb='VERB'
                            else:
                                return
                            outputFiles = semantic_aggregation_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir_what_else, config_filename, noun_verb,
                                                                        openOutputFiles, chartPackage, dataTransformation, language_var)
                            if outputFiles != None:
                                if isinstance(outputFiles, str):
                                    filesToOpen.append(outputFiles)
                                else:
                                    filesToOpen.extend(outputFiles)

                        if nouns_var == True:
                            inputFilename = files[1]  # Nouns but... double check
                            if "nouns" in inputFilename.lower():
                                noun_verb='NOUN'
                            else:
                                return
                            outputFiles = semantic_aggregation_WordNet_util.aggregate_GoingUP(WordNetDir,inputFilename, outputDir_what_else, config_filename, noun_verb,
                                                                        openOutputFiles, chartPackage, dataTransformation, language_var)
                            if outputFiles != None:
                                if isinstance(outputFiles, str):
                                    filesToOpen.append(outputFiles)
                                else:
                                    filesToOpen.extend(outputFiles)
                    else:
                        if (what_else_var and what_else_menu_var == '*'):
                            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Missing WordNet',
                                                               'The analysis of \'What else is in your corpus\' will skip the nouns and verbs classification requiring WordNet and will continue with all other CoreNLP annotators')

        if what_else_var and what_else_menu_var == '*':
            inputFilename=inputFilenameSV

            annotator_list = ['NER', 'gender', 'quote', 'normalized-date']
            NER_list=['PERSON','ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
            outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      chartPackage, dataTransformation,
                                                                      annotator_list, False,
                                                                      language_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                      NERs=NER_list)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if people_organizations_var == True:
            # NER for people & organizations, via the user-selected package (Stanza/spaCy/CoreNLP)
            outputFiles = _annotate_NER_by_package(package, config_filename, inputFilename, inputDir,
                                                   outputDir_what_else, openOutputFiles,
                                                   chartPackage, dataTransformation,
                                                   language_var, language_list, export_json_var, memory_var,
                                                   document_length_var, limit_sentence_length_var,
                                                   corenlp_NERs=['PERSON', 'ORGANIZATION'],
                                                   ontonotes_NERs='PERSON, ORG')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if gender_var == True and _CoreNLP_only_ok('Females & males (gender annotator)', package):
            annotator = 'gender'
            outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      chartPackage, dataTransformation,
                                                                      annotator, False, language_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var)

            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if dialogues_var==True and _CoreNLP_only_ok('Dialogues (quote annotator)', package):
            annotator = 'quote'
            outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      chartPackage, dataTransformation,
                                                                      annotator, False, language_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var,
                                                                      single_quote_var = single_quote)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if times_var==True and _CoreNLP_only_ok('References to date & time (normalized dates)', package):
            annotator='normalized-date'
            outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir_what_else,
                        openOutputFiles, chartPackage, dataTransformation,
                        annotator, False, language_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if locations_var == True:
            # NER for geographical locations, via the user-selected package (Stanza/spaCy/CoreNLP)
            outputFiles = _annotate_NER_by_package(package, config_filename, inputFilename, inputDir,
                                                   outputDir_what_else, openOutputFiles,
                                                   chartPackage, dataTransformation,
                                                   language_var, language_list, export_json_var, memory_var,
                                                   document_length_var, limit_sentence_length_var,
                                                   corenlp_NERs=['CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION'],
                                                   ontonotes_NERs='GPE, LOC')
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if sentiments_var == True:
            annotator = 'sentiment'
            outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                      outputDir_what_else, openOutputFiles,
                                                                      chartPackage, dataTransformation,
                                                                      annotator, False,
                                                                      memory_var, export_json_var, document_length_var,
                                                                      limit_sentence_length_var)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)
# GIS --------------------------------------------------------------------------------
    if GIS_var==True:
        if open_GIS_GUI_var == True:
            run_script_util.run_script("GIS_main.py")
        else:
            # run with all default values;
            # location NER via the user-selected package (Stanza/spaCy/CoreNLP), then geocode & map
            locations = _annotate_NER_by_package(package, config_filename, inputFilename, inputDir,
                                                 outputDir_what_else, openOutputFiles,
                                                 chartPackage, dataTransformation,
                                                 language_var, language_list, export_json_var, memory_var,
                                                 document_length_var, limit_sentence_length_var,
                                                 corenlp_NERs=['COUNTRY', 'STATE_OR_PROVINCE', 'CITY', 'LOCATION'],
                                                 ontonotes_NERs='GPE, LOC',
                                                 extract_date_from_text_var=0,
                                                 filename_embeds_date_var=filename_embeds_date_var,
                                                 date_format=date_format_var,
                                                 items_separator_var=items_separator_var,
                                                 date_position_var=date_position_var)

            if locations is None or len(locations) == 0:
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
        # CoreNLP writes the token in a 'Word' column; spaCy & Stanza write it in 'Form'
        locationColumnName = _NER_word_column(package)
        encoding_var = 'utf-8'

        # create a subdirectory of the output directory
        outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir_what_else, label='GIS',
                                                           silent=True)
        if outputDir_temp == '':
            return

        # locationColumnName where locations to be geocoded (or geocoded) are stored in the csv file;
        #   any changes to the columns will result in error
        outputFiles = GIS_pipeline_util.GIS_pipeline(GUI_util.window, config_filename,
                        NER_outputFilename,inputDir, outputDir_temp,
                        geocoder, GIS_package_var, chartPackage, dataTransformation,
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

        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # SVO ------------------------------------------------------------------------------------

    if SVO_var==True:
        outputDir_SVO = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                               label='SVO',
                                                               silent=True)
        if outputDir_SVO == '':
            return

        outputLocations = []
        if open_SVO_GUI_var == True:
            run_script_util.run_script("SVO_main.py")
        else:
            # run with all default values; SVO pipeline via the user-selected package (Stanza/spaCy/CoreNLP)
            pkg = _selected_package(package)
            location_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                        pkg + '_SVO_LOCATIONS')
            outputLocations.append(location_filename)
            # SVO + location extraction exist in all three engines
            svo_kwargs = dict(extract_date_from_text_var=False,
                              filename_embeds_date_var=filename_embeds_date_var,
                              date_format=date_format_var,
                              items_separator_var=items_separator_var,
                              date_position_var=date_position_var,
                              google_earth_var=True,
                              location_filename=location_filename)
            if pkg == 'CoreNLP':
                # gender & dialogue/quote extraction are bundled into the CoreNLP SVO pipeline ONLY
                gender_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                          'CoreNLP_SVO_gender')
                quote_filename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir_SVO, '.csv',
                                                                         'CoreNLP_SVO_quote')
                svo_kwargs.update(gender_var=True, gender_filename=gender_filename,
                                  quote_var=True, quote_filename=quote_filename)
            else:
                IO_user_interface_util.timed_alert(GUI_util.window, 6000, 'Running SVO via ' + str(package),
                    'The SVO (Subject-Verb-Object) pipeline will run via ' + str(package) + '.\n\n'
                    'The bundled gender and dialogue/quote extraction is available ONLY via Stanford '
                    'CoreNLP and will be skipped. Subject-Verb-Object and location extraction will be '
                    'produced normally.', False)
            outputFiles = _annotate_SVO_by_package(package, config_filename, inputFilename, inputDir,
                                                   outputDir_SVO, openOutputFiles,
                                                   chartPackage, dataTransformation,
                                                   language_var, language_list, export_json_var, memory_var,
                                                   document_length_var, limit_sentence_length_var,
                                                   **svo_kwargs)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    openOutputFiles=openOutputFilesSV
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=630, # height at brief display
                             GUI_height_full=670, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for a Sweeping View of Your Corpus (Single/Multiple Document(s)) - A Pipeline'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

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

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

check_clean_var= tk.IntVar()
check_clean_menu_var = tk.StringVar()

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
    check_clean_var.set(1),
    check_clean_menu_var.set('*')
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

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses', variable=extra_GUIs_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Corpus statistics (Open GUI)','Style Analysis (Open GUI)','N-grams & Co-Occurrences (Open GUI)','CoNLL table analyzer (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def open_GUI(*args):
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    else:
        extra_GUIs_menu.configure(state='disabled')
        return
    if extra_GUIs_menu_var.get():
        if 'statistics' in extra_GUIs_menu_var.get():
            run_script_util.run_script("statistics_txt_main.py")
        if 'Style' in extra_GUIs_menu_var.get():
            run_script_util.run_script("style_analysis_main.py")
        if 'N-grams' in extra_GUIs_menu_var.get():
            run_script_util.run_script("NGrams_CoOccurrences_main.py")
        if 'CoNLL' in extra_GUIs_menu_var.get():
            run_script_util.run_script("CoNLL_table_analyzer_main.py")
extra_GUIs_menu_var.trace('w',open_GUI)
extra_GUIs_var.trace('w',open_GUI)

check_clean_var.set(1)
check_clean_menu_var.set('*')

check_clean_checkbox = tk.Checkbutton(window,text="Check & clean corpus", variable=check_clean_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,check_clean_checkbox,True)

check_clean_menu = tk.OptionMenu(window,  check_clean_menu_var, '*', 'Check input document(s) for utf-8 encoding',
                                 'Convert non-ASCII apostrophes & quotes and % to percent')

# check_clean_menu.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.whats_in_your_corpus_corpus_statistics_options_menu_lb_pos, y_multiplier_integer,
                                               check_clean_menu, False)


def activate_linguistic_features_options():
    if corpus_statistics_var.get():
        corpus_statistics_options_menu.configure(state='normal')
    else:
        corpus_statistics_options_menu.configure(state='disabled')

corpus_statistics_var.set(1)
corpus_statistics_checkbox = tk.Checkbutton(window,text="Document(s) linguistic features", variable=corpus_statistics_var, onvalue=1, offvalue=0, command=lambda: activate_linguistic_features_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,corpus_statistics_checkbox,True)

corpus_statistics_options_menu_var.set('*')
corpus_statistics_options_menu_lb = tk.Label(window, text='NLP tools options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.whats_in_your_corpus_corpus_statistics_options_menu_lb_pos,y_multiplier_integer,corpus_statistics_options_menu_lb,True)

corpus_statistics_options_menu = tk.OptionMenu(window, corpus_statistics_options_menu_var,
                                               '*',
                                               'Compute statistics (sentences, words, syllables)',
                                               'Compute n-grams',
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
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.whats_in_your_corpus_corpus_statistics_options_menu_pos,y_multiplier_integer,corpus_statistics_options_menu, True)

corpus_text_options_menu_var.set('*')
corpus_options_menu_lb = tk.Label(window, text='Text options')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,y_multiplier_integer,corpus_options_menu_lb,True)

corpus_options_menu = tk.OptionMenu(window, corpus_text_options_menu_var, '*','Lemmatize words', 'Exclude stopwords & punctuation')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.whats_in_your_corpus_corpus_options_menu_pos,y_multiplier_integer,corpus_options_menu)

wordclouds_var.set(1)
wordclouds_checkbox = tk.Checkbutton(window,text="Visualization options", variable=wordclouds_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,wordclouds_checkbox, True)

open_wordclouds_GUI_var.set(0) # wordclouds GUI
open_wordclouds_GUI_checkbox = tk.Checkbutton(window,text="Open visualizations GUI", state='disabled', variable=open_wordclouds_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,y_multiplier_integer,open_wordclouds_GUI_checkbox)

def activate_wordclouds_GUI(*args):
    if wordclouds_var.get():
        open_wordclouds_GUI_checkbox.configure(state='normal')
    else:
        open_wordclouds_GUI_checkbox.configure(state='disabled')
wordclouds_var.trace('w', activate_wordclouds_GUI)

activate_wordclouds_GUI()

topics_checkbox = tk.Checkbutton(window,text="What are the topics? (Topic modeling via BERT, Gensim, MALLET)", variable=topics_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,topics_checkbox,True)

def changed_filename(*args):
    if inputFilename.get()!='':
        reminders_util.checkReminder(scriptName,
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

open_tm_GUI_var.set(0) # topic modeling GUI
open_GUI_checkbox = tk.Checkbutton(window,text="Open topic modeling GUI", variable=open_tm_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,y_multiplier_integer,open_GUI_checkbox)

open_word2vec_GUI_var = tk.IntVar()
open_word2vec_GUI_var.set(0)
word2vec_checkbox = tk.Checkbutton(window,text="Word embeddings (via BERT, Gensim) and word sense disambiguation (Open GUI)", variable=open_word2vec_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,word2vec_checkbox)

def activate_topics(*args):
    if topics_var.get()==True:
        open_GUI_checkbox.configure(state='normal')
    else:
        open_GUI_checkbox.configure(state='disabled')
topics_var.trace('w',activate_topics)

def activate_all_options(*args):
    if open_tm_GUI_var.get()==True:
        corpus_statistics_var.set(0)
        corpus_statistics_checkbox.configure(state='disabled')
        what_else_var.set(0)
        what_else_checkbox.configure(state='disabled')
    else:
        corpus_statistics_var.set(1)
        corpus_statistics_checkbox.configure(state='normal')
        what_else_var.set(1)
        what_else_checkbox.configure(state='normal')
open_tm_GUI_var.trace('w',activate_all_options)

# language options
language_var_lb = tk.Label(window, text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               language_var_lb, True)

what_else_var.set(1)
what_else_checkbox = tk.Checkbutton(window,text="What else is in your document(s)? (via Stanza, CoreNLP, and WordNet)", variable=what_else_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,what_else_checkbox,True)

what_else_menu_var.set('*')
what_else_menu = tk.OptionMenu(window,  what_else_menu_var, '*', 'Coreference resolution (CoreNLP)', 'Dialogues (CoreNLP quote annotator)','Noun and verb classes (Stanza NER & WordNet)', 'People & organizations (Stanza NER)', 'Females & males (CoreNLP gender annotator)',
                               'References to date & time (CoreNLP normalized NER dates)',
                               'References to geographical locations (Stanza NER)',
                               'References to nature (Stanza NER & WordNet)',
                               'Sentiments expressed (Stanza)')
what_else_menu.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.whats_in_your_corpus_what_else_menu_pos, y_multiplier_integer,
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
            y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,
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

open_sentiment_GUI_var = tk.IntVar()
open_sentiment_GUI_var.set(0)
sentiment_checkbox = tk.Checkbutton(window,text="Sentiment analysis (via BERT, Stanza, spaCy, VADER, NRC, SentiWordNet, ANEW, hedonometer) (Open GUI)", variable=open_sentiment_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,sentiment_checkbox)

GIS_var.set(1)
GIS_checkbox = tk.Checkbutton(window,text="GIS (Geographic Information System) pipeline", variable=GIS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,GIS_checkbox, True)

open_GIS_GUI_var.set(0) # GIS GUI
open_GIS_GUI_checkbox = tk.Checkbutton(window,text="Open GIS GUI", state='disabled', variable=open_GIS_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,y_multiplier_integer,open_GIS_GUI_checkbox)

def activate_GIS_GUI(*args):
    if GIS_var.get():
        open_GIS_GUI_checkbox.configure(state='normal')
    else:
        open_GIS_GUI_checkbox.configure(state='disabled')
        open_GIS_GUI_var.set(0)
GIS_var.trace('w', activate_GIS_GUI)

activate_GIS_GUI()

SVO_var.set(1)
SVO_checkbox = tk.Checkbutton(window,text="SVO (Subject-Verb-Object) & SRL (Semantic Role Labeling) pipeline", variable=SVO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SVO_checkbox, True)

open_SVO_GUI_var.set(0) # SVO GUI
open_SVO_GUI_checkbox = tk.Checkbutton(window,text="Open SVO GUI", state='disabled', variable=open_SVO_GUI_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate,y_multiplier_integer,open_SVO_GUI_checkbox)

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

TIPS_lookup = {'Excel - Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf', 'Lemmas & stopwords':'TIPS_NLP_NLP Basic language.pdf', 'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf', 'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf', 'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf', 'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf','N-Grams (word & character)':'TIPS_NLP_Ngram (word & character).pdf','Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf','NLP Suite Ngram and Word Co-Occurrence Viewer':'TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf','Style analysis':'TIPS_NLP_Style analysis.pdf','Statistical measures':'TIPS_NLP_Statistical measures.pdf','Style analysis':'TIPS_NLP_Style analysis.pdf','Wordclouds':'TIPS_NLP_Wordclouds Visualizing word clouds.pdf','Topic modeling':'TIPS_NLP_Topic modeling.pdf','Topic modeling and corpus size':'TIPS_NLP_Topic modeling and corpus size.pdf','Topic modeling (Gensim)':'TIPS_NLP_Topic modeling Gensim.pdf','Topic modeling (Mallet)':'TIPS_NLP_Topic modeling Mallet.pdf','Mallet installation':'TIPS_NLP_Topic modeling Mallet installation.pdf','CoreNLP NER (Named Entity Recognition)':'TIPS_NLP_NER tags across packages.pdf','The world of emotions and sentiments':'TIPS_NLP_The world of emotions and sentiments.pdf','Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf','Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',"Stanford CoreNLP Gender annotator":"TIPS_NLP_Stanford CoreNLP gender annotator.pdf",'GIS (Geographic Information System): Mapping Locations':'TIPS_NLP_GIS (Geographic Information System).pdf','SVO extraction and visualization':'TIPS_NLP_SVO extraction and visualization.pdf','Stanford CoreNLP enhanced dependencies parser (SVO)':'TIPS_NLP_Stanford CoreNLP enhanced dependencies parser (SVO).pdf','WordNet':'TIPS_NLP_WordNet.pdf'}
TIPS_options='Text encoding (utf-8)','Excel - Enabling Macros', 'csv files - Problems & solutions', 'Statistical measures', 'English Language Benchmarks', 'Things to do with words: Overall view', 'Lemmas & stopwords', 'N-Grams (word & character)','Google Ngram Viewer','NLP Suite Ngram and Word Co-Occurrence Viewer','Style analysis','Wordclouds','Topic modeling','Topic modeling and corpus size','Topic modeling (Gensim)','Topic modeling (Mallet)','Mallet installation','CoreNLP NER (Named Entity Recognition)','The world of emotions and sentiments','Sentiment analysis','Stanford CoreNLP date extractor (NER normalized date)','Stanford CoreNLP Gender annotator','GIS (Geographic Information System): Mapping Locations','SVO extraction and visualization','Stanford CoreNLP enhanced dependencies parser (SVO)','WordNet'

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
                                      "Please, tick the checkbox to open other related GUIs (e.g., Corpus statistics, Style Analysis, N-grams, CoNLL table analyzer).\n\nThe selected GUI will open without having to press RUN.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      "Please, tick the checkbox to check your input corpus for utf-8 encoding and/or to convert non-ASCII apostrophes & quotes and % to percent.\n   Non utf-8 compliant texts are likely to lead to code breakdown.\n   ASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n   % signs may lead to code breakdown of Stanford CoreNLP.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick checkbox to compute corpus statistics: number of documents, number of sentences and words, word n-grams by document.\n\nFOR N-GRAMS, THERE IS A SEPARATE SCRIPT WITH MORE GENERAL OPTIONS: NGrams_CoOccurrences_Viewer_main.\n\nThe * option will lemmatize words and exclude stopwords and punctuation. IT WILL COMPUTE BASIC WORD N-GRAMS. IT WILL NOT COMPUTE LINE LENGTH. YOU WOULD NEED TO RUN THE LINE LENGTH OPTION SEPARATELY.\n\nLine length in a typical document mostly depends upon typesetting formats. Only for poetry or music lyrics does the line-length measure make sense; in fact, you could use the option the detect those documents in your corpus characterized by different typesetting formats (.g., a poem document among narrative documents).\n\nRUN THE LINE-LENGTH OPTION ONLY IF IT MAKES SENSE FOR YOUR CORPUS.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox for visualization options.\n\nWith the checkbox ticked, a default wordcloud will be generated. Tick 'Open visualizations GUI' to access the full data visualization GUI with options for wordclouds, network graphs (Gephi, vis.js), Sankey charts, sunburst, treemap, colormap/heatmap, boxplots, bubble charts, GIS maps, and more.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to open the topic modeling GUI.\n\nThe topic modeling GUI provides access to three approaches:\n  - BERTopic (transformer-based, best for 100+ documents)\n  - Gensim LDA (fast, works well on small corpora)\n  - MALLET LDA (Java-based, requires separate installation)")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to open the Word embeddings GUI.\n\nThe GUI provides three tools:\n  - Word embeddings via BERT (contextual embeddings from a pre-trained English language model)\n  - Word2Vec via Gensim (static embeddings trained on your corpus, Skip-Gram or CBOW)\n  - Word sense disambiguation via BERT (automatically identifies different senses of a word in your corpus)")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to analyze your corpus for a variety of tools. Select the default \'*\' to run all options. Alternatively, select the specific option to run.\n\nMost options use Stanza (Python). Four options require Stanford CoreNLP (Java): coreference resolution, dialogues, gender, and normalized dates.\n\nThe NLP tools will allow you to answer questions such as:\n  1. Who refers to whom? (CoreNLP coreference resolution — opens the coreference GUI)\n  2. Are there dialogues in your corpus? (CoreNLP quote annotator — extracts quotes and attributes them to speakers. Default is DOUBLE quotes; tick 'Include single quotes' for both.)\n  3. Do nouns and verbs cluster in specific aggregates, e.g., communication, movement? (Stanza NER + WordNet)\n  4. Does the corpus contain references to people and organizations? (Stanza NER)\n  5. Are there references to females and males? (CoreNLP gender annotator)\n  6. References to dates and times? (CoreNLP SUTime normalized date extraction)\n  7. References to geographical locations that could be placed on a map? (Stanza NER)\n  8. References to nature, e.g., weather, seasons, animals, plants? (Stanza NER + WordNet)\n  9. Sentiments expressed? (Stanza)")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to open the Sentiment Analysis GUI.\n\nThe GUI provides multiple approaches:\n  - Large Language Models: BERT (English and Multilingual)\n  - Neural network: Stanford CoreNLP, Stanza\n  - Dictionary-based: ANEW, hedonometer, NRC (emotion wheel), spaCy/TextBlob, SentiWordNet, VADER\n  - Character-level: Character Emotion Arcs (NER + NRC)")
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
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of a corpus, automatically extracting all relevant data from texts and visualizing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, Excel charts, and HTML files)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

config_filename = GUI_util.config_filename_selected_config.get()
filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(config_filename, config_input_output_numeric_options)
extract_date_from_text_var=0

GUI_util.window.mainloop()
