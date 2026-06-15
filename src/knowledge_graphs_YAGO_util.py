# YAGO Knowledge Graph annotation utility
# refactored for efficiency June 2026

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "annotator_YAGO_util.py",
        ['os', 're', 'pandas', 'string', 'requests', 'stanza', 'fuzzywuzzy']) == False:
    sys.exit(0)

import os
import string
import re
from re import split
import ssl
import pandas as pd
import requests
import stanza
from fuzzywuzzy import fuzz

import IO_files_util
import IO_user_interface_util
import IO_csv_util

SPARQL_URL = "https://yago-knowledge.org/sparql/query"
SPARQL_TIMEOUT = 30
BATCH_SIZE = 25
PUNCTUATION_AND_DIGITS = set(string.punctuation + '0123456789')
SKIP_POS = frozenset({'VERB', 'DET', 'ADP', 'PRON', 'AUX'})

_stannlp = None


def _get_stanza_pipeline():
    global _stannlp
    if _stannlp is None:
        try:
            _stannlp = stanza.Pipeline(lang='en', processors='tokenize,ner,mwt,pos,lemma',
                                       use_gpu=False, verbose=False)
        except Exception:
            stanza.download('en', verbose=False)
            _stannlp = stanza.Pipeline(lang='en', processors='tokenize,ner,mwt,pos,lemma',
                                       use_gpu=False, verbose=False)
    return _stannlp


def YAGO_annotate(inputFile, inputDir, outputDir, configFileName, annotationTypes, color1, colorls,
                  chartPackage='Excel', dataTransformation='No transformation'):
    ssl._create_default_https_context = ssl._create_unverified_context

    filesToOpen = []
    all_phrases = []
    all_links = []
    all_onts = []
    all_sent_ids = []
    all_sentences = []
    all_documents = []
    all_html_docs = []

    numberOfAnnotations = len(annotationTypes)
    if numberOfAnnotations == 0:
        categories = ['schema:Thing', 'owl:Class']
        if not colorls:
            colorls = ['red', 'blue']
    else:
        categories = []
        for anntype in annotationTypes:
            if anntype == "Emotion":
                categories.append("yago:Emotion")
            elif anntype in ["BioChemEntity", "Gene", "Taxon", "MolecularEntity"]:
                categories.append("bioschemas:" + anntype)
            else:
                categories.append("schema:" + anntype)

    cat_colors = {}
    for idx, cat in enumerate(categories):
        cat_colors[cat] = colorls[idx] if idx < len(colorls) else color1

    files = IO_files_util.getFileList(inputFile, inputDir, '.txt', silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running YAGO Knowledge Graph at', True,
        '\nAnnotating types: ' + str(categories) + " with associated colors: " + str(colorls),
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

        eligible_lemmas = _collect_eligible_lemmas(doc)
        print("   " + str(len(eligible_lemmas)) + " unique eligible words to query")

        cache = _batch_query_yago(list(eligible_lemmas), categories, cat_colors, color1, session)
        print("   " + str(sum(1 for v in cache.values() if v is not None)) + " words matched in YAGO")

        html_str, phrases, links, onts, sent_ids, sentences = _build_html(
            doc, cache, color1, file)

        outFilename = os.path.join(outputDir,
                                   "NLP_YAGO_annotated_" + os.path.splitext(tail)[0] + '.html')
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
                                           'Finished running YAGO Knowledge Graph at',
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
    csvname = "YAGO_output_" + date.today().strftime("%b_%d_%Y") + "_" + datetime.now().strftime("%H_%M_%S") + ".csv"
    csvname = os.path.join(outputDir, csvname)
    df.to_csv(csvname, encoding='utf-8', index=False)
    filesToOpen.append(csvname)

    if not df.empty:
        import charts_util
        chart_label = annotationTypes[0] if annotationTypes else 'Thing'
        outputFiles = charts_util.visualize_chart(
            chartPackage, dataTransformation, csvname, outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=['Token'],
            chart_title='Frequency of YAGO ' + chart_label + ' Words',
            count_var=1,
            hover_label=[],
            outputFileNameType='',
            column_xAxis_label='YAGO ' + chart_label + ' word',
            groupByList=['Document'],
            plotList=[],
            chart_title_label='')
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running YAGO Knowledge Graph at',
                                       True, '', True, startTime, False)
    return filesToOpen


def _collect_eligible_lemmas(doc):
    eligible = set()
    for sent in doc.sentences:
        prev_tr = ""
        for word in sent.words:
            if word.xpos in ("NNP", "NNPS"):
                prev_tr += word.lemma + " "
            else:
                if prev_tr:
                    lemma = prev_tr.strip()
                    if _eligible(lemma):
                        eligible.add(lemma)
                    prev_tr = ""
                if word.pos not in SKIP_POS and _eligible(word.lemma):
                    eligible.add(word.lemma)
        if prev_tr:
            lemma = prev_tr.strip()
            if _eligible(lemma):
                eligible.add(lemma)
    return eligible


