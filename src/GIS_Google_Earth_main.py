# Roberto Franzosi, Jack Hester
# Edited by Roberto Franzosi and Yuhang Feng Fall 2019-Spring 2020
# Rewritten by Roberto Franzosi May, September 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS",['os','tkinter','tkcolorpicker','PIL'])==False:
    sys.exit(0)

import os
import tkinter as tk

import io
from PIL import Image, ImageTk
import tkinter.ttk as ttk
# tkcolorpicker requires tkinter and pillow to be installed (https://libraries.io/pypi/tkcolorpicker)
# tkcolorpicker is both the package and module name
# pillow is the Python 3 version of PIL which was an older Python 2 version
# PIL being the commmon module for both packages, you need to check for PIL and trap PIL to tell the user to install pillow
from tkcolorpicker import askcolor
import CoNLL_util

import tkinter.messagebox as mb
from urllib.request import urlopen # used to call Google website to display a selected pin

import GUI_IO_util
import GIS_Google_pin_util
import IO_files_util
import GIS_file_check_util
import GIS_pipeline_util
import IO_csv_util
import reminders_util

# RUN section ______________________________________________________________________________________________________________________________________________________

# ISO 3166-1 defines two-letter, three-letter, and three-digit country codes.
# python-iso3166 is a self-contained module that converts between these codes
#   and the corresponding country name.
# import iso3166 #pip install
# from iso3166 import countries


def run(inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation,
            encoding_var,
            locationColumnName,
            date_var, date_format_var,
            group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
            icon_var_list, specific_icon_var_list,
            name_var_list, scale_var_list, color_var_list, color_style_var_list,
            description_csv_field_var, bold_var_list, italic_var_list,
            description_var_list, description_csv_field_var_list, heat_map_var):

    if GUI_util.setup_IO_menu_var.get() == 'Default I/O configuration':
        config_filename = 'NLP_default_IO_config.csv'
    else:
        config_filename = scriptName.replace('main.py', 'config.csv')

    filesToOpen = []
    inputIsCoNLL = False

    if locationColumnName=='':
        mb.showwarning(title='No location column selected', message='No csv column containing location names has been selected.\n\nPlease, select a column and try again.')
        return

    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable=GIS_file_check_util.CoNLL_checker(inputFilename)

    if withHeader==True:
        locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumnName, inputFilename)

    # Word is the header from Stanford CoreNLP NER annotator
    if not 'Location' in headers and not 'Word' in headers and not 'NER' in headers:
        GUI_util.run_button.configure(state='disabled')
        mb.showwarning(title='Warning',
                       message="The selected input csv file does not contain the word 'Location' or 'NER' in its headers.\n\nThe GIS algorithms expect in input either\n   1. a csv file\n      a. with a column of locations (with header 'Location') to be geocoded and mapped;\n      b. a csv file with a column of locations (with header 'Location') already geocoded and to be mapped (this file will also contain latitudes and longitudes, with headers 'Latitude' and 'Longitude').\n\nThe RUN button is disabled until the expected csv file is seleted in input.\n\nPlease, select the appropriate input csv file and try again.")

        return

    # if restrictions_checker(inputFilename,inputIsCoNLL,numColumns,withHeader,headers,locationColumnName)==False:
    # 	return

    if group_var == 1 and group_number_var == 1:
        mb.showwarning(title='Only One Group Chose for Multiple Group Mapping', message='The group box is ticked for multiple groups mapping but only one group is chose.\n\nPlease, check your input and try again.')
        return

    icon_csv_field_var_name = icon_csv_field_var.get()

    if group_var == 1 and len(icon_csv_field_var_name) < 1:
        mb.showwarning(title='No CSV field for Group Split Criterion Found', message='The group box is ticked for multiple groups mapping but no csv field is specified for group splitting criterion.\n\nPlease, check your input and try again.')
        return

    datePresent=False
    geocoder='Nominatim'
    encodingValue='utf-8'

    reminders_util.checkReminder(scriptName, reminders_util.title_options_geocoder,
                                 reminders_util.message_geocoder, True)

    country_bias = ''
    area_var = ''
    restrict = False

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label='GIS-GEP',
                                                            silent=True)
    if outputDir == '':
        return
    if heat_map_var:
        mapping_package = 'Google Earth & Google Maps'
    else:
        mapping_package = 'Google Earth'
    filesToOpen = GIS_pipeline_util.GIS_pipeline(GUI_util.window,config_filename,
                                       inputFilename, inputDir, outputDir,
                                       geocoder, mapping_package, chartPackage, dataTransformation,
                                       datePresent,
                                       country_bias,
                                       area_var,
                                       restrict,
                                       locationColumnName,
                                       encodingValue,
                                       group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                                       icon_var_list, specific_icon_var_list,
                                       name_var_list, scale_var_list, color_var_list, color_style_var_list,
                                       bold_var_list, italic_var_list,
                                       description_var_list, description_csv_field_var_list)

    if filesToOpen!=None:
        if len(filesToOpen) == 0:
                return

    # # always open the kml file
    # IO_files_util.open_kmlFile(kmloutputFilename)
    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)

