# Charts of word-pair distances and similarities (Word2Vec: Gensim and BERT).
# The old charts drew ONE BAR PER WORD PAIR - with the top 200 words, 19,900 unreadable bars (Roberto, 21 Oct 2026:
# "The chart output is unreadable and pretty useless. There must be a better way of visualizing this"). Four views
# replace them, for cosine similarity and for n-dimensional Euclidean distance alike:
#   1. a HISTOGRAM of the values (how the pairs are spread: are most pairs close, is there a tail of very close ones?)
#   2. the 25 CLOSEST PAIRS, horizontal bars with readable labels
#   3. a HEATMAP of the top words, reordered so that similar words sit together (groups show as blocks)
#   4. the NEAREST NEIGHBOURS of every word (csv table: each word and its 5 closest words)
# The logic is plain Python on (word_1, word_2, value) rows, so it is unit-tested; Plotly only draws.

import csv
import math

TOP_PAIRS = 25
NEIGHBOURS = 5
HISTOGRAM_BINS = 25
HEATMAP_MAX_WORDS = 300     # beyond this a heatmap is too dense to read (and heavy to draw)


def _closer(a, b, larger_is_closer):
    """True when value a means CLOSER than value b (cosine: larger; Euclidean distance: smaller)."""
    return a > b if larger_is_closer else a < b


def histogram_bins(values, n_bins=HISTOGRAM_BINS):
    """[(from, to, number of pairs)] over the range of the values; the last bin includes its upper edge."""
    values = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [(lo, hi, len(values))]
    width = (hi - lo) / n_bins
    counts = [0] * n_bins
    for v in values:
        counts[min(int((v - lo) / width), n_bins - 1)] += 1
    return [(lo + i * width, lo + (i + 1) * width, counts[i]) for i in range(n_bins)]


def closest_pairs(rows, larger_is_closer, k=TOP_PAIRS):
    """The k closest (word_1, word_2, value) rows, closest first."""
    return sorted(rows, key=lambda r: r[2], reverse=larger_is_closer)[:k]


def nearest_neighbours(rows, larger_is_closer, k=NEIGHBOURS):
    """{word: [(other word, value), ...]} - each word's k closest words, closest first."""
    by_word = {}
    for w1, w2, v in rows:
        by_word.setdefault(w1, []).append((w2, v))
        by_word.setdefault(w2, []).append((w1, v))
    return {w: sorted(lst, key=lambda x: x[1], reverse=larger_is_closer)[:k] for w, lst in by_word.items()}


def cluster_order(rows, larger_is_closer):
    """The words in an order that puts similar words next to each other (greedy nearest-neighbour chain: start from
    the closest pair, then repeatedly add the unplaced word closest to the last one placed). Words of each group of
    similar words end up together, so the heatmap shows them as blocks."""
    if not rows:
        return []
    value = {}
    for w1, w2, v in rows:
        value[(w1, w2)] = value[(w2, w1)] = v
    words, seen = [], set()
    for w1, w2, _v in rows:
        for w in (w1, w2):
            if w not in seen:
                seen.add(w)
                words.append(w)
    first = closest_pairs(rows, larger_is_closer, 1)[0]
    order = [first[0], first[1]]
    left = [w for w in words if w not in order]
    while left:
        last = order[-1]
        best = None
        for w in left:
            v = value.get((last, w))
            if v is None:
                continue
            if best is None or _closer(v, best[1], larger_is_closer):
                best = (w, v)
        nxt = best[0] if best else left[0]
        order.append(nxt)
        left.remove(nxt)
    return order


def matrix(order, rows):
    """Square matrix (list of lists) of the values for the words in order; the diagonal is left empty (None)."""
    value = {}
    for w1, w2, v in rows:
        value[(w1, w2)] = value[(w2, w1)] = v
    return [[None if a == b else value.get((a, b)) for b in order] for a in order]


def write_neighbours_csv(path, neighbours, measure, k=NEIGHBOURS):
    """One row per word: the word, then its k closest words and their values."""
    head = ['Word'] + [x for i in range(1, k + 1) for x in ('Neighbour %d' % i, '%s %d' % (measure, i))]
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(head)
        for word in sorted(neighbours, key=str.lower):
            cells = [word]
            for other, v in neighbours[word]:
                cells += [other, round(v, 4)]
            w.writerow(cells)
    return path


def charts(rows, measure, larger_is_closer, output_name):
    """Draw the four views of one measure. rows: [(word_1, word_2, value)]; measure: 'Cosine similarity' or
    'n-dimensional Euclidean distance'; output_name(label, extension) -> a full output path. Returns the files
    written. Plotly draws the three charts (html); the nearest neighbours are a csv table."""
    import plotly.graph_objects as go

    files = []
    if not rows:
        return files
    closer = 'higher = closer' if larger_is_closer else 'lower = closer'
    n_words = len({w for r in rows for w in r[:2]})

    # 1. histogram
    bins = histogram_bins([r[2] for r in rows])
    fig = go.Figure(go.Bar(x=['%.3f-%.3f' % (a, b) for a, b, _n in bins], y=[n for _a, _b, n in bins],
                           hovertemplate='%{x}: %{y} word pairs<extra></extra>'))
    fig.update_layout(title='How the %d word pairs are spread: %s (%s)' % (len(rows), measure, closer),
                      xaxis_title=measure, yaxis_title='Number of word pairs', template='plotly_white')
    files.append(output_name('hist', '.html'))
    fig.write_html(files[-1])

    # 2. the closest pairs
    top = closest_pairs(rows, larger_is_closer)
    fig = go.Figure(go.Bar(x=[r[2] for r in top][::-1], y=['%s - %s' % (r[0], r[1]) for r in top][::-1],
                           orientation='h', hovertemplate='%{y}: %{x:.4f}<extra></extra>'))
    fig.update_layout(title='The %d closest word pairs: %s (%s)' % (len(top), measure, closer),
                      xaxis_title=measure, height=max(400, 22 * len(top) + 120), template='plotly_white')
    files.append(output_name('closest', '.html'))
    fig.write_html(files[-1])

    # 3. the clustered heatmap
    if n_words <= HEATMAP_MAX_WORDS:
        order = cluster_order(rows, larger_is_closer)
        fig = go.Figure(go.Heatmap(z=matrix(order, rows), x=order, y=order,
                                   colorscale='Viridis', reversescale=not larger_is_closer,
                                   hovertemplate='%{y} - %{x}: %{z:.4f}<extra></extra>', colorbar_title=measure))
        side = max(600, 12 * len(order) + 200)
        fig.update_layout(title='%s between the top %d words, similar words grouped together (%s)'
                                % (measure, len(order), closer),
                          width=side, height=side, template='plotly_white',
                          yaxis=dict(autorange='reversed'))
        files.append(output_name('heatmap', '.html'))
        fig.write_html(files[-1])

    # 4. nearest neighbours
    files.append(write_neighbours_csv(output_name('neighbours', '.csv'),
                                      nearest_neighbours(rows, larger_is_closer), measure))
    return files
