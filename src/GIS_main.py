# Written by Roberto Franzosi May, September 2020

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

import config_util
import GIS_geocode_util
import GIS_file_check_util
import GIS_KML_util
import GIS_Google_Maps_util
import IO_files_util
import Stanford_CoreNLP_annotator_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename,
		inputDir,
		outputDir,
		openOutputFiles,
		createExcelCharts,
		encoding_var,
		extract_date_from_text_var,
		extract_date_from_filename_var,
		date_format,
		date_separator_var,
		date_position_var,
		memory_var,
		NER_extractor_var,
		location_var,
		geocode_locations_var,
		GIS_package_var,
		GIS_package2_var,
		Google_API):

	filesToOpen = []

	inputIsCoNLL=False
	inputIsGeocoded=False
	geocoder='Nominatim'
	split_locations = ''
	locationColumnName = 'Location'
	datePresent = False

	# TODO code should go to pipeline?

	if inputFilename!='':
		if inputFilename.endswith('.txt'):
			#RF NER_extractor_var.set(1)
			NER_extractor_var=True

		#RF location_var.set('')
		location_var=''
		if inputFilename.endswith('.csv'):
			# If Column A is 'Word', rename to 'Location'
			temp = pd.read_csv(inputFilename)
			if temp.columns[0] == 'Word':
				temp = temp.rename(columns={"Word": "Location"})
			temp.to_csv(inputFilename, index=False)

			inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable= GIS_file_check_util.CoNLL_checker(inputFilename)

			# TODO check that lat or long are not there already; if they are then run Google Earth Pro
			#RF NER_extractor_var.set(0)
			NER_extractor_var=False
			if 'Latitude' in headers and 'Longitude' in headers:
				geocode_locations_var.set(0)
				geocode_locations_var=False
				location_var.set('Latitude')
				# GIS_package_var.set("Google Earth Pro")
				# GIS_package_var="Google Earth Pro"
			elif 'postag' and 'deprel' and 'ner' in str(headers).lower():
				location_var.set('Ner')
			else:
				geocode_locations_var.set(1)
				geocode_locations_var=True
	else:
		#RF NER_extractor_var.set(1)
		NER_extractor_var = True

	if NER_extractor_var==False and geocode_locations_var==False and GIS_package_var=='':
		mb.showwarning("Warning",
					   "No options have been selected.\n\nPlease, select an option to run and try again.")
		return


# START PROCESSING ---------------------------------------------------------------------------------------------------

	# save original filename since it will be changed by the pipeline but the original filename is used by the kml script
	inputFilenameSv = inputFilename

	# checking for txt: NER=='LOCATION', provide a csv output with column: [Locations]
	if NER_extractor_var==True:

		NERs = ['COUNTRY', 'STATE_OR_PROVINCE', 'CITY']

		locations = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, inputDir,
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
		if extract_date_from_text_var or extract_date_from_filename_var:
			datePresent = True
			df = pd.read_csv(locations[0]).rename(columns={"Word": "Location"})
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
			df = pd.read_csv(locations[0]).rename(columns={"Word": "Location"})
			# 'NER': ['Word', 'NER Value', 'Sentence ID', 'Sentence', 'tokenBegin', 'tokenEnd', 'Document ID', 'Document'],

		# Clean dataframe, remove any 'DATE' or non-location rows
		del_list = []
		for index, row in df.iterrows():
			if df['NER Value'][index] not in ['COUNTRY','STATE_OR_PROVINCE','CITY']:
				del_list.append(index)
		df = df.drop(del_list)

		if inputDir!='':
			outputFilename = outputDir + os.sep + os.path.basename(os.path.normpath(inputDir)) + '_LOCATIONS.csv'
		else:
			head, tail = os.path.split(inputFilename)
			outputFilename = outputDir + os.sep + tail[:-4]
			outputFilename=outputFilename+'_LOCATIONS.csv'
		df.to_csv(outputFilename, index=False)
		inputFilename=outputFilename
		withHeader=True
		locationColumnNumber=0
		location_num=0
		filenamePositionInCoNLLTable=0
		GUI_util.inputFilename.set(outputFilename)
		locationColumn='Location'

	geocoder = 'Nominatim'
	geoName = 'geo-' + str(geocoder[:3])
	kmloutputFilename = ''
	if geocode_locations_var==True:
		if not inputFilename.endswith('.csv'):
			mb.showwarning("Input file error","The geocoding option expects in input a csv file containing a list of locations (locations, perhaps, extracted using the Stanford CoreNLP NER extractor).\n\nPlease, select a csv file in input and try again.")
			return
		else:

			# Google_API=''
			country_bias=''
			locationColumnNumber=0
			locationColumnName='Location'
			geocodedLocationsoutputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'GIS',
																					  geoName, locationColumnName, '', '',
																					  False, True)
			locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.csv', 'GIS',
																					  geoName, 'Not-Found', locationColumnName, '',
																					  False, True)
			locations=''
			geocodedLocationsoutputFilename, locationsNotFoundoutputFilename = GIS_geocode_util.geocode(GUI_util.window,
																				locations,
																				inputFilename,
																				outputDir,
																				locationColumnName,
																				geocoder,
																				Google_API,
																				country_bias,
																				encoding_var)
			# Add in date info here if it exists
			if datePresent:
				temp_geocoded_csv = pd.read_csv(geocodedLocationsoutputFilename)
				temp_input_csv = pd.read_csv(inputFilename)
				temp_geocoded_csv['Date'] = temp_input_csv['Date']
				temp_geocoded_csv.to_csv(geocodedLocationsoutputFilename, index=False)
			inputIsGeocoded=True
			# when using the locations file the inputFilenameSv leads to errors in extract_index in GIS_locations_util; it does not happen with SVO
			inputFilenameSv=inputFilename
			GUI_util.inputFilename.set(geocodedLocationsoutputFilename)



	if inputIsGeocoded==False:
		mb.showwarning(title='Warning',message='No geocoding option selected. The GIS script will exit.')
		return

	if GIS_package_var=='Google Maps':
		if IO_libraries_util.inputProgramFileCheck('GIS_Google_Maps_util.py') == False:
			return
		heatMapoutputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir, '.html', 'GIS',
																		geoName, locationColumnName, '', '',
																		False, True)
		coordList = []
		df = pd.read_csv(GUI_util.inputFilename.get())
		if 'Latitude' in df and 'Longitude' in df:
			lat = df.Latitude
			lon = df.Longitude

			for i in range(len(lat)):
				coordList.append([lat[i], lon[i]])
		else:
			print("Error! input csv does not contain Latitude or Longitude columns")

		if Google_API=='':
			mb.showwarning('Warning','Google Maps requires an API key. You can get the key free of charge at the Google website console.developers.google.com/apis. Then, paste the API key  in the Google API box and try again.')
			return
		GIS_Google_Maps_util.create_js(heatMapoutputFilename, coordList, Google_API, geocoder, True)
		filesToOpen.append(heatMapoutputFilename)

	elif GIS_package_var=='Google Earth Pro':
		if GIS_package2_var == True:
			if IO_libraries_util.inputProgramFileCheck('GIS_Google_Earth_main.py') == False:
				return
			# save the current configuration to open GIS_Google_Earth_main with the right IO files
			if inputFilename.endswith('.csv'):
				configArray=['EMPTY LINE', inputFilename, 'EMPTY LINE', 'EMPTY LINE', 'EMPTY LINE', outputDir]
				config_util.saveConfig(GUI_util.window, 'GIS-Google-Earth-config.txt', configArray,True)
			call("python3GIS_Google_Earth_main.py", shell=True)
			return
		if IO_libraries_util.inputProgramFileCheck('GIS_KML_util.py') == False:
			return
		geocodedLocationsoutputFilename=GUI_util.inputFilename.get()
		locationColumnNumber=0
		# check that the starting input is not a geocoded file; only a ocations file would contain sentences to be displayed in KML DESCRIPTION field
		if inputFilenameSv==geocodedLocationsoutputFilename:
			description_var_list=[1]
			description_csv_field_var_list=['Location']
		else:
			description_var_list = [1]
			description_csv_field_var_list = ['Sentence']
		kmloutputFilename = GIS_KML_util.generate_kml(GUI_util.window, inputFilenameSv, geocodedLocationsoutputFilename,
													  datePresent,
													  locationColumnNumber,
													  'utf-8',
													  1, 1, 1, [1], [1],
													  'Location',
													  0, [''], [''],
													  ['Pushpins'], ['red'],
													  [0], ['1'], [0], [''],
													  description_var_list, description_csv_field_var_list)


	else:
		if GIS_package_var!='':
			mb.showwarning("Option not available","The " + GIS_package_var + " option is not available yet.\n\nSorry! Please, check back soon...")
			return

	if kmloutputFilename!='':
		filesToOpen.append(kmloutputFilename)
		# IO_files_util.open_kmlFile(kmloutputFilename)

	if len(filesToOpen) == 0:
		return

	if openOutputFiles == 1:
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
							GUI_util.input_main_dir_path.get(),
							GUI_util.output_dir_path.get(),
							GUI_util.open_csv_output_checkbox.get(),
							GUI_util.create_Excel_chart_output_checkbox.get(),
							encoding_var.get(),
							extract_date_from_text_var.get(),
							extract_date_from_filename_var.get(),
							date_format.get(),
							date_separator_var.get(),
							date_position_var.get(),
							memory_var.get(),
							NER_extractor_var.get(),
							location_var.get(),
							geocode_locations_var.get(),
							GIS_package_var.get(),
							GIS_package2_var.get(),
							Google_API_Google_maps_var.get()
							)

