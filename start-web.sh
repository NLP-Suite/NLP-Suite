#!/usr/bin/env bash
set -euo pipefail

NLP_SUITE_DIR="${NLP_SUITE_DIR:-$HOME/nlp-suite}"

if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker Desktop and try again."
  exit 1
fi

mkdir -p "$NLP_SUITE_DIR/input" "$NLP_SUITE_DIR/output" "$NLP_SUITE_DIR/csvInput"

export NLP_SUITE_DIR

docker compose up -d

echo "Waiting for NLP Suite to start..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:8000 > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -sf http://localhost:8000 > /dev/null 2>&1; then
  echo "NLP Suite did not start within 60 seconds."
  echo "Run 'docker compose logs' to investigate."
  exit 1
fi

echo "NLP Suite is running at http://localhost:8000"
echo "Your files are at: $NLP_SUITE_DIR"

case "$(uname)" in
  Darwin) open "http://localhost:8000" ;;
  Linux)  xdg-open "http://localhost:8000" 2>/dev/null || true ;;
esac
