import collections
import csv
import logging
import math
import os
import re
import subprocess
import time

import charts_util
import constants_util
import file_cleaner_util
import IO_csv_util
import IO_files_util
import IO_libraries_util
import IO_user_interface_util
import nltk
import pandas
import pandas as pd
import reminders_util
import stanza
from app_constants import CORENLP_URL
from autocorrect import Speller
from fuzzywuzzy import fuzz, process
from IO_files_util import make_directory
from langdetect import detect_langs
from langid.langid import LanguageIdentifier, model
from model_cache import get_spacy_model
from pandas import DataFrame
from pycorenlp import StanfordCoreNLP  # python wrapper for Stanford CoreNLP
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from spellchecker import SpellChecker
from textblob import Word
from util import collect

logger = logging.getLogger(__name__)


def lemmatizing(word):  # edited by Claude Hu 08/2020
    # https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    pos = ["n", "v", "a", "s", "r"]  # list of postags
    result = word
    for _p in pos:
        # if lemmatization with any postag gives different result from the word itself
        # that lemmatization is returned as result
        from Stanza_functions_util import lemmatize_stanza_word, stanzaPipeLine

        lemma = lemmatize_stanza_word(stanzaPipeLine(word))
        if lemma != word:
            result = lemma
            break
    return result


# https://www.nltk.org/book/ch02.html
def nltk_unusual_words(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    chartPackage="Excel",
    dataTransformation="No transformation",
):

    import nltk

    nltk.download("words")

    from Stanza_functions_util import (
        lemmatize_stanza_doc,
        lemmatize_stanza_word,
        stanzaPipeLine,
    )

    filesToOpen = []
    unusual = []
    container = []
    documentID = 0
    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="NLTK_unus", silent=True
    )
    if outputDir == "":
        return

    outputFilename_list = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "NLTK_unus_list", ""
    )
    filesToOpen.append(outputFilename_list)

    outputFilename_byDoc = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "NLTK_unus_byDoc", ""
    )
    filesToOpen.append(outputFilename_byDoc)

    # startTime=IO_user_interface_util.timed_alert(3000, 'NLTK unusual words-spelling checker start',
    #                                    'Started running NLTK unusual words-spelling checker at',
    #                                              True, '', True, '', False)

    # already shown in NLP.py

    # https://stackoverflow.com/questions/28339622/is-there-a-corpus-of-english-words-in-nltk
    import GUI_IO_util

    NLTK_corpus_lemmatized = GUI_IO_util.wordLists_libPath + os.sep + "NLTK_corpus_lemmatized.csv"
    filesToOpen.append(NLTK_corpus_lemmatized)

    if not os.path.exists(NLTK_corpus_lemmatized):
        logger.info(
            "Warning, The csv file of NLTK corpus of lemmatized English words was not found in the lib subdir ' + GUI_IO_util.wordLists_libPath + '\n\nThe script will now run the much slower lemmatization function.\n\nPlease, alert the NLP Suite developers of the missing file."
        )
        # this approach is extremely slow
        NLTK_english_vocab_lemmatized = []
        nltk.corpus = nltk.corpus.words.words()
        NLTK_corpus_size = len(nltk.corpus)
        for corpus_index, w in enumerate(nltk.corpus):
            lemma = lemmatize_stanza_word(stanzaPipeLine(w))
            NLTK_english_vocab_lemmatized.append(lemma)
            logger.info(
                "   NLTK corpus word " + str(corpus_index) + "/" + str(NLTK_corpus_size) + "  " + w + " / " + lemma
            )
        # this is much faster but does not lemmatize
        outputFilename_NLTK_corpus = IO_files_util.generate_output_file_name(
            "", "", outputDir, ".csv", "NLTK_corpus", ""
        )
        filesToOpen.append(outputFilename_NLTK_corpus)
        NLTK_english_vocab_lemmatized.insert(0, "NLTK corpus lemmatized words")
        if IO_csv_util.list_to_csv(NLTK_english_vocab_lemmatized, outputFilename_NLTK_corpus):
            return
    else:
        NLTK_english_vocab = open(NLTK_corpus_lemmatized, encoding="utf-8", errors="ignore").read()
        NLTK_english_vocab_lemmatized = NLTK_english_vocab.split("\n")  # '\n'.english_vocab()
    NLTK_english_vocab_lemmatized.pop(0)
    # NLTK_english_vocab_lemmatized are distinct values
    NLTK_english_vocab_lemmatized = set(NLTK_english_vocab_lemmatized)
    # you can add words to NLTK words, e.g.,
    # https://stackoverflow.com/questions/72099620/how-to-solve-missing-words-in-nltk-corpus-words-words
    ALL_files_unusual = []
    text_list_lemmatized = []
    for file in files:
        documentID = documentID + 1
        head, tail = os.path.split(file)
        logger.info("Processing file " + str(documentID) + "/" + str(nFile) + " " + tail)
        text = open(file, encoding="utf-8", errors="ignore").read()
        # the NLTK vocab is lowercase, lemmatized; must lemmatize your input
        # lemmatize the input corpus, to be comparable to the lemmatized NLTK corpus
        lemmatized_text = lemmatize_stanza_doc(stanzaPipeLine(text))
        for w in lemmatized_text:
            if w.isalpha():
                text_list_lemmatized.append(w)
        # convert list to set to produce distinct values
        text_vocab_lemmatized = set(text_list_lemmatized)

        # ------------------------------------------------------------------------------
        unusual = text_vocab_lemmatized - NLTK_english_vocab_lemmatized
        # ------------------------------------------------------------------------------

        # reconvert back to list
        text_vocab_lemmatized = list(text_vocab_lemmatized)
        # convert the set to a list
        unusual = list(unusual)
        # sort the list
        unusual.sort()
        ALL_files_unusual = ALL_files_unusual + unusual

        [container.append([word, documentID, IO_csv_util.dressFilenameForCSVHyperlink(file)]) for word in unusual]

    ALL_files_unusual.sort()
    ALL_files_unusual = set(ALL_files_unusual)
    ALL_files_unusual = list(ALL_files_unusual)
    ALL_files_unusual.sort()

    outputFilename_input_corpus = IO_files_util.generate_output_file_name(
        "", "", outputDir, ".csv", "Input_corpus_ALL_distinct_lemmatized_words", ""
    )
    filesToOpen.append(outputFilename_input_corpus)
    text_set = set(text_list_lemmatized)  # set are collections of unordered distinct items
    text_list = list(text_set)
    text_list.sort()
    text_list.insert(0, "Input lemmatized words (ALL distinct)")
    if IO_csv_util.list_to_csv(text_list, outputFilename_input_corpus):
        return

    if len(container) > 0:
        ALL_files_unusual.insert(0, "Misspelled-unusual lemmatized word")
        if IO_csv_util.list_to_csv(ALL_files_unusual, outputFilename_list):
            return
        container.insert(0, ["Misspelled-unusual lemmatized word", "Document ID", "Document"])
        if IO_csv_util.list_to_csv(container, outputFilename_byDoc):
            return
    else:
        if nFile == 1:
            return

    # NLTK unusual words
    chartPackage = "No charts"  # no point exporting charts
    if chartPackage != "No charts":
        if nFile > 10:
            pass
            # TODO: implement some front end?
            # def excel_chart_warning(request):
            #     nFile =

            # def start_excel_task(request):
            #     if request.method == "POST":
            #         # Run the Excel chart computation

            #  if result==False:
            #      pass

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename_byDoc,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Misspelled-unusual lemmatized word"],
            chart_title="Frequency of Misspelled-Unusual Words",
            count_var=0,  # no point counting; all values are distinct
            hover_label=[],
            outputFileNameType="",  # 'line_bar',
            column_xAxis_label="Misspelled-Unusual lemmatized word",
            groupByList=["Document"],
            plotList=[],
            chart_title_label="",
        )

        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    return filesToOpen


