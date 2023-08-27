# Written by Roberto Franzosi
# Modified by Cynthia Dong (November 2019-April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"shape_of_stories_main.py", ['subprocess', 'os', 'tkinter', 'matplotlib','csv','numpy','sklearn','tqdm','codecs']) == False:
    sys.exit(0)

# tqdm, sklearn, and codecs must be installed
# tqdm provides a progress bar (used in clustering_util)

import os
import tkinter as tk
import tkinter.messagebox as mb

import IO_user_interface_util
import statistics_txt_util
import shape_of_stories_clustering_util as cl
import shape_of_stories_vectorizer_util as vec
import shape_of_stories_visualization_util as viz

import config_util
import GUI_IO_util
import IO_files_util
import IO_csv_util
import reminders_util

import Stanford_CoreNLP_util
import spaCy_util
import Stanza_util

import sentiment_analysis_ANEW_util as ANEW
import sentiment_analysis_VADER_util as VADER
import sentiment_analysis_hedonometer_util as hedonometer
import sentiment_analysis_SentiWordNet_util as SentiWordNet
import file_checker_util as utf

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, sentimentAnalysis, sentimentAnalysisMethod, memory_var, corpus_analysis,
        hierarchical_clustering, SVD, NMF, best_topic_estimation):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('_main.py', '_config.csv')

    global nSAscoreFiles
    nSAscoreFiles = 0
    filesToOpen = []


    if sentimentAnalysis==False and corpus_analysis==False and hierarchical_clustering==False and SVD==False and NMF==False and best_topic_estimation==False:
        mb.showwarning(title='Option selection error',
                       message='No options have been selected.\n\nPlease, select an option and try again.')
        return

    # Error set to True
    if check_IO_requirements(inputFilename,inputDir):
        return

    # check if "Shape of Stories" default output directory exists
    sosDir = os.path.join(outputDir, "Shape of Stories")
    if not os.path.exists(sosDir):
        os.mkdir(sosDir)

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    tail = ''
    if inputFilename!='':
        sentiment_scores_input = inputFilename  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, os.path.basename(tail[:-4]))
    elif inputDir!='':
        sentiment_scores_input = inputDir  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, tail)

    # check that the specific default directory exists under "Shape of Stories"
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    # if GUI_util.output_dir_path.get()!=outputDir:
    #     # outputDir = head
    #     GUI_util.output_dir_path.set(outputDir)
    #     title_options_shape_of_stories = ['Output directory']
    #     message_shape_of_stories = 'The output directory was changed to:\n\n'+str(outputDir)
    #     reminders_util.checkReminder(scriptName,
    #                                  title_options_shape_of_stories,
    #                                  message_shape_of_stories,
    #                                  True)

# RUN SCRIPTS ---------------------------------------------------------------------------

    # utf.check_utf8_compliance(GUI_util.window, "", inputDir, outputDir, openOutputFiles)
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                        'Started running Shape of Stories at', True)

    # check corpus statistics
    if corpus_analysis:
        statistics_txt_util.compute_corpus_statistics(GUI_util.window, inputDir, inputDir, outputDir, config_filename, openOutputFiles,
                                                      createCharts, chartPackage)

