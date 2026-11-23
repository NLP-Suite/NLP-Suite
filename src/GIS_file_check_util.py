import CoNLL_util
import IO_csv_util


def CoNLL_checker(inputFilename):
    if CoNLL_util.check_CoNLL(inputFilename, True):
        inputIsCoNLL = True
        inputIsGeocoded = False
    else:
        inputIsCoNLL = False
    headers = IO_csv_util.get_csvfile_headers(inputFilename, False)
    if "Date" in headers:
        datePresent = True
    else:
        datePresent = False
    if "Latitude" in headers and "Longitude" in headers:
        inputIsGeocoded = True
    else:
        inputIsGeocoded = False
    withHeader = True
    filenamePositionInCoNLLTable = 11

    return inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable
