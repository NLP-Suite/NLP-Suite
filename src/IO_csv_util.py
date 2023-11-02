import sys
import GUI_util
# import IO_libraries_util
#
# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "IO_csv_util",
# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "IO_csv_util",
# 								['os', 'tkinter','csv','pandas']) == False:
# 	sys.exit(0)

import csv
import tkinter.messagebox as mb
import pandas as pd
import os
import IO_files_util
import IO_user_interface_util

#if any column header contains just numbers the function will return FALSE
def csvFile_has_header(file_path):
    is_header=False
    if not os.path.exists(file_path):
        return is_header
    reader = csv.reader(open(file_path, "r",encoding='utf-8',errors='ignore'))
    i = next(reader)
    is_header = not any(cell.isdigit() for cell in i)
    return is_header

# Take in file name, output is a list of rows each with columns 1->11 in the conll table
# Used to divide sentences etc.
def get_csv_data(inputFilename,withHeader):
    data=[]
    headers=''
    delimiter=','
    filename, file_extension = os.path.splitext(inputFilename)
    # file_extension will return any extension .xlsx, .csv, …
    if filename=='' or file_extension!='.csv':
        mb.showwarning(title='File type error', message='The file\n\n' + inputFilename + '\n\nis not an expected csv file. Please, check the file and try again.')
        return data, headers
    #numColumns=get_csvfile_numberofColumns(file_name)
    withHeader=csvFile_has_header(inputFilename)
    #print("io IO delimiter ",get_csvfile_numberofColumns(file_name))
    #TODO does not work; gives an error
    #print ("\n\n\n\ndetectCsvHeader(file_name) ",detectCsvHeader(file_name))
    with open(inputFilename,encoding='utf-8-sig',errors='ignore') as f:
        reader = csv.reader(f,delimiter=delimiter)
        if withHeader == True:
            headers = next(reader, None) #ADDED to skip header in new .csv CoNLL
        #data = [r[:numColumns] for r in reader]
        data = [r for r in reader]
        #f.close()
    if len(data)==0:
        mb.showwarning(title='Empty csv file', message='The csv file\n\n' + inputFilename + '\n\nis empty. Please, check the file and try again.')
    return data, headers

# csv file contains headers,
#   then the first row will be headers
def get_csvfile_headers (csvFile,ask_Question=False):
    headers = ''
    answer = True
    if not os.path.isfile(csvFile):
        mb.showwarning("Warning", "The csv file " + csvFile + " does not exist.")
        return headers
    if ask_Question:
        answer=mb.askyesno("File headers","Does the selected input file\n\n"+csvFile+"\n\nhave headers?")
    if csvFile!='' and answer ==True:
        with open(csvFile,'r',encoding="utf-8-sig",errors='ignore') as f:
            reader = csv.DictReader(f)
            try:
                headers=reader.fieldnames
            except IOError as e: # empty files will break the next
                mb.showwarning("Warning","Opening the csv file " + csvFile + " encountered an error.\n\n" + str(e))
                headers=''
            # f.seek(0)
    return headers

def get_csvfile_headers_pandas(inputFilename):
    # index_col = 0 excludes the first column, an ID column; but... we need that column
    # headers = pd.read_csv(inputFilename, index_col=0, nrows=0).columns.tolist()
    try:
        headers = pd.read_csv(inputFilename, nrows=0, encoding='utf-8',on_bad_lines='skip').columns.tolist()
    except:
        headers=[]
    return headers

# convert header alphabetic value for CSV files with or without headers to its numeric column value
# column numbers start at 0
def get_columnNumber_from_headerValue(headers,header_value, inputFilename):
    column_number = None
    for i in range(len(headers)):
        if header_value == headers[i]:
            column_number = i
            if column_number == None:
                IO_user_interface_util.timed_alert(GUI_util.window, 1000, 'Wrong header value',
                                                   'csv filename: ' + inputFilename + '\n  Header values "' + str(
                                                       header_value) + '" not found among file headers ' + str(headers),
                                                   False, '', True)
                break
    return column_number

# convert header alphabetic value for CSV files with or without headers to its numeric column value
# column numbers start at 0
def get_headerValue_from_columnNumber(headers,column_number=0):
    for i in range(len(headers)):
        if i==column_number:
            header_value= headers[i]
            column_number = i
            return header_value

