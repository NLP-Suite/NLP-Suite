import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP_setup_external_software_main",['os','tkinter','webbrowser','time'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import webbrowser
import time

import GUI_IO_util
import IO_files_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# There are no commands in the NLP_setup_package_language_main GUI

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(1),
                                                 GUI_height_brief=300, # height at brief display
                                                 GUI_height_full=320, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label = 'Graphical User Interface (GUI) for setting up external software used in the NLP Suite (e.g., Stanford CoreNLP, Gephi)'
config_filename = 'NLP_setup_external_software_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

config_input_output_numeric_options=[0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)
GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)
window = GUI_util.window

def clear(e):
    software_download_var.set('')
    software_website_url_var.set('')
    software_website_url=''
    software_install_dir_var.set('')
    software_install_var.set('')
    software_install_area=''
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

software_download_var = tk.StringVar()
software_install_var = tk.StringVar()
y_multiplier_integer=0

missing_software_lb = tk.Label(window,text='Missing external software')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, missing_software_lb, True)

y_multiplier_integer_SV=y_multiplier_integer

missing_software_var = tk.StringVar()

missing_software_display_area = tk.Entry(width=GUI_IO_util.missing_software_display_area_width, state='disabled', textvariable=missing_software_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.website_url_placement,
                                               y_multiplier_integer, missing_software_display_area, True)

def openConfigFile():
    IO_files_util.openFile(window, GUI_IO_util.configPath + os.sep + config_filename)
    time.sleep(10) # wait 10 seconds to give enough time to save any changes to the csv config file

openInputConfigFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openConfigFile())
# place widget with hover-over info
x_coordinate_hover_over=1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               openInputConfigFile_button, False, False, True,False, 90,
                                               x_coordinate_hover_over-120, "Open csv config file")

software_download_lb = tk.Label(window,text='Software download')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, software_download_lb, True)
software_download_var.set('')
# 'SENNA' was removed from SVO options; way too slow
# temporarily excluded '*'
software_download_menu = tk.OptionMenu(window, software_download_var, 'Stanford CoreNLP', 'Gephi','Google Earth Pro','Java (JDK)','MALLET','WordNet')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.dowload_install, y_multiplier_integer,
                                               software_download_menu, True, False, True, False, 90,
                                               GUI_IO_util.watch_videos_x_coordinate, "Select the FREEWARE external software to be downloaded; the software website url will be displayed after selection.\nYOU MUST BE CONNECTED TO THE INTERNET FOR DOWNLOADING SOFTWARE.\nThe software installation directory will be automatically displayed after selection so that it can be saved in the config file NLP_setup_external_software_config.csv.")

software_website = tk.Label(height=1, anchor='w', text='Website url')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.website_url_placement,
                                               y_multiplier_integer, software_website, True)

software_website_url_var=tk.StringVar()
software_website_display_area = tk.Entry(width=GUI_IO_util.missing_software_display_area_width, state='disabled', textvariable=software_website_url_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.website_url_placement,
                                               y_multiplier_integer, software_website_display_area, True)

error = False

def openWebsite(software_website_url):
    if software_website_url!='':
        webbrowser.open_new_tab(software_website_url)
    else:
        mb.showwarning(title='Warning',
                   message='There is no external software website url.\n\nPlease, using the dropdown menu, select the "Software download" option you want to access and try again.')

openWebsite_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openWebsite(software_website_url_var.get()))
# place widget with hover-over info
x_coordinate_hover_over=1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               openWebsite_button, False, False, True,False, 90,
                                               x_coordinate_hover_over-120, "Open software website")

def openSoftwareDir(software_dir):
    if software_dir!='':
        IO_files_util.open_directory_removing_date_from_directory(window,software_dir,True)
    else:
        mb.showwarning(title='Warning',
                message='There is no external software directory to open.\n\nPlease, using the dropdown menu, select the "Software install" option you want to access and try again.')

