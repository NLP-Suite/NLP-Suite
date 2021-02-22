# Written by Roberto Franzosi Fall 2020

import sys
import GUI_util
import IO_libraries_util

# if not IO_libraries_util.install_all_packages(GUI_util.window,"DB_SQL",['io','os','tkinter','subprocess','re','datetime','shutil','ntpath']):
#     sys.exit(0)

import os
from sys import platform
import tkinter.messagebox as mb
import tkinter as tk
from tkinter import filedialog
# import nltk
import webbrowser
import re
import datetime
import subprocess
from subprocess import call
import shutil
import ntpath  # to split the path from filename
from pathlib import Path

import reminders_util
import IO_CoNLL_util
import IO_user_interface_util

# There are 3 methods and a 2 constants present:
# abspath returns absolute path of a path
# join join to path strings
# dirname returns the directory of a file
# __file__ refers to the script's file name
# pardir returns the representation of a parent directory in the OS (usually ..)
from IO_user_interface_util import timed_alert

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# insert the src dir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


# check if a directory exists, remove if it does, and create
def make_directory(newDirectory):
	createDir = True
	# Got permission denied error if the folder is read-only.
	# Updates permission automatically
	if os.path.exists(newDirectory):
		shutil.rmtree(newDirectory)
	try:
		os.chmod(Path(newDirectory).parent.absolute(), 0o777)
		os.mkdir(newDirectory, 0o777)
	except Exception as e:
		print("error: ", e.__doc__)
		createDir = False
	return createDir


# for folder, subs, files in os.walk(inputDir):
# 	folderID += 1
# 	print("\nProcessing folder " + str(folderID) + "/ " + os.path.basename(
# 		os.path.normpath(folder)))
# 	for filename in files:
# https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
def getFileList_SubDir(inputFilename, inputDir, fileType='.*', silent=False):
	files = []
	if inputDir!='':
		for path in Path(inputDir).rglob('*' + fileType):
			files.append(str(path))
	else:
		if inputFilename.endswith(fileType):
			files = [inputFilename]
		else:
			if not silent:
				mb.showwarning(title='Input file error',
							   message='The input file type expected by the algorithm is ' + fileType + '.\n\nPlease, select the expected file type and try again.')
	# folder, subs, files = os.walk(inputDir)
	# filter files for the desired extension
	# if fileType!='.*':
	# 	files = [ fi for fi in files if not fi.endswith(fileType) ]
	# if dirName!='':
	# 	for path in Path(dirNameinputDir.rglob('*' + fileType)):
	# 		files.append(str(path))
	# else:
	# 	if inputFilename.endswith(fileType):
	# 		files = [inputFilename]
	# 	else:
	# 		if not silent:
	# 			mb.showwarning(title='Input file error',
	# 						   message='The input file type expected by the algorithm is ' + fileType + '.\n\nPlease, select the expected file type and try again.')
	# return folder, subs, files
	return files


# inputFile contains a file name with full path;
#   can also be blank 
# inputDir is the full path of an input directory
#   can also be blank 
# fileType can be * (for any fileType), .pdf, .csv, .txt, ...
# returns a list of either a single file or all files in a directory
#   examples of calls
# https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/

def getFileList(inputFile, inputDir, fileType='.*',silent=False):
	files = []
	if inputDir != '':
		for path in Path(inputDir).glob('*' + fileType):
			files.append(str(path))
		if len(files) == 0:
			mb.showwarning(title='Input files error',
						   message='No files of type ' + fileType + ' found in the directory ' + inputDir)
	else:
		if inputFile.endswith(fileType):
			files = [inputFile]
		else:
			mb.showwarning(title='Input file error',
						   message='The input file type expected by the algorithm is ' + fileType + '.\n\nPlease, select the expected file type and try again.')
	return files


