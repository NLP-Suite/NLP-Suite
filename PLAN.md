# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 17 Nov 2026. v1.6.42 released 17 Nov. Releases are now Cora's (handed over by Roberto).

## After the 1.6.42 tag

1.6.42 is the first release that students' copies install by themselves (1.6.41 → 1.6.42), so the updater gets its first real, full-size run. It ships #1704, #1705, #1711, #1712, #1714, #1715, #1716 and #1726.

Checked on the 17 Nov release candidate (Mac, macOS 26.5.2): both zips hold the entry point, `lib/release_manifest.tsv` and the default `config/`; the app opens; Shape of Stories, Sample corpus and Wordclouds open; the first RUN creates `NLP_output`; the first Stanza download works (it crashed the first candidate: #1725, fixed by #1726).

1. **Not checked on Windows before the tag:** #1705's start-up popups (menu with an empty `config/`, each Setup GUI) and #1704's first Stanza download. Do both on the released Windows zip.
2. **Update a real 1.6.41 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). This is the first full-size run; the 9 Nov test used a 26 MB stand-in release on localhost.
3. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

**Found after the tag (#1728):** on a new install, the 13 GUIs that import `Stanza_util` closed as they opened (Shape of Stories among them; HW 5 is due 6 Dec). Fixed on `roberto`. **1.6.43** ships it with #1731 (the menu's language advisor said Stanza supports no language) and a small links-and-copy PR (README and Release history links, the Word2Vec launch, the §5.2 copy outside the HW 5 files). Then 1.6.44 for HW 5, and bundle size in 1.6.45.

Ask students who report update problems to send that log to coralynn.yang@emory.edu.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**1.6.44 (planned): the HW 5 tools** (§4), issues #1718–#1724: Shape of Stories, NRC, SentiWordNet, spaCy sentiment, CoreNLP memory, vocabulary, language detection. QTM 446W's HW 5 is due Sun 6 Dec. #1722 and #1719 first.

**1.6.45 (proposed): dead files and bundle size.** Both change what the build ships, so they go out together, after HW 5.
- PR #1706 deletes the legacy setup scripts and unused files (§1.1). Rebase it on `roberto` first; it conflicts with #1705 in `README.txt` and `CLAUDE.md`. Deleting `src/requirements*.txt` also closes 108 of the 178 Dependabot alerts (§3.1).
- Drop TensorFlow, which nothing imports (§2.2), then trim `NLP_Suite.spec` to what the menu needs (§2.1), and remove the requirements that nothing imports (§2.3).

**1.6.46 (proposed): the Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs #1706 merged first (1.6.45).

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
- Stale remote branches (§13); deleting them is Roberto's call.
