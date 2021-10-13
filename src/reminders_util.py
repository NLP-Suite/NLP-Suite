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
import GUI_util
from csv import writer

# reminders content for specific GUIs are set in the csv file reminders
# check if the user wants tadded the release_version.txt fio see the message again
# reminders are typically called from GUIs (at the bottom)
#   but can also be called from main or util scripts
#       e.g., file_splitter_util
#       e.g., GIS_geocoder_util

# below is a lit of most reminders called from various scripts with their title_options and message

title_options_NLP_Suite_welcome = ['NLP Suite welcome & system requirements']
message_NLP_Suite_welcome = 'Welcome to the NLP Suite a package of Python 3 and Java tools designed for text processing and visualization. The Suite requires several FREWARE software components in order to run. You will need to download and install them.\n\n1. JAVA. Several scripts are based on the FREEWARE Java. You can download and install Java at https://www.java.com/en/download\n\n2. STANFORD CORENLP. The core text analyses of the NLP Suite are based on the FREEWARE Stanford CoreNLP. You can download Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n3. GEPHI. The visualization of network graphs requires the installation of the FREEWARE software Gephi. You can download and install Gephi at https://gephi.org/users/download/\n\n4. GOOGLE EARTH PRO. The visualization of geographic maps requires the installation of the FREEWARE software Google Earth Pro. You can download and install Google Earth Pro at https://www.google.com/earth/versions/#download-pro.\n\n5. MALLET. Mallet topic modelling requires the installation of the FREEWARE Mallet. You can download and install Mallet at http://mallet.cs.umass.edu/download.php.\n\n6. WORDNET. Aggregating and disaggregating words requires the installation of the FREWARE WordNet. You can download WordNet at https://wordnet.princeton.edu/download/current-version.'

title_options_NLP_Suite_architecture = ['NLP Suite architecture & filenames']
message_NLP_Suite_architecture = 'The Python scripts in the NLP Suite have filenames that clearly identify the Suite architecture.\n\nThe filename suffix designates two different types of files: _main and _util.\n\n_main files are the only ones that you can run in command line independently of others; they may call _util files.\n\nThe _main files, with their GUI options, lay out on the screen the widgets of a script for easy Graphical User Interface (GUI).\n\nALL SCRIPTS SUFFIXED BY _main CAN BE RUN INDIPENDENTLY OF THE NLP SUITE. Thus on command line you can type\nPython annotator_main.py\nand it will fire up the annotator GUI independently of NLP_main.py.\n\nThe filename prefix cluster together scripts used for the same purpose. Thus annotator identifies all files dealing with html annotation.'

title_options_NLP_Suite_reminders = ['NLP Suite reminders']
message_NLP_Suite_reminders = 'Several NLP Suite scripts will fire up reminders for the user. You can turn them off once you are familiar with a script. You can always turn any reminder back ON (or OFF for that matter) if you select the reminders dropdown menu at the bottom of each GUI and then select a specific reminder (if reminders are available for that GUI).'

title_options_SVO_input = ['SVO input']
message_SVO_input = "The SVO pipeline allows you to start from a TXT file in input and extract from it via OpenIE the SVOs and visualize them.\n\nBut you can also select a CSV file in input, the output file previosuly created by OpenIE characerized by the suffix '-svo.csv', and use that file to visualize the results without having to rerun OpenIE."

title_options_SVO_output = ['SVO output']
message_SVO_output = 'Depending upon the options you select, the SVO pipeline will produce in output different types of files: cvf files, wordcloud image, Google Earth Pro map, and Gephi network graph.\n\nWhile cvf and png files are easy to read, less so are Google Earth Pro kml files and, particularly, Gephi gexf files.\n\nPLEASE, read the Gephi TIPS file before you run the SVO pipeline.'

title_options_SVO_system_requirements = ['SVO system requirements']
message_SVO_system_requirements = 'The extraction and visualization of SVOs requires several software components.\n\n1. The extraction of SVOs requires the Stanford CoreNLP set of NLP tools. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP requires to have the Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/\n\n3. The visualization of the SVO output as GIS maps and network graphs further requires the installation of the FREEWARE software Gephi and Google Earth Pro.\n\n3a. You can download and install the FREEWARE GEPHI at https://gephi.org/users/download/\n\n3b. You can download and install the FREEWARE GOOGLE EARTH PRO at https://www.google.com/earth/versions/#download-pro'

