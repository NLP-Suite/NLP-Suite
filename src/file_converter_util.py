# Written by Roberto Franzosi November 2019
# edited by Cynthia Dong
# The script includes several types of document converters:
#   pdf --> txt
#   docx --> txt
#   tsv --> csv
#   csv --> txt

import sys

import GUI_IO_util
import IO_files_util
import GUI_util
import IO_libraries_util
import IO_user_interface_util

# pypdf is deliberately NOT in this list. This gate is a FATAL ERROR that exits the Suite, and it
# runs at module import, i.e. for EVERY converter (csv, docx, rtf, pdf --> txt). pypdf is only
# needed by the pdf --> docx option, is a recent addition, and an installation that predates it
# must not be locked out of the other converters; pdf_to_docx_converter checks for it on its own.
if IO_libraries_util.install_all_Python_packages(GUI_util.window,"file_converter_util",['os','__main__','tkinter','docx','pdfminer','striprtf','errno'])==False:
    sys.exit(0)

import os
import io

import csv
import tkinter as tk
import tkinter.messagebox as mb
import errno
# pip install pdfminer.six --user (since it may ask for permission) rather than pip install pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTFigure, LTImage, LTTextContainer
from docx import Document #pip install python-docx
from docx.shared import Inches, Pt
from os.path import splitext
from striprtf.striprtf import rtf_to_text

# https://pdfminersix.readthedocs.io/en/latest/
# https://pypi.org/project/pdfminer/#description
# https://towardsdatascience.com/pdf-preprocessing-with-python-19829752af9f

# pdf helper functions, shared by the pdf --> txt and pdf --> docx converters
# ______________________________________________________________________________________________

# collect the pdf files to be converted, either a single input file or a whole input directory
# returns an EMPTY list when there is nothing to convert; the caller has already been warned
def get_pdf_file_list(window, inputFilename, inputDir):
    # '.PDF' files used to be dropped SILENTLY by a case-sensitive f[-4:]=='.pdf' test
    def is_pdf(f):
        return not os.path.basename(f).startswith('~$') and f.lower().endswith('.pdf')

    if len(inputDir) > 0:
        msgbox_subDir = tk.messagebox.askyesnocancel("Process sub-directories", "Do you want to process for files in subdirectories?")
        if msgbox_subDir is None:  # CANCEL
            return []
        if msgbox_subDir:
            inputDocs = IO_files_util.getFileList_SubDir(inputFilename, inputDir, '.pdf')
            inputDocs = [f for f in inputDocs if is_pdf(f)]
        else:
            inputDocs = [os.path.join(inputDir, f) for f in os.listdir(inputDir) if is_pdf(f)]
    elif len(inputFilename) > 0:
        if is_pdf(inputFilename):
            inputDocs = [inputFilename]
        else:
            tk.messagebox.showinfo("pdf converter", "The input file " + inputFilename + " is not of type pdf.\n\nPlease, select a pdf type file (or directory) for input and try again.")
            return []
    else:
        tk.messagebox.showinfo("pdf converter", "No input filename or directory specified.\n\nPlease, select a pdf type file or directory for input and try again.")
        return []
    if len(inputDocs) == 0:
        tk.messagebox.showinfo("Warning", "There are no pdf files in the input directory.\n\nPlease, select a different directory (or pdf type file) for input and try again.")
    return inputDocs

# build the output path for doc, mirroring the sub-directory it sits in under inputDir.
# os.path.commonprefix, used here before, compares STRINGS and not paths: with inputDir
# 'C:/data/corpus' and a doc in 'C:/data/corpus2', the common prefix came out as 'C:/data/corpus'
# and os.path.relpath then returned '..\corpus2\a.pdf', writing the converted file OUTSIDE the
# output directory the user selected. Taking relpath against inputDir itself is both correct and
# simpler; anything not actually under inputDir falls back to a flat basename.
def get_converted_output_path(doc, inputDir, outputDir, extension='.txt'):
    relativePath = os.path.basename(doc)
    if inputDir:
        try:
            candidate = os.path.relpath(doc, inputDir)
            # '..' means doc is NOT under inputDir; os.pardir would escape outputDir
            if not candidate.startswith(os.pardir):
                relativePath = candidate
        except ValueError:
            # Windows: doc and inputDir on different drives
            pass
    return os.path.join(outputDir, os.path.splitext(relativePath)[0] + extension)

