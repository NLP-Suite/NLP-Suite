"""process_json_coref: the resolved text is built without crashing when a period comes first.

get_resolved skips a ". " that would follow another period, and checked result[-1] to find one. When ". " was the
first token output, result was still '' and the check raised IndexError: string index out of range, which ended a
958-document SVO + coreference run on its 86th file.
"""

import sys
from unittest.mock import MagicMock, patch

# Imported at the top of Stanford_CoreNLP_util but not needed by the json routines; CI installs only pytest.
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


def _token(word, lemma=None, pos="NN", after=" "):
    return {"word": word, "lemma": lemma or word, "pos": pos, "after": after}


def _resolve(sentences, corefs=None):
    json = {"sentences": [{"tokens": tokens} for tokens in sentences], "corefs": corefs or {}}
    return Stanford_CoreNLP_util.process_json_coref("config.csv", 1, "doc.txt", 0, json)


def test_period_first_does_not_crash():
    text = _resolve([[_token(".", pos=".")], [_token("Rain", pos="NN"), _token("fell", "fall", "VBD", "")]])
    assert text == ". Rain fell"


def test_period_after_period_is_still_skipped():
    text = _resolve([[_token("Stop", pos="VB", after=""), _token(".", pos=".", after="")], [_token(".", pos=".")]])
    assert text == "Stop."


def test_pronoun_takes_its_antecedent():
    corefs = {
        "1": [
            {"text": "Mary", "type": "PROPER", "sentNum": 1, "startIndex": 1},
            {"text": "she", "type": "PRONOMINAL", "sentNum": 2, "startIndex": 1},
        ]
    }
    text = _resolve(
        [
            [_token("Mary", pos="NNP"), _token("left", "leave", "VBD", ""), _token(".", pos=".")],
            [_token("she", "she", "PRP"), _token("returned", "return", "VBD", ""), _token(".", pos=".", after="")],
        ],
        corefs,
    )
    assert text == "Mary left. Mary returned."
