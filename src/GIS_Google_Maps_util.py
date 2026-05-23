# util to create google maps from table data
# jack hester September 2020

"""
Use the Google Maps API to create a heatmap of locations
Gathers the points of the location in lat, long format then puts them into the template file
Saves that template file with the addition to user-specified file name/location\
Template file should be located in the lib folder
"""
import GUI_IO_util
import GIS_geocode_util
import os
import reminders_util
import GIS_pipeline_util


# gathers the template html/js file to build a heat map,
# inserts correct javascript containing all of the points to plot on heatmap_template
# gmaps_list is a list of lat/long values to be written in the java script html output file
# then saves a new file that contains the html/js to display the heatmap
def create_google_heatmap(window, outputFilename, gmaps_list):
    api_key = GIS_pipeline_util.getGoogleAPIkey(window, 'Google-Maps-API_config.csv')
    # strip whitespace/newline that may be present
    if api_key:
        api_key = api_key.strip()
    if api_key is None or len(api_key) < 5:
        import tkinter.messagebox as mb
        mb.showwarning(title='Google Maps API key error',
                       message="The expected API key required by Google Maps is missing in the config file Google-Maps-API_config.csv.\n\nPlease, make sure to obtain the key, enter it, and save it correctly in the Google-Maps-API_config.csv file and try again.\n\nNo Google Maps heatmap can be produced.")
        return

    print(f"  Google Maps heatmap: {len(gmaps_list)} data points to write to {outputFilename}")

    js_template_loc = GUI_IO_util.Google_heatmaps_libPath + os.sep + "heatmap_template.html"
    with open(js_template_loc, 'r') as open_js:
        js_template = open_js.read()

    split_marker = "//DO NOT REMOVE! PROGRAM INSERTS THE CORRECT JS HERE!"
    js_to_write = js_template.split(split_marker)
    if len(js_to_write) != 2:
        print(f"  WARNING: heatmap_template.html does not contain the expected marker comment. "
              f"Split produced {len(js_to_write)} parts instead of 2.")
        return

    # build the data-point string
    s = ""
    for item in gmaps_list:
        s += str(item + "\n")

    with open(outputFilename, 'w', encoding='utf-8') as js_output_file:
        js_output_file.write(js_to_write[0].replace("<YOUR API KEY HERE>", api_key))
        js_output_file.write(s)
        js_output_file.write(js_to_write[1])

    # verify the output file was written correctly
    try:
        with open(outputFilename, 'r', encoding='utf-8') as verify_f:
            content = verify_f.read()
        if 'new google.maps.LatLng(' in content:
            count = content.count('new google.maps.LatLng(')
            print(f"  Google Maps heatmap: VERIFIED {count} LatLng points in output file.")
        else:
            print(f"  WARNING: Google Maps heatmap output file contains NO LatLng data points!")
        if api_key in content:
            print(f"  Google Maps heatmap: API key correctly inserted.")
        else:
            print(f"  WARNING: API key NOT found in output file!")
    except Exception as e:
        print(f"  WARNING: Could not verify heatmap output: {e}")

    return

# generate the javascript to be inserted into the template file to create the map
# returns lines with lat long pairs in google maps api syntax
# outputFilename where to save heatmap html file
# locations is either a list of locations or a list of lat long lists
# api_key is your google api key
# if latLongList is true, then the locations do not need to be generated,
# must provide geocoder if points are locations rather than lat longs
# if lat longs are provided, it should be via a nested list, i.e. [[lat1, long1], [lat2, long2], ...]
# otherwise it assumes the item provided is a list of locations (as strings)
def create_js(window, outputFilename, locations, geocoder, latLongList):
    gmaps_list = []
    if not latLongList:
        latLongList = []
        for l in locations:
            returned_loc = GIS_geocode_util.nominatim_geocode(geocoder, l)
            latLongList.append([returned_loc.latitude, returned_loc.longitude])
    else:
        latLongList = locations
    print(f"  create_js: {len(latLongList)} coordinate pairs to convert")
    for item in latLongList:
        gmaps_str = ''.join(["new google.maps.LatLng(",str(item[0]),", ",str(item[1]),"),"])
        gmaps_list.append(gmaps_str)
    print(f"  create_js: {len(gmaps_list)} LatLng strings generated")
    if len(gmaps_list) > 0:
        print(f"  create_js: first entry = {gmaps_list[0]}")
    create_google_heatmap(window, outputFilename, gmaps_list)
    head, scriptName = os.path.split(os.path.basename(__file__))
    reminders_util.checkReminder(scriptName,
                            reminders_util.title_options_Google_API,
                            reminders_util.message_Google_API,
                            True)

