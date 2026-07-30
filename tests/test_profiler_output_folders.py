"""Every analysis's files go in its own subfolder.

The report says so: "every individual output file is written to a category subfolder and LINKED from
the report". Most analyses honoured it because the utils they call make their own subfolder. Seven
did not, and left 40 files loose in the one folder a reader opens - fifteen from the semantic classes
alone, plus a 2.1 GB vector dump.

_analysis_dir is deliberately NOT IO_files_util.make_output_subdirectory: that deletes an existing
folder (shutil.rmtree, without asking when silent=True), and reuse depends on those files surviving.
"""
import importlib.util
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

_spec = importlib.util.spec_from_file_location('_real_profiler_dirs',
                                              os.path.join(_SRC, 'corpus_profiler_util.py'))
prof = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(prof)
finally:
    os.chdir(_cwd)


class TestAnalysisDir:
    def test_it_makes_a_folder_named_for_the_analysis_and_the_corpus(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'HPbooks'), 'inputFilename': ''}
        got = prof._analysis_dir(c, 'embeddings')
        assert os.path.basename(got) == 'embeddings_HPbooks'
        assert os.path.isdir(got)

    def test_it_does_NOT_delete_what_is_already_there(self, tmp_path):
        """The whole reason it is not make_output_subdirectory. Deleting the folder on a re-run
        would destroy the very files reuse is about to hand back."""
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'HPbooks'), 'inputFilename': ''}
        first = prof._analysis_dir(c, 'embeddings')
        keeper = os.path.join(first, 'vectors.csv')
        with open(keeper, 'w', encoding='utf-8') as fh:
            fh.write('x' * 100)

        again = prof._analysis_dir(c, 'embeddings')
        assert again == first
        assert os.path.isfile(keeper), 'the previous run\'s output was deleted'
        assert os.path.getsize(keeper) == 100

    def test_a_single_input_file_names_the_folder_after_it(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': '',
             'inputFilename': str(tmp_path / 'one_book.txt')}
        assert os.path.basename(prof._analysis_dir(c, 'topics_Gensim')) == 'topics_Gensim_one_book'

    def test_no_corpus_name_still_gives_a_folder(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': '', 'inputFilename': ''}
        assert os.path.basename(prof._analysis_dir(c, 'topics_Gensim')) == 'topics_Gensim'

    def test_no_output_folder_returns_what_it_was_given(self, tmp_path):
        assert prof._analysis_dir({'outputDir': ''}, 'embeddings') == ''

    def test_no_label_returns_the_profile_folder(self, tmp_path):
        out = str(tmp_path)
        assert prof._analysis_dir({'outputDir': out, 'inputDir': '', 'inputFilename': ''}, '') == out

    def test_different_analyses_get_different_folders(self, tmp_path):
        """Two analyses sharing a folder would be two analyses overwriting each other."""
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'HPbooks'), 'inputFilename': ''}
        made = {prof._analysis_dir(c, label) for label in
                ('embeddings', 'topics_Gensim', 'semantic_classes', 'vocabulary_richness',
                 'entity_locations', 'words_capital')}
        assert len(made) == 6
