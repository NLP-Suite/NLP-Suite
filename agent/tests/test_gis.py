import os
import pathlib
import shutil

import pytest
from conftest import output_csvs, read_rows

try:
    import GIS_geocode_util
    import GIS_location_util
    import GIS_pipeline_util
    import IO_internet_util
    from GIS_main import run_GIS
except (ImportError, SystemExit):
    pytest.skip("GIS dependencies not available", allow_module_level=True)


class _StubLocation:
    latitude = 41.9
    longitude = 12.5
    address = "Rome, Lazio, Italy"


class _StubGeolocator:
    def geocode(self, *args, **kwargs):
        return _StubLocation()


@pytest.fixture
def mocked_geocoder(monkeypatch):
    """Make the GIS pipeline hermetic: no internet check, no Nominatim."""
    monkeypatch.setattr(IO_internet_util, "check_internet_availability_warning", lambda *a, **k: True)
    monkeypatch.setattr(GIS_geocode_util, "get_geolocator", lambda *a, **k: _StubGeolocator())


@pytest.fixture
def locations_input(tmp_path, fixture_locations_csv):
    # the pipeline may rewrite its input csv in place (continent merging), so
    # give each test a disposable copy
    input_dir = tmp_path / "gis_input"
    input_dir.mkdir()
    dst = input_dir / "locations.csv"
    shutil.copy(fixture_locations_csv, dst)
    return dst


# unit tests on pure helpers --------------------------------------------------


def test_extract_ner_locations_from_conll(fixture_conll):
    locs = GIS_location_util.extract_NER_locations(str(fixture_conll), "utf-8", False)
    assert any(item[0] == "Italy" and item[1] == "COUNTRY" for item in locs)


def test_extract_csvfile_locations(fixture_locations_csv):
    locs = GIS_location_util.extract_csvFile_locations(str(fixture_locations_csv), True, 0, "utf-8", False, -1)
    # Rome and Paris are CITY rows; the PERSON row must be filtered out
    assert [item[0] for item in locs] == ["Rome", "Paris"]


def test_get_geolocator_nominatim():
    from geopy import Nominatim

    assert isinstance(GIS_geocode_util.get_geolocator("Nominatim"), Nominatim)


def test_convert_to_gep_date():
    assert GIS_geocode_util.convertToGEP("2020-05-01") == "2020-05-01"


# pipeline (hermetic, geocoder mocked) ----------------------------------------


def test_gis_pipeline_mocked_geocoder(locations_input, tmp_output, mocked_geocoder):
    out = tmp_output / "gis_out"
    out.mkdir()
    files = GIS_pipeline_util.GIS_pipeline(
        "NLP_default_IO_config.csv",
        str(locations_input),
        "",
        str(out),
        "Nominatim",
        "Google Earth Pro",  # kml only: produced offline via simplekml
        "No charts",
        "No transformation",
        True,  # datePresent (re-derived from the Date header anyway)
        "",  # country_bias
        "",  # area_var
        False,  # restrict
        "Location",
        "utf-8",
        0,
        1,
        [""],
        [""],
        ["Pushpins"],
        ["red"],
        [0],
        ["1"],
        [0],
        [""],
        [1],
        [1],
    )
    assert files, "expected the GIS pipeline to return output files"
    geocoded = [f for f in output_csvs(out) if "geo-Nom" in f and "not-found" not in f.lower()]
    assert len(geocoded) == 1
    rows = read_rows(geocoded[0])
    assert [r["Location"] for r in rows] == ["Rome", "Paris"]
    for r in rows:
        assert float(r["Latitude"]) == pytest.approx(41.9)
        assert float(r["Longitude"]) == pytest.approx(12.5)
        assert r["Country from Geocoder"] == "Italy"
    kmls = list(pathlib.Path(out).rglob("*.kml"))
    assert len(kmls) == 1


# run_GIS endpoint paths -------------------------------------------------------


def _run_gis(tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir="",
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        csv_file="",
        NER_extractor=False,
        location_menu="Location",
        geocoder="Nominatim",
        geocode_locations=False,
        country_bias_var="",
        area_var="e.g.,",  # placeholder skips the bounding-box validation
        restrict_var=False,
        map_locations="",
        GIS_package_var="",
        GIS_package2_var="",
    )
    args.update(kwargs)
    return run_GIS(**args)


def test_run_gis_no_package_returns_none(tiny_corpus, tmp_output):
    assert _run_gis(tmp_output, inputDir=str(tiny_corpus)) is None
    assert output_csvs(tmp_output) == []


def test_run_gis_csv_input_path_is_broken(locations_input, tmp_output, mocked_geocoder):
    # run_GIS passes the placeholder string 'NER_StanfordCoreNLP_output' to
    # GIS_pipeline instead of the csv file, so the csv input path silently does
    # nothing even with a working geocoder; see TECH_DEBT.md
    out = tmp_output / "run_gis_out"
    out.mkdir()
    result = _run_gis(out, csv_file=str(locations_input), GIS_package_var="Google Earth Pro")
    assert result is None
    assert [f for f in output_csvs(out) if "geo-Nom" in f] == []


# integration -----------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("NLP_SUITE_TEST_NETWORK"),
    reason="geocodes via the live Nominatim service; set NLP_SUITE_TEST_NETWORK=1 to run",
)
@pytest.mark.xfail(
    reason="GIS_geocode_util.geocode:688 raises UnboundLocalError on 'date' when the "
    "input has no Date column, breaking the whole no-date /gis NER path; see TECH_DEBT.md",
    raises=UnboundLocalError,
)
def test_run_gis_ner_extractor_nominatim(locations_txt, tmp_output, corenlp_running):
    files = _run_gis(
        tmp_output,
        inputDir=str(locations_txt),
        NER_extractor=True,
        GIS_package_var="Google Earth Pro",
    )
    assert files, "expected GIS outputs from the NER + Nominatim pipeline"
    geocoded = [f for f in output_csvs(tmp_output) if "geo-Nom" in f and "not-found" not in f.lower()]
    assert geocoded
    rows = read_rows(geocoded[0])
    assert {r["Location"] for r in rows} >= {"Rome", "Paris"}
