#coding=utf-8

#Edited by Elaine Dong, Feb 2, 2020.
#Edited by Roberto Franzosi, November 2, 2019.

# The command line should be:
#ArgumentL: 1. path of the lynching folder 2.output path 3. path of stanfordcorenlp
########### 4. the base line for similarity. Below which value of similarity would you consider the file to be an intruder? Recommand around 0.15.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Find Non-related Documents",['stanza','stanfordcorenlp','os','tkinter','glob'])==False:
    sys.exit(0)

from stanfordcorenlp import StanfordCoreNLP # python wrapper for Stanford CoreNLP
import os
from glob import glob

import GUI_IO_util
import IO_files_util
import IO_csv_util

# from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza
filesToOpen = []

#This fuction reads the social actor list from the same directory
#and save that into a set called "my_soc_actors"
def load_soc_actors():
    fName= GUI_IO_util.wordLists_libPath + os.sep + 'social-actor-list.csv'
    my_soc_actors = set()
    if not os.path.isfile(fName):
        print("The file "+fileName+" could not be found. The routine expects a csv dictionary file 'social-actor-list.csv' in a directory 'lib' expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again.")
        mb.showerror(title='File not found', message='The routine expects a csv dictionary file "social-actor-list.csv" in a directory "lib" expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again')
        sys.exit()
    with open(fName, encoding='utf-8', errors='ignore') as fin:
        for line in fin:
                # save the list of "social actors"
                my_soc_actors.add(line.strip().split(',')[0])
    return my_soc_actors

#CM soc_acts is the input. I filtered out all social actors in dir_path
# Version 2: when we need to filter out NERs.
def get_article_soc_actors_NER(dir_path, soc_acts, nlp, keywords, num_doc):
    from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza
    my_files = glob(dir_path+'*.txt')
    for file in my_files:
        num_doc+=1
        with open(file, encoding='utf-8',errors='ignore') as fin:
            fcontent = fin.read()
        # store the file name
        fileName = file.split(os.path.sep)[-1]
        keywords[fileName] = {}
        postag_seen = set()
        #tokenize the article into words, and also filter out all the nouns and store them into "nouns"
        for word, pos in nlp.pos_tag(fcontent):
            # find out all the nouns
            if (pos == 'NN' or pos == 'NNS' ):
                # lemma_word to check if is social actor
                # lemma_word = lemmatizer.lemmatize(word.lower())
                lemma_word = lemmatize_stanza(stanzaPipeLine(word.lower()))
                if lemma_word in soc_acts:
                    #add into the list.
                    if lemma_word in keywords[fileName]:
                        keywords[fileName][lemma_word] = keywords[fileName][lemma_word] + 1
                        # reduce the size that is needed to detect NER. save time
                    else:
                        postag_seen.add(lemma_word)
                        keywords[fileName][lemma_word] = 1
        for wordNER, pos in nlp.ner(fcontent):
            if (pos == 'LOCATION' or pos == 'DATE' or pos == 'ORGANIZATION' or pos == 'PERSON'):
                # lemma_NER = lemmatizer.lemmatize(wordNER.lower())
                lemma_NER = lemmatize_stanza(stanzaPipeLine(wordNER.lower()))
                if lemma_NER not in postag_seen:
                    if lemma_NER in keywords[fileName]:
                        keywords[fileName][lemma_NER] = keywords[fileName][lemma_NER] + 1
                        # reduce the size that is needed to detect NER. save time
                    else:
                        keywords[fileName][lemma_NER] = 1
    return keywords, num_doc

def percent_belongs(one_doc, all_doc):
    numerator = 0
    list1_sum_squre = 0
    list2_sum_squre = 0
    for word, freq in one_doc.items():
        list1_sum_squre += freq * freq
        if word in all_doc:
            numerator += one_doc[word] * all_doc[word]
    for word, freq in all_doc.items():
        list2_sum_squre += freq * freq
    l1_sqrt = list1_sum_squre**0.5
    l2_sqrt = list2_sum_squre**0.5
    if l1_sqrt == 0 or l2_sqrt == 0:
        return 0
    cos_sim = round(numerator / (l1_sqrt * l2_sqrt), 2)
    return cos_sim

#if the document is an intruder
def check(dir_path, soc_acts,nlp, intruder_list,id_list, has_intruder, similarityIndex_base,freq_intruder, num_doc, terminal_output, f):
    parts = dir_path.split(os.path.sep)
    id = parts[-2]
    # keywords are a dictionary, with keys being the name of each article; values being a set of all social actors (NNP, NNPS) and NERs.
    compare = {}
    keywords, num_doc = get_article_soc_actors_NER(dir_path, soc_acts, nlp, {}, num_doc)
    # when there is only one document in one folder
    if len(keywords) == 1:
        return intruder_list,id_list, False,freq_intruder, num_doc
    similar = {}
    all_words = []
    for doc_name in keywords.keys():
        sys.stdout = terminal_output
        print("    Processing document: ",doc_name)
        sys.stdout = f
        compare[doc_name] = {}
    # create another dictionary. Structure: key is the filename, value is list of keywords that is from all the other files.
    for doc_name in keywords.keys():
        for this_doc in compare.keys():
            if this_doc != doc_name:
                for word in keywords[doc_name]:
                    if word in compare[this_doc]:
                        compare[this_doc][word] = compare[this_doc][word] + 1
                    else:
                        compare[this_doc][word] = 1
    for doc in keywords:
        a = keywords[doc]
        b = compare[doc]
        similar[doc] = percent_belongs(a,b)
    my_files = glob(dir_path + '*.txt')
    #the local intruder in this folder
    this_intrude = []
    #print out the results.
    #my_files = '\n'.join(map(lambda x: x.split(os.path.sep)[-1], my_files))
    for doc, similarity in similar.items():
        #We set the minimum index to 0.1 now.
        if similarity < similarityIndex_base:
            freq_intruder +=1
            has_intruder = True
            intruder_list.append(doc)
            this_intrude.append(doc)
            if (str(id)) not in id_list:
                id_list.append(str(id))
    if keywords == {}:
        print(id,",No txt document in the input folder.,,,,,,**************************************")
    elif has_intruder == False:
        return intruder_list,id_list, False,freq_intruder, num_doc
    else:
        repeat_star = True
        for doc in this_intrude:
            filePath=os.path.join(dir_path,doc)
            if repeat_star == True:

                print(id+","+str(len(keywords.keys()))+","+doc+","+IO_csv_util.dressFilenameForCSVHyperlink(dir_path)+","+IO_csv_util.dressFilenameForCSVHyperlink(filePath)+","+str(similar[doc])+",,**************************************")
                repeat_star = False
            else:
                print(id+","+str(len(keywords.keys()))+","+doc+","+IO_csv_util.dressFilenameForCSVHyperlink(dir_path)+","+IO_csv_util.dressFilenameForCSVHyperlink(filePath)+","+str(similar[doc]))
    return intruder_list,id_list, has_intruder,freq_intruder, num_doc

