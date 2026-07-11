# corpus_profiler_main.py
#
# Corpus Profiler — run a battery of analyses with sensible DEFAULTS and produce a single
# navigable HTML report (NLP_corpus_profile.html), the only file auto-opened. Successor to
# the earlier corpus-overview tool. See docs/corpus_profiler_spec.md.
#
# Phase 0: three wired category rows (Counts, Vocabulary, Entities), each a checkbox + dropdown
# ('*' = run all in that group). The heavy lifting + the HTML report live in corpus_profiler_util.
# GUI placement is deliberately rough — refine the x/y coordinates to taste.

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "corpus profiler", ['os', 'tkinter']) == False:
    sys.exit(1)

import os
import time
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import IO_user_interface_util
import IO_files_util
import config_util
import corpus_profiler_util


def run():
    # widgets read at RUN time
    inputFilename = GUI_util.inputFilename.get()
    inputDir = GUI_util.input_main_dir_path.get()
    outputDir = GUI_util.output_dir_path.get()
    chartPackage = GUI_util.charts_package_options_widget.get()
    dataTransformation = GUI_util.data_transformation_options_widget.get()
    config_filename = GUI_util.config_filename_selected_config.get()

    if not (inputDir or inputFilename):
        mb.showwarning('Input missing',
                       'Please select an input corpus — a directory of txt files (recommended) or a single txt file.')
        return

    # configured NLP package / language / memory options
    error, package, parsers, package_basics, language, package_display_area_value, encoding_var, \
        export_json_var, memory_var, document_length_var, limit_sentence_length_var = \
        config_util.read_NLP_package_language_config()

    # everything goes under a single corpus_profile subdirectory. silent=False so, if a prior profile
    # folder exists, the user is asked before it is replaced (re-running re-does every ticked analysis,
    # which can take a very long time on a large corpus). Under NLP_SILENT the confirm auto-proceeds.
    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                       label='corpus_profile', silent=False)
    if outputDir == '':   # user declined to replace the existing profile folder
        return

    # expand a ticked group's dropdown value into concrete analysis ids
    def expand(category, menu_value):
        ids = corpus_profiler_util.analyses_in_category(category)
        if menu_value == '*' or str(menu_value).strip() == '':
            return ids
        return [aid for aid in ids if corpus_profiler_util.REGISTRY[aid]['label'] == menu_value]

    # GENERIC over the taxonomy: a category participates if its <cat>_var checkbox exists and is ticked.
    # Adding a new category = add its widgets + registry entries; run() needs no change.
    selected = []
    any_on = False
    for cat in corpus_profiler_util.CATEGORY_ORDER:
        var = globals().get(cat + '_var')
        if var is None or not var.get():
            continue
        any_on = True
        menu_var = globals().get(cat + '_menu_var')
        selected += expand(cat, menu_var.get() if menu_var is not None else '*')

    if not any_on:
        mb.showwarning('Nothing selected', 'Please tick at least one analysis group.')
        return
    if not selected:
        mb.showwarning('Nothing to run', 'The selected dropdown option matched no analysis.')
        return

    # up-front runtime heads-up: the CoreNLP-backed categories run Java over the whole corpus and can
    # take a very long time. Counts and Vocabulary are fast. Let the user opt into the long run knowingly.
    heavy = [aid for aid in selected
             if corpus_profiler_util.REGISTRY[aid]['category'] in ('entities', 'semantics', 'narrative')
             and corpus_profiler_util.REGISTRY[aid]['kind'] == 'batch']
    if heavy:
        if not mb.askyesno('This may take a while',
                           "The Entities and/or Semantics analyses run Stanford CoreNLP (Java) over your ENTIRE "
                           "corpus. On a large corpus this can take a long time — potentially hours.\n\n"
                           "Counts and Vocabulary are fast by comparison.\n\nContinue with the full run?",
                           default='yes'):  # silent/unattended mode proceeds
            return

    # shared context passed to every runner. openOutputFiles is FORCED off in the runners --
    # only the profile report opens at the end.
    ctx = dict(window=GUI_util.window, inputFilename=inputFilename, inputDir=inputDir, outputDir=outputDir,
               config_filename=config_filename, chartPackage=chartPackage, dataTransformation=dataTransformation,
               language=language, export_json_var=export_json_var, memory_var=memory_var,
               document_length_var=document_length_var, limit_sentence_length_var=limit_sentence_length_var)

    IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Corpus Profiler',
                                       'Running ' + str(len(selected)) + ' analyses with defaults.\n\n'
                                       'At the end a paper-style summary opens (with an HTML report beside it); '
                                       'every individual output file is linked from them.')

    results = corpus_profiler_util.run_profile(ctx, selected)
    header = corpus_profiler_util.corpus_header_stats(inputFilename, inputDir)

    if inputDir:
        corpus_name = os.path.basename(inputDir.rstrip('/\\')) or 'corpus'
    else:
        corpus_name = os.path.splitext(os.path.basename(inputFilename))[0]

    run_config = dict(
        subtitle='package: ' + str(package) + '  ·  language: ' + str(language) + '  ·  ' + time.strftime('%Y-%m-%d'),
        footer='NLP Suite — Corpus Profiler.  ' + str(len(results)) +
               ' analyses run.  Per-file detail lives in the category subfolders.')

    # build both: the navigable index (companion) and the paper-style summary (opened below)
    corpus_profiler_util.build_report(outputDir, corpus_name, results, header, run_config)
    summary = corpus_profiler_util.build_paper_summary(outputDir, corpus_name, results, header, run_config)

    # Open the paper-style SUMMARY (the headline read; it links to the full navigable report and
    # the report links back). Open the single HTML file DIRECTLY -- do NOT route through
    # OpenOutputFiles: it scans the whole output dir and, with 100+ files, shows a "too many files"
    # summary dialog instead of opening the page.
    try:
        IO_files_util.openFile(GUI_util.window, summary)
    except Exception:
        import webbrowser
        webbrowser.open('file:///' + summary.replace('\\', '/'))


GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________

IO_setup_display_brief = True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(
    IO_setup_display_brief,
    GUI_width=GUI_IO_util.get_GUI_width(3),
    GUI_height_brief=600,
    GUI_height_full=640,
    y_multiplier_integer=GUI_util.y_multiplier_integer,
    y_multiplier_integer_add=1,
    increment=1)

GUI_label = 'Corpus Profiler — what\'s in your corpus? (run a battery of analyses; get an HTML report and a paper-style summary)'
config_filename = 'NLP_default_IO_config.csv'
head, scriptName = os.path.split(os.path.basename(__file__))

# input file = 2 (txt), input dir, no secondary dir, output dir
config_input_output_numeric_options = [2, 1, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

# --- category rows: checkbox + dropdown ------------------------------------------------------
counts_var = tk.IntVar()
counts_menu_var = tk.StringVar()
vocabulary_var = tk.IntVar()
vocabulary_menu_var = tk.StringVar()
entities_var = tk.IntVar()
entities_menu_var = tk.StringVar()
spatial_var = tk.IntVar()
spatial_menu_var = tk.StringVar()
syntax_var = tk.IntVar()
syntax_menu_var = tk.StringVar()
semantics_var = tk.IntVar()
semantics_menu_var = tk.StringVar()
topics_var = tk.IntVar()
topics_menu_var = tk.StringVar()
narrative_var = tk.IntVar()
narrative_menu_var = tk.StringVar()
sentiment_var = tk.IntVar()
sentiment_menu_var = tk.StringVar()

_dropdown_x = GUI_IO_util.open_setup_x_coordinate  # rough; nudge to taste

# 1. Counts & measures
counts_var.set(1)
counts_checkbox = tk.Checkbutton(window, text='How big / how varied?  (Counts & measures)',
                                 variable=counts_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, counts_checkbox, True)
counts_menu_var.set('*')
counts_menu = tk.OptionMenu(window, counts_menu_var, '*',
                            'Statistics (sentences, words, syllables)',
                            'N-grams',
                            'Sentence length',
                            'Line length')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, counts_menu, False)

# 2. Vocabulary
vocabulary_var.set(1)
vocabulary_checkbox = tk.Checkbutton(window, text="What's the vocabulary like?  (Vocabulary)",
                                     variable=vocabulary_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, vocabulary_checkbox, True)
vocabulary_menu_var.set('*')
vocabulary_menu = tk.OptionMenu(window, vocabulary_menu_var, '*',
                                "Vocabulary richness (word type/token ratio or Yule's K)",
                                'Lexical diversity (TTR, MTLD, vocd-D)',
                                "Word frequency distribution (Zipf's Law)",
                                'TF-IDF (most distinctive words per document)',
                                'Hapax legomena (once-occurring words)',
                                'Unusual words (via NLTK)',
                                'Abstract / concrete vocabulary',
                                'Iconic vocabulary',
                                'Words with capital initial (proper nouns)',
                                'Language detection')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, vocabulary_menu, False)

