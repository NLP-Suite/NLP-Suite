#!/usr/bin/env python
"""GUI construction smoke test for the NLP Suite   (run:  python tests/gui_smoke.py)

WHY THIS EXISTS
The ~50 `src/*_main.py` GUIs are built by hand-placed Tk widgets and have NO automated coverage,
so a refactor can silently break a GUI's construction, or drop a whole widget row -- exactly what
happened to the DB_SQL "Select INPUT CSV file" row (removed as a side effect of an unrelated
data-validation commit, caught only by eye weeks later). This script gives that class of regression
a tripwire.

WHAT IT DOES
Imports EACH `src/*_main.py` in a fresh subprocess, with Tk / GUI_util / IO_libraries_util and the
heavy NLP libraries STUBBED (no real display, no pip, no models). So:
  * CONSTRUCTION CRASHES (undefined names, bad imports, an exception while building widgets at import
    time) are caught for every GUI; and
  * for a curated set of KEY GUIs, GOLDEN checks assert that specific widget LABELS still exist --
    which is what catches a silently-dropped row.

It's a standalone script (no `test_` prefix), matching tests/ctk_bundle_smoke.py, because the repo
has no pytest CI. Run it before shipping a GUI change. Exit 0 = all good; non-zero = a crash or a
missing golden widget. Prints a per-GUI report.
"""
import os
import sys
import glob
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(os.path.dirname(_HERE), 'src')

# GUIs whose specific widget LABELS must exist (catches a dropped/renamed load-bearing row).
# Keep these to rows that matter -- not every button.
GOLDEN = {
    'DB_SQL_main.py': ['Select INPUT CSV file', 'Generate SQL query', 'WHERE filter'],
    'corpus_profiler_main.py': ['Who did what to whom?  (Narrative)', 'What do the words mean?  (Semantics)'],
}

# Filenames matching these are NOT GUIs to smoke-test (helpers/launchers/skeletons).
_NOT_GUI = ('NLP_menu_notebook_skeleton',)

# GUIs that can't be reached by these stubs: at CONSTRUCTION they consume real GUI_util/tk-Var state
# or read real files (numeric attrs used before our defaults apply, conditional assignments gated on
# real config, a CSV read at build time, ...). They are NOT known-broken -- just not smoke-testable
# this way; verify them by launching. Listed so a real regression ELSEWHERE still turns the run red.
KNOWN_SKIP = {
    'GIS_Google_Earth_main.py', 'NLP_menu_main.py', 'NLP_setup_IO_main.py',
    'NLP_setup_external_software_main.py', 'NLP_welcome_main.py',
    'file_checker_pre_processing_pipeline_main.py',
}

