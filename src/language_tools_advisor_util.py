# Language -> available tools advisor.
#
# "What can I actually run on my corpus language?" Given the corpus language (the one set in the NLP
# Suite setup config), produce a self-contained HTML report of which NLP Suite capabilities can run on
# that language. Availability is DERIVED from the parser packages' own language lists -- not guessed --
# wherever a live list exists:
#   * Stanford CoreNLP : the setup's fixed parser-language list + CoreNLP's NER language set.
#   * Stanza / spaCy   : their list_all_languages(); Stanza per-capability lists available_ud
#                        (dependency parse), available_NER, available_sentiment (language CODES).
# English-only tools (WordNet/VerbNet/FrameNet aggregation, SRL, nominalization, concreteness, iconic
# language, and the English style dictionaries) are flagged as such. Language-INDEPENDENT tools (counts,
# n-grams, word frequency, TF-IDF, vocabulary richness / lexical diversity, topic modeling, word clouds,
# statistics, document similarity) always run.
#
# The report is a static HTML file opened in the browser; nothing here needs Java or a network.

import html as _html
import os
import webbrowser

import constants_util
import NLP_package_languages_util

# CoreNLP parser languages -- keep in sync with NLP_setup_package_language_main.get_available_languages()
_CORENLP_LANGUAGES = ["Arabic", "Chinese", "English", "German", "Hungarian", "Italian", "Spanish"]


def _name_to_code():
    # constants_util.languages is a list of (code, name); build name(lower) -> code
    out = {}
    for code, name in constants_util.languages:
        out.setdefault(str(name).lower(), str(code))
    return out


def _stanza_languages():
    """(Stanza's language names, problem): the problem says why the list could not be read, or is ''.

    The list is in Stanza's resources.json, which only Stanza knows where to find; the menu runs this module
    in the bundled python-env for that (issue #1731). It used to be read inside the frozen menu, which has no
    Stanza, and the error was swallowed: every language came out as unsupported."""
    try:
        import IO_internet_util

        names, _codes = IO_internet_util.stanza_languages()
    except Exception as e:
        return [], "Stanza could not be loaded (" + type(e).__name__ + ": " + str(e) + ")"
    if not names:
        return [], "Stanza's list of languages could not be downloaded (check the internet connection)"
    return NLP_package_languages_util.stanza_display_names(names.values()), ""


def _spacy_languages():
    return NLP_package_languages_util.spacy_language_names()


def _stanza_has(code, attr):
    """Is `code` in Stanza's <attr> list (available_ud / available_NER / available_sentiment)?"""
    return code in getattr(NLP_package_languages_util, attr)


