"""GIS: the "(NER tag: ...)" log line names the tag the geocoder actually uses.

A csv of locations with dates comes in as [location, date, NER tag, sentence, document]; without dates,
[location, NER tag, sentence, document]; a CoNLL table always has the tag in column 1. The log line printed
column 1 in every case, so a dated csv logged "Processing location ... (NER tag: 1893-04-12)" while the
geocoder used column 2.

GIS_geocode_util imports the GUI, so the helper is pulled out of the source and run on its own.
"""

import ast
import os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _load(name):
    source = open(os.path.join(SRC, "GIS_geocode_util.py"), encoding="utf-8-sig").read()
    namespace = {}
    for node in ast.parse(source).body:
        if getattr(node, "name", None) == name:
            exec(ast.get_source_segment(source, node), namespace)
    return namespace[name]


location_NER_tag = _load("location_NER_tag")


def test_a_csv_with_dates_has_the_tag_after_the_date():
    item = ["Chicago", "1893-04-12", "CITY", "A sentence.", "doc.txt"]
    assert location_NER_tag(item, inputIsCoNLL=False, datePresent=True) == "CITY"


def test_a_csv_without_dates_has_the_tag_second():
    item = ["Chicago", "CITY", "A sentence.", "doc.txt"]
    assert location_NER_tag(item, inputIsCoNLL=False, datePresent=False) == "CITY"


def test_a_conll_table_has_the_tag_second_even_with_dates():
    item = ["Chicago", "CITY", 3, "A sentence.", 1, "doc.txt", "1893-04-12"]
    assert location_NER_tag(item, inputIsCoNLL=True, datePresent=True) == "CITY"
