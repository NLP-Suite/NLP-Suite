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

# reminders content for specific GUIs are set in the csv file reminders
# check if the user wants tadded the release_version.txt fio see the message again
# reminders are typically called from GUIs (at the bottom)
#   but can also be called from main or util scripts
#       e.g., file_splitter_util
#       e.g., GIS_geocoder_util

# below is a lit of most reminders called from various scripts with their title_options and message

title_options_language_tool = ['Language & NLP tool']
message_language_tool = 'The selected NLP tool is not available for the selected language.'

title_options_English_language_WordNet = ['English language & WordNet']
message_English_language_WordNet = 'WordNet is only available for texts in the English language.'

title_options_English_language_Gensim = ['English language & Gensim topic modeling']
message_English_language_Gensim = 'Gensim topic modeling is only available for texts in the English language.'

title_options_English_language_MALLET = ['English language & MALLET topic modeling']
message_English_language_MALLET = 'MALLET topic modeling is only available for texts in the English language.'

#The core text analyses of the NLP Suite are based on the FREEWARE Stanford CoreNLP. You can download Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n   3. GEPHI. The visualization of network graphs requires the installation of the FREEWARE software Gephi. You can download and install Gephi at https://gephi.org/users/download/\n\n   4. GOOGLE EARTH PRO. The visualization of geographic maps requires the installation of the FREEWARE software Google Earth Pro. You can download and install Google Earth Pro at https://www.google.com/earth/versions/#download-pro.\n\n   5. MALLET. MALLET topic modelling requires the installation of the FREEWARE MALLET. You can download and install MALLET at http://mallet.cs.umass.edu/download.php.
# message_NLP_Suite_welcome = 'Welcome to the NLP Suite a package of Python 3 and Java tools designed for text processing and visualization. The Suite requires several FREWARE software components in order to run. You will need to download and install them or some functionality will be lost for some of the scripts (e.g., you cannot do any textual analysis of any kind without Stanford CoreNLP or produce any geographic maps without Google Earth Pro).'

title_options_missing_external_software_NLP_main_GUI = ['Missing external software NLP_menu_main GUI']
message_missing_external_software_NLP_main_GUI = 'At least some external software has not been installed. \n\nSome of the algorithms that require the software will not run.\n\nPlease, click on the button "Setup external software" in the NLP_menu_main GUI to download/install all software.'

title_options_missing_external_software_any_main_GUI = ['Missing external software any GUI']
message_missing_external_software_any_main_GUI = 'At least some external software has not been installed. \n\nSome of the algorithms that require the software will not run.\n\nPlease, using the dropdown menu "Setup" at the bottom of this GUI, select "Software download & install," to download/install external software.'

title_options_TensorFlow = ['TensorFlow and Mac M1 and M2 chips']
message_TensorFlow = 'The NLP package BERT used in the NLP Suite rely on the Google Machine Learning platform TensorFlow.\nOn a Mac with the new M1 or M2 chip TensorFlow may lead to various errors displayed in terminal (e.g., semaphore, zsh: illegal hardware instruction) and an inability to run any of the scripts in the NLP Suite.\n\nIf you do experience this problem, while waiting for a more permanent solution to the problem, follow the instructions provided here by Apple\n\nhttps://developer.apple.com/metal/tensorflow-plugin/'

title_options_NLP_Suite_architecture = ['NLP Suite architecture & filenames']
message_NLP_Suite_architecture = 'The Python scripts in the NLP Suite have filenames that clearly identify the Suite architecture.\n\nThe filename suffix designates two different types of files: _main and _util.\n\n_main files are the only ones that you can run in command line independently of others; they may call _util files.\n\nThe _main files, with their GUI options, lay out on the screen the widgets of a script for easy Graphical User Interface (GUI).\n\nALL SCRIPTS SUFFIXED BY _main CAN BE RUN INDIPENDENTLY OF THE NLP SUITE. Thus on command line you can type\nPython knowledge_graphs_main.py\nand it will fire up the annotator GUI independently of NLP_main.py.\n\nThe filename prefix cluster together scripts used for the same purpose. Thus annotator identifies all files dealing with html annotation.'

title_options_NLP_Suite_reminders = ['NLP Suite reminders']
message_NLP_Suite_reminders = 'Several NLP Suite scripts will fire up reminders for the user. You can turn them off once you are familiar with a script. You can always turn any reminder back ON (or OFF for that matter) if you select the reminders dropdown menu at the bottom of each GUI and then select a specific reminder (if reminders are available for that GUI).'

title_options_SVO_system_requirements = ['SVO system requirements']
message_SVO_system_requirements = 'The extraction and visualization of SVOs requires several software components.\n\n1. The extraction of SVOs requires the Stanford CoreNLP set of NLP tools. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP requires to have the Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/\n\n3. The visualization of the SVO output as GIS maps and network graphs further requires the installation of the FREEWARE software Gephi and Google Earth Pro.\n\n3a. You can download and install the FREEWARE GEPHI at https://gephi.org/users/download/\n\n3b. You can download and install the FREEWARE GOOGLE EARTH PRO at https://www.google.com/earth/versions/#download-pro'

title_options_SVO_input = ['SVO input']
message_SVO_input = "The SVO pipeline allows you to start from a TXT file in input and extract from it via OpenIE the SVOs and visualize them.\n\nBut you can also select a CSV file in input, the output file previosuly created by OpenIE characerized by the suffix '-svo.csv', and use that file to visualize the results without having to rerun OpenIE."

