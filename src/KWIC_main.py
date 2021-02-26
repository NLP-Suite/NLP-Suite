"""
    -*- coding: utf-8 -*-
    This script is written in python 3 for both Apple and Windows machines
    Written by Cynthia Dong (February 2019)
    GUI written by Jack Hester (February 2019)
    KWIC algorithms modified by Jack Hester (Februar 2019)
    """
import GUI_IO_util
import IO_user_interface_util

"""
    Running from the command line:
    
    Main Command: Python KWIC_GUI.py
    
    Arguments for GENERATING NEW KWIC FROM CoNLL:
        argv[1]: input CoNLL table
        argv[2]: output KWIC (.csv) table
        
        example: Python KWIC_GUI.py /Users/jhester/Downloads/FW__KWIC_Search/mergedCoNLL.conll /Users/jhester/Downloads/FW__KWIC_Search/KWIC.csv
        
    Arguments for SEARCHING EXISTING KWIC TABLE:
        argv[1]: input KWIC (.csv) table
        argv[2]: output .csv table
        argv[3]: keyword to search
        argv[4]: search window size (-10 to 10 not includign 0)
        argv[5]: position/direction to search (left, right, both)
        argv[6]: within or at search window, 1 for within, 0 for at search window
        
        example: Python KWIC_GUI.py /Users/jhester/Downloads/FW__KWIC_Search/KWIC.csv /Users/jhester/Downloads/FW__KWIC_Search/output.csv father 4 both 1
"""

#from pycorenlp import StanfordCoreNLP
import os
from io import open
import pandas as pd
import sys
#from contextlib import closing
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as mb
#from tkinter import DISABLED
import csv
#from sys import platform
#from subprocess import call
#import subprocess

import Help_util
import TIPS_util
import IO_files_util
import Excel_util
import IO_csv_util

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# insert the src dir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# location of this python file
scriptPath = os.path.dirname(os.path.realpath(__file__))
# TIPS directory folder, assuming it's in same dir as this file
tipsPath = os.path.join(scriptPath,'TIPS')

#subdirectory of script directory where config files are saved
configPath = os.path.join(scriptPath,'config')

global inputCoNLLtable

filesToOpen = [] # Store all files that are to be opened once finished


"""
GUI
"""
# make GUI window
window = tk.Tk()
window.title('GUI for KWIC (Key Word In Context)')
window.geometry('1100x600')

# useful measurements for later
help_button_x_coordinate = 50

labels_x_coordinate = 120 #start point of all labels in the second column (first column after ? HELP) #150
x_drop_down = 350 #drop down menu position
entry_box_x_coordinate = 450 #start point of all labels in the third  column (second column after ? HELP)
basic_y_coordinate = 90

y_step = 40 #50
x_indent_step = 60 #50
y_main_buttons = 530 #read me, quit...

# checking if they have conllu installed
# try:
#     from conllu import parse_incr
# except:
#     tk.messagebox.showinfo("WARNING", "The conllu package is needed to run this method, please install using 'pip install conllu' in terminal or command prompt.")
#     print("The conllu package is needed to run this method, please install using 'pip install conllu' in terminal or command prompt.")
#     sys.exit(0)


