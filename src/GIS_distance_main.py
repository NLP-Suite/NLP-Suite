# Roberto Franzosi Fall 2019-Spring 2020

# INPUT The function computeDistance assumes that:
#   the location name is always the column of the FIRST location name followed by its latitude and longitude
#       followed by the SECOND location name followed by its latitude and longitude
#   longitude is always in the next column of latitude 1 and 2

# geodesic distance
# Geopy can calculate geodesic distance between two points using
#   the geodesic distance
#   the great-circle distance

# The geodesic distance (also called great circle distance) is the shortest distance on the surface of an ellipsoidal model of the earth.
# There are multiple popular ellipsoidal models.
#   Which one will be the most accurate depends on where your points are located on the earth.
#   The default is the WGS-84 ellipsoid, which is the most globally accurate.
#   geopy includes a few other models in the distance.ELLIPSOIDS dictionary.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS",['tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import IO_files_util
import GUI_IO_util
import GIS_file_check_util
import GIS_distance_util
import GIS_geocode_util
import GIS_pipeline_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,outputDir, openOutputFiles, chartPackage, dataTransformation,
        encoding,
        # geocode,
        compute_pairwise_distances, compute_baseline_distances, compute_consecutive_distances, baselineLocation, pairwise_scope):
    config_filename = GUI_util.config_filename_selected_config.get()

    filesToOpen = []

    # step 1 - geocoder_Google_Earth
    # step 2 - extract_NER_locations
    # step 3 - geocode
    # step 4 - generate_kml
    # compute geodesic distances
    # compute geodesic distances from specific location

    # this will check the appended country names and short name
    # from iso3166 import countries
    # for c in countries:
    #     print(c)

    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable=GIS_file_check_util.CoNLL_checker(inputFilename)

    if input_main_dir_path.get() != '':
        mb.showwarning(title='File type error',
                       message='The GIS distance script expects a csv file in input. Please, select a csv file and try again.')
        return
    if not inputFilename.endswith('.csv'):
        mb.showwarning(title='File type error',
                       message='The input file\n\n' + inputFilename + '\n\nis not an expected csv file. Please, check the file and try again.')
        return

    if compute_pairwise_distances== False and compute_baseline_distances==False and compute_consecutive_distances==False:
        mb.showwarning(title='Warning',
                       message="No options have been selected.\n\nPlease, select an option and try again.")
        return

    # Location / Latitude / Longitude are resolved BY HEADER NAME inside the util functions,
    # so no FIRST/SECOND location-column selection is needed. Pairwise forms all-pairs of the
    # distinct geocoded locations itself; baseline auto-detects the 'Location' column.
    locationColumnNumber = 0

    encodingValue='utf-8'

    geocoder = 'Nominatim'

    if "Google" in geocoder:
        Google_API = GIS_pipeline_util.getGoogleAPIkey(window, 'Google-geocode-API_config.csv')
    else:
        Google_API=''

    geolocator = GIS_geocode_util.get_geolocator(geocoder,Google_API)

    distinctValues=True

    numColumns=len(headers)
    split_locations=''

    # the two modes are independent and may both run; accumulate the files each produces
    filesToOpen=[]

    if compute_baseline_distances and baselineLocation!='':
        baselineFiles=GIS_distance_util.computeDistancesFromSpecificLocation(GUI_util.window,inputFilename, outputDir, geolocator,geocoder,inputIsGeocoded,baselineLocation, headers,locationColumnNumber,'', distinctValues,withHeader,inputIsCoNLL,split_locations,datePresent,filenamePositionInCoNLLTable,encodingValue,chartPackage,dataTransformation)
        if baselineFiles:
            filesToOpen.extend(baselineFiles)

    if compute_pairwise_distances:
        # all-pairs of the DISTINCT geocoded locations; scope = per-document or whole-corpus
        pairwiseFiles=GIS_distance_util.computePairwiseDistances(GUI_util.window,inputFilename,outputDir,distinctValues,encodingValue,pairwise_scope,chartPackage,dataTransformation)
        pairwiseFiles=[f for f in pairwiseFiles if f]
        if pairwiseFiles:
            filesToOpen.extend(pairwiseFiles)

    if compute_consecutive_distances:
        # movement: distance between each geolocated location and the next, within each Document.
        # Resolves Latitude/Longitude/Document/Sentence ID by header name, so it consumes the
        # single-location geocoded csv directly (no hand-built two-location file).
        consecutiveFiles=GIS_distance_util.computeConsecutiveDistances(GUI_util.window, inputFilename, outputDir, distinctValues, encoding)
        consecutiveFiles=[f for f in consecutiveFiles if f]
        if consecutiveFiles:
            filesToOpen.extend(consecutiveFiles)

    if len(filesToOpen)==0:
        return

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.charts_package_options_widget.get(),
                            GUI_util.data_transformation_options_widget.get(),
                            encoding_var.get(),
                            # geocode_var.get(),
                            compute_pairwise_distances_var.get(),
                            compute_baseline_distances_var.get(),
                            compute_consecutive_distances_var.get(),
                            baselineLocation_entry_var.get(),
                            pairwise_scope_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=505, # height at brief display
                                                 GUI_height_full=545, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Computing Geodesic and Great-Circle Distances between Locations'
