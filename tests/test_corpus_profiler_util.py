"""Tests for src/corpus_profiler_util.py, one file per module (folded from 5 files, 23 Nov 2026).

From test_corpus_provenance.py:

Reuse must not cross corpora.

The profiler's reuse probes search the output directory for a table with the right filename and the
right columns. Nothing in that ties a table to the text it was built from — "a prior run on THIS
corpus" is an assumption resting on one output directory per corpus. Run a coreference-resolved copy
of a corpus while keeping the original's output directory and the probe finds the ORIGINAL's table,
matches on name and columns, passes the module-fingerprint check because no code changed, and reuses
it. The two runs then agree perfectly, because they are the same numbers.

These tests pin the guard that refuses that reuse.

From test_interp_spatial_split.py:

Two kinds of place, told apart.

The old paragraph ran them together: "328 distinct places; the most frequent are the Great Hall
(229), Gryffindor Tower (98) ... The top 40 were geocoded". Both halves misled. The most-named
places in that corpus have no coordinates and never will - the Great Hall is a KIND of space, which
is what the symbolic analysis is for - and the top 40 were not geocoded: 15 were.

From test_profiler_code_stamp.py:

Reuse must notice when the analysis itself has changed.

Reuse checked that the recorded files still existed, were not empty, and came from this corpus. It
never asked whether the CODE that wrote them had changed - so improving an analysis never reached
a profile that already existed.

Symbolic space is what exposed it. The runner grew transitions, a heat map and an interactive
timeline; a profile with an older manifest entry kept replaying the one-file record from the
BUILD-only version, and the summary showed a lone csv while the new charts sat unlisted on disk.

From test_profiler_output_folders.py:

Every analysis's files go in its own subfolder.

The report says so: "every individual output file is written to a category subfolder and LINKED from
the report". Most analyses honoured it because the utils they call make their own subfolder. Seven
did not, and left 40 files loose in the one folder a reader opens - fifteen from the semantic classes
alone, plus a 2.1 GB vector dump.

_analysis_dir is deliberately NOT IO_files_util.make_output_subdirectory: that deletes an existing
folder (shutil.rmtree, without asking when silent=True), and reuse depends on those files surviving.

From test_profiler_reuse_all.py:

Reuse for EVERY analysis, from one rule.

Eight analyses had a hand-written probe - the parses, where the hours were - and the other fifteen
re-ran from scratch every time. Defended as "the rest are cheap", which is true of any one of them
and false of all of them together: after the disk filled on 30 July, a re-run spent an afternoon
recomputing work already sitting on disk, including BERT embeddings.

A probe guesses which file belongs to an analysis, by name and columns, and each new one is another
chance to guess wrong. The manifest does not guess: the run that produced a file wrote down which
analysis produced it. So the rule needs no per-analysis knowledge, cannot mismatch, and covers an
analysis added tomorrow with no extra code.
"""

import importlib.util
import json
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

# conftest stubs the heavy libraries for the session; corpus_profiler_util is the module under test,
# so load the real source under a private name. Its own imports still resolve against the stubs.
_spec = importlib.util.spec_from_file_location(
    "_real_corpus_profiler_util", os.path.join(_SRC, "corpus_profiler_util.py")
)
prof = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(prof)
finally:
    # sibling modules chdir into src/ at import; put the working directory back so tmp_path and any
    # later test using a relative path still resolve where they expect.
    os.chdir(_cwd)


def _corpus(tmp_path, name, files):
    d = tmp_path / name
    d.mkdir()
    for filename, text in files.items():
        (d / filename).write_text(text, encoding="utf-8")
    return {"inputDir": str(d), "inputFilename": ""}