title_options_Excel_Charts = ['Excel Charts']
message_Excel_Charts = 'The Excel chart to be displayed has hover-over effects (i.e., when you hover the mouse over chart points some information will be displayed).\n\nFirst, hover-over charts are based on Excel macros. You need to enable macros in Excel to view the chart (read the TIPS file on how to do this).\n\nSecond, if the Excel chart has nothing in it or chart titles are not displayed, you need to hover the mouse over the chart area to display the chart properly. That is how hover-over charts work.'

title_options_GIS_Nominatim = ['GIS Nominatim geocoder']
message_GIS_Nominatim = "If the Nominatim geocoder service exits with the error 'too many requests', you can break up the csv location file and process each subfile for geocoding as normal csv files."

title_options_Google_Earth_Pro_download = ['Google Earth Pro']
message_Google_Earth_Pro_download = 'The GIS pipeline requires a copy of the FREEWARE Google Earth Pro installed on your machine in order to visualize the kml files produced for Google Earth Pro.\n\nYou can download and install the FREEWARE GOOGLE EARTH PRO for desktop at https://www.google.com/earth/versions/'

title_options_VADER = ['VADER']
message_VADER = 'VADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n\npython -m nltk.downloader all'

title_options_WordNet_system_requirements = ['WordNet system requirements']
message_WordNet_system_requirements = 'The scripts in this GUI require the FREEWARE WordNet on your machine. You can download WordNet at https://wordnet.princeton.edu/download/current-version.'

title_options_WordNet_input_file_button = ['WordNet input file button']
message_WordNet_input_file_button = 'The Select INPUT file button is disabled (grayed out) when you open WordNet. Different options require either no file or different file types.\n\nPlease, tick a checkbox to activate the button.'

title_options_WordNet_verb_aggregation = ['WordNet VERB aggregation']
message_WordNet_verb_aggregation = "CAVEAT!\n\nFor VERBS, the aggregated 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get'). You may wish to exclude these auxiliary verbs from frequencies."

title_options_Mallet_installation = ['Mallet download and installation']
message_Mallet_installation = 'The Mallet topic modelling tool requires a copy of the FREEWARE Mallet installed on your machine. You can download the FREEWARE Mallet at http://mallet.cs.umass.edu/download.php.\n\nMallet in turn requires a copy of the JAVA development kit installed on your machine.\n\nRead carrefully the Mallet and Java installation TIPS.'

title_options_CoreNLP_Sentiment_Analysis_system_requirements = ['Stanford CoreNLP Sentiment Analysis system requirements']
message_CoreNLP_Sentiment_Analysis_system_requirements = 'The Stanford CoreNLP Sentiment Analysis tool requires two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'

title_options_CoreNLP_system_requirements = ['Stanford CoreNLP system requirements']
message_CoreNLP_system_requirements = 'Some of the NLP tools in this GUI require two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'

# not used
title_options_CoreNLP_Java = ['Stanford CoreNLP Java 64-Bits']
message_CoreNLP_Java = 'The Java call to Stanford CoreNLP script uses the property -d64 for the 64 bits JAVA. Java is normally set to 32 bits Virtual Machine as default on a Windows machine. If you see an error the property -d64 is not recognized, you will need to change the Java default to 64 bits VM.\n\nTo test your VM settings, open  command prompt/terminal and type Java - version. You should see "64-Bit Server VM" in the last line of output.'

title_options_CoreNLP_coref = ['Stanford CoreNLP coref merged files']
message_CoreNLP_coref = 'The Stanford CoreNLP coref annotator with a corpus of files in a directory in input will create a merged coref file in output.'

title_options_CoreNLP_shutting_down = ['CoreNLP Server is shutting down']
message_CoreNLP_shutting_down = "The Stanford CoreNLP, after firing up, will display on command line/prompt the message: CoreNLP Server is shutting down.\n\nIt is NOT a problem. The process will continue..."

title_options_CoreNLP_NER_tags = ['CoreNLP NER tags']
message_CoreNLP_NER_tags = "The CoNLL table produced by the CoreNLP parser has a record for each token in the document(s) processed.\n\nIf you are planning to produce frequency distributions of NER tags directly from the CoNLL table, you need to remember that tags such as 'Date' or 'City' may be grossly overestimated. For instance, in the expression 'the day before Christmas' each word 'the,' 'day,' 'before,' 'Christmas' will be tagged as NER date. The same is true for NER CITY tags such as 'New York City.'\n\nA better way to obtain frequency distributions of NER values is to run the NER annotators from the 'Stanford_CoreNLP_NER_main.py.'"

