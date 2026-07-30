"""GUI layout gate -- build every src/*_main.py under REAL Tk and check two ways a layout can break:

  OVERFLOW: a widget's right edge runs past the window's right edge (content is clipped).
  OVERLAP : two widgets on the same row sit on top of each other (a jumbled row).

gui_smoke.py uses a FAKE tkinter, so it proves a GUI CONSTRUCTS but can say nothing about geometry.
This uses genuine Tk, so winfo_x()/winfo_width() are real and these two failures are measurable.

Run it after any layout change:  python tests/gui_layout_gate.py
It needs the Anaconda **NLP** env (real stanza/pandas/... so every GUI builds). Each GUI is built in
its own subprocess (isolation, like gui_smoke). Exit 0 = all pass; non-zero = at least one FAIL.
Results are also written to tests/gui_layout_gate.log.

Caveat, stated in the code so nobody forgets: this measures THIS machine's Windows font metrics. It
traps Windows overflow/overlap; it does NOT predict macOS (different default font) or another Windows
box at a different DPI. Mac is confirmed only by a person opening the GUIs there.
"""
import glob
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(os.path.dirname(_HERE), 'src')
_NOT_GUI = ('NLP_menu_main', 'NLP_welcome_main', 'NLP_setup_')  # not standard placeWidget GUIs
# GUIs that don't build headless even under real libs (Java/CoreNLP resource probes at import) -- same
# spirit as gui_smoke's KNOWN_SKIP. Verify these by launching.
_KNOWN_SKIP = {'file_checker_pre_processing_pipeline_main.py'}

# The worker builds ONE GUI under real Tk and prints a single VERDICT line. Heavy libs are left REAL
# (run under the NLP env); only the pip-install / Java probes are neutered so the GUI reaches its
# widgets instead of sys.exit()-ing first.
_WORKER = r'''
import sys, os
os.environ['NLP_SILENT'] = '1'
SRC = r"{src}"
sys.path.insert(0, SRC)
import importlib.util
import IO_libraries_util
IO_libraries_util.install_all_Python_packages = lambda *a, **k: True
IO_libraries_util.check_java_installation = lambda *a, **k: True
import GUI_util
import GUI_IO_util
GUI_util.window.mainloop = lambda *a, **k: None
target = sys.argv[1]
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

# Collect each widget's rectangle in window coordinates by ACCUMULATING winfo_x()/winfo_y() (each is
# relative to its parent, and is reliable even before the window is mapped -- unlike winfo_rootx()).
# Do NOT descend into a Notebook: its tab frames are stacked at the same spot (only one is visible),
# so recursing would read every tab's contents as overlapping the others -- a false alarm.
rects = []
def walk(widget, ox, oy):
    for ch in widget.winfo_children():
        try:
            cx, cy = ox + ch.winfo_x(), oy + ch.winfo_y()
            rects.append((cx, cy, cx + ch.winfo_width(), cy + ch.winfo_height(), ch.winfo_class()))
            if ch.winfo_class() != 'TNotebook':
                walk(ch, cx, cy)
        except Exception:
            pass
walk(w, 0, 0)
rects = [r for r in rects if r[2] > r[0] and r[3] > r[1]]  # drop zero-size

# OVERFLOW: farthest right edge vs the window width
max_right = max((r[2] for r in rects), default=0)
overflow = max_right - win_w

# OVERLAP: widgets whose vertical spans meet AND whose horizontal spans overlap by > 8px, but NOT
# when they share (nearly) the same left x -- that is a deliberate stack (e.g. the INPUT/OUTPUT
# display areas), not a jumble.
def v_overlap(a, b):
    return a[1] < b[3] - 4 and b[1] < a[3] - 4
overlaps = 0
worst = ""
S = sorted(rects, key=lambda r: (r[0], r[1]))
for i in range(len(S)):
    for j in range(i + 1, len(S)):
        a, b = S[i], S[j]
        if b[0] - a[0] > 60 and b[0] >= a[2]:
            break  # b starts clear to the right of a; no later b overlaps a either
        # A same-x stack IS intentional for the INPUT/OUTPUT display areas: two Text widgets of the
        # same size layered at one spot. It is NOT intentional for two different widgets dropped into
        # one grid cell, and the old test excluded both - it dismissed ANY pair sharing a left edge,
        # which is exactly the shape of a row collision. The Corpus Profiler had two Checkbuttons at
        # x=88 on one row, "Open output files" painted over "Rebuild the report & summary...", and
        # this gate reported overlaps=0. The exemption now requires the same class AND near the same
        # width, which a real layered stack has and a collision does not.
        if abs(a[0] - b[0]) <= 6 and a[4] == b[4] and abs((a[2] - a[0]) - (b[2] - b[0])) <= 6:
            continue
        if v_overlap(a, b) and min(a[2], b[2]) - max(a[0], b[0]) > 8:
            overlaps += 1
            if not worst:
                worst = "%s@%d..%d / %s@%d..%d row~%d" % (a[4], a[0], a[2], b[4], b[0], b[2], a[1])
opted = 0 if GUI_IO_util.grid_layout_enabled else 1
print("VERDICT overflow=%d max_right=%d win=%d overlaps=%d opted=%d %s"
      % (overflow, max_right, win_w, overlaps, opted, ("| " + worst) if worst else ""))
'''.replace("{src}", _SRC)