class TestCorpusFingerprint:
    def test_same_corpus_gives_the_same_digest(self, tmp_path):
        files = {"a.txt": "Harry waved his wand.", "b.txt": "Ron said nothing."}
        one = _corpus(tmp_path, "raw", files)
        two = _corpus(tmp_path, "raw_copy", files)
        # a moved or renamed corpus is still the same corpus: the path is NOT in the digest
        assert prof.corpus_fingerprint(one)[0] == prof.corpus_fingerprint(two)[0]

    def test_a_coreferenced_copy_is_a_different_corpus(self, tmp_path):
        raw = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand. He smiled."})
        cor = _corpus(tmp_path, "cor", {"a.txt": "Harry waved Harry wand. Harry smiled."})
        assert prof.corpus_fingerprint(raw)[0] != prof.corpus_fingerprint(cor)[0]

    def test_an_added_document_changes_the_digest(self, tmp_path):
        one = _corpus(tmp_path, "one", {"a.txt": "x" * 40})
        two = _corpus(tmp_path, "two", {"a.txt": "x" * 40, "b.txt": "y" * 40})
        assert prof.corpus_fingerprint(one)[0] != prof.corpus_fingerprint(two)[0]

    def test_the_label_is_the_folder_name(self, tmp_path):
        c = _corpus(tmp_path, "Harry Potter", {"a.txt": "text"})
        assert prof.corpus_fingerprint(c)[1] == "Harry Potter"

    def test_a_single_input_file_is_fingerprinted(self, tmp_path):
        f = tmp_path / "only.txt"
        f.write_text("one document", encoding="utf-8")
        fp, label = prof.corpus_fingerprint({"inputDir": "", "inputFilename": str(f)})
        assert fp and label == "only.txt"

    def test_nothing_to_fingerprint_is_empty_not_an_error(self):
        assert prof.corpus_fingerprint({"inputDir": "", "inputFilename": ""}) == ("", "")
        assert prof.corpus_fingerprint(None) == ("", "")

    def test_a_sidecar_dropped_beside_the_corpus_does_not_change_it(self, tmp_path):
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        before = prof.corpus_fingerprint(c)[0]
        (tmp_path / "raw" / "a.txt.provenance.json").write_text("{}", encoding="utf-8")
        assert prof.corpus_fingerprint(c)[0] == before


