"""tool_sweep.py: the comparison logic, and that every tool GUI is either swept or listed with a reason."""

import glob
import json
import os

import tool_sweep_compare as tc
import tool_sweep_recipes as tr

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def test_every_main_has_a_recipe_or_a_reason():
    mains = {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(SRC, "*_main.py"))}
    swept = {r.module for r in tr.RECIPES}
    listed = set(tr.NOT_COVERED)
    assert mains - swept - listed == set(), "add a recipe or a NOT_COVERED reason"
    assert (swept | listed) - mains == set(), "recipe or NOT_COVERED entry for a GUI that no longer exists"
    assert swept & listed == set(), "a GUI with recipes is still listed as not covered"


def test_recipe_names_are_unique_and_inputs_known():
    names = [r.name for r in tr.RECIPES]
    assert len(names) == len(set(names))
    fixtures = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "sweep_docs"))
    for r in tr.RECIPES:
        assert r.input in ("articles", "stories", "docs") or r.input.startswith(("file:", "from:", "docs:")), r.name
        assert r.csv == "" or r.csv.startswith("from:"), r.name
        if r.input.startswith("docs:"):
            assert r.input[5:] in fixtures, r.name
        for dep in r.deps():
            assert dep in names, r.name
        assert set(r.needs) <= {"corenlp", "mallet", "gephi", "internet"}, r.name
        assert r.call.isidentifier(), r.name


def test_dependent_recipes_run_after_the_ones_they_read():
    import tool_sweep

    a = tr.Recipe("a", "m")
    b = tr.Recipe("b", "m", input="from:a:*.csv")
    c = tr.Recipe("c", "m", csv="from:b:*.csv")
    assert [r.name for r in tool_sweep.ordered([c, b, a])] == ["a", "b", "c"]
    assert [r.name for r in tool_sweep.ordered([c])] == ["c"]  # its dependency was not selected


ROOTS_A = [("/a/sweep", "<OUT>")]
ROOTS_B = [("/b/sweep", "<OUT>")]


def test_identical_after_paths_are_normalized():
    a = [["Document", "score"], ['=hyperlink("/a/sweep/_inputs/x.txt")', "0.5"]]
    b = [["Document", "score"], ['=hyperlink("/b/sweep/_inputs/x.txt")', "0.5"]]
    assert tc.compare_rows(a, b, ROOTS_A, ROOTS_B) == ("identical", "")


def test_floating_point_noise_is_identical_and_real_changes_are_numbers():
    a = [["k", "v"], ["1", "0.30000000000000004"]]
    assert tc.compare_rows(a, [["k", "v"], ["1", "0.3"]], ROOTS_A, ROOTS_B)[0] == "identical"
    verdict, detail = tc.compare_rows(a, [["k", "v"], ["1", "0.31"]], ROOTS_A, ROOTS_B)
    assert verdict == "numbers" and "0.01" in detail


def test_text_rows_and_columns():
    a = [["k", "v"], ["1", "joy"]]
    assert tc.compare_rows(a, [["k", "v"], ["1", "fear"]], ROOTS_A, ROOTS_B)[0] == "text"
    assert tc.compare_rows(a, [["k", "v"], ["1", "joy"], ["2", "joy"]], ROOTS_A, ROOTS_B)[0] == "shape"
    assert tc.compare_rows(a, [["k", "w"], ["1", "joy"]], ROOTS_A, ROOTS_B)[0] == "columns"


def test_unordered_rule_ignores_row_order_and_the_named_column():
    a = [["Sentence", "Character", "Joy"], ["s1", "Elliot", "0.2"], ["s1", "Anne", "0.1"]]
    b = [["Sentence", "Character", "Joy"], ["s1", "Anne", "0.1"], ["s1", "Lady Elliot", "0.2"]]
    assert tc.compare_rows(a, b, ROOTS_A, ROOTS_B)[0] == "text"
    assert tc.compare_rows(a, b, ROOTS_A, ROOTS_B, ignore=("Character",), unordered=True)[0] == "identical"
    assert tc.rule_for("sentiment_Character_Emotion_Arcs", "x/NLP_character_emotion_arcs.csv")[0] == "unordered"


