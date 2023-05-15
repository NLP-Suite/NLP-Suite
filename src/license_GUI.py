import sys
import os
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import GUI_util
import config_util

GUI_size='700x550'
GUI_label='License agreement for suite of NLP tools'
config_filename='license_config.csv'

# The 4 values of config_option refer to:
#   input file
        # 1 for CoNLL file
        # 2 for TXT file
        # 3 for csv file
        # 4 for any type of file
        # 5 for txt or html
        # 6 for txt or csv
#   input dir
#   input secondary dir
#   output dir
config_input_output_numeric_options=[0,0,0,0]
current_config_input_output_alphabetic_options = ['', '', '', '', ]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

text_area = tk.Text()
# text_area.configure(height=440)
text_area.pack()

if (os.path.isfile(os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-Suite-1.0.txt'))):
	f= open(os.path.join(GUI_IO_util.libPath, "LICENSE-NLP-Suite-1.0.txt"))
else:
	if (os.path.isfile(os.path.join(GUI_IO_util.libPath, 'LICENSE-NLP-1.0.txt'))):
		f = open(os.path.join(GUI_IO_util.libPath, "LICENSE-NLP-1.0.txt"))
		# rename the file to the new standard
		os.rename('LICENSE-NLP-1.0.txt', 'LICENSE-NLP-Suite-1.0.txt')
	else:
		mb.showwarning(title='Fatal error', message="The licence agreement file 'LICENSE-NLP-Suite-1.0.txt' could not be found in the 'lib' subdirectory of your main NLP Suite directory\n" + GUI_IO_util.scriptPath + "\n\nPlease, make sure to copy this file in the 'lib' subdirectory.\n\nThe NLP Suite will now exit.")
		sys.exit()
	
text_area.insert(tk.END, f.read())

agreement_checkbox_var=tk.IntVar()
agreement_checkbox = tk.Checkbutton(GUI_util.window, variable=agreement_checkbox_var, onvalue=1, offvalue=0, text="I have read and agree with the license terms")
agreement_checkbox.place(x=10, y=500)
agreement_checkbox_var.set(0)

def save_agreement(*args):
	if agreement_checkbox_var.get()==1:
		# first time users may not have the config directory
		if os.path.isdir(GUI_IO_util.configPath) == False:
			try:
				os.mkdir(GUI_IO_util.configPath)
			except:
				mb.showwarning(title='Permission error?',
							   message="The command failed to create the Config directory.\n\nIf you look at your command line and you see a \'Permission error\', it means that the folder where you installed your NLP Suite is Read only.\n\nYou can check whether that's the case by right clicking on the folder name, clicking on \'Properties\'. Make sure that the \'Attributes\' setting, the last one on the display window, is NOT set to \'Read only\'. If so, click on the checkbox until the Read only is cleared, click on \'Apply\' and then \'OK\', exit the NLP Suite and try again.")
				return
		config_util.write_IO_config_file(GUI_util.window, config_filename, config_input_output_numeric_options,
									  current_config_input_output_alphabetic_options)
		GUI_util.window.destroy()
agreement_checkbox_var.trace('w',save_agreement)

# sidebar
# sidebar = tk.Frame(GUI_util.window, width=900, bg='white', height=640, relief='sunken', borderwidth=2)
# sidebar.pack(expand=True, fill='both', side='left', anchor='nw')

# main content area
# mainarea = tk.Frame(GUI_util.window, bg='#CCC', width=900, height=640)
# mainarea.pack(expand=True, fill='both', side='right')

GUI_util.window.mainloop()

