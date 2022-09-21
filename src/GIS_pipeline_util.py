# Cynthia Dong May 2020
# Cynthia Dong May 2020
# Roberto Franzosi September 2020
# Mino Cha September 2022

import os
import pandas as pd
import tkinter.messagebox as mb
import tkinter as tk
import csv

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
import TIPS_util
import constants_util
import charts_util

# The script is used by SVO_main and by Google_Earth_main to run a csv file that 1. needs geocoding; 2. mapping geocoded location onto Google Earth Pro.
import IO_user_interface_util

# Google_config: 'Google-geocode-API_config.csv' or 'Google-Maps-API_config.csv'
def getGoogleAPIkey(Google_config, display_key=False):
    configFilePath = os.path.join(GUI_IO_util.configPath, Google_config)
    configAPIKey = []
    if os.path.isfile(configFilePath):
        f_config = open(configFilePath, 'r', encoding='utf-8', errors='ignore')
        configAPIKey = f_config.readlines()
    if len(configAPIKey) == 0 or display_key:
        if 'Maps' in Google_config:
            msg='Maps'
            config_file = 'Google-Maps-API_config.csv'
        else:
            msg='geocoder'
            config_file = 'Google-geocode-API_config.csv'
        if len(configAPIKey) == 0:
            message = 'No config file ' + config_file + ' was found in the config subfolder of the NLP-SUIte.\n\nGoogle ' + msg + ' requires an API key (in fact, Google requires two separate free API keys, one for Google geocoder, the other for Google Maps).'
            if 'geocode' in Google_config:
                message = message + '\n\nWithout a Google geocoder API key you can only geocode locations with Nominatim.'
            if 'Maps' in Google_config:
                message = message + '\n\nWithout a Google Maps API key you can only map locations in Google Earth Pro.'
            message = message + '\n\nPlease, read the TIPS file TIPS_NLP_Google API Key.pdf on how to obtain free Google API keys.\n\nWould you like to open the TIPS file now?'
            answer = tk.messagebox.askyesno("Warning",message)
            if answer:
                TIPS_util.open_TIPS('TIPS_NLP_Google API Key.pdf')
        if 'Maps' in Google_config:
            config_type='Maps'
        else:
            config_type = 'geocoder'
        if display_key and len(configAPIKey) > 0:
            key=configAPIKey[0]
        else:
            key=''
        if key=='':
            message = "Enter the Google " + config_type + " API key"
        else:
            message = "Enter a new Google " + config_type + " API key if you want to change the key"
        key, string_out = GUI_IO_util.enter_value_widget(message, 'Enter', 1, key, 'API key', key)
        # save the API key
        if key!='':
            config_util.Google_API_Config_Save(Google_config, key)
    else:
        key = configAPIKey[0]
    return key