# ----------------------------------------------------------------------------------------------------
    # step 1: run sentiment analysis
    if sentimentAnalysis == 1:

        # get the NLP package and language options
        error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
        language_var = language
        language_list = [language]

        # run appropriate sentiment analysis method as indicated by sentimentAnalysisMethod
        # if 'CoreNLP' in sentimentAnalysisMethod:
        #     reminders_util.checkReminder(scriptName,
        #                                  reminders_util.title_options_shape_of_stories_CoreNLP,
        #                                  reminders_util.message_shape_of_stories_CoreNLP,
        #                                  True)
        #
        #     # TODO any changes in the way the CoreNLP_annotator generates output filenames will need to be edited here
        #     outputFilename = 'NLP_CoreNLP_sentiment_Dir_'+tail + '.csv'
        #
        #     if os.path.isfile(os.path.join(outputDir,outputFilename)):
        #         computeSAScores=mb.askyesno("Sentiment Analysis","You have selected to run sentiment analysis on your corpus. But there already exists a csv file of sentiment scores for this corpus saved in the default output directory:\n\n"+outputFilename+"\n\nAre you sure you want to recompute the scores?")
        #         if not computeSAScores:
        #             return
        #     tempOutputfile=Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, '', inputDir, outputDir, openOutputFiles,
        #                         createCharts, chartPackage,'sentiment',False, language_var, export_json_var, memory_var)
        #     if tempOutputfile==None:
        #         return
        #     sentiment_scores_input=tempOutputfile[0]

        # BERT ---------------------------------------------------------

        if 'BERT' in sentimentAnalysisMethod:
            import BERT_util
            if 'Multilingual' in sentimentAnalysisMethod:
                model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"  # multilingual model
            else:
                model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # English language model
            tempOutputFiles = BERT_util.sentiment_main(inputFilename, inputDir, outputDir, config_filename, '', createCharts, chartPackage, model_path)
            if tempOutputFiles == None:
                return
            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # spaCy  _______________________________________________________

        elif 'spaCy' in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util
            if not IO_internet_util.check_internet_availability_warning('spaCy Sentiment Analysis'):
                return
            #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
            #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

            annotator = ['sentiment']
            document_length_var = 1
            limit_sentence_length_var = 1000
            tempOutputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                        outputDir, config_filename,
                                                        openOutputFiles,
                                                        createCharts, chartPackage,
                                                        annotator, False,
                                                        language_var,
                                                        memory_var, document_length_var, limit_sentence_length_var,
                                                        filename_embeds_date_var=0,
                                                        date_format='',
                                                        items_separator_var='',
                                                        date_position_var=0)

            if tempOutputFiles == None:
                return

            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # Stanford CORENLP  _______________________________________________________

        elif 'CoreNLP' in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util
            if not IO_internet_util.check_internet_availability_warning('Stanford CoreNLP Sentiment Analysis'):
                return
            #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
            #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

            flag = "false"  # the true option does not seem to work

            if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
                return
            tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                    outputDir, openOutputFiles, createCharts,
                                                                    chartPackage, 'sentiment', False,
                                                                    language_var, export_json_var,
                                                                    memory_var)
            # outputFilename=outputFilename[0] # annotators return a list and not a string
            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # Stanza  _______________________________________________________

        elif 'Stanza' in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util
            if not IO_internet_util.check_internet_availability_warning('Stanza Sentiment Analysis'):
                return

            annotator = 'sentiment'
            document_length_var = 1
            limit_sentence_length_var = 1000
            tempOutputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                          outputDir,
                                                          openOutputFiles,
                                                          createCharts, chartPackage,
                                                          annotator, False,
                                                          [language_var],
                                                          # Stanza_util takes language_var as a list
                                                          memory_var, document_length_var,
                                                          limit_sentence_length_var,
                                                          filename_embeds_date_var=0,
                                                          date_format='',
                                                          items_separator_var='',
                                                          date_position_var=0)

            if tempOutputFiles == None:
                return

            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

