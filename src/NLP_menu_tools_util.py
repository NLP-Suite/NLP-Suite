"""Tool catalog and search for the NLP_menu_main tool browser.

The menu lists ~100 tools in seven category lists (constants_util.NLP_Suite_*_tools_menu), and pydict
maps each label to the script it opens. This module turns those lists into one catalog the menu can
browse by category or search by typing, so a user no longer has to guess which dropdown holds a tool.

Kept free of Tk and of the suite's import-time side effects so it can be unit-tested
(tests/test_NLP_menu_tools_util.py).
"""

# Labels whose GUI holds tools the label does not name. Matched by search, never displayed.
SEARCH_KEYWORDS = {
    "Semantic analysis": "word sense induction WSI word sense disambiguation WSD "
    "semantic role labelling SRL document embeddings similarity clustering",
}

OTHER_CATEGORY = "Other tools"

# What the tool list shows for a dropdown label. The labels stay as they are, because they are the
# pydict keys that pick the script; search matches both. A label missing here is shown as it is.
TOOL_NAMES = {
    # Corpus
    "Co-Occurrences VIEWER": "Co-occurrences viewer",
    "N-grams VIEWER": "N-grams viewer",
    # Corpus / document
    "CORPUS PROFILER. WHAT'S IN YOUR CORPUS? A SWEEPING VIEW.": "Corpus profiler: a sweeping view of what's in your corpus",
    "Corpus/document(s) statistics (Sentences, words, lines)": "Statistics: sentences, words, lines",
    "Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)": "Statistics: nouns, verbs, adjectives, pronouns, and more",
    "N-grams & Co-Occurrences": "N-grams & co-occurrences",
    "N-grams & Co-occurrences": "N-grams & co-occurrences",
    "CoNLL table analyzer - Search the CoNLL table": "CoNLL table analyzer: search the table",
    "CoNLL table analyzer - Clause, noun, verb, function words frequencies": "CoNLL table analyzer: clause, noun, verb and function-word frequencies",
    "CoreNLP annotator - date (normalized NER date)": "CoreNLP annotator: dates, normalized",
    "CoreNLP annotator - gender (male & female names; via CoreNLP and dictionaries)": "CoreNLP annotator: gender of male and female names",
    "CoreNLP annotator - quote": "CoreNLP annotator: quotations",
    "CoreNLP annotator - coreference (pronominal)": "CoreNLP annotator: pronoun coreference",
    "HTML annotator - dictionary, gender, DBpedia, YAGO, WordNet - (All options GUI)": "HTML annotator: dictionary, gender, DBpedia, YAGO, WordNet (all options)",
    "Geographic maps: From texts to maps via Google Earth Pro and Google Maps": "Geographic maps from texts (Google Earth Pro, Google Maps)",
    "NER (Named Entity Recognition) annotator": "Named entity recognition (NER)",
    "Narrative analysis (ALL options GUI)": "Narrative analysis (all options)",
    "Syntactic analysis (ALL)": "Syntactic analysis (all options)",
    "Sentiments/emotions (ALL options GUI)": "Sentiments & emotions (all options)",
    "Sentiment analysis (dictionary options: ANEW, hedonometer, SentiWordNet, VADER)": "Sentiment analysis with dictionaries (ANEW, hedonometer, SentiWordNet, VADER)",
    "Sentiment analysis (neural network/tensor options: BERT, spaCy, Stanford CoreNLP, Stanza)": "Sentiment analysis with neural models (BERT, spaCy, CoreNLP, Stanza)",
    "SRL Semantic Role Labeling": "Semantic role labeling (SRL)",
    "SVO (Subject-Verb-Object) extractor & visualization": "Subject-verb-object (SVO) extraction & visualization",
    "Wordclouds (ALL options GUI)": "Word clouds (all options)",
    "Word embeddings (Word2Vec) (via BERT & Gensim)": "Word embeddings: Word2Vec (BERT, Gensim)",
    "Style analysis (ALL options GUI)": "Style analysis (all options)",
    "Co-Occurrences": "Co-occurrences",
    "N-grams/Co-Occurrences VIEWER": "N-grams & co-occurrences viewer",
    "Sentence/text readability (via textstat)": "Readability of sentences and texts (textstat)",
    "Spelling checker cleaner (Find & Replace string)": "Spelling fixes: find & replace",
    "Who wrote the text? Man or woman? (via Gender guesser)": "Was the author a man or a woman? (Gender Guesser website)",
    "Search (ALL options GUI)": "Search (all options)",
    "Search text file(s) for n-grams & co-occurrences": "Search texts for n-grams & co-occurrences",
    "Search text file(s) for words/collocations": "Search texts for words & collocations",
    # Sentence
    "Sentence analysis (ALL options GUI)": "Sentence analysis (all options)",
    # Data & files
    "Data manipulation (ALL options GUI)": "Data manipulation (all options)",
    "File handler (ALL options GUI)": "File handler (all options)",
    "Sample corpus (ALL options GUI)": "Sample a corpus (all options)",
    "File checker (file name)": "Check file names",
    "File classifier (file name) (dumb classifier via embedded date)": "Classify files by the date in their names",
    "File-type converter (csv, docx, pdf, rtf --> txt)": "Convert csv, docx, pdf and rtf files to txt",
    "File matcher (file name)": "Match files by name",
    "File manager (file name) (List, Rename, Copy, Move, Delete, Count, Split)": "File manager: list, rename, copy, move, delete, count, split",
    "PC-ACE database (via Pandas)": "PC-ACE database (pandas)",
    "SQL database (via SQLite)": "SQL database (SQLite)",
    # Pre-processing
    "File checker (A pre-processing pipeline of data quality control)": "Quality-control pipeline for your documents",
    "File checker (file content)": "Check file content",
    "File checker (file content utf-8 encoding)": "Check utf-8 encoding",
    "File cleaner (file content) (Change to ASCII non-ASCII apostrophes & quotes and % to percent)": "Clean: straight quotes and apostrophes, % to 'percent'",
    "File cleaner (file content) (Find & Replace string)": "Clean: find & replace",
    "File cleaner (file content) (Remove blank lines from txt file(s))": "Clean: remove blank lines",
    "File cleaner (file content) (Add full stop . at the end of paragraphs without end-of-paragraph punctuation)": "Clean: end unpunctuated paragraphs with a full stop",
    "File cleaner (file content) (Pronominal resolution via CoreNLP)": "Clean: replace pronouns with what they refer to (CoreNLP)",
    "File finder (file name)": "Find files by name",
    # Statistics
    "Statistics (csv files)": "Statistics for csv files",
    # Visualization
    "Geographic maps: From csv file to maps via Google Earth Pro and Google Maps": "Geographic maps from a csv file (Google Earth Pro, Google Maps)",
    "Animated time-dependent bar plot (Plotly)": "Animated bar chart over time (Plotly)",
    "Sentence visualization: Dependency tree viewer (png graphs)": "Dependency tree viewer (png images)",
    "Sentence visualization: Dynamic sentence network viewer (Gephi graphs)": "Dynamic sentence network viewer (Gephi)",
    # Other tools (search only)
    "Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)": "Pronoun coreference resolution (CoreNLP)",
    "Symbolic space: characters in NON-geocodable space (house, field, forest, threshold)": "Symbolic space: places that cannot be mapped (house, field, forest, threshold)",
}


