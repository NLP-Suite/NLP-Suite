"""Parsers & annotators: which CoreNLP annotator a parser choice runs, and '' when the package does not offer it.

With Stanford CoreNLP as the package, run() mapped only "PCFG" and "Neural Network" to an annotator; any other
parser choice (e.g. "Dependency parser", left in the menu from Stanza or spaCy) left the annotator empty and RUN
did nothing, with no message (found 22 Nov 2026 by tests/tool_sweep.py, recipe parser_CoreNLP). run() now warns
when ``CoreNLP_parser_annotator`` returns ''.
"""

import sys
from unittest.mock import MagicMock, patch

# Imported at the top of Stanford_CoreNLP_util but not needed here; CI installs only pytest.
_STUBS = [
    "pycorenlp",
    "Stanford_CoreNLP_clause_util",
    "Stanford_CoreNLP_SVO_enhanced_dependencies_util",
    "file_splitter_ByLength_util",
    "file_splitter_merged_txt_util",
    "parsers_annotators_visualization_util",
]
with patch.dict(sys.modules, {name: MagicMock() for name in _STUBS}):
    import Stanford_CoreNLP_util


def test_the_two_CoreNLP_parsers():
    assert (
        Stanford_CoreNLP_util.CoreNLP_parser_annotator("Probabilistic Context Free Grammar (PCFG)") == "parser (pcfg)"
    )
    assert Stanford_CoreNLP_util.CoreNLP_parser_annotator("Neural Network") == "parser (nn)"


def test_parsers_of_other_packages_give_nothing():
    for choice in ("Dependency parser", "Constituency parser", ""):
        assert Stanford_CoreNLP_util.CoreNLP_parser_annotator(choice) == ""


def test_every_parser_offered_for_CoreNLP_maps_to_an_annotator():
    # the list NLP_setup_package_language_main and config_util offer for Stanford CoreNLP
    for choice in ("Neural Network", "Probabilistic Context Free Grammar (PCFG)"):
        assert Stanford_CoreNLP_util.CoreNLP_parser_annotator(choice) != ""