# step 2 ----------------------------------------------------------------------------------------------------

    if hierarchical_clustering or SVD or NMF or best_topic_estimation:
        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(sentiment_scores_input, 'Shape of Stories', 'Document ID')

        # step 2: vectorize
        # the sentiment_scores_input can either be a single merged csv file or a directory with multiple SA scores files

        vectz = vec.Vectorizer(sentiment_scores_input)

        # pop up window
        # window size

        val = GUI_IO_util.slider_widget(GUI_util.window,"Please, select the value for window size. Window size is the number of sentences "
                                 + "that will be averaged to obtain one point of the story arc. The recommend value is " + str(vectz.window_size)
                     + ".", 1, vectz.min_doc_len - 1, vectz.window_size)
        vectz.window_size = val

        # sentiment_vector_size
        val = GUI_IO_util.slider_widget(GUI_util.window,"Please, select the value for sentiment vector size. Sentiment vector size is the number of values "
                                 + "that each document will be represented with. The recommend value is " + str(vectz.ideal_sent_v_size)
                     + ".", 1, vectz.min_doc_len, vectz.ideal_sent_v_size)

        vectz.sentiment_vector_size = val

        sentiment_vectors, file_list, scoresFile_list = vectz.vectorize()#ANGEl

        rec_n_clusters = vectz.compute_suggested_n_clusters(sentiment_vectors)
        if rec_n_clusters==None:
            return

        # visualize a Principal Component Analysis (PCA) scatter plot of sentiment scores
        PCAFilename=viz.visualize_sentiment_arcs(sentiment_vectors, outputDir)
        filesToOpen.append(PCAFilename)

        # number of clusters
        val = GUI_IO_util.slider_widget(GUI_util.window,"Please, select the value for number of clusters (modes). The recommend value is " + str(
                         rec_n_clusters)
                              + ".", 1, vectz.sentiment_vector_size, rec_n_clusters)
        rec_n_clusters = val

    # hierarchical clustering
    if hierarchical_clustering:
        # create HC subdir
        outputHCDir = IO_files_util.make_output_subdirectory('', '', outputDir, label='HC_cluster',
                                                              silent=True)
        if outputHCDir == '':
            return
        hier = cl.Clustering(rec_n_clusters)

        DendogramFilename, grouped_vectors, clusters_indices, vectors = hier.cluster(sentiment_vectors, outputHCDir)
        filesToOpen.append(DendogramFilename)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters, os.path.join(outputHCDir, "Hierarchical Clustering Documents.csv"), inputDir)
        vis = viz.Visualizer(outputHCDir)
        vis.visualize_clusters(nSAscoreFiles, grouped_vectors, "Hierarchical Clustering (HC)", "HC", clusters_file)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputHCDir, "HC_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputHCDir, "HC_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputHCDir, "Hierarchical_Clustering_Documents.csv"))

    # svd
    if SVD:
        # create SVD subdir
        outputSVDDir = IO_files_util.make_output_subdirectory('', '', outputDir, label='SVD_cluster',
                                                              silent=True)
        if outputSVDDir == '':
            return
        svd = cl.SVDClustering(rec_n_clusters)
        pos_vector_clusters, pos_clusters_indices, pos_modes, neg_vector_clusters, neg_clusters_indices, neg_modes = \
            svd.cluster(sentiment_vectors)
        clusters_file = cl.processCluster(pos_clusters_indices,scoresFile_list, file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputSVDDir, "SVD_Positive_Documents.csv"), inputDir)
        vis = viz.Visualizer(outputSVDDir)
        vis.visualize_clusters(nSAscoreFiles, pos_vector_clusters, "Singular Value Decomposition Positive (SVD Positive)", "SVD_Positive",
                               clusters_file, modes=pos_modes)
        clusters_file = cl.processCluster(neg_clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputSVDDir, "SVD_Negative_Documents.csv"), inputDir)
        vis = viz.Visualizer(outputSVDDir)
        vis.visualize_clusters(nSAscoreFiles, neg_vector_clusters, "Singular Value Decomposition Negative (SVD Negative)", "SVD_Negative",
                               clusters_file, modes=neg_modes)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputSVDDir, "SVD_Positive_Cluster_" + str(i + 1) + ".png"))
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputSVDDir, "SVD_Negative_Cluster_" + str(i + 1) + ".png"))
        filesToOpen.append(os.path.join(outputSVDDir, "SVD_Positive_Documents.csv"))
        filesToOpen.append(os.path.join(outputSVDDir, "SVD_Negative_Documents.csv"))

    # NMF
    if NMF:
        # create NMF subdir
        outputNMFDir = IO_files_util.make_output_subdirectory('', '', outputDir, label='NMF_cluster',
                                                              silent=True)
        if outputNMFDir == '':
            return

        nmf = cl.NMFClustering(rec_n_clusters)
        grouped_vectors, clusters_indices, vectors = nmf.cluster(sentiment_vectors)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputNMFDir, "NMF_Documents.csv"), inputDir)
        vis = viz.Visualizer(outputNMFDir)
        vis.visualize_clusters(nSAscoreFiles, grouped_vectors, "Non-negative Matrix Factorization (NMF)", "NMF", clusters_file)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputNMFDir, "NMF_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputNMFDir, "NMF_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputNMFDir, "NMF_Documents.csv"))

    # best topic estimate
    if best_topic_estimation:
        startTime1=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                           'Started running estimate_best_k at', True,'You can follow the progress bar in command line.')
        filesToOpen = cl.estimate_best_k(sentiment_vectors, outputDir, filesToOpen)
        IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                            'Finished running estimate_best_k at', True, '', True, startTime1)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                        'Finished running Shape of Stories at', True, '', True, startTime)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_chart_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 sentiment_analysis_var.get(),
                                 sentiment_analysis_menu_var.get(),
                                 memory_var.get(),
                                 corpus_analysis_var.get(),
                                 # sentence_window_entry_var.get(),
                                 # sliding_window_entry_var.get(),
                                 hierarchical_clustering_var.get(),
                                 # hierarchical_default_entry_var.get(),
                                 SVD_var.get(),
                                 # SVD_default_entry_var.get(),
                                 NMF_var.get(),
                                 best_topic_estimation_var.get())
                                 # NMF_default_entry_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=480, # height at brief display
                             GUI_height_full=560, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for "Shape of Stories" Extraction and Visualization Pipeline'
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
config_input_output_numeric_options=[3,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

sentiment_analysis_var=tk.IntVar()
sentiment_analysis_menu_var=tk.StringVar()
memory_var = tk.IntVar()

corpus_analysis_var=tk.IntVar()
# sentence_window_entry_var=tk.StringVar()
# sliding_window_entry_var=tk.StringVar()
hierarchical_clustering_var=tk.IntVar()
#hierarchical_default_entry_var=tk.StringVar()
SVD_var=tk.IntVar()
#SVD_default_entry_var=tk.StringVar()
NMF_var=tk.IntVar()
#NMF_default_entry_var=tk.StringVar()
best_topic_estimation_var=tk.IntVar()

sentiment_analysis_var.set(0)
sentiment_analysis_checkbox = tk.Checkbutton(window, text='Sentiment Analysis', variable=sentiment_analysis_var,
                        onvalue=1, offvalue=0, command=lambda: check_IO_requirements(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get()))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,sentiment_analysis_checkbox,True)

