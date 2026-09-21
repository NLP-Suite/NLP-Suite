"""Every Suite map draws on Esri's tiles: a map page opened from disk is refused
by OpenStreetMap ("403 Access blocked") and stamped by CARTO ("API KEY
REQUIRED"). Roberto, 21 Sept 2026."""
import os
import re

import map_tiles_util as mt

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')


def test_folium_kwargs_are_esri():
    kw = mt.folium_tiles()
    assert 'arcgisonline.com' in kw['tiles']
    assert '{z}/{y}/{x}' in kw['tiles']          # ArcGIS order, y before x
    assert kw['attr'] and kw['max_zoom'] == mt.MAX_ZOOM


def test_leaflet_line_for_a_format_template():
    plain = mt.leaflet_tile_layer_js('map')
    doubled = mt.leaflet_tile_layer_js('map', braces_doubled=True)
    assert plain.startswith("L.tileLayer('https://server.arcgisonline.com") and plain.endswith('.addTo(map);')
    assert doubled.format() == plain              # what str.format turns it back into


def test_no_suite_module_asks_for_blocked_tiles():
    bad = re.compile(r"tile\.openstreetmap\.org|basemaps\.cartocdn\.com|tiles=['\"](?:OpenStreetMap|CartoDB)", re.I)
    offenders = []
    for name in sorted(os.listdir(SRC)):
        if name.endswith('.py') and name != 'map_tiles_util.py':
            with open(os.path.join(SRC, name), encoding='utf-8', errors='replace') as fh:
                for i, line in enumerate(fh, 1):
                    if bad.search(line):
                        offenders.append('%s:%d' % (name, i))
    assert not offenders, offenders