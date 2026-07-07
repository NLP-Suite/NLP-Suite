# Roberto Franzosi September 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Stanford_CoreNLP_NER_extractor",['os','pandas','tkinter'])==False:
    sys.exit(0)
# IBM https://ibm.github.io/zshot/ "pip install zshot"

import os
import tkinter as tk
import tkinter.messagebox as mb
from subprocess import call

import GUI_IO_util
import IO_files_util
import reminders_util
import config_util
import spaCy_util
import Stanford_CoreNLP_util
import Stanza_util
import NER_entity_timeline_util
import run_script_util

# location NER tags across all schemes (CoreNLP, OntoNotes, CoNLL); BIOES prefixes are stripped before testing
_LOCATION_TAGS = ('GPE', 'LOC', 'LOCATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY')

def _find_main_NER_csv(files):
    # pick the main NER data csv from the produced files (skip charts/freq/timeline/geocoded files)
    import os as _os
    for f in files:
        if not isinstance(f, str) or not f.lower().endswith('.csv'):
            continue
        b = _os.path.basename(f).lower()
        if 'ner' in b and not any(x in b for x in ('freq', 'chart', 'hyperlink', 'timeline', 'summary', 'tracking', 'not-found', 'geo-')):
            return f
    return ''

def _count_location_entities(ner_csv):
    # count location entities in an NER output csv (entity heads when a Multi-Word Expression column exists)
    import pandas as pd
    try:
        df = pd.read_csv(ner_csv, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        return 0
    if 'NER' not in df.columns:
        return 0
    loc_mask = df['NER'].astype(str).apply(lambda t: str(t).split('-')[-1] in _LOCATION_TAGS)
    sub = df[loc_mask]
    if 'Multi-Word Expression' in df.columns and len(sub) > 0:
        mwe = sub['Multi-Word Expression'].astype(str)
        heads = sub[(mwe.str.strip() != '') & (mwe.str.lower() != 'nan') & (mwe != 'O')]
        if len(heads) > 0:
            return len(heads)
    return len(sub)

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation, config_filename,
        NER_package, NER_list, NER_entity_timeline):

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []  # Store all files that are to be opened once finished

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]

    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    if NER_entry_var.get().strip() == '' and not NER_entity_timeline:
        mb.showwarning(title='No options selected',
                       message='No options have been selected.\n\nPlease, select an option and try again.')
        return

    if len(NER_list)==0 and 'CoreNLP' in NER_packages_var.get():
        mb.showwarning(title='No NER tag selected', message='No NER tag has been selected.\n\nPlease, select an NER tag and try again.')
        return

    skip_NER_extraction = NER_entity_timeline and NER_entry_var.get().strip() == ''

