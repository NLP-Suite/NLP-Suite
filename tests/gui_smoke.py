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
# ---------- fake customtkinter ----------
# customtkinter (CTk migration, GUI_theme_util) can't be imported for real here: its widget classes
# subclass real tkinter.Frame/tkinter.Tk AT IMPORT TIME (e.g. CTkBaseClass(tkinter.Frame, ...)),
# which the fake tkinter's `_rec` function stand-ins can't satisfy (you can't subclass a function),
# and constructing a real CTk widget needs a live Tk root this headless harness deliberately lacks.
#
# It is stubbed HAND-WRITTEN rather than as a MagicMock tree (which is what it was through Phase 1).
# A MagicMock answers every call and every subscript, so it silently absorbs exactly the breakages a
# tk->CTk conversion introduces. All three bugs found converting the first pilot (wordclouds_main)
# passed a MagicMock-stubbed smoke run untouched:
#   * `widget.config(...)`      -- real CTk RAISES AttributeError ("use 'configure' instead").
#   * `widget['state']`         -- real CTk resolves __getitem__ against the underlying tk frame,
#                                  which has no such option -> TclError.
#   * `widget['values'] = [...]` -- tkinter's __setitem__ passes the dict as CTkComboBox.configure's
#                                  first POSITIONAL arg (require_redraw), so it SILENTLY no-ops.
# So the stub below reproduces those three contracts and nothing else it doesn't have to. It also
# records `text=` into _texts like `_rec` does, which keeps GOLDEN label checks working for GUIs once
# their widgets move to GUI_theme_util factories.
def _check_values_are_strings(values):
    # Real CTkOptionMenu/CTkComboBox feed `values=` into customtkinter's DropdownMenu, whose
    # _add_menu_commands() calls value.ljust(...) on every item UNCONDITIONALLY -- a legacy
    # tk.OptionMenu(var, 1, 2, 3) or a float-threshold list (.1, .15, ...) passed straight through
    # crashes with AttributeError the moment the real widget builds. A MagicMock/permissive stub
    # would swallow this silently (found only by importing a real Tk + real CTk root, which this
    # headless harness deliberately avoids), so mirror the crash here too.
    if values is None:
        return
    for v in values:
        if not isinstance(v, str):
            raise TypeError(
                "CTkOptionMenu/CTkComboBox values=%r contains a non-string item (%r) -- CTk's "
                "DropdownMenu calls value.ljust(...) on every item and crashes on int/float. "
                "Coerce with values=[str(v) for v in ...] (or pass through set_values/"
                "create_option_menu/create_combobox, which now str()-coerce automatically)."
                % (values, v)
            )


class _CTkWidget(object):
    # The parameters are spelled out (rather than a bare **k) because GUI_theme_util.translate_kwargs
    # filters translated kwargs against `inspect.signature(cls.__init__)`: a `(*a, **k)` stub reports
    # an EMPTY accepted-parameter set, so every kwarg -- `text` included -- would be dropped and the
    # GOLDEN label checks would silently record nothing. This list is deliberately permissive; the
    # exact per-class kwarg filtering is covered against the REAL CTk classes by the pytest suite.
    def __init__(self, master=None, text=None, width=None, height=None, state=None, command=None,
                 variable=None, textvariable=None, values=None, font=None, image=None, anchor=None,
                 corner_radius=None, border_width=None, placeholder_text=None, fg_color=None,
                 hover_color=None, text_color=None, button_color=None, button_hover_color=None,
                 checkbox_width=None, checkbox_height=None, onvalue=None, offvalue=None,
                 from_=None, to=None, orientation=None, number_of_steps=None, **k):
        self._opts = dict(k)
        self._opts.update({key: val for key, val in (
            ('text', text), ('state', state), ('values', values), ('width', width),
            ('height', height), ('variable', variable), ('textvariable', textvariable),
        ) if val is not None})
        if text is not None:
            try: _texts.append(str(text))
            except Exception: pass
        _check_values_are_strings(values)

    def config(self, *a, **k):
        # Mirrors customtkinter.CTkBaseClass.config, which exists only to raise.
        raise AttributeError("'config' is not implemented for CTk widgets. "
                             "For consistency, always use 'configure' instead.")

    def configure(self, require_redraw=False, **k):
        if not isinstance(require_redraw, bool):
            # The `widget['x'] = y` silent no-op: tkinter's __setitem__ lands the option dict here.
            raise TypeError("CTk configure() got a non-bool as require_redraw (%r) -- this is the "
                            "`widget[key] = value` idiom, which silently no-ops on CTk widgets. "
                            "Use widget.configure(key=value) or GUI_theme_util.set_values()."
                            % (require_redraw,))
        t = k.get('text')
        if t is not None:
            try: _texts.append(str(t))
            except Exception: pass
        _check_values_are_strings(k.get('values'))
        self._opts.update(k)

    def cget(self, key):
        return self._opts.get(key, '')

    def __getitem__(self, key):
        raise TypeError("CTk widgets do not support widget[%r] lookup (it resolves against the "
                        "underlying tk frame and raises TclError). Use widget.cget(%r)." % (key, key))

    def __setitem__(self, key, value):
        raise TypeError("CTk widgets do not support widget[%r] = ... (it silently no-ops). "
                        "Use widget.configure(%s=...) or GUI_theme_util.set_values()." % (key, key))

    def __getattr__(self, _n):
        return MagicMock()

