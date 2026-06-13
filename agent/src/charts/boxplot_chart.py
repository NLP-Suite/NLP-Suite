# written by Roberto April 2023


import charts_util
import IO_files_util


def run(
    inputFilename,
    outputDir,
    csv_field_visualization_var,
    points_var,
    split_data_byCategory_var,
    csv_field_boxplot_var,
    csv_field_boxplot_color_var,
    # TODO:
    inputFileData,
):
    """Render a boxplot from a numeric csv field."""
    filesToOpen = []

    # if extra_GUIs_var.get()==False and csv_field_visualization_var == '':

    # if extra_GUIs_var.get()==False and visualizations_menu_var=='':

    # if csv_field_visualization_var=='':

    # boxplots --------------------------------------------------------------------------------

    if points_var == "":
        return

    if split_data_byCategory_var and csv_field_boxplot_var == "":
        # mb.showwarning(title='Warning',
        # message='The "Split data by category" Boxplots option requires a second CATEGORICAL csv file field for processing.\n\nPlease, use the dropdown menu to select the csv file field and try again.')
        return

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, "", outputDir, ".html", "boxplot")
    # You cannot keep it as float inside the csv. The csv will treat everything as strings.
    # https://stackoverflow.com/questions/65393774/writing-floats-into-a-csv-file-but-floats-become-a-string
    outputfilename = charts_util.boxplot(
        inputFileData,
        outputFilename,
        csv_field_visualization_var,
        points_var,
        split_data_byCategory_var,
        csv_field_boxplot_var,
        csv_field_boxplot_color_var,
    )  # , points_var, color=None)
    if outputfilename != "":
        filesToOpen.append(outputfilename)
