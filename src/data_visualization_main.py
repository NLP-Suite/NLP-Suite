# Combined visualization GUI with tabbed interface
# Merges data_visualization_1_main.py (relational, categorical, temporal)
# and data_visualization_2_main.py (numeric/statistical)

import sys

import GUI_util
import IO_libraries_util

if (
    IO_libraries_util.install_all_Python_packages(
        GUI_util.window, "data_visualization_main.py", ["os", "tkinter"]
    )
    == False
):
    sys.exit(0)

import os
import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as mb

import customtkinter as ctk

import charts_util
import GUI_IO_util
import GUI_theme_util
import IO_csv_util
import IO_files_util
import run_script_util

# The section-header labels below ("Gephi/vis.js", "Sankey", "Boxplot", ...) used a hardcoded
# font=("Courier", ...), a leftover typewriter-style font that reads as visibly out of step with
# every other reformatted CTk label on this GUI. Resolve the platform's actual default UI font
# (mirrors NLP_menu_main.py's _ui_font_family) so these headers match the rest of the suite instead.
_ui_font_family = tkfont.nametofont("TkDefaultFont").actual("family")

# ── Run functions ──────────────────────────────────────────────────────────────


def runGephi(
    inputFilename, outputDir, csv_file_relational_field_list, dynamic_network_field_var
):
    import Gephi_util

    fileBase = os.path.basename(inputFilename)[0:-4]
    return Gephi_util.create_gexf(
        GUI_util.window,
        fileBase,
        outputDir,
        inputFilename,
        csv_file_relational_field_list[0],
        csv_file_relational_field_list[1],
        csv_file_relational_field_list[2],
        dynamic_network_field_var,
        "abnormal",
    )


def run_relational(
    inputFilename,
    outputDir,
    openOutputFiles,
    relations_menu_var,
    csv_field_relational_var,
    csv_file_relational_field_list,
    dynamic_network_field_var,
    Sankey_limit1_var,
    Sankey_limit2_var,
    Sankey_limit3_var,
):
    filesToOpen = []
    if inputFilename == "" or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning(
            "Warning",
            "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.",
        )
        return
    if relations_menu_var == "":
        mb.showwarning(
            "Warning",
            "Please, use the dropdown menu to select one of the options for visualizing relations: Gephi, Network graph (vis.js), Sankey and try again.",
        )
        return

    outputFilename = ""

    # Gephi
    if relations_menu_var == "*" or relations_menu_var == "Gephi":
        if len(csv_file_relational_field_list) != 3:
            if relations_menu_var == "Gephi":
                mb.showwarning(
                    "Warning",
                    "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic network graph you can select a fourth field to be used as the dynamic index (e.g., Sentence ID or Date).",
                )
                return
        else:
            try:
                outputFiles = runGephi(
                    inputFilename,
                    outputDir,
                    csv_file_relational_field_list,
                    dynamic_network_field_var,
                )
                if outputFiles != None:
                    if isinstance(outputFiles, str):
                        filesToOpen.append(outputFiles)
                    else:
                        filesToOpen.extend(outputFiles)
            except Exception as e:
                if relations_menu_var == "*":
                    print(f"  Gephi skipped (not installed or error): {e}")
                else:
                    mb.showwarning("Warning", f"Gephi error: {e}")
                    return

    # Network graph (vis.js)
    if relations_menu_var == "*" or relations_menu_var == "Network graph (vis.js)":
        if len(csv_file_relational_field_list) != 3:
            if relations_menu_var == "Network graph (vis.js)":
                mb.showwarning(
                    "Warning",
                    "You must select three csv fields to be used in the computation of the network graph, in the order of node, edge, node (e.g., Subject, Verb, Object).\n\nIf you wish to create a dynamic temporal network you can select a fourth field to be used as the dynamic index (e.g., Date).",
                )
                return
        else:
            date_field = (
                dynamic_network_field_var if dynamic_network_field_var else None
            )
            outputFiles = charts_util.network_graph_visjs(
                inputFilename,
                outputDir,
                csv_file_relational_field_list[0],
                csv_file_relational_field_list[1],
                csv_file_relational_field_list[2],
                date_col=date_field,
            )
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    # Sankey
    if relations_menu_var == "*" or relations_menu_var == "Sankey":
        if (
            len(csv_file_relational_field_list) != 2
            and len(csv_file_relational_field_list) != 3
        ):
            if relations_menu_var == "Sankey":
                mb.showwarning(
                    "Warning",
                    "You must select 2 or 3 csv fields to be used in the computation of a Sankey chart (e.g., Subject, Verb, Object or Subject, Object).\n\nMAKE SURE TO CLICK ON THE + BUTTON AFTER THE LAST SELECTION. CLICK ON THE SHOW BUTTON TO SEE THE CURRENT SELECTION.",
                )
                return
        else:
            if len(csv_file_relational_field_list) == 3:
                three_way_Sankey = True
                var3 = csv_file_relational_field_list[2]
            else:
                three_way_Sankey = False
                var3 = None
                Sankey_limit3_var = None
            outputFiles = charts_util.Sankey(
                inputFilename,
                outputFilename,
                csv_file_relational_field_list[0],
                Sankey_limit1_var,
                csv_file_relational_field_list[1],
                Sankey_limit2_var,
                three_way_Sankey,
                var3,
                Sankey_limit3_var,
            )
            if outputFiles != None:
                if isinstance(outputFiles, str):
                    filesToOpen.append(outputFiles)
                else:
                    filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(
            GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName
        )


def run_categorical(
    inputFilename,
    outputDir,
    openOutputFiles,
    categorical_menu_var,
    csv_field_categorical_var,
    case_sensitive_var,
    csv_file_categorical_field_list,
    filter_options_var,
    fixed_param_var,
    rate_param_var,
    base_param_var,
    max_rows_var,
    color_1_style_var,
    color_2_style_var,
    data_transformation_var,
    csv_files_list,
    csv_field_visualization_var,
):
    filesToOpen = []
    if inputFilename == "" or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning(
            "Warning",
            "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.",
        )
        return

    if categorical_menu_var == "":
        mb.showwarning(
            "Warning",
            "Please, use the dropdown menu to select one of the options for categorical data and try again.",
        )
        return

    # Comparative bar charts have their own validation
    if "Comparative" in categorical_menu_var:
        if len(csv_files_list) < 2:
            mb.showwarning(
                "Warning",
                "The 'Comparative bar charts' option requires at least two csv files in input.\n\nPlease, select at least 2 csv files and try again.",
            )
            return
        if csv_field_visualization_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.",
            )
            return
        outputFiles = charts_util.comparative_bar_charts(
            csv_files_list, outputDir, csv_field_visualization_var
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)
        if openOutputFiles and len(filesToOpen) > 0:
            IO_files_util.OpenOutputFiles(
                GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName
            )
        return

    if len(csv_file_categorical_field_list) < 2:
        mb.showwarning(
            "Warning",
            "You must have at least 2 sets of csv file search field and search values to produce meaningful "
            + categorical_menu_var
            + " charts.\n\nPlease, select another combination of csv file field and search values and try again.",
        )
        return
    if csv_field_categorical_var == "":
        mb.showwarning(
            "Warning",
            "The categorical data visualization functions require a set of comma-separated entries to be used in the search (could be parts of a filenames, if the Document field is selected).\n\nPlease, enter value(s) and try again.",
        )
        return

    label = csv_field_categorical_var
    outputFilename = ""

    # Colormap
    if "*" in categorical_menu_var or "Colormap" in categorical_menu_var:
        all_fields = []
        intermediate_fields = []
        for i in range(len(csv_file_categorical_field_list)):
            if i > 0 and i < len(csv_file_categorical_field_list) - 1:
                intermediate_fields.append(
                    csv_file_categorical_field_list[i][0].split("|")[0]
                )
            all_fields.append(csv_file_categorical_field_list[i][0].split("|")[0])
        all_fields_str = ", ".join(all_fields)
        intermediate_fields_str = ", ".join(intermediate_fields)
        mb.showwarning(
            title="Search values",
            message="You have entered "
            + str(len(csv_file_categorical_field_list))
            + ' different search fields: "'
            + all_fields_str
            + '".'
            + '\n\nThe first selected field "'
            + csv_file_categorical_field_list[0][0].split("|")[0]
            + '" will be used as the GroupBy field.'
            + '\n\nThe last field "'
            + csv_file_categorical_field_list[len(csv_file_categorical_field_list) - 1][
                0
            ].split("|")[0]
            + '" will be used as the field whose values will be displayed.'
            + '\n\nAll other intermediate fields "'
            + intermediate_fields_str
            + '" will be used as the conditional WHERE CLAUSE.',
        )
        params = [
            max_rows_var,
            color_1_style_var,
            color_2_style_var,
            data_transformation_var,
        ]
        outputFiles = charts_util.colormap(
            inputFilename, outputDir, csv_file_categorical_field_list, params
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if filter_options_var == "No filtering":
        fixed_param_var_val = None
        rate_param_var_val = None
        base_param_var_val = None
    elif filter_options_var == "Fixed parameter":
        fixed_param_var_val = fixed_param_var
        rate_param_var_val = None
        base_param_var_val = None
    else:
        fixed_param_var_val = None
        rate_param_var_val = rate_param_var
        base_param_var_val = base_param_var

    # Sunburst
    if "*" in categorical_menu_var:
        chart_type = 3
    if "*" in categorical_menu_var or "Sunburst" in categorical_menu_var:
        chart_type = 1
        outputFiles = charts_util.Sunburst_Treemap(
            inputFilename,
            outputFilename,
            outputDir,
            csv_file_categorical_field_list,
            chart_type,
            fixed_param_var_val,
            rate_param_var_val,
            base_param_var_val,
            filter_options_var,
            case_sensitive_var,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    # Stacked bar / Grouped bar
    if (
        "*" in categorical_menu_var
        or "Stacked bar" in categorical_menu_var
        or "Grouped bar" in categorical_menu_var
    ):
        if len(csv_file_categorical_field_list) < 2:
            mb.showwarning(
                "Warning",
                "The bar chart requires at least 2 csv file fields: one for the groups (rows) and one for the segments (colors).\n\nPlease, select at least 2 fields and try again.",
            )
        else:
            group_field = csv_file_categorical_field_list[0][0].split("|")[0]
            segment_field = csv_file_categorical_field_list[1][0].split("|")[0]
            is_grouped = "Grouped" in categorical_menu_var
            outputFile = charts_util.stacked_bar_from_csv(
                inputFilename, outputDir, group_field, segment_field, grouped=is_grouped
            )
            if outputFile:
                filesToOpen.append(outputFile)
            if "*" in categorical_menu_var:
                outputFile2 = charts_util.stacked_bar_from_csv(
                    inputFilename,
                    outputDir,
                    group_field,
                    segment_field,
                    grouped=not is_grouped,
                )
                if outputFile2:
                    filesToOpen.append(outputFile2)

    # Waffle chart
    if "*" in categorical_menu_var or "Waffle" in categorical_menu_var:
        if len(csv_file_categorical_field_list) < 1:
            mb.showwarning(
                "Warning",
                "The waffle chart requires at least 1 csv file field.\n\nPlease, select a categorical field and try again.",
            )
        else:
            category_field = csv_file_categorical_field_list[0][0].split("|")[0]
            outputFile = charts_util.waffle_chart(
                inputFilename, outputDir, category_field
            )
            if outputFile:
                filesToOpen.append(outputFile)

    # Treemap
    if "Treemap" in categorical_menu_var:
        chart_type = 0
        outputFiles = charts_util.Sunburst_Treemap(
            inputFilename,
            outputFilename,
            outputDir,
            csv_file_categorical_field_list,
            chart_type,
            fixed_param_var_val,
            rate_param_var_val,
            base_param_var_val,
            filter_options_var,
            case_sensitive_var,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(
            GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName
        )


def run_temporal(
    inputFilename,
    outputDir,
    openOutputFiles,
    temporal_menu_var,
    csv_field_relational_var,
    time_mapper_field_var,
    date_format_var,
    time_var,
    cumulative_var,
    timeline_Y_axis_var,
    timeline_date_var,
    calendar_date_var,
    calendar_value_var,
):
    filesToOpen = []
    if inputFilename == "" or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning(
            "Warning",
            "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.",
        )
        return

    if "Time mapper" in temporal_menu_var:
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, "", outputDir, ".html", "timeMapper"
        )
        monthly = False
        yearly = False
        if time_var == "Monthly":
            monthly = True
        elif time_var == "Yearly":
            yearly = True

        date_col = time_mapper_field_var if time_mapper_field_var else None
        outputFiles = charts_util.TimeMapper(
            inputFilename,
            outputFilename,
            csv_field_relational_var,
            date_format_var,
            cumulative_var,
            monthly,
            yearly,
            date_col=date_col,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif "Calendar" in temporal_menu_var:
        if calendar_date_var == "":
            mb.showwarning(
                "Warning",
                "No date field has been selected.\n\nPlease, select a date field and try again.",
            )
            return
        value_col = calendar_value_var if calendar_value_var else None
        outputFile = charts_util.heatmap_calendar(
            inputFilename,
            outputDir,
            calendar_date_var,
            value_col=value_col,
            date_format=date_format_var,
        )
        if outputFile:
            filesToOpen.append(outputFile)

    elif "Timeline" in temporal_menu_var:
        if timeline_Y_axis_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.",
            )
            return
        if timeline_date_var == "":
            mb.showwarning(
                "Warning",
                "No date field has been selected for the X-axis.\n\nPlease, select a date field and try again.",
            )
            return

        headers = IO_csv_util.get_csvfile_headers(inputFilename)
        col_num = IO_csv_util.get_columnNumber_from_headerValue(
            headers, timeline_Y_axis_var, inputFilename
        )
        columns_to_be_plotted_yAxis = [[col_num, col_num]]

        outputFiles = charts_util.run_all(
            columns_to_be_plotted_yAxis,
            inputFilename,
            outputDir,
            outputFileLabel="",
            chartPackage=GUI_util.charts_package_options_widget.get(),
            dataTransformation=GUI_util.data_transformation_options_widget.get(),
            chart_type_list=["Line"],
            chart_title=timeline_Y_axis_var + " over Time",
            column_xAxis_label_var=timeline_date_var,
            hover_info_column_list=[],
            count_var=1,
            complete_sid=False,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(
            GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName
        )


def run_numeric(
    inputFilename,
    outputDir,
    openOutputFiles,
    visualizations_menu_var,
    csv_field_visualization_var,
    X_axis_var,
    csv_file_field_Y_axis_list,
    points_var,
    split_data_byCategory_var,
    csv_field_boxplot_var,
    csv_field_boxplot_color_var,
    X_axis_bubble_var,
    color_1_style_var,
    histogram_nbins_var,
    histogram_category_var,
    histogram_marginal_var,
    violin_points_var,
    violin_category_var,
):
    filesToOpen = []
    if inputFilename == "" or os.path.basename(inputFilename)[-4:] != ".csv":
        mb.showwarning(
            "Warning",
            "The visualization options require a csv file in input.\n\nPlease, select a csv file and try again.",
        )
        return

    config_filename = GUI_util.config_filename_selected_config.get()

    if "Boxplot" in visualizations_menu_var:
        if csv_field_visualization_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.",
            )
            return
        outputFiles = charts_util.boxplot(
            inputFilename,
            outputDir,
            csv_field_visualization_var,
            complete_sid=False,
            csv_field_Y_axis_list=csv_file_field_Y_axis_list,
            X_axis_var=X_axis_var,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif "Bubble" in visualizations_menu_var:
        if csv_field_visualization_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a Y-axis variable and try again.",
            )
            return
        outputFiles = charts_util.bubble_chart(
            inputFilename,
            outputDir,
            csv_field_visualization_var,
            X_axis_var=X_axis_bubble_var,
            color_column=color_1_style_var,
        )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif "Excel" in visualizations_menu_var or "Plotly" in visualizations_menu_var:
        if X_axis_var == "" and len(csv_file_field_Y_axis_list) < 1:
            mb.showwarning(
                "Warning",
                "No X-axis or Y-axis variable has been selected.\n\nPlease, select a variable and try again.",
            )
            return
        if len(csv_file_field_Y_axis_list) < 1:
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select at least one Y-axis variable and try again.",
            )
            return
        if len(csv_file_field_Y_axis_list) < 3:
            outputFiles = charts_util.visualize_chart(
                GUI_util.window,
                inputFilename,
                outputDir,
                complete_sid=False,
                csv_field_Y_axis_list=csv_file_field_Y_axis_list,
                X_axis_var=X_axis_var,
            )
        else:
            outputFiles = charts_util.visualize_chart(
                GUI_util.window,
                inputFilename,
                outputDir,
                complete_sid=False,
                csv_field_Y_axis_list=csv_file_field_Y_axis_list,
                X_axis_var=X_axis_var,
            )
        if outputFiles != None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    elif "Correlation" in visualizations_menu_var:
        outputFile = charts_util.correlation_heatmap(inputFilename, outputDir)
        if outputFile:
            filesToOpen.append(outputFile)

    elif "Histogram" in visualizations_menu_var:
        if csv_field_visualization_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a numeric csv file field and try again.",
            )
            return
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename,
            "",
            outputDir,
            ".html",
            "histogram",
            csv_field_visualization_var,
        )
        nbins = (
            int(histogram_nbins_var)
            if histogram_nbins_var.isdigit() and int(histogram_nbins_var) > 0
            else 0
        )
        marginal = histogram_marginal_var if histogram_marginal_var else None
        category = histogram_category_var if histogram_category_var else None
        outputFile = charts_util.histogram(
            inputFilename,
            outputFilename,
            csv_field_visualization_var,
            nbins=nbins,
            category=category,
            marginal=marginal,
        )
        if outputFile:
            filesToOpen.append(outputFile)

    elif "Violin" in visualizations_menu_var:
        if csv_field_visualization_var == "":
            mb.showwarning(
                "Warning",
                "No Y-axis variable has been selected.\n\nPlease, select a numeric csv file field and try again.",
            )
            return
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, "", outputDir, ".html", "violin", csv_field_visualization_var
        )
        category = violin_category_var if violin_category_var else None
        outputFile = charts_util.violin_plot(
            inputFilename,
            outputFilename,
            csv_field_visualization_var,
            points=violin_points_var,
            category=category,
        )
        if outputFile:
            filesToOpen.append(outputFile)

    if openOutputFiles and len(filesToOpen) > 0:
        IO_files_util.OpenOutputFiles(
            GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName
        )


