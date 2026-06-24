# SRL worker - runs INSIDE the isolated Python 3.8 env (srl_test38), NOT the NLP Suite's 3.10 env.
# It is invoked as a subprocess by SRL_util.py. Reads txt input (a file or a directory of .txt),
# runs Riccorl/transformer-srl, and writes one CSV row per (sentence, predicate) with PropBank roles
# mapped to plain-language columns. Keep dependencies to what the srl_test38 env provides.
#
# Usage:  python SRL_worker.py <input_file_or_dir> <output_csv> [model_path]

import sys
import os
import csv
import glob
import html
import re
import urllib.parse

# NOTE: transformer_srl is imported LAZILY inside main() (not at module top), so this script stays
# importable under the Suite's Python 3.10 bundle (e.g. a PyInstaller import audit). transformer_srl
# only loads when the worker is actually RUN as a subprocess in the isolated Python 3.8 SRL env.

# Fallback only; SRL_util passes the resolved model path as argv[3]. Default to <NLP-Suite>/lib/SRL/.
DEFAULT_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "lib", "SRL", "srl_bert_base_conll2012.tar.gz")

# Columns: PropBank label -> human-readable header
ROLE_COLUMNS = [
    ("ARG0", "ARG0 (Agent)"),
    ("ARG1", "ARG1 (Patient)"),
    ("ARG2", "ARG2 (Recipient/Beneficiary)"),
    ("ARGM-LOC", "Where (ARGM-LOC)"),
    ("ARGM-TMP", "When (ARGM-TMP)"),
    ("ARGM-MNR", "How (ARGM-MNR)"),
    ("ARGM-CAU", "Why (ARGM-CAU)"),
]
HEADERS = ["Document", "Date", "Sentence ID", "Sentence", "Predicate", "Frame", "VerbNet class"] + \
          [h for _, h in ROLE_COLUMNS] + ["Refined roles", "Description"]

# --- Heuristic refined-role enrichment (PropBank numbered args -> fairly-accurate thematic-role
# names, alongside the ARG columns). Not a substitute for VerbNet/VerbAtlas, but reliable for
# preposition-marked roles (Recipient/Beneficiary/Source/Instrument/Location) and experiencer-subject
# verbs. ARG0->Agent (Experiencer for psych/perception verbs); ARG1->Patient/Theme. ---
PSYCH_VERBS = {
    "see", "hear", "feel", "smell", "taste", "notice", "perceive", "sense", "observe", "watch",
    "fear", "love", "hate", "like", "dislike", "want", "wish", "need", "know", "believe", "think",
    "understand", "realize", "remember", "forget", "recognize", "doubt", "suspect", "enjoy",
    "prefer", "admire", "envy", "pity", "regret", "miss", "appreciate", "dread", "hope", "expect",
    "imagine", "suppose", "consider", "trust", "value", "resent", "adore", "loathe", "crave",
}
PREP_ROLE = {
    "to": "Recipient", "for": "Beneficiary", "from": "Source", "with": "Instrument",
    "as": "Attribute", "into": "Goal", "onto": "Goal", "toward": "Goal", "towards": "Goal",
    "in": "Location", "at": "Location", "on": "Location", "over": "Location", "under": "Location",
    "near": "Location", "inside": "Location", "outside": "Location",
}
ARGM_ROLE = {
    "ARGM-LOC": "Location", "ARGM-TMP": "Time", "ARGM-MNR": "Manner", "ARGM-CAU": "Cause",
    "ARGM-DIR": "Direction", "ARGM-GOL": "Goal", "ARGM-PRP": "Purpose", "ARGM-EXT": "Extent",
}
REFINED_ORDER = ["ARG0", "ARG1", "ARG2", "ARG3", "ARG4",
                 "ARGM-LOC", "ARGM-TMP", "ARGM-MNR", "ARGM-CAU"]