def generate_simple_csv(Dataframe):
    pass


# check within subdirectory
def check_for_typo_sub_dir(
    inputDir,
    outputDir,
    inputCsvDictionaryFile,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    NERs,
    similarity_value,
    by_all_tokens_var,
    spelling_checker_var=False,
):
    outputFileName_complete = IO_files_util.generate_output_file_name(
        "",
        inputDir,
        outputDir,
        ".csv",
        "WordSimil",
        str(similarity_value),
        "Edit_dist_algo",
        "NERs",
        "Full-table",
    )
    outputFileName_simple = IO_files_util.generate_output_file_name(
        "",
        inputDir,
        outputDir,
        ".csv",
        "WordSimil",
        str(similarity_value),
        "Edit_dist_algo",
        "NERs",
        "Concise-table",
    )
    filesToOpen = []
    if inputDir == "":
        return
    subdir = [f.path for f in os.scandir(inputDir) if f.is_dir()]
    if subdir == []:
        logger.info(
            "Check Subdir option There are no sub directories under the selected input directory\n\n"
            + inputDir
            + "\n\nPlease, uncheck your subdir option if you want to process this directory and try again."
        )

    df_list = []
    for _dir in subdir:
        dfs = check_for_typo(
            inputDir,
            outputDir,
            inputCsvDictionaryFile,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            NERs,
            similarity_value,
            by_all_tokens_var,
        )
        df_list.append(dfs)
    if len(df_list) > 0:
        df_complete_list = [df[0] for df in df_list]
        df_simple_list = [df[1] for df in df_list]
        df_complete = pd.concat(df_complete_list, ignore_index=True)
        df_simple = pd.concat(df_simple_list, ignore_index=True)
        df_simple.to_csv(outputFileName_simple, encoding="utf-8", index=False)
        df_complete.to_csv(outputFileName_complete, encoding="utf-8", index=False)

        filesToOpen.append(outputFileName_simple)
        filesToOpen.append(outputFileName_complete)

        inputFilename = ""  # temporary fix
        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            inputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Typo?"],
            chart_title="Frequency of Potential Typos",
            count_var=1,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
            hover_label=[],
            outputFileNameType="Leven_spell",
            column_xAxis_label="Typo",
            groupByList=[],
            plotList=[],
            chart_title_label="",
        )
        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    return filesToOpen


# the check for typo function
# check whether a single word is considered as typo within a list of words
# design choice for this algorithm:
#   if the word is shorter than user-supplied word length (default 4 characters):
#       1 or more character mistake will be considered as typo should use 1 only for longer words
#   else (the word is longer than or equal to user-supplied word length (default 4 characters):
#       2 or more character mistake will be considered as typo; DEFAULT

# checklist contains words with more than 1 time of appearance
# similarity_value is the gaging_difference attribute

# -------------------Angel-----------------End of fuzzywuzzy


def fuzzywuzzy_check_dist(input_word, checklist, similarity_value):  # similarity_value will be on a scale 1-100
    exist_typo = False
    for word in checklist:
        # TODO see also pyslpellchecker https://pypi.org/project/pyspellchecker/ which is based on
        #   Peter Norvig’s blog post on setting up a simple spell checking algorithm based on Levenshtein's edit distance
        # It uses a Levenshtein Distance
        dist = fuzz.ratio(input_word, word[0])
        if dist >= similarity_value and dist < 100:  # cannot be 100 as that means matching a typo with another typo
            exist_typo = True
            return exist_typo, word[0], word[1]
    return exist_typo, "", ""


# -------------------Angel-----------------End of fuzzywuzzy


def check_edit_dist(input_word, checklist, similarity_value):
    exist_typo = False
    for word in checklist:
        # TODO see also pyslpellchecker https://pypi.org/project/pyspellchecker/ which is based on
        #   Peter Norvig’s blog post on setting up a simple spell checking algorithm based on Levenshtein's edit distance
        # It uses a Levenshtein Distance
        dist = nltk.edit_distance(input_word, word[0])
        if len(input_word) >= similarity_value:
            if 0 < dist <= 2:
                exist_typo = True
                return exist_typo, word[0], word[1]
                # word[0] is the token, word[1] is the frequency of the token in the entire corpus
        else:
            if 0 < dist <= 1:
                exist_typo = True
                return exist_typo, word[0], word[1]
    return exist_typo, "", ""


# the main checking function, takes input:
#   CoreNLPDirectory, inputDir, output_file_path
# now checking for NER list ['CITY', 'LOCATION', 'PERSON']
# output csv header list: ['NNPs', 'sentenceID', 'DocumentID', 'fileName', 'NamedEntity', 'potential_Typo']


