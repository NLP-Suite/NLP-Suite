
#2. Google Maps Style Heat Map

#Import modules

import pandas as pd
import geopandas
import gmaps
import shapely
import folium
from shapely.geometry import Point
import geocoder
import sys
'geopandas' in sys.modules
import googlemaps
from googlemaps import Client



#insert google maps key
##need to insert googlemaps api key " "
gmaps = googlemaps.Client(key=" ") #AIzaSyApsnv-diA8hrDMrfEEp6Ci6tfUYN7POzg <- This is Denny's key, but when integrated, need to call distinct key

#importing Location file produced (below is my local address)
lynchLocation = pd.read_csv('/Users/taehyung/Desktop/NLP/Lynching_text/textToMap_output/NLP_GIS_combinedFinal1-5_LOCATIONS_geo-Nom_Location.csv')
lynchLocation

#need to change the column name, because you cannot extract latitude & longitude column at the same time for some reason.
# ex. [lynchLocation['Latitude', 'Longitude']] doesn't work

lynchLocation.rename(columns={'Latitude':'lat',
                          'Longitude':'lng'}, 
                 inplace=True)

lynchLocation

#extracting lat & lng
locationsData = lynchLocation[['lat', 'lng']]
locationsData

#converting lattitude & longitude coordinates in to tuple --> add as coordinates column
locationsData['coordinates'] = list(zip(locationsData.lat, locationsData.lng))
locationsData

#making coordinates into list
coordinatsList = locationsData['coordinates'].tolist()
coordinatsList


import gmaps.datasets
gmaps.configure(api_key='') #<- insert distinct API Key. My key is: AIzaSyApsnv-diA8hrDMrfEEp6Ci6tfUYN7POzg

fig = gmaps.figure()
heatmap_layer = gmaps.heatmap_layer(
    lynchLocation[['lat', 'lng']],
    max_intensity=40, point_radius=3.0
)
fig.add_layer(heatmap_layer)
fig
