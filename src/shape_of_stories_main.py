# Written by Roberto Franzosi
# Modified by Cynthia Dong (November 2019-April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"shape_of_stories_main.py", ['subprocess', 'os', 'tkinter', 'shutil','matplotlib','csv','numpy','sklearn','tqdm','codecs']) == False:
    sys.exit(0)

# tqdm, sklearn, and codecs must be installed
# tqdm provides a progress bar (used in clustering_util)

import os
import shutil
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
import file_utf8_compliance_util as utf

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, createExcelCharts, sentimentAnalysis, sentimentAnalysisMethod, memory_var, corpus_analysis,
        hierarchical_clustering, SVD, NMF, best_topic_estimation):

    # check all IO options ---------------------------------------------------------------------------
    # check that the default directory of sentiment scores exists under the new default outputDir
    # sentiment_scores_folder = os.path.join(outputDir, "sentiment_analysis_scores_" + os.path.basename(inputDir))

    # computeSAScores = False
    # if os.path.exists(sentiment_scores_input):
    #     if sentimentAnalysis == True:
    #         if nSAscoreFiles>0:
    #             computeSAScores=mb.askyesno("Sentiment Analysis","You have selected to run sentiment analysis on your corpus of stories. But there already exists a set of sentiment scores for this corpus saved in the default output directory:\n\n"+sentiment_scores_input+"\n\nAre you sure you want to recompute the scores?")
    #             if computeSAScores ==True:
    #                 # remove current sentiment scores directory and recreate it
    #                 shutil.rmtree(sentiment_scores_input)
    #                 os.mkdir(sentiment_scores_input)
    #             else:
    #                 if hierarchical_clustering == False and SVD == False and NMF == False:
    #                     mb.showwarning(title='Option selection error',
    #                                    message='No data reduction options have been selected.\n\nPlease, select an option and try again.')
    #                     return
    #                 else:
    #                     answer = mb.askyesno("Sentiment Analysis",
    #                                                   "The 'Shape of Stories' algorithms will not compute sentiment scores and will continue running the data reduction algorithms using the already available scores.\n\nAre you sure you want to continue?")
    #                     if answer == False:
    #                         return
    #         else:
    #             computeSAScores=True
    #     else:
    #         if nSAscoreFiles==0:
    #             mb.showwarning(title="Folder error",
    #                            message="There are no csv files of sentiment analysis scores in the directory\n\n" +str(sentiment_scores_input) + \
    #                                     "\n\nYou will need to run the sentiment analysis algorithm. Please, tick the checkbox to run Sentiment Analysis and try again.")
    #             return
    # else:
    #     os.mkdir(sentiment_scores_input)
    #     computeSAScores = True

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
        title_options = ['Output directory']
        message = 'The output directory was changed to:\n\n'+str(outputDir)
        reminders_util.checkReminder(config_filename,
                                     title_options,
                                     message,
                                     True)

# RUN SCRIPTS ---------------------------------------------------------------------------

    filesToOpen = []

    # utf.check_utf8_compliance(GUI_util.window, "", inputDir, outputDir, openOutputFiles)
    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                        'Started running Shape of Stories at', True)

    # check corpus statistics
    if corpus_analysis:
        statistics_txt_util.compute_corpus_statistics(GUI_util.window, inputDir, inputDir, outputDir, openOutputFiles,
                                                      True)
    # step 1: run sentiment analysis
    if sentimentAnalysis == 1:
        # run appropriate sentiment analysis method as indicated by sentimentAnalysisMethod
        if sentimentAnalysisMethod == "Stanford CoreNLP Neural Network":
            title_options = ['Stanford CoreNLP Neural Network']
            message = 'The Stanford CoreNLP Neural Network approach to Sentiment analysis, like all neural network algorithms, is VERY slow. On a few hundred stories it may take hours to run.\n\nAlso, neural network algorithms are memory hogs. MAKE SURE TO ALLOCATE AS MUCH MEMORY AS YOU CAN AFFORD ON YOUR MACHINE.'
            reminders_util.checkReminder(config_filename,
                                         title_options,
                                         message,
                                         True)

            # TODO any changes in the way the CoreNLP_annotator generates output filenames will need to be edited here
            outputFilename = 'NLP_CoreNLP_sentiment_Dir_'+tail + '.csv'

            if os.path.isfile(os.path.join(outputDir,outputFilename)):
                computeSAScores=mb.askyesno("Sentiment Analysis","You have selected to run sentiment analysis on your corpus. But there already exists a csv file of sentiment scores for this corpus saved in the default output directory:\n\n"+outputFilename+"\n\nAre you sure you want to recompute the scores?")
                if not computeSAScores:
                    return
            tempOutputfile=Stanford_CoreNLP_annotator_util.CoreNLP_annotate('', inputDir, outputDir, openOutputFiles, createExcelCharts,'sentiment',False, memory_var)
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
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                           'Started running estimate_best_k at', True,'You can follow the progress bar in command line.')
        filesToOpen = cl.estimate_best_k(sentiment_vectors, outputDir, filesToOpen)
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                            'Finished running estimate_best_k at', True)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                        'Finished running Shape of Stories at', True)

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

