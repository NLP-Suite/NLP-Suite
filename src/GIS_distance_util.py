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

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS_distance_util",['tkinter','csv','pandas','geopy'])==False:
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

def createCharts(distanceoutputFilename, outputDir, filesToOpen, chartPackage, dataTransformation, baselineLocation=''):

    xlsxFilename=distanceoutputFilename
    yAxis = 'Geodesic distance in miles'
    xAxis = ''
    if baselineLocation=='':
        chart_title = 'Geodesic distance in miles'
    else:
        chart_title = 'Geodesic distance in miles from ' + baselineLocation
    columns_to_be_plotted_xAxis=[]
    columns_to_be_plotted_yAxis=[[3,6]]
    outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                              '',
                                              chartPackage=chartPackage,
                                              dataTransformation=dataTransformation,
                                              chart_type_list=["bar"],
                                              chart_title=chart_title,
                                              column_xAxis_label_var=xAxis,
                                              hover_info_column_list=[],
                                              count_var = 0,
                                              column_yAxis_label_var=yAxis)

    xlsxFilename = outputFiles.replace('.xlsx','_Geodesic.xlsx')
    try:
        os.rename(outputFiles,xlsxFilename)
    except:
        # the file already exists and must be removed
        if os.path.isfile(xlsxFilename):
            os.remove(xlsxFilename)
        os.rename(outputFiles,xlsxFilename)
    filesToOpen.append(xlsxFilename)

    xlsxFilename=distanceoutputFilename
    yAxis = 'Great circle distance in miles'
    xAxis = ''
    if baselineLocation=='':
        chart_title = 'Great circle distance in miles'
    else:
        chart_title = 'Great circle distance in miles from ' + baselineLocation
    columns_to_be_plotted_xAxis=[]
    columns_to_be_plotted_yAxis=[[3,8]]
    outputFiles = charts_util.run_all(columns_to_be_plotted_yAxis, xlsxFilename, outputDir,
                                              '',
                                              chartPackage=chartPackage,
                                              dataTransformation=dataTransformation,
                                              chart_type_list=["bar"],
                                              chart_title=chart_title,
                                              column_xAxis_label_var=xAxis,
                                              hover_info_column_list=[],
                                              count_var = 0,
                                              column_yAxis_label_var=yAxis)
    xlsxFilename = outputFiles.replace('.xlsx','_GreatCircle.xlsx')
    try:
        os.rename(outputFiles,xlsxFilename)
    except:
        # the file already exists and must be removed
        if os.path.isfile(xlsxFilename):
            os.remove(xlsxFilename)
        os.rename(outputFiles,xlsxFilename)
    filesToOpen.append(xlsxFilename)
    return filesToOpen


# Distribution of distances across bands: how many location pairs fall in each distance range
# (0, 1-10, 11-20, ..., 101+ miles). This is the useful part of the former standalone
# GIS_distance_plot.py, generalized to any distance output file produced by this tool. Unlike
# the per-pair chart in createCharts, it scales to large corpora (thousands of pairs).
def create_distance_distribution_charts(distanceoutputFilename, outputDir, filesToOpen, encodingValue='utf-8'):
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except Exception as e:
        print('GIS_distance distribution charts: matplotlib/numpy unavailable:', e)
        return filesToOpen
    try:
        df = pd.read_csv(distanceoutputFilename, encoding=encodingValue, on_bad_lines='skip')
    except Exception as e:
        print('GIS_distance distribution charts: cannot read', distanceoutputFilename, e)
        return filesToOpen

    # log-decade bins: geographic distances span orders of magnitude (a few miles to a few
    # thousand), so fixed local bands (the old 0-100 mile scheme) dumped everything into one
    # open-ended catch-all bar. Decade bands read across both local and global scales.
    bins = [0, 1, 10, 100, 1000, 10000, np.inf]
    names = ['<1', '1-10', '10-100', '100-1,000', '1,000-10,000', '10,000+']
    # both algorithms in miles (km is only a unit conversion, same distribution shape)
    for measure in ['Geodesic distance in miles', 'Great circle distance in miles']:
        if measure not in df.columns:
            continue
        try:
            vals = pd.to_numeric(df[measure], errors='coerce').dropna()
            if vals.empty:
                continue
            counts = pd.cut(vals, bins, labels=names, include_lowest=True).value_counts().reindex(names, fill_value=0)
            fig = plt.figure(figsize=(8, 5))
            ax = fig.add_subplot(111)
            counts.plot(kind='bar', ax=ax, color='#4C72B0')
            ax.set_title('Distribution of ' + measure)
            ax.set_xlabel('Distance band (miles)')
            ax.set_ylabel('Frequency (number of location pairs)')
            fig.tight_layout()
            pngFilename = IO_files_util.generate_output_file_name(distanceoutputFilename, '', outputDir, '.png', 'GIS', 'distance-distribution', measure.replace(' ', '-'), '', '', False, True)
            fig.savefig(pngFilename, dpi=100)
            plt.close(fig)
            filesToOpen.append(pngFilename)
        except Exception as e:
            print('GIS_distance distribution chart failed for', measure, ':', e)
    return filesToOpen


