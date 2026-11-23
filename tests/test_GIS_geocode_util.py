"""Tests for src/GIS_geocode_util.py, one file per module (folded from 3 files, 23 Nov 2026).

From test_gis_continent_geocode.py:

GIS: continents are joined only to a direction word, and a geocoder miss is retried.

Continent merge: any location that was a continent name was joined onto the previous row's location, whatever it
was ('Madrid America', 'Vienna Europe', even across documents), the previous row was dropped, and the result was
written back over the input csv. Now only a direction word ('South', 'Western', ...) just before the continent, in the
same sentence of the same document, is joined, and the input file is left alone.

Nominatim: the NER tag is passed as featuretype (STATE_OR_PROVINCE -> 'state'). Leicestershire is a county to
Nominatim, so the filtered search found nothing and the place was recorded NOT FOUND. A miss is now retried once
without the filter.

Google: google_geocode overwrote its region argument with '.US' and retried a timeout forever.

The GIS modules import the GUI, so the functions under test are pulled out of the source and run on their own.

From test_gis_geocode_cache.py:

GIS: the geocode cache survives between runs, is keyed by the geocoder settings, and never caches service errors.

The cache was written to the GIS output folder, which make_output_subdirectory deletes at the start of every GIS
run, so it never survived: every rerun on a 711-location corpus took about 13 minutes. Its key was the bare place
name, so a result found with one country bias was reused for another. And a timeout or an HTTP 403 block was
retried, turned into None, and cached as NOT FOUND, so an outage looked like bad place names on every later run.

The GIS modules import the GUI, so the functions under test are pulled out of the source and run on their own.

From test_gis_ner_tag_column.py:

GIS: the "(NER tag: ...)" log line names the tag the geocoder actually uses.

A csv of locations with dates comes in as [location, date, NER tag, sentence, document]; without dates,
[location, NER tag, sentence, document]; a CoNLL table always has the tag in column 1. The log line printed
column 1 in every case, so a dated csv logged "Processing location ... (NER tag: 1893-04-12)" while the
geocoder used column 2.

GIS_geocode_util imports the GUI, so the helper is pulled out of the source and run on its own.
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


# ---- formerly tests/test_gis_geocode_cache.py ---------------------------------------------------------------

import json  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

CACHE_NAMES = {
    "_GEOCODE_CACHE_FILENAME",
    "_GEOCODE_CACHE_VERSION",
    "_GEOCODE_CACHE",
    "_GEOCODE_CACHE_PATH",
    "_GEOCODE_CACHE_DIRTY",
    "_geocode_cache_path",
    "_geocode_cache_key",
    "_load_geocode_cache",
    "_save_geocode_cache",
    "_cache_get",
    "_cache_put",
    "_CONTINENTS",
    "_nominatim_featuretype",
    "nominatim_geocode",
}


class Blocked(Exception):
    pass


class RateLimited(Exception):
    pass


def _load_gis_geocode_cache(names, namespace):
    source = open(os.path.join(SRC, "GIS_geocode_util.py"), encoding="utf-8-sig").read()
    tree = ast.parse(source)
    for node in tree.body:
        targets = [t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)]
        if getattr(node, "name", None) in names or any(t in names for t in targets):
            exec(ast.get_source_segment(source, node), namespace)
    return namespace


@pytest.fixture
def ns(tmp_path):
    namespace = {
        "os": os,
        "json": json,
        "time": MagicMock(),
        "GUI_IO_util": MagicMock(configPath=str(tmp_path / "config")),
        "GeocoderInsufficientPrivileges": Blocked,
        "GeocoderRateLimited": RateLimited,
    }
    return _load_gis_geocode_cache(CACHE_NAMES, namespace)


def test_cache_is_kept_in_the_config_folder_and_survives_a_reload(ns, tmp_path):
    ns["_load_geocode_cache"]()
    key = ns["_geocode_cache_key"]("Atlanta", "Nominatim", featuretype="city")
    ns["_cache_put"](key, 33.7, -84.4, "Atlanta, Georgia, United States")
    ns["_save_geocode_cache"]()
    assert os.path.isfile(tmp_path / "config" / "GIS_geocode_cache.json")

    ns["_GEOCODE_CACHE"].clear()
    ns["_load_geocode_cache"]()
    assert ns["_cache_get"](key) == (33.7, -84.4, "Atlanta, Georgia, United States")


def test_geocode_no_longer_puts_the_cache_in_the_output_folder():
    source = open(os.path.join(SRC, "GIS_geocode_util.py"), encoding="utf-8-sig").read()
    assert "_load_geocode_cache(outputDir)" not in source


def test_old_flat_cache_files_are_discarded(ns, tmp_path):
    os.makedirs(tmp_path / "config")
    (tmp_path / "config" / "GIS_geocode_cache.json").write_text(json.dumps({"Paris": [0, 0, " NOT FOUND"]}))
    ns["_load_geocode_cache"]()
    assert ns["_GEOCODE_CACHE"] == {}


def test_settings_that_change_the_answer_are_part_of_the_key(ns):
    key = ns["_geocode_cache_key"]
    base = key("Paris", "Nominatim")
    assert key("Paris", "Nominatim", country_bias="us") != base
    assert key("Paris", "Nominatim", area="(1,2),(3,4)") != base
    assert key("Paris", "Nominatim", restrict=True) != base
    assert key("Paris", "Nominatim", featuretype="city") != base
    assert key("Paris", "Google") != base
    assert key("Paris", "Nominatim", area="(1, 2),(3, 4)") == key("Paris", "Nominatim", area="(1,2),(3,4)")


def test_featuretype_comes_from_the_ner_tag_except_for_continents(ns):
    ft = ns["_nominatim_featuretype"]
    assert ft("Leicestershire", "STATE_OR_PROVINCE") == "state"
    assert ft("Oslo", "CITY") == "city"
    assert ft("Norway", "COUNTRY") == "country"
    assert ft("South America", "LOCATION") == ""
    assert ft("Europe", "COUNTRY") == ""


def test_exhausted_timeouts_raise_instead_of_looking_like_a_miss(ns):
    geolocator = MagicMock()
    geolocator.geocode.side_effect = TimeoutError
    with pytest.raises(TimeoutError):
        ns["nominatim_geocode"](geolocator, "Oslo")
    assert geolocator.geocode.call_count == 5  # timeouts of 4, 8, 12, 16 and 20 seconds


def test_a_403_block_is_not_retried(ns):
    geolocator = MagicMock()
    geolocator.geocode.side_effect = Blocked
    with pytest.raises(Blocked):
        ns["nominatim_geocode"](geolocator, "Oslo")
    assert geolocator.geocode.call_count == 1


def test_a_real_miss_still_returns_none(ns):
    geolocator = MagicMock()
    geolocator.geocode.return_value = None
    assert ns["nominatim_geocode"](geolocator, "Nowhereville") is None


def test_a_timeout_retry_keeps_the_area(ns):
    # the retry passed back the parsed area; parsing it again crashed, and the crash was recorded as NOT FOUND
    geolocator = MagicMock()
    geolocator.geocode.side_effect = [TimeoutError, "hit"]
    assert ns["nominatim_geocode"](geolocator, "Oslo", box_tuple="(60, 10), (59, 11)") == "hit"
    assert geolocator.geocode.call_args.kwargs["viewbox"] == [(60.0, 10.0), (59.0, 11.0)]


# ---- formerly tests/test_gis_ner_tag_column.py --------------------------------------------------------------

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _load_gis_ner_tag_column(name):
    source = open(os.path.join(SRC, "GIS_geocode_util.py"), encoding="utf-8-sig").read()
    namespace = {}
    for node in ast.parse(source).body:
        if getattr(node, "name", None) == name:
            exec(ast.get_source_segment(source, node), namespace)
    return namespace[name]


location_NER_tag = _load_gis_ner_tag_column("location_NER_tag")


def test_a_csv_with_dates_has_the_tag_after_the_date():
    item = ["Chicago", "1893-04-12", "CITY", "A sentence.", "doc.txt"]
    assert location_NER_tag(item, inputIsCoNLL=False, datePresent=True) == "CITY"


def test_a_csv_without_dates_has_the_tag_second():
    item = ["Chicago", "CITY", "A sentence.", "doc.txt"]
    assert location_NER_tag(item, inputIsCoNLL=False, datePresent=False) == "CITY"


def test_a_conll_table_has_the_tag_second_even_with_dates():
    item = ["Chicago", "CITY", 3, "A sentence.", 1, "doc.txt", "1893-04-12"]
    assert location_NER_tag(item, inputIsCoNLL=True, datePresent=True) == "CITY"
