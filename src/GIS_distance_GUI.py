import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS",['os','io','PIL','tkinter','tkcolorpicker','urllib'])==False:
    sys.exit(0)

import tkinter as tk

import os
import io
from PIL import Image, ImageTk
from sys import platform
import csv
import tkinter.ttk as ttk
from tkinter import filedialog
from tkcolorpicker import askcolor

import tkinter.messagebox as mb
from urllib.request import urlopen # used to call Google website to display a selected pin

import GUI_IO_util
import IO_csv_util
import config_util # used for Google API
import reminders_util
import GIS_Google_pin_util

# GUI CHANGES add following lines to every special GUI
# +3 is the number of lines starting at 1 of IO widgets
y_multiplier_integer=GUI_util.y_multiplier_integer+1
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_options,config_filename)

"""
Icons
http://maps.google.com/mapfiles/kml/shapes
http://maps.google.com/mapfiles/kml/pushpin
http://maps.google.com/mapfiles/kml/paddle
http://earth.google.com/images/kml-icons/
http://maps.google.com/mapfiles/kml/pal1,pal2, pal3, pal4, pal5
http://maps.google.com/mapfiles
"""

# GUI CHANGES add following lines to every special GUI
y_multiplier_integer=GUI_util.y_multiplier_integer+1
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

encoding_var=tk.StringVar()
location_var=tk.StringVar()
location_var2=tk.StringVar()
baselineLocation_entry_var=tk.StringVar()

def clear(e):
	location_var.set('')
	location_var2.set('')
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300, y_multiplier_integer,encodingValue,True)
encoding_lb = tk.Label(window, text='Select the encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,encoding_lb)

baselineLocation_value_lb = tk.Label(window, text='Enter baseline location ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,baselineLocation_value_lb,True)
baselineLocation_entry = tk.Entry(window, textvariable=baselineLocation_entry_var)
baselineLocation_entry.configure(width=50, state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+150,y_multiplier_integer,baselineLocation_entry)

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

TIPS_lookup = {"Google Earth Pro":"TIPS_NLP_Google Earth Pro.pdf","Google Earth Pro KML Options":"TIPS_NLP_Google Earth Pro KML options.pdf","HTML":"TIPS_NLP_Google Earth Pro HTML.pdf","Google Earth Pro Icon":"TIPS_NLP_Google Earth Pro Icon.pdf", "Google Earth Pro Description":"TIPS_NLP_Google Earth Pro Description.pdf"}
TIPS_options='Geocoding', 'Google Earth Pro', 'Google Earth Pro KML Options', 'HTML', 'Google Earth Pro Icon', 'Google Earth Pro Description'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util. 
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",'Please, select an input csv file for the GIS distance script.\n\nThe INPUT csv file for GIS distances expects geocoded data with Latitude and Longitude values for two sets of locations whose distances you want to compute.The input file must have a column with the FIRST selected location name, followed by its latitude and longitude; followed by the SECOND selected location name, followed by its latitude and longitude.\n\nThe input csv file may contain other fields but the location and geocoded fields MUST be in this order.')
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_outputDirectory)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help","Please, enter a location name (e.g., New York) in the 'Enter baseline location' field, if you wish to compute distances of all locations listed in your input file from a specific location (again, e.g., New York).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","Please, using the dropdown menu, select the column containing the FIRST set of location names (e.g., New York).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","Please, using the dropdown menu, select the column containing the SECOND set of location names (e.g., Atlanta).")
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script computes geographic distances between locations, in both kilometers and miles, by either geodesic distance or by great circle distance. Distances will be visualized in Excel charts.\n\nBoth GEODESIC and GREAT CIRCLE distances, in miles and kilometers, will be computed.\n\nIn INPUT the script expects geocoded data with Latitude and Longitude values for two sets of locations whose distances you want to compute. The input file must have a column with the FIRST selected location name, followed by its latitude and longitude; followed by the SECOND selected location name, followed by its latitude and longitude.\n\nThe input csv file may contain other fields but the location and geocoded fields MUST be in this order.\n\nEnter a location name (e.g., New York) in the 'Enter baseline location' field, if you wish to compute distances of all locations listed in your input file from a specific location (again, e.g., New York)."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

