import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL search", ['os', 'tkinter']) == False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_CoNLL_util
import CoNLL_search_util
import statistics_csv_util
import Excel_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util

import Stanford_CoreNLP_tags_util

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size = '1000x750'
GUI_label = 'GUI for CoNLL Table Search'
config_filename = 'conll-table-search-config.txt'  # filename used in Stanford_CoreNLP_main
# The 6 values of config_option refer to:
#   software directory
#   input file 1 for CoNLL file 2 for TXT file 3 for csv file 4 for any type of file
#   input dir
#   input secondary dir
#   output file
#   output dir
config_option = [0, 1, 0, 0, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +1 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + 1
window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

from CoNLL_table_searcher_GUI import *

# RUN section ____________________________________________________________________________________________________


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
def run(search_filters):
    for search_filter in search_filters:
        search_filter.is_and = and_or_selector.get() == "All of the below is true"
        if search_filter.searched_term.startswith('*'):
            search_filter.searched_term.replace('*', '')
            search_filter.search_type = SearchType.starts_with
        elif search_filter.searched_term.endswith('*'):
            search_filter.searched_term.replace('*', '')
            search_filter.search_type = SearchType.ends_with
        search_filter.searched_term = search_filter.searched_term.split('-')[0].replace(' ', '')

    global recordID_position, documentId_position, data, data_divided_sents

    noResults = "No results found matching your search criteria for your input CoNLL file. Please, try different search criteria.\n\nTypical reasons for this warning are:\n   1.  You are searching for a token/word not found in the FORM or LEMMA fields (e.g., 'child' in FORM when in fact FORM contains 'children', or 'children' in LEMMA when in fact LEMMA contains 'child'; the same would be true for the verbs 'running' in LEMMA instead of 'run');\n   2. you are searching for a token that is a noun (e.g., 'children'), but you select the POS value 'VB', i.e., verb, for the POSTAG of searched token."
    filesToOpen = []  # Store all files that are to be opened once finished

    input_file_name = GUI_util.inputFilename.get()
    output_dir = GUI_util.output_dir_path.get()

    withHeader = True
    recordID_position = 8
    documentId_position = 10
    data, header = IO_csv_util.get_csv_data(input_file_name, withHeader)
    if len(data) == 0:
        return
    data_divided_sents = IO_CoNLL_util.sentence_division(data)
    if data_divided_sents is None:
        return
    if len(data_divided_sents) == 0:
        return

    documentId_position = 10
    data, header = IO_csv_util.get_csv_data(input_file_name, withHeader=True)

    if len(data) <= 1000000:
        try:
            data = sorted(data, key=lambda x: int(x[8]))
        except:
            mb.showwarning(title="CoNLLL table ill formed",
                           message="The CoNLL table is ill formed. You may have tinkered with it. Please, rerun the Stanford CoreNLP parser since many scripts rely on the CoNLL table.")
            return

    if len(data) == 0:
        return
    all_sents = IO_CoNLL_util.sentence_division(data)
    if len(all_sents) == 0:
        return
    queried_list = CoNLL_search_util.search_conll_table2(all_sents, filters)

    if len(queried_list) != 0:
        output_file_name = IO_files_util.generate_output_file_name(input_file_name, output_dir, '.csv', 'QC',
                                                                   'CoNLL_Search', searchedCoNLLField)
        headers = ['ID', 'Form', 'Lemma', 'Postag', 'NER', 'Head', 'Deprel', 'Clausal Tag', 'Record ID',
                   'Sentence ID', 'Document ID', 'Document']
        queried_list.insert(0, headers)
        errorFound = IO_csv_util.list_to_csv(GUI_util.window, queried_list, output_file_name)
        if errorFound:
            return
        filesToOpen.append(output_file_name)

        if GUI_util.open_csv_output_checkbox.get():
            IO_files_util.OpenOutputFiles(GUI_util.window, True, filesToOpen)

    # # Gephi network graphs _________________________________________________
    # TODO
    # the CoNLL table search can export a word and related words in a variety of relations to the word (by POS DEPREL etc.)
    # ideally, these sets of related words can be visualized in a network graph in Gephi
    # But... Gephi has been hard coded for SVO, since it has only been used for that so far, but any 2 or 3-terms can be visualized as a network
    # Furthermore, if we cant to create dynamic models that vary ov ertime, wehere we use the sentence index as a proxy for time, we need to pass that variable as well (the saentence index)
    # create_gexf would need to read in the proper column names, rather than S V OA
    # outputFileBase = os.path.basename(output_file_name)[0:-4] # without .csv or .txt
    # gexf_file = Gephi_util.create_gexf(outputFileBase, output_dir, output_file_name)
    # filesToOpen.append(gexf_file)

    else:
        mb.showwarning(title='Empty query results', message=noResults)



run_script_command = lambda: run(search_filters=filters)

GUI_util.run_button.configure(command=run_script_command)

GUI_util.window.mainloop()
