# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi October 2021
# refactored for efficiency June 2026

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "knowledge_graph_DBpedia_util.py",
                                          ['os', 'requests', 'urllib', 'ssl', 'shutil', 'bs4']) == False:
    sys.exit(0)

import os
import pandas as pd
import requests
import urllib.parse
import ssl
import shutil
from bs4 import BeautifulSoup

import IO_user_interface_util
import file_splitter_ByLength_util
import IO_files_util
import IO_csv_util

ssl._create_default_https_context = ssl._create_unverified_context

SPOTLIGHT_URL = 'http://api.dbpedia-spotlight.org/en/annotate'
REQUEST_TIMEOUT = 30


def DBpedia_annotate(inputFile, inputDir, outputDir, configFileName, openOutputFiles,
                     annotationTypes, colors, confidence_level=0.5, chartPackage='Excel',
                     dataTransformation='No transformation'):

    filesToOpen = []
    all_phrases = []
    all_urls = []
    all_ontologies = []
    all_documents = []

    annotationTypes = _check_ontology(annotationTypes)
    colormap = {ont: colors[idx] for idx, ont in enumerate(annotationTypes)}

    annotationOpts = '' if 'Thing' in annotationTypes else ','.join(annotationTypes)

    files = IO_files_util.getFileList(inputFile, inputDir, '.txt', silent=False, configFileName=configFileName)
    nFile = len(files)
    if nFile == 0:
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running DBpedia Knowledge Graph at', True,
        'Annotating types: ' + str(annotationTypes) + '\nConfidence level: ' + str(confidence_level), False)
    print('\n\nAnnotating types:', annotationTypes, 'with confidence level', str(confidence_level))

    session = requests.Session()

    for i, file in enumerate(files, 1):
        head, tail = os.path.split(file)
        print("Processing file " + str(i) + "/" + str(nFile) + " " + tail)

        defaultSize = 8000
        listOfSplitFiles = [file]
        splitFilesDir = ''
        splitHtmlFileList = []
        numberOfSplitSubfiles = 0

        j = 0
        while j < len(listOfSplitFiles):
            doc = listOfSplitFiles[j]
            _, doc_tail = os.path.split(doc)
            outFilename = os.path.join(outputDir, "NLP_DBpedia_annotated_" + doc_tail[:-4] + '.html')

            if numberOfSplitSubfiles > 0:
                if listOfSplitFiles[0] == file:
                    j += 1
                    continue
                print('   Processing split file ' + str(j + 1) + "/" + str(len(listOfSplitFiles)) +
                      ' ' + doc_tail + ' with DBpedia size ' + str(defaultSize))
                splitHtmlFileList.append(outFilename)

            with open(doc, 'r', encoding='utf-8', errors='ignore') as _f:
                contents = _f.read()

            contents = _preprocessing(contents)

            params = {
                'text': contents,
                'confidence': str(confidence_level),
                'support': '20',
                'types': annotationOpts,
            }

            try:
                r = session.get(SPOTLIGHT_URL, params=params,
                                headers={'Accept': 'application/json'}, timeout=REQUEST_TIMEOUT)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                print('   Connection error to DBpedia Spotlight: ' + str(e))
                j += 1
                continue

            if r.status_code == 414:
                print('   ERROR: Line too long (size ' + str(defaultSize) + '). Splitting document.')
                defaultSize -= 1000
                if defaultSize < 2000:
                    print('   Split size below 2000. Skipping file.')
                    break
                listOfSplitFiles = file_splitter_ByLength_util.splitDocument_byLength(
                    GUI_util.window, 'DBpedia', doc, outputDir, defaultSize)
                head2, _ = os.path.split(listOfSplitFiles[0])
                splitFilesDir = head2
                numberOfSplitSubfiles = len(listOfSplitFiles)
                j = 0
                continue

            if r.status_code != 200:
                print('   DBpedia returned status ' + str(r.status_code) + '. Skipping.')
                j += 1
                continue

            response = r.json()

            uri_type_map = {}
            if 'Resources' in response:
                for res in response['Resources']:
                    uri = res['@URI']
                    res_types = res.get('@types', '')
                    matched = _match_annotation_type(res_types, annotationTypes)
                    if matched:
                        uri_type_map[uri] = matched

            try:
                r_html = session.get(SPOTLIGHT_URL, params=params,
                                     headers={'Accept': 'text/html'}, timeout=REQUEST_TIMEOUT)
                html_content = r_html.text
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                html_content = response.get('@text', '')

            if uri_type_map:
                html_content, phrases, urls, ontologies = _color_and_extract(
                    html_content, uri_type_map, colormap, annotationTypes, session)
                for p, u, o in zip(phrases, urls, ontologies):
                    all_phrases.append(p)
                    all_urls.append(u)
                    all_ontologies.append(o)
                    all_documents.append(file)

            with open(outFilename, 'w', encoding='utf-8', errors='ignore') as outfile:
                outfile.write(html_content)

            j += 1

        if numberOfSplitSubfiles > 0:
            outFilename = os.path.join(outputDir,
                                       "NLP_DBpedia_annotated_" + os.path.split(file)[1].split('.txt')[0] + '.html')
            with open(outFilename, 'w', encoding='utf-8', errors='ignore') as outfile:
                for htmlDoc in splitHtmlFileList:
                    if htmlDoc == outFilename:
                        continue
                    if os.path.exists(htmlDoc):
                        with open(htmlDoc, 'r', encoding='utf-8', errors='ignore') as infile:
                            outfile.write(infile.read())
                    try:
                        os.remove(htmlDoc)
                    except:
                        continue
                if os.path.exists(splitFilesDir):
                    shutil.rmtree(splitFilesDir)

        filesToOpen.append(outFilename)

    if not all_phrases:
        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                           'Finished running DBpedia Knowledge Graph at', True, '', True, startTime)
        return filesToOpen

    DocumentID = []
    current_doc = None
    doc_id = 0
    for d in all_documents:
        if d != current_doc:
            doc_id += 1
            current_doc = d
        DocumentID.append(doc_id)

    HyperLinkedURL = [IO_csv_util.dressFilenameForCSVHyperlink(u) for u in all_urls]
    HyperLinkedDoc = [IO_csv_util.dressFilenameForCSVHyperlink(d) for d in all_documents]

    df = pd.DataFrame({
        'Token': all_phrases,
        'URL': HyperLinkedURL,
        'Ontology class': all_ontologies,
        'Document ID': DocumentID,
        'Document': HyperLinkedDoc,
    })

    from datetime import datetime, date
    csvname = "DBpedia_output_" + date.today().strftime("%b_%d_%Y") + "_" + datetime.now().strftime("%H_%M_%S") + ".csv"
    csvname = os.path.join(outputDir, csvname)
    df.to_csv(csvname, encoding='utf-8', index=False)
    filesToOpen.append(csvname)

    if not df.empty:
        import charts_util
        outputFiles = charts_util.plot(csvname, outputDir, columns=['Token'], title='Frequency of DBpedia Words', x_label='DBpedia word')
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running DBpedia Knowledge Graph at', True, '', True, startTime)
    return filesToOpen


