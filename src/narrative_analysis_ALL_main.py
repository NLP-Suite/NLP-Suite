#written by Roberto Franzosi August 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"narrative-analysis",['os','tkinter','subprocess'])==False:
    sys.exit(0)

import os
from subprocess import call

import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import run_script_util
import reminders_util


# RUN section ______________________________________________________________________________________________________________________________________________________

def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    inputdirname = GUI_util.input_main_dir_path.get()
    outdirname = GUI_util.output_dir_path.get()
    open_csv_output_checkbox = GUI_util.open_csv_output_checkbox.get()
    create_chart_output_checkbox = GUI_util.charts_package_options_widget.get()
    charts_package_options_widget = GUI_util.data_transformation_options_widget.get()
    characters_NER_var = globals()['characters_NER_var'].get()
    characters_WordNet_var = globals()['characters_WordNet_var'].get()
    characters_DBpedia_YAGO_var = globals()['characters_DBpedia_YAGO_var'].get()
    characters_byGender_var = globals()['characters_byGender_var'].get()
    characters_byGender_CoreNLP_var = globals()['characters_byGender_CoreNLP_var'].get()
    characters_byGender_dict_var = globals()['characters_byGender_dict_var'].get()
    characters_sentiment_arcs_var = globals()['characters_sentiment_arcs_var'].get()
    characters_movement_var = globals()['characters_movement_var'].get()
    dialogue_quotes_var = globals()['dialogue_quotes_var'].get()
    dialogue_coref_var = globals()['dialogue_coref_var'].get()
    characters_semantic_space_var = globals()['characters_semantic_space_var'].get()
    time_NER_var = globals()['time_NER_var'].get()
    story_plot_var = globals()['story_plot_var'].get()
    space_NER_var = globals()['space_NER_var'].get()
    space_GIS_var = globals()['space_GIS_var'].get()
    space_WordNet_var = globals()['space_WordNet_var'].get()
    space_DBpedia_YAGO_var = globals()['space_DBpedia_YAGO_var'].get()
    action_var = globals()['action_var'].get()
    action_POS_var = globals()['action_POS_var'].get()
    action_WordNet_var = globals()['action_WordNet_var'].get()
    action_VerbNet_var = globals()['action_VerbNet_var'].get()
    action_FrameNet_var = globals()['action_FrameNet_var'].get()
    action_DBpedia_YAGO_var = globals()['action_DBpedia_YAGO_var'].get()
    SVO_var = globals()['SVO_var'].get()
    shape_stories_var = globals()['shape_stories_var'].get()
    story_parts_var = globals()['story_parts_var'].get()
    extra_GUIs_var = globals()['extra_GUIs_var'].get()

    if (extra_GUIs_var==False and \
        characters_NER_var==False and \
        characters_WordNet_var==False and \
        characters_DBpedia_YAGO_var==False and \
        characters_byGender_var==False and \
        characters_byGender_CoreNLP_var==False and \
        characters_byGender_dict_var==False and \
        characters_sentiment_arcs_var==False and \
        characters_movement_var==False and \
        dialogue_quotes_var==False and \
        dialogue_coref_var==False and \
        characters_semantic_space_var==False and \
        time_NER_var==False and \
        story_plot_var==False and \
        space_NER_var==False and \
        space_GIS_var==False and \
        space_WordNet_var==False and \
        space_DBpedia_YAGO_var==False and \
        action_var==False and \
        action_POS_var==False and \
        action_WordNet_var==False and \
        action_VerbNet_var==False and \
        action_FrameNet_var==False and \
        action_DBpedia_YAGO_var==False and \
        SVO_var==False and \
        shape_stories_var==False and \
        story_parts_var==False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    config_filename = GUI_util.config_filename_selected_config.get()

    # if IO_libraries_util.check_inputPythonJavaProgramFile('parsers_annotators_main.py')==False:
    #     return
    #     run_script_util.run_script("parsers_annotators_main.py")

    if characters_NER_var==True or time_NER_var==True or space_NER_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('NER_main.py')==False:
            return
        run_script_util.run_script("NER_main.py")

    # WordNet / VerbNet / FrameNet for characters, space, and action all open the semantic
    # aggregation GUI, which aggregates nouns/verbs via any of the three lexical databases.
    if characters_WordNet_var==True or space_WordNet_var == True or action_WordNet_var == True \
            or action_VerbNet_var == True or action_FrameNet_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('semantic_aggregation_main.py')==False:
            return
        run_script_util.run_script("semantic_aggregation_main.py")

    if characters_DBpedia_YAGO_var == True or characters_DBpedia_YAGO_var == True or space_DBpedia_YAGO_var==True or action_DBpedia_YAGO_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('knowledge_graphs_main.py') == False:
            return
        run_script_util.run_script("knowledge_graphs_main.py")

    if characters_byGender_CoreNLP_var == True or characters_DBpedia_YAGO_var == True or characters_byGender_dict_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_gender_main.py') == False:
            return
        run_script_util.run_script("html_annotator_gender_main.py")

    if characters_sentiment_arcs_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_main.py') == False:
            return
        run_script_util.run_script("sentiment_analysis_main.py")

    if characters_movement_var == True:
        # the character-movement map lives in GIS_main (its "MAP characters moving in time and
        # space" option); open that GUI so this stays a launcher option like every other checkbox.
        if IO_libraries_util.check_inputPythonJavaProgramFile('GIS_main.py') == False:
            return
        run_script_util.run_script("GIS_main.py")

    if dialogue_quotes_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('parsers_annotators_main.py') == False:
            return
        run_script_util.run_script("parsers_annotators_main.py")

    if dialogue_coref_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('coreference_main.py') == False:
            return
        run_script_util.run_script("coreference_main.py")

    if characters_semantic_space_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('word2vec_main.py') == False:
            return
        run_script_util.run_script("word2vec_main.py")

    if story_plot_var==True or action_POS_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('parsers_annotators_main.py') == False:
            return
        run_script_util.run_script("parsers_annotators_main.py")

    if space_GIS_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('GIS_main.py')==False:
            return
        run_script_util.run_script("GIS_main.py")

    if SVO_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('SVO_main.py')==False:
            return
        run_script_util.run_script("SVO_main.py")

    if shape_stories_var==True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('shape_of_stories_main.py')==False:
            return
        run_script_util.run_script("shape_of_stories_main.py")

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=560, # height at brief display
                             GUI_height_full=520, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Narrative Analysis'
head, scriptName = os.path.split(os.path.basename(__file__))
# hardcode the default config here (as every other GUI does): at module-init time
# GUI_util.config_filename_selected_config is not yet populated and .get() returns '', which makes
# the startup I/O check read an empty config and falsely report the INPUT/OUTPUT fields as missing
config_filename = 'NLP_default_IO_config.csv'

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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

characters_NER_var= tk.IntVar()
characters_WordNet_var= tk.IntVar()
characters_DBpedia_YAGO_var= tk.IntVar()

characters_byGender_var= tk.IntVar()
characters_byGender_CoreNLP_var= tk.IntVar()
characters_byGender_dict_var= tk.IntVar()
characters_sentiment_arcs_var = tk.IntVar()
characters_movement_var = tk.IntVar()
dialogue_quotes_var = tk.IntVar()
dialogue_coref_var = tk.IntVar()
characters_semantic_space_var = tk.IntVar()

time_NER_var = tk.IntVar()
story_plot_var= tk.IntVar()

space_NER_var = tk.IntVar()
space_GIS_var = tk.IntVar()
space_WordNet_var = tk.IntVar()
space_DBpedia_YAGO_var = tk.IntVar()

action_var = tk.IntVar()
action_POS_var = tk.IntVar()
action_WordNet_var = tk.IntVar()
action_VerbNet_var = tk.IntVar()
action_FrameNet_var = tk.IntVar()
action_DBpedia_YAGO_var = tk.IntVar()

SVO_var = tk.IntVar()
shape_stories_var = tk.IntVar()
story_parts_var = tk.IntVar()

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

# ── 0. GUIs available for narrative analysis ──

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for narrative analysis ', variable=extra_GUIs_var, onvalue=1, offvalue=0, command=lambda: activate_extra_GUIs())
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,extra_GUIs_checkbox,True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window,extra_GUIs_menu_var,'Topic modeling (Open GUI)','Style analysis (Open GUI)','N-grams & Co-Occurrences (Open GUI)','Sentiment analysis (Open GUI)','Word2Vec/BERT embeddings (Open GUI)','WordNet (Open GUI)','Corpus Profiler (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                   extra_GUIs_menu,
                                   False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                   "Select other related types of analysis you wish to perform" \
                                    "\nThe selected GUI will open without having to press RUN")

