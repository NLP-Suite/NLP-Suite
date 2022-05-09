#Written by Roberto Franzosi (help by Jack Hester, Feb 2019 and Karol Josh, March 2020)

import sys

# this will renew the SSL certificate indefinitely
# pip install pyOpenSSL
# pip install requests[security]
import requests

# import GUI_util
import IO_libraries_util

# Creates a circular dependent imports
# if IO_libraries_util.install_all_packages(GUI_util.window, "GUI_util", ['tkinter', 'os', 'subprocess', 'PIL']) == False:
#     sys.exit(0)

import tkinter as tk
window = tk.Tk()
from sys import platform

import os
import tkinter.messagebox as mb
import inspect
from subprocess import call
# import webbrowser
# import atexit

import config_util
import reminders_util
import videos_util
import TIPS_util
import GUI_IO_util
import IO_files_util
import IO_internet_util

y_multiplier_integer = 1
noLicenceError=False

# gather GUI info from external file
# def set_window(size, label, config, config_option):
def set_window(size, label, config, config_option):

    global GUI_size, GUI_label, config_filename, config_input_output_numeric_options
    GUI_size, GUI_label, config_filename, config_input_output_numeric_options = size, label, config, config_option
    # window.geometry(GUI_size)
    # window.title(GUI_label)
    window.geometry(size)
    window.title(label)

# insert side bar
# To connect a vertical scrollbar to such a widget, you have to do two things:
# Set the widget’s yscrollcommand callbacks to the set method of the scrollbar.
# Set the scrollbar’s command to the yview method of the widget.
# solution? https://gist.github.com/novel-yet-trivial/3eddfce704db3082e38c84664fc1fdf8
# NOT THIS SIMPLE; SCROLL BAR DOES NOT SCROLL
# https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
# scrollbar = tk.Scrollbar(window)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# listbox = tk.Listbox(window, yscrollcommand=scrollbar.set)
# for line in range(1000):
# 	# listbox.insert(tk.END, "This is line number " + str(line))
# 	listbox.insert(tk.END)
# #listbox.pack(side=tk.LEFT, fill=tk.BOTH)
# scrollbar.config(command=listbox.yview)

def clear(e):
    charts_dropdown_field.set('Excel')
    videos_dropdown_field.set('Watch videos')
    tips_dropdown_field.set('Open TIPS files')
    reminders_dropdown_field.set('Open reminders')
window.bind("<Escape>", clear)


#IO widgets

IO_setup_menu_var = tk.StringVar()
IO_setup_menu = tk.OptionMenu(window, IO_setup_menu_var, 'Default I/O configuration', 'GUI-specific I/O configuration')
IO_setup_var = tk.StringVar()

select_input_file_button=tk.Button()
select_input_main_dir_button=tk.Button()
select_input_secondary_dir_button=tk.Button()
select_output_dir_button=tk.Button()

inputFilename=tk.StringVar()
inputFilename.set('')
input_main_dir_path=tk.StringVar()
input_main_dir_path.set('')
input_secondary_dir_path=tk.StringVar()
input_secondary_dir_path.set('')
output_dir_path=tk.StringVar()
output_dir_path.set('')

release_version_var=tk.StringVar()
GitHub_release_version_var=tk.StringVar()

open_csv_output_checkbox = tk.IntVar()
create_Excel_chart_output_checkbox = tk.IntVar()
charts_dropdown_field = tk.StringVar()

videos_dropdown_field = tk.StringVar()
tips_dropdown_field = tk.StringVar()
reminders_dropdown_field = tk.StringVar()

run_button = tk.Button(window, text='RUN', width=10,height=2)

# license agreement GUI
agreement_checkbox_var=tk.IntVar()
agreement_checkbox = tk.Checkbutton()

# Trace and update the checkbox configuration to inform user of selection
label = None
checkbox = None
onText = None
offText = None
# answer = True when you do not wish to enter I/O information on the IO_setup_main GUI; changed below
answer = True
run_button_state='disabled'

# tracer when the checkbox has a separate label widget (label_local) attached to the checkbox widget (checkbox_local)
#For the labels to change the text with the ON/OFF value of the checkbox the command=lambda must be included in the definition of the tk.button
#	For example (see the example in this script):
#	create_Excel_chart_output_label = tk.Checkbutton(window, variable=create_Excel_chart_output_checkbox, onvalue=1, offvalue=0,command=lambda: trace_checkbox(create_Excel_chart_output_label, create_Excel_chart_output_checkbox, "Automatically compute Excel charts", "NOT automatically compute Excel charts"))
#	The next line must always be included to dsplay te label the first time the GUI is opened
#	create_Excel_chart_output_label.configure(text="Automatically open output Excel charts for inspection")

def trace_checkbox(label_local, checkbox_local, local_onText, local_offText):
    if checkbox_local.get() == 1:
        label_local.config(text=local_onText)
    else:
        label_local.config(text=local_offText)

# tracer when the checkbox has a separate label widget (label_local) attached to the checkbox widget (checkbox_local)
# an exampple is in geocoder_Google_Earth and file_handling; here are the lines from file_handling
# 	matching_checkbox = tk.Checkbutton(window, variable=matching_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(matching_var, matching_checkbox, "Exact match", "Partial match"))
# 	matching_checkbox.config(text="Exact match",state='disabled')
# checkbox_var and checkbox_text are the var and checkbox widgets
# onText, offText the texts to be displayed on 1 or 0

