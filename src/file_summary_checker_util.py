#coding=utf-8

#Edited by Elaine Dong, Feb 18, 2020. 
# The command line should be:
#Arguments: 1. path of the lynching folder 2. path of compilation folder 3.output path 4. path of stanfordcorenlp 5. whether or not you want to use NER to detect Named Entity Recognition (1 for yes, 0 for no)

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"Summary CoreNLP Checker",['nltk','stanfordcorenlp','os','tkinter','glob'])==False:
    sys.exit(0)

from stanfordcorenlp import StanfordCoreNLP
import os
from glob import glob
import IO_files_util
import GUI_IO_util
import charts_Excel_util
import IO_user_interface_util

# check WordNet
IO_libraries_util.import_nltk_resource(GUI_util.window,'corpora/WordNet','WordNet')
from nltk.stem.wordnet import WordNetLemmatizer
import tkinter.messagebox as mb

lemmatizer = WordNetLemmatizer()
filesToOpen = []
terminal_out = sys.stdout

#This fuction reads the social actor list from the same directory
#and save that into a set called "my_soc_actors"
def load_soc_actors(fName):
    my_soc_actors = set()
    with open(fName, encoding='utf-8',errors='ignore') as fin:
        for line in fin:
                # save the list of "social actors"
                my_soc_actors.add(line.strip().split(',')[0])
    return my_soc_actors

#CM soc_acts is the input. Filter out all social actors in dir_path
#Version 1: when we do not need to filter out the NERs 
def get_article_soc_actors(dir_path, soc_acts, nlp):
    my_files = glob(dir_path+'*.txt')
    #store all social actors in the artActors
    artActors = set()
    if len(my_files)==0:
        print("      No documents found in folder")
    for file in my_files:
        print("      Processing document: "+file.split(os.path.sep)[-1])
        fcontent = open(file, encoding='utf-8',errors='ignore').read()
        # nouns to store all nouns in article
        nouns = []
        #tokenize the article into words, and also filter out all the nouns and store them into "nouns"
        for word, pos in nlp.pos_tag(fcontent):
            # add nouns and use it to filter social actors later
            if (pos == 'NN' or pos == 'NNS'):
                word = lemmatizer.lemmatize(word.lower())
                nouns.append(word)
        # Store all the social actors in the filtered nouns into a set called "artActors" 
        for noun in nouns:
            if noun in soc_acts:
                artActors.add((noun, file.split(os.path.sep)[-1]))          
    return artActors

# Version 2: when we need to filter out NERs. 
def get_article_soc_actors_NER(dir_path, soc_acts, nlp):
    my_files = glob(dir_path+'*.txt')

    # Store all the social actors in the filtered nouns into a set called "artActors"
    artActors = set()
    #Interested: NER values of Location, Date, Person, Organization 
    art_location = set()
    art_date = set()
    art_person = set()
    art_org = set() # organization

    if len(my_files)==0:
        print("      No documents found in folder")
    for file in my_files:
        print("      Processing document: "+file.split(os.path.sep)[-1])
        fcontent = open(file, encoding='utf-8',errors='ignore').read()
        # store the file name
        fileName = file.split(os.path.sep)[-1]
        #tokenize the article into words, and also filter out all the nouns and store them into "nouns"
        for word, pos in nlp.pos_tag(fcontent):
            # find out all the nouns
            if (pos == 'NN' or pos == 'NNS' ):
                # lemma_word to check if is social actor
                lemma_word = lemmatizer.lemmatize(word.lower())
                if lemma_word in soc_acts:
                    #add into the list. 
                    artActors.add((lemma_word, fileName))
        for wordNER, pos in nlp.ner(fcontent):
            wordNER = lemmatizer.lemmatize(wordNER.lower())
            # if (pos == 'LOCATION'):
            if (pos == 'CITY') or (pos == 'STATE_OR_PROVINCE') or (pos == 'COUNTRY' or (pos == 'LOCATION')):
                if (wordNER, fileName) not in art_location and (wordNER, fileName) not in artActors:
                    art_location.add((wordNER, fileName))
            if (pos == 'DATE'):
                if (wordNER, fileName) not in art_date and (wordNER, fileName) not in artActors:
                    art_date.add((wordNER, fileName))
            if (pos == 'ORGANIZATION'):
                if (wordNER, fileName) not in art_org and (wordNER, fileName) not in artActors: 
                    art_org.add((wordNER, fileName))
                    #art_org.add((wordNER.encode("Windows-1252").decode("UTF-8", "ignore"), fileName))
            if (pos == 'PERSON'):
                if (wordNER, fileName) not in art_person and (wordNER, fileName) not in artActors:
                    art_person.add((wordNER, fileName))
    return artActors, art_location, art_date, art_org, art_person