sentiment_analysis_lb = tk.Label(window,text='Select the Sentiment Analysis algorithm')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.shape_of_stories_sentiment_analysis_lb_pos,y_multiplier_integer,sentiment_analysis_lb,True)

sentiment_analysis_menu_var.set('BERT (English model)')
sentiment_analysis_menu = tk.OptionMenu(window,sentiment_analysis_menu_var,'Neural network approaches:', '   BERT (English model)', '   BERT (Multilingual model)', '   spaCy','   Stanford CoreNLP','   Stanza','','Dictionary approaches:','   ANEW','   hedonometer','   SentiWordNet','   VADER')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.shape_of_stories_sentiment_analysis_menu_pos,y_multiplier_integer,sentiment_analysis_menu,True)

#memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.shape_of_stories_memory_lb_pos,y_multiplier_integer,memory_var_lb,True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.shape_of_stories_memory_pos,y_multiplier_integer,memory_var)

def activate_warning(*args):
    if not 'CoreNLP' in sentiment_analysis_menu_var.get() and not \
            'BERT (English model)' in sentiment_analysis_menu_var.get() and not \
            'BERT (Multilingual model)' in sentiment_analysis_menu_var.get() and not \
            'spaCy' in sentiment_analysis_menu_var.get() and not \
            'Stanza' in sentiment_analysis_menu_var.get():
            mb.showwarning(title="Sentiment Analysis option deprecated",
                            message="The selected sentiment analysis dictionary-based option '" + (sentiment_analysis_menu_var.get()).lstrip() + "' is deprecated.\n\nPlease, use one of the neural network approaches, slower perhaps, but far more accurate.")
sentiment_analysis_menu_var.trace("w",activate_warning)

corpus_analysis_var.set(0)
corpus_analysis_checkbox = tk.Checkbutton(window, text='Compute & visualize corpus statistics', variable=corpus_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,corpus_analysis_checkbox)


hierarchical_clustering_var.set(1)
hierarchical_clustering_checkbox = tk.Checkbutton(window, text='Hierarchical Clustering (HC)', variable=hierarchical_clustering_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,hierarchical_clustering_checkbox)


