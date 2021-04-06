#Written by Roberto Franzosi (help by Jack Hester, Feb 2019 and Karol Josh, March 2020)

import sys
import GUI_util

# Creates a circular dependent imports
# if install_all_packages(GUI_util.window, "GUI_util", ['tkinter', 'os', 'subprocess', 'PIL']) == False:
#     sys.exit(0)

import tkinter as tk
window = tk.Tk()

import os
import tkinter.messagebox as mb

from subprocess import call

import config_util
import reminders_util
import TIPS_util
import GUI_IO_util
import IO_files_util
import IO_CoNLL_util

y_multiplier_integer = 1
noLicenceError=False

# gather GUI info from external file
def set_window(size, label, config, config_option):
    global GUI_size, GUI_label, config_filename, config_input_output_options
    GUI_size, GUI_label, config_filename, config_input_output_options = size, label, config, config_option
    window.geometry(GUI_size)
    window.title(GUI_label)

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
    videos_dropdown_field.set('Watch videos')
    tips_dropdown_field.set('Open TIPS files')
    reminders_dropdown_field.set('Open reminders')
window.bind("<Escape>", clear)


#IO widgets

select_softwareDir_button=tk.Button()
select_input_file_button=tk.Button()
select_input_main_dir_button=tk.Button() 
select_input_secondary_dir_button=tk.Button() 
select_output_file_button=tk.Button()
select_output_dir_button=tk.Button()

softwareDir=tk.StringVar() #StanfordCoreNLP, WordNet, or Mallet
softwareDir.set('')
inputFilename=tk.StringVar()
inputFilename.set('')
input_main_dir_path=tk.StringVar()
input_main_dir_path.set('')
input_secondary_dir_path=tk.StringVar()
input_secondary_dir_path.set('')
outputFilename=tk.StringVar()
outputFilename.set('')
output_dir_path=tk.StringVar()
output_dir_path.set('')
output_dir_path.set('')

release_version_var=tk.StringVar()

open_csv_output_checkbox = tk.IntVar()
create_Excel_chart_output_checkbox = tk.IntVar()

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


# tracer when the checkbox has a separate label widget (label_local) attached to the checkbox widget (checkbox_local)
#For the labels to change the text with the ON/OFF value of the checkbox the command=lambda must be included in the definition of the tk.button
#	For example (see the example in this script):
#	create_Excel_chart_output_label = tk.Checkbutton(window, variable=create_Excel_chart_output_checkbox, onvalue=1, offvalue=0,command=lambda: trace_checkbox(create_Excel_chart_output_label, create_Excel_chart_output_checkbox, "Automatically compute and open Excel charts", "NOT automatically compute and open Excel charts"))
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
    if install_all_packages(GUI_util.window, "GUI_util", ['tkinter', 'os', 'subprocess', 'PIL']) == False:
        sys.exit(0)

    from PIL import Image, ImageTk
    # https://stackoverflow.com/questions/17504570/creating-simply-image-gallery-in-python-tkinter-pil
    image_list = [GUI_IO_util.image_libPath + os.sep + "logo.png"]
    for x in image_list:
        img = ImageTk.PhotoImage(Image.open(x).resize((85,50), Image.ANTIALIAS))
        logo = tk.Label(window, width=85, height=50, anchor='nw', image=img)
        logo.image = img
        logo.place(x=GUI_IO_util.get_help_button_x_coordinate(), y=10)

#__________________________________________________________________________________________________________________
#GUI top widgets ALL IO widgets 
#	softwareDir, input filename, input dir, secondary input dir, output filename, output dir
#__________________________________________________________________________________________________________________