def make_output_directory(outputFilename):
    directory = os.path.dirname(outputFilename)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

# extract the text of ONE pdf with pdfminer.
# retstr.getvalue() used to be called inside the page loop, which re-materialized the whole
# accumulated buffer on EVERY page (quadratic: a 500-page book copied ~250 times more text than it
# needed) and left 'data' undefined - a NameError - for a pdf with no extractable page.
def extract_pdf_text(doc):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=LAParams())
    try:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        with open(doc, 'rb') as fp:
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
    finally:
        device.close()  # flush the converter; it was never closed before
    data = retstr.getvalue()
    retstr.close()
    return data

# inputFilename contains full path
def pdf_converter(window,inputFilename, inputDir, outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):

    inputDocs = get_pdf_file_list(window, inputFilename, inputDir)
    if len(inputDocs) == 0:
        return

    mb.showwarning(title='Warning', message='The Python pdf to text converter used here (pdfminer) is UNLIKELY to covert successfully multiple-column, full-page newspaper articles, with multiple headings and pictures. pdfminer CAN convert multiple-column documents with a simpler layout (e.g., journal articles) and does very well with full-page books/documents.\n\nAny image embedded in the pdf file is LOST in the txt output. Use the "Document converter (pdf --> docx)" option to keep text AND images in a single document.\n\nFor more information on what pdfminer can do, see https://pdfminer-docs.readthedocs.io/programming.html.\n\nPLEASE, MAKE SURE TO CHECK THE CONVERTED OUTPUT FILE. IF YOU PLAN TO PARSE THE TXT OUTPUT VIA STANFORD CORENLP, YOU SHOULD CONSIDER CLEANING YOUR OUTPUT FROM COPYRIGHT MATERIAL AND BIBLIOGRAPHICAL REFERENCES, SINCE SUCH TEXTUAL ELEMENTS DO NOT HAVE COMPLETE SENTENCES.')

    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running pdf to txt converter at',
                                                   True, '', True, '', False)
    if inputDir == "":
        inputDir = os.path.dirname(inputFilename)

    numberOfDocs = len(inputDocs)
    outputFilename = ''
    convertedDocs = 0
    failedDocs = []
    for docNum, doc in enumerate(inputDocs):
        head, tail = os.path.split(doc)
        print('Processing file ' + str(docNum+1) + "/" + str(numberOfDocs) + " " + tail)
        # a single unreadable pdf used to abort the WHOLE batch; record it and carry on,
        # then report every failure at the end (rather than failing silently)
        try:
            data = extract_pdf_text(doc)
            outputFilename = get_converted_output_path(doc, inputDir, outputDir, '.txt')
            make_output_directory(outputFilename)
            with open(outputFilename, "w", encoding="utf-8") as f:
                f.write(data)
            convertedDocs += 1
        except Exception as e:
            failedDocs.append(tail + ': ' + str(e))

    IO_user_interface_util.timed_alert(window, 4000, 'Analysis end', 'Finished running pdf converter at', True, str(convertedDocs) + ' of ' + str(numberOfDocs) + ' files were successfully converted from pdf to txt format and saved in directory ' + outputDir, True, startTime, False)
    if failedDocs:
        mb.showwarning(title='pdf converter', message=str(len(failedDocs)) + ' of ' + str(numberOfDocs) + ' pdf files could NOT be converted:\n\n' + '\n'.join(failedDocs))
    if openOutputFiles and len(inputFilename)>0 and outputFilename!='':
        IO_files_util.openFile(window, outputFilename)