GUI_util.run_button.configure(command=run_script_command)

# GUI section ______________________________________________________________________________________________________________________________________________________

GUI_size='1300x520'
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
config_option=[0,6,1,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

# GUI CHANGES add following lines to every special GUI
# +3 is the number of lines starting at 1 of IO widgets (CoreNLP+inputfile+inputdir+ouutputdir=3)
y_multiplier_integer=GUI_util.y_multiplier_integer+2
window=GUI_util.window
config_input_output_options=GUI_util.config_input_output_options
config_filename=GUI_util.config_filename
inputFilename=GUI_util.inputFilename
input_main_dir_path=GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_options,config_filename)

encoding_var=tk.StringVar()
memory_var = tk.IntVar()

extract_date_from_text_var= tk.IntVar()
extract_date_from_filename_var= tk.IntVar()
date_format = tk.StringVar()
date_separator_var = tk.StringVar()
date_position_var = tk.IntVar()

location_var=tk.StringVar()
NER_extractor_var=tk.IntVar()
geocode_locations_var=tk.IntVar()
geocoder_var=tk.StringVar()
Google_API_Google_geocode_var = tk.StringVar()
country_bias_var=tk.StringVar()
GIS_package_var=tk.StringVar()
GIS_package2_var=tk.IntVar()
Google_API_Google_maps_var=tk.StringVar()
map_locations_var=tk.IntVar()

config_filename = 'GIS-config.txt'
Google_API=''

def clear(e):
	encoding_var.set('utf-8')
	location_var.set('')
	GIS_package_var.set('')
	GUI_util.clear("Escape")
window.bind("<Escape>", clear)

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

menu_values=IO_csv_util.get_csvfile_headers(inputFilename.get())

location_field_lb = tk.Label(window, text='Select the column containing location names')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(),y_multiplier_integer,location_field_lb,True)
if menu_values!='':
	location_field = tk.OptionMenu(window,location_var,*menu_values)
else:
	location_field = tk.OptionMenu(window,location_var,menu_values)
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+300, y_multiplier_integer,location_field)

y_multiplier_integer_save_one=y_multiplier_integer

geocode_locations_var.set(0)
geocode_locations_checkbox = tk.Checkbutton(window, variable=geocode_locations_var, onvalue=1, offvalue=0)
geocode_locations_checkbox.config(text="GEOCODE locations")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,geocode_locations_checkbox, True)

def activate_geocoder(*args):
    if geocode_locations_var.get()==True:
        geocoder.configure(state='normal')
    else:
        geocoder.configure(state='disabled')
geocode_locations_var.trace('w',activate_geocoder)

geocoder_lb = tk.Label(window, text='Geocoder service')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+150,y_multiplier_integer,geocoder_lb,True)
geocoder_var.set('Nominatim')
geocoder = tk.OptionMenu(window,geocoder_var,'Nominatim','Google')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+250, y_multiplier_integer,geocoder,True)

# https://developers.google.com/maps/documentation/embed/get-api-key
Google_API_geocode_lb = tk.Label(window, text='API key')
Google_API_geocode = tk.Entry(window, width=60, textvariable=Google_API_Google_geocode_var)

