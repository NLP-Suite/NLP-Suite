# Written by Roberto Franzosi Fall 2020
# Written by Roberto Franzosi Fall 2020
import csv
import sys

import numpy as np

import GUI_util
import IO_libraries_util

# if not IO_libraries_util.install_all_Python_packages(GUI_util.window,"DB_SQL",['io','os','tkinter','subprocess','re','datetime','shutil','ntpath']):
#     sys.exit(0)

import os
from sys import platform
import tkinter.messagebox as mb
import tkinter as tk
from tkinter import filedialog
import math
import webbrowser
import re
# import datetime
from datetime import datetime
import subprocess
from subprocess import call
import shutil
import ntpath  # to split the path from filename
from pathlib import Path

import reminders_util
import CoNLL_util
import IO_user_interface_util
import GUI_IO_util
import IO_csv_util

# There are 3 methods and a 2 constants present:
# abspath returns absolute path of a path
# join join path strings
# dirname returns the directory of a file
# __file__ refers to the script's file name
# pardir returns the representation of a parent directory in the OS (usually ..)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# insert the src dir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# check if a directory exists, remove if it does, and create
def make_directory(newDirectory,silent=True):
    createDir = True
    # newDirectory=''
    # Got permission denied error if the folder is read-only.
    # Updates permission automatically
    if os.path.exists(newDirectory):
        if not silent:
            result = mb.askyesno('Directory already exists',
                                        'There already exists a directory\n\n' + newDirectory + '\n\nThis directory will be replaced.\n\nAre you sure you want to continue?')
            if not result:
                # createDir = False
                # return createDir
                return newDirectory
        shutil.rmtree(newDirectory)
    try:
        os.chmod(Path(newDirectory).parent.absolute(), 0o755)
        os.mkdir(newDirectory, 0o755)
    except Exception as e:
        print("error: ", e.__doc__)
        # createDir = False
        newDirectory=''
    # return createDir
    return newDirectory

def make_output_subdirectory(inputFilename, inputDir, outputDir, label, silent=True):
    outputSubDir=''
    if inputFilename!='':
        # process file
        inputFileBase = os.path.basename(inputFilename)[0:-4]  # without .txt
        outputSubDir = os.path.join(outputDir, label + "_" + inputFileBase)  # + "_CoRefed_files")
    elif inputDir!='':
        # processing a directory
        inputDirBase = os.path.basename(inputDir)
        outputSubDir = os.path.join(outputDir, label + "_" + inputDirBase)
    elif label != '':
        outputSubDir = os.path.join(outputDir, label)
    else:
        outputSubDir = outputDir
    if os.path.exists(outputSubDir):
        if not silent:
            result = mb.askyesno('Directory already exists',
                                        'The algorithms will create a new directory\n\n' + outputSubDir + '\n\nA directory by the same name already exists and it will be replaced.\n\nAre you sure you want to continue?')
            if not result:
                # createDir = False
                # return createDir
                return ''
        try:
            shutil.rmtree(outputSubDir)
        except Exception as e:
            mb.showwarning(title='Directory error',
                           message="Could not create the directory " + outputSubDir + "\n\n" + str(e))
            outputSubDir = ''
    try:
        # chmod() changes the mode of path to the passed numeric mode
        if outputSubDir != '':
            os.chmod(Path(outputSubDir).parent.absolute(), 0o755)
            os.mkdir(outputSubDir, 0o755)
    except Exception as e:
        mb.showwarning(title='Directory error',
                       message="Could not create the directory " + outputSubDir + "\n\n" + str(e))
        print("error: ", e.__doc__)
        # createDir = False
        outputSubDir=''

    return outputSubDir


# for folder, subs, files in os.walk(inputDir):
# 	folderID += 1
# 	print("\nProcessing folder " + str(folderID) + "/ " + os.path.basename(
# 		os.path.normpath(folder)))
# 	for filename in files:
# https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
def getFileList_SubDir(inputFilename, inputDir, fileType='.*', silent=False):
    files = []
    if inputDir!='':
        if not checkDirectory(inputDir):
            return files
        for path in Path(inputDir).rglob('*' + fileType):
            files.append(str(path))
    else:
        if not checkFile(inputFilename):
            return files
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




import functools
from datetime import datetime
import os


# the below is to convert from self-defined date format to the correct datetime format
rule_to_format = {
    "mm-dd-yyyy": "%m-%d-%Y",
    "dd-mm-yyyy": "%d-%m-%Y",
    "yyyy-mm-dd": "%Y-%m-%d",
    "yyyy-dd-mm": "%Y-%d-%m",
    "yyyy-mm": "%Y-%m",
    "yyyy": "%Y",
}
def parse_date(date_str, date_formats):
    # the parse date takes in a string like 09-19-2002 and converts using a date formats defined above
    try:
        return datetime.strptime(date_str, rule_to_format[date_formats])
    except ValueError:
        pass
    return None