# BERT -------------------------------------------------------------------------

    if not skip_NER_extraction and ('*' in NER_package or 'BERT' in NER_package):
        if language!='English':
            mb.showwarning(title='Warning', message='NER in BERT is only available for the English language. Your currently selected language is ' + language + '.' \
            "\n\nYou can change the selected language using the Setup dropdown menu at the bottom of this GUI, select the 'Setup NLP package and corpus language' to open the GUI where you can change the language option.")
            return
        import BERT_util
        # '*' (run all) extracts every tag; an explicit BERT run honors the user's tag selection
        if '*' in NER_package:
            NER_selection = ', '.join(BERT_util.NER_dict['NERs'])
        else:
            NER_selection = NER_entry_var.get()
        outputFiles = BERT_util.NER_tags_BERT(window,inputFilename, inputDir, outputDir, config_filename, '', chartPackage, dataTransformation, NERs=NER_selection)
        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# spaCy -------------------------------------------------------------------------

    if not skip_NER_extraction and ('*' in NER_package or 'spaCy' in NER_package):
        document_length_var = 1
        limit_sentence_length_var = 1000
        # '*' (run all) extracts every tag; an explicit spaCy run honors the user's tag selection
        if '*' in NER_package:
            NER_selection = ', '.join(spaCy_util.NER_dict)
        else:
            NER_selection = NER_entry_var.get()
        outputFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                    outputDir,
                                                    openOutputFiles,
                                                    chartPackage, dataTransformation,
                                                    ['NER'], False,
                                                    language,
                                                    memory_var, document_length_var, limit_sentence_length_var,
                                                    NERs=NER_selection,
                                                    filename_embeds_date_var=filename_embeds_date_var,
                                                    date_format=date_format_var,
                                                    items_separator_var=items_separator_var,
                                                    date_position_var=date_position_var)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# Stanford CoreNLP -------------------------------------------------------------------------

    if not skip_NER_extraction and ('*' in NER_package or 'CoreNLP' in NER_package):
        NER_list = NER_entry_var.get() #Stanford_CoreNLP_util.NER_list
        outputFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir, outputDir,
                                                            openOutputFiles, chartPackage, dataTransformation,
                                                            'NER',
                                                            language=language_var,
                                                            NERs=NER_list,
                                                            DoCleanXML=False,
                                                            export_json_var= export_json_var,
                                                            memory_var=memory_var,
                                                            document_length=document_length_var,
                                                            sentence_length=limit_sentence_length_var,
                                                            extract_date_from_text_var=extract_date_from_text_var,
                                                            filename_embeds_date_var=filename_embeds_date_var,
                                                            date_format=date_format_var,
                                                            items_separator_var=items_separator_var,
                                                            date_position_var=date_position_var)

        if outputFiles!=None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# Stanza -------------------------------------------------------------------------

    if not skip_NER_extraction and ('*' in NER_package or 'Stanza' in NER_package):
        document_length_var = 1
        limit_sentence_length_var = 1000

        # '*' (run all) extracts every tag; an explicit Stanza run honors the user's tag selection
        if '*' in NER_package:
            NER_selection = ', '.join(get_NER_list('Stanza', language))
        else:
            NER_selection = NER_entry_var.get()

        outputFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir,
                                                      openOutputFiles,
                                                      chartPackage, dataTransformation,
                                                      'NER', False,
                                                      language_list,
                                                      memory_var, document_length_var, limit_sentence_length_var,
                                                      filename_embeds_date_var=filename_embeds_date_var,
                                                      NERs=NER_selection,
                                                      date_format=date_format_var,
                                                      items_separator_var=items_separator_var,
                                                      date_position_var=date_position_var)

        if outputFiles!= None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# NER Entity Timeline (Stanza) -------------------------------------------------------------------------

    if NER_entity_timeline:
        if 'Stanza' not in NER_package and NER_package != '*':
            mb.showwarning(title='NER Entity Timeline',
                           message='The NER Entity Timeline always uses Stanza as its NER engine, regardless of the NER package selected above (' + NER_package + ').\n\nThe NER extraction selected above will still run with ' + NER_package + '.')
        outputFiles = NER_entity_timeline_util.main(GUI_util.inputFilename.get(),
                                                     GUI_util.input_main_dir_path.get(),
                                                     GUI_util.output_dir_path.get(),
                                                     chartPackage, dataTransformation)
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