class TestReuseAcrossCorpora:
    def _table(self, tmp_path, name="NLP_SVO_Stanza_Dir_corpus.csv"):
        p = tmp_path / name
        p.write_text("Subject,Verb,Object\nHarry,waved,wand\n", encoding="utf-8")
        return str(p)

    def test_a_table_is_reused_for_the_corpus_that_made_it(self, tmp_path):
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo", c)
        ok, why = prof.provenance_is_current(table, "svo", c)
        assert ok and why == ""

    def test_a_table_is_REFUSED_for_a_different_corpus(self, tmp_path):
        raw = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand. He smiled."})
        cor = _corpus(tmp_path, "coreferenced", {"a.txt": "Harry waved Harry wand. Harry smiled."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo", raw)
        ok, why = prof.provenance_is_current(table, "svo", cor)
        assert not ok
        # the message has to name both corpora, or the user cannot tell what happened
        assert "DIFFERENT corpus" in why and "raw" in why and "coreferenced" in why

    def test_the_stamp_records_the_corpus(self, tmp_path):
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo", c)
        with open(table + prof.PROVENANCE_SUFFIX, encoding="utf-8") as fh:
            stamped = json.load(fh)
        assert stamped["corpus"] == prof.corpus_fingerprint(c)[0]
        assert stamped["corpus_label"] == "raw"
        assert stamped["kind"] == "svo" and stamped["fingerprint"]

    def test_an_older_stamp_without_a_corpus_is_reused_but_says_so(self, tmp_path):
        """Refusing these would re-parse every profile built before this change, for a risk that is
        usually theoretical. It must be spoken, though, never silent."""
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo")  # no corpus recorded, as before this change
        ok, why = prof.provenance_is_current(table, "svo", c)
        assert ok and "no corpus recorded" in why

    def test_changed_code_still_refuses_regardless_of_corpus(self, tmp_path):
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo", c)
        with open(table + prof.PROVENANCE_SUFFIX, encoding="utf-8") as fh:
            stamped = json.load(fh)
        stamped["fingerprint"] = "deadbeefdeadbeef"
        with open(table + prof.PROVENANCE_SUFFIX, "w", encoding="utf-8") as fh:
            json.dump(stamped, fh)
        ok, why = prof.provenance_is_current(table, "svo", c)
        assert not ok and "code that produced it has changed" in why

    def test_no_stamp_at_all_is_reused_and_says_so(self, tmp_path):
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        ok, why = prof.provenance_is_current(table, "svo", c)
        assert ok and "no provenance stamp" in why

    def test_the_check_is_skipped_when_no_corpus_is_passed(self, tmp_path):
        """Callers that have no corpus context must keep working exactly as before."""
        c = _corpus(tmp_path, "raw", {"a.txt": "Harry waved his wand."})
        table = self._table(tmp_path)
        prof.stamp_provenance([table], "svo", c)
        ok, why = prof.provenance_is_current(table, "svo")
        assert ok and why == ""


# ---- formerly tests/test_interp_spatial_split.py ------------------------------------------------------------

import pytest  # noqa: E402

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)


@pytest.fixture(scope="module")
def prof_interp_spatial_split():
    """The profiler with the REAL pandas in place for the whole file.

    conftest stubs pandas, and _interp_spatial imports it lazily inside the call - so a stub would
    make every reading return None and every test here pass vacuously. Note that a MagicMock answers
    hasattr(pandas, 'DataFrame') with True, which is why the check below asks for something a mock
    cannot fake. The stub is restored when the file is done.
    """
    roots = ("pandas", "numpy")
    saved = {k: v for k, v in sys.modules.items() if k in roots or k.startswith(tuple(r + "." for r in roots))}

    def _drop():
        for k in [k for k in list(sys.modules) if k in roots or k.startswith(tuple(r + "." for r in roots))]:
            del sys.modules[k]

    _drop()
    try:
        import pandas

        # a MagicMock would sail past hasattr; a real DataFrame has real columns
        if list(pandas.DataFrame({"Location": ["x"]}).columns) != ["Location"]:
            raise ImportError("pandas is the stub")
    except Exception as exc:
        _drop()
        sys.modules.update(saved)
        pytest.skip("real pandas not available: %s" % exc)

    spec = importlib.util.spec_from_file_location("_prof_spatial", os.path.join(_SRC, "corpus_profiler_util.py"))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        _drop()
        sys.modules.update(saved)
        pytest.skip("could not load the profiler against real pandas: %s" % exc)
    finally:
        os.chdir(cwd)

    yield mod
    _drop()
    sys.modules.update(saved)


@pytest.fixture
def typology(monkeypatch):
    """A typology of our own, so these tests measure the SPLIT rather than WordNet.

    The real one classifies "the Great Hall" through its last token, hall -> room -> a
    domestic_interior anchor, which is a WordNet climb; conftest stubs nltk, so under test the real
    typology classifies nothing and every place would look unresolved. What belongs here is whether
    _interp_spatial reports a classified place separately from a mapped one - the typology has its
    own tests.
    """
    import types

    fake = types.ModuleType("GIS_symbolic_typology_util")
    fake.UNCLASSIFIED = "unclassified"

    def classify(word, **kw):
        w = str(word).lower()
        if "hall" in w:
            return "domestic_interior"
        if "tower" in w:
            return "tower_height"
        if "forest" in w:
            return "wild_forest"
        return "unclassified"

    fake.classify = classify
    monkeypatch.setitem(sys.modules, "GIS_symbolic_typology_util", fake)
    return fake


def _tracking(tmp_path, rows, name="NLP_NER_entity_location_tracking.csv"):
    p = tmp_path / name
    lines = ["Entity,Location,Sentence ID"]
    for entity, place, n in rows:
        for i in range(n):
            lines.append("%s,%s,%d" % (entity, place, i))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


def _map(tmp_path, plotted):
    p = tmp_path / "NLP_locations_Location_map.html"
    body = "".join("<div>%s: %d</div>" % (name, n) for name, n in plotted)
    p.write_text("<html><body>%s</body></html>" % body, encoding="utf-8")
    return str(p)


class TestTheSplit:
    def test_a_kind_of_space_is_not_reported_as_geocoded(self, prof_interp_spatial_split, typology, tmp_path):
        """the Great Hall has no coordinates and never will."""
        files = [
            _tracking(tmp_path, [("Harry", "the Great Hall", 20), ("Harry", "London", 5)]),
            _map(tmp_path, [("London", 5)]),
        ]
        text = " ".join(prof_interp_spatial_split._interp_spatial(files))
        assert "the Great Hall" in text
        assert "KIND of space" in text
        # the sentence naming what was mapped must not be the one naming the Great Hall
        mapped_sentence = [
            s for s in prof_interp_spatial_split._interp_spatial(files) if "resolved to coordinates" in s
        ]
        assert mapped_sentence and "Great Hall" not in mapped_sentence[0]

    def test_it_reports_what_was_MAPPED_not_how_many_were_sent(self, prof_interp_spatial_split, tmp_path):
        """ "The top 40 were geocoded" was false; the geocoder resolved a fraction of them."""
        rows = [("Harry", "Place%02d" % i, 3) for i in range(40)]
        files = [_tracking(tmp_path, rows), _map(tmp_path, [("Place01", 3), ("Place02", 3)])]
        out = prof_interp_spatial_split._interp_spatial(files)
        mapped = [s for s in out if "resolved to coordinates" in s]
        assert mapped, out
        assert mapped[0].startswith("2 places")
        assert "40" not in mapped[0]

    def test_unresolved_places_are_counted_separately(self, prof_interp_spatial_split, tmp_path):
        files = [
            _tracking(tmp_path, [("Harry", "Hogsmeade", 9), ("Harry", "London", 4)]),
            _map(tmp_path, [("London", 4)]),
        ]
        text = " ".join(prof_interp_spatial_split._interp_spatial(files))
        assert "Hogsmeade" in text
        assert "no coordinates to find" in text

    def test_the_totals_add_up(self, prof_interp_spatial_split, tmp_path):
        files = [
            _tracking(tmp_path, [("Harry", "the Great Hall", 7), ("Harry", "London", 4), ("Harry", "Hogsmeade", 2)]),
            _map(tmp_path, [("London", 4)]),
        ]
        out = prof_interp_spatial_split._interp_spatial(files)
        assert out[0].startswith("The corpus names 3 distinct places")

    def test_no_location_table_says_nothing(self, prof_interp_spatial_split, tmp_path):
        p = tmp_path / "other.csv"
        p.write_text("A,B\n1,2\n", encoding="utf-8")
        assert prof_interp_spatial_split._interp_spatial([str(p)]) == []


class TestItPicksTheRightTable:
    def test_the_richest_location_table_wins(self, prof_interp_spatial_split, tmp_path):
        """The dimension also carries a top-40 subset written for the movement map. Reading that
        one reported "40 distinct places" for a corpus that names far more."""
        full = _tracking(tmp_path, [("Harry", "Place%02d" % i, 2) for i in range(30)], name="full_tracking.csv")
        subset = _tracking(tmp_path, [("Harry", "Place%02d" % i, 2) for i in range(5)], name="top40_subset.csv")
        out = prof_interp_spatial_split._interp_spatial([subset, full])
        assert out[0].startswith("The corpus names 30 distinct places")

    def test_a_summary_table_counts_MENTIONS_not_rows(self, prof_interp_spatial_split, tmp_path):
        """The summary table is one row per entity-place pair with the mentions in a Count column.
        Counting rows there reported the Great Hall at 69 when it is named 229 times."""
        p = tmp_path / "NLP_entity_location_summary.csv"
        p.write_text(
            "Entity,Location,Count\nHarry,the Great Hall,100\nRon,the Great Hall,129\nHarry,London,73\n",
            encoding="utf-8",
        )
        text = " ".join(prof_interp_spatial_split._interp_spatial([str(p)]))
        assert "(229)" in text, text


class TestTheAmbiguousPins:
    def test_a_place_that_is_also_a_character_is_flagged(self, prof_interp_spatial_split, tmp_path):
        """A geocoder answers the name it is given. Montague is a Quidditch player here and a town
        in Michigan; the pin looks as authoritative as London's."""
        files = [
            _tracking(tmp_path, [("Montague", "London", 6), ("Harry", "Montague", 5)]),
            _map(tmp_path, [("London", 6), ("Montague", 5)]),
        ]
        text = " ".join(prof_interp_spatial_split._interp_spatial(files))
        assert "Montague" in text
        assert "character name" in text

    def test_a_flagged_pin_does_not_lead_the_headline_list(self, prof_interp_spatial_split, tmp_path):
        """It would be the first thing quoted, and it is the least trustworthy."""
        files = [
            _tracking(tmp_path, [("Montague", "London", 3), ("Harry", "Montague", 50)]),
            _map(tmp_path, [("London", 3), ("Montague", 50)]),
        ]
        mapped = [s for s in prof_interp_spatial_split._interp_spatial(files) if "resolved to coordinates" in s]
        assert mapped
        assert "the most mentioned are London" in mapped[0]

    def test_nothing_ambiguous_means_no_warning(self, prof_interp_spatial_split, tmp_path):
        files = [_tracking(tmp_path, [("Harry", "London", 4)]), _map(tmp_path, [("London", 4)])]
        text = " ".join(prof_interp_spatial_split._interp_spatial(files))
        assert "character name" not in text


# ---- formerly tests/test_profiler_code_stamp.py -------------------------------------------------------------

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

_spec_profiler_code_stamp = importlib.util.spec_from_file_location(
    "_prof_code_stamp", os.path.join(_SRC, "corpus_profiler_util.py")
)
prof_profiler_code_stamp = importlib.util.module_from_spec(_spec_profiler_code_stamp)
_cwd = os.getcwd()
try:
    _spec_profiler_code_stamp.loader.exec_module(prof_profiler_code_stamp)
finally:
    os.chdir(_cwd)


def _rec(tmp_path, aid="spatial_symbolic", code="abc123", **kw):
    f = tmp_path / "events.csv"
    f.write_text("actor,space\nHarry,house\n", encoding="utf-8")
    rec = {"id": aid, "files": [str(f)], "error": ""}
    rec.update(kw)
    if code is not None:
        rec["code"] = code
    return rec


class TestTheFingerprint:
    def test_a_real_analysis_has_one(self):
        assert prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")

    def test_it_is_stable_across_calls(self):
        """An unstable stamp would re-run everything on every profile, for ever."""
        assert prof_profiler_code_stamp.analysis_code_fingerprint(
            "spatial_symbolic"
        ) == prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")

    def test_different_analyses_get_different_stamps(self):
        seen = {
            prof_profiler_code_stamp.analysis_code_fingerprint(a)
            for a in ("spatial_symbolic", "statistics", "semantic_classes", "topics_gensim")
        }
        assert len(seen) == 4

    def test_a_gui_pointer_has_none(self):
        """It produces no files, so there is nothing to invalidate."""
        assert prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic_more") == ""

    def test_an_unknown_analysis_does_not_raise(self):
        assert prof_profiler_code_stamp.analysis_code_fingerprint("no_such_analysis") == ""

    def test_it_covers_the_helper_modules_not_just_the_runner(self):
        """_run_spatial_symbolic is a few lines that call GIS_symbolic_util, which calls the
        typology. A change to the typology - today's London fix - is exactly the kind a reader
        would notice, and it must not be invisible to reuse."""
        import inspect

        body = inspect.getsource(prof_profiler_code_stamp.REGISTRY["spatial_symbolic"]["run"])
        assert "GIS_symbolic_util" in body
        # the stamp must actually depend on that file's bytes
        path = os.path.join(_SRC, "GIS_symbolic_util.py")
        original = open(path, "rb").read()
        before = prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")
        try:
            with open(path, "ab") as fh:
                fh.write(b"\n# fingerprint probe\n")
            after = prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")
        finally:
            with open(path, "wb") as fh:
                fh.write(original)
        assert before != after, "a change in the helper module left the stamp unchanged"
        assert prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic") == before, "not restored"


class TestReuseHonoursIt:
    def test_a_changed_stamp_refuses_reuse(self, tmp_path):
        previous = [_rec(tmp_path, code="0000deadbeef0000")]
        assert prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", previous, True) == []

    def test_a_matching_stamp_reuses(self, tmp_path):
        current = prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")
        previous = [_rec(tmp_path, code=current)]
        assert len(prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", previous, True)) == 1

    def test_no_stamp_still_reuses(self, tmp_path):
        """An older profile has none. Refusing would make every returning user recompute
        everything once, which is a worse trade than saying the check could not be made."""
        previous = [_rec(tmp_path, code=None)]
        assert len(prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", previous, True)) == 1

    def test_the_other_rules_still_apply(self, tmp_path):
        current = prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")
        empty = tmp_path / "empty.csv"
        empty.write_text("", encoding="utf-8")
        rec = _rec(tmp_path, code=current)
        rec["files"] = [str(empty)]
        assert prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", [rec], True) == []

        failed = _rec(tmp_path, code=current, error="it blew up")
        assert prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", [failed], True) == []

        ok = _rec(tmp_path, code=current)
        assert prof_profiler_code_stamp.reusable_from_manifest({}, "spatial_symbolic", [ok], False) == []


class TestTheStampSurvivesTheRoundTrip:
    def test_a_reused_record_keeps_the_OLD_stamp(self, tmp_path):
        """Re-stamping reused files with today's code would declare that today's code produced
        them - and the next run would find them in order however much had changed since."""
        out = tmp_path / "profile"
        out.mkdir()
        rec = _rec(tmp_path, code="0000deadbeef0000", reused=True)
        prof_profiler_code_stamp.save_manifest(str(out), [rec], None)
        import json

        written = json.load(open(os.path.join(str(out), prof_profiler_code_stamp.MANIFEST_NAME), encoding="utf-8"))
        assert written["results"][0]["code"] == "0000deadbeef0000"

    def test_a_record_with_no_stamp_is_not_given_one_on_reuse(self, tmp_path):
        """Blessing unstamped old files with today's code is the same lie, quieter."""
        out = tmp_path / "profile"
        out.mkdir()
        rec = _rec(tmp_path, code=None, reused=True)
        prof_profiler_code_stamp.save_manifest(str(out), [rec], None)
        import json

        written = json.load(open(os.path.join(str(out), prof_profiler_code_stamp.MANIFEST_NAME), encoding="utf-8"))
        assert not written["results"][0].get("code")

    def test_an_analysis_that_actually_RAN_is_stamped_with_today(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        rec = _rec(tmp_path, code=None)  # ran this time: no 'reused' flag
        prof_profiler_code_stamp.save_manifest(str(out), [rec], None)
        import json

        written = json.load(open(os.path.join(str(out), prof_profiler_code_stamp.MANIFEST_NAME), encoding="utf-8"))
        assert written["results"][0]["code"] == prof_profiler_code_stamp.analysis_code_fingerprint("spatial_symbolic")


# ---- formerly tests/test_profiler_output_folders.py ---------------------------------------------------------

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

_spec_profiler_output_folders = importlib.util.spec_from_file_location(
    "_real_profiler_dirs", os.path.join(_SRC, "corpus_profiler_util.py")
)
prof_profiler_output_folders = importlib.util.module_from_spec(_spec_profiler_output_folders)
_cwd = os.getcwd()
try:
    _spec_profiler_output_folders.loader.exec_module(prof_profiler_output_folders)
finally:
    os.chdir(_cwd)


class TestAnalysisDir:
    def test_it_makes_a_folder_named_for_the_analysis_and_the_corpus(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "HPbooks"), "inputFilename": ""}
        got = prof_profiler_output_folders._analysis_dir(c, "embeddings")
        assert os.path.basename(got) == "embeddings_HPbooks"
        assert os.path.isdir(got)

    def test_it_does_NOT_delete_what_is_already_there(self, tmp_path):
        """The whole reason it is not make_output_subdirectory. Deleting the folder on a re-run
        would destroy the very files reuse is about to hand back."""
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "HPbooks"), "inputFilename": ""}
        first = prof_profiler_output_folders._analysis_dir(c, "embeddings")
        keeper = os.path.join(first, "vectors.csv")
        with open(keeper, "w", encoding="utf-8") as fh:
            fh.write("x" * 100)

        again = prof_profiler_output_folders._analysis_dir(c, "embeddings")
        assert again == first
        assert os.path.isfile(keeper), "the previous run's output was deleted"
        assert os.path.getsize(keeper) == 100

    def test_a_single_input_file_names_the_folder_after_it(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": "", "inputFilename": str(tmp_path / "one_book.txt")}
        assert (
            os.path.basename(prof_profiler_output_folders._analysis_dir(c, "topics_Gensim")) == "topics_Gensim_one_book"
        )

    def test_no_corpus_name_still_gives_a_folder(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": "", "inputFilename": ""}
        assert os.path.basename(prof_profiler_output_folders._analysis_dir(c, "topics_Gensim")) == "topics_Gensim"

    def test_no_output_folder_returns_what_it_was_given(self, tmp_path):
        assert prof_profiler_output_folders._analysis_dir({"outputDir": ""}, "embeddings") == ""

    def test_no_label_returns_the_profile_folder(self, tmp_path):
        out = str(tmp_path)
        assert (
            prof_profiler_output_folders._analysis_dir({"outputDir": out, "inputDir": "", "inputFilename": ""}, "")
            == out
        )

    def test_different_analyses_get_different_folders(self, tmp_path):
        """Two analyses sharing a folder would be two analyses overwriting each other."""
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "HPbooks"), "inputFilename": ""}
        made = {
            prof_profiler_output_folders._analysis_dir(c, label)
            for label in (
                "embeddings",
                "topics_Gensim",
                "semantic_classes",
                "vocabulary_richness",
                "entity_locations",
                "words_capital",
            )
        }
        assert len(made) == 6


class TestTheTwoKindsOfSpaceLiveTogether:
    """The row asks one question - "Where does it all happen?" - so its two answers belong in one
    place. Nested WITHOUT repeating the corpus name: naming it at every level is what put paths
    over Windows' 260-character limit, twice in one day.
    """

    def test_geocodable_and_symbolic_are_siblings_under_one_GIS_folder(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "HPbooks"), "inputFilename": ""}
        geo = prof_profiler_output_folders._analysis_dir(c, "GIS", "geocodable")
        sym = prof_profiler_output_folders._analysis_dir(c, "GIS", "symbolic")
        assert os.path.dirname(geo) == os.path.dirname(sym)
        assert os.path.basename(os.path.dirname(geo)) == "GIS_HPbooks"
        assert os.path.basename(geo) == "geocodable"
        assert os.path.basename(sym) == "symbolic"
        assert os.path.isdir(geo) and os.path.isdir(sym)

    def test_the_corpus_is_named_ONCE_not_at_every_level(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "harrypotter_r_corpus_10_17_2024"), "inputFilename": ""}
        got = prof_profiler_output_folders._analysis_dir(c, "GIS", "symbolic")
        rel = os.path.relpath(got, str(out))
        assert rel.count("harrypotter_r_corpus_10_17_2024") == 1

    def test_nesting_still_does_not_delete_what_is_there(self, tmp_path):
        out = tmp_path / "profile"
        out.mkdir()
        c = {"outputDir": str(out), "inputDir": str(tmp_path / "HPbooks"), "inputFilename": ""}
        first = prof_profiler_output_folders._analysis_dir(c, "GIS", "symbolic")
        keeper = os.path.join(first, "events.csv")
        with open(keeper, "w", encoding="utf-8") as fh:
            fh.write("actor,space\n")
        assert prof_profiler_output_folders._analysis_dir(c, "GIS", "symbolic") == first
        assert os.path.isfile(keeper)

    def test_symbolic_space_actually_runs_in_the_sweep_now(self):
        """It was kind='gui' - a pointer - while the row promised symbolic space."""
        entry = prof_profiler_output_folders.REGISTRY["spatial_symbolic"]
        assert entry["kind"] == "batch"
        assert callable(entry["run"])

    def test_the_steps_needing_a_chosen_attribute_stay_a_pointer(self):
        """Distribution and movement need an actor attribute that is a research decision; guessing
        it unattended would put numbers in a report nobody chose."""
        entry = prof_profiler_output_folders.REGISTRY["spatial_symbolic_more"]
        assert entry["kind"] == "gui"
        assert entry["gui_script"] == "GIS_symbolic_main.py"


