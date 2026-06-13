import difflib as df
import logging
import re

import IO_user_interface_util
import Stanford_CoreNLP_util
from app_constants import CORENLP_URL
from pycorenlp import StanfordCoreNLP

# Set up logging for tracking errors and processes
logger = logging.getLogger(__name__)

# Constants
CoreNLP_web = "https://stanfordnlp.github.io/CoreNLP/"

pronouns = r"\b(i|you|he|she|it|we|they|me|him|her|us|them|my|mine|hers|its|ours|their|your|yours|myself|yourself|himself|herself|oneself|itself|ourselves|yourselves|themselves)\b"


def split_into_sentences(text):
    """
    Helper function to split the input text into sentences.
    """
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(r"(Mr|St|Mrs|Ms|Dr)[.]", "\\1<prd>", text)
    text = re.sub(r"[.](com|net|org|io|gov|edu)", "<prd>\\1", text)
    text = re.sub(r"([0-9])[.]([0-9])", "\\1<prd>\\2", text)
    if "Ph.D" in text:
        text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub(r"\s([A-HJ-Z])[.]\s", " \\1<prd> ", text)
    text = re.sub(r"([A-Z][.][A-Z][.](?:[A-Z][.])?)", "\\1<stop>", text)
    text = re.sub(r"([A-Z])[.]([A-Z])[.]([A-Z])[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(r"([A-Z])[.]([A-Z])[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(r"\s(Inc|Ltd|Jr|Sr|Co)[.] ", " \\1<stop> ", text)
    text = re.sub(r"([A-Z])[.]([A-Z])[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(r"([A-Z])[.]", "\\1<prd>", text)
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def compare_results(origin_text, corefed_text):
    """
    Compare the original text with the coreference-resolved text.
    """
    origin_sentences = split_into_sentences(origin_text)
    corefed_sentences = split_into_sentences(corefed_text)
    origin_display = []
    corefed_display = []
    origin_non_coref = []
    corefed_non_coref = []

    for i in range(min(len(corefed_sentences), len(origin_sentences))):
        origin_display_highlighted = []
        corefed_display_highlighted = []

        origin_len = 0
        corefed_len = 0

        s = df.SequenceMatcher(lambda x: x in " '\t\"", origin_sentences[i], corefed_sentences[i], autojunk=False)
        matching = s.get_matching_blocks()

        for j in range(len(matching)):
            if origin_len != matching[j][0]:
                origin_display_highlighted.append((origin_len, matching[j][0]))
            if corefed_len != matching[j][1]:
                corefed_display_highlighted.append((corefed_len, matching[j][1]))
            origin_len = matching[j][0] + matching[j][2]
            corefed_len = matching[j][1] + matching[j][2]

        origin_display.append((origin_sentences[i], origin_display_highlighted))
        corefed_display.append((corefed_sentences[i], corefed_display_highlighted))

        non_coref = [(a.start(), a.end()) for a in list(re.finditer(pronouns, origin_sentences[i].lower()))]
        origin_non_coref.append((origin_sentences[i], non_coref))

        non_coref_corefed = [(a.start(), a.end()) for a in list(re.finditer(pronouns, corefed_sentences[i].lower()))]
        corefed_non_coref.append((corefed_sentences[i], non_coref_corefed))

    return origin_display, corefed_display, origin_non_coref, corefed_non_coref


def manualCoref(original_file, corefed_file, outputFile):
    """
    Handle manual coreference correction.
    """
    try:
        with open(original_file, encoding="utf-8", errors="ignore") as f:
            original_text = f.read()
        with open(corefed_file, encoding="utf-8", errors="ignore") as f:
            corefed_text = f.read()
    except Exception as e:
        logger.error(f"Error reading files for manual coreference: {e}")
        return 1

    origin_display, corefed_display, origin_non_coref, corefed_non_coref = compare_results(original_text, corefed_text)

    if len(corefed_display) == 0 and len(origin_display) == 0:
        logger.error("Cannot perform manual coreference due to empty displays.")
        return 1

    result = "\n".join(corefed_text.split("\n")[2:])

    try:
        with open(outputFile, "w", encoding="utf-8", errors="ignore") as f:
            f.write(result)
    except Exception as e:
        logger.error(f"Error saving the coreference-resolved file: {e}")
        return 1

    logger.info("Manual coreference completed successfully.")
    return 0


def run(
    config_filename,
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    language_var,
    memory_var,
    export_json_var,
    manual_Coref,
):

    StanfordCoreNLP(CORENLP_URL)
    corefed_files = []
    errorFound = False

    try:
        # Annotate with CoreNLP
        corefed_files = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            ["coref table", "coref"],
            False,
            language_var,
            export_json_var,
            memory_var,
        )

        # If manual coref is enabled and only a single file is being processed
        if manual_Coref and inputDir == "" and inputFilename != "":
            for file in corefed_files:
                if file.endswith(".txt"):
                    # Call manual coref on the processed file
                    error = manualCoref(inputFilename, file, file)
                    if error:
                        logger.error("Error during manual coreference resolution.")
                        return corefed_files, True  # Return error state if manual coref fails
        else:
            # Handle the case where manual coref is requested for directory processing
            if manual_Coref:
                IO_user_interface_util.timed_alert(
                    2000,
                    "Manual Coreference Unavailable",
                    "Manual Coreference is only available when processing a single file, not a directory.",
                    silent=True,
                )
            else:
                # If manual coref is not enabled, proceed normally
                IO_user_interface_util.timed_alert(2000, "Coreference Completed", "Coreference resolution completed.")

    except Exception as e:
        logger.error(f"Error in Coreference resolution: {e}")
        return corefed_files, True  # Return error state in case of any exception

    return corefed_files, errorFound
