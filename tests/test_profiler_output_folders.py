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


class TestTheTwoKindsOfSpaceLiveTogether:
    """The row asks one question - "Where does it all happen?" - so its two answers belong in one
    place. Nested WITHOUT repeating the corpus name: naming it at every level is what put paths
    over Windows' 260-character limit, twice in one day.
    """

    def test_geocodable_and_symbolic_are_siblings_under_one_GIS_folder(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'HPbooks'), 'inputFilename': ''}
        geo = prof._analysis_dir(c, 'GIS', 'geocodable')
        sym = prof._analysis_dir(c, 'GIS', 'symbolic')
        assert os.path.dirname(geo) == os.path.dirname(sym)
        assert os.path.basename(os.path.dirname(geo)) == 'GIS_HPbooks'
        assert os.path.basename(geo) == 'geocodable'
        assert os.path.basename(sym) == 'symbolic'
        assert os.path.isdir(geo) and os.path.isdir(sym)

    def test_the_corpus_is_named_ONCE_not_at_every_level(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'harrypotter_r_corpus_10_17_2024'),
             'inputFilename': ''}
        got = prof._analysis_dir(c, 'GIS', 'symbolic')
        rel = os.path.relpath(got, str(out))
        assert rel.count('harrypotter_r_corpus_10_17_2024') == 1

    def test_nesting_still_does_not_delete_what_is_there(self, tmp_path):
        out = tmp_path / 'profile'
        out.mkdir()
        c = {'outputDir': str(out), 'inputDir': str(tmp_path / 'HPbooks'), 'inputFilename': ''}
        first = prof._analysis_dir(c, 'GIS', 'symbolic')
        keeper = os.path.join(first, 'events.csv')
        with open(keeper, 'w', encoding='utf-8') as fh:
            fh.write('actor,space\n')
        assert prof._analysis_dir(c, 'GIS', 'symbolic') == first
        assert os.path.isfile(keeper)

    def test_symbolic_space_actually_runs_in_the_sweep_now(self):
        """It was kind='gui' - a pointer - while the row promised symbolic space."""
        entry = prof.REGISTRY['spatial_symbolic']
        assert entry['kind'] == 'batch'
        assert callable(entry['run'])

    def test_the_steps_needing_a_chosen_attribute_stay_a_pointer(self):
        """Distribution and movement need an actor attribute that is a research decision; guessing
        it unattended would put numbers in a report nobody chose."""
        entry = prof.REGISTRY['spatial_symbolic_more']
        assert entry['kind'] == 'gui'
        assert entry['gui_script'] == 'GIS_symbolic_main.py'