save_APIkey_button_Google_geocode = tk.Button(window, text='OK', width=2,height=1,command=lambda: config_util.Google_API_geocode_var.get())

def activate_Google_API_geocode(y_multiplier_integer_save_one,Google_API_geocode_lb,Google_API_geocode,*args):
    if geocoder_var.get()=='Google':
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+370,y_multiplier_integer_save_one,Google_API_geocode_lb,True)
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+420,y_multiplier_integer,Google_API_geocode,True)
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+820,y_multiplier_integer,save_APIkey_button_Google_geocode)
        configFilePath=os.path.join(GUI_IO_util.configPath, 'Google-API-config.txt')
        configAPIKey=[]
        if os.path.isfile(configFilePath):
            f_config = open(configFilePath, 'r', encoding='utf-8', errors='ignore')
            configAPIKey = f_config.readlines()
        if len(configAPIKey) == 0:
            mb.showwarning(title='No Google API Found', message='You need a Google API key to use the Google geocoder service.\n\nPlease, go to the Google website console.developers.google.com/apis to obtain a Google API key and paste the key in the Google API box and try again.')
        else:
            key = configAPIKey[0]
            Google_API_Google_geocode_var.set(key)
            Google_API=key
    else:
        # hide the Google API label and entry widgets until Google is selected
		# pack and place have their own _forget options
        Google_API_geocode_lb.place_forget() #invisible
        Google_API_geocode.place_forget() #invisible
        save_APIkey_button_Google_geocode.place_forget() #invisible

geocoder_var.trace('w',callback = lambda x,y,z: activate_Google_API_geocode(y_multiplier_integer_save_one,Google_API_geocode_lb,Google_API_geocode))

activate_Google_API_geocode(y_multiplier_integer_save_one,Google_API_geocode_lb,Google_API_geocode)

country_menu = constants_util.ISO_GIS_country_menu

country_bias_lb = tk.Label(window, text='Country bias')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_entry_box_x_coordinate()+600,y_multiplier_integer,country_bias_lb,True)
country_bias_var.set('')
country_bias = ttk.Combobox(window, width = 25, textvariable = country_bias_var)
country_bias['values'] = country_menu
country_bias.configure(state='disabled')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+970, y_multiplier_integer,country_bias)

y_multiplier_integer_save_two=y_multiplier_integer

# split_locations_prefix_var.set('south, north, west, east, los, new, san, las, la, hong')
# split_locations_prefix_lb = tk.Label(window, text='Split-name locations  PREFIX')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+20, y_multiplier_integer,split_locations_prefix_lb,True)
# split_locations_prefix_entry = tk.Entry(window, textvariable=split_locations_prefix_var)
# split_locations_prefix_entry.configure(width=50, state='disabled')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+200,y_multiplier_integer,split_locations_prefix_entry,True)
#
# split_locations_suffix_var.set('city, island')
# split_locations_suffix_lb = tk.Label(window, text='SUFFIX')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+580, y_multiplier_integer,split_locations_suffix_lb,True)
# split_locations_suffix_entry = tk.Entry(window, textvariable=split_locations_suffix_var)
# split_locations_suffix_entry.configure(width=50, state='disabled')
# y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_indented_coordinate()+650,y_multiplier_integer,split_locations_suffix_entry)

map_locations_var.set(0)
map_locations_checkbox = tk.Checkbutton(window, variable=map_locations_var, onvalue=1, offvalue=0)
map_locations_checkbox.config(text="MAP locations")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate(), y_multiplier_integer,map_locations_checkbox,True)

GIS_package_lb = tk.Label(window, text='Select software')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+120,y_multiplier_integer,GIS_package_lb,True)
GIS_package_var.set('')
GIS_package = tk.OptionMenu(window,GIS_package_var,'Google Earth Pro','Google Maps','QGIS','Tableau','TimeMapper')
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+220, y_multiplier_integer,GIS_package,True)

y_multiplier_integer_save_two=y_multiplier_integer

GIS_package2_var.set(0)
GIS_package2_checkbox = tk.Checkbutton(window, variable=GIS_package2_var, onvalue=1, offvalue=0)
GIS_package2_checkbox.config(text="GIS package - Open GUI")
y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700, y_multiplier_integer,GIS_package2_checkbox)