# Offer to geocode & map extracted locations -------------------------------------------------
    if not skip_NER_extraction:
        ner_csv = _find_main_NER_csv(filesToOpen)
        nLocations = _count_location_entities(ner_csv) if ner_csv else 0
        if nLocations > 0:
            if mb.askyesno('Map extracted locations?',
                    str(nLocations) + " location entities were extracted.\n\n"
                    "Would you like to geocode and map them now (Google Earth Pro + folium pin/heat maps)?\n\n"
                    "NOTE: geocoding contacts an online service for each location, so this can take some time "
                    "(especially with Nominatim, which is rate-limited to about 1 request per second).\n\n"
                    "For many more mapping options - choice of geocoder (Nominatim/Google), folium pin & heat maps, "
                    "proportional-circle maps, QGIS, Tableau, TimeMapper, date-based animation, custom icons and "
                    "labels - use the dedicated GIS GUI (GIS_main), which can take this NER output as its input."):
                import GIS_pipeline_util
                # place GIS output inside the NER folder, in a 'GIS' subfolder (like SVO),
                # so only one output folder is opened. Resolve ner_csv to an absolute path first
                # so the GIS subfolder (and the KML path GEP receives) is absolute, not relative
                # to the process cwd.
                ner_csv = os.path.abspath(ner_csv)
                gis_subdir = IO_files_util.make_output_subdirectory('', '', os.path.dirname(ner_csv), label='GIS', silent=True)
                # GIS_pipeline requires a 'Location' column; the raw NER csv has 'Form'/'Word' and
                # BIOES tags. Normalize it (Form->Location, tag normalization, multi-word merge) first.
                prepared_csv = os.path.join(gis_subdir, os.path.basename(ner_csv))
                prepared_csv = GIS_pipeline_util.normalize_NER_csv_for_GIS(ner_csv, prepared_csv,
                                    filename_embeds_date_var=filename_embeds_date_var,
                                    date_format=date_format_var, items_separator=items_separator_var,
                                    date_position=date_position_var)
                if prepared_csv == '':
                    mb.showinfo('No mappable locations',
                        'No mappable location entities were found in the NER output, so no map was produced.')
                    gis_out = None
                else:
                    # auto-pick the geocoder silently: Google only if a key is already configured,
                    # otherwise Nominatim (no "enter API key" nag for users without a Google key)
                    geocoder = 'Google' if GIS_pipeline_util.has_google_api_key('Google-geocode-API_config.csv') else 'Nominatim'
                    date_present = bool(filename_embeds_date_var)
                    gis_out = GIS_pipeline_util.GIS_pipeline(GUI_util.window, config_filename, prepared_csv, inputDir,
                                gis_subdir, geocoder, 'Google Earth Pro & Google Maps & Python folium pin map & heatmap', chartPackage, dataTransformation,
                                date_present, '', '', False, 'Location', 'utf-8',
                                0, 1, [''], [''], ['Pushpins'], ['red'], [0], ['1'], [0], [''], [1], [1])
                if gis_out is not None:
                    if isinstance(gis_out, str):
                        gis_out = [gis_out]
                    # the user explicitly chose to map -> open the maps NOW, regardless of the
                    # 'open output files' checkbox; let non-map GIS files go through normal handling
                    for f in gis_out:
                        if not isinstance(f, str):
                            continue
                        is_map = f.endswith('.kml') or (f.endswith('.html') and 'Folium' in f)
                        if is_map and os.path.isfile(f):
                            if f.endswith('.kml'):
                                IO_files_util.open_kmlFile(GUI_util.window, f)
                            else:
                                try:
                                    IO_files_util.openFile(GUI_util.window, f)
                                except Exception:
                                    pass
                        else:
                            filesToOpen.append(f)

    if openOutputFiles==True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

    if '*' in NER_package:
        NER_list = []
        NER_tag_var.set(' ')
        NER_entry_var.set(NER_list)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(
                            GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            GUI_util.data_transformation_options_widget.get(),
                            config_filename,
                            NER_packages_var.get(),
                            NER_list,
                            NER_entity_timeline_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                             GUI_width=GUI_IO_util.get_GUI_width(3),
                             GUI_height_brief=390, # height at brief display
                             GUI_height_full=460, # height at full display
                             y_multiplier_integer=GUI_util.y_multiplier_integer,
                             y_multiplier_integer_add=2, # to be added for full display
                             increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for NER (Named Entity Recognition) Extraction'
config_filename = 'NLP_default_IO_config.csv'
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
config_input_output_numeric_options=[2,1,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
inputFilename=GUI_util.inputFilename

input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

NER_list=[]

encoding_var=tk.StringVar()

NER_tag_var = tk.StringVar()
NER_entry_var = tk.StringVar()

global coming_from_add, coming_from_reset
coming_from_add = False
coming_from_reset = False

GUI=''

def open_GUI1():
    run_script_util.run_script("file_checker_converter_cleaner_main.py")

pre_processing_button = tk.Button(window, text='Pre-processing tools (file checking & cleaning GUI)',command=open_GUI1)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               pre_processing_button)

NER_entry_lb = tk.Label(window, text='NER packages')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,NER_entry_lb,True)

NER_packages_var = tk.StringVar()
NER_packages_var.set('BERT (English language model)')
# IBM https://ibm.github.io/zshot/ "pip install zshot" — placeholder; not yet implemented
NER_packages_menu = tk.OptionMenu(window,NER_packages_var,'*', 'BERT (English language model)','IBM','spaCy','Stanford CoreNLP','Stanza')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_packages_menu_pos, y_multiplier_integer,
                    NER_packages_menu, False, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Select the NER package you wish to use as NER annotator")

NER_tag_lb = tk.Label(window, text='NER tags')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,NER_tag_lb,True)