run_script_command=lambda: run(GUI_util.inputFilename.get(),
                GUI_util.input_main_dir_path.get(),
                GUI_util.output_dir_path.get(),GUI_util.open_csv_output_checkbox.get(),
                GUI_util.charts_package_options_widget.get(),
                GUI_util.data_transformation_options_widget.get(),
                encoding_var.get(),
                location_var.get(),
                date_var.get(),date_format_var.get(),
                group_var.get(), group_number_var.get(), group_values_entry_var_list,group_label_entry_var_list,
                icon_var_list, specific_icon_var_list,
                name_var_list, scale_var_list, color_var_list, color_style_var_list,
                description_csv_field_var.get(), italic_var_list, bold_var_list,
                description_var_list, description_csv_field_var_list, heat_map_var.get())


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(IO_setup_display_brief,
                                                 GUI_width=GUI_IO_util.get_GUI_width(3),
                                                 GUI_height_brief=550, # height at brief display
                                                 GUI_height_full=590, # height at full display
                                                 y_multiplier_integer=GUI_util.y_multiplier_integer,
                                                 y_multiplier_integer_add=1, # to be added for full display
                                                 increment=1)  # to be added for full display

GUI_label='Graphical User Interface (GUI) for Geocoding, Preparing kml File, and Visualizing Maps in Google Earth Pro'
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
config_input_output_numeric_options=[3,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

"""
Icons
http://maps.google.com/mapfiles/kml/shapes
http://maps.google.com/mapfiles/kml/pushpin
http://maps.google.com/mapfiles/kml/paddle
http://earth.google.com/images/kml-icons/
http://maps.google.com/mapfiles/kml/pal1,pal2, pal3, pal4, pal5
http://maps.google.com/mapfiles
"""

# window = GUI_util.window
# config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
# config_filename = GUI_util.config_filename
# inputFilename = GUI_util.inputFilename
# input_main_dir_path = GUI_util.input_main_dir_path

encoding_var = tk.StringVar()

location_var = tk.StringVar()

date_var = tk.StringVar()
date_format_var = tk.StringVar()

icon_var_list = []
specific_icon_var_list = []
name_var_list = []
scale_var_list = []
color_var_list = []
color_style_var_list = []
description_var_list = []
description_csv_field_var_list = []
italic_var_list = []
bold_var_list = []

selected_group = []
group_values_entry_var_list = []
group_label_entry_var_list = []

group_var = tk.IntVar()
group_number_var = tk.IntVar()
group_label_entry_var = tk.StringVar()
group_values_entry_var = tk.StringVar()

icon_var = tk.StringVar()
specific_icon_var = tk.StringVar()
icon_csv_field_var = tk.StringVar()
description_csv_field_var = tk.StringVar()
name_var = tk.IntVar()
color_var = tk.IntVar()
scale_var = tk.StringVar()
opacity_var = tk.StringVar()
description_var = tk.IntVar()
bold_var = tk.IntVar()
italic_var = tk.IntVar()
color_style_var = tk.StringVar()

inputError=False

def clear(e):
    encoding_var.set('utf-8')
    date_var.set('')
    date_format_var.set('')
    location_var.set('')
    group_var.set(0)
    name_var.set(0)
    description_var.set(0)
    description_csv_field_menu.configure(state='normal')
    description_csv_field_var_list.clear
    description_csv_field_menu.configure(state='disabled')
    description_csv_field_var.set('')
    bold_checkbox.configure(state='disabled')
    italic_checkbox.configure(state='disabled')
    GUI_util.clear("Escape")

window.bind("<Escape>", clear)

encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window, encoding_var, 'utf-8', 'utf-16-le', 'utf-32-le', 'latin-1', 'ISO-8859-1')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer, encodingValue, True)
encoding_lb = tk.Label(window, text='Select encoding type (utf-8 default)')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer, encoding_lb)

##
menu_values=[]
menu_values=" "
location_field_lb = tk.Label(window, text='Column containing location names')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               location_field_lb, True)
if menu_values != '':
    location_field = tk.OptionMenu(window, location_var, *menu_values)
else:
    location_field = tk.OptionMenu(window, location_var, menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               location_field)

date_field_lb = tk.Label(window, text='Column containing date')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               date_field_lb, True)
if menu_values != '':
    date_field = tk.OptionMenu(window, date_var, *menu_values)
else:
    date_field = tk.OptionMenu(window, date_var, menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               date_field, True)

date_format_var.set('')
date_format_lb = tk.Label(window, text='Date format ')

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate, y_multiplier_integer,
                                               date_format_lb, True)
date_format_menu = tk.OptionMenu(window, date_format_var, 'mm-dd-yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy-dd-mm',
                                 'yyyy-mm', 'yyyy')
date_format_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400, y_multiplier_integer,
                                               date_format_menu)


def check_dateFields(*args):
    if date_var.get() != '':
        date_format_var.set('mm-dd-yyyy')
        date_format_menu.config(state="normal")
    else:
        date_format_var.set('')
        date_format_menu.config(state="disabled")


date_var.trace('w', check_dateFields)

def reset_all_values():
    selected_group.clear()
    group_var.set(0)
    group_number_var.set(1)
    icon_csv_field_var.set('')
    group_values_entry_var.set('')
    group_label_entry_var.set('')

    icon_var.set('Pushpins')
    specific_icon_var.set('red')

    name_var.set(0)
    scale_var.set(2)
    color_var.set(0)
    color_style_var.set("")

    description_var.set(0)
    description_csv_field_var.set("") # location
    bold_var.set(1)
    italic_var.set(1)

    group_values_entry_var_list.clear()
    group_label_entry_var_list.clear()

    icon_var_list.clear()
    specific_icon_var_list.clear()

    name_var_list.clear()
    scale_var_list.clear()
    color_var_list.clear()
    color_style_var_list.clear()
    description_var_list.clear()
    description_csv_field_var_list.clear()
    italic_var_list.clear()
    bold_var_list.clear()


