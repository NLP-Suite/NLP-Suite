# created by Samir Kaddoura, November 2022

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"charts_Sunburster_util",['pandas','numpy','tkinter','plotly','re','warnings'])==False:
    sys.exit(0)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

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

    finaldata=data.iloc[id_list] #filter dataset by row with interest values
    finaldata['interest']=interestvector #add interest column

    return finaldata


#Returns sunburst piechart. Input a dataframe provided by the NLP suite as data,
# interest is a vector including interest separation based on separator (as defined above)
#label is a categorical variable we're interested in
#first_sentences is the n first sentences
#last_sentences is the n last sentences
#half_text is a boolean defining whether to split the text in half or not
def Sunburster(data,interest,label,first_sentences=None,last_sentences=None,half_text=None):
    #the last 3 arguments are optional. If first_sentences is specified and last_sentences is not or vice versa, we return a message stating they must both be specified or absent at the same time
    if (first_sentences==None and last_sentences!=None) or (first_sentences!=None and last_sentences==None):
        return 'both number of first sentences and number of last sentences have to be specified or absent at the same time'
    else: #Otherwise, we run the Sunburster

        tempdata=separator(data,interest) #Create "interest" variable

        if half_text==True or (first_sentences==None and last_sentences==None): #If half text is true or both number of first sentences and last sentences is absent, we split each text in half and attribute a "beginning" half and "end" half

            ogdata=tempdata[tempdata['Document ID']==1] #take the first document

            ogdata1=ogdata[ogdata['Sentence ID']<=len(ogdata)/2] #split the document by first half
            oglist1=list(np.repeat('Beginning',len(ogdata1)))
            ogdata1['Beginning or End']=oglist1 #add list "Beginning" the length of the first half

            ogdata2=ogdata[ogdata['Sentence ID']>len(ogdata)/2] #split the document by first half
            oglist2=list(np.repeat('End',len(ogdata2)))
            ogdata2['Beginning or End']=oglist2 #add list "End" the length of the first half

            finaldata=ogdata1.append(ogdata2) #merge dataframes

            for i in range(2,max(data['Document ID'])+1): #iterate same process for each document
                intermediatedata=tempdata[tempdata['Document ID']==i]

                intermediatedata1=intermediatedata[intermediatedata['Sentence ID']<=len(intermediatedata)/2]
                intermediatelist1=list(np.repeat('Beginning',len(intermediatedata1)))
                intermediatedata1['Beginning or End']=intermediatelist1

                finaldata=finaldata.append(intermediatedata1)

                intermediatedata2=intermediatedata[intermediatedata['Sentence ID']>len(intermediatedata)/2]
                intermediatelist2=list(np.repeat('End',len(intermediatedata2)))
                intermediatedata2['Beginning or End']=intermediatelist2

                finaldata=finaldata.append(intermediatedata2)

            fig=px.sunburst(finaldata,path=['interest','Beginning or End',label]) #return sunburster

            return fig

        else:
            tempdata1=tempdata[tempdata['Sentence ID']<=first_sentences] #all observations with the first n sentences

            list1=list(np.repeat('Beginning',len(tempdata1))) #List repeating 'Beginning'

            for i in range(1,max(data['Document ID'])+1):
                intermediatedata1=tempdata[tempdata['Document ID']==i]
                intermediatedata2=intermediatedata1[intermediatedata1['Sentence ID']>(len(intermediatedata1)-last_sentences)]
                tempdata1=tempdata1.append(intermediatedata2).reset_index().drop(columns={'index'}) #all observations with last n sentences

            list2=list(np.repeat('End',len(tempdata1)-len(list1))) #List repeating 'End'
            finallist=list1+list2 #Create a vector defining if the sentence is at the beginning or the end
            finaldata=tempdata1
            finaldata['Beginning or End']=finallist

            fig=px.sunburst(finaldata,path=['interest','Beginning or End',label]) #create sunburst plot

            return fig
