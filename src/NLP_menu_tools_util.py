"""Tool catalog and search for the NLP_menu_main tool browser.

The menu lists ~100 tools in seven category lists (constants_util.NLP_Suite_*_tools_menu), and pydict
maps each label to the script it opens. This module turns those lists into one catalog the menu can
browse by category or search by typing, so a user no longer has to guess which dropdown holds a tool.

Kept free of Tk and of the suite's import-time side effects so it can be unit-tested
(tests/test_NLP_menu_tools_util.py).
"""

import re

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

# One line under the selected tool saying what it does, written from each tool's Read Me. Search matches it
# too, so a user can find a tool by its purpose ("duplicate", "readability"). A label missing here shows none.
TOOL_DESCRIPTIONS = {
    # Corpus
    "Co-Occurrences VIEWER": "Chart how often words appear together, document by document or over time.",
    "N-grams VIEWER": "Chart how often word sequences appear, document by document or over time.",
    "Shape of stories": "Trace the emotional arc of each story and group stories with similar arcs.",
    "Similarities between documents (via TF-IDF)": "Score how alike documents are, to spot near-duplicates and outliers.",
    "Topic modeling (via MALLET & Gensim)": "Find the topics running through a corpus, with an interactive HTML display.",
    # Corpus / document
    "CORPUS PROFILER. WHAT'S IN YOUR CORPUS? A SWEEPING VIEW.": "Run a battery of analyses with sensible defaults; get an HTML report.",
    "Corpus/document(s) statistics (Sentences, words, lines)": "Count documents, sentences, words, lines and syllables.",
    "Corpus/document(s) statistics (Nouns, verbs, adjectives, pronouns, ...)": "Count nouns, verbs, adjectives, pronouns and other parts of speech.",
    "N-grams & Co-Occurrences": "Find frequent word sequences and words that appear together.",
    "N-grams & Co-occurrences": "Find frequent word sequences and words that appear together.",
    "Parsers & annotators (CoreNLP, spaCy, Stanza)": "Parse texts into a CoNLL table, the input of most linguistic tools.",
    "CoNLL table analyzer - Search the CoNLL table": "Search a parsed CoNLL table for words, tags and grammatical relations.",
    "CoNLL table analyzer - Clause, noun, verb, function words frequencies": "Count clauses, nouns, verbs and function words in a CoNLL table.",
    "CoreNLP annotator - date (normalized NER date)": "Find dates in texts and turn them into a standard date format.",
    "CoreNLP annotator - gender (male & female names; via CoreNLP and dictionaries)": "Tag first names as male or female and highlight them in HTML.",
    "CoreNLP annotator - quote": "Find the quotations in texts.",
    "CoreNLP annotator - coreference (pronominal)": "Link pronouns (he, she, it, they) to the people and things they refer to.",
    "HTML annotator - dictionary, gender, DBpedia, YAGO, WordNet - (All options GUI)": "Highlight in HTML the words that match a dictionary or knowledge graph.",
    "Geographic maps: From texts to maps via Google Earth Pro and Google Maps": "Extract places from texts, geocode them and draw them on maps.",
    "Knowledge graphs: DBpedia, YAGO & Wikipedia": "Tag words that match DBpedia or YAGO classes (people, places, events).",
    "NER (Named Entity Recognition) annotator": "Extract people, places, organizations, dates and other named entities.",
    "Narrative analysis (ALL options GUI)": "Extract who did what to whom, when and where, and visualize the stories.",
    "Semantic analysis": "Word senses, semantic roles, document similarity and clustering.",
    "Syntactic analysis (ALL)": "Parse sentences and analyze grammatical form and structure.",
    "Sentiments/emotions (ALL options GUI)": "Every sentiment and emotion tool in the Suite, in one place.",
    "Sentiment analysis (dictionary options: ANEW, hedonometer, SentiWordNet, VADER)": "Score sentiment, arousal and dominance with word lists.",
    "Sentiment analysis (neural network/tensor options: BERT, spaCy, Stanford CoreNLP, Stanza)": "Score sentence sentiment with trained neural models.",
    "SVO (Subject-Verb-Object) extractor & visualization": "Extract who did what to whom; draw the results as networks and maps.",
    "Wordclouds (ALL options GUI)": "Draw word clouds, where bigger words are more frequent.",
    "Word embeddings (Word2Vec) (via BERT & Gensim)": "Find words used in similar contexts and plot them.",
    "Style analysis (ALL options GUI)": "Vocabulary, sentence complexity, readability and other features of style.",
    "Co-Occurrences": "Find words that appear together in the same document or sentence.",
    "Language detection": "Detect the language each document is written in.",
    "N-grams": "Find the most frequent sequences of 1 to 4 words.",
    "N-grams search": "Search texts for specific word sequences.",
    "N-grams/Co-Occurrences VIEWER": "Chart how often word sequences and co-occurrences appear over time.",
    "Nominalization": "Find nouns made from verbs ('the lynching' instead of 'they lynched').",
    "Sentence complexity": "Measure how complex each sentence is and chart it across the text.",
    "Sentence/text readability (via textstat)": "Score how easy each sentence and text is to read.",
    "Similarities between words (Levenshtein distance)": "Find words spelled almost alike, by edit distance.",
    "Spelling checkers": "Find misspelled and unusual words.",
    "Spelling checker cleaner (Find & Replace string)": "Fix misspellings across files with find & replace.",
    "Who wrote the text? Man or woman? (via Gender guesser)": "Opens a website that guesses the author's gender from a text sample.",
    "Search (ALL options GUI)": "Every search tool in the Suite, in one place.",
    "Search CoNLL table": "Search a parsed CoNLL table for words, tags and grammatical relations.",
    "Search text file(s) for n-grams & co-occurrences": "Search texts for word sequences and words that appear together.",
    "Search text file(s) for words/collocations": "Search texts for words and phrases, with the sentences they appear in.",
    # Sentence
    "Sentence analysis (ALL options GUI)": "Sentence length, complexity, readability and trees, sentence by sentence.",
    # Data & files
    "Data manipulation (ALL options GUI)": "Merge, append, filter, sort and reshape csv files.",
    "File handler (ALL options GUI)": "Every file-handling tool in the Suite, in one place.",
    "Sample corpus (ALL options GUI)": "Draw a sample of documents from a corpus.",
    "File checker (file name)": "Check that file names follow a pattern (e.g., a date in each name).",
    "File classifier (file name) (dumb classifier via embedded date)": "Sort files into subfolders by the date in their names.",
    "File-type converter (csv, docx, pdf, rtf --> txt)": "Convert csv, docx, pdf and rtf files to plain text.",
    "File matcher (file name)": "Find files with the same name but a different type (e.g., pdf vs. txt).",
    "File manager (file name) (List, Rename, Copy, Move, Delete, Count, Split)": "List, rename, copy, move, delete, count or split files by name.",
    "PC-ACE database (via Pandas)": "Convert and chart data from a PC-ACE event-coding database.",
    "SQL database (via SQLite)": "Build an SQLite database from csv files and query it with SQL.",
    # Pre-processing
    "File checker (A pre-processing pipeline of data quality control)": "Run a series of quality checks on a corpus before analyzing it.",
    "File checker (file content)": "Check texts for utf-8 problems and misspellings.",
    "File checker (file content utf-8 encoding)": "Find characters that are not valid utf-8.",
    "File cleaner (file content) (Change to ASCII non-ASCII apostrophes & quotes and % to percent)": "Replace curly quotes and apostrophes, and % with 'percent'.",
    "File cleaner (file content) (Find & Replace string)": "Find and replace text across many files.",
    "File cleaner (file content) (Remove blank lines from txt file(s))": "Delete empty lines from text files.",
    "File cleaner (file content) (Add full stop . at the end of paragraphs without end-of-paragraph punctuation)": "Add a full stop to paragraphs that lack one, so parsers split sentences.",
    "File cleaner (file content) (Pronominal resolution via CoreNLP)": "Rewrite texts with each pronoun replaced by what it refers to.",
    "File finder (file name)": "Find files whose names match a pattern.",
    # Statistics
    "Statistics (csv files)": "Descriptive statistics for the columns of a csv file.",
    # Visualization
    "Excel charts": "Draw bar, line, pie, scatter and radar charts from a csv file.",
    "Geographic maps: From csv file to maps via Google Earth Pro and Google Maps": "Geocode places listed in a csv file and draw them on maps.",
    "Geographic distances between locations": "Compute distances in km and miles between geocoded places.",
    "Animated time-dependent bar plot (Plotly)": "An animated bar chart that steps through time.",
    "Boxplot": "Compare the spread of values across groups.",
    "Colormap chart": "A heatmap: color shows the size of each value in a table.",
    "Multiple bar charts": "Bar charts side by side, to compare groups.",
    "Network graphs (Gephi)": "Draw networks of who is connected to whom.",
    "Sankey flowchart (Plotly)": "Show flows between categories as bands of varying width.",
    "Sunburst pie chart (Plotly)": "A layered pie chart for nested categories.",
    "Treemap (Plotly)": "Nested rectangles sized by value.",
    "Sentence visualization: Dependency tree viewer (png graphs)": "Draw the grammatical tree of a sentence as an image.",
    # Other tools (search only)
    "HTML annotator extractor": "Extract the annotated words from HTML-annotated files.",
    "Statistics (txt files): Number of documents, words, syllables": "Count documents, sentences, words, lines and syllables.",
    "Statistics (txt files): Number of nouns, verbs, adjectives, pronouns, ...": "Count nouns, verbs, adjectives, pronouns and other parts of speech.",
    "Co-Reference PRONOMINAL resolution (via Stanford CoreNLP)": "Link pronouns to the people and things they refer to.",
    "Corpus checker (PC-ACE data)": "Automated checks on whether a corpus is complete and reliable.",
    "Duplicate documents (find near-duplicates via TF-IDF)": "Find documents that are copies or near-copies of one another.",
    "Duplicates (documents that copy one another)": "Find documents that are copies or near-copies of one another.",
    "File classifier (dumb classifier via embedded date) (file name)": "Sort files into subfolders by the date in their names.",
    "File search (file content for words/collocations)": "Search texts for words and phrases, with the sentences they appear in.",
    "File search (file content for n-grams & co-occurrences)": "Search texts for word sequences and words that appear together.",
    "File merger (file content)": "Merge many text files into one.",
    "File splitter (file content)": "Split text files into smaller files.",
    "File splitter (file name)": "Split text files into smaller files.",
    "Find non-related documents": "Find documents that do not belong with the rest of the corpus.",
    "Symbolic space: characters in NON-geocodable space (house, field, forest, threshold)": "Find the symbolic places of a story: house, field, forest, threshold.",
    "Newspaper article/Document titles": "Separate the titles of newspaper articles from their text.",
    "Sentiment analysis": "Score the sentiment of texts, sentence by sentence.",
    "Stanford CoreNLP": "Parse and annotate texts with Stanford CoreNLP.",
    "Dictionary items by sentence index": "List the dictionary words found in each sentence.",
    "utf-8 compliance": "Find characters that are not valid utf-8.",
    "Semantic aggregation (WordNet, VerbNet, FrameNet)": "Group words into broader categories with WordNet, VerbNet or FrameNet.",
}

