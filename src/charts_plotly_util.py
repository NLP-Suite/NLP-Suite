# Written by Tony Chen Gu in Feb 2022
# Contact: chentony2011@hotmail.com

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"charts_plotly_util",['os','pandas','plotly','kaleido'])==False:
    sys.exit(0)
# if plotly fails, install version 0.1.0 of kaleido
# pip install kaleido==0.1.0post1

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import IO_csv_util

## NOTE:
## some graphing functions has a column placed at the end
## these functions supports the feature of getting frequencies of the categorical variables
## the static_flag is used to indicate whether the chart is static or not

# def create_excel_chart(window,data_to_be_plotted,inputFilename,outputDir,scriptType,
#                        chart_title,
#                        chart_type_list,
#                        column_xAxis_label='',
#                        column_yAxis_label='',
#                        hover_info_column_list=[],
#                        reverse_column_position_for_series_label=False,
#                        series_label_list=[],
#                        second_y_var=0,
#                        second_yAxis_label=''):
# match the excel chart format
def create_plotly_chart(inputFilename,outputDir,chart_title,chart_type_list,cols_to_plot,
                        column_xAxis_label='',
                        column_yAxis_label='',
                        remove_hyperlinks=True,
                        static_flag=False):
    # if we need to remove the hyperlinks, we need to make a temporary data for plotting
    if remove_hyperlinks:
        remove_hyperlinks,inputFilename = IO_csv_util.remove_hyperlinks(inputFilename)

    try:
        data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except pd.errors.ParserError:
        data = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip', sep='delimiter')
    except:
        print("Error: failed to read the csv file named: "+inputFilename)
        return

    headers = data.columns.tolist()
    file_list = []
    for j in range(0,len(chart_type_list)):
        i = chart_type_list[j]
        x_cols = []
        y_cols = ''
        fig = None
        x_cols = headers[cols_to_plot[j][0]]
        y_cols = headers[cols_to_plot[j][1]]
        if i == 'bar':
            if len(chart_type_list) < len(cols_to_plot):
                fig = plot_multi_bar_chart_px(data, chart_title, cols_to_plot)
                file_list.append(save_chart(fig,outputDir,chart_title,static_flag,column_xAxis_label,column_yAxis_label))
                break
            else:
                fig = plot_bar_chart_px(x_cols,inputFilename,chart_title,y_cols)
        elif i == 'pie':
            fig = plot_pie_chart_px(x_cols,inputFilename,chart_title,y_cols)
        #elif(i == 'scatter' or i == 'radar'):
        elif i == 'scatter':
            fig = plot_scatter_chart_px(x_cols,y_cols,inputFilename,chart_title)
        elif i == 'radar':
            fig = plot_radar_chart_px(x_cols,y_cols,inputFilename,chart_title)
        elif i == 'line':
            #plot_multi_line_chart_w_slider_px(fileName, chart_title, col_to_be_ploted, series_label_list = NULL)
            fig = plot_multi_line_chart_w_slider_px(inputFilename,chart_title,cols_to_plot)
            file_list.append(save_chart(fig,outputDir,chart_title,static_flag,column_xAxis_label,column_yAxis_label))
            break
        else:
            print('Chart type not supported '+i+'! Skipped and continue with next chart.')
        file_list.append(save_chart(fig,outputDir,chart_title,static_flag,column_xAxis_label,column_yAxis_label))
    #remove the temporary file
    if remove_hyperlinks:
        os.remove(inputFilename)
    # if the length of thr file list is 1, only return the string to avoid IO_files error
    if len(file_list) == 1:
        return file_list[0]
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
def save_chart(fig, outputDir, chart_title, static_flag, x_label = '', y_label = ''):
    #fig.show()
    if x_label != '':
        fig.update_layout(xaxis_title=x_label)
    if y_label != '':
        fig.update_layout(yaxis_title=y_label)
    if static_flag:
        savepath = os.path.join(outputDir, chart_title + '.png')
        fig.write_image(savepath)
    else:
        # if the chat title has double lines, keep only the last line
        if "\n" in chart_title:
            chart_title=chart_title.split("\n")[1]
        savepath = os.path.join(outputDir, chart_title + '.html')
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
def plot_bar_chart_px(x_label, fileName, chart_title, height = ''):
    data = pd.read_csv(fileName, encoding='utf-8', on_bad_lines='skip')
    if height == '':
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.bar(data,x=x_label,y=height)
    # to ensure the bar doesn't look to wide if x label's length is not enough
    if len(data[x_label]) < 5:
        fig.update_traces(width=0.2)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig

