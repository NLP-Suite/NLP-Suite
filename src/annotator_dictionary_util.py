"""
    Generates html files from input text files annotated with the use of dictionary terms
    by Jack Hester
    rewritten by Roberto Franzosi, Zhangyi Pan April 2020, Brett Landau October 2020
"""

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window,"annotator_dictionary_util",['os','re','csv'])==False:
    sys.exit(0)

import os
import re

import IO_files_util
import IO_user_interface_util
from csv import reader
import IO_csv_util

# the function associates specific values of a csv file to a specific color
def readCsv(wordColNum, catColNum, dictFile, csvValue_color_list):
    dictionary = []
    number_of_items = len(csvValue_color_list)
    num_cats = range(2,number_of_items,3)
    num_colors = range(3,number_of_items,3)
    # Add lists to dictionary for # of categories
    # Append a list to dictionary for however many categories exist
    # Need to parse categories and colors from csvValue_color_list
    color_list = []
    categories = []
    for i in num_cats:
        categories.append(csvValue_color_list[i])
        # We want a list in dictionary for each category we have
        dictionary.append([])
    for i in num_colors:
        color_list.append(csvValue_color_list[i])
    with open(dictFile, 'r', encoding='utf-8', errors='ignore') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            if len(categories)>0:
                # We check every line of the csv input to see if it matches one of the target categories
                for c in range(len(categories)):
                    # Check if the current row has category value equivalent to one of our categories
                    if row[catColNum] == categories[c]:
                        # dictionary[c] represents the list of words from category 'c'
                        if row[wordColNum] not in dictionary[c]:
                            dictionary[c].append(row[wordColNum])
            else:
                dictionary.append(row[wordColNum])

    return dictionary, color_list

# annotate words based on a list of terms from a csv file (dictionary)
# takes in file to annotate and list of terms to check against
# returns list of a list of terms with appropriate annotations for each file
# annotation allows custom tagging style (via csv, etc.)

