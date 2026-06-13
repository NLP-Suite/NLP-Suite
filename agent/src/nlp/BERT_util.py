"""Sentiment analysis with HuggingFace roBERTa models.

Ported June 2026 from the upstream desktop repo's BERT_util.py, sentiment
functions only: the upstream NER_tags_BERT, doc_summary_BERT, and
word_embeddings_BERT functions depend on packages not installed in the agent
image (contextualSpellCheck, bert-extractive-summarizer) and were not ported.

Models (downloaded from HuggingFace on first use, then cached):
  cardiffnlp/twitter-roberta-base-sentiment-latest  English
  cardiffnlp/twitter-xlm-roberta-base-sentiment     multilingual
"""

import csv
import logging
import os

import charts_util
import IO_csv_util
import IO_files_util
import IO_internet_util
from model_cache import get_hf_pipeline

logger = logging.getLogger(__name__)


def sentiment_analysis_BERT(sentiment_task, inputFilename, writer, Document_ID, Document):
    """Score each sentence of inputFilename with the given HF pipeline and write rows to the csv writer."""
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    if len(fulltext) < 1:
        logger.warning("Empty file %s", inputFilename)
        return

    from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    for i, s in enumerate(sentences, start=1):
        sentiment = sentiment_task(s)
        writer.writerow(
            {
                "Sentiment score": sentiment[0].get("score"),
                "Sentiment label": sentiment[0].get("label"),
                "Sentence ID": i,
                "Sentence": s,
                "Document ID": Document_ID,
                "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
            }
        )


def sentiment_main(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    mode,
    chartPackage="Excel",
    dataTransformation="No transformation",
    model_path="cardiffnlp/twitter-xlm-roberta-base-sentiment",
):
    """Run roBERTa sentiment over a single txt file or a directory of txt files."""
    # the model outputs one score and label per sentence; mode (mean/median) does not apply
    if not IO_internet_util.check_internet_availability_warning("BERT_util.py (Function sentiment_analysis_BERT)"):
        return

    filesToOpen = []

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_BERT", silent=True
    )
    if outputDir == "":
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "roBERTa", "", "", "", "", False, True
    )

    sentiment_task = get_hf_pipeline("sentiment-analysis", model_path, truncation=True)

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        fieldnames = ["Sentiment score", "Sentiment label", "Sentence ID", "Sentence", "Document ID", "Document"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if inputFilename != "":  # handle single file
            if not os.path.exists(inputFilename):
                logger.warning('Input file "%s" is invalid.', inputFilename)
                return
            sentiment_analysis_BERT(sentiment_task, inputFilename, writer, 1, inputFilename)
        else:  # handle directory
            if not os.path.isdir(inputDir):
                logger.warning('Input directory "%s" is invalid.', inputDir)
                return
            inputDocs = IO_files_util.getFileList(
                inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
            )
            nDocs = len(inputDocs)
            documentID = 0
            for file in inputDocs:
                documentID += 1
                logger.info("Processing file %d/%d %s", documentID, nDocs, os.path.basename(file))
                filename = os.path.join(inputDir, os.fsdecode(file))
                if filename.endswith(".txt"):
                    sentiment_analysis_BERT(sentiment_task, filename, writer, documentID, filename)
    filesToOpen.append(outputFilename)

    if chartPackage != "No charts":
        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Sentiment score"],
            chart_title="Frequency of roBERTa Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="roBERTa_scores",
            column_xAxis_label="Sentiment score",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=["Sentiment Score"],
            chart_title_label="roBERTa Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Sentiment label"],
            chart_title="Frequency of roBERTa Sentiment Labels",
            count_var=1,
            hover_label=[],
            outputFileNameType="roBERTa_labels",
            column_xAxis_label="Sentiment label",
            column_yAxis_label="Frequency",
            groupByList=["Document"],
            plotList=["Sentiment label"],
            chart_title_label="roBERTa Sentiment Labels",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen
