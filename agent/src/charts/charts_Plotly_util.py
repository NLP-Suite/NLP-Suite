# Written by Tony Chen Gu in Feb 2022
# https://plotly.com/python/
import io
import logging
import math
import os

import IO_csv_util
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

## NOTE:
## some graphing functions has a column placed at the end
## these functions supports the feature of getting frequencies of the categorical variables
## the static_flag is used to indicate whether the chart is static or not


# def create_excel_chart(data_to_be_plotted,inputFilename,outputDir,scriptType,
#                        chart_title,
#                        chart_type_list,
#                        second_yAxis_label=''):
# match the excel chart format
def create_Plotly_chart(
    inputFilename,
    outputDir,
    chart_title,
    chart_type_list,
    cols_to_plot,
    column_xAxis_label="",
    column_yAxis_label="",
    remove_hyperlinks=True,
    static_flag=False,
    csv_field_Y_axis_list=None,
    X_axis_var=None,
    inputFileData="",
):
    # if we need to remove the hyperlinks, we need to make a temporary data for plotting
    if X_axis_var is None:
        X_axis_var = []
    if csv_field_Y_axis_list is None:
        csv_field_Y_axis_list = []
    # inputFileData may be a csv string (the agent endpoints) or an already-read DataFrame
    if isinstance(inputFileData, pd.DataFrame):
        data = inputFileData.copy()
        inputFilename = None  # No need to refer to a file when using inputFileData
    elif inputFileData:
        try:
            # Convert inputFileData to a DataFrame
            data = pd.read_csv(io.StringIO(inputFileData), encoding="utf-8", on_bad_lines="skip")
            inputFilename = None  # No need to refer to a file when using inputFileData
        except pd.errors.ParserError:
            logger.info("Error: failed to parse the provided inputFileData.")
            return
        except Exception as e:
            logger.info(f"Error: {e}")
            return
    else:
        # Process inputFilename as usual
        if remove_hyperlinks:
            remove_hyperlinks, inputFilename = IO_csv_util.remove_hyperlinks(inputFilename)
        try:
            data = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines="skip")
        except pd.errors.ParserError:
            try:
                data = pd.read_csv(
                    inputFilename,
                    encoding="utf-8",
                    on_bad_lines="skip",
                    sep="delimiter",
                )
            except Exception:
                logger.info("Error: failed to read the csv file: " + inputFilename)
                return
        except Exception as e:
            logger.info(f"Error: {e}")
            return
    # print on X-axis the filename w/o path
    headers = data.columns.tolist()
    file_list = []
    for j in range(0, len(chart_type_list)):
        i = chart_type_list[j]
        x_cols = []
        y_cols = ""
        fig = None

        # remove the path from the filename
        def do(x):
            return os.path.split(x)[1].replace('")', "")

        try:
            data["Document"] = data["Document"].apply(do)
        except Exception:
            pass
        if not csv_field_Y_axis_list:
            x_cols = headers[cols_to_plot[j][0]]
            y_cols = headers[cols_to_plot[j][1]]
        else:
            y_cols = csv_field_Y_axis_list
            x_cols = X_axis_var
            html_template = """
                                <html>
                                <head>
                                <style>
                                    .container {{
                                        display: flex;
                                        flex-wrap: wrap;
                                        align-items: center;
                                        justify-content: center;
                                    }}
                                    .chart {{
                                        margin: 10px;
                                    }}
                                </style>
                                </head>
                                <body>
                                <div class="container">
                                    {charts}
                                </div>
                                </body>
                                </html>
                                """

            def process_multiple(x_cols, y_cols, lst, df2_fn, fig_fn, types, data, _html_template=html_template):
                chart_htmls = []
                for chart_name in lst:
                    df2 = df2_fn(chart_name) if df2_fn else None
                    fig = fig_fn(df2, chart_name)
                    chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
                    chart_htmls.append(f'<div class="chart">{chart_html}</div>')
                final_html = _html_template.format(charts="".join(chart_htmls))
                with open(outputDir + os.sep + types + "chart of the " + x_cols + ".html", "w") as file:
                    file.write(final_html)

            if i.lower() == "bar":
                process_multiple(
                    x_cols,
                    y_cols,
                    y_cols,
                    None,
                    lambda df2, chart_name, x_cols=x_cols: px.bar(data, x=x_cols, color=chart_name),
                    "bar",
                    data,
                )
                file_list.append(outputDir + os.sep + "bar" + "chart of the " + x_cols + ".html")
                # file_list.append(
                #    save_chart(fig, outputDir, 'Frequency Distribution of '+x_cols, static_flag, x_cols))
            elif i.lower() == "pie":
                if not x_cols:
                    df2 = data[y_cols].value_counts()
                    fig = px.pie(df2, values=df2.values, names=list(df2.index))
                    file_list.append(
                        save_chart(
                            fig,
                            outputDir,
                            "Pie chart of " + y_cols[0] + "no x grouping",
                            static_flag,
                            x_cols,
                        )
                    )
                else:
                    lst = list(data[x_cols].value_counts().keys())
                    process_multiple(
                        x_cols,
                        y_cols,
                        lst,
                        lambda chart_name, x_cols=x_cols, y_cols=y_cols: data[data[x_cols] == chart_name][
                            y_cols[0]
                        ].value_counts(),
                        lambda df2, chart_name: px.pie(df2, values=df2.values, names=df2.index, title=chart_name),
                        "Pie",
                        data,
                    )
                    file_list.append(outputDir + os.sep + "pie" + "chart of the " + x_cols + ".html")
            elif i.lower() == "scatter":
                process_multiple(
                    x_cols,
                    y_cols,
                    y_cols,
                    None,
                    lambda df2, chart_name, x_cols=x_cols: px.scatter(data, x=x_cols, color=chart_name),
                    "scatter",
                    data,
                )
                file_list.append(outputDir + os.sep + "scatter" + "chart of the " + x_cols + ".html")
            elif i.lower() == "radar":
                process_multiple(
                    x_cols,
                    y_cols,
                    y_cols,
                    None,
                    lambda df2, chart_name, x_cols=x_cols: px.line_polar(data, r=x_cols, theta=chart_name),
                    "Radar",
                    data,
                )
                file_list.append(outputDir + os.sep + "radar" + "chart of the " + x_cols + ".html")
            elif i.lower() == "line":
                process_multiple(
                    x_cols,
                    y_cols,
                    y_cols,
                    None,
                    lambda df2, chart_name, x_cols=x_cols: px.line(data, x=x_cols, color=chart_name),
                    "line",
                    data,
                )
                file_list.append(outputDir + os.sep + "line" + "chart of the " + x_cols + ".html")
                # file_list.append(
                #    save_chart(fig, outputDir, 'Frequency Distribution of ' + x_cols, static_flag, x_cols))
            elif i.lower() == "bubble":
                fig = px.scatter(data, x=x_cols, y=y_cols[0], size=y_cols[1], color=y_cols[2])
                file_list.append(save_chart(fig, outputDir, "Bubble Chart of " + x_cols, static_flag, x_cols))

            else:
                logger.info("Bad for now!")

            if len(file_list) == 1:
                return file_list[0]
            return file_list

        if i.lower() == "bar":
            if len(chart_type_list) < len(cols_to_plot):
                fig = plot_multi_bar_chart_px(data, chart_title, cols_to_plot)
                file_list.append(
                    save_chart(
                        fig,
                        outputDir,
                        chart_title,
                        static_flag,
                        column_xAxis_label,
                        column_yAxis_label,
                    )
                )
                break
            else:
                fig = plot_bar_chart_px(x_cols, inputFilename, chart_title, y_cols)
        elif i.lower() == "pie":
            fig = plot_pie_chart_px(x_cols, inputFilename, chart_title, y_cols)
        elif i.lower() == "scatter":
            fig = plot_scatter_chart_px(x_cols, y_cols, inputFilename, chart_title)
        elif i.lower() == "radar":
            fig = plot_radar_chart_px(x_cols, y_cols, inputFilename, chart_title)
        elif i.lower() == "line":
            fig = plot_multi_line_chart_w_slider_px(inputFilename, chart_title, cols_to_plot)
            file_list.append(
                save_chart(
                    fig,
                    outputDir,
                    chart_title,
                    static_flag,
                    column_xAxis_label,
                    column_yAxis_label,
                )
            )
            break
        else:
            logger.info(i + " chart currently not supported in the NLP Suite. Check back soon!")
            continue
        file_list.append(
            save_chart(
                fig,
                outputDir,
                chart_title,
                static_flag,
                column_xAxis_label,
                column_yAxis_label,
            )
        )
    # remove the temporary file
    if remove_hyperlinks:
        os.remove(inputFilename)
    # if the length of thr file list is 1, only return the string to avoid IO_files error
    if len(file_list) == 1:
        return file_list[0]
    return file_list


