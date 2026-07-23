"""Build every src/*_main.py under real Tk, screenshot each window, and assemble ONE HTML page so you
can scan all the GUIs at a glance and spot anything off.

Output:
  tests/gui_screenshots/<gui>.png   -- full-resolution shot of each GUI
  tests/gui_gallery.html            -- one self-contained page: every GUI as a card with a PASS/FAIL
                                       badge (same overflow/overlap check as gui_layout_gate.py)

Run in the Anaconda **NLP** env (real libs, and PIL for the screen grab):
    python tests/gui_gallery.py
Windows will flash open one at a time while it grabs them -- that's expected. Leave the machine be
for the ~2 minutes it runs so nothing covers the windows mid-grab.

Same honest scope as the gate: this is THIS machine's Windows rendering. It is not macOS.
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
_NOT_GUI = ('NLP_setup_',)  # include NLP_menu + NLP_welcome here -- we WANT to see them

# Worker: build one GUI, run the overflow/overlap check, map the window, grab it to a PNG.
_WORKER = r'''
import sys, os, time
os.environ['NLP_SILENT'] = '1'
SRC = r"{src}"
sys.path.insert(0, SRC)
import importlib.util
import IO_libraries_util
IO_libraries_util.install_all_Python_packages = lambda *a, **k: True
IO_libraries_util.check_java_installation = lambda *a, **k: True
import GUI_util
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

# overflow + overlap (same logic as the gate; window-relative coords; skip Notebook internals)
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
print("VERDICT overflow=%d overlaps=%d win=%d" % (overflow, overlaps, win_w))

# map the window and grab it
try:
    w.deiconify()
    w.lift()
    w.attributes('-topmost', True)
    w.update()
    time.sleep(0.45)
    w.update()
    from PIL import ImageGrab
    x, y = w.winfo_rootx(), w.winfo_rooty()
    ww, hh = w.winfo_width(), w.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + ww, y + hh))
    img.save(png)
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
        v = next((ln for ln in out.splitlines() if ln.startswith('VERDICT')), '')
        overflow = overlaps = None
        if v:
            d = dict(kv.split('=') for kv in v.split() if '=' in kv)
            overflow, overlaps = int(d['overflow']), int(d['overlaps'])
        bad = overflow is None or overflow > 4 or (overlaps or 0) > 0
        status = 'BUILD?' if overflow is None else ('OFF' if bad else 'OK')
        if os.path.exists(png):
            uri = thumb_data_uri(png)
            img_html = '<img src="%s" alt="%s">' % (uri, f)
        else:
            img_html = '<div class="noshot">no screenshot</div>'
        note = '' if overflow is None else 'overflow %d px&nbsp;&middot;&nbsp;overlaps %d' % (overflow, overlaps)
        cards.append((status, f, note, img_html))
        print('%-8s %-46s %s' % (status, f, note))

    order = {'OFF': 0, 'BUILD?': 1, 'OK': 2}
    cards.sort(key=lambda c: (order.get(c[0], 3), c[1]))
    n_off = sum(1 for c in cards if c[0] != 'OK')
    body = []
    for status, name, note, img_html in cards:
        body.append(
            '<figure class="card %s"><figcaption><span class="badge">%s</span> %s'
            '<span class="note">%s</span></figcaption>%s</figure>'
            % (status.lower().rstrip('?'), status, name, note, img_html))
    html = '''<!doctype html><meta charset="utf-8"><title>NLP Suite - GUI gallery</title>
<style>
 body{font:14px system-ui,Segoe UI,sans-serif;margin:0;padding:20px;background:#f4f4f6;color:#222}
 h1{font-size:18px;margin:0 0 4px} .sub{color:#666;margin:0 0 18px}
 .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(360px,1fr))}
 .card{margin:0;background:#fff;border:1px solid #ddd;border-radius:8px;overflow:hidden}
 .card.off{border-color:#d33;box-shadow:0 0 0 2px #d3333322}
 figcaption{padding:8px 10px;font-size:12px;border-bottom:1px solid #eee;display:flex;
   align-items:center;gap:8px;flex-wrap:wrap}
 .note{color:#888;margin-left:auto}
 .badge{font-weight:700;font-size:11px;padding:2px 7px;border-radius:10px;color:#fff;background:#3a3}
 .off .badge{background:#d33} .build\\? .badge,.card.build .badge{background:#e90}
 img{display:block;width:100%;height:auto} .noshot{padding:40px;text-align:center;color:#aaa}
 @media(prefers-color-scheme:dark){body{background:#16171a;color:#ddd}.card{background:#212226;border-color:#333}
   figcaption{border-color:#2c2d31}.sub{color:#999}}
</style>
<h1>NLP Suite - GUI gallery</h1>
<p class="sub">''' + '%d GUIs, %d flagged (shown first). This machine\'s Windows rendering only.' % (len(cards), n_off) + '''</p>
<div class="grid">''' + '\n'.join(body) + '</div>'
    out_path = os.path.join(_HERE, 'gui_gallery.html')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('\n%d GUIs, %d flagged.  Open: %s' % (len(cards), n_off, out_path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
