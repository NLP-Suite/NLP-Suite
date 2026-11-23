# Logic of the Syntactic analysis GUI (syntactic_analysis_ALL_main.py) that can be tested without the GUI

# The GUI that each entry of the "GUIs available for more analyses" menu opens
EXTRA_GUIS = {
    "Corpus statistics (Open GUI)": "statistics_txt_main.py",
    "N-grams & Co-Occurrences (Open GUI)": "NGrams_CoOccurrences_main.py",
    "Corpus Profiler (Open GUI)": "corpus_profiler_main.py",
}


def extra_GUI_script(menu_value):
    return EXTRA_GUIS.get(menu_value, "")
