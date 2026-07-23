"""Build every src/*_main.py under real Tk, screenshot each window, and assemble ONE HTML page so you
can scan all the GUIs at a glance and spot anything off.

The page has a table of contents and two sections:
  * Full-grid GUIs      -- the standard GUIs laid out by the grid (placeWidget -> columns)
  * Special GUIs        -- the few kept on absolute .place (GUI_IO_util.GRID_OPT_OUT: DB_SQL, NLP_menu,
                           the PC-ACE tools, parsers)
Each card is titled with the GUI's own window caption and carries a PASS/FAIL badge (same
overflow/overlap check as gui_layout_gate.py); flagged GUIs sort to the top of their section.

Output:
  tests/gui_screenshots/<gui>.png   -- full-resolution shot of each GUI
  tests/gui_gallery.html            -- the page (self-contained; open in a browser)

Run in the Anaconda **NLP** env (real libs + PIL). Windows flash open one at a time while it grabs
them -- leave the machine be for the ~2 minutes it runs. Same honest scope as the gate: THIS machine's
Windows rendering, not macOS.
"""
import base64
import glob
import io as _io
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(os.path.dirname(_HERE), 'src')
_SHOTS = os.path.join(_HERE, 'gui_screenshots')
_NOT_GUI = ('NLP_setup_',)

_WORKER = r'''
import sys, os, time, base64
os.environ['NLP_SILENT'] = '1'
SRC = r"{src}"
sys.path.insert(0, SRC)
import importlib.util
import IO_libraries_util
IO_libraries_util.install_all_Python_packages = lambda *a, **k: True
IO_libraries_util.check_java_installation = lambda *a, **k: (False, 0, '', '')
import GUI_util, GUI_IO_util
GUI_util.window.mainloop = lambda *a, **k: None
target, png = sys.argv[1], sys.argv[2]
try:
    spec = importlib.util.spec_from_file_location("_gui", os.path.join(SRC, target))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
except SystemExit:
    pass
except BaseException as e:
    print("BUILD_FAIL", type(e).__name__, str(e)[:120]); raise SystemExit(0)
w = GUI_util.window
w.update_idletasks()
try:
    win_w = int(w.geometry().split("+")[0].split("x")[0])
except Exception:
    win_w = w.winfo_reqwidth()

rects = []
def walk(widget, ox, oy):
    for ch in widget.winfo_children():
        try:
            cx, cy = ox + ch.winfo_x(), oy + ch.winfo_y()
            rects.append((cx, cy, cx + ch.winfo_width(), cy + ch.winfo_height()))
            if ch.winfo_class() != 'TNotebook':
                walk(ch, cx, cy)
        except Exception:
            pass
walk(w, 0, 0)
rects = [r for r in rects if r[2] > r[0] and r[3] > r[1]]
max_right = max((r[2] for r in rects), default=0)
overflow = max_right - win_w
overlaps = 0
S = sorted(rects, key=lambda r: (r[0], r[1]))
for i in range(len(S)):
    for j in range(i + 1, len(S)):
        a, b = S[i], S[j]
        if b[0] - a[0] > 60 and b[0] >= a[2]:
            break
        if abs(a[0] - b[0]) <= 6:
            continue
        if a[1] < b[3] - 4 and b[1] < a[3] - 4 and min(a[2], b[2]) - max(a[0], b[0]) > 8:
            overlaps += 1
opted = 0 if GUI_IO_util.grid_layout_enabled else 1
title = ''
try:
    title = w.title()
except Exception:
    pass
print("META overflow=%d overlaps=%d opted=%d title=%s"
      % (overflow, overlaps, opted, base64.b64encode(title.encode('utf-8')).decode()))

try:
    w.deiconify()
    w.geometry('+0+0')
    w.lift()
    w.attributes('-topmost', True)
    w.update()
    time.sleep(0.5)
    w.update()
    from PIL import ImageGrab
    x, y = w.winfo_rootx(), w.winfo_rooty()
    ww, hh = w.winfo_width(), w.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + ww, y + hh)).save(png)
    print("SHOT ok")
except Exception as e:
    print("SHOT_FAIL", str(e)[:120])
'''.replace("{src}", _SRC)


