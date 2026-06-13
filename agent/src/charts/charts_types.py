# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023
import io
import logging
import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


def multiple_barchart(datalist, outputFilename, var, ntopchoices):
    # Read each file in datalist into a pandas DataFrame
    tempdatalist = [pd.read_csv(i, encoding="utf-8", on_bad_lines="skip") for i in datalist]

    # Process each DataFrame to count the top 'ntopchoices' values of the column 'var'
    newDatalist = [
        df[var].value_counts().reset_index().rename(columns={"index": var, var: "Frequency"}).head(ntopchoices)
        for df in tempdatalist
    ]

    # Create a subplot layout
    fig = make_subplots(
        rows=2,
        cols=(len(datalist) // 2) + (len(datalist) % 2),
        subplot_titles=[f"Algorithm {i + 1}" for i in range(len(datalist))],
    )

    # Add the bar charts for the first row
    for i in range(len(newDatalist)):
        row = 1 if i < (len(datalist) + 1) // 2 else 2
        col = i % ((len(datalist) + 1) // 2) + 1
        fig.add_trace(
            go.Bar(
                x=newDatalist[i][var],
                y=newDatalist[i]["Frequency"],
                name=f"Algorithm {i + 1}",
            ),
            row=row,
            col=col,
        )

    # Save the plot to an HTML file
    fig.write_html(outputFilename)
    return outputFilename


# written by Samir Kaddoura, March 2023


# var is the variable of choice to apply the boxplot on
# bycategory is a boolean that chooses whether we want to split it by category along a categorical variable, determined by the following category argument
# points is the choice to represent all points of data, the outliers, or none of them, it should be given through a dropdown menu
# color is another choice of categorical variable to split the data along
def boxplot(
    data,
    outputFilename,
    var,
    points,
    bycategory=None,
    category=None,
    color=None,
    inputFileData="",
):
    if points == "All points":
        points = "all"
    elif points == "no points":
        points = False
    elif points == "outliers only":
        points = "outliers"
    if color == "":
        color = None

    if inputFileData:
        data = pd.read_csv(io.StringIO(inputFileData), encoding="utf-8", on_bad_lines="skip")
    elif isinstance(data, str):
        data = pd.read_csv(inputFileData, encoding="utf-8", on_bad_lines="skip")

    if "int" not in str(type(data[var][0])) and "float" not in str(type(data[var][0])):
        logger.info(
            'Warning The "Boxplots" option requires a numeric field.\n\nPlease, use the dropdown menu to select a numeric csv file field for visualization and try again.'
        )
        return

    if bycategory != 0 and bycategory is not None and category is not None:
        if "str" not in str(type(data[category][0])):
            logger.info(
                'Warning The "Split data by category" Boxplots option requires a CATEGORICAL "csv file field"".\n\nPlease, use the "csv file field" dropdown menu to select a CATEGORICAL field and try again.'
            )
            return

    if color is not None:
        if "str" not in str(type(data[color][0])):
            logger.info(
                'Warning The Boxplots with "Split data by category" and color options requires a secodn CATEGORICAL "csv file field" for the color option".\n\nPlease, use the second "csv file field" dropdown menu to select a CATEGORICAL field and try again.'
            )
            return

    if not bycategory:
        fig = px.box(data, y=var, points=points)
    else:
        fig = px.box(data, x=category, y=var, points=points, color=color)
    fig.write_html(outputFilename)
    return outputFilename


# written by Samir Kaddoura, March 2023


# var1 is the first categorical variable, lengthvar1 is the amount of var 1: should take values of 5 or 10
# var2 is the second categorical variable, lengthvar2 is the amount of var 2: should take values of 5,10 or 20
# var3 is the third categorical variable, lengthvar3 is the amount of var 3: should take values of 5,10, 20 or 30
# All these recommendations are for performance
# three_way_Sankey is a boolean variable that dictates whether the returned Sankey is 2way or 3way. True for 3 variables, false for 2 variables
def Sankey(
    data,
    outputFilename,
    var1,
    lengthvar1,
    var2,
    lengthvar2,
    three_way_Sankey,
    var3=None,
    lengthvar3=None,
):
    # if pd.__version__[0] == '2':
    #     mb.showwarning(title='Warning',
    #                    message='The Sankey algorithm is incompatible with a version of pandas higher than 2.0\n\nIn command line, please, pip unistall pandas and pip install pandas==1.5.2.\n\nMake sure you are in the right NLP environment by typing conda activate NLP')

    finalframe = pd.DataFrame()
    if isinstance(data, str):
        try:
            data = pd.read_csv(data, encoding="utf-8", on_bad_lines="skip")
        except Exception:
            logger.info(
                "Warning, the input file  %s  is empty.\n\nNo Sankey flowchart can be produced.\n\nPlease, check your input file and try again.",
                data,
            )
            return

    if not isinstance(data[var1][0], float):  # nan values are float, but do not need to be checked here
        if not isinstance(data[var1][0], str) or not isinstance(data[var2][0], str):
            logger.info(
                "Waring, all csv file fields should be categorical for a Saneky flowchart.\n\nPlease, select categorical field(s) (i.e., fields with string values), rather than continuous numeric field(s), and try again. "
            )

    if three_way_Sankey:
        # 3 variables
        data[var1] = data[var1].str.lower()
        tempframe = pd.DataFrame(data[var1].value_counts().head(lengthvar1)).reset_index()
        try:
            finalframe = data[data[var1].isin(list(set(tempframe["index"])))]
        except Exception:
            if len(finalframe) == 0:
                logger.info(
                    "Warning The dataframe computed by the Sankey flowchart is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2"
                )
                return

            finalframe = data[data[var1].isin(list(set(tempframe.index)))]
        tempframe2 = pd.DataFrame(finalframe[var2]).value_counts().head(lengthvar2).reset_index()
        tempframe3 = pd.DataFrame(finalframe[var3]).value_counts().head(lengthvar3).reset_index()
        finalframe = finalframe[finalframe[var2].isin(list(set(tempframe2[var2])))]
        finalframe = finalframe[finalframe[var3].isin(list(set(tempframe3[var3])))]
        finalframe = finalframe.reset_index(drop=True)
        sourcelist = list(range(0, len(set(finalframe[var1])) + len(set(finalframe[var2]))))
        source = [item for item in sourcelist for _ in range(len(set(finalframe[var2])) + len(set(finalframe[var3])))]
        target1 = list(range(0, len(set(finalframe[var2])) + len(set(finalframe[var3]))))
        target2 = [x + len(set(finalframe[var1])) for x in target1]
        target = target2 * len(sourcelist)

        labelvector = sorted(set(finalframe[var1])) + sorted(set(finalframe[var2])) + sorted(set(finalframe[var3]))
        valuevector = []

        for i in sorted(list(set(finalframe[var1]))):
            tempvec = []
            tempframe = finalframe[finalframe[var1] == i]
            wantedframe = (
                pd.DataFrame(tempframe[var2].value_counts())
                .reset_index()
                .rename(columns={"index": var2, var2: "Frequency"})
            )
            for j in sorted(list(set(finalframe[var2]))):
                if j not in list(wantedframe[var2]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var2] == j]["Frequency"])[0])
            tempvec = tempvec + list(np.repeat(0, len(target2) - len(tempvec)))
            valuevector = valuevector + tempvec
        for i in sorted(list(set(finalframe[var2]))):
            tempvec = []
            tempframe = finalframe[finalframe[var2] == i]
            wantedframe = (
                pd.DataFrame(tempframe[var3].value_counts())
                .reset_index()
                .rename(columns={"index": var3, var3: "Frequency"})
            )
            tempvec = list(np.repeat(0, len(set(finalframe[var2]))))
            for j in sorted(list(set(finalframe[var3]))):
                if j not in list(wantedframe[var3]):
                    tempvec.append(0)
                else:
                    tempvec.append(list(wantedframe[wantedframe[var3] == j]["Frequency"])[0])
            valuevector = valuevector + tempvec

    else:
        # 2 variables

        data[var1] = data[var1].str.lower()
        tempframe = data[var1].value_counts().head(lengthvar1).reset_index()
        tempframe.columns = [var1, "Frequency"]
        finalframe = data[data[var1].isin(tempframe[var1])]

        tempframe2 = finalframe[var2].value_counts().head(lengthvar2).reset_index()
        tempframe2.columns = [var2, "Frequency"]
        finalframe = finalframe[finalframe[var2].isin(tempframe2[var2])]
        finalframe.reset_index(drop=True, inplace=True)

        source = []
        target = []
        valuevector = []

        for i, val1 in enumerate(finalframe[var1].unique()):
            for j, val2 in enumerate(finalframe[var2].unique()):
                source.append(i)
                target.append(j + len(finalframe[var1].unique()))
                valuevector.append(len(finalframe[(finalframe[var1] == val1) & (finalframe[var2] == val2)]))

        labelvector = list(finalframe[var1].unique()) + list(finalframe[var2].unique())

        # except:
        #     mb.showwarning(title='Warning',
        #                    message='The dataframe computed by the Sankey flowchart is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2')
        #
        #
        # for i in sorted(list(set(finalframe[var1]))):
        #         columns={'index': var2, var2: 'Frequency'})
        #     for j in sorted(list(set(tempdata[var2]))):
        #         if j not in list(tempdata[var2]):

    fig = go.Figure(
        go.Sankey(
            link=dict(source=source, target=target, value=valuevector),
            node=dict(label=labelvector, pad=35, thickness=10),
        )
    )
    fig.write_html(outputFilename)

    return outputFilename