title_options_CoreNLP_POS_NER_maxlen = ['CoreNLP POS/NER max sentence length']
message_CoreNLP_POS_NER_maxlen = "The CoreNLP POS/NER annotators set a maximum sentence length for processing.\n\nSentences longer that your selected max length will be cut and some POS/NER tags in those long sentences may be be lost."

title_options_memory = ['Available memory']
message_memory = 'Your computer may not have enough memory to run some of the more resource-intensive algorithms of Stanford CoreNLP (e.g., coreference or some neural network models)\n\nStill, there are several options you may take (e.g., splitting up long documents into shorter parts and feeding tem to CoreNLP; checking your sentence length statistics - anything above 70 will most likely give you troubles, cnsidering that the average sentence length in modern English is 20 words). On Stanford Core NLP and memory issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.'

title_options_CoreNLP_percent = ['% sign in file']
message_CoreNLP_percent = 'The file contains % sign. This will break Stanford CoreNLP annotators. The % sign was temporarily replaced with "percent" for processing. But... you should run the script "Convert non-ASCII apostrophes & quotes and % to percent" to change the sign permanently.'

title_options_CoNLL_table = ['CoNLL table']
message_CoNLL_table = 'The CoNLL table produced by the Stanford CoreNLP parser is the input to a number of NLP Suite algorithms.\n\nPLEASE, DO NOT TINKER WITH THE CONLL TABLE OR MANY NLP SUITE ALGORITHMS WILL FAIL.'

title_options_CoreNLP_split_files = ['CoreNLP split files']
message_CoreNLP_split_files = 'Stanford CoreNLP has a limit of 100,000 characters maximum text size.\n\nThe input file was automatically split into chunks smaller than 100K characters size, fed to Stanford CoreNLP and the output recomposed into a single file.\n\nSplit files are created in a sub-folder named "split_files" inside the directory where the input txt files are located, regardless of the choice of output directory.\n\nIf you are processing files in a directory, other files may similarly need to be split and the message display may become annoying.'

title_options_CoreNLP_sentence_length = ['CoreNLP sentence length']
message_CoreNLP_sentence_length = "The length of the current sentence exceeds 100 words. The average sentence length in modern English is 20 words.\n\nMore to the point, Stanford CoreNLP's performance deteriorates with sentences with more that 70/100 words.\n\nYou should run the algorithm that extracts all sentences from a corpus and computes sentence length. This will allow you to either edit the sentence manually or perhaps run the algorithm that will add full stops (.) to sentences without end-of-sentence markers (too many sentences of this kind, one after the other, can create unduly long sentences).\n\nOn Stanford CoreNLP and memory and performance issues and what to do about them, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nIf you are processing files in a directory, other files may similarly need to be split and the message display may become annoying."

title_options_Output_directory_of_split_files = ['Output directory of split files']
message_Output_directory_of_split_files = 'This is a reminder that all file splitter scripts save the split files inside a subdirectory by the name of split_files of the directory where the input txt files are located, regardless of the choice of output directory.'

title_options_non_utf8 = ['file not utf-8 compliant']
message_non_utf8 = 'The file contains non-utf-8 compliant characters. The file cannot be processed. Please, run he utf-8 file check to get a csv sting of all non-utf-8 compliantt characters.'

title_options_Plagiarist = ['Plagiarist']
message_Plagiarist = "The 'plagiarist' script, based on Lucene, can process files with embedded dates.\n\nIf the filenames in the input directory embed dates, please tick the checkbox 'Filename embeds date' above."

title_options_IO_configuration = ['Input/Output configurations']
message_IO_configuration = 'Most GUIs in the NLP Suite provide two types of Input/Output (I/O) configurations that specify your selection for your input file or directory (these are mutually exclusive; you can only select one or the other) and output directory:\n\n  Default I/O configuration\n  Alternative I/O configuration\n\nThe Default I/O configuration applies to ALL GUIs in the NLP Suite. This is an ideal option if you work exclusively, or mostly, with the same input file(s) regardless of GUI (i.e., NLP algorithms); you would not need to select these options for every GUI.\n\nIf you occasionally need to run a script using a different set of I/O options, setup the Alternative I/O configuration. This will not affect your I/O selections for all GUIs and will only apply to a specific GUI if you chose the menu option Alternative I/O configuration.'

title_options_IO_setup = ['Input/Output options']
message_IO_setup = 'The two widgets for INPUT FILE and INPUT DIRECTORY are mutually exclusive. You can select one OR the other but not both. Click on either button to make your selection.\n\nTo change an already selected option from FILE to DIRECTORY or from DIRECTORY to FILE, simply click on the button you want to select, make your selection, and the I/O configuration will automatically update.'

