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
import traceback
import tkinter as tk
import tkinter.messagebox as mb

import GUI_IO_util
import GUI_theme_util
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

    # everything goes under a single corpus_profile subdirectory. If a prior folder exists AND holds results
    # the profiler can REUSE (a completed CoreNLP pass and/or a Stanza POS table -- HOURS to recompute), the
    # user is first offered to KEEP & reuse them in place rather than the blanket wipe (so they needn't hunt
    # for the folder to preserve); otherwise the standard 'will be replaced?' confirm. NLP_SILENT auto-proceeds.
    outputDir = corpus_profiler_util.setup_profile_output_dir(GUI_util.window, inputFilename, inputDir, outputDir)
    if outputDir == '':   # user declined to replace the existing profile folder
        return

    # expand a ticked group's dropdown value into concrete analysis ids. Merged dropdowns (e.g. the
    # combined Counts+Vocabulary row) decorate their entries with '--- ' group headers and '     '
    # indents for readability, so strip those before matching REGISTRY labels. A bare group header
    # (e.g. '--- Vocabulary') normalizes to a word that matches no analysis label -> nothing selected.
    def expand(category, menu_value):
        ids = corpus_profiler_util.analyses_in_category(category)
        norm = str(menu_value).lstrip('- ').strip()
        if norm == '*' or norm == '':
            return ids
        return [aid for aid in ids if corpus_profiler_util.REGISTRY[aid]['label'] == norm]

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

    # NOTE: CoreNLP availability is handled inside the runners (corpus_profiler_util), NOT here. The
    # profiler auto-USES CoreNLP for the CoreNLP-only features (gender/dialogue/dates, semantics POS)
    # when CoreNLP + Java are installed -- even under a Stanza/spaCy config -- and otherwise degrades
    # gracefully (Stanza NER; those features skipped) with the summary telling the user how to install
    # CoreNLP. So there is no config-based pre-flight that drops analyses or blocks the run.

    # up-front runtime heads-up: the CoreNLP-backed work runs Java over the whole corpus and can take a very
    # long time. The Gender/Dialogue/Dates row (entities category) is the CoreNLP-only one; Narrative SVO is
    # CoreNLP only under a CoreNLP config. Counts (incl. NER via the configured parser), Vocabulary, Syntax
    # and Semantics are fast (Stanza/BERT, no Java). Let the user opt into the long run knowingly.
    heavy = [aid for aid in selected
             if corpus_profiler_util.REGISTRY[aid]['category'] in ('entities', 'narrative')
             and corpus_profiler_util.REGISTRY[aid]['kind'] == 'batch']
    # ...unless that Java pass is going to be REUSED: the user kept a completed CoreNLP pass in the profile
    # folder, so it is skipped entirely and the run is quick. Warning about hours that will not be spent
    # only teaches the user to ignore the warning.
    if heavy and corpus_profiler_util.corenlp_pass_reusable(outputDir):
        print('>>> Corpus Profiler: CoreNLP pass will be reused -- skipping the "may take a while" warning')
        heavy = []
    if heavy:
        if not mb.askyesno('This may take a while',
                           "The Gender / Dialogue / Dates analysis runs Stanford CoreNLP (Java) over your ENTIRE "
                           "corpus and can take a long time — potentially hours on a large corpus.\n\n"
                           "Counts (including entities/NER), Vocabulary, Syntax and Semantics are fast by "
                           "comparison.\n\nContinue with the full run?",
                           default='yes'):  # silent/unattended mode proceeds
            return

    # shared context passed to every runner. openOutputFiles is FORCED off in the runners --
    # only the profile report opens at the end.
    ctx = dict(window=GUI_util.window, inputFilename=inputFilename, inputDir=inputDir, outputDir=outputDir,
               config_filename=config_filename, chartPackage=chartPackage, dataTransformation=dataTransformation,
               language=language, export_json_var=export_json_var, memory_var=memory_var,
               document_length_var=document_length_var, limit_sentence_length_var=limit_sentence_length_var,
               package=package)   # so runners honor the CONFIGURED parser (e.g. SVO via Stanza, not forced CoreNLP)

    # Top-level bracket around the WHOLE sweep: "Started ... with N of M analyses checked at TIME" now,
    # and a matching "Finished ... taking ..." at the very end (profiler_startTime feeds the elapsed).
    _total_analyses = len(corpus_profiler_util.REGISTRY)
    profiler_startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 4000, 'Corpus Profiler',
        'Started running the Corpus Profiler with ' + str(len(selected)) + ' of ' +
        str(_total_analyses) + ' analyses checked at', True,
        'At the end a paper-style summary opens (with an HTML report beside it); '
        'every individual output file is linked from them.')

    # DIAGNOSTIC INSTRUMENTATION (temporary): the whole tail is wrapped so that ANYTHING that ends
    # the process at the end of a run -- a raised exception, or a late SystemExit from a lazily
    # imported util's install_all_Python_packages()==False: sys.exit(0) (SystemExit is NOT an
    # Exception, so run_profile's per-analysis `except Exception` would let it through) -- prints its
    # full origin traceback instead of a silent "Process finished with exit code 0". The >>> markers
    # localize exactly how far run() got; if the LAST marker prints and the window still closes, the
    # teardown is a .quit()/.destroy() somewhere (no exception), not a crash.
    try:
        # SILENT MODE: for the duration of the unattended batch, suppress the OK-button dialogs
        # (showwarning / showerror / showinfo) so a stray warning from any analysis can't FREEZE the run
        # waiting for a click -- they print to the console instead. Restored in the finally below.
        # (askyesno/askokcancel are left alone -- they branch on the answer; timed_alert already
        # auto-dismisses.) Modules call these as `mb.showwarning`, i.e. tkinter.messagebox.showwarning,
        # so patching the module attributes covers them all.
        import tkinter.messagebox as _mbmod
        _orig_dialogs = (_mbmod.showwarning, _mbmod.showerror, _mbmod.showinfo,
                         _mbmod.askyesno, _mbmod.askokcancel)

        def _silent_dialog(title=None, message=None, **_kw):
            print('[Corpus Profiler: dialog suppressed] %s -- %s'
                  % (title, str(message).replace('\n', ' ')[:300]))

        def _silent_ask(title=None, message=None, **_kw):
            # Never block the unattended batch on a Yes/No prompt. Honor the dialog's own declared
            # `default` (e.g. the "Directory already exists ... replace?" prompts pass default='yes');
            # fall back to proceed=True when no default is given ("continue?" dialogs mean yes).
            ans = str(_kw.get('default', 'yes')).lower() != 'no'
            print('[Corpus Profiler: auto-%s] %s -- %s'
                  % ('yes' if ans else 'no', title, str(message).replace('\n', ' ')[:300]))
            return ans
        _mbmod.showwarning = _silent_dialog
        _mbmod.showerror = _silent_dialog
        _mbmod.showinfo = _silent_dialog
        _mbmod.askyesno = _silent_ask
        _mbmod.askokcancel = _silent_ask
        # Loud, unmistakable marker: if you DON'T see this line at the top of a run, the process is
        # running STALE code (Python does not reload edited modules into a live process) -- fully stop
        # and restart before trusting the dialog-suppression / speed fixes.
        print('>>> Corpus Profiler: SILENT MODE ACTIVE -- OK/Yes-No dialogs auto-handled for this run.')

        results = corpus_profiler_util.run_profile(ctx, selected)
        print('>>> Corpus Profiler: %d analyses done; building index report...' % len(results))
        header = corpus_profiler_util.corpus_header_stats(inputFilename, inputDir)

        if inputDir:
            corpus_name = os.path.basename(inputDir.rstrip('/\\')) or 'corpus'
        else:
            corpus_name = os.path.splitext(os.path.basename(inputFilename))[0]

        # Record WHICH RELEASE produced this profile: the summary is a paper-style artifact that outlives
        # the run and gets shared, so the reader must be able to tell which version of the Suite made it
        # (findings change as analyses are fixed or added). Read from lib/release_version.txt via the same
        # getter the GUI's version display uses; degrade to no release stamp rather than fail the summary.
        try:
            _release = str(GUI_util.get_local_release_version() or '').strip()
        except Exception:
            _release = ''
        run_config = dict(
            subtitle='package: ' + str(package) + '  ·  language: ' + str(language) +
                     ('  ·  NLP Suite ' + _release if _release else '') +
                     '  ·  ' + time.strftime('%Y-%m-%d'),
            footer='NLP Suite — Corpus Profiler.  ' + str(len(results)) +
                   ' analyses run.  Per-file detail lives in the category subfolders.',
            inputDir=inputDir, inputFilename=inputFilename)   # so the summary can draw a corpus wordcloud

        # build both: the navigable index (companion) and the paper-style summary (opened below)
        corpus_profiler_util.build_report(outputDir, corpus_name, results, header, run_config)
        print('>>> Corpus Profiler: index report built; building paper-style summary...')
        summary = corpus_profiler_util.build_paper_summary(outputDir, corpus_name, results, header, run_config)
        print('>>> Corpus Profiler: summary built: %s' % summary)

        # Open the paper-style SUMMARY (the headline read; it links to the full navigable report and the
        # report links back). os.startfile (a direct Win32 ShellExecute) is the most robust path: unlike
        # os.system('start ...') -- which IO_files_util.openFile uses -- it works even when the app is
        # launched WITHOUT a console (pythonw / the frozen build). Try startfile -> webbrowser ->
        # openFile in turn. NOTE: webbrowser.open RETURNS False when it cannot launch a browser (it
        # does NOT raise), so we must check its boolean result -- otherwise a failed webbrowser.open
        # looks like success and the summary silently never opens.
        summary_abs = os.path.abspath(summary)
        print('>>> Corpus Profiler: opening summary: %s' % summary_abs)
        opened = False
        try:
            os.startfile(summary_abs)                                                       # Windows
            opened = True
        except Exception as _e:
            print('   os.startfile failed: %s' % _e)
        if not opened:
            try:
                if __import__('webbrowser').open('file:///' + summary_abs.replace('\\', '/')):
                    opened = True
            except Exception as _e:
                print('   webbrowser.open failed: %s' % _e)
        if not opened:
            try:
                IO_files_util.openFile(GUI_util.window, summary_abs)
                opened = True
            except Exception as _e:
                print('   openFile failed: %s' % _e)
        if not opened:
            print('Corpus Profiler: could not auto-open the summary. Open it manually:\n  ' + summary_abs)

        IO_user_interface_util.timed_alert(
            GUI_util.window, 4000, 'Corpus Profiler',
            'Finished running the Corpus Profiler with ' + str(len(selected)) + ' of ' +
            str(_total_analyses) + ' analyses checked at', True, '', True, profiler_startTime)
        print('>>> Corpus Profiler: run() complete; the GUI window should remain open.')
    except BaseException:
        # BaseException (not Exception) so a late SystemExit is captured with its origin too.
        print('>>> Corpus Profiler: run() tail terminated abnormally -- traceback follows:')
        traceback.print_exc()
        raise
    finally:
        # restore the real dialogs no matter how the run ended
        try:
            (_mbmod.showwarning, _mbmod.showerror, _mbmod.showinfo,
             _mbmod.askyesno, _mbmod.askokcancel) = _orig_dialogs
        except Exception:
            pass