# created by Samir Kaddoura, November 2022

# Function creates a new column that identifies the documents based on a specific interest variable
# two inputs taken: data is the dataset in question, interest is a vector that the user will have to define, as it changes depending on the corpus


def separator(data, interest, algorithm):
    interestvector = []  # empty interest vector
    id_list = []  # empty id list in which we record every entry in the dataset that contains one of the interest inputs

    for i in range(0, len(data)):  # check every entry in dataset
        for j in range(0, len(interest)):  # check every interest vector
            if re.search(
                ".*" + interest[j] + "[^.]", data["Document"][i]
            ):  # if the name of the document contains a word of intersest, we append that word to a vector
                interestvector.append(interest[j])
                id_list.append(i)  # append the index of the row that contains the interest value

    finaldata = data.loc[id_list, :]  # filter dataset by row with interest values
    finaldata["interest"] = interestvector  # add interest column
    if finaldata.empty:
        logger.info(
            "Warning %s",
            "The "
            + algorithm
            + " algorithm has produced an empty dataframe.\n\nPlease, make sure that the 'Filename label/part' you have entered are in the document name under the Document field of your input file.\n\nREMEMBER THAT SEARCH WORDS ARE CASE SENSITIVE.\n\nPlease, try again.",
        )
    return finaldata


