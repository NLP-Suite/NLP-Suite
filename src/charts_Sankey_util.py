import pandas as pd
import plotly.graph_objects as go
import numpy as np


#data is input dataset, var1 is the leftmost variable in Sankey, var2 is the final or intermediate variable depending on the next argument
#three_way_Sankey is a boolean variable. If False, returns two-variable Sankey. If True, returns a three variable Sankey where you specify var3
#Some specifications: two variable Sankey takes the 5 most common of var2 for each var1
#Three variable Sankey takes the 10 most common var1, the 30 most common of var2 and the 50 most common of var3

def Sankey(data,outputFilename,var1,var2,three_way_Sankey,var3=None):
    if type(data)==str:
        data=pd.read_csv(data)

    if three_way_Sankey==False:
    
        data[var1]=data[var1].str.lower()
        sourcelist=list(range(0,len(set(data[var1]))))
        source=[item for item in sourcelist for _ in range(len(set(data[var2])))]

        target1=list(range(0,len(set(data[var2]))))
        target2 = [x+len(set(data[var1])) for x in target1]
        target=target2*len(set(data[var1]))

        valuevector=[]
        for i in sorted(list(set(data[var1]))):
            tempdata=pd.DataFrame(data[data[var1]==i][var2].value_counts()).reset_index().rename(columns={'index':var2,var2:'Frequency'}).head(5)
            for j in sorted(list(set(data[var2]))):
                if j not in list(tempdata[var2]):
                    valuevector.append(0)
                else:
                    valuevector.append(list(tempdata[tempdata[var2]==j]['Frequency'])[0])

        labelvector=sorted(list(set(data[var1])))+sorted(list(set(data[var2])))

    else:
        tempframe=pd.DataFrame(data[var1].value_counts().head(10)).reset_index()
        finalframe=data[data[var1].isin(list(set(tempframe['index'])))]
        tempframe2=pd.DataFrame(finalframe[var2]).value_counts().head(30).reset_index()
        tempframe3=pd.DataFrame(finalframe[var3]).value_counts().head(50).reset_index()
        finalframe=finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        finalframe=finalframe[finalframe[var3].isin(list(set(tempframe3[var3])))]
        finalframe=finalframe.reset_index(drop=True)
        source1=list(range(0,len(set(finalframe[var1]))+len(set(finalframe[var2]))))
        source=[item for item in source1 for _ in range(len(set(finalframe[var2]))+len(set(finalframe[var3])))]
        target1=list(range(0,len(set(finalframe[var2]))+len(set(finalframe[var3]))))
        target2=[x+len(set(finalframe[var1])) for x in target1]
        target=target2*len(source1)
        labelvector=sorted(set(finalframe[var1]))+sorted(set(finalframe[var3]))+sorted(set(finalframe[var2]))
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
            tempvec=list(np.repeat(0,len(target2)-len(source1)-len(list(set(finalframe[var1])))))
            for j in sorted(list(set(finalframe[var3]))):
                if j not in list(wantedframe[var3]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var3]==j]['Frequency'])[0])
            valuevector=valuevector+tempvec
            
    fig=go.Figure(go.Sankey(link=dict(source=source,target=target,value=valuevector),node=dict(label=labelvector,pad=35,thickness=10)))
    fig.write_html(outputFilename)
    return outputFilename