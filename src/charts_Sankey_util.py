import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Important to note, like Sunburster, for this function to be efficient,
# Inflow should be a categorical variable with a small amount of different values
# Outflow should also be categorical
# Sankey may take a bit longer than Sunburster or timechart to run
def Sankey(data,outputFilename,inflow,outflow):#Function takes a csv file as data input, inflow is the variable of choice into which the outflow variable flows. For example, in coreference, inflow would be Pronoun and outflow would be Reference

    if type(data)==str:# Converts data to dataframe
        data=pd.read_csv(data)

    data[inflow]=data[inflow].str.lower()#Everything to lowercase to avoid unnecessary duplications
    sourcelist=list(range(0,len(set(data[inflow]))))#Preparing source vector for Sankey in accordance with the Plotly documentation
    source=[item for item in sourcelist for _ in range(len(set(data[outflow])))] #Finishing source vector

    target1=list(range(0,len(set(data[outflow]))))#Preparing target vector for Sankey in accordance with the Plotly documentation
    target2 = [x+len(set(data[inflow])) for x in target1]
    target=target2*len(set(data[inflow]))#Finishing target vector

    valuevector=[]#The following for loops puts in a vector the corresponding frequencies of each outflow into its inflow
    for i in sorted(list(set(data[inflow]))):
        tempdata=pd.DataFrame(data[data[inflow]==i][outflow].value_counts()).reset_index().rename(columns={'index':outflow,outflow:'Frequency'}).head(5) #We take the top 5 outflow to avoid overcluttering the Sankey graph
        for j in sorted(list(set(data[outflow]))):
            if j not in list(tempdata[outflow]):
                valuevector.append(0)
            else:
                valuevector.append(list(tempdata[tempdata[outflow]==j]['Frequency'])[0])

    label=sorted(list(set(data[inflow])))+sorted(list(set(data[outflow]))) #Labeling the Sankey graph in accordance to Plotly Documentation

    fig=go.Figure(go.Sankey(link=dict(source=source,target=target,value=valuevector),node=dict(label=label,pad=35,thickness=10)))#Creating Sankey graph

    fig.update_layout(
    hovermode = 'x',
    title="Sankey plot of "+inflow+' and '+outflow,
    font=dict(size = 10, color = 'white'),
    plot_bgcolor='black',
    paper_bgcolor='black'
)#Cosmetic changes
    fig.write_html(outputFilename)
    return outputFilename
