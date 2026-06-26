import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "CoNLL table_analyzer", ['os', 'tkinter','pandas']) == False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import CoNLL_util
import CoNLL_table_search_util
import statistics_csv_util
import charts_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import Stanford_CoreNLP_tags_util
import CoNLL_k_sentences_util
import reminders_util
import run_script_util

# from data_manager_main import extract_from_csv

# more imports (e.g., import CoNLL_clause_analysis_util) are called below under separate if statements

# RUN section ______________________________________________________________________________________________________________________________________________________

# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation,
        searchedCoNLLField, searchField_kw, postag, deprel, co_postag, co_deprel, Begin_K_sent_var, End_K_sent_var):

    # 'Run the default parser' option: this analyzer needs a CoNLL table; if the user has none, open the
    # Parsers/Annotators GUI, which parses the corpus and reopens the analyzer with the fresh CoNLL. We do NOT
    # close this window: if the parse stalls/fails the user still has the analyzer (a fresh one opens on success;
    # the empty one can simply be closed). Checked first so it works even when no valid CoNLL is loaded.
    if run_parser_var.get():
        IO_user_interface_util.timed_alert(GUI_util.window, 5000, 'Running the parser',
            'The Parsers/Annotators GUI is opening in a separate window. Run it there; when it finishes a NEW '
            'CoNLL Table Analyzer will open with the parsed CoNLL table. You can then close THIS (empty) window.',
            True, '', True)
        run_script_util.run_script_detached("parsers_annotators_main.py", "open_analyzer")
        return

    global recordID_position, documentId_position, data, all_CoNLL_records
    recordID_position = 9 # NEW CoNLL_U
    documentId_position = 11 # NEW CoNLL_U

    noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."
    config_filename = GUI_util.config_filename_selected_config.get()
    filesToOpen = []  # Store all files that are to be opened once finished
    outputFiles = []

    if extra_GUIs_var.get() == False and \
        all_analyses_var.get() == False and\
        advanced_analyses_var.get() == False and \
        search_token_var.get() == False and \
        WordNet_var.get() == False and \
        compute_sentence_var.get() == False and \
        k_sentences_var.get() == False:
            mb.showwarning(title='No option selected',
                       message="No option has been selected.\n\nPlease, select an option by ticking a checkbox and try again.")
            return

    # if extra_GUIs_var.get():
    #     if 'Data manipulation' in extra_GUIs_menu_var.get():
    #         run_script_util.run_script("data_manipulation_main.py")
    #     elif 'Style' in extra_GUIs_menu_var.get():
    #         run_script_util.run_script("style_analysis_main.py")
    #     if 'Ngrams searches' in extra_GUIs_menu_var.get():
    #         run_script_util.run_script("NGrams_CoOccurrences_main.py")
    #     if 'Word searches' in extra_GUIs_menu_var.get():
    #         run_script_util.run_script("file_search_byWord_main.py")
    #     if 'Wordnet' in extra_GUIs_menu_var.get():
    #         run_script_util.run_script("semantic_aggregation_main.py")

# Ngrams searches & VIEWER','Word searches


    if search_token_var.get() and 'e.g.: father' in searchField_kw:
        mb.showwarning(title='Search error',
                       message="The 'Searched token' field must be different from 'e.g.: father'. Please, enter a CoNLL table token/word and try again.")
        return

    if not CoNLL_util.check_CoNLL(inputFilename):
        return

    withHeader = True
    # TODO Chen we are reading inputFilename twice, once here then again as a dataframe
    data, header = IO_csv_util.get_csv_data(inputFilename, withHeader)
    if len(data) == 0:
        return
    # Detect source package and normalize columns to canonical (CoreNLP) order
    # so all downstream positional indexing works regardless of package
    source_package = CoNLL_util.detect_CoNLL_package(header)
    header, data = CoNLL_util.normalize_to_canonical(header, data)
    all_CoNLL_records = CoNLL_util.CoNLL_record_division(data)
    if all_CoNLL_records == None:
        return
    if len(all_CoNLL_records) == 0:
        return

