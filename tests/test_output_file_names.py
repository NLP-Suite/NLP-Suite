"""Output filenames: labels are added once, and the name still says everything it did.

A tool's output becomes the next tool's input, so the input filename already carries the labels
of every step that made it. Adding them again produced names like

    NLP_GIS_GIS_GIS_CoreNLP_NER_ALL_NER_Dir_<corpus>_geo-Goo_Location_distance_pairwise_...

162 characters before the folders above it — and on Windows a path over 260 characters cannot be
copied. The co-author on the Harry Potter paper hit exactly that, with a dialog whose Skip button
would have silently dropped the files.
"""
import importlib.util
import os
import sys

# conftest replaces IO_files_util with a MagicMock for the whole session, because most modules under
# test only import it for side effects. Here it IS the module under test, so the real one is loaded
# from source under a private name - its own imports (GUI_util, IO_libraries_util, pandas...) still
# resolve against the stubs, and sys.modules['IO_files_util'] stays the stub for every other test.
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)
_spec = importlib.util.spec_from_file_location('_real_IO_files_util',
                                               os.path.join(_SRC, 'IO_files_util.py'))
io = importlib.util.module_from_spec(_spec)

# IO_files_util does os.chdir(src) at import, so merely loading it moves the WHOLE test process into
# src/ and any later test using a relative path resolves it somewhere unexpected. Put the working
# directory back.
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(io)
finally:
    os.chdir(_cwd)


class TestLabelAlreadyInName:
    def test_a_word_of_the_name_is_found(self):
        assert io.label_already_in_name('GIS', 'NLP_GIS_Dir_corpus')

    def test_a_word_that_is_not_there_is_not_found(self):
        assert not io.label_already_in_name('SVO', 'NLP_GIS_Dir_corpus')

    def test_it_compares_words_not_substrings(self):
        """'NER' is inside 'GENERAL'; a substring test would drop a label that belongs."""
        assert not io.label_already_in_name('NER', 'NLP_GENERAL_Dir_corpus')
        assert not io.label_already_in_name('GIS', 'NLP_AEGIS_Dir_corpus')

    def test_case_does_not_matter(self):
        assert io.label_already_in_name('ner', 'NLP_NER_Dir_corpus')

    def test_a_multi_word_label_needs_the_whole_sequence(self):
        assert io.label_already_in_name('NER_ALL', 'NLP_CoreNLP_NER_ALL_Dir_corpus')
        assert not io.label_already_in_name('NER_ALL', 'NLP_NER_Dir_ALL_corpus')


class TestNamesDoNotAccumulate:
    def test_a_fresh_corpus_gets_its_label(self, tmp_path):
        out = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path),
                                           '.csv', 'GIS')
        assert os.path.basename(out) == 'NLP_GIS_Dir_HPbooks.csv'

    def test_running_the_same_step_again_does_not_repeat_its_label(self, tmp_path):
        """The bug: GIS output fed back into GIS gave NLP_GIS_GIS_..."""
        first = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path),
                                             '.csv', 'GIS')
        second = io.generate_output_file_name(first, '', str(tmp_path), '.csv', 'GIS')
        assert 'GIS_GIS' not in os.path.basename(second)
        assert 'GIS' in os.path.basename(second)

    def test_three_passes_do_not_treble_it(self, tmp_path):
        name = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path), '.csv', 'GIS')
        for _ in range(2):
            name = io.generate_output_file_name(name, '', str(tmp_path), '.csv', 'GIS')
        assert os.path.basename(name).count('GIS') == 1

    def test_a_different_label_is_still_added(self, tmp_path):
        first = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path),
                                             '.csv', 'GIS')
        second = io.generate_output_file_name(first, '', str(tmp_path), '.csv', 'NER')
        base = os.path.basename(second)
        assert 'GIS' in base and 'NER' in base

    def test_trailing_labels_are_not_repeated_either(self, tmp_path):
        """label2..label5 accumulated the same way — NER_ALL_NER in the real filename."""
        first = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path),
                                             '.csv', 'NER', 'Location')
        second = io.generate_output_file_name(first, '', str(tmp_path), '.csv', 'NER', 'Location')
        assert os.path.basename(second).count('Location') == 1

    def test_the_name_still_carries_every_step(self, tmp_path):
        """Shorter must not mean less informative: everything that finds files by name
        (the reuse probes, the report, OpenOutputFiles) reads these words."""
        name = io.generate_output_file_name('', str(tmp_path / 'HPbooks'), str(tmp_path),
                                            '.csv', 'GIS', 'Location')
        name = io.generate_output_file_name(name, '', str(tmp_path), '.csv', 'NER', 'distance')
        base = os.path.basename(name).lower()
        for word in ('gis', 'location', 'ner', 'distance', 'hpbooks'):
            assert word in base

    def test_the_real_case_gets_much_shorter(self, tmp_path):
        """The filename from the screenshot, rebuilt the way the pipeline builds it."""
        name = io.generate_output_file_name('', str(tmp_path / 'newspaperArticles'), str(tmp_path),
                                            '.csv', 'GIS', 'CoreNLP_NER_ALL')
        for _ in range(2):
            name = io.generate_output_file_name(name, '', str(tmp_path), '.csv', 'GIS', 'NER')
        base = os.path.basename(name)
        assert 'GIS_GIS' not in base
        assert 'NER_ALL_NER' not in base
        assert len(base) < 80, base


