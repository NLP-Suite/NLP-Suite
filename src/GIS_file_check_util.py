import tkinter.messagebox as mb
import IO_csv_util
import IO_CoNLL_util

# returns False if error found
def geocoded_checker(numColumns, minColumns, headers, locationColumnValue, inputFilename, encodingValue):
    # check that the file REALLY contains geocoded data, with float values for lat and long
    # location_num=0 #RF
    for i in range(len(headers)):
        if locationColumnValue == headers[i]:
            location_num = i
            break
    latitude_name = headers[location_num + 1]
    longitude_name = headers[location_num + 2]
    try:
        dt = pd.read_csv(inputFilename, encoding=encodingValue)
    except:
        mb.showerror(title='Input file error', message="There was an error reading the input file\n" + str(
            inputFilename) + "\nwith geocoded input. Most likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.")
        return False

    check1 = True
    check2 = True
    for x in dt[latitude_name]:
        if isinstance(x, float) is not True:
            check1 = False
            break
        elif x > 90 or x < -90:
            check1 = False
            break
    for y in dt[longitude_name]:
        if isinstance(y, float) is not True:
            check2 = False
            break
        elif y > 180 or y < -180:
            check1 = False
            break

    if check1 == False or check2 == False:
        mb.showerror(title='Input file error',
                     message="You have ticked the geocoded checkbox.\n\nBut the input file does not have two consecutive columns of float type data (in the forms of: columns of latitude in range [-90, 90] and longitude in range [-180, 180]) right after your selected location field, " + str(
                         locationColumnValue) + ".\n\nPlease, check your input file and/or deselect the geocoded option and try again.")
        return False
    else:
        return True


# Checks that the location column is a column of strings
def location_column_checker(inputFilename, locationColumnValue, encodingValue):
    try:
        dt = pd.read_csv(inputFilename, encoding=encodingValue)
    except:
        mb.showerror(title='Input file error', message="There was an error reading the input file\n" + str(
            inputFilename) + "\nwith geocoded input. Most likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.")
        return False
    check1 = True
    # convert np.nan (in float form) to an empty string
    dt[locationColumnValue] = dt[locationColumnValue].replace(np.nan, '')
    for x in dt[locationColumnValue]:
        if isinstance(x, str) is not True:
            check1 = False
            break
    if check1 == False:
        mb.showerror(title='Input file error',
                     message="The location column you selected, " + locationColumnValue + ", is not a column of strings, as expected for the column containing location names.\n\nPlease, reselect your location column and try again.")
        return False
    else:
        return True


# def restrictions_checker(inputFilename,inputIsCoNLL,inputIsGeocoded,numColumns,withHeader,headers,computeDistance_var,baselineLocation,locationColumnValue,locationColumnValue2,encodingValue):
def restrictions_checker(inputFilename, inputIsCoNLL, withHeader, headers,
                         locationColumnValue):
    # Error messages -------------------------------------------------

    msgSelect2SetsOfLocations = "select the columns that contain location values for the two sets of locations for which a distance is computed."
    msgNolocationColumnValue = "You need to specify the column that contains location values.\n\nPlease, click on the menu button 'Select the column containing location names' and try again."
    msgFloat = "The location column you selected does not have two consecutive columns of float-type data (latitude and longitude) right after it. \n\nPlease, reselect the location column and try again."

    # Get minimum expected number of columns -------------------------------------------------

    minColumns = 3  # 3 columns for loc1, lat1, long1

    # Check location columns for string values -------------------------------------------------

    encodingValue = 'utf-8'
    locationColumnNumber=IO_csv_util.get_columnNumber_from_headerValue(headers,locationColumnValue)
    if inputIsCoNLL == False:
        if len(locationColumnValue) > 0:
            # check that location column is a column of strings
            if location_column_checker(inputFilename, locationColumnValue, encodingValue) is False:
                return False

    else:
        if len(locationColumnValue) == 0:
            if inputIsCoNLL == False:
                mb.showerror(title='Option selection error', message=msgNolocationColumnValue)
                return False

    # set default values --------------------------------------------------------------------------------------------------
    inputIsGeocoded = True
    if inputIsGeocoded == True:
        if numColumns >= minColumns:
            for i in range(len(headers)):
                if locationColumnValue == headers[i]:
                    location_num = i
                    break
                if location_num + 2 >= numColumns:
                    mb.showerror(title='Input file warning', message=msgFloat)
                    return False
        else:
            mb.showerror(title='Input file warning', message=msgTooFewColumnsForGeocoded)
            return False
        # Check if the inputfile is REALLY geocoded or not for the two sets of locations
        if geocoded_checker(numColumns, minColumns, headers, locationColumnValue, inputFilename, encodingValue) == False:
            return False
    return True


def CoNLL_checker(inputFilename):
    if IO_CoNLL_util.check_CoNLL(inputFilename,True):
        inputIsCoNLL = True
        inputIsGeocoded = False
    else:
        inputIsCoNLL = False
    headers = IO_csv_util.get_csvfile_headers(inputFilename, False)
    if 'Date' in headers:
        datePresent = True
    else:
        datePresent = False
    if 'Latitude' in headers and 'Longitude' in headers:
        inputIsGeocoded = True
    else:
        inputIsGeocoded = False
    withHeader=True
    filenamePositionInCoNLLTable=11

    return inputIsCoNLL, inputIsGeocoded, withHeader, headers, datePresent, filenamePositionInCoNLLTable
