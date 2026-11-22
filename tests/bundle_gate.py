#!/usr/bin/env python
"""Bundle gate: does a built NLP Suite still have everything its code uses?   (see docs below)

WHY THIS EXISTS
Trimming the build (NLP_Suite.spec excludes, packages dropped from requirements) can break a tool only
in the downloaded zip: pytest and gui_smoke.py stub the heavy libraries, so a missing package never
shows there. The same was true of #1725, a crash that only the built zip had. This script looks at a
built, unzipped NLP Suite and records three things, then compares two such records (a release that
works, and the candidate) and fails on anything the candidate lost.

  imports  Every third-party module imported anywhere in the bundle's src/ (also inside functions,
           where a tool imports a package only when RUN is clicked), imported for real by the
           bundle's own python-env.
  guis     Every src/*_main.py built by the bundle's python-env under the real Tk, with its windows
           hidden, the event loop skipped and every popup recorded instead of shown.
  menu     The frozen menu (the NLP_Suite program, built by NLP_Suite.spec): started with
           --from-welcome and watched for a crash, and its module archive compared with every
           third-party module the menu's code can reach (the spec's excludes are where this bites).

USAGE
  python tests/bundle_gate.py snapshot <unzipped NLP_Suite folder> -o base.json [--pyinstaller PY]
  python tests/bundle_gate.py compare base.json candidate.json

--pyinstaller names a Python that has PyInstaller installed (any version that can read the build's
archive); without it the menu's archive is not listed. Each snapshot takes a few minutes and opens
(hidden) Tk windows. It writes only inside the bundle folder and a temporary HOME, never in yours.
`compare` exits 1 when the candidate lost something the base had.
"""

import argparse
import ast
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import tempfile
import time

MARK = "@@GATE@@"


def out(line=""):
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


# ---------------------------------------------------------------- static scan of the source (pure)


def imported_modules(source):
    """Top-level names of the absolute imports in `source`, at any depth (inside functions too)."""
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def scan_src(src_dir):
    """{module name: set of top-level names it imports} for every .py file directly in src_dir.
    A file that does not parse maps to None."""
    graph = {}
    for fn in sorted(os.listdir(src_dir)):
        if fn.endswith(".py"):
            with open(os.path.join(src_dir, fn), encoding="utf-8", errors="replace") as f:
                try:
                    graph[fn[:-3]] = imported_modules(f.read())
                except SyntaxError:
                    graph[fn[:-3]] = None
    return graph


def third_party(graph, stdlib):
    """{third-party name: sorted importing modules}: neither local (in graph) nor standard library."""
    users = {}
    for mod, names in graph.items():
        for name in names or ():
            if name not in graph and name not in stdlib and name != "__future__":
                users.setdefault(name, set()).add(mod)
    return {name: sorted(mods) for name, mods in sorted(users.items())}


def reachable_third_party(graph, start, stdlib):
    """{third-party name: import chain from `start`} for every third-party module that the local
    modules reachable from `start` import (shortest chain, breadth first)."""
    chains = {start: [start]}
    queue = [start]
    found = {}
    while queue:
        mod = queue.pop(0)
        for name in sorted(graph.get(mod) or ()):
            if name in graph:
                if name not in chains:
                    chains[name] = chains[mod] + [name]
                    queue.append(name)
            elif name not in stdlib and name != "__future__" and name not in found:
                found[name] = chains[mod] + [name]
    return found


# ---------------------------------------------------------------- comparing two snapshots (pure)


def _popups(gui):
    return {(p[0], p[1]) for p in gui.get("popups", []) if p[0] in ("showerror", "showwarning")}


