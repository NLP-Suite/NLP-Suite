# written by Samir Kaddoura, December 2022

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"charts_timeline_util.py",['pandas','numpy','regex','plotly.express'])==False:
    sys.exit(0)

import pandas as pd
import numpy as np
import regex as re
import plotly.express as px
import tkinter.messagebox as mb

# data is a csv file that contains a Document column with embedded date in filename
# var is a variable to be used to show the evolution through time
# outputFilename to save output, monthly and yearly are boolean variables
# cumulative time chart shows the frequency of the chosen variable up until a current day rather than visualizing the frequency day by day
# if monthly or yearly is passed as true, return monthly or yearly graph respectively
#   if both are passed as false, return daily graph
#   both cannot be simultaneously true

def timeline(data, outputFilename, var, cumulative, monthly=None, yearly=None):
#convert csv to pandas
    if type(data)==str:
        data=pd.read_csv(data)
#Extract day from document
    day=[]
    for i in range(0,len(data)):
        try:
            day.append(re.search('\d.*\d',data['Document'][i])[0])
        except:
            mb.showwarning("Warning",
                           "The Plotly timeline algorithm expects in input a csv file with a header 'Document' and filenames with dates embedded in the filename (e.g., The New York Times_12-23-1992).\n\nPlease, select a different csv file and try again.")
            return ''
    data['day']=day
#Extract month and year
    month=[]
    year=[]
    for i in range(0,len(data)):
        month.append(data['day'][i][0:7])
        year.append(data['day'][i][0:4])
    data['month']=month
    data['year']=year
#Plot corresponding graph depending on the options
    if cumulative==False:
        #monthly and yearly can't simultaneously be True
        if monthly==True and yearly==True:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"

        elif monthly==True:#If monthly is True, return monthly non-cumulative graph
            data=data.sort_values('month')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['month'])):
                tester=pd.DataFrame(data[data['month']==i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',animation_frame='date').update_xaxes(categoryorder='total ascending')

        elif yearly==True:#If yearly is True, return yearly non-cumulative graph
            data=data.sort_values('year')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['year'])):
                tester=pd.DataFrame(data[data['year']==i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',animation_frame='date').update_xaxes(categoryorder='total ascending')
        else:#If neither is True, return daily non-cumulative graph
            data=data.sort_values('day')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['day'])):
                tester=pd.DataFrame(data[data['day']==i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',animation_frame='date').update_xaxes(categoryorder='total ascending')
    else:
        if monthly==True and yearly==True:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"
        elif yearly==True:#If yearly is True, return yearly cumulative graph
            data=data.sort_values('year')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['year'])):
                tester=pd.DataFrame(data[data['year']<=i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',animation_frame='date').update_xaxes(categoryorder='total ascending')
        elif monthly==True:#If monthly is True, return monthly cumulative graph
            data=data.sort_values('month')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['month'])):
                tester=pd.DataFrame(data[data['month']<=i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',var,animation_frame='date').update_xaxes(categoryorder='total ascending')
        else:#If neither is True, return daily cumulative graph
            data=data.sort_values('day')
            finalframe=pd.DataFrame()
            for i in sorted(set(data['day'])):
                tester=pd.DataFrame(data[data['day']<=i][var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'})
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp=pd.DataFrame([j,0]).T.rename(columns={0:var}).rename(columns={0:var,1:'Frequency'})
                        tester=pd.concat([tester,temp])
                tester=tester.sort_values(var)
                tester
                date=np.repeat(i,len(tester))
                tester['date']=date
                tester=tester.reset_index(drop=True)
                finalframe=pd.concat([finalframe,tester])
            fig=px.bar(finalframe,var,'Frequency',animation_frame='date').update_xaxes(categoryorder='total ascending')

    fig=fig.update_geos(projection_type="equirectangular", visible=True, resolution=110)

    fig.write_html(outputFilename)
    return outputFilename