# written by Samir Kaddoura, March 2023


# Returns sunburst piechart. Input a dataframe provided by the NLP suite as data, interest is a vector including interest separation based on separator (as defined above)
# label is a categorical variable we're interested in
# first_sentences is the n first sentences
# last_sentences is the n last sentences
# half_text is a boolean defining whether to split the text in half or not
# beginning_and_end is a boolean that dictates if its a two-level or three level Sunburst
def Sunburst(
    data,
    outputFilename,
    outputDir,
    case_sensitive,
    interest,
    label,
    beginning_and_end=False,
    first_sentences=None,
    last_sentences=None,
    half_text=None,
):
    if isinstance(data, str):
        data = pd.read_csv(data, encoding="utf-8", on_bad_lines="skip")
        # @@@ nan values will break the code
        data = data.fillna("Blank/missing value")
    # The presence of a Nan value will classify the object as float
    if not isinstance(data[label][0], str):
        logger.info(
            "Warning The csv file field selected should be categorical.\n\nYou should select a categorical field, rather than a continuous numeric field, and try again."
        )
    # the last 3 arguments are optional. If first_sentences is specified and last_sentences is not or vice versa, we return a message stating they must both be specified or absent at the same time
    if (first_sentences is None and last_sentences is not None) or (
        first_sentences is not None and last_sentences is None
    ):
        return "both number of first sentences and number of last sentences have to be specified or absent at the same time"
    else:  # Otherwise, we run the Sunburst
        tempdata = separator(data, interest, "Sunburst")  # Create "interest" variable
        if not beginning_and_end:
            if (
                half_text or (first_sentences is None and last_sentences is None)
            ):  # If half text is true or both number of first sentences and last sentences is absent, we split each text in half and attribute a "beginning" half and "end" half
                first_docID = tempdata["Document ID"].iloc[0]
                ogdata = tempdata[tempdata["Document ID"] == first_docID]  # take the first document

                ogdata1 = ogdata[ogdata["Sentence ID"] <= len(ogdata) / 2]  # split the document by first half
                oglist1 = list(np.repeat("Beginning", len(ogdata1)))
                ogdata1["Beginning or End"] = oglist1  # add list "Beginning" the length of the first half

                ogdata2 = ogdata[ogdata["Sentence ID"] > len(ogdata) / 2]  # split the document by first half
                oglist2 = list(np.repeat("End", len(ogdata2)))
                ogdata2["Beginning or End"] = oglist2  # add list "End" the length of the first half

                finaldata = pd.concat([ogdata1, ogdata2])  # merge dataframes
                if not finaldata.empty:
                    for i in range(2, max(data["Document ID"]) + 1):  # iterate same process for each document
                        intermediatedata = tempdata[tempdata["Document ID"] == i]

                        intermediatedata1 = intermediatedata[
                            intermediatedata["Sentence ID"] <= len(intermediatedata) / 2
                        ]
                        intermediatelist1 = list(np.repeat("Beginning", len(intermediatedata1)))
                        intermediatedata1["Beginning or End"] = intermediatelist1

                        finaldata = pd.concat([finaldata, intermediatedata1])

                        intermediatedata2 = intermediatedata[
                            intermediatedata["Sentence ID"] > len(intermediatedata) / 2
                        ]
                        intermediatelist2 = list(np.repeat("End", len(intermediatedata2)))
                        intermediatedata2["Beginning or End"] = intermediatelist2

                        finaldata = pd.concat([finaldata, intermediatedata2])
                    # finaldata not empty
                    # @@@ nan values will break the code
                    finaldata = finaldata.fillna("Blank/missing value")
                    fig = px.sunburst(finaldata, path=["interest", "Beginning or End", label])  # return Sunburst
                else:
                    if finaldata.empty:
                        logger.info(
                            "Warning The Sunburst algorithm has produced an empty dataframe.\n\nPlease, make sure that the 'Filename label/part' you have entered are in the document name under the Document field of your input file.\n\nREMEMBER THAT SEARCH WORDS ARE CASE SENSITIVE.\n\nPlease, try again."
                        )

            else:
                tempdata1 = tempdata[
                    tempdata["Sentence ID"] <= first_sentences
                ]  # all observations with the first n sentences

                list1 = list(np.repeat("Beginning", len(tempdata1)))  # List repeating 'Beginning'

                for i in range(1, max(data["Document ID"]) + 1):
                    intermediatedata1 = tempdata[tempdata["Document ID"] == i]
                    intermediatedata2 = intermediatedata1[
                        intermediatedata1["Sentence ID"] > (len(intermediatedata1) - last_sentences)
                    ]
                    tempdata1 = (
                        pd.concat([tempdata1, intermediatedata2]).reset_index().drop(columns={"index"})
                    )  # all observations with last n sentences
                    if len(tempdata1) == 0:
                        logger.info(
                            "Warning The dataframe computed by theSunburst chart algorithm is empty.\n\nIt is likely that you are using a version of pandas > 1.5.2. If so, in command line please, pip unistall pandas and pip install pandas==1.5.2"
                        )
                        return

                list2 = list(np.repeat("End", len(tempdata1) - len(list1)))  # List repeating 'End'
                finallist = list1 + list2  # Create a vector defining if the sentence is at the beginning or the end
                finaldata = tempdata1
                finaldata["Beginning or End"] = finallist

                fig = px.sunburst(finaldata, path=["interest", "Beginning or End", label])  # create sunburst chart
        else:
            # @@@ nan values will break the code
            tempdata = tempdata.fillna("Blank/missing value")
            fig = px.sunburst(tempdata, path=["interest", label])
            finaldata = tempdata
        if finaldata.empty:
            outputFilename = None
        else:
            fig.write_html(outputFilename)

        return outputFilename


