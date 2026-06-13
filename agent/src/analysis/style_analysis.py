import logging

import config_util
import file_spell_checker_util
import IO_files_util
import IO_libraries_util
import Stanza_util
import statistics_txt_util
import style_analysis_abstract_concreteness_analysis_util
from util import collect

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_style_analysis(
    inputFilename,
    inputDir,
    outputDir,
    chartPackage,
    dataTransformation,
    extra_GUIs_var,
    complexity_readability_analysis_var,
    complexity_readability_analysis_menu_var,
    vocabulary_analysis_var,
    vocabulary_analysis_menu_var,
    gender_guesser_var,
    min_rating,
    max_rating_sd,
):
    """Run the selected readability/complexity/vocabulary style analyses."""
    openOutputFiles = True
    config_filename = "NLP_default_IO_config.csv"

    filesToOpen = []  # Store all files that are to be opened once finished

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
    language_list = [language]

    # get the date options from filename
    # filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
    #     config_filename, config_input_output_numeric_options)

    if package_display_area_value == "":
        logger.info(
            "No setup for NLP package and language, The default NLP package and language has not been setup. \nPlease, click on the Setup NLP button and try again."
        )
        return

    openOutputFilesSV = openOutputFiles
    outputDir_style = outputDir

    if (
        not extra_GUIs_var
        and not complexity_readability_analysis_var
        and not vocabulary_analysis_var
        and not gender_guesser_var
    ):
        logger.info("Warning, No options have been selected.\n\nPlease, select an option and try again.")
        return

    # complexity_readability    ---------------------------------------------------------------------

    if complexity_readability_analysis_var:
        if "*" in complexity_readability_analysis_menu_var or "Sentence" in complexity_readability_analysis_menu_var:
            if not IO_libraries_util.check_inputPythonJavaProgramFile("statistics_txt_util.py"):
                return
            filesToOpen = statistics_txt_util.compute_sentence_complexity(
                inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation
            )
        if "*" in complexity_readability_analysis_menu_var or "Text" in complexity_readability_analysis_menu_var:
            if not IO_libraries_util.check_inputPythonJavaProgramFile("statistics_txt_util.py"):
                return
            statistics_txt_util.compute_sentence_text_readability(
                inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation
            )

        if complexity_readability_analysis_menu_var == "":
            logger.info(
                "Warning, No option has been selected for Complexity/readability analysis.\n\nPlease, select an option from the dropdown menu and try again."
            )
            return

    # vocabulary analysis    ---------------------------------------------------------------------

    if vocabulary_analysis_var:
        openOutputFilesSV = openOutputFiles
        openOutputFiles = False  # to make sure files are only opened at the end of this multi-tool script
        if vocabulary_analysis_menu_var == "":
            logger.info(
                "Warning, No option has been selected for Vocabulary analysis.\n\nPlease, select an option and try again."
            )
            return

        if "*" == vocabulary_analysis_menu_var:
            outputDir_style = IO_files_util.make_output_subdirectory(
                inputFilename, inputDir, outputDir, label="style", silent=True
            )
            if outputDir_style == "":
                return
        else:
            outputDir_style = outputDir

        if "*" in vocabulary_analysis_menu_var or "Vocabulary (via unigrams)" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "unigrams",
                language,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Hapax legomena" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "Hapax legomena",
                language,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if (
            "*" in vocabulary_analysis_menu_var
            or "Objectivity/subjectivity (via spaCy)" in vocabulary_analysis_menu_var
        ):
            if "*" in vocabulary_analysis_menu_var:
                pass
            else:
                pass
            annotator_available = True
            if annotator_available:
                outputFiles = statistics_txt_util.process_words(
                    config_filename,
                    inputFilename,
                    inputDir,
                    outputDir_style,
                    openOutputFiles,
                    chartPackage,
                    dataTransformation,
                    "Objectivity/subjectivity (via spaCy)",
                    language,
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Repetition: Words" in vocabulary_analysis_menu_var:
            if "*" in vocabulary_analysis_menu_var:
                process = "*Repetition: Words in first K and last K sentences"
            else:
                process = "Repetition: Words in first K and last K sentences"
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                process,
                language,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Repetition: Last" in vocabulary_analysis_menu_var:
            if "*" in vocabulary_analysis_menu_var:
                # this will force a deafault setting of k_str = '4' to avoid stopping all algorithms
                process = "*Repetition: Last K words of a sentence/First K words of next sentence"
            else:
                process = "Repetition: Last K words of a sentence/First K words of next sentence"
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                process,
                language,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Stanza" in vocabulary_analysis_menu_var:
            annotator = "Lemma"
            language_list = ["English"]
            memory_var = 8
            document_length_var = 1
            limit_sentence_length_var = 1000
            outputFiles = Stanza_util.Stanza_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                annotator,
                False,
                language_list,
                memory_var,
                document_length_var,
                limit_sentence_length_var,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "capital" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "capital",
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Word length" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "Word length",
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "Vowel" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "Vowel",
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "pathos" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.process_words(
                config_filename,
                inputFilename,
                inputDir,
                outputDir_style,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                "pathos",
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" == vocabulary_analysis_menu_var or "NLTK" in vocabulary_analysis_menu_var:
            # TODO: file_spell_checker_util.py warning line 186
            outputFiles = file_spell_checker_util.nltk_unusual_words(
                inputFilename, inputDir, outputDir_style, config_filename, chartPackage, dataTransformation
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" == vocabulary_analysis_menu_var or "Abstract" in vocabulary_analysis_menu_var:
            if language == "English":
                outputFiles = style_analysis_abstract_concreteness_analysis_util.main(
                    inputFilename,
                    inputDir,
                    outputDir_style,
                    config_filename,
                    chartPackage,
                    dataTransformation,
                    processType="",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)
            else:
                if not "*" == vocabulary_analysis_menu_var:
                    logger.info(
                        "Warning, The Abstract/concrete vocabulary analysis algorithm is only available for the English language."
                    )

        if "*" == vocabulary_analysis_menu_var or "Iconic" in vocabulary_analysis_menu_var:
            if language == "English":
                import style_analysis_iconicity_analysis_util

                outputFiles = style_analysis_iconicity_analysis_util.main(
                    inputFilename,
                    inputDir,
                    outputDir_style,
                    config_filename,
                    chartPackage,
                    dataTransformation,
                    min_rating,
                    max_rating_sd,
                    processType="",
                )
                if outputFiles is not None:
                    collect(filesToOpen, outputFiles)
            else:
                if not "*" == vocabulary_analysis_menu_var:
                    logger.info("Warning, The Iconicity analysis algorithm is only available for the English language.")

        if "*" == vocabulary_analysis_menu_var or "Yule" in vocabulary_analysis_menu_var:
            outputFiles = statistics_txt_util.yule(inputFilename, inputDir, outputDir, config_filename)
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

        if "*" in vocabulary_analysis_menu_var or "detection" in vocabulary_analysis_menu_var:
            outputFiles = file_spell_checker_util.language_detection(
                inputFilename,
                inputDir,
                outputDir_style,
                config_filename,
                openOutputFiles,
                chartPackage,
                dataTransformation,
            )
            if outputFiles is not None:
                collect(filesToOpen, outputFiles)

    if gender_guesser_var:
        IO_files_util.runScript_fromMenu_option(
            "Gender guesser", 0, inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation
        )
        return

    openOutputFiles = openOutputFilesSV
    return filesToOpen


def main():
    inputFilename = ""
    inputDir = "/Users/aidenamaya/nlp-suite/input"
    outputDir = "/Users/aidenamaya/nlp-suite/output"
    chartPackage = "Excel"
    dataTransformation = "No transformation"
    extra_GUIs_var = False
    complexity_readability_analysis_var = True
    complexity_readability_analysis_menu_var = "*"
    vocabulary_analysis_var = True
    vocabulary_analysis_menu_var = "*"
    gender_guesser_var = False
    min_rating = 5
    max_rating_sd = 1

    run_style_analysis(
        inputFilename=inputFilename,
        inputDir=inputDir,
        outputDir=outputDir,
        chartPackage=chartPackage,
        dataTransformation=dataTransformation,
        extra_GUIs_var=extra_GUIs_var,
        complexity_readability_analysis_var=complexity_readability_analysis_var,
        complexity_readability_analysis_menu_var=complexity_readability_analysis_menu_var,
        vocabulary_analysis_var=vocabulary_analysis_var,
        vocabulary_analysis_menu_var=vocabulary_analysis_menu_var,
        gender_guesser_var=gender_guesser_var,
        min_rating=min_rating,
        max_rating_sd=max_rating_sd,
    )


if __name__ == "__main__":
    main()