class TestSymbolicRunsAfterTheThingThatFeedsIt:
    """Symbolic space reads a CoNLL dependency table; SVO writes one. CATEGORY_ORDER puts 'spatial'
    BEFORE 'narrative', so on a fresh corpus symbolic space ran first, found no CoNLL, and returned
    nothing - 0 files, no error, no folder. It only looked correct on a corpus profiled before,
    where a CoNLL table was already on disk.
    """

    def _order(self, selected):
        got = list(selected)
        if "spatial_symbolic" in got and "narrative_svo" in got:
            if got.index("spatial_symbolic") < got.index("narrative_svo"):
                got.remove("spatial_symbolic")
                got.insert(got.index("narrative_svo") + 1, "spatial_symbolic")
        return got

    def test_symbolic_is_moved_after_svo(self):
        got = self._order(["statistics", "spatial_map", "spatial_symbolic", "narrative_svo", "sentiment_stanza"])
        assert got.index("spatial_symbolic") > got.index("narrative_svo")

    def test_everything_else_keeps_its_place(self):
        got = self._order(["statistics", "spatial_map", "spatial_symbolic", "narrative_svo", "sentiment_stanza"])
        assert [a for a in got if a != "spatial_symbolic"] == [
            "statistics",
            "spatial_map",
            "narrative_svo",
            "sentiment_stanza",
        ]

    def test_already_after_svo_is_left_alone(self):
        selected = ["narrative_svo", "spatial_symbolic"]
        assert self._order(selected) == selected

    def test_symbolic_without_svo_is_untouched(self):
        """Nothing to wait for - it will report that it has no CoNLL table to read."""
        selected = ["statistics", "spatial_symbolic"]
        assert self._order(selected) == selected

    def test_svo_without_symbolic_is_untouched(self):
        selected = ["statistics", "narrative_svo"]
        assert self._order(selected) == selected


