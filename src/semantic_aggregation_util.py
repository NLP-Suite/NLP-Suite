# Semantic Aggregation dispatcher (WordNet / VerbNet / FrameNet).
#
# WordNet aggregation (hierarchical: climb to anchor synsets / supersenses) lives in
# semantic_aggregation_WordNet_util. VerbNet (verb classes) and FrameNet (frames) are FLAT
# membership look-ups via NLTK, handled here. The hub (semantic_aggregation_main) calls aggregate()
# and the Knowledge base dropdown chooses the resource ('*' = all applicable).

import sys

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "semantic_aggregation",
                                                 ['os', 're', 'csv', 'tkinter', 'nltk', 'pandas']) == False:
    sys.exit(0)

import os
import re
import csv
import tkinter.messagebox as mb
from collections import defaultdict

import charts_util
import IO_user_interface_util
import GUI_IO_util
import semantic_aggregation_WordNet_util as wn_util


# ---- KB-aware category lists for the GUI picker (WordNet top synsets / VerbNet classes / FrameNet frames) ----

_WORDNET_TOP_NOUN = ('act', 'animal', 'artifact', 'attribute', 'body', 'cognition', 'communication', 'event',
                     'feeling', 'food', 'group', 'location', 'motive', 'object', 'person', 'phenomenon', 'plant',
                     'possession', 'process', 'quantity', 'relation', 'shape', 'state', 'substance', 'time')
_WORDNET_TOP_VERB = ('body', 'change', 'cognition', 'communication', 'competition', 'consumption', 'contact',
                     'creation', 'emotion', 'motion', 'perception', 'possession', 'social', 'stative', 'weather')
_category_cache = {}


def _categories_from_csv_or_nltk(filename, nltk_fn):
    """Read the first column of lib/<filename> (the reference list that backs the dropdown);
    if the csv is missing, fall back to computing the list from NLTK so the picker never comes up empty."""
    if filename in _category_cache:
        return _category_cache[filename]
    vals = []
    try:
        with open(os.path.join(GUI_IO_util.libPath, filename), encoding='utf-8') as f:
            rdr = csv.reader(f)
            next(rdr, None)  # header
            vals = [row[0] for row in rdr if row and row[0].strip()]
    except Exception:
        vals = []
    if not vals:
        try:
            vals = nltk_fn()
        except Exception:
            vals = []
    _category_cache[filename] = vals
    return vals


def _vn_classes():
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/verbnet', 'verbnet')
    from nltk.corpus import verbnet as vn
    return sorted(vn.classids())


def _fn_frames():
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/framenet_v17', 'framenet_v17')
    from nltk.corpus import framenet as fn
    return sorted((f.name for f in fn.frames()), key=str.lower)


def get_categories(knowledge_base, noun_verb):
    """Categories to list in the KB-aware picker dropdown: WordNet top synsets (by NOUN/VERB),
    the 429 VerbNet classes, or the 1,221 FrameNet frames."""
    kb = knowledge_base or 'WordNet'
    if kb == 'VerbNet':
        return _categories_from_csv_or_nltk('VerbNet_classes.csv', _vn_classes)
    if kb == 'FrameNet':
        return _categories_from_csv_or_nltk('FrameNet_frames.csv', _fn_frames)
    return list(_WORDNET_TOP_NOUN if noun_verb == 'NOUN' else _WORDNET_TOP_VERB)


def _read_word_list(inputFile):
    import pandas as pd
    data = pd.read_csv(inputFile, encoding='utf-8', on_bad_lines='skip')
    if data.shape[1] == 0:
        return []
    return [str(w).strip() for w in data.iloc[:, 0].dropna().unique().tolist() if str(w).strip()]