SVD_var.set(1)
SVD_checkbox = tk.Checkbutton(window, text='Singular Value Decomposition (SVD)', variable=SVD_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,SVD_checkbox)


NMF_var.set(1)
NMF_checkbox = tk.Checkbutton(window, text='Non-Negative Matrix Factorization (NMF)', variable=NMF_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,NMF_checkbox)

# RF
best_topic_estimation_var.set(0)
best_topic_estimation_checkbox = tk.Checkbutton(window, text='Best topic estimation', variable=best_topic_estimation_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,best_topic_estimation_checkbox)

def check_IO_requirements(inputFilename, inputDir):
    sentimentAnalysis=sentiment_analysis_var.get()
    corpus_analysis=corpus_analysis_var.get()
    hierarchical_clustering=hierarchical_clustering_var.get()
    SVD=SVD_var.get()
    NMF=NMF_var.get()
    best_topic_estimation=best_topic_estimation_var.get()

    # nSAscoreFiles refers to the number of files required for analysis:
    #   depending upon the options selected, these could be txt files or csv files or a single csv file containging a set of sentiment analysis scores for different files

    txt_dir_required = "The selected options \'Sentiment analysis\' and/or \'Compute & visualize corpus statistcs\' require in input a LARGE set of txt files for which to compute sentiment scores and/or compute corpus statistics."
    csv_file_required = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a csv file containing sentiment scores for a LARGE set of documents (or a directory containing a LARGE set of csv files of sentiment scores)."
    csv_dir_required = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a directory containing a LARGE set of csv files of sentiment scores (or a csv file containing sentiment scores for a LARGE set of documents)."

    untick_txt_options = "or untick the checkboxes 'Sentiment Analysis' and/or 'Compute & visualize corpus statistics'"
    untick_csv_options = "or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization' and/or 'Best topic estimation'"

    get_txt_dir = "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate directory containing txt files (" + untick_txt_options + ") and try again."
    get_csv_dir = "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate directory containing a LARGE set of csv files of sentiment scores (or select an input csv file of sentiment scores for a LARGE set of documents or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization' and/or 'Best topic estimation') and try again."
    get_csv_file = "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate csv file containing sentiment scores for a LARGE set of documents (or an appropriate directory containing a LARGE set of csv files of sentiment scores (" + untick_csv_options + ") and try again."

    txt_fileErr = txt_dir_required + get_txt_dir
    txt_DirErr = txt_dir_required + "\n\nThe selected input directory\n\n" + inputDir + "\n\ndoes not contain any txt files." + get_txt_dir
    txt_dirWarning = "The selected input directory\n\n" + inputDir + "\n\ncontains fewer than the minimum recommended 50 txt files from which to compute sentiment scores. TOO FEW!\n\nYou REALLY should select a different directory (" + untick_txt_options + ") and try again.\n\nAre you sure you want to continue?"

    csv_DirErr = csv_dir_required + "\n\nThe selected input directory\n\n" + inputDir + "\n\ndoes not contain any csv files." + get_csv_dir
    csv_dirWarning = "The selected input directory\n\n" + inputDir + "\n\ncontains fewer than the minimum recommended 50 csv files of sentiment scores from which to compute the shape of stories. TOO FEW!\n\nYou REALLY should select a different directory (or select a csv file containing sentiment scores for a LARGE set of documents or untick the checkbox 'Sentiment Analysis') and try again.\n\nAre you sure you want to continue?"

    csv_fileWarning = "The selected input csv file\n\n" + inputFilename + "\n\ncontains fewer than the minimum recommended 50 files of sentiment scores from which to compute the shape of stories. TOO FEW!\n\nYou REALLY should select a different csv file (or select a directory containing a LARGE set of csv files of sentiment scores or untick the checkbox 'Sentiment Analysis') and try again.\n\nAre you sure you want to continue?"
    csv_fileErr = csv_file_required + "\n\nThe selected input file\n\n" + inputFilename + "\n\nis not a csv file containing sentiment scores." + get_csv_file

    Error = False

    if inputFilename!='':
        if sentimentAnalysis == True or corpus_analysis == True:
            # txt files required
            mb.showwarning(title='Input directory error',
                           message=txt_fileErr)
            Error = True
            return Error

        # get headers so as to check that it is a sentiment score file
        str1=' '
        str2=str1.join(IO_csv_util.get_csvfile_headers(inputFilename))
        if not('Document' in str2 and 'Sentence' in str2 and 'Sentiment' in str2):
            mb.showwarning(title='csv file error',
                           message=csv_fileErr)
            Error = True
            return Error

        computeSAScores = False

        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(inputFilename,'Shape of Stories','Document ID')
        if nSAscoreFiles == 0:
            return

        if nSAscoreFiles < 50:
            # too few csv files
            answer = mb.askyesno("Data warning: Data reduction algorithms",
                                 message=csv_fileWarning)
            if answer == False:
                Error = True
                return Error
    else: # inputDir
        if inputDir!='':
            if sentimentAnalysis == True or corpus_analysis == True:
                nSAscoretxtFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
                if nSAscoretxtFiles == 0:
                    # text files required
                    mb.showwarning(title="Input directory error",
                                   message=txt_DirErr)
                    Error = True
                    return Error
                if nSAscoretxtFiles < 50 and sentimentAnalysis == True:
                    # too few txt files
                    answer = mb.askyesno("Input directory warning",
                                         message=txt_dirWarning)
                    if answer == False:
                        Error = True
                        return Error

            if (not sentimentAnalysis):
                if hierarchical_clustering or SVD or NMF or best_topic_estimation:
                    nSAscorecsvFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
                    if nSAscorecsvFiles==0:
                        alternative_msg = ''
                        nSAscoretxtFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
                        if nSAscoretxtFiles > 0:
                            if nSAscoretxtFiles < 50:
                                alternative_msg="\n\nALTERNATIVELY, tick the checkbox 'Sentiment analysis,' select one of the available sentiment analysis algorithms (neural network highly recommended), and try again. YOUR INPUT DIRECTORY, HOWEVER, CONTAINS ONLY " + str(nSAscoretxtFiles) + " txt FILES, FEWER THAN THE RECOMMENDED 50 MINIMUM, ALTHOUGH THE ALGORITHMS WILL STILL RUN."
                            else:
                                alternative_msg = "\n\nALTERNATIVELY, tick the checkbox 'Sentiment analysis,' select one of the available sentiment analysis algorithms (neural network highly recommended), and try again. "
                        mb.showwarning(title="Input directory error",
                                       message=csv_DirErr+alternative_msg)
                        Error = True
                    elif nSAscorecsvFiles < 50 and sentimentAnalysis == True:
                        # too few csv files
                        answer = mb.askyesno("Data reduction algorithms",
                                             message=csv_dirWarning)
                        if answer == False:
                            Error = True
                return Error

    # check input file that must be a csv file containing sentiment analysis score of any data reduction options are ticked
    if inputFilename!='' and sentiment_analysis_var.get() == False and corpus_analysis_var.get() == False and (
            hierarchical_clustering_var.get() == True or SVD_var.get() == True or NMF_var.get() == True):
        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(inputFilename,'Shape of Stories','Document ID')
        if nSAscoreFiles == 0:
            Error = True
            return Error
        # if nSAscoreFiles < 50:
        #     # too few csv files
        #     answer = mb.askyesno("Data reduction algorithms",
        #                          message=csv_fileWarning)
        #     if answer == False:
        #         Error = True
        #         return Error
            # mb.showwarning(title="Data warning: Data reduction algorithms",
            #                      message=csv_fileWarning)
            # Error = True
            # return Error

    # check that there is inputDir value if sentiment analysis and/or corpus are checked
    if inputDir=='' and (sentimentAnalysis == True or corpus_analysis_var.get() == True):
        mb.showwarning(title='Input directory error',
                       message=txt_DirErr)
        Error = True
        return Error
        # check inputDir files that must be txt if sentiment analysis and/or corpus are checked
        nSAscoreFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        if nSAscoreFiles==0:
            mb.showwarning(title="Input directory error",
                           message=txt_DirErr)
            Error = True
            return Error
        if sentiment_analysis_var.get() == True:
            reminders_util.checkReminder(scriptName,
                                         reminders_util.title_options_SA_CoreNLP_system_requirements,
                                         reminders_util.message_SA_CoreNLP_system_requirements,
                                         True)

    # check data reduction and IO input values
    if inputDir!='' and sentiment_analysis_var.get() == False and corpus_analysis_var.get() == False and (
            hierarchical_clustering_var.get() == True or SVD_var.get() == True or NMF_var.get() == True):
        nSAscoreFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
        if nSAscoreFiles==0:
            mb.showwarning(title="Data warning: Data reduction algorithms",
                           message=csv_DirErr)
            Error = True
            return Error

        # if nSAscoreFiles < 50:
        #     # too few csv files
        #     mb.showwarning(title="Data warning: Data reduction algorithms",
        #                          message=csv_dirWarning)
        #     Error = True
        #     return Error

    return Error