title_options_SVO_corpus = ['SVO with corpus data']
message_SVO_corpus = 'You have selected to work with a set of txt files in a directory (your corpus).\n\nBeware that SVO extraction is computationally demanding. Furthermore, depending upon the options you choose (manual coreference editing, GIS maps), it may require manual input on each input file processed.\n\nDepending upon corpus size, manual coreference editing may also not be possible, due to memory requirements.'

title_options_shape_of_stories_CoreNLP = ['Stanford CoreNLP Neural Network']
message_shape_of_stories_CoreNLP = 'The Stanford CoreNLP Neural Network approach to Sentiment analysis, like all neural network algorithms, is VERY slow. On a few hundred stories it may take hours to run.\n\nAlso, neural network algorithms are memory hogs. MAKE SURE TO ALLOCATE AS MUCH MEMORY AS YOU CAN AFFORD ON YOUR MACHINE.'

title_options_CoNLL_analyzer = ['CoNLL table analyzer']
message_CoNLL_analyzer = "The Stanford CoreNLP GUI will now open the 'CoNLL table analyzer' where you can:\n\n  1. search the words contained in the CoNLL table (the one just created or a different one) by their syntactical properties and the type of relations to other words;\n  2. compute frequency distributions of various types of linguistic objects: clauses, nouns, verbs, function words ('junk/stop' words)."

title_options_shape_of_stories_best_topic = ['Best topic estimation']
message_shape_of_stories_best_topic = 'The function that estimates the best topics is VERY slow and may take an hour or longer. You can follow its progress in command line.'

title_options_language_detection = ['Language detection']
message_language_detection = 'Language detection algorithms are very slow. The NLP Suite runs three different types of algorithms: LANGDETECT, SPACY, and LANGID.\n\nPlease, arm yourself with patience, depennding upon the number and size of documents processed.'

title_options_SSdata = ['Time to download new US SS data']
message_SSdata = 'It has been more than two years since the US Social Security gender data have been downloaded to your machine.\n\nCheck on the US Social Security website whether more current data are available at US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html'

reminder_options_GUIfrontend = ['GUI front end']
message_GUIfrontend = 'The current GUI is a convenient front end that displays all the options available for the GUI.\n\nNo Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.'

# this problem seems to have been fixed by tkinter
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

title_options_Google_Earth_CoNLL = ['GIS/Google Earth Pro with CoNLL input']
message_Google_Earth_CoNLL = "You are using a GIS visualization tool with a CoNLL table in input. The algorithm will geocode every instance of NER location tags (CITY, STATE_OR_PROVINCE, COUNTRY). But... The CoNLL table produced by the CoreNLP parser has a record for each token in the document(s) processed.\n\nThus, each word in 'New York City' would have a separate NER CITY tag.\n\nAs input, you should use the csv file of NER values produced by 'Stanford_CoreNLP_NER_main.py.'"

title_options_Google_API=['Google Maps API']
message_Google_API = 'If the heatmap produced by Google Maps is displayed correctly for a split second and then displays "Oops! Something went wrong" you probably:\n\n   1. pasted incorrectly into the API key widget the Google API key;\n   2. you may not have entered billing information when applying for an API key; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale;\n   3. you may not have enabled the Maps JavaScript API (and if you use Google for geocoding, you also need to enable the Geocoding API).\n\nPlease, check the API key, your billing information, and the API enabled and try again.'

title_options_Excel = ['Excel Charts']
message_Excel = 'The Excel chart to be displayed has hover-over effects (i.e., when you hover the mouse over chart points some information will be displayed).\n\nFirst, hover-over charts are based on Excel macros. You need to enable macros in Excel to view the chart (read the TIPS file on how to do this).\n\nSecond, if the Excel chart has nothing in it or chart titles are not displayed, you need to hover the mouse over the chart area to display the chart properly. That is how hover-over charts work.'

title_options_gensim = ['What is in your corpus - Gensim']
message_gensim = 'The Gensim topic modeling routine run from here is a reduced version of the script, meant to provide a quick overview of the topics in your corpus.\n\nFor a more in-depth analysis of topics, use the topic modeling scripts for Gensim and Mallet.'

title_options_gensim_release = ['Gensim 4.0']
message_gensim_release = 'Gensim release 4.0 removed the wrappers of other library algorithms. The algorithms running Mallet through Gensim cannot be run. Please, run Mallet using the Mallet topic modelling script to run Mallet. If your work depends on any of the Gensim modules based on wrappers (e.g., the computation of the coherence value for each topic or of the optimal number of topics), uninstall Gensim 4.0 and install Gensim 3.8.3, the last release when wrappers was supported.\n\nFor more information, please, visit the Gensim GitHub page https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4#15-removed-third-party-wrappers.'