def compare(base, cand):
    """(failures, notes): what the candidate lost against the base, and what changed otherwise."""
    fails, notes = [], []
    bi, ci = base.get("imports", {}), cand.get("imports", {})
    for name, rec in sorted(ci.items()):
        if rec["ok"]:
            continue
        where = ", ".join(rec["used_by"][:4]) + (" ..." if len(rec["used_by"]) > 4 else "")
        if name not in bi:
            fails.append(f"import {name}: newly imported by {where}, and fails: {rec['error']}")
        elif bi[name]["ok"]:
            fails.append(f"import {name}: worked in the base, fails now ({rec['error']}); used by {where}")
    for name in sorted(set(bi) - set(ci)):
        notes.append(f"import {name}: no longer imported by any module")

    bg, cg = base.get("guis", {}), cand.get("guis", {})
    for gui, rec in sorted(cg.items()):
        old = bg.get(gui)
        if old is None:
            if rec["status"] != "ok":
                fails.append(f"GUI {gui}: new, and {rec['status']}: {rec['error']}")
            continue
        if old["status"] == "ok" and rec["status"] != "ok":
            fails.append(f"GUI {gui}: built in the base, {rec['status']} now: {rec['error']}")
        for kind, title in sorted(_popups(rec) - _popups(old)):
            fails.append(f"GUI {gui}: a new {kind} popup at opening: {title!r}")
        lost = sorted(set(old.get("modules", [])) - set(rec.get("modules", [])))
        if lost and rec["status"] == "ok":
            notes.append(
                f"GUI {gui}: no longer loads at opening: {', '.join(lost[:8])}" + (" ..." if len(lost) > 8 else "")
            )
    for gui in sorted(set(bg) - set(cg)):
        notes.append(f"GUI {gui}: gone from the candidate")

    bm, cm = base.get("menu", {}), cand.get("menu", {})
    if bm.get("runs") and not cm.get("runs"):
        fails.append(f"frozen menu: started in the base, not now: {cm.get('error')}")
    if cm.get("tracebacks") and not bm.get("tracebacks"):
        fails.append(f"frozen menu: prints a traceback now: {cm.get('tracebacks')[-1]}")
    base_missing = set(bm.get("missing_from_archive", {}))
    for name, chain in sorted(cm.get("missing_from_archive", {}).items()):
        if name not in base_missing:
            notes.append(f"REVIEW frozen menu: can reach {name} but it is not in the archive: {' -> '.join(chain)}")

    for part in ("total_mb", "python_env_mb", "internal_mb"):
        if part in base.get("sizes", {}) and part in cand.get("sizes", {}):
            notes.append(f"size {part}: {base['sizes'][part]} -> {cand['sizes'][part]}")
    return fails, notes


# ---------------------------------------------------------------- running things in the bundle


def bundle_python(bundle):
    for rel in (("python-env", "bin", "python3"), ("python-env", "python.exe")):
        path = os.path.join(bundle, *rel)
        if os.path.exists(path):
            return path
    raise SystemExit("No python-env in " + bundle + ": is this an unzipped NLP Suite build?")


def _env(home):
    # DO_NOT_TRACK: otherwise the first-run usage question covers the frozen menu for the whole check
    env = dict(
        os.environ, HOME=home, USERPROFILE=home, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", DO_NOT_TRACK="1"
    )
    env.pop("PYTHONPATH", None)
    return env


def _run(cmd, cwd, home, timeout):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=_env(home), capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return None, "", "timed out after " + str(timeout) + " s"


def _last_line(text):
    lines = [x for x in text.strip().splitlines() if x.strip()]
    return lines[-1][:300] if lines else ""


def check_import(py, name, home):
    code, out, err = _run([py, "-c", "import " + name], tempfile.gettempdir(), home, 300)
    return code == 0, "" if code == 0 else (_last_line(err) or "exit code " + str(code))


