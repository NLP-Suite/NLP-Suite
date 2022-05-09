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

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS",['tkinter'])==False:
    sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb

import IO_files_util
import GUI_IO_util
import GIS_file_check_util
import GIS_distance_util
import IO_csv_util
import GIS_geocode_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,outputDir, openOutputFiles, createExcelCharts,
        encoding, geocoder,
        # geocode,
        compute_pairwise_distances, compute_baseline_distances, baselineLocation,locationColumn,locationColumn2):


    filesToOpen = []

    # step 1 - geocoder_Google_Earth
    # step 2 - extract_NER_locations
    # step 3 - geocode
    # step 4 - generate_kml
    # compute geodesic distances
    # compute geodesic distances from specific location

    # this will check the extended country names and short name
    # from iso3166 import countries
    # for c in countries:
    #     print(c)

    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable=GIS_file_check_util.CoNLL_checker(inputFilename)

    # if input_main_dir_path.get()!='':
    #     mb.showwarning(title='File type error',
    #                    message='The GIS distance scripts expects in input a csv file. Please, select a csv file and try again.')
    #     return
    # if inputFilename.endswith('.csv') == False:
    #     mb.showwarning(title='File type error',
    #                    message='The input file\n\n' + inputFilename + '\n\nis not an expected csv file. Please, check the file and try again.')
    #     return

    if compute_pairwise_distances== False and compute_baseline_distances==False:
        mb.showwarning(title='Warning',
                       message="No options have been selected.\n\nPlease, select an option and try again.")
        return

    if compute_pairwise_distances== True and inputIsGeocoded==False:
        mb.showwarning(title='Warning',
                       message='You are running the GIS algorithm for pairwise distances with an input file that seems to be non-geocoded. You cannot run this option with non-geocoded data. You can only run the option "Compute distances from baseline location."\n\nPlease, select a different option or a geocoded file with six columns and try again.')
        return

    if compute_pairwise_distances and (locationColumn==""):
        mb.showwarning(title='Warning',
                       message='You are running the GIS algorithm for pairwise distances. You must select the column containing the First location names.\n\nPlease, using the dropdown menu, select the column of the FIRST location names and try again.')
        return

    if compute_pairwise_distances== True and inputIsGeocoded and len(headers)<6:
        mb.showwarning(title='Warning',
                       message='You are running the GIS algorithm for pairwise distances. But your input file has fewer than the expected 6 headers (Location1, Latitude1, Longitude1, Location2, Latitude2, Longitude2):\n\n' + str(headers) + '\n\nPlease, select a different file and try again.')
        return

    if compute_pairwise_distances== False and inputIsGeocoded and (locationColumn=="" or locationColumn2==""):
        mb.showwarning(title='Warning',
                       message='You are running the GIS distance algorithm using two sets of locations. You must select the columns containing the First and Second location names.\n\nPlease, using the dropdown menu, select the column of the FIRST and SECOND location names and try again.')
        return

    if compute_baseline_distances and baselineLocation != '' and locationColumn=="":
        mb.showwarning(title='Warning',
                       message='You are running the GIS distance algorithm from the baseline location ' + baselineLocation + '. You must select the column containing the First location name.\n\nPlease, using the dropdown menu, select the column of the FIRST location names and try again.')
        return


    locationColumnNumber = 0
    locationColumnNumber2 = 0

    if withHeader==True:
        locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumn)
        if len(locationColumn2)>0:
            locationColumnNumber2=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumn2)

    encodingValue='utf-8'

    geocoder = 'Nominatim'

    if "Google" in geocoder:
        Google_API = GIS_pipeline_util.getGoogleAPIkey('Google-geocode-API_config.csv')
    else:
        Google_API=''

    geolocator = GIS_geocode_util.get_geolocator(geocoder,Google_API)

    distinctValues=True

    numColumns=len(headers)
    split_locations=''

    if compute_baseline_distances and baselineLocation!='':
        filesToOpen=GIS_distance_util.computeDistancesFromSpecificLocation(GUI_util.window,inputFilename, outputDir, createExcelCharts, geolocator,geocoder,inputIsGeocoded,baselineLocation, headers,locationColumnNumber,locationColumn, distinctValues,withHeader,inputIsCoNLL,split_locations,datePresent,filenamePositionInCoNLLTable,encodingValue)
        if len(filesToOpen)==0:
            return
    if compute_pairwise_distances:
        filesToOpen=GIS_distance_util.computePairwiseDistances(GUI_util.window,inputFilename,outputDir,createExcelCharts,headers,locationColumnNumber,locationColumnNumber2,locationColumn,locationColumn2, distinctValues,geolocator,geocoder,inputIsCoNLL,datePresent,encodingValue)
        if len(filesToOpen)==0:
            return
        if len(filesToOpen) == 0:
            return

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            encoding_var.get(),
                            geocoder_var.get(),
                            # geocode_var.get(),
                            compute_pairwise_distances_var.get(),
                            compute_baseline_distances_var.get(),
                            baselineLocation_entry_var.get(),
                            location_var.get(),
                            location_var2.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=480, # height at brief display
                                                 GUI_height_full=520, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Computing Geodesic and Great-Circle Distances between Locations'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = scriptName.replace('main.py', 'config.csv')

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

