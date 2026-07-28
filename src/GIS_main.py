# Written by Roberto Franzosi May, September 2020
# Written by Roberto Franzosi September 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS",['os','tkinter','pandas','subprocess'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
from subprocess import call
import pandas as pd
# Ignore error coming from df['Date'][index] = saved_date
pd.options.mode.chained_assignment = None

import tkinter as tk
from tkinter import ttk

import GUI_IO_util
import config_util # used for Google API
import reminders_util
import constants_util
import IO_csv_util
import GIS_pipeline_util
import GIS_file_check_util
import IO_files_util
import CoNLL_util
import Stanford_CoreNLP_util
import run_script_util
import Stanza_util
import spaCy_util
import BERT_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run():
    # widget values read here at RUN time (was: run_script_command lambda + run() params)
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    csv_file = csv_file_var.get()
    NER_extractor = NER_extractor_var.get()
    NER_package = NER_package_var.get()
    location_menu = location_menu_var.get()
    geocoder = geocoder_var.get()
    geocode_locations = geocode_locations_var.get()
    country_bias_var = globals()['country_bias_var'].get()
    area_var = globals()['area_var'].get()
    restrict_var = globals()['restrict_var'].get()
    map_locations = map_locations_var.get()
    GIS_package_var = globals()['GIS_package_var'].get()
    Google_Earth_OpenGUI = globals()['Google_Earth_OpenGUI'].get()
    map_characters = map_characters_var.get()

    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []
    locationColumnName=''

    # get the NLP package and language options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, export_json_var, memory_var, document_length_var, limit_sentence_length_var = config_util.read_NLP_package_language_config()
    language_var = language
    language_list = [language]
    if package_display_area_value == '':
        mb.showwarning(title='No setup for NLP package and language',
                       message="The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again.")
        return

    # get the date options from filename
    filename_embeds_date_var, date_format_var, items_separator_var, date_position_var, config_file_exists = config_util.get_date_options(
        config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    # get last two characters for ISO country code
    country_bias = country_bias_var[-2:]

    box_tuple=''
    if not 'e.g.,' in area_var:
        if (area_var.count('(') + area_var.count(')') != 4) or (area_var.count(',') != 3):
            mb.showwarning("Warning",
                           "The area variable is not set correctly. The expected value should be something like this: (34.98527, -85.59790), (30.770444, -81.521974)\n\nThe two sets of values refer to the upper left-hand and lower right-hand corner latitude and longitude coordinates of the area to wich you wish to restrict geocoding.\n\nPlease, enter the correct value and try again.")
            area_var.set('(34.98527, -85.59790), (30.770444, -81.521974)')
            return
        box_tuple=area_var

    # Save GIS settings to the input directory so other GUIs (analyzer, SQL)
    # can pick them up automatically when geocoding from that database.
    _save_dir = inputDir if inputDir else (os.path.dirname(inputFilename) if inputFilename else '')
    if _save_dir and os.path.isdir(_save_dir):
        GIS_pipeline_util.save_GIS_settings(
            _save_dir,
            country_bias=country_bias_var,
            area=area_var if 'e.g.,' not in area_var else '',
            restrict=bool(restrict_var))

    # The GIS output subdirectory, made ONCE per run. make_output_subdirectory DELETES the directory if
    # it already exists (shutil.rmtree) and makes it again empty, so the second call for the same label
    # wiped whatever the first option had just written -- the character-movement CSVs were written,
    # destroyed by the GIS options that ran after them, and then handed to Excel to open, which is the
    # "Sorry, we couldn't find ..." box.
    outputDir_GIS = ''

    if map_characters:
        outputDir_mc = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='GIS',
                                                              silent=True)
        outputDir_GIS = outputDir_mc
        if outputDir_mc == '':
            return
        import NER_location_tracking_util
        import charts_util
        trackingFiles = NER_location_tracking_util.main(inputFilename, inputDir, outputDir_mc)
        if trackingFiles:
            csv_files = [f for f in trackingFiles if f.endswith('.csv')]
            if csv_files:
                # ordered by Sentence ID and filterable by document: the checkbox promises movement in
                # TIME and space, and with no sequence column the animation plays in CSV row order,
                # which is a chronology of nothing. The Corpus Profiler always passed these two.
                mapFiles = charts_util.animated_migration_map(
                    csv_files[0], outputDir_mc, 'Entity', 'Location',
                    sequence_col='Sentence ID', doc_col='Document')
                if mapFiles:
                    filesToOpen.extend(mapFiles if isinstance(mapFiles, list) else [mapFiles])
            filesToOpen.extend(trackingFiles)
            if openOutputFiles:
                IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir_mc, scriptName)
        else:
            mb.showwarning("No results", "No person-location pairs were found in the input text.\n\nThe animated character movement map requires text that mentions both people and places.")
        if NER_extractor==False and geocode_locations_var==False and map_locations==False:
            return

    if NER_extractor==False and geocode_locations_var==False and GIS_package_var=='':
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if display_csv_file_options()==True:
         return
    if display_txt_file_options()==True:
         return

    if csv_file!='':
        result = mb.askokcancel("GIS pipeline input file",
                       "This is a reminder that you are running the GIS pipeline with the csv input file\n\n"+csv_file+'\n\nand the GIS package ' + GIS_package_var +'\n\nPress Cancel then Esc to clear the csv file widget if you want to run the GIS pipeline from your input txt file(s) (you can select a different mapping software using the dropdown menu) and try again.',
                       default='ok')  # silent/unattended mode proceeds
        if result == False:
            return
        inputFilename=csv_file

    # geocoder = 'Nominatim'
    geoName = 'geo-' + str(geocoder[:3])
    kmloutputFilename = ''
    # locationColumnName = 'Location'
    # locationColumnName = location_menu_var #.get()
    if geocode_locations_var == True:
        geocodedLocationsoutputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,
                                                                                  outputDir, '.csv', 'GIS',
                                                                                  geoName, locationColumnName, '',
                                                                                  '',
                                                                                  False, True)
        locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir,
                                                                                  outputDir, '.csv', 'GIS',
                                                                                  geoName, 'Not-Found',
                                                                                  locationColumnName, '',
                                                                                  False, True)

        reminders_util.checkReminder(scriptName, reminders_util.title_options_geocoder,
                                     reminders_util.message_geocoder, True)

        locationFiles = []

    # START PROCESSING ---------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # NER extraction via CoreNLP, Stanza, or spaCy

    # create a subdirectory of the output directory -- REUSING the one the character-movement option
    # already made, because making it again deletes it and everything written into it
    if outputDir_GIS:
        outputDir = outputDir_GIS
    else:
        outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='GIS',
                                                           silent=True)
    if outputDir == '':
        return

    # checking for txt: NER=='LOCATION', provide a csv output with column: [Locations]
    if NER_extractor and csv_file=='':

        if 'BERT' in NER_package:
            # --- BERT NER extraction (highest accuracy, slowest) ---
            locationFiles = BERT_util.NER_tags_BERT(GUI_util.window, inputFilename, inputDir,
                                                     outputDir, config_filename, '', chartPackage, dataTransformation)
        elif 'Stanza' in NER_package:
            # --- Stanza NER extraction ---
            locationFiles = Stanza_util.Stanza_annotate(config_filename, inputFilename, inputDir,
                                                        outputDir, openOutputFiles, chartPackage, dataTransformation,
                                                        'NER', False,
                                                        [language_var],
                                                        memory_var, 90000, 1000,
                                                        filename_embeds_date_var=filename_embeds_date_var,
                                                        date_format=date_format_var,
                                                        items_separator_var=items_separator_var,
                                                        date_position_var=date_position_var)
        elif 'spaCy' in NER_package:
            # --- spaCy NER extraction ---
            locationFiles = spaCy_util.spaCy_annotate(config_filename, inputFilename, inputDir,
                                                      outputDir, openOutputFiles, chartPackage, dataTransformation,
                                                      ['NER'], False,
                                                      language_var,
                                                      memory_var, 90000, 1000,
                                                      filename_embeds_date_var=filename_embeds_date_var,
                                                      date_format=date_format_var,
                                                      items_separator_var=items_separator_var,
                                                      date_position_var=date_position_var)
        else:
            # --- Stanford CoreNLP NER extraction (default) ---
            NERs = ['COUNTRY', 'STATE_OR_PROVINCE', 'CITY', 'LOCATION']
            locationFiles = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                    outputDir, openOutputFiles, chartPackage, dataTransformation,
                                                                    'NER', False,
                                                                    language_var,
                                                                    export_json_var,
                                                                    memory_var,
                                                                    NERs=NERs,
                                                                    extract_date_from_text_var=0,
                                                                    filename_embeds_date_var=filename_embeds_date_var,
                                                                    date_format=date_format_var,
                                                                    items_separator_var=items_separator_var,
                                                                    date_position_var=date_position_var)

        if locationFiles is None or len(locationFiles)==0:
            mb.showwarning("No locations","There are no NER locations to be geocoded and mapped in the selected input txt file.\n\nPlease, select a different txt file and try again.")
            return
        else:
            filesToOpen.extend(locationFiles)
            NER_outputFilename = locationFiles[0]

        # Normalize the raw NER csv in place via the shared helper: Form/Word -> Location,
        # scheme-aware NER tags (GPE/LOC), multi-word-entity merge, AND Date extracted from each
        # filename (so the maps get a time slider). Same logic the NER->map prompt uses.
        prepared = GIS_pipeline_util.normalize_NER_csv_for_GIS(
            NER_outputFilename, NER_outputFilename,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var, items_separator=items_separator_var,
            date_position=date_position_var)
        if prepared == '':
            mb.showwarning("No locations","There are no NER locations to be geocoded and mapped in the selected input txt file.\n\nPlease, select a different txt file and try again.")
            return
        location_menu_var.set('Location')
        csv_file_var.set(NER_outputFilename)
        filesToOpen.append(NER_outputFilename)
        locationColumnName = 'Location'
        check_csv_file_headers(NER_outputFilename)

    else:
        NER_outputFilename=csv_file_var.get()
        locationColumnName = location_menu #RF

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # running the GIS options
    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    if 'Proportional' in GIS_package_var:
        import charts_util
        outputfilename = charts_util.proportional_circle_map(
            NER_outputFilename, outputDir, locationColumnName)
        if outputfilename:
            filesToOpen.append(outputfilename)
        if len(filesToOpen) > 0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

    elif 'folium' in GIS_package_var or 'Google' in GIS_package_var:
        # if GIS_package_var=='Google Earth Pro': # check installation
            # locationColumnName where locations to be geocoded (or geocoded) are stored in the csv file;
        #   any changes to the columns will result in error
        # outputFiles includes both kml file and Google Earth files
        outputFiles = GIS_pipeline_util.GIS_pipeline(GUI_util.window, config_filename,
                        NER_outputFilename, inputDir, outputDir, geocoder,
                        GIS_package_var, chartPackage, dataTransformation,
                        extract_date_from_text_var,
                        country_bias,
                        box_tuple,
                        restrict_var,
                        locationColumnName,
                        encoding_var,
                        0, 1, [''], [''],# group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                        ['Pushpins'], ['red'], # icon_var_list, specific_icon_var_list,
                        [0], ['1'], [0], [''], # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                        [1],[1]) # bold_var_list, italic_var_list)

        if outputFiles!=None:
            if len(outputFiles)>0:
                filesToOpen.extend(outputFiles)
                csv_file_var.set(outputFiles[1])
                NER_extractor_var.set(0)
                NER_extractor_checkbox.config(state='disabled')
                geocode_locations_var.set(0)

        if len(filesToOpen)>0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)
    else:
        if GIS_package_var!='':
            mb.showwarning("Option not available","The " + GIS_package_var + " option is not available yet.\n\nSorry! Please, check back soon...")
            return

    if Google_Earth_OpenGUI:
        run_script_util.run_script("GIS_Google_Earth_main.py")
        return

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=560, # height at brief display
                                                 GUI_height_full=640, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=2, # to be added for full display
                                                 increment=2)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for GIS (Geographic Information System) Pipeline from Text to Map'
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
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