class TestIllegalCharactersInLabels:
    """A label comes from a column header, and a column header can hold anything.

    'Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)' was used as a filename label. On
    Windows a colon opens an NTFS alternate data stream, so that wrote a ZERO-BYTE file named
    'NLP_Sentence iconicity (Mean score' with no extension and put the data in a stream nothing
    reads. The iconicity chart had been failing that way silently: the file exists, so nothing looks
    wrong until you open it.
    """

    def test_a_colon_becomes_a_dash(self):
        assert io.safe_filename_part('Mean score: 1 Not iconic') == 'Mean score- 1 Not iconic'

    def test_slashes_cannot_reach_the_filesystem(self):
        """A slash would write into a subdirectory, or above one."""
        cleaned = io.safe_filename_part('a/b' + chr(92) + 'c')
        assert '/' not in cleaned and chr(92) not in cleaned

    def test_every_character_windows_refuses(self):
        illegal = '<>:"/' + chr(92) + '|?*'
        cleaned = io.safe_filename_part('a'.join(illegal))
        for ch in illegal:
            assert ch not in cleaned

    def test_a_trailing_dot_or_space_is_dropped(self):
        """Windows silently strips them, which turns two different names into one."""
        assert io.safe_filename_part('name. ') == 'name'
        assert io.safe_filename_part('name ') == 'name'

    def test_ordinary_text_is_untouched(self):
        assert io.safe_filename_part('NLP_SVO_Stanza_Dir_corpus') == 'NLP_SVO_Stanza_Dir_corpus'

    def test_the_real_iconicity_label_produces_a_usable_name(self, tmp_path):
        name = io.generate_output_file_name(
            '', str(tmp_path / 'HPbooks'), str(tmp_path), '.csv',
            'Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)')
        assert ':' not in os.path.basename(name)
        assert os.path.basename(name).endswith('.csv')


class TestTheCorpusNameIsNotSaidThreeTimes:
    def test_dropped_when_the_output_folder_already_names_the_corpus(self, tmp_path):
        corpus = tmp_path / 'harrypotter_r_corpus_10_17_2024'
        out = tmp_path / 'corpus_profile_harrypotter_r_corpus_10_17_2024'
        out.mkdir()
        name = os.path.basename(io.generate_output_file_name(
            '', str(corpus), str(out), '.csv', 'SVO', 'Stanza'))
        assert 'harrypotter_r_corpus_10_17_2024' not in name
        assert 'SVO' in name and 'Stanza' in name      # the labels that identify it still there

    def test_KEPT_when_the_output_folder_does_not(self, tmp_path):
        """A file written somewhere that does not say which corpus it came from must still say so."""
        corpus = tmp_path / 'harrypotter_r_corpus_10_17_2024'
        out = tmp_path / 'somewhere_else'
        out.mkdir()
        name = os.path.basename(io.generate_output_file_name(
            '', str(corpus), str(out), '.csv', 'SVO', 'Stanza'))
        assert 'Dir_harrypotter_r_corpus_10_17_2024' in name
