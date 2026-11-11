# PLAN — NLP Suite open work

What's open, what to close, what to fix next. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md), not here.

**Last updated:** 10 Nov 2026, getting ready for 1.6.42 (v1.6.41 released 10 Nov).

**State on GitHub (10 Nov 2026):** 9 open PRs (§2). The issue lists are proposals for Roberto: nothing in them has been closed or commented on.

## Contents

1. [Release 1.6.42 (getting ready)](#1-release-1642-getting-ready)
2. [Open pull requests](#2-open-pull-requests)
3. [Recent issues (2025–2026)](#3-recent-issues-20252026)
4. [The 2021–2024 backlog](#4-the-20212024-backlog)
5. [Tech debt](#5-tech-debt)
6. [Requirements, release checks and settled decisions](#6-requirements-release-checks-and-settled-decisions)
7. [Branches](#7-branches)
8. [Performance: slow GUI opening and "downloading"](#8-performance-slow-gui-opening-and-downloading)
9. [Outdated copy and flows (scan of 9 Nov 2026)](#9-outdated-copy-and-flows-scan-of-9-nov-2026)
10. [Dead code (scan of 10 Nov 2026)](#10-dead-code-scan-of-10-nov-2026)
11. [UI overhaul: findings (10 Nov 2026)](#11-ui-overhaul-findings-10-nov-2026)
12. [The GitHub wiki (scan of 10 Nov 2026)](#12-the-github-wiki-scan-of-10-nov-2026)
13. [Security alerts and the Python 3.11 release (scan of 11 Nov 2026)](#13-security-alerts-and-the-python-311-release-scan-of-11-nov-2026)

---

## 1. Release 1.6.42 (getting ready)

**Why this release matters:** it is the first one students' copies install by themselves (1.6.41 → 1.6.42), so the updater gets its first real, full-size run. Keep it to low-risk fixes. 1.6.41 shipped 10 Nov 2026; what it holds is in CHANGELOG.

**Still owed from 1.6.41:** send the students the one-time "download 1.6.41 by hand" email: draft in [NLP Suite 1.6.41: student email](https://claude.ai/artifact/KrHdadt32qC61AfRjK2fCi).

### 1.1 Scope: what goes in, and why

The rule: nothing that changes a shared structure (CoNLL columns, config files, chart inputs), the parsers, or the updater. Copy and dead files pass that rule, since neither changes what an analysis computes, and both belong in this release in particular:

- **The copy (PR #1705).** 1.6.42 is the first version that reaches every student without their doing anything. Without #1705, the version they get automatically still tells zip users to run STEP3 and `conda`, asks the "three setup options" question at every start, and the release page's "Already have an older version?" text predates the updater. The risk is in the start-up flows #1705 changes (`NLP_menu_main` start-up, the `IO_libraries_util` popups, the Setup GUIs), so it needs the GUI checks it has not had yet.
- **Dead files (§10.1).** Nothing imports them, yet the zip ships them. The updater swaps the whole folder, so a file dropped from the release is gone from the install after the update (§6); deleting files is not a new path for it.

In merge order:

| # | What | PR | State | Before merging |
|---|---|---|---|---|
| 1 | Stanza model checked only when missing, pipeline built on first use (§8.1) | #1704 | Mergeable, CI green | Its PLAN.md hunk still uses the old numbers (§9.1, §9.2 for what is now §8.1, §8.2): renumber on the branch, or drop its PLAN.md change and move the measured results into §8.1 after the merge. Open Style analysis and RUN it once by hand |
| 2 | `gui_smoke.py` no longer hangs in a checkout with no `config/`; Wordclouds first-run crash (#1708) | branch `fix/1708-wordclouds-first-run` | PR open | `run_script_util` is stubbed, so no setup GUI opens; each GUI is built with your `config/`, an empty one and `lib/config_defaults` (`--config` picks one). Then run it to check #1705 |
| 3 | Outdated copy and flows (§9.1) | #1705 | Mergeable, CI green; merges cleanly with #1704 | `tests/gui_smoke.py`; open the menu with an empty `config/` on Windows and on a Mac, and each Setup GUI; trigger the missing-module popup in a source run |
| 4 | Dead files and the legacy setup scripts (§10.1) | — | Done on local branch `chore/remove-dead-files` (`e65ebcef`), not pushed; needs Roberto's yes | After #1705: both touch `README.txt` and `CLAUDE.md`. The spec changes, so the pre-tag build is its test |
| 4b | Shape of Stories crashes at open with the default config (§11.3) | branch `fix/shape-of-stories-relative-config` | PR open | `config_util.read_config_file` resolves relative I/O paths against the NLP Suite folder; the `chdir` stays. Merges cleanly with #1705 (different lines of `config_util`). Still check on a fresh 1.6.41 zip |
| 5 | HW 4 leftover: GIS "(NER tag: …)" log line | — | Not started | `GIS_geocode_util.py` ~704 prints the date when there is one; the tag used is `item[2]` |
| 6 | §9.3 smaller copy | — | Optional | Only if ready before the freeze: strings, plus the `Word2Vec_main.py` case fix. Otherwise 1.6.43 |

Not in 1.6.42:
- PR #1682 (spaCy CoNLL ID/HEAD): correct, but it changes the CoNLL table, a shared structure (§2). 1.6.43.
- §8.3 (pandas and requests out of `GUI_util`'s import chain): it rewrites how every GUI reads its config, in `config_util` and `reminders_util`, which #1705 also edits. 1.6.43.
- §9.2's behaviour changes (decisions for Roberto); only its deletions (#1, #14, #15) are in, via §10.1.
- PR #1688 (Python 3.11 + Pillow 13, its own release once the updater has proven itself), PR #1683 (needs changes, §2), backlog triage (§4), the bulk of tech debt (§5).

### 1.2 The updater: known limits (open)

- **Long paths:** staging is 17 characters deeper than the install; without Windows LongPathsEnabled the deep `node_modules` paths (#1653) fail to unpack. Fails safely with a message. Fix with #1653.
- No checksum (GitHub's asset `digest` is unused) and no resume of a broken download. Ctrl-C during the download leaves `_update` behind, which blocks updates for 24 h (the message says which folder to delete).
- GitHub allows 60 unauthenticated API calls an hour per IP; on a shared campus network the exit-time release lookup can get 403. The fallback is the download page with the reason.
- The Git update on `current-stable` still runs `git add -A` + `git stash`, so local edits go into a stash silently.
- A release file the NLP Suite itself rewrites at run time would keep the backup every time; none is known.

### 1.3 Before tagging 1.6.42

1. The usual checks (§6), plus: `lib/release_manifest.tsv` is in both zips; the app icon still resolves after the icons moved (§10.1); none of the §10.1 files is in the zips.
2. **Right after the zips are up, update a real 1.6.41 install** on Windows and on a Mac: close it, accept, check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). This is the first full-size run; the 9 Nov test used a 26 MB stand-in release on localhost.
3. Not yet tested by hand: a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).
4. Ask students who report update problems to send that log to coralynn.yang@emory.edu.

### 1.4 After 1.6.42

1. **Close the four stale 2024 PRs** (§2) with a short thank-you comment.
2. **Retest and close the recent issues that releases may have fixed** (§3, "Retest" rows).
3. **Fix the open recent bugs** (§3, "Bug" rows), one branch and test each, per CLAUDE.md.
4. **Triage the 2021–2024 backlog** (§4). Proposal: bulk-close the stale ones with a comment inviting a reopen.
5. **1.6.43:** PR #1682, §8.3, §9.3 if it missed 1.6.42, and §9.2's behaviour changes as Roberto decides them. **Proposed instead (§13.3):** make 1.6.43 the Python 3.11 / Pillow 13 security release and move these to 1.6.44.
6. **Performance** in §8.10's order; **tech debt** in §5's order.
7. **Add the missing regression tests**: an empty-DataFrame test and a multi-column chart test for `charts_util` (§5.6).

## 2. Open pull requests

Reviewed 9 Nov 2026 (#1699, #1701, #1702 shipped in 1.6.41; #1679 and #1656 were re-applied there and closed); #1704 and #1705 checked 10 Nov. The older PRs conflict only because v1.6.40 reformatted all of `src/` (PR #1687).

"Tests" = the PR's own new tests, run on Windows in the NLP env on 9 Nov.

| PR | Opened | What | Merge | Tests | 1.6.42? | Review |
|---|---|---|---|---|---|---|
| #1704 | 11-09 | Stanza model downloaded only when missing; pipeline built on first use (§8.1) | Clean; CI green | 15 new; pytest 613 pass, the 2 known failures; gui_smoke 49 ok | Yes, first | Not opened and RUN by hand; no first-download, Mac or zip test. Its PLAN.md hunk uses the old section numbers (§1.1) |
| #1705 | 11-10 | Outdated copy and flows: docs, popups, reminders (§9.1), 49 files | Clean; CI green; clean with #1704 | `test_install_messages.py`; pytest 2 known failures | Yes, after #1704 | `gui_smoke.py` not run (hangs without `config/`), no GUI opened, Mac paths not run: §1.1 row 3 |
| #1682 | 10-16 | spaCy CoNLL ID/HEAD sentence-level and 1-based | Conflict: ruff only, mechanical | 2 pass | No: 1.6.43 (shared structure) | Correct: Stanza and CoreNLP already write 1-based, sentence-level, root 0, and no reader compensates for spaCy's old values. Shared structure, so not in a release about the updater. spaCy tables already on disk stay 0-based: say "re-parse" in the CHANGELOG |
| #1683 | 10-16 | Gender dictionary looks up only PERSON tokens | Conflict: ruff only | 5 pass | No | **Needs changes:** hardcodes `Stanford_CoreNLP_util.CoreNLP_annotate` whatever parser is configured (so the option now needs Java); returns `''` with no message when no NER csv comes back; once "Will" is a PERSON anywhere, every "will" is tagged |
| #1688 | 10-26 | Python 3.11 build so Pillow can go to 13.0.0 | Conflict: 2 adjacent lines | CI only | No (§1.1) | Decide. Whole pinned stack must rebuild on 3.11. STEP2 scripts still create `python=3.8` envs (`setup_Windows/STEP2-install_NLP-Suite.ps1:12`, `setup_Mac/STEP2-install_NLP-Suite.command:35`) and `pyproject.toml`/`pyrightconfig.json` say py310; the PR touches none of them |
| #1528 | 2024-09 | "dictionary functionality" (CallaGong) | — | — | No | **Close**: targets `current-stable`, 2 years old |
| #1525 | 2024-09 | Generalized Excel file reads (esunn0412) | — | — | No | **Close**: targets `current-stable`, 2 years old |
| #1436 | 2024-03 | Document Statistics sentence-length fix (razzak-ammar) | — | — | No | **Close**: check first that v1.6.39's sentence-statistics rewrite fixed it |
| #1383 | 2024-01 | Alternative STEP2 install script (Eli-Todd) | — | — | No | **Close**: install was rebuilt around PyInstaller |

All 2026 PRs are by coralynnkc and target `roberto`.


## 3. Recent issues (2025–2026)

"Retest": a later release says it fixed this or something close. Rerun on v1.6.41 and close if it's gone.

| # | Title | Kind | Note |
|---|---|---|---|
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

## 4. The 2021–2024 backlog

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
- **Enhancements and unlabelled `Emory-NLP` notes:** Roberto skims and keeps the ones still wanted. Add the kept ones to §3 or to a `wishlist` label, and close the rest.
- **Other unlabelled reports:** treat as bugs.

To do this with `gh` (needs a login): `gh issue close N -c "<comment>"`. Without a login, use the GitHub web UI.

## 5. Tech debt

Re-measured 7 Nov 2026 with Ruff 0.16.0 over `src/` (221 files). The 16 Jul figures are in brackets.

### 5.1 Latent crashes: undefined names (F821): 44 [68]

Most of the remaining 44 are in rarely used tools:

| File | Count |
|---|---|
| `syntactic_analysis_ALL_main.py` | 6 |
| `GIS_file_check_util.py` | 5 (`np`, `numColumns`, `msgTooFewColumnsForGeocoded`) |
| `Gephi_util.py` | 5 (`attvalue_xml`, `type_choices`) |
| `CoNLL_function_words_analysis_util.py` | 5 (`stats_pronouns` …) |
| `IO_files_util.py` | 3 (§5.2) |
| 13 more files | 1–2 each |

Full list: `ruff check src/ --select F821`.

### 5.2 Error handler that crashes: `IO_files_util.py` ~line 292

In the filename-date sort's `except:`, `date_location` is undefined, so a filename with an unparsable date raises `NameError` instead of printing the "non fatal" notice. The same file also has `gatherCLAs()` (~line 1640), which uses `argparse` without importing it. Delete it or fix it.

### 5.3 Silent failures: 215 bare `except:` [221]

Largest reliability lever. Convert to `except Exception`, and on user-facing paths report via `messagebox`. Worst files in July: `IO_files_util`, `GIS_geocode_util`, `file_filename_util`, `charts_util`, `Stanford_CoreNLP_util`.

### 5.4 Wrong-result risks

- **Late-binding closures in loops (B023): 8.** `statistics_csv_util.py` (`col`, `df`/`currentColumn`, `temp_str`), `CoNLL_k_sentences_util.py`, `charts_Plotly_util.py`, `charts_util.py`. Verify each, then bind at definition (`lambda col=col: ...`).
- **Mutable default arguments (B006): 47.** Mechanical fix.
- **Shadowed redefinitions (F811): 5** [37].

### 5.5 Fragility

- `eval()` (S307): 6. In `charts_Plotly_util.py`, `charts_util.py` and `hashfile.py`. Replace with `ast.literal_eval` or explicit parsing.
- `subprocess(..., shell=True)` (S602): 9. Breaks on paths with spaces. Use argument lists.

### 5.6 Tests

Coverage is 508 test functions in 52 files [3]. Gaps:
- No **empty-DataFrame** regression test for the chart/statistics pipeline (only `test_emotion_arc_html.py` covers an empty frame).
- No **multi-column chart** regression test for `charts_util` (the v1.6.4 "by Document" grouped-bar fix has no test).

### 5.7 Hygiene

- Unused variables (F841): 498. Unused imports (F401): 1 [290]. Invalid escapes (W605): 0 [80].
- Tab-indented lines remain in 2 files.
- Large modules (lines): `DB_PCACE_data_analysis_util` 7,731 · `charts_util` 5,620 · `corpus_profiler_util` 4,191 · `Stanford_CoreNLP_util` 3,563 · `statistics_txt_util` 3,033. When you open one for a feature, pull testable helpers out instead of adding in place.
- About 900 `print()` calls. Move to `logging` over time.

**Order:** §5.2 → F821 file by file → bare excepts on user paths → B023 → B006 → eval/shell.

## 6. Requirements, release checks and settled decisions

- **coreferee** is gone from `requirements.txt` (it pins `spacy<3.6` and broke the PyInstaller build). `fastcoref` replaces it. Don't re-add it. spaCy is unpinned.
- **pygit2** is no longer a requirement (1.6.41): the source-checkout updater uses the `git` program. Don't re-add it.
- **`lib/release_manifest.tsv`** is written by the build's last step before zipping (1.6.41). The self-updater relies on it to tell the user's files from the release's: any step that adds files to `dist/` must come before it.
- **A release may delete files.** The self-updater installs the new release as a whole folder and carries over only `config/`, `reminders/` and files the user added (not in the old manifest); a release file the new release drops is left in `<folder>_previous` and goes with it. A dropped file the user had edited stays in that backup, which is then kept (`user_files` in `NLP_setup_self_update_util.py`).
- **Pillow** is pinned to 10.4.0 (12.x breaks the bundled Tcl/Tk 8.6). PR #1688 tests Python 3.11 + Pillow 13 for the security advisory; its own release (§1.1). What else rides along: §13.
- **CI Python:** 3.10 for tests and installers. SRL stays on its own 3.8 env.
- **Mac runners:** `macos-15` since 2 Nov 2026 (`macos-14` retired). No Intel Mac build.
- **`src/` is Ruff-formatted** (v1.6.40). PRs opened before that need a rebase, not a hand merge.
- **Update order matters.** The in-app check reads `current-stable`'s `lib/release_version.txt`, which changes before the tag's zips finish building. The self-updater and the launch popup both wait until that version's zip is on the release page.
- **Before every tag:** build, unzip both artifacts, confirm `Launch NLP Suite (Mac).command` and the Windows entry point exist, confirm the app imports, then draft the CHANGELOG section. `lib/release_version.txt` must equal the tag (CI enforces it).

## 7. Branches

Remote branches besides `roberto`, `current-stable`:

- `cora-batch-2` (30 Oct 2026): collaborator staging, holds a merge of #1699. Not in `roberto`.
- `mac-font-pin` (22 Jul 2026): not in `roberto`, no open PR. Check whether it's still needed.
- `dictionary` (Sep 2024), `taeeun` (Dec 2024): heads of stale PRs #1528 and #1525. Delete after those PRs are closed.
- `remove_shortcut_prompt` (2021), `tony` (2023): no open PR. Delete candidates.

Deleting a remote branch is Roberto's call.

## 8. Performance: slow GUI opening and "downloading"

Evaluated 9 Nov 2026 on `current-stable` @ `43cbca1c` (v1.6.40), Windows 11, NLP env (Python 3.10), warm disk, good connection. Nothing in the code was changed; this section is findings and proposed fixes, ranked.

**Not measured:** the installer (zip) build and its bundled `python-env`; macOS; a cold start after a reboot; a first-time model download; the speed of the analyses themselves after RUN (§8.9 is read from the code only).

**How it was measured.** `python -X importtime -c "import GUI_util"`; each third-party library imported alone in a fresh process; for every `*_main.py`, the libraries it reaches through module-level imports (followed through the local `src` modules, including the `install_all_Python_packages` lists) imported together in one fresh process; `stanza.download("en")` and the Stanza pipeline timed with the model already on disk; `import Stanza_functions_util` and `import statistics_txt_util` run for real. The per-GUI figures in §8.2 are import cost only, from that static trace: no GUI window was opened and clicked.

### 8.0 Summary

| # | Finding | Measured cost | Who pays | Fix size |
|---|---|---|---|---|
| 1 | Stanza model re-checked (and a pipeline built) every time a GUI opens | 9–11 s per check, 8.7 s for the pipeline | 18 of 55 GUIs | Small |
| 2 | Heavy libraries imported when the GUI opens, not at RUN | 10–40 s | 32 of 55 GUIs | Medium, file by file |
| 3 | Every GUI starts with 4.6 s of `GUI_util` imports (pandas, requests) | 4.6 s vs 0.9 s for a bare Tk window | Every GUI, every open | Small |
| 4 | "Started/Finished running" alerts and reminders block until their countdown ends | 1–12 s each | Every RUN | Small (a decision first) |
| 5 | Fixed `time.sleep` calls freeze the GUI | 5–10 s each | Config-file edits, CoreNLP, spell checker | Small |
| 6 | Version check on the main thread on every GUI open; other web calls without a timeout | 0.1 s here; up to ~16–18 s on a blocked or dead network | Every GUI | Small; the offline part shipped in 1.6.41 |
| 7 | First three launches start three Python processes before the menu shows | about 3 × 4.6 s | New users | Small |
| 8 | Menu runs `java -version` (and `pip freeze` on Apple Silicon source installs) at every start | Not measured | Menu | Small |
| 9 | Row-by-row pandas loops in the analyses | Not measured | RUN on large corpora | Profile first |

Findings 1–3 are where the opening time goes. Adding up the measured parts, a GUI such as Style analysis takes an estimated minute or more to open (4.6 s base + 29 s of libraries + three model checks + the pipeline; not timed end to end) and should drop to a few seconds; the menu and the light GUIs should drop from about 5 s to about 1.5 s.

### 8.1 The Stanza model is re-checked every time a GUI opens (the "downloading")

Four modules call `stanza.download("en")` at import time, i.e. when a GUI that uses them opens, not when RUN is clicked:

- `src/Stanza_util.py:43` (it tests whether `~/stanza_resources/en` exists at line 33, then downloads regardless)
- `src/Stanza_functions_util.py:39`, and line 42 then builds `stanza.Pipeline(lang="en", processors="tokenize, lemma")`
- `src/statistics_txt_util.py:34`
- `src/wordclouds_util.py:34`

With the model already on disk, each call still takes **9.1–10.7 s**: Stanza fetches its resources list from GitHub and re-hashes the model files. Building the pipeline takes another **8.7 s**. Measured end to end: `import Stanza_functions_util` **33 s**, `import statistics_txt_util` **38.5 s**.

18 of the 55 GUIs import at least one of these modules when they open. Style analysis, Semantic analysis and Syntactic analysis (ALL) import three of them, so they run the check three times.

**Fix.**
1. One helper, e.g. `Stanza_functions_util.ensure_stanza_model(lang)`: return at once if the model folder exists; otherwise download with the existing `IO_internet_util.download_with_warning`. Call it from the four places.
2. Build the pipeline on first use, not at import: replace the module-level `stanzaPipeLine` with a cached `get_stanza_pipeline()`. `stanzaPipeLine` is referenced 156 times in 28 files, so this is a mechanical change that needs a test for the helper and a `tests/gui_smoke.py` run.

Expected saving: 10–30 s per open for those 18 GUIs. Offline, it also removes the download-failure dialogs at open.

### 8.2 Heavy libraries are imported when the GUI opens

Each `*_util.py` starts with `install_all_Python_packages(...)`, which **imports** every listed package to test that it is installed, and then with module-level imports of the same libraries. A GUI therefore loads everything any of its options might use before it draws.

Libraries alone, fresh process (seconds): `sentence_transformers` 39.5 · `summarizer` 25.2 · `spacy_langdetect` 23.6 · `tensorflow` 21.0 · `stanza` 16.8 · `contextualSpellCheck` 15.0 · `spacy` 14.6 · `seaborn` 11.4 · `transformers` 9.4 · `textblob` 8.2 · `pyLDAvis` 8.1 · `textstat` 7.5 · `nltk` 7.4 · `sklearn` 5.6 · `gensim` 5.2 · `folium` 3.6 · `openpyxl` 3.4 · `pandas` 3.1–3.5.

Library import cost per GUI (all its libraries together, one process; excludes §8.1 and the Suite's own code):

| Cost | GUIs |
|---|---|
| 3–4 s (23) | menu, welcome, NLP_setup_IO, NLP_setup_external_software, DB_SQL, SRL, corpus_profiler, data_manipulation, file_checker_converter_cleaner, file_handler_ALL, file_manager, file_matcher, file_merger, file_search_ALL, file_splitter, html_annotator, knowledge_graphs, narrative_analysis_ALL, nominalization, sample_corpus, semantic_analysis_ALL, sentiments_emotions_ALL, statistics_txt |
| 10–18 s (11) | GIS_symbolic 9.9, GIS_distance 10.6, charts_Excel 10.9, data_visualization 10.9, statistics_csv 10.9, GIS_Google_Earth 11.2, wordclouds 12.8, word2vec 13.2, CoNLL_table_analyzer 13.7, semantic_aggregation 13.7, NGrams_CoOccurrences 17.5 |
| 22–40 s (21) | file_classifier 22.5, sentiment_analysis 22.9, file_checker_pre_processing_pipeline 25.3, topic_modeling 25.4, file_search_byWord 25.5, corpus_checker_PCACE_data 25.9, shape_of_stories 25.9, NER 28.8, SVO 28.9, semantic_analysis 29.1, style_analysis 29.1, syntactic_analysis_ALL 29.1, html_annotator_gender 29.2, sentence_analysis 30.2, coreference 32.0, parsers_annotators 32.0, DB_PCACE_data_validation 33.2, NLP_setup_package_language 33.2, file_spell_checker 38.2, DB_PCACE_data_analysis 38.8, GIS 39.8 |

The GUIs in the first row already import their logic inside `run()`; they pay the cost at RUN instead, which is the right place.

**Fix, in this order.**
1. **`install_all_Python_packages` (`src/IO_libraries_util.py:102`): test with `importlib.util.find_spec(module)` instead of `__import__`.** It answers "is it installed?" without loading the package. One function, every GUI benefits; the existing name mapping (pdfminer, docx, PIL …) stays. Needs a unit test.
2. **Move the heavy imports into the functions that use them**, starting with the modules shared by most GUIs: `Stanza_util`, `statistics_txt_util`, `Stanza_functions_util`, `charts_util` (plotly, numpy), `IO_csv_util` (§8.3). Then the slow GUIs from the bottom of the table up. One PR per module, each with a `tests/gui_smoke.py` run.
3. In each `X_main.py`, import `X_util` inside `run()` where it is not needed to build the window (the pattern the fast GUIs already follow).

### 8.3 Every GUI pays 4.6 s before its own code runs

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

### 8.4 Timed alerts block the run

`IO_user_interface_util.timed_alert` (372 calls in 94 files) calls `GUI_IO_util.message_box_widget`, which ends with `top_message.wait_window()` (`src/GUI_IO_util.py:1384`). The analysis does not start, or the outputs do not open, until the popup closes.

The countdown is also longer than the `timeout` passed: it counts `timeout / 500` seconds, or `timeout / 1500` for "Started running"/"Finished running" messages (`GUI_IO_util.py:1255-1294`). A "2000 ms" alert waits 4 s, a 6000 ms one 12 s, unless the user clicks OK. Reminders wait 30 s.

**Fix (Roberto decides the behaviour):** for OK-type alerts, show the popup and return at once, letting it close itself with `after(timeout, ...)`; make the countdown equal `timeout`. Yes/No reminders must keep waiting for an answer.

### 8.5 Fixed sleeps

- `time.sleep(10)` after opening a config file, on the GUI thread, so the window freezes for 10 s: `src/GUI_util.py:1075`, `src/NLP_setup_external_software_main.py:101`, `src/NLP_setup_package_language_main.py:235`. The stated reason is "give enough time to save any changes"; re-read the file when it is next needed instead.
- `src/Stanford_CoreNLP_util.py:900` `time.sleep(5)` and `src/file_spell_checker_util.py:684` `time.sleep(5)`: waiting for the CoreNLP server. Poll the port until it answers (it is often ready sooner, and sometimes not ready after 5 s).

The 1 s pauses in `GIS_geocode_util` and `charts_util` are Nominatim's rate limit and must stay.

### 8.6 Network calls on the main thread

**Partly done in 1.6.41:** the offline check is quiet and CLOSE no longer checks twice.

- `GUI_util.display_release()` runs at the end of `GUI_bottom` for every GUI: `internet_on()` then a GET to GitHub, before the window is usable. Here it took 0.03 s + 0.07 s, so on a good connection it is not the problem. On a dead or filtered network `internet_on()` can take up to 16 s (3 + 3 + 5 + 5 s of timeouts), and the GET up to 18 s (3 tries × 6 s).
- **Fix:** run the check in a background thread and fill the release label with `window.after`; check once per session, not once per window (the menu can pass the result to the GUIs it starts, like `NLP_SUITE_OPEN_WINDOWS`).
- No timeout at all, so a stalled connection hangs the GUI: `IO_libraries_util.check_CoreNLPVersion` (line 442, called at the start of every CoreNLP run from `Stanford_CoreNLP_util.py:360`), `IO_libraries_util.open_url` (line 720) and `GUI_util.watch_video` (line 2166). The last two fetch the whole page only to test that it exists before opening the browser; open the browser directly. Give the CoreNLP check `timeout=5` and run it at most once a day.

### 8.7 The first three launches start three processes

`NLP_menu_main.py` imports `GUI_util` (4.6 s) and only then, at lines 87–108, reads `config/launch_count.json` and starts `NLP_welcome_main.py` as a new process (another 4.6 s plus PIL), which in turn starts the menu again with `--from-welcome`. A new user waits roughly 14 s for the menu on the launches where first impressions are made.

**Fix:** move the launch-count block above `import GUI_util` (it needs only `json`, `os`, `sys` and `run_script_util`).

### 8.8 Menu start-up extras (not timed)

- `setup_external_programs_checkbox()` (`NLP_menu_main.py:1283`) → `get_external_software_dir` → `check_java_installation` runs `java -version` in a subprocess on every menu start. Cache the answer in the config file it already updates.
- Apple Silicon, source install: `pip freeze` in a subprocess on every menu start (`NLP_menu_main.py:1323`) to look for TensorFlow. Use `importlib.util.find_spec("tensorflow")`.

### 8.9 The analyses themselves (not profiled)

Read from the code only: 96 `iterrows()` / row-append patterns in 29 files, most in `DB_PCACE_data_analysis_util` (35), `charts_util` (13) and `corpus_profiler_util` (6). These grow quadratically on large tables. Do not rewrite them blind: time one real corpus run per tool (`python -X importtime` is no help here; use `cProfile`) and fix what the profile shows.

### 8.10 Order of work

1. §8.1 Stanza check and lazy pipeline: the largest single saving, one small PR.
2. §8.3 pandas and requests out of the `GUI_util` import chain; §8.2 step 1 (`find_spec`). Every GUI gets faster.
3. §8.7 launch-count block; §8.5 sleeps; §8.6 timeouts.
4. §8.4 alerts, once Roberto has decided the behaviour.
5. §8.2 steps 2–3, module by module.
6. Re-measure with the same commands, on Windows and on a Mac, and on the zip build. Add a CI check that `import GUI_util` under the test stubs does not import pandas or requests, so the gain is not lost.

Every change follows CLAUDE.md: unit tests for new helpers, `pytest tests/`, and `python tests/gui_smoke.py` after any GUI edit.

## 9. Outdated copy and flows (scan of 9 Nov 2026)

A scan of all of `src/`, `reminders/`, the docs and the setup scripts for text and flows that predate how the NLP Suite works now: the zip build (no Anaconda, no pip, no terminal), Stanza as default parser, the bundled Java runtime, the self-updater, the new menu, fastcoref, pandas 2, Python 3.10. Six read-only passes, one per slice; each finding below was checked against the code before it was changed or listed.

**Not read line by line:** the long help/readMe bodies of `DB_PCACE_data_analysis_main`, `DB_PCACE_data_validation_main`, `data_visualization_main`, `file_manager_main`, `DB_SQL_main`; the middle of `GUI_util` (about lines 1100–1750, 2190–2600), `NGrams_CoOccurrences_main` (400–1280), `NLP_setup_IO_main` (630–1050), `knowledge_graphs_main` (240–730). These were keyword-searched only. The TIPS pdfs themselves were not opened (only their names were checked). No web link was tested online.

### 9.1 Changed in PR #1705 (open, not yet in `roberto`)

Docs:

| Where | What |
|---|---|
| `docs/Installing-the-NLP-Suite.md`, `Download-Install-Update-Run.md`, `Troubleshooting.md` | Mac: the removed "NLP Suite Mac Setup" app replaced by `Launch NLP Suite (Mac).command` (v1.6.33). Update: describes the 1.6.41 self-update; "config resets after an update" and "extract to a new folder" removed; not Program Files, not OneDrive. Java: bundled, no JDK download. NLTK/WordNet data: downloaded on first use, not bundled. Developer setup: `pip install -r requirements.txt` and `python src/NLP_menu_main.py` (was a hand-typed pip list and `NLP_Suite_main.py`, which does not exist). New "Updating" troubleshooting table |
| `docs/Installing-External-Software.md` | Java row moved to "no longer required"; Stanza does not replace the CoreNLP-only annotators |
| `docs/What-the-NLP-Suite-Does.md` | spaCy (TextBlob) sentiment is dictionary-based, as in the GUI |
| `docs/release_body_header.md` | "Already have an older version?" now matches the updater; "zip", not "installer" |
| `docs/Narrative_Symbolic_Space_design.md`, `corpus_profiler_spec.md` | Status lines: both are implemented |
| `README.txt` | Was the 2021 STEP1/STEP2 Anaconda instructions; now points to Releases and `GETTING_STARTED.txt` |
| `README.md`, `GETTING_STARTED.txt` | What is bundled (Java yes; models download on first use); Windows "Unblock", not "Unlock" |
| `CLAUDE.md` | Ruff target is py310; `setup_Windows/`, `setup_Mac/` are legacy scripts, not installers |
| `requirements.txt`, `build-installers.yml` | Comments only: OCR did ship (v1.6.34); two builds, not three; no Setup app |

Popups and flows:

| Where | What |
|---|---|
| `IO_libraries_util` missing-module popup | Was STEP3 / `(base)` / zsh / "Conda install Python=3.7" / a torch + cudatoolkit recipe, three popups. Now one: `pip install -r requirements.txt`, or use the download. Source checkouts only (the zip returns early). `which_shell()` removed: on a Mac with bash it blocked the message and returned False |
| `IO_libraries_util.import_nltk_resource` | Shown in the zip build too. No more STEP3/conda advice there; the source run keeps one command |
| `IO_libraries_util` Java messages | No Oracle account. In the zip a Java failure means the bundled `jre` is missing: says so. Link goes to Temurin 17. Gephi no longer triggers the Java check |
| `IO_libraries_util` external software | "You cannot do any textual analysis without Stanford CoreNLP" removed: all external software is optional. Gephi download text no longer talks about Intel Macs. `open_url` named every website "Check on GitHub the NLP Suite newest release version" when offline |
| `NLP_menu_main` start-up | The "three setup options not completed" question fired at every start when any optional external program was missing, described buttons the menu no longer has, and offered a video. Now a warning only when Input & output or Parser & language needs setup. Removed: the Mac TensorFlow reminder shown to every Mac user and the source-only `pip install tensorflow-metal` popup |
| `GUI_util` Setup dropdown | "Setup preferences" removed: in every GUI it only said "not available yet". Licence message names the right file |
| 11 GUIs | "click on the Setup NLP button" (no such button) → the Setup dropdown item by its real name |
| `NLP_setup_package_language_main`, `Stanza_util` | "Stanza does not seem to be installed… conda activate NLP… pip install stanza" → the model download failed, check the internet. The video question used a key that does not exist (KeyError on Yes): fixed |
| `NLP_setup_IO_main` | Video question removed: its link is empty |
| `NLP_setup_external_software_main` | The config file test looked in the current folder, so the long first-time popup always showed. "All external software has been installed" warning at every opening removed |
| `NLP_setup_update_util` | Offline no longer prints "up-to-date (0.0.0)" |
| `file_checker_converter_cleaner_main` | rtf → txt showed Mac terminal instructions on every platform before running the Suite's own converter: removed |
| `file_search_ALL_main` | "Search word(s) for different word senses" opened Word2Vec; word sense induction now lives in Semantic analysis |
| `SRL_util`, `run_script_util`, `coreference_*`, `file_converter_util`, `topic_modeling_gensim_util`, `statistics_csv_util`, `config_util`, `CoNLL_*`, `corpus_profiler_util`, `IO_files_util` | pip/conda/Anaconda Prompt advice replaced by what a zip user can do, with one line for source runs; names of scripts and buttons that no longer exist (`StanfordCoreNLP.py`, `NLP_GUI.py`, "Setup button") corrected. SRL says plainly that it is not in the zip build |
| `reminders_util`, `reminders.csv` | Rewritten: NLP Suite architecture (was "type Python knowledge_graphs_main.py… NLP_main.py"), coreference (was "exclusively Stanford CoreNLP"), VADER (was "run python -m nltk.downloader all"), GIS txt input, `Stanford_CoreNLP_NER_main.py` → `NER_main.py`, wrong TIPS name for the Google API key. Removed 9 rows for tools that no longer exist (`whats_in_your_corpus`, `NGrams_CoOccurrences_Viewer`, `file-spell-checker`, "SVO Someone?", "GIS Multi-word Locations") |

New tests: `tests/test_install_messages.py`. `pytest`: only the 2 known local failures. **Not run:** `tests/gui_smoke.py` (it hangs in a checkout without `config/`) and no GUI was opened by hand; the Mac paths were not run.

### 9.2 Decisions for Roberto (not changed)

Deletions and behaviour changes. Each is ready to do once decided.

| # | What | Evidence | Proposal |
|---|---|---|---|
| 1 | `setup_Windows/` and `setup_Mac/` scripts (STEP1-3, `run_NLP-Suite.*`, `NLP.bat`, shortcut scripts, `readme_*_beta.md`) | Not in the zip. Anaconda 2021.05, `python=3.8`, `cudatoolkit` on a Mac, `git checkout -f`, read the stale `src/requirements.txt`; the Mac STEP3 points to a folder that does not exist | **1.6.42, §10.1** |
| 2 | SRL in the zip build | `setup_SRL.py` is not shipped and needs conda, so SRL cannot be set up there. The checkboxes in SVO, Semantic analysis and SRL_main stay enabled; the menu entry "SRL Semantic Role Labeling" shows as unavailable although `SRL_main.py` exists | Either disable the SRL checkboxes when frozen, or ship an SRL environment. Then fix the menu entry to match |
| 3 | Java as "external software" | A JRE is bundled, but Setup external software still lists "Java (JDK)" as missing and offers to download it. In the install branch (`IO_libraries_util`, "RF 8/30") the test reads `if Java_errorFound:` → "IS ALREADY INSTALLED" | Hide the Java row when the bundled `jre` is found. Check the RF 8/30 condition |
| 4 | Coreference default | `coreference_main` defaults to Stanford CoreNLP (needs CoreNLP); Stanza and BERT need nothing. Menu labels still say "CoreNLP annotator - coreference", "Pronominal resolution via CoreNLP" (`constants_util` 1011, 1067; `NLP_menu_tools_util` 40, 87, 97) | Default to Stanza; rename the labels (keys change in three files together) |
| 5 | `config_util` fallback | When the package config cannot be read the fallback is Stanford CoreNLP (line 199) | Stanza |
| 6 | First three launches open `NLP_welcome_main` in a second process | §8.7; its video button is disabled, Enter only reopens the menu | Remove the redirect and the file |
| 7 | `NLP_menu_main` external-software reminder | `setup_external_programs_checkbox` returns the module global (always ""), so the reminder never shows; `setup_external_software_warning`/`callback` are never called | Delete the three |
| 8 | N-grams VIEWER | The checkbox and two menu entries are live; RUN answers "temporarily disconnected" | Hide until it is back, or reconnect |
| 9 | Topic modeling "Run MALLET (coherence)" checkbox | Calls `gensim.models.wrappers`, removed in Gensim 4; always ends in "install Gensim 3.8.3" | Remove, or rewrite with Gensim's CoherenceModel. Help text also says "Gensim uses the MALLET algorithm" (it does not) |
| 10 | OCR menu item | pytesseract/pdf2image are not bundled, so in the zip it can only end in the "missing" message | Hide when frozen, or bundle |
| 11 | `parsers_annotators_main` | Two unreachable "select Stanford CoreNLP as your default package" branches (300–313, 395–408); "Open coreference GUI" checkbox is read and never used; Word2Vec item never matches its own label; coreference item says "via spaCy" (coreferee is gone); Stanza constituency says "not available yet" though Setup offers it | One PR for the annotator menu |
| 12 | Open-GUI launchers that use `sys.executable` | `DB_PCACE_data_analysis_main`, `DB_PCACE_data_validation_main`, `DB_SQL_main` (frozen: that is the app, not Python); `corpus_checker_PCACE_data_main` runs `sudo Python X_main.py` on a Mac and launches `WordNet.py`, which does not exist | Use `run_script_util` everywhere |
| 13 | TIPS menu | "pip install & Anaconda environments", "Python: download, install, run", "Anaconda & pip useful commands" are second in the main TIPS list | Move to the end as developer TIPS, or remove. The pdfs themselves, and the Java / CoreNLP / MALLET install TIPS and "Topic modeling and corpus size", need a read |
| 14 | Dead files | `videos_util.py` (pafy/vlc, imported nowhere), `NLP_setup_download_jars.py`, `knowledge_graphs_DBpedia_util_SPARQL.py`, `nyt_api_call.py`, `html_annotator_extractor_util_NEW.py`, `TensorFlow_semantic_analysis.py`, `GIS_heatMapIntegration.py`, `GIS_heatMapintegration_ver2.py`, `post_build_fixup.py`, `wiki-draft-About.md`, `.github/workflows/build-family-viewer.yml` (its spec files are not in the repo) | **1.6.42, §10.1.** |
| 15 | `NLP_Suite.spec` | Hidden imports for 8 modules that do not exist (`data_visualization_1_main`, `_2_main`, `whats_in_your_corpus_main`, `GIS_folium_map_util`, `SENNA_util`, `social_science_research_main`, `knowledge_graphs_DBpedia_YAGO_main`, `charts_matplotlib_seaborn_util`); a local build bundles the live `config/` (API keys); "Python 3.8" comment | Hidden imports and the comment: **1.6.42, §10.1**. The `config/` bundling changes what a build ships: 1.6.43 |
| 16 | Reminders | 50 titles are in `reminders.csv` twice, under a GUI and under `*`. Popups read only the `*` row, the dropdown toggles the GUI row, so switching a reminder off there does nothing. About 12 definitions in `reminders_util` are used nowhere (Java 64-bit `-d64`, "CoreNLP Server is shutting down", tkinter Mac bug, SVO/WordNet/MALLET/Google Earth "system requirements") | Delete the per-GUI duplicates and the unused definitions |
| 17 | Release history button | Opens the wiki page `NLP-Suite-Release-History`; the update popup already links `CHANGELOG.md` | Point to CHANGELOG if the wiki page is no longer kept |
| 18 | wordclouds | Menu offers Wordle (site gone) and Tagxedo (needs Silverlight); "Tagul" is now WordArt; Python WordCloud asks for internet though it needs none | Remove the two, rename the third, drop the check |
| 19 | `MEMO_Development_Notes.md`, `docs/CustomTkinter-Migration-Plan.md` | June 2026 history (Python 3.8 build, Mac Intel CI, files since deleted); a plan that names `setup-app/` and says installers build from `roberto` | A "historical" banner on each, or delete |

### 9.3 Smaller copy still to fix

Low risk, not done only to keep PR #1705 reviewable.

- **CoreNLP-era wording where three or four packages now work:** `NER_main` 611, 634, 658, 990; `GIS_main` 1290, 1322, 1343; `coreference_main` 272, 364, 563, 592, 635; `narrative_analysis_ALL_main` 443, 459, 927; `corpus_profiler_main` 717 ("hundreds" of documents), 726; `parsers_annotators_main` 972 (a "*" option that does not exist); `shape_of_stories_main` 599–600, 996, 1061 and `sentiments_emotions_ALL_main` 247 (spaCy listed as neural); `sentiment_analysis_main` 1077–1083, 1123 (old script names, `nltk.downloader`); `language_tools_advisor_util` 186, 254, 263; `NLP_setup_external_software_main` 491, 499, 518.
- **"Setup NLP package and corpus language"** (the item is "Setup NLP package (parsers & annotators) and corpus language"): `NER_main` 144, `NGrams_CoOccurrences_main` 1571, `Stanza_util` 202/731, `Stanford_CoreNLP_util` 177, `sentiment_analysis_main` (7 places), `semantic_aggregation_main` 1417, `IO_internet_util` 89, and the "NLP setup options" reminder built in 9 GUIs.
- **"pulling the latest release from GitHub"** hover on CLOSE: `GUI_util` 2659, `NLP_welcome_main` 316, `NLP_setup_package_language_main` 775, `NLP_setup_external_software_main` 455.
- **Names that do not exist:** `knowledge_graphs_main` 989 (TIPS name), 928–941 (YAGO and Wikipedia TIPS not offered); `file_classifier_NER_util` 40–46 and `file_find_non_related_documents_util` 43–49 (`concreteness_analysis.py`, then `sys.exit`); `sentiment_analysis_hedonometer_util` 59, `sentiment_analysis_VADER_util` 85 (wrong lib path and script name); `semantic_aggregation_main` 499 and `semantic_analysis_main` 1086 launch `Word2Vec_main.py` (the file is `word2vec_main.py`: fails on a case-sensitive disk).
- **Windows-only advice also shown on a Mac:** `config_util` 130, 159, 250, 284, 665, 698; `license_GUI` 77; `GUI_IO_util` 22.
- **Other:** `IO_libraries_util` Windows 64-bit Java branch; MALLET and Google Earth download links to check; `topic_modeling_mallet_util` "TEMPORARY FIX… environment variables" popups on every run (the code sets them itself); `file_manager_main` utf-8/ASCII checkboxes that only say "not available yet"; `file_merger_main` 326; `NLP_menu_main` 593–598, 1157 (readMe: "Java and Python tools", LGPL 2.1 though the licence file is GPL 3, CoreNLP 4.3.1); `docs/Supported-Systems-Languages.md` 38; `requirements-mac.txt` still lists pafy/python-vlc.

## 10. Dead code (scan of 10 Nov 2026)

**How it was found:** every `src/*.py` whose module name appears nowhere else in `src/`, `tests/`, `lib/`, the specs, the workflows or the setup scripts (`grep -w`), plus the §9.2 findings. A mention in a comment counts as a use, so the list is short of complete (`videos_util` was found only by reading). Not swept: dead functions and branches inside live modules (§5.7 counts 498 unused variables); `lib/` data files; TIPS pdfs no GUI names.

### 10.1 Delete in 1.6.42 (needs Roberto's yes)

One PR, after #1705 (§1.1 row 4). Each file was checked: nothing imports it, launches it with `run_script`, or names it in a workflow; the spec names some of them only as hidden imports.

| Group | Files | Evidence |
|---|---|---|
| Legacy setup scripts | `setup_Windows/`, `setup_Mac/` (all but the two icons), `src/NLP_setup_shortcut_add.py`, `src/NLP_setup_shortcut_remove.py`, `src/requirements.txt`, `src/requirements_mac.txt` | §9.2 #1. Outside those folders, only the spec uses them: its icon path and two hidden imports. The two `src/requirements*` files are read only by STEP2 |
| Icons (move, don't delete) | `setup_Windows/NLP_Suite.ico`, `logo.ico` | `NLP_Suite.spec:27` uses `NLP_Suite.ico`; `logo.ico` is used nowhere. Move the first (e.g. to `lib/`), update line 27, drop the second |
| PC-ACE debugging scripts (June 2026) | `src/_add_indexes.py`, `_add_indexes_now.py`, `_check_idx.py`, `_check_path.py`, `_debug_hops.py`, `_debug_xref.py`, `_test_actor_process.py`, `_test_cross_join.py` | One-off scripts with a hard-coded `C:/Users/rfranzo/Desktop/...sqlite` path; imported nowhere |
| Unused modules | `GIS_heatMapIntegration.py`, `GIS_heatMapintegration_ver2.py`, `html_annotator_extractor_util_NEW.py`, `knowledge_graphs_DBpedia_util_SPARQL.py` (440 lines), `nyt_api_call.py`, `TensorFlow_semantic_analysis.py`, `POTUS_webscraper.py` (2023), `pandas_compat_util.py`, `videos_util.py`, `NLP_setup_download_jars.py` | Imported nowhere. `pandas_compat_util` (July 2026) is a shim for pandas < 1.3 that nothing ever adopted; pandas 2 is pinned. `videos_util` is imported only in commented-out lines (`GUI_util`, `NLP_welcome_main`); drop `pafy` and `python-vlc` from `requirements-mac.txt` with it. `NLP_setup_download_jars` appears only in the spec's hidden imports |
| Repo root and workflows | `post_build_fixup.py`, `wiki-draft-About.md`, `.github/workflows/build-family-viewer.yml` | §9.2 #14. The spec mentions `post_build_fixup` only in a comment |
| `NLP_Suite.spec` | Hidden imports of the modules above and of the 8 that do not exist (§9.2 #15); the "Python 3.8" comment | The pre-tag build checks it |

**Checks for the PR:** rerun the grep on the final tree; `pytest tests/`; `tests/gui_smoke.py`; CHANGELOG: one line ("Removed the 2021 Anaconda setup scripts and unused files; nothing a tool uses changed").

### 10.2 Looks dead, is not

- `src/network_graph_app.py` and `NetworkGraphViewer.spec`: the standalone Network Graph Viewer, built by `build-network-viewer.yml` on `ngv-*` tags.
- `setup_SRL.py`: sets up the SRL environment for source runs (§9.2 #2).
- `requirements-mac.txt`, `requirements-windows.txt` (root): installed by `build-installers.yml`.

### 10.3 Later

- `NLP_menu_main`: `setup_external_software_warning` and its callback are never called (§9.2 #7). `setup_external_programs_checkbox` is called and runs `java -version` at every start (§8.8), so it goes with that decision, not here.
- `MEMO_Development_Notes.md`, `docs/CustomTkinter-Migration-Plan.md`: a "historical" banner or delete (§9.2 #19).
- `NLP_welcome_main.py`: dead once §9.2 #6 removes the redirect.
- Stale remote branches (§7).
- A `vulture src/` pass for dead functions. Expect false positives: GUI callbacks are bound by name and modules are launched by string.

## 11. UI overhaul: findings (10 Nov 2026)

**Decision so far:** stay with CustomTkinter (CTk). A TypeScript front end would mean rewriting 55 GUIs and the way they start each other; CTk keeps every `run()` as it is.

**How it was looked at:** each `*_main.py` built under real Tk on a Mac (macOS, 1470×956 logical screen, the NLP310 env, `config/` seeded from `lib/config_defaults`), screenshotted, and its widgets walked: the `gui_layout_gate.py` method, plus the screenshot step of `tests/gui_gallery.py` from the CTk branch, adapted to `roberto`. All 55 GUIs, Windows not looked at. Counts are from `grep` over `src/`.

### 11.1 Where the migration stands

- **A CTk migration was mostly built in July and never merged.** Branch `ctk/phase1-grid` on the coralynnkc fork (last commit 23 Jul): `GUI_theme_util.py` (theme, widget factories, tooltips; 880 lines), `ctk_bundle_util.py` (the `CTkImage` fix for the bundled Python), `nlp_suite_theme.json`, `tests/ctk_bundle_smoke.py`, `tests/gui_gallery.py`, and Phases 2–3 (all GUIs converted, PRs #7–#20 on the fork). It is 49 commits ahead and 196 behind `roberto`, and 64 files conflict, mostly because v1.6.40 reformatted `src/`. Only the grid half of Phase 1 (`placeWidget` → grid) reached `roberto`.
- **On `roberto` only the menu's tool browser is CTk.** Everything else is plain Tk: 326 `tk.Label`, 321 `tk.Checkbutton`, 273 `tk.Button`, 214 `tk.OptionMenu`, 136 `tk.Entry`, 58 `ttk.Combobox`, 9 `tk.Scale`. 171 raw `.place()` calls bypass the layout helper.
- 9 GUIs opt out of the grid layout (`GUI_IO_util.GRID_OPT_OUT`): 7 on all platforms, `charts_Excel` and `file_manager` on Mac only.
- `docs/CustomTkinter-Migration-Plan.md` describes the branch, not `roberto`. Its Windows bundle smoke test (§5.1 there) was never run.

### 11.2 What the screenshots show

Most of these are about content and chrome, not the widget toolkit; CTk alone fixes only the last few.

| # | Finding | Where |
|---|---|---|
| 1 | The same five-line "Welcome to this Python 3 script…" block tops every GUI (about 110 px): it explains the HELP buttons, TIPS and RUN, and calls the tool a script | `GUI_util.GUI_top`, all 55 |
| 2 | A "? HELP" button starts every row: 597 of them. Some rows have nothing else (`file_classifier`, two in `DB_PCACE_data_validation`) | `place_help_button` |
| 3 | Four blank buttons right of the I/O row (`text=""`, 9 such buttons in `GUI_util`); what they do shows only on hover. The right-most is cut off at the window edge: Wordclouds draws 71 px past its window | `GUI_util` I/O row |
| 4 | "Release 1.6.41/1.6.41": local/GitHub version, not explained | `GUI_util.py:533` |
| 5 | Nine controls of chrome on every analysis GUI: the chart row (Excel, Bar chart, No transformation, Data tools), even in tools that make no chart, plus Read Me, Watch videos, Open TIPS files, Open reminders, Setup. "Watch videos" is red in some GUIs and black in others; the colour code is not explained | `GUI_util.GUI_bottom` |
| 6 | Window titles all start "Graphical User Interface (GUI) for …" | `GUI_label` in each GUI |
| 7 | The grid spreads columns across the full 1350 px, so a value can sit far from its label (GIS "Country bias", N-grams "Options", Sample corpus "Date type"); columns do not line up across rows | grid layout |
| 8 | Disabled controls are very faint, and a disabled RUN looks almost like an enabled one; why it is disabled is said only in a popup at open | all |
| 9 | 14 GUIs show one to three popups before the window can be used, mostly "requires a csv FILE in INPUT; RUN is disabled": CoNLL table analyzer (2), PC-ACE data analysis (3), Excel charts (2), Data manipulation (2), Setup external software (2, one asks to watch a video), the menu (the "three setup options" question, removed in #1705), GIS Google Earth, GIS distance, GIS symbolic, Corpus checker, Data visualization, File classifier, File manager, Statistics csv | `check_IO_requirements`-style code at the end of each GUI |
| 10 | Mixed fonts: tab labels and section headings in red bold Courier (PC-ACE data analysis, Data visualization, Narrative analysis ALL); italic red headings in the welcome window | those GUIs |
| 11 | The five "ALL" hubs (File handler, File search, Semantic analysis, Sentiments & emotions, Syntactic analysis) are lists of "(Open GUI)" buttons, each with a HELP button. The menu's searchable tool list already does this | the `_ALL_main` GUIs |
| 12 | Column groups without headers: SVO's three Lemmatize/Filter groups do not say which parser each is | `SVO_main` |
| 13 | Every window is 1350 px wide (Wordclouds 1450, File search by word 1418) on a 1470 px screen, though most use the left half. None is taller than this screen | `get_GUI_width` |
| 14 | The menu mixes the CTk tool browser with the Tk header and footer; its footer still has RUN beside the browser's own Open button | `NLP_menu_main` |
| 15 | Old-style Tk sliders (`tk.Scale`) | Setup package & language, Semantic analysis (WSI) |

### 11.3 Bugs found along the way

- **Shape of Stories crashes at open** with the default config: `FileNotFoundError: 'lib/sampleData/newspaperArticles'` at `IO_files_util.py:1408`, called from `shape_of_stories_main.py:813`. `lib/config_defaults/NLP_default_IO_config.csv` stores relative paths (`lib/sampleData/newspaperArticles`, `NLP_output`), and importing `IO_files_util` runs `os.chdir` into `src/` (line 39), so they resolve under `src/`. PC-ACE data analysis says the same folder "does not exist". The zip build seeds `config/` from those defaults, and the menu's `ensure_default_configs` writes absolute paths only when the file is missing, so a fresh zip install probably hits this. **Check on a fresh 1.6.41 zip** (§1.1 row 4b). Fix: resolve relative config paths against `GUI_IO_util.NLPPath`; drop the `chdir`. Also check where `NLP_output` lands: possibly `src/NLP_output`.
- Not bugs: `NLP_setup_IO_main` refuses to run on its own (by design); `data_manipulation`, the menu and the setup GUIs build their window only under `__main__`.

### 11.4 Proposed order (not before 1.6.42; its own releases)

1. **Content and chrome first, no new toolkit** (11.2 #1–9, #11; decisions for Roberto): cut the welcome block to one line or nothing; replace the HELP column with an ⓘ beside each label that shows the same text; label or icon the four I/O buttons; show the chart row only in GUIs that chart; say why RUN is disabled next to RUN instead of in popups; shorter titles. Almost all of it lives in `GUI_util` and `GUI_IO_util`, so all 55 GUIs change at once.
2. **Bring the CTk groundwork over as new files** (no conflicts): `GUI_theme_util.py`, `ctk_bundle_util.py`, the theme JSON, `tests/ctk_bundle_smoke.py`. Run the bundle smoke test inside a built zip on Windows and on a Mac before anything uses it.
3. **CTk chrome:** `GUI_top`, `GUI_bottom`, the help/tooltip and popup widgets through the factories. Every GUI gets the new look outside its own rows.
4. **Per-GUI conversion in tranches**, re-running the branch's mechanical recipe on today's files instead of rebasing its 49 commits; use the branch commits as the reference for each GUI's quirks.
5. **Fold the hubs into the menu** (11.2 #11) and hide what the zip cannot run (§9.2).

Each PR carries before/after screenshots from a gallery script. Add one to `tests/` that runs on a Mac too (the branch's `gui_gallery.py` reads Windows screen scaling; on a Mac `screencapture -R` works, and the GUIs that build only under `__main__` need `runpy`).

## 12. The GitHub wiki (scan of 10 Nov 2026)

**How it was looked at:** cloned `NLP-Suite.wiki` (19 pages, last edit 23 Jun 2026), compared each page with its `docs/` copy, and grepped `src/`, `README.md`, the setup readmes and the wiki itself for `wiki/` links. Em dashes counted with `grep -o '—'`.

**The main problem is two copies.** `docs/` holds 11 pages that mirror the wiki (moved there 21 Jun) plus `Watch-YouTube-Videos.md`, which the wiki lacks. Nothing copies one to the other, so the `docs/` fixes in PR #1705 (§9.1) will not reach the wiki when it merges. The names do not match either, despite the 21 Jun commit "Standardize docs/ filenames to match GitHub wiki naming": `Installing-the-NLP-Suite` is `Installation-of-the-NLP-Suite` on the wiki, `The-History` is `A-Brief-History-of-the-NLP-Suite`, `How-to-Cite` is `How-to-Cite-the-NLP-Suite`, `Installing-External-Software` is `Install-External-Software`. `NLP-Suite-Architecture` exists only on the wiki.

### 12.1 Delete from the wiki (needs Roberto's yes)

| Page | Evidence |
|---|---|
| `Installation-Instructions-for-the-NLP-Suite` | Byte-identical to `Installation-of-the-NLP-Suite`; linked nowhere |
| `Supported-Systems-&-Languages` | Byte-identical to `Supported-Systems-Languages`; linked nowhere |
| `Download,-Install,-Update,-Run-the-NLP-Suite` | Linked nowhere; overlaps the install page. Its Update and Config Folder sections are not on the install page: merge them in (from the #1705 version of `docs/Download-Install-Update-Run.md`), then delete both the wiki page and the `docs/` file |
| `Install-Git`, `pip-install` | Feb 2022; for the Anaconda STEP2 install and git-based updates, both gone (§9.2 #1). Linked nowhere |

**Replace, not delete:** `Install-External-Software` (Oct 2022) tells users to install the Java JDK and CoreNLP. The #1705 version of `docs/Installing-External-Software.md` is current (optional tools, bundled fallbacks). Publish it under the wiki name and link it from the sidebar.

### 12.2 Broken links

| Link | Where | Fix |
|---|---|---|
| `wiki/Install-the-NLP-Suite` (no such page) | `README.md:9` (the main "Download and install" link), `README.md:38`; `setup_Mac/readme_Mac_beta.md`, `setup_Windows/readme_Windows_beta.md` | `Installation-of-the-NLP-Suite`. The setup readmes go in §10.1 |
| `wiki/NLP-Suite-Release-History` (no such page) | `README.md:42`, wiki `Home`, the Release history button (`GUI_IO_util.py:1135`) | Releases page or `CHANGELOG.md` (§9.2 #17) |
| `Watch-YouTube-Videos` (no such page) | Wiki `_Sidebar` | Publish `docs/Watch-YouTube-Videos.md`, or drop the entry |

`README.md` is changed by #1705, so its two fixes wait for that merge (CLAUDE.md: don't edit files in an open PR).

### 12.3 Pages in use that are out of date

| Page | Problem | Em dashes |
|---|---|---|
| `Installation-of-the-NLP-Suite`, `Troubleshooting` | Tell Mac users to use the "NLP Suite Mac Setup" app, removed in 1.6.33 for `Launch NLP Suite (Mac).command`. Fixed in `docs/` by #1705 | 12, 4 |
| `Home` | Says the build bundles BERT; models download on first use (README, §9.1). Links the missing Release History page | 16 |
| `What-the-NLP-Suite-Does` | spaCy (TextBlob) sentiment described wrongly; fixed in `docs/` by #1705 | 15 |
| `NLP-Suite-Architecture` | Linked from `README.md:40` but not in `docs/`. Broken image path (`images/lib/nlp-welcome.png`, should be `lib/images/`), "INDIPENDENTLY", and a section on running `*_main.py` from the command line that only applies to source installs | 0 |
| `About`, `Supported-Systems-Languages` | One em dash each; otherwise fine | 1, 1 |

Fine as they are: `How-to-Cite-the-NLP-Suite`, `License`, `A-Brief-History-of-the-NLP-Suite`, `The-NLP-Suite-Team`, `_Footer`.

About 50 em dashes on user-facing pages. The design notes in `docs/` have more (`CustomTkinter-Migration-Plan` 53, `Semantic_Aggregation_GUI_design` 41, `corpus_profiler_spec` 29, `Narrative_Symbolic_Space_design` 21, `Annotation_join_engine_design` 11), but no user sees them; leave them.

### 12.4 Proposed order

1. Merge #1705.
2. **Make `docs/` the source.** One PR: rename the `docs/` pages to the exact wiki names (so publishing is a plain copy), add `NLP-Suite-Architecture.md` from the wiki, fix 12.3 and the em dashes, merge the Download page into the install page (12.1), fix the `README.md` links (12.2).
3. **Publish to the wiki** by hand for 1.6.42: clone `NLP-Suite.wiki`, copy `docs/` over, delete the 12.1 pages, update `_Sidebar` (Install External Software in, Watch YouTube Videos in or out). The wiki is live once pushed, so Roberto looks first.
4. Later: a release step (or workflow on `current-stable`) that copies `docs/` to the wiki, so the two cannot drift again. Add it to §6.

## 13. Security alerts and the Python 3.11 release (scan of 11 Nov 2026)

Dependabot alerts on `current-stable`, read 11 Nov 2026 with `gh api repos/NLP-Suite/NLP-Suite/dependabot/alerts`. Versions below were checked with `uv pip compile requirements.txt requirements-windows.txt` (and the Mac platform) against PyPI on the same day; nothing was built or run.

### 13.1 What is open: 178 alerts

| Manifest | Pillow | transformers | stanza | protobuf | Closed by |
|---|---|---|---|---|---|
| `requirements.txt` (what the build installs) | 52 (4 critical) | 18 (6 high) | — | — | Pillow: #1688. transformers: §13.2 |
| `src/requirements.txt` | 51 | — | 1 | 2 | Deleting the file (#1706) |
| `src/requirements_mac.txt` | 50 | — | 1 | 3 | Deleting the file (#1706) |

- **108 of the 178 are in the two stale `src/` files**, which no build reads. #1706 deletes both, so they close when that reaches `current-stable` (Dependabot reads the default branch, not `roberto`). The stanza and protobuf alerts are only there: the root file leaves both unpinned, and today they resolve to stanza 1.15.0 and protobuf 7.36.2, above every fixed version.
- **Pillow 13.0.0 fixes all 52 in the root file**, and it needs Python 3.11 (no 3.10 wheels). That is #1688.
- **transformers 4.41.2 is the other 18**, and Pillow does not touch them. 14 are fixed by 4.53 (ReDoS, three untrusted-pickle loaders); 4 need 5.x: two remote-code-execution paths (fixed in 5.3 and 5.5), a `save_pretrained` path traversal (5.10) and the `Trainer` (5.0). transformers 5 also needs Python 3.11, so it can only move with #1688.
- **Not seen by Dependabot:** the SRL env (`setup_SRL.py`: `transformer-srl==2.4.6`, torch 1.7, allennlp, spaCy 2, Python 3.8). It is old and has known advisories of its own, but it is opt-in, local, and has no newer release to move to. Leave it; say so if anyone asks.

Practical exposure is low across the board (the Suite opens the user's own files and downloads fixed models from Hugging Face), but the critical Pillow ones are in JPEG and TIFF decoding, which any image input reaches.

### 13.2 What blocks transformers: `bert-extractive-summarizer`

The pin exists because `bert-extractive-summarizer` 0.10.1 (its last release, 2021) imports `TransfoXLModel` at load time (`summarizer/bert.py:12`), and transformers removed it in 4.52. So `import summarizer` fails on anything that fixes the alerts, and `BERT_util.py:50` imports it at module level, so every BERT GUI would fail to open, not only the summary.

It has **one caller**: `doc_summary_BERT`, `BERT_util.py:215`, `Summarizer()` then `bert_model(fullText, min_length=60)`. (It also builds the model inside the per-document loop, so it reloads bert-large-uncased once per file.)

**Fix (small, one PR, before the bump):** replace it with a function in `BERT_util` that does what the package does by default: split sentences, drop those under 60 characters, embed each with `bert-large-uncased` (mean of the second-to-last hidden layer), k-means with k = ceil(0.2 × sentences), keep the sentence nearest each centroid, in document order. transformers and scikit-learn are already requirements, so nothing new is added. Build the model once, outside the loop. Test the selection step (embeddings in, chosen sentence indices out) with synthetic vectors. Then drop `bert-extractive-summarizer` from `requirements.txt`. This works on today's 4.41.2 too, so it can land in any release before the bump.

The other transformers users look safe on 5.x from their imports: `BERT_util` (`AutoTokenizer`, `AutoModelForTokenClassification`, `pipeline`), `WSI_util` (`BertModel`, `BertTokenizer`), `sentence-transformers`, `bertopic`. **fastcoref 2.1.6 is the risk**: it subclasses `BertPreTrainedModel` and imports `transformers.activations.ACT2FN`. The imports still exist in 5.x, but it is unmaintained since 2023 and needs a real coreference run.

Resolution check: with Pillow 13.0.0 and `transformers>=5.10` on Python 3.11, both Windows and Mac resolve (transformers 5.22.2, tokenizers 0.23.3, sentence-transformers 6.3.0, fastcoref 2.1.6, bertopic 0.17.4).

### 13.3 Proposed release: 1.6.43

The Python bump means users download a new bundled Python (the whole env is rebuilt), so if something breaks it should be clear it was the bump. Proposal: 1.6.43 is this release and nothing else; #1682 and §8.3 (now in §1.4 item 5) move to 1.6.44. Roberto's call.

Prerequisites, in order:
1. #1705 and #1706 are merged (1.6.42 plan). #1706 deletes `src/requirements*.txt` and the STEP1–3 scripts, which also settles two of #1688's open review points: its `src/requirements.txt` hunk goes away, and nothing left creates a `python=3.8` env.
2. The summarizer PR (§13.2), on its own.
3. Rebase #1688 onto `roberto` after both (its `requirements.txt` hunk sits next to #1705's lines; its `src/requirements.txt` hunk becomes a modify/delete conflict: drop it).

What #1688 then carries, beyond the 3.10 → 3.11 workflow and Pillow change it already has:

| Change | File | Why |
|---|---|---|
| `transformers>=5.10` (was `==4.41.2`; rewrite the comment) | `requirements.txt` | Closes the other 18. If fastcoref fails on 5.x: `transformers>=4.53,<5` closes 14 and leaves the 4, and still needs §13.2 |
| `stanza>=1.12.2` (was unpinned) | `requirements.txt` | No-op today (resolves 1.15.0), but stops a cached or constrained resolve from going back below the pickle-RCE fix |
| `target-version = "py311"`, `"pythonVersion": "3.11"` | `pyproject.toml`, `pyrightconfig.json` | #1688 left them at 3.10; nothing else open touches them now |
| "Python 3.8"/"3.10" comment | `NLP_Suite.spec` | Already §9.2 #15 |
| Pillow bullet; "CI Python" bullet → 3.11 | PLAN §6 | Settled decisions |
| Security line: "Pillow 13 and transformers 5 fix N advisories; the app now runs on Python 3.11" | `CHANGELOG.md` | User-facing |

Checks before tagging, added to #1688's own list (installer build on both OSes, welcome screen and logo, `gui_smoke.py` on 3.11, Google Earth icon preview, one heavy pipeline, SRL still runs):
- BERT: NER, document summary (the §13.2 replacement), word embeddings, sentiment, WSI. Each downloads its model on first use, so test on a clean Hugging Face cache once.
- Coreference with the BERT (fastcoref) engine, end to end.
- BERTopic topic modeling.
- The self-updater from 1.6.42 → 1.6.43: the first update that replaces the bundled Python itself.
- After the promotion to `current-stable`: re-read the Dependabot list; expect 0 open.

Not needed: protobuf (transitive, resolves to 7.36.2), or a `.github/dependabot.yml` (alerts work without one; version-update PRs would fight the deliberate pins).
