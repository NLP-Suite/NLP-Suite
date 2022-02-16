# written by Roberto Franzosi, Wei Dai January 1 2021

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_packages(GUI_util.window, "NLP",
                                          ['os', 'tkinter', 'itertools', 'PIL', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
from itertools import cycle
# https://pillow.readthedocs.io/en/3.0.x/handbook/tutorial.html
# https://pillow.readthedocs.io/en/stable/installation.html
# Pillow and PIL cannot co-exist in the same environment. Before installing Pillow, please uninstall PIL.
# Pillow >= 1.0 no longer supports “import Image”. Please use “from PIL import Image” instead.
from PIL import Image, ImageTk
from subprocess import call

import GUI_IO_util
import videos_util

GUI_size = str(GUI_IO_util.get_GUI_width(1)) + 'x600'

GUI_util.set_window(GUI_size, '', '', '')

window = GUI_util.window

'''
    OPTIONS FOR GRID https://www.tutorialspoint.com/python/tk_grid.htm
    This view uses Grid for layout. There are six columns in total. 
    Use widget.grid(row, column, rowspan=1, columnspan=1, padx=0, pady=0) for view layout
    where:
        row          The horizontal (x) position of the widget
        column       The vertical (y) position of the widget
        columnspan   The width of the widget, where columnspan=1 takes up 1/6 of the window width
                     and columnspan=6 takes up the whole window width
        rowspan      The height of the widget
        padx/pady    The horizontal/vertical padding around each widget
        sticky − What to do if the cell is larger than widget. 
                By default, with sticky='', widget is centered in its cell. 
                sticky may be the string concatenation of zero or more of N, E, S, W, NE, NW, SE, and SW, 
                compass directions indicating the sides and corners of the cell to which widget sticks.    
    Also, window.rowconfigure(x, weight=1) makes row x resizable. 
    Make sure to set ONLY resizable rows as resizable (for example, buttons are probably not resizable).
    Changing the weight changes relative heights.
    
    Currently:
    Row 0-4 are the three labels on top. 
    Row 5 are the "NLP Suite Team" and "How to cite" buttons
    Row 6 is the banner
    Row 7 are screenshots
    Row 8 is the "Enter NLP Suite" button 
    
'''


def run_NLP():
    if IO_libraries_util.check_inputPythonJavaProgramFile('NLP_menu_main.py') == False:
        return
    call("python NLP_menu_main.py", shell=True)

def close_NLP():
    global local_release_version, GitHub_release_version
    GUI_IO_util.exit_window(window, '', 'NLP_welcome_main', [0,0,0,0], [], local_release_version, GitHub_release_version)

def watch_video(video_button):
    videos_util.get_videos('File manager', {'File manager': 'NLP_File manager.mp4'}, video_button, '')

images = []


def make_images(canvas_width, canvas_height):
    images.clear()
    image_1_list = [GUI_IO_util.image_libPath + os.sep + "visual1.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual2.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual3.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual4.jpg"]
    image_2_list = [GUI_IO_util.image_libPath + os.sep + "visual5.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual6.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual7.jpg"]
    image_3_list = [GUI_IO_util.image_libPath + os.sep + "visual8.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual9.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual10.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual11.jpg",
                    GUI_IO_util.image_libPath + os.sep + "visual12.jpg"]
    # can use im.width, im.height in resize
    # .resize((450, 250), Image.ANTIALIAS)
    image_list = image_1_list + image_2_list + image_3_list
    photos_list = []
    for image in image_list:
        image_height = Image.open(image).height
        image_width = Image.open(image).width
        if canvas_height < image_height:
            image_width = image_width * canvas_height / image_height
            image_height = canvas_height
        if canvas_width < image_width:
            image_height = image_height * canvas_width / image_width
            image_width = canvas_width
        image_obj = Image.open(image).resize((int(image_width), int(image_height)), Image.ANTIALIAS)
        images.append(image_obj)
        photo_image = ImageTk.PhotoImage(image_obj)
        photos_list.append(photo_image)

    photos1 = cycle(photos_list[0:len(image_1_list)])
    photos2 = cycle(photos_list[len(image_1_list):len(image_1_list)+len(image_2_list)])
    photos3 = cycle(photos_list[len(image_1_list)+len(image_2_list):len(image_1_list)+len(image_2_list)+len(image_3_list)])
    return photos1, photos2, photos3


def run_slides():
    global photos1, photos2, photos3, canvas1, canvas_img1, canvas2, canvas_img2, image2, image3, canvas_img3, canvas3

    photos1, photos2, photos3 = make_images(1000, 1000)
    img, img2, img3 = next(photos1), next(photos2), next(photos3)

    # the 3 canvas are used to display different types of NLP visualization output across the window
    canvas1 = tk.Canvas(window)
    canvas1.grid(row=7, column=0, columnspan=2,padx=(20, 0))
    canvas_img1 = canvas1.create_image(canvas1.winfo_width()/2, canvas1.winfo_height()/2, image=img, anchor=tk.CENTER)

    canvas2 = tk.Canvas(window)
    canvas2.grid(row=7, column=2, columnspan=2)
    canvas_img2 = canvas2.create_image(canvas1.winfo_width()/2, canvas1.winfo_height()/2, image=img2,
                                       anchor=tk.CENTER)  # the 100,100 is not where image is on page, it's position WITHIN canvas!

    canvas3 = tk.Canvas(window)
    canvas3.grid(row=7, column=4, columnspan=2)
    canvas_img3 = canvas3.create_image(canvas1.winfo_width()/2, canvas1.winfo_height()/2, image=img3)


def display_text():

    welcome_line1 = tk.Label(window, text='Welcome to the NLP Suite', foreground="red", font=("Arial", 22, "bold","italic"))
    welcome_line1.grid(row=0, column=0, columnspan=6)

    welcome_line3 = tk.Label(window, text='\nNatural Language Processing & Visualization', foreground="black",
                             font=("Arial", 18, "bold", "italic"))
    welcome_line3.grid(row=1, column=0, columnspan=6)

    welcome_line4 = tk.Label(window,
                             text='\nFreeware, open source Python tools designed for humanists and social scientists with ZERO computer science background',
                             foreground="black", font=("Arial", 12))
    welcome_line4.grid(row=2, column=0, columnspan=6)


def display_enter_button():
    # display CLOSE button
    enter_button = tk.Button(window, text='CLOSE', width=15, height=1,
                             font=("Arial", 14),
                             command=lambda: close_NLP())
    enter_button.grid(row=9, column=4, columnspan=3, rowspan=2, sticky=(tk.N,tk.W),padx=30)

    # display Enter NLP button
    enter_button = tk.Button(window, text='Enter NLP Suite', width=20, height=2, foreground="red",
                             font=("Arial", 14, "bold"),
                             command=lambda: run_NLP())
    # enter_button.grid(row=8, column=4, columnspan=3, rowspan=2, pady=50)
    enter_button.grid(row=8, column=2, columnspan=2, rowspan=2, pady=50)

    roberto_franzosi = tk.Label(window,
                             text='Roberto Franzosi',
                             foreground="black", font=("Arial", 12,"italic"))
    roberto_franzosi.grid(row=8, column=0, columnspan=3, sticky=(tk.S,tk.W),padx=30)
    emory = tk.Label(window,
                             text='Emory University',
                             foreground="black", font=("Arial", 12,"italic"))
    emory.grid(row=9, column=0, columnspan=3, sticky=(tk.N,tk.W),padx=30)

    video_button = tk.Button(window, text='Watch video', width=15, height=1, foreground="red",
                             font=("Arial", 12, "italic"),
                             command=lambda: watch_video(video_button))
    video_button.configure(state='disabled')
    video_button.grid(row=9, column=1, columnspan=3, sticky=(tk.N,tk.W),padx=30)


def update_images():
    img = next(photos1)
    canvas1.itemconfig(canvas_img1, image=img)
    img2 = next(photos2)
    canvas2.itemconfig(canvas_img2, image=img2)
    img3 = next(photos3)
    canvas3.itemconfig(canvas_img3, image=img3)
    window.after(2000, update_images)


# running banner
svar = tk.StringVar()
# scolling_labl = tk.Label(window, textvariable=svar, height=10, width=1100, foreground="black",
scolling_labl=tk.Label(window, textvariable=svar, height=10, width=GUI_IO_util.get_GUI_width(1), foreground="black",
                                                font=("Arial", 14, 'italic'))


def display_running_banner():
    display_running_banner.msg = display_running_banner.msg[1:] + display_running_banner.msg[0]
    svar.set(display_running_banner.msg)
    window.after(100, display_running_banner)


def place_banner():
    display_running_banner.msg = '                    Go from texts to visuals at the simple click of a button!                    '
    display_running_banner()
    scolling_labl.grid(row=6, column=0, columnspan=6)


run_slides()
update_images()  # this MUST be before  displaying logo, text, and buttons

GUI_util.display_logo()
display_text()

# GUI_util.display_release()

scriptName = 'NLP_welcome_main.py'
GUI_util.display_about_release_team_cite_buttons(scriptName)

place_banner()
display_enter_button()

window.rowconfigure(6, weight=1)
window.rowconfigure(7, weight=1)
for i in range(0, 6):
    window.columnconfigure(i, weight=1)

def fit_images(event):
    global photos1, photos2, photos3, canvas1, canvas2, canvas3
    if event.widget is canvas1:
        photos1, photos2, photos3 = make_images(event.width, event.height)
        img = next(photos1)
        canvas1.itemconfig(canvas_img1, image=img)
        canvas1.coords(canvas_img1, event.width/2, event.height/2)

        img2 = next(photos2)
        canvas2.coords(canvas_img2, event.width/2, event.height/2)
        canvas2.itemconfig(canvas_img2, image=img2)

        img3 = next(photos3)
        canvas3.coords(canvas_img3, event.width/2, event.height/2)
        canvas3.itemconfig(canvas_img3, image=img3)

local_release_version, GitHub_release_version = GUI_util.display_release()

window.bind("<Configure>", fit_images)
window.mainloop()
