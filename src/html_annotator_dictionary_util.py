"""
    Generates html files from input text files annotated with the use of dictionary terms
    by Jack Hester
    rewritten by Roberto Franzosi, Zhangyi Pan April 2020, Brett Landau October 2020
"""

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"html_annotator_dictionary_util",['os','re','csv','tkinter'])==False:
    sys.exit(0)

import os
import re
import tkinter.messagebox as mb

import IO_files_util
import IO_user_interface_util
from csv import reader
import IO_csv_util


def _term_regex(term):
    """Build a whole-word regex for a dictionary term, to be used with re.IGNORECASE:
       - flexible whitespace inside multi-word terms (extra spaces / line breaks);
       - FrameNet '(particle)' notation treated as OPTIONAL (e.g. 'fall (upon)' matches 'fall' or 'fall upon');
       - all other characters escaped (hyphens, dots, ...).
       Replace matches via a function using m.group(0) so the text's original case/spacing is preserved."""
    pieces = []
    for piece in re.split(r'(\([^)]*\))', term.strip()):
        if not piece:
            continue
        if piece.startswith('(') and piece.endswith(')'):
            inner = piece[1:-1].split()
            if inner:
                pieces.append(r'(?:\s+' + r'\s+'.join(re.escape(w) for w in inner) + r')?')
        else:
            words = piece.split()
            if words:
                pieces.append(r'\s+'.join(re.escape(w) for w in words))
    core = ''.join(pieces)
    if not core:
        return None
    return r'\b(?=\w)' + core + r'\b(?!\w)'


def _expand_terms_by_lemma(terms, files):
    """Expand single-word dictionary terms with their inflected forms found in the corpus, using the Suite's
    config-aware basic NLP layer (basic_NLP_util.basic_nlp) - which tokenizes + lemmatizes with the package
    the user picked for basic functions (spaCy or Stanza), NO dependency parse. For each corpus token whose
    LEMMA matches a dictionary term's lemma, the token's SURFACE form is returned, so inflected forms
    (attacked, bombing, Attack) get tagged while the original text stays untouched. Multi-word terms are left
    to the phrase matcher. Returns [] (and warns) if the lemmatizer is unavailable -> exact-form fallback."""
    try:
        import basic_NLP_util
    except Exception as e:
        mb.showwarning(title='Lemma annotation',
                       message="Could not load the basic NLP layer for lemma annotation:\n\n%s\n\n"
                               "Falling back to exact-form matching." % e)
        return []

    # lemmatize the SINGLE-WORD dictionary terms (multi-word terms stay with the phrase matcher)
    dict_lemmas = set()
    for t in terms:
        t = str(t).strip()
        if not t or ' ' in t:
            continue
        pairs = basic_NLP_util.basic_nlp_lemmas(t)
        dict_lemmas.add((pairs[0][1] if pairs else t).lower())
    if not dict_lemmas:
        return []

    surfaces = set()
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as _fh:
                text = _fh.read()
        except Exception:
            continue
        for surface, lemma in basic_NLP_util.basic_nlp_lemmas(text):
            if lemma and lemma.lower() in dict_lemmas:
                s = surface.strip()
                if s:
                    surfaces.add(s)
    return sorted(surfaces)


# the function associates specific values of a csv file to a specific color
# append the function to allow multiple wordColNum and catColNum (cat for categories)
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
                    # go through all catCols
                    for i in range(len(catColNum)):
                        if row[catColNum[i]] == categories[c]:
                            # dictionary[c] represents the list of words from category 'c'
                            if row[wordColNum[i]] not in dictionary[c]:
                                dictionary[c].append(row[wordColNum[i]])
            else:
                for i in range(len(wordColNum)):
                    dictionary.append(row[wordColNum[i]])

    return dictionary, color_list