"""
    Main generation methods
"""
#windowSize: from 1-10
# inputCoNLL: conll used to generate kwic
#outputName: output kwic table name
#def generate_kwic(inputCoNLL, windowSize, outputName, ranWithCLAs=False):
def generate_kwic(inputCoNLL, outputName, ranWithCLAs=False):
    IO_user_interface_util.timed_alert(window, 3000, 'Generating KWIC Table', 'Started running KWIC at', True)
    windowSize = 10
    if IO_files_util.check_merged_CoNLL(inputCoNLL)==False:
        return
    if inputCoNLL.strip()[-6:]=='.conll':
        oldCoNLL=True
        withHeader=False
    else:
        oldCoNLL=False
        withHeader=True
    #data=IO_util.get_csv_data(inputCoNLL,withHeader)
    with open(inputCoNLL, "r", encoding="utf-8", errors = "ignore") as f:
        if withHeader==True:
            next(f)
        data_words = []
        Sentence ID = []
        count=IO_csv_util.get_csvfile_numberofColumns(inputCoNLL)
        for lines in f:
            if oldCoNLL==False:
                words = lines.split(",")
            else:
                words = lines.split("\t")
            data_words.append(words[2])
            Sentence ID.append(words[9]) #sentenceID position stays the same in old and new CoNLL tables
    # add every word in conll table to data_words list and add their corresponding sentence id to Sentence ID list
    data_kwic = list()
    word_list = list()
    tmp_list = ['', '']  # initialize the list
    index = 0
    for token in data_words:
        # index is current working
        # i is the index of words within distance windowSize (say 10)
        i = index - windowSize
        while i <= index + windowSize:
            if (i < 0 or i >= len(data_words) or i == index):
                i = i + 1
                continue
            tmp_list[0] = data_words[index]
            tmp_list[1] = data_words[i]
            if ([tmp_list[0], tmp_list[1]] in word_list):
                # update the value
                occ_index = word_list.index([tmp_list[0], tmp_list[1]])
                if ((i - index) > 0):
                    data_kwic[occ_index][i - index + windowSize - 1] = data_kwic[occ_index][i - index + windowSize - 1] + 1
                else:
                    data_kwic[occ_index][i - index + windowSize] = data_kwic[occ_index][i - index + windowSize] + 1
                if (Sentence ID[index] == Sentence ID[i]):
                    data_kwic[occ_index][-1] = data_kwic[occ_index][-1] + 1
            else:
                word_list.append([tmp_list[0], tmp_list[1]])
                tmp_num_list = [0] * (windowSize * 2 + 1)
                if ((i - index) > 0):
                    tmp_num_list[i - index + windowSize - 1] = 1
                else:
                    tmp_num_list[i - index + windowSize] = 1
                if (Sentence ID[index] == Sentence ID[i]):
                    tmp_num_list[-1] = 1
                data_kwic.append(tmp_num_list)
            i = i + 1
        index = index + 1
    word_list.insert(0, ["word1", "word2"])
    header = list()
    j = -windowSize
    while j <= windowSize:
        if (j == 0):
            j = j + 1
            continue
        header.append(j)
        j = j + 1
    header.append("sentence frequency")
    data_kwic.insert(0, header)
    tmp = []
    with open(outputName, 'w', encoding="utf-8", errors = "ignore", newline='') as csvFile:
        writer = csv.writer(csvFile)
        for i in range(0, len(word_list)):
            tmp.append(word_list[i][0])
            tmp.append(word_list[i][1])
            for j in range(0, (windowSize * 2 + 1)):
                tmp.append(data_kwic[i][j])
            writer.writerow(tmp)
            tmp.clear()
        filesToOpen.append(outputName)
    if ranWithCLAs == False:
        IO_user_interface_util.timed_alert(window, 3000, 'KWIC Table Generated', 'Finished running KWIC at', True)