#For the labels to change the text with the ON/OFF value of the checkbox the command=lambda must be included in the definition of the tk.button
#	For example (see the example in geocoder_Google_eart_GUI or in WordNet_GUI):
#	geoCodedFile_checkbox = tk.Checkbutton(window, variable=geoCodedFile_var, onvalue=1, offvalue=0, command=lambda: GUI_util.trace_checkbox_NoLabel(geoCodedFile_var, geoCodedFile_checkbox, "File contains geocoded data with Latitude and Longitude", "File does NOT contain geocoded data with Latitude and Longitude"))
#	The next line must always be included to display the label the first time the GUI is opened
#	geoCodedFile_checkbox.config(text="File does NOT contain geocoded data with Latitude and Longitude")

def trace_checkbox_NoLabel(checkbox_var, checkbox_text, onText, offText):
    if checkbox_var.get() == 1:
        checkbox_text.config(text=onText)
    else:
        checkbox_text.config(text=offText)


# designed by Jamie Martin
# font Gotham for NLP
# RGB red is #b10a0a

def display_logo():
    # Necessary to avoid creating a circular dependent import
    from IO_libraries_util import install_all_packages
    if install_all_packages(window, "GUI_util", ['tkinter', 'os', 'subprocess', 'PIL']) == False:
        sys.exit(0)

    from PIL import Image, ImageTk
    # https://stackoverflow.com/questions/17504570/creating-simply-image-gallery-in-python-tkinter-pil
    image_list = [GUI_IO_util.image_libPath + os.sep + "logo.png"]
    for x in image_list:
        img = ImageTk.PhotoImage(Image.open(x).resize((85,50), Image.ANTIALIAS))
        logo = tk.Label(window, width=85, height=50, anchor='nw', image=img)
        logo.image = img
        # the logo has some white spaces to its left; better cutting this so that it can be aligned with HELP? buttons
        # -12 works for Windows; must be checked for Mac
        if platform == "win32":
            offset=12
        else:
            offset=12
        logo.place(x=GUI_IO_util.get_help_button_x_coordinate()-offset, y=10)


# define the variable local_release_version
local_release_version = '0.0.0' #stored in lib\release_version.txt

def get_GitHub_release(silent = False):
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("GUI_util.py (Function Automatic check for NLP Suite newest release version on GitHub)"):
        return '0.0.0'
    release_url = 'https://raw.githubusercontent.com/NLP-Suite/NLP-Suite/current-stable/lib/release_version.txt'
    try:
        GitHub_newest_release = requests.get(release_url).text
        GitHub_release_version_var.set(GitHub_newest_release)
    except:
        if not silent:
            mb.showwarning(title='Internet connection error', message="The attempt to connect to GitHub failed.\n\nIt is not possible to check the latest release of the NLP Suite at this time. You can continue run your current release and try again later.")
        GitHub_newest_release = '0.0.0'
    return GitHub_newest_release

def check_GitHub_release(local_release_version: str, silent = False):
    GitHub_newest_release = get_GitHub_release()
    if GitHub_newest_release == None or GitHub_newest_release == '0.0.0': # when not connected to internet
        return
    # local_release_version = '2.3.1' # line used for testing; should be LOWER than the version on GitHub
    # split the text string of release version (e.g., 1.5.9) into three parts separated by .
    local_release_version_parts=[local_release_version[i:i + 1] for i in range(0, len(local_release_version), 2)]
    GitHub_release_version_parts=[GitHub_newest_release[i:i + 1] for i in range(0, len(GitHub_newest_release), 2)]
    old_version = False
    # check numbers
    if int(local_release_version_parts[0]) > int(GitHub_release_version_parts[0]):
        return
    if int(local_release_version_parts[0])<int(GitHub_release_version_parts[0]):
        old_version = True
    else:
        # if the first parts are the same, check the second part
        if int(local_release_version_parts[1])>int(GitHub_release_version_parts[1]):
            return
        if int(local_release_version_parts[1]) < int(GitHub_release_version_parts[1]):
            old_version = True
        else:
            # if the second parts are the same, check the third part
            if int(local_release_version_parts[2]) < int(GitHub_release_version_parts[2]):
                old_version = True
            else:
                return
    if 'Not Found' not in GitHub_newest_release and old_version: #GitHub_newest_release != local_release_version:
        # update is carried out in NLP_setup_update_util.py
        result = mb.askyesno("NLP Suite Outdated",
                    "You are running the NLP Suite release version " + str(local_release_version) + ", an OLD version." +
                    "\n\nA NEW version of the NLP Suite has been released on GitHub: " + str(GitHub_newest_release) + "." +
                    "\n\nThe OLD and NEW release versions are displayed on the top left-hand corner of the GUI, local OLD version left of \ GitHUB new version right of \ (0.0.0 is displayed when you are not connected to the internet to access GitHub)." +
                    "\n\nTo update to the newer release, EXIT the NLP Suite NOW by clicking on the CLOSE button and fire up the NLP Suite again.\n\nThe NLP Suite is automatically updated every time you exit the NLP Suite and fire it up again." +
                    "\n\nThe update features of the NLP Suite rely on Git. Please download Git at this link https://git-scm.com/downloads, if it hasn’t been installed already." +
                    "\n\nWOULD YOU LIKE TO SEE WHAT IS NEW IN THE RELEASE VERSION " + str(GitHub_newest_release) + "?")
        if result:
            url = "https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Release-History"
            IO_libraries_util.open_url('NLP Suite GitHub', url)
            # webbrowser.open_new_tab("https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Release-History")