# ANALYSES -----------------------------------------------------------------------------------

    if all_analyses_var.get():
        # # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
        # outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_analyses',
        #                                                    silent=True)
        # if outputDir_temp == '':
        #     return
        #
        # outputDir=outputDir_temp
        #
        if all_analyses.get() == '*':
            label = "All CoNLL table analyses"
        else:
            label = all_analyses.get()
        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running CoNLL table ' + label + ' analyses at',
                                                     True, '', True, '', False)

        outputDirSV = outputDir

        if all_analyses.get() == '*' or all_analyses.get() == 'Clause analysis':
            # Check if Clause Tag column has actual data (not all empty)
            clause_tag_idx = header.index('Clause Tag') if 'Clause Tag' in header else -1
            has_clause_tags = False
            if clause_tag_idx >= 0:
                has_clause_tags = any(row[clause_tag_idx].strip() != '' for row in data if clause_tag_idx < len(row))
            if not has_clause_tags:
                if all_analyses.get() == 'Clause analysis':
                    mb.showwarning(title='Input file error',
                                   message='The CLAUSE analysis algorithm requires a CoNLL table with clause tags (generated by the Stanford CoreNLP PCFG parser or Stanza constituency parser).\n\nNo clause tags found in this CoNLL table.\n\nSkipping clause analysis.')
                    print('Clause analysis skipped: no clause tags in CoNLL table (source: ' + source_package + ').')
                else:
                    print('Clause analysis skipped: no clause tags in CoNLL table (source: ' + source_package + ').')
            else:
                # create a subdirectory of the output directory
                outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir,
                                                                        label='CoNLL_clause',
                                                                        silent=True)
                if outputDir_temp == '':
                    return
                outputDir = outputDir_temp

                if 'CoNLL' in inputFilename and '_nn_' in inputFilename:
                    if all_analyses.get() == 'Clause analysis':
                        mb.showwarning(title='Input file error',
                                       message='The CLAUSE analysis algorithm expects in input a CoNLL table generated by the Stanford CoreNLP PCFG parser, rather than the nn, neural network parser.\n\nOnly the PCFG parser exports clause tags.\n\nPlease check your input file and try again.')
                        print('The CLAUSE analysis algorithm expects in input a CoNLL table generated by the Stanford CoreNLP PCFG parser, rather than the nn, neural network parser. Only the PCFG parser exports clause tags. Please check your input file and try again.')
                if 'CoNLL' in inputFilename and not '_nn_' in inputFilename:
                    import CoNLL_clause_analysis_util
                    outputFiles = CoNLL_clause_analysis_util.clause_stats(inputFilename, '', outputDir,
                                                                          data,
                                                                          all_CoNLL_records,
                                                                          openOutputFiles, chartPackage, dataTransformation)
                    if outputFiles!=None:
                        filesToOpen.extend(outputFiles)

        if all_analyses.get() =='*' or all_analyses.get() =='Noun analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_noun',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_noun_analysis_util
            outputFiles = CoNLL_noun_analysis_util.noun_stats(inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles,
                                                              chartPackage,
                                                              dataTransformation)
            if outputFiles!=None:
                filesToOpen.extend(outputFiles)


        if all_analyses.get() =='*' or all_analyses.get() =='Adjective analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_adjective',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_adjective_analysis_util
            outputFiles = CoNLL_adjective_analysis_util.adjective_stats(inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles,
                                                              chartPackage,
                                                              dataTransformation)
            if outputFiles!=None:
                filesToOpen.extend(outputFiles)


        if all_analyses.get() =='*' or all_analyses.get() =='Content/Function ratio analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_ratio',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_ratio_analysis_util
            outputFiles = CoNLL_ratio_analysis_util.compute_word_class_frequencies(inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles,
                                                              chartPackage,
                                                              dataTransformation)
            if outputFiles!=None:
                filesToOpen.extend(outputFiles)


        if all_analyses.get() =='*' or all_analyses.get() =='Adverb analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_adverb',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_adverb_analysis_util
            outputFiles = CoNLL_adverb_analysis_util.adverb_stats(inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles,
                                                              chartPackage,
                                                              dataTransformation)
            if outputFiles!=None:
                filesToOpen.extend(outputFiles)
        if all_analyses.get() =='*' or all_analyses.get() =='Verb analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_verb',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_verb_analysis_util
            outputFiles = CoNLL_verb_analysis_util.verb_stats(config_filename, inputFilename, outputDir, data, all_CoNLL_records,
                                                              openOutputFiles, chartPackage, dataTransformation)

            if outputFiles!=None:
                filesToOpen.extend(outputFiles)

        if all_analyses.get() =='*' or all_analyses.get() =='Function (junk/stop) words analysis':
            # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
            outputDir_temp = IO_files_util.make_output_subdirectory(inputFilename, '', outputDirSV,
                                                                    label='CoNLL_stop',
                                                                    silent=True)
            if outputDir_temp == '':
                return
            outputDir = outputDir_temp
            import CoNLL_function_words_analysis_util
            outputFiles = CoNLL_function_words_analysis_util.function_words_stats(inputFilename, outputDir, data,
                                                                                  all_CoNLL_records, openOutputFiles,
                                                                                  chartPackage, dataTransformation)
            if outputFiles!=None:
                filesToOpen.extend(outputFiles)

        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                           'Finished running CoNLL table ' + label + ' analyses at',
                                           True, '', True, startTime, False)

    if advanced_analyses_var.get():
        # Advanced CoNLL analyses ported from the semantic_aggregation GUI; they all consume the CoNLL table
        # (inputFilename) and the companion selectors (NOUN/VERB, Knowledge base, dictionary csv, K-begin/end).
        sel = advanced_analyses.get()
        nv_sel = noun_verb_menu_var.get()
        # default (anything other than a specific 'NOUN'/'VERB') processes BOTH word classes
        noun_verb_list = [nv_sel] if nv_sel in ('NOUN', 'VERB') else ['NOUN', 'VERB']
        adv_startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                           'Started running CoNLL Advanced analyses at', True, '', True, '', False)
        # all Advanced analyses write into a dedicated subdirectory (keeps them out of the cluttered main output dir)
        adv_outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_Advanced_analyses', silent=True) or outputDir
        if sel == '*' or sel == 'Classification of Nouns & Verbs via FrameNet, VerbNet, WordNet':
            import semantic_aggregation_util, config_util
            cfg = config_util.read_NLP_package_language_config()
            cfg_language = cfg[4] if len(cfg) > 4 else ''
            noun_form_csv, noun_lemma_csv, verb_form_csv, verb_lemma_csv = CoNLL_util.get_nouns_verbs_CoNLL(inputFilename, adv_outputDir)
            for noun_verb in noun_verb_list:
                lemma_csv = noun_lemma_csv if noun_verb == 'NOUN' else verb_lemma_csv
                outFiles = semantic_aggregation_util.aggregate(knowledge_base_menu_var.get(), '', lemma_csv, adv_outputDir,
                                                               config_filename, noun_verb, openOutputFiles, chartPackage,
                                                               dataTransformation, cfg_language, [])
                if outFiles:
                    filesToOpen.extend(outFiles)
        if sel == '*' or sel == 'Word Sense Disambiguation (WSD)':
            import semantic_aggregation_util
            for noun_verb in noun_verb_list:
                outFiles = semantic_aggregation_util.wsd_aggregate_WordNet(inputFilename, adv_outputDir, noun_verb, chartPackage, dataTransformation)
                if outFiles:
                    filesToOpen.extend(outFiles)
        if sel == '*' or sel == 'Zoom OUT/UP by Sentence Index':
            import semantic_aggregation_WordNet_util, semantic_aggregation_util, config_util
            # No dictionary file-picking: the resource comes from the Knowledge base selector, and the aggregation
            # dictionary is GENERATED on the fly (Zoom OUT/UP) from the corpus, then plotted by sentence. This keeps
            # the same two selectors (Knowledge base + NOUN/VERB) driving every Advanced option. A browse fallback
            # remains for an externally-made dictionary (used only if generation yields nothing).
            resource = knowledge_base_menu_var.get()
            if resource in ('', '*'):
                resource = 'WordNet'  # by-sentence default when no specific resource is selected
            cfg = config_util.read_NLP_package_language_config()
            cfg_language = cfg[4] if len(cfg) > 4 else ''
            nf_csv, noun_lemma_csv, vf_csv, verb_lemma_csv = CoNLL_util.get_nouns_verbs_CoNLL(inputFilename, adv_outputDir)
            for noun_verb in noun_verb_list:
                lemma_csv = noun_lemma_csv if noun_verb == 'NOUN' else verb_lemma_csv
                # generate the aggregation dictionary (Zoom OUT/UP) for this resource + class
                agg_files = semantic_aggregation_util.aggregate(resource, '', lemma_csv, adv_outputDir, config_filename,
                                                                noun_verb, openOutputFiles, chartPackage, dataTransformation,
                                                                cfg_language, [])
                dict_path = next((f for f in (agg_files or [])
                                  if '_up_' in os.path.basename(f).lower()
                                  and 'frequency' not in os.path.basename(f).lower()), '')
                if not dict_path:  # fallback: let the user browse for an external dictionary
                    dict_path = tk.filedialog.askopenfilename(
                        title="Select an aggregation dictionary csv for %s %s" % (resource, noun_verb),
                        filetypes=[("csv files", "*.csv")])
                    if not dict_path:
                        continue
                outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', adv_outputDir, '.csv', resource + '_' + noun_verb, 'conll')
                outFiles = semantic_aggregation_WordNet_util.Wordnet_bySentenceID(inputFilename, dict_path, outputFilename, adv_outputDir, noun_verb, openOutputFiles, chartPackage, dataTransformation)
                if outFiles:
                    if isinstance(outFiles, str):
                        filesToOpen.append(outFiles)
                    else:
                        filesToOpen.extend(outFiles)
        if sel == '*' or sel == 'Beginning-End K sentences analyzer (repetition finder)':
            if Begin_K_sent_var == 0 or End_K_sent_var == 0:
                mb.showwarning(title='K sentences required',
                               message="The 'Beginning-End K sentences analyzer (repetition finder)' needs the Begin K-sentences and End K-sentences values.\n\nPlease enter them and try again.")
            else:
                temp_outputDir, outFiles = CoNLL_k_sentences_util.k_sent(inputFilename, adv_outputDir, chartPackage, dataTransformation, Begin_K_sent_var, End_K_sent_var)
                if outFiles:
                    filesToOpen.extend(outFiles)
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                           'Finished running CoNLL Advanced analyses at', True, '', True, adv_startTime, False)

