# Written by Roberto Franzosi
# Modified by Cynthia Dong (November 2019-April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"shape_of_stories_main.py", ['subprocess', 'os', 'tkinter', 'matplotlib','csv','numpy','sklearn','tqdm','codecs']) == False:
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

import GUI_IO_util
import IO_files_util
import IO_csv_util
import reminders_util

import Stanford_CoreNLP_annotator_util

import sentiment_analysis_ANEW_util as ANEW
import sentiment_analysis_VADER_util as VADER
import sentiment_analysis_hedonometer_util as hedonometer
import sentiment_analysis_SentiWordNet_util as SentiWordNet
import file_checker_util as utf

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts, sentimentAnalysis, sentimentAnalysisMethod, memory_var, corpus_analysis,
        hierarchical_clustering, SVD, NMF, best_topic_estimation):

    global nSAscoreFiles
    nSAscoreFiles = 0

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


    tail = ''
    if inputFilename!='':
        sentiment_scores_input = inputFilename  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, os.path.basename(head))
    elif inputDir!='':
        sentiment_scores_input = inputDir  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, tail)

    # check that the specific default directory exists under "Shape of Stories"
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    if GUI_util.output_dir_path.get()!=outputDir:
        # outputDir = head
        GUI_util.output_dir_path.set(outputDir)
        title_options_shape_of_stories = ['Output directory']
        message_shape_of_stories = 'The output directory was changed to:\n\n'+str(outputDir)
        reminders_util.checkReminder(config_filename,
                                     title_options_shape_of_stories,
                                     message_shape_of_stories,
                                     True)