def display_release():
    # first digit for major upgrades
    # second digit for new features
    # third digit for bug fixes and minor changes to current version
    # must also change the Release version in readMe on GitHub

    global local_release_version
    release_version_file = GUI_IO_util.libPath + os.sep + "release_version.txt"

    if os.path.isfile(release_version_file):
        with open(release_version_file,'r') as file:
            local_release_version = file.read()

    release_version_var.set(local_release_version)

    y_multiplier_integer=-.7

    # get the release version available on GitHub
    GitHub_newest_release = get_GitHub_release()
    release_display = str(release_version_var.get()) + "/" + str(GitHub_newest_release)
    release_lb = tk.Label(window, text='Release ' + release_display,foreground="red")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_help_button_x_coordinate(),
                                                   y_multiplier_integer, release_lb, True)
    # check and display a possible warning message
    if GitHub_newest_release != '0.0.0':
        check_GitHub_release(local_release_version)
    else:
        mb.showwarning(title='GitHub release version',message="The GitHub release version is displayed on the top left-hand corner of the GUI as 0.0.0.\n\nWithout internet the newest release available on GitHub cannnot be retrieved.")
    return local_release_version, GitHub_newest_release

def selectFile_set_options(window, IsInputFile,checkCoNLL,inputFilename,input_main_dir_path,title,fileType,extension):
    currentFilename=inputFilename.get()
    if len(currentFilename)>0:
        initialFolder=os.path.dirname(inputFilename.get())
    else:
        initialFolder=''
    #get the file
    if IsInputFile==True:
        filename = IO_files_util.selectFile(window, IsInputFile, checkCoNLL, title, fileType, extension, None, initialFolder)
    else:
        filename = IO_files_util.selectFile(window, IsInputFile, checkCoNLL, title, fileType, extension, outputFilename, None, initialFolder)
    if len(filename)==0:
        return
        # filename=currentFilename
    else:
        inputFilename.set(filename)
        input_main_dir_path.set('')

#changeVar is the name of the IO FIELD (.get()) that needs to be displayed
#changeVar1 is the name of the IO BUTTON that needs to be disabled in the case of mutuallyexclusive options
#title is the name that will appear when selecting the directory, e.g., "Select Stanford CoreNLP directory"
def selectDirectory_set_options(window, input_main_dir_path,output_dir_path,title,inputMainDir=False):
    initialFolder = ''
    if 'INPUT' in title:
        if inputMainDir:
            if len(input_main_dir_path.get())>0:
                initialFolder=input_main_dir_path.get()
        else:
            if len(input_secondary_dir_path.get()) > 0:
                initialFolder = input_secondary_dir_path.get()
    else:
        if len(output_dir_path.get()) > 0:
            initialFolder = output_dir_path.get()
    #get the directory
    directoryName=IO_files_util.selectDirectory(title, initialFolder)
    if directoryName=='':
        directoryName=initialFolder
    if 'INPUT' in title:
        if inputMainDir==True:
            # if there is no filename it would give an error
            try:
                inputFilename.set('') # inputFilename
            except:
                pass
            input_main_dir_path.set(directoryName)
        else:
            input_secondary_dir_path.set(directoryName)
    else:
        if (GUI_IO_util.NLPPath + '\\') in directoryName.replace('/','\\'):
            mb.showwarning(title='Warning',
                           message="You have selected an output directory for your scripts that is inside the NLP Suite directory.\n\nPlease, select a different directory and try again.")
            return
        output_dir_path.set(directoryName)