# ── GUI setup ──────────────────────────────────────────────────────────────────

IO_setup_display_brief = True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(
    IO_setup_display_brief,
    GUI_width=GUI_IO_util.get_GUI_width(3),
    GUI_height_brief=600,
    GUI_height_full=680,
    y_multiplier_integer=GUI_util.y_multiplier_integer,
    y_multiplier_integer_add=2,
    increment=2,
)

GUI_label = "Graphical User Interface (GUI) for Data Visualization"
config_filename = "NLP_default_IO_config.csv"
head, scriptName = os.path.split(os.path.basename(__file__))

config_input_output_numeric_options = [3, 0, 0, 1]

GUI_util.set_window(
    GUI_size, GUI_label, config_filename, config_input_output_numeric_options
)
window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(
    config_input_output_numeric_options,
    config_filename,
    IO_setup_display_brief,
    scriptName,
)

# ── Shared variables ──────────────────────────────────────────────────────────

extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()
input_csv_file_var = tk.StringVar()

# Relational tab variables
relations_menu_var = tk.StringVar()
Gephi_var = tk.IntVar()
Sankey_var = tk.IntVar()
selected_csv_file_fields_var = tk.StringVar()
csv_field_relational_var = tk.StringVar()
dynamic_network_field_var = tk.StringVar()
selected_csv_file_fields = tk.StringVar()

# Categorical tab variables
categorical_menu_var = tk.StringVar()
csv_field_categorical_var = tk.StringVar()
search_values_categorical_var = tk.StringVar()
case_sensitive_var = tk.IntVar()
filter_options_var = tk.StringVar()
fixed_param_var = tk.StringVar()
rate_param_var = tk.StringVar()
base_param_var = tk.StringVar()
max_rows_var = tk.IntVar()
color_1_var = tk.IntVar()
color_2_var = tk.IntVar()
color_1_style_var = tk.StringVar()
color_2_style_var = tk.StringVar()
data_transformation_var = tk.StringVar()

# Temporal tab variables
temporal_menu_var = tk.StringVar()
temporal_menu_var.set("Time mapper")
timeline_Y_axis_var = tk.StringVar()
time_mapper_field_var = tk.StringVar()
calendar_date_var = tk.StringVar()
calendar_value_var = tk.StringVar()
date_format_var = tk.StringVar()
date_format_var.set("mm-dd-yyyy")
time_var = tk.StringVar()
time_var.set("Daily")
cumulative_var = tk.IntVar()

# Numeric tab variables
visualizations_menu_var = tk.StringVar()
csv_field_visualization_var = tk.StringVar()
Y_axis_var = tk.StringVar()
X_axis_var = tk.StringVar()
split_data_byCategory_var = tk.IntVar()
csv_field_boxplot_var = tk.StringVar()
csv_field_boxplot_color_var = tk.StringVar()
X_axis_bubble_var = tk.StringVar()
points_var = tk.StringVar()
histogram_nbins_var = tk.StringVar()
histogram_category_var = tk.StringVar()
histogram_marginal_var = tk.StringVar()
violin_points_var = tk.StringVar()
violin_category_var = tk.StringVar()
csv_file_var = tk.StringVar()

# Shared lists
csv_file_categorical_field_string = ""
csv_file_relational_field_list = []
csv_file_categorical_field_list = []
csv_file_field_Y_axis_list = []
csv_files_list = []
file_menu_values = []
menu_values = []
color_1_style_var_list = []
color_2_style_var_list = []
color_1_var_list = []
color_2_var_list = []
error = False
csv_field_visualization_var_SV = ""

# ── Shared widgets on window (GUIs available + csv file display) ──────────────


def open_GUI(*args):
    if "manipulation" in extra_GUIs_menu_var.get():
        run_script_util.run_script("data_manipulation_main.py")
    elif "Texts to maps" in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_main.py")
    elif "Google Earth" in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_Google_Earth_main.py")
    elif "Proportional" in extra_GUIs_menu_var.get():
        run_script_util.run_script("GIS_main.py")
    elif "HTML" in extra_GUIs_menu_var.get():
        run_script_util.run_script("html_annotator_main.py")
    elif "Wordclouds" in extra_GUIs_menu_var.get():
        run_script_util.run_script("wordclouds_main.py")


extra_GUIs_menu_var.trace("w", open_GUI)

extra_GUIs_var.set(0)
extra_GUIs_checkbox = GUI_theme_util.create_checkbox(
    window,
    text="GUIs available for more analyses ",
    variable=extra_GUIs_var,
    onvalue=1,
    offvalue=0,
    command=lambda: activate_all_options(),
)
y_multiplier_integer = GUI_IO_util.placeWidget(
    window,
    GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    extra_GUIs_checkbox,
    True,
)

extra_GUIs_menu_var.set("")
extra_GUIs_menu = GUI_theme_util.create_option_menu(
    window,
    variable=extra_GUIs_menu_var,
    values=[
        "Data manipulation",
        "Texts to maps (Open GUI)",
        "Google Earth Pro (Open GUI)",
        "Proportional circle map (Open GUI)",
        "HTML annotator (Open GUI)",
        "Wordclouds (Open GUI)",
    ],
)
extra_GUIs_menu.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(
    window,
    GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    extra_GUIs_menu,
    False,
    False,
    True,
    False,
    90,
    GUI_IO_util.IO_configuration_menu,
    "Select other related types of analysis you wish to perform\nThe selected GUI will open without having to press RUN",
)


# CSV file display row
def get_input_csv_file(window_ref, title, fileType):
    if input_csv_file_var.get() != "":
        initialFolder = os.path.dirname(os.path.abspath(input_csv_file_var.get()))
    else:
        initialFolder = os.path.dirname(os.path.abspath(__file__))
    filePath = tk.filedialog.askopenfilename(
        title=title, initialdir=initialFolder, filetypes=fileType
    )
    if len(filePath) > 0:
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(
            filePath, "utf-8"
        )
        if nRecords == 0:
            mb.showwarning(
                title="Warning",
                message="The selected input csv file is empty.\n\nPlease, select a different file and try again.",
            )
            filePath = ""
        else:
            input_csv_file_var.set(filePath)
            changed_filename(filePath)
    return filePath


input_csv_file_button = GUI_theme_util.create_button(
    window,
    width=GUI_IO_util.select_file_directory_button_width,
    text="Select INPUT CSV file",
    command=lambda: get_input_csv_file(
        window, "Select INPUT csv file", [("csv files", "*.csv")]
    ),
)
y_multiplier_integer = GUI_IO_util.placeWidget(
    window,
    GUI_IO_util.labels_x_coordinate,
    y_multiplier_integer,
    input_csv_file_button,
    True,
)

open_input_csv_file_button = GUI_theme_util.create_open_file_button(
    window, command=lambda: IO_files_util.openFile(window, input_csv_file_var.get())
)
y_multiplier_integer = GUI_IO_util.placeWidget(
    window,
    GUI_IO_util.IO_configuration_menu,
    y_multiplier_integer,
    open_input_csv_file_button,
    True,
    False,
    True,
    False,
    90,
    GUI_IO_util.IO_configuration_menu,
    "Open INPUT csv file",
)

input_csv_file_entry = GUI_theme_util.create_entry(
    window, width=GUI_IO_util.csv_file_width, textvariable=input_csv_file_var
)
input_csv_file_entry.configure(state="disabled")
y_multiplier_integer = GUI_IO_util.placeWidget(
    window,
    GUI_IO_util.entry_box_x_coordinate,
    y_multiplier_integer,
    input_csv_file_entry,
)

