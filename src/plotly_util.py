# Written by Tony Chen Gu Feb 2022

import pandas as pd
import plotly.express as px
import os

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
#suport both static and dynamic chart
def save_chart(fig, outputDir, chartTitle, static_flag):
    if static_flag:
        savepath = os.path.join(outputDir, chartTitle + '.png')
        fig.write_image(savepath)
    else:
        savepath = os.path.join(outputDir, chartTitle + '.html')
        fig.write_html(savepath)
    return

#plot bar chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
#Users are expected to provide the x label and their hights.
#If not call the get_frequencies function to get the frequencies of the categorical variables in x_label column
def plot_bar_chart_px(x_label, fileName, outputDir, chartTitle, height = None, static_flag = False):
    data = pd.read_csv(fileName, encoding='utf-8')
    if height is None:
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.bar(data,x=x_label,y=height)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    save_chart(fig, outputDir, chartTitle, static_flag)
    return

#plot pie chart with plotly
#fileName is a csv file with data to be plotted 
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
def plot_pie_chart_px(x_label, fileName, outputDir, chartTitle, height = None, static_flag = False):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.pie(data, values=height, names=x_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    save_chart(fig, outputDir, chartTitle, static_flag)
    return

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#x_label indicates the column name of x axis from the data    COULD BE A DISCRETE VARIABLE
#y_label indicates the column name of y axis from the data    COULD BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
def plot_scatter_chart_px(x_label, y_label, fileName, outputDir, chartTitle, static_flag = False):
    data = pd.read_csv(fileName, encoding='utf-8')
    fig = px.scatter(data, x=x_label, y=y_label)
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    save_chart(fig, outputDir, chartTitle, static_flag)
    return

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#theta_label indicates the column name of the "feature" from the data    SHOULD BE A DISCRETE VARIABLE
#r_label indicates the column name of the value of the feature from the data    CANNOT BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
#null value will cause an unclosed shape. This function default removes all rows contaning null values
def plot_radar_chart_px(theta_label, fileName, outputDir, chartTitle, r_label = None, static_flag = False):
    data = pd.read_csv(fileName, encoding='utf-8')
    if r_label is None:
        r_label = theta_label+"_count"
        data = get_frequencies(data, theta_label)
    data = data.dropna(subset = [theta_label, r_label])
    fig = px.line_polar(data, r=r_label, theta=theta_label, line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(title=chartTitle, title_x=0.5)
    fig.show()
    save_chart(fig, outputDir, chartTitle, static_flag)
    return

#=======================================================================================================================
# debug use
#=======================================================================================================================
# def main():
#     x_label = 'char'
#     height = 'count'
#     hover_label = 'count'
#     chartTitle = 'test chart'
#     fileName =  ''
#     outputDir = 'D:/'
#     #plot_bar_chart(x_label, height, fileName, outputDir, chartTitle, hover_label)
#     plot_radar_chart_px(x_label, height, fileName, outputDir, chartTitle)

# if __name__ == "__main__":
#     main()