GUI_size = '1100x550'
GUI_label = 'Graphical User Interface (GUI) for "Shape of Stories" Extraction and Visualization Pipeline'
config_filename = 'shape-of-stories-config.txt'
# The 6 values of config_option refer to: 
#   software directory
#   input file
        # 1 for CoNLL file 
        # 2 for TXT file 
        # 3 for csv file 
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option = [0, 3, 1, 0, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename

GUI_util.GUI_top(config_input_output_options,config_filename)

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

# NMF_default_lb = tk.Label(window,text='Number of clusters')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300,y_multiplier_integer,NMF_default_lb,True)

# NMF_window_max=100
# NMF_default_entry = tk.Scale(window, from_=0, to=NMF_window_max, orient=tk.HORIZONTAL)
# NMF_default_entry.pack()
# NMF_default_entry.set(NMF_window_max/2)
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+500,y_multiplier_integer,NMF_default_entry)

def check_IO_requirements(inputFilename, inputDir):
    sentimentAnalysis=sentiment_analysis_var.get()
    corpus_analysis=corpus_analysis_var.get()
    hierarchical_clustering=hierarchical_clustering_var.get()
    SVD=SVD_var.get()
    NMF=NMF_var.get()
    best_topic_estimation=best_topic_estimation_var.get()

    nSAscoreFiles = None

    DirErr_txt = "The selected options \'Sentiment analysis\' and/or \'Compute & visualize corpus statistcs\' require in input a LARGE set of txt files for which to compute sentiment scores and/or compute corpus statistics. The selected input directory\n\n" + inputDir + "\n\ndoes not contain any txt files.\n\nPlease, use the IO widget \'Select INPUT files directory\' to select a different directory (or untick the checkboxes 'Sentiment Analysis' and/or 'Compute & visualize corpus statistics') and try again."
    DirErr_txt_file = "The selected options \'Sentiment analysis\' and/or \'Compute & visualize corpus statistcs\' require in input a LARGE set of txt files for which to compute sentiment scores and/or compute corpus statistics.\n\nPlease, use the IO widget \'Select INPUT files directory\' to select the appropriate directory containg txt files (or untick the checkboxes 'Sentiment Analysis' and/or 'Compute & visualize corpus statistics') and try again."
    DirErr_csv_file = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a LARGE set of csv files in a directory (or a csv file containing sentiment analysis scores). The selected input directory\n\n" + inputDir + "\n\ndoes not contain any csv files.\n\nPlease, select a different directory (or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization'  and/or 'Best topic estimation' or select an input csv file of sentiment scores) and try again."
    csv_fileWarning = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization) require in input a LARGE set of txt files. The selected input directory\n\n" + inputDir + "\n\ncontains only " + str(
         nSAscoreFiles) + " txt files from which to compute sentiment scores. TOO FEW!\n\nYou REALLY should select a different directory (or untick the checkbox 'Sentiment Analysis') and try again.\n\nAre you sure you want to continue?"
    csv_fileErr='The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a csv file containing sentiment scores (or a directory containing a LARGE set of csv files of sentiment scores).\n\nThe selected file\n\n' + inputFilename + '\n\nis not a csv file containing sentiment scores.\n\nPlease, use the IO widget \'Select INPUT csv file\' to select the appropriate csv file containing sentiment scores (or the appropriate directory) and try again.'

    Error = False

    if inputDir=='' and inputFilename!='':
        if sentimentAnalysis == True:
            mb.showwarning(title='Input file error',
                           message=DirErr_txt_file)
            Error = True
            return Error
        if corpus_analysis == True:
            mb.showwarning(title='Input folder error',
                           message=DirErr_txt)
            Error = True
            return Error

    if inputFilename!='':
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
        if nSAscoreFiles == None:
            return
        if nSAscoreFiles < 50:
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
                    mb.showwarning(title="Input folder error",
                                   message=DirErr_txt)
                    Error = True
                    return Error
                if nSAscoreFiles < 50 and sentimentAnalysis == True:
                    answer = mb.askyesno("Directory error",
                                         message=Dir_Err_txt)
                    Error = True
                    return Error

            if (not sentimentAnalysis) and (hierarchical_clustering or SVD or NMF or best_topic_estimation):
                nSAscoreFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
                if nSAscoreFiles==0:
                    mb.showwarning(title="Directory error",
                                   message=DirErr_csv_file)
                    Error = True
                    return Error
                elif nSAscoreFiles < 50 and sentimentAnalysis == True:
                    answer = mb.askyesno("Data reduction algorithms",
                                         message=csv_fileWarning)
                if answer == False:
                    Error = True
                    return Error

    # check input file that must be a csv file containing sentiment analysis score of any data reduction options are ticked
    if inputFilename!='' and sentiment_analysis_var.get() == False and corpus_analysis_var.get() == False and (
            hierarchical_clustering_var.get() == True or SVD_var.get() == True or NMF_var.get() == True):
        nSAscoreFiles = IO_csv_util.GetNumberOfDocumentsInCSVfile(inputFilename,'Shape of Stories')
        if nSAscoreFiles == None:
            Error = True
            return Error
        # nSAscoreFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
        if nSAscoreFiles < 50:
            mb.showwarning(title="Data warning: Data reduction algorithms",
                                 message=csv_fileWarning)
            Error = True
            return Error
    # check that there is inputDir value if sentiment analysis and/or corpus are checked
    if inputDir=='' and sentimentAnalysis == True or corpus_analysis_var.get() == True:
        mb.showwarning(title='Input folder error',
                       message=DirErr_txt)
        Error = True
        return Error

    # check inputDir files that must be txt if sentiment analysis and/or corpus are checked
    if inputDir!='' and sentiment_analysis_var.get() == True or corpus_analysis_var.get() == True:
        nSAscoreFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'txt')
        if nSAscoreFiles==0:
            mb.showwarning(title="Input folder error",
                           message=DirErr_txt)
            Error = True
            return Error
        if sentiment_analysis_var.get() == True:
            title_options = ['Stanford CoreNLP Sentiment Analysis system requirements']
            message = 'The Stanford CoreNLP Sentiment Analysis tool requires two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'
            reminders_util.checkReminder(config_filename,
                                         title_options,
                                         message,
                                         True)
            # Error = True
            # return Error

    # check data reduction and IO input values
    if inputDir!='' and sentiment_analysis_var.get() == False and corpus_analysis_var.get() == False and (
            hierarchical_clustering_var.get() == True or SVD_var.get() == True or NMF_var.get() == True):
        nSAscoreFiles=IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, 'csv')
        if nSAscoreFiles==0:
            mb.showwarning(title="Data warning: Data reduction algorithms",
                           message=csv_fileWarning)
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

