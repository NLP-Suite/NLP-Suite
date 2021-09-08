# Written by Cynthia Dong April 2020
# Edited by Roberto Franzosi
import GUI_IO_util
import IO_files_util
import sys

# if IO_util.install_all_packages(window,"reminders_util",['os','tkinter','pandas'])==False:
#     sys.exit(0)

import os
import tkinter.messagebox as mb
import pandas as pd
import csv
from csv import writer

# reminders content for specific GUIs are set in the csv file reminders
# check if the user wants to see the message again
# reminders are typically called from GUIs (at the bottom)
#   but can also be called from main or util scripts
#       e.g., file_splitter_util
#       e.g., GIS_geocoder_util

# below is a lit of most reminders called from various scripts with their title_options and message

title_options_IO_configuration = ['Input/Output configurations']
message_IO_configuration = 'Most GUIs in the NLP Suite provide two types of Input/Output (I/O) configurations that specify your selection for your input file or directory (these are mutually exclusive; you can only select one or the other) and output directory:\n\n  Default I/O configuration\n  Alternative I/O configuration\n\nThe Default I/O configuration applies to ALL GUIs in the NLP Suite. This is an ideal option if you work exclusively, or mostly, with the same input file(s) regardless of GUI (i.e., NLP algorithms); you would not need to select these options for every GUI.\n\nIf you occasionally need to run a script using a different set of I/O options, setup the Alternative I/O configuration. This will not affect your I/O selections for all GUIs and will only apply to a specific GUI if you chose the menu option Alternative I/O configuration.'

title_options_IO_setup = ['Input/Output options']
message_IO_setup = 'The two widgets for INPUT FILE and INPUT DIRECTORY are mutually exclusive. You can select one OR the other but not both. Click on either button to make your selection.\n\nTo change an already selected option from FILE to DIRECTORY or from DIRECTORY to FILE, simply click on the button you want to select, make your selection, and the I/O configuration will automatically update.'

title_options_SVO_corpus = ['SVO with corpus data']
message_SVO_corpus = 'You have selected to work with a set of txt files in a directory (your corpus).\n\nBeware that SVO extraction is computationally demanding. Furthermore, depending upon the options you choose (manual coreference editing, GIS maps), it may require manual input on each input file processed.\n\nDepending upon corpus size, manual coreference editing may also not be possible, due to memory requirements.'

title_options_shape_of_stories_CoreNLP = ['Stanford CoreNLP Neural Network']
message_shape_of_stories_CoreNLP = 'The Stanford CoreNLP Neural Network approach to Sentiment analysis, like all neural network algorithms, is VERY slow. On a few hundred stories it may take hours to run.\n\nAlso, neural network algorithms are memory hogs. MAKE SURE TO ALLOCATE AS MUCH MEMORY AS YOU CAN AFFORD ON YOUR MACHINE.'

title_options_shape_of_stories_best_topic = ['Best topic estimation']
message_shape_of_stories_best_topic = 'The function that estimates the best topics is VERY slow and may take an hour or longer. You can follow its progress in command line.'

title_options_language_detection = ['Language detection']
message_language_detection = 'Language detection algorithms are very slow. The NLP Suite runs three different types of algorithms: LANGDETECT, SPACY, and LANGID.\n\nPlease, arm yourself with patience, depennding upon the number and size of documents processed.'

title_options_CoNLL_analyzer = ['CoNLL table analyzer']
message_CoNLL_analyzer = "The Stanford CoreNLP GUI will now open the 'CoNLL table analyzer' where you can:\n\n  1. search the words contained in the CoNLL table (the one just created or a different one) by their syntactical properties and the type of relations to other words;\n  2. compute frequency distributions of various types of linguistic objects: clauses, nouns, verbs, function words ('junk/stop' words)."

title_options_SSdata = ['Time to download new US SS data']
message_SSdata = 'It has been more than two years since the US Social Security gender data have been downloaded to your machine.\n\nCheck on the US Social Security website whether more current data are available at US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html'

reminder_options_GUIfrontend = ['GUI front end']
message_GUIfrontend = 'The current GUI is a convenient front end that displays all the options available for the GUI.\n\nNo Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.'