title_options_SVO_corpus = ['SVO with corpus data']
message_SVO_corpus = 'You have selected to work with a set of txt files in a directory (your corpus).\n\nBeware that SVO extraction with Stanford CoreNLP is computationally demanding. Furthermore, depending upon the options you choose (manual coreference editing, GIS maps), it may require manual input on each input file processed.\n\nDepending upon corpus size, manual coreference is also not possible, due to memory requirements.'

title_options_SVO_output = ['SVO output']
message_SVO_output = 'The SVO pipeline will create in output an SVO subdirectory inside the main output directory.\n\nDepending upon the options you select it will also create different subdirectories (e.g., GIS, WordNet) inside the SVO subdirectory. Contrary to this, the creference resolution option will create a subdirectory inside the main output directory rather than the SVO subdirectory, since coreferenced files can then be used as input to any NLP algorithms.\n\nDepending upon the options you select, the SVO pipeline will produce different types of files: cvf files, wordcloud image, Google Earth Pro map, and Gephi network graph.\n\nWhile cvf and png files are easy to read, less so are Google Earth Pro kml files and, particularly, Gephi gexf files.\n\nPLEASE, read the Gephi TIPS file before you run the SVO pipeline.'

title_options_SVO_default = ['SVO default visualization options']
message_SVO_default = 'The SVO algorithms use default settings for visualizing results in Python Wordclouds and Google Earth Pro. If you want to customize the visualization options, please, use the Wordclouds GUI and the GIS Google Earth GUI with the csv files produced by SVO in input.'

title_options_no_SVO_records = ['No SVO records extracted']
message_no_SVO_records = 'The SVO algorithms have not extracted any SVOs. If you have selected to filter Subject and/or Verb, the filtering algorithms may have excluded available records.\n\nYou may want to untick either/both checkboxes and try again.'

title_options_SVO_someone = ['SVO Someone?']
message_SVO_someone = 'The SVO algorithms convert passive sentences into active ones. When no subject is present (e.g., "A beautiful car was bought"), a subject is automatically added as Someone?.'

title_options_CoreNLP_pronouns = ['CoreNLP pronouns detected']
message_CoreNLP_pronouns = 'The CoreNLP algorithms have detected the presence of pronouns (e.g., he, she). You should run the coreference annotator to resolve the coreferences.'

title_options_CoreNLP_gender = ['CoreNLP gender annotator']
message_CoreNLP_gender = 'The gender annotator is only available for the Stanford CoreNLP package and the English language.'

title_options_CoreNLP_quote = ['CoreNLP quote/speaker annotator']
message_CoreNLP_quote = 'The quote/speaker annotator is only available for the Stanford CoreNLP package and the English language.'

title_options_Stanza_languages = ['Stanza languages']
message_Stanza_languages = 'Pressing + with the default language option "English" displayed in the dropdown menu, will add "English" to the list of languages processed by Stanza. If you do not wish to include "English," please, click the Reset button first then add the languages to be processed one at a time.'

title_options_GIS_Nominatim = ['GIS Nominatim geocoder']
message_GIS_Nominatim = "If the Nominatim geocoder service exits with the error 'too many requests', you can break up the csv location file and process each subfile for geocoding as normal csv files."

title_options_Google_Earth_Pro_download = ['Google Earth Pro']
message_Google_Earth_Pro_download = 'The GIS pipeline requires a copy of the FREEWARE Google Earth Pro installed on your machine in order to visualize the kml files produced for Google Earth Pro.\n\nYou can download and install the FREEWARE GOOGLE EARTH PRO for desktop at https://www.google.com/earth/versions/'

title_options_VADER = ['VADER']
message_VADER = 'VADER heavily relies on a number of NLTK libraries. If VADER fails to run, make sure that in command line you run\n\npython -m nltk.downloader all'

title_options_WordNet_system_requirements = ['WordNet system requirements']
message_WordNet_system_requirements = 'The scripts in this GUI require the FREEWARE WordNet on your machine. You can download WordNet at https://wordnet.princeton.edu/download/current-version.'

title_options_WordNet_inputFilename_button = ['WordNet input file button']
message_WordNet_inputFilename_button = 'The Select INPUT file button is disabled (grayed out) when you open WordNet. Different options require either no file or different file types.\n\nPlease, tick a checkbox to activate the button.'

title_options_WordNet_verb_aggregation = ['WordNet VERB aggregation']
message_WordNet_verb_aggregation = "CAVEAT!\n\nFor VERBS, the aggregated 'stative' category includes the auxiliary 'be' probably making up the vast majority of stative verbs. Similarly, the category 'possession' include the auxiliary 'have' (and 'get'). You may wish to exclude these auxiliary verbs from frequencies.\n\nThe WordNet_UP function will automatically compute VERB frequencies with/without auxiliaries and display both Excel charts."

title_options_spaCy_parameters = ['spaCy annotators']
message_spaCy_parameters = 'Contrary to Stanford CoreNLP and Stanza, spaCy does not process specific annotators (e.g., POS, NER). Regardless of selected annotator, spaCy will also process the corpus with its full parser.'

title_options_topic_modeling = ['What is in your corpus - Topic modeling']
message_topic_modeling = 'The topic modeling option requires in input a set of txt documents, rather than a single txt file. The topic modeling option is disabled for single documents.'