# The per-GUI subprocess harness: stub the world, import the target, print OK + recorded widget texts.
_HARNESS = r'''
import sys, os, types, traceback
from unittest.mock import MagicMock
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')   # widget labels contain -> etc.
except Exception:
    pass

_texts = []

def _rec(*a, **k):
    t = k.get('text')
    if t is not None:
        try: _texts.append(str(t))
        except Exception: pass
    return MagicMock()

# ---------- fake tkinter ----------
_tk = types.ModuleType('tkinter')
for _n in ('Tk','Toplevel','Frame','LabelFrame','Button','Label','Entry','Text','Checkbutton',
           'Radiobutton','Canvas','Scrollbar','Listbox','Menu','Menubutton','OptionMenu','Spinbox',
           'PanedWindow','Scale','Message'):
    setattr(_tk, _n, _rec)
# Tk variables need real .get() values -- code does `if intvar.get() > 1`, `strvar.get()=='x'`, etc.
def _mkvar(_default):
    class _V(object):
        def __init__(self, *a, **k):
            self._v = k.get('value', _default)
        def get(self):
            return self._v
        def set(self, v):
            self._v = v
        def __getattr__(self, _n):
            return MagicMock()
    return _V
_tk.StringVar = _mkvar('')
_tk.IntVar = _mkvar(0)
_tk.DoubleVar = _mkvar(0.0)
_tk.BooleanVar = _mkvar(False)
for _c in ('END','W','E','N','S','NW','NE','SW','SE','NS','EW','NSEW','LEFT','RIGHT','TOP','BOTTOM',
           'CENTER','X','Y','BOTH','NONE','HORIZONTAL','VERTICAL','DISABLED','NORMAL','ACTIVE','WORD',
           'CHAR','SINGLE','MULTIPLE','EXTENDED','BROWSE','RAISED','SUNKEN','FLAT','GROOVE','RIDGE',
           'SOLID','INSERT','ANCHOR','SEL','SEL_FIRST','SEL_LAST'):
    setattr(_tk, _c, _c)
_tk.TclError = Exception
sys.modules['tkinter'] = _tk
_ttk = types.ModuleType('tkinter.ttk')
for _n in ('Combobox','Treeview','Notebook','Progressbar','Separator','Style','Frame','Label',
           'Button','Entry','Scrollbar','Checkbutton','Radiobutton','Scale','Spinbox','LabelFrame',
           'Panedwindow','Sizegrip'):
    setattr(_ttk, _n, _rec)
sys.modules['tkinter.ttk'] = _ttk
_tk.ttk = _ttk
for _sub in ('filedialog','messagebox','font','colorchooser','simpledialog','scrolledtext','dnd'):
    _m = MagicMock(); sys.modules['tkinter.'+_sub] = _m; setattr(_tk, _sub, _m)

# ---------- neutralize import-time guards / heavy infra ----------
_iolib = MagicMock()
_iolib.install_all_Python_packages.return_value = True    # not False -> the guard won't sys.exit
sys.modules['IO_libraries_util'] = _iolib

# GUI_util is a mock, BUT its Tk .window feeds GUI_IO_util.GUI_settings() which computes sizes/offsets
# from winfo_* geometry -- those must be real numbers or downstream numeric comparisons crash with
# "'>' not supported between MagicMock and float". Give the geometry queries realistic ints, and give
# the fixed-shape helpers a right-sized tuple so `a, b, ... = GUI_util.setup_parsers_annotators(...)`
# unpacks. (These are stub conveniences, not assertions about GUI_util's real API.)
_guiu = MagicMock()
for _wm in ('winfo_screenwidth', 'winfo_screenheight', 'winfo_width', 'winfo_height', 'winfo_x',
            'winfo_y', 'winfo_reqwidth', 'winfo_reqheight', 'winfo_rootx', 'winfo_rooty'):
    getattr(_guiu.window, _wm).return_value = 1200
# numeric layout attributes read off GUI_util and fed into arithmetic / GUI_IO_util.GUI_settings():
# these MUST be real numbers or `max(...)` / `y > x` comparisons crash.
for _attr, _val in (('y_multiplier_integer', 0), ('y_multiplier_integer_add', 0), ('increment', 0),
                    ('GUI_width', 1200), ('GUI_height_brief', 600), ('GUI_height_full', 800),
                    ('GUI_height', 700), ('basic_y_coordinate', 0), ('y_step', 20)):
    setattr(_guiu, _attr, _val)
_guiu.setup_parsers_annotators.return_value = (0, 'Stanza', ['Dependency parser'], 'Stanza', 'English',
                                               '', '', 'utf-8', 0, 4, 90000, 100)
sys.modules['GUI_util'] = _guiu

# reminders_util is stubbed for a side-effect reason, not an import one: its real checkReminder reads
# and REWRITES reminders/reminders.csv, a tracked file. Building 54 GUIs therefore left the repo with a
# permanently modified reminders.csv (pandas' to_csv writes CRLF where the committed file has LF), so
# `git status` was never clean after a smoke run. A test harness must not touch the working tree.
sys.modules['reminders_util'] = MagicMock()

# ---------- stub ENTIRE heavy dependency trees (submodules included) via a meta-path finder ----------
# A flat MagicMock in sys.modules can't satisfy `from nltk.stem.porter import X` or
# `from plotly.subplots import Y` (those need real sub-package resolution). A finder that returns a
# stub module (with a PEP-562 module __getattr__ -> MagicMock) for anything under these roots does.
# NOTE: pandas / numpy are deliberately NOT stubbed -- they're installed, fast (cached), and used
# concretely at import in some GUIs, where a mock would recurse. Let them be real.
import importlib.abc, importlib.machinery
_STUB_ROOTS = {'stanza','spacy','nltk','torch','torchvision','transformers','sentence_transformers',
               'gensim','sklearn','scipy','matplotlib','plotly','seaborn','wordcloud','folium','geopy',
               'pyLDAvis','textstat','langdetect','langid','nrclex','openpyxl','xlrd','xlsxwriter','bs4',
               'requests','networkx','pydotplus','graphviz','PIL','cv2','allennlp','pattern','textblob',
               'vaderSentiment','stanfordcorenlp','pycountry','emoji','tqdm','regex','sqlalchemy',
               'gender_guesser','pyspellchecker','autocorrect','sparqlwrapper','SPARQLWrapper',
               'transformer_srl','wikipedia','newspaper','tweepy','praw','umap','hdbscan','bertopic',
               'spacy_langdetect','spacytextblob','contractions','unidecode','chardet','pdfplumber',
               'docx','fitz','striprtf','pyLDAvis','little_mallet_wrapper','tkcolorpicker','tkinterdnd2',
               'pymupdf','pdf2image','pytesseract','wikipediaapi','geotext','reverse_geocoder'}


class _StubLoader(importlib.abc.Loader):
    def create_module(self, spec):
        m = types.ModuleType(spec.name)
        m.__getattr__ = lambda _name: MagicMock()   # PEP 562: any attribute -> a fresh mock
        m.__path__ = []                              # mark as a package so submodules import
        return m
    def exec_module(self, module):
        pass


class _StubFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name.split('.')[0] in _STUB_ROOTS:
            return importlib.machinery.ModuleSpec(name, _StubLoader(), is_package=True)
        return None


sys.meta_path.insert(0, _StubFinder())

_srcdir, _target = sys.argv[1], sys.argv[2]
sys.path.insert(0, _srcdir)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('_gui_under_test', os.path.join(_srcdir, _target))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('SMOKE_OK')
except SystemExit as e:
    print('SMOKE_OK' if (e.code or 0) == 0 else 'SMOKE_FAIL')
    if (e.code or 0) != 0:
        traceback.print_exc()
except BaseException:
    print('SMOKE_FAIL')
    traceback.print_exc()
for _t in _texts:
    print('WTEXT\t' + _t.replace(chr(9), ' ').replace(chr(10), ' '))
'''


