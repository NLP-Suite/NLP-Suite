# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 21 Nov 2026. v1.6.43 released 18 Nov (the evening of the 17th, Atlanta time). Releases are now Cora's (handed over by Roberto).

## Now: 1.6.43 is out; 1.6.44 (bundle size) is on `release/v1.6.44`; 1.6.45 (HW 5 speedups) is on `roberto`

1.6.43 (what it ships is in the CHANGELOG) passed `bundle_gate.py` and the HW 5 sweep on the published Mac zip; nothing has been checked on Windows. HW 5 is due Sun 6 Dec. 1.6.44 (bundle size) is on `release/v1.6.44`, 12 commits on top of `0a0ea64b`: the bundle-size commits of `spike/1.6.43-bundle-size-rc`, cherry-picked on 18 Nov without its copy commit and docs, and the rest of the old §5.2 copy. On 21 Nov the dead-file deletion (`setup_Windows/`, `setup_Mac/`, `src/requirements*.txt`) was taken off the branch: it comes later with #1706 (future-work §1.1), so 1.6.44 changes only what the build ships. Its CHANGELOG section and the future-work prune are on the branch; `pytest tests/` 781 passed, the CI-like run 731, `gui_smoke.py` 0 crashed. A CI build of the same bundle commits on 13 Nov was 775 MB (Mac) and 863 MB (Windows), against 1,332 and 1,541 MB for 1.6.43. `roberto` has moved on: the three HW 5 speedups (#1734 sentiment lemma cache, #1735 Shape of Stories best k, #1736/#1737 Stanza charts once) merged on 21 Nov and are 1.6.45. Releasing them separately keeps a regression traceable to one release.

Still to check on 1.6.43, on the published zips:
1. **Windows:** one Shape of Stories run with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704).
2. **Update a real 1.6.42 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). The 1.6.41 → 1.6.42 update was never checked by hand either.
3. **A fresh NLTK download:** NRC and SentiWordNet once with an empty `~/nltk_data`, so `punkt_tab` and `averaged_perceptron_tagger_eng` download (every run so far reused data already on disk).
4. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

Ask students who report update problems to send the update log (item 2) to coralynn.yang@emory.edu.

To finish 1.6.44:
1. **Fix `bundle_gate.py`'s two false alarms** (future-work §14): set `DO_NOT_TRACK` in its `_env`, and ignore CustomTkinter's "application has been destroyed" at shutdown. Small, test-only; first, since every check below uses the gate.
2. *(#1706 and the setup-script deletion are no longer in 1.6.44: see Future work.)*
3. **Maybe trim the spec further** (§2.1): it keeps spaCy, pandas and the rest for the language advisor, which since #1732 runs on `python-env` instead. Probe build first.
4. **Re-sync the dev env** before testing: `pip install -r requirements.txt -r requirements-mac.txt --upgrade` in NLP310 (on 17 Nov it had transformers 4.51.3, the pin was 4.41.2; on the branch the pin is now 4.51.3).
5. **Checks on a candidate** (`build-installers.yml`, workflow_dispatch on `release/v1.6.44`, after setting `lib/release_version.txt` and the CHANGELOG heading there):
   - `bundle_gate.py` against 1.6.43 on the Mac zip (`DO_NOT_TRACK=1`): the spec trim is what its menu-archive check is for.
   - The HW 5 sweep (`qtm446/assignments/hw5/hw5_suite_run.py`) on the candidate's own `python-env`: transformers moves to 4.51.3 under BERT sentiment and Shape of Stories. Use the 60-document sample for Shape of Stories (under 50 documents it asks "TOO FEW!", which silent mode answers No).
   - §2.5: zip sizes on both OSes; the menu from each zip; one tool per family on `python-env` (BERT NER, BERTopic, coreference with fastcoref, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart). Launch the menu, Setup external software and the welcome screen by hand: `gui_smoke.py` skips them, and the copy pass changed their text.
   - The self-updater 1.6.43 → 1.6.44: the first update that drops files from the release (`NLP_Suite_previous` holds them until the next start).
6. **The release job is untested until the tag:** the branch moves the actions to Node 24, `download-artifact` and `action-gh-release` too, which only run on a tag. If the release job fails, the zips are still in the run's artifacts; rerun the job or attach them by hand.
7. Promote **`release/v1.6.44` itself** to `current-stable` (a fast-forward: `current-stable` is its ancestor), not `roberto`, which would bring the 1.6.45 speedups with it. Tag `v1.6.44` there, then merge `release/v1.6.44` into `roberto` (the only conflict is the `## Unreleased` heading in CHANGELOG.md: one list, the 1.6.44 bullets under `## v1.6.44`). HW 5 is due Sun 6 Dec: tag after that unless the checks are clean well before, so students do not take a large update in the middle of the homework. Then delete `spike/1.6.43-bundle-size-rc` and its fork copies.

Then **1.6.45, the HW 5 speedups**, from `roberto` after 1.6.44 is merged into it: set the version and the CHANGELOG heading, build a candidate, and run the HW 5 sweep on its `python-env` (sentiment dictionaries, Shape of Stories best k, a Stanza run on the 60-document sample), and `bundle_gate.py` against 1.6.44. The usual promote and tag.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**Dead files** (§1.1): PR #1706 plus the setup scripts and `src/requirements*.txt` (108 Dependabot alerts), after 1.6.45; Roberto agrees to the deletions first.

**1.6.46 (proposed): the Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs #1706 merged first.

**Later, unscheduled:**
- Smaller copy left over from #1705 (§5.2), and the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Retest and close the recent issues that releases may have fixed; fix the open recent bugs (§10). Triage the 2021–2024 backlog (§11).
- Performance, in §6.10's order (next: pandas out of `GUI_util`, §6.3; `requests` and §6.7 come with 1.6.44).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, and the silent `git stash` (§15).
- The GitHub wiki: make `docs/` the source, then publish (§8).
- UI overhaul (§7), as its own releases.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13): delete Cora's merged ones; the others are Roberto's call.