# this below function attempts to make it more clear in structure.
def help_date(c1, c2, date_loc, file_end, compare_date):
    val1 = parse_date(c1[date_loc].replace(file_end, ''), compare_date)
    val2 = parse_date(c2[date_loc].replace(file_end, ''), compare_date)

    if val1 is not None and val2 is not None:
        return val1<val2
    return -1
def complete_order(bb, c):
    # Helper function. usage: bb is the number, for instance 4. c is the list of preference, that is not complete.
    # for instance bb = 5, c = [1,3,4], then out = [0,2,3,1,4]. In short, it seeks
    # to find a sequence where the desired sequence is preserved, and following that complement item
    # index will be in order. This way the self compared function can be properly
    # instantiated.
    all_elements = set(range(1, bb+1))
    non_appearing_elements = list(all_elements.difference(set(c)))
    non_appearing_elements.sort()
    return [x-1 for x in (c+ non_appearing_elements)]
  ##############
  # example: input_list: a lists of files
    # compare_split, what do you want to be splitting each file. For instance, a_b_1989.txt, has it _.
    # compare_date, what form of date do you want to be compared. For instance, YYYY
    # file_end, what file ending is the file, for instance, .txt in the above case
    # date_loc, where is your date location. For instance, the above is 3 (natural order).
    # ordering: the string like "2,3"



def do_compare(input_list, file_end, sort_order, compare_split, date_format, date_loc):
    def compare(filename1, filename2):
        if not compare_split in filename1:
            print("Non fatal filename error in filename separator. Error ignored.\nThe filename separator '" + compare_split + "' stored for the filenames in your corpus is not contained in the filename\n   " + filename1 + "\nYou should edit the filename settings using the button 'Setup INPUT/OUTPUT configuration at the top of the GUI.\n\n")
            return -1
        if not compare_split in filename2:
            #  The information may have been entered incorrectly when setting up INPUT/OUTPUT (I/O) configuration. Please, check and edit the information. The information may have been entered incorrectly when setting up INPUT/OUTPUT (I/O) configuration. Please, check and edit the information.
            print("Non fatal filename error in filename separator. Error ignored.\nThe filename separator '" + compare_split + "' stored for the filenames in your corpus is not contained in the filename\n   " + filename2 + "\nYou should edit the filename settings using the button 'Setup INPUT/OUTPUT configuration at the top of the GUI.\n\n")
            return -1

        try:
            filename1 = os.path.basename(filename1).replace(file_end, '')
            filename2 = os.path.basename(filename2).replace(file_end, '')

            if compare_split in filename1 and compare_split in filename2:
                # scenario where filenames contain separators
                filename1 = filename1.split(compare_split)
                filename2 = filename2.split(compare_split)
                i = 0
                q = complete_order(len(filename1), [int(x) for x in sort_order.split(",")])

                while i <= len(filename1) - 1:
                    if q[i] + 1 == date_loc:
                        if help_date(filename1, filename2, date_loc - 1, file_end, date_format):
                            return -1
                        else:
                            return 1
                    else:
                        if filename1[q[i]] < filename2[q[i]]:
                            return -1
                        else:
                            return 1
                    i += 1
            else:
                # scenario where filenames contain dates
                val1 = parse_date(filename1, date_format)
                val2 = parse_date(filename2, date_format)
                if val1 is not None and val2 is not None:
                    return -1 if val1 < val2 else 1
        except:
            # The following pair of filenames are incompatible with the
            print("Non fatal filename error: date error. Error ignored.\nThe date format " + date_format + " and/or date location " + str(date_location) + " stored for the filenames in your corpus are not valid for the filename\n   " + filename2 + "\nYou should edit the filename settings using the button 'Setup INPUT/OUTPUT configuration at the top of the GUI.\n\n")
            print(filename1, "\n", filename2)
            return -1

    return sorted(input_list, key=functools.cmp_to_key(compare))


def getFileListOld(inputFile, inputDir, fileType='.*',silent=False):
    files = []
    if inputDir != '':
        if not checkDirectory(inputDir):
            return files
        for path in Path(inputDir).glob('*' + fileType):
            files.append(str(path))
        if len(files) == 0:
            mb.showwarning(title='Input files error',
                           message='No files of type ' + fileType + ' found in the directory\n\n' + inputDir)
    else:
        if not checkFile(inputFile):
            return files
        if inputFile.endswith(fileType):
            files = [inputFile]
        else:
            mb.showwarning(title='Input file error',
                           message='The input file type expected by the algorithm is ' + fileType + '.\n\nPlease, select the expected file type and try again.')
    return files
