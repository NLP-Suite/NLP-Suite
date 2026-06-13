import logging
import os

import GUI_IO_util
import IO_csv_util
import IO_files_util
import pandas as pd
import Stanford_CoreNLP_util

logger = logging.getLogger(__name__)


def text_generate(inputFilename, inputDir):
    from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

    articles = []
    if inputFilename == "":
        for folder, _subs, files in os.walk(inputDir):
            logger.info("Processing folder: %s", os.path.basename(os.path.normpath(folder)))
            for filename in files:
                if not filename.endswith(".txt"):
                    continue
                logger.info("  Processing file: %s", filename)
                with open(os.path.join(folder, filename), encoding="utf-8", errors="ignore") as src:
                    text = src.read().replace("\n", " ")
                sentences = sentence_split_stanza_text(stanzaPipeLine(text))
                articles.append([sentences, IO_csv_util.dressFilenameForCSVHyperlink(filename)])
                # name, sentence, sentenceID, documentID, documentName
    else:
        inputDir = inputFilename
        if not inputFilename.endswith(".txt"):
            raise ValueError("The file selected is not a txt file. Please check again.")
        with open(inputFilename, encoding="utf-8", errors="ignore") as src:
            text = src.read().replace("\n", " ")
        sentences = sentence_split_stanza_text(stanzaPipeLine(text))
        articles.append([sentences, inputFilename])
    return articles, inputDir


def dictionary_annotate(
    config_filename,
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    memory_var,
    dictionary_file,
    personal_pronouns_var,
):
    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text

    document_length_var = 90000
    limit_sentence_length_var = 100

    tempOutputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
        config_filename,
        inputFilename,
        inputDir,
        outputDir,
        openOutputFiles,
        chartPackage,
        dataTransformation,
        "NER",
        False,
        "English",
        NERs=["PERSON"],
        memory_var=memory_var,
        document_length=document_length_var,
        sentence_length=limit_sentence_length_var,
        dateExtractedFromFileContent=False,
        filename_embeds_date_var=False,
        date_format="",
        items_separator_var="",
        date_position_var="",
    )

    if len(tempOutputFiles) == 0:
        return tempOutputFiles
    NER_fileName = tempOutputFiles[0]
    ners = pd.read_csv(NER_fileName, usecols=[0, 1], encoding="utf-8", on_bad_lines="skip")

    articles, inputDir = text_generate(inputFilename, inputDir)

    people = []
    for article_num, article in enumerate(articles):
        for sentence_num, sentence in enumerate(article[0]):
            # itertuples, not "for ner in ners": iterating a DataFrame yields
            # column labels, so the original desktop code never matched a row
            for ner in ners.itertuples(index=False):
                if ner[1] == "PERSON":
                    people.append([ner[0], sentence, sentence_num + 1, article_num + 1, article[1]])
            if personal_pronouns_var:
                tokens = tokenize_stanza_text(stanzaPipeLine(sentence))
                for token in tokens:
                    if token in ["his", "His", "He", "he", "Him", "him"]:
                        people.append([token, "Male", sentence, sentence_num + 1, article_num + 1, article[1]])
                    if token in ["She", "she", "Her", "her"]:
                        people.append([token, "Female", sentence, sentence_num + 1, article_num + 1, article[1]])

    dict_df = pd.read_csv(dictionary_file, encoding="utf-8", on_bad_lines="skip")
    for person in people:
        if len(person) == 5:
            temp = dict_df[dict_df["Name"] == person[0]]["Gender"]
            gender = "Not Found" if temp.empty else temp.values[0]
            person.insert(1, gender)
    annotated = pd.DataFrame(people, columns=["Name", "Gender", "Sentence", "SentenceID", "DocumentID", "Document"])
    output_path = IO_files_util.generate_output_file_name("", inputDir, outputDir, ".csv", "gender", "annotated")
    annotated.to_csv(output_path, encoding="utf-8")
    return tempOutputFiles


def SSA_annotate(year_state_var, firstName_entry_var, outputDir):
    filesToOpen = []
    for i in firstName_entry_var.split(","):
        output = SSA_annotate_help(year_state_var, i, outputDir)
        filesToOpen.extend(output)
    return filesToOpen


# return a list with the filename
def SSA_annotate_help(year_state_var, firstName_entry_var, outputDir):
    df1 = pd.read_csv(
        GUI_IO_util.namesGender_libPath + os.sep + "SS_state_yearOfBirth.csv", encoding="utf-8", on_bad_lines="skip"
    )
    target1 = df1[df1["Name"] == firstName_entry_var]
    df2 = pd.read_csv(
        GUI_IO_util.namesGender_libPath + os.sep + "SS_yearOfBirth.csv", encoding="utf-8", on_bad_lines="skip"
    )
    target2 = df2[df2["Name"] == firstName_entry_var]

    # STATE ---------------------------------------------------------

    if year_state_var == "State":
        output_path = IO_files_util.generate_output_file_name(
            "", "", outputDir, ".csv", year_state_var, firstName_entry_var
        )
        target1 = target1.drop(columns=["Year of birth"])
        group1 = target1.groupby(["Gender", "State"]).sum()
        group1.insert(0, "Name", firstName_entry_var)

        group1.reset_index().to_csv(output_path, encoding="utf-8", index=False)
        q2 = pd.read_csv(output_path, encoding="utf-8", on_bad_lines="skip")
        q2 = q2[["Name", "Gender", "Frequency", "State"]]
        q2 = q2.sort_values(by=["Frequency"], ascending=False)
        q2.to_csv(output_path, encoding="utf-8", index=False)

    # YEAR OF BIRTH  ---------------------------------------------------------

    elif year_state_var == "Year of birth":
        output_path = IO_files_util.generate_output_file_name(
            "", "", outputDir, ".csv", year_state_var, firstName_entry_var
        )

        target2.to_csv(output_path, encoding="utf-8", index=False)
        q2 = pd.read_csv(output_path, encoding="utf-8", on_bad_lines="skip")
        q2 = q2[["Name", "Gender", "Frequency", "Year of birth"]]
        q2 = q2.sort_values(by=["Frequency"], ascending=False)
        q2.to_csv(output_path, encoding="utf-8", index=False)

    # STATE & YEAR OF BIRTH  ---------------------------------------------------------

    elif year_state_var == "State & Year of birth":
        output_path = IO_files_util.generate_output_file_name(
            "", "", outputDir, ".csv", year_state_var, firstName_entry_var
        )

        target1.to_csv(output_path, encoding="utf-8", index=False)
        q2 = pd.read_csv(output_path, encoding="utf-8", on_bad_lines="skip")
        q2 = q2[["Name", "Gender", "Frequency", "Year of birth", "State"]]
        q2 = q2.sort_values(by=["Frequency"], ascending=False)
        q2.to_csv(output_path, encoding="utf-8", index=False)

    return [output_path]
