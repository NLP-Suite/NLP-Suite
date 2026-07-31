"""XML that arrives inside somebody else's document must not be able to read the disk.

A .docx is a zip of XML written by whoever sent the file, and the Suite reads its author field.
lxml's DEFAULTS resolve entities, so such a document can declare an entity pointing at a local file
and have its contents pulled into the parse: the user sees an author, and the parser has quietly
read something else. Same for a .gexf handed to the Gephi importer.

These tests use a real XXE payload and assert the file contents do NOT come back. They run against
whatever lxml is installed - which is the point, because the environments in the field are old.
"""
import importlib.util
import io
import os
import sys
import zipfile

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

etree = pytest.importorskip('lxml.etree', reason='lxml not installed')
if not hasattr(etree, 'XMLParser'):
    pytest.skip('lxml is stubbed', allow_module_level=True)


def _load(name):
    spec = importlib.util.spec_from_file_location(
        '_xxe_' + name, os.path.join(_SRC, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


@pytest.fixture(scope='module')
def io_files():
    return _load('IO_files_util')


@pytest.fixture
def secret(tmp_path):
    p = tmp_path / 'secret.txt'
    p.write_text('TOP-SECRET-CONTENTS', encoding='utf-8')
    return p


def _xxe_document(secret_path):
    """The classic external-entity attack: &xxe; expands to the named file's contents."""
    uri = 'file:///' + str(secret_path).replace('\\', '/')
    return (
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE cp:coreProperties [ <!ENTITY xxe SYSTEM "%s"> ]>\n'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/'
        'core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:creator>&xxe;</dc:creator>'
        '</cp:coreProperties>' % uri
    ).encode('utf-8')


class TestTheHardenedParser:
    def test_it_exists_and_is_a_parser(self, io_files):
        assert io_files.safe_xml_parser() is not None

    def test_an_external_entity_is_not_expanded(self, io_files, secret):
        parser = io_files.safe_xml_parser()
        doc = etree.fromstring(_xxe_document(secret), parser=parser)
        text = etree.tostring(doc, encoding='unicode')
        assert 'TOP-SECRET-CONTENTS' not in text

    def test_the_DEFAULT_parser_is_why_this_is_needed(self, secret):
        """Not a test of our code - a demonstration that the default is unsafe on this very lxml,
        so the hardening is load-bearing rather than decorative. Skipped if a future lxml makes the
        default safe, which is itself the news."""
        doc = etree.fromstring(_xxe_document(secret))
        leaked = 'TOP-SECRET-CONTENTS' in etree.tostring(doc, encoding='unicode')
        if not leaked:
            pytest.skip('this lxml (%s) no longer expands external entities by default'
                        % etree.__version__)
        assert leaked

    def test_ordinary_xml_still_parses_normally(self, io_files):
        parser = io_files.safe_xml_parser()
        doc = etree.fromstring(
            b'<a xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>Roberto</dc:creator></a>',
            parser=parser)
        ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
        assert doc.xpath('//dc:creator', namespaces=ns)[0].text == 'Roberto'


class TestGetAuthor:
    """The real call site: reading the author out of a .docx.

    file_filename_util reaches its parser through IO_files_util, which conftest stubs - and a
    MagicMock parser makes lxml raise, which get_author's bare `except` turns into an empty author.
    That is a test artifact, not a defect, but it hides the only thing worth checking here, so
    these tests put the REAL IO_files_util back before calling.
    """

    def _module(self, io_files):
        mod = _load('file_filename_util')
        mod.IO_files_util = io_files
        return mod

    def _docx(self, path, core_xml):
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr('docProps/core.xml', core_xml)
            zf.writestr('[Content_Types].xml', '<Types/>')
        return str(path)

    def test_a_normal_docx_still_yields_its_author(self, io_files, tmp_path):
        mod = self._module(io_files)
        good = (b'<cp:coreProperties '
                b'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/'
                b'core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">'
                b'<dc:creator>Roberto Franzosi</dc:creator></cp:coreProperties>')
        path = self._docx(tmp_path / 'ok.docx', good)
        assert mod.get_author(path) == 'Roberto Franzosi'

    def test_a_malicious_docx_does_not_leak_a_local_file(self, io_files, tmp_path, secret):
        mod = self._module(io_files)
        path = self._docx(tmp_path / 'evil.docx', _xxe_document(secret))
        got = mod.get_author(path)
        assert 'TOP-SECRET-CONTENTS' not in str(got)

    def test_a_malicious_docx_does_not_crash_the_caller(self, io_files, tmp_path, secret):
        """It is called while listing a folder of documents; one hostile file must not end the
        listing."""
        mod = self._module(io_files)
        path = self._docx(tmp_path / 'evil.docx', _xxe_document(secret))
        assert isinstance(mod.get_author(path), str)


class TestGephiImporter:
    def test_its_parsers_are_hardened_too(self):
        """A .gexf can arrive from anywhere. Checked by reading the source rather than by driving
        the importer, which needs a full graph to do anything."""
        src = open(os.path.join(_SRC, 'Gephi_util.py'), encoding='utf-8', errors='replace').read()
        made = src.count('etree.XMLParser(')
        hardened = src.count('resolve_entities=False')
        assert made > 0
        assert hardened == made, 'an XMLParser in Gephi_util still uses lxml defaults'