# need to discuss further
def get_chart_title(xVar="", yVar="", base_title="", chart_type=""):
    return base_title + " of " + xVar + " and " + yVar


# get frequencies of categorical variables
def get_frequencies(data, variable):
    # this line give a column of the counts for the categorical vairable
    # the name of row is the categorical variable
    data_count = data[variable].value_counts()
    # extract the row name = categorical variables
    data_head = data_count.index
    header = variable + "_count"
    # rebuild the dataframe with a column of categorical vairables and a column of their counts
    # the row name is still the categorical variable
    return pd.DataFrame({variable: data_head, header: data_count})


# helper function for saving the chart
# set up the output directory path
# support both static and dynamic chart
def save_chart(fig, outputDir, chart_title, static_flag, x_label="", y_label=""):
    if x_label != "":
        fig.update_layout(xaxis_title=x_label)
    if y_label != "":
        fig.update_layout(yaxis_title=y_label)
    if static_flag:
        savepath = os.path.join(outputDir, chart_title + ".png")
        fig.write_image(savepath)
    else:
        # if the chat title has double lines, keep only the last line
        if "\n" in chart_title:
            chart_title = chart_title.split("\n")[1]
        savepath = os.path.join(outputDir, chart_title + ".html")
        fig.write_html(savepath)
    return savepath


