"""The background tiles for every map the NLP Suite writes.

WHY NOT OPENSTREETMAP. The Suite's maps are HTML pages opened from disk
(file://), so their tile requests carry no Referer. Since September 2026
tile.openstreetmap.org answers every such request with a picture reading
"403 Access blocked - App is not following the tile usage policy", so a map
drawn on 'OpenStreetMap' shows a wall of those notices instead of a map.
CARTO (basemaps.cartocdn.com, folium's 'CartoDB positron') is no better: it
serves a real-looking tile STAMPED "API KEY REQUIRED".

Esri's World Street Map serves a page on disk with a plain map. It is the
first of the Family Archive viewer's own tile sources, chosen for the same
reason (family_archive_viewer_util.TILE_SOURCES).

Stdlib only: imported by GIS_folium_util and charts_util, and testable alone.
"""

#: Esri's tile address - note {y} before {x}, the ArcGIS order.
TILE_URL = ('https://server.arcgisonline.com/ArcGIS/rest/services/'
            'World_Street_Map/MapServer/tile/{z}/{y}/{x}')
ATTRIBUTION = 'Tiles &copy; Esri'
MAX_ZOOM = 18


def folium_tiles():
    """Keyword arguments for folium.Map: tiles, attr and max_zoom."""
    return {'tiles': TILE_URL, 'attr': ATTRIBUTION, 'max_zoom': MAX_ZOOM}


def leaflet_tile_layer_js(map_var='map', braces_doubled=False):
    """The Leaflet line that adds these tiles to *map_var*.

    braces_doubled for a str.format template, where { must be written {{."""
    js = ("L.tileLayer('%s', {attribution: '%s', maxZoom: %d}).addTo(%s);"
          % (TILE_URL, ATTRIBUTION, MAX_ZOOM, map_var))
    return js.replace('{', '{{').replace('}', '}}') if braces_doubled else js