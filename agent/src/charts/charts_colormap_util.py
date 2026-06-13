# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023
import io
import logging
import os
import re

import IO_csv_util
import numpy as np
import pandas as pd
import plotly.express as px
from charts_types import process_and_aggregate_data, transform_data, visualize_data


def extract_file_name(link_string):
    import re

    match = re.search(r"\/([^\/]+)\.txt", link_string)
    return match.group(1) if match else link_string


def renamedf(df):
    raw_names = [extract_file_name(col) for col in df.columns]
    sorted_names = sorted(raw_names)
    df.columns = sorted_names


# csv_file_categorical_field_list is a double list with each list containing the combination csv field & search values
#   for example, [[Document | Mao, Deng, Xi][NER | PERSON][WORD|'']
# params is a single lst with the max number of rows and RGB color, e.g., [20, 255 166 0]


def read_filename_color(inputFilename):
    try:
        dataFrame = pd.read_csv(inputFilename)
        # Displaying some basic statistics

        # Display the datatypes

        # Checking for missing values
        missing_values = dataFrame.isnull().sum()
        if missing_values.any():
            logger.info("Number of missing values for each column:")
            logger.info("%s \n", missing_values[missing_values > 0])
        else:
            logger.info("There are no missing values in the dataset.\n")
        return dataFrame
        # Display summary statistics for numeric columns
    # if choice == 'y':

    # Display top 5 rows
    # if choice == 'y':

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return 0


def get_transformation_choice(choice=5):
    transformations = {1: "min-max", 2: "square-root", 3: "log", 4: "z-score", 5: None}
    return transformations.get(choice, None)


def further_group(df, major_parm, small_prm):
    ## majro_parm = str, small_prm = list of string to be regexed against a
    ## as we need to check suffix of string for GROUP BY
    col = df[major_parm].value_counts().index.tolist()
    mps_suffix = {}
    for i in col:
        for j in small_prm:
            if re.search(".*" + str(j) + ".*", str(i)):
                mps_suffix[str(i)] = str(j)
    df["Real_" + major_parm] = df[major_parm].map(mps_suffix)


def sql_commands(s, dataFrame):
    """
    In sql, we all know the famous quote, SELECT * FROM any_sort_of_datatable WHERE * GROUP BY *
    This command is in effect doing that.
    The  WHERE command, in which you know at which point ROWS you'd like to filter fow
    The  GROUP BY command, in which COLUMN's FIELDS you know you would like to aggregate the RESULT upon
    The SELECT command, in which you know which COLUMNS you'd like to present to the viewers
    The return is, in essence, a pythonic database searching command that achieves this effect
    """
    WHERE_s = s[1:-1]
    GROUPBY_s = s[0][0].split("|")
    GROUPBY = GROUPBY_s[0]
    add = GROUPBY_s[1]
    if add:
        all_values = add.split(", ")
        further_group(dataFrame, GROUPBY, all_values)
        logger.info("The function detected string values in input, and they were mapped accordingly")
        GROUPBY = "Real_" + GROUPBY
    SELECT = s[-1][0].replace("|", "")
    WHERE = {}
    if WHERE_s:
        for condition in WHERE_s:
            cmd = condition[0].split("|")
            mtc = cmd[1].split(", ")
            WHERE[cmd[0]] = mtc
    return WHERE, GROUPBY, SELECT


def special_sql_commands(s, dataFrame):
    """
    THIS IS FOR sunburst / treemaps only
    For the first parameter, it should be fixed to be partial match or none
    For all other parameters, it should be fixed to fixed match or none
    Example:
        Given: NY_1_piggy, NY_2_bank, NY_3_piggy, NY_2_bank
        Entering piggy would yield partial match: NY_1_piggy, NY_3_piggy aggregates
        .............. would yield fixed match: None. Only if entering NY_1_piggy would yield crrect
    Example2:
        In NER, entering O would yield partial match: PERSON, ORGANIZATION, IDEOLOGY, O....
        Entering O would yield fixed match: O only.
    """
    WHERE_s = s[1:]
    GROUPBY_s = s[0][0].split("|")
    GROUPBY = GROUPBY_s[0]
    add = GROUPBY_s[1]
    if add:
        all_values = add.split(", ")
        further_group(dataFrame, GROUPBY, all_values)
        logger.info("The function detected string values in input, and they were mapped accordingly")
        GROUPBY = "Real_" + GROUPBY
    WHERE = {}
    if WHERE_s:
        for condition in WHERE_s:
            cmd = condition[0].split("|")
            mtc = cmd[1].split(", ")
            WHERE[cmd[0]] = mtc
    return WHERE, GROUPBY


from matplotlib.colors import LinearSegmentedColormap

logger = logging.getLogger(__name__)