# SEARCH -----------------------------------------------------------------------------------

    if search_token_var.get() and searchField_kw != 'e.g.: father':
        # # create a subdirectory of the output directory
        # outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_search',
        #                                                    silent=True)

        if ' ' in searchField_kw:
            mb.showwarning(title='Search error',
                           message="The CoNLL table search can only contain one token/word since the table has one record for each token/word.\n\nPlease, enter a different word and try again.\n\nIf you need to search your corpus for collocations, i.e., multi-word expressions, you need to use the 'N-grams/Co-occurrence searches' or the 'Words/collocations searches' in the ALL searches GUI.")
            return
        if searchedCoNLLField.lower() not in ['lemma', 'form']:
            searchedCoNLLField_var.set('FORM')
        if postag_var.get() != '*':
            postag = str(postag_var.get()).split(' - ')[0]
            postag = postag.strip()
        else:
            postag = '*'
        if deprel != '*':
            deprel = str(deprel).split(' - ')[0]
            deprel = deprel.strip()
        else:
            deprel = '*'
        if co_postag != '*':
            co_postag = str(co_postag).split(' - ')[0]
            co_postag = co_postag.strip()
        else:
            co_postag = '*'
        if co_deprel != '*':
            co_deprel = str(co_deprel).split(' - ')[0]
            co_deprel = co_deprel.strip()
        else:
            co_deprel = '*'

        if 'e.g.: father' in searchField_kw:
            if (not os.path.isfile(inputFilename.strip())) and \
                    ('CoNLL' not in inputFilename) and \
                    (not inputFilename.strip()[-4:] == '.csv'):
                mb.showwarning(title='INPUT File Path Error',
                               message='Please, check INPUT FILE PATH and try again. The file must be a CoNLL table (extension .conll or .csv).')
                return
            msg = "Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from the default value (e.g.: father)."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return  # breaks loop
        if len(searchField_kw) == 0:
            msg = "Please, check the \'Searched token\' field and try again.\n\nThe value entered must be different from blank."
            mb.showwarning(title='Searched Token Input Error', message=msg)
            return  # breaks loop

        startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running CoNLL search at',
                                                     True, '', True, '', True)

        withHeader = True
        data, header = IO_csv_util.get_csv_data(inputFilename, withHeader)
        header, data = CoNLL_util.normalize_to_canonical(header, data)

        if len(data) <= 1000000:
            try:
                data = sorted(data, key=lambda x: int(x[recordID_position]))
            except:
                mb.showwarning(title="CoNLLL table ill formed",
                               message="The CoNLL table is ill formed. You may have tinkered with it. Please, rerun the parser (Stanford CoreNLP, Stanza, or spaCy) since many scripts rely on the CoNLL table.")
                return

        temp_outputDir, filesToOpen = CoNLL_table_search_util.search_CoNLL_table(inputFilename, outputDir, config_filename,
                                          chartPackage, dataTransformation,
                                          all_CoNLL_records, searchField_kw, searchedCoNLLField,
                                          related_token_POSTAG=co_postag,
                                          related_token_DEPREL=co_deprel, _tok_postag_=postag,
                                          _tok_deprel_=deprel)

        if len(filesToOpen)>0:
            outputDir = temp_outputDir

# WordNet ------------------------------------------------------------------------------

    if WordNet_var.get():
        # create a subdirectory of the output directory; should create a subdir with increasing number to avoid writing ver
        outputDir_SV = outputDir
        outputDir = IO_files_util.make_output_subdirectory(inputFilename, '', outputDir, label='CoNLL_WordNet',
                                                           silent=False)
        if outputDir == '':
            return

        import pandas as pd
        df = pd.read_csv(inputFilename)
        df_nouns = df[df['POS'].isin(['NN', 'NNPS', 'NNP', 'NNS'])][['Lemma', 'POS']]
        inputFilename_nouns = outputDir + os.sep + "CoNLL_nouns_forWordNet.csv"
        df_nouns.to_csv(inputFilename_nouns, index=False) # , header=None
        df_verbs = df[df['POS'].isin(['VB', 'VBN', 'VBD', 'VBG', 'VBP', 'VBZ'])][['Lemma', 'POS']]
        inputFilename_verbs = outputDir + os.sep + "CoNLL_verbs_forWordNet.csv"
        df_verbs.to_csv(inputFilename_verbs, index=False) # , header=None

        filesToOpen.append(inputFilename_nouns)
        filesToOpen.append(inputFilename_verbs)

        # the WordNet installation directory is now checked in aggregate_GoingUP
        WordNetDir = ''
        import semantic_aggregation_util
        output = semantic_aggregation_util.aggregate('*', WordNetDir, inputFilename_nouns, outputDir,
                                                     config_filename, 'NOUN',
                                                     openOutputFiles, chartPackage, dataTransformation,
                                                     language_var='English')
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)

        output = semantic_aggregation_util.aggregate('*', WordNetDir, inputFilename_verbs, outputDir,
                                                     config_filename, 'VERB',
                                                     openOutputFiles, chartPackage, dataTransformation,
                                                     language_var='English')
        if output != None:
            if isinstance(output, str):
                filesToOpen.append(output)
            else:
                filesToOpen.extend(output)

        outputDir=outputDir_SV

# -----------------------------------------------------------------------------------------------------------------------------
    if compute_sentence_var.get():
        tempOutputFile = CoNLL_util.compute_sentence_table(inputFilename, outputDir)
        filesToOpen.append(tempOutputFile)

