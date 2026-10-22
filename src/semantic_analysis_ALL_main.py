# Semantic analysis (ALL): one GUI that gathers the NLP Suite's existing semantic GUIs, as syntactic_analysis_ALL_main
#   does for the syntactic ones. It runs no analysis of its own: each button opens another GUI.

import sys

import GUI_util
import IO_libraries_util

# returns None when everything is installed, so test for False itself
if (
    IO_libraries_util.install_all_Python_packages(GUI_util.window, "semantic_analysis_ALL_main.py", ["os", "tkinter"])
    is False
):
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import run_script_util

# the GUIs gathered here: button label -> script it opens
SEMANTIC_GUIS = {
    "Semantic analysis: WSI, WSD, SRL (Open GUI)": "semantic_analysis_main.py",
    "Word embeddings: Gensim Word2Vec, BERT (Open GUI)": "word2vec_main.py",
    # a checkbox of the Semantic analysis GUI, given its own button so students find it (Roberto, 21 Oct 2026)
    "DOCUMENT embeddings (via SBERT) (Open GUI)": "semantic_analysis_main.py",
    "WordNet, VerbNet, FrameNet (Open GUI)": "semantic_aggregation_main.py",
    "Semantic Role Labeling (SRL) (Open GUI)": "SRL_main.py",
    "Topic modeling: MALLET & Gensim (Open GUI)": "topic_modeling_main.py",
    "Knowledge graphs: DBpedia & YAGO (Open GUI)": "knowledge_graphs_main.py",
}

# RUN section ______________________________________________________________________________________________________________________________________________________


def run():
    # every option of this GUI opens another GUI from its own button; there is nothing to RUN here
    mb.showwarning(
        title="Warning",
        message="This GUI does not run any analysis of its own.\n\nPlease, click on one of the (Open GUI) buttons to open the GUI of the semantic analysis you wish to perform, then click RUN there.",
    )


# the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief = True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(
    IO_setup_display_brief,
    GUI_width=GUI_IO_util.get_GUI_width(3),
    GUI_height_brief=520,  # height at brief display
    GUI_height_full=600,  # height at full display
    y_multiplier_integer=GUI_util.y_multiplier_integer,
    y_multiplier_integer_add=1,  # to be added for full display
    increment=1,
)  # to be added for full display

GUI_label = "Graphical User Interface (GUI) for Semantic Analysis (ALL)"
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
config_input_output_numeric_options = [6, 1, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)


def clear(e):
    GUI_util.clear("Escape")


window.bind("<Escape>", clear)

# one button per GUI, placed as in syntactic_analysis_ALL_main
for button_label, script in SEMANTIC_GUIS.items():
    button = tk.Button(
        window, width=50, text=button_label, command=lambda script=script: run_script_util.run_script(script)
    )
    y_multiplier_integer = GUI_IO_util.placeWidget(
        window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer, button, False
    )

videos_lookup = {"No videos available": ""}
videos_options = "No videos available"

TIPS_lookup = {
    "Word Sense Induction (WSI)": "TIPS_NLP_Word Sense Induction (WSI).pdf",
    "Word Sense Disambiguation (WSD)": "TIPS_NLP_Word Sense Disambiguation (WSD).pdf",
    "Semantic similarity (document embeddings)": "TIPS_NLP_Semantic similarity (document embeddings).pdf",
    "Word2Vec": "TIPS_NLP_Word2Vec.pdf",
    "BERT word embeddings": "TIPS_NLP_BERT word embeddings.pdf",
    "WordNet": "TIPS_NLP_WordNet.pdf",
    "Lexical databases (WordNet, VerbNet, FrameNet)": "TIPS_NLP_Lexical databases (WordNet, VerbNet, FrameNet).pdf",
    "Topic modeling": "TIPS_NLP_Topic modeling.pdf",
    "Topic modeling and corpus size": "TIPS_NLP_Topic modeling and corpus size.pdf",
    "DBpedia": "TIPS_NLP_Annotator DBpedia.pdf",
    "Things to do with words: Overall view": "TIPS_NLP_Things to do with words Overall view.pdf",
}

TIPS_options = tuple(TIPS_lookup)


# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_csv_txtFile
        )
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_corpusData
        )
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_outputDirectory
        )
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_IO_setup
        )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'Semantic analysis: WSI, WSD, SRL (Open GUI)' button to open the Semantic analysis GUI.\n\nThere you can induce the different senses of keywords from how your corpus uses them (Word Sense Induction, WSI, via BERT and K-means), assign WordNet senses to words (Word Sense Disambiguation, WSD), run Semantic Role Labeling (SRL), and compute the semantic similarity of documents and cluster them.",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'Word embeddings: Gensim Word2Vec, BERT (Open GUI)' button to compute word embeddings for your corpus, with Gensim Word2Vec or BERT.\n\nWord embeddings represent each word as a vector, so that words used in similar contexts are close together. The GUI computes the distances between words and maps them in 2 or 3 dimensions (t-SNE).",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'DOCUMENT embeddings (via SBERT) (Open GUI)' button to open the Semantic analysis GUI, then tick 'DOCUMENT embeddings: Semantic similarity & clustering (via SBERT)'.\n\nEach document is embedded with SBERT (sentence-transformers); the GUI computes a document-by-document semantic similarity matrix (csv and an interactive heatmap) and clusters the documents by MEANING. It is the document-level counterpart of the word-level Word2Vec/BERT embeddings. It needs at least 2 txt documents.",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'WordNet, VerbNet, FrameNet (Open GUI)' button to work with the lexical databases WordNet, VerbNet and FrameNet.\n\nYou can zoom OUT/UP from words to their higher-level categories (e.g., 'walk', 'run', 'flee' under the verb category 'motion') and zoom IN/DOWN from a category to the words under it (e.g., 'person' to 'police', 'woman', ...).",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'Semantic Role Labeling (SRL) (Open GUI)' button to label who did what to whom, when, where and how in each sentence: the semantic roles of the arguments of each verb (agent, patient, instrument, location, time, ...).\n\nSRL is an optional install that runs in its own Python environment.",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'Topic modeling: MALLET & Gensim (Open GUI)' button to find the topics of your corpus: groups of words that tend to occur in the same documents.\n\nTopic modeling works on a corpus (a directory of documents), not on a single document.",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Click on the 'Knowledge graphs: DBpedia & YAGO (Open GUI)' button to annotate the words of your documents that match a class of the knowledge graphs DBpedia or YAGO (e.g., a person, a place, an organization).",
    )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_openOutputFiles
    )
    return y_multiplier_integer - 1


y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "These Python 3 scripts bring together the NLP Suite's SEMANTIC analyses - the analysis of MEANING (as opposed to grammatical FORM and STRUCTURE, handled by the Syntactic analysis (ALL) GUI).\n\nYou can: induce and disambiguate word senses, label semantic roles and compute the semantic similarity of documents (Semantic analysis, where Word Sense Induction now lives); compute word embeddings with Gensim Word2Vec or BERT (Word embeddings); embed whole documents with SBERT and cluster them by meaning (DOCUMENT embeddings);aggregate words into the semantic categories of WordNet, VerbNet and FrameNet; label who did what to whom (Semantic Role Labeling); find the topics of a corpus (Topic modeling); and annotate documents with the knowledge graphs DBpedia and YAGO (Knowledge graphs).\n\nEach button opens a dedicated GUI, where you then click RUN. This GUI runs no analysis of its own."


def readMe_command():
    GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)


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

GUI_util.window.mainloop()
