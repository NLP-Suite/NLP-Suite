# Social-actor typology: what KIND of person is acting.
#
# The sibling of GIS_symbolic_typology_util, which classifies the SPACE. That one
# answers "what kind of place is this?"; this one answers "what kind of person is
# this?" — which is the attribute the STATIC (distribution) analysis crosses
# against space, and which the user was previously told to code by hand.
#
# Two passes, exactly as the space typology does it:
#   1. exact lookup in lib/social_actor_typology.csv (hand-curated, editable), then
#   2. a WordNet hypernym-path fallback (walk a word's ancestors; if an anchor
#      synset for a category is on the path, assign that category).
#
# It classifies COMMON NOUNS — "the sheriff", "a farmer", "the mob". It cannot
# classify a PROPER NAME: WordNet does not know that Harry is a schoolboy. Named
# characters are handled by naming them in the CSV (a corpus has few of them,
# however many documents it has) or, for real people in historical corpora, by
# the DBpedia / YAGO annotators.
#
# Deliberately GUI-free (no GUI_util / install guard) so it is importable and
# unit-testable on its own.

import csv
import os

CATEGORIES = [
    'kin_family', 'child_youth', 'laborer', 'professional', 'authority_official',
    'military_police', 'clergy', 'merchant_trade', 'elite_landowner',
    'crowd_collective', 'criminal_accused', 'generic_person',
]

# WordNet anchor synsets per category, used only for the hypernym fallback (words
# not present in the curated lexicon). Conservative on purpose: a wrong social
# type is worse than none, because it becomes a cell in a crosstab.
_ANCHORS = {
    'kin_family':         ['relative.n.01', 'parent.n.01', 'spouse.n.01', 'sibling.n.01'],
    'child_youth':        ['child.n.01', 'juvenile.n.01'],
    'laborer':            ['worker.n.01', 'laborer.n.01', 'peasant.n.01', 'servant.n.01',
                           'slave.n.01'],
    'professional':       ['professional.n.01', 'health_professional.n.01',
                           'educator.n.01', 'intellectual.n.01'],
    'authority_official': ['official.n.01', 'head_of_state.n.01', 'administrator.n.01',
                           'magistrate.n.01', 'legislator.n.01'],
    'military_police':    ['serviceman.n.01', 'lawman.n.01', 'military_officer.n.01'],
    'clergy':             ['clergyman.n.01', 'religious_person.n.01'],
    'merchant_trade':     ['merchant.n.01', 'businessman.n.01', 'trader.n.01'],
    'elite_landowner':    ['aristocrat.n.01', 'landowner.n.01', 'capitalist.n.02'],
    'crowd_collective':   ['gathering.n.01', 'social_group.n.01'],
    'criminal_accused':   ['criminal.n.01', 'wrongdoer.n.01', 'prisoner.n.01'],
}

# Person words too generic to be a social TYPE. They are people, so the WordNet
# fallback would happily file them under whatever ancestor it meets first; they
# carry no social information and belong in their own bucket.
_GENERIC = {
    'man', 'woman', 'men', 'women', 'person', 'people', 'boy', 'girl', 'one',
    'someone', 'somebody', 'anyone', 'anybody', 'everyone', 'everybody', 'no one',
    'nobody', 'they', 'other', 'others', 'individual', 'human', 'being', 'folk',
    'folks', 'party', 'figure', 'fellow', 'guy', 'body', 'soul', 'creature',
}

UNCLASSIFIED = 'unclassified'

_lexicon_cache = None


def _default_lexicon_path():
    """lib/social_actor_typology.csv, via GUI_IO_util.libPath when available."""
    try:
        import GUI_IO_util
        return os.path.join(GUI_IO_util.libPath, 'social_actor_typology.csv')
    except Exception:
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(repo, 'lib', 'social_actor_typology.csv')


def load_lexicon(path=None):
    """Return {term: category} from the typology CSV. Cached when path is default."""
    global _lexicon_cache
    if path is None and _lexicon_cache is not None:
        return _lexicon_cache
    p = path or _default_lexicon_path()
    lex = {}
    if os.path.isfile(p):
        try:
            with open(p, encoding='utf-8-sig', newline='') as fh:
                for row in csv.DictReader(fh):
                    term = str(row.get('term', '')).strip().lower()
                    category = str(row.get('category', '')).strip()
                    if term and category:
                        lex[term] = category
        except OSError:
            pass
    if path is None:
        _lexicon_cache = lex
    return lex


def _wordnet_category(word):
    """Climb *word*'s hypernyms; return the category whose anchor is on the path."""
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        return UNCLASSIFIED
    try:
        synsets = wn.synsets(word, pos=wn.NOUN)
    except Exception:
        return UNCLASSIFIED
    if not synsets:
        return UNCLASSIFIED

    anchors = {}
    for category, names in _ANCHORS.items():
        for name in names:
            try:
                anchors[wn.synset(name)] = category
            except Exception:
                continue

    # the first sense only: later senses of a common word wander far from the
    # reading a narrative intends ("minister" -> diplomat, "mother" -> abbess)
    seen, frontier = set(), [synsets[0]]
    for _ in range(12):                      # WordNet's person hierarchy is shallow
        nxt = []
        for syn in frontier:
            if syn in anchors:
                return anchors[syn]
            if syn in seen:
                continue
            seen.add(syn)
            nxt.extend(syn.hypernyms())
        if not nxt:
            break
        frontier = nxt
    return UNCLASSIFIED


def classify(actor, pos=''):
    """The social type of *actor*, or UNCLASSIFIED.

    *pos* is the actor's part of speech when known. A PROPER NOUN is never
    classified here: WordNet has no entry for Harry, and guessing from a first
    name would be worse than saying nothing. Name those in the CSV instead.
    """
    if str(pos).strip().upper() in ('PROPN', 'NNP', 'NNPS'):
        return UNCLASSIFIED
    word = str(actor or '').strip().lower()
    if not word:
        return UNCLASSIFIED
    lexicon = load_lexicon()
    if word in lexicon:                       # the curated list wins, always
        return lexicon[word]
    if word in _GENERIC:
        return 'generic_person'
    return _wordnet_category(word)


def classify_series(actors, positions=None):
    """Classify many actors at once, one WordNet climb per DISTINCT word.

    A corpus has thousands of rows and a few hundred distinct actors; classifying
    row by row would climb the same hypernyms thousands of times.
    """
    positions = list(positions) if positions is not None else [''] * len(list(actors))
    actors = list(actors)
    cache = {}
    out = []
    for actor, pos in zip(actors, positions):
        key = (str(actor).strip().lower(), str(pos).strip().upper())
        if key not in cache:
            cache[key] = classify(actor, pos)
        out.append(cache[key])
    return out