# sentiment_analysis_var.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
# corpus_analysis_var.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
# hierarchical_clustering_var.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
# SVD_var.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
# NMF_var.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
#
# GUI_util.inputFilename.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))
# GUI_util.input_main_dir_path.trace('w',lambda x, y, z: check_IO_requirements(GUI_util.inputFilename.get(),GUI_util.input_main_dir_path.get()))

videos_lookup = {'No videos available':''}
videos_options='No videos available'

#'Data reduction algorithms: Parameters formulae','Hierarchical clustering','Singular Value Decomposition','Non-negative Matrix Factorization (NMF)
TIPS_lookup = {'Shape of stories':'TIPS_NLP_Shape of stories.pdf',
               'Data reduction algorithms: Parameters formulae':'TIPS_NLP_Data reduction algorithms Parameters formulae.pdf',
               'Data reduction algorithms: Hierarchical clustering (HC)':'TIPS_NLP_Data reduction algorithms_Hierarchical clustering (HC).pdf',
               'Data reduction algorithms: Singular Value Decomposition (SVD)':'TIPS_NLP_Data reduction algorithms_Singular Value Decomposition (SVD).pdf',
               'Data reduction algorithms: Non-negative Matrix Factorization (NMF)':'TIPS_NLP_Data reduction algorithms_Non-negative Matrix Factorization (NMF).pdf',
               'Shape of stories: Best topic estimation':'TIPS_NLP_Shape of stories_Best topic estimation.pdf',
               'Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf',
               'Excel smoothing data series': 'TIPS_NLP_Excel smoothing data series.pdf',
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='Shape of stories','Sentiment analysis','Data reduction algorithms: Parameters formulae','Data reduction algorithms: Hierarchical clustering (HC)','Data reduction algorithms: Singular Value Decomposition (SVD)','Data reduction algorithms: Non-negative Matrix Factorization (NMF)','Shape of stories: Best topic estimation','Excel smoothing data series', 'csv files - Problems & solutions', 'Statistical measures'


def display_reminder(*args):
    if best_topic_estimation_var.get():
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_shape_of_stories_best_topic,
                                     reminders_util.message_shape_of_stories_best_topic,
                                     True)
