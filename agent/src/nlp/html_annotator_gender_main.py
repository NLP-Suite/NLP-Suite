# Created on Thu Nov 21 09:45:47 2019
# rewritten by Roberto Franzosi April 2020, May 2022
# ported to the web agent June 2026 (tkinter GUI stripped)

import logging

import config_util
import html_annotator_dictionary_util
import Stanford_CoreNLP_util

logger = logging.getLogger(__name__)


def run(
    inputFilename,
    input_main_dir_path,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    CoreNLP_gender_annotator_var,
    CoreNLP_download_gender_file_var,
    CoreNLP_upload_gender_file_var,
    annotator_dictionary_var,
    annotator_dictionary_file_var,
    personal_pronouns_var,
    plot_var,
    year_state_var,
    firstName_entry_var,
    new_SS_folders,
    config_filename="NLP_default_IO_config.csv",
):
    """Annotate first names & pronouns in documents for gender (Male/Female)."""
    filesToOpen = []

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

    if annotator_dictionary_var and annotator_dictionary_file_var == "":
        raise ValueError(
            "You have selected to annotate your corpus using dictionary entries, "
            "but you have not provided the required .csv dictionary file."
        )
    if not CoreNLP_gender_annotator_var and not annotator_dictionary_var and not plot_var:
        raise ValueError("There are no options selected. Please, select one of the available options and try again.")

    # CoreNLP annotate
    if CoreNLP_gender_annotator_var:
        output = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            input_main_dir_path,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            "gender",
            False,
            language,
            export_json_var,
            memory_var,
        )
        # the gender annotator returns 2 Excel charts in addition to the csv file
        if len(output) > 0:
            filesToOpen.append(output)

    # dict annotate
    elif annotator_dictionary_var:
        if "CMU" in annotator_dictionary_file_var:  # CMU column name for Name is Names
            csv_field1_var = ["Names"]
        else:
            csv_field1_var = ["Name"]
        if "SS" in annotator_dictionary_file_var:  # US SS classify gender names as F M rather than Female or Male
            csvValue_color_list = ["Gender", "|", "F", "red", "|", "M", "blue", "|"]
        else:
            csvValue_color_list = ["Gender", "|", "Female", "red", "|", "Male", "blue", "|"]
        tagAnnotations = ['<span style="color: blue; font-weight: bold">', "</span>"]
        fileSubsc = "gender"
        output = html_annotator_dictionary_util.dictionary_annotate(
            inputFilename,
            input_main_dir_path,
            outputDir,
            config_filename,
            annotator_dictionary_file_var,
            csv_field1_var,
            csvValue_color_list,
            True,
            tagAnnotations,
            ".txt",
            fileSubsc,
        )
        if len(output) > 0:
            filesToOpen.append(output)

    # plot annotate (US Social Security first-name databases)
    elif plot_var:
        # the lib/namesGender SS data files were never ported from the desktop repo
        raise ValueError(
            "The US Social Security names option is not available: the lib/namesGender "
            "data files have not been ported from the desktop NLP-Suite repository."
        )

    return filesToOpen
