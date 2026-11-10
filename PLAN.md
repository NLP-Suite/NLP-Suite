# PLAN — NLP Suite open work

What's open, what to close, what to fix next. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md), not here.

**Last updated:** 9 Nov 2026, for release 1.6.41 (v1.6.40 released 7 Nov).

**State on GitHub (9 Nov 2026):** 12 open PRs before the 1.6.41 merges; 255 open issues on 7 Nov, plus #1700. Nothing below has been merged, closed or commented on GitHub: the lists are proposals for Roberto.

## Contents

1. [Release 1.6.41](#1-release-1641)
2. [Next steps after 1.6.41](#2-next-steps-after-1641)
3. [Open pull requests](#3-open-pull-requests)
4. [Recent issues (2025–2026)](#4-recent-issues-20252026)
5. [The 2021–2024 backlog](#5-the-20212024-backlog)
6. [Tech debt](#6-tech-debt)
7. [Requirements, release checks and settled decisions](#7-requirements-release-checks-and-settled-decisions)
8. [Branches](#8-branches)
9. [Performance: slow GUI opening and "downloading"](#9-performance-slow-gui-opening-and-downloading)

---

## 1. Release 1.6.41

A patch release whose top priority is auto-update (issue #1700). **State (9 Nov 2026):** everything below is merged on `roberto`; `lib/release_version.txt` and CHANGELOG say 1.6.41. **Not yet promoted to `current-stable` or tagged** (Roberto's step, §1.4). What each change does is in CHANGELOG v1.6.41.

### 1.1 In 1.6.41

| What | How it got in |
|---|---|
| #1701 auto-update without pygit2 | Merged; plus a fix: `.git` is rebuilt only when git says it is damaged, never on "dubious ownership", a lock or a timeout |
| #1702 the zip build updates itself | Merged; plus the review fixes (next row) |
| #1702 review fixes | An unmarked `<folder>_previous` is never deleted (checked before the download). The build writes `lib/release_manifest.tsv` (path, size, hash) as its last step before zipping, and the updater uses it to carry over the user's files at any depth and to keep the backup when a release file was edited. A failed rollback says where the app is. A partial backup deletion is finished next start. A swap script that never starts (group policy) is reported. Silent failures became messages. Typographic quotes in paths. OneDrive warning |
| Launch popup and offline check | No popups offline. The "Outdated" message fits the install (zip vs Git) and waits until the zip download exists |
| pygit2 leftovers | Removed from the missing-module message |
| #1699 GIS geocode cache | Merged as is |
| #1679 CoNLL DEPREL filter, #1656 nominalization batching | Re-applied on the ruff-formatted `roberto` (their conflicts were only the reformat); author kept |
| Homework 4 tool fixes | See §1.1a |

Tests on Windows: the updater's PowerShell swap runs for real in `pytest` (normal update, unmarked `_previous`, marked one, an edited release file, a folder named with ’ and brackets); the Mac `sh` swap was run the same way under Git's `sh` (CI runs it on Linux).

### 1.1a Homework 4 tools, checked end to end (9 Nov 2026)

Run unattended on Windows (NLP env, CoreNLP 4.5.6, Java 20) on `The Three Little Pigs.txt` and a 2-document newspaper corpus: SVO with CoreNLP (with and without coreference), spaCy, Stanza and '*'; lemmatized/filtered SVO, WordNet, Sankey/sunburst/treemap, wordclouds, Gephi .gexf (ISO dates), GIS from SVO and from GIS_main (Nominatim, Folium pin/heat/time maps, .kml), the new geocode cache. All work. Fixed in 1.6.41 and rerun: the GIS long-path crash, '*' comparisons overwriting each other, SVO-csv-input outputs landing beside the input, console prints crashing on cp1252. `pytest`: only the 2 known local failures. Not covered: Google geocoder and Google Earth Pro (no API key), OpenIE, Mac.

Open, not blocking (for after 1.6.41):
- `GIS_geocode_util.py` ~704: the "(NER tag: ...)" log line prints the date when there is one; the tag used is `item[2]`.
- CoreNLP's main SVO csv is already lemmatized, so `SVO_lemma` is identical to it, and no unlemmatized csv is written (only the form charts).
- Stanza downloads `resources.json` on every run, so it needs internet.
- Geocoding quality, not code: Nominatim puts "Flushing" in the Netherlands; spaCy tags names like "Campari" as places.
- `tests/gui_smoke.py` hangs in a checkout with no `config/` folder: a setup GUI opens as a real window and waits. Make the smoke run create or stub the config.

### 1.2 Not in 1.6.41

- **PR #1688** (Python 3.11 + Pillow 13): changes the build Python for every user. Its own release, after auto-update is proven.
- **PR #1682** (spaCy CoNLL ID/HEAD): correct, but changes a shared CoNLL structure. First thing after 1.6.41 (§3).
- **PR #1683** (gender dictionary): needs changes (§3).
- Backlog triage (§5) and tech debt (§6).

### 1.3 Known limits of the updater (open, not blocking)

- **Long paths:** staging is 17 characters deeper than the install; without Windows LongPathsEnabled the deep `node_modules` paths (#1653) fail to unpack. Fails safely with a message. Fix with #1653.
- **The first real self-update is 1.6.41 → 1.6.42.** 1.6.40 and older don't have the code.
- No checksum (GitHub's asset `digest` is unused) and no resume of a broken download. Ctrl-C during the download leaves `_update` behind, which blocks updates for 24 h (the message now says which folder to delete).
- GitHub allows 60 unauthenticated API calls an hour per IP; on a shared campus network the exit-time release lookup can get 403. The fallback is the download page with the reason.
- The Git update on `current-stable` still runs `git add -A` + `git stash`, so local edits go into a stash silently (unchanged behaviour).
- A release file the NLP Suite itself rewrites at run time would keep the backup every time; none is known. Watch the first 1.6.42 update logs (`%TEMP%\NLP_Suite_update.log`).

### 1.4 Before promoting and tagging (Roberto)

1. **Hand checks on Windows** (CI can't do these):
   - One real self-update with the app open, using the PR's steps: build or unzip a release, replace its `src/` with `roberto`'s, write a manifest (`python -c "import sys; sys.path.insert(0,'src'); import NLP_setup_self_update_util as u; u.write_manifest('.')"` in that folder), set `lib/release_version.txt` to 1.6.40, start with `python-env\python.exe src\NLP_menu_main.py`, close, accept. Until 1.6.41's zips exist the updater has no newer release to fetch, so do this right after tagging, against 1.6.41 itself.
   - A source checkout on `current-stable` updates with git; one on `roberto` is left alone.
   - Offline: open and close a GUI with the network off; no popups.
2. Promote `roberto` → `current-stable`; tag `v1.6.41` on that commit. CI checks `lib/release_version.txt` = tag and that the file list has over 1,000 files. Then the usual artifact check (§7), plus: `lib/release_manifest.tsv` is in both zips.
3. **Tell students once:** they must download 1.6.41 by hand (CHANGELOG's first bullet says how). Course announcement too.

## 2. Next steps after 1.6.41

In order:

1. **Close the four stale 2024 PRs** (§3) with a short thank-you comment.
2. **Merge #1682 after a rebase; send #1683 back with the review; decide #1688** (§3).
3. **Retest and close the recent issues that releases may have fixed** (§4, "Retest" rows).
4. **Fix the open recent bugs** (§4, "Bug" rows), one branch and test each, per CLAUDE.md.
5. **Triage the 2021–2024 backlog** (§5). Proposal: bulk-close the stale ones with a comment inviting a reopen.
6. **Burn down tech debt** (§6) in the listed order.
7. **Add the missing regression tests**: an empty-DataFrame test and a multi-column chart test for `charts_util` (§6.6).

## 3. Open pull requests

Reviewed 9 Nov 2026. #1701, #1702 and #1699 are merged into `roberto` (GitHub marks them merged once `roberto` is pushed). The older PRs conflicted only because v1.6.40 reformatted all of `src/` (PR #1687).

"Tests" = the PR's own new tests, run on Windows in the NLP env on 9 Nov.

| PR | Opened | What | Merge | Tests | 1.6.41? | Review |
|---|---|---|---|---|---|---|
| #1679 | 10-14 | CoNLL search DEPREL filter | — | 4 pass | **In 1.6.41** (re-applied) | Close on GitHub by hand, pointing to the re-applied commit: its own commits were not merged. Keep #1561 open until its crash is reproduced |
| #1656 | 09-15 | Nominalization: one batched tagging call per document | — | 11 pass | **In 1.6.41** (re-applied) | Close on GitHub by hand, as #1679 |
| #1682 | 10-16 | spaCy CoNLL ID/HEAD sentence-level and 1-based | Conflict: ruff only, mechanical | 2 pass | No: after 1.6.41 | Correct: Stanza and CoreNLP already write 1-based, sentence-level, root 0, and no reader compensates for spaCy's old values. Shared structure, so not in a release about the updater. spaCy tables already on disk stay 0-based: say "re-parse" in the CHANGELOG |
| #1683 | 10-16 | Gender dictionary looks up only PERSON tokens | Conflict: ruff only | 5 pass | No | **Needs changes:** hardcodes `Stanford_CoreNLP_util.CoreNLP_annotate` whatever parser is configured (so the option now needs Java); returns `''` with no message when no NER csv comes back; once "Will" is a PERSON anywhere, every "will" is tagged |
| #1688 | 10-26 | Python 3.11 build so Pillow can go to 13.0.0 | Conflict: 2 adjacent lines | CI only | No (§1.2) | Decide. Whole pinned stack must rebuild on 3.11. STEP2 scripts still create `python=3.8` envs (`setup_Windows/STEP2-install_NLP-Suite.ps1:12`, `setup_Mac/STEP2-install_NLP-Suite.command:35`) and `pyproject.toml`/`pyrightconfig.json` say py310; the PR touches none of them |
| #1528 | 2024-09 | "dictionary functionality" (CallaGong) | — | — | No | **Close**: targets `current-stable`, 2 years old |
| #1525 | 2024-09 | Generalized Excel file reads (esunn0412) | — | — | No | **Close**: targets `current-stable`, 2 years old |
| #1436 | 2024-03 | Document Statistics sentence-length fix (razzak-ammar) | — | — | No | **Close**: check first that v1.6.39's sentence-statistics rewrite fixed it |
| #1383 | 2024-01 | Alternative STEP2 install script (Eli-Todd) | — | — | No | **Close**: install was rebuilt around PyInstaller |

All 2026 PRs are by coralynnkc and target `roberto`.

#1651 (CustomTkinter migration of all GUIs) was closed on 9 Nov without merging.

## 4. Recent issues (2025–2026)

"Retest": a later release says it fixed this or something close. Rerun on v1.6.40 and close if it's gone.

| # | Title | Kind | Note |
|---|---|---|---|
| 1700 | Auto-update fails on most student machines: asks for pygit2 | Bug | Fixed in 1.6.41 (§1). Close when 1.6.41 is tagged |
| 1671 | BERT word embeddings are context-free | Design | Each word is encoded alone, so vectors don't depend on the corpus. Affects a homework question. Decide: keep, document, or encode in context |
| 1653 | Windows zip: JavaScript paths too long under `AppData\Local\Programs` | Bug | MAX_PATH in bundled node_modules. Shorten in the build or document the install location. Also matters for the self-updater's `_update` folder |
| 1623 | Boxplot: asks for an option but none appear | Bug | |
| 1620 | pdf → txt converter error | Retest | v1.6.34 fixed several pdf → txt faults |
| 1619 | Selecting a new input file/directory (pdf converter) | Bug | CANCEL path in the I/O setup |
| 1616 | Progress indicator never shows "complete" | Bug | All tools |
| 1614 | GIS country-bias list has only 2 countries | Bug | |
| 1609 | Parser runs but writes nothing | Retest | Needs a reproduction |
| 1607 | CoNLL Table Analyzer RUN does nothing | Bug | No error shown, so it breaks the no-silent-failures rule |
| 1606 | Gensim Word2Vec error | Retest | v1.6.39 fixed Gensim Word2Vec with Lemmatize |
| 1604 | Style analysis error after update | Check | The error is a JSON "detail" message, possibly from a web runner, not this repo |
| 1603 | Google Earth GUI: "Icon for group of values" not implemented | Bug | Values passed but unused in `GIS_pipeline_util` |
| 1599 | PC-ACE analyzer: complex-object frequencies count identifiers | Enhancement | |
| 1598 | Data visualization 1: colormap/heatmap error on SVO csv | Bug | |
| 1593 | Sentiment Analysis GUI fails to open | Retest | Run `tests/gui_smoke.py` |
| 1592 | Readability: negative grade level ("-1th grade") | Bug | Clamp or label below grade 1 |
| 1589 | SVO + CoreNLP coreference error (Mac M2) | Retest | v1.6.40 fixed SVO-with-coreference crashes |
| 1582 | Deprecated `encoding='utf-8', strict=True` warning | Bug | Small |
| 1579 | CoNLL Table Analyzer works only on CoreNLP tables | Enhancement | Extend to Stanza and spaCy. Related: PR #1682 |
| 1575 | WSI output: csv extension, chartable | Enhancement | v1.6.39 fixed the WSI crash, not the output format |
| 1573 | Normalize punctuation frequencies | Enhancement | |
| 1566 | Excel "by Document" charts: no Document ID, no hyperlink | Enhancement | |
| 1564 | Search words by document: chart and word label | Enhancement | 4 comments |
| 1561 | CoNLL analyzer passive verbs: wrong DEPRELs in output | Bug | Possibly the DEPREL filter fixed by PR #1679 |
| 1560 | Bubble chart problem (Mac M2) | Bug | |
| 1558 | utf-8 problem in n-grams VIEWER output (Mac M2) | Bug | |

## 5. The 2021–2024 backlog

229 issues, #44 to #1551. 164 have no comments. 119 were opened by `Emory-NLP` (Roberto's own notes).

| Labels | Count |
|---|---|
| none | 118 |
| enhancement | 65 |
| bug | 22 |
| bug + student-bug | 20 |
| help wanted | 3 |
| OS X + bug | 1 |

Since then the code has had a full RUN-button rewrite (v1.6.2), a chart-engine rewrite (v1.6.3) and a format pass (v1.6.40). Many of these reports describe code that no longer exists.

**Proposal (needs Roberto's yes):**
- **Bugs (43):** close as stale with a comment: "Closing as part of a backlog cleanup; much of this code was rewritten in 2026. If it still happens on v1.6.40 or later, please reopen with the steps." Keep any Roberto marks as still real.
- **Enhancements and unlabelled `Emory-NLP` notes:** Roberto skims and keeps the ones still wanted. Add the kept ones to §4 or to a `wishlist` label, and close the rest.
- **Other unlabelled reports:** treat as bugs.

To do this with `gh` (needs a login): `gh issue close N -c "<comment>"`. Without a login, use the GitHub web UI.

## 6. Tech debt

Re-measured 7 Nov 2026 with Ruff 0.16.0 over `src/` (221 files). The 16 Jul figures are in brackets.

### 6.1 Latent crashes: undefined names (F821): 44 [68]

Most of the remaining 44 are in rarely used tools:

| File | Count |
|---|---|
| `syntactic_analysis_ALL_main.py` | 6 |
| `GIS_file_check_util.py` | 5 (`np`, `numColumns`, `msgTooFewColumnsForGeocoded`) |
| `Gephi_util.py` | 5 (`attvalue_xml`, `type_choices`) |
| `CoNLL_function_words_analysis_util.py` | 5 (`stats_pronouns` …) |
| `IO_files_util.py` | 3 (§6.2) |
| 13 more files | 1–2 each |

Full list: `ruff check src/ --select F821`.

### 6.2 Error handler that crashes: `IO_files_util.py` ~line 292

In the filename-date sort's `except:`, `date_location` is undefined, so a filename with an unparsable date raises `NameError` instead of printing the "non fatal" notice. The same file also has `gatherCLAs()` (~line 1640), which uses `argparse` without importing it. Delete it or fix it.

### 6.3 Silent failures: 215 bare `except:` [221]

Largest reliability lever. Convert to `except Exception`, and on user-facing paths report via `messagebox`. Worst files in July: `IO_files_util`, `GIS_geocode_util`, `file_filename_util`, `charts_util`, `Stanford_CoreNLP_util`.

### 6.4 Wrong-result risks

- **Late-binding closures in loops (B023): 8.** `statistics_csv_util.py` (`col`, `df`/`currentColumn`, `temp_str`), `CoNLL_k_sentences_util.py`, `charts_Plotly_util.py`, `charts_util.py`. Verify each, then bind at definition (`lambda col=col: ...`).
- **Mutable default arguments (B006): 47.** Mechanical fix.
- **Shadowed redefinitions (F811): 5** [37].

### 6.5 Fragility

- `eval()` (S307): 6. In `charts_Plotly_util.py`, `charts_util.py` and `hashfile.py`. Replace with `ast.literal_eval` or explicit parsing.
- `subprocess(..., shell=True)` (S602): 9. Breaks on paths with spaces. Use argument lists.

### 6.6 Tests

Coverage is 508 test functions in 52 files [3]. Gaps:
- No **empty-DataFrame** regression test for the chart/statistics pipeline (only `test_emotion_arc_html.py` covers an empty frame).
- No **multi-column chart** regression test for `charts_util` (the v1.6.4 "by Document" grouped-bar fix has no test).

### 6.7 Hygiene

- Unused variables (F841): 498. Unused imports (F401): 1 [290]. Invalid escapes (W605): 0 [80].
- Tab-indented lines remain in 2 files.
- Large modules (lines): `DB_PCACE_data_analysis_util` 7,731 · `charts_util` 5,620 · `corpus_profiler_util` 4,191 · `Stanford_CoreNLP_util` 3,563 · `statistics_txt_util` 3,033. When you open one for a feature, pull testable helpers out instead of adding in place.
- About 900 `print()` calls. Move to `logging` over time.

**Order:** §6.2 → F821 file by file → bare excepts on user paths → B023 → B006 → eval/shell.

## 7. Requirements, release checks and settled decisions

- **coreferee** is gone from `requirements.txt` (it pins `spacy<3.6` and broke the PyInstaller build). `fastcoref` replaces it. Don't re-add it. spaCy is unpinned.
- **pygit2** is no longer a requirement (1.6.41): the source-checkout updater uses the `git` program. Don't re-add it.
- **`lib/release_manifest.tsv`** is written by the build's last step before zipping (1.6.41). The self-updater relies on it to tell the user's files from the release's: any step that adds files to `dist/` must come before it.
- **Pillow** is pinned to 10.4.0 (12.x breaks the bundled Tcl/Tk 8.6). PR #1688 tests Python 3.11 + Pillow 13 for the security advisory; after 1.6.41 (§1.3).
- **CI Python:** 3.10 for tests and installers. SRL stays on its own 3.8 env.
- **Mac runners:** `macos-15` since 2 Nov 2026 (`macos-14` retired). No Intel Mac build.
- **`src/` is Ruff-formatted** (v1.6.40). PRs opened before that need a rebase, not a hand merge.
- **Update order matters.** The in-app check reads `current-stable`'s `lib/release_version.txt`, which changes before the tag's zips finish building. The self-updater and the launch popup both wait until that version's zip is on the release page.
- **Before every tag:** build, unzip both artifacts, confirm `Launch NLP Suite (Mac).command` and the Windows entry point exist, confirm the app imports, then draft the CHANGELOG section. `lib/release_version.txt` must equal the tag (CI enforces it).

## 8. Branches

Remote branches besides `roberto`, `current-stable`:

- `cora-batch-2` (30 Oct 2026): collaborator staging, holds a merge of #1699. Not in `roberto`.
- `mac-font-pin` (22 Jul 2026): not in `roberto`, no open PR. Check whether it's still needed.
- `dictionary` (Sep 2024), `taeeun` (Dec 2024): heads of stale PRs #1528 and #1525. Delete after those PRs are closed.
- `remove_shortcut_prompt` (2021), `tony` (2023): no open PR. Delete candidates.

Deleting a remote branch is Roberto's call.

## 9. Performance: slow GUI opening and "downloading"

Evaluated 9 Nov 2026 on `current-stable` @ `43cbca1c` (v1.6.40), Windows 11, NLP env (Python 3.10), warm disk, good connection. Nothing in the code was changed; this section is findings and proposed fixes, ranked.

**Not measured:** the installer (zip) build and its bundled `python-env`; macOS; a cold start after a reboot; a first-time model download; the speed of the analyses themselves after RUN (§9.9 is read from the code only).

**How it was measured.** `python -X importtime -c "import GUI_util"`; each third-party library imported alone in a fresh process; for every `*_main.py`, the libraries it reaches through module-level imports (followed through the local `src` modules, including the `install_all_Python_packages` lists) imported together in one fresh process; `stanza.download("en")` and the Stanza pipeline timed with the model already on disk; `import Stanza_functions_util` and `import statistics_txt_util` run for real. The per-GUI figures in §9.2 are import cost only, from that static trace: no GUI window was opened and clicked.

### 9.0 Summary

| # | Finding | Measured cost | Who pays | Fix size |
|---|---|---|---|---|
| 1 | Stanza model re-checked (and a pipeline built) every time a GUI opens. **Fixed on branch `claude/codebase-performance-eval-09cb55`, not yet merged (§9.1)** | 9–11 s per check, 8.7 s for the pipeline | 18 of 55 GUIs | Small |
| 2 | Heavy libraries imported when the GUI opens, not at RUN | 10–40 s | 32 of 55 GUIs | Medium, file by file |
| 3 | Every GUI starts with 4.6 s of `GUI_util` imports (pandas, requests) | 4.6 s vs 0.9 s for a bare Tk window | Every GUI, every open | Small |
| 4 | "Started/Finished running" alerts and reminders block until their countdown ends | 1–12 s each | Every RUN | Small (a decision first) |
| 5 | Fixed `time.sleep` calls freeze the GUI | 5–10 s each | Config-file edits, CoreNLP, spell checker | Small |
| 6 | Version check on the main thread on every GUI open; other web calls without a timeout | 0.1 s here; up to ~16–18 s on a blocked or dead network | Every GUI | Small; overlaps §1 |
| 7 | First three launches start three Python processes before the menu shows | about 3 × 4.6 s | New users | Small |
| 8 | Menu runs `java -version` (and `pip freeze` on Apple Silicon source installs) at every start | Not measured | Menu | Small |
| 9 | Row-by-row pandas loops in the analyses | Not measured | RUN on large corpora | Profile first |

Findings 1–3 are where the opening time goes. Adding up the measured parts, a GUI such as Style analysis takes an estimated minute or more to open (4.6 s base + 29 s of libraries + three model checks + the pipeline; not timed end to end) and should drop to a few seconds; the menu and the light GUIs should drop from about 5 s to about 1.5 s.

### 9.1 The Stanza model is re-checked every time a GUI opens (the "downloading")

Four modules call `stanza.download("en")` at import time, i.e. when a GUI that uses them opens, not when RUN is clicked:

- `src/Stanza_util.py:43` (it tests whether `~/stanza_resources/en` exists at line 33, then downloads regardless)
- `src/Stanza_functions_util.py:39`, and line 42 then builds `stanza.Pipeline(lang="en", processors="tokenize, lemma")`
- `src/statistics_txt_util.py:34`
- `src/wordclouds_util.py:34`

With the model already on disk, each call still takes **9.1–10.7 s**: Stanza fetches its resources list from GitHub and re-hashes the model files. Building the pipeline takes another **8.7 s**. Measured end to end: `import Stanza_functions_util` **33 s**, `import statistics_txt_util` **38.5 s**.

18 of the 55 GUIs import at least one of these modules when they open. Style analysis, Semantic analysis and Syntactic analysis (ALL) import three of them, so they run the check three times.

**Fixed 9 Nov 2026 on branch `claude/codebase-performance-eval-09cb55` (not merged, not pushed).**
1. `IO_internet_util.ensure_stanza_model(...)` downloads only when no unpacked tokenizer model is on disk (`stanza_model_present`: `<resources>/<lang>/tokenize/*.pt` under Stanza's own `stanza.resources.common.DEFAULT_MODEL_DIR`, a per-version cache folder since Stanza 1.10; the first version of this fix looked in the old `~/stanza_resources` and so never found the model). It is called when a tool RUNs (Stanza_annotate, coref, sentence length, wordclouds, the shared pipeline), not at import; the download runs in a background thread behind a window that stays up and shows the MB downloaded (`run_with_progress`). Issue #1703. `Stanza_util`'s bare `except: pass` around the download is gone, so a failed first download is reported.
2. `stanzaPipeLine` is now an `IO_internet_util.LazyModel`: it builds the pipeline the first time it is called and passes the call through, so none of its 156 uses in 28 files changed. A failed build shows the existing download-failure dialog and raises.

Measured after the fix, same machine: `import Stanza_functions_util` 33.0 → **18.5 s**, `import statistics_txt_util` 38.5 → **21.3 s**, `import wordclouds_util` 14.2 s. What remains is library import time (§9.2). The first `stanzaPipeLine(...)` call took 7.0 s, later calls 0.01 s. Checks: 15 new tests in `tests/test_IO_internet_util.py`; `pytest tests/` 613 passed, the same 2 failures as on `roberto`; `tests/gui_smoke.py` 49 ok, 0 crashed, 6 skipped (the usual stub-limited ones).

**Not checked:** a GUI opened and RUN by hand; a machine with no Stanza model (first download); macOS; the zip build. A model folder with a tokenizer but another file missing is trusted at open; `stanza.Pipeline` fetches the missing file when the pipeline is built.

### 9.2 Heavy libraries are imported when the GUI opens

Each `*_util.py` starts with `install_all_Python_packages(...)`, which **imports** every listed package to test that it is installed, and then with module-level imports of the same libraries. A GUI therefore loads everything any of its options might use before it draws.

Libraries alone, fresh process (seconds): `sentence_transformers` 39.5 · `summarizer` 25.2 · `spacy_langdetect` 23.6 · `tensorflow` 21.0 · `stanza` 16.8 · `contextualSpellCheck` 15.0 · `spacy` 14.6 · `seaborn` 11.4 · `transformers` 9.4 · `textblob` 8.2 · `pyLDAvis` 8.1 · `textstat` 7.5 · `nltk` 7.4 · `sklearn` 5.6 · `gensim` 5.2 · `folium` 3.6 · `openpyxl` 3.4 · `pandas` 3.1–3.5.

Library import cost per GUI (all its libraries together, one process; excludes §9.1 and the Suite's own code):

| Cost | GUIs |
|---|---|
| 3–4 s (23) | menu, welcome, NLP_setup_IO, NLP_setup_external_software, DB_SQL, SRL, corpus_profiler, data_manipulation, file_checker_converter_cleaner, file_handler_ALL, file_manager, file_matcher, file_merger, file_search_ALL, file_splitter, html_annotator, knowledge_graphs, narrative_analysis_ALL, nominalization, sample_corpus, semantic_analysis_ALL, sentiments_emotions_ALL, statistics_txt |
| 10–18 s (11) | GIS_symbolic 9.9, GIS_distance 10.6, charts_Excel 10.9, data_visualization 10.9, statistics_csv 10.9, GIS_Google_Earth 11.2, wordclouds 12.8, word2vec 13.2, CoNLL_table_analyzer 13.7, semantic_aggregation 13.7, NGrams_CoOccurrences 17.5 |
| 22–40 s (21) | file_classifier 22.5, sentiment_analysis 22.9, file_checker_pre_processing_pipeline 25.3, topic_modeling 25.4, file_search_byWord 25.5, corpus_checker_PCACE_data 25.9, shape_of_stories 25.9, NER 28.8, SVO 28.9, semantic_analysis 29.1, style_analysis 29.1, syntactic_analysis_ALL 29.1, html_annotator_gender 29.2, sentence_analysis 30.2, coreference 32.0, parsers_annotators 32.0, DB_PCACE_data_validation 33.2, NLP_setup_package_language 33.2, file_spell_checker 38.2, DB_PCACE_data_analysis 38.8, GIS 39.8 |

The GUIs in the first row already import their logic inside `run()`; they pay the cost at RUN instead, which is the right place.

**Fix, in this order.**
1. **`install_all_Python_packages` (`src/IO_libraries_util.py:102`): test with `importlib.util.find_spec(module)` instead of `__import__`.** It answers "is it installed?" without loading the package. One function, every GUI benefits; the existing name mapping (pdfminer, docx, PIL …) stays. Needs a unit test.
2. **Move the heavy imports into the functions that use them**, starting with the modules shared by most GUIs: `Stanza_util`, `statistics_txt_util`, `Stanza_functions_util`, `charts_util` (plotly, numpy), `IO_csv_util` (§9.3). Then the slow GUIs from the bottom of the table up. One PR per module, each with a `tests/gui_smoke.py` run.
3. In each `X_main.py`, import `X_util` inside `run()` where it is not needed to build the window (the pattern the fast GUIs already follow).

### 9.3 Every GUI pays 4.6 s before its own code runs

`import GUI_util` takes **4.6 s** (4.6–5.6 s across three runs); a bare `tkinter.Tk()` process takes 0.9 s. Each GUI is a new Python process (`run_script_util.run_script`), so this is paid on every open, not once per session.

| Part | Time | Why it is there |
|---|---|---|
| pandas | 2.2 s (3.1–3.5 s alone) | `IO_csv_util`, `reminders_util` and `config_util` import it at the top to read a few small config CSVs |
| requests (with urllib3) | 1.3 s | `GUI_util.py:13` and `IO_libraries_util.py:13`, for the release check and three other small GETs |
| Tk window, the rest | about 1.1 s | |

**Fix.**
- `reminders_util`, `config_util`: read `reminders.csv` and the config files with the `csv` module. `getReminders_list` and `checkReminder` each re-read `reminders.csv` with pandas, two or three times per GUI open.
- `IO_csv_util`: `import pandas` inside the functions that need a DataFrame.
- `GUI_util`, `IO_libraries_util`: `import requests` inside the functions that call it (or use `urllib.request`, which `usage_util` already does).

Expected saving: about 3.5 s on every window, the menu included. The menu also imports `customtkinter` (1.4 s), which is needed.

### 9.4 Timed alerts block the run

`IO_user_interface_util.timed_alert` (372 calls in 94 files) calls `GUI_IO_util.message_box_widget`, which ends with `top_message.wait_window()` (`src/GUI_IO_util.py:1384`). The analysis does not start, or the outputs do not open, until the popup closes.

The countdown is also longer than the `timeout` passed: it counts `timeout / 500` seconds, or `timeout / 1500` for "Started running"/"Finished running" messages (`GUI_IO_util.py:1255-1294`). A "2000 ms" alert waits 4 s, a 6000 ms one 12 s, unless the user clicks OK. Reminders wait 30 s.

**Fix (Roberto decides the behaviour):** for OK-type alerts, show the popup and return at once, letting it close itself with `after(timeout, ...)`; make the countdown equal `timeout`. Yes/No reminders must keep waiting for an answer.

### 9.5 Fixed sleeps

- `time.sleep(10)` after opening a config file, on the GUI thread, so the window freezes for 10 s: `src/GUI_util.py:1075`, `src/NLP_setup_external_software_main.py:101`, `src/NLP_setup_package_language_main.py:235`. The stated reason is "give enough time to save any changes"; re-read the file when it is next needed instead.
- `src/Stanford_CoreNLP_util.py:900` `time.sleep(5)` and `src/file_spell_checker_util.py:684` `time.sleep(5)`: waiting for the CoreNLP server. Poll the port until it answers (it is often ready sooner, and sometimes not ready after 5 s).

The 1 s pauses in `GIS_geocode_util` and `charts_util` are Nominatim's rate limit and must stay.

### 9.6 Network calls on the main thread

**Overlaps §1 (auto-update): coordinate with that work, don't duplicate it.** `release-1.6.41` already makes the offline check quiet and stops CLOSE from checking twice.

- `GUI_util.display_release()` runs at the end of `GUI_bottom` for every GUI: `internet_on()` then a GET to GitHub, before the window is usable. Here it took 0.03 s + 0.07 s, so on a good connection it is not the problem. On a dead or filtered network `internet_on()` can take up to 16 s (3 + 3 + 5 + 5 s of timeouts), and the GET up to 18 s (3 tries × 6 s).
- **Fix:** run the check in a background thread and fill the release label with `window.after`; check once per session, not once per window (the menu can pass the result to the GUIs it starts, like `NLP_SUITE_OPEN_WINDOWS`).
- No timeout at all, so a stalled connection hangs the GUI: `IO_libraries_util.check_CoreNLPVersion` (line 442, called at the start of every CoreNLP run from `Stanford_CoreNLP_util.py:360`), `IO_libraries_util.open_url` (line 720) and `GUI_util.watch_video` (line 2166). The last two fetch the whole page only to test that it exists before opening the browser; open the browser directly. Give the CoreNLP check `timeout=5` and run it at most once a day.

### 9.7 The first three launches start three processes

`NLP_menu_main.py` imports `GUI_util` (4.6 s) and only then, at lines 87–108, reads `config/launch_count.json` and starts `NLP_welcome_main.py` as a new process (another 4.6 s plus PIL), which in turn starts the menu again with `--from-welcome`. A new user waits roughly 14 s for the menu on the launches where first impressions are made.

**Fix:** move the launch-count block above `import GUI_util` (it needs only `json`, `os`, `sys` and `run_script_util`).

### 9.8 Menu start-up extras (not timed)

- `setup_external_programs_checkbox()` (`NLP_menu_main.py:1283`) → `get_external_software_dir` → `check_java_installation` runs `java -version` in a subprocess on every menu start. Cache the answer in the config file it already updates.
- Apple Silicon, source install: `pip freeze` in a subprocess on every menu start (`NLP_menu_main.py:1323`) to look for TensorFlow. Use `importlib.util.find_spec("tensorflow")`.

### 9.9 The analyses themselves (not profiled)

Read from the code only: 96 `iterrows()` / row-append patterns in 29 files, most in `DB_PCACE_data_analysis_util` (35), `charts_util` (13) and `corpus_profiler_util` (6). These grow quadratically on large tables. Do not rewrite them blind: time one real corpus run per tool (`python -X importtime` is no help here; use `cProfile`) and fix what the profile shows.

### 9.10 Order of work

1. §9.1 Stanza check and lazy pipeline: the largest single saving, one small PR.
2. §9.3 pandas and requests out of the `GUI_util` import chain; §9.2 step 1 (`find_spec`). Every GUI gets faster.
3. §9.7 launch-count block; §9.5 sleeps; §9.6 timeouts (after §1 lands).
4. §9.4 alerts, once Roberto has decided the behaviour.
5. §9.2 steps 2–3, module by module.
6. Re-measure with the same commands, on Windows and on a Mac, and on the zip build. Add a CI check that `import GUI_util` under the test stubs does not import pandas or requests, so the gain is not lost.

Every change follows CLAUDE.md: unit tests for new helpers, `pytest tests/`, and `python tests/gui_smoke.py` after any GUI edit.