GUI_util.run_button.configure(command=run)

# GUI section ______________________________________________________________________________________

IO_setup_display_brief = True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(
    IO_setup_display_brief,
    GUI_width=GUI_IO_util.get_GUI_width(3),
    GUI_height_brief=640,
    GUI_height_full=680,
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
characters_var = tk.IntVar()
characters_menu_var = tk.StringVar()

_dropdown_x = GUI_IO_util.open_setup_x_coordinate  # rough; nudge to taste

# 1. Counts & measures
counts_var.set(1)
counts_checkbox = GUI_theme_util.create_checkbox(window, text='How big / how varied? (Counts, measures, vocabulary, and entities - people, organizations, locations)',
                                 variable=counts_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, counts_checkbox, True)
counts_menu_var.set('*')
counts_menu = GUI_theme_util.create_option_menu(window, variable=counts_menu_var,
                              values=['*',
                                     '--- Statistics (sentences, words, syllables)',
                                     '     N-grams',
                                     '     Sentence length',
                                     '--- Vocabulary',
                                     "     Vocabulary richness (word type/token ratio or Yule's K)",
                                     '     Lexical diversity (TTR, MTLD, vocd-D)',
                                     "     Word frequency distribution (Zipf's Law)",
                                     '     TF-IDF (most distinctive words per document)',
                                     '     Unusual words (via NLTK)',
                                     '     Abstract / concrete vocabulary',
                                     '     Iconic vocabulary',
                                     '     Capital-initial words',
                                     '--- Entities',
                                     '     People, organizations, locations (NER)'
                                     ])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, counts_menu, False)

