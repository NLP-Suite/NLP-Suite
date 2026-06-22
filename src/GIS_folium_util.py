import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "GIS_folium_util",
                                                  ['os', 'pandas', 'folium']) == False:
    sys.exit(0)

import os
import pandas as pd
import folium
from folium.plugins import HeatMap, TimestampedGeoJson
import tkinter.messagebox as mb

import IO_files_util
import IO_user_interface_util


def _load_geocoded_data(inputFilename):
    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        mb.showwarning('Warning',
                       'Could not read the input csv file\n\n' + inputFilename + '\n\n' + str(e))
        return None

    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        mb.showwarning('Warning',
                       'The input csv file\n\n' + inputFilename +
                       '\n\ndoes not contain Latitude and Longitude columns required for Folium mapping.'
                       '\n\nPlease, select a geocoded csv file in input and try again.')
        return None

    df = df.dropna(subset=['Latitude', 'Longitude'])
    if len(df) == 0:
        mb.showwarning('Warning',
                       'The input csv file\n\n' + inputFilename +
                       '\n\ncontains no valid geocoded rows (all Latitude/Longitude values are empty).')
        return None

    return df


def _compute_center(df):
    return [df['Latitude'].mean(), df['Longitude'].mean()]


# Columns excluded from popup descriptions (infrastructure, not user-facing data)
_POPUP_SKIP_COLS = {
    'Latitude', 'Longitude', 'latitude', 'longitude',
    'Address', 'Country from Geocoder',
    'Sentence ID', 'Document ID', 'Source_ID', 'Target_ID',
    'Complex ID', 'Document ID',
}
_POPUP_SKIP_SUFFIXES = ('_ID', '_Simplex', ' Order', ' Identifier')


def _build_popup_html(row, df_columns, location_col=None, max_text_len=200):
    """Build a rich HTML popup from all non-infrastructure columns in a row,
    matching the Google Earth Pro description style (bold label: value)."""
    parts = []

    # Location first if available
    if location_col and location_col in df_columns:
        val = row.get(location_col)
        if pd.notna(val) and str(val).strip():
            parts.append(f"<b>Location</b>: {val}")

    for col in df_columns:
        if col == location_col:
            continue
        if col in _POPUP_SKIP_COLS:
            continue
        if any(col.endswith(s) for s in _POPUP_SKIP_SUFFIXES):
            continue

        val = row.get(col)
        if pd.isna(val):
            continue
        val_str = str(val).strip()
        if not val_str or val_str == 'nan':
            continue

        # Clean up HYPERLINK-wrapped document paths
        if col == 'Document':
            val_str = os.path.basename(val_str.replace('=HYPERLINK("', '').rstrip('")'))

        # Truncate long text fields (e.g. Sentence)
        if len(val_str) > max_text_len:
            val_str = val_str[:max_text_len] + '...'

        parts.append(f"<b>{col}</b>: {val_str}")

    return "<br/>".join(parts) if parts else ""


def create_folium_pin_map(window, inputFilename, outputDir, locationColumnName='Location'):
    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Folium pin map',
                                                    'Started running Folium pin map at',
                                                    True, '', True, '', False)

    df = _load_geocoded_data(inputFilename)
    if df is None:
        return ''

    center = _compute_center(df)
    m = folium.Map(location=center, zoom_start=4, tiles='OpenStreetMap')

    location_col = locationColumnName if locationColumnName in df.columns else None
    popup_columns = [c for c in df.columns]

    for _, row in df.iterrows():
        lat = row['Latitude']
        lng = row['Longitude']

        name = str(row[location_col]) if location_col else f"{lat:.4f}, {lng:.4f}"
        popup_html = _build_popup_html(row, popup_columns, location_col)

        folium.CircleMarker(
            location=[lat, lng],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7
        ).add_to(m)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                              '.html', 'GIS',
                                                              'Folium-pin', locationColumnName, '', '',
                                                              False, True)
    m.save(outputFilename)

    IO_user_interface_util.timed_alert(window, 2000, 'Folium pin map',
                                        'Finished running Folium pin map at',
                                        True, '', True, startTime)

    return outputFilename


