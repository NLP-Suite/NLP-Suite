# -*- coding: utf-8 -*-
"""Make a folium TimestampedGeoJson map's play button actually play.

WHY. The Leaflet.TimeDimension that folium loads has two faults that together
leave the slider dead on a historical corpus (found 21 Sept 2026: "Nothing
happens when hitting the arrow to run"):

  1. It ignores the period folium hands it. Its timeline becomes ONE date,
     the layer's own dates are intersected down to that one, and play has
     nowhere to go.
  2. With no duration, the layer keeps only what falls between time 0 and
     the current time - and time 0 is 1 January 1970. Every record before
     1970 (negative milliseconds) is dropped from the map.

So, after folium writes the page, the timeline is given its stops outright
(times: [...]), the layer is told not to rewrite them, and it is given a
window of five centuries. The step is chosen from the span of the data: a
year when it is longer than about a decade, a month when longer than a
year, otherwise a day - one day a step over eighty years is thirty thousand
presses of play.

Stdlib only, so it is unit-testable without folium or pandas.
"""
import datetime
import json
import re

EPOCH = datetime.datetime(1970, 1, 1)
DAY_MS = 86400000


def period_for(first, last):
    """'P1Y', 'P1M' or 'P1D' for data spanning first..last (datetimes)."""
    span = (last - first).days
    return 'P1Y' if span > 3650 else 'P1M' if span > 365 else 'P1D'


def date_format(period):
    """The slider's date label for that step: a year shows as 1859, not 1859-12-31."""
    return {'P1Y': 'YYYY', 'P1M': 'YYYY-MM'}.get(period, 'YYYY-MM-DD')


def _end_of(day):
    """The last millisecond of that calendar day, in ms since 1970 (negative before it)."""
    start = datetime.datetime(day.year, day.month, day.day) - EPOCH
    return int(start.total_seconds() * 1000) + DAY_MS - 1


def stops(first, last, period):
    """The slider's stops: the END of every year (month, day) from first's to
    last's, so the stop labelled 1859 shows everything dated up to its close."""
    out = []
    if period == 'P1Y':
        for year in range(first.year, last.year + 1):
            out.append(_end_of(datetime.date(year, 12, 31)))
    elif period == 'P1M':
        year, month = first.year, first.month
        while (year, month) <= (last.year, last.month):
            nxt = datetime.date(year + (month == 12), month % 12 + 1, 1)
            out.append(_end_of(nxt - datetime.timedelta(days=1)))
            year, month = nxt.year, nxt.month
    else:
        day = datetime.date(first.year, first.month, first.day)
        end = datetime.date(last.year, last.month, last.day)
        while day <= end:
            out.append(_end_of(day))
            day += datetime.timedelta(days=1)
    return out


def patch(html, stop_list):
    """(html, True) with the slider fixed, or (html unchanged, False) when the
    page is not in the form folium writes - which the caller must say."""
    period = re.search(r'period: "P[^"]*",', html)
    if not period or 'updateTimeDimension: true,' not in html or 'duration: undefined,' not in html:
        return html, False
    html = html.replace(period.group(0), 'times: %s,' % json.dumps(list(stop_list)), 1)
    html = html.replace('updateTimeDimension: true,', 'updateTimeDimension: false,', 1)
    html = html.replace('duration: undefined,', 'duration: "P500Y",', 1)
    return html, True


def patch_file(path, stop_list):
    """True when the saved page was fixed."""
    with open(path, encoding='utf-8') as fh:
        html = fh.read()
    html, ok = patch(html, stop_list)
    if ok:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(html)
    return ok