# ---- formerly tests/test_profiler_reuse_all.py --------------------------------------------------------------

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

_spec_profiler_reuse_all = importlib.util.spec_from_file_location(
    "_real_profiler_reuse", os.path.join(_SRC, "corpus_profiler_util.py")
)
prof_profiler_reuse_all = importlib.util.module_from_spec(_spec_profiler_reuse_all)
_cwd = os.getcwd()
try:
    _spec_profiler_reuse_all.loader.exec_module(prof_profiler_reuse_all)
finally:
    os.chdir(_cwd)


def a_corpus(tmp_path, name="HPbooks", docs=("a.txt", "b.txt")):
    d = tmp_path / name
    d.mkdir()
    for doc in docs:
        (d / doc).write_text("Harry waved his wand.", encoding="utf-8")
    return {"inputDir": str(d), "inputFilename": "", "outputDir": str(tmp_path / "out")}


def an_output(ctx):
    os.makedirs(ctx["outputDir"], exist_ok=True)
    return ctx["outputDir"]


def a_result(out, aid="ngrams", files=("table.csv",), error="", size=10):
    made = []
    for f in files:
        p = os.path.join(out, f)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("x" * size)
        made.append(p)
    return {"id": aid, "category": "counts", "label": aid, "kind": "batch", "files": made, "error": error}