# ── Read initial csv headers ──────────────────────────────────────────────────


def get_csv_file_menu_values():
    global menu_values
    if (
        GUI_util.inputFilename.get() != ""
        and GUI_util.inputFilename.get()[-4:] == ".csv"
    ):
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(
            GUI_util.inputFilename.get()
        )
        if IO_csv_util.csvFile_has_header(GUI_util.inputFilename.get()) == False:
            menu_values = range(1, nColumns + 1)
        else:
            data, headers = IO_csv_util.get_csv_data(GUI_util.inputFilename.get(), True)
            menu_values = headers
    else:
        nColumns = 0
        menu_values = " "
    if nColumns == -1:
        pass
    return menu_values


get_csv_file_menu_values()

if GUI_util.inputFilename.get() != "" and GUI_util.inputFilename.get()[-4:] == ".csv":
    file_menu_values = [inputFilename.get()]
else:
    file_menu_values = " "

# ── Notebook ──────────────────────────────────────────────────────────────────
#
# Phase 4 CTk re-layout: this GUI was the last one still hand-placing (.place(x=,y=)) its widgets --
# a ttk.Notebook whose seven tab frames held ~140 absolutely-positioned children. §3 of the migration
# plan maps ttk.Notebook -> CTkTabview, which also fixes a parenting hazard: CTk widgets read their
# background off the master, and a ttk.Frame has no queryable `bg`, so CTk children can't parent into
# ttk tab frames. CTkTabview.add(name) returns a real CTkFrame, so each tab's children get a valid CTk
# master. The absolute-pixel rows below are rebuilt as grid rows: each logical row is a transparent
# CTkFrame gridded in column 0 (widgets pack left-to-right inside it), with the row's ? HELP button
# gridded in column 1. The old ttk.Style/theme_use tab styling is gone with the notebook (§6).

TAB_RELATIONAL = "Relational"
TAB_CATEGORICAL = "Categorical"
TAB_TEMPORAL = "Temporal"
TAB_NUMERIC = "Numeric"
TAB_GEOGRAPHIC = "Geographic"
TAB_WORDCLOUDS = "Wordclouds"
TAB_TREE = "Hierarchical tree"
# run_command dispatched on the notebook's integer tab index; CTkTabview reports the selected tab by
# NAME (.get()), so keep the name->index map the dispatch used to read positionally.
_TAB_INDEX = {
    TAB_RELATIONAL: 0,
    TAB_CATEGORICAL: 1,
    TAB_TEMPORAL: 2,
    TAB_NUMERIC: 3,
    TAB_GEOGRAPHIC: 4,
    TAB_WORDCLOUDS: 5,
    TAB_TREE: 6,
}


def tab_help(parent, row, message):
    """Grid a per-row ? HELP button into column 1 of a tab (was a .place() at the far-right pixel x).

    ``width=10`` matches the char width ``place_help_button`` (GUI_IO_util.py) gives every other
    GUI's ? HELP buttons; without it CTkButton falls back to its 140px default, rendering these
    noticeably wider than the rest of the suite's reformatted (narrower) ? HELP buttons.
    """
    GUI_theme_util.create_button(
        parent, text="? HELP", width=10, command=lambda: mb.showinfo("NLP Suite Help", message)
    ).grid(row=row, column=1, sticky="ne", padx=(20, 10), pady=3)


def tab_row(parent, row):
    """A transparent CTkFrame gridded as one row of a tab; widgets pack left-to-right inside it.

    Replaces a band of .place(x=,y=)'d widgets that shared a common y. Packing inside a per-row frame
    keeps each row's internal columns independent of the other rows (grid columns are shared window-
    wide), so a wide row can't inflate a narrow one -- the column-sharing pitfall §2.2 warns about.
    """
    fr = ctk.CTkFrame(parent, fg_color="transparent")
    fr.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=2)
    return fr


_nb_width = GUI_IO_util.get_GUI_width(3) - GUI_IO_util.labels_x_coordinate - 20
_nb_height = 320
notebook = ctk.CTkTabview(window, width=_nb_width, height=_nb_height)
# The body is grid-managed (slice 2b), so the tabview is gridded into the current row spanning the
# full column band -- a .place() here would put it at a pixel-y the grid no longer uses.
notebook.grid(
    row=GUI_IO_util._GRID_HEADER_ROWS + int(round(y_multiplier_integer)),
    column=0,
    columnspan=GUI_IO_util._GRID_TOTAL_COLUMNS,
    padx=(GUI_IO_util.labels_x_coordinate, 10),
    pady=6,
    sticky="we",
)

tab_relational = notebook.add(TAB_RELATIONAL)
tab_categorical = notebook.add(TAB_CATEGORICAL)
tab_temporal = notebook.add(TAB_TEMPORAL)
tab_numeric = notebook.add(TAB_NUMERIC)
tab_geographic = notebook.add(TAB_GEOGRAPHIC)
tab_wordclouds = notebook.add(TAB_WORDCLOUDS)
tab_tree = notebook.add(TAB_TREE)
notebook.set(TAB_RELATIONAL)
# Column 0 (the row frames) absorbs the tab width so the ? HELP column stays pinned to the right edge.
for _tab in (
    tab_relational,
    tab_categorical,
    tab_temporal,
    tab_numeric,
    tab_geographic,
    tab_wordclouds,
    tab_tree,
):
    _tab.grid_columnconfigure(0, weight=1)

# Advance y_multiplier_integer past the notebook area (320px / 40px per row = 8 rows)
y_multiplier_integer = y_multiplier_integer + 8

# ── Tab 1: Relational ────────────────────────────────────────────────────────

_r0 = tab_row(tab_relational, 0)
tab_help(
    tab_relational,
    0,
    "Select a visualization type from the dropdown menu: * (all), Gephi network graph, Network graph (vis.js), or Sankey flowchart.\n\n"
    "Select * to run all available options.",
)

relations_lb = GUI_theme_util.create_label(_r0, text="Visualize relations")
relations_lb.pack(side="left", padx=(0, 8))

relations_menu_var.set("Gephi")
relations_menu = GUI_theme_util.create_option_menu(
    _r0,
    variable=relations_menu_var,
    values=["*", "Gephi", "Network graph (vis.js)", "Sankey"],
)
relations_menu.pack(side="left")

_r1 = tab_row(tab_relational, 1)
tab_help(
    tab_relational,
    1,
    "Select a csv file field from the dropdown menu, then press the + button to add it.\n\n"
    "For Gephi/vis.js: select 3 fields in the order node, edge, node (e.g., Subject, Verb, Object).\n\n"
    "For Sankey: select 2 or 3 fields.\n\n"
    "Press Reset to clear your selections. The selected fields are shown in the entry area.\n\n"
    "vis.js supports the display of images for nodes. If the CSV has an Image or Photo column with URLs, nodes render as circular portraits instead of colored dots.",
)

csv_field_lb = GUI_theme_util.create_label(_r1, text="csv file field")
csv_field_lb.pack(side="left", padx=(0, 8))

csv_field_relational_menu = GUI_theme_util.create_option_menu(
    _r1, variable=csv_field_relational_var, values=list(menu_values)
)
csv_field_relational_menu.pack(side="left", padx=(0, 8))

selected_csv_fields_area = GUI_theme_util.create_entry(
    _r1, width=30, state="disabled", textvariable=selected_csv_file_fields
)
selected_csv_fields_area.pack(side="left", padx=(0, 8))


def display_selected_csv_fields():
    if (
        csv_field_relational_var.get() != ""
        and not csv_field_relational_var.get() in csv_file_relational_field_list
    ):
        csv_file_relational_field_list.append(csv_field_relational_var.get())
        new_string = ", ".join(csv_file_relational_field_list)
        selected_csv_file_fields.set(new_string.lstrip())
    else:
        mb.showwarning(
            title="Warning",
            message='The option "'
            + csv_field_relational_var.get()
            + '" has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.',
        )
        csv_field_relational_menu.configure(state="normal")
    selected_csv_file_fields_var.set(str(csv_file_relational_field_list))
    activate_csv_fields_relational_selection(True)


def reset_relational():
    csv_file_relational_field_list.clear()
    csv_field_relational_var.set("")
    selected_csv_file_fields.set("")
    dynamic_network_field_var.set("")
    selected_csv_file_fields_var.set("")


add_button_relational = GUI_theme_util.create_button(
    _r1, text="+", width=2, command=lambda: display_selected_csv_fields()
)
add_button_relational.pack(side="left", padx=(0, 6))

reset_button_relational = GUI_theme_util.create_button(
    _r1, text="Reset", width=4, state="disabled", command=lambda: reset_relational()
)
reset_button_relational.pack(side="left")


def show_Gephi_options_list():
    if len(csv_file_relational_field_list) == 0:
        mb.showwarning(
            title="Warning", message="There are no currently selected Gephi options."
        )
    else:
        mb.showwarning(
            title="Warning",
            message="The currently selected Gephi options are:\n\n  "
            + "\n  ".join(csv_file_relational_field_list)
            + "\n\nPlease, press the Reset button (or ESCape) to start fresh.",
        )


# Gephi/vis.js row
_r2 = tab_row(tab_relational, 2)
tab_help(
    tab_relational,
    2,
    "Optionally select a date field to create a DYNAMIC (time-varying) network graph.\n\n"
    "If no date field is selected, a static network graph will be produced.",
)

Gephi_lb = GUI_theme_util.create_label(
    _r2, text="Gephi/vis.js", foreground="red", font=(_ui_font_family, 12, "bold")
)
Gephi_lb.pack(side="left", padx=(0, 8))

csv_field_dynamic_network_lb = GUI_theme_util.create_label(
    _r2, text="csv file field for dynamic graph"
)
csv_field_dynamic_network_lb.pack(side="left", padx=(0, 8))

dynamic_network_field_menu = GUI_theme_util.create_option_menu(
    _r2, variable=dynamic_network_field_var, values=list(menu_values)
)
dynamic_network_field_menu.configure(state="disabled")
dynamic_network_field_menu.pack(side="left")

# Sankey row
_r3 = tab_row(tab_relational, 3)
tab_help(
    tab_relational,
    3,
    "Adjust the maximum number of items displayed for each variable in the Sankey chart.\n\n"
    "Variable 1, 2, and 3 correspond to the csv fields selected above in order.",
)

Sankey_lb = GUI_theme_util.create_label(
    _r3, text="Sankey", foreground="red", font=(_ui_font_family, 12, "bold")
)
Sankey_lb.pack(side="left", padx=(0, 8))

Sankey_limit1_lb = GUI_theme_util.create_label(_r3, text="Variable 1 max")
Sankey_limit1_lb.pack(side="left", padx=(0, 6))

Sankey_limit1_var = tk.IntVar()
Sankey_limit1_var.set(5)
Sankey_limit1_menu = GUI_theme_util.create_option_menu(
    _r3, variable=Sankey_limit1_var, values=["5", "10"]
)
Sankey_limit1_menu.pack(side="left", padx=(0, 12))

Sankey_limit2_lb = GUI_theme_util.create_label(_r3, text="Variable 2 max")
Sankey_limit2_lb.pack(side="left", padx=(0, 6))

Sankey_limit2_var = tk.IntVar()
Sankey_limit2_var.set(10)
Sankey_limit2_menu = GUI_theme_util.create_option_menu(
    _r3, variable=Sankey_limit2_var, values=["5", "10", "20"]
)
Sankey_limit2_menu.pack(side="left", padx=(0, 12))

Sankey_limit3_lb = GUI_theme_util.create_label(_r3, text="Variable 3 max")
Sankey_limit3_lb.pack(side="left", padx=(0, 6))

Sankey_limit3_var = tk.IntVar()
Sankey_limit3_var.set(20)
Sankey_limit3_menu = GUI_theme_util.create_option_menu(
    _r3, variable=Sankey_limit3_var, values=["5", "10", "20", "30"]
)
Sankey_limit3_menu.pack(side="left")


def activate_csv_fields_relational_selection(comingFromPlus=False):
    if csv_field_relational_var.get() != "":
        if comingFromPlus:
            csv_field_relational_menu.configure(state="normal")
        else:
            csv_field_relational_menu.configure(state="disabled")
        add_button_relational.configure(state="normal")
        reset_button_relational.configure(state="normal")
        if len(csv_file_relational_field_list) == 3:
            csv_field_relational_menu.configure(state="disabled")
            dynamic_network_field_menu.configure(state="normal")
            if dynamic_network_field_var.get() == "":
                mb.showwarning(
                    title="Warning",
                    message='You have selected the maximum number of fields (3) to visualize relations.\n\nPress the "Show" button to display your selection. Press the "Reset" button to clear your selection and start again.',
                )
    else:
        csv_field_relational_menu.configure(state="normal")
        dynamic_network_field_menu.configure(state="normal")
        reset_button_relational.configure(state="disabled")


