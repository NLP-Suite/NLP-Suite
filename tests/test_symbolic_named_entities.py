"""A real, geocodable place is not a KIND of space.

"London appears many times as symbolic space. It shouldn't." London is a city with coordinates -
GIS_main's business. It reached the symbolic table because WordNet files real people and places as
INSTANCES of a class, and hypernym_paths() walks straight through the instance link: london ->
(instance of) city -> municipality, which is the market_public anchor.

It was never only London. On the 5,228-event Harry Potter table the same path let in Ogden, Cairo,
Aberdeen, Firenze, the river James, and - because WordNet knows them as US place names - the
ordinary words snake, twin, boulder, bend, white, angel, male and reading.

The guard skips INSTANCE synsets. It must not cost the common nouns that names are built from:
the Great HALL, the Astronomy TOWER, the Forbidden FOREST all still classify, because hall, tower
and forest are classes in WordNet, not instances.
"""
import importlib.util
import os
import sys
import types

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')


def _load():
    """Load the typology fresh, so a test can install its own fake WordNet first."""
    spec = importlib.util.spec_from_file_location(
        '_typ_named_entities', os.path.join(_SRC, 'GIS_symbolic_typology_util.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Syn:
    """The two WordNet relations that matter here, and nothing else.

    A CLASS synset has hypernyms and no instance_hypernyms; an INSTANCE (a named entity) has
    instance_hypernyms. hypernym_paths() reproduces WordNet's own behaviour of walking through
    the instance link - which is exactly what let London in.
    """

    def __init__(self, name, parent=None, instance_of=None):
        self._name, self._parent, self._instance_of = name, parent, instance_of

    def name(self):
        return self._name

    def hypernyms(self):
        return [self._parent] if self._parent else []

    def instance_hypernyms(self):
        return [self._instance_of] if self._instance_of else []

    def hypernym_paths(self):
        up = self._parent or self._instance_of
        if not up:
            return [[self]]
        return [path + [self] for path in up.hypernym_paths()]


def _fake_wordnet():
    """municipality <- city <- (instance) london, and municipality <- city <- town as a class."""
    municipality = _Syn('municipality.n.01')          # the market_public anchor
    city = _Syn('city.n.01', parent=municipality)
    town = _Syn('town.n.01', parent=municipality)     # a common noun: must still classify
    london = _Syn('london.n.01', instance_of=city)    # a named entity: must not
    ogden = _Syn('ogden.n.01', instance_of=city)

    room = _Syn('room.n.01')                          # the domestic_interior anchor
    hall = _Syn('hall.n.01', parent=room)             # "the Great Hall" - a class, keep it

    table = {'london': [london], 'ogden': [ogden], 'town': [town], 'hall': [hall],
             'city': [city]}

    wn = types.SimpleNamespace(
        NOUN='n',
        synsets=lambda w, pos=None: table.get(str(w).lower(), []),
        synset=lambda n: {'municipality.n.01': municipality, 'city.n.01': city,
                          'room.n.01': room}[n],
    )
    corpus = types.ModuleType('nltk.corpus')
    corpus.wordnet = wn
    nltk = types.ModuleType('nltk')
    nltk.corpus = corpus
    return {'nltk': nltk, 'nltk.corpus': corpus}


class TestTheInstanceGuard:
    def setup_method(self):
        self._saved = {k: sys.modules.get(k) for k in ('nltk', 'nltk.corpus')}
        sys.modules.update(_fake_wordnet())
        self.typ = _load()
        # an empty curated lexicon, so every answer below comes from the WordNet fallback
        self.lex = {}

    def teardown_method(self):
        for k, v in self._saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v

    def _cat(self, word):
        return self.typ.classify(word, lexicon=self.lex)

    def test_London_is_not_a_kind_of_space(self):
        assert self._cat('London') == self.typ.UNCLASSIFIED

    def test_lower_case_london_is_refused_too(self):
        """A real city is GIS_main's business whatever the capitalisation - and the classifier
        lower-cases the word before it looks anything up, so capitalisation was never the signal."""
        assert self._cat('london') == self.typ.UNCLASSIFIED

    def test_another_instance_of_the_same_class_is_refused(self):
        assert self._cat('Ogden') == self.typ.UNCLASSIFIED

    def test_a_common_noun_under_that_very_same_anchor_still_classifies(self):
        """The guard has to be about instance-ness, not about the anchor: town reaches
        municipality by an ordinary hypernym and must keep its category."""
        assert self._cat('town') == 'market_public'

    def test_the_common_noun_inside_a_proper_name_still_classifies(self):
        """"the Great Hall" is capitalised, but hall is a class in WordNet, so the symbolic
        reading of the place survives."""
        assert self._cat('Hall') == 'domestic_interior'

    def test_a_word_wordnet_has_never_heard_of_is_unclassified(self):
        assert self._cat('Hogwarts') == self.typ.UNCLASSIFIED

    def test_the_curated_lexicon_still_wins_over_the_guard(self):
        """If somebody deliberately puts a named place in the CSV, that is a research decision and
        it must be honoured - the guard only governs the WordNet fallback."""
        assert self.typ.classify('London', lexicon={'london': 'market_public'}) == 'market_public'


class TestAgainstRealWordNet:
    """The fake above proves the rule; these prove the rule matches the WordNet actually shipped.

    Skipped wherever nltk or the wordnet corpus is unavailable (CI stubs the heavy libraries), so
    this file still passes there on the strength of the tests above.
    """

    def setup_method(self):
        import pytest
        try:
            from nltk.corpus import wordnet as wn
            wn.synsets('london', pos=wn.NOUN)
        except Exception:
            pytest.skip('real WordNet not available')
        for k in list(sys.modules):
            if k == 'nltk' or k.startswith('nltk.'):
                if isinstance(getattr(sys.modules[k], '__file__', None), str) is False:
                    pytest.skip('nltk is stubbed')
        self.typ = _load()

    def test_the_place_names_that_were_leaking_in_are_gone(self):
        for word in ('London', 'Ogden', 'Cairo', 'Aberdeen', 'Firenze'):
            assert self.typ.classify(word) == self.typ.UNCLASSIFIED, word

    def test_the_ordinary_words_that_are_also_US_place_names_are_gone(self):
        """snake, boulder, reading, male: WordNet knows each as a town or a river, and each was
        being counted as a kind of narrative space."""
        for word in ('snake', 'boulder', 'reading', 'male', 'bend', 'angel'):
            assert self.typ.classify(word) == self.typ.UNCLASSIFIED, word

    def test_every_real_space_word_is_untouched(self):
        expected = {'hall': 'domestic_interior', 'tower': 'tower_height',
                    'forest': 'wild_forest', 'room': 'domestic_interior',
                    'chamber': 'domestic_interior', 'castle': 'royal_court',
                    'street': 'market_public', 'hill': 'wild_forest', 'wood': 'wild_forest',
                    'kitchen': 'domestic_interior', 'church': 'sacred', 'town': 'market_public',
                    'river': 'water_passage', 'cellar': 'subterranean',
                    'door': 'threshold_liminal'}
        for word, want in expected.items():
            assert self.typ.classify(word) == want, word