def _aggregate_flat(resource, category_fn, inputFile, outputDir, noun_verb, chartPackage, dataTransformation):
    """Shared writer for the FLAT (membership) resources. category_fn(lemma) -> category string.
    Writes a Word/category csv + a frequency csv + a frequency chart; returns the output files."""
    filesToOpen = []
    words = _read_word_list(inputFile)
    fileName = os.path.basename(inputFile).split('.')[0]
    cat_col = resource + ' category'
    csv1 = os.path.join(outputDir, "NLP_%s_UP_%s_%s.csv" % (resource, noun_verb, fileName))
    csv2 = os.path.join(outputDir, "NLP_%s_UP_%s_%s_frequency.csv" % (resource, noun_verb, fileName))
    rows = []
    counts = defaultdict(int)
    not_found = 0
    for w in words:
        cat = category_fn(w.lower()) or 'Not found'
        if cat == 'Not found':
            not_found += 1
        counts[cat] += 1
        rows.append({'Word': w, cat_col: cat})
    if not rows or all(r[cat_col] == 'Not found' for r in rows):
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
            "%s %s aggregation.\n\n%s found none of the %s in the input csv file\n%s."
            % (resource, noun_verb, resource, noun_verb, inputFile))
        return filesToOpen
    if not_found > 0:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Aggregation results',
            "%s %s aggregation.\n\n%d of %d word(s) were classified into %s categories; %d were not found (labelled 'Not found')."
            % (resource, noun_verb, len(words) - not_found, len(words), resource, not_found))
    with open(csv1, 'w', encoding='utf-8', newline='') as f:
        wtr = csv.DictWriter(f, fieldnames=['Word', cat_col]); wtr.writeheader(); wtr.writerows(rows)
    with open(csv2, 'w', encoding='utf-8', newline='') as f:
        wtr = csv.DictWriter(f, fieldnames=[cat_col, 'Frequency']); wtr.writeheader()
        for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
            wtr.writerow({cat_col: cat, 'Frequency': n})
    filesToOpen += [csv1, csv2]
    if chartPackage and chartPackage != 'No charts':
        of = charts_util.plot(csv1, outputDir, columns=[cat_col], title='Frequency of %s categories for %s' % (resource, noun_verb), x_label='%s %s category' % (resource, noun_verb), group_by=None)
        if of:
            filesToOpen.extend(of if isinstance(of, list) else [of])
    return filesToOpen


def aggregate_VerbNet(inputFile, outputDir, noun_verb, chartPackage, dataTransformation):
    """Aggregate a list of VERBS to their VerbNet class (the first/most-basic class per lemma).
    NOTE: bare lemmas are polysemous (e.g. 'hang' is in several classes); this takes the first."""
    if noun_verb != 'VERB':
        mb.showwarning(title="VerbNet",
                       message="VerbNet classifies VERBS only - it has no nouns.\n\nPlease select VERB "
                               "as the Lexical category for the VerbNet knowledge base.")
        return []
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/verbnet', 'verbnet')
    from nltk.corpus import verbnet as vn
    start = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
        'Started running VerbNet aggregation at', True, '', True)
    def cat(lemma):
        ids = vn.classids(lemma=lemma)
        return ids[0] if ids else 'Not found'
    out = _aggregate_flat('VerbNet', cat, inputFile, outputDir, noun_verb, chartPackage, dataTransformation)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
        'Finished running VerbNet aggregation at', True, '', True, start)
    return out


# Cached FrameNet lemma index, built once per process: {(lemma_lower, pos): {frame names}}. The OLD
# aggregate_FrameNet called fn.lus(regex) PER lemma, and fn.lus(pattern) regex-scans all ~13,000
# lexical units every time -- O(lemmas x 13k), which is why FrameNet was minutes while WordNet/VerbNet
# were seconds. Building this index is a single pass over FrameNet's frames; every lookup is then O(1).
_FRAMENET_LEMMA_INDEX = None


