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
import re
import shutil

import csv
import tkinter as tk
import tkinter.messagebox as mb
import errno
# pip install pdfminer.six --user (since it may ask for permission) rather than pip install pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTAnno, LTChar, LTFigure, LTImage, LTTextContainer, LTTextLine
from docx import Document #pip install python-docx
from docx.shared import Inches, Pt, RGBColor
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

# a pdf records no bold/italic flag: the typeface is in the font NAME, one font per style
# (TimesNewRomanPS-BoldMT, -ItalicMT, -BoldItalicMT, ...)
def get_char_style(ch):
    fontname = (ch.fontname or '').lower()
    bold = 'bold' in fontname or 'black' in fontname or 'heavy' in fontname or 'semibold' in fontname
    italic = 'italic' in fontname or 'oblique' in fontname
    return bold, italic, round(ch.size, 1), get_char_colour(ch)

# pdfminer reports colour components as 0-1 values, in whatever space the pdf uses: one value for
# grayscale, three for RGB, four for CMYK. Returns (r, g, b) 0-255, or None for ordinary black,
# which is left to the docx default rather than written out on every single run.
def get_char_colour(ch):
    try:
        colour = ch.graphicstate.ncolor
    except AttributeError:
        return None
    if colour is None:
        return None
    if isinstance(colour, (int, float)):
        values = [colour, colour, colour]
    else:
        values = list(colour)
        if len(values) == 1:
            values = values * 3
        elif len(values) == 4:
            cyan, magenta, yellow, black = values
            values = [(1 - cyan) * (1 - black), (1 - magenta) * (1 - black), (1 - yellow) * (1 - black)]
        elif len(values) != 3:
            return None
    try:
        rgb = tuple(max(0, min(255, int(round(float(value) * 255)))) for value in values)
    except (TypeError, ValueError):
        return None
    return None if rgb == (0, 0, 0) else rgb

# a pdf breaks its lines wherever the page ran out of room, and pdfminer faithfully reports those
# breaks; copied straight into a docx they turn up as line breaks in the middle of sentences.
# Lines are joined back into flowing text with a blank, EXCEPT after an end-of-line hyphen, where
# the two halves are joined tight and the hyphen is KEPT: whether it is typesetting hyphenation
# ('dictionar-y') or a real compound ('pretty-smart') cannot be told apart here, and the Suite
# already asks the user that question in file_cleaner_util.remove_typeseting_hyphenation.
def get_line_separator(previous_text):
    if previous_text == '' or previous_text[-1].isspace():
        return ''  # the line already ends with a blank; a second one would show up in the docx
    if previous_text.endswith('-') and len(previous_text) >= 2 and previous_text[-2] != ' ':
        return ''
    return ' '

# returns [(text, bold, italic, size, colour), ...] for one pdfminer text container: consecutive
# characters sharing a style are merged into a single run, so a docx paragraph can be rebuilt with
# the bold, italic, size and colour the pdf actually used
def get_text_runs(element):
    runs = []

    def append(text, style):
        if text == '':
            return
        if runs and runs[-1][1] == style:
            runs[-1][0].append(text)
        else:
            runs.append(([text], style))

    for line in element:
        if not isinstance(line, LTTextLine):
            continue
        if runs:
            # close the previous line before opening this one
            previous_text = ''.join(runs[-1][0])
            append(get_line_separator(previous_text), runs[-1][1])
        for ch in line:
            if isinstance(ch, LTChar):
                append(ch.get_text(), get_char_style(ch))
            elif isinstance(ch, LTAnno):
                # blanks and the end-of-line marker inserted by the layout analyser: they carry no
                # style of their own, so they extend the run already open
                text = ch.get_text()
                if text != '\n' and runs:
                    append(text, runs[-1][1])

    merged = [(''.join(chunks), style) for chunks, style in runs]
    # trim the leading/trailing whitespace of the paragraph as a whole
    while merged and merged[0][0].strip() == '':
        merged.pop(0)
    while merged and merged[-1][0].strip() == '':
        merged.pop()
    if merged:
        merged[0] = (merged[0][0].lstrip(), merged[0][1])
        merged[-1] = (merged[-1][0].rstrip(), merged[-1][1])
    return [(text, style[0], style[1], style[2], style[3]) for text, style in merged if text != '']