# written by Samir Kaddoura, March 2023

# This function takes the data, an interest vector defined the same way as in the Sunburst function,
#   a variable of choice (should be categorical) var,
#   a boolean variable to dictate if the user wants to observe an additional variable with "extra_dimension_average",
#   the numerical variable of choice average_variable


# The graph shows the frequencies of each group by default depending on the interest vector and the initial variable of choice. If specified, it shows the average of average_variable per group
def Treemap(
    data,
    outputFilename,
    interest,
    csv_file_field,
    extra_dimension_average,
    average_variable=None,
):
    if isinstance(data, str):  # convert data to dataframe
        data = pd.read_csv(data, encoding="utf-8", on_bad_lines="skip")
    # The presence of a Nan value will classify the object as float
    if not isinstance(data[csv_file_field][0], str):
        logger.info(
            "Warning The csv file field selected should be categorical.\n\nYou should select a categorical field, rather than a continuous numeric field, and try again."
        )
    if extra_dimension_average and not isinstance(data[average_variable][0], np.float64):
        logger.info(
            "Warning The csv file field selected should be numeric.\n\nYou should select a numeric field, rather than an alphabetic field, and try again."
        )
        return
    data = separator(data, interest, "Treemap")  # use separator function to create interest vector
    if data.empty:
        outputFilename = None
    else:
        if not extra_dimension_average:  # return regular 2 variable graph if false
            fig = px.treemap(data, path=[px.Constant("Total Frequency"), "interest", csv_file_field])
        else:  # return graph with extra variable if true
            fig = px.treemap(
                data,
                path=[px.Constant("Total Frequency"), "interest", csv_file_field],
                color=average_variable,
                color_continuous_scale="RdBu",
            )
        fig.write_html(outputFilename)
    return outputFilename


