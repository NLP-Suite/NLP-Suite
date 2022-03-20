# Written by Chen Gong spring 2022

import os
import tkinter.messagebox as mb
import string
import re
from re import split
from urllib import request, error
import stanza
from SPARQLWrapper import SPARQLWrapper, JSON, XML
import IO_files_util

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

stanza.download('en')
stannlp = stanza.Pipeline(lang='en', processors='tokenize,ner,mwt,pos,lemma')

punksAndNum = string.punctuation + '1' + '2' + '3' + '4' + '5' + '6' + '7' + '8' + '9' + '0'

tA1 = ['<span>', '</span>\n']
tA2 = ['<a href=\"',
       '\">',
       '</a>\n']

cache = {}  # cache the queried result

def DBpedia_annotate(inputFile, inputDir, outputDir, annotationTypes):
    """
    the main function for DBpedia annotation, create annotated html files
    Parameters
    ----------
    inputFile: input file path String
    inputDir: input directory path String
    outputDir: output directory path String
    annotationTypes: a list of ontology class

    Returns
    -------
    files to open: a list of annotated html files
    """
    filesToOpen = []
    inputFiles = []
    files = IO_files_util.getFileList(inputFile, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        print("No input file\n");
        return
    file_count = 1
    annotationTypes = check_ontology(annotationTypes)
    for file in files:
        fileName = file.split('/')[-1]
        print("processing file:", fileName, "\nFile: ", file_count, "/", nFile)
        contents = open(file, 'r', encoding='utf-8', errors='ignore').read()
        contents = preprocessing(contents)
        # ontology_type = annotationTypes[0]  # extract string from the list
        ontology_type = annotationTypes
        html_str = annotate(contents, ontology_type)

        outFilename = os.path.join(outputDir,
                                   "NLP_DBpedia_annotated_" + str(fileName.split('.txt')[0]) + '.html')
        out = open(outFilename, 'w+', encoding="utf-8", errors='ignore')
        out.write(html_str)
        filesToOpen.append(outFilename)
        out.close()

    return filesToOpen

def check_ontology(annotationTypes):
    res = []
    for type in annotationTypes:
        if type == 'Thing':
            type = 'owl:' + type
        else:
            type = 'dbo:' + type
        res.append(type)
    return res

def annotate(contents, annotationTypes):
    """
    annotate the input contents. Using stanford annotator to filter out words.
    NNP and NNPs will be grouped together if they are directly followed by each other. (prev_og and prev_tr are used to cache the NNPs)

    Parameters
    ----------
    contents: preprocessed file content
    annotationTypes:

    Returns
    -------
    annotated html string

    """
    color1 = 'black'
    color2 = 'blue'
    html_str = '<html>\n<body>\n<div>\n'
    html_str_end = '\n</div>\n</body>\n</html>'

    # tA1 = ['<span style=\"color: ' + color1 + '\">',
    #         '</span> ']
    # tA2 = ['<a style=\"color:' + color2 + '\" href=\"',
    #        '\">',
    #        '</a> ']



    annotated_doc = stanford_annotator(contents)
    for sent_id in range(len(annotated_doc.sentences)):
        sent = annotated_doc.sentences[sent_id]
        prev_og = ""
        prev_tr = ""
        pos = True
        for i in range(len(sent.words)):
            word = sent.words[i]
            pos = True
            if (word.pos == "VERB") or (word.pos == "DET") or (word.pos == "ADP") or (word.pos == "PRON") or (
                    word.pos == "AUX"):
                pos = False
            if word.xpos == "NNP" or word.xpos == "NNPS":
                prev_tr = prev_tr + word.lemma + " "
                prev_og = prev_og + word.text + " "
            else:  # annotate the Proper noun cached previously and the current word
                if prev_og:  # if prev_og is not empty, then annotate it
                    html_str = query_and_html(prev_og[:-1], prev_tr[:-1], annotationTypes, html_str)
                    prev_og = ""
                    prev_tr = ""
                    #TODO: if (word.id == 1)
                # if check_eligible(str(word.text)) and pos:  # query and update html
                if word.pos == 'NN' or word.pos == 'NNS' and pos:
                    # print(word.pos)
                    html_str = query_and_html(str(word.text), str(word.lemma), annotationTypes, html_str)
                else:  # update html without querying
                    html_str = html_without_query(str(word.text), html_str)

    if prev_og:  # if the last word in the document is NNP, query the last word
        html_str = query_and_html(prev_og[:-1], prev_tr[:-1], annotationTypes, html_str)

    return html_str + html_str_end


def query_and_html(phrase_og, phrase_tr, cats, html_str):
    '''
    query the input phrase and update the html based on the query result

    Parameters
    ----------
    phrase_og
    phrase_tr
    cats:      ontology classes
    html_str:  the current html string

    Returns
    -------
    updated html string

    '''
    new_html_str = search_dict(html_str, phrase_og, phrase_tr)
    if new_html_str: # if the word has been queried
        return new_html_str

    query = form_query_string(phrase_tr, cats)
    res = get_result(query)
    if not res:  # no url returned normal html, no annotation
        cache[phrase_tr] = "None"
        html_str += tA1[0] + phrase_og + tA1[1]
    else:  # annotate with the url
        url = res[0]
        cache[phrase_tr] = str(url)
        html_str += tA2[0] + str(url) + tA2[1] + phrase_og + tA2[2]
        ## TODO choose the best link

    return html_str


def html_without_query(phrase_og, html_str):
    html_str += tA1[0] + phrase_og + tA1[1]
    return html_str


def form_query_string(phrase, ont_ls):
    """
    construct the query string

    Parameters
    ----------
    phrase: lemma
    ont_ls: ontology list

    Returns
    -------
    query string
    """
    query_body = ''
    # "PREFIX https://dbpedia.org/snorql/"
    # + 'PREFIX dbpedia2: <http://dbpedia.org/property/>' + '\n' \
    query_s = 'PREFIX schema: <http://schema.org/>' + '\n' \
              + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>' + '\n' \
              + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' + '\n' \
              + 'PREFIX dbo: <http://dbpedia.org/ontology/>' + '\n' \
              + 'SELECT DISTINCT'
                # + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>' + '\n' \
                # + 'PREFIX dbpedia: <http://dbpedia.org/>' + '\n' \
                 # + 'PREFIX : <http://dbpedia.org/resource/>' + '\n' \
                # 'PREFIX owl: <http://www.w3.org/2002/07/owl#>' + '\n' \
    # TODO: check dbo:wikiPageDisambiguates for similar expression
    query_s = query_s + ' ?' + 'w1'  # SELECT DISTINCT w1
    query_body = query_body + '{?w1 ' + 'rdfs:label \"' + phrase + '\" @en.}'
    # query_body = query_body + ' UNION' + '{?w1 rdfs:label \"' + phrase + ' (disambiguation)\" @en.}\n'
    query_body = query_body + 'OPTIONAL{?w1 dbo:wikiPageDisambiguates ?s1.}'
    query_body = query_body + 'OPTIONAL{?w1 a ?type. ?s1 a ?type2}\n'
    # query_body = query_body  + "?w1 rdf:type " + "dbo:" + ont_ls[0]
    for ont in ont_ls:
        query_body = query_body + " { ?w1 a " + ont + ' } UNION' + '{?w1 a ?type.\n ?type rdfs:subClassOf* ' + ont+ '} UNION'

    query_body = query_body[:-5] # remove the last UNION
    query_s = query_s + "\nWHERE { OPTIONAL{"
    query_s = query_s + query_body
    query_s = query_s + "}}"

    print(query_s)
    return query_s


def get_result(query):
    """
    send query request and get the result, extract all the links and return as a list

    Parameters
    ----------
    query: query string

    Returns
    -------
    results: a list of urls
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        print("Waiting for DBpedia response...")
        # print(query)
        results = sparql.query().convert()
        print("Received")
    except error.HTTPError:
        # this may occasionally give time out error depending upon server's traffic
        mb.showwarning(title='Warning',
                       message='Take a look at your command line/prompt. An HTTP error of 500 means that the YAGO server failed. Please, check command line/prompt for "Operation timed out" error\n\nTry running the script later, when the server may be be less busy.')
        return None

    # TODO process the result in dataframe?
    bindings = results['results']['bindings']  # [{w1: {type: uri, value: "http:/xxx"}}]
    url_list = []
    # print(len(bindings))
    if len(bindings) > 1: # has returned link
        for link in bindings:
            url_list.append(link['w1']['value'])
    return url_list


def search_dict(html_str, phrase_og, phrase_tr):
    # Search global cached url to skip querying the same word again.
    if phrase_tr in cache:
        if cache[phrase_tr] != 'None': # annotate with previous url
            url = cache[phrase_tr]
            html_str += tA2[0] + str(url) + tA2[1] + phrase_og + tA2[2]
        else: # no result from query, no annotation
            html_str += tA1[0] + phrase_og + tA1[1]

        return html_str
    else:
        return None


def check_eligible(phrase):
    if [x for x in phrase if (not (x in punksAndNum))] != [] and len(phrase) > 2 and phrase.lower() != "not":
        return True
    else:
        return False


def preprocessing(contents):
    """
    Preprocess the contents by removing some special chars
    Parameters
    ----------
    contents: String, raw contents in the document

    Returns
    -------
    contents: cleaned string of content
    """
    contents = ' '.join(contents.split())  # reformat content
    contents = contents.replace('\0', '')  # remove null bytes
    contents = contents.replace('\'', '')  # remove quotation marks
    contents = contents.replace('\"', '')
    contents = contents.replace("\\", '')
    contents = contents.replace("/", ' or ')
    return contents


def stanford_annotator(content):
    return stannlp(content)


# Testing
if __name__ == '__main__':
    contents = "Atlanta. I am from China"
    annotationTypes = ['Place']

    inputFile = '/Users/gongchen/Emory_NLP/NLP-Suite/DBpedia_in/news.txt' # new copy.txt

    outputDir = '/Users/gongchen/Emory_NLP/NLP-Suite/DBpedia_out'
    inputDir = ''

    ### TEST query ####
    # phrase = "China"
    # query = form_query_string(phrase, annotationTypes)
    # res = get_result(query)
    # print(type(res))


    #########
    html_str = DBpedia_annotate(inputFile, inputDir, outputDir, annotationTypes)
    print(html_str)
