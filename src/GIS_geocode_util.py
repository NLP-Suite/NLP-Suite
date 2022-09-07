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
		# this will renew the SSL certificate indefinitely
		# pip install pyOpenSSL
		# pip install requests[security]
		# import ssl
		# # disable TLS certificate verification completely
		# ctx = ssl.create_default_context()
		# ctx.check_hostname = False
		# ctx.verify_mode = ssl.CERT_NONE

		geolocator = Nominatim(user_agent="NLP Suite")
		# geolocator = Nominatim(user_agent="NLP Suite", timeout=10)

	else:
		# Country specification
		# UK: domain = 'maps.google.co.uk'
		geolocator = GoogleV3(api_key=Google_API, domain='maps.google.com')
	return geolocator

# TODO MINO: add featuretype parameter
# Country specification; uses 2-digit lowercase ISO_3166 country codes
def nominatim_geocode(geolocator,loc,country_bias='',box_tuple='',restrict=False,timeout=4, featuretype=None):
	# https://geopy.readthedocs.io/en/stable/#geopy.geocoders.options
	# this will renew the SSL certificate indefinitely
	# pip install pyOpenSSL
	# pip install requests[security]

	# import ssl
	# # disable TLS certificate verification completely
	# ctx = ssl.create_default_context()
	# ctx.check_hostname = False
	# ctx.verify_mode = ssl.CERT_NONE

	# disable TLS certificate verification
	# import certifi
	# import geopy.geocoders
	# geopy.geocoders.options.default_ssl_context = ctx
	# ctx = ssl.create_default_context(cafile=certifi.where())
	# geopy.geocoders.options.default_ssl_context = ctx
	# Limits the search to a specific country or a list of countries. Country codes must be in ISO 3166-1 alpha2.
	if country_bias == '':
		country_bias = None
	# https://github.com/geopy/geopy/issues/261
	# this gives precedence to Georgia
	# bounded=1 this restricts to Georgia
	# https://developer.mapquest.com/documentation/open/nominatim-search/search/ EXPLAINS ALL PARAMS
	# Preferred area to find search results. viewbox=left,top,right,bottom
	# although given on some website the following does NOT work
	# viewbox = 34.98527546066368, -85.59790207354965, 30.770444751951388, -81.5219744485591
	# bounded can take values 0 (No, do not restrict results) or 1 (Yes, restrict results)
	# def string_to_tuples(string: str):
	"""
	This function converts a string of tuples into a list of tuples
	:param string: a string of tuples, e.g. '(1,2.3),(4,5.5)'
	:return: a list of tuples, e.g. [(1,2.3),(4,5.5)]
	"""
		# return [tuple(map(float, t.strip('()').split(','))) for t in string.split('),(')]

	if box_tuple == '':
		box_tuple = None
	else:
		box_tuple=box_tuple.replace(" ",'')
		box_tuple=[tuple(map(float, t.strip('()').split(','))) for t in box_tuple.split('),(')]
		# box_tuple = tuple([(34.98527546066368, -85.59790207354965), (30.770444751951388, -81.5219744485591)])
		# georgia viewbox 	34.98527546066368, -85.59790207354965 (upper left);
		# 					30.770444751951388, -81.5219744485591 (lower right)

	try:
		# TODO MINO: add featuretype parameter
		return geolocator.geocode(loc,language='en',country_codes=country_bias,viewbox=box_tuple, bounded=restrict, timeout=timeout, featuretype=featuretype) # TODO MINO: add country restriction
		# https: // gis.stackexchange.com / questions / 173569 / avoid - time - out - error - nominatim - geopy - openstreetmap
	except:
		print("********************************************TIMEOUT",timeout)
		if timeout<20:
			# try again, adding timeout
			try:
				# TODO MINO: add featuretype parameter
				return nominatim_geocode(geolocator,loc=loc,country_codes=country_bias,box_tuple=box_tuple,bounded=restrict,timeout=timeout + 2, featuretype=featuretype)# add 2 second for the next round
			except:
				return None
		else:
			print("Maximum number of retries to access Nominatim server exceeded in geocoding " + loc)
			raise

# https://developers.google.com/maps/documentation/embed/get-api-key
# console.developers.google.com/apis
def google_geocode(geolocator,loc,region=None,timeout=10):
	# print("Processing Google location for geocoding:",loc)
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
			geocoder,country_bias,area,restrict,
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
		Google_API = GIS_pipeline_util.getGoogleAPIkey('Google-geocode-API_config.csv')
	else:
		Google_API=''

	geolocator = get_geolocator(geocoder,Google_API)

	inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)

	startTime=IO_user_interface_util.timed_alert(window, 3000, "GIS geocoder", "Started geocoding locations via the online service '" + geocoder + "' at",
												 True, '', True,'',True)
	# if geocoder=='Nominatim':
	# 	config_filename='GIS-geocode_config.csv'
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
		if datePresent==True:
			geowriter.writerow(['Location','Latitude','Longitude','Address', 'Date'])
		else:
			geowriter.writerow(['Location', 'Latitude', 'Longitude', 'Address'])

	# CYNTHIA
	# ; added in SVO list of locations in SVO output (e.g., Los Angeles; New York; Washington)
	tmp_loc = []
	for item in locations:
		if ";" in item[0]:
			sep_locs = item[0].split(";")
			for l in sep_locs:
				tmp_loc.append([l] + item[1:])
		else:
			tmp_loc.append(item)
	locations = tmp_loc

	for item in locations:
		index=index+1 #items in locations are NOT DISTINCT
		print("Processing location " + str(index) + "/" + str(len(locations)) + ": " + item[0])
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
				itemToGeocode =item[0]
				NER_Tag = item[len(item)-1] # TODO MINO: add NER_Tag
				if datePresent==True:
					date=item[1]

			# avoid repetition; location already in list
			if itemToGeocode in distinctGeocodedList:
				location = itemToGeocode
			else:
				print("   Geocoding DISTINCT location: " + itemToGeocode)
				distinctGeocodedList.append(itemToGeocode)
				if geocoder=='Nominatim':
					# TODO MINO: add NER_Tag as input for featuretype parameter
					location = nominatim_geocode(geolocator,loc=itemToGeocode,country_bias=country_bias,box_tuple=area,restrict=restrict,featuretype=NER_Tag.lower())
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
					if datePresent==True:
						geowriter.writerow([itemToGeocode, lat, lng, address, date])
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
	IO_user_interface_util.timed_alert(window, 3000, "GIS geocoder", "Finished geocoding locations via the online service '" + geocoder + "' at", True, str(locationsNotFound) + " location(s) was/were NOT geocoded out of " + str(index) + ". The list will be displayed as a csv file.\n\nPlease, check your locations and try again.\n\nA Google Earth Pro kml map file will now be produced for all successfully geocoded locations.", True, startTime, True)
	return geocodedLocationsoutputFilename, locationsNotFoundoutputFilename