def _match_annotation_type(types_str, annotationTypes):
    if not types_str:
        return None
    for ann_type in annotationTypes:
        if ann_type == 'Thing':
            return 'Thing'
        if 'DBpedia:' + ann_type in types_str or 'Schema:' + ann_type in types_str:
            return ann_type
    return None


def _color_and_extract(html_content, uri_type_map, colormap, annotationTypes, session):
    phrases = []
    urls = []
    ontologies = []

    soup = BeautifulSoup(html_content, 'html.parser')
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '') or a_tag.get('title', '')
        if not href:
            continue

        matched_type = uri_type_map.get(href)
        if not matched_type and href.startswith('http'):
            matched_type = _sparql_fallback(href, annotationTypes, session)

        if matched_type and matched_type in colormap:
            a_tag['style'] = 'color:' + colormap[matched_type]
            phrases.append(a_tag.get_text())
            urls.append(href)
            ontologies.append(matched_type)

    return str(soup), phrases, urls, ontologies


def _sparql_fallback(uri, annotationTypes, session):
    if not annotationTypes:
        return None
    if annotationTypes == ['Thing']:
        return 'Thing'

    union_parts = []
    for t in annotationTypes:
        if t == 'Thing':
            union_parts.append('{ <' + uri + '> rdf:type owl:Thing . BIND("Thing" AS ?t) }')
        else:
            union_parts.append('{ <' + uri + '> rdf:type dbo:' + t + ' . BIND("' + t + '" AS ?t) }')

    query = 'SELECT ?t WHERE { ' + ' UNION '.join(union_parts) + ' } LIMIT 1'
    try:
        r = session.get('https://dbpedia.org/sparql', params={
            'default-graph-uri': 'http://dbpedia.org',
            'query': query,
            'format': 'application/sparql-results+json',
            'timeout': '10000',
        }, timeout=15)
        if r.status_code == 200:
            bindings = r.json().get('results', {}).get('bindings', [])
            if bindings:
                return bindings[0].get('t', {}).get('value', '')
    except:
        pass
    return None


def _check_ontology(annotationTypes):
    res = []
    for t in annotationTypes:
        if t != 'Thing':
            s1 = t.split(' ')
            t = s1[-1]
        res.append(t)
    if len(res) == 0:
        res = ['Thing', 'unknown']
    return res


def _preprocessing(contents):
    contents = ' '.join(contents.split())
    contents = contents.replace('\0', '')
    contents = contents.replace('\'', '')
    contents = contents.replace('\"', '')
    contents = contents.replace("\\", '')
    contents = contents.replace("/", ' or ')
    return contents
