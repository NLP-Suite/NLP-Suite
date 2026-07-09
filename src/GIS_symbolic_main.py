# written by Roberto Franzosi and Claude July 2026
# Narrative / Symbolic Space Analyzer (non-geocodable space) — sibling of GIS_main.
# See docs/Narrative_Symbolic_Space_design.md and GIS_symbolic_util.py.

import sys
import GUI_util
import IO_libraries_util
import tkinter.messagebox as mb

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "GIS_symbolic_main",
        ['os', 'tkinter', 'pandas', 'numpy', 'scipy', 'matplotlib', 'nltk']) == False:
    sys.exit(0)

import os
import tkinter as tk
from tkinter import filedialog
import IO_files_util
import GUI_IO_util

# RUN section ______________________________________________________________________________________________________________________________________________________

def run(inputFilename, inputDir, outputDir, openOutputFiles, chartPackage, dataTransformation,
        do_extract, do_movement, do_distribution, location_col, attribute_col, sequence_col):

    filesToOpen = []

    if not do_extract and not do_movement and not do_distribution:
        mb.showwarning(title='No analysis selected',
                       message="Please tick at least one option:\n\n"
                               "  • Extract social actors in non-geocodable space… (BUILD)\n"
                               "  • MAP social actors moving… (DYNAMIC)\n"
                               "  • Distribution of social actors… (STATIC)")
        return

    if not inputFilename or not os.path.isfile(inputFilename):
        grabbed = ''
        if do_extract:
            # BUILD reads a CoNLL table. Try to auto-grab the newest CoNLL found for this corpus (e.g. one
            # just produced by the parser), drop it into the input box, and continue this run.
            import CoNLL_util
            conlls = CoNLL_util.find_corpus_CoNLL(outputDir, GUI_util.inputFilename.get(),
                                                  GUI_util.input_main_dir_path.get())
            if conlls and mb.askyesno(title='Use this CoNLL for BUILD?',
                    message='Found a CoNLL table for your corpus:\n\n' + os.path.basename(conlls[0]) +
                            '\n\nUse it as the BUILD input?'):
                _apply_selected_csv(conlls[0])   # populate the input textbox + enable RUN
                grabbed = conlls[0]
        if grabbed:
            inputFilename = grabbed              # continue this run with the grabbed CoNLL
        elif do_extract:
            import run_script_util
            if mb.askyesno(title='No CoNLL input',
                    message='The BUILD step needs a CoNLL table of your corpus, and none was found.\n\n'
                            'Open the Parsers & annotators GUI now to parse your corpus into a CoNLL table?\n\n'
                            '(Then come back and click RUN again — this tool will grab the CoNLL for you.)'):
                run_script_util.run_script("parsers_annotators_main.py")
            return
        else:
            mb.showwarning(title='No input file',
                           message='The DYNAMIC / STATIC analyses need a Social-actors csv.\n\nClick Select INPUT '
                                   'CSV — the picker lists the tables the BUILD step produces (or Browse to one).')
            return

    if not outputDir:
        mb.showwarning(title='No output directory',
                       message='Please select an OUTPUT files directory (the top I/O row, or Setup).')
        return

    import pandas as pd
    import GIS_symbolic_util as ss

    # ---- BUILD: extract the actor-in-space table from a CoNLL corpus ---------
    if do_extract:
        events_csv = ss.extract_actor_space_events(inputFilename, outputDir)
        if events_csv:
            filesToOpen.append(events_csv)
            # push the BUILD output into the input box (replacing the CoNLL) so the DYNAMIC / STATIC
            # analyses run on the Social-actors table and its columns (space_type, Sentence ID…) populate
            # the Location / Sequence / Attribute dropdowns
            _apply_selected_csv(events_csv)
            inputFilename = events_csv
            # BUILD is a one-shot: untick it so a follow-up RUN does not try to re-BUILD from this
            # (non-CoNLL) Social-actors table
            extract_var.set(0)
        else:
            mb.showwarning(title='No events extracted',
                           message='No social-actor-in-non-geocodable-space events were found.\n\n'
                                   'The BUILD step expects a CoNLL table (parse your corpus first via the '
                                   'Parsers & annotators or SVO GUI).')
            return

    # the movement / distribution analyses read the assembled actor-location csv;
    # if only BUILD was requested, we are done
    if not do_movement and not do_distribution:
        if filesToOpen and openOutputFiles == 1:
            IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)
        return

    if not location_col:
        mb.showwarning(title='No location column',
                       message='The movement / distribution analyses need a Location column from your CSV.')
        return

    try:
        try:
            df = pd.read_csv(inputFilename, encoding='utf-8', engine='python')
        except UnicodeDecodeError:
            df = pd.read_csv(inputFilename, encoding='ISO-8859-1', engine='python')
    except Exception as e:
        mb.showerror(title='Could not read CSV', message='Failed to read the input CSV:\n{}'.format(e))
        return

    if location_col not in df.columns:
        mb.showwarning(title='Column not found',
                       message="The location column '{}' is not in the CSV.".format(location_col))
        return

    # ---- STATIC: distribution of the attribute across space-types ----------
    if do_distribution:
        if not attribute_col:
            mb.showwarning(title='No attribute column',
                           message='The Distribution analysis needs an Attribute column '
                                   '(gender, race, class…).')
            return
        obs = list(zip(df[attribute_col].astype(str), df[location_col].astype(str)))
        table = ss.attribute_space_crosstab(obs)
        if table.empty:
            mb.showwarning(title='No data',
                           message='No (attribute, classifiable-location) pairs were found.\n\n'
                                   'Check the columns, and consider editing '
                                   'lib/symbolic_space_typology.csv to add your domain’s place words.')
        else:
            stats = ss.crosstab_stats(table)
            base = attribute_col.strip().replace(' ', '_')
            csv_out = os.path.join(outputDir, 'symbolic_space_{}_x_space.csv'.format(base))
            ss.save_crosstab_csv(table, csv_out, stats)
            filesToOpen.append(csv_out)
            png = os.path.join(outputDir, 'symbolic_space_{}_x_space_heatmap.png'.format(base))
            ss.plot_attribute_space_heatmap(table, png, values='residuals', stats=stats,
                                            title='{} × non-geocodable space'.format(attribute_col))
            filesToOpen.append(png)

    # ---- DYNAMIC: movement through space-types (narrative transitions) ------
    if do_movement:
        d = df
        if sequence_col and sequence_col in df.columns:
            try:
                d = df.sort_values(sequence_col)
            except Exception:
                d = df
        sequence = [str(x) for x in d[location_col].tolist()]
        path, edges = ss.narrative_transitions(sequence)
        if not edges:
            mb.showwarning(title='No movement',
                           message='No transitions between classifiable spaces were found.\n\n'
                                   'The dynamic view needs the rows in narrative ORDER (pick a '
                                   'Sequence column) and place words the typology recognizes.')
        else:
            trans_csv = os.path.join(outputDir, 'symbolic_space_transitions.csv')
            pd.DataFrame(edges, columns=['from_space', 'to_space', 'count']).to_csv(
                trans_csv, index=False, encoding='utf-8-sig')
            filesToOpen.append(trans_csv)
            png = os.path.join(outputDir, 'symbolic_space_movement.png')
            ss.plot_transition_graph(edges, png)
            filesToOpen.append(png)

    if not filesToOpen:
        return
    if openOutputFiles == 1:
        IO_files_util.OpenOutputFiles(GUI_util.window, openOutputFiles, filesToOpen, outputDir, scriptName)


