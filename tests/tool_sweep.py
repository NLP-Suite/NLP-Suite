#!/usr/bin/env python
"""Tool sweep: run every tool of a built NLP Suite the way RUN does, and compare two releases.

WHY THIS EXISTS
pytest and gui_smoke.py check helpers and that every window opens; bundle_gate.py checks that every import
resolves. None of them clicks RUN, so a tool can open fine and still produce nothing (or something else)
after a library upgrade. Before this, each release was checked by running hand-picked tools. This runs
each tool's real run() on the Suite's own sample data, on a zip's own python-env, and compares the
outputs with the last release's.

HOW
Each recipe (tool_sweep_recipes.py) runs in its own process on the bundle's python-env: it imports the
tool's *_main.py without showing it, sets its widgets, and calls run(), which is what RUN does. NLP_SILENT
answers every dialog with its safe default; files the Suite would open (Excel, the browser) are recorded,
not opened. A recipe that needs software the zip lacks (CoreNLP, MALLET, the internet) is SKIPPED with
the reason. Each recipe works on its own copy of config/ and of the sample input, so nothing in the bundle
changes.

USAGE
  python tests/tool_sweep.py list
  python tests/tool_sweep.py run <unzipped NLP_Suite> -o <sweep dir> [--only a,b] [--skip a,b]
         [--external-config <NLP_setup_external_software_config.csv>] [--input <folder of .txt>]
         [--timeout-scale N]
  python tests/tool_sweep.py compare <baseline sweep dir> <candidate sweep dir>
  python tests/tool_sweep.py report <sweep dir>

--input runs every recipe on another corpus, to see what grows with its size (raise --timeout-scale with
it). `compare` lists a recipe as SLOWER when it took 1.5x as long and 10 s more (for review: timings depend
on the machine's load). `run` can also take a source checkout (a folder with src/ and lib/ and no python-env): it then uses this
Python. --only and --skip take recipe names or fnmatch patterns (e.g. 'sentiment_*'). `compare` exits 1 when
the candidate lost something the baseline had (docs/future-work.md §14 lists the known noise).
NLP_SILENT=1 and DO_NOT_TRACK=1 are set for you. Outputs: <sweep dir>/<recipe>/, logs/, report.jsonl, report.md.
"""

import argparse
import fnmatch
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
from typing import Any
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tool_sweep_compare  # noqa: E402
import tool_sweep_recipes  # noqa: E402

MARK = "@@SWEEP@@"
ORDER = {"CRASHED": 0, "TIMEOUT": 1, "FAILED": 2, "EMPTY": 3, "WARNED": 4, "SKIPPED": 5, "ok": 6}


def out(line=""):
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


# ------------------------------------------------------------------------------------------- parent side


def bundle_python(bundle):
    py = os.path.join(bundle, "python-env", "bin", "python")
    if sys.platform == "win32":
        py = os.path.join(bundle, "python-env", "python.exe")
    return py if os.path.isfile(py) else sys.executable


def select(names, only, skip):
    def hit(name, patterns):
        return any(fnmatch.fnmatch(name, p.strip()) for p in patterns if p.strip())

    chosen = [n for n in names if (not only or hit(n, only)) and not hit(n, skip)]
    return chosen


def ordered(recipes):
    """Recipes that read another recipe's output ('from:<recipe>:...') run after it."""
    names = {r.name for r in recipes}
    done, result = set(), []
    pending = list(recipes)
    while pending:
        progressed = False
        for r in list(pending):
            dep = r.input.split(":")[1] if r.input.startswith("from:") else None
            if dep is None or dep in done or dep not in names:
                result.append(r)
                done.add(r.name)
                pending.remove(r)
                progressed = True
        if not progressed:  # a cycle: run the rest as they are
            result += pending
            break
    return result