# https://developers.google.com/maps/documentation/embed/get-api-key
Google_API_Google_maps_lb = tk.Label(window, text='API key')
Google_API_Google_maps = tk.Entry(window, width=60, textvariable=Google_API_Google_maps_var)

save_APIkey_button_Google_maps = tk.Button(window, text='OK', width=2,height=1,command=lambda: config_util.Google_API_Config_Save(Google_API_Google_maps_var.get()))

def activate_Google_API_Google_Maps(y_multiplier_integer_save_two,Google_API_lb,Google_API,*args):
    global GIS_package2_checkbox
    if GIS_package_var.get()=='Google Maps':
        # hide the widget
		# pack and place have their own _forget options
        GIS_package2_checkbox.place_forget()  #invisible
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+520,y_multiplier_integer_save_two,Google_API_Google_maps_lb,True)
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+590,y_multiplier_integer,Google_API_Google_maps,True)
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+980,y_multiplier_integer,save_APIkey_button_Google_maps)
        configFilePath=os.path.join(GUI_IO_util.configPath, 'Google-API-config.txt')
        configAPIKey=[]
        if os.path.isfile(configFilePath):
            f_config = open(configFilePath, 'r', encoding='utf-8', errors='ignore')
            configAPIKey = f_config.readlines()
        if len(configAPIKey) == 0:
            mb.showwarning(title='No Google API Found', message='You need a Google API key to use the Google geocoder service.\n\nPlease, go to the Google website console.developers.google.com/apis to obtain a Google API key and paste the key in the Google API box and try again.')
        else:
            key = configAPIKey[0]
            Google_API_Google_maps_var.set(key)
            Google_API=key
    else:
        y_multiplier_integer=GUI_IO_util.placeWidget(GUI_IO_util.get_labels_x_coordinate()+700,y_multiplier_integer_save_two,GIS_package2_checkbox)
        # hide the Google API label and entry widgets until Google is selected
		# pack and place have their own _forget options
        Google_API_Google_maps_lb.place_forget() #invisible
        Google_API_Google_maps.place_forget() #invisible
        save_APIkey_button_Google_maps.place_forget() #invisible
GIS_package_var.trace('w',callback = lambda x,y,z: activate_Google_API_Google_Maps(y_multiplier_integer_save_two,Google_API_Google_maps_lb,Google_API_Google_maps))

activate_Google_API_Google_Maps(y_multiplier_integer_save_two,Google_API_Google_maps_lb,Google_API_Google_maps)

def changed_input_filename(*args):
    # display the date widgets
    if inputFilename.get().endswith('.txt') or len(input_main_dir_path.get()) > 0:
        extract_date_from_text_checkbox.config(state='normal')
        extract_date_from_filename_checkbox.config(state='normal')
    else:
        extract_date_from_text_checkbox.config(state='disabled')
        extract_date_from_filename_checkbox.config(state='disabled')

        NER_extractor_var.set(1)
        NER_extractor_checkbox.configure(state='disabled')
        location_var.set('')
        location_field.config(state='disabled')
        country_bias.configure(state='normal')
        # split_locations_prefix_entry.configure(state='normal')
        # split_locations_suffix_entry.configure(state='normal')
        geocode_locations_var.set(1)
        geocode_locations_checkbox.configure(state='normal')
        geocoder.configure(state='normal')
        map_locations_var.set(1)
        map_locations_checkbox.configure(state='normal')
    if inputFilename.get().endswith('.csv'):
        headers = IO_csv_util.get_csvfile_headers(inputFilename.get())

        NER_extractor_var.set(0)
        NER_extractor_checkbox.configure(state='disabled')
        # CoNLL table
        map_locations_var.set(1)
        map_locations_checkbox.configure(state='normal')
        if 'postag' in str(headers).lower() and 'deprel' in str(headers).lower() and 'ner' in str(headers).lower():
            # the coNLL table must be geocoded
            location_var.set('ner')
            location_field.config(state='disabled')
            geocode_locations_var.set(1)
            # geocode_locations_checkbox.configure(state='disabled')
            country_bias.configure(state='normal')
            # split_locations_prefix_entry.configure(state='normal')
            # split_locations_suffix_entry.configure(state='normal')
        elif 'lat' and 'long' in str(headers).lower():
            # the file already contains geocoded data
            geocode_locations_var.set(0)
            geocode_locations_checkbox.configure(state='disabled')
            geocoder.configure(state='disabled')
            country_bias.configure(state='disabled')
            # split_locations_prefix_entry.configure(state='disabled')
            # split_locations_suffix_entry.configure(state='disabled')
            location_var.set('Location')
            location_field.config(state='normal')
        elif 'location' in str(headers).lower():
            location_var.set('Location')
            location_field.config(state='normal')
        else:
            location_field.config(state='normal')
            location_var.set('')
        menu_values = IO_csv_util.get_csvfile_headers(inputFilename.get())

        # must change all 3 widgets where menus must be updated after changing the filename
        m = location_field["menu"]
        m.delete(0, "end")
        for s in menu_values:
            m.add_command(label=s, command=lambda value=s: location_var.set(value))
    if GIS_package2_var.get() == False:
        GIS_package_var.set('Google Earth Pro')
