# Created on Thu Nov 21 09:45:47 2019
# @author: jack hester
# rewritten by Roberto Franzosi October 2021

import sys
from tracemalloc import start
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "knowledge_graph_DBpedia_util.py",
                                          ['os', 'SPARQLWrapper', 'requests', 'urllib', 'ssl', 'shutil']) == False:
    sys.exit(0)

import os
# import tkinter.messagebox as mb
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import requests
import urllib
import urllib.parse
from urllib.request import urlopen
from urllib import request, error
import ssl
# pip install pyOpenSSL
# pip install requests[security]
import shutil

import IO_user_interface_util
import file_splitter_ByLength_util
import IO_files_util
import IO_csv_util

"""
A simple python wrapper for DBpedia spotlight
This relies on DBpedia's own web server to run
It is also possible to create a local server via:

    1) wget http://downloads.DBpedia-spotlight.org/spotlight/DBpedia-spotlight-0.7.1.jar
    2) wget http://downloads.DBpedia-spotlight.org/2016-04/en/model/en.tar.gz
    3) tar xzf en.tar.gz
    4) java -jar DBpedia-spotlight-latest.jar en http://localhost:2222/rest
Eventual implementation of local server would be more reliable/faster...
...but would require extra downloads/setup on students' behalf
# The script handles text annotation via DBpedia (outputs html)
# inputDir is .txt files to annotate
# outputDir is location to save .html annotated files
# annotationTypes = ['Person','WrittenWork'] # example used in chong (fast)
# annotation types should be user-provided via GUI
# details on all supported annotation types can be found at: 
# https://github.com/DBpedia-spotlight/DBpedia-spotlight/wiki/User's-manual
# or at https://www.DBpedia-spotlight.org/demo/
"""

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
ssl._create_default_https_context = ssl._create_unverified_context

colormap = {}

Document = []
Phrase = []
Ontology_class = []
URL_link = []
Html_link = []


