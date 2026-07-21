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
    # A raw TCP connection to a public DNS server is the most reliable "is the internet up" check --
    # it doesn't depend on HTTP/HTTPS, SSL certificates, or any single web host being reachable. The old
    # check hit only http://www.google.com with a 10s timeout, so a single flaky request (SSL error,
    # momentary timeout, that host blocked) produced a FALSE "no internet" even when the user was online.
    import socket
    for host in ('1.1.1.1', '8.8.8.8'):  # Cloudflare and Google public DNS
        try:
            with socket.create_connection((host, 53), timeout=3):
                return True
        except Exception:
            continue
    # fallback: an HTTPS fetch, in case port 53 is firewalled but the web works
    for url in ('https://www.google.com', 'https://www.github.com'):
        try:
            urlopen(url, timeout=5)
            return True
        except Exception:
            continue
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


def report_download_failure(script, err, resource='a language model'):
    """Show, in the GUI, WHY a model download failed.

    Without this the exception reaches the terminal only. A user who launched the Suite from the app --
    which is everyone outside development -- then sees the window close with no explanation at all,
    because the traceback goes to a console they never look at."""
    detail = type(err).__name__ + ': ' + str(err)
    print("Download failed in '" + script + "': " + detail)
    mb.showerror(title='Language model could not be downloaded',
                 message="The NLP Suite could not download " + resource + " needed by '" + script + "'.\n\n"
                 "TECHNICAL DETAIL\n" + detail + "\n\n"
                 "The models are fetched from the internet the FIRST time they are used, then cached, so "
                 "this normally happens only once.\n\n"
                 "WHAT TO DO\n"
                 "  1. Check that you are connected to the internet, and try again.\n"
                 "  2. A VPN, a proxy or an institutional firewall may block the download even when other "
                 "sites open normally: the models come from raw.githubusercontent.com and "
                 "huggingface.co.\n"
                 "  3. If you cannot reach those sites, you can select a different NLP package (Stanford "
                 "CoreNLP or spaCy) in the NLP Suite setup, under 'Setup NLP package and language'.\n\n"
                 "The analysis cannot run until the model is available.")


def download_with_warning(script, download_function, resource='a language model'):
    """Download a model, surfacing any failure in the GUI instead of only on the terminal.

    On failure the user is offered the usual internet-check bypass (for VPN or proxy users whose
    connection the Suite's own check cannot see); if they accept, the download is RETRIED -- the previous
    code offered the bypass but never tried again, so answering Yes changed nothing and the script
    carried on to crash later with an unhandled ConnectionError.

    Returns True when the model is available, False when it is not, so callers can degrade instead of
    dying."""
    try:
        download_function()
        return True
    except Exception as err:
        if check_internet_availability_warning(script):
            try:
                download_function()
                return True
            except Exception as retry_err:
                err = retry_err
        report_download_failure(script, err, resource)
        return False

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