# # 2. Vocabulary
# vocabulary_var.set(1)
# vocabulary_checkbox = tk.Checkbutton(window, text="What's the vocabulary like?  (Vocabulary)",
#                                      variable=vocabulary_var, onvalue=1, offvalue=0)
# y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
#                                                y_multiplier_integer, vocabulary_checkbox, True)
# vocabulary_menu_var.set('*')
# vocabulary_menu = tk.OptionMenu(window, vocabulary_menu_var, '*',
#                                 "Vocabulary richness (word type/token ratio or Yule's K)",
#                                 'Lexical diversity (TTR, MTLD, vocd-D)',
#                                 "Word frequency distribution (Zipf's Law)",
#                                 'TF-IDF (most distinctive words per document)',
#                                 'Hapax legomena (once-occurring words)',
#                                 'Unusual words (via NLTK)',
#                                 'Abstract / concrete vocabulary',
#                                 'Iconic vocabulary',
#                                 'Words with capital initial (proper nouns)',
#                                 'Language detection')
# y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, vocabulary_menu, False)

# 3. Entities (English + Stanford CoreNLP)
entities_var.set(1)
entities_checkbox = GUI_theme_util.create_checkbox(window, text='Who said what, and when? (gender, dialogue, dates) (via CoreNLP)',
                                   variable=entities_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, entities_checkbox, True)