def assess_language(language):
    """Return an ordered list of (section, [(capability, available_bool, note)]) for `language`."""
    lang = str(language or "").strip()
    code = _name_to_code().get(lang.lower(), "")
    stanza_langs, stanza_problem = _stanza_languages()
    spacy_langs = _spacy_languages()

    # per-capability Stanza support (by code); spaCy ships parser + NER for its listed languages
    st_ud = _stanza_has(code, "available_ud")
    st_ner = _stanza_has(code, "available_NER")
    st_senti = _stanza_has(code, "available_sentiment")

    in_corenlp = lang in _CORENLP_LANGUAGES
    # without Stanza's own list, a language with a Stanza parser, NER or sentiment model is still a Stanza language
    in_stanza = lang in stanza_langs or st_ud or st_ner or st_senti
    in_spacy = lang in spacy_langs
    is_english = lang.lower() == "english"
    # coreference_main: CoreNLP resolves English and Chinese; Stanza and BERT (fastcoref) English only
    coref_corenlp = in_corenlp and lang.lower() in ("english", "chinese")

    def _pkgs(*flags_names):
        got = [n for f, n in flags_names if f]
        return ("via " + ", ".join(got)) if got else ""

    any_parser = in_corenlp or in_stanza or in_spacy
    can_depparse = st_ud or in_spacy or in_corenlp  # SVO rides the dependency parse
    can_ner = st_ner or in_spacy or (in_corenlp and lang in _CORENLP_LANGUAGES)
    can_sentiment = st_senti or is_english  # Stanza sentiment, else English VADER/etc.

    sections = []

    # 1. Always-on (language independent -- counting / frequency / bag-of-words / corpus-trained
    #    embeddings / geometry / visualization / data & file tools)
    sections.append(
        (
            "Always available — language-independent (counting, frequency, topics, maps, viz, data)",
            [
                ("Corpus / document statistics — documents, words, sentences, syllables, lines", True, ""),
                ("N-grams (word & character) & co-occurrences (+ viewers, n-gram search)", True, ""),
                ("Word / collocation search, CoNLL-table search", True, ""),
                ("Word frequency (Zipf), TF-IDF distinctive words", True, ""),
                ("Vocabulary richness (TTR / Yule’s K), lexical diversity (MTLD / vocd-D)", True, ""),
                (
                    "Topic modeling — Gensim LDA, MALLET, BERTopic",
                    True,
                    "bag-of-words; results improve with language-specific stopwords",
                ),
                ("Word embeddings — Word2Vec / Gensim trained on YOUR corpus", True, "learns from the corpus itself"),
                ("Word clouds", True, ""),
                ("Document similarity / plagiarism (TF-IDF + cosine); word similarity (Levenshtein)", True, ""),
                ("Language detection", True, "identifies the language of each document"),
                (
                    "GIS — maps (Google Earth / Maps), geographic distances, symbolic space",
                    True,
                    "mapping is language-independent; extracting place names from text needs NER (below)",
                ),
                (
                    "Charts & network graphs — Excel, Plotly (Sankey / sunburst / treemap / boxplot / …), Gephi",
                    True,
                    "",
                ),
                ("Statistical measures & hypothesis tests (csv)", True, ""),
                (
                    "Data & file tools — PC-ACE & SQL databases, file check / clean / convert / split / merge / search",
                    True,
                    "",
                ),
            ],
        )
    )

    # 2. Parsing & annotation (depends on package support for THIS language)
    sections.append(
        (
            "Parsing & annotation — needs a package that supports %s" % (lang or "your language"),
            [
                (
                    "Parsers & annotators — tokenize, lemma, POS tagging",
                    any_parser,
                    _pkgs((in_corenlp, "CoreNLP"), (in_stanza, "Stanza"), (in_spacy, "spaCy")),
                ),
                (
                    "POS-based statistics — noun / verb / adjective / pronoun counts",
                    any_parser,
                    _pkgs((in_corenlp, "CoreNLP"), (in_stanza, "Stanza"), (in_spacy, "spaCy")),
                ),
                (
                    "Dependency parse & SVO (Subject-Verb-Object) + dependency-tree viewer",
                    can_depparse,
                    _pkgs((st_ud, "Stanza"), (in_spacy, "spaCy"), (in_corenlp, "CoreNLP")),
                ),
                (
                    "CoNLL-table analysis — clause / noun / verb / function-word frequencies",
                    can_depparse,
                    "reads the parsed CoNLL table",
                ),
                ("Sentence complexity", can_depparse, "needs a dependency parse"),
                (
                    "Named-Entity Recognition (people / organizations / locations)",
                    can_ner,
                    _pkgs((st_ner, "Stanza"), (in_spacy, "spaCy"), (in_corenlp, "CoreNLP")),
                ),
                (
                    "Coreference resolution (pronominal)",
                    coref_corenlp or is_english,
                    _pkgs((coref_corenlp, "CoreNLP"), (is_english, "Stanza"), (is_english, "BERT (fastcoref)")),
                ),
                (
                    "Sentiment analysis + Shape of Stories (sentiment arc)",
                    can_sentiment,
                    _pkgs(
                        (st_senti, "Stanza"),
                        (is_english, "English dictionaries (VADER / ANEW / SentiWordNet / hedonometer)"),
                    ),
                ),
            ],
        )
    )

    # 3. Stanford CoreNLP-only capabilities (need CoreNLP + a CoreNLP-supported language)
    sections.append(
        (
            "Stanford CoreNLP-only — needs CoreNLP + Java, and a CoreNLP language",
            [
                (
                    "Gender annotation (CoreNLP + dictionaries)",
                    in_corenlp,
                    "" if in_corenlp else "CoreNLP does not cover %s" % lang,
                ),
                ("Dialogue / quote extraction (speaker attribution)", in_corenlp, ""),
                ("Normalized dates & time expressions", in_corenlp, ""),
            ],
        )
    )

    # 4. English (as shipped): the models / dictionaries / endpoints are English. Some (BERT, DBpedia
    #    Spotlight, the spell checker) have multilingual variants, but the Suite ships the English ones.
    sections.append(
        (
            "English tools (as shipped) — English models / dictionaries / endpoints",
            [
                ("Semantic analysis & aggregation — WordNet / VerbNet / FrameNet classes", is_english, ""),
                ("Word-sense disambiguation (WSD) & semantic similarity (WordNet)", is_english, ""),
                ("Semantic Role Labeling (SRL, transformer)", is_english, ""),
                ("Nominalization analysis", is_english, ""),
                ("Concreteness / abstractness, iconic language", is_english, ""),
                ("Style analysis & dictionaries — objectivity/subjectivity, pathos, ANEW, hedonometer", is_english, ""),
                ("Readability (textstat)", is_english, "formulas are English-calibrated"),
                ("Hedge / uncertainty annotation", is_english, ""),
                ("Spelling checker", is_english, "English + a few European languages (pyspellchecker)"),
                ("Gender guesser (who wrote it — man or woman?)", is_english, "name-based; Western names"),
                (
                    "BERT — word-embedding semantic map, BERT NER, BERT sentiment",
                    is_english,
                    "English models shipped (all-distilroberta); multilingual BERT (102 languages) exists",
                ),
                (
                    "DBpedia & YAGO entity linking / knowledge graphs; HTML annotator",
                    is_english,
                    "uses the English DBpedia Spotlight endpoint (/en/) as shipped",
                ),
            ],
        )
    )

    return sections, dict(
        code=code, in_corenlp=in_corenlp, in_stanza=in_stanza, in_spacy=in_spacy, stanza_problem=stanza_problem
    )


