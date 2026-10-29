"""GIS: continents are joined only to a direction word, and a geocoder miss is retried.

Continent merge: any location that was a continent name was joined onto the previous row's location, whatever it
was ('Madrid America', 'Vienna Europe', even across documents), the previous row was dropped, and the result was
written back over the input csv. Now only a direction word ('South', 'Western', ...) just before the continent, in the
same sentence of the same document, is joined, and the input file is left alone.

Nominatim: the NER tag is passed as featuretype (STATE_OR_PROVINCE -> 'state'). Leicestershire is a county to
Nominatim, so the filtered search found nothing and the place was recorded NOT FOUND. A miss is now retried once
without the filter.

Google: google_geocode overwrote its region argument with '.US' and retried a timeout forever.

The GIS modules import the GUI, so the functions under test are pulled out of the source and run on their own.
"""

import ast
import os
from unittest.mock import MagicMock

import _real_pandas
import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _load(filename, names, namespace):
    source = open(os.path.join(SRC, filename), encoding="utf-8-sig").read()
    tree = ast.parse(source)
    for node in tree.body:
        targets = [t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)]
        if getattr(node, "name", None) in names or any(t in names for t in targets):
            exec(ast.get_source_segment(source, node), namespace)
    return namespace


@pytest.fixture(scope="module")
def pd():
    try:
        pandas, saved = _real_pandas.swap_in()
    except ImportError as exc:
        pytest.skip(f"real pandas not available: {exc}")
    yield pandas
    _real_pandas.swap_out(saved)


@pytest.fixture(scope="module")
def merge(pd):
    return _load("GIS_pipeline_util.py", {"CONTINENTS", "DIRECTIONS", "merge_direction_continent"}, {})[
        "merge_direction_continent"
    ]


def _frame(pd, rows):
    return pd.DataFrame(rows, columns=["Location", "NER", "Sentence", "Document"])


def test_direction_word_and_continent_become_one_location(pd, merge):
    df = _frame(
        pd,
        [
            ["South", "LOCATION", "s1", "d1"],
            ["America", "LOCATION", "s1", "d1"],
            ["Western", "LOCATION", "s2", "d1"],
            ["Europe", "LOCATION", "s2", "d1"],
        ],
    )
    assert list(merge(df)["Location"]) == ["South America", "Western Europe"]


def test_other_places_before_a_continent_are_left_alone(pd, merge):
    rows = [
        ["Madrid", "CITY", "s1", "d1"],
        ["America", "LOCATION", "s1", "d1"],
        ["China", "COUNTRY", "s2", "d1"],
        ["Asia", "LOCATION", "s2", "d1"],
        ["Melbourne", "CITY", "s3", "d1"],
        ["Australia", "COUNTRY", "s3", "d1"],
    ]
    assert list(merge(_frame(pd, rows))["Location"]) == [r[0] for r in rows]


def test_no_join_across_sentences_or_documents(pd, merge):
    rows = [
        ["South", "LOCATION", "s1", "d1"],
        ["America", "LOCATION", "s2", "d1"],
        ["East", "LOCATION", "s3", "d1"],
        ["Asia", "LOCATION", "s3", "d2"],
    ]
    assert list(merge(_frame(pd, rows))["Location"]) == [r[0] for r in rows]


def test_merge_does_not_change_the_frame_it_is_given(pd, merge):
    df = _frame(pd, [["South", "LOCATION", "s1", "d1"], ["America", "LOCATION", "s1", "d1"]])
    merge(df)
    assert list(df["Location"]) == ["South", "America"]


def test_pipeline_no_longer_writes_to_its_input_file():
    source = open(os.path.join(SRC, "GIS_pipeline_util.py"), encoding="utf-8-sig").read()
    assert "to_csv(inputFilename" not in source


def _geocode_namespace():
    namespace = {"time": MagicMock(), "GeocoderTimedOut": TimeoutError}
    return _load("GIS_geocode_util.py", {"nominatim_geocode_any_type", "google_geocode"}, namespace)


def test_nominatim_miss_with_a_featuretype_is_retried_without_it():
    ns = _geocode_namespace()
    found = object()
    calls = []

    def fake(geolocator, featuretype=None, **kwargs):
        calls.append(featuretype)
        return None if featuretype else found

    ns["nominatim_geocode"] = fake
    assert (
        ns["nominatim_geocode_any_type"](
            None, "Leicestershire", country_bias="", box_tuple="", restrict=False, featuretype="state"
        )
        is found
    )
    assert calls == ["state", None]


def test_nominatim_hit_or_unfiltered_miss_is_not_retried():
    ns = _geocode_namespace()
    calls = []
    ns["nominatim_geocode"] = lambda *a, featuretype=None, **k: calls.append(featuretype) or "hit"
    assert (
        ns["nominatim_geocode_any_type"](
            None, "Oslo", country_bias="", box_tuple="", restrict=False, featuretype="city"
        )
        == "hit"
    )
    ns["nominatim_geocode"] = lambda *a, featuretype=None, **k: calls.append(featuretype)
    assert (
        ns["nominatim_geocode_any_type"](None, "Nowhere", country_bias="", box_tuple="", restrict=False, featuretype="")
        is None
    )
    assert calls == ["city", ""]


def test_google_uses_the_country_bias_and_gives_up_on_repeated_timeouts():
    ns = _geocode_namespace()
    geolocator = MagicMock()
    ns["google_geocode"](geolocator, "Leicester", "gb")
    assert geolocator.geocode.call_args.kwargs["region"] == "gb"
    ns["google_geocode"](geolocator, "Leicester", "")
    assert geolocator.geocode.call_args.kwargs["region"] is None

    geolocator.geocode.side_effect = TimeoutError
    assert ns["google_geocode"](geolocator, "Leicester") is None
    assert geolocator.geocode.call_count == 2 + 3  # the two calls above, then 10, 20 and 30 seconds


def test_gis_main_checks_the_geocode_checkbox_value_not_the_tk_variable():
    source = open(os.path.join(SRC, "GIS_main.py"), encoding="utf-8-sig").read()
    assert "geocode_locations_var==False" not in source
    assert "geocode_locations_var == True" not in source


def test_continents_are_not_searched_with_an_invalid_featuretype():
    # Nominatim's featuretype takes country, state, city or settlement; 'continent' sent South America to Florida
    source = open(os.path.join(SRC, "GIS_geocode_util.py"), encoding="utf-8-sig").read()
    assert "NER_Tag_Nominatim='continent'" not in source