head, scriptName = os.path.split(os.path.basename(__file__))
# hardcode the default config at module init: config_filename_selected_config is empty this early,
# which would make the startup I/O check falsely report the INPUT/OUTPUT fields as missing
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

config_input_output_numeric_options=[3,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window=GUI_util.window
config_input_output_numeric_options=GUI_util.config_input_output_numeric_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

# ---- INPUT csv picker + related-GUIs launcher (template from nominalization_main; adapted so
# ---- the picker takes ANY geocoded csv, not a CoNLL table) ----------------------------------
csv_file_var = tk.StringVar()
extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()

def _plausible_gis(path):
    # drop the geocoding residue that has no coordinates
    p = os.path.basename(path).lower()
    return not any(n in p for n in ('not-found', 'not_found', 'non-distinct'))

def _is_geocoded_csv(path):
    # a GIS-distance input is a GEOCODED csv: it must carry Latitude + Longitude columns
    # (also matches the pairwise 6-column form Latitude1/Longitude1/Latitude2/Longitude2).
    try:
        with open(path, encoding='utf-8-sig', newline='') as f:
            cols = {c.strip().strip('"').lower() for c in (f.readline() or '').split(',')}
    except Exception:
        return False
    return any('latitude' in c for c in cols) and any('longitude' in c for c in cols)

def _apply_selected_csv(f):
    csv_file_var.set(f)
    GUI_util.inputFilename.set(f)            # trace -> refreshes the location-column dropdowns
    GUI_util.input_main_dir_path.set('')
    try:                                     # re-evaluate RUN now that a csv is selected
        _missing = '' if GUI_util.output_dir_path.get() != '' else 'OUTPUT files directory\n'
        GUI_util.activateRunButton(GUI_util.config_filename_selected_config.get() or config_filename,
                                   IO_setup_display_brief, scriptName, _missing, True)
    except Exception as e:
        print('GIS_distance select_csv_file: could not re-evaluate RUN button:', e)

def select_csv_file():
    import CoNLL_util
    import tkinter.filedialog as filedialog
    # list only the GEOCODED GIS csv files found for this corpus (Latitude + Longitude columns)
    matches = CoNLL_util.find_corpus_csv(GUI_util.output_dir_path.get(),
                                         GUI_util.inputFilename.get(),
                                         GUI_util.input_main_dir_path.get(),
                                         path_filter=_plausible_gis, validator=_is_geocoded_csv)
    chosen = IO_files_util.select_path_from_list(
        window, matches,
        'Select a GEOCODED GIS csv (Latitude & Longitude columns) found for your corpus, '
        'or browse for another file:',
        title='Available geocoded GIS csv files')
    if chosen is None:
        return
    if chosen == '__BROWSE__':
        f = filedialog.askopenfilename(title='Select INPUT geocoded csv file',
                                       filetypes=[('csv files', '*.csv'), ('All files', '*.*')])
    else:
        f = chosen
    if f:
        _apply_selected_csv(f)

csv_file_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width,
                            text='Select INPUT CSV file', command=lambda: select_csv_file())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               csv_file_button, True)

openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                    openInputFile_button, True, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                    "Open the selected INPUT csv file")

csv_file = tk.Entry(window, width=GUI_IO_util.csv_file_width, textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, csv_file)

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ', variable=extra_GUIs_var,
                                     onvalue=1, offvalue=0, command=lambda: open_GUI())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               extra_GUIs_checkbox, True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window, extra_GUIs_menu_var, 'GIS: Mapping locations (Open GUI)',
                                'Google Earth (Open GUI)', 'Symbolic (non-geocodable) space (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                    extra_GUIs_menu, False, False, True, False, 90, GUI_IO_util.IO_configuration_menu,
                    "Open a related GIS tool without leaving this GUI.\nThe selected GUI opens without pressing RUN.")

