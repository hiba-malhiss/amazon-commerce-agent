#!/usr/bin/env bash
# Run the backend for local development: the indexing worker AND the API together, so an
# upload is never stuck on `indexing` because the worker was forgotten.
#
# Usage, from backend/:   ./scripts/dev.sh
# Needs Postgres and Redis running (docker compose up -d postgres redis from the repo root).
set -euo pipefail
cd "$(dirname "$0")/.."

# Stop the worker when this script exits (Ctrl-C), so no stray worker is left behind
worker_pid=""
cleanup() { [ -n "$worker_pid" ] && kill "$worker_pid" 2>/dev/null || true; }
trap cleanup EXIT

echo "Starting the indexing worker..."
.venv/bin/celery -A app.worker.celery_app worker --loglevel=info &
worker_pid=$!

echo "Starting the API on http://127.0.0.1:8000 ..."
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000  # foreground: Ctrl-C stops both
