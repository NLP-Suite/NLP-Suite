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


# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputdirname, outdirname,
        open_csv_output_checkbox,
        create_chart_output_checkbox,
        charts_package_options_widget,
        characters_NER_var,
        characters_WordNet_var,
        characters_DBpedia_YAGO_var,
        characters_byGender_var,
        characters_byGender_CoreNLP_var,
        characters_byGender_dict_var,
        characters_sentiment_arcs_var,
        characters_movement_var,
        dialogue_quotes_var,
        dialogue_coref_var,
        time_NER_var,
        story_plot_var,
        space_NER_var,
        space_GIS_var,
        space_WordNet_var,
        space_DBpedia_YAGO_var,
        action_var,
        action_POS_var,
        action_WordNet_var,
        action_DBpedia_YAGO_var,
        SVO_var,
        shape_stories_var,
        story_parts_var):

    if (characters_NER_var==False and \
        characters_WordNet_var==False and \
        characters_DBpedia_YAGO_var==False and \
        characters_byGender_var==False and \
        characters_byGender_CoreNLP_var==False and \
        characters_byGender_dict_var==False and \
        characters_sentiment_arcs_var==False and \
        characters_movement_var==False and \
        dialogue_quotes_var==False and \
        dialogue_coref_var==False and \
        time_NER_var==False and \
        story_plot_var==False and \
        space_NER_var==False and \
        space_GIS_var==False and \
        space_WordNet_var==False and \
        space_DBpedia_YAGO_var==False and \
        action_var==False and \
        action_POS_var==False and \
        action_WordNet_var==False and \
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

    if characters_WordNet_var==True or space_WordNet_var == True or action_WordNet_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('knowledge_graphs_WordNet_main.py')==False:
            return
        run_script_util.run_script("knowledge_graphs_WordNet_main.py")

    if characters_DBpedia_YAGO_var == True or characters_DBpedia_YAGO_var == True or space_DBpedia_YAGO_var==True or action_DBpedia_YAGO_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('knowledge_graphs_DBpedia_YAGO_main.py') == False:
            return
        run_script_util.run_script("knowledge_graphs_DBpedia_YAGO_main.py")

    if characters_byGender_CoreNLP_var == True or characters_DBpedia_YAGO_var == True or characters_byGender_dict_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('html_annotator_gender_main.py') == False:
            return
        run_script_util.run_script("html_annotator_gender_main.py")

    if characters_sentiment_arcs_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('sentiment_analysis_main.py') == False:
            return
        run_script_util.run_script("sentiment_analysis_main.py")

    if characters_movement_var == True:
        import NER_location_tracking_util
        filesToOpen = NER_location_tracking_util.main(inputFilename, inputdirname, outdirname)
        if filesToOpen and open_csv_output_checkbox:
            import IO_files_util
            IO_files_util.OpenOutputFiles(GUI_util.window, open_csv_output_checkbox, filesToOpen, outdirname)

    if dialogue_quotes_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('parsers_annotators_main.py') == False:
            return
        run_script_util.run_script("parsers_annotators_main.py")

    if dialogue_coref_var == True:
        if IO_libraries_util.check_inputPythonJavaProgramFile('coreference_main.py') == False:
            return
        run_script_util.run_script("coreference_main.py")

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
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            GUI_util.data_transformation_options_widget.get(),
                            characters_NER_var.get(),
                            characters_WordNet_var.get(),
                            characters_DBpedia_YAGO_var.get(),
                            characters_byGender_var.get(),
                            characters_byGender_CoreNLP_var.get(),
                            characters_byGender_dict_var.get(),
                            characters_sentiment_arcs_var.get(),
                            characters_movement_var.get(),
                            dialogue_quotes_var.get(),
                            dialogue_coref_var.get(),
                            time_NER_var.get(),
                            story_plot_var.get(),
                            space_NER_var.get(),
                            space_GIS_var.get(),
                            space_WordNet_var.get(),
                            space_DBpedia_YAGO_var.get(),
                            action_var.get(),
                            action_POS_var.get(),
                            action_WordNet_var.get(),
                            action_DBpedia_YAGO_var.get(),
                            SVO_var.get(),
                            shape_stories_var.get(),
                            story_parts_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=False

GUI_width=str(GUI_IO_util.get_GUI_width(2))
GUI_size = GUI_width + 'x600' #height

GUI_label='Graphical User Interface (GUI) for Narrative Analysis'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = GUI_util.config_filename_selected_config.get()
increment = 0

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
config_input_output_numeric_options=[0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
# y_multiplier_integer=GUI_util.y_multiplier_integer+0 #2
y_multiplier_integer = 0
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

time_NER_var = tk.IntVar()
story_plot_var= tk.IntVar()

space_NER_var = tk.IntVar()
space_GIS_var = tk.IntVar()
space_WordNet_var = tk.IntVar()
space_DBpedia_YAGO_var = tk.IntVar()

action_var = tk.IntVar()
action_POS_var = tk.IntVar()
action_WordNet_var = tk.IntVar()
action_DBpedia_YAGO_var = tk.IntVar()

SVO_var = tk.IntVar()
shape_stories_var = tk.IntVar()
story_parts_var = tk.IntVar()


# ── 1. Characters: Who & Whom ──

characters_lb = tk.Label(window, text='Characters: Who & Whom', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,characters_lb)

characters_NER_var.set(0)
characters_NER_checkbox = tk.Checkbutton(window,text="Via NER", variable=characters_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,characters_NER_checkbox,True)

characters_WordNet_var.set(0)
characters_WordNet_checkbox = tk.Checkbutton(window,text="Via WordNet", variable=characters_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,characters_WordNet_checkbox,True)

characters_DBpedia_YAGO_var.set(0)
characters_DBpedia_YAGO_checkbox = tk.Checkbutton(window,text="Via DBpedia/YAGO", variable=characters_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,characters_DBpedia_YAGO_checkbox,True)

characters_byGender_CoreNLP_var.set(0)
characters_byGender_CoreNLP_checkbox = tk.Checkbutton(window,text="By gender - Via CoreNLP", variable=characters_byGender_CoreNLP_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,characters_byGender_CoreNLP_checkbox,True)

characters_byGender_dict_var.set(0)
characters_byGender_dict_checkbox = tk.Checkbutton(window,text="By gender - Via dictionaries", variable=characters_byGender_dict_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_5th_column,y_multiplier_integer,characters_byGender_dict_checkbox)

dialogue_coref_var.set(0)
dialogue_coref_checkbox = tk.Checkbutton(window,text="Who are all those he/she? Coreference resolution (CoreNLP)", variable=dialogue_coref_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,dialogue_coref_checkbox)

# ── 2. Action: What ──

action_lb = tk.Label(window, text='Action: What', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,action_lb)

action_POS_var.set(0)
action_POS_checkbox = tk.Checkbutton(window, text="Via POS verb tags", variable=action_POS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,action_POS_checkbox,True)

action_WordNet_var.set(0)
action_WordNet_checkbox = tk.Checkbutton(window, text="Via WordNet", variable=action_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,action_WordNet_checkbox,True)

action_DBpedia_YAGO_var.set(0)
action_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="Via DBpedia/YAGO", variable=action_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,action_DBpedia_YAGO_checkbox)

# ── 3. Characters in action: Who does/says What ──

character_action_lb = tk.Label(window, text='Characters in action: Who does/says What', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,character_action_lb)

SVO_var.set(0)
SVO_checkbox = tk.Checkbutton(window, text="SVOs (Who, What, Whom)",variable=SVO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,SVO_checkbox,True)

dialogue_quotes_var.set(0)
dialogue_quotes_checkbox = tk.Checkbutton(window,text="Dialogues (CoreNLP)", variable=dialogue_quotes_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,dialogue_quotes_checkbox,True)

story_parts_var.set(0)
story_parts_checkbox = tk.Checkbutton(window,text="Narrative elements", variable=story_parts_var, onvalue=1, offvalue=0)
story_parts_checkbox.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column, y_multiplier_integer,
                                   story_parts_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_3rd_column,
                                   "Narrative elements from Labov: abstract, orientation, complicating action, evaluation, resolution, coda")

