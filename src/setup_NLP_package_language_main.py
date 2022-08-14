import tkinter as tk
from tkinter import ttk

import GUI_IO_util
import GUI_util
y_multiplier_integer = GUI_util.y_multiplier_integer + 0
window = GUI_util.window
package_var=tk.IntVar()
language_var=tk.IntVar()

package_lb = tk.Label(window,text='NLP package')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, package_lb, True)
package_var.set('Stanford CoreNLP')
package_menu = tk.OptionMenu(window, package_var, 'Stanford CoreNLP','spaCy','Stanza')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+100,
                                               y_multiplier_integer, package_menu, True)

language_lb = tk.Label(window,text='Language')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+300,
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
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.get_labels_x_coordinate()+400,
                                               y_multiplier_integer, language_menu,True)

add_language_button = tk.Button(window, text='+', width=2,height=1,state='normal',command=lambda: activate_language_var())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 710,y_multiplier_integer,add_language_button, True)

reset_language_button = tk.Button(window, text='Reset', width=5,height=1,state='normal',command=lambda: reset_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 750,y_multiplier_integer,reset_language_button,True)

show_language_button = tk.Button(window, text='Show', width=5,height=1,state='normal',command=lambda: show_language_list())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.get_open_file_directory_coordinate() + 810,y_multiplier_integer,show_language_button)

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
        parser_menu_var.set("Probabilistic Context Free Grammar (PCFG)")
    if package_var.get() == 'Stanza':
        available_parsers = 'Constituency parser', 'Dependency parser'
        parser_menu_var.set("Dependency parser")
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