#plot pie chart with plotly
#fileName is a csv file with data to be plotted
#x_label indicates the column name of x axis from the data
#height indicates the column name of y axis from the data
#the output file would be a html file with hover over effect names by the chart title
#duplicates allowed, would add up the counts
def plot_pie_chart_px(x_label, fileName, chart_title, height = ''):
    data = pd.read_csv(fileName, encoding='utf-8', on_bad_lines='skip')
    if height == '':
        height = x_label+"_count"
        data = get_frequencies(data, x_label)
    fig = px.pie(data, values=height, names=x_label)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#x_label indicates the column name of x axis from the data    COULD BE A DISCRETE VARIABLE
#y_label indicates the column name of y axis from the data    COULD BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
def plot_scatter_chart_px(x_label, y_label, fileName, chart_title):
    data = pd.read_csv(fileName, encoding='utf-8', on_bad_lines='skip')
    fig = px.scatter(data, x=x_label, y=y_label)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig

#plot scatter chart with plotly
#fileName is a csv file with data to be plotted
#theta_label indicates the column name of the "feature" from the data    SHOULD BE A DISCRETE VARIABLE
#r_label indicates the column name of the value of the feature from the data    CANNOT BE A DISCRETE VARIABLE
#the output file would be a html file with hover over effect names by the chart title
#null value will cause an unclosed shape. This function default removes all rows contaning null values
def plot_radar_chart_px(theta_label, fileName, chart_title, r_label = None):
    data = pd.read_csv(fileName, encoding='utf-8', on_bad_lines='skip')
    if r_label is None:
        r_label = theta_label+"_count"
        data = get_frequencies(data, theta_label)
    data = data.dropna(subset = [theta_label, r_label])
    fig = px.line_polar(data, r=r_label, theta=theta_label, line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig

#plot multi bar chart (data should be already preprocessed)
# cols_to_plot just like Excel is a double list eg [[1,2],[1,3]]
# no need to call prepare data to be plotted first, all subplots shared the same x axis
def plot_multi_bar_chart_px(data, chart_title, cols_to_plot):
    fig = go.Figure()
    headers = data.columns.values.tolist()
    for col in cols_to_plot:
        fig.add_trace(go.Bar(x=data[headers[col[0]]], y=data[headers[col[1]]], name=headers[col[0]]))
    fig.update_layout(title=chart_title, title_x=0.5)
    if len(cols_to_plot) < 5:
        fig.update_traces(width=0.2)
    return fig

#plot multi line chart
def plot_multi_line_chart_w_slider_px(fileName, chart_title, col_to_be_ploted, series_label_list = None):
    data = pd.read_csv(fileName, encoding='utf-8', on_bad_lines='skip')
    data.fillna(0, inplace=True)
    figs = make_subplots()
    col_name = list(data.head())
    default_series_name = (series_label_list is None)
    # overlay subplots
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
    figs.update_layout(title=chart_title, title_x=0.5)
    # allow for sliders
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
    #save_chart(figs, outputDir, chart_title, False)
    return figs


# written by Simon Bian
# September 2023

def process_and_aggregate_data(data, **kwargs):
    conditions = kwargs.get('conditions', {})
    for col, value in conditions.items():
        if isinstance(value, (list, tuple)):
            data = data[data[col].isin(value)]
        else:
            data = data[data[col] == value]
    agg_column = kwargs.get('agg_column', 'Document')
    agg_data = data.groupby([agg_column, 'Lemma']).size().reset_index(name='Count')
    pivot_data = agg_data.pivot_table(index='Lemma', columns=agg_column, values='Count', fill_value=0)
    return pivot_data


def transform_data(pivot_data, transformation='min-max'):
    if transformation == 'min-max':
        min_val = pivot_data.min().min()
        max_val = pivot_data.max().max()
        return (pivot_data - min_val) / (max_val - min_val)
    elif transformation == 'square-root':
        return np.sqrt(pivot_data)
    elif transformation == 'log':
        return np.log1p(pivot_data)
    elif transformation == 'z-score':
        means = pivot_data.mean()
        stds = pivot_data.std()
        # Skip columns with std very close to zero
        z_scores = pivot_data.subtract(means, axis='columns').divide(stds.where(stds > 1e-5, 1), axis='columns')
        # Replace inf and -inf values with NaN for safety
        z_scores.replace([np.inf, -np.inf], np.nan, inplace=True)
        return z_scores
    else:
        return pivot_data  # return original data if no recognized transformation is given


def visualize_data(data, top_n=60, figsize=(15, 10), y_label='Lemma', x_label='Document', normalize='log',
                   color='YlOrBr', outputname='output_figure'):

    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    numeric_data = data.select_dtypes(include=[np.number])
    sorted_columns = numeric_data.columns.sort_values()
    sorted_pivot_data = numeric_data[sorted_columns][::-1]
    sorted_rows = numeric_data.sum(axis=1).sort_values(ascending=False).index
    sorted_pivot_data = sorted_pivot_data.loc[sorted_rows]
    transposed_data = sorted_pivot_data.head(top_n)
    print("doing calculations...complete!")
    plt.figure(figsize=figsize)
    sns.heatmap(transposed_data, annot=False, fmt='.2f', cmap=color, cbar_kws={'label': normalize})
    ax = plt.gca()
    ax.set_yticks(np.arange(len(transposed_data.index)))
    ax.set_yticklabels(transposed_data.index)
    ax.set_xticks(np.arange(len(transposed_data.columns)))
    ax.set_xticklabels(transposed_data.columns, rotation=90)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(y_label + ' Frequency Visualization over ' + x_label + ' on a ' + normalize + ' Scale')
    plt.savefig(outputname + '.png')
    print(f"Data visualization saved as {outputname}.png.")
    plt.show()


def extract_file_name(link_string):
    import re
    match = re.search(r'\/([^\/]+)\.txt', link_string)
    return match.group(1) if match else link_string

def renamedf(df):
    raw_names = [extract_file_name(col) for col in df.columns]
    sorted_names = sorted(raw_names)

    # Set the sorted names as column names
    df.columns = sorted_names

def main_colormaps(inputFilename, outputDir, params):
    # Menu 1. Select the metrics
    filePath = input("Please enter the ABSOLUTE path of the file: ")
    dataFrame = pd.read_csv(filePath)

    # Menu Display
    try:
        dataFrame = pd.read_csv(filePath)
        print("Thank you. Data reading success.\n")

        # Displaying some basic statistics
        print(f"Number of Columns: {dataFrame.shape[1]}")
        print(f"Number of Rows: {dataFrame.shape[0]}\n")

        print(f"Column names: {dataFrame.columns.tolist()}\n")

        # Display the datatypes
        print("Data types for each column:")
        print(dataFrame.dtypes, "\n")

        # Checking for missing values
        missing_values = dataFrame.isnull().sum()
        if missing_values.any():
            print("Number of missing values for each column:")
            print(missing_values[missing_values > 0], "\n")
        else:
            print("There are no missing values in the dataset.\n")

        # Display summary statistics for numeric columns
        choice = input("Would you like summary statistics for numeric columns? (y/n): ").strip().lower()
        if choice == 'y':
            print("\nSummary Statistics:")
            print(dataFrame.describe())

        # Display top 5 rows
        choice = input("\nWould you like to see the first 5 rows of the data? (y/n): ").strip().lower()
        if choice == 'y':
            print(dataFrame.head())

    except Exception as e:
        print(f"An error occurred: {e}")

    conditions = {}

    while True:
        # Display available columns
        print("\nAvailable columns:")
        print(*dataFrame.columns.tolist(), sep='\n')

        query = input("\nWhich column would you like to visit? Type full name or -1 to end the query: ")
        if query == '-1':
            break
        if query not in dataFrame.columns:
            print("\nError: Invalid column name. Please try again.")
            continue

        while True:
            unique_values = dataFrame[query].unique().tolist()

            if len(unique_values) < 100:
                print("\nUnique values:")
                print(*unique_values, sep='\n')
            else:
                print("\nThere are too many unique values. Please specify the value you're interested in.")

            subquery = input(
                "\nWhich identity would you like to filter for? (-1 for back to upper level, 'remove' to remove filter): ")

            if subquery == '-1':
                break
            elif subquery == 'remove':
                if query in conditions:
                    conditions.pop(query)
                    print(f"\nFilter for column '{query}' has been removed.")
            else:
                if query in conditions:
                    conditions[query].append(subquery)
                else:
                    conditions[query] = [subquery]

    print("\nSelected conditions:")
    print(conditions)

    # Display available columns
    print("\nAvailable columns:")
    print(*dataFrame.columns.tolist(), sep='\n')

    query = input("\nWhich column would you like to aggregate on? Type full name or -1 to go to default as Document: ")
    if query == '-1' or query not in dataFrame.columns:
        query = 'Document'
        print("We will proceed with default")
    else:
        print(query)

    step1 = process_and_aggregate_data(dataFrame, conditions=conditions, agg_column=query)


    def get_transformation_choice():
        print("\nData Transformation Options:")
        print("1. Min-Max scaling")
        print("2. Square Root transformation")
        print("3. Logarithmic transformation")
        print("4. Z-Score normalization")
        print("5. No transformation (Original data)")

        choice = input("Choose a transformation option (1-5): ")
        transformations = {
            '1': 'min-max',
            '2': 'square-root',
            '3': 'log',
            '4': 'z-score',
            '5': None
        }

        return transformations.get(choice, None)


    val = get_transformation_choice()
    step2 = transform_data(step1, val)


    def get_visualization_parameters():
        parameters = {}

        top_n = input("\nHow many top items do you want to display (default 60): ")
        if top_n:
            parameters['top_n'] = int(top_n)

        figsize_width = input("\nFigure width (default 15): ")
        figsize_height = input("Figure height (default 10): ")
        if figsize_width and figsize_height:
            parameters['figsize'] = (int(figsize_width), int(figsize_height))

        y_label = input("\nY label (default 'Lemma'): ")
        if y_label:
            parameters['y_label'] = y_label

        x_label = input("\nX label (default 'Document'): ")
        if x_label:
            parameters['x_label'] = x_label

        dic = {1: "Min-Max", 2: "Square Root", 3: "Log Trans", 4: "z-score", 5: "No transformation"}
        if val in dic:
            parameters['normalize'] = dic[val]
        else:
            parameters['normalize'] = dic[5]

        color = input(
            "\nColor for the heatmap (default 'YlOrBr'). You can go to https://camo.githubusercontent.com/7b6d4ecccbf250ccffee665f157e63b353916d60d6e8ab9a14dffe461400a0ed/68747470733a2f2f6a6c636f746f2e6769746875622e696f2f696d672f6272657765725f73657175656e7469616c2e706e67 to see color palletes ")
        if color:
            parameters['color'] = color

        name = input("\nHow would you like to name your figure? Default is output_figure ")
        if name:
            parameters['outputname'] = name

        return parameters


    if input("Do you want NOT to normalize name if your headers contain filename? type NO to reject.") == 'no':
        pass
    else:
        renamedf(step2)

    parameters = get_visualization_parameters()
    visualize_data(step2, **parameters)

#=======================================================================================================================
# debug use
#=======================================================================================================================
# def main():
#     x_label = 'char'
#     height = 'count'
#     hover_label = 'count'
#     chart_title = 'test chart'
#     fileName =  'C:/Users/Tony Chen/Desktop/NLP_working/Test OutputNLP_NVA_conll_eng_Noun_POSTAG_list_frequencies.csv'
#     outputDir = 'C:/Users/Tony Chen/Desktop/NLP_working'

#     #plot_bar_chart(x_label, height, fileName, outputDir, chart_title, hover_label)

#     #plot_radar_chart_px(x_label, height, fileName, outputDir, chart_title)
#     plot_multi_line_chart_w_slider_px(fileName,outputDir,chart_title)

# if __name__ == "__main__":
#     main()
