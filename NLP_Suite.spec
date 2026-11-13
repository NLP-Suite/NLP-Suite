# -*- mode: python ; coding: utf-8 -*-
# NLP Suite PyInstaller spec file
# Builds a one-folder distribution for Windows (and Mac via GitHub Actions)
#
# Usage:
#   cd C:\Users\rfranzo\Desktop\NLP-Suite
#   python -m PyInstaller NLP_Suite.spec
#
# Output: dist/NLP_Suite/NLP_Suite.exe

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# ── Project root ────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath('.')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

# ── App / Dock icon ─────────────────────────────────────────────────────────
# PyInstaller wants a .icns on macOS and a .ico on Windows. Both are square
# renderings of the NLP Suite wordmark (built from lib/images/logo.png).
if sys.platform == 'darwin':
    APP_ICON = os.path.join(PROJECT_ROOT, 'lib', 'images', 'NLP_Suite.icns')
else:
    APP_ICON = os.path.join(PROJECT_ROOT, 'lib', 'images', 'NLP_Suite.ico')

# ── What the frozen executable runs ─────────────────────────────────────────
# The PyInstaller executable runs ONLY the menu (NLP_menu_main) and what it does in its own process: the setup
# panel, the language advisor, TIPS, the self-updater. Every tool is started by run_script_util with the
# bundled portable Python (python-env/) on the loose src/*.py at the app root, so the tools' libraries live in
# python-env, not here. PyInstaller follows the menu's imports by itself (including imports inside functions);
# it is not given the ~180 tool modules, nor the scientific stack, as hidden imports any more. Until 1.6.43
# they were, and _internal/ carried a second, unused copy of pandas/scipy/transformers/spaCy/stanza...
# (docs/future-work.md 2.1).

_hiddenimports = [
    # imported inside functions or conditionally by the menu's modules
    'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'tkinter.scrolledtext',
    'PIL', 'PIL.Image', 'PIL.ImageTk',
    # NLP_menu_main's setup panel and tool browser; darkdetect is CustomTkinter's appearance-mode
    # dependency, imported conditionally inside it
    'customtkinter', 'darkdetect',
    # the self-updater and the release check (NLP_setup_self_update_util, GUI_util)
    'requests', 'psutil',
]

# CustomTkinter loads its color themes and fonts from its package directory at runtime
try:
    _ctk_datas = collect_data_files('customtkinter')
except Exception:
    _ctk_datas = []

# ── Data files ──────────────────────────────────────────────────────────────
# None from the project. The code resolves lib/, config/, TIPS/, reminders/ and src/ from the folder of the
# executable (GUI_IO_util.NLPPath), and the build copies them there: build-installers.yml's "Copy data
# directories to dist" step (with config/ seeded from lib/config_defaults), or post_build_fixup.py for a local
# build. Until 1.6.43 the spec also put them in _internal/, a second copy (about 150 MB) that nothing read, and
# on a local build that copy included the developer's own config/ (API keys).

# ── Analysis ────────────────────────────────────────────────────────────────

a = Analysis(
    [os.path.join(SRC_DIR, 'NLP_menu_main.py')],
    pathex=[SRC_DIR],
    binaries=[],
    datas=_ctk_datas,
    hiddenimports=_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Libraries only the TOOLS use (they run on python-env). The menu's modules mention them inside
        # functions that the menu process never calls, so PyInstaller would otherwise pack them.
        # NOT excluded, because the menu's language advisor imports spaCy_util in-process: spacy, numpy,
        # pandas, scipy, matplotlib, plotly, openpyxl.
        'tensorflow', 'tensorflow_hub', 'tensorflow_intel',
        'torch', 'torchvision', 'torchaudio',
        'transformers', 'tokenizers', 'sentence_transformers', 'huggingface_hub', 'hf_xet', 'safetensors',
        'stanza',    # needs torch, so it could not load in the menu even before 1.6.43
        'sklearn', 'gensim', 'bertopic', 'umap', 'hdbscan', 'pyLDAvis', 'fastcoref', 'summarizer',
        'nltk',      # nltk downloads its data at runtime, in the tools
        'textblob', 'textstat', 'pyphen', 'nrclex', 'langdetect', 'langid', 'spacy_langdetect', 'spacytextblob',
        'autocorrect', 'spellchecker', 'fuzzywuzzy', 'wn', 'emoji',
        'seaborn', 'wordcloud', 'folium', 'geopy', 'simplekml', 'kaleido',
        'pdfminer', 'pypdf', 'docx', 'striprtf', 'pycorenlp', 'stanfordcorenlp',
        'IPython', 'jedi', 'parso', 'ipywidgets', 'h5py',
        'gmaps', 'contextualSpellCheck', 'pygit2',
        # SRL (transformer_srl/allennlp) runs ONLY in a separate Python 3.8 subprocess env, never in
        # this bundle. src/SRL_worker.py ships as a data script and imports them lazily at run
        # time, so it never needs to import here. Exclude them so the legacy stack is never pulled in.
        'transformer_srl', 'allennlp',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NLP_Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True so users can see error messages; set False for release
    icon=APP_ICON,  # NLP Suite Dock/taskbar icon (.icns on macOS, .ico on Windows)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NLP_Suite',
)