def load_semlink_map(path):
    """Load SemLink pb-vn2.json - {sense: {vn_class: {ARG0:'agent', ARG1:'theme', ...}}} - into
    role_map {(sense,'ARG0'):'Agent'} (the per-frame PropBank->VerbNet thematic role) AND
    class_map {sense: vn_class} (the DISAMBIGUATED VerbNet class id for the predicate's sense, e.g.
    '42.1'). Returns ({}, {}) if the file is absent/unparseable, so SRL falls back to the heuristic."""
    role_map, class_map = {}, {}
    if not path or not os.path.exists(path):
        return role_map, class_map
    try:
        import json
        data = json.load(open(path, encoding="utf-8"))
        for sense, classes in data.items():
            for vn_class, argmap in classes.items():     # take the first VerbNet class for this sense
                class_map[sense] = vn_class
                for arg, role in argmap.items():
                    if role:
                        role_map[(sense, arg.upper())] = str(role).replace("_", " ").title()
                break
    except Exception as e:
        sys.stderr.write("Could not parse SemLink map %s: %s\n" % (path, e))
        return {}, {}
    sys.stderr.write("Loaded %d SemLink role mappings from %s\n" % (len(role_map), path))
    return role_map, class_map


def _mapped_role(role_map, sense, label):
    """VerbNet thematic role for a PropBank (sense, label), or None if not mapped."""
    if not role_map or not sense:
        return None
    return role_map.get((sense, label.upper()))


def refine_role(label, text, predicate_lemma, sense=None, role_map=None):
    """The principled SemLink/VerbNet role for (sense, label) when available, KEPT ALONGSIDE the
    preposition cue on oblique args when the two differ (e.g. 'Destination / Source' for a 'from'
    phrase). Falls back to a heuristic (preposition + psych-verb list) when SemLink has no mapping."""
    mapped = _mapped_role(role_map, sense, label)
    prep_role = None
    if label in ("ARG2", "ARG3", "ARG4") and text.strip():
        prep_role = PREP_ROLE.get(text.strip().split()[0].lower())
    if mapped:
        if prep_role and prep_role.lower() != mapped.lower():
            return "%s / %s" % (mapped, prep_role)   # both: VerbNet frame role + preposition cue
        return mapped
    if label == "ARG0":
        return "Experiencer" if predicate_lemma in PSYCH_VERBS else "Agent"
    if label == "ARG1":
        return "Patient/Theme"
    if label in ("ARG2", "ARG3", "ARG4"):
        return prep_role or ("Arg" + label[-1])
    return ARGM_ROLE.get(label, label)


def roles_from_tags(words, tags):
    """Reconstruct {role: 'text span'} from BIO tags (B-ARG0, I-ARG0, O, ...)."""
    roles = {}
    current = None
    buf = []
    for word, tag in zip(words, tags):
        if tag == "O":
            if current is not None:
                roles.setdefault(current, []).append(" ".join(buf))
                current, buf = None, []
            continue
        prefix, _, label = tag.partition("-")
        if prefix == "B":
            if current is not None:
                roles.setdefault(current, []).append(" ".join(buf))
            current, buf = label, [word]
        else:  # "I" - continuation
            buf.append(word)
    if current is not None:
        roles.setdefault(current, []).append(" ".join(buf))
    return roles


def sentence_split(text):
    """Split text into sentences. Use spaCy en_core_web_sm if present; else a simple fallback."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner", "parser"])
        nlp.add_pipe(nlp.create_pipe("sentencizer"))
        return [s.text.strip() for s in nlp(text).sents if s.text.strip()]
    except Exception:
        import re
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def gather_input_files(input_path):
    if os.path.isdir(input_path):
        return sorted(glob.glob(os.path.join(input_path, "*.txt")))
    return [input_path]


def extract_date(filename):
    """Pull a date embedded in a filename (e.g. '..._02-13-2015.txt') and return it as mm-dd-yyyy,
    the format the Suite's network/Gephi date handling parses. Returns '' if no date is found."""
    m = re.search(r'(\d{1,2})[-_/.](\d{1,2})[-_/.](\d{4})', filename)
    if m:
        return "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
    m = re.search(r'(\d{4})[-_/.](\d{1,2})[-_/.](\d{1,2})', filename)  # yyyy-mm-dd -> mm-dd-yyyy
    if m:
        return "%s-%s-%s" % (m.group(2), m.group(3), m.group(1))
    return ""


