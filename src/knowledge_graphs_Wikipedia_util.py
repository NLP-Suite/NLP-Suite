# Written by Roberto Franzosi & Claude
# Wikipedia annotator for the Knowledge graphs GUI.
#
# WHY A THIRD ANNOTATOR: DBpedia and YAGO both extract their structured knowledge FROM Wikipedia, and
# both constrain what they annotate to an ontology class. Wikipedia itself has no ontology, so this
# annotator answers a simpler question -- does this name have a Wikipedia article? -- and links to it.
# It is the right tool when a corpus names people, places and organizations that never made it into an
# ontology, which is the normal case for local nineteenth-century material.
#
# WHAT IT ANNOTATES: PROPER NOUNS ONLY (Stanza NNP/NNPS, including multi-word sequences such as
# 'The Atlanta Constitution'). This is a deliberate restriction. Practically every common noun has a
# Wikipedia article -- 'sheriff' and 'lynching' both resolve -- so annotating content words as DBpedia
# and YAGO do, minus their ontology filter, would turn every page into a wall of links and say nothing.
# Restricting to proper nouns makes the output ENTITY linking, which is what a knowledge graph gives.
#
# HOW: the MediaWiki API takes up to 50 titles per request and reports, in one round trip, which exist,
# what they normalize to, and where they redirect -- so 'The Atlanta Constitution' correctly resolves to
# 'The Atlanta Journal-Constitution'. Disambiguation pages are dropped: a link to a list of nine
# different Macons annotates nothing.
#
# The Stanza pipeline, the text preprocessing and the HTML builder are shared with the YAGO annotator
# rather than copied, so the three knowledge bases produce identical output structure.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "Wikipedia knowledge graph",
                                                 ['os', 'requests', 'pandas', 'stanza']) == False:
    sys.exit(0)

import os
import ssl
from urllib.parse import quote

import pandas as pd
import requests

import IO_files_util
import IO_user_interface_util
import IO_csv_util
import IO_internet_util

# shared with the YAGO annotator: same parser, same preprocessing, same HTML shape
from knowledge_graphs_YAGO_util import _get_stanza_pipeline, _preprocess, _build_html, _eligible

API_URL = 'https://en.wikipedia.org/w/api.php'
ARTICLE_URL = 'https://en.wikipedia.org/wiki/'
# the MediaWiki API accepts 50 titles per request for anonymous clients
BATCH_SIZE = 50
API_TIMEOUT = 30
# MediaWiki asks that clients identify themselves; an unidentified bulk client can be throttled
USER_AGENT = 'NLP-Suite (https://github.com/NLP-Suite/NLP-Suite; academic text analysis)'

ONTOLOGY_LABEL = 'Wikipedia article'

# Newspaper prose names people by title -- 'Sheriff Jim Cobb', 'Governor Hugh Dorsey' -- and Stanza tags
# the honorific NNP too, so the phrase handed to the API includes it. Wikipedia has no article called
# 'Sheriff Jim Cobb', so the person went unlinked; the article is under the bare name. The honorific is
# therefore stripped before the lookup, while the annotation still covers the whole phrase as written.
HONORIFICS = {
    'mr', 'mrs', 'miss', 'ms', 'dr', 'doctor', 'prof', 'professor', 'rev', 'reverend', 'fr', 'father',
    'sheriff', 'deputy', 'marshal', 'constable', 'judge', 'justice', 'attorney', 'solicitor',
    'governor', 'gov', 'senator', 'sen', 'congressman', 'representative', 'rep', 'president',
    'mayor', 'alderman', 'councilman', 'commissioner', 'coroner', 'warden', 'chief',
    'captain', 'capt', 'colonel', 'col', 'major', 'general', 'gen', 'lieutenant', 'lt', 'sergeant',
    'sgt', 'corporal', 'private', 'admiral', 'commander', 'sir', 'lord', 'lady', 'saint', 'st',
}

# Month and weekday names are proper nouns, so they are collected like any other, but linking every
# 'May' in a corpus of dated newspaper articles to the article about the month is pure noise.
CALENDAR_WORDS = {
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
    'november', 'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct',
    'nov', 'dec', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
}