# Pairwise (all-pairs) distances: given the DISTINCT geocoded locations in the input file,
#   compute the distance between every combination of two of them. No pre-built two-location
#   file is needed -- the tool forms the pairs itself, reading Location/Latitude/Longitude
#   (and Document) by header name.
#   scope='per-document' -> all-pairs WITHIN each Document (cheap, narrative-aware; needs a
#       Document column, falls back to whole-corpus with a warning if absent);
#   scope='whole-corpus'  -> all-pairs across every distinct location in the file (grows as N^2);
#   scope='*'             -> run both scopes, producing two separate output files.
def computePairwiseDistances(window, inputFilename, outputDir, distinctValues, encodingValue,
                             scope='per-document', chartPackage='No charts', dataTransformation=''):
    import itertools
    filesToOpen = []
    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running GIS pairwise (all-pairs) distances at',
                                                   True, '', True, '', True)
    try:
        df = pd.read_csv(inputFilename, encoding=encodingValue, on_bad_lines='skip')
    except Exception:
        mb.showerror(title='Input file error',
                     message="There was an error in the function 'Compute GIS pairwise distances' reading the input file\n"
                             + str(inputFilename) + "\nMost likely, the error is due to an encoding error. Your current encoding value is "
                             + encodingValue + ".\n\nSelect a different encoding value and try again.")
        return ['']

    locCol = _find_column_by_name(df, 'location')
    latCol = _find_column_by_name(df, 'latitude')
    lonCol = _find_column_by_name(df, 'longitude')
    if latCol is None or lonCol is None:
        mb.showwarning(title='Missing coordinates',
                       message="To compute pairwise distances the input csv must be a GEOCODED file containing Latitude and Longitude columns.\n\nColumns found:\n"
                               + str(list(df.columns)) + "\n\nPlease, geocode your locations first (GIS mapping tool) and select the geocoded csv, then try again.")
        return ['']
    docCol = _find_column_by_name(df, 'document')

    df[latCol] = pd.to_numeric(df[latCol], errors='coerce')
    df[lonCol] = pd.to_numeric(df[lonCol], errors='coerce')
    df = df.dropna(subset=[latCol, lonCol]).reset_index(drop=True)
    if df.empty:
        mb.showwarning(title='No geocoded data',
                       message="The input csv has no rows with valid Latitude/Longitude values.\n\nPlease, geocode your locations first and try again.")
        return ['']

    # which scope(s) to run: '*' runs per-document AND whole-corpus (two output files)
    requested = ['per-document', 'whole-corpus'] if scope == '*' else [scope]
    if docCol is None and 'per-document' in requested:
        mb.showwarning(title='No Document column',
                       message="PER-DOCUMENT pairwise distances need a 'Document' column to group by, which is missing from the input csv.\n\nThe tool will compute WHOLE-CORPUS pairwise distances instead (all-pairs across every location in the file).")
        requested = ['whole-corpus']   # collapse (avoids a duplicate run when '*' was selected)

    def _distinct_locations(sub):
        seen = set()
        out = []
        for _, r in sub.iterrows():
            name = str(r[locCol]) if locCol is not None else ''
            rec = (name, float(r[latCol]), float(r[lonCol]))
            if distinctValues and rec in seen:
                continue
            seen.add(rec)
            out.append(rec)
        return out

    any_output = False
    for one_scope in requested:
        per_document = (one_scope == 'per-document')
        if per_document:
            groups = [(str(g), _distinct_locations(sub)) for g, sub in df.groupby(docCol, sort=False)]
        else:
            groups = [('', _distinct_locations(df))]

        total_pairs = sum(len(locs) * (len(locs) - 1) // 2 for _, locs in groups)
        if total_pairs == 0:
            mb.showwarning(title='No pairs',
                           message="No " + one_scope + " location pairs could be formed.\n\nThis can happen when each document (per-document) or the whole file (whole-corpus) has fewer than two distinct geocoded locations.")
            continue
        if total_pairs > 200000:
            if not mb.askyesno(title='Large computation',
                               message="The " + one_scope + " option will compute " + str(total_pairs) + " location pairs, which may take a long time.\n\nConsider PER-DOCUMENT scope to reduce the number of pairs.\n\nDo you want to continue?"):
                continue

        distanceoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', 'pairwise', one_scope, '', False, True)
        header = ['Location 1', 'Latitude 1', 'Longitude 1', 'Location 2', 'Latitude 2', 'Longitude 2',
                  'Geodesic distance in miles', 'Geodesic distance in Km',
                  'Great circle distance in miles', 'Great circle distance in Km', 'Document']

        with open(distanceoutputFilename, 'w', newline='', encoding=encodingValue, errors='ignore') as outputFile:
            geowriter = csv.writer(outputFile)
            geowriter.writerow(header)
            for gname, locs in groups:
                for (n1, la1, lo1), (n2, la2, lo2) in itertools.combinations(locs, 2):
                    wp1 = (la1, lo1)
                    wp2 = (la2, lo2)
                    distMiles = distance.distance(wp1, wp2).miles
                    distKm = distance.distance(wp1, wp2).km
                    GCdistMiles = great_circle(wp1, wp2).miles
                    GCdistKm = great_circle(wp1, wp2).km
                    geowriter.writerow([n1, la1, lo1, n2, la2, lo2, distMiles, distKm, GCdistMiles, GCdistKm, gname])

        filesToOpen.append(distanceoutputFilename)
        filesToOpen = create_distance_distribution_charts(distanceoutputFilename, outputDir, filesToOpen, encodingValue)
        if chartPackage != 'No charts':
            try:
                filesToOpen = createCharts(distanceoutputFilename, outputDir, filesToOpen, chartPackage, dataTransformation)
            except Exception as e:
                print('GIS_distance createCharts (pairwise) failed:', e)
        any_output = True

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running GIS pairwise (all-pairs) distances at', True, '', True, startTime, True)
    if not any_output:
        return ['']
    return filesToOpen

# The function computes the distance between a pre-selected city and all cities in a list
#   distances are calculated in miles and Km
#   distances are calculated using both geodesic and Great Circle algorithms
#   If the list contains previously geocoded values the function will NOT geocode the values
#       otherwise it will geocode the location names

def computeDistancesFromSpecificLocation(window,inputFilename,outputDir,geolocator,geocoder,InputIsGeocoded,baselineLocation,headers,locationColumnNumber,locationColumnName,distinctValues,withHeader,inputIsCoNLL,split_locations,datePresent,filenamePositionInCoNLLTable,encodingValue,chartPackage='No charts',dataTransformation=''):
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

    # honor the actual file: a csv that already has Latitude/Longitude columns is geocoded,
    # so read its coordinates directly instead of re-geocoding (the CoNLL_checker flag can
    # miss Suite-format geocoded files -> without this they wrongly enter the geocoding branch)
    try:
        _cols = {str(c).strip().lower() for c in pd.read_csv(inputFilename, nrows=0, encoding=encodingValue).columns}
        if any('latitude' in c for c in _cols) and any('longitude' in c for c in _cols):
            InputIsGeocoded = True
    except Exception:
        pass

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
            locations = GIS_location_util.extract_csvFile_locations(GUI_util.window,inputFilename,withHeader,locationColumnNumber,encodingValue,False,0)

        if locations==None or len(locations)==0:
            filesToOpen.append('')
            return filesToOpen
        geocodedLocationsoutputFilename, locationsNotFoundFilename = GIS_geocode_util.geocode(window,locations,inputFilename, outputDir, locationColumnName,geocoder,'',encodingValue)

        try:
            dt = pd.read_csv(geocodedLocationsoutputFilename,encoding=encodingValue, on_bad_lines='skip')
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
            dt = pd.read_csv(inputFilename,encoding=encodingValue, on_bad_lines='skip')
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
        # resolve the location/latitude/longitude columns BY NAME so the function works on the
        # Suite's standard geocoded layout (Location, NER, Latitude, Longitude, ...) and not only
        # on files where latitude/longitude happen to sit right after the location column
        latColName = _find_column_by_name(dt, 'latitude')
        lonColName = _find_column_by_name(dt, 'longitude')
        locColName = _find_column_by_name(dt, 'location')
        if locColName is None:
            locColName = locationColumnName
        if latColName is None or lonColName is None:
            mb.showwarning(title='Missing coordinates',
                           message="To compute distances from a baseline location on a geocoded file, the input csv must contain Latitude and Longitude columns.\n\nColumns found:\n"
                                   + str(list(dt.columns)) + "\n\nPlease, geocode your locations first (GIS mapping tool) and try again.")
            filesToOpen.append('')
            return filesToOpen
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(inputFilename, encodingValue)
        # loop through for the waypoints of the second location
        for index, row in dt.iterrows():
            currentLocation=str(row[locColName]) if locColName in dt.columns else ''
            currRecord = str(index) + "/" + str(nRecords)
            if currentLocation!='' and currentLocation!='nan': #nan Not A Numeric value SHOULD NOT BE NECESSARY!!!
                lat_val = row[latColName]
                lon_val = row[lonColName]
                try:
                    float(lat_val)
                    float(lon_val)
                except (TypeError, ValueError):
                    # rows that failed geocoding have empty/non-numeric coordinates -> skip them
                    print(currRecord,"     WAYPOINTS NOT NUMERIC (nan) ",currentLocation)
                    waypoints2=''
                else:
                    waypoints2=[lat_val,lon_val]
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

    filesToOpen = create_distance_distribution_charts(distanceoutputFilename, outputDir, filesToOpen, encodingValue)
    if chartPackage!='No charts':
        try:
            filesToOpen = createCharts(distanceoutputFilename,outputDir,filesToOpen,chartPackage,dataTransformation,baselineLocation)
        except Exception as e:
            print('GIS_distance createCharts (baseline) failed:', e)

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end', 'Finished running GIS distance at', True, '', True, startTime,True)
    return filesToOpen


def _find_column_by_name(df, wanted):
    # case-insensitive exact match on a header name (wanted is already lower-case)
    for c in df.columns:
        if str(c).strip().lower() == wanted:
            return c
    return None


# Movement distances between CONSECUTIVE geolocated locations.
#   Within each group (Document), the geolocated rows are ordered by Sentence ID and the
#   distance is computed between each location and the NEXT one, i.e. how far the
#   narrative/character moves from one geolocated place to the next.
#   Unlike the pairwise/baseline functions, coordinates are resolved BY HEADER NAME
#   (Location, Latitude, Longitude, Document, Sentence ID), so the function consumes the
#   Suite's standard geocoded output directly (Location, NER, Latitude, Longitude, ...,
#   Sentence ID, ..., Document) without any hand-built two-location file.
def computeConsecutiveDistances(window, inputFilename, outputDir, distinctValues, encodingValue,
                                groupColumn='Document', orderColumn='Sentence ID'):
    filesToOpen = []
    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Analysis start',
                                                   'Started running GIS consecutive (movement) distances at',
                                                   True, '', True, '', True)
    try:
        df = pd.read_csv(inputFilename, encoding=encodingValue, on_bad_lines='skip')
    except Exception:
        mb.showerror(title='Input file error',
                     message="There was an error in the function 'Compute GIS consecutive (movement) distances' reading the input file\n"
                             + str(inputFilename) + "\nMost likely, the error is due to an encoding error. Your current encoding value is "
                             + encodingValue + ".\n\nSelect a different encoding value and try again.")
        return ['']

    locCol = _find_column_by_name(df, 'location')
    latCol = _find_column_by_name(df, 'latitude')
    lonCol = _find_column_by_name(df, 'longitude')
    if latCol is None or lonCol is None:
        mb.showwarning(title='Missing coordinates',
                       message="To compute movement (consecutive-location) distances the input csv must be a GEOCODED file containing Latitude and Longitude columns.\n\nColumns found:\n"
                               + str(list(df.columns)) + "\n\nPlease, geocode your locations first (GIS mapping tool) and select the geocoded csv, then try again.")
        return ['']

    grpCol = _find_column_by_name(df, groupColumn.lower())          # 'document'
    ordCol = _find_column_by_name(df, orderColumn.lower())          # 'sentence id'
    if ordCol is None:
        ordCol = _find_column_by_name(df, 'sentence')               # fall back to Sentence

    # keep only rows with valid numeric coordinates (drops 'Geocoding failed' rows)
    df[latCol] = pd.to_numeric(df[latCol], errors='coerce')
    df[lonCol] = pd.to_numeric(df[lonCol], errors='coerce')
    df = df.dropna(subset=[latCol, lonCol]).reset_index(drop=True)
    if df.empty:
        mb.showwarning(title='No geocoded data',
                       message="The input csv has no rows with valid Latitude/Longitude values.\n\nPlease, geocode your locations first and try again.")
        return ['']

    distanceoutputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', 'GIS', 'distance', 'consecutive', 'movement', '', False, True)

    header = ['Location 1', 'Latitude 1', 'Longitude 1', 'Location 2', 'Latitude 2', 'Longitude 2',
              'Geodesic distance in miles', 'Geodesic distance in Km',
              'Great circle distance in miles', 'Great circle distance in Km',
              'Document', 'From sentence', 'To sentence']

    nWritten = 0
    with open(distanceoutputFilename, 'w', newline='', encoding=encodingValue, errors='ignore') as outputFile:
        geowriter = csv.writer(outputFile)
        geowriter.writerow(header)
        # pair consecutive locations within each Document; without a Document column treat the
        # whole file as a single sequence
        if grpCol is not None:
            group_iter = list(df.groupby(grpCol, sort=False))
        else:
            group_iter = [('', df)]
        for gname, sub in group_iter:
            if ordCol is not None:
                sub = sub.sort_values(by=ordCol, kind='stable')
            sub = sub.reset_index(drop=True)
            for i in range(len(sub) - 1):
                r1 = sub.iloc[i]
                r2 = sub.iloc[i + 1]
                wp1 = (float(r1[latCol]), float(r1[lonCol]))
                wp2 = (float(r2[latCol]), float(r2[lonCol]))
                # skip consecutive mentions at the SAME place (no movement)
                if distinctValues and wp1 == wp2:
                    continue
                loc1 = str(r1[locCol]) if locCol is not None else ''
                loc2 = str(r2[locCol]) if locCol is not None else ''
                fromS = str(r1[ordCol]) if ordCol is not None else ''
                toS = str(r2[ordCol]) if ordCol is not None else ''
                distMiles = distance.distance(wp1, wp2).miles
                distKm = distance.distance(wp1, wp2).km
                GCdistMiles = great_circle(wp1, wp2).miles
                GCdistKm = great_circle(wp1, wp2).km
                geowriter.writerow([loc1, wp1[0], wp1[1], loc2, wp2[0], wp2[1],
                                    distMiles, distKm, GCdistMiles, GCdistKm,
                                    str(gname), fromS, toS])
                nWritten += 1

    IO_user_interface_util.timed_alert(window, 2000, 'Analysis end',
                                       'Finished running GIS consecutive (movement) distances at',
                                       True, '', True, startTime, True)
    if nWritten == 0:
        mb.showwarning(title='No movement',
                       message="No consecutive-location movements were found to measure.\n\nThis can happen if each document has only one geolocated location, or all consecutive locations are identical.")
        return ['']
    filesToOpen.append(distanceoutputFilename)
    filesToOpen = create_distance_distribution_charts(distanceoutputFilename, outputDir, filesToOpen, encodingValue)
    return filesToOpen