def interpolate_colors(color1, color2, num_colors):
    color1, color2 = [x / 255.0 for x in color1], [x / 255.0 for x in color2]
    return [np.array(color1) * (1 - ratio) + np.array(color2) * ratio for ratio in np.linspace(0, 1, num_colors)]


def cmaps(start_color, end_color):
    colors = interpolate_colors(start_color, end_color, 256)
    cmap_custom = LinearSegmentedColormap.from_list("custom", colors, N=256)
    return cmap_custom


def main_colormap(inputFilename, outputDir, csv_file_categorical_field_list, params, inputFileData=""):
    if inputFileData:
        dataFrame = pd.read_csv(io.StringIO(inputFileData))
    else:
        dataFrame = read_filename_color(inputFilename)
    WHERE, GROUPBY, SELECT = sql_commands(csv_file_categorical_field_list, dataFrame)
    step1 = process_and_aggregate_data(dataFrame, where_column=WHERE, groupby_column=GROUPBY, select_column=SELECT)
    step2 = transform_data(step1)  # There needs to be a GUI to allow transformation, but...
    # We proceed with default instead perhaps...
    if GROUPBY == "Document":
        renamedf(step2)  # We rename to file relative location, not absolute location
    try:
        cmap = cmaps(eval(params[1]), eval(params[2]))
    except (ValueError, TypeError):
        cmap = cmaps((135, 207, 236), (0, 0, 255))
    import IO_files_util

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, "", outputDir, ".colormetric")
    visualize_data(
        step2,
        outputname=outputFilename,
        color=cmap,
        top_n=params[0],
        normalize=params[-1],
    )  # There is no GUI yet...

    return outputFilename


def select_and_counting(df, select_and_count):
    grouped = df.groupby(select_and_count).size()
    counts_df = grouped.reset_index(name="values")
    new_df = pd.merge(df, counts_df, on=select_and_count, how="left")
    return new_df
    # This one tells us for each word, how many times it appear
    # THIS IS FOR SUNBURST ? TREE MAP


def where_data(data, **kwargs):
    conditions = kwargs.get("where_column", {})  # WHERE conditions
    for col, value in conditions.items():
        if value == "" or value == [""]:
            continue
        if isinstance(value, (list, tuple)):
            data = data[data[col].isin(value)]
    # THIS FUNCTION IS DOING: SELECT FROM DATA WHERE cond_1, cond_2, ... con_n for ** kwargs
    return data


def fixed_transform_helper(df, prt, nms):
    nms = int(nms)
    top_X_items = list(df[prt].value_counts()[0:nms].keys())
    df = df[df[prt].isin(top_X_items)]
    return df


def fixed_transform(df, fixed_value):
    for col in df.columns:
        if col != "counts":
            df = fixed_transform_helper(df, col, fixed_value)
    return df


def rate_prop_helper(df, prt, nms):
    nms = int(nms)
    top_X_items = list(df[prt].value_counts()[0:nms].keys())
    df = df[df[prt].isin(top_X_items)]
    return df


def rate_prop(df, rt, base):
    for col in df.columns:
        if col != "counts":
            df = rate_prop_helper(df, col, base)
            base = base * rt
    return df


# Option 1: Fixed Parameter Filtering 50-100 (default 50)
# Option 2: Rate-Propagating Parameter Filtering: 2 values Rate filtering 3 value Base filtering value def = 40
# Option 3: No filter at all


# THIS IS AN ABBREVIATED VERSION FOR The sunburst / treemap


def Sunburst_Treemap(
    inputFileName,  # Change inputFileName to use string contents of csv
    outputFilename,
    outputDir,
    csv_file_categorical_field_list,
    suntree,
    fixed_param_var,
    rate_param_var,
    base_param_var,
    filter_options_var,
    file_data="",
):
    import io

    logger.info("%s %s %s %s", fixed_param_var, rate_param_var, base_param_var, filter_options_var)
    if file_data != "":
        data = pd.read_csv(io.StringIO(file_data))
    else:
        data = pd.read_csv(inputFileName)
    WHERE, GROUPBY = special_sql_commands(csv_file_categorical_field_list, data)
    data = where_data(data, where_column=WHERE)
    select_and_count = [GROUPBY]
    select_and_count.extend(list(WHERE.keys()))
    df = select_and_counting(data, select_and_count)
    df_grouped = df.groupby(select_and_count).size().reset_index(name="counts")

    df_grouped.to_csv(outputDir + os.sep + "Output_Csv_intermediate.csv", index=False)
    logger.info(df_grouped)
    if filter_options_var == "Fixed parameter":
        df_grouped = fixed_transform(df_grouped, int(fixed_param_var))
        logger.info("Fixed parameter applied")
    if filter_options_var == "Propagating parameter":
        df_grouped = rate_prop(df_grouped, int(rate_param_var), int(base_param_var))
        logger.info("Propagating parameter applied")
    logger.info(df_grouped)
    if suntree:
        fig = px.sunburst(df_grouped, path=select_and_count, values="counts")  # Ensure the hierarchy levels are correct
    else:
        fig = px.treemap(df_grouped, path=select_and_count, values="counts")
    fig.write_html(outputFilename)
    return outputFilename


