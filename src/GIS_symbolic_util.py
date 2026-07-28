# Written by Roberto Franzosi & Claude, 2026
# Narrative / Symbolic Space Analyzer — pipeline engine
# (see docs/Narrative_Symbolic_Space_design.md).
#
# Phase 2: split place mentions into geocodable (real) vs symbolic (routed to
#          the spatial-domain typology).
# Phase 3: gender x space cross-tabulation + chi-square / Cramer's V + heatmap.
#
# Deliberately GUI-free (no GUI_util / install guard) so the analysis engine is
# importable and unit-testable on its own; the GUI/main carries the guard and
# feeds this NER/SVO + gender data.

import os

import GIS_symbolic_typology_util as typology

# Space types that are inherently symbolic/interior even if a string happens to
# weakly geocode (e.g. "Kitchen" is a hamlet somewhere) — the guard from the memo.
_INHERENTLY_SYMBOLIC = {'domestic_interior', 'threshold_liminal'}

# Prepositions that mark a locative oblique ("in the cupboard", "to the door");
# used by the CoNLL dependency extractor to keep only spatial obl/nmod nouns.
_SPATIAL_PREP = {'in', 'into', 'inside', 'on', 'onto', 'at', 'to', 'toward', 'towards',
                 'through', 'across', 'behind', 'under', 'beneath', 'below', 'above',
                 'near', 'by', 'within', 'up', 'down', 'out', 'outside', 'around',
                 'past', 'along', 'over', 'from'}

# Subject tags that are a REFERENCE to a character rather than a character: PRON covers
# he/she/they/which in the Universal tagset, PRP/PRP$/WP/WDT the Penn one, so a CoNLL
# table from any of the Suite's parsers is handled.
_PRONOUN_POS = {'PRON', 'PRP', 'PRP$', 'WP', 'WP$', 'WDT', 'DET'}


# ---- Phase 2: geocodable vs symbolic --------------------------------------

def _default_geocoder():
    """A cached, rate-limited geopy Nominatim geocode fn, or None if unavailable."""
    try:
        from geopy.geocoders import Nominatim
        from geopy.extra.rate_limiter import RateLimiter
    except Exception:
        return None
    geolocator = Nominatim(user_agent='NLP_Suite_symbolic_space')
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    cache = {}

    def _fn(place):
        key = str(place).strip().lower()
        if not key:
            return None
        if key in cache:
            return cache[key]
        try:
            loc = geocode(place)
            result = (loc.latitude, loc.longitude) if loc else None
        except Exception:
            result = None
        cache[key] = result
        return result

    return _fn


def split_by_geocoding(mentions, geocode_fn=None):
    """Classify each place mention as geocodable (real) or symbolic.

    *mentions*: iterable of place strings, or (surface, lemma) pairs.
    *geocode_fn*: callable place -> (lat, lng) or None. If None, uses the default
    Nominatim geocoder when geopy is present, else nothing geocodes.

    Returns a list of dicts with: mention, lemma, geocoded (bool), lat, lng,
    space_category (always from the typology), symbolic (bool).
    """
    if geocode_fn is None:
        geocode_fn = _default_geocoder()
    out = []
    for m in mentions:
        if isinstance(m, (tuple, list)):
            surface = m[0]
            lemma = m[1] if len(m) > 1 and m[1] else m[0]
        else:
            surface = lemma = m
        category = typology.classify(lemma)
        coord = geocode_fn(surface) if geocode_fn else None
        geocoded = coord is not None
        symbolic = (not geocoded) or (category in _INHERENTLY_SYMBOLIC)
        out.append({
            'mention': surface,
            'lemma': lemma,
            'geocoded': geocoded,
            'lat': coord[0] if coord else None,
            'lng': coord[1] if coord else None,
            'space_category': category,
            'symbolic': symbolic,
        })
    return out


# ---- Phase 3: gender x space ----------------------------------------------