title_options_topic_modeling_gensim = ['What is in your corpus - Topic modeling Gensim']
message_topic_modeling_gensim = 'The Gensim topic modeling routine run from here is a reduced version of the script, meant to provide a quick overview of the topics in your corpus.\n\nFor a more in-depth analysis of topics, use the topic modeling scripts for Gensim and MALLET.'

title_options_GIS_redundancy = ['What is in your corpus - GIS redundant options']
message_GIS_redundancy = 'You are running simultaneously two options that are redundant: "References to geographical locations (CoreNLP NER)" under "What else is in your document(s)?" and "GIS (Geographic Information System) pipeline".\n\nThe GIS option has the advantage that it extracts locations via CoreNLP NER annotator and maps them via Google Earth Pro and Google Maps. But... you need to install these freeware software options.'

title_options_gensim_release = ['Gensim 4.0']
message_gensim_release = 'Gensim release 4.0 removed the wrappers of other library algorithms. The algorithms running MALLET through Gensim cannot be run. Please, run MALLET using the MALLET topic modelling script to run MALLET. If your work depends on any of the Gensim modules based on wrappers (e.g., the computation of the coherence value for each topic or of the optimal number of topics), uninstall Gensim 4.0 and install Gensim 3.8.3, the last release when wrappers was supported.\n\nFor more information, please, visit the Gensim GitHub page https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4#15-removed-third-party-wrappers.'

title_options_Mallet_installation = ['MALLET download and installation']
message_Mallet_installation = 'The MALLET topic modelling tool requires a copy of the FREEWARE MALLET installed on your machine. You can download the FREEWARE MALLET at http://mallet.cs.umass.edu/download.php.\n\nMALLET in turn requires a copy of the JAVA development kit installed on your machine.\n\nRead carrefully the MALLET and Java installation TIPS.'

title_options_topic_modelling_number_of_topics = ['Topic modelling: Number of topics']
message_topic_modelling_number_of_topics = 'You are running the topic modelling algorithm with the default value of 20 topics.\n\nYOU ARE STRONGLY ADVISED to run the algorithm repeatedly with different number of topics (e.g., 50, 40 30, 20, 10). You should then select the number of topics that gives you the best set of topics with no or minimum word overlap across topics. When running Gensim, the topic circles displayed in the Intertopic Distance Map (via multidimensional scaling) should be scattered throughout the four quadrants and should not be overlapping.'

title_options_Word2Vec = ['Word2Vec HTML visual']
message_Word2Vec = 'The Word2Vec HTML visual may be very messy.\n\nDepending upon the number of words displayed, it will be impossible to see anything but a black blotch.\n\nIf that happens, with your mouse, draw an area you want to focus on in the Cartesian plane where the image is displayed. It will re-displayed with a much clearer focus. You can repeat that operation in the new display to further zoom in.\n\nYOU CAN GO BACK TO THE ORIGINAL DISPLAY BY CLICKING THE REFRESH BUTTON IN YOUR BROWSER.'

title_options_Word2Vec_eucledian_distance = ['Word2Vec Eucledian distance']
message_Word2Vec_eucledian_distance = 'The Word2Vec algorithms compute the Eucledian distance of every word with every other word for the 10 most frequent words. You can use this csv file to locate the most significant words in the Cartesian space.'

title_options_CoreNLP_Sentiment_Analysis_system_requirements = ['Stanford CoreNLP Sentiment Analysis system requirements']
message_CoreNLP_Sentiment_Analysis_system_requirements = 'The Stanford CoreNLP Sentiment Analysis tool requires two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'

title_options_CoreNLP_system_requirements = ['Stanford CoreNLP system requirements']
message_CoreNLP_system_requirements = 'Some of the NLP tools in this GUI require two components.\n\n1. A copy of the FREEWARE Stanford CoreNLP suite installed on your machine. You can download the FREEWARE Stanford CoreNLP at https://stanfordnlp.github.io/CoreNLP/download.html.\n\n2. CoreNLP, in turn, requires to have the FREEWARE Java installed. You can download and install the FREEWARE JAVA at https://www.java.com/en/download/'

# not used
title_options_CoreNLP_Java = ['Stanford CoreNLP Java 64-Bits']
message_CoreNLP_Java = 'The Java call to Stanford CoreNLP script uses the property -d64 for the 64 bits JAVA. Java is normally set to 32 bits Virtual Machine as default on a Windows machine. If you see an error the property -d64 is not recognized, you will need to change the Java default to 64 bits VM.\n\nTo test your VM settings, open  command prompt/terminal and type Java - version. You should see "64-Bit Server VM" in the last line of output.'

title_options_CoreNLP_coref = ['Stanford CoreNLP coref merged files']
message_CoreNLP_coref = "The Stanford CoreNLP coref annotator with a corpus of files in a directory in input will create a merged corefed file (with filenames embedded in <@# #@>) in output.\n\nManual coreference resolution will not be available; depending upon the number of files merged, bringing the files into memory for manual editing may exceed memory capacity. You can always\n   1. manually edit the merged file anyway using the 'coreference_main' GUI;\n   2. split the merged file and then edit the individual coreferenced files, again, using the 'coreference_main' GUI."

title_options_only_CoreNLP_coref = ['Stanford CoreNLP coreference']
message_only_CoreNLP_coref = "The coreference algorithms in this GUI are based exclusively on Stanford CoreNLP coref annotator.\n\nWatch this space for an extension to spaCy of coreference resolution (Stanza relies on Stanford CoreNLP coreference annotator)."