# the list of arguments reflect the order of widgets in the Google_Earth_main GUI
# processes one file at a time
def GIS_pipeline(window, config_filename, inputFilename, inputDir, outputDir,
                        geocoder, mapping_package, createCharts, chartPackage,
                        datePresent,
                        country_bias,
                        area_var,
                        restrict,
                        locationColumnName,
                        encodingValue,
                        group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                        icon_var_list, specific_icon_var_list, # pushpin, red
                        name_var_list, scale_var_list, color_var_list, color_style_var_list,
                        bold_var_list, italic_var_list,
                        description_var_list=[], description_csv_field_var_list=[]):

    filesToOpen=[]

    split_locations_prefix="south, north, west, east, los, new, san, las, la, hong"
    split_locations_suffix="city, island"

    # if datePresent:
    #     date, dateStr = IO_files_util.getDateFromFileName(inputFilename, dateFormat, dateDelimiter, int(datePosition))
        # if date == '':
        #     continue  # TODO: Warn user this file has a bad date; done in getDate
        # else:

    inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)

    locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumnName, inputFilename)

    if locationColumnNumber == None:
        return

    dateColumnNumber = -1
    if datePresent == True:
        dateColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,"Date", inputFilename)

    outputCsvLocationsOnly = ''

    software=config_filename.replace('_config.csv','')
    GoogleEarthProDir, missing_external_software = IO_libraries_util.get_external_software_dir(software + ', with the option of mappping locations,','Google Earth Pro')
    if GoogleEarthProDir == None:
        return

    startTime = IO_user_interface_util.timed_alert(window, 3000, 'Analysis start', 'Started running GIS pipeline at',
                                                   True, '', True, '', False)

    #
    # ------------------------------------------------------------------------------------
    # get locations
    # ------------------------------------------------------------------------------------

    if inputIsCoNLL == True:
        outputCsvLocationsOnly = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
                                                                   'NER_locations', '', '', '', False, True)
        locations = GIS_location_util.extract_NER_locations(window, inputFilename, encodingValue,
                                                            split_locations_prefix,
                                                            split_locations_suffix,
                                                            datePresent)
    else:
        # locations is a list of names of locations
        locations = GIS_location_util.extract_csvFile_locations(window, inputFilename, withHeader, locationColumnNumber,encodingValue, datePresent, dateColumnNumber)
        if geocoder == 'Nominatim':
            changed = False
            nom_df = pd.DataFrame(locations, columns=['Location', 'Date','NER']) if len(locations[0])==3 else pd.DataFrame(locations, columns=['Location', 'Index', '0','NER'])
            drop_idx = []
            changed_idx = {}
            for i,row in nom_df.iterrows():
                # if i!=0 and row[0] in constants_util.continents and nom_df.at[i-1, 'Location'] in constants_util.directions:
                if i!=0 and \
                    (row[0] == 'Africa' or \
                    row[0] == 'Antarctica' or \
                    row[0] == 'Asia' or \
                    row[0] == 'Australia' or \
                    row[0] == 'Europe' or \
                    row[0] == 'Oceania' or \
                    row[0] == 'America') and \
                    (nom_df.at[i - 1, 'Location'] == 'North' or \
                    nom_df.at[i - 1, 'Location'] == 'South'):
                    nom_df.at[i, 'Location'] = nom_df.at[i-1, 'Location'] + ' ' + row[0]
                    drop_idx.append(i-1)
                    changed_idx[i] = nom_df.at[i, 'Location']
                    changed = True
                # TODO special case for 'America' without 'North' or 'South' in front: convert it to 'United States'
                elif row[0] == 'America':
                    nom_df.at[i, 'Location'] = 'United States'
                    changed_idx[i] = nom_df.at[i, 'Location']
                    changed = True
            if changed:
                tmp_df = pd.read_csv(inputFilename)
                for k,v in changed_idx.items():
                    tmp_df.at[k, 'Location'] = v
                tmp_df = tmp_df.drop(drop_idx)
                tmp_df.to_csv(inputFilename, index=False) # TODO: drop a index column, which will produce error with producing KML (if selected).
            nom_df = nom_df.drop(drop_idx)
            locations = [row.values.tolist() for _,row in nom_df.iterrows()]

    if locations == None or len(locations) == 0:
        return

    #
    # ------------------------------------------------------------------------------------
    # geocode
    # ------------------------------------------------------------------------------------

    if inputIsGeocoded == False:  # the input file is NOT already geocoded
        geoName = 'geo-' + str(geocoder[:3])
        geocodedLocationsOutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                  'GIS',
                                                                                  geoName, locationColumnName, '', '',
                                                                                  False,
                                                                                  True)
        locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                                                  'GIS',
                                                                                  geoName, 'Not-Found',
                                                                                  locationColumnName, '',
                                                                                  False, True)
        kmloutputFilename = geocodedLocationsOutputFilename.replace('.csv', '.kml')

        geocodedLocationsOutputFilename, \
            locationsNotFoundoutputFilename, \
            locationsNotFoundNonDistinctoutputFilename = \
            GIS_geocode_util.geocode(window, locations, inputFilename, outputDir,
                locationColumnName,geocoder,country_bias,area_var,restrict,encodingValue,split_locations_prefix,split_locations_suffix)
        if geocodedLocationsOutputFilename=='' and locationsNotFoundoutputFilename=='': #when geocoding cannot run because of internet connection
            return
    else:
        geocodedLocationsOutputFilename = inputFilename
        locationsNotFoundoutputFilename = ''
        locationsNotFoundNonDistinctoutputFilename = ''

    if len(locations) > 0 and inputIsCoNLL == True:
        # locations contains the following values:
        #	location, sentence, filename, date (if present)
        filesToOpen.append(outputCsvLocationsOnly)
        if datePresent == True:
            # always use the location_var variable passed by algorithms to make sure locations are then matched
            locations.insert(0, ['Location', 'NER Tag', 'Sentence ID', 'Sentence', 'Document ID', 'Document',  'Date'])
        else:
            # always use the location_var variable passed by algorithms to make sure locations are then matched
            locations.insert(0, ['Location', 'NER Tag', 'Sentence ID', 'Sentence', 'Document ID', 'Document'])
        IO_csv_util.list_to_csv(window, locations, outputCsvLocationsOnly)

    # the plot of locations frequencies is done in the CoreNLP_annotator_util
    # the plot of location NER Tags frequencies is done in the CoreNLP_annotator_util
    # need to plot locations geocoded and not geocoded

    nRecordsFound, nColumns  = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(geocodedLocationsOutputFilename)
    if geocodedLocationsOutputFilename != '' and nRecordsFound >0:
        filesToOpen.append(geocodedLocationsOutputFilename)
        if createCharts:
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, geocodedLocationsOutputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Location'],
                                                               chartTitle='Frequency Distribution of Locations Found by ' + geocoder,
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=1, hover_label=[],
                                                               outputFileNameType='found',  # 'NER_tag_bar',
                                                               column_xAxis_label='Locations',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)

    if locationsNotFoundNonDistinctoutputFilename!='':
        nRecordsNotFound, nColumns  = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(locationsNotFoundNonDistinctoutputFilename)
        if nRecordsNotFound>0:
            filesToOpen.append(locationsNotFoundNonDistinctoutputFilename)
            if createCharts:
                chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, locationsNotFoundNonDistinctoutputFilename,
                                                                       outputDir,
                                                                       columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Location'],
                                                                       chartTitle='Frequency Distribution of Locations not Found by ' + geocoder,
                                                                       # count_var = 1 for columns of alphabetic values
                                                                       count_var=1, hover_label=[],
                                                                       outputFileNameType='not-found',  # 'NER_tag_bar',
                                                                       column_xAxis_label='Locations',
                                                                       groupByList=[],
                                                                       plotList=[],
                                                                       chart_title_label='')
                if chart_outputFilename != None:
                    if len(chart_outputFilename) > 0:
                        filesToOpen.extend(chart_outputFilename)

            # save to csv file and run visualization
            outputFilename= IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv','found-notFound')
            with open(outputFilename, "w", newline="", encoding='utf-8', errors='ignore') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(
                    ["Number of Distinct Locations Found by Geocoder ", "Number of Distinct Locations NOT Found by Geocoder"])
                writer.writerow([nRecordsFound, nRecordsNotFound])
                csvFile.close()
            # no need to display since the chart will contain the values
            # return_files.append(outputFilename)
            columns_to_be_plotted_yAxis=["Number of Distinct Locations Found by Geocoder ", "Number of Distinct Locations NOT Found by Geocoder"]
            chart_outputFilename = charts_util.visualize_chart(createCharts, chartPackage, outputFilename,
                                                               outputDir,
                                                               columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=columns_to_be_plotted_yAxis,
                                                               chartTitle='Number of DISTINCT Locations Found and not Found by Geocoder',
                                                               # count_var = 1 for columns of alphabetic values
                                                               count_var=0, hover_label=[],
                                                               outputFileNameType='',
                                                               column_xAxis_label='Geocoder results',
                                                               groupByList=[],
                                                               plotList=[],
                                                               chart_title_label='')
            if chart_outputFilename != None:
                if len(chart_outputFilename) > 0:
                    filesToOpen.extend(chart_outputFilename)


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

        kmloutputFilename = GIS_KML_util.generate_kml(window, inputFilename, geocodedLocationsOutputFilename,
                              datePresent,
                              locationColumnName,
                              encodingValue,
                              group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
                              icon_var_list, specific_icon_var_list,
                              name_var_list, scale_var_list, color_var_list, color_style_var_list,
                              bold_var_list, italic_var_list,
                              description_var_list, description_csv_field_var_list)

        if kmloutputFilename!='':
            filesToOpen.append(kmloutputFilename)

    # ------------------------------------------------------------------------------------
    # Google Maps
    # ------------------------------------------------------------------------------------

    if 'Google Maps' in mapping_package:
        heatMapoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                                        '.html', 'GIS',
                                                                        geocoder, locationColumnName, '', '',
                                                                        False, True)
        coordList = []
        df = pd.read_csv(geocodedLocationsOutputFilename, encoding='utf-8', error_bad_lines=False)
        if 'Latitude' in df and 'Longitude' in df:
            lat = df.Latitude
            lon = df.Longitude

            for i in range(len(lat)):
                coordList.append([lat[i], lon[i]])
        else:
            mb.showwarning('Warning',
                           'The input csv file\n\n' + geocodedLocationsOutputFilename + '\n\ndoes not contain geocoded data with Latitude or Longitude columns required for Google Maps to produce heat maps.\n\nPlease, select a geocoded csv file in input and try again.')
            return

        Google_Maps_API = getGoogleAPIkey('Google-Maps-API_config.csv')
        if Google_Maps_API == '':
            return

        GIS_Google_Maps_util.create_js(heatMapoutputFilename, coordList, geocoder, True)
        filesToOpen.append(heatMapoutputFilename)

    IO_user_interface_util.timed_alert(window, 5000, 'Analysis end', 'Finished running GIS pipeline at', True, '', True, startTime)
    return filesToOpen
