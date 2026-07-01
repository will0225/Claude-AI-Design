#!/bin/bash
# Build HAM Report Studio.app for Mac (run on macOS)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== HAM Report Studio — Mac build ==="

# Clean previous build venv if pywebview failed before
if [ -d build/venv-build ]; then
  echo "Using existing build/venv-build (delete it to start fresh)"
fi

python3 -m venv build/venv-build
source build/venv-build/bin/activate

python -m pip install -q --upgrade pip setuptools wheel
pip install -q -r python/requirements.txt
pip install -q -r python/requirements-build.txt

# pywebview is OPTIONAL — needs Xcode Command Line Tools to compile pyobjc on some Macs
if pip install -q pywebview 2>/dev/null; then
  echo "✓ pywebview installed (native app window)"
else
  echo "⚠ Skipping pywebview — no compiler or wheels unavailable."
  echo "  The .app will open Report Studio in your default browser (works fine for clients)."
  echo "  For a native window later, run:  xcode-select --install"
  echo "  Then rebuild."
fi

pyinstaller build/report_studio.spec --noconfirm --clean

echo ""
echo "✓ Built: dist/HAM Report Studio.app"
echo "  Drag to Applications, then double-click to run."
echo "  Client adds API key once in Settings — no terminal needed."
