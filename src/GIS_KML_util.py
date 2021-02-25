import sys

import GUI_IO_util
import IO_files_util
import GUI_util
import IO_libraries_util
import IO_user_interface_util
import dateutil

if IO_libraries_util.install_all_packages(GUI_util.window, "GIS_KML_util",
								['os', 'tkinter', 'csv', 'simplekml', 'datetime']) == False:
	sys.exit(0)

import os
import tkinter.messagebox as mb
import simplekml  # pip install simplekml
import csv
from datetime import datetime

import GIS_location_util
import GIS_Google_pin_util
import IO_csv_util


# generates .kml file based on CSV of geocoded locations with row format filename,loc type,name,lat,lng
# headers row(s) are NOT expected
# will colorize pins of different files differently, supports up to 300 unique colors (hex values)
# Red – ff0000ff.
# Yellow – ff00ffff.
# Blue – ffff0000.
# Green – ff00ff00.
# Purple – ff800080.
# Orange – ff0080ff.
# Brown – ff336699.
# Pink – ffff00ff.


def generate_kml(window, inputFilename, inputGeocodedCsvFile,
				 datePresent,
				 locationColumnNumber,
				 encodingValue,
				 group_number_var, italic_var, bold_var, italic_var_list, bold_var_list,
				 location_var,
				 group_var, group_values_entry_var_list, group_label_entry_var_list,
				 icon_var_list, specific_icon_var_list,
				 name_var_list, scale_var_list, color_var_list, color_style_var_list,
				 description_var_list, description_csv_field_var_list, colorize=True):
	IO_user_interface_util.timed_alert(window, 3000, 'GIS kml generator', 'Started generating KML file at', True,
						'You can follow the klm generator in command line.')

	colorList = ['93730E', '503DD3', '3C2D66', '3B817B', 'ED6651', '1F4825', '786A53', 'E90167', '7A2FCA', 'AA711C',
				 '22C7BE', 'D263DC', '7C67DC', 'E57143', 'BFE20F', 'F31BBD', '98F0BD', 'D393A7', '09C7A1', 'B50971',
				 '865A20', '7C97C5', '4A8EE2', '5EB165', '21B3B2', '549AEB', 'B674E4', 'A2F21D', '46C073', '6A51E0',
				 '434DE3', '9AA1F8', '69A5BC', '30201A', '374893', '8D7DB6', '140B6F', '3C9E24', 'A65D66', '79EC27',
				 'FB5680', 'C95D5C', 'D9967B', 'B220F9', '763525', 'D20399', '352928', '501E69', 'A1BD2B', '6929F5',
				 'EC7F00', '836BD9', '33941F', 'EC1993', '5FD79C', 'C79469', '5EDB9B', '5DEE20', 'E0C0A6', '4F517E',
				 'E4678D', '1DCF96', 'AE38D5', '8B65B0', 'BF0117', '0FB674', '49208C', '62A9B7', 'F4359F', '65F660',
				 'E60AD8', 'E11129', 'D8C728', 'F2C386', '3EB252', '3394D6', 'CB8DCA', '7A2425', 'C1785F', 'E8DAB2',
				 'CF6533', 'C0F4DC', 'E56198', '76AEEF', 'ED8B83', 'E434A7', '8677A5', '39A9B4', '12AB19', 'BF73BF',
				 '794BEE', '2649EF', 'E189B4', 'DD6887', '246981', '9FBDAA', 'CC106F', 'F418DC', 'CB9342', 'B6620E',
				 '49EF79', 'A36B4C', 'B40CCE', '99A2DE', '484BA5', 'AEF8E6', '28A84F', '4F35B0', '34AE77', 'CCF18A',
				 '6285B7', 'CDF763', '6A3A0F', 'B4362B', 'DE7D0F', '8620CD', '78B701', 'B6CE1C', 'DD1133', 'D124E2',
				 '469676', '4FE07E', '125E17', 'AF4C18', 'FE9228', '57FEE7', '43733E', '241823', 'FD2493', 'C916B4',
				 'E0BEFA', '53DC70', 'B95C28', 'F2526F', '5387A4', 'B94774', '2C7F9F', '04950B', 'D0D324', '388B02',
				 '0CB543', '960169', '06D9CE', '49F2D2', '60BFCB', '1C7D1B', '0B20C8', 'ACF86B', '6B56D2', '84233F',
				 'E4B62D', '228435', 'DD1C58', '8C3D20', 'FB42E7', '2DCD4E', 'B614B5', '982B58', '3D56A8', '7A3BD2',
				 '3F00D4', 'F8B1D6', '67E923', '1607DB', 'F45202', '54154E', 'A47555', 'BBCA4F', 'D65ED2', '9C6EF7',
				 '14B39F', '133998', 'E44AE9', 'ACFFAC', '249938', '04CB76', 'B9AE33', '718CC6', '56246D', '181A14',
				 '3280D0', '68A17D', '5FEDBB', '402658', '361513', '945242', '2BBDC3', 'A228FE', '44E6A4', 'FEA04C',
				 '3D0805', 'B3070D', 'AAFD3F', 'B73AEE', 'EDD9E1', '51F5AF', 'A62BE2', '88C85F', '817CB5', 'B93921',
				 'A73ADE', '985C43', 'ECBB51', 'BE32BE', '868CFA', 'DA2140', 'FE94AD', '89A340', '5FE929', '7B0F70',
				 'A5AD6F', 'E6D7B8', '431E75', 'ED5D68', '7E37DA', '780166', '14DEB9', '70C8F4', 'DD13B7', 'B25E93',
				 '91C932', '047D32', '6A3322', '70084B', '0FD6E7', 'A7861C', '9100F3', '26E591', '811895', '3A5113',
				 '9BB22C', 'EBEEBD', '2E304C', '1CD347', '982F93', '33FE51', 'B3C927', '65696A', '6764BB', 'C53E4D',
				 '280165', '319FBC', '711DB7', '72FE6B', '920C15', '94DA64', 'F96981', '5F37DE', 'E40D27', '8CA99B',
				 'F20CC6', '1CF867', '9C7D34', 'C19DFC', '478E11', 'A04AD1', '0EE064', '800FD4', '495E64', 'ABC39D',
				 '44D9FB', 'BF9900', 'E80E8E', '3D88BE', 'D5A984', '7D8477', 'F279B7', 'A90A88', '9B5140', '016AAF',
				 'E2D764', 'E66602', 'DACE54', '6E0CF4', 'D063A1', '39300A', '4E1B51', 'D2C911', 'E70F40', '310A5A',
				 'B83E94', '8D3A98', 'B6B80C', 'AE3AD8', 'A1AABF', '578961', 'DFF099', '95F4D0', '07F42C', 'CCE67A',
				 '6C2F68', '037041', '9D6914', '92B86E', '53A4A2', 'F0E1F4', '90811C', '2AA84C', 'CEE875', '6C8112']

	result = IO_files_util.openCSVFile(inputGeocodedCsvFile, 'r', encodingValue)
	if result == '':
		return ''

	kmloutputFilename = inputGeocodedCsvFile.replace('.csv', '.kml')

	inputfile = csv.reader(result)
	kml = simplekml.Kml()
	colorIndex = 0
	prev_filename = 'EMPTY'
	first_row = next(inputfile)  # skip header
	index = 0

	# index_list = GIS_location_util.extract_index(inputFilename, inputGeocodedCsvFile, encodingValue, location_var)
	index_list = GIS_location_util.extract_index(inputFilename, inputGeocodedCsvFile, encodingValue, location_var)

	if group_number_var <= 1:
		numberOfRecords = IO_csv_util.GetNumberOfRecordInCSVFile(inputGeocodedCsvFile, encodingValue)
		print("Processing geocoded record for kml:", '1' + "/" + str(numberOfRecords) + ' header record skipped')
		for row in inputfile:
			index = index + 1
			currRecord = str(index + 1) + "/" + str(numberOfRecords)
			print("Processing geocoded record for kml:", currRecord)
			# if inputIsCoNLL==True:
			curr_filename = row[0]
			GGPdateFormat = ''
			# if inputIsCoNLL==True:
			if datePresent == True:
				date = row[4]
				if date != 'nan' and date != '':
					# if dates are present they MUST be converted to Google Earth Pro expected date format yyyy-mm-dd
					# get format of your date
					# https://stackoverflow.com/questions/44298131/detecting-date-format-and-converting-them-to-mm-dd-yyyy-using-Python
					# date options https://i.pinimg.com/736x/25/f7/0d/25f70de25821648c2f268b3d52da6eb8.jpg

					# https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
					# %b : Returns the first three characters of the month name. ...
					# %B : Returns the full name of the month, e.g. September
					# %m : Returns month in 2 digit form 1 to 12
					# %d : Returns day of the month, from 1 to 31
					# %Y : Returns the year in four-digit format
					# %y : Returns the year in two-digit format 18 for 1918

					# a combinations of formats are admitted, with:
					#    year (2 or 4 digits), month, day in numeric format and in various order
					#    with month in 3 or full alphabetic format
					fmts = ('%Y', '%y', '%Y-%m-%d', '%y-%m-%d', '%Y-%m', '%y-%m',
							'%Y-%B-%d', '%y-%B-%d', '%Y-%b-%d', '%y-%b-%d', '%Y-%B', '%y-%B', '%Y-%b', '%y-%b'
																									   '%m-%d-%Y',
							'%m-%d-%y', '%d-%m-%Y', '%d-%m-%y', '%m-%Y', '%m-%y',
							'%B-%d-%Y', '%B-%d-%y', '%b-%d-%Y', '%b-%d-%y', '%d-%B-%Y', '%d-%B-%y',
							'%d-%b-%Y', '%d-%b-%y', '%m-%Y', '%m-%y', '%B-%Y', '%B-%y', '%b-%Y', '%b-%y')

					for e in date.splitlines():
						for fmt in fmts:
							try:
								t = datetime.strptime(e, fmt)
								break
							except ValueError as err:
								pass
					currentDateFormat = dateutil.parser.parse(date)
					# years before 1900 cannot be used
					# pre 1900 dates may give a problem in Windows: ValueError: format %y requires year >= 1900 on Windows
					# https://stackoverflow.com/questions/10263956/use-datetime-strftime-on-years-before-1900-require-year-1900
					# There are various ways to alter strftime so that it handles pre-1900 dates
					try:
						GGPdateFormat = currentDateFormat.strftime('%Y-%m-%d')
					except:
						mb.showerror(title='Date error',
									 message="There was an error in processing the date '" + date + "'.\n\nThe date format '" + fmt + "' was automatically applied to process the date, where format values are as follows:\n%B or %b   alphabetic month name in full or first 3 characters;\n%m   2-digit month (1 to 12);\n%d   2-digit day of the month (1 to 31);\n%Y   4-digit and %y 2-digit year (1918, 18).\n\nBut... either\n1.   the format automatically applied is incorrect for the date;\n2.   the date is in unrecognized format (e.g., it contains time besides date);\n3.   the date is prior to 1900. The library 'strftime' used here to deal with dates cannot process dates prior to 1900 in Windows.")
						return ''



			# Mapping with one group
			# we do not want to print the name of the location or the map becomes unreadable
			# pnt = kml.newpoint(name=row[0], coords=[(row[2],row[1])])  # wants to be read in in lng, lat order
			# print(currRecord,row[0]) #document name
			if row[2] != 0 and row[1] != 0:
				pnt = kml.newpoint(coords=[(row[2], row[1])])  # wants to be read in in lng, lat order
				pnt = GIS_Google_pin_util.pin_customizer(inputFilename, pnt, index, index_list, location_var, group_var,
														 group_values_entry_var_list, group_label_entry_var_list,
														 icon_var_list, specific_icon_var_list, name_var_list,
														 scale_var_list, color_var_list, color_style_var_list,
														 description_var_list, description_csv_field_var_list,
														 italic_var_list, bold_var_list, group_number_var, j=0)
				pnt.timespan.begin = GGPdateFormat
				pnt.timespan.end = GGPdateFormat

	# Mapping with multiple group
	else:
		for j in range(group_number_var):
			values_raw = []
			values_raw_temp = []
			values_row_num = []
			specified_values_raw = []
			specified_values_temp = []
			specified_values = []

			withHeader_var = IO_csv_util.csvFile_has_header(inputFilename)  # check if the file has header
			data, headers = IO_csv_util.get_csv_data(inputFilename, withHeader_var)  # get the data and header
			# get the column name and its column num that we are splitting groups based on
			icon_csv_field_var_name = icon_csv_field_var

			for m in range(len(headers)):
				if icon_csv_field_var_name == headers[m]:
					icon_csv_field_var_name_num = m

			if len(group_values_entry_var_list[j]) == 0:
				for i in range(len(data)):
					values_raw_temp.append(data[i][icon_csv_field_var_name_num])

				values_raw = values_raw_temp

				for k in range(len(group_values_entry_var_list)):
					if len(group_values_entry_var_list[k]) != 0:
						specified_values_raw.append(GUI_util.group_values_entry_var_list[k])
						specified_values_temp = specified_values_raw[0].split(",")

						for u in range(len(specified_values_temp)):
							specified_values_temp[u] = specified_values_temp[u].strip()

						for w in range(len(specified_values_temp)):
							specified_values.append(specified_values_temp[w])
							specified_values_raw.clear()

				duplicates = []
				for s in range(len(values_raw_temp)):
					for r in range(len(specified_values)):
						if values_raw_temp[s] == specified_values[r]:
							duplicates.append(values_raw_temp[s])

				for t in range(len(duplicates)):
					values_raw.remove(duplicates[t])

				values = values_raw
				new_value = ', '.join(values)
				group_values_entry_var_list[j] = new_value

			else:
				values_raw.append(group_values_entry_var_list[j])
				values = values_raw[0].split(",")
				for u in range(len(values)):
					values[u] = values[u].strip()
				new_value = ', '.join(values)
				group_values_entry_var_list[j] = new_value

			for n in range(len(data)):
				for a in range(len(values)):
					if values[a] == data[n][icon_csv_field_var_name_num]:
						values_row_num.append(n)

			index = 0
			inputfile = csv.reader(open(inputGeocodedCsvFile, 'r', encoding=encodingValue, errors='ignore'))
			for row in inputfile:
				for b in range(len(values_row_num)):
					if index - 1 == values_row_num[b]:
						currRecord = str(index - 1) + "/" + str(
							IO_csv_util.GetNumberOfRecordInCSVFile(inputGeocodedCsvFile, encodingValue))
						# we do not want to print the name of the location or the map becomes unreadable
						# pnt = kml.newpoint(name=row[0], coords=[(row[2],row[1])])  # wants to be read in in lng, lat order
						# print(currRecord,row[0]) #document name
						pnt = kml.newpoint(coords=[(row[locationColumnNumber + 2], row[
							locationColumnNumber + 1])])  # wants to be read in in lng, lat order
						pnt = GIS_Google_pin_util.pin_customizer(inputFilename, pnt, index, index_list, location_var,
																 group_var, group_values_entry_var_list,
																 group_label_entry_var_list, icon_var_list,
																 specific_icon_var_list, name_var_list, scale_var_list,
																 color_var_list, color_style_var_list,
																 description_var_list, description_csv_field_var_list,
																 italic_var_list, bold_var_list, group_number_var, j=0)
				index = index + 1
	IO_user_interface_util.timed_alert(window, 3000, 'GIS kml generator', 'Finished generating KML file at', True)
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
