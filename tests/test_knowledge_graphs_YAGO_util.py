"""Tests for _select_best_uri, which decides WHICH YAGO entity a phrase is linked to.

The module is import-coupled to Tk and the heavy NLP libraries, so it is imported only after
conftest has installed its stubs in sys.modules.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import knowledge_graphs_YAGO_util as yago  # noqa: E402

BASE = 'http://yago-knowledge.org/resource/'


def uri(name):
    return BASE + name


class TestSelectBestUri:
    def test_exact_match_wins(self):
        uris = [uri('Bacon_County'), uri('Atlanta_Georgia'), uri('Atlanta')]
        assert yago._select_best_uri(uris, 'atlanta') == uri('Atlanta')

    def test_exact_match_folds_case_and_underscores(self):
        assert yago._select_best_uri([uri('New_York_City')], 'new york city') == uri('New_York_City')

    def test_empty_uri_list_returns_none(self):
        # max() over an empty sequence raised ValueError before the guard
        assert yago._select_best_uri([], 'atlanta') is None

    def test_picks_the_closest_of_several(self):
        uris = [uri('Bacon_County'), uri('Macon_Georgia'), uri('Mason_Ohio')]
        assert yago._select_best_uri(uris, 'macon') == uri('Macon_Georgia')

    def test_underscores_do_not_penalize_a_correct_candidate(self):
        # 'The_Atlanta_Constitution' must still win against a shorter distractor
        uris = [uri('Atlanta'), uri('The_Atlanta_Constitution')]
        assert yago._select_best_uri(uris, 'atlanta constitution') == uri('The_Atlanta_Constitution')

    def test_case_does_not_change_the_choice(self):
        uris = [uri('Bacon_County'), uri('Atlanta_Georgia')]
        assert (yago._select_best_uri(uris, 'atlanta georgia')
                == yago._select_best_uri(uris, 'ATLANTA GEORGIA')
                == uri('Atlanta_Georgia'))

    def test_unrelated_phrase_below_threshold_returns_none(self):
        assert yago._select_best_uri([uri('Bacon_County')], 'zzzzzzzzzz') is None

    def test_q_suffix_is_stripped_before_scoring(self):
        # YAGO names can carry a Wikidata id suffix; it must not count against the match
        assert yago._select_best_uri([uri('Atlanta_Georgia_Q23556')], 'atlanta georgia') \
            == uri('Atlanta_Georgia_Q23556')

    def test_result_is_one_of_the_inputs(self):
        uris = [uri('Bacon_County'), uri('Macon_Georgia')]
        result = yago._select_best_uri(uris, 'macon')
        assert result in uris
