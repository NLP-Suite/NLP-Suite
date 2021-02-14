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
import IO_files_util
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS",['os','pandas','tkinter','numpy'])==False:
	sys.exit(0)

import os
import pandas as pd
import tkinter as tk
import tkinter.messagebox as mb
import numpy as np

import GIS_file_check_util
import GIS_geocode_util
import GIS_distance_util
import IO_csv_util

GUI_size='1240x440'
GUI_label='Graphical User Interface (GUI) for Computing Geodesic and Great-Circle Distances between Locations'
config_filename='GIS-distance-config.txt'
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
config_option=[0,3,0,0,0,1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_option)

import GIS_distance_GUI

# ISO 3166-1 defines two-letter, three-letter, and three-digit country codes. 
# python-iso3166 is a self-contained module that converts between these codes 
#   and the corresponding country name.
# import iso3166 #pip install
# from iso3166 import countries

# from geopy.extra.rate_limiter import RateLimiter

filesToOpen=[]

def run(inputFilename,outputDir, baselineLocation,locationColumn,locationColumn2,openOutputFiles):


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

	geocoder = 'Nominatim'

	inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable=GIS_file_check_util.CoNLL_checker(inputFilename)

	if withHeader==True:
		locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumn)
		if len(locationColumn2)>0:
			locationColumnNumber2=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumn2)

	encodingValue='utf-8'
	#def restrictions_checker(inputFilename, inputIsCoNLL, withHeader, headers, locationColumn):

	# if GIS_file_check_util.restrictions_checker(inputFilename,inputIsCoNLL,inputIsGeocoded,withHeader,headers,baselineLocation,locationColumn,locationColumn2,encodingValue)==False:
	if GIS_file_check_util.restrictions_checker(inputFilename,inputIsCoNLL,withHeader,headers,locationColumn)==False:
		return

	if len(baselineLocation)>0:
		filesToOpen=GIS_distance_util.computeDistanceFromSpecificLocation(GUI_util.window,geolocator,geocoder,inputIsGeocoded,baselineLocation, inputFilename,headers,locationColumnNumber,locationColumn, distinctValues,withHeader,inputIsCoNLL,split_locations,datePresent,filenamePositionInCoNLLTable,encodingValue,outputDir)
		if len(filesToOpen)==0:
			return
	else:
		if inputIsGeocoded==True:
			filesToOpen=GIS_distance_util.computeDistance(GUI_util.window,inputFilename,headers,locationColumnNumber,locationColumnNumber2,locationColumn,locationColumn2, distinctValues,geolocator,geocoder,inputIsCoNLL,datePresent,encodingValue,outputDir)
			if len(filesToOpen)==0:
				return
		else:
			inputFilename = GIS_geocode_util.geocode_distance(GUI_util.window,inputFilename,locationColumnNumber,locationColumnNumber2,locationColumn,locationColumn2,geolocator,geocoder,inputIsCoNLL,datePresent,numColumns,encodingValue,outputDir)
			if numColumns > 2:
				locationColumnNumber = 0
				locationColumnNumber2 = 1
			locationColumnNumber2 = locationColumnNumber2+2
			filesToOpen=GIS_distance_util.computeDistance(GUI_util.window,inputFilename,headers,locationColumnNumber,locationColumnNumber2,locationColumn,locationColumn2, distinctValues,geolocator,geocoder,inputIsCoNLL,datePresent,encodingValue,outputDir)
			if len(filesToOpen)==0:
				return

	if openOutputFiles == 1:
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)

#the values of the GUI widgets MUST be entered in the command otherwise they will not be updated
run_script_command=lambda: run(GUI_util.inputFilename.get(),
							GUI_util.output_dir_path.get(),
							GIS_distance_GUI.baselineLocation_entry_var.get(),
							GIS_distance_GUI.location_var.get(),
							GIS_distance_GUI.location_var2.get(),
							GUI_util.open_csv_output_checkbox.get())

GUI_util.run_button.configure(command=run_script_command)

GUI_util.window.mainloop()