def open_GUI(*args):
    import run_script_util
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    sel = extra_GUIs_menu_var.get()
    if not sel:
        return
    if 'Mapping' in sel:
        run_script_util.run_script("GIS_main.py")
    elif 'Google Earth' in sel:
        run_script_util.run_script("GIS_Google_Earth_main.py")
    elif 'Symbolic' in sel:
        run_script_util.run_script("GIS_symbolic_main.py")

extra_GUIs_menu_var.trace('w', open_GUI)

encoding_var=tk.StringVar()
# geocode_var=tk.IntVar()
pairwise_scope_var=tk.StringVar()
compute_baseline_distances_var=tk.IntVar()
baselineLocation_entry_var=tk.StringVar()
compute_pairwise_distances_var=tk.IntVar()
compute_consecutive_distances_var=tk.IntVar()

def clear(e):
    csv_file_var.set('')
    GUI_util.inputFilename.set('')
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set('')
    extra_GUIs_menu.configure(state='disabled')
    encoding_var.set('utf-8')
    compute_pairwise_distances_var.set(0)
    compute_baseline_distances_var.set(0)
    compute_consecutive_distances_var.set(0)
    baselineLocation_entry_var.set('')
    pairwise_scope_var.set('per-document')
    GUI_util.run_button.configure(state='disabled')   # no input -> RUN off until a csv is picked again
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+350, y_multiplier_integer,encodingValue,True)
encoding_lb = tk.Label(window, text='Select the encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,y_multiplier_integer,encoding_lb)

# geocode_var.set(0)
# geocode_checkbox = tk.Checkbutton(window, variable=geocode_var, onvalue=1, offvalue=0)
# geocode_checkbox.config(text="Geocode locations")
# y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
#                                                y_multiplier_integer, geocode_checkbox)

compute_pairwise_distances_var.set(0)
compute_pairwise_distances_checkbox = tk.Checkbutton(window, variable=compute_pairwise_distances_var, onvalue=1, offvalue=0)
compute_pairwise_distances_checkbox.config(text="Compute pairwise distances (all-pairs of distinct locations)")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, compute_pairwise_distances_checkbox,True)

pairwise_scope_var.set('per-document')
pairwise_scope_menu = tk.OptionMenu(window, pairwise_scope_var, 'per-document', 'whole-corpus', 'both')
pairwise_scope_menu.configure(state='disabled')   # enabled when the pairwise checkbox is ticked
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+350, y_multiplier_integer, pairwise_scope_menu)

compute_baseline_distances_var.set(0)
compute_baseline_distances_checkbox = tk.Checkbutton(window, variable=compute_baseline_distances_var, onvalue=1, offvalue=0)
compute_baseline_distances_checkbox.config(text="Compute distances from baseline location")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, compute_baseline_distances_checkbox,True)

baselineLocation_value_lb = tk.Label(window, text='Enter location ')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+350,y_multiplier_integer,baselineLocation_value_lb,True)
baselineLocation_entry = tk.Entry(window, textvariable=baselineLocation_entry_var)
baselineLocation_entry.configure(width=50, state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate+450,y_multiplier_integer,baselineLocation_entry)

compute_consecutive_distances_var.set(0)
compute_consecutive_distances_checkbox = tk.Checkbutton(window, variable=compute_consecutive_distances_var, onvalue=1, offvalue=0)
compute_consecutive_distances_checkbox.config(text="Compute distances between consecutive locations (movement per document)")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, compute_consecutive_distances_checkbox)

def activate_options(*args):
    # modes are independent and may all run together; each enables only its own widget
    if compute_pairwise_distances_var.get():
        pairwise_scope_menu.configure(state='normal')
    else:
        pairwise_scope_menu.configure(state='disabled')

    if compute_baseline_distances_var.get():
        baselineLocation_entry.configure(state='normal')
    else:
        baselineLocation_entry.configure(state='disabled')
        baselineLocation_entry_var.set('')

compute_pairwise_distances_var.trace('w',activate_options)
compute_baseline_distances_var.trace('w',activate_options)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Geocoding":"TIPS_NLP_GIS_Geocoding.pdf","Geographic distances":"TIPS_NLP_GIS distances.pdf",'Statistical measures':'TIPS_NLP_Statistical measures.pdf'}
TIPS_options='Geocoding', 'Geographic distances', 'Statistical measures'

# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,'Please, select an input file for the GIS script. Two two types of files are acceptable: txt or csv.\n\nTXT FILE. When a txt file is selected, the script will use NER to obtain a list of locations saved as a csv file. The script will then process this file the same way as it would process a csv file in input containing location names.\n\nCSV FILE. When a csv file is selected it can be:\n  1. a file containing a column of location names that need to be geocoded (e.g., New York);\n  2. a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script parsers_annotators_main.py (the script parses text documents using the selected parser: spaCy, Stanford CoreNLP, or Stanza).'+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_corpusData+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory+GUI_IO_util.msg_Esc)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, click the 'Select INPUT CSV file' button to choose the GEOCODED GIS csv file to process.\n\nThe picker lists only the geocoded csv files found for your corpus, i.e., files that contain Latitude and Longitude columns (typically produced by the GIS mapping tool). You can also browse for another file.\n\nThe distance algorithms require geocoded data (Latitude/Longitude) to compute distances between locations."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the 'GUIs available for more analyses' checkbox to enable the dropdown menu, then select a related tool to open its Graphical User Interface (GUI):\n\n  1. GIS: Mapping locations, to map geocodable locations in time and space;\n  2. Google Earth, to visualize locations in Google Earth Pro;\n  3. Symbolic (non-geocodable) space, to analyze characters moving in NON-geocodable narrative space (house, field, forest, threshold).\n\nThe selected GUI opens without pressing RUN."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to compute PAIRWISE distances, i.e., the distance between every combination of two of the DISTINCT geolocated locations in your input file.\n\nIn INPUT the script expects a single GEOCODED csv (as produced by the GIS mapping tool) with a Location column and Latitude/Longitude columns. You do NOT need to prepare a file with two location columns: the tool forms the pairs itself.\n\nUse the dropdown to the right to select the SCOPE:\n   - per-document (default): all-pairs WITHIN each document. Cheap and narrative-aware (it pairs only places that co-occur in the same story); requires a Document column.\n   - whole-corpus: all-pairs across every distinct location in the file. This grows as N-squared (N = number of distinct locations) and can be very slow on large, place-rich corpora; it also pairs locations from unrelated documents.\n   - both: runs per-document AND whole-corpus, producing two separate output files.\n\nSee the 'Geographic distances' TIPS for the computing-cost details."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to compute distances of all locations listed in your input file from a specific location (e.g., Atlanta). You will need to enter the location name (e.g., again, Atlanta).\n\nIn INPUT the script expects either\n   1. a list of locations that will be geocoded before computing distances from a baseline location. The input file must have a column of locations (selected in the FIRST selected location names).\n   2. geocoded data with Latitude and Longitude values for a set of locations whose distances from a baseline location you want to compute. The input file must have a column with the FIRST selected location name, followed by its latitude and longitude."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to compute MOVEMENT distances, i.e., the distance between each geolocated location and the NEXT one within the same document (how far the narrative/characters move from place to place across a story).\n\nIn INPUT the script expects a single GEOCODED csv (as produced by the GIS mapping tool) with Latitude and Longitude columns. Locations are ordered by Sentence ID within each Document and paired in sequence, so a single-location geocoded file is all you need: the FIRST/SECOND location columns are NOT used by this option.\n\nIn OUTPUT the script lists each consecutive location pair with its geodesic and great circle distances (miles and Km), together with the Document and the from/to sentences."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    return y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.help_button_x_coordinate,0)

# change the value of the readMe_message
readMe_message="This Python 3 script computes geographic distances between locations, in both kilometers and miles, by either geodesic or great circle distance.\n\nIn INPUT the script expects a single GEOCODED csv (as produced by the GIS mapping/geocoding tool) with a Location column and Latitude/Longitude columns. Locations, coordinates and (optionally) Document/Sentence are read by column name; you do NOT need to prepare a file with two location columns.\n\nThree distance options are available:\n   1. PAIRWISE distances: the distance between every combination of two of the distinct locations, either within each document (per-document) or across the whole file (whole-corpus).\n   2. BASELINE distances: the distance from a location you type (e.g., New York) to each location in the file.\n   3. MOVEMENT distances: the distance between each location and the next one within a document (how far characters move across a story).\n\nAll options compute both GEODESIC and GREAT CIRCLE distances (miles and Km) and produce a distance-distribution chart."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()