GUI_util.GUI_top(config_input_output_numeric_options,config_filename,IO_setup_display_brief)

encoding_var=tk.StringVar()
geocoder_var=tk.StringVar()
# geocode_var=tk.IntVar()
location_var=tk.StringVar()
location_var2=tk.StringVar()
compute_baseline_distances_var=tk.IntVar()
baselineLocation_entry_var=tk.StringVar()
compute_pairwise_distances_var=tk.IntVar()

def clear(e):
    location_var.set('')
    location_var2.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350, y_multiplier_integer,encodingValue,True)
encoding_lb = tk.Label(window, text='Select the encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,encoding_lb)

geocoder_lb = tk.Label(window, text='Geocoder')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,geocoder_lb,True)
geocoder_var.set('Nominatim')
geocoder = tk.OptionMenu(window,geocoder_var,'Nominatim','Google')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350, y_multiplier_integer,geocoder)

# geocode_var.set(0)
# geocode_checkbox = tk.Checkbutton(window, variable=geocode_var, onvalue=1, offvalue=0)
# geocode_checkbox.config(text="Geocode locations")
# y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),
#                                                y_multiplier_integer, geocode_checkbox)

compute_pairwise_distances_var.set(0)
compute_pairwise_distances_checkbox = tk.Checkbutton(window, variable=compute_pairwise_distances_var, onvalue=1, offvalue=0)
compute_pairwise_distances_checkbox.config(text="Compute pairwise distances")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, compute_pairwise_distances_checkbox)

compute_baseline_distances_var.set(0)
compute_baseline_distances_checkbox = tk.Checkbutton(window, variable=compute_baseline_distances_var, onvalue=1, offvalue=0)
compute_baseline_distances_checkbox.config(text="Compute distances from baseline location")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),
                                               y_multiplier_integer, compute_baseline_distances_checkbox,True)

baselineLocation_value_lb = tk.Label(window, text='Enter location ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350,y_multiplier_integer,baselineLocation_value_lb,True)
baselineLocation_entry = tk.Entry(window, textvariable=baselineLocation_entry_var)
baselineLocation_entry.configure(width=50, state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+450,y_multiplier_integer,baselineLocation_entry)

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

location_field_lb = tk.Label(window, text='Select the column containing the FIRST location names')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,location_field_lb,True)
if menu_values!='':
    location_field = tk.OptionMenu(window,location_var,*menu_values)
else:
    location_field = tk.OptionMenu(window,location_var,menu_values)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350, y_multiplier_integer,location_field)

location_field_lb2 = tk.Label(window, text='Select the column containing the SECOND location names')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,location_field_lb2,True)
if menu_values!='':
    location_field2 = tk.OptionMenu(window,location_var2,*menu_values)
else:
    location_field2 = tk.OptionMenu(window,location_var2,menu_values)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+350, y_multiplier_integer,location_field2)

def activate_options(*args):
    if compute_pairwise_distances_var.get():
        compute_baseline_distances_checkbox.configure(state='disabled')
        baselineLocation_entry.configure(state='disabled')
        location_field2.configure(state='normal')
        baselineLocation_entry_var.set('')
    else:
        compute_baseline_distances_checkbox.configure(state='normal')
        baselineLocation_entry.configure(state='normal')
        location_field2.configure(state='disabled')

    if compute_baseline_distances_var.get():
        compute_pairwise_distances_checkbox.configure(state='disabled')
        baselineLocation_entry.configure(state='normal')
        location_field2.configure(state='disabled')
    else:
        compute_pairwise_distances_checkbox.configure(state='normal')
        baselineLocation_entry.configure(state='disabled')
        location_field2.configure(state='normal')
        baselineLocation_entry_var.set('')

compute_pairwise_distances_var.trace('w',activate_options)
compute_baseline_distances_var.trace('w',activate_options)

