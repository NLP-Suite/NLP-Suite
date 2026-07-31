"""Reuse must notice when the analysis itself has changed.

Reuse checked that the recorded files still existed, were not empty, and came from this corpus. It
never asked whether the CODE that wrote them had changed - so improving an analysis never reached
a profile that already existed.

Symbolic space is what exposed it. The runner grew transitions, a heat map and an interactive
timeline; a profile with an older manifest entry kept replaying the one-file record from the
BUILD-only version, and the summary showed a lone csv while the new charts sat unlisted on disk.
"""
import importlib.util
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

_spec = importlib.util.spec_from_file_location(
    '_prof_code_stamp', os.path.join(_SRC, 'corpus_profiler_util.py'))
prof = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(prof)
finally:
    os.chdir(_cwd)


def _rec(tmp_path, aid='spatial_symbolic', code='abc123', **kw):
    f = tmp_path / 'events.csv'
    f.write_text('actor,space\nHarry,house\n', encoding='utf-8')
    rec = {'id': aid, 'files': [str(f)], 'error': ''}
    rec.update(kw)
    if code is not None:
        rec['code'] = code
    return rec


class TestTheFingerprint:
    def test_a_real_analysis_has_one(self):
        assert prof.analysis_code_fingerprint('spatial_symbolic')

    def test_it_is_stable_across_calls(self):
        """An unstable stamp would re-run everything on every profile, for ever."""
        assert (prof.analysis_code_fingerprint('spatial_symbolic')
                == prof.analysis_code_fingerprint('spatial_symbolic'))

    def test_different_analyses_get_different_stamps(self):
        seen = {prof.analysis_code_fingerprint(a) for a in
                ('spatial_symbolic', 'statistics', 'semantic_classes', 'topics_gensim')}
        assert len(seen) == 4

    def test_a_gui_pointer_has_none(self):
        """It produces no files, so there is nothing to invalidate."""
        assert prof.analysis_code_fingerprint('spatial_symbolic_more') == ''

    def test_an_unknown_analysis_does_not_raise(self):
        assert prof.analysis_code_fingerprint('no_such_analysis') == ''

    def test_it_covers_the_helper_modules_not_just_the_runner(self):
        """_run_spatial_symbolic is a few lines that call GIS_symbolic_util, which calls the
        typology. A change to the typology - today's London fix - is exactly the kind a reader
        would notice, and it must not be invisible to reuse."""
        import inspect
        body = inspect.getsource(prof.REGISTRY['spatial_symbolic']['run'])
        assert 'GIS_symbolic_util' in body
        # the stamp must actually depend on that file's bytes
        path = os.path.join(_SRC, 'GIS_symbolic_util.py')
        original = open(path, 'rb').read()
        before = prof.analysis_code_fingerprint('spatial_symbolic')
        try:
            with open(path, 'ab') as fh:
                fh.write(b'\n# fingerprint probe\n')
            after = prof.analysis_code_fingerprint('spatial_symbolic')
        finally:
            with open(path, 'wb') as fh:
                fh.write(original)
        assert before != after, 'a change in the helper module left the stamp unchanged'
        assert prof.analysis_code_fingerprint('spatial_symbolic') == before, 'not restored'


class TestReuseHonoursIt:
    def test_a_changed_stamp_refuses_reuse(self, tmp_path):
        previous = [_rec(tmp_path, code='0000deadbeef0000')]
        assert prof.reusable_from_manifest({}, 'spatial_symbolic', previous, True) == []

    def test_a_matching_stamp_reuses(self, tmp_path):
        current = prof.analysis_code_fingerprint('spatial_symbolic')
        previous = [_rec(tmp_path, code=current)]
        assert len(prof.reusable_from_manifest({}, 'spatial_symbolic', previous, True)) == 1

    def test_no_stamp_still_reuses(self, tmp_path):
        """An older profile has none. Refusing would make every returning user recompute
        everything once, which is a worse trade than saying the check could not be made."""
        previous = [_rec(tmp_path, code=None)]
        assert len(prof.reusable_from_manifest({}, 'spatial_symbolic', previous, True)) == 1

    def test_the_other_rules_still_apply(self, tmp_path):
        current = prof.analysis_code_fingerprint('spatial_symbolic')
        empty = tmp_path / 'empty.csv'
        empty.write_text('', encoding='utf-8')
        rec = _rec(tmp_path, code=current)
        rec['files'] = [str(empty)]
        assert prof.reusable_from_manifest({}, 'spatial_symbolic', [rec], True) == []

        failed = _rec(tmp_path, code=current, error='it blew up')
        assert prof.reusable_from_manifest({}, 'spatial_symbolic', [failed], True) == []

        ok = _rec(tmp_path, code=current)
        assert prof.reusable_from_manifest({}, 'spatial_symbolic', [ok], False) == []


class TestTheStampSurvivesTheRoundTrip:
    def test_a_reused_record_keeps_the_OLD_stamp(self, tmp_path):
        """Re-stamping reused files with today's code would declare that today's code produced
        them - and the next run would find them in order however much had changed since."""
        out = tmp_path / 'profile'
        out.mkdir()
        rec = _rec(tmp_path, code='0000deadbeef0000', reused=True)
        prof.save_manifest(str(out), [rec], None)
        import json
        written = json.load(open(os.path.join(str(out), prof.MANIFEST_NAME), encoding='utf-8'))
        assert written['results'][0]['code'] == '0000deadbeef0000'

    def test_a_record_with_no_stamp_is_not_given_one_on_reuse(self, tmp_path):
        """Blessing unstamped old files with today's code is the same lie, quieter."""
        out = tmp_path / 'profile'
        out.mkdir()
        rec = _rec(tmp_path, code=None, reused=True)
        prof.save_manifest(str(out), [rec], None)
        import json
        written = json.load(open(os.path.join(str(out), prof.MANIFEST_NAME), encoding='utf-8'))
        assert not written['results'][0].get('code')

    def test_an_analysis_that_actually_RAN_is_stamped_with_today(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        rec = _rec(tmp_path, code=None)          # ran this time: no 'reused' flag
        prof.save_manifest(str(out), [rec], None)
        import json
        written = json.load(open(os.path.join(str(out), prof.MANIFEST_NAME), encoding='utf-8'))
        assert written['results'][0]['code'] == prof.analysis_code_fingerprint('spatial_symbolic')