# Run by the bundle's python for one GUI: real Tk, hidden windows, no event loop, popups recorded.
_GUI_HARNESS = (
    r"""
import json, os, runpy, sys, traceback
src, target = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
os.chdir(src)
sys.argv = [os.path.join(src, target)]
popups = []
import tkinter, tkinter.messagebox as mb, tkinter.filedialog as fd, webbrowser
_tk_init, _top_init = tkinter.Tk.__init__, tkinter.Toplevel.__init__
def tk_init(self, *a, **k):
    _tk_init(self, *a, **k)
    self.withdraw()
def top_init(self, *a, **k):
    _top_init(self, *a, **k)
    try:
        self.withdraw()
    except Exception:
        pass
tkinter.Tk.__init__, tkinter.Toplevel.__init__ = tk_init, top_init
tkinter.Wm.deiconify = tkinter.Wm.wm_deiconify = lambda self: None
tkinter.Misc.mainloop = lambda self, n=0: None
tkinter.mainloop = lambda n=0: None
tkinter.Misc.wait_window = lambda self, window=None: None
def recorder(kind, answer):
    def show(title=None, message=None, **k):
        popups.append([kind, str(title), str(message)[:300]])
        return answer
    return show
for kind in ("showinfo", "showwarning", "showerror"):
    setattr(mb, kind, recorder(kind, "ok"))
for kind in ("askyesno", "askokcancel", "askretrycancel", "askyesnocancel"):
    setattr(mb, kind, recorder(kind, False))
mb.askquestion = recorder("askquestion", "no")
for kind in ("askopenfilename", "askopenfilenames", "askdirectory", "asksaveasfilename"):
    setattr(fd, kind, recorder(kind, ""))
webbrowser.open = webbrowser.open_new = webbrowser.open_new_tab = recorder("webbrowser", True)
# Nothing this GUI starts may run outside the harness: another GUI (run_script), a program, a shell
# command. Each is recorded and reported as having succeeded.
import subprocess
class FakePopen:
    def __init__(self, args, *a, **k):
        popups.append(["launch", " ".join(map(str, args)) if isinstance(args, (list, tuple)) else str(args), ""])
        self.args, self.returncode, self.pid, self.stdout, self.stderr, self.stdin = args, 0, 0, None, None, None
        self.empty = "" if (k.get("text") or k.get("universal_newlines") or k.get("encoding") or k.get("errors")) else b""
    def poll(self): return 0
    def wait(self, timeout=None): return 0
    def communicate(self, input=None, timeout=None): return (self.empty, self.empty)
    def kill(self): pass
    def terminate(self): pass
    def __enter__(self): return self
    def __exit__(self, *exc): return False
subprocess.Popen = FakePopen
os.system = lambda cmd: popups.append(["launch", str(cmd), ""]) or 0
if hasattr(os, "startfile"):
    os.startfile = lambda path, *a, **k: popups.append(["launch", str(path), ""])
import run_script_util
for name in ("run_script", "run_script_detached"):
    if hasattr(run_script_util, name):
        setattr(run_script_util, name, lambda script, *a, _n=name, **k: popups.append([_n, str(script), ""]))
status, error = "ok", ""
try:
    runpy.run_path(os.path.join(src, target), run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        status, error = "exit", "SystemExit(" + repr(e.code) + ")"
    else:
        status, error = "exit", "SystemExit(0) while opening"
except BaseException:
    status, error = "crash", traceback.format_exc().strip().splitlines()[-1][:300]
mods = sorted({m.split(".")[0] for m in list(sys.modules) if not m.startswith("_")})
print("""
    + repr(MARK)
    + r""" + json.dumps({"status": status, "error": error, "popups": popups, "modules": mods}))
sys.stdout.flush()
os._exit(0)
"""
)


def check_gui(py, src, target, home):
    code, out, err = _run([py, "-c", _GUI_HARNESS, src, target], src, home, 240)
    for line in out.splitlines():
        if line.startswith(MARK):
            return json.loads(line[len(MARK) :])
    error = _last_line(err) or ("exit code " + str(code))
    return {"status": "crash" if code is not None else "timeout", "error": error, "popups": [], "modules": []}


def frozen_program(bundle):
    """The frozen menu program (NLP_Suite.exe or NLP_Suite), or None."""
    for name in ("NLP_Suite.exe", "NLP_Suite"):
        if os.path.isfile(os.path.join(bundle, name)):
            return os.path.join(bundle, name)
    return None