# changeVar is the name of the IO that needs to be displayed (e.g., filename)
# changeVar1 is the name of the IO button that needs to be disabled in the case of mutuallyexclusive options
def selectFile(window, IsInputFile, checkCoNLL, changeVar, changeVar1, title, fileType, extension, outputFileVar=None,
			   initialFolder=''):
	filePath = ""
	if initialFolder == '':
		initialFolder = os.path.dirname(os.path.abspath(__file__))
	if IsInputFile == True:  # as opposed to output file
		# when the file string is blank, the directory option should always also be available
		filePath = tk.filedialog.askopenfilename(initialdir=initialFolder, title=title, filetypes=fileType)
		from os.path import splitext
		file_name, extension = splitext(filePath)
	else:
		if outputFileVar != None:
			outputFilename = outputFileVar
			filePath = tk.filedialog.asksaveasfile(initialdir=initialFolder, initialfile=outputFilename.get(),
												   title=title, filetypes=fileType)
		else:
			print('Error in output file name creation')
	# when the file string is blank, the directory option should always also be available
	if filePath is None:
		filePath = ""
	filePath = str(filePath)
	if len(filePath) < 3:
		filePath = ""
	if (checkCoNLL == True) and (IsInputFile == 1) and (extension == ".csv") and (len(filePath) > 3):
		if IO_CoNLL_util.check_CoNLL(filePath, True) == False:
			filePath = ""
	changeVar.set(filePath)

	return filePath


def selectDirectory(window, changeVar, changeVar1, title, initialFolder=''):
	if initialFolder == '':
		initialFolder = os.path.dirname(os.path.abspath(__file__))
	path = tk.filedialog.askdirectory(initialdir=initialFolder, title=title)
	# when the directory string is blank, the file option should always also be available
	if len(path) < 3:
		path = ""
	try:  # if the button is not present this would throw an error
		changeVar1.config(state="normal")
	except:
		pass
	changeVar.set(path)
	return path


def openExplorer(window, directory):
	if sys.platform == 'win32':  # Windows
		os.startfile(directory)
	elif sys.platform == 'darwin':  # Mac
		subprocess.Popen(['open', directory])
	else:
		try:
			subprocess.Popen(['xdg-open', directory])  # Linux
		except OSError:
			print("OS error in accessing directory")


# returns date, dateStr
def getDateFromFileName(file_name, sep='_', date_field_position=2, date_format='mm-dd-yyyy', errMsg=True):
	# configFile_basename is the filename w/o the full path
	file_name = ntpath.basename(file_name)
	x = file_name
	# must assign or you get an error in return
	date = ''
	dateStr = ''
	if 1:
		startSearch = 0
		iteration = 0
		while iteration < date_field_position - 1:
			startSearch = x.find(sep, startSearch + 1)
			iteration += 1
		# the altSeparator="."
		altSeparator = "."
		end = x.find(sep, startSearch + 1)
		if end == -1:
			end = x.find(altSeparator, startSearch + 1)
		if date_field_position == 1:
			raw_date = x[startSearch:end]
		else:
			raw_date = x[startSearch + 1:end]
		# https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
		# the strptime command (strptime(date_string, format) takes date_string and formats it according to format where format has the following values:
		# %m 09 %-m 9 (does not work on all platforms); %d 07 %-d 7 (does not work on all platforms);
		# loop through INPUT date formats and change format to Python style
		# print('DATEFORMAT',date_format)
		try:
			dateStr = ''
			if date_format == 'mm-dd-yyyy':
				date = datetime.datetime.strptime(raw_date, '%m-%d-%Y').date()
				dateStr = date.strftime('%m-%d-%Y')
			elif date_format == 'dd-mm-yyyy':
				date = datetime.datetime.strptime(raw_date, '%d-%m-%Y').date()
				dateStr = date.strftime('%d-%m-%Y')
			elif date_format == 'yyyy-mm-dd':
				date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
				dateStr = date.strftime('%Y-%m-%d')
			elif date_format == 'yyyy-dd-mm':
				date = datetime.datetime.strptime(raw_date, '%Y-%d-%m').date()
				dateStr = date.strftime('%Y-%d-%m')
			elif date_format == 'yyyy-mm':
				date = datetime.datetime.strptime(raw_date, '%Y-%m').date()
				dateStr = date.strftime('%Y-%m')
			elif date_format == 'yyyy':
				date = datetime.datetime.strptime(raw_date, '%Y').date()
				dateStr = date.strftime('%Y')
			dateStr = dateStr.replace('/', '-')
		except ValueError:
			if errMsg == True:
				# mb.showwarning(title='Date format error in filename', message='You have selected the option that your input filename ('+file_name+') embeds a date.\n\nBut... you may have provided\n\n   1. the wrong date format (' + date_format + ')\n   2. the wrong date in the input filename (' + raw_date + ')\n   3. the wrong date position in the filename ('+str(date_field_position)+')\n   4. the wrong date character separator in the filename ('+sep+').\n\nPlease, check your filename and/or the date options in the GUI.\n\nThe date will be set to blank in the output CoNLL table.')
				# print('\nDate format error in filename. You have selected the option that your input filename ('+file_name+') embeds a date.\n\nBut... you may have provided\n\n   1. the wrong date format (' + date_format + ')\n   2. the wrong date in the input filename (' + raw_date + ')\n   3. the wrong date position in the filename ('+str(date_field_position)+')\n   4. the wrong date character separator in the filename ('+sep+').\n\nPlease, check your filename and/or the date options in the GUI.\n\nThe date will be set to blank in the output CoNLL table.\n')
				print(
					'\nDate format error in filename: ' + file_name + '\n   Date found: ' + raw_date + '; Expected date format: ' + date_format + '; Expected date position: ' + str(
						date_field_position) + '; Character separator ' + sep)
				date = ''  # must assign or you get an error in return
				dateStr = ''
	# TODO: see the modification, so we can get a date object and a string from the same method, DO keep this change for the file_classifier to work.
	return date, dateStr


