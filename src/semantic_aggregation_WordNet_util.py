#Written by Roberto Franzosi
#Modified by Cynthia Dong (Fall 2019-Spring 2020)
#Wordnet_bySentenceID written by Yi Wang (April 2020)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"WordNet",['os','csv','tkinter','nltk','pandas'])==False:
    sys.exit(0)

import os
import re
import pandas as pd
import csv
import tkinter.messagebox as mb
from collections import defaultdict

import reminders_util
import charts_util
import IO_files_util
import IO_user_interface_util
import data_manipulation_util
import IO_csv_util
import statistics_csv_util

IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/wordnet', 'wordnet')
from nltk.corpus import wordnet as wn

filesToOpen=[]

NOUN_TOP_SYNSETS = {
    'act', 'animal', 'artifact', 'attribute', 'body', 'cognition',
    'communication', 'event', 'feeling', 'food', 'group', 'location',
    'motive', 'object', 'person', 'phenomenon', 'plant', 'possession',
    'process', 'quantity', 'relation', 'shape', 'state', 'substance', 'time'
}

VERB_TOP_SYNSETS = {
    'body', 'change', 'cognition', 'communication', 'competition',
    'consumption', 'contact', 'creation', 'emotion', 'motion',
    'perception', 'possession', 'social', 'stative', 'weather'
}


def _get_wn_pos(noun_verb):
    return wn.VERB if noun_verb == 'VERB' else wn.NOUN


def _get_all_hyponyms(synset):
    result = []
    queue = [synset]
    seen = set()
    while queue:
        s = queue.pop(0)
        if s in seen:
            continue
        seen.add(s)
        for lemma in s.lemmas():
            result.append((lemma.name().replace('_', ' '), s))
        queue.extend(s.hyponyms())
    return result


def _climb_to_top(synset, top_synsets):
    visited = set()
    queue = [([synset.name()], synset)]
    while queue:
        path, current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        lexname = current.lexname().split('.')[-1] if '.' in current.lexname() else current.lexname()
        if lexname in top_synsets:
            return lexname, path
        for parent in current.hypernyms():
            queue.append((path + [parent.name()], parent))
    return 'unknown', [synset.name()]


def _resolve_anchor_synsets(anchor_terms, pos):
    """Resolve user anchor terms to a set of WordNet synsets to aggregate UP toward. Each term may be
    a word/phrase ('person', 'ethnic group') or an explicit synset name ('person.n.01'). Words use
    the first (most frequent) sense. Returns (anchors_set, unresolved_list)."""
    anchors = set()
    unresolved = []
    for term in anchor_terms:
        term = str(term).strip()
        if not term:
            continue
        key = term.replace(' ', '_')
        if re.match(r'^[\w\-]+\.[a-z]\.\d+$', key):     # explicit synset name, e.g. person.n.01
            try:
                anchors.add(wn.synset(key))
                continue
            except Exception:
                unresolved.append(term)
                continue
        syns = wn.synsets(key, pos=pos)
        if syns:
            anchors.add(syns[0])                        # first (most frequent) sense
        else:
            unresolved.append(term)
    return anchors, unresolved


def _climb_to_target(synset, target_synsets, top_synsets):
    """Climb hypernyms until an ancestor IS one of the user's anchor synsets; return (anchor_label,
    path) for the NEAREST (most specific) matching anchor. If no anchor is an ancestor, fall back to
    the top-level supersense so the word still gets a category, prefixed '(other) '."""
    visited = set()
    queue = [([synset.name()], synset)]
    while queue:
        path, current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        if current in target_synsets:
            return current.lemmas()[0].name().replace('_', ' '), path
        for parent in current.hypernyms():
            queue.append((path + [parent.name()], parent))
    category, path = _climb_to_top(synset, top_synsets)
    return '(other) ' + category, path