def dress_hyperlink(path):
    """Wrap a file path as an Excel hyperlink, matching the NLP Suite convention used in every
    output CSV (=hyperlink("path") - click opens the source document). Falls back to the bare
    filename if the formula would exceed Excel's 255-character hyperlink limit."""
    link = '=hyperlink("' + str(path) + '")'
    return link if len(link) <= 255 else os.path.basename(path)


def write_html_duplicate(html_dir, doc_name, sentences):
    """Write an HTML copy of the document with one anchored, highlightable element per sentence,
    so a hyperlink ending in #s5 opens the browser scrolled to (and highlighting) sentence 5.
    Returns the html file path. The sentence ids (s1, s2, ...) match the Sentence ID in the CSV."""
    html_path = os.path.join(html_dir, doc_name + ".html")
    parts = [
        "<!DOCTYPE html>", "<html><head><meta charset='utf-8'>",
        "<title>" + html.escape(doc_name) + "</title>",
        "<style>",
        "body{font-family:Georgia,serif;line-height:1.7;max-width:820px;margin:2em auto;padding:0 1em;color:#222;}",
        "h2{font-size:1.05em;color:#555;border-bottom:1px solid #ddd;padding-bottom:.3em;}",
        "p{margin:0 0 .35em 0;padding:.15em .4em;border-left:4px solid transparent;scroll-margin-top:1.5em;}",
        "p:target,p.hl{background:#fff176;border-left-color:#f9a825;}",
        "p.hl{animation:flash 1.1s ease-in-out 2;}",
        "@keyframes flash{0%,100%{background:#fff176}50%{background:#ffd54f}}",
        ".sid{color:#aaa;font-size:.72em;margin-right:.5em;user-select:none;}",
        "</style></head><body>",
        "<h2>" + html.escape(doc_name) + "</h2>",
    ]
    for i, s in enumerate(sentences, 1):
        parts.append('<p id="s%d"><span class="sid">%d</span>%s</p>' % (i, i, html.escape(s)))
    # Actively scroll to + highlight the sentence named in the URL hash (#sN). More robust than the
    # CSS :target alone, and re-runs if the hash changes.
    parts.append(
        "<script>function goS(){"
        "var q=new URLSearchParams(location.search).get('s');"
        "var id=q?('s'+q):(location.hash?location.hash.slice(1):'');"
        "if(!id)return;var e=document.getElementById(id);"
        "if(e){e.scrollIntoView({block:'center'});e.classList.remove('hl');"
        "void e.offsetWidth;e.classList.add('hl');}}"
        "addEventListener('DOMContentLoaded',goS);addEventListener('load',goS);addEventListener('hashchange',goS);</script>")
    parts.append("</body></html>")
    with open(html_path, "w", encoding="utf-8") as out:
        out.write("\n".join(parts))

    # Per-sentence redirector files in a _jump subfolder. Excel opens these plain files; each one's
    # script navigates the browser to mainfile.html#sN (the in-browser jump the browser honors).
    jump_dir = os.path.join(html_dir, "_jump")
    os.makedirs(jump_dir, exist_ok=True)
    main_url = "file:///" + urllib.parse.quote(os.path.abspath(html_path).replace("\\", "/"), safe="/:")
    for i in range(1, len(sentences) + 1):
        with open(redirector_path(html_path, i), "w", encoding="utf-8") as r:
            r.write('<!DOCTYPE html><meta charset="utf-8">'
                    '<script>location.replace("%s#s%d")</script>' % (main_url, i))
    return html_path


def redirector_path(html_path, sid):
    """Path of the per-sentence redirector file for a given main HTML page + sentence id."""
    jump_dir = os.path.join(os.path.dirname(html_path), "_jump")
    base = os.path.basename(html_path)[:-5]  # strip ".html"
    return os.path.join(jump_dir, base + "__s%d.html" % sid)