# -----------------------------------------------------------------------------------------------------------------------------
    if k_sentences_var.get():
        if Begin_K_sent_var==0 or End_K_sent_var==0:
            mb.showwarning(title='Warning',
                           message="The Repetion finder algorithm needs beginning and end K sentences.\n\nPlease, enter valid K number(s) of sentences and try again.")
            return
        startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                       'Started running the CoNLL table K-sentences analyzer at',
                                                       True, '', True, '', False)
        temp_outputDir, outputFiles = CoNLL_k_sentences_util.k_sent(inputFilename, outputDir, chartPackage, dataTransformation, Begin_K_sent_var, End_K_sent_var)
        if outputFiles!=None:
            outputDir = temp_outputDir
            filesToOpen.extend(outputFiles)
        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                           'Finished running the CoNLL table K-sentences analyzer at',
                                           True, '', True, startTime, False)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 GUI_util.data_transformation_options_widget.get(),
                                 searchedCoNLLField_var.get(),
                                 searchField_kw_var.get(),
                                 postag_var.get(),
                                 deprel_var.get(),
                                 co_postag_var.get(),
                                 co_deprel_var.get(),
                                 Begin_K_sent_var.get(),
                                 End_K_sent_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=640, # height at brief display
                                                 GUI_height_full=680, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for CoNLL Table Analyzer'
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
config_input_output_numeric_options=[1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

csv_file_var= tk.StringVar()
extra_GUIs_var = tk.IntVar()
run_parser_var = tk.IntVar()
# Advanced CoNLL analyses companion selectors (ported from semantic_aggregation_main; user places the widgets)
noun_verb_menu_var = tk.StringVar()
noun_verb_menu_var.set('NOUN & VERB')  # default: process both; pick 'NOUN' or 'VERB' in the (user-placed) dropdown to restrict
knowledge_base_menu_var = tk.StringVar()
knowledge_base_menu_var.set('*')
dict_WordNet_filename_var = tk.StringVar()

extra_GUIs_menu_var = tk.StringVar()
all_analyses = tk.StringVar()
advanced_analyses = tk.StringVar()
searchField_kw_var = tk.StringVar()
searchField_POS_var = tk.StringVar()

searchedCoNLLField_var = tk.StringVar()
k_words_var = tk.IntVar()
before_K_words_var = tk.IntVar()
after_K_words_var = tk.IntVar()
postag_var = tk.StringVar()
deprel_var = tk.StringVar()
co_postag_var = tk.StringVar()
co_postag_var = tk.StringVar()
co_deprel_var = tk.StringVar()
k_sentences_var = tk.IntVar()
Begin_K_sent_var = tk.IntVar()
End_K_sent_var = tk.IntVar()
csv_file_field_list = []

clausal_analysis_var = tk.IntVar()

compute_sentence_var = tk.IntVar()

all_analyses_var = tk.IntVar()
advanced_analyses_var = tk.IntVar()
WordNet_var = tk.IntVar()  # dormant: old WordNet checkbox removed (Advanced menu replaces it); kept defined so run()/clear() don't NameError

buildString = ''
menu_values = []
error = False

postag_menu = '*', 'JJ* - Any adjective', 'NN* - Any noun', 'VB* - Any verb', *sorted([k + " - " + v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()])
deprel_menu = '*', *sorted([k + " - " + v for k, v in Stanford_CoreNLP_tags_util.dict_DEPREL.items()])

def clear(e):
    extra_GUIs_var.set(0)
    all_analyses_var.set(0)
    advanced_analyses_var.set(0)
    all_analyses_checkbox.configure(state='normal')
    all_analyses_menu.configure(state='disabled')
    all_analyses.set('*')
    advanced_analyses.set('*')
    search_token_var.set(0)
    searchField_kw_var.set('e.g.: father or * for all tokens in the CoNLL table')
    postag_var.set('*')
    deprel_var.set('*')
    co_postag_var.set('*')
    co_postag_var.set('*')
    co_deprel_var.set('*')
    WordNet_var.set(0)
    k_sentences_var.set(0)
    compute_sentence_var.set(0)
    activate_all_options()
    GUI_util.clear("Escape")


def clear_on_escape(e):
    # Escape resets the options (clear) AND additionally clears the input CoNLL textbox + the run-parser checkbox.
    # (clear() itself must NOT clear the csv, because changed_filename calls clear() right after loading a CoNLL.)
    global error
    error = True
    clear(e)
    csv_file_var.set('')
    run_parser_var.set(0)
    GUI_util.run_button.configure(state='disabled')


window.bind("<Escape>", clear_on_escape)

def check_csv_file_headers(csv_file):
    cannotRun=False
    inputIsCoNLL = CoNLL_util.check_CoNLL(csv_file_var.get(), True)
    if inputIsCoNLL:
        reminders_util.checkReminder(scriptName, reminders_util.title_options_input_csv_file,
                                     reminders_util.message_input_csv_file, True)
    return cannotRun

def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    # First offer the CoNLL tables discovered for the current corpus (output/input/default dirs); only fall
    # back to a file dialog if none are found or the user chooses to browse.
    chosen = CoNLL_util.choose_corpus_CoNLL(window, GUI_util.output_dir_path.get(), GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get())
    if chosen is None:
        return ''
    if chosen != '__BROWSE__':
        filePath = chosen
    else:
        if csv_file!='':
            initialFolder=os.path.dirname(os.path.abspath(csv_file_var.get()))
        else:
            initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        nRecords, nColumns =IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords==0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath=''
        else:
            csv_file_var.set(filePath)
            GUI_util.inputFilename.set(filePath)
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv CoNLL table file', [("csv files", "*.csv")],True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,openInputFile_button,
                    True, False, True,False, 90, GUI_IO_util.IO_configuration_menu, "Open INPUT csv CoNLL table file")

csv_file=tk.Entry(window, width=GUI_IO_util.csv_file_width,textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,csv_file)

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
# extra_GUIs_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Ngrams searches & VIEWER','Word searches','Wordnet searches','Data manipulation GUI for more options on querying the CoNLL table','Corpus statistics','Style analysis')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def open_GUI(*args):
    extra_GUIs_menu.configure(state='disabled')
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    else:
        return
    if extra_GUIs_var.get():
        if 'Data manipulation' in extra_GUIs_menu_var.get():
            run_script_util.run_script("data_manipulation_main.py")
        elif 'Style' in extra_GUIs_menu_var.get():
            run_script_util.run_script("style_analysis_main.py")
        if 'Ngrams searches' in extra_GUIs_menu_var.get():
            run_script_util.run_script("NGrams_CoOccurrences_main.py")
        if 'Word searches' in extra_GUIs_menu_var.get():
            run_script_util.run_script("file_search_byWord_main.py")
        if 'Wordnet' in extra_GUIs_menu_var.get():
            run_script_util.run_script("semantic_aggregation_main.py")
        if 'statistics' in extra_GUIs_menu_var.get():
            run_script_util.run_script("statistics_txt_main.py")
extra_GUIs_menu_var.trace('w',open_GUI)

run_parser_var.set(0)
def run_parser_toggled():
    # 'Run the default parser' goes off to PARSE a CoNLL, so it needs no CoNLL in input: enable RUN when ticked;
    # when unticked, restore RUN to its CoNLL-based state (disabled if no valid CoNLL is loaded).
    if run_parser_var.get():
        GUI_util.run_button.configure(state='normal')
    else:
        GUI_util.run_button.configure(state='disabled' if error else 'normal')
run_parser_checkbox = tk.Checkbutton(window, text='Run the default parser (Open GUI)', variable=run_parser_var,
                                    onvalue=1, offvalue=0, command=lambda: run_parser_toggled())
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                             run_parser_checkbox,
                                             False, False, True, False,
                                             90, GUI_IO_util.open_TIPS_x_coordinate,
                                             "Tick the checkbox to run the default parser on the currently selected I/O corpus and prepare the CoNLL table before opening the GUI.")

all_analyses_var = tk.IntVar()
all_analyses_checkbox = tk.Checkbutton(window, state='disabled', variable = all_analyses_var, text='Basic CoNLL analyses',
                                onvalue=1, offvalue=0, command = lambda: activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                                    y_multiplier_integer, all_analyses_checkbox,True)

all_analyses.set('*')
all_analyses_menu = tk.OptionMenu(window, all_analyses, '*', 'Clause analysis', 'Noun analysis', 'Verb analysis', 'Adjective analysis', 'Adverb analysis', 'Function (junk/stop) words analysis','Content/Function ratio analysis')
all_analyses_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               all_analyses_menu,False)

advanced_analyses_var = tk.IntVar()
advanced_analyses_checkbox = tk.Checkbutton(window, state='disabled', variable = advanced_analyses_var, text='Advanced CoNLL analyses',
                                onvalue=1, offvalue=0, command = lambda: activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                                    y_multiplier_integer, advanced_analyses_checkbox,True)
