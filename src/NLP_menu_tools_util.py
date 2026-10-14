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

    Each entry is a dict: label, category, section, available.
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
                {"label": item, "category": category, "section": section, "available": is_available(item, pydict)}
            )
            listed.add(item)
    for label in pydict:
        if label == "" or _is_separator(label) or label in listed:
            continue
        catalog.append(
            {"label": label, "category": OTHER_CATEGORY, "section": "", "available": is_available(label, pydict)}
        )
    return catalog


def entries_in_category(catalog, category):
    return [entry for entry in catalog if entry["category"] == category]


def search(catalog, query, pydict=None):
    """Return the entries matching every word of query, best matches first, each label once.

    A word matches the label, its category and section, its script's filename, or its SEARCH_KEYWORDS.
    Ranking: label starts with the query, then a label word starts with a query word, then the rest;
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
            [label, entry["category"], entry["section"], script, SEARCH_KEYWORDS.get(label, "")]
        ).lower()
        if not all(word in haystack for word in words):
            continue
        seen.add(label)
        label_lower = label.lower()
        label_words = label_lower.replace("(", " ").replace("/", " ").split()
        if label_lower.startswith(query_text):
            rank = 0
        elif any(label_word.startswith(word) for word in words for label_word in label_words):
            rank = 1
        else:
            rank = 2
        results.append((not entry["available"], rank, position, entry))
    results.sort(key=lambda result: result[:3])
    return [result[3] for result in results]
