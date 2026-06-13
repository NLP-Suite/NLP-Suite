import datetime
import glob
import logging
import os

import config_util
import IO_csv_util
import IO_files_util
import NGrams_CoOccurrences_util
import pandas as pd
from util import collect

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_ngrams(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    ngrams_options_list,
    Ngrams_compute_var,
    ngrams_menu_var,
    ngrams_options_menu_var,
    ngrams_size,
    search_words,
    minus_K_words_var,
    plus_K_words_var,
    Ngrams_search_var,
    csv_file_var,
    ngrams_viewer_var,
    CoOcc_Viewer_var,
    # within_sentence_co_occurrence_search_var,
    date_options,
    temporal_aggregation_var,
    viewer_options_list,
    language_list,
    config_input_output_numeric_options,
    number_of_years,
):
    """Compute n-gram frequencies and word co-occurrences, with charts."""
    config_filename = "NLP_default_IO_config.csv"

    extra_GUIs_var = False
    filesToOpen = []

    if csv_file_var != "":
        logger.info(
            "Warning This is a reminder that you are now running the N-grams searches with the csv input file\n\n"
            + csv_file_var
            + "\n\nPress Cancel then Esc to clear the csv file widget if you want to run the N-grams functions using the input file(s) displayed in the I/O configuration and try again."
        )
        return

    logger.info("language_list %s", language_list)

    total_file_number = 0
    error_file_number = 0
    error_filenames = []
    error_flag = False
    ngrams_word_var = True

    if ngrams_viewer_var:
        logger.info(
            "Warning, the N-grams VIEWER is temporarily disconnected, while we develop the same fast approach done for the Co-occurrences function.\n\nPlease, check back soon."
        )
        return
    # if csv_file_var!='':
    #
    #

    # if extra_GUIs_var.get() and extra_GUIs_menu_var.get()!='':
    #     if 'CoNLL' in extra_GUIs_menu_var.get():
    #     if 'WordNet' in extra_GUIs_menu_var.get():
    #     if 'Word search' in extra_GUIs_menu_var.get():

    # get the date options from filename
    (
        filename_embeds_date_var,
        date_format_var,
        items_separator_var,
        date_position_var,
        config_file_exists,
    ) = config_util.get_date_options(config_filename, config_input_output_numeric_options)

    if (
        not extra_GUIs_var
        and not Ngrams_compute_var
        and not Ngrams_search_var
        and not ngrams_viewer_var
        and not CoOcc_Viewer_var
    ):
        logger.info(
            "Warning, there are no options selected.\n\nPlease, select one of the available options and try again."
        )
        return
    if inputDir == "" and (ngrams_viewer_var or CoOcc_Viewer_var):
        logger.info(
            "Warning, you have selected to run the Viewer option but... this option requires a directory of txt files in input. Your configuration specifies a single txt file in input.\n\nPlease, select a directory in input or deselect the Viewer option and try again."
        )
        return

    # COMPUTE Ngrams ______________________________________________________________________________

    if Ngrams_compute_var:
        logger.info("N-grams options: %s", ngrams_options_list)
        ngrams_word_var = False
        lemmatize = False
        normalize = False
        excludePunctuation = False
        excludeArticles = False
        bySentenceIndex_word_var = False
        if ngrams_menu_var == "Word":
            ngrams_word_var = True
        else:
            pass
        if "Lemmatize" in str(ngrams_options_list):
            lemmatize = True
        frequency = None
        if "Hapax" in str(ngrams_options_list) and len(ngrams_options_list) == 1:
            frequency = 1

        excludePunctuation = False
        excludeArticles = False
        excludeDeterminers = False
        excludeStopWords = False

        # done in statistics_txt_util
        # outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='N-grams',
        #                                                    silent=False)
        # if outputDir == '':

        if "sensitive" in str(ngrams_options_list):
            pass
        if "insensitive" in str(ngrams_options_list):
            pass
        if "punctuation" in str(ngrams_options_list):
            excludePunctuation = True
        if "articles" in str(ngrams_options_list):
            excludeArticles = True
        if "determiners" in str(ngrams_options_list):
            excludeDeterminers = True
        if "stopwords" in str(ngrams_options_list):
            excludeStopWords = True
        if "sentence index" in str(ngrams_options_list):
            if ngrams_menu_var == "Word":
                bySentenceIndex_word_var = True
            else:
                pass

        if (
            "*" in str(ngrams_options_list)
            or "POSTAG" in str(ngrams_options_list)
            or "DEPREL" in str(ngrams_options_list)
            or "NER" in str(ngrams_options_list)
        ):
            logger.info("Warning, the selected option is not available yet.\n\nSorry!")
            if "Repetition" in str(ngrams_options_list):
                logger.info("Warning, do check out the repetition finder algorithm in the CoNLL Table Analyzer GUI.")
            return

        if ngrams_word_var or bySentenceIndex_word_var:
            import statistics_txt_util

            if ngrams_word_var or bySentenceIndex_word_var:
                hapax_words = True  # set it temporarily to True since we default to compute it every time
                wordgram = ngrams_word_var  # true r false depending upon whether n-grams are for word or character
                bySentenceID = bySentenceIndex_word_var
                outputFiles, outputDir = statistics_txt_util.compute_character_word_ngrams(
                    inputFilename,
                    inputDir,
                    outputDir,
                    config_filename,
                    ngrams_size,
                    frequency,
                    hapax_words,
                    normalize,
                    lemmatize,
                    # case_sensitive,
                    excludePunctuation,
                    excludeArticles,
                    excludeDeterminers,
                    excludeStopWords,
                    wordgram,
                    openOutputFiles,
                    chartPackage,
                    dataTransformation,
                    bySentenceID,
                )
                import statistics_csv_util

                for file in outputFiles:
                    if "csv" in file:
                        statistics_csv_util.data_transformation(file, dataTransformation).to_csv(file, index=False)
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

            # # character n-grams
            # if ngrams_character_var or bySentenceIndex_character_var:
            #     statistics_txt_util.compute_character_word_ngrams(GUI_util.window, inputFilename, inputDir,
            #                                                       outputDir, config_filename,
            #                                                       ngrams_size, frequency, normalize,
            #                                                       excludePunctuation, excludeArticles, excludeDeterminers, excludeStopWords, openOutputFiles,
            #                                                       chartPackage, dataTransformation,
            #                                                       bySentenceIndex_character_var)

    # SEARCH & VIEWER

    # The following set of options apply to both csv-file search and viewer

    if Ngrams_search_var or (ngrams_viewer_var or CoOcc_Viewer_var):
        logger.info("Search/VIEWER options: %s", viewer_options_list)
        logger.info("Search word(s): %s", search_words)

        normalize = False
        useLemma = False
        if "sensitive" in str(viewer_options_list):
            pass
        if "insensitive" in str(viewer_options_list):
            pass
        if "Normalize" in str(viewer_options_list):
            normalize = True
        if "Scale" in str(viewer_options_list):
            pass
        if "Lemmatize" in str(viewer_options_list):
            useLemma = True
        if "Partial" in str(viewer_options_list):
            pass
        else:
            pass
        if "within sentence" in str(viewer_options_list):
            within_sentence_co_occurrence_search_var = True
        else:
            within_sentence_co_occurrence_search_var = False

    # Search N-grams csv file ____________________________________________________________________________________________

    if Ngrams_search_var:
        outputFiles = NGrams_CoOccurrences_util.search_ngrams_csv_file(
            csv_file_var,
            inputDir,
            outputDir,
            config_filename,
            search_words,
            plus_K_words_var,
            minus_K_words_var,
            chartPackage,
            dataTransformation,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # VIEWER ____________________________________________________________________________________________

    if ngrams_viewer_var or CoOcc_Viewer_var:
        if date_options:
            new_date_format = date_format_var.replace("yyyy", "%Y").replace("mm", "%m").replace("dd", "%d")
            for folder, _subs, files in os.walk(inputDir):
                for filename in files:
                    if not filename.endswith(".txt"):
                        continue
                    filename = filename.replace(".txt", "")
                    total_file_number = total_file_number + 1
                    try:
                        date_text = ""
                        date_text = filename.split(items_separator_var)[date_position_var - 1]
                    except Exception:  # if a file in the folder has no date it will break the code
                        pass
                    try:
                        datetime.datetime.strptime(date_text, new_date_format)
                    except ValueError:
                        error_file_number = error_file_number + 1
                        error_filenames.append(
                            IO_csv_util.dressFilenameForCSVHyperlink(os.path.join(folder, filename + ".txt"))
                        )
                        error_flag = True

        if error_flag:
            df = pd.DataFrame(
                error_filenames,
                columns=["File with date not in position " + str(date_position_var)],
            )
            error_output = IO_files_util.generate_output_file_name(
                "", inputDir, outputDir, ".csv", "Date_position_errors_file"
            )
            df.to_csv(error_output, encoding="utf-8", index=False)
            logger.info(
                "Warning, there are "
                + str(error_file_number)
                + " files out of "
                + str(total_file_number)
                + " processed in the selected input directory with errors in either the date format or the date position. \n\nThe selected date format is "
                + str(date_format_var)
                + " and the selected date position is "
                + str(date_position_var)
                + ".\n\nClick OK to open a csv file with a list of files with erroneous dates. Check carefully, both date format and date position. Any erroneous file will need to be fixed or removed from the input directory before processing. You may also simply need to select a different date format and/or date position."
            )

            filesToOpen.append(error_output)

            # if openOutputFiles == True:

        if (ngrams_viewer_var or CoOcc_Viewer_var) and (chartPackage == "No charts"):
            logger.info(
                "Warning, the checkbox to compute Excel charts is unticked. Since the VIEWER produces Excel charts as output, the script will abort.\n\nPlease, tick the checkbox to produce Excel charts and try again."
            )
            return

        txtCounter = len(glob.glob1(inputDir, "*.txt"))
        if txtCounter == 0:
            logger.info(
                "Warning, there are no files with txt extension in the selected directory.\n\nPlease, select a different directory and try again."
            )
            return

        if txtCounter == 1:
            logger.info(
                "Warning, there is only one file with txt extension in the selected directory. The script requires at least two files.\n\nPlease, select a different directory and try again."
            )
            return

        if search_words != "" and not ngrams_viewer_var and not CoOcc_Viewer_var:
            logger.info(
                "Warning, you have entered the string "
                " + search_words + "
                " in the Search widget but you have not selected which Viewer you wish to use, N-gram or Co-Occurrence.\n\nPlease, select an option and try again."
            )
            return

        if search_words == "" and (ngrams_viewer_var or CoOcc_Viewer_var):
            logger.info(
                "Warning, you have selected to run a VIEWER but you have not entered any search strings in the Search widget.\n\nPlease, enter search values  and try again."
            )
            return

        if ngrams_viewer_var == 1 and len(search_words) > 0:
            if date_options == 0:
                logger.info(
                    "Warning, no Date options selected. The N-Grams routine requires date metadata (i.e., date information embedded in the document filenames, e.g., The New York Times_12-18-1899).\n\nPlease, tick the Date options checkbox, enter the appropariate date options and try again."
                )
                return

            # reminders_util.checkReminder(scriptName,
            #                              reminders_util.title_options_NGrams,
            #                              reminders_util.message_NGrams,
            #                              True)

            # run VIEWER ------------------------------------------------------------------------------------

            # if within_sentence_co_occurrence_search_var:
            #     outputFiles = NGrams_CoOccurrences_util.search_within_sentence_coOccurences(inputFilename,
            #                                     inputDir,
            #                                     config_filename,
            #                                     outputDir,
            #                                     exact_word_match)

            #     if outputFiles != None:
            #         if isinstance(outputFiles, str):
            outputFiles = NGrams_CoOccurrences_util.NGrams_coOccurrences_VIEWER(
                inputDir,
                outputDir,
                config_filename,
                chartPackage,
                dataTransformation,
                ngrams_viewer_var,
                CoOcc_Viewer_var,
                search_words,
                minus_K_words_var,
                plus_K_words_var,
                language_list,
                useLemma,
                date_options,
                temporal_aggregation_var,
                number_of_years,
                date_format_var,
                items_separator_var,
                date_position_var,
                viewer_options_list,
                ngrams_size,
                Ngrams_search_var,
                csv_file_var,
                within_sentence_co_occurrence_search_var,
            )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

        return filesToOpen

    # compute-only runs (no viewer) collect their outputs above
    return filesToOpen