def visualize_colormap_data(
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
    except (ValueError, TypeError):
        logger.info("There appears to be an error with cmap; we revert to default")
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
    x_label = x_label.replace("Real_", "")
    ax.set_xlabel(x_label)
    ax.set_title("Colormap/heatmap of " + y_label + " Frequency by " + x_label + " Values (" + normalize + " Scale)")
    plt.savefig(outputname + ".png")
    logger.info(f"Data visualization saved as {outputname}.png.")
    # plt.show() // we don't need to show it because we have that other option


def colormap(inputFilename, outputDir, csv_file_categorical_field_list, params, inputFileData=""):
    filesToOpen = []
    if inputFileData:
        dataFrame = pd.read_csv(io.StringIO(inputFileData))
    else:
        dataFrame = read_filename_color(inputFilename)

    WHERE, GROUPBY, SELECT = sql_commands(csv_file_categorical_field_list, dataFrame)
    # step1 is a dataframe
    step1 = process_and_aggregate_data(dataFrame, where_column=WHERE, groupby_column=GROUPBY, select_column=SELECT)
    if step1.empty:
        logger.info(
            "No search values found"
            + "No combination of csv file fields and search values were found in your input file.\n\n"
            + str(csv_file_categorical_field_list)
            + "\n\nPlease, make sure to check whether\n   1. you have not entered the same field twice;\n   2. you are using a case sensitive search option.\n\nPlease, click on the Reset button and start again."
        )
        return
    colormap_dataframe_csv_filename = outputDir + os.sep + "colormap_dataframe.csv"
    filesToOpen.append(colormap_dataframe_csv_filename)
    # add headers to dataframe
    if GROUPBY == "Document":
        if len(WHERE) == 0:
            for i in range(len(list(step1.columns.values))):
                header = list(step1.columns.values)[i]
                head, tail = os.path.split(header)
                step1 = step1.rename(columns={header: "Frequency in: " + tail})
    step1.to_csv(colormap_dataframe_csv_filename, index=True)

    step2 = transform_data(step1)  # There needs to be a GUI to allow transformation, but...
    # We proceed with default instead perhaps...
    if GROUPBY == "Document":
        # if len(WHERE)==0:
        # when a specific document part (e.g., Book1 for Harry Potter) is not entered by the user
        #   the document will contain the entire path along with an hypewrlink and this may be very cumbersome to display in the X axis
        #   must remove hyperlink and display document tail only
        # for i in range(len(list(step2.columns.values))):
        renamedf(step2)  # We rename to file relative location, not absolute location
    try:
        cmap = cmaps(eval(params[1]), eval(params[2]))
    except (ValueError, TypeError):
        cmap = cmaps((135, 207, 236), (0, 0, 255))
    import IO_files_util

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, "", outputDir, ".colormetric")

    visualize_colormap_data(
        step2,
        top_n=params[0],
        y_label=SELECT,
        x_label=GROUPBY,
        normalize=params[-1],
        color=cmap,
        outputname=outputFilename,
    )  # There is no GUI yet...
    filesToOpen.append(outputFilename)
    return filesToOpen


