# Written by Roberto Franzosi January 2023

import sys
import GUI_util
import IO_libraries_util

# if pafy gives an error
#   pip uninstall pafy
#   pip install git+https://github.com/Cupcakus/pafy
if IO_libraries_util.install_all_packages(GUI_util.window,"videos_util",['tkinter','vlc','pafy'])==False:
    sys.exit(0)

import tkinter.messagebox as mb
# importing vlc module
import vlc
# importing pafy module
import pafy

import IO_internet_util

# def get_videos(selected_videos,lookup,menu_lb, dropdown_field):
def get_video(selected_video, lookup):
    # lookup[selected_video] contains the YouTube video url
    if selected_video=='Watch videos':
        return
    if lookup=={''} or selected_video=='No videos available':
        mb.showinfo(title='videos Warning', message="There are no videos available for this GUI.")
        return
    try:
        if len(lookup[selected_video])==0:
            pass
    except:
        mb.showinfo(title='videos keyError', message="There was an error in the videos dictionary lookup for \n\n" + selected_videos +"\n\nPlease, report the issue to the NLP Suite developers.")
        return False
    play_video(lookup[selected_video])

# #Trace and open videos files based on user selection
# field = None
# lookup = None
def videos_Tracer(*args):
    if lookup=={''}:
        mb.showinfo(title='videos Warning', message="There are no videos available for this GUI.")
        return
    if len(field.get())=='No videos available':
        mb.showinfo(title='videos Warning', message="There are no videos available for this GUI.")
        return
    if field.get()!='Watch videos':
        get_video(field.get(), lookup)
#
def trace_open_videos(field_local,lookup_local):
    # print("field_local,menu_local,lookup_local ",field_local,menu_local,lookup_local)
    global field, lookup
    field=field_local
    lookup=lookup_local
    field.trace("w",videos_Tracer)

def play_video(video_url):
    if not IO_internet_util.check_internet_availability_warning("videos_util.py"):
        return
    try:
        # creating pafy object of the video
        video = pafy.new(video_url)
    except:
        # if pafy gives an error
        #   pip uninstall pafy
        #   pip install git+https://github.com/Cupcakus/pafy
        mb.showinfo(title='Warning', message="The YouTube video module pafy has raised an error.\n\nPlease, in command line/prompt and in the NLP environment type\n\npip uninstall pafy\n\nWhen uninstalling pafy is complete, type\n\npip install git+https://github.com/Cupcakus/pafy\n\nClose the NLP Suite and try again.")
        return
    # getting best stream
    best = video.getbest()
    # creating vlc media player object
    media = vlc.MediaPlayer(best.url)
    # media.set_hwnd(GUI_util.window.handle)
    # start playing video
    media.play()