# 3. Entities (English + Stanford CoreNLP)
entities_var.set(1)
entities_checkbox = tk.Checkbutton(window, text='Who, what, where, when  (Entities, via CoreNLP)',
                                   variable=entities_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, entities_checkbox, True)
entities_menu_var.set('*')
entities_menu = tk.OptionMenu(window, entities_menu_var, '*',
                              'People, organizations, locations, gender, dates, dialogue (CoreNLP)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, entities_menu, False)

# 3b. Spatial — geocodable & symbolic space (network-heavy: pointers to the GIS / Symbolic Space GUIs)
spatial_var.set(1)
spatial_checkbox = tk.Checkbutton(window, text='Where does it all happen?  (geocodable and symbolic space)',
                                  variable=spatial_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, spatial_checkbox, True)
spatial_menu_var.set('*')
spatial_menu = tk.OptionMenu(window, spatial_menu_var, '*',
                             'Geocodable space — geocode & map corpus locations  (opens GIS GUI)',
                             'Symbolic space — narrative / gendered space typology  (opens Symbolic Space GUI)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, spatial_menu, False)

# 4. Grammar & structure (Syntax) — batch parse + CoNLL analyses live in the analyzer GUI
syntax_var.set(1)
syntax_checkbox = tk.Checkbutton(window, text='Grammar & structure  (Syntax)',
                                 variable=syntax_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, syntax_checkbox, True)
syntax_menu_var.set('*')
syntax_menu = tk.OptionMenu(window, syntax_menu_var, '*',
                            'POS · dependency · clause · N/V/Adj/Adv · function words · complexity · readability')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, syntax_menu, False)

# 5. What do the words mean? (Semantics)
semantics_var.set(1)
semantics_checkbox = tk.Checkbutton(window, text='What do the words mean?  (Semantics)',
                                    variable=semantics_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, semantics_checkbox, True)
semantics_menu_var.set('*')
semantics_menu = tk.OptionMenu(window, semantics_menu_var, '*',
                               'Noun & verb classes (WordNet top synsets)',
                               'WSD · word embeddings · semantic similarity · nominalization  (opens Semantic Analysis GUI)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, semantics_menu, False)

# 6. What is it about? (Topics)
topics_var.set(1)
topics_checkbox = tk.Checkbutton(window, text='What is it about?  (Topics)',
                                 variable=topics_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, topics_checkbox, True)
topics_menu_var.set('*')
topics_menu = tk.OptionMenu(window, topics_menu_var, '*',
                            'Topic modeling (BERT / Gensim / MALLET)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, topics_menu, False)

# 7. Who did what to whom? (Narrative)
narrative_var.set(1)
narrative_checkbox = tk.Checkbutton(window, text='Who did what to whom?  (Narrative)',
                                    variable=narrative_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, narrative_checkbox, True)
narrative_menu_var.set('*')
narrative_menu = tk.OptionMenu(window, narrative_menu_var, '*',
                               'SVO (Subject-Verb-Object)',
                               'SRL (Semantic Role Labeling)',
                               'Coreference · dialogue · 5 Ws  (opens SVO GUI)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, narrative_menu, False)

# 8. How does it feel? (Sentiment)
sentiment_var.set(1)
sentiment_checkbox = tk.Checkbutton(window, text='How does it feel?  (Sentiment)',
                                    variable=sentiment_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, sentiment_checkbox, True)
sentiment_menu_var.set('*')
sentiment_menu = tk.OptionMenu(window, sentiment_menu_var, '*',
                               'Sentiment (Stanza)',
                               'BERT · spaCy · VADER · NRC · SentiWordNet  (opens Sentiment GUI)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, sentiment_menu, False)

# --- help buttons (one per row, in order) ----------------------------------------------------
videos_lookup = {'No videos available': ''}
videos_options = 'No videos available'
TIPS_lookup = {'Text encoding (utf-8)': 'TIPS_NLP_Text encoding (utf-8).pdf',
               'Statistical measures': 'TIPS_NLP_Statistical measures.pdf',
               'Style analysis': 'TIPS_NLP_Style analysis.pdf',
               'CoreNLP NER (Named Entity Recognition)': 'TIPS_NLP_NER tags across packages.pdf'}
TIPS_options = ('Text encoding (utf-8)', 'Statistical measures', 'Style analysis',
                'CoreNLP NER (Named Entity Recognition)')


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                             "NLP Suite Help", GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "COUNTS & MEASURES — how big and how varied is the corpus. Statistics (sentences/words/syllables), "
        "n-grams, sentence & line length. Select '*' to run all, or pick one. Runs with defaults.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "VOCABULARY — a SNAPSHOT of the corpus's lexical character: vocabulary richness (TTR / Yule's K), lexical "
        "diversity (MTLD / vocd-D), word frequency (Zipf), TF-IDF distinctive words, hapax legomena, unusual words "
        "(NLTK), abstract/concrete, iconic vocabulary, proper nouns, language detection. Select '*' to run all; each "
        "runs with defaults.\n\nThis is a curated subset. For the FULL set of ~20 vocabulary & style options "
        "(short/vowel words, punctuation-as-pathos, objectivity/subjectivity, repetition, unigram variants, and more), "
        "open the dedicated STYLE ANALYSIS GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "ENTITIES — who, what, where, when. A single Stanford CoreNLP pass extracts people & organizations, "
        "locations, gender, dates & time, and dialogue/quotes. ENGLISH + Stanford CoreNLP only — because gender, "
        "dialogue/quotes and normalized dates are available ONLY via CoreNLP, the whole pass uses it (NER for "
        "people/organizations/locations is also available via Stanza/spaCy in the dedicated NER GUI).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "WHERE DOES IT ALL HAPPEN? — the space of the corpus, in two senses. GEOCODABLE space: the place names your "
        "text mentions (from NER) can be geocoded and mapped (Google Earth / folium / distances). SYMBOLIC space: the "
        "non-geocodable, culturally-coded space of a narrative — kitchen vs. field, inside vs. outside, women's vs. "
        "men's space — analysed by typology and cross-tabulated with gender. Both are network-heavy or interactive, so "
        "this section OPENS the GIS and Symbolic-Space GUIs rather than running in the batch profile.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SYNTAX — grammar & structure. The full parse + CoNLL analyses (POS, dependency, clause, noun/verb/adj/adverb, "
        "function words, sentence complexity, readability) live in the CoNLL Table Analyzer GUI, which this section "
        "points you to. The CoNLL table it works from is generated by the parser you selected in Setup "
        "(Stanza, spaCy, or Stanford CoreNLP). (Batch wiring into the profile is planned.)")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SEMANTICS — what the words mean. The profile runs a snapshot: nouns & verbs aggregated UP to their WordNet "
        "top-synset classes (English + WordNet). Deeper tools — word-sense disambiguation, word embeddings, semantic "
        "similarity, nominalization — open from the Semantic Analysis GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "TOPICS — what the corpus is about. Topic modeling (BERTopic, Gensim LDA, MALLET) opens from the Topic "
        "Modeling GUI; the report points you there.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "NARRATIVE — who did what to whom. The profile now RUNS, with defaults, SVO (Subject-Verb-Object, via "
        "CoreNLP) and SRL (Semantic Role Labeling; skipped automatically if its transformer env isn't installed).\n\n"
        "Coreference — resolving 'he, she, his, they…' to WHO they actually are — underpins a great deal of the "
        "semantic and narrative reading of a text. It is VERY slow, so rather than run it here it opens (with "
        "dialogue and the 5 Ws) from the SVO GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SENTIMENT — how the corpus feels. The profile now RUNS Stanza neural sentiment by default (a real model, "
        "not a dictionary; already installed with Stanza, no extra download). The other engines (BERT, spaCy, VADER, "
        "NRC, SentiWordNet) open from the Sentiment Analysis GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer - 1


y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

readMe_message = ("The Corpus Profiler runs a battery of NLP analyses on your corpus with sensible DEFAULTS and "
                  "assembles the results into a single navigable HTML report — NLP_corpus_profile.html — the only "
                  "file opened automatically. Every individual output file (csv, xlsx, charts, maps) is written to a "
                  "category subfolder and LINKED from the report, so hundreds of files become depth-on-demand rather "
                  "than a flood.\n\nTick the analysis groups you want (or all), select '*' in a group's dropdown to run "
                  "everything in it, and press RUN. For full control over any single analysis, open its dedicated GUI.")
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