def classify_observations(observations):
    """(attribute, location) pairs -> (attribute_lower, space_category) pairs.

    The attribute is any categorical actor attribute cross-tabbed against space -
    gender, race, class, age, ... - not just gender.
    """
    result = []
    for attribute, location in observations:
        a = (str(attribute) if attribute is not None else 'unknown').strip().lower()
        result.append((a or 'unknown', typology.classify(location)))
    return result


def attribute_space_crosstab(observations, classify=True,
                             drop_unclassified=True, drop_unknown_attribute=True):
    """pandas contingency table (attribute rows x space-category columns).

    observations: (attribute, location) if classify=True, else (attribute, category).
    The attribute is gender / race / class / ... (a categorical actor attribute).
    """
    import pandas as pd
    if classify:
        pairs = classify_observations(observations)
    else:
        pairs = [((str(a) if a is not None else 'unknown').strip().lower(), c)
                 for a, c in observations]
    if drop_unclassified:
        pairs = [(a, c) for a, c in pairs if c != typology.UNCLASSIFIED]
    if drop_unknown_attribute:
        pairs = [(a, c) for a, c in pairs if a not in ('unknown', '', 'nan')]
    if not pairs:
        return pd.DataFrame()
    df = pd.DataFrame(pairs, columns=['attribute', 'space'])
    return pd.crosstab(df['attribute'], df['space'])


def crosstab_stats(table):
    """chi-square, p, dof, Cramer's V, and standardized (Pearson) residuals."""
    if table is None or getattr(table, 'size', 0) == 0 or table.values.sum() == 0:
        return {}
    import numpy as np
    import pandas as pd
    from scipy.stats import chi2_contingency
    chi2, p, dof, expected = chi2_contingency(table.values)
    n = table.values.sum()
    k = min(table.shape) - 1
    cramers_v = float((chi2 / (n * k)) ** 0.5) if k > 0 else 0.0
    with np.errstate(divide='ignore', invalid='ignore'):
        resid = (table.values - expected) / np.sqrt(expected)
    residuals = pd.DataFrame(resid, index=table.index, columns=table.columns)
    return {'chi2': float(chi2), 'p_value': float(p), 'dof': int(dof),
            'cramers_v': cramers_v, 'residuals': residuals, 'n': int(n)}