def dress_html_anchor_link(html_path, sid):
    """Excel hyperlink to the per-sentence REDIRECTOR file. Excel opens this plain file (it has no
    #anchor or ?query for Excel to mangle); the redirector's one-line script then navigates the
    browser to mainfile.html#sN, which the browser honors. This bridges the two failures: Excel
    strips '#' from links, and the browser ignores '?query' for local file:// pages - but a real
    in-browser navigation to #sN works."""
    url = "file:///" + urllib.parse.quote(
        os.path.abspath(redirector_path(html_path, sid)).replace("\\", "/"), safe="/:")
    link = '=hyperlink("' + url + '")'
    return link if len(link) <= 255 else os.path.basename(html_path)


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python SRL_worker.py <input_file_or_dir> <output_csv> [model_path]\n")
        sys.exit(2)
    input_path = sys.argv[1]
    output_csv = sys.argv[2]
    model_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL

    if not os.path.exists(model_path):
        sys.stderr.write("SRL model not found at: %s\n" % model_path)
        sys.exit(3)

    # Optional SemLink mapping (drop pb-vn2.json next to the model). If present, Refined roles use the
    # principled per-frame PropBank->VerbNet roles; if absent, the heuristic applies.
    role_map, class_map = load_semlink_map(os.path.join(os.path.dirname(os.path.abspath(model_path)), "pb-vn2.json"))

    files = gather_input_files(input_path)
    if not files:
        sys.stderr.write("No .txt input found at: %s\n" % input_path)
        sys.exit(4)

    # HTML duplicates (one anchored, highlightable element per sentence) go in a subfolder next to
    # the CSV, so the Document hyperlink can open the browser at the exact sentence.
    html_dir = os.path.join(os.path.dirname(os.path.abspath(output_csv)), "SRL_documents_html")
    os.makedirs(html_dir, exist_ok=True)

    sys.stderr.write("Loading SRL model (first load ~30-60s)...\n")
    # Imported here, not at module top: transformer_srl + its submodules register the AllenNLP
    # components, but the legacy py3.8 stack only exists in the isolated SRL env where this runs.
    from transformer_srl import dataset_readers, models, predictors  # noqa: F401
    predictor = predictors.SrlTransformersPredictor.from_path(model_path, "transformer_srl")

    rows = []
    for f in files:
        doc_name = os.path.basename(f)
        doc_date = extract_date(doc_name)
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception as e:
            sys.stderr.write("Could not read %s: %s\n" % (f, e))
            continue
        sentences = sentence_split(text)
        html_path = write_html_duplicate(html_dir, doc_name, sentences)
        for sid, sentence in enumerate(sentences, 1):
            doc_link = dress_html_anchor_link(html_path, sid)
            try:
                res = predictor.predict(sentence=sentence)
            except Exception as e:
                sys.stderr.write("SRL failed on a sentence in %s: %s\n" % (doc_name, e))
                continue
            words = res.get("words", [])
            for v in res.get("verbs", []):
                r = roles_from_tags(words, v.get("tags", []))
                frame = v.get("frame", v.get("sense", ""))
                predicate_lemma = (frame.split(".")[0] if frame else v.get("verb", "")).lower()
                row = {
                    "Document": doc_link,
                    "Date": doc_date,
                    "Sentence ID": sid,
                    "Sentence": sentence,
                    "Predicate": v.get("verb", ""),
                    "Frame": frame,
                    "VerbNet class": class_map.get(frame, ""),
                    "Description": v.get("description", ""),
                }
                for label, header in ROLE_COLUMNS:
                    row[header] = "; ".join(r.get(label, []))
                # Refined thematic-role reading alongside the ARG columns (VerbAtlas if pb2va.tsv is
                # present, else heuristic).
                refined = []
                for label in REFINED_ORDER:
                    for txt in r.get(label, []):
                        role = refine_role(label, txt, predicate_lemma, sense=frame, role_map=role_map)
                        refined.append("%s: %s" % (role, txt))
                row["Refined roles"] = " | ".join(refined)
                rows.append(row)

    with open(output_csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    sys.stderr.write("Wrote %d SRL rows to %s\n" % (len(rows), output_csv))


if __name__ == "__main__":
    main()