csv_file_var= tk.StringVar()

location_menu_var=tk.StringVar()
NER_extractor_var=tk.IntVar()
geocode_locations_var=tk.IntVar()
geocoder_var=tk.StringVar()
country_bias_var=tk.StringVar()
area_var=tk.StringVar()
restrict_var=tk.IntVar()
GIS_package_var=tk.StringVar()
Google_Earth_OpenGUI=tk.IntVar()
map_locations_var=tk.IntVar()
open_API_config_var=tk.StringVar()

inputIsGeocoded = False

def clear(e):
    csv_file_var.set('')
    NER_extractor_var.set(1)
    NER_extractor_checkbox.config(state='disabled')
    NER_package_var.set('Stanza')
    location_menu_var.set('')
    geocode_locations_var.set(1)
    geocode_locations_checkbox.configure(state='normal')
    map_locations_var.set(1)
    # GIS_package_var.set('Google Earth Pro & Google Maps')
    GIS_package_var.set('Python folium pin map & heatmap')
    geocoder_var.set('Nominatim')
    country_bias_var.set('')
    area_var.set('e.g., (34.98527, -85.59790), (30.770444, -81.521974)')
    map_characters_var.set(0)
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)


def check_csv_file_headers(csv_file):
    cannotRun=False
    NER_extractor=False
    geocode_locations=False
    location_menu=''
    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(
        csv_file_var.get())
    if inputIsCoNLL:
        reminders_util.checkReminder(scriptName, reminders_util.title_options_Google_Earth_CoNLL,
                                     reminders_util.message_Google_Earth_CoNLL, True)

        reminders_util.checkReminder(scriptName, reminders_util.title_options_input_csv_file,
                                     reminders_util.message_input_csv_file, True)
        location_menu_var.set('NER')
        location_menu='NER'
        geocoder_var.set('Nominatim')
        geocoder = 'Nominatim'
        location_field.config(state='disabled')
    if ('Location' in headers and not 'Latitude' in headers) or "Word" in headers:
        geocode_locations_var.set(1)
        geocode_locations_checkbox.configure(state='disabled')
        if "Word" in headers:
            location_menu_var.set('Word') #RF
            location_menu='Word' #RF
        else:
            geocoder_var.set('Nominatim')
            location_menu_var.set('Location') #RF
            location_menu='Location' #RF
    elif 'Latitude' in headers and 'Longitude' in headers:
        NER_extractor_var.set(0)
        NER_extractor_checkbox.config(state='disabled')
        geocode_locations_var.set(0)
        geocode_locations_checkbox.configure(state='disabled')
        geocode_locations=False
        location_menu_var.set('Location') #RF
        location_menu='Latitude'
    # Word is the header from Stanford CoreNLP NER annotator
    elif not 'Location' in headers and not 'Word' in headers and not 'NER' in headers:
        mb.showwarning(title='Warning',
                       message="The selected input csv file does not contain the word 'Location' in its headers.\n\nThe GIS algorithms expect in input either\n   1. txt file(s) from which to extract locations (via Stanford CoreNLP NER annotator) to be geocoded and mapped;\n   2. a csv file\n      a. with a column of locations (with header 'Location') to be geocoded and mapped;\n      b. a csv file with a column of locations (with header 'Location'; the header 'Word' from the CoreNLP NER annotator will be converted automatically to 'Location')';\n      c. already geocoded and to be mapped (this file will also contain latitudes and longitudes, with headers 'Latitude' and 'Longitude').\n\nPlease, select the appropriate input csv file and try again. Or simply run the complete pipeline, going from text to maps, with txt file(s) in input.")
        geocoder_var.set('Nominatim')
        csv_file_var.set('')
        NER_extractor_var.set(1)
        NER_extractor = True
        NER_extractor_checkbox.config(state='disabled')
        # cannotRun = True
        # return cannotRun
    else: # no location or lat long
        geocoder_var.set('Nominatim')
        geocode_locations_var.set(1)
        geocode_locations=True
        NER_extractor_checkbox.config(state='disabled')
        NER_extractor_var.set(1)
        NER_extractor = True

    if inputIsGeocoded:
        geocode_locations_var.set(0)
        geocode_locations_checkbox.configure(state='disabled')
        geocode_locations=0
        geocode_locations_checkbox.config(state='disabled')
    else:
        if location_menu_var.get()=='':
            mb.showwarning(title='Warning',
                           message="You have selected the 'GEOCODE locations' option, but you have not selected the column containing location names.\n\nYou cannot geocode without selecting the column containing locations to be coded.")
            cannotRun=True
        elif geocoder_var.get() == '':
            mb.showwarning(title='Warning', message='No geocoder service option selected.\n\nThe GIS script will exit.')
            cannotRun=True
        elif geocode_locations_var.get() == False:
            if map_locations_var.get() == True:
                mb.showwarning(title='Warning',
                               message="You have selected the 'MAP locations' option, but the current csv input file is not geocoded and the 'GEOCODE location' widget is unchecked.\n\nYou cannot map without geocoding.")
                # geocode_locations_var.set(1)
                # geocode_locations_checkbox.configure(state='disabled')
                cannotRun=True

    if map_locations_var.get()==False and inputIsGeocoded==True:
        mb.showwarning(title='Warning',
                       message="The 'MAP locations' checkbox is ticked off with a csv file of geocoded locations in input.\n\nThere is nothing to do for the GIS pipeline...")
        cannotRun = True

    return cannotRun, NER_extractor, geocode_locations, location_menu

