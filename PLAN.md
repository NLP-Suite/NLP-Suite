# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md); section numbers below refer to it. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue); how a release is checked is in §14. What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 23 Nov 2026. v1.6.46 (fixes from the tool sweep) released 23 Nov; v1.6.45 (HW 5 speedups) 22 Nov; v1.6.44 (bundle size) 21 Nov. Releases are Cora's (handed over by Roberto). HW 5 is due Sun 6 Dec.

## Next: 1.6.47, the Python 3.11 security release (§3)

Python 3.11 with Pillow 13 and transformers 5 should close the open Dependabot alerts. The release carries the bump and nothing else, so a regression points to it (§3.3). It was planned as 1.6.46; that number went to the sweep's bug fixes. In order:

1. **Legacy setup only, `chore/remove-legacy-setup`** (§1.1): `setup_Windows/`, `setup_Mac/`, the two shortcut scripts and `src/requirements*.txt` (108 alerts, closed once on `current-stable`), plus the icon move to `lib/images/`. #1688 depends on it. The rest of #1706 (one-off scripts, unused modules, `build-family-viewer.yml`) waits until it is checked against the family viewer; rebase #1706 after this merges.
2. **The summarizer** (§3.2), its own PR: `bert-extractive-summarizer` blocks transformers ≥ 4.52. Nothing calls `doc_summary_BERT` (no GUI offers it), so ask Roberto whether to delete it with its requirement, which is simpler than the rewrite §3.2 proposes.
3. **Rebase #1688** (`spike/python-3.11-pillow-13`) onto `roberto` and add what §3.3's table lists: transformers ≥ 5.10, `stanza>=1.12.2`, the `peft` decision, py311 in `pyproject.toml` and `pyrightconfig.json`, §14's bullets, the CHANGELOG security line.
4. **Re-sync the dev env** on the new Python before testing (a new NLP311 env from `requirements.txt` + `requirements-mac.txt`).
5. **Checks before the tag** (§3.3's list plus §14). The whole `python-env` is rebuilt, so this one needs the **full** tool sweep of 1.6.47 against **1.6.46** (`~/Documents/NLP_output/tool_sweep/1.6.46`, the published zip), not only the changed tools; then `bundle_gate.py` against a 1.6.46 snapshot. Also BERT NER, embeddings, WSI, fastcoref and Stanza coreference, and BERTopic on a clean Hugging Face cache, and the self-updater 1.6.46 → 1.6.47 (the first update that replaces the bundled Python).
6. After promotion: re-read the Dependabot list (expect 0 open). Merge the release branch back into `roberto` with a merge commit, not a squash, as for 1.6.45 (#1743) and 1.6.46 (#1797), so the next release can fast-forward `current-stable`.

Settled 23 Nov: the legacy-setup deletion rides in 1.6.47; the rest of #1706 waits.

**The tool sweep** (`tests/tool_sweep.py`, 129 recipes, every GUI has one or a `NOT_COVERED` reason) found the bugs 1.6.46 fixed (#1769–#1796). The second batch and the compare fixes (a recipe the baseline never ran is listed for review, not as a regression) are PR #1799. 1.6.46 checked clean on the published Mac zip: 0 regressions against 1.6.45, and the bundle gate passes. Baselines in `~/Documents/NLP_output/tool_sweep/`: 1.6.45, 1.6.46-rc1 and 1.6.46.

## Still to check on the published releases

Nothing has been checked on Windows since 1.6.42. One pass on the **published 1.6.46 Windows zip** covers what 1.6.43–1.6.46 changed:
1. The menu from the zip, and one tool per family on `python-env` (§2.5): BERT NER, BERTopic, fastcoref coreference, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart.
2. Shape of Stories with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704).
3. The self-updater from a 1.6.45 install to 1.6.46. Read `%TEMP%\NLP_Suite_update.log`.

On a Mac (1.6.43 → 1.6.44 and 1.6.44 → 1.6.45 self-updates pass, 22 Nov; 1.6.45 → 1.6.46 not yet run):
4. Update a real **1.6.42** install to the latest release by closing it and clicking Yes (the driver-based checks skipped the click, and the deletion of `NLP_Suite_previous` through a real menu start).
5. NRC and SentiWordNet once with an empty `~/nltk_data`, so `punkt_tab` and `averaged_perceptron_tagger_eng` download.
6. A GIS map and wordclouds from the zip.
7. A source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).
8. The 1.6.45 speedups on the 958-document corpus (measured only on the 60-document sample in the zip).

Ask students who report update problems to send the update log to coralynn.yang@emory.edu.

## After 1.6.47

- **Fold the tests into one file per `src/` module** (`test_<module>.py`): about 105 files today, some modules spread over three (`config_util`, `IO_files_util`, `topic_modeling_gensim_util`) and GIS over about a dozen, some named after a bug or a person. Its own PR, a pure move: `pytest --collect-only` counts the same tests before and after. Watch the GIS tests that load functions from the source with their own module-level setup. #1683 and #1682 add `test_gender_dictionary_persons.py` and `test_spaCy_conll_head.py`: rename them after they merge. Can go before 1.6.47.
- Left from the sweep: #1779 (functions that do not exist, e.g. Comparative bar charts); the categorical treemap, sunburst and colormap charts stop with "No search values found" (§10).
- **Trim the spec further** (§2.1): it keeps spaCy, pandas and the rest for the language advisor, which since #1732 runs on `python-env`. Probe build first.
- **Performance**, in §6.10's order: next, pandas out of `GUI_util` (§6.3).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Smaller copy left from #1705 (§5.2); the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- Retest and close recent issues that releases may have fixed; fix the open recent bugs (§10). Triage the 2021–2024 backlog (§11).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, the silent `git stash` (§15).
- UI overhaul (§7), as its own releases.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13): delete Cora's merged ones; the others are Roberto's call.
