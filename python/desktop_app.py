#!/usr/bin/env python3
"""
Desktop app — double-click to open Report Studio (Mac .app / Windows .exe).

Development:
  cd python && pip install pywebview
  python desktop_app.py
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Path setup before other local imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_paths import APP_NAME, ensure_user_setup, init_paths, is_frozen  # noqa: E402


def _free_port() -> int:
    preferred = int(os.getenv("HAM_UI_PORT", "8765"))
    for port in (preferred, preferred + 1, preferred + 2, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


def _wait_for_server(url: str, timeout: float = 15.0) -> bool:
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def _run_server(port: int) -> None:
    import uvicorn
    from web_app import app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def main() -> None:
    ensure_user_setup()
    init_paths()
    from app_paths import apply_brand_loader_paths

    apply_brand_loader_paths()

    port = _free_port()
    url = f"http://127.0.0.1:{port}"

    thread = threading.Thread(target=_run_server, args=(port,), daemon=True)
    thread.start()

    if not _wait_for_server(url):
        print(f"Could not start {APP_NAME} server on {url}")
        sys.exit(1)

    # Native window when pywebview is available (desktop builds)
    try:
        import webview

        webview.create_window(
            APP_NAME,
            url,
            width=1440,
            height=920,
            min_size=(1024, 700),
            text_select=True,
        )
        webview.start()
    except ImportError:
        # Fallback: system browser (dev without pywebview)
        if not is_frozen():
            print(f"\n  {APP_NAME}")
            print(f"  Open: {url}\n")
            print("  Install pywebview for a native window: pip install pywebview\n")
        webbrowser.open(url)
        try:
            while thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