def display_csv_file_options():
    cannotRun = False
    if csv_file_var.get() == '':
        return cannotRun
    menu_values = IO_csv_util.get_csvfile_headers(csv_file_var.get())
    # must change all 3 widgets where menus must be updated after changing the filename
    m = location_field["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: location_menu_var.set(value))
    # if Google_Earth_OpenGUI.get() == False:
    #     # GIS_package_var.set('Google Earth Pro & Google Maps')
    #     GIS_package_var.set('Python folium pin map & heatmap')
    # the csv_file Entry widget is created once at GUI setup and auto-updates via csv_file_var;
    # do NOT re-create it here (the old line crashed unpacking an Entry into 3 names).
    # check_csv_file_headers returns 4 values; capture all of them.
    cannotRun, NER_extractor, geocode_locations, location_menu = check_csv_file_headers(csv_file_var.get())

    return cannotRun

def _is_geocoded_csv(path):
    """True if the csv has Latitude AND Longitude columns (a geocoded GIS file)."""
    try:
        hdrs = set(h.strip().lower() for h in IO_csv_util.get_csvfile_headers(path))
        return 'latitude' in hdrs and 'longitude' in hdrs
    except Exception:
        return False


def find_geocoded_csv(outputDir, inputFilename='', inputDir=''):
    """Newest-first list of geocoded GIS csv files (Latitude/Longitude) for the current corpus. Only csvs whose
    path mentions 'gis'/'geocod' are header-validated, to stay fast on large trees. Thin wrapper over the shared
    CoNLL_util.find_corpus_csv discovery (no stem-narrowing: a geocoded file may not carry the corpus name)."""
    return CoNLL_util.find_corpus_csv(outputDir, inputFilename, inputDir,
                path_filter=lambda p: 'gis' in p.lower() or 'geocod' in p.lower(),
                validator=_is_geocoded_csv, narrow_by_stem=False)


def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    # First offer the geocoded csv files discovered in the output (incl. GIS subfolders under SVO); only fall
    # back to a file dialog if none are found or the user chooses to browse.
    chosen = IO_files_util.select_path_from_list(window,
                 find_geocoded_csv(GUI_util.output_dir_path.get(), GUI_util.inputFilename.get(), GUI_util.input_main_dir_path.get()),
                 'Select a geocoded csv file (with Latitude/Longitude) found in your output, or browse for another file:',
                 title='Available geocoded csv files')
    if chosen is None:
        return ''
    if chosen != '__BROWSE__':
        filePath = chosen
    else:
        if csv_file!='':
            initialFolder=os.path.dirname(os.path.abspath(csv_file_var.get()))
        else:
            initialFolder = os.path.dirname(os.path.abspath(__file__))
        filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        nRecords, nColumns =IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(filePath, 'utf-8')
        if nRecords==0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath=''
        else:
            csv_file_var.set(filePath)
            display_csv_file_options()
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv file', [("dictionary files", "*.csv")],True))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

#setup a button to open Windows Explorer on the selected input directory
openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,openInputFile_button,
                    True, False, True,False, 90, GUI_IO_util.IO_configuration_menu, "Open INPUT csv dictionary file")

