import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import os
import sys

import GUI_IO_util
import GUI_util
import Stanza_util
import spaCy_util
import reminders_util
import config_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# There are no commands to run in the NLP_setup_package_language_main GUI

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(1),
                                                 GUI_height_brief=480, # height at brief display
                                                 GUI_height_full=520, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for setting up the default NLP packages and the language of your corpus'
config_filename = 'NLP_default_package_language_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

config_input_output_numeric_options=[0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)
window = GUI_util.window

package_var = tk.StringVar()
package_basics_var = tk.StringVar()
language_var = tk.StringVar()
language_list = []

memory_var = tk.IntVar()
document_length_var = tk.IntVar()
limit_sentence_length_var = tk.IntVar()

encoding_var = tk.StringVar()
export_json_var = tk.IntVar()
y_multiplier_integer=0

current_package_lb = tk.Label(window,text='Currently available default NLP package and language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, current_package_lb, True)

error = False

y_multiplier_integer_SV1=y_multiplier_integer

def clear(e):
    reset_language_list()
    export_json_var.set(0)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def display_available_options():
    global y_multiplier_integer, y_multiplier_integer_SV1, error, parsers, memory_var, document_length_var, limit_sentence_length_var, package_display_area_value
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory, document_length, limit_sentence_length = config_util.read_NLP_package_language_config()
    package_var.set(package)
    package_basics_var.set(package_basics)
    if language_var.get()!=language:
        language_var.set(language)
    memory_var.set(int(memory))
    document_length_var.set(int(document_length))
    limit_sentence_length_var.set(int(limit_sentence_length))
    # print("display",parsers_display_area)
    package_display_area = tk.Label(width=GUI_IO_util.package_display_area_width, height=1, anchor='w', text=str(package_display_area_value), state='disabled')
    # place widget with hover-over info
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.all_widget_pos,
                                                   y_multiplier_integer_SV1,
                                                   package_display_area, True, False, False, False, 90,
                                                   GUI_IO_util.open_TIPS_x_coordinate,
                                                   "The text area displays the currently selected options. To change this selection, use the NLP package and/or language dropdown menu,")

def get_str_package_display_area_value():
    display_area_value= \
        str(package_var.get()) + \
        str(package_basics_var.get()) + \
        str(language_var.get()) + \
        str(encoding_var.get()) + \
        str(export_json_var.get()) + \
        str(memory_var.get()) + \
        str(document_length_var.get()) + \
        str(limit_sentence_length_var.get())
    return display_area_value

def openConfigFile():
    import IO_files_util
    import time
    IO_files_util.openFile(window, GUI_IO_util.configPath + os.sep + config_filename)
    time.sleep(10) # wait 10 seconds to give enough time to save any changes to the csv config file
    # display_IO_setup(window, IO_setup_display_brief, temp_config_filename,
    #                  config_input_output_numeric_options, scriptName, silent)

openInputConfigFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openConfigFile())
# place widget with hover-over info
x_coordinate_hover_over=1100 # Mac 1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               openInputConfigFile_button, False, False, True,False, 90, x_coordinate_hover_over-50, "Open csv config file")

package_lb = tk.Label(window,text='NLP package (parser & annotators)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, package_lb, True)
package_var.set('Stanford CoreNLP')
package_menu = tk.OptionMenu(window, package_var, 'BERT', 'spaCy','Stanford CoreNLP', 'Stanza')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.all_widget_pos,
                                               y_multiplier_integer, package_menu)

y_multiplier_integer_SV2=y_multiplier_integer

# display_available_options()

def changed_NLP_package_set_parsers(*args):
    global y_multiplier_integer_SV2
    global parsers_display_area
    if package_var.get() == 'spaCy':
        available_parsers = ['Dependency parser']
    if package_var.get()=='Stanford CoreNLP':
        available_parsers = ['Neural Network', 'Probabilistic Context Free Grammar (PCFG)']
    if package_var.get() == 'Stanza':
        available_parsers = ['Constituency parser', 'Dependency parser']

    parsers_lb = tk.Label(window, text='Available parsers for ' + package_var.get()+'                      ')
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                                   y_multiplier_integer_SV2, parsers_lb, True)

    # mac 70
    parsers_display_area = tk.Label(width=80, height=1, anchor='w', text=', '.join(available_parsers), state='disabled')
    y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.all_widget_pos,
                                                   y_multiplier_integer_SV2, parsers_display_area)
    return y_multiplier_integer

y_multiplier_integer = changed_NLP_package_set_parsers()

