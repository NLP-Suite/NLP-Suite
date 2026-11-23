"""Input files whose names do not all carry a date in the configured place keep the 1.6.45 order (alphabetical).

getFileList sorts by the filename settings of the I/O configuration (separator, date format, date position),
through IO_files_util.do_compare, and falls back to alphabetical order when that comparison fails. Until #1774
the comparison's error handler itself raised NameError (`date_location`), so a failure always reached the
fallback. #1774 fixed the name, and the handler then returned -1 for any pair, an inconsistent comparison
that left the files in arbitrary order: Shape of Stories on the 5 sample reviews plus the 5 sample stories got
its documents in a different order, and different clusters, in the 1.6.46 candidate (tool_sweep, 23 Nov).
"""

import importlib.util
import os
import sys

# conftest stubs IO_files_util; load the real one under a private name, as test_output_file_names does
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)
_spec = importlib.util.spec_from_file_location("_real_IO_files_util_order", os.path.join(_SRC, "IO_files_util.py"))
IO_files_util = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(IO_files_util)  # it chdirs to src/ at import
finally:
    os.chdir(_cwd)

STORIES = [  # the sweep's "stories" input: 5 reviews with a date in item 4, 5 stories without one
    "Bunin - Gentle breath.txt",
    "Faulkner - Dry September.txt",
    "Murphy - Miracles thicker than fog.txt",
    "Professor Dumbass.txt",
    "The Three Little Pigs.txt",
    "A Spool of Blue Thread_Anne Tyler_Rebecca Pepper Sinkler_02-13-2015.txt",
    "Barkskins_Annie Proulx_William T Vollmann_06-17-2016.txt",
    "Career of Evil_JK Rowling_Charles Finch_10-29-2015.txt",
    "Sweetbitter_Stephanie Danler_Gabrielle Hamilton_05-24-2016.txt",
    "The Fixer_Joseph Finder_Ken Tucker_06-10-2015.txt",
]
DEFAULT_IO = dict(sort_order="0", separator="_", date_format="mm/dd/yyyy", date_pos=4)  # lib/config_defaults


def test_a_corpus_the_date_order_cannot_sort_comes_back_alphabetical():
    for start in (STORIES, list(reversed(STORIES)), STORIES[3:] + STORIES[:3]):
        assert IO_files_util.sort_by_filename_settings(list(start), ".txt", **DEFAULT_IO) == sorted(STORIES)


def test_a_dated_corpus_sorts_the_same_whatever_order_the_files_come_in():
    dated = STORIES[5:]
    first = IO_files_util.sort_by_filename_settings(list(dated), ".txt", **DEFAULT_IO)
    assert sorted(first) == sorted(dated)
    for start in (list(reversed(dated)), dated[2:] + dated[:2]):
        assert IO_files_util.sort_by_filename_settings(list(start), ".txt", **DEFAULT_IO) == first