advanced_analyses.set('*')
advanced_analyses_menu = tk.OptionMenu(window, advanced_analyses, '*', 'Classification of Nouns & Verbs via FrameNet, VerbNet, WordNet','Beginning-End K sentences analyzer (repetition finder)','Word Sense Disambiguation (WSD)','Zoom OUT/UP by Sentence Index')
advanced_analyses_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               advanced_analyses_menu,False)

# WordNet_var = tk.IntVar()
# WordNet_checkbox = tk.Checkbutton(window, state='disabled', variable=WordNet_var,  text='Classification of Nouns & Verbs via FrameNet, VerbNet, WordNet', onvalue=1,
#                                   offvalue=0, command = lambda:  activate_all_options())
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
#                                                     y_multiplier_integer, WordNet_checkbox)

search_token_var = tk.IntVar()
searchToken_checkbox = tk.Checkbutton(window, state='disabled', variable=search_token_var,  text='Search token/word', onvalue=1,
                                  offvalue=0, command = lambda:  activate_all_options())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                                    y_multiplier_integer, searchToken_checkbox,True)

searchField_kw_var.set('e.g.: father or * for all tokens in the CoNLL table')
# search_kw_var = tk.IntVar()
# searchKw_checkbox = tk.Checkbutton(window, state='disabled', variable=search_token_var,  text='Search token/word', onvalue=1,
#                                   offvalue=0, command = lambda:  activate_all_options())
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+70,
#                                                     y_multiplier_integer, searchKw_checkbox,True)
#
# used to place noun/verb checkboxes starting at the top level
y_multiplier_integer_top = y_multiplier_integer

entry_searchField_kw = tk.Entry(window, width=GUI_IO_util.combobox_width, state='disabled', textvariable=searchField_kw_var)
# place widget with hover-over info
#labels_x_indented_coordinate+140
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    entry_searchField_kw,
    False, False, False, False, 90, GUI_IO_util.watch_videos_x_coordinate,
    "Enter the CASE SENSITIVE word (ONE WORD ONLY) that you would like to search (* for any word). All searches are done WITHIN EACH SENTENCE for the EXACT word.")

# search_POS_var = tk.IntVar()
# searchPOS_checkbox = tk.Checkbutton(window, state='disabled', variable=search_POS_var,  text='Search POS', onvalue=1,
#                                   offvalue=0, command = lambda:  activate_all_options())
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate+130,
#                                                     y_multiplier_integer, searchPOS_checkbox,True)
# searchField_POS_var.set('e.g.: NN*')
#
# entry_searchField_POS = tk.Entry(window, width=GUI_IO_util.combobox_width, state='disabled', textvariable=searchField_POS_var)
# # place widget with hover-over info
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+70,
#     y_multiplier_integer,
#     entry_searchField_POS,
#     False, False, False, False, 90, GUI_IO_util.IO_configuration_menu,
#     "Enter the CASE SENSITIVE word (ONE WORD ONLY) that you would like to search (* for any word). All searches are done WITHIN EACH SENTENCE for the EXACT word.")
#

# Search type var (FORM/LEMMA)
searchedCoNLLField_var.set('FORM')
searchedCoNLLdescription_csv_field_menu_lb = tk.Label(window, text='CoNLL search field')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               searchedCoNLLdescription_csv_field_menu_lb,True)

searchedCoNLLdescription_csv_field_menu_lb = tk.OptionMenu(window, searchedCoNLLField_var, 'FORM', 'LEMMA')
searchedCoNLLdescription_csv_field_menu_lb.configure(width=GUI_IO_util.combobox_width, state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               searchedCoNLLdescription_csv_field_menu_lb)

k_words_var.set(0)
k_words_checkbox = tk.Checkbutton(window, text="Before-After K words",
                              variable=k_words_var, onvalue=1, offvalue=0, command = lambda: activate_all_options())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_indented_coordinate,
                                               y_multiplier_integer,
                                               k_words_checkbox, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_indented_coordinate,
                                               "Tick the checkbox if you want to search the CoNLL table for the selected word and extract a number of words BEFORE and AFTER the search word.\nTHE OPTION IS NOT AVAILABLE YET.")

before_K_words_entry_lb = tk.Label(window,
                                    text='Before K-words')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                                               before_K_words_entry_lb, True)

before_K_words_entry = tk.Entry(window, textvariable=before_K_words_var)
before_K_words_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+130,
                                               y_multiplier_integer,
                                               before_K_words_entry, True, False, False, False, 90,
                                               GUI_IO_util.file_splitter_split_mergedFile_separator_entry_begin_pos,
                                               "Enter the integer number of words (do not enter -) to be extracted BEFORE the selected search word")

after_K_words_entry_lb = tk.Label(window,
                                    text='After K-words')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate, y_multiplier_integer,
                                               after_K_words_entry_lb, True)

after_K_words_entry = tk.Entry(window, textvariable=after_K_words_var)
after_K_words_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate+120,
                                               y_multiplier_integer,
                                               after_K_words_entry, False, False, False, False, 90,
                                               GUI_IO_util.file_splitter_split_mergedFile_separator_entry_end_pos,
                                               "Enter the integer number of words (do not enter +) to be extracted AFTER the selected search word")


search_token_lb = tk.Label(window, text='Searched token')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               search_token_lb, True)

# POSTAG variable
postag_var.set('*')
POS_lb = tk.Label(window, text='POSTAG')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+140, y_multiplier_integer,
                                               POS_lb, True)

postag_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = postag_var)
postag_menu_lb['values'] = postag_menu
postag_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               postag_menu_lb,True)

# DEPREL variable

deprel_var.set('*')
DEPREL_lb = tk.Label(window, text='DEPREL')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               DEPREL_lb, True)

deprel_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = deprel_var)
deprel_menu_lb['values'] = deprel_menu
deprel_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+70, y_multiplier_integer,
                                               deprel_menu_lb)

# Co-Occurring POSTAG menu
CoOc_lb = tk.Label(window, text='Co-occurring tokens')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate, y_multiplier_integer,
                                               CoOc_lb, True)

co_postag_var.set('*')

POSTAG_CoOc_lb = tk.Label(window, text='POSTAG')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate+140, y_multiplier_integer,
                                               POSTAG_CoOc_lb, True)

co_postag_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = co_postag_var)
co_postag_menu_lb['values'] = postag_menu
co_postag_menu_lb.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               co_postag_menu_lb, True)