# pdf --> docx, keeping BOTH the text and the images embedded in the pdf
# ______________________________________________________________________________________________
# pdfminer gives the layout objects (text boxes AND image placements) with their bounding boxes,
# which is what puts text and pictures back in reading order; pypdf gives the properly decoded
# image bytes (it runs them through Pillow); python-docx writes the result. All three are already
# NLP Suite dependencies, so this adds nothing to the installers.
# NOTE this is a REFLOW, not a facsimile: a single-column document with the original text and
# images in reading order, NOT the original fonts, columns and page geometry.

# returns, for one pdf, a list of pages, each a list of (kind, payload) in top-to-bottom order,
# with kind 'text' (payload is the string) or 'image' (payload is a (name, width in pdf points))
def get_pdf_layout_items(doc):
    def walk_images(obj):
        # an LTImage can sit directly on the page or nested inside an LTFigure
        if isinstance(obj, LTImage):
            yield obj
        elif isinstance(obj, LTFigure):
            for child in obj:
                for image in walk_images(child):
                    yield image

    pages = []
    for page_layout in extract_pages(doc, laparams=LAParams()):
        items = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text().strip()
                if text:
                    items.append(('text', element.y1, text))
            else:
                for image in walk_images(element):
                    items.append(('image', element.y1, (image.name, image.width)))
        # in a pdf the y coordinate grows UPWARD, so sorting descending gives reading order
        items.sort(key=lambda item: -item[1])
        pages.append([(kind, payload) for kind, y, payload in items])
    return pages

# pdfminer reports WHERE the images are but cannot reliably hand us the bytes: its own ImageWriter
# fails with 'unrecognized image mode' on ordinary png images, and what it does write, python-docx
# then refuses. pypdf decodes them properly (DCTDecode/FlateDecode/... through Pillow).
# Returns True when pypdf can be imported, so the caller can say so instead of quietly dropping
# every picture.
def is_pypdf_available():
    try:
        import pypdf  # noqa: F401
        return True
    except ImportError:
        return False

# returns one list of decoded images per page, or [] when pypdf cannot read them
def get_pdf_page_images(doc):
    import pypdf
    reader = pypdf.PdfReader(doc)
    page_images = []
    for page in reader.pages:
        try:
            page_images.append(list(page.images))
        except Exception:
            # an unsupported image filter must not cost us the text of the whole page
            page_images.append([])
    return page_images

# keep the picture the size it had in the pdf (72 pdf points = 1 inch), but never wider than the
# 6-inch text column of a default Letter/A4 docx, or Word pushes it off the page
def get_docx_image_width(width_in_points, max_inches=6.0):
    try:
        inches = float(width_in_points) / 72.0
    except (TypeError, ValueError):
        return Inches(max_inches)
    if inches <= 0 or inches > max_inches:
        return Inches(max_inches)
    return Inches(inches)

# A new python-docx document inherits Word's own docDefaults: 10 pt of space AFTER every paragraph
# and 1.15 line spacing (w:after="200" w:line="276"). One paragraph per block of pdf text then comes
# out looking double spaced next to a single spaced pdf. Setting the Normal style explicitly
# overrides those defaults for every paragraph in the document.
def set_single_spacing(document):
    paragraph_format = document.styles['Normal'].paragraph_format
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)
    paragraph_format.line_spacing = 1.0
    return document

def build_docx_from_pdf(doc, outputFilename):
    layout_pages = get_pdf_layout_items(doc)
    try:
        page_images = get_pdf_page_images(doc)
    except Exception:
        page_images = []
    document = set_single_spacing(Document())
    imagesPlaced = 0
    imagesLost = 0
    for pageNum, items in enumerate(layout_pages):
        available = list(page_images[pageNum]) if pageNum < len(page_images) else []
        used = 0
        for kind, payload in items:
            if kind == 'text':
                document.add_paragraph(payload)
            elif used < len(available):
                image = available[used]
                used = used + 1
                try:
                    document.add_picture(io.BytesIO(image.data), width=get_docx_image_width(payload[1]))
                    imagesPlaced = imagesPlaced + 1
                except Exception:
                    # never fail silently: leave a visible marker where the picture belonged
                    document.add_paragraph('[IMAGE could not be converted: ' + str(payload[0]) + ']')
                    imagesLost = imagesLost + 1
            else:
                document.add_paragraph('[IMAGE could not be extracted: ' + str(payload[0]) + ']')
                imagesLost = imagesLost + 1
        if pageNum < len(layout_pages) - 1:
            document.add_page_break()
    make_output_directory(outputFilename)
    document.save(outputFilename)
    return imagesPlaced, imagesLost

