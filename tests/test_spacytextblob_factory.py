"""spaCy's TextBlob sentiment and Objectivity/subjectivity: the "spacytextblob" factory is registered (#1720).

spacytextblob registers the factory only when spacytextblob.spacytextblob is imported; without the import
nlp.add_pipe("spacytextblob") failed with E002 "Can't find factory".
"""

from unittest.mock import MagicMock, patch

import statistics_txt_util


def test_the_pipeline_imports_spacytextblob_before_add_pipe_and_loads_once():
    events = []
    nlp = MagicMock()
    nlp.add_pipe.side_effect = lambda name: events.append(("add_pipe", name))
    factory_module = MagicMock()

    real_import = __import__

    def tracking_import(name, *args, **kwargs):
        if name == "spacytextblob.spacytextblob":
            events.append(("import", name))
            return factory_module
        return real_import(name, *args, **kwargs)

    with (
        patch.object(statistics_txt_util, "_spacy_textblob_nlp", None),
        patch.object(statistics_txt_util.spacy, "load", return_value=nlp) as load,
        patch("builtins.__import__", side_effect=tracking_import),
    ):
        first = statistics_txt_util.spacy_textblob_pipeline()
        second = statistics_txt_util.spacy_textblob_pipeline()
    assert first is nlp and second is nlp
    assert load.call_count == 1
    assert events == [("import", "spacytextblob.spacytextblob"), ("add_pipe", "spacytextblob")]


def test_spacy_util_imports_the_factory_before_add_pipe():
    # spaCy_util is a large GUI-side module; check the source order instead of running spaCy_annotate
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "spaCy_util.py")
    src = open(path, encoding="utf-8").read()
    assert src.index("import spacytextblob.spacytextblob") < src.index('nlp.add_pipe("spacytextblob")')
