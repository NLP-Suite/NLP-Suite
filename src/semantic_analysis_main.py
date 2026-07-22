
# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"semantic_analysis_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import tkinter as tk
from subprocess import call

import GUI_IO_util
import IO_files_util
import file_spell_checker_util
import statistics_txt_util
import style_analysis_abstract_concreteness_analysis_util
import Stanza_util
import reminders_util
import config_util
import run_script_util

# RUN section ______________________________________________________________________________________________________________________________________________________



def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    extra_GUIs_var = globals()['extra_GUIs_var'].get()
    extra_GUIs_menu_var = globals()['extra_GUIs_menu_var'].get()
    WSI_var = globals()['WSI_var'].get()
    WSI_keywords_var = globals()['WSI_keywords_var'].get()
    WSIdictionary_file_var = globals()['WSIdictionary_file_var'].get()
    WSD_var = globals()['WSD_var'].get()
    SRL_var = globals()['SRL_var'].get()
    SSC_var = globals()['SSC_var'].get()
    vocabulary_analysis_var = globals()['vocabulary_analysis_var'].get()
    vocabulary_analysis_menu_var = globals()['vocabulary_analysis_menu_var'].get()


    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []  # Store all files that are to be opened once finished

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    # filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    #     config_filename, config_input_output_numeric_options)
    # extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    openOutputFilesSV=openOutputFiles
    outputDir_style=outputDir


    if (extra_GUIs_var == False and
        WSI_var == False and
        WSD_var == False and
        SRL_var == False and
        SSC_var == False and
        vocabulary_analysis_var == False):
        mb.showwarning('Warning','No options have been selected.\n\nPlease, select an option and try again.')
        return

    if WSI_var == 1:
        if WSI_keywords_var=='':
            mb.showwarning(title='Missing keywords',message='The "Word Sense Induction" algorithm requires a comma-separated list of case-sensitive keywords taken from the corpus in order to run.\n\nPlease, enter the keywords and try again.')
            return

        import WSI_util, WSI_viz, WSI_keyterms

        all_sent, all_vocab, Word2Vec_Dir, docs, paths = WSI_util.get_data(inputFilename, inputDir, Word2Vec_Dir, u_vocab=WSI_keywords_var.get(), fileType='.txt', configFileName=config_filename)
        k_range = (k_means_min_var.get(), k_means_max_var.get())
        WSI_util.get_centroids(all_sent, all_vocab, Word2Vec_Dir, k_range)
        WSI_util.match_embeddings(all_sent, all_vocab, Word2Vec_Dir)
        s_paths = WSI_util.get_cluster_sentences(Word2Vec_Dir)
        v_paths = WSI_viz.sense_bar_chart(Word2Vec_Dir)
        n = int(ngrams_menu_var.get().split('-')[0])
        k_paths = WSI_keyterms.get_keyterms(Word2Vec_Dir, topn=top_keywords_var.get(), ngram_range=(1, n))
        filesToOpen = s_paths + v_paths + k_paths

    if WSD_var:
        if not "CoNLL" in inputFilename and not "CoNLL" in csv_file.get():
            mb.showwarning(title='Warning',message="The script Word Sense Disambiguation (WSD) algorithm requires a CoNLL FILE in INPUT.\n\n" \
                                                                                  "Please, select a csv CoNLL file in I/O comfiguration or select a CoNLL file using the 'Select INPUT CSV file' button and try again.")
            return
        import semantic_aggregation_util
        # WSD writes into a dedicated subdirectory (keeps the outputs out of the cluttered main output dir)
        wsd_outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='WSD', silent=True) or outputDir
        noun_verb_list = ['NOUN', 'VERB']
        for noun_verb in noun_verb_list:
            outFiles = semantic_aggregation_util.wsd_aggregate_WordNet(inputFilename, wsd_outputDir, noun_verb, chartPackage, dataTransformation)
            if outFiles:
                filesToOpen.extend(outFiles)

    if SRL_var == 1:
        # SRL now has its own dedicated GUI (SRL_main.py); open it rather than running inline,
        # so the hub inherits future SRL options (engine choice, nominal SRL). The engine itself
        # still lives in SRL_util.run_SRL, called from that GUI.
        run_script_util.run_script("SRL_main.py")

    # DOCUMENT embeddings: semantic similarity & clustering (SBERT). Promoted from the old
    # 'More semantic analyses' dropdown to its own checkbox; runs inline like WSD.
    if SSC_var == 1:
        import semantic_similarity_util
        # write the similarity matrix/heatmap/clusters into a dedicated subdirectory
        # (keeps them out of the cluttered main output dir)
        simDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='semantic_similarity', silent=True) or outputDir
        outFiles = semantic_similarity_util.document_similarity_clustering(window, inputFilename, inputDir, simDir, openOutputFiles, chartPackage, dataTransformation)
        if outFiles:
            filesToOpen.extend(outFiles)

    # vocabulary analysis    ---------------------------------------------------------------------

    if vocabulary_analysis_var == True:
        openOutputFilesSV=openOutputFiles
        openOutputFiles = False  # to make sure files are only opened at the end of this multi-tool script
        if vocabulary_analysis_menu_var=='':
            mb.showwarning('Warning', 'No option has been selected for Vocabulary analysis.\n\nPlease, select an option and try again.')
            return

        if 'Iconic' in vocabulary_analysis_menu_var:
            mb.showwarning('Warning', 'The selected option is not available yet.\n\nSorry!')
            return

        if '*' == vocabulary_analysis_menu_var:
            outputDir_style = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                                   label='style',
                                                                   silent=True)
            if outputDir_style == '':
                return
        else:
            outputDir_style=outputDir

        if '*' in vocabulary_analysis_menu_var or 'Coreference' in vocabulary_analysis_menu_var:
            run_script_util.run_script("coreference_main.py")
            if mb.askyesno(title='Coreferenced corpus',
                           message="You have run the coreference resolution algorithm, creating a new coreferenced corpus.\n\nDo you want to use the new coreferenced corpus for your analyses in this GUI?"):
                # the coreference GUI writes the coreferenced txt files into a 'coref_*' subdirectory of the
                # output dir (e.g. coref_CoreNLP_<corpus>); use the newest one, descending to the folder that
                # actually holds the txt files, else let the user select the folder.
                import glob
                from tkinter import filedialog
                coref_dir = ''
                outDir = GUI_util.output_dir_path.get()
                if outDir and os.path.isdir(outDir):
                    cands = sorted([d for d in glob.glob(os.path.join(outDir, 'coref_*')) if os.path.isdir(d)],
                                   key=os.path.getmtime, reverse=True)
                    if cands:
                        coref_dir = cands[0]
                        for r, ds, fs in os.walk(cands[0]):
                            if any(f.lower().endswith('.txt') for f in fs):
                                coref_dir = r
                                break
                if not coref_dir:
                    coref_dir = filedialog.askdirectory(title='Select the coreferenced corpus folder (its coreferenced txt files)')
                if coref_dir:
                    GUI_util.input_main_dir_path.set(coref_dir)
                    GUI_util.inputFilename.set('')
                    # refresh the brief INPUT/OUTPUT display panel so it reflects the new corpus;
                    # the panel is built from the config, not the live StringVar, so it must be
                    # rewritten explicitly or the user sees the OLD input dir and thinks nothing changed
                    try:
                        if getattr(GUI_util, 'IO_setup_brief_display_area', None) is not None:
                            io_display = "INPUT DIR: " + os.path.basename(os.path.normpath(coref_dir)) + \
                                         "\nOUTPUT DIR: " + os.path.basename(os.path.normpath(GUI_util.output_dir_path.get()))
                            GUI_util.update_display_area(io_display, GUI_util.IO_setup_brief_display_area)
                    except Exception as e:
                        print("Could not refresh the INPUT/OUTPUT display panel: " + str(e))
                    mb.showinfo(title='Input updated',
                                message="The GUI input is now the coreferenced corpus:\n\n" + coref_dir +
                                        "\n\nThe INPUT/OUTPUT panel above now shows this corpus. "
                                        "Re-run your analyses; they will use it.")
            return

        if '*' in vocabulary_analysis_menu_var or 'Vocabulary (via unigrams)' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, chartPackage,dataTransformation,'unigrams',language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Hapax legomena' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, chartPackage,dataTransformation,'Hapax legomena', language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        #Added this option to be able to test the subjectivity/objectivity output (Naman Sahni 10/01/2022)
        if '*' in vocabulary_analysis_menu_var or 'Objectivity/subjectivity (via spaCy)' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                silent=True
            else:
                silent=False
            import spaCy_util
            # annotator_available = spaCy_util.check_spaCy_annotator_availability(['Objectivity/subjectivity'], language,
            #                                                                     silent)
            annotator_available=True
            if annotator_available:
                outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                            openOutputFiles, 
                                                            chartPackage,dataTransformation,'Objectivity/subjectivity (via spaCy)', language)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Repetition: Words' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                # this will force a deafault setting of k_str = '4' to avoid stopping all algorithms
                process='*Repetition: Words in first K and last K sentences'
            else:
                process = 'Repetition: Words in first K and last K sentences'
            # a reminder about CoNLL table analyzer option is posted in process_words
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, 
                                                       chartPackage,dataTransformation,process,language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Repetition: Last' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                # this will force a deafault setting of k_str = '4' to avoid stopping all algorithms
                process='*Repetition: Last K words of a sentence/First K words of next sentence'
            else:
                process = 'Repetition: Last K words of a sentence/First K words of next sentence'
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, 
                                                       chartPackage, dataTransformation,process, language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Repetition across' in vocabulary_analysis_menu_var:
            if '*' in vocabulary_analysis_menu_var:
                process='*Repetition across sentences (special ngrams)'
            else:
                process = 'Repetition across sentences (special ngrams)'
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles,
                                                       chartPackage, dataTransformation, process, language)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Stanza' in vocabulary_analysis_menu_var:
            annotator = 'Lemma'
            language_list = ['English']
            memory_var = 8
            document_length_var = 1
            limit_sentence_length_var = 1000
            outputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                          outputDir,
                                                          openOutputFiles,
                                                          chartPackage,dataTransformation,
                                                          annotator, False,
                                                          language_list,
                                                          memory_var, document_length_var, limit_sentence_length_var)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'capital' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                                   openOutputFiles, chartPackage,dataTransformation,'capital')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Sentence length' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.compute_sentence_length(inputFilename, inputDir, outputDir,
                                                                      config_filename, chartPackage, dataTransformation)
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Word length' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.process_words(window, config_filename, inputFilename,inputDir, outputDir_style,
                                                      openOutputFiles, chartPackage,dataTransformation,'Word length')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Vowel' in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                       openOutputFiles, chartPackage,dataTransformation,'Vowel')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'pathos' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.process_words(window, config_filename, inputFilename, inputDir, outputDir_style,
                                                      openOutputFiles, chartPackage,dataTransformation,'pathos')
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == vocabulary_analysis_menu_var or 'NLTK' in vocabulary_analysis_menu_var:
            outputFiles =file_spell_checker_util.nltk_unusual_words(window, inputFilename, inputDir, outputDir_style, config_filename, False, chartPackage, dataTransformation)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' == vocabulary_analysis_menu_var or 'Abstract' in vocabulary_analysis_menu_var:
            if language == 'English':
                mode = "both" # mean, median, both (calculates both mean and median)
                outputFiles = style_analysis_abstract_concreteness_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir_style, config_filename, openOutputFiles, chartPackage, dataTransformation,processType='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)
            else:
                if not '*' == vocabulary_analysis_menu_var:
                    mb.showwarning(title='Warning', message='The Abstract/concrete vocabulary analysis algorithm is only available for the English language.')

        if '*' == vocabulary_analysis_menu_var or 'Iconic' in vocabulary_analysis_menu_var:
            if language == 'English':
                mode = "both" # mean, median, both (calculates both mean and median)
                import style_analysis_iconicity_analysis_util
                outputFiles = style_analysis_iconicity_analysis_util.main(GUI_util.window, inputFilename, inputDir, outputDir_style, config_filename, openOutputFiles, chartPackage, dataTransformation, processType='')
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)
            else:
                if not '*' == vocabulary_analysis_menu_var:
                    mb.showwarning(title='Warning', message='The Iconicity analysis algorithm is only available for the English language.')

        if '*' == vocabulary_analysis_menu_var or 'Yule' in vocabulary_analysis_menu_var:
            outputFiles =statistics_txt_util.yule(window, inputFilename, inputDir, outputDir, config_filename)
            if outputFiles!=None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'detection' in vocabulary_analysis_menu_var:
                outputFiles = file_spell_checker_util.language_detection(window, inputFilename, inputDir, outputDir_style, config_filename,
                                                                         openOutputFiles, chartPackage, dataTransformation)
                if outputFiles!=None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'TF-IDF' in vocabulary_analysis_menu_var:
            import statistics_corpus_tfidf_util
            outputFiles = statistics_corpus_tfidf_util.compute_tfidf(inputFilename, inputDir, outputDir_style,
                                                                       chartPackage, dataTransformation)
            if outputFiles is not None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Lexical diversity' in vocabulary_analysis_menu_var:
            import statistics_corpus_lexical_diversity_util
            outputFiles = statistics_corpus_lexical_diversity_util.compute_lexical_diversity(
                inputFilename, inputDir, outputDir_style, chartPackage, dataTransformation)
            if outputFiles is not None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

        if '*' in vocabulary_analysis_menu_var or 'Word frequency distribution' in vocabulary_analysis_menu_var:
            import statistics_corpus_word_frequency_util
            outputFiles = statistics_corpus_word_frequency_util.compute_word_frequency(
                inputFilename, inputDir, outputDir_style, chartPackage, dataTransformation)
            if outputFiles is not None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    openOutputFiles=openOutputFilesSV
    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir_style, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=640, # height at brief display
                             GUI_height_full=600, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Semantic Analysis'
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
config_input_output_numeric_options=[6,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename,config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

csv_file_var= tk.StringVar()
extra_GUIs_var = tk.IntVar()
WSI_var = tk.IntVar()
WSD_var = tk.IntVar()
SRL_var = tk.IntVar()
SSC_var = tk.IntVar() # semantic similarity & clustering

# WSD_menu_var= tk.StringVar()

def clear(e):
    csv_file_var.set('')
    GUI_util.inputFilename.set('')  # get_csv_file stores the CoNLL here too; clear it so RUN doesn't keep it as input
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')

    WSI_var.set(0)
    WSD_var.set(0)
    SRL_var.set(0)
    SSC_var.set(0)

    vocabulary_analysis_var.set(0)

    vocabulary_analysis_menu_var.set('*')

    activate_all_options()
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

# GUI CHANGES cut/paste special GUI widgets from GUI_util

ngrams_list=[]

bySentenceIndex_var=tk.IntVar()

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()
vocabulary_analysis_var=tk.IntVar()

# CoNLL_table_analysis_menu_var=tk.StringVar()
vocabulary_analysis_menu_var=tk.StringVar()



csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: IO_files_util.get_corpus_CoNLL_csv(window, csv_file_var,'Select INPUT csv CoNLL table file', [("csv files", "*.csv")],True))
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
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Coreference resolution (Open GUI)','Spelling/grammar checker (Open GUI)','Corpus statistics (Open GUI)','N-grams & Co-Occurrences (Open GUI)','Nominalization (Open GUI)','CoNLL table analyzer (Open GUI)','WordNet (Open GUI)','Corpus Profiler (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def open_GUI(*args):
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    if extra_GUIs_menu_var.get():
        if 'Spelling' in extra_GUIs_menu_var.get():
            run_script_util.run_script("file_spell_checker_main.py")
        if 'statistics' in extra_GUIs_menu_var.get():
            run_script_util.run_script("statistics_txt_main.py")
        if 'N-grams' in extra_GUIs_menu_var.get():
            run_script_util.run_script("NGrams_CoOccurrences_main.py")
        if 'Nominalization' in extra_GUIs_menu_var.get():
            run_script_util.run_script("nominalization_main.py")
        if 'CoNLL' in extra_GUIs_menu_var.get():
            run_script_util.run_script("CoNLL_table_analyzer_main.py")
        if 'WordNet' in extra_GUIs_menu_var.get():
            run_script_util.run_script("semantic_aggregation_main.py")
        if 'Profile' in extra_GUIs_menu_var.get():
            run_script_util.run_script("corpus_profiler_main.py")
        if 'Coreference' in extra_GUIs_menu_var.get():
            run_script_util.run_script("coreference_main.py")

extra_GUIs_menu_var.trace('w',open_GUI)


## option for WSI via BERT
# Word sense induction (WSI) is the problem of automatically identifying the different senses expressed by a word used in a collection of documents.
WSI_var.set(0)
WSI_checkbox = tk.Checkbutton(window, text='Word Sense Induction (WSI) (via BERT (English language model))', variable=WSI_var, onvalue=1, offvalue=0, command=lambda:activate_all_options())
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,WSI_checkbox,True)

# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    WSI_checkbox,
    True, False, False, False, 90, GUI_IO_util.labels_x_coordinate,
    "Tick the checkbox to run the word sense induction (WSI) algorithm to automatically identify the different senses expressed by a word used in your corpus based on Lucy & Bamman, 2021, BERT model.\nAdjust the various options in the next line of widgets to control the model parameters.")

k_means_min_var = tk.Scale(window, from_=2, to=9, orient=tk.HORIZONTAL)
k_means_min_var.set(4)
# place widget with hover-over info # memory_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_reminders_x_coordinate,
                                               y_multiplier_integer,
                                               k_means_min_var, True, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Use the slider widget to set the K-means MINIMUM value you wish to use for word sense induction")

k_means_max_var = tk.Scale(window, from_=3, to=15, orient=tk.HORIZONTAL)
k_means_max_var.set(6)
# place widget with hover-over info # memory_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_setup_x_coordinate-40,
                                               y_multiplier_integer,
                                               k_means_max_var, True, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Use the slider widget to set the K-means MAXIMUM value you wish to use for word sense induction")

ngrams_lb = tk.Label(window,text='N-grams')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.run_button_x_coordinate-55,y_multiplier_integer,ngrams_lb,True)
ngrams_menu_var = tk.StringVar()
ngrams_menu_var.set('1-grams')
ngrams_menu = tk.OptionMenu(window,ngrams_menu_var, '1-grams (unigrams)','2-grams (bigrams)','3-grams (trigrams)','4-grams (quadgrams)')
# place widget with hover-over info # memory_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.run_button_x_coordinate+25,
                                               y_multiplier_integer,
                                               ngrams_menu, True, False, False, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "Use the dropdown menu to select the N-grams to be used in computing the highest scoring N-grams to return as cluster key terms ")