def _smoke_one(target):
    try:
        p = subprocess.run([sys.executable, '-c', _HARNESS, _SRC, target],
                           capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return False, [], '(timed out)'
    ok = 'SMOKE_OK' in p.stdout
    texts = [ln[6:] for ln in p.stdout.splitlines() if ln.startswith('WTEXT\t')]
    err_tail = ''
    if not ok:
        err = (p.stdout + '\n' + p.stderr).strip().splitlines()
        err_tail = '\n      '.join(err[-6:])
    return ok, texts, err_tail


def main():
    gui_files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(_SRC, '*_main.py'))
                       if not any(s in os.path.basename(f) for s in _NOT_GUI))
    print('GUI construction smoke test: %d *_main.py GUIs under %s\n' % (len(gui_files), _SRC))
    crashed, missing, skipped = [], [], []
    for f in gui_files:
        ok, texts, err_tail = _smoke_one(f)
        if not ok:
            if f in KNOWN_SKIP:
                skipped.append(f)
                print('SKIP   %-52s (not smoke-testable under stubs -- verify by launching)' % f)
                continue
            crashed.append(f)
            print('CRASH  %-52s' % f)
            if err_tail:
                print('      ' + err_tail)
            continue
        if f in KNOWN_SKIP:
            print('OK*    %-52s (built now -- consider removing from KNOWN_SKIP)' % f)
        # golden widget-label check (only for curated GUIs that imported OK)
        want = GOLDEN.get(f)
        if want:
            blob = ' \n '.join(texts)
            absent = [w for w in want if w not in blob]
            if absent:
                missing.append((f, absent))
                print('MISSING %-51s golden labels not found: %s' % (f, ', '.join(absent)))
                continue
            print('OK     %-52s (built; %d widgets; golden ok)' % (f, len(texts)))
        else:
            print('OK     %-52s (built; %d widgets)' % (f, len(texts)))

    print('\n%d GUIs: %d ok, %d crashed, %d missing golden, %d skipped (stub-limited).'
          % (len(gui_files), len(gui_files) - len(crashed) - len(missing) - len(skipped),
             len(crashed), len(missing), len(skipped)))
    if crashed:
        print('  CRASHED (real -- fix these): ' + ', '.join(crashed))
    if missing:
        print('  MISSING GOLDEN (a required widget label is gone!): '
              + ', '.join('%s -> %s' % (f, ','.join(a)) for f, a in missing))
    if skipped:
        print('  skipped: ' + ', '.join(skipped))
    # Green ONLY if no real crash and no golden regression. Skips don't fail the run.
    return 1 if (crashed or missing) else 0


if __name__ == '__main__':
    sys.exit(main())