inputFilename.trace('w', changed_input_filename)
input_main_dir_path.trace('w', changed_input_filename)

changed_input_filename()

def display_warning(*args):
    if GIS_package2_var.get():
        # routine_options = reminders_util.getReminder_list(config_filename)
        reminders_util.checkReminder(config_filename,
                                     ['Open Google Earth GUI'],
                                     'You should tick the Open GUI checkbox ONLY if you wish to open the GUI.\n\nThe Google Earth Pro GUI will provide a number of options to personalize a Google Earth Pro map. Press Run after selecting the Open GUI option.',
                                     True)
        routine_options = reminders_util.getReminder_list(config_filename)
        return
GIS_package2_var.trace('w', display_warning)

TIPS_lookup = {"Google Earth Pro":"TIPS_NLP_Google Earth Pro.pdf","Google Earth Pro KML Options":"TIPS_NLP_Google Earth Pro KML options.pdf","HTML":"TIPS_NLP_Google Earth Pro HTML.pdf","Google Earth Pro Icon":"TIPS_NLP_Google Earth Pro Icon.pdf", "Google Earth Pro Description":"TIPS_NLP_Google Earth Pro Description.pdf"}
TIPS_options='Geocoding', 'Google Earth Pro', 'Google Earth Pro KML Options', 'HTML', 'Google Earth Pro Icon', 'Google Earth Pro Description'

