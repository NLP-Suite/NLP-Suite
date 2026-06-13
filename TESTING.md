# Testing the web UI without merging

The web UI lives across four pull requests. You don't need to merge any of them to try it — GitHub lets you check out a pull request's branch locally, run it, then discard it.

## Prerequisites

- **Docker Desktop** installed and running ([Mac](https://www.docker.com/products/docker-desktop/) | [Windows](https://www.docker.com/products/docker-desktop/))
- A clone of this repository

Nothing else: Python, Java, Stanford CoreNLP, MALLET, and the rest of the project's usual dependencies are all installed *inside the containers* at first run.

## One checkout that includes everything

PR #1626 (CoreNLP + MALLET containers), #1627 (web UI + agent), #1628 (tests), and this PR are stacked, so checking out **this PR's branch** gives you everything ready to run.

Using the GitHub CLI:

```bash
gh pr checkout <this-PR-number>
```

Or with plain git:

```bash
git fetch origin pull/<this-PR-number>/head:try-web
git checkout try-web
```

## Run it

### macOS / Linux

```bash
./start-web.sh
```

### Windows

Either double-click `start-web.bat` in File Explorer, or from PowerShell:

```powershell
.\start-web.ps1
```

(If PowerShell blocks the script with an execution-policy warning, the `.bat` wrapper sidesteps that by passing `-ExecutionPolicy Bypass`.)

A browser will open at <http://localhost:8000> once the stack is healthy. The first run takes 10–15 minutes because Docker downloads CoreNLP, MALLET, the Stanza English model, and NLTK data; subsequent runs are a few seconds.

## Where files go

The launcher creates `~/nlp-suite/` (macOS/Linux) or `%USERPROFILE%\nlp-suite\` (Windows) with three subfolders:

- `input/` — drop text files here before running a tool
- `csvInput/` — drop CSV files here for tools that consume them
- `output/` — tool results land here

Override the location with the `NLP_SUITE_DIR` environment variable:

```bash
NLP_SUITE_DIR=/path/to/data ./start-web.sh
```

```powershell
$env:NLP_SUITE_DIR = "D:\nlp-suite-data"
.\start-web.ps1
```

## When you're done

```bash
docker compose down
```

That stops and removes the containers. Your data in `~/nlp-suite/` (or wherever you pointed `NLP_SUITE_DIR`) is preserved.

To remove the downloaded container images entirely:

```bash
docker compose down --rmi all
```

## Returning to your regular branch

```bash
git checkout current-stable
git branch -D try-web
```

The tkinter codebase is untouched throughout — nothing about the existing `setup_Mac/`, `setup_Windows/`, or `src/` changes when you switch branches.

## PR-by-PR testing (optional)

If you want to evaluate each PR in isolation rather than the whole stack:

| PR | What to test after `gh pr checkout <n>` |
| --- | --- |
| #1626 | `docker compose -f docker-compose.corenlp-mallet.yml up -d` then `curl http://localhost:9000/`. CoreNLP + MALLET only — no UI. |
| #1627 | `./start-web.sh` (Mac/Linux) or `.\start-web.ps1` (Windows). The full web UI. |
| #1628 | `cd agent && pytest`. The agent test suite. |
| this PR | Same as #1627, plus verifying the Windows scripts. |

Each branch builds on the previous one, so #1627 already contains #1626's files, #1628 contains both, and this PR contains all three.
