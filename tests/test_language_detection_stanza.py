"""Language detection uses Stanza's language identifier only, not its full parser (#1724).

MultilingualPipeline() ran tokenize, POS, lemma and both parsers on every document (about a minute each)
to use only doc.lang.
"""

import importlib.util
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "file_spell_checker_util.py")


@pytest.fixture(scope="module")
def fsc():
    # a large module with many third-party imports: stub, while it loads, whatever is missing or stubbed
    stubs = {}
    for name in (
        "spacy",
        "spacy.language",
        "spacy_langdetect",
        "stanza",
        "textblob",
        "autocorrect",
        "fuzzywuzzy",
        "langdetect",
        "langid",
        "langid.langid",
        "spellchecker",
        "pandas",
    ):
        if name not in sys.modules or isinstance(sys.modules[name], MagicMock):
            stubs[name] = MagicMock()
    with patch.dict(sys.modules, stubs):
        for _ in range(30):
            spec = importlib.util.spec_from_file_location("_fsc_langid", _PATH)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                break
            except ModuleNotFoundError as e:
                if not e.name or e.name in sys.modules:
                    raise
                sys.modules[e.name] = MagicMock()
        yield module


def test_only_the_langid_processor_is_loaded(fsc):
    with patch.object(fsc, "stanza") as stanza:
        fsc.stanza_langid_pipeline()
    stanza.Pipeline.assert_called_once_with(lang="multilingual", processors="langid", verbose=False)
    stanza.download.assert_not_called()


def test_the_model_is_downloaded_when_missing(fsc):
    with patch.object(fsc, "stanza") as stanza:
        stanza.Pipeline.side_effect = [FileNotFoundError("no model"), MagicMock()]
        fsc.stanza_langid_pipeline()
    stanza.download.assert_called_once_with(lang="multilingual", verbose=False)
    assert stanza.Pipeline.call_count == 2