title_options_only_CoreNLP_NER = ['Stanford CoreNLP NER']
message_only_CoreNLP_NER = "The NER algorithms in this GUI are based exclusively on Stanford CoreNLP NER annotator.\n\nWatch this space for an extension to spaCy and Stanza of the NER algorithms behind this GUI (the spaCy and Stanza parsers and NER annotators, however, do prooduce NER tags)."

title_options_only_CoreNLP_CoNLL_analyzer = ['CoNLL table analyzer']
message_only_CoreNLP_CoNLL_analyzer = "The CoNLL table analyzer algorithms in this GUI are based exclusively on Stanford CoreNLP parser.\n\nWatch this space for an extension to spaCy and Stanza of the NER algorithms behind this GUI."

title_options_only_CoreNLP_CoNLL_repetition_finder = ['K sentences repetition finder in CoNLL table']
message_only_CoreNLP_CoNLL_repetition_finder = "In the CoNLL table analyzer GUI there is another K-sentences repetition finder algorithm. It provides data based based on the CoNLL table POS tags on counts and proportions of nouns, verbs, adjectives, and proper nouns in the first and last K sentences of a document."

lemma_frequencies = ['Lemma frequency']
message_lemma_frequencies = "A blank is likely to be a frequent lemma in your corpus. It is likely to 'mask' all other values. If that is the case, when the chart is displayed you may want to delete rows containing a blank lemma to have a better view of all other values."

NER_frequencies = ['NER tags frequency']
message_NER_frequencies = "O is likely to be the most frequent NER tag in your corpus. It is likely to 'mask' all other tags. If that is the case, when the chart is displayed you may want to delete the row containing the O tag in the Data worksheet of the Excel chart file to have a better view of all other tags."

DepRel_frequencies = ['DepRel tags frequency']
message_DepRel_frequencies = "punct (punctuation) and det (determiner/article) are likely to be the most frequent DepRel tags in your corpus. It is likely to 'mask' all other tags. If that is the case, when the chart is displayed you may want to delete in the Data worksheet of the Excel chart file the rows containing the 'punct' and 'det' tags to have a better view of all other tags."

title_options_CoreNLP_shutting_down = ['CoreNLP Server is shutting down']
message_CoreNLP_shutting_down = "The Stanford CoreNLP, after firing up, will display on command line/prompt the message: CoreNLP Server is shutting down.\n\nIt is NOT a problem. The process will continue..."

title_options_CoreNLP_NER_tags = ['CoreNLP NER tags']
message_CoreNLP_NER_tags = "The CoNLL table produced by the CoreNLP parser has a record for each token in the document(s) processed.\n\nIf you are planning to produce frequency distributions of NER tags directly from the CoNLL table, you need to remember that tags such as 'Date' or 'City' may be grossly overestimated. For instance, in the expression 'the day before Christmas' each word 'the,' 'day,' 'before,' 'Christmas' will be tagged as NER date. The same is true for NER CITY tags such as 'New York City.'\n\nA better way to obtain frequency distributions of NER values is to run the NER annotators from the 'Stanford_CoreNLP_NER_main.py.'"

title_options_CoreNLP_website = ['CoreNLP language/annotator options website']
message_CoreNLP_website = "You will be asked next if you want to open the Stanford CoreNLP language website to get a list of available annotators for each supported language.\n\nIf you do not want to be asked again to open the website, just hit 'No' below."

title_options_TIPS_file = ['Open TIPS file']
message_TIPS_file = "You will be asked next if you want to open a TIPS file for help.\n\nIf you do not want to be asked again to open the TIPS file, just hit 'No' below."

title_options_CoreNLP_POS_NER_maxlen = ['CoreNLP POS/NER max sentence length']
message_CoreNLP_POS_NER_maxlen = "The CoreNLP POS/NER annotators set a maximum sentence length for processing.\n\nSentences longer than your selected max length will be cut and some POS/NER tags in those long sentences may be lost."

title_options_CoreNLP_nn_parser = ['Clause tags with CoreNLP neural network parser']
message_CoreNLP_nn_parser = "The CoreNLP neural network parser does not produce clause tags in output. The column 'Clause Tag' in the output csv CoNLL table would contain all blank values."

title_options_CoreNLP_quote_annotator = ['CoreNLP quote annotator']
message_CoreNLP_quote_annotator = "The CoreNLP quote annotator works with double quotes as default \" rather than with single quotes \'. If your document(s) use single quotes for dialogue, make sure to tick the checkbox \'Include single quotes\'. The Stanford CoreNLP annotator will then process BOTH single AND double quotes, otherwise single quotes for dialogues would be missed (e.g., The user said: 'This NLP Suite sucks.')."

title_options_memory = ['Available memory']
message_memory = 'Your computer may not have enough memory to run some of the more resource-intensive algorithms of Stanford CoreNLP (e.g., coreference or some neural network models)\n\nStill, there are several options you may take (e.g., splitting up long documents into shorter parts and feeding tem to CoreNLP; checking your sentence length statistics - anything above 70 will most likely give you troubles, cnsidering that the average sentence length in modern English is 20 words). On Stanford Core NLP and memory issues, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.'

title_options_CoreNLP_percent = ['% sign in file']
message_CoreNLP_percent = 'The file contains % sign. This will break Stanford CoreNLP annotators. The % sign was temporarily replaced with "percent" for processing. But... you should run the script "Convert non-ASCII apostrophes & quotes and % to percent" to change the sign permanently.'

