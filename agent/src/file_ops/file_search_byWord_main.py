import logging

# written by Roberto Franzosi October 2019, edited Spring 2020
import file_search_byWord_util
from util import collect

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_search_byWord(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    search_options,
    search_by_dictionary,
    selectedCsvFile,
    search_by_keyword,
    search_keyword_values,
    minus_K_words_sentences_var,
    plus_K_words_sentences_var,
    extract_sentences_var,
    coOccurring_keywords_var,
    create_subcorpus_var,
    search_options_menu_var,
    search_options_list,
    language_list,
    language,
):  # ,
    # extract_sentences_search_words_var_str):

    """Search the corpus for keywords or dictionary terms and export the matches."""
    config_filename = "NLP_default_IO_config.csv"

    filesToOpen = []
    extra_GUIs_var = False

    if not extra_GUIs_var and not search_by_dictionary and not search_by_keyword:
        logger.info(
            "Input error, No search options have been selected.\n\nPlease, select a search option and try again."
        )
        return

    if search_options_menu_var != "" and search_options_menu_var not in str(search_options_list):
        logger.info(
            "Warning, There is a search value '"
            + str(search_options_menu_var.get())
            + "' that has not been added (using the + button) to the csv file fields to be processed.\n\nAre you sure you want to continue?"
        )
        return

    # if extra_GUIs_var.get():
    #     if 'CoNLL' in extra_GUIs_menu_var.get():
    #     if 'Style' in extra_GUIs_menu_var.get():
    #     if 'Ngrams searches' in extra_GUIs_menu_var.get():
    #     if 'Wordnet' in extra_GUIs_menu_var.get():

    # # create a subdirectory of the output directory
    # outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='search',
    #                                                    silent=False)
    # if outputDir == '':

    if "Search within document" not in search_options_list:
        if "Search within sentence (default)" not in search_options_list:
            search_options_list.append("Search within sentence (default)")

    if "Lemmatize" in str(search_options_list):
        useLemma = True
    else:
        useLemma = False

    if search_by_dictionary:
        "SEARCH word(s) by values in dictionary file: " + selectedCsvFile
    else:
        "SEARCH word(s): " + search_keyword_values
    # @@
    # IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Word/collocation search start',
    #                     'Started running Word/collocation search at', True,
    #                                    True, '', True)

    if search_by_dictionary or search_by_keyword:
        if coOccurring_keywords_var:
            import NGrams_CoOccurrences_util

            outputFiles = NGrams_CoOccurrences_util.NGrams_coOccurrences_VIEWER(
                inputDir,
                outputDir,
                config_filename,
                chartPackage,
                dataTransformation,
                0,  # n-grams VIEWER
                1,  # coOccurring_keywords_var
                search_keyword_values,
                minus_K_words_sentences_var,
                plus_K_words_sentences_var,
                language_list,
                useLemma,
                0,
                "",
                0,
                "",
                "",
                0,
                search_options_list,
                0,
                "",
                "",
            )

            if outputFiles is not None:
                collect(filesToOpen, outputFiles)
        else:
            filesToOpen = file_search_byWord_util.search_sentences_documents(
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                search_by_dictionary,
                selectedCsvFile,
                search_by_keyword,
                search_keyword_values,
                minus_K_words_sentences_var,
                plus_K_words_sentences_var,
                extract_sentences_var,
                create_subcorpus_var,
                search_options_list,
                language,
                chartPackage,
                dataTransformation,
            )
