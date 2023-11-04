import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"GIS_folium_map_util",['os','pandas','folium','fsspec'])==False:
    sys.exit(0)

import pandas as pd
import folium
from folium import plugins
from folium.plugins import HeatMap

# pin map
#   https://python-visualization.github.io/folium/latest/getting_started.html
# heatmap
#   https://www.kaggle.com/code/daveianhickey/how-to-folium-for-maps-heatmaps-time-data

def run(inputFilename, folium_pinmap_outputFilename, folium_heatmap_outputFilename):

    filesToOpen=[]

    GISLocation = pd.read_csv(inputFilename)

# produce pin map --------------------------------------------------------------------------

    locationsData = GISLocation[['Latitude', 'Longitude']]
    # locationsData

    #converting lattitude & longitude coordinates in to tuple --> add as coordinates column

    locationsData['coordinates'] = list(zip(locationsData.Latitude, locationsData.Longitude))
    # locationsData

    #making coordinates into list
    coordinatsList = locationsData['coordinates'].tolist()

    # define the object
    # zoom_start defines how close you want to get to the map, entire world for zoom_start = 0, or very close for higher values of zoom_start
    mappingLocation = folium.Map(location= [GISLocation['Latitude'][0], GISLocation['Longitude'][0]], zoom_start = 2)

    for i in GISLocation.index:
        if pd.notnull(GISLocation['Latitude'][i]):
            folium.CircleMarker([GISLocation['Latitude'][i], GISLocation['Longitude'][i]],
                                 radius=3, color = '#CD3181',
                                 fill_color = '#CD3181').add_to(mappingLocation)
            folium.Marker(location=[GISLocation['Latitude'][i], GISLocation['Longitude'][i]],
                tooltip="Click me!",
                popup=GISLocation['Location'][i],
                icon=folium.Icon(color="red")).add_to(mappingLocation)
    mappingLocation.save(folium_pinmap_outputFilename)
    mappingLocation
    filesToOpen.append(folium_pinmap_outputFilename)

# produce heat map --------------------------------------------------------------------------

    heatmap = folium.Map(location=[51.5074, 0.1278],
                        zoom_start = 3)

    # Ensure you're handing it floats
    GISLocation['Latitude'] = GISLocation['Latitude'].astype(float)
    GISLocation['Longitude'] = GISLocation['Longitude'].astype(float)

    # Filter the DF for rows, then columns, then remove NaNs
    # heat_df = GISLocation[GISLocation['Speed_limit']=='40'] # Reducing data size so it runs faster
    # heat_df = GISLocation[GISLocation['Year']=='2007'] # Reducing data size so it runs faster
    GISLocation = GISLocation[['Latitude', 'Longitude']]
    GISLocation = GISLocation.dropna(axis=0, subset=['Latitude','Longitude'])

    # List comprehension to make out list of lists
    GISLocation = [[row['Latitude'],row['Longitude']] for index, row in GISLocation.iterrows()]

    # Plot it on the map
    HeatMap(GISLocation).add_to(heatmap)

    # Display the map
    heatmap

    heatmap.save(folium_heatmap_outputFilename)
    filesToOpen.append(folium_heatmap_outputFilename)
    return filesToOpen
