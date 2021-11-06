import sys
# import GUI_util
# import IO_libraries_util
# if not IO_libraries_util.install_all_packages(GUI_util.window,"GUI_IO_util", ['tkinter', 'os']):
#     sys.exit(0)

import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

import config_util
import IO_internet_util
import webbrowser

# HELP messages
text_msg=''

introduction_main = "Welcome to this Python 3 script.\nFor brief general information about this script, click on the \"Read Me\" button.\nFor brief information on specific lines click on any of the \"?HELP\" buttons.\nFor longer information on various aspects of the script, click on the \"Open TIPS files\" button and select the pdf help file to view.\nAfter selecting an option, click on \"RUN\" (the RUN button is disabled until all I/O information has been entered).   Click on \"CLOSE\" to exit."
# msg_fileButtonDisabled="\n\nIf the Select INPUT file button is greyed out because you previously selected an INPUT directory but you now wish to use a file as input, click on the Select INPUT directory button and press ESCape to make all INPUT options available."
# msg_dirButtonDisabled="\n\nIf the Select INPUT directory button is greyed out because you previously selected an INPUT file but you now wish to use a directory as input, click on the Select INPUT file button and press ESCape to make all INPUT options available."
msg_openExplorer="\n\nA small button appears next to the select directory button. Click on the button to open Windows Explorer on the directory displayed, if one is displayed, or on the directory where the NLP script is saved." 
msg_openFile="\n\nA small button appears next to the select file button. Click on the button to open the file, if one has been selected, as a check that you selected the correct file." # + msg_fileButtonDisabled
msg_Esc="\n\nPress the ESCape button to clear any previously selected options and start fresh."