# using Levenshtein distance to check for typos
def check_for_typo(
    inputDir,
    outputDir,
    inputCsvDictionaryFile,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    NERs,
    similarity_value,
    by_all_tokens_var,
):

    def find_similar_words(word, true_spellings, threshold=95):
        exact_match = [w for w in true_spellings if w.lower() == word.lower()]
        if exact_match:
            return [(exact_match[0], 100)]
        similar = process.extractBests(word, true_spellings, score_cutoff=threshold)
        return similar

    def preprocess_word_list(word_list, true_spellings):
        processed_words = {}
        for word in word_list:
            if len(word) > 3 and word.isalpha():
                lower_word = word.lower()
                if lower_word in true_spellings:
                    processed_words[word] = "Correct spell"
                elif word[0].isupper():
                    processed_words[word] = "Potential new spell"
                else:
                    processed_words[word] = "Unknown"
        return processed_words

    def check_spell(word, sentence, processed_words, speller, true_spellings):
        similar_words = find_similar_words(word, true_spellings)
        if similar_words and similar_words[0][1] == 100:
            return word, "Correct spell", similar_words

        if word in processed_words:
            status = processed_words[word]
            if status == "Unknown":
                corrected = speller.correction(word)
                if corrected != word:
                    return corrected, "Potential typo", similar_words
                else:
                    return word, "Not a spell", []
            elif status == "Potential new spell":
                return word, status, similar_words
            else:
                return word, status, []
        else:
            return word, "Not a spell", []

    def find_unused_spells(true_spellings, words_in_book):
        return true_spellings - set(words_in_book)

    def find_potential_new_spells(documents, true_spellings):
        potential_spells = set()
        for document in documents:
            for sentence in document[0]:
                words = sentence.split()
                for word in words:
                    if word.isalpha() and len(word) > 3 and word not in true_spellings:
                        if identify_potential_spell(sentence, word, true_spellings):
                            potential_spells.add(word)
        return potential_spells

    def analyze_processed_words(processed_words, true_spellings):
        correct_spells = set()
        potential_new_spells = set()
        potential_typos = set()

        for word, status in processed_words.items():
            if status == "Correct spell":
                correct_spells.add(word)
            elif status == "Potential new spell":
                potential_new_spells.add(word)
            elif status == "Unknown":
                potential_typos.add(word)

        unused_spells = true_spellings - set(word.lower() for word in correct_spells)

        return correct_spells, potential_new_spells, potential_typos, unused_spells

    def identify_potential_spell(sentence, word, true_spellings):
        lower_sentence = sentence.lower()
        lower_word = word.lower()

        spell_patterns = [
            r"\b" + re.escape(lower_word) + r"!",
            r'"' + re.escape(lower_word) + r'"',
            r"cast.*" + re.escape(lower_word),
            r"spell.*" + re.escape(lower_word),
            r"incantation.*" + re.escape(lower_word),
            r"wand.*" + re.escape(lower_word),
            r"shouted.*" + re.escape(lower_word),
            r"yelled.*" + re.escape(lower_word),
        ]

        if any(re.search(pattern, lower_sentence) for pattern in spell_patterns):
            return True

        if lower_word in true_spellings:
            return True

        return False

    import csv

    def write_additional_analysis(
        correct_spells,
        potential_new_spells,
        potential_typos,
        unused_spells,
        outputDir,
        true_spellings,
    ):
        output_file = os.path.join(outputDir, "spell_analysis.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write header
            csvwriter.writerow(["Category", "Spell in Dict", "Spell in Book", "Status"])

            # Write correct spells
            for spell in sorted(correct_spells):
                csvwriter.writerow(["Correct Spell", spell, spell, "Exact match in dictionary"])

            # Write potential new spells
            for spell in sorted(potential_new_spells):
                similar = find_similar_words(spell, true_spellings)
                if similar and similar[0][1] == 100:
                    csvwriter.writerow(["Correct Spell", spell, spell, "Exact match in dictionary"])
                elif similar and similar[0][1] >= 95:
                    similar_str = ", ".join([f"{w}" for w, s in similar]) if similar else ""
                    csvwriter.writerow(
                        [
                            "Potential New Spell",
                            spell,
                            similar_str,
                            "Similar spell found",
                        ]
                    )

            # Write potential typos
            for word in sorted(potential_typos):
                similar = find_similar_words(word, true_spellings)
                if similar and similar[0][1] == 100:
                    csvwriter.writerow(["Correct Spell", word, word, "Exact match in dictionary"])
                elif similar and similar[0][1] >= 95:
                    similar_str = ", ".join([f"{w}" for w, s in similar]) if similar else ""
                    csvwriter.writerow(["Potential Typo", word, similar_str, "Similar spell found"])

            # Write unused spells
            for spell in sorted(unused_spells):
                csvwriter.writerow(["Unused Spell", spell, "", "Not found in text"])

        return output_file

    filesToOpen = []
    all_header_rows_dict = []
    ner_dict = {}

    # check that the CoreNLPdir has been setup
    CoreNLPDir, existing_software_config, errorFound = IO_libraries_util.external_software_install(
        "file_spell_checker_util",
        "Stanford CoreNLP",
        "",
        silent=False,
        errorFound=False,
    )

    if CoreNLPDir is None or CoreNLPDir == "":
        return
    if by_all_tokens_var or inputCsvDictionaryFile != "":
        pass
    else:
        if NERs[0] == "*":
            NERs = [
                "CITY",
                "LOCATION",
                "PERSON",
                "COUNTRY",
                "STATE_OR_PROVINCE",
                "ORGANIZATION",
            ]
        else:
            pass
    documents = []
    folderID = 0
    fileID = 0

    # read dictionary file
    if inputCsvDictionaryFile != "":
        df = pd.read_csv(inputCsvDictionaryFile, encoding="utf-8", on_bad_lines="skip")
        # only the first columns matters; any other column is ignored
        true_spellings = df.iloc[:, 0]
        # convert to a set of unique, distinct value
        true_spellings = set(true_spellings)

        # Check if there is repetition in the dictionary file

        if len(true_spellings) != len(df):
            logger.info("There are repeated words in the dictionary file.")
            return
        else:
            logger.info("All words in the dictionary file are distinct.")

    # startTime=IO_user_interface_util.timed_alert(3000, 'Word similarity start', 'Started running Word similarity at',
    #                                              True, '', True, '', True)

    # TODO which annotators is it using? We do not need all annotators! Sentence splitter and tokenizer (and NER)
    p = subprocess.Popen(
        [
            "java",
            "-mx" + str(5) + "g",
            "-cp",
            os.path.join(CoreNLPDir, "*"),
            "edu.stanford.nlp.pipeline.StanfordCoreNLPServer",
            "-timeout",
            "999999",
        ]
    )
    time.sleep(5)

    logger.info("Starting to run Stanford CoreNLP to prepare data for each folder and file.")

    for folder, subs, files in os.walk(inputDir):
        nFolders = len(subs) + 1
        folderID += 1
        logger.info(
            "\nProcessing folder "
            + str(folderID)
            + "/"
            + str(nFolders)
            + ": "
            + os.path.basename(os.path.normpath(folder))
        )
        fileID = 0
        for filename in files:
            fileID += 1
            if not filename.endswith(".txt"):
                continue
            logger.info("  Processing file " + str(fileID) + "/" + str(len(files)) + ": " + filename)
            dir_path = os.path.join(folder, filename)
            with open(dir_path, encoding="utf-8", errors="ignore") as src:
                text = src.read().replace("\n", " ")
                text = text.replace("%", "percent")
                NLP = StanfordCoreNLP(CORENLP_URL)
            from Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

            sentences = sentence_split_stanza_text(stanzaPipeLine(text))
            documents.append([sentences, filename, dir_path])
    if by_all_tokens_var:
        # TODO header_rows ends up including filename as well; must only include the words in the documents
        # for document_number, document in enumerate(documents):
        #     for sentence_number, sentence in enumerate(document[0]):
        #         for word in NLP.word_tokenize(sentence):
        #             if (len(word) > 3) and (word not in processed_word_list) and (word.isalpha()):
        #                 # print("      Processing DISTINCT word " + str(processed_wordID) + "/" + str(
        #                 #     len(distinct_word_list)) + ": " + word)
        #                 if respelled_word != word:
        #                     header_rows = [[word, respelled_word, sentence_number + 1, document_number + 1, sentence, document[1],
        #                                     IO_csv_util.dressFilenameForCSVHyperlink(document[2]), '']]
        #                     # if value_tuple[0]:  # a close match been found
        #                     #     header_row.append(
        #                     #         value_tuple[2])  # returned similar word frequency from check_edit_list

        header_rows = [
            [
                token,
                sentence_number + 1,
                document_number + 1,
                sentence,
                document[1],
                IO_csv_util.dressFilenameForCSVHyperlink(document[2]),
                "",
            ]
            for document_number, document in enumerate(documents)
            for sentence_number, sentence in enumerate(document[0])
            for token in NLP.word_tokenize(sentence)
        ]  # document[1]: filename, document[0]:sentences
        temp = [elmt[0] for elmt in header_rows]  # list of all tokens
        all_header_rows_dict = [(item, count) for item, count in collections.Counter(temp).items() if count > 1]
        header_row_list_to_check = header_rows

    else:
        logger.info("Running NER on each file...")
        logger.info("documents:  %s", documents)

        NER = [
            [
                ners[0],
                sentence_number + 1,
                document_number + 1,
                sentence,
                document[1],
                IO_csv_util.dressFilenameForCSVHyperlink(document[2]),
                ners[1],
            ]
            for document_number, document in enumerate(documents)
            for sentence_number, sentence in enumerate(document[0])
            for ners in NLP.ner(sentence)
            if ners[1] in NERs
        ]
        ner_dict = {}
        for each_ner in NERs:
            temp = [
                elmt[0] for elmt in NER if elmt[-1] == each_ner
            ]  # list of all tokens that belong to specified NER categories
            ner_dict[each_ner] = [(item, count) for item, count in collections.Counter(temp).items() if count > 1]
        # Testing why NRE is empty
        # for document_number, document in enumerate(documents):
        #     for sentence_number, sentence in enumerate(document[0]):
        #         for ner in ners:
        #             if ner[1] in NERs:
        #                 NER.append([ner[0], sentence_number + 1, document_number + 1, sentence, document[1],
        #                             IO_csv_util.dressFilenameForCSVHyperlink(document[2]), ner[1]])
        #
        # End of test
        header_row_list_to_check = NER
        word_list = []
        for document in documents:
            for sentence in document[0]:
                ners = NLP.ner(sentence)

                for token, _entity_type in ners:
                    word_list.append(token)

        word_list = list(set(word_list))
        processed_words = preprocess_word_list(word_list, true_spellings)
        logger.info("Now word_list:  %s", word_list)
        unused_spells = find_unused_spells(true_spellings, set(word_list))
        potential_new_spells = find_potential_new_spells(documents, true_spellings)

    # word_list contains all the first element - token - of each row, i.e., a list of all words
    word_list = [elmt[0] for elmt in header_row_list_to_check]
    distinct_word_list = set(word_list)
    word_freq_dict = {i: word_list.count(i) for i in set(word_list)}
    # convert word_list to set to obtain a list of DISTINCT words
    # for each element in list_to_check, it is in this format:
    # word, NamedEntity, sentenceID, documentID, fileName

    logger.info(
        "Finished running Stanford CoreNLP to prepare data for folder "
        + str(folderID)
        + " and "
        + str(fileID)
        + " files."
    )
    logger.info(
        "   Processed "
        + str(len(header_row_list_to_check))
        + " words and "
        + str(len(distinct_word_list))
        + " DISTINCT words. Now computing spelling and word differences for DISTINCT words..."
    )
    # These headers reflect the items returned from the processing above
    # THEIR ORDER CANNOT BE CHANGED, UNLESS ABOVE ORDER OF PROCESSING IS ALSO CHANGED
    # These headers are then used selectively for the output (see headers2)
    headers1 = [
        "Words",
        "Word frequency in document",
        "Sentence ID",
        "Document ID",
        "Sentence",
        "Document",
        "Document path",
        "Named Entity (NER)",
        "Similar word in directory",
        "Similar-word frequency in directory",
        "Typo?",
        "Corrected Word",
        "Spell Status",
        "Similar Words in Dictionary",
    ]
    # Angel: header_row_list_to_check are list of all rows with token and meta-data information
    header_row_list_final = []  # Angel: header_row_list_final are list of all rows that appear in final output
    processed_word_list = []  # keeps track of words processed before
    if by_all_tokens_var:
        # headers 2 rearranges the headers but must have the same values
        headers2 = [
            "Words",
            "Word frequency in document",
            "Similar word in directory",
            "Similar-word frequency in directory",
            "Typo?",
            "Number of documents processed",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
            "Document path",
            "Processed directory",
            "Corrected Word",
            "Spell Status",
            "Similar Words in Dictionary",
        ]
        headers2.extend(["Corrected Word", "Spell Status"])
        header_rowID = 0
        processed_wordID = 0
        word_index = headers1.index("Words")
        sentence_index = headers1.index("Sentence")
        document_index = headers1.index("Document")
        speller = SpellChecker()
        for header_row in header_row_list_to_check:
            header_rowID += 1
            word = header_row[word_index]
            sentence = header_row[sentence_index]
            document = header_row[document_index]
            header_row.insert(1, word_freq_dict.get(word))
            checker_against = all_header_rows_dict
            if (len(word) > 3) and (word not in processed_word_list) and (word.isalpha()):
                processed_wordID = processed_wordID + 1
                corrected_word, spell_status, similar_words = check_spell(
                    word, sentence, processed_words, speller, true_spellings
                )
                header_row.append(corrected_word)
                header_row.append(spell_status)
                speller = SpellChecker()
                respelled_word = speller.correction(word)
                logger.info(
                    "      Processing DISTINCT word "
                    + str(processed_wordID)
                    + "/"
                    + str(len(distinct_word_list))
                    + ": "
                    + word
                )
                if similar_words:
                    header_row.append(", ".join([f"{w}({s})" for w, s in similar_words]))
                else:
                    header_row.append("")
                if respelled_word != word:
                    # should check edit distance only if the word is misspelled
                    value_tuple = fuzzywuzzy_check_dist(word, checker_against, similarity_value)  # Angel
                    if value_tuple[0]:  # a close match been found
                        header_row.append(value_tuple[1])  # returned similar word from check_edit_list
                        header_row.append(value_tuple[2])  # returned similar word frequency from check_edit_list
                        header_row.append("Typo?")
                        header_row_list_final.append(header_row)
                if spell_status in ["Potential typo", "Potential new spell"]:
                    value_tuple = fuzzywuzzy_check_dist(word, checker_against, similarity_value)
                    if value_tuple[0]:  # a close match been found
                        header_row.append(value_tuple[1:])  # returned similar word from check_edit_list
                        header_row.append("Typo?")
                        header_row_list_final.append(header_row)
            if word not in processed_word_list:
                processed_word_list.append(word)

    # Processing by NER tag
    else:
        # headers 2 rearranges the headers but must have the same values
        # it includes the NER tag
        headers2 = [
            "Words",
            "Named Entity (NER)",
            "Word frequency in document",
            "Similar word in directory",
            "Similar-word frequency in directory",
            "Typo?",
            "Number of documents processed",
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
            "Document path",
            "Processed directory",
            "Corrected Word",
            "Spell Status",
            "Similar Words in Dictionary",
        ]
        for header_row in header_row_list_to_check:
            word = header_row[0]
            speller = SpellChecker()  # Angel
            respelled_word = speller.correction(word)  # Angel
            if word not in processed_word_list and respelled_word != word:  # Angel
                header_row.insert(1, word_freq_dict.get(word))
                # [('word', Count:int)]
                for each_ner in NERs:
                    if header_row[-1] == each_ner:
                        checker_against = ner_dict.get(each_ner)
                        value_tuple = fuzzywuzzy_check_dist(word[0], checker_against, similarity_value)  # Angel
                        if value_tuple[0]:
                            header_row.append(value_tuple[1])  # returned similar word from check_edit_list
                            header_row.append(value_tuple[2])  # returned similar word frequency from check_edit_list
                            header_row.append("Typo?")
                            header_row_list_final.append(header_row)  # Angel
                    # else:#Angel
                processed_word_list.append(word)  # Angel
    correct_spells, potential_new_spells, potential_typos, unused_spells = analyze_processed_words(
        processed_words, true_spellings
    )
    analysis_file = write_additional_analysis(
        correct_spells,
        potential_new_spells,
        potential_typos,
        unused_spells,
        outputDir,
        true_spellings,
    )
    filesToOpen.append(analysis_file)
    df = pd.DataFrame(header_row_list_final, columns=headers1)
    df["Number of documents processed"] = None  # Add this line to initialize the column
    for index, row in df.iterrows():
        if row["Similar-word frequency in directory"] is not None:
            tmp = df[df["Words"] == row["Similar word in directory"]]
            df.loc[index, "Number of documents processed"] = tmp.Document.nunique()  # count number of distinct elements
    df["Processed directory"] = IO_csv_util.dressFilenameForCSVHyperlink(inputDir)
    df = df[headers2]

    # complete includes all repeats
    df_complete = df[headers2]

    # simple excludes all repeats
    df_simple = df.drop_duplicates(subset=["Words", "Document ID"], keep="last")

    if by_all_tokens_var:
        outputFileName_complete = IO_files_util.generate_output_file_name(
            "",
            inputDir,
            outputDir,
            ".csv",
            "WordSimil",
            str(similarity_value),
            "Edit_dist_algo",
            "header_rows",
            "Full-table",
        )
        outputFileName_simple = IO_files_util.generate_output_file_name(
            "",
            inputDir,
            outputDir,
            ".csv",
            "WordSimil",
            str(similarity_value),
            "Edit_dist_algo",
            "header_rows",
            "Concise-table",
        )
    else:
        outputFileName_complete = IO_files_util.generate_output_file_name(
            "",
            inputDir,
            outputDir,
            ".csv",
            "WordSimil",
            str(similarity_value),
            "Edit_dist_algo",
            "NERs",
            "Full-table",
        )
        outputFileName_simple = IO_files_util.generate_output_file_name(
            "",
            inputDir,
            outputDir,
            ".csv",
            "WordSimil",
            str(similarity_value),
            "Edit_dist_algo",
            "NERs",
            "Concise-table",
        )
    if len(df_simple) > 0 and len(df_complete) > 0:
        df_simple.to_csv(outputFileName_simple, encoding="utf-8", index=False)
        df_complete.to_csv(outputFileName_complete, encoding="utf-8", index=False)
        filesToOpen.append(outputFileName_simple)
        filesToOpen.append(outputFileName_complete)

        filesToOpen.append(outputFileName_simple)
        filesToOpen.append(outputFileName_complete)

        # IO_user_interface_util.timed_alert(3000, 'Word similarity end',
        #                                    'Finished running Word similarity at', True, '', True, startTime, True)

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFileName_simple,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Typo?"],
            chart_title="Frequency of Potential Typos",
            count_var=1,  # 1 for alphabetic fields that need to be coounted;  1 for numeric fields (e.g., frequencies, scorers)
            hover_label=[],
            outputFileNameType="Leven_spell",
            column_xAxis_label="Typo",
            groupByList=[],
            plotList=[],
            chart_title_label="",
        )
        if outputFiles is not None:
            collect(filesToOpen, outputFiles)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(openOutputFiles, filesToOpen, outputDir)
        filesToOpen = []  # empty the list to avoid opening files twice

    p.kill()

    return filesToOpen


