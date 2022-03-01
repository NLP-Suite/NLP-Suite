# Written by Gabriel Wang, Jack Hester and Cynthia Dong 2018-2019 

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"CoReference Resolution",['os','tkinter','re'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import difflib as df
import tkinter as tk
from tkinter import *
import re

import IO_user_interface_util
import Stanford_CoreNLP_annotator_util
import reminders_util

# part of the code about search text function is adapted from 
# https://www.geeksforgeeks.org/create-find-and-replace-features-in-tkinter-text-widget/
def createCompareWindow(origin_display, coref_display, origin_non_coref, root, result):
    top = Toplevel(root)
    top.title("Comparing result from {0} (Edit text on the right hand side and Save) - in BLUE pronouns not done; in YELLOW & RED pronouns done".format('Neural Network'))

    # adding of single line text box
    topFrame = tk.Frame(top)
    topFrame.pack(fill="both", expand=False, side=tk.TOP, padx=300)
    searchBox = Entry(topFrame)
    searchBox.pack(fill = BOTH, expand=False)
    searchBox.focus_set()
    # adding of search button
    findButton = Button(topFrame, text ='Find')
    findButton.pack()

    text1 = tk.Text(top, height=40, width=70)
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
                             background="yellow", foreground="blue")
        for highlight in non_coref[1]:
            text1.tag_add("coref",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text1.tag_config("coref",
                             background="blue", foreground="yellow")

    text2 = tk.Text(top, height=40, width=70)
    scroll = tk.Scrollbar(top, command=text2.yview)
    text2.configure(yscrollcommand=scroll.set)

    for i in range(len(coref_display)):
        each = coref_display[i]
        text2.insert(tk.INSERT, each[0] + '\n')

        for highlight in each[1]:
            text2.tag_add("here",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text2.tag_config("here",
                             background="red", foreground="blue")
    text2.pack(side=tk.LEFT)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def exit_btn_save():
        result[0] = text2.get('1.0', tk.END)
        top.destroy()
        top.update()

    def exit_btn():
        msgbox_save = tk.messagebox.askyesnocancel("Finish Manual Editing", "Do you want to QUIT manual editing without saving changes?")
        if msgbox_save:
            top.destroy()
            top.update()
        return
    
    # function to search string in text
    def find():
        # remove tag 'found' from index 1 to END
        text2.tag_remove('found', '1.0', END)
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
        searchBox.focus_set()
    findButton.config(command = find)

    bottomFrame = tk.Frame(top)
    bottomFrame.pack(fill="both", expand=True, side=tk.BOTTOM)
    tk.Button(bottomFrame, text="Quit", command=exit_btn).pack(side="left")
    tk.Button(bottomFrame, text="Save", command=exit_btn_save).pack(side="left")
    
    top.protocol("WM_DELETE_WINDOW", exit_btn)
    root.wait_window(top)

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

pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "her", "him", "us", "them", "my", "mine",
                     "hers", "his", "its", "our", "ours", "their", "your", "yours", "myself", "yourself", "himself", "herself",
                     "oneself", "itself", "ourselves", "yourselves", "themselves"]

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

        for j in range(0, len(matching) - 1):
            start = matching[j]
            end = matching[j + 1]

            origin_display_highlighted.append((start[0] + start[2] + origin_len,
                                               end[0] + origin_len))
            corefed_display_highlighted.append((start[1] + start[2] + corefed_len,
                                                end[1] + corefed_len))

        origin_len += end[0]
        corefed_len += end[1]

        origin_display_tuple = (origin_sentences[i],
                                origin_display_highlighted)

        corefed_display_tuple = (corefed_sentences[i],
                                 corefed_display_highlighted)

        origin_display.append(origin_display_tuple)
        corefed_display.append(corefed_display_tuple)

        non_coref = []
        for pronoun in pronouns:
            match = [(a.start(), a.end()) for a in list(re.finditer(pronoun, origin_sentences[i].lower()))]
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
                        m_new[1] = m_new[1] - 1
                    m_new[1] -= 1
                    non_coref.append(tuple(m_new))
        origin_non_coref.append((origin_sentences[i], non_coref))
    return origin_display, corefed_display, origin_non_coref


# return error indicator: 1 error; 0 no error
def manualCoref(original_file, corefed_file, outputFile):
    f = open(original_file, "r", encoding='utf-8', errors='ignore')
    original_text = f.read()
    f.close()
    f = open(corefed_file, "r", encoding='utf-8', errors='ignore')
    corefed_text = f.read()
    f.close()

    origin_display, corefed_display, origin_non_coref = compare_results(original_text, corefed_text)
    # cannot do manual coref
    if len(corefed_display) == 0 and len(origin_display) == 0:
        return 1
    result = []
    result.append("\n".join(corefed_text.split("\n")[2:])) 
    createCompareWindow(origin_display, corefed_display, origin_non_coref, GUI_util.window, result)
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
def run(config_filename,inputFilename, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts,
        memory_var, manual_Coref):

    corefed_file = []
    errorFound = False

    # check that the CoreNLPdir as been setup
    CoreNLPdir, missing_external_software=IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_coreference_util', 'Stanford CoreNLP')
    if CoreNLPdir==None:
        return filesToOpen

    # errorFound, error_code, system_output=IO_libraries_util.check_java_installation('CoreNLP coreference')
    # if errorFound:
    #     return filesToOpen, errorFound
    #
    if IO_libraries_util.check_inputPythonJavaProgramFile('Stanford_CoreNLP_annotator_util.py') == False:
        return
    # with only one input file
    if len(inputFilename)>0:
        base = os.path.basename(inputFilename)
        fileName = os.path.splitext(base)[0]

    else: # dir input
        reminders_util.checkReminder(config_filename, reminders_util.title_options_CoreNLP_coref,
                                     reminders_util.message_CoreNLP_coref, True)

    corefed_file = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(config_filename, inputFilename, input_main_dir_path,
                                                                    output_dir_path, openOutputFiles, createExcelCharts,
                                                                    ['coref', 'coref table'], False,
                                                                    memory_var)

    if manual_Coref:
        if len(input_main_dir_path) == 0 and len(inputFilename) > 0:
            for file in corefed_file:
                if file[-4:] == ".txt":
                    error = manualCoref(inputFilename, file, file)
                    # return the corefed_file
        else:
            IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'Feature Not Available', 'Manual Coreference is only available when processing single file, not input directory.')

    return corefed_file, errorFound
