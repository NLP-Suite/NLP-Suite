# Written by Roberto Franzosi November 2019
# edited by Cynthia Dong
# The script includes several types of document converters:
#   pdf --> txt
#   docx --> txt
#   tsv --> csv
#   csv --> txt
import csv
import errno
import logging
import os

# pip install pdfminer.six --user (since it may ask for permission) rather than pip install pdfminer
from os.path import splitext

import IO_files_util
from striprtf.striprtf import rtf_to_text

logger = logging.getLogger(__name__)

# https://pdfminersix.readthedocs.io/en/latest/
# # https://pypi.org/project/pdfminer/#description
# # https://towardsdatascience.com/pdf-preprocessing-with-python-19829752af9f
# # inputFilename contains full path
# def pdf_converter(window, inputFilename, inputDir, outputDir, config_filename, openOutputFiles, chartPackage, dataTransformation):

#     if len(inputDir) > 0:
#         # Removed GUI prompt, just process all subdirectories
#         # filter files
#         if inputFilename[:2] != '~$' and inputFilename[-4:] == '.pdf':

#     if len(inputDocs) == 0:

#     print("PLEASE, MAKE SURE TO CHECK THE CONVERTED OUTPUT FILE. IF YOU PLAN TO PARSE THE TXT OUTPUT VIA STANFORD CORENLP, YOU SHOULD CONSIDER CLEANING YOUR OUTPUT FROM COPYRIGHT MATERIAL AND BIBLIOGRAPHICAL REFERENCES, SINCE SUCH TEXTUAL ELEMENTS DO NOT HAVE COMPLETE SENTENCES.")

#     for docNum, doc in enumerate(inputDocs):
#         with open(doc, 'rb') as fp:

#             if inputDir == "":


#             if not os.path.exists(os.path.dirname(outputFilename)):
#                     if exc.errno != errno.EEXIST:
#                         raise

#             for page in PDFPage.get_pages(fp):


#     if openOutputFiles and len(inputFilename) > 0:

# if __name__ == '__main__':


# # https://www.geeksforgeeks.org/python-working-with-docx-module/
# # docx files all have the full path embedded
# # Document Converter (docx ---> txt)'
# # ONLY WORKS WITH DOCX; THERE ARE NO LIBRARIES TO CONVERT DOC DOCUMENTS

# def docx_converter(window,inputFilename,inputDir,outputDir,config_filename,openOutputFiles,chartPackage, dataTransformation):

#     # replaced GUI prompt with default False (no)
#     if len(inputDir)>0:
#         # Default no sub-directory processing (you can change to True if wanted)
#     if msgbox_subDir:

#         inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.docx',
#                                               configFileName=config_filename)


#     outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDirSV,
#                                                        silent=True)

#     for docNum, doc in enumerate(inputDocs):
#         if tail.startswith('~$'):
#             continue
#         if fileExtension =="docx":

#             # TODO: if the subdirectory doesn't exist in output directory, create it
#             if not os.path.exists(os.path.dirname(textFilename)):
#                     if exc.errno != errno.EEXIST:
#                         raise
#             with open(textFilename,"w", encoding="utf-8",errors='ignore') as textFile:
#                 for para in document.paragraphs:

#     if openOutputFiles and len(inputFilename)>0:


def csv_converter(
    window,
    inputFilename,
    inputDir,
    outputDir,
    config_filename,
    openOutputFiles,
    chartPackage,
    dataTransformation,
):
    if inputFilename != "":
        if inputFilename[:2] != "~$" and inputFilename[-4:] == ".csv":
            pass
        else:
            logger.info(
                f"INFO: The input file {inputFilename} is not of type csv. Please select a csv type file for input and try again."
            )
            return
    else:
        if inputDir != "":
            logger.info(
                "INFO: No input filename. The csv converter works only on a single csv file, rather than a whole directory. Please select an input csv file and try again."
            )
            return
        else:
            logger.info("INFO: No input filename. Please select an input csv file and try again.")
            return
        logger.info("INFO: The function is still under construction.\nSorry!")
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


