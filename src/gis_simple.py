# -*- coding: utf-8 -*-
"""
Created on Wed Nov 6 19:22:35 2019
@author: sabrina
"""

#source: https://www.youtube.com/watch?v=zdPW4aVha8M

#import libraries
import os
import pandas as pd
import googlemaps

#set up working dir and set up input and output filenames
os.chdir('C:\\Program Files (x86)\\PC-ACE\\NLP')
inputFilenamename = 'city_freq_2019nov5.csv'
output_filename = 'OUT_city_freq_2019nov5.csv'

#import data
#df = pd.read_csv(inputFilenamename, encoding='utf-8')
df = pd.read_csv(inputFilenamename, encoding='latin-1')

#set Google API
api_key = ""
#see: console.developers.google.com/apis

#request lat,long and other data from google map API
gmaps_key = googlemaps.Client(key = "")

#create empty columns to store results in my panda df
df['Lat'] = None
df['Lon'] = None
df['Add'] = None

#get the data and store them
for i in range(len(df)):
    geocode_result = gmaps_key.geocode(df.loc[i, 'address']) #send request for each address in df
    #note: geocode_result saves all GoogleApi results: inspect it to decide results to save
    try: #use a try/except in case requests do not give resutls
        lat = geocode_result[0]["geometry"]["location"]["lat"] #extracting lat from the request resutls
        lng = geocode_result[0]["geometry"]["location"]["lng"]
        add = geocode_result[0]["formatted_address"]
        df.loc[i, "Lat"] = lat  #imputing lat in my df
        df.loc[i, "Lon"] = lng
        df.loc[i, "Add"] = add
    except:
        lat = None
        lng = None
        add = None
    print(i)

#print first 20 results to check
print(df[:10])

#count all 'None' results
df.isnull().sum() #135 null results

#extract all 'None' resutls
none = df[df['Add'].isnull()]

#export results
pd.DataFrame(df).to_csv(output_filename, encoding='utf-8')
