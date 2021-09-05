#written by Roberto Franzosi August 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"narrative-analysis",['os','tkinter','subprocess'])==False:
    sys.exit(0)

from subprocess import call

import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util


# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,inputdirname, outdirname,
        open_csv_output_checkbox,
        create_Excel_chart_output_checkbox,
        characters_NER_var,
        characters_WordNet_var,
        characters_DBpedia_YAGO_var,
        characters_bySetting_var,
        characters_byGender_var,
        characters_byGender_CoreNLP_var,
        characters_byGender_dict_var,
        time_NER_var,
        story_plot_var,
        space_NER_var,
        space_GIS_var,
        space_WordNet_var,
        space_DBpedia_YAGO_var,
        action_var,
        action_WordNet_var,
        action_DBpedia_YAGO_var,
        SVO_var,
        shape_stories_var,
        story_parts_var):

    if (characters_NER_var==False and \
        characters_WordNet_var==False and \
        characters_DBpedia_YAGO_var==False and \
        characters_bySetting_var==False and \
        characters_byGender_var==False and \
        characters_byGender_CoreNLP_var==False and \
        characters_byGender_dict_var==False and \
        time_NER_var==False and \
        story_plot_var==False and \
        space_NER_var==False and \
        space_GIS_var==False and \
        space_WordNet_var==False and \
        space_DBpedia_YAGO_var==False and \
        action_var==False and \
        action_WordNet_var==False and \
        action_DBpedia_YAGO_var==False and \
        SVO_var==False and \
        shape_stories_var==False and \
        story_parts_var==False):
            mb.showwarning(title='No options selected', message='No options have been selected.\n\nPlease, select an option and try again.')
            return

    # if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_main.py')==False:
    #     return
    #     call("python Stanford_CoreNLP_main.py", shell=True)

    if characters_NER_var==True or time_NER_var==True or space_NER_var==True:
        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_NER_main.py')==False:
            return
        call("python Stanford_CoreNLP_NER_main.py", shell=True)

    if characters_WordNet_var==True or space_WordNet_var == True or action_WordNet_var == True:
        if IO_libraries_util.inputProgramFileCheck('WordNet_main.py')==False:
            return
        call("python WordNet_main.py", shell=True)

    if characters_DBpedia_YAGO_var == True or characters_DBpedia_YAGO_var == True or space_DBpedia_YAGO_var==True or action_DBpedia_YAGO_var == True:
        if IO_libraries_util.inputProgramFileCheck('annotator_main.py') == False:
            return
        call("python annotator_main.py", shell=True)

    if characters_byGender_CoreNLP_var == True or characters_DBpedia_YAGO_var == True or characters_byGender_dict_var == True:
        if IO_libraries_util.inputProgramFileCheck('annotator_gender_main.py') == False:
            return
        call("python annotator_gender_main.py", shell=True)

    if story_plot_var==True:
        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_main.py') == False:
            return
        call("Stanford_CoreNLP_main.py", shell=True)

    if space_GIS_var==True:
        if IO_libraries_util.inputProgramFileCheck('GIS_main.py')==False:
            return
        call("python GIS_main.py", shell=True)

    if SVO_var==True:
        if IO_libraries_util.inputProgramFileCheck('SVO_main.py')==False:
            return
        call("python SVO_main.py", shell=True)

    if shape_stories_var==True:
        if IO_libraries_util.inputProgramFileCheck('shape_of_stories_main.py')==False:
            return
        call("python shape_of_stories_main.py", shell=True)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            characters_NER_var.get(),
                            characters_WordNet_var.get(),
                            characters_DBpedia_YAGO_var.get(),
                            characters_bySetting_var.get(),
                            characters_byGender_var.get(),
                            characters_byGender_CoreNLP_var.get(),
                            characters_byGender_dict_var.get(),
                            time_NER_var.get(),
                            story_plot_var.get(),
                            space_NER_var.get(),
                            space_GIS_var.get(),
                            space_WordNet_var.get(),
                            space_DBpedia_YAGO_var.get(),
                            action_var.get(),
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

GUI_size='1200x550'
GUI_label='Graphical User Interface (GUI) for Narrative Analysis'
config_filename='narrative-analysis-config.txt'
# The 6 values of config_option refer to:
#   software directory
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output file
#   output dir
# config_option=[0,4,1,0,0,1]
config_option=[0,0,0,0,0,0]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +2 is the number of lines starting at 1 of IO widgets
# y_multiplier_integer=GUI_util.y_multiplier_integer+0 #2
y_multiplier_integer = 0
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