# ── 4. Scenes/settings: When & Where ──

scene_lb = tk.Label(window, text='Scenes/settings: When & Where',foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,scene_lb)

time_NER_var.set(0)
time_NER_checkbox = tk.Checkbutton(window, text="Time (NER)",variable=time_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,time_NER_checkbox, True)

story_plot_var.set(0)
story_plot_checkbox = tk.Checkbutton(window,text="Story & plot (CoreNLP)", variable=story_plot_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,story_plot_checkbox,True)

space_NER_var.set(0)
space_NER_checkbox = tk.Checkbutton(window, text="Space (NER)",variable=space_NER_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,space_NER_checkbox,True)

space_GIS_var.set(0)
space_GIS_checkbox = tk.Checkbutton(window, text="GIS",variable=space_GIS_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_4th_column,y_multiplier_integer,space_GIS_checkbox,True)

space_WordNet_var.set(0)
space_WordNet_checkbox = tk.Checkbutton(window, text="WordNet", variable=space_WordNet_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_5th_column,y_multiplier_integer,space_WordNet_checkbox)

space_DBpedia_YAGO_var.set(0)
space_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="DBpedia/YAGO", variable=space_DBpedia_YAGO_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,space_DBpedia_YAGO_checkbox,True)

characters_movement_var.set(0)
characters_movement_checkbox = tk.Checkbutton(window,text="Movement tracking (Stanza NER): Characters across time and space", variable=characters_movement_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_2nd_column,y_multiplier_integer,
                                   characters_movement_checkbox,
                                   False, False, True, False, 90, GUI_IO_util.narrative_analysis_2nd_column,
                                   "Track how characters move across locations over time. Uses Stanza NER to pair every PERSON with every LOCATION in the same sentence, producing a CSV ready for the animated movement map.")

