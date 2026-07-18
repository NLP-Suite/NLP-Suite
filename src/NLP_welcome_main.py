# written by Roberto Franzosi, Wei Dai January 1 2021

import sys
import IO_libraries_util
import GUI_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NLP_welcome_main",
                                          ['os', 'tkinter', 'itertools', 'PIL', 'subprocess']) == False:
    sys.exit(0)

import os
import tkinter as tk
from itertools import cycle

# https://pillow.readthedocs.io/en/3.0.x/handbook/tutorial.html
# https://pillow.readthedocs.io/en/stable/installation.html
# Pillow and PIL cannot co-exist in the same environment. Before installing Pillow, please uninstall PIL.
# Pillow >= 1.0 no longer supports “import Image”. Please use “from PIL import Image” instead.
from PIL import Image
from subprocess import call

import GUI_IO_util
import GUI_theme_util
# TODO RF
# import videos_util
import NLP_setup_update_util
import run_script_util

GUI_size = str(GUI_IO_util.get_GUI_width(2)) + 'x600'

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
    run_script_util.run_script("NLP_menu_main.py", "--from-welcome")

def close_NLP():
    global local_release_version, GitHub_release_version
    # NLP_setup_update_util.exit_window(window, '', 'NLP_welcome_main', [0,0,0,0], [], local_release_version, GitHub_release_version)
    NLP_setup_update_util.exit_window()

def watch_video(video_button):
    # videos_lookup = {'Setup external software': 'https://www.youtube.com/watch?v=K8jUe_pKPPQ'}
    # videos_options = 'Setup external software'
    import IO_internet_util
    if not IO_internet_util.check_internet_availability_warning(scriptName):
        return
    import webbrowser
    # TODO must change the url link to the welcome video when ready
    webbrowser.open('https://www.youtube.com/watch?v=K8jUe_pKPPQ')
    # GUI_util.watch_video(videos_lookup,scriptName)
    # videos_util.get_video(videos_options, videos_lookup)

def open_TIPS():
    import sys
    import subprocess
    TIPS_file='TIPS_NLP_Questions & answers.pdf'
    if os.path.isfile(os.path.join(GUI_IO_util.TIPSPath, TIPS_file)):
        if sys.platform in ['win32', 'cygwin', 'win64']:
            subprocess.Popen([GUI_IO_util.TIPSPath + os.sep + TIPS_file], shell=True)
        else:
            call(['open', GUI_IO_util.TIPSPath + os.sep + TIPS_file])

images = []

# Height budget for the slideshow row. The three canvases share it, so a fixed value keeps them the
# same height and stops a tall screenshot in one cell from shoving the neighbouring cells' images
# off their own baseline.
SLIDE_HEIGHT = 220


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
    # .resize((450, 250), Image.Resampling.LANCZOS)
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
        # https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
        image_obj = Image.open(image).resize((int(image_width), int(image_height)), Image.Resampling.LANCZOS)
        images.append(image_obj)
        # Native Tk PhotoImage (no PIL.ImageTk/_imagingtk) - see GUI_util.tk_image_from_pil:
        # the bundled portable Python's statically-embedded Tcl/Tk crashes ImageTk with
        # invalid command name "PyImagingPhoto".
        photo_image = GUI_util.tk_image_from_pil(image_obj)
        photos_list.append(photo_image)

    photos1 = cycle(photos_list[0:len(image_1_list)])
    photos2 = cycle(photos_list[len(image_1_list):len(image_1_list)+len(image_2_list)])
    photos3 = cycle(photos_list[len(image_1_list)+len(image_2_list):len(image_1_list)+len(image_2_list)+len(image_3_list)])
    return photos1, photos2, photos3


def _center_image(event, canvas, item):
    """Keep ``item`` in the middle of ``canvas`` as the cell resizes.

    Each canvas gets its own binding and uses its OWN width/height. The previous single
    window-level handler applied canvas1's geometry to all three canvases, so canvases 2 and 3
    were centered against a cell that was not theirs.
    """
    canvas.coords(item, event.width / 2, event.height / 2)