# RUN SCRIPTS ---------------------------------------------------------------------------

    filesToOpen = []

    # utf.check_utf8_compliance(GUI_util.window, "", inputDir, outputDir, openOutputFiles)
    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                        'Started running Shape of Stories at', True)

    # check corpus statistics
    if corpus_analysis:
        statistics_txt_util.compute_corpus_statistics(GUI_util.window, inputDir, inputDir, outputDir, openOutputFiles,
                                                      True)
    # step 1: run sentiment analysis
    if sentimentAnalysis == 1:
        # run appropriate sentiment analysis method as indicated by sentimentAnalysisMethod
        if sentimentAnalysisMethod == "Stanford CoreNLP Neural Network":
            reminders_util.checkReminder(config_filename,
                                         reminders_util.title_options_shape_of_stories_CoreNLP,
                                         reminders_util.message_shape_of_stories_CoreNLP,
                                         True)

            # TODO any changes in the way the CoreNLP_annotator generates output filenames will need to be edited here
            outputFilename = 'NLP_CoreNLP_sentiment_Dir_'+tail + '.csv'

            if os.path.isfile(os.path.join(outputDir,outputFilename)):
                computeSAScores=mb.askyesno("Sentiment Analysis","You have selected to run sentiment analysis on your corpus. But there already exists a csv file of sentiment scores for this corpus saved in the default output directory:\n\n"+outputFilename+"\n\nAre you sure you want to recompute the scores?")
                if not computeSAScores:
                    return
            tempOutputfile=Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, '', inputDir, outputDir, openOutputFiles, createExcelCharts,'sentiment',False, memory_var)
            if tempOutputfile==None:
                return
            sentiment_scores_input=tempOutputfile[0]
        else:
            mb.showwarning(title="Sentiment Analysis Method not available", message=sentimentAnalysisMethod + " is not currently available. The only available option is the \'Stanford CoreNLP neural network\' method. Sorry!")
            return

    if hierarchical_clustering or SVD or NMF or best_topic_estimation:
        nSAscoreFiles = IO_csv_util.GetNumberOfDocumentsInCSVfile(sentiment_scores_input, 'Shape of Stories')

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
        hier = cl.Clustering(rec_n_clusters)

        DendogramFilename, grouped_vectors, clusters_indices, vectors = hier.cluster(sentiment_vectors, outputDir)
        filesToOpen.append(DendogramFilename)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters, os.path.join(outputDir, "Hierarchical Clustering Documents.csv"), inputDir)
        vis = viz.Visualizer(outputDir)
        vis.visualize_clusters(nSAscoreFiles, grouped_vectors, "Hierarchical Clustering (HC)", "HC", clusters_file)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputDir, "HC_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputDir, "HC_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputDir, "Hierarchical Clustering Documents.csv"))

    # svd
    if SVD:
        svd = cl.SVDClustering(rec_n_clusters)
        pos_vector_clusters, pos_clusters_indices, pos_modes, neg_vector_clusters, neg_clusters_indices, neg_modes = \
            svd.cluster(sentiment_vectors)
        clusters_file = cl.processCluster(pos_clusters_indices,scoresFile_list, file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputDir, "SVD Positive Documents.csv"), inputDir)
        vis = viz.Visualizer(outputDir)
        vis.visualize_clusters(nSAscoreFiles, pos_vector_clusters, "Singular Value Decomposition Positive (SVD Positive)", "SVDPositive",
                               clusters_file, modes=pos_modes)
        clusters_file = cl.processCluster(neg_clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputDir, "SVD Negative Documents.csv"), inputDir)
        vis = viz.Visualizer(outputDir)
        vis.visualize_clusters(nSAscoreFiles, neg_vector_clusters, "Singular Value Decomposition Negative (SVD Negative)", "SVDNegative",
                               clusters_file, modes=neg_modes)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputDir, "SVD_Positive_Cluster_" + str(i + 1) + ".png"))
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputDir, "SVD_Negative_Cluster_" + str(i + 1) + ".png"))
        filesToOpen.append(os.path.join(outputDir, "SVD Positive Documents.csv"))
        filesToOpen.append(os.path.join(outputDir, "SVD Negative Documents.csv"))

    # NMF
    if NMF:
        nmf = cl.NMFClustering(rec_n_clusters)
        grouped_vectors, clusters_indices, vectors = nmf.cluster(sentiment_vectors)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(clusters_indices, scoresFile_list,file_list, sentiment_vectors, rec_n_clusters,
                       os.path.join(outputDir, "NMF Documents.csv"), inputDir)
        vis = viz.Visualizer(outputDir)
        vis.visualize_clusters(nSAscoreFiles, grouped_vectors, "Non-negative Matrix Factorization (NMF)", "NMF", clusters_file)
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputDir, "NMF_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputDir, "NMF_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputDir, "NMF Documents.csv"))

    # best topic estimate
    if best_topic_estimation:
        startTime1=IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Started running estimate_best_k at', True,'You can follow the progress bar in command line.')
        filesToOpen = cl.estimate_best_k(sentiment_vectors, outputDir, filesToOpen)
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                            'Finished running estimate_best_k at', True, '', True, startTime1)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                        'Finished running Shape of Stories at', True, '', True, startTime)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# the values of the GUI widgets MUST be entered in the command as widget.get() otherwise they will not be updated
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.create_Excel_chart_output_checkbox.get(),
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
config_filename = 'shape_of_stories_config.csv'
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

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

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
sentiment_analysis_checkbox = tk.Checkbutton(window, text='Sentiment Analysis', variable=sentiment_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sentiment_analysis_checkbox,True)

sentiment_analysis_lb = tk.Label(window,text='Select the Sentiment Analysis algorithm')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+150,y_multiplier_integer,sentiment_analysis_lb,True)

sentiment_analysis_menu_var.set('Stanford CoreNLP Neural Network')
sentiment_analysis_menu = tk.OptionMenu(window,sentiment_analysis_menu_var,'Stanford CoreNLP Neural Network','ANEW','VADER','hedonometer', 'SentiWordNet')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+100,y_multiplier_integer,sentiment_analysis_menu,True)

#memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 400,y_multiplier_integer,memory_var_lb,True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(6)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 480,y_multiplier_integer,memory_var)