# the values of the GUI widgets MUST be read here so they are current at RUN time
run_script_command = lambda: run(GUI_util.inputFilename.get(),
                                 GUI_util.input_main_dir_path.get(),
                                 GUI_util.output_dir_path.get(),
                                 GUI_util.open_csv_output_checkbox.get(),
                                 GUI_util.charts_package_options_widget.get(),
                                 GUI_util.data_transformation_options_widget.get(),
                                 extract_var.get(),
                                 map_var.get(),
                                 distribution_var.get(),
                                 location_col_var.get(),
                                 attribute_col_var.get(),
                                 sequence_col_var.get())

GUI_util.run_button.configure(command=run_script_command)


# GUI section ______________________________________________________________________________________________________________________________________________________

IO_setup_display_brief = True
GUI_size, y_multiplier_integer, increment = GUI_IO_util.GUI_settings(
    IO_setup_display_brief,
    GUI_width=GUI_IO_util.get_GUI_width(3),
    GUI_height_brief=560,
    GUI_height_full=640,
    y_multiplier_integer=GUI_util.y_multiplier_integer,
    y_multiplier_integer_add=2,
    increment=2)

GUI_label = 'Graphical User Interface (GUI) for Non-geocodable (Symbolic) Space — from Text to Narrative-Space Map'
head, scriptName = os.path.split(os.path.basename(__file__))
config_filename = 'NLP_default_IO_config.csv'

