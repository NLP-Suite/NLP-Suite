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
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Project root ────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath('.')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

# ── Local hidden imports ────────────────────────────────────────────────────
# All .py files in src/ that might be imported dynamically at runtime.
# PyInstaller can't see imports inside subprocess.call('python script.py')
# or inside string-based imports.

_local_modules = [
    'BERT_util',
    'charts_Excel_main', 'charts_Excel_util', 'charts_matplotlib_seaborn_util',
    'charts_Plotly_util', 'charts_util',
    'config_util',
    'CoNLL_adjective_analysis_util', 'CoNLL_adverb_analysis_util',
    'CoNLL_clause_analysis_util', 'CoNLL_function_words_analysis_util',
    'CoNLL_k_sentences_util', 'CoNLL_noun_analysis_util',
    'CoNLL_ratio_analysis_util', 'CoNLL_table_analyzer_main',
    'CoNLL_table_search_util', 'CoNLL_util', 'CoNLL_verb_analysis_util',
    'constants_util',
    'coreference_main',
    'data_manipulation_main', 'data_manipulation_util',
    'data_visualization_1_main', 'data_visualization_2_main',
    'DB_PCACE_data_analysis_main', 'DB_PCACE_data_analysis_util',
    'DB_PCACE_data_validation_main',
    'DB_SQL_main', 'DB_SQL_util',
    'file_checker_converter_cleaner_main', 'file_checker_pre_processing_pipeline_main',
    'file_checker_util', 'file_classifier_date_util', 'file_classifier_main',
    'file_classifier_NER_util', 'file_cleaner_util', 'file_converter_util',
    'file_filename_util', 'file_find_non_related_documents_util',
    'file_handler_ALL_main', 'file_manager_main',
    'file_matcher_main', 'file_matcher_util',
    'file_merger_main', 'file_merger_util',
    'file_search_ALL_main', 'file_search_byWord_main', 'file_search_byWord_util',
    'file_spell_checker_main', 'file_spell_checker_util',
    'file_splitter_ByBME_K_sentences_util', 'file_splitter_ByDocumentID_csv_util',
    'file_splitter_ByKeyword_conll_util', 'file_splitter_ByKeyword_txt_util',
    'file_splitter_ByLength_util', 'file_splitter_ByNumber_util',
    'file_splitter_ByString_util', 'file_splitter_ByTOC_util',
    'file_splitter_main', 'file_splitter_merged_txt_util',
    'file_summary_checker_util',
    'Gephi_util',
    'GIS_distance_main', 'GIS_distance_util',
    'GIS_file_check_util', 'GIS_folium_map_util', 'GIS_folium_util',
    'GIS_geocode_util', 'GIS_Google_Earth_main', 'GIS_Google_Maps_util',
    'GIS_Google_pin_util', 'GIS_KML_util', 'GIS_location_util',
    'GIS_main', 'GIS_pipeline_util',
    'GUI_IO_util', 'GUI_util',
    'hashfile',
    'html_annotator_dictionary_util', 'html_annotator_extractor_util',
    'html_annotator_gender_dictionary_util', 'html_annotator_gender_main',
    'html_annotator_main',
    'IO_csv_util', 'IO_files_util', 'IO_internet_util',
    'IO_libraries_util', 'IO_string_util', 'IO_user_interface_util',
    'knowledge_graphs_DBpedia_util', 'knowledge_graphs_DBpedia_YAGO_main',
    'knowledge_graphs_WordNet_main', 'knowledge_graphs_WordNet_util',
    'knowledge_graphs_YAGO_util',
    'lib_util', 'license_GUI',
    'narrative_analysis_ALL_main',
    'NER_main',
    'NGrams_CoOccurrences_main', 'NGrams_CoOccurrences_util', 'NGrams_util',
    'NLP_menu_main', 'NLP_setup_download_jars',
    'NLP_setup_external_software_main', 'NLP_setup_IO_main',
    'NLP_setup_package_language_main', 'NLP_setup_shortcut_add',
    'NLP_setup_shortcut_remove', 'NLP_setup_update_util', 'run_script_util',
    'NLP_welcome_main',
    'nominalization_main', 'nominalization_util',
    'parsers_annotators_main', 'parsers_annotators_visualization_util',
    'reminders_util',
    'sample_corpus_main', 'sample_corpus_util',
    'SENNA_util',
    'sentence_analysis_main', 'sentence_analysis_util',
    'sentence_complexity_node_util',
    'sentiment_analysis_ANEW_util', 'sentiment_analysis_hedonometer_util',
    'sentiment_analysis_main', 'sentiment_analysis_SentiWordNet_util',
    'sentiment_analysis_VADER_util',
    'sentiments_emotions_ALL_main',
    'shape_of_stories_clustering_util', 'shape_of_stories_main',
    'shape_of_stories_vectorizer_util', 'shape_of_stories_visualization_util',
    'social_science_research_main',
    'spaCy_util',
    'Stanford_CoreNLP_clause_util', 'Stanford_CoreNLP_coreference_util',
    'Stanford_CoreNLP_port_util', 'Stanford_CoreNLP_SVO_enhanced_dependencies_util',
    'Stanford_CoreNLP_tags_util', 'Stanford_CoreNLP_util',
    'Stanza_functions_util', 'Stanza_util',
    'statistics_csv_main', 'statistics_csv_util',
    'statistics_txt_main', 'statistics_txt_util',
    'string_util',
    'style_analysis_abstract_concreteness_analysis_util',
    'style_analysis_iconicity_analysis_util', 'style_analysis_main',
    'SVO_main', 'SVO_util',
    'TIPS_util',
    'topic_modeling_bert_util', 'topic_modeling_gensim_util',
    'topic_modeling_main', 'topic_modeling_mallet_util',
    'tree', 'videos_util',
    'whats_in_your_corpus_main',
    'word2vec_distances_util', 'word2vec_Gensim_util',
    'word2vec_main', 'word2vec_tsne_plot_util',
    'wordclouds_main', 'wordclouds_util',
    'WSI_classes', 'WSI_keyterms', 'WSI_util', 'WSI_viz',
]

