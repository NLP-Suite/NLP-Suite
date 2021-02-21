# Written by Cynthia Dong April 2020
# Edited by Roberto Franzosi
import GUI_IO_util
import IO_files_util
import sys

# if IO_util.install_all_packages(window,"reminders_util",['os','tkinter','pandas'])==False:
#     sys.exit(0)

import os
import tkinter as tk
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

def generate_reminder_list(path: str) -> None:
    """
    Generate The Reminder List with Default Text

    Args:
        path - the path to the reminders file
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(path + "/reminders.csv", "w+") as f:
        f.writeline("Routine,Title,Message,Event,Status NLP,NLP Suite welcome & system requirements,Welcome to the NLP Suite a package of Python 3 and Java tools designed for text processing and visualization. The Suite requires several FREWARE software components in order to run. You will need to download and install them.\n\n1. JAVA. Several scripts are based on the FREEWARE Java. You can download and install Java at https://www.java.com/en/download\n\n2. STANFORD CORENLP. The core text analyses of the NLP Suite are based on the FREEWARE Stanford CoreNLP. You can download Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n3. GEPHI. The visualization of network graphs requires the installation of the FREEWARE software Gephi. You can download and install Gephi at https://gephi.org/users/download/\n\n4. GOOGLE EARTH PRO. The visualization of geographic maps requires the installation of the FREEWARE software Google Earth Pro. You can download and install Google Earth Pro at https://www.google.com/earth/versions/#download-pro.\n\n5. MALLET. Mallet topic modelling requires the installation of the FREEWARE Mallet. You can download and install Mallet at http://mallet.cs.umass.edu/download.php.\n\n6. WORDNET. Aggregating and disaggregating words requires the installation of the FREWARE WordNet. You can download WordNet at https://wordnet.princeton.edu/download/current-version.,Yes,Yes NLP,NLP Suite architecture & filenames,The Python scripts in the NLP Suite have filenames that clearly identify the Suite architecture.\n\nThe filename suffix designates three different types of files: main GUI and util.\n\nmain files are the only ones that you can run in command line independently of others; they will call both GUI and util files.\n\nGUI files lay out on the screen the widgets of a script for easy Graphical User Interface (GUI).\n\nALL SCRIPTS SUFFIXED BY main CAN BE RUN INDIPENDENTLY OF THE NLP SUITE. Thus on command line you can type\nPython annotatormain.py\nAnd it will fire up the annotator GUI independently of NLP_main.py.\n\nThe filename prefix cluster together scripts used for the same purpose. Thus annotator identifies all files dealing with html annotation.,No,Yes NLP,NLP Suite reminders,Several NLP Suite scripts will fire up reminders for the user. You can turn them off once you are familiar with a script. You can always turn any reminder back ON (or OFF for that matter) if you select the reminders dropdown menu at the bottom of each GUI and then select a specific reminder (if reminders are available for that GUI).,No,Yes SVO,SVO output,'Depending upon the options you select, the SVO pipeline will produce in output different types of files: cvf files, wordcloud image, Google Earth Pro map, and Gephi network graph.\n\nWhile cvf and png files are easy to read, less so are Google Earth Pro kml files and, particularly, Gephi gexf files.\n\nPLEASE, read the Gephi TIPS file before you run the SVO pipeline.',No,Yes SVO,SVO input,'The SVO pipeline allows you to start from a TXT file in input and extract from it via OpenIE the SVOs and visualize them.\n\nBut you can also select a CSV file in input, the output file previosuly created by OpenIE characerized by the suffix '-svo.csv', and use that file to visualize the results without having to rerun OpenIE.',No,Yes SVO,SVO system requirements,The extraction and visualization of SVOs requires several software components.\n\n1. The extraction of SVOs requires the Stanford CoreNLP set of NLP tools. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP requires to have the Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/\n\n3. The visualization of the SVO output as GIS maps and network graphs further requires the installation of the FREEWARE software Gephi and Google Earth Pro.\n\n3a. You can download and install the FREEWARE GEPHI at https://gephi.org/users/download/\n\n3b. You can download and install the FREEWARE GOOGLE EARTH PRO at https://www.google.com/earth/versions/#download-pro,No,Yes *,Excel Charts,'The Excel chart to be displayed has hover-over effects (i.e., when you hover the mouse over chart points some information will be displayed).\n\nFirst, hover-over charts are based on Excel macros. You need to enable macros in Excel to view the chart (read the TIPS file on how to do this).\n\nSecond, if the Excel chart has nothing in it or chart titles are not displayed, you need to hover the mouse over the chart area to display the chart properly. That is how hover-over charts work.',Yes,No GIS,GIS Nominatim geocoder,'If the Nominatim geocoder service exits with the error 'too many requests', you can break up the csv location file and process each subfile for geocoding as normal csv files.',No,Yes GIS,Google Earth Pro download,The GIS pipeline requires a copy of the FREEWARE Google Earth Pro installed on your machine.\n\nYou can download and install the FREEWARE GOOGLE EARTH PRO at https://www.google.com/earth/versions/#download-pro,No,No sentiment-concreteness-analysis,VADER,'VADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n\npython -m nltk.downloader all',Yes,Yes WordNet,WordNet system requirements,The scripts in this GUI require the FREWARE WordNet on your machine. You can download WordNet at https://wordnet.princeton.edu/download/current-version.,No,Yes WordNet,WordNet input file button,'The Select INPUT file button is disabled (grayed out) when you open WordNet. Different options require either no file or different file types.\n\nPlease, tick a checkbox to activate the button.',No,Yes topic-modeling-mallet,Mallet download and installation,The Mallet topic modelling tool requires a copy of the FREEWARE Mallet installed on your machine. You can download the FREEWARE Mallet at http://mallet.cs.umass.edu/download.php.\n\nMallet in turn requires a copy of the JAVA development kit installed on your machine.\n\nRead carrefully the Mallet and Java installation TIPS.,No,Yes sentiment-concreteness-analysis,Stanford CoreNLP Sentiment Analysis system requirements,'The Stanford CoreNLP Sentiment Analysis tool requires two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/',Yes,Yes Stanford-CoreNLP,Stanford CoreNLP system requirements,'Some of the NLP tools in this GUI require two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/',No,Yes Stanford-CoreNLP,CoNLL table,'The CoNLL table produced by the Stanford CoreNLP parser is the input to a number of NLP Suite algorithms.\n\nPLEASE, DO NOT TINKER WITH THE CONLL TABLE OR MANY NLP SUITE ALGORITHMS WILL FAIL.',No,Yes file-splitter,Output directory of split files,'This is a reminder that all file splitter scripts save the split files inside a subdirectory by the name of split_files of the directory where the input txt files are located, regardless of the choice of output directory.',No,Yes social-science-research,Plagiarist,'The 'plagiarist' script, based on Lucene, can process files with embedded dates.\n\nIf the filenames in the input directory embed dates, please tick the checkbox 'Filename embeds date' above.',Yes,No social-science-research,Filename checker,'The 'filename checker' script can process files with embedded dates. If the filenames in the input directory embed dates, please tick the checkbox 'Filename embeds date' above.',Yes,Yes annotator-gender,Time to download new US SS data,'It has been more than two years since the US Social Security gender data have been downloaded to your machine. Check on the US Social Security website whether more current data are available at US Social Security website https://www.ssa.gov/oact/babynames/limits.html',Yes,Yes sentence-analysis,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',No,Yes Senten,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',No,Yes style-analysis,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',No,Yes NLP,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',Yes,Yes *,csv files,'If csv ouput files open displaying weird characters in a Windows OS (e.g., a€), most likely the cause is due to non utf-8 compliant input text. Apostrophes and quotes are the typical culprits, but also other punctuation characters. Please, run the tool to check documents for utf-8 compliance and, if necessary, run the tool for automatic apostrophe and quote conversion from non utf-8 to utf-8. To learm more on utf-8 compliance, read the TIPS on utf-8 compliance.',No,No shape-of-stories,Best topic estimation,The function that estimates the best topics is VERY slow and make take an hour or longer. You can follow its progress in command line.,Yes,Yes narrative-analysis,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI. No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',No,Yes n-grams-co-occurrences-viewer,subprocess.call(cmd) error,'subprocess.call(cmd) error If the VIEWER you are running exits with an error code about a file not fond, most likely the cmd command is too long for Windows to handle (the cmd length is 2047). You may need to move your input and output folders so as to have a shorter path (e.g., desktop).',Yes,Yes GIS-geocode,GIS Nominatim geocoder,,Yes,Yes GIS,GIS GUI options,'The options available on the GUI have been automatically set for you depending upon the type of input file selected: txt or csv. With a txt file, NER extraction via Stanford CoreNLP must be first performed. With a csv file, the script checks whether the file is a CoNLL table, a geocoded file containing latitude and longitude values, ot a file containing a list of locations that need to be geocoded.',No,No sentiment-concreteness-analysis,VADER Mean/Median,'VADER cannot compute separate mean and median sentence values because VADER computes a single for the entire sentence. Use the hedonometer to compute separate values and word list of words found.',Yes,Yes sentiment-concreteness-analysis,SentiWordNet,SentiWordNet does not compute sentence mean and median values nor does it display a list of the individual words found.,Yes,Yes sentiment-concreteness-analysis,Stanford CoreNLP,'The Stanford CoreNLP Sentiment Analysis tool requires two components. 1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html. 2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/',Yes,Yes GIS,Google Maps API,'If the heatmap is displayed by Google Maps for a split second before saying ''Oops! Someghing went wrong'' you probably entered the Google API key incorrectly. Please, check the API key and try again.',Yes,Yes GIS,Open Google Earth GUI,'You should tick the Open GUI checkbox ONLY if you wish to open the GUI. The Google Earth Pro GUI will provide a number of options to personalize a Google Earth Pro map. Press Run after selecting the Open GUI option.',Yes,Yes Stanford-CoreNLP,CoNLL table analyzer,'The Stanford CoreNLP parseer having produced in output a CoNLL table, it will now open the 'CoNLL table analyzer' where you can 1. search the results contained in the CoNLL table by syntactical properties and relations or 2. compute frequency distributions of various types of linguistic objects: clauses, nouns, verbs, function words ('junk/stop' words).',Yes,Yes shape-of-stories,Stanford CoreNLP Sentiment Analysis system requirements,'The Stanford CoreNLP Sentiment Analysis tool requires two components. 1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html. 2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/',Yes,Yes shape-of-stories,Output directory,'The output directory was changed to: C:/Program Files (x86)/NLP_backup/Output/Shape of Stories/Matt-Siyan',Yes,Yes shape-of-stories,Stanford CoreNLP Neural Network,'The Stanford CoreNLP Neural Network approach to Sentiment analysis, like all neural network algorithms, is VERY slow. On a few hundred stories it may take hours to run. Also, neural network algorithms are memory hogs. MAKE SURE TO ALLOCATE AS MUCH MEMORY AS YOU CAN AFFORD ON YOUR MACHINE.',Yes,Yes sentiment-analysis,SentiWordNet,SentiWordNet does not compute sentence mean and median values nor does it display a list of the individual words found.,Yes,Yes sentiment-analysis,VADER,'VADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run python -m nltk.downloader all',Yes,Yes sentiment-analysis,VADER Mean/Median,'VADER cannot compute sentence mean and median values because VADER computes a single compound value for the entire sentence. Use the hedonometer to compute separate values and word list of words found.',Yes,Yes sentiment-analysis,Stanford CoreNLP,'The Stanford CoreNLP Sentiment Analysis tool requires two components. 1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html. 2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/',Yes,Yes corpus,GUI front end,'The script GUI is a convenient front end that displays all the options available for the GUI. No Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.',No,Yes corpus,What is in your corpus,'The Gensim topic modeling routine run from here is a reduced version of the script, meant to provide a quick overview of the topics. For a more in-depth analysis of topics, use the topic modeling scripts for Gensim and Mallet.',Yes,No corpus,What is in your corpus - Gensim,'The Gensim topic modeling routine run from here is a reduced version of the script, meant to provide a quick overview of the topics in your corpus. For a more in-depth analysis of topics, use the topic modeling scripts for Gensim and Mallet.',Yes,No annotator,DBpedia/YAGO options,'Please, using the dropdown menu, select an ontology class or enter a sub-class in the 'Sub-class' widget (for sub-classes, consult the TIPS files on ontology classes). If you select an ontology class from the dropdown menu, the 'Select color' widget will become available. You MUST select a color to be associated to the selected ontology class. After selecting a color, the + button will become available for multiple selections of class/color. You can select the same color for different classes.',Yes,No file-spell-checker,Language detection,'Language detection algorithms are very slow. The NLP Suite runs three different types of algorithms: LANGDETECT, SPACY, and LANGID. Please, arm yourself with patience, depennding upon the number and size of documents processed.',Yes,Yes")


#
# config_filename is the first column in reminders.csv
#   it refers to the general Python script that calls the reminder
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
    except Exception:
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
        routine = config_filename[:-len('-config.txt')]
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
        df1=df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
        if len(df1) == 0:
            # if the title does not exist for a given routine try to see if a universal routine (*) is available
            df1=df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
        if len(df1) != 0:
            row_num = df1.index[0]
            event=df1.at[row_num, "Event"]
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

