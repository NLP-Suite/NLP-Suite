import logging

import IO_files_util
import IO_internet_util
import topic_modeling_bert_util
import topic_modeling_gensim_util
import topic_modeling_mallet_util

logger = logging.getLogger(__name__)


def run_topic_modeling(
    inputDir,
    outputDir,
    chartPackage,
    dataTransformation,
    num_topics,
    BERT_var,
    split_docs_var,
    MALLET_var,
    optimize_intervals_var,
    Gensim_var,
    remove_stopwords_var,
    lemmatize_var,
    nounsOnly_var,
    Gensim_MALLET_var,
):
    """Run topic modeling (Gensim, MALLET, or BERTopic) over the corpus."""
    filesToOpen = []

    labels = []
    if BERT_var:
        labels.append("BERTopic")
    if MALLET_var:
        labels.append("MALLET")
    if Gensim_var:
        labels.append("Gensim")

    if not labels:
        logger.info(
            "Warning: No options selected. Please select at least one of the available options (BERTopic, MALLET, or Gensim) and try again."
        )
        return

    label = "-".join(labels)

    # Check internet availability
    if not IO_internet_util.check_internet_availability_warning(label + " Topic Modeling"):
        return

    if num_topics == 20:
        logger.info(
            "Warning: The default number of topics is 20. If you would like to specify a different number of topics, please do so and try again. YOU ARE STRONGLY ADVISED to run the algorithm repeatedly with different number of topics (e.g., 50, 40 30, 20, 10). You should then select the number of topics that gives you the best set of topics with no or minimum word overlap across topics. When running Gensim, the topic circles displayed in the Intertopic Distance Map (via multidimensional scaling) should be scattered throughout the four quadrants and should not be overlapping."
        )
        # reminders_util.checkReminder(scriptName, reminders_util.title_options_topic_modelling_number_of_topics,
        #                              reminders_util.message_topic_modelling_number_of_topics, True)

    # Create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory("", inputDir, outputDir, label="TM-" + label, silent=True)
    if outputDir == "":
        return

    # Run BERTopic
    if BERT_var:
        bert_files = topic_modeling_bert_util.run_BERTopic(inputDir, outputDir, split_docs_var)
        if bert_files:
            filesToOpen.extend(bert_files)

    # Run MALLET
    if MALLET_var:
        mallet_files = topic_modeling_mallet_util.run_MALLET(
            inputDir,
            outputDir,
            chartPackage,
            dataTransformation,
            optimize_intervals_var,
            num_topics,
        )
        if mallet_files:
            filesToOpen.extend(mallet_files)

    # Run Gensim
    if Gensim_var:
        gensim_files = topic_modeling_gensim_util.run_Gensim(
            inputDir,
            outputDir,
            "",
            num_topics,
            remove_stopwords_var,
            lemmatize_var,
            nounsOnly_var,
            Gensim_MALLET_var,
        )
        if gensim_files:
            filesToOpen.extend(gensim_files)

    return filesToOpen
