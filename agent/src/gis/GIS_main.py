import logging

# FLAGGED
# Written by Roberto Franzosi May, September 2020
# Written by Roberto Franzosi September 2021
import pandas as pd

# Ignore error coming from df['Date'][index] = saved_date
pd.options.mode.chained_assignment = None


import config_util  # used for Google API
import GIS_pipeline_util
import IO_files_util
import Stanford_CoreNLP_util

logger = logging.getLogger(__name__)

# RUN section ______________________________________________________________________________________________________________________________________________________


def run_GIS(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    csv_file,
    NER_extractor,
    location_menu,
    geocoder,
    geocode_locations,
    country_bias_var,
    area_var,
    restrict_var,
    map_locations,
    GIS_package_var,
    GIS_package2_var,
):
    """Geocode locations found in the corpus and produce interactive maps."""
    config_filename = "NLP_default_IO_config.csv"

    filesToOpen = []
    locationColumnName = ""

    # get the NLP package and language options
    (
        error,
        package,
        parsers,
        package_basics,
        language,
        package_display_area_value,
        encoding_var,
        export_json_var,
        memory_var,
        document_length_var,
        limit_sentence_length_var,
    ) = config_util.read_NLP_package_language_config()
    language_var = language
    if package_display_area_value == "":
        logger.info(
            "No setup for NLP package and language, The default NLP package and language has not been setup.\n\nPlease, click on the Setup NLP button and try again."
        )
        return

    # get the date options from filename
    config_input_output_numeric_options = [1, 0, 0, 1]
    (
        filename_embeds_date_var,
        date_format_var,
        items_separator_var,
        date_position_var,
        config_file_exists,
    ) = config_util.get_date_options(config_filename, config_input_output_numeric_options)
    extract_date_from_text_var = 0

    # get last two characters for ISO country code
    country_bias = country_bias_var[-2:]

    box_tuple = ""
    if "e.g.," not in area_var:
        if (area_var.count("(") + area_var.count(")") != 4) or (area_var.count(",") != 3):
            logger.info(
                "Warning, The area variable is not set correctly. The expected value should be something like this: (34.98527, -85.59790), (30.770444, -81.521974)\n\nThe two sets of values refer to the upper left-hand and lower right-hand corner latitude and longitude coordinates of the area to wich you wish to restrict geocoding.\n\nPlease, enter the correct value and try again."
            )
            area_var.set("(34.98527, -85.59790), (30.770444, -81.521974)")
            return
        box_tuple = area_var

    geocode_locations_var = True
    if not NER_extractor and not geocode_locations_var and GIS_package_var == "":
        logger.info("Warning, no options have been selected.\n\nPlease, select an option to run and try again.")
        return

    if csv_file != "":
        result = (
            "GIS pipeline input file This is a reminder that you are running the GIS pipeline with the csv input file\n\n"
            + csv_file
            + "\n\nand the GIS package "
            + GIS_package_var
            + "\n\nPress Cancel then Esc to clear the csv file widget if you want to run the GIS pipeline from your input txt file(s) (you can select a different mapping software using the dropdown menu) and try again."
        )
        logger.info(result)
        if not result:
            return
        inputFilename = csv_file

    geoName = "geo-" + str(geocoder[:3])
    if geocode_locations_var:
        IO_files_util.generate_output_file_name(
            inputFilename,
            inputDir,
            outputDir,
            ".csv",
            "GIS",
            geoName,
            locationColumnName,
            "",
            "",
            False,
            True,
        )
        IO_files_util.generate_output_file_name(
            inputFilename,
            inputDir,
            outputDir,
            ".csv",
            "GIS",
            geoName,
            "Not-Found",
            locationColumnName,
            "",
            False,
            True,
        )

        locationFiles = []

    # START PROCESSING ---------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # NER extraction via CoreNLP

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir, label="GIS", silent=True)
    if outputDir == "":
        return

    # checking for txt: NER=='LOCATION', provide a csv output with column: [Locations]
    if NER_extractor and csv_file == "":
        NERs = ["COUNTRY", "STATE_OR_PROVINCE", "CITY", "LOCATION"]

        locationFiles = Stanford_CoreNLP_util.CoreNLP_annotate(
            config_filename,
            inputFilename,
            inputDir,
            outputDir,
            openOutputFiles,
            chartPackage,
            dataTransformation,
            "NER",
            False,
            language_var,
            export_json_var,
            memory_var,
            NERs=NERs,
            extract_date_from_text_var=0,
            filename_embeds_date_var=filename_embeds_date_var,
            date_format=date_format_var,
            items_separator_var=items_separator_var,
            date_position_var=date_position_var,
        )

        if len(locationFiles) == 0:
            logger.info(
                "No locations There are no NER locations to be geocoded and mapped in the selected input txt file.\n\nPlease, select a different txt file and try again."
            )
            return
        else:
            filesToOpen.extend(locationFiles)
            NER_outputFilename = locationFiles[0]

        # If Column A is 'Word' (coming from CoreNLP NER annotator), rename to 'Location'
        # if IO_csv_util.rename_header(inputFilename, "Word", "Location") == False:
        df = pd.read_csv(locationFiles[0], encoding="utf-8", on_bad_lines="skip").rename(columns={"Word": "Location"})

        # Clean dataframe, remove any 'DATE' or non-location rows
        del_list = []
        for index, _row in df.iterrows():
            if df["NER"][index] not in [
                "COUNTRY",
                "STATE_OR_PROVINCE",
                "CITY",
                "LOCATION",
            ]:
                del_list.append(index)
        df = df.drop(del_list)
        df.to_csv(NER_outputFilename, encoding="utf-8", index=False)
        filesToOpen.append(NER_outputFilename)
        locationColumnName = "Location"

    else:
        NER_outputFilename = "NER_StanfordCoreNLP_output"
        locationColumnName = location_menu  # RF

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # running the GIS options
    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    if (
        "folium" in GIS_package_var
        or GIS_package_var == "Google Earth Pro & Google Maps"
        or GIS_package_var == "Google Maps"
        or GIS_package_var == "Google Earth Pro"
    ):
        # if GIS_package_var=='Google Earth Pro': # check installation
        # locationColumnName where locations to be geocoded (or geocoded) are stored in the csv file;
        #   any changes to the columns will result in error
        # outputFiles includes both kml file and Google Earth files
        outputFiles = GIS_pipeline_util.GIS_pipeline(
            config_filename,
            NER_outputFilename,
            inputDir,
            outputDir,
            geocoder,
            GIS_package_var,
            chartPackage,
            dataTransformation,
            extract_date_from_text_var,
            country_bias,
            box_tuple,
            restrict_var,
            locationColumnName,
            encoding_var,
            0,
            1,
            [""],
            [""],  # group_var, group_number_var, group_values_entry_var_list, group_label_entry_var_list,
            ["Pushpins"],
            ["red"],  # icon_var_list, specific_icon_var_list,
            [0],
            ["1"],
            [0],
            [""],  # name_var_list, scale_var_list, color_var_list, color_style_var_list,
            [1],
            [1],
        )  # bold_var_list, italic_var_list)

        if outputFiles is not None:
            if len(outputFiles) > 0:
                filesToOpen.extend(outputFiles)

        if len(filesToOpen) > 0:
            return filesToOpen
    else:
        if GIS_package_var != "":
            logger.info(
                "Option not available The "
                + GIS_package_var
                + "option is not available yet.\n\nSorry! Please, check back soon..."
            )
            return