msg_IO_setup="Please, using the dropdown menu, select the type of INPUT/OUTPUT configuration you wish to use in this GUI.\n   INPUT file or directory\n   OUTPUT directory where files produced by the NLP tools will be saved (csv, txt, html, kml, jpg).\n\nThe default configuration is the I/O option used for all GUIs as default;\n   the GUI-specific configuration is an I/O option also typically used in this GUI;\n   the New configuration allows you to setup a new GUI-specific I/O configuration.\n\nYou can click on the display area and scroll to visualize the current configuration. You can also click on the 'Setup INPUT/OUTPUT configuration' button to get a better view of the available options.\n\nClick on the small buttons to the right of the I/O display area to open the input file, the input directory, and output directory displayed."
msg_CoreNLP="Please, select the directory where you downloaded the Stanford CoreNLP software.\n\nYou can download Stanford CoreNLP from https://stanfordnlp.github.io/CoreNLP/download.html\n\nYou can place the Stanford CoreNLP folder anywhere on your machine. But... on some machines CoreNLP will not run unless the folder is inside the NLP folder.\n\nIf you suspect that CoreNLP may have given faulty results for some sentences, you can test those sentences directly on the Stanford CoreNLP website at https://corenlp.run\n\nYOU MUST BE CONNECTED TO THE INTERNET TO RUN CoreNLP."
msg_WordNet="Please, select the directory where you downloaded the WordNet lexicon database.\n\nYou can download WordNet from https://wordnet.princeton.edu/download/current-version."
msg_Mallet="Please, select the directory where you downloaded the Mallet topic modeling software."
msg_CoNLL="Please, select a CoNLL table that you would like to analyze.\n\nA CoNLL table is a file generated by the Python script StanfordCoreNLP.py. The CoreNLP script parses a set of text documents using the Stanford CoreNLP parser, providing a dependency tree for each sentence of the documents. In a CoNLL table, each token is labeled with a part-of-speech tag (POSTAG), a Dependency Relation tag (DEPREL), its dependency relation within the corresponding dependency tree, and other useful information." + msg_openFile
msg_corpusData="Please, select the directory where you store your TXT corpus to be analyzed. ALL TXT FILES PRESENT IN THE DIRECTORY WILL BE PARSED. NON TXT FILES WILL BE IGNORED. MOVE ANY TXT FILES YOU DO NOT WISH TO PROCESS TO A DIFFERENT DIRECTORY."  + msg_openExplorer # + msg_dirButtonDisabled
msg_anyData="Please, select the directory where you store the files to be analyzed. ALL FILES OF A SELECTED EXTENSION TYPE (pdf, docx, txt, csv, conll), PRESENT IN THE DIRECTORY WILL BE PROCESSED. ALL OTHER FILE TYPES WILL BE IGNORED."  + msg_openExplorer # + msg_dirButtonDisabled
msg_anyFile="Please, select the file to be analyzed (of any type: pdf, docx, txt, csv, conll)."  + msg_openFile
msg_txtFile="Please, select the TXT file to be analyzed." + msg_openFile # + msg_fileButtonDisabled
msg_csvFile="Please, select the csv file to be analyzed." + msg_openFile # + msg_fileButtonDisabled
msg_csv_txtFile="Please, select either a CSV file or a TXT file to be analyzed." + msg_openFile # + msg_fileButtonDisabled
msg_txt_htmlFile="Please, select either a TXT file or an html file to be analyzed." + msg_openFile # + msg_fileButtonDisabled
msg_outputDirectory="Please, select the directory where the script will save all OUTPUT files of any type (txt, csv, png, html)."  + msg_openExplorer
msg_outputFilename="Please, enter the OUTPUT file name. THE SELECT OUTPUT BUTTON IS DISABLED UNTIL A SEARCHED TOKEN HAS BEEN ENTERED.\n\nThe search result will be saved as a separated csv file with the file path and name entered. \n\nThe same information will be displayed in the command line."
msg_openOutputFiles="Please, tick the checkbox to open automatically (or not open) output csv file(s), including any Excel charts.\n\nIn the NLP Suite, all CSV FILES that contain information on web links or files with their path will encode this information as hyperlinks. If you click on the hyperlink, it will automatically open the file or take you to a website. IF YOU ARE A MAC USER, YOU MUST OPEN ALL CSV FILES WITH EXCEL, RATHER THAN NUMBERS, OR THE HYPERLINK WILL BE BARRED AND DISPLAYED AS A RED TRIANGLE.\n\nEXCEL HOVER-OVER EFFECT.  Most Excel charts have been programmed for hover-over effects, whereby when you pass the cursor over a point on the chart (hover over) some releveant information will be displayed (e.g., the sentence at that particular point).\n\nEXCEL EMPTY CHART AREA.  If the hover-over chart area is empty, with no chart displayed, enlarge the chart area by dragging any of its corners or by moving the zoom slide bar on the bottomg right-hand corner of Excel.\n\nEXCEL ENABLE MACROS.  The hover-over effect is achieved using VBA macros (Virtual Basic for Applications, Windows programming language). If Excel warns you that you need to enable macros, while at the same time warning you that macros may contain viruses, do the following: open an Excel workbook; click on File; slide cursor all the way down on the left-hand banner to Options; click on Trust Center; then on Trust Center Settings; then Macro Settings; Click on Enable all macros, then OK. The message will never appear again."
msg_multipleDocsCoNLL="\n\nFOR CONLL FILES THAT INCLUDE MULTIPLE DOCUMENTS, THE EXCEL CHARTS PROVIDE OVERALL FREQUENCIES ACROSS ALL DOCUMENTS. FOR SPECIFIC DOCUMENT ANALYSES, PLEASE USE THE GENERAL EXCEL OUTPUT FILE."

# location of this src python file
#one folder UP, the NLP folder
#subdirectory of script directory where config files are saved
#subdirectory of script directory where lib files are saved
#subdirectory of script directory where Google maps lib files are saved
#subdirectory of script directory where Excel lib files are saved
#subdirectory of script directory where lib files are saved
#subdirectory of script directory where lib files are saved
#subdirectory of script directory where lib files are saved
#subdirectory of script directory where gender names are saved
#global TIPSPath
#subdirectory of script directory where reminders file is saved

