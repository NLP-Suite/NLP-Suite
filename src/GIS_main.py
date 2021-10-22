# Written by Roberto Franzosi May, September 2020
# Written by Roberto Franzosi May, September 2020
# Written by Roberto Franzosi September 2021

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS",['os','tkinter','pandas','subprocess'])==False:
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
import Stanford_CoreNLP_annotator_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(inputFilename,
        inputDir,
        outputDir,
        openOutputFiles,
        createExcelCharts,
        csv_file,
        encoding_var,
        extract_date_from_text_var,
        extract_date_from_filename_var,
        date_format,
        date_separator_var,
        date_position_var,
        memory_var,
        NER_extractor,
        location_menu,
        geocode_locations,
        map_locations,
        GIS_package_var,
        GIS_package2_var):

    filesToOpen = []
    locationColumnName=''

    if NER_extractor==False and geocode_locations_var==False and GIS_package_var=='':
        mb.showwarning("Warning",
                       "No options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if display_csv_file_options()==True:
         return
    if display_txt_file_options()==True:
         return

    if csv_file != '':
        inputFilename=csv_file

    geocoder = 'Nominatim'
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

        reminders_util.checkReminder(config_filename, reminders_util.title_options_geocoder,
                                     reminders_util.message_geocoder, True)

        locations = ''

    # START PROCESSING ---------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # NER extraction via CoreNLP

    # checking for txt: NER=='LOCATION', provide a csv output with column: [Locations]
    if NER_extractor and csv_file=='':

        NERs = ['COUNTRY', 'STATE_OR_PROVINCE', 'CITY']

        locations = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                outputDir, openOutputFiles, createExcelCharts, 'NER', False,
                                                                memory_var,
                                                                NERs=NERs,
                                                                extract_date_from_text_var=extract_date_from_text_var,
                                                                extract_date_from_filename_var=extract_date_from_filename_var,
                                                                date_format=date_format,
                                                                date_separator_var=date_separator_var,
                                                                date_position_var=date_position_var)

        if len(locations)==0:
            mb.showwarning("No locations","There are no NER locations to be geocoded and mapped in the selected input txt file.\n\nPlease, select a different txt file and try again.")
            return
        else:
            NER_outputFilename = locations[0]

        if extract_date_from_text_var or extract_date_from_filename_var:
            datePresent = True
            # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
            df = pd.read_csv(locations[0]).rename(columns={"Word": "Location"})
            # if IO_csv_util.rename_header(inputFilename, "Word", "Location") == False:
            #     return
            location_menu_var.set('Location')
            # 'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID', 'Document'],
            # Fill in empty dates with most recent valid date
            saved_date = ""
            for index, row in df.iterrows():
                if df['Date'][index] != "":
                    # We found a valid date, save it
                    saved_date = df['Date'][index]
                else:
                    df['Date'][index] = saved_date
        else:
            # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
            # if IO_csv_util.rename_header(inputFilename, "Word", "Location") == False:
            #     return
            df = pd.read_csv(locations[0]).rename(columns={"Word": "Location"})
            location_menu_var.set('Location')
            # 'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID', 'Document'],

        # Clean dataframe, remove any 'DATE' or non-location rows
        del_list = []
        for index, row in df.iterrows():
            if df['NER Value'][index] not in ['COUNTRY','STATE_OR_PROVINCE','CITY','LOCATION']:
                del_list.append(index)
        df = df.drop(del_list)
        df.to_csv(NER_outputFilename, index=False)
        csv_file_var.set(NER_outputFilename)
        filesToOpen.append(NER_outputFilename)
        locationColumnName = 'Location'
    else:
        NER_outputFilename=csv_file_var.get()
        locationColumnName = location_menu #RF

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # running the GIS options
    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    if GIS_package_var == 'Google Earth Pro & Google Maps' or GIS_package_var == 'Google Maps' or GIS_package_var == 'Google Earth Pro':
        datePresent = False
        # if GIS_package_var=='Google Earth Pro': # check installation

        # locationColumnName where locations to be geocoded (or geocoded) are stored in the csv file;
        #   any changes to the columns will result in error
        out_file, kmloutputFilename = GIS_pipeline_util.GIS_pipeline(GUI_util.window, config_filename,
                        NER_outputFilename,outputDir,
                        'Nominatim', GIS_package_var,
                        datePresent,
                        locationColumnName,
                        encoding_var,
                        0, 1, [''], [''],# group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                        ['Pushpins'], ['red'], # icon_var_list, specific_icon_var_list,
                        [0], ['1'], [0], [''], # name_var_list, scale_var_list, color_var_list, color_style_var_list,
                        [1],[1]) # bold_var_list, italic_var_list)

        if len(out_file)>0:
            filesToOpen.extend(out_file)
        if kmloutputFilename!='':
            filesToOpen.append(kmloutputFilename)
        if len(filesToOpen)>0:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
    else:
        if GIS_package_var!='':
            mb.showwarning("Option not available","The " + GIS_package_var + " option is not available yet.\n\nSorry! Please, check back soon...")
            return