# plot bar chart with Plotly
# fileName is a csv file with data to be plotted
# x_label indicates the column name of x axis from the data
# height indicates the column name of y axis from the data
# the output file would be a html file with hover over effect names by the chart title
# duplicates allowed, would add up the counts
# Users are expected to provide the x label and their hights.
# If not call the get_frequencies function to get the frequencies of the categorical variables in x_label column
def plot_bar_chart_px(x_label, fileName, chart_title, height=""):
    data = pd.read_csv(fileName, encoding="utf-8", on_bad_lines="skip")
    if height == "":
        height = x_label + "_count"
        data = get_frequencies(data, x_label)
    fig = px.bar(data, x=x_label, y=height)
    # to ensure the bar doesn't look to wide if x label's length is not enough
    if len(data[x_label]) < 5:
        fig.update_traces(width=0.2)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig


# plot pie chart with Plotly
# fileName is a csv file with data to be plotted
# x_label indicates the column name of x axis from the data
# height indicates the column name of y axis from the data
# the output file would be a html file with hover over effect names by the chart title
# duplicates allowed, would add up the counts
def plot_pie_chart_px(x_label, fileName, chart_title, height=""):
    data = pd.read_csv(fileName, encoding="utf-8", on_bad_lines="skip")
    if height == "":
        height = x_label + "_count"
        data = get_frequencies(data, x_label)
    fig = px.pie(data, values=height, names=x_label)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig


# plot scatter chart with Plotly
# fileName is a csv file with data to be plotted
# x_label indicates the column name of x axis from the data    COULD BE A DISCRETE VARIABLE
# y_label indicates the column name of y axis from the data    COULD BE A DISCRETE VARIABLE
# the output file would be a html file with hover over effect names by the chart title
def plot_scatter_chart_px(x_label, y_label, fileName, chart_title):
    data = pd.read_csv(fileName, encoding="utf-8", on_bad_lines="skip")
    fig = px.scatter(data, x=x_label, y=y_label)
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig


# plot scatter chart with Plotly
# fileName is a csv file with data to be plotted
# theta_label indicates the column name of the "feature" from the data    SHOULD BE A DISCRETE VARIABLE
# r_label indicates the column name of the value of the feature from the data    CANNOT BE A DISCRETE VARIABLE
# the output file would be a html file with hover over effect names by the chart title
# null value will cause an unclosed shape. This function default removes all rows contaning null values
def plot_radar_chart_px(theta_label, r_label, fileName, chart_title):
    data = pd.read_csv(fileName, encoding="utf-8", on_bad_lines="skip")
    if r_label is None:
        r_label = theta_label + "_count"
        data = get_frequencies(data, theta_label)
    data = data.dropna(subset=[theta_label, r_label])
    fig = px.line_polar(data, r=r_label, theta=theta_label, line_close=True)
    fig.update_traces(fill="toself")
    fig.update_layout(title=chart_title, title_x=0.5)
    return fig


# plot multi bar chart (data should be already preprocessed)
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


# plot multi line chart
def plot_multi_line_chart_w_slider_px(fileName, chart_title, col_to_be_ploted, series_label_list=None):
    data = pd.read_csv(fileName, encoding="utf-8", on_bad_lines="skip")
    data.fillna(0, inplace=True)
    figs = make_subplots()
    col_name = list(data.head())
    default_series_name = series_label_list is None
    # overlay subplots
    for i in range(0, len(col_to_be_ploted)):
        if default_series_name:
            series_label = col_name[col_to_be_ploted[i][1]]
        else:
            series_label = series_label_list[i]
        trace = go.Scatter(
            x=data[col_name[col_to_be_ploted[i][0]]],
            y=data[col_name[col_to_be_ploted[i][1]]],
            name=series_label,
        )
        figs.add_trace(trace)
    figs.update_layout(title=chart_title, title_x=0.5)
    # allow for sliders
    figs.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
        )
    )
    return figs


# Bubble Chart Graph
# Created by Aiden Amaya and ChatGPT 3.5
# The chart will plot yAxis vs the xAxis, but categorize them using the category field.
# Filename is the csv file it will read, xAxis, yAxis, and category are all csv file column fields.


def plot_graph_bubble_chart(fileName, xAxis, yAxis, category):
    # Load csv
    df = pd.read_csv(fileName)

    # Determine x-axis and y-axis columns based on user inputs, as well as the category you want bubbles to be separated by.
    x_axis = df.columns[xAxis]
    y_axis = df.columns[yAxis]
    cat = df.columns[category]

    # Define hover text based off of the column entries.
    hover_text = []
    for _index, row in df.iterrows():
        text = ""
        for col in df.columns:
            text += f"{col}: {row[col]}<br>"
        hover_text.append(text)

    df["text"] = hover_text

    # If there is a number column, determine bubble size based on it.
    numeric_columns = df.select_dtypes(include=["number"]).columns
    if not numeric_columns.empty:
        bubble_size = [math.sqrt(row[numeric_columns[0]]) for _, row in df.iterrows()]
        df["size"] = bubble_size
        sizeref = 2.0 * max(df["size"]) / (100**2)
    else:
        sizeref = None

    # Define color mapping for categories
    category_colors = {
        category_value: f"rgb({i * 50 % 256}, {i * 30 % 256}, {i * 70 % 256})"
        for i, category_value in enumerate(df[cat].unique())
    }

    fig = go.Figure()

    # Create scatterplot.
    for _i, (_, row) in enumerate(df.iterrows()):
        color = category_colors[row[cat]] if cat in df.columns else None
        fig.add_trace(
            go.Scatter(
                x=[row[x_axis]],
                y=[row[y_axis]],
                text=row["text"],
                marker=dict(
                    size=row["size"] if "size" in df.columns else None,
                    color=color,
                ),
                name=row[cat] if cat in df.columns else None,
            )
        )

    # Tune marker appearance and layout
    fig.update_traces(mode="markers", marker=dict(sizemode="area", sizeref=sizeref, line_width=2))

    # Adjust bubble positions based on the values of the x and y axes
    if sizeref:
        fig.update_layout(autosize=False, width=800, height=600)
        fig.update_xaxes(scaleanchor="y", scaleratio=1)
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

    fig.update_layout(
        title=f"{x_axis} vs {y_axis}",
        xaxis=dict(
            title=f"{x_axis}",
            gridcolor="white",
            gridwidth=2,
        ),
        yaxis=dict(
            title=f"{y_axis}",
            gridcolor="white",
            gridwidth=2,
        ),
        paper_bgcolor="rgb(243, 243, 243)",
        plot_bgcolor="rgb(243, 243, 243)",
    )

    # Visible toggle buttons based on category.
    if cat in df.columns:
        buttons = []
        categories = df[cat].unique()
        for category in categories:
            buttons.append(
                dict(
                    label=str(category),
                    method="update",
                    args=[
                        {"visible": [True if x == category else False for x in df[cat]]},
                        {"title": f"{x_axis} vs {y_axis} - {category}"},
                    ],
                )
            )
        fig.update_layout(
            updatemenus=[
                {
                    "buttons": buttons,
                    "direction": "down",
                    "showactive": True,
                    "x": 1.1,
                    "xanchor": "left",
                    "y": 1.05,
                    "yanchor": "top",
                }
            ]
        )

    # Add a reset toggle button option.
    buttons.append(
        dict(
            label="Reset Zoom",
            method="update",
            args=[{"visible": [True] * len(df)}, {"title": f"{x_axis} vs {y_axis}"}],
        )
    )
    fig.update_layout(
        updatemenus=[
            {
                "buttons": buttons,
                "showactive": True,
                "x": 1.1,
                "xanchor": "left",
                "y": 1.05,
                "yanchor": "top",
            }
        ]
    )
    return fig