title_options_input_csv_file = ["Input csv file"]
message_input_csv_file = "You have a csv file in the 'Select INPUT CSV file' widget. The RUN command would process this file in input rather than the file stored in the I/O configuration.\n\nPress ESC if you want to clear the 'Select INPUT CSV file' widget."

title_options_geocoder = ["GIS geocoder"]
message_geocoder = 'After the geocoding and mapping is done, please, check carefully the results. If you are geocoding locations such as Athens or Rome in Georgia, most likely they will be geocoded in Greece and Italy. If you specify the United States as the country bias, the geocoder may select Rome, New York, or Indiana, or Illinois, rather than Georgia. To make sure the geocoded Rome is in Georgia, you may need to edit the geocoded csv file, adding Georgia as the state, e.g., Rome, Georgia.'

title_options_wordclouds = ['Web-based word clouds services']
message_wordclouds = "After the selected web-based word-clouds service opens up on your browser, you will need to either copy/paste the text you want to visualize or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file."

def create_remindersFile() -> None:
    """
    Generate The Reminder List with Default Text

    Args:
        path - the path to the reminders file
    """
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    if not os.path.exists(GUI_IO_util.remindersPath):
        os.makedirs(GUI_IO_util.remindersPath, exist_ok=True)
    if not os.path.isfile(remindersFile):
        # save new reminders file
        with open(remindersFile, "a", newline='', encoding='utf-8',
                  errors='ignore') as reminders:  # write a new row in the reminder csv file
            writer = csv.writer(reminders)
            writer.writerow(['Routine', 'Title', 'Message', 'Event', 'Status'])
            reminders.close()

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
def getReminders_list(config_filename,silent=False):
    routine=config_filename[:-len('-config.txt')]
    title_options=[]
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    try:
        df = pd.read_csv(remindersFile)
    except FileNotFoundError:
        if silent == False:
            mb.showwarning(title='Reminders file generated', message="The reminders.csv file saved in the reminders subdirectory was not found. If this is your first time running NLP Suite, do not worry. A default reminders.csv has been automatically generated for you.")
        create_remindersFile()
        return getReminders_list(config_filename, silent)
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

# when displaying messages the message field is '' since the actual message is not known until the csv file is read
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
    if currentStatus!=status:
        saveReminder(df,row_num, message, event, status)

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
        title_options = getReminders_list(config_filename)
    else:
        if len(title_options)==0:
            title_options = getReminders_list(config_filename)
            if len(title_options)==0: # ill formed reminders
                return None
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    try:
        df = pd.read_csv(remindersFile)
    except FileNotFoundError:
        create_remindersFile()
        # mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory was not found. If this is your first time running NLP Suite, do not worry. A default reminders.csv has been automatically generated for you.")
        return checkReminder(config_filename, title_options, message, triggered_by_GUI_event)
    except Exception:
        mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
        return None # open_message
    # get the row number of the routine that we are looking at
    silent = False
    for title in title_options:
        routines = routine.split(';') # if more routines use the same reminder; NOT used
        for routine in routines:
            df1 = df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
            if len(df1) == 0:
                # if the title does not exist for a given routine try to see if a universal routine (*) is available
                df1 = df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
            if len(df1) != 0:
                row_num = df1.index[0]
                # message_csv = df1.at[row_num, "Message"]
                # if message != '' and message != message_csv:
                #     message = df1.at[row_num, "Message"]
                event = df1.at[row_num, "Event"]
                status = df1.at[row_num, "Status"]
                # save any status changes or messages in reminders.csv file different from the Python reminder message in this scrit
                #   always update the reminder message in reminders.csv file if we changed the message programmatically
                message_csv = df1.at[row_num, "Message"].replace("\\n", os.linesep)
                if message != '' and message != message_csv:
                    # must save the new message
                    saveReminder(df, row_num, message, event, status)
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
def saveReminder(df,row_num, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    df.at[row_num, "Message"] = message # change it to yes or no
    df.at[row_num, "Event"] = event # change it to yes or no
    df.at[row_num, "Status"] = status # change it to yes or no
    df.to_csv(remindersFile, index=False, header=True)

def insertReminder(routine,title, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    with open(remindersFile, "a",newline = '', encoding='utf-8',errors='ignore') as reminders:#write a new row in the reminder csv file
        writer = csv.writer(reminders)
        writer.writerow([routine, title, message, event, status])
        reminders.close()

