#Written by Jack Hester and Roberto Franzosi

import sys
import os
import tkinter as tk
from tkinter import filedialog
from subprocess import call
import subprocess
import tkinter.messagebox as mb

import GUI_IO_util
import IO_files_util

def get_TIPS(selected_TIPS,lookup,menu_lb, dropdown_field):
    # lookup[selected_TIPS] would throw a keyError 
    #   if there is a differen spelling, even in letter case
    #   between TIPS_lookup and TIPS_options, for instance
    #   TIPS_lookup = {'NLP Searches': 'TIPS_NLP_NLP searches.pdf'}
    #   TIPS_options='NLP searches'
    try:
        if len(lookup[selected_TIPS])==0:
            pass
    except:
        mb.showinfo(title='TIPS keyError', message="There was an error in the TIPS dictionary lookup for \n\n" + selected_TIPS +"\n\nPlease, report the issue to the NLP Suite developers.")
        return False
    if selected_TIPS=='No TIPS available':
        mb.showinfo(title='TIPS Warning', message="There are no TIPS available for this script.")
        return False
    if menu_lb['state']!='disabled':
        if os.path.isfile(os.path.join(GUI_IO_util.TIPSPath, lookup[selected_TIPS]))==False:
            TIPSFile_Exists=False
            mb.showinfo(title='TIPS Warning', message="The TIPS file\n\n"+lookup[selected_TIPS]+"\n\ncould not be found in your TIPS directory.")
            return False
        else:
            TIPSFile_Exists=True
            if sys.platform in ['win32','cygwin','win64']:
                subprocess.Popen([GUI_IO_util.TIPSPath + os.sep + lookup[selected_TIPS]], shell=True)
            else:
                call(['open', GUI_IO_util.TIPSPath + os.sep + lookup[selected_TIPS]])
        return TIPSFile_Exists

def checkTIPSDir(menu_lb):
    TIPS_dir_exists = True
    # win_tipsSubdir = os.path.join(NLPPath,'TIPS') #TIPSPath+os.sep+'TIPS'+os.sep
    # unix_tipsSubdir = os.path.join(NLPPath,'Tips') #'Tips'+os.sep
    if not os.path.isdir(GUI_IO_util.TIPSPath):
        mb.showinfo(title='TIPS Warning', message='The script could not find a TIPS subdirectory. TIPS should be stored in a subdirectory called TIPS where your python script is stored.')
        menu_lb.configure(state='disabled')
        TIPS_dir_exists = False
    return TIPS_dir_exists

#Trace and open TIPS files based on user selection
field = None
lookup = None
menu = None
def TIPS_Tracer(*args):
    if len(field.get())=='No TIPS available':
        mb.showinfo(title='TIPS Warning', message="There are no TIPS available for this script.")
        return
    foundTips = checkTIPSDir(menu)
    if foundTips and field.get()!='Open TIPS files':
        get_TIPS(field.get(),lookup, menu, field)

"""
Use the following convention in GUI_util for those scripts that have no TIPS
TIPS_lookup = {'No TIPS available':''}
TIPS_options='No TIPS available'
"""
def trace_open_tips(field_local,menu_local,lookup_local):
    # print("field_local,menu_local,lookup_local ",field_local,menu_local,lookup_local)
    if lookup_local=={''}:
        mb.showinfo(title='TIPS Warning', message="There are no TIPS available for this script.")
        return
    global field, lookup, menu
    field=field_local
    lookup=lookup_local
    menu=menu_local
    field.trace("w",TIPS_Tracer)