def activate_extra_GUIs():
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    else:
        extra_GUIs_menu.configure(state='disabled')

def open_extra_GUI(*args):
    if extra_GUIs_var.get() and extra_GUIs_menu_var.get():
        if 'Topic' in extra_GUIs_menu_var.get():
            run_script_util.run_script("topic_modeling_main.py")
        if 'Style' in extra_GUIs_menu_var.get():
            run_script_util.run_script("style_analysis_main.py")
        if 'N-grams' in extra_GUIs_menu_var.get():
            run_script_util.run_script("NGrams_CoOccurrences_main.py")
        if 'Sentiment' in extra_GUIs_menu_var.get():
            run_script_util.run_script("sentiment_analysis_main.py")
        if 'Word2Vec' in extra_GUIs_menu_var.get():
            run_script_util.run_script("word2vec_main.py")
        if 'WordNet' in extra_GUIs_menu_var.get():
            run_script_util.run_script("semantic_aggregation_main.py")
        if 'Profile' in extra_GUIs_menu_var.get():
            run_script_util.run_script("corpus_profiler_main.py")
extra_GUIs_menu_var.trace('w', open_extra_GUI)

# ── 1. Characters: Who & Whom ──

characters_lb = tk.Label(window, text='Characters: Who & Whom', foreground="red",font=("Courier", 12, "bold"))
characters_lb.place(x=GUI_IO_util.labels_x_coordinate, y=GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step*y_multiplier_integer - 17)

