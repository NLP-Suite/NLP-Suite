"""Two kinds of place, told apart.

The old paragraph ran them together: "328 distinct places; the most frequent are the Great Hall
(229), Gryffindor Tower (98) ... The top 40 were geocoded". Both halves misled. The most-named
places in that corpus have no coordinates and never will - the Great Hall is a KIND of space, which
is what the symbolic analysis is for - and the top 40 were not geocoded: 15 were.
"""
import importlib.util
import os
import sys

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)


@pytest.fixture(scope='module')
def prof():
    """The profiler with the REAL pandas in place for the whole file.

    conftest stubs pandas, and _interp_spatial imports it lazily inside the call - so a stub would
    make every reading return None and every test here pass vacuously. Note that a MagicMock answers
    hasattr(pandas, 'DataFrame') with True, which is why the check below asks for something a mock
    cannot fake. The stub is restored when the file is done.
    """
    roots = ('pandas', 'numpy')
    saved = {k: v for k, v in sys.modules.items()
             if k in roots or k.startswith(tuple(r + '.' for r in roots))}

    def _drop():
        for k in [k for k in list(sys.modules)
                  if k in roots or k.startswith(tuple(r + '.' for r in roots))]:
            del sys.modules[k]

    _drop()
    try:
        import pandas
        # a MagicMock would sail past hasattr; a real DataFrame has real columns
        if list(pandas.DataFrame({'Location': ['x']}).columns) != ['Location']:
            raise ImportError('pandas is the stub')
    except Exception as exc:
        _drop()
        sys.modules.update(saved)
        pytest.skip('real pandas not available: %s' % exc)

    spec = importlib.util.spec_from_file_location(
        '_prof_spatial', os.path.join(_SRC, 'corpus_profiler_util.py'))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        _drop()
        sys.modules.update(saved)
        pytest.skip('could not load the profiler against real pandas: %s' % exc)
    finally:
        os.chdir(cwd)

    yield mod
    _drop()
    sys.modules.update(saved)


@pytest.fixture
def typology(monkeypatch):
    """A typology of our own, so these tests measure the SPLIT rather than WordNet.

    The real one classifies "the Great Hall" through its last token, hall -> room -> a
    domestic_interior anchor, which is a WordNet climb; conftest stubs nltk, so under test the real
    typology classifies nothing and every place would look unresolved. What belongs here is whether
    _interp_spatial reports a classified place separately from a mapped one - the typology has its
    own tests.
    """
    import types
    fake = types.ModuleType('GIS_symbolic_typology_util')
    fake.UNCLASSIFIED = 'unclassified'

    def classify(word, **kw):
        w = str(word).lower()
        if 'hall' in w:
            return 'domestic_interior'
        if 'tower' in w:
            return 'tower_height'
        if 'forest' in w:
            return 'wild_forest'
        return 'unclassified'

    fake.classify = classify
    monkeypatch.setitem(sys.modules, 'GIS_symbolic_typology_util', fake)
    return fake


def _tracking(tmp_path, rows, name='NLP_NER_entity_location_tracking.csv'):
    p = tmp_path / name
    lines = ['Entity,Location,Sentence ID']
    for entity, place, n in rows:
        for i in range(n):
            lines.append('%s,%s,%d' % (entity, place, i))
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return str(p)


def _map(tmp_path, plotted):
    p = tmp_path / 'NLP_locations_Location_map.html'
    body = ''.join('<div>%s: %d</div>' % (name, n) for name, n in plotted)
    p.write_text('<html><body>%s</body></html>' % body, encoding='utf-8')
    return str(p)


