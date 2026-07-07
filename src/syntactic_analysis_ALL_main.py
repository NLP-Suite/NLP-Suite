
# written by Roberto Franzosi (Spring/summer 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"syntactic_analysis_ALL_main.py",['os','csv','tkinter','ntpath','collections','subprocess'])==False:
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



def run(inputFilename, inputDir, outputDir, openOutputFiles,chartPackage,dataTransformation,
        extra_GUIs_var,
        extra_GUIs_menu_var,
        WSI_var,
        WSI_keywords_var,
        WSIdictionary_file_var,
        WSD_var,
        SRL_var,
        SSC_var,
        vocabulary_analysis_var,
        vocabulary_analysis_menu_var):


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
        import SVO_util
        # WSD writes into a dedicated subdirectory (keeps the outputs out of the cluttered main output dir)
        wsd_outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='WSD', silent=True) or outputDir
        noun_verb_list = ['NOUN', 'VERB']
        for noun_verb in noun_verb_list:
            outFiles = SVO_util.wsd_aggregate_WordNet(inputFilename, wsd_outputDir, noun_verb, chartPackage, dataTransformation)
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
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                GUI_util.data_transformation_options_widget.get(),
                                extra_GUIs_var.get(),
                                extra_GUIs_menu_var.get(),
                                WSI_var.get(),
                                WSI_keywords_var.get(),
                                WSIdictionary_file_var.get(),
                                WSD_var.get(),
                                SRL_var.get(),
                                SSC_var.get(),
                                vocabulary_analysis_var.get(),
                                vocabulary_analysis_menu_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=520, # height at brief display
                             GUI_height_full=480, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=1, # to be added for full display
                             increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Syntactic Analysis'
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
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var, onvalue=1, offvalue=0)
# extra_GUIs_checkbox.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Corpus statistics (Open GUI)','N-grams & Co-Occurrences (Open GUI)', 'What\'s in Your Corpus (Open GUI)')
# extra_GUIs_menu.configure(state='disabled')
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
        if 'Ngrams' in extra_GUIs_menu_var.get():
            run_script_util.run_script("NGrams_CoOccurrences_main.py")
        if 'What' in extra_GUIs_menu_var.get():
            run_script_util.run_script("whats_in_your_corpus_main.py")
        if 'Corpus' in extra_GUIs_menu_var.get():
            run_script_util.run_script("statistics_txt_main.py")

extra_GUIs_menu_var.trace('w',open_GUI)


#setup a button to open Windows Explorer on the selected input directory
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, WSI_keywords_var.get()))
# openInputFile_button.configure(state='disabled')
# the button widget has hover-over effects (no_hover_over_widget=False) and the info displayed is in text_info
# the two x-coordinate and x-coordinate_hover_over must have the same values
y_multiplier_integer = GUI_IO_util.placeWidget(window,
    GUI_IO_util.labels_x_indented_coordinate + 250, y_multiplier_integer,
    openInputFile_button, True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate + 250, "Open csv dictionary file")