def _close_tree(p):
    """Close a process started in its own group, and everything it started."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
    else:
        import signal

        try:
            os.killpg(p.pid, signal.SIGTERM)
            p.wait(10)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def seed_config(bundle):
    """Start every GUI as on an install that is already set up: license accepted, welcome screens seen.
    (The first-run path is checked by hand on a fresh unzip; here it would open setup windows instead.)"""
    config = os.path.join(bundle, "config")
    os.makedirs(config, exist_ok=True)
    license_csv = os.path.join(config, "license_config.csv")
    if not os.path.isfile(license_csv):
        with open(license_csv, "w") as f:
            f.write("I/O configuration label,Path,Sort order,Item separator character(s),Date format,Date position\n")
    with open(os.path.join(config, "launch_count.json"), "w") as f:
        json.dump({"count": 99}, f)


# CustomTkinter's DPI-scaling timer can fire after the gate has closed the menu (1.6.42 does it too, 1 run in 2)
_SHUTDOWN_NOISE = "application has been destroyed"


def menu_tracebacks(log_text):
    """The last line of each traceback in the frozen menu's log, without the one CustomTkinter prints at shutdown."""
    lasts = [
        b.strip().splitlines()[-1][:300] for b in log_text.split("Traceback (most recent call last):")[1:] if b.strip()
    ]
    return [line for line in lasts if _SHUTDOWN_NOISE not in line]


def check_frozen_menu(bundle, home, seconds=40):
    exe = frozen_program(bundle)
    if exe is None:
        return {"runs": False, "error": "no NLP_Suite program in the bundle", "tracebacks": []}
    log = os.path.join(home, "frozen_menu.log")
    # Its own process group, so that the menu and every window it opens are closed together afterwards.
    windows = os.name == "nt"
    with open(log, "w") as f:
        p = subprocess.Popen(
            [exe, "--from-welcome"],
            cwd=bundle,
            env=_env(home),
            stdout=f,
            stderr=subprocess.STDOUT,
            creationflags=0x00000200 if windows else 0,  # CREATE_NEW_PROCESS_GROUP
            start_new_session=not windows,
        )
        deadline = time.time() + seconds
        while time.time() < deadline and p.poll() is None:
            time.sleep(1)
        runs = p.poll() is None
        _close_tree(p)
    with open(log, encoding="utf-8", errors="replace") as f:
        text = f.read()
    tracebacks = menu_tracebacks(text)
    error = "" if runs else "exited with code " + str(p.returncode) + ": " + _last_line(text)
    return {"runs": runs, "error": error, "tracebacks": tracebacks}


_ARCHIVE_LISTER = r"""
import json, sys
from PyInstaller.archive.readers import CArchiveReader
c = CArchiveReader(sys.argv[1])
names = {n.split(".")[0] for n in c.open_embedded_archive("PYZ.pyz").toc}
names |= {n.split(".")[0] for n in c.toc}
print(json.dumps(sorted(names)))
"""