# ── Third-party hidden imports ──────────────────────────────────────────────
# Packages that PyInstaller may not detect because they are imported
# conditionally or inside try/except blocks in NLP Suite code.

_third_party_hiddenimports = [
    # Core data science
    'pandas', 'numpy', 'scipy', 'sklearn', 'sklearn.feature_extraction.text',
    'sklearn.metrics.pairwise', 'sklearn.manifold', 'sklearn.cluster',
    'sklearn.decomposition', 'sklearn.preprocessing',
    'openpyxl', 'openpyxl.utils', 'openpyxl.styles',
    'xlrd', 'sqlite3',
    # NLP
    'stanza', 'stanza.pipeline', 'stanza.models',
    'spacy', 'nltk', 'nltk.corpus', 'nltk.tokenize',
    'gensim', 'gensim.models', 'gensim.corpora',
    'textblob', 'textstat', 'langdetect', 'langid',
    'autocorrect', 'spellchecker', 'fuzzywuzzy',
    'transformers', 'sentence_transformers',
    # Visualization
    'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends',
    'matplotlib.backends.backend_tkagg',
    'plotly', 'plotly.express', 'plotly.graph_objects', 'plotly.subplots',
    'seaborn', 'wordcloud', 'mpld3',
    # GIS
    'folium', 'geopy', 'geopy.geocoders', 'simplekml',
    'shapely', 'geopandas',
    # Web / parsing
    'requests', 'bs4', 'lxml', 'lxml.etree',
    'pdfminer', 'pdfminer.high_level',
    'docx', 'striprtf',
    # Stanford CoreNLP client
    'pycorenlp', 'stanfordcorenlp',
    # Deep learning (optional — large)
    'torch', 'tensorflow', 'tensorflow_hub',
    # tkinter extras
    'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
    'tkinter.scrolledtext',
    # Other
    'PIL', 'PIL.Image', 'PIL.ImageTk',
    'chardet', 'tqdm', 'psutil', 'json', 'csv', 'pickle',
    'collections', 'functools', 'itertools', 'statistics',
    'SPARQLWrapper',
]