def GUI_top(config_input_output_options,config_filename):
    import IO_libraries_util
    from PIL import Image, ImageTk
    def activateRunButton(*args):
        configArray, missingIO=config_util.setup_IO_configArray(window,config_input_output_options,select_softwareDir_button,softwareDir,select_input_file_button,inputFilename,select_input_main_dir_button,input_main_dir_path,select_input_secondary_dir_button,input_secondary_dir_path,select_output_file_button,outputFilename,select_output_dir_button,output_dir_path)
        # last parameter True: do not continue to warn the user about missing options when enetering all IOs
        run_button_state=GUI_IO_util.check_missingIO(window,missingIO,config_filename,True)
        run_button.configure(state=run_button_state)

    # global so that they are recognized wherever they are used (e.g., select_input_secondary_dir_button in shape_of_stories_GUI)
    global select_softwareDir_button, select_input_file_button, select_input_main_dir_button, select_input_secondary_dir_button, select_output_file_button, select_output_dir_button

    current_y_multiplier_integer1=0 #used for input file
    current_y_multiplier_integer2=0 #used for main input directory
    current_y_multiplier_integer3=0 #used for secondary input directory
    current_y_multiplier_integer4=0 #used for output directory

    # No top help lines displayed when opening the license agreement GUI
    if config_filename!='license-config.txt':
        y_multiplier_integer = 0

        # team_button = tk.Button(window, text='The NLP Suite Team', width=20, height=1, foreground="red",
        #                         command=lambda: GUI_IO_util.list_team(window, config_filename))
        # y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_help_button_x_coordinate(),0,team_button)

        # team_button.pack()

        # canvas = Canvas(window, width=300, height=300)
        # canvas.pack()
        # img = ImageTk.PhotoImage(Image.open("ball.png"))
        # canvas.create_image(20, 20, anchor=NW, image=img)

        intro = tk.Label(window, text=GUI_IO_util.introduction_main)
        intro.pack()

        display_logo()

        if config_filename=='NLP-config.txt':

            release_version_lb = tk.Label(window, text='Release version',foreground="red")
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_help_button_x_coordinate(),
                                                           y_multiplier_integer, release_version_lb, True)
            # first digit for major upgrades
            # second digit for new features
            # third digit for bug fixes and minor changes to current version

            release_version_var.set("1.3.5")
            release_version = tk.Entry(window, state='disabled', width=6, foreground="red", textvariable=release_version_var)
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_help_button_x_coordinate() + 100,
                                                           y_multiplier_integer, release_version,True)


            team_button = tk.Button(window, text='NLP Suite team', width=13, height=1, foreground="red",
                                    command=lambda: GUI_IO_util.list_team(window, config_filename))
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), 0,
                                                           team_button, True)
            cite_button = tk.Button(window, text='How to cite', width=13, height=1, foreground="red",
                                    command=lambda: GUI_IO_util.cite_NLP(window, config_filename))
            y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 150, 0,
                                                           cite_button)

    y_multiplier_integer=0

    global IO_options
    missingIO=""


    #__________________________________________________________________________________________________________________
    # INPUT options widgets
    # IO_options contains the .get() value for each IO widget
    #	e.g.,  ['C:/Program Files (x86)/NLP_backup/WordNet-3.0', '', '', '', '', 'C:/Program Files (x86)/NLP_backup/Output']
    # IO_options will contain the specific user SAVED values for the script
    
    # there should only be one case of 
    #   config_input_output_options = [0,0,0,0,0,0]
    #   in NLP_GUI (NLP-config.txt) since no IO lines are displayed 
    if config_input_output_options!=[0,0,0,0,0,0]:
        IO_options=config_util.readConfig(config_filename,config_input_output_options)
    else:
        IO_options=None

    # the following check and lines are necessary 
    #   to avoid code break in 
    #   if IO_options[] in later tests 
    #   when there is no config folder
    if IO_options==None or IO_options==[]:
        IO_options=[]
        for i in range(len(config_input_output_options)):
            if config_input_output_options[i]>0:
                lineValue="EMPTY LINE"
            else:
                lineValue=""
            IO_options.append(lineValue)

    # software widgets no longer used
    # softwareDir option ______________________________________________
    #softwareDir option 1 for CoreNLP 2 for WordNet 3 for Mallet
    if config_input_output_options[0]==1 or config_input_output_options[0]==2 or config_input_output_options[0]==3:
        if config_input_output_options[0]==1: #directory for Stanford CoreNLP
            #Lambda prevents the command to be executed when you first open the GUI
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            # CoreNLP
            select_softwareDir_button = tk.Button(window,width=GUI_IO_util.select_file_directory_button_width, text='Select Stanford CoreNLP directory', command=lambda: GUI_IO_util.selectDirectory_set_options(window,softwareDir,'',"Select Stanford CoreNLP directory",config_input_output_options,''))

        #config_input_output_options[0] 1 for CoreNLP 2 for WordNet 3 for Mallet
        elif config_input_output_options[0]==2: #directory for WordNet
            #Lambda prevents the command to be executed when you first open the GUI
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            #WordNet
            select_softwareDir_button = tk.Button(window,width=GUI_IO_util.select_file_directory_button_width, text='Select WordNet directory', command=lambda: GUI_IO_util.selectDirectory_set_options(window,softwareDir,'',"Select WordNet directory",config_input_output_options,''))

        #config_input_output_options[0] 1 for CoreNLP 2 for WordNet 3 for Mallet
        # Mallet
        elif config_input_output_options[0]==3: #directory for Mallet
            #Lambda prevents the command to be executed when you first open the GUI
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_softwareDir_button = tk.Button(window,width=GUI_IO_util.select_file_directory_button_width, text='Select Mallet directory', command=lambda: GUI_IO_util.selectDirectory_set_options(window,softwareDir,'',"Select WordNet directory",config_input_output_options,''))

        softwareDir.trace("w",activateRunButton)

        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_softwareDir_button)
        tk.Label(window, textvariable=softwareDir).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))


    #file input file option ______________________________________________
    #	1 for CoNLL file,
    #	2 for txt file,
    #	3 for csv file,
    #	4 for any type file
    #	5 for txt, html (used in annotator)
    #	6 for txt, csv (used in SVO)
    if config_input_output_options[1]>0:
        # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
        # openInputFile_button  = tk.Button(window, width=3, text='', command=lambda: IO_files_util.openFile(window, inputFilename.get()))
        # openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
        #
        if config_input_output_options[1]==1: #single CoNLL file
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CoNLL table', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,True,inputFilename,select_input_main_dir_button,'Select INPUT CoNLL table (csv file)',[('CoNLL csv file','.csv')],".csv",input_main_dir_path))
        elif config_input_output_options[1]==2: #single txt file:
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT TXT file', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,False,inputFilename,select_input_main_dir_button,'Select INPUT TXT file',[('text file','.txt')],".txt",input_main_dir_path))
        elif config_input_output_options[1]==3: #single csv file:
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT csv file', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,False,inputFilename,select_input_main_dir_button,'Select INPUT csv file',[('csv file','.csv')],".csv",input_main_dir_path))
        if config_input_output_options[1]==4: #any type file (used in NLP.py)
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,False,inputFilename,select_input_main_dir_button,'Select INPUT file (any file type: pdf, docx, html, txt, csv, conll); switch extension type below near File name:',[("txt file","*.txt"),("csv file","*.csv"),("pdf file","*.pdf"),("docx file","*.docx"),("html file","*.html"),("CoNLL table","*.conll")], "*.*",input_main_dir_path))
        if config_input_output_options[1]==5: #txt/html
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,False,inputFilename,select_input_main_dir_button,'Select INPUT file (txt, html); switch extension type below near File name:',[("txt file","*.txt"),("html file","*.html")], "*.*",input_main_dir_path))
        if config_input_output_options[1]==6: #txt/csv
            # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
            select_input_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT file', command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,True,False,inputFilename,select_input_main_dir_button,'Select INPUT file (txt, csv); switch extension type below near File name:',[("txt file","*.txt"),("csv file","*.csv")], "*.*",input_main_dir_path))

        inputFilename.trace("w",activateRunButton)

        # place the INPUT file widget
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_file_button)
        tk.Label(window, textvariable=inputFilename).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input file
        current_y_multiplier_integer2=y_multiplier_integer-1
        openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, inputFilename.get()))
        openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer2)

    #primary INPUT directory ______________________________________________
    if config_input_output_options[2]==1: #directory input
        # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
        select_input_main_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT files directory',  command=lambda: GUI_IO_util.selectDirectory_set_options(window,input_main_dir_path,select_input_file_button,"Select INPUT files directory",config_input_output_options,inputFilename,True))
        # select_input_main_dir_button.config(state="normal")

        if IO_options[2]=="EMPTY LINE":
            input_main_dir_path.set("")

        input_main_dir_path.trace("w",activateRunButton)

        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_main_dir_button)
        tk.Label(window, textvariable=input_main_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer2=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, input_main_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer2)

    #secondary INPUT directory ______________________________________________
    if config_input_output_options[3]==1: #secondary directory input
        # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
        select_input_secondary_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT secondary directory',  command=lambda: GUI_IO_util.selectDirectory_set_options(window,input_secondary_dir_path,'',"Select INPUT secondary TXT directory",config_input_output_options,''))

        input_secondary_dir_path.trace("w",activateRunButton)

        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_input_secondary_dir_button)
        tk.Label(window, textvariable=input_secondary_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer3=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, input_secondary_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer3)

    #__________________________________________________________________________________________________________________
    #OUTPUT options
    #OUTPUT file & directory options

    #OUTPUT file ______________________________________________ NOT USED
    if config_input_output_options[4]==1: #output file
        # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
        select_output_file_button=tk.Button(window, width = GUI_IO_util.select_file_directory_button_width,text='Select OUTPUT csv file',  command=lambda: GUI_IO_util.selectFile_set_options(window,config_input_output_options,False,False,outputFilename,'','Select OUTPUT csv file','csv file','.csv',False,input_main_dir_path))
        y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_output_file_button)
        tk.Label(window, textvariable=outputFilename).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        outputFilename.trace("w",activateRunButton)

    #OUTPUT directory ______________________________________________
    if config_input_output_options[5]==1: #output directory
        # buttons are set to normal or disabled in GUI_IO_util.selectFile_set_options
        select_output_dir_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select OUTPUT files directory',  command=lambda: GUI_IO_util.selectDirectory_set_options(window,output_dir_path,select_output_file_button,"Select OUTPUT files directory",config_input_output_options,output_dir_path))

        output_dir_path.trace("w",activateRunButton)

        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,select_output_dir_button)
        tk.Label(window, textvariable=output_dir_path).place(x=GUI_IO_util.get_entry_box_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate() + GUI_IO_util.get_y_step()*(y_multiplier_integer-1))

        #setup a button to open Windows Explorer on the selected input directory
        current_y_multiplier_integer4=y_multiplier_integer-1
        openDirectory_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openExplorer(window, output_dir_path.get()))
        openDirectory_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*current_y_multiplier_integer4)

    old_license_file=os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-1.0.txt')
    if os.path.isfile(old_license_file):
        # rename the file to the new standard
        os.rename(old_license_file, os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-Suite-1.0.txt'))

    if (os.path.isfile(os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-Suite-1.0.txt')) and (IO_libraries_util.inputProgramFileCheck('license_GUI.py'))):
        if not os.path.isfile(GUI_IO_util.configPath + os.sep + 'license-config.txt'):
            call("python " + "license_GUI.py", shell=True)
    else:
        # The error message is displayed at the end of the script after the whole GUI has been displayed
        global noLicenceError
        noLicenceError=True

#__________________________________________________________________________________________________________________
#GUI bottom buttons widgets (ReadMe, TIPS, RUN, QUIT)
#__________________________________________________________________________________________________________________

def GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options):
    """
    :type TIPS_options: object
    """
    # No bottom lines (README, TIPS, RUN, QUIT) displayed when opening the license agreement GUI
    if config_filename=='license-config.txt':
        return
    # IO_options=[]
    reminder_options=[]
    video_options=[]
    missingIO=""

    # for those GUIs (e.g., style analysis) that simply
    #   display options for opening more specialized GUIs
    #   do NOT display the next two sets of widgets
    #   since there is no output to display
    if  config_input_output_options!=[0, 0, 0, 0, 0, 0]:
        #open out csv files widget defined above since it is used earlier
        open_csv_output_label = tk.Checkbutton(window, variable=open_csv_output_checkbox, onvalue=1, offvalue=0, command=lambda: trace_checkbox(open_csv_output_label, open_csv_output_checkbox, "Automatically open output csv file(s)", "Do NOT automatically open output csv file(s)"))
        open_csv_output_label.configure(text="Automatically open output csv file(s)")
        open_csv_output_label.place(x=GUI_IO_util.get_labels_x_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
        open_csv_output_checkbox.set(1)

        #creat Excel chart files widget defined above since it is used earlier
        create_Excel_chart_output_label = tk.Checkbutton(window, variable=create_Excel_chart_output_checkbox, onvalue=1, offvalue=0,command=lambda: trace_checkbox(create_Excel_chart_output_label, create_Excel_chart_output_checkbox, "Automatically compute and open Excel charts", "Do NOT automatically compute and open Excel charts"))
        create_Excel_chart_output_label.configure(text="Automatically compute and open Excel chart(s)")
        create_Excel_chart_output_label.place(x=GUI_IO_util.get_labels_x_coordinate()+380, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)
        create_Excel_chart_output_checkbox.set(1)

        y_multiplier_integer=y_multiplier_integer+1

    readme_button = tk.Button(window, text='Read Me',command=readMe_command,width=10,height=2)
    readme_button.place(x=GUI_IO_util.read_button_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    video_options=['No videos available']
    videos_dropdown_field.set('Watch videos')
    if len(video_options)==0:
        videos_menu_lb = tk.OptionMenu(window,videos_dropdown_field,video_options)
    else:
        if video_options[0] == "No videos available":
            videos_menu_lb = tk.OptionMenu(window, videos_dropdown_field, "No videos available")
        else:
            videos_menu_lb = tk.OptionMenu(window,videos_dropdown_field,*video_options)
            videos_menu_lb.configure(foreground="red")
    videos_menu_lb.place(x=GUI_IO_util.watch_videos_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

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

    routine = config_filename[:-len('-config.txt')]
    # get the list of titles available for a given GUI
    reminder_options = reminders_util.getReminder_list(config_filename, True)
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

    # get_help_button_x_coordinate()+700
    run_button.place(x=GUI_IO_util.run_button_x_coordinate, y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    def _close_window():
        configArray = \
        config_util.setup_IO_configArray(window, config_input_output_options, select_softwareDir_button, softwareDir,
                                         select_input_file_button, inputFilename, select_input_main_dir_button,
                                         input_main_dir_path, select_input_secondary_dir_button,
                                         input_secondary_dir_path,
                                         select_output_file_button, outputFilename, select_output_dir_button,
                                         output_dir_path)[0]

        GUI_IO_util.exit_window(window, config_filename, configArray)

    # quit_button = tk.Button(window, text='QUIT', width=10,height=2, command=lambda: GUI_IO_util.exit_window(window,config_filename,configArray))
    quit_button = tk.Button(window, text='QUIT', width=10,height=2, command=lambda: _close_window())
    # get_help_button_x_coordinate()+820
    quit_button.place(x=GUI_IO_util.quit_button_x_coordinate,y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

    # Any message should be displayed after the whole GUI has been displayed
    
    if noLicenceError==True:
        mb.showwarning(title='Fatal error', message="The licence agreement file 'LICENSE-NLP-1.0.txt' could not be found in the 'lib' subdirectory of your main NLP Suite directory\n" + GUI_IO_util.NLPPath + "\n\nPlease, make sure to copy this file in the 'lib' subdirectory.\n\nThe NLP Suite will now exit.")
        sys.exit()
    
    if IO_options[0]=="EMPTY LINE": # INPUT software directory
        softwareDir.set('')
    else:
        softwareDir.set(config_util.checkConfigDirExists(config_filename,IO_options[0],'INPUT'))

    if IO_options[1]=="EMPTY LINE": # INPUT filename
        inputFilename.set('')
    else:
        inputFilename.set(config_util.checkConfigFileExists(config_filename,IO_options[1],'INPUT'))

    if IO_options[2]=="EMPTY LINE": # INPUT main directory
        input_main_dir_path.set('')
    else:
        input_main_dir_path.set(config_util.checkConfigDirExists(config_filename,IO_options[2],'INPUT'))

    if IO_options[3]=="EMPTY LINE": # INPUT secondary directory
        input_secondary_dir_path.set('')
    else:
        input_secondary_dir_path.set(config_util.checkConfigDirExists(config_filename,IO_options[3],'INPUT'))

    if IO_options[4]=="EMPTY LINE": # OUTPUT file name
        outputFilename.set('')
    else:
        outputFilename.set(config_util.checkConfigFileExists(config_filename,IO_options[4],'OUTPUT'))

    if IO_options[5]=="EMPTY LINE": # OUTPUT directory
        output_dir_path.set('')
    else:
        output_dir_path.set(config_util.checkConfigDirExists(config_filename,IO_options[5],'OUTPUT'))
    
    # set the state (enabled/disabled) of the RUN button
    #   depending upon IO widgets; no IO info, RUN disabled
    configArray, missingIO=config_util.setup_IO_configArray(window,config_input_output_options,select_softwareDir_button,softwareDir,select_input_file_button,inputFilename,select_input_main_dir_button,input_main_dir_path,select_input_secondary_dir_button,input_secondary_dir_path,select_output_file_button,outputFilename,select_output_dir_button,output_dir_path)
    run_button_state=GUI_IO_util.check_missingIO(window,missingIO,config_filename)
    run_button.configure(state=run_button_state)

    if ('GUI front end' not in reminder_options) and (configArray==['EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE']):
        # reminders_util.No_IO_reminder(config_filename)
        reminder_options=['GUI front end']
        message = 'The current GUI is a convenient front end that displays all the options available for the GUI.\n\nNo Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.'
        # recompute the options since a new line has been added
    else:
        message=''

    # this will now display the error message
    if reminders_error==True:
        reminders_util.checkReminder(config_filename, reminder_options, message)

    window.protocol("WM_DELETE_WINDOW", _close_window)
