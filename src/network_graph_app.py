"""Standalone vis.js Network Graph Viewer.

A lightweight tkinter application that opens a CSV file and generates
an interactive vis.js network graph in the browser.  Designed to be
bundled with PyInstaller as a self-contained executable.

Usage (source):  python network_graph_app.py
Usage (exe):     NetworkGraphViewer.exe
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

import pandas as pd

# ---------------------------------------------------------------------------
# Inline the network-graph builder so the standalone exe has zero dependency
# on the NLP Suite codebase.  This is a trimmed copy of
# charts_util.network_graph_visjs() — kept in sync manually.
# ---------------------------------------------------------------------------

def _build_network_html(inputFilename, outputDir, col1, col2, col3,
                        date_col=None, top_n_per_role=15):
    """Build an interactive vis.js network graph and return the HTML path."""
    import json as _json
    import math as _math

    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(inputFilename, encoding='ISO-8859-1', on_bad_lines='skip')

    svo_cols = [col1, col2, col3]
    for c in svo_cols:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in CSV")

    _has_dates = date_col and date_col in df.columns
    _net_cols = list(svo_cols)
    if _has_dates:
        _net_cols.append(date_col)

    net_df = df[_net_cols].dropna(subset=svo_cols, how='all').copy()
    for sc in svo_cols:
        net_df[sc] = net_df[sc].fillna('').astype(str)
    if net_df.empty:
        raise ValueError("No data rows after filtering")

    palette = {'S': '#E04040', 'V': '#4060E0', 'O': '#30A030'}
    role_keys = ['S', 'V', 'O']
    role_labels = [col1, col2, col3]
    role_of = {}
    top_per_role = {}
    for idx_r, sc in enumerate(svo_cols):
        rk = role_keys[idx_r]
        top_vals = net_df[sc].value_counts().head(top_n_per_role).index.tolist()
        top_per_role[sc] = set(top_vals)
        for v in top_vals:
            if v and v not in role_of:
                role_of[v] = rk

    mask = net_df.apply(
        lambda row: all(row[c] in top_per_role[c] or row[c] == ''
                        for c in svo_cols), axis=1)
    net_df = net_df[mask]
    if net_df.empty:
        raise ValueError("No data rows after top-N filtering")

    edges = {}
    edge_dates = {}
    edge_labels = {}
    for _, row in net_df.iterrows():
        vals = [row[c] for c in svo_cols if row[c]]
        row_date = None
        if _has_dates and pd.notna(row.get(date_col)):
            row_date = pd.to_datetime(row[date_col], errors='coerce')
            if pd.isna(row_date):
                row_date = None
        for i in range(len(vals) - 1):
            key = (vals[i], vals[i + 1])
            edges[key] = edges.get(key, 0) + 1
            if row_date is not None:
                edge_dates.setdefault(key, []).append(row_date)
        if len(vals) >= 3:
            verb = row[svo_cols[1]]
            if verb:
                edge_labels.setdefault((vals[0], vals[-1]), set()).add(verb)
                for i in range(len(vals) - 1):
                    edge_labels.setdefault((vals[i], vals[i + 1]), set()).add(verb)

    triplet_counts = {}
    for _, row in net_df.iterrows():
        vals = tuple(row[c] for c in svo_cols)
        if any(v == '' for v in vals):
            continue
        triplet_counts[vals] = triplet_counts.get(vals, 0) + 1

    node_triplets = {}
    for triplet, cnt in triplet_counts.items():
        for val in triplet:
            node_triplets.setdefault(val, []).append(list(triplet) + [cnt])

    all_nodes = set()
    for (s, t) in edges:
        all_nodes.add(s)
        all_nodes.add(t)

    node_freq = {}
    for sc in svo_cols:
        for val, cnt in net_df[sc].value_counts().items():
            if val:
                node_freq[val] = node_freq.get(val, 0) + cnt

    if not all_nodes:
        raise ValueError("No nodes to display")

    freq_vals = [node_freq.get(n, 1) for n in all_nodes]
    max_freq = max(freq_vals)
    min_freq = min(freq_vals)
    SIZE_MIN, SIZE_MAX = 8, 45

    def _node_size(freq):
        if max_freq == min_freq:
            return (SIZE_MIN + SIZE_MAX) / 2
        log_ratio = _math.log(1 + freq - min_freq) / _math.log(1 + max_freq - min_freq)
        return SIZE_MIN + log_ratio * (SIZE_MAX - SIZE_MIN)

    node_id_map = {n: i for i, n in enumerate(sorted(all_nodes))}
    vis_nodes = []
    for n, nid in node_id_map.items():
        rk = role_of.get(n, role_keys[-1])
        freq = node_freq.get(n, 1)
        sz = round(_node_size(freq), 1)
        fsz = max(10, min(22, int(10 + (sz - SIZE_MIN) / (SIZE_MAX - SIZE_MIN) * 12)))
        vis_nodes.append({
            'id': nid, 'label': n,
            'color': palette.get(rk, '#888'),
            'font': {'size': fsz},
            'shape': 'dot', 'size': sz,
            'title': '{} (freq: {})'.format(n, freq),
            'role': rk})

    all_verbs = sorted(set(v for labels in edge_labels.values() for v in labels))
    edge_color_palette = [
        '#E04040', '#4060E0', '#30A030', '#E0A020', '#9040C0',
        '#20B0B0', '#E06090', '#808000', '#FF6020', '#6080FF',
        '#A05030', '#00A060', '#C04080', '#5090A0', '#D0D030',
        '#8060C0', '#40C080', '#E08040', '#6060A0', '#B04040']
    verb_color_map = {}
    for i, v in enumerate(all_verbs):
        verb_color_map[v] = edge_color_palette[i % len(edge_color_palette)]

    vis_edges = []
    for (s, t), w in edges.items():
        labels_for_edge = edge_labels.get((s, t), set())
        if len(labels_for_edge) == 1:
            ec = verb_color_map[next(iter(labels_for_edge))]
        else:
            ec = '#aaaaaa'
        label_str = ', '.join(sorted(labels_for_edge)) if labels_for_edge else ''
        title_parts = ['{} → {}'.format(s, t)]
        if label_str:
            title_parts.append('via: {}'.format(label_str))
        title_parts.append('count: {}'.format(w))
        e_entry = {
            'from': node_id_map[s], 'to': node_id_map[t],
            'value': w,
            'title': ' | '.join(title_parts),
            'label': label_str if len(labels_for_edge) == 1 else '',
            'color': {'color': ec, 'highlight': '#333333'},
            'edgeVerb': label_str}
        if _has_dates and (s, t) in edge_dates:
            e_entry['dates'] = sorted(set(
                d.strftime('%Y-%m-%d') for d in edge_dates[(s, t)]))
        vis_edges.append(e_entry)

    _all_dates_set = set()
    if _has_dates:
        for dlist in edge_dates.values():
            for d in dlist:
                _all_dates_set.add(d.strftime('%Y-%m-%d'))
        node_dates = {}
        for (s, t), dlist in edge_dates.items():
            for d in dlist:
                ds = d.strftime('%Y-%m-%d')
                node_dates.setdefault(node_id_map[s], set()).add(ds)
                node_dates.setdefault(node_id_map[t], set()).add(ds)
        for vn in vis_nodes:
            nid = vn['id']
            if nid in node_dates:
                vn['dates'] = sorted(node_dates[nid])
    _all_dates_sorted = sorted(_all_dates_set) if _all_dates_set else []

    js_node_triplets = {}
    for label, trips in node_triplets.items():
        nid = node_id_map.get(label)
        if nid is not None:
            trips_sorted = sorted(trips, key=lambda x: -x[-1])[:30]
            js_node_triplets[nid] = trips_sorted

    _role_arrow_label = ' → '.join(role_labels)
    _role_arrow_short = ' → '.join(role_keys)

    legend_parts = []
    for rk, rl in zip(role_keys, role_labels):
        legend_parts.append(
            '<span class="leg" style="background:{}"></span>{}'.format(palette[rk], rl))
    if all_verbs:
        legend_parts.append('&nbsp;&nbsp;|&nbsp;&nbsp;<b>Edges:</b>')
        for v in all_verbs[:12]:
            legend_parts.append(
                '<span class="leg-e" style="background:{}"></span>{}'.format(verb_color_map[v], v))
        if len(all_verbs) > 12:
            legend_parts.append('… +{} more'.format(len(all_verbs) - 12))
    legend_html = '  '.join(legend_parts)

    slider_display = 'block' if _has_dates else 'none'
    network_height = '78vh' if not _has_dates else '70vh'

    _table_header_html = ''
    _table_row_js = ''
    _th = []
    for _i, _rc in enumerate(role_labels):
        if _i > 0:
            _th.append('<th></th>')
        _th.append('<th>{}</th>'.format(_rc))
    _th.append('<th>Count</th>')
    _table_header_html = ''.join(_th)

    _td = []
    for _i, _rc in enumerate(role_labels):
        _css = role_keys[_i].lower()
        if _i > 0:
            _td.append("'<td>&rarr;</td>'")
        _td.append("'<td class=\"{}\">' + t[{}] + '</td>'".format(_css, _i))
    _td.append("'<td>' + t[{}] + '</td>'".format(len(svo_cols)))
    _table_row_js = ' + '.join(_td)

    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Network Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; margin: 0; }}
  #network {{ width: 100%; height: {network_height}; border: 1px solid #ccc; }}
  #title {{ text-align: center; padding: 8px; font-size: 16px; font-weight: bold; }}
  #legend {{ text-align: center; padding: 4px; font-size: 13px; }}
  .leg {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%;
          vertical-align: middle; margin: 0 3px 0 12px; }}
  .leg-e {{ display: inline-block; width: 20px; height: 4px;
            vertical-align: middle; margin: 0 3px 0 10px; border-radius: 2px; }}
  #time-slider-container {{ display: {slider_display}; padding: 6px 20px;
           background: #f8f8f8; border-top: 1px solid #ddd; text-align: center; }}
  #time-slider-container label {{ font-size: 13px; margin-right: 8px; }}
  #time-slider {{ width: 60%; vertical-align: middle; }}
  #time-label {{ font-weight: bold; font-size: 13px; margin-left: 8px; min-width: 100px;
                 display: inline-block; }}
  #time-slider-container button {{ margin-left: 12px; font-size: 12px; padding: 2px 10px;
                                    cursor: pointer; }}
  #info {{ padding: 8px 16px; font-size: 13px; color: #333;
           max-height: 18vh; overflow-y: auto; border-top: 1px solid #ccc; }}
  #info table {{ border-collapse: collapse; margin: 4px auto; }}
  #info th, #info td {{ padding: 2px 10px; text-align: left; }}
  #info th {{ border-bottom: 1px solid #999; }}
  .s {{ color: #E04040; font-weight: bold; }}
  .v {{ color: #4060E0; font-weight: bold; }}
  .o {{ color: #30A030; font-weight: bold; }}
</style>
</head><body>
<div id="title">Network (top {top_n} per role) &mdash; click a node to see {role_arrow_label} chains</div>
<div id="legend">{legend_html} &nbsp;&nbsp;&nbsp; <span style="font-size:12px;color:#666">&#9679; Node size = frequency</span></div>
<div id="time-slider-container">
  <label>Timeline:</label>
  <input type="range" id="time-slider" min="0" max="0" value="0" step="1">
  <span id="time-label">All dates</span>
  <button id="time-play">&#9654; Play</button>
  <button id="time-reset">Show All</button>
</div>
<div id="network"></div>
<div id="info">Click a node to see its {role_arrow_short} relationships.</div>
<script>
var allDates = {all_dates_json};
var nodes = new vis.DataSet({nodes_json});
var edges = new vis.DataSet({edges_json});
var nodeTriplets = {triplets_json};
var container = document.getElementById('network');
var gdata = {{ nodes: nodes, edges: edges }};
var options = {{
  physics: {{ solver: 'forceAtlas2Based',
              forceAtlas2Based: {{ gravitationalConstant: -60, springLength: 150,
                                  springConstant: 0.04, damping: 0.5 }},
              stabilization: {{ iterations: 200 }} }},
  interaction: {{ hover: true, tooltipDelay: 100 }},
  nodes: {{ scaling: {{ min: 8, max: 45 }} }},
  edges: {{ arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
            smooth: {{ type: 'continuous' }}, scaling: {{ min: 1, max: 6 }},
            font: {{ size: 10, color: '#555', strokeWidth: 2, strokeColor: '#fff', align: 'top' }} }}
}};
var network = new vis.Network(container, gdata, options);
var origNodeProps = {{}};
nodes.forEach(function(n) {{
  origNodeProps[n.id] = {{ size: n.size, fontSize: n.font ? n.font.size : 14 }};
}});
var origEdgeColors = {{}};
edges.forEach(function(e) {{
  origEdgeColors[e.id] = e.color && e.color.color ? e.color.color : '#aaaaaa';
}});
function resetAll() {{
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                    font: {{ size: orig.fontSize, color: '#333' }} }});
  }});
  edges.forEach(function(e) {{
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
  }});
}}
var slider = document.getElementById('time-slider');
var timeLabel = document.getElementById('time-label');
var playBtn = document.getElementById('time-play');
var resetBtn = document.getElementById('time-reset');
var playInterval = null;
if (allDates.length > 0) {{
  slider.max = allDates.length;
  slider.value = 0;
  slider.addEventListener('input', function() {{ applyTimeFilter(parseInt(this.value)); }});
  resetBtn.addEventListener('click', function() {{ slider.value = 0; applyTimeFilter(0); stopPlay(); }});
  playBtn.addEventListener('click', function() {{
    if (playInterval) {{ stopPlay(); return; }}
    if (parseInt(slider.value) >= allDates.length) slider.value = 0;
    playInterval = setInterval(function() {{
      var v = parseInt(slider.value) + 1;
      if (v > allDates.length) {{ stopPlay(); return; }}
      slider.value = v;
      applyTimeFilter(v);
    }}, 800);
    playBtn.textContent = '\\u275A\\u275A Pause';
  }});
}}
function stopPlay() {{
  if (playInterval) {{ clearInterval(playInterval); playInterval = null; }}
  playBtn.textContent = '\\u25B6 Play';
}}
function applyTimeFilter(idx) {{
  if (idx === 0 || allDates.length === 0) {{
    timeLabel.textContent = 'All dates';
    resetAll();
    return;
  }}
  var cutoff = allDates[idx - 1];
  timeLabel.textContent = cutoff;
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    var dates = n.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    if (visible) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: orig.fontSize, color: '#333' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.1, size: 4,
                      font: {{ size: 1, color: 'transparent' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var dates = e.dates || [];
    var visible = dates.length === 0 || dates.some(function(d) {{ return d <= cutoff; }});
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (visible) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eeeeee', opacity: 0.1 }} }});
    }}
  }});
}}
network.on('click', function(params) {{
  if (params.nodes.length === 0) {{ resetAll(); return; }}
  var nid = params.nodes[0];
  var trips = nodeTriplets[nid] || [];
  var infoDiv = document.getElementById('info');
  if (trips.length === 0) {{
    infoDiv.innerHTML = 'No {role_arrow_short} triplets for this node.';
    return;
  }}
  var html = '<table><tr>{table_header}</tr>';
  trips.forEach(function(t) {{
    html += '<tr>' + {table_row_js} + '</tr>';
  }});
  html += '</table>';
  infoDiv.innerHTML = html;
  var connEdges = network.getConnectedEdges(nid);
  var connNodes = new Set();
  connNodes.add(nid);
  connEdges.forEach(function(eid) {{
    var e = edges.get(eid);
    connNodes.add(e.from);
    connNodes.add(e.to);
  }});
  nodes.forEach(function(n) {{
    var orig = origNodeProps[n.id] || {{ size: 12, fontSize: 14 }};
    if (connNodes.has(n.id)) {{
      nodes.update({{ id: n.id, opacity: 1.0, size: orig.size,
                      font: {{ size: orig.fontSize, color: '#333' }} }});
    }} else {{
      nodes.update({{ id: n.id, opacity: 0.15, size: 4,
                      font: {{ size: 1, color: 'transparent' }} }});
    }}
  }});
  edges.forEach(function(e) {{
    var oc = origEdgeColors[e.id] || '#aaaaaa';
    if (connEdges.indexOf(e.id) >= 0) {{
      edges.update({{ id: e.id, color: {{ color: oc, opacity: 1.0 }} }});
    }} else {{
      edges.update({{ id: e.id, color: {{ color: '#eeeeee', opacity: 0.08 }} }});
    }}
  }});
}});
</script>
</body></html>"""

    html = html.format(
        network_height=network_height,
        slider_display=slider_display,
        top_n=top_n_per_role,
        role_arrow_label=_role_arrow_label,
        role_arrow_short=_role_arrow_short,
        legend_html=legend_html,
        all_dates_json=_json.dumps(_all_dates_sorted),
        nodes_json=_json.dumps(vis_nodes),
        edges_json=_json.dumps(vis_edges),
        triplets_json=_json.dumps(js_node_triplets),
        table_header=_table_header_html,
        table_row_js=_table_row_js)

    base = os.path.splitext(os.path.basename(inputFilename))[0]
    output_file = os.path.join(outputDir, f'{base}_network.html')
    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(html)
    return output_file