def checkDirectory(path, message=True):
	if os.path.isdir(path):
		return True
	else:
		if message:
			mb.showwarning(title='Directory error',
						   message='The directory ' + path + ' does not exist. It may have been renamed, deleted, moved. Please, check the DIRECTORY and try again')
		return False


# check to make sure the file exists, and optionally that the desired extension matches the file's
# also gives user the option to generate a message box warning of why
def checkFile(filePath, extension=None, silent=False):
	if 'reminders.csv' in filePath:
		head, tail = os.path.split(filePath)
		reminders_util.generate_reminder_list(head)
	if not os.path.isfile(filePath):
		if not silent:
			print("The file " + filePath + " could not be found.")
			mb.showwarning(title='Input file not found',
						   message='Error in input filename and path.\n\nThe file ' + filePath + ' could not be found.\n\nPlease, check the INPUT FILE PATH and try again.')
		return False
	if extension != None and not '.' + filePath.rsplit('.', 1)[1] == extension:
		if not silent:
			print('File has the wrong extension.')
			mb.showwarning(title='Input file extension error',
						   message='Error in input filename and path.\n\nThe file ' + filePath + ' does not have the expected extension ' + extension + '\n\nPlease, check the INPUT FILE and try again.')
		return False
	else:
		return True


# filePath contains filename with path
def open_kmlFile(window,filePath):
	if sys.platform == 'win32':
		# https://stackoverflow.com/questions/26498302/how-to-load-the-kml-file-into-google-earth-using-python
		os.startfile(filePath)
		# also webbrowser.open(filePath) will open the kml file in GEP
	elif sys.platform == 'darwin':
		subprocess.Popen(['open', filePath])
	else:
		try:
			subprocess.Popen(['xdg-open', filePath])
		except OSError:
			print("OS error in opening file " + filePath)


