#coding=utf-8

#Edited by Elaine Dong, Jan 30, 2021.

# this version uses cosine similarity.
import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"Find Non-related Documents",['stanza','tkinter','stanfordcorenlp','os','tkinter','glob'])==False:
    sys.exit(0)

from stanfordcorenlp import StanfordCoreNLP # python wrapper for Stanford CoreNLP
import os
from glob import glob
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util
import IO_csv_util
import IO_user_interface_util
import charts_util

# from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza

#This fuction reads the social actor list from the same directory
#and save that into a set called "my_soc_actors"
def load_soc_actors():
    fName= GUI_IO_util.wordLists_libPath + os.sep + 'social-actor-list.csv'
    my_soc_actors = set()
    if not os.path.isfile(fName):
        print("The file "+fileName+" could not be found. The routine expects a csv dictionary file 'social-actor-list.csv' in a directory 'lib' expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again.")
        mb.showerror(title='File not found', message='The routine expects a csv dictionary file "social-actor-list.csv" in a directory "lib" expected to be a subdirectory of the directory where the concreteness_analysis.py script is stored.\n\nPlease, check your lib directory and try again')
        sys.exit()
    with open(fName) as fin:
        for line in fin:
                # save the list of "social actors"
                my_soc_actors.add(line.strip().split(',')[0])
    return my_soc_actors

#CM soc_acts is the input. I filtered out all social actors in dir_path
# Version 2: when we need to filter out NERs.
def get_article_soc_actors_NER(dir_path, soc_acts, nlp, keywords, printing):
    from Stanza_functions_util import stanzaPipeLine, lemmatize_stanza
    my_files = glob(dir_path+'*.txt')
    num_doc = 0
    for file in my_files:
        num_doc += 1
        fcontent=open(file, encoding='utf-8',errors='ignore').read()
        # store the file name
        fileName = file.split(os.path.sep)[-1]
        if printing:
            print("    Processing document: ", fileName)
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

#Used cosine similarity to find relativity
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

def get_NER_POSTAG(dir, soc_acts, nlp, compare):
    compare[dir] = {}
    keywords, num_doc = get_article_soc_actors_NER(dir, soc_acts, nlp, {}, True)
    for docname, dict_of_words in keywords.items():
        for word, freq in dict_of_words.items():
            compare[dir][word] = freq
    return compare

def find(doc_dir, soc_acts, nlp, compare, sim_base, f, terminal_output):
    keywords, num_doc = get_article_soc_actors_NER(doc_dir, soc_acts, nlp, {}, False)
    num_unclass = 0
    num_class = 0
    num_multiclass = 0
    if keywords == {}:
        print("There is no text file in document path.")
    for doc in keywords:
        sys.stdout = terminal_output
        print("Processing document: ",doc)
        sys.stdout = f
        a = keywords[doc]
        num_target_dir = 0
        print_content = ""
        max_index = 0
        for each_folder in compare.keys():
            b = compare[each_folder]
            similarity = percent_belongs(a,b)
            if similarity > max_index:
                max_index = similarity
        for each_folder in compare.keys():
            b = compare[each_folder]
            similarity = percent_belongs(a,b)
            if similarity >= sim_base:
                if num_target_dir == 0:
                    print_content += (IO_csv_util.dressFilenameForCSVHyperlink(doc_dir + doc)+","+IO_csv_util.dressFilenameForCSVHyperlink(each_folder)+",")
                    if similarity == max_index:
                        print_content += "*"
                    print_content += (","+str(similarity))
                if num_target_dir == 1:
                    print_content += (",Repeated,**************************************\n"+IO_csv_util.dressFilenameForCSVHyperlink(doc_dir + doc)+","+IO_csv_util.dressFilenameForCSVHyperlink(each_folder)+",")
                    if similarity == max_index:
                        print_content += "*"
                    print_content += (","+str(similarity)+",Repeated")
                if num_target_dir == 2:
                    print(print_content)
                if num_target_dir > 1:
                    print_line = (IO_csv_util.dressFilenameForCSVHyperlink(doc_dir + doc)+","+IO_csv_util.dressFilenameForCSVHyperlink(each_folder)+",")
                    if similarity == max_index:
                        print_line += "*"
                    print_line += (","+str(similarity)+",Repeated")
                    print(print_line)
                num_target_dir += 1
        if num_target_dir == 0:
            print(IO_csv_util.dressFilenameForCSVHyperlink(doc_dir + doc)+",No target directory is found,,,Unclassified,**************************************")
            num_unclass += 1
        if num_target_dir == 1:
            print(print_content + ",Classified,**************************************")
            num_class += 1
        if num_target_dir == 2:
            print(print_content)
        if num_target_dir >1:
            num_multiclass += 1

    return num_doc, num_unclass, num_class, num_multiclass