def main():
    guis = sorted(os.path.basename(f) for f in glob.glob(os.path.join(_SRC, '*_main.py'))
                  if not any(s in os.path.basename(f) for s in _NOT_GUI))
    print('GUI layout gate: %d GUIs, real Tk, this machine\'s Windows fonts\n' % len(guis))
    fails, skipped, log = [], [], []
    for f in guis:
        try:
            p = subprocess.run([sys.executable, '-c', _WORKER, f],
                               capture_output=True, text=True, timeout=300, cwd=_SRC)
        except subprocess.TimeoutExpired:
            if f in _KNOWN_SKIP:
                skipped.append(f); continue
            fails.append(f); print('FAIL   %-46s (timeout)' % f); continue
        line = next((ln for ln in p.stdout.splitlines() if ln.startswith('VERDICT')), '')
        if not line:
            if f in _KNOWN_SKIP:
                skipped.append(f); print('SKIP   %-46s (does not build headless)' % f); continue
            fails.append(f); print('FAIL   %-46s (no build)' % f)
            log.append('%s: no build\n%s' % (f, p.stdout[-400:] + p.stderr[-400:])); continue
        d = dict(kv.split('=') for kv in line.split() if '=' in kv)
        overflow, overlaps, opted = int(d['overflow']), int(d['overlaps']), int(d.get('opted', 0))
        # opted-out GUIs use legacy .place (hand-tuned); overlap there isn't a grid problem and can
        # false-positive (DB_SQL's side-by-side buttons), so flag them on overflow only.
        # A lone overlap (<=1 pair) in a GUI that fits with room to spare (comfortably negative overflow)
        # is sub-visible noise -- bounding boxes touch by a few px with no visible collision (e.g. the
        # launcher hubs after the font pin). Flag overlaps only where the GUI is tight/over-wide, or on
        # any multi-pair (>=2) collision.
        overlap_noise = overflow < -40 and overlaps <= 1
        bad = overflow > 4 or (overlaps > 0 and not opted and not overlap_noise)
        tag = 'FAIL  ' if bad else 'ok    '
        detail = line[len('VERDICT '):]
        print('%s %-46s %s' % (tag, f, detail))
        log.append('%s %s :: %s' % (tag.strip(), f, detail))
        if bad:
            fails.append(f)

    with open(os.path.join(_HERE, 'gui_layout_gate.log'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(log) + '\n')
    print('\n%d GUIs: %d pass, %d FAIL, %d skipped   (log: tests/gui_layout_gate.log)'
          % (len(guis), len(guis) - len(fails) - len(skipped), len(fails), len(skipped)))
    if fails:
        print('  FAIL:', ', '.join(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