# input file 3 = csv file; no input dir / secondary dir; output dir on
config_input_output_numeric_options = [3, 0, 0, 1]

GUI_util.set_window(GUI_size, GUI_label, config_filename, config_input_output_numeric_options)

window = GUI_util.window
config_input_output_numeric_options = GUI_util.config_input_output_numeric_options
config_filename = GUI_util.config_filename
inputFilename = GUI_util.inputFilename
input_main_dir_path = GUI_util.input_main_dir_path

GUI_util.GUI_top(config_input_output_numeric_options, config_filename, IO_setup_display_brief, scriptName)

csv_file_var = tk.StringVar()
extract_var = tk.IntVar()
map_var = tk.IntVar()
distribution_var = tk.IntVar()
location_col_var = tk.StringVar()
attribute_col_var = tk.StringVar()
sequence_col_var = tk.StringVar()
extra_GUIs_var = tk.IntVar()
extra_GUIs_menu_var = tk.StringVar()


def _enable_run_button(*args):
    # RUN becomes available as soon as an analysis is ticked (BUILD / DYNAMIC / STATIC);
    # run() validates the input file + output dir at click time.
    if extract_var.get() or map_var.get() or distribution_var.get():
        GUI_util.run_button.configure(state='normal')
extract_var.trace('w', _enable_run_button)
map_var.trace('w', _enable_run_button)
distribution_var.trace('w', _enable_run_button)


# ---- INPUT CSV file — smart picker (lists csv files found for the corpus) ---
def _builder_output(path):
    """The picker lists ONLY the tables produced by the Social-actors BUILD step
    (NLP_GIS_symbolic_actor_space_events_*.csv) — the ready actor-in-space input the
    DYNAMIC / STATIC analyses read. Anything else (a CoNLL to BUILD from, or a hand-coded
    csv) is reached with 'Browse for another file'."""
    return 'actor_space_events' in os.path.basename(path).lower()


def refresh_run_button():
    # Re-evaluate the RUN button after selecting the csv via the custom button. Config
    # [3,0,0,1] expects a csv FILE and RUN is gated on GUI_util.inputFilename, which the
    # custom button (not the standard IO widget) must populate. Pass missing='' when the
    # output dir is set so activateRunButton validates the live inputFilename and enables RUN.
    out_dir = GUI_util.output_dir_path.get()
    missing = '' if out_dir != '' else 'OUTPUT files directory\n'
    cfg = GUI_util.config_filename_selected_config.get() or config_filename
    try:
        GUI_util.activateRunButton(cfg, IO_setup_display_brief, scriptName, missing, True)
    except Exception as e:
        print('refresh_run_button: could not re-evaluate RUN button:', e)