def add_group_to_list():
    if len(selected_group) < int(group_number_var.get()):
        selected_group.append([group_values_entry_var.get()])
        group_number_var.set(group_number_var.get() + 1)

        group_values_entry_var_list.clear() # .append("")
        group_label_entry_var_list.clear() # .append("")
        group_values_entry_var.set("")
        group_label_entry_var.set("")

        icon_var_list.append('Pushpins')
        specific_icon_var_list.append('red')
        icon_var.set('Pushpins')
        specific_icon_var.set('red')

        name_var_list.append(0)
        scale_var_list.clear() # .append("")
        color_var_list.clear() # .append("")
        color_style_var_list.clear() # .append("")

        name_var.set(0)
        scale_var.set(2)
        color_var.set(0)
        color_style_var.set("")

        description_var_list.clear()
        description_csv_field_var_list.clear()
        italic_var_list.clear()
        bold_var_list.clear() # append("")

        description_var.set(0)
        description_csv_field_var.set('')
        bold_var.set(1)
        italic_var.set(1)
    else:
        selected_group.clear()
        selected_group.append([group_values_entry_var.get()])
        group_label_entry_var_list.append(group_label_entry_var.get())
        group_values_entry_var_list.append(group_values_entry_var.get())

group_checkbox = tk.Checkbutton(window, text='Icon for group of values', variable=group_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               group_checkbox, True)

group_number_var.set(1)
group_lb = tk.Label(window, text='Group ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               group_lb, True)
group_number = tk.Entry(window, width=3, state='disabled', textvariable=group_number_var)

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 50, y_multiplier_integer,
                                               group_number, True)

add_group_button = tk.Button(window, text='+', width=GUI_IO_util.add_button_width, height=1, state='disabled', command=lambda: add_group_to_list())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                               add_group_button, True)

reset_group_button = tk.Button(window, text='Reset ', width=GUI_IO_util.reset_button_width, height=1, state='disabled',
                               command=lambda: reset_all_values())
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 140, y_multiplier_integer,
                                               reset_group_button, True)

csv_field_forGroups_lb = tk.Label(window, text='Select csv field ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate, y_multiplier_integer,
                                               csv_field_forGroups_lb, True)

if menu_values != '':
    csv_field_forGroups_menu = tk.OptionMenu(window, icon_csv_field_var, *menu_values)
else:
    csv_field_forGroups_menu = tk.OptionMenu(window, icon_csv_field_var, menu_values)

y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400, y_multiplier_integer,
                                               csv_field_forGroups_menu, True)

group_values_entry_var.set('')
group_values_entry_var_list.append('')
group_label_entry_var.set('')
group_label_entry_var_list.append('')


def groupSelection(*args):
    if group_var.get() == 1:
        reset_group_button.config(state='normal')
        group_values_entry.configure(state='normal')
        group_label_entry.configure(state='normal')
        csv_field_forGroups_menu.config(state='normal')
    else:
        group_number_var.set(1)
        add_group_button.config(state='disabled')
        group_values_entry_var.set('')
        group_values_entry.configure(state='disabled')
        group_label_entry_var.set('')
        group_label_entry.configure(state='disabled')
        reset_group_button.config(state='disabled')
        csv_field_forGroups_menu.config(state='disabled')


group_var.trace('w', groupSelection)

group_values_lb = tk.Label(window, text='Enter value(s) ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 540, y_multiplier_integer,
                                               group_values_lb, True)
group_values_entry = tk.Entry(window, width=10, textvariable=group_values_entry_var)
group_values_entry.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 640, y_multiplier_integer,
                                               group_values_entry, True)

group_lb = tk.Label(window, text='Group label ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 750, y_multiplier_integer,
                                               group_lb, True)
group_label_entry = tk.Entry(window, width=10, textvariable=group_label_entry_var)
group_label_entry.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 840, y_multiplier_integer,
                                               group_label_entry)

icon_var.set('Pushpins')
icon_var_list.append('Pushpins')
icon_lb = tk.Label(window, text='ICON ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer, icon_lb,
                                               True)
icon_value_lb = tk.Label(window, text='Icon type ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               icon_value_lb, True)
icon_menu = tk.OptionMenu(window, icon_var, 'Directions', 'Paddles (teardrop)', 'Paddles (square)', 'Pushpins',
                          'Shapes', 'Other icons')
# icon_menu.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                               icon_menu, True)

specific_icon_var.set('red')
specific_icon_var_list.append('red')
specific_icon_value_lb = tk.Label(window, text='Icon sub-type') # 'Select type of ' + str(icon_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate,
                                               y_multiplier_integer, specific_icon_value_lb, True)
icon_menu_values = ['blue', 'green', 'light_blue', 'pink', 'purple', 'red', 'white', 'yellow']
specific_icon_menu = tk.OptionMenu(window, specific_icon_var, *icon_menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400,
                                               y_multiplier_integer, specific_icon_menu, True)

image_lb = tk.Label(window)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 650, y_multiplier_integer,
                                               image_lb, False)

y_multiplier_integer_save = y_multiplier_integer - 1