# opens a filename with its path
# if a file with the same name is already open, it throws an error 
def openFile(window, filePath):
	if len(filePath) == 0:
		tk.messagebox.showinfo("Input file error", "The filename is blank. No file can be opened.")
		return
	if os.path.isfile(filePath):
		# windows
		if platform in ['win32', 'cygwin']:
			try:
				os.system('start "" "' + filePath + '"')
			except IOError:
				mb.showwarning(title='Input file error',
							   message="Could not open the file " + filePath + "\n\nA file with the same name is already open. Please, close the Excel file and try again!")
				return True
		# macOS and other unix
		else:
			try:
				call(['open', filePath])
			except IOError:
				mb.showwarning(title='Input file error',
							   message="Could not open the file " + filePath + "\n\nA file with the same name is already open. Please, close the Excel file and try again!")
				return True
	else:
		tk.messagebox.showinfo("Error", "The file " + filePath + " could not be found.")
		print("The file " + filePath + " could not be found.")


# open a set of output files (csv, txt,...) stored as a list in filesToOpen
def OpenOutputFiles(window, openOutputFiles, filesToOpen):
	if filesToOpen == None:
		return
	if len(filesToOpen) == 0:
		return
	if len(filesToOpen) == 1:
		singularPlural = 'file'
	else:
		singularPlural = 'files'
	if openOutputFiles == True:  # now the approach is to open all files at the end, so this extra check is redundant "and runningAll==False:""
		# should display a reminder about csv files with weird characters most likely dues to non utf-8 apostrophes and quotes
		#   but... this reminder does not have a specific config, so... perhaps *?
		reminders_util.checkReminder('*',
									 ['csv files'],
									 'If csv ouput files open displaying weird characters in a Windows OS (e.g., a€), most likely the cause is due to non utf-8 compliant input text. Apostrophes and quotes are the typical culprits, but also other punctuation characters.\n\nPlease, run the tool to check documents for utf-8 compliance and, if necessary, run the tool for automatic apostrophe and quote conversion from non utf-8 to utf-8.\n\nTo learm more on utf-8 compliance, read the TIPS on utf-8 compliance.',
									 True)
		routine_options = reminders_util.getReminder_list('*')
		timed_alert(window, 2000, 'Warning',
					'Opening ' + str(len(filesToOpen)) + ' output ' + singularPlural + '... Please wait...', False)
		for file in filesToOpen:
			if os.path.isfile(file):
				if file.endswith('.kml'):
					open_kmlFile(window, file)
				else:
					openFile(window, file)
			# once printed empty array
		# if len(filesToOpen)>0:
		#     filesToOpen.clear()


def getFileExtension(inputfilePath):
	path, inputfile = ntpath.split(inputfilePath)  # remove/take out path
	inputfile, extension = os.path.splitext(inputfile)  # remove/take out the extension
	return extension


def getFilename(inputfilePath):
	path, inputfile = ntpath.split(inputfilePath)  # remove/take out path
	inputfile, extension = os.path.splitext(inputfile)  # remove/take out the extension
	return inputfile


