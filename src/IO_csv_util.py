import sys
import GUI_util
# import IO_libraries_util
#
# if IO_libraries_util.install_all_packages(GUI_util.window, "IO_csv_util",
# 								['os', 'tkinter','csv','pandas']) == False:
# 	sys.exit(0)

import csv
import tkinter.messagebox as mb
import pandas as pd
import os
import stat


#if any column header contains just numbers the function will return FALSE
def csvFile_has_header(file_path):
    is_header=False
    if file_path=='':
        return is_header
    reader = csv.reader(open(file_path, "r",encoding='utf-8',errors='ignore'))
    i = next(reader)
    is_header = not any(cell.isdigit() for cell in i)
    return is_header

# Take in file name, output is a list of rows each with columns 1->11 in the conll table
# Used to divide sentences etc.
def get_csv_data(file_name,withHeader):
    data=[]
    headers=''
    delimiter=','
    filename, file_extension = os.path.splitext(file_name)
    # file_extension will return any extension .xlsx, .csv, …
    if file_name=='' or file_extension!='.csv':
        mb.showwarning(title='File type error', message='The file\n\n' + file_name + '\n\nis not an expected csv file. Please, check the file and try again.')
        return data, headers
    #numColumns=get_csvfile_numberofColumns(file_name)
    withHeader=csvFile_has_header(file_name)
    #print("io IO delimiter ",get_csvfile_numberofColumns(file_name))
    #TODO does not work; gives an error
    #print ("\n\n\n\ndetectCsvHeader(file_name) ",detectCsvHeader(file_name))
    with open(file_name,encoding='utf-8',errors='ignore') as f:
        reader = csv.reader(f,delimiter=delimiter)
        if withHeader == True:
            headers = next(reader, None) #ADDED to skip header in new .csv CoNLL
        #data = [r[:numColumns] for r in reader]
        data = [r for r in reader]
        #f.close()
    if len(data)==0:
        mb.showwarning(title='Empty csv file', message='The csv file\n\n' + file_name + '\n\nis empty. Please, check the file and try again.')
    return data, headers

# csv file contains headers,
#   then the first row will be headers
def get_csvfile_headers (csvFile,ask_Question=False):
    headers=''
    answer=True
    if ask_Question:
        answer=mb.askyesno("File headers","Does the selected input file\n\n"+csvFile+"\n\nhave headers?")
    if csvFile!='' and answer ==True:
        with open(csvFile,'r',encoding="utf-8",errors='ignore') as f:
            reader = csv.reader(f)
            try:
                headers=next(reader)
            except: # empty files will break the next
                # mb.showwarning("Warning","The selected csv file has no records.\n\nPlease, check the file content and select a different file.")
                # headers=''
                return headers
            f.seek(0)
    return headers

# convert header alphabetic value for CSV files with or without headers to its numeric column value
# column numbers start at 0
def get_columnNumber_from_headerValue(headers,header_value):
    column_number = 0
    for i in range(len(headers)):
        if header_value == headers[i]:
            column_number = i
            return column_number

# convert header alphabetic value for CSV files with or without headers to its numeric column value
# column numbers start at 0
def get_headerValue_fromcolumnNumber(headers,column_number=0):
    for i in range(len(headers)):
        if i==column_number:
            header_value= headers[i]
            column_number = i
            return header_value

# the function extracts all the UNIQUE values in a column of a csv file
# the function is used, for instance, to create the values of a dropdown menu
#   for an example, see annotator_GUI.py
#   column_name is the header
def get_csv_field_values(inputfile_name, column_name):
    unique_values = set()
    if inputfile_name == '' or column_name == '':
        return ['']

    with open(inputfile_name, 'r', encoding="utf-8", errors='ignore') as f:
        csvreader = csv.reader(f)
        fields = next(csvreader)
        # from the column header get the column number that we want to extract
        col_num = get_columnNumber_from_headerValue(fields, column_name)
        for row in csvreader:
            unique_values.add(row[col_num])
        sorted_unique_values=sorted(unique_values)
        # convert set to list; to obtain a string of values simply str(sorted_unique_values)
        # the list is sorted with proper names, with capital initial first, then the improper names
    return list(sorted_unique_values)

# get the number of columns of a csv file
def get_csvfile_numberofColumns (csvFile):
    countColumns=0
    if csvFile!='':
        with open(csvFile,'r',encoding="utf-8",errors='ignore') as f:
            reader = csv.reader(f)
            try:
                first_row=next(reader)
            except:
                mb.showwarning(title='Warning', message='The csv file\n\n' + str(csvFile) + '\n\nis empty.')
                return
            countColumns = len(first_row)
            f.seek(0)
    return countColumns