class TestTheSplit:
    def test_a_kind_of_space_is_not_reported_as_geocoded(self, prof, typology, tmp_path):
        """the Great Hall has no coordinates and never will."""
        files = [_tracking(tmp_path, [('Harry', 'the Great Hall', 20), ('Harry', 'London', 5)]),
                 _map(tmp_path, [('London', 5)])]
        text = ' '.join(prof._interp_spatial(files))
        assert 'the Great Hall' in text
        assert 'KIND of space' in text
        # the sentence naming what was mapped must not be the one naming the Great Hall
        mapped_sentence = [s for s in prof._interp_spatial(files) if 'resolved to coordinates' in s]
        assert mapped_sentence and 'Great Hall' not in mapped_sentence[0]

    def test_it_reports_what_was_MAPPED_not_how_many_were_sent(self, prof, tmp_path):
        """"The top 40 were geocoded" was false; the geocoder resolved a fraction of them."""
        rows = [('Harry', 'Place%02d' % i, 3) for i in range(40)]
        files = [_tracking(tmp_path, rows), _map(tmp_path, [('Place01', 3), ('Place02', 3)])]
        out = prof._interp_spatial(files)
        mapped = [s for s in out if 'resolved to coordinates' in s]
        assert mapped, out
        assert mapped[0].startswith('2 places')
        assert '40' not in mapped[0]

    def test_unresolved_places_are_counted_separately(self, prof, tmp_path):
        files = [_tracking(tmp_path, [('Harry', 'Hogsmeade', 9), ('Harry', 'London', 4)]),
                 _map(tmp_path, [('London', 4)])]
        text = ' '.join(prof._interp_spatial(files))
        assert 'Hogsmeade' in text
        assert 'no coordinates to find' in text

    def test_the_totals_add_up(self, prof, tmp_path):
        files = [_tracking(tmp_path, [('Harry', 'the Great Hall', 7), ('Harry', 'London', 4),
                                      ('Harry', 'Hogsmeade', 2)]),
                 _map(tmp_path, [('London', 4)])]
        out = prof._interp_spatial(files)
        assert out[0].startswith('The corpus names 3 distinct places')

    def test_no_location_table_says_nothing(self, prof, tmp_path):
        p = tmp_path / 'other.csv'
        p.write_text('A,B\n1,2\n', encoding='utf-8')
        assert prof._interp_spatial([str(p)]) == []


class TestItPicksTheRightTable:
    def test_the_richest_location_table_wins(self, prof, tmp_path):
        """The dimension also carries a top-40 subset written for the movement map. Reading that
        one reported "40 distinct places" for a corpus that names far more."""
        full = _tracking(tmp_path, [('Harry', 'Place%02d' % i, 2) for i in range(30)],
                         name='full_tracking.csv')
        subset = _tracking(tmp_path, [('Harry', 'Place%02d' % i, 2) for i in range(5)],
                           name='top40_subset.csv')
        out = prof._interp_spatial([subset, full])
        assert out[0].startswith('The corpus names 30 distinct places')

    def test_a_summary_table_counts_MENTIONS_not_rows(self, prof, tmp_path):
        """The summary table is one row per entity-place pair with the mentions in a Count column.
        Counting rows there reported the Great Hall at 69 when it is named 229 times."""
        p = tmp_path / 'NLP_entity_location_summary.csv'
        p.write_text('Entity,Location,Count\n'
                     'Harry,the Great Hall,100\n'
                     'Ron,the Great Hall,129\n'
                     'Harry,London,73\n', encoding='utf-8')
        text = ' '.join(prof._interp_spatial([str(p)]))
        assert '(229)' in text, text


class TestTheAmbiguousPins:
    def test_a_place_that_is_also_a_character_is_flagged(self, prof, tmp_path):
        """A geocoder answers the name it is given. Montague is a Quidditch player here and a town
        in Michigan; the pin looks as authoritative as London's."""
        files = [_tracking(tmp_path, [('Montague', 'London', 6), ('Harry', 'Montague', 5)]),
                 _map(tmp_path, [('London', 6), ('Montague', 5)])]
        text = ' '.join(prof._interp_spatial(files))
        assert 'Montague' in text
        assert 'character name' in text

    def test_a_flagged_pin_does_not_lead_the_headline_list(self, prof, tmp_path):
        """It would be the first thing quoted, and it is the least trustworthy."""
        files = [_tracking(tmp_path, [('Montague', 'London', 3), ('Harry', 'Montague', 50)]),
                 _map(tmp_path, [('London', 3), ('Montague', 50)])]
        mapped = [s for s in prof._interp_spatial(files) if 'resolved to coordinates' in s]
        assert mapped
        assert 'the most mentioned are London' in mapped[0]

    def test_nothing_ambiguous_means_no_warning(self, prof, tmp_path):
        files = [_tracking(tmp_path, [('Harry', 'London', 4)]), _map(tmp_path, [('London', 4)])]
        text = ' '.join(prof._interp_spatial(files))
        assert 'character name' not in text