#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
                            GUI_util.input_main_dir_path.get(),
                            GUI_util.output_dir_path.get(),
                            GUI_util.open_csv_output_checkbox.get(),
                            GUI_util.create_Excel_chart_output_checkbox.get(),
                            csv_file_var.get(),
                            encoding_var.get(),
                            extract_date_from_text_var.get(),
                            extract_date_from_filename_var.get(),
                            date_format.get(),
                            date_separator_var.get(),
                            date_position_var.get(),
                            memory_var.get(),
                            NER_extractor_var.get(),
                            location_menu_var.get(),
                            geocode_locations_var.get(),
                            map_locations_var.get(),
                            GIS_package_var.get(),
                            GIS_package2_var.get())

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

# the GUIs are all setup to run with a brief I/O display or full display (with filename, inputDir, outputDir)
#   just change the next statement to True or False IO_setup_display_brief=True
IO_setup_display_brief=True
GUI_width=1300
GUI_height=600 # height of GUI with full I/O display

if IO_setup_display_brief:
    GUI_height = GUI_height - 80
    y_multiplier_integer = GUI_util.y_multiplier_integer  # IO BRIEF display
    increment=0 # used in the display of HELP messages
else: # full display
    # GUI CHANGES add following lines to every special GUI
    # +3 is the number of lines starting at 1 of IO widgets
    # y_multiplier_integer=GUI_util.y_multiplier_integer+2
    y_multiplier_integer = GUI_util.y_multiplier_integer + 2  # IO FULL display
    increment=2

GUI_size = str(GUI_width) + 'x' + str(GUI_height)

GUI_label='Graphical User Interface (GUI) for GIS (Geographic Information System) Pipeline from Text to Map'
config_filename='GIS-config.txt'
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
config_option=[0,2,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename,IO_setup_display_brief)

csv_file_var= tk.StringVar()

encoding_var=tk.StringVar()
memory_var = tk.IntVar()

extract_date_from_text_var= tk.IntVar()
extract_date_from_filename_var= tk.IntVar()
date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

location_menu_var=tk.StringVar()
NER_extractor_var=tk.IntVar()
geocode_locations_var=tk.IntVar()
geocoder_var=tk.StringVar()
country_bias_var=tk.StringVar()
GIS_package_var=tk.StringVar()
GIS_package2_var=tk.IntVar()
map_locations_var=tk.IntVar()

def clear(e):
    csv_file_var.set('')
    encoding_var.set('utf-8')
    NER_extractor_var.set(1)
    NER_extractor_checkbox.config(state='disabled')
    location_menu_var.set('')
    geocode_locations_var.set(1)
    geocode_locations_checkbox.configure(state='normal')
    map_locations_var.set(1)
    GIS_package_var.set('Google Earth Pro & Google Maps')
    geocoder_var.set('Nominatim')
    country_bias_var.set('')
    GUI_util.clear("Escape")
window.bind("<Escape>", clear)

def display_txt_file_options(*args):
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
                extract_date_from_text_checkbox.config(state='normal')
                extract_date_from_filename_checkbox.config(state='normal')
                NER_extractor_var.set(1)
                NER_extractor = True
                NER_extractor_checkbox.configure(state='disabled')
                country_bias.configure(state='normal')
                geocode_locations_var.set(1)
                geocode_locations = True
                map_locations_var.set(1)
                map_locations = True
        return cannotRun