title_options_CoNLL_table = ['CoNLL table']
message_CoNLL_table = 'The CoNLL table produced by the Stanford CoreNLP parser is the input to a number of NLP Suite algorithms.\n\nPLEASE, DO NOT TINKER WITH THE CONLL TABLE OR MANY NLP SUITE ALGORITHMS WILL FAIL.'

title_options_CoNLL_analyzer = ['CoNLL table analyzer']
message_CoNLL_analyzer = "The Stanford CoreNLP GUI will now open the 'CoNLL table analyzer' GUI. When the GUI opens, you will need to select theGUI-specific I/O configuration.\n\nIn the 'CoNLL table analyzer' GUI you can:\n\n  1. search the words contained in the CoNLL table (the one just created or a different one) by their syntactical properties and the type of relations to other words;\n  2. compute frequency distributions of various types of linguistic objects: clauses, nouns, verbs, function words ('junk/stop' words)."

title_options_CoNLL_table_verb_modality = ['CoNLL table - Verb modality']
message_CoNLL_table_verb_modality = 'The categories of Verb modality (Obligation, Will/would, Can/may) computed from the CoNLL table are NOT mutually exclusive. The same verb may appear in several categories.'

title_options_CoreNLP_split_files = ['CoreNLP split files']
message_CoreNLP_split_files = 'Stanford CoreNLP has a limit of 100,000 characters maximum text size.\n\nThe input file was automatically split into chunks smaller than 100K characters size, fed to Stanford CoreNLP and the output recomposed into a single file.\n\nSplit files are created in a sub-folder named "split_files" inside the directory where the input txt files are located, regardless of the choice of output directory.\n\nIf you are processing files in a directory, other files may similarly need to be split and the message display may become annoying.'

title_options_CoreNLP_sentence_length = ['CoreNLP sentence length']
message_CoreNLP_sentence_length = "The length of the current sentence exceeds 100 words. The average sentence length in modern English is 20 words.\n\nMore to the point, Stanford CoreNLP's performance deteriorates with sentences with more that 70/100 words.\n\nYou should run the algorithm that extracts all sentences from a corpus and computes sentence length. This will allow you to either edit the sentence manually or perhaps run the algorithm that will add full stops (.) to sentences without end-of-sentence markers (too many sentences of this kind, one after the other, can create unduly long sentences).\n\nOn Stanford CoreNLP and memory and performance issues and what to do about them, please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.\n\nIf you are processing files in a directory, other files may similarly need to be split and the message display may become annoying."

title_options_Output_directory_of_split_files = ['Output directory of split files']
message_Output_directory_of_split_files = 'This is a reminder that all file splitter scripts save the split files inside a subdirectory by the name of split_files of the directory where the input txt files are located, regardless of the choice of output directory.'

title_options_line_length = ['Line length']
message_line_length = 'Line length only makes sense for poetry or song lyrics (or perhaps for newspaper articles to gauge the importance of the article by the column width).\n\nFor your typical document line length depends on the vaguaries of typesetting and sentence length may provide a better measure of style.'

title_options_non_utf8 = ['file not utf-8 compliant']
message_non_utf8 = 'The file contains non-utf-8 compliant characters. The file cannot be processed. Please, run he utf-8 file check to get a csv sting of all non-utf-8 compliantt characters.'

title_options_Plagiarist = ['Plagiarist']
message_Plagiarist = "The 'plagiarist' script, based on Lucene, can process files with embedded dates.\n\nIf the filenames in the input directory embed dates, please tick the checkbox 'Filename embeds date' above."

title_options_IO_configuration = ['Input/Output configurations']
message_IO_configuration = 'Most GUIs in the NLP Suite provide two types of Input/Output (I/O) configurations that specify your selection for your input file or directory (these are MUTUALLY EXCLUSIVE. YOU CAN ONLY HAVE ONE OR THE OTHER BUT NOT BOTH) and output directory:\n\n  Default I/O configuration\n GUI-specific I/O configuration\n\nThe Default I/O configuration applies to ALL GUIs in the NLP Suite. This is an ideal option if you work exclusively, or mostly, with the same input file(s) regardless of GUI (i.e., NLP algorithms); you would not need to select these options for every GUI.\n\nIf you occasionally need to run a script using a different set of I/O options, setup theGUI-specific I/O configuration. This will not affect your I/O selections for all GUIs and will only apply to a specific GUI if you chose the menu optionGUI-specific I/O configuration.'

title_options_IO_setup = ['Input/Output options']
message_IO_setup = 'The two widgets for INPUT FILE and INPUT DIRECTORY are mutually exclusive. You can select one OR the other but not both. Click on either button to make your selection.\n\nTo change an already selected option from FILE to DIRECTORY or from DIRECTORY to FILE, simply click on the button you want to select, make your selection, and the I/O configuration will automatically update.'

title_options_IO_setup_date_options = ['Date options']
message_IO_setup_date_options = 'Some of the algorithms in the NLP Suite (e.g., GIS models and network models) can build dynamic models (i.e., models that vary with tiime) when time/date is known.\n\n' \
                                'Tick the checkbox, if the filenames in the selected INPUT option embed a date (e.g., The New York Times_12-19-1899), the NLP Suite can use that metadata information to build dynamic models. If that is the case, using the dropdown menu, select the date format of the date embedded in the filename (default mm-dd-yyyy).\n\nPlease, enter the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _).\n\nPlease, using the dropdown menu, select the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers) (default 2)'

