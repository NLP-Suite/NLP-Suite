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

def timeline(data, outputFilename, var,date_format_var, cumulative, monthly=None, yearly=None):
#convert csv to pandas
    if type(data)==str:
        data=pd.read_csv(data)
    if type(data[var][0]) != str:
        mb.showwarning("Warning",
                       "The csv file field selected must be categorical.\n\nPlease select a categorical field, rather than a continuous numeric field, and try again.")
        return
    #Extract day from document
    date=[]
    year=[]
    month=[]
    day=[]
    if date_format_var=='yyyy':#creates year variable based on yyyy format
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',data['Document'][i])[0])
            data['year']=year
    elif date_format_var=='mm-yyyy': #creates year and month variable in yyyy-mm format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][0:2])
        data['year']=year
        data['month']=month
    elif date_format_var=='yyyy-mm': #creates year and month variable in yyyy-mm format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][-2:])
        data['year']=year
        data['month']=month
    elif date_format_var=='dd-mm-yyyy':#creates year,month and day variable in yyyy-mm-dd format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][3:5])
        for i in range(0,len(data['Document'])):
            day.append(month[i]+'-'+date[i][0:2])
        data['day']=day
        data['year']=year
        data['month']=month
    elif date_format_var=='mm-dd-yyyy':#creates year,month and day variable in yyyy-mm-dd format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][0:2])
        for i in range(0,len(data['Document'])):
            day.append(month[i]+'-'+date[i][3:5])
        data['year']=year
        data['month']=month
        data['day']=day
    elif date_format_var=='yyyy-mm-dd':#creates year,month and day variable in yyyy-mm-dd format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][5:7])
        data['year']=year
        data['month']=month
        data['day']=date
    elif date_format_var=='yyyy-dd-mm':#creates year,month and day variable in yyyy-mm-dd format
        for i in range(0,len(data['Document'])):
            date.append(re.search('\d.*\d',data['Document'][i])[0])
        for i in range(0,len(data['Document'])):
            year.append(re.search('\d{4}',date[i])[0])
        for i in range(0,len(data['Document'])):
            month.append(year[i]+'-'+date[i][-2:])
        for i in range(0,len(data['Document'])):
            day.append(month[i]+'-'+date[i][5:7])
        data['year']=year
        data['month']=month
        data['day']=day
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