inputFilename.trace('w',display_txt_file_options)
input_main_dir_path.trace('w',display_txt_file_options)



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
    if GIS_package2_var.get() == False:
        GIS_package_var.set('Google Earth Pro & Google Maps')

    # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
    if IO_csv_util.rename_header(csv_file_var.get(), "Word", "Location")==False:
        return
    location_menu_var.set('Location')
    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(
        csv_file_var.get())
    if inputIsGeocoded:
        geocode_locations_var.set(0)
        geocode_locations_checkbox.configure(state='disabled')
        geocode_locations=0
        geocode_locations_checkbox.config(state='disabled')

    if map_locations_var.get()==False and inputIsGeocoded==True:
        mb.showwarning(title='Warning',
                       message="The 'MAP locations' checkbox is ticked off with a csv file of geocoded locations in input.\n\nThere is nothing to do for the GIS pipeline...")
        cannotRun = True
        return cannotRun

    location_field.config(state='normal')

    NER_extractor_var.set(0)
    NER_extractor=False
    if 'Location' in headers and not 'Latitude' in headers:
        geocode_locations_var.set(1)
        geocode_locations_checkbox.configure(state='disabled')
        location_menu_var.set('Location') #RF
        location_menu='Location' #RF
    elif 'Latitude' in headers and 'Longitude' in headers:
        geocode_locations_var.set(0)
        geocode_locations_checkbox.configure(state='disabled')
        geocode_locations=False
        location_menu_var.set('Location') #RF
        location_menu='Latitude'
    elif 'postag' and 'deprel' in str(headers).lower():
        location_menu_var.set('Location') #RF
        location_menu='Location' #RF
        # location_menu='NER' #RF
        # Word is the header from Stanford CoreNLP NER annotator
    elif not 'Location' in headers and not 'Word' in headers:
        mb.showwarning(title='Warning',
                       message="The selected input csv file does not contain the word 'Location' in its headers.\n\nThe GIS algorithms expect in input either\n   1. txt file(s) from which to extract locations (via Stanford CoreNLP NER annotator) to be geocoded and mapped;\n   2. a csv file\n      a. with a column of locations (with header 'Location') to be geocoded and mapped;\n      b. a csv file with a column of locations (with header 'Location'; the header 'Word' from the CoreNLP NER annotator will be converted automatically to 'Location')';\n      c. already geocoded and to be mapped (this file will also contain latitudes and longitudes, with headers 'Latitude' and 'Longitude').\n\nPlease, select the appropriate input csv file and try again. Or simply run the complete pipeline, going from text to maps, with txt file(s) in input.")
        csv_file_var.set('')
        NER_extractor_var.set(1)
        NER_extractor = True
        NER_extractor_checkbox.config(state='disabled')
        #
        # cannotRun = True
        return cannotRun
    else:
        geocode_locations_var.set(1)
        geocode_locations=True
        NER_extractor_var.set(1)
        NER_extractor = True

    if inputIsGeocoded == False: #and fromSelectInputCSV==False
        if location_menu_var.get()=='':
            mb.showwarning(title='Warning',
                           message="You have selected the 'GEOCODE locations' option, but you have not selected the column containing location names.\n\nYou cannot geocode without selecting the column containing locations to be coded.")
            cannotRun=True
            return cannotRun
        elif geocoder_var.get() == '':
            mb.showwarning(title='Warning', message='No geocoder service option selected.\n\nThe GIS script will exit.')
            cannotRun=True
            return cannotRun
        elif geocode_locations_var.get() == False:
            if map_locations_var.get() == True:
                mb.showwarning(title='Warning',
                               message="You have selected the 'MAP locations' option, but the current csv input file is not geocoded and the 'GEOCODE location' widget is unchecked.\n\nYou cannot map without geocoding.")
                # geocode_locations_var.set(1)
                # geocode_locations_checkbox.configure(state='disabled')
                cannotRun=True
                return cannotRun
    else:
        geocode_locations_var.set(0)
        geocode_locations_checkbox.config(state='disabled')

    if inputIsCoNLL == True:
        reminders_util.checkReminder(config_filename, reminders_util.title_options_Google_Earth_CoNLL,
                                     reminders_util.message_Google_Earth_CoNLL, True)

    reminders_util.checkReminder(config_filename, reminders_util.title_options_input_csv_file,
                                 reminders_util.message_input_csv_file, True)


    return cannotRun