# add all the lines lines to the end to every special GUI
# change the last item (message displayed) of each line of the function help_buttons
# any special message (e.g., msg_anyFile stored in GUI_IO_util) will have to be prefixed by GUI_IO_util.
def help_buttons(window,help_button_x_coordinate,basic_y_coordinate,y_step):
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate,"Help",'Please, select an input file for the GIS script. Two two types of files are acceptable: txt or csv.\n\nTXT FILE. When a txt file is selected, the script will use the NER values from Stanford CoreNLP to obtain a list of locations saved as a csv file. The script will then process this file the same way as it would process a csv file in input containing location names.\n\nCSV FILE. When a csv file is selected it can be:\n  1. a file containing a column of location names that need to be geocoded (e.g., New York);\n  2. a file of previously geocoded locations with at least three columns: location names, latitude, longitude (all other columns would be ignored);\n  3. a CoNLL table that may contain NER Location values.\n\nA CoNLL table is a file generated by the Python script Stanford_CoreNLP_main.py (the script parses text documents using the Stanford CoreNLP parser).'+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step,"Help",GUI_IO_util.msg_corpusData+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*2,"Help",GUI_IO_util.msg_outputDirectory+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*3,"Help","Please, using the dropdown menu, select the type of encoding you wish to use.\n\nLocations in different languages may require encodings (e.g., latin-1 for French or Italian) different from the standard (and default) utf-8 encoding.\n\nYou can adjust the memory required to run the CoreNLP NER annotator by sliding the memory bar; the default value of 4 should be sufficient."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*4,"Help","The GIS algorithms allow you to extract a date to be used to build dynamic GIS maps. You can extract dates from the document content or from the filename if this embeds a date.\n\nPlease, the tick the checkbox 'From document content' if you wish to extract normalized NER dates from the text itself.\n\nPlease, tick the checkbox 'From filename' if filenames embed a date (e.g., The New York Times_12-05-1885).\n\nDATE WIDGETS ARE NOT VISIBLE WHEN SELECTING A CSV INPUT FILE."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*5,"Help","Please, tick the checkbox if you wish to EXTRACT locations from a text file using Stanford CoreNLP NER extractor.\n\nThe option is available ONLY when an input txt file is selected.\n\nTick the Open GUI checkbox ONLY if you wish to open the Stanford CoreNLP NER extractor GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*6,"Help","Please, using the dropdown menu, select the column containing the location names (e.g., New York) to be geocoded and mapped.\n\nTHE OPTION IS NOT AVAILABLE WHEN SELECTING A CONLL INPUT CSV FILE. NER IS THE COLUMN AUTOMATICALLY USED WHEN WORKING WITH A CONLL FILE IN INPUT."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*7,"Help","Please, tick the checkbox if you wish to GEOCODE  a list of locations.\n\nThe option is available ONLY when a csv file of locations NOT yet geocoded is selected.\n\nTo obtain more accurate geocoded results, select a country where most locations are expected to be. Thus, if you select United States as your country bias, the geocoder will geocode locations such as Florence, Rome, or Venice in the United States rather than in Italy.\n\nTick the Open GUI checkbox ONLY if you wish to open the geocode GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    # GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help","Please, edit the list of locations with split names for any additional cases, entering separately the first (PREFIX) part (e.g., hong for Hong Kong) and the last part (SUFFIX) (e.g., city for Atlantic City) of a location.\n\nThese values are used to improve geocoding acccuracy, so that Jefferson City, Tennessee, is not geocoded separately as Jefferson, Texas, and City, as the City of London in the United Kingdom."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*8,"Help","Please, tick the checkbox if you wish to MAP a list of geococed locations.\n\nUsing the dropdown menu, select the GIS (Geographic Information System) package you wish to use to produce maps.\n\nGoogle Maps requires an API key that you obtain from registering.\n\nWhen selecting Google Maps, the API key field will become available.\n\nYou will need to get the API key from the Google console and entering it there. REMEMBER! When applying for an API key you will need to enter billing information; billing information is required although it is VERY unlikely you will be charged since you are not producing maps on a massive scale.\n https://developers.google.com/maps/documentation/embed/get-api-key.\n\nAfter entering the Google API key, click OK to save it and the key will be read in automatically next time around.\n\nTick the Open GUI checkbox ONLY if you wish to open the Google Earth Pro GUI for more options. Do not tick the checkbox if you wish to run the pipeline automatically from text to maps."+GUI_IO_util.msg_Esc)
    GUI_IO_util.place_help_button(window,help_button_x_coordinate,basic_y_coordinate+y_step*9,"Help",GUI_IO_util.msg_openOutputFiles)

help_buttons(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),GUI_IO_util.get_y_step())

# change the value of the readMe_message
readMe_message="This Python 3 script allows users to go from text to map in three steps:\n\n1. EXTRACT locations from a text file using Stanford CoreNLP NER extractor (NER values: CITY, STATE_OR_PROVINCE, COUNTRY);\n2. GEOCODE locations, previously extracted, using Nominatim or Google (an API is needed for Google);\n3. MAP locations, previously geocoded, using a selected GIS package (e.g., Google Earth Pro; Google Maps to produce heat maps; Google Maps requires an API key).\n\nOptions are preset and\or disabled depending upon the input type (directory or file; txt or csv file; csv CoNLL file or list of locations to be geocoded or already geocoded).\n\nAll three steps can be selected and carried out in sequence in a pipeline, going automatically from text to map."
readMe_command=lambda: GUI_IO_util.readme_button(window,GUI_IO_util.get_help_button_x_coordinate(),GUI_IO_util.get_basic_y_coordinate(),"Help",readMe_message)
GUI_util.GUI_bottom(config_input_output_options,y_multiplier_integer,readMe_command, TIPS_lookup,TIPS_options)

# routine_options = reminders_util.getReminder_list(config_filename)
result = reminders_util.checkReminder(config_filename,
                             ['GIS GUI options'],
                             'The options available on the GUI have been automatically set for you depending upon the type of input file selected: txt or csv.\n\nWith a TXT file, NER extraction via Stanford CoreNLP must be first performed.\n\nWith a CSV file, the script checks whether the file is a CoNLL table, a geocoded file containing latitude and longitude values, or a file containing a list of locations that need to be geocoded.')
if result!=None:
	routine_options = reminders_util.getReminder_list(config_filename)

GUI_util.window.mainloop()