entities_menu_var.set('*')
entities_menu = GUI_theme_util.create_option_menu(window, variable=entities_menu_var,
                              values=['*', 'Gender, dates, dialogue (via CoreNLP)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, entities_menu, False)

# 3b. Spatial — geocodable & symbolic space (network-heavy: pointers to the GIS / Symbolic Space GUIs)
spatial_var.set(1)
spatial_checkbox = GUI_theme_util.create_checkbox(window, text='Where does it all happen?  (geocodable and symbolic space)',
                                  variable=spatial_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, spatial_checkbox, True)
spatial_menu_var.set('*')
spatial_menu = GUI_theme_util.create_option_menu(window, variable=spatial_menu_var,
                              values=['*',
                                     'Geocodable space — proportional-symbol map of corpus locations (Nominatim/Google)',
                                     'Full geocoding & mapping — geocoder choice, API key, Google Earth / folium / distances  (opens GIS GUI)',
                                     'Symbolic space — narrative / gendered space typology  (opens Symbolic Space GUI)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, spatial_menu, False)

# 4. Grammar & structure (Syntax) — batch parse + CoNLL analyses live in the analyzer GUI
syntax_var.set(1)
syntax_checkbox = GUI_theme_util.create_checkbox(window, text='Grammar & structure  (Syntax)',
                                 variable=syntax_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, syntax_checkbox, True)
syntax_menu_var.set('*')
syntax_menu = GUI_theme_util.create_option_menu(window, variable=syntax_menu_var,
                              values=['*',
                                     'POS · dependency · clause · N/V/Adj/Adv · function words · complexity · readability'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, syntax_menu, False)

# 5. What do the words mean? (Semantics)
semantics_var.set(1)
semantics_checkbox = GUI_theme_util.create_checkbox(window, text='What do the words mean?  (Semantics)',
                                    variable=semantics_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, semantics_checkbox, True)
semantics_menu_var.set('*')
semantics_menu = GUI_theme_util.create_option_menu(window, variable=semantics_menu_var,
                              values=['*',
                                     'Noun & verb classes (WordNet top synsets)',
                                     'WSD · word embeddings · semantic similarity · nominalization  (opens Semantic Analysis GUI)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, semantics_menu, False)

# 6. What is it about? (Topics)
topics_var.set(1)
topics_checkbox = GUI_theme_util.create_checkbox(window, text='What is it about?  (Topics)',
                                 variable=topics_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, topics_checkbox, True)
topics_menu_var.set('*')
topics_menu = GUI_theme_util.create_option_menu(window, variable=topics_menu_var,
                              values=['*', 'Topic modeling (BERT / Gensim / MALLET)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, topics_menu, False)

# 7. Who did what to whom? (Narrative)
narrative_var.set(1)
narrative_checkbox = GUI_theme_util.create_checkbox(window, text='Who did what to whom?  (Narrative)',
                                    variable=narrative_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, narrative_checkbox, True)
narrative_menu_var.set('*')
narrative_menu = GUI_theme_util.create_option_menu(window, variable=narrative_menu_var,
                              values=['*',
                                     'SVO (Subject-Verb-Object)',
                                     'SRL (Semantic Role Labeling)',
                                     'Coreference · 5 Ws  (opens SVO GUI)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, narrative_menu, False)

# 8. How does it feel? (Sentiment)
sentiment_var.set(1)
sentiment_checkbox = GUI_theme_util.create_checkbox(window, text='How does it feel?  (Sentiment)',
                                    variable=sentiment_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, sentiment_checkbox, True)
sentiment_menu_var.set('*')
sentiment_menu = GUI_theme_util.create_option_menu(window, variable=sentiment_menu_var,
                              values=['*',
                                     'Sentiment (Stanza)',
                                     'BERT · spaCy · VADER · NRC · SentiWordNet  (opens Sentiment GUI)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, sentiment_menu, False)

# 9. Zooming in on characters (emotional arcs + movement in space)
characters_var.set(1)
characters_checkbox = GUI_theme_util.create_checkbox(window,
                               text="Zooming in on characters: Characters' emotional arcs and movements in time and space",
                               variable=characters_var, onvalue=1, offvalue=0)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, characters_checkbox, True)
characters_menu_var.set('*')
characters_menu = GUI_theme_util.create_option_menu(window, variable=characters_menu_var,
                              values=['*',
                                     'Emotion arcs (NRC 8 emotions, per character across the story)',
                                     'Movement in time & space (each character’s places over the story, mapped)'])
y_multiplier_integer = GUI_IO_util.placeWidget(window, _dropdown_x, y_multiplier_integer, characters_menu, False)

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
        "COUNTS, MEASURES, & VOCABULARY\n\n"
        'COUNTS & MEASURES — how big and how varied is the corpus. Statistics (sentences/words/syllables)\n\n'
        "VOCABULARY — a SNAPSHOT of the corpus's lexical character: vocabulary richness (TTR / Yule's K), lexical "
        "diversity (MTLD / vocd-D), word frequency (Zipf), TF-IDF distinctive words, hapax legomena, unusual words "
        "(NLTK), abstract/concrete, iconic vocabulary, proper nouns, language detection. Select '*' to run all; each "
        "runs with defaults.\n\nThis is a curated subset. For the FULL set of ~20 vocabulary & style options "
        "(short/vowel words, punctuation-as-pathos, objectivity/subjectivity, repetition, unigram variants, and more), "
        "open the dedicated STYLE ANALYSIS GUI.\n\n"
        "ENTITIES — people, organizations and locations (Named-Entity Recognition). Extracted with the parser "
        "you set as your DEFAULT NLP package (Stanza, spaCy or Stanford CoreNLP); this always runs — no Java "
        "required unless CoreNLP is your chosen parser. Gender, dialogue and dates are separate (the 'Who said "
        "what, and when?' row — those need CoreNLP + Java).\n\n"
        "n-grams, sentence & line length. Select '*' to run all, or pick one. Runs with defaults.")
    # y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
    #     "VOCABULARY — a SNAPSHOT of the corpus's lexical character: vocabulary richness (TTR / Yule's K), lexical "
    #     "diversity (MTLD / vocd-D), word frequency (Zipf), TF-IDF distinctive words, hapax legomena, unusual words "
    #     "(NLTK), abstract/concrete, iconic vocabulary, proper nouns, language detection. Select '*' to run all; each "
    #     "runs with defaults.\n\nThis is a curated subset. For the FULL set of ~20 vocabulary & style options "
    #     "(short/vowel words, punctuation-as-pathos, objectivity/subjectivity, repetition, unigram variants, and more), "
    #     "open the dedicated STYLE ANALYSIS GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "GENDER, DIALOGUE & DATES (Stanford CoreNLP). Three enrichments that exist ONLY in CoreNLP: character "
        "GENDER (coreference-based), speaker-attributed DIALOGUE/QUOTES (who said what), and normalized DATES & "
        "TIMES (SUTime — 'the next morning' resolved to an actual date). This row RUNS only when CoreNLP + Java "
        "are installed, and uses CoreNLP whenever present REGARDLESS of your default parser, because there is no "
        "Stanza/spaCy equivalent. If CoreNLP/Java are absent it is skipped and the summary tells you how to "
        "enable it — your people/organizations/locations are unaffected: those (NER) are extracted in the "
        "Counts row above with the parser you selected as the default NLP package (Stanza, spaCy or CoreNLP).")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "WHERE DOES IT ALL HAPPEN? — the space of the corpus, in two senses. GEOCODABLE space now RUNS in the "
        "batch as a quick snapshot: the place names your text mentions (from NER) are geocoded and drawn as a "
        "proportional-symbol map (bubble size = mentions). Only the top 40 distinct places are geocoded, so an "
        "unattended run can't stall. Geocoder: Google if you have configured a geocode API key, otherwise "
        "Nominatim/OpenStreetMap with folium — no key or download needed, chosen silently. As with other "
        "dimensions, the dedicated GIS GUI offers far more control (geocoder choice, API key for speed, "
        "Google Earth / folium / distances, manual correction of bad geocodes); the profiler is the quick "
        "snapshot. SYMBOLIC space — the non-geocodable, culturally-coded space of a narrative (kitchen vs. field, "
        "inside vs. outside, women's vs. men's space), analysed by typology and cross-tabulated with gender — is "
        "interactive and still OPENS the Symbolic-Space GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SYNTAX — grammar & structure. The profile now RUNS, with defaults, a parts-of-speech distribution "
        "(nouns, verbs, adjectives, adverbs, pronouns) using the Stanza POS tagger, and reports the breakdown and "
        "the noun-to-verb ratio with a chart. The deeper CoNLL analyses (dependency, clause, function words, "
        "sentence complexity, readability) open from the CoNLL Table Analyzer GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SEMANTICS — what the words mean. The profile RUNS: (1) nouns & verbs aggregated UP to THREE knowledge "
        "bases — WordNet top-synset classes (nouns & verbs), VerbNet classes (verbs) and FrameNet frames "
        "(nouns & verbs) — three complementary lenses on meaning; and (2) BERT word embeddings "
        "(sentence-transformers all-distilroberta-v1) of the 200 most frequent words, projected into an "
        "interactive 2-D t-SNE semantic map. Deeper tools — word-sense disambiguation, semantic similarity, "
        "nominalization — open from the Semantic Analysis GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "TOPICS — what the corpus is about. The profile now RUNS Gensim LDA topic modeling with defaults "
        "(10 topics), producing an interactive pyLDAvis map plus a topic-keywords table the summary reads. "
        "NOTE: topic modeling needs many documents (hundreds) for authoritative results; on a small corpus the "
        "topics are only indicative. Deeper engines (BERTopic, MALLET, coherence tuning) open from the Topic "
        "Modeling GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "NARRATIVE — who did what to whom. The profile now RUNS, with defaults, SVO (Subject-Verb-Object, via "
        "CoreNLP) and SRL (Semantic Role Labeling; skipped automatically if its transformer env isn't installed).\n\n"
        "Coreference — resolving 'he, she, his, they…' to WHO they actually are — underpins a great deal of the "
        "semantic and narrative reading of a text. It is VERY slow, so rather than run it here it opens (with the "
        "5 Ws, and speaker-attributed dialogue) from the SVO GUI. Note: plain dialogue/quotes are already "
        "extracted in the Entities pass above, so they are not repeated here.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "SENTIMENT — how the corpus feels. The profile now RUNS Stanza neural sentiment by default (a real model, "
        "not a dictionary; already installed with Stanza, no extra download). The other engines (BERT, spaCy, VADER, "
        "NRC, SentiWordNet) open from the Sentiment Analysis GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "ZOOMING IN ON CHARACTERS — a character-centric lens, RUN with defaults. Two analyses:\n\n"
        "• EMOTION ARCS — how each character feels and how that feeling rises and falls: a per-character trace of "
        "NRC's eight emotions (anger, anticipation, disgust, fear, joy, sadness, surprise, trust) across the "
        "narrative, using Stanza NER to attribute sentences to characters; produces an emotion-arc chart and a "
        "dominant-emotion timeline per leading character.\n\n"
        "• MOVEMENT IN TIME & SPACE — where each character goes, and when: Stanza tracks the places each character "
        "passes through and builds an animated migration MAP whose timeline follows narrative order (sentence "
        "index), with a per-document filter. Only the DISTINCT locations are geocoded (bounded), and we cap to the "
        "40 most frequent, so a big-corpus run can't stall on the network.\n\n"
        "Whole-narrative 'shape of stories' (heavy BERT + clustering) stays in the Sentiment Analysis GUI.")
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer,
                                                         "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer - 1


y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

readMe_message = ("The Corpus Profiler runs a battery of NLP analyses on your corpus with sensible DEFAULTS and "
                  "assembles the results into a single navigable HTML report — NLP_corpus_profile.html — the only "
                  "file opened automatically. Every individual output file (csv, xlsx, charts, maps) is written to a "
                  "category subfolder and LINKED from the report, so hundreds of files become depth-on-demand rather "
                  "than a flood.\n\nTick the analysis groups you want (or all), select '*' in a group's dropdown to run "
                  "everything in it, and press RUN. For full control over any single analysis, open its dedicated GUI."
                  "\n\nSome passes run heavy NLP models (Stanford CoreNLP, and SRL - Semantic Role Labeling) and "
                  "can take a LONG time on a large corpus - hours. SRL in particular runs in a separate, isolated "
                  "engine and shows NO progress while it works: a silent, seemingly frozen window during SRL is "
                  "EXPECTED, not a crash - let it finish.\n\nIf a run is interrupted (a crash, a power cut), just "
                  "run it again and choose to KEEP the existing profile folder when asked: every completed pass "
                  "(CoreNLP, POS, NER, SVO, sentiment, SRL) is reused from disk, so you RESUME where you left off "
                  "rather than restart from zero.")
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)

GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command,
                    videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)

GUI_util.window.mainloop()
