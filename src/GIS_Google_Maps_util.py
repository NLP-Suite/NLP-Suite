# util to create google maps from table data
# jack hester September 2020

"""
Use the Google Maps API to create a heatmap of locations
Gathers the points of the location in lat, long format then puts them into the template file
Saves that template file with the addition to user-specified file name/location\
Template file should be located in the lib folder
"""
import GUI_IO_util
import IO_files_util
import GIS_geocode_util
import os
import reminders_util
import GIS_pipeline_util


# gathers the template html/js file to build a heat map,
# inserts correct javascript containing all of the points to plot on heatmap_template
# gmaps_list is a list of lat/long values to be written in the java script html output file
# then saves a new file that contains the html/js to display the heatmap
def create_google_heatmap(output_filename, gmaps_list):
    api_key = GIS_pipeline_util.getGoogleAPIkey('Google_Maps_API_config.csv')
    if api_key == '' or api_key == None :
        return

    js_template_loc = GUI_IO_util.Google_heatmaps_libPath + os.sep + "heatmap_template.html"
    open_js = open(js_template_loc, 'r')
    js_contents = open_js.readlines()
    js_template = "".join(js_contents)
    open_js.close()

    js_to_write = js_template.split("//DO NOT REMOVE! PROGRAM INSERTS THE CORRECT JS HERE!")
    #js_to_write.insert(1,js_to_insert)
    s = ""
    for item in gmaps_list:
        s += str(item+"\n")
    js_output_file = open(output_filename, 'w+')
    js_output_file.write(js_to_write[0].replace("<YOUR API KEY HERE>",api_key))
    js_output_file.write(s)
    js_output_file.write(js_to_write[1])
    js_output_file.close()
    return

# generate the javascript to be inserted into the template file to create the map
# returns lines with lat long pairs in google maps api syntax
# output_filename where to save heatmap html file
# locations is either a list of locations or a list of lat long lists
# api_key is your google api key
# if latLongList is true, then the locations do not need to be generated,
# must provide geocoder if points are locations rather than lat longs
# if lat longs are provided, it should be via a nested list, i.e. [[lat1, long1], [lat2, long2], ...]
# otherwise it assumes the item provided is a list of locations (as strings)
def create_js(output_filename, locations, geocoder, latLongList):
    gmaps_list = []
    if not latLongList:
        latLongList = []
        for l in locations:
            returned_loc = GIS_geocode_util.nominatim_geocode(geocoder, l)
            latLongList.append([returned_loc.latitude, returned_loc.longitude])
    else:
        latLongList = locations
    for item in latLongList:
        gmaps_str = ''.join(["new google.maps.LatLng(",str(item[0]),", ",str(item[1]),"),"])
        gmaps_list.append(gmaps_str)
        # gmaps_list geocoded values
    create_google_heatmap(output_filename, gmaps_list)
    config_filename = 'GIS_config.csv'
    reminders_util.checkReminder(config_filename,
                            reminders_util.title_options_Google_API,
                            reminders_util.message_Google_API,
                            True)

