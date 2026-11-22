"""Compare two tool sweeps (tool_sweep.py run): a baseline release and a candidate.

Standard library only, so pytest can test it without the Suite's heavy libraries; comparing Excel files needs
openpyxl in the Python that runs `compare` (any zip's python-env has it); without it each Excel file is listed as an error.

A recipe REGRESSES when the candidate lost something the baseline had: the baseline ran (ok or WARNED)
and the candidate did not, or the candidate wrote fewer files, or a file the baseline wrote is missing.
Contents are compared table by table, with each sweep's own folders replaced by <OUT> and <BUNDLE>, and
classified for a person to review: identical, numbers that moved (with the largest change), text that
changed, rows or columns that changed. Only regressions make `compare` fail; content changes are listed,
because a new library version (transformers in 1.6.46) moves model scores on purpose.

NOISE lists what is known to differ from one run to the next of the same code (docs/future-work.md §14).
"""

import csv
import fnmatch
import io
import json
import math
import os

RAN = ("ok", "WARNED")
# a recipe is listed as SLOWER (for review, not a failure) when the candidate took both this many times as
# long and this many seconds more; timings depend on the machine's load and on first-run model downloads
SLOWER_RATIO = 1.5
SLOWER_SECONDS = 10
TABLES = (".csv", ".xlsx")
# absolute and relative tolerance under which two numbers count as the same (floating-point noise)
ABS_TOL = 1e-9
REL_TOL = 1e-9

# (recipe pattern, file pattern, rule, columns). Rules:
#   skip       the file's contents are not compared (its name still is)
#   ignore     these columns are not compared
#   unordered  rows are compared as a multiset, after dropping the columns given
NOISE = [
    # langdetect's confidence and vocd-D's sampling are random
    ("*", "*anguage*detect*", "ignore", ("Probability", "Confidence", "langdetect probability")),
    ("*", "*exical*iversity*", "ignore", ("vocd-D", "vocd_D", "VOCD-D")),
    # CoreNLP's speed assessment is a timing
    ("*", "*speed*assess*", "skip", ()),
    # Character Emotion Arcs builds a sentence's characters from a set: their order, and which of
    # "Lady Elliot" / "Elliot" names a row, change from run to run (same scores)
    ("*", "*character_emotion_arcs*", "unordered", ("Character",)),
]


def norm_path(text, roots):
    for root, tag in roots:
        if root:
            text = text.replace(root, tag)
    return text