def thumb_data_uri(png_path, max_w=680):
    from PIL import Image
    img = Image.open(png_path).convert('RGB')
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
    buf = _io.BytesIO()
    img.save(buf, format='JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    os.makedirs(_SHOTS, exist_ok=True)
    guis = sorted(os.path.basename(f) for f in glob.glob(os.path.join(_SRC, '*_main.py'))
                  if not any(s in os.path.basename(f) for s in _NOT_GUI))
    print('Building + screenshotting %d GUIs (windows will flash open)...\n' % len(guis))
    cards = []
    for f in guis:
        png = os.path.join(_SHOTS, f.replace('.py', '.png'))
        try:
            p = subprocess.run([sys.executable, '-c', _WORKER, f, png],
                               capture_output=True, text=True, timeout=300, cwd=_SRC)
        except subprocess.TimeoutExpired:
            p = None
        out = p.stdout if p else ''
        meta = next((ln for ln in out.splitlines() if ln.startswith('META')), '')
        overflow = overlaps = opted = None
        title = ''
        if meta:
            d = dict(kv.split('=', 1) for kv in meta.split() if '=' in kv)
            overflow, overlaps, opted = int(d['overflow']), int(d['overlaps']), int(d['opted'])
            try:
                title = base64.b64decode(d['title']).decode('utf-8')
            except Exception:
                title = ''
        if not title:
            title = f.replace('_main.py', '').replace('_', ' ')
        bad = overflow is None or overflow > 4 or (overlaps or 0) > 0
        status = 'BUILD?' if overflow is None else ('OFF' if bad else 'OK')
        img_html = ('<img loading="lazy" src="%s" alt="%s">' % (thumb_data_uri(png), esc(f))
                    if os.path.exists(png) else '<div class="noshot">no screenshot</div>')
        note = '' if overflow is None else 'overflow %d px &middot; overlaps %d' % (overflow, overlaps)
        cards.append(dict(status=status, file=f, title=title, note=note, img=img_html,
                          opted=(opted == 1)))
        print('%-8s %-46s %s' % (status, f, title[:60]))

    order = {'OFF': 0, 'BUILD?': 1, 'OK': 2}
    grid = sorted([c for c in cards if not c['opted']], key=lambda c: (order.get(c['status'], 3), c['file']))
    special = sorted([c for c in cards if c['opted']], key=lambda c: (order.get(c['status'], 3), c['file']))

    def anchor(f):
        return 'g_' + f.replace('.', '_')

    def toc(group):
        return '\n'.join(
            '<li><a href="#%s" class="%s">%s</a></li>' % (anchor(c['file']), c['status'].lower().rstrip('?'), esc(c['title']))
            for c in group)

    def section(title, subtitle, group):
        body = []
        for c in group:
            body.append(
                '<figure id="%s" class="card %s"><figcaption>'
                '<span class="badge">%s</span><span class="t">%s</span>'
                '<span class="fn">%s</span><span class="note">%s</span></figcaption>%s</figure>'
                % (anchor(c['file']), c['status'].lower().rstrip('?'), c['status'],
                   esc(c['title']), esc(c['file']), c['note'], c['img']))
        return ('<h2>%s <span class="cnt">%d</span></h2><p class="sub">%s</p><div class="grid">%s</div>'
                % (title, len(group), subtitle, '\n'.join(body)))

    n_off = sum(1 for c in cards if c['status'] != 'OK')
    html = '''<!doctype html><meta charset="utf-8"><title>NLP Suite - GUI gallery</title>
<style>
 body{font:14px system-ui,Segoe UI,sans-serif;margin:0;padding:22px;background:#f4f4f6;color:#222;max-width:1500px}
 h1{font-size:20px;margin:0 0 2px} h2{font-size:16px;margin:30px 0 2px;border-bottom:2px solid #ccc;padding-bottom:4px}
 .cnt{color:#999;font-weight:400;font-size:13px} .sub{color:#666;margin:2px 0 14px;font-size:12px}
 .toc{display:grid;grid-template-columns:1fr 1fr;gap:6px 30px;background:#fff;border:1px solid #ddd;
   border-radius:8px;padding:14px 18px;margin:10px 0 8px}
 .toc h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#888}
 .toc ul{margin:0;padding:0;list-style:none;columns:2;font-size:12.5px} .toc li{margin:1px 0;break-inside:avoid}
 .toc a{text-decoration:none;color:#345} .toc a:hover{text-decoration:underline}
 .toc a.off{color:#c22;font-weight:600} .toc a.build{color:#c80}
 .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(360px,1fr))}
 .card{margin:0;background:#fff;border:1px solid #ddd;border-radius:8px;overflow:hidden;scroll-margin-top:12px}
 .card.off{border-color:#d33;box-shadow:0 0 0 2px #d3333322} .card.build{border-color:#e90}
 figcaption{padding:8px 10px;font-size:12px;border-bottom:1px solid #eee;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
 .t{font-weight:600} .fn{color:#aaa;font-size:11px;font-family:ui-monospace,Consolas,monospace} .note{color:#999;margin-left:auto}
 .badge{font-weight:700;font-size:10px;padding:2px 7px;border-radius:10px;color:#fff;background:#3a3;align-self:center}
 .off .badge{background:#d33} .build .badge{background:#e90}
 img{display:block;width:100%;height:auto} .noshot{padding:40px;text-align:center;color:#bbb}
 @media(prefers-color-scheme:dark){body{background:#16171a;color:#ddd}.card,.toc{background:#212226;border-color:#333}
   figcaption,h2{border-color:#2c2d31}.sub,.cnt{color:#999}.toc a{color:#8ab}}
</style>
<h1>NLP Suite - GUI gallery</h1>
<p class="sub">''' + '%d GUIs &middot; %d flagged &middot; this machine\'s Windows rendering only' % (len(cards), n_off) + '''</p>
<div class="toc">
 <div><h3>Full-grid GUIs</h3><ul>''' + toc(grid) + '''</ul></div>
 <div><h3>Special GUIs (absolute layout)</h3><ul>''' + toc(special) + '''</ul></div>
</div>
''' + section('Full-grid GUIs', 'Standard layout via the grid (placeWidget &rarr; columns).', grid) + \
        section('Special GUIs', 'Kept on absolute .place (GUI_IO_util.GRID_OPT_OUT) &mdash; too coupled to pixel positions for grid.', special)

    out_path = os.path.join(_HERE, 'gui_gallery.html')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('\n%d GUIs (%d grid, %d special), %d flagged.  Open: %s'
          % (len(cards), len(grid), len(special), n_off, out_path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