def get_runs_text(runs):
    return ''.join(run[0] for run in runs)

# python-docx writes XML, and XML 1.0 cannot represent most control characters. A pdf carrying one
# made add_run() raise ValueError, and because that happens mid-document the WHOLE file was lost --
# TIPS_NLP_Universal dependencies.pdf holds 186 NUL bytes, so one invisible byte cost the entire
# conversion of a 20-page document. Extraction puts them there: a NUL in the pdf's font or encoding
# tables comes through as text. They are dropped rather than converted, because there is nothing to
# convert them TO -- but the count is reported, since a silent edit to someone's document is exactly
# the kind of thing this Suite must not do.
_xml_incompatible_pattern = re.compile(
    u'[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]')

def strip_xml_incompatible(text):
    """(clean text, how many characters were dropped) for one run of pdf text."""
    cleaned = _xml_incompatible_pattern.sub('', text)
    return cleaned, len(text) - len(cleaned)

# pdfminer often reports the wrapped lines of ONE paragraph as SEPARATE text boxes - it does so for
# every line of an indented numbered list - so joining the lines inside a box is not enough: the
# pdf's line breaks come back as paragraph breaks between boxes. The geometry tells them apart. In
# TIPS_NLP_Annotator dictionary.pdf the continuation lines of a list item sit 1.5-1.8 pt below the
# line they continue, against 6.8 pt between the lines of the table of contents and 15 pt or more
# between real paragraphs. The threshold is therefore taken from the text's own line height rather
# than hard-coded in points, so it holds for other type sizes.
list_marker_pattern = re.compile(r'^\s*(\d+\s*[\.\)]|[a-zA-Z]\s*[\.\)]|[•·●∙*-])\s')

def is_list_marker(text):
    return bool(list_marker_pattern.match(text))

# previous and current are the box dictionaries built in get_pdf_layout_items
def should_join_text_boxes(previous, current):
    if previous is None or previous['kind'] != 'text' or current['kind'] != 'text':
        return False
    gap = previous['y0'] - current['y1']
    if gap < 0 or gap > 0.3 * max(previous['line_height'], 1):
        return False
    # a continuation line is never LESS indented than the line it continues: a hanging indent puts
    # it further right, and a line starting further LEFT is a new item going back to the margin
    if current['x0'] < previous['x0'] - 1:
        return False
    # '3.', 'b)', a bullet: the start of a new item, however tightly it is set
    if is_list_marker(get_runs_text(current['payload'])):
        return False
    return True

# returns, for one pdf, a list of pages, each a list of (kind, payload) in top-to-bottom order,
# with kind 'text' (payload is a list of styled runs) or 'image' (payload is a (name, width))
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
                runs = get_text_runs(element)
                if get_runs_text(runs).strip():
                    text_lines = [line for line in element if isinstance(line, LTTextLine)]
                    items.append({'kind': 'text', 'payload': runs,
                                  'x0': element.x0, 'y0': element.y0, 'y1': element.y1,
                                  'line_height': element.height / max(len(text_lines), 1)})
            else:
                for image in walk_images(element):
                    items.append({'kind': 'image', 'payload': (image.name, image.width),
                                  'x0': element.x0, 'y0': element.y0, 'y1': element.y1,
                                  'line_height': element.height})
        # in a pdf the y coordinate grows UPWARD, so sorting descending gives reading order
        items.sort(key=lambda item: -item['y1'])

        # stitch the wrapped lines of one paragraph back together across boxes
        merged = []
        for item in items:
            previous = merged[-1] if merged else None
            if should_join_text_boxes(previous, item):
                separator = get_line_separator(get_runs_text(previous['payload']))
                if separator:
                    last_text, bold, italic, size, colour = previous['payload'][-1]
                    previous['payload'][-1] = (last_text + separator, bold, italic, size, colour)
                previous['payload'] = previous['payload'] + item['payload']
                previous['y0'] = item['y0']
            else:
                merged.append(item)
        pages.append([(item['kind'], item['payload']) for item in merged])
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
    charactersDropped = 0
    for pageNum, items in enumerate(layout_pages):
        available = list(page_images[pageNum]) if pageNum < len(page_images) else []
        used = 0
        for kind, payload in items:
            if kind == 'text':
                paragraph = document.add_paragraph()
                for text, bold, italic, size, colour in payload:
                    text, dropped = strip_xml_incompatible(text)
                    charactersDropped = charactersDropped + dropped
                    if text == '':
                        continue
                    run = paragraph.add_run(text)
                    run.bold = bold
                    run.italic = italic
                    if size:
                        run.font.size = Pt(size)
                    if colour:
                        run.font.color.rgb = RGBColor(*colour)
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
    if charactersDropped:
        print('   ' + str(charactersDropped) + ' control character(s) in the pdf were dropped; '
              'Word cannot store them. No visible text is affected.')
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


