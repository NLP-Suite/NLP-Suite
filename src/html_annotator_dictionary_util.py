"""
    Generates html files from input text files annotated with the use of dictionary terms
    by Jack Hester
    rewritten by Roberto Franzosi, Zhangyi Pan April 2020, Brett Landau October 2020
    code cleanup + optimization by Jerry Zhang @Jerrybibo, Feb 2022
"""

import sys

import IO_libraries_util
import GUI_util

if not IO_libraries_util.install_all_packages(GUI_util.window, "annotator_dictionary_util",
                                              ['os', 're', 'csv', 'tkinter']):
    sys.exit(0)

import os
import re
import tkinter.messagebox as mb
from csv import reader

import IO_files_util
import IO_user_interface_util
import IO_csv_util


# the function associates specific values of a csv file to a specific color
# extend the function to allow multiple wordColNum and catColNum
def read_csv(word_col_num, cat_col_num, dict_file, csv_value_color_list):

    dictionary = []

    number_of_items = len(csv_value_color_list)
    num_cats = range(2, number_of_items, 3)
    num_colors = range(3, number_of_items, 3)

    # Add lists to dictionary for # of categories
    # Append a list to dictionary for however many categories exist
    # Need to parse categories and colors from csvValue_color_list
    color_list, categories = [], []

    for i in num_cats:
        categories.append(csv_value_color_list[i])
        # We want a list in dictionary for each category we have
        dictionary.append([])

    for i in num_colors:
        color_list.append(csv_value_color_list[i])

    with open(dict_file, 'r', encoding='utf-8', errors='ignore') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            if len(categories) > 0:
                # We check every line of the csv input to see if it matches one of the target categories
                for c in range(len(categories)):
                    # Check if the current row has category value equivalent to one of our categories
                    # go through all catCols
                    for i in range(len(cat_col_num)):
                        if row[cat_col_num[i]] == categories[c]:
                            # dictionary[c] represents the list of words from category 'c'
                            if row[word_col_num[i]] not in dictionary[c]:
                                dictionary[c].append(row[word_col_num[i]])
            else:
                for i in range(word_col_num):
                    dictionary.append(row[word_col_num[i]])

    return dictionary, color_list


