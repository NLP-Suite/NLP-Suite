import sys
import GUI_util
# import IO_libraries_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "IO_internet_util",
# 								['os', 'tkinter','urllib']) == False:
# 	sys.exit(0)

from urllib.request import urlopen #to check internet connection
from tkinter import *
import tkinter.messagebox as mb

#check internet connection
#if internet connection is available, return True #otherwise, return False
#If you ARE connected to the internet, and the check ALWAYS returns false, from cmmand line you will need
#   /Applications/Python 3.7/Install Certificates.command then import from urllib.request import urlopen
#   on some machines the SSL certificate is required
#   https://docs.python.org/3/library/urllib.request.html

def internet_on():
    try:
        response = urlopen('https://www.bing.com/', timeout=10)
        return True
    except:
        return False

#if internet connection is available, return True #otherwise, pop up warning
#script can be Gensim, Stanford CoreNLP or any script that requires internet cnnection to run
def check_internet_availability_warning(script):
    if not internet_on():
        print("Internet is not available... The script '" + script + "' requires internet connection to run. Please, check internet connection and try again.")
        # mb.showwarning(title='Internet Connection', message='Internet is not available... The script "' + script + '" requires internet connection to run.\n\nPlease, check internet connection and try again.')
        answer = mb.askyesno("Warning", "Internet is not available... The script '" + script + "' requires internet connection to run.\n\nPlease, check internet connection and try again.\n\n\nIf you are running '" + script + "' from a country (e.g., China) with internet access barriers but you are connected to internet by other means (e.g., VPN) you can bypass the NLP Suite internet check.\n\nWould you like to bypass the check and run '" + script + "' anyway?")
        if answer == True:
            return True
        else:
            return False
    else:
        return True

"""
'strict' to raise a ValueError exception if there is an encoding error. The default value of None has the same effect.
'ignore' ignores errors. Note that ignoring encoding errors can lead to data loss. IT WILL SIMPLY TAKE OUT THE OFFENDING CHARACTER
'replace' causes a replacement marker (such as '?') to be inserted where there is malformed data.
'surrogateescape' will represent any incorrect bytes as code points in the Unicode Private Use Area ranging from U+DC80 to U+DCFF.
   These private code points will then be turned back into the same bytes when the surrogateescape error handler is used when writing data. 
   This is useful for processing files in an unknown encoding.

Opening the file with anything other than 'strict' 
    ('ignore',  'replace', etc.) will let you read 
    the file without exceptions being raised.

Note that decoding takes place per buffered block of data, 
not per textual line. 
If you must detect errors on a line-by-line basis, use the 
surrogateescape handler and test each line read for codepoints 
in the surrogate range

"""