csv_field_relational_var.trace(
    "w", callback=lambda x, y, z: activate_csv_fields_relational_selection()
)
dynamic_network_field_var.trace(
    "w", callback=lambda x, y, z: activate_csv_fields_relational_selection()
)


# ── Tab 2: Categorical ───────────────────────────────────────────────────────

_c0 = tab_row(tab_categorical, 0)
tab_help(
    tab_categorical,
    0,
    "Select a chart type from the dropdown menu: * (all), Colormap/heatmap, Comparative bar charts, Grouped bar, Stacked bar, Sunburst, Treemap, or Waffle chart.\n\n"
    "STACKED BAR / GROUPED BAR / SUNBURST / TREEMAP / WAFFLE CHART: just select the chart type and press RUN — no extra options needed.\n\n"
    "COLORMAP/HEATMAP: configure Max rows, colors, and normalization on the Colormap row below.\n\n"
    "COMPARATIVE BAR CHARTS: select csv files to compare on the Comparative row below.\n\n"
    "Select * to run all available options.",
)

categorical_lb = GUI_theme_util.create_label(_c0, text="Visualize categorical data")
categorical_lb.pack(side="left", padx=(0, 8))

categorical_menu_var.set("Sunburst")
categorical_menu = GUI_theme_util.create_option_menu(
    _c0,
    variable=categorical_menu_var,
    values=[
        "*",
        "Colormap/heatmap",
        "Comparative bar charts",
        "Grouped bar",
        "Stacked bar",
        "Sunburst",
        "Treemap",
        "Waffle chart",
    ],
)
categorical_menu.pack(side="left")

_c1 = tab_row(tab_categorical, 1)
tab_help(
    tab_categorical,
    1,
    "Select a csv file field from the dropdown, optionally enter search values (comma-separated), "
    "then press the + button to add the combination.\n\n"
    "Repeat for at least one more field. You need at least 2 field/value combinations.\n\n"
    "Use Reset to clear and Show to display your current selections.",
)

csv_field_categorical_lb = GUI_theme_util.create_label(_c1, text="Search field")
csv_field_categorical_lb.pack(side="left", padx=(0, 8))

csv_field_categorical_menu = GUI_theme_util.create_option_menu(
    _c1, variable=csv_field_categorical_var, values=list(menu_values)
)
csv_field_categorical_menu.pack(side="left", padx=(0, 8))

case_sensitive_var.set(1)
case_sensitive_checkbox = GUI_theme_util.create_checkbox(
    _c1, text="Case", variable=case_sensitive_var, onvalue=1, offvalue=0
)
case_sensitive_checkbox.pack(side="left", padx=(0, 8))

search_values_categorical_label_lb = GUI_theme_util.create_label(
    _c1, text="Search values"
)
search_values_categorical_label_lb.pack(side="left", padx=(0, 6))

search_values_categorical_var.set("")
search_values_categorical = GUI_theme_util.create_entry(
    _c1, state="disabled", textvariable=search_values_categorical_var, width=20
)
search_values_categorical.pack(side="left", padx=(0, 8))


def add_combination_csvField_searchValues():
    global csv_file_categorical_field_string
    if (not search_values_categorical_var.get() == "") and (
        search_values_categorical_var.get() in csv_file_categorical_field_string
    ):
        result = mb.askyesno(
            "Warning",
            'You have already entered the search value(s) "'
            + search_values_categorical_var.get()
            + '"\n\nAre you sure you want to use the same search values?',
        )
        if not result:
            return
    csv_file_categorical_field_string = (
        csv_field_categorical_var.get() + "|" + search_values_categorical_var.get()
    )
    csv_file_categorical_field_list.append([csv_file_categorical_field_string])
    search_values_categorical_var.set("")
    csv_field_categorical_menu.focus_set()
    activate_all_options()


add_button_categorical = GUI_theme_util.create_button(
    _c1, text="+", width=2, command=lambda: add_combination_csvField_searchValues()
)
add_button_categorical.pack(side="left", padx=(0, 6))


def reset_categorical():
    csv_file_categorical_field_list.clear()
    csv_field_categorical_var.set("")
    search_values_categorical_var.set("")
    csv_field_categorical_menu.configure(state="normal")
    if csv_field_categorical_var.get() == "" and "Document" in menu_values:
        csv_field_categorical_var.set("Document")


reset_button_categorical = GUI_theme_util.create_button(
    _c1, text="Reset", width=4, command=lambda: reset_categorical()
)
reset_button_categorical.pack(side="left", padx=(0, 6))


def show_categorical_list():
    if len(csv_file_categorical_field_list) == 0:
        mb.showwarning(
            title="Warning",
            message="There are no currently selected combinations of csv file field and search words.",
        )
    else:
        mb.showwarning(
            title="Warning",
            message="The currently selected combination of csv file field and search word are:\n\n"
            + str(csv_file_categorical_field_list)
            + "\n\nPlease, press the Reset button (or ESCape) to start fresh.",
        )


show_button_categorical = GUI_theme_util.create_button(
    _c1, text="Show", width=4, command=lambda: show_categorical_list()
)
show_button_categorical.pack(side="left")

# Filtering row
_c2 = tab_row(tab_categorical, 2)
tab_help(
    tab_categorical,
    2,
    "Select a filtering option for Sunburst/Treemap charts.\n\n"
    "No filtering: display all data.\n"
    "Fixed parameter: filter items below a fixed frequency threshold.\n"
    "Propagating parameter: filter using a rate and base that propagate through hierarchy levels.",
)

filter_lb = GUI_theme_util.create_label(_c2, text="Filtering options")
filter_lb.pack(side="left", padx=(0, 8))

filter_options_var.set("No filtering")
filter_options_menu = GUI_theme_util.create_option_menu(
    _c2,
    variable=filter_options_var,
    values=["No filtering", "Fixed parameter", "Propagating parameter"],
)
filter_options_menu.pack(side="left", padx=(0, 12))

fixed_param_lb = GUI_theme_util.create_label(_c2, text="Fixed")
fixed_param_lb.pack(side="left", padx=(0, 6))

fixed_param_var.set(15)
fixed_param = GUI_theme_util.create_entry(
    _c2, state="disabled", textvariable=fixed_param_var, width=3
)
fixed_param.pack(side="left", padx=(0, 12))

rate_param_lb = GUI_theme_util.create_label(_c2, text="Rate")
rate_param_lb.pack(side="left", padx=(0, 6))

rate_param_var.set(3)
rate_param = GUI_theme_util.create_entry(
    _c2, state="disabled", textvariable=rate_param_var, width=3
)
rate_param.pack(side="left", padx=(0, 12))

base_param_lb = GUI_theme_util.create_label(_c2, text="Base")
base_param_lb.pack(side="left", padx=(0, 6))

base_param_var.set(15)
base_param = GUI_theme_util.create_entry(
    _c2, state="disabled", textvariable=base_param_var, width=3
)
base_param.pack(side="left")


def activate_filtering_options(*args):
    fixed_param.configure(state="disabled")
    rate_param.configure(state="disabled")
    base_param.configure(state="disabled")
    if "Fixed" in filter_options_var.get():
        fixed_param.configure(state="normal")
    if "Propagating" in filter_options_var.get():
        rate_param.configure(state="normal")
        base_param.configure(state="normal")


filter_options_var.trace("w", activate_filtering_options)

# Colormap row
_c3 = tab_row(tab_categorical, 3)
tab_help(
    tab_categorical,
    3,
    "Colormap/heatmap options (only active when Colormap/heatmap is selected).\n\n"
    "Max rows: maximum number of rows to display.\n"
    "Color: click the checkbox to pick a custom color for the start/end of the color gradient.\n"
    "Normalize: apply a data transformation (Min-Max, Z-score, etc.) before plotting.",
)

colormap_lb = GUI_theme_util.create_label(
    _c3, text="Colormap/heatmap", foreground="red", font=(_ui_font_family, 12, "bold")
)
colormap_lb.pack(side="left", padx=(0, 8))

max_rows_lb = GUI_theme_util.create_label(_c3, text="Max rows")
max_rows_lb.pack(side="left", padx=(0, 6))

max_rows_var.set(20)
max_rows = GUI_theme_util.create_entry(
    _c3, state="disabled", textvariable=max_rows_var, width=3
)
max_rows.pack(side="left", padx=(0, 12))

color_1_var.set(0)
color_1_style_var_list.append("")
color_1_var_list.append(0)
color_1_checkbox = GUI_theme_util.create_checkbox(
    _c3, text="Color ", variable=color_1_var, onvalue=1, offvalue=0
)
color_1_checkbox.pack(side="left", padx=(0, 6))

color_1_style_var.set("135, 207, 236")
color_1_entry = GUI_theme_util.create_entry(
    _c3, width=10, textvariable=color_1_style_var
)
color_1_entry.configure(state="disabled")
color_1_entry.pack(side="left", padx=(0, 12))


def activate_color_1_palette(*args):
    try:
        from tkcolorpicker import askcolor

        if color_1_var.get() == 1:
            color_1_list = askcolor((135, 207, 236), window)
            color_1_style = color_1_list[0]
            color_1_style_var.set(color_1_style)
    except ImportError:
        pass


color_1_var.trace("w", activate_color_1_palette)

color_2_var.set(0)
color_2_style_var_list.append("")
color_2_var_list.append(0)
color_2_checkbox = GUI_theme_util.create_checkbox(
    _c3, text="Color ", variable=color_2_var, onvalue=1, offvalue=0
)
color_2_checkbox.pack(side="left", padx=(0, 6))

color_2_style_var.set("0, 0, 255")
color_2_entry = GUI_theme_util.create_entry(
    _c3, width=10, textvariable=color_2_style_var
)
color_2_entry.configure(state="disabled")
color_2_entry.pack(side="left", padx=(0, 12))


def activate_color_2_palette(*args):
    try:
        from tkcolorpicker import askcolor

        if color_2_var.get() == 1:
            color_2_list = askcolor((0, 0, 255), window)
            color_2_style = color_2_list[0]
            color_2_style_var.set(color_2_style)
    except ImportError:
        pass


color_2_var.trace("w", activate_color_2_palette)

data_transformation_lb = GUI_theme_util.create_label(_c3, text="Normalize")
data_transformation_lb.pack(side="left", padx=(0, 6))

data_transformation_var.set("No transform")
data_transformation_menu = GUI_theme_util.create_option_menu(
    _c3,
    variable=data_transformation_var,
    values=["No transform", "Min-Max", "Z-score", "Square root", "Log", "Ln"],
)
data_transformation_menu.pack(side="left")

# Comparative bar charts row
_c4 = tab_row(tab_categorical, 4)
tab_help(
    tab_categorical,
    4,
    "Comparative bar charts compare the same variable across multiple csv files.\n\n"
    "Use the + button to add csv files (at least 2 required).\n"
    "Select a Y-axis field from the main Y-axis dropdown above.\n"
    "Press Reset to clear the file list.",
)

comparative_bar_lb = GUI_theme_util.create_label(
    _c4, text="Comparative bar charts", foreground="red", font=(_ui_font_family, 12, "bold")
)
comparative_bar_lb.pack(side="left", padx=(0, 8))


def add_csvFile_comparative(window_ref, title, fileType):
    initialFolder = GUI_util.output_dir_path.get()
    filePath = tk.filedialog.askopenfilename(
        title=title, initialdir=initialFolder, filetypes=fileType
    )
    if len(filePath) > 0:
        if filePath not in csv_files_list:
            csv_files_list.append(filePath)
            process_csv_file_menu_comparative(filePath)
        else:
            mb.showwarning(
                title="Warning",
                message="The file has already been selected. Selection ignored.",
            )


def process_csv_file_menu_comparative(InputFile):
    GUI_theme_util.set_values(csv_file_menu_comparative, list(csv_files_list))


add_file = GUI_theme_util.create_button(
    _c4,
    text="+",
    width=2,
    command=lambda: add_csvFile_comparative(
        window, "Select csv file", [("csv files", "*.csv")]
    ),
)
add_file.pack(side="left", padx=(0, 6))


def reset_files():
    csv_files_list.clear()
    csv_file_var.set("")
    if GUI_util.inputFilename.get().endswith(".csv"):
        csv_files_list.append(GUI_util.inputFilename.get())
        process_csv_file_menu_comparative(GUI_util.inputFilename.get())


reset_file_button = GUI_theme_util.create_button(
    _c4, text="Reset", width=4, command=lambda: reset_files()
)
reset_file_button.pack(side="left", padx=(0, 6))

openInputFile_button_comparative = GUI_theme_util.create_open_file_button(
    _c4, command=lambda: IO_files_util.openFile(window, csv_file_var.get())
)
openInputFile_button_comparative.pack(side="left", padx=(0, 8))

select_csv_file_lb = GUI_theme_util.create_label(_c4, text="Select csv file")
select_csv_file_lb.pack(side="left", padx=(0, 6))