package_basics_lb = tk.Label(window,text='NLP package for basic functions')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               package_basics_lb, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Use the dropdown menu to select the package (spaCy, Stanza) to be used for basic NLP operations: sentence splitting, tokenizing, lemmatizing.")
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
#                                                y_multiplier_integer, package_basics_lb, True)
package_basics_var.set('Stanza')
# TODO 'spaCy' will be added as an option for basic tokenizer and lemmatizer
package_basics_menu = tk.OptionMenu(window, package_basics_var, 'Stanza', 'spaCy')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.all_widget_pos,
                                               y_multiplier_integer,
                                               package_basics_menu, False, False, False, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "Use the dropdown menu to select the package (spaCy, Stanza) to be used for basic NLP operations: sentence splitting, tokenizing, lemmatizing.")

def activate_NLP_basics(*args):
    if package_basics_var.get()=='spaCy':
        mb.showwarning(title='Warning',
                       message='spaCy is not available yet for basic NLP operations.\n\nPlease, select another option.')
package_basics_var.trace('w', activate_NLP_basics)

language_lb = tk.Label(window,text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, language_lb, True)

menu_values = []
global language_menu
def get_available_languages():
    if package_var.get() == 'Stanford CoreNLP':
        languages_available=['Arabic','Chinese','English', 'German','Hungarian','Italian','Spanish']
    if package_var.get() == 'BERT':
        mb.showwarning(title='Option', message='The BERT option is not available yet. Sorry!\n\nPlease, select another option.')
        package_var.set('Stanford CoreNLP')
        return
    if package_var.get() == 'spaCy':
        languages_available = spaCy_util.list_all_languages()
    if package_var.get() == 'Stanza':
        languages_available = Stanza_util.list_all_languages()
    return languages_available

language_var.set('')
language_menu = ttk.Combobox(window, width=GUI_IO_util.language_widget_width, textvariable=language_var)
language_menu['values'] = get_available_languages()
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.all_widget_pos, y_multiplier_integer,
                                               language_menu, True, False, False, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "Use the dropdown menu to select the language your corpus is written in.\nDifferent packages (CoreNLP, spaCy, Stanza) can handle different sets of languages. Only Stanza allows multi-language selection.")

add_language_button = tk.Button(window, text='+', width=2,height=1,state='normal',command=lambda: activate_language_var())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.plus_column, y_multiplier_integer,
                                               add_language_button, True, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Click on the + button to activate the language dropdown menu where you can select another language to add to the list.\nOnly Stanza allows multi-language selection.")

reset_language_button = tk.Button(window, text='Reset', width=5,height=1,state='normal',command=lambda: reset_language_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.reset_column, y_multiplier_integer,
                                               reset_language_button, True, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Click on the Reset button to clear the list of any previously selected language(s).")

show_language_button = tk.Button(window, text='Show', width=5,height=1,state='normal',command=lambda: show_language_list())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.show_column, y_multiplier_integer,
                                               show_language_button, False, False, False, False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate,
                                               "Click on the Show button to display the list of selected language(s).")

encoding_lb = tk.Label(window, text='Select encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,encoding_lb, True)

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.all_widget_pos, y_multiplier_integer,encodingValue)

export_json_var.set(0)
export_json_label = tk.Checkbutton(window,
                                variable=export_json_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox(export_json_label, export_json_var, "Export Json file(s)", "Do NOT export Json file(s)"))
export_json_label.configure(text="Do NOT export Json file(s)")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               export_json_label, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "Tick the checkbox to export json files for every input file processed\nDepending upon the number of input files processed, the option may considerably affect disk space and processing speed")
# memory options
memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               memory_var_lb, True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(4)
# place widget with hover-over info # memory_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate+70,
                                               y_multiplier_integer,
                                               memory_var, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_indented_coordinate,
                                               "Use the slider widget to adjust the memory (NOT DISK SPACE!) you make available to Stanford CoreNLP\n4 OK for most CoreNLP annotators; coreference may need more memory\nThe memory widget is only available for the Stanford CoreNLP package for parser & annotators")

document_length_var_lb = tk.Label(window, text='Document length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               document_length_var_lb, True)

document_length_var = tk.Scale(window, from_=40000, to=90000, orient=tk.HORIZONTAL)
document_length_var.pack()
document_length_var.set(90000)
# place widget with hover-over info # document_length_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate+130,
                                               y_multiplier_integer,
                                               document_length_var, True, False, False, False, 90,
                                               GUI_IO_util.labels_x_indented_coordinate,
                                               "Stanford CoreNLP has a limit of 99999 characters for processing input files; the NLP Suite CoreNLP algorithms automatically split and merge larger input files (see TIPS file)\nLowering the document size does not seem to significantly improve the performance of CoreNLP annotators\nThe document length widget is only available for the Stanford CoreNLP package for parser & annotators")