def get_csv_file(window,title,fileType,annotate):
    #csv_file_var.set('')
    if csv_file!='':
        initialFolder=os.path.dirname(os.path.abspath(csv_file_var.get()))
    else:
        initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(title = title, initialdir = initialFolder, filetypes = fileType)

    if len(filePath)>0:
        nRecords=IO_csv_util.GetNumberOfRecordInCSVFile(filePath, 'utf-8')
        if nRecords==0:
            mb.showwarning(title='Warning',
                           message="The selected input csv file is empty.\n\nPlease, select a different file and try again.")
            filePath=''
        else:
            csv_file_var.set(filePath)
            display_csv_file_options()
    return filePath

csv_file_button=tk.Button(window, width=GUI_IO_util.select_file_directory_button_width, text='Select INPUT CSV file',command=lambda: get_csv_file(window,'Select INPUT csv file', [("dictionary files", "*.csv")],True))
# csv_file_button.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,csv_file_button,True)

#setup a button to open Windows Explorer on the selected input directory
# current_y_multiplier_integer2=y_multiplier_integer-1
# openInputFile_button  = tk.Button(window, width=3, state='disabled', text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
openInputFile_button  = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='', command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
openInputFile_button.place(x=GUI_IO_util.get_open_file_directory_coordinate(), y=GUI_IO_util.get_basic_y_coordinate()+GUI_IO_util.get_y_step()*y_multiplier_integer)

csv_file=tk.Entry(window, width=130,textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,csv_file)

encoding_lb = tk.Label(window, text='Select encoding type (utf-8 default)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,encoding_lb,True)
encoding_var.set('utf-8')
encodingValue = tk.OptionMenu(window,encoding_var,'utf-8','utf-16-le','utf-32-le','latin-1','ISO-8859-1')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,encodingValue,True)


#memory options

memory_var_lb = tk.Label(window, text='Memory ')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 190,y_multiplier_integer,memory_var_lb,True)

memory_var = tk.Scale(window, from_=1, to=16, orient=tk.HORIZONTAL)
memory_var.pack()
memory_var.set(4)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 270,y_multiplier_integer,memory_var)

extract_date_lb = tk.Label(window, text='Extract date (for dynamic GIS)')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,extract_date_lb,True)

extract_date_from_text_var.set(0)
extract_date_from_text_checkbox = tk.Checkbutton(window, variable=extract_date_from_text_var, onvalue=1, offvalue=0)
extract_date_from_text_checkbox.config(text="From document content")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),
                                               y_multiplier_integer, extract_date_from_text_checkbox, True)

extract_date_from_filename_var.set(0)
extract_date_from_filename_checkbox = tk.Checkbutton(window, variable=extract_date_from_filename_var, onvalue=1, offvalue=0)
extract_date_from_filename_checkbox.config(text="From filename")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 190,
                                               y_multiplier_integer, extract_date_from_filename_checkbox, True)

date_format_lb = tk.Label(window,text='Format ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 320,
                                               y_multiplier_integer, date_format_lb, True)
date_format.set('mm-dd-yyyy')
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')
date_format_menu.configure(width=10,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 380,
                                               y_multiplier_integer, date_format_menu, True)
date_separator_var.set('_')
date_separator_lb = tk.Label(window, text='Character separator ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 510,
                                               y_multiplier_integer, date_separator_lb, True)
date_separator = tk.Entry(window, textvariable=date_separator_var)
date_separator.configure(width=2,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 640,
                                               y_multiplier_integer, date_separator, True)
date_position_var.set(2)
date_position_menu_lb = tk.Label(window, text='Position ')
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 670,
                                               y_multiplier_integer, date_position_menu_lb, True)
date_position_menu = tk.OptionMenu(window,date_position_var,1,2,3,4,5)
date_position_menu.configure(width=1,state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate() + 740,
                                               y_multiplier_integer, date_position_menu)

