# INPUT The function computeDistance assumes that:
#   the location name is always the column of the FIRST location name followed by its latitude and longitude
#       followed by the SECOND location name followed by its latitude and longitude
#   longitude is always in the next column of latitude 1 and 2

# geodesic distance
# Geopy can calculate geodesic distance between two points using
#   the geodesic distance
#   the great-circle distance

# The geodesic distance (also called great circle distance) is the shortest distance on the surface of an ellipsoidal model of the earth.
# There are multiple popular ellipsoidal models.
#   Which one will be the most accurate depends on where your points are located on the earth.
#   The default is the WGS-84 ellipsoid, which is the most globally accurate.
#   geopy includes a few other models in the distance.ELLIPSOIDS dictionary.


import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"GIS_distance_util",['tkinter','csv','pandas','geopy'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import pandas as pd
import csv

from geopy import distance

from geopy.distance import great_circle

# from geopy.extra.rate_limiter import RateLimiter

import GIS_location_util
import GIS_geocode_util
import IO_files_util
import IO_user_interface_util
import charts_util
import IO_csv_util
import IO_internet_util

def createCharts(distanceoutputFilename, outputDir, filesToOpen, baselineLocation=''):

    xlsxFilename=distanceoutputFilename
    yAxis = 'Geodesic distance in miles'
    xAxis = ''
    if baselineLocation=='':
        chartTitle = 'Geodesic distance in miles'
    else:
        chartTitle = 'Geodesic distance in miles from ' + baselineLocation
    columns_to_be_plotted_xAxis=[]
    columns_to_be_plotted_yAxis=[[3,6]]
    chart_outputFilename = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                              '',
                                              chartPackage=chartPackage,
                                              chart_type_list=["bar"],
                                              chart_title=chartTitle,
                                              column_xAxis_label_var=xAxis,
                                              hover_info_column_list=[],
                                              count_var = 0,
                                              column_yAxis_label_var=yAxis)

    xlsxFilename = chart_outputFilename.replace('.xlsx','_Geodesic.xlsx')
    try:
        os.rename(chart_outputFilename,xlsxFilename)
    except:
        # the file already exists and must be removed
        if os.path.isfile(xlsxFilename):
            os.remove(xlsxFilename)
        os.rename(chart_outputFilename,xlsxFilename)
    filesToOpen.append(xlsxFilename)

    xlsxFilename=distanceoutputFilename
    yAxis = 'Great circle distance in miles'
    xAxis = ''
    if baselineLocation=='':
        chartTitle = 'Great circle distance in miles'
    else:
        chartTitle = 'Great circle distance in miles from ' + baselineLocation
    columns_to_be_plotted_xAxis=[]
    columns_to_be_plotted_yAxis=[[3,8]]
    chart_outputFilename = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                              '',
                                              chartPackage=chartPackage,
                                              chart_type_list=["bar"],
                                              chart_title=chartTitle,
                                              column_xAxis_label_var=xAxis,
                                              hover_info_column_list=[],
                                              count_var = 0,
                                              column_yAxis_label_var=yAxis)
    xlsxFilename = chart_outputFilename.replace('.xlsx','_GreatCircle.xlsx')
    try:
        os.rename(chart_outputFilename,xlsxFilename)
    except:
        # the file already exists and must be removed
        if os.path.isfile(xlsxFilename):
            os.remove(xlsxFilename)
        os.rename(chart_outputFilename,xlsxFilename)
    filesToOpen.append(xlsxFilename)
    return filesToOpen