# the function extracts all the UNIQUE values in a column of a csv file
# the function is used, for instance, to create the values of a dropdown menu
#   for an example, see annotator_GUI.py
#   column_name is the string header
# returns a sorted list of DISTINCT values or a string of comma-separated values (to be used, for instance, for a wordcloud)
# since a set contains only unique values, it cannot be used as such to construct wordclouds images
def get_csv_field_values(inputFilename, column_name, uniqueValues=True, returnList=True):
    if uniqueValues:
        unique_values = set()
    else:
        unique_values = ''
    if inputFilename == '' or column_name == '':
        return ['']

    with open(inputFilename, 'r', encoding="utf-8", errors='ignore') as f:
        csvreader = csv.reader(f)
        fields = next(csvreader)
        # from the column header get the column number that we want to extract
        col_num = get_columnNumber_from_headerValue(fields, column_name, inputFilename)
        if col_num==None:
            return ['']
        for row in csvreader:
            if uniqueValues:
                unique_values.add(row[col_num])
                # convert set to list; to obtain a string of values simply str(sorted_unique_values)
                # the list is sorted with proper names, with capital initial first, then the improper names
                sorted_unique_values = sorted(unique_values)
                list(sorted_unique_values)
            else:
                unique_values = row[col_num] + ', ' + unique_values
    return unique_values

# get the number of records and columns of a csv file
def GetNumberOf_Records_Columns_inCSVFile(inputFilename,encodingValue='utf-8'):
    nRecords=0
    nColumns=0
    try:
        maxnum = pd.read_csv(inputFilename, encoding=encodingValue,on_bad_lines='skip').shape
    except:
        return nRecords, nColumns
    return maxnum # tuple with first value number of records, second value number of columns

# inputFile has path
def GetMaxValueInCSVField(inputFilename,algorithm='',columnHeader='Document ID',encodingValue='utf-8'):
    maxvalue = 0
    df = pd.read_csv(inputFilename,encoding='utf-8',on_bad_lines='skip')
    try:
        column = df[columnHeader]
    except:
        if algorithm != '':
            msg = "\n\nThe '" + algorithm + "' algorithm requires in input a csv file with a '" + columnHeader + "' column."
        mb.showwarning(title='csv file error',
                       message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + columnHeader + msg + "\n\nPlease, select a different csv file in input and try again!")
        return 0
    maxvalue = column.max()
    if maxvalue=='': # to avoid an error
        maxvalue = 0
    return maxvalue


# triggered by a df.to_csv
# headers is a list []
def df_to_csv(window,data_frame, outputFilename, headers=None, index=False, language_encoding='utf-8'):
    while True: # repeat until file is closed
        try:
            # when the dataframe already includes headers (e.g., in all CoNLL table analyzer functions)
            #   you do not want to add a header then header=None;
            #   however, if you pass a header, then you cannot have header=None or a header will never be saved
            if headers!=None:
                data_frame.to_csv(outputFilename, columns=headers, index=False, encoding=language_encoding)
            else:
                data_frame = data_frame.applymap(
                    lambda x: x.encode('utf-8', 'replace').decode('utf-8') if isinstance(x, str) else x)
                data_frame.to_csv(outputFilename, columns=headers, header=None, index=False, encoding=language_encoding)
            break # exit loop
        except IOError as e:
            # mb.showwarning(title='Output file error', message="Could not write the file " + outputFilename + "\n\nA file with the same name is already open. Please, close the Excel file and then click OK to resume.")
            mb.showwarning(title='Output file error', message="Could not write the file " +
                                outputFilename + "\n\n"+str(e) + "\n\nCLOSE THE FILE TO EXIT LOOP...")
            if not "Permission" in str(e):
                outputFilename = ''
                break  # exit loop; the error is not due to file being open
            # restart the loop
    return outputFilename

# list_output has the following type format [['PRONOUN ANALYSIS','FREQUENCY'], ['PRP', 105], ['PRP$', 11], ['WP', 5], ['WP$', 0]]
# outputFilename is the name of the outputfile with path
# returns True when an error is found

# TODO this is a quick way to still use the old-fashioned way of saving a csv fle
def list_to_csv(window,list_output,outputFilename,colnum=0, encoding='utf-8'):
    error = False
    if not isinstance(list_output, list):
        return True
    #if a specific column number is given, generate only the colnum columns as output
    if colnum!=0:
        list_output = [i[:colnum] for i in list_output]