def display_icon_image(pic_url, y_multiplier_integer_save):
    import IO_internet_util
    if not IO_internet_util.check_internet_availability_warning("Google Earth Pro"):
        return
    my_page = urlopen(pic_url)
    my_picture = io.BytesIO(my_page.read())
    pil_img = Image.open(my_picture)
    # The (25, 25) is (height, width)
    pil_img = pil_img.resize((25, 25), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(pil_img)
    image_lb = tk.Label(window, image=tk_img)
    # display only if the Select type of icon has a value
    if specific_icon_var.get() != '':
        image_lb.image = tk_img
    else:
        image_lb.image = ''
    image_lb.pack(padx=1, pady=1)
    GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 650, y_multiplier_integer_save, image_lb, False)

# image_lb.config(state='normal')

def update_specific_icon_menu(icon_var, specific_icon_menu, y_multiplier_integer_save, *args):
    m = specific_icon_menu["menu"]
    m.delete(0, "end")
    icon_menu_values = []
    if icon_var.get() == 'Directions':
        icon_menu_values = ['North (track 0)', 'Northeast (track 1)',
                            'Northeast (track 2)', 'Northeast (track 3)', 'East (track 4)',
                            'Southeast (track 5)', 'Southeast (track 6)', 'Southeast (track 7)',
                            'South (track 8)', 'Southwest (track 9)', 'Southwest (track 10)',
                            'Southwest (track 11)', 'West (track 12)', 'Northwest (track 13)',
                            'Northwest (track 14)', 'Northwest (track 15)']
    elif icon_var.get() == 'Paddles (teardrop)':
        icon_menu_values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                            'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                            'go-sign(green)', 'pause-sign(yellow)', 'stop-sign(red)', 'blue-blank', 'blue-circle',
                            'blue-diamond', 'blue-square', 'blue-stars', 'green-blank', 'green-circle', 'green-diamond',
                            'green-square', 'green-stars', 'light-blue-blank', 'light-blue-circle',
                            'light-blue-diamond', 'light-blue-square', 'light-blue-stars', 'pink-blank', 'pink-circle',
                            'pink-diamond', 'pink-square', 'pink-stars', 'purple-blank', 'purple-circle',
                            'purple-diamond', 'purple-square', 'purple-stars', 'red-blank', 'red-circle', 'red-diamond',
                            'red-square', 'red-stars', 'white-blank', 'white-circle', 'white-diamond', 'white-square',
                            'white-stars', 'yellow-blank', 'yellow-circle', 'yellow-diamond', 'yellow-square',
                            'yellow-stars', 'orange-blank', 'orange-circle', 'orange-diamond', 'orange-square',
                            'orange-stars']
    elif icon_var.get() == 'Paddles (square)':
        icon_menu_values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'go-sign(green)', 'pause-sign(yellow)',
                            'stop-sign(red)', 'blue-blank', 'blue-circle', 'blue-diamond', 'blue-square', 'blue-stars',
                            'green-blank', 'green-circle', 'green-diamond', 'green-square', 'green-stars',
                            'purple-blank', 'purple-circle', 'purple-diamond', 'purple-square', 'purple-stars',
                            'red-blank', 'red-circle', 'red-diamond', 'red-square', 'red-stars', 'white-blank',
                            'white-circle', 'white-diamond', 'white-square', 'white-stars', 'yellow-blank',
                            'yellow-circle', 'yellow-diamond', 'yellow-square', 'yellow-stars']
    elif icon_var.get() == 'Pushpins':
        icon_menu_values = ['blue', 'green', 'light_blue', 'pink', 'purple', 'red', 'white', 'yellow']
    elif icon_var.get() == 'Shapes':
        icon_menu_values = ['airports', 'arrow-reverse', 'arrow', 'arts', 'bars', 'broken_link', 'bus', 'cabs',
                            'camera', 'campfire', 'campground', 'capital_big', 'capital_big_highlight', 'capital_small',
                            'capital_small_highlight', 'caution', 'church', 'coffee', 'convenience', 'cross-hairs',
                            'cross-hairs_highlight', 'cycling', 'dining', 'dollar', 'donut', 'earthquake',
                            'electronics', 'euro', 'falling_rocks', 'ferry', 'firedept', 'fishing', 'flag', 'forbidden',
                            'gas_stations', 'golf', 'grocery', 'heliport', 'highway', 'hiker', 'homegardenbusiness',
                            'horsebackriding', 'hospitals', 'info-i', 'info', 'info_circle', 'lodging', 'man', 'marina',
                            'mechanic', 'motorcycling', 'mountains', 'movies', 'open-diamond', 'parking_lot', 'parks',
                            'pharmacy_rx', 'phone', 'picnic', 'placemark_circle', 'placemark_circle_highlight',
                            'placemark_square', 'placemark_square_highlight', 'play', 'poi', 'police', 'polygon',
                            'post_office', 'rail', 'ranger_station', 'realestate', 'road_shield1', 'road_shield2',
                            'road_shield3', 'ruler', 'sailing', 'salon', 'schools', 'shaded_dot', 'shopping', 'ski',
                            'snack_bar', 'square', 'star', 'subway', 'swimming', 'target', 'terrain', 'toilets',
                            'trail', 'tram', 'triangle', 'truck', 'volcano', 'water', 'webcam',
                            'wheel_chair_accessible', 'woman', 'yen', 'sunny', 'partly_cloudy', 'snowflake_simple',
                            'rainy', 'thunderstorm']
    for s in icon_menu_values:
        m.add_command(label=s, command=lambda value=s: specific_icon_var.set(value))
        specific_icon_menu = tk.OptionMenu(window, specific_icon_var, *icon_menu_values)
    pic_url = GIS_Google_pin_util.pin_icon_select(icon_var.get(), specific_icon_var.get())
    display_icon_image(pic_url, y_multiplier_integer_save)