# inputfilePath is the input filename with path
# returns outFilename with path
# label1 (SCNLP, QC, NVA,...)
#  in label1 the following labels are passed by the calling script: SCNLP (Stanford CoreNLP), QC (query conll), NVA (noun verb analysis), FW (function words), TC (tpic modeling), SA (sentiment analysis), CA (concretenss analysis)
# label2 (sub-field, e.g., pigs_Lemma, or hedonometer)
# label3,label4,label5 are available options
def generate_output_file_name(inputfilePath, inputDir, outputDir, outputExtension, label1='', label2='', label3='', label4='',
							  label5='', useTime=True, disable_suffix=False):
	useTime = False  # files become too long with the addition of datetime
	if inputDir!='':
		Dir = os.path.basename(os.path.normpath(inputDir))
		inputfile='Dir_' + Dir
	else:
		inputfile = getFilename(inputfilePath)
	default_outputFilename_str =''
	# do not add the NLP_ prefix if processing a file previously processed and with the prefix already added
	if "NLP_" not in inputfile:
		if label1=='':
			default_outputFilename_str = 'NLP_' + inputfile  # adding to front of file name
		else:
			default_outputFilename_str = 'NLP_' + str(label1) + "_" + inputfile  # adding to front of file name
	else:
		default_outputFilename_str=inputfile
	if len(str(label2)) > 0:
		default_outputFilename_str = default_outputFilename_str + "_" + str(label2)
	if len(str(label3)) > 0:
		default_outputFilename_str = default_outputFilename_str + "_" + str(label3)
	if len(str(label4)) > 0:
		default_outputFilename_str = default_outputFilename_str + "_" + str(label4)
	if len(str(label5)) > 0:
		default_outputFilename_str = default_outputFilename_str + "_" + str(label5)
	if useTime == True:
		default_outputFilename_str = default_outputFilename_str + '_' + re.sub(" ", "_", re.sub(':', '',
																								re.sub('-', '_', str(
																									datetime.datetime.now())))[
																						 :-7])
	default_outputFilename_str = default_outputFilename_str + outputExtension
	# checking if file with that name exists, if so adding _ and integer to end
	if disable_suffix == False:
		if os.path.isfile(default_outputFilename_str):
			for i in range(1,
						   1000):  # can't (and shouldn't) have more than 999 of the same title or last will overwrite
				default_outputFilename_str = default_outputFilename_str.split('.cs')[0]
				default_outputFilename_str = default_outputFilename_str + '_' + str(i)
				if os.path.isfile(default_outputFilename_str + outputExtension):
					# clearing that end integer so it can increment
					default_outputFilename_str = default_outputFilename_str.split('_' + str(i))[0]
					continue
				else:
					default_outputFilename_str = default_outputFilename_str + outputExtension
					break  # file name found, end loop
	outFilename = os.path.normpath(os.path.join(outputDir, default_outputFilename_str))
	return outFilename


# extension can be 'txt', 'xlsx', 'doc, 'docx' WITHOUT .
def GetNumberOfDocumentsInDirectory(inputDirectory, extension=''):
	if extension == '':  # count any document
		numberOfDocs = len([os.path.join(inputDirectory, f) for f in os.listdir(inputDirectory)])
	else:  # count documents by specific document type
		extensionLength = len(extension)
		numberOfDocs = len([os.path.join(inputDirectory, f) for f in os.listdir(inputDirectory) if
							f[:2] != '~$' and f[-(extensionLength + 1):] == '.' + extension])
	return numberOfDocs


# inputfile: input file path
# open_type: "r" for read, "w" for write
# return csvfile if opened up properly, or empty string if error occurs
def openCSVFile(inputfile, open_type, encoding_type='utf-8'):
	try:
		csvfile = open(inputfile, open_type, newline='', encoding=encoding_type, errors='ignore')
		return csvfile
	except IOError:
		mb.showwarning(title='File error',
					   message="Could not open the file " + inputfile + "\n\nA file with the same name is already open.\n\nPlease, close the Excel file and try again!")
		return ""


