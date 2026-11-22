# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md); section numbers below refer to it. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue); how a release is checked is in §14. What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 22 Nov 2026. v1.6.45 (HW 5 speedups) released 22 Nov; v1.6.44 (bundle size) 21 Nov; v1.6.43 18 Nov. Releases are Cora's (handed over by Roberto). HW 5 is due Sun 6 Dec.

## Next: 1.6.46, the Python 3.11 security release (§3)

Python 3.11 with Pillow 13 and transformers 5 should close the open Dependabot alerts. The release carries the bump and nothing else, so a regression points to it (§3.3). In order:

0. **A sweep of every tool, `tests/tool_sweep.py`** (in progress, started 22 Nov). One recipe per tool (per option where options take different code paths) sets the GUI's widgets and calls its `run()` on `lib/sampleData`, each in its own process, on a zip's own `python-env`, like `bundle_gate.py`. `compare` diffs a candidate's outputs against a baseline, ignoring the known noise (§14). Baseline: the published 1.6.45 zip. It replaces the hand-picked tool runs before each tag, and is step 5's full check. Test-only, so no release of its own. Order: the tools 1.6.46 puts at risk first (BERT, Stanza, spaCy, fastcoref, BERTopic, sentiment, Shape of Stories), then CoreNLP, GIS, SVO, charts and the file tools. Recipes that need software the zip lacks (CoreNLP path, Gephi, MALLET, SRL) report SKIPPED with the reason. Dead files (§1.1) are not menu tools, so nothing here depends on them.
1. **Dead files, PR #1706** (§1.1): rebase onto `roberto`, apply the file list (it also moves the Windows icon to `lib/images/` and updates the spec), merge. Roberto agrees to the deletions first. It removes `src/requirements*.txt` (108 alerts) and the STEP1–3 scripts, which #1688 depends on.
2. **Summarizer replacement** (§3.2), its own PR: `doc_summary_BERT` without `bert-extractive-summarizer`, which blocks transformers ≥ 4.52.
3. **Rebase #1688** (`spike/python-3.11-pillow-13`) onto `roberto` and add what §3.3's table lists: transformers ≥ 5.10, `stanza>=1.12.2`, py311 in `pyproject.toml` and `pyrightconfig.json`, §14's bullets, the CHANGELOG security line.
4. **Re-sync the dev env** on the new Python before testing (a new NLP311 env from `requirements.txt` + `requirements-mac.txt`).
5. **Checks before the tag** (§3.3's list plus §14). The whole `python-env` is rebuilt, so this one needs the **full** tool sweep (step 0) of 1.6.46 against 1.6.45, not only the changed tools, plus BERT NER, summary, embeddings, WSI, fastcoref coreference and BERTopic on a clean Hugging Face cache, and the self-updater 1.6.45 → 1.6.46 (the first update that replaces the bundled Python).
6. After promotion: re-read the Dependabot list (expect 0 open).

Open question: does #1706 ship as its own release first (then the Python bump becomes 1.6.47), or ride in 1.6.46? §3.3 assumed its own.

## Still to check on the published releases

Nothing has been checked on Windows since 1.6.42. One pass on the **published 1.6.45 Windows zip** covers what 1.6.43–1.6.45 changed:
1. The menu from the zip, and one tool per family on `python-env` (§2.5): BERT NER, BERTopic, fastcoref coreference, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart.
2. Shape of Stories with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704).
3. The self-updater from a 1.6.44 install to 1.6.45. Read `%TEMP%\NLP_Suite_update.log`.

On a Mac (1.6.43 → 1.6.44 and 1.6.44 → 1.6.45 self-updates pass, 22 Nov):
4. Update a real **1.6.42** install to the latest release by closing it and clicking Yes (the driver-based checks skipped the click, and the deletion of `NLP_Suite_previous` through a real menu start).
5. NRC and SentiWordNet once with an empty `~/nltk_data`, so `punkt_tab` and `averaged_perceptron_tagger_eng` download.
6. A GIS map and wordclouds from the zip.
7. A source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).
8. The 1.6.45 speedups on the 958-document corpus (measured only on the 60-document sample in the zip).

Ask students who report update problems to send the update log to coralynn.yang@emory.edu.

Once the Windows pass is done: delete `spike/1.6.43-bundle-size-rc` (origin), `spike/1.6.43-bundle-size` (local and fork), and the local `backup/release-v1.6.44-with-dead-files`.

## After 1.6.46

- **Trim the spec further** (§2.1): it keeps spaCy, pandas and the rest for the language advisor, which since #1732 runs on `python-env`. Probe build first.
- **Performance**, in §6.10's order: next, pandas out of `GUI_util` (§6.3).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Smaller copy left from #1705 (§5.2); the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- Retest and close recent issues that releases may have fixed; fix the open recent bugs (§10), including BERTopic on a small corpus of whole documents. Triage the 2021–2024 backlog (§11).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, the silent `git stash` (§15).
- UI overhaul (§7), as its own releases.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13): delete Cora's merged ones; the others are Roberto's call.