specific_icon_var.trace('w', callback=lambda x, y, z: update_specific_icon_menu(icon_var, specific_icon_menu,
                                                                                y_multiplier_integer_save))


def activate_specific_icon(icon_var, specific_icon_value_lb, specific_icon_menu, *args):
    specific_icon_value_lb.config(text='Icon sub-type ') # + str(icon_var.get()))
    specific_icon_var.set('')
    update_specific_icon_menu(icon_var, specific_icon_menu, y_multiplier_integer_save)


icon_var.trace('w',
               callback=lambda x, y, z: activate_specific_icon(icon_var, specific_icon_value_lb, specific_icon_menu,
                                                               y_multiplier_integer_save))

pic_url = GIS_Google_pin_util.pin_icon_select(icon_var.get(), specific_icon_var.get())

##
# display_icon_image(pic_url, y_multiplier_integer_save)

name_var.set(0)
name_var_list.append(0)
name_checkbox = tk.Checkbutton(window, text='NAME ', variable=name_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               name_checkbox, True)

scale_var_list.append(1)

scale_var.set(1)
scale_lb = tk.Label(window, text='Scale ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               scale_lb, True)
scale_entry = tk.Entry(window, width=4, textvariable=scale_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 50, y_multiplier_integer,
                                               scale_entry, True)

opacity_lb = tk.Label(window, text='Opacity ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                               opacity_lb, True)
opacity_entry = tk.Entry(window, width=4, textvariable=opacity_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 170, y_multiplier_integer,
                                               opacity_entry, True)

color_var.set(0)
color_var_list.append(0)
color_checkbox = tk.Checkbutton(window, text='Color ', variable=color_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate, y_multiplier_integer,
                                               color_checkbox, True)

color_style_var_list.append("")
color_lb = tk.Label(window, text='RGB color code ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 400, y_multiplier_integer,
                                               color_lb, True)
color_entry = tk.Entry(window, width=10, textvariable=color_style_var)
color_entry.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 500, y_multiplier_integer,
                                               color_entry)


def activate_color_palette(*args):
    if color_var.get() == 1:
        style = ttk.Style(window)
        style.theme_use('clam')
        color_list = askcolor((255, 255, 0), window)
        color_style = color_list[0]
        color_style_var.set(color_style)


color_var.trace('w', activate_color_palette)


def activate_name_options(*args):
    if name_var.get() == 1:
        scale_entry.configure(width=4, state='normal')
        # opacity_entry.configure(width=4, state='normal')
        opacity_entry.configure(width=4, state='disabled')
        color_checkbox.config(state='normal')
    # users shoud not be able to mess with the RGB color scheme; always disabled as set above
    # color_entry.configure(state='normal')
    else:
        scale_entry.configure(width=4, state='disabled')
        opacity_entry.configure(width=4, state='disabled')
        color_checkbox.config(state='disabled')


# color_entry.configure(state='disabled')
name_var.trace('w', activate_name_options)
activate_name_options()

description_var.set(0)
description_var_list.clear()
description_checkbox = tk.Checkbutton(window, text='DESCRIPTION ', variable=description_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               description_checkbox, True)

description_csv_field_var_list.clear()
field_lb = tk.Label(window, text='Select csv field ')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               field_lb, True)
if menu_values != '':
    description_csv_field_menu = tk.OptionMenu(window, description_csv_field_var, *menu_values)
else:
    description_csv_field_menu = tk.OptionMenu(window, description_csv_field_var, menu_values)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu + 100, y_multiplier_integer,
                                               description_csv_field_menu, True)


def changed_GIS_filename(*args):
    global errorDisplayed, inputError
    errorDisplayed=True
    # check that input file is a CoNLL table;
    #	many options are NOT available when working with a CoNLL table
    if (GUI_util.input_main_dir_path.get()!='') or (not GUI_util.inputFilename.get().endswith('.csv')):
        inputError=True
        return

    inputIsCoNLL = CoNLL_util.check_CoNLL(inputFilename.get(), True)
    if inputIsCoNLL == True:
        reminders_util.checkReminder(scriptName, reminders_util.title_options_Google_Earth_CoNLL,
                                         reminders_util.message_Google_Earth_CoNLL, True)

        # location_var.set('NER') #moved at the end or it gets reset below
        location_field.config(state='disabled')
        icon_csv_field_var.set('')
        description_csv_field_var.set('')
        csv_field_forGroups_menu.config(state='disabled')
        # name_checkbox.config(state='disabled')
        # description_checkbox.config(state='disabled')
        description_csv_field_menu.config(state='disabled')
    else:
        # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
        if IO_csv_util.rename_header(inputFilename.get(), "Word", "Location") == False:
            inputError = True
            return
        GUI_util.run_button.configure(state='normal')
        location_var.set('Location')
        location_field.config(state='normal')
        icon_csv_field_var.set('')
        description_csv_field_var.set('')
        csv_field_forGroups_menu.config(state='normal')
        name_checkbox.config(state='normal')
        description_checkbox.config(state='normal')
        description_csv_field_menu.config(state='normal')

    menu_values = IO_csv_util.get_csvfile_headers(inputFilename.get())

    # must change all 3 widgets where menus must be updated after changing the filename
    m = date_field["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: date_var.set(value))

    m = location_field["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: location_var.set(value))

    m = csv_field_forGroups_menu["menu"]
    m.delete(0, "end")
    for s in menu_values:
        m.add_command(label=s, command=lambda value=s: icon_csv_field_var.set(value))

    m = description_csv_field_menu["menu"]
    m.delete(0, "end")
    for s in menu_values:
        if 'Sentence' == s:
            description_csv_field_var.set('Sentence')
        m.add_command(label=s, command=lambda value=s: description_csv_field_var.set(value))

    if 'date' in str(menu_values).lower():
        date_var.set('Date')
    else:
        date_var.set('')

    if 'location' in str(menu_values).lower():
        location_var.set('Location')
    else:
        location_var.set('')

    if description_csv_field_var.get()=='':
        if 'location' in str(menu_values).lower():
            description_var.set(1)
            description_csv_field_var.set('Location')
        else:
            description_var.set(0)
            description_csv_field_var.set('')
    if inputIsCoNLL == True:
        location_var.set('NER')
inputFilename.trace('w', changed_GIS_filename)
# GUI_util.input_main_dir_path.trace('w', changed_GIS_filename)

# changed_GIS_filename() added at the end after all widgets have been displayed

italic_var_list.append(1)
bold_var_list.append(1)

bold_var.set(1)
bold_checkbox = tk.Checkbutton(window, text='Bold ', variable=bold_var, onvalue=1, offvalue=0)
bold_checkbox.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.setup_IO_brief_coordinate, y_multiplier_integer,
                                               bold_checkbox, True)

italic_var.set(1)
italic_checkbox = tk.Checkbutton(window, text='Italic ', variable=italic_var, onvalue=1, offvalue=0)
italic_checkbox.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.IO_configuration_menu+400, y_multiplier_integer,
                                               italic_checkbox)

