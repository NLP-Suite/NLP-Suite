"""The folium pin-map popup: a web address (the Family Archive's record link, often
over 200 characters) is a whole, clickable link, not text cut at 200. Roberto, 26 Sept 2026."""
import math
import sys
import types
from unittest.mock import MagicMock

# CI installs pytest only: folium is imported at module top
for _name in ('folium', 'folium.plugins'):
    sys.modules.setdefault(_name, MagicMock())

import GIS_folium_util as gf  # noqa: E402


def _isna(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


# pandas is a MagicMock under conftest; the popup only needs isna / notna
gf.pd = types.SimpleNamespace(isna=_isna, notna=lambda v: not _isna(v))


def test_long_web_address_is_whole_clickable_link():
    url = 'https://onedrive.live.com/?id=' + 'A' * (300 - len('https://onedrive.live.com/?id='))
    assert len(url) == 300
    out = gf._build_popup_html({'record link': url}, ['record link'])
    assert out == f'<b>record link</b>: <a href="{url}" target="_blank">open</a>'


def test_web_address_is_escaped():
    out = gf._build_popup_html({'record link': 'https://x.org/?a=1&b="2"'}, ['record link'])
    assert 'href="https://x.org/?a=1&amp;b=&quot;2&quot;"' in out


def test_long_text_is_still_cut_at_200():
    text = 'word ' * 100
    out = gf._build_popup_html({'Sentence': text}, ['Sentence'])
    assert out == '<b>Sentence</b>: ' + text.strip()[:200] + '...'


def test_plain_value_is_not_a_link():
    out = gf._build_popup_html({'Note': 'see www.example.org'}, ['Note'])
    assert out == '<b>Note</b>: see www.example.org'
    assert '<a ' not in out