def activate_warning(*args):
    if sentiment_analysis_menu_var.get()!='Stanford CoreNLP Neural Network':
        mb.showwarning(title="Sentiment Analysis Method not available",
                       message=sentiment_analysis_menu_var.get() + " is not currently available. The only available option is the \'Stanford CoreNLP neural network\' method. Sorry!")
sentiment_analysis_menu_var.trace("w",activate_warning)

corpus_analysis_var.set(0)
corpus_analysis_checkbox = tk.Checkbutton(window, text='Compute & visualize corpus statistics', variable=corpus_analysis_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,corpus_analysis_checkbox)

# sentence_window_lb = tk.Label(window,text='Size of sentence window')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sentence_window_lb,True)

# sentence_window_max=100
# sentence_window_entry = tk.Scale(window, from_=0, to=sentence_window_max, orient=tk.HORIZONTAL)
# sentence_window_entry.pack()
# sentence_window_entry.set(sentence_window_max/2)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,sentence_window_entry)

# sliding_window_lb = tk.Label(window,text='Size of sliding window (stride)')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,sliding_window_lb,True)

# sliding_window_max=200
# sliding_window_entry = tk.Scale(window, from_=0, to=sliding_window_max, orient=tk.HORIZONTAL)
# sliding_window_entry.pack()
# sliding_window_entry.set(sliding_window_max/2)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,sliding_window_entry)

hierarchical_clustering_var.set(1)
hierarchical_clustering_checkbox = tk.Checkbutton(window, text='Hierarchical Clustering (HC)', variable=hierarchical_clustering_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,hierarchical_clustering_checkbox)

# hierarchical_default_lb = tk.Label(window,text='Number of modes')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300,y_multiplier_integer,hierarchical_default_lb,True)

# hierarchical_window_max=200
# hierarchical_default_entry = tk.Scale(window, from_=0, to=hierarchical_window_max, orient=tk.HORIZONTAL)
# hierarchical_default_entry.pack()
# hierarchical_default_entry.set(150)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,hierarchical_default_entry)

SVD_var.set(1)
SVD_checkbox = tk.Checkbutton(window, text='Singular Value Decomposition (SVD)', variable=SVD_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SVD_checkbox)

# SVD_default_lb = tk.Label(window,text='Number of clusters')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300,y_multiplier_integer,SVD_default_lb,True)

# SVD_window_max=100
# SVD_default_entry = tk.Scale(window, from_=0, to=SVD_window_max, orient=tk.HORIZONTAL)
# SVD_default_entry.pack()
# SVD_default_entry.set(SVD_window_max)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,SVD_default_entry)

NMF_var.set(1)
NMF_checkbox = tk.Checkbutton(window, text='Non-Negative Matrix Factorization (NMF)', variable=NMF_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,NMF_checkbox)