title_options_shape_of_stories_CoreNLP = ['Stanford CoreNLP Neural Network']
message_shape_of_stories_CoreNLP = 'The Stanford CoreNLP Neural Network approach to Sentiment analysis, like all neural network algorithms, is VERY slow. On a few hundred stories it may take hours to run.\n\nAlso, neural network algorithms are memory hogs. MAKE SURE TO ALLOCATE AS MUCH MEMORY AS YOU CAN AFFORD ON YOUR MACHINE.'

title_options_shape_of_stories = ['Shape of stories']
message_shape_of_stories = "The Sentiment Analysis GUI will now open the 'Shape of stories' GUI. When the GUI opens, you will need to select theGUI-specific I/O configuration."

title_options_shape_of_stories_best_topic = ['Best topic estimation']
message_shape_of_stories_best_topic = 'The function that estimates the best topics is VERY slow and may take an hour or longer. You can follow its progress in command line.'

title_options_language_detection = ['Language detection']
message_language_detection = 'Language detection algorithms are very slow. The NLP Suite runs three different types of algorithms: LANGDETECT, SPACY, and LANGID.\n\nPlease, arm yourself with patience, depending upon the number and size of documents processed.\n\nStanza, contrary to the other algorithms, does not compute the probability of language detection.'

title_options_SSdata = ['Time to download new US SS data']
message_SSdata = 'It has been more than two years since the US Social Security gender data have been downloaded to your machine.\n\nCheck on the US Social Security website whether more current data are available at US Social Security website\n\nhttps://www.ssa.gov/oact/babynames/limits.html'

reminder_options_GUIfrontend = ['GUI front end']
message_GUIfrontend = 'The current GUI is a convenient front end that displays all the options available for the GUI.\n\nNo Input/Output options are displayed in this GUI since any selected option, when RUN, will open a specialized GUI with its own Input/Output requirements.'

# this problem seems to have been fixed by tkinter
title_options_Mac_tkinter_bug = ['tkinter MacOS bug']
message_Mac_tkinter_bug = 'MacOS bug in tkinter (https://www.python.org/download/mac/tcltk/).\n\nPython\'s integrated development environment, IDLE, and the tkinter GUI toolkit it uses, depend on the Tk GUI toolkit which is not part of Python itself. For best results, it is important that the proper release of Tcl/Tk is installed on your machine. For recent Python installers for macOS downloadable from this website, here is a summary of current recommendations followed by more detailed information.'

title_options_DBpedia_YAGO = ['DBpedia/YAGO options']
message_DBpedia_YAGO = "You have several options available. You can\n   1. select an ontology class, using the dropdown menu;\n   2. enter a sub-class in the \'Sub-class\' widget taking the value from the TIPS files on ontology classes;\n   3. you can enter both class and sub-class if needed.\n\nAfter selecting/entering a class, several widgets will become available. You can select a color to be associated to the selected class; blue will be the default color if none is selected; you can select the same color for different classes.\n\nAfter selecting class (and perhaps sub-class and color), press\n   1. 'Reset' to start all over;\n   2. 'Show' to display the choices made thuus far;\n   3. + to approve the choices made and possibly add new choices.\n\nThen press RUN.\n\nCompared to DBpedia, YAGO can be much slower (10 seconds vs. 1 minute for a short document)."

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

title_options_GIS_GUI = ['GIS default GUI options']
message_GIS_GUI = 'The options available on the GUI have been automatically set for you depending upon the type of input file selected: txt or csv.\n\nWith a TXT file, NER extraction via Stanford CoreNLP must be first performed.\n\nWith a CSV file, the script checks whether the file is a CoNLL table, a geocoded file containing latitude and longitude values, or a file containing a list of locations that need to be geocoded.'

title_options_GIS_default = ['GIS default visualization options']
message_GIS_default = 'The Google Earth Pro visualization options in the GIS GUI are set by default. If you want to customize Google Earth Pro, please, use the GIS Google Earth GUI with the list of locations or of geocoded locations produced by the GIS pipeline as csv files.'

title_options_GIS_OpenIE_SENNA = ["GIS with OpenIE & SENNA"]
message_GIS_OpenIE_SENNA = 'OpenIE and SENNA do not extract geocodable locations that can be mapped. Please, use another option if you want to produce maps.'

title_options_geocoder = ["GIS geocoder"]
message_geocoder = 'After the geocoding and mapping is done, please, check carefully the results. If you are geocoding locations such as Athens or Rome in Georgia, most likely they will be geocoded in Greece and Italy. If you specify the United States as the country bias, the geocoder may select Rome, New York, or Indiana, or Illinois, rather than Georgia. To make sure the geocoded Rome is in Georgia, you may need to edit the geocoded csv file, adding Georgia as the state, e.g., Rome, Georgia.'

title_options_Google_Earth=['Open Google Earth GUI']
message_Google_Earth = 'You should tick the Open GUI checkbox ONLY if you wish to open the Google Earth Pro GUI.\n\nThe Google Earth Pro GUI will provide a number of options to personalize a Google Earth Pro map. Press Run if you wish to open the Google Earth Pro GUI.'

title_options_Google_Earth_CoNLL = ['GIS/Google Earth Pro with CoNLL input']
message_Google_Earth_CoNLL = "You are using a GIS visualization tool with a CoNLL table in input. The algorithm will geocode every instance of NER location tags (CITY, STATE_OR_PROVINCE, COUNTRY). But... The CoNLL table produced by the CoreNLP parser has a record for each token in the document(s) processed.\n\nThus, each word in 'New York City' would have a separate NER CITY tag.\n\nAs input, you should use the csv file of NER values produced by 'Stanford_CoreNLP_NER_main.py.'"