co_deprel_menu = '*','acl - clausal modifier of noun (adjectival clause)', 'acl:relcl - relative clause modifier', 'acomp - adjectival complement', 'advcl - adverbial clause modifier', 'advmod - adverbial modifier', 'agent - agent', 'amod - adjectival modifier', 'appos - appositional modifier', 'arg - argument', 'aux - auxiliary', 'auxpass - passive auxiliary', 'case - case marking', 'cc - coordinating conjunction', 'ccomp - clausal complement with internal subject', 'cc:preconj - preconjunct','compound - compound','compound:prt - phrasal verb particle','conj - conjunct','cop - copula conjunction','csubj - clausal subject','csubjpass - clausal passive subject','dep - unspecified dependency','det - determiner','det:predet - predeterminer','discourse - discourse element','dislocated - dislocated element','dobj - direct object','expl - expletive','foreign - foreign words','goeswith - goes with','iobj - indirect object','list - list','mark - marker','mod - modifier','mwe - multi-word expression','name - name','neg - negation modifier','nn - noun compound modifier','nmod - nominal modifier','nmod:npmod - noun phrase as adverbial modifier','nmod:poss - possessive nominal modifier','nmod:tmod - temporal modifier','nummod - numeric modifier','npadvmod - noun phrase adverbial modifier','nsubj - nominal subject','nsubjpass - passive nominal subject','num - numeric modifier','number - element of compound number','parataxis - parataxis','pcomp - prepositional complement','pobj - object of a preposition','poss - possession modifier', 'possessive - possessive modifier','preconj - preconjunct','predet - predeterminer','prep - prepositional modifier','prepc - prepositional clausal modifier','prt - phrasal verb particle','punct - punctuation','quantmod - quantifier phrase modifier','rcmod - relative clause modifier','ref - referent','remnant - remnant in ellipsis','reparandum - overridden disfluency','ROOT - root','sdep - semantic dependent','subj - subject','tmod - temporal modifier','vmod - reduced non-finite verbal modifier','vocative - vocative','xcomp - clausal complement with external subject','xsubj - controlling subject','# - #'

co_deprel_var.set('*')
DEPREL_CoOc_lb = tk.Label(window, text='DEPREL')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                                               DEPREL_CoOc_lb, True)

co_deprel_menu_lb = ttk.Combobox(window, width = GUI_IO_util.combobox_width, textvariable = co_deprel_var)
co_deprel_menu_lb['values'] = deprel_menu
co_deprel_menu_lb.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate+70
                                             , y_multiplier_integer,co_deprel_menu_lb)

# WordNet_var = tk.IntVar()
# WordNet_checkbox = tk.Checkbutton(window, state='disabled', variable=WordNet_var,  text='WordNet classification of Nouns & Verbs', onvalue=1,
#                                   offvalue=0, command = lambda:  activate_all_options())
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
#                                                     y_multiplier_integer, WordNet_checkbox)

def changed_filename(tracedInputFile):
    global error
    if os.path.isfile(tracedInputFile):
        if not CoNLL_util.check_CoNLL(tracedInputFile,True):
            error = True
            GUI_util.run_button.configure(state='normal' if run_parser_var.get() else 'disabled')
            return
        else:
            error = False
    else:
        error = True
    # enable RUN once a valid CoNLL is loaded (or when 'Run the default parser' is ticked); else disable
    GUI_util.run_button.configure(state='normal' if (not error or run_parser_var.get()) else 'disabled')
    activate_all_options()
    clear("<Escape>")
# GUI_util.inputFilename.trace('w', lambda x, y, z: changed_filename(GUI_util.inputFilename.get()))

# k_sentences_var.set(0)
# k_sentences_checkbox = tk.Checkbutton(window, text="Beginning-End K sentences analyzer (repetition finder)",
#                               variable=k_sentences_var, onvalue=1, offvalue=0, command = lambda: activate_all_options())
# # k_sentences_checkbox.configure(state='disabled')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
#                                                k_sentences_checkbox,True)
#
# Begin_K_sent_entry_lb = tk.Label(window,
#                                     text='Begin K-sentences')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
#                                                Begin_K_sent_entry_lb, True)
#
# Begin_K_sent_entry = tk.Entry(window, textvariable=Begin_K_sent_var)
# Begin_K_sent_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate+130,
#                                                y_multiplier_integer,
#                                                Begin_K_sent_entry, True, False, False, False, 90,
#                                                GUI_IO_util.file_splitter_split_mergedFile_separator_entry_begin_pos,
#                                                "Enter the beginning number of sentences to be analyzed in the CoNLL table for repeated elements")
#
# End_K_sent_entry_lb = tk.Label(window,
#                                     text='End K-sentences')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate, y_multiplier_integer,
#                                                End_K_sent_entry_lb, True)
#
# End_K_sent_entry = tk.Entry(window, textvariable=End_K_sent_var)
# End_K_sent_entry.configure(width=GUI_IO_util.widget_width_extra_short, state='disabled')
# # place widget with hover-over info
# y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate+120,
#                                                y_multiplier_integer,
#                                                End_K_sent_entry, False, False, False, False, 90,
#                                                GUI_IO_util.file_splitter_split_mergedFile_separator_entry_end_pos,
#                                                "Enter the end number of sentences to be analyzed in the CoNLL table for repeated elements")

all_analyses_checkbox.configure(state='normal')
searchToken_checkbox.configure(state='normal')
# k_sentences_checkbox.configure(state='normal')


