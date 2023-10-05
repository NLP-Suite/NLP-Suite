import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS_location_util",['re','tkinter','csv','pandas'])==False:
	sys.exit(0)

import tkinter.messagebox as mb
import re
import pandas as pd
import csv

import CoNLL_util
import IO_csv_util
import IO_user_interface_util

# inputFilename is a csv file
# inputFilename is the locations file generated by NER; with sentence and other fields
# InputCodedCsvFile is the geocoded file
# the function matches the records of the location file, with sentences, and the geocoded data with lat and long
# TODO MINO GIS convert this function to pandas
def extract_index(inputFilename, InputCodedCsvFile, encodingValue, location_var_name):

	# startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS extract_index ', 'Started running extract_index algorithm at',
	# 											   True, '', True, '', silent=True)

	inputfile = pd.read_csv(InputCodedCsvFile, encoding=encodingValue, on_bad_lines='skip')
	data = pd.read_csv(inputFilename, encoding=encodingValue, on_bad_lines='skip')
	headers = data.columns.values.tolist()
	if len(inputfile)==0:
		return []
	location_num=0
	for m in range(len(headers)):
		if location_var_name == headers[m]:
			location_num = m
	index_list = inputfile['Location'].isin(data['Location'])
	index_list = [i+1 for i,bool in enumerate(index_list) if bool]
	data = data.values.tolist()

	# IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS extract_index', 'Finished running extract_index algorithm at', True, '',
	# 								   True, startTime, silent=True)
	list_to_return = index_list, data, headers, location_num
	return list_to_return

#the CoNLL table includes the filename; the position in the table varies with old and new CoNLL
# returns filename, location, sentence, date (if present)
def extract_NER_locations(window,conllFile,encodingValue,split_locations_prefix,split_locations_suffix,datePresent):
	filenamePositionInCoNLLTable=12
	# startTime=IO_user_interface_util.timed_alert(window, 2000, 'NER locations extraction', "Started extracting NER locations from CoNLL table at",
	# 											 True,'', True, '', True)

	# re.sub(pattern, repl, string, count=0, flags=0)
	split_locations_prefix = re.sub("[^\w]", " ",  split_locations_prefix).split()
	if encodingValue=='':
		encodingValue = 'utf-8'
	dt = pd.read_csv(conllFile,encoding=encodingValue, on_bad_lines='skip')
	numDocs=dt['Document ID'].max()
	numRecords=dt['Record ID'].max()
	currentRecord=0
	sentence_str=""
	# 0 & 1 so that the first sentence can be computed, since the first sentence is always 1
	sentenceID=1
	documentID=1
	# currList contains the info for the current location in the CoNLL table
	locList, currList, locationsOnlyList = [], [], []
	tempLocation=''
	# loop through all records of the CoNLL table
	# print("The script will list the current record position in the CoNLL table out of all CoNLL records and the sentenceID and recordID")
	for index, row in dt.iterrows():
		if row[4] in ['LOCATION','STATE_OR_PROVINCE','CITY','COUNTRY']: #col 4 is NER
			# do NOT compute the same sentence for the same document
			if (sentenceID==1 and documentID==1) or (row[10]!=sentenceID and row[11]==documentID):
				currentRecord, sentence_str = CoNLL_util.compute_sentence(conllFile,currentRecord,row[10],row[11])
			if row[filenamePositionInCoNLLTable] in currList:
				# No need to display the filename in Description when only one file is processed
				# A blank value for the filename will be checked in Description to avoid displaying it
				if numDocs!=1:
					# currList.append(row[filenamePositionInCoNLLTable]) #append filename
					if "=dressforhyperlink" in str(row[filenamePositionInCoNLLTable]):
						currList.append(row[filenamePositionInCoNLLTable])  # append filename
					else:
						currList.append(IO_csv_util.dressFilenameForCSVHyperlink(row[filenamePositionInCoNLLTable])) #append filename
			elif len(currList) == 0:
				# # A blank value for the filename will be checked in Description to avoid displaying it
				if row[1].lower() in split_locations_prefix:
					# the current location value (e.g., las) needs to be merged with the next row value (e.g., las vegas)
					tempLocation=row[1]
					continue
				else:
					if tempLocation!='': #we are on the next row
						currList.append(tempLocation + ' ' + row[1]) #col 1 is the FORM value
						currList.append(row[4])  # append NER tag (e.g., COUNTRY)
						tempLocation=''
					else:
						currList.append(row[1]) #col 1 is the FORM value (e.g., Italy)
						currList.append(row[4])  # append NER tag (e.g., COUNTRY)

				currList.append(sentenceID)
				currList.append(sentence_str.lstrip())
				currList.append(documentID)

				# A blank value for the filename will be checked in Description to avoid displaying it
				# currList = [row[filenamePositionInCoNLLTable]] #col 11 is the filename
				if "=hyperlink" in str(row[filenamePositionInCoNLLTable]):
					currList.append(row[filenamePositionInCoNLLTable])  # append filename
				else:
					currList.append(IO_csv_util.dressFilenameForCSVHyperlink(
						row[filenamePositionInCoNLLTable]))  # col 11 is the filename

				# years before 1900 cannot be used
				# pre 1900 dates may give a problem in Windows: ValueError: format %y requires year >= 1900 on Windows
				# https://stackoverflow.com/questions/10263956/use-datetime-strftime-on-years-before-1900-require-year-1900
				# There are various ways to alter strftime so that it handles pre-1900 dates
				if currList!=['']: # do NOT append the date to an empty list
					if datePresent==True:
						currList.append(row[13]) #col 12 is the date, IFF present
					else:
						currList.append('')
			if currList!=[''] and len(currList)>1: # sometimes only the filename is printed; no location
				locList.append(currList)
				#locList+=currList
			print("Processing NER location " + str(index)+"/"+str(numRecords)+ " " + str(sentenceID)+"/"+str(documentID) + "   " + str(currList)+ "\n")
			currList = []
			if row[9]!=sentenceID:
				sentenceID=row[10]
			if row[10]!=documentID:
				documentID=row[11]
	if len(locList)==0:
		mb.showwarning(title='NER locations', message="There are no NER tags for 'LOCATION','STATE_OR_PROVINCE','CITY','COUNTRY' in your CoNLL file\n\n" + conllFile + "\n\nThere is no geocoding to be done.")
	# else:
	# 	IO_user_interface_util.timed_alert(window, 2000, 'NER locations extraction', "Finished extracting NER locations from CoNLL table at", True, '', True, startTime, True)
	# returns filename, location, sentence, date (if present)
	# return sorted(locList)
	# do not sort locations so that you can check from wrong CoreNLP NER tag, e.g., South America as South = LOCATION, America = COUNTRY
	return locList

