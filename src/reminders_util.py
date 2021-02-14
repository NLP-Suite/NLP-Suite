# Written by Cynthia Dong April 2020
# Edited by Roberto Franzosi
import GUI_IO_util
import IO_files_util
import sys

# if IO_util.install_all_packages(window,"reminders_util",['os','tkinter','pandas'])==False:
#     sys.exit(0)

import os
import tkinter as tk
import tkinter.messagebox as mb
import pandas as pd
import csv
from csv import writer

# reminders content for specific GUIs are set in the csv file reminders
# check if the user wants to see the message again
# reminders are typically called from GUIs (at the bottom)
#   but can also be called from main or util scripts
#       e.g., file_splitter_util
#       e.g., GIS_geocoder_util

#
# config_filename is the first column in reminders.csv
#   it refers to the general Python script that calls the reminder
# title is the second column in reminders.csv
#   it refers to the specific Python option that calls the reminder
# message is typically stored in the reminders.csv files
#   For reminders that require a current value (e.g., date and time stamp)
#   the message is passed (an example is found in GUI_frontEnd in GUI_IO_util.py)
# triggered_by_GUI_event is passed when triggered by an event in the GUI (a checkbox ticked, a file opened)
#   (e.g., in shape_of_stories_GUI)

def getReminder_list(config_filename,silent=False):
    routine=config_filename[:-len('-config.txt')]
    title_options=[]
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    if IO_files_util.checkFile(remindersFile)==False:
        return title_options
    try:
        df = pd.read_csv(remindersFile)
    except:
        if silent==False:
            mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
        return None
    # check among the * routine to make sure that the title is not there
    title_options = df[df['Routine'] == '*']['Title'].tolist()
    # now check among the specific routines
    temp=df[df["Routine"] == routine]['Title'].tolist()
    if len(temp)>0:
        title_options.extend(temp)
    if len(title_options)==0:
        title_options = ['Open reminders']
    return title_options

# * in the Routine column are used for reminders that apply to any GUI
# the functions gets the list of reminders for any given GUI (i.e., routine)

def displayReminder(df,row_num,title, message, event, currentStatus, question, seeMsgAgain=False) -> object:
    try:
        message = df.at[row_num, "Message"].replace("\\n", os.linesep)
    except:
        pass
    if message == '':
        answer = mb.askquestion(title="Reminder: " + df.at[row_num, "Title"],
                                message=message+question)
    else:
        answer = mb.askquestion(title="Reminder: " + title,
                                message=message+question)
    answer=answer.capitalize() # Yes/No
    if seeMsgAgain==True:
        if answer == 'No':
            status='No'
        else:
            status = 'Yes'
    else:
        if answer=='Yes':
            if currentStatus == 'No':
                status = 'Yes'
            else:
                status = 'No'
        else:
            status=currentStatus
    # save any status changes
    if currentStatus!=status:
        saveReminder(df,row_num, event, status)

# routine is a string
# title_options is a list [] of all Routine values
# * in the Routine column are used for reminders that apply to any GUI

def checkReminder(config_filename,title_options=[],message='', triggered_by_GUI_event=False):
    # * denotes messages that apply to ALL scripts
    if config_filename=='*':
        routine='*'
    else:
        routine = config_filename[:-len('-config.txt')]
    if title_options==None:
        title_options = getReminder_list(config_filename)
    else:
        if len(title_options)==0:
            title_options = getReminder_list(config_filename)
            if len(title_options)==0: # ill formed reminders
                return None
    # if len(title_options)==1 and title_options[0] == 'No Reminders available':
    #         mb.showwarning(title='Reminders warning', message="There are no reminders available for this script.")
    #         return
    # open_message = True
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    try:
        df = pd.read_csv(remindersFile)
    except:
        mb.showwarning(title='Reminders file error', message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
        return None # open_message
    # get the row number of the routine that we are looking at
    silent = False
    for title in title_options:
        df1=df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
        if len(df1) == 0:
            # if the title does not exist for a given routine try to see if a universal routine (*) is available
            df1=df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
        if len(df1) != 0:
            row_num = df1.index[0]
            event=df1.at[row_num, "Event"]
            status = df1.at[row_num, "Status"]
            if triggered_by_GUI_event == False and event=='Yes':
                silent = True
            else:
                silent = False
            if status == "Yes":
                if silent == False:
                    # must pass the entire dataframe and not the sub-dataframe dt1
                    displayReminder(df, row_num, title, message, event, status,
                                    "\n\nDo you want to see this message again?", True)
        else: # the reminder option does not exist and must be inserted and then displayed
            if triggered_by_GUI_event == True:
                event='Yes'
            else:
                event = 'No'
            insertReminder(routine, title, message, event, "Yes")
            # after inserting the new reminder return to check whether you want to see the reminder again
            if silent == False:
                # title_options is the value you originally came in with (i.e., [title]) and that was inserted
                checkReminder(config_filename, title_options, message,
                              triggered_by_GUI_event)

# called from a GUI when a reminder is selected from the reminder dropdown menu
# title is a string, the reminders option selected in the GUI dropdown menu
def resetReminder(config_filename,title):
    routine = config_filename[:-len('-config.txt')]
    if title != "Open reminders":
        if title == 'No Reminders available':
            mb.showwarning(title='Reminders warning', message="There are no reminders available for this script.")
            return
        remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
        try:
            df = pd.read_csv(remindersFile)
            # get the row number of the routine that we are looking at
        except:
            mb.showwarning(title='Reminders file error',
                           message="The reminders.csv file saved in the reminders subdirectory is ill formed. Most likely, it contains extra , in one of the three fields (Routine, Title, Message).\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.\n\nIf any of the fields contain , the field content must be enclosed in \"\".")
            return
        try:
            df1 = df.loc[(df['Routine'] == routine) & (df['Title'] == title)]
            if len(df1) != 0:
                row_num = df1.index[0]
            else:
                # check among the * routine to make sure that the title is not there
                df1 = df.loc[(df['Routine'] == '*') & (df['Title'] == title)]
                if len(df1) != 0:
                    row_num = df1.index[0]
                else:
                    return
        except:
            mb.showwarning(title='Reminders file error',
                           message="The reminders.csv file saved in the reminders subdirectory does not contain the reminder '" + title + "'.\n\nPlease, let the NLP Suite development team know the problem so it can be fixed.")
            return

        event = df.at[row_num, "Event"]
        status = df.at[row_num, "Status"]
        if status == "No":  # currently off
            question = '\n\nNow this reminder is turned OFF. Do you want to turn it ON?'
        else:
            question = '\n\nNow this reminder is turned ON. Do you want to turn it OFF?'
        displayReminder(df, row_num, title, '', event, status, question, False)


# update do_not_show_message.csv so that we don't show the message box again
# status: "Yes"/"No"
def saveReminder(df,row_num, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    df.at[row_num, "Event"] = event # change it to yes or no
    df.at[row_num, "Status"] = status # change it to yes or no
    df.to_csv(remindersFile, index=False, header=True)

def insertReminder(routine,title, message, event, status):
    remindersFile = os.path.join(GUI_IO_util.remindersPath, 'reminders.csv')
    with open(remindersFile, "a",newline = '', encoding='utf-8',errors='ignore') as reminders:#write a new row in the reminder csv file
        writer = csv.writer(reminders)
        writer.writerow([routine, title, message, event, status])
        reminders.close()

