import logging
import os

import charts_matplotlib_seaborn_util
import charts_util
import file_converter_util
import IO_files_util
import pandas as pd
import requests
from app_constants import MALLET_URL, NLP_SUITE_ROOT
from util import collect

logger = logging.getLogger(__name__)


def mallet_to_agent_path(path):
    return path.replace("/app", NLP_SUITE_ROOT)


def call_mallet_api(command, args):
    api_url = MALLET_URL

    # Working locally
    payload = {"command": command, "args": args}

    logger.info(f"Calling MALLET: {command} with args {args}")

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to call MALLET API ({command}): {e}") from e


def run_MALLET(inputDir, outputDir, chartPackage, dataTransformation, OptimizeInterval, numTopics):
    filesToOpen = []

    # Validate text files in inputDir
    IO_files_util.GetNumberOfDocumentsInDirectory(inputDir, "txt")

    # (Optional) Keep warnings about number of files if you want them
    # if numFiles == 0:

    logger.info("Importing directory into MALLET format")

    # Convert directory into .mallet file
    import_args = {
        "input": "/app/input",
        "output": "/app/output/TM-MALLET_input/input.mallet",
        "keep-sequence": True,
        "remove-stopwords": True,
    }

    try:
        import_result = call_mallet_api("import-dir", import_args)
        if import_result.get("status") != "success":
            logger.info(f"Error: import-dir failed: {import_result}")
            return
    except Exception as e:
        logger.info(f"Error: MALLET import-dir API call failed: {e}")
        return

    logger.info("Training topics")

    #  Train topics on the .mallet file
    train_args = {
        "input": "/app/output/TM-MALLET_input/input.mallet",
        "num-topics": str(numTopics),
        "optimize-interval": str(OptimizeInterval),
        "output-topic-keys": "/app/output/TM-MALLET_input/topic_keys.txt",
        "output-doc-topics": "/app/output/TM-MALLET_input/doc_topics.txt",
    }

    try:
        train_result = call_mallet_api("train-topics", train_args)
        if train_result.get("status") != "success":
            logger.info(f"Error: train-topics failed: {train_result}")
            return
    except Exception as e:
        logger.info(f"Error: MALLET train-topics API call failed: {e}")
        return

    logger.info("Topic modeling complete!")

    # Map expected local file paths
    Keys_FileName = mallet_to_agent_path("/app/output/TM-MALLET_input/topic_keys.txt")
    Composition_FileName = mallet_to_agent_path("/app/output/TM-MALLET_input/doc_topics.txt")

    logger.info(Keys_FileName)
    logger.info(Composition_FileName)
    logger.info(outputDir)
    if not os.path.isfile(Keys_FileName) or not os.path.isfile(Composition_FileName):
        logger.info("Error: Expected output files from MALLET API were not found.")
        return

    # Convert TSV files (same as your old code)
    header_keys = ["Topic #", "Weight", "Keywords"]
    Keys_FileName = file_converter_util.tsv_converter(None, Keys_FileName, outputDir, header_keys)

    header_comp = ["Document ID", "Document"] + [f"Topic #{i} Weight in Document" for i in range(numTopics)]
    Composition_FileName = file_converter_util.tsv_converter(None, Composition_FileName, outputDir, header_comp)

    pd.read_csv(Composition_FileName, encoding="utf-8", on_bad_lines="skip")

    filesToOpen.append(Keys_FileName)
    filesToOpen.append(Composition_FileName)

    #  Create charts if requested
    if chartPackage != "No charts":
        columns_to_be_plotted_yAxis = [[0, 1]]
        chart_title = "MALLET Topics (Topic Weight by Topic)"
        xAxis = "Topic #"
        yAxis = "Topic weight"

        outputFiles = charts_util.run_all(
            columns_to_be_plotted_yAxis,
            Keys_FileName,
            outputDir,
            "MALLET_TM",
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            chart_type_list=["bar"],
            chart_title=chart_title,
            column_xAxis_label_var=xAxis,
            hover_info_column_list=[],
            count_var=0,
            column_yAxis_label_var=yAxis,
        )

        collect(filesToOpen, outputFiles)

    # Generate heatmap
    heatmap_files = charts_matplotlib_seaborn_util.MALLET_heatmap(
        Composition_FileName,
        Keys_FileName,
        outputDir,
        fig_set={"figure.figsize": (8, 6), "figure.dpi": 300},
        show_topics=True,
    )
    collect(filesToOpen, heatmap_files)

    return filesToOpen
