import sys

import pandas as pd

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS_geocode_util",['os','tkinter','csv','geopy'])==False:
	sys.exit(0)

import IO_files_util
import IO_user_interface_util
import csv
import tkinter.messagebox as mb
import os # TODO MINO GIS create kml record

from geopy import Nominatim
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut
import simplekml # TODO MINO GIS create kml record
import pandas as pd # TODO MINO GIS create kml record
from datetime import datetime # TODO MINO GIS date option
import dateutil

import GIS_location_util
import GIS_file_check_util
import IO_internet_util
import GIS_pipeline_util
import GIS_Google_pin_util # TODO MINO GIS create kml record
import IO_csv_util # TODO MINO GIS create kml record

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

# Country specification; uses 2-digit lowercase ISO_3166 country codes
def nominatim_geocode(geolocator, loc, country_bias='', box_tuple='', restrict=False, timeout=4, featuretype=None):
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
		return geolocator.geocode(loc,language='en',country_codes=country_bias,viewbox=box_tuple, bounded=restrict, timeout=timeout, featuretype=featuretype)
		# https: // gis.stackexchange.com / questions / 173569 / avoid - time - out - error - nominatim - geopy - openstreetmap
	except:
		print("******************************************** Nominatim TIMEOUT", timeout)
		if timeout<20:
			# try again, adding timeout
			try:
				return nominatim_geocode(geolocator, loc=loc, country_codes=country_bias, box_tuple=box_tuple, bounded=restrict, timeout=timeout + 2, featuretype=featuretype)# add 2 second for the next round
			except:
				return None
		else:
			print("Maximum number of retries to access Nominatim server exceeded in geocoding " + loc)
			raise

# https://developers.google.com/maps/documentation/embed/get-api-key
# console.developers.google.com/apis
def google_geocode(geolocator, loc, region=None, timeout=10):
	# print("Processing Google location for geocoding:",loc)
	region='.US'
	try:
		return geolocator.geocode(loc, region=region, timeout=timeout)
	except GeocoderTimedOut:
		return google_geocode(geolocator, loc, region=region, timeout=timeout)

# the function processes an INPUT list of NON DISTINCT locations
#   Since you do NOT want to geocode the same location multiple times and be thrown out by the selected geocoder service
#   the function filters DISTINCT locations to be passed for processing to the function nominatim_geocode
# Expects to have a list with sub lists containing [filename, location name 1, loc name 2...]
# creates csv file of geocoded values
# called by GIS_Google_Earth_util
# return 2 filenames of csv files of geocoded and non-geocoded locations
#	 filenames are '' if empty, perhaps for a permission error