def _batch_query_yago(lemmas, categories, cat_colors, default_color, session):
    cache = {}

    for batch_start in range(0, len(lemmas), BATCH_SIZE):
        batch = lemmas[batch_start:batch_start + BATCH_SIZE]

        for cat in categories:
            values = ' '.join('"' + lemma.replace('"', '\\"') + '"@en' for lemma in batch)

            query = (
                'PREFIX owl: <http://www.w3.org/2002/07/owl#>\n'
                'PREFIX schema: <http://schema.org/>\n'
                'PREFIX bioschemas: <http://bioschemas.org/>\n'
                'PREFIX yago: <http://yago-knowledge.org/resource/>\n'
                'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n'
                'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
                'SELECT DISTINCT ?label ?w1 WHERE {\n'
                '  VALUES ?label { ' + values + ' }\n'
                '  { ?w1 rdfs:label ?label } UNION { ?w1 schema:alternateName ?label } .\n'
                '  { ?w1 rdfs:subClassOf* ' + cat + ' } UNION { ?w1 rdf:type ' + cat + ' }\n'
                '}'
            )

            try:
                r = session.post(SPARQL_URL,
                                 data={'query': query},
                                 headers={'Accept': 'application/sparql-results+json'},
                                 timeout=SPARQL_TIMEOUT)
                if r.status_code != 200:
                    continue

                results = r.json()
                bindings = results.get('results', {}).get('bindings', [])

                label_uris = {}
                for b in bindings:
                    label = b.get('label', {}).get('value', '')
                    uri = b.get('w1', {}).get('value', '')
                    if label and uri:
                        if label not in label_uris:
                            label_uris[label] = []
                        label_uris[label].append(uri)

                color = cat_colors.get(cat, default_color)
                for lemma in batch:
                    if lemma in cache and cache[lemma] is not None:
                        continue
                    uris = label_uris.get(lemma, [])
                    if not uris:
                        continue
                    best_uri = _select_best_uri(uris, lemma)
                    if best_uri:
                        cache[lemma] = (best_uri, cat, color)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                print('   YAGO SPARQL timeout for batch. Continuing...')
            except Exception as e:
                print('   YAGO SPARQL error: ' + str(e))

    for lemma in lemmas:
        if lemma not in cache:
            cache[lemma] = None

    return cache


def _select_best_uri(uris, phrase_tr):
    uri_names = [str(x).split("/")[-1] for x in uris]
    cleaned = [split("_Q[0-9]+", name)[0] for name in uri_names]

    for idx, name in enumerate(uri_names):
        if name.lower().replace("_", " ") == phrase_tr.lower():
            return uris[idx]

    scores = [fuzz.ratio(phrase_tr, c) for c in cleaned]
    best_idx = scores.index(max(scores))
    if scores[best_idx] > 42:
        return uris[best_idx]
    return None


def _build_html(doc, cache, default_color, document_name):
    html_str = '<html>\n<body>\n<div>\n'
    tA1_open = '<span style="color: ' + default_color + '">'
    tA1_close = '</span> '

    phrases = []
    links = []
    onts = []
    sent_ids = []
    sentences = []

    for sent_id, sent in enumerate(doc.sentences):
        prev_og = ""
        prev_tr = ""
        for word in sent.words:
            if word.xpos in ("NNP", "NNPS"):
                prev_tr += word.lemma + " "
                prev_og += word.text + " "
            elif word.id == 1:
                html_str = _emit_word(html_str, word.text, word.lemma,
                                      word.pos not in SKIP_POS,
                                      cache, tA1_open, tA1_close,
                                      sent_id, sent.text,
                                      phrases, links, onts, sent_ids, sentences)
            else:
                if prev_og:
                    html_str = _emit_word(html_str, prev_og.strip(), prev_tr.strip(),
                                          True, cache, tA1_open, tA1_close,
                                          sent_id, sent.text,
                                          phrases, links, onts, sent_ids, sentences)
                html_str = _emit_word(html_str, word.text, word.lemma,
                                      word.pos not in SKIP_POS,
                                      cache, tA1_open, tA1_close,
                                      sent_id, sent.text,
                                      phrases, links, onts, sent_ids, sentences)
                prev_og = ""
                prev_tr = ""

        if prev_og and sent.words[-1].text[0].isupper():
            html_str = _emit_word(html_str, prev_og.strip(), prev_tr.strip(),
                                  True, cache, tA1_open, tA1_close,
                                  sent_id, sent.text,
                                  phrases, links, onts, sent_ids, sentences)

    html_str += '\n</div>\n</body>\n</html>'
    return html_str, phrases, links, onts, sent_ids, sentences


def _emit_word(html_str, original, lemma, is_content_pos,
               cache, tA1_open, tA1_close,
               sent_id, sentence,
               phrases, links, onts, sent_ids, sentences):
    if is_content_pos and _eligible(lemma):
        entry = cache.get(lemma)
        if entry is not None:
            url, ont_class, color = entry
            html_str += '<a style="color:' + color + '" href="' + url + '">' + original + '</a> '
            phrases.append(original)
            links.append(url)
            onts.append(ont_class)
            sent_ids.append(sent_id)
            sentences.append(sentence)
            return html_str

    html_str += tA1_open + original + tA1_close
    return html_str


def _eligible(phrase):
    if not phrase or len(phrase) <= 2 or phrase.lower() == "not":
        return False
    return any(c not in PUNCTUATION_AND_DIGITS for c in phrase)


def _preprocess(contents):
    contents = ' '.join(contents.split())
    contents = contents.replace('\0', '')
    contents = contents.replace('\'', '')
    contents = contents.replace('\"', '')
    contents = contents.replace("\\", '')
    contents = contents.replace("/", ' or ')
    return contents