def activate_description_options(*args):
    if description_var.get() == 1:
        description_csv_field_menu.configure(state='normal')
        bold_checkbox.configure(state='normal')
        italic_checkbox.configure(state='normal')
    else:
        description_csv_field_var_list.clear
        description_csv_field_menu.configure(state='disabled')
        description_csv_field_var.set('')
        bold_checkbox.configure(state='disabled')
        italic_checkbox.configure(state='disabled')

description_var.trace('w', activate_description_options)
activate_description_options()

def activate_description(*args):
    if len(description_csv_field_var.get()) > 0:
        bold_checkbox.config(state='normal')
        italic_checkbox.config(state='normal')
    else:
        bold_checkbox.config(state='disabled')
        italic_checkbox.config(state='disabled')

description_csv_field_var.trace('w', activate_description)
activate_description()


def activate_group_options(*args):
    if group_var.get() == 1 and len(icon_var_list) == int(group_number_var.get()) and len(
            specific_icon_var_list) == int(group_number_var.get()):
        add_group_button.config(state='normal')
    else:
        add_group_button.config(state='disabled')
    reset_group_button.config(state='normal')


specific_icon_var.trace('w', activate_group_options)
group_var.trace('w', activate_group_options)
activate_group_options()


def csv_field_forGroups_menu_state(*args):
    if group_number_var.get() > 1:
        csv_field_forGroups_menu.config(state='disabled')
    group_values_entry.configure(state='disabled')
    group_label_entry.configure(state='disabled')
    group_values_entry.configure(state='normal')
    group_label_entry.configure(state='normal')


group_number_var.trace('w', csv_field_forGroups_menu_state)
csv_field_forGroups_menu_state()


def group_values_entry_var_list_update(*args):
    if len(group_values_entry_var.get()) > 0:
        if len(group_values_entry_var_list) >= int(group_number_var.get()):
            del group_values_entry_var_list[-1]  # delete the last selected if there is a new currently selected chart
        group_values_entry_var_list.append(group_values_entry_var.get())
    # print("group_values_entry_var_list",group_values_entry_var_list)
    else:
        if len(group_values_entry_var_list) >= int(group_number_var.get()):
            del group_values_entry_var_list[-1]  # delete the last selected if there is a new currently selected chart
        group_values_entry_var_list.append(group_values_entry_var.get())


# print("group_values_entry_var_list",group_values_entry_var_list)
group_values_entry_var.trace('w', group_values_entry_var_list_update)
group_values_entry_var_list_update()


def group_label_entry_var_list_update(*args):
    if len(group_label_entry_var.get()) > 0:
        if len(group_label_entry_var_list) >= int(group_number_var.get()):
            del group_label_entry_var_list[-1]  # delete the last selected if there is a new currently selected chart
        group_label_entry_var_list.append(group_label_entry_var.get())
    # print("group_label_entry_var_list",group_label_entry_var_list)
    else:
        if len(group_label_entry_var_list) >= int(group_number_var.get()):
            del group_label_entry_var_list[-1]  # delete the last selected if there is a new currently selected chart
        group_label_entry_var_list.append(group_label_entry_var.get())


# print("group_label_entry_var_list",group_label_entry_var_list)
group_label_entry_var.trace('w', group_label_entry_var_list_update)
group_label_entry_var_list_update()


def icon_var_list_update(*args):
    if len(icon_var.get()) > 0:
        if len(icon_var_list) >= int(group_number_var.get()):
            del icon_var_list[-1]  # delete the last selected if there is a new currently selected chart
        icon_var_list.append(icon_var.get())


# print("icon_var_list",icon_var_list)
icon_var.trace('w', icon_var_list_update)
icon_var_list_update()


def specific_icon_var_list_update(*args):
    if len(specific_icon_var.get()) > 0:
        if len(specific_icon_var_list) >= int(group_number_var.get()):
            del specific_icon_var_list[-1]  # delete the last selected if there is a new currently selected chart
        specific_icon_var_list.append(specific_icon_var.get())


