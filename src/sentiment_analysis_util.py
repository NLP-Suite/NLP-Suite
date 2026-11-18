"""Bookkeeping for sentiment_analysis_main.run(): which algorithms a menu choice runs, and what each one returned.

Kept out of the GUI so it can be tested without a window (#1719, #1720).
"""

import os

# what '*' runs (Character Emotion Arcs is separate: it has its own checkbox)
ALL_ALGORITHMS = (
    "BERT",
    "spaCy",
    "CoreNLP",
    "Stanza",
    "ANEW",
    "hedonometer",
    "NRC",
    "SentiWordNet",
    "VADER",
)

# (text in the menu label, algorithm). Order matters: the first match wins, and
# "Character Emotion Arcs (NER + NRC)" contains "NRC", so it must come before NRC (#1719).
_LABELS = (
    ("Character Emotion Arcs", "Character Emotion Arcs"),
    ("BERT", "BERT"),
    ("spaCy", "spaCy"),
    ("Stanford CoreNLP", "CoreNLP"),
    ("Stanza", "Stanza"),
    ("SentiWordNet", "SentiWordNet"),
    ("ANEW", "ANEW"),
    ("NRC", "NRC"),
    ("hedonometer", "hedonometer"),
    ("VADER", "VADER"),
)


def selected_algorithms(menu_value):
    """The set of algorithms that a value of the algorithm menu runs; an empty set for a heading or blank line."""
    if menu_value == "*":
        return set(ALL_ALGORITHMS)
    for text, algorithm in _LABELS:
        if text in menu_value:
            return {algorithm}
    return set()


def add_outputs(outputFiles, filesToOpen):
    """Add what an algorithm returned to filesToOpen. Return its first file, or "" when it produced nothing.

    Annotators return None, a single path, or a list that can be empty: spaCy returned [] when its
    sentiment pipeline failed to load, and outputFiles[0] then stopped the whole '*' run (#1720).
    """
    if not outputFiles:
        return ""
    if isinstance(outputFiles, str):
        filesToOpen.append(outputFiles)
        return outputFiles
    filesToOpen.extend(outputFiles)
    return outputFiles[0]


def failed_algorithms_message(failed):
    """The warning shown at the end of a run when some algorithms produced no output; "" when none failed."""
    if not failed:
        return ""
    return (
        "These sentiment analysis algorithms produced no output:\n\n   "
        + "\n   ".join(failed)
        + "\n\nThe other algorithms ran. Please, check the command line/terminal for the reason, or run the"
        " algorithms above one at a time."
    )


def sentiment_scores_ready(sentimentAnalysis, sentiment_scores_input, inputFilename, inputDir):
    """Shape of Stories: whether step 2 (HC, SVD, NMF, best k) has sentiment scores to read.

    Either step 1 wrote a scores csv (it then replaces the txt input), or the input itself is a csv or a folder
    with csv files. Without this check the txt folder went on to the vectorizer, which read it as a csv and
    stopped with a pandas ParserError (#1722).
    """
    if sentimentAnalysis:
        return sentiment_scores_input not in ("", inputFilename, inputDir)
    if os.path.isdir(sentiment_scores_input):
        return any(f.lower().endswith(".csv") for f in os.listdir(sentiment_scores_input))
    return sentiment_scores_input.lower().endswith(".csv")