def rtf_converter(
    window,
    inputFilename,
    inputDir,
    outputDir,
    config_filename,
    openOutputFiles,
    chartPackage,
    dataTransformation,
):
    textFilename = ""
    # replaced GUI prompt with default False (no)
    msgbox_subDir = False
    if len(inputDir) > 0:
        msgbox_subDir = False
        if msgbox_subDir:
            inputRTFs = IO_files_util.getFileList_SubDir(inputFilename, inputDir, ".rtf")

            inputRTFs = [f for f in inputRTFs if os.path.basename(f)[:2] != "~$" and f[-4:] == ".rtf"]
        else:
            inputRTFs = [os.path.join(inputDir, f) for f in os.listdir(inputDir) if f[:2] != "~$" and f[-4:] == ".rtf"]
    elif len(inputFilename) > 0:
        if inputFilename[:2] != "~$" and inputFilename[-4:] == ".rtf":
            inputRTFs = [inputFilename]
        else:
            logger.info(
                f"INFO: The input file {inputFilename} is not of type rtf. Please select a rtf type file for input and try again."
            )
            return
        inputRTFs = [inputFilename]
    else:
        logger.info("INFO: No input filename or directory specified. The program will exit.")
        return
    if len(inputRTFs) == 0:
        logger.info("WARNING: There are no rtf files in the input directory. The program will exit.")
        return
    numberOfDocs = len(inputRTFs)

    for docNum, doc in enumerate(inputRTFs):
        head, tail = os.path.split(doc)
        logger.info("Processing file " + str(docNum + 1) + "/" + str(numberOfDocs) + " " + tail)
        fileExtension = doc.split(".")[-1]
        if fileExtension == "rtf":
            fullText = open(doc, encoding="utf-8", errors="ignore").read()
            # https://stackoverflow.com/questions/60897366/how-to-read-rtf-file-and-convert-into-python3-strings-and-can-be-stored-in-pyth
            # https://stackoverflow.com/questions/44580580/how-to-convert-rtf-string-to-plain-text-in-python-using-any-library
            # https://stackoverflow.com/questions/188545/regular-expression-for-extracting-text-from-an-rtf-string/188877#188877
            text = rtf_to_text(fullText)
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
            with open(textFilename, "w", encoding="utf-8", errors="ignore") as textFile:
                textFile.write(text)
    if openOutputFiles and len(inputFilename) > 0:
        IO_files_util.openFile(window, textFilename)


# the tsv file (inputFilename) has the full path embedded
# File Converter (tsv --> csv)
def tsv_converter(window, inputFilename, outputDir, header):
    # read a tab-separated file
    with open(inputFilename, encoding="utf-8", errors="ignore") as fin:
        cr = csv.reader(fin, delimiter="\t")
        filecontents = [line for line in cr]

    # write comma-separated file (comma is the default delimiter)
    inputFilename, extension = splitext(inputFilename)
    with open(inputFilename + ".csv", "w", newline="") as fou:
        cw = csv.writer(fou, dialect="excel")
        cw.writerow(header)
        for item in filecontents:
            cw.writerow(item)
    return inputFilename + ".csv"


# with given string of directory, this script will use pytesseract to convert all the pdfs
# inside the directory into .txt files


# this tesseract path will differ for every machine..
# for Windows:
# for Mac:


################################################
# necessary functions to convert pdf to img to txt
################################################
def convert_pdf_to_img(pdf_file):
    from pdf2image import convert_from_path

    return convert_from_path(pdf_file)


def convert_image_to_text(file):
    from pytesseract import image_to_string

    text = image_to_string(file)
    return text


def get_text_from_any_pdf(pdf_file):
    images = convert_pdf_to_img(pdf_file)
    final_text = ""
    for _pg, img in enumerate(images):
        final_text += convert_image_to_text(img)

    return final_text


#################################################
# actual execution of the functions
#################################################

# the directory of pdf files
#
# for filename in os.listdir(pdf_dir):
#     if os.path.isfile(path_to_pdf) and path_to_pdf.endswith('pdf'):
#
#
#         with open(f'{title}.txt', 'w') as f:
