import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS_location_util",['re','tkinter','csv','pandas'])==False:
	sys.exit(0)

import tkinter.messagebox as mb
import re
import pandas as pd
import csv

import IO_CoNLL_util
import IO_csv_util
import IO_user_interface_util

def extract_index(inputFilename, InputCodedCsvFile, encodingValue, location_var_name):
	geo_index = 0
	index = 0
	index_list = []

	inputfile = csv.reader(open(InputCodedCsvFile,'r',encoding = encodingValue,errors='ignore'))
	first_row = next(inputfile) #skip header

	withHeader_var = IO_csv_util.csvFile_has_header(inputFilename) # check if the file has header
	data, headers = IO_csv_util.get_csv_data(inputFilename,withHeader_var) # get the data and header

	geo_withHeader_var = IO_csv_util.csvFile_has_header(InputCodedCsvFile) # check if the file has header
	geo_data, geo_headers = IO_csv_util.get_csv_data(InputCodedCsvFile,geo_withHeader_var) # get the data and header

	if len(geo_data)==0:
		return index_list

	names = []
	location_num=0
	for m in range(len(headers)):
		if location_var_name == headers[m]:
			location_num = m

	for n in range(len(data)):
		names.append(data[n][location_num])

	for row in inputfile:
		geo_index += 1
		geo_name = geo_data[geo_index-1][0]

		for l in range(len(names)):
			if geo_name == names[l]:
				index = l
				if index not in index_list:
					break
		index_list.append(index)

	for i in range(len(index_list)):
		index_list[i] += 1

	return index_list

#the CoNLL table includes the filename; the position in the table varies with old and new CoNLL
# returns filename, location, sentence, date (if present)
# called by GIS_Google_Earth_util
def extract_NER_locations(window,conllFile,encodingValue,split_locations_prefix,split_locations_suffix,datePresent):
	filenamePositionInCoNLLTable=11
	IO_user_interface_util.timed_alert(window, 2000, 'NER locations extraction', "Started extracting NER locations from CoNLL table at", True)
	print("NER location extractions from CoNLL table started.")

	# re.sub(pattern, repl, string, count=0, flags=0)
	split_locations_prefix = re.sub("[^\w]", " ",  split_locations_prefix).split()
	if encodingValue=='':
		encodingValue = 'utf-8'
	dt = pd.read_csv(conllFile,encoding = encodingValue)
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
	print("The script will list the current record position in the CoNLL table out of all CoNLL records and the sentenceID and recordID")
	for index, row in dt.iterrows():
		if row[4] in ['LOCATION','STATE_OR_PROVINCE','CITY','COUNTRY']: #col 4 is NER
			# do NOT compute the same sentence for the same document
			if (sentenceID==1 and documentID==1) or (row[9]!=sentenceID and row[10]==documentID):
				currentRecord, sentence_str = IO_CoNLL_util.compute_sentence(conllFile,currentRecord,row[9],row[10])
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
				# A blank value for the filename will be checked in Description to avoid displaying it
				# currList = [row[filenamePositionInCoNLLTable]] #col 11 is the filename
				if "=hyperlink" in str(row[filenamePositionInCoNLLTable]):
					currList.append(row[filenamePositionInCoNLLTable])  # append filename
				else:
					currList = [IO_csv_util.dressFilenameForCSVHyperlink(row[filenamePositionInCoNLLTable])] #col 11 is the filename
				if row[1].lower() in split_locations_prefix:
					# the currrent location value (e.g., las) needs to be merged with the next row value (e.g., las vegas)
					tempLocation=row[1]
				else:
					if tempLocation!='': #we are on the next row 
						currList.append(tempLocation + ' ' + row[1]) #col 1 is the FORM value
						tempLocation=''
					else:
						currList.append(row[1]) #col 1 is the FORM value
					currList.append(sentenceID)
					currList.append(sentence_str)
					currList.append(documentID)
					# years before 1900 cannot be used
					# pre 1900 dates may give a problem in Windows: ValueError: format %y requires year >= 1900 on Windows
					# https://stackoverflow.com/questions/10263956/use-datetime-strftime-on-years-before-1900-require-year-1900
					# There are various ways to alter strftime so that it handles pre-1900 dates
					if currList!=['']: # do NOT append the date to an empty list
						if datePresent==True:
							currList.append(row[12]) #col 12 is the date, IFF present
						else:
							currList.append('')
			if currList!=[''] and len(currList)>1: # sometimes only the filename is printed; no location
				locList.append(currList)
				#locList+=currList
			print("Processing NER location " + str(index)+"/"+str(numRecords)+ " " + str(sentenceID)+"/"+str(documentID) + "   " + str(currList)+ "\n")
			currList = []
			if row[9]!=sentenceID:
				sentenceID=row[9]
			if row[10]!=documentID:
				documentID=row[10]
	if len(locList)==0:
		mb.showwarning(title='NER locations', message="There are no NER tags for 'LOCATION','STATE_OR_PROVINCE','CITY','COUNTRY' in your CoNLL file\n\n" + inputFilename + "\n\nThere is no geocoding to be done.")
	else:
		IO_user_interface_util.timed_alert(window, 2000, 'NER locations extraction', "Finished extracting NER locations from CoNLL table at", True)
		print("NER locations extraction from CoNLL table finished.")
	# returns filename, location, sentence, date (if present)
	return sorted(locList)

# called from GIS_Google_util
#locationColumnNumber where locations are stored in the csv file; any changes to the columns will result in error
def extract_csvFile_locations(window,inputFilename,withHeader,locationColumnNumber,encodingValue):
	# IO_user_interface_util.timed_alert(window, 2000, 'csv file locations extraction', "Started extracting locations from csv file at", True)
	print("Started extracting locations from csv file")
	locList = []
	#latin-1 for the Italian or the code will break
	try:
		dt = pd.read_csv(inputFilename,encoding = encodingValue)
		count_row = dt.shape[0]  # gives number of row count
		#count_col = dt.shape[1]  # gives number of col count
	except:
		mb.showerror(title='Input file error', message="There was an error in the function 'Extract csv locations' reading the input csv file\n" + str(inputFilename) + "\nMost likely, the error is due to an encoding error. Your current encoding value is '" + encodingValue + "'.\n\nSelect a different encoding value and try again.")
		return
	if withHeader==True:
		index=1 #skip header
		for index, row in dt.iterrows():
			print("Processing record " + str(index)+"/"+str(count_row)+ " in csv file; location: " + str(row[locationColumnNumber])+ "\n")
			if str(row[locationColumnNumber])!='' and str(row[locationColumnNumber])!='nan':
				locList.append(row[locationColumnNumber])
	if len(locList)==0:
		mb.showwarning(title='Locations', message="There are no locations in your input file\n\n" + inputFilename + "\n\nThere is no geocoding to be done.\n\nNo map via Google Earth Pro can be done.")
		return
	else:
		# IO_user_interface_util.timed_alert(window, 2000, 'csv file locations extraction', "Finished extracting locations from csv file at", True)
		print("Finished extracting locations from csv file")
	return sorted(locList)