def _framenet_lemma_index(fn):
    global _FRAMENET_LEMMA_INDEX
    if _FRAMENET_LEMMA_INDEX is None:
        idx = {}
        for frame in fn.frames():                       # one pass over all frames
            fname = frame.name
            for lu_name in frame.lexUnit:               # keys look like 'run.v', 'give up.v', 'dog.n'
                lemma, _sep, p = lu_name.rpartition('.')
                if p:
                    idx.setdefault((lemma.lower(), p.lower()), set()).add(fname)
        _FRAMENET_LEMMA_INDEX = idx
    return _FRAMENET_LEMMA_INDEX


def aggregate_FrameNet(inputFile, outputDir, noun_verb, chartPackage, dataTransformation):
    """Aggregate a list of nouns or verbs to their FrameNet frame (the first frame per lemma+POS).
    NOTE: bare lemmas are polysemous; this takes the first frame."""
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/framenet_v17', 'framenet_v17')
    from nltk.corpus import framenet as fn
    pos = 'v' if noun_verb == 'VERB' else 'n'
    start = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
        'Started running FrameNet aggregation at', True, '', True)
    index = _framenet_lemma_index(fn)   # built once; the set of frames whose LU is 'lemma.pos' matches
    def cat(lemma):                     # exactly what fn.lus(^lemma\.pos$) returned, just precomputed
        frames = index.get((str(lemma).lower(), pos))
        return sorted(frames)[0] if frames else 'Not found'
    out = _aggregate_flat('FrameNet', cat, inputFile, outputDir, noun_verb, chartPackage, dataTransformation)
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
        'Finished running FrameNet aggregation at', True, '', True, start)
    return out


def wsd_aggregate_WordNet(conll_file, outputDir, noun_verb, chartPackage, dataTransformation):
    """Word Sense Disambiguation aggregation (WordNet). For each NOUN/VERB token in a CoNLL table, disambiguate
    its sense IN CONTEXT with the Lesk algorithm (NLTK `nltk.wsd.lesk`; Lesk 1986) using the token's sentence,
    then aggregate to that synset's WordNet top-level category (lexname / supersense). This picks the
    context-correct sense instead of the bare-lemma first sense. WordNet-only - VerbNet/FrameNet sense
    disambiguation is the SRL/SemLink route. See docs/Semantic_Aggregation_GUI_design.md section 8 (WSD vs WSI)."""
    import pandas as pd
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/wordnet', 'wordnet')
    from nltk.wsd import lesk
    try:
        conll = pd.read_csv(conll_file, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        mb.showwarning(title='Word sense disambiguation',
                       message="Could not read the CoNLL table:\n\n%s\n\n%s" % (conll_file, e))
        return []
    cols = {str(c).strip().lower(): c for c in conll.columns}
    form_c = cols.get('form')
    pos_c = cols.get('pos')
    lemma_c = cols.get('lemma')
    sent_c = cols.get('sentence id')
    doc_c = cols.get('document id') or cols.get('document')
    if not form_c or not pos_c or not sent_c:
        mb.showwarning(title='Word sense disambiguation',
                       message="Word sense disambiguation expects a CoNLL table with Form, POS and Sentence ID "
                               "columns (it needs each word's sentence as context).\n\n%s\n\nPlease select a "
                               "CoNLL table and try again." % conll_file)
        return []
    import CoNLL_util
    wn_pos = 'n' if noun_verb == 'NOUN' else 'v'
    pos_match = CoNLL_util.is_noun_POS if noun_verb == 'NOUN' else CoNLL_util.is_verb_POS
    start = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
        'Started running Word sense disambiguation (Lesk) at', True, '', True)
    rows = []
    counts = defaultdict(int)
    group_keys = [c for c in (doc_c, sent_c) if c]
    for _, sent_df in conll.groupby(group_keys, sort=False):
        context = [str(f) for f in sent_df[form_c].tolist() if str(f).strip() and str(f) != 'nan']
        for _, r in sent_df.iterrows():
            if not pos_match(r[pos_c]):
                continue
            surface = str(r[form_c]).strip()
            word = str(r[lemma_c]).strip() if lemma_c else surface
            if not word or word == 'nan':
                continue
            try:
                syn = lesk(context, word, wn_pos)
            except Exception:
                syn = None
            # lexname is 'pos.category' (e.g. 'verb.stative', 'noun.person'); drop the pos prefix
            # since the noun/verb is already stated in the chart title and the output file name
            cat = syn.lexname().split('.', 1)[-1] if syn else 'Not found'
            counts[cat] += 1
            rows.append({'Word': surface, 'Lemma': word, 'WordNet category': cat})
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
        'Finished running Word sense disambiguation (Lesk) at', True, '', True, start)
    if not rows:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Invalid Input',
            "Word sense disambiguation found no %s in the CoNLL table\n%s." % (noun_verb, conll_file))
        return []
    fileName = os.path.basename(conll_file).split('.')[0]
    csv1 = os.path.join(outputDir, "NLP_WSD_WordNet_%s_%s.csv" % (noun_verb, fileName))
    csv2 = os.path.join(outputDir, "NLP_WSD_WordNet_%s_%s_frequency.csv" % (noun_verb, fileName))
    filesToOpen = []
    with open(csv1, 'w', encoding='utf-8', newline='') as f:
        wtr = csv.DictWriter(f, fieldnames=['Word', 'Lemma', 'WordNet category'])
        wtr.writeheader(); wtr.writerows(rows)
    with open(csv2, 'w', encoding='utf-8', newline='') as f:
        wtr = csv.DictWriter(f, fieldnames=['WordNet category', 'Frequency']); wtr.writeheader()
        for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
            wtr.writerow({'WordNet category': cat, 'Frequency': n})
    filesToOpen += [csv1, csv2]
    if chartPackage and chartPackage != 'No charts':
        of = charts_util.plot(csv1, outputDir, columns=['WordNet category'], title='Word-sense-disambiguated WordNet categories for %s' % noun_verb, x_label='WordNet category (WSD)', group_by=None)
        if of:
            filesToOpen.extend(of if isinstance(of, list) else [of])
    return filesToOpen


