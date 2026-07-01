#!/bin/bash
# Build HAM Report Studio.app for Mac (run on macOS)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== HAM Report Studio — Mac build ==="

python3 -m venv build/venv-build
source build/venv-build/bin/activate
pip install -q -r python/requirements.txt -r python/requirements-build.txt

pyinstaller build/report_studio.spec --noconfirm --clean

echo ""
echo "✓ Built: dist/HAM Report Studio.app"
echo "  Drag to Applications, then double-click to run."
echo "  Client adds API key once in Settings — no terminal needed."
