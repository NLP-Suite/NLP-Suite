import logging

# written by Roberto Franzosi November 2019
import os

import config_util
import IO_internet_util
import IO_libraries_util

logger = logging.getLogger(__name__)

os.environ["KMP_DUPLICATE_LIB_OK"] = (
    "True"  # for mac users to solve one error: https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
)
# RUN section ______________________________________________________________________________________________________________________________________________________


def transform_format(val):
    if val == 0:
        return 255
    else:
        return val


def run_wordcloud(
    inputFilename,
    inputDir,
    outputDir,
    visualization_tools,
    prefer_horizontal,
    font,
    max_words,
    lemmatize,
    exclude_stopwords,
    exclude_punctuation,
    lowercase,
    collocation,
    differentPOS_differentColor,
    prepare_image_var,
    selectedImage,
    use_contour_only,
    differentColumns_differentColors,
    csvField_color_list,
    openOutputFiles,
    doNotCreateIntermediateFiles,
):
    """Generate word-cloud images from the corpus."""
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

    if len(visualization_tools) == 0 and not differentColumns_differentColors:
        logger.info("Warning, No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if (differentColumns_differentColors) and ((len(inputFilename) == 0) or (inputFilename[-3:] != "csv")):
        logger.info(
            "Warning, You have selected the option of using different colors for different columns of a single csv file. But... you have not selected in input a csv file.\n\nPlease, select an appropriate csv file in input and try again."
        )
        return

    if (differentColumns_differentColors) and len(csvField_color_list) == 0:
        logger.info(
            "Warning, You have selected the option of using different colors for different columns of a single csv file. But... you have not selected in input the csv file field.\n\nPlease, select an appropriate csv file field and try again. "
        )
        return

    if differentColumns_differentColors and "|" not in str(csvField_color_list):
        logger.info(
            "Warning, you have selected the option of using different colors for different columns of a csv file. But... you have not selected the colors to be used.\n\nPlease, select a color by ticking the Color checkbox, select your preferred color and try again."
        )
        return

    if inputFilename[-4:] == ".csv":
        import CoNLL_util

        if not CoNLL_util.check_CoNLL(inputFilename, True):
            if not differentColumns_differentColors:
                logger.info(
                    "Warning, You have selected to use wordclouds with a csv file that is not a CoNLL table.\n\nYou must select the fields you want to use for wordclouds visualization by ticking the checkbox 'Use different colors...' and then selecting the csv field(s).\n\nPlease, select those options and try again. "
                )
                return

    if differentColumns_differentColors:
        visualization_tools = "Python WordCloud"

    if "Python" in visualization_tools:
        if prepare_image_var:
            # check internet connection
            # if not IO_internet_util.check_internet_availability_warning(visualization_tools):
            # https://www.adobe.com/express/feature/image/remove-background
            # https://express.adobe.com/tools/remove-background
            # https://www.slazzer.com/upload
            url = "https://www.remove.bg/"
            if not IO_libraries_util.open_url("remove.bg", url):
                return

    if (
        visualization_tools == "TagCrowd"
        or visualization_tools == "Tagul"
        or visualization_tools == "Tagxedo"
        or visualization_tools == "Wordclouds"
        or visualization_tools == "Wordle"
    ):
        # check internet connection
        if not IO_internet_util.check_internet_availability_warning(visualization_tools):
            return
        if visualization_tools == "TagCrowd":
            url = "https://tagcrowd.com/"
        if visualization_tools == "Tagul":
            url = "https://wordart.com/"
        if visualization_tools == "Tagxedo":
            url = "http://www.tagxedo.com/"
        if visualization_tools == "Wordclouds":
            url = "https://www.wordclouds.com/"
        if visualization_tools == "Wordle":
            url = "http://www.wordle.net/"

        if not IO_libraries_util.open_url(
            visualization_tools,
            url,
            message_title="",
            message="",
            config_filename="",
            reminder_title="",
            reminder_message="",
            scriptName="",
        ):
            return
    elif visualization_tools == "Python WordCloud":
        import wordclouds_util

        filesToOpen = wordclouds_util.python_wordCloud(
            inputFilename,
            inputDir,
            outputDir,
            configFileName="",
            selectedImage=selectedImage,
            use_contour_only=use_contour_only,
            wordcloud_title="",
            prefer_horizontal=prefer_horizontal,
            font=font,
            max_words=max_words,
            lemmatize=lemmatize,
            exclude_stopwords=exclude_stopwords,
            exclude_punctuation=exclude_punctuation,
            lowercase=lowercase,
            differentPOS_differentColors=differentPOS_differentColor,
            differentColumns_differentColors=differentColumns_differentColors,
            csvField_color_list=csvField_color_list,
            doNotListIndividualFiles=doNotCreateIntermediateFiles,
            openOutputFiles=openOutputFiles,
            collocation=collocation,
        )
    return filesToOpen