limit_sentence_length_var_lb = tk.Label(window, text='Sentence length')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.sentence_length_lb, y_multiplier_integer,
                                               limit_sentence_length_var_lb,True)

limit_sentence_length_var = tk.Scale(window, from_=70, to=400, orient=tk.HORIZONTAL)
limit_sentence_length_var.pack()
limit_sentence_length_var.set(100)
# place widget with hover-over info # sentence_length_pos
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.sentence_length_pos,
                                               y_multiplier_integer,
                                               limit_sentence_length_var, False, False, False, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate,
                                               "The performance of Stanford CoreNLP annotators is affected by the sentence length in number of words of input documents (see TIPS file)\nStanford CoreNLP recommends a maximum sentence length in the range of 70-100 words\nThe sentence length widget is only available for the Stanford CoreNLP package for parser & annotators")
def save_NLP_config(parsers):
    encoding = encoding_var.get()
    export_json = export_json_var.get()
    memory = memory_var.get()
    document_length = document_length_var.get()
    limit_sentence_length = limit_sentence_length_var.get()
    if not 'CoreNLP' in package_var.get():
        timeout = 0
        memory = 0
        document_length = 0
        limit_sentence_length = 0

    # TODO any change in the labels MAIN NLP PACKAGE, LEMMATIZER PACKAGE, and LANGUAGE(S) must be carried out
    #   several times in config_util.py
    currently_selected_package_language= {'MAIN NLP PACKAGE': package_var.get(), 'LEMMATIZER PACKAGE': package_basics_var.get(), "LANGUAGE(S)": language_var.get()}
    config_util.save_NLP_package_language_config(window, currently_selected_package_language, package_var.get(), package_basics_var.get(),
                            language_var.get(), parsers_display_area['text'],
                            encoding, export_json, memory, document_length, limit_sentence_length)
    display_available_options()

def activate_language_var():
    # Disable the + after clicking on it and enable the class menu
    if language_menu.get()=='English' and package_var.get()=='Stanza':
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_Stanza_languages,
                                     reminders_util.message_Stanza_languages,
                                     True)
    add_language_button.configure(state='disabled')
    language_menu.configure(state='normal')

def check_language(*args):
    if language_var.get() in language_list:
        mb.showwarning(title='Warning',
                       message='The selected language "' + language_var.get() + '" is already in your selection list: ' + str(
                           language_list) + '.\n\nPlease, select another language.')
        window.focus_force()
        return
    else:
        if language_var.get() == '':
            language_menu.configure(state='normal')
            add_language_button.configure(state='disabled')
            reset_language_button.configure(state='disabled')
            show_language_button.configure(state='disabled')
        else:
            language_list.append(language_var.get())
            language_menu.configure(state='disabled')
            reset_language_button.configure(state='normal')
            show_language_button.configure(state='normal')
        if package_var.get()=='Stanza':
            add_language_button.configure(state='normal')
        else:
            add_language_button.configure(state='disabled')
language_var.trace('w', check_language)

check_language()

def changed_NLP_package(*args):
    global y_multiplier_integer
    global y_multiplier_integer_SV2
    global parsers_display_area
    if 'CoreNLP' in package_var.get():
        memory_var.configure(state='normal')
        document_length_var.configure(state='normal')
        limit_sentence_length_var.configure(state='normal')
    else:
        memory_var.configure(state='disabled')
        document_length_var.configure(state='disabled')
        limit_sentence_length_var.configure(state='disabled')
    language_list.clear()
    language_menu['values'] = get_available_languages()
    check_language()
    changed_NLP_package_set_parsers()
package_var.trace('w',changed_NLP_package)

changed_NLP_package()

def reset_language_list():
    language_var.set('')
    language_list.clear()
    language_menu.configure(state='normal')
    language_menu.set('')

def show_language_list():
    if len(language_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected language options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected language options are:\n\n  ' + '\n  '.join(language_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')

# y_multiplier_integer = y_multiplier_integer +.5

def close_GUI():
    if language_var.get()=='':
        mb.showwarning(title='Warning',message='You must select the language your corpus is written in before closing.')
        return
    if package_basics_var.get()=='':
        mb.showwarning(title='Warning',message='You must select the package for the basic functions of tokenizing, lemmatizing, sentence splitting before closing.')
        return
    import NLP_setup_update_util
    currently_selected_package_language = get_str_package_display_area_value()
    if package_display_area_value_upon_entry != currently_selected_package_language:
        answer = tk.messagebox.askyesno("Warning", 'You have made changes to the default NLP packages and language.\n\nYou will lose your changes if you CLOSE without saving.\n\nWOULD YOU LIKE TO SAVE THE CHANGES MADE?')
        if answer:
            save_NLP_config(parsers)
    NLP_setup_update_util.exit_window()

