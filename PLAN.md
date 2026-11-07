# PLAN — NLP Suite open work

What's open, what to close, what to fix next. How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue).

**Last updated:** 7 Nov 2026, against `roberto` @ `43cbca1c` (v1.6.40). Replaces `docs/techdebt.md` (16 Jul 2026 audit); its numbers are re-measured in §5.

**State on GitHub (7 Nov 2026):** 255 open issues, 11 open PRs. Nothing below has been closed or changed on GitHub yet: the lists are proposals for Roberto.

## Contents

1. [Next steps](#1-next-steps)
2. [Open pull requests](#2-open-pull-requests)
3. [Recent issues (2025–2026)](#3-recent-issues-20252026)
4. [The 2021–2024 backlog](#4-the-20212024-backlog)
5. [Tech debt](#5-tech-debt)
6. [Requirements and release checks](#6-requirements-and-release-checks)
7. [Branches](#7-branches)
8. [Done](#8-done)

---

## 1. Next steps

In order:

1. **Review the six open collaborator PRs** (§2). They're small, tested, and all target `roberto`. Merging them first keeps the issue work from colliding with them.
2. **Close the four stale 2024 PRs** (§2) with a short thank-you comment.
3. **Retest and close the recent issues that releases may have fixed** (§3, "Retest" rows).
4. **Fix the open recent bugs** (§3, "Bug" rows), one branch and test each, per CLAUDE.md.
5. **Triage the 2021–2024 backlog** (§4). Proposal: bulk-close the stale ones with a comment inviting a reopen.
6. **Burn down tech debt** (§5) in the listed order.
7. **Add the missing regression tests** named in the issue workflow: an empty-DataFrame test and a multi-column chart test for `charts_util` (§5.6).

## 2. Open pull requests

None of these is merged into `roberto` (checked with `git merge-base` and `git cherry`).

| PR | Opened | Author | What | Proposal |
|---|---|---|---|---|
| #1699 | 2026-10-29 | coralynnkc | GIS geocode cache survives runs, never caches errors (stacked on #1692, which is merged) | Review. Already merged on `cora-batch-2` |
| #1688 | 2026-10-26 | coralynnkc | Spike: Python 3.11 build so Pillow can go to 13.0.0 (security advisory GHSA-c6hw-5grf-ff96) | Decide. Touches the build Python and Pillow pin (§6) |
| #1683 | 2026-10-16 | coralynnkc | Gender dictionary annotator looks up only PERSON tokens | Review |
| #1682 | 2026-10-16 | coralynnkc | spaCy CoNLL ID/HEAD sentence-level and 1-based | Review. **Changes a shared CoNLL structure**: check every reader of ID/HEAD |
| #1679 | 2026-10-14 | coralynnkc | CoNLL search applies the DEPREL filter; outputs go beside the analyses | Review |
| #1656 | 2026-09-15 | coralynnkc | Nominalization: one batched tagging call per document | Review |
| #1651 | 2026-07-23 | coralynnkc | CustomTkinter migration, all ~50 GUIs (49 commits) | Decide. Large; the menu already uses customtkinter. Likely needs a rebase; see `docs/CustomTkinter-Migration-Plan.md` |
| #1528 | 2024-09-18 | CallaGong | "dictionary functionality" | **Close**: targets `current-stable`, 2 years old |
| #1525 | 2024-09-08 | esunn0412 | Generalized Excel file reads (27 commits) | **Close**: targets `current-stable`, 2 years old |
| #1436 | 2024-03-17 | razzak-ammar | Document Statistics sentence-length fix | **Close**: from a fork's `current-stable`. Check that the bug is fixed first; v1.6.39 rewrote sentence statistics |
| #1383 | 2024-01-31 | Eli-Todd | Alternative STEP2 install script | **Close**: install was rebuilt around PyInstaller |

## 3. Recent issues (2025–2026)

"Retest": a later release says it fixed this or something close. Rerun on v1.6.40 and close if it's gone.

| # | Title | Kind | Note |
|---|---|---|---|
| 1671 | BERT word embeddings are context-free | Design | Each word is encoded alone, so vectors don't depend on the corpus. Affects a homework question. Decide: keep, document, or encode in context |
| 1653 | Windows zip: JavaScript paths too long under `AppData\Local\Programs` | Bug | MAX_PATH in bundled node_modules. Shorten in the build or document the install location |
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

### 5.2 Error handler that crashes: `IO_files_util.py` ~line 292: **still open**

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
- Formatting split is resolved: `src/` was reformatted in v1.6.40. Tab-indented lines remain in 2 files.
- Large modules (lines): `DB_PCACE_data_analysis_util` 7,731 · `charts_util` 5,620 · `corpus_profiler_util` 4,191 · `Stanford_CoreNLP_util` 3,563 · `statistics_txt_util` 3,033. When you open one for a feature, pull testable helpers out instead of adding in place.
- About 900 `print()` calls. Move to `logging` over time.

**Order:** §5.2 → F821 file by file → bare excepts on user paths → B023 → B006 → eval/shell.

## 6. Requirements and release checks

- **coreferee** was removed from `requirements.txt` (it pins `spacy<3.6` and broke the PyInstaller build). `fastcoref` replaces it. spaCy is unpinned. No `spacy<3.8` pin exists any more.
- **Pillow** is pinned to 10.4.0 (12.x breaks the bundled Tcl/Tk 8.6). PR #1688 tests Python 3.11 + Pillow 13 for the security advisory; decide on it before the next release.
- **CI Python:** 3.10 for tests and installers. SRL stays on its own 3.8 env.
- **Mac runners:** `macos-15` since 2 Nov 2026 (`macos-14` retired).
- **Before the next tag:** build, unzip both artifacts, confirm `Launch NLP Suite (Mac).command` and the Windows entry point exist, confirm the app imports, then draft the CHANGELOG section. `lib/release_version.txt` is 1.6.40.

## 7. Branches

Remote branches besides `roberto`, `current-stable`:

- `cora-batch-2` (30 Oct 2026): collaborator staging, holds a merge of #1699. Not in `roberto`.
- `mac-font-pin` (22 Jul 2026): not in `roberto`, no open PR. Check whether it's still needed.
- `dictionary` (Sep 2024), `taeeun` (Dec 2024): heads of stale PRs #1528 and #1525. Delete after those PRs are closed.
- `remove_shortcut_prompt` (2021), `tony` (2023): no open PR. Delete candidates.

Deleting a remote branch is Roberto's call.

## 8. Done

Since the 16 Jul audit:
- `data_manipulation_main.py`: the unbound `comingFrom_Plus`/`comingFrom_OK` crash and the duplicate `build_extract_string` are gone.
- One-shot Ruff format of `src/` (v1.6.40).
- Unused imports and invalid escape sequences cleared.
- Test suite grew from 3 to 508 tests. `gui_layout_gate.py` added.
- coreferee removed.