def _apply_selected_csv(f):
    """Store the chosen csv and refresh dependent widgets + the RUN button.
    Clearing input_main_dir_path is required — activateRunButton disables RUN when an
    input dir is set but none is expected. csv_file_var's trace refreshes the columns."""
    csv_file_var.set(f)
    GUI_util.inputFilename.set(f)
    GUI_util.input_main_dir_path.set('')
    refresh_columns()
    refresh_run_button()


def select_csv_file():
    import CoNLL_util
    # list ONLY the Social-actors BUILD output tables found for this corpus, newest-first
    matches = CoNLL_util.find_corpus_csv(GUI_util.output_dir_path.get(),
                                         GUI_util.inputFilename.get(),
                                         GUI_util.input_main_dir_path.get(),
                                         path_filter=_builder_output)
    if not matches:
        mb.showinfo(title='No Social-actors table yet',
                    message="No Social-actors table (NLP_GIS_symbolic_actor_space_events_*.csv) was found for "
                            "this corpus.\n\nProduce one with the BUILD step: tick 'Extract social actors in "
                            "non-geocodable space (BUILD)', select a CoNLL table of your corpus, and RUN. Then this "
                            "picker will list it.\n\nOr browse now for a table you already have.")
        f = filedialog.askopenfilename(title='Select INPUT csv file',
                                       filetypes=[('csv files', '*.csv'), ('All files', '*.*')])
        if f:
            _apply_selected_csv(f)
        return
    chosen = IO_files_util.select_path_from_list(
        window, matches,
        'Select a Social-actors table produced by the BUILD step, or browse for another file:',
        title='Available Social-actors tables')
    if chosen is None:
        return
    if chosen == '__BROWSE__':
        f = filedialog.askopenfilename(title='Select INPUT CSV file',
                                       filetypes=[('csv files', '*.csv'), ('All files', '*.*')])
    else:
        f = chosen
    if f:
        _apply_selected_csv(f)

csv_file_button = tk.Button(window, width=GUI_IO_util.select_file_directory_button_width,
                            text='Select INPUT CSV file', command=lambda: select_csv_file())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate,
                                               y_multiplier_integer, csv_file_button, True)

openInputFile_button = tk.Button(window, width=GUI_IO_util.open_file_directory_button_width, text='',
                                 command=lambda: IO_files_util.openFile(window, csv_file_var.get()))
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               openInputFile_button, True, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu, "Open the INPUT csv file")

csv_file = tk.Entry(window, width=GUI_IO_util.csv_file_width, textvariable=csv_file_var)
csv_file.config(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.entry_box_x_coordinate, y_multiplier_integer, csv_file)


# ---- Related GUIs (quick launch) ------------------------------------------
def open_GUI(*args):
    import run_script_util
    if extra_GUIs_var.get():
        extra_GUIs_menu.configure(state='normal')
    sel = extra_GUIs_menu_var.get()
    if not sel:
        return
    if 'GIS' in sel or 'geocodable' in sel:
        run_script_util.run_script("GIS_main.py")
    elif 'SVO' in sel:
        run_script_util.run_script("SVO_main.py")
    elif 'NER' in sel:
        run_script_util.run_script("NER_main.py")
    elif 'Semantic' in sel:
        run_script_util.run_script("semantic_analysis_main.py")
    elif 'Narrative' in sel:
        run_script_util.run_script("narrative_analysis_ALL_main.py")
    else:
        mb.showwarning(title='Warning',
                       message="The selected option is not available.\n\nPlease, select a different option and try again.")

extra_GUIs_var.set(0)
extra_GUIs_checkbox = tk.Checkbutton(window, text='GUIs available for more analyses ',
                                     variable=extra_GUIs_var, onvalue=1, offvalue=0,
                                     command=lambda: open_GUI())
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               extra_GUIs_checkbox, True)

extra_GUIs_menu_var.set('')
extra_GUIs_menu = tk.OptionMenu(window, extra_GUIs_menu_var,
                                'GIS — map geocodable space (Open GUI)',
                                'SVO — who did what where (Open GUI)',
                                'NER — extract place mentions (Open GUI)',
                                'Semantic analysis (Open GUI)',
                                'Narrative analysis (Open GUI)')