# inputFile has path
def GetNumberOfDocumentsInCSVfile(inputFilename,algorithm,columnHeader='Document ID',encodingValue='utf-8'):
    with open(inputFilename,encoding=encodingValue,errors='ignore') as f:
        reader = csv.reader(f)
        next(reader) # skip header row
        headers=get_csvfile_headers(inputFilename)
        if not columnHeader in str(headers):
            mb.showwarning(title='csv file error',
                           message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + columnHeader + "\n\nThe '" + algorithm + "' algorithm requires in input a csv file with a \'Document ID\' column.\n\nPlease, select a different csv file in input and try again!")
            return 0
        columnNumber=get_columnNumber_from_headerValue(headers,columnHeader)

        val_list = list()
        for column in reader:
            try:
                val_list.append(int(float(column[columnNumber].replace(',', ''))))
            except:
                pass
        maxnum = max(val_list)
        # the following line would break in the presence of a blank field in column
        # maxnum = max(int(column[columnNumber].replace(',', '')) for column in reader)
        f.close()
    return maxnum

def GetNumberOfRecordInCSVFile(inputFilename,encodingValue='utf-8'):
    with open(inputFilename,'r',encoding=encodingValue,errors='ignore') as f:
        return sum(1 for line in f)

# list_output has the following type format [['PRONOUN ANALYSIS','FREQUENCY'], ['PRP', 105], ['PRP$', 11], ['WP', 5], ['WP$', 0]]
# path_output is the name of the outputfile with path
# returns True when an error is found
def list_to_csv(window,list_output,path_output,colnum=0):
    if list_output==None:
        return True
    try:
        #if a specific column number is given, generate only the colnum columns as output
        if colnum!=0:
            list_output = [i[:colnum] for i in list_output]
        #when writing a csv file newline='' prevents writing an extra blank line after every record
        #bad non utf-8 characters may be exported in lines when checking for non utf-8 characters
        with open(path_output,'w',newline='', encoding='utf-8',errors='surrogateescape') as csvFile:
        # with open(path_output,'w',newline='', encoding='utf-8',errors='ignore') as csvFile: #bad non utf-8 characters may be exported in lines when checking for non utf-8 characters
            writer = csv.writer(csvFile)
            # saving the case of a single list, for example
            # ['inheriting', 'instilled', 'interacting', 'looked', 'loved', 'nyc', 'paused', 'seemed']
            if isinstance(list_output[0], list):
                # case of list of list, for example
                # [['PRONOUN ANALYSIS','FREQUENCY'], ['PRP', 105],...]
                writer.writerows(list_output)
            else:
                current = list_output
                for item in current:
                    writer.writerow([item])
        csvFile.close()
        return False
    except OSError as e:
        if 'Invalid argument' in str(e):
            mb.showwarning(title='Output file error',
                           message="Could not write the file\n\n" + path_output + "\n\nThe filename contains an invalid argument. Please, check the filename and try again!")
        elif 'Permission denied' in str(e):
            mb.showwarning(title='Output file error', message="Could not write the file " + path_output + "\n\nA file with the same name is already open. Please, close the csv file and try again!")
        else:
            mb.showwarning(title='Output file error',
                           message="Could not write the file " + path_output + "\n\nThe following error occurred while opening the file in output:\n\n" + str(e) + "\n\nPlease, close the Excel file and try again!")
        return True

def openCSVOutputFile(outputCSVFilename, IO='w', encoding='utf-8',errors='ignore', newline=''):

    try:
        with open(outputCSVFilename,'w') as csvfile:
            csvfile.close()
            return False
    except OSError as e:
        if 'Invalid argument' in str(e):
            mb.showwarning(title='Output file error',
                           message="Could not write the file\n\n" + outputCSVFilename + "\n\nThe filename contains an invalid argument. Please, check the filename and try again!")
        elif 'Permission denied' in str(e):
            mb.showwarning(title='Output file error', message="Could not write the file " + outputCSVFilename + "\n\nA file with the same name is already open. Please, close the csv file and try again!")
        else:
            mb.showwarning(title='Output file error',
                           message="Could not write the file " + outputCSVFilename + "\n\nThe following error occurred while opening the file in output:\n\n" + str(e) + "\n\nPlease, close the Excel file and try again!")
        return True

# triggered by a df.to_csv
def df_to_csv(window,data_frame, outputFilename, headers=None, index=False):
    try:
        data_frame.to_csv(outputFilename, columns=headers, index=False)
        return outputFilename
    except IOError:
        mb.showwarning(title='Output file error', message="Could not write the file " + outputFilename + "\n\nA file with the same name is already open. Please, close the Excel file and try again!")
        return ''


