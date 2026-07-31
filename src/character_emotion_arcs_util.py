import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "character_emotion_arcs_util",
        ['os', 'csv', 'tkinter', 'nrclex', 'numpy', 'matplotlib', 'pandas', 'stanza']) == False:
    sys.exit(0)

import os
import csv
import re
import math
import numpy as np
import pandas as pd
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
from nrclex import NRCLex

import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_util

EIGHT_EMOTIONS = ["anger", "anticipation", "disgust", "fear",
                   "joy", "sadness", "surprise", "trust"]

NRC_COLORS = {
    "anger":        "#E24B4A",
    "anticipation": "#BA7517",
    "disgust":      "#D4537E",
    "fear":         "#1D9E75",
    "joy":          "#F9CB42",
    "sadness":      "#534AB7",
    "surprise":     "#378ADD",
    "trust":        "#639922",
}


def _score_sentence_nrc(text):
    emotion_obj = NRCLex(text)
    # NRCLex API drift: older versions expose .raw_emotion_scores (counts); some newer builds only
    # populate .affect_frequencies (normalized). Fall back so a version mismatch doesn't crash the
    # character emotion arcs -- either is fine here since we re-normalize over the 8 emotions below.
    raw = getattr(emotion_obj, 'raw_emotion_scores', None)
    if not raw:
        raw = getattr(emotion_obj, 'affect_frequencies', None) or {}
    total = sum(raw.get(e, 0) for e in EIGHT_EMOTIONS) or 1
    return {e: raw.get(e, 0) / total for e in EIGHT_EMOTIONS}


def _extract_persons_from_sentence(sent):
    persons = set()
    for ent in sent.ents:
        if ent.type == "PERSON":
            persons.add(ent.text.strip())
    return persons


def _strip_possessive(name):
    """"Harry's" and "Harrys" are Harry. NER hands back the possessive form of a
    name often enough that leaving it alone produced a separate character with
    1,890 sentences of its own in the Harry Potter corpus."""
    name = name.strip()
    for suffix in ("’s", "'s", "’", "'"):
        if name.endswith(suffix) and len(name) > len(suffix) + 1:
            return name[:-len(suffix)].strip()
    if len(name) > 2 and name.endswith('s') and not name.endswith('ss'):
        return name          # 'Harrys' -> left alone here; the map below folds it in
    return name


# Words that are not part of a name, and must not be what two names are matched on.
_TITLES = {'mr', 'mrs', 'ms', 'miss', 'dr', 'doctor', 'professor', 'prof', 'sir',
           'lady', 'lord', 'madam', 'madame', 'uncle', 'aunt', 'auntie', 'the',
           'a', 'an', 'of', 'and'}


def _name_tokens(name):
    """The words of a name that identify a person: no titles, no punctuation."""
    cleaned = re.sub(r"[^\w\s]", ' ', name.lower())
    return {w for w in cleaned.split() if w and w not in _TITLES}


def _normalize_character_name(name, canonical_map):
    """Fold a name into the one already seen for that person.

    Matching is on WORDS, and only when one name's words are all contained in
    the other's: "Harry" and "Mr. Potter" both fold into "Harry Potter". It used
    to be a raw substring test, which is a different thing entirely - "ron" is
    inside "the leaky cauld-RON", and "gran" inside "hermione GRAN-ger", so Ron
    and Hermione were absorbed into a pub and a grandmother.

    A name that could belong to two different people already seen is left alone.
    Uniqueness is the safeguard: guessing which character a mention belongs to
    would be worse than reporting them separately, and the CSV shows the split.

    *canonical_map* is shared by the WHOLE corpus. Rebuilt per document, each of
    199 Harry Potter files chose its own canonical form, so one person came out
    as Harry, Harry's, Harry Potter, Harrys and The Cave Harry.
    """
    name = _strip_possessive(name)
    lower = name.lower().strip()
    if not lower:
        return name
    # every entry is (the name to use, the tokens of THAT name) - an alias keeps
    # its canonical form's tokens, so aliases never widen what will match next
    if lower in canonical_map:
        return canonical_map[lower][0]

    tokens = _name_tokens(name)
    if tokens:
        candidates = {}
        for canon, canon_tokens in canonical_map.values():
            if canon_tokens and (tokens <= canon_tokens or canon_tokens <= tokens):
                candidates[canon] = canon_tokens
        if len(candidates) == 1:
            canon, canon_tokens = next(iter(candidates.items()))
            canonical_map[lower] = (canon, canon_tokens)
            return canon

    canonical_map[lower] = (name, tokens)
    return name


def analyze_file(filepath, nlp_pipeline, doc_id, canonical_map=None):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if not text.strip():
        return []

    doc = nlp_pipeline(text)
    # one map for the whole corpus when the caller keeps it; see
    # _normalize_character_name for why per-document maps split people up
    if canonical_map is None:
        canonical_map = {}
    rows = []

    for sent_idx, sent in enumerate(doc.sentences, 1):
        sent_text = sent.text
        persons = _extract_persons_from_sentence(sent)
        scores = _score_sentence_nrc(sent_text)

        normalized_persons = set()
        for p in persons:
            normalized_persons.add(_normalize_character_name(p, canonical_map))

        if not normalized_persons:
            normalized_persons = {"_NARRATOR/UNATTRIBUTED_"}

        for character in normalized_persons:
            row = {
                'Document ID': doc_id,
                'Document': IO_csv_util.dressFilenameForCSVHyperlink(filepath),
                'Sentence ID': sent_idx,
                'Sentence': sent_text,
                'Character': character,
            }
            for e in EIGHT_EMOTIONS:
                row[e.capitalize()] = round(scores[e], 4)
            rows.append(row)

    return rows


