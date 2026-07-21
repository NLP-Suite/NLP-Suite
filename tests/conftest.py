"""Pytest bootstrap for the legacy NLP-Suite ``src/`` modules.

The legacy modules under ``src/`` are written to be run from a Tk GUI: importing
one (e.g. ``statistics_txt_util``) pulls in ``GUI_util`` which calls
``tkinter.Tk()`` at module load, and ``IO_libraries_util.install_all_Python_packages``
which shells out to ``pip``. Neither is acceptable inside a unit test (no display,
no network, no side effects).

To unit-test the pure, stdlib-only helpers without refactoring production code,
we replace the GUI/infra modules and the heavy NLP libraries with ``MagicMock``
stubs in ``sys.modules`` *before* the modules under test are imported. A
``MagicMock`` makes the module's import-time guards harmless: e.g.
``install_all_Python_packages(...) == False`` evaluates to ``False`` (a mock is
truthy and not equal to ``False``), so the ``sys.exit(0)`` guard is skipped, and
``import_nltk_resource(...)`` becomes a no-op.

Standard-library modules the helpers actually rely on (``re``, ``string``,
``collections``) are intentionally NOT stubbed, so the functions execute for real.
"""

import pathlib
import sys
from unittest.mock import MagicMock

# Legacy modules import each other by bare name (``import GUI_util``), which only
# works because ``src/`` is on sys.path at runtime. Reproduce that here.
_SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_SRC))

# Project infra modules that drag in the Tk window / pip bootstrap.
_INFRA_STUBS = [
    "GUI_util",
    "IO_libraries_util",
    "GUI_IO_util",
    "IO_user_interface_util",
    "IO_files_util",
    "IO_csv_util",
    "charts_util",
    "reminders_util",
    "TIPS_util",
    "statistics_statistical_tests_util",
    "statistics_csv_util",
    "run_script_util",
    "config_util",
    "tree",
    "sentence_complexity_node_util",
]

# Heavy third-party libraries imported at module top but unused by the pure
# helpers. Dotted submodules must be registered explicitly so that
# ``from nltk.stem.porter import PorterStemmer`` resolves against the stub.
_HEAVY_STUBS = [
    # CI installs pytest and nothing else, so anything imported at module top by a module under
    # test must be stubbed here or collection fails -- and a collection error aborts the WHOLE run,
    # not just the one file. requests is imported by the DBpedia/YAGO/Wikipedia annotators.
    "requests",
    "stanza",
    "spacy",
    "textstat",
    "pandas",
    "PIL",
    "PIL.Image",
    "spacytextblob",
    "spacytextblob.spacytextblob",
    "nltk",
    "nltk.stem",
    "nltk.stem.porter",
    "nltk.corpus",
    "nltk.tree",
    "nltk.draw",
]

for _name in _INFRA_STUBS + _HEAVY_STUBS:
    sys.modules.setdefault(_name, MagicMock())