# annotate words based on a list of terms from a csv file (dictionary)
# takes in file to annotate and list of terms to check against
# returns list of a list of terms with appropriate annotations for each file
# annotation allows custom tagging style (via csv, etc.)
# NOTICE: csv_field1_var and first entry of csvValue_color_list should be a list
def dictionary_annotate(input_file, input_dir, output_dir, dict_file, csv_field1_var, csv_value_color_list, bold_var,
                        tag_annotations, file_type='.txt'):
    write_out, files_to_open = [], []

    files = IO_files_util.getFileList(input_file, input_dir, file_type)
    if len(files) == 0:
        return
    start_time = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis start',
                                                    'Started running Dictionary annotator at',
                                                    True, '', True, '', True)
    word_col_num, cat_col_num = [0], [1]

    if len(csv_field1_var) > 0:
        headers = IO_csv_util.get_csvfile_headers(dict_file)
        word_col_num = []
        for field in csv_field1_var:
            col = IO_csv_util.get_columnNumber_from_headerValue(headers, field)
            if col is None:
                mb.showerror(title='Input file error',
                             message="The selected dictionary file\n\n" + dict_file +
                                     "\n\ndoes not contain the expected header \'" + csv_field1_var +
                                     "\'\n\nPlease, select a different dictionary file and try again.")
                return
            word_col_num.append(col)
        cat_col_num = []
        if len(csv_value_color_list) > 0:
            for field in csv_value_color_list[0]:
                cat_col_num.append(IO_csv_util.get_columnNumber_from_headerValue(headers, field))

    dictionary, color_list = read_csv(word_col_num, cat_col_num, dict_file, csv_value_color_list)
    reserved_dictionary = ['bold', 'color', 'font', 'span', 'style', 'weight',
                           'black', 'blue', 'green', 'pink', 'yellow', 'red']
    # check the dictionary list if any of the reserved annotator terms
    # (bold, color, font, span, style, weight) appear in the list
    # reserved terms must be processed first to avoid replacing terms twice

    i = 0
    # loop through every txt file and annotate via dictionary
    for file in files:
        head, tail = os.path.split(file)
        i += 1
        print("Processing file " + str(i) + "/" + str(len(files)) + " " + tail)
        text = open(file, 'r', encoding='utf-8', errors='ignore').read()
        # put filename in bold
        tail = '<b>' + tail + '</b>'
        write_out.append(tail + '<br />\n')  # add the filename and a hard return
        term_id = 0
        term_in_text_id = 0
        if len(csv_value_color_list) == 0:
            terms = dictionary
            # check reserved_dictionary list FIRST if any of the reserved annotator terms
            # (bold, color, font, span, style, weight) appear in the list
            # reserved terms must be processed first to avoid replacing terms twice
            # process reserved tag words first to avoid re-tagging already tagged words leading to tagging errors
            term_id = 0
            term_in_text_id = 0
            for term in terms:
                term_id += 1
                print("Processing dictionary field '" + csv_field1_var + "' " + str(term_id) + "/" +
                      str(len(terms)) + " " + term)
                # TODO Optimization starts around here
                if re.search(r'\b' + term + r'\b', text) is None:
                    continue
                for reserved_term in reserved_dictionary:
                    if reserved_term in dictionary:
                        tagString = tag_annotations[0] + reserved_term + tag_annotations[1]
                        # TODO the what regex what now why how when just use replace
                        # use regular expression replace to check for distinct words (e.g., he not tagging he in held)
                        # \b beginning and ending of word
                        # \w word character including numbers and characters
                        text = re.sub(rf"\b(?=\w){reserved_term}\b(?!\w)", tagString, text)
                        # remove term from dictionary, to avoid double processing in next tagging
                        terms.remove(str(reserved_term))
                        continue

                term_in_text_id += 1
                print("   Annotating '" + term + "' in text " + str(term_in_text_id) + "/" + str(len(text)))
                tagString = tag_annotations[0] + term + tag_annotations[1]

                # use regular expression replace to check for distinct words
                # (e.g., not tagging "he" again when encountering "held")
                text = re.sub(rf"\b(?=\w){term}\b(?!\w)", tagString, text)
        else:
            for i in range(len(dictionary)):
                terms = dictionary[i]
                color = color_list[i]
                if bold_var:
                    tag_annotations = ['<span style=\"color: ' + color + '; font-weight: bold\">', '</span>']
                else:
                    tag_annotations = ['<span style=\"color: ' + color + '\">', '</span>']
                for term in terms:
                    term_id += 1
                    print("Processing dictionary field value " + str(term_id) + "/" + str(
                        len(terms)) + " " + term)
                    try:
                        if re.search(r'\b' + term + r'\b', text) is None:
                            continue
                    # Replace with proper Exception type
                    except BaseException:
                        continue
                    for reserved_term in reserved_dictionary:
                        if reserved_term in terms:
                            tagString = tag_annotations[0] + reserved_term + tag_annotations[1]
                            # use regular expression replace to check for distinct words
                            # (e.g., not tagging "he" again when encountering "held")
                            text = re.sub(rf"\b(?=\w){reserved_term}\b(?!\w)", tagString, text)
                            # remove term from dictionary, to avoid double processing in next tagging
                            terms.remove(str(reserved_term))
                            continue
                    term_in_text_id += 1
                    print("   Annotating '" + term + "' in text " + str(term_in_text_id) + "/" + str(len(text)))
                    tagString = tag_annotations[0] + term + tag_annotations[1]
                    # use regular expression replace to check for distinct words
                    # (e.g., not tagging "he" again when encountering "held")
                    try:
                        text = re.sub(rf"\b(?=\w){term}\b(?!\w)", tagString, text)
                    # Replace with proper Exception type
                    except BaseException:
                        continue
        write_out.append(text)
        write_out.append("<br />\n<br />\n")  # add 2 hard returns

    if file_type == '.html':
        if "NLP_DBpedia_annotated_dict_annotated_" in file:
            base_filename = os.path.basename(os.path.normpath(file))[len("NLP_DBpedia_annotated_dict_annotated_"):]
            output_filename = "NLP_DBpedia_annotated_multiDict_annotated_" + base_filename
            output_filename = os.path.join(output_dir, output_filename)
        elif "NLP_DBpedia_annotated_" in file:
            base_filename = os.path.basename(os.path.normpath(file))[len("NLP_DBpedia_annotated_"):]
            output_filename = "NLP_DBpedia_annotated_dict_annotated_" + base_filename
            output_filename = os.path.join(output_dir, output_filename)
        elif "NLP_dict_annotated_" in file:
            base_filename = os.path.basename(os.path.normpath(file))[len("NLP_dict_annotated_"):]
            output_filename = "NLP_multiDict_annotated_" + base_filename
            output_filename = os.path.join(output_dir, output_filename)
        else:
            output_filename = file
    else:
        if input_dir != '':
            output_filename = os.path.join(output_dir, "NLP_dict_annotated_" +
                                           os.path.basename(os.path.normpath(input_dir)) + '.html')
        else:
            output_filename = os.path.join(output_dir, "NLP_dict_annotated_" +
                                           os.path.basename(os.path.normpath(file))[:-4] + '.html')
    files_to_open.append(output_filename)
    with open(output_filename, 'w+', encoding='utf-8', errors='ignore') as f:
        f.write('<html>\n<body>\n<div>\n')
        for s in write_out:
            f.write(s)
        f.write('\n</div>\n</body>\n</html>')
    f.close()

    IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Analysis end',
                                       'Finished running Dictionary annotator at', True, '', True, start_time)
    return files_to_open