characters_NER_var= tk.IntVar()
characters_WordNet_var= tk.IntVar()
characters_DBpedia_YAGO_var= tk.IntVar()

characters_bySetting_var= tk.IntVar()
characters_byGender_var= tk.IntVar()
characters_byGender_CoreNLP_var= tk.IntVar()
characters_byGender_dict_var= tk.IntVar()

time_NER_var = tk.IntVar()
story_plot_var= tk.IntVar()

space_NER_var = tk.IntVar()
space_GIS_var = tk.IntVar()
space_WordNet_var = tk.IntVar()
space_DBpedia_YAGO_var = tk.IntVar()

action_var = tk.IntVar()
action_WordNet_var = tk.IntVar()
action_DBpedia_YAGO_var = tk.IntVar()

SVO_var = tk.IntVar()
shape_stories_var = tk.IntVar()
story_parts_var = tk.IntVar()


characters_lb = tk.Label(window, text='Characters: Who & Whom')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,characters_lb)

characters_NER_var.set(0)
characters_NER_checkbox = tk.Checkbutton(window,text="Via NER", variable=characters_NER_var, onvalue=1, offvalue=0)
# characters_NER_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,characters_NER_checkbox,True)

characters_WordNet_var.set(0)
characters_WordNet_checkbox = tk.Checkbutton(window,text="Via WordNet", variable=characters_WordNet_var, onvalue=1, offvalue=0)
# characters_WordNet_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+190,y_multiplier_integer,characters_WordNet_checkbox,True)

characters_DBpedia_YAGO_var.set(0)
characters_DBpedia_YAGO_checkbox = tk.Checkbutton(window,text="Via DBpedia/YAGO", variable=characters_DBpedia_YAGO_var, onvalue=1, offvalue=0)
# characters_DBpedia_YAGO_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+320,y_multiplier_integer,characters_DBpedia_YAGO_checkbox,True)

characters_byGender_CoreNLP_var.set(0)
characters_byGender_CoreNLP_checkbox = tk.Checkbutton(window,text="By gender - Via CoreNLP", variable=characters_byGender_CoreNLP_var, onvalue=1, offvalue=0)
# characters_byGender_CoreNLP_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+470,y_multiplier_integer,characters_byGender_CoreNLP_checkbox,True)

characters_byGender_dict_var.set(0)
characters_byGender_dict_checkbox = tk.Checkbutton(window,text="By gender - Via dictionaries", variable=characters_byGender_dict_var, onvalue=1, offvalue=0)
# characters_byGender_dict_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+650,y_multiplier_integer,characters_byGender_dict_checkbox)

scene_lb = tk.Label(window, text='Scenes/settings (When & where action happens)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,scene_lb)

time_NER_var.set(0)
time_NER_checkbox = tk.Checkbutton(window, text="Time: When (via NER)",variable=time_NER_var, onvalue=1, offvalue=0)
# time_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,time_NER_checkbox, True)

story_plot_var.set(0)
story_plot_checkbox = tk.Checkbutton(window,text="Story & plot (Via CoreNLP NER normalized time)", variable=story_plot_var, onvalue=1, offvalue=0)
# story_plot_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+190,y_multiplier_integer,story_plot_checkbox)

space_NER_var.set(0)
space_NER_checkbox = tk.Checkbutton(window, text="Space: Where (via NER)",variable=space_NER_var, onvalue=1, offvalue=0)
#space_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,space_NER_checkbox,True)

space_GIS_var.set(0)
space_GIS_checkbox = tk.Checkbutton(window, text="Via GIS",variable=space_GIS_var, onvalue=1, offvalue=0)
#GIS_locations_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+190,y_multiplier_integer,space_GIS_checkbox,True)

space_WordNet_var.set(0)
space_WordNet_checkbox = tk.Checkbutton(window, text="Via WordNet", variable=space_WordNet_var, onvalue=1, offvalue=0)
# space_WordNet_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+320,y_multiplier_integer,space_WordNet_checkbox,True)

space_DBpedia_YAGO_var.set(0)
space_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="Via DBpedia/YAGO", variable=space_DBpedia_YAGO_var, onvalue=1, offvalue=0)
# space_DBpedia_YAGO_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+470,y_multiplier_integer,space_DBpedia_YAGO_checkbox)

characters_BySettings_lb = tk.Label(window, text='Characters in their scenes/settings')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,characters_BySettings_lb)

characters_bySetting_var.set(0)
characters_bySetting_checkbox = tk.Checkbutton(window,text="Characters (By scene/setting)", variable=characters_bySetting_var, onvalue=1, offvalue=0)
characters_bySetting_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,characters_bySetting_checkbox)

