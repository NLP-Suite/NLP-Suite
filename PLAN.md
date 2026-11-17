# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 17 Nov 2026. v1.6.42 released 17 Nov. Releases are now Cora's (handed over by Roberto).

## After the 1.6.42 tag

1.6.42 is the first release that students' copies install by themselves (1.6.41 → 1.6.42), so the updater gets its first real, full-size run. It ships #1704, #1705, #1711, #1712, #1714, #1715, #1716 and #1726.

Checked on the 17 Nov release candidate (Mac, macOS 26.5.2): both zips hold the entry point, `lib/release_manifest.tsv` and the default `config/`; the app opens; Shape of Stories, Sample corpus and Wordclouds open; the first RUN creates `NLP_output`; the first Stanza download works (it crashed the first candidate: #1725, fixed by #1726).

1. **Not checked on Windows before the tag:** #1705's start-up popups (menu with an empty `config/`, each Setup GUI) and #1704's first Stanza download. Do both on the released Windows zip.
2. **Update a real 1.6.41 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). This is the first full-size run; the 9 Nov test used a 26 MB stand-in release on localhost.
3. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

Ask students who report update problems to send that log to coralynn.yang@emory.edu.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**1.6.43: bundle size, small speed-ups and copy** is on `spike/1.6.43-bundle-size` (13 Nov), with a CHANGELOG section: TensorFlow and 14 unused requirements dropped (§2.2, §2.3), the spec trimmed to the menu (§2.1: `_internal/` 496 → 187 MB on a local Mac build), TIPS recompressed (§2.4), `setup_Windows/`, `setup_Mac/` and `src/requirements*.txt` deleted (108 alerts), transformers 4.51.3 (7 alerts), `requests` out of every window's start-up and two timeouts (§6.3, §6.6), the welcome redirect before `import GUI_util` (§6.7), and part of §5.2's copy. **No `src/*.py` file was deleted:** the dead modules of PR #1706 stay until Roberto agrees; #1706 needs a rebase onto this branch, dropping what it already does. Before tagging: run `build-installers.yml` on the branch (workflow_dispatch) and do §2.5's checks, which a Mac without the CI env could not: zip sizes on both OSes, the menu from each zip, and one tool per family on `python-env`.

**1.6.44 (planned): the HW 5 tools** (§4), issues #1718–#1724: Shape of Stories, NRC, SentiWordNet, spaCy sentiment, CoreNLP memory, vocabulary, language detection. QTM 446W's HW 5 is due Sun 6 Dec. #1722 and #1719 first.

**Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs the 1.6.43 branch merged first (it deletes `src/requirements*.txt`, which #1688 edits). Its release number has to be settled against 1.6.44.

**Later, unscheduled:**
- The rest of the smaller copy left over from #1705 (§5.2; the Setup item name, the CLOSE hover and Word2Vec are done on the 1.6.43 branch), and the repeated config warning on a first run from source (§5.3).
- Roberto's decisions on outdated flows: SRL in the zip, Java row, coreference default, N-grams VIEWER, MALLET coherence, reminders (§5.1).
- PR #1682 (spaCy CoNLL IDs, a shared structure) and PR #1683, which needs changes (§9). Close the four stale 2024 PRs with a thank-you comment.
- Retest and close the recent issues that releases may have fixed; fix the open recent bugs (§10). Triage the 2021–2024 backlog (§11).
- Performance, in §6.10's order (next: pandas out of `GUI_util`, §6.3; requests is done on the 1.6.43 branch).
- The updater's known limits: long paths, no checksum or resume, the GitHub API rate limit, and the silent `git stash` (§15).
- The GitHub wiki: make `docs/` the source, then publish (§8).
- UI overhaul (§7), as its own releases.
- Tech debt in §12's order, and the missing chart regression tests (§12.6).
- Stale remote branches (§13); deleting them is Roberto's call.