def analyze_conll_table(conll_path):
    """Same output as analyze_file, but DERIVED from an existing Stanza NER CoNLL table (Form + NER +
    Sentence ID + Document ID, one token per row) instead of re-parsing the corpus with Stanza NER. The
    Corpus Profiler already produced that table, so this turns a full ~1.5h re-NER into a groupby + the
    same (fast, lexicon-based) NRC scoring. Per (document, sentence, PERSON character) a row with the 8 NRC
    emotion scores; character names are normalized across the WHOLE corpus, exactly as analyze_file does
    it. Returns [] if the table lacks the needed columns (the caller then parses)."""
    import pandas as pd
    df = pd.read_csv(conll_path, encoding='utf-8', on_bad_lines='skip')
    formcol = 'Form' if 'Form' in df.columns else ('Word' if 'Word' in df.columns else None)
    if not formcol or not {'NER', 'Sentence ID', 'Document ID'}.issubset(df.columns):
        return []
    has_mwe = 'Multi-Word Expression' in df.columns
    has_doc = 'Document' in df.columns
    rows = []
    canonical_map = {}   # ONE map for the corpus, like analyze_file
    for doc_id, doc_g in df.groupby('Document ID', sort=True):
        doc_link = doc_g['Document'].iloc[0] if has_doc else ''
        for sent_id, g in doc_g.groupby('Sentence ID', sort=True):
            forms = [str(x) for x in g[formcol].tolist() if str(x) != 'nan']
            sent_text = ' '.join(forms)
            # PERSON entities: the Multi-Word Expression column holds the full name (e.g. 'Harry Potter'
            # for both its tokens); fall back to the token Form. Same set semantics as
            # _extract_persons_from_sentence(sent) over sent.ents of type PERSON.
            persons = set()
            for _, r in g[g['NER'].astype(str).str.contains('PERSON', na=False)].iterrows():
                mwe = str(r['Multi-Word Expression']) if has_mwe else ''
                name = (mwe if mwe and mwe.lower() != 'nan' else str(r[formcol])).strip()
                if name and name.lower() != 'nan':
                    persons.add(name)
            scores = _score_sentence_nrc(sent_text)
            normalized = {_normalize_character_name(p, canonical_map) for p in persons} or {"_NARRATOR/UNATTRIBUTED_"}
            for character in normalized:
                row = {
                    'Document ID': int(doc_id) if str(doc_id).isdigit() else doc_id,
                    'Document': doc_link,
                    'Sentence ID': int(sent_id) if str(sent_id).isdigit() else sent_id,
                    'Sentence': sent_text,
                    'Character': character,
                }
                for e in EIGHT_EMOTIONS:
                    row[e.capitalize()] = round(scores[e], 4)
                rows.append(row)
    return rows


def add_corpus_position(df):
    """A single sentence axis for the whole corpus, in document order.

    Sentence IDs restart at 1 in every document, so ordering by Sentence ID
    alone interleaves them - in the Harry Potter corpus, 199 files shuffled
    together, which is not a narrative order at all. Each document is offset by
    the length of the ones before it, giving a position that runs from the first
    sentence of the first document to the last of the last.
    """
    df = df.copy()
    lengths = df.groupby('Document ID')['Sentence ID'].max().sort_index()
    offsets = lengths.cumsum().shift(1).fillna(0).astype(int)
    df['Corpus Position'] = df['Document ID'].map(offsets) + df['Sentence ID']
    return df.sort_values(['Corpus Position', 'Character']).reset_index(drop=True)


# How many of a character's sentences a bin must hold before its average is
# drawn. Below this the average is one or two sentences and swings between 0
# and 1 while everybody else sits at 0.05.
_MIN_SENTENCES_PER_BIN = 3


def _smoothing_window(n, window_size):
    """A window that still smooths something on a long series.

    A 5-sentence window over 14,522 points drawn 12 inches wide is about 1,200
    points to the inch: solid ink, and every apparent spike is one sentence. The
    window grows with the series so that a chart shows roughly 200 turns of the
    line however long the text is.
    """
    return max(window_size, int(n / 200)) if n else window_size


def _smooth(values, window):
    if window > 1 and len(values) >= window:
        return pd.Series(values).rolling(window=window, center=True, min_periods=1).mean().values
    return values


def plot_character_arcs(df, character, outputDir, base_name, window_size=5):
    char_df = df[df['Character'] == character].copy()
    sort_col = 'Corpus Position' if 'Corpus Position' in char_df.columns else 'Sentence ID'
    char_df = char_df.sort_values(sort_col).reset_index(drop=True)

    if len(char_df) < 2:
        return []

    files = []
    fig, ax = plt.subplots(figsize=(12, 6))

    window = _smoothing_window(len(char_df), window_size)
    for emotion in EIGHT_EMOTIONS:
        col = emotion.capitalize()
        smoothed = _smooth(char_df[col].values, window)
        ax.plot(range(len(smoothed)), smoothed, label=emotion.capitalize(),
                color=NRC_COLORS[emotion], linewidth=1.8, alpha=0.85)

    # NOT the sentence number in the text: this character's own appearances, in
    # order. A character absent for fifty pages leaves no gap on their own chart.
    ax.set_xlabel(f'{character}\'s appearances, in order '
                  f'(smoothed over {window} sentences)', fontsize=11)
    ax.set_ylabel('Emotion Intensity', fontsize=11)
    safe_char = character.replace('/', '_').replace('\\', '_').replace(' ', '_')[:30]
    ax.set_title(f'Emotion Arc — {character}\n({base_name})', fontsize=13)
    ax.legend(loc='upper right', fontsize=8, ncol=2)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    arc_file = os.path.join(outputDir, f'emotion_arc_{safe_char}.png')
    plt.savefig(arc_file, dpi=150, bbox_inches='tight')
    plt.close()
    files.append(arc_file)

    return files


def _bin_edges(n, n_bins):
    """Equal-COUNT bin edges. One definition, used by everything that bins an arc, so a second
    reading of the same chart can never drift half a bin away from the first."""
    n_bins = max(1, min(int(n_bins), n))
    return [round(i * n / n_bins) for i in range(n_bins + 1)]


