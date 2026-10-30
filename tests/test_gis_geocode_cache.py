"""GIS: the geocode cache survives between runs, is keyed by the geocoder settings, and never caches service errors.

The cache was written to the GIS output folder, which make_output_subdirectory deletes at the start of every GIS
run, so it never survived: every rerun on a 711-location corpus took about 13 minutes. Its key was the bare place
name, so a result found with one country bias was reused for another. And a timeout or an HTTP 403 block was
retried, turned into None, and cached as NOT FOUND, so an outage looked like bad place names on every later run.

The GIS modules import the GUI, so the functions under test are pulled out of the source and run on their own.
"""

import ast
import json
import os
from unittest.mock import MagicMock

import pytest

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


def _load(names, namespace):
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
    return _load(CACHE_NAMES, namespace)


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
