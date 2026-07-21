"""Tests for string_similarity_util (pure stdlib -- no GUI or NLP imports involved)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import string_similarity_util as sim  # noqa: E402


class TestLevenshteinDistance:
    def test_identical(self):
        assert sim.levenshtein_distance('Cobb', 'Cobb') == 0

    def test_empty(self):
        assert sim.levenshtein_distance('', 'Cobb') == 4
        assert sim.levenshtein_distance('Cobb', '') == 4
        assert sim.levenshtein_distance('', '') == 0

    def test_single_edits(self):
        assert sim.levenshtein_distance('Lee', 'Loe') == 1        # substitution
        assert sim.levenshtein_distance('Fleming', 'Flemming') == 1  # insertion
        assert sim.levenshtein_distance('Flemming', 'Fleming') == 1  # deletion

    def test_known_textbook_value(self):
        assert sim.levenshtein_distance('kitten', 'sitting') == 3

    def test_symmetric(self):
        assert sim.levenshtein_distance('Coolidge', 'Cooledge') == sim.levenshtein_distance('Cooledge', 'Coolidge')


class TestLevenshteinRatio:
    def test_identical_is_100(self):
        assert sim.levenshtein_ratio('Fleming', 'Fleming') == 100.0
        assert sim.levenshtein_ratio('', '') == 100.0

    def test_no_overlap_is_0(self):
        assert sim.levenshtein_ratio('abc', 'xyz') == 0.0

    def test_substitution_weighted_two(self):
        # 'Lee'/'Loe': lengths sum to 6, one substitution costs 2 -> (6-2)/6
        assert sim.levenshtein_ratio('Lee', 'Loe') == 66.7

    def test_bounded(self):
        for a, b in [('Cobb', 'Cobbs'), ('a', 'zzzzz'), ('Macon', 'Bacon')]:
            assert 0.0 <= sim.levenshtein_ratio(a, b) <= 100.0

    def test_case_sensitive_by_design(self):
        # the raw ratio is case-sensitive; similarity() is the case-folding entry point
        assert sim.levenshtein_ratio('COBB', 'Cobb') < 100.0


class TestSimilarity:
    def test_case_variants_score_100(self):
        # the regression that motivated this module: fuzz.ratio scored 'COBB'/'Cobb' 25
        assert sim.similarity('COBB', 'Cobb') == 100.0
        assert sim.similarity('Fleming', 'fleming') == 100.0

    def test_word_order_variants_score_100(self):
        assert sim.similarity('Jim Cobb', 'Cobb, Jim') == 100.0

    def test_real_spelling_variants_score_high(self):
        assert sim.similarity('Fleming', 'Flemming') > 90
        assert sim.similarity('Coolidge', 'Cooledge') > 85

    def test_distinct_short_names_stay_below_identity(self):
        assert sim.similarity('Macon', 'Bacon') < 100

    def test_token_sort_never_lowers_the_score(self):
        for a, b in [('Atlanta Constitution', 'Atlanta Constitutional'), ('Jim Cobb', 'Jim Cobbs')]:
            assert sim.similarity(a, b) >= sim.levenshtein_ratio(a.lower(), b.lower())


class TestBestMatch:
    CANDIDATES = [('Flemming', 3), ('Fleming', 12), ('Flemmings', 2)]

    def test_returns_closest_not_first(self):
        # the old first-over-threshold scan returned 'Flemming' purely because it was listed first
        matched, freq, score, distance = sim.best_match('Flemin', self.CANDIDATES, 80)
        assert matched == 'Fleming'
        assert freq == 12

    def test_returns_none_below_threshold(self):
        assert sim.best_match('Zebra', self.CANDIDATES, 80) is None

    def test_skips_the_word_itself(self):
        matched, _, _, _ = sim.best_match('Fleming', self.CANDIDATES, 80)
        assert matched != 'Fleming'

    def test_keeps_case_only_variants(self):
        # 'COBB' vs 'Cobb' is an inconsistency worth reporting, not a self-match to skip
        result = sim.best_match('COBB', [('Cobb', 7)], 80)
        assert result is not None
        assert result[0] == 'Cobb'
        assert result[2] == 100.0

    def test_reports_edit_distance(self):
        _, _, _, distance = sim.best_match('Flemin', [('Fleming', 12)], 80)
        assert distance == 1

    def test_accepts_plain_strings(self):
        matched, freq, _, _ = sim.best_match('Flemin', ['Fleming'], 80)
        assert matched == 'Fleming'
        assert freq == ''

    def test_empty_candidates(self):
        assert sim.best_match('Fleming', [], 80) is None