def getScript(pydict,script):
	# global script_to_run, IO_values
	IO_values = 0
	script_to_run = ''

	if script == '':
		return script_to_run, IO_values

	# There are FOUR values in the pydict dictionary:
	#	1. KEY the label displayed in any of the menus (the key to be used)
	#	val[0] the name of the python script (to be passed to NLP.py) LEAVE BLANK IF OPTION NOT AVAILABLE
	#	val[1] 0 False 1 True whether the script has a GUI that will check IO items or we need to check IO items here
	#	val[2] 1, 2, 3 (when the script has no GUI, i.e., val[1]=0)
	#		1 requires input file
	#		2 requires input Dir
	#		3 requires either Dir or file
	#	val[3] input file extension txt, csv, pdf, docx

	try:
		val = pydict[script]
	except:
		# entry not in dic; programming error; must be added!
		mb.showwarning(title='Warning',
					   message="The selected option '" + script + "' was not found in the Python dictionary in NLP_GUI.py.\n\nPlease, inform the NLP Suite developers of the problem.\n\nSorry!")
		return script_to_run, IO_values
	# name of the python script
	if val[0] == '':
		mb.showwarning(title='Warning', message="The selected option '" + script + "' is not available yet.\n\nSorry!")
		return script_to_run, IO_values
	# check that Python script exists
	scriptName = val[0]
	# this is the case when there is no GUI and we call a function in a script
	#	e.g., statistics_txt_util.compute_corpus_statistics

	# all jar cases are handled separately in NLP.py
	if scriptName.endswith('.jar'):
		scriptName = scriptName  # do not split jar filenames
	# deal with scripts without a GUI such as
	#	statistics_txt_util.compute_corpus_statistics
	#	where the first part of the item constitutes the script name
	#	and the second part the specific function in the script
	if (not (scriptName.endswith('.py'))) and (not (scriptName.endswith('.jar'))):
		# val[2] IO value 1, 2, 3; whether it requires a filename, a dir, or either
		# val[3] file extension (e.g., csv)
		scriptName = val[0].split(".", 1)[0]
		# add .py to scriptName so as to check whether the file exists in the NLP directory
		scriptName = scriptName + ".py"
		# passed to NLP.py
		# val[2] IO value 1, 2, 3; whether it requires a filename, a dir, or either
		IO_values = val[2]
	# check the IO requirements of the function;
	#	all py cases have their own GUI where IO requirements are checked
	# if val[1]==0: #NO GUI; must check IO requirements here
	# 	if checkIO_Filename_InputDir (scriptName,val[2], val[3])==False:
	# RF return
	# IO_values is 0 when an internet program is used; do not check software in the software dir
	if IO_values != 0:
		if IO_libraries_util.inputProgramFileCheck(scriptName) == False:
			return script_to_run, IO_values
	# passed to NLP.py
	script_to_run = val[0]

	return script_to_run, IO_values

def run_jar_script(scriptName, inputFilename, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts):
	filesToOpen = []
	if IO_libraries_util.inputProgramFileCheck(scriptName) == False:
		return
	# if scriptName=='Sentence_Complexity.jar':
	#     outputFilename=IO_util.generate_output_file_name(inputFilename,output_dir_path,'.csv','SCo','','')
	#     filesToOpen.append(outputFilename)
	#     temp_outputFilename=ntpath.basename(outputFilename)
	#     IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running Sentence Complexity at',True,'\n\nYou can follow Sentence Complexity in command line.')
	#     subprocess.call(['java', '-jar', 'Sentence_Complexity.Jar', inputFilename, output_dir_path, temp_outputFilename])
	#     IO_util.timed_alert(GUI_util.window,2000,'Analysis end','Finished running Sentence Complexity at',True)
	#     if createExcelCharts:
	#         columns_to_be_plotted = [[1,3], [1,4], [1,6], [1,7]]
	#         hover_label=['Sentence','Sentence','Sentence','Sentence']
	#         outputFilenameXLSM_1 = Excel_util.run_all(columns_to_be_plotted,inputFilename,output_dir_path, outputFilename, chart_type_list = ["line"], chart_title= "Sentence complexity", column_xAxis_label_var = 'Sentence ID',column_yAxis_label_var = 'Complexity',outputExtension = '.xlsm',label1='Scomp',label2='line',label3='chart',label4='',label5='', useTime=False,disable_suffix=True,  count_var=0, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[''], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)
	#         if outputFilenameXLSM_1 != "":
	#             filesToOpen.append(outputFilenameXLSM_1)

	# elif scriptName=='DependenSee.jar':
	#     #inputFilename must include the file full path with txt extension
	#     #inputFilename must be a txt file
	#     IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running Sentence visualization: Dependency tree viewer (png graphs) at',True,'\n\nYou can follow Sentence Complexity in command line.')
	#     subprocess.call(['java', '-jar', 'DependenSee.Jar', inputFilename, output_dir_path])
	#     IO_util.timed_alert(GUI_util.window,2000,'Analysis end','Finished running Sentence visualization: Dependency tree viewer (png graphs) at',True,'\n\nMake sure to open the png files in output, one graph for each sentence.')
	if visualization_tools == "Sentence visualization: Dynamic sentence network viewer (Gephi graphs)":
		# TODO the script does not work even in command line using the arguments in the ReadMe file; it seems to want two more parameters
		"""
		Error in input parameters
		Usage Example:
		args1 = "inputFilePath"
		args2 = "outputFilePath.gexf"
		args3 = true or false
		args4 = $$$
		# if checkIO_Filename_InputDir ("Sentence Visualization: Dynamic Sentence Network Viewer (Gephi graphs)",inputFilename, input_main_dir_path, output_dir_path):
		#     subprocess.call(['java', '-jar', 'DynamicSentenceViewer.jar', inputFilename, output_dir_path])
		"""
		return
	if openOutputFiles == True:
		IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


