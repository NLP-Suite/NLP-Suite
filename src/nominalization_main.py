#written by Catherine Xiao, Apr 2018
#edited by Elaine Dong, Dec 04 2019
#edited by Roberto Franzosi, Nov 2019, October 2020

# https://stackoverflow.com/questions/2836959/adjective-nominalization-in-python-nltk
# https://stackoverflow.com/questions/45109767/get-verb-from-noun-wordnet-python

# https://github.com/topics/nominalization
# https://pypi.org/project/qanom/0.0.1/

import sys
import GUI_util
import IO_libraries_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Nominalization",['tkinter','nltk','pywsd','wn','csv','re','os','collections'])==False:
#     sys.exit(0)

import os
import tkinter as tk
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputDir, outputDir,openOutputFiles,createCharts,chartPackage, check_ending):

    filesToOpen = []

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')

    import nominalization_util
    outputFiles = nominalization_util.nominalization(inputFilename,inputDir, outputDir, config_filename, config_input_output_numeric_options, openOutputFiles,createCharts,chartPackage,check_ending)

    if outputFiles!=None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)

    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                                GUI_util.input_main_dir_path.get(),
                                GUI_util.output_dir_path.get(),
                                GUI_util.open_csv_output_checkbox.get(),
                                GUI_util.create_chart_output_checkbox.get(),
                                GUI_util.charts_package_options_widget.get(),
                                check_nom_verb_ending_var.get())

GUI_util.run_button.configure(command=run_script_command)


# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=280, # height at brief display
                             GUI_height_full=360, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Nominalization'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('_main.py', '_config.csv')

# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

check_nom_verb_ending_var = tk.IntVar()

check_nom_verb_ending_var.set(1)
check_nom_verb_ending_checkbox = tk.Checkbutton(window, variable=check_nom_verb_ending_var, onvalue=1, offvalue=0)
check_nom_verb_ending_checkbox.config(text="Check the nominalized verb ending")
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer,
                                               check_nom_verb_ending_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "The checkbox, when ticked, checks nominalized verbs (i.e., nouns) for the typical ending of nominalized verbs:\
                                               \nnent, ing, ion, ance, ence")

# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,check_nom_verb_ending_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Nominalization':'TIPS_NLP_Nominalization.pdf'}
TIPS_options='Nominalization'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, untick the checkbox if you do not want to check nominalized verbs for their typical ending (e.g., ing, ion; see TIPS file).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The Python 3 scripts analyzes a text file for instances of nominalization (i.e., the use of nouns instead of verbs, such as 'the lynching' occurred).\n\nNominalization, together with passive verb voices, can be used to deny agency. In fact, in an expression such as 'the lynching occurred' there is no mention of an agent, of who did it."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