best_topic_estimation_var.trace('w',display_reminder)

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    IO_widget = "\n\nPlease, use the \'Select INPUT/OUTPUT configuration\' button to select the appropriate input/output options."
    inputFileMsg ='Please, select the csv file of merged sentiment scores to be analyzed by the data reduction algorithms to visualize the shape of stories.'
    inputDirTXTCSVMsg='Please, select the directory where you store your TXT corpus to be analyzed or the csv files of sentiment scores.\n\nIn INPUT the algorithms expect a LARGE set of TXT files or a LARGE set of csv files of sentiment scores.'
    inputDirTXTMsg ='Please, select the directory where you store your TXT corpus to be analyzed or the csv files of sentiment scores.\n\nIn INPUT the algorithms expect a LARGE set of TXT files.'
    inputDirCSVMsg ='\n\nIn INPUT the algorithms expect a csv file containing sentiment scores for a LARGE set of documents or a directory containing a LARGE set of csv files of sentiment scores.'
    outputDirMsg='\n\nIn OUTPUT all results of the analyses will be saved in a double subdirectory of the output directory - Shape of Stories/Last part of input directory name/sentiment_analysis_results_last part of input directory name.' + IO_widget

    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", inputFileMsg+GUI_IO_util.msg_openFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", inputDirTXTCSVMsg+GUI_IO_util.msg_openExplorer)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox \'Sentiment Analysis\' if you wish to run the Sentiment Analysis algorithm.\n\nIf you do want to run the algorithm, using the dropdown menu, please select the type of Sentiment Analysis algorithm you wish to use (Stanford CoreNLP neural network approach recommended).'+ inputDirTXTMsg+outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to compute & visualize corpus statistics. This will help you identify any document outlier in terms of number of words and, particularly relevant for the analysis of the shape of stories, number of sentences.'+inputDirTXTMsg+outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to run the Hierarchical Clustering algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to run the SVD (Singular Value Decomposition) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to run the NMF (Non-Negative Matrix Factorization) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", 'Please, tick the checkbox if you wish to estimate the best number of topics providing graphical visualization.\n\nWARNING! This function is very slow and make take an hour or longer. You can follow its progress in command line.' + inputDirCSVMsg + outputDirMsg)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of analyzing the emotional arc of a set of stories and of visualizing common patterns of behavior among the stories.\n\nThe shape of stories algorithms are fundamentally based on sentiment analysis of the input stories and on data reduction of the calculated sentiment scores.\n\nThe data reduction algorithms rely heavily on Andrew Reagan et al. work on the emotional arc of stories. Andrew J. Reagan et al. 2016. The emotional arcs of stories are dominated by six basic shapes. https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-016-0093-1   For code, see Reagan's GitHub repository at https://github.com/andyreagan \n\n" \
