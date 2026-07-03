# SRL bridge - runs in the NLP Suite's main (3.10) env. Semantic Role Labeling cannot run in the
# Suite's environment (Riccorl/transformer-srl pins a legacy 2020-2022 stack: torch 1.7, allennlp
# 1.2, spaCy 2.x, Python 3.8). So SRL runs in a SEPARATE isolated Python 3.8 env, invoked here as a
# subprocess - the same pattern by which CoreNLP runs as a separate Java process.
#
# Output: a CSV (Document, Sentence ID, Sentence, Predicate, Frame, ARG0 Agent, ARG1 Patient,
# ARG2 Recipient/Beneficiary, Where/When/How/Why) - the "who did what to whom" structure.

import os
import sys
import subprocess
import tkinter.messagebox as mb

import IO_files_util
import IO_user_interface_util
import GUI_util

# SRL runs in a SEPARATE isolated Python 3.8 env (transformer-srl pins a legacy torch 1.7 / allennlp
# 1.2 / spaCy-2 stack), invoked as a subprocess - the same pattern CoreNLP uses for Java. To work on
# ANY machine (not hardcoded dev paths) we DISCOVER the pieces rather than hardcode them:
#   * the SRL env's python : $NLP_SRL_PYTHON, else a sibling conda env named nlp_srl/srl_test38/srl
#   * the model            : <NLP-Suite>/lib/SRL/srl_bert_base_conll2012.tar.gz (legacy fallback too)
#   * the worker           : src/SRL_worker.py (ships with the Suite)
# Run  python setup_SRL.py  once on a new machine to create the env and download the model.

SRL_WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SRL_worker.py")
_SRL_LIB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib", "SRL")
SRL_MODEL = os.path.join(_SRL_LIB_DIR, "srl_bert_base_conll2012.tar.gz")
_SRL_ENV_NAMES = ("nlp_srl", "srl_test38", "srl")
_MODEL_FILENAME = "srl_bert_base_conll2012.tar.gz"

# Copula/auxiliary/modal predicate lemmas filtered OUT of the network/Sankey/charts (NOT the CSV),
# so the visuals surface meaningful actions instead of function words.
_COPULA_AUX = {"be", "will", "would", "can", "could", "shall", "should", "may", "might", "must", "ought"}


def _parse_refined(cell):
    """'Stimulus: The news | Experiencer: the man' -> {'The news': 'Stimulus', ...}. Each role keeps
    only its primary name (the part before ' / ', dropping the preposition cue)."""
    out = {}
    for seg in str(cell).split(' | '):
        if ': ' in seg:
            role, _, filler = seg.partition(': ')
            filler = filler.strip()
            if filler:
                out[filler] = role.split(' / ')[0].strip()
    return out


def _refined_roles_list(cell):
    """All primary role names in a 'Refined roles' cell (one per labelled argument), for counting."""
    roles = []
    for seg in str(cell).split(' | '):
        if ': ' in seg:
            role, _, filler = seg.partition(': ')
            if filler.strip():
                roles.append(role.split(' / ')[0].strip())
    return roles


def _verbnet_class_names():
    """Map a VerbNet numeric class id (as SemLink records it, e.g. '42.1') to the readable NLTK id
    ('murder-42.1'), for friendlier charts. Best-effort: returns {} if NLTK VerbNet is unavailable."""
    try:
        from nltk.corpus import verbnet as vn
        names = {}
        for cid in vn.classids():
            num = cid.split('-', 1)[1] if '-' in cid else cid   # 'murder-42.1' -> '42.1'
            names[num] = cid
        return names
    except Exception:
        return {}


def srl_python():
    """Locate the isolated SRL env's python: explicit $NLP_SRL_PYTHON, else a sibling conda env
    (nlp_srl / srl_test38 / srl) of the interpreter running the Suite. '' if not found."""
    override = os.environ.get("NLP_SRL_PYTHON", "")
    if override and os.path.isfile(override):
        return override
    envs_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))  # .../envs
    for name in _SRL_ENV_NAMES:
        for sub in ("python.exe", os.path.join("bin", "python3"), os.path.join("bin", "python")):
            cand = os.path.join(envs_dir, name, sub)
            if os.path.isfile(cand):
                return cand
    return ""