csv_file=tk.Entry(window, width=GUI_IO_util.csv_file_width,textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,csv_file)

map_characters_var = tk.IntVar()
map_characters_checkbox = tk.Checkbutton(window, variable=map_characters_var, onvalue=1, offvalue=0)
map_characters_checkbox.config(text="MAP characters moving in time and geocodable space")
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                    map_characters_checkbox, True,
                    x_coordinate_hover_over=GUI_IO_util.labels_x_coordinate,
                    text_info="Here 'space' means GEOGRAPHIC, geocodable space - real places that resolve to map "
                              "coordinates (cities, counties, countries).\n\nFor SYMBOLIC / SOCIAL space that has "
                              "NO map coordinates (e.g. house vs. field), or how a social attribute (gender, race, "
                              "class) maps onto types of space, use the 'Symbolic / non-geocodable space' GUI - "
                              "opened with the button to the right.")

# same row: shortcut to the non-geocodable sibling (this GUI has no 'GUIs available' dropdown).
# NOTE (layout): x=560 is chosen to clear the long checkbox label; verify/nudge if it overlaps.
open_symbolic_button = tk.Button(window, text='Open Symbolic (non-geocodable) Space GUI',
                                 command=lambda: run_script_util.run_script("GIS_symbolic_main.py"))
y_multiplier_integer = GUI_IO_util.placeWidget(window, 560, y_multiplier_integer, open_symbolic_button, False,
                    x_coordinate_hover_over=560,
                    text_info="Open the Symbolic / non-geocodable Space GUI - the companion to this tool for kinds "
                              "of place that carry social meaning but have NO map coordinates (house, field, "
                              "threshold, woods), and how gender / race / class map onto them.")

NER_extractor_var.set(0)
NER_package_var = tk.StringVar()
NER_package_var.set('Stanza')

NER_extractor_checkbox = tk.Checkbutton(window, variable=NER_extractor_var, onvalue=1, offvalue=0)
NER_extractor_checkbox.config(text="EXTRACT locations (via NER)")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,NER_extractor_checkbox, True)

NER_package_menu = tk.OptionMenu(window, NER_package_var, 'BERT', 'Stanza', 'spaCy', 'Stanford CoreNLP')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                NER_package_menu,
                                False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                                "Select the NLP package for NER location extraction.\n\n"
                                "BERT: highest accuracy (~92% F1), uses XLM-RoBERTa transformer; slowest but best for small corpora.\n"
                                "Stanza (recommended): modern BiLSTM-CRF neural network (~89% F1), 30+ languages, good speed/accuracy tradeoff.\n"
                                "spaCy: fast (~86-90% F1), 20+ languages.\n"
                                "Stanford CoreNLP: fine-grained location types (CITY, STATE, COUNTRY), English-focused, requires Java.")

if os.path.isfile(inputFilename.get()):
    menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())
else:
    menu_values = ' '

location_field_lb = tk.Label(window, text='Select the column containing location names')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,location_field_lb,True)
if menu_values!=' ':
    location_field = tk.OptionMenu(window, location_menu_var,*menu_values)
else:
    location_field = tk.OptionMenu(window, location_menu_var,menu_values)

y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,location_field)

geocode_locations_var.set(0)
geocode_locations_checkbox = tk.Checkbutton(window, variable=geocode_locations_var, onvalue=1, offvalue=0)
geocode_locations_checkbox.config(text="GEOCODE locations")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,geocode_locations_checkbox, True)


geocoder_lb = tk.Label(window, text='Geocoder')

y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.label_columns,y_multiplier_integer,geocoder_lb,True)
geocoder_var.set('Nominatim')
geocoder = tk.OptionMenu(window,geocoder_var,'Nominatim','Google')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                    geocoder, False, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate, "Select the geocoder to be used: Nominatim or Google.\nNominatim is less accurate than Google, but Google requires an API key (please, read the TIPS file on how to obtain a free Google API key).")