csv_file_menu_comparative = GUI_theme_util.create_option_menu(
    _c4, variable=csv_file_var, values=list(file_menu_values)
)
csv_file_menu_comparative.pack(side="left")


def activate_csv_fields_categorical_selection(comingFromPlus=True):
    global csv_file_categorical_field_string
    if csv_field_categorical_var.get() != "":
        if csv_field_categorical_var.get() in csv_file_categorical_field_list:
            mb.showwarning(
                title="Warning",
                message="The option has already been selected. Selection ignored.\n\nYou can see your current selections by clicking the Show button.",
            )
            return
        else:
            csv_file_categorical_field_string = (
                csv_file_categorical_field_string
                + "|"
                + csv_field_categorical_var.get()
            )
    if csv_field_categorical_var.get() != "":
        search_values_categorical.configure(state="normal")
        if comingFromPlus:
            csv_field_categorical_menu.configure(state="normal")
        else:
            csv_field_categorical_menu.configure(state="disabled")
        add_button_categorical.configure(state="normal")
        reset_button_categorical.configure(state="normal")
    else:
        search_values_categorical.configure(state="disabled")
        csv_field_categorical_menu.configure(state="normal")
    activate_all_options()


categorical_menu_var.trace(
    "w", callback=lambda x, y, z: activate_csv_fields_categorical_selection()
)


# ── Tab 3: Temporal ───────────────────────────────────────────────────────────

_t0 = tab_row(tab_temporal, 0)
tab_help(
    tab_temporal,
    0,
    "Select a visualization type:\n  Calendar heatmap — days × weeks grid colored by value; reveals seasonal patterns.\n  Time mapper — interactive HTML timeline.\n  Timeline plot — line chart via Excel/Plotly.",
)

temporal_options_lb = GUI_theme_util.create_label(_t0, text="Visualize temporal data")
temporal_options_lb.pack(side="left", padx=(0, 8))

temporal_menu_var.set("Time mapper")
temporal_menu = GUI_theme_util.create_option_menu(
    _t0,
    variable=temporal_menu_var,
    values=["Calendar heatmap", "Time mapper", "Timeline plot"],
)
temporal_menu.pack(side="left")

# Time mapper row
_t1 = tab_row(tab_temporal, 1)
tab_help(
    tab_temporal,
    1,
    "TIME MAPPER: creates an interactive HTML timeline.\nSelect the Y-axis field (the variable to display over time).",
)

temporal_lb = GUI_theme_util.create_label(
    _t1, text="Time mapper", foreground="red", font=(_ui_font_family, 12, "bold")
)
temporal_lb.pack(side="left", padx=(0, 8))

csv_field_time_mapper_lb = GUI_theme_util.create_label(_t1, text="Y-axis field")
csv_field_time_mapper_lb.pack(side="left", padx=(0, 8))

csv_field_temporal_menu = GUI_theme_util.create_option_menu(
    _t1, variable=csv_field_relational_var, values=list(menu_values)
)
csv_field_temporal_menu.pack(side="left")

_t2 = tab_row(tab_temporal, 2)
tab_help(
    tab_temporal,
    2,
    "Select the Date field, date Format, Timeline granularity (Daily/Monthly/Yearly), and optionally check Cumulative.",
)

date_field_lb = GUI_theme_util.create_label(_t2, text="Date field")
date_field_lb.pack(side="left", padx=(0, 8))

time_mapper_field_menu = GUI_theme_util.create_option_menu(
    _t2, variable=time_mapper_field_var, values=list(menu_values)
)
time_mapper_field_menu.pack(side="left", padx=(0, 12))

date_format_lb = GUI_theme_util.create_label(_t2, text="Format")
date_format_lb.pack(side="left", padx=(0, 6))

date_format_var.set("mm-dd-yyyy")
date_format_menu = GUI_theme_util.create_option_menu(
    _t2,
    variable=date_format_var,
    values=["mm-dd-yyyy", "dd-mm-yyyy", "yyyy-mm-dd", "yyyy-dd-mm", "yyyy-mm", "yyyy"],
)
date_format_menu.pack(side="left", padx=(0, 12))

select_time_lb = GUI_theme_util.create_label(_t2, text="Timeline")
select_time_lb.pack(side="left", padx=(0, 6))

time_var.set("Daily")
select_time_menu = GUI_theme_util.create_option_menu(
    _t2, variable=time_var, values=["Daily", "Monthly", "Yearly"]
)
select_time_menu.pack(side="left", padx=(0, 12))

cumulative_var.set(0)
cumulative_checkbox = GUI_theme_util.create_checkbox(
    _t2, text="Cumulative", variable=cumulative_var, onvalue=1, offvalue=0
)
cumulative_checkbox.pack(side="left")

# Timeline plot row
_t3 = tab_row(tab_temporal, 3)
tab_help(
    tab_temporal,
    3,
    "TIMELINE PLOT: creates a line chart (Excel or Plotly).\nSelect the Y-axis field and the Date field for the X-axis.\nChart package is controlled by the Charts package option at the bottom of the GUI.",
)

timeline_plot_lb = GUI_theme_util.create_label(
    _t3, text="Timeline plot", foreground="red", font=(_ui_font_family, 12, "bold")
)
timeline_plot_lb.pack(side="left", padx=(0, 8))

timeline_Y_axis_lb = GUI_theme_util.create_label(_t3, text="Y-axis field")
timeline_Y_axis_lb.pack(side="left", padx=(0, 8))

timeline_Y_axis_menu = GUI_theme_util.create_option_menu(
    _t3, variable=timeline_Y_axis_var, values=list(menu_values)
)
timeline_Y_axis_menu.pack(side="left", padx=(0, 12))

timeline_date_lb = GUI_theme_util.create_label(_t3, text="Date field (X-axis)")
timeline_date_lb.pack(side="left", padx=(0, 8))

timeline_date_var = tk.StringVar()
timeline_date_menu = GUI_theme_util.create_option_menu(
    _t3, variable=timeline_date_var, values=list(menu_values)
)
timeline_date_menu.pack(side="left")

# Calendar heatmap row
_t4 = tab_row(tab_temporal, 4)
tab_help(
    tab_temporal,
    4,
    "CALENDAR HEATMAP: shows daily values or event counts as a colored grid (days x weeks).\n"
    "Select the Date field. Optionally select a Value field (numeric); if blank, counts events per day.\n"
    "Date format is shared with the Time mapper row above.",
)

calendar_lb = GUI_theme_util.create_label(
    _t4, text="Calendar heatmap", foreground="red", font=(_ui_font_family, 12, "bold")
)
calendar_lb.pack(side="left", padx=(0, 8))

calendar_date_lb = GUI_theme_util.create_label(_t4, text="Date field")
calendar_date_lb.pack(side="left", padx=(0, 6))

calendar_date_menu = GUI_theme_util.create_option_menu(
    _t4, variable=calendar_date_var, values=list(menu_values)
)
calendar_date_menu.pack(side="left", padx=(0, 12))

calendar_value_lb = GUI_theme_util.create_label(_t4, text="Value field (optional)")
calendar_value_lb.pack(side="left", padx=(0, 6))

calendar_value_menu = GUI_theme_util.create_option_menu(
    _t4, variable=calendar_value_var, values=[""] + list(menu_values)
)
calendar_value_menu.pack(side="left")


# ── Tab 4: Numeric ────────────────────────────────────────────────────────────

_n0 = tab_row(tab_numeric, 0)
tab_help(
    tab_numeric,
    0,
    "Select a visualization type: Boxplots, Bubble chart, Correlation heatmap, Excel/Plotly charts, Histogram, or Violin plot.\n\n"
    "CORRELATION HEATMAP uses all numeric columns automatically — no Y-axis selection needed.",
)

visualization_basic_options_lb = GUI_theme_util.create_label(
    _n0, text="Visualization options"
)
visualization_basic_options_lb.pack(side="left", padx=(0, 8))

visualizations_menu_var.set("Excel/Plotly charts")
visualizations_menu = GUI_theme_util.create_option_menu(
    _n0,
    variable=visualizations_menu_var,
    values=[
        "Boxplots",
        "Bubble chart",
        "Correlation heatmap",
        "Excel/Plotly charts",
        "Histogram",
        "Violin plot",
    ],
)
visualizations_menu.pack(side="left")

_n1 = tab_row(tab_numeric, 1)
tab_help(
    tab_numeric,
    1,
    "Select the csv file field to use as the Y-axis for charts, boxplots, or bubble charts.",
)

csv_field_visualization_lb = GUI_theme_util.create_label(
    _n1, text="csv file field for visualization (Y-axis)"
)
csv_field_visualization_lb.pack(side="left", padx=(0, 8))

csv_field_visualization_menu = GUI_theme_util.create_option_menu(
    _n1, variable=csv_field_visualization_var, values=list(menu_values)
)
csv_field_visualization_menu.pack(side="left")


def check_selected_csv_file_field_Y_axis_list(main_Y_axis):
    global csv_field_visualization_var_SV
    if not "Excel" in visualizations_menu_var.get():
        return
    if csv_field_visualization_var.get() != "":
        if csv_field_visualization_var_SV == "":
            csv_field_visualization_var_SV = csv_field_visualization_var.get()
        else:
            if main_Y_axis:
                if csv_field_visualization_var_SV in str(
                    ", ".join(csv_file_field_Y_axis_list)
                ):
                    csv_file_field_Y_axis_list.remove(csv_field_visualization_var_SV)
                csv_field_visualization_var_SV = ""
    if main_Y_axis:
        field_value = csv_field_visualization_var.get()
    else:
        field_value = Y_axis_var.get()
    if field_value == "":
        return
    if field_value in str(", ".join(csv_file_field_Y_axis_list)):
        mb.showwarning(
            title="Warning",
            message='The option "'
            + field_value
            + '" has already been selected. Selection ignored.\n\nYou can see your current selections by using the dropdown menu.',
        )
    else:
        csv_file_field_Y_axis_list.append(field_value)


csv_field_visualization_var.trace(
    "w", lambda x, y, z: check_selected_csv_file_field_Y_axis_list(True)
)

# Excel/Plotly row
_n2 = tab_row(tab_numeric, 2)
tab_help(
    tab_numeric,
    2,
    "EXCEL/PLOTLY CHARTS: Select an X-axis field. Use + to add additional Y-axis fields, Reset to clear, Show to view current selections.",
)

Excel_Plotly_lb = GUI_theme_util.create_label(
    _n2, text="Excel/Plotly", foreground="red", font=(_ui_font_family, 12, "bold")
)
Excel_Plotly_lb.pack(side="left", padx=(0, 8))

X_axis_lb = GUI_theme_util.create_label(_n2, text="X-axis")
X_axis_lb.pack(side="left", padx=(0, 6))

X_axis_menu = GUI_theme_util.create_option_menu(
    _n2, variable=X_axis_var, values=list(file_menu_values)
)
X_axis_menu.pack(side="left", padx=(0, 12))

Y_axis_lb = GUI_theme_util.create_label(_n2, text="Additional Y-axis")
Y_axis_lb.pack(side="left", padx=(0, 6))

Y_axis_menu = GUI_theme_util.create_option_menu(
    _n2, variable=Y_axis_var, values=list(file_menu_values)
)
Y_axis_menu.pack(side="left", padx=(0, 12))

add_Y_axis = GUI_theme_util.create_button(
    _n2,
    text="+",
    width=2,
    command=lambda: check_selected_csv_file_field_Y_axis_list(False),
)
add_Y_axis.pack(side="left", padx=(0, 6))


def reset_csv_field_Y_axis_values():
    csv_file_field_Y_axis_list.clear()
    csv_field_visualization_menu.configure(state="normal")
    csv_field_visualization_var.set("")
    Y_axis_var.set("")


reset_Y_axis_button = GUI_theme_util.create_button(
    _n2,
    text="Reset",
    width=4,
    state="normal",
    command=lambda: reset_csv_field_Y_axis_values(),
)
reset_Y_axis_button.pack(side="left", padx=(0, 6))


def show_Y_axis_list():
    if len(csv_file_field_Y_axis_list) == 0:
        mb.showwarning(
            title="Warning",
            message="There are no currently selected additional Y-axis variables.",
        )
    else:
        mb.showwarning(
            title="Warning",
            message="The currently selected Y-axis variables are:\n\n"
            + ", ".join(csv_file_field_Y_axis_list)
            + "\n\nPlease, press the RESET button (or ESCape) to start fresh.",
        )


show_Y_axis_button = GUI_theme_util.create_button(
    _n2, text="Show", width=4, command=lambda: show_Y_axis_list()
)
show_Y_axis_button.pack(side="left")

# Boxplot row
_n3 = tab_row(tab_numeric, 3)
tab_help(
    tab_numeric,
    3,
    "BOXPLOT: Select data points to display (all, None, outliers). Optionally split by category and pick a category field and color field.",
)

boxplot_lb = GUI_theme_util.create_label(
    _n3, text="Boxplot", foreground="red", font=(_ui_font_family, 12, "bold")
)
boxplot_lb.pack(side="left", padx=(0, 8))