def srl_model():
    """Path to the SRL model under <NLP-Suite>/lib/SRL/, with a legacy dev fallback. '' if absent."""
    if os.path.isfile(SRL_MODEL):
        return SRL_MODEL
    legacy = os.path.join(os.path.expanduser("~"), "Documents", "NLP_SRL_resources", _MODEL_FILENAME)
    return legacy if os.path.isfile(legacy) else ""


def is_available():
    """True only if the isolated SRL env, the worker, and the model are all present/discoverable."""
    return bool(srl_python()) and os.path.isfile(SRL_WORKER) and bool(srl_model())


def availability_message():
    """Human-readable reason SRL can't run, for surfacing to the user (no silent failure)."""
    missing = []
    if not srl_python():
        missing.append("the isolated SRL Python 3.8 environment (a conda env named 'nlp_srl')")
    if not srl_model():
        missing.append("the SRL model (lib/SRL/%s)" % _MODEL_FILENAME)
    if not os.path.isfile(SRL_WORKER):
        missing.append("the SRL worker script (src/SRL_worker.py)")
    return ("Semantic Role Labeling needs a one-time setup that is not yet complete on this "
            "machine.\n\nMissing:\n - " + "\n - ".join(missing) +
            "\n\nRun  python setup_SRL.py  (in the NLP Suite folder) to create the SRL environment "
            "and download the model.\n\nSRL runs in its own isolated environment - it cannot share "
            "the Suite's packages.")


def run_SRL(window, inputFilename, inputDir, outputDir, chartPackage='No charts', dataTransformation=''):
    """Run SRL on the selected txt file or directory. Returns a list of output file paths (or [])."""
    if not is_available():
        mb.showwarning(title="SRL not available", message=availability_message())
        return []

    input_path = inputFilename if inputFilename else inputDir
    if not input_path:
        mb.showwarning(title="No input",
                       message="Please select a txt file or a directory of txt files for SRL.")
        return []

    # Put all SRL output in an SRL_<corpus> subdirectory (the CSV plus the HTML document
    # duplicates), consistent with the SVO_/NER_ output-folder naming convention.
    srl_dir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                     label='SRL', silent=True)
    if not srl_dir:
        mb.showwarning(title="SRL output folder",
                       message="Could not create the SRL output subdirectory.\n\nPlease check the "
                               "output directory and try again.")
        return []

    output_csv = IO_files_util.generate_output_file_name(
        input_path, inputDir, srl_dir, ".csv", "SRL")

    startTime = IO_user_interface_util.timed_alert(
        window, 2000, 'Analysis start',
        'Started running SRL (Semantic Role Labeling) at', True, '', True)

    try:
        proc = subprocess.run(
            [srl_python(), SRL_WORKER, input_path, output_csv, srl_model()],
            capture_output=True, text=True)
    except Exception as e:
        mb.showerror(title="SRL error", message="Could not launch the SRL subprocess:\n\n%s" % e)
        return []

    if proc.returncode != 0:
        # Surface the worker's stderr rather than failing silently.
        tail = (proc.stderr or "").strip()[-1500:]
        mb.showerror(title="SRL error",
                     message="The SRL subprocess reported an error:\n\n%s" % tail)
        return []

    if not os.path.isfile(output_csv):
        mb.showwarning(title="SRL produced no output",
                       message="SRL completed but produced no output file. Worker messages:\n\n%s"
                               % (proc.stderr or "").strip()[-1500:])
        return []

    # Add the WordNet sense column alongside the SemLink VerbNet class / FrameNet frame columns.
    # The worker runs in the isolated srl_test38 env (JSON only, no NLTK); WordNet needs NLTK, so it
    # is resolved here in the main env, context-disambiguated (Lesk) like the WSD feature.
    _add_wordnet_column(output_csv)

    output_files = [output_csv]
    output_files.extend(_build_srl_visualizations(
        window, output_csv, srl_dir, inputFilename, inputDir, chartPackage, dataTransformation))

    IO_user_interface_util.timed_alert(
        window, 2000, 'Analysis end',
        'Finished running SRL (Semantic Role Labeling) at', True, '', True, startTime, False)

    return output_files


