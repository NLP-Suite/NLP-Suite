import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

import GUI_IO_util
import GUI_util
import Stanza_util
import reminders_util


# RUN section ______________________________________________________________________________________________________________________________________________________

# There are no commands in the NLP_setup_package_language_main GUI

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(1),
                                                 GUI_height_brief=310, # height at brief display
                                                 GUI_height_full=350, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for setting up the default NLP packages and the language of your corpus'
config_filename = 'NLP_setup_package_language_main_config.csv'

config_input_output_numeric_options=[0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)
window = GUI_util.window

package_var = tk.StringVar()
package_basics_var = tk.StringVar()
language_var = tk.StringVar()
language_list = []
y_multiplier_integer=0

current_package_lb = tk.Label(window,text='Currently available default NLP package and language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, current_package_lb, True)

package, parsers, package_basics, language = GUI_IO_util.read_NLP_package_language_config(window, '')

package_display_area_value = f"NLP PACKAGE: {package}, NLP BASIC PACKAGE: {package_basics}, LANGUAGE(S): {language}"

package_display_area = tk.Label(width=80, height=1, text=str(package_display_area_value), state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.get_open_file_directory_coordinate()+250,
                                               y_multiplier_integer, package_display_area)

package_lb = tk.Label(window,text='NLP package (parser & annotators)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, package_lb, True)
package_var.set('Stanford CoreNLP')
package_menu = tk.OptionMenu(window, package_var, 'Stanford CoreNLP','spaCy','Stanza')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+100,
                                               y_multiplier_integer, package_menu)

package_basics_lb = tk.Label(window,text='NLP package (tokenizer/lemmatizer)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, package_basics_lb, True)
package_basics_var.set('Stanza')
# TODO 'spaCy' will be added as an option
package_basics_menu = tk.OptionMenu(window, package_basics_var, 'Stanza')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+100,
                                               y_multiplier_integer, package_basics_menu)

language_lb = tk.Label(window,text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, language_lb, True)

menu_values = []
global language_menu
def get_available_languages():
    if package_var.get() == 'Stanford CoreNLP':
        languages_available=['Arabic','Chinese','English', 'German','Hungarian','Italian','Spanish']
    if package_var.get() == 'spaCy':
        languages_available = ['English']
    if package_var.get() == 'Stanza':
        languages_available = Stanza_util.list_all_languages()
    return languages_available

language_var.set('English')
language_menu = ttk.Combobox(window, width=70, textvariable=language_var)
language_menu['values'] = get_available_languages()
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate()+100,
                                               y_multiplier_integer, language_menu,True)

add_language_button = tk.Button(window, text='+', width=2,height=1,state='normal',command=lambda: activate_language_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 510,y_multiplier_integer,add_language_button, True)

reset_language_button = tk.Button(window, text='Reset', width=5,height=1,state='normal',command=lambda: reset_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 550,y_multiplier_integer,reset_language_button,True)

show_language_button = tk.Button(window, text='Show', width=5,height=1,state='normal',command=lambda: show_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 610,y_multiplier_integer,show_language_button)

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
        else:
            language_list.append(language_var.get())
            language_menu.configure(state='disabled')
        if package_var.get()=='Stanza':
            add_language_button.configure(state='normal')
            reset_language_button.configure(state='normal')
            show_language_button.configure(state='normal')
        else:
            add_language_button.configure(state='disabled')
            # reset_language_button.configure(state='disabled')
            show_language_button.configure(state='disabled')
language_var.trace('w', check_language)

check_language()

def changed_NLP_package(*args):
    language_list.clear()
    language_menu['values'] = get_available_languages()
    check_language()
    if package_var.get()=='Stanford CoreNLP':
        available_parsers = 'Neural Network', 'Probabilistic Context Free Grammar (PCFG)'
    if package_var.get() == 'Stanza':
        available_parsers = 'Constituency parser', 'Dependency parser'
package_var.trace('w',changed_NLP_package)

changed_NLP_package()


def reset_language_list():
    language_list.clear()
    language_menu.configure(state='normal')
    language_var.set('')

def show_language_list():
    if len(language_list)==0:
        mb.showwarning(title='Warning', message='There are no currently selected language options.')
    else:
        mb.showwarning(title='Warning', message='The currently selected language options are:\n\n  ' + '\n  '.join(language_list) + '\n\nPlease, press the RESET button (or ESCape) to start fresh.')


videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Setup INPUT-OUTPUT options':'TIPS_NLP_Setup INPUT-OUTPUT options.pdf'}
TIPS_options='Setup INPUT-OUTPUT options'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The text widget displays the currently selected default NLP package and language values."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the NLP package to be used as the default package for parser and annotators."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the NLP package to be used as the default package for basic functions, namely, sentence splitter, tokenizer, lemmatizer."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the language(s) your input txt file(s) are written in. Different NLP packages support a different range of languages.\n\nFor those NLP packages that suport multiple languages (e.g., texts written in both English and Chinese), such as Stanza, hit the + button multiple times to add multiple languages. Since English is the default value, if you hit + English will be added as part of a multi-language selection. If you do not want English to be part of the multi-language selection, hit Reset before hitting + and select and add your languages.\n\nHit the Reset buttons to start fresh.\n\nHit the Show button to display the current language selection.")
    y_multiplier_integer = 5
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window, GUI_IO_util.get_help_button_x_coordinate(), 0)
# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up the default NLP package (e.g., spaCy, Stanford CoreNLP, Stanza) and language (e.g., English, Chinese) to be used for parsing and annotating your corpus in a specific language. Different packages support different sets of languages."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, True, 'NLP_setup_package_language_main')

GUI_util.window.mainloop()