def read_report(sweep_dir):
    """Latest record per recipe from <sweep>/report.jsonl."""
    records = {}
    path = os.path.join(sweep_dir, "report.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    records[rec["recipe"]] = rec
    return records


def read_meta(sweep_dir):
    path = os.path.join(sweep_dir, "meta.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def roots_of(sweep_dir):
    meta = read_meta(sweep_dir)
    roots = [(os.path.abspath(sweep_dir), "<OUT>")]
    if meta.get("out") and meta["out"] != os.path.abspath(sweep_dir):  # the sweep was moved after it ran
        roots.append((meta["out"], "<OUT>"))
    if meta.get("bundle"):
        roots.append((meta["bundle"], "<BUNDLE>"))
    # longest first, so a root inside another is replaced before it
    return sorted(roots, key=lambda r: -len(r[0]))


def files_of(folder):
    found = []
    for root, _, names in os.walk(folder):
        for n in names:
            if n == ".DS_Store" or n.startswith("~$"):
                continue
            found.append(os.path.relpath(os.path.join(root, n), folder))
    return sorted(found)


def rule_for(recipe, rel):
    for recipe_pat, file_pat, rule, columns in NOISE:
        if fnmatch.fnmatch(recipe, recipe_pat) and fnmatch.fnmatch(os.path.basename(rel).lower(), file_pat.lower()):
            return rule, columns
    return None, ()


def as_number(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def read_csv_table(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return [row for row in csv.reader(f)]


def read_xlsx_tables(path):
    """{sheet: rows} with every cell as text; formulas as written (=hyperlink(...))."""
    import openpyxl  # in the bundle's python-env

    book = openpyxl.load_workbook(path, read_only=True, data_only=False)
    tables = {}
    for sheet in book.worksheets:
        tables[sheet.title] = [["" if v is None else str(v) for v in row] for row in sheet.iter_rows(values_only=True)]
    book.close()
    return tables


def compare_rows(a, b, roots_a, roots_b, ignore=(), unordered=False):  # noqa: PLR0917
    """Classify two tables (lists of rows; the first row is the header).

    Returns (verdict, detail): verdict is 'identical', 'numbers', 'text', 'shape' or 'columns'.
    """
    a = [[norm_path(c, roots_a) for c in row] for row in a]
    b = [[norm_path(c, roots_b) for c in row] for row in b]
    header_a, header_b = (a[0] if a else []), (b[0] if b else [])
    if header_a != header_b:
        return "columns", f"columns {header_a[:12]} -> {header_b[:12]}"
    keep = [i for i, name in enumerate(header_a) if name not in ignore]
    a = [[row[i] if i < len(row) else "" for i in keep] for row in a[1:]]
    b = [[row[i] if i < len(row) else "" for i in keep] for row in b[1:]]
    if len(a) != len(b):
        return "shape", f"{len(a)} rows -> {len(b)}"
    if unordered:
        a, b = sorted(a), sorted(b)
    worst, text_cells, first_text = 0.0, 0, ""
    for i, (row_a, row_b) in enumerate(zip(a, b, strict=False)):
        for j, (x, y) in enumerate(zip(row_a, row_b, strict=False)):
            if x == y:
                continue
            nx, ny = as_number(x), as_number(y)
            if nx is not None and ny is not None:
                if not math.isclose(nx, ny, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                    worst = max(worst, abs(nx - ny))
                continue
            text_cells += 1
            if not first_text:
                name = header_a[keep[j]] if j < len(keep) and keep[j] < len(header_a) else str(j)
                first_text = f"row {i + 1}, {name}: {x[:80]!r} -> {y[:80]!r}"
    if text_cells:
        return "text", f"{text_cells} cells, first {first_text}"
    if worst:
        return "numbers", f"largest change {worst:.3g}"
    return "identical", ""


def compare_file(recipe, rel, path_a, path_b, roots_a, roots_b):  # noqa: PLR0917
    """(verdict, detail) for one output file both sweeps wrote."""
    rule, columns = rule_for(recipe, rel)
    if rule == "skip":
        return "skipped", "known noise"
    ext = os.path.splitext(rel)[1].lower()
    unordered = rule == "unordered"
    try:
        if ext == ".csv":
            return compare_rows(
                read_csv_table(path_a), read_csv_table(path_b), roots_a, roots_b, ignore=columns, unordered=unordered
            )
        if ext == ".xlsx":
            sheets_a, sheets_b = read_xlsx_tables(path_a), read_xlsx_tables(path_b)
            if list(sheets_a) != list(sheets_b):
                return "columns", f"sheets {list(sheets_a)} -> {list(sheets_b)}"
            order = ["identical", "numbers", "text", "shape", "columns"]
            verdict, details = "identical", []
            for name in sheets_a:
                v, d = compare_rows(
                    sheets_a[name], sheets_b[name], roots_a, roots_b, ignore=columns, unordered=unordered
                )
                if v != "identical":
                    details.append(f"{name}: {d}")
                    verdict = max(verdict, v, key=order.index)
            return verdict, "; ".join(details)
    except (OSError, ValueError, KeyError, ImportError) as e:
        return "error", f"{type(e).__name__}: {e}"
    return "unchecked", ""


def compare_sweeps(base_dir, cand_dir):
    """Every recipe both sweeps ran: [(recipe, problems, file_results)].

    problems: regressions (the candidate lost something); file_results: [(rel, verdict, detail)].
    """
    base, cand = read_report(base_dir), read_report(cand_dir)
    roots_a, roots_b = roots_of(base_dir), roots_of(cand_dir)
    results = []
    for recipe in sorted(set(base) | set(cand)):
        a, b = base.get(recipe), cand.get(recipe)
        problems, file_results = [], []
        if a is None and b is not None:
            results.append((recipe, ["new in the candidate: {}".format(b["status"])], []))
            continue
        if a is None or b is None:
            status = a["status"] if a is not None else "?"
            results.append((recipe, [f"not run in the candidate (baseline: {status})"], []))
            continue
        if a["status"] in RAN and b["status"] not in RAN:
            problems.append(
                "status {} -> {}{}".format(a["status"], b["status"], (": " + b["error"]) if b.get("error") else "")
            )
        out_a, out_b = os.path.join(base_dir, recipe), os.path.join(cand_dir, recipe)
        files_a, files_b = files_of(out_a), files_of(out_b)
        lost = [f for f in files_a if f not in files_b]
        if lost:
            problems.append(f"{len(lost)} file(s) missing: {', '.join(lost[:5])}")
        slower = timing(a, b)
        if slower:
            file_results.append(("(time)", "slower", slower))
        gained = [f for f in files_b if f not in files_a]
        if gained:
            file_results.append(("(new files)", "new", ", ".join(gained[:5])))
        for rel in files_a:
            if rel in files_b and os.path.splitext(rel)[1].lower() in TABLES:
                v, d = compare_file(recipe, rel, os.path.join(out_a, rel), os.path.join(out_b, rel), roots_a, roots_b)
                file_results.append((rel, v, d))
        results.append((recipe, problems, file_results))
    return results


def timing(a, b):
    """'12s -> 40s (3.3x)' when the candidate ran clearly slower, else ''."""
    secs_a, secs_b = a.get("secs") or 0, b.get("secs") or 0
    if a.get("status") in RAN and b.get("status") in RAN and secs_a > 0:
        if secs_b >= secs_a * SLOWER_RATIO and secs_b - secs_a >= SLOWER_SECONDS:
            return f"{secs_a:.0f}s -> {secs_b:.0f}s ({secs_b / secs_a:.1f}x)"
    return ""


def format_comparison(results, base_label="baseline", cand_label="candidate"):
    lines, regressions = [], 0
    counts = {}
    for _, _, files in results:
        for _, v, _ in files:
            counts[v] = counts.get(v, 0) + 1
    lines.append(f"{base_label} vs {cand_label}: {len(results)} recipes")
    lines.append("tables: " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items())))
    for recipe, problems, files in results:
        review = [(rel, v, d) for rel, v, d in files if v not in ("identical", "skipped")]
        if not problems and not review:
            continue
        lines.append("")
        lines.append(("REGRESSION  " if problems else "REVIEW      ") + recipe)
        regressions += bool(problems)
        lines += ["    " + p for p in problems]
        lines += [f"    {v:<9} {rel}" + (f"  ({d})" if d else "") for rel, v, d in review]
    lines.append("")
    lines.append(f"{regressions} regression(s)")
    return "\n".join(lines), regressions


def table_text(rows):
    """For tests and debugging: rows -> csv text."""
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue()
