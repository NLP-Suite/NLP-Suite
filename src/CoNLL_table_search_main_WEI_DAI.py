import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "CoNLL table_search", ['os', 'tkinter','typing']) == False:
    sys.exit(0)

import tkinter as tk
import tkinter.messagebox as mb
import tkinter.ttk as ttk
from typing import List

import GUI_IO_util
import IO_CoNLL_util
import CoNLL_table_search_util
import IO_files_util
import IO_csv_util

import Stanford_CoreNLP_tags_util
from CoNLL_table_search_util import SearchField, SearchType, CoNLLFilter
from CoNLL_table_search_util import SearchField, SearchType, CoNLLFilter

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
    queried_list = CoNLL_table_search_util.search_conll_table2(all_sents, filters)

    if len(queried_list) != 0:
        output_file_name = IO_files_util.generate_output_file_name(input_file_name, output_dir, '.csv', 'QC',
                                                                   'CoNLL_Search', searchedCoNLLField)
        headers = ['ID', 'Form', 'Lemma', 'POStag', 'NER', 'Head', 'DEPrel', 'Clause Tag', 'Record ID',
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


GUI_util.run_button.configure(command=run_script_command)

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

window = GUI_util.window
config_input_output_options = GUI_util.config_input_output_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options, config_filename)

searchedCoNLLField = tk.StringVar()
searched_term = tk.StringVar()
searched_type = tk.StringVar()
filters: List[CoNLLFilter] = []
and_or_selector = tk.StringVar()
should_be_false = tk.StringVar()


def clear(e):
    searched_term.set('e.g.: father')
    searchedCoNLLField.set('*')
    GUI_util.clear("Escape")


window.bind("<Escape>", clear)

# used to place noun/verb checkboxes starting at the top level
y_multiplier_integer_top = y_multiplier_integer

tk.Label(window, text='Searched Field') \
    .place(x=GUI_IO_util.get_labels_x_coordinate(),
           y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step() * y_multiplier_integer)

searched_field_menu = tk.OptionMenu(window, searchedCoNLLField, *SearchField.list())
searchedCoNLLField.set(SearchField.FORM.name)

y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               searched_field_menu)

tk.Label(window, text='Should it be false?') \
    .place(x=GUI_IO_util.get_labels_x_coordinate(),
           y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step() * y_multiplier_integer)

should_be_false_option_menu = tk.OptionMenu(window, should_be_false, 'does', 'does not')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               should_be_false_option_menu)
should_be_false.set('does')

tk.Label(window, text='Type of filter') \
    .place(x=GUI_IO_util.get_labels_x_coordinate(),
           y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step() * y_multiplier_integer)

searched_type_menu = tk.OptionMenu(window, searched_type, *SearchType.list())
searched_type.set(SearchType.match.name)

y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               searched_type_menu)
y_multiplier_for_searched_term = y_multiplier_integer

tk.Label(window, text='Searched token') \
    .place(x=GUI_IO_util.get_labels_x_coordinate(),
           y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step() * y_multiplier_integer)

searched_term.set('father')

entry_searchField_kw = tk.Entry(window, textvariable=searched_term)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               entry_searchField_kw)

filter_table = ttk.Treeview(window, columns=('field', 'does/does not', 'type', 'term'))
filter_table.heading('field', text='Field')
filter_table.heading('does/does not', text='does/does not')
filter_table.heading('type', text='Type')
filter_table.heading('term', text='Term')
for index in range(0, 3):
    filter_table.column(index, width=120)
filter_table.column(3, width=220)


def add_filter():
    new_filter = CoNLLFilter()
    new_filter.searched_term = searched_term.get()
    new_filter.search_type = SearchType[searched_type.get()]
    new_filter.search_field = SearchField[searchedCoNLLField.get()]
    new_filter.should_be_false = should_be_false.get() == 'does not'
    new_filter.is_and = True
    filters.append(new_filter)
    filter_table.insert('', 'end', text=str(len(filters) - 1),
                        values=(new_filter.search_field.name,
                                should_be_false.get(),
                                new_filter.search_type.name,
                                new_filter.searched_term))


add_button = tk.Button(window, text='Add this filter', command=add_filter)


def delete_filter():
    selected = filter_table.focus()
    index_of_selected = filter_table.index(selected)
    filter_table.delete(selected)
    filters.pop(index_of_selected)
    print(index_of_selected)


delete_button = tk.Button(window, text='Delete Selected Filter', command=delete_filter)

y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(), y_multiplier_integer,
                                               add_button, sameY=True)
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               delete_button)

tk.Label(window, text='Condition') \
    .place(x=GUI_IO_util.get_labels_x_coordinate(),
           y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step() * y_multiplier_integer)

condition_option = tk.OptionMenu(window, and_or_selector, "Any of the below is true", "All of the below is true")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,
                                               condition_option)
and_or_selector.set("All of the below is true")

y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,
                                               filter_table)


def on_searched_field_change(*args):
    field = searchedCoNLLField.get()
    global entry_searchField_kw
    if SearchField[field] == SearchField.DEPREL:
        new_entry = tk.OptionMenu(window, searched_term, '*',
                                  *sorted(
                                      [k + " - " + v for k, v in
                                       Stanford_CoreNLP_tags_util.dict_DEPREL.items()]
                                  ))
        searched_term.set('*')
    elif SearchField[field] == SearchField.POSTAG:
        new_entry = tk.OptionMenu(window, searched_term, '*', 'JJ* - Any adjective', 'NN* - Any noun', 'VB* - Any verb',
                                  *sorted(
                                      [k + " - " + v for k, v in Stanford_CoreNLP_tags_util.dict_POSTAG.items()]
                                  )
                                  )
        searched_term.set('*')

    else:
        new_entry = tk.Entry(window, textvariable=searched_term)
        searched_term.set('')

    GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),
                            y_multiplier_for_searched_term,
                            new_entry)
    entry_searchField_kw.destroy()
    entry_searchField_kw = new_entry
searchedCoNLLField.trace('w', on_searched_field_change)

readMe_message = "This Python 3 script allows you to search in the CoNLL table."
readMe_command = lambda: GUI_IO_util.readme_button(window, GUI_IO_util.get_help_button_x_coordinate(),
                                                   GUI_IO_util.get_basic_y_coordinate(), "Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options, y_multiplier_integer + 5, readMe_command, {'None': 'None'}, 'None')

GUI_util.window.mainloop()
