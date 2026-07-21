"""Tests for the newspaper-title detection in file_cleaner_util.

Only the two pure helpers are exercised; newspaper_titles() itself drives the GUI and the Stanza
tokenizer.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import file_cleaner_util as fc  # noqa: E402


class TestIsTitle:
    def test_all_caps_headline(self):
        assert fc.isTitle('THREE NEGROES LYNCHED', 20) is True

    def test_title_case_headline(self):
        assert fc.isTitle('Mob Takes Prisoners From Jail', 20) is True

    def test_short_unpunctuated_line(self):
        assert fc.isTitle('Lynching in Macon', 20) is True

    def test_ordinary_sentence_is_not_a_title(self):
        assert fc.isTitle('The sheriff took the prisoner to Atlanta.', 20) is False

    def test_a_line_that_already_ends_a_sentence_is_never_a_title(self):
        # the splitter already handles it, so there is nothing to fix
        for line in ['MAN SHOT DEAD.', 'MAN SHOT DEAD!', 'Was he guilty?']:
            assert fc.isTitle(line, 20) is False

    def test_a_headline_ending_in_a_comma_is_still_a_title(self):
        # the old test used all of string.punctuation, so this counted as already punctuated
        assert fc.isTitle('MOB GATHERS AT JAIL,', 20) is True

    def test_returns_a_real_boolean_not_none(self):
        # the old isTitle fell off the end and returned None
        assert fc.isTitle('some ordinary body text that runs on', 20) is False

    def test_blank_and_none(self):
        assert fc.isTitle('', 20) is False
        assert fc.isTitle('   ', 20) is False
        assert fc.isTitle(None, 20) is False

    def test_position_limits_detection(self):
        assert fc.isTitle('MAN SHOT DEAD', 20, position=0) is True
        assert fc.isTitle('MAN SHOT DEAD', 20, position=50) is False

    def test_position_test_can_be_disabled(self):
        assert fc.isTitle('MAN SHOT DEAD', 20, position=50, lead_paragraphs=None) is True

    def test_length_limit_is_honoured(self):
        assert fc.isTitle('a quiet day in macon', 25) is True
        assert fc.isTitle('a quiet day in macon', 5) is False


class TestPunctuateTitle:
    def test_adds_the_missing_full_stop(self):
        assert fc.punctuate_title('THREE NEGROES LYNCHED') == 'THREE NEGROES LYNCHED.'

    def test_leaves_existing_stoppers_alone(self):
        assert fc.punctuate_title('MAN SHOT DEAD!') == 'MAN SHOT DEAD!'
        assert fc.punctuate_title('Was he guilty?') == 'Was he guilty?'
        assert fc.punctuate_title('MAN SHOT DEAD.') == 'MAN SHOT DEAD.'

    def test_strips_whitespace(self):
        assert fc.punctuate_title('  MAN SHOT DEAD  ') == 'MAN SHOT DEAD.'

    def test_empty(self):
        assert fc.punctuate_title('') == ''
        assert fc.punctuate_title(None) == ''

    def test_the_splitter_problem_is_fixed(self):
        # a headline glued to the first sentence is the bug the routine exists for
        headline = fc.punctuate_title('THREE NEGROES LYNCHED')
        assert headline.split('.')[0] == 'THREE NEGROES LYNCHED'
