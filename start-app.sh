#!/bin/bash
# Start Report Studio — native window or browser
set -e
cd "$(dirname "$0")"

if [ ! -f brand/brand.config.yaml ] && [ -f brand/brand.config.example.yaml ]; then
  cp brand/brand.config.example.yaml brand/brand.config.yaml
fi

cd python
if [ -d "../venv/bin" ]; then
  PY="../venv/bin/python"
  PIP="../venv/bin/pip"
else
  PY="python3"
  PIP="pip"
fi

$PIP install -r requirements.txt -q
$PIP install pywebview -q 2>/dev/null || true

# Prefer native desktop window when pywebview is available
if $PY -c "import webview" 2>/dev/null; then
  $PY desktop_app.py
else
  echo "Tip: pip install pywebview for a native app window"
  $PY web_app.py
fi
