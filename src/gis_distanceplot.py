"""
@author: Sabrina Nardin, Nov 11 2019
#edited: Roberto Franzosi Nov 15 2019
"""

#import libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#set up working dir and set up filenames
os.chdir('C:\\Program Files (x86)\\PC-ACE\\NLP')
input_dir='C:\\Users\\rfranzo\\Documents\\My Publications\\My Papers\\IN PROGRESS\\LA STAMPA\\Annunci matrimoniali Turin\\GIS results\\output\\Distances FINAL cleaned\\'
output_dir='C:\\Users\\rfranzo\\Documents\\My Publications\\My Papers\\IN PROGRESS\\LA STAMPA\\Annunci matrimoniali Turin\\GIS results\\output\\Distances FINAL cleaned\\'

# groom residence and bride residence distance from each other, all 22K records
# comment/uncomment the next 7 lines
# input_filename = 'NLP_GIS_la_stampa_groom_bride_waypoints_distance_gis_groom_res_gis_bride_res_ALL.csv'
# input_filename=os.path.join(input_dir,input_filename)
# # titles to be displayed in the chart
# chartTitle1='Geodesic distance in miles (Groom\'s residence distance to bride\'s residence)'
# chartTitle2='Geodesic distance in Km (Groom\'s residence distance to bride\'s residence)'
# chartTitle3='Great circle distance in miles (Groom\'s residence distance to bride\'s residence)'
# chartTitle4='Great circle distance in Km (Groom\'s residence distance to bride\'s residence)'

# groom residence distance from Torino, all 22K records
# comment/uncomment the next 7 lines
# input_filename = 'NLP_GIS_la_stampa_groom_bride_waypoints_distance_gis_groom_res_gis_bride_res_ALL.csv'
# input_filename=os.path.join(input_dir,input_filename)
# # titles to be displayed in the chart
# chartTitle1='Geodesic distance in miles (Groom\'s residence distance to Turin)'
# chartTitle2='Geodesic distance in Km (Groom\'s residence distance to Turin)'
# chartTitle3='Great circle distance in miles (Groom\'s residence distance to Turin)'
# chartTitle4='Great circle distance in Km (Groom\'s residence distance to Turin)'

# bride residence distance from Torino, all 22K records
# comment/uncomment the next 7 lines
input_filename = 'NLP_GIS_la_stampa_groom_bride_waypoints_distance_Torino_gis_bride_res_ALL.csv'
input_filename=os.path.join(input_dir,input_filename)
# titles to be displayed in the chart
chartTitle1='Geodesic distance in miles (Bride\'s residence distance to Turin)'
chartTitle2='Geodesic distance in Km (Bride\'s residence distance to Turin)'
chartTitle3='Great circle distance in miles (Bride\'s residence distance to Turin)'
chartTitle4='Great circle distance in Km (Bride\'s residence distance to Turin)'

encodingValue='latin-1'

#import data
df = pd.read_csv(input_filename, encoding=encodingValue, low_memory=False)

# setup all variabels #################################################################

#These are the column headers to be plotted in the csv input file
column1='Geodesic distance in miles'
column2='Geodesic distance in Km'
column3='Great circle distance in miles'
column4='Great circle distance in Km'

xAxisLabel1='Miles'
xAxisLabel2='Kilometers'

yAxisLabel='Frequency of grouped distances'

chartType1='bar'
chartType2='pie'

#cut numerical data into categories (cuts could be done also automatically but no good results)
#https://stackoverflow.com/questions/49382207/how-to-map-numeric-data-into-categories-bins-in-pandas-dataframe
bins =  [0, 1, 10, 20, 30, 40, 50, 100, np.inf] #np.inf is the same as np.float
names = ['0', '1-10', '11-20', '21-30','31-40','41-50','51-100','101+']

# process data and visualize  #################################################################

#turn 0 into 0.0, i.e., floating
print(df.dtypes)
df.loc[df[column1] == 0, [column1]] = 0.01
df.loc[df[column2] == 0, [column2]] = 0.01
df.loc[df[column3] == 0, [column3]] = 0.01
df.loc[df[column4] == 0, [column4]] = 0.01

#yAxisLabel is the new Y-axis label
#yAxisLabel is the new Y-axis label
df[yAxisLabel] = pd.cut(df[column1], bins, labels=names)
df[yAxisLabel] = pd.cut(df[column2], bins, labels=names)

#plot miles with matplot lib -- bar chart
df[yAxisLabel].value_counts().sort_index(ascending=True).plot(kind=chartType1)
plt.title(chartTitle1)
plt.xlabel(xAxisLabel1)
plt.ylabel(yAxisLabel)
outFilename=os.path.join(output_dir,chartTitle1+'.png')
plt.savefig(outFilename,dpi=100)
plt.show()

#plot km with matplot lib -- bar chart
df[yAxisLabel].value_counts().sort_index(ascending=True).plot(kind=chartType1)
plt.title(chartTitle2)
plt.xlabel(xAxisLabel2)
plt.ylabel(yAxisLabel)
outFilename=os.path.join(output_dir,chartTitle2+'.png')
plt.savefig(outFilename,dpi=100)
plt.show()

#plot miles with matplot lib -- pie chart
df[yAxisLabel].value_counts().plot(kind=chartType2, autopct='%1.1f%%')
plt.title(chartTitle3)
plt.ylabel('')
outFilename=os.path.join(output_dir,chartTitle3+'.png')
plt.savefig(outFilename,dpi=100)
plt.show()

#plot km with matplot lib -- pie chart
df[yAxisLabel].value_counts().plot(kind=chartType2, autopct='%1.1f%%')
plt.title(chartTitle4)
plt.ylabel('')
outFilename=os.path.join(output_dir,chartTitle4+'.png')
plt.savefig(outFilename,dpi=100)
plt.show()

#plot data with seaborn 
#sns.set()
#sns.countplot(df['GeoKmRange'],color='blue')  #distr on x
#sns.countplot(y=df['GeoKmRange'],color='blue') #distr on y 