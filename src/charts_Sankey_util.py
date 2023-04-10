import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "charts_Sankey_util",
                                          ['pandas', 'numpy',  'plotly'], 'tkinter') == False:
    sys.exit(0)

import pandas as pd
import numpy as np
import plotly.graph_objects as go

import tkinter.messagebox as mb

#var1 is the first categorical variable, lengthvar1 is the amount of var 1: should take values of 5 or 10
#var2 is the second categorical variable, lengthvar2 is the amount of var 2: should take values of 5,10 or 20
#var3 is the third categorical variable, lengthvar3 is the amount of var 3: should take values of 5,10, 20 or 30
#All these recommendations are for performance
#three_way_Sankey is a boolean variable that dictates whether the returned Sankey is 2way or 3way. True for 3 variables, false for 2 variables
def Sankey(data,outputFilename,var1,lengthvar1,var2,lengthvar2,three_way_Sankey,var3=None,lengthvar3=None):
    if type(data)==str:
        data=pd.read_csv(data)
    if type(data[var1][0])!=str and type(data[var2][0])!=str:
        mb.showwarning("Warning",
                   "The csv file field(s) selected should be categorical.\n\nYou should select categorical field(s), rather than continuous numeric field(s), and try again.")

    if three_way_Sankey==False:

        data[var1]=data[var1].str.lower()
        tempframe=pd.DataFrame(data[var1].value_counts().head(lengthvar1)).reset_index()
        finalframe=data[data[var1].isin(list(set(tempframe['index'])))]
        tempframe2=pd.DataFrame(finalframe[var2]).value_counts().head(lengthvar2).reset_index()
        finalframe=finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        finalframe=finalframe.reset_index(drop=True)
        sourcelist=list(range(0,len(set(finalframe[var1]))))
        source=[item for item in sourcelist for _ in range(len(set(finalframe[var2])))]

        target1=list(range(0,len(set(finalframe[var2]))))
        target2 = [x+len(set(finalframe[var1])) for x in target1]
        target=target2*len(set(finalframe[var1]))

        valuevector=[]
        for i in sorted(list(set(finalframe[var1]))):
            tempdata=pd.DataFrame(finalframe[finalframe[var1]==i][var2].value_counts()).reset_index().rename(columns={'index':var2,var2:'Frequency'})
            for j in sorted(list(set(tempdata[var2]))):
                if j not in list(tempdata[var2]):
                    valuevector.append(0)
                else:
                    valuevector.append(list(tempdata[tempdata[var2]==j]['Frequency'])[0])

        labelvector=sorted(list(set(finalframe[var1])))+sorted(list(set(finalframe[var2])))

    else:
        data[var1]=data[var1].str.lower()
        tempframe=pd.DataFrame(data[var1].value_counts().head(lengthvar1)).reset_index()
        finalframe=data[data[var1].isin(list(set(tempframe['index'])))]
        tempframe2=pd.DataFrame(finalframe[var2]).value_counts().head(lengthvar2).reset_index()
        tempframe3=pd.DataFrame(finalframe[var3]).value_counts().head(lengthvar3).reset_index()
        finalframe=finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        finalframe=finalframe[finalframe[var3].isin(list(set(tempframe3[var3])))]
        finalframe=finalframe.reset_index(drop=True)
        source1=list(range(0,len(set(finalframe[var1]))+len(set(finalframe[var2]))))
        source=[item for item in source1 for _ in range(len(set(finalframe[var2]))+len(set(finalframe[var3])))]
        target1=list(range(0,len(set(finalframe[var2]))+len(set(finalframe[var3]))))
        target2=[x+len(set(finalframe[var1])) for x in target1]
        target=target2*len(source1)
        labelvector=sorted(set(finalframe[var1]))+sorted(set(finalframe[var2]))+sorted(set(finalframe[var3]))
        valuevector=[]
        for i in sorted(list(set(finalframe[var1]))):
            tempvec=[]
            tempframe=finalframe[finalframe[var1]==i]
            wantedframe=pd.DataFrame(tempframe[var2].value_counts()).reset_index().rename(columns={'index':var2,var2:'Frequency'})
            for j in sorted(list(set(finalframe[var2]))):
                if j not in list(wantedframe[var2]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var2]==j]['Frequency'])[0])
            tempvec=tempvec+list(np.repeat(0,len(target2)-len(tempvec)))
            valuevector=valuevector+tempvec
        for i in sorted(list(set(finalframe[var2]))):
            tempvec=[]
            tempframe=finalframe[finalframe[var2]==i]
            wantedframe=pd.DataFrame(tempframe[var3].value_counts()).reset_index().rename(columns={'index':var3,var3:'Frequency'})
            tempvec=list(np.repeat(0,len(set(finalframe[var2]))))
            for j in sorted(list(set(finalframe[var3]))):
                if j not in list(wantedframe[var3]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var3]==j]['Frequency'])[0])
            valuevector=valuevector+tempvec
    fig=go.Figure(go.Sankey(link=dict(source=source,target=target,value=valuevector),node=dict(label=labelvector,pad=35,thickness=10)))
    fig.write_html(outputFilename)

    return outputFilename