characters_NER_var.set(0)
characters_NER_checkbox = tk.Checkbutton(window,text="Via NER", variable=characters_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,characters_NER_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Extract character names using Named Entity Recognition (NER). Identifies PERSON entities in your texts.")

characters_WordNet_var.set(0)
characters_WordNet_checkbox = tk.Checkbutton(window,text="Via WordNet", variable=characters_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,characters_WordNet_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Look up character names in the WordNet lexical database for semantic relations (e.g., hypernyms, synonyms).")

characters_DBpedia_YAGO_var.set(0)
characters_DBpedia_YAGO_checkbox = tk.Checkbutton(window,text="Via DBpedia/YAGO", variable=characters_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,characters_DBpedia_YAGO_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Annotate character names using the DBpedia/YAGO knowledge bases for encyclopedic information.")

characters_byGender_CoreNLP_var.set(0)
characters_byGender_CoreNLP_checkbox = tk.Checkbutton(window,text="By gender - Via CoreNLP", variable=characters_byGender_CoreNLP_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,characters_byGender_CoreNLP_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_4th_column,
                                   "Classify characters by gender using CoreNLP's statistical gender annotator.")

characters_byGender_dict_var.set(0)
characters_byGender_dict_checkbox = tk.Checkbutton(window,text="By gender - Via dictionaries", variable=characters_byGender_dict_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_5th_column,y_multiplier_integer,characters_byGender_dict_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_5th_column,
                                   "Classify characters by gender using name-gender dictionaries (no CoreNLP required).")

dialogue_coref_var.set(0)
dialogue_coref_checkbox = tk.Checkbutton(window,text="Who are all those he/she? Coreference resolution (CoreNLP)", variable=dialogue_coref_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,dialogue_coref_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Resolve pronouns (he, she, they) to the characters they refer to, using CoreNLP coreference resolution.")

characters_semantic_space_var.set(0)
characters_semantic_space_checkbox = tk.Checkbutton(window,text="Characters in their semantic space (BERT)", variable=characters_semantic_space_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,characters_semantic_space_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_4th_column,
                                   "Explore how close characters are to other words (actions, places, concepts) in semantic space using BERT embeddings. Opens the Word2Vec/BERT GUI.")

# ── 2. Action: What ──

action_lb = tk.Label(window, text='Action: What', foreground="red",font=("Courier", 12, "bold"))
action_lb.place(x=GUI_IO_util.labels_x_coordinate, y=GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step*y_multiplier_integer - 17)

action_POS_var.set(0)
action_POS_checkbox = tk.Checkbutton(window, text="Via POS verb tags", variable=action_POS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,action_POS_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Extract action verbs using Part-of-Speech tagging. Identifies what characters DO in the narrative.")

action_WordNet_var.set(0)
action_WordNet_checkbox = tk.Checkbutton(window, text="Via WordNet", variable=action_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,action_WordNet_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Look up action verbs in WordNet for semantic relations (hypernyms, synonyms, verb frames). Opens the semantic aggregation GUI.")

action_VerbNet_var.set(0)
action_VerbNet_checkbox = tk.Checkbutton(window, text="Via VerbNet", variable=action_VerbNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,action_VerbNet_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Aggregate action verbs into VerbNet classes (thematic-role verb classes, e.g. murder-42.1). Opens the semantic aggregation GUI.")

action_FrameNet_var.set(0)
action_FrameNet_checkbox = tk.Checkbutton(window, text="Via FrameNet", variable=action_FrameNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,action_FrameNet_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_4th_column,
                                   "Aggregate action verbs into FrameNet frames (event/scene frames such as Motion, Killing, Cause_harm). Opens the semantic aggregation GUI.")

action_DBpedia_YAGO_var.set(0)
action_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="Via DBpedia/YAGO", variable=action_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_5th_column,y_multiplier_integer,action_DBpedia_YAGO_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_5th_column,
                                   "Annotate action verbs using DBpedia/YAGO knowledge bases for encyclopedic information.")

# ── 3. Characters in action: Who does/says What ──

character_action_lb = tk.Label(window, text='Characters in action: Who does/says What', foreground="red",font=("Courier", 12, "bold"))
character_action_lb.place(x=GUI_IO_util.labels_x_coordinate, y=GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step*y_multiplier_integer - 17)

SVO_var.set(0)
SVO_checkbox = tk.Checkbutton(window, text="SVOs (Who, What, Whom)",variable=SVO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,SVO_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Extract Subject-Verb-Object triplets: who does what to whom. The basic building block of narrative action.")

dialogue_quotes_var.set(0)
dialogue_quotes_checkbox = tk.Checkbutton(window,text="Dialogues (CoreNLP)", variable=dialogue_quotes_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,dialogue_quotes_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Extract dialogue and direct speech: who says what. Uses CoreNLP quote annotator to attribute quotes to speakers.")

story_parts_var.set(0)
story_parts_checkbox = tk.Checkbutton(window,text="Narrative elements", variable=story_parts_var, onvalue=1, offvalue=0)
story_parts_checkbox.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column, y_multiplier_integer,
                                   story_parts_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Narrative elements from Labov: abstract, orientation, complicating action, evaluation, resolution, coda")

# ── 4. Scenes/settings: When & Where ──

scene_lb = tk.Label(window, text='Scenes/settings: When & Where',foreground="red",font=("Courier", 12, "bold"))
scene_lb.place(x=GUI_IO_util.labels_x_coordinate, y=GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step*y_multiplier_integer - 17)

time_NER_var.set(0)
time_NER_checkbox = tk.Checkbutton(window, text="Time (NER)",variable=time_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,time_NER_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Extract temporal expressions (dates, times, durations) using NER. When does the story happen?")

story_plot_var.set(0)
story_plot_checkbox = tk.Checkbutton(window,text="Story & plot (CoreNLP)", variable=story_plot_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,story_plot_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Analyze narrative structure via CoreNLP deep parsing: temporal sequences, plot progression, and discourse patterns.")

space_NER_var.set(0)
space_NER_checkbox = tk.Checkbutton(window, text="Space (NER)",variable=space_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,space_NER_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Extract place names (cities, countries, locations) using NER. Where does the story take place?")

space_GIS_var.set(0)
space_GIS_checkbox = tk.Checkbutton(window, text="GIS",variable=space_GIS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,space_GIS_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.narrative_analysis_4th_column,
                                   "Map extracted locations on an interactive GIS map using geocoding.")

space_WordNet_var.set(0)
space_WordNet_checkbox = tk.Checkbutton(window, text="WordNet", variable=space_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_5th_column,y_multiplier_integer,space_WordNet_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_5th_column,
                                   "Look up place names in WordNet for semantic relations.")

space_DBpedia_YAGO_var.set(0)
space_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="DBpedia/YAGO", variable=space_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,space_DBpedia_YAGO_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Annotate place names using DBpedia/YAGO knowledge bases for encyclopedic information.")

characters_movement_var.set(0)
characters_movement_checkbox = tk.Checkbutton(window,text="MAP characters moving in time and space", variable=characters_movement_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,
                                   characters_movement_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Track how characters move across locations over time. Uses Stanza NER to pair every PERSON with every LOCATION in the same sentence, producing a CSV ready for the animated movement map.")

# ── 5. Characters & emotions: How they feel ──

emotions_lb = tk.Label(window, text='Characters & emotions: How they feel', foreground="red",font=("Courier", 12, "bold"))
emotions_lb.place(x=GUI_IO_util.labels_x_coordinate, y=GUI_IO_util.basic_y_coordinate + GUI_IO_util.y_step*y_multiplier_integer - 17)

characters_sentiment_arcs_var.set(0)
characters_sentiment_arcs_checkbox = tk.Checkbutton(window,text="Sentiment arcs by character (Stanza NER + NRC)", variable=characters_sentiment_arcs_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,characters_sentiment_arcs_checkbox,
                                   True, False, True, False, 90, GUI_IO_util.labels_x_indented_coordinate,
                                   "Chart how each character's emotional arc changes across the narrative, using Stanza NER to identify characters and NRC to score sentiment.")

shape_stories_var.set(0)
shape_stories_checkbox = tk.Checkbutton(window, text="Shape of stories",variable=shape_stories_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,shape_stories_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Compute the overall emotional shape of the story (rise, fall, rise-fall, etc.) following Kurt Vonnegut's shapes of stories idea.")

def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    extra_GUIs_menu.configure(state='disabled')
    characters_NER_var.set(0)
    characters_WordNet_var.set(0)
    characters_DBpedia_YAGO_var.set(0)
    characters_byGender_CoreNLP_var.set(0)
    characters_byGender_dict_var.set(0)
    dialogue_coref_var.set(0)
    characters_semantic_space_var.set(0)
    characters_sentiment_arcs_var.set(0)
    characters_movement_var.set(0)
    action_POS_var.set(0)
    action_WordNet_var.set(0)
    action_VerbNet_var.set(0)
    action_FrameNet_var.set(0)
    action_DBpedia_YAGO_var.set(0)
    SVO_var.set(0)
    dialogue_quotes_var.set(0)
    story_parts_var.set(0)
    time_NER_var.set(0)
    story_plot_var.set(0)
    space_NER_var.set(0)
    space_GIS_var.set(0)
    space_WordNet_var.set(0)
    space_DBpedia_YAGO_var.set(0)
    shape_stories_var.set(0)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Narrative analysis":"TIPS_NLP_Things to do with words Narrative analysis.pdf",
               'WordNet':'TIPS_NLP_WordNet.pdf',
               'Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               "SVO (Subject-Verb-Object extractor)":"TIPS_NLP_SVO extraction and visualization.pdf",
               'Shape of stories':"TIPS_NLP_Shape of stories.pdf",
               "Annotator":"TIPS_NLP_Annotator.pdf",
               "DBpedia":"TIPS_NLP_Annotator DBpedia.pdf","YAGO":"TIPS_NLP_YAGO.pdf",
               'DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf',
               'YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf',
               "Annotator (via dictionary)":"TIPS_NLP_Annotator dictionary.pdf",
               "Gender annotator":"TIPS_NLP_Stanford CoreNLP gender annotator.pdf",
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf'}
TIPS_options='Narrative analysis', 'Stanford CoreNLP date extractor (NER normalized date)','WordNet','Annotator','DBpedia','DBpedia ontology classes','YAGO','YAGO (schema.org) ontology classes','Gender annotator','Annotator (via dictionary)','SVO (Subject-Verb-Object extractor)', 'Shape of stories','English Language Benchmarks', 'Things to do with words: Overall view'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    # 0. GUIs available for narrative analysis
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the 'GUIs available' checkbox to see and select other available tools suitable for narrative analysis (e.g., topic modeling, style analysis, sentiment analysis). The selected GUI will open without having to press RUN.")
    # 1. Characters: Who & Whom (identity row; no extra row for label — label floats above)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick any of the checkboxes to extract the story characters using different NLP tools.")
    # 1. Characters: Who & Whom (coreference + semantic space row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to resolve coreferences: who do all those 'he', 'she', 'they' refer to? (via CoreNLP). Or tick 'Characters in their semantic space' to explore how close characters are to other words (actions, places, concepts) using BERT embeddings.")
    # 2. Action: What (label floats above)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to extract action via the POS annotator (Part of Speech) with verb tags, one of the three lexical databases WordNet, VerbNet or FrameNet (which aggregate the action verbs into semantic categories - WordNet senses, VerbNet classes, or FrameNet frames - via the semantic aggregation GUI), or the knowledge bases DBpedia/YAGO.")
    # 3. Characters in action: Who does/says What (label floats above)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to extract SVO triplets (Subject-Verb-Object), dialogue (who says what, via CoreNLP quote annotator), or narrative elements.")
    # 4. Scenes/settings: When & Where (time + space row; label floats above)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkboxes to analyze the TEMPORAL and/or SPATIAL dimensions of stories via NER, CoreNLP, GIS, WordNet, and/or DBpedia/YAGO.")
    # 4. Scenes/settings: When & Where (DBpedia + movement tracking row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkboxes to analyze space via DBpedia/YAGO or to track how characters move across geographic locations over time (entity-location co-occurrence via Stanza NER).")
    # 5. Characters & emotions: How they feel (label floats above)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkboxes to analyze characters' emotional trajectories: sentiment arcs by character (via Stanza NER + NRC) or the overall shape of stories.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer - 1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of stories, automatically extracting the Who, What, Whom, When, and Where from texts and visualiziing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, network graphs, geographic maps, Excel charts)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# On opening, remind the user that this is a launcher: every checkbox opens its own dedicated GUI.
reminders_util.checkReminder(scriptName, reminders_util.title_options_narrative_analysis_ALL,
                             reminders_util.message_narrative_analysis_ALL, True)

GUI_util.window.mainloop()
