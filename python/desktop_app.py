#!/usr/bin/env python3
"""
Desktop app — double-click to open Report Studio (Mac .app / Windows .exe).

Development:
  cd python && python desktop_app.py
  Optional native window: pip install pywebview  (Mac: xcode-select --install first)
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

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


def _native_webview(url: str) -> None:
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


def _browser_mode(url: str, thread: threading.Thread) -> None:
    """Open system browser; keep app alive with a small control window when bundled."""
    webbrowser.open(url)

    if is_frozen():
        try:
            import tkinter as tk

            root = tk.Tk()
            root.title(APP_NAME)
            root.geometry("520x220")
            root.resizable(False, False)

            msg = (
                f"{APP_NAME} is running.\n\n"
                "Your browser should open automatically.\n"
                "Use the browser to upload notes and generate reports.\n\n"
                "Keep this window open while you work.\n"
                "Close this window to quit the app."
            )
            tk.Label(root, text=msg, justify="left", padx=16, pady=12).pack(expand=True)
            tk.Button(root, text="Open in browser again", command=lambda: webbrowser.open(url)).pack(pady=(0, 12))

            def on_close() -> None:
                root.destroy()
                os._exit(0)

            root.protocol("WM_DELETE_WINDOW", on_close)
            root.mainloop()
            return
        except Exception:
            pass

    print(f"\n  {APP_NAME}")
    print(f"  Open: {url}\n")
    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        pass


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

    try:
        _native_webview(url)
    except ImportError:
        if not is_frozen():
            print("  Tip: pip install pywebview for a native window (Mac: xcode-select --install)\n")
        _browser_mode(url, thread)


if __name__ == "__main__":
    main()