# RF
best_topic_estimation_var.set(0)
best_topic_estimation_checkbox = tk.Checkbutton(window, text='Best topic estimation', variable=best_topic_estimation_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,best_topic_estimation_checkbox)

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

    get_txt_dir = "\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate directory containing txt files (" + untick_txt_options + ") and try again."
    get_csv_dir = "\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate directory containing a LARGE set of csv files of sentiment scores (or select an input csv file of sentiment scores for a LARGE set of documents or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization' and/or 'Best topic estimation') and try again."
    get_csv_file = "\n\nPlease, use the IO widget \'Select INPUT/OUTPUT configuration\' to select the appropriate csv file containing sentiment scores for a LARGE set of documents (or an appropriate directory containing a LARGE set of csv files of sentiment scores (" + untick_csv_options + ") and try again."

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
            mb.showwarning(title='Directory error',
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

        nSAscoreFiles = IO_csv_util.GetNumberOfDocumentsInCSVfile(inputFilename,'Shape of Stories')
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
                nSAscoreFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
                if nSAscoreFiles == 0:
                    # text files required
                    mb.showwarning(title="Input directory error",
                                   message=txt_DirErr)
                    Error = True
                    return Error
                if nSAscoreFiles < 50 and sentimentAnalysis == True:
                    # too few txt files
                    answer = mb.askyesno("Directory warning",
                                         message=txt_dirWarning)
                    if answer == False:
                        Error = True
                        return Error

            if (not sentimentAnalysis) and (hierarchical_clustering or SVD or NMF or best_topic_estimation):
                nSAscoreFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
                if nSAscoreFiles==0:
                    # directory requires csv files
                    mb.showwarning(title="Directory error",
                                   message=csv_DirErr)
                    Error = True
                    return Error
                elif nSAscoreFiles < 50 and sentimentAnalysis == True:
                    # too few csv files
                    answer = mb.askyesno("Data reduction algorithms",
                                         message=csv_dirWarning)
                    if answer == False:
                        Error = True
                        return Error

    # check input file that must be a csv file containing sentiment analysis score of any data reduction options are ticked
    if inputFilename!='' and sentiment_analysis_var.get() == False and corpus_analysis_var.get() == False and (
            hierarchical_clustering_var.get() == True or SVD_var.get() == True or NMF_var.get() == True):
        nSAscoreFiles = IO_csv_util.GetNumberOfDocumentsInCSVfile(inputFilename,'Shape of Stories')
        if nSAscoreFiles == 0:
            Error = True
            return Error
        if nSAscoreFiles < 50:
            # too few csv files
            mb.showwarning(title="Data warning: Data reduction algorithms",
                                 message=csv_fileWarning)
            Error = True
            return Error

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
            reminders_util.checkReminder(config_filename,
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

        if nSAscoreFiles < 50:
            # too few csv files
            mb.showwarning(title="Data warning: Data reduction algorithms",
                                 message=csv_dirWarning)
            Error = True
            return Error

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
TIPS_lookup = {'Shape of stories':'TIPS_NLP_Shape of stories.pdf','Data reduction algorithms: Parameters formulae':'TIPS_NLP_Data reduction algorithms: Parameters formulae.pdf','Hierarchical clustering':'Data reduction algorithms: Hierarchical clustering.pdf','Singular Value Decomposition':'Data reduction algorithms: Singular Value Decomposition.pdf','Non-negative Matrix Factorization (NMF)':'TIPS_NLP_Shape of stories - Non-Negative Matrix Factorization (NMF).pdf','Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf'}
TIPS_options='Shape of stories','Sentiment analysis'

def display_reminder(*args):
    if best_topic_estimation_var.get():
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_shape_of_stories_best_topic,
                                     reminders_util.message_shape_of_stories_best_topic,
                                     True)
best_topic_estimation_var.trace('w',display_reminder)

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    IO_widget = "\n\nPlease, use the \'Select INPUT/OUTPUT configuration\' button to select the appropriate input/output options."
    inputFileMsg ='Please, select the csv file of merged sentiment scores to be analyzed by the data reduction algorithms to visualize the shape of stories.'
    inputDirTXTCSVMsg='\n\nIn INPUT the algorithms expect a LARGE set of TXT files, a csv file containing sentiment scores for a LARGE set of documents or a directory containing a LARGE set of csv files of sentiment scores.'
    inputDirTXTMsg ='\n\nIn INPUT the algorithms expect a LARGE set of TXT files.'
    inputDirCSVMsg ='\n\nIn INPUT the algorithms expect a csv file containing sentiment scores for a LARGE set of documents or a directory containing a LARGE set of csv files of sentiment scores.'
    outputDirMsg='\n\nIn OUTPUT all results of the analyses will be saved in a double subdirectory of the output directory - Shape of Stories/Last part of input directory name/sentiment_analysis_results_last part of input directory name.' + IO_widget

    if not IO_setup_display_brief:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", inputFileMsg+GUI_IO_util.msg_openFile)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", inputDirTXTCSVMsg+GUI_IO_util.msg_openExplorer)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+1),"Help", 'Please, tick the checkbox \'Sentiment Analysis\' if you wish to run the Sentiment Analysis algorithm.\n\nIf you do want to run the algorithm, using the dropdown menu, please select the type of Sentiment Analysis algorithm you wish to use (Stanford CoreNLP neural network approach recommended).'+ inputDirTXTMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+2),"Help", 'Please, tick the checkbox if you wish to compute & visualize corpus statistics. This will help you identify any document outlier in terms of number of words and, particularly relevant for the analysis of the shape of stories, number of sentences.'+inputDirTXTMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+3),"Help", 'Please, tick the checkbox if you wish to run the Hierarchical Clustering algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+4),"Help", 'Please, tick the checkbox if you wish to run the SVD (Singular Value Decomposition) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+5),"Help", 'Please, tick the checkbox if you wish to run the NMF (Non-Negative Matrix Factorization) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+6),"Help", 'Please, tick the checkbox if you wish to estimate the best number of topics providing graphical visualization.\n\nWARNING! This function is very slow and make take an hour or longer. You can follow its progress in command line.' + inputDirCSVMsg + outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*(increment+7),"Help", GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of analyzing the emotional arc of a set of stories and of visualizing common patterns of behavior among the stories.\n\nThe shape of stories algorithms are fundamentally based on sentiment analysis of the input stories and on data reduction of the calculated sentiment scores.\n\nThe data reduction algorithms rely heavily on Andrew Reagan et al. work on the emotional arc of stories. Andrew J. Reagan et al. 2016. The emotional arcs of stories are dominated by six basic shapes. https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-016-0093-1   For code, see Reagan's GitHub repository at https://github.com/andyreagan \n\n" \
