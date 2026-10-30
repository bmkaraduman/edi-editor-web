#!/usr/bin/env bash
# One-shot setup: dependencies, seed catalog, model training.
set -euo pipefail
cd "$(dirname "$0")"
pip install -r requirements.txt
python3 scripts/build_seed.py
python3 -m app.ml.train
echo
echo "Run:  uvicorn app.main:app --reload   ->  http://127.0.0.1:8000"