def run_slides():
    global photos1, photos2, photos3, canvas1, canvas_img1, canvas2, canvas_img2, image2, image3, canvas_img3, canvas3

    # Sized to the cell each canvas actually occupies (2 of 6 columns wide, minus the padding), not to
    # a 1000x1000 box. make_images only ever scales DOWN, so the old budget left the wider screenshots
    # at native size and let them overflow their cell, which is why they read as unaligned.
    # `or 1250` mirrors the banner label below: get_GUI_width can return None on an unresolved screen.
    cell_width = max(int((GUI_IO_util.get_GUI_width(2) or 1250) / 3) - 40, 120)
    photos1, photos2, photos3 = make_images(cell_width, SLIDE_HEIGHT)
    img, img2, img3 = next(photos1), next(photos2), next(photos3)

    # the 3 canvas are used to display different types of NLP visualization output across the window
    # CTk has no canvas widget, so these stay plain tk.Canvas (a sanctioned exception, like Listbox).
    # They do need painting by hand: a bare tk.Canvas defaults to a white/platform fill with a 2px
    # focus highlight, which against the themed window ground reads as three grey plates with borders
    # framing the screenshots. normalize_legacy_backgrounds skips Canvas, so set both here.
    canvas_style = {'background': GUI_theme_util.window_bg(), 'highlightthickness': 0, 'borderwidth': 0,
                    'height': SLIDE_HEIGHT}

    # sticky='nsew' so each canvas actually FILLS its grid cell. Without it the canvas shrinks to its
    # (unset, so default 378x265) requested size and sits centered in a cell of a different size, which
    # is half of why the screenshots did not line up with each other.
    canvas1 = tk.Canvas(window, **canvas_style)
    canvas1.grid(row=7, column=0, columnspan=2, padx=(20, 0), sticky='nsew')
    canvas2 = tk.Canvas(window, **canvas_style)
    canvas2.grid(row=7, column=2, columnspan=2, sticky='nsew')
    canvas3 = tk.Canvas(window, **canvas_style)
    canvas3.grid(row=7, column=4, columnspan=2, sticky='nsew')

    # The other half: every image was created at (winfo_width()/2, winfo_height()/2) read BEFORE the
    # canvases were mapped, so winfo_* returned 1 and all three images were anchored at (0.5, 0.5) --
    # i.e. pinned to the top-left corner, not centered. canvas3's create_image also omitted
    # anchor=tk.CENTER, so its image hung down and right of the other two. Both are fixed by placing
    # each image at its own canvas's real center, which _center_image does on every <Configure>.
    canvas_img1 = canvas1.create_image(0, 0, image=img, anchor=tk.CENTER)
    canvas_img2 = canvas2.create_image(0, 0, image=img2, anchor=tk.CENTER)
    canvas_img3 = canvas3.create_image(0, 0, image=img3, anchor=tk.CENTER)

    for canvas, item in ((canvas1, canvas_img1), (canvas2, canvas_img2), (canvas3, canvas_img3)):
        canvas.bind('<Configure>', lambda event, c=canvas, i=item: _center_image(event, c, i))


def display_text():

    # foreground="black" is dropped on the two lower lines: the CTk theme's text color follows the
    # appearance mode, and a hard-coded black is invisible on the dark-mode ground. The headline keeps
    # an explicit color, now the brand red rather than tk's pure "red".
    welcome_line1 = GUI_theme_util.create_label(window, text='Welcome to the NLP Suite',
                                                foreground=GUI_theme_util.NLP_SUITE_ACCENT,
                                                font=("Arial", 22, "bold","italic"))
    welcome_line1.grid(row=0, column=0, columnspan=6, pady=(12, 0))

    welcome_line3 = GUI_theme_util.create_label(window, text='Natural Language Processing & Visualization',
                                                font=("Arial", 18, "bold", "italic"))
    welcome_line3.grid(row=1, column=0, columnspan=6, pady=(6, 0))

    welcome_line4 = GUI_theme_util.create_label(window,
                             text='Freeware, open source Python tools designed for humanists and social scientists with ZERO computer science background',
                             font=("Arial", 12))
    welcome_line4.grid(row=2, column=0, columnspan=6, pady=(6, 0))


