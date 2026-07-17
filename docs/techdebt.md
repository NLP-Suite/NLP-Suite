# Technical Debt Audit — NLP Suite

**Date:** 2026-07-16 · **Branch audited:** `roberto` @ `a5849717` (tag `v1.6.22` + 2 commits)
**Method:** Ruff 120-rule sweep over all of `src/` (211 files, ~109k lines), Pyright spot checks on recently changed files, anti-pattern greps (silent failures, `eval`, `shell=True`), documentation cross-check, branch classification. Every finding below carries a file:line and a confidence level (High = tool-confirmed and manually verified; Medium = tool-flagged, pattern-consistent; Low = suspicion).

This document catalogues debt — it does not fix it. Items are ordered by risk, so it can be burned down top-to-bottom.

---

## 1. Critical — latent crashes and broken error paths

### 1.1 Undefined names: 68 latent `NameError` crashes (Ruff F821) — High confidence

Each of these is a code path that **cannot execute** — reaching it raises `NameError`. They are concentrated in less-trafficked tools, which is exactly why they survive: nobody has walked that branch recently. Per-file counts:

| File | Count | Examples |
|---|---|---|
| `social_science_research_main.py` | 8 | `chartPackage`, `dataTransformation` (lines 188–255), `startTime` |
| `syntactic_analysis_ALL_main.py` | 7 | `Word2Vec_Dir`, `k_means_min_var`, `ngrams_menu_var`, `top_keywords_var` (89–96) |
| `GIS_file_check_util.py` | 5 | `np` (60), `numColumns` (105–117), `msgTooFewColumnsForGeocoded` (114) |
| `Gephi_util.py` | 5 | `attvalue_xml` (579–912), `type_choices` (302) |
| `file_spell_checker_util.py` | 5 | `nltk` (295, 905, 930), `speller` (671), `inputFilename` (249) |
| `CoNLL_function_words_analysis_util.py` | 5 | `stats_pronouns`/`_prepositions`/`_articles`/`_conjunctions`/`_auxiliaries` (73–314) |
| `SENNA_util.py` | 4 | `scriptName` (89), `openOutputFiles`, `chartPackage`, `dataTransformation` (422) |
| `IO_files_util.py` | 3 | see 1.2 and 1.3 below |
| 21 more files | 1–2 each | `semantic_analysis_main.py` (`Word2Vec_Dir`, `outputDir`), `sample_corpus_main.py`, `nyt_api_call.py`, `Stanford_CoreNLP_port_util.py` (`sys` not imported), `BERT_util.py` (`main`), … |

Full list: `ruff check src/ --select F821`.

**Fix approach:** most are missing imports (`np`, `nltk`, `sys`, `argparse`), variables renamed on one side of a refactor, or GUI variables referenced from `_util` modules. Each is a small, testable fix; the smoke test (`tests/gui_smoke.py`) plus a targeted unit test should accompany each batch.

### 1.2 Error handler that itself crashes — `IO_files_util.py:261` — High confidence, manually verified

```python
except:
    print("... date location " + str(date_location) + " stored for the filenames ...")
```

Inside the filename-date sort's exception handler, `date_location` is undefined in scope. The moment a corpus has a filename that doesn't parse — the exact situation this handler exists for — the handler raises `NameError` inside `functools.cmp_to_key`, aborting the sort instead of printing the "non fatal" notice. The error-reporting path has never worked.

### 1.3 Dead-but-callable helpers with missing imports — `IO_files_util.py:1122, 1195` — High confidence, manually verified

- `:1122` references `visualization_tools`, undefined in the enclosing function (surrounding logic is commented out; this branch survived the commenting).
- `:1195` `gatherCLAs()` uses `argparse` without importing it — the comment above it admits it's "not used". Delete it or fix it; as written it's a trap for the next person who calls it.

### 1.4 Unbound GUI-state flags — `data_manipulation_main.py:972, 1001` — High confidence, Pyright-confirmed + manually verified

`activate_WHERE_options(*args)` reads `comingFrom_Plus` and `comingFrom_OK`, but those names exist only as **parameters of other functions** (`build_extract_string`, `activate_extract_fields`, `build_string_for_processing`) — there is no module-level or enclosing binding. When the WHERE-options callback fires with a non-empty field selection, it raises `NameError`. This is in a file touched by the most recent commit (`a5849717`), so it's live code.