# ---------------------------------------------------------------------------
# Tkinter GUI
# ---------------------------------------------------------------------------

class NetworkGraphApp:
    def __init__(self, master):
        self.master = master
        master.title('Network Graph Viewer')
        master.geometry('600x420')
        master.resizable(False, False)

        self.csv_path = tk.StringVar()
        self.col1_var = tk.StringVar()
        self.col2_var = tk.StringVar()
        self.col3_var = tk.StringVar()
        self.date_var = tk.StringVar(value='(none)')
        self.topn_var = tk.IntVar(value=15)
        self.columns = []

        pad = {'padx': 12, 'pady': 4}

        # Title
        ttk.Label(master, text='Network Graph Viewer',
                  font=('Segoe UI', 16, 'bold')).pack(pady=(12, 4))
        ttk.Label(master, text='Generate interactive vis.js network graphs from CSV data',
                  font=('Segoe UI', 9)).pack(pady=(0, 8))

        # CSV file
        f1 = ttk.Frame(master)
        f1.pack(fill='x', **pad)
        ttk.Label(f1, text='CSV file:').pack(side='left')
        ttk.Entry(f1, textvariable=self.csv_path, width=45).pack(side='left', padx=4)
        ttk.Button(f1, text='Browse…', command=self._browse).pack(side='left')

        # Column selectors
        f2 = ttk.LabelFrame(master, text='Column mapping')
        f2.pack(fill='x', **pad)

        for label, var in [('Node 1 (e.g. Subject):', self.col1_var),
                           ('Edge label (e.g. Verb):', self.col2_var),
                           ('Node 2 (e.g. Object):', self.col3_var),
                           ('Date column (optional):', self.date_var)]:
            row = ttk.Frame(f2)
            row.pack(fill='x', padx=8, pady=2)
            ttk.Label(row, text=label, width=26).pack(side='left')
            cb = ttk.Combobox(row, textvariable=var, width=28, state='readonly')
            cb.pack(side='left')
            if var is self.date_var:
                self._date_cb = cb
            elif var is self.col1_var:
                self._col1_cb = cb
            elif var is self.col2_var:
                self._col2_cb = cb
            elif var is self.col3_var:
                self._col3_cb = cb

        # Top N
        f3 = ttk.Frame(master)
        f3.pack(fill='x', **pad)
        ttk.Label(f3, text='Top N values per role:').pack(side='left')
        ttk.Spinbox(f3, from_=5, to=100, textvariable=self.topn_var,
                     width=6).pack(side='left', padx=4)

        # Generate button
        self.gen_btn = ttk.Button(master, text='Generate Network Graph',
                                  command=self._generate, state='disabled')
        self.gen_btn.pack(pady=12)

        # Status
        self.status_var = tk.StringVar(value='Select a CSV file to begin.')
        ttk.Label(master, textvariable=self.status_var,
                  font=('Segoe UI', 9), foreground='#666').pack(pady=(0, 8))

    def _browse(self):
        path = filedialog.askopenfilename(
            title='Select CSV file',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if not path:
            return
        self.csv_path.set(path)
        try:
            df = pd.read_csv(path, nrows=5, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(path, nrows=5, encoding='ISO-8859-1', on_bad_lines='skip')
        self.columns = list(df.columns)
        cols_with_none = ['(none)'] + self.columns
        self._col1_cb['values'] = self.columns
        self._col2_cb['values'] = self.columns
        self._col3_cb['values'] = self.columns
        self._date_cb['values'] = cols_with_none

        # Auto-detect SVO columns
        for c in self.columns:
            cl = c.lower().strip()
            if 'subject' in cl or cl == 's':
                self.col1_var.set(c)
            elif 'verb' in cl or cl == 'v':
                self.col2_var.set(c)
            elif 'object' in cl or cl == 'o':
                self.col3_var.set(c)
            elif 'date' in cl:
                self.date_var.set(c)

        if not self.col1_var.get() and len(self.columns) >= 3:
            self.col1_var.set(self.columns[0])
            self.col2_var.set(self.columns[1])
            self.col3_var.set(self.columns[2])

        self.gen_btn.configure(state='normal')
        self.status_var.set(f'Loaded {len(self.columns)} columns. Map them and click Generate.')

    def _generate(self):
        csv_path = self.csv_path.get()
        if not csv_path or not os.path.isfile(csv_path):
            messagebox.showerror('Error', 'Please select a valid CSV file.')
            return
        c1 = self.col1_var.get()
        c2 = self.col2_var.get()
        c3 = self.col3_var.get()
        if not c1 or not c2 or not c3:
            messagebox.showerror('Error', 'Please select all three column mappings.')
            return
        date_col = self.date_var.get()
        if date_col == '(none)':
            date_col = None
        top_n = self.topn_var.get()
        output_dir = os.path.dirname(csv_path)

        self.status_var.set('Generating network graph…')
        self.master.update()

        try:
            html_path = _build_network_html(csv_path, output_dir, c1, c2, c3,
                                            date_col=date_col, top_n_per_role=top_n)
            self.status_var.set(f'Saved: {os.path.basename(html_path)}')
            webbrowser.open('file://' + os.path.abspath(html_path))
        except Exception as e:
            messagebox.showerror('Error', str(e))
            self.status_var.set('Error generating graph.')


def main():
    root = tk.Tk()
    NetworkGraphApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
