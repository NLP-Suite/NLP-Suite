"""The NLP_menu tool browser: building one catalog from the category dropdowns, and searching it.

The menu used to hide ~100 tools in seven dropdowns, so finding a tool meant guessing its dropdown.
NLP_menu_tools_util is the pure part of the replacement: the catalog the browser lists by category,
and the search that matches what a user types against labels, scripts and keywords.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import NLP_menu_tools_util as tools  # noqa: E402

PYDICT = {
    "": ["", 0],
    "Topic modeling (via MALLET & Gensim)": ["topic_modeling_main.py", 1],
    "Shape of stories": ["shape_of_stories_main.py", 1],
    "Semantic analysis": ["semantic_analysis_main.py", 1],
    "SRL Semantic Role Labeling": ["", 0],
    "Search (ALL options GUI)": ["file_search_ALL_main.py", 1],
    "Sentiment analysis": ["sentiment_analysis_main.py", 1],
    "Duplicates (documents that copy one another)": ["corpus_checker_PCACE_data_main.py", 1],
    "------------------": ["", 2],
}

CATEGORIES = [
    ("Corpus", ("Shape of stories", "Topic modeling (via MALLET & Gensim)")),
    (
        "Corpus/document",
        (
            "Fundamental NLP tools -----------------------",
            "",
            "Search (ALL options GUI)",
            "",
            "Specialized tools ---------------------------",
            "",
            "Semantic analysis",
            "SRL Semantic Role Labeling",
            "Hedge/uncertainty annotator",
        ),
    ),
    ("Pre-processing", ("Search (ALL options GUI)", "", "-------------------------", "", "Shape of stories")),
]


def labels(entries):
    return [entry["label"] for entry in entries]


class TestBuildCatalog:
    def test_spacers_and_headers_are_not_tools(self):
        catalog = tools.build_catalog(CATEGORIES, PYDICT)
        assert "" not in labels(catalog)
        assert not any("-----" in label for label in labels(catalog))

    def test_a_header_names_the_section_of_the_tools_below_it(self):
        corpus_document = tools.entries_in_category(tools.build_catalog(CATEGORIES, PYDICT), "Corpus/document")
        sections = {entry["label"]: entry["section"] for entry in corpus_document}
        assert sections["Search (ALL options GUI)"] == "Fundamental NLP tools"
        assert sections["Semantic analysis"] == "Specialized tools"

    def test_a_bare_dashed_line_ends_the_section(self):
        pre_processing = tools.entries_in_category(tools.build_catalog(CATEGORIES, PYDICT), "Pre-processing")
        assert [entry["section"] for entry in pre_processing] == ["", ""]

    def test_a_tool_listed_in_two_categories_appears_in_both(self):
        catalog = tools.build_catalog(CATEGORIES, PYDICT)
        assert labels(tools.entries_in_category(catalog, "Pre-processing")) == [
            "Search (ALL options GUI)",
            "Shape of stories",
        ]
        assert "Search (ALL options GUI)" in labels(tools.entries_in_category(catalog, "Corpus/document"))

    def test_an_empty_script_or_a_label_missing_from_pydict_is_unavailable(self):
        availability = {entry["label"]: entry["available"] for entry in tools.build_catalog(CATEGORIES, PYDICT)}
        assert availability["Semantic analysis"] is True
        assert availability["SRL Semantic Role Labeling"] is False
        assert availability["Hedge/uncertainty annotator"] is False

    def test_pydict_tools_in_no_category_are_kept_under_other_tools(self):
        other = tools.entries_in_category(tools.build_catalog(CATEGORIES, PYDICT), tools.OTHER_CATEGORY)
        assert labels(other) == ["Sentiment analysis", "Duplicates (documents that copy one another)"]


class TestSearch:
    catalog = tools.build_catalog(CATEGORIES, PYDICT)

    def find(self, query):
        return labels(tools.search(self.catalog, query, PYDICT))

    def test_an_empty_query_finds_nothing(self):
        assert self.find("   ") == []

    def test_matching_ignores_case(self):
        assert self.find("TOPIC") == ["Topic modeling (via MALLET & Gensim)"]

    def test_every_word_must_match(self):
        assert self.find("topic mallet") == ["Topic modeling (via MALLET & Gensim)"]
        assert self.find("topic stories") == []

    def test_a_tool_in_two_categories_is_listed_once(self):
        assert self.find("search all") == ["Search (ALL options GUI)"]

    def test_the_script_filename_matches(self):
        assert self.find("file_search_ALL") == ["Search (ALL options GUI)"]

    def test_keywords_find_a_tool_its_label_does_not_name(self):
        # word sense induction lives inside the Semantic analysis GUI
        assert self.find("WSI") == ["Semantic analysis"]
        assert self.find("word sense") == ["Semantic analysis"]

    def test_tools_in_no_category_are_found(self):
        assert self.find("duplicate") == ["Duplicates (documents that copy one another)"]

    def test_a_label_starting_with_the_query_ranks_first(self):
        assert self.find("se")[:3] == ["Search (ALL options GUI)", "Semantic analysis", "Sentiment analysis"]

    def test_a_query_word_must_start_a_word(self):
        # 'ram' sits inside 'N-grams' and 'Paragraphs'; matching it there filled the list with noise
        catalog = tools.build_catalog([("Tools", ("N-grams", "Paragraphs", "RAM usage"))], {})
        assert labels(tools.search(catalog, "ram")) == ["RAM usage"]
        # 'N-grams' is split at the hyphen, so 'grams' starts a word
        assert labels(tools.search(catalog, "grams")) == ["N-grams"]

    def test_punctuation_in_the_query_splits_words(self):
        catalog = tools.build_catalog([("Tools", ("N-grams & Co-Occurrences", "Topic modeling"))], {})
        assert labels(tools.search(catalog, "co-occ")) == ["N-grams & Co-Occurrences"]

    def test_common_words_are_ignored(self):
        assert self.find("the topic of a corpus") == ["Topic modeling (via MALLET & Gensim)"]

    def test_the_description_matches(self):
        catalog = tools.build_catalog([("Tools", ("Shape of stories", "Topic modeling (via MALLET & Gensim)"))], PYDICT)
        assert labels(tools.search(catalog, "emotional arc")) == ["Shape of stories"]

    def test_all_words_in_the_name_outrank_some(self):
        catalog = tools.build_catalog([("Tools", ("Search CoNLL table", "Search (ALL options GUI)"))], PYDICT)
        # 'all' starts no word of 'Search CoNLL table', so only the second tool matches
        assert labels(tools.search(catalog, "search all")) == ["Search (ALL options GUI)"]
        catalog = tools.build_catalog([("Search tools", ("Search CoNLL table", "Search (ALL options GUI)"))], PYDICT)
        # 'tools' matches both through the category; 'conll' is in the name of the first only
        assert labels(tools.search(catalog, "search tools conll")) == ["Search CoNLL table"]

    def test_unavailable_tools_rank_last(self):
        assert self.find("semantic") == ["Semantic analysis", "SRL Semantic Role Labeling"]


class TestToolNames:
    catalog = tools.build_catalog(CATEGORIES, PYDICT)

    def name_of(self, label):
        return next(entry["name"] for entry in self.catalog if entry["label"] == label)

    def test_a_renamed_label_shows_its_readable_name(self):
        assert self.name_of("SRL Semantic Role Labeling") == "Semantic role labeling (SRL)"

    def test_a_label_without_a_new_name_shows_as_it_is(self):
        assert self.name_of("Shape of stories") == "Shape of stories"

    def test_search_matches_the_new_name_and_the_old_label(self):
        # 'role' only in the new name's word order; 'SRL' leads the old label
        assert labels(tools.search(self.catalog, "role labeling", PYDICT)) == ["SRL Semantic Role Labeling"]
        # Semantic analysis matches too, through its SRL keyword
        assert labels(tools.search(self.catalog, "srl semantic", PYDICT)) == [
            "Semantic analysis",
            "SRL Semantic Role Labeling",
        ]

    def test_ranking_uses_the_name(self):
        # the label 'CoreNLP annotator - quote' is shown as 'CoreNLP annotator: quotations'; a name starting with
        # the query outranks one that only contains it
        catalog = tools.build_catalog([("Tools", ("Search CoNLL table", "CoreNLP annotator - quote"))], {})
        assert labels(tools.search(catalog, "quot")) == ["CoreNLP annotator - quote"]
        catalog = tools.build_catalog([("Tools", ("Find quotes", "Quotations"))], {})
        assert labels(tools.search(catalog, "quot")) == ["Quotations", "Find quotes"]

    def test_every_renamed_label_is_a_real_menu_label(self):
        # a typo in a TOOL_NAMES key would silently leave the old label on screen
        import re

        import constants_util

        listed = set()
        for name in dir(constants_util):
            if name.startswith("NLP_Suite_") and name.endswith("_menu"):
                listed.update(getattr(constants_util, name))
        menu = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "NLP_menu_main.py")
        with open(menu, encoding="utf-8") as f:
            source = f.read()
        # pydict keys are written pydict["..."] or pydict['...'] at the start of a line
        for double, single in re.findall(r"""^pydict\[(?:"([^"]*)"|'([^']*)')\]""", source, re.M):
            listed.add(double or single)
        assert set(tools.TOOL_NAMES) - listed == set()


class TestToolDescriptions:
    def test_every_described_label_is_a_real_menu_label(self):
        # same check as for TOOL_NAMES: a typo would leave a tool without its description
        import re

        import constants_util

        listed = set()
        for name in dir(constants_util):
            if name.startswith("NLP_Suite_") and name.endswith("_menu"):
                listed.update(getattr(constants_util, name))
        menu = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "NLP_menu_main.py")
        with open(menu, encoding="utf-8") as f:
            source = f.read()
        for double, single in re.findall(r"""^pydict\[(?:"([^"]*)"|'([^']*)')\]""", source, re.M):
            listed.add(double or single)
        assert set(tools.TOOL_DESCRIPTIONS) - listed == set()

    def test_a_catalog_entry_carries_its_description(self):
        catalog = tools.build_catalog([("Corpus", ("Shape of stories", "Unknown tool"))], PYDICT)
        assert catalog[0]["description"] == tools.TOOL_DESCRIPTIONS["Shape of stories"]
        assert catalog[1]["description"] == ""

    def test_descriptions_fit_on_one_line(self):
        assert [label for label, text in tools.TOOL_DESCRIPTIONS.items() if len(text) > 80] == []