def pdf_to_docx_converter(window,inputFilename, inputDir, outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):

    # the images are the whole point of this option; without pypdf it would quietly degrade to a
    # worse copy of the pdf --> txt converter, so say what is missing and how to fix it
    if not is_pypdf_available():
        mb.showwarning(title='Missing module pypdf', message='The "Document converter (pdf --> docx)" option needs the Python module pypdf to extract the images embedded in a pdf file.\n\npypdf is NOT installed in your NLP environment.\n\nIn command prompt/terminal, type\n\nconda activate NLP\n\nthen type\n\npip install pypdf\n\nclose the NLP Suite and try again.\n\nIn the meantime you can use the "Document converter (pdf --> txt) (via pdfminer)" option, which needs no extra module but does NOT keep the images.')
        return

    inputDocs = get_pdf_file_list(window, inputFilename, inputDir)
    if len(inputDocs) == 0:
        return

    mb.showwarning(title='Warning', message='The pdf to docx converter keeps BOTH the text and the images embedded in your pdf files in a single Word document.\n\nPLEASE, NOTE that the docx output is a REFLOW of the pdf and NOT a photographic copy: you will get the original text and images in reading order, in a single column, but NOT the original fonts, columns and page layout. Tables are converted as lines of text and not as Word tables.\n\nA scanned pdf (i.e., a pdf that contains no text but only a picture of a page) contains no text to extract; only its images will be saved.\n\nUse the "Document converter (pdf --> txt)" option instead when you need plain text to feed to the NLP Suite tools.')

    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running pdf to docx converter at',
                                                   True, '', True, '', False)
    if inputDir == "":
        inputDir = os.path.dirname(inputFilename)

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                       label='pdf_2_docx',
                                                       silent=True)
    numberOfDocs = len(inputDocs)
    outputFilename = ''
    convertedDocs = 0
    imagesPlaced = 0
    imagesLost = 0
    failedDocs = []
    for docNum, doc in enumerate(inputDocs):
        head, tail = os.path.split(doc)
        print('Processing file ' + str(docNum+1) + "/" + str(numberOfDocs) + " " + tail)
        try:
            outputFilename = get_converted_output_path(doc, inputDir, outputDir, '.docx')
            placed, lost = build_docx_from_pdf(doc, outputFilename)
            imagesPlaced = imagesPlaced + placed
            imagesLost = imagesLost + lost
            convertedDocs = convertedDocs + 1
        except Exception as e:
            failedDocs.append(tail + ': ' + str(e))

    IO_user_interface_util.timed_alert(window, 4000, 'Analysis end', 'Finished running pdf to docx converter at', True, str(convertedDocs) + ' of ' + str(numberOfDocs) + ' files were successfully converted from pdf to docx format, with ' + str(imagesPlaced) + ' embedded images, and saved in directory ' + outputDir, True, startTime, False)
    if imagesLost > 0:
        mb.showwarning(title='pdf to docx converter', message=str(imagesLost) + ' embedded image(s) could not be extracted from your pdf file(s).\n\nEvery one of them is flagged in the docx output by a line reading [IMAGE could not be extracted] or [IMAGE could not be converted], so that you can see exactly where it belonged.')
    if failedDocs:
        mb.showwarning(title='pdf to docx converter', message=str(len(failedDocs)) + ' of ' + str(numberOfDocs) + ' pdf files could NOT be converted:\n\n' + '\n'.join(failedDocs))
    if openOutputFiles and len(inputFilename)>0 and outputFilename!='':
        IO_files_util.openFile(window, outputFilename)


# https://www.geeksforgeeks.org/python-working-with-docx-module/
# docx files all have the full path embedded
# Document Converter (docx ---> txt)'
# ONLY WORKS WITH DOCX; THERE ARE NO LIBRARIES TO CONVERT DOC DOCUMENTS

