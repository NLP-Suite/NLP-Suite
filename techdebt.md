# Tech Debt

Known issues in the fork, deliberately not fixed yet. Entries tagged by
priority: **P1** next up, **P2** worth a dedicated PR, **P3** fine to defer.

This fork carries two parallel codebases under one repo: the legacy desktop
tkinter app at `/src/` (~199 modules, the upstream NLP-Suite) and the new
Dockerized agent + Django UI under `/agent/`, `/ui/`, `/corenlp/`, `/mallet/`
(added across PRs #1626–#1629). Most debt below sits on the boundary between
those two — what got ported, what didn't, and what's duplicated.

**Next up:**
1. **[P1] Decide the fate of `/src/`** — the legacy desktop tree is still
   shipped alongside the new agent. Either remove it or document it as a
   reference-only archive (see *Two parallel codebases* below).
2. **[P2] Port the `/word2vec` backends** (`word2vec_Gensim_util`, `WSI_*`)
   from `/src/` into `agent/src/analysis/` — endpoint crashes on every real
   option; tests in `agent/tests/test_word2vec.py` document the breakage.
3. **[P2] Package conversion** (flat `sys.path` → real package), own PR.

## Two parallel codebases

- **[P1] `/src/` (legacy desktop) and `/agent/src/` coexist with no clear
  contract.** ~199 modules under `/src/` are the tkinter desktop app; the
  Dockerized agent re-ports a subset into `agent/src/{analysis,charts,core,
  gis,io,nlp,stories,topic_modeling,file_ops}`. There is no mapping doc, no
  CI check that the two stay in sync, and several agent modules were ported
  partially (see *Functional gaps*). Pick one of: (a) delete `/src/` and
  archive it on a tag, (b) move it to `legacy/src/` with a README declaring
  it read-only, or (c) commit to keeping them in sync with a manifest.
- **[P2] Debug-script litter in `/src/`.** Eight `_*.py` files
  (`_add_indexes.py`, `_add_indexes_now.py`, `_check_idx.py`, `_check_path.py`,
  `_debug_hops.py`, `_debug_xref.py`, `_test_actor_process.py`,
  `_test_cross_join.py`) are ad-hoc scripts left in the tree. Delete unless
  someone claims them.
- **[P2] Three dependency manifests, no single source of truth.** Root
  `requirements.txt` (desktop), `agent/requirements.txt`, `ui/requirements.txt`
  — heavy ML pins (torch 2.2.2, transformers 4.39.2, spacy 3.7.4) live only
  in `agent/`. Root `requirements.txt` is for the PyInstaller desktop build
  and will drift. Decide whether the desktop build is still supported.
- **[P3] PyInstaller spec (`NLP_Suite.spec`, `post_build_fixup.py`) and
  `setup_Mac/`, `setup_Windows/` belong to the desktop era.** The new
  `start-web.{sh,bat,ps1}` scripts and `docker-compose.yml` are the supported
  entry points (per `TESTING.md`). If desktop is deprecated, remove these and
  the matching GitHub Actions workflow that builds the installer.
- **[P3] Root-level corpora dirs (`csvInput/`, `input/`, `output/`).** Empty
  in git, but the agent mounts `~/nlp-suite/{input,output}` — these root
  placeholders confuse new contributors about where data actually goes.
- **[P3] `MEMO_Development_Notes.md` (35 KB) and `wiki-draft-About.md` are
  desktop-era.** Mostly historical. Either move to `docs/legacy/` or trim
  to what the agent contributor actually needs.

## Functional gaps (agent endpoints)

These largely match the upstream nlp-suite audit since `agent/src/` is the
same ported code:

- **[P2] `/word2vec` backends were never ported — every real option crashes.**
  `agent/src/analysis/word2vec.py` imports `word2vec_Gensim_util`, `WSI_util`,
  `WSI_keyterms`, `WSI_viz` (all missing → ModuleNotFoundError) and calls
  `BERT_util.word_embeddings_BERT` (never ported → AttributeError).
  `agent/tests/test_word2vec.py` pins down each failure mode. Port from
  `/src/` (which has the desktop versions), Gensim path first.
- **[P2] CoNLL table "all analyses" modules were never ported.** The seven
  `CoNLL_*_analysis_util` modules (clause, noun, adjective, ratio, adverb,
  verb, function-words) live in `/src/` but are missing from `agent/src/nlp/`,
  so `all_analyses_var=True` always raises ModuleNotFoundError (documented by
  `agent/tests/test_conll_table.py`). Search, compute-sentence, and
  k-sentences paths work and are tested.
- **[P3] Gender analysis: US Social Security plot path is coming-soon.**
  Backend works via `POST /gender`, but `plot_var` needs the
  `lib/namesGender/` data files (`SS_yearOfBirth.csv`,
  `SS_state_yearOfBirth.csv`, CMU/census name lists) — never copied from
  `/src/`. Root `lib/namesGender/` exists (legacy desktop) but isn't wired
  to `GUI_IO_util.namesGender_libPath`. Copy into `agent/lib/namesGender/`,
  re-enable plot controls in `gender_analysis.html`, stop hardcoding
  `plot_var=False` in the endpoint.
- **[P3] Non-Python wordcloud "services" just open external websites**
  (TagCrowd, Wordle, etc.). A headless agent cannot open browser windows.
  The Python WordCloud backend works. Either remove the external-service
  dropdown options in `ui/templates/wordclouds.html` or turn them into
  plain links.
- **[P3] Wordcloud image-mask options are coming-soon** (`prepareImage`,
  `usePNGFile`, `imageContour`, `useColorsForCsvColumns`): `/wordcloud`
  accepts the params and the backend supports masks, but there is no
  image-upload workflow. Same story for `manualCoreference` in `SVO.html`
  (needs interactive split-screen editor) and `csv_file_var` in
  `NGrams_CoOccurrences.html` (needs a csv-file picker).
- **[P3] `/gis` csv-file input silently does nothing.** `GIS_main.py` passes
  the placeholder string `NER_StanfordCoreNLP_output` to `GIS_pipeline` when
  `NER_extractor` is off, so the pipeline bails on a nonexistent file
  (documented by `agent/tests/test_gis.py`). The pipeline itself works when
  handed a real locations csv (SVO calls it that way). Related bugs found
  in the same sweep: `GIS_geocode_util.geocode` hits UnboundLocalError on
  `date` when input has no Date column — breaks the entire `/gis` NER path
  for corpora without filename dates (network-gated xfail). And
  `GIS_main.py` calls `area_var.set(...)` (a tkinter remnant) on a plain
  string when the area value is malformed.
- **[P3] CoNLL k-sentences crashes on short documents.**
  `CoNLL_k_sentences_util.k_sent` truth-tests a pandas Series whenever a
  document has <= 2*K sentences (`ValueError: truth value of a Series is
  ambiguous`); fine for K=1 on real documents, but any short document kills
  the whole run.
- **[P3] `BERT_util` is a partial port.** Sentiment backend was ported.
  Upstream `NER_tags_BERT`, `doc_summary_BERT`, `word_embeddings_BERT`
  depend on packages not in the agent image (`contextualSpellCheck`,
  `bert-extractive-summarizer`) and were not ported.
- **[P3] External-software install flow is desktop-era.** Algorithms needing
  external software (WordNet jars, Google Earth, …) used to launch
  `NLP_setup_external_software_main.py` (tkinter). The agent has no headless
  download path — affected endpoints log a warning and return. Would need a
  download-into-`~/nlp-suite/external_software` path to re-enable the
  WordNet knowledge-graph endpoint, etc.
- **[P3] Tips File feature removed, not replaced.** Old templates had
  broken "Tips File" buttons pointing at `tips_files.js` and `TIPS_*.pdf`.
  Buttons were deleted from the new UI; the 169-file `TIPS/` directory and
  the `TIPS docx/` directory are still in the repo root. If the feature
  isn't coming back, move both to `legacy/` or drop them.

## Architecture

- **[P2] Flat `sys.path` imports in the agent.** `agent/src/main.py` adds
  every `agent/src/*` subdirectory to `sys.path`, and the ~100 modules
  underneath import each other by bare name. Defeats IDE
  navigation/refactoring. Right fix: convert `agent/src` into a real package
  with relative imports — large, mechanical, easy to get wrong; do it in one
  dedicated PR with no other changes. Related constraint:
  `Stanford_CoreNLP_util.py` imports the `corenlp_json_*` modules at its
  bottom, so those modules must not import it at module level (shared helpers
  live in `corenlp_json_common.py`).
- **[P3] Single-job concurrency by design.** The agent holds one
  `threading.Lock`; concurrent requests get 503. Fine for single-researcher
  use, but any multi-user deployment needs a real job queue.
- **[P3] UI ↔ agent contract is implicit.** `ui/app/views.py` posts form
  fields straight to the agent and relays its response. There is no shared
  schema, no typed client — endpoint param renames silently break the UI.
  An OpenAPI export from the FastAPI agent + a generated client in the UI
  would catch this at build time.

## Code quality

- **[P3] ~129 inline TODO/FIXME comments** remain in `agent/src`, inherited
  from the research codebase. Densest files: `gis/GIS_geocode_util.py`,
  `nlp/corenlp_json_syntax.py`, `charts/`. Most document genuine known
  limitations rather than stale notes.
- **[P3] Python 3.9 ceiling.** The agent image (ubuntu:20.04) runs Python
  3.9, so 3.10+ syntax (`X | None`, `zip(strict=)`, match statements) breaks
  at runtime. `ruff target-version = "py39"` in `agent/pyproject.toml` guards
  lint suggestions, but tests run on the host's newer Python and won't catch
  it. Consider a newer base image when upgrading the ML stack.
- **[P3] No type checking in CI.** `agent/pyproject.toml` configures ruff
  but there is no `mypy`/`pyright` step. Given the flat `sys.path` and the
  number of undefined-name bugs found in earlier porting passes, even a
  permissive type check would pay off.

## Performance

- **Model-load caching: fixed** via `agent/src/core/model_cache.py`
  (process-wide dict keyed by model args; stanza/spaCy/SentenceTransformer
  getters). Residuals: `Stanza_functions_util.py` builds its module-level
  `stanzaPipeLine` at import time (loaded even for jobs that never use it —
  could become lazy via the cache), and `file_spell_checker_util.py`'s
  `MultilingualPipeline()` calls.
- **[P3] Pervasive `df.iterrows()`/row-append loops** (~31 sites) inherited
  from the research code. Vectorize per-algorithm, only when an endpoint
  feels slow in practice.

## Security / deployment (defer until any hosted deployment)

- **[P3] Django `SECRET_KEY` is hardcoded** in `ui/config/settings.py`
  (`django-insecure-...`) and `DEBUG` defaults on. Acceptable for the local
  Docker-only research tool; must be env-injected before any hosted
  deployment.
- **[P3] CORS is wide open** on the agent (`origins = ["*"]` in
  `agent/src/main.py`). Same caveat.
- **[P3] `docker-compose.yml` pins container IPs in a custom subnet**
  (`172.16.0.0/16`). Convenient for local dev but will collide on networks
  that already use that range. Switch to service-name DNS
  (`http://agent:3000`) once UI/agent stop hard-coding IPs.
- **[P3] No `.env.example`.** Now that `.env` is git-ignored
  (this PR), ship a checked-in `.env.example` listing the variables
  docker-compose reads (`NLP_SUITE_DIR`, agent/UI env vars) so new clones
  know what to fill in.

## Testing

- **[P3] ~10 of 24 agent endpoints still have no tests.** Covered: core
  utils, model cache, NER, wordnet*, boxplot, excel charts, wordcloud,
  sentiment, topic modeling (Gensim), ngrams, gender analysis*, shape of
  stories*, parse*, word2vec, conll_table, svo*, gis*, statistics
  (\*some paths integration-, network-, or external-software-gated).
  Remaining: file_manager, style_analysis, sunburst, colormap, sankey,
  file_search, sentence_analysis, settings. Tests skip on the host (heavy
  deps live in the Docker image); run them in the agent container:
  `docker run --rm -v "$PWD/agent:/work" -w /work nlp-suite-agent python3.9 -m pytest tests/`
  For CoreNLP-gated tests, run on the compose network with
  `--network nlp-suite-fork_nlp-suite-network -e CORENLP_URL=http://corenlp:9000`
  and `-m integration`; Nominatim-gated GIS tests need
  `NLP_SUITE_TEST_NETWORK=1`.
- **[P3] No tests for the Django UI.** `ui/app/views.py` is untested — the
  routing/relay logic to the agent is small but the form-field passthrough
  is exactly where the implicit UI↔agent contract breaks.
- **[P3] MALLET topic modeling has no hermetic test.** The mallet service
  reads its own mounted `/app/input` (the live `~/nlp-suite/input`), so a
  test would touch real user data. The BERTopic path and roBERTa sentiment
  are testable but gated behind `NLP_SUITE_TEST_BERT=1` (large HuggingFace
  model downloads on first run).
- **[P3] No CI for the new Docker stack.** The repo's existing GitHub
  Actions builds the PyInstaller desktop installer; nothing builds the
  agent/UI images or runs `pytest`. A minimal `docker compose build` +
  `pytest` job would catch most regressions before review.

## Forks (`corenlp/`, `mallet/`) — no code changes by policy

- `mallet/Dockerfile` installs unversioned `python3` + `fastapi`/`uvicorn`;
  `mallet/api.py` is live (serves `POST /run` on 5050 — do not delete).
- Heavy ML pins in `agent/requirements.txt` (torch 2.2.2, transformers
  4.39.2, spacy 3.7.4) deliberately frozen; upgrading needs
  model-compatibility testing.