TIPS_lookup = {'Shape of stories':'TIPS_NLP_Shape of stories.pdf','Data reduction algorithms: Parameters formulae':'TIPS_NLP_Data reduction algorithms: Parameters formulae.pdf','Hierarchical clustering':'Data reduction algorithms: Hierarchical clustering.pdf','Singular Value Decomposition':'Data reduction algorithms: Singular Value Decomposition.pdf','Non-negative Matrix Factorization (NMF)':'TIPS_NLP_Shape of stories - Non-Negative Matrix Factorization (NMF).pdf','Sentiment analysis':'TIPS_NLP_Sentiment analysis.pdf'}
TIPS_options='Shape of stories','Sentiment analysis','Data reduction algorithms: Parameters formulae','Hierarchical clustering','Singular Value Decomposition','Non-negative Matrix Factorization (NMF)'

def display_reminder(*args):
    if best_topic_estimation_var.get():
        reminders_util.checkReminder(config_filename,
                                     ['Best topic estimation'],
                                     'The function that estimates the best topics is VERY slow and may take an hour or longer. You can follow its progress in command line.',
                                     True)
best_topic_estimation_var.trace('w',display_reminder)

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    inputFileMsg ='Please, slect the csv file of merged sentiment scores to be analyzed by the data reduction algorithms to visualize the shape of stories.'
    inputDirTXTCSVMsg ='In INPUT the algorithms expect either a set of TXT files or CSV files in a directory depending upon the options selected:\n   1. compute sentiment scores (txt files);\n   2. compute data-reduction shape-of-stories visuals (csv files).\n\nPlease, use the \'Select INPUT files directory\' IO widget to select the appropriate directory.'
    inputDirCSVMsg ='\n\nIn INPUT the algorithms expect a set of csv files of sentiment scores in a directory. Please, use the \'Select INPUT files directory\' IO widget to select the directory.'
    inputDirTXTMsg ='\n\nIn INPUT the algorithms expect a set of txt files in a directory for which to compute sentiment scores. Please, use the \'Select INPUT files directory\' IO widget to select the directory.'
    outputDirMsg='\n\nIn OUPUT the sentiment analysis scores will be saved in a double subdirectory of the output directory - Shape of Stories/Last part of input directory name/sentiment_analysis_results_last part of input directory name.'
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help", inputFileMsg+GUI_IO_util.msg_openFile)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help", inputDirTXTCSVMsg+GUI_IO_util.msg_openExplorer)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help", GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help", 'Please, tick the checkbox \'Sentiment Analysis\' if you wish to run the Sentiment Analysis algorithm.\n\nIf you do want to run the algorithm, using the dropdown menu, please select the type of Sentiment Analysis algorithm you wish to use (Stanford CoreNLP neural network approach recommended).'+inputDirTXTMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help", 'Please, tick the checkbox if you wish to compute & visualize corpus statistics. This will help you identify any document outlier in terms of number of words and, particularly relevant for the analysis of the shape of stories, number of sentences.'+inputDirTXTMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help", 'Please, tick the checkbox if you wish to run the Hierarchical Clustering algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help", 'Please, tick the checkbox if you wish to run the SVD (Singular Value Decomposition) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help", 'Please, tick the checkbox if you wish to run the NMF (Non-Negative Matrix Factorization) algorithm of data reduction.'+inputDirCSVMsg+outputDirMsg)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help", 'Please, tick the checkbox if you wish to estimate the best number of topics providing graphical visualization.\n\nWARNING! This function is very slow and make take an hour or longer. You can follow its progress in command line.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help", GUI_IO_util.msg_openOutputFiles)
help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The Python 3 scripts provide ways of analyzing the emotional arc of a set of stories and of visualizing common patterns of behavior among the stories.\n\nThe shape of stories algorithms are fundamentally based on sentiment analysis of the input stories and on data reduction of the calculated sentiment scores.\n\n" \
"In INPUT the algorithms expect either\n   1. a csv file of sentiment scores or an directory of csv files of sentiment scores\n" \
"   2. a set of TXT files or CSV files in a directory depending upon the options selected: compute sentiment scores (txt files); compute data-reduction shape-of-stories visuals (csv files).\n\nPlease, use the \'Select INPUT files directory\' IO widget to select the appropriate directory.\n\n" \
"In OUTPUT the algorithms will produce sentiment analysis scores (if the option is selected) and a number of visual plots (e.g., sentiment arcs). " \
"Output files will be saved in a sub-directory called \'Shape of Stories\' itself a subdirectory of the current default output directory; inside this \'Shape of Stories\' subdirecory all files will be saved inside a further subdirectory with the name of the final part of the input directory.\n\n" \
"Four different approaches to SENTIMENT ANALYSIS can be used to measure the emotional arc of stories: ANEW, VADER, hedonometer, Stanford CoreNLP neural network approach (recommended).\n\n" \
"Three different approaches to DATA REDUCTION are used: Hierarchical clustering (HC), Singular Value Decomposition (SVD), Non-Negative Matrix Factorization (NMF).\n\n" \
"During execution, the algorithm will ask the user to confirm three different PARAMETERS used by the data reduction algorithms: Window size, Sentiment Vector Size, Cluster (modes) size.\n\n" \
"   WINDOW SIZE: the number of sentences that will be averaged to obtain one point of the story arc.\n   Lower bound: At least one sentence must be take average to get the values in sentiment score vector.\n   Upper bound: minimum document length-1. Window size should be less than the minimum document length, i.e, number of sentences in the shortest document.\n" \
"\n   SENTIMENT VECTOR SIZE: the number of values that each document will be represented with.\n   Lower bound: Each document should be represented by at least one value.\n   Upper bound: minimum document length. Each document should be represented by at most [minimum document length] values.\n" \
"\n   CLUSTER (MODE) SIZE: the number of clusters that users want the documents to be grouped into.\n   The recommended cluster size is calculated using Principal Component Analysis (PCA, via the Python sklearn library). A cluster size is considered good if documents in the same cluster are similar to one another, and dissimilar from the documents in other clusters.\n   Lower bound: All documents should be clustered into at least one cluster.\n   Upper bound: sentiment vector size. The number of clusters should not exceed the sentiment vector size."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

# check_IO_requirements(GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get())

GUI_util.window.mainloop()