def _row(cap, ok, note):
    mark = "✓" if ok else "✗"
    cls = "yes" if ok else "no"
    note_html = ('<span class="note">%s</span>' % _html.escape(note)) if note else ""
    return '<tr class="%s"><td class="mark">%s</td><td>%s %s</td></tr>' % (cls, mark, _html.escape(cap), note_html)


def build_report(language, outputDir):
    """Write the HTML advisor report for `language` into outputDir; return the file path."""
    sections, info = assess_language(language)
    lang_disp = _html.escape(str(language or "(not set)"))
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>NLP Suite — tools available for %s</title>" % lang_disp,
        "<style>",
        "body{font-family:-apple-system,Segoe UI,Roboto,Georgia,serif;max-width:900px;margin:2em auto;"
        "padding:0 1.2em;color:#222;line-height:1.5;}",
        "h1{font-size:1.5em;} h2{font-size:1.05em;margin-top:1.6em;border-bottom:1px solid #ddd;padding-bottom:.3em;}",
        ".lang{color:#c1121f;font-weight:700;}",
        "table{border-collapse:collapse;width:100%;margin:.4em 0 1em;}",
        "td{padding:.3em .5em;vertical-align:top;border-bottom:1px solid #f0f0f0;}",
        "td.mark{width:1.4em;text-align:center;font-weight:700;}",
        "tr.yes td.mark{color:#178a3f;} tr.no td.mark{color:#c1121f;}",
        "tr.no td{color:#888;}",
        ".note{color:#888;font-size:.9em;font-style:italic;}",
        ".foot{margin-top:2em;color:#666;font-size:.9em;}",
        "</style></head><body>",
        "<h1>What can I run on a <span class='lang'>%s</span> corpus?</h1>" % lang_disp,
        "<p>Availability below is derived from each NLP package’s own language coverage "
        "(Stanford CoreNLP, Stanza, spaCy). Change your corpus language in "
        "the NLP Suite menu: <b>Set up</b> next to <b>Parser &amp; language</b>.</p>",
    ]
    if info["stanza_problem"]:
        parts.append(
            "<p class='note'>%s. Stanza is shown only for its parser, NER and sentiment models, which the NLP "
            "Suite lists itself; open this report again once Stanza's list is available.</p>"
            % _html.escape(info["stanza_problem"])
        )
    for title, rows in sections:
        parts.append("<h2>%s</h2><table>" % _html.escape(title))
        parts.extend(_row(c, ok, note) for c, ok, note in rows)
        parts.append("</table>")
    parts.append(
        "<p class='foot'>✓ = available for %s · ✗ = not available for this language. "
        "This is a guide to language coverage; a few tools may still need their model or "
        "dictionary downloaded (Setup ▸ Download / install external software).</p>" % lang_disp
    )
    parts.append("</body></html>")

    os.makedirs(outputDir, exist_ok=True)
    path = os.path.join(
        outputDir,
        "NLP_tools_available_for_%s.html" % "".join(ch if ch.isalnum() else "_" for ch in str(language or "language")),
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return path


def run(outputDir="", language=""):
    """Entry point for the menu button. Uses the CONFIGURED corpus language unless one is passed;
    writes the HTML report and opens it in the browser. Returns the report path (or '')."""
    if not language:
        try:
            import config_util

            cfg = config_util.read_NLP_package_language_config()
            language = cfg[4]  # (error, package, parsers, basics_package, language, ...)
        except Exception:
            language = ""
    if not outputDir:
        try:
            import GUI_IO_util

            outputDir = GUI_IO_util.outputDirPath if hasattr(GUI_IO_util, "outputDirPath") else os.getcwd()
        except Exception:
            outputDir = os.getcwd()
    try:
        path = build_report(language, outputDir)
    except Exception as e:
        _error("The report of the tools available for your language could not be written.\n\n" + _detail(e))
        return ""
    url = "file:///" + os.path.abspath(path).replace("\\", "/")
    try:
        opened = webbrowser.open(url)
    except Exception:  # reported just below, with the file to open by hand
        opened = False
    if not opened:
        _error("The report was written, but no web browser could be opened. Open this file yourself:\n\n" + path)
    return path


def _detail(e):
    return type(e).__name__ + ": " + str(e)


def _error(message):
    import tkinter.messagebox as mb

    mb.showerror(title="Which tools work with my corpus language?", message=message)


if __name__ == "__main__":
    # The menu runs this in the bundled python-env (run_script_util.run_script_detached), where Stanza loads
    # (issue #1731). Argument: the output folder.
    import sys

    run(outputDir=sys.argv[1] if len(sys.argv) > 1 else "")
