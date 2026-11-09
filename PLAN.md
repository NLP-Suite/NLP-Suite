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

Tests on Windows: the updater's PowerShell swap runs for real in `pytest` (normal update, unmarked `_previous`, marked one, an edited release file, a folder named with ’ and brackets); the Mac `sh` swap was run the same way under Git's `sh` (CI runs it on Linux).

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