_ctk = types.ModuleType('customtkinter')
for _n in ('CTk','CTkToplevel','CTkFrame','CTkScrollableFrame','CTkLabel','CTkButton','CTkEntry',
           'CTkCheckBox','CTkOptionMenu','CTkComboBox','CTkSlider','CTkSwitch','CTkTextbox',
           'CTkRadioButton','CTkProgressBar','CTkSegmentedButton','CTkTabview','CTkImage','CTkFont',
           'CTkCanvas','CTkScrollbar'):
    setattr(_ctk, _n, type(_n, (_CTkWidget,), {}))
# create_textbox() reads this real CTkTextbox class attribute directly (see its docstring: `state`,
# `wrap`, etc. are never named __init__ params, only forwarded through it) -- without it here the
# stub would silently re-introduce the very bug that gap fix exists to catch.
_ctk.CTkTextbox._valid_tk_text_attributes = {
    "autoseparators", "cursor", "exportselection", "insertborderwidth", "insertofftime",
    "insertontime", "insertwidth", "maxundo", "padx", "pady", "selectborderwidth", "spacing1",
    "spacing2", "spacing3", "state", "tabs", "takefocus", "undo", "wrap",
    "xscrollcommand", "yscrollcommand",
}
for _fn in ('set_appearance_mode','set_default_color_theme','set_widget_scaling',
            'deactivate_automatic_dpi_awareness','get_appearance_mode'):
    setattr(_ctk, _fn, lambda *a, **k: None)
_ctk.__version__ = '6.0.0'
sys.modules['customtkinter'] = _ctk


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
    # A mid-import sys.exit(0) is NOT a pass: the module stopped before building its widgets, so the
    # run proves nothing about the GUI. Reporting it as OK is how shape_of_stories/semantic_analysis
    # sat at "OK (4 widgets)" -- those 4 were a timed_alert popup -- while the GUI body never ran.
    # (Stanza_util sys.exit()s at import when stanza's resources.json is missing, which is an env
    # condition, not a code defect -- hence its own status rather than a crash.)
    if (e.code or 0) == 0:
        print('SMOKE_EXIT')
        traceback.print_exc()
    else:
        print('SMOKE_FAIL')
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
    exited = 'SMOKE_EXIT' in p.stdout
    texts = [ln[6:] for ln in p.stdout.splitlines() if ln.startswith('WTEXT\t')]
    err_tail = ''
    if not ok:
        err = (p.stdout + '\n' + p.stderr).strip().splitlines()
        err_tail = '\n      '.join(err[-6:])
    return ok, exited, texts, err_tail


def main():
    gui_files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(_SRC, '*_main.py'))
                       if not any(s in os.path.basename(f) for s in _NOT_GUI))
    print('GUI construction smoke test: %d *_main.py GUIs under %s\n' % (len(gui_files), _SRC))
    crashed, missing, skipped, uncovered = [], [], [], []
    for f in gui_files:
        ok, exited, texts, err_tail = _smoke_one(f)
        if exited:
            # sys.exit(0) partway through the import: the GUI body never ran, so this run verified
            # nothing. Not a crash (usually a missing model/resource in this env), but not a pass.
            uncovered.append(f)
            print('UNCOV  %-52s (exited during import -- GUI body never built; verify by launching)' % f)
            if err_tail:
                print('      ' + err_tail)
            continue
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

    print('\n%d GUIs: %d ok, %d crashed, %d missing golden, %d uncovered, %d skipped (stub-limited).'
          % (len(gui_files),
             len(gui_files) - len(crashed) - len(missing) - len(skipped) - len(uncovered),
             len(crashed), len(missing), len(uncovered), len(skipped)))
    if crashed:
        print('  CRASHED (real -- fix these): ' + ', '.join(crashed))
    if missing:
        print('  MISSING GOLDEN (a required widget label is gone!): '
              + ', '.join('%s -> %s' % (f, ','.join(a)) for f, a in missing))
    if uncovered:
        print('  UNCOVERED (imported nothing here -- verify by launching): ' + ', '.join(uncovered))
    if skipped:
        print('  skipped: ' + ', '.join(skipped))
    # Green ONLY if no real crash and no golden regression. Skips don't fail the run.
    return 1 if (crashed or missing) else 0


if __name__ == '__main__':
    sys.exit(main())