# https://developers.google.com/maps/documentation/embed/get-api-key
# Google_API_geocode_lb = tk.Label(window, text='API key')
# Google_API_geocode = tk.Entry(window, width=40, textvariable=Google_API_Google_geocode_var)

# save_APIkey_button_Google_geocode = tk.Button(window, text='OK', width=2,height=1,command=lambda: config_util.Google_API_Config_Save('Google-geocode-API_config.csv',Google_API_Google_geocode_var.get()))

def activate_Google_API_geocode(*args):
    if geocoder_var.get()=='Google':
        key = GIS_pipeline_util.getGoogleAPIkey(window, 'Google-geocode-API_config.csv')
        if key=='' or key==None:
            geocoder_var.set('Nominatim')
            geocoder='Nominatim'
        area.configure(state='disabled')
        restrict_checkbox.configure(state='disabled')
    else:
        area.configure(state='normal')
        restrict_checkbox.configure(state='normal')
geocoder_var.trace('w',activate_Google_API_geocode)

# split lines

country_bias_lb = tk.Label(window, text='Country bias')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.label_columns,y_multiplier_integer,country_bias_lb,True)

country_menu = constants_util.ISO_GIS_country_menu

country_bias_var.set('')
country_bias = ttk.Combobox(window, width = GUI_IO_util.country_bias_width, textvariable = country_bias_var)
country_bias['values'] = country_menu
country_bias.configure(state='disabled')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                    country_bias, True, False, True, False,
                    90, GUI_IO_util.labels_x_coordinate, "Select a country to privilege geocoding locations in that country when similar locations are found in other countries (e.g., Rome, Georgia, US, and Rome, Italy)")

area_lb = tk.Label(window, text='Area')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate,y_multiplier_integer,area_lb,True)

area_var.set('e.g., (34.98527, -85.59790), (30.770444, -81.521974)')
area=tk.Entry(window, width=GUI_IO_util.area_width,textvariable=area_var)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.area_pos, y_multiplier_integer,
                    area, True, False, True,False, 90,
                    GUI_IO_util.labels_x_coordinate,
                    "For Nominatim, you can enter the latitude and longiture of upper left-hand corner and lower right-hand corner of a rectangular area to privilege locations in that area (e.g., Rome, Georgia, vs. Rome, New York)")

restrict_var.set(0)
restrict_checkbox = tk.Checkbutton(window, text="Restrict", variable=restrict_var, onvalue=1, offvalue=0)
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.restrict_pos, y_multiplier_integer,
                    restrict_checkbox, False, False, True,False, 90,
                    GUI_IO_util.open_TIPS_x_coordinate,
                    "For Nominatim, after entering area latitude and longitude, you can restrict locations to that specific area or leave it open for Nominatim to decide")

map_locations_var.set(0)
map_locations_checkbox = tk.Checkbutton(window, variable=map_locations_var, onvalue=1, offvalue=0)
map_locations_checkbox.config(text="MAP locations")
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,map_locations_checkbox,True)

def display_txt_file_options(*args):
    global inputIsGeocoded
    cannotRun = False
    if csv_file_var.get() == '':
        if inputFilename.get()!='' or input_main_dir_path.get()!='':
            if geocode_locations_var.get()==False and map_locations_var.get()==True:
                mb.showwarning(title='Warning',
                               message="The 'GEOCODE locations' checkbox is ticked off but you have the 'MAP locations' checkbox ticked.\n\nYou cannot map without geocoding.")
                cannotRun = True
            else:
                location_menu_var.set('')
                location_field.config(state='disabled')
                NER_extractor_var.set(1)
                NER_extractor = True
                NER_extractor_checkbox.configure(state='disabled')
                country_bias.configure(state='normal')
                if inputIsGeocoded:
                    geocode_locations_var.set(0)
                    geocode_locations = False
                else:
                    geocode_locations_var.set(1)
                    geocode_locations = True
                map_locations_var.set(1)
                map_locations = True
        else:
            location_menu_var.set('')
            location_field.config(state='disabled')
    else:
        display_csv_file_options()
    return cannotRun
inputFilename.trace('w',display_txt_file_options)
input_main_dir_path.trace('w',display_txt_file_options)
display_txt_file_options()

def activate_geocoder(*args):
    if geocode_locations_var.get()==True:
        geocoder.configure(state='normal')
    else:
        geocoder_var.set('')
        geocoder.configure(state='disabled')

    if geocode_locations_var.get()==0:
        if display_csv_file_options()==True:
            return
        if display_txt_file_options()==True:
            return
geocode_locations_var.trace('w',activate_geocoder)

def call_reminders(*args):
    if map_locations_var.get()==True:
        if GIS_package_var.get()=='':
            # GIS_package_var.set('Google Earth Pro & Google Maps')
            GIS_package_var.set('Python folium pin map & heatmap')
    else:
        GIS_package_var.set('')
    if display_csv_file_options():
        return
map_locations_var.trace('w',call_reminders)

GIS_package_lb = tk.Label(window, text='Software')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.label_columns,y_multiplier_integer,GIS_package_lb,True)

GIS_package_var.set('Python folium pin map & heatmap')
GIS_package = tk.OptionMenu(window,GIS_package_var,'Python folium pin map & heatmap','Proportional circle map','Google Earth Pro & Google Maps','Google Earth Pro','Google Maps','QGIS','Tableau','TimeMapper')
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,
                    GIS_package, True, False, True, False,
                    90, GUI_IO_util.watch_videos_x_coordinate, "The visualization of GIS maps is set by default on Python folium pin map & heatmap.\nGoogle maps do have some advantages but... Google requires setting up a free API key. And you may wish not to that, regarless of advantages.")
# y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer,GIS_package,True)

Google_Earth_OpenGUI.set(0)
GIS_package2_checkbox = tk.Checkbutton(window, variable=Google_Earth_OpenGUI, onvalue=1, offvalue=0)
GIS_package2_checkbox.config(text="Google Earth Pro - Open GUI")

# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_setup_x_coordinate, y_multiplier_integer,
                    GIS_package2_checkbox, False, False, True, False,
                    90, GUI_IO_util.open_reminders_x_coordinate, "Open the GIS_Google_Earth_main GUI.\nGUI opened automatically after running the NER location extractor (and geocoder).\nAfter the GUI opens, you will need to select as input the csv file produced by either the NER location extractor or the geocoder.")



# map_characters_help_button = tk.Button(window, text='? HELP', width=5,
#     command=lambda: mb.showinfo("Map character movement",
#         "This option extracts person entities and locations from your text files using Stanza NER, "
#         "then produces an animated map showing how characters move across locations over the course of the narrative.\n\n"
#         "The map shows dashed lines connecting successive locations for each person, with a timeline slider "
#         "when dates or document sequence are available.\n\n"
#         "REQUIREMENT: Text file(s) in input (not a csv file).\n\n"
#         "The option uses the same NER extraction as the GIS pipeline but focuses on PERSON entities "
#         "and their co-occurring locations rather than geocoding all location mentions."))
# y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.open_TIPS_x_coordinate, y_multiplier_integer,
#                     map_characters_help_button, False)

open_API_config_lb = tk.Label(window, text='View Google API key')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,open_API_config_lb,True)

open_API_config_var.set('Google Maps')
API = tk.OptionMenu(window,open_API_config_var,'Google Maps','Google geocoding')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.label_columns, y_multiplier_integer,API, True)

open_API_config_button=tk.Button()
if 'Maps' in open_API_config_var.get():
    config_file = 'Google-Maps-API_config.csv'
else:
    config_file = 'Google-geocode-API_config.csv'
open_API_config_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width,
                                     text='',
                                     command=lambda:GIS_pipeline_util.getGoogleAPIkey(window,  config_file,True))
# place widget with hover-over info
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.open_reminders_x_coordinate, y_multiplier_integer,
                    open_API_config_button, False, False, True, False,
                    90, GUI_IO_util.open_reminders_x_coordinate, "Open csv file for Google API key")


# https://developers.google.com/maps/documentation/embed/get-api-key
# Google_API_Google_maps_lb = tk.Label(window, text='API key')
# Google_API_Google_maps = tk.Entry(window, width=40, textvariable=Google_API_Google_maps_var)

def activate_Google_API_Google_Maps(*args):
    global GIS_package2_checkbox
    if not 'folium' in GIS_package_var.get() and not 'Google' in GIS_package_var.get() and len(GIS_package_var.get())>0:
        # QGIS is not unavailable, it is simply not AUTOMATED: the Suite geocodes and writes the kml, and
        # the user maps it in QGIS. Telling them it is 'not available yet' hid a workflow that works and
        # that the 24 QGIS TIPS in the dropdown below document step by step.
        if 'QGIS' in GIS_package_var.get():
            GIS_package_var.set('')
            mb.showinfo(title='Mapping in QGIS',
                        message="The NLP Suite does not drive QGIS directly; it prepares the map data and you "
                        "open it in QGIS.\n\nPlease, select any of the Google or folium options to geocode "
                        "your locations and write the kml file, then import that file into QGIS.\n\nThe TIPS "
                        "dropdown at the bottom of this GUI carries 24 QGIS documents covering the whole "
                        "process: importing the kml, dot, heat, feature and frequency maps, styling points "
                        "and attributes, and what to do about the common QGIS errors.")
        else:
            GIS_package_var.set('')
            mb.showwarning(title='Warning',
                           message="The selected software option is not available yet. Sorry!\n\nSelect any of the Google options and try again.")
        return
    if 'Maps' in GIS_package_var.get():
        key = GIS_pipeline_util.getGoogleAPIkey(window,'Google-Maps-API_config.csv')
        if key == '' or key == None:
            GIS_package_var.set('Google Earth Pro')
GIS_package_var.trace('w',activate_Google_API_Google_Maps)

def display_reminder(*args):
    if Google_Earth_OpenGUI.get():
        routine_options = reminders_util.getReminders_list(scriptName)
        reminders_util.checkReminder(scriptName,
                                     reminders_util.title_options_Google_Earth,
                                     reminders_util.message_Google_Earth,
                                     True)
        routine_options = reminders_util.getReminders_list(scriptName)
        return
Google_Earth_OpenGUI.trace('w', display_reminder)

videos_lookup = {'GIS: From texts to maps':'https://www.youtube.com/watch?v=kIgXoxa6Az0'}
videos_options='GIS: From texts to maps'