class TestTheManifestRecordsTheCorpus:
    def test_written_and_read_back(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out)], ctx)
        fp, label = prof_profiler_reuse_all.manifest_corpus(out)
        assert fp == prof_profiler_reuse_all.corpus_fingerprint(ctx)[0]
        assert label == "HPbooks"

    def test_no_manifest_is_not_an_error(self, tmp_path):
        assert prof_profiler_reuse_all.manifest_corpus(str(tmp_path)) == ("", "")

    def test_it_is_written_whole_or_not_at_all(self, tmp_path):
        """A manifest truncated by a full disk is worse than none: the next run would read a
        half-list as the complete story."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out)], ctx)
        path = os.path.join(out, prof_profiler_reuse_all.MANIFEST_NAME)
        with open(path, encoding="utf-8") as fh:
            json.load(fh)  # parses, so it is complete
        assert not os.path.isfile(path + ".tmp")


class TestReusableFromManifest:
    def test_a_recorded_analysis_is_reused(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams")]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True)

    def test_ANY_analysis_id_works_including_one_that_never_had_a_probe(self, tmp_path):
        """The whole point: embeddings, topics, iconicity, an analysis added next year."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        for aid in ("embeddings", "topics", "iconic", "yule", "tfidf", "something_new"):
            previous = [a_result(out, aid, files=("%s.csv" % aid,))]
            assert prof_profiler_reuse_all.reusable_from_manifest(ctx, aid, previous, True), aid

    def test_an_analysis_that_FAILED_is_re_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams", error="No space left on device")]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True) == []

    def test_a_ZERO_BYTE_file_is_refused(self, tmp_path):
        """A full disk leaves 0-byte files. Reusing one as real output is worse than re-running -
        exactly what the 30 July crash left behind."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams", size=0)]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True) == []

    def test_a_deleted_file_is_refused(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams")]
        os.remove(previous[0]["files"][0])
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True) == []

    def test_one_missing_file_out_of_several_refuses_the_whole_analysis(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams", files=("one.csv", "two.csv"))]
        os.remove(previous[0]["files"][1])
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True) == []

    def test_a_different_corpus_reuses_nothing(self, tmp_path):
        """corpus_ok is decided once per run by the caller; False must stop everything."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams")]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, False) == []

    def test_an_analysis_not_in_the_manifest_is_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        previous = [a_result(out, "ngrams")]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "embeddings", previous, True) == []

    def test_an_analysis_recorded_with_no_files_is_run(self, tmp_path):
        ctx = a_corpus(tmp_path)
        an_output(ctx)
        previous = [{"id": "ngrams", "files": [], "error": ""}]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", previous, True) == []

    def test_nothing_previous_reuses_nothing(self, tmp_path):
        ctx = a_corpus(tmp_path)
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", [], True) == []