# OCR: pdf --> txt for SCANNED pdf files
# ______________________________________________________________________________________________
# A scanned pdf holds no text at all, only a picture of each page: pdfminer correctly returns
# nothing for it. OCR reads the letters out of that picture. This needs FOUR separate pieces - the
# pytesseract and pdf2image Python modules, plus the Tesseract and poppler BINARIES - and the
# binaries cannot be bundled into the frozen NLP Suite installers, so every one of them is checked
# and reported by name instead of failing with a stack trace.
#
# The earlier version of this code was never reachable: the menu entry ran pdfminer, and
# convert_image_to_text called image_to_string, which was imported inside ANOTHER function, so it
# would have raised NameError on the first call.

# Tesseract and poppler are frequently installed where a GUI app's PATH does not reach (a Mac app
# launched from the Finder does not see /opt/homebrew/bin), which is why the old code carried a
# commented-out hard-coded homebrew path. Look in PATH first, then in the usual install locations.
# both lists hold DIRECTORIES to look in, never filenames
tesseract_search_paths = [
    r'C:\Program Files\Tesseract-OCR',
    r'C:\Program Files (x86)\Tesseract-OCR',
    '/opt/homebrew/bin',
    '/usr/local/bin',
    '/usr/bin']

poppler_search_paths = [
    r'C:\Program Files\poppler\Library\bin',
    r'C:\Program Files\poppler\bin',
    '/opt/homebrew/bin',
    '/usr/local/bin',
    '/usr/bin']

def find_executable(name, search_paths):
    found = shutil.which(name)
    if found:
        return found
    for directory in search_paths:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path
        if os.path.isfile(path + '.exe'):
            return path + '.exe'
    return None

def get_tesseract_path():
    return find_executable('tesseract', tesseract_search_paths)

# pdf2image needs the DIRECTORY holding pdftoppm, not the executable itself
def get_poppler_path():
    executable = find_executable('pdftoppm', poppler_search_paths)
    return os.path.dirname(executable) if executable else None

# returns a list of the missing pieces, empty when OCR can actually run
def get_OCR_missing_requirements():
    missing = []
    try:
        import pytesseract  # noqa: F401
    except ImportError:
        missing.append('the Python module pytesseract   (in the NLP environment, type: pip install pytesseract)')
    try:
        import pdf2image  # noqa: F401
    except ImportError:
        missing.append('the Python module pdf2image   (in the NLP environment, type: pip install pdf2image)')
    if get_tesseract_path() is None:
        if sys.platform == 'darwin':
            missing.append('the Tesseract OCR software   (in terminal, type: brew install tesseract)')
        else:
            missing.append('the Tesseract OCR software   (download the installer from https://github.com/UB-Mannheim/tesseract/wiki and install it in C:\\Program Files\\Tesseract-OCR)')
    if get_poppler_path() is None:
        if sys.platform == 'darwin':
            missing.append('the poppler software   (in terminal, type: brew install poppler)')
        else:
            missing.append('the poppler software   (download it from https://github.com/oschwartz10612/poppler-windows/releases and unzip it to C:\\Program Files\\poppler)')
    return missing

