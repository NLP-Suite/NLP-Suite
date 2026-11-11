# import IO_libraries_util

# if IO_libraries_util.install_all_Python_packages(GUI_util.window, "IO_internet_util",
# 								['os', 'tkinter','urllib']) == False:
# 	sys.exit(0)

from tkinter import *
import tkinter.messagebox as mb
from urllib.request import urlopen  # to check internet connection

# check internet connection
# if internet connection is available, return True #otherwise, return False
# If you ARE connected to the internet, and the check ALWAYS returns false, from cmmand line you will need
#   /Applications/Python 3.7/Install Certificates.command then import from urllib.request import urlopen
#   on some machines the SSL certificate is required
#   https://docs.python.org/3/library/urllib.request.html


def internet_on():
    # A raw TCP connection to a public DNS server is the most reliable "is the internet up" check --
    # it doesn't depend on HTTP/HTTPS, SSL certificates, or any single web host being reachable. The old
    # check hit only http://www.google.com with a 10s timeout, so a single flaky request (SSL error,
    # momentary timeout, that host blocked) produced a FALSE "no internet" even when the user was online.
    import socket

    for host in ("1.1.1.1", "8.8.8.8"):  # Cloudflare and Google public DNS
        try:
            with socket.create_connection((host, 53), timeout=3):
                return True
        except Exception:
            continue
    # fallback: an HTTPS fetch, in case port 53 is firewalled but the web works
    for url in ("https://www.google.com", "https://www.github.com"):
        try:
            urlopen(url, timeout=5)
            return True
        except Exception:
            continue
    return False


# if internet connection is available, return True #otherwise, pop up warning
# script can be Gensim, Stanford CoreNLP or any script that requires internet cnnection to run
def check_internet_availability_warning(script):
    if not internet_on():
        print(
            "Internet is not available... The script '"
            + script
            + "' requires internet connection to run. Please, check internet connection and try again."
        )
        # mb.showwarning(title='Internet Connection', message='Internet is not available... The script "' + script + '" requires internet connection to run.\n\nPlease, check internet connection and try again.')
        answer = mb.askyesno(
            "Warning",
            "Internet is not available... The script '"
            + script
            + "' requires internet connection to run.\n\nPlease, check internet connection and try again.\n\n\nIf you are running '"
            + script
            + "' from a country (e.g., China) with internet access barriers but you are connected to internet by other means (e.g., VPN) you can bypass the NLP Suite internet check.\n\nWould you like to bypass the check and run '"
            + script
            + "' anyway?",
        )
        if answer == True:
            return True
        else:
            return False
    else:
        return True


def report_download_failure(script, err, resource="a language model"):
    """Show, in the GUI, WHY a model download failed.

    Without this the exception reaches the terminal only. A user who launched the Suite from the app --
    which is everyone outside development -- then sees the window close with no explanation at all,
    because the traceback goes to a console they never look at."""
    detail = type(err).__name__ + ": " + str(err)
    print("Download failed in '" + script + "': " + detail)
    mb.showerror(
        title="Language model could not be downloaded",
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
        "The analysis cannot run until the model is available.",
    )


def download_with_warning(script, download_function, resource="a language model"):
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
    except Exception as first_err:
        failure = first_err
        if check_internet_availability_warning(script):
            try:
                download_function()
                return True
            except Exception as retry_err:
                failure = retry_err
        report_download_failure(script, failure, resource)
        return False


def stanza_resources_dir():
    """Where Stanza keeps its models, asked of Stanza itself.

    Since Stanza 1.10 this is a per-version cache folder (STANZA_RESOURCES_DIR if set), e.g.
    ~/Library/Caches/stanza/1.14.0/resources on Mac. The old ~/stanza_resources is no longer used; checking
    it made the model look missing on every machine, so it was re-downloaded at every import (issue #1703)."""
    from stanza.resources.common import DEFAULT_MODEL_DIR

    return DEFAULT_MODEL_DIR


def stanza_model_present(lang="en", resources_dir=None):
    """True when the Stanza model for `lang` is already unpacked on disk.

    The test is an unpacked tokenizer model (<resources>/<lang>/tokenize/*.pt). The folder alone is not
    enough: a first download that was interrupted leaves <lang>/default.zip and nothing usable."""
    import os

    tokenize_dir = os.path.join(resources_dir or stanza_resources_dir(), lang, "tokenize")
    try:
        return any(name.endswith(".pt") for name in os.listdir(tokenize_dir))
    except OSError:
        return False


def folder_size_mb(path):
    """Size of everything under `path`, in whole MB (0 if it does not exist yet)."""
    import os

    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                continue  # a file the download is renaming or unpacking right now; counted on the next pass
    return total // (1024 * 1024)


def downloaded_mb(dirs):
    """MB written so far to the first of `dirs` that exists (None entries are skipped).

    A download may land in more than one folder (a cache first, then a copy); counting only the first
    one that exists shows the bytes that came over the network, without counting the copy twice."""
    import os

    for path in dirs:
        if path and os.path.isdir(path):
            return folder_size_mb(path)
    return 0


def huggingface_stanza_cache_dir(lang):
    """The Hugging Face cache folder that a Stanza `lang` download writes to first, or None without
    huggingface_hub (older Stanza versions download straight into their own folder)."""
    import os

    try:
        import huggingface_hub.constants as hf_constants
    except ImportError:
        return None
    return os.path.join(hf_constants.HF_HUB_CACHE, "models--stanfordnlp--stanza-" + lang)