def getFileList(inputFile, inputDir, fileType='.*',silent=False, configFileName=''): #New
    files = []

    if inputDir != '':
        if not checkDirectory(inputDir):
            return files
        for path in Path(inputDir).glob('*' + fileType):
            files.append(str(path))
        if len(files) == 0:
            mb.showwarning(title='Input files error',
                           message='No files of type ' + fileType + ' found in the directory\n\n' + inputDir)
    else:
        if not checkFile(inputFile):
            return files
        if inputFile.endswith(fileType):
            files = [inputFile]
        else:
            mb.showwarning(title='Input file error',
                           message='The input file type expected by the algorithm is ' + fileType + '.\n\nPlease, select the expected file type and try again.')
    configFileName= GUI_IO_util.configPath + os.sep+configFileName
    #print(inputDir)

    # append sort order and separator
    # unfortunately, the sort order is saved as first column in the config file and separator second,
    #   contrary to the display in the IO setup GUI)
    if configFileName!='':
        import pandas as pd
        try:
            a = pd.read_csv(configFileName, index_col=False,encoding='utf-8',on_bad_lines='skip')
        except:
            if configFileName=='NLP_default_IO_config.csv':
                mb.showwarning(title='Input config file error',
                               message='The default I/O config file ' + configFileName + ' does not exist.\n\nPlease, use the "Setup INPUT/OUTPUT configuration" button to setup the I/O config file and try again.')
            else:
                mb.showwarning(title='Input config file error',
                               message='The GUI-specific config file ' + configFileName + ' does not exist.\n\nPlease, use the dropdown menu "I/O configuration" to select the GUI-specific option, then click on "Setup INPUT/OUTPUT configuration" button to setup the GUI-specific I/O config file and try again.')
            return files

        sort_order = str(a['Sort order'][1])

        if str(sort_order) =="nan":
            sort_order = "1"
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Warning',
                        "No sort order available. Files will be read without sorting.\nIf you wish to sort the input files in a specific order, you should edit the filename settings using the button 'Setup INPUT/OUTPUT configuration' at the top of the GUI.\n\n", False,'',True,'',False)

        try:
            aa = float(sort_order)
            aa = int(aa)
            sort_order = str(aa)
        except:
            pass

        separator = a['Item separator character(s)'][1]
        if str(separator)=="nan":
            separator=' '

        date_format = a['Date format'][1]
        try:
            date_pos = int(a['Date position'][1])
        except:
            date_pos = 9e999
        #@@@
        # separator = a['Item separator character(s)'][1]
        # if str(separator)=="nan":
        #     separator=' '

        try:
            files = do_compare(files, fileType, sort_order, separator, date_format, date_pos)
        except:
            files.sort()
        return files


def selectFile(window, IsInputFile, checkCoNLL, title, fileType, extension, outputFileVar=None,
               initialFolder=''):
    inputFilename = ""
    # print(fileType, extension, GUI_util.outputDir.get())
    if initialFolder == '':
        # initialFolder = os.path.dirname(os.path.abspath(__file__)) # this sets itself on NLP\src
        if extension == '.txt':
            initialFolder = GUI_IO_util.sampleData_libPath
        else:
            if GUI_util.output_dir_path.get()!='' and extension == '.csv':
                initialFolder = GUI_util.input_main_dir_path.get()
    if IsInputFile == True:  # as opposed to output file
        # when the file string is blank, the directory option should always also be available
        inputFilename = tk.filedialog.askopenfilename(initialdir=initialFolder, title=title, filetypes=fileType)
        from os.path import splitext
        file_name, extension = splitext(inputFilename)
    else:
        if outputFileVar != None:
            outputFilename = outputFileVar
            inputFilename = tk.filedialog.asksaveasfile(initialdir=initialFolder, initialfile=outputFilename.get(),
                                                   title=title, filetypes=fileType)
        else:
            print('Error in output file name creation')
    # when the file string is blank, the directory option should always also be available
    if inputFilename is None:
        inputFilename = ""
    inputFilename = str(inputFilename)
    if len(inputFilename) < 3:
        inputFilename = ""
    if (checkCoNLL == True) and (IsInputFile == 1) and (extension == ".csv") and (len(inputFilename) > 3):
        if CoNLL_util.check_CoNLL(inputFilename, False) == False:
            inputFilename = ""
    return inputFilename


def selectDirectory(title, initialFolder=''):
    if initialFolder == '':
        # initialFolder = os.path.dirname(os.path.abspath(__file__)) NLP\src
        initialFolder = GUI_IO_util.sampleData_libPath
    path = tk.filedialog.askdirectory(initialdir=initialFolder, title=title)
    return path


def openExplorer(window, directory):
    if not os.path.isdir(directory):
        mb.showwarning(title='Input dir error',message='The directory ' + directory + ' does not exist. It must have been removed.\n\nPlease, select a different directory and try again.')
    if sys.platform == 'win32':  # Windows
        os.startfile(directory)
    elif sys.platform == 'darwin':  # Mac
        subprocess.Popen(['open', directory])
    else:
        try:
            subprocess.Popen(['xdg-open', directory])  # Linux
        except OSError:
            print("OS error in accessing directory")

