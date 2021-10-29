import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS_geocode_util",['os','tkinter','csv','geopy'])==False:
	sys.exit(0)

import IO_files_util
import IO_user_interface_util
import csv
import tkinter.messagebox as mb

from geopy import Nominatim 
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut

import GIS_location_util
import GIS_file_check_util
import IO_internet_util
import IO_csv_util
import GIS_pipeline_util

filesToOpen = []

# TODO
# geocode(query, exactly_one=True, timeout=DEFAULT_SENTINEL, limit=None, addressdetails=False, language=False, geometry=None, extratags=False, country_codes=None, viewbox=None, bounded=None)
# Return a location point by address.
# Parameters: 
# query (dict or str) –
# The address, query or a structured query you wish to geocode.
# Changed in version 1.0.0: For a structured query, provide a dictionary whose keys are one of: street, city, county, state, country, or postalcode. For more information, see Nominatim’s documentation for structured requests:
# https://wiki.openstreetmap.org/wiki/Nominatim

# processes one loc at a time; only DISTINCT locations are passed to the function by geocode

# The function geocodes a list of input locations (e.g., cities) and maps them using Google Earth Pro
# The current release uses Nominatim as geocoding service
#   Since July 2018 Google requires each request to have an API key
# 		https://developers.google.com/maps/documentation/embed/get-api-key
# 		console.developers.google.com/apis

# for comparative evaluation of geocoding services
# https://dlab.berkeley.edu/blog/locating-geocoding-tool-works-you-and-your-data

# DOCUMENTATION
# https://pypi.org/project/geopy/
# https://geopy.readthedocs.io/en/stable/ geopy documentation

# geolocator will contain a string such as
#	<geopy.geocoders.osm.Nominatim object at 0x00000208F97C0438>
# using the geolocator by Nominatim/Google
#	compute the Google Earth kml file

# get latitude and longitude via a geocoder service
def get_geolocator(geocoder,Google_API=''):
	if geocoder == 'Nominatim':
		geolocator = Nominatim(user_agent="NLP Suite")
		# geolocator = Nominatim(user_agent="NLP Suite", timeout=10)

	else:
		# Country specification
		# UK: domain = 'maps.google.co.uk'
		geolocator = GoogleV3(api_key=Google_API, domain='maps.google.com')
	return geolocator

# Country specification; uses 2-digit lowercase ISO_3166 country codes
def nominatim_geocode(geolocator,loc,country_bias='',timeout=10):
	if country_bias=='':
		country_bias=None
	print("Processing Nominatim location:",loc)
	try:
		return geolocator.geocode(loc,country_codes=country_bias,timeout=timeout)
	except GeocoderTimedOut:
		print("   Nominatim timed out on " + loc + ". Timeout increased by 10 and repeatedly retried.")
		timeout=timeout+10
		return nominatim_geocode(geolocator,country_codes=country_bias,timeout=timeout)

# https://developers.google.com/maps/documentation/embed/get-api-key
# console.developers.google.com/apis
def google_geocode(geolocator,loc,region=None,timeout=10):
	print("Processing Google location for geocoding:",loc)
	region='.US'
	try:
		return geolocator.geocode(loc,region=region,timeout=timeout)
	except GeocoderTimedOut:
		return google_geocode(geolocator,loc,region=region,timeout=timeout)

# the function processes an INPUT list of NON DISTINCT locations
#   Since you do NOT want to geocode the same location multiple times and be thrown out by the selected geocoder service
#   the function filters DISTINCT locations to be passed for processing to the function nominatim_geocode
# Expects to have a list with sub lists containing [filename, location name 1, loc name 2...]
# creates csv file of geocoded values
# called by GIS_Google_Earth_util
# return 2 filenames of csv files of geocoded and non-geocoded locations
#	 filenames are '' if empty, perhaps for a permission error

