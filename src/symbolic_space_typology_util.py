# Written by Roberto Franzosi & Claude, 2026
# Spatial-domain typology for the Narrative / Symbolic Space Analyzer
# (see docs/Narrative_Symbolic_Space_design.md).
#
# Classifies a location noun into a symbolic SPACE TYPE (domestic/interior,
# field/labor, wild/forest, threshold/liminal, royal/court, sacred,
# market/public, water/passage) rather than a lat/long. This is the counterpart
# to geographic geocoding: places that do NOT resolve to a map coordinate
# (kitchen, forest, castle) are the ones this typology is for.
#
# Two-step classification:
#   1. exact lookup in lib/symbolic_space_typology.csv (hand-curated), then
#   2. a WordNet hypernym-path fallback (walk a word's ancestors; if any anchor
#      synset for a category is on the path, assign that category).
#
# Deliberately GUI-free (no GUI_util / install guard) so it is importable and
# unit-testable on its own; the GUI/main modules that use it carry the guard.

import csv
import os

CATEGORIES = [
    'domestic_interior', 'field_labor', 'wild_forest', 'threshold_liminal',
    'royal_court', 'sacred', 'market_public', 'water_passage',
]

# WordNet anchor synsets per category, used only for the hypernym fallback
# (words not present in the curated lexicon). Kept conservative on purpose.
_ANCHORS = {
    'domestic_interior': ['room.n.01', 'dwelling.n.01', 'house.n.01', 'housing.n.01'],
    'field_labor':       ['tract.n.01', 'farm.n.01', 'field.n.01'],
    'wild_forest':       ['forest.n.01', 'wood.n.01', 'geological_formation.n.01'],
    'royal_court':       ['castle.n.02', 'palace.n.01'],
    'sacred':            ['place_of_worship.n.01', 'religious_residence.n.01'],
    'market_public':     ['mercantile_establishment.n.01', 'municipality.n.01'],
    'water_passage':     ['body_of_water.n.01', 'way.n.06'],
    # threshold_liminal is hard to anchor cleanly in WordNet; rely on the lexicon.
}

UNCLASSIFIED = 'unclassified'

_lexicon_cache = None


def _default_lexicon_path():
    """lib/symbolic_space_typology.csv, via GUI_IO_util.libPath when available."""
    try:
        import GUI_IO_util
        return os.path.join(GUI_IO_util.libPath, 'symbolic_space_typology.csv')
    except Exception:
        # Fallback: <repo>/lib next to this file's src/ folder.
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(repo, 'lib', 'symbolic_space_typology.csv')


def load_lexicon(path=None):
    """Return {term: category} from the typology CSV. Cached when path is default."""
    global _lexicon_cache
    if path is None and _lexicon_cache is not None:
        return _lexicon_cache
    p = path or _default_lexicon_path()
    lex = {}
    if os.path.isfile(p):
        with open(p, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                term = (row.get('term') or '').strip().lower()
                cat = (row.get('category') or '').strip()
                if term and cat:
                    lex[term] = cat
    if path is None:
        _lexicon_cache = lex
    return lex


def _wordnet_category(word):
    """Category from the first anchor synset found on any hypernym path, or None."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return None
    anchor_to_cat = {name: cat for cat, names in _ANCHORS.items() for name in names}
    try:
        synsets = wn.synsets(word, pos=wn.NOUN)
    except Exception:
        return None
    for syn in synsets:
        for path in syn.hypernym_paths():
            for hyp in reversed(path):  # most specific first
                cat = anchor_to_cat.get(hyp.name())
                if cat:
                    return cat
    return None


def classify(word, lexicon=None, use_wordnet=True):
    """Return the space category for *word*, or 'unclassified'.

    Order: exact lexicon hit -> last-token hit (e.g. 'throne room' -> 'room')
    -> WordNet hypernym fallback -> unclassified.
    """
    if not word:
        return UNCLASSIFIED
    w = str(word).strip().lower()
    if not w:
        return UNCLASSIFIED
    lex = lexicon if lexicon is not None else load_lexicon()
    if w in lex:
        return lex[w]
    if ' ' in w:
        last = w.split()[-1]
        if last in lex:
            return lex[last]
    if use_wordnet:
        cat = _wordnet_category(w)
        if cat:
            return cat
    return UNCLASSIFIED