# The NLP script and sentence_analysis script use pydict dictionaries to run the script selected in a menu
# the dict can contain a python file, a jar file or a combination of python file + function
def runScript_fromMenu_option(script_to_run, IO_values, inputFilename, input_main_dir_path, output_dir_path,
							  openOutputFiles, createExcelCharts):
	if len(script_to_run) == 0:
		return
	if script_to_run == "Gender guesser":
		import IO_internet_util
		# check internet connection
		if not IO_internet_util.check_internet_availability_warning("Gender guesser"):
			return
		webbrowser.open('http://www.hackerfactor.com/GenderGuesser.php#About')
	elif script_to_run.endswith('.py'):  # with GUI
		if IO_libraries_util.inputProgramFileCheck(script_to_run) == False:
			return
		call("python " + script_to_run, shell=True)
	elif script_to_run.endswith('.jar'):  # with GUI
		run_jar_script(script_to_run, inputFilename, input_main_dir_path, output_dir_path, openOutputFiles,
					   createExcelCharts)
	else:  # with NO GUI; does not end with py
		if input_main_dir_path != '':
			IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
											   'Started running ' + script_to_run + ' at', True,
											   'You can follow ' + script_to_run + ' in command line.')
		else:
			IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
											   'Started running ' + script_to_run + ' at', True)
		script = script_to_run.split(".", 1)
		import importlib
		pythonFile = importlib.import_module(script[0])
		# script[0] contains the Python file name
		# script[1] contains the function name insime a specific Python file
		if IO_libraries_util.inputProgramFileCheck(script[0] + '.py') == False:
			return
		func = getattr(pythonFile, script[1])
		# correct values are checked in NLP_GUI
		if IO_values == 1:
			func(GUI_util.window, inputFilename, output_dir_path, openOutputFiles, createExcelCharts)
		elif IO_values == 2:
			func(GUI_util.window, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts)
		else:
			func(GUI_util.window, inputFilename, input_main_dir_path, output_dir_path,
				 openOutputFiles,createExcelCharts)

		IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
										   'Finished running ' + script_to_run + ' at', True)


"""
#does not work, despite StackOverFlow recommandation; always returns None
def detectCsvHeader (csvFile):
    with open(csvFile, 'r',encoding="utf8",errors='ignore') as csvf:
        has_header = csv.Sniffer().sniff(csvf.read(2048))
        csvf.seek(0)
        reader=csv.reader(csvf, has_header)
        print ("detectCsvHeader has_header ",has_header)
"""


# function written by Jian Chen for NVA but not used but very helpful to generalize for all scripts
# Gather any user provided arguments. If incorrect number to run from CL, return False
def gatherCLAs():
	parser = argparse.ArgumentParser(description='Process command line arguments for noun verb analysis')
	parser.add_argument('--inputFile', help='CoNLL file input')
	parser.add_argument('--outputDir', help='Directory to save output excel/csv files')
	parser.add_argument('--openFiles', help='<True/False> If true, will open all exported excel/csv files')
	args = parser.parse_args()

	# numArgsProvided = len(vars(args))
	# print(numArgsProvided)
	if len(sys.argv) != 3:
		return False
	else:
		if args.openFiles == 'True':
			openOut = True
		else:
			openOut = False
		return args.inputFile, args.outputDir, openOut
