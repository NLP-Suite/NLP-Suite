# Written by Tony Chen Gu in Feb 2022
# Contact: chentony2011@hotmail.com

from asyncio.windows_events import NULL
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os

## NOTE:
## some graphing functions has a column placed at the end
## these functions supports the feature of getting frequencies of the categorical variables
## the static_flag is used to indicate whether the chart is static or not

# def create_excel_chart(window,data_to_be_plotted,inputFilename,outputDir,scriptType,
#                        chartTitle,
#                        chart_type_list,
#                        column_xAxis_label='',
#                        column_yAxis_label='',
#                        hover_info_column_list=[],
#                        reverse_column_position_for_series_label=False,
#                        series_label_list=[],
#                        second_y_var=0,
#                        second_yAxis_label=''):
# match the excel chart format
def create_plotly_chart(inputFilename,outputDir,chartTitle,chart_type_list,cols_to_plot,
                        column_xAxis_label='',
                        column_yAxis_label='',
                        static_flag=False,):
    try:
        data = pd.read_csv(inputFilename, encoding='utf-8')
    except pd.errors.ParserError:
        data = pd.read_csv(inputFilename, encoding='utf-8', sep='delimiter')
    except:
        print("Error: failed to read the csv file named: "+inputFilename)
        return
    headers = data.columns.tolist()
    file_list = []
    for j in range(0,len(chart_type_list)):
        i = chart_type_list[j]
        x_cols = []
        y_cols = []
        fig = NULL
        #if(i == 'bar' or i == 'pie'):
        x_cols = headers[cols_to_plot[j][0]-1]
        y_cols = headers[cols_to_plot[j][1]-1]
        if i == 'bar':
            fig = plot_bar_chart_px(x_cols,inputFilename,chartTitle)
        elif i == 'pie':
            fig = plot_pie_chart_px(x_cols,inputFilename,chartTitle)
        #elif(i == 'scatter' or i == 'radar'):
        elif i == 'scatter':
            fig = plot_scatter_chart_px(x_cols,y_cols,inputFilename,chartTitle)
        elif i == 'radar':
            fig = plot_radar_chart_px(x_cols,y_cols,inputFilename,chartTitle)
        elif i == 'line':
            #plot_multi_line_chart_w_slider_px(fileName, chartTitle, col_to_be_ploted, series_label_list = NULL)
            fig = plot_multi_line_chart_w_slider_px(inputFilename,chartTitle,cols_to_plot)
            file_list.append(save_chart(fig,outputDir,chartTitle,static_flag,column_xAxis_label,column_yAxis_label))
            return file_list
        else:
            print('Chart type not supported '+i+'! Skipped and continue with next chart.')
        file_list.append(save_chart(fig,outputDir,chartTitle,static_flag,column_xAxis_label,column_yAxis_label))
    return file_list

# need to discuss further
def get_chart_title(xVar = '', yVar = '', base_title = '', chart_type = ''):
    return base_title+" of "+xVar+" and "+yVar

# get frequencies of categorical variables
def get_frequencies(data, variable):
    #this line give a column of the counts for the categorical vairable
    #the name of row is the categorical variable
    data_count = data[variable].value_counts()
    #extract the row name = categorical variables
    data_head = data_count.index
    header = variable+"_count"
    #rebuild the dataframe with a column of categorical vairables and a column of their counts
    #the row name is still the categorical variable
    return pd.DataFrame({variable:data_head,header:data_count})

#helper function for saving the chart
#set up the output directory path
#support both static and dynamic chart
def save_chart(fig, outputDir, chartTitle, static_flag, x_label = '', y_label = ''):
    fig.show()
    if x_label != '':
        fig.update_layout(xaxis_title=x_label)
    if y_label != '':
        fig.update_layout(yaxis_title=y_label)
    if static_flag:
        savepath = os.path.join(outputDir, chartTitle + '.png')
        fig.write_image(savepath)
    else:
        savepath = os.path.join(outputDir, chartTitle + '.html')
        fig.write_html(savepath)
    return savepath

#plot bar chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
#Users are expected to provide the x label and their hights.
#If not call the get_frequencies function to get the frequencies of the categorical variables in x_label column
def plot_bar_chart_px(x_label, fileName, chartTitle, height = ''):
    data = pd.read_csv(fileName, encoding='utf-8')
    if height == '':
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.bar(data,x=x_label,y=height)
    fig.update_layout(title=chartTitle, title_x=0.5)
    return fig

#plot pie chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
def plot_pie_chart_px(x_label, fileName, chartTitle, height = ''):
    data = pd.read_csv(fileName, encoding='utf-8')
    if height == '':
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.pie(data, values=height, names=x_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    return fig

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#x_label indicates the column name of x axis from the data    COULD BE A DISCRETE VARIABLE
#y_label indicates the column name of y axis from the data    COULD BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
def plot_scatter_chart_px(x_label, y_label, fileName, chartTitle):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.scatter(data, x=x_label, y=y_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    return fig

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#theta_label indicates the column name of the "feature" from the data    SHOULD BE A DISCRETE VARIABLE
#r_label indicates the column name of the value of the feature from the data    CANNOT BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
#null value will cause an unclosed shape. This function default removes all rows contaning null values
def plot_radar_chart_px(theta_label, fileName, chartTitle, r_label = None):
    data = pd.read_csv(fileName, encoding='utf-8')
    if r_label is None:
        r_label = theta_label+"_count"
        data = get_frequencies(data, theta_label)
    data = data.dropna(subset = [theta_label, r_label])
    fig = px.line_polar(data, r=r_label, theta=theta_label, line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(title=chartTitle, title_x=0.5)
    return fig

#plot 
def plot_multi_line_chart_w_slider_px(fileName, chartTitle, col_to_be_ploted, series_label_list = NULL):
    data = pd.read_csv(fileName, encoding='utf-8')
    data.fillna(0, inplace=True)
    figs = make_subplots()
    col_name = list(data.head())
    default_series_name = (series_label_list == NULL)
    for i in range(0,len(col_to_be_ploted)):
        if default_series_name:
            series_label = col_name[col_to_be_ploted[i][1]]
        else:
            series_label = series_label_list[i]
        trace = go.Scatter(
            x = data[col_name[col_to_be_ploted[i][0]]],
            y = data[col_name[col_to_be_ploted[i][1]]],
            name = series_label)
        figs.add_trace(trace)
    figs.update_layout(title=chartTitle, title_x=0.5)
    figs.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1),
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
        )
    )
    return figs
#=======================================================================================================================
# debug use
#=======================================================================================================================
# def main():
#     x_label = 'char'
#     height = 'count'
#     hover_label = 'count'
#     chartTitle = 'test chart'
#     fileName =  'C:/Users/Tony Chen/Desktop/NLP_working/Test OutputNLP_NVA_conll_eng_Noun_POSTAG_list_frequencies.csv'
#     outputDir = 'C:/Users/Tony Chen/Desktop/NLP_working'

#     #plot_bar_chart(x_label, height, fileName, outputDir, chartTitle, hover_label)
    
#     #plot_radar_chart_px(x_label, height, fileName, outputDir, chartTitle)
#     plot_multi_line_chart_w_slider_px(fileName,outputDir,chartTitle)

# if __name__ == "__main__":
#     main()