def get_comp_soc_actors(id, soc_acts, c_path, nlp, checkNER):
    my_path = c_path+os.path.sep+ id + '.txt'
    print("   Processing compilation: "+id + '.txt')
    #read the compilation, and check that it is not an empty folder
    try:
        fcontent =open(my_path,'r',encoding="utf-8",errors='ignore').read()
    except IOError:
        print("")
        print("   Error: There is no compilation for event ID",id)
        print("")
        return set(), set(), set()
    # Do the same as the article, store all social actors in compActors (No need to filter out nouns) 
    tokens = nlp.word_tokenize(fcontent)
    compActors = set()
    #store all NERs.
    com_ner = set()
    com_date = set()
    #reduce token. So if one word is social actor already, no need to check ner
    reduce_token = []
    #lemma token is a no repeat word list. is used to compare with article's ner
    lemma_token = []
    for token in tokens: 
        lemma = lemmatizer.lemmatize(token.lower())
        if lemma in soc_acts:
            # add social actor
            compActors.add(lemma)
            # reduce the range of checking NER
            reduce_token.append(token)
        elif lemma not in lemma_token:
            # store the non-social-actor words. 
            lemma_token.append(lemma)
    if (checkNER == 1):
        #need lemmatize and lower case in order to compare with Article's ones
        for word, pos in nlp.ner(fcontent):
            if (pos == 'ORGANIZATION'):
                com_ner.add(lemmatizer.lemmatize(word.lower()))
            # if (pos == 'LOCATION' or pos == 'PERSON'):
            if (pos == 'PERSON') or (pos == 'CITY') or (pos == 'STATE_OR_PROVINCE') or (pos == 'COUNTRY') or (pos == 'LOCATION'):
                com_ner.add(lemmatizer.lemmatize(word.lower()))
            if (pos == 'DATE'):
                com_date.add(lemmatizer.lemmatize(word.lower()))
        return compActors, com_ner, com_date
    else:
        return compActors

#This method alllows me to add only distinct missing words. Combine the article sources. 
def addDistinct(addTargetTuple,missings, encode_wrong, article, comp_id,freq_miss, miss_list, id_miss,id):
    repeat = -1
    oldtuple = ()
    targetWord, targetArticle = addTargetTuple
    for tuples in missings:
        if (targetWord.lower() in tuples[0].lower()):
            repeat = 1
            oldtuple = tuples
    if repeat == 1:
        missings.remove(oldtuple)
        new_art = oldtuple[1]+", "+targetArticle
        new_tuple = (targetWord, new_art)
        missings.append(new_tuple)
        if article not in miss_list:
            miss_list.append(article)
    else:
        missings.append(addTargetTuple)
        ## for evaluation 
        ##
        freq_miss +=1
        if article not in miss_list:
            miss_list.append(article)
        if comp_id not in id_miss:
            id_miss.append(str(id)+'.txt')
        # freq table
    return missings, freq_miss, miss_list ,id_miss

#if the social actors in article are not in Compilation, add it is missing


