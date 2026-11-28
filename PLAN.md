# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md); section numbers below refer to it. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue); how a release is checked is in §14. What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 23 Nov 2026. v1.6.47 (Python 3.11, Pillow 13, transformers 5: the security release) released 23 Nov; v1.6.46 (fixes from the tool sweep) 23 Nov; v1.6.45 (HW 5 speedups) 22 Nov; v1.6.44 (bundle size) 21 Nov. Releases are Cora's (handed over by Roberto). HW 5 is due Sun 6 Dec.

## Next: 1.6.48, cleanup and what the sweep left

No dependency changes: `requirements*.txt` and the bundled Python (python-build-standalone `20251217`) stay as in 1.6.47, so the sweep against 1.6.47 shows only what the code changed. In order:

1. **Tests, one file per `src/` module: PR #1803.** Rebase on `roberto`. 1.6.47 added two tests to `test_WSI.py`, which #1803 splits: they go to `test_WSI_classes.py`. #1801 has merged, so also fold its two BERT test files (`test_BERT_sentiment_truncation.py`, `test_BERT_word_embeddings.py`) into `test_BERT_util.py`. Pure move: `pytest --collect-only` counts the same tests before and after.
2. **The rest of #1706** (§1.1): the one-off `src/_*.py` scripts, the unused modules, `post_build_fixup.py`, `wiki-draft-About.md`, `build-family-viewer.yml`. The family-viewer worry is settled (23 Nov): the viewer (`family_archive_app.py`, `gedcom_to_csv.py`) moved to a private repo on 16 Jun 2026 and imported only pandas, geopy and the standard library, nothing #1706 deletes; `build-family-viewer.yml` builds two spec files that are no longer in the repo. Rebase #1706 on `roberto`, drop what 1.6.47 already deleted, merge once Roberto agrees.
3. **Left from the sweep** (§10): #1779 (functions that do not exist, e.g. Comparative bar charts); the categorical treemap, sunburst and colormap charts stop with "No search values found".
4. **`tool_sweep.py` on a source checkout:** seed each recipe's `config/` from `lib/config_defaults` when the folder being swept has none. On 23 Nov a source sweep ran about 40 recipes with no language set (VADER: "your language is ''"), so it could not stand in for a zip sweep.
5. **Checks before the tag** (§14): tool sweep of the candidate against **1.6.47** (sweep the published 1.6.47 zip first; until then `~/Documents/NLP_output/tool_sweep/1.6.47-rc2` plus `1.6.47-rc3-wsi2` for WSI), `bundle_gate.py` against a 1.6.47 snapshot, the self-updater 1.6.47 → 1.6.48. After promotion, merge the release branch back into `roberto` with a merge commit (#1804 did it for 1.6.47).

## 1.6.49: Tcl/Tk 9, and the newest CPython 3.11 (§3.3)

1.6.47 bundles CPython 3.11.14 from python-build-standalone `20251217`, the last release with Tcl/Tk 8.6. The newest 3.11 (3.11.18, `20261110`) comes only with Tcl/Tk 9, which crashed 54 GUIs at open in the first 1.6.47 candidate. Porting `src/` to Tcl 9 lets the bundled Python take four more CPython patch releases. Its own release, because it touches every GUI. Plan in §3.3.

## Still to check on the published releases

Nothing has been checked on Windows since 1.6.42. One pass on the **published 1.6.47 Windows zip** covers what 1.6.43–1.6.47 changed:
1. The menu from the zip, and one tool per family on `python-env` (§2.5): BERT NER, BERTopic, fastcoref coreference, Stanza coreference, WSI with BERT, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart.
2. Shape of Stories with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704); the welcome screen and logo (Pillow 13).
3. The self-updater from a 1.6.46 install to 1.6.47: the first update that replaces the bundled Python, through the Windows (PowerShell) swap script, which the Mac check on 23 Nov did not exercise. Read `%TEMP%\NLP_Suite_update.log`.

Ask students who report update problems to send the update log to coralynn.yang@emory.edu.

## After 1.6.49

- **pandas 3, folium 1, ipython 9** (§3.2): 1.6.47 caps them below those versions; moving to each is its own change, tested with the sweep.
- **Trim the spec further** (§2.1): it keeps spaCy, pandas and the rest for the language advisor, which since #1732 runs on `python-env`. Probe build first.
- **Performance**, in §6.10's order: next, pandas out of `GUI_util` (§6.3).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Smaller copy left from #1705 (§5.2); the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- Retest and close recent issues that releases may have fixed; fix the open recent bugs (§10). Triage the 2021–2024 backlog (§11).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, the silent `git stash` (§15).
- UI overhaul (§7), as its own releases.
- Outdated NLP tools and models (§16): SRL env first, then one configurable embedding model, GlotLID, Maverick and GLiNER as new options; each its own issue, checked with the sweep.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13): delete Cora's merged ones; the others are Roberto's call.