software_install_lb = tk.Label(window,text='Software install')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, software_install_lb, True)
software_install_var.set('')
# temporarily excluded '*'
software_install_menu = tk.OptionMenu(window, software_install_var, 'Stanford CoreNLP', 'Gephi','Google Earth Pro','Java (JDK)','MALLET','WordNet')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.dowload_install, y_multiplier_integer,
                                               software_install_menu, True, False, True, False, 90,
                                               GUI_IO_util.watch_videos_x_coordinate, "Select the external software to be installed after having downloaded it; the software installation directory will be displayed after selection.\nThe software installation directory will be automatically saved in the config file NLP_setup_external_software_config.csv.")

software_install_dir_var=tk.StringVar()
software_install_area = tk.Entry(width=GUI_IO_util.missing_software_display_area_width, state='disabled', textvariable=software_install_dir_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.website_url_placement,
                                               y_multiplier_integer, software_install_area, True)

opensoftware_dir_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openSoftwareDir(software_install_dir_var.get()))
# place widget with hover-over info
x_coordinate_hover_over=1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               opensoftware_dir_button, False, False, True,False, 90,
                                               x_coordinate_hover_over-200, "Open external software directory")

def activate_software_website(*args):
    global software_dir
    existing_software_config = IO_libraries_util.get_existing_software_config()
    software_website_url = ''
    # software_download_var contains the external software download options
    if software_download_var.get() != '':
        software_dir, software_website_url = IO_libraries_util.external_software_download(scriptName,
                                            software_download_var.get(), existing_software_config)
        if software_dir==None or software_dir=='':
            return
        software_website_url_var.set(software_website_url)
        software_website_url = software_website_url_var.get()

        activate_software_install()
software_download_var.trace('w', activate_software_website)

def activate_software_install(*args):
    global software_dir, existing_software_config, missing_software_list
    missing_software_list=[]
    # software_install_var contains the external software menu options
    if software_install_var.get()!='':
        # avoid triggering the messages in external_software_install when you have downloaded the external software
        if software_download_var.get()=='':
            software_dir, existing_software_config = IO_libraries_util.external_software_install(scriptName, software_install_var.get(), existing_software_config)
        else:
            software_install_var.set(software_download_var.get())
        if software_dir==None:
            return
        software_install_dir_var.set(software_dir)
        software_install_area=software_install_dir_var.get()
        missing_software_string=missing_software_var.get()
        # convert comma-separated string to list []
        missing_software_list = missing_software_var.get().split(",")
        for index, x in enumerate(missing_software_list):
            if x.lstrip()==software_install_var.get().upper():
                missing_software_list.remove(x)
                break
        new_missing_software_string=', '.join(missing_software_list)
        missing_software_var.set(new_missing_software_string.lstrip())
        if missing_software_var.get()=='':
            missing_software_var.set('All external software has been installed')
            mb.showwarning(title='Warning',message='All external software has been installed.')
        missing_software_display_area=new_missing_software_string.lstrip()
    else:
        # software_download_var contains the external software download options
        if software_download_var.get() != '':
            software_install_var.set(software_download_var.get())
            software_install_dir_var.set(software_dir)
            software_install_area = software_install_dir_var.get()
software_install_var.trace('w',activate_software_install)

def save_external_software_config():
    IO_libraries_util.save_software_config(existing_software_config, missing_software_var.get())

def close_GUI():
    import NLP_setup_update_util
    if missing_external_software_upon_entry!=missing_software_var.get():
        answer = tk.messagebox.askyesno("Warning", 'You have made changes to the installed software.\n\nYou will lose your changes if you CLOSE without saving.\n\nWould you like to save the changes made?')
        if answer:
            save_external_software_config()
    NLP_setup_update_util.exit_window(window, GUI_util.local_release_version, GUI_util.GitHub_newest_release)
    window.destroy()
    sys.exit(0)