def _sweep(tmp_path, name, records, files):
    d = tmp_path / name
    d.mkdir()
    (d / "meta.json").write_text(json.dumps({"bundle": str(tmp_path / ("bundle_" + name))}))
    with open(d / "report.jsonl", "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return str(d)


def test_compare_flags_lost_status_and_lost_files_only(tmp_path):
    base = _sweep(
        tmp_path,
        "base",
        [{"recipe": "a", "status": "ok"}, {"recipe": "b", "status": "ok"}, {"recipe": "c", "status": "FAILED"}],
        {"a/out.csv": "k,v\n1,2\n", "a/chart.xlsx.png": "x", "b/out.csv": "k,v\n1,2\n"},
    )
    cand = _sweep(
        tmp_path,
        "cand",
        [
            {"recipe": "a", "status": "ok"},
            {"recipe": "b", "status": "FAILED", "error": "boom"},
            {"recipe": "c", "status": "ok"},
        ],
        {"a/out.csv": "k,v\n1,3\n"},
    )
    results = {name: (problems, files) for name, problems, files in tc.compare_sweeps(base, cand)}
    assert any("missing" in p for p in results["a"][0])  # chart.xlsx.png lost
    assert ("out.csv", "numbers", "largest change 1") in results["a"][1]
    assert any("ok -> FAILED: boom" in p for p in results["b"][0])
    assert results["c"][0] == []  # a recipe that now runs is not a regression
    text, regressions = tc.format_comparison(tc.compare_sweeps(base, cand))
    assert regressions == 2 and "REGRESSION  a" in text and "REGRESSION  b" in text


def test_slower_only_when_both_ratio_and_seconds_are_crossed():
    assert tc.timing({"status": "ok", "secs": 10}, {"status": "ok", "secs": 40}) == "10s -> 40s (4.0x)"
    assert tc.timing({"status": "ok", "secs": 2}, {"status": "ok", "secs": 8}) == ""  # 4x but only 6 s more
    assert tc.timing({"status": "ok", "secs": 100}, {"status": "ok", "secs": 130}) == ""  # 30 s more but 1.3x
    assert tc.timing({"status": "ok", "secs": 10}, {"status": "FAILED", "secs": 40}) == ""


def test_a_moved_sweep_still_normalizes_its_original_folder(tmp_path):
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "meta.json").write_text(json.dumps({"out": "/scratch/sweep"}))
    roots = tc.roots_of(str(moved))
    assert tc.norm_path("/scratch/sweep/a.csv", roots) == "<OUT>/a.csv"
    assert tc.norm_path(str(moved / "a.csv"), roots) == "<OUT>/a.csv"


def test_files_named_after_unstable_names_are_compared_by_count(tmp_path):
    rec = [{"recipe": "sentiment_Character_Emotion_Arcs", "status": "ok"}]
    base = _sweep(tmp_path, "base", rec, {"sentiment_Character_Emotion_Arcs/emotion_arc_Robin.png": "x"})
    same = _sweep(tmp_path, "same", rec, {"sentiment_Character_Emotion_Arcs/emotion_arc_Robin_Ellacott.png": "x"})
    fewer = _sweep(tmp_path, "fewer", rec, {"sentiment_Character_Emotion_Arcs/other.txt": "x"})
    assert tc.compare_sweeps(base, same)[0][1] == []
    assert "fewer per-name" in tc.compare_sweeps(base, fewer)[0][1][0]


def test_random_tools_are_compared_by_files_only():
    assert tc.rule_for("topics_BERTopic_split", "TM-BERTopic_articles/topic_info.csv")[0] == "skip"
    assert tc.rule_for("topics_Gensim", "x/topics.csv")[0] is None


def test_a_recipe_the_baseline_never_ran_is_listed_for_review_not_as_a_regression(tmp_path):
    base = _sweep(tmp_path, "base", [{"recipe": "a", "status": "ok"}], {"a/out.csv": "k\n1\n"})
    cand = _sweep(
        tmp_path,
        "cand",
        [{"recipe": "a", "status": "ok"}, {"recipe": "new_tool", "status": "EMPTY"}],
        {"a/out.csv": "k\n1\n"},
    )
    results = {name: (problems, files) for name, problems, files in tc.compare_sweeps(base, cand)}
    assert results["new_tool"][0] == []
    assert ("(recipe)", "new", "not in the baseline; EMPTY in the candidate") in results["new_tool"][1]
    text, regressions = tc.format_comparison(tc.compare_sweeps(base, cand))
    assert regressions == 0 and "REVIEW      new_tool" in text
    # the other way round, a recipe the candidate did not run, is still a regression
    assert tc.format_comparison(tc.compare_sweeps(cand, base))[1] == 1


def test_files_named_after_the_time_they_were_written_are_compared_by_count(tmp_path):
    rec = [{"recipe": "knowledge_graph_Wikipedia", "status": "ok"}]
    name = (
        "knowledge_graph_Wikipedia/Wikipedia_articles/NLP_byDoc_freq_Wikipedia_output_Nov_23_2026_{}_no_hyperlinks.csv"
    )
    base = _sweep(tmp_path, "base", rec, {name.format("03_25_46"): "k\n1\n"})
    later = _sweep(tmp_path, "later", rec, {name.format("04_40_30"): "k\n1\n"})
    assert tc.compare_sweeps(base, later)[0][1] == []