def process_geocoded_data_for_kml(window,locations, inputFilename, outputDir,
			locationColumnName, encodingValue):
	Google_API = GIS_pipeline_util.getGoogleAPIkey(window, 'Google-geocode-API_config.csv')
	kml = simplekml.Kml()
	icon_url = GIS_Google_pin_util.pin_icon_select(['Pushpins'], ['red'])
	kmloutputFilename = inputFilename.replace('.csv', '.kml')
	head, tail = os.path.split(kmloutputFilename)
	# when you are processing a csv file in input separately from the regular input file,
	# 	you do not want to save the kml file in the input directory of the csv file
	# 	but in the regular output directory
	kmloutputFilename = outputDir + os.sep + tail

	inputIsCoNLL, inputIsGeocoded, withHeader, \
		headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)
	input_df = pd.read_csv(inputFilename, encoding=encodingValue)
	# input_df = input_df[['Location', 'Latitude', 'Longitude']]
	input_df = input_df.reset_index()
	for index, row in input_df.iterrows():
		location = row['Location']
		lat = row['Latitude']
		lng = row['Longitude']
		if datePresent:
			date = row['Date']

		# try:
		# 	description = row['Description']
		# except:
		# 	print('No description field available')


		# TODO MINO GIS create kml record
		print("   Processing geocoded record for kml file for Google Earth Pro " + str(index+1) + '/' + str(len(input_df.index)))
		pnt = kml.newpoint(coords=[(lng, lat)])
		pnt.style.iconstyle.icon.href = icon_url
		pnt.name = location
		pnt.style.labelstyle.scale = '1'
		# pnt.style.labelstyle.color = simplekml.Color.rgb(int(r_value), int(g_value), int(b_value))
		# the code would break if no sentence is passed (e.g., from DB_PC-ACE)
		try:
			label = 'Event'
			sentence = input_df.at[index-1, label]
			pnt.description = "<i><b>Location</b></i>: " + location + "<br/><br/>" \
																		   "<i><b>Description</b></i>: " + sentence + "<br/><br/>"
		except:
			pnt.description = "<i><b>Location</b></i>: " + location + "<br/><br/>"
		# TODO MINO GIS date option
		if datePresent:
			GGPdateFormat = convertToGGP(date)
			pnt.timespan.begin = GGPdateFormat
			pnt.timespan.end = GGPdateFormat

	try:
		kml.save(kmloutputFilename)
	except:
		mb.showwarning(title='kml file save failure',
					   message="Saving the kml file failed. A typical cause of failure is is bad characters in the input text/csv file(s) (e.g, 'LINE TABULATION' or 'INFORMATION SEPARATOR ONE' characters).\n\nThe GIS KML script will now try to automattically clean the kml file, save it in safe mode, and open the kml file in Google Earth Pro.\n\nIf the file cleaning was successful, the map will display correctly. If not, Google Earth Pro will open exactly on the bad character position. Remove the character and save the file. But, you should really clean the original input txt/csv file.")
		# Save kml regardless of validity. Let the user find any bad characters.
		kml.save(kmloutputFilename, False)
		# Clean out any "LINE TABULATION" and "INFORMATION SEPARATOR ONE" characters from the input (causes error with KML).
		with open(kmloutputFilename, 'r+', encoding='utf_8', errors='ignore') as kmlfile:
			content = kmlfile.read()
			content = content.replace(u"\u000B", "")
			content = content.replace(u"\u001F", "")
			kmlfile.seek(0)
			kmlfile.write(content)
			kmlfile.truncate()
	return kmloutputFilename

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
	nonDistinctNotGeocodedList=[]
	nonDistinctNotGeocodedFull=[]
	locationsNotFound=0
	index=0

	if "Google" in geocoder:
		Google_API = GIS_pipeline_util.getGoogleAPIkey(window,'Google-geocode-API_config.csv')
	else:
		Google_API=''

	geolocator = get_geolocator(geocoder,Google_API)
	kml = simplekml.Kml()
	icon_url = GIS_Google_pin_util.pin_icon_select(['Pushpins'], ['red'])

	inputIsCoNLL, inputIsGeocoded, withHeader, \
		headers, datePresent, filenamePositionInCoNLLTable = GIS_file_check_util.CoNLL_checker(inputFilename)
	input_df = pd.read_csv(inputFilename, encoding=encodingValue)

	startTime=IO_user_interface_util.timed_alert(window, 2000, "GIS geocoder", "Started geocoding locations via the online service '" + geocoder + "' at",
												 True, '', True,'',True)
	# if geocoder=='Nominatim':
	# 	config_filename='GIS-geocode_config.csv'
	# 	reminders_util.checkReminder(config_filename,["GIS Nominatim geocoder"],'',True)

	geoName = 'geo-' + str(geocoder[:3])
	geocodedLocationsOutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																			  geoName, locationColumnName, '', '', False,
																			  True)
	locationsNotFoundoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																			  geoName, 'Not-Found', locationColumnName, '',
																			  False, True)
	locationsNotFoundNonDistinctoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS',
																			geoName, 'Not-Found-Non-Distinct', locationColumnName, '',
																			False, True)
	# TODO MINO GIS create kml record
	kmloutputFilename = geocodedLocationsOutputFilename.replace('.csv', '.kml')

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

	csvfile = IO_files_util.openCSVFile(geocodedLocationsOutputFilename, 'w', encodingValue)
	if csvfile=='': # permission error
		return '', ''
	csvfileNotFound = IO_files_util.openCSVFile(locationsNotFoundoutputFilename, 'w', encodingValue)
	if csvfileNotFound=='': # permission error
		return '', ''
	csvfileNotFoundNonDistinct = IO_files_util.openCSVFile(locationsNotFoundNonDistinctoutputFilename, 'w', encodingValue)
	if csvfileNotFoundNonDistinct=='': # permission error
			return '', ''
	geowriter = csv.writer(csvfile)
	geowriterNotFound = csv.writer(csvfileNotFound)
	geowriterNotFoundNonDistinct = csv.writer(csvfileNotFoundNonDistinct)

	# define variable
	NER_Tag = ''

	if inputIsCoNLL==True: #the filename, sentence, date were exported
		if datePresent==True:
			# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
			geowriter.writerow(['Location','NER Tag','Latitude','Longitude','Address','Sentence ID','Sentence','Document ID','Document','Date'])
		else:
			# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
			geowriter.writerow(['Location','NER Tag','Latitude','Longitude','Address','Sentence ID','Sentence','Document ID','Document'])
	else:
		# always use the locationColumnName variable passed by algorithms to make sure locations are then matched
		if datePresent==True:
			geowriter.writerow(['Location','NER Tag','Latitude','Longitude','Address', 'Date'])
		else:
			geowriter.writerow(['Location','NER Tag','Latitude', 'Longitude', 'Address'])
	geowriterNotFound.writerow(['Location','NER Tag'])
	geowriterNotFoundNonDistinct.writerow(['Location','NER Tag'])
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
	skipNext = False
	index_list = []
	for item in locations:
		index=index+1 #items in locations are NOT DISTINCT
		if skipNext:
			continue
		if str(item)!='nan' and str(item)!='':
			currRecord=str(index) + "/" + str(len(locations))
			print("Processing location " + currRecord + " for geocoding: "
				  + str(item[0]) + " (NER tag: " + str(item[len(item) - 1]) + ")")
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
				itemToGeocode =item[0]
				NER_Tag = item[len(item)-1]
				if NER_Tag == 'COUNTRY':
					NER_Tag_nominatim = 'country'
				elif NER_Tag == 'STATE_OR_PROVINCE':
					NER_Tag_nominatim = 'state'
				elif NER_Tag == 'CITY':
					NER_Tag_nominatim = 'city'

				if datePresent:
					date=item[1]

			# avoid repetition so as not to access the geocoder service several times for the same location;
			# 	location already in list
			if itemToGeocode in distinctGeocodedList:
				location = itemToGeocode
				# TODO: special case for 'America': convert to 'United States'
				if itemToGeocode == 'America':
					itemToGeocode = 'United States'
				if itemToGeocode in nonDistinctNotGeocodedList:
					nonDistinctNotGeocodedList.append(itemToGeocode)
					nonDistinctNotGeocodedFull.append((itemToGeocode,NER_Tag))
					lat = lng = 0 # TODO set 0 for lat and lng since itemToGeocode is in notGeocodedList
				else:
					lat = distinctGeocodedLocations[itemToGeocode][0]
					lng = distinctGeocodedLocations[itemToGeocode][1]
					address = distinctGeocodedLocations[itemToGeocode][2]
			else:
				print("   Geocoding DISTINCT location: " + itemToGeocode)
				# TODO special case for 'America': convert to 'United States', so that 'United States' is appended to distinctGeocodedList
				if itemToGeocode == 'America':
					itemToGeocode = 'United States'
				distinctGeocodedList.append(itemToGeocode)
				#distinctGeocodedList.add(itemToGeocode)
				if geocoder=='Nominatim':
					NER_Tag_nominatim = ''
					# CoreNLP NER tag for continents is often wrong and as a result Nominatim geocodes them wrongly
					#	we should skip them, particularly when they are lowercase
					# continents='Africa, Antarctica, Asia, Australia, Europe, Oceania, North America, South America'
					if itemToGeocode == 'Africa' or \
						itemToGeocode == 'Antarctica' or \
						itemToGeocode == 'Asia' or \
						itemToGeocode == 'Australia' or \
						itemToGeocode == 'Europe' or \
						itemToGeocode == 'Oceania' or \
						itemToGeocode == 'North America' or \
						itemToGeocode == 'South America':
						NER_Tag_nominatim='continent'
					location = nominatim_geocode(geolocator,loc=itemToGeocode,country_bias=country_bias,box_tuple=area,restrict=restrict,featuretype=NER_Tag_nominatim)
				else:
					location = google_geocode(geolocator,itemToGeocode,country_bias)
				# location is None when not found
				if geocoder=='Nominatim':
					try:
						lat, lng, address = location.latitude, location.longitude, location.address
					except Exception as e:
						lat, lng, address = 0, 0, " LOCATION NOT FOUND BY " + geocoder
						locationsNotFound=locationsNotFound+1
						geowriterNotFound.writerow([itemToGeocode, NER_Tag])
						nonDistinctNotGeocodedList.append(itemToGeocode)
						nonDistinctNotGeocodedFull.append((itemToGeocode,NER_Tag))
						print(currRecord,"     LOCATION NOT FOUND BY " + geocoder,itemToGeocode)
				else: #Google
					try: #use a try/except in case requests do not give results
						lat, lng, address = location.latitude, location.longitude, location.address #extracting lat from the request results
					except:
						lat, lng, address = 0, 0, " LOCATION NOT FOUND BY " + geocoder
						locationsNotFound=locationsNotFound+1
						geowriterNotFound.writerow([itemToGeocode, NER_Tag])
						nonDistinctNotGeocodedList.append(itemToGeocode)
						nonDistinctNotGeocodedFull.append((itemToGeocode,NER_Tag))
						print(currRecord,"     LOCATION NOT FOUND BY " + geocoder,itemToGeocode)
				if lat!=0 and lng!=0:
					distinctGeocodedLocations[itemToGeocode] = (lat, lng, address)
					lat = distinctGeocodedLocations[itemToGeocode][0]
					lng = distinctGeocodedLocations[itemToGeocode][1]
					address = distinctGeocodedLocations[itemToGeocode][2]
			#print(currRecord + itemToGeocode + str(lat) + str(lng) + address+"\n")
			if lat!=0 and lng!=0:
				if inputIsCoNLL==True:
					if datePresent:
						geowriter.writerow([itemToGeocode, NER_Tag, lat, lng, address, sentenceID, sentence, documentID, filename, date])
					else:
						geowriter.writerow([itemToGeocode, NER_Tag, lat, lng, address, sentenceID, sentence, documentID, filename])
				else:
					if datePresent:
						geowriter.writerow([itemToGeocode, NER_Tag, lat, lng, address, date])
					else:
						geowriter.writerow([itemToGeocode, NER_Tag, lat, lng, address])

				# TODO MINO GIS create kml record
				print("   Processing geocoded record for kml file for Google Earth Pro")
				pnt = kml.newpoint(coords=[(lng, lat)])
				pnt.style.iconstyle.icon.href = icon_url
				# pnt.name = itemToGeocode
				pnt.style.labelstyle.scale = '1'
				# pnt.style.labelstyle.color = simplekml.Color.rgb(int(r_value), int(g_value), int(b_value))
				# the code would break if no sentence is passed (e.g., from DB_PC-ACE)
				try:
					sentence = input_df.at[index-1, 'Sentence']
					document = input_df.at[index - 1, 'Document']
					document = os.path.split(IO_csv_util.undressFilenameForCSVHyperlink(document))[1]
					pnt.description = "<i><b>Location</b></i>: " + itemToGeocode + "<br/><br/>" \
																				   "<i><b>Sentence</b></i>: " + sentence + "<br/><br/>" + \
									  "<i><b>Document</b></i>: " + document
				except:
					pnt.description = "<i><b>Location</b></i>: " + itemToGeocode + "<br/><br/>"
				# TODO MINO GIS date option
				if datePresent:
					GGPdateFormat = convertToGGP(date)
					pnt.timespan.begin = GGPdateFormat
					pnt.timespan.end = GGPdateFormat

	[geowriterNotFoundNonDistinct.writerow([item[0], item[1]]) for item in nonDistinctNotGeocodedFull]
	csvfile.close()
	csvfileNotFound.close()
	csvfileNotFoundNonDistinct.close()
	# TODO MINO GIS create kml record
	try:
		kml.save(kmloutputFilename)
	except:
		mb.showwarning(title='kml file save failure',
					   message="Saving the kml file failed. A typical cause of failure is is bad characters in the input text/csv file(s) (e.g, 'LINE TABULATION' or 'INFORMATION SEPARATOR ONE' characters).\n\nThe GIS KML script will now try to automattically clean the kml file, save it in safe mode, and open the kml file in Google Earth Pro.\n\nIf the file cleaning was successful, the map will display correctly. If not, Google Earth Pro will open exactly on the bad character position. Remove the character and save the file. But, you should really clean the original input txt/csv file.")
		# Save kml regardless of validity. Let the user find any bad characters.
		kml.save(kmloutputFilename, False)
		# Clean out any "LINE TABULATION" and "INFORMATION SEPARATOR ONE" characters from the input (causes error with KML).
		with open(kmloutputFilename, 'r+', encoding='utf_8', errors='ignore') as kmlfile:
			content = kmlfile.read()
			content = content.replace(u"\u000B", "")
			content = content.replace(u"\u001F", "")
			kmlfile.seek(0)
			kmlfile.write(content)
			kmlfile.truncate()

	if locationsNotFound==0:
		locationsNotFoundoutputFilename='' #used NOT to open the file since there are NO errors
	else:
		if locationsNotFound==index:
			geocodedLocationsOutputFilename='' #used NOT to open the file since there are no records
			# this warning is already given
	IO_user_interface_util.timed_alert(window, 2000, "GIS geocoder", "Finished geocoding " + str(len(locations)) + " locations via the online service '" + geocoder + "' at", True, str(locationsNotFound) + " location(s) was/were NOT geocoded out of " + str(index) + ". The list will be displayed as a csv file.\n\nPlease, check your locations and try again.\n\nA Google Earth Pro kml map file will now be produced for all successfully geocoded locations.", True, startTime, True)
	return geocodedLocationsOutputFilename, locationsNotFoundoutputFilename, locationsNotFoundNonDistinctoutputFilename, kmloutputFilename