def plot_attribute_space_heatmap(table, output_path, values='residuals', stats=None,
                                 title='Attribute × non-geocodable space'):
    """Save a heatmap PNG. values='counts', or 'residuals' (needs stats)."""
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    if values == 'residuals' and stats and 'residuals' in stats:
        data = stats['residuals']
        cmap = 'RdBu_r'
        bar_label = 'Std. residual (red = more, blue = less than expected)'
        vmax = float(np.nanmax(np.abs(data.values))) or 1.0
        vmin = -vmax
    else:
        data = table
        cmap = 'YlOrRd'
        bar_label = 'Count'
        vmin, vmax = 0, (float(np.nanmax(data.values)) if data.size else 1)

    fig, ax = plt.subplots(figsize=(max(6, data.shape[1] * 1.15),
                                    max(3, data.shape[0] * 0.9)))
    im = ax.imshow(data.values, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    ax.set_xticks(range(data.shape[1]))
    ax.set_xticklabels(data.columns, rotation=40, ha='right', fontsize=8)
    ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels(data.index, fontsize=9)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data.values[i, j]
            ax.text(j, i, ('{:.1f}'.format(v) if values == 'residuals' else int(v)),
                    ha='center', va='center', fontsize=8)
    ttl = title
    if stats and stats.get('cramers_v') is not None:
        ttl += "  (Cramer's V = {:.2f}, p = {:.3g})".format(
            stats['cramers_v'], stats['p_value'])
    ax.set_title(ttl, fontsize=10)
    plt.colorbar(im, ax=ax, shrink=0.8, label=bar_label)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path


def bipartite_edges(table):
    """Edge list [(gender, space_category, weight), ...] for a gender<->space network."""
    edges = []
    for g in table.index:
        for c in table.columns:
            w = int(table.loc[g, c])
            if w > 0:
                edges.append((g, c, w))
    return edges


def narrative_transitions(sequence, classify=True, collapse_repeats=True,
                          keep_unclassified=False):
    """Turn an ordered sequence of locations into a movement through space-types.

    *sequence*: ordered location strings (narrative order), or space-categories
    if classify=False. Returns (path, edges):
      path  = list of space-categories in narrative order (consecutive repeats
              collapsed when collapse_repeats),
      edges = list of (from_category, to_category, count) directed transitions.
    This is the symbolic-space analogue of the geographic character-movement map:
    the "movement" is between TYPES of space, not map coordinates.
    """
    from collections import Counter
    if classify:
        cats = [typology.classify(loc) for loc in sequence]
    else:
        cats = list(sequence)
    if not keep_unclassified:
        cats = [c for c in cats if c != typology.UNCLASSIFIED]
    path = []
    for c in cats:
        if not (collapse_repeats and path and path[-1] == c):
            path.append(c)
    counts = Counter(zip(path, path[1:]))
    edges = [(a, b, n) for (a, b), n in counts.items()]
    return path, edges


def plot_transition_graph(edges, output_path,
                          title='Movement through non-geocodable space'):
    """Directed graph of space-type transitions. edges = [(from, to, count), ...].
    Nodes laid out on a circle; arrow width scales with transition count."""
    import math
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    nodes = []
    for a, b, _ in edges:
        for n in (a, b):
            if n not in nodes:
                nodes.append(n)
    if not nodes:
        return None
    n = len(nodes)
    pos = {}
    for i, name in enumerate(nodes):
        ang = 2 * math.pi * i / n - math.pi / 2
        pos[name] = (math.cos(ang) if n > 1 else 0.0,
                     math.sin(ang) if n > 1 else 0.0)
    maxc = max((c for _, _, c in edges), default=1)

    fig, ax = plt.subplots(figsize=(8, 8))
    for a, b, c in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=20,
            lw=1 + 3 * c / maxc, color='#555555', alpha=0.85,
            connectionstyle='arc3,rad=0.15', shrinkA=20, shrinkB=20))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(c), fontsize=8,
                color='#b00000', ha='center', va='center')
    for name, (x, y) in pos.items():
        ax.scatter([x], [y], s=2000, c='#cfe3f5', edgecolors='#33667a',
                   linewidths=1.5, zorder=3)
        ax.text(x, y, name.replace('_', '\n'), fontsize=8, ha='center',
                va='center', zorder=4)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')
    ax.set_title(title, fontsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path


def save_crosstab_csv(table, output_path, stats=None):
    """Write the contingency table (and residuals alongside, if provided) to CSV."""
    table.to_csv(output_path, encoding='utf-8-sig')
    if stats and 'residuals' in stats:
        base, ext = os.path.splitext(output_path)
        stats['residuals'].to_csv(base + '_residuals' + ext, encoding='utf-8-sig')
    return output_path


# ---- BUILD pipeline: actor-in-space events from a CoNLL corpus -------------

def symbolic_movement_timeline(events_csv, outputDir, top_n=8, actor_col='actor',
                               location_col='', title=''):
    """An INTERACTIVE view of movement through symbolic space, as one HTML file.

    The geocodable map animates characters across a real map because its places
    have coordinates. These do not: a kitchen has no latitude, and putting
    'domestic_interior' somewhere in the Atlantic to reuse a map would be a
    picture of nothing. The honest equivalent of a map here is a TIMELINE —
    narrative position across, kind of space up the side, one track per
    character — with a cursor you drag or play. Where two tracks meet, two
    characters are in the same kind of space at the same point in the story,
    which is the thing the static transition graph cannot show.

    Self-contained: no basemap, no libraries, no internet. Returns the html path
    or '' if there was nothing to draw.
    """
    import json
    import pandas as pd

    try:
        df = pd.read_csv(events_csv, encoding='utf-8-sig')
    except Exception:
        try:
            df = pd.read_csv(events_csv, encoding='ISO-8859-1')
        except Exception:
            return ''
    if actor_col not in df.columns:
        return ''

    # the space TYPE: already there in a BUILD table, otherwise classified from whichever column
    # holds the place words, so a hand-made csv works too
    space_col = 'space_type'
    if space_col not in df.columns:
        if not location_col or location_col not in df.columns:
            return ''
        df = df.copy()
        df[space_col] = [typology.classify(str(v)) for v in df[location_col]]

    df = df[df[space_col].astype(str).str.strip().ne('')
            & df[space_col].astype(str).ne(typology.UNCLASSIFIED)].copy()
    if df.empty:
        return ''

    # one narrative axis for the whole corpus: sentence IDs restart in every document
    if 'Sentence ID' in df.columns:
        df['_sent'] = pd.to_numeric(df['Sentence ID'], errors='coerce').fillna(0)
    else:
        df['_sent'] = range(len(df))
    if 'Document ID' in df.columns:
        lengths = df.groupby('Document ID')['_sent'].max().sort_index()
        offsets = lengths.cumsum().shift(1).fillna(0)
        df['_pos'] = df['Document ID'].map(offsets).fillna(0) + df['_sent']
    else:
        df['_pos'] = df['_sent']
    df = df.sort_values('_pos')

    counts = df[actor_col].astype(str).value_counts()
    actors = [a for a in counts.head(top_n).index if str(a).strip()]
    if not actors:
        return ''

    spaces = [c for c in typology.CATEGORIES
              if c in set(df[space_col].astype(str))]
    doc_col = next((c for c in ('Document', 'Document ID') if c in df.columns), '')

    tracks = []
    for actor in actors:
        rows = df[df[actor_col].astype(str) == actor]
        tracks.append({
            'actor': str(actor),
            'points': [{
                'x': float(r['_pos']),
                'space': str(r[space_col]),
                'doc': str(r[doc_col]) if doc_col else '',
                'sentence': str(r.get('Sentence', ''))[:300],
                'word': str(r.get('space_noun', '')),
            } for _, r in rows.iterrows()],
        })

    payload = {
        'title': title or os.path.basename(events_csv),
        'spaces': spaces,
        'tracks': tracks,
        'docs': sorted({t['doc'] for tr in tracks for t in tr['points'] if t['doc']}),
        'xmin': float(df['_pos'].min()),
        'xmax': float(df['_pos'].max()),
    }

    html = _TIMELINE_HTML.replace('__DATA__', json.dumps(payload, ensure_ascii=False))
    output_path = os.path.join(outputDir, 'symbolic_space_movement_timeline.html')
    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    return output_path


# The timeline page. Vanilla SVG and JS on purpose: it has to open on any machine,
# from a folder, with no network - the same promise the family-archive HTML makes.
_TIMELINE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Movement through symbolic space</title>
<style>
 body{font:14px/1.5 "Segoe UI",Inter,sans-serif;margin:0;padding:18px 24px;color:#222;background:#fff;}
 h1{font-size:19px;margin:0 0 2px;} .sub{color:#666;font-size:12px;margin-bottom:14px;}
 #wrap{overflow-x:auto;border:1px solid #e3e3e3;border-radius:6px;padding:8px 0 0;}
 .ctl{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:12px 0;}
 button{font:inherit;padding:5px 14px;border:1px solid #c9c9c9;background:#f7f7f7;border-radius:5px;cursor:pointer;}
 button:hover{background:#eee;}
 input[type=range]{flex:1;min-width:240px;}
 select{font:inherit;padding:4px;}
 .legend{display:flex;gap:12px;flex-wrap:wrap;margin:6px 0 2px;}
 .legend span{display:flex;align-items:center;gap:5px;font-size:12px;cursor:pointer;user-select:none;}
 .legend i{width:11px;height:11px;border-radius:50%;display:inline-block;}
 .legend .off{opacity:.3;}
 #read{margin-top:10px;padding:10px 12px;background:#fafafa;border:1px solid #eee;border-radius:6px;
       font-size:13px;min-height:44px;}
 .muted{color:#888;}
 text{font:11px "Segoe UI",sans-serif;fill:#555;}
 .gl{stroke:#eee;} .cursor{stroke:#c1121f;stroke-width:1.5;}
</style></head><body>
<h1>Movement through symbolic space</h1>
<div class="sub" id="sub"></div>

<div class="legend" id="legend"></div>
<div id="wrap"><svg id="plot"></svg></div>

<div class="ctl">
  <button id="play">▶ Play</button>
  <input type="range" id="scrub" min="0" max="1000" value="1000">
  <span id="posn" class="muted"></span>
  <label>Document
    <select id="doc"><option value="">all</option></select>
  </label>
</div>
<div id="read" class="muted">Drag the slider, or press Play. Click a point to read its sentence.</div>

<script>
var DATA = __DATA__;
var COLORS = ['#0b5394','#b35e3c','#38761d','#7f6000','#4c1130','#134f5c','#783f04','#20124d'];
var PAD = {l:150, r:24, t:14, b:34}, ROW = 34;
var svg = document.getElementById('plot'), hidden = {}, doc = '', playing = null;

function tracks(){
  return DATA.tracks.filter(function(t){ return !hidden[t.actor]; });
}
function pointsOf(t){
  return t.points.filter(function(p){ return !doc || p.doc === doc; });
}
function xOf(p, w){
  var span = (DATA.xmax - DATA.xmin) || 1;
  return PAD.l + (p - DATA.xmin) / span * (w - PAD.l - PAD.r);
}
function yOf(space){
  return PAD.t + DATA.spaces.indexOf(space) * ROW + ROW / 2;
}

function draw(cut){
  var w = Math.max(900, DATA.spaces.length ? svg.parentNode.clientWidth - 16 : 900);
  var h = PAD.t + DATA.spaces.length * ROW + PAD.b;
  svg.setAttribute('width', w); svg.setAttribute('height', h);
  var out = [];
  DATA.spaces.forEach(function(s, i){
    var y = PAD.t + i * ROW + ROW / 2;
    out.push('<line class="gl" x1="'+PAD.l+'" y1="'+y+'" x2="'+(w-PAD.r)+'" y2="'+y+'"/>');
    out.push('<text x="'+(PAD.l-10)+'" y="'+(y+4)+'" text-anchor="end">'+s+'</text>');
  });
  tracks().forEach(function(t, i){
    var color = COLORS[DATA.tracks.indexOf(t) % COLORS.length];
    var pts = pointsOf(t).filter(function(p){ return p.x <= cut; });
    var d = '';
    pts.forEach(function(p, k){
      var x = xOf(p.x, w), y = yOf(p.space);
      if (k === 0) { d += 'M' + x + ',' + y; }
      else { d += 'L' + x + ',' + yOf(pts[k-1].space) + 'L' + x + ',' + y; }
    });
    if (d) out.push('<path d="'+d+'" fill="none" stroke="'+color+'" stroke-width="1.6" opacity=".75"/>');
    pts.forEach(function(p, k){
      out.push('<circle cx="'+xOf(p.x, w)+'" cy="'+yOf(p.space)+'" r="3.4" fill="'+color+
               '" opacity=".9" data-t="'+DATA.tracks.indexOf(t)+'" data-k="'+k+'" style="cursor:pointer"/>');
    });
    var last = pts[pts.length-1];
    if (last) {
      out.push('<circle cx="'+xOf(last.x, w)+'" cy="'+yOf(last.space)+'" r="6.5" fill="none" stroke="'+
               color+'" stroke-width="2"/>');
    }
  });
  var cx = xOf(cut, w);
  out.push('<line class="cursor" x1="'+cx+'" y1="'+PAD.t+'" x2="'+cx+'" y2="'+(h-PAD.b+6)+'"/>');
  out.push('<text x="'+PAD.l+'" y="'+(h-10)+'">sentence '+Math.round(DATA.xmin)+'</text>');
  out.push('<text x="'+(w-PAD.r)+'" y="'+(h-10)+'" text-anchor="end">'+Math.round(DATA.xmax)+'</text>');
  svg.innerHTML = out.join('');
  document.getElementById('posn').textContent = 'sentence ' + Math.round(cut);
}

function cutFromSlider(){
  var f = document.getElementById('scrub').value / 1000;
  return DATA.xmin + f * (DATA.xmax - DATA.xmin);
}
function redraw(){ draw(cutFromSlider()); }

document.getElementById('scrub').addEventListener('input', redraw);
document.getElementById('play').addEventListener('click', function(){
  var b = this;
  if (playing) { clearInterval(playing); playing = null; b.textContent = '▶ Play'; return; }
  var s = document.getElementById('scrub');
  if (+s.value >= 1000) s.value = 0;
  b.textContent = '❚❚ Pause';
  playing = setInterval(function(){
    s.value = Math.min(1000, +s.value + 4);
    redraw();
    if (+s.value >= 1000) { clearInterval(playing); playing = null; b.textContent = '▶ Play'; }
  }, 40);
});
document.getElementById('doc').addEventListener('change', function(){ doc = this.value; redraw(); });

svg.addEventListener('click', function(e){
  var c = e.target;
  if (c.tagName !== 'circle' || !c.hasAttribute('data-t')) return;
  var t = DATA.tracks[+c.getAttribute('data-t')];
  var p = pointsOf(t)[+c.getAttribute('data-k')];
  if (!p) return;
  document.getElementById('read').className = '';
  document.getElementById('read').innerHTML =
    '<b>' + t.actor + '</b> — <b>' + p.space + '</b> ("' + p.word + '")' +
    (p.doc ? ' · ' + p.doc : '') + '<br>' + (p.sentence || '<span class="muted">(no sentence)</span>');
});

(function init(){
  document.getElementById('sub').textContent =
    DATA.title + ' · ' + DATA.tracks.length + ' characters · ' + DATA.spaces.length +
    ' kinds of space · narrative position runs left to right, documents in order';
  var lg = document.getElementById('legend');
  DATA.tracks.forEach(function(t, i){
    var s = document.createElement('span');
    s.innerHTML = '<i style="background:' + COLORS[i % COLORS.length] + '"></i>' + t.actor +
                  ' <span class="muted">(' + t.points.length + ')</span>';
    s.onclick = function(){
      hidden[t.actor] = !hidden[t.actor];
      s.className = hidden[t.actor] ? 'off' : '';
      redraw();
    };
    lg.appendChild(s);
  });
  var sel = document.getElementById('doc');
  DATA.docs.forEach(function(d){
    var o = document.createElement('option'); o.value = d; o.textContent = d; sel.appendChild(o);
  });
  redraw();
  window.addEventListener('resize', redraw);
})();
</script></body></html>
"""


def extract_actor_space_events(conll_file, outputDir):
    """Build the actor-in-(non-geocodable)-space table from a CoNLL dependency table.

    For each sentence, find every place noun whose lemma classifies to a space TYPE and
    that sits in a locative oblique (obl/nmod under a spatial preposition), then walk the
    dependency Head up to the governing predicate and down to its subject = the acting
    CHARACTER. Writes one row per actor-in-space event:
        Document ID, Sentence ID (order), actor, actor_pos, space_noun, space_type,
        preposition, Sentence.
    This is the table the DYNAMIC and STATIC analyses read (add the actor ATTRIBUTE by
    hand or via the gender annotator).

    PRONOUN subjects are DROPPED. "he", "they", "which" are not characters: they are
    references to characters, and left in they accumulate as the largest "actors" in
    every crosstab while telling you nothing about anybody. Resolving them to the people
    they stand for is what coreference resolution does, and running it BEFORE this step
    is how those events are recovered rather than lost.

    Returns (output csv path, dropped) where *dropped* counts the pronoun-subject events
    left out; the caller reports it, since dropping them silently would look like a
    corpus with very little movement in it. The path is '' if nothing was produced (e.g.
    the input is not a CoNLL table).
    """
    import pandas as pd
    try:
        df = pd.read_csv(conll_file, encoding='utf-8', dtype=str, keep_default_na=False)
    except Exception:
        return '', 0
    needed = {'ID', 'Form', 'Lemma', 'POS', 'Head', 'DepRel', 'Sentence ID', 'Document ID'}
    if not needed.issubset(set(df.columns)):
        return '', 0

    rows = []
    dropped_pronouns = 0
    for (doc, sent), g in df.groupby(['Document ID', 'Sentence ID'], sort=False):
        tok, kids = {}, {}
        for _, r in g.iterrows():
            try:
                tid = int(float(r['ID']))
                head = int(float(r['Head'])) if str(r['Head']).strip() else 0
            except ValueError:
                continue
            tok[tid] = {'form': r['Form'], 'lemma': r['Lemma'], 'pos': r['POS'],
                        'head': head, 'deprel': r['DepRel']}
            kids.setdefault(head, []).append(tid)
        text = ' '.join(tok[i]['form'] for i in sorted(tok))
        for tid, t in tok.items():
            if t['pos'] not in ('NOUN', 'PROPN'):
                continue
            if t['deprel'] not in ('obl', 'nmod', 'obl:loc', 'obl:tmod'):
                continue
            space_type = typology.classify(t['lemma'])
            if space_type == typology.UNCLASSIFIED:
                continue
            prep = ''
            for c in kids.get(tid, []):
                if tok[c]['deprel'] == 'case' and tok[c]['lemma'].lower() in _SPATIAL_PREP:
                    prep = tok[c]['lemma'].lower()
                    break
            if not prep:
                continue
            actor, gov = None, t['head']
            for _ in range(4):  # walk up through cop/aux/conj to the predicate carrying the subject
                subj = [c for c in kids.get(gov, []) if tok[c]['deprel'] in ('nsubj', 'nsubj:pass')]
                if subj:
                    actor = tok[subj[0]]
                    break
                gov = tok.get(gov, {}).get('head', 0)
                if gov == 0:
                    break
            if actor is None or not str(actor['form']).strip():
                continue
            # a pronoun is a reference to a character, not a character
            if str(actor['pos']).strip().upper() in _PRONOUN_POS:
                dropped_pronouns += 1
                continue
            rows.append({'Document ID': doc, 'Sentence ID': sent, 'actor': actor['form'],
                         'actor_pos': actor['pos'], 'space_noun': t['lemma'],
                         'space_type': space_type, 'preposition': prep, 'Sentence': text})
    if not rows:
        return '', dropped_pronouns
    base = os.path.splitext(os.path.basename(conll_file))[0] if conll_file else 'corpus'
    output_path = os.path.join(outputDir, 'NLP_GIS_symbolic_actor_space_events_' + base + '.csv')
    out = pd.DataFrame(rows, columns=['Document ID', 'Sentence ID', 'actor', 'actor_pos',
                                      'space_noun', 'space_type', 'preposition', 'Sentence'])

    # WHAT KIND of person each actor is - the attribute the STATIC analysis crosses against space.
    # Telling the reader to code it by hand was telling them to hand-code a corpus; the same
    # curated-lexicon-then-WordNet-hypernym method that classifies the SPACE classifies the ACTOR.
    # Common nouns only ("the sheriff", "a farmer", "the mob"): a proper name is left unclassified,
    # because WordNet does not know who Harry is.
    try:
        import GIS_symbolic_actor_typology_util as actor_typology
        out.insert(4, 'actor_type',
                   actor_typology.classify_series(out['actor'], out['actor_pos']))
    except Exception as e:
        print('GIS symbolic: actor types not added (%s)' % e)

    out.to_csv(output_path, index=False, encoding='utf-8-sig')
    return output_path, dropped_pronouns