def _is_separator(item):
    return "-----" in item


def _section_name(item):
    """'Specialized tools -------' -> 'Specialized tools'; a bare '-------' line -> ''."""
    return item.split("-----")[0].strip(" -")


def is_available(label, pydict):
    """A label is available when pydict maps it to a script (an empty script means 'not available yet')."""
    value = pydict.get(label)
    return bool(value) and value[0] != ""


def build_catalog(categories, pydict):
    """Flatten the category lists into catalog entries, in menu order.

    categories: list of (category_name, items), where items are the dropdown labels, including the
    '' spacers and the '--- header ---' lines the dropdowns use to group tools into sections.
    pydict entries that no category lists are appended under OTHER_CATEGORY, so search still finds them.

    Each entry is a dict: label (the pydict key), name (what the list shows), category, section, available.
    """
    catalog = []
    listed = set()
    for category, items in categories:
        section = ""
        for item in items:
            if item == "":
                continue
            if _is_separator(item):
                section = _section_name(item)
                continue
            catalog.append(
                {
                    "label": item,
                    "name": TOOL_NAMES.get(item, item),
                    "category": category,
                    "section": section,
                    "available": is_available(item, pydict),
                }
            )
            listed.add(item)
    for label in pydict:
        if label == "" or _is_separator(label) or label in listed:
            continue
        catalog.append(
            {
                "label": label,
                "name": TOOL_NAMES.get(label, label),
                "category": OTHER_CATEGORY,
                "section": "",
                "available": is_available(label, pydict),
            }
        )
    return catalog


def entries_in_category(catalog, category):
    return [entry for entry in catalog if entry["category"] == category]


def search(catalog, query, pydict=None):
    """Return the entries matching every word of query, best matches first, each label once.

    A word matches the name or the label, its category and section, its script's filename, or its
    SEARCH_KEYWORDS. Ranking: name starts with the query, then a name word starts with a query word,
    then the rest;
    ties keep menu order. Available tools rank ahead of unavailable ones.
    """
    words = query.lower().split()
    if not words:
        return []
    query_text = " ".join(words)
    results = []
    seen = set()
    for position, entry in enumerate(catalog):
        label = entry["label"]
        if label in seen:
            continue
        script = ""
        if pydict and label in pydict and pydict[label]:
            script = str(pydict[label][0])
        haystack = " ".join(
            [entry["name"], label, entry["category"], entry["section"], script, SEARCH_KEYWORDS.get(label, "")]
        ).lower()
        if not all(word in haystack for word in words):
            continue
        seen.add(label)
        name_lower = entry["name"].lower()
        name_words = name_lower.replace("(", " ").replace("/", " ").replace(":", " ").split()
        if name_lower.startswith(query_text):
            rank = 0
        elif any(name_word.startswith(word) for word in words for name_word in name_words):
            rank = 1
        else:
            rank = 2
        results.append((not entry["available"], rank, position, entry))
    results.sort(key=lambda result: result[:3])
    return [result[3] for result in results]