points_lb = GUI_theme_util.create_label(_n3, text="Data")
points_lb.pack(side="left", padx=(0, 6))

points_menu = GUI_theme_util.create_option_menu(
    _n3, variable=points_var, values=["all", "None", "outliers"]
)
points_menu.pack(side="left", padx=(0, 12))

split_data_byCategory_checkbox = GUI_theme_util.create_checkbox(
    _n3,
    variable=split_data_byCategory_var,
    text="Split data by category",
    onvalue=1,
    offvalue=0,
    command=lambda: activate_split_options(),
)
split_data_byCategory_checkbox.pack(side="left", padx=(0, 12))

csv_field2_lb = GUI_theme_util.create_label(_n3, text="csv file field")
csv_field2_lb.pack(side="left", padx=(0, 6))

csv_field_boxplot_menu = GUI_theme_util.create_option_menu(
    _n3, variable=csv_field_boxplot_var, values=list(menu_values)
)
csv_field_boxplot_menu.configure(state="disabled")
csv_field_boxplot_menu.pack(side="left", padx=(0, 12))

csv_field_boxplot_color_lb = GUI_theme_util.create_label(_n3, text="Color field")
csv_field_boxplot_color_lb.pack(side="left", padx=(0, 6))

csv_field_boxplot_color_menu = GUI_theme_util.create_option_menu(
    _n3, variable=csv_field_boxplot_color_var, values=list(menu_values)
)
csv_field_boxplot_color_menu.configure(state="disabled")
csv_field_boxplot_color_menu.pack(side="left")


def activate_split_options(*args):
    if split_data_byCategory_var.get():
        csv_field_boxplot_menu.configure(state="normal")
        csv_field_boxplot_color_menu.configure(state="normal")
    else:
        csv_field_boxplot_var.set("")
        csv_field_boxplot_color_var.set("")
        csv_field_boxplot_menu.configure(state="disabled")
        csv_field_boxplot_color_menu.configure(state="disabled")


split_data_byCategory_var.trace("w", activate_split_options)

# Bubble chart row
_n4 = tab_row(tab_numeric, 4)
tab_help(
    tab_numeric,
    4,
    "BUBBLE CHART: Select an X-axis field. Optionally enable Color and enter an RGB value (e.g., 135, 207, 236).",
)

bubble_chart_lb = GUI_theme_util.create_label(
    _n4, text="Bubble chart", foreground="red", font=(_ui_font_family, 12, "bold")
)
bubble_chart_lb.pack(side="left", padx=(0, 8))

X_axis_bubble_lb = GUI_theme_util.create_label(_n4, text="X-axis")
X_axis_bubble_lb.pack(side="left", padx=(0, 6))

X_axis_bubble_menu = GUI_theme_util.create_option_menu(
    _n4, variable=X_axis_bubble_var, values=list(file_menu_values)
)
X_axis_bubble_menu.pack(side="left", padx=(0, 12))

num_color_1_var = tk.IntVar()
num_color_1_style_var = tk.StringVar()
num_color_1_checkbox = GUI_theme_util.create_checkbox(
    _n4, text="Color", variable=num_color_1_var, onvalue=1, offvalue=0
)
num_color_1_checkbox.pack(side="left", padx=(0, 6))

num_color_1_style_var.set("135, 207, 236")
num_color_1_entry = GUI_theme_util.create_entry(
    _n4, width=10, textvariable=num_color_1_style_var
)
num_color_1_entry.configure(state="disabled")
num_color_1_entry.pack(side="left")

# Histogram row
_n5 = tab_row(tab_numeric, 5)
tab_help(
    tab_numeric,
    5,
    "HISTOGRAM: Shows the frequency distribution of a numeric variable.\n"
    "Optionally select a category field to color bars by group, and a marginal plot (rug, box, or violin).",
)

histogram_lb = GUI_theme_util.create_label(
    _n5, text="Histogram", foreground="red", font=(_ui_font_family, 12, "bold")
)
histogram_lb.pack(side="left", padx=(0, 8))

histogram_nbins_lb = GUI_theme_util.create_label(_n5, text="Bins")
histogram_nbins_lb.pack(side="left", padx=(0, 6))

histogram_nbins_var.set("0")
histogram_nbins_entry = GUI_theme_util.create_entry(
    _n5, width=4, textvariable=histogram_nbins_var
)
histogram_nbins_entry.pack(side="left", padx=(0, 12))

histogram_category_lb = GUI_theme_util.create_label(_n5, text="Group by")
histogram_category_lb.pack(side="left", padx=(0, 6))

histogram_category_menu = GUI_theme_util.create_option_menu(
    _n5, variable=histogram_category_var, values=list(menu_values)
)
histogram_category_menu.pack(side="left", padx=(0, 12))

histogram_marginal_lb = GUI_theme_util.create_label(_n5, text="Marginal")
histogram_marginal_lb.pack(side="left", padx=(0, 6))

histogram_marginal_var.set("")
histogram_marginal_menu = GUI_theme_util.create_option_menu(
    _n5, variable=histogram_marginal_var, values=["", "rug", "box", "violin"]
)
histogram_marginal_menu.pack(side="left")

# Violin plot row
_n6 = tab_row(tab_numeric, 6)
tab_help(
    tab_numeric,
    6,
    "VIOLIN PLOT: Shows the full distribution shape of a numeric variable.\n"
    "A box plot is drawn inside the violin. Select data points (all, None, outliers).\n"
    "Optionally split by a category field.",
)

violin_lb = GUI_theme_util.create_label(
    _n6, text="Violin plot", foreground="red", font=(_ui_font_family, 12, "bold")
)
violin_lb.pack(side="left", padx=(0, 8))

violin_points_lb = GUI_theme_util.create_label(_n6, text="Data")
violin_points_lb.pack(side="left", padx=(0, 6))

violin_points_var.set("all")
violin_points_menu = GUI_theme_util.create_option_menu(
    _n6, variable=violin_points_var, values=["all", "None", "outliers"]
)
violin_points_menu.pack(side="left", padx=(0, 12))

violin_category_lb = GUI_theme_util.create_label(_n6, text="Group by")
violin_category_lb.pack(side="left", padx=(0, 6))

violin_category_menu = GUI_theme_util.create_option_menu(
    _n6, variable=violin_category_var, values=list(menu_values)
)
violin_category_menu.pack(side="left")


# ── Tab 5: Geographic ───────────────────────────────────────────────────────

_g0 = tab_row(tab_geographic, 0)
tab_help(
    tab_geographic,
    0,
    "Geographic visualization: map where your corpus's entities are, and how they move.\n\n"
    "Geocodable space (real map coordinates) via the GIS / Google Earth GUIs; non-geocodable\n"
    "space (house, field, forest - no coordinates) via the Symbolic Space GUI. Use the per-row\n"
    "? HELP buttons for each option below.",
)

geo_description = GUI_theme_util.create_label(
    _g0, text="Geographic visualization", font=(_ui_font_family, 12, "bold"), foreground="red"
)
geo_description.pack(side="left")

_g1 = tab_row(tab_geographic, 1)
tab_help(
    tab_geographic,
    1,
    "Open a full mapping GUI:\n\n"
    "Open GIS GUI - geocodable geographic mapping (Google Earth Pro / Google Maps).\n"
    "Open Google Earth GUI - build KML / Google Earth maps from a csv.\n"
    "Open Symbolic (non-geocodable) Space GUI - the companion for kinds of place that carry\n"
    "social meaning but have NO map coordinates (house vs. field; gender / race / class x space).",
)

geo_open_button = GUI_theme_util.create_button(
    _g1,
    text="Open GIS GUI",
    width=18,
    command=lambda: run_script_util.run_script("GIS_main.py"),
)
geo_open_button.pack(side="left", padx=(0, 8))

geo_open_ge_button = GUI_theme_util.create_button(
    _g1,
    text="Open Google Earth GUI",
    width=22,
    command=lambda: run_script_util.run_script("GIS_Google_Earth_main.py"),
)
geo_open_ge_button.pack(side="left", padx=(0, 8))

# the non-geocodable sibling of GIS_main (kitchen/forest/threshold vs map coordinates)
geo_open_symbolic_button = GUI_theme_util.create_button(
    _g1,
    text="Open Symbolic (non-geocodable) Space GUI",
    width=40,
    command=lambda: run_script_util.run_script("GIS_symbolic_main.py"),
)
geo_open_symbolic_button.pack(side="left")


def run_entity_location_tracking():
    inputFile = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()
    import NER_location_tracking_util

    filesToOpen = NER_location_tracking_util.main(inputFile, inputDir, outputDir)
    if filesToOpen:
        csv_files = [f for f in filesToOpen if f.endswith(".csv")]
        if csv_files:
            csv_path = csv_files[0]
            GUI_util.inputFilename.set(csv_path)
            input_csv_file_var.set(csv_path)
            GUI_util.run_button.configure(state="normal")
            mig_entity_var.set("Entity")
            mig_location_var.set("Location")
        if openOutputFiles:
            IO_files_util.OpenOutputFiles(
                GUI_util.window, openOutputFiles, filesToOpen, outputDir
            )


_g2 = tab_row(tab_geographic, 2)
tab_help(
    tab_geographic,
    2,
    "Extract entity-location CSV from text (Stanza NER): runs NER on your text files and pairs\n"
    "every PERSON with every LOCATION mentioned in the same sentence, producing a csv ready for\n"
    "the animated movement map below. The result is auto-loaded into the input box.",
)

geo_gen_button = GUI_theme_util.create_button(
    _g2,
    text="Extract entity-location CSV from text (Stanza NER)",
    width=50,
    command=run_entity_location_tracking,
)
geo_gen_button.pack(side="left")

_g3 = tab_row(tab_geographic, 3)
tab_help(
    tab_geographic,
    3,
    "Animated movement map (from CSV): visualize how entities (people, characters) move across\n"
    "locations over time. Pick the Entity, Location, and optional Date/sequence columns; locations\n"
    "are auto-geocoded via Nominatim, or provide pre-geocoded Latitude / Longitude columns. Then RUN.",
)

geo_sep = GUI_theme_util.create_label(
    _g3,
    text="─── Animated movement map (from CSV) ───",
    font=(_ui_font_family, 10, "bold"),
    foreground="#555",
)
geo_sep.pack(side="left")

_g4 = tab_row(tab_geographic, 4)
mig_entity_label = GUI_theme_util.create_label(_g4, text="Entity/person column:")
mig_entity_label.pack(side="left", padx=(0, 8))
mig_entity_var = tk.StringVar()
mig_entity_menu = GUI_theme_util.create_combobox(
    _g4, textvariable=mig_entity_var, width=25, state="readonly"
)
mig_entity_menu.pack(side="left", padx=(0, 16))

mig_location_label = GUI_theme_util.create_label(_g4, text="Location column:")
mig_location_label.pack(side="left", padx=(0, 8))
mig_location_var = tk.StringVar()
mig_location_menu = GUI_theme_util.create_combobox(
    _g4, textvariable=mig_location_var, width=25, state="readonly"
)
mig_location_menu.pack(side="left")

_g5 = tab_row(tab_geographic, 5)
mig_date_label = GUI_theme_util.create_label(
    _g5, text="Date/sequence column (optional):"
)
mig_date_label.pack(side="left", padx=(0, 8))
mig_date_var = tk.StringVar()
mig_date_menu = GUI_theme_util.create_combobox(
    _g5, textvariable=mig_date_var, width=25, state="readonly"
)
mig_date_menu.pack(side="left")

_g6 = tab_row(tab_geographic, 6)
mig_lat_label = GUI_theme_util.create_label(_g6, text="Latitude col (optional):")
mig_lat_label.pack(side="left", padx=(0, 8))
mig_lat_var = tk.StringVar()
mig_lat_menu = GUI_theme_util.create_combobox(
    _g6, textvariable=mig_lat_var, width=20, state="readonly"
)
mig_lat_menu.pack(side="left", padx=(0, 16))

mig_lon_label = GUI_theme_util.create_label(_g6, text="Longitude col (optional):")
mig_lon_label.pack(side="left", padx=(0, 8))
mig_lon_var = tk.StringVar()
mig_lon_menu = GUI_theme_util.create_combobox(
    _g6, textvariable=mig_lon_var, width=20, state="readonly"
)
mig_lon_menu.pack(side="left")


# ── Tab 6: Wordclouds ──────────────────────────────────────────────────────

_w0 = tab_row(tab_wordclouds, 0)
tab_help(
    tab_wordclouds,
    0,
    "Generate word clouds from text files or CSV word-frequency data.\n\n"
    "The Wordclouds GUI provides options for customizing the cloud: max words, font, layout,\n"
    "lemmatization, stopword removal, POS-tag coloring, and more.\n\n"
    "Click 'Open Wordclouds GUI' to access the full set of options.",
)

wc_description = GUI_theme_util.create_label(
    _w0, text="Wordcloud visualization", font=(_ui_font_family, 12, "bold"), foreground="red"
)
wc_description.pack(side="left")