def aggregate(knowledge_base, WordNetDir, inputFile, outputDir, config_filename, noun_verb,
              openOutputFiles, chartPackage, dataTransformation, language_var='', target_terms=None):
    """Dispatch a Zoom OUT/UP aggregation to the chosen Knowledge base. '*' = all applicable
    (WordNet always; VerbNet only for verbs; FrameNet for nouns or verbs) - one labelling per resource."""
    kb = knowledge_base or 'WordNet'
    files = []

    def run_wn():
        r = wn_util.aggregate_GoingUP(WordNetDir, inputFile, outputDir, config_filename, noun_verb,
                                      openOutputFiles, chartPackage, dataTransformation, language_var, target_terms)
        return r or []

    def run_vn():
        return aggregate_VerbNet(inputFile, outputDir, noun_verb, chartPackage, dataTransformation) or []

    def run_fn():
        return aggregate_FrameNet(inputFile, outputDir, noun_verb, chartPackage, dataTransformation) or []

    if kb == 'WordNet':
        files += run_wn()
    elif kb == 'VerbNet':
        files += run_vn()
    elif kb == 'FrameNet':
        files += run_fn()
    else:  # '*' = all applicable resources
        files += run_wn()
        if noun_verb == 'VERB':
            files += run_vn()
        files += run_fn()
    return files


# ---- Zoom IN/DOWN: build a word list from a category (VerbNet class / FrameNet frame) ----

def _strip_pos_prefix(term):
    """The WordNet keyword widget prefixes entries with 'noun.'/'verb.'; strip that so the term works
    as a VerbNet class / FrameNet frame / lemma."""
    t = str(term).strip()
    if t.lower().startswith('noun.') or t.lower().startswith('verb.'):
        return t.split('.', 1)[1]
    return t