def docx_converter(window,inputFilename,inputDir,outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running docx to txt converter at',
                                                 True, '', True, '', False)

    outputDirSV=outputDir
    textFilename=''
    msgbox_subDir=False
    if len(inputDir)>0:
        msgbox_subDir = tk.messagebox.askyesnocancel("Process sub-directories",
                                                     "Do you want to process files in subdirectories?")
    if msgbox_subDir:
        inputDocs = IO_files_util.getFileList_SubDir(inputFilename,inputDir,'.docx')

        # inputDocs = [f for f in inputDocs if os.path.basename(f)[:2] != '~$' and (f[-5:] == '.docx' or f[-4:] == '.doc')]
    else:
        inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.docx',
                                              silent=False,
                                              configFileName=config_filename)
    nDocs = len(inputDocs)

    numberOfDocs=len(inputDocs)

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDirSV,
                                                       label='docx_2_txt',
                                                       silent=True)

    for docNum, doc in enumerate(inputDocs):
        head, tail = os.path.split(doc)
        if tail.startswith('~$'):
            numberOfDocs=numberOfDocs-1
            continue
        fileExtension=doc.split(".")[-1]
        #fileExtension = os.path.splitext(doc)[1]
        if fileExtension =="docx":
            print('Processing docx file ' + str(docNum + 1) + "/" + str(numberOfDocs) + " " + tail)

            document = Document(doc)
            textFilename = os.path.join(outputDir, tail[:-5] + ".txt")
            # TODO: if the subdirectory doesn't exist in output directory, create it
            if not os.path.exists(os.path.dirname(textFilename)):
                try:
                    os.makedirs(os.path.dirname(textFilename))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            with open(textFilename,"w", encoding="utf-8",errors='ignore') as textFile:
                for para in document.paragraphs:
                    textFile.write(para.text+'\n') #line of texts

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running docx to txt converter at', True, str(numberOfDocs) + ' txt files exported to the output subdirectory ' + outputDir, True, startTime, False)

    if openOutputFiles and len(inputFilename)>0:
        IO_files_util.openFile(window, textFilename)

def csv_converter(window,inputFilename,inputDir,outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):
    if inputFilename!='':
        if inputFilename[:2] != '~$' and inputFilename[-4:]=='.csv':
            inputDocs=[inputFilename]
        else:
            tk.messagebox.showinfo("csv converter","The input file " + inputFilename + " is not of type csv.\n\nPlease, select a csv type file for input and try again.")
            return
        inputDocs=[inputFilename]
    else:
        if inputDir!='':
            tk.messagebox.showinfo("csv converter","No input filename. The csv converter works only on a single csv file, rather than a whole directory. Please, select an input csv file and try again.")
            return
        else:
            tk.messagebox.showinfo("csv converter","No input filename. Please, select an input csv file and try again.")
            return
        tk.messagebox.showinfo("csv converter","The function is still under construction.\n\nSorry!")
        return
        # TODO add a REMINDER that if they need to use some of the csv fields as filters,
        #   they need to use first the Data manipulation to extract specific fields by specific values
        #   for instance, in the csv output of the gender annotator, you may want to extract all the sentences
        #       WHERE the gender is Male and/or Female for separate analysis
        # TODO Check headers if Sentence is present and export sentences
        # TODO If Document ID present, loop through all documents
        #   ask the user if they want to export the Document (i.e., filename) adding it before each document sentence
        #   If the values of Document ID > 1  further ask if they want to create separate files or a single merged file
        #   Could further ask if they want to embed the filename in special symbols (e.g., <@ @>, as in <@filename@>
        #       so that the files can also be easily split