_w1 = tab_row(tab_wordclouds, 1)
wc_info = GUI_theme_util.create_label(
    _w1,
    wraplength=700,
    text="Generate word clouds to visualize word frequency and prominence.\n\n"
    "Wordclouds can be produced from raw text files or from CSV files\n"
    "containing word-frequency data.\n\n"
    "Options include: max number of words, font selection, horizontal/free layout,\n"
    "lemmatization, stopword/punctuation exclusion, POS-tag coloring, and MWE handling.",
)
wc_info.pack(side="left")

_w2 = tab_row(tab_wordclouds, 2)
wc_open_button = GUI_theme_util.create_button(
    _w2,
    text="Open Wordclouds GUI",
    width=20,
    command=lambda: run_script_util.run_script("wordclouds_main.py"),
)
wc_open_button.pack(side="left")


# ── Tab 7: Hierarchical tree ──────────────────────────────────────────────────

_tr0 = tab_row(tab_tree, 0)
tab_help(
    tab_tree,
    0,
    "Build an interactive hierarchical tree from a csv with parent-child columns - family\n"
    "trees / genealogy, org charts, PC-ACE grammar hierarchies, narrative structure, dependency\n"
    "trees. Map the columns below and click RUN. Use the per-row ? HELP for each column.",
)

tree_description = GUI_theme_util.create_label(
    _tr0,
    text="Hierarchical tree visualization",
    font=(_ui_font_family, 12, "bold"),
    foreground="red",
)
tree_description.pack(side="left")

_tr1 = tab_row(tab_tree, 1)
tab_help(
    tab_tree,
    1,
    "Parent column / Child column (required): each row of the csv is one edge, parent -> child;\n"
    "the tree is assembled from all such edges. E.g. for a genealogy, Parent = the ancestor and\n"
    "Child = their descendant.",
)

tree_parent_label = GUI_theme_util.create_label(_tr1, text="Parent column:")
tree_parent_label.pack(side="left", padx=(0, 8))
tree_parent_var = tk.StringVar()
tree_parent_menu = GUI_theme_util.create_combobox(
    _tr1, textvariable=tree_parent_var, width=25, state="readonly"
)
tree_parent_menu.pack(side="left", padx=(0, 16))

tree_child_label = GUI_theme_util.create_label(_tr1, text="Child column:")
tree_child_label.pack(side="left", padx=(0, 8))
tree_child_var = tk.StringVar()
tree_child_menu = GUI_theme_util.create_combobox(
    _tr1, textvariable=tree_child_var, width=25, state="readonly"
)
tree_child_menu.pack(side="left")

_tr2 = tab_row(tab_tree, 2)
tab_help(
    tab_tree,
    2,
    "Label column (optional): the display name shown on each node. Defaults to the child value\n"
    "when not set.",
)

tree_label_label = GUI_theme_util.create_label(_tr2, text="Label column (optional):")
tree_label_label.pack(side="left", padx=(0, 8))
tree_label_var = tk.StringVar()
tree_label_menu = GUI_theme_util.create_combobox(
    _tr2, textvariable=tree_label_var, width=25, state="readonly"
)
tree_label_menu.pack(side="left")

_tr3 = tab_row(tab_tree, 3)
tab_help(
    tab_tree,
    3,
    "Info / tooltip column (optional): extra text shown when you hover over a node.",
)

tree_info_label = GUI_theme_util.create_label(
    _tr3, text="Info/tooltip column (optional):"
)
tree_info_label.pack(side="left", padx=(0, 8))
tree_info_var = tk.StringVar()
tree_info_menu = GUI_theme_util.create_combobox(
    _tr3, textvariable=tree_info_var, width=25, state="readonly"
)
tree_info_menu.pack(side="left")

_tr4 = tab_row(tab_tree, 4)
tab_help(
    tab_tree,
    4,
    "Color-group column (optional): color the nodes by this column's category, to group them\n"
    "visually (e.g. by generation, department, or type).",
)

tree_color_label = GUI_theme_util.create_label(
    _tr4, text="Color-group column (optional):"
)
tree_color_label.pack(side="left", padx=(0, 8))
tree_color_var = tk.StringVar()
tree_color_menu = GUI_theme_util.create_combobox(
    _tr4, textvariable=tree_color_var, width=25, state="readonly"
)
tree_color_menu.pack(side="left")


# ── changed_filename (populates all menus across all tabs) ────────────────────


def changed_filename(tracedInputFile):
    global error
    if tracedInputFile.endswith(".csv"):
        error = False
    else:
        error = True

    menu_values_local = []
    if tracedInputFile != "" and os.path.basename(tracedInputFile)[-4:] == ".csv":
        nRecords, nColumns = IO_csv_util.GetNumberOf_Records_Columns_inCSVFile(
            tracedInputFile
        )
        if nColumns == 0 or nColumns == None:
            return False
        if IO_csv_util.csvFile_has_header(tracedInputFile) == False:
            menu_values_local = list(range(1, nColumns + 1))
        else:
            data, headers = IO_csv_util.get_csv_data(tracedInputFile, True)
            menu_values_local = headers

        # Initialize csv_files_list for comparative bar charts
        if tracedInputFile not in csv_files_list:
            csv_files_list.clear()
            csv_files_list.append(tracedInputFile)
            process_csv_file_menu_comparative(tracedInputFile)
    else:
        menu_values_local = []

    # CTk repopulation: every dropdown was refilled via the tk `widget["menu"]` mutation, which is a
    # silent no-op on a CTkOptionMenu (§6). set_values() is the CTk replacement; the per-item command
    # lambdas are gone because CTkOptionMenu writes the picked string straight to its bound variable.
    mv = [str(s) for s in menu_values_local]

    # Relational tab menus
    GUI_theme_util.set_values(csv_field_relational_menu, mv)
    GUI_theme_util.set_values(dynamic_network_field_menu, mv)

    # Categorical tab menus
    GUI_theme_util.set_values(csv_field_categorical_menu, mv)

    # Temporal tab menus
    GUI_theme_util.set_values(time_mapper_field_menu, mv)
    GUI_theme_util.set_values(csv_field_temporal_menu, mv)
    GUI_theme_util.set_values(timeline_Y_axis_menu, mv)
    GUI_theme_util.set_values(timeline_date_menu, mv)

    # Numeric tab menus
    GUI_theme_util.set_values(csv_field_visualization_menu, mv)
    GUI_theme_util.set_values(X_axis_menu, mv)
    GUI_theme_util.set_values(Y_axis_menu, mv)
    GUI_theme_util.set_values(csv_field_boxplot_menu, mv)
    GUI_theme_util.set_values(csv_field_boxplot_color_menu, mv)
    GUI_theme_util.set_values(X_axis_bubble_menu, mv)
    GUI_theme_util.set_values(histogram_category_menu, [""] + mv)
    GUI_theme_util.set_values(violin_category_menu, [""] + mv)

    # Calendar heatmap menus (Temporal tab)
    GUI_theme_util.set_values(calendar_date_menu, mv)
    GUI_theme_util.set_values(calendar_value_menu, [""] + mv)

    # Hierarchical tree tab menus (Comboboxes)
    tree_vals = [""] + mv
    GUI_theme_util.set_values(tree_parent_menu, tree_vals)
    GUI_theme_util.set_values(tree_child_menu, tree_vals)
    GUI_theme_util.set_values(tree_label_menu, tree_vals)
    GUI_theme_util.set_values(tree_info_menu, tree_vals)
    GUI_theme_util.set_values(tree_color_menu, tree_vals)

    # Migration map tab menus (Comboboxes)
    mig_vals = [""] + mv
    GUI_theme_util.set_values(mig_entity_menu, mig_vals)
    GUI_theme_util.set_values(mig_location_menu, mig_vals)
    GUI_theme_util.set_values(mig_date_menu, mig_vals)
    GUI_theme_util.set_values(mig_lat_menu, mig_vals)
    GUI_theme_util.set_values(mig_lon_menu, mig_vals)

    clear("<Escape>")


def on_inputFilename_change(*args):
    f = GUI_util.inputFilename.get()
    if f.endswith(".csv"):
        input_csv_file_var.set(f)
    changed_filename(f)


GUI_util.inputFilename.trace("w", lambda x, y, z: on_inputFilename_change())


# ── activate_all_options ──────────────────────────────────────────────────────


def activate_all_options(*args):
    if error:
        return

    extra_GUIs_menu.configure(state="disabled")

    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state="normal")

    # Relational tab state based on relations_menu_var
    current_rel = relations_menu_var.get()
    dynamic_network_field_menu.configure(state="disabled")
    Sankey_limit1_menu.configure(state="disabled")
    Sankey_limit2_menu.configure(state="disabled")
    Sankey_limit3_menu.configure(state="disabled")

    if current_rel == "*":
        dynamic_network_field_menu.configure(state="normal")
        Sankey_limit1_menu.configure(state="normal")
        Sankey_limit2_menu.configure(state="normal")
        Sankey_limit3_menu.configure(state="normal")
        try:
            GephiDir, _, errorFound = IO_libraries_util.external_software_install(
                "Gephi_util", "Gephi", "", silent=True, errorFound=False
            )
            if GephiDir is None or GephiDir == "":
                mb.showwarning(
                    "Warning",
                    "Gephi is not installed on this machine.\n\nThe '*' option will run Network graph (vis.js) and Sankey but will skip Gephi.\n\nYou can install Gephi from the Setup menu.",
                )
        except Exception:
            mb.showwarning(
                "Warning",
                "Gephi is not installed on this machine.\n\nThe '*' option will run Network graph (vis.js) and Sankey but will skip Gephi.\n\nYou can install Gephi from the Setup menu.",
            )
    elif current_rel == "Gephi" or current_rel == "Network graph (vis.js)":
        dynamic_network_field_menu.configure(state="normal")
    elif current_rel == "Sankey":
        Sankey_limit1_menu.configure(state="normal")
        Sankey_limit2_menu.configure(state="normal")
        Sankey_limit3_menu.configure(state="normal")

    # Categorical tab state
    cat_sel = categorical_menu_var.get()
    is_all = "*" in cat_sel
    is_colormap = "Colormap" in cat_sel
    is_comparative = "Comparative" in cat_sel
    is_sunburst_treemap = "Sunburst" in cat_sel or "Treemap" in cat_sel

    # Search field row — needed for all except Colormap (which uses its own row)
    search_state = "normal" if (not is_colormap or is_all) else "disabled"
    csv_field_categorical_menu.configure(state=search_state)
    case_sensitive_checkbox.configure(state=search_state)
    search_values_categorical.configure(state=search_state)
    add_button_categorical.configure(state=search_state)
    reset_button_categorical.configure(state=search_state)
    show_button_categorical.configure(state=search_state)

    # Filtering row — only for Sunburst/Treemap/*
    filter_state = "normal" if (is_sunburst_treemap or is_all) else "disabled"
    filter_options_menu.configure(state=filter_state)
    if filter_state == "disabled":
        fixed_param.configure(state="disabled")
        rate_param.configure(state="disabled")
        base_param.configure(state="disabled")
    else:
        activate_filtering_options()

    # Colormap row
    colormap_state = "normal" if (is_colormap or is_all) else "disabled"
    max_rows.configure(state=colormap_state)
    color_1_checkbox.configure(state=colormap_state)
    color_2_checkbox.configure(state=colormap_state)
    data_transformation_menu.configure(state=colormap_state)

    # Comparative row
    comp_state = "normal" if (is_comparative or is_all) else "disabled"
    add_file.configure(state=comp_state)
    reset_file_button.configure(state=comp_state)
    openInputFile_button_comparative.configure(state=comp_state)
    csv_file_menu_comparative.configure(state=comp_state)

    # Temporal tab state
    is_time_mapper = "Time mapper" in temporal_menu_var.get()
    is_timeline_plot = "Timeline" in temporal_menu_var.get()
    is_calendar = "Calendar" in temporal_menu_var.get()

    csv_field_temporal_menu.configure(state="normal" if is_time_mapper else "disabled")
    time_mapper_field_menu.configure(state="normal" if is_time_mapper else "disabled")
    date_format_menu.configure(
        state="normal" if (is_time_mapper or is_calendar) else "disabled"
    )
    select_time_menu.configure(state="normal" if is_time_mapper else "disabled")
    cumulative_checkbox.configure(state="normal" if is_time_mapper else "disabled")

    timeline_Y_axis_menu.configure(state="normal" if is_timeline_plot else "disabled")
    timeline_date_menu.configure(state="normal" if is_timeline_plot else "disabled")

    calendar_date_menu.configure(state="normal" if is_calendar else "disabled")
    calendar_value_menu.configure(state="normal" if is_calendar else "disabled")

    # Numeric tab state — disable all, then enable per selection
    num_sel = visualizations_menu_var.get().lower()

    X_axis_menu.configure(state="disabled")
    Y_axis_menu.configure(state="disabled")
    add_Y_axis.configure(state="disabled")
    reset_Y_axis_button.configure(state="disabled")
    show_Y_axis_button.configure(state="disabled")
    points_menu.configure(state="disabled")
    split_data_byCategory_checkbox.configure(state="disabled")
    csv_field_boxplot_menu.configure(state="disabled")
    csv_field_boxplot_color_menu.configure(state="disabled")
    X_axis_bubble_menu.configure(state="disabled")
    histogram_nbins_entry.configure(state="disabled")
    histogram_category_menu.configure(state="disabled")
    histogram_marginal_menu.configure(state="disabled")
    violin_points_menu.configure(state="disabled")
    violin_category_menu.configure(state="disabled")

    if "plotly" in num_sel:
        X_axis_menu.configure(state="normal")
        Y_axis_menu.configure(state="normal")
        add_Y_axis.configure(state="normal")
        reset_Y_axis_button.configure(state="normal")
        show_Y_axis_button.configure(state="normal")
    if "boxplot" in num_sel:
        points_menu.configure(state="normal")
        split_data_byCategory_checkbox.configure(state="normal")
        csv_field_boxplot_menu.configure(state="normal")
        csv_field_boxplot_color_menu.configure(state="normal")
    if "bubble" in num_sel:
        X_axis_bubble_menu.configure(state="normal")
    if "histogram" in num_sel:
        histogram_nbins_entry.configure(state="normal")
        histogram_category_menu.configure(state="normal")
        histogram_marginal_menu.configure(state="normal")
    if "violin" in num_sel:
        violin_points_menu.configure(state="normal")
        violin_category_menu.configure(state="normal")