def _add_wordnet_column(srl_csv):
    """Add a 'WordNet' column to the SRL table: the predicate's WordNet verb synset, disambiguated
    IN CONTEXT with the Lesk algorithm against the row's Sentence (same approach as the WSD feature).
    Placed next to the SemLink 'VerbNet class'/'FrameNet frame' columns so the table carries all three
    sense inventories (WordNet, VerbNet, FrameNet) for the predicate. Errors are surfaced, not swallowed."""
    import pandas as pd
    try:
        df = pd.read_csv(srl_csv, encoding='utf-8', on_bad_lines='skip', dtype={'VerbNet class': str})
    except Exception as e:
        mb.showwarning(title="SRL WordNet column",
                       message="Could not read the SRL table to add the WordNet column:\n\n%s" % e)
        return
    if 'WordNet' in df.columns or 'Predicate' not in df.columns:
        return
    try:
        import IO_libraries_util
        IO_libraries_util.import_nltk_resource(GUI_util.window, 'corpora/wordnet', 'wordnet')
        from nltk.wsd import lesk
    except Exception as e:
        mb.showwarning(title="SRL WordNet column",
                       message="Could not load WordNet (NLTK) to add the WordNet column:\n\n%s" % e)
        return

    def _wn_sense(row):
        # the predicate LEMMA: from the PropBank Frame ('picture.01' -> 'picture'), else the surface predicate
        frame = str(row.get('Frame', '') or '')
        lemma = frame.split('.')[0].strip().lower() if frame and frame.lower() != 'nan' else ''
        if not lemma:
            lemma = str(row.get('Predicate', '') or '').strip().lower()
        if not lemma:
            return ''
        sent = str(row.get('Sentence', '') or '')
        context = sent.split() if sent.strip() else [lemma]
        try:
            syn = lesk(context, lemma, 'v')
        except Exception:
            syn = None
        return syn.name() if syn else 'Not found'

    df['WordNet'] = df.apply(_wn_sense, axis=1)
    # place 'WordNet' right after 'FrameNet frame' so the three sense inventories sit together
    cols = list(df.columns)
    if 'FrameNet frame' in cols:
        cols.remove('WordNet')
        cols.insert(cols.index('FrameNet frame') + 1, 'WordNet')
        df = df[cols]
    try:
        df.to_csv(srl_csv, index=False, encoding='utf-8')
    except Exception as e:
        mb.showwarning(title="SRL WordNet column",
                       message="Could not write the SRL table with the WordNet column:\n\n%s" % e)


