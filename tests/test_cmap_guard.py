"""A crafted pdf must not be able to make pdfminer unpickle a file of its choosing.

pdfminer builds "<name>.pickle.gz" from a CMap name taken out of the pdf and os.path.join()s it
onto its own cmap directory - and os.path.join DISCARDS the directory when what follows is
absolute. So "\\\\attacker\\share\\evil", "C:/tmp/evil" or "../../evil" lands wherever the attacker
likes, and pdfminer then pickle.loads() it. Loading a pickle runs whatever code it carries:
GHSA-wf5f-4jwr-ppcp, CVSS 8.6, arbitrary code execution from opening a pdf. On Windows the path can
be a NETWORK location, so nothing needs planting on the machine first.

Fixed upstream in pdfminer.six 20251107, which requires Python >= 3.9. This suite runs 3.8, where
the newest available is 20250324 - the fix cannot be installed, hence the guard.

The name check is a pure function over strings, so the hostile inputs are just strings and this
whole file runs without pdfminer installed.
"""
import importlib.util
import os
import sys

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)


@pytest.fixture(scope='module')
def io_files():
    spec = importlib.util.spec_from_file_location(
        '_io_cmap_guard', os.path.join(_SRC, 'IO_files_util.py'))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


class TestNamesThatEscape:
    """Every one of these resolves OUTSIDE pdfminer's cmap directory."""

    @pytest.mark.parametrize('name', [
        r'\\attacker\share\evil',          # UNC: the Windows remote case, no local file needed
        '//attacker/share/evil',
        'C:/Windows/Temp/evil',
        r'C:\Windows\Temp\evil',
        'c:evil',                          # drive-relative
        '../../../../Users/Public/evil',
        r'..\..\evil',
        '/tmp/evil',
        '/etc/passwd',
        '~/evil',
        'UniJIS-UCS2-H/../../evil',
        'sub/dir/evil',
        r'sub\dir\evil',
    ])
    def test_it_is_refused(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is False


class TestNamesThatAreJustWrong:
    @pytest.mark.parametrize('name', ['', '.', '..', 'x' * 129, ' ', 'a name with spaces',
                                      'evil\x00', 'evil\x00.pickle.gz', '-leading-dash',
                                      '.hidden', 'na\nme'])
    def test_it_is_refused(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is False

    @pytest.mark.parametrize('name', [None, 42, b'bytes-not-str', ['a'], object()])
    def test_a_non_string_is_refused_rather_than_crashing(self, io_files, name):
        """It is called from inside pdfminer with whatever the pdf contained."""
        assert io_files.is_safe_cmap_name(name) is False


class TestRealCMapNamesStillWork:
    """A whitelist that blocked a legitimate name would quietly degrade text extraction for
    Japanese, Chinese and Korean pdfs - a silent loss, and the worst possible outcome here."""

    @pytest.mark.parametrize('name', [
        'UniJIS-UCS2-H', 'UniJIS-UCS2-V', '90ms-RKSJ-H', '78-EUC-V', 'Adobe-Japan1-UCS2',
        'B5pc-H', 'ETen-B5-H', 'KSCms-UHC-HW-V', 'UniGB-UCS2-H', 'Identity-H',
        'to-unicode-Adobe-Japan1', 'to-unicode-Adobe-Korea1', 'Add-RKSJ-H', 'EUC-H',
        'Hankaku', 'Roman', 'WP-Symbol', 'Ext-RKSJ-V', 'UniKS-UTF16-H',
    ])
    def test_it_is_allowed(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is True

    def test_every_cmap_pdfminer_actually_ships_is_allowed(self, io_files):
        """The real test set, not a sample of it. Skipped when pdfminer is absent (CI)."""
        try:
            import pdfminer.cmapdb as cmapdb
        except Exception:
            pytest.skip('pdfminer not installed')
        cmap_dir = os.path.join(os.path.dirname(cmapdb.__file__), 'cmap')
        if not os.path.isdir(cmap_dir):
            pytest.skip('no bundled cmap directory')
        names = [f[:-len('.pickle.gz')] for f in os.listdir(cmap_dir) if f.endswith('.pickle.gz')]
        assert names, 'no bundled cmaps found to check against'
        rejected = [n for n in names if not io_files.is_safe_cmap_name(n)]
        assert rejected == [], 'the guard would break these real pdfs: %s' % rejected[:10]
        # the unicode maps are looked up with a prefix
        prefixed = [n for n in ('to-unicode-%s' % n for n in names)
                    if not io_files.is_safe_cmap_name(n)]
        assert prefixed == []


class TestTheGuardIsWiredIn:
    def test_installing_it_is_idempotent(self, io_files):
        pytest.importorskip('pdfminer.cmapdb', reason='pdfminer not installed')
        from pdfminer.cmapdb import CMapDB
        assert io_files.harden_pdfminer_cmap() is True
        first = CMapDB._load_data
        assert getattr(first, '_nlp_suite_guarded', False)
        assert io_files.harden_pdfminer_cmap() is True
        assert getattr(CMapDB._load_data, '_nlp_suite_guarded', False)

    def test_a_hostile_name_raises_the_error_pdfminer_ALREADY_handles(self, io_files):
        """CMapNotFound is caught in pdffont and pdfinterp, so a hostile pdf degrades to slightly
        thinner text instead of ending the conversion."""
        pytest.importorskip('pdfminer.cmapdb', reason='pdfminer not installed')
        from pdfminer.cmapdb import CMapDB
        io_files.harden_pdfminer_cmap()
        with pytest.raises(CMapDB.CMapNotFound):
            CMapDB._load_data(r'\\attacker\share\evil')

    def test_a_real_cmap_still_loads(self, io_files):
        pytest.importorskip('pdfminer.cmapdb', reason='pdfminer not installed')
        from pdfminer.cmapdb import CMapDB
        io_files.harden_pdfminer_cmap()
        assert CMapDB._load_data('UniJIS-UCS2-H') is not None

    def test_the_converter_installs_it_before_opening_any_pdf(self):
        """Checked in the source: the call must sit at module level, next to the pdfminer imports,
        not inside a function that a code path might miss."""
        src = open(os.path.join(_SRC, 'file_converter_util.py'),
                   encoding='utf-8', errors='replace').read()
        assert 'harden_pdfminer_cmap()' in src
        call_at = src.index('harden_pdfminer_cmap()')
        # before the first function that reads a pdf
        first_def = src.index('\ndef ')
        assert call_at < first_def, 'the guard is installed after the module already defines readers'