parsers_annotators_button=tk.Button(window, width=90, text='Parsers & annotators (Open GUI)',command=lambda: run_script_util.run_script("parsers_annotators_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               parsers_annotators_button, False)

CoNLL_table_button=tk.Button(window, width=90, text='CoNLL table analyzer (Open GUI)',command=lambda: run_script_util.run_script("CoNLL_table_analyzer_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               CoNLL_table_button, False)

SVO_button=tk.Button(window, width=90, text='Subject-Verb-Object (SVO) (Open GUI)',command=lambda: run_script_util.run_script("SVO_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               SVO_button, False)


sentence_structure_button=tk.Button(window, width=90, text='Sentence structure (Open GUI)',command=lambda: run_script_util.run_script("sentence_analysis_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               sentence_structure_button, False)

style_analysis_button=tk.Button(window, width=90, text='Style analysis (Open GUI)',command=lambda: run_script_util.run_script("style_analysis_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               style_analysis_button, False)

# vocabulary_analysis_var.set(0)
# vocabulary_analysis_checkbox = tk.Checkbutton(window, text='More syntactic analyses', variable=vocabulary_analysis_var, onvalue=1, offvalue=0, command=lambda: activate_all_options())
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,vocabulary_analysis_checkbox,True)

# # vocabulary_analysis_menu_var.set('*')
# # vocabulary_analysis_lb = tk.Label(window, text='Select the vocabulary analysis you wish to perform')
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu,y_multiplier_integer,vocabulary_analysis_lb,True)
# place widget with hover-over info
# vocabulary_analysis_menu = tk.OptionMenu(window,vocabulary_analysis_menu_var,'*',
#                                          'Style analysis (Open GUI)',
#                                          'Nominalization',
#                                          'Abstract/concrete vocabulary',
#                                          'Iconic vocabulary',
#                                          'Objectivity/subjectivity (via spaCy)',
#                                          'Topic modelling')
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
#                                    vocabulary_analysis_menu,
#                                    False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
#                                    "Select the vocabulary analysis you wish to perform (* for all); widget disabled until checkbox ticked,")
#
# def activate_all_options(*args):
#     extra_GUIs_checkbox.configure(state='normal')
#     extra_GUIs_menu.configure(state='disabled')
#     vocabulary_analysis_checkbox.configure(state='normal')
#     vocabulary_analysis_menu.configure(state='disabled')
#     if extra_GUIs_var.get():
#         # extra_GUIs_checkbox.configure(state='normal')
#         extra_GUIs_menu.configure(state='normal')
#         vocabulary_analysis_checkbox.configure(state='disabled')
#         vocabulary_analysis_menu.configure(state='disabled')
#     # place widget with hover-over info
#     if vocabulary_analysis_var.get()==True:
#         vocabulary_analysis_menu.configure(state='normal')
#         extra_GUIs_checkbox.configure(state='disabled')
#         extra_GUIs_menu.configure(state='disabled')
#
# activate_all_options()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {
               'CoNLL Table': "TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",
               'Style analysis':'TIPS_NLP_Style analysis.pdf',
               'N-Grams (word & character)':"TIPS_NLP_Ngram (word & character).pdf",
               'NLP Ngram and Word Co-Occurrence VIEWER':"TIPS_NLP_Ngram and Word Co-Occurrence VIEWER.pdf",
               'Google Ngram Viewer':'TIPS_NLP_Ngram Google Ngram Viewer.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf'}

TIPS_options=('CoNLL Table','Style analysis', \
             'N-Grams (word & character)','NLP Ngram and Word Co-Occurrence VIEWER','Google Ngram Viewer', \
             'Statistical measures','Things to do with words: Overall view', \
             'csv files - Problems & solutions','English Language Benchmarks')

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

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click on the 'Parsers & annotators (Open GUI)' button to parse your corpus with the NLP package you selected in Setup (Stanford CoreNLP, Stanza, or spaCy).\n\nThe parser produces a CoNLL table: a csv file in which each token (word) is tagged with its part of speech (POSTAG), dependency relation (DEPREL), lemma, and named entity (NER). You can also run individual annotators (POS, lemma, sentence splitter, constituency parser, NER).\n\nThe CoNLL table produced here is the required input for most of the other syntactic analyses (CoNLL table analyzer, SVO).")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click on the 'CoNLL table analyzer (Open GUI)' button to analyze a CoNLL table produced by a parser (Stanford CoreNLP, Stanza, or spaCy).\n\nThe analyzer computes part-of-speech (POSTAG) and dependency-relation (DEPREL) distributions, clause analysis, and detailed statistics for nouns, verbs, adjectives, adverbs, and function words (pronouns, prepositions, articles, conjunctions, auxiliaries). You can also search the table by word, POS tag, or dependency relation.\n\nIn input, use the 'Select INPUT CSV file' button to pick a CoNLL table found for your corpus.")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click on the 'Subject-Verb-Object (SVO) (Open GUI)' button to extract Subject-Verb-Object triplets (who did what to whom) from your corpus via dependency parsing.\n\nSVO works with Stanford CoreNLP, Stanza, and spaCy, and can optionally add Semantic Role Labelling (SRL). It produces csv files and visualizations, and can map the locations and movements of the social actors (subjects) it finds.")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click on the 'Sentence structure (Open GUI)' button to measure the syntactic structure of sentences: sentence length, sentence complexity, and readability (via textstat), and to visualize a sentence's structure as a dependency tree.")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                                         "Click on the 'Style analysis (Open GUI)' button to profile the writing style of your corpus: sentence-level stylistic features useful for stylometry and authorship analysis.")

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="These Python 3 scripts bring together the NLP Suite's SYNTACTIC analyses - the analysis of grammatical FORM and STRUCTURE (as opposed to MEANING, handled by the Semantic analysis GUI).\n\nYou can: parse your corpus with Stanford CoreNLP, Stanza, or spaCy to produce a CoNLL table - each token tagged with its part of speech (POSTAG), dependency relation (DEPREL), lemma, and named entity (Parsers & annotators); analyze that CoNLL table for POS and dependency-relation distributions, clause structure, and noun/verb/adjective/adverb/function-word statistics (CoNLL table analyzer); extract Subject-Verb-Object triplets - who did what to whom - via dependency parsing, optionally with Semantic Role Labelling (SVO); measure sentence length, complexity and readability and visualize sentence structure as a dependency tree (Sentence structure); and profile writing style (Style analysis).\n\nUnder 'GUIs available for more analyses' you can also open Corpus statistics, N-grams & Co-Occurrences, and What's in Your Corpus.\n\nMost syntactic analyses take a CoNLL table in input, produced by the Parsers & annotators GUI. Each button opens a dedicated GUI."
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

