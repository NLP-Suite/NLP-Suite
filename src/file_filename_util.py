# Written by Roberto Franzosi December 2019
#	edited July 2020

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "file_filename_util",
                                ['csv', 'os', 'platform', 'shutil', 'time', 'datetime']) == False:
    sys.exit(0)

import os
import os.path, time, datetime
from datetime import datetime, date
import csv
import shutil
import platform

import IO_csv_util
import IO_files_util

def dateGreater(d1, d2):
    # This function returns True if d1 is a more recent date than d2, False otherwise
    if d1 == '' or d2 == '':
        print("Could not compare dates.")
        return False
    else:
        dt1 = datetime.strptime(d1, "%m/%d/%Y")
        dt2 = datetime.strptime(d2, "%m/%d/%Y")
        return dt1.date() > dt2.date()


def purge_duplicate_rows_byFilename(window, inputFilename, output_path, openOutputFiles, filenameCol):
    bestFiles = {}
    filenameColNum = 2
    with open(inputFilename, 'r', encoding="utf-8", errors='ignore') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        filenameColNum = IO_csv_util.get_columnNumber_from_headerValue(header, filenameCol)
        if header is not None:
            for row in csv_reader:
                head, fName = os.path.split(row[filenameColNum])
                # First, check if the file at hand exists in the dictionary
                if fName in bestFiles:
                    # File exists, compare it's modification date to the one in the dictionary currently
                    dictDate = get_creation_date(bestFiles.get(fName)[filenameColNum])[1]
                    testDate = get_creation_date(row[filenameColNum])[1]
                    if dateGreater(testDate, dictDate):
                        # The current row has a newer file, update the value in dictionary to this row
                        bestFiles[fName] = row
                else:
                    # File is not yet in dictionary, add it in
                    bestFiles[fName] = row

    deleteList = []
    with open(inputFilename, 'r', encoding="utf-8", errors='ignore') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header is not None:
            for row in csv_reader:
                head, fName = os.path.split(row[filenameColNum])
                # fName = row[0]
                if fName in bestFiles:
                    # Only print rows NOT in bestFiles. We want to output the old files (they are the ones to be deleted).
                    if row != bestFiles.get(fName):
                        # The above line performs the filtering and skips the deletion of the files we want to KEEP.
                        deleteList.append([row[filenameColNum]])

    # Now, we can call list_to_csv so that we can generate a new CSV with the list of files to be deleted
    filesToOpen = [output_path + os.sep + 'files_to_delete.csv']
    IO_csv_util.list_to_csv(window, deleteList, output_path + os.sep + 'files_to_delete.csv', colnum=0)
    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


def fill_dictionary(row, dict, nameColNum=0, filenameColNum=2):
    name = row[nameColNum]
    head, fName = os.path.split(row[filenameColNum])
    # Add this file to the pdf dictionary
    if name in dict:
        # File exists in the dictionary, compare its length and date
        dhead, dfName = os.path.split(dict.get(name)[filenameColNum])
        if len(fName) > len(dfName):
            # Len is greater, replace value in dictionary
            dict[name] = row
        elif len(fName) == len(dfName):
            # Lens are equal, take the one with most recent mod date
            dictDate = get_creation_date(dict.get(name)[filenameColNum])[1]
            testDate = get_creation_date(row[filenameColNum])[1]
            if dateGreater(testDate, dictDate):
                # The current row has a newer file, update the value in dictionary to this row
                dict[name] = row
    else:
        # Not yet in dict, add it in
        dict[name] = row


def purge_partial_matches(window, inputFilename, output_path, openOutputFiles, nameCol, filenameCol):
    pdfdict = {}
    docxdict = {}
    nameColNum = 0
    filenameColNum = 2
    with open(inputFilename, 'r', encoding="utf-8", errors='ignore') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        nameColNum = IO_csv_util.get_columnNumber_from_headerValue(header, nameCol)
        filenameColNum = IO_csv_util.get_columnNumber_from_headerValue(header, filenameCol)
        print(nameColNum, filenameColNum)
        if header is not None:
            for row in csv_reader:
                if os.path.splitext(row[filenameColNum])[1].lower() == '.pdf':
                    fill_dictionary(row, pdfdict, nameColNum, filenameColNum)
                elif os.path.splitext(row[filenameColNum])[1].lower() == '.docx':
                    fill_dictionary(row, docxdict, nameColNum, filenameColNum)
                else:
                    print("Unrecognized file:", row[filenameColNum])

    deleteList = []
    with open(inputFilename, 'r', encoding="utf-8", errors='ignore') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header is not None:
            for row in csv_reader:
                # Go through the csv file again, this time picking out the files that are NOT in the dictionary
                name = row[nameColNum]
                head, fName = os.path.split(row[filenameColNum])
                if os.path.splitext(fName)[1].lower() == '.pdf':
                    # We are in the pdf dictionary
                    if row != pdfdict.get(name):
                        # This file is not in the dictionary, so we should delete it! Add it to the list.
                        deleteList.append([row[filenameColNum]])
                elif os.path.splitext(fName)[1].lower() == '.docx':
                    if row != docxdict.get(name):
                        deleteList.append([row[filenameColNum]])

    # Now, we can call list_to_csv so that we can generate a new CSV with the list of files to be deleted
    filesToOpen = [output_path + os.sep + 'files_to_delete.csv']
    IO_csv_util.list_to_csv(window, deleteList, output_path + os.sep + 'files_to_delete.csv', colnum=0)
    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)