def geocode(window,locations, inputFilename, outputDir,
			locationColumnName,
			geocoder,country_bias,
			encodingValue,
			split_locations_prefix='',
			split_locations_suffix=''):

	if not IO_internet_util.check_internet_availability_warning('GIS geocoder'):
		return '', ''  # empty output files

	distinctGeocodedLocations= {}
	distinctGeocodedList=[]
	locationsNotFound=0
	index=0

	if "Google" in geocoder:
		Google_API = GIS_pipeline_util.getGoogleAPIkey('Google-geocode-API-config.txt')
	else:
		Google_API=''

	geolocator = get_geolocator(geocoder,Google_API)

	inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)

	startTime=IO_user_interface_util.timed_alert(window, 3000, "GIS geocoder", "Started geocoding locations via the online service '" + geocoder + "' at", True, 'You can follow geocoding in command line.', True)
	# if geocoder=='Nominatim':
	# 	config_filename='GIS-geocode-config.txt'
	# 	reminders_util.checkReminder(config_filename,["GIS Nominatim geocoder"],'',True)

	geoName = 'geo-' + str(geocoder[:3])
	geocodedLocationsoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																			  geoName, locationColumnName, '', '', False,
																			  True)
	locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																			  geoName, 'Not-Found', locationColumnName, '',
																			  False, True)
	if locations=='':
		outputCsvLocationsOnly = ''
		if inputIsCoNLL == True:
			outputCsvLocationsOnly = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																	   'NER_locations', '', '', '', False, True)
			locations = GIS_location_util.extract_NER_locations(window, inputFilename, encodingValue, split_locations_prefix, split_locations_suffix, datePresent)
		else:
			# locations is a list of names of locations
			locations = GIS_location_util.extract_csvFile_locations(window, inputFilename, withHeader, locationColumnName, encodingValue)

		if locations == None or len(locations) == 0:
			return '', ''  # empty output files

	csvfile = IO_files_util.openCSVFile(geocodedLocationsoutputFilename, 'w', encodingValue)
	if csvfile=='': # permission error
		return '', '' 
	csvfileNotFound = IO_files_util.openCSVFile(locationsNotFoundoutputFilename, 'w', encodingValue)
	if csvfileNotFound=='': # permission error
		return '', '' 

	geowriter = csv.writer(csvfile)
	geowriterNotFound = csv.writer(csvfileNotFound)

	if inputIsCoNLL==True: #the filename, sentence, date were exported
		if datePresent==True:
			# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
			geowriter.writerow(['Location','Latitude','Longitude','Address','Sentence ID','Sentence','Document ID','Document','Date'])
		else:
			# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
			geowriter.writerow(['Location','Latitude','Longitude','Address','Sentence ID','Sentence','Document ID','Document'])
	else:
		# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
		geowriter.writerow(['Location','Latitude','Longitude','Address'])

	# CYNTHIA
	# ; added in SVO list of locations in SVO output (e.g., Los Angeles; New York; Washington)
	tmp_loc = []
	for item in locations:
		tmp_loc = tmp_loc + item.split(";")
	locations = tmp_loc

	for item in locations:
		index=index+1 #items in locations are NOT DISTINCT
		if str(item)!='nan' and str(item)!='':
			currRecord=str(index) + "/" + str(len(locations))
			#for CoNLL tables as input rows & columns 
			#   refer to the four fields exported by the NER locator
			if inputIsCoNLL==True: #the filename was exported in GIS_location_util
				itemToGeocode = item[0] # location in FORM
				sentenceID = item[1]
				sentence = item[2]
				documentID = item[3]
				filename = item[4]
				if datePresent==True:
					date = item[5]
			else:
				# itemToGeocode =[item[0]]
				itemToGeocode =item

			# repetition; location already in list
			if itemToGeocode in distinctGeocodedList:
				location = itemToGeocode
			else:
				distinctGeocodedList.append(itemToGeocode)
				if geocoder=='Nominatim':
					location = nominatim_geocode(geolocator,itemToGeocode,country_bias)
				else:
					location = google_geocode(geolocator,itemToGeocode,country_bias)
				if geocoder=='Nominatim':
					try:
						lat, lng, address = location.latitude, location.longitude, location.address
					except Exception as e:
						lat, lng, address = 0, 0, " LOCATION NOT FOUND BY " + geocoder
						locationsNotFound=locationsNotFound+1
						geowriterNotFound.writerow([itemToGeocode])
						print(currRecord,"     LOCATION NOT FOUND BY " + geocoder,itemToGeocode)
				else: #Google
					try: #use a try/except in case requests do not give results
						lat, lng, address = location.latitude, location.longitude, location.address #extracting lat from the request results
					except:
						lat, lng, address = 0, 0, " LOCATION NOT FOUND BY " + geocoder
						locationsNotFound=locationsNotFound+1
						geowriterNotFound.writerow([itemToGeocode])
						print(currRecord,"     LOCATION NOT FOUND BY " + geocoder,itemToGeocode)
				if lat!=0 and lng!=0:
					distinctGeocodedLocations[itemToGeocode] = (lat, lng, address)
					lat = distinctGeocodedLocations[itemToGeocode][0]
					lng = distinctGeocodedLocations[itemToGeocode][1]
					address = distinctGeocodedLocations[itemToGeocode][2]
			#print(currRecord + itemToGeocode + str(lat) + str(lng) + address+"\n")
			if lat!=0 and lng!=0:
				if inputIsCoNLL==True:
					if datePresent==True:
						geowriter.writerow([itemToGeocode, lat, lng, address, sentenceID, sentence, documentID, filename, date])
					else:
						geowriter.writerow([itemToGeocode, lat, lng, address, sentenceID, sentence, documentID, filename])
				else:
					geowriter.writerow([itemToGeocode, lat, lng, address])
	csvfile.close()
	csvfileNotFound.close()
	
	if locationsNotFound==0:
		locationsNotFoundoutputFilename='' #used NOT to open the file since there are NO errors
	else:
		if locationsNotFound==index:
			geocodedLocationsoutputFilename='' #used NOT to open the file since there are no records
			# this warning is already given 
	IO_user_interface_util.timed_alert(window, 3000, "GIS geocoder", "Finished geocoding locations via the online service '" + geocoder + "' at", True, str(locationsNotFound) + " location(s) was/were NOT geocoded out of " + str(index) + ". The list will be displayed as a csv file.\n\nPlease, check your locations and try again.\n\nA Google Earth Pro kml map file will now be produced for all successfully geocoded locations.", True, startTime)
	return geocodedLocationsoutputFilename, locationsNotFoundoutputFilename