# when called from GUI_util command=lambda we open the file
# when called from NLP_setup_IO_main we just want to remove the date portion from the filename without opening the file
def open_file_removing_date_from_filename(window,inputFile, open):
    if ' (Date: ' in inputFile:
        char_pos = inputFile.find(' (Date: ')
        inputFile = inputFile[:char_pos] # remove the date portion (e.g., (Date: mm-dd-yyyy, _, 4) from the filename
        inputFile.rstrip()
    if open:
        openFile(window, inputFile)
    return inputFile

# when called from GUI_util command=lambda we open the directory
# when called from NLP_setup_IO_main we just want to remove the date portion from the directory without opening the directory
def open_directory_removing_date_from_directory(window,inputDir, open):
    if ' (Date: ' in inputDir:
        char_pos = inputDir.find(' (Date: ')
        inputDir = inputDir[:char_pos] # remove the date portion (e.g., (Date: mm-dd-yyyy, _, 4) from the dir name
        inputDir.rstrip()
    if open:
        openExplorer(window, inputDir)
    return inputDir

# returns date, dateStr
def getDateFromFileName(file_name, date_format='mm-dd-yyyy', sep='_', date_field_position=2, errMsg=True):

    # configFile_basename is the filename w/o the full path
    file_name = ntpath.basename(file_name)
    x = file_name

    reminders_util.checkReminder(file_name,
                                 reminders_util.title_options_date_embedded,
                                 reminders_util.message_date_embedded,
                                 False)
    # must assign or you get an error in return
    date = ''
    month=''
    day=''
    year=''
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
                # date = datetime.datetime.strptime(raw_date, '%m-%d-%Y').date()
                date = datetime.strptime(raw_date, '%m-%d-%Y').date()
                dateStr = date.strftime('%Y-%m-%d')
                month=dateStr[5:7]
                day=dateStr[8:10]
                year=dateStr[:4]
            elif date_format == 'dd-mm-yyyy':
                # date = datetime.datetime.strptime(raw_date, '%d-%m-%Y').date()
                date = datetime.strptime(raw_date, '%d-%m-%Y').date()
                dateStr = date.strftime('%Y-%m-%d') # '%d-%m-%Y'
                month=dateStr[5:7]
                day=dateStr[8:10]
                year=dateStr[:4]
            elif date_format == 'yyyy-mm-dd':
                # date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
                date = datetime.strptime(raw_date, '%Y-%m-%d').date()
                dateStr = date.strftime('%Y-%m-%d') # '%Y-%m-%d'
                month=dateStr[5:7]
                day=dateStr[8:10]
                year=dateStr[:4]
            elif date_format == 'yyyy-dd-mm':
                # date = datetime.datetime.strptime(raw_date, '%Y-%d-%m').date()
                date = datetime.strptime(raw_date, '%Y-%d-%m').date()
                dateStr = date.strftime('%Y-%m-%d') # '%Y-%d-%m'
                month=dateStr[5:7]
                day=dateStr[8:10]
                year=dateStr[:4]
            elif date_format == 'yyyy-mm':
                # date = datetime.datetime.strptime(raw_date, '%Y-%m').date()
                date = datetime.strptime(raw_date, '%Y-%m').date()
                dateStr = date.strftime('%Y-%m')
                month=dateStr[5:7]
                day=0
                year=dateStr[:4]
            elif date_format == 'yyyy':
                # date = datetime.datetime.strptime(raw_date, '%Y').date()
                date = datetime.strptime(raw_date, '%Y').date()
                dateStr = date.strftime('%Y')
                month = 0
                day = 0
                year = dateStr[:4]
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
    int_month=''
    int_day=''
    int_year=''
    if month!='':
        int_month=int(month)
    if day!='':
        int_day=int(day)
    if year != '':
        int_year=int(year)
    return date, dateStr, int_month, int_day, int_year

def checkDirectory(path, message=True):
    if os.path.isdir(path):
        return True
    else:
        if message:
            mb.showwarning(title='Directory error',
                           message='The directory ' + path + ' does not exist. It may have been renamed, deleted, moved.\n\nPlease, check the DIRECTORY and try again')
        return False


# check to make sure the file exists, and optionally that the desired extension matches the file's
# also gives user the option to generate a message box warning of why
def checkFile(inputFilename, extension=None, silent=False):
    if 'reminders.csv' in inputFilename:
        head, tail = os.path.split(inputFilename)
        reminders_util.generate_reminder_list(head)
    if not os.path.isfile(inputFilename):
        if not silent:
            print("The file " + inputFilename + " could not be found.")
            mb.showwarning(title='Input file not found',
                           message='Error in input filename and path.\n\nThe file ' + inputFilename + ' could not be found.\n\nPlease, check the INPUT FILE PATH and try again.')
        return False
    if extension != None and not '.' + inputFilename.rsplit('.', 1)[1] == extension:
        if not silent:
            print('File has the wrong extension.')
            mb.showwarning(title='Input file extension error',
                           message='Error in input filename and path.\n\nThe file ' + inputFilename + ' does not have the expected extension ' + extension + '\n\nPlease, check the INPUT FILE and try again.')
        return False
    else:
        return True