def disaggregate_GoingDOWN(WordNetDir, outputDir, wordNet_keyword_list, noun_verb):
    filesToOpen = []
    pos = _get_wn_pos(noun_verb)

    if len(wordNet_keyword_list) > 1:
        fileName = wordNet_keyword_list[0] + "-plus-list"
    else:
        fileName = wordNet_keyword_list[0] + "-list"

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start',
        'Started running WordNet (Zoom IN/DOWN) at', True,
        'Running WordNet with the ' + noun_verb + ' option with following keywords:\n\n' + str(wordNet_keyword_list))

    simple_file = os.path.join(outputDir, "NLP_WordNet_DOWN_" + fileName + ".csv")
    verbose_file = os.path.join(outputDir, "NLP_WordNet_DOWN_" + fileName + "-verbose.csv")

    all_terms = []
    not_found = []

    for keyword in wordNet_keyword_list:
        synsets = wn.synsets(keyword, pos=pos)
        if not synsets:
            not_found.append(keyword)
            continue
        synset = synsets[0]
        hyponyms = _get_all_hyponyms(synset)
        for term, syn in hyponyms:
            definition = syn.definition()
            examples = '; '.join(syn.examples()) if syn.examples() else ''
            freq = sum(l.count() for l in syn.lemmas())
            all_terms.append({
                'Term': term,
                'WordNet Category': keyword,
                'Definition': definition,
                'Frequency': freq,
                'Examples': examples
            })

    if len(all_terms) == 0:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Warning',
            'WordNet did not find any of the synset(s) in your search list:\n' + str(wordNet_keyword_list) +
            '\nin the WordNet lexical database for ' + noun_verb + '.\n\nPlease, check your synset list and try again.')
        return filesToOpen

    if not_found:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Warning',
            'WordNet did not find some of the synset(s) in your search list:\n' + str(not_found) +
            '\nin the WordNet lexical database for ' + noun_verb + '.')

    with open(simple_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Term', 'WordNet Category'])
        writer.writeheader()
        for row in all_terms:
            writer.writerow({'Term': row['Term'], 'WordNet Category': row['WordNet Category']})

    with open(verbose_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Term', 'WordNet Category', 'Definition', 'Frequency', 'Examples'])
        writer.writeheader()
        writer.writerows(all_terms)

    filesToOpen.append(simple_file)
    filesToOpen.append(verbose_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
        'Finished running WordNet (Zoom IN/DOWN) at', True, '', True, startTime)
    return filesToOpen


def aggregate_GoingUP(WordNetDir, inputFile, outputDir, config_filename, noun_verb, openOutputFiles, chartPackage, dataTransformation, language_var='', target_terms=None):
    filesToOpen = []

    head, scriptName = os.path.split(os.path.basename(__file__))
    if language_var == '' or language_var != 'English':
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_English_language_WordNet,
            reminders_util.message_English_language_WordNet,
            True)
        return filesToOpen
    if noun_verb == 'VERB':
        reminders_util.checkReminder(
            scriptName,
            reminders_util.title_options_WordNet_verb_aggregation,
            reminders_util.message_WordNet_verb_aggregation,
            True)

    pos = _get_wn_pos(noun_verb)
    top_synsets = VERB_TOP_SYNSETS if noun_verb == 'VERB' else NOUN_TOP_SYNSETS

    # Optional lower-level aggregation: if the user supplied anchor synsets (the 'YOUR synset(s)' /
    # 'Top-level synset' field), aggregate UP to the NEAREST of those (e.g. person vs artifact for
    # 'violence against people vs things') instead of the fixed top-level supersenses.
    anchors = set()
    if target_terms:
        anchors, unresolved = _resolve_anchor_synsets(target_terms, pos)
        if unresolved:
            mb.showwarning(title='WordNet anchor synset(s) not found',
                message="These anchor synset(s) were not found in WordNet for " + noun_verb +
                        " and will be ignored:\n\n" + ", ".join(unresolved))
        if anchors:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'WordNet aggregation level',
                "Aggregating UP to your " + str(len(anchors)) + " anchor synset(s):\n\n" +
                ", ".join(sorted(a.name() for a in anchors)) +
                "\n\ninstead of the top-level supersenses. Words not under any anchor are labelled "
                "'(other) ...'.", False, '', True)

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Analysis start',
        'Started running WordNet (Zoom OUT/UP) with the ' + noun_verb + ' option at', True, '', True, '', True)

    data = pd.read_csv(inputFile, encoding='utf-8', on_bad_lines='skip')
    words = data.iloc[:, 0].dropna().unique().tolist()

    fileName = os.path.basename(inputFile).split(".")[0]
    outputFilenameCSV1 = os.path.join(outputDir, "NLP_WordNet_UP_" + noun_verb + "_" + fileName + ".csv")
    outputFilenameCSV2 = os.path.join(outputDir, "NLP_WordNet_UP_" + noun_verb + "_" + fileName + "_frequency.csv")

    rows = []
    not_found_count = 0
    category_counts = defaultdict(int)

    for word in words:
        word_clean = str(word).strip().lower()
        synsets = wn.synsets(word_clean, pos=pos)
        if not synsets:
            not_found_count += 1
            rows.append({'Word': word_clean, 'WordNet Category': 'Not found',
                         'Intermediate synset 1': ''})
            continue
        synset = synsets[0]
        if anchors:
            category, path = _climb_to_target(synset, anchors, top_synsets)
        else:
            category, path = _climb_to_top(synset, top_synsets)
        category_counts[category] += 1
        intermediate_dict = {'Word': word_clean, 'WordNet Category': category}
        for idx, step in enumerate(path):
            intermediate_dict['Intermediate synset ' + str(idx + 1)] = step
        rows.append(intermediate_dict)

    if len(rows) == 0 or all(r['WordNet Category'] == 'Not found' for r in rows):
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
            "WordNet " + noun_verb + " aggregation.\n\nWordNet cannot find any word in the input csv file \n" +
            inputFile + "\nfor " + noun_verb + ".")
        return filesToOpen

    if not_found_count > 0:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
            "WordNet " + noun_verb + " aggregation.\n\nSome words in the list to be aggregated do not exist in WordNet for " +
            noun_verb + ".\n\n" + str(not_found_count) + " word(s) not found.")

    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    intermediate_cols = sorted([k for k in all_keys if k.startswith('Intermediate synset')],
                                key=lambda x: int(x.split()[-1]))
    fieldnames = ['Word', 'WordNet Category'] + intermediate_cols

    with open(outputFilenameCSV1, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    with open(outputFilenameCSV2, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['WordNet Category', 'Frequency'])
        writer.writeheader()
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            writer.writerow({'WordNet Category': cat, 'Frequency': count})

    filesToOpen.append(outputFilenameCSV1)
    filesToOpen.append(outputFilenameCSV2)

    outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilenameCSV1, outputDir,
                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['WordNet Category'],
                                               chart_title='Frequency of WordNet Aggregate Categories for ' + noun_verb,
                                               count_var=1,
                                               hover_label=[],
                                               outputFileNameType='',
                                               column_xAxis_label='WordNet ' + noun_verb + ' category',
                                               groupByList=[],
                                               plotList=[],
                                               chart_title_label='')
    if outputFiles is not None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    if noun_verb == 'VERB':
        operation_results_text_list = []
        operation_results_text_list.append(str(outputFilenameCSV1) + ',Word,<>,be,and')
        operation_results_text_list.append(str(outputFilenameCSV1) + ',Word,<>,have,and')
        outputFilenameCSV3_new = data_manipulation_util.export_csv_to_csv_txt(outputDir, operation_results_text_list, '.csv', [0, 1])

        outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, outputFilenameCSV3_new,
                                                   outputDir,
                                                   columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['WordNet Category'],
                                                   chart_title='Frequency of WordNet Aggregate Categories for ' + noun_verb + ' (No Auxiliaries)',
                                                   count_var=1,
                                                   hover_label=[],
                                                   outputFileNameType='',
                                                   column_xAxis_label='WordNet ' + noun_verb + ' category',
                                                   groupByList=[],
                                                   plotList=[],
                                                   chart_title_label='')
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        if outputFilenameCSV3_new != "":
            os.remove(outputFilenameCSV3_new)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
        'Finished running WordNet (Zoom OUT/UP) at', True, '', True, startTime, True)

    return filesToOpen

