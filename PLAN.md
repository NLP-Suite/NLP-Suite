# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 22 Nov 2026. v1.6.45 released 22 Nov (the HW 5 speedups). v1.6.44 released 21 Nov (tagged on `current-stable` at `140672db`). v1.6.43 released 18 Nov. Releases are now Cora's (handed over by Roberto).

## Now: 1.6.45 (HW 5 speedups) is out

1.6.44 changes only what the build ships (smaller zips, faster window opening, transformers 4.51.3, copy); the dead files and the HW 5 speedups are separate releases, so a regression points to one of them. HW 5 is due Sun 6 Dec: students who update mid-homework get the same tool code as 1.6.43 (the HW 5 sweep matched it step for step). 1.6.45 (the speedups) is on `roberto`.

Still to check on 1.6.43, on the published zips:
1. **Windows:** one Shape of Stories run with Hierarchical Clustering ticked (the default); NRC and SentiWordNet; #1705's start-up popups (menu with an empty `config/`, each Setup GUI); the first Stanza download (#1704).
2. **Update a real 1.6.42 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). The 1.6.41 → 1.6.42 update was never checked by hand either.
3. **A fresh NLTK download:** NRC and SentiWordNet once with an empty `~/nltk_data`, so `punkt_tab` and `averaged_perceptron_tagger_eng` download (every run so far reused data already on disk).
4. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

Ask students who report update problems to send the update log (item 2) to coralynn.yang@emory.edu.

**Checked on 1.6.44 before the tag.** Run 44956055378 (21 Nov, commit `387b9ec2`, version and CHANGELOG heading set) built both zips: the Mac zip is 721 MB (1.6.43: 1,332); the Windows download from the run is 772 MB (1.6.43 zip: 1,541; the zip inside not measured).

On the Mac zip (21 Nov):
- `bundle_gate.py` against the published 1.6.43: unzipped 4,417 → 2,227 MB (`python-env` 3,226 → 1,783, `_internal/` 831 → 148). Every GUI that built still builds, no new popup at opening, the frozen menu starts with no new traceback; about 30 GUIs no longer load IPython, h5py, ipywidgets and the like when they open. 3 FAILs, all expected: `SPARQLWrapper`, `gmaps`, `googlemaps` no longer import, and only the dead `knowledge_graphs_DBpedia_util_SPARQL` and `GIS_heatMapIntegration*` use them (§1.1; nothing references those modules). They go away with the dead files. 3 REVIEW notes (`stanza`, `huggingface_hub`, `pdfminer` reachable from the menu, not in its archive): the spec excludes them on purpose, and they are imported only inside functions that tools call on `python-env`.
- The HW 5 sweep on each zip's own `python-env` and JRE, the 60-document sample, every job (sa, sa_star, sa_to_sos, sos, sos_csv, style, wordnet), 1.6.43 against the candidate: all 40 steps have the same status and file count, and about the same time (37 min each). Output contents: 127 csvs identical, and every difference explained. BERT scores move by at most 4e-6 (transformers 4.51.3), with no label changed, which moves one best-k dispersion coefficient in the 4th decimal (k = 10). One Character Emotion Arcs row names "Elliot" where 1.6.43 had "Lady Elliot", with the same scores. Language detection's langdetect confidence and lexical diversity's vocd-D sample at random, so they differ run to run. CoreNLP's speed assessment is timing. Shape of Stories' cluster csvs differ only in output paths. VADER in Shape of Stories is EMPTY on both (not offered since 1.6.43).
- By hand: the menu, Setup external software and the welcome screen open.
- The tools on transformers that the sweep does not reach, each zip on its own `python-env`, same sample: BERT NER (all tags) and fastcoref coreference give identical output on both zips (64 files, apart from output paths). BERTopic stops on both zips the same way with documents whole (a bug that predates this release: future-work §10); with "split documents" on, it runs on the candidate.

Still to check on 1.6.44, on the published zips:
1. **Windows:** the menu from the zip, and one tool per family on `python-env` (§2.5: BERT NER, BERTopic, coreference with fastcoref, a CoreNLP parse with the bundled JRE, a GIS map, wordclouds, an Excel chart). Nothing has been checked on Windows since 1.6.42.
2. **The self-updater 1.6.43 → 1.6.44 on Windows.** *(Mac done 22 Nov: the published 1.6.43 zip's own `update_zip_install`, on its `python-env`, its dialogs answered Yes by a driver, against the live release. Downloaded, unpacked and swapped in 8 s; the new folder is a clean 1.6.44 file for file plus the added word list, corpus folder, config file and changed config line; the files 1.6.44 dropped are gone; `remove_previous_version` deleted `NLP_Suite_previous`. Not exercised: the real close-and-Yes click, and the deletion through a menu start, since the welcome screen of a first launch waits for a click before the menu runs.)*
3. *(Done: the release job passed on the Node 24 actions, run 44965238993; the zips are 721 MB (Mac) and 790 MB (Windows). The size line in the release notes was corrected by hand from the 13 Nov test build's numbers.)*
4. Mac, not run: a GIS map and wordclouds (their code did not change; `bundle_gate.py` checked their imports).

Then delete `spike/1.6.43-bundle-size-rc` and its fork copies, and the local `backup/release-v1.6.44-with-dead-files`.

**Checked on 1.6.45 before the tag** (22 Nov, run 45065397429 on `release/v1.6.45`, Mac zip). Only the seven `src` files of #1734, #1735 and #1736 differ from 1.6.44, and `python-env` has the same 184 packages at the same versions, so the full HW 5 sweep was not rerun: `sa` and `sos` on the 60-document sample, each zip on its own `python-env` and JRE. Every step has the same status and file count. 107 of 111 csv and Excel outputs are identical; best k's `best_topic_estimation_stats.csv` (BERT, spaCy, Stanza) differs by at most 9e-15; Character Emotion Arcs differs only in which of a sentence's characters comes first and "Lady Elliot"/"Elliot" in one row, with the same scores (set order, as on 1.6.44). Shape of Stories took 6.7 min (1.6.44: 12.6). CoreNLP steps are EMPTY on both (no CoreNLP path in a fresh unzip's config). `bundle_gate.py` against 1.6.44: 0 failures, sizes unchanged (menu archive not listed: no PyInstaller in NLP310). Zips 756 MB (Mac) and 810 MB (Windows).

Still to check on 1.6.45: the self-updater 1.6.44 → 1.6.45 on the published zips (Mac, then Windows), and the speedups on the 958-document corpus. Dev env: re-sync with `pip install -r requirements.txt -r requirements-mac.txt --upgrade` in NLP310.

Next: the dead files (§1.1, #1706), then 1.6.46.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**Maybe trim the spec further** (§2.1): it keeps spaCy, pandas and the rest for the language advisor, which since #1732 runs on `python-env` instead. Probe build first.

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