# annotate words based on a list of terms from a csv file (dictionary)
# takes in file to annotate and list of terms to check against
# returns list of a list of terms with appropriate annotations for each file
# annotation allows custom tagging style (via csv, etc.)
# NOTICE:
#   csv_field1_var ['Name']
#   csvValue_color_list should be a list, for gender is csvValue_color_list = [genderCol, '|', 'FEMALE', 'red', '|', 'MALE', 'blue', '|']
#   tagAnnotations is also a list, for gender  ['<span style="color: blue; font-weight: bold">', '</span>']
def dictionary_annotate(inputFile, inputDir, outputDir, configFileName, dict_file,
                        csv_field1_var, csvValue_color_list, bold_var, tagAnnotations, fileType='.txt', fileSubc='', lemmatize=False):
    writeout = []
    filesToOpen = []
    # TODO needs to check how csv_field1_var is passed when multiple fields are selected
    #   would need to use split()
    if isinstance(csv_field1_var,str):
        csv_field1_var=[csv_field1_var]
    files=IO_files_util.getFileList(inputFile, inputDir, fileType, silent=False, configFileName=configFileName)
    nFile=len(files)
    if nFile==0:
        return
    startTime=IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis start', 'Started running Dictionary annotator at',
                                                 True, '', True, '', True)
    i=0
    wordColNum = [0]
    catColNum = [1]
    if len(csv_field1_var) > 0:
        headers=IO_csv_util.get_csvfile_headers(dict_file)
        wordColNum = []
        for field in csv_field1_var:
            col = IO_csv_util.get_columnNumber_from_headerValue(headers,field, dict_file)
            if col == None:
                mb.showerror(title='Input file error',
                             message="The selected dictionary file\n\n" + dict_file + "\n\ndoes not contain the expected header \'" + str(csv_field1_var) + "\'\n\nPlease, select a different dictionary file and try again.")
                return
            wordColNum.append(col)
        catColNum = []
        # csvValue_color_list=[csvValue_color_list]
        if len(csvValue_color_list) > 0:
            # for field in str(csvValue_color_list[0]):
            #     catColNum.append(IO_csv_util.get_columnNumber_from_headerValue(headers, field, dict_file))
            field=csvValue_color_list[0]
            catColNum.append(IO_csv_util.get_columnNumber_from_headerValue(headers, field, dict_file))

    dictionary, color_list = readCsv(wordColNum, catColNum, dict_file, csvValue_color_list)
    # Lemma annotation: lemmatize the corpus (fast Stanza tokenize+lemma) and add the surface forms whose
    # LEMMA is a dictionary term, so inflected forms are tagged too - each in its ORIGINAL form (text untouched).
    if lemmatize and len(csvValue_color_list) == 0 and isinstance(dictionary, list):
        for surface in _expand_terms_by_lemma(dictionary, files):
            if surface not in dictionary:
                dictionary.append(surface)
    reserved_dictionary = ['bold', 'color', 'font', 'span', 'style', 'weight', 'black', 'blue', 'green', 'pink', 'yellow', 'red']
    # check the dictionary list if any of the reserved annotator terms (bold, color, font, span, style, weight) appear in the list
    #   reserved terms must be processed first to avoid replacing terms twice

    # PERFORMANCE: compile ONE combined regex per colour group (or one for a flat dictionary) ONCE, up
    # front, and tag every term in a SINGLE pass per file below. The old code ran a full-text re.sub
    # PER TERM PER FILE -- on a large corpus with thousands of dialogue terms that is files x terms
    # full-text scans (over an hour on Harry Potter). Terms are combined longest-first so a longer
    # phrase wins over a shorter substring at the same position; reserved HTML/CSS words (span, style,
    # color, colour names) are excluded so a later group's pass can't match inside an inserted
    # <span ...> tag -- which is what the old per-term reserved_dictionary pre-pass tried to prevent.
    # m.group(0) in the replacement preserves each match's original case/spacing.
    def _build_combined_regex(term_group):
        _reserved = set(w.lower() for w in reserved_dictionary)
        seen, alts = set(), []
        for t in sorted((str(x) for x in term_group), key=len, reverse=True):
            tl = t.strip().lower()
            if not tl or tl in seen or tl in _reserved:
                continue
            seen.add(tl)
            p = _term_regex(t)
            if p:
                alts.append('(?:%s)' % p)
        if not alts:
            return None
        try:
            return re.compile('|'.join(alts), re.IGNORECASE)
        except re.error as _e:
            print("Dictionary annotator: could not build the combined regex (%s)" % _e)
            return None

    _compiled_groups = []   # list of (compiled_regex, tagAnnotations)
    if len(csvValue_color_list) == 0:
        _rx = _build_combined_regex(dictionary)
        if _rx is not None:
            _compiled_groups.append((_rx, tagAnnotations))
    else:
        for _gi in range(len(dictionary)):
            _color = color_list[_gi]
            if bold_var == True:
                _tags = ['<span style=\"color: ' + _color + '; font-weight: bold\">', '</span>']
            else:
                _tags = ['<span style=\"color: ' + _color + '\">', '</span>']
            _rx = _build_combined_regex(dictionary[_gi])
            if _rx is not None:
                _compiled_groups.append((_rx, _tags))

    # loop through every txt file and annotate via dictionary
    for file in files:
        head, tail = os.path.split(file)
        i += 1
        print("Processing file " + str(i) + "/" + str(nFile) + " " + tail)
        with open(file, 'r', encoding='utf-8',errors='ignore') as _f:
            text = _f.read()
        # put filename in bold
        tail='<b>' + tail + '</b>'
        writeout.append('<@#' + tail +'#@>' +'<br />\n')  # add the embedded filename (embedded  in <@# so that the merged file can be split) and a hard return
        # Fast single-pass tagging: apply the pre-compiled combined regex(es) built once above -- ONE
        # pass per colour group per file, instead of a full-text re.sub PER TERM. Groups are applied in
        # order (as before), so an earlier group tags before a later one.
        for _rx, _tags in _compiled_groups:
            try:
                text = _rx.sub(lambda m, _t=_tags: _t[0] + m.group(0) + _t[1], text)
            except Exception as _e:
                print("   Dictionary annotator: a tagging pass failed on this file (%s)" % _e)
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
            outputFilename=os.path.join(outputDir,"NLP_dict_annotated_" + fileSubc + "_" + os.path.basename(os.path.normpath(inputDir)) + '.html')
        else:
            outputFilename=os.path.join(outputDir,"NLP_dict_annotated_" + fileSubc + "_" + os.path.basename(os.path.normpath(file))[:-4] + '.html')
    filesToOpen.append(outputFilename)
    with open(outputFilename, 'w+',encoding='utf-8',errors='ignore') as f:
        f.write('<html>\n<body>\n<div>\n')
        for s in writeout:
            f.write(s)
        f.write('\n</div>\n</body>\n</html>')

    IO_user_interface_util.timed_alert(GUI_util.window,2000,'Analysis end', 'Finished running Dictionary annotator at', True, '', True, startTime)
    return filesToOpen