def _build_srl_visualizations(window, srl_csv, srl_dir, inputFilename, inputDir,
                              chartPackage, dataTransformation):
    """Build visuals from the SRL CSV by mapping ARG0 -> Agent (ARG0), Predicate -> Predicate,
    ARG1 -> Patient (ARG1) and reusing the SVO suite's network (Gephi), Sankey, and bar-chart machinery
    - so SRL gets the 'who did what to whom' network, Sankey flow, and frequency charts of the top
    Agents/Predicates/Patients. Each visual is guarded so one failure never blocks the others or the
    SRL CSV itself (errors are surfaced, never swallowed)."""
    import pandas as pd
    outputs = []
    try:
        # 'VerbNet class' must stay a string: ids like '44' or '9.10' would be mangled to 44.0 / 9.1
        # if pandas infers the column as float.
        df = pd.read_csv(srl_csv, encoding='utf-8', on_bad_lines='skip', dtype={'VerbNet class': str})
    except Exception as e:
        mb.showwarning(title="SRL visualization",
                       message="Could not read the SRL output for visualization:\n\n%s" % e)
        return outputs

    def col(name):
        return df[name].fillna('') if name in df.columns else [''] * len(df)

    svo = pd.DataFrame()
    svo['Agent (ARG0)'] = col('ARG0 (Agent)')
    svo['Predicate'] = col('Predicate')
    svo['Patient (ARG1)'] = col('ARG1 (Patient)')
    svo['Location'] = col('Where (ARGM-LOC)')
    svo['Time'] = col('When (ARGM-TMP)')
    svo['Sentence ID'] = col('Sentence ID')
    svo['Sentence'] = col('Sentence')
    svo['Document'] = col('Document')
    svo['Date'] = col('Date')
    svo['Refined roles'] = col('Refined roles')   # carried for the VerbNet-role views (not the relations file)
    svo['VerbNet class'] = col('VerbNet class')   # the disambiguated VerbNet class per predicate (SemLink)
    svo['FrameNet frame'] = col('FrameNet frame') # the disambiguated FrameNet frame per predicate (SemLink chain)
    svo['WordNet'] = col('WordNet')               # the Lesk-disambiguated WordNet verb synset per predicate

    # Keep rows with a predicate AND at least an agent or a patient (i.e., a drawable edge).
    s = svo['Agent (ARG0)'].astype(str).str.strip()
    v = svo['Predicate'].astype(str).str.strip()
    o = svo['Patient (ARG1)'].astype(str).str.strip()
    # Drop copula/auxiliary/modal predicates so the visuals show real actions, not function words.
    # The predicate LEMMA comes from the Frame (be.01 -> be), falling back to the surface word.
    if 'Frame' in df.columns:
        lemma = df['Frame'].fillna('').astype(str).str.split('.').str[0].str.lower()
        lemma = lemma.where(lemma.str.strip() != '', v.str.lower())
    else:
        lemma = v.str.lower()
    svo = svo[(v != '') & ((s != '') | (o != '')) & (~lemma.isin(_COPULA_AUX))]
    if svo.empty:
        return outputs

    # A numeric, 1-based Document ID per unique Document name. The shared chart code
    # (visualize_charts_util) requires a 'Document ID' column whenever a chart is grouped
    # by Document (groupByList=['Document']); the SRL CoNLL only carries the Document name.
    doc_id_map = {d: i + 1 for i, d in enumerate(dict.fromkeys(svo['Document'].astype(str)))}
    def _doc_id(doc):
        return doc_id_map.get(str(doc), 0)
    svo['Document ID'] = svo['Document'].astype(str).map(doc_id_map)

    svo_csv = IO_files_util.generate_output_file_name(srl_csv, inputDir, srl_dir, '.csv', 'relations')
    try:
        svo[['Agent (ARG0)', 'Predicate', 'Patient (ARG1)', 'Location', 'Time',
             'Sentence ID', 'Sentence', 'Document ID', 'Document', 'Date']].to_csv(svo_csv, index=False, encoding='utf-8')
        outputs.append(svo_csv)
    except Exception as e:
        mb.showwarning(title="SRL visualization",
                       message="Could not write the SVO-format file:\n\n%s" % e)
        return outputs

    fileBase = os.path.splitext(os.path.basename(srl_csv))[0]
    use_date = svo['Date'].astype(str).str.strip().ne('').any()

    # Interactive network graph (Python vis.js) - agent -> predicate -> patient. Opens in the browser,
    # no external app needed. Passing the Date column makes it DYNAMIC/time-varying ('agency over
    # time') when the documents are dated. This is the primary network for SRL.
    try:
        import charts_util
        net = charts_util.network_graph_visjs(
            svo_csv, srl_dir, 'Agent (ARG0)', 'Predicate', 'Patient (ARG1)',
            date_col='Date' if use_date else None)
        if net:
            outputs.extend(net if isinstance(net, list) else [net])
    except Exception as e:
        mb.showwarning(title="SRL network graph (interactive)",
                       message="Could not build the interactive SRL network graph:\n\n%s" % repr(e))

    # Gephi network graph (.gexf) - for users who prefer Gephi; create_gexf self-skips if Gephi is
    # not installed. logic='default'+spellCol='Date' gives a dynamic graph when dated, else static.
    try:
        import Gephi_util
        gexf = Gephi_util.create_gexf(window, fileBase, srl_dir, svo_csv,
                                      'Agent (ARG0)', 'Predicate', 'Patient (ARG1)',
                                      spellCol='Date' if use_date else '',
                                      logic='default' if use_date else 'static')
        if gexf:
            outputs.extend(gexf if isinstance(gexf, list) else [gexf])
    except Exception as e:
        mb.showwarning(title="SRL network graph (Gephi)",
                       message="Could not build the SRL Gephi network graph:\n\n%s" % repr(e))

    # 2) Sankey flow: agent -> predicate -> patient
    try:
        import charts_util
        sankey_out = IO_files_util.generate_output_file_name(svo_csv, inputDir, srl_dir, '.html', 'sankey')
        sk = charts_util.Sankey(svo_csv, sankey_out, 'Agent (ARG0)', 5, 'Predicate', 10, True, 'Patient (ARG1)', 20)
        if sk:
            outputs.extend(sk if isinstance(sk, list) else [sk])
    except Exception as e:
        mb.showwarning(title="SRL Sankey",
                       message="Could not build the SRL Sankey chart:\n\n%s" % e)

    # 3) Frequency bar charts: top Agents (ARG0), Predicates, Patients (ARG1)
    if chartPackage and chartPackage != 'No charts':
        try:
            import charts_util
            chart_specs = [
                ('Agent (ARG0)', 'Frequency Distribution of SRL Agents (ARG0)', 'Agent (ARG0)', 'SRL-agent'),
                ('Predicate', 'Frequency Distribution of SRL Predicates', 'Predicate', 'SRL-predicate'),
                ('Patient (ARG1)', 'Frequency Distribution of SRL Patients (ARG1)', 'Patient (ARG1)', 'SRL-patient'),
            ]
            for ycol, title, xlabel, ftype in chart_specs:
                try:
                    of = charts_util.visualize_chart(
                        chartPackage, dataTransformation, svo_csv, srl_dir,
                        columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=[ycol],
                        chart_title=title, count_var=1, hover_label=[],
                        outputFileNameType=ftype, column_xAxis_label=xlabel,
                        groupByList=['Document'], plotList=['Frequency'], chart_title_label=xlabel)
                    if of:
                        outputs.extend(of if isinstance(of, list) else [of])
                except Exception as e:
                    mb.showwarning(title="SRL chart",
                                   message="Could not build the '%s' chart:\n\n%s" % (title, e))
        except Exception as e:
            mb.showwarning(title="SRL charts",
                           message="Could not build the SRL frequency charts:\n\n%s" % e)

    # ---- VerbNet-role views: the refined SemLink roles drive their OWN role-flow network and Sankey
    # (Agent-role -> Predicate -> Patient-role) plus a frequency profile of the roles, so the NEW role
    # values are visualized, not just the S/V/O structure. Reuses the same machinery on role-typed
    # columns, so no change to shared chart code. The Agent/Patient role is read back from the
    # 'Refined roles' column by matching the argument filler text. ----
    refined_maps = [_parse_refined(x) for x in svo['Refined roles']]
    agent_roles, patient_roles = [], []
    for m, a, p in zip(refined_maps,
                       svo['Agent (ARG0)'].astype(str), svo['Patient (ARG1)'].astype(str)):
        a, p = a.strip(), p.strip()
        agent_roles.append(m.get(a, 'Agent') if a else '')
        patient_roles.append(m.get(p, 'Patient/Theme') if p else '')
    role_df = svo.copy()
    role_df['Agent role'] = agent_roles
    role_df['Patient role'] = patient_roles

    role_csv = IO_files_util.generate_output_file_name(svo_csv, inputDir, srl_dir, '.csv', 'roles')
    role_view_ok = False
    try:
        role_df[['Agent role', 'Predicate', 'Patient role', 'Location', 'Time',
                 'Sentence ID', 'Sentence', 'Document', 'Date']].to_csv(
            role_csv, index=False, encoding='utf-8')
        outputs.append(role_csv)
        role_view_ok = True
    except Exception as e:
        mb.showwarning(title="SRL role visualization",
                       message="Could not write the VerbNet-role relations file:\n\n%s" % e)

    if role_view_ok:
        # Role-flow network: Agent-role -> Predicate -> Patient-role.
        try:
            import charts_util
            rnet = charts_util.network_graph_visjs(
                role_csv, srl_dir, 'Agent role', 'Predicate', 'Patient role',
                date_col='Date' if use_date else None)
            if rnet:
                outputs.extend(rnet if isinstance(rnet, list) else [rnet])
        except Exception as e:
            mb.showwarning(title="SRL role network",
                           message="Could not build the VerbNet-role network:\n\n%s" % repr(e))
        # Role-flow Sankey: Agent-role -> Predicate -> Patient-role.
        try:
            import charts_util
            rsankey_out = IO_files_util.generate_output_file_name(
                role_csv, inputDir, srl_dir, '.html', 'role-sankey')
            rsk = charts_util.Sankey(role_csv, rsankey_out,
                                     'Agent role', 5, 'Predicate', 10, True, 'Patient role', 20)
            if rsk:
                outputs.extend(rsk if isinstance(rsk, list) else [rsk])
        except Exception as e:
            mb.showwarning(title="SRL role Sankey",
                           message="Could not build the VerbNet-role Sankey:\n\n%s" % e)

    # Refined-role frequency profile (counts every labelled role across the corpus).
    if chartPackage and chartPackage != 'No charts':
        try:
            import charts_util
            role_rows = []
            for rr, doc in zip(svo['Refined roles'], svo['Document'].astype(str)):
                for role in _refined_roles_list(rr):
                    role_rows.append({'Document ID': _doc_id(doc), 'Document': doc, 'Role': role})
            if role_rows:
                roles_freq_csv = IO_files_util.generate_output_file_name(
                    svo_csv, inputDir, srl_dir, '.csv', 'role-freq')
                pd.DataFrame(role_rows).to_csv(roles_freq_csv, index=False, encoding='utf-8')
                of = charts_util.visualize_chart(
                    chartPackage, dataTransformation, roles_freq_csv, srl_dir,
                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['Role'],
                    chart_title='Frequency Distribution of SRL Refined Roles (VerbNet)',
                    count_var=1, hover_label=[], outputFileNameType='SRL-refined-role',
                    column_xAxis_label='Refined role (VerbNet)', groupByList=['Document'],
                    plotList=['Frequency'], chart_title_label='Refined role (VerbNet)')
                if of:
                    outputs.extend(of if isinstance(of, list) else [of])
        except Exception as e:
            mb.showwarning(title="SRL refined-role chart",
                           message="Could not build the refined-role frequency chart:\n\n%s" % e)

        # VerbNet-class profile: how often each DISAMBIGUATED VerbNet class occurs (the predicate's
        # sense-resolved class via SemLink) - the backbone for verb aggregation (e.g. grouping
        # murder-42.1 / destroy-44 / hit-18.1 into a 'violence' category).
        try:
            import charts_util
            class_names = _verbnet_class_names()      # numeric id -> readable 'murder-42.1' (best-effort)
            vn_rows = []
            for cls, doc in zip(svo['VerbNet class'], svo['Document'].astype(str)):
                cls = str(cls).strip()
                if cls:
                    vn_rows.append({'Document ID': _doc_id(doc), 'Document': doc, 'VerbNet class': class_names.get(cls, cls)})
            if vn_rows:
                vn_freq_csv = IO_files_util.generate_output_file_name(
                    svo_csv, inputDir, srl_dir, '.csv', 'verbnet-class')
                pd.DataFrame(vn_rows).to_csv(vn_freq_csv, index=False, encoding='utf-8')
                of = charts_util.visualize_chart(
                    chartPackage, dataTransformation, vn_freq_csv, srl_dir,
                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['VerbNet class'],
                    chart_title='Frequency Distribution of SRL VerbNet Classes',
                    count_var=1, hover_label=[], outputFileNameType='SRL-verbnet-class',
                    column_xAxis_label='VerbNet class', groupByList=['Document'],
                    plotList=['Frequency'], chart_title_label='VerbNet class')
                if of:
                    outputs.extend(of if isinstance(of, list) else [of])
        except Exception as e:
            mb.showwarning(title="SRL VerbNet class chart",
                           message="Could not build the VerbNet class frequency chart:\n\n%s" % e)

        # FrameNet frame profile: how often each disambiguated FrameNet frame occurs (the predicate's
        # frame via the SemLink chain + gated lemma fallback) - interpretable action categories
        # (Killing, Destroying, Execution, Attack, Cause_harm ...) for content analysis.
        try:
            import charts_util
            fn_rows = []
            for fr, doc in zip(svo['FrameNet frame'], svo['Document'].astype(str)):
                fr = str(fr).strip()
                if fr:
                    fn_rows.append({'Document ID': _doc_id(doc), 'Document': doc, 'FrameNet frame': fr})
            if fn_rows:
                fn_freq_csv = IO_files_util.generate_output_file_name(
                    svo_csv, inputDir, srl_dir, '.csv', 'framenet-frame')
                pd.DataFrame(fn_rows).to_csv(fn_freq_csv, index=False, encoding='utf-8')
                of = charts_util.visualize_chart(
                    chartPackage, dataTransformation, fn_freq_csv, srl_dir,
                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['FrameNet frame'],
                    chart_title='Frequency Distribution of SRL FrameNet Frames',
                    count_var=1, hover_label=[], outputFileNameType='SRL-framenet-frame',
                    column_xAxis_label='FrameNet frame', groupByList=['Document'],
                    plotList=['Frequency'], chart_title_label='FrameNet frame')
                if of:
                    outputs.extend(of if isinstance(of, list) else [of])
        except Exception as e:
            mb.showwarning(title="SRL FrameNet frame chart",
                           message="Could not build the FrameNet frame frequency chart:\n\n%s" % e)

        # WordNet-sense profile: how often each Lesk-disambiguated WordNet verb synset occurs -
        # the WordNet counterpart of the VerbNet-class and FrameNet-frame profiles above.
        try:
            import charts_util
            wn_rows = []
            for wn, doc in zip(svo['WordNet'], svo['Document'].astype(str)):
                wn = str(wn).strip()
                if wn and wn.lower() != 'nan':
                    wn_rows.append({'Document ID': _doc_id(doc), 'Document': doc, 'WordNet': wn})
            if wn_rows:
                wn_freq_csv = IO_files_util.generate_output_file_name(
                    svo_csv, inputDir, srl_dir, '.csv', 'wordnet-sense')
                pd.DataFrame(wn_rows).to_csv(wn_freq_csv, index=False, encoding='utf-8')
                of = charts_util.visualize_chart(
                    chartPackage, dataTransformation, wn_freq_csv, srl_dir,
                    columns_to_be_plotted_xAxis=[], columns_to_be_plotted_yAxis=['WordNet'],
                    chart_title='Frequency Distribution of SRL WordNet Senses',
                    count_var=1, hover_label=[], outputFileNameType='SRL-wordnet-sense',
                    column_xAxis_label='WordNet sense', groupByList=['Document'],
                    plotList=['Frequency'], chart_title_label='WordNet sense')
                if of:
                    outputs.extend(of if isinstance(of, list) else [of])
        except Exception as e:
            mb.showwarning(title="SRL WordNet sense chart",
                           message="Could not build the WordNet sense frequency chart:\n\n%s" % e)

    return outputs