def computePairwiseDistances(window,inputFilename,outputDir,createCharts, headers,locationColumnNumber,locationColumnNumber2,locationColumnName,locationColumnName2,distinctValues,geolocator,geocoder,inputIsCoNLL,datePresent,encodingValue):
    filesToOpen=[]
    currList=[]
    startTime=IO_user_interface_util.timed_alert(window, 2000, 'Analysis start', 'Started running GIS distance at',
                                                 True, '', True, '', True)
    if distinctValues==True:
        distanceoutputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', locationColumnName, locationColumnName2, 'DISTINCT', False, True)
    else:
        distanceoutputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', locationColumnName, locationColumnName2, 'ALL', False, True)
    filesToOpen.append(distanceoutputFilename)

    #with open(distanceoutputFilename, 'w',newline='',encoding="utf-8",errors='ignore') as csvfile:
    #latin-1
    with open(inputFilename, 'r',newline='',encoding=encodingValue,errors='ignore') as inputFile, open(distanceoutputFilename, 'w',newline='',encoding=encodingValue,errors='ignore') as outputFile:
        geowriter = csv.writer(outputFile)
        try:
            dt = pd.read_csv(inputFile,encoding=encodingValue, error_bad_lines=False)
        except:
            mb.showerror(title='Input file error', message="There was an error in the function 'Compute GIS distance' reading the input file\n" + str(inputFile) + "\nMost likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.")
            filesToOpen.append('')
            return filesToOpen
        geowriter.writerow(['Location 1','Latitude 1','Longitude 1','Location 2','Latitude 2','Longitude 2','Geodesic distance in miles','Geodesic distance in Km','Great circle distance in miles','Great circle distance in Km'])
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename, encodingValue)
        for index, row in dt.iterrows():
            currRecord=str(index) + "/" + str(nRecords)
            currentLocation1=str(row[locationColumnNumber])
            currentLocation2=str(row[locationColumnNumber2])
            if (str(currentLocation1)!='' and str(currentLocation1)!='nan' and str(currentLocation2)!='' and str(currentLocation2)!='nan'): #nan Not A Numeric value SHOULD NOT BE NECESSARY!!!
                #nan Not A Numeric value
                if str(row[locationColumnNumber+1])=='' or str(row[locationColumnNumber+2])=='' or str(row[locationColumnNumber+1])=='nan' or str(row[locationColumnNumber+2])=='nan':
                    print(currRecord,"     WAYPOINTS NOT NUMERIC (nan) ",currentLocation1)
                    waypoints1=''
                    waypoints2=''
                elif str(row[locationColumnNumber+4])=='' or str(row[locationColumnNumber+5])=='' or str(row[locationColumnNumber+4])=='nan' or str(row[locationColumnNumber+5])=='nan':
                    print(currRecord,"     WAYPOINTS NOT NUMERIC (nan) ",currentLocation2)
                    waypoints1=''
                    waypoints2=''
                else:
                    try:
                        float(row[locationColumnNumber+1])
                    except:
                        mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+1) + " (" + headers[locationColumnNumber+2] + ") of your input csv file does not contain proper Latitude values for the first location.\n\nPlease, check your selected 'Column containing location names' and/or input csv filename and try again.")
                        filesToOpen.append('')
                        return filesToOpen
                    try:
                        float(row[locationColumnNumber+2])
                    except:
                        mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+2) + " (" + headers[locationColumnNumber+3] + ") of your input csv file does not contain proper Longitude values for the first location.\n\nPlease, check your selected 'Column containing location names' and/or input csv filename and try again.")
                        filesToOpen.append('')
                        return filesToOpen
                    try:
                        float(row[locationColumnNumber+4])
                    except:
                        mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+4) + " (" + headers[locationColumnNumber+5] +") of your input csv file does not contain proper Latitude values for the second location.\n\nPlease, check your selected 'Select the second column containing location names (for distances)' and/or input csv filename and try again.")
                        filesToOpen.append('')
                        return filesToOpen
                    try:
                        float(row[locationColumnNumber+5])
                    except:
                        mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+5) + " (" + headers[locationColumnNumber+6] +") of your input csv file does not contain proper Longitude values for the second location.\n\nPlease, check your selected 'Select the second column containing location names (for distances)' and/or input csv filename and try again.")
                        filesToOpen.append('')
                        return filesToOpen
                    waypoints1=(row[locationColumnNumber+1], row[locationColumnNumber+2])
                    waypoints2=(row[locationColumnNumber2+1], row[locationColumnNumber2+2])
                    # print(currRecord, currentLocation1, currentLocation2, str(row[locationColumnNumber+1]),str(row[locationColumnNumber+2]))
                    if (distinctValues==False) or ([waypoints1,waypoints2] not in currList):
                        currList.append([waypoints1,waypoints2])
                        distMiles=distance.distance(waypoints1, waypoints2).miles
                        distKm=distance.distance(waypoints1, waypoints2).km
                        GCdistMiles=great_circle(waypoints1, waypoints2).miles
                        GCdistKm=great_circle(waypoints1, waypoints2).km
                        # geowriter.writerow([row[locationColumnNumber], row[locationColumnNumber2],row[locationColumnNumber+1],row[locationColumnNumber+2],row[locationColumnNumber2+1],row[locationColumnNumber2+2],distMiles,distKm,GCdistMiles,GCdistKm])
                        geowriter.writerow([row[locationColumnNumber],str(waypoints1[0]),str(waypoints1[1]),row[locationColumnNumber2],str(waypoints2[0]),str(waypoints2[1]),distMiles,distKm,GCdistMiles,GCdistKm])
    outputFile.close()
    filesToOpen.append(distanceoutputFilename)

    if createCharts == True:
        filesToOpen = createCharts(distanceoutputFilename,outputDir,filesToOpen)
        # if len(chart_outputFilename) > 0:
        # 	filesToOpen.append(chart_outputFilename)


    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running GIS distance at', True, '', True, startTime, True)
    return filesToOpen