def spelling_checker_cleaner(window, inputFilename, inputDir, outputDir, openOutputFiles, configFileName):
    logger.info(
        "Find & Replace csv file (with 'Original' and 'Corrected' headers) Please, select the csv file that contains the information about words that need correcting.\n\nMostly likely this file was created by the spell checker algorithms and edited by you keeping only correct entries.\n\nThe Find & Replace will expect 2 column headers 'Original' and 'Corrected'.\n\nPlease, make sure that your csv file has those characteristics."
    )

    csv_spelling_file = ""
    if csv_spelling_file == "":
        return
    df = pd.read_csv(csv_spelling_file, encoding="utf-8", on_bad_lines="skip")
    try:  # make sure the csv have two columns of "original" and "corrected"
        original = df["Original"]
        corrected = df["Corrected"]
    except Exception:
        logger.info(
            "CSV file error, The selected csv file does not have the expected format. The Find & Replace expects 2 column headers 'Original' and 'Corrected'.\n\nPlease, make sure that your csv file has those characteristics and try again. "
        )

        logger.info(
            "The selected csv file does not have the expected format. The Find & Replace expects 2 column headers 'Original' and 'Corrected'.\n\nPlease, make sure that your csv file has those characteristics and try again."
        )
        return
    # preparting the input to the cleaning function: lists of words to replace
    input_original = []
    input_corrected = []
    for i in range(len(original)):
        # the correction can be empty string or NaN,
        #   then both original and corrected will be added to the input lists
        # if (isinstance(corrected[i], str) and corrected[i] != '') or (not math.isnan(corrected[i])):
        if isinstance(corrected[i], str) or (math.isnan(corrected[i])):
            input_original.append(original[i])
            if math.isnan(corrected[i]):
                corrected[i] = ""
            input_corrected.append(corrected[i])
    file_cleaner_util.find_replace_string(
        window,
        inputFilename,
        inputDir,
        outputDir,
        configFileName,
        openOutputFiles,
        input_original,
        input_corrected,
    )


