import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "charts_multipleBars_util",
                                          ['pandas', 'plotly']) == False:
    sys.exit(0)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Returns a grid of barcharts for each algorithm.
#Algorithms are horizontally organized based on the order on which they are inputted
#datalist is list of algorithms
#var is variable of choice
#ntopchoices is the n max values
def multiple_barchart(datalist,outputFilename,var,ntopchoices):
    tempdatalist=[]
    for i in datalist:
        tempdatalist.append(pd.DataFrame(i))
    newDatalist=[]
    for i in tempdatalist:
        newDatalist.append(pd.DataFrame(i[var].value_counts()).reset_index().rename(columns={'index':var,var:'Frequency'}).head(ntopchoices))
    fig=make_subplots(rows=2,cols=int(len(datalist)/2)+len(datalist)%2)
    cols=1
    for i in range(0,len(newDatalist)):
        if i<int(len(datalist)/2)+len(datalist)%2:
            fig.add_trace(go.Bar(x=newDatalist[i][var],y=newDatalist[i]['Frequency'],name='Algorithm '+str(i+1)),row=1,col=cols)
            cols=cols+1
    cols=1
    for i in range(0,len(newDatalist)):
        if i>=int(len(datalist)/2)+len(datalist)%2:
            fig.add_trace(go.Bar(x=newDatalist[i][var],y=newDatalist[i]['Frequency'],name='Algorithm '+str(i+1)),row=2,col=cols)
            cols=cols+1
    fig.write_html(outputFilename)
    return fig
