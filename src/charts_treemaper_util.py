import pandas as pd
import numpy as np
import plotly.express as px
import re
import tkinter.messagebox as mb

# Function creates a new column that identifies the documents based on a specific interest variable
#two inputs taken: data is the dataset in question, interest is a vector that the user will have to define, as it changes depending on the corpus
def separator(data,interest):

    interestvector=[]#empty interest vector
    id_list=[] #empty id list in which we record every entry in the dataset that contains one of the interest inputs

    for i in range(0,len(data)): #check every entry in dataset
        for j in range(0,len(interest)): #check every interest vector
            if re.search('.*'+interest[j]+'[^.]',data['Document'][i]):#if the name of the document contains a word of intersest, we append that word to a vector
                interestvector.append(interest[j])
                id_list.append(i)#append the index of the row that contains the interest value

    finaldata=data.loc[id_list] #filter dataset by row with interest values
    finaldata['interest']=interestvector #add interest column

    return finaldata


# This function takes the data, an interest vector defined the same way as in the sunburster function,
#   a variable of choice (should be categorical) var,
#   a boolean variable to dictate if the user wants to observe an additional variable with "extra_dimension_average",
#   the numerical variable of choice average_variable

#The graph shows the frequencies of each group by default depending on the interest vector and the initial variable of choice. If specified, it shows the average of average_variable per group
def treemaper(data,outputFilename,interest,csv_file_field,extra_dimension_average,average_variable=None):
    if type(data)==str:#convert data to dataframe
        data=pd.read_csv(data)
    if type(data[csv_file_field][0])!=str:
        mb.showwarning("Warning",
                   "The csv file field selected should be categorical.\n\nYou should select a categorical field, rather than a continuous numeric field, and try again.")
    if extra_dimension_average and type(data[average_variable][0])!=np.float64:
        mb.showwarning("Warning",
                   "The csv file field selected should be numeric.\n\nYou should select a numeric field, rather than an alphabetic field, and try again.")

    data=separator(data,interest)#use separator function to create interest vector

    if extra_dimension_average==False:#return regular 2 variable graph if false
        fig=px.treemap(data,path=[px.Constant('Total Frequency'),'interest',csv_file_field])
    else:#return graph with extra variable if true
        fig=px.treemap(data,path=[px.Constant('Total Frequency'),'interest',csv_file_field],color=average_variable,color_continuous_scale='RdBu')
    fig.write_html(outputFilename)
    return outputFilename
