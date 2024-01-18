# Written by Gabriel Wang, Jack Hester and Cynthia Dong 2018-2019

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window,"CoReference Resolution",['os','tkinter','re'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import difflib as df
import tkinter as tk
from tkinter import *
import re

import IO_user_interface_util
import Stanford_CoreNLP_util
import reminders_util
import GUI_IO_util

# part of the code about search text function is adapted from
# https://www.geeksforgeeks.org/create-find-and-replace-features-in-tkinter-text-widget/
def createCorefCompareWindow(origin_display, coref_display, origin_non_coref, corefed_non_coref, root, result):
    top = Toplevel(root)
    # top.title("Comparing results from {0} LEFT: ORIGINAL text; in BLUE pronouns NOT corefed; in YELLOW pronouns corefed; RIGHT: COREFED text; in RED pronouns corefed; Edit text on the right and Save".format('Neural Network'))
    top.title("Corefed results compared (LEFT: ORIGINAL text; RIGHT: COREFED text). In BLUE pronouns NOT corefed; in RED pronouns corefed. EDIT text on the right. Use FIND bar to search text. CLOSE to exit and save changes".format('Neural Network'))
    # adding of single line text box
    topFrame = tk.Frame(top)
    topFrame.pack(fill="both", expand=False, side=tk.TOP, padx=300)
    searchBox = Entry(topFrame)
    searchBox.pack(fill = BOTH, expand=False)
    searchBox.focus_set()
    # adding of search button
    findButton = Button(topFrame, text ='Find', width=10)
    findButton.pack()
    closeButton = Button(topFrame, text ='Close', width=10)
    closeButton.pack()

    text1 = tk.Text(top, height=40, width=GUI_IO_util.widget_width_long)
    text1.pack(side=tk.LEFT)
    scroll = tk.Scrollbar(top, command=text1.yview)
    text1.configure(yscrollcommand=scroll.set)

    for i in range(len(origin_display)):
        each = origin_display[i]
        non_coref = origin_non_coref[i]
        text1.insert(tk.INSERT, each[0] + '\n')

        for highlight in each[1]:
            text1.tag_add("here",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text1.tag_config("here",
                             background="red", foreground="blue")
        for highlight in non_coref[1]:
            text1.tag_add("coref",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text1.tag_config("coref",
                             background="blue", foreground="yellow")

    text2 = tk.Text(top, height=40, width=GUI_IO_util.widget_width_long)
    scroll = tk.Scrollbar(top, command=text2.yview)
    text2.configure(yscrollcommand=scroll.set)

    for i in range(len(coref_display)):
        each = coref_display[i]
        text2.insert(tk.INSERT, each[0] + '\n')
        non_coref = corefed_non_coref[i]

        for highlight in each[1]:
            text2.tag_add("here",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text2.tag_config("here",
                             background="red", foreground="blue")
        for highlight in non_coref[1]:
            text2.tag_add("coref",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text2.tag_config("coref",
                             background="blue", foreground="yellow")

    text2.pack(side=tk.LEFT)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def exit_btn_save():
        result[0] = text2.get('1.0', tk.END)
        top.destroy()
        top.update()

    def exit_btn():
        global answer
        answer = tk.messagebox.askyesnocancel("Exit Manual Editing", "Do you want to SAVE any changes you have made in manual editing before quitting?")
        if answer: # save
            exit_btn_save()
        elif answer==False: # quit w/o saving
            top.destroy()
            top.update()
        return answer

    # function to search string in text
    def find():
        # remove tag 'found' from index 1 to END
        text2.tag_remove('found', '1.0', END)
        text1.tag_remove('found', '1.0', END)
        # returns to widget currently in focus
        s = searchBox.get()

        if (s):
            idx = '1.0'
            while 1:
                # searches for desired string from index 1
                idx = text2.search(s, idx, nocase = 1,
                                stopindex = END)
                if not idx: break
                # last index sum of current index and
                # length of text
                lastidx = '% s+% dc' % (idx, len(s))
                # overwrite 'Found' at idx
                text2.tag_add('found', idx, lastidx)
                idx = lastidx

            # mark located string as red
            text2.tag_config('found', foreground ='red', background='gainsboro')
            idx = '1.0'
            while 1:
                # searches for desired string from index 1
                idx = text1.search(s, idx, nocase=1,
                                   stopindex=END)
                if not idx: break
                # last index sum of current index and
                # length of text
                lastidx = '% s+% dc' % (idx, len(s))
                # overwrite 'Found' at idx
                text1.tag_add('found', idx, lastidx)
                idx = lastidx

            # mark located string as red
            text1.tag_config('found', foreground='red', background='gainsboro')
        searchBox.focus_set()

    findButton.config(command = find)

    closeButton.config(command = exit_btn)

    top.protocol("WM_DELETE_WINDOW", exit_btn)
    root.wait_window(top)
    return answer

caps = "([A-HJ-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|edu)"
digits = "([0-9])"

# personal_pronouns = [" i ", " me ", " my ", " you ", " she ", " her ", " he ", " him ",
#                      " we ", " us ", " they ", " them ", " he's ", " she's "]

# pronoun cases:
#   nominative: I, you, he/she, it, we, they
#   objective: me, you, him, her, it, them
#   possessive: my, mine, his/her(s), its, our(s), their, your, yours
#   reflexive: myself, yourself, himself, herself, oneself, itself, ourselves, yourselves, themselves

# pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "her", "him", "us", "them", "my", "mine",
#                      "hers", "his", "its", "our", "ours", "their", "your", "yours", "myself", "yourself", "himself", "herself",
#                      "oneself", "itself", "ourselves", "yourselves", "themselves"]

pronouns = r'\b(i|you|he|she|it|we|they|me|him|her|us|them|my|mine|hers|its|ours|their|your|yours|myself|yourself|himself|herself|oneself|itself|ourselves|yourselves|themselves)\b'

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def compare_results(origin_text,corefed_text):

    if '<@#' in corefed_text and '#@>' in corefed_text:
        # remove '<@# #@> first two lines in corefed_text; introduced in the CoreNLP_annotator
        corefed_text = "\n".join(corefed_text.split("\n")[2:])

    origin_sentences = split_into_sentences(origin_text)
    corefed_sentences = split_into_sentences(corefed_text)
    origin_display = []
    corefed_display = []
    origin_non_coref = []
    corefed_non_coref = []
    """
    SequenceMatcher gave matching point for each sentences;
    We use this to find the difference.
    """
    for i in range(0, min(len(corefed_sentences), len(origin_sentences))):
        origin_display_highlighted = []
        corefed_display_highlighted = []

        origin_len = 0
        corefed_len = 0

        # mark junk characters " ' tab and space
        s = df.SequenceMatcher(lambda x: x in " \'\t\"",
                               origin_sentences[i], corefed_sentences[i], autojunk=False)
        matching = s.get_matching_blocks()
        try:
            end = matching[1]
        except:
            mb.showwarning(title='Warning', message='The Co-Refereced output file generated by Stanford CoreNLP CoRef is too big to be displayed side-by-side with the original file, with pronouns highlighted in the orignal file (on the left panel) and the Co-Referenced form highlighted (on the right panel).\n\nManual editing cannot be done.\n\nIf you wish to carry out manual editing, you may wish to open the file manager and split the file into separate sub-files by a maximum number of words. Then, run the Co-Reference on the split files and merge the Co-Referenced output files.')
            return [], []

        for j in range(0, len(matching)):
            if origin_len != matching[j][0]:
                origin_display_highlighted.append((origin_len, matching[j][0]))
            if corefed_len != matching[j][1]:
                corefed_display_highlighted.append((corefed_len, matching[j][1]))
            origin_len = matching[j][0] + matching[j][2]
            corefed_len = matching[j][1] + matching[j][2]

        origin_display_tuple = (origin_sentences[i],
                                origin_display_highlighted)

        corefed_display_tuple = (corefed_sentences[i],
                                 corefed_display_highlighted)

        origin_display.append(origin_display_tuple)
        corefed_display.append(corefed_display_tuple)

        non_coref = []
        match = [(a.start(), a.end()) for a in list(re.finditer(pronouns, origin_sentences[i].lower()))]
        for m in match:
            # check if this match overlap with any text that is already highlighted
            overlap = False
            for highlighted in origin_display_highlighted:
                if (m[0] <= highlighted[0] <= m[1]) or (highlighted[0] <= m[0] <= highlighted[1]):
                    overlap = True
                    break
            if overlap == False:
                m_new = [m[0], m[1]]
                if origin_sentences[i][m_new[0]] == " ":
                    m_new[0] = m_new[0] + 1
                if origin_sentences[i][m_new[1]] == " ":
                    m_new[1] = m_new[1]
                non_coref.append(tuple(m_new))
        origin_non_coref.append((origin_sentences[i], non_coref))
        non_coref = []
        match = [(a.start(), a.end()) for a in list(re.finditer(pronouns, corefed_sentences[i].lower()))]
        for m in match:
            # check if this match overlap with any text that is already highlighted
            overlap = False
            for highlighted in corefed_display_highlighted:
                if (m[0] <= highlighted[0] <= m[1]) or (highlighted[0] <= m[0] <= highlighted[1]):
                    overlap = True
                    break
            if overlap == False:
                m_new = [m[0], m[1]]
                if corefed_sentences[i][m_new[0]] == " ":
                    m_new[0] = m_new[0] + 1
                if corefed_sentences[i][m_new[1]] == " ":
                    m_new[1] = m_new[1]
                non_coref.append(tuple(m_new))
        corefed_non_coref.append((corefed_sentences[i], non_coref))
    return origin_display, corefed_display, origin_non_coref, corefed_non_coref

# displays side-by-side the original and coreferenced file for manual editing
# return error indicator: 1 error; 0 no error
def manualCoref(original_file, corefed_file, outputFile):
    f = open(original_file, "r", encoding='utf-8', errors='ignore')
    original_text = f.read()
    f.close()
    f = open(corefed_file, "r", encoding='utf-8', errors='ignore')
    corefed_text = f.read()
    f.close()

    origin_display, corefed_display, origin_non_coref, corefed_non_coref = compare_results(original_text, corefed_text)
    # cannot do manual coref
    if len(corefed_display) == 0 and len(origin_display) == 0:
        return 1
    result = []
    result.append("\n".join(corefed_text.split("\n")[2:]))
    answer = createCorefCompareWindow(origin_display, corefed_display, origin_non_coref, corefed_non_coref, GUI_util.window, result)
    if answer==False: # use coreferenced text with no manual edits
        result[0]=corefed_text
    f = open(outputFile, "w", encoding='utf-8', errors='ignore')
    try:
        f.write(result[0])
    except:
        mb.showwarning(title='Warning',
                       message='The corefereced output file generated by Stanford CoreNLP CoRef is too big to be displayed side-by-side with the original file, with pronouns highlighted in the orignal file (on the left panel) and the coreferenced form highlighted (on the right panel).\n\nManual editing cannot be done.\n\nIf you wish to carry out manual editing, you may wish to open the file manager and split the file into separate sub-files by a maximum number of words. Then, run the coreference on the split files and merge the coreferenced output files.')
        f.close()
        return 1
    f.close()
    print("=======Finished Displaying Manual Editing=========")
    return 0

# return file_to_open
def run(config_filename,inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation,
        language_var, memory_var, export_json_var, manual_Coref):

    corefed_files = []
    errorFound = False

    # check that the CoreNLPdir as been setup
    CoreNLPdir, existing_software_config, errorFound = IO_libraries_util.external_software_install('Stanford_CoreNLP_coreference_util',
                                                                                         'Stanford CoreNLP',
                                                                                         '',
                                                                                         silent=False, errorFound=False)

    if CoreNLPdir==None or CoreNLPdir=='':
        return []

    # errorFound, error_code, system_output=IO_libraries_util.check_java_installation('CoreNLP coreference')
    # if errorFound:
    #     return filesToOpen, errorFound
    #
    if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_util.py') == False:
        return

    if inputDir!='':
        head, scriptName = os.path.split(os.path.basename(__file__))
        reminders_util.checkReminder(scriptName, reminders_util.title_options_CoreNLP_coref,
                                     reminders_util.message_CoreNLP_coref, True)

    corefed_files = Stanford_CoreNLP_util.CoreNLP_annotate(config_filename, inputFilename, inputDir,
                                                                    outputDir, openOutputFiles, chartPackage, dataTransformation,
                                                                    ['coref table','coref'], False,
                                                                    language_var, memory_var, export_json_var)

    if manual_Coref:
        if len(inputDir) == 0 and len(inputFilename) > 0:
            for file in corefed_files:
                if file[-4:] == ".txt":
                    error = manualCoref(inputFilename, file, file)
                    # return the corefed_files
        else:
            IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Feature Not Available', 'Manual Coreference is only available when processing single file, not input directory.')

    return corefed_files, errorFound