def bin_positions(char_df, n_bins, col='Corpus Position'):
    """Where each bin sits on the CORPUS's own sentence axis - the median of its rows.

    Two characters' bin 60 are not the same moment in the book: bins are cut over each character's
    own appearances, and Harry has three times as many as Hermione. To draw two characters against
    each other in narrative time rather than in their own time, each bin needs a real position.
    """
    if col not in char_df.columns:
        col = 'Sentence ID' if 'Sentence ID' in char_df.columns else ''
    if not col:
        return []
    values = list(char_df[col])
    out = []
    for lo, hi in zip(_bin_edges(len(values), n_bins), _bin_edges(len(values), n_bins)[1:]):
        if hi <= lo:
            hi = lo + 1
        chunk = sorted(float(v) for v in values[lo:hi])
        out.append(chunk[len(chunk) // 2] if chunk else 0.0)
    return out


def arc_by_bin(char_df, n_bins):
    """(labels, means, counts) - one character's MEAN intensity per emotion, in narrative order.

    The counterpart of emotion_mix_by_bin, which gives each emotion's SHARE of a bin. Shares answer
    "what is the mixture here"; means answer "how strongly is this felt here", which is what the arc
    chart plots and what a reader comparing two characters wants.

    Equal-COUNT bins over the character's own appearances, for the same reason as the mixture chart:
    equal widths would be empty wherever the character is absent, and an empty stretch in a line
    chart reads as calm rather than as absence.
    """
    cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    present = [c for c in cols if c in char_df.columns]
    n = len(char_df)
    if n == 0 or not present:
        return [], {}, []

    edges = _bin_edges(n, n_bins)
    labels, counts = [], []
    means = {c: [] for c in present}
    for b in range(len(edges) - 1):
        lo, hi = edges[b], edges[b + 1]
        if hi <= lo:
            hi = lo + 1
        chunk = char_df.iloc[lo:hi]
        for c in present:
            means[c].append(float(chunk[c].mean()))
        counts.append(len(chunk))
        labels.append(lo)
    return labels, means, counts


_ARC_HTML_BINS = 120


def emotion_arc_html(df, characters, outputDir, base_name, bins=_ARC_HTML_BINS):
    """The emotion arcs as ONE interactive HTML file, with a character and an emotion to choose.

    The PNG plots eight emotions over every appearance a character has. For Hermione that is about
    5,000 points per emotion, 40,000 in a chart 12 inches wide: the lines cross so often that the
    picture is a solid band of colour and no arc can be followed. Nothing is wrong with the numbers;
    the chart simply asks the reader to separate eight overlapping series by eye.

    Two changes make it readable, and neither discards data:
      - the appearances are grouped into ~120 equal-count bins and each bin draws its MEAN, so a
        line has 120 turns rather than 5,000 and its shape survives being drawn;
      - one emotion can be brought to the front, the other seven dropping to faint grey so they
        stay as context instead of competing.

    The PNG is still written. This is the copy you explore; that is the copy you paste into a paper.
    Self-contained - no libraries, no internet - so it travels with the rest of the output.
    """
    import json

    if df is None or not len(characters):
        return ''

    cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    sort_col = 'Corpus Position' if 'Corpus Position' in df.columns else 'Sentence ID'

    chars = []
    for character in characters:
        char_df = df[df['Character'] == character]
        if len(char_df) < 2:
            continue
        char_df = char_df.sort_values(sort_col).reset_index(drop=True)
        labels, means, counts = arc_by_bin(char_df, bins)
        if not labels:
            continue
        peaks = {}
        for c in means:
            top = max(range(len(means[c])), key=lambda i: means[c][i])
            peaks[c] = {'i': top, 'v': round(means[c][top], 4)}
        chars.append({
            'name': str(character),
            'n': int(len(char_df)),
            'counts': counts,
            'pos': [round(p, 1) for p in bin_positions(char_df, bins)],
            'series': {c: [round(v, 4) for v in means[c]] for c in means},
            'peaks': peaks,
            'avg': {c: round(float(char_df[c].mean()), 4) for c in cols if c in char_df.columns},
        })
    if not chars:
        return ''

    positions = [p for c in chars for p in c['pos']]
    data = {
        'base': str(base_name),
        'xmin': min(positions) if positions else 0,
        'xmax': max(positions) if positions else 1,
        'emotions': [c for c in cols],
        'colors': {e.capitalize(): NRC_COLORS[e] for e in EIGHT_EMOTIONS},
        'bins': int(bins),
        'chars': chars,
    }
    out_file = os.path.join(outputDir, f'emotion_arcs_{base_name}.html')
    with open(out_file, 'w', encoding='utf-8') as fh:
        fh.write(_ARC_HTML.replace('__DATA__', json.dumps(data)))
    return out_file


_ARC_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Emotion arcs</title>
<style>
 body{font:14px/1.5 "Segoe UI",Inter,sans-serif;margin:0;padding:18px 24px;color:#222;background:#fff;}
 h1{font-size:19px;margin:0 0 2px;} .sub{color:#666;font-size:12px;margin-bottom:14px;}
 #wrap{overflow-x:auto;border:1px solid #e3e3e3;border-radius:6px;padding:8px 0 0;}
 .ctl{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:12px 0;}
 select{font:inherit;padding:4px;}
 button{font:inherit;padding:4px 12px;border:1px solid #c9c9c9;background:#f7f7f7;
        border-radius:5px;cursor:pointer;} button:hover{background:#eee;}
 #picked{display:flex;gap:6px;flex-wrap:wrap;}
 .chip{display:flex;align-items:center;gap:5px;font-size:12px;cursor:pointer;user-select:none;
       padding:3px 9px;border:1px solid #d6d6d6;border-radius:12px;background:#f7f7f7;}
 .chip:hover{background:#eee;} .chip i{width:10px;height:10px;border-radius:50%;
       display:inline-block;} .chip.clear{color:#666;font-style:italic;}
 .legend{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 2px;}
 .legend span{display:flex;align-items:center;gap:5px;font-size:12px;cursor:pointer;user-select:none;}
 .legend i{width:11px;height:11px;border-radius:2px;display:inline-block;}
 .legend .off{opacity:.28;}
 #read{margin-top:10px;padding:10px 12px;background:#fafafa;border:1px solid #eee;border-radius:6px;
       font-size:13px;min-height:44px;}
 .muted{color:#888;}
 text{font:11px "Segoe UI",sans-serif;fill:#555;}
 .gl{stroke:#eee;} .ax{stroke:#ccc;}
 .cursor{stroke:#c1121f;stroke-width:1;}
 table.vals{border-collapse:collapse;font-size:12px;} table.vals td{padding:1px 8px 1px 0;}
 table.vals i{width:9px;height:9px;border-radius:2px;display:inline-block;margin-right:5px;}
 .big{font-weight:600;}
 /* on the chart, not only in the TIPS: both of these change what the arcs may be used to claim,
    and the person reading the chart is the person who needs them */
 #care{margin:16px 0 4px;padding:12px 14px;border:1px solid #e6d9b8;background:#fdfaf1;
       border-radius:6px;font-size:12.5px;max-width:78ch;}
 #care p{margin:6px 0 0;}
</style></head><body>
<h1>Emotion arcs</h1>
<div class="sub" id="sub"></div>

<div class="ctl">
  <label>Character <select id="who"></select></label>
  <button id="compare" type="button">compare with another</button>
  <span id="picked"></span>
  <label>Emotion <select id="emo"></select></label>
  <label><input type="checkbox" id="scale"> scale to the chosen emotion</label>
  <label id="alignbox" style="display:none">Line up by
    <select id="align">
      <option value="own">each character's own arc</option>
      <option value="corpus">position in the corpus</option>
    </select>
  </label>
</div>

<div class="legend" id="legend"></div>
<div id="wrap"><svg id="plot"></svg></div>
<div id="read" class="muted">Move across the chart to read the values at any point.</div>

<div id="care">
  <b>Reading these numbers</b>
  <p>An emotion score belongs to the <b>sentence the character appears in</b>, not to the character.
     The NRC lexicon scores the whole sentence, so a calm character standing in a frightening room
     scores fear. This measures the emotional colour of the prose <i>around</i> a character — a real
     thing, but not the character's own feeling, and it should not be reported as one.</p>
  <p>Characters in the same book <b>tend to come out looking alike</b>, because the ranking largely
     reflects the book's vocabulary rather than a difference between them. Compare the SHAPE of an
     arc across the narrative, and compare characters at the same moment; treat a small gap in
     overall averages as saying little.</p>
  <p class="muted">Full discussion in the TIPS: <i>Character emotion arcs</i>.</p>
</div>

<script>
var DATA = __DATA__;
var PAD = {l:56, r:18, t:12, b:40}, H = 380;
var svg = document.getElementById('plot');
var who = 0, emo = '', hidden = {}, hoverBin = -1, picked = [];
var CHAR_COLORS = ['#0b5394','#b35e3c','#38761d','#7f6000','#4c1130','#134f5c'];

function chart(){ return DATA.chars[who]; }
function comparing(){ return picked.length > 1; }
function picks(){
  // in the order they were chosen, so the pair sits on the rows the reader put it on
  var out = [];
  picked.forEach(function(name){
    DATA.chars.forEach(function(c){ if (c.name === name) out.push(c); });
  });
  return out;
}
function drawn(){
  // the chosen emotion alone is never the whole story: the other seven stay, faint, so a peak can
  // be read against what else is being felt at that moment
  return DATA.emotions.filter(function(e){ return !hidden[e]; });
}
function maxY(){
  var c = chart(), m = 0;
  var pool = (emo && document.getElementById('scale').checked) ? [emo] : drawn();
  pool.forEach(function(e){
    (c.series[e] || []).forEach(function(v){ if (v > m) m = v; });
  });
  return m || 1;
}

function drawCompare(){
  // ONE emotion, several characters. Two characters times eight emotions is sixteen lines, which
  // is the unreadable chart this file exists to replace - so comparing forces a single emotion.
  var cs = picks(), align = document.getElementById('align').value;
  var w = Math.max(880, svg.parentNode.clientWidth - 16);
  var top = 0;
  cs.forEach(function(c){ (c.series[emo] || []).forEach(function(v){ if (v > top) top = v; }); });
  top = top || 1;
  var y = function(v){ return PAD.t + (1 - v / top) * (H - PAD.t - PAD.b); };
  var xOf = function(c, i){
    var span = (H && 1) && (w - PAD.l - PAD.r);
    if (align === 'corpus') {
      var range = (DATA.xmax - DATA.xmin) || 1;
      return PAD.l + ((c.pos[i] - DATA.xmin) / range) * span;
    }
    var n = c.counts.length;
    return PAD.l + (n < 2 ? 0 : i / (n - 1) * span);
  };
  svg.setAttribute('width', w); svg.setAttribute('height', H);
  var out = [];
  for (var g = 0; g <= 4; g++) {
    var v = top * g / 4, yy = y(v);
    out.push('<line class="gl" x1="'+PAD.l+'" y1="'+yy+'" x2="'+(w-PAD.r)+'" y2="'+yy+'"/>');
    out.push('<text x="'+(PAD.l-8)+'" y="'+(yy+4)+'" text-anchor="end">'+v.toFixed(2)+'</text>');
  }
  out.push('<line class="ax" x1="'+PAD.l+'" y1="'+(H-PAD.b)+'" x2="'+(w-PAD.r)+'" y2="'+
           (H-PAD.b)+'"/>');
  cs.forEach(function(c, k){
    var s = c.series[emo] || [], d = '';
    for (var i = 0; i < s.length; i++) { d += (i ? 'L' : 'M') + xOf(c, i) + ',' + y(s[i]); }
    var col = CHAR_COLORS[k % CHAR_COLORS.length];
    out.push('<path d="'+d+'" fill="none" stroke="'+col+'" stroke-width="2" opacity=".9"/>');
  });
  out.push('<text x="'+PAD.l+'" y="'+(H-14)+'">' +
           (align === 'corpus' ? 'start of the corpus' : 'first appearance') + '</text>');
  out.push('<text x="'+(w-PAD.r)+'" y="'+(H-14)+'" text-anchor="end">' +
           (align === 'corpus' ? 'end of the corpus' : 'last appearance') + '</text>');
  out.push('<text x="'+PAD.l+'" y="'+(H-2)+'" class="muted">' + emo + ' · ' +
           (align === 'corpus'
              ? 'lined up in the book, so a flat gap means the character is absent'
              : 'each arc stretched over its own appearances: SHAPES, not the same moment') +
           '</text>');
  svg.innerHTML = out.join('');
  document.getElementById('read').className = '';
  var html = '<b>' + emo + '</b> compared across ' + cs.length +
             ' characters<table class="vals">';
  cs.forEach(function(c, k){
    var s = c.series[emo] || [];
    var mean = s.reduce(function(a, b){ return a + b; }, 0) / (s.length || 1);
    html += '<tr><td><i style="background:' + CHAR_COLORS[k % CHAR_COLORS.length] + '"></i>' +
            c.name + '</td><td>mean ' + mean.toFixed(3) + '</td><td class="muted">' +
            c.n.toLocaleString() + ' appearances</td></tr>';
  });
  document.getElementById('read').innerHTML = html + '</table>';
}

function draw(){
  if (comparing()) { drawCompare(); return; }
  var c = chart(), n = c.counts.length, top = maxY();
  var w = Math.max(880, svg.parentNode.clientWidth - 16);
  svg.setAttribute('width', w); svg.setAttribute('height', H);
  var x = function(i){ return PAD.l + (n < 2 ? 0 : i / (n - 1) * (w - PAD.l - PAD.r)); };
  var y = function(v){ return PAD.t + (1 - v / top) * (H - PAD.t - PAD.b); };
  var out = [];

  for (var g = 0; g <= 4; g++) {
    var v = top * g / 4, yy = y(v);
    out.push('<line class="gl" x1="'+PAD.l+'" y1="'+yy+'" x2="'+(w-PAD.r)+'" y2="'+yy+'"/>');
    out.push('<text x="'+(PAD.l-8)+'" y="'+(yy+4)+'" text-anchor="end">'+v.toFixed(2)+'</text>');
  }
  out.push('<line class="ax" x1="'+PAD.l+'" y1="'+(H-PAD.b)+'" x2="'+(w-PAD.r)+'" y2="'+(H-PAD.b)+'"/>');
  out.push('<text x="'+PAD.l+'" y="'+(H-14)+'">first appearance</text>');
  out.push('<text x="'+(w-PAD.r)+'" y="'+(H-14)+'" text-anchor="end">last appearance</text>');
  out.push('<text x="'+PAD.l+'" y="'+(H-2)+'" class="muted">'+c.n.toLocaleString()+
           ' appearances in '+n+' stretches · mean intensity per stretch</text>');

  function path(e){
    var s = c.series[e] || [], d = '';
    for (var i = 0; i < s.length; i++) { d += (i ? 'L' : 'M') + x(i) + ',' + y(s[i]); }
    return d;
  }
  // faint first, chosen last, so the chosen line is never drawn under another
  drawn().forEach(function(e){
    if (emo && e !== emo) {
      out.push('<path d="'+path(e)+'" fill="none" stroke="#bbb" stroke-width="1" opacity=".55"/>');
    }
  });
  drawn().forEach(function(e){
    if (emo && e !== emo) return;
    var col = DATA.colors[e];
    if (emo === e) {
      var s = c.series[e] || [], area = path(e);
      area += 'L' + x(s.length - 1) + ',' + y(0) + 'L' + x(0) + ',' + y(0) + 'Z';
      out.push('<path d="'+area+'" fill="'+col+'" opacity=".13"/>');
    }
    out.push('<path d="'+path(e)+'" fill="none" stroke="'+col+'" stroke-width="'+
             (emo === e ? 2.4 : 1.5)+'" opacity="'+(emo === e ? 1 : .85)+'"/>');
  });
  if (emo && !hidden[emo] && c.peaks[emo]) {
    var p = c.peaks[emo];
    out.push('<circle cx="'+x(p.i)+'" cy="'+y(p.v)+'" r="4.5" fill="none" stroke="'+
             DATA.colors[emo]+'" stroke-width="2"><title>strongest '+emo+'</title></circle>');
  }
  if (hoverBin >= 0 && hoverBin < n) {
    out.push('<line class="cursor" x1="'+x(hoverBin)+'" y1="'+PAD.t+'" x2="'+x(hoverBin)+
             '" y2="'+(H-PAD.b)+'"/>');
  }
  svg.innerHTML = out.join('');
}

function readout(i){
  var c = chart();
  if (i < 0 || i >= c.counts.length) {
    document.getElementById('read').className = 'muted';
    document.getElementById('read').textContent =
      'Move across the chart to read the values at any point.';
    return;
  }
  var rows = DATA.emotions.slice().sort(function(a, b){
    return (c.series[b] || [])[i] - (c.series[a] || [])[i];
  });
  var html = '<b>' + c.name + '</b> · stretch ' + (i + 1) + ' of ' + c.counts.length +
             ' <span class="muted">(' + c.counts[i] + ' sentences)</span><table class="vals">';
  rows.forEach(function(e){
    var v = (c.series[e] || [])[i] || 0;
    html += '<tr><td><i style="background:' + DATA.colors[e] + '"></i>' +
            (emo === e ? '<span class="big">' + e + '</span>' : e) + '</td><td>' +
            v.toFixed(3) + '</td></tr>';
  });
  document.getElementById('read').className = '';
  document.getElementById('read').innerHTML = html + '</table>';
}

function subtitle(){
  var el = document.getElementById('sub');
  if (comparing()) {
    var byCorpus = document.getElementById('align').value === 'corpus';
    el.textContent = DATA.base + ' · ' + picked.join(' vs ') + ' · ' + emo + ' · ' +
      (byCorpus
         ? 'lined up in the book, so the same x is the same moment'
         : 'each arc over its OWN appearances — the same x is NOT the same moment');
    return;
  }
  var c = chart();
  var best = DATA.emotions.slice().sort(function(a, b){ return c.avg[b] - c.avg[a]; })[0];
  el.textContent =
    DATA.base + ' · ' + c.name + ' · ' + c.n.toLocaleString() + ' appearances grouped into ' +
    c.counts.length + ' equal stretches · strongest on average: ' + best +
    ' (' + c.avg[best].toFixed(3) + ')' +
    (emo ? ' · showing ' + emo + ', the rest in grey' : '');
}

function drawChips(){
  var box = document.getElementById('picked');
  box.innerHTML = '';
  picked.forEach(function(name, i){
    var s = document.createElement('span');
    s.className = 'chip';
    s.innerHTML = '<i style="background:' + CHAR_COLORS[i % CHAR_COLORS.length] + '"></i>' +
                  name + ' ×';
    s.title = 'remove ' + name;
    s.onclick = function(){ picked.splice(i, 1); afterPick(); };
    box.appendChild(s);
  });
  if (picked.length) {
    var one = document.createElement('span');
    one.className = 'chip clear';
    one.textContent = 'back to one character';
    one.onclick = function(){ picked = []; afterPick(); };
    box.appendChild(one);
  }
  document.getElementById('alignbox').style.display = comparing() ? '' : 'none';
  document.getElementById('legend').style.display = comparing() ? 'none' : '';
}

function afterPick(){
  // comparing needs ONE emotion: several characters times eight emotions is the unreadable chart
  // again. Never switch silently - say so in the subtitle and leave the choice showing.
  if (comparing() && !emo) {
    var c = picks()[0];
    emo = DATA.emotions.slice().sort(function(a, b){ return c.avg[b] - c.avg[a]; })[0];
    document.getElementById('emo').value = emo;
  }
  if (comparing()) { hidden[emo] = false; }
  drawChips();
  hoverBin = -1;
  redraw();
}

function buildLegend(){
  var lg = document.getElementById('legend');
  lg.innerHTML = '';
  DATA.emotions.forEach(function(e){
    var s = document.createElement('span');
    s.innerHTML = '<i style="background:' + DATA.colors[e] + '"></i>' + e;
    s.className = hidden[e] ? 'off' : '';
    s.onclick = function(){ hidden[e] = !hidden[e]; s.className = hidden[e] ? 'off' : ''; draw(); };
    lg.appendChild(s);
  });
}
function redraw(){ subtitle(); draw(); }

(function init(){
  var w = document.getElementById('who');
  DATA.chars.forEach(function(c, i){
    var o = document.createElement('option');
    o.value = i; o.textContent = c.name + ' (' + c.n.toLocaleString() + ')';
    w.appendChild(o);
  });
  var e = document.getElementById('emo');
  var all = document.createElement('option');
  all.value = ''; all.textContent = 'all eight';
  e.appendChild(all);
  DATA.emotions.forEach(function(name){
    var o = document.createElement('option');
    o.value = name; o.textContent = name;
    e.appendChild(o);
  });
  // the dropdown selects the character AND, chosen a second time, adds one to compare
  w.addEventListener('change', function(){
    who = +this.value;
    var name = DATA.chars[who].name;
    if (picked.length) {
      if (picked.indexOf(name) < 0) { picked.push(name); }
      afterPick();
      return;
    }
    hoverBin = -1; readout(-1); redraw();
  });
  document.getElementById('compare').addEventListener('click', function(){
    var name = DATA.chars[who].name;
    if (picked.indexOf(name) < 0) { picked.push(name); }
    if (picked.length === 1) {
      // one chip alone is not a comparison: seed it with the character shown next to it
      var other = DATA.chars.filter(function(c){ return c.name !== name; })[0];
      if (other) { picked.push(other.name); }
    }
    afterPick();
  });
  // the subtitle names which reading is on screen, so it has to be rewritten too
  document.getElementById('align').addEventListener('change', redraw);
  e.addEventListener('change', function(){
    if (comparing() && !this.value) {
      // "all eight" across several characters is sixteen-plus lines; refuse and say why
      this.value = emo;
      document.getElementById('sub').textContent =
        'Comparing characters needs ONE emotion — remove a character to see all eight.';
      return;
    }
    emo = this.value;
    // choosing an emotion that was switched off in the legend drew an empty chart and explained
    // nothing - it read as "this character never feels this". Choosing it turns it back on.
    if (emo && hidden[emo]) { hidden[emo] = false; buildLegend(); }
    redraw();
  });
  document.getElementById('scale').addEventListener('change', draw);
  svg.addEventListener('mousemove', function(ev){
    if (comparing()) return;      // the comparison readout is the per-character means, not a point
    var c = chart(), n = c.counts.length;
    var w2 = +svg.getAttribute('width');
    var f = (ev.offsetX - PAD.l) / (w2 - PAD.l - PAD.r);
    hoverBin = Math.max(0, Math.min(n - 1, Math.round(f * (n - 1))));
    draw(); readout(hoverBin);
  });
  svg.addEventListener('mouseleave', function(){ hoverBin = -1; draw(); readout(-1); });
  buildLegend();
  redraw();
  window.addEventListener('resize', draw);
})();
</script></body></html>
"""


def plot_character_comparison(df, characters, emotion, outputDir, base_name, window_size=5,
                              by_corpus_position=True):
    """One emotion, several characters, on ONE chart.

    Two readings, and both are written out:

      by_corpus_position=True   x is the sentence's place in the CORPUS, so the
                                characters line up: where two arcs cross, they
                                cross at the same moment in the text, and a
                                character who is absent leaves a gap.
      by_corpus_position=False  x is each character's own appearances in order,
                                which compares the SHAPE of their arcs when they
                                appear a very different number of times.

    The first is what the old chart claimed to be and was not: everyone was
    drawn from x=0 against their own count, so Harry ran to 14,522 and Ron
    stopped at 5,177, and it looked as though Harry took over the story.
    """
    have_position = by_corpus_position and 'Corpus Position' in df.columns
    fig, ax = plt.subplots(figsize=(14, 5))
    col = emotion.capitalize()
    colors = plt.cm.tab10.colors

    if have_position:
        # On a shared axis the unit that means anything is a STRETCH of text,
        # not a sentence: five characters' sentence-by-sentence lines over
        # 70,000 positions is ink, not a reading. The corpus is cut into equal
        # bins and each character's average in each bin is plotted, so the
        # lines are comparable at every x - and a bin a character is absent
        # from is a gap in their line rather than a jump across it.
        n_bins = 150
        lo, hi = df['Corpus Position'].min(), df['Corpus Position'].max()
        edges = np.linspace(lo, hi, n_bins + 1)
        centres = (edges[:-1] + edges[1:]) / 2

    for i, character in enumerate(characters):
        char_df = df[df['Character'] == character].sort_values(
            'Corpus Position' if have_position else 'Sentence ID')
        if len(char_df) < 2:
            continue
        if have_position:
            grouped = char_df.groupby(
                pd.cut(char_df['Corpus Position'], bins=edges, include_lowest=True),
                observed=False)[col]
            means, counts = grouped.mean(), grouped.count()
            # A bin holding one sentence is not a reading of that stretch of the
            # text: one sentence that happens to be all anger draws a spike to
            # 1.0 next to everybody else's 0.05. Too little to say -> say
            # nothing, and the line breaks there.
            y = means.where(counts >= _MIN_SENTENCES_PER_BIN).values
            x = centres
        else:
            window = _smoothing_window(len(char_df), window_size)
            y = _smooth(char_df[col].values, window)
            x = range(len(y))
        # thin and semi-transparent: five opaque lines simply painted over one
        # another, whichever was drawn last winning
        ax.plot(x, y, label=f'{character} ({len(char_df)})',
                color=colors[i % len(colors)], linewidth=1.5, alpha=0.8)

    if have_position:
        ax.set_xlabel(f'Sentence position in the corpus, documents in order '
                      f'(averaged over {int((hi - lo) / n_bins)} sentences)', fontsize=11)
    else:
        ax.set_xlabel('Each character\'s own appearances, in order', fontsize=11)
    ax.set_ylabel(f'{col} Intensity', fontsize=11)
    ax.set_title(f'{col} Arc — Character Comparison\n({base_name})', fontsize=13)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    safe_emo = emotion.replace(' ', '_')
    suffix = '' if have_position else '_by_own_appearances'
    out_file = os.path.join(outputDir, f'character_comparison_{safe_emo}{suffix}.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


# A 14-inch figure at 150 dpi is about 2100 pixels wide. Below this many stripes each one is a
# couple of pixels and a per-appearance timeline reads; above it the stripes are thinner than a
# pixel, overdraw one another, and what you see is whichever drew LAST rather than what dominates.
_MAX_STRIPES = 400
_TIMELINE_BINS = 100


def emotion_mix_by_bin(char_df, n_bins):
    """(labels, mix, dominant, counts) for one character's appearances, in narrative order.

    mix[emotion] is that emotion's SHARE of each bin, so every bin sums to 1 and the picture is the
    changing MIXTURE rather than a count that mostly tracks how often the character appears.

    Shares rather than winners on purpose: taking only the per-appearance winner threw away
    everything else felt in that sentence, and with eight emotions a winner can win on a small
    plurality. Keeping the other seven visible is what makes a shift legible.

    Equal-COUNT bins, not equal-width: equal widths would be empty wherever the character is absent
    for a stretch, and a gap in a mixture chart reads as an emotion rather than as absence.

    Empty structures for an empty frame rather than an exception: a character with no rows is a
    reason to skip a chart, not to end a profile.
    """
    emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    present = [c for c in emotion_cols if c in char_df.columns]
    n = len(char_df)
    if n == 0 or not present:
        return [], {}, [], []

    n_bins = max(1, min(int(n_bins), n))
    edges = [round(i * n / n_bins) for i in range(n_bins + 1)]

    labels, dominant, counts = [], [], []
    mix = {c: [] for c in present}
    for b in range(n_bins):
        lo, hi = edges[b], edges[b + 1]
        if hi <= lo:
            hi = lo + 1
        chunk = char_df.iloc[lo:hi]
        totals = {c: float(chunk[c].sum()) for c in present}
        grand = sum(totals.values())
        for c in present:
            mix[c].append((totals[c] / grand) if grand else 0.0)
        dominant.append(max(totals, key=totals.get) if grand else '')
        counts.append(len(chunk))
        labels.append(lo)
    return labels, mix, dominant, counts


def plot_dominant_emotion_timeline(df, character, outputDir, base_name):
    """How the mixture of a character's emotions shifts across the narrative.

    This drew one bar per appearance. For Harry that is 16,641 bars across about 2100 pixels -
    eight to a pixel, each thinner than the pixel holding it - so the chart showed whichever bar
    drew last and read as a solid band of noise. It now BINS the appearances and shows the share of
    each emotion per bin, with the per-bin winner as a strip above. Under _MAX_STRIPES appearances
    the per-appearance strip is still drawn: at that size it is readable and more precise.
    """
    sort_col = 'Corpus Position' if 'Corpus Position' in df.columns else 'Sentence ID'
    char_df = df[df['Character'] == character].sort_values(sort_col).reset_index(drop=True)
    if len(char_df) < 2:
        return None

    emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    safe_char = character.replace('/', '_').replace('\\', '_').replace(' ', '_')[:30]
    out_file = os.path.join(outputDir, f'dominant_emotion_timeline_{safe_char}.png')
    color_map = {e.capitalize(): NRC_COLORS[e] for e in EIGHT_EMOTIONS}
    n = len(char_df)

    if n <= _MAX_STRIPES:
        dominant = char_df[emotion_cols].idxmax(axis=1)
        fig, ax = plt.subplots(figsize=(14, 3))
        ax.bar(range(len(dominant)), [1] * len(dominant), width=1.0,
               color=[color_map.get(e, '#999999') for e in dominant], edgecolor='none')
        ax.set_xlim(-0.5, len(dominant) - 0.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel(f"{character}'s appearances, in order  ({n} in all)", fontsize=10)
        ax.set_title(f'Dominant Emotion Timeline — {character} ({base_name})', fontsize=12)
    else:
        labels, mix, dominant, counts = emotion_mix_by_bin(char_df, _TIMELINE_BINS)
        if not labels:
            return None
        n_bins = len(labels)
        per_bin = max(1, n // n_bins)
        fig, (ax_top, ax) = plt.subplots(
            2, 1, figsize=(14, 4.6), sharex=True,
            gridspec_kw={'height_ratios': [1, 6], 'hspace': 0.10})

        # the winner per stretch: the question the old chart asked, at a width you can see
        ax_top.bar(range(n_bins), [1] * n_bins, width=1.0,
                   color=[color_map.get(e, '#999999') for e in dominant], edgecolor='none')
        ax_top.set_xlim(-0.5, n_bins - 0.5)
        ax_top.set_ylim(0, 1)
        ax_top.set_yticks([])
        ax_top.set_ylabel('strongest', fontsize=8, rotation=0, ha='right', va='center')
        ax_top.set_title(f'Emotional Mixture Across the Narrative — {character} ({base_name})',
                         fontsize=12)

        # and the whole mixture underneath, stacked to 1
        bottom = [0.0] * n_bins
        for e in EIGHT_EMOTIONS:
            col = e.capitalize()
            if col not in mix:
                continue
            ax.bar(range(n_bins), mix[col], width=1.0, bottom=bottom,
                   color=NRC_COLORS[e], edgecolor='none')
            bottom = [b + v for b, v in zip(bottom, mix[col])]
        ax.set_xlim(-0.5, n_bins - 0.5)
        ax.set_ylim(0, 1)
        ax.set_ylabel('share of emotion words', fontsize=9)
        ax.set_xlabel(f"{character} across the narrative — {n_bins} stretches of about "
                      f"{per_bin} appearances each ({n} in all)", fontsize=10)

    patches = [mpatches.Patch(color=NRC_COLORS[e], label=e.capitalize()) for e in EIGHT_EMOTIONS]
    ax.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, -0.30),
              ncol=4, fontsize=8)

    # tight_layout cannot handle the two-panel gridspec (it warns "Axes that are not compatible")
    # and would re-space the panels it was given fixed ratios for. bbox_inches='tight' at save time
    # already trims the margins, which is all that was wanted.
    if n <= _MAX_STRIPES:
        plt.tight_layout()
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def main(inputFilename, inputDir, outputDir, chartPackage='Excel',
         dataTransformation='No transformation', min_sentences=5, top_n_characters=5,
         window_size=5, conll_ner_table=None):

    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='character_emotion_arcs', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Character Emotion Arcs at', True)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'character_emotion_arcs',
                                                              '', '', '', '', False, True)

    fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Character'] + \
                 [e.capitalize() for e in EIGHT_EMOTIONS]

    all_rows = []
    # REUSE: when the caller (Corpus Profiler) hands us a Stanza NER CoNLL table it already produced, DERIVE
    # characters + sentences from it -- no re-parse. This pass otherwise builds its OWN Stanza NER pipeline
    # and re-parses the whole corpus (~1.5h on Harry Potter). Falls back to parsing when no table is given.
    if conll_ner_table:
        print('>>> Character Emotion Arcs: derived from an existing Stanza NER table (%s) -- no re-parse'
              % os.path.basename(conll_ner_table))
        try:
            all_rows = analyze_conll_table(conll_ner_table)
        except Exception as e:
            print('Character Emotion Arcs: could not derive from the NER table (%s); parsing instead' % e)
            all_rows = []

    if not all_rows:
        import stanza
        try:
            nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', use_gpu=False)
        except Exception as e:
            mb.showerror(title='Stanza Error',
                         message=f'Could not initialize Stanza NER pipeline.\n\n{str(e)}')
            return filesToOpen
        # ONE canonical name map for the whole corpus: a map per document made
        # Harry, Harry's and Harry Potter three different characters
        canonical_map = {}
        if inputFilename and os.path.exists(inputFilename):
            print("Processing file 1/1 " + os.path.basename(inputFilename))
            all_rows = analyze_file(inputFilename, nlp, 1, canonical_map)
        elif inputDir and os.path.isdir(inputDir):
            txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
            for doc_id, file in enumerate(txt_files, 1):
                print("Processing file " + str(doc_id) + "/" + str(len(txt_files)) + ' ' + file)
                all_rows.extend(analyze_file(os.path.join(inputDir, file), nlp, doc_id,
                                             canonical_map))

    if not all_rows:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    filesToOpen.append(outputFilename)

    df = pd.read_csv(outputFilename)
    # one sentence axis for the corpus, so the charts can put the characters on
    # the same x and a gap means the character is absent
    df = add_corpus_position(df)

    named_chars = df[df['Character'] != '_NARRATOR/UNATTRIBUTED_']
    char_counts = named_chars.groupby('Character')['Sentence ID'].count()
    eligible = char_counts[char_counts >= min_sentences]
    top_characters = eligible.nlargest(top_n_characters).index.tolist()

    if inputFilename:
        base_name = os.path.basename(inputFilename)[:-4]
    else:
        base_name = os.path.basename(inputDir)

    for character in top_characters:
        arc_files = plot_character_arcs(df, character, outputDir, base_name, window_size)
        filesToOpen.extend(arc_files)

        timeline_file = plot_dominant_emotion_timeline(df, character, outputDir, base_name)
        if timeline_file:
            filesToOpen.append(timeline_file)

    # ONE interactive file for every character, beside the per-character PNGs: eight arcs over
    # thousands of appearances cannot be read off a static image, whatever it is plotted at
    arc_html = emotion_arc_html(df, top_characters, outputDir, base_name)
    if arc_html:
        filesToOpen.append(arc_html)

    if len(top_characters) >= 2:
        for emotion in ['joy', 'anger', 'fear', 'sadness']:
            # both readings: on the corpus's own sentence axis, where the
            # characters line up and absence shows as a gap, and against each
            # character's own appearances, which compares the SHAPE of arcs
            # belonging to characters who appear very different amounts
            filesToOpen.append(plot_character_comparison(
                df, top_characters, emotion, outputDir, base_name, window_size,
                by_corpus_position=True))
            filesToOpen.append(plot_character_comparison(
                df, top_characters, emotion, outputDir, base_name, window_size,
                by_corpus_position=False))

    summary_file = os.path.join(outputDir, f'character_emotion_summary_{base_name}.csv')
    summary_rows = []
    for character in top_characters:
        char_df = df[df['Character'] == character]
        row = {'Character': character, 'Sentences': len(char_df)}
        for e in EIGHT_EMOTIONS:
            row[f'Avg {e.capitalize()}'] = round(char_df[e.capitalize()].mean(), 4)
        emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
        avg_vals = {e: char_df[e].mean() for e in emotion_cols}
        row['Dominant Emotion'] = max(avg_vals, key=avg_vals.get)
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    filesToOpen.append(summary_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Character Emotion Arcs at', True, '', True, startTime)

    return filesToOpen