def extract_from_csv(inputFilename, outputDir, data_files, columns_to_exported=None):
    import IO_files_util
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                             'extract',
                                                             '', '', '', '', False, True)

    df = pd.DataFrame(pd.read_csv(inputFilename))
    df.to_csv(outputFilename, columns=columns_to_exported, index=False)
    return outputFilename


# convert an xlsx file to csv
def convert_Excel_to_csv(inputFilename,outputDir, headers=None):
    # importing pandas as pd
    # Read and store content of an excel file
    read_file = pd.read_excel(inputFilename)

    # Write the dataframe object
    # into csv file
    outputFilename=outputDir + os.sep + "Test.csv"
    read_file.to_csv(outputFilename,
                     index=None,
                     header=True)

    # read csv file and convert into a dataframe object
    df = pd.DataFrame(pd.read_csv(outputFilename))
    df.to_csv(outputFilename, columns=headers, index=False)
    return outputFilename

    # show the dataframe

# sort a csv file by a set of columns
# headers_tobe_sorted is a list of type ['Document ID','Sort order']
def sort_csvFile_by_columns(inputFilename, outputFilename, headers_tobe_sorted):
    df = pd.read_csv(inputFilename)
    df = df.sort_values(by=headers_tobe_sorted)
    df.to_csv(outputFilename)

# the function dresses a filename as an hyperlink
#   to be used in a csv file;
#   when you click on the hyperlink from the csv file, the file will open
# fileName can be a filename + path
# fileName can also be a full path with NO filename
# e.g., =HYPERLINK("C:\Users\Desktop\CORPUS DATA\Sample text\Atlanta Constitution_02-09-1888_2.txt")
# hyperlinks have a maximum length of 255 characters
def dressFilenameForCSVHyperlink(fileName):
    tempFileName='=hyperlink("'+str(fileName)+'")'
    if len(tempFileName)<=255:
        fileName=tempFileName
    return fileName

def undressFilenameForCSVHyperlink(fileName):
    fileName=fileName.replace('=hyperlink("','')
    fileName=fileName.replace('")','')
    return fileName


# If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location' in GIS files
def rename_header(inputFilename, header1, header2):
    headerFound=False
    if not inputFilename.endswith('.csv'):
        return True
    headers = get_csvfile_headers(inputFilename)
    # temp=None
    for header in headers:
        if header2 == header:  # the file already contains the header2
            return True
        if header1 == header:
            ID=get_columnNumber_from_headerValue(headers, header1)
            # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
            temp = pd.read_csv(inputFilename)
            if temp.columns[ID] == header1:
                temp = temp.rename(columns={header1: header2})
                temp.to_csv(inputFilename, index=False)
                headerFound = True
                break
    if headerFound==False:
        mb.showwarning(title="File type error", message='The file\n\n' + inputFilename + "\n\ndoes not contain a header '" + header1 + "' to be converted to '" + header2 + "'.\n\nPlease, check the file and try again.")
    return temp


def export_csv_to_text(inputFilename, outputDir, column=None, column_list=[]):
    filename, file_extension = os.path.splitext(inputFilename)

    if inputFilename == '' or file_extension != '.csv':
        mb.showwarning(title='File type error',
                       message='The file\n\n' + inputFilename + '\n\nis not an expected csv file. Please, check the file and try again.')
        return
    if column != None and len(column_list) != 0:
        mb.showwarning(title='Field(s) input error',
                       message='Cannot have field and field_list as filter at the same time.\n\nPlease, select one and try again.')
        return
    if column == None and len(column_list) == 0:

        # reading csv file
        text = open(inputFilename, "r", encoding="utf-8", errors='ignore')

        # joining with space content of text
        text = ' '.join([i for i in text])
        # replacing ',' by space
        text = text.replace(",", " ")
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w") as text_file:
            text_file.write(text)

    elif len(column_list) == 0:
        df = pd.read_csv(inputFilename)
        if not column in df.columns:
            mb.showwarning(title='csv file error',
                           message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + column)
            return

        a = list(df[column])
        # converting list into string and then joining it with space
        text = '\n'.join(str(e) for e in a)
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w") as text_file:
            text_file.write(text)
    else:
        df = pd.read_csv(inputFilename)

        for column in column_list:
            if not column in df.columns:
                mb.showwarning(title='csv file error',
                               message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + column)
                return

        text = df[column_list].to_csv(index=False)
        # replacing ',' by space
        text = text.replace(",", " ")
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w") as text_file:
            text_file.write(text)
