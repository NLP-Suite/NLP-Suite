import logging
from urllib.request import urlopen  # to check internet connection

logger = logging.getLogger(__name__)

# check internet connection
# if internet connection is available, return True #otherwise, return False
# If you ARE connected to the internet, and the check ALWAYS returns false, from cmmand line you will need
#   /Applications/Python 3.7/Install Certificates.command then import from urllib.request import urlopen
#   on some machines the SSL certificate is required
#   https://docs.python.org/3/library/urllib.request.html


def internet_on():
    try:
        urlopen("http://www.google.com/", timeout=10)
        return True
    except Exception:
        return False


# if internet connection is available, return True #otherwise, pop up warning
# script can be Gensim, Stanford CoreNLP or any script that requires internet cnnection to run
def check_internet_availability_warning(script):
    if not internet_on():
        logger.info(
            "Internet is not available... The script '"
            + script
            + "' requires internet connection to run. Please, check internet connection and try again."
        )
        logger.info(
            "Warning %s",
            "Internet is not available... The script '"
            + script
            + "' requires internet connection to run.\n\nPlease, check internet connection and try again.\n\n\nIf you are running '"
            + script
            + "' from a country (e.g., China) with internet access barriers but you are connected to internet by other means (e.g., VPN) you can bypass the NLP Suite internet check.\n\nWould you like to bypass the check and run '"
            + script
            + "' anyway?",
        )
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
