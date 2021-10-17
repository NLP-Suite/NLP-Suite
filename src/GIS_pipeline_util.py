# Cynthia Dong May 2020
# Cynthia Dong May 2020
# Roberto Franzosi September 2020

import os
import pandas as pd
import tkinter.messagebox as mb

import IO_files_util
import IO_csv_util
import GUI_IO_util
import reminders_util
import GIS_file_check_util
import GIS_location_util
import GIS_geocode_util
import GIS_KML_util
import GIS_Google_Maps_util
import IO_libraries_util
import config_util

# The script is used by SVO_main and by Google_Earth_main to run a csv file that 1. needs geocoding; 2. mapping geocoded location onto Google Earth Pro.
import IO_user_interface_util

# Google_config: 'Google-geocode-API-config.txt' or 'Google-Maps-API-config.txt'
def getGoogleAPIkey(Google_config):
    configFilePath = os.path.join(GUI_IO_util.configPath, Google_config)
    configAPIKey = []
    if os.path.isfile(configFilePath):
        f_config = open(configFilePath, 'r', encoding='utf-8', errors='ignore')
        configAPIKey = f_config.readlines()
    if len(configAPIKey) == 0:
        if 'Maps' in Google_config:
            msg='Maps'
        else:
            msg='geocoder'
        mb.showwarning('Warning',
                       'Google ' + msg + ' requires an API key.\n\nTwo separate API keys are required for Google geocoder and Google Maps.\n\nYou can get the keys free of charge at the Google website console.developers.google.com/apis. Then, paste the API key in the Google API box, save it by pressing OK, and try again.')
        key=''
        if 'Maps' in Google_config:
            config_type='Maps'
        else:
            config_type = 'geocoder'
        key, string_out = GUI_IO_util.enter_value_widget("Enter the Google " + config_type + " API key",
                                                               'Enter', 1, '', 'API key', '')
        # save the API key
        if key!='':
            config_util.Google_API_Config_Save(Google_config, key)
    else:
        key = configAPIKey[0]
        return key