top_keywords_var = tk.Scale(window, from_=5, to=20, orient=tk.HORIZONTAL)
top_keywords_var.set(10)
# place widget with hover-over info # memory_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate+50,
                                               y_multiplier_integer,
                                               top_keywords_var, False, False, False, False, 90,
                                               GUI_IO_util.run_button_x_coordinate,
                                               "Maximum number of keywords to be returned ")

WSI_keywords_var = tk.StringVar()
WSI_keywords_var.set('')
WSI_keywords_lb = tk.Label(window, text='Keywords (WSI)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,WSI_keywords_lb,True)

WSIdictionary_file_var=tk.StringVar() # dictionary file used to annotate
def get_dictionary_file(window,title,fileType):
    #WSIdictionary_var.set('')
    filePath = tk.filedialog.askopenfilename(title = title, initialdir =outputDir, filetypes = fileType)
    if len(filePath)>0:
        # WSIdictionary_file.config(state='normal')
        WSI_keywords_var.set(filePath)

WSIdictionary_button=tk.Button(window, text='Select dictionary file ',command=lambda: get_dictionary_file(window,'Select INPUT dictionary file', [("dictionary files", "*.csv")]))
# WSIdictionary_button.config(state='disabled')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate + 100, y_multiplier_integer,
                                   WSIdictionary_button,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Click to select a csv file containing a list of words for which disambiguation is sought.\nIf disambiguation is sought for only a few words, please, enter them comma-separated in the entry widget.")

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, WSI_keywords_var.get()))
# openInputFile_button.configure(state='disabled')
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.labels_x_indented_coordinate + 250, y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate + 250, "Open csv dictionary file")