# configuration_type is the value displayed on the GUI: Default I/O configuration,GUI-specific I/O configuration
def display_IO_setup(window,IO_setup_display_brief,config_filename,config_input_output_numeric_options,scriptName,silent,*args):
    error = False
    fileName = ''
    dirName = ''
    y_multiplier_integer=1
    # temp_config_filename is used to check the existence of the default or GUI specific config
    if 'Default' in IO_setup_menu_var.get():
        temp_config_filename='default_config.csv'
    else:
        temp_config_filename=config_filename
    silent=False
    config_input_output_alphabetic_options, config_input_output_full_options, missingIO=config_util.read_config_file(temp_config_filename, config_input_output_numeric_options)

    # the full options must always be displayed, even when the brief option is selected;
    #   the reason is that the IO widgets filename, inputDir, and outputDir are used to check missing options and activate the RUN button

    # the next two variables are used in setup display brief
    inputDirName = ''
    outputDirName = ''

    # INPUT file name -----------------------------------------------------------------------------------

    if config_input_output_alphabetic_options[0]=='': # INPUT filename
        inputFilename.set('')
    else:
        if error==False:
            error, fileName = config_util.checkConfigFileExists(temp_config_filename, config_input_output_alphabetic_options[0], 'INPUT')
        inputFilename.set(fileName)

    # -----------------------------------------------------------------------------------
    # INPUT main directory

    if config_input_output_alphabetic_options[1]=='': # INPUT main directory
        input_main_dir_path.set('')
    else:
        if error==False:
            error, dirName = config_util.checkConfigDirExists(temp_config_filename, config_input_output_alphabetic_options[1], 'INPUT')
        input_main_dir_path.set(dirName)

    # -----------------------------------------------------------------------------------
    # INPUT secondary directory

    if config_input_output_alphabetic_options[2]=='': # INPUT secondary directory
        input_secondary_dir_path.set('')
    else:
        if error==False:
            error, dirName = config_util.checkConfigDirExists(temp_config_filename, config_input_output_alphabetic_options[2], 'INPUT')
        input_secondary_dir_path.set(dirName)

    # -----------------------------------------------------------------------------------
    # OUTPUT directory

    if config_input_output_alphabetic_options[3]=='': # OUTPUT directory
        outputDirName = ''
        output_dir_path.set('')
    else:
        if error==False:
            error, dirName = config_util.checkConfigDirExists(temp_config_filename, config_input_output_alphabetic_options[3], 'OUTPUT')
        output_dir_path.set(dirName)

    # display I/O info briefly
    if IO_setup_display_brief == True and config_input_output_numeric_options!=[0,0,0,0]:
        IO_setup_display_string = ''
        # check filename
        if str(config_input_output_alphabetic_options[0])!='':
            #head is path, tail is filename
            head, tail = os.path.split(config_input_output_alphabetic_options[0])
            IO_setup_display_string = "INPUT FILE: " + str(tail)
        else:
            # check input directory
            if str(config_input_output_alphabetic_options[1]) != '':
                inputDirName = config_input_output_alphabetic_options[1]
                IO_setup_display_string = "INPUT DIR: " + str(inputDirName)

        # both filename [1] and input Dir [2] are empty
        if (config_input_output_alphabetic_options[0] == '') and (
                config_input_output_alphabetic_options[1] == ''):
            IO_setup_display_string = "INPUT FILE:\nINPUT DIR:"

        outputDirName = config_input_output_alphabetic_options[3]

        IO_setup_display_string = IO_setup_display_string + "\nOUTPUT DIR: " + str(outputDirName)
        IO_setup_brief_display_area = tk.Text(width=60, height=2)
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+250,
                                                       0, IO_setup_brief_display_area)
        IO_setup_brief_display_area.delete(0.1, tk.END)
        IO_setup_var.set(IO_setup_display_string)
        IO_setup_brief_display_area.insert("end", IO_setup_display_string)
        # IO_setup_brief_display_area.pack(side=tk.LEFT)
        IO_setup_brief_display_area.configure(state='disabled')
    # answer = True when you do not wish to enter I/O information on the IO_setup_main GUI
    answer = activateRunButton(temp_config_filename,IO_setup_display_brief,scriptName,silent)
    if not answer:
        return
    if run_button_state=='disabled':
        setup_IO_configuration_options(IO_setup_display_brief,scriptName,silent)

# config_filename can be either the Default value or the GUI_specific value depending on IO_setup_menu_var.get()
def activateRunButton(config_filename,IO_setup_display_brief,scriptName,silent = False):
    global run_button_state, answer
    if config_input_output_numeric_options == [0,0,0,0]:
        run_button_state = 'disabled'
        run_button.configure(state=run_button_state)
        return
    # answer = True when you do not wish to enter I/O information on the IO_setup_main GUI
    # if answer:
    # there is no RUN button when setting up IO information so the call to check_missingIO should be silent
    config_input_output_alphabetic_options, config_input_output_full_options, missingIO=config_util.read_config_file(config_filename, config_input_output_numeric_options)
    run_button_state, answer = config_util.check_missingIO(window,missingIO,config_filename, scriptName, IO_setup_display_brief, silent)
    run_button.configure(state=run_button_state)
    return answer

#GUI top widgets ALL IO widgets
#	 input filename, input dir, secondary input dir, output dir
#__________________________________________________________________________________________________________________

def IO_config_setup_brief(window, y_multiplier_integer,scriptName, silent):
    IO_setup_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width,text='Setup INPUT/OUTPUT configuration',command=lambda: setup_IO_configuration_options(True,scriptName, silent))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),
                                                   y_multiplier_integer,
                                                   IO_setup_button, True)

    IO_setup_menu_var.set("Default I/O configuration")
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate(),
                                                   y_multiplier_integer,
                                                   IO_setup_menu,True)

    # setup buttons to open an input file, an input directory, an output directory, and a csv config file

    # setup a button to open an input file
    openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                     command=lambda: IO_files_util.openFile(window, inputFilename.get()))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+GUI_IO_util.open_file_button_brief, y_multiplier_integer,
                                                   openInputFile_button, True)

    def open_directory():
        open_dir = input_main_dir_path.get()
        if input_main_dir_path.get()!='':
            open_dir= input_main_dir_path.get()
        if inputFilename.get()!='':
            head, tail = os.path.split(inputFilename.get())
            open_dir = head
        IO_files_util.openExplorer(window, open_dir)

    # setup a button to open Windows Explorer on the selected INPUT directory
    openInputDirectory_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                     command=lambda: open_directory())
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+GUI_IO_util.open_inputDir_button_brief, y_multiplier_integer,
                                                   openInputDirectory_button, True)

    # setup a button to open Windows Explorer on the selected OUTPUT directory
    openOutputDirectory_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                     command=lambda: IO_files_util.openExplorer(window, output_dir_path.get()))
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+GUI_IO_util.open_outputDir_button_brief, y_multiplier_integer,
                                                   openOutputDirectory_button, True)

    def openConfigFile():
        if 'Default' in IO_setup_menu_var.get():  # GUI_util.GUI_util.IO_setup_menu_var.get()
            temp_config_filename = 'default_config.csv'
        else:
            temp_config_filename = config_filename
        IO_files_util.openFile(window, GUI_IO_util.configPath + os.sep + temp_config_filename)

    openInputConfigFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                     command=lambda: openConfigFile())
    y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_open_file_directory_coordinate()+GUI_IO_util.open_config_file_button_brief, y_multiplier_integer,
                                                   openInputConfigFile_button, True)