# written by Yi Wang April 2020
# ConnlTable is the inputFilename
# TODO TONY do we need this now? Don't we have more general ways of dealing with this?
def Wordnet_bySentenceID(ConnlTable, wordnetDict, outputFilename, outputDir, noun_verb, openOutputFiles,
                         chartPackage, dataTransformation):
    filesToOpen = []
    startTime = IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                                   'Started running WordNet charts by sentence index at',
                                                   True, '', True, '', False)

    if noun_verb == 'NOUN':
        checklist = ['NN', 'NNP', 'NNPS', 'NNS']
    else:
        checklist = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    # read in the CoreNLP CoNLL table
    connl = pd.read_csv(ConnlTable,encoding='utf-8',on_bad_lines='skip')
    # read in the dictionary file to be used to filter CoNLL values
    # The file is expected to have 2 columns with headers: Word, WordNet Category
    try:
        wn_dict = pd.read_csv(wordnetDict,encoding='utf-8',on_bad_lines='skip')
    except:
        mb.showwarning("Warning",
                       "The file \n\n" + wordnetDict + "\n\ndoes not have the expected 2 columns: Word, WordNet Category. You may have selected the wrong input file.\n\nPlease, select the right input file and try again.")
        return
    # set up the double list conll from the conll data
    try:
        connl = connl[['Form', 'Lemma', 'POS', 'Sentence ID', 'Document ID', 'Document']]
    except:
        mb.showwarning("Warning",
                       "The file \n\n" + ConnlTable + "\n\ndoes not appear to be a CoNLL table with expected column names: Form,Lemma,POS, SentenceID, DocumentID, Document.\n\nPlease, select the right input file and try again.")
        return
    # filter the list by noun or verb
    connl = connl[connl['POS'].isin(checklist)]
    # eliminate any duplicate value in Word (Form))
    # Term is exported by the WordNet java script and cannot be modifiied
    wn_dict = wn_dict.drop_duplicates().rename(columns={'Term': 'Lemma', 'WordNet Category': 'Category'})
    connl = connl.merge(wn_dict, how='left', on='Lemma')
    # the CoNLL table value is not found in the dictionary Word value
    connl.fillna('Not in INPUT dictionary for ' + noun_verb, inplace=True)
    # add the WordNet category to the conll list
    connl = connl[['Form', 'Lemma', 'POS', 'Category', 'Sentence ID', 'Document ID', 'Document']]
    # put headers on conll list
    connl.columns = ['Form', 'Lemma', 'POS', 'Category', 'Sentence ID', 'Document ID', 'Document']

    Row_list = []
    # Iterate over each row
    for index, rows in connl.iterrows():
        # Create list for the current row
        my_list = [rows.Form, rows.Lemma, rows.POS, rows.Category, rows['Sentence ID'], rows['Document ID'], rows.Document]
        # append the list to the final list
        Row_list.append(my_list)
    for index, row in enumerate(Row_list):
        if index == 0 and Row_list[index][4] != 1:
            for i in range(Row_list[index][4] - 1, 0, -1):
                Row_list.insert(0, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
        else:
            if index < len(Row_list) - 1 and Row_list[index + 1][4] - Row_list[index][4] > 1:
                for i in range(Row_list[index + 1][4] - 1, Row_list[index][4], -1):
                    Row_list.insert(index + 1, ['', '', '', '', i, Row_list[index][5], Row_list[index][6]])
    df = pd.DataFrame(Row_list,
                      index=['Form', 'Lemma', 'POS', 'WordNet Category', 'Sentence ID', 'Document ID', 'Document'])
    outputFilename = charts_util.add_missing_IDs(df,outputFilename)

    if chartPackage!='No charts':
        outputFiles = statistics_csv_util.compute_csv_column_frequencies(GUI_util.window,
                                                                       ConnlTable,
                                                                       df,
                                                                       outputDir,
                                                                       openOutputFiles,
                                                                       
                                                                       chartPackage,
                                                                       dataTransformation,
                                                                       [[4, 5]],
                                                                       ['WordNet Category'], ['Form'],
                                                                       ['Sentence ID', 'Document ID', 'Document'],
                                                                       )
        if len(outputFiles) > 0:
            filesToOpen.extend(outputFiles)
    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end',
                                       'Finished running WordNet charts by sentence index at', True, '', True,
                                       startTime)

    return filesToOpen

# The output file returned by the JAVA script WordNet_Search_UP.jar contains
#   several intermediate synsets under the same column header Intermediate Synsets
#   causing problems to pandas
#   The list of Intermediate Synsets mustt be separated and ut under separate headings

def complete_csv_header(inputFilename, padding_base_name):
    max_length = 0
    new_header = []
    # find the longest row
    with open(inputFilename, newline='', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for row in reader:
            if max_length < len(row):
                max_length = len(row)
    with open(inputFilename, newline='', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        # only read the first line
        for row in reader:
            max_length = max_length - len(row)
            new_header = row
            for i in range(1, max_length+1):
                new_header.append(padding_base_name + " " + str(i+1))
            break
    tempFile = os.path.splitext(inputFilename)[0] + "_modified.csv"
    os.rename(inputFilename, tempFile)
    with open(tempFile, newline='') as fr, open(inputFilename,"w", newline='', encoding='utf-8', errors='ignore') as fw:
        r = csv.reader(fr)
        w = csv.writer(fw)
        w.writerow(new_header)
        next(r, None)
        for row in r:
            w.writerow(row)
    os.remove(tempFile)
    return