# searchSize: search window size
# position: left, right, both
# searchWord: which word you want to search for
# inputKWIC: input KWIC table
# within: 1 if you want to search within the window size or 0 if you want to search at the window size
# outFile: file name for output
def search(searchWord, searchSize, position, inputKWICfile, within, outFile, ranWithCLAs=False):
    # read in word1,word2,targeted window size column in the csv file
    if (within == 1):
        cols = []
        cols.append(0)
        cols.append(1)
        i = 12 - searchSize
        while i <= 11 + searchSize:
            cols.append(i)
            i+=1
        data = pd.read_csv(inputKWICfile, usecols=cols, engine='python')
    else:
        data = pd.read_csv(inputKWICfile, usecols=[0, 1, 12-searchSize, 11+searchSize], engine='python')
    # filter out the rows where searchWord is in
    target = data['word1'].str.lower() == searchWord.lower()
    target_rows = data[target]
    # get the values in dataframe
    rownum = target_rows.shape[0]
    colnum = target_rows.shape[1]
    i = 0
    global leftKWIC, rightKWIC 
    leftKWIC = []
    rightKWIC = []
    result = []
    mid = 1+(colnum-2)/2
    #every row refers to a new combination of two words
    while i < rownum:
        #every row refers to a new combination of two words; the counts should start over at zero
        countLeft = 0
        countRight = 0
        #print("i ",i) i is correct
        if (position == "left"):
            j = 2
            while j <= mid:
                countLeft += target_rows.iloc[i][j]
                j+=1
            if not (countLeft == 0):
                result.append([target_rows.iloc[i]['word1'], target_rows.iloc[i]['word2'], countLeft])
                if countLeft>0:
                    leftKWIC.append([target_rows.iloc[i]['word2'],countLeft])
                    # write into csv file
                    with open(outFile, 'w', encoding="utf-8", errors = "ignore", newline='') as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(["Searched Key Word", "Word in Context", "Position_left(-"+str(searchSize)+" words)"])
                        for items in result:
                            writer.writerow(items)
                            #leftKWIC.append(items[2],items[3])
        elif (position == "right"):
            j = round(mid + 1)
            while j < colnum:
                countRight += target_rows.iloc[i][j]
                j += 1
            if not (countRight == 0):
                result.append([target_rows.iloc[i]['word1'], target_rows.iloc[i]['word2'], countRight])
                if countRight>0:
                    rightKWIC.append([target_rows.iloc[i]['word2'],countRight])
                    # write into csv file
                    with open(outFile, 'w', encoding="utf-8", errors = "ignore", newline='') as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(["Searched Key Word", "Word in Context", "Position_right(+"+str(searchSize)+" words"])
                        for items in result:
                            writer.writerow(items)
        else:
            j = 2
            while j <= mid:
                countLeft += target_rows.iloc[i][j]
                j += 1
            while j < colnum:
                countRight += target_rows.iloc[i][j]
                j += 1
            if not (countLeft == 0 and countRight == 0):
                result.append([target_rows.iloc[i]['word1'], target_rows.iloc[i]['word2'], countLeft, countRight])
            if countLeft>0:
                leftKWIC.append([target_rows.iloc[i]['word2'],countLeft])
            if countRight>0:
                rightKWIC.append([target_rows.iloc[i]['word2'],countRight])
                # write into csv file
                with open(outFile, 'w', encoding="utf-8", errors = "ignore", newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(["Searched Key Word", "Word in Context", "Position_left(-"+str(searchSize)+" words)", "Position_right(+"+str(searchSize)+" words"])
                    for items in result:
                        writer.writerow(items)
        i+=1
    #TODO
    #searchWord should be displayed in quotes in the chart
    #should exclude stopwords (putting a widget on GUI)
    filesToOpen.append(KWIC_search_output_filename)

    """
    #display chart for searchWord within sentence
    KWIC_search_output_filename_sentence=KWIC_search_output_filename.strip()[:-4]+"_sentence_counts.xlsx"
    sentenceKWIC=
    IO_util.list_to_csv(window,sentenceKWIC,KWIC_search_output_filename_sentence)
    #sort will not work with headers; headers inserted after
    sentenceKWIC=stats_visuals_util.sort_data(sentenceKWIC,1,True)
    sentenceKWIC.insert(0,["KWIC (sentence tokens)","Counts"])
    stats_visuals_util.create_excel_chart(window,"bar","Sentence tokens for " + searchWord,rightKWIC,KWIC_search_output_filename_sentence,20)
    filesToOpen.append(KWIC_search_output_filename_sentence)
    """
    
    if position == "left" or position == "both":
        if len(leftKWIC)>0:
            KWIC_search_output_filename_stats=KWIC_search_output_filename.strip()[:-4]+"_left_counts.xlsx"
            IO_csv_util.list_to_csv(window,leftKWIC,KWIC_search_output_filename_stats)
            #sort will not work with headers; headers inserted after
            leftKWIC=stats_visuals_util.sort_data(leftKWIC,1,True)
            leftKWIC.insert(0,["KWIC (left-hand tokens)","Counts"])
            Excel_util.create_excel_chart(window,"bar","Left-hand tokens for " + searchWord,[leftKWIC],KWIC_search_output_filename_stats,20)
            filesToOpen.append(KWIC_search_output_filename_stats)
        else:
            IO_user_interface_util.timed_alert(window, 3000, 'Searching KWIC Table', 'There are no left-hand words for the searched keyword: ' + searchWord)
    if position == "right" or position == "both":    
        if len(rightKWIC)>0:
            KWIC_search_output_filename_stats=KWIC_search_output_filename.strip()[:-4]+"_right_counts.xlsx"
            IO_csv_util.list_to_csv(window,rightKWIC,KWIC_search_output_filename_stats)
            #sort will not work with headers; headers inserted after
            rightKWIC=stats_visuals_util.sort_data(rightKWIC,1,True)
            rightKWIC.insert(0,["KWIC (right-hand tokens)","Counts"])
            Excel_util.create_excel_chart(window,"bar","Right-hand tokens for " + searchWord,[rightKWIC],KWIC_search_output_filename_stats,20)
            filesToOpen.append(KWIC_search_output_filename_stats)
        else:
            IO_user_interface_util.timed_alert(window, 3000, 'Searching KWIC Table', 'There are no right-hand words for the searched keyword: ' + searchWord)

    if ranWithCLAs == False:
        IO_user_interface_util.timed_alert(window, 3000, 'Searching KWIC Table', 'Finished running KWIC at', True)

def checkKWIC (csvFile):
    KWICfile=False
    with open(csvFile,'r') as f:
        firstLine=f.readline()
        #print("in IO firstLine.find(Word in Context) ",firstLine)
        if firstLine.find("word1")!=-1 and firstLine.find("word2")!=-1:
            KWICfile=True
        else:
            KWICfile=False
            mb.showwarning(title='Input file error', message='The script expects in input a KWIC csv file with a first-column and a second-column in its header labeled word1 and word2.\n\nThe header\n\n' + firstLine + '\nin the input file\n\n' + csvFile + '\n\ndoes not contain first- and second-column labels word1 and word2.\n\nPlease, select a KWIC file and try again.')
    return KWICfile

def create_KWIC():

    inputCoNLLtable = str(CoNLL_input_file_path.get())
    newKWIC = str(KWIC_create_output_file_path.get())
    windowStr = str(window_dropdown_field.get())
    windowStr = windowStr.strip('+/-')
    windowSize = int(windowStr)
    # make sure they gave an input and output file
    if inputCoNLLtable == '' or newKWIC == '':
        print('error with input/output files')
        tk.messagebox.showinfo("ERROR", "You did not provide a valid input and/or output file! Please try again.")
        return 'error'
    
    generate_kwic(inputCoNLLtable, newKWIC)
    checkOpen(newKWIC)

def search_KWIC():
    # gather vars
    searchWord = str(searchField_kw.get())
    searchSizeStr = str(window_dropdown_field.get())
    searchSizeStr = searchSizeStr.strip('+/-')
    searchSize = int(searchSizeStr) # like window size
    position = str(position_dropdown_field.get())
    withinStr = str(where_dropdown_field.get())
    if withinStr == 'within':
        within = 1 # they want to search within the window
    else:
        within = 0
    inputKWICfile = str(KWIC_input_file_path.get())
    KWIC_search_output_filename = str(KWIC_search_output_file_path.get())
    # make sure they gave an input and output file
    if inputKWICfile == '' or KWIC_search_output_filename == '':
        print('error with input/output files')
        tk.messagebox.showinfo("ERROR", "You did not provide a valid input and/or output file! Please try again.")
        return 'error'

    IO_user_interface_util.timed_alert(window, 3000, 'Searching KWIC Table', 'Started running KWIC at', True)

    search(searchWord, searchSize, position, inputKWICfile, within, KWIC_search_output_filename)

    checkOpen(KWIC_search_output_filename)


def exit_window():
        global window
        msgbox_save = tk.messagebox.askquestion("Save Configuration", "If the paths configuration has changed (i.e., input and output paths), would you like to save the paths configuration? \n\nIf you save the paths configuration you will not need to enter them again next time you run this Python script.")
        
        if msgbox_save == 'yes':
                config_file_path = "KWIC-config.txt"

                config1 = CoNLL_input_file_path.get()
                if config1 == '':
                    config1 = 'EMPTY LINE'
                config2 = KWIC_create_output_file_path.get()
                if config2 == '':
                    config2 = 'EMPTY LINE'
                config3 = KWIC_input_file_path.get()
                if config3 == '':
                    config3 = 'EMPTY LINE'
                config4 = KWIC_search_output_file_path.get()
                if config4 == '':
                    config4 = 'EMPTY LINE'

                configFile=os.path.join(configPath,config_file_path)
                with open (configFile, "w+",encoding="utf-8", errors = "ignore") as f:
                        f=open(configFile, "w+")
                        for config in [config1,config2,config3,config4]:
                            f.write(config+'\n')
                        f.close()
                        print("INPUT and OUTPUT paths configuration saved.")
                window.destroy()
                exit()
        else:    
                window.destroy()
                exit()


def select_conll_input_dir():
    global inputCoNLLtable
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    in_file_path = filedialog.askopenfilename(initialdir = initialFolder, title='Select INPUT MERGED CoNLL table (.conll extension for old CoreNLP; .csv for new CoreNLP); switch extension type below near File name:',filetypes = (("csv files","*.csv"),("CoNLL tables","*.conll")))
    if len(in_file_path)<4:
        CoNLL_input_file_path.set("")
    else:
        CoNLL_input_file_path.set(in_file_path)
    inputCoNLLtable=CoNLL_input_file_path.get()
    check_conll()
    check_KWIC()
    return inputCoNLLtable

#where the new KWIC table will be saved
def select_KWIC_output_dir():
    global KWIC_create_output_filename
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    out_file = filedialog.asksaveasfilename(initialdir = initialFolder, initialfile=IO_files_util.generate_output_file_name(inputCoNLLtable, KWIC_create_output_filename, '.csv', 'KWIC', 'Table'), title='Save output KWIC csv file', filetypes = (("csv", "*.csv"), ("all files", "*.*")))
    if len(out_file)<4:
    	KWIC_create_output_file_path.set("")
    else:
    	KWIC_create_output_file_path.set(out_file)
    KWIC_create_output_filename=KWIC_create_output_file_path.get()
    return KWIC_create_output_filename

def select_existing_KWIC():
    global inputKWICfile
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    in_file_path = filedialog.askopenfilename(initialdir =initialFolder, title='Select input KWIC csv file',filetypes = (("csv","*.csv"),("all files","*.*")))
    if len(in_file_path)<4:
    	KWIC_input_file_path.set("")
    else:
    	KWIC_input_file_path.set(in_file_path)
    inputKWICfile=KWIC_input_file_path.get()
    if inputKWICfile=="":
        return
    if checkKWIC(inputKWICfile)==False:
        return
    check_conll()
    check_KWIC()
    return inputKWICfile

def select_KWIC_Search_Output_dir():
    global KWIC_search_output_filename
    initialFolder = os.path.dirname(os.path.abspath(__file__))
    out_file= filedialog.asksaveasfilename(initialdir = initialFolder, initialfile=IO_files_util.generate_output_file_name(inputKWICfile, KWIC_search_output_filename, '.csv', 'KWIC', 'Search'), title='Save output KWIC search csv file', filetypes = (("csv", "*.csv"), ("all files", "*.*")))
    if len(out_file)<4:
        KWIC_search_output_file_path.set("")
    else:
        KWIC_search_output_file_path.set(out_file)
    KWIC_search_output_filename=KWIC_search_output_file_path.get()
    check_conll()
    check_KWIC()
    return KWIC_search_output_filename


# text input fields
# configurations
CoNLL_input_file_path = tk.StringVar()

KWIC_create_output_file_path = tk.StringVar()

KWIC_input_file_path = tk.StringVar()

KWIC_search_output_file_path = tk.StringVar()


generateKWICIntro = tk.Label(window, anchor = 'w', text="Generate a new KWIC table from a MERGED CoNLL table")
generateKWICIntro.place(x=labels_x_coordinate,y=basic_y_coordinate)

searchKWICIntro = tk.Label(window, anchor = 'w', text="Search existing KWIC table")
searchKWICIntro.place(x=labels_x_coordinate,y=basic_y_coordinate+y_step*3)

quit_button = tk.Button(window, text='QUIT', width=20,height=2, command=exit_window)
quit_button.place(x=900,y=y_main_buttons)

create_KWIC_button = tk.Button(window, text='RUN (new KWIC table)', width=20,height=2, command=create_KWIC)
create_KWIC_button.place(x=500,y=y_main_buttons)

search_KWIC_button = tk.Button(window, text='RUN (KWIC search)', width=20,height=2, command=search_KWIC)
search_KWIC_button.place(x=700,y=y_main_buttons)


readMe_command=lambda: Help_util.readme_message_KWIC(window,help_button_x_coordinate,basic_y_coordinate,y_step)

readme_button = tk.Button(window, text='Read Me',command=readMe_command,width=20,height=2)
readme_button.place(x=100,y=y_main_buttons)

intro = tk.Label(window, anchor = 'w', text=Help_util.introduction_main)
intro.pack()

# input
select_input_CoNLL_button=tk.Button(window, width=44,text='Select INPUT MERGED CoNLL table to create NEW KWIC', command=select_conll_input_dir, anchor="w")
select_input_CoNLL_button.place(x=labels_x_coordinate+x_indent_step, y=basic_y_coordinate+y_step)
tk.Label(window, textvariable=CoNLL_input_file_path).place(x=entry_box_x_coordinate+60, y=basic_y_coordinate+y_step)


# output kwic from conll
select_save_KWIC_file_button=tk.Button(window, width=44,text='Select OUTPUT KWIC table', command=select_KWIC_output_dir, anchor="w")
select_save_KWIC_file_button.place(x=labels_x_coordinate+x_indent_step, y=basic_y_coordinate+y_step*2)
tk.Label(window, textvariable=KWIC_create_output_file_path).place(x=entry_box_x_coordinate+60, y=basic_y_coordinate+y_step*2)

# existing kwic to search
select_input_KWIC_button=tk.Button(window, width=44,text='Select existing INPUT KWIC table', command=select_existing_KWIC, anchor="w")
select_input_KWIC_button.place(x=labels_x_coordinate+x_indent_step, y=basic_y_coordinate+y_step*4)
tk.Label(window, textvariable=KWIC_input_file_path).place(x=entry_box_x_coordinate+60, y=basic_y_coordinate+y_step*4)

# output of existing kwic search
select_save_KWIC_Search_file_button=tk.Button(window, width=44,text='Select OUTPUT file for KWIC search results', command=select_KWIC_Search_Output_dir, anchor="w")
select_save_KWIC_Search_file_button.place(x=labels_x_coordinate+x_indent_step, y=basic_y_coordinate+y_step*5)
tk.Label(window, textvariable=KWIC_search_output_file_path).place(x=entry_box_x_coordinate+60, y=basic_y_coordinate+y_step*5)

# Keyword field labels
kw_Info = tk.Label(window, anchor = 'w', text="Key word to search")
kw_Info.pack()
kw_Info.place(x=labels_x_coordinate+x_indent_step,y=basic_y_coordinate+y_step*6)

# Setting up keyword search
searchField_kw = tk.StringVar()
searchField_kw.set('e.g.: father')
entry_searchField_kw = tk.Entry(window, textvariable=searchField_kw)
entry_searchField_kw.place(x=x_drop_down, y=basic_y_coordinate+y_step*6)

# Setting up window dropdown
window_dropdown_field = tk.StringVar()
window_dropdown_field.set('+/-5')

windowInfo = tk.Label(window, anchor = 'w', text="Search window size")
windowInfo.pack()
windowInfo.place(x=labels_x_coordinate+x_indent_step,y=basic_y_coordinate+y_step*7)

# Window size menu dropdown and var monitoring
window_menu_lb = tk.OptionMenu(window,window_dropdown_field,'+/-10', '+/-9', '+/-8', '+/-7', '+/-6', '+/-5', '+/-4', '+/-3', '+/-2', '+/-1')
window_menu_lb.place(x=x_drop_down, y=basic_y_coordinate+y_step*7)

# Setting up position dropdown (left, right, both)
position_dropdown_field = tk.StringVar()
position_dropdown_field.set('both')
positionInfo = tk.Label(window, anchor = 'w', text="Direction (position) to search")
positionInfo.pack()
positionInfo.place(x=labels_x_coordinate+x_indent_step,y=basic_y_coordinate+y_step*8)

# Position menu dropdown and var monitoring
position_dropdown_lb = tk.OptionMenu(window,position_dropdown_field,'left','right','both')
position_dropdown_lb.place(x=x_drop_down, y=basic_y_coordinate+y_step*8)

# Setting up at/within search menu (left, right, both)
where_dropdown_field = tk.StringVar()
where_dropdown_field.set('within')
whereInfo = tk.Label(window, anchor = 'w', text="Search at or within")
whereInfo.pack()
whereInfo.place(x=labels_x_coordinate+x_indent_step,y=basic_y_coordinate+y_step*9)

# location (at/where) search and var monitoring
where_dropdown_lb = tk.OptionMenu(window,where_dropdown_field,'at','within')
where_dropdown_lb.place(x=x_drop_down, y=basic_y_coordinate+y_step*9)

# monitor if key word to search was enabled
def check_kw(*args):
    window_menu_lb.configure(state='normal')
    position_dropdown_lb.configure(state='normal')
    where_dropdown_lb.configure(state='normal')
    search_KWIC_button.configure(state='normal')
searchField_kw.trace("w", check_kw)

# function if they want to open output csv or not
def print_open_file_or_not():
    if ask_open_table.get() == 1:
        l_checkbox.config(text="You will automatically open the saved output file for inspection")
    elif ask_open_table.get() == 0:
        l_checkbox.config(text="You will NOT automatically open the saved output file for inspection")

#open or not
l_checkbox = tk.Label(window)
l_checkbox.place(x=labels_x_coordinate+30,y=basic_y_coordinate+y_step*10)
ask_open_table = tk.IntVar()
ask_open_table.set(1)
openCheck = tk.Checkbutton(window, variable=ask_open_table, onvalue=1, offvalue=0,
                    command=print_open_file_or_not)
openCheck.place(x=labels_x_coordinate, y=basic_y_coordinate+y_step*10)

# monitor if input path selected for generating kwic
def check_conll(*args):
    if str(CoNLL_input_file_path.get()) == '' and str(KWIC_create_output_file_path.get()== '' ):
        create_KWIC_button.configure(state='disabled')
        select_input_KWIC_button.configure(state='normal')
        select_save_KWIC_Search_file_button.configure(state='normal')
    else:
        if str(CoNLL_input_file_path.get()) == '' or str(KWIC_create_output_file_path.get()== '' ):
            select_input_KWIC_button.configure(state='disabled')
            select_save_KWIC_Search_file_button.configure(state='disabled')
        create_KWIC_button.configure(state='normal')
CoNLL_input_file_path.trace("w", check_conll)
KWIC_create_output_file_path.trace("w", check_conll)

# monitor if input path selected for searching kwic
def check_KWIC(*args):
    if str(KWIC_input_file_path.get()) == '' and str(KWIC_search_output_file_path.get()== '' ):
        search_KWIC_button.configure(state='disabled')
        select_input_CoNLL_button.configure(state='normal')
        select_save_KWIC_file_button.configure(state='normal')
    else:
        if str(KWIC_input_file_path.get()) == '' or str(KWIC_search_output_file_path.get()== '' ):
            select_input_CoNLL_button.configure(state='disabled')
            select_save_KWIC_file_button.configure(state='disabled')
        if str(searchField_kw.get()) == "e.g.: father":
            search_KWIC_button.configure(state='disabled')
        else:
            search_KWIC_button.configure(state='normal')

KWIC_input_file_path.trace("w", check_KWIC)
KWIC_search_output_file_path.trace("w", check_KWIC)


tips_dropdown_field = tk.StringVar()
tips_dropdown_field.set('Open TIPS files')
lookup = {'CoNLL Table':"TIPS_NLP_Stanford CoreNLP CoNLL table.pdf",'KWIC Table':"TIPS_NLP_KWIC (Key Word In Context).pdf"}
TIPS_options='CoNLL Table', 'KWIC Table'
if len(lookup)==1:
    tips_menu_lb = tk.OptionMenu(window,tips_dropdown_field,TIPS_options)
else:
    tips_menu_lb = tk.OptionMenu(window,tips_dropdown_field,*TIPS_options)
tips_menu_lb.place(x=300,y=y_main_buttons)

TIPS_util.trace_open_tips(tips_dropdown_field,tips_menu_lb,lookup)

#__________________________________________________________________________________________________________________
#GUI HELP buttons

Help_buttons='KWIC'

Help_util.place_help_buttons(window,Help_buttons,help_button_x_coordinate,basic_y_coordinate,y_step)


paths = [CoNLL_input_file_path,KWIC_create_output_file_path,KWIC_input_file_path,KWIC_search_output_file_path]

configFile=os.path.join(configPath,"KWIC-config.txt")
if os.path.isfile(configFile)==True:
        f_config = open(configFile,'r')
        path_config = f_config.readlines()
        path_config = [i.strip() for i in path_config if i.strip()!='']

        if len(path_config) == 4:
            for path,config in zip(paths,path_config):
                if config == 'EMPTY LINE':
                    path.set('')
                else:
                    path.set(config)
        else:
            for path in paths:
                path.set('')
else:
        for path in paths:
            path.set('')

inputCoNLLtable=CoNLL_input_file_path.get()
KWIC_create_output_filename=KWIC_create_output_file_path.get()
inputKWICfile=KWIC_input_file_path.get()
KWIC_search_output_filename=KWIC_search_output_file_path.get()

check_conll()
check_KWIC()

print_open_file_or_not()


####
def checkOpen(output_file_name):
    if (ask_open_table.get() != 0):
        if str(search_KWIC_button['state']) == 'normal':
            if len(leftKWIC) == 0 and len(rightKWIC) == 0:
                return
        if str(output_file_name)=='':
            print('No output file was provided yet')
            return
        IO_files_util.OpenOutputFiles(window, ask_open_table.get(), filesToOpen)

"""
    Running main method to gather CLAs or run GUI
"""
"""
try:
    # see if 1st arg is a .conll or kwic table in CSV and handle generating or searching kwic
    inputCoNLLtable = sys.argv[1] # user input of csv or conll table
    if os.path.splitext(inputCoNLLtable)[1] == '.conll':
        # we are generating KWIC
        inputKWIC = sys.argv[2]
        #windowSize = int(sys.argv[3])
        ranWithCLAs = True
        print('Generating a KWIC table from your CoNLL input.')
        #generate_kwic(inputCoNLLtable, windowSize, inputKWIC, ranWithCLAs)
        generate_kwic(inputCoNLLtable, inputKWIC, ranWithCLAs)
    elif os.path.splitext(inputCoNLLtable)[1] == '.csv':
        # we are using and searching existing KWIC
        inputKWIC_search_csv = sys.argv[2]
        searchWord = sys.argv[3]
        searchSize = int(sys.argv[4]) # int; search window size
        position = sys.argv[5] # string; left, right, both
        within = int(sys.argv[6]) #int; 1 if you want to search within the window size or 0 if you want to search at the window size
        ranWithCLAs = True
        print('Executing search on input KWIC table.')
        search(searchWord, searchSize, position, inputCoNLLtable, within, inputKWIC_search_csv, ranWithCLAs)
    else:
        print('invalid input format')
except Exception as e:
    print ("\nCommand line arguments are empty, incorrect, or out of order")
    print ("\nGraphical User Interface (GUI) will be activated")
    #print(e.__doc__)
 """  

window.mainloop()
