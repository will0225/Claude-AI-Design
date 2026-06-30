#!/usr/bin/env python3
"""Extract colors/fonts from brand/design/*.dc.html into brand.config.yaml comments."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

BRAND_DIR = Path(__file__).resolve().parent.parent / "brand"
CONFIG = BRAND_DIR / "brand.config.yaml"
DESIGN_DIR = BRAND_DIR / "design"
DEFAULT_DC = DESIGN_DIR / "Standard Review - 4600 Northgate.dc.html"


def extract_from_html(html: str) -> dict:
    colors = {}
    for name, pattern in [
        ("primary", r"--(?:color-)?primary[^:]*:\s*(#[0-9a-fA-F]{3,8})"),
        ("secondary", r"--(?:color-)?secondary[^:]*:\s*(#[0-9a-fA-F]{3,8})"),
        ("accent", r"--(?:color-)?accent[^:]*:\s*(#[0-9a-fA-F]{3,8})"),
        ("text", r"--(?:color-)?text[^:]*:\s*(#[0-9a-fA-F]{3,8})"),
    ]:
        m = re.search(pattern, html)
        if m:
            colors[name] = m.group(1)

    fonts = {}
    for name, pattern in [
        ("heading", r"--font-heading[^:]*:\s*['\"]?([^;'\"]+)"),
        ("body", r"--font-body[^:]*:\s*['\"]?([^;'\"]+)"),
    ]:
        m = re.search(pattern, html)
        if m:
            fonts[name] = m.group(1).split(",")[0].strip("'\"")

    return {"colors": colors, "fonts": fonts}


def main() -> None:
    dc = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DC
    if not dc.exists():
        print(f"❌ Not found: {dc}")
        sys.exit(1)

    html = dc.read_text(encoding="utf-8")
    extracted = extract_from_html(html)
    print(f"Extracted from {dc.name}:")
    print(yaml.dump(extracted, default_flow_style=False))

    if not CONFIG.exists():
        print(f"\nCopy values into {CONFIG} manually.")
        return

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    updated = False
    for k, v in extracted.get("colors", {}).items():
        if v and config.get("colors", {}).get(k) != v:
            config.setdefault("colors", {})[k] = v
            updated = True
    for k, v in extracted.get("fonts", {}).items():
        if v and config.get("fonts", {}).get(k) != v:
            config.setdefault("fonts", {})[k] = v
            updated = True

    if updated:
        CONFIG.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True), encoding="utf-8")
        print(f"✓ Updated {CONFIG}")
    else:
        print("No config changes needed.")


if __name__ == "__main__":
    main()