extra_GUIs_menu.configure(state='disabled')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               extra_GUIs_menu, False, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "Other analyses you may want to run, opened without leaving this GUI:\n\n"
                                               "GIS — the geocodable sibling of this tool: maps real map-coordinate space.\n"
                                               "SVO (who-did-what-where) — scaffolds the actor + place (+ order) rows; you "
                                               "still add the ATTRIBUTE column by hand (gender can be tagged by the gender "
                                               "annotator; race/class you code).\n"
                                               "NER — extracts place mentions (a location-level view, no actor).\n"
                                               "Semantic analysis — WordNet / VerbNet / FrameNet on the same corpus.\n"
                                               "Narrative analysis — story-grammar / narrative-structure tools on the same corpus.\n\n"
                                               "The selected GUI opens without pressing RUN.")

extra_GUIs_menu_var.trace('w', open_GUI)


# ---- BUILD — extract the actor-in-space table from a text corpus -----------
extract_var.set(0)
extract_checkbox = tk.Checkbutton(window, variable=extract_var, onvalue=1, offvalue=0)
extract_checkbox.config(text="Extract social actors in non-geocodable space from a corpus  (BUILD)")
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               extract_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "BUILD step. Runs the extraction pipeline on a CoNLL parse of your corpus: "
                                               "for each place noun that maps to a non-geocodable space type, it walks the "
                                               "dependency parse to the acting social actor (subject), producing the "
                                               "actor-in-space table the DYNAMIC and STATIC analyses read.\n\nInput here is "
                                               "a CoNLL table (parse the corpus first via Parsers & annotators or SVO).")


# ---- Row 1: DYNAMIC — movement through non-geocodable space ----------------
map_var.set(0)
map_checkbox = tk.Checkbutton(window, variable=map_var, onvalue=1, offvalue=0)
map_checkbox.config(text="MAP social actors moving in time and non-geocodable space  (DYNAMIC)")
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               map_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "DYNAMIC view. Traces how social actors MOVE between kinds of space "
                                               "over the narrative (door → house → field → woods…) as a "
                                               "directed movement graph.\n\nNeeds the rows in narrative ORDER: pick a "
                                               "Sequence column below (or a date/index).")


# ---- Row 2: STATIC — distribution across non-geocodable space --------------
distribution_var.set(0)
distribution_checkbox = tk.Checkbutton(window, variable=distribution_var, onvalue=1, offvalue=0)
distribution_checkbox.config(text="Distribution of social actors across non-geocodable space  (STATIC)")
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               distribution_checkbox, False, False, False, False, 90,
                                               GUI_IO_util.labels_x_coordinate,
                                               "STATIC view. Cross-tabulates a social ATTRIBUTE (gender, race, class…) "
                                               "against the KIND of space, with a heatmap + chi-square / Cramer's V.\n\n"
                                               "Answers: which actors appear in which kind of space.")


# ---- Column pickers (populated from the selected CSV's headers) -----------
def _column_menu(col_var):
    menu = tk.OptionMenu(window, col_var, '')
    menu.configure(state='disabled')
    return menu

