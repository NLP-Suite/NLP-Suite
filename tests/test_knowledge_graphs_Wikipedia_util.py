"""Tests for the Wikipedia annotator's lookup logic.

The network call is stubbed with a fake session, so these run offline and assert on how the MediaWiki
response is interpreted -- normalization, redirects, missing pages and disambiguation pages.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import knowledge_graphs_Wikipedia_util as wiki  # noqa: E402


class TestLookupTitle:
    def test_plain_name_is_unchanged(self):
        assert wiki._lookup_title('Atlanta') == 'Atlanta'
        assert wiki._lookup_title('Atlanta Constitution') == 'Atlanta Constitution'

    def test_honorific_is_stripped(self):
        # newspapers name people by title; Wikipedia files them under the bare name
        assert wiki._lookup_title('Sheriff Jim Cobb') == 'Jim Cobb'
        assert wiki._lookup_title('Governor Hugh Dorsey') == 'Hugh Dorsey'
        assert wiki._lookup_title('Mr. Smith') == 'Smith'

    def test_several_honorifics_are_stripped(self):
        assert wiki._lookup_title('Colonel Sir Henry Clinton') == 'Henry Clinton'

    def test_a_lone_honorific_survives(self):
        # 'Sheriff' by itself is a word worth linking; stripping would leave nothing
        assert wiki._lookup_title('Sheriff') == 'Sheriff'

    def test_calendar_words_are_skipped(self):
        for word in ['May', 'january', 'Sept.', 'Monday']:
            assert wiki._lookup_title(word) == ''

    def test_calendar_word_inside_a_name_is_kept(self):
        assert wiki._lookup_title('May Department Stores') == 'May Department Stores'

    def test_empty(self):
        assert wiki._lookup_title('') == ''
        assert wiki._lookup_title('   ') == ''


class _FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _FakeSession:
    """Returns one canned MediaWiki payload and records the titles asked for."""

    def __init__(self, payload):
        self.payload = payload
        self.requested = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.requested.append(params['titles'].split('|'))
        return _FakeResponse(self.payload)


PAYLOAD = {'query': {
    'normalized': [{'from': 'lynching', 'to': 'Lynching'}],
    'redirects': [{'from': 'Atlanta Constitution', 'to': 'The Atlanta Journal-Constitution'}],
    'pages': {
        '1': {'title': 'Atlanta'},
        '2': {'title': 'The Atlanta Journal-Constitution'},
        '3': {'title': 'Jim Cobb'},
        '4': {'title': 'Macon', 'pageprops': {'disambiguation': ''}},
        '-1': {'title': 'Zzzqqq', 'missing': ''},
        '5': {'title': 'Lynching'},
    }}}


class TestBatchQuery:
    def _run(self, phrases):
        session = _FakeSession(PAYLOAD)
        return wiki._batch_query_wikipedia(phrases, 'red', session), session

    def test_existing_article_is_linked(self):
        cache, _ = self._run(['Atlanta'])
        url, label, color = cache['Atlanta']
        assert url == 'https://en.wikipedia.org/wiki/Atlanta'
        assert label == wiki.ONTOLOGY_LABEL
        assert color == 'red'

    def test_redirect_is_followed(self):
        cache, _ = self._run(['Atlanta Constitution'])
        assert cache['Atlanta Constitution'][0].endswith('The_Atlanta_Journal-Constitution')

    def test_normalization_is_followed(self):
        cache, _ = self._run(['lynching'])
        assert cache['lynching'][0].endswith('/Lynching')

    def test_missing_page_is_not_linked(self):
        cache, _ = self._run(['Zzzqqq'])
        assert cache['Zzzqqq'] is None

    def test_disambiguation_page_is_not_linked(self):
        # linking to a page listing nine different Macons annotates nothing
        cache, _ = self._run(['Macon'])
        assert cache['Macon'] is None

    def test_honorific_phrase_resolves_but_keeps_its_own_key(self):
        cache, session = self._run(['Sheriff Jim Cobb'])
        assert session.requested[0] == ['Jim Cobb']          # asked without the honorific
        assert cache['Sheriff Jim Cobb'][0].endswith('/Jim_Cobb')   # stored under the phrase as written

    def test_calendar_word_is_never_queried(self):
        cache, session = self._run(['May'])
        assert cache['May'] is None
        assert session.requested == []                       # no request made at all

    def test_titles_are_deduplicated(self):
        _, session = self._run(['Sheriff Jim Cobb', 'Jim Cobb'])
        assert session.requested[0] == ['Jim Cobb']          # one title, not two

    def test_every_phrase_gets_a_key(self):
        phrases = ['Atlanta', 'Macon', 'May', 'Zzzqqq']
        cache, _ = self._run(phrases)
        assert set(cache) == set(phrases)

    def test_pipe_in_a_phrase_is_not_sent(self):
        # '|' separates titles in the API, so a phrase containing one would corrupt the batch
        cache, session = self._run(['Atlanta|Macon'])
        assert cache['Atlanta|Macon'] is None
        assert session.requested == []

    def test_no_phrases_makes_no_request(self):
        cache, session = self._run([])
        assert cache == {}
        assert session.requested == []
