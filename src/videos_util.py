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

def get_videos(selected_videos,lookup,menu_lb, dropdown_field):
    # lookup[selected_videos] would throw a keyError 
    #   if there is a different spelling, even in letter case
    #   between videos_lookup and videos_options, for instance
    #   videos_lookup = {'NLP Searches': 'videos_NLP_NLP searches.pdf'}
    #   videos_options='NLP searches'
    try:
        if len(lookup[selected_videos])==0:
            pass
    except:
        mb.showinfo(title='videos keyError', message="There was an error in the videos dictionary lookup for \n\n" + selected_videos +"\n\nPlease, report the issue to the NLP Suite developers.")
        return False
    if selected_videos=='No videos available':
        mb.showinfo(title='videos Warning', message="There are no videos available for this script.")
        return False
    if menu_lb['state']!='disabled':
        if os.path.isfile(os.path.join(GUI_IO_util.videosPath, lookup[selected_videos]))==False:
            videosFile_Exists=False
            mb.showinfo(title='videos Warning', message="The videos file\n\n"+lookup[selected_videos]+"\n\ncould not be found in your videos directory.")
            return False
        else:
            videosFile_Exists=True
            if sys.platform in ['win32','cygwin','win64']:
                subprocess.Popen([GUI_IO_util.videosPath + os.sep + lookup[selected_videos]], shell=True)
            else:
                call(['open', GUI_IO_util.videosPath + os.sep + lookup[selected_videos]])
        return videosFile_Exists

def checkvideosDir(menu_lb):
    videos_dir_exists = True
    # win_videosSubdir = os.path.join(NLPPath,'videos') #videosPath+os.sep+'videos'+os.sep
    # unix_videosSubdir = os.path.join(NLPPath,'videos') #'videos'+os.sep
    if not os.path.isdir(GUI_IO_util.videosPath):
        mb.showinfo(title='videos Warning', message='The script could not find a videos subdirectory. videos should be stored in a subdirectory called videos where your python script is stored.')
        menu_lb.configure(state='disabled')
        videos_dir_exists = False
    return videos_dir_exists

#Trace and open videos files based on user selection
field = None
lookup = None
menu = None
def videos_Tracer(*args):
    if len(field.get())=='No videos available':
        mb.showinfo(title='videos Warning', message="There are no videos available for this script.")
        return
    foundvideos = checkvideosDir(menu)
    if foundvideos and field.get()!='Watch videos':
        get_videos(field.get(),lookup, menu, field)

"""
Use the following convention in GUI_util for those scripts that have no videos
videos_lookup = {'No videos available':''}
videos_options='No videos available'
"""
def trace_open_videos(field_local,menu_local,lookup_local):
    # print("field_local,menu_local,lookup_local ",field_local,menu_local,lookup_local)
    if lookup_local=={''}:
        mb.showinfo(title='videos Warning', message="There are no videos available for this script.")
        return
    global field, lookup, menu
    field=field_local
    lookup=lookup_local
    menu=menu_local
    field.trace("w",videos_Tracer)

def open_videos(selected_videos):
    if os.path.isfile(os.path.join(GUI_IO_util.videosPath, selected_videos)) == False:
        videosFile_Exists = False
        mb.showinfo(title='videos Warning', message="The video file\n\n" + lookup[
            selected_videos] + "\n\ncould not be found in your videos directory.")
        return False
    else:
        videosFile_Exists = True
        if sys.platform in ['win32', 'cygwin', 'win64']:
            subprocess.Popen([GUI_IO_util.videosPath + os.sep + selected_videos], shell=True)
        else:
            call(['open', GUI_IO_util.videosPath + os.sep + selected_videos])
    return videosFile_Exists