location_col_label = tk.Label(window, text='Location column  (both)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               location_col_label, True)
location_col_menu = _column_menu(location_col_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               location_col_menu, False, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "Select the CSV column that holds the place / location names "
                                               "(e.g. door, house, field, woods).\n\nIf your input is a Social-actors "
                                               "table from the BUILD step, pick 'space_noun' (the raw place word) or "
                                               "'space_type' (its category, e.g. domestic_interior).")

sequence_col_label = tk.Label(window, text='Sequence column  (DYNAMIC)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               sequence_col_label, True)
sequence_col_menu = _column_menu(sequence_col_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               sequence_col_menu, False, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "Optional. The CSV column giving narrative ORDER (a step index or date) "
                                               "so the movement view knows the sequence. Only used by the dynamic view."
                                               "\n\nIn a Social-actors table from the BUILD step, pick 'Sentence ID'.")

attribute_col_label = tk.Label(window, text='Attribute column  (STATIC)')
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.labels_x_coordinate, y_multiplier_integer,
                                               attribute_col_label, True)
attribute_col_menu = _column_menu(attribute_col_var)
y_multiplier_integer = GUI_IO_util.placeWidget(window, GUI_IO_util.IO_configuration_menu, y_multiplier_integer,
                                               attribute_col_menu, False, False, True, False, 90,
                                               GUI_IO_util.IO_configuration_menu,
                                               "Select the CSV column holding the social attribute of the actor "
                                               "(gender, race, class…). Required for the Distribution analysis.\n\n"
                                               "The BUILD step does NOT create this column — it gives you 'actor' "
                                               "(who acts) but not their attribute. Add a gender / race / class column "
                                               "to the Social-actors table (by hand, or gender via the gender "
                                               "annotator), then pick it here.")


def refresh_columns(*args):
    """Repopulate the three column dropdowns from the selected CSV's headers."""
    cols = []
    path = csv_file_var.get()
    if path and os.path.isfile(path):
        try:
            import pandas as pd
            try:
                cols = list(pd.read_csv(path, nrows=0, encoding='utf-8', engine='python').columns)
            except UnicodeDecodeError:
                cols = list(pd.read_csv(path, nrows=0, encoding='ISO-8859-1', engine='python').columns)
        except Exception:
            cols = []
    for col_var, menu in ((location_col_var, location_col_menu),
                          (attribute_col_var, attribute_col_menu),
                          (sequence_col_var, sequence_col_menu)):
        m = menu['menu']
        m.delete(0, 'end')
        for opt in [''] + cols:
            m.add_command(label=opt, command=lambda v=col_var, o=opt: v.set(o))
        col_var.set('')
        menu.configure(state='normal' if cols else 'disabled')

csv_file_var.trace('w', refresh_columns)

# Receive a csv pushed from a producer GUI (e.g. the SVO extractor), like the CoNLL analyzer.
if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) and sys.argv[1].lower().endswith('.csv'):
    _apply_selected_csv(sys.argv[1])


videos_lookup = {'No videos available': ''}
videos_options = 'No videos available'

TIPS_lookup = {'Narrative / non-geocodable symbolic space': 'TIPS_NLP_GIS Narrative non-geocodable symbolic space.pdf',
               'Geocoding': 'TIPS_NLP_GIS_Geocoding.pdf',
               'csv files - Problems & solutions': 'TIPS_NLP_csv files - Problems & solutions.pdf'}
TIPS_options = 'Narrative / non-geocodable symbolic space', 'Geocoding', 'csv files - Problems & solutions'


