import pandas as pd
import folium


#importing Location file produced

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

#mappingLocation = folium.Map(location= [lynchLocation['Latitude'].mean(), lynchLocation['Longitude'].mean()], zoom_start = 1000)

mappingLocation = folium.Map(location= [41.850033, -87.6500523], zoom_start = 3)


for i in lynchLocation.index:
    if pd.notnull(lynchLocation['lat'][i]):
        folium.CircleMarker([lynchLocation['lat'][i], lynchLocation['lng'][i]],
                             radius=5, color = '#CD3181',
                             fill_color = '#CD3181').add_to(mappingLocation)

mappingLocation
