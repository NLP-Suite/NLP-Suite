# Written by Roberto Franzosi January 2023

import sys
import GUI_util
import IO_libraries_util

# if pafy gives an error
#   pip uninstall pafy
#   pip install git+https://github.com/Cupcakus/pafy
# if IO_libraries_util.install_all_Python_packages('',"videos_util",['tkinter','vlc','pafy'])==False:
#     sys.exit(0)

import tkinter.messagebox as mb
# importing vlc module
# try:
#     import vlc
# except:
#     message = "FATAL ERROR. The imort of the vieo module vlc failed. Please, read carefully. The NLP Suite will exit the video script.\n\nThe script '" + \
#               "\n\nPlease, in command prompt/terminal, type" + \
#               "\n\nconda activate NLP\n\nThe command will activate the right NLP environment (NLP case sensitive) where to install the package. In the right NLP environment, type" + \
#               "\n\npip install python-vlc to install the vlc module, close the NLP Suite and try again."
#     mb.showinfo(title='python-vlc module', message=message)
#     sys.exit(0)
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
        mb.showinfo(title='videos keyError', message="There was an error in the videos dictionary lookup for \n\n" + selected_video +"\n\nPlease, report the issue to the NLP Suite developers.")
        return False
    play_video(lookup[selected_video])

# #Trace and open videos files based on user selection
# field = None
# lookup = None

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
