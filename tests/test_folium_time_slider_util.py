"""folium_time_slider_util: the time map's play button moves, and records
before 1970 are kept (21 Sept 2026)."""
import datetime

import folium_time_slider_util as ts

FOLIUM_LIKE = '''L.timeDimension({ period: "P1D", });
L.timeDimension.layer.geoJson(geoJsonLayer, {
    updateTimeDimension: true,
    addlastPoint: true,
    duration: undefined,
})'''


def test_period_follows_the_span():
    d = datetime.datetime
    assert ts.period_for(d(1859, 4, 28), d(1910, 4, 4)) == 'P1Y'
    assert ts.period_for(d(1900, 1, 1), d(1903, 1, 1)) == 'P1M'
    assert ts.period_for(d(1900, 1, 1), d(1900, 3, 1)) == 'P1D'


def test_year_stops_are_year_ends_and_can_be_before_1970():
    got = ts.stops(datetime.datetime(1859, 4, 28), datetime.datetime(1862, 2, 1), 'P1Y')
    assert len(got) == 4 and got == sorted(got) and got[0] < 0
    first = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=got[0])
    assert (first.year, first.month, first.day, first.hour) == (1859, 12, 31, 23)


def test_month_and_day_stops():
    assert len(ts.stops(datetime.datetime(1900, 11, 5), datetime.datetime(1901, 2, 1), 'P1M')) == 4
    assert len(ts.stops(datetime.datetime(1900, 1, 30), datetime.datetime(1900, 2, 2), 'P1D')) == 4


def test_patch_sets_stops_window_and_stops_the_rewrite():
    html, ok = ts.patch(FOLIUM_LIKE, [1, 2])
    assert ok
    assert 'times: [1, 2],' in html and 'period:' not in html
    assert 'updateTimeDimension: false,' in html and 'duration: "P500Y",' in html


def test_an_unrecognised_page_is_reported_not_changed():
    html, ok = ts.patch('<html></html>', [1])
    assert not ok and html == '<html></html>'


def test_a_bare_year_is_a_year_not_nanoseconds_after_1970():
    assert ts.date_text(1870) == '1870-01-01'
    assert ts.date_text(1870.0) == '1870-01-01'
    assert ts.date_text('1870-06') == '1870-06-01'
    assert ts.date_text('1870-00-00') == '1870-01-01'
    assert ts.date_text('June 1870') == 'June 1870'