def dictionary_annotate(inputFile, inputDir, outputDir, dict_file, csv_field1_var, csvValue_color_list, bold_var, tagAnnotations, fileType='.txt'):

    writeout = []
    filesToOpen = []

    files=IO_files_util.getFileList(inputFile, inputDir, fileType)
    nFile=len(files)
    if nFile==0:
        return
    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start', 'Started running Dictionary annotator at', True, 'You can follow Dictionary annotator in command line.')
    i=0
    wordColNum=0
    catColNum = 1
    if csv_field1_var!='':
        headers=IO_csv_util.get_csvfile_headers (dict_file)
        wordColNum=IO_csv_util.get_columnNumber_from_headerValue(headers,csv_field1_var)
        catColNum = wordColNum
    # if csv_field2_var!='':
    #     catColNum = IO_csv_util.get_columnNumber_from_headerValue(headers,csv_field2_var)
    dictionary, color_list = readCsv(wordColNum, catColNum, dict_file, csvValue_color_list)
    reserved_dictionary = ['bold', 'color', 'font', 'span', 'style', 'weight', 'black', 'blue', 'green', 'pink', 'yellow', 'red']
    # check the dictionary list if any of the reserved annotator terms (bold, color, font, span, style, weight) appear in the list
    #   reserved terms must be processed first to avoid replacing terms twice

    # loop through every txt file and annotate via dictionary
    for file in files:
        head, tail = os.path.split(file)
        i += 1
        print("Processing file " + str(i) + "/" + str(nFile) + " " + tail)
        text=open(file, 'r', encoding='utf-8',errors='ignore').read()
        # put filename in bold
        tail='<b>' + tail + '</b>'
        writeout.append(tail + '<br />\n')  # add the filename and a hard return
        termID = 0
        term_intextID = 0
        if len(csvValue_color_list) == 0:
            terms = dictionary
            # check reserved_dictionary list FIRST if any of the reserved annotator terms (bold, color, font, span, style, weight) appear in the list
            #   reserved terms must be processed first to avoid replacing terms twice
            # process reserved tag words first to avoid re-tagging already tagged words leading to tagging errors
            termID=0
            term_intextID=0
            for term in terms:
                termID=termID+1
                print("Processing dictionary field '" + csv_field1_var + "' " + str(termID) + "/" + str(len(terms)) + " " + term)
                if re.search(r'\b' + term + r'\b', text)==None:
                    continue
                for term1 in reserved_dictionary:
                    if term1 in dictionary:
                        tagString = tagAnnotations[0] + term1 + tagAnnotations[1]
                        # use regular expression replace to check for distinct words (e.g., he not tagging he in held)
                        # \b beginning and ending of word
                        # \w word character including numbers and characters
                        text = re.sub(rf"\b(?=\w){term1}\b(?!\w)", tagString, text)
                        # remove term from dictionary, to avoid double processing in next tagging
                        terms.remove(str(term1))
                        continue
                term_intextID=term_intextID+1
                print("   Annotating '" + term + "' in text " + str(term_intextID) + "/" + str(len(text)))
                tagString = tagAnnotations[0] + term + tagAnnotations[1]

                # use regular expression replace to check for distinct words (e.g., he not tagging he in held)
                text = re.sub(rf"\b(?=\w){term}\b(?!\w)", tagString, text)
        else:
            for i in range(len(dictionary)):
                terms = dictionary[i]
                color = color_list[i]
                if bold_var == True:
                    tagAnnotations = ['<span style=\"color: ' + color + '; font-weight: bold\">','</span>']
                else:
                    tagAnnotations = ['<span style=\"color: ' + color + '\">','</span>']
                for term in terms:
                    termID = termID + 1
                    print("Processing dictionary field value " + str(termID) + "/" + str(
                        len(terms)) + " " + term)
                    try:
                        if re.search(r'\b' + term + r'\b', text) == None:
                            continue
                    except:
                        continue
                    for term1 in reserved_dictionary:
                        if term1 in terms:
                            tagString = tagAnnotations[0] + term1 + tagAnnotations[1]
                            # use regular expression replace to check for distinct words (e.g., he not tagging he in held)
                            text = re.sub(rf"\b(?=\w){term1}\b(?!\w)", tagString, text)
                            # remove term from dictionary, to avoid double processing in next tagging
                            terms.remove(str(term1))
                            continue
                    term_intextID=term_intextID+1
                    print("   Annotating '" + term + "' in text " + str(term_intextID) + "/" + str(len(text)))
                    tagString = tagAnnotations[0] + term + tagAnnotations[1]
                    # use regular expression replace to check for distinct words (e.g., he not tagging he in held)
                    try:
                        text = re.sub(rf"\b(?=\w){term}\b(?!\w)", tagString, text)
                    except:
                        continue
        writeout.append(text)
        writeout.append("<br />\n<br />\n") # add 2 hard returns

    if fileType=='.html':
        if "_multiDict_annotated_" in file:
            outputFilename=file
        elif "NLP_DBpedia_annotated_dict_annotated_" in file:
            baseFilename=os.path.basename(os.path.normpath(file))[len("NLP_DBpedia_annotated_dict_annotated_"):]
            outputFilename="NLP_DBpedia_annotated_multiDict_annotated_"+baseFilename
            outputFilename=os.path.join(outputDir,outputFilename)
        elif "NLP_DBpedia_annotated_" in file:
            baseFilename=os.path.basename(os.path.normpath(file))[len("NLP_DBpedia_annotated_"):]
            outputFilename="NLP_DBpedia_annotated_dict_annotated_"+baseFilename
            outputFilename=os.path.join(outputDir,outputFilename)
        elif "NLP_dict_annotated_" in file:
            baseFilename=os.path.basename(os.path.normpath(file))[len("NLP_dict_annotated_"):]
            outputFilename="NLP_multiDict_annotated_"+baseFilename
            outputFilename=os.path.join(outputDir,outputFilename)
        else:
            outputFilename=file
    else:
        if inputDir!='':
            outputFilename=os.path.join(outputDir,"NLP_dict_annotated_" + os.path.basename(os.path.normpath(inputDir)) + '.html')
        else:
            outputFilename=os.path.join(outputDir,"NLP_dict_annotated_" + os.path.basename(os.path.normpath(file))[:-4] + '.html')
    filesToOpen.append(outputFilename)
    with open(outputFilename, 'w+',encoding='utf-8',errors='ignore') as f:
        f.write('<html>\n<body>\n<div>\n')
        for s in writeout:
            f.write(s)
        f.write('\n</div>\n</body>\n</html>')
    f.close()

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end', 'Finished running Dictionary annotator at', True)
    return filesToOpen