# NER tags menu
# CoreNLP uses its own fine-grained NER scheme (CITY, STATE_OR_PROVINCE, CAUSE_OF_DEATH, ...)
NER_tags_CoreNLP = ['All NER tags', '--- All quantitative expressions','NUMBER', 'ORDINAL', 'PERCENT', '--- All social actors', 'PERSON', 'ORGANIZATION', '--- All spatial expressions', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION', '--- All temporal expressions', 'DATE', 'TIME', 'DURATION', 'SET',  '--- All other expressions', 'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE', 'EMAIL', 'IDEOLOGY', 'MISC', 'MONEY', 'NATIONALITY', 'RELIGION', 'TITLE', 'URL']
# spaCy and Stanza (English) use the OntoNotes scheme (GPE, LOC, NORP, FAC, CARDINAL, ...)
NER_tags_OntoNotes = ['All NER tags', '--- All quantitative expressions', 'CARDINAL', 'ORDINAL', 'PERCENT', 'MONEY', 'QUANTITY', '--- All social actors', 'PERSON', 'NORP', 'ORG', '--- All spatial expressions', 'GPE', 'LOC', 'FAC', '--- All temporal expressions', 'DATE', 'TIME', '--- All other expressions', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']
# BERT now uses an OntoNotes-fine-tuned model (djagatiya/ner-roberta-base-ontonotesv5-englishv4),
# so it shares the same grouped OntoNotes scheme (18 tags, by category) as spaCy & Stanza
NER_tags_BERT = NER_tags_OntoNotes

NER_tag_var.set('All NER tags') #--- All NER tags
NER_menu = tk.OptionMenu(window,NER_tag_var,*NER_tags_CoreNLP)

# repopulate the NER tags dropdown to match the selected package's NER scheme
def set_NER_menu_options(tags_list):
    menu = NER_menu['menu']
    menu.delete(0, 'end')
    for tag in tags_list:
        menu.add_command(label=tag, command=lambda value=tag: NER_tag_var.set(value))

# the package's full set of real tags (excludes the 'All NER tags' and '--- ...' selectors)
def _full_tag_set(pkg):
    if 'BERT' in pkg:
        tags = NER_tags_BERT
    elif ('spaCy' in pkg) or ('Stanza' in pkg):
        tags = NER_tags_OntoNotes
    else:
        tags = NER_tags_CoreNLP
    return {t for t in tags if t != 'All NER tags' and '---' not in t}
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_menu_pos, y_multiplier_integer,
                    NER_menu, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Options currently available only for Stanford CoreNLP.\nSelect the NER tag(s) you wish to search for. Click on the + or Reset buttons when the widget is disabled to add new NER tags or to start fresh.")

add_NER_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width,height=1,state='disabled',command=lambda: activate_NER_Options(True,False))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                    add_NER_button, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Click on the + button, when available, to add a new NEW tag. Option currently available only for Stanford CoreNLP.\nSelect the NER tag(s) you wish to search for. Click on the + or Reset buttons when the widget is disabled to add new NER tags or to start fresh.")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.setup_pop_up_text_widget,y_multiplier_integer,add_NER_button, True)

reset_NER_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width,height=1,state='disabled',command=lambda: clear_NER_list(coming_from_add=False,coming_from_reset=True))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_reset_NER_button_pos, y_multiplier_integer,
                    reset_NER_button, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate,
                    "Click the 'Reset ' button, to clear all currently selected NER tags and start fresh, selecting and adding new NER tags. The option is currently available only for Stanford CoreNLP.")

# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_reset_NER_button_pos,y_multiplier_integer,reset_NER_button,True)

NER_entry_lb = tk.Label(window, text='NER list')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_entry_lb_pos,y_multiplier_integer,NER_entry_lb,True)

NER_entry = tk.Entry(window,width=GUI_IO_util.widget_width_medium,textvariable=NER_entry_var)
NER_entry.configure(state="disabled")
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_entry_pos, y_multiplier_integer,
                    NER_entry, False, False, True, False,
                    90, GUI_IO_util.open_reminders_x_coordinate,
                    "The widget, always disabled, displays all the NER tags available for the selected package")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.NER_NER_entry_pos,y_multiplier_integer,NER_entry)

NER_entity_timeline_var = tk.IntVar()
NER_entity_timeline_checkbox = tk.Checkbutton(window, text='NER Entity Timeline (when people/places/organizations appear across narrative, via Stanza)', variable=NER_entity_timeline_var, onvalue=1, offvalue=0)
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_indented_coordinate,y_multiplier_integer,NER_entity_timeline_checkbox)