title_options_Google_API=['Google Maps API']
message_Google_API = 'If the heatmap produced by Google Maps is displayed correctly for a split second and then displays "Oops! Something went wrong" you probably:\n\n   1. pasted incorrectly into the API key popup widget the Google API key;\n   2. you may not have entered billing information when applying for an API key; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale;\n   3. you may not have enabled the Maps JavaScript API (and if you use Google for geocoding, you also need to enable the Geocoding API).\n\nPlease, check the API key, your billing information, and the API enabled and try again.\n\nPLEASE, read the TIPS_NLP_Google API Key.pdf for help.'

title_options_Excel_Charts = ['Excel Charts']
message_Excel_Charts = 'The Excel chart to be displayed has hover-over effects (i.e., when you hover the mouse over chart points some information will be displayed).\n\nFirst, hover-over charts are based on Excel macros. You need to enable macros in Excel to view the chart (read the TIPS file on how to do this).\n\nSecond, if the Excel chart has nothing in it or chart titles are not displayed, you need to hover the mouse over the chart area to display the chart properly. That is how hover-over charts work.\n\nThird, if the chart is displayed but the bars of a bar chart, for instance, have the same height, contrary to expectations, click on Data then on Chart to display the chart properly.'

title_options_input_csv_file = ["Input csv file"]
message_input_csv_file = "You have a csv file in the 'Select INPUT CSV file' widget. The RUN command would process this file in input rather than the file stored in the I/O configuration.\n\nPress ESC if you want to clear the 'Select INPUT CSV file' widget."

title_options_python_wordclouds_horizontal = ['Python wordclouds']
message_python_wordclouds_horizontal = "You have selected to visualize words only horizontally in the wordclouds image. Some of the lower-frequency words may need to be dropped from the wordclouds image since there may not be enough room for their display.\n\nCombining horizontal and vertical displays maximizes the number of words visualized in the wordclouds image."

title_options_wordclouds = ['Web-based wordclouds services']
message_wordclouds = "After the selected web-based wordclouds service opens up on your browser, you will need to either copy/paste the text you want to visualize or upload a text file, depending upon the word clouds service. If you wish to visualize the words in all the files in a directory, you would need to merge the files first via the file_merger_main, then use your merged file."

title_options_Gensim_Word2Vec_timing = ['Gensim Word2Vec timing']
message_Gensim_Word2Vec_timing = "Beware that Gensim Word2Vec on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, with the tokenizing, lemmatzing, and Eucledian distance options, takes approximately 2 hours on a standard laptop. Eucledian distance is the item taking the longest."

title_options_BERT_Word2Vec_timing = ['BERT Word2Vec timing']
message_BERT_Word2Vec_timing = "Beware that BERT Word2Vec on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, with the tokenizing, lemmatzing, and Eucledian distance options, takes approximately 2 hours on a standard laptop. Eucledian distance is the item taking the longest."

title_options_CoreNLP_coref_timing = ['CoreNLP coreference timing']
message_CoreNLP_coref_timing = "Beware that CoreNLP coreference resolution on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 3 hours on a standard laptop."

title_options_CoreNLP_SVO_timing = ['CoreNLP SVO timing']
message_CoreNLP_SVO_timing = "Beware that the CoreNLP SVO algorithms on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 1 hour and 20 minutes on a standard laptop."

title_options_CoreNLP_SVO_gender_quote_timing = ['CoreNLP SVO + gender + quote timing']
message_CoreNLP_SVO_gender_quote_timing = "Beware that the CoreNLP SVO + gender + quote algorithms on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 4 hours on a standard laptop."

title_options_CoreNLP_gender_timing = ['CoreNLP gender timing']
message_CoreNLP_gender_timing = "Beware that the CoreNLP gender algortithm on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 3 hours on a standard laptop."

title_options_CoreNLP_quote_timing = ['CoreNLP quote timing']
message_CoreNLP_quote_timing = "Beware that the CoreNLP quote annotator on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 3 hours on a standard laptop."

title_options_CoreNLP_normalized_date_timing = ['CoreNLP normalized date timing']
message_CoreNLP_normalized_date_timing = "Beware that the CoreNLP normalized date algortithm on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 50 minutes on a standard laptop."

title_options_CoreNLP_sentiment_timing = ['CoreNLP sentiment timing']
message_CoreNLP_sentiment_timing = "Beware that the CoreNLP sentiment algortithm on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 7 hours and 30 minutes on a standard laptop."

title_options_CoreNLP_nn_parser_timing = ['CoreNLP neural network parser timing']
message_CoreNLP_nn_parser_timing = "Beware that the CoreNLP neural network parser algortithm on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 1 hour and 40 minutes on a standard laptop."

title_options_CoreNLP_PCFG_parser_timing = ['CoreNLP PCFG parser timing']
message_CoreNLP_PCFG_parser_timing = "Beware that the CoreNLP PCFG parser on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 1 hour and 40 minutes on a standard laptop."

title_options_CoreNLP_NER_timing = ['CoreNLP NER annotator timing']
message_CoreNLP_NER_timing = "Beware that the CoreNLP NER annotator on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 50 minutes on a standard laptop."

