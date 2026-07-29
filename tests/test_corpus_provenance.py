"""Reuse must not cross corpora.

The profiler's reuse probes search the output directory for a table with the right filename and the
right columns. Nothing in that ties a table to the text it was built from — "a prior run on THIS
corpus" is an assumption resting on one output directory per corpus. Run a coreference-resolved copy
of a corpus while keeping the original's output directory and the probe finds the ORIGINAL's table,
matches on name and columns, passes the module-fingerprint check because no code changed, and reuses
it. The two runs then agree perfectly, because they are the same numbers.

These tests pin the guard that refuses that reuse.
"""
import importlib.util
import json
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

# conftest stubs the heavy libraries for the session; corpus_profiler_util is the module under test,
# so load the real source under a private name. Its own imports still resolve against the stubs.
_spec = importlib.util.spec_from_file_location('_real_corpus_profiler_util',
                                               os.path.join(_SRC, 'corpus_profiler_util.py'))
prof = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(prof)
finally:
    # sibling modules chdir into src/ at import; put the working directory back so tmp_path and any
    # later test using a relative path still resolve where they expect.
    os.chdir(_cwd)


def _corpus(tmp_path, name, files):
    d = tmp_path / name
    d.mkdir()
    for filename, text in files.items():
        (d / filename).write_text(text, encoding='utf-8')
    return {'inputDir': str(d), 'inputFilename': ''}


class TestCorpusFingerprint:
    def test_same_corpus_gives_the_same_digest(self, tmp_path):
        files = {'a.txt': 'Harry waved his wand.', 'b.txt': 'Ron said nothing.'}
        one = _corpus(tmp_path, 'raw', files)
        two = _corpus(tmp_path, 'raw_copy', files)
        # a moved or renamed corpus is still the same corpus: the path is NOT in the digest
        assert prof.corpus_fingerprint(one)[0] == prof.corpus_fingerprint(two)[0]

    def test_a_coreferenced_copy_is_a_different_corpus(self, tmp_path):
        raw = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand. He smiled.'})
        cor = _corpus(tmp_path, 'cor', {'a.txt': 'Harry waved Harry wand. Harry smiled.'})
        assert prof.corpus_fingerprint(raw)[0] != prof.corpus_fingerprint(cor)[0]

    def test_an_added_document_changes_the_digest(self, tmp_path):
        one = _corpus(tmp_path, 'one', {'a.txt': 'x' * 40})
        two = _corpus(tmp_path, 'two', {'a.txt': 'x' * 40, 'b.txt': 'y' * 40})
        assert prof.corpus_fingerprint(one)[0] != prof.corpus_fingerprint(two)[0]

    def test_the_label_is_the_folder_name(self, tmp_path):
        c = _corpus(tmp_path, 'Harry Potter', {'a.txt': 'text'})
        assert prof.corpus_fingerprint(c)[1] == 'Harry Potter'

    def test_a_single_input_file_is_fingerprinted(self, tmp_path):
        f = tmp_path / 'only.txt'
        f.write_text('one document', encoding='utf-8')
        fp, label = prof.corpus_fingerprint({'inputDir': '', 'inputFilename': str(f)})
        assert fp and label == 'only.txt'

    def test_nothing_to_fingerprint_is_empty_not_an_error(self):
        assert prof.corpus_fingerprint({'inputDir': '', 'inputFilename': ''}) == ('', '')
        assert prof.corpus_fingerprint(None) == ('', '')

    def test_a_sidecar_dropped_beside_the_corpus_does_not_change_it(self, tmp_path):
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        before = prof.corpus_fingerprint(c)[0]
        (tmp_path / 'raw' / 'a.txt.provenance.json').write_text('{}', encoding='utf-8')
        assert prof.corpus_fingerprint(c)[0] == before


class TestReuseAcrossCorpora:
    def _table(self, tmp_path, name='NLP_SVO_Stanza_Dir_corpus.csv'):
        p = tmp_path / name
        p.write_text('Subject,Verb,Object\nHarry,waved,wand\n', encoding='utf-8')
        return str(p)

    def test_a_table_is_reused_for_the_corpus_that_made_it(self, tmp_path):
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo', c)
        ok, why = prof.provenance_is_current(table, 'svo', c)
        assert ok and why == ''

    def test_a_table_is_REFUSED_for_a_different_corpus(self, tmp_path):
        raw = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand. He smiled.'})
        cor = _corpus(tmp_path, 'coreferenced', {'a.txt': 'Harry waved Harry wand. Harry smiled.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo', raw)
        ok, why = prof.provenance_is_current(table, 'svo', cor)
        assert not ok
        # the message has to name both corpora, or the user cannot tell what happened
        assert 'DIFFERENT corpus' in why and 'raw' in why and 'coreferenced' in why

    def test_the_stamp_records_the_corpus(self, tmp_path):
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo', c)
        with open(table + prof.PROVENANCE_SUFFIX, encoding='utf-8') as fh:
            stamped = json.load(fh)
        assert stamped['corpus'] == prof.corpus_fingerprint(c)[0]
        assert stamped['corpus_label'] == 'raw'
        assert stamped['kind'] == 'svo' and stamped['fingerprint']

    def test_an_older_stamp_without_a_corpus_is_reused_but_says_so(self, tmp_path):
        """Refusing these would re-parse every profile built before this change, for a risk that is
        usually theoretical. It must be spoken, though, never silent."""
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo')          # no corpus recorded, as before this change
        ok, why = prof.provenance_is_current(table, 'svo', c)
        assert ok and 'no corpus recorded' in why

    def test_changed_code_still_refuses_regardless_of_corpus(self, tmp_path):
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo', c)
        with open(table + prof.PROVENANCE_SUFFIX, encoding='utf-8') as fh:
            stamped = json.load(fh)
        stamped['fingerprint'] = 'deadbeefdeadbeef'
        with open(table + prof.PROVENANCE_SUFFIX, 'w', encoding='utf-8') as fh:
            json.dump(stamped, fh)
        ok, why = prof.provenance_is_current(table, 'svo', c)
        assert not ok and 'code that produced it has changed' in why

    def test_no_stamp_at_all_is_reused_and_says_so(self, tmp_path):
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        ok, why = prof.provenance_is_current(table, 'svo', c)
        assert ok and 'no provenance stamp' in why

    def test_the_check_is_skipped_when_no_corpus_is_passed(self, tmp_path):
        """Callers that have no corpus context must keep working exactly as before."""
        c = _corpus(tmp_path, 'raw', {'a.txt': 'Harry waved his wand.'})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], 'svo', c)
        ok, why = prof.provenance_is_current(table, 'svo')
        assert ok and why == ''