# inputFilename contains filename with path
def open_kmlFile(window,inputFilename):
    if sys.platform == 'win32':
        # https://stackoverflow.com/questions/26498302/how-to-load-the-kml-file-into-google-earth-using-python
        os.startfile(inputFilename)
        # also webbrowser.open(inputFilename) will open the kml file in GEP
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', inputFilename])
    else:
        try:
            subprocess.Popen(['xdg-open', inputFilename])
        except OSError:
            print("OS error in opening file " + inputFilename)


# opens a filename with its path
# if a file with the same name is already open, it throws an error
def openFile(window, inputFilename):
    if len(inputFilename) == 0:
        tk.messagebox.showinfo("Input file error", "The filename is blank. No file can be opened.")
        return
    if os.path.isfile(inputFilename):
        # windows
        if platform in ['win32', 'cygwin']:
            while True: # repeat until you close
                try:
                    os.system('start "" "' + inputFilename + '"')
                    break # exit loop
                except IOError as e:
                    mb.showwarning(title='Input file error',
                                   message="Could not open the file " + inputFilename + "\n\n"+str(e))
                    if "Errno 22" in str(e):
                        break  # exit loop; the error is not due to file being open
                    # mb.showwarning(title='Input file error',
                    #                message="Could not open the file " + inputFilename + "\n\nA file with the same name is already open. Please, close the Excel file and then click OK to resume.")
                    # restart loop
        # macOS and other unix
        else:
            while True: # repeat until you close
                try:
                    call(['open', inputFilename])
                    break # exit loop
                except IOError as e:
                    mb.showwarning(title='Input file error',
                                   message="Could not open the file " + inputFilename + "\n\n"+str(e))
                    if "Errno 22" in str(e):
                        break  # exit loop; the error is not due to file being open
                    # mb.showwarning(title='Input file error',
                    #                message="Could not open the file " + inputFilename + "\n\nA file with the same name is already open. Please, close the Excel file and then click OK to resume.")
                    # restart loop
    else:
        tk.messagebox.showinfo("Error", "The file " + inputFilename + " could not be found.")
        print("The file " + inputFilename + " could not be found.")


# open a set of output files (csv, txt,...) stored as a list in filesToOpen []
# filesToOpen is a single list []
def OpenOutputFiles(window, openOutputFiles, filesToOpen, outputDir, scriptName='', filesToOpenSubset=[]):
    if filesToOpen == None:
        return
    if len(filesToOpen) == 0:
        return
    if not isinstance(filesToOpen, list):
        if isinstance(filesToOpen, set):
            filesToOpen = list(set(filesToOpen))
        else:
            filesToOpen = list(filesToOpen)

    if len(filesToOpenSubset)> 0:
        filesToOpen=filesToOpenSubset

    # you want to check the number of files through all subdir created
    #   only when the output directory is NOT the default output directory
    #   (in which case you potentially get a huge number of files having nothing to do with the script being run)
    check_number_ofFiles = False
    if outputDir!=GUI_util.output_dir_path.get():
        # check that no output subdir has been created;
        #   e.g., the parse_annotator_main passes only the main output dir rather than the subdir
        temp_outputDir=outputDir
        check_number_ofFiles = True
    else:
        # get the outputDir from the first output file
        # temp_outputDir = os.path.dirname(outputDir)
        temp_outputDir=os.path.dirname(filesToOpen[0])
        if temp_outputDir!=outputDir:
            check_number_ofFiles = True
    split_files = False
    if check_number_ofFiles: #outputDir != temp_outputDir: #GUI_util.output_dir_path.get():
        subDirs=next(os.walk(temp_outputDir))[1]
        listOfFiles = list()
        for (dirpath, dirnames, filenames) in os.walk(temp_outputDir):
            if "split_" in dirpath:
                split_files=True
                subDirs.remove(os.path.basename(dirpath))
                continue
            if len(os.listdir(dirpath))==0:
                # remove empty directories
                shutil.rmtree(dirpath)
                # remove from list of subDirs
                if os.path.basename(dirpath) in str(subDirs):
                    subDirs.remove(os.path.basename(dirpath))
                continue
            listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    else:
        listOfFiles = filesToOpen
        subDirs = []
    nFiles=len(listOfFiles)
    nSubDirs = len(subDirs)
    subDirs="\n".join(subDirs)
    wayTooMany = ''
    label = ''
    subsetLabel = ''
    opened_folder_label = ''

    if nFiles > 10:
        wayTooMany = "\n\nWAY TOO MANY TO BE OPENED AUTOMATICALLY."

    if nFiles == 1:
        file_singular_plural='file'
    else:
        file_singular_plural = 'files'

    opened_folder_label = "\n\nFor your convenience, the NLP Suite will place you in the main output subdirectory where you can select any other files you want/need to open:\n\n" + temp_outputDir

    if nSubDirs==1:
        label = " exported to the subfolder:\n\n" + temp_outputDir
    elif nSubDirs > 1:
        label = "  The files are organized in " + str(nSubDirs) + " different subfolders:\n\n" + subDirs

    if nSubDirs > 0:
        opened_folder_label = "\n\nFor your convenience, the NLP Suite will place you in this output subdirectory."

    if split_files:
        label = label + "\n\nA folder containing split files was generated by Stanford CoreNLP to deal with CoreNLP file-size limitation of 99000 characters. " \
                        "You do not need to be concerned about that; large files will have been split for processing and put back together automatically by the SVO algorithm."
    if nSubDirs > 0:
        if len(filesToOpenSubset)>0:
            subsetLabel = "\n\nThe NLP Suite will open next a subset of " + str(len(filesToOpenSubset)) + " most relevant output files from the different subfolders: all charts and main csv files.\n"

    # always open outputDir
    openExplorer(window, temp_outputDir)

    mb.showwarning(title="Output files",message="The " + scriptName + " has generated " +
                str(nFiles) + " " + file_singular_plural + " in output." + wayTooMany + label + subsetLabel + opened_folder_label)

    if nFiles > 10 and len(filesToOpenSubset) > 10:
        return

    if len(filesToOpen) == 1:
        singularPlural = 'file'
    else:
        singularPlural = 'files'
    if openOutputFiles == True:  # now the approach is to open all files at the end, so this extra check is redundant "and runningAll==False:""
        # should display a reminder about csv files with weird characters most likely dues to non utf-8 apostrophes and quotes
        #   but... this reminder does not have a specific config, so... perhaps *?
        reminders_util.checkReminder('*', reminders_util.title_csv_files, reminders_util.message_weird_characters, True)
        routine_options = reminders_util.getReminders_list('*')
        IO_user_interface_util.timed_alert(window, 2000, 'Warning',
                    'Opening ' + str(len(filesToOpen)) + ' output ' + singularPlural + '... Please wait...', False,'',True,'',True)
        if isinstance(filesToOpen[0], list):
            filesToOpen = filesToOpen[0]
        for file in filesToOpen:
            if file == None or file == '':
                continue
            if os.path.isfile(file):
                if file.endswith('.kml'):
                    open_kmlFile(window, file)
                else:
                    openFile(window, file)
            # once printed empty array
        # if len(filesToOpen)>0:
        #     filesToOpen.clear()