# convert list to dataframe
    df = pd.DataFrame(list_output)
    df_to_csv(GUI_util.window, df, outputFilename)
    return error


def openCSVOutputFile(outputCSVFilename, IO='w', encoding='utf-8',errors='ignore', newline=''):
# https://stackoverflow.com/questions/29347790/difference-between-ioerror-and-oserror#:~:text=There%27s%20no%20difference%20between%20IOError,a%20file%20or%20removing%20one.
# There's no difference between IOError and OSError cause they mostly appear on similar commands like opening a file or removing one.
    try:
        with open(outputCSVFilename,'w', encoding='utf-8', errors='ignore') as csvfile:
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
                           message="Could not write the file " + outputCSVFilename + "\n\nThe following error occurred while opening the file in output:\n\n" + str(e) + "\n\nPlease, close the csv file and try again!")
        return True


def extract_from_csv(inputFilename, outputDir, data_files, columns_to_export=None):
    import IO_files_util
    # TODO must check for data_files passed
    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv',
                                                             'extract',
                                                             '', '', '', '', False, True)

    df = pd.DataFrame(pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip'))
    # TODO must extract columns by specific values passed
    df.to_csv(outputFilename, encoding='utf-8', columns=columns_to_export, index=False)
    return outputFilename


# convert an xlsx file to csv
def convert_Excel_to_csv(inputFilename,outputDir, headers=None):
    # importing pandas as pd
    # Read and store content of an excel file
    read_file = pd.read_excel(inputFilename)

    # Write the dataframe object
    # into csv file
    outputFilename=outputDir + os.sep + "Test.csv"
    read_file.to_csv(outputFilename, encoding='utf-8', index=None, header=True)

    # read csv file and convert into a dataframe object
    df = pd.DataFrame(pd.read_csv(outputFilename, encoding='utf-8', on_bad_lines='skip'))
    df.to_csv(outputFilename, encoding='utf-8', columns=headers, index=False)
    return outputFilename

    # show the dataframe

# sort a csv file by a set of columns
# headers_tobe_sorted is a list of type ['Document ID','Sentence ID']
def sort_csvFile_by_columns(inputFilename, outputFilename, headers_tobe_sorted):
    df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    df = df.sort_values(by=headers_tobe_sorted)
    df.to_csv(outputFilename,encoding='utf-8', index=False)

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

# the function takes a string (i.e., a filename) and removes the hyperlinks
def undressFilenameForCSVHyperlink(fileName):
    try:
        fileName=fileName.replace('=hyperlink("','')
    except:
        return fileName
    fileName=fileName.replace('")','')
    return fileName

# given a csv file containing a document field with filenames with hyperlinks,
#   the function will remove the hyperlinks from every col & row
def remove_hyperlinks(inputFilename):
    try:
        data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except pd.errors.ParserError:
        data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip', sep='delimiter')
    except:
        print("Error: failed to read the csv file named: "+inputFilename)
        return False, ''
    # data = pd.read_csv(inputFilename)
    try:
        document = data['Document']
    except:
        no_hyperlink_filename=inputFilename
        return True, no_hyperlink_filename
    new_document = []
    for i in document:
        try:
            new_document.append(IO_files_util.getFilename(i)[2]) #0 for tail; 2 for full path
        except:
            continue
    data['Document'] = new_document
    no_hyperlink_filename = os.path.join(os.path.split(inputFilename)[0],os.path.split(inputFilename)[1])[:-4] +"_no_hyperlinks.csv"
    data.to_csv(no_hyperlink_filename, encoding='utf-8',index=0)
    return True, no_hyperlink_filename

# If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location' in GIS files
# header1 is old header, header2 is new header
# returns True if header is changed successfully; otherwise false
def rename_header(inputFilename, header1, header2):
    headerFound=False
    if not inputFilename.endswith('.csv'):
        mb.showwarning(title="File type error", message='The file\n\n' + inputFilename + "\n\is not an expected csv file with headers.\n\nPlease, check the file and try again.")
        return headerFound
    headers = get_csvfile_headers(inputFilename)
    for header in headers:
        if header2 == header:  # the file already contains the header2
            headerFound = True
            return headerFound
        if header1 == header:
            ID=get_columnNumber_from_headerValue(headers, header1, inputFilename)
            # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
            temp = pd.read_csv(inputFilename,encoding='utf-8',on_bad_lines='skip')
            if temp.columns[ID] == header1:
                temp = temp.rename(columns={header1: header2})
                temp.to_csv(inputFilename, encoding='utf-8', index=False)
                headerFound = True
                break
    if headerFound==False:
        mb.showwarning(title="File type error", message='The file\n\n' + inputFilename + "\n\ndoes not contain a header '" + header1 + "' to be renamed to '" + header2 + "'.\n\nPlease, check the file and try again.")
    return headerFound


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
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w", encoding='utf-8', errors='ignore') as text_file:
            text_file.write(text)

    elif len(column_list) == 0:
        df = pd.read_csv(inputFilename,encoding='utf-8',on_bad_lines='skip')
        if not column in df.columns:
            mb.showwarning(title='csv file error',
                           message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + column)
            return

        a = list(df[column])
        # converting list into string and then joining it with space
        text = '\n'.join(str(e) for e in a)
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w", encoding='utf-8', errors='ignore') as text_file:
            text_file.write(text)
    else:
        df = pd.read_csv(inputFilename,encoding='utf-8',on_bad_lines='skip')

        for column in column_list:
            if not column in df.columns:
                mb.showwarning(title='csv file error',
                               message="The selected csv file\n\n" + inputFilename + "\n\ndoes not contain the column header\n\n" + column)
                return

        text = df[column_list].to_csv(encoding='utf-8', index=False)
        # replacing ',' by space
        text = text.replace(",", " ")
        with open(outputDir + '/' + os.path.basename(inputFilename) + '.txt', "w", encoding='utf-8', errors='ignore') as text_file:
            text_file.write(text)

def df_to_list_w_header(df):
    res = []
    header = list(df.columns)
    res.append(header)
    for index, row in df.iterrows():
        temp = [row[tag] for tag in header]
        res.append(temp)
    return res


def df_to_list(df):
    res = []
    header = list(df.columns)
    for index, row in df.iterrows():
        temp = [row[tag] for tag in header]
        res.append(temp)
    return res


def list_to_df(tag_list):
    header = tag_list[0]
    df = pd.DataFrame(tag_list[1:], columns=header)
    return df


def header_check(inputFile):
    sentenceID_pos=''
    docID_pos=''
    docName_pos=''

    if isinstance(inputFile, pd.DataFrame):
        header = list(inputFile.columns)
    else:
        header = get_csvfile_headers(inputFile)
    if 'Sentence ID' in header:
        sentenceID_pos = header.index('Sentence ID')
    else:
        pass

    if 'Document ID' in header:
        docID_pos = header.index('Document ID')
    else:
        pass

    if 'Document' in header:
        docName_pos = header.index('Document')
    else:
        pass
    return sentenceID_pos, docID_pos, docName_pos, header


def sort_by_column(input, column):
    if isinstance(input, pd.DataFrame):
        df = input
    else:
        df = pd.read_csv(input,encoding='utf-8',on_bad_lines='skip')
    col_list = set(df[column].tolist())
    df_list = [df[df[column] == value] for value in col_list]
    return df_list


def align_dataframes(df_list):
    max = 0
    for df in df_list:
        header = list(df.columns)
        if 'Sentence ID' in header:
            sentenceID = 'Sentence ID'
        if df[sentenceID].max() > max:
            max = df[sentenceID].max()
    new_list = []
    for df in df_list:
        if df.empty:
            continue
        temp = df.iloc[-1,:]
        if temp[sentenceID] != max:
            # TODO solve warning issue
            # https://www.dataquest.io/blog/settingwithcopywarning/
            # ​​​​SettingwithCopyWarning
            temp[sentenceID] = max
            temp['Frequency'] = 0
            new_df = df.append(temp,ignore_index=True)
        else:
            new_df = df
        new_list.append(new_df)

    df_list = [add_missing_IDs(data) for data in new_list if not data.empty]
    return df_list


def slicing_dataframe(df,columns):
    df = df[columns]
    return df


def rename_df(df,col):
    for index, row in df.iterrows():
        if row[col] != '':
            name = row[col]
            break
    df.rename(columns={"Frequency": name + " Frequency"},inplace=True)
    df = df.drop(columns=[col])
    return df

#sortOrder = True (descending 3, 2, 1)
#sortOrder = False (ascending 1, 2, 3)
def sort_data (ExcelChartData, sortColumn,sortOrder):
    sorted_data = sorted(ExcelChartData, key=lambda tup:tup[sortColumn],reverse=sortOrder)
    return sorted_data
