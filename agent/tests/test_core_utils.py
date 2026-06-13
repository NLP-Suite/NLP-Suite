"""Unit tests for core utilities that don't require NLP deps."""

import pytest

# ---------------------------------------------------------------------------
# constants_util
# ---------------------------------------------------------------------------

try:
    import constants_util

    _constants_available = True
except ImportError:
    _constants_available = False

pytestmark_constants = pytest.mark.skipif(not _constants_available, reason="constants_util not importable")


@pytestmark_constants
def test_languages_is_list():
    assert isinstance(constants_util.languages, list)
    assert len(constants_util.languages) > 50


@pytestmark_constants
def test_languages_contains_english():
    names = [name for _, name in constants_util.languages]
    assert "English" in names


@pytestmark_constants
def test_countries_is_list():
    assert isinstance(constants_util.countries, list)
    assert len(constants_util.countries) > 100


@pytestmark_constants
def test_iso_gis_country_menu_contains_usa():
    entries = constants_util.ISO_GIS_country_menu
    assert any("United States" in e for e in entries)


@pytestmark_constants
def test_dbpedia_ontology_menu_is_sequence():
    assert len(constants_util.DBpedia_ontology_class_menu) > 0
    assert "Thing" in constants_util.DBpedia_ontology_class_menu


# ---------------------------------------------------------------------------
# data_manipulation_util
# ---------------------------------------------------------------------------

try:
    import data_manipulation_util

    _dmu_available = True
except ImportError:
    _dmu_available = False

pytestmark_dmu = pytest.mark.skipif(not _dmu_available, reason="data_manipulation_util not importable")


@pytestmark_dmu
def test_get_comparator_lt():
    assert data_manipulation_util.get_comparator("less than") == "<"


@pytestmark_dmu
def test_get_comparator_gt():
    assert data_manipulation_util.get_comparator("greater than") == ">"


@pytestmark_dmu
def test_list_to_string_comma():
    result = data_manipulation_util.listToString(["a", "b", "c"], ",")
    assert result == "a,b,c"


@pytestmark_dmu
def test_list_to_string_space():
    result = data_manipulation_util.listToString(["hello", "world"], " ")
    assert result == "hello world"
