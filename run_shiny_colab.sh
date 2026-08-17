#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
test -f model_bundle.pkl
exec python -m shiny run --host 0.0.0.0 --port "${PORT:-8000}" app.py