def timechart(
    data,
    outputFilename,
    var,
    date_format_var,
    cumulative,
    monthly=None,
    yearly=None,
    inputFileData="",
):
    if inputFileData:
        try:
            data = pd.read_csv(io.StringIO(inputFileData), encoding="utf-8", on_bad_lines="skip")
            headers = IO_csv_util.get_csvfile_headers(data, inputFileData=inputFileData)
        except Exception as e:
            logger.info(f"Error processing inputFileData: {e}")
            return
    elif isinstance(data, str):
        try:
            headers = IO_csv_util.get_csvfile_headers(data)
            data = pd.read_csv(data, encoding="utf-8", on_bad_lines="skip")
        except Exception as e:
            logger.info(f"Error loading file {data}: {e}")
            return
    if "Date" in headers:
        date_field = "Date"
    elif "Document" in headers:
        date_field = "Document"
    else:
        logger.info(
            "Warning. The time mapper algorithm requires a csv input file with either a 'Date' or 'Document' field in the headers.\n\nPlease, select the expected csv file and try again."
        )
        return
    date = []
    year = []
    month = []
    day = []

    if date_format_var == "yyyy":  # creates year variable based on yyyy format
        for i in range(0, len(data["Document"])):
            year.append(re.search(r"\d{4}", data[date_field][i])[0])
            data["year"] = year
    elif date_format_var == "mm-yyyy":  # creates year and month variable in yyyy-mm format
        for i in range(0, len(data["Document"])):
            date.append(re.search(r"\d.*\d", data[date_field][i])[0])
        for i in range(0, len(data["Document"])):
            year.append(re.search(r"\d{4}", date[i])[0])
        for i in range(0, len(data["Document"])):
            month.append(year[i] + "-" + date[i][0:2])
        data["year"] = year
        data["month"] = month
    elif date_format_var == "yyyy-mm":  # creates year and month variable in yyyy-mm format
        for i in range(0, len(data[date_field])):
            date.append(re.search(r"\d.*\d", data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search(r"\d{4}", date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + "-" + date[i][-2:])
        data["year"] = year
        data["month"] = month
    elif date_format_var == "dd-mm-yyyy":  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search(r"\d.*\d", data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search(r"\d{4}", date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + "-" + date[i][3:5])
        for i in range(0, len(data[date_field])):
            day.append(month[i] + "-" + date[i][0:2])
        data["day"] = day
        data["year"] = year
        data["month"] = month
    elif date_format_var == "mm-dd-yyyy":  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            try:
                date.append(re.search(r"\d.*\d", data[date_field][i])[0])
            except (TypeError, IndexError):
                continue
        for i in range(0, len(data[date_field])):
            try:
                year.append(re.search(r"\d{4}", date[i])[0])
            except (TypeError, IndexError):
                continue
        for i in range(0, len(data[date_field])):
            try:
                month.append(year[i] + "-" + date[i][0:2])
            except (TypeError, IndexError):
                continue
        for i in range(0, len(data[date_field])):
            try:
                day.append(month[i] + "-" + date[i][3:5])
            except (TypeError, IndexError):
                continue
        data["year"] = year
        data["month"] = month
        data["day"] = day
    elif date_format_var == "yyyy-mm-dd":  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search(r"\d.*\d", data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search(r"\d{4}", date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + "-" + date[i][5:7])
        data["year"] = year
        data["month"] = month
        data["day"] = date
    elif date_format_var == "yyyy-dd-mm":  # creates year,month and day variable in yyyy-mm-dd format
        for i in range(0, len(data[date_field])):
            date.append(re.search(r"\d.*\d", data[date_field][i])[0])
        for i in range(0, len(data[date_field])):
            year.append(re.search(r"\d{4}", date[i])[0])
        for i in range(0, len(data[date_field])):
            month.append(year[i] + "-" + date[i][-2:])
        for i in range(0, len(data[date_field])):
            day.append(month[i] + "-" + date[i][5:7])
        data["year"] = year
        data["month"] = month
        data["day"] = day

    # Plot corresponding graph depending on the options
    if not cumulative:
        if monthly and yearly:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"
        elif monthly:
            data = data.sort_values("month")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["month"])):
                tester = (
                    pd.DataFrame(data[data["month"] == i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
        elif yearly:
            data = data.sort_values("year")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["year"])):
                tester = (
                    pd.DataFrame(data[data["year"] == i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
        else:
            data = data.sort_values("day")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["day"])):
                tester = (
                    pd.DataFrame(data[data["day"] == i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
    else:
        if monthly and yearly:
            return "Choose one of the following: daily graph, monthly graph, yearly graph"
        elif yearly:
            data = data.sort_values("year")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["year"])):
                tester = (
                    pd.DataFrame(data[data["year"] <= i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
        elif monthly:
            data = data.sort_values("month")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["month"])):
                tester = (
                    pd.DataFrame(data[data["month"] <= i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
        else:
            data = data.sort_values("day")
            finalframe = pd.DataFrame()
            for i in sorted(set(data["day"])):
                tester = (
                    pd.DataFrame(data[data["day"] <= i][var].value_counts())
                    .reset_index()
                    .rename(columns={"index": var, var: "Frequency"})
                )
                for j in set(data[var]):
                    if j not in set(tester[var]):
                        temp = pd.DataFrame([j, 0]).T.rename(columns={0: var}).rename(columns={0: var, 1: "Frequency"})
                        tester = pd.concat([tester, temp])
                tester = tester.sort_values(var)
                date = np.repeat(i, len(tester))
                tester["date"] = date
                tester = tester.reset_index(drop=True)
                finalframe = pd.concat([finalframe, tester])
                value = []
                for i in list(set(finalframe[var])):
                    value.append(max(finalframe[finalframe[var] == i]["Frequency"]))
            fig = px.bar(
                finalframe,
                y=var,
                x="Frequency",
                animation_frame="date",
                orientation="h",
                range_x=[0, max(value)],
            ).update_yaxes(categoryorder="total ascending")
    fig = fig.update_geos(projection_type="equirectangular", visible=True, resolution=110)
    fig.write_html(outputFilename)

    return outputFilename
