import logging

# written by Roberto Franzosi (Spring/summer 2020)
import os

import IO_files_util
import IO_libraries_util
import statistics_txt_util

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_sentence_analysis(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    compute_sentence_length_var,
    visualize_bySentenceIndex_var,
    visualize_bySentenceIndex_options_var,
    script_to_run,
    IO_values,
    sentence_complexity_var,
    text_readability_var,
    visualize_sentence_structure_var,
    num_sentences,
):
    """Compute per-sentence length, complexity, and readability measures."""
    config_filename = "NLP_default_IO_config.csv"

    filesToOpen = []  # Store all files that are to be opened once finished

    if (
        not compute_sentence_length_var
        and not visualize_bySentenceIndex_var
        and not sentence_complexity_var
        and not text_readability_var
        and not visualize_sentence_structure_var
    ):
        logger.info("No options have been selected.\n\nPlease, select an option and try again")
        return

    if compute_sentence_length_var:
        filesToOpen = statistics_txt_util.compute_sentence_length(
            inputFilename, inputDir, outputDir, config_filename, chartPackage, dataTransformation
        )

    if visualize_bySentenceIndex_var:
        filesToOpen = IO_files_util.runScript_fromMenu_option(
            script_to_run,
            IO_values,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            visualize_bySentenceIndex_options_var,
        )

    if sentence_complexity_var:
        if not IO_libraries_util.check_inputPythonJavaProgramFile("statistics_txt_util.py"):
            return
        filesToOpen = statistics_txt_util.compute_sentence_complexity(
            inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation
        )
        if filesToOpen is None:
            return

    if text_readability_var:
        if not IO_libraries_util.check_inputPythonJavaProgramFile("statistics_txt_util.py"):
            return
        statistics_txt_util.compute_sentence_text_readability(
            inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation
        )

    if visualize_sentence_structure_var:
        # if IO_libraries_util.check_inputPythonJavaProgramFile('DependenSee.Jar')==False:
        # if errorFound:
        # if inputFilename=='' and inputFilename.strip()[-4:]!='.txt':

        def first_file(path):
            try:
                entries = os.listdir(path)

                first = None
                for entry in entries:
                    if entry.endswith(".txt"):
                        first = os.path.join(path, entry)
                        return first

                return None

            except Exception as e:
                logger.info("Error  %s  has occurred.", e)
                return None

        inputFilename = first_file(inputDir)
        statistics_txt_util.sentence_structure_tree(inputFilename, outputDir, num_sentences)