def _write_word_list(rows, resource, outputDir, category_col):
    """rows: list of {'Term', category_col}. Write a de-duplicated word-list csv; return [csv] or []."""
    import pandas as pd
    if not rows:
        mb.showwarning(title="%s word list" % resource,
                       message="%s found no words for the category/categories you entered.\n\nCheck the "
                               "spelling - e.g. a VerbNet class like 'murder-42.1' (or a member verb like "
                               "'murder'), or a FrameNet frame like 'Killing'." % resource)
        return []
    out_csv = os.path.join(outputDir, "NLP_%s_DOWN_wordlist.csv" % resource)
    try:
        pd.DataFrame(rows)[['Term', category_col]].drop_duplicates().to_csv(out_csv, index=False, encoding='utf-8')
    except Exception as e:
        mb.showwarning(title="%s word list" % resource, message="Could not write the word list:\n\n%s" % e)
        return []
    return [out_csv]


def disaggregate_VerbNet(terms, outputDir, noun_verb):
    """Build a word list from VerbNet: each term is a member verb (-> its class's verbs) or a class id
    (-> that class's verbs)."""
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/verbnet', 'verbnet')
    from nltk.corpus import verbnet as vn
    all_ids = None
    rows = []
    for raw in terms:
        t = _strip_pos_prefix(raw).lower()
        classes = vn.classids(lemma=t)              # t as a verb lemma -> its class(es)
        if not classes:                              # else t as a class id (full id or numeric part)
            if all_ids is None:
                all_ids = vn.classids()
            classes = [c for c in all_ids if c == t or c.split('-', 1)[-1] == t]
        for c in classes:
            for m in vn.lemmas(c):
                rows.append({'Term': m.replace('_', ' '), 'VerbNet class': c})
    return _write_word_list(rows, 'VerbNet', outputDir, 'VerbNet class')


def disaggregate_FrameNet(terms, outputDir, noun_verb):
    """Build a word list from FrameNet: each term is a frame name (-> its lexical units) or a word
    (-> the frames it evokes -> their lexical units). Includes verbs AND nouns (event nouns)."""
    IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/framenet_v17', 'framenet_v17')
    from nltk.corpus import framenet as fn
    rows = []
    for raw in terms:
        t = _strip_pos_prefix(raw)
        try:
            frames = list(fn.frames(r'(?i)^' + re.escape(t) + r'$'))      # t as a frame name
        except Exception:
            frames = []
        if not frames:                                                    # else t as a lemma
            try:
                frames = list(fn.frames_by_lemma(re.compile(r'(?i)^' + re.escape(t) + r'\.')))
            except Exception:
                frames = []
        for fr in frames:
            for lu_name in fr.lexUnit:
                rows.append({'Term': lu_name.rsplit('.', 1)[0], 'FrameNet frame': fr.name})
    return _write_word_list(rows, 'FrameNet', outputDir, 'FrameNet frame')


def disaggregate(knowledge_base, WordNetDir, outputDir, terms, noun_verb):
    """Dispatch Zoom IN/DOWN (build a word list from a category) to the chosen Knowledge base.
    '*' = all applicable (WordNet always; VerbNet only for verbs; FrameNet always)."""
    kb = knowledge_base or 'WordNet'
    files = []

    def run_wn():
        return wn_util.disaggregate_GoingDOWN(WordNetDir, outputDir, terms, noun_verb) or []

    def run_vn():
        return disaggregate_VerbNet(terms, outputDir, noun_verb) or []

    def run_fn():
        return disaggregate_FrameNet(terms, outputDir, noun_verb) or []

    if kb == 'WordNet':
        files += run_wn()
    elif kb == 'VerbNet':
        files += run_vn()
    elif kb == 'FrameNet':
        files += run_fn()
    else:  # '*' = all applicable
        files += run_wn()
        if noun_verb == 'VERB':
            files += run_vn()
        files += run_fn()
    return files