TIPS_lookup = {'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               'csv files - Problems & solutions':'TIPS_NLP_csv files - Problems & solutions.pdf',
               'Statistical measures':'TIPS_NLP_Statistical measures.pdf',
               'GIS (Geographic Information System): Mapping Locations':'TIPS_NLP_GIS (Geographic Information System).pdf',
               'Characters moving in time and space':'TIPS_NLP_Characters moving in time and space.pdf',
               'Symbolic (non-geocodable) space':'TIPS_NLP_GIS Narrative non-geocodable symbolic space.pdf',
               'Extracting locations: NER (Named Entity Recognition)':'TIPS_NLP_NER tags across packages.pdf',
               'Geocoding: How to Improve Nominatim':'TIPS_NLP_GIS_Geocoding Nominatim.pdf',
               "Geocoding":"TIPS_NLP_GIS_Geocoding.pdf",
               "Google Earth Pro":"TIPS_NLP_GIS_Google Earth Pro.pdf",
               "Google API Key":"TIPS_NLP_GIS_Google API Key.pdf",
               "HTML":"TIPS_NLP_GIS_Google Earth Pro HTML.pdf",
               "Google Earth Pro Icon":"TIPS_NLP_GIS_Google Earth Pro Icon.pdf",
               "Google Earth Pro Description":"TIPS_NLP_GIS_Google Earth Pro Description.pdf",
               "Google Earth Pro From KML to Excel":"TIPS_NLP_GIS_Google Earth Pro From KML to Excel.pdf",
               # QGIS is not driven by the Suite: it writes the kml, the user maps it in QGIS by hand.
               # These 24 documents describe that manual work and had no entry, so nothing could open them.
               'QGIS: Getting started KML (PC-ACE) files coordinate systems and QGIS project files':'TIPS_NLP_QGIS Getting started KML (PC-ACE) files coordinate systems and QGIS project files.pdf',
               'QGIS: Import a KML file in QGIS':'TIPS_NLP_QGIS Import a KML file in QGIS.pdf',
               'QGIS: Import data from Excel in QGIS':'TIPS_NLP_QGIS Import data from Excel in QGIS.pdf',
               'QGIS: Import more attributes than NAME and DESCRIPTION':'TIPS_NLP_QGIS Import more attributes than NAME and DESCRIPTION.pdf',
               'QGIS: Join data (mapping multiple variables)':'TIPS_NLP_QGIS Join data (mapping multiple variables).pdf',
               'QGIS: Dot map':'TIPS_NLP_QGIS Dot map.pdf',
               'QGIS: Feature map':'TIPS_NLP_QGIS Feature map.pdf',
               'QGIS: Heat map':'TIPS_NLP_QGIS Heat map.pdf',
               'QGIS: Frequency map (graduated color map choropleth)':'TIPS_NLP_QGIS Frequency map (graduated color map choropleth).pdf',
               'QGIS: Frequency map (proportional symbol)':'TIPS_NLP_QGIS Frequency map (proportional symbol).pdf',
               'QGIS: Shape files':'TIPS_NLP_QGIS Shape files.pdf',
               'QGIS: Change dots style':'TIPS_NLP_QGIS Change dots style.pdf',
               'QGIS: Change pin style':'TIPS_NLP_QGIS Change pin style.pdf',
               'QGIS: Change pin or map colors':'TIPS_NLP_QGIS Change pin or map colors.pdf',
               'QGIS: Change style of displayed data':'TIPS_NLP_QGIS Change style of displayed data.pdf',
               'QGIS: Display attributes attached to a data point':'TIPS_NLP_QGIS Display attributes attached to a data point.pdf',
               'QGIS: Display different attributes':'TIPS_NLP_QGIS Display different attributes.pdf',
               'QGIS: View data behind layers':'TIPS_NLP_QGIS View data behind layers.pdf',
               'QGIS: Finishing touches in producing a map':'TIPS_NLP_QGIS Finishing touches in producing a map.pdf',
               'QGIS: Data points not visible on the map':'TIPS_NLP_QGIS Data points not visible on the map.pdf',
               'QGIS: KML file error':'TIPS_NLP_QGIS KML file error.pdf',
               'QGIS: Layer error':'TIPS_NLP_QGIS Layer error.pdf',
               'QGIS: Map not visible on the screen':'TIPS_NLP_QGIS Map not visible on the screen.pdf',
               'QGIS: Shapefile error':'TIPS_NLP_QGIS Shapefile error.pdf'}
TIPS_options='utf-8 encoding','csv files - Problems & solutions','Statistical measures','GIS (Geographic Information System): Mapping Locations','Characters moving in time and space','Symbolic (non-geocodable) space','Extracting locations: NER (Named Entity Recognition)','Geocoding','Geocoding: How to Improve Nominatim', 'Google Earth Pro', 'Google API Key', 'HTML', 'Google Earth Pro Icon', 'Google Earth Pro Description','Google Earth Pro From KML to Excel','QGIS: Getting started KML (PC-ACE) files coordinate systems and QGIS project files','QGIS: Import a KML file in QGIS','QGIS: Import data from Excel in QGIS','QGIS: Import more attributes than NAME and DESCRIPTION','QGIS: Join data (mapping multiple variables)','QGIS: Dot map','QGIS: Feature map','QGIS: Heat map','QGIS: Frequency map (graduated color map choropleth)','QGIS: Frequency map (proportional symbol)','QGIS: Shape files','QGIS: Change dots style','QGIS: Change pin style','QGIS: Change pin or map colors','QGIS: Change style of displayed data','QGIS: Display attributes attached to a data point','QGIS: Display different attributes','QGIS: View data behind layers','QGIS: Finishing touches in producing a map','QGIS: Data points not visible on the map','QGIS: KML file error','QGIS: Layer error','QGIS: Map not visible on the screen','QGIS: Shapefile error'


# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",'Please, select an input file for the GIS script. Two two types of files are acceptable: txt or csv.\n\nTXT FILE. When a txt file is selected, the script will use NER to obtain a list of locations saved as a csv file. The script will then process this file the same way as it would process a csv file in input containing location names.\n\nCSV FILE. When a csv file is selected it can be:\n  1. a file containing a column of location names that need to be geocoded (e.g., New York);\n  2. a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script parsers_annotators_main.py (the script parses text documents using the selected parser: spaCy, Stanford CoreNLP, or Stanza).'+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_corpusData+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory+GUI_IO_util.msg_Esc)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                  "The INPUT csv file widget displays the csv LOCATION file as soon as produced by the NER annotator.\n\nEdit the file and rerun the algorithm to geocode from scratch.\n\nYou can also use the 'Select INPUT CSV file' button to select\n   1. a csv file, however created (e.g., NER annotator), containing a list of locations, i.e., a column header 'Location' and different locations in each row (e.g., Atlanta, New York City, Paris, South Korea); when a DATE field is present, the GIS algorithms will create dynamic maps;\n   2. a csv file of geocoded locations (with fields LATITUDE and LONGITUDE) previosuly created either by this algorithm or externally; if a 'Document' field, or 'Sentence' field, or 'Summary' field or 'Date' field are presnt in the csv file, they will be displayed when clicking on a pin; when a 'Date' field is present, the GIS algorithms will create dynamic maps;\n   3. a csv CoNLL table file with NER location tags; this last option, however, is highly discouraged since the CoNLL table currently available in the NLP Suite has one record per word/token and such country location like 'United States of America' would then not be taken as a single entity for geocoding, but as separate entities.\n\nDifferent options will be available depending upon what the csv file widget displays.\n\nTO RERUN THE PIPELINE, FROM SCRATCH, FROM TEXT TO MAPS, PRESS ESC TO CLEAR THE CSV FILE WIDGET.\n\nYou can also select a geocoded csv file and run the 'MAP locations' option." + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","This option extracts person entities and locations from your text files using Stanza NER, "
                                                                       "then produces an animated map showing how characters move across GEOGRAPHIC space (real places that resolve to map coordinates: cities, counties, countries) over the course of the narrative.\n\n"
                                                                       "The map shows dashed lines connecting successive locations for each person, with a timeline slider "
                                                                       "when dates or document sequence are available.\n\n"
                                                                       "REQUIREMENT: Text file(s) in input (not a csv file).\n\n"
                                                                       "The option uses the same NER extraction as the GIS pipeline but focuses on PERSON entities "
                                                                       "and their co-occurring locations rather than geocoding all location mentions.\n\n"
                                                                       "NOTE ON 'SPACE': here 'space' means GEOGRAPHIC, geocodable space. For SYMBOLIC / SOCIAL space that has NO map coordinates - e.g. house vs. field, or how a social attribute (gender, race, class) maps onto types of space - use the 'Symbolic / social space' option below."+GUI_IO_util.msg_Esc)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to EXTRACT locations from a text file using NER (Named Entity Recognition).\n\nUse the dropdown menu to select the NER package:\n\n   Stanza (recommended): modern neural network (BiLSTM-CRF), supports 30+ languages, multi-word entities are pre-joined (e.g., 'United States of America' is returned as a single entity).\n\n   spaCy: fast, supports 20+ languages.\n\n   Stanford CoreNLP: fine-grained location types (CITY, STATE_OR_PROVINCE, COUNTRY, LOCATION), primarily English, requires Java.\n\nThe option is available ONLY when input txt file(s) is selected.\n\nTo improve the geocoding of those locations that can take multiple names (e.g., 'United States', 'US', 'USA'), the NLP Suite Stanford CoreNLP algorithm uses the entries of the multi_name_locations.csv file stored in the lib\\wordLists subdirectory of the NLP Suite installation folder. Locations known under different names can be all geocoded under a single name (e.g., 'United States'). You can edit the multi_name_locations.csv file to suit your specific needs and improve geocoding."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the column containing the location names (e.g., New York) to be geocoded and mapped.\n\nTHE OPTION IS NOT AVAILABLE WHEN SELECTING A CONLL INPUT CSV FILE. NER IS THE COLUMN AUTOMATICALLY USED WHEN WORKING WITH A CONLL FILE IN INPUT."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to GEOCODE a list of locations.\n\n'Split' locations (e.g. South America, Atlantic City) will be joined together for geocoding using the following prefix values:\n  south, north, west, east, los, new, san, las, la, hong\nand suffix values:\n  city, island\n\nWHEN USING THE CoNLL TABLE AS INPUT, ONLY TWO CONSECUTIVE VALUES WILL BE JOINED TOGETHER (thus, 'New South Wales' would not be joined).\n\nThe geocoding option is available ONLY when a csv file of locations NOT yet geocoded is selected."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","To obtain more accurate geocoded results, select a country where most locations are expected to be. Locations falling in the selected country of bias will be given PREFERENCE by the geocoder over locations with the same name in other countries. Thus, if you select United States as your country bias, the geocoder will geocode locations such as Florence, Rome, or Venice in the United States rather than in Italy.\n\nIf you want to geocode locations mostly located in a specific area, enter the latitude and longitude for the upper left-hand and lower right-hand corners of a rectangle that will be used for finding the locations.\n\nTick the Restrict checkbox if you wish to restrict the search area to the selected area ONLY (otherwise, it is just a preference).\n\nAREA AND RESTRICT WIDGETS ARE AVAILABLE ONLY FOR NOMINATIM."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to MAP a list of geocoded locations.\n\nUsing the dropdown menu, select the GIS (Geographic Information System) package you wish to use to produce maps.\n\nGoogle Maps requires an API key that you obtain from registering.\n\nWhen selecting Google Maps, the API key field will become available.\n\nYou will need to get the API key from the Google console and entering it there. REMEMBER! When applying for an API key you will need to enter billing information; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale.\n https://developers.google.com/maps/documentation/embed/get-api-key.\n\nAfter entering the Google API key, click OK to save it and the key will be read in automatically next time around.\n\nTick the Open GUI checkbox ONLY if you wish to open the Google Earth Pro GUI for more options after running the NER location extractor (and, perhaps, the geocoder)."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the Google Api key you wish to visualize, then click on the button to open the config file to view/change the key."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script allows users to go from text to map in three steps:\n\n1. EXTRACT locations from a text file using NER (Named Entity Recognition) via the selected NER package (BERT, Stanza, spaCy, or Stanford CoreNLP);\n2. GEOCODE locations, previously extracted, using Nominatim or Google (an API is needed for Google);\n3. MAP locations, previously geocoded, using a selected GIS package (e.g., Google Earth Pro; Google Maps to produce heat maps; Google Maps requires an API key).\n\nOptions are preset and/or disabled depending upon the input type (directory or file; txt or csv file; csv CoNLL file or list of locations to be geocoded or already geocoded).\n\nAll three steps can be selected and carried out in sequence in a pipeline, going automatically from text to map.\n\nIn INPUT, the script can either take:\n   1. A CoNLL table produced by the selected parser and use the NER (Named Entity Recognition) values of LOCATION (STATE, PROVINCE, CITY, COUNTRY), values for geocoding;\n   2. a csv file that contains location names to be geocoded (e.g., Chicago);\n   2. a csv file that contains geocoded location names with latitude and longitude.\n\ncsv files, except for the CoNLL table, must have a column header 'Location' (the header 'Word' from the NER annotator will be converted automatically to 'Location')."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

reminders_util.checkReminder(scriptName, reminders_util.title_options_GIS_default,
                             reminders_util.message_GIS_default, True)

# routine_options = reminders_util.getReminders_list(config_filename)
result = reminders_util.checkReminder(scriptName,
                              reminders_util.title_options_GIS_GUI,
                              reminders_util.message_GIS_GUI)
if result!=None:
    routine_options = reminders_util.getReminders_list(scriptName)

activate_Google_API_geocode()
activate_Google_API_Google_Maps()

GUI_util.window.mainloop()
