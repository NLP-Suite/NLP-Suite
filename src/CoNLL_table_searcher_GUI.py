import tkinter as tk
import tkinter.ttk as ttk
import GUI_util
import GUI_IO_util
import Stanford_CoreNLP_tags_util
from CoNLL_search_util import SearchField, SearchType, CoNLLFilter
from typing import List

# GUI CHANGES add following lines to every special GUI
# +1 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + 1
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
GUI_util.GUI_bottom(config_input_output_options, y_multiplier_integer + 5, readMe_command, {'None': 'None'}, 'None')