def DBpedia_annotate(inputFile, inputDir, outputDir, openOutputFiles, annotationTypes, colors, confidence_level=0.5):

    filesToOpen = []
    annotationOpts = ''
    splitTxtFileList = []


    annotationTypes = check_ontology(annotationTypes)
    map_color_ont(colors, annotationTypes)

    n = len(annotationTypes)
    if 'Thing' in annotationTypes:
        annotationOpts = ""
    else:
        for i in range(n):
            if i == n - 1:
                annotationOpts = annotationOpts + annotationTypes[i]
            else:
                annotationOpts = annotationOpts + annotationTypes[i] + ','
    # stores color options

    # loop through every file and annotate via request to DBpedia
    files = IO_files_util.getFileList(inputFile, inputDir, '.txt')
    nFile = len(files)
    if nFile == 0:
        return

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                   'Started running DBpedia Knowledge Graph at', True,
                                                   'Annotating types: ' + str(
                                                       annotationTypes) + '\nConfidence level: ' + str(
                                                       confidence_level),False)
    print('\n\nAnnotating types: ', annotationTypes, 'with confidence level', str(confidence_level))


    url_certificate = ssl.SSLContext()  # Only for url


    adjust = '\n\nIf DBpedia fails and returns in command line "The command line is too long", lower the value of the file size using the slider widget and try again.'
    if sys.platform == 'win32':
        defaultSize = 8000
        minsize = 4000
        maxsize = 30000
        message = 'Windows/DBpedia can process files of size smaller than the Windows command line. In Windows, 32767 seems to be the command line size but ' + str(
            defaultSize) + ' sometimes fails. ' + adjust
    else:
        defaultSize = 3000
        minsize = 3000
        maxsize = 100000
        message = 'Mac/DBpedia set a limit to the file size that it can process.' + adjust

    i = 0
    sizeErrorDisplayed = False
    for file in files:
        defaultSize = 8000 # start fresh with every document
        splitFileValue = defaultSize
        splitHtmlFileList = []
        numberOfSplitSubfiles = 0
        # initialize the listOfSplitFiles to the current file
        #   in case file needs to be split listOfSplitFiles will contain the list of split files
        listOfSplitFiles=[file]
        splitFilesDir=''
        # listOfSplitFiles.remove(file)
        j=0
        i = i + 1
        head, tail = os.path.split(file)
        print("Processing file " + str(i) + "/" + str(nFile) + " " + tail)
        # Windows error: The command line is too long.
        # 32767 characters max https://support.thoughtworks.com/hc/en-us/articles/213248526-Getting-around-maximum-command-line-length-is-32767-characters-on-Windows
        # https://stackoverflow.com/questions/3205027/maximum-length-of-command-line-string
        # https://stackoverflow.com/questions/55969620/how-do-i-fix-the-error-the-command-line-is-too-long-if-i-want-to-have-the-outp
        # https://stackoverflow.com/questions/49607998/the-command-line-is-too-longwindows
        contents = open(file, 'r', encoding='utf-8', errors='ignore').read()
        while j < len(listOfSplitFiles):
            doc=listOfSplitFiles[j]
            head, tail = os.path.split(doc)
            outFilename = os.path.join(outputDir,"NLP_DBpedia_annotated_" + tail[:-4] + '.html')
            if numberOfSplitSubfiles>0:
                if listOfSplitFiles[0] == file:
                    # do not process the first large file and process only split files
                    continue
                print('   Processing split file ' + str(j+1) + "/" + str(len(listOfSplitFiles)) + ' ' + tail + ' with DBpedia size ' + str(defaultSize))
                splitHtmlFileList.append(outFilename)
            contents = open(doc, 'r', encoding='utf-8', errors='ignore').read()

            contents = preprocessing(contents)
            REQUEST, HEADERS = spotlight_request(contents, annotationOpts, confidence_level)
            all_urls = []
            r = requests.get(url=REQUEST, headers=HEADERS)
            # print('RESPONSE r.status_code', r.status_code)
            # 200 = OK
            # 400 bad request
            # 414 line too long
            if r.status_code == requests.codes['ok']:
                has_annotation = False
                response = r.json()
                s = response.keys()
                if 'Resources' not in response.keys():
                    content = response['@text']
                    print("The current file doesn't have the ontology types")
                else:
                    has_annotation = True
                    resources = response['Resources']
                # try:
                #     resources = response['Resources']
                # except:
                #     IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Warning',
                #                                        'The DBpedia server may have time out while processing the document\n\n' + doc + '\n\nThe document will be ignored.')
                #     j = j + 1
                #     continue

                url = REQUEST
                # url_certificate = ssl.SSLContext()  # Only for url
                HTML_HEADERS = {'Accept': 'text/html'}
                content = requests.get(url=REQUEST, headers=HTML_HEADERS).text
                if has_annotation:
                    for res in resources:
                        all_urls.append(res['@URI'])

                    url_number = len(all_urls)
                    # print('      DBpedia resource',res['@URI'])
                # save locally the DBpedia annotated web output file
                    content = extract_html(content, annotationTypes, doc, url_number)
                with open(outFilename, 'w',encoding="utf-8",errors='ignore') as outfile:
                    try:
                        outfile.write(content)
                    except:
                        # IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Warning',
                        #                                    'An error was encountered saving the file\n\n' + outFilename +'\n\nThe file will be ignored.\n\nPlease, check your input txt file and try again.')
                        print('Error saving file ' + outFilename + ' File ignored. Check your input txt file.')
                outfile.close()
            else:
                if r.status_code == 414: # line too long
                    if sizeErrorDisplayed == False: # avoid repeating message
                        IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Warning',
                                                           'The DBpedia knowledge graph ran into a "line too long" error for document\n\n' + doc + '\n\nThe document will now be split for DBpedia.')
                        # mb.showwarning(title='Warning',
                        #                message='The DBpedia knowledge graph ran into a "line too long" error. The DBpedia server has a limit on chunk of text it can process. The document passed\n\n' + doc + '\n\nis too big for the server. The NLP Suite function will now split the document into parts and process each part separately and then put the annotated output back together automatically.')
                        # set error to avoid repeating warning for every file processed
                        sizeErrorDisplayed = True
                    print('   ERROR: Line too long (current split size ' + str(defaultSize) + '). The document will be split into sub-files.')
                    defaultSize=defaultSize-1000
                    splitFileValue=defaultSize
                    if defaultSize < 2000: # other errors have occurred
                        print('Split size below 2000. Algorithm exiting...')
                        return
                    listOfSplitFiles = file_splitter_ByLength_util.splitDocument_byLength(GUI_util.window, 'DBpedia',
                                                                                     doc, outputDir,
                                                                                     splitFileValue)

                    # get directory of split subfiles so that it can be deleted at the end
                    head, tail = os.path.split(listOfSplitFiles[0])
                    splitFilesDir = head
                    numberOfSplitSubfiles=len(listOfSplitFiles)
                    j=-1
            j = j + 1
        if numberOfSplitSubfiles > 0:
            # outFilename here is the combined html file from the split files
            outFilename = os.path.join(outputDir,
                                       "NLP_DBpedia_annotated_" + os.path.split(file)[1].split('.txt')[0] + '.html')
            with open(outFilename, 'w', encoding="utf-8", errors='ignore') as outfile:
                for htmlDoc in splitHtmlFileList:
                    # do not process the first large file and process only split files
                    if htmlDoc == outFilename:
                        continue
                    if os.path.exists(htmlDoc):
                        with open(htmlDoc,'r', encoding="utf-8",errors='ignore') as infile:
                            for line in infile:
                                outfile.write(line)
                            infile.close()
                    try:
                        os.remove(htmlDoc)  # delete temporary split html file from output directory
                    except:
                        continue
                outfile.close()
                # remove directory of split files
                if os.path.exists(splitFilesDir):
                    shutil.rmtree(splitFilesDir)
        j = 0
        numberOfSplitSubfiles=0
        HyperLinkedURL = []
        for link in URL_link:
            hyperLink = IO_csv_util.dressFilenameForCSVHyperlink(link)
            HyperLinkedURL.append(hyperLink)
        HyperLinkedDoc = []
        for doc in Document:
            hyperLinkedDoc = IO_csv_util.dressFilenameForCSVHyperlink(doc)
            HyperLinkedDoc.append(hyperLinkedDoc)

        df = pd.DataFrame(list(zip(Phrase,HyperLinkedURL,Ontology_class,HyperLinkedDoc)),columns=['Token','URL','Ontology class','Document'])

        # generate CSV file
        #
        # from datetime import datetime
        # from datetime import date
        # csvname= "DBpedia_output_"+date.today().strftime("%b_%d_%Y")+"_"+datetime.now().strftime("%H_%M_%S")+".csv"
        # csvname = os.path.join(outputDir,csvname)
        # df.to_csv((csvname),index=False)

        filesToOpen.append(outFilename)
        for k in range(len(Document)-len(Html_link)):
            Html_link.append(outFilename)

    from datetime import datetime
    from datetime import date
    csvname = "DBpedia_output_" + date.today().strftime("%b_%d_%Y") + "_" + datetime.now().strftime("%H_%M_%S") + ".csv"
    csvname = os.path.join(outputDir, csvname)
    # generate CSV file
    df = generate_csv()
    df.to_csv((csvname), index=False)
    filesToOpen.append(csvname)
    clear_cache()

    # add charts

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running DBpedia Knowledge Graph at',
                                       True, '', True, startTime)

    return filesToOpen