def writeOutput(inputPath, input_filename, outputPath, output_filename, fieldnames,
                by_creation_date_var,
                creation_date,
                modification_date,
                by_author_var,
                author,
                string_entry_var,

                by_embedded_items_var,
                number_of_items_var,
                embedded_item_character_value,

                character_count_var,
                character_entry_var,
                characterCount,

                fileName_embeds_date,
                date,
                dateStr):
    printLine = {}
    if not os.path.isdir(os.path.join(inputPath, input_filename)):
        with open(outputPath + os.sep + output_filename, 'a', errors='ignore', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            head, tail = os.path.split(input_filename)
            printLine = {'File_Name': tail, 'Path_To_File': IO_csv_util.dressFilenameForCSVHyperlink(inputPath),
                         'File_Name_With_Path': IO_csv_util.dressFilenameForCSVHyperlink(input_filename)}
            if by_creation_date_var == 1:
                printLine['Creation_date'] = creation_date
                printLine['Modification_date'] = modification_date
            if by_author_var == 1:
                printLine['Author'] = author
            if by_embedded_items_var == 1:
                printLine['Embedded items count (' + embedded_item_character_value + ')'] = str(number_of_items_var)
            if character_count_var == 1:
                printLine['Character count (' + character_entry_var + ')'] = str(characterCount)
            if fileName_embeds_date == 1:
                # print("date,dateStr",date,dateStr)
                printLine['Date'] = dateStr
            writer.writerow(printLine)
    else:
        fileFound = False


def processFile(inputPath, outputPath, filename, output_filename,
                fieldnames,
                selectedCsvFile_var,
                hasFullPath,
                utf8_var,
                ASCII_var,
                list_var,
                rename_var,
                copy_var,
                move_var,
                delete_var,
                rename_new_entry,
                file_type_menu_var,
                by_creation_date_var,
                by_author_var,
                by_prefix_var,
                by_substring_var,
                string_entry_var,
                by_foldername_var,
                folder_character_separator_var,
                by_embedded_items_var,
                comparison_var,
                number_of_items_var,
                embedded_item_character_value,
                include_exclude_var,
                character_count_var,
                character_entry_var,
                include_subdir_var,
                fileName_embeds_date,
                date_format,
                date_separator,
                date_position):
    # TODO must handle selectedCsvFile_var
    #	if selectedCsvFile_var.get()!='' if whatever filename is passed to processFile is in the csv file then we do something

    characterCount = 0
    creation_date = ''
    modification_date = ''
    author = ''
    date = ''
    dateStr = ''
    fileFound = True

    if character_count_var == 1:
        # use the Python built-in function count for strings
        characterCount = filename.count(character_entry_var)
    else:
        characterCount = 0

    if by_prefix_var == 1:
        if filename.startswith(string_entry_var):
            fileFound = True
        else:
            fileFound = False

    if len(file_type_menu_var) > 0:
        if file_type_menu_var == '*':
            fileFound = True
        else:
            ext = IO_files_util.getFileExtension(os.path.join(inputPath, filename))

            if ext == "." + file_type_menu_var:
                fileFound = True
            else:
                fileFound = False

    # endswith would not distinguish between, for instance, .doc and .docx or .xls and .xlsx
    # if filename.endswith('.'+by_file_type_var):
    # 	fileFound=True

    if by_substring_var == 1:
        if string_entry_var in filename:
            fileFound = True
        else:
            fileFound = False

    if list_var == 1 and fileFound:
        # if utf8_var==1:
        #     import chardet
        #     the_encoding = chardet.detect(b'filename)['encoding']
        #
        #     try:
        #         filename.encode('utf-8')
        #     except UnicodeError:
        #         print('   Filename ' + filename + ' is not utf-8')
        # ASCII_var,

        # old_file=filename
        if by_creation_date_var == 1:
            creation_date, modification_date = get_creation_date(os.path.join(inputPath, filename))

        # https://stackoverflow.com/questions/7021141/how-to-retrieve-author-of-a-office-file-in-python
        # get_author works for docx files only
        if by_author_var == 1:
            ext = IO_files_util.getFileExtension(os.path.join(inputPath, filename))
            if ext == '.docx' or ext == 'docx':
                author = get_author(os.path.join(inputPath, filename))
            else:
                author = ""

        if fileName_embeds_date == 1:
            date, dateStr = IO_files_util.getDateFromFileName(filename, date_separator, date_position, date_format, False)

        if by_embedded_items_var == 1:
            # old_file = filename
            filename = get_spec_num_files(filename, comparison_var, number_of_items_var, embedded_item_character_value)
            # filename = numEmbedded(filename, comparison_var,  embedded_item_character_value, include_exclude_var)
            if filename == '':
                fileFound = False

    if rename_var == 1:
        if by_prefix_var == 1:
            # rename only the first occurrence when using the by_prefix_var option
            filenameOut = filename.replace(string_entry_var, rename_new_entry, 1)
        if by_substring_var == 1:
            filenameOut = filename.replace(string_entry_var, rename_new_entry)
        if by_foldername_var:
            currentDir = os.path.basename(os.path.normpath(inputPath))
            ext = IO_files_util.getFileExtension(os.path.join(inputPath, filename))
            n = len(ext)
            filename_noExtension = filename[:-n]
            filenameOut = filename.replace(filename,
                                           filename_noExtension + folder_character_separator_var + currentDir + ext)

        if fileFound == True:  # always True when Renaming the file
            try:
                os.rename(inputPath + os.sep + filename, inputPath + os.sep + filenameOut)
            except:
                print(
                    "Cannot rename file '" + filenameOut + "' because a file by that name already exists in the output directory.")
                fileFound = False
    # fileFound==False

    if "HYPERLINK" in filename:
        filename = IO_csv_util.undressFilenameForCSVHyperlink(filename)
    if len(filename) > 255:
        print(
            'The file ' + filename + ' was skipped from processing. The combined length of filename + path exceeds the maximum of 255 characters.')
        return False, len(filename), '', '', '', '', ''

    if copy_var == 1:
        if hasFullPath:
            try:
                shutil.copy(filename, outputPath + os.sep + os.path.split(filename)[1])
            except:
                print(
                    'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
                fileFound = False
        else:
            if fileFound == True:
                try:
                    shutil.copy(inputPath + os.sep + filename, outputPath + os.sep + filename)
                except:
                    print(
                        'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
                    fileFound = False
    if move_var == 1:
        if hasFullPath:
            try:
                shutil.move(filename, outputPath + os.sep + os.path.split(filename)[1])
                fileFound = False
            except:
                print(
                    'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
        else:
            if fileFound == True:
                try:
                    shutil.move(inputPath + os.sep + filename, outputPath + os.sep + filename)
                except:
                    print(
                        'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
                    fileFound = False

    if delete_var == 1:
        if hasFullPath:
            try:
                os.unlink(filename)
            except:
                print(
                    'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
                fileFound = False
        else:
            if fileFound == True:
                try:
                    os.unlink(inputPath + os.sep + filename)
                except:
                    print(
                        'The file ' + filename + ' was skipped from processing. An unexpected error occurred when processing the file.')
                    fileFound = False

    if (fileFound == True):

        writeOutput(inputPath, filename, outputPath, output_filename, fieldnames, by_creation_date_var, creation_date,
                    modification_date, by_author_var, author, string_entry_var, by_embedded_items_var,
                    number_of_items_var, embedded_item_character_value, character_count_var, character_entry_var,
                    characterCount, fileName_embeds_date, date, dateStr)

    return fileFound, characterCount, creation_date, modification_date, author, date, dateStr


# https://automatetheboringstuff.com/chapter9/

def get_count(path, outputPath, output_filename):
    folders = []
    for i in os.scandir(path):
        if i.is_dir():
            folders.append(i.path)

    fieldnames = ['Main_Dir', 'Subdir', 'pdf', 'doc', 'docx', 'txt', 'Matching']
    # fieldnames = ['a','b','c','d','e','f','g']
    # output_filename = 'Ext_count.csv'
    with open(outputPath + os.sep + output_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        i = 0
        for folder in folders:
            pdf, doc, docx, txt = 0, 0, 0, 0
            flag = True
            for file in os.listdir(folder):
                i = i + 1
                filename, file_extension = os.path.splitext(file)
                ext = file_extension[1:]
                if ext == 'pdf':
                    pdf += 1
                elif ext == 'doc':
                    doc += 1
                elif ext == 'docx':
                    docx += 1
                elif ext == 'txt':
                    txt += 1

                if (pdf != doc and doc != 0) or (pdf != docx and docx != 0) or (pdf != txt and txt != 0) or (
                        doc + docx + txt == 0 and pdf != 0):
                    flag = False
            subDir = os.path.basename(os.path.normpath(folder))
            printLine = {'Main_Dir': IO_csv_util.dressFilenameForCSVHyperlink(path),
                         'Subdir': IO_csv_util.dressFilenameForCSVHyperlink(subDir), 'pdf': pdf, 'doc': doc, 'docx': docx,
                         'txt': txt, 'Matching': flag}
            writer.writerow(printLine)
    return i


# https://stackoverflow.com/questions/7021141/how-to-retrieve-author-of-a-office-file-in-python
# get_author works for docx files only
def get_author(path_to_file):
    import zipfile, lxml.etree
    # open zipfile
    try:
        zf = zipfile.ZipFile(path_to_file)
    except:
        zf = ""
    # use lxml to parse the xml file we are interested in
    try:
        doc = lxml.etree.fromstring(zf.read('docProps/core.xml'))
    except:
        doc = ""
    # retrieve creator
    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    try:
        creator = doc.xpath('//dc:creator', namespaces=ns)[0].text
    except:
        creator = ""
    return creator


# https://stackoverflow.com/questions/7021141/how-to-retrieve-author-of-a-office-file-in-python

# https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
# path_to_file is the filename with path
def get_creation_date(path_to_file):
    creation_date = ''
    modification_date = ''

    # should not be a list but a string
    if isinstance(path_to_file, list):
        return creation_date, modification_date

    if len(str(path_to_file)) > 256:
        print("The filename and path " + str(
            path_to_file) + " exceeds the 256 character limit of filename length. Please, shorten the filename with its path and try again.")
        return creation_date, modification_date

    if os.path.isfile(path_to_file):
        pass
    else:
        print("The string " + str(
            path_to_file) + " is not a filename and path as expected. Document creation and modification date will be skipped.")
        return creation_date, modification_date

    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """

    if platform.system() == 'Windows':
        named_tuple = time.ctime(os.path.getctime(path_to_file))
        try:
            creation_date = datetime.strptime(named_tuple, "%a %b %d %H:%M:%S %Y").strftime("%m/%d/%Y")
        except:
            creation_date = ''
        try:
            modification_date = datetime.fromtimestamp(os.path.getmtime(path_to_file)).strftime("%m/%d/%Y")
        except:
            modification_date = ''
        if creation_date == None or modification_date == None:
            creation_date, modification_date = ''
        return creation_date, modification_date
    else:
        stat = os.stat(path_to_file)
        try:
            # return stat.st_birthtime,
            # https://www.w3resource.com/python-exercises/python-basic-exercise-64.php
            return time.ctime(os.path.getmtime(path_to_file)), time.ctime(os.path.getctime(path_to_file))
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_spec_num_files(filename, comparator, number_of_items_var, embedded_item_character_value):
    # outputList = []
    # with open(inputCSV, 'r', encoding="utf-8", errors='ignore') as read_obj:
    #     csv_reader = csv.reader(read_obj)
    #     header = next(csv_reader)
    #     if header is not None:
    # for row in csv_reader:
    # fullFilePath = row[fullPathColNum] # fullPathColNum should point to the col that has the complete path to the file ie  C:\Users\brett\Desktop\myfile.docx
    justName = os.path.splitext(os.path.split(filename)[1])[0]
    itemCount = len(justName.split(embedded_item_character_value))
    result = ''
    if comparator == '=':
        if itemCount == number_of_items_var:
            # outputList.append([filename])
            result = filename
    elif comparator == '>=':
        if itemCount >= number_of_items_var:
            # outputList.append([filename])
            result = filename
    elif comparator == '<=':
        if itemCount <= number_of_items_var:
            # outputList.append([filename])
            result = filename
    return result

    # print(outputList)
    # filesToOpen = [outputCSV]
    # IO_csv_util.list_to_csv(0, outputList, outputCSV, colnum=0)


def numEmbedded(filename, embedded_item_character_value, number_of_items_var, include_exclude_var):
    number_of_items_var = int(number_of_items_var)
    item_lst = filename.split(embedded_item_character_value)
    ext_lst = item_lst[len(item_lst) - 1]
    lst = ext_lst.split(".")
    ext = lst[1]
    result = ""
    if len(item_lst) < number_of_items_var:
        return result
    if include_exclude_var == 1:
        for i in range(number_of_items_var):
            result += item_lst[i]
            result += embedded_item_character_value
    else:
        for i in range(number_of_items_var, len(item_lst)):
            result += item_lst[i]
            result += embedded_item_character_value
    return result[:-1]