def bubble_chart(inputFilename, outputFilename, x, y, color, show_labels=True, inputFileData=""):
    import random
    from collections import Counter

    import mpld3
    import numpy as np
    from mpld3 import plugins

    logger.info(f"\nCHART PARAMETERS: {x} (X-axis) vs. {y} (Y-axis)")
    if inputFileData:
        df = pd.read_csv(io.StringIO(inputFileData))
    else:
        df = pd.read_csv(inputFilename)

    df = df[(df[x] != "None") & (df[y] != "None")]

    df[x] = df[x].astype(str)
    df[y] = df[y].astype(str)

    xy_pairs = list(zip(df[x], df[y]))
    pair_counts = Counter(xy_pairs)

    unique_pairs = list(pair_counts.keys())
    frequencies = list(pair_counts.values())

    n_bubbles = len(frequencies)
    max_size = 5000 / np.sqrt(n_bubbles)
    min_size = max_size / 10

    sizes = np.array(frequencies)
    sizes = (sizes - sizes.min()) / (sizes.max() - sizes.min()) * 50 * (max_size - min_size) + min_size

    unique_x = sorted(set(df[x]))
    unique_y = sorted(set(df[y]))
    x_pos = [unique_x.index(pair[0]) for pair in unique_pairs]
    y_pos = [unique_y.index(pair[1]) for pair in unique_pairs]

    labels = [f"{pair[0]}, {pair[1]}\nFreq: {freq}" for pair, freq in zip(unique_pairs, frequencies)]

    unique_frequencies = sorted(set(frequencies))
    frequency_colors = {freq: f"#{random.randint(0, 0xFFFFFF):06x}" for freq in unique_frequencies}
    colors = [frequency_colors[freq] for freq in frequencies]

    class BubbleChart:
        def __init__(self, area, x_pos, y_pos, colors):
            bubble_spacing = 0.1
            area = np.asarray(area)
            r = np.sqrt(area / np.pi)

            self.bubble_spacing = bubble_spacing
            self.bubbles = np.ones((len(area), 4))
            self.bubbles[:, 2] = r
            self.bubbles[:, 3] = area
            self.maxstep = 2 * self.bubbles[:, 2].max() + self.bubble_spacing
            self.step_dist = self.maxstep / 2
            self.colors = colors

            length = np.ceil(np.sqrt(len(self.bubbles)))
            grid = np.arange(length) * self.maxstep
            gx, gy = np.meshgrid(grid, grid)
            self.bubbles[:, 0] = gx.flatten()[: len(self.bubbles)]
            self.bubbles[:, 1] = gy.flatten()[: len(self.bubbles)]

            self.com = self.center_of_mass()

        def center_of_mass(self):
            return np.average(self.bubbles[:, :2], axis=0, weights=self.bubbles[:, 3])

        def center_distance(self, bubble, bubbles):
            return np.hypot(bubble[0] - bubbles[:, 0], bubble[1] - bubbles[:, 1])

        def outline_distance(self, bubble, bubbles):
            center_distance = self.center_distance(bubble, bubbles)
            return center_distance - bubble[2] - bubbles[:, 2] - self.bubble_spacing

        def check_collisions(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return len(distance[distance < 0])

        def collides_with(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return np.argmin(distance, keepdims=True)

        def collapse(self, n_iterations=50):
            """
            Move bubbles to the center of mass.

            Parameters
            ----------
            n_iterations : int, default: 50
                Number of moves to perform.
            """
            for _i in range(n_iterations):
                moves = 0
                for i in range(len(self.bubbles)):
                    rest_bub = np.delete(self.bubbles, i, 0)

                    dir_vec = self.com - self.bubbles[i, :2]
                    dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))
                    new_point = self.bubbles[i, :2] + dir_vec * self.step_dist
                    new_bubble = np.append(new_point, self.bubbles[i, 2:4])

                    if not self.check_collisions(new_bubble, rest_bub):
                        self.bubbles[i, :] = new_bubble
                        self.com = self.center_of_mass()
                        moves += 1
                    else:
                        for colliding in self.collides_with(new_bubble, rest_bub):
                            dir_vec = rest_bub[colliding, :2] - self.bubbles[i, :2]
                            dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))
                            orth = np.array([dir_vec[1], -dir_vec[0]])
                            new_point1 = self.bubbles[i, :2] + orth * self.step_dist
                            new_point2 = self.bubbles[i, :2] - orth * self.step_dist
                            dist1 = self.center_distance(self.com, np.array([new_point1]))
                            dist2 = self.center_distance(self.com, np.array([new_point2]))
                            new_point = new_point1 if dist1 < dist2 else new_point2
                            new_bubble = np.append(new_point, self.bubbles[i, 2:4])
                            if not self.check_collisions(new_bubble, rest_bub):
                                self.bubbles[i, :] = new_bubble
                                self.com = self.center_of_mass()

                if moves / len(self.bubbles) < 0.1:
                    self.step_dist = self.step_dist / 2

        def plot(self, ax, labels):
            """
            Draw the bubble plot with specified colors and scale text to bubble size.

            Parameters
            ----------
            ax : matplotlib.axes.Axes
            labels : list
                Labels of the bubbles.
            """
            self.circles = []
            self.texts = []
            for i in range(len(self.bubbles)):
                circ = plt.Circle(self.bubbles[i, :2], self.bubbles[i, 2], color=self.colors[i])
                self.circles.append(circ)
                ax.add_patch(circ)

                bubble_size = self.bubbles[i, 2] * 2
                text_size = bubble_size / 10

                if show_labels:
                    text = ax.text(
                        *self.bubbles[i, :2],
                        labels[i],
                        horizontalalignment="center",
                        verticalalignment="center",
                        fontsize=text_size,
                        color="black",
                    )
                    self.texts.append(text)

    bubble_chart = BubbleChart(area=sizes, x_pos=x_pos, y_pos=y_pos, colors=colors)
    bubble_chart.collapse()

    fig, ax = plt.subplots(figsize=(10, 8))
    bubble_chart.plot(ax, labels)
    ax.axis("off")
    ax.relim()
    ax.autoscale_view()
    ax.set_title("Bubble Chart for " + x + " (X-axis) and " + y + " (Y-axis)")

    scatter = ax.scatter(
        [bubble[0] for bubble in bubble_chart.bubbles],
        [bubble[1] for bubble in bubble_chart.bubbles],
        s=[bubble[3] for bubble in bubble_chart.bubbles],
        color=bubble_chart.colors,
        alpha=0,
    )

    tooltip = plugins.PointLabelTooltip(scatter, labels=labels)
    plugins.connect(fig, tooltip)

    plt.tight_layout(pad=0.1, w_pad=0.1, h_pad=0.1)
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

    mpld3.save_html(fig, outputFilename + ".html")
    return outputFilename + ".html"