# the list of arguments reflect the order of widgets in the Google_Earth_main GUI
def GIS_pipeline(window, config_filename, inputFilename, outputDir,
                        geocoder, mapping_package,
                        datePresent,
                        locationColumnName,
                        encodingValue,
                        group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                        icon_var_list, specific_icon_var_list, # pushpin, red
                        name_var_list, scale_var_list, color_var_list, color_style_var_list,
                        bold_var_list, italic_var_list,
                        description_var_list=[], description_csv_field_var_list=[]):

    # if inputFilename.endswith('.txt'):
    # 	if NER_extractor2_var == False:
    # 		GIS_GUI.NER_extractor_var.set(1)
    # 		NER_extractor_var = True
    # if inputFilename.endswith('.csv'):
    # 	inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(
    # 		inputFilename)

    split_locations_prefix="south, north, west, east, los, new, san, las, la, hong"
    split_locations_suffix="city, island"

    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)

    locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumnName)

    filesToOpen=[]

    outputCsvLocationsOnly = ''

    software=config_filename.replace('-config.txt','')
    GoogleEarthProDir, missing_external_software = IO_libraries_util.get_external_software_dir(software + ', with the option of mappping locations,','Google Earth Pro')
    if GoogleEarthProDir == None:
        return '', ''

    IO_user_interface_util.timed_alert(window, 3000, 'Analysis start', 'Started running GIS pipeline at', True,
                                       'You can follow the pipeline in command line.')

    #
    # ------------------------------------------------------------------------------------
    # get locations
    # ------------------------------------------------------------------------------------

    if inputIsCoNLL == True:

        # reminders_util.checkReminder(config_filename, reminders_util.title_options_Google_Earth_CoNLL,
        #                                  reminders_util.message_Google_Earth_CoNLL, True)
        outputCsvLocationsOnly = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
                                                                   'NER_locations', '', '', '', False, True)
        locations = GIS_location_util.extract_NER_locations(window, inputFilename, encodingValue,
                                                            split_locations_prefix,
                                                            split_locations_suffix,
                                                            datePresent)
    else:
        # locations is a list of names of locations
        locations = GIS_location_util.extract_csvFile_locations(window, inputFilename, withHeader, locationColumnNumber,encodingValue)

    if locations == None or len(locations) == 0:
        return '', ''  # empty output files

    #
    # ------------------------------------------------------------------------------------
    # geocode
    # ------------------------------------------------------------------------------------

    if inputIsGeocoded == False:  # the input file is NOT already geocoded
        geoName = 'geo-' + str(geocoder[:3])
        geocodedLocationsoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                  'GIS',
                                                                                  geoName, locationColumnName, '', '',
                                                                                  False,
                                                                                  True)
        locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                  'GIS',
                                                                                  geoName, 'Not-Found',
                                                                                  locationColumnName, '',
                                                                                  False, True)
        kmloutputFilename = geocodedLocationsoutputFilename.replace('.csv', '.kml')

        country_bias=''

        geocodedLocationsoutputFilename, locationsNotFoundoutputFilename = GIS_geocode_util.geocode(window, locations, inputFilename, outputDir,
                                                                                    locationColumnName,geocoder,country_bias,encodingValue,split_locations_prefix,split_locations_suffix)
        if geocodedLocationsoutputFilename=='' and locationsNotFoundoutputFilename=='': #when geocoding cannot run because of internet connection
            return '', ''
    else:
        geocodedLocationsoutputFilename = inputFilename
        locationsNotFoundoutputFilename = ''

    if len(locations) > 0 and inputIsCoNLL == True:
        # locations contains the following values:
        #	filename, location, sentence, date (if present)
        filesToOpen.append(outputCsvLocationsOnly)
        if datePresent == True:
            # always use the location_var variable passed by algorithms to make sure locations are then matched
            locations.insert(0, ['Location', 'Sentence ID', 'Sentence', 'Document ID', 'Document',  'Date'])
        else:
            # always use the location_var variable passed by algorithms to make sure locations are then matched
            locations.insert(0, ['Location', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
        IO_csv_util.list_to_csv(window, locations, outputCsvLocationsOnly)

    if locationsNotFoundoutputFilename != '':
        filesToOpen.append(locationsNotFoundoutputFilename)
    if geocodedLocationsoutputFilename != '':
        filesToOpen.append(geocodedLocationsoutputFilename)

    # ------------------------------------------------------------------------------------
    # map
    # ------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------
    # Google Earth Pro
    # ------------------------------------------------------------------------------------

    if 'Google Earth Pro' in mapping_package:
        reminders_util.checkReminder(config_filename,
                          reminders_util.title_options_Google_Earth_Pro_download,
                          reminders_util.message_Google_Earth_Pro_download)

        if inputIsCoNLL==True:
            inputFilename=outputCsvLocationsOnly
        headers=IO_csv_util.get_csvfile_headers(inputFilename)
        for header in headers:
            if 'Sentence' == header:
                if len(description_csv_field_var_list)==0:
                    description_csv_field_var_list = ['Sentence']
        if not 'Sentence' in description_csv_field_var_list:
            description_csv_field_var_list = ['Location']
        description_var_list = [1]

        kmloutputFilename = GIS_KML_util.generate_kml(window, inputFilename, geocodedLocationsoutputFilename,
                              datePresent,
                              locationColumnName,
                              encodingValue,
                              group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                              icon_var_list, specific_icon_var_list,
                              name_var_list, scale_var_list, color_var_list, color_style_var_list,
                              bold_var_list, italic_var_list,
                              description_var_list, description_csv_field_var_list)

    # ------------------------------------------------------------------------------------
    # Google Maps
    # ------------------------------------------------------------------------------------

    if 'Google Maps' in mapping_package:
        heatMapoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                        '.html', 'GIS',
                                                                        geocoder, locationColumnName, '', '',
                                                                        False, True)
        coordList = []
        df = pd.read_csv(geocodedLocationsoutputFilename)
        if 'Latitude' in df and 'Longitude' in df:
            lat = df.Latitude
            lon = df.Longitude

            for i in range(len(lat)):
                coordList.append([lat[i], lon[i]])
        else:
            mb.showwarning('Warning',
                           'The input csv file\n\n' + geocodedLocationsoutputFilename + '\n\ndoes not contain geocoded data with Latitude or Longitude columns required for Google Maps to produce heat maps.\n\nPlease, select a geocoded csv file in input and try again.')
            return

        Google_Maps_API = getGoogleAPIkey('Google-Maps-API-config.txt')
        if Google_Maps_API == '':
            return

        GIS_Google_Maps_util.create_js(heatMapoutputFilename, coordList, geocoder, True)
        filesToOpen.append(heatMapoutputFilename)

    IO_user_interface_util.timed_alert(window, 5000, 'Analysis end', 'Finished running GIS pipeline at', True)
    return filesToOpen, kmloutputFilename