activate_all_options()

relations_menu_var.trace("w", activate_all_options)
visualizations_menu_var.trace("w", activate_all_options)
categorical_menu_var.trace("w", activate_all_options)
temporal_menu_var.trace("w", activate_all_options)


# ── Run command (tab-aware) ───────────────────────────────────────────────────


def run_command():
    # CTkTabview reports the selected tab by NAME (.get()); map back to the integer index the
    # dispatch below was written against (was notebook.index(notebook.select()) on the ttk.Notebook).
    active_tab = _TAB_INDEX[notebook.get()]
    inputFile = (
        input_csv_file_var.get()
        if input_csv_file_var.get()
        else GUI_util.inputFilename.get()
    )
    outputDir = GUI_util.output_dir_path.get()
    openOutputFiles = GUI_util.open_csv_output_checkbox.get()

    if active_tab == 0:  # Relational
        run_relational(
            inputFile,
            outputDir,
            openOutputFiles,
            relations_menu_var.get(),
            csv_field_relational_var.get(),
            csv_file_relational_field_list,
            dynamic_network_field_var.get(),
            Sankey_limit1_var.get(),
            Sankey_limit2_var.get(),
            Sankey_limit3_var.get(),
        )
    elif active_tab == 1:  # Categorical
        run_categorical(
            inputFile,
            outputDir,
            openOutputFiles,
            categorical_menu_var.get(),
            csv_field_categorical_var.get(),
            case_sensitive_var.get(),
            csv_file_categorical_field_list,
            filter_options_var.get(),
            fixed_param_var.get(),
            rate_param_var.get(),
            base_param_var.get(),
            max_rows_var.get(),
            color_1_style_var.get(),
            color_2_style_var.get(),
            data_transformation_var.get(),
            csv_files_list,
            csv_field_visualization_var.get(),
        )
    elif active_tab == 2:  # Temporal
        run_temporal(
            inputFile,
            outputDir,
            openOutputFiles,
            temporal_menu_var.get(),
            csv_field_relational_var.get(),
            time_mapper_field_var.get(),
            date_format_var.get(),
            time_var.get(),
            cumulative_var.get(),
            timeline_Y_axis_var.get(),
            timeline_date_var.get(),
            calendar_date_var.get(),
            calendar_value_var.get(),
        )
    elif active_tab == 3:  # Numeric
        run_numeric(
            inputFile,
            outputDir,
            openOutputFiles,
            visualizations_menu_var.get(),
            csv_field_visualization_var.get(),
            X_axis_var.get(),
            csv_file_field_Y_axis_list,
            points_var.get(),
            split_data_byCategory_var.get(),
            csv_field_boxplot_var.get(),
            csv_field_boxplot_color_var.get(),
            X_axis_bubble_var.get(),
            color_1_style_var.get(),
            histogram_nbins_var.get(),
            histogram_category_var.get(),
            histogram_marginal_var.get(),
            violin_points_var.get(),
            violin_category_var.get(),
        )
    elif active_tab == 4:  # Geographic
        if mig_entity_var.get() and mig_location_var.get():
            outputFiles = charts_util.animated_migration_map(
                inputFile,
                outputDir,
                mig_entity_var.get(),
                mig_location_var.get(),
                date_col=mig_date_var.get() or None,
                lat_col=mig_lat_var.get() or None,
                lon_col=mig_lon_var.get() or None,
            )
            if outputFiles:
                filesToOpen = (
                    outputFiles if isinstance(outputFiles, list) else [outputFiles]
                )
                if openOutputFiles:
                    IO_files_util.OpenOutputFiles(
                        GUI_util.window, openOutputFiles, filesToOpen, outputDir
                    )
        else:
            run_script_util.run_script("GIS_main.py")
    elif active_tab == 5:  # Wordclouds
        run_script_util.run_script("wordclouds_main.py")
    elif active_tab == 6:  # Hierarchical tree
        if not tree_parent_var.get() or not tree_child_var.get():
            mb.showwarning(
                "Warning",
                "Please select at least the Parent and Child columns for the hierarchical tree.",
            )
            return
        outputFiles = charts_util.hierarchical_tree(
            inputFile,
            outputDir,
            tree_parent_var.get(),
            tree_child_var.get(),
            label_col=tree_label_var.get() or None,
            info_col=tree_info_var.get() or None,
            color_col=tree_color_var.get() or None,
        )
        if outputFiles:
            filesToOpen = (
                outputFiles if isinstance(outputFiles, list) else [outputFiles]
            )
            if openOutputFiles:
                IO_files_util.OpenOutputFiles(
                    GUI_util.window, openOutputFiles, filesToOpen, outputDir
                )


GUI_util.run_button.configure(command=run_command)


# ── Clear ─────────────────────────────────────────────────────────────────────


def clear(e):
    extra_GUIs_var.set(0)
    extra_GUIs_menu_var.set("")
    input_csv_file_var.set("")
    relations_menu_var.set("Gephi")
    categorical_menu_var.set("Sunburst")
    csv_field_relational_var.set("")
    dynamic_network_field_var.set("")
    selected_csv_file_fields.set("")
    selected_csv_file_fields_var.set("")
    csv_file_relational_field_list.clear()
    csv_field_categorical_var.set("")
    search_values_categorical_var.set("")
    csv_file_categorical_field_list.clear()
    case_sensitive_var.set(1)
    fixed_param_var.set(15)
    rate_param_var.set(3)
    base_param_var.set(15)
    temporal_menu_var.set("Time mapper")
    time_mapper_field_var.set("")
    date_format_var.set("mm-dd-yyyy")
    time_var.set("Daily")
    cumulative_var.set(0)
    timeline_Y_axis_var.set("")
    timeline_date_var.set("")
    visualizations_menu_var.set("Excel/Plotly charts")
    X_axis_var.set("")
    Y_axis_var.set("")
    csv_field_visualization_var.set("")
    csv_field_boxplot_var.set("")
    points_var.set("")
    split_data_byCategory_var.set(0)
    csv_field_boxplot_color_var.set("")
    csv_files_list.clear()
    csv_file_field_Y_axis_list.clear()
    activate_filtering_options()
    activate_all_options()
    GUI_util.clear("Escape")


window.bind("<Escape>", clear)


# ── TIPS, Videos, Help ────────────────────────────────────────────────────────

videos_lookup = {"Data visualization": "https://youtu.be/EDKdurWa56g"}
videos_options = "Data visualization"

TIPS_lookup = {
    "Network Graphs (via Gephi)": "TIPS_NLP_Gephi network graphs.pdf",
    "Network graph (vis.js)": "TIPS_NLP_Gephi network graphs.pdf",
    "Sankey chart": "TIPS_NLP_Charts - Sankey chart.pdf",
    "Stacked bar chart": "TIPS_NLP_Charts - Multiple bar charts.pdf",
    "Sunburst pie chart": "TIPS_NLP_Charts - Sunburst pie chart.pdf",
    "Colormap/heatmap chart": "TIPS_NLP_Charts - Colormap-heatmap.pdf",
    "Treemap chart": "TIPS_NLP_Charts - Treemap chart.pdf",
    "Boxplots": "TIPS_NLP_Charts - Boxplots.pdf",
    "Bubble chart": "TIPS_NLP_Charts - Bubble chart.pdf",
    "Multiple bar charts": "TIPS_NLP_Charts - Multiple bar charts.pdf",
    "Time mapper": "TIPS_NLP_Charts - Time mapper.pdf",
    "Word clouds": "TIPS_NLP_Wordclouds Visualizing word clouds.pdf",
    "Excel charts": "TIPS_NLP_Excel Charts.pdf",
    "csv files - Problems & solutions": "TIPS_NLP_csv files - Problems & solutions.pdf",
    "Statistical measures": "TIPS_NLP_Statistical measures.pdf",
}

TIPS_options = (
    "Network Graphs (via Gephi)",
    "Network graph (vis.js)",
    "Sankey chart",
    "Stacked bar chart",
    "Sunburst pie chart",
    "Colormap/heatmap chart",
    "Treemap chart",
    "Boxplots",
    "Bubble chart",
    "Multiple bar charts",
    "Time mapper",
    "Word clouds",
    "Excel charts",
    "csv files - Problems & solutions",
    "Statistical measures",
)


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window,
            help_button_x_coordinate,
            y_multiplier_integer,
            "NLP Suite Help",
            GUI_IO_util.msg_CoNLL,
        )
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window,
            help_button_x_coordinate,
            y_multiplier_integer,
            "NLP Suite Help",
            GUI_IO_util.msg_corpusData,
        )
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window,
            help_button_x_coordinate,
            y_multiplier_integer,
            "NLP Suite Help",
            GUI_IO_util.msg_outputDirectory,
        )
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(
            window,
            help_button_x_coordinate,
            y_multiplier_integer,
            "NLP Suite Help",
            GUI_IO_util.msg_IO_setup,
        )

    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Please, tick the 'GUIs available' checkbox if you wish to see and select the range of other available tools suitable for data visualization.",
    )
    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Please, click the 'Select INPUT CSV file' button to select a csv file to visualize.\n\nThe csv file headers will be used to populate the dropdown menus for selecting the fields to be used for visualization.",
    )
    # One help button at the top of the notebook area, then skip the rest
    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        "Select a tab to choose the type of visualization you wish to produce.\n\n"
        "RELATIONAL tab: Network graphs (Gephi, vis.js) and Sankey charts to visualize relationships between entities (e.g., Subject-Verb-Object).\n\n"
        "CATEGORICAL tab: Colormap/heatmap, Comparative bar charts, Grouped bar, Stacked bar, Sunburst, Treemap, and Waffle charts to visualize categorical data.\n\n"
        "TEMPORAL tab: Time mapper, Calendar heatmap, and Timeline plot to visualize temporal data.\n\n"
        "NUMERIC tab: Excel/Plotly charts, Boxplots, Bubble charts, Correlation heatmap, Histogram, and Violin plot to visualize numeric/statistical data.\n\n"
        "GEOGRAPHIC tab: Open the GIS GUI to map locations, or build an animated movement map showing how entities move across locations over time.\n\n"
        "WORDCLOUDS tab: Open the Wordclouds GUI to generate word clouds from text or CSV data.\n\n"
        "HIERARCHICAL TREE tab: Build an interactive tree from parent-child CSV data (genealogy, grammar hierarchies, org charts).",
    )
    y_multiplier_integer += 6
    y_multiplier_integer = GUI_IO_util.place_help_button(
        window,
        help_button_x_coordinate,
        y_multiplier_integer,
        "NLP Suite Help",
        GUI_IO_util.msg_openOutputFiles,
    )
    return y_multiplier_integer - 1


y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

readMe_message = "The Python 3 script provides access to different types of data visualization: network graphs (Gephi, vis.js), Sankey charts, sunburst, treemap, colormap/heatmap, stacked bar charts, time mapper, boxplots, bubble charts, comparative bar charts, and Excel/Plotly charts.\n\nIn INPUT the algorithms expect a csv file.\n\nIn OUTPUT the algorithms produce different types of interactive html charts."
readMe_command = lambda: GUI_IO_util.display_help_button_info(
    "NLP Suite Help", readMe_message
)
GUI_util.GUI_bottom(
    config_filename,
    config_input_output_numeric_options,
    y_multiplier_integer,
    readMe_command,
    videos_lookup,
    videos_options,
    TIPS_lookup,
    TIPS_options,
    IO_setup_display_brief,
    scriptName,
)

activate_all_options()

GUI_util.window.mainloop()