# CoreNLPDir: the path to stanfordCoreNLP folder. example name is "stanford-corenlp-4.2.0"
# inputDir: the path to a folder that stores ungrouped documents in txt format.
# inputTargetDir: the path to a folder that stores several folders which contains several documents of the same target
def main(window, inputDir, inputTargetDir, outputDir, openOutputFiles, createCharts, chartPackage, relativity_threshold):

    filesToOpen = []
    # check that the CoreNLPdir has been setup
    CoreNLPDir, existing_software_config = IO_libraries_util.external_software_install('file_classifier_NER_util',
                                                                                         'Stanford CoreNLP',
                                                                                         '',
                                                                                         silent=False)
    if CoreNLPDir==None:
        return filesToOpen

    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start',
                                       'Started running the File Classifier by NER values at', True,
                                       '\n\nThe script will first build a dictionary of NER values for the documents in each subfolder, then process each unclassified document.  Please, be patient.',True)

    if inputDir[-1] != '/':
        inputDir = inputDir + '/'
    outputFilename = IO_files_util.generate_output_file_name('', inputTargetDir, outputDir, '.csv', 'SSR', 'NER_class', '', '', '', False, True)
    filesToOpen.append(outputFilename)
    f = open(outputFilename, 'w',encoding='utf-8',errors='ignore')
    terminal_output = sys.stdout
    sys.stdout = f
    print("Source document,Target directory,Highest index,Relativity index (>" + str(relativity_threshold) + "),Outcome")
    actors = load_soc_actors()
    dirs = glob(inputTargetDir+'/*/')
    if dirs==[]:
        mb.showwarning("Warning", "No target subdirectories.\n\nNo target subdirectories found in\n\n" + inputTargetDir + "\n\nPlease, check your target directory in the INPUT secondary directory in the IO widgets.")
        filesToOpen=[]
        sys.stdout = terminal_output
        return filesToOpen

    nlp = StanfordCoreNLP(CoreNLPDir)
    compare = {}
    num_folder = 0
    sys.stdout = terminal_output
    for dir in dirs:
        print("Processing folder " + str(num_folder + 1) + "/" + str(len(dirs)) + "; Folder name: " + dir.split(os.path.sep)[-2])
        compare = get_NER_POSTAG(dir, actors, nlp, compare)
        num_folder +=1
    print("Finished all " + str(num_folder) + " folders. Start to process documents now.")
    sys.stdout = f
    #compare stores: key- folder id; value: a set of words
    num_doc, num_unclass, num_class, num_multiclass  = find(inputDir, actors, nlp, compare, relativity_threshold, f, terminal_output)
    sys.stdout = terminal_output
    mb.showinfo(title="Final results",
                message=str(num_doc) + " SOURCE document processed\n" + \
                        str(num_class) + " SOURCE documents classified in TARGET subdirectories\n" + \
                        str(num_multiclass) + " SOURCE documents classified in MULTIPLE TARGET subdirectories\n" + \
                        str(num_unclass) + " SOURCE documents unclassified")

    print("Number of unclassified documents processed in input: " + str(num_doc))
    print("Number of classified documents in output: "+ str(num_class))
    print("Number of classified documents (with multiple targets) in output: "+ str(num_multiclass))
    print("Number of unclassified documents in output: "+ str(num_unclass))

    nlp.close()
    f.close()

    if createCharts == True:
        columns_to_be_plotted_xAxis=[]
        columns_to_be_plotted_yAxis=[[3, 3]]
        hover_label=''
        inputFilename = outputFilename
        chart_outputFilename = charts_util.run_all(columns_to_be_plotted_yAxis, inputFilename, outputDir,
                                                  outputFileLabel='SSR_NER_home',
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["pie"],
                                                  chart_title='Frequency Distribution of Find a Home Outcome',
                                                  column_xAxis_label_var='',
                                                  hover_info_column_list=hover_label,
                                                  count_var=1)
    if chart_outputFilename != None:
        if len(chart_outputFilename) > 0:
            filesToOpen.extend(chart_outputFilename)

    if openOutputFiles == True:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir)
        filesToOpen = []  # to avoid opening twice here and in calling fuunction

    return filesToOpen

if __name__ == '__main__':
    main()