def IO_config_setup_full (window, y_multiplier_integer):
    if 'Default' in IO_setup_menu_var.get():
        config_input_output_alphabetic_options, config_input_output_full_options, missingIO=config_util.read_config_file('default_config.csv', config_input_output_numeric_options)
    else:
        config_input_output_alphabetic_options, config_input_output_full_options, missingIO=config_util.read_config_file(config_filename, config_input_output_numeric_options)

    # global so that they are recognized wherever they are used (e.g., select_input_secondary_dir_button in shape_of_stories_GUI)
    global select_input_file_button, select_input_main_dir_button, \
        select_input_secondary_dir_button, select_output_dir_button
    if config_input_output_numeric_options[0]>0:
        # buttons are set to normal or disabled in selectFile_set_options
        if config_input_output_numeric_options[0]==1: #single CoNLL file
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CoNLL table', command=lambda: selectFile_set_options(window,True,True,inputFilename,input_main_dir_path,'Select INPUT CoNLL table (csv file)',[('CoNLL csv file','.csv')],".csv"))
        elif config_input_output_numeric_options[0]==2: #single txt file:
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT TXT file', command=lambda: selectFile_set_options(window,True,False,inputFilename,input_main_dir_path,'Select INPUT TXT file',[('text file','.txt')],".txt"))
        elif config_input_output_numeric_options[0]==3: #single csv file:
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT csv file', command=lambda: selectFile_set_options(window,True,False,inputFilename,input_main_dir_path,'Select INPUT csv file',[('csv file','.csv')],".csv"))
        if config_input_output_numeric_options[0]==4: #any type file (used in NLP.py)
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: selectFile_set_options(window,True,False,inputFilename,input_main_dir_path,'Select INPUT file (any file type: pdf, docx, html, txt, csv, conll); switch extension type below near File name:',[("txt file","*.txt"),("csv file","*.csv"),("pdf file","*.pdf"),("docx file","*.docx"),("html file","*.html"),("CoNLL table","*.conll")], "*.*"))
        if config_input_output_numeric_options[0]==5: #txt/html
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: selectFile_set_options(window,True,False,inputFilename,input_main_dir_path,'Select INPUT file (txt, html); switch extension type below near File name:',[("txt file","*.txt"),("html file","*.html")], "*.*"))
        if config_input_output_numeric_options[0]==6: #txt/csv
            # buttons are set to normal or disabled in selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: selectFile_set_options(window,True,False,inputFilename,input_main_dir_path,'Select INPUT file (txt, csv); switch extension type below near File name:',[("txt file","*.txt"),("csv file","*.csv")], "*.*"))

        # place the INPUT file widget
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_file_button)
        tk.Label(window, textvariable=inputFilename).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input file
        current_y_multiplier_integer=y_multiplier_integer-1
        openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, inputFilename.get()))
        openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer)

    #primary INPUT directory ______________________________________________
    if config_input_output_numeric_options[1]==1: #directory input
        # buttons are set to normal or disabled in selectFile_set_options
        select_input_main_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT files directory',  command = lambda: selectDirectory_set_options(window,input_main_dir_path,output_dir_path,"Select INPUT files directory",True))
        # select_input_main_dir_button.config(state="normal")

        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_main_dir_button)
        tk.Label(window, textvariable=input_main_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, input_main_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer)

    #secondary INPUT directory ______________________________________________
    if config_input_output_numeric_options[2]==1: #secondary directory input
        # buttons are set to normal or disabled in selectFile_set_options
        select_input_secondary_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT secondary directory',  command=lambda: selectDirectory_set_options(window,input_main_dir_path, input_secondary_dir_path,"Select INPUT secondary TXT directory"))

        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_secondary_dir_button)
        tk.Label(window, textvariable=input_secondary_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer3=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, input_secondary_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer3)

    #OUTPUT directory ______________________________________________
    if config_input_output_numeric_options[3]==1: #output directory
        # buttons are set to normal or disabled in selectFile_set_options
        select_output_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select OUTPUT files directory',  command=lambda: selectDirectory_set_options(window,input_main_dir_path,output_dir_path,"Select OUTPUT files directory"))

        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_output_dir_button)
        tk.Label(window, textvariable=output_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer4=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, output_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer4)

def setup_IO_configuration_options(IO_setup_display_brief,scriptName,silent):
    if 'Default' in IO_setup_menu_var.get(): # GUI_util.GUI_util.IO_setup_menu_var.get()
        temp_config_filename = 'default_config.csv'
    else:
        temp_config_filename=config_filename
    # 2 arguments are passed to python IO_setup_main.py:
    #   1. config_input_output_numeric_options (i.e., the list of GUI specific IO options setup in every _main [1,0,0,1])
    #       when passing a default config, this list will be checked in IO_setup_main against the GUI specific IO list
    #       if you have a specific GUI requiring only input Dir, rather than filename, and the default option specifies an inputfile
    #       a warning will be raised
    #   2. temp_config_filename, either as default or GUI-specific config
    # same call to IO_setup_main.py in NLP_menu_main
    if not 'IO_setup_main' in scriptName:
        call("python IO_setup_main.py --config_option " + str(config_input_output_numeric_options).replace('[', '"').replace(']', '"') + " --config_filename " + temp_config_filename, shell=True)
        # must pass config_filename and not temp_config_filename since the value is recomputed in display_IO_setup
        display_IO_setup(window, IO_setup_display_brief, config_filename, config_input_output_numeric_options, scriptName,silent)

