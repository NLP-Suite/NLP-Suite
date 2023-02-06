#written by Roberto Franzosi October 2019
#edited by Cynthia Dong

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"utf8_compliance_util",['os','re','tkinter','chardet'])==False:
    sys.exit(0)

import os
import re
import tkinter as tk
import tkinter.messagebox as mb
import chardet
import IO_csv_util

import IO_files_util
import IO_user_interface_util

# to detect encoding could use chardet (https://pypi.org/project/chardet/)
# pip install chardet
# chardet can detect:
#   ASCII, UTF-8, UTF-16 (2 variants), UTF-32 (4 variants)
#   Big5, GB2312, EUC-TW, HZ-GB-2312, ISO-2022-CN (Traditional and Simplified Chinese)
#   EUC-JP, SHIFT_JIS, CP932, ISO-2022-JP (Japanese)
#   EUC-KR, ISO-2022-KR (Korean)
#   KOI8-R, MacCyrillic, IBM855, IBM866, ISO-8859-5, windows-1251 (Cyrillic)
#   ISO-8859-5, windows-1251 (Bulgarian)
#   ISO-8859-1, windows-1252 (Western European languages)
#   ISO-8859-7, windows-1253 (Greek)
#   ISO-8859-8, windows-1255 (Visual and Logical Hebrew)
#   TIS-620 (Thai)

# Predict a file's encoding using chardet
def predict_encoding(window, inputFilename, inputDir, outputDir, n_lines=20):
    if inputFilename=='' and inputDir!='':
        mb.showwarning(title='Input inputFilename',
                       message="The predict encoding script only works with single files in input, rather than a directory. The input inputFilename is blank.\n\nPlease, select a file and try again.")
        return
    # Open the file as binary data
    with open(inputFilename, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
    encoding=chardet.detect(rawdata)['encoding']
    mb.showwarning(title='Predicted encoding', message=encoding + '\n\nis the predicted encoding, using first ' + str(n_lines) + ' lines, of the file\n\n' + inputFilename )
    return encoding


# https://geek-tips.github.io/articles/494831/index.html
# decoding occurs for each buffered data block,
#   and not for a text string.
#   If you need to detect errors line by line,
#   use the surrogateescape handler and check each read line
#   for the presence of code points in the surrogate range

#'surrogateescape' will represent any invalid bytes as unicode points
#   in the Unicode Private Use Range, ranging from U + DC80 to U + DCFF.
#These private code points will then be returned in the same bytes when the surrogateescape error handler is used to write data. This is useful for processing files in an unknown encoding.

_surrogates = re.compile(r"[\uDC80-\uDCFF]")
#_surrogates = re.compile(r"[\u0080-\u00FF]")
#[\uDC80-\uDCFF]") #the map of unicode private code characters
#0 to 127    "\u0000" to "\u007F"   Basic Latin or U.S. ASCII  "A", "\n", "7", "&"
#128 to 247 "\u0080" to "\u00FF"    Latin 1 supplement Most Latinic alphabets* "ę", "±", "ƌ", "ñ"
#           "\u0080" to "\u07FF"    Latin appended A, Latin appended B
#                                   + Greek, coptyc, cyrrilic, armenian, hebrew, arabic, siriac
# Chinese characters are utf-8

#https://stackoverflow.com/questions/24616678/unicodedecodeerror-in-python-when-reading-a-file-how-to-ignore-the-error-and-ju
#https://docstore.mik.ua/orelly/java/javanut/ch11_02.htm
def detect_decoding_errors_line(l, _s=_surrogates.finditer):
    """Return decoding errors in a line of text
    Works with text lines decoded with the surrogateescape error handler.
    Returns a list of (pos, byte) tuples
    DC80 - DCFF encode bad bytes 80-FF
    """

    return [(m.start(), bytes([ord(m.group()) - 0xDC00]))
            for m in _s(l)]

#https://stackoverflow.com/questions/19771751/how-to-use-unidecode-in-python-3-3
#convert a non utf-8 to the closest ASCII value
#   https://pypi.python.org/pypi/Unidecode
def check_utf8_compliance(window,inputFilename,inputDir,outputDir,openOutputFiles=False,silent=False):
    if len(inputDir)>0:
        silent=True
        inputDocs = [os.path.join(inputDir,f) for f in os.listdir(inputDir) if f[:2]!='~$' and f[-4:]=='.txt']
        outFile= IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'NLP', 'non_utf8')
    elif len(inputFilename)>0:
        inputDocs=[inputFilename]
        outFile= IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'NLP', 'non_utf8')
    else:
        mb.showinfo("Utf-8 compliance","No input inputFilename or directory specified. Routine will exit.")
        return
    if len(inputDocs) == 0:
        mb.showwarning(title='Input error', message='There are no files of type txt in the selected input directory to be checked for utf-8 compliance.\n\nPlease, select a different directory (or file) and try again.')
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                       'Started running utf8 compliance test at',
                                        True, '', True, '', True)

    nonUtf8CompliantNumber=0
    numberOfDocs=len(inputDocs)
    nonUtf8CompliantList=[['Document ID','Document','Line number', 'Line text', 'Non utf-8 Character Position','Non utf-8 Character']]

    for docNum, doc in enumerate(inputDocs):
            docSV=doc
            #try:
            head, tail = os.path.split(doc)
            print("Processing file " + str(docNum+1) + "/" + str(numberOfDocs) + ' ' + tail)
            # IO_util.timed_alert(window,700,'utf-8 compliance ','Processing file ' + str(docNum+1) + " (out of " + str(numberOfDocs) + ")\n\n" + doc,False)
            # https://geek-tips.github.io/articles/494831/index.html
            # 'surrogateescape' will represent any invalid bytes as code points in the Unicode Private Use Range, ranging from U + DC80 to U + DCFF.
            with open(doc, 'r',encoding="utf-8", errors="surrogateescape") as f:
                for i, line in enumerate(f, 1):
                    errors = detect_decoding_errors_line(line)
                    for (col, b) in errors:
                        if docSV==doc:
                            nonUtf8CompliantNumber = nonUtf8CompliantNumber + 1
                            docSV=''
                        nonUtf8CompliantList+=[[docNum,IO_csv_util.dressFilenameForCSVHyperlink(doc),i,line,col,line[col]]]
    #f.close() #does not work
    lengUtf8=len(nonUtf8CompliantList)-1
    if len(nonUtf8CompliantList)>1:
        IO_csv_util.list_to_csv(window,nonUtf8CompliantList,outFile)
        if len(inputDir)==0:
            tk.messagebox.showinfo("Utf-8 compliance","The file\n\n" + doc + "\n\nIS NOT utf-8 compliant.\n\nClick OK to open a csv file with the non utf-8 compliant lines and characters.")
        else:
            tk.messagebox.showinfo("Warning", str(nonUtf8CompliantNumber)+ " files (out of " + str(numberOfDocs) + ") in the directory\n\n" + inputDir + "\n\nare NOT utf-8 compliant.\n\nClick OK to open a csv file with the non utf-8 compliant documents and lines and characters.\n\nApostrophes and quotes are often a cause of non -utf-8 compliance and, when opening a csv file, they will be displayed with weird characters in a Windows machine (not on Mac). Please, read the TIPS file on utf-8 compliance. You may also want to replace automatically all non utf-8 apostrophes and quotes using the script in the Clean files.")
        #always open the output file regardless of the setting of openOutputFiles
        IO_files_util.openFile(window, outFile)
    else:
        if len(inputDir)==0:
            if silent:
                IO_user_interface_util.timed_alert(window, 700, 'utf-8 compliance ', "The file\n\n" + inputFilename + "\n\nis utf-8 compliant.")
            else:
                tk.messagebox.showinfo("Warning","The file\n\n" + inputFilename + "\n\nis utf-8 compliant.")
        else:
            if silent:
                IO_user_interface_util.timed_alert(window, 700, 'utf-8 compliance ', "All " + str(numberOfDocs) + " files in the directory " + inputDir + " are utf-8 compliant.",False,'',True,'',True)
            else:
                tk.messagebox.showinfo("Warning", "All " + str(numberOfDocs) + " files in the directory\n\n" + inputDir + "\n\nare utf-8 compliant.",False,'',True,'',True)

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running utf-8 compliance test at', True, '', True, startTime, True)