def main(CoreNLPDir, inputDir, outputDir,openOutputFiles, chartPackage, dataTransformation, similarityIndex_base):
    # similarityIndex_base = float(similarityIndex_base)
    ##
    ##This is just for evaluation purposes
    freq_intruded_folder = 0
    freq_intruder = 0
    intruder_list = []
    id_list = []
    ##End of evaluation
    if inputDir[-1] == '/':
        inputDir = inputDir[:-1]
    if outputDir[-1] == '/':
        outputDir = outputDir[:-1]
    outputFilename = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'SSR', 'INTRD', '', '', '', False, True)
    filesToOpen.append(outputFilename)
    f = open(outputFilename, 'w',encoding='utf-8',errors='ignore')
    terminal_output = sys.stdout
    sys.stdout = f
    print("Group identifier (Folder name),Documents in group,Intruder document,Group path,Document path,Similarity index ( <"+str(similarityIndex_base)+")")
    actors = load_soc_actors()
    dirs = glob(inputDir+'/*/')
    nlp = StanfordCoreNLP(CoreNLPDir)
    num_folder = 0
    num_doc = 0
    for dir in dirs:
        has_intruder = False
        sys.stdout = terminal_output
        print("Processing folder " + str(num_folder + 1) + "/" + str(len(dirs)) + "; Folder name: " + dir.split(os.path.sep)[-2])
        sys.stdout = f
        intruder_list,id_list, has_intruder,freq_intruder, num_doc = check(dir, actors, nlp, intruder_list,id_list, has_intruder, similarityIndex_base,freq_intruder, num_doc, terminal_output, f)
        if has_intruder == True:
            freq_intruded_folder+=1
        num_folder +=1
    sys.stdout = terminal_output
    print("Finished all " + str(num_folder) + " folders. Printing outputs now.")
    nlp.close()
    f.close()
    ##
    outputFilename = IO_files_util.generate_output_file_name('', inputDir, outputDir, '.csv', 'SSR', 'Intrud', 'freq', '', '', False, True)
    filesToOpen.append(outputFilename)

    f_e = open(outputFilename, 'w')
    sys.stdout = f_e
    if(len(intruder_list)<= 320):
        print("Similarity index cutoff,Number of intruders,Percentage of intruders among all documents for all groups (folders),Number of intruded groups (folders),Percentage of intruded groups (folders),List of intruded groups (folders),List of intruded documents")
        print(str(similarityIndex_base)+","+str(freq_intruder)+","+str(round((freq_intruder/num_doc)*100,2))+","+str(freq_intruded_folder)+","+str(round((freq_intruded_folder/num_folder)*100,2))+","+"; ".join(d.strip() for d in id_list)+","+"; ".join(d.strip() for d in intruder_list))
    elif(len(intruder_list)<= 640):
        print("Similarity index cutoff,Number of intruders,Percentage of intruders among all documents for all groups (folders),Number of intruded groups (folders),Percentage of intruded groups (folders),List of intruded groups (folders),List of intruded documents,Continued list of intruded documents")
        print(str(similarityIndex_base)+","+str(freq_intruder)+","+str(round((freq_intruder/num_doc)*100,2))+","+str(freq_intruded_folder)+","+str(round((freq_intruded_folder/num_folder)*100,2))+","+"; ".join(d.strip() for d in id_list)+","+"; ".join(d.strip() for d in intruder_list[:320])+","+"; ".join(c for c in intruder_list[320:]))
    else:
        print("Similarity index cutoff,Number of intruders,Percentage of intruders among all documents for all groups (folders),Number of intruded groups (folders),Percentage of intruded groups (folders),List of intruded groups (folders),List of intruded documents,Continued list of intruded documents,Continued list of intruded documents")
        print(str(similarityIndex_base)+","+str(freq_intruder)+","+str(round((freq_intruder/num_doc)*100,2))+","+str(freq_intruded_folder)+","+str(round((freq_intruded_folder/num_folder)*100,2))+","+"; ".join(d.strip() for d in id_list)+","+"; ".join(d.strip() for d in intruder_list[:320])+","+"; ".join(c for c in intruder_list[320:640])+","+"; ".join(c for c in intruder_list[640:]))
    f_e.close()
    sys.stdout = terminal_output
    # type "sys.stdout = terminal_out" before print

    # Nothing to plot; only one line in the output csv file

    return filesToOpen

if __name__ == '__main__':
    main()
