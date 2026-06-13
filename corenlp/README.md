# Dockerized Stanford CoreNLP

This directory builds a Docker image that runs the [Stanford CoreNLP server](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html). It removes the need to install Java + CoreNLP locally — one of the most common install pain points reported by NLP-Suite users.

The Dockerfile is adapted from [NLPbox/stanford-corenlp-docker](https://github.com/NLPbox/stanford-corenlp-docker) (MIT-licensed). It downloads the latest CoreNLP release and the English language model at build time.

## Run it

From the repository root:

```bash
docker compose -f docker-compose.corenlp-mallet.yml up -d corenlp
```

CoreNLP will be available at `http://localhost:9000`.

## Test it

```bash
curl -s --data "Stanford CoreNLP is running." \
  'http://localhost:9000/?properties={"annotators":"tokenize,ssplit,pos","outputFormat":"json"}'
```

You should see a JSON response with tokens, sentences, and POS tags.

## Memory

By default CoreNLP gets 4 GB of RAM. Override with:

```bash
JAVA_XMX=2g docker compose -f docker-compose.corenlp-mallet.yml up -d corenlp
```

## Why this is useful

Today, NLP-Suite tools that depend on CoreNLP (parser, NER, SVO, coreference, etc.) require the user to download and extract the Stanford CoreNLP archive, install a matching Java runtime, and configure paths. This container packages all of that. The container is consumed by the web UI (see [PR #2](../README.md)), and future work can let the existing tkinter tools query it instead of spawning their own Java process.
