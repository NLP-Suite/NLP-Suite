import logging

import IO_files_util
import reminders_util

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_word2vec(
    inputFilename,
    inputDir,
    outputDir,
    chartPackage,
    dataTransformation,
    remove_stopwords_var,
    lemmatize_var,
    WSI_var,
    BERT_var,
    Gensim_var,
    sg_menu_var,
    vector_size_var,
    window_var,
    min_count_var,
    vis_menu_var,
    dim_menu_var,
    compute_distances_var,
    top_words_var,
    keywords_var,
    keywordInput,
    range4,
    range6,
    range20,
    ngramsDropDown,
):
    """Train Word2Vec embeddings on the corpus and visualize them."""
    config_filename = "NLP_default_IO_config.csv"
    scriptName = "word2vec.py"

    if not BERT_var and not Gensim_var and not WSI_var and not compute_distances_var:
        logger.info(
            "No option has been selected.\n\nPlease select the Word2Vec package you wish to use (BERT and/or Gensim) and try again."
        )
        return

    filesToOpen = []

    if "Do not" not in vis_menu_var:
        logger.info(
            'Visualization via t-SNE: You have selected to run Word2Vec with the t-SNE visualization option ("Plot word vectors"). Depending upon the total number of words in your corpus, this option is computationally VERY demanding.'
        )
        # if not result:

    label = ""
    if BERT_var:
        label = "Word2Vec_BERT"
    elif Gensim_var:
        label = "Word2Vec_Gensim"
    elif WSI_var:
        label = "WSI"

    Word2Vec_Dir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label=label, silent=True)
    logger.info("Word2vec directory")
    logger.info(Word2Vec_Dir)
    if Word2Vec_Dir == "":
        return

    # Word Sense Induction
    if WSI_var:
        # def get_dictionary_file(window,title,fileType):
        #     if len(filePath)>0:

        # TODO: file upload functionality
        WSI_keywords_var = keywordInput
        if WSI_keywords_var == "":
            logger.info(
                'The "Word sense induction" algorithm requires a comma-separated list of case-sensitive keywords taken from the corpus in order to run.\n\nPlease, enter the keywords and try again.'
            )
            return

        import WSI_keyterms
        import WSI_util
        import WSI_viz

        # Load WSI data with the specified keyword list and k-means range
        all_sent, all_vocab, Word2Vec_Dir, docs, paths = WSI_util.get_data(
            inputFilename,
            inputDir,
            Word2Vec_Dir,
            u_vocab=WSI_keywords_var,
            fileType=".txt",
            configFileName=config_filename,
        )

        # k-means range from web sliders (range4 and range6)

        # TODO: add a label for K means
        k_means_min_var = int(range4)  # TODO: range(2, 9)
        k_means_max_var = int(range6)  # TODO: range(3, 15)
        k_range = (k_means_min_var, k_means_max_var)

        WSI_util.get_centroids(all_sent, all_vocab, Word2Vec_Dir, k_range)
        WSI_util.match_embeddings(all_sent, all_vocab, Word2Vec_Dir)
        s_paths = WSI_util.get_cluster_sentences(Word2Vec_Dir)
        v_paths = WSI_viz.sense_bar_chart(Word2Vec_Dir)

        ngrams_menu_var = int(ngramsDropDown.split("-")[0])  # TODO: needs to be between 1 and 4
        top_keywords_var = int(range20)  # TODO: change to between 5 to 20
        k_paths = WSI_keyterms.get_keyterms(Word2Vec_Dir, topn=top_keywords_var, ngram_range=(1, ngrams_menu_var))

        filesToOpen = s_paths + v_paths + k_paths

    if BERT_var:
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_BERT_Word2Vec_timing,
            reminders_util.message_BERT_Word2Vec_timing,
            True,
        )
        import BERT_util

        BERT_output = BERT_util.word_embeddings_BERT(
            inputFilename,
            inputDir,
            Word2Vec_Dir,
            False,
            chartPackage,
            dataTransformation,
            vis_menu_var,
            dim_menu_var,
            compute_distances_var,
            top_words_var,
            keywords_var,
            lemmatize_var,
            remove_stopwords_var,
            config_filename,
        )
        filesToOpen.append(BERT_output)

    if Gensim_var:
        # reminders_util.checkReminder(scriptName,
        #                              reminders_util.title_options_Gensim_Word2Vec_timing,
        #                              reminders_util.message_Gensim_Word2Vec_timing,
        #                              True)
        import word2vec_Gensim_util

        Gensim_output = word2vec_Gensim_util.run_Gensim_word2vec(
            inputFilename,
            inputDir,
            Word2Vec_Dir,
            config_filename,
            chartPackage,
            dataTransformation,
            remove_stopwords_var,
            lemmatize_var,
            keywords_var,
            compute_distances_var,
            top_words_var,
            sg_menu_var,
            vector_size_var,
            window_var,
            min_count_var,
            vis_menu_var,
            dim_menu_var,
        )
        filesToOpen.append(Gensim_output)

    return filesToOpen
