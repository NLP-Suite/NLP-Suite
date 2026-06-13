import logging

import config_util
import CoNLL_table_analyzer_main
import spaCy_util
import Stanford_CoreNLP_coreference_util
import Stanford_CoreNLP_util
from app_constants import CORENLP_URL
from pycorenlp import StanfordCoreNLP
from util import collect


def run_parsers_annotators(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    manual_Coref,
    parser_var,
    parser_menu_var,
    single_quote,
    CoNLL_table_analyzer_var,
    annotators_var,
    annotators_menu_var,
    package,
):
    """Run the selected parser/annotators (CoreNLP, spaCy, or Stanza) over the corpus."""
    logger = logging.getLogger(__name__)
    logger.info(
        "started: inputFilename=%s parser_var=%s parser_menu_var=%s", inputFilename, parser_var, parser_menu_var
    )
    StanfordCoreNLP(CORENLP_URL)

    # Set the config filename
    config_filename = "NLP_default_IO_config.csv"

    filesToOpen = []

    if "--------------" in annotators_menu_var:
        logger.info("annotator is invalid")
        raise ValueError(
            "Your annotator selection is invalid. It is only a label to make readability of menu options easier. Please select a different option and try again."
        )

    # Get the NLP package and language options
    (
        error,
        _,
        parsers,
        package_basics,
        language,
        package_display_area_value,
        encoding_var,
        export_json_var,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
    ) = config_util.read_NLP_package_language_config()  # package used to be _
    logger.info(package)
    language_list = [language]
    if package_display_area_value == "":
        raise ValueError(
            "The default NLP package and language has not been set up. Please set up the NLP package and language and try again."
        )
    logger.info("past1")
    # Placeholder for date options (adjust as needed)
    filename_embeds_date_var = False
    date_format_var = ""
    items_separator_var = ""
    date_position_var = ""

    # Check for invalid combinations
    if parser_var == 0 and CoNLL_table_analyzer_var == 1:
        logger.info("%s %s Error1", parser_var, CoNLL_table_analyzer_var)
        raise ValueError(
            "You have selected to open the CoNLL table analyser. This option expects to run the parser first. Please select the CoreNLP parser option and try again."
        )

    if annotators_var and annotators_menu_var == "":
        logger.info("%s %s Error2", annotators_var, annotators_menu_var)
        raise ValueError(
            "You have selected to run an annotator but no annotator has been selected. Please select an annotator and try again."
        )

    if annotators_menu_var == "Word embeddings (Word2Vec)":
        logger.info("was word2vec")
        raise ValueError(
            'The "Word embeddings (Word2Vec)" annotator is not available yet for either BERT or spaCy. Please select a different annotator and try again.'
        )

    # **Stanford CoreNLP**
    if package == "Stanford CoreNLP":
        if parser_var or (annotators_var and annotators_menu_var != ""):
            annotator = []

            if parser_var:
                if "PCFG" in parser_menu_var:
                    annotator = "parser (pcfg)"
                elif parser_menu_var == "Neural Network":
                    annotator = "parser (nn)"
            elif annotators_var and annotators_menu_var != "":
                if "NER annotator" in annotators_menu_var:
                    annotator = "NER"
                elif "Sentence splitter" in annotators_menu_var:
                    annotator = "Sentence"
                elif "Lemma annotator" in annotators_menu_var:
                    annotator = "Lemma"
                elif "POS annotator" in annotators_menu_var:
                    annotator = "All POS"
                elif "Gender" in annotators_menu_var:
                    annotator = "gender"
                elif "Quote" in annotators_menu_var:
                    annotator = "quote"
                elif "Normalized" in annotators_menu_var:
                    annotator = "normalized-date"
                elif "*" in annotators_menu_var:
                    annotator = ["gender", "normalized-date", "quote"]
                elif "Sentiment analysis" in annotators_menu_var:
                    annotator = ["sentiment"]
                elif "SVO" in annotators_menu_var:
                    annotator = ["SVO"]
                elif "OpenIE" in annotators_menu_var:
                    annotator = ["OpenIE"]
                elif "Coreference PRONOMINAL resolution" in annotators_menu_var:
                    logger.info("Stanford_CoreNLP_coreference_util")
                    # Run Coreference resolution
                    outputFiles, error_indicator = Stanford_CoreNLP_coreference_util.run(
                        config_filename,
                        inputFilename,
                        inputDir,
                        outputDir,
                        openOutputFiles,
                        chartPackage,
                        dataTransformation,
                        language,
                        memory_var,
                        export_json_var,
                        manual_Coref,
                    )
                    if error_indicator != 0:
                        raise RuntimeError("Stanford CoreNLP Co-Reference Resolution encountered an error.")
                    if outputFiles:
                        collect(filesToOpen, outputFiles)
                else:
                    logger.info("Selected annotator not available")
                    logger.warning("Selected annotator is not available. Please select a different option.")
                    return

            if len(annotator) > 0:
                logger.info("CoreNLP Annotate")
                # Run CoreNLP annotate
                outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
                    config_filename,
                    inputFilename,
                    inputDir,
                    outputDir,
                    openOutputFiles,
                    chartPackage,
                    dataTransformation,
                    annotator,
                    False,
                    language,
                    export_json_var,
                    memory_var,
                    document_length_var,
                    limit_sentence_length_var,
                    filename_embeds_date_var=filename_embeds_date_var,
                    date_format=date_format_var,
                    items_separator_var=items_separator_var,
                    date_position_var=date_position_var,
                    single_quote_var=single_quote,
                )
                if outputFiles is None:
                    return
                collect(filesToOpen, outputFiles)

    # **spaCy**
    elif package == "spaCy":
        if parser_var or (annotators_var and annotators_menu_var != ""):
            if parser_var:
                annotator = "depparse"

            if annotators_var:
                if annotators_menu_var == "":
                    raise ValueError("No annotator has been selected. Please select an annotator option and try again.")
                if "Sentence splitter (with sentence length)" in annotators_menu_var:
                    annotator = "Sentence"
                elif "Lemma annotator" in annotators_menu_var:
                    annotator = "Lemma"
                elif "POS annotator" in annotators_menu_var:
                    annotator = "All POS"
                elif "NER annotator" in annotators_menu_var:
                    annotator = "NER"
                elif "Sentiment analysis" in annotators_menu_var:
                    annotator = "sentiment"
                elif "SVO extraction" in annotators_menu_var:
                    annotator = "SVO"
                else:
                    raise ValueError(
                        f'The selected option "{annotators_menu_var}" is not available in spaCy. Please select another annotator and try again.'
                    )

            # Run spaCy annotate
            outputFiles = spaCy_util.spaCy_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                [annotator],
                False,
                language,
                memory_var,
                document_length_var,
                limit_sentence_length_var,
                filename_embeds_date_var=filename_embeds_date_var,
                date_format=date_format_var,
                items_separator_var=items_separator_var,
                date_position_var=date_position_var,
            )
            if outputFiles is None:
                return
            collect(filesToOpen, outputFiles)

    # **Stanza**
    elif package == "Stanza":
        if parser_var or (annotators_var and annotators_menu_var != ""):
            if parser_var:
                if parser_menu_var == "Constituency parser":
                    raise ValueError(
                        'The selected option "Constituency parser" is not available in Stanza. Please select a different option and try again.'
                    )
                annotator = "depparse"

            if annotators_var:
                if annotators_menu_var == "":
                    raise ValueError("No annotator has been selected. Please select an annotator option and try again.")
                if "Sentence splitter (with sentence length)" in annotators_menu_var:
                    annotator = "Sentence"
                elif "Lemma annotator" in annotators_menu_var:
                    annotator = "Lemma"
                elif "POS annotator" in annotators_menu_var:
                    annotator = "All POS"
                elif "NER annotator" in annotators_menu_var:
                    annotator = "NER"
                elif "Sentiment analysis" in annotators_menu_var:
                    annotator = "sentiment"
                elif "SVO extraction" in annotators_menu_var:
                    annotator = "SVO"
                else:
                    raise ValueError(
                        f'The selected option "{annotators_menu_var}" is not available in Stanza. Please select another annotator and try again.'
                    )
            from Stanza_util import Stanza_annotate

            # Run Stanza annotate
            outputFiles = Stanza_annotate(
                config_filename,
                inputFilename,
                inputDir,
                outputDir,
                openOutputFiles,
                chartPackage,
                dataTransformation,
                [annotator],
                False,
                language_list,
                memory_var,
                document_length_var,
                limit_sentence_length_var,
                filename_embeds_date_var=filename_embeds_date_var,
                date_format=date_format_var,
                items_separator_var=items_separator_var,
                date_position_var=date_position_var,
            )
            if outputFiles is None:
                return
            collect(filesToOpen, outputFiles)

    else:
        raise ValueError(f'The selected NLP package "{package}" is not supported.')

    if CoNLL_table_analyzer_var:
        logger.info("Running CoNLL Table Analyzer...")
        outputFiles = CoNLL_table_analyzer_main.run(
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            searchedCoNLLField="FORM",
            searchField_kw="e.g.: father",
            postag="NN",
            deprel="nsubj",
            co_postag="VB",
            co_deprel="dobj",
            Begin_K_sent_var=1,
            End_K_sent_var=5,
        )
        if outputFiles:
            filesToOpen.extend(outputFiles)
    # Return the list of output files
    return filesToOpen