# The function computes the distance between a pre-selected city and all cities in a list
#   distances are calculated in miles and Km
#   distances are calculated using both geodesic and Great Circle algorithms
#   If the list contains previously geocoded values the function will NOT geocode the values
#       otherwise it will geocode the location names

def computeDistancesFromSpecificLocation(window,inputFilename,outputDir,createCharts, geolocator,geocoder,InputIsGeocoded,baselineLocation,headers,locationColumnNumber,locationColumnName,distinctValues,withHeader,inputIsCoNLL,split_locations,datePresent,filenamePositionInCoNLLTable,encodingValue):
    currList=[]
    filesToOpen=[]
    startTime=IO_user_interface_util.timed_alert(window, 2000, 'Analysis start', 'Started running GIS distance from ' + baselineLocation + ' at',
                                                 True, '', True, '', True)
    if distinctValues==True:
        distanceoutputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', baselineLocation, locationColumnName, 'DISTINCT', False, True)
    else:
        distanceoutputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', locationColumnName, baselineLocation, 'ALL', False, True)
    filesToOpen.append(distanceoutputFilename)

    #for baselineLocation locationColumnNumber inputFilename
    baseLocationLat = 0
    baseLocationLon = 0

    # not geocoded input
    if InputIsGeocoded == False:
        import IO_internet_util
        if not IO_internet_util.check_internet_availability_warning('GIS geocoder'):
            return
        startTime=IO_user_interface_util.timed_alert(window, 2000, 'Analysis start', 'Started running GIS geocoder at',
                                                     True, '', True, '', True)
        geoName='geo-'+str(geocoder[:3])
        geocodedLocationsoutputFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', geoName, locationColumnName, '', '', False, True)
        locationsNotFoundFilename=IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', geoName, 'Not-Found', locationColumnName, '', False, True)

        outputCsvLocationsOnly=''
        if inputIsCoNLL==True:
            outputCsvLocationsOnly=IO_files_util.generate_output_file_name(inputFilename,'', outputDir, '.csv', 'GIS', 'NER_locations', '', '', '', False, True)
            locations = GIS_location_util.extract_NER_locations(inputFilename,filenamePositionInCoNLLTable,encodingValue,split_locations,datePresent)
        else:
            locations = GIS_location_util.extract_csvFile_locations(GUI_util.window,inputFilename,withHeader,locationColumnNumber,encodingValue)

        if locations==None or len(locations)==0:
            filesToOpen.append('')
            return filesToOpen
        geocodedLocationsoutputFilename, locationsNotFoundFilename = GIS_geocode_util.geocode(window,locations,inputFilename, outputDir, locationColumnName,geocoder,'',encodingValue)

        try:
            dt = pd.read_csv(geocodedLocationsoutputFilename,encoding=encodingValue, error_bad_lines=False)
        except:
            mb.showerror(title='File error', message="There was an error in the function 'Compute GIS distance from specific location' reading the output file\n" + str(geocodedLocationsoutputFilename) + "\nwith non geocoded input. Most likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.")
            filesToOpen.append('')
            return filesToOpen

        filesToOpen.append(geocodedLocationsoutputFilename)
        filesToOpen.append(locationsNotFoundFilename)

        locationColumnNumber = 0
        location = GIS_geocode_util.nominatim_geocode(geolocator,baselineLocation)
        if location is None:
            mb.showerror(title='Input error', message="The baseline location cannot be geocoded. \n\nPlease, enter a new baseline location and try again.")
            filesToOpen.append('')
            return filesToOpen
        waypoints1 = [location.latitude, location.longitude] #, location.address]
    # geocoded input
    else:
        try:
            dt = pd.read_csv(inputFilename,encoding=encodingValue, error_bad_lines=False)
        except:
            mb.showerror(title='Input file error', message="There was an error in the function 'Compute GIS distance from specific location' reading the input file\n" + str(inputFilename) + "\nwith geocoded input. Most likely, the error is due to an encoding error. Your current encoding value is " + encodingValue + ".\n\nSelect a different encoding value and try again.")
            filesToOpen.append('')
            return filesToOpen
        if geocoder=='Nominatim':
            location = GIS_geocode_util.nominatim_geocode(geolocator,baselineLocation)
        else:
            location = GIS_geocode_util.google_geocode(geolocator,baselineLocation)
        if location is None:
            mb.showerror(title='Input error', message="The baseline location cannot be geocoded. \n\nPlease, enter a new baseline location and try again.")
            filesToOpen.append('')
            return filesToOpen
        waypoints1 = [location.latitude, location.longitude] #, location.address]

    # with open(inputFilename, 'r',newline='',encoding=encodingValue,errors='ignore') as inputFile, open(distanceoutputFilename, 'w',newline='',encoding=encodingValue,errors='ignore') as outputFile:
    with open(distanceoutputFilename, 'w',newline='',encoding=encodingValue,errors='ignore') as outputFile:
        geowriter = csv.writer(outputFile)
        geowriter.writerow(['Location 1','Latitude 1','Longitude 1','Location 2','Latitude 2','Longitude 2','Geodesic distance in miles','Geodesic distance in Km','Great circle distance in miles','Great circle distance in Km'])
        # loop through for the waypoints of the second location
        for index, row in dt.iterrows():
            currentLocation=str(row[locationColumnNumber])
            nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename, encodingValue)
            currRecord = str(index) + "/" + str(nRecords)
            if currentLocation!='' and currentLocation!='nan': #nan Not A Numeric value SHOULD NOT BE NECESSARY!!!
                try:
                    float(row[locationColumnNumber+1])
                except:
                    mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+1) + " (" + headers[locationColumnNumber+2] + ") of your input csv file does not contain proper Latitude values for your location.\n\nPlease, check your selected 'Column containing location names' and/or input csv filename and try again.")
                    filesToOpen.append('')
                    return filesToOpen
                try:
                    float(row[locationColumnNumber+2])
                except:
                    mb.showerror(title='Input file error', message="Column number " + str(locationColumnNumber+2) + " (" + headers[locationColumnNumber+3] + ") of your input csv file does not contain proper Longitute values for your location.\n\nPlease, check your selected 'Column containing location names' and/or input csv filename and try again.")
                    filesToOpen.append('')
                    return filesToOpen

                #nan Not A Numeric value
                if str(row[locationColumnNumber+1])=='' or str(row[locationColumnNumber+2])=='' or str(row[locationColumnNumber+1])=='nan' or str(row[locationColumnNumber+2])=='nan':
                    print(currRecord,"     WAYPOINTS NOT NUMERIC (nan) ",currentLocation)
                    waypoints2=''
                else:
                    waypoints2=[row[locationColumnNumber+1],row[locationColumnNumber+2]]
            else:
                print(currRecord,"     CURRENT LOCATION IS BLANK")
                waypoints2=''

            if (waypoints2!=''):
                if (distinctValues==False) or ([waypoints1,waypoints2] not in currList) and (baselineLocation!=currentLocation):
                    currList.append([waypoints1,waypoints2])
                    distMiles=distance.distance(waypoints1, waypoints2).miles
                    distKm=distance.distance(waypoints1, waypoints2).km
                    GCdistMiles=great_circle(waypoints1, waypoints2).miles
                    GCdistKm=great_circle(waypoints1, waypoints2).km
                    geowriter.writerow([baselineLocation,str(waypoints1[0]),str(waypoints1[1]),currentLocation,str(waypoints2[0]),str(waypoints2[1]),distMiles,distKm,GCdistMiles,GCdistKm])
    outputFile.close()
    filesToOpen.append(distanceoutputFilename)

    if createCharts == True:
        filesToOpen = createCharts(distanceoutputFilename,outputDir,filesToOpen,baselineLocation)
        # if len(chart_outputFilename) > 0:
        # 	filesToOpen.append(chart_outputFilename)

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running GIS distance at', True, '', True, startTime,True)
    return filesToOpen