def generate_csv():
    HyperLinkedURL = []
    for link in URL_link:
        hyperLink = IO_csv_util.dressFilenameForCSVHyperlink(link)
        HyperLinkedURL.append(hyperLink)
    HyperLinkedDoc = []
    for doc in Document:
        hyperLinkedDoc = IO_csv_util.dressFilenameForCSVHyperlink(doc)
        HyperLinkedDoc.append(hyperLinkedDoc)
    Html_Hyper_Links = []
    for html in Html_link:
        hyperlinkedHtml = IO_csv_util.dressFilenameForCSVHyperlink(html)
        Html_Hyper_Links.append(hyperlinkedHtml)

    df = pd.DataFrame(list(zip(Phrase, HyperLinkedURL, Ontology_class, HyperLinkedDoc,Html_Hyper_Links)),
                      columns=['Token', 'URL', 'Ontology class', 'Document', 'Html'])



    return df




def map_color_ont(colors, ont_list):
    for idx, ont in enumerate(ont_list):
        colormap[ont] = colors[idx]

# Return spotlight query string
def spotlight_request(contents, annotationOpts, confidence_level):
    BASE_URL = 'http://api.dbpedia-spotlight.org/en/annotate?text={text}&confidence={confidence}&support={support}&types={annotationOpts}'
    CONFIDENCE = confidence_level
    SUPPORT = '20'
    REQUEST = BASE_URL.format(
        text=urllib.parse.quote_plus(contents),
        confidence=CONFIDENCE,
        support=SUPPORT,
        annotationOpts = annotationOpts
    )
    # print('REQUEST',REQUEST) # REQUEST contains the url to the html annotated input file
    HEADERS = {'Accept': 'application/json'}

    return REQUEST, HEADERS


# extract links from the entire html string so we can save links into csv files later
def extract_html(content, annotationTypes, doc, url_num):
    a_start = content.find('<a')
    a_end = content.find('</a>')
    prev = content[0:a_start]
    ta = content[a_start+3:a_end]
    post = content[a_end+4:]
    count = 1
    # print("PREV: ", prev)
    # print("\n")
    # print("POST: ", post)
    while 1:
        #find link
        print("  Extracting link " + str(count) + "/" + str(url_num))
        count += 1
        find_ont = False
        start_link = ta.find('\"')
        end_link = ta[start_link+1:].find('\"') + start_link
        url = ta[start_link+1:end_link + 1]
        # print("URL: ", url)
        # print(annotationTypes)
        for type in annotationTypes:
            request = form_request(url, type)
            res = get_request(request)
            # print(res)
            if res:
                ta = update_color(ta, type)
                find_ont = True
                prev = prev + ta
                update_csv(ta, type, doc, url)
                break
        if not find_ont:
            prev = prev + '<a ' + ta + '</a>'
        a_start = post.find('<a')
        a_end = post.find('</a>')
        if a_start < 0:
            break
        ta = post[a_start+3:a_end]
        prev = prev + post[0:a_start]
        post = post[a_end+4:]
        # print("******PREV\n:", prev)
        # print("*******POST\n", post)

    new_html = prev + post
    return new_html