def prepare_inputs(bundle, sweep, corpus=None):
    """Copies of the sample data inside the sweep, so tools never write next to the bundle's own files.

    corpus: a folder of .txt files used for every recipe instead of the sample data (--input), to see how
    the tools scale: 5 documents do not show what grows with the corpus (1.6.45's fixes showed only at 958).
    """
    lib = os.path.join(bundle, "lib", "sampleData")
    inputs = os.path.join(sweep, "_inputs")
    articles = os.path.join(inputs, "articles")
    stories = os.path.join(inputs, "stories")
    for d in (articles, stories):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    if corpus:
        for name in sorted(os.listdir(corpus)):
            if name.endswith(".txt"):
                shutil.copy(os.path.join(corpus, name), articles)
                shutil.copy(os.path.join(corpus, name), stories)
        return inputs
    for name in sorted(os.listdir(os.path.join(lib, "newspaperArticles"))):
        if name.endswith(".txt"):
            shutil.copy(os.path.join(lib, "newspaperArticles", name), articles)
            shutil.copy(os.path.join(lib, "newspaperArticles", name), stories)
    for name in sorted(os.listdir(lib)):
        if name.endswith(".txt"):
            shutil.copy(os.path.join(lib, name), stories)
    return inputs


def run_sweep(bundle, sweep, only=(), skip=(), external_config=None, timeout_scale=1.0, corpus=None):  # noqa: PLR0917
    bundle, sweep = os.path.abspath(bundle), os.path.abspath(sweep)
    if not os.path.isdir(os.path.join(bundle, "src")):
        sys.exit("not an NLP Suite folder (no src/): " + bundle)
    os.makedirs(os.path.join(sweep, "logs"), exist_ok=True)
    python = bundle_python(bundle)
    version = ""
    vfile = os.path.join(bundle, "lib", "release_version.txt")
    if os.path.isfile(vfile):
        with open(vfile, encoding="utf-8") as f:
            version = f.read().strip()
    meta = dict(
        bundle=bundle,
        python=python,
        version=version,
        started=time.strftime("%Y-%m-%d %H:%M"),
        input=os.path.abspath(corpus) if corpus else "lib/sampleData",
    )
    with open(os.path.join(sweep, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    prepare_inputs(bundle, sweep, corpus)
    recipes = ordered(
        [
            r
            for r in tool_sweep_recipes.RECIPES
            if r.name in select([x.name for x in tool_sweep_recipes.RECIPES], only, skip)
        ]
    )
    out(f"NLP Suite {version or '?'} at {bundle}, {len(recipes)} recipes, python {python}")
    env = dict(os.environ, NLP_SILENT="1", DO_NOT_TRACK="1", TOKENIZERS_PARALLELISM="false", PYTHONIOENCODING="utf-8")
    jre = os.path.join(bundle, "jre")
    if os.path.isdir(jre):
        env["JAVA_HOME"] = jre
        env["PATH"] = os.path.join(jre, "bin") + os.pathsep + env.get("PATH", "")
    report = os.path.join(sweep, "report.jsonl")
    start_all = time.time()
    for i, r in enumerate(recipes, 1):
        log = os.path.join(sweep, "logs", r.name + ".log")
        cmd = [python, "-I", os.path.abspath(__file__), "_one", r.name, "--bundle", bundle, "--sweep", sweep]
        if external_config:
            cmd += ["--external-config", os.path.abspath(external_config)]
        start = time.time()
        record: dict[str, Any] | None = None
        with open(log, "w", encoding="utf-8") as f:
            try:
                proc = subprocess.run(
                    cmd, stdout=f, stderr=subprocess.STDOUT, env=env, timeout=r.timeout_min * 60 * timeout_scale
                )
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code = "timeout"
        with open(log, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith(MARK):
                    record = json.loads(line[len(MARK) :])
        if record is None:
            status = "TIMEOUT" if code == "timeout" else "CRASHED"
            record = dict(
                recipe=r.name,
                module=r.module,
                status=status,
                secs=round(time.time() - start, 1),
                files=0,
                error="process {}; see logs/{}.log".format(
                    f"ran past {r.timeout_min * timeout_scale:.0f} min" if code == "timeout" else f"exited with {code}",
                    r.name,
                ),
            )
        record["known"] = r.known
        with open(report, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        secs, nfiles, err = record.get("secs", 0), record.get("files", 0), (record.get("error") or "")[:110]
        out(f"[{i}/{len(recipes)}] {r.name:<34} {record['status']:<8} {secs:6.0f}s {nfiles:>4} files  {err}")
    out("done in %.1f min" % ((time.time() - start_all) / 60))
    write_report(sweep)


def write_report(sweep):
    records = tool_sweep_compare.read_report(sweep)
    meta = tool_sweep_compare.read_meta(sweep)
    rows = sorted(records.values(), key=lambda r: (ORDER.get(r["status"], 9), r["recipe"]))
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = [
        "# Tool sweep: NLP Suite {}".format(meta.get("version", "?")),
        "",
        "{}; {}".format(meta.get("bundle", ""), ", ".join(f"{k} {n}" for k, n in sorted(counts.items()))),
        "",
        "| recipe | status | s | files | problem |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        problem = r.get("error") or next(iter(r.get("dialogs_error") or []), "") or ""
        if r.get("known") and r["status"] not in tool_sweep_compare.RAN:
            problem = "(known: {}) {}".format(r["known"], problem)
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                r["recipe"], r["status"], r.get("secs", ""), r.get("files", ""), problem.replace("|", "/")[:200]
            )
        )
    ran = sorted((r for r in rows if r.get("secs")), key=lambda r: -r["secs"])[:10]
    lines += ["", "## Slowest recipes", "", "| recipe | s |", "|---|---|"]
    lines += [f"| {r['recipe']} | {r['secs']:.0f} |" for r in ran]
    lines += ["", "## Details", ""]
    for r in rows:
        if r["status"] in ("ok", "SKIPPED"):
            continue
        lines += ["### {}: {}".format(r["recipe"], r["status"]), ""]
        if r.get("dialogs_error"):
            lines += ["Error dialogs:", ""] + ["- " + d for d in r["dialogs_error"]] + [""]
        if r.get("traceback"):
            lines += ["```", r["traceback"].strip(), "```", ""]
        if r.get("empty"):
            lines += ["Empty outputs: " + ", ".join(r["empty"]), ""]
    path = os.path.join(sweep, "report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    out("report: " + path)


# -------------------------------------------------------------------------------------------- child side


def missing_need(need, config_dir):
    """Why a recipe cannot run here, or ''."""
    if need == "internet":
        try:
            socket.create_connection(("nominatim.openstreetmap.org", 443), timeout=5).close()
            return ""
        except OSError as e:
            return f"no internet ({e})"
    names = {"corenlp": "Stanford CoreNLP", "mallet": "MALLET", "gephi": "Gephi"}
    import csv

    path = os.path.join(config_dir, "NLP_setup_external_software_config.csv")
    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            for row in csv.reader(f):
                if row and row[0].strip() == names[need]:
                    where = row[1].strip() if len(row) > 1 else ""
                    if where and os.path.exists(where):
                        return ""
                    return f"{names[need]}: path {where!r} not found" if where else f"{names[need]} not set up"
    return f"{names[need]} not set up (no path in NLP_setup_external_software_config.csv; pass --external-config)"


def written(path):
    files, empty = [], []
    for root, _, names in os.walk(path):
        for n in names:
            p = os.path.join(root, n)
            files.append(p)
            try:
                if os.path.getsize(p) == 0:
                    empty.append(p)
                elif n.endswith(".csv"):
                    with open(p, encoding="utf-8", errors="replace") as f:
                        if sum(1 for _ in zip(range(2), f, strict=False)) < 2:
                            empty.append(p)
            except OSError:
                empty.append(p)
    return files, empty


def run_one(name, bundle, sweep, external_config=None):
    r = tool_sweep_recipes.by_name()[name]
    src = os.path.join(bundle, "src")
    rec_out = os.path.join(sweep, name)
    shutil.rmtree(rec_out, ignore_errors=True)
    os.makedirs(rec_out)
    # the recipe's own config/, so the package switch and the run's settings never touch the bundle
    config_dir = os.path.join(sweep, "_config", name)
    shutil.rmtree(config_dir, ignore_errors=True)
    shutil.copytree(os.path.join(bundle, "config"), config_dir)
    if external_config:
        shutil.copy(external_config, os.path.join(config_dir, "NLP_setup_external_software_config.csv"))
    record: dict[str, Any] = dict(
        recipe=name,
        module=r.module,
        status="ok",
        secs=0,
        files=0,
        error="",
        traceback="",
        dialogs=[],
        dialogs_error=[],
        opened=[],
        handoffs=[],
        empty=[],
        py_warnings={},
        when=time.strftime("%Y-%m-%d %H:%M"),
    )

    def emit():
        sys.stdout.write(MARK + json.dumps(record) + "\n")
        sys.stdout.flush()

    for need in r.needs:
        why = missing_need(need, config_dir)
        if why:
            record.update(status="SKIPPED", error=why)
            emit()
            return
    if r.package:
        set_package(config_dir, r.package)

    sys.path.insert(0, src)
    os.chdir(src)
    import GUI_IO_util

    GUI_IO_util.configPath = config_dir
    import GUI_util

    GUI_util.window.mainloop = lambda *a, **k: None
    # charts_util reads the chart type from this widget, which only the GUI sets
    GUI_util.charts_type_options_widget.set("Bar chart")
    capture(record, r)

    input_dir, input_file = resolve_input(r, sweep, bundle)
    import importlib

    start = time.time()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            if r.input.startswith("from:") and not input_file:
                raise FileNotFoundError(
                    "no {} in {}'s output (run it first)".format(*tuple(r.input.split(":")[2:0:-1]))
                )
            gui = importlib.import_module(r.module)
            set_io(GUI_util, rec_out, input_dir, input_file)
            for var, value in r.set.items():
                widget = getattr(gui, var, None)
                if widget is None or not hasattr(widget, "set"):
                    raise AttributeError(f"recipe sets {r.module}.{var}, which the GUI no longer has")
                widget.set(value)
            gui.run(*r.args)
        except SystemExit as e:  # the Suite calls sys.exit() on missing packages
            record.update(status="FAILED", error=f"SystemExit({e.code!r})", traceback=traceback.format_exc())
        except BaseException as e:  # noqa: BLE001 (the point is to record it)
            record.update(status="FAILED", error=f"{type(e).__name__}: {e}", traceback=traceback.format_exc())
    record["secs"] = round(time.time() - start, 1)
    files, empty = written(rec_out)
    record["files"] = len(files)
    record["empty"] = [os.path.relpath(p, rec_out) for p in empty][:20]
    if record["status"] == "ok" and not files:
        record["status"] = "EMPTY"
    elif record["status"] == "ok" and (record["dialogs_error"] or empty):
        record["status"] = "WARNED"
    seen = {}
    for w in caught:
        message = str(w.message).splitlines()[0][:200] if str(w.message) else ""
        key = f"{w.category.__name__} {os.path.basename(w.filename)}:{w.lineno}: {message}"
        seen[key] = seen.get(key, 0) + 1
    record["py_warnings"] = dict(sorted(seen.items(), key=lambda kv: -kv[1])[:15])
    record["traceback"] = record["traceback"][-4000:]
    emit()


def set_package(config_dir, package):
    import csv

    path = os.path.join(config_dir, "NLP_default_package_language_config.csv")
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    rows[1][0] = package
    if package == "Stanford CoreNLP":
        rows[1][1] = "Neural Network"
        for i in (6, 7, 8):  # memory, document length, sentence length: the Setup GUI's defaults
            rows[1][i] = {6: "4", 7: "90000", 8: "100"}[i] if rows[1][i] in ("", "0", "0.0") else rows[1][i]
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def resolve_input(r, sweep, bundle):
    inputs = os.path.join(sweep, "_inputs")
    if r.input in ("articles", "stories"):
        return os.path.join(inputs, r.input), ""
    if r.input.startswith("file:"):
        return "", os.path.join(bundle, "lib", r.input[5:])
    if r.input.startswith("from:"):
        _, recipe, pattern = r.input.split(":", 2)
        for root, _, names in os.walk(os.path.join(sweep, recipe)):
            for n in sorted(names):
                if fnmatch.fnmatch(n, pattern):
                    return "", os.path.join(root, n)
        return "", ""
    raise ValueError(f"unknown input {r.input!r}")


def set_io(GUI_util, out_dir, input_dir, input_file):
    GUI_util.inputFilename.set(input_file)
    GUI_util.input_main_dir_path.set("" if input_file else input_dir)
    GUI_util.output_dir_path.set(out_dir)
    GUI_util.open_csv_output_checkbox.set(0)
    GUI_util.charts_package_options_widget.set("Excel")
    GUI_util.data_transformation_options_widget.set("No transformation")
    GUI_util.config_filename_selected_config.set("NLP_default_IO_config.csv")


def capture(record, recipe):
    """Record dialogs, timed alerts, files the Suite would open, and GUIs it would launch."""
    import tkinter.messagebox as mb

    for kind in ("showwarning", "showerror", "showinfo"):
        silent = getattr(mb, kind)

        def show(title="", message="", *a, _kind=kind, _silent=silent, **k):
            line = "{} | {} | {}".format(_kind[4:], title, " ".join(str(message).split())[:300])
            record["dialogs"].append(line)
            if _kind == "showerror":
                record["dialogs_error"].append(line)
            return _silent(title, message, *a, **k)

        setattr(mb, kind, show)
    for kind in ("askyesno", "askokcancel", "askyesnocancel", "askquestion", "askretrycancel"):
        silent = getattr(mb, kind)

        def ask(title="", message="", *a, _kind=kind, _silent=silent, **k):
            text = f"{title} {message}"
            yes = any(key in text for key in recipe.yes)
            if yes:
                answer = "yes" if _kind == "askquestion" else True
            else:
                answer = _silent(title, message, *a, **k)
            record["dialogs"].append(f"{_kind} | {title} | {' '.join(str(message).split())[:200]} -> {answer}")
            return answer

        setattr(mb, kind, ask)
    import GUI_IO_util

    def no_box(window, message_title, message_text, buttonType="OK", timeout=3000):
        record["dialogs"].append("timed | {} | {}".format(message_title, " ".join(str(message_text).split())[:200]))
        return ""

    GUI_IO_util.message_box_widget = no_box
    ask = GUI_IO_util.enter_value_widget

    def answer(masterTitle, textCaption, *a, **k):
        for key, value in recipe.answers.items():
            if key in str(masterTitle) or key in str(textCaption):
                record["dialogs"].append(f"answered | {masterTitle} | {value}")
                return (value, "") if not isinstance(value, tuple) else value
        return ask(masterTitle, textCaption, *a, **k)

    GUI_IO_util.enter_value_widget = answer
    import webbrowser

    import IO_files_util

    def opened(*a, **k):
        record["opened"].append(" ".join(str(x) for x in a)[:300])
        return True

    IO_files_util.open_in_desktop = opened
    webbrowser.open = webbrowser.open_new = webbrowser.open_new_tab = opened
    if hasattr(os, "startfile"):
        setattr(os, "startfile", opened)  # noqa: B010 (os.startfile exists on Windows only)
    import run_script_util

    def handoff(name, *a, **k):
        record["handoffs"].append(str(name))

    run_script_util.run_script = handoff
    if hasattr(run_script_util, "run_script_detached"):
        run_script_util.run_script_detached = handoff


# --------------------------------------------------------------------------------------------------- CLI


def main(argv=None):
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    pr = sub.add_parser("run")
    pr.add_argument("bundle")
    pr.add_argument("-o", "--out", required=True)
    pr.add_argument("--only", default="")
    pr.add_argument("--skip", default="")
    pr.add_argument("--external-config", default=None)
    pr.add_argument("--timeout-scale", type=float, default=1.0)
    pr.add_argument("--input", default=None, help="a folder of .txt files to use instead of lib/sampleData")
    pc = sub.add_parser("compare")
    pc.add_argument("base")
    pc.add_argument("cand")
    prep = sub.add_parser("report")
    prep.add_argument("sweep")
    p1 = sub.add_parser("_one")  # internal: one recipe, in the bundle's python-env
    p1.add_argument("recipe")
    p1.add_argument("--bundle", required=True)
    p1.add_argument("--sweep", required=True)
    p1.add_argument("--external-config", default=None)
    a = p.parse_args(argv)
    if a.cmd == "list":
        for r in tool_sweep_recipes.RECIPES:
            known = ("  known: " + r.known) if r.known else ""
            out(f"{r.name:<34} {r.module:<32} {','.join(r.needs)}{known}")
        n_recipes, n_left = len(tool_sweep_recipes.RECIPES), len(tool_sweep_recipes.NOT_COVERED)
        out(f"\n{n_recipes} recipes; not covered: {n_left} GUIs (see NOT_COVERED)")
    elif a.cmd == "run":
        run_sweep(
            a.bundle,
            a.out,
            a.only.split(",") if a.only else (),
            a.skip.split(",") if a.skip else (),
            a.external_config,
            a.timeout_scale,
            a.input,
        )
    elif a.cmd == "report":
        write_report(a.sweep)
    elif a.cmd == "compare":
        results = tool_sweep_compare.compare_sweeps(a.base, a.cand)
        text, regressions = tool_sweep_compare.format_comparison(
            results,
            tool_sweep_compare.read_meta(a.base).get("version", a.base),
            tool_sweep_compare.read_meta(a.cand).get("version", a.cand),
        )
        out(text)
        return 1 if regressions else 0
    elif a.cmd == "_one":
        run_one(a.recipe, a.bundle, a.sweep, a.external_config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
