# Written by Gabriel Wang, Jack Hester and Cynthia Dong 2018-2019 

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"CoReference Resolution",['os','tkinter','stanfordcorenlp','re'])==False:
    sys.exit(0)

import os
import tkinter.messagebox as mb
import difflib as df
import tkinter as tk
from tkinter import *
import re

import Stanford_CoreNLP_annotator_util

def createCompareWindow(origin_display, coref_display, coref_method, root, result):
    top = Toplevel(root)
    top.title("Comparing result from {0} (Edit text on the right hand side and Save)".format(coref_method))
    text1 = tk.Text(top, height=40, width=70)

    text1.pack(side=tk.LEFT)
    scroll = tk.Scrollbar(top, command=text1.yview)
    text1.configure(yscrollcommand=scroll.set)

    for i in range(len(origin_display)):
        each = origin_display[i]
        text1.insert(tk.INSERT, each[0] + '\n')

        for highlight in each[1]:
            text1.tag_add("here",
                          str(i + 1) + "." + str(highlight[0]),
                          str(i + 1) + "." + str(highlight[1]))
            text1.tag_config("here",
                             background="yellow", foreground="blue")

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
        result.append(text2.get('1.0', tk.END))
        # print("exit result: ", result)
        top.destroy()
        top.update()

    def exit_btn():
        msgbox_save = tk.messagebox.askyesnocancel("Finish Manual Editing", "Do you want to quit manual editing without saving changes?")
        result.append(text1.get('1.0', tk.END))
        if msgbox_save:
            top.destroy()
            top.update()
        return

    bottomFrame = tk.Frame(top)
    bottomFrame.pack(fill="both", expand=True, side=tk.BOTTOM)
    tk.Button(bottomFrame, text="Quit", command=exit_btn).pack(side="left")
    tk.Button(bottomFrame, text="Save", command=exit_btn_save).pack(side="left")

    root.wait_window(top)

caps = "([A-HJ-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|edu)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
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
    origin_sentences = split_into_sentences(origin_text)
    corefed_sentences = split_into_sentences(corefed_text)
    origin_display = []
    corefed_display = []
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
            mb.showwarning(title='Warning', message='The Co-Refereced output file generated by Stanford CoreNLP CoRef is too big to be displayed side-by-side with the original file, with pronouns highlighted in the orignal file (on the left panel) and the Co-Referenced form highlighted (on the right panel).\n\nManual editing cannot be done.\n\nIf you wish to carry out manual editing, you may wish to open the file manager and split the file into separate sub-files by a maximum number of words. Then, run the Co-Reference on the splitted files and merge the Co-Referenced output files.')
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

    return origin_display, corefed_display

# return error indicator: 1 error; 0 no error
def manualCoref(original_file, corefed_file, outputFile, coRefOptions):
    f = open(original_file, "r", encoding='utf-8', errors='ignore')
    original_text = f.read()
    f.close()
    f = open(corefed_file, "r", encoding='utf-8', errors='ignore')
    corefed_text = f.read()
    f.close()

    origin_display, corefed_display = compare_results(original_text, corefed_text)
    # cannot do manual coref
    if len(corefed_display) == 0 and len(origin_display) == 0:
        return 1
    result = []
    createCompareWindow(origin_display, corefed_display, coRefOptions, GUI_util.window, result)
    f = open(outputFile, "w", encoding='utf-8', errors='ignore')
    try:
        f.write(result[0])
    except:
        mb.showwarning(title='Warning',
                       message='The corefereced output file generated by Stanford CoreNLP CoRef is too big to be displayed side-by-side with the original file, with pronouns highlighted in the orignal file (on the left panel) and the coreferenced form highlighted (on the right panel).\n\nManual editing cannot be done.\n\nIf you wish to carry out manual editing, you may wish to open the file manager and split the file into separate sub-files by a maximum number of words. Then, run the coreference on the splitted files and merge the coreferenced output files.')
        f.close()
        return 1
    f.close()
    print("=======Finished Displaying Manual Editing=========")
    return 0