def clear_cache():
    colormap.clear()

    Document.clear()
    Phrase.clear()
    Ontology_class.clear()
    URL_link.clear()
    Html_link.clear()



def update_csv(ta, type, doc,link):
    #find phrase
    start = ta.find('>')
    end = ta.find('</a>')
    phrase = ta[start+1:end]

    Document.append(doc)
    Phrase.append(phrase)
    Ontology_class.append(type)
    URL_link.append(link)

    return


def form_request(url, type):
    BASE_URL = 'https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query={QUERY}&format=application%2Fsparql-results%2Bjson&timeout=30000&signal_void=on&signal_unconnected=on'
    # HEADERS = {'Accept': 'application/json'}
    if type == "Thing":
        query = 'ASK { <' + url + '> rdf:type owl:Thing }'
    else:
        query = 'ASK { <' + url + '> rdf:type dbo:' + type + ' }'
    REQUEST = BASE_URL.format(
                    QUERY=urllib.parse.quote_plus(query),
                )
    # print(REQUEST)
    return REQUEST

def get_request(request):
    r = requests.get(url=request)
    response = r.json()
    # print(r.content)
    # print(type(r))
    # print(type(response["boolean"]))
    return response["boolean"]



def update_color(ta, type):
    prev = '<a'
    color = ' style=color:' + colormap[type] + ' '
    ta = '<a' + color + ta + '</a>'
    # print(ta)
    return ta


def get_query_res(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        print("Waiting for DBpedia response...")
        # print(query)
        results = sparql.query().convert()
        print("Received")

    except error.HTTPError:
        # this may occasionally give time out error depending upon server's traffic
        print(query)
        # mb.showwarning(title='Warning',
        #                message='Take a look at your command line/prompt. An HTTP error of 500 means that the YAGO server failed. Please, check command line/prompt for "Operation timed out" error\n\nTry running the script later, when the server may be be less busy.')
        return None
    except error.URLError:
        print(query)
        print("Query time out")
        return None

    print(results)

def check_ontology(annotationTypes):
    res = []
    for type in annotationTypes:
        if type != 'Thing':
            # s1 = type.split('>')
            # s2 = s1[1].split(' ')
            s1 = type.split(' ')
            type = s1[-1]
        # else:
        #     type = 'owl#Thing'
        res.append(type)
    n = len(annotationTypes)
    if n == 0:
        res = ['Thing', 'unknown']
    return res

def preprocessing(contents):
    contents = ' '.join(contents.split())  # reformat content
    contents = contents.replace('\0', '')  # remove null bytes
    contents = contents.replace('\'', '')  # remove quotation marks
    contents = contents.replace('\"', '')
    contents = contents.replace("\\", '')
    contents = contents.replace("/", ' or ')
    return contents




if __name__ == '__main__':
    # annotationTypes = [' > Place', ' > Person']
    # colors = ['green', 'red']
    annotationTypes = [' Place']
    colors = ['green']
    # inputFile = '/Users/gongchen/Emory_NLP/NLP-Suite/DBpedia_in/news.txt'  # new copy.txt
    inputFile = '/Users/gongchen/Emory_NLP/QTM446/POTUS speeches - UCSB-American Presidency Project/ina/ina_adams_3-04-1797.txt'
    outputDir = '/Users/gongchen/Emory_NLP/NLP-Suite/DBpedia_out'
    inputDir = ''


    ### TEST query ####
    # phrase = "China"
    # query = form_query_string(phrase, annotationTypes)
    # res = get_result(query)
    # print(type(res))

    #########
    outputfile = DBpedia_annotate(inputFile=inputFile, inputDir=inputDir,openOutputFiles=0, outputDir=outputDir, annotationTypes= annotationTypes, colors=colors)
    print(outputfile)

    # colormap['Place'] = 'red'
    # colormap['Person'] = 'blue'
    # # content = 'andy <a href="http://dbpedia.org/resource/David_Chase" title="http://dbpedia.org/resource/David_Chase" target="_blank">Chase</a> said he'
    # content = 'Randy Chase said he was visiting the area when he saw the waves rush onto the beach, pushing around large logs.<br/><br/>It was 3 bigger waves that pushed the high tide line up maybe 30 or 50 feet on this beach, said Chase.<br/><br/>An underwater <a href="http://dbpedia.org/resource/Tonga" title="http://dbpedia.org/resource/Tonga" target="_blank">Tongan</a> volcano erupted in the Pacific, triggering tsunami advisories at beaches and marinas across the'
    # new_html = extract_html(content, annotationTypes = ['Place', 'Person'])
    # print(new_html)
