"""Reuse for EVERY analysis, from one rule.

Eight analyses had a hand-written probe - the parses, where the hours were - and the other fifteen
re-ran from scratch every time. Defended as "the rest are cheap", which is true of any one of them
and false of all of them together: after the disk filled on 30 July, a re-run spent an afternoon
recomputing work already sitting on disk, including BERT embeddings.

A probe guesses which file belongs to an analysis, by name and columns, and each new one is another
chance to guess wrong. The manifest does not guess: the run that produced a file wrote down which
analysis produced it. So the rule needs no per-analysis knowledge, cannot mismatch, and covers an
analysis added tomorrow with no extra code.
"""
import importlib.util
import json
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

_spec = importlib.util.spec_from_file_location('_real_profiler_reuse',
                                              os.path.join(_SRC, 'corpus_profiler_util.py'))
prof = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(prof)
finally:
    os.chdir(_cwd)


def a_corpus(tmp_path, name='HPbooks', docs=('a.txt', 'b.txt')):
    d = tmp_path / name
    d.mkdir()
    for doc in docs:
        (d / doc).write_text('Harry waved his wand.', encoding='utf-8')
    return {'inputDir': str(d), 'inputFilename': '', 'outputDir': str(tmp_path / 'out')}


def an_output(ctx):
    os.makedirs(ctx['outputDir'], exist_ok=True)
    return ctx['outputDir']


def a_result(out, aid='ngrams', files=('table.csv',), error='', size=10):
    made = []
    for f in files:
        p = os.path.join(out, f)
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write('x' * size)
        made.append(p)
    return {'id': aid, 'category': 'counts', 'label': aid, 'kind': 'batch',
            'files': made, 'error': error}


class TestTheManifestRecordsTheCorpus:
    def test_written_and_read_back(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof.save_manifest(out, [a_result(out)], ctx)
        fp, label = prof.manifest_corpus(out)
        assert fp == prof.corpus_fingerprint(ctx)[0]
        assert label == 'HPbooks'

    def test_no_manifest_is_not_an_error(self, tmp_path):
        assert prof.manifest_corpus(str(tmp_path)) == ('', '')

    def test_it_is_written_whole_or_not_at_all(self, tmp_path):
        """A manifest truncated by a full disk is worse than none: the next run would read a
        half-list as the complete story."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof.save_manifest(out, [a_result(out)], ctx)
        path = os.path.join(out, prof.MANIFEST_NAME)
        with open(path, encoding='utf-8') as fh:
            json.load(fh)                       # parses, so it is complete
        assert not os.path.isfile(path + '.tmp')


class TestReusableFromManifest:
    def test_a_recorded_analysis_is_reused(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams')]
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True)

    def test_ANY_analysis_id_works_including_one_that_never_had_a_probe(self, tmp_path):
        """The whole point: embeddings, topics, iconicity, an analysis added next year."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        for aid in ('embeddings', 'topics', 'iconic', 'yule', 'tfidf', 'something_new'):
            previous = [a_result(out, aid, files=('%s.csv' % aid,))]
            assert prof.reusable_from_manifest(ctx, aid, previous, True), aid

    def test_an_analysis_that_FAILED_is_re_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams', error='No space left on device')]
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True) == []

    def test_a_ZERO_BYTE_file_is_refused(self, tmp_path):
        """A full disk leaves 0-byte files. Reusing one as real output is worse than re-running -
        exactly what the 30 July crash left behind."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams', size=0)]
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True) == []

    def test_a_deleted_file_is_refused(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams')]
        os.remove(previous[0]['files'][0])
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True) == []

    def test_one_missing_file_out_of_several_refuses_the_whole_analysis(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams', files=('one.csv', 'two.csv'))]
        os.remove(previous[0]['files'][1])
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True) == []

    def test_a_different_corpus_reuses_nothing(self, tmp_path):
        """corpus_ok is decided once per run by the caller; False must stop everything."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams')]
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, False) == []

    def test_an_analysis_not_in_the_manifest_is_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, 'ngrams')]
        assert prof.reusable_from_manifest(ctx, 'embeddings', previous, True) == []

    def test_an_analysis_recorded_with_no_files_is_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        an_output(ctx)
        previous = [{'id': 'ngrams', 'files': [], 'error': ''}]
        assert prof.reusable_from_manifest(ctx, 'ngrams', previous, True) == []

    def test_nothing_previous_reuses_nothing(self, tmp_path):
        ctx = a_corpus(tmp_path)
        assert prof.reusable_from_manifest(ctx, 'ngrams', [], True) == []


class TestTheCorpusGuardOnAWholeRun:
    def test_the_same_corpus_matches(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof.save_manifest(out, [a_result(out)], ctx)
        assert prof.manifest_corpus(out)[0] == prof.corpus_fingerprint(ctx)[0]

    def test_an_edited_corpus_does_not(self, tmp_path):
        """A coreference-resolved copy, or a document added: the numbers would no longer describe
        the corpus in front of you."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof.save_manifest(out, [a_result(out)], ctx)
        (tmp_path / 'HPbooks' / 'c.txt').write_text('Ron said nothing.', encoding='utf-8')
        assert prof.manifest_corpus(out)[0] != prof.corpus_fingerprint(ctx)[0]
