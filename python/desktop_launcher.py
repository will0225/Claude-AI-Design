"""Startup helpers for the frozen desktop app (Windows/Mac)."""

from __future__ import annotations

import io
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

APP_NAME = "HAM Report Studio"

# Uvicorn default logging calls stream.isatty() — fails when stdout/stderr are None (Windows .exe)
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "WARNING", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "WARNING", "propagate": False},
    },
}


def fix_stdio() -> None:
    """PyInstaller windowed apps on Windows have sys.stdout/stderr = None."""
    if sys.stdout is None:
        sys.stdout = io.TextIOWrapper(open(os.devnull, "wb"), encoding="utf-8", errors="replace")
    if sys.stderr is None:
        sys.stderr = io.TextIOWrapper(open(os.devnull, "wb"), encoding="utf-8", errors="replace")


def setup_frozen() -> None:
    """Required for PyInstaller on Windows."""
    fix_stdio()
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