# check if the coreference ends successfully
# return files_to_open, error indicator
# 0: no error; 1: error and no manual coref;
def checkSingleFile(inputFilename, corefed_file, manual_Coref, coRefOptions, files_to_open):
    # check if corefed_file is empty:
    f = open(corefed_file, "r", encoding='utf-8', errors='ignore')
    corefed_text = f.read()
    f.close()
    # if the file is empty
    if corefed_text == "":
        if manual_Coref:
            msgbox_exit = mb.askyesno("Co-Reference Resolution Error",
                                      "Something went wrong for Co-Reference Resolution; the Co-Referenced output file is empty.\n\nPlease, check the command line, most likely for 'GC overhead limit exceeded' when processing large files.\n\n" +
                                      "Do you want to use the original file to continue manual Co-Reference process? If not, please click 'No' to end the process of Coreference Resolution")
            if msgbox_exit:
                if manualCoref(inputFilename, inputFilename, corefed_file, coRefOptions) == 0:  # use the orginal file as coref
                    # manual coref success!
                    files_to_open.append(corefed_file)
                    return files_to_open, 0
                else:
                    # manual coref error!
                    return files_to_open, 1
            else:
                # user don't want to use the original file to continue manual coref
                return files_to_open, 1
        else:
            mb.showinfo("Co-Reference Resolution Error",
                        "Something went wrong for Co-Reference Resolution; the Co-Referenced output file is empty.\n\nPlease, check the command line, most likely for 'GC overhead limit exceeded' when processing large files.\n\n")

            return files_to_open, 1
    # coreference success!
    else:
        if manual_Coref:
            manualCoref(inputFilename, corefed_file, corefed_file, coRefOptions)
        files_to_open.append(corefed_file)

    return files_to_open, 0


# return file_to_open
def run(inputFilename, input_main_dir_path, output_dir_path, openOutputFiles, createExcelCharts,
        memory_var,coRefOptions, manual_Coref):

    files_to_open = []

    # check that the CoreNLPdir as been setup
    CoreNLPdir=IO_libraries_util.get_external_software_dir('Stanford_CoreNLP_coreference_util', 'Stanford CoreNLP')
    if CoreNLPdir==None:
        return files_to_open

    errorFound, error_code, system_output=IO_libraries_util.check_java_installation('SVO extractor')
    if errorFound:
        return filesToOpen

    # IO_user_interface_util.timed_alert(GUI_util.window, 5000, 'Analysis start',
    #                     'Started running Stanford CoreNLP ' + coRefOptions + ' Co-Reference Resolution at', True,
    #                     'PLEASE, BE PATIENT... Depending upon the size of the document/number of documents processed this may take from a few minutes to a few hours.')

    error = 0
    # with only one input file
    if len(inputFilename)>0:
        base = os.path.basename(inputFilename)
        fileName = os.path.splitext(base)[0]

        if IO_libraries_util.inputProgramFileCheck('Stanford_CoreNLP_annotator_util.py')==False:
            return
        corefed_file = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename,input_main_dir_path,output_dir_path, openOutputFiles, createExcelCharts,'coref',False,memory_var)
        files_to_open, error = checkSingleFile(inputFilename, corefed_file[0], manual_Coref, coRefOptions, files_to_open)

    else:
        corefed_file = Stanford_CoreNLP_annotator_util.CoreNLP_annotate(inputFilename, input_main_dir_path,
                                                                   output_dir_path, openOutputFiles, createExcelCharts,'coref', False,
                                                                   memory_var)

    for file in corefed_file:
        if file[-4:] == ".txt":
            head, tail = os.path.split(file)
            # get the original file path from coref processed file path
            original_file = input_main_dir_path + '/' + tail[18:]
            files_to_open, error = checkSingleFile(original_file, file, manual_Coref, coRefOptions,
                                                   files_to_open)

    return files_to_open, error