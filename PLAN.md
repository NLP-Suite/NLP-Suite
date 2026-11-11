# PLAN — NLP Suite

What to do before tagging the next release, and what comes after it. The findings behind each future item (evidence, line numbers, proposed fixes) are in [docs/future-work.md](docs/future-work.md). How to fix an issue is in [CLAUDE.md](CLAUDE.md#fixing-an-issue). What has shipped is in [CHANGELOG.md](CHANGELOG.md).

**Last updated:** 11 Nov 2026. v1.6.41 released 10 Nov; 1.6.42 to be tagged the week of 16 Nov.

## Before tagging 1.6.42

1.6.42 is the first release that students' copies install by themselves (1.6.41 → 1.6.42), so the updater gets its first real, full-size run. Its scope is closed: what is merged into `roberto` (#1704, #1705, #1711, #1712, #1714, #1715, #1716) is what ships. CHANGELOG's Unreleased section covers all of it.

1. **#1705 on Windows.** Open the menu with an empty `config/`, and open each Setup GUI. Most of the start-up popups #1705 changed were Windows text, and it has only been checked on a Mac.
2. **#1704 where it was not checked:** the first Stanza download on a machine with no model, and Windows.
3. **Build the release candidate and do the usual checks** ([future-work §14](docs/future-work.md#14-requirements-release-checks-and-settled-decisions)): unzip both artifacts, confirm `Launch NLP Suite (Mac).command` and the Windows entry point, confirm the app imports, and confirm `lib/release_manifest.tsv` is in both zips.
4. **First run on the release-candidate zip, with no `config/`:** Shape of Stories opens (#1711), Sample corpus opens (#1714), and the first RUN creates `NLP_output` (#1716).
5. **Release:** retitle CHANGELOG's Unreleased section to v1.6.42; Roberto promotes `roberto` → `current-stable` and sets `lib/release_version.txt` to 1.6.42, which must equal the tag; then the tag.
6. **Right after the zips are up, update a real 1.6.41 install** on Windows and on a Mac: close it, accept the update, and check that config and user files survive and that `NLP_Suite_previous` is gone after the next start. Read `%TEMP%\NLP_Suite_update.log` (Mac: the log named in the message). This is the first full-size run; the 9 Nov test used a 26 MB stand-in release on localhost.
7. **Not yet tested by hand:** a source checkout on `current-stable` updating with git; opening and closing a GUI offline (no popups expected).

After the tag, ask students who report update problems to send that log to coralynn.yang@emory.edu.

## Future work

Details in [docs/future-work.md](docs/future-work.md); section numbers below refer to it.

**1.6.43 (proposed): dead files and bundle size.** Both change what the build ships, so they go out together.
- PR #1706 deletes the legacy setup scripts and unused files (§1.1). Rebase it on `roberto` first; it conflicts with #1705 in `README.txt` and `CLAUDE.md`. Deleting `src/requirements*.txt` also closes 108 of the 178 Dependabot alerts (§3.1).
- Drop TensorFlow, which nothing imports (§2.2), then trim `NLP_Suite.spec` to what the menu needs (§2.1), and remove the requirements that nothing imports (§2.3).

**1.6.44 (planned): the HW 5 tools** (§4), issues #1718–#1724: Shape of Stories, NRC, SentiWordNet, spaCy sentiment, CoreNLP memory, vocabulary, language detection. QTM 446W's HW 5 is due Sun 6 Dec. #1722 and #1719 first.

**Python 3.11 security release** (§3): the summarizer replacement (§3.2), then #1688 rebased with Pillow 13 and transformers 5. It needs #1706 merged first. Its release number has to be settled against 1.6.44.

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