title_options_Mac_tkinter_bug = ['tkinter MacOS bug']
message_Mac_tkinter_bug = 'MacOS bug in tkinter (https://www.python.org/download/mac/tcltk/).\n\nPython\'s integrated development environment, IDLE, and the tkinter GUI toolkit it uses, depend on the Tk GUI toolkit which is not part of Python itself. For best results, it is important that the proper release of Tcl/Tk is installed on your machine. For recent Python installers for macOS downloadable from this website, here is a summary of current recommendations followed by more detailed information.'

title_options_DBpedia_YAGO = ['DBpedia/YAGO options']
message_DBpedia_YAGO = "Please, using the dropdown menu, select an ontology class or enter a sub-class in the \'Sub-class\' widget (for sub-classes, consult the TIPS files on ontology classes). If you select an ontology class from the dropdown menu, the \'Select color\' widget will become available. You MUST select a color to be associated to the selected ontology class. After selecting a color, the + button will become available for multiple selections of class/color.\n\nYou can select the same color for different classes."

title_options_SA_CoreNLP_system_requirements = ['Stanford CoreNLP Sentiment Analysis system requirements']
message_SA_CoreNLP_system_requirements = 'The Stanford CoreNLP Sentiment Analysis tool requires two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'

title_options_SA_VADER = ['VADER Sentiment Analysis system requirements']
message_SA_VADER = 'VADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n\npython -m nltk.downloader all'

title_options_VADER_MeanMedian = ['VADER Mean/Median']
message_VADER_MeanMedian = 'VADER cannot compute sentence mean and median values because VADER computes a single compound value for the entire sentence.\n\nUse the hedonometer to compute separate values and word list of words found.'

title_options_SA_SentiWordNet = ['SentiWordNet']
message_SA_SentiWordNet = 'SentiWordNet does not compute sentence mean and median values nor does it display a list of the individual words found.'

title_options_NGrams = ['subprocess.call(cmd) error']
message_NGrams = 'subprocess.call(cmd) error\n\nIf the VIEWER you are running exits with an error code about a file not found, most likely your selected INPUT & OUTPUT directory options are too long for Windows to handle.\n\nYou may need to move your input and output folders so as to have a shorter path (e.g., desktop).'

title_options_GIS_GUI = ['GIS GUI options']
message_GIS_GUI = 'The options available on the GUI have been automatically set for you depending upon the type of input file selected: txt or csv.\n\nWith a TXT file, NER extraction via Stanford CoreNLP must be first performed.\n\nWith a CSV file, the script checks whether the file is a CoNLL table, a geocoded file containing latitude and longitude values, or a file containing a list of locations that need to be geocoded.'

title_options_Google_Earth=['Open Google Earth GUI']
message_Google_Earth = 'You should tick the Open GUI checkbox ONLY if you wish to open the GUI.\n\nThe Google Earth Pro GUI will provide a number of options to personalize a Google Earth Pro map. Press Run after selecting the Open GUI option.'

title_options_Google_API=['Google Maps API']
message_Google_API = 'If the heatmap produced by Google Maps is displayed correctly for a split second and then displays "Oops! Something went wrong" you probably:\n  1. pasted incorrectly into the API key widget the Google API key;\n  2. you may not have entered billing information when applying for an API key; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale;\n  3. you may not have enabled the Maps JavaScript API (and if you use Google for geocoding, you also need to enable the Geocoding API.\n\nPlease, check the API key, your billing information, and tthe API enabled and try again.'

title_options_Excel = ['Excel Charts']
message_Excel = 'The Excel chart to be displayed has hover-over effects (i.e., when you hover the mouse over chart points some information will be displayed).\n\nFirst, hover-over charts are based on Excel macros. You need to enable macros in Excel to view the chart (read the TIPS file on how to do this).\n\nSecond, if the Excel chart has nothing in it or chart titles are not displayed, you need to hover the mouse over the chart area to display the chart properly. That is how hover-over charts work.'

title_options_gensim = ['What is in your corpus - Gensim']
message_gensim = 'The Gensim topic modeling routine run from here is a reduced version of the script, meant to provide a quick overview of the topics in your corpus.\n\nFor a more in-depth analysis of topics, use the topic modeling scripts for Gensim and Mallet.'

