# Dockerized MALLET

This directory builds a Docker image that wraps [MALLET](https://mimno.github.io/Mallet/) (the Java-based topic-modeling toolkit) behind a small HTTP API. It removes the need to install Java + MALLET locally.

The container is built on Amazon Corretto 17 and installs MALLET 2.0.8. A thin FastAPI app (`api.py`) exposes a single endpoint that runs `mallet <command>` with the given arguments.

## Run it

From the repository root:

```bash
docker compose -f docker-compose.corenlp-mallet.yml up -d mallet
```

The API will be available at `http://localhost:8081`.

## API

`POST /run` accepts JSON of the form:

```json
{
  "command": "import-dir",
  "args": {
    "input": "/app/my-corpus",
    "output": "/app/out.mallet",
    "keep-sequence": true
  }
}
```

This runs `mallet import-dir --input /app/my-corpus --output /app/out.mallet --keep-sequence`. Boolean `true` becomes a flag; other values become `--key value` pairs.

The container expects the corpus to live inside `/app` (mount your data with `-v $PWD:/app` if running standalone). The full Docker-compose setup in [PR #2](../README.md) wires this volume mount automatically.

## Test it

```bash
curl -s http://localhost:8081/openapi.json | head -c 200
```

You should see the FastAPI schema document.

## Why this is useful

Topic-modeling tools in NLP-Suite require a working MALLET install, which is a frequent source of setup failures. This container packages MALLET and a uniform HTTP interface. The container is consumed by the web UI (see [PR #2](../README.md)).