scriptPath = os.path.dirname(os.path.abspath(__file__))
NLPPath=os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + os.sep + os.pardir)
configPath = os.path.join(NLPPath,'config')
libPath = os.path.join(NLPPath,'lib')
image_libPath = os.path.join(NLPPath,'lib'+os.sep+'images')
Google_heatmaps_libPath = os.path.join(NLPPath,'lib'+os.sep+'sampleHeatmap')
Excel_charts_libPath = os.path.join(NLPPath,'lib'+os.sep+'sampleCharts')
sampleData_libPath = os.path.join(NLPPath,'lib'+os.sep+'sampleData')
sentiment_libPath = os.path.join(NLPPath,'lib'+os.sep+'sentimentLib')
concreteness_libPath = os.path.join(NLPPath,'lib'+os.sep+'concretenessLib')
CoreNLP_enhanced_dependencies_libPath = os.path.join(NLPPath,'lib'+os.sep+'CoreNLP_enhanced_dependencies')
wordLists_libPath = os.path.join(NLPPath,'lib'+os.sep+'wordLists')
namesGender_libPath = os.path.join(NLPPath, 'lib'+os.sep+'namesGender')
GISLocations_libPath = os.path.join(NLPPath,'lib'+os.sep+'GIS')
TIPSPath = os.path.join(NLPPath,'TIPS')
videosPath = os.path.join(NLPPath,'videos')
remindersPath = os.path.join(NLPPath, 'reminders')

def placeWidget(x_coordinate,y_multiplier_integer,widget_name,sameY=False, centerX=False, basic_y_coordinate=90):
    #basic_y_coordinate = 90
    y_step = 40 #the line-by-line increment on the GUI
    if centerX:
        widget_name.place(relx=0.5, anchor=tk.CENTER, y=basic_y_coordinate + y_step*y_multiplier_integer)
    else:
        widget_name.place(x=x_coordinate, y=basic_y_coordinate + y_step*y_multiplier_integer)
    if sameY==False:
        y_multiplier_integer = y_multiplier_integer+1
    return y_multiplier_integer

if sys.platform == 'darwin': #Mac OS
    help_button_x_coordinate = 70
    labels_x_coordinate = 150  # start point of all labels in the second column (first column after ? HELP)
    labels_x_indented_coordinate = 160
    select_file_directory_button_width=23
    open_file_directory_button_width = 1
    IO_button_name_width=1
    open_file_directory_coordinate = 400
    entry_box_x_coordinate = 470 #start point of all labels in the third column (second column after ? HELP); where IO filename, dir, etc. are displayed
    read_button_x_coordinate = 70
    watch_videos_x_coordinate = 200
    open_TIPS_x_coordinate = 370
    open_reminders_x_coordinate = 570
    run_button_x_coordinate = 850
    close_button_x_coordinate = 980

    open_file_button_brief = 700
    open_inputDir_button_brief = 740
    open_outputDir_button_brief = 780

    # special internal GUI specific values
    SVO_2nd_column = 570
    SVO_2nd_column_top = 450
    SVO_3rd_column_top = 850

else: #windows and anything else
    help_button_x_coordinate = 50
    labels_x_coordinate = 120  # start point of all labels in the second column (first column after ? HELP)
    labels_x_indented_coordinate = 140
    select_file_directory_button_width=30
    IO_button_name_width=30
    open_file_directory_button_width = 3
    open_file_directory_coordinate = 350
    entry_box_x_coordinate = 400 #start point of all labels in the third column (second column after ? HELP)
    read_button_x_coordinate = 50
    watch_videos_x_coordinate = 170
    open_TIPS_x_coordinate = 350
    open_reminders_x_coordinate = 550
    run_button_x_coordinate = 840
    close_button_x_coordinate = 960
    open_file_button_brief = 760
    open_inputDir_button_brief = 800
    open_outputDir_button_brief = 840

    # special internal GUI specific values
    SVO_2nd_column = 520
    SVO_2nd_column_top = 400
    SVO_3rd_column_top = 800

basic_y_coordinate = 90
y_step = 40 #the line-by-line increment on the GUI

def get_GUI_width(size_type=1):
    if sys.platform == 'darwin':  # Mac OS
        if size_type == 1: # for now we have one basic size
            return 1400
        if size_type == 2:
            return 1400
        if size_type == 3:
            return 1400
        if size_type == 4:
            return 1400
    elif sys.platform == 'win32': # for now we have two basic sizes
        if size_type == 1:
            return 1250
        if size_type == 2:
                return 1300
        elif size_type==3:
            return 1300
        elif size_type==4:
            return 1300

def get_basic_y_coordinate():
    return basic_y_coordinate
def get_y_step():
    return y_step
def get_help_button_x_coordinate():
    return help_button_x_coordinate

def get_labels_x_coordinate():
    return labels_x_coordinate

def get_labels_x_indented_coordinate():
    return labels_x_indented_coordinate

def get_entry_box_x_coordinate():
    return entry_box_x_coordinate

def get_open_file_directory_coordinate():
    return open_file_directory_coordinate

def about():
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub what the NLP Suite is all about"):
        return
    webbrowser.open_new("https://github.com/NLP-Suite/NLP-Suite/wiki/About")

def release_history():
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub the NLP Suite release history"):
        return
    webbrowser.open_new("https://github.com/NLP-Suite/NLP-Suite/wiki/NLP-Suite-Release-History")

# The function displays the contributors to the development of the NLP Suite
def list_team():
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub the NLP Suite team"):
        return
    webbrowser.open_new("https://github.com/NLP-Suite/NLP-Suite/wiki/The-NLP-Suite-Team")

def cite_NLP():
    # check internet connection
    if not IO_internet_util.check_internet_availability_warning("Check on GitHub the NLP Suite newest release version"):
        return
    webbrowser.open_new("https://github.com/NLP-Suite/NLP-Suite/wiki/About#How-to-Cite-the-NLP-Suite")

#configFilename with no path;
#configArray contains all the IO files and paths
#configArray is computed by setup_IO_configArray in config_util
# config_input_output_options is set to [0, 0, 0, 0, 0, 0] for GUIs that are placeholders for more specialized GUIs
#   in these cases (e.g., narrative_analysis_main, there are no I/O options to save
def exit_window(window,configFilename, ScriptName, config_input_output_options, configArray):
    if ScriptName!='NLP_menu_main' and config_input_output_options != [0, 0, 0, 0, 0, 0]:
        config_util.saveConfig(window,configFilename, configArray)
    window.destroy()
    sys.exit(0)

# missingIO is called from GUI_util
def check_missingIO(window,missingIO,config_filename,IO_setup_display_brief,ScriptName,silent=False):
    if config_filename=='NLP-config.txt':
        config_filename = 'default-config.txt'
    # the IO_button_name error message changes depending upon the call
    button = "button"
    # there is no RUN button when setting up IO information so the call to check_missingIO should be silent
    run_button_disabled_msg = "The RUN button is disabled until the required information for the selected Input/Output fields is entered.\n\n"
    if "IO_setup_main" in ScriptName:
        run_button_disabled_msg = ""
    if IO_setup_display_brief==True:
        IO_button_name = "Setup INPUT/OUTPUT configuration" # when displaying brief
    if IO_setup_display_brief==False:
        if 'NLP_menu_main' in ScriptName:
            IO_button_name = "Setup default I/O options"  # when displaying from NLP_menu_main
        else:
            IO_button_name = "Select INPUT & Select OUTPUT" # when displaying full
            button="buttons"
    Run_Button_Off=False
    #do not check IO requirements for NLP.py; too many IO options available depending pon the sript run
    # if config_filename=="NLP-config.txt" or config_filename=="social-science-research-config.txt":
    if config_filename == "social-science-research-config.txt":
        # RUN button always active since several options are available and IO gets checked in the respective scripts
        Run_Button_Off=False
        missingIO=''
    mutually_exclusive_msg=''
    if "Input file" in missingIO and "Input files directory" in missingIO:
        mutually_exclusive_msg='The two I/O options - "Input file" and "Input files directory" - are mutually exclusive. You can only select one or the other. In other words, you can choose to work with a sigle file in input or with many files stored in a directory.\n\n'

    if len(missingIO)>0:
        if not silent:
            mb.showwarning(title='Warning', message='The following required INPUT/OUTPUT information is missing in config file ' + config_filename + ':\n\n' + missingIO + '\n\n' + mutually_exclusive_msg + run_button_disabled_msg + 'Please, click on the "' + IO_button_name + '" ' + button + ' at the top of the GUI and enter the required I/O information.')
            Run_Button_Off=True
    if Run_Button_Off==True:
        run_button_state="disabled"
    else:
        run_button_state="normal"
    window.focus_force()
    return run_button_state

from tkinter import Toplevel
def Dialog2Display(title: str):
    Dialog2 = Toplevel(height=1000, width=1000)

# The function places and displays a message for each ? HELP button in the GUIs
def place_help_button(window,x_coordinate,y_coordinate,text_title,text_msg):
    if text_title=='Help':
        text_title='NLP Suite Help'
    def msg_box():
        mb.showinfo(title=text_title, message=text_msg)
    tk.Button(window, text='? HELP', command=msg_box).place(x=x_coordinate,y=y_coordinate)

# The function displays the info for the ReadMe button in the GUIs
def readme_button(Window, xCoord, yCoord, text_title,text_msg):
    if text_title=='Help':
        text_title='NLP Suite Help'
    mb.showinfo(title=text_title, message=text_msg)


# creating popup menu in tkinter

def dropdown_menu_widget(window,textCaption, menu_values, default_value):
    # from tkinter import *

    class App():

        chunks = ['A','B','C']

        def __init__(self,master):

            self.testVariable = StringVar()

            def refresh():
                # Prints what's in the variable
                print(self.testVariable.get())

            def testFunc(x):
                return lambda: self.testVariable.set(x)

            def initSummary():
                self.dataButton["menu"].delete(0, 'end')
                for i in self.chunks:
                    self.dataButton["menu"].add_command(label=i, command = testFunc(i))

            top = self.top = Toplevel()
            self.sumButton = Button(top, text="Test", width=25, command=lambda: initSummary())
            self.sumButton.grid(row=0, column=0, sticky=W)
            self.dataButton = OptionMenu(top, self.testVariable, "Stuff")
            self.dataButton.grid(row=0, column=1, sticky=W)
            self.testButton = Button(top, text="Variable", width=25, command = lambda: refresh())
            self.testButton.grid(row=1, column=0, sticky=W)

    # Call the main app
    root = Tk()
    app = App(root)
    root.mainloop()

# https://stackoverflow.com/questions/51591163/self-made-tkinter-popup-menu-python
#     root = Tk()
#     popup = Menu(root, tearoff=0)
#     popup.add_command(label="Main Product")
#     popup.add_command(label="Side Product")
#
#     def popupm(bt):
#         try:
#             x = bt.winfo_rootx()
#             y = bt.winfo_rooty()
#             popup.tk_popup(x, y, 0)
#         finally:
#             popup.grab_release()
#
#     bt = Button(root, text='Menu')
#     bt.configure(command=lambda: popupm(bt))
#     bt.place(x=10, y=15)
#
#     root.mainloop()

    # master = tk.Tk()
    # master.focus_force()
    # tk.Label(master, width=len(textCaption)+30).grid(row=0)
    # master.title(textCaption)
    #
    # # menu_var = tk.StringVar()
    # # menu = ttk.Combobox(master, width=90, textvariable=menu_var)
    # menu = ttk.Combobox(master, width=90)
    # menu['values'] = menu_values
    # menu.pack()
    # menu.focus_force()
    # master.mainloop()
    # master.destroy()

    # window.wait_window(master)
    return # must return selected value

    # https://www.geeksforgeeks.org/popup-menu-in-tkinter/
    # creates parent window
    #     def __init__(self):
    #
    #         self.root = tkinter.Tk()
    #         self.root.geometry('400x30')
    #
    #         self.frame1 = tkinter.Label(self.root,
    #                                     width=400,
    #                                     height=20,
    #                                     bg='#AAAAAA')
    #         self.frame1.pack()
    #
    #     # create menu
    #     def popup(self):
    #         self.popup_menu = tkinter.Menu(self.root,
    #                                        tearoff=0)
    #
    #         self.popup_menu.add_command(label="say hi",
    #                                     command=lambda: self.hey("hi"))
    #
    #         self.popup_menu.add_command(label="say hello",
    #                                     command=lambda: self.hey("hello"))
    #         self.popup_menu.add_separator()
    #         self.popup_menu.add_command(label="say bye",
    #                                     command=lambda: self.hey("bye"))
    #
    #     # display menu on right click
    #     def do_popup(self, event):
    #         try:
    #             self.popup_menu.tk_popup(event.x_root,
    #                                      event.y_root)
    #         finally:
    #             self.popup_menu.grab_release()
    #
    #     def hey(self, s):
    #         self.frame1.configure(text=s)
    #
    #     def run(self):
    #         self.popup()
    #         self.root.bind("<Button-3>", self.do_popup)
    #         tkinter.mainloop()
    #
    #
    # a = A()
    # a.run()

def slider_widget(window,textCaption, lower_bound, upper_bound, default_value):
    top = tk.Toplevel(window)
    l = tk.Label(top, text= textCaption)
    l.pack()
    s = tk.Scale(top, from_= lower_bound, to=upper_bound, orient=tk.HORIZONTAL)
    s.set(default_value)
    s.pack()

    def get_value():
        global val
        val = s.get()
        top.destroy()
        top.update()

    def _delete_window():
        mb.showwarning(title = "Invalid Operation", message = "Please click OK to save your choice of parameter.")

    top.protocol("WM_DELETE_WINDOW", _delete_window)

    tk.Button(top, text='OK', command=lambda: get_value()).pack()
    window.wait_window(top)
    return val

# TODO
# 2 widgets max for now; should allow more, dynamically
# called by
def enter_value_widget(masterTitle,textCaption,numberOfWidgets=1,defaultValue='',textCaption2='',defaultValue2=''):
    value1=defaultValue
    value2=defaultValue2

    # TODO should not restrict to 2; should have a loop
    if numberOfWidgets==2:
        # TODO should have a list and break it up assigning values in a loop
        value2=defaultValue2
    master = tk.Tk()
    master.focus_force()

    tk.Label(master,width=len(textCaption),text=textCaption).grid(row=0)
    # TODO should not restrict to 2; should have a loop
    if numberOfWidgets==2:
        tk.Label(master, width=len(textCaption2),text=textCaption2).grid(row=1)

    master.title(masterTitle)
    # the width in tk.Entry determines the overall width of the widget;
    #   MUST be entered
    #   + 30 to add room for - [] and X in a widget window
    e1 = tk.Entry(master,width=len(masterTitle)+30)
    e1.focus_force()

    # TODO 2 could be a larger number; should have a loop
    if numberOfWidgets==2:
        e2 = tk.Entry(master,width=len(masterTitle)+30)

    e1.grid(row=0, column=1)
    # TODO 2 could be a larger number; should have a loop
    if numberOfWidgets==2:
        e2.grid(row=1, column=1)

    e1.insert(len(textCaption), defaultValue) # display a default value
    # TODO 2 could be a larger number; should have a loop
    if numberOfWidgets==2:
        e2.insert(len(textCaption2), defaultValue2) # display a default value

    tk.Button(master,
              text='OK',
              command=master.quit).grid(row=3,
                                        column=0,
                                        sticky=tk.W,
                                        pady=4)
    master.mainloop()
    value1=str(e1.get())
    # TODO 2 could be a larger number; should have a loop
    if numberOfWidgets==2:
        value2=str(e2.get())
    master.destroy()
    # convert to list; value1 is checked for length in calling function
    #   so do not convert if empty or its length will be the length of ['']
    # if value1!='':
    #     value1=list(value1.split(" "))
    return value1, value2
