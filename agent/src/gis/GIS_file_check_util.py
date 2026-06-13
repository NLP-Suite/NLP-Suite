import logging

import CoNLL_util
import IO_csv_util
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# returns False if error found
def geocoded_checker(numColumns, minColumns, headers, locationColumnValue, inputFilename, encodingValue):
    # check that the file REALLY contains geocoded data, with float values for lat and long
    for i in range(len(headers)):
        if locationColumnValue == headers[i]:
            location_num = i
            break
    latitude_name = headers[location_num + 1]
    longitude_name = headers[location_num + 2]
    try:
        dt = pd.read_csv(inputFilename, encoding=encodingValue, on_bad_lines="skip")
    except OSError as e:
        logger.info(
            "Input file error,There was an error reading the input file\n"
            + str(inputFilename)
            + "\nwith geocoded input.\n\n"
            + str(e)
        )
        #  Most likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.
        return False

    check1 = True
    check2 = True
    for x in dt[latitude_name]:
        if not isinstance(x, float):
            check1 = False
            break
        elif x > 90 or x < -90:
            check1 = False
            break
    for y in dt[longitude_name]:
        if not isinstance(y, float):
            check2 = False
            break
        elif y > 180 or y < -180:
            check2 = False
            break

    if not check1 or not check2:
        logger.info(
            "Input file error, ou have ticked the geocoded checkbox.\n\nBut the input file does not have two consecutive columns of float type data (in the forms of: columns of latitude in range [-90, 90] and longitude in range [-180, 180]) right after your selected location field, "
            + str(locationColumnValue)
            + ".\n\nPlease, check your input file and/or deselect the geocoded option and try again."
        )
        return False
    else:
        return True


# Checks that the location column is a column of strings
def location_column_checker(inputFilename, locationColumnValue, encodingValue):
    try:
        dt = pd.read_csv(inputFilename, encoding=encodingValue, on_bad_lines="skip")
    except Exception:
        logger.info(
            "Input file error, there was an error reading the input file\n "
            + str(inputFilename)
            + "\nwith geocoded input. Most likely, the error is due to an encoding error. Your current encoding value is "
            + encodingValue
            + ".\n\nSelect a different encoding value and try again."
        )

        return False
    check1 = True
    # convert np.nan (in float form) to an empty string
    dt[locationColumnValue] = dt[locationColumnValue].replace(np.nan, "")
    for x in dt[locationColumnValue]:
        if isinstance(x, str) is not True:
            check1 = False
            break
    if not check1:
        logger.info(
            "Input file error The location column you selected, "
            + locationColumnValue
            + ", is not a column of strings, as expected for the column containing location names.\n\nPlease, reselect your location column and try again."
        )
        return False
    else:
        return True


# def restrictions_checker(inputFilename,inputIsCoNLL,inputIsGeocoded,numColumns,withHeader,headers,computeDistance_var,baselineLocation,locationColumnValue,locationColumnValue2,encodingValue):
def restrictions_checker(inputFilename, inputIsCoNLL, withHeader, headers, locationColumnValue):
    # Error messages -------------------------------------------------

    # Get minimum expected number of columns -------------------------------------------------

    minColumns = 3  # 3 columns for loc1, lat1, long1

    # Check location columns for string values -------------------------------------------------

    encodingValue = "utf-8"
    IO_csv_util.get_columnNumber_from_headerValue(headers, locationColumnValue, inputFilename)
    if not inputIsCoNLL:
        if len(locationColumnValue) > 0:
            # check that location column is a column of strings
            if location_column_checker(inputFilename, locationColumnValue, encodingValue) is False:
                return False

    else:
        if len(locationColumnValue) == 0:
            if not inputIsCoNLL:
                logger.info("option selection error, no location column value")
                return False

    # set default values --------------------------------------------------------------------------------------------------
    numColumns = len(headers)
    inputIsGeocoded = True
    if inputIsGeocoded:
        if numColumns >= minColumns:
            for i in range(len(headers)):
                if locationColumnValue == headers[i]:
                    location_num = i
                    break
                if location_num + 2 >= numColumns:
                    logger.info("input file warning, msg Float")
                    return False
        else:
            logger.info("Input file warning, message = two few colms for geocoded.")
            return False
        # Check if the inputfile is REALLY geocoded or not for the two sets of locations
        if not geocoded_checker(
            numColumns,
            minColumns,
            headers,
            locationColumnValue,
            inputFilename,
            encodingValue,
        ):
            return False
    return True


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

    return (
        inputIsCoNLL,
        inputIsGeocoded,
        withHeader,
        headers,
        datePresent,
        filenamePositionInCoNLLTable,
    )