def check(dir_path, soc_acts, nlp, compilation_path, checkNER, freq_act_miss, act_miss_list, id_act_miss, freq_loc_miss, loc_miss_list, id_loc_miss, freq_org_miss, org_miss_list, id_org_miss, freq_per_miss, per_miss_list, id_per_miss, freq_date_miss, date_miss_list, id_date_miss):
    
    if_act = False
    if_loc = False
    if_per = False
    if_org = False
    if_date = False

    csv_out = sys.stdout
    parts = dir_path.split(os.path.sep) 
    id = parts[-2]
    comp_id = str(id)+'.txt'
    # get the social actors from article and compilation 
    sys.stdout = terminal_out
    if (checkNER == 1):
        article_actors, a_loc, a_date, a_org, a_per = get_article_soc_actors_NER(dir_path, soc_acts, nlp)
        comp_actors, comp_ner, comp_date = get_comp_soc_actors(id, soc_acts, compilation_path, nlp, checkNER)
    else:
        article_actors = get_article_soc_actors(dir_path, soc_acts, nlp)
        comp_actors = get_comp_soc_actors(id, soc_acts, compilation_path, nlp, checkNER)
    missings = []
    # add the missing words in "missing"
    for act_tup in article_actors:
        article_act, article = act_tup
        if article_act not in comp_actors:
            if_act = True
            missings, freq_act_miss, act_miss_list , id_act_miss = addDistinct(act_tup, missings, 0, article, comp_id,freq_act_miss, act_miss_list , id_act_miss,id )
    # when we need to check each NERs
    if (checkNER == 1):
        for Locs in a_loc:
            loc, article = Locs
            if loc not in comp_ner:
                if_loc = True
                missings, freq_loc_miss, loc_miss_list , id_loc_miss = addDistinct(Locs, missings, 0, article, comp_id,freq_loc_miss, loc_miss_list , id_loc_miss,id)
        for Dates in a_date:
            Date, article = Dates
            if Date not in comp_date:
                if_date = True
                missings , freq_date_miss, date_miss_list , id_date_miss= addDistinct(Dates, missings, 0, article, comp_id,freq_date_miss, date_miss_list , id_date_miss,id)
        for Orgs in a_org:
            org, article = Orgs
            if org not in comp_ner:
                if_org = True
                missings, freq_org_miss, org_miss_list , id_org_miss = addDistinct(Orgs, missings, 1, article, comp_id, freq_org_miss, org_miss_list , id_org_miss,id )
        for Persons in a_per:
            person, article = Persons
            if person not in comp_ner:
                if_per = True
                missings, freq_per_miss, per_miss_list , id_per_miss = addDistinct(Persons, missings, 0, article, comp_id, freq_per_miss, per_miss_list , id_per_miss,id)
    my_files = glob(dir_path + '*.txt')
    sorted_missing = sorted(missings, key=lambda x:x[0]) 
    #print out the results. 
    my_files = '\n            '.join(map(lambda x: x.split(os.path.sep)[-1], my_files))
    sys.stdout = csv_out
    if article_actors == set():
        print("*******************************************************************************************************************************************************")
        print("Group Identifier: ", id)
        print(",,,,,No document in the input folder.")
    elif comp_actors == set():
        print("*******************************************************************************************************************************************************")
        print("Group Identifier: ", id)
        print(",,,,,No compilation. Can't compare")
    else:
        print("*******************************************************************************************************************************************************")
        print("Group Identifier: ", id)
        print("    Compilation Filename: "+id+'.txt')
        print("        Input Documents:")
        print("           ", my_files)
        print("                Missing Words,Input Documents")
        for missing in sorted_missing:
            print('"                    '+missing[0]+'"', end=',')
            print('"'+missing[1]+'"')
    return freq_act_miss,act_miss_list,id_act_miss,freq_loc_miss,loc_miss_list,id_loc_miss,freq_org_miss,org_miss_list,id_org_miss,freq_per_miss,per_miss_list,id_per_miss,freq_date_miss,date_miss_list,id_date_miss, if_act, if_loc, if_org, if_per, if_date