"In INPUT the algorithms expect either\n   1. a csv file of sentiment scores or a directory of csv files of sentiment scores\n" \
"   2. a set of TXT files or CSV files in a directory depending upon the options selected: compute sentiment scores (txt files); compute data-reduction shape-of-stories visuals (csv files).\n\n" \
"In OUTPUT the algorithms will produce sentiment analysis scores (if the option is selected) and a number of visual plots (e.g., sentiment arcs). " \
"\n\nPlease, use the 'Select INPUT/OUTPUT configuration' button to select the appropriate options. " \
"Output files will be saved in a sub-directory called \'Shape of Stories\' itself a subdirectory of the current default output directory; inside this \'Shape of Stories\' subdirecory all files will be saved inside a further subdirectory with the name of the final part of the input directory.\n\n" \
"Two different types of approaches to SENTIMENT ANALYSIS are used: 1. neural network and 2. dictionary-based approaches.\n\nNeural network approaches, albeit slower, are far more reliable. The NLP Suite provides four different neural network algorithms - BERT, spaCy, Stanford CoreNLP, Stanza - and four dictionary-based algorithms - ANEW, hedonometer, sentiWordNet, VADER.\n\n" \
"Three different approaches to DATA REDUCTION are used: Hierarchical clustering (HC), Singular Value Decomposition (SVD), Non-Negative Matrix Factorization (NMF).\n\n" \
"During execution, the algorithm will ask the user to confirm three different PARAMETERS used by the data reduction algorithms: Window size, Sentiment Vector Size, Cluster (modes) size.\n\n" \
"   WINDOW SIZE: the number of sentences that will be averaged to obtain one point of the story arc.\n   Lower bound: At least one sentence must be take average to get the values in sentiment score vector.\n   Upper bound: minimum document length-1. Window size should be less than the minimum document length, i.e, number of sentences in the shortest document.\n" \
"\n   SENTIMENT VECTOR SIZE: the number of values that each document will be represented with.\n   Lower bound: Each document should be represented by at least one value.\n   Upper bound: minimum document length. Each document should be represented by at most [minimum document length] values.\n" \
"\n   CLUSTER (MODE) SIZE: the number of clusters that users want the documents to be grouped into.\n   The recommended cluster size is calculated using Principal Component Analysis (PCA, via the Python sklearn library). A cluster size is considered good if documents in the same cluster are similar to one another, and dissimilar from the documents in other clusters.\n   Lower bound: All documents should be clustered into at least one cluster.\n   Upper bound: sentiment vector size. The number of clusters should not exceed the sentiment vector size."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

check_IO_requirements(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get())

GUI_util.window.mainloop()