def rtf_converter(window,inputFilename,inputDir,outputDir,config_filename, openOutputFiles,chartPackage, dataTransformation):
    textFilename=''
    if len(inputDir)>0:
        msgbox_subDir = tk.messagebox.askyesnocancel("Process sub-directories",
                                                     "Do you want to process for files in subdirectories?")
        if msgbox_subDir:
            inputRTFs = IO_files_util.getFileList_SubDir(inputFilename,inputDir,'.rtf')

            inputRTFs = [f for f in inputRTFs if os.path.basename(f)[:2] != '~$' and  f[-4:] == '.rtf']
        else:
            inputRTFs = [os.path.join(inputDir,f) for f in os.listdir(inputDir) if f[:2]!='~$' and  f[-4:]=='.rtf']
    elif len(inputFilename)>0:
        if inputFilename[:2] != '~$' and inputFilename[-4:]=='.rtf':
            inputRTFs=[inputFilename]
        else:
            tk.messagebox.showinfo("rtf converter","The input file " + inputFilename + " is not of type rtf.\n\nPlease, select a rtf type file for input and try again.")
            return
        inputRTFs=[inputFilename]
    else:
        tk.messagebox.showinfo("rtf converter","No input filename or directory specified. The program will exit.")
        return
    if len(inputRTFs) == 0:
        tk.messagebox.showinfo("Warning","There are no rtf files in the input directory. The program will exit.")
        return
    numberOfDocs=len(inputRTFs)

    for docNum, doc in enumerate(inputRTFs):
        head, tail = os.path.split(doc)
        print('Processing file ' + str(docNum+1) + "/" + str(numberOfDocs) + " " + tail)
        fileExtension=doc.split(".")[-1]
        #fileExtension = os.path.splitext(doc)[1]
        if fileExtension =="rtf":
            lines = []#list of each line in the txt files
            with open(doc, 'r', encoding='utf-8', errors='ignore') as rtf_fh:
                fullText = rtf_fh.read()
            # https://stackoverflow.com/questions/60897366/how-to-read-rtf-file-and-convert-into-python3-strings-and-can-be-stored-in-pyth
            # https://stackoverflow.com/questions/44580580/how-to-convert-rtf-string-to-plain-text-in-python-using-any-library
            # https://stackoverflow.com/questions/188545/regular-expression-for-extracting-text-from-an-rtf-string/188877#188877
            text = rtf_to_text(fullText)
            # text=fullText
            common = os.path.commonprefix([doc, inputDir])
            relativePath = os.path.relpath(doc, common)
            textFilename = os.path.join(outputDir, os.path.splitext(relativePath)[0] + ".txt")
            # TODO: if the subdirectory doesn't exist in output directory, create it
            if not os.path.exists(os.path.dirname(textFilename)):
                try:
                    os.makedirs(os.path.dirname(textFilename))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            with open(textFilename,"w", encoding="utf-8",errors='ignore') as textFile:
                textFile.write(text)
    if openOutputFiles and len(inputFilename)>0:
        IO_files_util.openFile(window, textFilename)

# the tsv file (inputFilename) has the full path embedded
# File Converter (tsv --> csv)
def tsv_converter(window,inputFilename,outputDir, header):
    # read a tab-separated file
    with open(inputFilename,'r',encoding="utf-8",errors='ignore') as fin:
        cr = csv.reader(fin, delimiter='\t')
        filecontents = [line for line in cr]

    # write comma-separated file (comma is the default delimiter)
    inputFilename,extension = splitext(inputFilename)
    with open(inputFilename+'.csv','w',newline='') as fou:
        cw = csv.writer(fou, dialect = 'excel')
        cw.writerow(header)
        for item in filecontents:
            cw.writerow(item)
    return inputFilename+'.csv'


# An OCR (pytesseract) pdf converter used to be sketched out here and offered in the GUI as
# 'Document converter (pdf --> txt) (via pytesseract)'. It was never reachable: the menu entry was
# wired to pdf_converter (i.e., it ran pdfminer), the helpers imported image_to_string INSIDE
# convert_pdf_to_img so convert_image_to_text raised NameError, and neither pytesseract nor
# pdf2image was ever listed in requirements.txt/requirements_mac.txt. Removed rather than left to
# look like a working option. Real OCR also needs the Tesseract and poppler BINARIES installed on
# the user's machine, which does not fit the frozen NLP Suite installers; a pip-only OCR engine
# would be the way back in.