title_options_CoreNLP_POS_timing = ['CoreNLP POS annotator timing']
message_CoreNLP_POS_timing = "Beware that the CoreNLP POS annotator on the 296 files (2042312 words total) of the President of the United States Inaugural and State of the Union speeches, takes approximately 2 minutes on a standard laptop."

title_options_GIS_timing = ['GIS timing']
message_GIS_timing = "Beware that geocoding some 30,000 locations via Nominatim and preparing the KML file for map visualization in Goodgle Earth Pro takes approximately 15 minutes on a standard laptop."

title_options_data_manager_merge = ['Merge option']
message_data_manager_merge1 = "Please, select next the field to be used as KEY for merging files."
message_data_manager_merge2 = "Please, click next the + sign on this line to select another KEY to be used for merging files or click OK to accept current selection."
# after clicking + to select another field as KEY
message_data_manager_merge3 = "Please, select next the field to be used as secondary KEY for merging files."
# after clicking OK with only one file selected
message_data_manager_merge4 = "Please, click next the + sign next to File at the top of the GUI to select another csv file to merge."
# after selecting a new file
message_data_manager_merge5 = "Please, select next the field from the newly selected file to be used as KEY for merging the new file with the previous one(s)."
# after selecting a field with at least two files selected
message_data_manager_merge6 = "Please, click next the + sign next to File at the top of the GUI to select another csv file to merge or click OK to accept the merge options and then click RUN."
# after clicking OK with at least two files selected
message_data_manager_merge7 = "Please, click next the + sign next to File at the top of the GUI to select another csv file to merge or click RUN."


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
#   The routine field contains the name used by the reminder script to visualize the correct reminder; it is the name of the config filename trimmed of _config.csv (e.g., GIS for GIS_config.csv, GIS-Google-Earth for GIS-Google-Earth_config.csv).
#   When the Routine field contains a * the reminder will be displayed in ALL GUIs

# title is the second column in reminders.csv
#   it refers to the specific Python option that calls the reminder
# message is typically stored in the reminders.csv files
#   For reminders that require a current value (e.g., date and time stamp)
#   the message is passed (an example is found in GUI_frontEnd in GUI_IO_util.py)
# triggered_by_GUI_event is passed when triggered by an event in the GUI (a checkbox ticked, a file opened)
#   (e.g., in shape_of_stories_GUI)
def getReminders_list(config_filename,silent=False):
    # if '_config.csv' in config_filename:
    routine=config_filename[:-len('_config.csv')]
    # else:
    #     routine = config_filename
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
    if len(temp) > 0:
        for t in temp:
            title_options.append(t)
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
    if message == '': # there is no message to be displayed
        return
    else:
        # message = message + question # the question "Do you want to see this message again?" is asked
        #   in GUI_IO_util.message_box_widget so that it can be placed n red
        answer = GUI_IO_util.message_box_widget(1, title, message, buttonType='Yes-No', timeout=30000)

    answer=answer.capitalize() # Yes/No
    if seeMsgAgain==True:
        if answer == 'No':
            status='OFF'
        else:
            status = 'ON'
    else:
        if answer=='Yes':
            if currentStatus == 'No' or currentStatus == 'OFF': # 'No' the old way of saving reminders
                status = 'ON'
            else:
                status = 'OFF'
        else:
            status=currentStatus
    if currentStatus!=status:
        saveReminder(df,row_num, message, event, status)

# routine is a string
# title_options is a list [] of all Routine values
# * in the Routine column are used for reminders that apply to any GUI
# set silent to True if you just want to check the status of the reminder ON or OFF without asking the question
def checkReminder(config_filename,title_options=[],message='', triggered_by_GUI_event=False, silent=False):
    # * denotes messages that apply to ALL scripts
    status=''
    if config_filename=='*':
        routine='*'
    else:
        routine = config_filename.replace('_config.csv', '')
        # routine = config_filename[:-len('_config.csv')]
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
        if not silent:
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
                if status == "Yes" or status == "ON": # 'Yes' the old way of saving reminders
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
    return status # returns Yes for ON or No for OFF

# called from a GUI when a reminder is selected from the reminder dropdown menu
# title is a string, the reminders option selected in the GUI dropdown menu
def resetReminder(config_filename,title):
    routine = config_filename[:-len('_config.csv')]
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

        message = df.at[row_num, "Message"]
        event = df.at[row_num, "Event"]
        status = df.at[row_num, "Status"]
        if status == "No" or status == "OFF":  # 'No' the old way of saving reminders
            question = '\n\nNow this reminder is turned OFF. Do you want to turn it ON?'
        else:
            question = '\n\nNow this reminder is turned ON. Do you want to turn it OFF?'
        displayReminder(df, row_num, title, message, event, status, question, False)


# update do_not_show_message.csv so that we don't show the message box again
# status: "Yes"/"No" old way of saving reminders; now ON/OFF
def saveReminder(df,row_num, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    df.at[row_num, "Message"] = message # change it to yes or no
    df.at[row_num, "Event"] = event # change it to yes or no
    df.at[row_num, "Status"] = status # change it to yes or no
    df.to_csv(remindersFile, encoding='utf-8', index=False, header=True)

def insertReminder(routine,title, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    with open(remindersFile, "a",newline = '', encoding='utf-8',errors='ignore') as reminders:#write a new row in the reminder csv file
        writer = csv.writer(reminders)
        writer.writerow([routine, title, message, event, status])
        reminders.close()