# ── 5. Characters & emotions: How they feel ──

emotions_lb = tk.Label(window, text='Characters & emotions: How they feel', foreground="red",font=("Courier", 12, "bold"))
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,emotions_lb)

characters_sentiment_arcs_var.set(0)
characters_sentiment_arcs_checkbox = tk.Checkbutton(window,text="Sentiment arcs by character (Stanza NER + NRC)", variable=characters_sentiment_arcs_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,characters_sentiment_arcs_checkbox,True)

shape_stories_var.set(0)
shape_stories_checkbox = tk.Checkbutton(window, text="Shape of stories",variable=shape_stories_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.narrative_analysis_3rd_column,y_multiplier_integer,shape_stories_checkbox)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Narrative analysis":"TIPS_NLP_Things to do with words Narrative analysis.pdf",
               'WordNet':'TIPS_NLP_WordNet.pdf',
               'Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',
               "SVO (Subject-Verb-Object extractor)":"TIPS_NLP_SVO extraction and visualization.pdf",
               'Shape of stories':"TIPS_NLP_Shape of stories.pdf",
               "Annotator":"TIPS_NLP_Annotator.pdf",
               "DBpedia":"TIPS_NLP_Annotator DBpedia.pdf","YAGO":"TIPS_NLP_Annotator YAGO.pdf",
               'DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf',
               'YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf',
               "Annotator (via dictionary)":"TIPS_NLP_Annotator dictionary.pdf",
               "Gender annotator":"TIPS_NLP_Gender annotator.pdf",
               'English Language Benchmarks': 'TIPS_NLP_English Language Benchmarks.pdf',
               'Things to do with words: Overall view': 'TIPS_NLP_Things to do with words Overall view.pdf'}
TIPS_options='Narrative analysis', 'Stanford CoreNLP date extractor (NER normalized date)','WordNet','Annotator','DBpedia','DBpedia ontology classes','YAGO','YAGO (schema.org) ontology classes','Gender annotator','Annotator (via dictionary)','SVO (Subject-Verb-Object extractor)', 'Shape of stories','English Language Benchmarks', 'Things to do with words: Overall view'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_CoNLL)
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_corpusData)
    # y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    # 1. Characters: Who & Whom (identity row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick any of the checkboxes to extract the story characters using different NLP tools.")
    # 1. Characters: Who & Whom (coreference row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer, "NLP Suite Help","Please, tick the checkbox to resolve coreferences: who do all those 'he', 'she', 'they' refer to? (via CoreNLP).")
    # 2. Action: What
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help","Please, tick the checkboxes to extract action via the POS annotator (Part of Speech) with verb tags, WordNet or the knowledge bases DBpedia/YAGO.")
    # 3. Characters in action: Who does/says What
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help","Please, tick the checkboxes to extract SVO triplets (Subject-Verb-Object), dialogue (who says what, via CoreNLP quote annotator), or narrative elements.")
    # 4. Scenes/settings: When & Where (time + space row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer+1, "NLP Suite Help","Please, tick the checkboxes to analyze the TEMPORAL and/or SPATIAL dimensions of stories via NER, CoreNLP, GIS, WordNet, and/or DBpedia/YAGO.")
    # 4. Scenes/settings: When & Where (DBpedia + movement tracking row)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help","Please, tick the checkboxes to analyze space via DBpedia/YAGO or to track how characters move across geographic locations over time (entity-location co-occurrence via Stanza NER).")
    # 5. Characters & emotions: How they feel
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer+1,"NLP Suite Help","Please, tick the checkboxes to analyze characters' emotional trajectories: sentiment arcs by character (via Stanza NER + NRC) or the overall shape of stories.")

    return y_multiplier_integer
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,1)

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of stories, automatically extracting the Who, What, Whom, When, and Where from texts and visualiziing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, network graphs, geographic maps, Excel charts)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
