"""The vis.js network pages' timeline must update the graph ONCE per step.

Roberto, 4 Oct 2026, on a network of ~1,900 nodes and edges: "The time bar does not move". Every step called
nodes.update / edges.update once per item, and each call makes vis-network redraw and re-run its physics, so the page
froze after a step or two. The templates are checked as text: charts_util imports the heavy libraries the tests
stub, so the page cannot be generated here."""
import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'charts_util.py')


def _src():
    with open(SRC, encoding='utf-8-sig') as f:
        return f.read()


def test_no_per_item_update_in_the_network_templates():
    s = _src()
    assert not re.search(r'nodes\.update\(\{\{ id: n\.id', s)
    assert not re.search(r'edges\.update\(\{\{ id: e\.id', s)


def test_every_batch_is_flushed_once():
    s = _src()
    declared = s.count('var nu = [], eu = [];')
    assert declared >= 3
    assert s.count('nodes.update(nu); edges.update(eu);') == declared


def test_each_template_defines_the_edge_colours_it_uses():
    s = _src()
    # the second template used origEdgeColors in its timeline without defining it
    for m in re.finditer(r'function applyTimeFilter\(idx\)', s):
        before = s[:m.start()]
        start = before.rfind('new vis.Network(')
        assert start >= 0
        assert 'var origEdgeColors = {{}};' in before[start:], 'template at offset %d' % m.start()
