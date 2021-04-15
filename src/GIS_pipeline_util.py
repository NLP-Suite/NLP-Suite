# Cynthia Dong May 2020
# Roberto Franzosi September 2020

import IO_files_util
import GIS_location_util
import GIS_geocode_util
import GIS_KML_util
import IO_csv_util

# The script is used by SVO_main and by Google_Earth_main to run a csv file that 1. needs geocoding; 2. mapping geocoded location onto Google Earth Pro.
import IO_user_interface_util


def GIS_pipeline(window, inputFilename, outputDir,
					 	geocoder, mapping_package,
					 	withHeader, inputIsCoNLL,
						split_locations_prefix,
				 		split_locations_suffix,
				 		datePresent, InputIsGeocoded,
					 	filenamePositionInCoNLLTable,locationColumnNumber,
					 	locationColumnName,
					 	encodingValue,
						group_number_var, italic_var, bold_var, italic_var_list, bold_var_list,
						location_var,
					 	group_var, group_values_entry_var_list,group_label_entry_var_list,
					 	icon_var_list, specific_icon_var_list,
						name_var_list, scale_var_list, color_var_list, color_style_var_list,
						description_var_list, description_csv_field_var_list):


	# TODO  bring in code from GIS_main that checks for type of file and gets all relevant values; we can eliminate several variables passed to this function
	# if inputFilename.endswith('.txt'):
	# 	if NER_extractor2_var == False:
	# 		GIS_GUI.NER_extractor_var.set(1)
	# 		NER_extractor_var = True
	# if inputFilename.endswith('.csv'):
	# 	inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(
	# 		inputFilename)

	filesToOpen=[]
	IO_user_interface_util.timed_alert(window, 3000, 'Analysis start', 'Started running GIS pipeline at', True,
						'You can follow Geocoder in command line.')
	geoName = 'geo-' + str(geocoder[:3])
	geocodedLocationsoutputFilename = IO_files_util.generate_output_file_name(inputFilename, outputDir, '.csv', 'GIS',
																			  geoName, locationColumnName, '', '', False,
																			  True)
	locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, outputDir, '.csv', 'GIS',
																			  geoName, 'Not-Found', locationColumnName, '',
																			  False, True)
	kmloutputFilename = geocodedLocationsoutputFilename.replace('.csv', '.kml')
	outputCsvLocationsOnly = ''

	if inputIsCoNLL == True:
		outputCsvLocationsOnly = IO_files_util.generate_output_file_name(inputFilename, outputDir, '.csv', 'GIS',
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

	if InputIsGeocoded == False:  # the input file is NOT already geocoded
		Google_API=''
		country_bias=''

		geocodedLocationsoutputFilename, locationsNotFoundoutputFilename = GIS_geocode_util.geocode(window, locations, inputFilename, outputDir, locationColumnName,geocoder,Google_API,country_bias,encodingValue,split_locations_prefix,split_locations_suffix)
		if geocodedLocationsoutputFilename=='' and locationsNotFoundoutputFilename=='': #when geocoding cannot run because of internet connection
			return '',''
		headers=IO_csv_util.get_csvfile_headers(geocodedLocationsoutputFilename)
	else:
		geocodedLocationsoutputFilename = inputFilename
	if len(locations) > 0 and inputIsCoNLL == True:
		# locations contains the following values:
		#	filename, location, sentence, date (if present)
		filesToOpen.append(outputCsvLocationsOnly)
		if datePresent == True:
			# always use the location_var variable passed by algorithms to make sure locations are then matched
			locations.insert(0, [location_var, 'SentenceID', 'Sentence', 'DocumentID', 'Filename',  'Date'])
		else:
			# always use the location_var variable passed by algorithms to make sure locations are then matched
			locations.insert(0, [location_var, 'SentenceID', 'Sentence', 'DocumentID', 'Filename'])
		IO_csv_util.list_to_csv(window, locations, outputCsvLocationsOnly)
	if locationsNotFoundoutputFilename != '':
		filesToOpen.append(locationsNotFoundoutputFilename)
	if geocodedLocationsoutputFilename != '':
		filesToOpen.append(geocodedLocationsoutputFilename)

	# TODO must connect the mapping package Google Maps for heat maps (GIS_Google_Maps_util)
	# In Google Maps util there are unnecessary functions since we can already pass the geocoded stuff
	if mapping_package=='Google Earth Pro':

		kmloutputFilename = GIS_KML_util.generate_kml(window, inputFilename, geocodedLocationsoutputFilename,
													  datePresent,
													  locationColumnNumber,
													  encodingValue,
													  group_number_var, italic_var, bold_var, italic_var_list, bold_var_list,
													  location_var,
													  group_var,group_values_entry_var_list, group_label_entry_var_list,
													  icon_var_list, specific_icon_var_list, name_var_list,
													  scale_var_list, color_var_list, color_style_var_list,
													  description_var_list, description_csv_field_var_list)
	elif mapping_package == 'Google Maps':
		# TODO must bring here the code in GIS_main for heatmaps
		pass
	else:
		kmloutputFilename = ''
	IO_user_interface_util.timed_alert(window, 5000, 'Analysis end', 'Finished running GIS pipeline at', True)
	return filesToOpen, kmloutputFilename