# TODO MINO GIS date option
# from GIS_KML_util
def convertToGGP(date):
	GGPdateFormat = ''
	if 'float' in str(type(date)): # this occurs when dealing with an integer YEAR only
		date=str(int(date))
	if 'int' in str(type(date)): # this occurs when dealing with an integer YEAR only
		date=str(int(date))
	if date != 'nan' and date != '':
		fmts = ('%Y', '%y', '%Y-%m-%d', '%y-%m-%d', '%Y-%m', '%y-%m',
				'%Y-%B-%d', '%y-%B-%d', '%Y-%b-%d', '%y-%b-%d', '%Y-%B', '%y-%B', '%Y-%b', '%y-%b'
				'%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y', '%m-%Y', '%m-%y',
				'%B-%d-%Y', '%B-%d-%y', '%b-%d-%Y', '%b-%d-%y', '%d-%B-%Y', '%d-%B-%y',
				'%d-%b-%Y', '%d-%b-%y', '%m-%Y', '%m-%y', '%B-%Y', '%B-%y', '%b-%Y', '%b-%y')
		for e in date.splitlines():
			for fmt in fmts:
				try:
					t = datetime.strptime(e, fmt)
					break
				except ValueError as err:
					pass
		try:
			currentDateFormat = dateutil.parser.parse(date)
		except:
			mb.showerror(title='Date error',
							message="There was an error in processing the date '" + date + "'.\n\nThe date format '" + fmt + "' was automatically applied to process the date, where format values are as follows:\n%B or %b   alphabetic month name in full or first 3 characters;\n%m   2-digit month (1 to 12);\n%d   2-digit day of the month (1 to 31);\n%Y   4-digit and %y 2-digit year (1918, 18).\n\nBut... either\n1.   the format automatically applied is incorrect for the date;\n2.   the date is in unrecognized format (e.g., it contains time besides date);\n3.   the date is prior to 1900. The library 'strftime' used here to deal with dates cannot process dates prior to 1900 in Windows.")
		# years before 1900 cannot be used
		# pre 1900 dates may give a problem in Windows: ValueError: format %y requires year >= 1900 on Windows
		try:
			GGPdateFormat = currentDateFormat.strftime('%Y-%m-%d')
		except:
			mb.showerror(title='Date error',
							message="There was an error in processing the date '" + date + "'.\n\nThe date format '" + fmt + "' was automatically applied to process the date, where format values are as follows:\n%B or %b   alphabetic month name in full or first 3 characters;\n%m   2-digit month (1 to 12);\n%d   2-digit day of the month (1 to 31);\n%Y   4-digit and %y 2-digit year (1918, 18).\n\nBut... either\n1.   the format automatically applied is incorrect for the date;\n2.   the date is in unrecognized format (e.g., it contains time besides date);\n3.   the date is prior to 1900. The library 'strftime' used here to deal with dates cannot process dates prior to 1900 in Windows.")
		return GGPdateFormat