close_button = tk.Button(window, text='CLOSE', width=10, height=2, command=lambda: close_GUI())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate,
                                               y_multiplier_integer,
                                               close_button, True, False, False, False, 90,
                                               GUI_IO_util.read_button_x_coordinate,
                                               "When clicking the CLOSE button, the script will give you the option to save the currently selected configuration IF different from the previously saved configuration."
                                               "\nThe CLOSE button will also trigger the automatic update of the NLP Suite pulling the latest release from GitHub. The new release will be displayed next time you open your local NLP Suite."
                                               "\nYou must be connected to the internet for the auto update to work.")

videos_lookup = {'Setup NLP package & language options 1':'https://www.youtube.com/watch?v=-F8C22F_T_E&list=PL95lLs07jOtqArcIYzO-FX14T7lkauuab&index=1', 'Setup NLP package & language options 2':'https://www.youtube.com/watch?v=-F8C22F_T_E&list=PL95lLs07jOtqArcIYzO-FX14T7lkauuab&index=1'}
videos_options='Setup NLP package & language options 1','Setup NLP package & language options 2'

TIPS_lookup = {'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf','Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf','Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf'}
TIPS_options='Text encoding (utf-8)','Stanford CoreNLP memory issues','Stanford CoreNLP performance & accuracy'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The text widget displays the currently selected default NLP package and language values.\n\nClick on the button to the far right to open the config file for inspection."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the NLP package to be used as the default package for parser and annotators."+GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The text widget displays the available parsers for the selected NLP package " + package_var.get() +"." + GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the NLP package to be used as the default package for basic functions, namely, sentence splitter, tokenizer, lemmatizer."+GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the language(s) your input txt file(s) are written in. Different NLP packages support a different range of languages.\n\nFor those NLP packages that suport multiple languages (e.g., texts written in both English and Chinese), such as Stanza, hit the + button multiple times to add multiple languages.\n\nHit the Reset buttons to start fresh.\n\nHit the Show button to display the current language selection." + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,
                                  "NLP Suite Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding."+GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                                         "Tick the checkbox to export or not export the Json file(s) in txt format produced by the selected NLP package." + GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                                         "The performance of different NLP tools (e.g., Stanford CoreNLP) is affected by various issues: memory size of your computer, document size, sentence length\n\nPlease, select the memory size Stanford CoreNLP will use. Default memory is 4. Lower this value if CoreNLP runs out of resources.\n   For CoreNLP co-reference resolution you may wish to increase the memory size when processing larger files (compatibly with the memory size of your machine).\n\nLonger documents affect performace. Stanford CoreNLP has a limit of 100,000 characters processed (the NLP Suite limits this to 90,000 as default). If you run into performance issues you may wish to further reduce the document size.\n\nSentence length also affect performance. The Stanford CoreNLP recommendation is to limit sentence length to 70 or 100 words.\n   You may wish to compute the sentence length of your document(s) so that perhaps you can edit the longer sentences.\n\nOn these issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf." + GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    return y_multiplier_integer

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up the default NLP package (e.g., spaCy, Stanford CoreNLP, Stanza), language (e.g., English, Chinese), and language encoding (e.g., utf-8) to be used for parsing and annotating your corpus in a specific language. Different packages support different sets of languages.\n\n" + \
                "When Stanford CoreNLP is selected as NLP package, various options become available that apply only to CoreNLP: Memory, Document length (CoreNLP has a maximum processing size of 100,000 characters), Limit sentence length (CoreNLP performance deteriorates rapidly with sentence lengths above 100 words)\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, True, scriptName, False)

display_available_options()

if error:
    mb.showwarning(title='Warning',
               message="The config file " + config_filename + " could not be found in the sub-directory 'config' of your main NLP Suite folder.\n\nPlease, setup the default NLP package and language options then click on the CLOSE button to save your options.")
    answer = tk.messagebox.askyesno("Warning", 'Do you want to watch the video on how to setup NLP package and language options?')
    if answer:
        GUI_util.videos_dropdown_field.set('Setup NLP package & language options')
        # GUI_util.watch_video(videos_lookup, scriptName)

package_display_area_value_upon_entry = get_str_package_display_area_value()

# to make sure the release version is updated even when users do not click on the CLOSE button
#   but on the Mac top-left red button or Windows top-right X button
GUI_util.window.protocol("WM_DELETE_WINDOW", close_GUI)
GUI_util.window.mainloop()
