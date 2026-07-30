"""What the topic modeler says about corpus size.

It used to say "Topic modeling requires a large number of files (in the hundreds at least) to
produce valid results" and block, by default, under 50 files. Two faults. The number is not a
property of the method - a file is not a fixed quantity of text, and MALLET's own tutorial corpus is
under twenty documents. And it refused work the user had asked for on the strength of it.

What is true is narrower: per-document topic proportions are estimated per document, so with very
few documents the fitted topics are unstable across runs. The remedy is splitting long documents,
not reaching a file count.
"""
import importlib.util
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

# corpus_size_advice is pure - it takes a number and returns two strings - but it lives in a module
# that imports the whole topic-modeling stack at import time. conftest stubs the top-level packages;
# `from gensim.utils import simple_preprocess` needs the DOTTED submodules stubbed too.
from unittest.mock import MagicMock                                          # noqa: E402
for _mod in ('gensim', 'gensim.corpora', 'gensim.utils', 'gensim.models',
             'spacy', 'pyLDAvis', 'pyLDAvis.gensim', 'pyLDAvis.gensim_models',
             'matplotlib', 'matplotlib.pyplot', 'pandas'):
    sys.modules.setdefault(_mod, MagicMock())

_spec = importlib.util.spec_from_file_location('_real_topic_util',
                                              os.path.join(_SRC, 'topic_modeling_gensim_util.py'))
tm = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(tm)
finally:
    os.chdir(_cwd)

advice = tm.corpus_size_advice


class TestWhenItRefuses:
    def test_no_documents_is_an_error(self):
        level, msg = advice(0)
        assert level == 'error'
        assert 'no .txt files' in msg

    def test_one_document_is_an_error_that_explains_why(self):
        """Not "you need hundreds" - the actual reason: there is nothing to compare it with."""
        level, msg = advice(1)
        assert level == 'error'
        assert 'ACROSS documents' in msg
        assert 'split' in msg.lower()


class TestWhenItAdvises:
    def test_a_small_corpus_advises_but_does_NOT_refuse(self):
        level, msg = advice(20)
        assert level == 'advice'
        assert 'This will run' in msg

    def test_the_advice_names_the_real_risk(self):
        """Instability across runs, which is checkable - not an unsourced threshold."""
        msg = advice(20)[1]
        assert 'shift from one run to the next' in msg
        assert 'run it twice' in msg

    def test_it_does_not_claim_a_number_of_files_is_required(self):
        msg = advice(20)[1]
        low = msg.lower()
        assert 'hundreds' not in low
        assert 'requires a large number' not in low

    def test_it_says_what_actually_matters(self):
        msg = advice(20)[1]
        assert 'amount of text' in msg
        assert 'not the number of files' in msg

    def test_the_count_is_reported_back(self):
        assert '37' in advice(37)[1]


class TestWhenItSaysNothing:
    def test_a_large_corpus_gets_no_message(self):
        assert advice(200) == ('', '')

    def test_the_threshold_itself(self):
        assert advice(tm._FEW_DOCUMENTS)[0] == ''
        assert advice(tm._FEW_DOCUMENTS - 1)[0] == 'advice'


class TestMalletsTutorialCorpus:
    def test_under_twenty_documents_runs_with_advice_not_a_refusal(self):
        """The case that started this: MALLET ships a tutorial corpus of fewer than 20 documents.
        The old dialog defaulted to No and would have stopped it."""
        level, _msg = advice(19)
        assert level == 'advice'