# called from GIS_Google_util
#locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
def extract_csvFile_locations(window,inputFilename,withHeader,locationColumnNumber,encodingValue, datePresent, dateColumnNumber):
	# startTime=IO_user_interface_util.timed_alert(window, 2000, 'csv file locations extraction', "Started extracting locations from csv file at",
	# 											 True,'', True, '', True)
	locList = []
	#latin-1 for the Italian or the code will break
	try:
		dt = pd.read_csv(inputFilename,encoding=encodingValue, on_bad_lines='skip')
		count_row = dt.shape[0]  # gives number of row count
		#count_col = dt.shape[1]  # gives number of col count
	except:
		mb.showerror(title='Input file error', message="There was an error in the function 'Extract csv locations' reading the input csv file\n" + str(inputFilename) + "\nMost likely, the error is due to an encoding error. Your current encoding value is '" + encodingValue + "'.\n\nSelect a different encoding value and try again.")
		return
	if withHeader==True:

		index=1 #skip header
		for index, row in dt.iterrows():
			print("Processing record " + str(index+1)+"/"+str(count_row)+ " in csv file; location: " + str(row[locationColumnNumber]))
			if str(row[locationColumnNumber])!='' and str(row[locationColumnNumber])!='nan':
				if datePresent == True:
					try:
						#NER Tag may not be present when an expernal input csv file of locations is passed
						locList.append([row[locationColumnNumber], row[dateColumnNumber], row['NER']])
					except:
						locList.append([row[locationColumnNumber], row[dateColumnNumber]])
				else:
					# the code would break if no NER Tag is passed (e.g., from DB_PC-ACE)
					try:
						locList.append([row[locationColumnNumber],[index],[0], row['NER']])
					except:
						locList.append([row[locationColumnNumber], [index], [0]])

	if len(locList)==0:
		mb.showwarning(title='Locations', message="There are no locations in your input file\n\n" + inputFilename + "\n\nThere is no geocoding to be done.\n\nNo map via Google Earth Pro and Google Maps can be done.")
		return
	# IO_user_interface_util.timed_alert(window, 2000, 'csv file locations extraction', "Finished extracting locations from csv file at", True, '', True, startTime, True)
	# return sorted(locList)
	# do not sort locations so that you can check from wrong CoreNLP NER tag, e.g., South America as South = LOCATION, America = COUNTRY

	# locList is a list of four items: location mane, row index in the locations table, date, NER tag (e.g., COUNTRY)
	return locList
