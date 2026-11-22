"""Issue #1731: the menu's "Which tools work with my corpus language?" said Stanza supports no language.

It ran inside the frozen menu, which has no Stanza, imported Stanza_util anyway and swallowed the error.
"""

import ast
import os
import sys
import types

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))

import language_tools_advisor_util as advisor  # noqa: E402
import NLP_package_languages_util as langs  # noqa: E402


def _tree(name):
    with open(os.path.join(_ROOT, "src", name), encoding="utf-8") as f:
        return ast.parse(f.read())


def _imports(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


class TestLanguageLists:
    def test_the_lists_module_loads_no_package(self):
        assert _imports(_tree("NLP_package_languages_util.py")) <= {"constants_util"}

    def test_the_advisor_does_not_import_the_package_utils(self):
        # Stanza_util and spaCy_util import GUI_util (a Tk window) and the packages themselves
        assert not _imports(_tree("language_tools_advisor_util.py")) & {"Stanza_util", "spaCy_util", "GUI_util"}

    def test_stanza_util_and_spacy_util_still_have_their_lists(self):
        for module, names in (
            ("Stanza_util.py", {"available_ud", "available_NER", "available_sentiment"}),
            ("spaCy_util.py", {"spacy_available_lang"}),
        ):
            found = set()
            for node in _tree(module).body:
                if isinstance(node, ast.ImportFrom) and node.module == "NLP_package_languages_util":
                    found.update(a.name for a in node.names)
            assert names <= found, module

    def test_stanza_names_sort_variants_together_and_drop_traditional_chinese(self):
        names = ["Simplified_Chinese", "Traditional_Chinese", "English", "Ancient_Greek", "Greek"]
        assert langs.stanza_display_names(names) == ["Chinese_Simplified", "English", "Greek", "Greek_Ancient"]

    def test_spacy_names(self):
        names = langs.spacy_language_names()
        assert "English" in names and names == sorted(names)

    def test_the_lists_are_language_codes(self):
        assert "en" in langs.available_ud and "en" in langs.available_NER and "en" in langs.available_sentiment
        assert "en" in langs.spacy_available_lang


class TestWithoutStanzasList:
    def test_a_stanza_language_is_still_one_from_the_nlp_suites_own_lists(self, monkeypatch):
        monkeypatch.setattr(advisor, "_stanza_languages", lambda: ([], "Stanza could not be loaded"))
        sections, info = advisor.assess_language("Italian")
        assert info["in_stanza"] is True and info["stanza_problem"] == "Stanza could not be loaded"

    def test_the_report_says_the_list_was_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(advisor, "_stanza_languages", lambda: ([], "Stanza could not be loaded"))
        with open(advisor.build_report("Italian", str(tmp_path)), encoding="utf-8") as f:
            assert "Stanza could not be loaded" in f.read()

    def test_no_note_when_the_list_was_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(advisor, "_stanza_languages", lambda: (["English", "Italian"], ""))
        with open(advisor.build_report("Italian", str(tmp_path)), encoding="utf-8") as f:
            assert "could not" not in f.read()

    def test_stanza_that_cannot_load_is_a_problem_not_an_exception(self, monkeypatch):
        def boom(*a, **k):
            raise ModuleNotFoundError("No module named 'torch'")

        monkeypatch.setitem(sys.modules, "IO_internet_util", types.SimpleNamespace(stanza_languages=boom))
        names, problem = advisor._stanza_languages()
        assert names == [] and "torch" in problem

    def test_stanza_names_from_resources_json(self, monkeypatch):
        fake = types.SimpleNamespace(stanza_languages=lambda: ({"en": "English", "zh-hans": "Simplified_Chinese"}, {}))
        monkeypatch.setitem(sys.modules, "IO_internet_util", fake)
        assert advisor._stanza_languages() == (["Chinese_Simplified", "English"], "")


class TestRunReportsProblems:
    def test_a_report_that_cannot_be_written_is_shown(self, tmp_path, monkeypatch):
        shown = []
        monkeypatch.setattr(advisor, "_error", shown.append)
        monkeypatch.setattr(advisor, "build_report", lambda *a: (_ for _ in ()).throw(OSError("disk full")))
        assert advisor.run(outputDir=str(tmp_path), language="English") == ""
        assert shown and "disk full" in shown[0]

    def test_no_browser_is_shown_with_the_file_to_open(self, tmp_path, monkeypatch):
        shown = []
        monkeypatch.setattr(advisor, "_error", shown.append)
        monkeypatch.setattr(advisor, "_stanza_languages", lambda: (["English"], ""))
        monkeypatch.setattr(advisor.webbrowser, "open", lambda url: False)
        path = advisor.run(outputDir=str(tmp_path), language="English")
        assert os.path.isfile(path) and shown and path in shown[0]


class TestMenuRunsTheAdvisorOutsideTheFrozenMenu:
    def test_the_menu_launches_it_in_python_env(self):
        tree = _tree("NLP_menu_main.py")
        assert "language_tools_advisor_util" not in _imports(tree)
        calls = [
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and getattr(n.func, "attr", "") == "run_script_detached"
            and n.args
            and getattr(n.args[0], "value", "") == "language_tools_advisor_util.py"
        ]
        assert len(calls) == 1


class TestCoreference:
    """Coreference is not CoreNLP-only: Stanza and BERT (fastcoref) resolve it for English; CoreNLP for English and
    Chinese (coreference_main), not for every CoreNLP parser language."""

    @staticmethod
    def _row(language, monkeypatch):
        monkeypatch.setattr(advisor, "_stanza_languages", lambda: ([], ""))
        sections, _ = advisor.assess_language(language)
        for title, rows in sections:
            for cap, ok, note in rows:
                if cap.startswith("Coreference"):
                    return title, ok, note
        raise AssertionError("no coreference row")

    def test_not_in_the_corenlp_only_section(self, monkeypatch):
        title, _, _ = self._row("English", monkeypatch)
        assert "CoreNLP-only" not in title

    def test_english_and_chinese_yes_italian_no(self, monkeypatch):
        assert self._row("English", monkeypatch)[1]
        assert self._row("Chinese", monkeypatch)[1]
        assert not self._row("Italian", monkeypatch)[1]

    def test_english_names_the_three_packages(self, monkeypatch):
        note = self._row("English", monkeypatch)[2]
        assert "Stanza" in note and "BERT" in note and "CoreNLP" in note