def display_bottom_line_buttons():
    # Byline: no hard-coded "black" -- the theme's text color follows the appearance mode.
    roberto_franzosi = GUI_theme_util.create_label(window,
                             text='Roberto Franzosi',
                             font=("Arial", 12,"italic"))
    roberto_franzosi.grid(row=8, column=0, columnspan=2, sticky=(tk.S,tk.W),padx=30)
    emory = GUI_theme_util.create_label(window,
                             text='Emory University',
                             font=("Arial", 12,"italic"))
    emory.grid(row=9, column=0, columnspan=2, sticky=(tk.N,tk.W),padx=30)

    # The columnspans on this row used to be 3 apiece from adjacent columns, so every widget's span
    # overlapped its neighbours' (col 1 covering 1-3, col 2 covering 2-4) and CLOSE at column 5 spanned
    # into two phantom columns past the 6-column grid, stretching it past the window's right edge.
    # Each widget now spans only what it occupies.
    TIPS_button = GUI_theme_util.create_button(window, text='Open TIPS file', width=15, height=1,
                             font=("Arial", 12, "italic"),
                             command=lambda: open_TIPS())
    TIPS_button.grid(row=9, column=2, sticky=(tk.N,tk.W),padx=30)

    video_button = GUI_theme_util.create_button(window, text='Watch video', width=15, height=1,
                             font=("Arial", 12, "italic"),
                             command=lambda: watch_video(video_button))
    # No welcome video recorded yet (see the TODO in watch_video), so the button is disabled -- and
    # under the CTk theme's rule that grey means inactive, _StateFillMixin now repaints it to match.
    video_button.configure(state='disabled')
    video_button.grid(row=9, column=3, sticky=(tk.N,tk.W),padx=30)

    # display Enter NLP button
    # accent=True: the one primary action on this window, the same treatment RUN gets elsewhere.
    enter_button = GUI_theme_util.create_button(window, text='Enter NLP Suite', width=20, height=2,
                             accent=True,
                             font=("Arial", 14, "bold"),
                             command=lambda: run_NLP())
    # column 4, not 3: with columnspan=2 from column 3 this button covered columns 3-4 and rows 8-9,
    # i.e. exactly the cell holding the "Watch video" button, and the two were drawn on top of each
    # other. The bottom row is now one widget per column -- TIPS (2), Watch video (3), ENTER (4),
    # CLOSE (5) -- with nothing overlapping.
    enter_button.grid(row=8, column=4, rowspan=2, pady=50)

    text_info_enter = "Click to access all the tools in the NLP Suite.\n\nLasciate ogni speranza, voi ch'entrate/Abandon hope all ye who enter here (Dante Inferno/Hell III, 9)."

    # Tooltips are bound to the widget now (GUI_theme_util.ToolTip) instead of being positioned from
    # hard-coded per-platform pixel coordinates that no longer describe where anything is. This also
    # retires the hand-rolled hover-color swapping (CTkButton has hover_color built in), the paired
    # <Enter>/<Leave> binds, and the extra <Button> bind that existed only because clicking ENTER
    # never fires <Leave>, so the old tooltip was left floating over the menu that opened. ToolTip
    # hides itself on <ButtonPress>.
    GUI_theme_util.ToolTip(enter_button, text_info_enter)

    # display close button
    close_button = GUI_theme_util.create_button(window, text='CLOSE', width=15, height=1,
                             font=("Arial", 14),
                             command=lambda: close_NLP())
    close_button.grid(row=9, column=5, sticky=(tk.N,tk.W),padx=30)

    text_info_close="Pressing the CLOSE button in any of the GUIs triggers the automatic update of the NLP Suite, pulling the latest release from GitHub.\nThe new release is displayed the next time you open your local NLP Suite."\
                                                   "\nYou must be connected to the internet for the auto update to work."
    GUI_theme_util.ToolTip(close_button, text_info_close)

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
# The marquee MUST go through create_label: CTkLabel forwards textvariable out of **kwargs, so a raw
# CTkLabel call drops it silently and the banner would sit there reading "CTkLabel" forever (plan §6).
# width is the window width in PIXELS, not characters -- a fixed-width box keeps the scrolling text
# from jittering as characters rotate through a proportional font. Passing it as a character count
# (the default) would ask for a ~10,000px label and blow out the grid, hence width_is_chars=False.
# The old height=10 was 10 text LINES of empty vertical padding; the banner is one line, so the
# spacing moves to the grid's pady where it belongs.
scolling_labl = GUI_theme_util.create_label(window, textvariable=svar, width_is_chars=False,
                                            width=GUI_IO_util.get_GUI_width(1) or 1250,
                                            font=("Arial", 14, 'italic'))

# The scrolling message, held on the module instead of as an attribute stuck on the function object.
banner_msg = '                    Go from texts to visuals at the simple click of a button!                    '


def display_running_banner():
    global banner_msg
    banner_msg = banner_msg[1:] + banner_msg[0]
    svar.set(banner_msg)
    window.after(100, display_running_banner)


def place_banner():
    display_running_banner()
    scolling_labl.grid(row=6, column=0, columnspan=6, pady=(10, 10))


run_slides()
update_images()  # this MUST be before displaying logo, text, and buttons

GUI_util.display_logo()
display_text()

# The release versions are displayed in GUI_util
# GUI_util.display_release()

scriptName = 'NLP_welcome_main.py'
GUI_util.display_about_release_team_cite_buttons(scriptName)

place_banner()
display_bottom_line_buttons()

# Repaint the plain-tk leftovers (the logo holder, the nav-button frame) from the platform button face
# to the themed window fill, so they stop reading as grey plates floating on the light CTk ground.
# Every other GUI gets this from GUI_bottom's _fit_window_to_content; the welcome window has no
# GUI_top/GUI_bottom chrome, so it calls it itself.
try:
    GUI_theme_util.normalize_legacy_backgrounds(window)
except Exception as e:
    print('legacy background normalization skipped:', e)

window.rowconfigure(6, weight=1)
window.rowconfigure(7, weight=1)
for i in range(0, 6):
    window.columnconfigure(i, weight=1)

local_release_version, GitHub_release_version = GUI_util.display_release()

# The old window-level <Configure> handler (fit_images) is gone: it fired for EVERY widget's configure
# event, rebuilt all twelve images from disk each time, and re-centered all three canvases against
# canvas1's geometry. Centering now lives on each canvas's own <Configure> (see _center_image), and
# the images are sized once, up front, to the cell they have to fit.
window.mainloop()
