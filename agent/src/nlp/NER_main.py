import logging

# Roberto Franzosi September 2020
# IBM https://ibm.github.io/zshot/ "pip install zshot"
import config_util
import spaCy_util
import Stanford_CoreNLP_util
import Stanza_util
from util import collect

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_NER(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    config_filename,
    NER_package,
    NER_list,
):
    """Extract named entities and export tables and charts."""
    config_input_output_numeric_options = [0, 1, 0, 1]

    config_filename = "NLP_default_IO_config.csv"
    filesToOpen = []  # Store all files that are to be opened once finished
    original_NER_list = NER_list

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
    language_list = [language]

    # get the date options from filename
    (
        filename_embeds_date_var,
        date_format_var,
        items_separator_var,
        date_position_var,
        config_file_exists,
    ) = config_util.get_date_options(config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == "":
        logger.info(
            "No setup for NLP package and language, The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again."
        )
        return

    if len(NER_list) == 0 and "CoreNLP" in NER_package:
        logger.info("No NER tag selected, No NER tag has been selected.\n\nPlease, select an NER tag and try again.")
        return

    # BERT -------------------------------------------------------------------------

    if "*" in NER_package or "BERT" in NER_package:
        if language != "English":
            logger.info(
                "Warning, NER in BERT is only available for the English language. Your currently selected language is ' + language + '.' "
                + "\n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the 'Setup NLP package and corpus language' to open the GUI where you can change the language option."
            )
            return
        import BERT_util

        NER_list = BERT_util.NER_dict
        outputFiles = BERT_util.NER_tags_BERT(
            inputFilename,
            inputDir,
            outputDir,
            config_filename,
            "",
            chartPackage,
            dataTransformation,
        )
        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # spaCy -------------------------------------------------------------------------

    if "*" in NER_package or "spaCy" in NER_package:
        document_length_var = 1
        limit_sentence_length_var = 1000
        NER_list = spaCy_util.NER_dict
        outputFiles = spaCy_util.spaCy_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            ["NER"],
            False,
            language,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
            NERs=NER_list,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # Stanford CoreNLP -------------------------------------------------------------------------

    if "*" in NER_package or "CoreNLP" in NER_package:
        NER_list = original_NER_list
        outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            "NER",
            language=language_var,
            NERs=NER_list,
            DoCleanXML=False,
            export_json_var=export_json_var,
            memory_var=memory_var,
            document_length=document_length_var,
            sentence_length=limit_sentence_length_var,
            extract_date_from_text_var=extract_date_from_text_var,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # Stanza -------------------------------------------------------------------------

    if "*" in NER_package or "Stanza" in NER_package:
        document_length_var = 1
        limit_sentence_length_var = 1000

        NER_list = original_NER_list

        outputFiles = Stanza_util.Stanza_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            "NER",
            False,
            language_list,
            memory_var,
            document_length_var,
            limit_sentence_length_var,
            filename_embeds_date_var=filename_embeds_date_var,
            NERs=NER_list,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    if "*" in NER_package:
        NER_list = []