def display_about_release_team_cite_buttons(scriptName):
    if 'NLP_welcome_main' in scriptName or 'NLP_menu_main' in scriptName:
        if 'NLP_welcome_main' in scriptName:
            y_multiplier_integer = 1.7
        else:
            y_multiplier_integer = 0
        about_button = tk.Button(window, text='About', width=15, height=1, foreground="red",
                                command=lambda: GUI_IO_util.about())
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.about_button_x_coordinate, y_multiplier_integer,
                                                       about_button, True)

        release_history_button = tk.Button(window, text='Release history', width=15, height=1, foreground='red',
                                           command=lambda: GUI_IO_util.release_history())
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.release_history_button_x_coordinate, y_multiplier_integer,
                                                       release_history_button, True)

        team_button = tk.Button(window, text='NLP Suite team', width=15, height=1, foreground="red",
                                command=lambda: GUI_IO_util.list_team())
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.team_button_x_coordinate, y_multiplier_integer,
                                                       team_button, True)

        cite_button = tk.Button(window, text='How to cite', width=15, height=1, foreground="red",
                                command=lambda: GUI_IO_util.cite_NLP())
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.cite_button_x_coordinate, y_multiplier_integer,
                                                       cite_button)

# scriptName is typically blank; it is the name of the calling script; for now it is only used by IO_setup_main
#   it can be used for handling GUIs with special treatment (e.g., IO_setup_main which does not have a RUN button)
#   for consistency, it should also be used for NLP_main that for now relies on a previous approach based on config (i.e., NLP_config.csv)
# silent is set to True in those GUIs where the selected default I/O configuration does not confirm to the expected input
#   For example, you need a csv file but the default is a Directory, e.g., data_manager_main
def GUI_top(config_input_output_numeric_options,config_filename, IO_setup_display_brief,scriptName='',silent=False):
    import IO_libraries_util
    from PIL import Image, ImageTk

    # global so that they are recognized wherever they are used (e.g., select_input_secondary_dir_button in shape_of_stories_GUI)
    global select_input_file_button, select_input_main_dir_button, select_input_secondary_dir_button, select_output_dir_button
    global config_input_output_alphabetic_options

    # No top help lines displayed when opening the license agreement GUI
    if config_filename!='license_config.csv':

        intro = tk.Label(window, text=GUI_IO_util.introduction_main)
        intro.pack()
        display_logo()
        # although the release version appears in the top part of the GUI,
        #   it is run at the end otherwise a message will be displayed with an incomplete GUI
        # display_release()
        display_about_release_team_cite_buttons(scriptName)

    y_multiplier_integer=0

    #__________________________________________________________________________________________________________________
    # INPUT options widgets
    # config_input_output_alphabetic_options contains the .get() value for each IO widget
    #	e.g.,  ['C:/Program Files (x86)/NLP_backup/WordNet-3.0', '', '', '', '', 'C:/Program Files (x86)/NLP_backup/Output']
    # config_input_output_alphabetic_options will contain the specific user SAVED values for the script

    # there should only be one case of
    #   config_input_output_numeric_options = [0,0,0,0]
    #   in NLP_GUI (NLP_config.csv) since no IO lines are displayed

    #file input file option ______________________________________________
    #	1 for CoNLL file,
    #	2 for txt file,
    #	3 for csv file,
    #	4 for any type file
    #	5 for txt, html (used in annotator)
    #	6 for txt, csv (used in SVO)

    if not 'NLP_menu_main' in scriptName and config_input_output_numeric_options!=[0,0,0,0]:
        if not IO_setup_display_brief:
            IO_config_setup_full(window, y_multiplier_integer)
        else:
            IO_config_setup_brief(window, y_multiplier_integer,scriptName,silent)

    old_license_file=os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-1.0.txt')
    if os.path.isfile(old_license_file):
        # rename the file to the new standard
        os.rename(old_license_file, os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-Suite-1.0.txt'))

    if (os.path.isfile(os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-Suite-1.0.txt')) and (IO_libraries_util.check_inputPythonJavaProgramFile('license_GUI.py'))):
        if not os.path.isfile(GUI_IO_util.configPath + os.sep + 'license_config.csv'):
            call("python " + "license_GUI.py", shell=True)
    else:
        # The error message is displayed at the end of the script after the whole GUI has been displayed
        global noLicenceError
        noLicenceError=True

#__________________________________________________________________________________________________________________
# GUI bottom buttons widgets (ReadMe, Videos, TIPS, RUN, CLOSE)
# silent is set to True in those GUIs where the selected default I/O configuration does not confirm to the expected input
#   For example, you need a csv file but the default is a Directory, e.g., data_manager_main
def GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command,
               videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief,scriptName='', silent=False):

    # No bottom lines (README, TIPS, RUN, CLOSE) displayed when opening the license agreement GUI
    if config_filename=='license_config.csv':
        return
    reminder_options=[]

    # for those GUIs (e.g., style analysis) that simply
    #   display options for opening more specialized GUIs
    #   do NOT display the next two sets of widgets
    #   since there is no output to display
    # if config_input_output_numeric_options!=[0,0,0,0] and config_filename!='default_config.csv':

    # "IO_setup_main" has no Excel display
    # GUIs that serve only as frontend GUIs for more specialized GUIs should NOT display Open ooutput and Excel tickboxes
    #   that is the case, for instance, in narrative_analysis_main
    #   in this case config_input_output_numeric_options = [0,0,0,0]
    if config_input_output_numeric_options!= [0,0,0,0] and \
            not 'NLP_menu_main' in scriptName and \
            not "IO_setup_main" in scriptName:
        #open output csv files widget defined above since it is used earlier
        open_csv_output_label = tk.Checkbutton(window, variable=open_csv_output_checkbox, onvalue=1, offvalue=0, command=lambda: trace_checkbox(open_csv_output_label, open_csv_output_checkbox, "Automatically open ALL output files", "Do NOT automatically open ALL output files"))
        open_csv_output_label.configure(text="Automatically open ALL output files")
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),
                                                       y_multiplier_integer,
                                                       open_csv_output_label,True,False,False)
        # open_csv_output_label.place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
        open_csv_output_checkbox.set(1)

        #creat Excel chart files widget defined above since it is used earlier
        create_Excel_chart_output_label = tk.Checkbutton(window, variable=create_Excel_chart_output_checkbox, onvalue=1, offvalue=0,command=lambda: trace_checkbox(create_Excel_chart_output_label, create_Excel_chart_output_checkbox, "Automatically compute charts", "Do NOT automatically compute charts"))
        create_Excel_chart_output_label.configure(text="Automatically compute chart(s)")
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+380,
                                                       y_multiplier_integer,
                                                       create_Excel_chart_output_label,True,False,False)

        # create_Excel_chart_output_label.place(x=GUI_IO_util.get_labels_x_coordinate()+380, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
        create_Excel_chart_output_checkbox.set(1)
        # y_multiplier_integer=y_multiplier_integer+1
        charts_options = ['Excel','Python Plotly']
        charts_dropdown_field.set('Excel')
        charts_menu_lb = tk.OptionMenu(window,charts_dropdown_field,*charts_options)
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+620,
                                                       y_multiplier_integer,
                                                       charts_menu_lb,False,False,False)

    def warning_message(*args):
        if charts_dropdown_field.get()!='Excel':
            mb.showwarning(title='Warning',
                           message="The 'Python Plotly' option to draw charts is not available yet; it is under development. Sorry!")
            charts_dropdown_field.set('Excel')
    charts_dropdown_field.trace('w',warning_message)

    # readme_button = tk.Button(window, text='Read Me',command=readMe_command,width=10,height=2)
    readme_button = tk.Button(window, text='Read Me',command=readMe_command,width=10,height=2)
    GUI_IO_util.placeWidget(GUI_IO_util.read_button_x_coordinate,y_multiplier_integer,readme_button,True,False,True)

    videos_dropdown_field.set('Watch videos')
    if len(videos_lookup)==1:
        if videos_options == "No videos available":
            videos_menu_lb = tk.OptionMenu(window,videos_dropdown_field,videos_options)
        else:
            videos_menu_lb = tk.OptionMenu(window, videos_dropdown_field, videos_options)
            videos_menu_lb.configure(foreground="red")
    else:
        videos_menu_lb = tk.OptionMenu(window,videos_dropdown_field,*videos_options)
        videos_menu_lb.configure(foreground="red")
    videos_menu_lb.place(x=GUI_IO_util.watch_videos_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    videos_util.trace_open_videos(videos_dropdown_field, videos_menu_lb, videos_lookup)

    tips_dropdown_field.set('Open TIPS files')
    if len(TIPS_lookup)==1:
        if TIPS_options == "No TIPS available":
            tips_menu_lb = tk.OptionMenu(window,tips_dropdown_field,TIPS_options)
        else:
            tips_menu_lb = tk.OptionMenu(window, tips_dropdown_field, TIPS_options)
            tips_menu_lb.configure(foreground="red")
    else:
        tips_menu_lb = tk.OptionMenu(window,tips_dropdown_field,*TIPS_options)
        tips_menu_lb.configure(foreground="red")
    tips_menu_lb.place(x=GUI_IO_util.open_TIPS_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    TIPS_util.trace_open_tips(tips_dropdown_field,tips_menu_lb,TIPS_lookup)

    reminders_util.checkReminder('*',
                                 reminders_util.title_options_NLP_Suite_reminders,
                                 reminders_util.message_NLP_Suite_reminders,
                                 True)

    routine = config_filename[:-len('_config.csv')]
    # get the list of titles available for a given GUI
    if 'NLP_menu_main' in scriptName:
        # config_filename='NLP_config.csv'
        config_filename = 'default_config.csv'
    reminder_options = reminders_util.getReminders_list(config_filename, True)
    # None returned for a faulty reminders.csv
    reminders_error = False
    if reminder_options==None:
        reminders_error=True
        reminder_options = ["No Reminders available"]

    # reminders content for specific GUIs are set in the csv file reminders
    # called from any GUI
    reminders_dropdown_field.set('Open reminders')
    reminders_menu_lb = tk.OptionMenu(window,  reminders_dropdown_field,"No Reminders available")

    if len(reminder_options)==0:
        reminder_options = ["No Reminders available"]
    if len(reminder_options)==0 or len(reminder_options)==1:
        if reminder_options == ["No Reminders available"]:
            reminders_menu_lb = tk.OptionMenu(window, reminders_dropdown_field, *reminder_options)
        else:
            reminders_menu_lb = tk.OptionMenu(window, reminders_dropdown_field, *reminder_options)
            reminders_menu_lb.configure(foreground="red")
    else:
        reminders_menu_lb = tk.OptionMenu(window,reminders_dropdown_field,*reminder_options)
        reminders_menu_lb.configure(foreground="red")
    reminders_menu_lb.place(x=GUI_IO_util.open_reminders_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    def trace_reminders_dropdown(*args):
        if len(reminder_options)>0:
            reminders_util.resetReminder(config_filename,reminders_dropdown_field.get())
    reminders_dropdown_field.trace('w', trace_reminders_dropdown)

    # there is no RUN button when setting up IO information in IO_setup_main.py
    if not "IO_setup_main" in scriptName:
        GUI_IO_util.placeWidget(GUI_IO_util.run_button_x_coordinate, y_multiplier_integer, run_button, False, False,
                                True)

    def _close_window():
        if 'Default' in IO_setup_menu_var.get(): #GUI_util.IO_setup_menu_var.get()
            temp_config_filename = 'default_config.csv'
        else:
            temp_config_filename = config_filename
        config_input_output_alphabetic_options=[]

        # get the IO values currently displayed on a GUI so that they can be checked with the values saved in the csv config file
        config_input_output_alphabetic_options.append(inputFilename.get())
        config_input_output_alphabetic_options.append(input_main_dir_path.get())
        config_input_output_alphabetic_options.append(input_secondary_dir_path.get())
        config_input_output_alphabetic_options.append(output_dir_path.get())
        global local_release_version
        # def exit_handler():
        #     global local_release_version
        #     from NLP_setup_update_util import update_self
        #     # local_release_version is the release on the local machine
        #     local_release_version = local_release_version.strip('\n')
        #     # local_release_version = "2.5.3" # used to test
        #     # GitHub_release_version_var is the release available on GitHub
        #     GitHub_release_version = GitHub_release_version_var.get()
        #     GitHub_release_version = GitHub_release_version.strip('\n')
        #     GitHub_release_version = GitHub_release_version.strip('\r')
        #     if GitHub_release_version != local_release_version:
        #         update_self(window, GitHub_release_version)
        #     else:
        #         print('\nYour NLP Suite is already up-to-date with the release available on GitHub (' + GitHub_release_version_var.get() + ').')
        # local_release_version is the release on the local machine
        # local_release_version = "2.5.3" # used to test
        # GitHub_release_version_var is the release available on GitHub
        local_release_version = local_release_version.strip('\n')
        GitHub_release_version = GitHub_release_version_var.get()
        GitHub_release_version = GitHub_release_version.strip('\n')
        GitHub_release_version = GitHub_release_version.strip('\r')

        GUI_IO_util.exit_window(window, temp_config_filename, scriptName, config_input_output_numeric_options,config_input_output_alphabetic_options, local_release_version, GitHub_release_version)

        # atexit.register(exit_handler())
        #
        # GUI_IO_util.exit_window(window, temp_config_filename, scriptName, config_input_output_numeric_options,config_input_output_alphabetic_options)

    close_button = tk.Button(window, text='CLOSE', width=10,height=2, command=lambda: _close_window())
    GUI_IO_util.placeWidget(GUI_IO_util.close_button_x_coordinate, y_multiplier_integer, close_button, False, False,
                            True)
    #
    # Any message should be displayed after the whole GUI has been displayed

    # although the release version appears in the top part of the GUI,
    #   it is run here otherwise a message will be displayed with an incomplete GUI
    display_release()

    if noLicenceError==True:
        mb.showwarning(title='Fatal error', message="The licence agreement file 'LICENSE-NLP-1.0.txt' could not be found in the 'lib' subdirectory of your main NLP Suite directory\n" + GUI_IO_util.NLPPath + "\n\nPlease, make sure to copy this file in the 'lib' subdirectory.\n\nThe NLP Suite will now exit.")
        sys.exit()

    if 'Default' in IO_setup_menu_var.get():  # GUI_util.IO_setup_menu_var.get()
        temp_config_filename = 'default_config.csv'
    else:
        temp_config_filename = config_filename

    global IO_setup_config_SV
    IO_setup_config_SV=''

    def changed_IO_setup_config(*args):
        global IO_setup_config_SV
        if IO_setup_menu_var.get()!=IO_setup_config_SV:
            IO_setup_config_SV=IO_setup_menu_var.get()
            # must pass config_filename and not temp_config_filename since the value is recomputed in display_IO_setup
            display_IO_setup(window, IO_setup_display_brief, config_filename,
                                             config_input_output_numeric_options, scriptName, silent)

    IO_setup_menu_var.trace("w",changed_IO_setup_config)
    changed_IO_setup_config()

    # answer = True when you do not wish to enter I/O information on the IO_setup_main GUI
    answer = activateRunButton(temp_config_filename, IO_setup_display_brief, scriptName, silent)
    # GUI front end is used for those GUIs that do not have any code to run functions but the buttons just open other GUIs
    if ('GUI front end' not in reminder_options):
        # recompute the options since a new line has been added
        message=reminders_util.message_GUIfrontend
    else:
        message=''

    # this will now display the error message
    if reminders_error==True:
        reminders_util.checkReminder(config_filename,
                                     reminders_util.reminder_options_GUIfrontend,
                                     message)

    # routine_options = reminders_util.getReminders_list(config_filename)
    result = reminders_util.checkReminder('*',
                                          reminders_util.title_options_IO_configuration,
                                          reminders_util.message_IO_configuration)
    if result != None:
        routine_options = reminders_util.getReminders_list(temp_config_filename)

    # check_GitHub_release(local_release_version)

    window.protocol("WM_DELETE_WINDOW", _close_window)