def help_buttons(window, help_button_x_coordinate, y_multiplier_integer):
    if not IO_setup_display_brief:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_corpusData)
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_outputDirectory)
    else:
        y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_IO_setup)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "Select an INPUT csv file that has (at least) a column of place / location names, and a column of the actor's "
        "social attribute (gender, race, class). For the movement (dynamic) view, the rows should be in narrative ORDER, "
        "or have a sequence / date column.\n\nThis tool analyzes NON-geocodable space: kinds of place that do not resolve "
        "to map coordinates (house, field, threshold, woods, market). Place words are classified via "
        "lib/symbolic_space_typology.csv, which you can edit to add your domain's terms." + GUI_IO_util.msg_openFile)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "Tick 'GUIs available for more analyses' to open a related tool of interest without leaving this GUI:\n"
        "   • GIS — the geocodable sibling of this analyzer (maps real map-coordinate space);\n"
        "   • SVO (who-did-what-where) — scaffolds the actor + place (+ order) rows; you still add the ATTRIBUTE "
        "column by hand (gender can be tagged by the gender annotator; race/class you code);\n"
        "   • NER — extracts place mentions (a location-level view, no actor);\n"
        "   • Semantic analysis — WordNet / VerbNet / FrameNet on the same corpus;\n"
        "   • Narrative analysis — story-grammar / narrative-structure tools on the same corpus.\n\n"
        "Tip: if you have no input csv yet, the 'Select INPUT CSV file' picker will offer to open the SVO extractor "
        "for you." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "BUILD step (the pipeline). This is how you get the input table when you start from TEXT rather than a ready csv.\n\n"
        "In INPUT it expects a CoNLL dependency table (parse your corpus first via the Parsers & annotators or SVO GUI). "
        "It walks the parse to find, for every non-geocodable place noun (cupboard, hall, forest, dungeon…), the social "
        "actor acting there (the subject), classifying the place into a space type via lib/symbolic_space_typology.csv.\n\n"
        "In OUTPUT it writes NLP_GIS_symbolic_actor_space_events_<corpus>.csv — one row per actor-in-space event "
        "(actor, space noun, space type, order). That file is the actor-location table the DYNAMIC and STATIC analyses "
        "read; you add the actor ATTRIBUTE (gender/race/class) column to it (the gender annotator can tag gender)."
        + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "DYNAMIC view (movement). Traces how social actors move between KINDS of space over the narrative "
        "(e.g. door → house → field → woods) and draws a directed movement graph.\n\n"
        "In INPUT the algorithm expects a csv file with a LOCATION column (place names) and, to establish the "
        "narrative ORDER, a SEQUENCE column (a step index or a date). This is a file you ASSEMBLE yourself — no "
        "single tool outputs it: the SVO extractor gives the actor + LOCATION (+ order) rows, and you add any "
        "attribute column by hand. Rows are read in that order; place words are classified into space types via "
        "lib/symbolic_space_typology.csv (editable).\n\n"
        "In OUTPUT the algorithm produces:\n"
        "   1. symbolic_space_transitions.csv — each from-space → to-space transition and its count;\n"
        "   2. symbolic_space_movement.png — the directed movement graph (arrow width scaled by transition count)."
        + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "STATIC view (distribution). Cross-tabulates a social ATTRIBUTE (gender, race, class) against the KIND of "
        "space — which actors appear in which kind of space.\n\n"
        "In INPUT the algorithm expects a csv file with a LOCATION column (place names) and an ATTRIBUTE column "
        "(gender, race, class…). This is a file you ASSEMBLE yourself — no single tool outputs it: the SVO extractor "
        "gives the actor + LOCATION rows, but the ATTRIBUTE is your own coding (race and class have no annotator; "
        "gender the gender annotator can tag). Place words are classified into space types via "
        "lib/symbolic_space_typology.csv (editable).\n\n"
        "In OUTPUT the algorithm produces:\n"
        "   1. symbolic_space_<attribute>_x_space.csv — the contingency table (attribute × space type), plus "
        "symbolic_space_<attribute>_x_space_residuals.csv (standardized residuals);\n"
        "   2. symbolic_space_<attribute>_x_space_heatmap.png — a heatmap annotated with chi-square, Cramer's V, "
        "and the over/under-represented cells." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "Select the CSV column that holds the place / location names (e.g. door, house, field, woods).\n\n"
        "If your input is a Social-actors table produced by the BUILD step, pick 'space_noun' (the raw place word) "
        "or 'space_type' (its category, e.g. domestic_interior)." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "Optional. The CSV column giving narrative ORDER (a step index or a date) so the movement view knows the "
        "sequence. Only used by the dynamic view.\n\nIn a Social-actors table from the BUILD step, pick 'Sentence ID'."
        + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help",
        "Select the CSV column holding the actor's social attribute (gender, race, class…). Required for the "
        "Distribution analysis; used to colour trajectories in the movement view.\n\nThe BUILD step does NOT create "
        "this column — it gives 'actor' but not their attribute. Add a gender / race / class column to the "
        "Social-actors table (by hand, or gender via the gender annotator), then pick it here." + GUI_IO_util.msg_Esc)
    y_multiplier_integer = GUI_IO_util.place_help_button(window, help_button_x_coordinate, y_multiplier_integer, "NLP Suite Help", GUI_IO_util.msg_openOutputFiles)
    return y_multiplier_integer - 1