title_options_geocoder = ["GIS geocoder"]
message_geocoder = 'After the geocoding and mapping is done, please, check carefully the results. If you are geocoding locations such as Athens or Rome in Georgia, most likely they will be geocoded in Greece and Italy. If you specify the United States as the country bias, the geocoder may select Rome, New York, or Indiana, or Illinois, rather than Georgia. To make sure the geocoded Rome is in Georgia, you may need to edit the geocoded csv file, adding Georgia as the state, e.g., Rome, Georgia.'

title_options_wordclouds = ['Web-based word clouds services']
message_wordclouds = "After the selected web-based word-clouds service opens up on your browser, you will need to either copy/paste the text you want to visualize or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file."

def generate_reminder_list(path: str) -> None:
    """
    Generate The Reminder List with Default Text

    Args:
        path - the path to the reminders file
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    if not os.path.isfile(path+os.sep+'reminders.csv'):
        if sys.platform == 'win32':
            os.system(f"copy ..{os.sep}reminders{os.sep}default.csv ..{os.sep}reminders{os.sep}reminders.csv")
        else: # darwin and linux
            os.system(f"cp ..{os.sep}reminders{os.sep}default.csv ..{os.sep}reminders{os.sep}reminders.csv")
#
# config_filename is the first column in reminders.csv
#   it refers to the general Python script that calls the reminder
#   The routine field contains the name used by the reminder script to visualize the correct reminder; it is the name of the config filename trimmed of -config.txt (e.g., GIS for GIS-config.txt, GIS-Google-Earth for GIS-Google-Earth-config.txt).
#   When the Routine field contains a * the reminder will be displayed in ALL GUIs

# title is the second column in reminders.csv
#   it refers to the specific Python option that calls the reminder
# message is typically stored in the reminders.csv files
#   For reminders that require a current value (e.g., date and time stamp)
#   the message is passed (an example is found in GUI_frontEnd in GUI_IO_util.py)
# triggered_by_GUI_event is passed when triggered by an event in the GUI (a checkbox ticked, a file opened)
#   (e.g., in shape_of_stories_GUI)
def getReminder_list(config_filename,silent=False):
    routine=config_filename[:-len('-config.txt')]
    title_options=[]
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    if IO_files_util.checkFile(remindersFile)==False:
        return title_options
    try:
        df = pd.read_csv(remindersFile)
    except FileNotFoundError:
        if silent == False:
            mb.showwarning(title='Reminders file generated', message="The reminders.csv file saved in the reminders subdirectory was not found. If this is your first time running NLP Suite, do not worry. A default reminders.csv has been automatically generated for you.")
        generate_reminder_list(GUI_IO_util.remindersPath)
        return getReminder_list(config_filename, silent)
    except Exception as e:
        print(str(e))
        if silent==False:
            mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
        return None
    # check among the * routine to make sure that the title is not there
    title_options = df[df['Routine'] == '*']['Title'].tolist()
    # now check among the specific routines
    temp=df[df["Routine"] == routine]['Title'].tolist()
    if len(temp)>0:
        title_options.extend(temp)
    if len(title_options)==0:
        title_options = ['Open reminders']
    return title_options

# * in the Routine column are used for reminders that apply to any GUI
# the functions gets the list of reminders for any given GUI (i.e., routine)

def displayReminder(df,row_num,title, message, event, currentStatus, question, seeMsgAgain=False) -> object:
    try:
        message = df.at[row_num, "Message"].replace("\\n", os.linesep)
    except:
        pass
    if message == '':
        answer = mb.askquestion(title="Reminder: " + df.at[row_num, "Title"],
                                message=message+question)
    else:
        answer = mb.askquestion(title="Reminder: " + title,
                                message=message+question)
    answer=answer.capitalize() # Yes/No
    if seeMsgAgain==True:
        if answer == 'No':
            status='No'
        else:
            status = 'Yes'
    else:
        if answer=='Yes':
            if currentStatus == 'No':
                status = 'Yes'
            else:
                status = 'No'
        else:
            status=currentStatus
    # save any status changes
    if currentStatus!=status:
        saveReminder(df,row_num, event, status)

# routine is a string
# title_options is a list [] of all Routine values
# * in the Routine column are used for reminders that apply to any GUI

def checkReminder(config_filename,title_options=[],message='', triggered_by_GUI_event=False):
    # * denotes messages that apply to ALL scripts
    if config_filename=='*':
        routine='*'
    else:
        routine = config_filename.replace('-config.txt', '')
        # routine = config_filename[:-len('-config.txt')]
    if title_options==None:
        title_options = getReminder_list(config_filename)
    else:
        if len(title_options)==0:
            title_options = getReminder_list(config_filename)
            if len(title_options)==0: # ill formed reminders
                return None
    # if len(title_options)==1 and title_options[0] == 'No Reminders available':
    #         mb.showwarning(title='Reminders warning', message="There are no reminders available for this script.")
    #         return
    # open_message = True
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    try:
        df = pd.read_csv(remindersFile)
    except FileNotFoundError:
        generate_reminder_list(GUI_IO_util.remindersPath)
        mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory was not found. If this is your first time running NLP Suite, do not worry. A default reminders.csv has been automatically generated for you.")
        return checkReminder(config_filename, title_options, message, triggered_by_GUI_event)
    except Exception:
        mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
        return None # open_message
    # get the row number of the routine that we are looking at
    silent = False
    for title in title_options:
        routines = routine.split(';')
        for routine in routines:
            df1 = df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
            if len(df1) == 0:
                # if the title does not exist for a given routine try to see if a universal routine (*) is available
                df1 = df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
            if len(df1) != 0:
                row_num = df1.index[0]
                event = df1.at[row_num, "Event"]
                status = df1.at[row_num, "Status"]
                if triggered_by_GUI_event == False and event=='Yes':
                    silent = True
                else:
                    silent = False
                if status == "Yes":
                    if silent == False:
                        # must pass the entire dataframe and not the sub-dataframe dt1
                        displayReminder(df, row_num, title, message, event, status,
                                        "\n\nDo you want to see this message again?", True)
            else: # the reminder option does not exist and must be inserted and then displayed
                if triggered_by_GUI_event == True:
                    event='Yes'
                else:
                    event = 'No'
                insertReminder(routine, title, message, event, "Yes")
                # after inserting the new reminder return to check whether you want to see the reminder again
                if silent == False:
                    # title_options is the value you originally came in with (i.e., [title]) and that was inserted
                    checkReminder(config_filename, title_options, message,
                                  triggered_by_GUI_event)

# called from a GUI when a reminder is selected from the reminder dropdown menu
# title is a string, the reminders option selected in the GUI dropdown menu
def resetReminder(config_filename,title):
    routine = config_filename[:-len('-config.txt')]
    if title != "Open reminders":
        if title == 'No Reminders available':
            mb.showwarning(title='Reminders warning', message="There are no reminders available for this script.")
            return
        remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
        try:
            df = pd.read_csv(remindersFile)
            # get the row number of the routine that we are looking at
        except:
            mb.showwarning(title='Reminders file error',
                           message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
            return
        try:
            df1 = df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
            if len(df1) != 0:
                row_num = df1.index[0]
            else:
                # check among the * routine to make sure that the title is not there
                df1 = df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
                if len(df1) != 0:
                    row_num = df1.index[0]
                else:
                    return
        except:
            mb.showwarning(title='Reminders file error',
                           message="The reminders.csv file saved in the reminders subdirectory does not contain the reminder '" + title + "'.\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.")
            return

        event = df.at[row_num, "Event"]
        status = df.at[row_num, "Status"]
        if status == "No":  # currently off
            question = '\n\nNow this reminder is turned OFF. Do you want to turn it ON?'
        else:
            question = '\n\nNow this reminder is turned ON. Do you want to turn it OFF?'
        displayReminder(df, row_num, title, '', event, status, question, False)


# update do_not_show_message.csv so that we don't show the message box again
# status: "Yes"/"No"
def saveReminder(df,row_num, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    df.at[row_num, "Event"] = event # change it to yes or no
    df.at[row_num, "Status"] = status # change it to yes or no
    df.to_csv(remindersFile, index=False, header=True)

def insertReminder(routine,title, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    with open(remindersFile, "a",newline = '', encoding='utf-8',errors='ignore') as reminders:#write a new row in the reminder csv file
        writer = csv.writer(reminders)
        writer.writerow([routine, title, message, event, status])
        reminders.close()

