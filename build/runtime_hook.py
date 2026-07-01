# PyInstaller runtime hook — run before app code
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)

# Fix None stdout/stderr before any imports use logging (Windows windowed exe)
try:
    import io

    if sys.stdout is None:
        sys.stdout = io.TextIOWrapper(open(os.devnull, "wb"), encoding="utf-8", errors="replace")
    if sys.stderr is None:
        sys.stderr = io.TextIOWrapper(open(os.devnull, "wb"), encoding="utf-8", errors="replace")
except Exception:
    pass