def getFileExtension(inputFilename):
    path, inputfile = ntpath.split(inputFilename)  # remove/take out path
    inputfile, extension = os.path.splitext(inputfile)  # remove/take out the extension
    return extension

def getFilename(passed_string):

    # when X-axis values contain a document dressed for hyperlink and with full path
    #   undressed the hyperlink and only display the tail of the document
    tail=passed_string
    tail_noExtension=tail

    if isinstance(passed_string, str): # and math.isnan(passed_string) is False
        if '=hyperlink' in passed_string:
            passed_string=IO_csv_util.undressFilenameForCSVHyperlink(passed_string)
        if os.path.isfile(passed_string):
            head, tail = os.path.split(passed_string)
            tail_noExtension = tail.replace(getFileExtension(tail),'')
        return tail, tail_noExtension, passed_string
    elif math.isnan(passed_string):
        return '', '', passed_string


# def getFilename(inputFilename):
#     path, inputfile = ntpath.split(inputFilename)  # remove/take out path
#     inputfile, extension = os.path.splitext(inputfile)  # remove/take out the extension
#     return inputfile


# inputFilename is the input filename with path
# returns outFilename with path
# label1 (SCNLP, QC, NVA,...)
#  in label1 the following labels are passed by the calling script: SCNLP (Stanford CoreNLP), QC (query conll), NVA (noun verb analysis), FW (function words), TC (tpic modeling), SA (sentiment analysis), CA (concretenss analysis)
# label2 (sub-field, e.g., pigs_Lemma, or hedonometer)
# label3,label4,label5 are available options
def generate_output_file_name(inputFilename, inputDir, outputDir, outputExtension, label1='', label2='', label3='', label4='',
                              label5='', useTime=True, disable_suffix=False):
    useTime = False  # files become too long with the addition of datetime
    if inputDir!='':
        Dir = os.path.basename(os.path.normpath(inputDir))
        inputfile='Dir_' + Dir
        inputfile_noExtension=''
    elif inputFilename!='':
        inputfile, inputfile_noExtension, filename_no_hyperlink = getFilename(inputFilename)
        # use inputfile_noExtension for json
        inputfile = inputfile_noExtension
    else:
        inputfile = ''
    default_outputFilename_str =''
    # do not add the NLP_ prefix if processing a file previously processed and with the prefix already added
    if inputfile[0:4]!='NLP_': #"NLP_" not in inputfile:
        if label1=='':
            default_outputFilename_str = 'NLP_' + inputfile  # adding to front of file name
        else:
            if inputfile!='':
                default_outputFilename_str = 'NLP_' + str(label1) + "_" + inputfile  # adding to front of file name
            else:
                default_outputFilename_str = 'NLP_' + str(label1)   # adding to front of file name
    else:
        if label1=='':
            default_outputFilename_str=inputfile
        else:
            if inputfile[0:4]=='NLP_': #only replace first 4 characters since NLP may occur elsewhere in the filename
                default_outputFilename_str = inputfile[0:4].replace('NLP_','NLP_' + label1 + '_') + inputfile[4:]
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
    outFilename = os.path.join(outputDir, default_outputFilename_str)

    # rename a filename coreferenced by CoreNLP to obtain better filename; NLP_CoreNLP_coref should only be once n the filename
    if 'NLP_CoreNLP_coref' in outFilename:
        if outFilename.count('NLP_CoreNLP_coref')>1:
            outFilename = outFilename.replace('NLP_CoreNLP_coref','coref')
            # outFilename = 'NLP_CoreNLP_coref'+outFilename
    if 'CoreNLP_SENNA_SVO_coref' in outFilename:
        outFilename = outFilename.replace('CoreNLP_SENNA_SVO_coref','_coref')

    if sys.platform == 'win32':  # Windows
        if len(outFilename)>255:
            mb.showwarning(title='Warning',message='The length (' + str(len(outFilename)) + ' characters) of the filename\n\n' + outFilename + '\n\nexceeds the maximum length of 255 characters allowed by Windows Operating System.\n\nPlease, reduce the filename length and try again.')

    return outFilename


