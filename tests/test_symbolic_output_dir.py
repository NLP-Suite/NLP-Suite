"""The symbolic space tool writes into a folder of its own.

Its seven outputs - the actor-space events table, the cross-tab with its residuals and heatmap, the
transitions, the movement chart and the interactive timeline - went straight into the output
directory, where they sat loose among everything else and could not be found.

The folder is created, never re-created: the tool's three steps (BUILD, distribution, movement) are
run separately into the same place, so a step that wiped the folder would destroy what the previous
one produced. That is why this does not use IO_files_util.make_output_subdirectory, which calls
shutil.rmtree on an existing folder without asking.
"""
import importlib.util
import os
import sys
from unittest.mock import MagicMock

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, _SRC)

for _mod in ('GUI_util', 'GUI_IO_util', 'IO_libraries_util', 'IO_files_util', 'CoNLL_util',
             'reminders_util', 'run_script_util', 'IO_user_interface_util', 'config_util',
             'GIS_symbolic_util', 'GIS_symbolic_actor_typology_util', 'charts_util'):
    sys.modules.setdefault(_mod, MagicMock())

_spec = importlib.util.spec_from_file_location('_real_symbolic_main',
                                              os.path.join(_SRC, 'GIS_symbolic_main.py'))
sym = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(sym)
except BaseException:
    # the GUI builds at import; the helper under test is defined before that work
    pass
finally:
    os.chdir(_cwd)

folder = sym._symbolic_output_dir


class TestSymbolicOutputDir:
    def test_named_after_the_corpus_directory(self, tmp_path):
        out = str(tmp_path)
        got = folder(out, '', str(tmp_path / 'HPbooks'))
        assert os.path.basename(got) == 'symbolic_space_HPbooks'
        assert os.path.isdir(got)

    def test_a_conll_filename_keeps_the_corpus_not_the_prefix_chain(self, tmp_path):
        """A CoNLL table is named NLP_CoNLL_Stanza_Dir_<corpus>.csv; the folder should say the
        corpus, not repeat the whole processing history."""
        out = str(tmp_path)
        conll = str(tmp_path / 'NLP_CoNLL_Stanza_Dir_harrypotter_r_corpus_10_17_2024.csv')
        assert os.path.basename(folder(out, conll, '')) == \
            'symbolic_space_harrypotter_r_corpus_10_17_2024'

    def test_a_plain_filename_is_used_as_it_is(self, tmp_path):
        out = str(tmp_path)
        assert os.path.basename(folder(out, str(tmp_path / 'tales.csv'), '')) == \
            'symbolic_space_tales'

    def test_no_corpus_still_gives_a_folder(self, tmp_path):
        assert os.path.basename(folder(str(tmp_path), '', '')) == 'symbolic_space'

    def test_a_SECOND_step_does_not_destroy_the_first(self, tmp_path):
        """BUILD, then the distribution, then the movement map - three separate runs into one
        folder. This is the case make_output_subdirectory would have broken."""
        out = str(tmp_path)
        first = folder(out, '', str(tmp_path / 'HPbooks'))
        events = os.path.join(first, 'NLP_GIS_symbolic_actor_space_events.csv')
        with open(events, 'w', encoding='utf-8') as fh:
            fh.write('actor,space\n')

        again = folder(out, '', str(tmp_path / 'HPbooks'))
        assert again == first
        assert os.path.isfile(events), "BUILD's output was destroyed by the next step"

    def test_the_input_directory_wins_over_the_filename(self, tmp_path):
        out = str(tmp_path)
        got = folder(out, str(tmp_path / 'something.csv'), str(tmp_path / 'HPbooks'))
        assert os.path.basename(got) == 'symbolic_space_HPbooks'