def check_dateFields(*args):
    if extract_date_from_text_var.get() == 1:
        extract_date_from_filename_checkbox.config(state="disabled")
    else:
        extract_date_from_text_checkbox.config(state="normal")
        extract_date_from_filename_checkbox.config(state="normal")
    if extract_date_from_filename_var.get() == 1:
        extract_date_from_text_checkbox.config(state="disabled")
        date_format_menu.config(state="normal")
        date_separator.config(state='normal')
        date_position_menu.config(state='normal')
    else:
        date_format_menu.config(state="disabled")
        date_separator.config(state='disabled')
        date_position_menu.config(state="disabled")
extract_date_from_text_var.trace('w',check_dateFields)
extract_date_from_filename_var.trace('w',check_dateFields)

NER_extractor_var.set(0)
NER_extractor_checkbox = tk.Checkbutton(window, variable=NER_extractor_var, onvalue=1, offvalue=0)
NER_extractor_checkbox.config(text="EXTRACT locations (via Stanford CoreNLP NER) - Default parameters")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,NER_extractor_checkbox)

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

location_field_lb = tk.Label(window, text='Select the column containing location names')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,location_field_lb,True)
if menu_values!='':
    location_field = tk.OptionMenu(window,location_menu_var,*menu_values)
else:
    location_field = tk.OptionMenu(window,location_menu_var,menu_values)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(), y_multiplier_integer,location_field)

geocode_locations_var.set(0)
geocode_locations_checkbox = tk.Checkbutton(window, variable=geocode_locations_var, onvalue=1, offvalue=0)
geocode_locations_checkbox.config(text="GEOCODE locations")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,geocode_locations_checkbox, True)

def activate_geocoder(*args):
    if geocode_locations_var.get()==True:
        geocoder.configure(state='normal')
    else:
        geocoder.configure(state='disabled')

    if geocode_locations_var.get()==0:
        if display_csv_file_options()==True:
            return
        if display_txt_file_options()==True:
            return
geocode_locations_var.trace('w',activate_geocoder)

geocoder_lb = tk.Label(window, text='Geocoder')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,geocoder_lb,True)
geocoder_var.set('Nominatim')
geocoder = tk.OptionMenu(window,geocoder_var,'Nominatim','Google')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+80, y_multiplier_integer,geocoder,True)

# https://developers.google.com/maps/documentation/embed/get-api-key
# Google_API_geocode_lb = tk.Label(window, text='API key')
# Google_API_geocode = tk.Entry(window, width=40, textvariable=Google_API_Google_geocode_var)

# save_APIkey_button_Google_geocode = tk.Button(window, text='OK', width=2,height=1,command=lambda: config_util.Google_API_Config_Save('Google-geocode-API-config.txt',Google_API_Google_geocode_var.get()))

def activate_Google_API_geocode(*args):
    if geocoder_var.get()=='Google':
        key = GIS_pipeline_util.getGoogleAPIkey('Google-geocode-API-config.txt')
        if key=='' or key==None:
            mb.showwarning(title='Warning',
                           message="No Google geocoder API key was entered. The geocoder option has been reset to 'Nominatim.'")
            geocoder_var.set('Nominatim')
            geocoder='Nominatim'
geocoder_var.trace('w',activate_Google_API_geocode)

country_menu = constants_util.ISO_GIS_country_menu

country_bias_lb = tk.Label(window, text='Country bias')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+600,y_multiplier_integer,country_bias_lb,True)
country_bias_var.set('')
country_bias = ttk.Combobox(window, width = 25, textvariable = country_bias_var)
country_bias['values'] = country_menu
country_bias.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+970, y_multiplier_integer,country_bias)

map_locations_var.set(0)
map_locations_checkbox = tk.Checkbutton(window, variable=map_locations_var, onvalue=1, offvalue=0)
map_locations_checkbox.config(text="MAP locations")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,map_locations_checkbox,True)

def call_reminders(*args):
    if map_locations_var.get()==True:
        if GIS_package_var.get()!='':
            GIS_package_var.set('Google Earth Pro & Google Maps')
    else:
        GIS_package_var.set('')
    if display_csv_file_options():
        return
map_locations_var.trace('w',call_reminders)