# OCR one pdf: every page is rendered to an image, then read back as text.
# 300 dpi is the resolution Tesseract is documented to work best at; the pdf2image default of 200
# noticeably costs accuracy on small print.
# The pages are rendered ONE AT A TIME. Handing the whole pdf to convert_from_path returns a list
# holding every page as an uncompressed image at once: at 300 dpi a Letter page is 2550 x 3300
# pixels in 3 bands, i.e. 24 MB, so a 300-page book would ask for over 7 GB of memory before a
# single character had been read. Rendering page by page keeps it at one page's worth, and lets the
# user see progress on a job that runs for seconds per page.
def OCR_pdf_text(doc, language='eng', dpi=300):
    import pytesseract
    from pdf2image import convert_from_path, pdfinfo_from_path

    tesseract_path = get_tesseract_path()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    poppler_path = get_poppler_path()

    try:
        numberOfPages = int(pdfinfo_from_path(doc, poppler_path=poppler_path)['Pages'])
    except Exception:
        numberOfPages = 0
    if numberOfPages < 1:
        # the page count could not be read; fall back to converting in one go
        pages = convert_from_path(doc, dpi=dpi, poppler_path=poppler_path)
        return '\n'.join(pytesseract.image_to_string(page, lang=language) for page in pages)

    text = []
    for pageNumber in range(1, numberOfPages + 1):
        print('   OCR page ' + str(pageNumber) + '/' + str(numberOfPages))
        for page in convert_from_path(doc, dpi=dpi, poppler_path=poppler_path,
                                      first_page=pageNumber, last_page=pageNumber):
            text.append(pytesseract.image_to_string(page, lang=language))
            page.close()  # release the 24 MB before rendering the next page
    return '\n'.join(text)

# the NLP Suite language names are not the 3-letter codes Tesseract uses for its language packs
tesseract_language_codes = {
    'english': 'eng', 'italian': 'ita', 'french': 'fra', 'german': 'deu',
    'spanish': 'spa', 'portuguese': 'por', 'dutch': 'nld', 'russian': 'rus',
    'chinese': 'chi_sim', 'japanese': 'jpn', 'arabic': 'ara', 'latin': 'lat'}

# Tesseract can read SEVERAL languages in one pass: the languages are joined with a + sign, as in
# 'eng+ita', and the first one is the primary. The Suite's own 'Corpus language' setting is a
# LANGUAGE(S) field and can likewise hold more than one.
# Note that piling up languages is not free: each one slows the recognition down and, for languages
# that do not share an alphabet, can make the result WORSE. Ask for the ones you actually have.
#
# Returns (the lang string to hand to Tesseract, the codes whose pack is NOT installed). Packs that
# are missing are dropped instead of letting Tesseract abort with 'Failed loading language'.
def get_tesseract_languages(language):
    names = [name.strip() for name in re.split(r'[,;+/]|\band\b', str(language)) if name.strip()]
    codes = []
    for name in names:
        code = tesseract_language_codes.get(name.lower())
        if code and code not in codes:
            codes.append(code)
    if not codes:
        codes = ['eng']
    try:
        import pytesseract
        tesseract_path = get_tesseract_path()
        if tesseract_path:
            # get_languages shells out to tesseract, which is NOT necessarily on PATH
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        installed = pytesseract.get_languages(config='')
    except Exception:
        # cannot tell what is installed; hand Tesseract what was asked for and let it complain
        return '+'.join(codes), []
    available = [code for code in codes if code in installed]
    missing = [code for code in codes if code not in installed]
    if not available:
        available = ['eng'] if 'eng' in installed else codes
    return '+'.join(available), missing

