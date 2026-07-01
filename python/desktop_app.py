#!/usr/bin/env python3
"""
Desktop app — double-click to open Report Studio (Mac .app / Windows .exe).
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

# PyInstaller on Windows requires this before anything else
if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_paths import APP_NAME, ensure_user_setup, init_paths, is_frozen  # noqa: E402
from desktop_launcher import UVICORN_LOG_CONFIG, fatal_error, log, log_path, setup_frozen, show_error  # noqa: E402


def _free_port() -> int:
    preferred = int(os.getenv("HAM_UI_PORT", "8765"))
    for port in (preferred, preferred + 1, preferred + 2, preferred + 3, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


def _wait_for_server(url: str, timeout: float = 30.0) -> bool:
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False


def _run_server(port: int, error_box: list) -> None:
    try:
        import uvicorn
        from web_app import app

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
            log_config=UVICORN_LOG_CONFIG,
        )
    except Exception as exc:
        error_box.append(exc)
        log("SERVER ERROR:\n" + traceback.format_exc())


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


def _browser_mode(url: str) -> None:
    webbrowser.open(url)
    log(f"Opened browser: {url}")

    if is_frozen():
        try:
            import tkinter as tk

            root = tk.Tk()
            root.title(APP_NAME)
            root.geometry("540x240")
            root.resizable(False, False)

            msg = (
                f"{APP_NAME} is running.\n\n"
                "Your browser should open automatically.\n"
                "Upload notes and generate reports in the browser.\n\n"
                "Keep this window open while you work.\n"
                "Close this window to quit."
            )
            tk.Label(root, text=msg, justify="left", padx=16, pady=12).pack(expand=True)
            tk.Button(root, text="Open in browser again", command=lambda: webbrowser.open(url)).pack(pady=(0, 12))

            def on_close() -> None:
                root.destroy()
                os._exit(0)

            root.protocol("WM_DELETE_WINDOW", on_close)
            root.mainloop()
            return
        except Exception as exc:
            log("TKINTER ERROR:\n" + traceback.format_exc())
            show_error(
                f"{APP_NAME} is running in your browser.\n\n"
                f"Open: {url}\n\n"
                f"(Control window unavailable: {exc})"
            )
            while True:
                time.sleep(3600)
        return

    print(f"\n  {APP_NAME}\n  Open: {url}\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def main() -> None:
    setup_frozen()
    log(f"Starting {APP_NAME} (frozen={is_frozen()}) cwd={os.getcwd()}")

    ensure_user_setup()
    init_paths()
    from app_paths import apply_brand_loader_paths

    apply_brand_loader_paths()

    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    log(f"Using port {port}")

    server_error: list = []
    thread = threading.Thread(target=_run_server, args=(port, server_error), daemon=True)
    thread.start()

    if not _wait_for_server(url):
        if server_error:
            fatal_error("Report Studio could not start the server.", server_error[0])
        fatal_error(
            f"Report Studio did not start within 30 seconds.\n\n"
            f"Try opening manually: {url}\n\n"
            f"Log: {log_path()}"
        )

    log("Server ready")

    try:
        _native_webview(url)
    except ImportError:
        _browser_mode(url)
    except Exception as exc:
        fatal_error("Report Studio failed to open the window.", exc)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        fatal_error("Report Studio crashed on startup.", exc)