def create_folium_heatmap(window, inputFilename, outputDir, locationColumnName='Location'):
    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Folium heatmap',
                                                    'Started running Folium heatmap at',
                                                    True, '', True, '', False)

    df = _load_geocoded_data(inputFilename)
    if df is None:
        return ''

    center = _compute_center(df)
    m = folium.Map(location=center, zoom_start=4, tiles='OpenStreetMap')

    heat_data = df[['Latitude', 'Longitude']].values.tolist()

    HeatMap(heat_data, radius=15, blur=10, max_zoom=13).add_to(m)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                              '.html', 'GIS',
                                                              'Folium-heat', locationColumnName, '', '',
                                                              False, True)
    m.save(outputFilename)

    IO_user_interface_util.timed_alert(window, 2000, 'Folium heatmap',
                                        'Finished running Folium heatmap at',
                                        True, '', True, startTime)

    return outputFilename


def create_folium_timestamped_map(window, inputFilename, outputDir,
                                   locationColumnName='Location',
                                   dateColumnName='Date'):
    startTime = IO_user_interface_util.timed_alert(window, 2000, 'Folium timestamped map',
                                                    'Started running Folium timestamped map at',
                                                    True, '', True, '', False)

    df = _load_geocoded_data(inputFilename)
    if df is None:
        return ''

    if dateColumnName not in df.columns:
        mb.showwarning('Warning',
                       'The input csv file\n\n' + inputFilename +
                       '\n\ndoes not contain a "' + dateColumnName + '" column required '
                       'for the Folium timestamped map with time slider.'
                       '\n\nPlease, select a geocoded csv file with dates and try again.')
        return ''

    df = df.dropna(subset=[dateColumnName])
    if len(df) == 0:
        mb.showwarning('Warning',
                       'The input csv file\n\n' + inputFilename +
                       '\n\ncontains no valid rows with dates for the Folium timestamped map.')
        return ''

    df[dateColumnName] = pd.to_datetime(df[dateColumnName], errors='coerce')
    df = df.dropna(subset=[dateColumnName])
    if len(df) == 0:
        mb.showwarning('Warning',
                       'No valid dates could be parsed from the "' + dateColumnName +
                       '" column in\n\n' + inputFilename)
        return ''

    df = df.sort_values(by=dateColumnName)

    location_col = locationColumnName if locationColumnName in df.columns else None
    popup_columns = [c for c in df.columns]

    features = []
    for _, row in df.iterrows():
        lat = row['Latitude']
        lng = row['Longitude']
        dt = row[dateColumnName]
        iso_time = dt.strftime('%Y-%m-%dT%H:%M:%S')

        name = str(row[location_col]) if location_col else f"{lat:.4f}, {lng:.4f}"
        popup_html = _build_popup_html(row, popup_columns, location_col)

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lng, lat],
            },
            'properties': {
                'time': iso_time,
                'popup': popup_html,
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': '#CD3181',
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 7,
                    'weight': 1,
                },
                'style': {'weight': 0},
            },
        }
        features.append(feature)

    center = _compute_center(df)
    m = folium.Map(location=center, zoom_start=4, tiles='OpenStreetMap')

    # place the time-slider control in the TOP-LEFT corner (like Google Earth Pro's time slider).
    # folium's TimestampedGeoJson does not expose a position option; the control defaults to the
    # bottom-left leaflet corner, so move that corner to the top-left, below the zoom buttons.
    m.get_root().header.add_child(folium.Element(
        "<style>"
        ".leaflet-bottom.leaflet-left{top:10px;bottom:auto;left:55px;}"
        ".leaflet-bottom.leaflet-left .leaflet-control-timecontrol{margin-bottom:0;}"
        "</style>"))

    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='P1D',
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY-MM-DD',
        time_slider_drag_update=True,
    ).add_to(m)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, '', outputDir,
                                                              '.html', 'GIS',
                                                              'Folium-time', locationColumnName, '', '',
                                                              False, True)
    m.save(outputFilename)

    IO_user_interface_util.timed_alert(window, 2000, 'Folium timestamped map',
                                        'Finished running Folium timestamped map at',
                                        True, '', True, startTime)

    return outputFilename