def pdf_OCR_converter(window,inputFilename, inputDir, outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):

    missing = get_OCR_missing_requirements()
    if missing:
        mb.showwarning(title='OCR software missing', message='The "Document converter (pdf --> txt) (via pytesseract OCR)" option reads the text out of SCANNED pdf files, i.e., pdf files that contain no text but only a picture of each page.\n\nUnlike every other converter, OCR needs software installed on your machine that the NLP Suite installers cannot bundle.\n\nThe following is missing:\n\n   ' + '\n\n   '.join(missing) + '\n\nInstall what is listed above, close the NLP Suite and try again.\n\nFor the complete instructions, please open the TIPS file "TIPS_NLP_pdf converters.pdf" via the "Open TIPS files" dropdown menu.\n\nIf your pdf files are NOT scanned (i.e., you can select the text in a pdf reader), you do not need OCR at all: use the "Document converter (pdf --> txt) (via pdfminer)" option, which is also far faster.')
        return

    inputDocs = get_pdf_file_list(window, inputFilename, inputDir)
    if len(inputDocs) == 0:
        return

    language = 'English'
    try:
        # honour the corpus language selected in NLP_setup_package_language_main; the language is
        # item 4 of the tuple (error, package, parsers, basics_package, language, ...)
        import config_util
        config_values = config_util.read_NLP_package_language_config()
        if config_values and len(config_values) > 4 and config_values[4]:
            language = config_values[4]
            if isinstance(language, (list, tuple)):  # the config can hold several languages
                language = ', '.join(str(item) for item in language)
    except Exception:
        pass
    language_code, missing_languages = get_tesseract_languages(language)
    if missing_languages:
        mb.showwarning(title='OCR language pack missing', message='Your corpus language is set to ' + str(language) + ', but the following Tesseract language pack(s) are NOT installed on your machine:\n\n   ' + ', '.join(missing_languages) + '\n\nThe OCR will run in ' + language_code + ' instead. Reading a corpus with the wrong language gives poor results, particularly for accented characters.\n\nOn a Mac, in terminal, type\n\nbrew install tesseract-lang\n\nto install ALL language packs. On Windows, re-run the Tesseract installer from https://github.com/UB-Mannheim/tesseract/wiki and tick the additional language(s) you need under "Additional language data".')

    mb.showwarning(title='Warning', message='OCR is SLOW: every page of every pdf file is first rendered as a 300 dpi image and then read character by character. Expect roughly a few seconds per page; a few hundred pages will take a good while. The NLP Suite will look frozen while it works - please, be patient and watch the progress in the command prompt/terminal window.\n\nOCR is also never perfect: ALWAYS check the converted output file. The better the scan, the better the result.\n\nIf your pdf files are NOT scanned (i.e., you can select the text in a pdf reader), use the "Document converter (pdf --> txt) (via pdfminer)" option instead: it is exact and far faster.')

    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running the pdf OCR converter at',
                                                   True, '', True, '', False)
    if inputDir == "":
        inputDir = os.path.dirname(inputFilename)

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                       label='pdf_OCR_2_txt',
                                                       silent=True)
    numberOfDocs = len(inputDocs)
    outputFilename = ''
    convertedDocs = 0
    emptyDocs = []
    failedDocs = []
    for docNum, doc in enumerate(inputDocs):
        head, tail = os.path.split(doc)
        print('OCR processing file ' + str(docNum+1) + "/" + str(numberOfDocs) + " " + tail)
        try:
            data = OCR_pdf_text(doc, language=language_code)
            outputFilename = get_converted_output_path(doc, inputDir, outputDir, '.txt')
            make_output_directory(outputFilename)
            with open(outputFilename, "w", encoding="utf-8") as f:
                f.write(data)
            convertedDocs = convertedDocs + 1
            if data.strip() == '':
                emptyDocs.append(tail)
        except Exception as e:
            failedDocs.append(tail + ': ' + str(e))

    IO_user_interface_util.timed_alert(window, 4000, 'Analysis end', 'Finished running the pdf OCR converter at', True, str(convertedDocs) + ' of ' + str(numberOfDocs) + ' files were successfully OCRed from pdf to txt format and saved in directory ' + outputDir, True, startTime, False)
    if emptyDocs:
        mb.showwarning(title='OCR converter', message='OCR found NO text in ' + str(len(emptyDocs)) + ' of your pdf files:\n\n' + '\n'.join(emptyDocs) + '\n\nThe output txt file(s) are empty. This usually means the scan is too poor to read, the page is upside down or sideways, or the language pack does not match the language of the document.')
    if failedDocs:
        mb.showwarning(title='OCR converter', message=str(len(failedDocs)) + ' of ' + str(numberOfDocs) + ' pdf files could NOT be OCRed:\n\n' + '\n'.join(failedDocs))
    if openOutputFiles and len(inputFilename)>0 and outputFilename!='':
        IO_files_util.openFile(window, outputFilename)
