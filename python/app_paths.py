"""
Application paths for dev, PyInstaller bundle, and per-user data.

Read-only assets (templates, CSS, web UI) ship inside the app bundle.
Writable data (config, inbox, output, API key) lives in the user's folder:
  Mac:     ~/Library/Application Support/HAM Report Studio
  Windows: %APPDATA%\\HAM Report Studio
  Linux:   ~/.ham-report-studio
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "HAM Report Studio"
ENV_FILENAME = ".env"
CONFIG_NAME = "brand.config.yaml"
CONFIG_EXAMPLE_NAME = "brand.config.example.yaml"

_initialized = False
bundle_root: Path = Path(__file__).resolve().parent.parent
user_data: Path = Path.home() / ".ham-report-studio"
web_dir: Path = bundle_root / "web"
brand_bundle: Path = bundle_root / "brand"
user_brand_dir: Path = user_data / "brand"
config_path: Path = user_brand_dir / CONFIG_NAME
config_example_path: Path = brand_bundle / CONFIG_EXAMPLE_NAME
styles_path: Path = brand_bundle / "styles" / "document.css"
fixed_template_path: Path = brand_bundle / "templates" / "fixed_document.html"
html_template_path: Path = brand_bundle / "templates" / "document.html"
output_dir: Path = user_brand_dir / "output"
inbox_dir: Path = user_brand_dir / "inbox"
inbox_done_dir: Path = inbox_dir / "done"
reference_dc: Path = brand_bundle / "design" / "Standard Review - 4600 Northgate.dc.html"
sample_source: Path = brand_bundle / "samples" / "sra-northgate-h1-2026-source.txt"
env_path: Path = user_data / ENV_FILENAME


def _user_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / APP_NAME
    return Path.home() / ".ham-report-studio"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def init_paths() -> None:
    global _initialized, bundle_root, user_data, web_dir, brand_bundle
    global user_brand_dir, config_path, config_example_path
    global styles_path, fixed_template_path, html_template_path
    global output_dir, inbox_dir, inbox_done_dir, reference_dc, sample_source, env_path

    if _initialized:
        return

    if is_frozen():
        bundle_root = Path(sys._MEIPASS)
    else:
        bundle_root = Path(__file__).resolve().parent.parent

    user_data = _user_data_dir()
    web_dir = bundle_root / "web"
    brand_bundle = bundle_root / "brand"
    user_brand_dir = user_data / "brand"
    config_path = user_brand_dir / CONFIG_NAME
    config_example_path = brand_bundle / CONFIG_EXAMPLE_NAME
    styles_path = brand_bundle / "styles" / "document.css"
    fixed_template_path = brand_bundle / "templates" / "fixed_document.html"
    html_template_path = brand_bundle / "templates" / "document.html"
    output_dir = user_brand_dir / "output"
    inbox_dir = user_brand_dir / "inbox"
    inbox_done_dir = inbox_dir / "done"
    reference_dc = brand_bundle / "design" / "Standard Review - 4600 Northgate.dc.html"
    sample_source = brand_bundle / "samples" / "sra-northgate-h1-2026-source.txt"
    env_path = user_data / ENV_FILENAME
    _initialized = True


def ensure_user_setup() -> None:
    """Create user folders and default config; load API key from user data."""
    init_paths()
    user_data.mkdir(parents=True, exist_ok=True)
    user_brand_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        if config_example_path.exists():
            shutil.copy2(config_example_path, config_path)
        elif (bundle_root / "brand" / CONFIG_EXAMPLE_NAME).exists():
            shutil.copy2(bundle_root / "brand" / CONFIG_EXAMPLE_NAME, config_path)

    # Dev fallback: also load python/.env when not frozen
    if not is_frozen():
        dev_env = Path(__file__).resolve().parent / ".env"
        if dev_env.exists():
            load_dotenv(dev_env)

    if env_path.exists():
        load_dotenv(env_path, override=True)


def apply_brand_loader_paths() -> None:
    """Point brand_loader module constants at resolved paths."""
    import brand_loader as bl

    init_paths()
    bl.BRAND_DIR = user_brand_dir
    bl.CONFIG_PATH = config_path
    bl.EXAMPLE_PATH = config_example_path
    bl.STYLES_PATH = styles_path
    bl.HTML_TEMPLATE_PATH = html_template_path
    bl.FIXED_TEMPLATE_PATH = fixed_template_path
    bl.OUTPUT_DIR = output_dir
    bl.INBOX_DIR = inbox_dir
    bl.INBOX_DONE_DIR = inbox_done_dir


def save_api_key(api_key: str) -> None:
    init_paths()
    user_data.mkdir(parents=True, exist_ok=True)
    key = api_key.strip()
    env_path.write_text(f"ANTHROPIC_API_KEY={key}\n", encoding="utf-8")
    os.environ["ANTHROPIC_API_KEY"] = key
    load_dotenv(env_path, override=True)


def api_key_configured() -> bool:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return bool(key and not key.startswith("sk-ant-api03-xxx"))


def masked_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key or len(key) < 12:
        return ""
    return f"{key[:10]}…{key[-4:]}"
