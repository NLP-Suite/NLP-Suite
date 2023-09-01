import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"NLP_setup_external_software_main",['os','tkinter','webbrowser','time'])==False:
    sys.exit(0)

# software is downloaded and installed in IO_libraries_util
#   def external_software_download(calling_script, software_name, existing_software_config)
#   def external_software_install(calling_script, software_name, existing_software_config):

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
                                                 GUI_height_brief=280, # height at brief display
                                                 GUI_height_full=300, # height at full display
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
    software_website_display_area=''
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
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.website_url_placement, y_multiplier_integer,
                                               missing_software_display_area, True, False, True, False, 90,
                                               GUI_IO_util.open_TIPS_x_coordinate, "The widget, always disabled, displays all the external software yet to be installed on your machine.")
def openConfigFile():
    IO_files_util.openFile(window, GUI_IO_util.configPath + os.sep + config_filename)
    time.sleep(10) # wait 10 seconds to give enough time to save any changes to the csv config file

openInputConfigFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openConfigFile())
# place widget with hover-over info
x_coordinate_hover_over=1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               openInputConfigFile_button, False, False, True,False, 90,
                                               GUI_IO_util.open_reminders_x_coordinate, "Open csv config file 'NLP_setup_external_software_config.csv'\nYou can manually enter any external software installation path (in case of errors with the setup algorithm)")

software_download_lb = tk.Label(window,text='Software DOWNLOAD from web')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, software_download_lb, True)
software_download_var.set('')
# 'SENNA' was removed from SVO options; way too slow
# temporarily excluded '*'
software_download_menu = tk.OptionMenu(window, software_download_var, 'Stanford CoreNLP', 'Gephi','Google Earth Pro','Java (JDK)','MALLET','WordNet')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               software_download_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate, "Select the FREEWARE external software to be downloaded; the software website url will be displayed after selection. YOU CAN MAKE MULTIPLE SELECTIONS AND SAVE UPON CLOSING."
                                                                                      "\nYOU MUST BE CONNECTED TO THE INTERNET FOR DOWNLOADING SOFTWARE.\nThe software installation directory will be automatically displayed after selection so that it can be saved in the config file NLP_setup_external_software_config.csv when you CLOSE.")

software_website = tk.Label(height=1, anchor='w', text='Website url')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.website_url_placement,
                                               y_multiplier_integer, software_website, True)

software_website_url_var=tk.StringVar()
software_website_display_area = tk.Entry(width=GUI_IO_util.missing_software_display_area_width, state='disabled', textvariable=software_website_url_var)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.website_url_placement, y_multiplier_integer,
                                               software_website_display_area, True, False, True, False, 90,
                                               GUI_IO_util.watch_videos_x_coordinate, "The widget, always disabled, displays the download website of the external software selected in the 'Software download from web' dropdown menu.")

error = False

def openWebsite(software_website_url):
    if software_website_url!='':
        webbrowser.open_new_tab(software_website_url)
    else:
        mb.showwarning(title='Warning',
                   message='There is no external software website url.\n\nPlease, using the dropdown menu "Software DOWNLOAD" select the software website and try again.')

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
                message='There is no external software directory to open.\n\nPlease, using the dropdown menu "Software INSTALL" select the software and try again.')

software_install_lb = tk.Label(window,text='Software INSTALL on your machine')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, software_install_lb, True)
software_install_var.set('')
# temporarily excluded '*'
software_install_menu = tk.OptionMenu(window, software_install_var, 'Stanford CoreNLP', 'Gephi','Google Earth Pro','Java (JDK)','MALLET','WordNet')
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
                                               software_install_menu, True, False, True, False, 90,
                                               GUI_IO_util.labels_x_coordinate, "Select the external software to be installed after having downloaded it; the software installation directory will be displayed after selection."
                                                                                      "\nYOU CAN MAKE MULTIPLE SELECTIONS AND SAVE UPON CLOSING.\nThe software installation directory will be automatically saved in the config file NLP_setup_external_software_config.csv when you CLOSE.")


software_install_dir_var=tk.StringVar()
software_install_area = tk.Entry(width=GUI_IO_util.missing_software_display_area_width, state='disabled', textvariable=software_install_dir_var)
# place widget with hover-over info
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.website_url_placement, y_multiplier_integer,
                                               software_install_area, True, False, True, False, 90,
                                               GUI_IO_util.watch_videos_x_coordinate, "The widget, always disabled, displays the installation directory of the external software selected in the 'Software installation on your machine' dropdown menu.")

opensoftware_dir_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: openSoftwareDir(software_install_dir_var.get()))
# place widget with hover-over info
x_coordinate_hover_over=1150
y_multiplier_integer = GUI_IO_util.placeWidget(window,x_coordinate_hover_over, y_multiplier_integer,
                                               opensoftware_dir_button, False, False, True,False, 90,
                                               x_coordinate_hover_over-200, "Open external software directory")