# print("specific_icon_var_list",specific_icon_var_list)
specific_icon_var.trace('w', specific_icon_var_list_update)
specific_icon_var_list_update()


def name_var_list_update(*args):
    if len(name_var_list) >= int(group_number_var.get()):
        del name_var_list[-1]  # delete the last selected if there is a new currently selected chart
    name_var_list.append(name_var.get())


# print("name_var_list",name_var_list)
name_var.trace('w', name_var_list_update)
name_var_list_update()


def scale_var_list_update(*args):
    if len(scale_var.get()) > 0:
        if len(scale_var_list) >= int(group_number_var.get()):
            del scale_var_list[-1]  # delete the last selected if there is a new currently selected chart
        scale_var_list.append(scale_var.get())


# print("scale_var_list",scale_var_list)
scale_var.trace('w', scale_var_list_update)
scale_var_list_update()


def color_var_list_update(*args):
    if len(color_var_list) >= int(group_number_var.get()):
        del color_var_list[-1]  # delete the last selected if there is a new currently selected chart
    color_var_list.append(color_var.get())


# print("color_var_list",color_var_list)
color_var.trace('w', color_var_list_update)
color_var_list_update()


def color_style_var_list_update(*args):
    if len(color_style_var_list) >= int(group_number_var.get()):
        del color_style_var_list[-1]  # delete the last selected if there is a new currently selected chart
    color_style_var_list.append(color_style_var.get())


# print("color_style_var_list",color_style_var_list)
color_style_var.trace('w', color_style_var_list_update)
color_style_var_list_update()


def description_var_list_update(*args):
    if len(description_var_list) >= int(group_number_var.get()):
        del description_var_list[-1]  # delete the last selected if there is a new currently selected chart
    if description_var.get()!=0:
        description_var_list.append(description_var.get())


# print("description_var_list",description_var_list)
description_var.trace('w', description_var_list_update)
description_var_list_update()


def description_csv_field_var_list_update(*args):
    if len(description_csv_field_var.get()) > 0:
        if len(description_csv_field_var_list) >= int(group_number_var.get()):
            del description_csv_field_var_list[
                -1]  # delete the last selected if there is a new currently selected chart
        description_csv_field_var_list.append(description_csv_field_var.get())


# print("description_csv_field_var_list",description_csv_field_var_list)
description_csv_field_var.trace('w', description_csv_field_var_list_update)
description_csv_field_var_list_update()


def italic_var_list_update(*args):
    if len(italic_var_list) >= int(group_number_var.get()):
        del italic_var_list[-1]  # delete the last selected if there is a new currently selected chart
    italic_var_list.append(italic_var.get())


# print("italic_var_list",italic_var_list)
italic_var.trace('w', italic_var_list_update)
italic_var_list_update()


def bold_var_list_update(*args):
    if len(bold_var_list) >= int(group_number_var.get()):
        del bold_var_list[-1]  # delete the last selected if there is a new currently selected chart
    bold_var_list.append(bold_var.get())


# print("bold_var_list",bold_var_list)
bold_var.trace('w', bold_var_list_update)
bold_var_list_update()

heat_map_var = tk.IntVar()
heat_map_var.set(1)
heat_map_checkbox = tk.Checkbutton(window, text='Heat map (via Google Maps)', variable=heat_map_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window,GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               heat_map_checkbox, True)

videos_lookup = {'No videos available':''}
videos_options='No videos available'

TIPS_lookup = {'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',
               "Geocoding": "TIPS_NLP_GIS_Geocoding.pdf",
               "Geocoding: How to Improve Nominatim":"TIPS_NLP_GIS_Geocoding Nominatim.pdf",
               "Google Earth Pro": "TIPS_NLP_GIS_Google Earth Pro.pdf",
               "Google Earth Pro KML Options": "TIPS_NLP_GIS_Google Earth Pro KML options.pdf",
               "HTML": "TIPS_NLP_GIS_Google Earth Pro HTML.pdf",
               "Google Earth Pro Icon": "TIPS_NLP_GIS_Google Earth Pro Icon.pdf",
               "Google Earth Pro Description": "TIPS_NLP_GIS_Google Earth Pro Description.pdf"}
TIPS_options = 'utf-8 encoding', 'Geocoding', 'Geocoding: How to Improve Nominatim', 'Google Earth Pro', 'HTML', 'Google Earth Pro Icon', 'Google Earth Pro Description'


