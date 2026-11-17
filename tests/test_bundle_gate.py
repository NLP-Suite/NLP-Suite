"""Tests for the pure parts of tests/bundle_gate.py: the import scan and the snapshot comparison."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bundle_gate as gate  # noqa: E402

STDLIB = {"os", "sys", "json", "tkinter"}


class TestImportedModules:
    def test_imports_inside_functions_count(self):
        src = "import os\ndef run():\n    import stanza\n    from transformers.pipelines import pipeline\n"
        assert gate.imported_modules(src) == {"os", "stanza", "transformers"}

    def test_relative_imports_are_not_modules(self):
        assert gate.imported_modules("from . import x\nfrom .y import z\n") == set()

    def test_dotted_names_keep_the_top_level(self):
        assert gate.imported_modules("import PIL.Image\nfrom tkinter import messagebox\n") == {"PIL", "tkinter"}


class TestThirdParty:
    def test_local_and_stdlib_modules_are_left_out(self):
        graph = {"a_util": {"os", "b_util", "pandas"}, "b_util": {"pandas", "stanza"}}
        assert gate.third_party(graph, STDLIB) == {"pandas": ["a_util", "b_util"], "stanza": ["b_util"]}

    def test_a_file_that_does_not_parse_is_skipped(self):
        assert gate.third_party({"broken": None, "ok": {"numpy"}}, STDLIB) == {"numpy": ["ok"]}


class TestReachable:
    def test_the_chain_names_how_the_menu_gets_there(self):
        graph = {
            "NLP_menu_main": {"GUI_util", "os"},
            "GUI_util": {"IO_util", "PIL"},
            "IO_util": {"stanza"},
            "unrelated_util": {"torch"},
        }
        found = gate.reachable_third_party(graph, "NLP_menu_main", STDLIB)
        assert found == {
            "PIL": ["NLP_menu_main", "GUI_util", "PIL"],
            "stanza": ["NLP_menu_main", "GUI_util", "IO_util", "stanza"],
        }

    def test_import_cycles_end(self):
        graph = {"NLP_menu_main": {"a"}, "a": {"b"}, "b": {"a", "pandas"}}
        assert set(gate.reachable_third_party(graph, "NLP_menu_main", STDLIB)) == {"pandas"}


def _snap(imports=None, guis=None, menu=None):
    return {"version": "x", "imports": imports or {}, "guis": guis or {}, "menu": menu or {"runs": True}}


def _imp(ok, used_by=("a_util",)):
    return {"ok": ok, "error": "" if ok else "ModuleNotFoundError: gone", "used_by": list(used_by)}


def _gui(status="ok", popups=(), modules=()):
    return {
        "status": status,
        "error": "" if status == "ok" else "boom",
        "popups": [list(p) for p in popups],
        "modules": list(modules),
    }


class TestCompare:
    def test_identical_snapshots_pass(self):
        snap = _snap({"pandas": _imp(True)}, {"x_main.py": _gui()})
        assert gate.compare(snap, snap)[0] == []

    def test_a_lost_package_fails(self):
        fails, _ = gate.compare(_snap({"wordcloud": _imp(True)}), _snap({"wordcloud": _imp(False)}))
        assert len(fails) == 1 and "wordcloud" in fails[0]

    def test_a_package_that_never_imported_is_not_a_regression(self):
        # e.g. a Windows-only module on a Mac build: it fails in both
        assert gate.compare(_snap({"win32com": _imp(False)}), _snap({"win32com": _imp(False)}))[0] == []

    def test_a_newly_imported_package_that_fails_is_caught(self):
        fails, _ = gate.compare(_snap(), _snap({"requests_cache": _imp(False)}))
        assert len(fails) == 1 and "newly imported" in fails[0]

    def test_a_gui_that_stops_building_fails(self):
        fails, _ = gate.compare(_snap(guis={"x_main.py": _gui()}), _snap(guis={"x_main.py": _gui("crash")}))
        assert len(fails) == 1 and "x_main.py" in fails[0]

    def test_a_new_error_popup_at_opening_fails(self):
        base = _snap(guis={"x_main.py": _gui(popups=[("showinfo", "Welcome", "")])})
        cand = _snap(
            guis={"x_main.py": _gui(popups=[("showinfo", "Welcome", ""), ("showerror", "Missing module", "")])}
        )
        fails, _ = gate.compare(base, cand)
        assert fails == ["GUI x_main.py: a new showerror popup at opening: 'Missing module'"]

    def test_a_menu_that_stops_running_fails(self):
        fails, _ = gate.compare(_snap(menu={"runs": True}), _snap(menu={"runs": False, "error": "exit 1"}))
        assert len(fails) == 1 and "frozen menu" in fails[0]

    def test_a_module_newly_missing_from_the_menu_is_for_review_not_a_failure(self):
        cand = _snap(menu={"runs": True, "missing_from_archive": {"stanza": ["NLP_menu_main", "IO_util", "stanza"]}})
        fails, notes = gate.compare(_snap(), cand)
        assert fails == [] and any("REVIEW" in n and "IO_util -> stanza" in n for n in notes)