def frozen_archive_modules(bundle, pyinstaller_python):
    """Top-level module names inside the frozen menu: its PYZ archive, plus _internal's packages and
    extension modules."""
    exe = frozen_program(bundle)
    if exe is None:
        raise SystemExit("No NLP_Suite program in " + bundle)
    p = subprocess.run([pyinstaller_python, "-c", _ARCHIVE_LISTER, exe], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise SystemExit("Could not read the menu's archive: " + _last_line(p.stderr))
    names = set(json.loads(p.stdout))
    internal = os.path.join(bundle, "_internal")
    for entry in os.listdir(internal) if os.path.isdir(internal) else ():
        names.add(entry.split(".")[0])
    return names


def folder_mb(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return round(total / 1e6)


def snapshot(bundle, pyinstaller_python=None, jobs=4, log=out):
    bundle = os.path.abspath(bundle)
    src = os.path.join(bundle, "src")
    py = bundle_python(bundle)
    home = tempfile.mkdtemp(prefix="bundle_gate_home_")
    seed_config(bundle)
    stdlib = set(
        json.loads(
            subprocess.run(
                [py, "-c", "import sys, json; print(json.dumps(sorted(sys.stdlib_module_names)))"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
    )
    graph = scan_src(src)
    users = third_party(graph, stdlib)
    result = {"bundle": bundle, "version": open(os.path.join(bundle, "lib", "release_version.txt")).read().strip()}

    log(f"imports: {len(users)} third-party modules used in src/")
    imports = {}
    with cf.ThreadPoolExecutor(jobs) as pool:
        futures = {pool.submit(check_import, py, name, home): name for name in users}
        for fut in cf.as_completed(futures):
            name = futures[fut]
            ok, err = fut.result()
            imports[name] = {"ok": ok, "error": err, "used_by": users[name]}
    result["imports"] = dict(sorted(imports.items()))

    targets = sorted(fn for fn in os.listdir(src) if fn.endswith("_main.py"))
    log(f"guis: building {len(targets)} GUIs")
    guis = {}
    with cf.ThreadPoolExecutor(jobs) as pool:
        futures = {pool.submit(check_gui, py, src, t, home): t for t in targets}
        for fut in cf.as_completed(futures):
            guis[futures[fut]] = fut.result()
            log(f"  {futures[fut]}: {guis[futures[fut]]['status']}")
    result["guis"] = dict(sorted(guis.items()))

    log("menu: starting the frozen menu")
    menu = check_frozen_menu(bundle, home)
    if pyinstaller_python:
        present = frozen_archive_modules(bundle, pyinstaller_python)
        reach = reachable_third_party(graph, "NLP_menu_main", stdlib)
        menu["missing_from_archive"] = {n: c for n, c in sorted(reach.items()) if n not in present}
    result["menu"] = menu

    result["sizes"] = {
        "total_mb": folder_mb(bundle),
        "python_env_mb": folder_mb(os.path.join(bundle, "python-env")),
        "internal_mb": folder_mb(os.path.join(bundle, "_internal")),
    }
    return result


def summary(snap):
    bad_imports = [n for n, r in snap["imports"].items() if not r["ok"]]
    bad_guis = [g for g, r in snap["guis"].items() if r["status"] != "ok"]
    lines = [
        f"version {snap['version']}: {len(snap['imports'])} imports ({len(bad_imports)} fail), "
        f"{len(snap['guis'])} GUIs ({len(bad_guis)} do not build), frozen menu "
        + ("runs" if snap["menu"].get("runs") else "DOES NOT RUN: " + snap["menu"].get("error", "")),
    ]
    lines += [f"  import {n}: {snap['imports'][n]['error']}" for n in bad_imports]
    lines += [f"  GUI {g}: {snap['guis'][g]['status']}: {snap['guis'][g]['error']}" for g in bad_guis]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a built NLP Suite for what its code uses.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot", help="record what a built, unzipped NLP Suite can import and build")
    s.add_argument("bundle")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--pyinstaller", help="a Python with PyInstaller, to list the frozen menu's archive")
    s.add_argument("--jobs", type=int, default=4)
    c = sub.add_parser("compare", help="fail on what the candidate lost against the base")
    c.add_argument("base")
    c.add_argument("candidate")
    args = parser.parse_args(argv)

    if args.cmd == "snapshot":
        snap = snapshot(args.bundle, args.pyinstaller, args.jobs)
        with open(args.output, "w") as f:
            json.dump(snap, f, indent=1)
        out(summary(snap))
        return 0

    with open(args.base) as f:
        base = json.load(f)
    with open(args.candidate) as f:
        cand = json.load(f)
    fails, notes = compare(base, cand)
    out(f"base {base.get('version')} vs candidate {cand.get('version')}")
    for line in notes:
        out("  note: " + line)
    for line in fails:
        out("  FAIL: " + line)
    out(f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