# add all the lines to the end to every special GUI
# change the last item (message displayed) of each line of the function y_multiplier_integer = help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      'Please, select an input csv file for the GIS Geogle Earth Pro script. Two types of csv files are acceptable:\n  1. a file containing a first column of location names that need to be geocoded (e.g., New York);\n2.  a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script parsers_annotators_main.py (the script parses text documents using the Stanford CoreNLP parser).')
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                      GUI_IO_util.msg_IO_setup)

    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the column containing the location names (e.g., New York) to be geocoded and mapped.\n\nTHE OPTION IS NOT AVAILABLE WHEN SELECTING A CONLL INPUT CSV FILE. NER IS THE COLUMN AUTOMATICALLY USED WHEN WORKING WITH A CONLL FILE IN INPUT.\n\nWhen GIS distance is to be computed, the column refers to the FIRST set of location names. In this case, you can use the second dropdown menu to select the column containing the second set of location names." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "\n\nUsing the dropdown menu, if a date is present, select the column containing the date and the date format. If a date is present, it will be used to construct dynamic GIS models." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick the checkbox if you wish to use different pins for different values in a field of the csv file.\n\nSeveral options become available after ticking the checkbox. In particular, you will be able to:\n\nselect the field in the csv file whose selected values will be used for the same icon;\nenter the comma-separated values that should all share the same icon (e.g., 'communists, socialists, maximalists, anarchists, protesters, demonstartors, trade unions' in a study of the rise of Italian fascism);\noptionally, enter a label for the group (e.g., 'the left'), otherwise leave blank.\n\nSeveral groups can be added by clicking on the + button. Again, in a study of the rise of Italian fascism, a second group may have values 'fascists, right-wingers, nationalists' and, optionally, a group label 'the right'.\n\nFor 'the left' group you may then select a red pin and a black pin for 'the right'.\n\ncsv field value NOT included in any of the two groups (in this specific example), should be added as a third group, leaving blank both fields for group values and group label and then selecting a different icon not associated to any previously defined groups (e.g., a white pin).\n\nWhen group labels are left blank, the labels will be set by default to Group 1, Group 2, Group 3, ...\n\nGroup labels and group values will be automatically displayed in the DESCRIPTION field, if the DESCRIPTION checkbox is ticked."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, using the dropdown menu, select the type of pin you wish to use on the map.\n\nSeveral options become available after selecting the basic type of icon pin." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, enter various types of information required for the pin NAME option.\n\nNAME refers to the label to be displayed on the map for each coordinates point. KEEP IN MIND THAT WHEN THE MAP CONTAINS A LARGE NUMBER OF LOCATIONS, DISPLAYING LOCATIONS WITH PINS AND NAMES MAY RESULT IN A VERY 'BUSY' MAP HARD TO READ.\n\nSCALE refers to the size of the label (NAME) to be displayed. Default value 1, but .5 or 2, 3,... acceptable. Try out different values!\n\nOPACITY refers to the transparency of the label displayed (i.e., how much you can see of the map behind the NAME label). Default value 100%. Enter a value (0-100) for the opacity of the label (NAME) to be displayed. Try out different opacity values!\n\nCOLOR refers to the color for the label (NAME) to be displayed on the map for each coordinates point."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, enter various types of information required for the pin DESCRIPTION option. DESCRIPTION contains the information that will be displayed when clicking on a pin.\n\nTHE OPTION IS NOT AVAILABLE WHEN SELECTING A CONLL INPUT CSV FILE. FOR CONLL FILES, THE DESCRIPTION FIELD IS AUTOMATICALLY COMPUTED, DISPLAYING THE LOCATION, THE FILENAME, AND THE SENTENCE WHERE THE LOCATION IS MENTIONED.\n\nSelect the field name from the input csv file whose values will be displayed when clicking on a pin on the map.\n\nTick the bold checkbox if you want to display in BOLD the field name.\n\nTick the italic checkbox if you want to display in ITALIC the field name."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  "Please, tick ther checkbox if you wish to produce a heat map using Google Maps.\n\n\MUST HAVE a GOOGLE MAPS API KEY."+ GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
                                  GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer -1

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

# change the value of the readMe_message
readMe_message = "This Python 3 script relies on the Python Geopy library to geocode locations, i.e., finding a locaton latitude and longitude so that it can be mapped using Google Earth Pro for pin maps and Google Maps for heat maps.\n\nFOR THESE OPTIONS YOU MUST HAVE GOOGLE API KEYS.\n\nYOU MUST DOWNLOAD AND INSTALL THE FREEWARE GOOGLE EARTH PRO at https://www.google.com/earth/versions/#download-pro.\n\nIn INPUT, the script can take:" \
    "\n   1. A CoNLL table produced by Stanford CoreNLP parser and use the NER (Named Entity Recognition) LOCATION, CITY, STATE-OR-PROVINCE, and COUNTRY values for geocoding;" \
    "\n   2. a csv file, however created (e.g., CoreNLP NER annotator), containing a list of locations to be geocoded (e.g., Chicago);" \
    "\n   3. a csv file that contains geocoded location names with latitude and longitude.\n\ncsv files, except for the CoNLL table, must have a column header 'Location' (the header 'Word' from the CoreNLP NER annotator will be converted automatically to 'Location'), two column headers 'Latitude' and 'Longitude'.\n\nIf a column header 'Date' is present, the field will be used to compute dynamic Google Earth Pro maps.\n\nWhen a CoNLL file is used, if the file contains a date, the script can automatically process a wide variety of date formats: day, month, and year in numeric form and in different order, year in 2 or 4 digit form, and month in numeric or alphabetic form and, in the latter case, in 3 or full characters (e.g., Jan or January).\n\nThe current release of the script relies on Nominatim, rather than Google, as the default geocoder tool. If you wish to use Google for geocoding, please, use the GIS_main script.\n\nThe script prepares the kml file to be displayed in Google Earth Pro.\n\nThe script can also be used to compute geographic distances between locations, in both kilometers and miles, by either geodesic distance or by great circle distance. Distances will be visualized in Excel charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

display_icon_image(pic_url, y_multiplier_integer_save)

GUI_util.window.mainloop()

# 2 IO_configuration_menu + 50 400
# 4 IO_configuration_menu + 100 480
# 1 IO_configuration_menu + 140 520
# IO_configuration_menu + 400 750
# 1 IO_configuration_menu + 550 850
# 3 IO_configuration_menu + 650 950
# 1 IO_configuration_menu + 750 1050
# 1 IO_configuration_menu + 850 1150