def changed_GIS_filename(*args):

    # check that input file is a CoNLL table;
    #	many options are NOT available when working with a CoNLL table
    location_var.set('')
    location_var2.set('')
    baselineLocation_entry.configure(state='normal')

    # 	reminders_util.checkReminder("geocoding_welcome","Welcome to the geocoder Graphical User Interface (GUI)","Welcome to the geocoder Graphical User Interface (GUI).\n\nWhen running the SVO (Subject-Verb-Object) algorithm, all geocoder options have been automatically setup for you.\n\nOf course, you can change any of the options after reading the TIPS files or the ?HELP messages.\n\nAs a first time user, for now, all you need to do is to CLICK RUN.")

    menu_values = IO_csv_util.get_csvfile_headers(inputFilename.get())

    # must change 2 widgets where menus must be updated after changing the filename
    m = location_field["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: location_var.set(value))

    m = location_field2["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: location_var2.set(value))

inputFilename.trace('w', changed_GIS_filename)

changed_GIS_filename()

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {"Geocoding":"TIPS_NLP_Geocoding.pdf","Geographic distances":"TIPS_NLP_GIS distances.pdf"}
TIPS_options='Geocoding', 'Geographic distances'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,y_multiplier_integer):
    if IO_setup_display_brief==False:
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,'Please, select an input file for the GIS script. Two two types of files are acceptable: txt or csv.\n\nTXT FILE. When a txt file is selected, the script will use the NER values from Stanford CoreNLP to obtain a list of locations saved as a csv file. The script will then process this file the same way as it would process a csv file in input containing location names.\n\nCSV FILE. When a csv file is selected it can be:\n  1. a file containing a column of location names that need to be geocoded (e.g., New York);\n  2. a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script Stanford_CoreNLP_main.py (the script parses text documents using the Stanford CoreNLP parser).'+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,GUI_IO_util.msg_corpusData+GUI_IO_util.msg_Esc)
        y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_outputDirectory+GUI_IO_util.msg_Esc)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the type of geocoding service you wish to use, Google or Nominatim. For Google you need an API key."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to compute distances of all locations listed in your input file.\n\nIn INPUT the script expects geocoded data with Latitude and Longitude values for two sets of locations whose distances you want to compute. The input file must have a column with the FIRST selected location name, followed by its latitude and longitude; followed by the SECOND selected location name, followed by its latitude and longitude.\n\nSix columns in input are expected (e.g., Location1, Latitude1, Longitude1, Location2, Latitude2, Longitude2, in this order). The input csv file may contain other fields but the location and geocoded fields MUST be in this order."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, tick the checkbox if you wish to compute distances of all locations listed in your input file from a specific location (e.g., Atlanta). You will need to enter the location name (e.g., again, Atlanta).\n\nIn INPUT the script expects either\n   1. a list of locations that will be geocoded before computing distances from a baseline location. The input file must have a column of locations (selected in the FIRST selected location names).\n   2. geocoded data with Latitude and Longitude values for a set of locations whose distances from a baseline location you want to compute. The input file must have a column with the FIRST selected location name, followed by its latitude and longitude."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the column containing the FIRST set of location names (e.g., Location1)."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help","Please, using the dropdown menu, select the column containing the SECOND set of location names (e.g., Location2)."+GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window,help_button_x_coordinate,y_multiplier_integer,"NLP Suite Help",GUI_IO_util.msg_openOutputFiles)

    retrun y_multiplier_integer -1
y_multiplier_integer = help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),0)

# change the value of the readMe_message
readMe_message="This Python 3 script computes geographic distances between locations, in both kilometers and miles, by either geodesic distance or by great circle distance. Distances will be visualized in Excel charts.\n\nBoth GEODESIC and GREAT CIRCLE distances, in miles and kilometers, will be computed.\n\nIn INPUT the script expects geocoded data with Latitude and Longitude values for one or two sets of locations, depending upon whether distances are computed from a specific baseline location or between two sets of locations listed in a csv input file. The input file must have a column with the FIRST selected location name, followed by its latitude and longitude; when computing pairwise distances, these first three columns must be followed by the SECOND selected location name, followed by its latitude and longitude.\n\nThe input csv file may contain other fields but the location and geocoded fields MUST be in this order.\n\nEnter a location name (e.g., New York) in the 'Enter baseline location' field, if you wish to compute distances of all locations listed in your input file from a specific location (again, e.g., New York)."
readMe_command = lambda: GUI_IO_util.display_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

def checkFile(*args):
    if input_main_dir_path.get()!='':
        mb.showwarning(title='File type error',
                       message='The GIS distance scripts expects in input a csv file. Please, select a csv file and try again.')
        return
    if not inputFilename.get().endswith('.csv'):
        mb.showwarning(title='File type error',
                       message='The input file\n\n' + inputFilename.get() + '\n\nis not an expected csv file. Please, check the file and try again.')
    return
inputFilename.trace('w',checkFile)
checkFile()

GUI_util.window.mainloop()