class xet_off:
    """Download from Hugging Face over plain HTTP, not Xet, while inside this `with` block.

    Xet downloads of the Stanza models stalled at 0 bytes on a Mac for minutes, while the same files over
    plain HTTP finished (issue #1703). huggingface_hub reads the HF_HUB_DISABLE_XET environment variable
    only at import, but it checks this constant on every download, so setting it here works at run time.
    The previous value is restored on the way out."""

    def __enter__(self):
        try:
            import huggingface_hub.constants as hf_constants
        except ImportError:
            self._constants = None  # older Stanza: no huggingface_hub, no Xet
            return self
        self._constants = hf_constants
        self._previous = hf_constants.HF_HUB_DISABLE_XET
        hf_constants.HF_HUB_DISABLE_XET = True
        return self

    def __exit__(self, *exc):
        if self._constants is not None:
            self._constants.HF_HUB_DISABLE_XET = self._previous
        return False


def run_with_progress(work, window=None, *, title="Please wait", message="", watch_dir=None, poll_seconds=0.1):
    """Run `work()` in a background thread, keeping the GUI alive until it ends.

    With a `window`, a small modal window shows `message` (and, with `watch_dir`, how many MB have been
    written so far) and stays up until the work ends, so a long download neither freezes the GUI nor
    disappears after a few seconds. `watch_dir` is a folder or a list of folders (see downloaded_mb).
    An exception raised by `work` is re-raised here, on the calling thread."""
    watch_dirs = [watch_dir] if isinstance(watch_dir, str) else list(watch_dir or [])
    import threading
    import tkinter as tk

    outcome = {}

    def target():
        try:
            work()
        except BaseException as e:  # handed back to the calling thread below
            outcome["error"] = e

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    box = status = None
    if window is not None:
        box = tk.Toplevel(window)
        box.title(title)
        box.resizable(False, False)
        box.transient(window)
        box.protocol("WM_DELETE_WINDOW", lambda: None)  # it closes by itself when the work ends
        tk.Label(box, text=message, justify=tk.LEFT, wraplength=440, padx=20, pady=12).pack()
        status = tk.Label(box, text="", padx=20, pady=8)
        status.pack()
        box.grab_set()  # no second RUN while the first one waits for its model
        box.lift()  # in front, not hidden behind another app's window
        box.focus_force()
    try:
        while thread.is_alive():
            if box is not None:
                if watch_dirs and status is not None:
                    status.config(text="Downloaded so far: " + str(downloaded_mb(watch_dirs)) + " MB")
                box.update()
            thread.join(poll_seconds)
    finally:
        if box is not None:
            box.grab_release()
            box.destroy()
    if "error" in outcome:
        raise outcome["error"]


def stanza_download_message(lang="en", language_name=None):
    """What the user reads while a Stanza model downloads."""
    name = language_name or ("English" if lang == "en" else lang)
    size = "about 1 GB" if lang == "en" else "several hundred MB to about 1 GB"
    return (
        "Downloading the Stanza " + name + " language model (" + size + ").\n\n"
        "This happens only the first time the model is used. It may take several minutes, depending on "
        "your internet connection.\n\nThis window closes by itself when the download is done."
    )


def ensure_stanza_model(
    script, download_function=None, resource=None, *, lang="en", resources_dir=None, window=None, language_name=None
):
    """Download the Stanza model only when it is not on disk yet. Returns True when it is available.

    Call it when a tool is about to use Stanza, not at import. stanza.download() fetches the resources
    list from GitHub and re-hashes every model file even when nothing is missing (9-11 s per call), and
    with no network it waits. A model that is present is trusted here; if one of its files is missing,
    stanza.Pipeline() fetches that file itself when the pipeline is built.

    With a `window`, the download runs in the background behind a window that stays up until it ends
    (see run_with_progress). A failed download is shown in a dialog (download_with_warning)."""
    import os

    if stanza_model_present(lang, resources_dir):
        return True

    def stanza_download():
        import stanza

        with xet_off():
            stanza.download(lang, model_dir=resources_dir or stanza_resources_dir())

    if resource is None:
        resource = "the Stanza " + (language_name or lang) + " language model"
    # Stanza 1.14 downloads into the Hugging Face cache and copies each file over only when it is complete,
    # so the Stanza folder alone stays at 0 MB until the end
    watch_dir = [huggingface_stanza_cache_dir(lang), os.path.join(resources_dir or stanza_resources_dir(), lang)]

    def download():
        run_with_progress(
            download_function or stanza_download,
            window,
            title="Stanza model download",
            message=stanza_download_message(lang, language_name),
            watch_dir=watch_dir,
        )

    return download_with_warning(script, download, resource)


class LazyModel:
    """A model (e.g. a Stanza pipeline) that is built the first time it is used, not at import.

    It stands in for the real object: calling it, or reading an attribute of it, builds the model once
    and passes the call through, so code written as `stanzaPipeLine(text)` needs no change. Building it
    at import made every GUI that might use it wait for it (8.7 s for the shared Stanza pipeline) before
    drawing its window.

    A failed build is shown in the GUI and then raised: the caller cannot go on without the model, and
    the next use tries again (the connection may be back)."""

    def __init__(self, build, script, resource="a language model"):
        self._build = build
        self._script = script
        self._resource = resource
        self._model = None

    def _get(self):
        if self._model is None:
            try:
                model = self._build()
                if model is None:
                    raise RuntimeError(self._resource + " is not available")
            except Exception as e:
                report_download_failure(self._script, e, self._resource)
                raise
            self._model = model
        return self._model

    def __call__(self, *args, **kwargs):
        return self._get()(*args, **kwargs)

    def __getattr__(self, name):
        # only reached for names not set in __init__, i.e. the real model's attributes
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._get(), name)


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