y_multiplier_integer = help_buttons(window, GUI_IO_util.help_button_x_coordinate, 0)

readMe_message = ("This script analyzes NON-geocodable space — the kinds of place that carry social / symbolic "
    "meaning but do not resolve to map coordinates (house, field, threshold, woods, market, court). It is the "
    "companion to GIS_main (which maps geocodable, real-coordinate space).\n\n"
    "Each place mention is classified into a space TYPE (domestic/interior, field/labour, wild/forest, "
    "threshold/liminal, royal/court, sacred, market/public, water/passage) using the editable gazetteer "
    "lib/symbolic_space_typology.csv (seeded from WordNet). It then produces two complementary analyses:\n\n"
    "  • DYNAMIC (movement): how social actors move between kinds of space over the narrative "
    "(door → house → field → woods), as a directed movement graph. Needs the rows in narrative order.\n\n"
    "  • STATIC (distribution): a cross-tabulation of a social attribute (gender, race, class) against the kind "
    "of space, with a heatmap and chi-square / Cramer's V — which actors appear in which kind of space.\n\n"
    "INPUT — one csv file. It needs a LOCATION column and an ATTRIBUTE column (gender, race, class; and, for the "
    "movement view, an ORDER or sequence/date column). Both analyses read the SAME file — they just use different "
    "columns. You map the columns yourself in the dropdowns.\n\n"
    "WHERE THE CSV COMES FROM. This is essentially a HAND-CODED table — no single tool produces it, because the "
    "ATTRIBUTE is a researcher judgement: race and class have no automatic annotator, and even gender is only "
    "semi-automatic. Two ways to build it:\n"
    "   (1) Code it yourself: any csv with these columns (this is how a hand-coded corpus, e.g. lynching accounts, "
    "works). This is the normal path.\n"
    "   (2) Scaffold from text: the SVO extractor (SVO_main, who-did-what-where) gives you the actor + location "
    "(+ order) rows; you then add the ATTRIBUTE column by hand (the gender annotator can tag gender; race and class "
    "you code).\n\n"
    "IMPORTANT — the unit of analysis is a SOCIAL ACTOR in a kind of space, so it requires an actor. When the input "
    "comes from SVO, the analysis therefore covers only ACTOR-BEARING clauses (those with at least a subject and "
    "verb): a place merely mentioned, with no social actor acting there, is NOT counted. This restriction is by "
    "design — an actorless place is not an observation for the attribute-by-space or actor-movement questions. "
    "If instead you want every place the narrative invokes regardless of actor, feed a NER location table — a "
    "location-level view, without the attribute.")
readMe_command = lambda: GUI_IO_util.display_help_button_info("NLP Suite Help", readMe_message)
GUI_util.GUI_bottom(config_filename, config_input_output_numeric_options, y_multiplier_integer, readMe_command, videos_lookup, videos_options, TIPS_lookup, TIPS_options, IO_setup_display_brief, scriptName)


def clear_selections():
    """Reset this GUI to a fresh state: clear the input csv, the analysis checkboxes,
    the column dropdowns, and disable RUN. The shared bottom dropdowns are reset by
    GUI_util.clear(), which bind_escape_reset chains after this."""
    csv_file_var.set('')           # trace -> refresh_columns() empties the column menus
    GUI_util.inputFilename.set('')
    extra_GUIs_menu_var.set('')
    extra_GUIs_var.set(0)
    extra_GUIs_menu.configure(state='disabled')
    map_var.set(0)
    distribution_var.set(0)
    location_col_var.set('')
    attribute_col_var.set('')
    sequence_col_var.set('')
    GUI_util.run_button.configure(state='disabled')

GUI_util.bind_escape_reset(GUI_util.window, clear_selections)

GUI_util.window.mainloop()