# written by Samir Kaddoura, March 2023

# choose a data set, a variable to show the evolution through time, outputFilename to save output, monthly and yearly are boolean variables
# If both are passed as false, return daily graph
# if monthly or yearly is passed as true, return monthly or yearly graph respectively
# Both cannot be simultaneously true


# written by Simon Bian
# September 2023


def process_and_aggregate_data(data, **kwargs):
    conditions = kwargs.get("where_column", {})  # WHERE conditions
    agg_column = kwargs.get("groupby_column")  # GROUP BY column
    select_columns = kwargs.get("select_column", [])  # SELECT columns
    for col, value in conditions.items():
        if isinstance(value, (list, tuple)):
            data = data[data[col].isin(value)]
        else:
            data = data[data[col] == value]

    if not select_columns:
        select_columns = [col for col in data.columns if col != agg_column]
        # If agg_column is not specified, we cannot proceed with grouping; handle this case as needed
    if not agg_column:
        raise ValueError("The 'groupby_column' parameter is required for aggregation.")
        logger.info(
            "Due to exception in missing groupby_column parameter required for aggregation, the function is aborted"
        )
        return
        # Group by the specified column along with select_columns and calculate the count
    agg_data = data.groupby([agg_column, select_columns]).size().reset_index(name="Count")
    # Pivot the table. If select_columns is empty, this will consider all other columns.
    pivot_data = agg_data.pivot_table(index=select_columns, columns=agg_column, values="Count", fill_value=0)
    return pivot_data


def transform_data(pivot_data, transformation="min-max"):
    if transformation == "min-max":
        min_val = pivot_data.min().min()
        max_val = pivot_data.max().max()
        return (pivot_data - min_val) / (max_val - min_val)
    elif transformation == "square-root":
        return np.sqrt(pivot_data)
    elif transformation == "log":
        return np.log1p(pivot_data)
    elif transformation == "z-score":
        means = pivot_data.mean()
        stds = pivot_data.std()
        # Skip columns with std very close to zero
        z_scores = pivot_data.subtract(means, axis="columns").divide(stds.where(stds > 1e-5, 1), axis="columns")
        # Replace inf and -inf values with NaN for safety
        z_scores.replace([np.inf, -np.inf], np.nan, inplace=True)
        return z_scores
    else:
        return pivot_data  # return original data if no recognized transformation is given


def visualize_data(
    data,
    top_n=60,
    figsize=(15, 10),
    y_label="Lemma",
    x_label="Document",
    normalize="log",
    color="YlOrBr",
    outputname="output_figure",
):
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    numeric_data = data.select_dtypes(include=[np.number])
    sorted_columns = numeric_data.columns.sort_values()
    sorted_pivot_data = numeric_data[sorted_columns][::-1]
    sorted_rows = numeric_data.sum(axis=1).sort_values(ascending=False).index
    sorted_pivot_data = sorted_pivot_data.loc[sorted_rows]
    transposed_data = sorted_pivot_data.head(top_n)
    plt.figure(figsize=figsize)
    try:
        sns.heatmap(
            transposed_data,
            annot=False,
            fmt=".2f",
            cmap=color,
            cbar_kws={"label": normalize},
        )
    except Exception:
        logger.info("There appears to be ann error with cmap; we revert to default ")
        sns.heatmap(
            transposed_data,
            annot=False,
            fmt=".2f",
            cmap="YlOrBr",
            cbar_kws={"label": normalize},
        )
    ax = plt.gca()
    ax.set_yticks(np.arange(len(transposed_data.index)))
    ax.set_yticklabels(transposed_data.index)
    ax.set_xticks(np.arange(len(transposed_data.columns)))
    ax.set_xticklabels(transposed_data.columns, rotation=90)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(y_label + " Frequency Visualization over " + x_label + " on a " + normalize + " Scale")
    plt.savefig(outputname + ".png")
    logger.info(f"Data visualization saved as {outputname}.png.")
    # plt.show() // we don't need to show it because we have that other option