# extension can be 'txt', 'xlsx', 'doc, 'docx' WITHOUT .
def GetNumberOfDocumentsInDirectory(inputDirectory, extension=''):
    numberOfDocs = 0
    if inputDirectory=='':
        mb.showwarning(title='No directory selected',message='The directory passed to the GetNumberOfDocumentsInDirectory function is blank.\n\nFunction aborted.')
        return numberOfDocs
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
    if inputfile=='':
        mb.showwarning(title='File error',
                       message="The input file is blank.")
        return ""
    try:
        csvfile = open(inputfile, open_type, newline='', encoding=encoding_type, errors='ignore')
        return csvfile
    except IOError:
        mb.showwarning(title='File error',
                       message="Could not open the file " + inputfile + "\n\nA file with the same name is already open.\n\nPlease, close the Excel file and then click OK to resume.")
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
        if '---------------------' in script or len(script)==0:
            mb.showwarning(title='Warning',
                           message="The selected option '" + script + "' is not a valid option.\n\nIt is only an explanatory label. \n\nPlease, select a different option.")
            return script_to_run, IO_values

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
        if IO_libraries_util.check_inputPythonJavaProgramFile(scriptName) == False:
            return script_to_run, IO_values
    # passed to NLP.py
    script_to_run = val[0]

    return script_to_run, IO_values

def run_jar_script(scriptName, inputFilename, inputDir, outputDir, openOutputFiles, createCharts, chartPackage):
    filesToOpen = []
    if IO_libraries_util.check_inputPythonJavaProgramFile(scriptName) == False:
        return
    # if scriptName=='Sentence_Complexity.jar':
    #     outputFilename=IO_util.generate_output_file_name(inputFilename,outputDir,'.csv','SCo','','')
    #     filesToOpen.append(outputFilename)
    #     temp_outputFilename=ntpath.basename(outputFilename)
    #     IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running Sentence Complexity at',True,'\n\nYou can follow Sentence Complexity in command line.')
    #     subprocess.call(['java', '-jar', 'Sentence_Complexity.Jar', inputFilename, outputDir, temp_outputFilename])
    #     IO_util.timed_alert(GUI_util.window,2000,'Analysis end','Finished running Sentence Complexity at',True)
    #     if createCharts:
    #         columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=[[1,3], [1,4], [1,6], [1,7]]
    #         hover_label=['Sentence','Sentence','Sentence','Sentence']
    #         outputFilenameXLSM_1 = charts_util.run_all(columns_to_be_plotted,inputFilename,outputDir, outputFilename, chart_type_list = ["line"], chart_title= "Sentence complexity", column_xAxis_label_var = 'Sentence ID',column_yAxis_label_var = 'Complexity',outputExtension = '.xlsm',label1='Scomp',label2='line',label3='chart',label4='',label5='', useTime=False,disable_suffix=True,  count_var=0, column_yAxis_field_list = [], reverse_column_position_for_series_label=False , series_label_list=[''], second_y_var=0, second_yAxis_label='', hover_info_column_list=hover_label)
    #         if outputFilenameXLSM_1 != "":
    #             filesToOpen.append(outputFilenameXLSM_1)

    # elif scriptName=='DependenSee.jar':
    #     #inputFilename must include the file full path with txt extension
    #     #inputFilename must be a txt file
    #     IO_util.timed_alert(GUI_util.window,2000,'Analysis start','Started running Sentence visualization: Dependency tree viewer (png graphs) at',True,'\n\nYou can follow Sentence Complexity in command line.')
    #     subprocess.call(['java', '-jar', 'DependenSee.Jar', inputFilename, outputDir])
    #     IO_util.timed_alert(GUI_util.window,2000,'Analysis end','Finished running Sentence visualization: Dependency tree viewer (png graphs) at',True,'\n\nMake sure to open the png files in output, one graph for each sentence.')
    if visualization_tools == "Sentence visualization: Dynamic sentence network viewer (Gephi graphs)":
        # TODO the script does not work even in command line using the arguments in the ReadMe file; it seems to want two more parameters
        """
        Error in input parameters
        Usage Example:
        args1 = "inputFilename"
        args2 = "outputinputFilename.gexf"
        args3 = true or false
        args4 = $$$
        # if checkIO_Filename_InputDir ("Sentence Visualization: Dynamic Sentence Network Viewer (Gephi graphs)",inputFilename, inputDir, outputDir):
        #     subprocess.call(['java', '-jar', 'DynamicSentenceViewer.jar', inputFilename, outputDir])
        """
        return
    if openOutputFiles == True:
        OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)