def spellchecking_autocorrect(text: str, inputFilename) -> (str, DataFrame):
    # startTime=IO_user_interface_util.timed_alert(3000, 'Autocorrect spelling checker start',
    #                                    'Started running AUTOCORRECT spelling checker on ' + inputFilename + ' at ',
    #                                     True, '', True, '', True)
    original_str_list = []
    new_str_list = []
    speller = Speller()
    # for word in nltk.word_tokenize(text):
    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text

    for word in tokenize_stanza_text(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = speller(word)
            if respelled_word != word:
                new_str_list.append(respelled_word)
            else:
                new_str_list.append("")
    return speller(text), DataFrame({"Original": original_str_list, "Corrected": new_str_list})


# the library has an indexer problem
# if checkIO_Filename_inputDir ("Spelling checker (via SpellChecker)",inputFilename, "NO input directory required", 'txt'):
#     if len(misspelledWordsList)>0:
# https://www.tutorialspoint.com/python_text_processing/python_spelling_check.htm
# def spellingChecker(window,inputFilename,outputFilename):
#     # SHOULD HAVE THIS FORMAT
#     # string.punctuation doesn't include non-English punctuation at all
#     # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
#     # misspelled contains the list of misspelled words
#     for word in misspelled:
#         # Get the one `most likely` answer
#         # Get a list of `likely` options


def spellchecking_pyspellchecker(text: str, inputFilename) -> (str, DataFrame):
    # startTime=IO_user_interface_util.timed_alert('Pyspellchecker spelling checker start',
    #                                    'Started running PYSPELLCHECKER spelling checker on ' + inputFilename + ' at',
    #                                              True, '', True, '', True)

    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text

    # :: pyspellchecker seems to remove punctuations.
    new_str_list = []
    original_str_list = []
    new_str_list_for_df = []
    treebank = nltk.tokenize.treebank.TreebankWordDetokenizer()
    speller = SpellChecker()
    # for word in nltk.word_tokenize(text):
    for word in tokenize_stanza_text(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = speller.correction(word)
            if respelled_word != word:
                new_str_list_for_df.append(respelled_word)
            else:
                new_str_list_for_df.append("")
        new_str_list.append(word)
    return treebank.detokenize(new_str_list), DataFrame(
        {"Original": original_str_list, "Corrected": new_str_list_for_df}
    )


def spellchecking_text_blob(text: str, inputFilename) -> (str, DataFrame):
    # startTime=IO_user_interface_util.timed_alert('Textblob spelling checker start',
    #                                    'Started running TEXTBLOB spelling checker on ' + inputFilename + ' at',
    #                                              True, '', True, '', True)
    new_str_list = []
    new_str_list_for_df = []
    original_str_list = []
    treebank = nltk.tokenize.treebank.TreebankWordDetokenizer()
    # for word in nltk.word_tokenize(text):
    from Stanza_functions_util import stanzaPipeLine, tokenize_stanza_text

    for word in tokenize_stanza_text(stanzaPipeLine(text)):
        if word.isalnum():
            original_str_list.append(word)
            respelled_word = Word(word).spellcheck()[0][0]
            if respelled_word != word:
                new_str_list_for_df.append(respelled_word)
            else:
                new_str_list_for_df.append("")
        new_str_list.append(word)
    return treebank.detokenize(new_str_list), DataFrame(
        {"Original": original_str_list, "Corrected": new_str_list_for_df}
    )


# not used
# def spellchecking_pytesseract(inputDir,outputDir):
#     if misspelled == set():
#         for misspell in misspelled:
#             # Get the one `most likely` answer

# not used
# def spell_word_pytesseract(word, spell):
#     if misspelled == set():
#         for misspell in misspelled:
#             # Get the one `most likely` answer
#
#     if spelling_checker_var:
#         if 'autocorrect' in checker_package:
#         header_rows = [[token, sentence_number + 1, document_number + 1, sentence, document[1],IO_csv_util.dressFilenameForCSVHyperlink(document[2]) ,''] for document_number, document in
#                      for sentence_number, sentence in enumerate(document[0])
#                      for token in NLP.word_tokenize(sentence)]
#
#         for word in list_to_check:
#             if 'pyspellchecker' in checker_package:
#             if value_tuple[0]:


def spellcheck(inputFilename, inputDir, checker_value_var, check_withinDir):
    folderID = 0
    fileID = 0

    autocorrect_df = pd.DataFrame({"Original": [], "Corrected": [], "Document ID": [], "Document": []})

    pyspellchecker_df = autocorrect_df.copy()
    textblob_df = autocorrect_df.copy()

    corrected_files_dir = os.path.join(inputDir, "spell_checked")
    make_directory(corrected_files_dir)

    if check_withinDir:
        files = IO_files_util.getFileList(inputFilename, inputDir, ".txt")
    else:
        files = IO_files_util.getFileList_SubDir(inputFilename, inputDir, ".txt")
    if len(files) == 0:
        return
    folderID += 1

    # if not check_withinDir:
    #     for folder, subs, files in os.walk(inputDir):
    #         print("\nProcessing folder " + str(folderID) + "/ " + os.path.basename(
    #              os.path.normpath(folder)))

    for filename in files:
        if check_withinDir:
            logger.info("Processing file: %s", filename)
        fileID = fileID + 1
        # with open(inputFilenames_path, 'r', encoding='utf-8', errors='ignore') as opened_file:
        with open(filename, encoding="utf-8", errors="ignore") as opened_file:
            logger.info("  Processing file: %s", filename)
            originalText = opened_file.read()
            os.path.join(inputDir, filename)
            if checker_value_var == "*" or "autocorrect" in checker_value_var:
                text, csv = spellchecking_autocorrect(originalText, filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                autocorrect_df = pandas.concat([autocorrect_df, csv], ignore_index=True)
                autocorrect_df = autocorrect_df.drop_duplicates()
                logger.info("AUTOCORRECT\n %s", text)

            if checker_value_var == "*" or "pyspellchecker" in checker_value_var:
                text, csv = spellchecking_pyspellchecker(originalText, filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                pyspellchecker_df = pandas.concat([pyspellchecker_df, csv], ignore_index=True)
                pyspellchecker_df = pyspellchecker_df.drop_duplicates()
                logger.info("PYSPELLCHECKER\n %s", text)

            if checker_value_var == "*" or "textblob" in checker_value_var:
                text, csv = spellchecking_text_blob(originalText, filename)
                csv["Document"] = [IO_csv_util.dressFilenameForCSVHyperlink(filename)] * csv.shape[0]
                csv["Document ID"] = [fileID] * csv.shape[0]
                textblob_df = pandas.concat([textblob_df, csv], ignore_index=True)
                textblob_df = textblob_df.drop_duplicates()
                logger.info("TEXTBLOB\n %s", text)

            head, tail = os.path.split(filename)
            # head is path, tail is filename

            corrected_files_path = os.path.join(corrected_files_dir, tail)
            with open(corrected_files_path, "w+", encoding="utf-8") as file_to_write:
                file_to_write.write(text)

    IO_user_interface_util.subdirectory_file_output_save(inputDir, corrected_files_path, "INPUT", "spell checker")

    logger.info(
        "Spell checking, Spell checker algorithms are not very accurate, perhaps pyspellchecker perfoming better than autocorrect and textblob performing the worse.\n\nThe spell checkers generate in output\n  1. corrected txt file(s) in a subdirectory 'spell_checked' of the input file and/or input directory;\n  2. csv files (one for each of the 3 available algorithms if run together) with the headers 'Original' and 'Corrected' that list all the words that would have been edited for misspellings in the output files.\n\nPLEASE, CAREFULLY INSPECT THE OUTPUT CSV FILE(S), DELETE ANY WRONGLY CORRECTED WORDS FROM EACH CELL UNDER THE 'Corrected' COLUMN, THEN, RUN THE 'Find & Replace string (Spelling checker cleaner)' SCRIPT TO EDIT THE ORIGINAL INPUT FILE(S). "
    )

    return autocorrect_df, pyspellchecker_df, textblob_df


# function implements three different approaches to language detection: langdetect, spacy, langid
# https://towardsdatascience.com/benchmarking-language-detection-for-nlp-8250ea8b67c
# TODO print all languages and their probabilities in a csv file, with Language, Probability, Document ID, Document (with hyperlink)


def language_detection(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    openOutputFiles,
    chartPackage,
    dataTransformation,
):

    fileID = 0
    filesToOpen = []

    outputFilenameCSV = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "lang_detect"
    )
    filesToOpen.append(outputFilenameCSV)

    files = IO_files_util.getFileList(inputFilename, inputDir, ".txt", silent=False, configFileName=configFileName)
    if len(files) == 0:
        return

    if IO_csv_util.openCSVOutputFile(outputFilenameCSV):
        return

    fieldnames = [
        "NLP Language Package",
        "Language",
        "Probability",
        "Document ID",
        "Document",
    ]

    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(
        scriptName,
        reminders_util.title_options_language_detection,
        reminders_util.message_language_detection,
        True,
    )

    # startTime=IO_user_interface_util.timed_alert('Analysis start',
    #                                    'Started running language detection algorithms at',
    #                                              True, '', True, '', True)

    # Stanza's multilingual pipeline needs to load only once, therefore called outside the for-loop
    from stanza.pipeline.multilingual import MultilingualPipeline

    try:
        nlp_stanza = MultilingualPipeline()
    except Exception:
        stanza.download(lang="multilingual", verbose=False)
        nlp_stanza = MultilingualPipeline()

    lang_dict = dict(constants_util.languages)

    with open(outputFilenameCSV, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        docErrors_empty = 0
        docErrors_unknown = 0
        filenameSV = ""
        for filename in files:
            fileID = fileID + 1
            head, tail = os.path.split(filename)
            logger.info("Processing file " + str(fileID) + "/" + str(len(files)) + " " + tail)
            text = open(filename, encoding="utf-8", errors="ignore").read()
            if len(text) == 0:
                logger.info("  The file is empty. It will be discarded from processing.")
                docErrors_empty = docErrors_empty + 1
                continue
            # split text into paragraphs, paragraph = text.split('\n\n')
            # loop through paragraphs passing each para to detect_lang

            # head is path, tail is filename
            try:
                value = detect_langs(text)
            except Exception:
                filenameSV = (
                    filename  # do not count the same document twice in this and the other algorithms that follow
                )
                docErrors_unknown = docErrors_unknown + 1
                logger.info("  Unknown file read error.")
                continue

            # LANGDETECT ----------------------------------------------------------

            value = str(value[0]).split(":")
            # TODO MINO get the value from the list in constants_util
            language = value[0]
            language = lang_dict.get(language)
            probability = round(float(value[1]), 2)
            # https://pypi.org/project/langdetect/
            # langdetect supports 55 languages out of the box (ISO 639-1 codes)
            # af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
            # hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
            # pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
            # ISO codes https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
            logger.info("   LANGDETECT %s %s", language, probability)
            currentLine = [
                [
                    "LANGDETECT",
                    language,
                    probability,
                    fileID,
                    IO_csv_util.dressFilenameForCSVHyperlink(filename),
                ]
            ]

            # LANGID ----------------------------------------------------------

            language = value[0]
            language = lang_dict.get(language)
            probability = round(float(value[1]), 2)
            # LANGID ``langid.py`` comes pre-trained on 97 languages (ISO 639-1 codes given)
            # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes for ISO codes
            # https://pypi.org/project/langid/1.1.5/
            # af, am, an, ar, as, az, be, bg, bn, br,
            # bs, ca, cs, cy, da, de, dz, el, en, eo,
            # es, et, eu, fa, fi, fo, fr, ga, gl, gu,
            # he, hi, hr, ht, hu, hy, id, is, it, ja,
            # jv, ka, kk, km, kn, ko, ku, ky, la, lb,
            # lo, lt, lv, mg, mk, ml, mn, mr, ms, mt,
            # nb, ne, nl, nn, no, oc, or, pa, pl, ps,
            # pt, qu, ro, ru, rw, se, si, sk, sl, sq,
            # sr, sv, sw, ta, te, th, tl, tr, ug, uk,
            # ur, vi, vo, wa, xh, zh, zu
            logger.info("   LANGID %s %s", language, probability)  # ('en', 0.999999999999998)
            currentLine.append(
                [
                    "LANGID",
                    language,
                    probability,
                    fileID,
                    IO_csv_util.dressFilenameForCSVHyperlink(filename),
                ]
            )

            # spaCY ----------------------------------------------------------
            nlp_spacy = get_spacy_model("en_core_web_sm")
            if "language_detector" not in nlp_spacy.pipe_names:
                Language.factory("language_detector", func=get_lang_detector)
                nlp_spacy.add_pipe("language_detector", last=True)
            try:
                doc = nlp_spacy(text)
            except Exception:
                if (
                    filename != filenameSV
                ):  # do not count the same document twice in this and the other algorithm that follows
                    docErrors_unknown = docErrors_unknown + 1
                    filenameSV = filename
                logger.info("  spaCy Unknown file read error.")
                break  # continue
            value = doc._.language
            language = value["language"]
            language = lang_dict.get(language)
            probability = round(float(value["score"]), 2)
            #
            logger.info("   SPACY %s %s", language, probability)  # {'language': 'en', 'score': 0.9999978351575265}
            currentLine.append(
                [
                    "spaCy",
                    language,
                    probability,
                    fileID,
                    IO_csv_util.dressFilenameForCSVHyperlink(filename),
                ]
            )

            lang_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            try:
                value = lang_identifier.classify(text)
            except Exception:
                if filename != filenameSV:
                    docErrors_unknown = docErrors_unknown + 1
                    filenameSV = filename
                logger.info("  spaCy Unknown file read error.")
                break  # continue

            # Stanza  ----------------------------------------------------------

            doc = nlp_stanza(text)
            language = doc.lang
            language = lang_dict.get(language)
            probability = float(1)
            logger.info("   Stanza %s %s", language, probability)
            currentLine.append(
                [
                    "Stanza",
                    language,
                    probability,
                    fileID,
                    IO_csv_util.dressFilenameForCSVHyperlink(filename),
                ]
            )

            writer = csv.writer(csvfile)
            writer.writerows(currentLine)
            filenameSV = filename
    csvfile.close()
    msg = ""
    if docErrors_empty == 0 and docErrors_unknown == 0:
        msg = str(fileID) + " documents successfully processed for language detection."
    else:
        if docErrors_empty > 0:
            msg = (
                str(fileID)
                + " documents processed for language detection.\n  "
                + str(docErrors_empty)
                + " document(s) found empty."
            )
        if docErrors_unknown > 0:
            if msg != "":
                msg = msg + "\n  " + str(docErrors_unknown) + " document(s) read with unknown errors."
            else:
                msg = (
                    str(fileID)
                    + " documents processed for language detection.\n  "
                    + str(docErrors_unknown)
                    + " document(s) read with unknown errors."
                )

        logger.info(
            "File read errors,"
            + "msg+ '\n\nFaulty files are listed in command line/terminal. Please, search for 'File read error' and inspect each file carefully."
        )

    filesToOpen.append(outputFilenameCSV)
    # IO_user_interface_util.timed_alert(1000, 'Analysis end',
    #                                    'Finished running Language Detection at', True,'Languages detected are exported via the ISO 639 two-letter code. ISO 639 is a standardized nomenclature used to classify languages. Check the ISO list at https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.', True, startTime, True)
    logger.info(
        "Languages detected are exported via the ISO 639 two-letter code. ISO 639 is a standardized nomenclature used to classify languages. Check the ISO list at https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes."
    )
    if chartPackage != "No charts":
        columns_to_be_plotted_yAxis = [[1, 1]]
        chart_title = "Frequency of Languages Detected by LANGDETECT, LANGID, spaCy, and Stanza"
        hover_label = []
        inputFilename = outputFilenameCSV
        outputFiles = charts_util.run_all(
            columns_to_be_plotted_yAxis,
            inputFilename,
            outputDir,
            outputFileLabel="_bar_chart",
            chartPackage=chartPackage,
            dataTransformation=dataTransformation,
            chart_type_list=["bar"],
            chart_title=chart_title,
            column_xAxis_label_var="Language",
            hover_info_column_list=hover_label,
            count_var=1,
        )
        if chartPackage == "Excel" and outputFiles is not None:
            collect(filesToOpen, outputFiles)

    # if openOutputFiles:
    return filesToOpen


def get_lang_detector(nlp, name):
    return LanguageDetector()