# words a search ignores, so 'tools for the corpus' is read as 'tools corpus'
_STOP_WORDS = {"a", "an", "and", "for", "in", "my", "of", "on", "the", "to", "with"}


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

    Each entry is a dict: label (the pydict key), name (what the list shows), description, category, section,
    available.
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
                    "description": TOOL_DESCRIPTIONS.get(item, ""),
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
                "description": TOOL_DESCRIPTIONS.get(label, ""),
            }
        )
    return catalog


def entries_in_category(catalog, category):
    return [entry for entry in catalog if entry["category"] == category]


def _words(text):
    """Lower-case words, split at anything that is not a letter or digit: 'file_search_ALL' -> file, search, all."""
    return re.findall(r"[a-z0-9]+", text.lower())


def search(catalog, query, pydict=None):
    """Return the entries matching every word of query, best matches first, each label once.

    A query word matches when it starts a word of the tool's name or label, description, category, section,
    script filename or SEARCH_KEYWORDS: 'sent' finds Sentiment and Sentence, but 'ram' does not find N-grams.
    Common words ('the', 'for') are ignored. Ranking: the name starts with the query, then every query word
    starts a word of the name, then some do, then the rest; ties keep menu order. Available tools rank ahead
    of unavailable ones.
    """
    words = [word for word in _words(query) if word not in _STOP_WORDS] or _words(query)
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
        haystack = _words(
            " ".join(
                [
                    entry["name"],
                    label,
                    entry.get("description", ""),
                    entry["category"],
                    entry["section"],
                    script,
                    SEARCH_KEYWORDS.get(label, ""),
                ]
            )
        )
        if not all(any(text_word.startswith(word) for text_word in haystack) for word in words):
            continue
        seen.add(label)
        name_words = _words(entry["name"])
        in_name = sum(any(name_word.startswith(word) for name_word in name_words) for word in words)
        if " ".join(name_words).startswith(query_text):
            rank = 0
        elif in_name == len(words):
            rank = 1
        elif in_name:
            rank = 2
        else:
            rank = 3
        results.append((not entry["available"], rank, position, entry))
    results.sort(key=lambda result: result[:3])
    return [result[3] for result in results]