def activate_software_download(*args):
    # global software_dir
    if software_download_var.get()=='' and software_install_var.get()=='':
        software_website_url_var.set('')
        software_website_display_area = ''
        software_install_dir_var.set('')
        software_install_area = ''
        return

    ###
    # existing_software_config = IO_libraries_util.get_existing_software_config()


    # software_download_var contains the external software names
    if software_download_var.get() != '':
        software_website_display_area = ''
        software_install_var.set('')
        software_name = software_download_var.get()
        # software_install_var contains the list of external software
        # this command will trigger install via .trace: software_install_var.set('')
        # get the installation directory and web download url
        software_dir, software_url, missing_software, error_found = IO_libraries_util.get_external_software_dir(
            scriptName, software_name,
            silent=True, only_check_missing=True, install_download='download')
        software_website_url_var.set(software_url)
        software_website_display_area=software_url
        download_message='###'
        software_dir, software_url, download_message = IO_libraries_util.external_software_download(scriptName,
                                                                                                    software_name,
                                                                                                    existing_software_config,
                                                                                                    False)
        if software_dir == None or software_dir == '':
            # software_install_var.set(software_download_var.get())  # set installation dropdown menu
            software_install_dir_var.set('Not installed')
            software_install_area = 'Not installed'  # software_install_dir_var.get()
        else:
            software_install_dir_var.set(software_dir)
            software_install_area=software_install_dir_var.get()
        # download_message=='' when the user opts NOT to install the software
        if software_dir!=None:
            if 'Java' in 'Java' in software_dir:
                return
        if download_message!='':
            silent = False
        else:
            silent = True

        activate_software_install('download', software_dir, software_url, missing_software, silent)
software_download_var.trace('w', activate_software_download)

def activate_software_install(download_install,software_dir, software_url, missing_software, silent=False):
    global existing_software_config, missing_software_list
    missing_software_list=[]
    if software_download_var.get()=='' and software_install_var.get()=='':
        software_website_url_var.set('')
        software_website_display_area = ''
        software_install_dir_var.set('')
        software_install_area = ''
        return

    # software_install_var contains the external software menu options
    if software_install_var.get()!='' or "download" in download_install:
        # avoid triggering the messages in external_software_install when you have downloaded the external software
        if software_install_var.get() != '':
            software_name = software_install_var.get()
        else:
            software_name = software_download_var.get()
        # get software_dir, software_url of software_name; must be silent to avoid message
        software_dir, software_url, missing_software, error_found = IO_libraries_util.get_external_software_dir(scriptName, software_name,
                                  silent=False, only_check_missing=True, install_download='install')
        # software_install_dir_var.set(software_dir)
        software_website_url_var.set(software_url)
        software_website_display_area = software_url
        if software_dir==None or software_dir=='':
            ###
            # if download_install=='install':
            #    software_install_var.set(software_download_var.get()) # set installation dropdown menu
            software_install_dir_var.set('Not installed')
            software_install_area = 'Not installed' # software_install_dir_var.get()
        else:
            software_install_dir_var.set(software_dir)
            software_install_area=software_install_dir_var.get()

        if software_install_var.get()!='':
            software_download_var.set('')

        # @@@
        # 9/1
        software_dir, existing_software_config = IO_libraries_util.external_software_install(scriptName,
                                                                                             software_name,
                                                                                             existing_software_config,
                                                                                             silent=False, errorFound=error_found)
        if software_dir==None or software_dir=='':
            software_install_dir_var.set('Not installed')
            software_install_area = 'Not installed' # software_install_dir_var.get()
            return
        software_install_dir_var.set(software_dir)
        software_install_area = software_install_dir_var.get()
        missing_software_string=missing_software_var.get()
        # convert comma-separated string to list [] to remove the installed softwarer from the list displayed in missing_software_display_area
        missing_software_list = missing_software_var.get().split(",")
        for index, x in enumerate(missing_software_list):
            if x.lstrip()==software_install_var.get().upper() or x.lstrip()==software_download_var.get().upper():
                missing_software_list.remove(x)
                break
        # software_download_var contains the list of external software
        # software_download_var.set('')
        new_missing_software_string=', '.join(missing_software_list)
        missing_software_var.set(new_missing_software_string.lstrip())
        if missing_software_var.get()=='':
            missing_software_var.set('All external software has been installed')
            mb.showwarning(title='Warning',message='All external software has been installed.')
        missing_software_display_area=new_missing_software_string.lstrip()
        # software_download_var contains the list of external software
        # if software_install_var.get()!='':
        #     software_download_var.set('')
    else:
        # software_download_var contains the external software download options
        if software_download_var.get() != '':
            # software_install_var.set(software_download_var.get())
            software_install_dir_var.set(software_dir)
            software_install_area = software_install_dir_var.get()
software_install_var.trace('w',lambda x, y, z: activate_software_install('',software_install_dir_var.get(),software_website_url_var.get(),'',silent=True))

def save_external_software_config():
    # existing_software_config is a global variable
    IO_libraries_util.save_software_config(existing_software_config, missing_software_var.get())