WSI_keywords_entry = tk.Entry(window, textvariable=WSI_keywords_var)
WSI_keywords_entry.configure(state='normal',width=GUI_IO_util.widget_width_extra_long)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+100,
    y_multiplier_integer,
    WSI_keywords_entry,
    False, False, False, False, 90, GUI_IO_util.IO_configuration_menu,
    "Enter the comma-separated, case-sensitive words to be used to compute word sense induction")

WSD_var.set(0)
WSD_checkbox = tk.Checkbutton(window, text='Word Sense Disambiguation (WSD) (via CoNLL)', variable=WSD_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,WSD_checkbox,False)

SRL_var.set(0)
SRL_checkbox = tk.Checkbutton(window, text='Semantic Role Labelling (SRL) (Open GUI)', variable=SRL_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SRL_checkbox,False)

SSC_var.set(0)
SSC_checkbox = tk.Checkbutton(window, text='DOCUMENT embeddings: Semantic similarity & clustering', variable=SSC_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SSC_checkbox,False)

classify_words_by_semantic_closeness_button=tk.Button(window, width=90, text='WORD embeddings: Classify words by semantic proximity: Word2Vec & word embeddings (Open GUI)',command=lambda: run_script_util.run_script("Word2Vec_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               classify_words_by_semantic_closeness_button, False)

semantic_aggregation_button=tk.Button(window, width=90, text='Aggregate words by semantics (Open GUI)',command=lambda: run_script_util.run_script("semantic_aggregation_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               semantic_aggregation_button, False)


vocabulary_analysis_var.set(0)
vocabulary_analysis_checkbox = tk.Checkbutton(window, text='More semantic analyses', variable=vocabulary_analysis_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,vocabulary_analysis_checkbox,True)

# # vocabulary_analysis_menu_var.set('*')
# # vocabulary_analysis_lb = tk.Label(window, text='Select the vocabulary analysis you wish to perform')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,vocabulary_analysis_lb,True)
# place widget with hover-over info
vocabulary_analysis_menu = tk.OptionMenu(window,vocabulary_analysis_menu_var,'*',
                                         'Coreference resolution (Open GUI)',
                                         'Nominalization',
                                         'Abstract/concrete vocabulary',
                                         'Iconic vocabulary',
                                         'Objectivity/subjectivity (via spaCy)',
                                         'Topic modelling')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   vocabulary_analysis_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select the vocabulary analysis you wish to perform (* for all); widget disabled until checkbox ticked,")

def activate_all_options(*args):
    extra_GUIs_checkbox.configure(state='normal')
    extra_GUIs_menu.configure(state='disabled')
    vocabulary_analysis_checkbox.configure(state='normal')
    vocabulary_analysis_menu.configure(state='disabled')
    if extra_GUIs_var.get():
        # extra_GUIs_checkbox.configure(state='normal')
        extra_GUIs_menu.configure(state='normal')
        vocabulary_analysis_checkbox.configure(state='disabled')
        vocabulary_analysis_menu.configure(state='disabled')
    # place widget with hover-over info
    if vocabulary_analysis_var.get()==True:
        vocabulary_analysis_menu.configure(state='normal')
        extra_GUIs_checkbox.configure(state='disabled')
        extra_GUIs_menu.configure(state='disabled')

activate_all_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {
               "Word Sense Induction (WSI) (via BERT & K-means)": "TIPS_NLP_Word Sense Induction (WSI).pdf",
               "Word Sense Disambiguation (WSD) (via CoNLL & WordNet)": "TIPS_NLP_Word Sense Disambiguation (WSD).pdf",
               "Lexical databases (WordNet, VerbNet, FrameNet)":"TIPS_NLP_Lexical databases (WordNet, VerbNet, FrameNet).pdf",
               "Word embeddings with BERT": "TIPS_NLP_BERT word embeddings.pdf",
               "Word2Vec with Gensim":"TIPS_NLP_Word2Vec.pdf",
               "Semantic similarity & clustering (document embeddings)":"TIPS_NLP_Semantic similarity (document embeddings).pdf",
               'Coreference resolution':'TIPS_NLP_Coreference resolution.pdf',
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'Abstract/concrete language':'TIPS_NLP_Language concreteness analysis.pdf',
               'Iconic language':'TIPS_NLP_Iconic language.pdf',
               'Objective/subjective language':'TIPS_NLP_Objectivity_subjectivity (via spaCy and TextBlob).pdf',
               'Nominalization':'TIPS_NLP_Nominalization.pdf',
               'N-Grams (word & character)':"TIPS_NLP_Ngram (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}

TIPS_options=('Word Sense Induction (WSI) (via BERT & K-means)','Word Sense Disambiguation (WSD) (via CoNLL & WordNet)','Word embeddings with BERT','Word2Vec with Gensim','Semantic similarity & clustering (document embeddings)', \
              'Lexical databases (WordNet, VerbNet, FrameNet)', \
              'Coreference resolution', \
              'Style analysis','CoNLL Table', 'English Language Benchmarks','Things to do with words: Overall view', \
             'Abstract/concrete language','Iconic language', 'Objective/subjective language',\
             'Nominalization',\
             'N-Grams (word & character)',\
             'NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer',\
             'csv files - Problems & solutions', 'Statistical measures')

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_csv_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "Please, use the 'Select INPUT CSV file' button to choose the CoNLL table to analyze.\n\nThe button first LISTS all CoNLL tables found for your current corpus - searching the output directory, the input directory, and the default output directory - so you can pick one directly without hunting for the file (each is labelled by its parser/corpus subfolder, e.g. a Stanza dependency parse vs a CoreNLP parse). You can also choose 'Browse for another file' to select any other CoNLL csv. If no CoNLL table is found, a file dialog opens directly.\n\nA CoNLL table is a csv file produced by a parser (spaCy, Stanford CoreNLP, or Stanza) via the Parsers & annotators GUI, in which each token is labeled with a part-of-speech tag (POSTAG), a Dependency Relation tag (DEPREL), and other linguistic information.\n\nThe selected file is validated to ensure it is a properly formatted CoNLL table." + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         'Please, tick the \'GUIs available\' checkbox if you wish to see and select the range of other available tools suitable for stylistic analysis.')
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, tick the checkbox to run word Sense Induction (WSI) via BERT.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                  "NLP Suite Help",
                                  "Please, select the csv dictionary file containing the words or enter the comma-separated words to be use to compute word sense induction via BERT.")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Tick 'Word Sense Disambiguation (WSD)' to disambiguate each NOUN and VERB in context. Unlike the WordNet aggregation options - which map each word to its FIRST (most common) sense regardless of context - WSD reads a CoNLL table and, for each noun/verb, uses its SENTENCE together with the Lesk algorithm (Lesk 1986; NLTK) to pick the WordNet synset whose definition best overlaps the surrounding words; the word is then aggregated to that synset's semantic category (e.g. the financial-institution sense of 'bank' vs. the river-bank sense). This is the precision alternative to bare-lemma first-sense aggregation, at the cost of needing sentence context - which is why the input is a CoNLL table rather than a word list.\n\nWSD is WordNet-based; for VerbNet classes and FrameNet frames use the Semantic Role Labelling (SRL) option below (PropBank/SemLink).\n\nNB: WSD assigns each word to a KNOWN sense from a fixed inventory (WordNet). It is distinct from Word Sense INDUCTION (WSI) above, which DISCOVERS a word's senses directly from your corpus with no predefined inventory (BERT + k-means).")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Tick 'Semantic Role Labelling (SRL)' to label, for each predicate in a sentence, its semantic arguments - WHO did WHAT to WHOM, and when/where/why (agent, patient, instrument, etc.). Where a parser gives grammatical relations (subject, object), SRL gives the MEANING roles the phrases play around a predicate.\n\nIn NLP Suite, SRL is also the sense-disambiguated route to VerbNet classes and FrameNet frames (via PropBank predicate senses and the SemLink mappings), complementing the WordNet-based WSD option above.\n\nNote: standard SRL is VERBAL - predicates are verbs; noun-evoked frames would require nominal SRL, which is not yet integrated.\n\nBE PATIENT - NO PROGRESS IS SHOWN: SRL runs a transformer model inside a separate, isolated Python 3.8 environment, and that process's output is not streamed back to this window. So while SRL is running you will see NO per-sentence or per-file progress - the terminal simply appears idle. On a large corpus SRL can take a long time (hours). This is expected, NOT a freeze; let it run to completion.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Tick 'DOCUMENT embeddings: Semantic similarity & clustering to embed each document with SBERT (sentence-transformers) and compute a document-by-document semantic similarity matrix (csv + an interactive heatmap) and cluster the documents by MEANING (number of clusters chosen automatically). This is the document-level counterpart to the word-level Word2Vec/BERT embeddings. Needs at least 2 txt documents; the SBERT model downloads once (~80 MB) on first use.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click 'Classify words by semantic proximity: Word2Vec & word embeddings (Open GUI)' to open the Word2Vec GUI. Instead of mapping words to predefined categories (as WordNet/VerbNet/FrameNet do), this learns each word's meaning from HOW IT IS USED in your corpus - producing word embeddings (Word2Vec/Gensim, or BERT) so you can find words that are semantically close, i.e. used in similar contexts. A data-driven notion of meaning, complementary to the inventory-based aggregation and WSD options.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click 'Aggregate words by semantics (Open GUI)' to open the Semantic Aggregation GUI. There you can classify and aggregate the NOUNS and VERBS of your corpus into WordNet, VerbNet, and FrameNet categories: build a word list from a category (Zoom IN/DOWN), or roll words up into higher-level categories (Zoom OUT/UP) - at the top-level supersense or at a lower-level synset you choose. This is the context-blind (first-sense) counterpart to the Word Sense Disambiguation option above.")
    #
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Please, tick 'More semantic analyses' and use the dropdown menu to select an analysis:\n\n   1. Coreference resolution (Open GUI) - opens the Coreference GUI to resolve pronouns to their antecedents; when it finishes you can choose to use the new coreferenced corpus for your analyses in this GUI.\n\n   2. Nominalization - detect deverbal nouns (nouns derived from verbs, e.g. 'destruction' from 'destroy').\n\n   3. Abstract/concrete vocabulary - mean/median concreteness per sentence (0=abstract to 5=concrete), using the ratings by Brysbaert, Warriner & Kuperman, Concreteness Ratings for 40 Thousand Generally Known English Word Lemmas, Behavioral Research (2014) 46:904-911. English only.\n\n   4. Iconic vocabulary - (not available yet).\n\n   5. Objectivity/subjectivity (via spaCy) - score how objective vs. subjective the language is.\n\n   6. Topic modelling - discover the latent topics in the corpus.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="These Python 3 scripts bring together the NLP Suite's SEMANTIC analyses - the analysis of MEANING.\n\nYou can: discover a word's senses directly from your corpus (Word Sense Induction, WSI, via BERT & k-means) or assign each word its context-correct sense from WordNet (Word Sense Disambiguation, WSD, via a CoNLL table); label semantic roles - who did what to whom - with Semantic Role Labelling (SRL); aggregate words into WordNet, VerbNet and FrameNet categories (Aggregate words by semantics); measure word-level semantic proximity with Word2Vec & BERT word embeddings; and measure document-level semantic similarity & clustering with sentence embeddings (SBERT).\n\nUnder 'More semantic analyses' you can also run coreference resolution, nominalization, abstract/concrete and objective/subjective vocabulary, and topic modelling.\n\nSome options open a dedicated GUI; others run here and produce csv files and charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)
def activate_NLP_options(*args):
    global error, package_basics, package, language, language_var, language_list
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
GUI_util.setup_menu.trace('w', activate_NLP_options)
activate_NLP_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file 'NLP_default_package_language_config.csv' could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup next the default NLP package and language options.")
    run_script_util.run_script("NLP_setup_package_language_main.py")
    # this will display the correct hover-over info after the python call, in case options were changed
    error, package, parsers, package_basics, language, package_display_area_value_new, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()

title = ["NLP setup options"]
message = "Some of the algorithms behind this GUI rely on a specific NLP package to carry out basic NLP functions (e.g., sentence splitting, tokenizing, lemmatizing) for a specific language your corpus is written in.\n\nYour selected corpus language is " \
          + str(language) + ".\nYour selected NLP package for basic functions (e.g., sentence splitting, tokenizing, lemmatizing) is " \
          + str(package_basics) + ".\n\nYou can always view your default selection saved in the config file NLP_default_package_language_config.csv by hovering over the Setup widget at the bottom of this GUI and change your default options by selecting Setup NLP package and corpus language."
reminders_util.checkReminder(scriptName, title, message)

GUI_util.window.mainloop()