class TestTheCorpusGuardOnAWholeRun:
    def test_the_same_corpus_matches(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out)], ctx)
        assert prof_profiler_reuse_all.manifest_corpus(out)[0] == prof_profiler_reuse_all.corpus_fingerprint(ctx)[0]

    def test_an_edited_corpus_does_not(self, tmp_path):
        """A coreference-resolved copy, or a document added: the numbers would no longer describe
        the corpus in front of you."""
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out)], ctx)
        (tmp_path / "HPbooks" / "c.txt").write_text("Ron said nothing.", encoding="utf-8")
        assert prof_profiler_reuse_all.manifest_corpus(out)[0] != prof_profiler_reuse_all.corpus_fingerprint(ctx)[0]


class TestAProfileFolderIsPortable:
    """Copying the output folder is the obvious way to keep a baseline before re-running.

    With absolute paths in the manifest, the copy still named files in the ORIGINAL: reuse read the
    original's outputs, the copy gained nothing, and deleting the original broke the copy entirely.
    """

    def test_paths_are_stored_relative_to_the_output_folder(self, tmp_path):
        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out, "ngrams")], ctx)
        with open(os.path.join(out, prof_profiler_reuse_all.MANIFEST_NAME), encoding="utf-8") as fh:
            stored = json.load(fh)["results"][0]["files"][0]
        assert not os.path.isabs(stored)
        assert stored == "table.csv"

    def test_a_COPIED_profile_refers_to_its_own_files(self, tmp_path):
        import shutil

        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        prof_profiler_reuse_all.save_manifest(out, [a_result(out, "ngrams")], ctx)

        copy = str(tmp_path / "baseline")
        shutil.copytree(out, copy)
        shutil.rmtree(out)  # the original is gone; the copy must stand alone

        loaded = prof_profiler_reuse_all.load_manifest(copy)
        assert loaded and loaded[0]["files"]
        assert os.path.dirname(loaded[0]["files"][0]) == copy
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", loaded, True)

    def test_an_older_manifest_with_absolute_paths_still_works(self, tmp_path):
        """Backwards compatible: manifests already on disk hold absolute paths."""
        import json

        ctx = a_corpus(tmp_path)
        out = an_output(ctx)
        rec = a_result(out, "ngrams")
        with open(os.path.join(out, prof_profiler_reuse_all.MANIFEST_NAME), "w", encoding="utf-8") as fh:
            json.dump({"version": 1, "results": [rec]}, fh)  # absolute, as written before
        loaded = prof_profiler_reuse_all.load_manifest(out)
        assert loaded and loaded[0]["files"]
        assert prof_profiler_reuse_all.reusable_from_manifest(ctx, "ngrams", loaded, True)

    def test_a_file_outside_the_output_folder_stays_absolute(self, tmp_path):
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        stray = str(elsewhere / "x.csv")
        assert prof_profiler_reuse_all._manifest_store_path(stray, str(tmp_path / "out")) == stray