Related: `build_extract_string` is **defined twice** in the same file (lines 262 and 788); the second definition silently replaces the first (see 2.4).

### 1.5 Silent failures: 221 bare `except:`, ~53 of them `except: pass` — High confidence

CLAUDE.md's own rule: *"No silent failures — surface problems with tkinter.messagebox; don't swallow exceptions."* The codebase currently has **221 bare excepts** (Ruff E722), of which roughly **53 swallow the exception entirely** (`pass`). Worst offenders:

| File | Bare excepts |
|---|---|
| `IO_files_util.py` | 12 |
| `GIS_geocode_util.py` | 12 |
| `file_filename_util.py` | 12 |
| `charts_util.py` | 11 |
| `Stanford_CoreNLP_util.py` | 10 |
| `IO_csv_util.py`, `config_util.py` | 9 each |

Bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, which in a GUI app means Ctrl-C and intentional exits get eaten. **Fix approach:** convert to `except Exception` at minimum; on user-facing paths, surface via `messagebox.showwarning/showerror` per the house rule. This is the largest single reliability lever in the codebase.

### 1.6 Late-binding closures over loop variables (Ruff B023) — 8 sites — Medium confidence

Closures created inside loops capture the loop **variable**, not its value — every closure sees the final iteration's value. Unlike the crashes above, these produce **wrong results silently**:

- `statistics_csv_util.py:71` (`col`), `:198` (`df`, `currentColumn`), `:539` (`temp_str`)
- `CoNLL_k_sentences_util.py:96` (`doc_id`, `DOC`)
- `charts_Plotly_util.py:118` (`html_template`)
- `charts_util.py:4119` (`preferred_kw`)

Each needs individual verification (some closures are invoked before the next iteration, which is safe), but `statistics_csv_util.py:198` capturing both `df` and `currentColumn` in a stats pipeline is the kind of bug that corrupts output without anyone noticing. **Fix:** bind at definition time (`lambda col=col: ...`).

---

## 2. Warning — should fix

### 2.1 `eval()` on runtime strings — 5 sites in 4 files — Medium confidence

- `charts_Plotly_util.py:112, 115, 138` — chart operations assembled as strings and `eval`'d
- `charts_util.py:2340` — `cmaps(eval(params[1]), eval(params[2]))`
- `hashfile.py:32` — `eval(tokens)` on file contents

Inputs are internal (config/param strings, not network data), so this is fragility more than an attack surface — but `eval` turns any malformed param into an arbitrary-exception generator and defeats all static analysis. `ast.literal_eval` or explicit parsing covers every one of these uses.

### 2.2 `subprocess` with `shell=True` — 12 sites — Medium confidence

`topic_modeling_mallet_util.py` (3), `social_science_research_main.py` (5), `TIPS_util.py` (2), `lib_util.py` (1), `NLP_welcome_main.py` (1). Paths interpolated into shell strings break on filenames with spaces/quotes (common in user corpora, and this suite is cross-platform). Prefer arg-list form, which also removes the injection class.

### 2.3 Mutable default arguments (Ruff B006) — 47 sites — High confidence (mechanical)

E.g. `IO_files_util.py:701`. A shared-list default mutated across calls is a classic state-leak bug. Mechanical fix (`=None` + guard), safe to batch.

### 2.4 Shadowing redefinitions (Ruff F811) — 37 sites — Medium confidence

Notable: `data_manipulation_main.py` defines `build_extract_string` at both 262 and 788 — the first is dead weight and a divergence trap. Also `IO_files_util.py:171` (`datetime` import shadowed by a local), `DB_PCACE_data_analysis_util.py:70` (`mb` re-imported). Each redefinition means one of the two definitions is silently ignored.

### 2.5 Test coverage is effectively zero

The pytest suite collects **3 tests**, all for `statistics_txt_util`. The infrastructure (conftest stubbing, CI workflow, `gui_smoke.py`) is in place and good — but 3 tests over ~109k lines means every finding in section 1 was reachable only by a user tripping over it. Growing the suite along the lines CLAUDE.md prescribes (pure stdlib helpers first: `CoNLL_util`, `semantic_aggregation_util`, regex builders) is the structural fix for this whole document.

### 2.6 Monolithic modules

