# written by Roberto Franzosi October 2019,
# edited Spring 2020, July 2020

# input: 1. file name
# input: 1. directory name
# output: directory name

import multiprocessing
import sys

multiprocessing.freeze_support()

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NLP", ["os", "tkinter", "customtkinter"]) == False:
    sys.exit(0)

import os
from sys import platform
import tkinter as tk
import tkinter.messagebox as mb
import webbrowser

import customtkinter as ctk

import config_util
import constants_util
import GUI_IO_util
import IO_files_util
import language_tools_advisor_util
import NLP_menu_tools_util
import reminders_util
import run_script_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    input_main_dir_path = GUI_util.input_main_dir_path.get()
    output_dir_path = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    script_to_run = globals()["script_to_run"]
    IO_values = globals()["IO_values"]

    if script_to_run == "":
        mb.showwarning(
            "No option selection",
            "No option has been selected.\n\nPlease, select one of the tools in the list (browse a category or type in the search box), then click on RUN again.",
        )
        return
    IO_files_util.runScript_fromMenu_option(
        script_to_run,
        IO_values,
        inputFilename,
        input_main_dir_path,
        output_dir_path,
        openOutputFiles,
        chartPackage,
        dataTransformation,
    )


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# Show welcome screen for the first 3 launches, then go straight to the menu.
# --from-welcome flag is passed by NLP_welcome_main to avoid a redirect loop.
import json as _json

if "--from-welcome" not in sys.argv:
    _launch_count_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "launch_count.json")
    try:
        with open(_launch_count_file) as _f:
            _launch_data = _json.load(_f)
        _launch_count = _launch_data.get("count", 0)
    except (FileNotFoundError, ValueError):
        _launch_count = 0

    _launch_count += 1
    try:
        os.makedirs(os.path.dirname(_launch_count_file), exist_ok=True)
        with open(_launch_count_file, "w") as _f:
            _json.dump({"count": _launch_count}, _f)
    except Exception:
        pass

    if _launch_count <= 3:
        import run_script_util as _rsu

        _rsu.run_script("NLP_welcome_main.py")
        sys.exit(0)

# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief = False

GUI_width = GUI_IO_util.get_GUI_width(2)
GUI_height = 630  # height of GUI with full I/O display

GUI_size = str(GUI_width) + "x" + str(GUI_height)