def main(CoreNLPDir, input_main_dir_path,input_secondary_dir_path,outputDir,openOutputFiles, createCharts, chartPackage, checkNER=False):
    articles_path = input_main_dir_path
    compilations_path = input_secondary_dir_path # summaries folder
    filesToOpen=[]

    startTime=IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running MISSING CHARACTER at',
                                       True, '', True, '', True)

    if len(articles_path)==0:
        mb.showerror(title='Articles directory not found', message='The summary checker script requires an input files directory.\n\nNo directory entered. Please, select the input files directory and try again.')
        sys.exit()

    if len(compilations_path)==0:
        tk.messagebox.showerror(title='Summary directory not found', message='The summary checker script requires a secondary input directory for the summary files.\n\nNo secondary directory entered. Please, select the secondary input directory and try again.')
        sys.exit()

    if len(outputDir)==0:
        mb.showerror(title='Output directory not found', message='The summary checker script requires an output directory.\n\nNo output directory entered. Please, select the output directory and try again.')
        sys.exit()

    if compilations_path[-1] == os.sep:
        compilations_path = compilations_path[:-1]
    if outputDir[-1] == os.sep:
        outputDir = outputDir[:-1]
    
    #############################
    ##This is just for evaluation purposes
    freq_act_miss = 0
    count_act_miss = 0
    act_miss_list = []
    id_act_miss = []
    freq_loc_miss = 0
    count_loc_miss = 0
    loc_miss_list = []
    id_loc_miss = []
    freq_org_miss = 0
    count_org_miss = 0
    org_miss_list = []
    id_org_miss = []
    freq_per_miss = 0
    count_per_miss = 0
    per_miss_list = []
    id_per_miss = []
    freq_date_miss = 0
    count_date_miss = 0
    date_miss_list = []
    id_date_miss = []
    ##End of evaluation
    #############################
    #write the output csv. 


    if checkNER == 1:
        outputFilename = IO_files_util.generate_output_file_name('',compilations_path, outputDir, '.csv', 'SSR', 'MA', 'NER', '', '', False, True)
    else:
        outputFilename = IO_files_util.generate_output_file_name('', compilations_path, outputDir, '.csv', 'SSR', 'MA', '', '', '', False, True)
    fName=GUI_IO_util.libPath+os.sep+'wordLists'+os.sep+'social-actor-list.csv'
    if not os.path.isfile(fName):
        print("The file "+fName+" could not be found. The routine expects a csv dictionary file 'social-actor-list.csv' in a directory 'lib\wordLists' expected to be a subdirectory of the main NLP directory.\n\nPlease, check your lib\wordLists directory and try again.")
        mb.showerror(title='File not found', message='The file '+fName+" could not be found.\n\nThe routine expects a csv dictionary file 'social-actor-list.csv' in a directory 'lib\wordLists' expected to be a subdirectory of the main NLP directory.\n\nPlease, check your lib\wordLists directory and try again.")
        sys.exit()
    actors = load_soc_actors(fName)
    f = open(outputFilename, 'w', encoding='utf-8',errors='ignore')
    sys.stdout = f
    dirs = glob(articles_path+os.sep + '*' + os.sep)
    nlp = StanfordCoreNLP(CoreNLPDir)
    num_id = 0
    num_dir = 0
    for compilation in glob(compilations_path+os.sep+'*'):
        num_id += 1
    for dir in dirs:
        sys.stdout = terminal_out
        print("Processing folder " + str(num_dir + 1) + "/" +
              str(len(dirs)) + "; Folder name: " + dir.split(os.path.sep)[-2])
        num_dir += 1
        sys.stdout = f
        try:
            count_act_miss, act_miss_list, id_act_miss, count_loc_miss, loc_miss_list, id_loc_miss, count_org_miss, org_miss_list, id_org_miss, count_per_miss, per_miss_list, id_per_miss, count_date_miss, date_miss_list, id_date_miss, if_act, if_loc, if_org, if_per, if_date = check(
                dir, actors, nlp, compilations_path, checkNER, count_act_miss, act_miss_list, id_act_miss, count_loc_miss, loc_miss_list, id_loc_miss, count_org_miss, org_miss_list, id_org_miss, count_per_miss, per_miss_list, id_per_miss, count_date_miss, date_miss_list, id_date_miss)
        except:
            print('         Unspecified error in processing the file')
            continue
        #############################
        #for evaluation
        if if_act == True:
            freq_act_miss += 1
        if if_per == True:
            freq_per_miss += 1
        if if_loc == True:
            freq_loc_miss += 1
        if if_org == True:
            freq_org_miss += 1
        if if_date == True:
            freq_date_miss += 1
        #############################
    nlp.close()
    ##
    ##This is to print out evaluation table
    if checkNER == 1:
        outputFilename = IO_files_util.generate_output_file_name('', compilations_path, outputDir, '.csv', 'SSR', 'MA', 'NER', 'freq', '', False, True)
    else:
        outputFilename = IO_files_util.generate_output_file_name('', compilations_path, outputDir, '.csv', 'SSR', 'MA', 'freq', '', '', False, True)
    f_e = open(outputFilename, 'w', encoding='utf-8',errors='ignore')
    sys.stdout = f_e
    if(len(act_miss_list)<= 320 and len(loc_miss_list)<= 320 and len(per_miss_list)<= 320 and len(org_miss_list)<= 320 and len(date_miss_list)<= 320):
        print("Type of Error,Frequency of Summaries in Error,Percentage of Summaries in Error,Frequency of Error,List of Summary Filenames for Type of Error,List of Documents for Type of Error")
        print("Social Actor,",str(freq_act_miss),",",freq_act_miss/num_id*100,",",count_act_miss,",","; ".join(a for a in id_act_miss),",", "; ".join(c for c in act_miss_list))
        print("Organization,",str(freq_org_miss),",",freq_org_miss/num_id*100,",",count_org_miss,",","; ".join(b for b in id_org_miss),",","; ".join(d for d in org_miss_list))
        print("Person,",str(freq_per_miss),",",freq_per_miss/num_id*100,",",count_per_miss,",","; ".join(b for b in id_per_miss),",","; ".join(d for d in per_miss_list))
        print("Date,",str(freq_date_miss),",",freq_date_miss/num_id*100,",",count_date_miss,",","; ".join(b for b in id_date_miss),",","; ".join(d for d in date_miss_list))
        print("Location,",str(freq_loc_miss),",",freq_loc_miss/num_id*100,",",count_loc_miss,",","; ".join(b for b in id_loc_miss),",","; ".join(d for d in loc_miss_list))
    elif(len(act_miss_list)<= 640 and len(loc_miss_list)<= 640 and len(per_miss_list)<= 640 and len(org_miss_list)<= 640 and len(date_miss_list)<= 640):
        print("Type of Error,Frequency of Summaries in Error,Percentage of Summaries in Error,Frequency of Error,List of Summary Filenames for Type of Error,List of Documents for Type of Error (Cut List),List of Documents for Type of Error (Continue List)")
        print("Social Actor,",str(freq_act_miss),",",freq_act_miss/num_id*100,",",count_act_miss,",","; ".join(a for a in id_act_miss),",", "; ".join(c for c in act_miss_list[:320]),",","; ".join(c for c in act_miss_list[320:]))
        print("Organization,",str(freq_org_miss),",",freq_org_miss/num_id*100,",",count_org_miss,",","; ".join(b for b in id_org_miss),",","; ".join(d for d in org_miss_list[:320]),",","; ".join(d for d in org_miss_list[320:]))
        print("Person,",str(freq_per_miss),",",freq_per_miss/num_id*100,",",count_per_miss,",","; ".join(b for b in id_per_miss),",","; ".join(d for d in per_miss_list[:320]),",","; ".join(d for d in per_miss_list[320:]))
        print("Date,",str(freq_date_miss),",",freq_date_miss/num_id*100,",",count_date_miss,",","; ".join(b for b in id_date_miss),",","; ".join(d for d in date_miss_list[:320]),",","; ".join(d for d in date_miss_list[320:]))
        print("Location,",str(freq_loc_miss),",",freq_loc_miss/num_id*100,",",count_loc_miss,",","; ".join(b for b in id_loc_miss),",","; ".join(d for d in loc_miss_list[:320]),",","; ".join(d for d in loc_miss_list[320:]))
    else:
        print("Type of Error,Frequency of Summaries in Error,Percentage of Summaries in Error,Frequency of Error,List of Summary Filenames for Type of Error,List of Documents for Type of Error (Cut List),List of Documents for Type of Error (Continue List),List of Documents for Type of Error (Continue List)")
        print("Social Actor,",str(freq_act_miss),",",freq_act_miss/num_id*100,",",count_act_miss,",","; ".join(a for a in id_act_miss),",", "; ".join(c for c in act_miss_list[:320]),",","; ".join(c for c in act_miss_list[320:640]),",","; ".join(c for c in act_miss_list[640:]))
        print("Organization,",str(freq_org_miss),",",freq_org_miss/num_id*100,",",count_org_miss,",","; ".join(b for b in id_org_miss),",","; ".join(d for d in org_miss_list[:320]),",","; ".join(d for d in org_miss_list[320:640]),",","; ".join(c for c in org_miss_list[640:]))
        print("Person,",str(freq_per_miss),",",freq_per_miss/num_id*100,",",count_per_miss,",","; ".join(b for b in id_per_miss),",","; ".join(d for d in per_miss_list[:320]),",","; ".join(d for d in per_miss_list[320:640]),",","; ".join(c for c in per_miss_list[640:]))
        print("Date,",str(freq_date_miss),",",freq_date_miss/num_id*100,",",count_date_miss,",","; ".join(b for b in id_date_miss),",","; ".join(d for d in date_miss_list[:320]),",","; ".join(d for d in date_miss_list[320:640]),",","; ".join(c for c in date_miss_list[640:]))
        print("Location,",str(freq_loc_miss),",",freq_loc_miss/num_id*100,",",count_loc_miss,",","; ".join(b for b in id_loc_miss),",","; ".join(d for d in loc_miss_list[:320]),",","; ".join(d for d in loc_miss_list[320:640]),",","; ".join(c for c in loc_miss_list[640:]))
    f_e.close()
    # type "sys.stdout = terminal_out" before print
    sys.stdout = terminal_out
    if createCharts:
        if checkNER == 1:
            fileType='SSR_summary_NER'
        else:
            fileType='SSR_summary'

        columns_to_be_plotted = [[0, 1], [0, 2], [0, 3]]
        hover_label = ['List of Summary Filenames for Type of Error',
                       'List of Summary Filenames for Type of Error',
                       'List of Summary Filenames for Type of Error']
        inputFilename = outputFilename
        chart_outputFilename = charts_Excel_util.run_all(columns_to_be_plotted, inputFilename, outputDir,
                                                  outputFileLabel=fileType,
                                                  chartPackage=chartPackage,
                                                  chart_type_list=["bar"],
                                                  chart_title='Missing Character (File Summaries in Error)',
                                                  column_xAxis_label_var='Type of Error',
                                                  hover_info_column_list=hover_label)
        if chart_outputFilename != "":
            filesToOpen.append(chart_outputFilename)


    if openOutputFiles:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen)
        filesToOpen=[] # avoid opening twice in the calling function

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running MISSING CHARACTER at',
                                       True,'',True,startTime,True)

    return filesToOpen

if __name__ == '__main__':
    main()
