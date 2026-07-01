"""Startup helpers for the frozen desktop app (Windows/Mac)."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from typing import Optional

APP_NAME = "HAM Report Studio"


def setup_frozen() -> None:
    """Required for PyInstaller on Windows."""
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        os.chdir(exe_dir)


def log_path() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP") or str(Path.home())
        return Path(base) / APP_NAME / "report-studio.log"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / f"{APP_NAME}.log"
    return Path.home() / ".ham-report-studio" / "report-studio.log"


def log(message: str) -> None:
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(message.rstrip() + "\n")
    except Exception:
        pass


def show_error(message: str) -> None:
    log(message)
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(  # type: ignore[attr-defined]
                0,
                message + f"\n\nLog file:\n{log_path()}",
                APP_NAME,
                0x10,
            )
            return
        except Exception:
            pass
    print(message, file=sys.stderr)


def fatal_error(message: str, exc: Optional[BaseException] = None) -> None:
    detail = message
    if exc is not None:
        detail += "\n\n" + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    show_error(detail)
    sys.exit(1)
