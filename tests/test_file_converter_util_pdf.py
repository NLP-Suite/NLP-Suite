"""Tests for the pdf converters in file_converter_util.

Covers the path bug that could write converted files OUTSIDE the user's output directory, and the
new pdf --> docx converter that keeps the text AND the images embedded in the pdf.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# pypdf reads PIL.__version__ at import time, and conftest has replaced PIL with a MagicMock (whose
# __version__ raises AttributeError). Lift the PIL stubs for the duration of these imports, then put
# them back so the other test modules -- which never touch a real image -- keep their stubs.
_PIL_stubs = {name: sys.modules.pop(name)
              for name in ('PIL', 'PIL.Image') if name in sys.modules}

# CI installs pytest and nothing else; skip the whole module rather than abort collection when the
# pdf/docx stack is absent. conftest stubs GUI_util & friends, so the import itself is Tk-free.
try:
    pytest.importorskip('PIL')
    pytest.importorskip('pdfminer')
    pytest.importorskip('docx')
    pytest.importorskip('pypdf')
    pytest.importorskip('striprtf')

    import file_converter_util as fc  # noqa: E402
except BaseException:
    # the real stack is not installed (pytest.importorskip raises Skipped, a BaseException):
    # hand the other test modules their stubs back before bowing out
    sys.modules.update(_PIL_stubs)
    raise
# on success the REAL PIL stays in sys.modules: pypdf decodes the embedded images through it at
# call time, and any other module importing PIL now gets a working one.

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# a real, repo-tracked pdf that embeds 3 images (2 png + 1 jpg)
TIPS_PDF = os.path.join(REPO, 'TIPS', 'TIPS_NLP_Annotator dictionary.pdf')


class TestGetConvertedOutputPath:
    def test_a_sibling_directory_sharing_a_name_prefix_stays_inside_the_output_dir(self):
        """os.path.commonprefix compared STRINGS: 'C:/data/corpus' vs a doc in 'C:/data/corpus2'
        yielded a relative path of '../corpus2/a.pdf', writing the output OUTSIDE outputDir."""
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'data', 'corpus2', 'a.pdf'),
                                           os.path.join('C:', os.sep, 'data', 'corpus'),
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert os.pardir not in out.split(os.sep)
        assert os.path.basename(out) == 'a.txt'

    def test_a_subdirectory_is_mirrored_under_the_output_dir(self):
        doc = os.path.join('C:', os.sep, 'corpus', 'novels', '1920', 'a.pdf')
        out = fc.get_converted_output_path(doc, os.path.join('C:', os.sep, 'corpus'),
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert out == os.path.join('C:', os.sep, 'out', 'novels', '1920', 'a.txt')

    def test_a_file_directly_in_the_input_dir_lands_directly_in_the_output_dir(self):
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'corpus', 'a.pdf'),
                                           os.path.join('C:', os.sep, 'corpus'),
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert out == os.path.join('C:', os.sep, 'out', 'a.txt')

    def test_no_input_dir_falls_back_to_the_basename(self):
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'x', 'y', 'a.pdf'), '',
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert out == os.path.join('C:', os.sep, 'out', 'a.txt')

    def test_the_docx_extension_is_used_when_asked_for(self):
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'corpus', 'a.pdf'),
                                           os.path.join('C:', os.sep, 'corpus'),
                                           os.path.join('C:', os.sep, 'out'), '.docx')
        assert out.endswith('a.docx')

    def test_an_upper_case_PDF_keeps_its_name(self):
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'corpus', 'A.PDF'),
                                           os.path.join('C:', os.sep, 'corpus'),
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert os.path.basename(out) == 'A.txt'

    def test_a_dot_in_the_filename_is_not_mistaken_for_the_extension(self):
        out = fc.get_converted_output_path(os.path.join('C:', os.sep, 'c', 'v1.2 draft.pdf'),
                                           os.path.join('C:', os.sep, 'c'),
                                           os.path.join('C:', os.sep, 'out'), '.txt')
        assert os.path.basename(out) == 'v1.2 draft.txt'


class TestGetDocxImageWidth:
    def test_a_pdf_width_is_converted_from_points_to_inches(self):
        from docx.shared import Inches
        assert fc.get_docx_image_width(144) == Inches(2)     # 144 pt = 2 in

    def test_an_over_wide_image_is_capped_to_the_text_column(self):
        from docx.shared import Inches
        assert fc.get_docx_image_width(1440) == Inches(6)    # 20 in -> capped

    def test_a_zero_or_negative_width_falls_back_to_the_cap(self):
        from docx.shared import Inches
        assert fc.get_docx_image_width(0) == Inches(6)
        assert fc.get_docx_image_width(-10) == Inches(6)

    def test_a_non_numeric_width_falls_back_to_the_cap(self):
        from docx.shared import Inches
        assert fc.get_docx_image_width(None) == Inches(6)
        assert fc.get_docx_image_width('wide') == Inches(6)


class TestPypdfIsOptional:
    """pypdf must stay OPTIONAL: it is needed only by the pdf --> docx option.

    It was briefly added to IO_libraries_util.install_all_Python_packages, which is a FATAL ERROR
    that exits the Suite and runs at MODULE IMPORT -- so an installation predating pypdf was locked
    out of the csv, docx, rtf and pdf --> txt converters too.
    """

    def test_pypdf_is_not_in_the_fatal_import_gate(self):
        source = open(os.path.join(REPO, 'src', 'file_converter_util.py'), encoding='utf-8').read()
        gate = source.split('install_all_Python_packages(', 1)[1].split(')', 1)[0]
        assert 'pypdf' not in gate

    def test_the_converter_checks_for_pypdf_itself(self):
        assert fc.is_pypdf_available() in (True, False)


@pytest.mark.skipif(not os.path.isfile(TIPS_PDF), reason='TIPS pdf fixture not available')
class TestPdfToDocx:
    def test_the_text_is_extracted(self):
        text = fc.extract_pdf_text(TIPS_PDF)
        assert 'Annotation via Dictionary' in text
        assert len(text) > 1000

    def test_the_layout_keeps_text_and_images_in_reading_order(self):
        pages = fc.get_pdf_layout_items(TIPS_PDF)
        assert len(pages) == 4
        kinds = [kind for page in pages for kind, payload in page]
        assert kinds.count('image') == 3
        assert kinds.count('text') > 20
        # the first page opens with its title, NOT with the picture halfway down it
        assert pages[0][0][0] == 'text'

    def test_the_docx_holds_both_the_text_and_every_image(self, tmp_path):
        out = str(tmp_path / 'sub' / 'rebuilt.docx')
        placed, lost = fc.build_docx_from_pdf(TIPS_PDF, out)
        assert (placed, lost) == (3, 0)
        assert os.path.isfile(out)   # the sub-directory was created for us

        from docx import Document
        document = Document(out)
        assert len(document.inline_shapes) == 3
        text = '\n'.join(p.text for p in document.paragraphs)
        assert 'Annotation via Dictionary' in text
        assert 'IMAGE could not be' not in text

    def test_the_output_is_single_spaced_like_the_pdf(self, tmp_path):
        """A new python-docx document inherits Word's docDefaults -- 10 pt after every paragraph
        and 1.15 line spacing -- which read as double spacing next to a single spaced pdf."""
        out = str(tmp_path / 'spacing.docx')
        fc.build_docx_from_pdf(TIPS_PDF, out)

        from docx import Document
        from docx.shared import Pt
        paragraph_format = Document(out).styles['Normal'].paragraph_format
        assert paragraph_format.space_before == Pt(0)
        assert paragraph_format.space_after == Pt(0)
        assert paragraph_format.line_spacing == 1.0

    def test_an_unreadable_pdf_raises_rather_than_writing_a_truncated_file(self, tmp_path):
        broken = tmp_path / 'broken.pdf'
        broken.write_bytes(b'%PDF-1.4 this is not a pdf')
        with pytest.raises(Exception):
            fc.build_docx_from_pdf(str(broken), str(tmp_path / 'broken.docx'))