GIS_package_var.set('Google Earth Pro & Google Maps')
GIS_package_lb = tk.Label(window, text='Software')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate(),y_multiplier_integer,GIS_package_lb,True)
GIS_package = tk.OptionMenu(window,GIS_package_var,'Google Earth Pro & Google Maps','Google Earth Pro','Google Maps','QGIS','Tableau','TimeMapper')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+80, y_multiplier_integer,GIS_package,True)

GIS_package2_var.set(0)
GIS_package2_checkbox = tk.Checkbutton(window, variable=GIS_package2_var, onvalue=1, offvalue=0)
GIS_package2_checkbox.config(text="GIS package - Open GUI")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700, y_multiplier_integer,GIS_package2_checkbox)

# https://developers.google.com/maps/documentation/embed/get-api-key
# Google_API_Google_maps_lb = tk.Label(window, text='API key')
# Google_API_Google_maps = tk.Entry(window, width=40, textvariable=Google_API_Google_maps_var)

def activate_Google_API_Google_Maps(*args):
    global GIS_package2_checkbox
    if not 'Google' in GIS_package_var.get() and len(GIS_package_var.get())>0:
        GIS_package_var.set('')
        mb.showwarning(title='Warning',
                       message="The selected software option is not available yet. Sorry!\n\nSelect any of the Google options and try again.")
        return
    if 'Maps' in GIS_package_var.get():
        key = GIS_pipeline_util.getGoogleAPIkey('Google-Maps-API-config.txt')
        if key == '' or key == None:
            GIS_package_var.set('Google Earth Pro')
            mb.showwarning(title='Warning',
                           message="No Google Maps API key was entered. The software package option has been reset to 'Google Earth Pro.'")
GIS_package_var.trace('w',activate_Google_API_Google_Maps)

def display_reminder(*args):
    if GIS_package2_var.get():
        # routine_options = reminders_util.getReminders_list(config_filename)
        reminders_util.checkReminder(config_filename,
                                     reminders_util.title_options_Google_Earth,
                                     reminders_util.message_Google_Earth,
                                     True)
        routine_options = reminders_util.getReminders_list(config_filename)
        return
GIS_package2_var.trace('w', display_reminder)