# The NLP script and sentence_analysis script use pydict dictionaries to run the script selected in a menu
# the dict can contain a python file, a jar file or a combination of python file + function
def runScript_fromMenu_option(script_to_run, IO_values, inputFilename, inputDir, outputDir,
                              openOutputFiles, createCharts, chartPackage, processType=''):
    filesToOpen = []
    if len(script_to_run) == 0:
        return filesToOpen
    if script_to_run == "Gender guesser":
        import IO_internet_util
        # check internet connection
        if not IO_internet_util.check_internet_availability_warning("Gender guesser"):
            return filesToOpen
        webbrowser.open('http://www.hackerfactor.com/GenderGuesser.php#About')
    elif script_to_run.endswith('.py'):  # with GUI
        if IO_libraries_util.check_inputPythonJavaProgramFile(script_to_run) == False:
            return filesToOpen
        call("python " + script_to_run, shell=True)
    elif script_to_run.endswith('.jar'):  # with GUI
        run_jar_script(script_to_run, inputFilename, inputDir, outputDir, openOutputFiles,
                       createCharts, chartPackage)
    else:  # with NO GUI; does not end with py
        script = script_to_run.split(".", 1)
        import importlib
        pythonFile = importlib.import_module(script[0])
        # script[0] contains the Python file name
        # script[1] contains the function name inside a specific Python file
        if IO_libraries_util.check_inputPythonJavaProgramFile(script[0] + '.py') == False:
            return filesToOpen
        func = getattr(pythonFile, script[1])
        # # correct values are checked in NLP_GUI
        if IO_values == 1: # no inputDir
            filesToOpen = func(GUI_util.window, inputFilename, outputDir, openOutputFiles, createCharts, chartPackage, processType)
        elif IO_values == 2: # no inputFilename
            filesToOpen = func(GUI_util.window, inputDir, outputDir, openOutputFiles, createCharts, chartPackage, processType)
        else: # both inputFilename and inputDir
            filesToOpen = func(GUI_util.window, inputFilename, inputDir, outputDir,
                 openOutputFiles,createCharts,chartPackage, processType)

        return filesToOpen

"""
#does not work, despite StackOverFlow recommendation; always returns None
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


 # move the gender & quote files under the gender & quote dir where a user is more likely to look for it
# the location_filename is moved above

    # if gender_var:
    #     # move the gender file under gender dir where a user is more likely to look for it
    #     gender_outputDir = outputDir + os.sep + os.path.basename(outputDir.replace('_SVO_', '_gender_'))
    #     if os.path.isfile(gender_filename) and os.path.isdir(gender_outputDir):
    #         target_filePath = gender_outputDir + os.sep + os.path.basename(gender_filename)
    #         # move the csv gender file
    #         if not os.path.isfile(target_filePath):
    #             os.replace(gender_filename, target_filePath)
    #         # move the html gender file
    #         target_filePath = gender_outputDir + os.sep + os.path.basename(gender_filename_html)
    #         if os.path.isfile(gender_filename_html) and not os.path.isfile(target_filePath):
    #             os.replace(gender_filename_html, target_filePath)
    #
    # if quote_var:
    #     quote_outputDir = outputDir + os.sep + os.path.basename(outputDir.replace('_SVO_', '_quote_'))
    #     if os.path.isfile(quote_filename) and os.path.isdir(quote_outputDir):
    #         target_filePath = quote_outputDir + os.sep + os.path.basename(quote_filename)
    #         # move the quote file under quote dir where a user is more likely to look for it
    #         os.replace(quote_filename, target_filePath)