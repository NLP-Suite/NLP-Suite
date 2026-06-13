import logging
import os
import sys

import IO_csv_util
import pandas as pd
import simplekml

logger = logging.getLogger(__name__)

# Icon URLs from http://kml4earth.appspot.com/icons.html#pushpin
_TRACK = "http://earth.google.com/images/kml-icons/track-directional/track-"
_PADDLE = "http://maps.google.com/mapfiles/kml/paddle/"
_PUSH = "http://maps.google.com/mapfiles/kml/pushpin/"
_SHAPE = "http://maps.google.com/mapfiles/kml/shapes/"

_ICON_URLS: dict[str, dict[str, str]] = {
    "Directions": {
        "none": f"{_TRACK}none.png",
        **{"North (track 0)": f"{_TRACK}0.png"},
        **{f"Northeast (track {i})": f"{_TRACK}{i}.png" for i in range(1, 4)},
        **{"East (track 4)": f"{_TRACK}4.png"},
        **{f"Southeast (track {i})": f"{_TRACK}{i}.png" for i in range(5, 8)},
        **{"South (track 8)": f"{_TRACK}8.png"},
        **{f"Southwest (track {i})": f"{_TRACK}{i}.png" for i in range(9, 12)},
        **{"West (track 12)": f"{_TRACK}12.png"},
        **{f"Northwest (track {i})": f"{_TRACK}{i}.png" for i in range(13, 16)},
    },
    "Paddles (teardrop)": {
        **{str(i): f"{_PADDLE}{i}.png" for i in range(1, 11)},
        **{c: f"{_PADDLE}{c}.png" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
        "go-sign(green)": f"{_PADDLE}go.png",
        "pause-sign(yellow)": f"{_PADDLE}pause.png",
        "stop-sign(red)": f"{_PADDLE}stop.png",
        "blue-blank": f"{_PADDLE}blu-blank.png",
        "blue-circle": f"{_PADDLE}blu-circle.png",
        "blue-diamond": f"{_PADDLE}blu-diamond.png",
        "blue-square": f"{_PADDLE}blu-square.png",
        "blue-stars": f"{_PADDLE}blu-stars.png",
        "green-blank": f"{_PADDLE}grn-blank.png",
        "green-circle": f"{_PADDLE}grn-circle.png",
        "green-diamond": f"{_PADDLE}grn-diamond.png",
        "green-square": f"{_PADDLE}grn-square.png",
        "green-stars": f"{_PADDLE}grn-stars.png",
        "light-blue-blank": f"{_PADDLE}ltblu-blank.png",
        "light-blue-circle": f"{_PADDLE}ltblu-circle.png",
        "light-blue-diamond": f"{_PADDLE}ltblu-diamond.png",
        "light-blue-square": f"{_PADDLE}ltblu-square.png",
        "light-blue-stars": f"{_PADDLE}ltblu-stars.png",
        "pink-blank": f"{_PADDLE}pink-blank.png",
        "pink-circle": f"{_PADDLE}pink-circle.png",
        "pink-diamond": f"{_PADDLE}pink-diamond.png",
        "pink-square": f"{_PADDLE}pink-square.png",
        "pink-stars": f"{_PADDLE}pink-stars.png",
        "purple-blank": f"{_PADDLE}purple-blank.png",
        "purple-circle": f"{_PADDLE}purple-circle.png",
        "purple-diamond": f"{_PADDLE}purple-diamond.png",
        "purple-square": f"{_PADDLE}purple-square.png",
        "purple-stars": f"{_PADDLE}purple-stars.png",
        "red-circle": f"{_PADDLE}red-circle.png",
        "red-diamond": f"{_PADDLE}red-diamond.png",
        "red-square": f"{_PADDLE}red-square.png",
        "red-stars": f"{_PADDLE}red-stars.png",
        "white-blank": f"{_PADDLE}wht-blank.png",
        "white-circle": f"{_PADDLE}wht-circle.png",
        "white-diamond": f"{_PADDLE}wht-diamond.png",
        "white-square": f"{_PADDLE}wht-square.png",
        "white-stars": f"{_PADDLE}wht-stars.png",
        "yellow-blank": f"{_PADDLE}ylw-blank.png",
        "yellow-circle": f"{_PADDLE}ylw-circle.png",
        "yellow-diamond": f"{_PADDLE}ylw-diamond.png",
        "yellow-square": f"{_PADDLE}ylw-square.png",
        "yellow-stars": f"{_PADDLE}ylw-stars.png",
        "orange-blank": f"{_PADDLE}orange-blank.png",
        "orange-circle": f"{_PADDLE}orange-circle.png",
        "orange-diamond": f"{_PADDLE}orange-diamond.png",
        "orange-square": f"{_PADDLE}orange-square.png",
        "orange-stars": f"{_PADDLE}orange-stars.png",
    },
    "Paddles (square)": {
        **{str(i): f"{_PADDLE}{i}-lv.png" for i in range(1, 11)},
        "go-sign(green)": f"{_PADDLE}go-lv.png",
        "pause-sign(yellow)": f"{_PADDLE}pause-lv.png",
        "stop-sign(red)": f"{_PADDLE}stop-lv.png",
        "blue-blank": f"{_PADDLE}blu-blank-lv.png",
        "blue-circle": f"{_PADDLE}blu-circle-lv.png",
        "blue-diamond": f"{_PADDLE}blu-diamond-lv.png",
        "blue-square": f"{_PADDLE}blu-square-lv.png",
        "blue-stars": f"{_PADDLE}blu-stars-lv.png",
        "green-blank": f"{_PADDLE}grn-blank-lv.png",
        "green-circle": f"{_PADDLE}grn-circle-lv.png",
        "green-diamond": f"{_PADDLE}grn-diamond-lv.png",
        "green-square": f"{_PADDLE}grn-square-lv.png",
        "green-stars": f"{_PADDLE}grn-stars-lv.png",
        "purple-blank": f"{_PADDLE}purple-blankv.png",
        "purple-circle": f"{_PADDLE}purple-circle-lv.png",
        "purple-diamond": f"{_PADDLE}purple-diamond-lv.png",
        "purple-square": f"{_PADDLE}purple-square-lv.png",
        "purple-stars": f"{_PADDLE}purple-stars-lv.png",
        "red-circle": f"{_PADDLE}red-circle-lv.png",
        "red-diamond": f"{_PADDLE}red-diamond-lv.png",
        "red-square": f"{_PADDLE}red-square-lv.png",
        "red-stars": f"{_PADDLE}red-stars-lv.png",
        "white-blank": f"{_PADDLE}wht-blank-lv.png",
        "white-circle": f"{_PADDLE}wht-circle-lv.png",
        "white-diamond": f"{_PADDLE}wht-diamond-lv.png",
        "white-square": f"{_PADDLE}wht-square-lv.png",
        "white-stars": f"{_PADDLE}wht-stars-lv.png",
        "yellow-blank": f"{_PADDLE}ylw-blank-lv.png",
        "yellow-circle": f"{_PADDLE}ylw-circle-lv.png",
        "yellow-diamond": f"{_PADDLE}ylw-diamond-lv.png",
        "yellow-square": f"{_PADDLE}ylw-square-lv.png",
        "yellow-stars": f"{_PADDLE}ylw-stars-lv.png",
    },
    "Pushpins": {
        "blue": f"{_PUSH}blue-pushpin.png",
        "green": f"{_PUSH}grn-pushpin.png",
        "light_blue": f"{_PUSH}ltblu-pushpin.png",
        "pink": f"{_PUSH}pink-pushpin.png",
        "purple": f"{_PUSH}purple-pushpin.png",
        "red": f"{_PUSH}red-pushpin.png",
        "white": f"{_PUSH}wht-pushpin.png",
        "yellow": f"{_PUSH}ylw-pushpin.png",
    },
    "Shapes": {
        s: f"{_SHAPE}{s}.png"
        for s in [
            "airports",
            "arrow-reverse",
            "arrow",
            "arts",
            "bars",
            "broken_link",
            "bus",
            "camera",
            "campfire",
            "campground",
            "capital_big",
            "capital_big_highlight",
            "capital_small",
            "capital_small_highlight",
            "caution",
            "church",
            "coffee",
            "convenience",
            "cross-hairs",
            "cross-hairs_highlight",
            "cycling",
            "dining",
            "dollar",
            "donut",
            "earthquake",
            "electronics",
            "euro",
            "falling_rocks",
            "ferry",
            "firedept",
            "fishing",
            "flag",
            "forbidden",
            "gas_stations",
            "golf",
            "grocery",
            "heliport",
            "highway",
            "hiker",
            "homegardenbusiness",
            "horsebackriding",
            "hospitals",
            "info-i",
            "info",
            "info_circle",
            "lodging",
            "man",
            "marina",
            "mechanic",
            "motorcycling",
            "mountains",
            "movies",
            "open-diamond",
            "parking_lot",
            "parks",
            "pharmacy_rx",
            "phone",
            "picnic",
            "placemark_circle",
            "placemark_circle_highlight",
            "placemark_square",
            "placemark_square_highlight",
            "play",
            "poi",
            "police",
            "polygon",
            "post_office",
            "rail",
            "ranger_station",
            "realestate",
            "road_shield1",
            "road_shield2",
            "road_shield3",
            "ruler",
            "sailing",
            "salon",
            "schools",
            "shaded_dot",
            "shopping",
            "ski",
            "snack_bar",
            "square",
            "star",
            "subway",
            "swimming",
            "target",
            "terrain",
            "toilets",
            "trail",
            "tram",
            "triangle",
            "truck",
            "volcano",
            "water",
            "webcam",
            "wheel_chair_accessible",
            "woman",
            "yen",
            "sunny",
            "partly_cloudy",
            "snowflake_simple",
            "rainy",
            "thunderstorm",
        ]
    },
}
# cabs reuses the arts URL
_ICON_URLS["Shapes"]["cabs"] = f"{_SHAPE}arts.png"

_DEFAULT_ICON = f"{_PUSH}ylw-pushpin.png"


def pin_icon_select(icon_type: str, icon_style: str) -> str:
    """Return the KML icon URL for a given type/style combination."""
    return _ICON_URLS.get(icon_type, {}).get(icon_style, _DEFAULT_ICON)


# inputFilename is a csv file generated by the NER_extractor
# customize pins for Google Earth Pro
# called from GIS_KML_util
def pin_customizer(
    inputFilename,
    pnt,
    geo_index,
    index_list,
    locationColumnName,
    sentence="",
    group_var=0,
    group_number_var=1,
    group_values=None,
    group_labels=None,
    icon_type_list=None,
    icon_style_list=None,
    icon_url="http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png",
    name_var_list=None,
    scale_var_list=None,
    color_var_list=None,
    color_style_var_list=None,
    bold_var_list=None,
    italic_var_list=None,
    description_var_list=None,
    description_csv_field_var_list=None,
    j=0,
    data=None,
    headers=None,
):
    if description_csv_field_var_list is None:
        description_csv_field_var_list = ["Sentence"]
    if description_var_list is None:
        description_var_list = [1]
    if italic_var_list is None:
        italic_var_list = [1]
    if bold_var_list is None:
        bold_var_list = [1]
    if color_style_var_list is None:
        color_style_var_list = [""]
    if color_var_list is None:
        color_var_list = [0]
    if scale_var_list is None:
        scale_var_list = ["1"]
    if name_var_list is None:
        name_var_list = [0]
    if icon_style_list is None:
        icon_style_list = ["red"]
    if icon_type_list is None:
        icon_type_list = ["Pushpins"]
    if group_labels is None:
        group_labels = [""]
    if group_values is None:
        group_values = [""]
    if data is None:
        withHeader_var = IO_csv_util.csvFile_has_header(inputFilename)  # check if the file has header
        data, headers = IO_csv_util.get_csv_data(inputFilename, withHeader_var)  # get the data and header

    # startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS kml pin customizer', 'Started running kml pin customizer at',
    # 											   True, '', True, '', silent=True)

    # Assign description
    if description_var_list[j] == 1:
        if len(description_csv_field_var_list[j]) == 0:
            logger.info(
                "No CSV Field Selected for Description for Group No."
                + str(j + 1)
                + "The description checkbox is ticked but no csv field was selected for the Group No."
                + str(j + 1)
                + ".\n\nPlease, check your input and try again."
            )

            sys.exit()
        if group_var == 1:
            if len(group_labels[j]) < 1:
                logger.info(
                    "No group labels specified for Group No. "
                    + str(j + 1)
                    + "There is no group label specified for Group No."
                    + str(j + 1)
                    + '.\n\nThe program will automatically set a group label for this group as "Group '
                    + str(j + 1)
                    + "."
                )

                new_label = "Group " + str(j + 1)
                group_labels[j] = new_label

        pnt = pin_description(
            inputFilename,
            pnt,
            data,
            headers,
            geo_index,
            index_list,
            locationColumnName,
            sentence,
            group_var,
            group_values,
            group_labels,
            j,
            name_var_list[j],
            description_csv_field_var_list[j],
            italic_var_list[j],
            bold_var_list[j],
        )
    # Assign name
    if name_var_list[j] == 1:
        pnt = pin_name(
            pnt,
            data,
            headers,
            geo_index,
            description_csv_field_var_list[j],
            scale_var_list[j],
            color_var_list[j],
            color_style_var_list[j],
        )

    # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS kml pin customizer', 'Finished running kml pin customizer at', True, '',
    # 								   True, startTime, silent=True)

    return pnt


# Add description to each point
# data is all the data from the inputfile, a double list [[]]
# 	Expected format: [[Atlanta, A, A, Georgia, ...], [Boston, B, B, Massachuttes, ...], [Charlotte, C, C, Notrh Carolina, ....]]
# headers is the inputfile's headers
# Expected format: [City, latitude, longitude, State, .....]
# Index is the number of the city we are currently plotting the point
# For example, from the example above, Atlanta will be 1, Boston will be 2....
# Column_name is the description_var (passed from GUI, the drop down menu, which column we want to put as description)
# Expected format: column_name ==  "State"
# inputFilename is a csv file generated by the NER_extractor


# name_var_list = [0], scale_var_list = ['1'],
# color_var_list = [0], color_style_var_list = [''],
#
# description_var_list = [1], description_csv_field_var_list = ['Sentence'],
# j = 0, data = None, headers = None):


def pin_description(
    inputFilename,
    pnt,
    data,
    headers,
    geo_index,
    index_list,
    description_location_var_name="Location",
    sentence="",
    group_var=0,
    group_values=None,
    group_labels=None,
    j=0,
    name_var=0,
    description_csv_field_var="Sentence",
    italic_var=None,
    bold_var=None,
):
    # # TODO if the inputFilename contains more than one document then the document name should be listed in descriptions
    if bold_var is None:
        bold_var = [1]
    if italic_var is None:
        italic_var = [1]
    if group_labels is None:
        group_labels = [""]
    if group_values is None:
        group_values = [""]
    if "Document ID" in headers:
        IO_csv_util.GetMaxValueInCSVField(inputFilename, "GIS_Google_pin", "Document ID")

    if description_location_var_name == "NER":
        description_location_var_name = "Location"

    if sentence == "":
        # the input filename contains the list of NER non-geocoded LOCATIONS
        # it is used to extract the sentence to be displayed when clicking on the pin
        documents = []
        names = []
        description = []
        for a in range(len(headers)):
            if "Document" == headers[a]:
                pass
            if description_csv_field_var == headers[a]:  # description_csv_field_var is typically set to sentence
                pass
            if description_location_var_name == headers[a]:
                pass
        # TODO MINO Pandas
        data = pd.read_csv(inputFilename, encoding="utf-8", on_bad_lines="skip")
        names = data["Location"].values.tolist()
        description = data["Sentence"].values.tolist()
        documents = data["Document"].apply(IO_csv_util.undressFilenameForCSVHyperlink)
        documents = documents.apply(os.path.split)
        documents = [item[1] for _, item in documents.items()]

    index = index_list[geo_index - 1]

    if group_var == 1:
        group_value = group_values[j]
        group_label = group_labels[j]
        if name_var == 0:
            if description_location_var_name == description_csv_field_var:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = (
                        "<i><b>Location</b></i>: "
                        + names[index - 1]
                        + "<br/><br/><i><b>Group Label</b></i>: "
                        + group_label
                        + "<br/><br/><i><b>Group Value</b></i>: "
                        + group_value
                    )
                elif bold_var == 1:
                    pnt.description = (
                        "<b>Location</b>: "
                        + names[index - 1]
                        + "<br/><br/><b>Group Label</b>: "
                        + group_label
                        + "<br/><br/><b>Group Value</b>: "
                        + group_value
                    )
                elif italic_var == 1:
                    pnt.description = (
                        "<i>Location</i>: "
                        + names[index - 1]
                        + "<br/><br/><i>Group Label</i>: "
                        + group_label
                        + "<br/><br/><i>Group Value</i>: "
                        + group_value
                    )
                else:
                    pnt.description = (
                        "Location: "
                        + names[index - 1]
                        + "<br/><br/>"
                        + "Group Label: "
                        + group_label
                        + "<br/><br/>"
                        + "Group Value: "
                        + group_value
                    )
            else:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = (
                        "<i><b>Location</b></i>: "
                        + names[index - 1]
                        + "<br/><br/><i><b>Group Label</b></i>: "
                        + group_label
                        + "<br/><br/><i><b>Group Value</b></i>: "
                        + group_value
                        + "<br/><br/><i><b>"
                        + description_csv_field_var
                        + "</b></i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i><b>Document"
                        + "</b></i>"
                        + ": "
                        + documents[index - 1]
                    )
                elif bold_var == 1:
                    pnt.description = (
                        "<b>Location</b>: "
                        + names[index - 1]
                        + "<br/><br/><b>Group Label</b>: "
                        + group_label
                        + "<br/><br/><b>Group Value</b>: "
                        + group_value
                        + "<br/><br/><b>"
                        + description_csv_field_var
                        + "</b>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<b>Document"
                        + "</b>"
                        + ": "
                        + documents[index - 1]
                    )
                elif italic_var == 1:
                    pnt.description = (
                        "<i>Location</i>: "
                        + names[index - 1]
                        + "<br/><br/><i>Group Label</i>: "
                        + group_label
                        + "<br/><br/><i>Group Value</i>: "
                        + group_value
                        + "<br/><br/><i>"
                        + description_csv_field_var
                        + "</i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i>Document"
                        + "</i>"
                        + ": "
                        + documents[index - 1]
                    )
                else:
                    pnt.description = (
                        "Location: "
                        + names[index - 1]
                        + "<br/><br/>"
                        + "Group Label: "
                        + group_label
                        + "<br/><br/>"
                        + "Group Value: "
                        + group_value
                        + "<br/><br/>"
                        + description_csv_field_var
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "Document"
                        + ": "
                        + documents[index - 1]
                    )
        else:
            if description_location_var_name == description_csv_field_var:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = (
                        "<i><b>Group Label</b></i>: "
                        + group_label
                        + "<br/><br/><i><b>Group Value</b></i>: "
                        + group_value
                    )
                elif bold_var == 1:
                    pnt.description = (
                        "<b>Group Label</b>: " + group_label + "<br/><br/><b>Group Value</b>: " + group_value
                    )
                elif italic_var == 1:
                    pnt.description = (
                        "<i>Group Label</i>: " + group_label + "<br/><br/><i>Group Value</i>: " + group_value
                    )
                else:
                    pnt.description = "Group Label: " + group_label + "<br/><br/>" + "Group Value: " + group_value
            else:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = (
                        "<i><b>Group Label</b></i>: "
                        + group_label
                        + "<br/><br/><i><b>Group Value</b></i>: "
                        + group_value
                        + "<br/><br/><i><b>"
                        + description_csv_field_var
                        + "</b></i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i><b>Document"
                        + "</b></i>"
                        + ": "
                        + documents[index - 1]
                    )
                elif bold_var == 1:
                    pnt.description = (
                        "<b>Group Label</b>: "
                        + group_label
                        + "<br/><br/><b>Group Value</b>: "
                        + group_value
                        + "<br/><br/><b>"
                        + description_csv_field_var
                        + "</b>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<b>Document"
                        + "</b>"
                        + ": "
                        + documents[index - 1]
                    )
                elif italic_var == 1:
                    pnt.description = (
                        "<i>Group Label</i>: "
                        + group_label
                        + "<br/><br/><i>Group Value</i>: "
                        + group_value
                        + "<br/><br/><i>"
                        + description_csv_field_var
                        + "</i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i>Document"
                        + "</i>"
                        + ": "
                        + documents[index - 1]
                    )
                else:
                    pnt.description = (
                        "Group Label: "
                        + group_label
                        + "<br/><br/>"
                        + "Group Value: "
                        + group_value
                        + "<br/><br/>"
                        + description_csv_field_var
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "Document"
                        + ": "
                        + documents[index - 1]
                    )

    elif group_var == 0:
        if name_var == 0:
            if description_location_var_name == description_csv_field_var:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = "<i><b>Location</b></i>: " + names[index - 1]
                elif bold_var == 1:
                    pnt.description = "<b>Location</b>: " + names[index - 1]
                elif italic_var == 1:
                    pnt.description = "<i>Location</i>: " + names[index - 1]
                else:
                    pnt.description = "Location: " + names[index - 1]
            else:
                if italic_var == 1 and bold_var == 1:
                    pnt.description = (
                        "<i><b>Location</b></i>: "
                        + names[index - 1]
                        + "<br/><br/><i><b>"
                        + description_csv_field_var
                        + "</b></i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i><b>Document"
                        + "</b></i>"
                        + ": "
                        + documents[index - 1]
                    )
                elif bold_var == 1:
                    pnt.description = (
                        "<b>Location</b>: "
                        + names[index - 1]
                        + "<br/><br/><b>"
                        + description_csv_field_var
                        + "</b>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<b>Document"
                        + "</b>"
                        + ": "
                        + documents[index - 1]
                    )

                elif italic_var == 1:
                    pnt.description = (
                        "<i>Location</i>: "
                        + names[index - 1]
                        + "<br/><br/><i>"
                        + description_csv_field_var
                        + "</i>"
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "<i>Document"
                        + "</i>"
                        + ": "
                        + documents[index - 1]
                    )
                else:
                    pnt.description = (
                        "Location: "
                        + names[index - 1]
                        + "<br/><br/>"
                        + description_csv_field_var
                        + ": "
                        + description[index - 1]
                        + "<br/><br/>"
                        + "Document"
                        + ": "
                        + documents[index - 1]
                    )
        else:
            if italic_var == 1 and bold_var == 1:
                pnt.description = (
                    "<i><b>"
                    + description_csv_field_var
                    + "</b></i>"
                    + ": "
                    + description[index - 1]
                    + "<i><b>Document"
                    + "</b></i>"
                    + ": "
                    + documents[index - 1]
                )

            elif bold_var == 1:
                pnt.description = (
                    "<b>"
                    + description_csv_field_var
                    + "</b>"
                    + ": "
                    + description[index - 1]
                    + "<b>Document"
                    + "</b>"
                    + ": "
                    + documents[index - 1]
                )

            elif italic_var == 1:
                pnt.description = (
                    "<i>"
                    + description_csv_field_var
                    + "</i>"
                    + ": "
                    + description[index - 1]
                    + "<i>Document"
                    + "</i>"
                    + ": "
                    + documents[index - 1]
                )

            else:
                pnt.description = (
                    description_csv_field_var + ": " + description[index - 1] + "Document" + ": " + documents[index - 1]
                )

    return pnt


# Add description to each point
# data is all the data from the inputfile
# 	Expected format: [[Atlanta, A, A, Georgia, ...], [Boston, B, B, Massachuttes, ...], [Charlotte, C, C, Notrh Carolina, ....]]
# headers is the inputfile's headers
# Expected format: [City, latitute, longitude, State, .....]
# Index is the number of the city we are currently plotting the point
# For example, from the example above, Atlanta will be 1, Boston will be 2....
# description_location_var_name is got from GUI_util, as the column where the locations' names at
# Expected format: location_var == "Name"
# scale_var is the variable for the scale of the name label
# Expected format: scale_var == 2 (it is an integer)
# color_var is the variable indicating whether the user choose a color of the name, 1 for yes, 0 for no
# Expected format: scale_var == 1 (it is an integer) and it will read set color_style_var
# Expected format: scale_var == 0 (it is an integer) and it will read default color white for color_style_var = (255, 255, 255)
# color_style_var is a string of rgb color code for the name
# Expected format: color_style_var = (255, 255, 255) is white


def pin_name(
    pnt,
    data,
    headers,
    geo_index,
    description_location_var_name,
    scale_var,
    color_var,
    color_style_var,
):
    names = []

    for i in range(len(headers)):
        if description_location_var_name == headers[i]:
            location_num = i
    for j in range(len(data)):
        names.append(data[j][location_num])
    pnt.name = names[geo_index - 1]
    pnt.style.labelstyle.scale = scale_var

    if int(color_var) == 1:
        color_code = color_style_var
    else:
        color_code = "(255, 255, 255)"
    rgb_value = color_code.split(", ")
    r = rgb_value[0].split("(")
    r_value = r[1]
    g_value = rgb_value[1]
    b = rgb_value[2].split(")")
    b_value = b[0]
    pnt.style.labelstyle.color = simplekml.Color.rgb(int(r_value), int(g_value), int(b_value))

    return pnt