def activate_all_options():
    extra_GUIs_checkbox.configure(state='normal')
    extra_GUIs_menu.configure(state='disabled')
    all_analyses_checkbox.configure(state='normal')
    all_analyses_menu.configure(state='disabled')
    advanced_analyses_checkbox.configure(state='normal')
    advanced_analyses_menu.configure(state='disabled')
    searchToken_checkbox.configure(state='normal')
    # WordNet_checkbox.configure(state='normal')
    # k_sentences_checkbox.configure(state='normal')
    # k_words_checkbox.configure(state='disabled')
    # before_K_words_entry.configure(state='disabled')
    # after_K_words_entry.configure(state='disabled')


    # search tokens

    entry_searchField_kw.configure(state='disabled')
    searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
    postag_menu_lb.configure(state='disabled')
    deprel_menu_lb.configure(state='disabled')
    co_postag_menu_lb.configure(state='disabled')
    co_deprel_menu_lb.configure(state='disabled')
    # WordNet_checkbox.configure(state='disabled')

    # k sentences options
    # Begin_K_sent_entry.configure(state='disabled')
    # End_K_sent_entry.configure(state='disabled')

    if error:
        extra_GUIs_checkbox.configure(state='disabled')
        all_analyses_checkbox.configure(state='disabled')
        all_analyses_menu.configure(state='disabled')
        advanced_analyses_checkbox.configure(state='disabled')
        advanced_analyses_menu.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        # k_sentences_checkbox.configure(state='disabled')
        return
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        # k_words_checkbox.configure(state='disabled')
        # k_sentences_checkbox.configure(state='disabled')
    elif all_analyses_var.get():
        all_analyses_menu.configure(state='normal')
        extra_GUIs_checkbox.configure(state='disabled')
        advanced_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        # k_sentences_checkbox.configure(state='disabled')
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_CoreNLP_nn_parser,
                                     reminders_util.message_CoreNLP_nn_parser,
                                     True)
    elif advanced_analyses_var.get():
        advanced_analyses_menu.configure(state='normal')
        extra_GUIs_checkbox.configure(state='disabled')
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
    elif search_token_var.get()==True:
        extra_GUIs_checkbox.configure(state='disabled')
        all_analyses_checkbox.configure(state='disabled')
        # k_words_checkbox.configure(state='disabled')
        # k_sentences_checkbox.configure(state='disabled')
        entry_searchField_kw.configure(state='normal')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='normal')
        postag_menu_lb.configure(state='normal')
        deprel_menu_lb.configure(state='normal')
        co_postag_menu_lb.configure(state='normal')
        co_deprel_menu_lb.configure(state='normal')
        k_words_checkbox.configure(state='normal')
    # elif WordNet_var.get():
    #     WordNet_checkbox.configure(state='normal')
    #
    #     extra_GUIs_checkbox.configure(state='disabled')
    #     all_analyses_checkbox.configure(state='disabled')
    #     k_words_checkbox.configure(state='disabled')
    #     searchToken_checkbox.configure(state='disabled')
    #     entry_searchField_kw.configure(state='disabled')
    #     searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
    #     postag_menu_lb.configure(state='disabled')
    #     deprel_menu_lb.configure(state='disabled')
    #     co_postag_menu_lb.configure(state='disabled')
    #     co_deprel_menu_lb.configure(state='disabled')
    #     k_sentences_checkbox.configure(state='disabled')
    #     Begin_K_sent_entry.configure(state='disabled')
    #     End_K_sent_entry.configure(state='disabled')
    # elif k_words_var.get():
    #     mb.showwarning(title='Warning',
    #                    message="The option is not available yet. Try again soon.\n\nSorry!")
    #     return
    #     extra_GUIs_checkbox.configure(state='disabled')
    #     all_analyses_checkbox.configure(state='disabled')
    #     searchToken_checkbox.configure(state='disabled')
    #     entry_searchField_kw.configure(state='disabled')
    #     before_K_words_entry.configure(state='normal')
    #     after_K_words_entry.configure(state='normal')
    #     searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
    #     postag_menu_lb.configure(state='disabled')
    #     deprel_menu_lb.configure(state='disabled')
    #     co_postag_menu_lb.configure(state='disabled')
    #     co_deprel_menu_lb.configure(state='disabled')
    #     k_sentences_checkbox.configure(state='disabled')
    #     Begin_K_sent_entry.configure(state='disabled')
    #     End_K_sent_entry.configure(state='disabled')
    elif compute_sentence_var.get():
        extra_GUIs_checkbox.configure(state='disabled')
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        entry_searchField_kw.configure(state='disabled')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
        postag_menu_lb.configure(state='disabled')
        deprel_menu_lb.configure(state='disabled')
        co_postag_menu_lb.configure(state='disabled')
        co_deprel_menu_lb.configure(state='disabled')
        # k_sentences_checkbox.configure(state='disabled')
    elif k_sentences_var.get():
        extra_GUIs_checkbox.configure(state='disabled')
        all_analyses_checkbox.configure(state='disabled')
        searchToken_checkbox.configure(state='disabled')
        entry_searchField_kw.configure(state='disabled')
        searchedCoNLLdescription_csv_field_menu_lb.configure(state='disabled')
        postag_menu_lb.configure(state='disabled')
        deprel_menu_lb.configure(state='disabled')
        co_postag_menu_lb.configure(state='disabled')
        co_deprel_menu_lb.configure(state='disabled')
        # Begin_K_sent_entry.configure(state='normal')
        # End_K_sent_entry.configure(state='normal')
    else:
        extra_GUIs_checkbox.configure(state='normal')
        extra_GUIs_menu.configure(state='disabled')
        all_analyses_checkbox.configure(state='normal')
        all_analyses_menu.configure(state='disabled')
        advanced_analyses_checkbox.configure(state='normal')
        advanced_analyses_menu.configure(state='disabled')
        searchToken_checkbox.configure(state='normal')
        # WordNet_checkbox.configure(state='normal')
        # k_sentences_checkbox.configure(state='normal')
    # if k_words_var.get():
    #     mb.showwarning(title='Warning',
    #                    message="The option is not available yet. Try again soon.\n\nSorry!")
    #     k_words_var.set(0)
    #     return

activate_all_options()

videos_lookup = {'CoNLL Table Analyzer 1':'https://www.youtube.com/watch?v=I-knso52gbM', 'CoNLL Table Analyzer 2':'https://youtu.be/5pkHaCJmsPk'}
videos_options='CoNLL Table Analyzer 1','CoNLL Table Analyzer 2'

TIPS_lookup = {'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'POSTAG (Part of Speech Tags)': "TIPS_NLP_POSTAG (Part of Speech Tags) Stanford CoreNLP.pdf",
               'DEPREL (Stanford Dependency Relations)': "TIPS_NLP_DEPREL (Dependency Relations) Stanford CoreNLP.pdf",
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Style Analysis': 'TIPS_NLP_Style Analysis.pdf', 'Clause Analysis': 'TIPS_NLP_Clause Analysis.pdf',
               'Noun Analysis': 'TIPS_NLP_Noun Analysis.pdf', 'Verb Analysis': 'TIPS_NLP_Verb Analysis.pdf',
               'Function Words Analysis': 'TIPS_NLP_Function Words Analysis.pdf',
               'Nominalization': 'TIPS_NLP_Nominalization.pdf', 'NLP Searches': "TIPS_NLP_NLP Searches.pdf",
               'WordNet': 'TIPS_NLP_WordNet.pdf',
               'Excel Charts': 'TIPS_NLP_Excel Charts.pdf',
               'Excel Enabling Macros': 'TIPS_NLP_Excel Enabling macros.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
                'Statistical measures':'TIPS_NLP_Statistical measures.pdf',
               'Network Graphs (via Gephi)': 'TIPS_NLP_Gephi network graphs.pdf'}
