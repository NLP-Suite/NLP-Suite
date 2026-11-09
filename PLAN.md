# PLAN — NLP Suite open work

What's open, what to close, what to fix next. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md), not here.

**Last updated:** 9 Nov 2026, against `roberto` @ `78b383d3` (v1.6.40 released 7 Nov).

**State on GitHub (9 Nov 2026):** 12 open PRs; 255 open issues on 7 Nov, plus #1700. Nothing below has been merged, closed or commented on GitHub: the lists are proposals for Roberto.

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

A patch release. **Top priority: auto-update works for students** (issue #1700). Everything else in it is a small, low-risk fix that is ready now.

### 1.1 Why auto-update is broken (v1.6.40 and earlier)

Checked in `src/GUI_util.py` and `src/NLP_setup_update_util.py` on `roberto`:

- **Zip (installer) build:** on every close with a newer release out, `update_self` asks for pygit2, which the spec excludes and students cannot install. The folder has no `.git`, so a git pull could not work anyway.
- **Source checkout:** the "is Git installed?" test runs `git pull` on whatever branch is checked out, *before* the check that only `current-stable` is updated. A developer on `roberto` gets pulled.
- **The exit test is a string `!=`**, not a version comparison: offline (`0.0.0`) or a developer copy ahead of GitHub also starts an update.
- **The rebuild path for a broken `.git` ran `git init ..`** relative to the launch folder, not the NLP Suite folder.
- **The launch-time "NLP Suite Outdated" popup** (`check_GitHub_release`, not touched by either PR) tells every user to install Git and to close and reopen to update, and links the old wiki release history. It also fires as soon as `current-stable`'s `release_version.txt` changes, before the tag's zips exist.
- **Offline, the version check stacks modals:** `get_GitHub_release_version` calls `check_internet_availability_warning` (an askyesno) and runs up to three times per window (open, CLOSE, `exit_window`), plus the "0.0.0" `showwarning` on open. The `silent` parameter it takes is never used.

### 1.2 In 1.6.41

| # | What | Status | Before merging |
|---|---|---|---|
| A | **PR #1701**: auto-update without pygit2; zip builds sent to the release page; git runs in `NLPPath`; `git pull` no longer used as the Git test; real version comparison | Merges cleanly | Fix review items in §1.4; drop its §8 "Done" line from PLAN.md on rebase (§8 is gone) |
| B | **PR #1702** (stacked on #1701): the zip build downloads and installs new releases itself | Merges cleanly | Fix review items in §1.4; **one real Windows update** (PR's own steps); drop its §8 "Done" lines from PLAN.md on rebase |
| C | **Launch-time popup** (`GUI_util.check_GitHub_release`): say "close the NLP Suite to install it" for zip builds, mention Git only for source checkouts, link `releases/latest` (or CHANGELOG) instead of the wiki, and stay quiet until the release for that version exists (same test #1702 uses) | Not started | New small PR; test the message choice |
| D | **Quiet offline check**: `get_GitHub_release_version(silent=True)` from `display_release`, `_close_window` and `exit_window`, no askyesno and no "0.0.0" popup; call it once per close, not twice | Not started | Same PR as C |
| E | Remove the dead pygit2 warning in `IO_libraries_util.py` (~line 163) and the `pygit2` line in `NLP_Suite.spec` excludes | Not started | Same PR as C, after #1701 |
| F | **#1699** (GIS cache), **#1679** (CoNLL DEPREL filter), **#1656** (nominalization batching) | Reviewed, tests pass (§3) | #1679 and #1656: rebase on `roberto` (ruff-only conflicts) |

### 1.3 Not in 1.6.41

- **PR #1688** (Python 3.11 + Pillow 13): changes the build Python for every user. Its own release, after auto-update is proven, so a bad build can be fixed by the new updater.
- **PR #1682** (spaCy CoNLL ID/HEAD): correct, but it changes a shared CoNLL structure. First thing after 1.6.41 (§3).
- **PR #1683** (gender dictionary): needs changes (§3).
- Backlog triage (§5) and tech debt (§6): no code risk in a release that must not break the updater.
- Windows long-path issue #1653: affects where the self-updater unpacks, so note it, but fix it separately.

### 1.4 Review of the auto-update PRs

Reviewed 9 Nov 2026 by reading the code (line numbers are in each PR's `src/NLP_setup_self_update_util.py` / `src/NLP_setup_update_util.py`) and by running `pytest tests/` on Windows on #1702's head: 647 passed, 14 skipped; the same 2 failures as on `roberto` (`test_cmap_guard`, `test_xml_entities`, local pdfminer/lxml). **The Windows PowerShell swap test ran and passed** on a temporary folder. That check was missing from the PR. Not yet run: a real update with the app open and the 1.5 GB download.

**#1701: ship, with one fix.**
- *Should fix:* when `git rev-parse` fails for any reason, `update_self` deletes `.git` and rebuilds it. Git also fails with "detected dubious ownership" (folder owned by another account, common on lab machines and OneDrive), and that is not damage. Rebuild only when git says the folder is not a repository or is corrupt; otherwise show the error and stop.
- Minor: the `current-stable` update still runs `git add -A` + `git stash` silently, so a user's local edits go into a stash they don't know about. Same as before; say so in the message.

**#1702: don't ship until 1 and 2 are fixed.**
1. **Blocker:** the swap script deletes any existing `<folder>_previous` (`rm -rf "$OLD"` ~line 252; `Remove-Item $Old` ~line 341) without checking for the backup marker. A backup kept *because* files were not carried over is wiped by the next update, and so is a user folder that happens to have that name. Delete it only when the marker is there; otherwise stop.
2. **Blocker:** only top-level items count as "user-added" (~lines 268 and 364). An edit or added file inside a shipped folder (`lib/sampleData`, `lib/wordLists`, custom dictionaries) is not carried over, the backup is still marked complete, and it is deleted on the next start. At least: list such files and keep the backup unmarked; better, compare against the old release's file list. The reverse also happens: files the old release shipped and the new one dropped are carried over as "user files" and pile up.
3. *Should fix:* if both the move-in and the rollback fail, `Fail` deletes the staged copy, leaving the app only as `_previous`, while the message says the current version still works (~347, ~255).
4. *Should fix:* `_delete_backup` (~385) removes the marker even when `rmtree(ignore_errors=True)` left locked or long-path files, so the leftover gigabytes are never cleaned up.
5. *Should fix:* nothing checks that the detached PowerShell actually started (group policy / AppLocker can block `-ExecutionPolicy Bypass`). The user waits for a message that never comes, ~3.5 GB stays in `_update`, and updates are blocked for 24 h.
6. *Should fix:* silent failures in the windowed app: missing asset or release/version mismatch only print to the console (~537); a `PermissionError` from `claim_stage` (~134, only `FileExistsError` caught) falls into `exit_handler`'s bare `except: print`.
7. *Should fix:* `_ps_quote` (~286) doubles only `'`; PowerShell also closes single-quoted strings on the curly quotes ‘ ’, so a folder like `Maria’s` breaks the script.
8. *Should fix:* OneDrive-synced folders (Documents is often redirected) are not detected; unpacking ~100k files there starts a multi-GB upload, and OneDrive's open handles can make the renames fail. Warn or refuse.
9. *Should fix:* staging is 17 characters deeper than the install, so without LongPathsEnabled the deep `node_modules` paths (#1653) fail to unpack. Fails safely, but the user can't update.
10. Minor: Ruff PLR0917 (too many positional arguments) at ~210 and ~290 will fail pre-commit. No checksum (GitHub's asset `digest` is unused), no resume. Ctrl-C leaves staging and blocks updates for 24 h. GitHub's 60 requests/hour unauthenticated limit will hit shared campus IPs (the fallback message is fine).

**Hand checks on Windows before tagging** (against a fake newer release): a real swap from Downloads, from an OneDrive Documents folder, and from a path with a space and an apostrophe; a tool and a CoreNLP `java` still running; reopening the app mid-swap; an existing `_previous` folder; an edited `lib/sampleData` file; a managed (group-policy) machine.

**If #1702 isn't ready in time**, ship 1.6.41 with #1701 alone (plus C–E). Zip users then get a working "download the new release" page instead of the pygit2 message, and #1702 goes in 1.6.42. Either way the first real self-update is from 1.6.41 to the next release.

### 1.5 Release steps

1. Merge A, B, C/D/E and the §3 "1.6.41" PRs into `roberto`, in that order. Rerun `pytest tests/` and `python tests/gui_smoke.py`.
2. **Hand checks** (not covered by CI):
   - Windows: one real self-update, using #1702's steps (unzip v1.6.40, swap in this `src/`, set `lib/release_version.txt` to 1.6.39, start with `python-env\python.exe src\NLP_menu_main.py`, close, accept). Check config and user files survive and `_previous` is removed on the next start.
   - Windows: a source checkout on `current-stable` updates with git; one on `roberto` is left alone.
   - Offline: open and close a GUI with the network off; no popups.
3. Bump `lib/release_version.txt` to 1.6.41, turn CHANGELOG's "Unreleased" into "v1.6.41", promote `roberto` → `current-stable`, tag `v1.6.41` on that commit. Then the usual artifact check (§7).
4. **Tell users once, by hand.** v1.6.40 and older zips don't have the new code: when 1.6.41 is out they will still show the pygit2 message (or the Git download page) on close. Students must download 1.6.41 from the release page once; from 1.6.41 on, closing the app updates it. Put this at the top of the 1.6.41 release notes and in a course announcement.

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

Checked 9 Nov 2026 against `roberto` @ `78b383d3` with `git merge-tree` (nothing merged). The four older collaborator PRs conflict mostly because v1.6.40 reformatted all of `src/` (PR #1687).

"Tests" = the PR's own new tests, run on Windows in the NLP env on 9 Nov.

| PR | Opened | What | Merge | Tests | 1.6.41? | Review |
|---|---|---|---|---|---|---|
| #1701 | 11-09 | Auto-update without pygit2 | Clean | Pass | **Yes** (A) | §1.4. Fix the `.git` rebuild on "dubious ownership" |
| #1702 | 11-09 | Zip build updates itself (stacked on #1701) | Clean | Pass, incl. Windows PowerShell swap | **Yes, if fixed** (B) | §1.4. Two blockers; hand checks on Windows |
| #1699 | 10-29 | GIS geocode cache in `config/`, keyed on geocoder settings, errors (403/429/timeouts) never cached | Clean | 9 pass | **Yes** | Correct. Follow-up, not blocking: after the first 403/429 it keeps calling Nominatim for every remaining place with no 1 s pause (~line 289); stop after the first |
| #1679 | 10-14 | CoNLL search applies the DEPREL filter (`filter_list_by_deprel` was never called); outputs go beside the analyses, none lost | Conflict: ruff only, mechanical | 4 pass | **Yes, after rebase** | Correct. Fixes the first symptom of #1561; keep #1561 open until its crash is reproduced |
| #1656 | 09-15 | Nominalization: one batched tagging call per document | Conflict: ruff only, mechanical | 11 pass | **Yes, after rebase** | Same matches as before; one warning instead of one per sentence. Check `bulk_process` exists in the pinned stanza 1.5.1 |
| #1682 | 10-16 | spaCy CoNLL ID/HEAD sentence-level and 1-based | Conflict: ruff only, mechanical | 2 pass | No: after 1.6.41 | Correct: Stanza and CoreNLP already write 1-based, sentence-level, root 0, and no reader compensates for spaCy's old values. Shared structure, so not in a release about the updater. spaCy tables already on disk stay 0-based: say "re-parse" in the CHANGELOG |
| #1683 | 10-16 | Gender dictionary looks up only PERSON tokens | Conflict: ruff only | 5 pass | No | **Needs changes:** hardcodes `Stanford_CoreNLP_util.CoreNLP_annotate` whatever parser is configured (so the option now needs Java); returns `''` with no message when no NER csv comes back; once "Will" is a PERSON anywhere, every "will" is tagged |
| #1688 | 10-26 | Python 3.11 build so Pillow can go to 13.0.0 | Conflict: 2 adjacent lines | CI only | No (§1.3) | Decide. Whole pinned stack must rebuild on 3.11. STEP2 scripts still create `python=3.8` envs (`setup_Windows/STEP2-install_NLP-Suite.ps1:12`, `setup_Mac/STEP2-install_NLP-Suite.command:35`) and `pyproject.toml`/`pyrightconfig.json` say py310; the PR touches none of them |
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
| 1700 | Auto-update fails on most student machines: asks for pygit2 | Bug | **1.6.41** (§1). Fixed by PRs #1701 + #1702 |
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
- **pygit2** is no longer a requirement once #1701 merges: the source-checkout updater uses the `git` program. Don't re-add it.
- **Pillow** is pinned to 10.4.0 (12.x breaks the bundled Tcl/Tk 8.6). PR #1688 tests Python 3.11 + Pillow 13 for the security advisory; after 1.6.41 (§1.3).
- **CI Python:** 3.10 for tests and installers. SRL stays on its own 3.8 env.
- **Mac runners:** `macos-15` since 2 Nov 2026 (`macos-14` retired). No Intel Mac build.
- **`src/` is Ruff-formatted** (v1.6.40). PRs opened before that need a rebase, not a hand merge.
- **Update order matters.** The in-app check reads `current-stable`'s `lib/release_version.txt`, which changes before the tag's zips finish building. #1702's self-updater waits until the release for that version exists; the launch popup should too (§1.2 C).
- **Before every tag:** build, unzip both artifacts, confirm `Launch NLP Suite (Mac).command` and the Windows entry point exist, confirm the app imports, then draft the CHANGELOG section. `lib/release_version.txt` must equal the tag (CI enforces it).

## 8. Branches

Remote branches besides `roberto`, `current-stable`:

- `cora-batch-2` (30 Oct 2026): collaborator staging, holds a merge of #1699. Not in `roberto`.
- `mac-font-pin` (22 Jul 2026): not in `roberto`, no open PR. Check whether it's still needed.
- `dictionary` (Sep 2024), `taeeun` (Dec 2024): heads of stale PRs #1528 and #1525. Delete after those PRs are closed.
- `remove_shortcut_prompt` (2021), `tony` (2023): no open PR. Delete candidates.

Deleting a remote branch is Roberto's call.