def check_empty_file(inputFilename, inputDir):
    # collecting input txt files
    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt')
    nDocs = len(inputDocs)
    docID = 0
    if nDocs == 0:
        return

    # DOCUMENTS WITH FULL STOPS ADDED
    count = 0
    docID = 0

    emptyFiles = 0
    for filename in inputDocs:
        docID = docID + 1
        _, tail = os.path.split(filename)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        edited = False
        with open(filename, 'r', encoding='utf-8', errors='ignore') as myfile:
            # read file into string
            fulltext = myfile.read()
            # end method if file is empty
            if len(fulltext) < 1:
                emptyFiles = emptyFiles + 1
                # mb.showerror(title='File empty',
                #              message='The file ' + filename + ' is empty.')
                print('   Empty file', tail)
            myfile.close()
    if nDocs==1:
        if emptyFiles == 0:
            msg='The file "' + tail + '" is not empty'
        else:
            msg = 'The file "' + tail + '" is empty'
    else:
        if emptyFiles == 0:
            msg = 'There are no empty files in the directory\n\n'+inputDir
        else:
            if emptyFiles == 1:
                msg = '1 file is empty in the directory\n\n' + inputDir + '\n\nPlease, check the command line/prompt searching for the word "empty."'
            else:
                msg = str(emptyFiles) + 'files are empty in the directory\n\n' + inputDir + '\n\nPlease, check the command line/prompt searching for the word "empty."'
    mb.showerror(title='File empty',
                         message=msg)
    return