# GUI_size='1150x670'
GUI_label = (
    "Graphical User Interface (GUI) for a suite of tools of Natural Language Processing (NLP) & Data Visualization"
)
# there is currently NO way to setup a specific I/O config for the NLP_menu_main; it can only have the default setup
# config_filename='NLP_config.csv'
# overwrite the standard way of setting up config_filename, since NLP_menu_main saves to default_config
config_filename = "NLP_default_IO_config.csv"
head, scriptName = os.path.split(os.path.basename(__file__))

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
config_input_output_numeric_options = [2, 1, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

# # GUI CHANGES add following lines to every special GUI
# # +2 is the number of lines starting at 1 of IO widgets
y_multiplier_integer = GUI_util.y_multiplier_integer + 0
window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

setup_IO_OK_checkbox_var = tk.IntVar()
setup_parsers_annotators_OK_checkbox_var = tk.IntVar()
setup_external_software_OK_checkbox_var = tk.IntVar()

script_to_run = ""
IO_values = ""

software = ""
missing_external_software = ""


def clear(e):

    software_setup_var.set("")
    clear_search()
    select_tool(None)
    GUI_util.clear("Escape")


window.bind("<Escape>", clear)


# IO fields do not need to be checked for scripts that open their own GUI
# TODO we should move this function to the GUI?
# IO_values 1 required file; 2 required dir; 3 either file or dir
def checkIO_Filename_InputDir(script, IO_values_local=0, fileExtension=""):
    if IO_values_local == 0:  # the case of a script with its own GUI; should never be here
        return True
    inputFilename = GUI_util.inputFilename.get()
    input_dir_path = GUI_util.input_main_dir_path.get()
    if IO_values_local == 1 or IO_values_local == 3:  # filename required
        # there MUST be a filename; check filename
        if IO_values_local == 1 and inputFilename == "":
            mb.showwarning(
                title="Fatal error",
                message="The script "
                + script
                + " requires a valid INPUT filename. The filename is currrently blank.\n\nPlease, select a valid INPUT filename and try again.",
            )
            return False
        if IO_values_local == 3 and inputFilename == "" and input_dir_path == "":
            mb.showwarning(
                title="Fatal error",
                message="The script "
                + script
                + " requires a valid INPUT filename and/or directory. Both filename and directory are currrently blank.\n\nPlease, select a valid INPUT filename or directory and try again.",
            )
        # RF return False
        # check file extension
        if inputFilename != "":
            fExtension = inputFilename.split(".")[-1]
            if fExtension not in fileExtension:
                mb.showwarning(
                    title="Fatal error",
                    message="The script "
                    + script
                    + " requires a valid INPUT file with extension "
                    + str(fileExtension)
                    + "."
                    + "\n\nPlease, select a valid INPUT file and try again.",
                )
                return False

    if IO_values_local == 2:  # input_dir required
        # there MUST be a directory; check directory
        if input_dir_path == "":
            mb.showwarning(
                title="Fatal error",
                message="The script "
                + script
                + " requires a valid INPUT directory. The directory is currrently blank.\n\nPlease, select a valid INPUT directory and try again.",
            )
            return False

    if IO_values_local == 3:  # either filename or input_dir required
        # already checked above
        if inputFilename == "" and input_dir_path == "":
            mb.showwarning(
                title="Fatal error",
                message="The script "
                + script
                + " requires a valid INPUT filename and/or directory. Both filename and directory are currrently blank.\n\nPlease, select a valid INPUT filename or directory and try again.",
            )
            return False

    return True


# if you want to get the value, just call val=pydict[input] where the input is the
# input from the table
# val[0] will be the py file you want and val[1] will be the availability with 1 to be available and 0 to be unexisting
# There are FIVE values in the dictionary:
# 1. the label displayed in any of the menus (the key to be used)
# 2. the name of the python script (to be passed to NLP.py) LEAVE BLANK IF OPTION NOT AVAILABLE
# 3. 0 False 1 True whether the script has a GUI that will check IO items or we need to check IO items here
# 4. 1, 2, 3 (to be chcked when the script has no GUI )
# 1 requires input Dir
# 2 requires input file
# 3 requires either Dir or file
# 5. file extension
# FOR CONVENIENCE, THE DIC ENTRIES ARE IN KEY ALPHABETICAL ORDER

# set all values to null when using a web-based program, as in:
# pydict["Gender guesser"] = ["Gender guesser", 0, 0,'']

# set 2 values to null when option is not available:
# pydict["Male & female names"] = ["", 0] not available

# all pydict values are grouped together in constants_util.py
pydict = {}
pydict[""] = ["", 0]  # not available
# https://stanfordnlp.github.io/CoreNLP/quote.html
pydict["Parsers & annotators (CoreNLP, spaCy, Stanza)"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - date (normalized NER date)"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - gender (male & female names; via CoreNLP and dictionaries)"] = [
    "html_annotator_gender_main.py",
    1,
]
pydict["CoreNLP annotator - quote"] = ["parsers_annotators_main.py", 1]
pydict["CoreNLP annotator - coreference (pronominal)"] = ["coreference_main.py", 1]
pydict["SVO (Subject-Verb-Object) extractor & visualization"] = ["SVO_main.py", 1]
pydict["Knowledge graphs: DBpedia, YAGO & Wikipedia"] = ["knowledge_graphs_main.py", 1]
pydict["HTML annotator - dictionary, gender, DBpedia, YAGO, WordNet - (All options GUI)"] = [
    "html_annotator_main.py",
    1,
]
pydict["HTML annotator extractor"] = ["html_annotator_main.py", 1]
pydict["Annotator - hedge/uncertainty"] = ["", 0]
pydict["CoNLL table analyzer - Search the CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["CoNLL table analyzer - Clause, noun, verb, function words frequencies"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Statistics (csv files)"] = ["statistics_csv_main.py", 1]
pydict["Statistics (txt files): Number of documents, words, syllables"] = [
    "statistics_txt_main.py",
    1,
]  # ["style_analysis_main.py", 1]
pydict["Statistics (txt files): Number of nouns, verbs, adjectives, pronouns, ..."] = [
    "statistics_txt_main.py",
    1,
]  # ["style_analysis_main.py", 1]
pydict["Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)"] = ["parsers_annotators_main.py", 1]
pydict["Co-Occurrences VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Co-Occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams search"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["N-grams/Co-Occurrences VIEWER"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Corpus checker (PC-ACE data)"] = ["corpus_checker_PCACE_data_main.py", 1]
pydict["Data manipulation (ALL options GUI)"] = ["data_manipulation_main.py", 1]
# The duplicate-detection tool is filed under 'Find the plagiarist' and 'Similarities between
# documents', so a user searching this menu for 'duplicate' -- the plain word for what it does --
# found nothing at all. Same synonym treatment the N-grams entries already get.
pydict["Duplicate documents (find near-duplicates via TF-IDF)"] = ["corpus_checker_PCACE_data_main.py", 1]
pydict["Duplicates (documents that copy one another)"] = ["corpus_checker_PCACE_data_main.py", 1]
pydict["File checker (A pre-processing pipeline of data quality control)"] = [
    "file_checker_pre_processing_pipeline_main.py",
    1,
]
pydict["File checker (file content)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file content utf-8 encoding)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File checker (file name)"] = ["file_manager_main.py", 1]
pydict["File cleaner (file content) (Change to ASCII non-ASCII apostrophes & quotes and % to percent)"] = [
    "file_checker_converter_cleaner_main.py",
    1,
]
pydict["File cleaner (file content) (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Remove blank lines from txt file(s))"] = [
    "file_checker_converter_cleaner_main.py",
    1,
]
pydict[
    "File cleaner (file content) (Add full stop . at the end of paragraphs without end-of-paragraph punctuation)"
] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File cleaner (file content) (Pronominal resolution via CoreNLP)"] = ["coreference_main.py", 1]
pydict["File classifier (dumb classifier via embedded date) (file name)"] = ["file_classifier_main.py", 1]
# the wording constants_util.NLP_Suite_data_file_handling_tools_menu lists it under
pydict["File classifier (file name) (dumb classifier via embedded date)"] = ["file_classifier_main.py", 1]
pydict["File finder (file name)"] = ["file_manager_main.py", 1]
pydict["File search (file content for words/collocations)"] = ["file_search_byWord_main.py", 1]
pydict["File search (file content for n-grams & co-occurrences)"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["File-type converter (csv, docx, pdf, rtf --> txt)"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["File matcher (file name)"] = ["file_matcher_main.py", 1]
pydict["File merger (file content)"] = ["file_merger_main.py", 1]
pydict["File splitter (file content)"] = ["file_splitter_main.py", 1]
pydict["File splitter (file name)"] = ["file_splitter_main.py", 1]
pydict["File manager (file name) (List, Rename, Copy, Move, Delete, Count, Split)"] = ["file_manager_main.py", 1]
pydict["Find non-related documents"] = ["corpus_checker_PCACE_data_main.py", 1]
pydict["Excel charts"] = ["charts_Excel_main.py", 1]
pydict["Animated time-dependent bar plot (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Boxplot"] = ["data_visualization_main.py", 1]
pydict["Colormap chart"] = ["data_visualization_main.py", 1]
pydict["Multiple bar charts"] = ["data_visualization_main.py", 1]
pydict["Network graphs (Gephi)"] = ["data_visualization_main.py", 1]
pydict["Sankey flowchart (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Sunburst pie chart (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Treemap (Plotly)"] = ["data_visualization_main.py", 1]
pydict["Geographic maps: From texts to maps via Google Earth Pro and Google Maps"] = ["GIS_main.py", 1]
pydict["Geographic maps: From csv file to maps via Google Earth Pro and Google Maps"] = ["GIS_Google_Earth_main.py", 1]
pydict["Geographic distances between locations"] = ["GIS_distance_main.py", 1]  # GIS_distance_main.py
pydict["Symbolic space: characters in NON-geocodable space (house, field, forest, threshold)"] = [
    "GIS_symbolic_main.py",
    1,
]
pydict["Language detection"] = ["style_analysis_main.py", 1]
pydict["NER (Named Entity Recognition) annotator"] = ["NER_main.py", 1]
pydict["Newspaper article/Document titles"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["N-grams & Co-occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Nominalization"] = ["nominalization_main.py", 1]
pydict["Sample corpus (ALL options GUI)"] = ["sample_corpus_main.py", 1]
pydict["File handler (ALL options GUI)"] = ["file_handler_ALL_main.py", 1]
pydict["Search (ALL options GUI)"] = ["file_search_ALL_main.py", 1]
pydict["Search CoNLL table"] = ["CoNLL_table_analyzer_main.py", 1]
pydict["Search text file(s) for n-grams & co-occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Search text file(s) for words/collocations"] = ["file_search_byWord_main.py", 1]
pydict["Sentence analysis (ALL options GUI)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence complexity"] = ["sentence_analysis_main.py", 1]
pydict["Sentence/text readability (via textstat)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dependency tree viewer (png graphs)"] = ["sentence_analysis_main.py", 1]
pydict["Sentence visualization: Dynamic sentence network viewer (Gephi graphs)"] = ["", 0]  # not available
pydict["Sentiment analysis"] = ["sentiment_analysis_main.py", 1]
pydict["Sentiment analysis (dictionary options: ANEW, hedonometer, SentiWordNet, VADER)"] = [
    "sentiment_analysis_main.py",
    1,
]
pydict["Sentiment analysis (neural network/tensor options: BERT, spaCy, Stanford CoreNLP, Stanza)"] = [
    "sentiment_analysis_main.py",
    1,
]
pydict["Sentiments/emotions (ALL options GUI)"] = ["sentiments_emotions_ALL_main.py", 1]
pydict["Shape of stories"] = ["shape_of_stories_main.py", 1]
pydict["Similarities between documents (via TF-IDF)"] = ["corpus_checker_PCACE_data_main.py", 1]
pydict["Similarities between documents (via Python difflib)"] = ["", 0]  # not available
pydict["Similarities between words (Levenshtein distance)"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checkers"] = ["file_spell_checker_main.py", 1]
pydict["Spelling checker cleaner (Find & Replace string)"] = ["file_checker_converter_cleaner_main.py", 1]
# pydict["Spelling checker/Unusual words (via NLTK)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via autocorrect)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via pyspellchecker)"] = ["file_spell_checker_main.py", 1]
# pydict["Spelling checker (via textblob)"] = ["file_spell_checker_main.py", 1]
pydict["PC-ACE database (via Pandas)"] = ["DB_PCACE_data_analysis_main.py", 1]
pydict["SQL database (via SQLite)"] = ["DB_SQL_main.py", 1]
pydict["Stanford CoreNLP"] = ["parsers_annotators_main.py", 1]
pydict["Semantic analysis"] = ["semantic_analysis_main.py", 1]
pydict["Syntactic analysis (ALL)"] = ["syntactic_analysis_ALL_main.py", 1]
pydict["Semantic analysis (ALL)"] = ["semantic_analysis_ALL_main.py", 1]
pydict["SRL Semantic Role Labeling"] = ["", 0]
pydict["Dictionary items by sentence index"] = ["sentence_analysis_util.dictionary_items_bySentenceID", 0, 3, "txt"]
pydict["Topic modeling (via MALLET & Gensim)"] = ["topic_modeling_main.py", 1]
pydict["utf-8 compliance"] = ["file_checker_converter_cleaner_main.py", 1]
pydict["Style analysis (ALL options GUI)"] = ["style_analysis_main.py", 1]
pydict["Narrative analysis (ALL options GUI)"] = ["narrative_analysis_ALL_main.py", 1]
pydict["CORPUS PROFILER. WHAT'S IN YOUR CORPUS? A SWEEPING VIEW."] = ["corpus_profiler_main.py", 1]
pydict["Corpus/document(s) statistics (Sentences, words, lines)"] = ["statistics_txt_main.py", 1]
pydict["Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)"] = ["statistics_txt_main.py", 1]
pydict["N-grams & Co-Occurrences"] = ["NGrams_CoOccurrences_main.py", 1]
pydict["Who wrote the text? Man or woman? (via Gender guesser)"] = ["Gender guesser", 0, 0, ""]
pydict["Wordclouds (ALL options GUI)"] = ["wordclouds_main.py", 1]
pydict["Semantic aggregation (WordNet, VerbNet, FrameNet)"] = ["semantic_aggregation_main.py", 1]
pydict["Word embeddings (Word2Vec) (via BERT & Gensim)"] = ["word2vec_main.py", 1]
# Word Sense Disambiguation, Word Sense Induction and Document embeddings are checkboxes of the Semantic analysis GUI
pydict["Document embeddings (Semantic similarity & clustering) (via SBERT)"] = ["semantic_analysis_main.py", 1]
pydict["Word Sense Disambiguation (WSD) via CoNLL"] = ["semantic_analysis_main.py", 1]
pydict["Word Sense Induction (WSI) via BERT"] = ["semantic_analysis_main.py", 1]
# pydict["Word embeddings (Word2Vec) (via spaCy)"] = ["", 0]
pydict["------------------"] = ["", 2]
# the following labels are found in constants_util
#   'Fundamental NLP tools ---------------------------------------------------------------------------'
#   'Specialized tools --------------------------------------------------------------------------------'
#   'Style analysis tools -----------------------------------------------------------------------------------'
# all pydict values are grouped together in constants_util.py

# NLP Suite team & How to cite are in GUI_util

software_setup_var = tk.StringVar()


def setup_IO():
    GUI_util.setup_IO_configuration_options(False, scriptName, silent=True, open_setup_IO_GUI=True)
    setup_IO_checkbox()


def setup_IO_checkbox():
    # RUN is always normal for NLP_mnenu_main so this test would fail
    # state = str(GUI_util.run_button['state'])
    # if state != 'disabled':

    config_input_output_alphabetic_options, missing_IO, config_file_exists = config_util.read_config_file(
        config_filename, config_input_output_numeric_options
    )

    if missing_IO == "":
        setup_IO_OK_checkbox_var.set(1)
    else:
        setup_IO_OK_checkbox_var.set(0)


NLP_package_language_config = GUI_IO_util.configPath + os.sep + "NLP_default_package_language_config.csv"


def setup_parsers_annotators_checkbox(NLP_package_language_config):
    if os.path.isfile(NLP_package_language_config):
        setup_parsers_annotators_OK_checkbox_var.set(1)
    else:
        setup_parsers_annotators_OK_checkbox_var.set(0)


setup_parsers_annotators_OK_checkbox_var.trace(
    "w", lambda x, y, z: setup_parsers_annotators_checkbox(NLP_package_language_config)
)

setup_parsers_annotators_checkbox(NLP_package_language_config)


def _setup_parsers_and_recheck():
    run_script_util.run_script("NLP_setup_package_language_main.py")
    setup_parsers_annotators_checkbox(NLP_package_language_config)


software_dir = ""


def setup_external_programs_checkbox():
    # If the config file doesn't exist, external software is not set up
    ext_config = GUI_IO_util.configPath + os.sep + "NLP_setup_external_software_config.csv"
    if not os.path.isfile(ext_config):
        setup_external_software_OK_checkbox_var.set(0)
        return ""
    # get the software_dir and software_url for the selected software_name from the config file
    software_dir, software_url, missing_software, error_found = IO_libraries_util.get_external_software_dir(
        "NLP_menu_main", "", silent=True, only_check_missing=True, install_download="download"
    )
    if missing_software != "":
        setup_external_software_OK_checkbox_var.set(0)
    else:
        setup_external_software_OK_checkbox_var.set(1)
    return missing_external_software


def callback(software: str):
    # print('IN CALLBACK')
    software_setup_var.set(software)
    setup_external_programs_checkbox()


def setup_external_software_warning():
    global software
    mb.showwarning(
        "External software option",
        "Please, select next the external software that you would like to download/install using the dropdown menu.",
    )
    software = GUI_IO_util.dropdown_menu_widget(
        window,
        "Please, select the external software to setup using the dropdown menu on the left, then click OK to accept your selection",
        ["Stanford CoreNLP", "Gephi", "Google Earth Pro", "MALLET", "WordNet"],
        "Stanford CoreNLP",
        callback,
    )
    if software != None:
        setup_external_programs_checkbox()


def setup_external_software():
    run_script_util.run_script("NLP_setup_external_software_main.py")
    setup_external_programs_checkbox()


def getScript(script):
    global script_to_run, IO_values
    script_to_run, IO_values = IO_files_util.getScript(pydict, script)


# ── Setup panel and tool browser ───────────────────────────────────────────────────────────────────────────
# The middle of the menu, between the shared header (GUI_top) and the RUN/CLOSE bar (GUI_bottom), is drawn
# with CustomTkinter: the setup steps on the left and, on the right, every tool in one list that can be
# browsed by category or searched by typing. It replaces the five SETUP rows and the two-tab notebook of
# seven dropdowns, where finding a tool meant guessing which dropdown held it.
# Every other GUI runs in its own process (run_script_util.run_script) and stays plain tkinter.

# CTk makes the whole process DPI-aware on Windows when it builds its first widget, which would rescale the
# plain-tk header and RUN bar around it. With that off, CTk draws at the same pixel scale as the tk widgets.
ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("light")

BRAND_RED = "#b10a0a"
BRAND_RED_HOVER = "#8f0808"
CARD_COLOR = "#ffffff"
CARD_BORDER = "#dcdcdc"
TEXT_COLOR = "#1f1f1f"
MUTED_TEXT = "#6e6e6e"
DISABLED_TEXT = "#a8a8a8"
ROW_HOVER = "#f4ecec"
ROW_SELECTED = "#f3d6d6"
READY_GREEN = "#2e7d32"


def _font(size=13, weight="normal"):
    return ctk.CTkFont(size=size, weight=weight)


def _outline_button(parent, text, command, width=72):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=28,
        font=_font(12),
        fg_color="transparent",
        border_width=1,
        border_color=BRAND_RED,
        text_color=BRAND_RED,
        hover_color=ROW_HOVER,
        corner_radius=8,
    )


# the rows the SETUP buttons and the notebook used to take; GUI_bottom places the RUN bar below them
panel_rows = 11
panel_y = GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step * y_multiplier_integer
y_multiplier_integer = y_multiplier_integer + panel_rows
panel_x = GUI_IO_util.help_button_x_coordinate
panel = ctk.CTkFrame(
    window,
    fg_color="transparent",
    corner_radius=0,
    width=GUI_width - 2 * panel_x,
    height=panel_rows * GUI_IO_util.y_step - 20,
)
panel.place(x=panel_x, y=panel_y)
panel.grid_propagate(False)
panel.grid_columnconfigure(1, weight=1)
panel.grid_rowconfigure(0, weight=1)

# --- Setup (left) ----------------------------------------------------------------------------------------------
IO_setup_help = (
    "Please, click on the Set up button to open the GUI that will allow you to setup default I/O options:\n   INPUT file and/or directory of files (your corpus) and\n   OUTPUT directory where all files (csv, txt, html, kml, jpg) produced by the NLP-Suite tools will be saved.\n\nThese default I/O options will be used for all GUIs.\n\nThe status reads Ready if all INPUT/OUTPUT options have been successfully selected and saved in the NLP_default_IO_config.csv file under the subdirectory config.\n\nYou can open the NLP_default_IO_config.csv file by clicking on the csv button."
    + GUI_IO_util.msg_IO_config
)
package_language_setup_help = "Please, click on the Set up button to open the GUI that will allow you to setup default NLP package to be used for parsers and annotators (spaCy, Stanford CoreNLP, Stanza) and the language of your corpus.\n\nThe status reads Ready if the NLP package and corpus language options have been saved in the NLP_default_package_language_config.csv file under the subdirectory config.\n\nYou can open the NLP_default_package_language_config.csv file by clicking on the csv button."
external_software_setup_help = (
    "The NLP-Suite relies for some of its operations on external software that needs to be downloaded and installed (Stanford CoreNLP, WordNet, MALLET, Java (JDK), Gephi, Google Earth Pro). When using any of these software, the NLP-Suite needs to know where they have been installed on your computer (e.g., C:\\Program Files (x86)\\WordNet).\n\nPlease, click on the Set up button to select the software option that you want to link to its installation directory. YOUR SELECTION WILL BE SAVED IN THE NLP_setup_external_software_config.csv FILE UNDER THE SUBDIRECTORY config.\n\nThe status reads Ready if all external software packages have been successfully installed.\n\nYou can open the NLP_setup_external_software_config.csv file by clicking on the csv button.\n\n"
    "The NLP_setup_external_software_config.csv file has three columns (with headers Software, Path, Download_link) and 6 rows, one for each of the external software and with the following expected labels: Stanford CoreNLP, MALLET, Java (JDK), WordNet, Gephi, Google Earth Pro and where "
    "Path refers to the installation path of the software on your machine. "
    "As an example, the three fields for the Stanford CoreNLP software would look like this: "
    "Stanford CoreNLP   C:/Program Files (x86)/stanford-corenlp-4.3.1   https://stanfordnlp.github.io/CoreNLP/download.html. "
    "Needless to say C:/Program Files (x86)/stanford-corenlp-4.3.1 will change, depending upon where you install CoreNLP locally."
)

# the card is as tall as its content, so the start buttons sit right under the setup rows, not at the
# bottom of a half-empty card
panel.grid_columnconfigure(0, minsize=380)
setup_card = ctk.CTkFrame(panel, fg_color=CARD_COLOR, border_color=CARD_BORDER, border_width=1, corner_radius=12)
setup_card.grid(row=0, column=0, sticky="new", padx=(0, 14))
setup_card.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(setup_card, text="Setup", font=_font(17, "bold"), text_color=TEXT_COLOR).grid(
    row=0, column=0, columnspan=5, sticky="w", padx=18, pady=(14, 4)
)


def _show_setup_status(var, dot, status):
    if var.get() == 1:
        dot.configure(text_color=READY_GREEN)
        status.configure(text="Ready", text_color=MUTED_TEXT)
    else:
        dot.configure(text_color=BRAND_RED)
        status.configure(text="Needs setup", text_color=BRAND_RED)


def _setup_row(row, title, *, status_var, setup_command, config_file, help_message):
    dot = ctk.CTkLabel(setup_card, text="●", font=_font(14), width=14)
    dot.grid(row=row, column=0, sticky="n", padx=(18, 8), pady=(8, 0))
    text = ctk.CTkFrame(setup_card, fg_color="transparent")
    text.grid(row=row, column=1, sticky="w", pady=6)
    ctk.CTkLabel(text, text=title, font=_font(13, "bold"), text_color=TEXT_COLOR, height=18).pack(anchor="w")
    status = ctk.CTkLabel(text, text="", font=_font(12), height=16)
    status.pack(anchor="w")
    _outline_button(setup_card, "Set up", setup_command, width=64).grid(row=row, column=2, padx=(4, 4))
    ctk.CTkButton(
        setup_card,
        text="csv",
        width=38,
        height=28,
        font=_font(11),
        corner_radius=8,
        fg_color="transparent",
        hover_color=ROW_HOVER,
        text_color=MUTED_TEXT,
        command=lambda: IO_files_util.openFile(window, config_file),
    ).grid(row=row, column=3)
    ctk.CTkButton(
        setup_card,
        text="?",
        width=28,
        height=28,
        font=_font(12, "bold"),
        corner_radius=14,
        fg_color="transparent",
        hover_color=ROW_HOVER,
        text_color=MUTED_TEXT,
        command=lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", help_message),
    ).grid(row=row, column=4, padx=(0, 12))
    status_var.trace_add("write", lambda *args: _show_setup_status(status_var, dot, status))
    _show_setup_status(status_var, dot, status)


_setup_row(
    2,
    "Input & output",
    status_var=setup_IO_OK_checkbox_var,
    setup_command=setup_IO,
    config_file=GUI_IO_util.configPath + os.sep + "NLP_default_IO_config.csv",
    help_message=IO_setup_help,
)
_setup_row(
    3,
    "Parser & language",
    status_var=setup_parsers_annotators_OK_checkbox_var,
    setup_command=_setup_parsers_and_recheck,
    config_file=NLP_package_language_config,
    help_message=package_language_setup_help,
)
_setup_row(
    4,
    "External software",
    status_var=setup_external_software_OK_checkbox_var,
    setup_command=setup_external_software,
    config_file=GUI_IO_util.configPath + os.sep + "NLP_setup_external_software_config.csv",
    help_message=external_software_setup_help,
)

# CORPUS PROFILER -- the flagship one-click tool keeps a button of its own, apart from the tool list
ctk.CTkFrame(setup_card, height=1, fg_color=CARD_BORDER).grid(
    row=5, column=0, columnspan=5, sticky="ew", padx=18, pady=(10, 0)
)
ctk.CTkLabel(setup_card, text="Start here", font=_font(13, "bold"), text_color=TEXT_COLOR).grid(
    row=6, column=0, columnspan=5, sticky="w", padx=18, pady=(8, 4)
)
start_frame = ctk.CTkFrame(setup_card, fg_color="transparent")
start_frame.grid(row=7, column=0, columnspan=5, sticky="ew", padx=18, pady=(0, 16))
ctk.CTkButton(
    start_frame,
    text="Corpus profiler: what's in your corpus?",
    height=38,
    font=_font(13, "bold"),
    fg_color=BRAND_RED,
    hover_color=BRAND_RED_HOVER,
    corner_radius=10,
    command=lambda: run_script_util.run_script("corpus_profiler_main.py"),
).pack(fill="x", pady=(0, 8))
# CORPUS LANGUAGE & NLP options available in the Suite
_outline_button(
    start_frame,
    "Which tools work with my corpus language?",
    lambda: language_tools_advisor_util.run(outputDir=GUI_util.output_dir_path.get()),
).pack(fill="x")

# --- Tool browser (right) -----------------------------------------------------------------------------------
# (category, description, the dropdown list it was built from); the lists keep their '' spacers and
# '--- header ---' lines, which NLP_menu_tools_util turns into sections
tool_categories = [
    (
        "Corpus",
        "Tools that apply to multiple documents only: a directory of files (the corpus).",
        constants_util.NLP_Suite_corpus_tools_menu,
    ),
    (
        "Corpus / document",
        "Tools that apply to either a corpus or a single document.",
        constants_util.NLP_Suite_corpus_document_tools_menu,
    ),
    (
        "Sentence",
        "Tools that work on a corpus or a document and report results by sentence index.",
        ["Sentence analysis (ALL options GUI)"],
    ),
    (
        "Data & files",
        "Handle data and files: check, convert, find, match, rename; query databases.",
        constants_util.NLP_Suite_data_file_handling_tools_menu,
    ),
    (
        "Pre-processing",
        "Check and clean your documents before analyzing them.",
        constants_util.NLP_Suite_pre_processing_tools_menu,
    ),
    (
        "Statistics",
        "Summary statistics for csv and txt files.",
        [
            "Statistics (csv files)",
            "Corpus/document(s) statistics (Sentences, words, lines)",
            "Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)",
            "N-grams & Co-occurrences",
        ],
    ),
    (
        "Visualization",
        "Charts, maps and networks. Most linguistic tools also chart their own results.",
        constants_util.NLP_Suite_visualization_tools_menu,
    ),
]
category_groups = [
    ("LINGUISTIC ANALYSIS", ["Corpus", "Corpus / document", "Sentence"]),
    ("GENERAL UTILITY", ["Data & files", "Pre-processing", "Statistics", "Visualization"]),
]
category_descriptions = {name: description for name, description, items in tool_categories}
tool_catalog = NLP_menu_tools_util.build_catalog(
    [(name, items) for name, description, items in tool_categories], pydict
)

tools_card = ctk.CTkFrame(panel, fg_color=CARD_COLOR, border_color=CARD_BORDER, border_width=1, corner_radius=12)
tools_card.grid(row=0, column=1, sticky="nsew")
tools_card.grid_columnconfigure(1, weight=1)
tools_card.grid_rowconfigure(2, weight=1)

# no textvariable: CTkEntry shows no placeholder text when it has one
search_entry = ctk.CTkEntry(
    tools_card,
    height=36,
    font=_font(14),
    corner_radius=10,
    border_color=CARD_BORDER,
    border_width=1,
    fg_color="#f7f7f7",
    text_color=TEXT_COLOR,
    placeholder_text="Search all tools  (e.g., topic, sentiment, word sense)",
)
search_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(14, 8))

# category list
category_frame = ctk.CTkFrame(tools_card, fg_color="transparent", width=190)
category_frame.grid(row=1, column=0, rowspan=3, sticky="nsw", padx=(10, 6), pady=(0, 12))
category_buttons = {}
for group, names in category_groups:
    ctk.CTkLabel(category_frame, text=group, font=_font(11, "bold"), text_color=MUTED_TEXT, height=22).pack(
        anchor="w", padx=8, pady=(6, 0)
    )
    for name in names:
        category_buttons[name] = ctk.CTkButton(
            category_frame,
            text=name,
            anchor="w",
            width=180,
            height=30,
            font=_font(13),
            corner_radius=8,
            fg_color="transparent",
            hover_color=ROW_HOVER,
            text_color=TEXT_COLOR,
            command=lambda n=name: show_category(n),
        )
        category_buttons[name].pack(anchor="w")

# shown only while searching: how many tools match
list_title = ctk.CTkLabel(tools_card, text="", font=_font(12), text_color=MUTED_TEXT, anchor="w", height=20)
tool_list = ctk.CTkScrollableFrame(tools_card, fg_color="transparent", corner_radius=0)
tool_list.grid(row=2, column=1, sticky="nsew", padx=(0, 6))
tool_list.grid_columnconfigure(0, weight=1)

# one button per tool, built once and re-gridded as the category or the search changes
tool_buttons = {}
for entry in tool_catalog:
    label = entry["label"]
    if label in tool_buttons:
        continue
    button = ctk.CTkButton(
        tool_list,
        text=entry["name"],
        anchor="w",
        height=28,
        font=_font(13),
        corner_radius=6,
        fg_color="transparent",
        hover_color=ROW_HOVER,
        text_color=TEXT_COLOR,
        command=lambda tool=label: select_tool(tool),
    )
    if not entry["available"]:
        button.configure(
            text=entry["name"] + "   (not available yet)", state="disabled", text_color_disabled=DISABLED_TEXT
        )
    else:
        button.bind("<Double-Button-1>", lambda e, tool=label: open_tool(tool))
    tool_buttons[label] = button
section_labels = {}
no_match_label = ctk.CTkLabel(tool_list, text="", font=_font(13), text_color=MUTED_TEXT)

# selected tool and Open button
detail_frame = ctk.CTkFrame(tools_card, fg_color="#f7f7f7", corner_radius=10)
detail_frame.grid(row=3, column=1, sticky="ew", padx=(6, 14), pady=(6, 12))
detail_frame.grid_columnconfigure(0, weight=1)
detail_name = ctk.CTkLabel(detail_frame, text="", font=_font(13, "bold"), text_color=TEXT_COLOR, anchor="w", height=20)
detail_name.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
detail_info = ctk.CTkLabel(detail_frame, text="", font=_font(12), text_color=MUTED_TEXT, anchor="w", height=18)
detail_info.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
open_button = ctk.CTkButton(
    detail_frame,
    text="Open",
    width=96,
    height=34,
    font=_font(13, "bold"),
    corner_radius=10,
    fg_color=BRAND_RED,
    hover_color=BRAND_RED_HOVER,
    command=lambda: run(),
)
open_button.grid(row=0, column=1, rowspan=2, padx=10)

current_category = "Corpus / document"
selected_tool = None
shown_entries = []
shown_widgets = []


def _entry_of(label):
    # the entry as listed now (a tool can sit in several categories), else its first listing
    for entry in shown_entries + tool_catalog:
        if entry["label"] == label:
            return entry
    raise KeyError(label)


def _enable_open(enabled):
    # a disabled CTkButton keeps its red; grey it so it does not look clickable
    open_button.configure(state="normal" if enabled else "disabled", fg_color=BRAND_RED if enabled else CARD_BORDER)


def select_tool(label):
    global selected_tool, script_to_run, IO_values
    if selected_tool in tool_buttons:
        tool_buttons[selected_tool].configure(fg_color="transparent", text_color=TEXT_COLOR)
    selected_tool = label
    if label is None:
        # nothing picked yet: when browsing, say what the category holds
        script_to_run, IO_values = "", ""
        if search_entry.get().strip() == "":
            detail_name.configure(text=current_category)
            detail_info.configure(text=category_descriptions.get(current_category, ""))
        else:
            detail_name.configure(text="No tool selected")
            detail_info.configure(text="")
        _enable_open(False)
        return
    tool_buttons[label].configure(fg_color=ROW_SELECTED, text_color=BRAND_RED)
    getScript(label)
    entry = _entry_of(label)
    detail_name.configure(text=entry["name"])
    detail_info.configure(text=entry["description"] or entry["category"])
    _enable_open(script_to_run != "")
    open_button.configure(text="Open" if str(script_to_run).endswith(".py") else "Run")


def open_tool(label):
    select_tool(label)
    if script_to_run != "":
        run()


def _scroll_into_view(widget):
    # the arrow keys move the selection; keep it on screen
    canvas = tool_list._parent_canvas
    tool_list.update_idletasks()
    total = tool_list.winfo_height()
    if total <= 0:
        return
    top, visible = widget.winfo_y(), canvas.winfo_height()
    first = canvas.yview()[0] * total
    if top < first:
        canvas.yview_moveto(top / total)
    elif top + widget.winfo_height() > first + visible:
        canvas.yview_moveto((top + widget.winfo_height() - visible) / total)


def _show_entries(entries, with_sections, empty_message=""):
    global shown_entries
    for widget in shown_widgets:
        if isinstance(widget, ctk.CTkButton):
            # a row that moves away from under the pointer never gets its <Leave>, and kept its hover color
            widget._on_leave()
        widget.grid_forget()
    shown_widgets.clear()
    shown_entries = entries
    row = 0
    section = ""
    for entry in entries:
        if with_sections and entry["section"] and entry["section"] != section:
            section = entry["section"]
            if section not in section_labels:
                section_labels[section] = ctk.CTkLabel(
                    tool_list,
                    text=section.upper(),
                    font=_font(11, "bold"),
                    text_color=MUTED_TEXT,
                    anchor="w",
                    height=22,
                )
            section_labels[section].grid(row=row, column=0, sticky="ew", padx=10, pady=(8 if row else 0, 0))
            shown_widgets.append(section_labels[section])
            row += 1
        tool_buttons[entry["label"]].grid(row=row, column=0, sticky="ew", padx=(0, 4))
        shown_widgets.append(tool_buttons[entry["label"]])
        row += 1
    if not entries:
        no_match_label.configure(text=empty_message)
        no_match_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        shown_widgets.append(no_match_label)
    tool_list._parent_canvas.yview_moveto(0)


def show_category(name):
    global current_category
    current_category = name
    if search_entry.get() != "":
        clear_search()
        return
    for category, button in category_buttons.items():
        if category == name:
            button.configure(fg_color=ROW_SELECTED, text_color=BRAND_RED, font=_font(13, "bold"))
        else:
            button.configure(fg_color="transparent", text_color=TEXT_COLOR, font=_font(13))
    list_title.grid_remove()
    _show_entries(NLP_menu_tools_util.entries_in_category(tool_catalog, name), True)
    if selected_tool is None or selected_tool not in [entry["label"] for entry in shown_entries]:
        select_tool(None)


def show_search_results():
    query = search_entry.get().strip()
    if query == "":
        show_category(current_category)
        return
    for button in category_buttons.values():
        button.configure(fg_color="transparent", text_color=TEXT_COLOR, font=_font(13))
    results = NLP_menu_tools_util.search(tool_catalog, query, pydict)
    count = str(len(results)) + (" tool matches" if len(results) == 1 else " tools match")
    list_title.configure(text=count + ' "' + query + '"   (Esc to clear)')
    if results:
        list_title.grid(row=1, column=1, sticky="ew", padx=(6, 14))
    else:
        list_title.grid_remove()
    _show_entries(results, False, 'No tool matches "' + query + '". Try another word, or browse the categories.')
    # the best match is picked, so Return (or Open, or RUN) opens it straight away
    available = [entry["label"] for entry in results if entry["available"]]
    select_tool(available[0] if available else None)


_search_after_id = None
_last_query = ""


def _search_soon(*args):
    # wait for a pause in typing, so the list is not rebuilt on every keystroke; arrow keys and Return
    # also end in a KeyRelease, and leave the query (and the list) as it is
    global _search_after_id, _last_query
    if search_entry.get() == _last_query:
        return
    _last_query = search_entry.get()
    if _search_after_id is not None:
        window.after_cancel(_search_after_id)
    _search_after_id = window.after(150, _run_pending_search)


search_entry.bind("<KeyRelease>", _search_soon)
# a paste or cut with the mouse changes the text without a key
search_entry.bind("<<Paste>>", lambda e: window.after_idle(_search_soon))
search_entry.bind("<<Cut>>", lambda e: window.after_idle(_search_soon))


def _run_pending_search():
    global _search_after_id
    _search_after_id = None
    show_search_results()


def _flush_search():
    # the arrow keys and Return act on the list for what is typed now, not on the list from before
    # the last keystroke still waiting out its pause
    _search_soon()
    if _search_after_id is not None:
        window.after_cancel(_search_after_id)
        _run_pending_search()


def clear_search():
    global _last_query, _search_after_id
    if _search_after_id is not None:
        window.after_cancel(_search_after_id)
        _search_after_id = None
    search_entry.delete(0, "end")
    _last_query = ""
    show_category(current_category)


def _move_selection(step):
    _flush_search()
    available = [entry["label"] for entry in shown_entries if entry["available"]]
    if not available:
        return "break"
    if selected_tool in available:
        position = min(max(available.index(selected_tool) + step, 0), len(available) - 1)
    else:
        position = 0
    select_tool(available[position])
    _scroll_into_view(tool_buttons[available[position]])
    return "break"


def _search_return(event):
    _flush_search()
    available = [entry["label"] for entry in shown_entries if entry["available"]]
    if selected_tool in available:
        open_tool(selected_tool)
    elif available:
        open_tool(available[0])
    return "break"


search_entry.bind("<Down>", lambda e: _move_selection(1))
search_entry.bind("<Up>", lambda e: _move_selection(-1))
search_entry.bind("<Return>", _search_return)

show_category(current_category)
select_tool(None)


def openYouTube(video_url):
    if video_url != "":
        webbrowser.open_new_tab(video_url)
    else:
        mb.showwarning(
            title="Warning",
            message="The YouTube video "
            + video_url
            + " could not be found in the NLP Suite YouTube channel.\n\nPlease, warn the NLP Suite developers.",
        )


videos_lookup = {"Setup the NLP Suite": "https://www.youtube.com/watch?v=W56SU9oAbpc"}
videos_options = "Setup the NLP Suite"

TIPS_lookup = {
    "NLP Suite: Package description": "TIPS_NLP_NLP Suite Package description.pdf",
    "pip install & Anaconda environments": "TIPS_NLP_Anaconda NLP environment pip.pdf",
    "Things to do with words: NLP approach": "TIPS_NLP_Things to do with words NLP approach.pdf",
    "Setup Input/Output configuration for your corpus": "TIPS_NLP_Setup INPUT-OUTPUT options.pdf",
    "Setup external software (e.g., MALLET)": "TIPS_NLP_Setup external software.pdf",
    "NLP Suite: General tools": "TIPS_NLP_NLP Suite General tools.pdf",
    "NLP Suite: Tools of linguistic analysis": "TIPS_NLP_NLP Suite Tools of linguistic analysis.pdf",
    "NLP basic language": "TIPS_NLP_NLP Basic language.pdf",
    "English Language Benchmarks": "TIPS_NLP_English Language Benchmarks.pdf",
    "Things to do with words: Overall view": "TIPS_NLP_Things to do with words Overall view.pdf",
    "Things to do with words: Content analysis": "TIPS_NLP_Things to do with words Content analysis.pdf",
    "Things to do with words: Frame analysis": "TIPS_NLP_Things to do with words Frame analysis.pdf",
    "Things to do with words: Narrative analysis": "TIPS_NLP_Things to do with words Narrative analysis.pdf",
    "Things to do with words: Rhetoric (Arguments)": "TIPS_NLP_Things to do with words Rhetorical analysis Arguments.pdf",
    "Things to do with words: Rhetoric (Tropes & Figures)": "TIPS_NLP_Things to do with words Rhetorical analysis Tropes and Figures.pdf",
    "Style analysis": "TIPS_NLP_Style analysis.pdf",
    "Text encoding (utf-8)": "TIPS_NLP_Text encoding (utf-8).pdf",
    "Excel - Enabling Macros": "TIPS_NLP_Excel Enabling macros.pdf",
    "csv files - Problems & solutions": "TIPS_NLP_csv files - Problems & solutions.pdf",
    "Statistical measures": "TIPS_NLP_Statistical measures.pdf",
    "Python: download, install, run": "TIPS_NLP_Python download install run.pdf",
    "Anaconda & pip useful commands": "TIPS_NLP_Anaconda & pip useful commands.pdf",
    "NLP software options": "TIPS_NLP_NLP software options.pdf",
    "Acknowledgments: external programs": "TIPS_NLP_Acknowledgments External Programs.pdf",
    "Web scraping (background reading)": "TIPS_NLP_Web scraping.pdf",
}
TIPS_options = (
    "NLP Suite: Package description",
    "pip install & Anaconda environments",
    "Text encoding (utf-8)",
    "Excel - Enabling Macros",
    "csv files - Problems & solutions",
    "Statistical measures",
    "Setup Input/Output configuration for your corpus",
    "Setup external software (e.g., MALLET)",
    "Things to do with words: NLP approach",
    "English Language Benchmarks",
    "NLP Suite: General tools",
    "NLP Suite: Tools of linguistic analysis",
    "NLP basic language",
    "Things to do with words: Overall view",
    "Things to do with words: Content analysis",
    "Things to do with words: Frame analysis",
    "Things to do with words: Narrative analysis",
    "Things to do with words: Rhetoric (Arguments)",
    "Things to do with words: Rhetoric (Tropes & Figures)",
    "Style analysis",
    "Python: download, install, run",
    "Anaconda & pip useful commands",
    "NLP software options",
    "Acknowledgments: external programs",
    "Web scraping (background reading)",
)


# reminders content for specific GUIs are set in the csv file reminders

# 'KWIC',
# 'KWIC':'TIPS_NLP_KWIC (Key Words In Context).pdf'


# change the value of the readMe_message
readMe_message = "This Python 3 script is the front end for a wide collection of Java and Python Natural Language Processing (NLP) tools.\n\nThe set of tools are divided into GENERAL UTILITY TOOLS (data and file handling, pre-processing, statistical, visualization) and LINGUISTIC ANALYSIS TOOLS.\n\nLINGUISTIC ANALYSIS TOOLS are divided into tools that expect in input CORPUS DATA (i.e., multiple documents stored in a directory), CORPUS and/or SINGLE DOCUMENT, and SENTENCE.\n\nWhile some linguistic tools are specific for one of these three categories (e.g., topic modeling cannot be performed on a single document), MANY TOOLS OVERLAP. Tools that can work on a single file or a corpus are all classified under CORPUS/DOCUMENT tools. SENTENCE TOOLS still require either a corpus or a single document in input; but they also provide in output sentence-level information for more ingrained linguistic analyses.\n\nAll tools are open source freeware software released under the GNU LGPLv2.1 license (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html).\n\nYou can cite the NLP Suite as:\n\nFranzosi, Roberto. 2020. NLP Suite: A collection of natural language processing and visualization tools GitHub: https://github.com/NLP-Suite/NLP-Suite/wiki."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(
    config_filename,
    config_input_output_numeric_options,
    y_multiplier_integer,
    readMe_command,
    videos_lookup,
    videos_options,
    TIPS_lookup,
    TIPS_options,
    IO_setup_display_brief,
    scriptName,
)

if platform == "darwin":
    window.update()

# temp_config_filename = config_filename # 'NLP_menu_config.csv'
routine_options = reminders_util.getReminders_list(scriptName)

reminders_util.checkReminder(
    scriptName, reminders_util.title_options_NLP_Suite_architecture, reminders_util.message_NLP_Suite_architecture, True
)
routine_options = reminders_util.getReminders_list(scriptName)

if sys.platform == "darwin":
    reminders_util.checkReminder(
        scriptName, reminders_util.title_options_TensorFlow, reminders_util.message_TensorFlow, True
    )
    routine_options = reminders_util.getReminders_list(scriptName)


# Auto-generate default config files on first run so the user can test immediately
def ensure_default_configs():
    import csv as _csv

    config_dir = GUI_IO_util.configPath
    if not os.path.isdir(config_dir):
        try:
            os.mkdir(config_dir)
        except Exception:
            return False

    created = []

    io_config = os.path.join(config_dir, "NLP_default_IO_config.csv")
    if not os.path.isfile(io_config):
        sample_dir = os.path.join(GUI_IO_util.NLPPath, "lib", "sampleData", "newspaperArticles")
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "NLP_output")
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception:
                output_dir = ""
        sample_dir_path = sample_dir.replace("\\", "/")
        output_dir_path = output_dir.replace("\\", "/")
        with open(io_config, "w", newline="", encoding="utf-8") as f:
            w = _csv.writer(f)
            w.writerow(
                [
                    "I/O configuration label",
                    "Path",
                    "Sort order",
                    "Item separator character(s)",
                    "Date format",
                    "Date position",
                ]
            )
            w.writerow(["Input txt filename with path", "", "", "", "", ""])
            w.writerow(["Input files directory", sample_dir_path, "0", "_", "mm-dd-yyyy", "4"])
            w.writerow(["Input files secondary directory", "", "", "", "", ""])
            w.writerow(["Output files directory", output_dir_path, "", "", "", ""])
        created.append("I/O configuration (input: lib/sampleData/newspaperArticles, output: ~/Documents/NLP_output)")

    pkg_config = os.path.join(config_dir, "NLP_default_package_language_config.csv")
    if not os.path.isfile(pkg_config):
        with open(pkg_config, "w", newline="", encoding="utf-8") as f:
            w = _csv.writer(f)
            w.writerow(
                [
                    "Parser & annotators",
                    "Parsers",
                    "Basic functions (tokenizer/lemmatizer)",
                    "Corpus language",
                    "Language encoding",
                    "Export Json",
                    "CoreNLP memory",
                    "CoreNLP document length",
                    "CoreNLP sentence-length limit",
                ]
            )
            w.writerow(
                [
                    "Stanza",
                    "Dependency parser, Constituency parser",
                    "Stanza",
                    "English",
                    "utf-8",
                    "0.0",
                    "0.0",
                    "0.0",
                    "0.0",
                ]
            )
        created.append("NLP package & language (Stanza, English)")

    if created:
        msg = (
            "The NLP Suite has automatically created default configuration files "
            "so you can start testing right away:\n\n"
        )
        for item in created:
            msg += "  • " + item + "\n"
        msg += "\nYou can change these options at any time using the SETUP buttons above."
        mb.showinfo("Default configuration created", msg)
        return True
    return False


configs_created = ensure_default_configs()

# check for missing I/O configuration options
setup_IO_checkbox()
setup_parsers_annotators_checkbox(NLP_package_language_config)

# check for missing external software
missing_external_software = setup_external_programs_checkbox()

if missing_external_software != "":
    reminders_util.checkReminder(
        scriptName,
        reminders_util.title_options_missing_external_software_NLP_main_GUI,
        reminders_util.message_missing_external_software_NLP_main_GUI,
        True,
    )
    routine_options = reminders_util.getReminders_list(scriptName)

if (
    not setup_IO_OK_checkbox_var.get()
    or not setup_parsers_annotators_OK_checkbox_var.get()
    or not setup_external_software_OK_checkbox_var.get()
):
    answer = tk.messagebox.askyesno(
        "Warning",
        "Some (or all) of the required three setup options:\n"
        "\n\nSetup default I/O options...\nSetup default NLP parsers and annotators...\nSetup external software"
        "\n\ndisplayed in the three buttons at the top of this GUI are not completed (the checkbox to the left of the incomplete setup button is not ticked off)."
        "\n\nYou should click on the appropriate Setup button and complete the required setup."
        "\n\nDo you want to watch the video on how to setup the NLP Suite options?",
    )
    if answer:
        GUI_util.videos_dropdown_field.set("Setup the NLP Suite")
        # GUI_util.watch_video(videos_lookup, scriptName)

if sys.platform == "darwin":
    import platform

    if platform.machine() != "x86_64":
        # When running as a PyInstaller frozen app, sys.executable is the bundle
        # binary, not a Python interpreter, so pip cannot be invoked. The bundled
        # python-env already includes TensorFlow with Apple Silicon support, so
        # no check is needed. Only warn when running from source (development mode).
        if not getattr(sys, "frozen", False):
            import subprocess

            try:
                output = subprocess.check_output(
                    [sys.executable, "-m", "pip", "freeze"], stderr=subprocess.DEVNULL
                ).decode("utf-8")
            except Exception:
                output = ""
            has_tensorflow = any(
                pkg in output for pkg in ("tensorflow-metal", "tensorflow-macos", "tensorflow==", "tensorflow ")
            )
            if not has_tensorflow:
                mb.showwarning(
                    title="Warning",
                    message="Your Mac uses an Apple Silicon chip (M1/M2/M3).\n\n"
                    "Some algorithms that rely on TensorFlow (e.g. BERT) may not work correctly "
                    "without a TensorFlow build that supports Apple Silicon.\n\n"
                    "If you plan to use those algorithms, install TensorFlow for Apple Silicon:\n\n"
                    "    pip install tensorflow tensorflow-metal\n\n"
                    "You do NOT need to reinstall Anaconda — the bundled python-env already "
                    "supports Apple Silicon.",
                )

GUI_util.window.mainloop()
