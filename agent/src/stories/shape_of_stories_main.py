import logging

# Written by Roberto Franzosi
# Modified by Cynthia Dong (November 2019-April 2020)
# if IO_libraries_util.install_all_Python_packages("shape_of_stories_main.py", ['subprocess', 'os', 'tkinter', 'matplotlib','csv','numpy','sklearn','tqdm','codecs']) == False:
# tqdm, sklearn, and codecs must be installed
# tqdm provides a progress bar (used in clustering_util)
import os

import config_util
import IO_csv_util
import IO_files_util
import IO_libraries_util
import IO_user_interface_util
import shape_of_stories_clustering_util as cl
import shape_of_stories_vectorizer_util as vec
import shape_of_stories_visualization_util as viz
import spaCy_util
import Stanford_CoreNLP_util
import Stanza_util
import statistics_txt_util

logger = logging.getLogger(__name__)

defaultConfigFilename = "NLP_default_IO_config.csv"

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    sentimentAnalysis,
    sentimentAnalysisMethod,
    memory_var,
    corpus_analysis,
    hierarchical_clustering,
    SVD,
    NMF,
    best_topic_estimation,
):
    """Compute document sentiment arcs and cluster them into story shapes."""
    config_filename = defaultConfigFilename
    nSAscoreFiles = 0
    filesToOpen = []

    if (
        not sentimentAnalysis
        and not corpus_analysis
        and not hierarchical_clustering
        and not SVD
        and not NMF
        and not best_topic_estimation
    ):
        # mb.showwarning(title='Option selection error',
        #                message='No options have been selected.\n\nPlease, select an option and try again.')
        raise Exception("Option selection error")
        return

    # Error set to True
    if check_IO_requirements(
        inputFilename,
        inputDir,
        sentimentAnalysis,
        corpus_analysis,
        hierarchical_clustering,
        SVD,
        NMF,
        best_topic_estimation,
    ):
        return

    # check if "Shape of Stories" default output directory exists
    sosDir = os.path.join(outputDir, "Shape of Stories")
    if not os.path.exists(sosDir):
        os.mkdir(sosDir)

    # get the NLP package and language options
    (
        error,
        package,
        parsers,
        package_basics,
        language,
        package_display_area_value,
        encoding_var,
        export_json_var,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
    ) = config_util.read_NLP_package_language_config()
    language_var = language

    tail = ""
    if inputFilename != "":
        sentiment_scores_input = inputFilename  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, os.path.basename(tail[:-4]))
    elif inputDir != "":
        sentiment_scores_input = inputDir  # INPUT
        head, tail = os.path.split(sentiment_scores_input)
        outputDir = os.path.join(sosDir, tail)

    # check that the specific default directory exists under "Shape of Stories"
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    # if GUI_util.output_dir_path.get()!=outputDir:
    #     reminders_util.checkReminder(scriptName,
    #                                  title_options_shape_of_stories,
    #                                  message_shape_of_stories,
    #                                  True)

    # RUN SCRIPTS ---------------------------------------------------------------------------

    # startTime=IO_user_interface_util.timed_alert('Analysis start',
    #                     'Started running Shape of Stories at', True)

    # check corpus statistics
    if corpus_analysis:
        statistics_txt_util.compute_corpus_statistics(
            inputDir,
            inputDir,
            outputDir,
            config_filename,
            openOutputFiles,
            chartPackage,
            dataTransformation,
        )

    # ----------------------------------------------------------------------------------------------------
    # step 1: run sentiment analysis
    if sentimentAnalysis == 1:
        # get the NLP package and language options
        (
            error,
            package,
            parsers,
            package_basics,
            language,
            package_display_area_value,
            encoding_var,
            export_json_var,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
        ) = config_util.read_NLP_package_language_config()
        language_var = language

        # run appropriate sentiment analysis method as indicated by sentimentAnalysisMethod
        # if 'CoreNLP' in sentimentAnalysisMethod:
        #     reminders_util.checkReminder(scriptName,
        #                                  reminders_util.title_options_shape_of_stories_CoreNLP,
        #                                  reminders_util.message_shape_of_stories_CoreNLP,
        #                                  True)
        #
        #     # TODO any changes in the way the CoreNLP_annotator generates output filenames will need to be edited here
        #
        #     if os.path.isfile(os.path.join(outputDir,outputFilename)):
        #         if not computeSAScores:
        #     tempOutputfile=Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, '', inputDir, outputDir, openOutputFiles,
        #                         chartPackage, dataTransformation,'sentiment',False, language_var, export_json_var, memory_var)
        #     if tempOutputfile==None:

        # BERT ---------------------------------------------------------

        if "BERT" in sentimentAnalysisMethod:
            import BERT_util

            if "Multilingual" in sentimentAnalysisMethod:
                model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"  # multilingual model
            else:
                model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # English language model
            tempOutputFiles = BERT_util.sentiment_main(
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                "",
                chartPackage,
                dataTransformation,
                model_path,
            )
            if tempOutputFiles is None:
                return
            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # spaCy  _______________________________________________________

        elif "spaCy" in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util

            if not IO_internet_util.check_internet_availability_warning("spaCy Sentiment Analysis"):
                return
            #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
            #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

            annotator = ["sentiment"]
            document_length_var = 1
            limit_sentence_length_var = 1000
            tempOutputFiles = spaCy_util.spaCy_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                annotator,
                False,
                language_var,
                memory_var,
                document_length_var,
                limit_sentence_length_var,
                filename_embeds_date_var=0,
                date_format="",
                items_separator_var="",
                date_position_var=0,
            )

            if tempOutputFiles is None:
                return

            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # Stanford CORENLP  _______________________________________________________

        elif "CoreNLP" in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util

            if not IO_internet_util.check_internet_availability_warning("Stanford CoreNLP Sentiment Analysis"):
                return
            #     flag="true" do NOT produce individual output files when processing a directory; only merged file produced
            #     flag="false" or flag="" ONLY produce individual output files when processing a directory; NO  merged file produced

            if not IO_libraries_util.check_inputPythonJavaProgramFile("Stanford_CoreNLP_util.py"):
                return
            tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "sentiment",
                False,
                language_var,
                export_json_var,
                memory_var,
            )
            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

        # Stanza  _______________________________________________________

        elif "Stanza" in sentimentAnalysisMethod:
            # check internet connection
            import IO_internet_util

            if not IO_internet_util.check_internet_availability_warning("Stanza Sentiment Analysis"):
                return

            annotator = "sentiment"
            document_length_var = 1
            limit_sentence_length_var = 1000
            tempOutputFiles = Stanza_util.Stanza_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                annotator,
                False,
                [language_var],
                # Stanza_util takes language_var as a list
                memory_var,
                document_length_var,
                limit_sentence_length_var,
                filename_embeds_date_var=0,
                date_format="",
                items_separator_var="",
                date_position_var=0,
            )

            if tempOutputFiles is None:
                return

            if len(tempOutputFiles) > 0:
                sentiment_scores_input = tempOutputFiles[0]
                filesToOpen.extend(tempOutputFiles)

    # step 2 ----------------------------------------------------------------------------------------------------

    if hierarchical_clustering or SVD or NMF or best_topic_estimation:
        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(sentiment_scores_input, "Shape of Stories", "Document ID")

        # step 2: vectorize
        # the sentiment_scores_input can either be a single merged csv file or a directory with multiple SA scores files

        vectz = vec.Vectorizer(sentiment_scores_input)

        # pop up window
        # window size

        # val = GUI_IO_util.slider_widget("Please, select the value for window size. Window size is the number of sentences "
        #              + ".", 1, vectz.min_doc_len - 1, vectz.window_size)
        val = vectz.window_size
        vectz.window_size = val

        # sentiment_vector_size
        # val = GUI_IO_util.slider_widget("Please, select the value for sentiment vector size. Sentiment vector size is the number of values "
        #              + ".", 1, vectz.min_doc_len, vectz.ideal_sent_v_size)
        vectz.sentiment_vector_size = val

        sentiment_vectors, file_list, scoresFile_list = vectz.vectorize()  # ANGEl

        rec_n_clusters = vectz.compute_suggested_n_clusters(sentiment_vectors)
        if rec_n_clusters is None:
            return

        # visualize a Principal Component Analysis (PCA) scatter plot of sentiment scores
        PCAFilename = viz.visualize_sentiment_arcs(sentiment_vectors, outputDir)
        filesToOpen.append(PCAFilename)

        # number of clusters
        #                  rec_n_clusters)
        #                       + ".", 1, vectz.sentiment_vector_size, rec_n_clusters)
        val = rec_n_clusters
        rec_n_clusters = val

    # hierarchical clustering
    if hierarchical_clustering:
        # create HC subdir
        outputHCDir = IO_files_util.make_output_subdirectory("", "", outputDir, label="HC_cluster", silent=True)
        if outputHCDir == "":
            return
        hier = cl.Clustering(rec_n_clusters)

        DendogramFilename, grouped_vectors, clusters_indices, vectors = hier.cluster(sentiment_vectors, outputHCDir)
        filesToOpen.append(DendogramFilename)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(
            clusters_indices,
            scoresFile_list,
            file_list,
            sentiment_vectors,
            rec_n_clusters,
            os.path.join(outputHCDir, "Hierarchical Clustering Documents.csv"),
            inputDir,
        )
        vis = viz.Visualizer(outputHCDir)
        vis.visualize_clusters(
            nSAscoreFiles,
            grouped_vectors,
            "Hierarchical Clustering (HC)",
            "HC",
            clusters_file,
        )
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputHCDir, "HC_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputHCDir, "HC_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputHCDir, "Hierarchical_Clustering_Documents.csv"))

    # svd
    if SVD:
        # create SVD subdir
        outputSVDDir = IO_files_util.make_output_subdirectory("", "", outputDir, label="SVD_cluster", silent=True)
        if outputSVDDir == "":
            return
        svd = cl.SVDClustering(rec_n_clusters)
        (
            pos_vector_clusters,
            pos_clusters_indices,
            pos_modes,
            neg_vector_clusters,
            neg_clusters_indices,
            neg_modes,
        ) = svd.cluster(sentiment_vectors)
        clusters_file = cl.processCluster(
            pos_clusters_indices,
            scoresFile_list,
            file_list,
            sentiment_vectors,
            rec_n_clusters,
            os.path.join(outputSVDDir, "SVD_Positive_Documents.csv"),
            inputDir,
        )
        vis = viz.Visualizer(outputSVDDir)
        vis.visualize_clusters(
            nSAscoreFiles,
            pos_vector_clusters,
            "Singular Value Decomposition Positive (SVD Positive)",
            "SVD_Positive",
            clusters_file,
            modes=pos_modes,
        )
        clusters_file = cl.processCluster(
            neg_clusters_indices,
            scoresFile_list,
            file_list,
            sentiment_vectors,
            rec_n_clusters,
            os.path.join(outputSVDDir, "SVD_Negative_Documents.csv"),
            inputDir,
        )
        vis = viz.Visualizer(outputSVDDir)
        vis.visualize_clusters(
            nSAscoreFiles,
            neg_vector_clusters,
            "Singular Value Decomposition Negative (SVD Negative)",
            "SVD_Negative",
            clusters_file,
            modes=neg_modes,
        )
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputSVDDir, "SVD_Positive_Cluster_" + str(i + 1) + ".png"))
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputSVDDir, "SVD_Negative_Cluster_" + str(i + 1) + ".png"))
        filesToOpen.append(os.path.join(outputSVDDir, "SVD_Positive_Documents.csv"))
        filesToOpen.append(os.path.join(outputSVDDir, "SVD_Negative_Documents.csv"))

    # NMF
    if NMF:
        # create NMF subdir
        outputNMFDir = IO_files_util.make_output_subdirectory("", "", outputDir, label="NMF_cluster", silent=True)
        if outputNMFDir == "":
            return

        nmf = cl.NMFClustering(rec_n_clusters)
        grouped_vectors, clusters_indices, vectors = nmf.cluster(sentiment_vectors)
        sentiment_vectors = vectors
        clusters_file = cl.processCluster(
            clusters_indices,
            scoresFile_list,
            file_list,
            sentiment_vectors,
            rec_n_clusters,
            os.path.join(outputNMFDir, "NMF_Documents.csv"),
            inputDir,
        )
        vis = viz.Visualizer(outputNMFDir)
        vis.visualize_clusters(
            nSAscoreFiles,
            grouped_vectors,
            "Non-negative Matrix Factorization (NMF)",
            "NMF",
            clusters_file,
        )
        for i in range(rec_n_clusters):
            filesToOpen.append(os.path.join(outputNMFDir, "NMF_Cluster_" + str(i + 1) + ".png"))
            filesToOpen.append(os.path.join(outputNMFDir, "NMF_Cluster_" + str(i + 1) + "_subplot.png"))
        filesToOpen.append(os.path.join(outputNMFDir, "NMF_Documents.csv"))

    # best topic estimate
    startTime1 = ""
    if best_topic_estimation:
        startTime1 = IO_user_interface_util.timed_alert(
            2000,
            "Analysis start",
            "Started running estimate_best_k at",
            True,
            "You can follow the progress bar in command line.",
        )
        filesToOpen = cl.estimate_best_k(sentiment_vectors, outputDir, filesToOpen)
        IO_user_interface_util.timed_alert(
            2000,
            "Analysis end",
            "Finished running estimate_best_k at",
            True,
            "",
            True,
            startTime1,
        )

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running Shape of Stories at",
        True,
        "",
        True,
        startTime1,
    )

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(openOutputFiles, filesToOpen, outputDir, scriptName)


# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True

GUI_label = 'Graphical User Interface (GUI) for "Shape of Stories" Extraction and Visualization Pipeline'
config_filename = "NLP_default_IO_config.csv"
head, scriptName = os.path.split(os.path.basename(__file__))

# # The 4 values of config_option refer to:
# #   input file
#         # 1 for CoNLL file
#         # 2 for TXT file
#         # 3 for csv file
#         # 4 for any type of file
#         # 5 for txt or html
#         # 6 for txt or csv
# #   input dir
# #   input secondary dir
# #   output dir

# def activate_warning(*args):
#             'BERT (English model)' in sentiment_analysis_menu_var.get() and not \
#             'BERT (Multilingual model)' in sentiment_analysis_menu_var.get() and not \
#             'spaCy' in sentiment_analysis_menu_var.get() and not \
#             'Stanza' in sentiment_analysis_menu_var.get():
#             mb.showwarning(title="Sentiment Analysis option deprecated",
#                             message="The selected sentiment analysis dictionary-based option '" + (sentiment_analysis_menu_var.get()).lstrip() + "' is deprecated.\n\nPlease, use one of the neural network approaches, slower perhaps, but far more accurate.")


def check_IO_requirements(
    inputFilename,
    inputDir,
    sentimentAnalysis,
    corpus_analysis,
    hierarchical_clustering,
    SVD,
    NMF,
    best_topic_estimation,
):
    sentimentAnalysis = sentimentAnalysis
    corpus_analysis = corpus_analysis
    hierarchical_clustering = hierarchical_clustering
    SVD = SVD
    NMF = NMF
    best_topic_estimation = best_topic_estimation

    # nSAscoreFiles refers to the number of files required for analysis:
    #   depending upon the options selected, these could be txt files or csv files or a single csv file containging a set of sentiment analysis scores for different files

    txt_dir_required = "The selected options 'Sentiment analysis' and/or 'Compute & visualize corpus statistcs' require in input a LARGE set of txt files for which to compute sentiment scores and/or compute corpus statistics."
    csv_file_required = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a csv file containing sentiment scores for a LARGE set of documents (or a directory containing a LARGE set of csv files of sentiment scores)."
    csv_dir_required = "The data reduction options selected (Hierarchical Clustering and/or Singular Value Decomposition and/or Non-Negative Matrix Factorization and/or Best topic estimation) require in input a directory containing a LARGE set of csv files of sentiment scores (or a csv file containing sentiment scores for a LARGE set of documents)."

    untick_txt_options = "or untick the checkboxes 'Sentiment Analysis' and/or 'Compute & visualize corpus statistics'"
    untick_csv_options = "or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization' and/or 'Best topic estimation'"

    get_txt_dir = (
        "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget 'Select INPUT/OUTPUT configuration' to select the appropriate directory containing txt files ("
        + untick_txt_options
        + ") and try again."
    )
    get_csv_dir = "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget 'Select INPUT/OUTPUT configuration' to select the appropriate directory containing a LARGE set of csv files of sentiment scores (or select an input csv file of sentiment scores for a LARGE set of documents or untick the checkboxes 'Hierarchical Clustering' and/or 'Singular Value Decomposition' and/or 'Non-Negative Matrix Factorization' and/or 'Best topic estimation') and try again."
    get_csv_file = (
        "\n\nThe RUN button is disabled until the expected I/O information is entered.\n\nPlease, use the IO widget 'Select INPUT/OUTPUT configuration' to select the appropriate csv file containing sentiment scores for a LARGE set of documents (or an appropriate directory containing a LARGE set of csv files of sentiment scores ("
        + untick_csv_options
        + ") and try again."
    )

    txt_fileErr = txt_dir_required + get_txt_dir
    txt_DirErr = (
        txt_dir_required
        + "\n\nThe selected input directory\n\n"
        + inputDir
        + "\n\ndoes not contain any txt files."
        + get_txt_dir
    )
    txt_dirWarning = (
        "The selected input directory\n\n"
        + inputDir
        + "\n\ncontains fewer than the minimum recommended 50 txt files from which to compute sentiment scores. TOO FEW!\n\nYou REALLY should select a different directory ("
        + untick_txt_options
        + ") and try again.\n\nAre you sure you want to continue?"
    )

    csv_DirErr = (
        csv_dir_required
        + "\n\nThe selected input directory\n\n"
        + inputDir
        + "\n\ndoes not contain any csv files."
        + get_csv_dir
    )
    csv_dirWarning = (
        "The selected input directory\n\n"
        + inputDir
        + "\n\ncontains fewer than the minimum recommended 50 csv files of sentiment scores from which to compute the shape of stories. TOO FEW!\n\nYou REALLY should select a different directory (or select a csv file containing sentiment scores for a LARGE set of documents or untick the checkbox 'Sentiment Analysis') and try again.\n\nAre you sure you want to continue?"
    )

    csv_fileWarning = (
        "The selected input csv file\n\n"
        + inputFilename
        + "\n\ncontains fewer than the minimum recommended 50 files of sentiment scores from which to compute the shape of stories. TOO FEW!\n\nYou REALLY should select a different csv file (or select a directory containing a LARGE set of csv files of sentiment scores or untick the checkbox 'Sentiment Analysis') and try again.\n\nAre you sure you want to continue?"
    )
    csv_fileErr = (
        csv_file_required
        + "\n\nThe selected input file\n\n"
        + inputFilename
        + "\n\nis not a csv file containing sentiment scores."
        + get_csv_file
    )

    Error = False

    if inputFilename != "":
        if sentimentAnalysis or corpus_analysis:
            # txt files required
            # mb.showwarning(title='Input directory error',
            #                message=txt_fileErr)
            logger.info(txt_fileErr)
            Error = True
            return Error

        # get headers so as to check that it is a sentiment score file
        str1 = " "
        str2 = str1.join(IO_csv_util.get_csvfile_headers(inputFilename))
        if not ("Document" in str2 and "Sentence" in str2 and "Sentiment" in str2):
            # mb.showwarning(title='csv file error',
            #                message=csv_fileErr)
            logger.info(csv_fileErr)
            Error = True
            return Error

        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(inputFilename, "Shape of Stories", "Document ID")
        if nSAscoreFiles == 0:
            return

        if nSAscoreFiles < 50:
            # too few csv files
            logger.info(csv_fileWarning)
            # answer = mb.askyesno("Data warning: Data reduction algorithms",
            #                      message=csv_fileWarning)
            # if answer == False:
    else:  # inputDir
        if inputDir != "":
            if sentimentAnalysis or corpus_analysis:
                nSAscoretxtFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, "txt")
                if nSAscoretxtFiles == 0:
                    # text files required
                    # mb.showwarning(title="Input directory error",
                    #                message=txt_DirErr)
                    logger.info(txt_DirErr)
                    Error = True
                    return Error
                if nSAscoretxtFiles < 50 and sentimentAnalysis:
                    # too few txt files
                    # answer = mb.askyesno("Input directory warning",
                    #                      message=txt_dirWarning)
                    logger.info(txt_dirWarning)
                    # if answer == False:

            if not sentimentAnalysis:
                if hierarchical_clustering or SVD or NMF or best_topic_estimation:
                    nSAscorecsvFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, "csv")
                    if nSAscorecsvFiles == 0:
                        alternative_msg = ""
                        nSAscoretxtFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, "txt")
                        if nSAscoretxtFiles > 0:
                            if nSAscoretxtFiles < 50:
                                alternative_msg = (
                                    "\n\nALTERNATIVELY, tick the checkbox 'Sentiment analysis,' select one of the available sentiment analysis algorithms (neural network highly recommended), and try again. YOUR INPUT DIRECTORY, HOWEVER, CONTAINS ONLY "
                                    + str(nSAscoretxtFiles)
                                    + " txt FILES, FEWER THAN THE RECOMMENDED 50 MINIMUM, ALTHOUGH THE ALGORITHMS WILL STILL RUN."
                                )
                            else:
                                alternative_msg = "\n\nALTERNATIVELY, tick the checkbox 'Sentiment analysis,' select one of the available sentiment analysis algorithms (neural network highly recommended), and try again. "
                        # mb.showwarning(title="Input directory error",
                        #                message=csv_DirErr+alternative_msg)
                        logger.info(csv_DirErr + alternative_msg)
                        Error = True
                    elif nSAscorecsvFiles < 50 and sentimentAnalysis:
                        # too few csv files
                        # answer = mb.askyesno("Data reduction algorithms",
                        #                      message=csv_dirWarning)
                        logger.info(csv_dirWarning)
                        # if answer == False:
                return Error

    # check input file that must be a csv file containing sentiment analysis score of any data reduction options are ticked
    if (
        inputFilename != ""
        and not sentimentAnalysis
        and not corpus_analysis
        and (hierarchical_clustering or SVD or NMF)
    ):
        nSAscoreFiles = IO_csv_util.GetMaxValueInCSVField(inputFilename, "Shape of Stories", "Document ID")
        if nSAscoreFiles == 0:
            Error = True
            return Error
        # if nSAscoreFiles < 50:
        #     # too few csv files
        #     answer = mb.askyesno("Data reduction algorithms",
        #                          message=csv_fileWarning)
        #     if answer == False:
        # mb.showwarning(title="Data warning: Data reduction algorithms",
        #                      message=csv_fileWarning)

    # check that there is inputDir value if sentiment analysis and/or corpus are checked
    if inputDir == "" and (sentimentAnalysis or corpus_analysis):
        # mb.showwarning(title='Input directory error',
        #                message=txt_DirErr)
        logger.info(txt_DirErr)
        Error = True
        return Error

    # check data reduction and IO input values
    if inputDir != "" and not sentimentAnalysis and not corpus_analysis and (hierarchical_clustering or SVD or NMF):
        nSAscoreFiles = IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, "csv")
        if nSAscoreFiles == 0:
            # mb.showwarning(title="Data warning: Data reduction algorithms",
            #                message=csv_DirErr)
            logger.info(csv_DirErr)
            Error = True
            return Error

        # if nSAscoreFiles < 50:
        #     # too few csv files
        #     mb.showwarning(title="Data warning: Data reduction algorithms",
        #                          message=csv_dirWarning)

    return Error


#
