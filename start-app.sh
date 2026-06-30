#!/bin/bash
# Start the client web UI — one command, no coding required.
set -e
cd "$(dirname "$0")"

if [ ! -f brand/brand.config.yaml ]; then
  echo "First-time setup: copying brand config…"
  cp brand/brand.config.example.yaml brand/brand.config.yaml
fi

if [ ! -f python/.env ]; then
  echo ""
  echo "⚠  Add your API key: copy python/.env.example to python/.env"
  echo "   You can still preview the format without a key."
  echo ""
fi

cd python
if [ -d "../venv/bin" ]; then
  ../venv/bin/pip install -r requirements.txt -q
  ../venv/bin/python web_app.py
else
  pip install -r requirements.txt -q
  python3 web_app.py
fi
