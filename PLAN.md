# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 18 Nov 2026. v1.6.43 released 18 Nov (the evening of the 17th, Atlanta time). Releases are now Cora's (handed over by Roberto).

## After the 1.6.43 tag

1.6.43 ships everything QTM 446W's HW 5 (due Sun 6 Dec) needs: the Stanza GUIs that closed on a new install (#1728), the language advisor (#1731), the HW 5 tool fixes (#1718–#1724, #1549), the links and copy of #1733, Shape of Stories opening without an "Input directory error", and `NLP_SILENT` covering the timed alerts. Students on 1.6.42 get it from the self-updater; it is the second full-size update (1.6.42 → 1.6.43).

Checked before the tag (Mac, 17 Nov): `pytest tests/` 778 passed (CI-like run 728); `gui_smoke.py` 0 crashed; a release candidate passed `bundle_gate.py` against 1.6.42 (12 of the 13 GUIs that closed on a new install now open; nothing lost); the HW 5 sweep passed on the candidate's own `python-env` (every sentiment algorithm, language detection, Shape of Stories with BERT, spaCy and Stanza through HC, SVD, NMF and best k). The eight issues closed with the promotion. **The published Mac zip:** `bundle_gate.py` against 1.6.42 is running (18 Nov).

Still to check, on the published zips:
1. **Windows:** one Shape of Stories run with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704).
2. **Update a real 1.6.42 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). The 1.6.41 → 1.6.42 update was never checked by hand either.
3. **A fresh NLTK download:** NRC and SentiWordNet once with an empty `~/nltk_data`, so `punkt_tab` and `averaged_perceptron_tagger_eng` download (every run so far reused data already on disk).
4. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

Ask students who report update problems to send the update log (item 2) to coralynn.yang@emory.edu.

## Before the 1.6.44 tag: dead files and bundle size

Both change what the build ships, so they go out together. Most of it is on `spike/1.6.43-bundle-size-rc` (13 Nov, 16 commits): TensorFlow and 14 unused requirements dropped (§2.2, §2.3), the spec trimmed to the menu (§2.1), TIPS recompressed (§2.4), `setup_Windows/`, `setup_Mac/` and `src/requirements*.txt` deleted (108 Dependabot alerts), transformers 4.41.2 → 4.51.3 (7 alerts), `requests` out of every window's start-up and two timeouts (§6.3, §6.6), the welcome redirect before `import GUI_util` (§6.7), build-workflow checks, and the actions on Node 24 (the "Node.js 20 is deprecated" warning). A CI build of it was 775 MB (Mac) and 863 MB (Windows), against 1,332 and 1,541 MB for 1.6.43.

1. **Rebase the branch on `roberto`, dropping `bea9d173`** (the copy #1733 merged). A trial merge on 18 Nov conflicted in 11 files: 8 in `src/` (mostly that commit; `GUI_util.py` may also clash with the `requests` change), plus CHANGELOG, PLAN and future-work. Its CHANGELOG section becomes 1.6.44's; drop the copy bullet that 1.6.43 already shipped. Rename the branch (`release/v1.6.44` once ready).
2. **PR #1706** (§1.1): the dead `src/*.py` modules the branch leaves alone. Rebase it onto the result, dropping what the branch already deletes; Roberto agrees to the deletions first.
3. **Fix `bundle_gate.py`'s two false alarms** (§14): set `DO_NOT_TRACK` in its `_env`, and ignore CustomTkinter's "application has been destroyed" at shutdown. Small, test-only; do it first, since every check below uses the gate.
4. **Checks on a candidate** (`build-installers.yml`, workflow_dispatch on the release branch):
   - `bundle_gate.py` against 1.6.43 on the Mac zip (`DO_NOT_TRACK=1`). The spec trim is what the gate's menu-archive check is for.
   - The HW 5 sweep (`qtm446/assignments/hw5/hw5_suite_run.py`) on the candidate's own `python-env`: transformers moves to 4.51.3 under BERT sentiment and Shape of Stories, mid-HW 5. Use the 60-document sample for Shape of Stories (under 50 documents it asks "TOO FEW!", which silent mode answers No).
   - §2.5: zip sizes on both OSes; the menu from each zip; one tool per family on `python-env` (BERT NER, BERTopic, coreference with fastcoref, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart).
   - The self-updater 1.6.43 → 1.6.44: the first update that drops files from the release (`NLP_Suite_previous` holds them until the next start).
5. **The release job is untested until the tag:** the Node 24 commit moves `download-artifact` and `action-gh-release` too, which only run on a tag. If the release job fails, the zips are still in the run's artifacts; rerun the job or attach them by hand.
6. Re-sync the dev env before testing: `pip install -r requirements.txt -r requirements-mac.txt --upgrade` in NLP310 (on 17 Nov it had transformers 4.51.3 although `requirements.txt` pins 4.41.2).

HW 5 is due Sun 6 Dec: tag 1.6.44 after that unless the checks are clean well before, so students do not take a large update in the middle of the homework.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**1.6.45 (proposed): the Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs #1706 merged first (1.6.44).

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