action_lb = tk.Label(window, text='Action: What')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,action_lb)

action_WordNet_var.set(0)
action_WordNet_checkbox = tk.Checkbutton(window, text="Via WordNet", variable=action_WordNet_var, onvalue=1, offvalue=0)
# action_WordNet_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20,y_multiplier_integer,action_WordNet_checkbox,True)

action_DBpedia_YAGO_var.set(0)
action_DBpedia_YAGO_checkbox = tk.Checkbutton(window, text="Via DBpedia/YAGO", variable=action_DBpedia_YAGO_var, onvalue=1, offvalue=0)
# action_DBpedia_YAGO_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+160,y_multiplier_integer,action_DBpedia_YAGO_checkbox)

SVO_var.set(0)
SVO_checkbox = tk.Checkbutton(window, text="SVOs: Who, What, Whom, When, Where",variable=SVO_var, onvalue=1, offvalue=0)
# SVO_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,SVO_checkbox,True)

shape_stories_var.set(0)
shape_stories_checkbox = tk.Checkbutton(window, text="Shape of stories",variable=shape_stories_var, onvalue=1, offvalue=0)
# shape_stories_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+260,y_multiplier_integer,shape_stories_checkbox,True)

story_parts_var.set(0)
story_parts_checkbox = tk.Checkbutton(window,text="Narrative elements (Labov's abstract, orientation, complicating action, evaluation, resolution, coda)", variable=story_parts_var, onvalue=1, offvalue=0)
story_parts_checkbox.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+460,y_multiplier_integer,story_parts_checkbox)

#abstract; orientation; complicating action; evaluation; resolution; and coda

TIPS_lookup = {"Narrative analysis":"TIPS_NLP_Things to do with words Narrative analysis.pdf",'WordNet':'TIPS_NLP_WordNet.pdf','Stanford CoreNLP date extractor (NER normalized date)':'TIPS_NLP_Stanford CoreNLP date extractor.pdf',"SVO (Subject-Verb-Object extractor)":"TIPS_NLP_SVO extraction and visualization.pdf",'Shape of stories':"TIPS_NLP_Shape of stories.pdf","Annotator":"TIPS_NLP_Annotator.pdf","DBpedia":"TIPS_NLP_Annotator DBpedia.pdf","YAGO":"TIPS_NLP_Annotator YAGO.pdf",'DBpedia ontology classes':'TIPS_NLP_Annotator DBpedia ontology classes.pdf','YAGO (schema.org) ontology classes':'TIPS_NLP_Annotator YAGO (schema.org) ontology classes.pdf',"Annotator (via dictionary)":"TIPS_NLP_Annotator dictionary.pdf","Gender annotator":"TIPS_NLP_Gender annotator.pdf"}
TIPS_options='Narrative analysis', 'Stanford CoreNLP date extractor (NER normalized date)','WordNet','Annotator','DBpedia','DBpedia ontology classes','YAGO','YAGO (schema.org) ontology classes','Gender annotator','Annotator (via dictionary)','SVO (Subject-Verb-Object extractor)', 'Shape of stories'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",GUI_IO_util.msg_CoNLL)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step, "Help","Please, tick any of the checkboxes to extract the story characters using different NLP tools.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step*3, "Help","Please, tick the checkbox to analyze the TEMPORAL (story/plot) dimensions of stories, extracting time via Stanford CoreNLP NER normalized time.")
    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step*4, "Help","Please, tick any of the checkboxes to analyze the SPATIAL dimensions of stories via the GIS pipeline, WordNet, and/or the knowledge bases DBpedia/YAGO.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","Please, tick the checkbox to extract characters by setting.\n\nThe option is not available. Sorry!")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help","Please, tick the checkboxes to extract action via WordNet or the knowledge bases DBpedia/YAGO.")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help","Please, tick the checkboxes:\n\n  1. to open the specialized GUI to extract SVO triplets (Subject-Verb-Object) and time (When) and location (Where);\n  2. to open the specialized GUI to analyze the shape of stories;\n  3. to open the specialized GUI to analyze narrative elements.")

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="The GUI brings together various Python 3 scripts to buil a pipeline for the analysis of stories, automatically extracting the Who, What, Whom, When, and Where from texts and visualiziing the results.\n\nEach tool performs all required computations then saves results as csv files and visualizes them in various ways (word clouds, network graphs, geographic maps, Excel charts)."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options, IO_setup_display_brief)

GUI_util.window.mainloop()