def _lookup_title(phrase):
    """The title to ask Wikipedia for, or '' when the phrase should not be looked up at all."""
    tokens = phrase.split()
    if not tokens:
        return ''
    if len(tokens) == 1 and tokens[0].lower().strip('.') in CALENDAR_WORDS:
        return ''
    # drop leading honorifics, but never reduce the phrase to nothing: 'Sheriff' alone stays 'Sheriff'
    while len(tokens) > 1 and tokens[0].lower().strip('.') in HONORIFICS:
        tokens = tokens[1:]
    return ' '.join(tokens)


def _collect_proper_noun_phrases(doc):
    """Every proper noun and multi-word proper-noun sequence in the document, lemmatized.

    Mirrors how _build_html walks the document, so that every phrase it will later try to look up in the
    cache is a phrase we actually queried."""
    phrases = set()
    for sent in doc.sentences:
        run = ''
        for word in sent.words:
            if word.xpos in ('NNP', 'NNPS'):
                run += word.lemma + ' '
            else:
                if run:
                    phrase = run.strip()
                    if _eligible(phrase):
                        phrases.add(phrase)
                    run = ''
        if run:
            phrase = run.strip()
            if _eligible(phrase):
                phrases.add(phrase)
    return phrases


def _batch_query_wikipedia(phrases, color, session):
    """{phrase: (url, 'Wikipedia article', color)} for phrases that have an article; None otherwise.

    Returns the same cache shape the YAGO annotator builds, so _build_html consumes it unchanged."""
    cache = {}
    phrases = list(phrases)

    # phrase as it appears in the text -> the title actually asked of Wikipedia. Several phrases can share
    # one title ('Sheriff Jim Cobb' and 'Jim Cobb'), so the queried titles are de-duplicated.
    lookup = {}
    for phrase in phrases:
        title = _lookup_title(phrase)
        if title and '|' not in title:
            lookup[phrase] = title
    titles = sorted(set(lookup.values()))
    resolved_titles = {}

    for start in range(0, len(titles), BATCH_SIZE):
        batch = titles[start:start + BATCH_SIZE]
        if not batch:
            continue
        try:
            response = session.get(API_URL,
                                   params={'action': 'query', 'format': 'json', 'redirects': 1,
                                           'prop': 'pageprops', 'ppprop': 'disambiguation',
                                           'titles': '|'.join(batch)},
                                   headers={'User-Agent': USER_AGENT},
                                   timeout=API_TIMEOUT)
            if response.status_code != 200:
                print('   Wikipedia API returned HTTP ' + str(response.status_code) + ' for a batch. Continuing...')
                continue
            data = response.json().get('query', {})
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print('   Wikipedia API timeout for a batch. Continuing...')
            continue
        except Exception as e:
            print('   Wikipedia API error: ' + str(e))
            continue

        # the API reports the title it normalized to ('lynching' -> 'Lynching') and the one it redirected
        # to ('The Atlanta Constitution' -> 'The Atlanta Journal-Constitution'); a phrase must be followed
        # through both to find its page
        normalized = {n['from']: n['to'] for n in data.get('normalized', [])}
        redirected = {r['from']: r['to'] for r in data.get('redirects', [])}
        pages_by_title = {}
        for page_id, page in data.get('pages', {}).items():
            title = page.get('title')
            if title is None:
                continue
            missing = ('missing' in page) or str(page_id).startswith('-')
            disambiguation = 'disambiguation' in (page.get('pageprops') or {})
            pages_by_title[title] = (missing, disambiguation)

        for title in batch:
            resolved = normalized.get(title, title)
            resolved = redirected.get(resolved, resolved)
            entry = pages_by_title.get(resolved)
            if entry is None:
                continue
            missing, disambiguation = entry
            if missing or disambiguation:
                # a disambiguation page names no single entity, so linking to it annotates nothing
                continue
            resolved_titles[title] = resolved

    for phrase in phrases:
        resolved = resolved_titles.get(lookup.get(phrase))
        if resolved:
            cache[phrase] = (ARTICLE_URL + quote(resolved.replace(' ', '_')), ONTOLOGY_LABEL, color)
        else:
            cache[phrase] = None
    return cache