TIPS_lookup = {'utf-8 encoding': 'TIPS_NLP_Text encoding.pdf',"Geocoding":"TIPS_NLP_Geocoding.pdf","Google Earth Pro":"TIPS_NLP_Google Earth Pro.pdf","Google API Key":"TIPS_NLP_Google API Key.pdf", "Google Earth Pro KML Options":"TIPS_NLP_Google Earth Pro KML options.pdf","HTML":"TIPS_NLP_Google Earth Pro HTML.pdf","Google Earth Pro Icon":"TIPS_NLP_Google Earth Pro Icon.pdf", "Google Earth Pro Description":"TIPS_NLP_Google Earth Pro Description.pdf"}
TIPS_options='utf-8 encoding','Geocoding', 'Google Earth Pro', 'Google API Key', 'HTML', 'Google Earth Pro Icon', 'Google Earth Pro Description'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    if IO_setup_display_brief==False:
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",'Please, select an input file for the GIS script. Two two types of files are acceptable: txt or csv.\n\nTXT FILE. When a txt file is selected, the script will use the NER values from Stanford CoreNLP to obtain a list of locations saved as a csv file. The script will then process this file the same way as it would process a csv file in input containing location names.\n\nCSV FILE. When a csv file is selected it can be:\n  1. a file containing a column of location names that need to be geocoded (e.g., New York);\n  2. a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script Stanford_CoreNLP_main.py (the script parses text documents using the Stanford CoreNLP parser).'+GUI_IO_util.msg_Esc)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData+GUI_IO_util.msg_Esc)
        GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory+GUI_IO_util.msg_Esc)
    else:
        GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate, "Help",
                                      GUI_IO_util.msg_IO_setup)

    GUI_IO_util.place_help_button(window, help_button_x_coordinate, basic_y_coordinate + y_step * (increment+1), "Help",
                                  "The INPUT csv file widget displays the csv LOCATION file as soon as produced by the Stanford CoreNLP NER annotator.\n\nEdit the file and rerun the algorithm to geocode from scratch.\n\nYou can also use the 'Select INPUT CSV file' button to select\n   1. a csv file, however created, containing a list of locations;\n   2. a csv file of geocoded locations (with fields Latitude and Longitude) previosuly created by this algorithm ;\n   3. a csv CoNLL table file.\n\nDifferent options will be available depending upon what the csv file widget displays.\n\nTO RERUN THE PIPELINE, FROM SCRATCH, FROM TEXT TO MAPS, PRESS ESC TO CLEAR THE CSV FILE WIDGET.\n\nYou can also select a geocoded csv file and run the 'MAP locations' option." + GUI_IO_util.msg_openFile)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+2),"Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding.\n\nYou can adjust the memory required to run the CoreNLP NER annotator by sliding the memory bar; the default value of 4 should be sufficient."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+3),"Help","The GIS algorithms allow you to extract a date to be used to build dynamic GIS maps. You can extract dates from the document content or from the filename if this embeds a date.\n\nPlease, the tick the checkbox 'From document content' if you wish to extract normalized NER dates from the text itself.\n\nPlease, tick the checkbox 'From filename' if filenames embed a date (e.g., The New York Times_12-05-1885).\n\nDATE WIDGETS ARE NOT VISIBLE WHEN SELECTING A CSV INPUT FILE."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+4),"Help","Please, tick the checkbox if you wish to EXTRACT locations from a text file using Stanford CoreNLP NER extractor.\n\nThe option is available ONLY when an input txt file is selected.\n\nTick the Open GUI checkbox ONLY if you wish to open the Stanford CoreNLP NER extractor GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+5),"Help","Please, using the dropdown menu, select the column containing the location names (e.g., New York) to be geocoded and mapped.\n\nTHE OPTION IS NOT AVAILABLE WHEN SELECTING A CONLL INPUT CSV FILE. NER IS THE COLUMN AUTOMATICALLY USED WHEN WORKING WITH A CONLL FILE IN INPUT."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+6),"Help","Please, tick the checkbox if you wish to GEOCODE  a list of locations.\n\nThe option is available ONLY when a csv file of locations NOT yet geocoded is selected.\n\nTo obtain more accurate geocoded results, select a country where most locations are expected to be. Thus, if you select United States as your country bias, the geocoder will geocode locations such as Florence, Rome, or Venice in the United States rather than in Italy.\n\nTick the Open GUI checkbox ONLY if you wish to open the geocode GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+7),"Help","Please, tick the checkbox if you wish to MAP a list of geococed locations.\n\nUsing the dropdown menu, select the GIS (Geographic Information System) package you wish to use to produce maps.\n\nGoogle Maps requires an API key that you obtain from registering.\n\nWhen selecting Google Maps, the API key field will become available.\n\nYou will need to get the API key from the Google console and entering it there. REMEMBER! When applying for an API key you will need to enter billing information; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale.\n https://developers.google.com/maps/documentation/embed/get-api-key.\n\nAfter entering the Google API key, click OK to save it and the key will be read in automatically next time around.\n\nTick the Open GUI checkbox ONLY if you wish to open the Google Earth Pro GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step* (increment+8),"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script allows users to go from text to map in three steps:\n\n1. EXTRACT locations from a text file using Stanford CoreNLP NER extractor (NER values: CITY, STATE_OR_PROVINCE, COUNTRY);\n2. GEOCODE locations, previously extracted, using Nominatim or Google (an API is needed for Google);\n3. MAP locations, previously geocoded, using a selected GIS package (e.g., Google Earth Pro; Google Maps to produce heat maps; Google Maps requires an API key).\n\nOptions are preset and\or disabled depending upon the input type (directory or file; txt or csv file; csv CoNLL file or list of locations to be geocoded or already geocoded).\n\nAll three steps can be selected and carried out in sequence in a pipeline, going automatically from text to map."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options,IO_setup_display_brief)

# routine_options = reminders_util.getReminders_list(config_filename)
result = reminders_util.checkReminder(config_filename,
                              reminders_util.title_options_GIS_GUI,
                              reminders_util.message_GIS_GUI)
if result!=None:
    routine_options = reminders_util.getReminders_list(config_filename)

activate_Google_API_geocode()
activate_Google_API_Google_Maps()

GUI_util.window.mainloop()