# Collect stanza and spacy data files (language models etc.)
# NOTE: nltk data files are downloaded at runtime, not bundled.
try:
    _stanza_datas = collect_data_files('stanza', include_py_files=True)
except Exception:
    _stanza_datas = []
try:
    _spacy_datas = collect_data_files('spacy', include_py_files=True)
except Exception:
    _spacy_datas = []
_nltk_datas = []  # nltk downloads data at runtime

# ── Data files to bundle ────────────────────────────────────────────────────
# These are copied alongside the executable so the app can find them at runtime.
# Format: (source_path, destination_folder_in_bundle)
#
# IMPORTANT: PyInstaller places data files inside _internal/ by default.
# The NLP Suite code resolves paths via __file__ → parent → NLPPath, which
# maps to the exe root folder (dist/NLP_Suite/), NOT _internal/.
# Therefore data directories (src, lib, config, TIPS, reminders) must be
# at the exe root level.
#
# After building, run the post-build script (or the CI workflow) to copy
# data files to the correct location. See post_build_fixup() below.

def _collect_tree(src_dir, dest_prefix):
    """Recursively collect all files under src_dir into dest_prefix."""
    result = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        if '__pycache__' in dirpath or '.git' in dirpath:
            continue
        for f in filenames:
            src_file = os.path.join(dirpath, f)
            rel_dir = os.path.relpath(dirpath, os.path.dirname(src_dir))
            result.append((src_file, rel_dir))
    return result

_project_datas = []

# All src/*.py files (needed because GUIs check for .py files and some launch via subprocess)
for f in os.listdir(SRC_DIR):
    if f.endswith('.py') and not f.startswith('_'):
        _project_datas.append((os.path.join(SRC_DIR, f), 'src'))

# Library data (recursive)
_lib_dir = os.path.join(PROJECT_ROOT, 'lib')
if os.path.isdir(_lib_dir):
    _project_datas += _collect_tree(_lib_dir, 'lib')

# Config files
_config_dir = os.path.join(PROJECT_ROOT, 'config')
if os.path.isdir(_config_dir):
    for f in os.listdir(_config_dir):
        if f.endswith('.csv'):
            _project_datas.append((os.path.join(_config_dir, f), 'config'))

# TIPS (PDF help files)
_tips_dir = os.path.join(PROJECT_ROOT, 'TIPS')
if os.path.isdir(_tips_dir):
    for f in os.listdir(_tips_dir):
        if f.endswith('.pdf'):
            _project_datas.append((os.path.join(_tips_dir, f), 'TIPS'))

# Reminders
_reminders_dir = os.path.join(PROJECT_ROOT, 'reminders')
if os.path.isdir(_reminders_dir):
    _project_datas += _collect_tree(_reminders_dir, 'reminders')

# ── Analysis ────────────────────────────────────────────────────────────────

a = Analysis(
    [os.path.join(SRC_DIR, 'NLP_menu_main.py')],
    pathex=[SRC_DIR],
    binaries=[],
    datas=_project_datas + _stanza_datas + _spacy_datas + _nltk_datas,
    hiddenimports=_local_modules + _third_party_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional packages to reduce size on first build.
        # Uncomment any line below to re-include if needed.
        'tensorflow', 'tensorflow_hub', 'tensorflow_intel',
        'torch',
        'bertopic',
        'pyLDAvis',
        'gmaps',
        'nltk',      # hook incompatible with Python 3.8; nltk downloads data at runtime
        'spacy_langdetect', 'contextualSpellCheck',  # optional, may not be installed
        'pygit2',    # not needed in bundled app; auto-update disabled when frozen
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
    icon=None,      # TODO: add NLP Suite icon path here
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