def Wikipedia_annotate(inputFile, inputDir, outputDir, configFileName, color1, colorls,
                       chartPackage='Excel', dataTransformation='No transformation'):
    """Annotate every proper noun that has a Wikipedia article. Returns the files to open.

    Unlike DBpedia and YAGO this takes no ontology class, because Wikipedia has no ontology: an article
    either exists for a name or it does not."""
    ssl._create_default_https_context = ssl._create_unverified_context

    filesToOpen = []
    all_phrases, all_links, all_onts = [], [], []
    all_sent_ids, all_sentences, all_documents, all_html_docs = [], [], [], []

    color = colorls[0] if colorls else color1

    files = IO_files_util.getFileList(inputFile, inputDir, '.txt', silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running Wikipedia Knowledge Graph at', True,
        '\nAnnotating the proper nouns that have a Wikipedia article, in ' + str(color) + '.',
        True, '', False)

    session = requests.Session()
    nlp = _get_stanza_pipeline()

    for file_idx, file in enumerate(files, 1):
        head, tail = os.path.split(file)
        print("Processing file " + str(file_idx) + "/" + str(nFile) + " " + tail)

        with open(file, 'r', encoding='utf-8', errors='ignore') as _f:
            contents = _f.read()
        contents = _preprocess(contents)

        doc = nlp(contents)

        candidates = _collect_proper_noun_phrases(doc)
        print("   " + str(len(candidates)) + " unique proper nouns to look up")

        cache = _batch_query_wikipedia(candidates, color, session)
        matched = sum(1 for v in cache.values() if v is not None)
        print("   " + str(matched) + " found in Wikipedia")

        html_str, phrases, links, onts, sent_ids, sentences = _build_html(doc, cache, color1, file)

        outFilename = os.path.join(outputDir,
                                   "NLP_Wikipedia_annotated_" + os.path.splitext(tail)[0] + '.html')
        with open(outFilename, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(html_str)
        filesToOpen.append(outFilename)

        hyper_html = IO_csv_util.dressFilenameForCSVHyperlink(outFilename)
        all_phrases.extend(phrases)
        all_links.extend(links)
        all_onts.extend(onts)
        all_sent_ids.extend(sent_ids)
        all_sentences.extend(sentences)
        all_documents.extend([file] * len(phrases))
        all_html_docs.extend([hyper_html] * len(phrases))

    if not all_phrases:
        IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                           'Finished running Wikipedia Knowledge Graph at',
                                           True, '', True, startTime, False)
        return filesToOpen

    DocumentID = []
    current_doc = None
    doc_id = 0
    for d in all_documents:
        if d != current_doc:
            doc_id += 1
            current_doc = d
        DocumentID.append(doc_id)

    HyperLinkedDoc = [IO_csv_util.dressFilenameForCSVHyperlink(d) for d in all_documents]
    HyperLinkedURL = [IO_csv_util.dressFilenameForCSVHyperlink(u) for u in all_links]

    df = pd.DataFrame({
        'Token': all_phrases,
        'Ontology class': all_onts,
        'url': HyperLinkedURL,
        'Sentence ID': all_sent_ids,
        'Sentence': all_sentences,
        'Document ID': DocumentID,
        'Document': HyperLinkedDoc,
        'Html File': all_html_docs,
    })

    from datetime import datetime, date
    csvname = "Wikipedia_output_" + date.today().strftime("%b_%d_%Y") + "_" + datetime.now().strftime("%H_%M_%S") + ".csv"
    csvname = os.path.join(outputDir, csvname)
    df.to_csv(csvname, encoding='utf-8', index=False)
    filesToOpen.append(csvname)

    if not df.empty:
        import charts_util
        outputFiles = charts_util.plot(csvname, outputDir, columns=['Token'],
                                       title='Frequency of Wikipedia annotated entities',
                                       x_label='Wikipedia entity')
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running Wikipedia Knowledge Graph at',
                                       True, '', True, startTime, False)
    return filesToOpen