TIPS_options = 'CoNLL Table', 'POSTAG (Part of Speech Tags)', 'DEPREL (Stanford Dependency Relations)', 'English Language Benchmarks', 'Style Analysis', 'Clause Analysis', 'Noun Analysis', 'Verb Analysis', 'Function Words Analysis', 'Nominalization', 'WordNet', 'NLP Searches', 'Excel Charts', 'Excel Enabling Macros', 'Excel smoothing data series', 'Statistical measures', 'Network Graphs (via Gephi)'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_CoNLL)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, use the 'Select INPUT CSV file' button to choose the CoNLL table to analyze.\n\nThe button first LISTS all CoNLL tables found for your current corpus - searching the output directory, the input directory, and the default output directory - so you can pick one directly without hunting for the file (each is labelled by its parser/corpus subfolder, e.g. a Stanza dependency parse vs a CoreNLP parse). You can also choose 'Browse for another file' to select any other CoNLL csv. If no CoNLL table is found, a file dialog opens directly.\n\nA CoNLL table is a csv file produced by a parser (spaCy, Stanford CoreNLP, or Stanza) via the Parsers & annotators GUI, in which each token is labeled with a part-of-speech tag (POSTAG), a Dependency Relation tag (DEPREL), and other linguistic information.\n\nThe selected file is validated to ensure it is a properly formatted CoNLL table." + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for searches and style analysis.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Tick 'Run the default parser (Open GUI)' when you do not yet have a CoNLL table: it opens the Parsers & Annotators GUI (with the parser and 'Open CoNLL table analyzer' pre-ticked). Run it there to parse your corpus with the configured parser, and this analyzer reopens loaded with the fresh CoNLL table." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox to analyze the CoNLL table for different types of clauses (e.g., noun-phrase, NP, verb phrase, VP), nouns (singular, plural, proper nouns, subject and object), verbs (modality, tense, voice), functions words (or junk/stop words) (e.g., articles/determinants, auxiliaries, conjunctions, prepositions, pronouns), adjectives, adverbs, and ratios of word classes (e.g., content words vs. junk words).\n\nThe CoNLL table analyzer works with CoNLL tables produced by any parser (spaCy, Stanford CoreNLP, Stanza).\n\nDEPENDENCY vs. CONSTITUENCY PARSING\nAll parsers (spaCy, Stanza, Stanford CoreNLP) produce dependency parse trees, which represent word-to-word grammatical relations (e.g., nsubj, obj, advmod). These relations power noun, verb, function word, and search analyses.\n\nConstituency parsing produces phrase-structure trees that group words into nested phrases (NP, VP, S, SBAR, PP, etc.). ONLY the Stanford CoreNLP PCFG parser and the Stanza constituency parser produce clause tags. No other parser provides clause tags. Without clause tags, the Clause analysis option will be skipped.\n\nCLAUSE TAGS\nClause tags label each token with its lowest enclosing phrase type (e.g., S for main clause, SBAR for subordinate clause, NP for noun phrase, VP for verb phrase). These tags enable analysis of clause types, clause length, and clause distribution across a text.\n\nTHE 'feats' COLUMN (Stanza only)\nStanza exports morphological features in the 'feats' column (e.g., Mood=Ind, Tense=Past, VerbForm=Fin, Number=Sing). This enables analysis of verb mood (indicative, imperative, subjunctive), verb tense (past, present, future), verb form (finite, infinitive, participle, gerund), and noun number (singular, plural). Neither spaCy nor Stanford CoreNLP export this information. These features are especially valuable for languages with rich morphology (e.g., Italian, German, French).\n\nNote: The Stanford CoreNLP neural network parser does NOT produce clause tags (only the PCFG parser - Probabilistic Context Free Grammar). spaCy does not support constituency parsing." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick 'Advanced CoNLL analyses' and pick an option from the dropdown:\n\n- Classification of Nouns & Verbs: aggregate the nouns/verbs in the CoNLL table into FrameNet, VerbNet, and WordNet categories.\n- Word Sense Disambiguation (WSD): disambiguate each noun/verb in its sentence context (Lesk algorithm) and aggregate to the context-correct WordNet category.\n- Zoom OUT/UP by Sentence Index: using an aggregation dictionary (a Zoom OUT/UP output mapping words to categories), plot where those WordNet/VerbNet/FrameNet categories occur across the sentences.\n- Beginning-End K sentences (repetition finder): content words that repeat in BOTH the first K and the last K sentences of a document (bookend repetition), plus counts/proportions of word classes in those sentences.\n\nBoth nouns and verbs are processed by default; use the NOUN/VERB selector to restrict to one.\n\nCAVEAT: For VERBS, the WordNet 'stative' category includes the auxiliary 'be' and 'possession' includes 'have'/'get'; you may wish to exclude these auxiliaries from frequencies." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checbox to search the CoNLL table for a specific token/word. Enter the CASE SENSITIVE token (i.e., word) to be searched (enter * for any word).\n\nENTER * TO SEARCH FOR ANY TOKEN/WORD.\n\nThe EXACT word will be searched (e.g., if you enter 'American', any instances of 'America' will not be found).\n\nDO NOT USE QUOTES WHEN ENTERING A SEARCH TOKEN. n\nThe algorithm will search all the tokens related to this token in the CoNLL table. For example, if the the token wife is entered, the algorithm will search in each dependency tree (i.e., each sentence).\n\nIn OUTPUT the algorithm will produce several charts and a Gephi network graphs of the relationship between searched and co-occurring words." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select the CoNLL field to be used for the search (FORM or LEMMA).\n\nFor example, if brother is entered as the searched token, and FORM is entered as search field, the algorithm will first search all occurrences of the FORM brother. Note that in this case brothers will NOT be considered. Otherwise, if LEMMA is entered as search field, the algorithm will search all occurences of the LEMMA brother. In this case, tokens with form brother and brothers will all be considered." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to search the CoNLL table for a selected search word and extract a selected number of words appearing BEFORE and AFTER in a sentence." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select POSTAG value for searched token (e.g., NN for noun; RETURN for ANY POSTAG value).\n\n" \
                                  "Select DEPREL value for searched token (e.g., nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, select POSTAG value for token co-occurring in the same sentence (e.g., NN for noun; RETURN for ANY POSTAG value).\n\n" \
                                  "Select DEPREL value for token co-occurring in the same sentence (e.g., DEPREL nsubjpass for passive nouns that are subjects; RETURN for ANY DEPREL value)." + GUI_IO_util.msg_Esc)
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
    #                               "Please, tick the checkbox if you wish to run the repetition finder to compute counts and proportions of nouns, verbs, adjectives, and proper nouns across selected K beginnning and ending sentences." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, increment)

# change the value of the readMe_message
readMe_message = "This Python 3 script will allow you to analyze in depth the contents of a CoNLL table (CoNLL U format) produced by Stanford CoreNLP, Stanza, or spaCy. You can do several things in this GUI.\n\nYou can get frequency distributions of various types of linguistic objects: clauses (CoreNLP or Stanza with constituency parsing), nouns, verbs, and function words.\n\nYou can search all the tokens (i.e., words) related to a user-supplied keyword, found in either FORM or LEMMA of a user-supplied CoNLL table. You can filter your search by specific POSTAG and DEPREL values for both searched and co-occurring tokens (e.g., POSTAG ‘NN for nouns, DEPREL nsubjpass for passive nouns that are subjects.)\n\nYou can get frequency distributions of words and nouns, verbs, adjectives, and proper nouns in the first and last K sentences.\n\nIn INPUT the script expects a CoNLL table generated by Stanford CoreNLP, Stanza, or spaCy. \n\nIn OUTPUT the script creates a tab-separated csv file with a user-supplied filename and path.\n\nThe script also displays the same infomation in the command line." + GUI_IO_util.msg_multipleDocsCoNLL
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
scriptName=os.path.basename(__file__)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,scriptName,True)

conll_from_argv = False
if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) and sys.argv[1].endswith('.csv'):
    GUI_util.inputFilename.set(sys.argv[1])
    csv_file_var.set(sys.argv[1])
    conll_from_argv = True

if conll_from_argv:
    GUI_util.run_button.configure(state='normal')
elif GUI_util.input_main_dir_path.get()!='' or (os.path.basename(GUI_util.inputFilename.get())[-4:] != ".csv"):
    GUI_util.run_button.configure(state='disabled')
    mb.showwarning(title='Input file',
                   message="The CoNLL Table Analyzer scripts require in input a csv CoNLL table created by Stanford CoreNLP, Stanza, or spaCy.\n\nAll options and RUN button are disabled until a valid CoNLL file is selected in input.\n\nPlease, click on the button Setup INPUT/OUTPUT configuration to select a CoNLL file in input.")
    error = True
    activate_all_options()
else:
    GUI_util.run_button.configure(state='normal')
    if inputFilename.get()!='':
        if CoNLL_util.check_CoNLL(inputFilename.get()):
            csv_file_var.set(inputFilename.get())
        else:
            error = True
            activate_all_options()

def on_inputFilename_changed(*args):
    tracedInputFile = GUI_util.inputFilename.get()
    if os.path.isfile(tracedInputFile) and CoNLL_util.check_CoNLL(tracedInputFile, True):
        csv_file_var.set(tracedInputFile)
    changed_filename(tracedInputFile)

GUI_util.inputFilename.trace('w', lambda x, y, z: on_inputFilename_changed())

activate_all_options()

GUI_util.window.lift()
GUI_util.window.focus_force()

GUI_util.window.mainloop()