def close_GUI():
    import NLP_setup_update_util
    current_software_config = []
    for row in existing_software_config[1:]:  # skip header line
        current_software_config.append(row[1])
    # if missing_external_software_upon_entry!=missing_software_var.get():
    if existing_software_config_upon_entry!=current_software_config:
        answer = tk.messagebox.askyesno("Warning", 'You have made changes to the installed software.\n\nYou will lose your changes if you CLOSE without saving.\n\nWOULD YOU LIKE TO SAVE THE CHANGES MADE?')
        if answer:
            # existing_software_config is a global variable
            save_external_software_config()
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

videos_lookup = {'Setup external software':'https://www.youtube.com/watch?v=K8jUe_pKPPQ'}
videos_options='Setup external software'

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
                                  "Please, using the dropdown menu, select the FREEWARE external software that you wish to download.\n\nYou do not need to download/install all external software at once. Different algorithms in the NLP Suite require different packages (e.g., you cannot do any textual analysis based on Stanford CoreNLP without Stanford CoreNLP or produce any geographic maps without Google Earth Pro).\n\nStanford CoreNLP, Gephi, and MALLET (and some other NLP Suite scripts) require a copy of the FREEWARE Java downloaded and installed on your machine."+GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the FREEWARE external software that you wish to install on your machine after downloading it.\n\nGephi and Google Earth Pro on a Mac are installed in Applications."+GUI_IO_util.msg_Esc + GUI_IO_util.msg_save_uponClose)
    return y_multiplier_integer

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script provides a front-end GUI (Graphical User Interface) for setting up all the external packages used in the NLP Suite: Stanford CoreNLP, Gephi, Google Earth Pro, Java (JDK), MALLET, WordNet.\n\nTHESE ARE ALL FREEWARE PACKAGES.\n\nFailure to install a specific package will only affect the functions that rely on the package. Thus, for instance, you cannot visualize network graphs unless you download and install Gephi or visualize GIS maps without downloading and installing Google Earth Pro. More crucially, you cannot perform many of the key NLP tasks (e.g., parser, NER annotator, gender annotator, coreference resolution, SVO-Subject-Verb-Object-extractor without downloading and installing Stanford CoreNLP.\n\nWhen clicking the CLOSE button, the script will give the option to save the currently selected configuration IF different from the previously saved configuration."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, True, scriptName, False)

# when looping through all the software rows in the NLP_setup_external_software_config.csv config
#   the algorithm should be silent and just give a summary at the end
software_dir, software_url, missing_external_software, error_found = IO_libraries_util.get_external_software_dir(scriptName, software_download_var.get(), silent=True, only_check_missing=True)
if missing_external_software == '':
    missing_software_var.set('All external software has been installed')
    mb.showwarning(title='Warning',message='All external software has been installed.')
    error = False
else:
    # must be displayed at the end after the whole GUI has been laid
    error = True
    temp_missing_external_software=missing_external_software.replace('\n\n',', ')[:-2]
    missing_software_var.set(temp_missing_external_software)
    if not os.path.isfile(config_filename):
        mb.showwarning(title='External software installation error',
           message='The following external software needs to be downloaded and/or installed or some of the algorithms that require the software listed below will not run.\n\n' + str(missing_external_software) + \
                   '\nDOWNLOAD means to open the sotware website to get a copy of the software on your machine (you must be connected to the internet);' \
                   '\nINSTALL means to select the folder where you downloaded the software so that the NLP Suite knows where to find it.' \
                   '\n\nPlease, using the dropdown menu "Software DOWNLOAD", or "Software INSTALL" if you have already downloaded the listed software, and download or install the listed software.' \
                    '\n\nYou can download and/or install all external software separately, downloading all listed software first, ' \
                    'and later install all downloaded software (advised if internet connection time is a premium).' \
                    '\n\nYou can also download and/or install a specific external software required to run a specific algorithm (not all external software is required at all times).')
    else:
        mb.showwarning(title='External software installation error',
                   message='The following external software have not been found or have been found with errors (e.g., you may have moved or renamed the Stanford CoreNLP directory) in the config file NLP_setup_external_software_config.csv:\n\n' + str(missing_external_software) + '\n\nSome of the algorithms that require the software listed above will not run.\n\nPlease, using the dropdown menu "Software DOWNLOAD" and "Software INSTALL", select the software to download and/or install.')
    answer = tk.messagebox.askyesno("Warning", 'Do you want to watch the video on how to setup external software?')
    if answer:
        GUI_util.videos_dropdown_field.set('Setup external software')
        # GUI_util.watch_video(videos_lookup, scriptName)

missing_external_software_upon_entry=missing_software_var.get()

existing_software_config = IO_libraries_util.get_existing_software_config()
existing_software_config_upon_entry=[]
for row in existing_software_config[1:]:  # skip header line
    existing_software_config_upon_entry.append(row[1])

# to make sure the release version is updated even when users do not click on the CLOSE button
#   but on the Mac top-left red button or Windows top-right X button
GUI_util.window.protocol("WM_DELETE_WINDOW", close_GUI)
GUI_util.window.mainloop()
