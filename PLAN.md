# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 18 Nov 2026. v1.6.42 released 17 Nov. Releases are now Cora's (handed over by Roberto).

## After the 1.6.42 tag

1.6.42 is the first release that students' copies install by themselves (1.6.41 → 1.6.42), so the updater gets its first real, full-size run. It ships #1704, #1705, #1711, #1712, #1714, #1715, #1716 and #1726.

Checked on the 17 Nov release candidate (Mac, macOS 26.5.2): both zips hold the entry point, `lib/release_manifest.tsv` and the default `config/`; the app opens; Shape of Stories, Sample corpus and Wordclouds open; the first RUN creates `NLP_output`; the first Stanza download works (it crashed the first candidate: #1725, fixed by #1726).

1. **Not checked on Windows before the tag:** #1705's start-up popups (menu with an empty `config/`, each Setup GUI) and #1704's first Stanza download. Do both on the released Windows zip.
2. **Update a real 1.6.41 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). This is the first full-size run; the 9 Nov test used a 26 MB stand-in release on localhost.
3. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

## Before the 1.6.43 tag

1.6.43 is everything QTM 446W's HW 5 (due Sun 6 Dec) needs, in one update: the Stanza GUIs that closed as they opened on a new install (#1728), the language advisor (#1731), the HW 5 tool fixes (#1718–#1724 and #1549, merged from `spike/1.6.44-hw5` on 18 Nov), the links and copy of #1733, Shape of Stories opening without an "Input directory error", and `NLP_SILENT` covering the timed alerts. Nothing in it changes what the build ships (the one requirements change is a `scikit-learn>=1.2` floor that resolves to the same version). It is on `release/v1.6.43` (version bump and CHANGELOG heading included).

**Checked on 17 Nov (Mac):** `pytest tests/` 778 passed, and the CI-like run (pytest only, Python 3.10) 728; `gui_smoke.py` 0 crashed. A candidate built from `release/v1.6.43` before its last commit (run 44218077157, both OSes green) passed `bundle_gate.py` against 1.6.42, with the last commit's two files copied into its `src/`: 12 of the 13 GUIs that closed on a new install in 1.6.42 now open (`NLP_setup_IO_main` exits by design); no import or GUI lost. The HW 5 sweep passed on that candidate's own `python-env` (transformers 4.41.2, Stanza 1.15.1, torch 2.14.1: not the versions of the dev env, which has transformers 4.51.3): every sentiment algorithm, language detection, and Shape of Stories with BERT, spaCy and Stanza through HC, SVD, NMF and best k (60 documents). CoreNLP ran in the dev env only (the candidate's fresh `config/` has no CoreNLP folder).

Not checked, before or after the tag:
1. **Windows:** one Shape of Stories run from the Windows zip with Hierarchical Clustering ticked (the default); NRC and SentiWordNet.
2. **A truly fresh install:** the sweep used a home folder that already had NLTK data, so the `punkt_tab` and `averaged_perceptron_tagger_eng` downloads did not run. Try NRC and SentiWordNet once with an empty `~/nltk_data`.
3. **The tagged build itself:** it is built fresh from the tag; run `bundle_gate.py` on it against 1.6.42 (set `DO_NOT_TRACK=1`, see future-work §14).
4. The 1.6.42 checks above that are still open.
5. After the promotion to `current-stable`, check that #1718–#1724 and #1549 closed (the merge commit says `Fixes` for each); close any that did not.

Ask students who report update problems to send the update log (item 2 above) to coralynn.yang@emory.edu.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**1.6.44 (proposed): dead files and bundle size.** Both change what the build ships, so they go out together, after 1.6.43. Most of it is already on `spike/1.6.43-bundle-size-rc` (13 Nov): TensorFlow and 14 unused requirements dropped, the spec trimmed to the menu, TIPS recompressed, the setup scripts deleted, transformers 4.51.3, and §6.3, §6.6 and §6.7; a CI build is 775 MB (Mac) and 863 MB (Windows). To ship it: rebase on `roberto` dropping `bea9d173` (#1733 merged the same copy), run `tests/bundle_gate.py` against 1.6.43, and rename the branch.
- PR #1706 deletes the legacy setup scripts and unused files (§1.1). Rebase it on `roberto` first; it conflicts with #1705 in `README.txt` and `CLAUDE.md`. Deleting `src/requirements*.txt` also closes 108 of the 178 Dependabot alerts (§3.1).
- Drop TensorFlow, which nothing imports (§2.2), then trim `NLP_Suite.spec` to what the menu needs (§2.1), and remove the requirements that nothing imports (§2.3).

**1.6.45 (proposed): the Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs #1706 merged first (1.6.44).

**Later, unscheduled:**
- Smaller copy left over from #1705 (§5.2), and the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Retest and close the recent issues that releases may have fixed; fix the open recent bugs (§10). Triage the 2021–2024 backlog (§11).
- Performance, in §6.10's order (next: pandas and requests out of `GUI_util`, §6.3).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, and the silent `git stash` (§15).
- The GitHub wiki: make `docs/` the source, then publish (§8).
- UI overhaul (§7), as its own releases.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13): delete Cora's merged ones; the others are Roberto's call.