| File | Lines |
|---|---|
| `DB_PCACE_data_analysis_util.py` | 7,382 |
| `charts_util.py` | 5,076 |
| `Stanford_CoreNLP_util.py` | 2,612 |
| `statistics_txt_util.py` | 2,144 |
| `corpus_profiler_util.py` | 2,116 |

Not urgent to split, but these are where the bare-except and F821 density is highest, and they're effectively untestable as units. When a module is next opened for a feature, peel testable helpers out rather than adding in place.

---

## 3. Info — hygiene backlog

- **NaN-check idiom via self-comparison (PLR0124, 7 sites):** `v == v` in `corpus_profiler_util.py:1763,1776`, `bf10 == bf10` in `statistics_statistical_tests_util.py:1274–1309`, `score == score` in `style_analysis_abstract_concreteness_analysis_util.py:110`. These are *intentional* NaN checks, not bugs — but `math.isnan()` / `pd.notna()` says what it means. (Verified: not defects.)
- **Auto-fixable Ruff backlog:** 502 unused variables (F841), 290 unused imports (F401), 435 unsorted imports (I001), 266 `u''` prefixes (UP025), 246 `.format()`→f-string (UP032), 148 redundant open modes, 80 invalid escape sequences (W605 — these can become errors in future Python). Most are `ruff --fix`-able; the pre-commit gate already stops new ones, so this backlog only shrinks if burned down deliberately. Suggested: one mechanical PR per rule class, verified by `tests/gui_smoke.py`.
- **Formatting split-brain:** 2,396 tab-indented lines and 226 mixed-tabs-and-spaces lines coexist with the Ruff-format config from PR #1636. Touched files get converted, so diffs carry whitespace noise. A one-shot format of `src/` (its own PR, no logic changes) would end this.
- **923 `print()` calls** in a GUI application — fine as an interim console log, but it's why real errors scroll past unseen. Long-term: route through `logging`.
- **187 TODO/FIXME/HACK markers** — worth a triage pass; several (e.g. `IO_files_util.py:1123` "the script does not work even in command line") mark features that are known-broken and should either get an issue or be removed.

---

## 4. Documentation accuracy

Checked CLAUDE.md claims against the tree — **substantially accurate**. All referenced paths exist and match: `tests/conftest.py` stubbing, `tests/gui_smoke.py`, `.github/workflows/tests.yml`, `NLP_Suite.spec`, `lib/wordLists`, `TIPS/` + `TIPS docx/`, pre-commit + `pyproject.toml` + `pyrightconfig.json`.

Minor drift:

- **File counts:** CLAUDE.md says ~50 `*_main.py` / ~122 `*_util.py` / ~201 total; actual is **54 / 131 / 211**. Within "~" tolerance but worth refreshing on the next CLAUDE.md edit.

## 5. Branch hygiene

Local branches fully merged into `roberto` — **safe to delete** (`git branch -d`):
`chore/lint-typecheck-config`, `ctk/phase0-bundle-imagetk-workaround`, `docs/customtkinter-migration-plan`, `docs/srl-optional-setup`, `fix/mac-welcome-screen-native-tk`, `fix/setup-app-probe`, `tests/document-statistics-poc`.

Keep: `roberto` (integration), `current-stable` (named snapshot), `ci-tests-target-roberto` (active — open PR #1639).

Upstream has five stale branches (2021–2024: `dev_ClaudeHu`, `dictionary`, `remove_shortcut_prompt`, `taeeun`, `tony`) — not this fork's to manage; noted for the maintainers.

---

## Summary

| Area | Critical | Warning | Info |
|---|---|---|---|
| Code | 68 latent NameErrors · 221 silent-failure excepts · 8 closure-capture sites · 2 verified live crashes | eval ×5 · shell=True ×12 · mutable defaults ×47 · shadowed defs ×37 · ~3-test coverage | ~2,000 auto-fixable lint items · formatting split-brain · 187 TODOs |
| Docs | — | — | file counts drifted (54/131/211) |
| Branches | — | — | 7 merged locals deletable |

**Suggested burn-down order:** (1) the two verified live crashes (§1.2, §1.4); (2) F821s file-by-file with smoke-test cover; (3) `except:` → `except Exception` + messagebox on user paths; (4) B023 closure verification; (5) mechanical Ruff batches; (6) one-shot formatting PR.
