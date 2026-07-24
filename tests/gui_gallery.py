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
them -- leave the machine be for the several minutes it runs (often 10+ on a slow machine; it prints
Started/Finished times and a per-GUI [i/total] counter). Honest scope: it captures THIS machine's
rendering, whatever platform that is (the page header names it). When a GUI can't be built/measured
it is marked BUILD? with the failure reason on the card, so a bad run is self-diagnosing.
"""
import base64
import glob
import io as _io
import os
import subprocess
import sys
import time
import webbrowser

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
# Neutralize anything that blocks an unattended build waiting for a human click. Many *_main.py call
# reminders_util.checkReminder at MODULE BUILD time; on a fresh machine (default reminders.csv, all
# reminders ON) that pops a modal per GUI and stalls the screenshot until someone clicks it away -- the
# exact Mac hang where closing the popup let the run continue. Already-seen reminders are suppressed, so
# a machine that has dismissed them never showed this. Stub the reminder + any modal messagebox so the
# gallery runs headless everywhere.
try:
    import reminders_util
    reminders_util.checkReminder = lambda *a, **k: None
except Exception:
    pass
import tkinter.messagebox as _mb
for _n in ('showinfo', 'showwarning', 'showerror'):
    setattr(_mb, _n, lambda *a, **k: None)
for _n in ('askyesno', 'askokcancel', 'askretrycancel', 'askquestion'):
    setattr(_mb, _n, lambda *a, **k: True)
target, png = sys.argv[1], sys.argv[2]
try:
    spec = importlib.util.spec_from_file_location("_gui", os.path.join(SRC, target))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
except SystemExit:
    pass
except BaseException as e:
    # Pinpoint WHERE it failed: the deepest traceback frame inside src/ (the GUI's own code), so a
    # Mac-only build crash reports "TypeError ... @ GIS_Google_Earth_main.py:527" instead of just the
    # type -- otherwise an error that doesn't reproduce on the dev's OS is impossible to locate.
    import traceback as _tb
    _frames = _tb.extract_tb(sys.exc_info()[2])
    _loc = ''
    for _fr in reversed(_frames):
        if os.path.dirname(_fr.filename) == SRC:
            _loc = ' @ %s:%d' % (os.path.basename(_fr.filename), _fr.lineno); break
    if not _loc and _frames:
        _loc = ' @ %s:%d' % (os.path.basename(_frames[-1].filename), _frames[-1].lineno)
    print("BUILD_FAIL", type(e).__name__, str(e)[:120] + _loc); raise SystemExit(0)
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
    w.update_idletasks()
    w.update()
    time.sleep(0.6)
    w.update_idletasks()
    w.update()
    from PIL import ImageGrab
    # DPI scaling: Tk's winfo_* returns LOGICAL pixels, but ImageGrab works in PHYSICAL pixels. On a
    # scaled display (this machine is 150%) a logical bbox grabs a smaller region than the window and
    # cuts the bottom (RUN/CLOSE). Grab the whole physical screen and crop with the logical->physical
    # scale, so it is correct at any scaling.
    full = ImageGrab.grab()
    scale = full.width / w.winfo_screenwidth()
    x, y = w.winfo_rootx(), w.winfo_rooty()
    ww, hh = w.winfo_width(), w.winfo_height()
    box = (round(x * scale), round(y * scale), round((x + ww) * scale), round((y + hh) * scale))
    full.crop(box).save(png)
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


def _elapsed_message(seconds):
    """Human 'H hours, M minutes, and S seconds' string, matching the suite's convert_time wording
    (IO_user_interface_util.convert_time) -- replicated locally so this terminal tool doesn't import
    the GUI stack just to format a duration."""
    h = int(seconds / 3600)
    m = int((seconds - h * 3600) / 60)
    s = int(seconds - h * 3600 - m * 60)
    parts = []
    if h:
        parts.append('%d hour%s' % (h, '' if h == 1 else 's'))
    if m:
        parts.append('%d minute%s' % (m, '' if m == 1 else 's'))
    parts.append('%d second%s' % (s, '' if s == 1 else 's'))
    if len(parts) == 1:
        return parts[0]
    return ', '.join(parts[:-1]) + ' and ' + parts[-1]


def main():
    plat = {'darwin': 'macOS', 'win32': 'Windows', 'linux': 'Linux'}.get(sys.platform, sys.platform)
    os.makedirs(_SHOTS, exist_ok=True)
    guis = sorted(os.path.basename(f) for f in glob.glob(os.path.join(_SRC, '*_main.py'))
                  if not any(s in os.path.basename(f) for s in _NOT_GUI))
    start_time = time.time()
    print('\nStarted running gui_gallery at %s.' % time.strftime('%H:%M:%S'), flush=True)
    print('Building + screenshotting %d GUIs one at a time (windows flash open; this takes several '
          'minutes -- often 10+ on a slow machine)...\n' % len(guis), flush=True)
    cards = []
    total = len(guis)
    for i, f in enumerate(guis, 1):
        print('[%d/%d] %s ...' % (i, total, f), flush=True)
        png = os.path.join(_SHOTS, f.replace('.py', '.png'))
        try:
            p = subprocess.run([sys.executable, '-c', _WORKER, f, png],
                               capture_output=True, text=True, timeout=300, cwd=_SRC)
        except subprocess.TimeoutExpired:
            p = None
        out = p.stdout if p else ''
        err = (p.stderr if p else '') or ''
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
        # When the worker never reported geometry (overflow is None) the GUI didn't build far enough to
        # measure -- the useful signal is WHY. The worker prints BUILD_FAIL/SHOT_FAIL on stdout and any
        # traceback on stderr; surface that here instead of discarding it, so a failed run (e.g. every
        # GUI dying on a Mac) is self-diagnosing rather than a wall of blank "BUILD?" cards.
        reason = ''
        if overflow is None:
            fail = next((ln for ln in out.splitlines()
                         if ln.startswith(('BUILD_FAIL', 'SHOT_FAIL'))), '')
            if p is None:
                reason = 'timeout (>300s)'
            elif fail:
                reason = fail
            elif err.strip():
                reason = err.strip().splitlines()[-1]
            else:
                reason = 'no geometry reported (window never built)'
            reason = reason[:200]
        # Opted-out GUIs use the legacy .place layout (hand-tuned, user-maintained). Their overlap
        # measurement isn't a grid problem and can false-positive (e.g. DB_SQL's side-by-side buttons
        # read as a 35px logical overlap that doesn't show on screen), so flag them on overflow only.
        bad = overflow is None or overflow > 4 or ((overlaps or 0) > 0 and opted != 1)
        status = 'BUILD?' if overflow is None else ('OFF' if bad else 'OK')
        if overflow is None:
            note = '&#9888; ' + esc(reason)
        else:
            note = 'overflow %d px &middot; overlaps %d' % (overflow, overlaps)
            if not os.path.exists(png):
                note += ' &middot; no shot'
        cards.append(dict(status=status, file=f, title=title, note=note, opted=(opted == 1),
                          png=png if os.path.exists(png) else None))
        # Don't truncate a failure reason -- it carries the "@ file:line" crash location we need; only
        # clip the (long, uninformative) window title on OK rows.
        tail = reason if reason else title[:70]
        print('[%d/%d] %-8s %-46s %s' % (i, total, status, f, tail), flush=True)

    order = {'OFF': 0, 'BUILD?': 1, 'OK': 2}
    flagged = sorted([c for c in cards if c['status'] != 'OK'], key=lambda c: (order.get(c['status'], 3), c['file']))
    grid_ok = sorted([c for c in cards if c['status'] == 'OK' and not c['opted']], key=lambda c: c['file'])
    special_ok = sorted([c for c in cards if c['status'] == 'OK' and c['opted']], key=lambda c: c['file'])

    def anchor(f):
        return 'g_' + f.replace('.', '_')

    def toc(group, cls=None):
        return '\n'.join(
            '<li><a href="#%s" class="%s">%s</a></li>' % (anchor(c['file']), cls or c['status'].lower().rstrip('?'), esc(c['title']))
            for c in group) or '<li class="none">none</li>'

    def card_html(c, big):
        if c['png']:
            # link the thumbnail to the full-resolution PNG (opens in a new tab) so a small preview is
            # enough to scan and one click gives you the real thing to inspect
            rel = 'gui_screenshots/' + os.path.basename(c['png'])
            img = '<a href="%s" target="_blank"><img loading="lazy" src="%s" alt="%s"></a>' % (
                rel, thumb_data_uri(c['png'], 1280 if big else 560), esc(c['file']))
        else:
            img = '<div class="noshot">no screenshot</div>'
        # A "special" GUI is an OK card that opted out of grid (legacy .place). Mark it distinctly so it
        # is obvious both in the TOC and while scrolling -- teal accent + a SPECIAL badge, not a green OK.
        special = c['opted'] and c['status'] == 'OK'
        klass = c['status'].lower().rstrip('?') + (' special' if special else '')
        badge = 'SPECIAL' if special else c['status']
        return ('<figure id="%s" class="card %s"><figcaption>'
                '<span class="badge">%s</span><span class="t">%s</span>'
                '<span class="fn">%s</span><span class="note">%s</span></figcaption>%s</figure>'
                % (anchor(c['file']), klass, badge,
                   esc(c['title']), esc(c['file']), c['note'], img))

    def section(title, subtitle, group, big=False):
        if not group:
            return ''
        klass = 'grid big' if big else 'grid'
        return ('<h2>%s <span class="cnt">%d</span></h2><p class="sub">%s</p><div class="%s">%s</div>'
                % (title, len(group), subtitle, klass, '\n'.join(card_html(c, big) for c in group)))

    n_off = len(flagged)
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
 .toc a.off{color:#c22;font-weight:600} .toc a.build{color:#c80} .toc a.special{color:#0a7d55;font-weight:700}
 .toc h3.special-h{color:#0a7d55;margin-top:14px}
 .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(440px,1fr))}
 .grid.big{grid-template-columns:1fr}                 /* flagged GUIs: one per row, full readable width */
 .card{margin:0;background:#fff;border:1px solid #ddd;border-radius:8px;overflow:hidden;scroll-margin-top:12px}
 .card.off{border-color:#d33;box-shadow:0 0 0 2px #d3333322} .card.build{border-color:#e90}
 .card.special{border-color:#0a7d55;box-shadow:0 0 0 2px #0a7d5522} .special .badge{background:#0a7d55}
 figcaption{padding:8px 10px;font-size:12px;border-bottom:1px solid #eee;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
 .t{font-weight:600;font-size:13px} .fn{color:#aaa;font-size:11px;font-family:ui-monospace,Consolas,monospace} .note{color:#999;margin-left:auto}
 .badge{font-weight:700;font-size:10px;padding:2px 7px;border-radius:10px;color:#fff;background:#3a3;align-self:center}
 .off .badge{background:#d33} .build .badge{background:#e90}
 a{display:block} img{display:block;width:100%;height:auto;cursor:zoom-in} .noshot{padding:40px;text-align:center;color:#bbb}
 .none{color:#999;list-style:none} .hint{color:#888;font-size:12px;margin:2px 0 0}
 @media(prefers-color-scheme:dark){body{background:#16171a;color:#ddd}.card,.toc{background:#212226;border-color:#333}
   figcaption,h2{border-color:#2c2d31}.sub,.cnt{color:#999}.toc a{color:#8ab}}
</style>
<h1>NLP Suite - GUI gallery</h1>
<p class="sub">''' + '%d GUIs &middot; %d flagged &middot; rendered on %s (this machine) &middot; click any shot for full resolution' % (len(cards), n_off, plat) + '''</p>
<div class="toc">
 <div><h3>Flagged <span class="cnt">''' + str(len(flagged)) + '''</span></h3><ul>''' + toc(flagged) + '''</ul>
  <h3 class="special-h">Special &mdash; .place opt-outs <span class="cnt">''' + str(len(special_ok)) + '''</span></h3><ul>''' + toc(special_ok, 'special') + '''</ul></div>
 <div><h3>Full-grid &mdash; OK <span class="cnt">''' + str(len(grid_ok)) + '''</span></h3><ul>''' + toc(grid_ok) + '''</ul></div>
</div>
''' + section('Flagged &mdash; needs a look', 'Shown large. Overflow &gt; 4px = a widget past the right edge; overlaps = two widgets on one spot. BUILD? = the GUI never built far enough to measure &mdash; see the reason on the card. (On a HiDPI/scaled display, wide GUIs can clip here that would fit a normal display.)', flagged, big=True) + \
        section('Full-grid GUIs &mdash; OK', 'Standard layout via the grid; these fit cleanly.', grid_ok) + \
        section('Special GUIs &mdash; OK', 'Kept on absolute .place (GUI_IO_util.GRID_OPT_OUT).', special_ok)

    out_path = os.path.join(_HERE, 'gui_gallery.html')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('\n%d GUIs (%d grid OK, %d special OK), %d flagged.  Open: %s'
          % (len(cards), len(grid_ok), len(special_ok), n_off, out_path))
    print('Finished running gui_gallery at %s taking %s.'
          % (time.strftime('%H:%M:%S'), _elapsed_message(time.time() - start_time)), flush=True)
    try:
        webbrowser.open('file://' + os.path.abspath(out_path))
    except Exception:
        pass  # headless/no browser -- the path is printed above
    return 0


if __name__ == '__main__':
    sys.exit(main())