"In INPUT the algorithms expect either\n   1. a csv file of sentiment scores or a directory of csv files of sentiment scores\n" \
"   2. a set of TXT files or CSV files in a directory depending upon the options selected: compute sentiment scores (txt files); compute data-reduction shape-of-stories visuals (csv files).\n\n" \
"In OUTPUT the algorithms will produce sentiment analysis scores (if the option is selected) and a number of visual plots (e.g., sentiment arcs). " \
"\n\nPlease, use the 'Select INPUT/OUTPUT configuration' button to select the appropriate options. " \
"Output files will be saved in a sub-directory called \'Shape of Stories\' itself a subdirectory of the current default output directory; inside this \'Shape of Stories\' subdirecory all files will be saved inside a further subdirectory with the name of the final part of the input directory.\n\n" \
"Four different approaches to SENTIMENT ANALYSIS can be used to measure the emotional arc of stories: ANEW, VADER, hedonometer, Stanford CoreNLP neural network approach (recommended).\n\n" \
"Three different approaches to DATA REDUCTION are used: Hierarchical clustering (HC), Singular Value Decomposition (SVD), Non-Negative Matrix Factorization (NMF).\n\n" \
"During execution, the algorithm will ask the user to confirm three different PARAMETERS used by the data reduction algorithms: Window size, Sentiment Vector Size, Cluster (modes) size.\n\n" \
"   WINDOW SIZE: the number of sentences that will be averaged to obtain one point of the story arc.\n   Lower bound: At least one sentence must be take average to get the values in sentiment score vector.\n   Upper bound: minimum document length-1. Window size should be less than the minimum document length, i.e, number of sentences in the shortest document.\n" \
"\n   SENTIMENT VECTOR SIZE: the number of values that each document will be represented with.\n   Lower bound: Each document should be represented by at least one value.\n   Upper bound: minimum document length. Each document should be represented by at most [minimum document length] values.\n" \
"\n   CLUSTER (MODE) SIZE: the number of clusters that users want the documents to be grouped into.\n   The recommended cluster size is calculated using Principal Component Analysis (PCA, via the Python sklearn library). A cluster size is considered good if documents in the same cluster are similar to one another, and dissimilar from the documents in other clusters.\n   Lower bound: All documents should be clustered into at least one cluster.\n   Upper bound: sentiment vector size. The number of clusters should not exceed the sentiment vector size."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

check_IO_requirements(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get())

GUI_util.window.mainloop()