def clear(e):
    NER_entity_timeline_var.set(0)
    clear_NER_list(coming_from_add=False,coming_from_reset=True)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def add_NER_tag(coming_from_add, coming_from_reset):
    global NER_list
    # if '---' in str(NER_list):
    #     mb.showwarning(title='Warning', message='You cannot add any other NER tags once you have selected an NER set ---\n\nPlease, press ESCape or RESET or RUN.')
    #     window.focus_force()
    #     return

    reset_NER_button.configure(state='normal')
    if coming_from_reset:
        NER_tag_var.set(' ')
        NER_entry_var.set(' ')
        coming_from_reset = False
        return coming_from_reset
    if coming_from_add:
        add_NER_button.configure(state='normal')
    pkg = NER_packages_var.get()
    sel = NER_tag_var.get()
    # BERT (OntoNotes-fine-tuned model), spaCy and Stanza all use the OntoNotes NER scheme;
    # CoreNLP uses its own fine-grained scheme
    if ('BERT' in pkg) or ('spaCy' in pkg) or ('Stanza' in pkg):
        if 'All NER tags' in sel:
            NER_list = ['PERSON', 'NORP', 'ORG', 'GPE', 'LOC', 'FAC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
            NER_entry_var.set(', '.join(NER_list))
        elif sel == '--- All quantitative expressions':
            NER_list = ['CARDINAL', 'ORDINAL', 'PERCENT', 'MONEY', 'QUANTITY']
            NER_entry_var.set(', '.join(NER_list))
        elif sel == '--- All social actors':
            NER_list = ['PERSON', 'NORP', 'ORG']
            NER_entry_var.set(', '.join(NER_list))
        elif sel == '--- All spatial expressions':
            NER_list = ['GPE', 'LOC', 'FAC']
            NER_entry_var.set(', '.join(NER_list))
        elif sel == '--- All temporal expressions':
            NER_list = ['DATE', 'TIME']
            NER_entry_var.set(', '.join(NER_list))
        elif sel == '--- All other expressions':
            NER_list = ['PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']
            NER_entry_var.set(', '.join(NER_list))
    else:
        if 'All NER tags' in sel: # == '--- All NER tags':
            NER_list = NER_list
            NER_entry_var.set('PERSON, ORGANIZATION, MISC, MONEY, NUMBER, ORDINAL, PERCENT, DATE, TIME, DURATION, SET, EMAIL, URL, CITY,STATE_OR_PROVINCE, COUNTRY, LOCATION, NATIONALITY, RELIGION, TITLE, IDEOLOGY, CRIMINAL_CHARGE,CAUSE_OF_DEATH')
        elif sel == '--- All quantitative expressions':
            NER_list = ['NUMBER', 'ORDINAL', 'PERCENT']
            NER_entry_var.set('NUMBER, ORDINAL, PERCENT')
        elif sel == '--- All social actors':
            NER_list = ['PERSON', 'ORGANIZATION']
            NER_entry_var.set('PERSON, ORGANIZATION')
        elif sel == '--- All spatial expressions':
            NER_list = ['CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
            NER_entry_var.set('CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION')
        elif sel == '--- All temporal expressions':
            NER_list = ['DATE', 'TIME', 'DURATION', 'SET']
            NER_entry_var.set('DATE, TIME, DURATION, SET')
        elif sel == '--- All other expressions':
            mb.showwarning(title='Warning', message='You cannot select the option --- All other expressions.\n\nPlease, select a different option and try again.')
            NER_tag_var.set(' ')
            window.focus_force()
            return
    # individual-tag selection (the 'All NER tags' and '--- ...' labels are selectors, not literal tags)
    if sel != ' ' and '---' not in sel and 'All NER tags' not in sel:
        full_default = _full_tag_set(pkg)
        current = {t.strip() for t in NER_entry_var.get().replace(',', ' ').split() if t.strip()}
        if not current or current == full_default:
            # textbox still holds the default (all tags) -> start a fresh subset with this tag
            NER_list = [sel]
            NER_entry_var.set(sel)
        elif sel in current:
            mb.showwarning(title='Warning', message='The NER tag "'+ sel + '" is already in your selection NER list: '+ str(NER_entry_var.get()) + '.\n\nPlease, select another NER tag (or hit the Reset button and try again).')
            window.focus_force()
            return
        else:
            # building a subset: add this tag to the existing selection
            NER_list.append(sel)
            NER_entry_var.set(NER_entry_var.get() + ', ' + sel)
        add_NER_button.configure(state="normal")
        reset_NER_button.configure(state="normal")

NER_tag_var.trace ('w',lambda x,y,z: add_NER_tag(coming_from_add, coming_from_reset))

add_NER_tag(coming_from_add, coming_from_reset)


def get_NER_list(package, language):
    NER_list=[]
    if 'Stanza' in package:
        import constants_util
        for short, long in constants_util.languages:
            if long == language:
                break
        try:
            NER_list = Stanza_util.NER_dict[short]
        except:
            # check that NER is available first
            if Stanza_util.check_Stanza_annotator_availability(['NER'], short, long, silent=False):
                # then check for specific NER tags for the selected language
                import IO_user_interface_util
                IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Warning',
                                                   'There are no ad-hoc NER tags for the ' + language + ' language in Stanza.\n\nPlease, check NER output for ' + language + '-specific NER tags.')
    return NER_list

# get the NLP package and language options
error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
language_var = language
language_list = [language]

def activate_NER_Options(coming_from_add, coming_from_reset):
    add_NER_button.configure(state="disabled")
    reset_NER_button.configure(state='disabled')
    NER_menu.configure(state='disabled')
    if 'BERT' in NER_packages_var.get():
        set_NER_menu_options(NER_tags_BERT)
        NER_menu.configure(state='normal')
        reset_NER_button.configure(state='normal')
        if coming_from_reset:
            NER_tag_var.set(' ')
        elif not coming_from_add:
            NER_tag_var.set('All NER tags')
    elif 'CoreNLP' in NER_packages_var.get():
        set_NER_menu_options(NER_tags_CoreNLP)
        NER_menu.configure(state='normal')
        reset_NER_button.configure(state='normal')
        if coming_from_reset:
            NER_tag_var.set(' ')
        else:
            if not coming_from_add:
                NER_tag_var.set('All NER tags')  # --- All NER tags
    elif 'spaCy' in NER_packages_var.get():
        set_NER_menu_options(NER_tags_OntoNotes)
        NER_menu.configure(state='normal')
        reset_NER_button.configure(state='normal')
        NER_list = spaCy_util.NER_dict
        NER_entry_var.set(NER_list)
        if coming_from_reset:
            NER_tag_var.set(' ')
        elif not coming_from_add:
            NER_tag_var.set('All NER tags')
    elif 'Stanza' in NER_packages_var.get():
        set_NER_menu_options(NER_tags_OntoNotes)
        NER_menu.configure(state='normal')
        reset_NER_button.configure(state='normal')
        NER_list = get_NER_list('Stanza',language)
        NER_entry_var.set(NER_list)
        if coming_from_reset:
            NER_tag_var.set(' ')
        elif not coming_from_add:
            NER_tag_var.set('All NER tags')
    else:
        NER_list=[]
        NER_entry_var.set(NER_list)
        if 'IBM' in NER_packages_var.get():
            mb.showwarning("Option not available",
                           "The selected " + NER_packages_var.get() + " option is not available yet.\n\nSorry! Please, check back soon...")
NER_packages_var.trace('w',lambda x,y,z: activate_NER_Options(coming_from_add, coming_from_reset))

# activate_NER_Options(coming_from_add, coming_from_reset)

def clear_NER_list(coming_from_add, coming_from_reset):
    if coming_from_reset: # and NER_packages_var.get()=='Stanford CoreNLP':
        NER_list.clear()
        NER_entry_var.set(' ')
        NER_entry=''
        NER_tag_var.set(' ')

activate_NER_Options(coming_from_add, coming_from_reset)

videos_lookup = {'NER extractor':'https://www.youtube.com/watch?v=QyvzjYp5D6s'}
videos_options='NER extractor'

TIPS_lookup = {'Stanford CoreNLP supported languages':'TIPS_NLP_Stanford CoreNLP supported languages.pdf',
               'Stanford CoreNLP performance & accuracy':'TIPS_NLP_Stanford CoreNLP performance and accuracy.pdf',
               'Stanford CoreNLP memory issues': 'TIPS_NLP_Stanford CoreNLP memory issues.pdf',
               'CoreNLP NER (Named Entity Recognition)':'TIPS_NLP_NER tags across packages.pdf',
               'NER tags across packages':'TIPS_NLP_NER tags across packages.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='CoreNLP NER (Named Entity Recognition)','NER tags across packages','csv files - Problems & solutions','Statistical measures','Stanford CoreNLP supported languages','Stanford CoreNLP performance & accuracy','Stanford CoreNLP memory issues'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_txtFile)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, click on the 'Pre-processing tools' button to open the GUI where you will be able to perform a variety of\n   file checking options (e.g., utf-8 encoding compliance of your corpus or sentence length);\n   file cleaning options (e.g., convert non-ASCII apostrophes & quotes and % to percent).\n\nNon utf-8 compliant texts are likely to lead to code breakdown in various algorithms.\n\nASCII apostrophes & quotes (the slanted punctuation symbols of Microsoft Word), will not break any code but they will display in a csv document as weird characters.\n\n% signs will lead to code breakdon of Stanford CoreNLP.\n\nSentences without an end-of-sentence marker (. ! ?) in Stanford CoreNLP will be processed together with the next sentence, potentially leading to very long sentences.\n\nSentences longer than 70 or 100 words may pose problems to Stanford CoreNLP (the average sentence length of modern English is 20 words). Please, read carefully the TIPS_NLP_Stanford CoreNLP memory issues.pdf.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the 23 NER tags that you would like to extract.\n\nFor English, the Stanford CoreNLP, by default through the NERClassifierCombiner annotator, recognizes the following NER values:\n  named (PERSON, LOCATION, ORGANIZATION, MISC);\n  numerical (MONEY, NUMBER, ORDINAL, PERCENT);\n  temporal (DATE, TIME, DURATION, SET).\n  In addition, via regexner, the following entity classes are tagged: EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job) TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH.\n\nClick on the + button to add more NER tags.\nClick on the Reset button (or ESCape) to cancel all selected options and start over."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","All NER annotators handle multi-word expressions (MWE), such as 'Harry Potter' as a single PERSON or 'United States of America' as a single COUNTRY/GPE.\n\nThe NER tags dropdown adapts to the package selected above, each using its own tag scheme:\n   - Stanford CoreNLP: its own fine-grained scheme (CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION, CAUSE_OF_DEATH, CRIMINAL_CHARGE, ...);\n   - spaCy, Stanza and BERT: the OntoNotes scheme (PERSON, NORP, ORG, GPE, LOC, FAC, DATE, TIME, MONEY, QUANTITY, ...).\n\nSelect 'All NER tags' to extract every tag, or pick a category (e.g. 'All spatial expressions') or an individual tag to extract only those. Your selection filters the output for all packages.\n\nPress the ESCape button to clear any previously selected options and start fresh."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox to run the NER Entity Timeline tool.\n\nThis tool uses Stanza NER to extract named entities (PERSON, GPE, LOC, ORG, etc.) and track WHEN they appear across the narrative.\n\nThe tool produces:\n   - Entity timeline CSV with every mention, its sentence, and narrative position (0 = beginning, 1 = end)\n   - Frequency bar chart of the top 20 entities across all types\n   - Per-type scatter timelines showing when each PERSON, GPE, ORG, or LOC appears\n   - Entity presence heatmap showing the density of mentions across 10 narrative segments\n   - Per-document entity counts (when processing multiple documents)\n\nThis tool runs independently of the NER package selected above — it always uses Stanza.\n\nNOTE: The heatmap divides the text into 10 narrative-position bins (0-10%, 10-20%, ... 90-100%). With very short texts (e.g., a single sentence like 'Berkeley went to New York with her friend Maria'), all entities will cluster in one bin, producing a single dark column. This is expected — the heatmap is designed for longer documents where entity mentions spread across the narrative arc."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script will extract NER tags from either tetxt file(s) using different packages for NER  annotation: BERT, spaCy, Stanford CoreNLP, Stanza.\n\nIn INPUT the algorith expects a single txt file or a set of txt files in a directory.\n\nIn OUTPUT the algorithm exports a csv file of extracted NER values and several bar charts (if the checkbox 'Create chart(s)' is not ticked off)."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

# reminders are based on the script name
# reminders_util.checkReminder(scriptName, reminders_util.NER_frequencies,
#                              reminders_util.message_NER_frequencies, True)

GUI_util.window.mainloop()