close_button = tk.Button(window, text='CLOSE', width=10, height=2, command=lambda: close_GUI())
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.close_button_x_coordinate,
                                               y_multiplier_integer,
                                               close_button, True, False, False, False, 90,
                                               GUI_IO_util.read_button_x_coordinate,
                                               "When clicking the CLOSE button, the script will give you the option to save the currently selected configuration IF different from the previously saved configuration."
                                               "\nThe CLOSE button will also trigger the automatic update of the NLP Suite pulling the latest release from GitHub. The new release will be displayed next time you open your local NLP Suite."
                                               "\nYou must be connected to the internet for the auto update to work.")

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'Stanford CoreNLP download install run':'TIPS_NLP_Stanford CoreNLP download install run.pdf',
               'Topic modeling MALLET installation':'TIPS_NLP_Topic modeling Mallet installation.pdf',
               'Java download install':'TIPS_NLP_Java download install run.pdf',
               'Google API Key':'TIPS_NLP_GIS_Google API Key.pdf',
               'Gephi':'TIPS_NLP_Gephi network graphs.pdf',
               'MALLET':'TIPS_NLP_Topic modeling Mallet.pdf',
               'WordNet':'TIPS_NLP_WordNet.pdf'}
TIPS_options='Stanford CoreNLP download install run','Topic modeling MALLET installation',\
             'Java download install','Google API Key','Gephi', 'MALLET', 'WordNet'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "The text widget, always disabled, displays the FREEWARE external software that has not been installed yet in the NLP Suite. All missing software will need to be downloaded/installed or some functionality will be lost for some of the scripts (e.g., you cannot do any textual analysis based on Stanford CoreNLP without Stanford CoreNLP or produce any geographic maps without Google Earth Pro).\n\nClick on the button to the far right to open the config file for inspection."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the FREEWARE external software that you wish to download.\n\nYou do not need to download/install all external software at once. Different algorithms in the NLP Suite require different packages (e.g., you cannot do any textual analysis based on Stanford CoreNLP without Stanford CoreNLP or produce any geographic maps without Google Earth Pro).\n\nStanford CoreNLP, Gephi, and MALLET (and some other NLP Suite scripts) require a copy of the FREEWARE Java downloaded and installed on your machine."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the FREEWARE external software that you wish to install on your machine after dowloading it.\n\nGephi and Google Earth Pro on a Mac are installed in Applications."+GUI_IO_util.msg_Esc)
    return y_multiplier_integer

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up all the external packages used in the NLP Suite: Stanford CoreNLP, Gephi, Google Earth Pro, Java (JDK), MALLET, WordNet.\n\nTHESE ARE ALL FREEWARE PACKAGES.\n\nFailure to install a specific package will only affect the functions that rely on the package. Thus, for instance, you cannot visualize network graphs unless you download and install Gephi or visualize GIS maps without downloading and installing Google Earth Pro. More crucially, you cannot perform many of the key NLP tasks (e.g., parser, NER annotator, gender annotator, coreference resolution, SVO-Subject-Verb-Object-extractor without downloading and installing Stanford CoreNLP.\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, True, scriptName, False)

software_dir, software_url, missing_external_software = IO_libraries_util.get_external_software_dir(scriptName, software_download_var.get(), silent=False, only_check_missing=False)
if missing_external_software == '':
    missing_software_var.set('All external software has been installed')
    error = False
else:
    # must be displayed at the end after the whole GUI has been laid
    error = True
    temp_missing_external_software=missing_external_software.replace('\n\n',', ')[:-2]
    missing_software_var.set(temp_missing_external_software)
    if not os.path.isfile(config_filename):
        mb.showwarning(title='External software installation error',
                   message='The following external software needs to be downloaded/installed or some of the algorithms that require the software listed below will not run.\n\n' + str(missing_external_software) +'\n\nPlease, using the dropdown menu Software download & install, select the software to download/install.')
    else:
        mb.showwarning(title='External software installation error',
                   message='The following external software have not been found or have been found with errors (e.g., you may have moved or renamed the Stanford CoreNLP directory) in the config file NLP_setup_external_software_config.csv:\n\n' + str(missing_external_software) + '\n\nSome of the algorithms that require the software listed above will not run.\n\nPlease, using the dropdown menu Software download & install, select the software to download/install.')

missing_external_software_upon_entry=missing_software_var.get()

existing_software_config = IO_libraries_util.get_existing_software_config()

GUI_util.window.mainloop()
